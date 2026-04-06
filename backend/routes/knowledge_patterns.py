"""
KNOWLEDGE PATTERNS — Base d'amelioration interne anonymisee
============================================================
Architecture RGPD-compliant pour l'enrichissement progressif du service.

# =========================================================================
# PROPRIETE INTELLECTUELLE — ACTIF STRATEGIQUE SENSIBLE
# Strategie & Expertise Sante — Tous droits reserves.
# Ce fichier contient un moteur de selection intelligent proprietaire
# (scoring contextuel, matching metier, injection de patterns, garde-fous).
# Toute reproduction, extraction, reutilisation ou transmission sans
# autorisation ecrite est interdite.
#
# ZONE GELEE — MOTEUR IA V1 VALIDE
# Date de gel : 05/04/2026
# Protocole : Aucune modification de la logique de scoring, des limites
#   ou des garde-fous sans ordre explicite du responsable.
#   Toute evolution future doit suivre le protocole IA_BASELINE_V1.md.
# =========================================================================

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


@router.post("/seed")
async def seed_patterns_endpoint(admin=Depends(get_current_admin)):
    """Injecte les patterns seed si la base est vide (admin only)."""
    from constants.seed_patterns import seed_knowledge_patterns
    result = await seed_knowledge_patterns(db)
    return result


@router.post("/seed-mdph")
async def seed_mdph_patterns_endpoint(admin=Depends(get_current_admin)):
    """Injecte le Pack MDPH Premium v1 si pas encore en base (admin only)."""
    from constants.seed_patterns import seed_mdph_patterns
    result = await seed_mdph_patterns(db)
    return result


@router.get("/case-outcomes/stats")
async def case_outcome_stats_endpoint(admin=Depends(get_current_admin)):
    """Statistiques agregees des case outcomes — admin only, V2 preparation."""
    from utils.case_outcome_memory import get_case_outcome_stats
    return await get_case_outcome_stats(db)


@router.get("/v2-readiness")
async def v2_readiness_endpoint(admin=Depends(get_current_admin)):
    """
    V2 Readiness Status — Feu tricolore pour l'admin.
    Calcule un score de 0 a 100 et determine le statut (rouge/orange/vert).
    Regle absolue : vert uniquement si >= 500 cas exploitables.
    """
    MINIMUM_GREEN = 500
    MINIMUM_ORANGE = 200

    total = await db.case_outcomes.count_documents({})
    usable = await db.case_outcomes.count_documents({"utilisable_pour_apprentissage": True})

    # --- Volume score (50 pts max) ---
    volume_score = min(usable / MINIMUM_GREEN, 1.0) * 50

    # --- Diversity score (20 pts max) ---
    # Unique families
    families_pipeline = [
        {"$match": {"famille_situation": {"$ne": ""}}},
        {"$group": {"_id": "$famille_situation"}},
    ]
    families = await db.case_outcomes.aggregate(families_pipeline).to_list(50)
    unique_families = len(families)
    # 8 families defined in case_outcome_memory => 8 = max diversity
    diversity_score = min(unique_families / 8, 1.0) * 10

    # Unique categories
    categories_pipeline = [
        {"$match": {"categorie_dossier": {"$ne": ""}}},
        {"$group": {"_id": "$categorie_dossier"}},
    ]
    categories = await db.case_outcomes.aggregate(categories_pipeline).to_list(50)
    unique_categories = len(categories)
    diversity_score += min(unique_categories / 6, 1.0) * 10

    # --- Completeness score (15 pts max) ---
    # Cases with at least one blocage documented
    with_blocage = await db.case_outcomes.count_documents({
        "blocage_principal": {"$ne": ""}
    })
    completeness_blocage = (with_blocage / total * 15) if total > 0 else 0

    # --- Quality score (15 pts max) ---
    # Cases with quality_level not empty
    with_quality = await db.case_outcomes.count_documents({
        "quality_level": {"$ne": ""}
    })
    quality_score = (with_quality / total * 8) if total > 0 else 0

    # Cases with leviers
    with_leviers = await db.case_outcomes.count_documents({
        "leviers_probables": {"$ne": []}
    })
    quality_score += (with_leviers / total * 7) if total > 0 else 0

    # --- Final score ---
    raw_score = volume_score + diversity_score + completeness_blocage + quality_score
    score = min(round(raw_score), 100)

    # --- Traffic light ---
    if usable >= MINIMUM_GREEN and score >= 70:
        status = "vert"
    elif usable >= MINIMUM_ORANGE and score >= 40:
        status = "orange"
    else:
        status = "rouge"

    # --- Complexity distribution ---
    complexity_pipeline = [
        {"$group": {"_id": "$niveau_complexite", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    complexities = await db.case_outcomes.aggregate(complexity_pipeline).to_list(10)

    # --- Source distribution ---
    source_pipeline = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    sources = await db.case_outcomes.aggregate(source_pipeline).to_list(10)

    return {
        "score": score,
        "status": status,
        "total_cases": total,
        "usable_cases": usable,
        "minimum_green": MINIMUM_GREEN,
        "minimum_orange": MINIMUM_ORANGE,
        "breakdown": {
            "volume": round(volume_score, 1),
            "diversity": round(diversity_score, 1),
            "completeness": round(completeness_blocage, 1),
            "quality": round(quality_score, 1),
        },
        "details": {
            "unique_families": unique_families,
            "unique_categories": unique_categories,
            "with_blocage": with_blocage,
            "with_quality": with_quality,
            "with_leviers": with_leviers,
        },
        "complexity_distribution": [
            {"niveau": c["_id"] or "inconnu", "count": c["count"]} for c in complexities
        ],
        "source_distribution": [
            {"source": s["_id"] or "inconnu", "count": s["count"]} for s in sources
        ],
    }


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
# HELPER — MOTEUR DE SELECTION INTELLIGENT + INJECTION MAITRISEE
# =============================================================================
# Regles absolues (Missions 3-4-7-8) :
# - Max 5 patterns, 4 vigilances, 4 leviers
# - Priorite : exact match > categorie coherente > rien
# - Anti-hallucination : formulations conditionnelles uniquement
# - Si contexte trop flou : ne rien injecter ou 1-2 vigilances generales
# - Uniquement usage_autorise=True
# =============================================================================

async def get_knowledge_patterns_context(
    categorie=None, metier=None, type_sinistre=None,
    type_garantie=None, blocage=None, situation_text=None
):
    """
    Moteur de selection intelligent des patterns valides.
    Retourne un contexte court, cible et non bavard pour injection SYSTEM.
    Retourne "" si rien de pertinent ou base vide.
    """
    # Verifier qu'il y a des patterns valides
    total_validated = await db.knowledge_patterns.count_documents({"usage_autorise": True})
    if total_validated == 0:
        return ""

    # Normaliser les entrees
    def norm(v):
        import unicodedata
        return unicodedata.normalize("NFD", (v or "").lower().strip()).encode("ascii", "ignore").decode("ascii")

    cat_n = norm(categorie)
    met_n = norm(metier)
    sin_n = norm(type_sinistre)
    gar_n = norm(type_garantie)
    blo_n = norm(blocage)

    # Evaluer la richesse du contexte (Mission 8)
    context_signals = sum(1 for v in [cat_n, met_n, sin_n, gar_n, blo_n] if v)
    if context_signals == 0:
        return ""

    # Recuperer tous les patterns valides
    all_patterns = await db.knowledge_patterns.find(
        {"usage_autorise": True},
        {"_id": 0, "description": 1, "pattern_type": 1, "categorie_dossier": 1,
         "metier": 1, "type_sinistre": 1, "type_garantie": 1,
         "blocage_principal": 1, "niveau_confiance": 1, "tags": 1}
    ).to_list(100)

    if not all_patterns:
        return ""

    # Scoring par priorite (Mission 4)
    scored = []
    for p in all_patterns:
        score = 0
        p_cat = norm(p.get("categorie_dossier", ""))
        p_met = norm(p.get("metier", ""))
        p_sin = norm(p.get("type_sinistre", ""))
        p_gar = norm(p.get("type_garantie", ""))
        p_blo = norm(p.get("blocage_principal", ""))
        p_tags = [norm(t) for t in p.get("tags", [])]

        # Priorite haute : exact match (+10 chacun)
        if met_n and p_met and met_n == p_met:
            score += 10
        if sin_n and p_sin and sin_n == p_sin:
            score += 10
        if gar_n and p_gar and gar_n == p_gar:
            score += 10
        if blo_n and p_blo and blo_n == p_blo:
            score += 10

        # Priorite moyenne : categorie coherente (+5)
        if cat_n and p_cat and cat_n == p_cat:
            score += 5

        # Priorite moyenne : match partiel dans tags (+3)
        for signal in [cat_n, met_n, sin_n, gar_n, blo_n]:
            if signal and signal in p_tags:
                score += 3

        # Priorite moyenne : metier voisin / contenu dans (+2)
        if met_n and p_met and (met_n in p_met or p_met in met_n):
            score += 2

        # Bonus confiance elevee
        if p.get("niveau_confiance") == "eleve":
            score += 2

        # Ignorer si aucun match (Mission 8 : pas d'injection floue)
        if score > 0:
            scored.append((score, p))

    if not scored:
        # Contexte trop faible : retourner rien (Mission 8)
        return ""

    # Trier par score decroissant
    scored.sort(key=lambda x: -x[0])

    # Categoriser par type (Mission 3 : limites strictes)
    patterns_out = []   # max 5
    vigilances_out = [] # max 4
    leviers_out = []    # max 4

    for _score, p in scored:
        ptype = p.get("pattern_type", "")
        desc = p.get("description", "")

        if ptype in ("vigilance", "erreur_frequente", "signal_faible"):
            if len(vigilances_out) < 4:
                vigilances_out.append(desc)
        elif ptype in ("levier", "argument_utile"):
            if len(leviers_out) < 4:
                leviers_out.append(desc)
        else:
            if len(patterns_out) < 5:
                patterns_out.append(desc)

        # Limiter le total a 12 elements
        if len(patterns_out) + len(vigilances_out) + len(leviers_out) >= 12:
            break

    # Si trop peu de resultats pertinents, retourner rien (Mission 8)
    total_selected = len(patterns_out) + len(vigilances_out) + len(leviers_out)
    if total_selected == 0:
        return ""

    # Construire le contexte d'injection (Mission 2 + Mission 7)
    lines = []
    lines.append("\n\n=== ENSEIGNEMENTS METIER VALIDES (couche d'enrichissement — ne remplace jamais les elements du dossier) ===")
    lines.append("REGLE ABSOLUE : Ces enseignements sont des tendances observees, PAS des faits du dossier. Utilise des formulations conditionnelles : 'ce type de situation expose souvent a...', 'dans ce type de configuration, la difficulte porte frequemment sur...', 'cela peut traduire un blocage classique de...'. JAMAIS de certitude non confirmee par les pieces du dossier.")

    if patterns_out:
        lines.append("\nPatterns metier pertinents :")
        for desc in patterns_out:
            lines.append(f"  - {desc}")

    if vigilances_out:
        lines.append("\nVigilances recurrentes :")
        for desc in vigilances_out:
            lines.append(f"  - {desc}")

    if leviers_out:
        lines.append("\nLeviers recurrents valides :")
        for desc in leviers_out:
            lines.append(f"  - {desc}")

    return "\n".join(lines)
