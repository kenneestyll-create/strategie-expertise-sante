"""
SEED PATTERNS — Base de demarrage pour knowledge_patterns
==========================================================
Patterns sobres, premium, credibles et utiles.
Pas de remplissage. Enseignements abstraits non identifiants.
A executer UNE FOIS pour initialiser la base.

# =========================================================================
# ZONE GELEE — MOTEUR IA V1 VALIDE
# Date de gel : 05/04/2026
# Perimetre : 14 seed patterns originaux (AT/MP/assurantiel/contestation)
#   + 26 patterns MDPH Premium v1 (AAH/RSDAE/PCH/RQTH/CMI/invalidantes).
#   Fonctions seed : seed_knowledge_patterns(), seed_mdph_patterns().
# Avertissement : Ne pas modifier les patterns existants sans ordre explicite.
#   L'ajout de NOUVEAUX patterns est autorise en suivant le protocole
#   IA_BASELINE_V1.md (creation incrementale, validation admin, test
#   de non-regression).
# =========================================================================
"""

SEED_PATTERNS = [
    # --- BLOCAGES ---
    {
        "categorie_dossier": "maladie_professionnelle",
        "metier": "transport_conduite",
        "type_sinistre": "mp_tms",
        "blocage_principal": "probatoire",
        "pattern_type": "blocage",
        "description": "Dans les postes de conduite prolongee, le retentissement fonctionnel reel est souvent sous-objective dans les expertises initiales. Le lien entre gestes professionnels et pathologie necessite une description precise des contraintes posturales et vibratoires.",
        "niveau_confiance": "eleve",
        "tags": ["mp", "tms", "conduite", "probatoire", "expertise"],
    },
    {
        "categorie_dossier": "litige_assurantiel",
        "type_garantie": "IPT",
        "blocage_principal": "contractuel",
        "pattern_type": "blocage",
        "description": "En litige IPT/ITT, la difficulte centrale vient souvent d'un ecart entre l'incapacite medicale vecue et la definition contractuelle opposable. La garantie peut etre refusee non pas parce que l'assure va bien, mais parce que sa situation ne correspond pas aux criteres contractuels stricts.",
        "niveau_confiance": "eleve",
        "tags": ["ipt", "itt", "assurance", "definition_contractuelle", "ecart"],
    },
    {
        "categorie_dossier": "litige_assurantiel",
        "type_garantie": "PE",
        "blocage_principal": "contractuel",
        "pattern_type": "blocage",
        "description": "Dans les refus d'assurance emprunteur, les exclusions ou seuils contractuels sont souvent plus determinants que le seul diagnostic medical. Le blocage reside frequemment dans la qualification juridique de l'etat de sante au regard des clauses specifiques du contrat.",
        "niveau_confiance": "eleve",
        "tags": ["assurance_emprunteur", "pe", "exclusion", "seuil_contractuel"],
    },
    {
        "categorie_dossier": "contestation_taux_ipp",
        "blocage_principal": "medico_evaluatif",
        "pattern_type": "blocage",
        "description": "La sous-evaluation du taux d'IPP resulte frequemment d'un defaut de traduction fonctionnelle : les sequelles sont decrites medicalement mais leur impact concret sur les actes de la vie quotidienne et professionnelle n'est pas suffisamment documente.",
        "niveau_confiance": "eleve",
        "tags": ["ipp", "sous_evaluation", "traduction_fonctionnelle"],
    },
    # --- VIGILANCES ---
    {
        "categorie_dossier": "accident_travail",
        "pattern_type": "vigilance",
        "description": "Verifier si le blocage est de nature probatoire (preuve insuffisante), contractuelle (definition non remplie) ou medico-evaluative (expertise defavorable). Le levier strategique differe radicalement selon la nature du blocage.",
        "niveau_confiance": "eleve",
        "tags": ["at", "diagnostic_blocage", "strategie"],
    },
    {
        "categorie_dossier": "litige_assurantiel",
        "pattern_type": "vigilance",
        "description": "Verifier si la piece medicale principale decrit reellement les limitations fonctionnelles utiles a la garantie invoquee. Un certificat medical qui liste des pathologies sans decrire leurs consequences fonctionnelles concretes est insuffisant pour activer la garantie.",
        "niveau_confiance": "eleve",
        "tags": ["assurance", "piece_medicale", "limitations_fonctionnelles"],
    },
    {
        "categorie_dossier": "maladie_professionnelle",
        "pattern_type": "vigilance",
        "description": "La chronologie du dossier est souvent sous-exploitee. Les dates cles (debut d'exposition, premier symptome, premiere consultation, declaration, consolidation) constituent des elements strategiques determinants pour etablir le lien de causalite.",
        "niveau_confiance": "eleve",
        "tags": ["mp", "chronologie", "causalite", "dates_cles"],
    },
    {
        "categorie_dossier": "contestation_taux_ipp",
        "pattern_type": "vigilance",
        "description": "L'incidence professionnelle est frequemment omise ou sous-evaluee dans les expertises. Elle peut representer jusqu'a un doublement du taux d'IPP lorsque les sequelles impactent directement la capacite a exercer le metier habituel.",
        "niveau_confiance": "eleve",
        "tags": ["ipp", "incidence_professionnelle", "doublement_taux"],
    },
    # --- LEVIERS ---
    {
        "categorie_dossier": "maladie_professionnelle",
        "pattern_type": "levier",
        "description": "Mieux traduire l'impact concret du trouble sur l'activite professionnelle reelle : decrire les gestes impossibles, les postures interdites, les taches abandonnees, plutot que de rester sur un diagnostic medical abstrait.",
        "niveau_confiance": "eleve",
        "tags": ["mp", "traduction_fonctionnelle", "impact_concret"],
    },
    {
        "categorie_dossier": "litige_assurantiel",
        "pattern_type": "levier",
        "description": "Isoler les contradictions entre les pieces medicales et la logique contractuelle opposee par l'assureur. Une contradiction explicite entre le motif de refus et les elements medicaux constitue un levier majeur de contestation.",
        "niveau_confiance": "eleve",
        "tags": ["assurance", "contradiction", "refus", "contestation"],
    },
    {
        "categorie_dossier": "accident_travail",
        "pattern_type": "levier",
        "description": "La formulation administrative initiale de l'accident conditionne souvent toute la suite du dossier. Verifier que la declaration reflete fidelement les circonstances reelles et le mecanisme lesionnel, avant toute contestation ulterieure.",
        "niveau_confiance": "eleve",
        "tags": ["at", "declaration", "formulation", "circonstances"],
    },
    # --- ERREURS FREQUENTES ---
    {
        "categorie_dossier": "contestation_taux_ipp",
        "pattern_type": "erreur_frequente",
        "description": "Contester le taux d'IPP sans avoir prealablement reuni un certificat medical detaille decrivant les limitations fonctionnelles, le retentissement professionnel et l'impact sur la vie quotidienne. La simple mention du diagnostic est insuffisante.",
        "niveau_confiance": "eleve",
        "tags": ["ipp", "certificat_medical", "erreur", "preparation"],
    },
    {
        "categorie_dossier": "litige_assurantiel",
        "pattern_type": "erreur_frequente",
        "description": "Argumenter sur le seul terrain medical alors que le blocage est de nature contractuelle. Le refus d'une garantie IPT n'est pas toujours un desaccord medical — c'est souvent un probleme de qualification au regard de la definition contractuelle.",
        "niveau_confiance": "eleve",
        "tags": ["assurance", "erreur", "terrain_medical_vs_contractuel"],
    },
    # --- PIECES MANQUANTES ---
    {
        "categorie_dossier": "maladie_professionnelle",
        "pattern_type": "piece_manquante",
        "description": "L'attestation detaillee de l'employeur ou du medecin du travail decrivant les gestes, postures et contraintes professionnels reels est frequemment absente des dossiers de MP. Cette piece est pourtant determinante pour etablir le lien professionnel.",
        "niveau_confiance": "eleve",
        "tags": ["mp", "attestation", "employeur", "medecin_travail"],
    },
]


