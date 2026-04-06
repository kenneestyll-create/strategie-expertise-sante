"""
PREDICTIVE V2 ADMIN ROUTES — Gestion admin de la V2 dormante
==============================================================
Routes admin-only pour : feature flag, activation securisee,
sandbox, comparateur V1/V2, configuration, audit log.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone

from config import db, logger
from utils.auth import get_current_admin
from utils.predictive_v2 import (
    is_v2_enabled, get_v2_config, set_v2_config,
    run_predictive_analysis, generate_v2_context_block, compare_v1_v2,
)
from utils.predictive_logging import log_v2_event, get_v2_audit_log
from utils.case_outcome_memory import extract_case_features

router = APIRouter(prefix="/predictive-v2", tags=["Predictive V2 Admin"])


# =============================================================================
# STATUS — Etat actuel complet de la V2
# =============================================================================

@router.get("/status")
async def v2_status(admin=Depends(get_current_admin)):
    """Retourne l'etat complet de la V2 : flag, config, readiness, verrous."""
    enabled = await is_v2_enabled(db)
    config = await get_v2_config(db)

    # Readiness check
    readiness = await _compute_readiness()

    # Activation locks
    min_cases = config.get("v2_min_cases", 500)
    min_score = config.get("v2_min_readiness_score", 70)
    locks = _compute_locks(readiness, min_cases, min_score)

    return {
        "enabled": enabled,
        "config": config,
        "readiness": readiness,
        "locks": locks,
        "can_activate": all(lock["passed"] for lock in locks),
    }


@router.get("/audit-log")
async def v2_audit_log(admin=Depends(get_current_admin)):
    """Historique complet des actions V2."""
    logs = await get_v2_audit_log(db, limit=100)
    return {"logs": logs, "count": len(logs)}


# =============================================================================
# ACTIVATION / DESACTIVATION — Securisee
# =============================================================================

@router.post("/activate")
async def v2_activate(data: dict, admin=Depends(get_current_admin)):
    """
    Active la V2 predictive.
    Requiert : confirmation_text == "ACTIVER V2" + readiness suffisant.
    """
    confirmation = data.get("confirmation_text", "")
    if confirmation != "ACTIVER V2":
        raise HTTPException(400, "Confirmation invalide. Saisissez exactement : ACTIVER V2")

    # Verifier readiness
    readiness = await _compute_readiness()
    config = await get_v2_config(db)
    min_cases = config.get("v2_min_cases", 500)
    min_score = config.get("v2_min_readiness_score", 70)
    locks = _compute_locks(readiness, min_cases, min_score)

    failed_locks = [lock for lock in locks if not lock["passed"]]
    if failed_locks:
        reasons = [lock["reason"] for lock in failed_locks]
        await log_v2_event(db, "activation_refused", admin.get("email", "admin"), {
            "reasons": reasons, "readiness_score": readiness["score"], "usable_cases": readiness["usable_cases"],
        })
        raise HTTPException(403, f"Activation impossible. Verrous non satisfaits : {', '.join(reasons)}")

    # Activer
    await set_v2_config(db, "predictive_v2_enabled", True)
    await set_v2_config(db, "v2_activated_at", datetime.now(timezone.utc).isoformat())
    await set_v2_config(db, "v2_activated_by", admin.get("email", "admin"))

    await log_v2_event(db, "activation", admin.get("email", "admin"), {
        "readiness_score": readiness["score"],
        "usable_cases": readiness["usable_cases"],
        "status": readiness["status"],
    })

    return {
        "success": True,
        "message": "V2 predictive activee. Les futures analyses integreront les signaux V2.",
        "activated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/deactivate")
async def v2_deactivate(admin=Depends(get_current_admin)):
    """Desactive immediatement la V2 (kill switch). Retour V1 instantane."""
    await set_v2_config(db, "predictive_v2_enabled", False)

    await log_v2_event(db, "deactivation", admin.get("email", "admin"), {
        "reason": "kill_switch_admin",
    })

    return {
        "success": True,
        "message": "V2 desactivee immediatement. Retour V1 pur. Aucune analyse future n'utilisera la V2.",
    }


