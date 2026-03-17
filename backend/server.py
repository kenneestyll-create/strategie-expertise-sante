from fastapi import FastAPI, APIRouter, Request as FastAPIRequest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import Response, RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from slowapi.errors import RateLimitExceeded
import asyncio
import os
import uuid
from datetime import datetime, timezone, timedelta, time as dtime

from config import client, db, logger, SITE_URL, limiter
from routes import all_routers

# Rate limiter — SECURITY FIX V2
app = FastAPI(title="Stratégie & Expertise Santé API")
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: FastAPIRequest, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Trop de tentatives. Veuillez réessayer dans quelques minutes."}
    )

# SECURITY FIX V5 — CORS strict: only authorized origins
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', SITE_URL).split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SECURITY FIX V12 — Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)

api_router = APIRouter(prefix="/api")

for router in all_routers:
    api_router.include_router(router)

app.include_router(api_router)

# ==================== EMAIL TRACKING (public, no auth) ====================

# 1x1 transparent PNG pixel
PIXEL = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

@app.get("/api/track/open/{reminder_id}")
async def track_email_open(reminder_id: str):
    """Tracking pixel endpoint — records email open."""
    now = datetime.now(timezone.utc).isoformat()
    # Try inactivity reminders first, then completeness notifications
    result = await db.inactivity_reminders.update_one(
        {"id": reminder_id, "opened_at": {"$exists": False}},
        {"$set": {"opened_at": now, "opened": True}}
    )
    if result.modified_count == 0:
        await db.completeness_notifications.update_one(
            {"id": reminder_id, "opened_at": {"$exists": False}},
            {"$set": {"opened_at": now, "opened": True}}
        )
    return Response(content=PIXEL, media_type="image/png", headers={"Cache-Control": "no-store, no-cache"})

@app.get("/api/track/click/{reminder_id}")
async def track_email_click(reminder_id: str):
    """CTA click tracking — records click and redirects to client space."""
    now = datetime.now(timezone.utc).isoformat()
    result = await db.inactivity_reminders.update_one(
        {"id": reminder_id, "clicked_at": {"$exists": False}},
        {"$set": {"clicked_at": now, "clicked": True}}
    )
    if result.modified_count == 0:
        await db.completeness_notifications.update_one(
            {"id": reminder_id, "clicked_at": {"$exists": False}},
            {"$set": {"clicked_at": now, "clicked": True}}
        )
    return RedirectResponse(url=f"{SITE_URL}/espace-client?tab=documents", status_code=302)

app.add_middleware(GZipMiddleware, minimum_size=500)


class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path.startswith("/api/faq") or path.startswith("/api/avis") or path.startswith("/api/visitors"):
            response.headers["Cache-Control"] = "public, max-age=300"
        elif path.startswith("/api/sitemap") or path.startswith("/api/robots"):
            response.headers["Cache-Control"] = "public, max-age=86400"
        return response


app.add_middleware(CacheControlMiddleware)


@app.on_event("startup")
async def startup_db_client():
    logger.info("Starting up: connected to MongoDB")
    await db.command("ping")
    logger.info("MongoDB ping successful")

    # Initialize object storage
    try:
        from utils.storage import init_storage
        init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.warning(f"Object storage init failed (will use DB fallback): {e}")

    # Auto-seed on first startup
    existing_admin = await db.admins.find_one({"email": "admin@accompagn-sante.fr"})
    if not existing_admin:
        from utils.auth import hash_password
        from models import AdminUser
        admin = AdminUser(
            email="admin@accompagn-sante.fr",
            password_hash=hash_password("Admin2024!"),
            nom="Administrateur"
        )
        doc = admin.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.admins.insert_one(doc)
        logger.info("Default admin created on startup")

    # Initialize cron config if not exists
    cron_config = await db.app_config.find_one({"key": "reminder_cron"}, {"_id": 0})
    if not cron_config:
        await db.app_config.insert_one({
            "key": "reminder_cron",
            "enabled": True,
            "hour": 9,
            "minute": 0,
            "last_run": None,
            "last_results": None,
        })
        logger.info("Reminder cron config initialized (enabled, 9h00)")

    # Start the daily reminder scheduler
    asyncio.create_task(_daily_reminder_scheduler())

    # Start the campaign scheduler (checks every minute)
    asyncio.create_task(_campaign_scheduler())


