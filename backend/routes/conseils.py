from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone, timedelta
from bson import ObjectId
import math
from utils.auth import get_current_admin
from config import db

router = APIRouter(prefix="/conseils", tags=["conseils"])

CATEGORIES = ["droits", "expertise", "indemnisation", "emploi", "demarches", "strategie", "actualite"]
LINK_OPTIONS = ["/calculatrice-ipp", "/dossier-express", "/ressources", "/simulateur", "/contact", "/accident-travail-maladie-professionnelle"]

DEFAULT_CONSEILS = [
    {"text": "Vous disposez en général de 2 ans pour déclarer une maladie professionnelle après le diagnostic.", "category": "droits", "link": "/ressources", "link_label": "Voir les ressources"},
    {"text": "Une contestation d'une décision de la CPAM doit être faite dans un délai de 2 mois.", "category": "droits", "link": "/ressources", "link_label": "En savoir plus"},
    {"text": "Un accident du travail doit être déclaré dans les 24 heures par l'employeur.", "category": "droits", "link": "/accident-travail-maladie-professionnelle", "link_label": "Accidents du travail"},
    {"text": "Vous pouvez déclarer vous-même un accident si l'employeur ne le fait pas.", "category": "droits", "link": "/ressources", "link_label": "Voir les démarches"},
    {"text": "Une rechute peut être reconnue même plusieurs années après consolidation.", "category": "droits", "link": "/simulateur", "link_label": "Analyser votre cas"},
    {"text": "Vous pouvez être assisté par un médecin lors d'une expertise.", "category": "expertise", "link": "/ressources", "link_label": "Préparer une expertise"},
    {"text": "Préparer ses documents médicaux est essentiel avant toute expertise.", "category": "expertise", "link": "/dossier-express", "link_label": "Dossier Express IA"},
    {"text": "Vous avez le droit de contester une expertise médicale.", "category": "expertise", "link": "/ressources", "link_label": "Vos droits"},
    {"text": "Le médecin expert doit rester indépendant.", "category": "expertise", "link": "/ressources", "link_label": "En savoir plus"},
    {"text": "Un rapport médical incomplet peut être contesté.", "category": "expertise", "link": "/simulateur", "link_label": "Analyser votre dossier"},
    {"text": "Une incapacité permanente donne droit à une indemnisation.", "category": "indemnisation", "link": "/calculatrice-ipp", "link_label": "Calculer votre IPP"},
    {"text": "Le taux d'IPP influence directement le montant de l'indemnisation.", "category": "indemnisation", "link": "/calculatrice-ipp", "link_label": "Calculatrice IPP"},
    {"text": "Une faute inexcusable de l'employeur peut majorer votre indemnisation.", "category": "indemnisation", "link": "/simulateur", "link_label": "Analyser avec StratégiIA"},
    {"text": "Certains préjudices ne sont pas automatiquement indemnisés.", "category": "indemnisation", "link": "/ressources", "link_label": "Voir les ressources"},
    {"text": "Une perte de carrière peut être reconnue sous conditions.", "category": "indemnisation", "link": "/ressources", "link_label": "IP et PGPF"},
    {"text": "Une inaptitude peut ouvrir droit à des indemnités spécifiques.", "category": "emploi", "link": "/ressources", "link_label": "Vos droits"},
    {"text": "Le reclassement professionnel est une obligation de l'employeur.", "category": "emploi", "link": "/accident-travail-maladie-professionnelle", "link_label": "En savoir plus"},
    {"text": "Une invalidité ne met pas fin automatiquement au contrat de travail.", "category": "emploi", "link": "/ressources", "link_label": "Voir les ressources"},
    {"text": "Vous pouvez cumuler certaines aides selon votre situation.", "category": "emploi", "link": "/ressources", "link_label": "Aides disponibles"},
    {"text": "Une reconversion peut être financée dans certains cas.", "category": "emploi", "link": "/ressources", "link_label": "En savoir plus"},
    {"text": "Conservez toujours une copie de vos documents médicaux.", "category": "demarches", "link": "/dossier-express", "link_label": "Dossier Express IA"},
    {"text": "Les échanges avec la CPAM doivent être tracés.", "category": "demarches", "link": "/ressources", "link_label": "Voir les guides"},
    {"text": "Un dossier incomplet peut ralentir votre indemnisation.", "category": "demarches", "link": "/dossier-express", "link_label": "Complétez votre dossier"},
    {"text": "Il est possible de se faire accompagner dans ses démarches.", "category": "demarches", "link": "/contact", "link_label": "Nous contacter"},
    {"text": "Une demande peut être réexaminée avec de nouveaux éléments.", "category": "demarches", "link": "/simulateur", "link_label": "Analyser votre situation"},
    {"text": "Anticiper une expertise améliore souvent son résultat.", "category": "strategie", "link": "/dossier-express", "link_label": "Dossier Express IA"},
    {"text": "Une bonne préparation peut influencer une décision.", "category": "strategie", "link": "/simulateur", "link_label": "StratégiIA"},
    {"text": "Chaque situation est unique et mérite une analyse personnalisée.", "category": "strategie", "link": "/simulateur", "link_label": "Analyser mon cas"},
    {"text": "Ne pas agir dans les délais peut faire perdre des droits.", "category": "strategie", "link": "/ressources", "link_label": "Délais importants"},
    {"text": "Se faire accompagner permet souvent d'optimiser ses démarches.", "category": "strategie", "link": "/contact", "link_label": "Prendre contact"},
]


