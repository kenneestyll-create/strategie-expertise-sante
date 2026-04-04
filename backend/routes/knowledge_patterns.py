"""
KNOWLEDGE PATTERNS — Base d'amelioration interne anonymisee
============================================================
Architecture RGPD-compliant pour l'enrichissement progressif du service.

REGLES ABSOLUES (Mission 5) :
- INTERDICTION de stocker du texte brut client
- INTERDICTION de stocker des donnees identifiantes (nom, email, matricule, adresse)
- INTERDICTION de stocker des resumes nominatifs ou des PDF recycles
- INTERDICTION de fine-tuning sauvage ou de base d'entrainement brute
- INTERDICTION de recuperation automatique integrale des dossiers

AUTORISE :
- Patterns anonymises (type blocage, type sinistre, metier, garantie)
- Enseignements abstraits et non reidentifiables
- Signaux metier, schemas de blocage, erreurs frequentes
- Statistiques internes agregees
- Bibliotheque de regles et enrichissements non identifiants
- Amelioration des prompts, regles et matrices

STRUCTURE :
- Chaque pattern est detache du dossier source (pas de reference au dossier, client, date precise)
- Le champ `source_type` indique seulement le type de service (strategiia, dossier_express)
- Le champ `usage_autorise` controle l'exploitation du pattern
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import uuid

from config import db, logger
from utils.auth import get_current_admin

router = APIRouter(prefix="/knowledge-patterns", tags=["knowledge-patterns"])

# =============================================================================
# SCHEMA DE REFERENCE — knowledge_patterns
# =============================================================================
# {
#   "id": str (uuid),
#   "categorie_dossier": str (ex: "maladie_professionnelle", "accident_travail", "invalidite", "litige_assurantiel", "contestation_ipp"),
#   "metier": str (ex: "transport_conduite", "btp", "sante", "administratif", "securite"),
#   "type_sinistre": str (ex: "mp_tableau_57", "at_lombaire", "rechute", "aggravation"),
#   "type_garantie": str | null (ex: "ITT", "IPT", "IPP", "PTIA", "PE"),
#   "blocage_principal": str (ex: "probatoire", "medical", "administratif", "qualification", "traduction_fonctionnelle"),
#   "pattern_type": str (ex: "blocage", "levier", "erreur_frequente", "piece_manquante", "argument_utile", "signal_faible", "vigilance"),
#   "description": str (contenu abstrait, non identifiant, max 500 chars),
#   "niveau_confiance": str ("eleve", "moyen", "faible"),
#   "usage_autorise": bool (True = exploitable, False = en attente de validation),
#   "source_type": str ("strategiia", "dossier_express", "manuel"),
#   "created_at": str (ISO),
#   "validated_by": str | null (admin qui a valide),
#   "validated_at": str | null,
#   "tags": list[str] (ex: ["ratp", "ccas", "cram", "sous_evaluation"]),
# }


# =============================================================================
# ENDPOINTS ADMIN — CRUD knowledge_patterns
# =============================================================================

@router.get("")
async def list_patterns(admin=Depends(get_current_admin)):
    """Liste tous les patterns (admin only)."""
    patterns = await db.knowledge_patterns.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return {"patterns": patterns, "count": len(patterns)}


@router.post("")
async def create_pattern(data: dict, admin=Depends(get_current_admin)):
    """Cree un pattern anonymise manuellement (admin only)."""
    required = ["categorie_dossier", "pattern_type", "description"]
    for field in required:
        if not data.get(field):
            raise HTTPException(400, f"Champ obligatoire manquant : {field}")

    if len(data.get("description", "")) > 500:
        raise HTTPException(400, "La description ne doit pas depasser 500 caracteres (enseignement abstrait uniquement).")

    pattern = {
        "id": str(uuid.uuid4()),
        "categorie_dossier": data.get("categorie_dossier", ""),
        "metier": data.get("metier", ""),
        "type_sinistre": data.get("type_sinistre", ""),
        "type_garantie": data.get("type_garantie"),
        "blocage_principal": data.get("blocage_principal", ""),
        "pattern_type": data["pattern_type"],
        "description": data["description"],
        "niveau_confiance": data.get("niveau_confiance", "moyen"),
        "usage_autorise": False,
        "source_type": data.get("source_type", "manuel"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "validated_by": None,
        "validated_at": None,
        "tags": data.get("tags", []),
    }
    await db.knowledge_patterns.insert_one(pattern)
    logger.info(f"[KNOWLEDGE_PATTERNS] Pattern created: {pattern['id']} type={pattern['pattern_type']} cat={pattern['categorie_dossier']}")
    del pattern["_id"]
    return pattern


@router.put("/{pattern_id}/validate")
async def validate_pattern(pattern_id: str, admin=Depends(get_current_admin)):
    """Valide un pattern pour exploitation (admin only)."""
    result = await db.knowledge_patterns.update_one(
        {"id": pattern_id},
        {"$set": {"usage_autorise": True, "validated_by": admin.get("email", "admin"), "validated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(404, "Pattern introuvable")
    logger.info(f"[KNOWLEDGE_PATTERNS] Pattern validated: {pattern_id}")
    return {"status": "validated", "id": pattern_id}


@router.delete("/{pattern_id}")
async def delete_pattern(pattern_id: str, admin=Depends(get_current_admin)):
    """Supprime un pattern (admin only)."""
    result = await db.knowledge_patterns.delete_one({"id": pattern_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Pattern introuvable")
    logger.info(f"[KNOWLEDGE_PATTERNS] Pattern deleted: {pattern_id}")
    return {"status": "deleted", "id": pattern_id}


@router.get("/stats")
async def pattern_stats(admin=Depends(get_current_admin)):
    """Statistiques agregees des patterns (admin only)."""
    total = await db.knowledge_patterns.count_documents({})
    validated = await db.knowledge_patterns.count_documents({"usage_autorise": True})
    pending = total - validated

    pipeline = [
        {"$group": {"_id": "$categorie_dossier", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    by_category = await db.knowledge_patterns.aggregate(pipeline).to_list(50)

    pipeline_type = [
        {"$group": {"_id": "$pattern_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    by_type = await db.knowledge_patterns.aggregate(pipeline_type).to_list(50)

    return {
        "total": total,
        "validated": validated,
        "pending": pending,
        "by_category": {item["_id"]: item["count"] for item in by_category if item["_id"]},
        "by_type": {item["_id"]: item["count"] for item in by_type if item["_id"]},
    }


# =============================================================================
# HELPER — get_validated_patterns_context()
# =============================================================================

async def get_validated_patterns_context(categorie=None, metier=None, limit=20):
    """
    Retourne les patterns valides pour injection dans le prompt LLM.
    Uniquement les patterns avec usage_autorise=True.
    """
    query = {"usage_autorise": True}
    if categorie:
        query["categorie_dossier"] = categorie
    if metier:
        query["metier"] = metier

    patterns = await db.knowledge_patterns.find(query, {"_id": 0, "description": 1, "pattern_type": 1, "blocage_principal": 1, "tags": 1}).sort("niveau_confiance", 1).to_list(limit)

    if not patterns:
        return ""

    lines = ["\n=== ENSEIGNEMENTS INTERNES ANONYMISES ==="]
    for p in patterns:
        ptype = p.get("pattern_type", "")
        desc = p.get("description", "")
        blocage = p.get("blocage_principal", "")
        prefix = {"blocage": "BLOCAGE", "levier": "LEVIER", "erreur_frequente": "ERREUR FREQUENTE", "piece_manquante": "PIECE MANQUANTE", "argument_utile": "ARGUMENT", "signal_faible": "SIGNAL", "vigilance": "VIGILANCE"}.get(ptype, ptype.upper())
        extra = f" (blocage: {blocage})" if blocage else ""
        lines.append(f"  [{prefix}{extra}] {desc}")

    return "\n".join(lines)
