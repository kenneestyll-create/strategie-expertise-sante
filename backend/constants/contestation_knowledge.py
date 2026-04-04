"""
BASE DE CONNAISSANCES — PROCEDURES DE CONTESTATION IPP
=======================================================
Source : Document officiel CCAS RATP (notification de taux IPP apres consolidation)
Integre le 04/04/2026.

Structure :
- CONTESTATION_PROCEDURES : procedures par regime (CCAS RATP, regime general CPAM)
- get_contestation_context() : helper pour injecter le contexte dans le prompt
"""

# =============================================================================
# PROCEDURES DE CONTESTATION (par regime / organisme)
# =============================================================================

CONTESTATION_PROCEDURES = {
    "ccas_ratp": {
        "nom": "CCAS de la RATP",
        "description": "Caisse de Coordination aux Assurances Sociales de la RATP. Regime special couvrant les agents RATP.",
        "adresse_siege": "30 rue Championnet, 75887 Paris Cedex 18",
        "telephone": "01 58 76 03 34",
        "site": "www.ccas-ratp.fr",
        "protection_donnees": {
            "email": "cil-ratp@ratp.fr",
            "courrier": "LAC LT73 — 185 rue de Bercy 75012 Paris",
        },
        "contestation": {
            "delai": "2 mois a compter de la reception de la notification",
            "base_legale": "Articles R142-1, R.711-20 et R711-21 du Code de la Securite Sociale",
            "types": {
                "administrative": {
                    "objet": "Contestation d'ordre administratif : calcul, modalites et/ou elements de calcul (a l'exclusion du taux d'IPP), paiement de la prestation.",
                    "instance": "Commission de Recours Amiable (CRA)",
                    "modalite": "Lettre recommandee avec avis de reception",
                    "adresse": {
                        "destinataire": "Commission de Recours Amiable — CRA de la CCAS",
                        "rue": "34 rue Championnet",
                        "batiment": "GTLY",
                        "bureau": "Bureau G2210",
                        "code_postal": "75887 Paris cedex 18",
                    },
                },
                "medicale": {
                    "objet": "Contestation d'ordre medical : taux d'incapacite permanente partielle (IPP), prestations complementaires pour recours a tierces personnes.",
                    "instance": "Commission de Recours Amiable statuant en matiere Medicale (CRAM)",
                    "modalite": "Lettre recommandee avec avis de reception",
                    "adresse": {
                        "destinataire": "Secretariat de la Commission de Recours Amiable en matiere Medicale — CRAM de la CCAS",
                        "rue": "34 rue Championnet",
                        "batiment": "GTLY",
                        "bureau": "Bureau G1197",
                        "code_postal": "75887 Paris cedex 18",
                    },
                },
            },
        },
        "recours_tiers": {
            "base_legale": "Article L.454-1 du Code de la Securite Sociale",
            "description": "Si l'accident est imputable a un tiers, l'assure conserve le droit de demander reparation du prejudice cause, conformement aux regles de droit commun, dans la mesure ou ce prejudice n'est pas repare par les prestations et indemnites legales du Livre IV du Code de la Securite Sociale.",
            "obligation": "Si l'assure intente une action, il est tenu d'appeler la RATP en declaration de jugement commun.",
        },
        "revision": {
            "base_legale": "Articles L.443-1 et R.443-1 du Code de la Securite Sociale",
            "delai_initial": "2 ans suivant la date de consolidation",
            "delai_subsequent": "Intervalle minimum d'un an entre chaque revision",
            "procedure": "Adresser la demande au secretariat de la Medecine-conseil, accompagnee d'un certificat medical detaille.",
            "note": "L'entite Prestations en Especes peut egalement, au cours d'un examen de controle, constater une aggravation ou une amelioration et proposer une modification du taux d'IPP.",
        },
        "conservation_document": "A conserver sans limitation de duree, aucun duplicata ne sera delivre.",
    },
    "regime_general": {
        "nom": "Regime general (CPAM)",
        "description": "Procedure standard pour les salaries du regime general.",
        "contestation": {
            "delai": "2 mois a compter de la notification",
            "base_legale": "Articles R142-1 et suivants du Code de la Securite Sociale",
            "types": {
                "administrative": {
                    "objet": "Contestation administrative (calcul, paiement).",
                    "instance": "Commission de Recours Amiable (CRA) de la CPAM",
                    "modalite": "Lettre recommandee avec avis de reception",
                },
                "medicale": {
                    "objet": "Contestation du taux d'IPP.",
                    "instance": "Tribunal judiciaire (pole social) apres expertise medicale",
                    "modalite": "Recours contentieux apres echec de la CRA",
                    "etapes": [
                        "1. Saisine de la CRA dans les 2 mois",
                        "2. En cas de rejet ou silence de 2 mois : saisine du pole social du tribunal judiciaire",
                        "3. Expertise medicale judiciaire",
                        "4. Jugement",
                    ],
                },
            },
        },
        "revision": {
            "base_legale": "Articles L.443-1 et R.443-1 du Code de la Securite Sociale",
            "delai_initial": "2 ans suivant la date de consolidation",
            "delai_subsequent": "Intervalle minimum d'un an entre chaque revision",
            "procedure": "Demande aupres de la CPAM avec certificat medical detaille attestant l'aggravation.",
        },
    },
}

# =============================================================================
# POINTS STRATEGIQUES TRANSVERSAUX — CONTESTATION TAUX IPP
# =============================================================================

