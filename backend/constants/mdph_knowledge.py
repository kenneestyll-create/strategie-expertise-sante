"""
BASE DE CONNAISSANCES — MDPH (Maison Departementale des Personnes Handicapees)
================================================================================
Sources :
- Code de l'Action Sociale et des Familles (CASF) : L.146-3 a L.146-13, L.241-1 a L.245-14
- Code de la Securite Sociale (CSS) : L.341-1 a L.341-16 (invalidite), L.821-1 a L.821-8 (AAH)
- Decrets et arretes en vigueur (2024-2026)
- Service-public.fr (references officielles)
- CNSA (Caisse Nationale de Solidarite pour l'Autonomie)

# =========================================================================
# PROPRIETE INTELLECTUELLE — ACTIF STRATEGIQUE SENSIBLE
# Strategie & Expertise Sante — Tous droits reserves.
# Ce fichier contient une base de connaissances metier proprietaire
# (structuration MDPH, logique AAH/PCH/RQTH, ciblage contextuel).
# Toute reproduction, extraction, reutilisation ou transmission sans
# autorisation ecrite est interdite.
#
# ZONE GELEE — MOTEUR IA V1 VALIDE
# Date de gel : 05/04/2026
# Protocole : Aucune modification sans ordre explicite du responsable.
#   Toute evolution future doit suivre le protocole IA_BASELINE_V1.md.
# =========================================================================

Structure :
- MDPH_GENERAL : presentation, missions, fonctionnement
- AAH_ALLOCATION : conditions, montants, procedures, cumul
- PCH_PRESTATION : conditions, aides, procedures
- RQTH_RECONNAISSANCE : conditions, avantages, procedures
- CMI_CARTE : types, conditions, procedures
- PENSION_INVALIDITE : categories, cumul AAH, articulation
- MALADIES_INVALIDANTES : definition, exemples, droits
- RECOURS_MDPH : voies de contestation
- MDPH_STRATEGY : points strategiques, erreurs frequentes
- get_mdph_context() : helper pour injection dans le prompt LLM
- detect_mdph_context() : detection automatique de contexte MDPH
Integre le 05/04/2026.
"""

# =============================================================================
# PRESENTATION GENERALE — MDPH
# =============================================================================

MDPH_GENERAL = {
    "definition": "La Maison Departementale des Personnes Handicapees (MDPH) est un guichet unique departmental cree par la loi du 11 fevrier 2005 pour l'egalite des droits et des chances. Elle accueille, informe, accompagne et conseille les personnes handicapees et leurs proches.",
    "missions": [
        "Accueil, information et accompagnement des personnes handicapees et de leurs familles",
        "Attribution des droits et prestations (AAH, PCH, RQTH, CMI, orientation)",
        "Evaluation des besoins par une equipe pluridisciplinaire (EP)",
        "Elaboration du Plan Personnalise de Compensation (PPC)",
        "Decisions prises par la Commission des Droits et de l'Autonomie des Personnes Handicapees (CDAPH)",
    ],
    "base_legale": {
        "loi_fondatrice": "Loi n°2005-102 du 11 fevrier 2005 pour l'egalite des droits et des chances, la participation et la citoyennete des personnes handicapees",
        "articles_casf": "Articles L.146-3 a L.146-13 du Code de l'Action Sociale et des Familles",
    },
    "equipe_pluridisciplinaire": {
        "composition": "Medecins, psychologues, ergotherapeutes, assistantes sociales, enseignants specialises, etc.",
        "role": "Evalue les besoins de compensation de la personne sur la base du formulaire de demande, du certificat medical, et de tout document complementaire (bilan fonctionnel, compte-rendu specialiste).",
        "outil": "Utilise le Guide d'Evaluation des besoins de compensation des personnes handicapees (GEVA).",
    },
    "cdaph": {
        "nom": "Commission des Droits et de l'Autonomie des Personnes Handicapees",
        "role": "Organe decisionnaire de la MDPH. Prend les decisions d'attribution des droits et prestations.",
        "composition": "Representants du departement, de l'Etat, des organismes de protection sociale, des associations de personnes handicapees, et des organisations syndicales.",
    },
    "formulaire": {
        "cerfa": "Cerfa n°15692*01 (formulaire unique de demande MDPH)",
        "certificat_medical": "Cerfa n°15695*01 (certificat medical de moins de 6 mois, sauf pathologie stabilisee : 12 mois)",
        "pieces_obligatoires": [
            "Formulaire Cerfa 15692*01 complete et signe",
            "Certificat medical Cerfa 15695*01 de moins de 6 mois",
            "Justificatif d'identite (CNI, passeport, titre de sejour)",
            "Justificatif de domicile de moins de 3 mois",
            "Photo d'identite (si demande de carte)",
        ],
        "pieces_recommandees": [
            "Bilans specialises (neuropsychologique, ergotherapique, ORL, ophtalmologique)",
            "Comptes-rendus d'hospitalisation",
            "Attestation employeur ou medecin du travail (si RQTH)",
            "Projet de vie detaille (element strategique majeur)",
        ],
    },
    "delais": {
        "instruction": "La MDPH dispose de 4 mois pour instruire la demande a compter de la reception du dossier complet.",
        "silence_vaut_rejet": "ATTENTION : contrairement a la CPAM, le silence de la MDPH au-dela de 4 mois vaut REJET implicite (Art. R.241-33 CASF). Le demandeur peut alors exercer un recours.",
        "renouvellement": "Deposer la demande de renouvellement 6 mois avant l'expiration des droits pour eviter toute rupture.",
    },
}

