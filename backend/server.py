from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import Response, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import asyncio
from datetime import datetime, timezone, time as dtime

from config import client, db, logger, SITE_URL
from routes import all_routers

app = FastAPI(title="Stratégie & Expertise Santé API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