CONTESTATION_STRATEGY = {
    "points_cles": [
        "Le delai de contestation est de 2 MOIS a compter de la reception de la notification — delai strict et non prorogeable.",
        "Distinguer contestation ADMINISTRATIVE (calcul, paiement) et contestation MEDICALE (taux IPP) — les instances et adresses sont differentes.",
        "La contestation medicale du taux IPP doit etre adressee a la CRAM (pas la CRA).",
        "La lettre doit etre RECOMMANDEE avec AVIS DE RECEPTION — toute autre forme peut etre rejetee.",
        "La reclamation doit etre MOTIVEE : joindre certificats medicaux, avis specialistes, descriptions detaillees des sequelles.",
    ],
    "revision_apres_consolidation": [
        "Revision possible dans les 2 ANS suivant la consolidation, puis tous les ans minimum.",
        "Necessite un certificat medical detaille attestant l'aggravation.",
        "L'organisme peut aussi initier une revision lors d'un examen de controle (aggravation OU amelioration).",
        "Attention : une revision peut entrainer une DIMINUTION du taux si amelioration constatee.",
    ],
    "recours_tiers": [
        "Si l'accident est imputable a un tiers, action en reparation possible (droit commun).",
        "Obligation d'appeler l'organisme (RATP, CPAM...) en declaration de jugement commun.",
        "Le prejudice indemnisable est celui non couvert par les prestations du Code de la Securite Sociale.",
    ],
    "erreurs_frequentes": [
        "Confondre CRA (administratif) et CRAM (medical) — la contestation du taux IPP releve du MEDICAL.",
        "Envoyer un courrier simple au lieu d'un recommande AR.",
        "Depasser le delai de 2 mois sans agir.",
        "Ne pas joindre de certificat medical detaille a la contestation.",
        "Ignorer la possibilite de revision en cas d'aggravation apres consolidation.",
        "Ne pas demander l'incidence professionnelle lors de la contestation du taux.",
    ],
}


def get_contestation_context(regime=None):
    """
    Retourne le contexte de contestation IPP injectable dans le prompt LLM.
    regime: 'ccas_ratp', 'regime_general', ou None (tous).
    """
    lines = []
    lines.append("=== PROCEDURES DE CONTESTATION DU TAUX IPP ===\n")

    # Points strategiques transversaux
    lines.append("POINTS STRATEGIQUES CLES :")
    for pt in CONTESTATION_STRATEGY["points_cles"]:
        lines.append(f"  - {pt}")

    lines.append("\nREVISION APRES CONSOLIDATION :")
    for pt in CONTESTATION_STRATEGY["revision_apres_consolidation"]:
        lines.append(f"  - {pt}")

    lines.append("\nRECOURS CONTRE TIERS :")
    for pt in CONTESTATION_STRATEGY["recours_tiers"]:
        lines.append(f"  - {pt}")

    lines.append("\nERREURS FREQUENTES A SIGNALER AU BENEFICIAIRE :")
    for pt in CONTESTATION_STRATEGY["erreurs_frequentes"]:
        lines.append(f"  - {pt}")

    # Procedures specifiques par regime
    regimes_to_show = [regime] if regime and regime in CONTESTATION_PROCEDURES else list(CONTESTATION_PROCEDURES.keys())

    for r in regimes_to_show:
        proc = CONTESTATION_PROCEDURES[r]
        lines.append(f"\n--- {proc['nom']} ---")

        contest = proc["contestation"]
        lines.append(f"Delai de contestation : {contest['delai']}")
        lines.append(f"Base legale : {contest['base_legale']}")

        for type_key, type_info in contest["types"].items():
            lines.append(f"\n  [{type_key.upper()}] {type_info['objet']}")
            lines.append(f"  Instance : {type_info['instance']}")
            lines.append(f"  Modalite : {type_info['modalite']}")
            if "adresse" in type_info:
                addr = type_info["adresse"]
                lines.append(f"  Adresse : {addr['destinataire']}")
                lines.append(f"           {addr['rue']}, {addr.get('batiment', '')}, {addr.get('bureau', '')}")
                lines.append(f"           {addr['code_postal']}")
            if "etapes" in type_info:
                for etape in type_info["etapes"]:
                    lines.append(f"    {etape}")

        rev = proc.get("revision")
        if rev:
            lines.append(f"\n  REVISION : {rev['base_legale']}")
            lines.append(f"  Delai initial : {rev['delai_initial']}")
            lines.append(f"  Delai subsequent : {rev['delai_subsequent']}")
            lines.append(f"  Procedure : {rev['procedure']}")

        if r == "ccas_ratp":
            lines.append(f"\n  Coordonnees : {proc['telephone']} — {proc['site']}")

    return "\n".join(lines)


def detect_contestation_context(text):
    """
    Detecte si le texte mentionne un contexte de contestation IPP / taux / consolidation.
    Retourne le regime detecte ou None.
    """
    import unicodedata
    def normalize(s):
        return unicodedata.normalize("NFD", (s or "").lower()).encode("ascii", "ignore").decode("ascii")

    text_norm = normalize(text)

    # Detection CCAS RATP
    ratp_keywords = ["ratp", "ccas", "ccas ratp", "cram de la ccas", "cra de la ccas", "championnet", "gtly"]
    for kw in ratp_keywords:
        if kw in text_norm:
            return "ccas_ratp"

    # Detection contexte contestation IPP (regime general par defaut)
    contestation_keywords = [
        "contestation taux", "contester le taux", "contester mon taux",
        "contestation ipp", "contester ipp", "contester l'ipp",
        "taux ipp", "taux d'ipp", "sous-evaluation", "sous evaluation",
        "revision taux", "reviser le taux", "aggravation",
        "commission de recours", "cra ", "cram ",
        "apres consolidation", "post-consolidation",
        "notification de taux", "taux incapacite",
        "contester", "contestation", "taux trop bas", "taux trop faible",
    ]
    for kw in contestation_keywords:
        if kw in text_norm:
            return "regime_general"

    return None
