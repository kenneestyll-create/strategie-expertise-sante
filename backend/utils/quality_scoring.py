"""
Scoring qualite interne pour les rapports PDF generes.
Outil de pilotage admin — ne modifie PAS le rendu client.

# =========================================================================
# PROPRIETE INTELLECTUELLE — ACTIF STRATEGIQUE SENSIBLE
# Strategie & Expertise Sante — Tous droits reserves.
# Ce fichier contient un mecanisme d'evaluation proprietaire (criteres de
# scoring, seuils de qualite, grille metier). Toute reproduction,
# extraction, reutilisation ou transmission sans autorisation ecrite
# est interdite.
#
# ZONE GELEE — MOTEUR IA V1 VALIDE
# Date de gel : 05/04/2026
# Protocole : Aucune modification sans ordre explicite du responsable.
#   Toute evolution future doit suivre le protocole IA_BASELINE_V1.md.
# =========================================================================
"""

import re


# Formulations generiques a detecter (signal de faible qualite)
GENERIC_PHRASES = [
    "met en lumière", "met en lumiere",
    "souligne l'importance", "souligne l importance",
    "révèle un enjeu", "revele un enjeu",
    "situation complexe",
    "éléments pertinents", "elements pertinents",
    "à ce stade", "a ce stade",
    "force est de constater",
    "il apparaît que", "il apparait que",
    "dans une logique de",
    "cet aspect mérite", "cet aspect merite",
    "il convient de noter",
    "il est important de souligner",
    "cette dimension",
    "ce volet",
    "sur ce point précis", "sur ce point precis",
    "de manière significative", "de maniere significative",
    "en définitive", "en definitive",
    "paradoxe médico", "paradoxe medico",
    "enjeu triple",
    "angles sous-exploités", "angles sous-exploites",
    "voies ouvertes",
    "situation qui mérite", "situation qui merite",
    "on observe que",
    "il ressort que",
    "il est à noter", "il est a noter",
    "une approche globale",
    "une vision d'ensemble", "une vision d ensemble",
    "dossier intéressant", "dossier interessant",
]

# Mots-cles metier pour detecter la personnalisation
METIER_KEYWORDS = {
    "transport": ["conduite", "conducteur", "chauffeur", "routier", "fimo", "fco", "vibrations", "station assise", "aptitude médicale", "aptitude medicale", "volant"],
    "btp": ["chantier", "manutention", "port de charges", "charges lourdes", "ouvrier", "bâtiment", "batiment", "intempéries", "intemperies", "échafaudage", "echafaudage"],
    "sante": ["soignant", "infirmier", "aide-soignant", "patient", "manutention de patients", "station debout", "hôpital", "hopital", "charges émotionnelles", "charges emotionnelles"],
    "administratif": ["bureau", "écran", "ecran", "saisie", "posture statique", "sédentaire", "sedentaire", "tms membres supérieurs", "tms membres superieurs", "répétitivité", "repetitivite"],
    "securite": ["intervention", "équipements", "equipements", "stress opérationnel", "stress operationnel", "contraintes physiques"],
    "industriel": ["exposition chimique", "bruit", "gestes répétitifs", "gestes repetitifs", "usinage", "technique"],
    "independant": ["libéral", "liberal", "indépendant", "independant", "continuité", "continuite", "couverture at"],
}

# Mots-cles sinistre
SINISTRE_KEYWORDS = {
    "mp": ["maladie professionnelle", "tableau", "crrmp", "exposition", "lien causal", "durée d'exposition", "duree d exposition"],
    "at": ["accident du travail", "fait accidentel", "circonstances", "matérialité", "materialite", "témoins", "temoins"],
    "rechute": ["rechute", "aggravation", "consolidation antérieure", "consolidation anterieure", "nouvelles lésions", "nouvelles lesions"],
    "ipp": ["sous-évaluation", "sous-evaluation", "taux", "barème", "bareme", "incidence professionnelle", "séquelles", "sequelles"],
    "refus": ["refus cpam", "motivation du refus", "voies de recours"],
    "expertise": ["expertise défavorable", "expertise defavorable", "contre-expertise", "contradictions"],
    "invalidite": ["invalidité", "invalidite", "inaptitude", "reclassement", "pension"],
}

# Blocs premium attendus par type de rapport
PREMIUM_BLOCKS = {
    "basic": [
        "vrai nœud", "vrai noeud",
        "étape la plus rentable", "etape la plus rentable",
    ],
    "premium": [
        "vrai nœud", "vrai noeud",
        "renforce", "fragilise",
        "évaluation stratégique rapide", "evaluation strategique rapide",
        "étape la plus rentable", "etape la plus rentable",
    ],
    "dossier_express": [
        "vrai nœud", "vrai noeud",
        "renforce", "fragilise",
        "évaluation stratégique rapide", "evaluation strategique rapide",
        "étape la plus rentable", "etape la plus rentable",
    ],
}


