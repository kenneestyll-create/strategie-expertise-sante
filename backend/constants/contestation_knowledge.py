"""
BASE DE CONNAISSANCES — REGIME SPECIAL RATP / CCAS
====================================================
Sources :
- Documents officiels CCAS RATP (courriers notification MP, contestation IPP)
- Site officiel ccas-ratp.fr (procedures MP, CSOM, Commission Medicale)
- Conseil de Prevoyance RATP (conseil-de-prevoyance-ratp.com)
- Articles du Code de la Securite Sociale (R.441-10, R.441-14, L.443-1, L.454-1)
Integre le 04/04/2026.

# =========================================================================
# PROPRIETE INTELLECTUELLE — ACTIF STRATEGIQUE SENSIBLE
# Strategie & Expertise Sante — Tous droits reserves.
# Ce fichier contient une base de connaissances metier proprietaire
# (procedures de contestation, logique CCAS RATP, ciblage regime special).
# Toute reproduction, extraction, reutilisation ou transmission sans
# autorisation ecrite est interdite.
#
# ZONE GELEE — MOTEUR IA V1 VALIDE
# Date de gel : 05/04/2026
# Protocole : Aucune modification sans ordre explicite du responsable.
#   Toute evolution future doit suivre le protocole IA_BASELINE_V1.md.
# =========================================================================

Structure :
- RATP_REGIME : architecture complete du regime special RATP
- CONTESTATION_PROCEDURES : procedures par regime (CCAS RATP, regime general CPAM)
- CONTESTATION_STRATEGY : points strategiques transversaux
- get_contestation_context() : helper pour injection dans le prompt LLM
- detect_contestation_context() : detection automatique du regime
"""

# =============================================================================
# ARCHITECTURE DU REGIME SPECIAL RATP
# =============================================================================

RATP_REGIME = {
    "presentation": {
        "nom": "Regime special de la RATP",
        "organisme": "CCAS de la RATP (Caisse de Coordination aux Assurances Sociales)",
        "nature": "Regime special de Securite Sociale pour les agents du cadre permanent RATP (statut EPIC)",
        "couverture": "Maladie, maternite, accidents du travail, maladies professionnelles, invalidite, deces, retraite",
        "particularite": "Les agents RATP ne dependent PAS du regime general (CPAM) mais du regime special gere par la CCAS. Les procedures, delais et interlocuteurs sont specifiques.",
    },
    "coordonnees": {
        "siege": {
            "adresse": "30 rue Championnet, 75887 Paris Cedex 18",
            "telephone": "01 58 76 03 34",
            "site": "www.ccas-ratp.fr",
        },
        "pole_at_mp": {
            "service": "GIS/PAP/ASOS/CCAS/PE — Bureau de liaison MP",
            "bureau": "B203 - GTLY",
            "adresse": "30 rue Championnet, 75887 Paris Cedex 18",
        },
        "medecine_conseil": {
            "service": "RATP / GIS / PSES / CCAS — Medecine conseil",
            "destinataire": "M. Le Medecin-conseil",
            "bureau": "CH34 — LAC CG01",
            "adresse": "30 rue Championnet, 75887 Paris Cedex 18",
        },
        "contestation_administrative_cra": {
            "service": "Commission de Recours Amiable (CRA) de la CCAS",
            "bureau": "Bureau G2210",
            "adresse": "34 rue Championnet, GTLY, 75887 Paris Cedex 18",
        },
        "contestation_medicale_cram": {
            "service": "Secretariat de la Commission de Recours Amiable en matiere Medicale (CRAM) de la CCAS",
            "bureau": "Bureau G1197",
            "adresse": "34 rue Championnet, GTLY, 75887 Paris Cedex 18",
        },
        "commission_medicale_csom": {
            "service": "RATP DRH PST — Commission medicale CSOM",
            "adresse": "LAC YH06, 54 Quai de la Rapee, 75012 Paris",
            "email": "drh-pst-csom@ratp.fr",
        },
        "conseil_prevoyance": {
            "service": "Conseil de Prevoyance de la RATP",
            "missions": "Veille, Conseil, Soutien, Assistance aux agents RATP",
            "adresse": "31 rue Belliard, 75018 Paris",
            "telephone": "01 58 76 03 05 / 01 58 76 72 58",
            "site": "www.conseil-de-prevoyance-ratp.com",
            "note": "Organisme independant qui aide les agents dans leurs demarches (invalidite, arret de travail, maladie professionnelle, inaptitude).",
        },
        "protection_donnees": {
            "email": "cil-ratp@ratp.fr",
            "courrier": "LAC LT73 — 185 rue de Bercy 75012 Paris",
        },
    },
}

