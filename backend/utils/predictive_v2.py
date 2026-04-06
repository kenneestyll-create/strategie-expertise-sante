"""
PREDICTIVE V2 — Module d'analyse predictive dormant
=====================================================
PROPRIETE INTELLECTUELLE — ACTIF STRATEGIQUE SENSIBLE
Strategie & Expertise Sante — Tous droits reserves.

STATUT : DORMANT — Ce module est preinstalle mais totalement inactif.
Il ne s'active QUE lorsque le feature flag predictive_v2_enabled = True
dans la collection app_config, ET que les conditions de readiness sont
reunies (>= 500 cas exploitables, score >= 70, diversite suffisante).

PHILOSOPHIE : Aucune prediction de resultat judiciaire. Aucune promesse.
Uniquement : detection de fragilites, anticipation de blocages, reperage
de signaux, score de robustesse, alerte contextuelle, priorisation.

Formulations autorisees :
- "ce type de dossier expose souvent a..."
- "point de vigilance frequent"
- "facteur de fragilite possible"
- "levier a renforcer"
- "zone a documenter davantage"
- "element souvent determinant"

Formulations INTERDITES :
- "vous serez refuse"
- "X% de chance de gagner"
- "le tribunal donnera raison"
- "votre contrat couvre cela"
- "la MDPH va accepter"
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger("config")


# =============================================================================
# FEATURE FLAG — LECTURE DEPUIS MONGODB
# =============================================================================

async def is_v2_enabled(db) -> bool:
    """Verifie si la V2 est activee via le feature flag en base."""
    config = await db.app_config.find_one({"key": "predictive_v2_enabled"}, {"_id": 0})
    if not config:
        return False
    return config.get("value", False) is True


async def get_v2_config(db) -> dict:
    """Recupere toute la configuration V2 depuis app_config."""
    defaults = {
        "predictive_v2_enabled": False,
        "v2_min_readiness_score": 70,
        "v2_min_cases": 500,
        "v2_max_alerts_per_analysis": 5,
        "v2_prudence_level": "haute",
    }
    configs = await db.app_config.find(
        {"key": {"$in": list(defaults.keys())}}, {"_id": 0}
    ).to_list(20)
    result = dict(defaults)
    for c in configs:
        result[c["key"]] = c["value"]
    return result


async def set_v2_config(db, key: str, value):
    """Met a jour une config V2 dans app_config (upsert)."""
    await db.app_config.update_one(
        {"key": key},
        {"$set": {"key": key, "value": value, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )


# =============================================================================
# ANALYSE PREDICTIVE — MOTEUR DORMANT
# =============================================================================

FRAGILITE_RULES = [
    {
        "id": "no_medical_cert",
        "label": "Absence probable de certificat medical detaille",
        "signal": "facteur de fragilite possible",
        "keywords": ["certificat medical", "cerfa", "certificat detaille"],
        "condition": "absent",
        "severity": "haute",
        "advice": "zone a documenter davantage — un certificat medical detaille est souvent determinant",
    },
    {
        "id": "no_proof_of_exposure",
        "label": "Deficit probatoire potentiel",
        "signal": "point de vigilance frequent",
        "keywords": ["preuve", "prouver", "probatoire", "attestation", "objectiver"],
        "condition": "absent",
        "severity": "haute",
        "advice": "ce type de dossier expose souvent a un blocage probatoire — levier a renforcer",
    },
    {
        "id": "deadline_risk",
        "label": "Risque de forclusion / delai",
        "signal": "point de vigilance frequent",
        "keywords": ["delai", "forclusion", "prescription", "hors delai", "trop tard"],
        "condition": "present",
        "severity": "critique",
        "advice": "element souvent determinant — verifier les delais avant toute demarche",
    },
    {
        "id": "weak_functional_translation",
        "label": "Traduction fonctionnelle insuffisante",
        "signal": "facteur de fragilite possible",
        "keywords": ["retentissement", "quotidien", "fonctionnel", "autonomie", "actes essentiels"],
        "condition": "absent",
        "severity": "moyenne",
        "advice": "zone a documenter davantage — le retentissement fonctionnel est souvent sous-documente",
    },
    {
        "id": "complexity_high",
        "label": "Complexite elevee detectee",
        "signal": "ce type de dossier expose souvent a des aleas supplementaires",
        "keywords": [],
        "condition": "complexity_high",
        "severity": "informative",
        "advice": "un accompagnement expert est recommande pour ce niveau de complexite",
    },
    {
        "id": "no_project_vie",
        "label": "Projet de vie non mentionne (MDPH)",
        "signal": "facteur de fragilite possible",
        "keywords": ["projet de vie", "journee type", "mdph", "aah", "pch"],
        "condition": "mdph_no_project",
        "severity": "haute",
        "advice": "zone a documenter davantage — le projet de vie est determinant pour la MDPH",
    },
    {
        "id": "undervaluation_risk",
        "label": "Risque de sous-evaluation du taux",
        "signal": "point de vigilance frequent",
        "keywords": ["sous-evaluation", "taux trop bas", "revalorisation", "contestation taux"],
        "condition": "present",
        "severity": "moyenne",
        "advice": "levier a renforcer — documenter les aggravations et le retentissement reel",
    },
    {
        "id": "no_witnesses",
        "label": "Absence de temoignages de l'entourage",
        "signal": "facteur de fragilite possible",
        "keywords": ["temoignage", "aidant", "proche", "entourage", "tiers"],
        "condition": "absent",
        "severity": "basse",
        "advice": "element souvent determinant — les temoignages renforcent la credibilite du dossier",
    },
]


def _normalize(text):
    """Normalise le texte pour la detection par mots-cles."""
    import unicodedata
    return unicodedata.normalize("NFD", (text or "").lower()).encode("ascii", "ignore").decode("ascii")


def run_predictive_analysis(situation_text, type_dossier="", regime="", case_features=None):
    """
    Execute l'analyse predictive V2 sur un texte de situation.
    Retourne un dict avec les alertes, le score de robustesse et les recommandations.
    Ne fait PAS d'appel LLM — logique par regles uniquement.
    """
    text_norm = _normalize(situation_text)
    alerts = []

    for rule in FRAGILITE_RULES:
        triggered = False

        if rule["condition"] == "absent":
            has_keyword = any(kw in text_norm for kw in rule["keywords"])
            if not has_keyword and rule["keywords"]:
                triggered = True

        elif rule["condition"] == "present":
            has_keyword = any(kw in text_norm for kw in rule["keywords"])
            if has_keyword:
                triggered = True

        elif rule["condition"] == "complexity_high":
            if case_features and case_features.get("niveau_complexite") == "eleve":
                triggered = True

        elif rule["condition"] == "mdph_no_project":
            is_mdph = any(kw in text_norm for kw in ["mdph", "aah", "pch", "rqth"])
            has_project = any(kw in text_norm for kw in ["projet de vie", "journee type"])
            if is_mdph and not has_project:
                triggered = True

        if triggered:
            alerts.append({
                "rule_id": rule["id"],
                "label": rule["label"],
                "signal": rule["signal"],
                "severity": rule["severity"],
                "advice": rule["advice"],
            })

    # Score de robustesse (inverse de fragilite)
    severity_weights = {"critique": 20, "haute": 15, "moyenne": 8, "basse": 4, "informative": 2}
    total_penalty = sum(severity_weights.get(a["severity"], 0) for a in alerts)
    robustness_score = max(0, min(100, 100 - total_penalty))

    # Niveau de robustesse
    if robustness_score >= 80:
        robustness_level = "solide"
    elif robustness_score >= 60:
        robustness_level = "correct"
    elif robustness_score >= 40:
        robustness_level = "fragile"
    else:
        robustness_level = "tres_fragile"

    # Tri par severite
    severity_order = {"critique": 0, "haute": 1, "moyenne": 2, "basse": 3, "informative": 4}
    alerts.sort(key=lambda a: severity_order.get(a["severity"], 5))

    return {
        "alerts": alerts,
        "alert_count": len(alerts),
        "robustness_score": robustness_score,
        "robustness_level": robustness_level,
        "analysis_version": "v2_dormant_1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "disclaimer": "Analyse interne experimentale. Ne constitue pas un avis juridique. Formulations conditionnelles uniquement.",
    }


def generate_v2_context_block(v2_result, max_alerts=5):
    """
    Genere un bloc textuel injectable dans le SYSTEM prompt (futur).
    Ce bloc est formule de maniere conditionnelle et prudente.
    """
    if not v2_result or not v2_result.get("alerts"):
        return ""

    lines = [
        "\n--- SIGNAUX INTERNES V2 (experimentaux, formulations conditionnelles) ---",
        f"Score de robustesse estime : {v2_result['robustness_score']}/100 ({v2_result['robustness_level']})",
        "",
    ]

    for alert in v2_result["alerts"][:max_alerts]:
        lines.append(f"- [{alert['severity'].upper()}] {alert['signal']} : {alert['advice']}")

    lines.append("")
    lines.append("Note : ces signaux sont des observations internes basees sur l'experience documentee. Adapter au cas reel.")
    lines.append("--- FIN SIGNAUX V2 ---\n")

    return "\n".join(lines)


# =============================================================================
# ANALYSE COMPARATIVE V1 vs V2 (sandbox)
# =============================================================================

def compare_v1_v2(v1_analysis_text, v2_result):
    """
    Compare une sortie V1 avec les signaux V2.
    Outil admin interne uniquement.
    """
    v1_text_norm = _normalize(v1_analysis_text)

    comparison = {
        "v2_alerts_total": v2_result.get("alert_count", 0),
        "v2_robustness": v2_result.get("robustness_score", 0),
        "v2_robustness_level": v2_result.get("robustness_level", ""),
        "alerts_already_in_v1": [],
        "alerts_new_in_v2": [],
    }

    for alert in v2_result.get("alerts", []):
        # Verifier si le V1 mentionne deja cette problematique
        keywords_to_check = FRAGILITE_RULES[0]["keywords"]
        for rule in FRAGILITE_RULES:
            if rule["id"] == alert["rule_id"]:
                keywords_to_check = rule["keywords"]
                break
        mentioned_in_v1 = any(kw in v1_text_norm for kw in keywords_to_check) if keywords_to_check else False

        entry = {"rule_id": alert["rule_id"], "label": alert["label"], "severity": alert["severity"]}
        if mentioned_in_v1:
            comparison["alerts_already_in_v1"].append(entry)
        else:
            comparison["alerts_new_in_v2"].append(entry)

    comparison["v2_added_value"] = len(comparison["alerts_new_in_v2"])
    return comparison