# =============================================================================
# CONFIGURATION — Parametres V2
# =============================================================================

@router.get("/config")
async def v2_get_config(admin=Depends(get_current_admin)):
    """Recupere la configuration V2 complete."""
    return await get_v2_config(db)


@router.put("/config")
async def v2_update_config(data: dict, admin=Depends(get_current_admin)):
    """Met a jour un parametre de configuration V2."""
    allowed_keys = {
        "v2_min_readiness_score", "v2_min_cases",
        "v2_max_alerts_per_analysis", "v2_prudence_level",
    }
    key = data.get("key", "")
    value = data.get("value")
    if key not in allowed_keys:
        raise HTTPException(400, f"Parametre non modifiable : {key}")

    old_config = await get_v2_config(db)
    old_value = old_config.get(key)

    await set_v2_config(db, key, value)

    await log_v2_event(db, "config_change", admin.get("email", "admin"), {
        "key": key, "old_value": old_value, "new_value": value,
    })

    return {"success": True, "key": key, "value": value}


# =============================================================================
# SANDBOX — Test interne sans impact client
# =============================================================================

@router.post("/sandbox/analyze")
async def v2_sandbox_analyze(data: dict, admin=Depends(get_current_admin)):
    """
    Teste l'analyse V2 sur un texte libre (sandbox admin).
    Ne stocke rien, ne modifie rien, n'impacte aucun client.
    """
    situation = data.get("situation", "")
    type_dossier = data.get("type_dossier", "")
    regime = data.get("regime", "")

    if not situation.strip():
        raise HTTPException(400, "Situation requise pour le test sandbox")

    features = extract_case_features(situation, type_dossier=type_dossier, regime=regime, situation=situation)
    v2_result = run_predictive_analysis(situation, type_dossier, regime, case_features=features)
    v2_context = generate_v2_context_block(v2_result)

    await log_v2_event(db, "sandbox_test", admin.get("email", "admin"), {
        "type_dossier": type_dossier, "alert_count": v2_result["alert_count"],
        "robustness_score": v2_result["robustness_score"],
    })

    return {
        "v2_result": v2_result,
        "v2_context_block": v2_context,
        "features_extracted": features,
    }


@router.post("/sandbox/compare")
async def v2_sandbox_compare(data: dict, admin=Depends(get_current_admin)):
    """
    Compare une sortie V1 existante avec ce que la V2 aurait ajoute.
    Outil admin interne — aucun impact client.
    """
    analysis_id = data.get("analysis_id", "")
    if not analysis_id:
        raise HTTPException(400, "analysis_id requis")

    # Chercher dans strategiia_analyses ou dossier_express
    analysis = await db.strategiia_analyses.find_one({"id": analysis_id}, {"_id": 0})
    source = "strategiia"
    if not analysis:
        analysis = await db.dossier_express.find_one({"id": analysis_id}, {"_id": 0})
        source = "dossier_express"
    if not analysis:
        raise HTTPException(404, "Analyse introuvable")

    situation = analysis.get("situation", "")
    v1_text = analysis.get("analysis", "")
    type_dossier = analysis.get("type_dossier", "")
    regime = analysis.get("regime", "")

    if not v1_text:
        raise HTTPException(400, "Cette analyse n'a pas de texte V1 exploitable")

    features = extract_case_features(v1_text, type_dossier=type_dossier, regime=regime, situation=situation)
    v2_result = run_predictive_analysis(situation or v1_text, type_dossier, regime, case_features=features)
    comparison = compare_v1_v2(v1_text, v2_result)

    await log_v2_event(db, "sandbox_compare", admin.get("email", "admin"), {
        "analysis_id": analysis_id, "source": source,
        "v2_added_value": comparison["v2_added_value"],
    })

    return {
        "source": source,
        "analysis_id": analysis_id,
        "v2_result": v2_result,
        "comparison": comparison,
        "v1_excerpt": v1_text[:500] + "..." if len(v1_text) > 500 else v1_text,
    }


# =============================================================================
# HELPERS INTERNES
# =============================================================================