# =============================================================================
# PROCEDURES MALADIE PROFESSIONNELLE RATP
# =============================================================================

MALADIE_PROFESSIONNELLE_RATP = {
    "definition": "Maladie consequence de l'exposition plus ou moins prolongee a un risque au cours de l'exercice habituel de l'activite professionnelle.",
    "conditions_reconnaissance": [
        "1. La maladie doit etre inscrite sur l'un des tableaux de maladies professionnelles (Art. L.461-1 CSS).",
        "2. L'agent doit avoir ete expose au risque et en apporter les elements de preuve. La liste des travaux est fixee par un tableau (limitative ou indicative).",
        "3. La maladie doit avoir ete constatee par un medecin dans le delai prevu par le tableau, debutant a la fin de l'exposition au risque.",
        "Systeme complementaire : possible pour les maladies ne figurant pas dans les tableaux ou si la procedure par tableau ne peut aboutir (passage CRRMP).",
    ],
    "procedure_declaration": {
        "etape_1": "Obtenir un certificat medical initial (CMI) du medecin traitant ou specialiste constatant la maladie a caractere professionnel.",
        "etape_2": "Retourner par courrier a la CCAS : la declaration de maladie professionnelle (formulaire CCAS) completee, datee et signee, accompagnee des resultats des examens medicaux complementaires.",
        "etape_3_envoi_declaration": {
            "destinataire": "GIS/PAP/ASOS/CCAS/PE — Bureau de liaison MP",
            "bureau": "B203 - GTLY",
            "adresse": "30 RUE CHAMPIONNET, 75887 PARIS CEDEX 18",
        },
        "etape_3_envoi_volets_medicaux": {
            "destinataire": "RATP / GIS / PSES / CCAS — Medecine conseil — M. Le Medecin-conseil",
            "bureau": "CH34 — LAC CG01",
            "adresse": "30 rue Championnet, 75887 Paris Cedex 18",
            "delai": "Volets 1 et 2 sous 48 heures, cachet de la poste faisant foi",
        },
    },
    "instruction": {
        "article": "R.441-10 du Code de la Securite Sociale",
        "texte_integral": "La Caisse dispose d'un delai de trente jours a compter de la date a laquelle elle a eu connaissance de l'accident ou de deux mois a compter de la date a laquelle elle a eu connaissance de la declaration de maladie professionnelle pour statuer sur le caractere professionnel de l'accident ou de la maladie.",
        "delai_at": "30 jours a compter de la connaissance de l'accident",
        "delai_mp": "2 mois a compter de la reception de la declaration de maladie professionnelle",
        "silence_vaut_acceptation": "En l'absence de decision de la caisse dans le delai prevu, le caractere professionnel de l'accident ou de la maladie est RECONNU (Article R.441-10 alinea 3).",
        "delai_complementaire": {
            "article": "R.441-14 du Code de la Securite Sociale",
            "motif": "Enquete en cours ou necessite d'instruction complementaire",
            "notification": "La CCAS doit informer l'agent de la prise de delai complementaire",
        },
    },
    "contacts_cles": {
        "pole_at_mp": "Pole AT/MP et Indemnisation de la CCAS de la RATP",
        "prestations_especes": "Entite Prestations en especes de la CCAS de la RATP",
    },
}

# =============================================================================
# CONGE SPECIAL D'ORDRE MEDICAL (CSOM) — SPECIFIQUE RATP
# =============================================================================

