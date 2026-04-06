"""
STRATEGIC FEEDBACK — Retour d'experience client
=================================================
Micro systeme de feedback strategique, declenche uniquement
apres une analyse StrategiIA ou Dossier Express.
Objectif : capter les vrais freins, besoins et incomprehensions.
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import uuid

from config import db, logger
from utils.auth import get_current_admin

router = APIRouter(prefix="/feedback", tags=["Strategic Feedback"])

# Categorisation automatique par mots-cles
CATEGORY_KEYWORDS = {
    "juridique": ["avocat", "tribunal", "juge", "recours", "procedure", "juridique", "droit", "loi", "jugement", "justice", "plainte", "contentieux"],
    "medical": ["medecin", "certificat", "examen", "pathologie", "diagnostic", "soin", "hopital", "docteur", "irm", "scanner", "expertise medicale"],
    "administratif": ["dossier", "formulaire", "document", "delai", "courrier", "cerfa", "cpam", "administration", "caisse", "declaration"],
    "assurantiel": ["assurance", "contrat", "garantie", "indemnisation", "generali", "groupama", "cnp", "emprunteur", "pret", "sinistre"],
    "mdph": ["mdph", "aah", "pch", "rqth", "handicap", "invalidite", "carte", "cmi", "incapacite", "autonomie"],
    "accompagnement": ["aide", "accompagnement", "soutien", "ecoute", "humain", "rassurer", "seul", "perdu", "comprendre", "expliquer", "guider"],
    "incomprehension_offre": ["comprend", "clair", "confus", "savoir", "quoi", "comment", "pourquoi", "difference", "service", "tarif", "prix", "offre"],
}


def _normalize(text):
    import unicodedata
    return unicodedata.normalize("NFD", (text or "").lower()).encode("ascii", "ignore").decode("ascii")


def auto_categorize(frein, besoin, commentaire):
    """Detecte automatiquement les categories a partir des reponses."""
    full_text = _normalize(f"{frein} {besoin} {commentaire}")
    detected = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in full_text:
                detected.append(cat)
                break
    return detected or ["non_categorise"]


# =============================================================================
# SOUMISSION (public — pas d'auth requise)
# =============================================================================

@router.post("")
async def submit_feedback(data: dict):
    """Soumet un retour d'experience client. Aucune donnee personnelle requise."""
    frein = (data.get("frein") or "").strip()[:500]
    besoin = (data.get("besoin") or "").strip()[:500]
    clarte = data.get("clarte", "")
    commentaire = (data.get("commentaire") or "").strip()[:300]
    source = data.get("source", "")
    type_dossier = data.get("type_dossier", "")

    if not clarte and not frein and not besoin:
        raise HTTPException(400, "Au moins une reponse requise")

    categories = auto_categorize(frein, besoin, commentaire)

    doc = {
        "id": str(uuid.uuid4()),
        "frein": frein,
        "besoin": besoin,
        "clarte": clarte,
        "commentaire": commentaire,
        "categories": categories,
        "source": source,
        "type_dossier": type_dossier,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.strategic_feedback.insert_one(doc)
    logger.info(f"[FEEDBACK] New feedback from {source}: categories={categories}")
    return {"success": True}


# =============================================================================
# LECTURE ADMIN
# =============================================================================

@router.get("")
async def list_feedback(admin=Depends(get_current_admin), category: str = "", limit: int = 100):
    """Liste les retours d'experience (admin only)."""
    query = {}
    if category:
        query["categories"] = category

    docs = await db.strategic_feedback.find(
        query, {"_id": 0}
    ).sort("created_at", -1).to_list(limit)

    return {"feedbacks": docs, "count": len(docs)}


@router.get("/stats")
async def feedback_stats(admin=Depends(get_current_admin)):
    """Statistiques agregees des feedbacks."""
    total = await db.strategic_feedback.count_documents({})

    # Clarte distribution
    clarte_pipeline = [
        {"$match": {"clarte": {"$ne": ""}}},
        {"$group": {"_id": "$clarte", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    clarte_dist = await db.strategic_feedback.aggregate(clarte_pipeline).to_list(10)

    # Categories distribution
    cat_pipeline = [
        {"$unwind": "$categories"},
        {"$group": {"_id": "$categories", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    cat_dist = await db.strategic_feedback.aggregate(cat_pipeline).to_list(20)

    # Source distribution
    source_pipeline = [
        {"$match": {"source": {"$ne": ""}}},
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    source_dist = await db.strategic_feedback.aggregate(source_pipeline).to_list(10)

    # Freins les plus mentionnes (non vides)
    frein_count = await db.strategic_feedback.count_documents({"frein": {"$ne": ""}})
    besoin_count = await db.strategic_feedback.count_documents({"besoin": {"$ne": ""}})

    return {
        "total": total,
        "with_frein": frein_count,
        "with_besoin": besoin_count,
        "clarte_distribution": [{"label": c["_id"], "count": c["count"]} for c in clarte_dist],
        "category_distribution": [{"category": c["_id"], "count": c["count"]} for c in cat_dist],
        "source_distribution": [{"source": s["_id"], "count": s["count"]} for s in source_dist],
    }
