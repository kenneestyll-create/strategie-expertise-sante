from fastapi import FastAPI, APIRouter, Request as FastAPIRequest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import Response, RedirectResponse, JSONResponse
from starlette.requests import Request
from slowapi.errors import RateLimitExceeded
import asyncio
import os
import uuid
from datetime import datetime, timezone, timedelta, time as dtime

from config import client, db, logger, SITE_URL, limiter
from routes import all_routers


# ==================== PURE ASGI MIDDLEWARE (no BaseHTTPMiddleware) ====================

class SecurityHeadersASGIMiddleware:
    """Adds security headers to all HTTP responses. Pure ASGI — no body deadlock."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend([
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"x-xss-protection", b"1; mode=block"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                ])
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_wrapper)


class CacheControlASGIMiddleware:
    """Adds Cache-Control headers for specific paths. Pure ASGI — no body deadlock."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                cache_val = None
                if path.startswith("/api/faq") or path.startswith("/api/avis") or path.startswith("/api/visitors"):
                    cache_val = b"public, max-age=300"
                elif path.startswith("/api/sitemap") or path.startswith("/api/robots"):
                    cache_val = b"public, max-age=86400"
                elif path == "/api/health":
                    cache_val = b"no-cache, no-store, must-revalidate"
                if cache_val:
                    headers = list(message.get("headers", []))
                    headers.append((b"cache-control", cache_val))
                    message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_wrapper)


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
app.add_middleware(CacheControlASGIMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(SecurityHeadersASGIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ==================== GUIDE FOLLOWUP TRACKING ====================

@app.get("/api/track/guide-open/{followup_id}")
async def track_guide_followup_open(followup_id: str):
    """Tracking pixel for guide followup emails."""
    now = datetime.now(timezone.utc).isoformat()
    await db.guide_followups.update_one(
        {"id": followup_id, "opened_at": {"$exists": False}},
        {"$set": {"opened_at": now, "opened": True}}
    )
    return Response(content=PIXEL, media_type="image/png", headers={"Cache-Control": "no-store, no-cache"})

@app.get("/api/track/guide-click/{followup_id}")
async def track_guide_followup_click(followup_id: str):
    """CTA click tracking for guide followups — redirects to StrategiIA."""
    now = datetime.now(timezone.utc).isoformat()
    await db.guide_followups.update_one(
        {"id": followup_id, "clicked_at": {"$exists": False}},
        {"$set": {"clicked_at": now, "clicked": True}}
    )
    # Redirect to homepage where StrategiIA can be opened
    return RedirectResponse(url=f"{SITE_URL}/?open=strategiia", status_code=302)





@app.on_event("startup")
async def startup_db_client():
    logger.info("Starting up: connected to MongoDB")
    await db.command("ping")
    logger.info("MongoDB ping successful")

    # Initialize object storage
    try:
        from utils.storage import init_storage, ensure_bucket
        init_storage()
        ensure_bucket()
        logger.info("Object storage initialized, bucket verified")
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

    # Auto-seed missing SEO pages (idempotent — only inserts missing slugs, never overwrites)
    try:
        from seed_seo_pages import seed_missing_only
        seo_report = await seed_missing_only(db)
        if seo_report["created"] > 0:
            logger.info(f"SEO auto-seed: {seo_report['created']} new page(s) inserted "
                        f"({seo_report['skipped']} already present, {seo_report['total_in_seed']} total in seed)")
    except Exception as e:
        logger.warning(f"SEO auto-seed skipped (non-blocking): {e}")

    # Apply pending SEO title/description migrations (idempotent — tracks applied IDs in seo_migrations)
    try:
        from utils.seo_migrations import apply_pending_migrations
        mig_report = await apply_pending_migrations(db)
        if mig_report["applied"]:
            logger.info(f"SEO migrations applied: {mig_report['applied']}")
    except Exception as e:
        logger.warning(f"SEO migrations skipped (non-blocking): {e}")

    # Auto-seed Kit Professionnel prompts (idempotent — only inserts if collection empty)
    try:
        from services.kit_professionnel import ensure_kit_prompts_seeded
        await ensure_kit_prompts_seeded()
    except Exception as e:
        logger.warning(f"Kit Pro prompts seed skipped (non-blocking): {e}")

    # Auto-snapshot AI agents state (idempotent — only creates if config hash differs)
    try:
        from routes.agents_versions import maybe_auto_snapshot
        await maybe_auto_snapshot()
    except Exception as e:
        logger.warning(f"agents_versions auto-snapshot skipped (non-blocking): {e}")

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

    # Start the guide followup scheduler (checks every hour)
    asyncio.create_task(_guide_followup_scheduler())

    # Start the data purge scheduler (runs daily at 3:00 AM)
    asyncio.create_task(_data_purge_scheduler())

    # Start the weekly report scheduler (checks daily at configured hour)
    asyncio.create_task(_weekly_report_scheduler())


# ==================== GUIDE FOLLOWUP EMAIL TEMPLATES ====================

GUIDE_FOLLOWUP_TEMPLATES = {
    "Maladie professionnelle": {
        "subject": "Votre guide sur la déclaration MP — et ensuite ?",
        "intro": "vous avez récemment téléchargé notre guide <strong>«\u00a0{guide_title}\u00a0»</strong>. Nous espérons qu'il vous a été utile pour mieux comprendre les démarches liées à la reconnaissance d'une maladie professionnelle.",
        "body": "Chaque situation est unique. Les tableaux de maladies professionnelles, les délais de prise en charge et les taux d'IPP varient considérablement d'un dossier à l'autre. Une analyse personnalisée de votre situation peut vous aider à identifier précisément vos droits et les démarches prioritaires à engager.",
        "cta_text": "Lancer ma pré-analyse StratégiIA",
    },
    "Accident du travail": {
        "subject": "Votre guide AT/IPP — allez plus loin dans votre démarche",
        "intro": "vous avez récemment téléchargé notre guide <strong>«\u00a0{guide_title}\u00a0»</strong>. La compréhension du taux d'IPP et de son impact sur votre indemnisation est une étape essentielle.",
        "body": "Le calcul de votre indemnisation dépend de nombreux facteurs : votre taux d'IPP, votre situation professionnelle, les barèmes en vigueur et les jurisprudences récentes. Notre outil StratégiIA peut croiser l'ensemble de ces données pour vous donner une vision claire de vos droits.",
        "cta_text": "Lancer ma pré-analyse StratégiIA",
    },
    "Expertise médicale": {
        "subject": "Votre expertise médicale approche ? Préparez-vous efficacement",
        "intro": "vous avez récemment téléchargé notre guide <strong>«\u00a0{guide_title}\u00a0»</strong>. La préparation d'une expertise médicale est un moment déterminant pour la reconnaissance de vos droits.",
        "body": "Une expertise bien préparée peut faire toute la différence sur l'évaluation de vos séquelles et le montant de votre indemnisation. Avant de vous y rendre, une analyse préalable de votre situation peut vous aider à identifier les points clés à défendre et les erreurs à éviter.",
        "cta_text": "Analyser ma situation avant l'expertise",
    },
    "MDPH": {
        "subject": "Votre dossier MDPH — optimisez vos chances",
        "intro": "vous avez récemment téléchargé notre guide <strong>«\u00a0{guide_title}\u00a0»</strong>. Constituer un dossier MDPH solide demande une préparation rigoureuse.",
        "body": "Le taux d'incapacité reconnu par la MDPH conditionne l'accès à de nombreux droits : AAH, carte mobilité inclusion, orientation professionnelle. Une pré-analyse de votre situation peut vous aider à structurer votre dossier de manière optimale.",
        "cta_text": "Lancer ma pré-analyse StratégiIA",
    },
    "Recours": {
        "subject": "Contester un refus — ne restez pas sans réponse",
        "intro": "vous avez récemment téléchargé notre guide <strong>«\u00a0{guide_title}\u00a0»</strong>. Faire face à un refus peut être décourageant, mais des recours existent et sont souvent fructueux.",
        "body": "Qu'il s'agisse d'une CRA, d'un RAPO ou d'un recours contentieux, la stratégie adoptée est déterminante. Notre outil StratégiIA peut analyser votre situation et vous indiquer le recours le plus adapté, en s'appuyant sur les jurisprudences récentes.",
        "cta_text": "Analyser mes options de recours",
    },
    "Assurances": {
        "subject": "Protection juridique — activez vos droits",
        "intro": "vous avez récemment téléchargé notre guide <strong>«\u00a0{guide_title}\u00a0»</strong>. Votre contrat d'assurance contient peut-être des garanties que vous n'exploitez pas encore.",
        "body": "La protection juridique est un levier souvent méconnu. Elle peut financer l'assistance d'un médecin conseil, d'un avocat spécialisé ou les frais de procédure. Une analyse de votre situation peut vous aider à identifier les garanties activables.",
        "cta_text": "Lancer ma pré-analyse StratégiIA",
    },
}

# Default template for unknown categories
GUIDE_FOLLOWUP_DEFAULT = {
    "subject": "Suite à votre téléchargement — une analyse personnalisée ?",
    "intro": "vous avez récemment téléchargé notre guide <strong>«\u00a0{guide_title}\u00a0»</strong>. Nous espérons qu'il vous a apporté des réponses utiles.",
    "body": "Chaque situation est unique et mérite une analyse personnalisée. Notre outil StratégiIA croise jurisprudences, barèmes et cas similaires pour vous donner un diagnostic précis de vos droits et des démarches prioritaires à engager.",
    "cta_text": "Lancer ma pré-analyse StratégiIA",
}


def _build_guide_followup_html(lead: dict, followup_id: str) -> tuple:
    """Build the personalized followup email HTML and subject."""
    category = lead.get("category", "")
    guide_title = lead.get("guide_title", "votre guide")
    template = GUIDE_FOLLOWUP_TEMPLATES.get(category, GUIDE_FOLLOWUP_DEFAULT)

    subject = template["subject"]
    intro = template["intro"].replace("{guide_title}", guide_title)
    body = template["body"]
    cta_text = template["cta_text"]
    site_url = SITE_URL

    html = f"""
    <html><body style="font-family:'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;padding:0;background:#f5f0e8;">
    <div style="background:#0a0a08;padding:28px 24px;text-align:center;">
        <h1 style="margin:0;color:#C9A84C;font-size:20px;letter-spacing:0.05em;">Stratégie &amp; Expertise Santé</h1>
        <p style="margin:6px 0 0;color:#999;font-size:11px;text-transform:uppercase;letter-spacing:0.15em;">Accompagnement stratégique</p>
    </div>
    <div style="background:#FFFFFF;padding:28px 24px;border-left:1px solid #e5e0d6;border-right:1px solid #e5e0d6;">
        <p style="font-size:15px;color:#333;line-height:1.6;">Bonjour,</p>
        <p style="font-size:14px;color:#555;line-height:1.7;">{intro}</p>
        <p style="font-size:14px;color:#555;line-height:1.7;">{body}</p>
        <div style="text-align:center;margin:28px 0;">
            <a href="{site_url}/api/track/guide-click/{followup_id}"
               style="background:#0a0a08;color:#C9A84C;padding:14px 32px;border-radius:50px;text-decoration:none;display:inline-block;font-weight:600;font-size:14px;letter-spacing:0.02em;">
                {cta_text}
            </a>
        </div>
        <p style="font-size:12px;color:#999;text-align:center;margin-top:24px;line-height:1.6;">
            Cette pré-analyse est gratuite, confidentielle et sans engagement.<br/>
            Elle prend moins de 2 minutes.
        </p>
    </div>
    <div style="background:#0a0a08;padding:20px 24px;text-align:center;border-top:2px solid #C9A84C;">
        <p style="margin:0;color:#666;font-size:11px;">Stratégie &amp; Expertise Santé — Pionnier en France</p>
        <p style="margin:4px 0 0;color:#555;font-size:10px;">Cet email fait suite à votre téléchargement de guide. Vous ne recevrez pas d'autre relance automatique pour ce guide.</p>
    </div>
    <img src="{site_url}/api/track/guide-open/{followup_id}" width="1" height="1" style="display:none;" alt="" />
    </body></html>
    """
    return subject, html


async def _data_purge_scheduler():
    """Background task: purges sensitive OCR text from completed dossiers after 30 days.
    Runs daily at 3:00 AM. Logs every purge operation for audit trail."""
    logger.info("Data purge scheduler started")
    while True:
        try:
            now = datetime.now(timezone.utc)
            # Wait until 3:00 AM
            target = now.replace(hour=3, minute=0, second=0, microsecond=0)
            if now >= target:
                target += timedelta(days=1)
            wait_secs = (target - now).total_seconds()
            await asyncio.sleep(wait_secs)

            # Purge documents_text from completed dossiers older than 30 days
            cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            result = await db.dossier_express.update_many(
                {
                    "status": "completed",
                    "completed_at": {"$lte": cutoff},
                    "documents_text": {"$exists": True, "$ne": ""},
                },
                {"$set": {"documents_text": "", "documents_text_purged": True, "purged_at": datetime.now(timezone.utc).isoformat()}}
            )
            if result.modified_count > 0:
                logger.info(f"DATA PURGE: Purged documents_text from {result.modified_count} completed dossier(s) older than 30 days")
                # Log the purge event for audit
                await db.purge_log.insert_one({
                    "type": "documents_text_purge",
                    "count": result.modified_count,
                    "cutoff_date": cutoff,
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                })
            else:
                logger.info("DATA PURGE: No dossiers to purge today")

            # Purge original files from Object Storage for old completed dossiers
            try:
                from utils.storage import get_object
                dossiers_with_files = await db.dossier_express.find(
                    {
                        "status": "completed",
                        "completed_at": {"$lte": cutoff},
                        "original_documents": {"$exists": True, "$ne": []},
                        "original_documents_purged": {"$ne": True},
                    },
                    {"_id": 0, "id": 1, "original_documents": 1}
                ).to_list(100)

                files_purged = 0
                for dossier in dossiers_with_files:
                    # Mark as purged (we can't delete from Object Storage, but we clear the references)
                    await db.dossier_express.update_one(
                        {"id": dossier["id"]},
                        {"$set": {"original_documents": [], "original_documents_purged": True, "files_purged_at": datetime.now(timezone.utc).isoformat()}}
                    )
                    files_purged += len(dossier.get("original_documents", []))

                if files_purged > 0:
                    logger.info(f"DATA PURGE: Cleared {files_purged} original file reference(s) from {len(dossiers_with_files)} dossier(s)")
                    await db.purge_log.insert_one({
                        "type": "original_files_purge",
                        "files_count": files_purged,
                        "dossiers_count": len(dossiers_with_files),
                        "cutoff_date": cutoff,
                        "executed_at": datetime.now(timezone.utc).isoformat(),
                    })
            except Exception as e:
                logger.warning(f"Original files purge step failed: {e}")

        except Exception as e:
            logger.error(f"Data purge scheduler error: {e}")
            await asyncio.sleep(3600)


async def _guide_followup_scheduler():
    """Background task: sends followup emails 48h after guide download."""
    logger.info("Guide followup scheduler started")
    while True:
        try:
            from config import RESEND_AVAILABLE, SENDER_EMAIL

            # Find leads that are 48h+ old and haven't been sent a followup
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
            leads = await db.guide_leads.find(
                {
                    "followup_sent": {"$ne": True},
                    "created_at": {"$lte": cutoff},
                },
                {"_id": 0}
            ).to_list(50)

            if leads:
                logger.info(f"Guide followup: {len(leads)} emails to send")

            sent = 0
            for lead in leads:
                try:
                    email = lead.get("email", "")
                    if not email:
                        continue

                    followup_id = str(uuid.uuid4())
                    subject, html = _build_guide_followup_html(lead, followup_id)

                    if RESEND_AVAILABLE and os.environ.get("RESEND_API_KEY"):
                        import resend
                        resend.api_key = os.environ.get("RESEND_API_KEY", "")
                        await asyncio.to_thread(resend.Emails.send, {
                            "from": SENDER_EMAIL,
                            "to": [email],
                            "subject": subject,
                            "html": html,
                        })

                    # Track the followup
                    await db.guide_followups.insert_one({
                        "id": followup_id,
                        "email": email,
                        "guide_id": lead.get("guide_id", ""),
                        "guide_title": lead.get("guide_title", ""),
                        "category": lead.get("category", ""),
                        "status": "sent",
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                    })

                    # Mark the lead as processed
                    await db.guide_leads.update_one(
                        {"email": email, "guide_id": lead.get("guide_id")},
                        {"$set": {"followup_sent": True, "followup_id": followup_id, "followup_sent_at": datetime.now(timezone.utc).isoformat()}}
                    )
                    sent += 1

                except Exception as e:
                    logger.error(f"Guide followup send error for {lead.get('email')}: {e}")

            if sent:
                logger.info(f"Guide followup: {sent}/{len(leads)} emails sent")

            await asyncio.sleep(3600)  # Check every hour

        except Exception as e:
            logger.error(f"Guide followup scheduler error: {e}")
            await asyncio.sleep(3600)


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


async def _weekly_report_scheduler():
    """Send weekly report email on the configured day and hour."""
    await asyncio.sleep(120)
    logger.info("Weekly report scheduler started")
    while True:
        try:
            config = await db.site_settings.find_one({"id": "weekly_report_config"}, {"_id": 0})
            if not config:
                config = {"enabled": True, "day": "monday", "hour": 8, "email": ""}

            if config.get("enabled"):
                now = datetime.now(timezone.utc)
                target_day = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}.get(config.get("day", "monday"), 0)
                target_hour = config.get("hour", 8)

                if now.weekday() == target_day and now.hour == target_hour:
                    today_str = now.strftime("%Y-%m-%d")
                    already_sent = await db.weekly_report_history.find_one({"sent_at": {"$regex": f"^{today_str}"}}, {"_id": 0})
                    if not already_sent:
                        from config import RESEND_AVAILABLE, SENDER_EMAIL, NOTIFICATION_EMAIL
                        if RESEND_AVAILABLE:
                            from routes.admin import _generate_weekly_report_data, _build_weekly_report_html
                            data = await _generate_weekly_report_data()
                            html = _build_weekly_report_html(data)
                            email_to = config.get("email") or NOTIFICATION_EMAIL or "contact@strategie-expertise-sante.fr"
                            try:
                                import resend
                                await asyncio.to_thread(resend.Emails.send, {
                                    "from": SENDER_EMAIL,
                                    "to": [email_to],
                                    "subject": f"Rapport hebdomadaire S.E.S. — {data['period']}",
                                    "html": html,
                                })
                                await db.weekly_report_history.insert_one({
                                    "sent_at": now.isoformat(),
                                    "email": email_to,
                                    "data": data,
                                    "trigger": "auto",
                                })
                                logger.info(f"Weekly report sent to {email_to}")
                            except Exception as e:
                                logger.error(f"Weekly report send error: {e}")

            await asyncio.sleep(3600)
        except Exception as e:
            logger.error(f"Weekly report scheduler error: {e}")
            await asyncio.sleep(3600)



@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