CSOM_RATP = {
    "definition": "Autorisation d'absence avec solde permettant d'amenager le temps de travail des salaries dont la capacite de travail est durablement diminuee du fait de la maladie.",
    "nature": "Dispositif specifique RATP encadre par l'accord du 12 juillet 2024.",
    "taux": "Entre 10% et 60%, attribue par la Commission medicale CSOM.",
    "temps_travail_effectif": "Les autorisations d'absence CSOM sont considerees comme du temps de travail effectif pour les droits (remuneration, conges, ARTT).",
    "conditions": {
        "condition_1": "Etre salarie de l'EPIC RATP (statut ou non).",
        "condition_2_cumulative": [
            "Etre apte a un emploi",
            "ET etre ou avoir ete atteint de :",
            "- ALD 30 (affection de longue duree)",
            "- Affection grave hors liste (31eme maladie)",
            "- Polypathologies (32eme maladie)",
            "- Polytraumatismes necessitant des soins",
        ],
        "exception": "Salaries dont la pathologie n'est pas prevue : courrier circonstancie au responsable de l'unite PST pour etude exceptionnelle.",
    },
    "procedure": {
        "demande": "Adresser la demande a la Commission medicale du CSOM de la RATP.",
        "examen": "Consultation par la Commission medicale composee de deux medecins du travail.",
        "decision": "Attribution d'un taux de CSOM (10% a 60%) pour une duree determinee.",
        "contact": "RATP DRH PST, LAC YH06, 54 Quai de la Rapee, 75012 Paris — drh-pst-csom@ratp.fr",
    },
    "incompatibilites": {
        "temps_partiel": "Le CSOM suspend toutes les conventions a temps partiel (sauf conge parental d'education).",
        "temps_partiel_therapeutique": "CSOM et temps partiel therapeutique sont incompatibles (objectifs differents).",
        "cpa": "Cessation progressive d'activite suspendue pendant le CSOM.",
    },
}

# =============================================================================
# COMMISSION MEDICALE RATP — VOIES DE RECOURS
# =============================================================================

COMMISSION_MEDICALE_RATP = {
    "role": "Instance medicale RATP statuant sur l'aptitude, l'invalidite, la reforme medicale des agents.",
    "recours": {
        "droit": "Tout agent a le droit de faire appel de la decision prise a son egard par la Commission Medicale.",
        "delai": "2 mois a compter du jour de la decision contestee.",
        "assistance": "L'interesse peut se faire assister par un medecin de son choix, entendu a titre consultatif.",
    },
    "articles_statut": {
        "article_80": "Disposition du statut RATP relative aux droits des agents en matiere medicale.",
        "article_83": "Disposition relative aux conditions de la reforme medicale.",
        "article_84": "Disposition relative aux modalites de la reforme.",
    },
}

# =============================================================================
# PROCEDURES DE CONTESTATION (par regime / organisme)
# =============================================================================