async def _compute_readiness():
    """Calcule le readiness V2 complet (reutilise la logique existante)."""
    MINIMUM_GREEN = 500
    MINIMUM_ORANGE = 200

    total = await db.case_outcomes.count_documents({})
    usable = await db.case_outcomes.count_documents({"utilisable_pour_apprentissage": True})

    # Volume (50 pts)
    volume_score = min(usable / MINIMUM_GREEN, 1.0) * 50

    # Diversite (20 pts)
    families = await db.case_outcomes.aggregate([
        {"$match": {"famille_situation": {"$ne": ""}}},
        {"$group": {"_id": "$famille_situation"}},
    ]).to_list(50)
    unique_families = len(families)
    diversity_score = min(unique_families / 8, 1.0) * 10

    categories = await db.case_outcomes.aggregate([
        {"$match": {"categorie_dossier": {"$ne": ""}}},
        {"$group": {"_id": "$categorie_dossier"}},
    ]).to_list(50)
    unique_categories = len(categories)
    diversity_score += min(unique_categories / 6, 1.0) * 10

    # Completude (15 pts)
    with_blocage = await db.case_outcomes.count_documents({"blocage_principal": {"$ne": ""}})
    completeness = (with_blocage / total * 15) if total > 0 else 0

    # Qualite (15 pts)
    with_quality = await db.case_outcomes.count_documents({"quality_level": {"$ne": ""}})
    quality = (with_quality / total * 8) if total > 0 else 0
    with_leviers = await db.case_outcomes.count_documents({"leviers_probables": {"$ne": []}})
    quality += (with_leviers / total * 7) if total > 0 else 0

    raw_score = volume_score + diversity_score + completeness + quality
    score = min(round(raw_score), 100)

    if usable >= MINIMUM_GREEN and score >= 70:
        status = "vert"
    elif usable >= MINIMUM_ORANGE and score >= 40:
        status = "orange"
    else:
        status = "rouge"

    return {
        "score": score,
        "status": status,
        "total_cases": total,
        "usable_cases": usable,
        "unique_families": unique_families,
        "unique_categories": unique_categories,
        "with_blocage": with_blocage,
        "with_quality": with_quality,
        "with_leviers": with_leviers,
        "breakdown": {
            "volume": round(volume_score, 1),
            "diversity": round(diversity_score, 1),
            "completeness": round(completeness, 1),
            "quality": round(quality, 1),
        },
    }


def _compute_locks(readiness, min_cases, min_score):
    """Evalue les verrous d'activation."""
    return [
        {
            "id": "min_cases",
            "label": f"Minimum {min_cases} cas exploitables",
            "passed": readiness["usable_cases"] >= min_cases,
            "current": readiness["usable_cases"],
            "required": min_cases,
            "reason": f"Seulement {readiness['usable_cases']}/{min_cases} cas exploitables",
        },
        {
            "id": "min_score",
            "label": f"Score readiness >= {min_score}",
            "passed": readiness["score"] >= min_score,
            "current": readiness["score"],
            "required": min_score,
            "reason": f"Score {readiness['score']}/{min_score} insuffisant",
        },
        {
            "id": "diversity",
            "label": "Diversite minimale (>= 3 familles)",
            "passed": readiness["unique_families"] >= 3,
            "current": readiness["unique_families"],
            "required": 3,
            "reason": f"Seulement {readiness['unique_families']} familles (minimum 3)",
        },
        {
            "id": "completeness",
            "label": "Completude minimale (>= 50% avec blocage)",
            "passed": (readiness["with_blocage"] / readiness["total_cases"] >= 0.5) if readiness["total_cases"] > 0 else False,
            "current": round(readiness["with_blocage"] / readiness["total_cases"] * 100) if readiness["total_cases"] > 0 else 0,
            "required": 50,
            "reason": "Completude des blocages insuffisante",
        },
        {
            "id": "status_vert",
            "label": "Feu tricolore readiness = VERT",
            "passed": readiness["status"] == "vert",
            "current": readiness["status"],
            "required": "vert",
            "reason": f"Feu tricolore = {readiness['status']} (vert requis)",
        },
    ]
