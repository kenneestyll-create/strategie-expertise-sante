from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
from utils.auth import get_current_admin
from utils.db import db

router = APIRouter(prefix="/api/conseils", tags=["conseils"])

CATEGORIES = ["droits", "expertise", "indemnisation", "emploi", "demarches", "strategie", "actualite"]
LINK_OPTIONS = ["/calculatrice-ipp", "/dossier-express", "/ressources", "/simulateur", "/contact", "/accident-travail-maladie-professionnelle"]

DEFAULT_CONSEILS = [
    {"text": "Vous disposez en general de 2 ans pour declarer une maladie professionnelle apres le diagnostic.", "category": "droits", "link": "/ressources", "link_label": "Voir les ressources"},
    {"text": "Une contestation d'une decision de la CPAM doit etre faite dans un delai de 2 mois.", "category": "droits", "link": "/ressources", "link_label": "En savoir plus"},
    {"text": "Un accident du travail doit etre declare dans les 24 heures par l'employeur.", "category": "droits", "link": "/accident-travail-maladie-professionnelle", "link_label": "Accidents du travail"},
    {"text": "Vous pouvez declarer vous-meme un accident si l'employeur ne le fait pas.", "category": "droits", "link": "/ressources", "link_label": "Voir les demarches"},
    {"text": "Une rechute peut etre reconnue meme plusieurs annees apres consolidation.", "category": "droits", "link": "/simulateur", "link_label": "Analyser votre cas"},
    {"text": "Vous pouvez etre assiste par un medecin lors d'une expertise.", "category": "expertise", "link": "/ressources", "link_label": "Preparer une expertise"},
    {"text": "Preparer ses documents medicaux est essentiel avant toute expertise.", "category": "expertise", "link": "/dossier-express", "link_label": "Dossier Express IA"},
    {"text": "Vous avez le droit de contester une expertise medicale.", "category": "expertise", "link": "/ressources", "link_label": "Vos droits"},
    {"text": "Le medecin expert doit rester independant.", "category": "expertise", "link": "/ressources", "link_label": "En savoir plus"},
    {"text": "Un rapport medical incomplet peut etre conteste.", "category": "expertise", "link": "/simulateur", "link_label": "Analyser votre dossier"},
    {"text": "Une incapacite permanente donne droit a une indemnisation.", "category": "indemnisation", "link": "/calculatrice-ipp", "link_label": "Calculer votre IPP"},
    {"text": "Le taux d'IPP influence directement le montant de l'indemnisation.", "category": "indemnisation", "link": "/calculatrice-ipp", "link_label": "Calculatrice IPP"},
    {"text": "Une faute inexcusable de l'employeur peut majorer votre indemnisation.", "category": "indemnisation", "link": "/simulateur", "link_label": "Analyser avec StrategiIA"},
    {"text": "Certains prejudices ne sont pas automatiquement indemnises.", "category": "indemnisation", "link": "/ressources", "link_label": "Voir les ressources"},
    {"text": "Une perte de carriere peut etre reconnue sous conditions.", "category": "indemnisation", "link": "/ressources", "link_label": "IP et PGPF"},
    {"text": "Une inaptitude peut ouvrir droit a des indemnites specifiques.", "category": "emploi", "link": "/ressources", "link_label": "Vos droits"},
    {"text": "Le reclassement professionnel est une obligation de l'employeur.", "category": "emploi", "link": "/accident-travail-maladie-professionnelle", "link_label": "En savoir plus"},
    {"text": "Une invalidite ne met pas fin automatiquement au contrat de travail.", "category": "emploi", "link": "/ressources", "link_label": "Voir les ressources"},
    {"text": "Vous pouvez cumuler certaines aides selon votre situation.", "category": "emploi", "link": "/ressources", "link_label": "Aides disponibles"},
    {"text": "Une reconversion peut etre financee dans certains cas.", "category": "emploi", "link": "/ressources", "link_label": "En savoir plus"},
    {"text": "Conservez toujours une copie de vos documents medicaux.", "category": "demarches", "link": "/dossier-express", "link_label": "Dossier Express IA"},
    {"text": "Les echanges avec la CPAM doivent etre traces.", "category": "demarches", "link": "/ressources", "link_label": "Voir les guides"},
    {"text": "Un dossier incomplet peut ralentir votre indemnisation.", "category": "demarches", "link": "/dossier-express", "link_label": "Completez votre dossier"},
    {"text": "Il est possible de se faire accompagner dans ses demarches.", "category": "demarches", "link": "/contact", "link_label": "Nous contacter"},
    {"text": "Une demande peut etre reetudiee avec de nouveaux elements.", "category": "demarches", "link": "/simulateur", "link_label": "Analyser votre situation"},
    {"text": "Anticiper une expertise ameliore souvent son resultat.", "category": "strategie", "link": "/dossier-express", "link_label": "Dossier Express IA"},
    {"text": "Une bonne preparation peut influencer une decision.", "category": "strategie", "link": "/simulateur", "link_label": "StrategiIA"},
    {"text": "Chaque situation est unique et merite une analyse personnalisee.", "category": "strategie", "link": "/simulateur", "link_label": "Analyser mon cas"},
    {"text": "Ne pas agir dans les delais peut faire perdre des droits.", "category": "strategie", "link": "/ressources", "link_label": "Delais importants"},
    {"text": "Se faire accompagner permet souvent d'optimiser ses demarches.", "category": "strategie", "link": "/contact", "link_label": "Prendre contact"},
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
                "created_at": now,
            })
        await db.strate_conseils.insert_many(docs)


