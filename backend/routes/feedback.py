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


# =============================================================================
# SYNTHESE INTELLIGENTE (admin — aggregation rule-based)
# =============================================================================

# Themes de regroupement pour l'extraction de signaux
SIGNAL_THEMES = {
    "delais_administratifs": ["delai", "attente", "temps", "lent", "long", "mois", "semaine", "retard", "reponse"],
    "complexite_demarches": ["complique", "complexe", "difficile", "comprend pas", "perdu", "confus", "lourd", "paperasse", "formulaire"],
    "manque_accompagnement": ["seul", "aide", "accompagnement", "guide", "soutien", "personne", "abandonne", "suivi", "humain"],
    "cout_tarif": ["cher", "prix", "tarif", "cout", "budget", "payer", "gratuit", "financier", "argent"],
    "information_insuffisante": ["information", "savoir", "comprendre", "expliquer", "clair", "detail", "documentation", "ressource"],
    "expertise_medicale": ["medecin", "expert", "expertise", "medical", "diagnostic", "certificat", "irm", "consultation"],
    "probleme_juridique": ["avocat", "tribunal", "recours", "juridique", "droit", "procedure", "jugement", "contentieux"],
    "assurance_litige": ["assurance", "contrat", "garantie", "indemnisation", "refus", "assureur", "sinistre", "franchise"],
    "mdph_handicap": ["mdph", "handicap", "aah", "rqth", "invalidite", "incapacite", "reconnaissance", "pch"],
    "incomprehension_offre": ["service", "offre", "cabinet", "quoi", "pourquoi", "difference", "propose", "mission"],
}

SIGNAL_LABELS = {
    "delais_administratifs": "Delais et lenteurs administratives",
    "complexite_demarches": "Complexite des demarches",
    "manque_accompagnement": "Manque d'accompagnement humain",
    "cout_tarif": "Frein financier / cout",
    "information_insuffisante": "Information insuffisante",
    "expertise_medicale": "Difficulte d'acces a l'expertise medicale",
    "probleme_juridique": "Blocage juridique",
    "assurance_litige": "Litige avec l'assureur",
    "mdph_handicap": "Complexite MDPH / handicap",
    "incomprehension_offre": "Incomprehension de l'offre du cabinet",
}


def _extract_signals(feedbacks: list) -> dict:
    """Analyse les feedbacks et extrait les signaux forts vs bruit."""
    total = len(feedbacks)
    if total == 0:
        return {"irritants": [], "besoins": [], "clarte": {}, "recommandations": [], "total": 0}

    # Compteurs par theme
    frein_themes = {}
    besoin_themes = {}
    frein_verbatims = {}
    besoin_verbatims = {}

    for fb in feedbacks:
        frein_norm = _normalize(fb.get("frein", ""))
        besoin_norm = _normalize(fb.get("besoin", ""))

        for theme, keywords in SIGNAL_THEMES.items():
            if frein_norm:
                for kw in keywords:
                    if kw in frein_norm:
                        frein_themes[theme] = frein_themes.get(theme, 0) + 1
                        if theme not in frein_verbatims:
                            frein_verbatims[theme] = []
                        if len(frein_verbatims[theme]) < 2:
                            frein_verbatims[theme].append(fb.get("frein", "")[:120])
                        break

            if besoin_norm:
                for kw in keywords:
                    if kw in besoin_norm:
                        besoin_themes[theme] = besoin_themes.get(theme, 0) + 1
                        if theme not in besoin_verbatims:
                            besoin_verbatims[theme] = []
                        if len(besoin_verbatims[theme]) < 2:
                            besoin_verbatims[theme].append(fb.get("besoin", "")[:120])
                        break

    # Seuil signal fort: >= 2 occurrences OU >= 15% du total
    threshold = max(2, int(total * 0.15))

    def build_signals(themes, verbatims):
        sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
        signals = []
        for theme, count in sorted_themes[:5]:
            signals.append({
                "theme": SIGNAL_LABELS.get(theme, theme),
                "count": count,
                "pct": round(count / total * 100),
                "signal": "fort" if count >= threshold else "faible",
                "verbatims": verbatims.get(theme, []),
            })
        return signals

    irritants = build_signals(frein_themes, frein_verbatims)
    besoins = build_signals(besoin_themes, besoin_verbatims)

    # Analyse clarte
    clarte_counts = {"oui": 0, "partiellement": 0, "non": 0}
    for fb in feedbacks:
        c = fb.get("clarte", "")
        if c in clarte_counts:
            clarte_counts[c] += 1

    clarte_total = sum(clarte_counts.values())
    clarte_analysis = {}
    if clarte_total > 0:
        non_pct = round(clarte_counts["non"] / clarte_total * 100)
        partial_pct = round(clarte_counts["partiellement"] / clarte_total * 100)
        oui_pct = round(clarte_counts["oui"] / clarte_total * 100)
        clarte_analysis = {
            "oui": {"count": clarte_counts["oui"], "pct": oui_pct},
            "partiellement": {"count": clarte_counts["partiellement"], "pct": partial_pct},
            "non": {"count": clarte_counts["non"], "pct": non_pct},
            "signal": "fort" if (non_pct + partial_pct) >= 40 else "faible",
            "alerte": (non_pct + partial_pct) >= 40,
        }

    # Recommandations automatiques
    recommandations = []
    if irritants:
        top = irritants[0]
        if top["signal"] == "fort":
            recommandations.append(f"Priorite 1 : Adresser '{top['theme']}' ({top['count']} mentions, {top['pct']}% des retours)")
    if clarte_analysis.get("alerte"):
        recommandations.append(f"Alerte clarte : {clarte_analysis['non']['pct'] + clarte_analysis['partiellement']['pct']}% des clients ne comprennent pas clairement l'offre")
    if besoins:
        top_b = besoins[0]
        if top_b["signal"] == "fort":
            recommandations.append(f"Besoin non couvert dominant : '{top_b['theme']}' ({top_b['count']} mentions)")

    # Sources distribution
    source_counts = {}
    for fb in feedbacks:
        s = fb.get("source", "inconnu") or "inconnu"
        source_counts[s] = source_counts.get(s, 0) + 1

    return {
        "irritants": irritants,
        "besoins": besoins,
        "clarte": clarte_analysis,
        "recommandations": recommandations,
        "sources": source_counts,
        "total": total,
        "seuil_signal_fort": threshold,
    }


@router.get("/synthesis")
async def feedback_synthesis(admin=Depends(get_current_admin)):
    """Synthese intelligente — signaux forts vs bruit, recommandations."""
    docs = await db.strategic_feedback.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).to_list(500)

    synthesis = _extract_signals(docs)
    return synthesis