# =============================================================================
# AAH — ALLOCATION AUX ADULTES HANDICAPES
# =============================================================================

AAH_ALLOCATION = {
    "definition": "L'Allocation aux Adultes Handicapes (AAH) est une aide financiere destinee a assurer un minimum de ressources aux personnes en situation de handicap. Elle est financee par l'Etat et versee par la CAF ou la MSA.",
    "base_legale": "Articles L.821-1 a L.821-8 du Code de la Securite Sociale",
    "conditions": {
        "age": "Avoir au moins 20 ans (ou 16 ans si plus a charge des parents). Pas de limite d'age superieure depuis le 1er janvier 2017 pour les personnes dont le taux d'incapacite >= 80%.",
        "residence": "Resider en France de facon stable et reguliere (plus de 3 mois consecutifs sur le territoire).",
        "taux_incapacite": {
            "condition_principale": "Taux d'incapacite permanente >= 80% (AAH-1), OU",
            "condition_alternative": "Taux d'incapacite entre 50% et 79% (AAH-2) avec une restriction substantielle et durable pour l'acces a l'emploi (RSDAE), reconnue par la CDAPH.",
            "important": "Le taux d'incapacite est evalue par l'equipe pluridisciplinaire de la MDPH selon le guide-bareme (annexe 2-4 du CASF).",
        },
        "ressources": "Les ressources du demandeur (et de son conjoint) ne doivent pas depasser un plafond annuel fixe par decret.",
    },
    "montant": {
        "taux_plein": "1016,05 euros/mois (montant au 1er avril 2024, revalorisation annuelle)",
        "calcul": "AAH differentielle si le demandeur percoit d'autres revenus (salaire, pension, etc.). L'AAH complete le revenu jusqu'au plafond.",
        "complement": "Le complement de ressources (CR) a ete supprime au 1er decembre 2019 (maintien transitoire pour les beneficiaires anterieurs). La Majoration pour la Vie Autonome (MVA) reste active : 104,77 euros/mois sous conditions (logement independant, pas d'activite professionnelle).",
    },
    "duree": {
        "taux_sup_80": "Attribution possible a titre definitif (sans limitation de duree) depuis le 1er janvier 2019 pour les personnes dont le handicap n'est pas susceptible d'evolution favorable.",
        "taux_50_79": "Attribution pour 1 a 5 ans, renouvelable. La RSDAE est reexaminee a chaque renouvellement.",
    },
    "cumul": {
        "avec_salaire": "Possible. Les revenus d'activite sont partiellement cumules avec l'AAH selon un mecanisme de decote progressive (abattement de 80% sur les premiers 530 euros, puis 40% au-dela).",
        "avec_pension_invalidite": {
            "principe": "Depuis le 1er decembre 2019, le cumul AAH + pension d'invalidite est possible. L'AAH est versee en complement differentiel si la pension est inferieure au montant de l'AAH.",
            "calcul": "AAH versee = montant AAH a taux plein - montant de la pension d'invalidite.",
            "important": "La personne doit faire valoir ses droits a pension d'invalidite en priorite (subsidiarite de l'AAH). Si la pension est superieure a l'AAH, l'AAH n'est pas versee.",
        },
        "avec_rente_at_mp": "Cumul possible dans les memes conditions que la pension d'invalidite. L'AAH est differentielle.",
        "avec_are": "Cumul possible avec l'ARE (Allocation de Retour a l'Emploi) selon les regles de Pole Emploi / France Travail.",
    },
    "deconjugalisation": {
        "reforme": "Depuis le 1er octobre 2023, les revenus du conjoint ne sont plus pris en compte pour le calcul de l'AAH (deconjugalisation). Seuls les revenus propres du demandeur sont consideres.",
        "impact": "Reforme majeure qui a permis a environ 120 000 personnes de voir leur AAH augmenter ou d'y acceder.",
    },
}

# =============================================================================
# PCH — PRESTATION DE COMPENSATION DU HANDICAP
# =============================================================================

