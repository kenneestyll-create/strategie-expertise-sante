from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from config import client, db, logger
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


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