CONTESTATION_PROCEDURES = {
    "ccas_ratp": {
        "nom": "CCAS de la RATP",
        "description": "Caisse de Coordination aux Assurances Sociales de la RATP. Regime special couvrant les agents RATP.",
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
            "description": "Si l'accident est imputable a un tiers, l'assure conserve le droit de demander reparation du prejudice cause, conformement aux regles de droit commun, dans la mesure ou ce prejudice n'est pas repare par les prestations du Livre IV du CSS.",
            "obligation": "Si l'assure intente une action, il est tenu d'appeler la RATP en declaration de jugement commun.",
        },
        "revision": {
            "base_legale": "Articles L.443-1 et R.443-1 du Code de la Securite Sociale",
            "delai_initial": "2 ans suivant la date de consolidation",
            "delai_subsequent": "Intervalle minimum d'un an entre chaque revision",
            "procedure": "Adresser la demande au secretariat de la Medecine-conseil, accompagnee d'un certificat medical detaille.",
            "note": "L'entite Prestations en Especes peut egalement constater une aggravation ou amelioration lors d'un examen de controle et proposer une modification du taux.",
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
# POINTS STRATEGIQUES TRANSVERSAUX
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
    "specificites_ratp": [
        "Les agents RATP ne dependent PAS de la CPAM mais de la CCAS — les procedures et interlocuteurs sont differents.",
        "Le Conseil de Prevoyance de la RATP (31 rue Belliard, 75018) peut accompagner l'agent dans ses demarches de contestation.",
        "La Commission Medicale RATP a ses propres voies de recours (appel dans 2 mois, assistance par medecin de son choix).",
        "Le CSOM (Conge Special d'Ordre Medical) est un dispositif specifique RATP permettant d'amenager le temps de travail (taux 10-60%).",
        "Le silence de la CCAS au-dela du delai d'instruction (2 mois pour MP, 30 jours pour AT) vaut reconnaissance du caractere professionnel (Art. R.441-10).",
        "La CCAS peut prendre un delai complementaire (Art. R.441-14) en raison d'une enquete en cours — elle doit en informer l'agent.",
        "Volets medicaux 1 et 2 a envoyer a la Medecine-conseil sous 48h (cachet de la poste).",
    ],
    "articles_reference": {
        "R.441-10": "Delais d'instruction (30j AT, 2 mois MP). Silence = reconnaissance.",
        "R.441-14": "Delai complementaire d'instruction pour enquete.",
        "R.142-1": "Contestation des decisions des organismes de Securite Sociale.",
        "R.711-20": "Contestation specifique aux regimes speciaux.",
        "R.711-21": "Contestation specifique aux regimes speciaux (suite).",
        "L.443-1": "Revision du taux d'IPP apres consolidation.",
        "R.443-1": "Modalites de la revision du taux.",
        "L.454-1": "Recours contre tiers responsable.",
        "L.461-1": "Tableaux des maladies professionnelles.",
        "L.432-6": "Lesions rattachees a un AT/MP anterieur.",
    },
}


# =============================================================================
# HELPER : get_contestation_context()
# =============================================================================

def get_contestation_context(regime=None):
    """
    Retourne le contexte de contestation IPP et procedures RATP injectable dans le prompt LLM.
    regime: 'ccas_ratp', 'regime_general', ou None (tous).
    """
    lines = []
    lines.append("=== BASE DE CONNAISSANCES — CONTESTATION TAUX IPP & PROCEDURES ===\n")

    # Si CCAS RATP, ajouter le contexte complet du regime special
    if regime == "ccas_ratp" or regime is None:
        lines.append("--- REGIME SPECIAL RATP (CCAS) ---")
        lines.append(f"Organisme : {RATP_REGIME['presentation']['organisme']}")
        lines.append(f"Particularite : {RATP_REGIME['presentation']['particularite']}")
        lines.append("")

        # Procedure MP
        lines.append("DECLARATION MALADIE PROFESSIONNELLE (RATP) :")
        mp = MALADIE_PROFESSIONNELLE_RATP
        for cond in mp["conditions_reconnaissance"]:
            lines.append(f"  {cond}")
        lines.append(f"  Envoi declaration : {mp['procedure_declaration']['etape_3_envoi_declaration']['destinataire']}, {mp['procedure_declaration']['etape_3_envoi_declaration']['bureau']}, {mp['procedure_declaration']['etape_3_envoi_declaration']['adresse']}")
        lines.append(f"  Envoi volets medicaux : {mp['procedure_declaration']['etape_3_envoi_volets_medicaux']['destinataire']}, {mp['procedure_declaration']['etape_3_envoi_volets_medicaux']['bureau']}, sous {mp['procedure_declaration']['etape_3_envoi_volets_medicaux']['delai']}")
        lines.append("")

        # Delais instruction
        instr = mp["instruction"]
        lines.append("DELAIS D'INSTRUCTION :")
        lines.append(f"  AT : {instr['delai_at']}")
        lines.append(f"  MP : {instr['delai_mp']}")
        lines.append(f"  SILENCE = RECONNAISSANCE : {instr['silence_vaut_acceptation']}")
        lines.append(f"  Delai complementaire (Art. {instr['delai_complementaire']['article']}) : {instr['delai_complementaire']['motif']}")
        lines.append("")

        # CSOM
        lines.append("CONGE SPECIAL D'ORDRE MEDICAL (CSOM) — specifique RATP :")
        lines.append(f"  {CSOM_RATP['definition']}")
        lines.append(f"  Taux : {CSOM_RATP['taux']}")
        for cond in CSOM_RATP["conditions"]["condition_2_cumulative"]:
            lines.append(f"  {cond}")
        lines.append(f"  Contact : {CSOM_RATP['procedure']['contact']}")
        lines.append("")

        # Commission Medicale
        lines.append("COMMISSION MEDICALE RATP — voies de recours :")
        cm = COMMISSION_MEDICALE_RATP["recours"]
        lines.append(f"  {cm['droit']}")
        lines.append(f"  Delai : {cm['delai']}")
        lines.append(f"  Assistance : {cm['assistance']}")
        lines.append("")

        # Conseil de Prevoyance
        cp = RATP_REGIME["coordonnees"]["conseil_prevoyance"]
        lines.append(f"CONSEIL DE PREVOYANCE RATP : {cp['missions']}")
        lines.append(f"  Adresse : {cp['adresse']}")
        lines.append(f"  Telephone : {cp['telephone']}")
        lines.append(f"  {cp['note']}")
        lines.append("")

    # Points strategiques
    lines.append("POINTS STRATEGIQUES CLES :")
    for pt in CONTESTATION_STRATEGY["points_cles"]:
        lines.append(f"  - {pt}")

    if regime == "ccas_ratp" or regime is None:
        lines.append("\nSPECIFICITES RATP :")
        for pt in CONTESTATION_STRATEGY["specificites_ratp"]:
            lines.append(f"  - {pt}")

    lines.append("\nREVISION APRES CONSOLIDATION :")
    for pt in CONTESTATION_STRATEGY["revision_apres_consolidation"]:
        lines.append(f"  - {pt}")

    lines.append("\nRECOURS CONTRE TIERS :")
    for pt in CONTESTATION_STRATEGY["recours_tiers"]:
        lines.append(f"  - {pt}")

    lines.append("\nERREURS FREQUENTES A SIGNALER :")
    for pt in CONTESTATION_STRATEGY["erreurs_frequentes"]:
        lines.append(f"  - {pt}")

    # Procedures de contestation specifiques
    regimes_to_show = [regime] if regime and regime in CONTESTATION_PROCEDURES else list(CONTESTATION_PROCEDURES.keys())

    for r in regimes_to_show:
        proc = CONTESTATION_PROCEDURES[r]
        lines.append(f"\n=== CONTESTATION — {proc['nom']} ===")

        contest = proc["contestation"]
        lines.append(f"Delai : {contest['delai']}")
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
            lines.append(f"  Procedure : {rev['procedure']}")

    # Articles de reference
    lines.append("\nARTICLES DE REFERENCE :")
    for art, desc in CONTESTATION_STRATEGY["articles_reference"].items():
        lines.append(f"  Art. {art} : {desc}")

    return "\n".join(lines)


# =============================================================================
# HELPER : detect_contestation_context()
# =============================================================================

def detect_contestation_context(text):
    """
    Detecte si le texte mentionne un contexte de contestation IPP / regime RATP / maladie professionnelle.
    Retourne le regime detecte ou None.
    """
    import unicodedata
    def normalize(s):
        return unicodedata.normalize("NFD", (s or "").lower()).encode("ascii", "ignore").decode("ascii")

    text_norm = normalize(text)

    # Detection CCAS RATP
    ratp_keywords = [
        "ratp", "ccas", "ccas ratp", "cram de la ccas", "cra de la ccas",
        "championnet", "gtly", "regime special ratp", "agent ratp",
        "conseil de prevoyance", "commission medicale ratp", "csom",
        "conge special d'ordre medical", "conge special ordre medical",
        "prestations en especes de la ccas", "pole at/mp",
        "medecine-conseil ratp", "medecine conseil ratp",
    ]
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
        "maladie professionnelle", "declaration mp",
    ]
    for kw in contestation_keywords:
        if kw in text_norm:
            return "regime_general"

    return None