PCH_PRESTATION = {
    "definition": "La Prestation de Compensation du Handicap (PCH) est une aide personnalisee destinee a financer les besoins lies au handicap. Elle est attribuee par la CDAPH et financee par le departement.",
    "base_legale": "Articles L.245-1 a L.245-14 du Code de l'Action Sociale et des Familles",
    "conditions": {
        "age": "Avoir moins de 60 ans lors de la premiere demande (ou moins de 75 ans si le handicap etait reconnu avant 60 ans). Pas de limite d'age si la personne exerce encore une activite professionnelle.",
        "residence": "Resider en France de facon stable et reguliere.",
        "handicap": "Presenter une difficulte absolue pour la realisation d'une activite essentielle, OU une difficulte grave pour au moins deux activites essentielles (parmi : mobilite, entretien personnel, communication, taches et exigences generales, relations interpersonnelles).",
        "pas_de_condition_ressources": "La PCH n'est pas soumise a condition de ressources pour son attribution. Les ressources influencent uniquement le taux de prise en charge (100% si revenus <= 29 061 euros/an, sinon 80%).",
    },
    "elements_couverts": {
        "element_1": {
            "nom": "Aides humaines",
            "objet": "Financement d'un aidant familial, d'un emploi direct, ou d'un service prestataire pour les actes essentiels, la surveillance, les frais supplementaires lies a l'activite professionnelle.",
            "plafond": "Jusqu'a 17h/jour d'aide humaine (plus si soins specifiques). Tarifs : emploi direct ~14,73 euros/h, aidant familial ~4,41 euros/h (2024).",
        },
        "element_2": {
            "nom": "Aides techniques",
            "objet": "Financement d'equipements (fauteuil roulant, protheses auditives, logiciels specifiques, etc.).",
            "plafond": "13 200 euros sur 3 ans.",
        },
        "element_3": {
            "nom": "Amenagement du logement, du vehicule, surcoûts transport",
            "objet": "Travaux d'adaptation du domicile, amenagement du vehicule, surcoûts lies aux transports.",
            "plafond_logement": "10 000 euros sur 10 ans",
            "plafond_vehicule": "5 000 euros sur 5 ans",
            "plafond_transport": "12 000 euros sur 5 ans",
        },
        "element_4": {
            "nom": "Charges specifiques ou exceptionnelles",
            "objet": "Depenses permanentes et previsibles (specifiques) ou ponctuelles (exceptionnelles) liees au handicap.",
            "plafond_specifiques": "100 euros/mois",
            "plafond_exceptionnelles": "6 000 euros sur 3 ans",
        },
        "element_5": {
            "nom": "Aide animaliere",
            "objet": "Financement de l'entretien d'un animal d'assistance (chien-guide, chien d'assistance).",
            "plafond": "50 euros/mois",
        },
    },
    "duree": {
        "aides_humaines": "Jusqu'a 10 ans (ou a vie si handicap non susceptible d'evolution favorable, depuis 2022).",
        "autres_elements": "3 a 10 ans selon l'element.",
    },
    "cumul": {
        "avec_aah": "Cumul possible. La PCH et l'AAH couvrent des besoins differents (compensation vs. minimum de ressources).",
        "avec_apa": "NON cumulable avec l'APA (Allocation Personnalisee d'Autonomie). La personne doit choisir.",
        "avec_actp": "NON cumulable avec l'ACTP (Allocation Compensatrice pour Tierce Personne). Droit d'option a chaque renouvellement.",
    },
}

# =============================================================================
# RQTH — RECONNAISSANCE QUALITE TRAVAILLEUR HANDICAPE
# =============================================================================

RQTH_RECONNAISSANCE = {
    "definition": "La Reconnaissance de la Qualite de Travailleur Handicape (RQTH) est une decision administrative attribuee par la CDAPH permettant a une personne dont les possibilites d'obtenir ou de conserver un emploi sont reduites du fait de son handicap de beneficier de mesures specifiques.",
    "base_legale": "Articles L.5213-1 a L.5213-6-2 du Code du Travail",
    "conditions": {
        "definition_th": "Est considere comme travailleur handicape toute personne dont les possibilites d'obtenir ou de conserver un emploi sont effectivement reduites par suite de l'alteration d'une ou plusieurs fonctions physique, sensorielle, mentale ou psychique (Art. L.5213-1 CT).",
        "age": "A partir de 16 ans.",
        "pas_de_taux_minimum": "Il n'y a pas de taux d'incapacite minimum requis pour obtenir la RQTH. L'evaluation porte sur l'impact du handicap sur les capacites professionnelles.",
    },
    "avantages": {
        "emploi": [
            "Acces a l'obligation d'emploi des travailleurs handicapes (OETH) : les entreprises de 20 salaries et plus doivent employer au minimum 6% de travailleurs handicapes.",
            "Acces aux aides de l'Agefiph (secteur prive) ou du FIPHFP (secteur public) : amenagements de poste, formations, primes a l'embauche.",
            "Priorite pour les contrats aides et les parcours d'insertion.",
            "Amenagement d'horaires et de poste (obligation de l'employeur, Art. L.5213-6 CT).",
        ],
        "formation": [
            "Acces aux stages de reeducation professionnelle.",
            "Contrat de reeducation professionnelle en entreprise.",
            "Formations specifiques en centre de readaptation professionnelle (CRP).",
        ],
        "protection": [
            "Doublement de la duree du preavis en cas de licenciement (dans la limite de 3 mois, Art. L.5213-9 CT).",
            "Surveillance medicale renforcee par le medecin du travail.",
        ],
    },
    "duree": "Attribuee pour 1 a 10 ans, ou sans limitation de duree si le handicap est irreversible (depuis 2020).",
    "attribution_automatique": "Les titulaires d'une pension d'invalidite, d'une rente AT/MP avec un taux d'incapacite >= 10%, ou de la carte mobilite inclusion mention invalidite beneficient automatiquement de l'OETH sans RQTH formelle (Art. L.5212-13 CT).",
}