async def _campaign_scheduler():
    """Background task that checks for scheduled campaigns to execute."""
    logger.info("Campaign scheduler started")
    while True:
        try:
            now = datetime.now(timezone.utc)
            # Find campaigns that are due
            due_campaigns = await db.scheduled_campaigns.find({
                "status": "scheduled",
                "scheduled_at": {"$lte": now.isoformat()}
            }, {"_id": 0}).to_list(10)

            for campaign in due_campaigns:
                await _execute_campaign(campaign)

            await asyncio.sleep(60)  # Check every minute

        except Exception as e:
            logger.error(f"Campaign scheduler error: {e}")
            await asyncio.sleep(120)


async def _execute_campaign(campaign: dict):
    """Execute a scheduled campaign: send the template to target clients."""
    from utils.email import resolve_template_variables, build_missing_docs_html, SAMPLE_CONTEXT
    from config import RESEND_AVAILABLE, SENDER_EMAIL

    campaign_id = campaign["id"]
    template_id = campaign["template_id"]
    target = campaign.get("target", "inactive_clients")
    ab_test_id = campaign.get("ab_test_id")

    logger.info(f"Executing campaign {campaign_id} (template={campaign.get('template_name')})")

    # Mark as executing
    await db.scheduled_campaigns.update_one(
        {"id": campaign_id}, {"$set": {"status": "executing"}}
    )

    # Load template
    tpl = await db.email_templates.find_one({"id": template_id}, {"_id": 0})
    if not tpl:
        await db.scheduled_campaigns.update_one(
            {"id": campaign_id},
            {"$set": {"status": "failed", "error": "Template introuvable", "executed_at": datetime.now(timezone.utc).isoformat()}}
        )
        return

    # Load AB test variants if applicable
    ab_variants = []
    if ab_test_id:
        ab_test = await db.ab_tests.find_one({"id": ab_test_id}, {"_id": 0})
        if ab_test:
            ab_variants = ab_test.get("variants", [])

    # Find target clients
    query = {}
    if target == "inactive_clients":
        cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        query = {"last_upload": {"$lt": cutoff}}
    # For "all_clients", no filter

    clients = await db.client_cases.find(query, {"_id": 0}).to_list(500)
    recipients_count = len(clients)
    sent_count = 0
    failed_count = 0
    site_url = os.environ.get("FRONTEND_URL", SITE_URL)

    for i, client_doc in enumerate(clients):
        try:
            email = client_doc.get("email", "")
            if not email:
                continue

            prenom = client_doc.get("prenom", client_doc.get("nom", "Client"))
            nom = client_doc.get("nom", "")
            comp_pct = client_doc.get("completeness_pct", 0)
            missing = client_doc.get("missing_docs", [])

            # Choose template content (AB variant or main template)
            if ab_variants and len(ab_variants) > 1:
                variant = ab_variants[i % len(ab_variants)]
                content = {
                    "subject": variant.get("subject", tpl.get("subject", "")),
                    "intro": variant.get("intro", tpl.get("intro", "")),
                    "motivation": variant.get("motivation", tpl.get("motivation", "")),
                    "cta_text": variant.get("cta_text", tpl.get("cta_text", "Compléter mon dossier")),
                }
            else:
                content = tpl

            # Resolve variables
            ctx = {
                "prenom": prenom,
                "nom": nom,
                "completeness": str(comp_pct),
                "documents_missing": build_missing_docs_html(missing),
                "date_inscription": client_doc.get("created_at", "")[:10] if client_doc.get("created_at") else "",
            }

            subject = resolve_template_variables(content.get("subject", ""), ctx)
            intro = resolve_template_variables(content.get("intro", ""), ctx)
            motivation = resolve_template_variables(content.get("motivation", ""), ctx)
            cta_text = resolve_template_variables(content.get("cta_text", "Compléter mon dossier"), ctx)

            record_id = str(uuid.uuid4())

            html = f"""
            <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:0;background:#f5f5f5;">
            <div style="background:#1a1a2e;color:#fff;padding:24px;text-align:center;">
                <h1 style="margin:0;color:#d4a44a;font-size:20px;">Stratégie &amp; Expertise Santé</h1>
            </div>
            <div style="background:#FFFFFF;padding:24px;border:1px solid #E5E0D6;">
                <p style="font-size:16px;">Bonjour <strong>{prenom}</strong>,</p>
                <p>{intro}</p>
                <div style="background:#F0F7F0;padding:16px;border-radius:8px;text-align:center;margin:20px 0;">
                    <p style="margin:0;font-size:36px;font-weight:bold;color:#f59e0b;">{comp_pct}%</p>
                    <p style="margin:4px 0 0;color:#666;font-size:13px;">de complétude</p>
                </div>
                <p style="color:#555;font-size:14px;">{motivation}</p>
                <div style="text-align:center;margin:24px 0;">
                    <a href="{site_url}/api/track/click/{record_id}"
                       style="background:#1a1a2e;color:#d4a44a;padding:14px 28px;border-radius:6px;text-decoration:none;display:inline-block;font-weight:600;font-size:14px;">
                        {cta_text}</a>
                </div>
            </div>
            <img src="{site_url}/api/track/open/{record_id}" width="1" height="1" style="display:none;" alt="" />
            </body></html>
            """

            if RESEND_AVAILABLE and os.environ.get("RESEND_API_KEY"):
                import resend
                resend.api_key = os.environ.get("RESEND_API_KEY", "")
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [email],
                    "subject": subject,
                    "html": html
                })

            # Track as inactivity reminder for KPI tracking
            await db.inactivity_reminders.insert_one({
                "id": record_id,
                "client_id": client_doc.get("client_id", ""),
                "client_email": email,
                "campaign_id": campaign_id,
                "ab_test_id": ab_test_id if ab_variants else None,
                "ab_variant": ab_variants[i % len(ab_variants)]["name"] if ab_variants else None,
                "level": 0,
                "status": "sent",
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            sent_count += 1

        except Exception as e:
            failed_count += 1
            logger.error(f"Campaign {campaign_id} send error for client: {e}")

    # Update campaign status
    await db.scheduled_campaigns.update_one(
        {"id": campaign_id},
        {"$set": {
            "status": "sent",
            "recipients_count": recipients_count,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }}
    )
    logger.info(f"Campaign {campaign_id} completed: {sent_count}/{recipients_count} sent")


async def _daily_reminder_scheduler():
    """Background task that runs inactivity reminders daily at the configured hour."""
    logger.info("Daily reminder scheduler started")
    while True:
        try:
            config = await db.app_config.find_one({"key": "reminder_cron"}, {"_id": 0})
            if not config or not config.get("enabled"):
                await asyncio.sleep(300)  # Check again in 5 min
                continue

            now = datetime.now(timezone.utc)
            target_hour = config.get("hour", 9)
            target_minute = config.get("minute", 0)

            # Check if we already ran today
            last_run = config.get("last_run")
            if last_run:
                last_run_date = last_run[:10] if isinstance(last_run, str) else str(last_run)[:10]
                today_str = now.strftime("%Y-%m-%d")
                if last_run_date == today_str:
                    await asyncio.sleep(300)
                    continue

            # Check if it's time to run
            if now.hour >= target_hour and now.minute >= target_minute:
                logger.info("Running scheduled inactivity reminders...")
                from utils.email import run_inactivity_reminders
                results = await run_inactivity_reminders()
                await db.app_config.update_one(
                    {"key": "reminder_cron"},
                    {"$set": {"last_run": now.isoformat(), "last_results": results}}
                )
                logger.info(f"Scheduled reminders completed: {results}")

            await asyncio.sleep(300)  # Check every 5 min

        except Exception as e:
            logger.error(f"Reminder scheduler error: {e}")
            await asyncio.sleep(600)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