def score_report(analysis_text: str, report_type: str, metier: str = "", sinistre: str = "", blocage: str = "") -> dict:
    """
    Analyse un rapport genere et retourne un scoring qualite interne.
    report_type: 'basic', 'premium', 'dossier_express'
    """
    text_lower = analysis_text.lower()
    scores = {}
    reasons = []

    # 1. Personnalisation metier (0-20)
    metier_score = 0
    metier_lower = metier.lower() if metier else ""
    for category, keywords in METIER_KEYWORDS.items():
        if metier_lower and any(k in metier_lower for k in [category] + keywords[:2]):
            hits = sum(1 for kw in keywords if kw in text_lower)
            metier_score = min(20, hits * 5)
            break
    if not metier_lower:
        for category, keywords in METIER_KEYWORDS.items():
            hits = sum(1 for kw in keywords if kw in text_lower)
            if hits >= 2:
                metier_score = min(20, hits * 4)
                break
    if metier_score >= 15:
        reasons.append("Personnalisation metier forte")
    elif metier_score < 5:
        reasons.append("Personnalisation metier insuffisante")
    scores["personnalisation_metier"] = metier_score

    # 2. Personnalisation sinistre (0-20)
    sinistre_score = 0
    sinistre_lower = sinistre.lower() if sinistre else ""
    for category, keywords in SINISTRE_KEYWORDS.items():
        if sinistre_lower and any(k in sinistre_lower for k in [category] + keywords[:2]):
            hits = sum(1 for kw in keywords if kw in text_lower)
            sinistre_score = min(20, hits * 5)
            break
    if not sinistre_lower:
        for category, keywords in SINISTRE_KEYWORDS.items():
            hits = sum(1 for kw in keywords if kw in text_lower)
            if hits >= 2:
                sinistre_score = min(20, hits * 4)
                break
    if sinistre_score >= 15:
        reasons.append("Adaptation sinistre visible")
    elif sinistre_score < 5:
        reasons.append("Adaptation sinistre faible")
    scores["personnalisation_sinistre"] = sinistre_score

    # 3. Identification du blocage (0-15)
    blocage_score = 0
    blocage_indicators = ["vrai nœud", "vrai noeud", "bloque", "blocage", "frein principal", "difficulté centrale", "difficulte centrale", "en clair"]
    hits = sum(1 for ind in blocage_indicators if ind in text_lower)
    blocage_score = min(15, hits * 4)
    if blocage_score >= 12:
        reasons.append("Blocage principal clairement identifie")
    elif blocage_score < 4:
        reasons.append("Blocage principal mal identifie")
    scores["identification_blocage"] = blocage_score

    # 4. Presence des blocs premium (0-15)
    expected_blocks = PREMIUM_BLOCKS.get(report_type, PREMIUM_BLOCKS["premium"])
    blocks_found = sum(1 for b in expected_blocks if b in text_lower)
    unique_expected = len(set([b.replace("œ", "oe") for b in expected_blocks])) // 2 + 1
    blocs_score = min(15, int((blocks_found / max(len(expected_blocks), 1)) * 15))
    if blocs_score >= 12:
        reasons.append("Blocs premium complets")
    elif blocs_score < 8:
        reasons.append("Blocs premium incomplets")
    scores["blocs_premium"] = blocs_score

    # 5. Densite utile (0-15) — ratio contenu substantiel vs longueur
    words = analysis_text.split()
    word_count = len(words)
    target_ranges = {"basic": (400, 600), "premium": (1600, 2500), "dossier_express": (1800, 2900)}
    target_min, target_max = target_ranges.get(report_type, (1000, 2500))
    if target_min <= word_count <= target_max:
        densite_score = 15
    elif word_count < target_min * 0.7:
        densite_score = 5
        reasons.append("Rapport trop court")
    elif word_count > target_max * 1.3:
        densite_score = 8
        reasons.append("Rapport trop long")
    else:
        densite_score = 11
    scores["densite_utile"] = densite_score

    # 6. Faible taux de genericite (0-10) — moins de formulations generiques = mieux
    generic_count = sum(1 for phrase in GENERIC_PHRASES if phrase in text_lower)
    if generic_count == 0:
        genericite_score = 10
        reasons.append("Zero formulation generique")
    elif generic_count <= 2:
        genericite_score = 7
    elif generic_count <= 5:
        genericite_score = 4
        reasons.append(f"{generic_count} formulations generiques detectees")
    else:
        genericite_score = 1
        reasons.append(f"{generic_count} formulations generiques — qualite degradee")
    scores["faible_genericite"] = genericite_score

    # 7. Coherence globale (0-5) — presence de structure, pas de contradictions evidentes
    structure_markers = ["##", "###", "**", "- "]
    structure_count = sum(1 for m in structure_markers if m in analysis_text)
    coherence_score = min(5, structure_count)
    scores["coherence_globale"] = coherence_score

    # Score total
    total = sum(scores.values())

    # Niveau qualite
    if total >= 80:
        level = "Excellence"
    elif total >= 60:
        level = "Premium"
    elif total >= 40:
        level = "Solide"
    else:
        level = "A Renforcer"

    # Limiter a 4 raisons max
    reasons = reasons[:4]
    if not reasons:
        reasons = ["Rapport dans les normes"]

    return {
        "score": total,
        "max_score": 100,
        "level": level,
        "details": scores,
        "reasons": reasons,
        "word_count": word_count,
        "generic_count": generic_count,
    }