# =============================================================================
# CMI — CARTE MOBILITE INCLUSION
# =============================================================================

CMI_CARTE = {
    "definition": "La Carte Mobilite Inclusion (CMI) remplace depuis le 1er janvier 2017 les anciennes cartes de priorite, d'invalidite et de stationnement. Elle est attribuee par la CDAPH (sauf CMI stationnement pour les invalides de guerre).",
    "base_legale": "Articles L.241-3 a L.241-3-2 du Code de l'Action Sociale et des Familles",
    "types": {
        "invalidite": {
            "condition": "Taux d'incapacite >= 80%, OU titulaire d'une pension d'invalidite classee en 3e categorie.",
            "avantages": [
                "Priorite d'acces aux places assises dans les transports en commun, espaces d'attente, etablissements publics.",
                "Priorite dans les files d'attente.",
                "Avantages fiscaux : demi-part supplementaire pour l'impot sur le revenu.",
                "Reductions tarifaires dans les transports.",
            ],
        },
        "priorite": {
            "condition": "Taux d'incapacite < 80% mais station debout penible reconnue par la CDAPH.",
            "avantages": ["Priorite d'acces aux places assises et dans les files d'attente."],
        },
        "stationnement": {
            "condition": "Atteinte d'une ou plusieurs fonctions (mobilite reduite, besoin d'accompagnement par tierce personne).",
            "avantages": [
                "Utilisation gratuite et sans limitation de duree de toutes les places de stationnement ouvertes au public.",
                "Valable dans toute l'UE.",
            ],
        },
    },
    "duree": "1 a 20 ans, ou definitive si handicap irreversible.",
}

# =============================================================================
# PENSION D'INVALIDITE — ARTICULATION AVEC MDPH
# =============================================================================

PENSION_INVALIDITE = {
    "definition": "La pension d'invalidite est versee par l'Assurance Maladie (CPAM, MSA, ou regime special) a l'assure dont la capacite de travail ou de gain est reduite d'au moins 2/3 suite a un accident ou une maladie d'origine NON professionnelle.",
    "base_legale": "Articles L.341-1 a L.341-16 du Code de la Securite Sociale",
    "conditions": [
        "Avoir moins de 62 ans (age d'ouverture de droit a la retraite).",
        "Capacite de travail ou de gain reduite d'au moins 2/3.",
        "Etre immatricule depuis au moins 12 mois et avoir cotise sur un salaire minimum.",
    ],
    "categories": {
        "categorie_1": {
            "condition": "Invalide capable d'exercer une activite remuneree.",
            "montant": "30% du salaire annuel moyen des 10 meilleures annees.",
        },
        "categorie_2": {
            "condition": "Invalide absolument incapable d'exercer une profession quelconque.",
            "montant": "50% du salaire annuel moyen des 10 meilleures annees.",
        },
        "categorie_3": {
            "condition": "Invalide necessite d'une tierce personne pour les actes de la vie courante.",
            "montant": "50% du salaire annuel moyen + majoration tierce personne (MTP, environ 1 231 euros/mois en 2024).",
        },
    },
    "cumul_aah": {
        "principe": "L'AAH est subsidiaire : la personne doit faire valoir ses droits a pension d'invalidite en priorite.",
        "cumul_possible": "Si la pension d'invalidite est inferieure au montant de l'AAH a taux plein, l'AAH differentielle est versee en complement.",
        "calcul": "AAH versee = AAH taux plein - pension d'invalidite nette.",
        "cas_pratique": "Un invalide de categorie 1 percevant 400 euros/mois de pension peut recevoir une AAH differentielle de 1016,05 - 400 = 616,05 euros/mois (sous reserve des plafonds de ressources).",
    },
    "cumul_rente_at_mp": {
        "principe": "La rente AT/MP et la pension d'invalidite ne sont PAS cumulables pour la meme pathologie. Mais elles peuvent l'etre si elles concernent des pathologies differentes.",
        "articulation_aah": "La rente AT/MP est traitee comme un avantage vieillesse/invalidite pour le calcul de l'AAH differentielle.",
    },
    "retraite": "A 62 ans, la pension d'invalidite est automatiquement convertie en pension de retraite pour inaptitude (sauf opposition de l'assure).",
}

# =============================================================================
# MALADIES INVALIDANTES
# =============================================================================