# =============================================================================
# PACK PATTERNS MDPH PREMIUM V1
# =============================================================================
# Patterns chirurgicaux, sobres, credibles, non reidentifiables.
# Couvrent : AAH, RQTH, PCH, CMI, orientation, refus/silence MDPH.
# Axes : blocage, levier, vigilance, piece_manquante, erreur_frequente.
# Chaque pattern est autonome, exploitable, et immediatement utile.
# =============================================================================

SEED_PATTERNS_MDPH = [
    # ===================== BLOCAGES (7) =====================
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "aah_rsdae",
        "blocage_principal": "probatoire",
        "pattern_type": "blocage",
        "description": "Un refus d'AAH avec taux evalue entre 50 et 79 % repose frequemment sur une restriction substantielle et durable d'acces a l'emploi (RSDAE) insuffisamment objectivee. Le dossier decrit la pathologie mais ne traduit pas concretement en quoi elle empeche ou limite durablement l'acces a un emploi.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "aah", "rsdae", "probatoire", "taux_50_79", "emploi"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "aah_taux_80",
        "blocage_principal": "medical",
        "pattern_type": "blocage",
        "description": "Ce type de refus survient lorsque le certificat medical, bien que decrivant une pathologie lourde, reste trop sommaire sur le retentissement fonctionnel reel. L'equipe pluridisciplinaire evalue le taux selon les consequences concretes, pas selon la gravite du diagnostic seul.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "aah", "taux_80", "certificat_medical", "retentissement"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "pch_aides",
        "blocage_principal": "traduction_fonctionnelle",
        "pattern_type": "blocage",
        "description": "Dans les demandes de PCH, le retentissement sur les actes essentiels de la vie quotidienne est souvent evoque de maniere trop generale. Les besoins en aide humaine, technique ou d'amenagement doivent etre detailles acte par acte : toilette, habillage, repas, deplacements, gestion administrative.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "pch", "aide_humaine", "actes_essentiels", "traduction_fonctionnelle"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "rqth_emploi",
        "blocage_principal": "qualification",
        "pattern_type": "blocage",
        "description": "Ce type de dossier RQTH est souvent fragilise lorsque les limitations concretes au poste de travail ne sont pas decrites avec precision. Un diagnostic seul ne suffit pas : il faut documenter les gestes impossibles, les postures interdites, les amenagements necessaires et la fatigabilite reelle en situation professionnelle.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "rqth", "emploi", "qualification", "poste_travail", "amenagement"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "cmi_mobilite",
        "blocage_principal": "probatoire",
        "pattern_type": "blocage",
        "description": "Les demandes de CMI sont frequemment rejetees lorsque les difficultes de deplacement ou de station debout prolongee sont decrites de maniere trop vague. Un ecart entre les douleurs alleguees et les elements fonctionnels objectifs constitue un motif recurrent de refus.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "cmi", "mobilite", "station_debout", "probatoire"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "refus_mdph",
        "blocage_principal": "traduction_fonctionnelle",
        "pattern_type": "blocage",
        "description": "Un refus MDPH repose souvent moins sur un desaccord medical que sur un defaut de traduction fonctionnelle. Le dossier peut contenir un diagnostic serieux mais echouer a documenter son impact concret sur la vie quotidienne, l'autonomie et la capacite de travail.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "refus", "traduction_fonctionnelle", "retentissement", "quotidien"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "maladie_invalidante",
        "blocage_principal": "probatoire",
        "pattern_type": "blocage",
        "description": "Pour les maladies invalidantes a expression fluctuante (fatigue chronique, fibromyalgie, Crohn, sclerose en plaques), le blocage porte frequemment sur l'absence de documentation des periodes de crise. Un dossier qui ne decrit que l'etat stable sous-evalue mecaniquement le retentissement reel.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "maladie_invalidante", "fluctuante", "crises", "probatoire", "handicap_invisible"],
    },
    # ===================== VIGILANCES (6) =====================
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "vigilance",
        "description": "Il est essentiel de distinguer un refus MDPH de nature administrative (dossier incomplet, formulaire manquant, certificat perime) d'un refus de nature fonctionnelle (retentissement juge insuffisant). Le levier strategique differe radicalement selon la nature du refus.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "refus", "administratif", "fonctionnel", "diagnostic_blocage"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "vigilance",
        "description": "Le projet de vie est un element determinant de l'evaluation MDPH. Un projet de vie trop court, trop vague ou redige sans ancrage concret dans le quotidien reel expose a une sous-evaluation du taux d'incapacite et a un rejet de certaines prestations.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "projet_de_vie", "evaluation", "quotidien", "sous_evaluation"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "vigilance",
        "description": "Un certificat medical redige par un medecin generaliste non familier de la pathologie en cause peut fragiliser le dossier. Pour les pathologies specialisees, un certificat du specialiste traitant (neurologue, psychiatre, rhumatologue) apporte une credibilite nettement superieure.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "certificat_medical", "generaliste", "specialiste", "credibilite"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "vigilance",
        "description": "Le silence de la MDPH au-dela de 4 mois vaut rejet implicite, contrairement au regime general ou le silence peut valoir acceptation. Ce piege procedural est frequemment ignore et peut entrainer une perte de delai pour exercer le recours administratif prealable obligatoire (RAPO).",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "silence", "rejet", "delai", "rapo", "procedure"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "vigilance",
        "description": "Depuis le 1er janvier 2019, le recours administratif prealable obligatoire (RAPO) est un passage impose avant tout recours contentieux devant le tribunal judiciaire. Saisir directement le tribunal sans RAPO prealable entraine l'irrecevabilite du recours.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "rapo", "contentieux", "irrecevabilite", "recours"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "aah_rsdae",
        "pattern_type": "vigilance",
        "description": "Pour l'AAH avec taux entre 50 et 79 %, la notion de RSDAE est evaluee au regard de la capacite reelle d'acces a l'emploi, pas au regard de la volonte subjective de travailler. Le dossier doit documenter les obstacles objectifs et durables, pas seulement l'absence actuelle d'emploi.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "aah", "rsdae", "emploi", "capacite_reelle", "objectivation"],
    },
    # ===================== LEVIERS (5) =====================
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "aah_rsdae",
        "pattern_type": "levier",
        "description": "Un levier frequent pour objectiver la RSDAE consiste a produire une attestation detaillee du medecin du travail ou de France Travail decrivant les limitations concretes observees en situation professionnelle et les postes incompatibles avec la pathologie.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "aah", "rsdae", "levier", "medecin_travail", "france_travail"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "maladie_invalidante",
        "pattern_type": "levier",
        "description": "Pour les maladies a expression fluctuante, la tenue d'un journal de crises sur 3 a 6 mois avant le depot constitue un element probatoire precieux. Y documenter la frequence, la duree, l'intensite des crises et leur impact sur les activites quotidiennes et professionnelles.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "maladie_invalidante", "journal_crises", "fluctuante", "levier"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "pch_aides",
        "pattern_type": "levier",
        "description": "Dans les demandes de PCH, joindre des temoignages detailles d'aidants familiaux ou de proches decrivant les actes quotidiens qui necessitent une aide concrete constitue un appui significatif, surtout lorsque le certificat medical seul ne reflte pas l'ampleur des besoins.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "pch", "temoignage", "aidant", "actes_quotidiens", "levier"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "rqth_emploi",
        "pattern_type": "levier",
        "description": "Pour une demande RQTH, une attestation du medecin du travail ou de l'employeur decrivant les amenagements deja mis en place ou les restrictions d'aptitude prononcees constitue un levier determinant pour objectiver les limitations professionnelles.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "rqth", "medecin_travail", "employeur", "amenagement", "levier"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "levier",
        "description": "Mieux traduire le retentissement fonctionnel reel dans le projet de vie : decrire une journee type avec les difficultes concretes rencontrees a chaque etape (lever, hygiene, repas, deplacements, travail, vie sociale, fatigue en fin de journee) plutot que de rester sur un recit clinique.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "projet_de_vie", "retentissement", "journee_type", "levier", "traduction_fonctionnelle"],
    },
    # ===================== ERREURS FREQUENTES (4) =====================
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "erreur_frequente",
        "description": "Redeposer un dossier MDPH strictement identique apres un refus, sans apporter de nouvelles pieces medicales, de bilans complementaires ou d'elements fonctionnels supplementaires. Ce renouvellement a l'identique aboutit presque systematiquement au meme refus.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "erreur", "renouvellement", "refus", "pieces_identiques"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "aah_rsdae",
        "pattern_type": "erreur_frequente",
        "description": "Ne pas demander la RQTH simultanement a l'AAH alors que les deux droits peuvent etre attribues dans le meme dossier. La RQTH ouvre des aides complementaires a l'insertion professionnelle et peut renforcer la credibilite de la demande d'AAH.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "aah", "rqth", "erreur", "cumul_droits"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "erreur_frequente",
        "description": "Confondre la gravite du diagnostic avec le retentissement fonctionnel. L'evaluation MDPH porte sur les consequences concretes de la pathologie sur la vie quotidienne et l'emploi, pas sur la severite intrinsèque du diagnostic medical. Un diagnostic grave avec faible retentissement documente aboutit a un taux faible.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "erreur", "diagnostic_vs_retentissement", "evaluation", "taux"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "erreur_frequente",
        "description": "Negliger le projet de vie ou le remplir en quelques lignes generiques. Ce document est lu par l'equipe pluridisciplinaire comme un element d'evaluation a part entiere. Son absence ou sa pauvrete prive le dossier d'un ancrage concret indispensable.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "erreur", "projet_de_vie", "negligence", "equipe_pluridisciplinaire"],
    },
    # ===================== PIECES MANQUANTES (4) =====================
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "piece_manquante",
        "description": "Le projet de vie detaille decrivant une journee type est frequemment absent ou insuffisant. Ce document doit traduire concretement les difficultes rencontrees a chaque moment de la journee : lever, hygiene, habillage, repas, deplacements, activites, fatigue, sommeil.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "piece_manquante", "projet_de_vie", "journee_type", "retentissement"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "piece_manquante",
        "description": "Un bilan fonctionnel specialise (ergotherapique, neuropsychologique, ou fonctionnel respiratoire) est souvent absent alors qu'il constitue l'element le plus objectif pour documenter le retentissement reel du handicap sur les capacites de la personne.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "piece_manquante", "bilan_fonctionnel", "ergotherapie", "neuropsychologie"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "type_sinistre": "rqth_emploi",
        "pattern_type": "piece_manquante",
        "description": "L'attestation detaillee du medecin du travail ou de l'employeur decrivant les restrictions d'aptitude, les amenagements de poste deja tentes ou necessaires est frequemment absente des dossiers RQTH. Cette piece est pourtant determinante pour objectiver l'impact professionnel.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "rqth", "piece_manquante", "medecin_travail", "employeur", "restrictions"],
    },
    {
        "categorie_dossier": "demande_mdph",
        "pattern_type": "piece_manquante",
        "description": "L'historique consolide des hospitalisations, arrets de travail et periodes d'incapacite est rarement reuni dans le dossier MDPH alors qu'il permet de documenter objectivement la chronicite et la recurrence du handicap dans le temps.",
        "niveau_confiance": "eleve",
        "tags": ["mdph", "piece_manquante", "historique", "hospitalisations", "arrets", "chronicite"],
    },
]


