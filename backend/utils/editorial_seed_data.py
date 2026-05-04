"""Pre-loaded legal reference base for the Editorial Studio.

This data seeds the `editorial_legal_refs` MongoDB collection on first boot.
Adding/removing entries here is safe — the seeder upserts by `ref_key`.

Each ref has:
  - ref_key: stable unique key (e.g. "L821-2_CSS")
  - kind: "loi" | "jurisprudence" | "chiffre" | "delai" | "barème"
  - label: human-readable label
  - text: short canonical text (1 sentence summary, neutral)
  - source: official URL (Légifrance, Ameli, etc.)
  - last_verified: ISO date
  - tags: list of subject tags (e.g. ["aah", "mdph"])
"""
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat()


SEED_LEGAL_REFS = [
    # ========== LOIS — Sécurité Sociale / Handicap ==========
    {"ref_key": "L821-1_CSS", "kind": "loi", "label": "Article L.821-1 CSS",
     "text": "Allocation aux Adultes Handicapés — bénéficiaires et conditions de base.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049554330",
     "last_verified": NOW, "tags": ["aah", "mdph"]},
    {"ref_key": "L821-2_CSS", "kind": "loi", "label": "Article L.821-2 CSS",
     "text": "AAH au taux 50-79 % avec restriction substantielle et durable d'accès à l'emploi (RSDAE).",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049554328",
     "last_verified": NOW, "tags": ["aah", "rsdae"]},
    {"ref_key": "L114-1_CASF", "kind": "loi", "label": "Article L.114-1 CASF",
     "text": "Définition légale du handicap — limitation d'activité ou restriction de participation à la vie en société.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006796446",
     "last_verified": NOW, "tags": ["mdph", "handicap"]},
    {"ref_key": "L241-6_CASF", "kind": "loi", "label": "Article L.241-6 CASF",
     "text": "Compétences de la CDAPH — attribution AAH, RQTH, PCH, orientation.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037112857",
     "last_verified": NOW, "tags": ["mdph", "cdaph"]},

    # ========== LOIS — Accident travail / Maladie pro ==========
    {"ref_key": "L411-1_CSS", "kind": "loi", "label": "Article L.411-1 CSS",
     "text": "Définition de l'accident du travail — fait accidentel survenu par le fait ou à l'occasion du travail.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006742964",
     "last_verified": NOW, "tags": ["at-mp", "accident-travail"]},
    {"ref_key": "L461-1_CSS", "kind": "loi", "label": "Article L.461-1 CSS",
     "text": "Maladies professionnelles — présomption d'imputabilité pour les pathologies inscrites aux tableaux.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048779671",
     "last_verified": NOW, "tags": ["at-mp", "maladie-pro"]},
    {"ref_key": "L452-1_CSS", "kind": "loi", "label": "Article L.452-1 CSS",
     "text": "Faute inexcusable de l'employeur — majoration de la rente et indemnisation complémentaire.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006743144",
     "last_verified": NOW, "tags": ["at-mp", "faute-inexcusable"]},
    {"ref_key": "L431-1_CSS", "kind": "loi", "label": "Article L.431-1 CSS",
     "text": "Prestations en cas d'accident du travail — soins, indemnités journalières, IPP, rente.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031086943",
     "last_verified": NOW, "tags": ["at-mp", "ipp"]},
    {"ref_key": "L434-2_CSS", "kind": "loi", "label": "Article L.434-2 CSS",
     "text": "Calcul de la rente AT/MP — taux IPP × salaire annuel de référence × coefficient.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033712707",
     "last_verified": NOW, "tags": ["at-mp", "ipp", "rente"]},
    {"ref_key": "R441-7_CSS", "kind": "loi", "label": "Article R.441-7 CSS",
     "text": "Délai d'instruction CPAM — 30 jours pour AT, 120 jours pour MP (avec prolongation possible).",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000040837085",
     "last_verified": NOW, "tags": ["at-mp", "cpam", "delais"]},

    # ========== LOIS — Expertise médicale ==========
    {"ref_key": "L141-1_CSS", "kind": "loi", "label": "Article L.141-1 CSS",
     "text": "Expertise médicale technique — désignation expert, contradiction et modalités.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033712753",
     "last_verified": NOW, "tags": ["expertise-medicale"]},
    {"ref_key": "R141-1_CSS", "kind": "loi", "label": "Article R.141-1 CSS",
     "text": "Expertise médicale — procédure : convocation, dires, rapport.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033712749",
     "last_verified": NOW, "tags": ["expertise-medicale"]},

    # ========== JURISPRUDENCES MAJEURES ==========
    {"ref_key": "Cass_soc_2002_amiante", "kind": "jurisprudence", "label": "Cass. soc. 28 février 2002 (arrêts amiante)",
     "text": "Manquement employeur à son obligation de sécurité de résultat = faute inexcusable de droit.",
     "source": "https://www.courdecassation.fr/decision/61372be4cd58014677404d97",
     "last_verified": NOW, "tags": ["faute-inexcusable", "amiante"]},
    {"ref_key": "Cass_soc_2010_burnout", "kind": "jurisprudence", "label": "Cass. soc. 1er juillet 2010 n°09-66.106",
     "text": "Le burn-out peut être reconnu comme accident du travail s'il survient au temps et lieu du travail.",
     "source": "https://www.courdecassation.fr/",
     "last_verified": NOW, "tags": ["accident-travail", "burnout"]},

    # ========== CHIFFRES OFFICIELS 2026 ==========
    {"ref_key": "AAH_montant_2026", "kind": "chiffre", "label": "Montant AAH plein 2026",
     "text": "Montant maximal AAH au 1er avril 2026 — à vérifier sur ameli.fr/CAF.",
     "source": "https://www.service-public.fr/particuliers/vosdroits/F12242",
     "last_verified": NOW, "tags": ["aah", "chiffre"]},
    {"ref_key": "Plafond_SS_2026", "kind": "chiffre", "label": "Plafond annuel Sécu 2026 (PASS)",
     "text": "Plafond annuel de la Sécurité Sociale 2026 — base de calcul des rentes AT-MP.",
     "source": "https://www.urssaf.fr/portail/home/taux-et-baremes/plafonds.html",
     "last_verified": NOW, "tags": ["pass", "rente"]},

    # ========== DÉLAIS PROCÉDURAUX ==========
    {"ref_key": "delai_RAPO_MDPH", "kind": "delai", "label": "Délai RAPO MDPH",
     "text": "2 mois à compter de la notification de la décision MDPH/CDAPH pour exercer le RAPO.",
     "source": "https://www.service-public.fr/particuliers/vosdroits/F31019",
     "last_verified": NOW, "tags": ["mdph", "rapo", "delais"]},
    {"ref_key": "delai_recours_pole_social", "kind": "delai", "label": "Délai recours pôle social",
     "text": "2 mois à compter de la notification de rejet du RAPO (ou silence > 2 mois) pour saisir le pôle social du tribunal judiciaire.",
     "source": "https://www.service-public.fr/particuliers/vosdroits/F31019",
     "last_verified": NOW, "tags": ["mdph", "tribunal", "delais"]},
    {"ref_key": "delai_declaration_AT", "kind": "delai", "label": "Délai déclaration AT par employeur",
     "text": "L'employeur dispose de 48 heures pour déclarer l'accident du travail à la CPAM.",
     "source": "https://www.ameli.fr/assure/droits-demarches/maladie-accident-hospitalisation/accident-travail/declarer-accident-travail",
     "last_verified": NOW, "tags": ["at", "delais", "employeur"]},
    {"ref_key": "delai_dires_expertise", "kind": "delai", "label": "Délai des dires (expertise)",
     "text": "8 jours après la réception du pré-rapport pour adresser ses dires (observations) à l'expert.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033712749",
     "last_verified": NOW, "tags": ["expertise-medicale", "dires", "delais"]},

    # ========== BARÈMES ==========
    {"ref_key": "bareme_IPP_concours_medical", "kind": "barème", "label": "Barème IPP — Concours Médical (AT-MP)",
     "text": "Barème indicatif d'invalidité utilisé pour évaluer l'IPP en AT-MP — Annexe I, fascicule 1.",
     "source": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031801580",
     "last_verified": NOW, "tags": ["ipp", "bareme", "at-mp"]},
    {"ref_key": "seuil_rente_10_pct", "kind": "chiffre", "label": "Seuil 10 % IPP — rente vs capital",
     "text": "IPP ≥ 10 % = rente viagère ; IPP < 10 % = capital unique versé une seule fois.",
     "source": "https://www.ameli.fr/assure/droits-demarches/maladie-accident-hospitalisation/accident-travail/sequelles-indemnisation",
     "last_verified": NOW, "tags": ["ipp", "rente", "at-mp"]},
]