MALADIES_INVALIDANTES = {
    "definition": "Les maladies invalidantes sont des maladies chroniques qui, bien que souvent invisibles, entrainent des limitations fonctionnelles significatives et durables. Elles donnent droit a une reconnaissance MDPH si elles impactent la vie quotidienne ou professionnelle.",
    "exemples_reconnus": [
        "Sclerose en plaques (SEP)",
        "Polyarthrite rhumatoide et spondylarthrites",
        "Maladies inflammatoires chroniques de l'intestin (Crohn, RCH)",
        "Insuffisance cardiaque et respiratoire chronique",
        "Diabete avec complications severes",
        "Epilepsie pharmacoresistante",
        "Fibromyalgie (reconnaissance variable, argumenter l'impact fonctionnel)",
        "Syndrome de fatigue chronique (idem)",
        "Cancers en cours de traitement ou avec sequelles",
        "Troubles bipolaires, depression severe recurrente, troubles anxieux severes",
        "Maladie de Parkinson",
        "Lupus erythemateux systemique",
        "VIH avec traitements lourds ou effets secondaires invalidants",
        "Endometriose severe (reconnaissance croissante depuis 2022)",
    ],
    "strategie_dossier": {
        "cle_1": "Le taux d'incapacite n'est PAS base sur le diagnostic mais sur les RETENTISSEMENTS FONCTIONNELS. Un dossier MDPH pour maladie invalidante doit detailler les consequences concretes sur la vie quotidienne, pas seulement le diagnostic.",
        "cle_2": "Joindre un certificat medical tres detaille (Cerfa 15695*01) avec description precise des limitations : douleur, fatigue, impact sur la mobilite, l'hygiene, la concentration, les relations sociales.",
        "cle_3": "Le projet de vie (partie 'Expression des attentes et besoins') est DETERMINANT. Y decrire une journee type avec les difficultes concretes.",
        "cle_4": "Joindre tous les bilans specialises : bilan neuropsychologique, bilan fonctionnel, test d'effort, bilan douleur, etc.",
        "cle_5": "Pour les maladies fluctuantes (SEP, Crohn, fibromyalgie), decrire les periodes de crise et leur frequence, pas seulement l'etat stable.",
    },
}

# =============================================================================
# VOIES DE RECOURS MDPH
# =============================================================================

RECOURS_MDPH = {
    "raad": {
        "nom": "Recours Administratif Prealable Obligatoire (RAPO) aupres de la MDPH",
        "description": "Depuis le 1er janvier 2019, le RAPO est OBLIGATOIRE avant tout recours contentieux. Il doit etre exerce dans les 2 mois suivant la notification de la decision CDAPH.",
        "forme": "Lettre recommandee avec AR adressee au directeur de la MDPH, motivee et accompagnee de la decision contestee et de pieces justificatives complementaires.",
        "delai": "2 mois a compter de la notification de la decision CDAPH.",
        "instruction": "La MDPH dispose de 2 mois pour repondre. Silence de 2 mois = rejet implicite.",
        "astuce": "Profiter du RAPO pour apporter des pieces complementaires (bilans recents, certificats detailles) qui n'etaient pas dans le dossier initial.",
    },
    "contentieux": {
        "nom": "Recours contentieux devant le Tribunal judiciaire (pole social)",
        "condition": "Uniquement apres rejet (explicite ou implicite) du RAPO.",
        "delai": "2 mois a compter du rejet du RAPO.",
        "competence": "Tribunal judiciaire (pole social) du lieu de domicile du demandeur.",
        "procedure": "Saisine par requete (formulaire Cerfa) ou lettre recommandee au greffe. Procedure gratuite, sans avocat obligatoire.",
        "expertise": "Le juge peut ordonner une expertise medicale judiciaire (consultant designe sur la liste des experts agrees).",
        "important": "Se faire accompagner par une association (APF France Handicap, FNATH, etc.) ou un avocat specialise augmente significativement les chances de succes.",
    },
    "mediation": {
        "nom": "Conciliation / Mediation",
        "description": "Possibilite de demander une conciliation aupres du tribunal avant l'audience. Certaines MDPH proposent aussi une mediation interne.",
    },
    "erreurs_frequentes_recours": [
        "Ne pas exercer le RAPO et saisir directement le tribunal (irrecevable depuis 2019).",
        "Depasser le delai de 2 mois pour le RAPO (forclusion).",
        "Ne pas motiver le recours et se contenter de dire 'je ne suis pas d'accord'.",
        "Ne pas apporter de nouvelles pieces medicales avec le RAPO.",
        "Ignorer la possibilite de demander une expertise medicale au tribunal.",
    ],
}

# =============================================================================
# ORIENTATION ET INSERTION PROFESSIONNELLE
# =============================================================================

