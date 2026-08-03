"""Suivi d'etat des composants critiques (supervision admin — P2, 04/08/2026)."""
from datetime import datetime, timezone
from config import db, logger


async def record_status(component: str, ok: bool, detail: str = ""):
    """Enregistre le dernier resultat connu d'un composant (email, storage, pdf...)."""
    try:
        await db.system_status.update_one(
            {"id": component},
            {"$set": {
                "id": component,
                "ok": ok,
                "detail": detail[:300],
                "at": datetime.now(timezone.utc).isoformat(),
            }},
            upsert=True,
        )
    except Exception as e:
        logger.warning(f"[SYSTEM_STATUS] record {component} failed (non-blocking): {e}")