class ConseilCreate(BaseModel):
    text: str = Field(..., max_length=200, min_length=5)
    category: str
    link: str = "/ressources"
    link_label: str = "En savoir plus"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    active: bool = True
    priority: bool = False
    tts_enabled: bool = True


class ConseilUpdate(BaseModel):
    text: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = None
    link: Optional[str] = None
    link_label: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    active: Optional[bool] = None
    priority: Optional[bool] = None
    tts_enabled: Optional[bool] = None


def serialize_conseil(doc):
    return {
        "id": str(doc["_id"]),
        "text": doc.get("text", ""),
        "category": doc.get("category", ""),
        "link": doc.get("link", "/ressources"),
        "link_label": doc.get("link_label", "En savoir plus"),
        "start_date": doc.get("start_date"),
        "end_date": doc.get("end_date"),
        "active": doc.get("active", True),
        "priority": doc.get("priority", False),
        "tts_enabled": doc.get("tts_enabled", True),
        "views": doc.get("views", 0),
        "clicks": doc.get("clicks", 0),
        "conversions": doc.get("conversions", 0),
        "created_at": doc.get("created_at", ""),
    }


async def ensure_seed():
    count = await db.strate_conseils.count_documents({})
    if count == 0:
        now = datetime.now(timezone.utc).isoformat()
        docs = []
        for c in DEFAULT_CONSEILS:
            docs.append({
                **c,
                "active": True,
                "priority": False,
                "tts_enabled": True,
                "start_date": None,
                "end_date": None,
                "views": 0,
                "clicks": 0,
                "conversions": 0,
                "created_at": now,
            })
        await db.strate_conseils.insert_many(docs)