ORIENTATION_PROFESSIONNELLE = {
    "milieu_ordinaire": {
        "definition": "Travail en entreprise classique, avec ou sans amenagement de poste.",
        "acteurs": [
            "France Travail (ex-Pole Emploi) — Cap Emploi pour l'accompagnement specialise",
            "Agefiph (secteur prive) — aides financieres, formations, amenagements",
            "FIPHFP (secteur public) — equivalent Agefiph pour la fonction publique",
        ],
    },
    "milieu_protege": {
        "definition": "Travail en ESAT (Etablissement et Service d'Aide par le Travail) pour les personnes dont la capacite de travail est insuffisante pour le milieu ordinaire.",
        "conditions": "Orientation par la CDAPH. Capacite de travail inferieure a 1/3 de la normale.",
        "remuneration": "Remuneration garantie (entre 55% et 110% du SMIC), cumulable avec l'AAH.",
    },
    "formation": {
        "crp": "Centres de Reeducation Professionnelle — formation qualifiante longue (10 a 30 mois) avec statut de stagiaire de la formation professionnelle.",
        "ueros": "Unites d'Evaluation, de Reentrainement et d'Orientation Sociale et/ou professionnelle — evaluation des capacites residuelles apres un accident ou une maladie.",
    },
}

# =============================================================================
# POINTS STRATEGIQUES — TRANSVERSAUX MDPH
# =============================================================================

MDPH_STRATEGY = {
    "points_cles": [
        "Le projet de vie est l'element strategique MAJEUR du dossier MDPH. Il doit etre detaille, concret et decrire les impacts du handicap au quotidien.",
        "Le certificat medical (Cerfa 15695*01) doit etre rempli par un specialiste du handicap concerne, pas par un generaliste quand c'est possible.",
        "Le taux d'incapacite est evalue selon le guide-bareme (annexe 2-4 CASF) : il mesure les RETENTISSEMENTS FONCTIONNELS, pas la gravite du diagnostic.",
        "La MDPH peut convoquer le demandeur pour un entretien. S'y preparer avec tous les documents originaux.",
        "Le silence de la MDPH au-dela de 4 mois vaut REJET (contrairement a la CPAM ou le silence peut valoir acceptation).",
        "Le RAPO (recours administratif) est OBLIGATOIRE avant le contentieux depuis le 1er janvier 2019.",
        "La deconjugalisation de l'AAH est effective depuis le 1er octobre 2023 : les revenus du conjoint ne comptent plus.",
    ],
    "erreurs_frequentes": [
        "Deposer un dossier incomplet (certificat medical manquant ou perime, pas de projet de vie).",
        "Rediger un projet de vie trop vague ou trop court (1 ou 2 lignes).",
        "Confier le certificat medical a un generaliste non familier de la pathologie.",
        "Ne pas joindre de bilans specialises complementaires (neuropsycho, ergo, etc.).",
        "Ne pas renouveler les droits 6 mois avant l'echeance (rupture de droits).",
        "Ignorer le RAPO et saisir directement le tribunal (irrecevable).",
        "Ne pas demander la RQTH en meme temps que l'AAH (alors que la RQTH facilite l'insertion).",
        "Sous-estimer l'importance des maladies invalidantes 'invisibles' dans le dossier.",
        "Ne pas mentionner les consequences sur l'emploi dans le projet de vie (essentiel pour la RSDAE si taux 50-79%).",
    ],
    "conseils_premium": [
        "Faire rediger le projet de vie par un professionnel (assistante sociale, association) pour optimiser la presentation.",
        "Joindre des temoignages d'aidants ou de proches pour etayer les difficultes quotidiennes.",
        "En cas de maladie fluctuante, tenir un journal des crises sur 3-6 mois avant le depot du dossier.",
        "Demander une visite a domicile de l'equipe pluridisciplinaire si la situation le justifie.",
        "En cas de refus, ne pas redéposer un dossier identique : apporter de nouvelles pieces et argumenter les points faibles identifies.",
    ],
    "articles_reference": {
        "L.821-1 CSS": "Conditions d'attribution de l'AAH.",
        "L.821-2 CSS": "AAH et RSDAE (taux 50-79%).",
        "L.245-1 CASF": "Conditions d'attribution de la PCH.",
        "L.241-3 CASF": "Carte Mobilite Inclusion.",
        "L.5213-1 CT": "Definition du travailleur handicape.",
        "L.5213-6 CT": "Obligation d'amenagement de poste.",
        "L.341-1 CSS": "Pension d'invalidite — conditions.",
        "R.241-33 CASF": "Delai d'instruction MDPH — silence vaut rejet.",
        "L.146-9 CASF": "Missions de la MDPH.",
    },
}


# =============================================================================
# HELPER : get_mdph_context()
# =============================================================================

