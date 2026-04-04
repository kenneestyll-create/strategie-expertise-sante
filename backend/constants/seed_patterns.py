"""
SEED PATTERNS — Base de demarrage pour knowledge_patterns
==========================================================
Patterns sobres, premium, credibles et utiles.
Pas de remplissage. Enseignements abstraits non identifiants.
A executer UNE FOIS pour initialiser la base.
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
