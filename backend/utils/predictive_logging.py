"""
PREDICTIVE V2 LOGGING — Tracabilite complete des actions V2
=============================================================
Journalise toutes les actions liees a la V2 predictive :
activation, desactivation, tests sandbox, changements de config.
"""

import logging
from datetime import datetime, timezone
import uuid

logger = logging.getLogger("config")


async def log_v2_event(db, event_type: str, admin_email: str, details: dict = None):
    """
    Enregistre un evenement V2 dans la collection v2_audit_log.
    """
    record = {
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "admin_email": admin_email,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await db.v2_audit_log.insert_one(record)
        logger.info(f"[V2_AUDIT] {event_type} by {admin_email}")
    except Exception as e:
        logger.warning(f"[V2_AUDIT] Failed to log event: {e}")
    return record["id"]


async def get_v2_audit_log(db, limit=50):
    """Recupere les derniers evenements V2."""
    docs = await db.v2_audit_log.find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).to_list(limit)
    return docs