def get_mdph_context(demande_type=None):
    """
    Retourne le contexte MDPH injectable dans le prompt LLM.
    demande_type: 'aah', 'pch', 'rqth', 'cmi', 'invalidite', 'orientation', ou None (complet).
    """
    lines = []
    lines.append("=== BASE DE CONNAISSANCES — MDPH (Maison Departementale des Personnes Handicapees) ===\n")

    # Presentation generale
    lines.append("PRESENTATION MDPH :")
    lines.append(f"  {MDPH_GENERAL['definition']}")
    lines.append(f"  Formulaire : {MDPH_GENERAL['formulaire']['cerfa']}")
    lines.append(f"  Certificat medical : {MDPH_GENERAL['formulaire']['certificat_medical']}")
    lines.append(f"  Delai instruction : {MDPH_GENERAL['delais']['instruction']}")
    lines.append(f"  ATTENTION : {MDPH_GENERAL['delais']['silence_vaut_rejet']}")
    lines.append(f"  Renouvellement : {MDPH_GENERAL['delais']['renouvellement']}")
    lines.append("")

    # AAH
    if demande_type in (None, "aah", "allocation"):
        lines.append("AAH — ALLOCATION AUX ADULTES HANDICAPES :")
        lines.append(f"  Base legale : {AAH_ALLOCATION['base_legale']}")
        cond = AAH_ALLOCATION["conditions"]
        lines.append(f"  Conditions : {cond['taux_incapacite']['condition_principale']}")
        lines.append(f"               {cond['taux_incapacite']['condition_alternative']}")
        lines.append(f"  Montant taux plein : {AAH_ALLOCATION['montant']['taux_plein']}")
        lines.append(f"  Deconjugalisation : {AAH_ALLOCATION['deconjugalisation']['reforme']}")
        cumul_inv = AAH_ALLOCATION["cumul"]["avec_pension_invalidite"]
        lines.append(f"  Cumul pension invalidite : {cumul_inv['principe']}")
        lines.append(f"  Calcul : {cumul_inv['calcul']}")
        lines.append(f"  Duree (>=80%) : {AAH_ALLOCATION['duree']['taux_sup_80']}")
        lines.append(f"  Duree (50-79%) : {AAH_ALLOCATION['duree']['taux_50_79']}")
        lines.append("")

    # PCH
    if demande_type in (None, "pch", "compensation"):
        lines.append("PCH — PRESTATION DE COMPENSATION DU HANDICAP :")
        lines.append(f"  Base legale : {PCH_PRESTATION['base_legale']}")
        lines.append(f"  Conditions : {PCH_PRESTATION['conditions']['handicap']}")
        lines.append("  Pas de condition de ressources pour l'attribution.")
        for key, elem in PCH_PRESTATION["elements_couverts"].items():
            lines.append(f"  - {elem['nom']} : {elem['objet']}")
        lines.append(f"  Cumul AAH : {PCH_PRESTATION['cumul']['avec_aah']}")
        lines.append(f"  NON cumulable APA : {PCH_PRESTATION['cumul']['avec_apa']}")
        lines.append("")

    # RQTH
    if demande_type in (None, "rqth", "travailleur"):
        lines.append("RQTH — RECONNAISSANCE QUALITE TRAVAILLEUR HANDICAPE :")
        lines.append(f"  Base legale : {RQTH_RECONNAISSANCE['base_legale']}")
        lines.append(f"  Definition : {RQTH_RECONNAISSANCE['conditions']['definition_th']}")
        lines.append("  Pas de taux minimum requis.")
        lines.append("  Avantages emploi :")
        for av in RQTH_RECONNAISSANCE["avantages"]["emploi"]:
            lines.append(f"    - {av}")
        lines.append("  Protection :")
        for pr in RQTH_RECONNAISSANCE["avantages"]["protection"]:
            lines.append(f"    - {pr}")
        lines.append(f"  Duree : {RQTH_RECONNAISSANCE['duree']}")
        lines.append("")

    # CMI
    if demande_type in (None, "cmi", "carte"):
        lines.append("CMI — CARTE MOBILITE INCLUSION :")
        for type_key, type_info in CMI_CARTE["types"].items():
            lines.append(f"  CMI {type_key} : {type_info['condition']}")
        lines.append("")

    # Pension invalidite / cumul
    if demande_type in (None, "invalidite", "pension"):
        lines.append("PENSION D'INVALIDITE — ARTICULATION MDPH :")
        for cat_key, cat_info in PENSION_INVALIDITE["categories"].items():
            lines.append(f"  {cat_key.replace('_', ' ').title()} : {cat_info['condition']} — {cat_info['montant']}")
        cumul = PENSION_INVALIDITE["cumul_aah"]
        lines.append(f"  Cumul AAH : {cumul['principe']}")
        lines.append(f"  Calcul : {cumul['calcul']}")
        lines.append(f"  Exemple : {cumul['cas_pratique']}")
        lines.append("")

    # Maladies invalidantes
    if demande_type in (None, "maladie_invalidante", "maladie"):
        lines.append("MALADIES INVALIDANTES :")
        lines.append(f"  {MALADIES_INVALIDANTES['definition']}")
        lines.append("  Exemples : " + ", ".join(MALADIES_INVALIDANTES["exemples_reconnus"][:8]) + "...")
        strat = MALADIES_INVALIDANTES["strategie_dossier"]
        for key, val in strat.items():
            lines.append(f"  {val}")
        lines.append("")

    # Voies de recours
    lines.append("VOIES DE RECOURS MDPH :")
    rapo = RECOURS_MDPH["raad"]
    lines.append(f"  1. RAPO obligatoire : {rapo['description']}")
    lines.append(f"     Delai : {rapo['delai']}")
    lines.append(f"     Astuce : {rapo['astuce']}")
    ct = RECOURS_MDPH["contentieux"]
    lines.append(f"  2. Contentieux : {ct['condition']}")
    lines.append(f"     Delai : {ct['delai']}")
    lines.append(f"     {ct['important']}")
    lines.append("")

    # Points strategiques
    lines.append("POINTS STRATEGIQUES MDPH :")
    for pt in MDPH_STRATEGY["points_cles"]:
        lines.append(f"  - {pt}")

    lines.append("\nERREURS FREQUENTES :")
    for err in MDPH_STRATEGY["erreurs_frequentes"]:
        lines.append(f"  - {err}")

    lines.append("\nCONSEILS PREMIUM :")
    for conseil in MDPH_STRATEGY["conseils_premium"]:
        lines.append(f"  - {conseil}")

    lines.append("\nARTICLES DE REFERENCE :")
    for art, desc in MDPH_STRATEGY["articles_reference"].items():
        lines.append(f"  {art} : {desc}")

    return "\n".join(lines)


