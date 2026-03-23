from fastapi import APIRouter, Request
from datetime import datetime, timezone
from config import db, logger

router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.post("/event")
async def track_event(request: Request):
    """Track page views and CTA clicks for conversion analysis."""
    try:
        body = await request.json()
        page = body.get("page", "unknown")
        action = body.get("action", "unknown")

        event = {
            "page": page,
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", ""),
        }

        await db.tracking_events.insert_one(event)

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Tracking error: {e}")
        return {"status": "ok"}


@router.get("/stats")
async def get_tracking_stats(page: str = None):
    """Get aggregated tracking statistics for admin use."""
    try:
        match_filter = {}
        if page:
            match_filter["page"] = page

        pipeline = [
            {"$match": match_filter},
            {"$group": {
                "_id": {"page": "$page", "action": "$action"},
                "count": {"$sum": 1},
                "last_event": {"$max": "$timestamp"}
            }},
            {"$sort": {"count": -1}}
        ]

        results = await db.tracking_events.aggregate(pipeline).to_list(100)

        stats = []
        for r in results:
            stats.append({
                "page": r["_id"]["page"],
                "action": r["_id"]["action"],
                "count": r["count"],
                "last_event": r.get("last_event", "")
            })

        return {"stats": stats}
    except Exception as e:
        logger.error(f"Tracking stats error: {e}")
        return {"stats": []}
