from fastapi import APIRouter, Request, Depends
from datetime import datetime, timezone, timedelta
from config import db, logger
from utils.auth import get_current_admin

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


@router.post("/contact-visit")
async def track_contact_visit(request: Request):
    """Track a visit to /contact with attribution params."""
    try:
        body = await request.json()
        via = body.get("via", "")
        source = body.get("source", "")
        campaign = body.get("campaign", "")

        if not via and not source:
            return {"status": "ok"}

        visit = {
            "via": via,
            "source": source,
            "campaign": campaign,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", ""),
        }
        await db.contact_visits.insert_one(visit)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Contact visit tracking error: {e}")
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


@router.get("/conversion-analytics")
async def get_conversion_analytics(period: str = "30d", admin: dict = Depends(get_current_admin)):
    """Admin endpoint: conversion funnel analytics by source."""
    days = 7 if period == "7d" else 30
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    # Visits by via+source
    visit_pipeline = [
        {"$match": {"date": {"$gte": cutoff}}},
        {"$group": {
            "_id": {"via": "$via", "source": "$source"},
            "visits": {"$sum": 1},
        }},
        {"$sort": {"visits": -1}},
    ]
    visit_agg = await db.contact_visits.aggregate(visit_pipeline).to_list(50)

    # Contacts (form submissions) by via+source
    contact_pipeline = [
        {"$match": {"created_at": {"$gte": cutoff}, "tracking_via": {"$ne": None}}},
        {"$group": {
            "_id": {"via": "$tracking_via", "source": "$tracking_source"},
            "contacts": {"$sum": 1},
        }},
    ]
    contact_agg = await db.contacts.aggregate(contact_pipeline).to_list(50)

    # Build channel map
    channels = {}
    for v in visit_agg:
        key = f"{v['_id'].get('via', 'direct')}|{v['_id'].get('source', '')}"
        channels[key] = {"via": v["_id"].get("via", "direct"), "source": v["_id"].get("source", ""), "visits": v["visits"], "contacts": 0}

    for c in contact_agg:
        key = f"{c['_id'].get('via', 'direct')}|{c['_id'].get('source', '')}"
        if key in channels:
            channels[key]["contacts"] = c["contacts"]
        else:
            channels[key] = {"via": c["_id"].get("via", "direct"), "source": c["_id"].get("source", ""), "visits": 0, "contacts": c["contacts"]}

    # Calculate conversion rates
    channel_list = []
    for ch in channels.values():
        v = ch["visits"]
        c = ch["contacts"]
        ch["conversion_rate"] = round((c / v) * 100, 1) if v > 0 else 0
        channel_list.append(ch)

    channel_list.sort(key=lambda x: x["visits"], reverse=True)

    # Daily timeseries
    daily_pipeline = [
        {"$match": {"date": {"$gte": cutoff}}},
        {"$group": {"_id": "$date", "visits": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    daily_visits = await db.contact_visits.aggregate(daily_pipeline).to_list(60)

    daily_contacts_pipeline = [
        {"$match": {"created_at": {"$gte": cutoff}, "tracking_via": {"$ne": None}}},
        {"$addFields": {"date_str": {"$substr": ["$created_at", 0, 10]}}},
        {"$group": {"_id": "$date_str", "contacts": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    daily_contacts = await db.contacts.aggregate(daily_contacts_pipeline).to_list(60)

    contact_by_date = {d["_id"]: d["contacts"] for d in daily_contacts}
    visit_by_date = {d["_id"]: d["visits"] for d in daily_visits}

    timeseries = []
    for i in range(days):
        dt = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        timeseries.append({
            "date": dt,
            "visits": visit_by_date.get(dt, 0),
            "contacts": contact_by_date.get(dt, 0),
        })

    # Totals
    total_visits = sum(ch["visits"] for ch in channel_list)
    total_contacts = sum(ch["contacts"] for ch in channel_list)

    return {
        "channels": channel_list,
        "timeseries": timeseries,
        "totals": {
            "visits": total_visits,
            "contacts": total_contacts,
            "conversion_rate": round((total_contacts / total_visits) * 100, 1) if total_visits > 0 else 0,
        },
        "period": period,
    }