# ── PUBLIC: Get today's conseil ──
@router.get("/today")
async def get_today_conseil():
    await ensure_seed()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Priority conseil for today
    priority = await db.strate_conseils.find_one({
        "active": True, "priority": True,
        "$or": [{"start_date": None}, {"start_date": {"$lte": today}}],
    }, {"_id": 0})
    if priority:
        end = priority.get("end_date")
        if not end or end >= today:
            await db.strate_conseils.update_one(
                {"text": priority["text"]}, {"$inc": {"views": 1}}
            )
            return priority

    # Active conseils within date range
    active = await db.strate_conseils.find({
        "active": True,
        "$or": [{"start_date": None}, {"start_date": {"$lte": today}}],
    }, {"_id": 0}).to_list(500)

    valid = []
    for c in active:
        end = c.get("end_date")
        if not end or end >= today:
            valid.append(c)

    if not valid:
        return DEFAULT_CONSEILS[0]

    import math
    now = datetime.now(timezone.utc)
    day_index = math.floor(now.timestamp() / 86400) % len(valid)
    conseil = valid[day_index]
    await db.strate_conseils.update_one(
        {"text": conseil["text"]}, {"$inc": {"views": 1}}
    )
    return conseil


# ── PUBLIC: Track click ──
@router.post("/click")
async def track_click(data: dict):
    text = data.get("text", "")
    if text:
        await db.strate_conseils.update_one({"text": text}, {"$inc": {"clicks": 1}})
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


# ── ADMIN: Stats ──
@router.get("/admin/stats")
async def get_stats(admin: dict = Depends(get_current_admin)):
    total = await db.strate_conseils.count_documents({})
    active = await db.strate_conseils.count_documents({"active": True})
    pipeline = [{"$group": {"_id": None, "total_views": {"$sum": "$views"}, "total_clicks": {"$sum": "$clicks"}}}]
    agg = await db.strate_conseils.aggregate(pipeline).to_list(1)
    stats = agg[0] if agg else {"total_views": 0, "total_clicks": 0}
    return {
        "total": total,
        "active": active,
        "total_views": stats.get("total_views", 0),
        "total_clicks": stats.get("total_clicks", 0),
    }
