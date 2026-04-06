"""
CASE OUTCOME MEMORY — Collecte structuree pour apprentissage metier futur
=========================================================================
Module de preparation V2 "IA d'Anticipation".

# =========================================================================
# PROPRIETE INTELLECTUELLE — ACTIF STRATEGIQUE SENSIBLE
# Strategie & Expertise Sante — Tous droits reserves.
# Ce fichier constitue une architecture d'apprentissage proprietaire.
# Toute reproduction, extraction ou reutilisation sans autorisation
# ecrite est interdite.
#
# IMPORTANT : Ce module est SILENCIEUX. Aucun affichage client.
#   Aucune prediction. Aucun score de probabilite. Collecte interne
#   uniquement, non bloquante, conforme RGPD (respect improvement_optout).
# =========================================================================
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger("config")


# =============================================================================
# EXTRACTION DE FEATURES STRUCTUREES (keyword-based, pas de LLM)
# =============================================================================

BLOCAGE_KEYWORDS = {
    "probatoire": ["preuve", "prouver", "probatoire", "justificatif", "attestation manquante", "documenter", "objectiver"],
    "medical": ["certificat medical", "expertise medicale", "bilan medical", "avis medical", "medecin conseil", "consolidation"],
    "administratif": ["delai", "forclusion", "prescription", "formulaire", "cerfa", "notification", "procedure"],
    "traduction_fonctionnelle": ["retentissement", "quotidien", "fonctionnel", "autonomie", "actes essentiels", "projet de vie"],
    "qualification": ["taux", "ipp", "incapacite", "evaluation", "bareme", "sous-evaluation", "revalorisation"],
}

PIECE_KEYWORDS = {
    "certificat_medical_detaille": ["certificat medical", "cerfa 15695", "certificat detaille"],
    "bilan_fonctionnel": ["bilan fonctionnel", "bilan ergotherapique", "bilan neuropsychologique"],
    "projet_de_vie": ["projet de vie", "journee type"],
    "attestation_employeur": ["attestation employeur", "medecin du travail", "restrictions d'aptitude"],
    "historique_arrets": ["historique", "arrets de travail", "hospitalisations"],
    "bilans_specialises": ["bilan specialise", "irm", "scanner", "emg", "eeg"],
    "temoignages": ["temoignage", "aidant", "proche", "entourage"],
}

LEVIER_KEYWORDS = {
    "expertise_amiable": ["expertise amiable", "contre-expertise", "expertise contradictoire"],
    "recours_cra": ["commission de recours", "cra", "recours amiable"],
    "recours_tci": ["tribunal", "tci", "contentieux", "pole social"],
    "rapo_mdph": ["rapo", "recours administratif prealable"],
    "consolidation": ["consolidation", "date de consolidation", "rechute"],
    "reclassification": ["reclassification", "revalorisation", "taux", "aggravation"],
    "documentation_complementaire": ["completer le dossier", "nouvelles pieces", "bilan complementaire"],
}

FAMILLE_KEYWORDS = {
    "at_mp": ["accident du travail", "maladie professionnelle", "at/mp", "tableau mp"],
    "assurance_emprunteur": ["assurance emprunteur", "garantie itt", "garantie ipt", "pret immobilier"],
    "mdph_aah": ["mdph", "aah", "allocation adulte", "taux d'incapacite"],
    "mdph_pch": ["pch", "prestation de compensation", "aide humaine"],
    "mdph_rqth": ["rqth", "travailleur handicape", "amenagement de poste"],
    "contestation_ipp": ["ipp", "incapacite permanente", "contestation taux"],
    "expertise_medicale": ["expertise medicale", "medecin expert", "medecin conseil"],
    "invalidite": ["invalidite", "pension invalidite", "categorie"],
}


def _normalize(text):
    """Normalise le texte pour la detection par mots-cles."""
    import unicodedata
    return unicodedata.normalize("NFD", (text or "").lower()).encode("ascii", "ignore").decode("ascii")


def _detect_items(text_norm, keyword_map, max_items=5):
    """Detecte les items les plus pertinents par mots-cles."""
    scores = {}
    for key, keywords in keyword_map.items():
        count = sum(1 for kw in keywords if kw in text_norm)
        if count > 0:
            scores[key] = count
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [item[0] for item in sorted_items[:max_items]]


def extract_case_features(analysis_text, type_dossier=None, regime=None, situation=None):
    """
    Extrait des features structurees a partir du texte d'analyse.
    Extraction par mots-cles uniquement (pas de LLM).
    Retourne un dictionnaire de signaux anonymises.
    """
    combined = _normalize(f"{analysis_text or ''} {situation or ''}")

    blocages = _detect_items(combined, BLOCAGE_KEYWORDS, max_items=3)
    pieces = _detect_items(combined, PIECE_KEYWORDS, max_items=5)
    leviers = _detect_items(combined, LEVIER_KEYWORDS, max_items=3)
    familles = _detect_items(combined, FAMILLE_KEYWORDS, max_items=2)

    # Niveau de complexite basique (longueur + nombre de signaux)
    signal_count = len(blocages) + len(pieces) + len(leviers)
    if signal_count >= 8:
        complexite = "eleve"
    elif signal_count >= 4:
        complexite = "moyen"
    else:
        complexite = "faible"

    return {
        "blocages_detectes": blocages,
        "pieces_manquantes_detectees": pieces,
        "leviers_detectes": leviers,
        "familles_situation": familles,
        "niveau_complexite": complexite,
        "signal_count": signal_count,
    }


async def store_case_outcome(db, source, type_dossier, regime, features, quality_score=None, improvement_optout=False):
    """
    Stocke un enregistrement anonymise dans la collection case_outcomes.
    Respecte strictement improvement_optout.
    """
    if improvement_optout:
        logger.debug(f"[CASE_OUTCOME] Opt-out actif, pas de stockage ({source})")
        return None

    import uuid
    record = {
        "id": str(uuid.uuid4()),
        "source": source,
        "categorie_dossier": type_dossier or "",
        "regime_ou_type_garantie": regime or "",
        "blocage_principal": features.get("blocages_detectes", [None])[0] if features.get("blocages_detectes") else "",
        "blocages_secondaires": features.get("blocages_detectes", [])[1:],
        "pieces_manquantes": features.get("pieces_manquantes_detectees", []),
        "leviers_probables": features.get("leviers_detectes", []),
        "famille_situation": features.get("familles_situation", [None])[0] if features.get("familles_situation") else "",
        "niveau_complexite": features.get("niveau_complexite", ""),
        "signal_count": features.get("signal_count", 0),
        "quality_level": quality_score.get("level", "") if quality_score else "",
        "quality_score_value": quality_score.get("score", 0) if quality_score else 0,
        "issue_reelle": "",
        "action_recommandee": "",
        "utilisable_pour_apprentissage": True,
        "improvement_optout": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        await db.case_outcomes.insert_one(record)
        logger.info(f"[CASE_OUTCOME] Stored ({source}, {type_dossier}, complexity={features.get('niveau_complexite')}, signals={features.get('signal_count')})")
        return record["id"]
    except Exception as e:
        logger.warning(f"[CASE_OUTCOME] Storage failed (non-blocking): {e}")
        return None


async def get_case_outcome_stats(db):
    """
    Retourne des statistiques agregees sur les case outcomes.
    Admin-only, pas de donnees identifiantes.
    """
    total = await db.case_outcomes.count_documents({})
    if total == 0:
        return {"total": 0, "message": "Aucune donnee collectee"}

    pipeline_blocage = [
        {"$match": {"blocage_principal": {"$ne": ""}}},
        {"$group": {"_id": "$blocage_principal", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    blocages = await db.case_outcomes.aggregate(pipeline_blocage).to_list(10)

    pipeline_pieces = [
        {"$unwind": "$pieces_manquantes"},
        {"$group": {"_id": "$pieces_manquantes", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    pieces = await db.case_outcomes.aggregate(pipeline_pieces).to_list(10)

    pipeline_famille = [
        {"$match": {"famille_situation": {"$ne": ""}}},
        {"$group": {"_id": "$famille_situation", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    familles = await db.case_outcomes.aggregate(pipeline_famille).to_list(10)

    pipeline_complexite = [
        {"$group": {"_id": "$niveau_complexite", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    complexites = await db.case_outcomes.aggregate(pipeline_complexite).to_list(10)

    pipeline_source = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    sources = await db.case_outcomes.aggregate(pipeline_source).to_list(10)

    pipeline_leviers = [
        {"$unwind": "$leviers_probables"},
        {"$group": {"_id": "$leviers_probables", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    leviers = await db.case_outcomes.aggregate(pipeline_leviers).to_list(10)

    return {
        "total": total,
        "blocages_frequents": [{"blocage": b["_id"], "count": b["count"]} for b in blocages],
        "pieces_manquantes_frequentes": [{"piece": p["_id"], "count": p["count"]} for p in pieces],
        "leviers_frequents": [{"levier": lev["_id"], "count": lev["count"]} for lev in leviers],
        "familles_situation": [{"famille": f["_id"], "count": f["count"]} for f in familles],
        "repartition_complexite": [{"niveau": c["_id"], "count": c["count"]} for c in complexites],
        "repartition_source": [{"source": s["_id"], "count": s["count"]} for s in sources],
    }