async def seed_mdph_patterns(db_instance):
    """Injecte les patterns MDPH v1 si aucun pattern MDPH n'existe deja."""
    import uuid
    from datetime import datetime, timezone

    # Verifier s'il y a deja des patterns MDPH
    mdph_count = await db_instance.knowledge_patterns.count_documents(
        {"categorie_dossier": "demande_mdph", "source_type": "seed_mdph_v1"}
    )
    if mdph_count > 0:
        return {"status": "skipped", "reason": f"Pack MDPH v1 deja en base ({mdph_count} patterns)"}

    inserted = 0
    for seed in SEED_PATTERNS_MDPH:
        pattern = {
            "id": str(uuid.uuid4()),
            "categorie_dossier": seed.get("categorie_dossier", ""),
            "metier": seed.get("metier", ""),
            "type_sinistre": seed.get("type_sinistre", ""),
            "type_garantie": seed.get("type_garantie"),
            "blocage_principal": seed.get("blocage_principal", ""),
            "pattern_type": seed["pattern_type"],
            "description": seed["description"],
            "niveau_confiance": seed.get("niveau_confiance", "moyen"),
            "usage_autorise": True,
            "source_type": "seed_mdph_v1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "validated_by": "system_seed_mdph_v1",
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "tags": seed.get("tags", []),
        }
        await db_instance.knowledge_patterns.insert_one(pattern)
        inserted += 1

    return {"status": "seeded_mdph_v1", "count": inserted}


async def seed_knowledge_patterns(db_instance):
    """Injecte les patterns seed si la base est vide."""
    import uuid
    from datetime import datetime, timezone

    count = await db_instance.knowledge_patterns.count_documents({})
    if count > 0:
        return {"status": "skipped", "reason": f"Base non vide ({count} patterns existants)"}

    inserted = 0
    for seed in SEED_PATTERNS:
        pattern = {
            "id": str(uuid.uuid4()),
            "categorie_dossier": seed.get("categorie_dossier", ""),
            "metier": seed.get("metier", ""),
            "type_sinistre": seed.get("type_sinistre", ""),
            "type_garantie": seed.get("type_garantie"),
            "blocage_principal": seed.get("blocage_principal", ""),
            "pattern_type": seed["pattern_type"],
            "description": seed["description"],
            "niveau_confiance": seed.get("niveau_confiance", "moyen"),
            "usage_autorise": True,
            "source_type": "seed",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "validated_by": "system_seed",
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "tags": seed.get("tags", []),
        }
        await db_instance.knowledge_patterns.insert_one(pattern)
        inserted += 1

    return {"status": "seeded", "count": inserted}