# ========== POOL DE 30 SUJETS PRIORITAIRES ==========
SEED_TOPICS = [
    # ====== AT / MP (8) ======
    {"title": "Tableau 57 maladies professionnelles : guide complet 2026",
     "category": "at-mp", "potential": "haut",
     "angle": "Guide complet des affections péri-articulaires reconnues : conditions médicales, délais, présomption d'imputabilité."},
    {"title": "Faute inexcusable de l'employeur : les 3 critères Cass. soc. à connaître",
     "category": "at-mp", "potential": "haut",
     "angle": "Décortique les 3 conditions : conscience du danger, absence de mesures, lien causal — avec exemples concrets."},
    {"title": "Accident du travail non déclaré par l'employeur : que faire en 2026",
     "category": "at-mp", "potential": "haut",
     "angle": "Procédure de déclaration personnelle, délais, preuve de l'accident, recours CPAM."},
    {"title": "Burn-out reconnu en accident du travail : la jurisprudence qui change tout",
     "category": "at-mp", "potential": "haut",
     "angle": "Conditions de reconnaissance, critères temps/lieu/travail, preuves à constituer."},
    {"title": "Refus de maladie professionnelle CPAM : la stratégie de recours efficace",
     "category": "at-mp", "potential": "moyen",
     "angle": "Comprendre les motifs de refus fréquents et structurer son contestation."},
    {"title": "Consolidation après accident du travail : ce que personne ne vous explique",
     "category": "at-mp", "potential": "haut",
     "angle": "Distinction guérison/consolidation, enjeux IPP, risque de consolidation prématurée."},
    {"title": "Coefficient socio-professionnel IPP : comment le faire majorer",
     "category": "at-mp", "potential": "moyen",
     "angle": "Critères de majoration, dires à formuler, jurisprudence favorable."},
    {"title": "Rechute après AT consolidé : vos droits et la procédure CPAM",
     "category": "at-mp", "potential": "moyen",
     "angle": "Définition juridique de la rechute, certificat médical, indemnités."},

    # ====== MDPH / AAH (8) ======
    {"title": "Refus AAH motif 6 : que répondre concrètement à la MDPH",
     "category": "mdph", "potential": "haut",
     "angle": "Décrypter le motif 6 (RSDAE non reconnue), construire un RAPO ciblé."},
    {"title": "Recours MDPH 2026 : guide pas à pas pour gagner en RAPO",
     "category": "mdph", "potential": "haut",
     "angle": "Procédure complète, pièces nouvelles, formulation argumentaire."},
    {"title": "PCH et aides humaines : comment monter un dossier solide",
     "category": "mdph", "potential": "moyen",
     "angle": "Évaluation GEVA-Sco, justificatifs, choix entre les 4 volets."},
    {"title": "RQTH et invalidité : compatibilité, cumul, stratégie",
     "category": "mdph", "potential": "moyen",
     "angle": "Différences statutaires, cumul possible, intérêt selon profil pro."},
    {"title": "Renouvellement AAH refusé alors que mon état s'aggrave : que faire",
     "category": "mdph", "potential": "haut",
     "angle": "Argumentation aggravation, certificat médical actualisé, jurisprudence."},
    {"title": "Tribunal judiciaire pôle social : comment plaider sans avocat",
     "category": "mdph", "potential": "moyen",
     "angle": "Procédure, pièces, oralité de l'audience, préparation."},
    {"title": "Carte mobilité inclusion (CMI) : critères 2026 et abus de refus",
     "category": "mdph", "potential": "moyen",
     "angle": "Stationnement, priorité, invalidité — les 3 mentions et leurs conditions."},
    {"title": "Dossier MDPH enfant : les pièges à éviter pour 2026",
     "category": "mdph", "potential": "moyen",
     "angle": "AEEH, compléments, GEVA-Sco, lien avec établissements scolaires."},

    # ====== Expertise médicale (6) ======
    {"title": "Médecin conseil CPAM : 7 questions auxquelles préparer une réponse",
     "category": "expertise", "potential": "haut",
     "angle": "Anticiper les questions clés et construire des réponses qui protègent le dossier."},
    {"title": "Expertise médicale assurance : reconnaître les pièges classiques",
     "category": "expertise", "potential": "haut",
     "angle": "Différence CPAM vs assurance, conflits d'intérêts, comment se protéger."},
    {"title": "Dires d'expertise : le modèle stratégique en 5 paragraphes",
     "category": "expertise", "potential": "moyen",
     "angle": "Structure type, formulations efficaces, exemples concrets."},
    {"title": "Contre-expertise : quand la demander et comment la construire",
     "category": "expertise", "potential": "moyen",
     "angle": "Motifs valables, choix de l'expert, pièces à transmettre."},
    {"title": "Préparer son expertise médicale : journal des douleurs sur 4 semaines",
     "category": "expertise", "potential": "haut",
     "angle": "Méthode, exemples, ce qu'il faut consigner et ce qu'il faut éviter."},
    {"title": "Expertise IPP défavorable : 3 leviers de contestation efficaces",
     "category": "expertise", "potential": "moyen",
     "angle": "Vice de procédure, sous-évaluation, oubli du coefficient socio-pro."},

    # ====== Invalidité / Protection juridique (4) ======
    {"title": "Invalidité catégorie 2 : conditions, calcul, cumul avec AAH",
     "category": "invalidite", "potential": "haut",
     "angle": "Critères CPAM, montant, articulation avec AAH différentielle."},
    {"title": "Litige assurance prévoyance : la stratégie qui fait basculer le dossier",
     "category": "protection-juridique", "potential": "moyen",
     "angle": "Lecture du contrat, antériorité, carence, jurisprudence assurés."},
    {"title": "Antériorité et carence en prévoyance : pièges à connaître",
     "category": "protection-juridique", "potential": "moyen",
     "angle": "Définitions, comment elles sont activées, recours possibles."},
    {"title": "Protection juridique : ce que votre contrat couvre vraiment",
     "category": "protection-juridique", "potential": "moyen",
     "angle": "Périmètre réel, plafonds, exclusions, comment activer."},

    # ====== Calculatrices / Stratégie globale (4) ======
    {"title": "Calculer son IPP avant l'expertise : pourquoi c'est essentiel",
     "category": "ipp", "potential": "moyen",
     "angle": "Méthode d'auto-évaluation, marges de négociation, rôle des dires."},
    {"title": "AAH différentielle : comment la calculer en 2026",
     "category": "aah", "potential": "moyen",
     "angle": "Cas concrets, ressources prises en compte, neutralisation conjoint."},
    {"title": "Cumul AAH + revenus du travail : règles 2026 et pièges",
     "category": "aah", "potential": "moyen",
     "angle": "Abattements, lissage trimestriel, cas ESAT, limite mensuelle."},
    {"title": "Salaire de référence AT/MP : comment le contester quand il est faussé",
     "category": "at-mp", "potential": "moyen",
     "angle": "Calcul CPAM, primes, années incomplètes, recours."},
]