async def _inc_daily(conseil_id: str, category: str, field: str):
    """Increment a field in the daily stats collection (upsert)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    await db.strate_daily_stats.update_one(
        {"conseil_id": conseil_id, "date": today},
        {
            "$inc": {field: 1},
            "$setOnInsert": {"conseil_id": conseil_id, "category": category, "date": today},
        },
        upsert=True,
    )


# ── PUBLIC: Get today's conseil ──
@router.get("/today")
async def get_today_conseil():
    await ensure_seed()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Priority conseil for today
    priority = await db.strate_conseils.find_one({
        "active": True, "priority": True,
        "$or": [{"start_date": None}, {"start_date": {"$lte": today}}],
    })
    if priority:
        end = priority.get("end_date")
        if not end or end >= today:
            return {
                "id": str(priority["_id"]),
                "text": priority["text"],
                "category": priority.get("category", ""),
                "link": priority.get("link", "/ressources"),
                "link_label": priority.get("link_label", "En savoir plus"),
            }

    # Active conseils within date range
    active = await db.strate_conseils.find({
        "active": True,
        "$or": [{"start_date": None}, {"start_date": {"$lte": today}}],
    }).to_list(500)

    valid = []
    for c in active:
        end = c.get("end_date")
        if not end or end >= today:
            valid.append(c)

    if not valid:
        first = await db.strate_conseils.find_one()
        if first:
            return {
                "id": str(first["_id"]),
                "text": first["text"],
                "category": first.get("category", ""),
                "link": first.get("link", "/ressources"),
                "link_label": first.get("link_label", "En savoir plus"),
            }
        return {"id": "", "text": DEFAULT_CONSEILS[0]["text"], "category": "droits", "link": "/ressources", "link_label": "Voir les ressources"}

    now = datetime.now(timezone.utc)
    day_index = math.floor(now.timestamp() / 86400) % len(valid)
    conseil = valid[day_index]
    return {
        "id": str(conseil["_id"]),
        "text": conseil["text"],
        "category": conseil.get("category", ""),
        "link": conseil.get("link", "/ressources"),
        "link_label": conseil.get("link_label", "En savoir plus"),
    }


# ── PUBLIC: Track view (deduplicated by frontend) ──
@router.post("/view")
async def track_view(data: dict):
    conseil_id = data.get("conseil_id", "")
    if not conseil_id:
        return {"ok": False}
    try:
        doc = await db.strate_conseils.find_one({"_id": ObjectId(conseil_id)})
        if doc:
            await db.strate_conseils.update_one({"_id": ObjectId(conseil_id)}, {"$inc": {"views": 1}})
            await _inc_daily(conseil_id, doc.get("category", ""), "views")
    except Exception:
        pass
    return {"ok": True}


# ── PUBLIC: Track click ──
@router.post("/click")
async def track_click(data: dict):
    conseil_id = data.get("conseil_id", "")
    if not conseil_id:
        # Fallback: match by text for backwards compat
        text = data.get("text", "")
        if text:
            doc = await db.strate_conseils.find_one({"text": text})
            if doc:
                await db.strate_conseils.update_one({"_id": doc["_id"]}, {"$inc": {"clicks": 1}})
                await _inc_daily(str(doc["_id"]), doc.get("category", ""), "clicks")
        return {"ok": True}
    try:
        doc = await db.strate_conseils.find_one({"_id": ObjectId(conseil_id)})
        if doc:
            await db.strate_conseils.update_one({"_id": ObjectId(conseil_id)}, {"$inc": {"clicks": 1}})
            await _inc_daily(conseil_id, doc.get("category", ""), "clicks")
    except Exception:
        pass
    return {"ok": True}


# ── PUBLIC: Track conversion (future-ready) ──
@router.post("/conversion")
async def track_conversion(data: dict):
    conseil_id = data.get("conseil_id", "")
    action = data.get("action", "unknown")
    if not conseil_id:
        return {"ok": False}
    try:
        doc = await db.strate_conseils.find_one({"_id": ObjectId(conseil_id)})
        if doc:
            await db.strate_conseils.update_one({"_id": ObjectId(conseil_id)}, {"$inc": {"conversions": 1}})
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            await db.strate_daily_stats.update_one(
                {"conseil_id": conseil_id, "date": today},
                {
                    "$inc": {"conversions": 1},
                    "$setOnInsert": {"conseil_id": conseil_id, "category": doc.get("category", ""), "date": today},
                },
                upsert=True,
            )
            # Also log to conversions collection for detailed analysis
            await db.strate_conversions.insert_one({
                "conseil_id": conseil_id,
                "action": action,
                "date": today,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
    except Exception:
        pass
    return {"ok": True}


# ── ADMIN: List all ──
@router.get("/admin/list")
async def list_conseils(admin: dict = Depends(get_current_admin)):
    await ensure_seed()
    docs = await db.strate_conseils.find().sort("created_at", -1).to_list(500)
    return [serialize_conseil(d) for d in docs]


# ── ADMIN: Create ──
@router.post("/admin/create")
async def create_conseil(data: ConseilCreate, admin: dict = Depends(get_current_admin)):
    dup = await db.strate_conseils.find_one({"text": data.text})
    if dup:
        raise HTTPException(400, "Ce conseil existe deja.")
    doc = {
        **data.dict(),
        "views": 0,
        "clicks": 0,
        "conversions": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await db.strate_conseils.insert_one(doc)
    return {"id": str(result.inserted_id), "ok": True}


# ── ADMIN: Update ──
@router.put("/admin/{conseil_id}")
async def update_conseil(conseil_id: str, data: ConseilUpdate, admin: dict = Depends(get_current_admin)):
    update = {k: v for k, v in data.dict().items() if v is not None}
    if not update:
        raise HTTPException(400, "Rien a modifier.")
    result = await db.strate_conseils.update_one(
        {"_id": ObjectId(conseil_id)}, {"$set": update}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Conseil non trouve.")
    return {"ok": True}


# ── ADMIN: Delete ──
@router.delete("/admin/{conseil_id}")
async def delete_conseil(conseil_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.strate_conseils.delete_one({"_id": ObjectId(conseil_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "Conseil non trouve.")
    return {"ok": True}


# ── ADMIN: Set priority today ──
@router.post("/admin/{conseil_id}/highlight")
async def highlight_conseil(conseil_id: str, admin: dict = Depends(get_current_admin)):
    await db.strate_conseils.update_many({}, {"$set": {"priority": False}})
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = await db.strate_conseils.update_one(
        {"_id": ObjectId(conseil_id)},
        {"$set": {"priority": True, "active": True, "start_date": today}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Conseil non trouve.")
    return {"ok": True}


# ── ADMIN: Stats (simple) ──
@router.get("/admin/stats")
async def get_stats(admin: dict = Depends(get_current_admin)):
    total = await db.strate_conseils.count_documents({})
    active = await db.strate_conseils.count_documents({"active": True})
    pipeline = [{"$group": {"_id": None, "total_views": {"$sum": "$views"}, "total_clicks": {"$sum": "$clicks"}, "total_conversions": {"$sum": "$conversions"}}}]
    agg = await db.strate_conseils.aggregate(pipeline).to_list(1)
    s = agg[0] if agg else {"total_views": 0, "total_clicks": 0, "total_conversions": 0}
    tv = s.get("total_views", 0)
    tc = s.get("total_clicks", 0)
    ctr = round((tc / tv) * 100, 1) if tv > 0 else 0
    return {
        "total": total,
        "active": active,
        "total_views": tv,
        "total_clicks": tc,
        "total_conversions": s.get("total_conversions", 0),
        "ctr": ctr,
    }


# ── ADMIN: Analytics (advanced) ──
@router.get("/admin/analytics")
async def get_analytics(period: str = "7d", category: str = "all", admin: dict = Depends(get_current_admin)):
    days = 30 if period == "30d" else 7
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    # Build daily stats query
    daily_query = {"date": {"$gte": start_date}}
    if category != "all":
        daily_query["category"] = category

    # ── Timeseries ──
    daily_docs = await db.strate_daily_stats.find(daily_query, {"_id": 0}).to_list(5000)

    # Aggregate by date
    date_map = {}
    for d in daily_docs:
        dt = d["date"]
        if dt not in date_map:
            date_map[dt] = {"date": dt, "views": 0, "clicks": 0, "conversions": 0}
        date_map[dt]["views"] += d.get("views", 0)
        date_map[dt]["clicks"] += d.get("clicks", 0)
        date_map[dt]["conversions"] += d.get("conversions", 0)

    # Fill missing dates
    timeseries = []
    for i in range(days):
        dt = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        if dt in date_map:
            timeseries.append(date_map[dt])
        else:
            timeseries.append({"date": dt, "views": 0, "clicks": 0, "conversions": 0})

    # ── Top conseils ──
    conseil_query = {}
    if category != "all":
        conseil_query["category"] = category

    top_docs = await db.strate_conseils.find(conseil_query).sort("views", -1).limit(10).to_list(10)
    top_conseils = []
    for d in top_docs:
        v = d.get("views", 0)
        c = d.get("clicks", 0)
        ctr = round((c / v) * 100, 1) if v > 0 else 0
        top_conseils.append({
            "id": str(d["_id"]),
            "text": d.get("text", ""),
            "category": d.get("category", ""),
            "views": v,
            "clicks": c,
            "conversions": d.get("conversions", 0),
            "ctr": ctr,
        })

    # ── Totals for period ──
    period_views = sum(t["views"] for t in timeseries)
    period_clicks = sum(t["clicks"] for t in timeseries)
    period_conversions = sum(t["conversions"] for t in timeseries)
    period_ctr = round((period_clicks / period_views) * 100, 1) if period_views > 0 else 0

    # ── Category breakdown ──
    cat_pipeline = [
        {"$match": daily_query},
        {"$group": {
            "_id": "$category",
            "views": {"$sum": "$views"},
            "clicks": {"$sum": "$clicks"},
        }},
        {"$sort": {"views": -1}},
    ]
    cat_agg = await db.strate_daily_stats.aggregate(cat_pipeline).to_list(20)
    categories_breakdown = []
    for c in cat_agg:
        cv = c.get("views", 0)
        cc = c.get("clicks", 0)
        categories_breakdown.append({
            "category": c["_id"] or "inconnu",
            "views": cv,
            "clicks": cc,
            "ctr": round((cc / cv) * 100, 1) if cv > 0 else 0,
        })

    return {
        "topConseils": top_conseils,
        "totals": {
            "views": period_views,
            "clicks": period_clicks,
            "conversions": period_conversions,
            "ctr": period_ctr,
        },
        "timeseries": timeseries,
        "categories": categories_breakdown,
    }