# =============================================================================
# HELPER : detect_mdph_context()
# =============================================================================

def detect_mdph_context(text):
    """
    Detecte si le texte mentionne un contexte MDPH et retourne le type de demande
    le plus probable, ou None si aucun contexte MDPH detecte.
    Retourne : 'aah', 'pch', 'rqth', 'cmi', 'invalidite', 'maladie_invalidante', 'general', ou None.
    """
    import unicodedata

    def normalize(s):
        return unicodedata.normalize("NFD", (s or "").lower()).encode("ascii", "ignore").decode("ascii")

    text_norm = normalize(text)

    # Detection par specificite (du plus specifique au plus general)

    # PCH
    pch_keywords = [
        "pch", "prestation de compensation", "prestation compensation handicap",
        "aide humaine", "aides humaines", "amenagement logement handicap",
        "amenagement vehicule handicap", "tierce personne handicap",
        "aidant familial pch", "emploi direct handicap",
    ]
    for kw in pch_keywords:
        if kw in text_norm:
            return "pch"

    # AAH
    aah_keywords = [
        "aah", "allocation adulte handicape", "allocation aux adultes handicapes",
        "allocation adultes handicapes", "deconjugalisation",
        "majoration vie autonome", "mva handicap",
        "rsdae", "restriction substantielle et durable",
        "complement de ressources handicap",
    ]
    for kw in aah_keywords:
        if kw in text_norm:
            return "aah"

    # RQTH
    rqth_keywords = [
        "rqth", "reconnaissance travailleur handicape",
        "qualite travailleur handicape", "travailleur handicape",
        "agefiph", "fiphfp", "cap emploi handicap",
        "obligation emploi handicape", "oeth",
        "amenagement poste handicap",
    ]
    for kw in rqth_keywords:
        if kw in text_norm:
            return "rqth"

    # CMI
    cmi_keywords = [
        "carte mobilite inclusion", "cmi invalidite", "cmi priorite",
        "cmi stationnement", "carte invalidite handicap",
        "carte stationnement handicap",
    ]
    for kw in cmi_keywords:
        if kw in text_norm:
            return "cmi"

    # Pension invalidite / cumul
    invalidite_keywords = [
        "pension invalidite", "pension d'invalidite",
        "invalidite categorie", "invalide categorie",
        "cumul aah pension", "cumul pension aah",
        "cumul invalidite aah", "cumul aah invalidite",
        "rente at aah", "rente mp aah",
    ]
    for kw in invalidite_keywords:
        if kw in text_norm:
            return "invalidite"

    # Maladies invalidantes
    maladie_keywords = [
        "maladie invalidante", "maladies invalidantes",
        "fibromyalgie mdph", "sclerose en plaques mdph", "sep mdph",
        "crohn mdph", "epilepsie mdph", "endometriose mdph",
        "fatigue chronique mdph", "handicap invisible",
    ]
    for kw in maladie_keywords:
        if kw in text_norm:
            return "maladie_invalidante"

    # MDPH general
    mdph_general_keywords = [
        "mdph", "maison departementale", "cdaph",
        "commission des droits", "equipe pluridisciplinaire mdph",
        "plan personnalise de compensation", "ppc handicap",
        "cerfa 15692", "cerfa 15695",
        "projet de vie mdph", "projet de vie handicap",
        "demande mdph", "dossier mdph",
        "renouvellement mdph", "recours mdph",
        "rapo mdph", "contestation mdph",
    ]
    for kw in mdph_general_keywords:
        if kw in text_norm:
            return "general"

    return None
