"""
BASE DE CONNAISSANCES ASSURANTIELLE — Strategie & Expertise Sante
=================================================================
Source : Notices d'information des contrats emprunteurs
Fichier exploitable par StrategiIA pour l'analyse des litiges assurantiels.

Structure :
- ASSURANCE_KNOWLEDGE : dictionnaire principal par assureur
- GARANTIES_DEFINITIONS : definitions normalisees inter-assureurs
- get_assurance_context() : helper pour injecter le contexte dans le prompt
"""

# =============================================================================
# DEFINITIONS NORMALISEES DES GARANTIES (inter-assureurs)
# =============================================================================

GARANTIES_DEFINITIONS = {
    "ITT": {
        "nom_complet": "Incapacite Temporaire Totale",
        "description": "Impossibilite temporaire totale d'exercer son activite professionnelle, constatee medicalement.",
        "nature": "Temporaire — cesse a la reprise ou a la consolidation.",
        "confusion_frequente": "Ne pas confondre avec l'arret maladie de la Securite Sociale. L'assureur applique sa propre definition contractuelle, souvent plus restrictive.",
    },
    "ITP": {
        "nom_complet": "Incapacite Temporaire Partielle",
        "description": "Reprise partielle d'activite (mi-temps therapeutique) apres une ITT indemnisee.",
        "nature": "Temporaire — limitee dans le temps (souvent 180 jours max).",
        "confusion_frequente": "Ne concerne que le mi-temps therapeutique prescrit medicalement, pas une simple reduction de temps de travail.",
    },
    "IPT": {
        "nom_complet": "Invalidite Permanente Totale",
        "description": "Etat permanent d'incapacite totale d'exercer son activite professionnelle, avec taux >= 66%.",
        "nature": "Permanente — apres consolidation de l'etat de sante.",
        "confusion_frequente": "Le taux est fixe par le medecin-conseil de l'assureur, independamment de la Securite Sociale. Un taux SS ne vaut pas taux assureur.",
    },
    "IPP": {
        "nom_complet": "Invalidite Permanente Partielle",
        "description": "Etat permanent d'incapacite partielle, avec taux entre 33% et 65%.",
        "nature": "Permanente — indemnisation partielle (souvent 50% des echeances).",
        "confusion_frequente": "Ne pas confondre avec le taux IPP de la Securite Sociale (AT/MP). Le bareme assureur est different.",
    },
    "PTIA": {
        "nom_complet": "Perte Totale et Irreversible d'Autonomie",
        "description": "Impossibilite definitive d'exercer toute activite ET necessite d'une tierce personne pour les actes de la vie courante.",
        "nature": "Definitive — conditions cumulatives tres strictes.",
        "confusion_frequente": "Beaucoup plus restrictive que l'invalidite 3e categorie SS. Exige DEUX conditions cumulatives.",
    },
    "PE": {
        "nom_complet": "Perte d'Emploi",
        "description": "Licenciement d'un CDI (hors faute grave/lourde, demission, rupture conventionnelle).",
        "nature": "Temporaire — limitee a 12-24 mois selon contrats.",
        "confusion_frequente": "Exclut quasi-systematiquement la rupture conventionnelle et la demission, meme indemnisee par Pole Emploi.",
    },
    "DECES": {
        "nom_complet": "Deces",
        "description": "Versement du capital restant du au preteur en cas de deces de l'assure.",
        "nature": "Definitive.",
        "confusion_frequente": "Le suicide est exclu la premiere annee (sauf pret immobilier residence principale <= 120 000 euros).",
    },
}


# =============================================================================
# BASE DE CONNAISSANCES PAR ASSUREUR
# =============================================================================

ASSURANCE_KNOWLEDGE = {

    # =========================================================================
    # GENERALI
    # =========================================================================
    "generali": {
        "contract_name": "Contrat d'assurance collectif n 7270",
        "assureur": "GENERALI VIE / GENERALI IARD",
        "type": "Assurance groupe emprunteur",
        "reference": "DDP7270D - NI 12/2020",
        "version": "Decembre 2020",

        "guarantees": {
            "DECES": {
                "definition": "Prise en charge du capital assure en cas de deces de l'assure.",
                "conditions": ["Adhesion au contrat", "Paiement des cotisations"],
                "age_limite": "85 ans",
                "franchise": "Aucune",
                "mode_evaluation": "Capital restant du au jour du deces",
                "exclusions": [
                    "Suicide < 1 an apres adhesion (sauf pret immo residence principale <= 120 000 euros)",
                    "Navigation aerienne (hors vols reguliers)",
                    "Acrobaties aeriennes, tentatives de record, paris, defis",
                    "Accidents anterieurs a l'adhesion non declares",
                    "Phenomenes de radioactivite",
                ],
                "pieces_justificatives": [
                    "Acte de deces original",
                    "Certificat medical post-mortem",
                    "Tableau d'amortissement arrete au jour du deces",
                    "Si accident : PV gendarmerie/police",
                ],
            },
            "PTIA": {
                "definition": "Invalidite physique ou intellectuelle rendant l'assure definitivement incapable d'exercer une activite quelconque ET necessitant l'assistance permanente d'une tierce personne pour TOUS les actes ordinaires de la vie.",
                "conditions": ["Conditions cumulatives : incapacite totale definitive + tierce personne permanente"],
                "age_limite": "70 ans",
                "franchise": "Aucune",
                "seuils": "Tierce personne pour se laver, se vetir, se nourrir, se deplacer",
                "mode_evaluation": "Capital assure verse",
                "exclusions": [
                    "Exclusions identiques au Deces",
                    "Tentative de suicide, mutilation volontaire, acte intentionnel",
                    "Conduite en etat d'ivresse ou sous emprise de stupefiants",
                ],
                "pieces_justificatives": [
                    "Declaration de l'assure (imprime assureur)",
                    "Certificat medical (imprime assureur)",
                    "Notification pension invalidite 3e categorie SS (si beneficiaire)",
                    "Tableau d'amortissement",
                ],
            },
            "ITT": {
                "definition": "Incapacite totale et temporaire d'exercer son activite professionnelle (ou occupations habituelles si sans emploi).",
                "conditions": ["Arret total et continu", "Constatation medicale"],
                "age_limite": "70 ans",
                "franchise": "90 jours",
                "duree_max_indemnisation": "Non precisee (jusqu'a consolidation ou reprise)",
                "mode_evaluation": "Paiement des echeances dues (capital + interets) dans la limite de la quotite assuree",
                "exoneration_cotisations": "A partir du 91e jour d'ITT",
                "exclusions": [
                    "Exclusions Deces + PTIA",
                    "Rixes (sauf legitime defense)",
                    "Guerre civile ou etrangere",
                    "AFFECTIONS DISCO-VERTEBRALES (hernie discale, lumbago, sciatique, cervicalgie, dorsalgie, lombalgie) — SAUF intervention chirurgicale ou hospitalisation >= 4 jours",
                    "AFFECTIONS PSYCHIQUES (depression, anxio-depressif, fibromyalgie, burnout, bipolarite, schizophrenie) — SAUF hospitalisation >= 5 jours en etablissement specialise",
                    "Maternite (conge maternite non considere comme incapacite)",
                ],
                "pieces_justificatives": [
                    "Declaration de l'assure",
                    "Certificat medical",
                    "Volets ou attestation SS",
                    "Justificatif SS si mi-temps therapeutique",
                    "Tableau d'amortissement",
                    "Certificats de prolongation",
                    "Certificat de fin d'incapacite",
                ],
                "rechute": "Delai de 2 mois : rechute = meme sinistre. Au-dela = nouvel arret avec nouvelle franchise.",
            },
            "IPT": {
                "definition": "Persistance d'une incapacite totale au travail apres consolidation. Taux >= 66% determine par expertise medicale de l'assureur.",
                "conditions": ["Consolidation medicale", "Taux incapacite >= 66%"],
                "age_limite": "70 ans",
                "franchise": "Aucune mentionnee (debut des la constatation)",
                "seuils": "Taux >= 66% (expertise medecin-conseil assureur)",
                "mode_evaluation": "Capital restant du (prets amortissables) ou capital initial (prets in fine)",
                "exclusions": [
                    "Identiques a l'ITT",
                ],
            },
            "ITP": {
                "definition": "Incapacite partielle et temporaire dans le cadre d'un mi-temps therapeutique, en continuite d'une ITT indemnisee.",
                "conditions": ["Doit suivre une ITT indemnisee", "Mi-temps therapeutique prescrit medicalement"],
                "age_limite": "70 ans",
                "franchise": "90 jours (rechutes : franchise a partir de la 3e rechute consecutive)",
                "duree_max": "180 jours continus maximum",
                "mode_evaluation": "50% des echeances dues",
                "exclusions": [
                    "Identiques a l'ITT",
                ],
            },
            "IPP": {
                "definition": "Persistance d'une incapacite partielle au travail apres consolidation. Taux entre 33% et 65%.",
                "conditions": ["Consolidation medicale", "Taux entre 33% et 65%"],
                "age_limite": "70 ans",
                "franchise": "90 jours",
                "seuils": "33% <= taux < 66%",
                "mode_evaluation": "Formule : (N-33)/33 x prestation IPT. N = taux reconnu.",
                "exclusions": [
                    "Identiques a l'ITT",
                ],
            },
            "PE": {
                "definition": "Licenciement d'un CDI. L'assure doit etre en CDI depuis au moins 12 mois.",
                "conditions": ["CDI depuis >= 12 mois", "Licenciement (hors faute grave/lourde)"],
                "age_limite": "62 ans",
                "franchise": "180 jours",
                "duree_max": "12 mois par periode de chomage, 24 mois cumules sur toute la duree de l'adhesion",
                "mode_evaluation": "75% des echeances dues (capital + interets)",
                "exclusions": [
                    "Retraite ou preretraite",
                    "Demission (meme indemnisee par Pole Emploi)",
                    "Rupture conventionnelle",
                    "Licenciement pour faute grave ou lourde",
                    "Rupture pendant ou a la fin de la periode d'essai",
                    "Licenciement d'un conjoint/ascendant/descendant (sauf liquidation judiciaire)",
                    "Cessation d'activite sans recherche d'emploi",
                ],
                "pieces_justificatives": [
                    "Copie lettre de licenciement",
                    "Lettre d'admission au revenu de remplacement (Pole Emploi)",
                    "Attestation employeur (nature contrat, dates)",
                    "Bordereaux de paiement Pole Emploi",
                    "Tableau d'amortissement",
                ],
            },
        },

        "red_flags": [
            "EXCLUSION DISCO-VERTEBRALE : Hernie discale, lumbago, sciatique exclus sauf chirurgie ou hospitalisation >= 4 jours. Piege majeur pour les lombalgies chroniques.",
            "EXCLUSION PSYCHIQUE : Depression, burnout, fibromyalgie exclus sauf hospitalisation >= 5 jours en etablissement specialise. Piege pour les arrets longue duree pour depression.",
            "FRANCHISE 90 JOURS ITT : L'assure doit payer ses echeances de pret pendant 3 mois avant toute indemnisation.",
            "PTIA = CONDITIONS CUMULATIVES : Impossibilite de TOUTE activite + tierce personne pour TOUS les actes de la vie. Critere extremement restrictif.",
            "PE = RUPTURE CONVENTIONNELLE EXCLUE : Tres frequent en pratique, systematiquement exclu par Generali.",
            "TAUX IPP/IPT : Evalue par le medecin-conseil Generali, PAS par la SS. Divergence frequente entre taux SS et taux assureur.",
            "SPORTS EXCLUS : Liste tres large (parapente, ULM, plongee, ski hors-piste, rugby, sports de combat, kitesurf, etc.). Rachetable moyennant surprime.",
            "ITP LIMITEE A 180 JOURS : Le mi-temps therapeutique n'est couvert que 6 mois maximum.",
        ],

        "strategic_reading": {
            "what_to_check_first": [
                "La garantie souscrite correspond-elle au sinistre declare (verifier option choisie) ?",
                "Le sinistre est-il survenu avant l'age limite de la garantie concernee ?",
                "L'affection releve-t-elle d'une exclusion disco-vertebrale ou psychique ?",
                "La franchise de 90 jours a-t-elle ete respectee/epuisee ?",
                "Le taux d'incapacite a-t-il ete evalue par le medecin-conseil Generali ?",
            ],
            "what_strengthens_claim": [
                "Hospitalisation >= 4 jours pour affection disco-vertebrale (leve l'exclusion)",
                "Hospitalisation >= 5 jours en psychiatrie pour affection psychique (leve l'exclusion)",
                "Coherence entre le diagnostic medical et la definition contractuelle de la garantie",
                "Documents prouvant l'incapacite totale (pas partielle) d'exercer son activite professionnelle",
                "Notification d'invalidite 2e ou 3e categorie par la Securite Sociale",
            ],
            "what_weakens_claim": [
                "Lombalgie chronique sans chirurgie ni hospitalisation >= 4 jours",
                "Depression sans hospitalisation specialisee >= 5 jours",
                "Taux d'incapacite fixe par la SS mais non reconnu par le medecin-conseil Generali",
                "Reprise partielle d'activite sans prescription de mi-temps therapeutique",
                "Declaration tardive du sinistre",
            ],
            "common_disputes": [
                "Divergence entre taux SS et taux medecin-conseil Generali",
                "Refus pour exclusion disco-vertebrale sur une pathologie reelle et invalidante",
                "Contestation de la date de consolidation",
                "Refus PE pour rupture conventionnelle alors que l'assure a ete contraint",
            ],
        },

        "global_notes": [
            "Contrat emprunteur classique avec exclusions standard mais strictes sur le rachis et le psychique.",
            "Les exclusions disco-vertebrales et psychiques sont rachetables moyennant surprime — verifier si le rachat a ete souscrit.",
            "La garantie provisoire accident couvre immediatement en cas de deces accidentel (60 jours max, 150 000 euros max).",
        ],
    },

    # =========================================================================
    # GROUPAMA GAN VIE
    # =========================================================================
    "groupama_gan_vie": {
        "contract_name": "Notice d'information du contrat d'assurance de groupe emprunteurs",
        "assureur": "Groupama Gan Vie",
        "type": "Assurance de groupe emprunteurs a adhesion facultative",
        "reference": "6092 / 200140",
        "version": "Avril 2022",

        "guarantees": {
            "DECES": {
                "definition": "Deces de l'assure par suite d'accident ou de maladie.",
                "conditions": ["Adhesion au contrat", "Prise d'effet des garanties"],
                "age_limite": "80 ans (31 decembre suivant le 80e anniversaire)",
                "franchise": "Aucune",
                "mode_evaluation": "Capital restant du au jour du deces (tableau d'amortissement)",
                "garantie_provisoire": "90 jours max a compter de la signature du bulletin d'adhesion (deces accidentel uniquement)",
                "exclusions": [
                    "Suicide < 1 an (sauf pret immo habitation principale <= 120 000 euros)",
                    "Guerre civile ou etrangere, insurrection, emeute, rixe, crime/delit avec participation active",
                    "Accident de navigation aerienne (sauf exceptions avec licence et appareil certifie)",
                ],
                "pieces_justificatives": [
                    "Acte de deces original",
                    "Certificat medical original (date et cause du deces)",
                    "Declaration de deces par les ayants droit",
                    "Tableau d'amortissement arrete au jour du deces",
                    "Attestation du preteur (capital restant du)",
                    "RIB",
                ],
            },
            "PTIA": {
                "definition": "Impossibilite definitive d'exercer une activite professionnelle quelconque ET obligation de recourir a une tierce personne pour l'ensemble des actes ordinaires de la vie courante (se laver, se vetir, se nourrir, se deplacer).",
                "conditions": ["Conditions cumulatives : aucune activite possible + tierce personne permanente", "Appreciation par le medecin-conseil de l'assureur"],
                "age_limite": "70 ans (31 decembre suivant le 70e anniversaire)",
                "franchise": "Aucune",
                "seuils": "Tierce personne pour les 4 actes : se laver, se vetir, se nourrir, se deplacer",
                "mode_evaluation": "Capital restant du",
                "exclusions": [
                    "Exclusions Deces",
                    "Acte volontaire, tentative de suicide, mutilation volontaire",
                    "Usage de stupefiants, psychotropes hors prescription",
                    "Explosions, irradiations atomiques",
                    "Accident en etat d'impregnation alcoolique (taux Code de la route)",
                    "Competitions amateurs avec engin a moteur, paris, tentatives de records",
                    "Saut a l'elastique, tauromachie",
                    "Sports professionnels ou remuneres",
                ],
                "exclusions_rachetables": [
                    "Competitions hippiques/equitation",
                    "Speleologie",
                    "Sports aeriens",
                    "Sports de montagne",
                    "Sports nautiques (plongee > 20m, navigation hauturiere solitaire)",
                    "Sports de neige",
                    "Sports avec engin a moteur (sauf initiation encadree)",
                ],
            },
            "ITT": {
                "definition": "Etat temporaire d'incapacite physique ou psychique totale d'exercer son activite professionnelle (ou occupations habituelles si sans emploi). Apprecie par le medecin-conseil de l'assureur, independamment de la SS.",
                "conditions": ["Arret total et continu", "Constatation medicale", "Independant de la decision SS"],
                "age_limite": "65 ans (31 decembre suivant le 65e anniversaire)",
                "franchise": "90 jours d'arret total et continu",
                "duree_max_indemnisation": "1095 jours au total",
                "mode_evaluation": "Mensualites du pret selon tableau d'amortissement au jour du sinistre",
                "mi_temps_therapeutique": "50% des prestations pendant 6 mois max apres ITT indemnisee",
                "rechute": "Dans les 2 mois = meme sinistre (pas de nouvelle franchise). Apres 2 mois = nouvel arret.",
                "exclusions": [
                    "Arrets en cours a la prise d'effet",
                    "Grossesse et accouchement (sauf complications post-maternite > 90 jours apres conge legal)",
                    "Traitements et chirurgie esthetiques",
                    "AFFECTIONS DORSALES — SAUF chirurgie OU hospitalisation > 7 JOURS (plus strict que Generali)",
                    "AFFECTIONS PSYCHIQUES — SAUF hospitalisation psychiatrique > 15 JOURS (beaucoup plus strict que Generali)",
                    "Certains sports nautiques et de neige (canyoning, hydrospeed, kayak mer, rafting, surf competition, hockey glace, luge competition, ski artistique)",
                ],
                "exclusions_rachetables": [
                    "Affections dorsales : rachat total possible (souscription option)",
                    "Affections psychiques : rachat total possible (souscription option)",
                ],
                "pieces_justificatives": [
                    "Copie bulletin et certificat d'adhesion",
                    "Attestation medicale confidentielle (medecin traitant)",
                    "Declaration d'arret de travail",
                    "Justificatif activite professionnelle au jour du sinistre",
                    "Prolongations (certificats, decomptes)",
                    "Notification pension invalidite si applicable",
                    "Tableau d'amortissement",
                    "Attestation preteur (mensualites dues)",
                    "RIB",
                ],
            },
            "IPT": {
                "definition": "Etat permanent d'incapacite physique ou psychique totale d'exercer son activite professionnelle. Taux >= 66%. Apprecie par le medecin-conseil de l'assureur.",
                "conditions": ["Consolidation medicale", "Taux >= 66% (medecin-conseil assureur)"],
                "age_limite": "65 ans",
                "franchise": "90 jours (non appliquee si fait suite a une ITT deja indemnisee sans discontinuite)",
                "seuils": "Taux incapacite >= 66% — croise taux fonctionnel + taux professionnel",
                "mode_evaluation": "Mensualites du pret (identique ITT)",
                "exclusions": ["Identiques a l'ITT"],
            },
            "IPP": {
                "definition": "Etat permanent d'incapacite physique ou psychique partielle. Taux entre 33% et 65%. Medecin-conseil assureur.",
                "conditions": ["Consolidation medicale", "Taux entre 33% et 65%"],
                "age_limite": "65 ans",
                "franchise": "90 jours",
                "seuils": "33% <= taux < 66%",
                "mode_evaluation": "50% des prestations prevues en cas d'IPT",
                "exclusions": ["Identiques a l'IPT"],
            },
        },

        "options_adhesion": {
            "option_1": {"age_max": "70 ans", "garanties": ["Deces", "PTIA"]},
            "option_2": {"age_max": "60 ans", "condition": "actif", "garanties": ["Deces", "PTIA", "ITT", "IPT"]},
            "option_3": {"age_max": "60 ans", "condition": "actif", "garanties": ["Deces", "PTIA", "ITT", "IPT", "IPP"]},
        },

        "red_flags": [
            "EXCLUSION DORSALE PLUS STRICTE : Hospitalisation > 7 JOURS requise (vs 4 jours chez Generali). Piege majeur.",
            "EXCLUSION PSYCHIQUE TRES STRICTE : Hospitalisation psychiatrique > 15 JOURS requise (vs 5 jours chez Generali). Extremement restrictif.",
            "TAUX INDEPENDANT DE LA SS : Le medecin-conseil de l'assureur evalue independamment de la Securite Sociale. Divergences frequentes et defavorables.",
            "ITT LIMITEE A 1095 JOURS : Plafond total d'indemnisation (3 ans).",
            "MI-TEMPS THERAPEUTIQUE = 50% pendant 6 mois seulement.",
            "PRETS MODULABLES : La mensualite prise en charge est celle de 6 mois avant l'arret (en cas de maladie). Si augmentation recente, elle n'est pas couverte.",
            "PAS DE GARANTIE PE : Groupama Gan Vie ne propose pas de garantie Perte d'Emploi dans ce contrat.",
            "RECHUTE > 2 MOIS = NOUVEL ARRET avec nouvelle franchise de 90 jours.",
            "AGE LIMITE 65 ANS pour ITT/IPT/IPP : Pret non couvert au-dela de cet age pour ces garanties.",
        ],

        "strategic_reading": {
            "what_to_check_first": [
                "Quelle option a ete souscrite (1, 2 ou 3) ?",
                "L'assure etait-il actif au jour du sinistre (conditionne l'acces aux options 2 et 3) ?",
                "L'affection releve-t-elle d'une exclusion dorsale (> 7 jours hospitalisation) ou psychique (> 15 jours) ?",
                "Le rachat des exclusions dorsales/psychiques a-t-il ete souscrit ?",
                "Le sinistre est-il survenu avant le 65e anniversaire ?",
            ],
            "what_strengthens_claim": [
                "Hospitalisation > 7 jours pour affection dorsale (leve l'exclusion Groupama)",
                "Hospitalisation psychiatrique > 15 jours (leve l'exclusion Groupama)",
                "Rachat total des exclusions souscrit a l'adhesion",
                "ITT faisant suite sans discontinuite a une ITT deja indemnisee (pas de nouvelle franchise pour IPT/IPP)",
                "Coherence entre diagnostic et definition contractuelle",
            ],
            "what_weakens_claim": [
                "Hospitalisation dorsale de 5-6 jours (insuffisant chez Groupama, suffisant chez Generali)",
                "Depression sans hospitalisation psychiatrique ou < 15 jours",
                "Taux SS reconnu mais non reconnu par medecin-conseil Groupama",
                "Pret modulable avec augmentation d'echeance recente avant sinistre",
            ],
            "common_disputes": [
                "Duree d'hospitalisation dorsale insuffisante pour lever l'exclusion",
                "Divergence taux fonctionnel/professionnel entre medecin traitant et medecin-conseil",
                "Refus d'indemnisation ITT pour depression sans hospitalisation psychiatrique suffisante",
                "Contestation du caractere total de l'incapacite (partiel vs total)",
            ],
        },

        "global_notes": [
            "Contrat emprunteur avec exclusions PLUS STRICTES que Generali sur le rachis (7 jours vs 4) et le psychique (15 jours vs 5).",
            "La Perte d'Emploi n'est pas proposee dans ce contrat.",
            "Le taux d'invalidite est croise entre fonctionnel et professionnel — le tableau de croisement determine le taux final.",
        ],
    },

    # =========================================================================
    # CNP ASSURANCES / BPCE VIE
    # =========================================================================
    "cnp_assurances": {
        "contract_name": "Senior - Garantie Deces seul (Formule 3) / Contrat 2252Y-2253Z",
        "assureur": "CNP Assurances et BPCE Vie (co-assureurs)",
        "type": "Assurance de groupe emprunteur",
        "reference": "2253Z (Senior) / 2252Y (Standard)",
        "version": "Janvier 2016",

        "guarantees": {
            "DECES": {
                "definition": "Remboursement sous forme de capital des prets de l'assure s'il decede avant son 75e anniversaire.",
                "conditions": ["Age 65-70 ans a l'adhesion (Formule 3 Senior)", "Residant fiscal en France (ou pays UE liste)"],
                "age_limite": "75 ans (Formule 3 Senior)",
                "franchise": "Aucune",
                "garantie_provisoire": "Accident uniquement, des la signature de la demande d'adhesion, jusqu'a prise d'effet",
                "mode_evaluation": "Capital restant du + interets courus entre derniere echeance et jour du deces",
                "exclusions": [
                    "Suicide < 1 an (sauf pret immo residence principale <= 120 000 euros)",
                    "Faute intentionnelle ou dolosive de l'assure (art. L.113-1)",
                    "Navigation aerienne (sauf vols reguliers avec pilote brevete et licence valide)",
                    "Participation active a des rixes (sauf legitime defense, assistance, devoir professionnel)",
                    "Guerre civile/etrangere, insurrection, emeute, attentat, terrorisme",
                    "Terrorisme avec matiere radioactive, chimique, bacteriologique ou virale",
                ],
                "pieces_justificatives": [
                    "Bulletin de deces original",
                    "Certificat medical (cause du deces, lien avec risques exclus ou non)",
                    "Si accident : PV police/gendarmerie, preuve du lien de causalite",
                    "Documents traduits en francais et certifies par representation legale francaise",
                ],
                "delai_declaration": "180 jours apres la survenance du sinistre",
            },
            "PTIA": {
                "definition": "L'assure est dans l'impossibilite totale et definitive de se livrer a toute occupation remuneree ET doit recourir de facon permanente a une tierce personne pour les 4 actes ordinaires de la vie (se laver, s'habiller, se nourrir, se deplacer). Doit survenir avant le 65e anniversaire.",
                "conditions": ["Conditions cumulatives : aucune activite remuneree + tierce personne permanente", "Avant 65 ans"],
                "age_limite": "65 ans",
                "franchise": "Aucune mentionnee",
                "seuils": "Tierce personne pour les 4 actes de la vie courante",
                "mode_evaluation": "Prestation identique au Deces (capital restant du)",
                "exclusions": [
                    "Exclusions Deces (sauf suicide)",
                    "Maladies/accidents volontaires, tentative suicide, mutilation, refus de se soigner",
                    "Usage stupefiants ou medicaments hors prescription",
                    "Competitions avec vehicules/embarcations a moteur",
                    "Explosions, degagements de chaleur, irradiations atomiques",
                    "PTIA survenant en PRERETRAITE OU RETRAITE, quelle qu'en soit la cause, y compris inaptitude",
                ],
                "pieces_justificatives": [
                    "Copie demande d'adhesion",
                    "Tableau d'amortissement a la date du sinistre",
                    "Copie offre ou contrat de pret",
                    "Attestation medicale (medecin traitant + assure)",
                    "Justificatif allocation tierce personne",
                    "Si accident : PV, preuve lien de causalite",
                    "Salaries/fonctionnaires : notification pension invalidite ou rente AT",
                ],
                "delai_declaration": "180 jours",
            },
            "ITT": {
                "definition": "Incapacite absolue, constatee medicalement, d'exercer son activite professionnelle ou toute recherche d'emploi (actifs) / d'exercer une quelconque activite (sans emploi). Avant 65 ans.",
                "conditions": ["Incapacite absolue et constante", "Constatation medicale", "Avant 65 ans"],
                "age_limite": "65 ans",
                "franchise": "90 jours d'incapacite totale et continue (non indemnises)",
                "franchise_rechute": "Non appliquee si reprise < 90 jours et rechute pour meme sinistre",
                "mode_evaluation": "Echeances de pret venant a echeance, selon quotite assuree",
                "plafonds_journaliers": "166 euros/jour (1 pret) ou 233 euros/jour (plusieurs prets)",
                "limitation_perte_revenu": "Prestations limitees a la perte de revenu (revenu reference - revenu remplacement)",
                "sans_activite": "Prise en charge limitee a 50% de la base de calcul",
                "exclusions": [
                    "Exclusions Deces + PTIA",
                    "AFFECTIONS PSYCHIATRIQUES (depression, anxio-depressif, psychotiques, nevrotiques) — SAUF hospitalisation > 15 JOURS continus OU mise sous tutelle/curatelle",
                    "ATTEINTE VERTEBRALE OU DISCALE (lumbago, lombalgie, sciatalgie) — SAUF intervention chirurgicale pendant l'incapacite",
                ],
                "pieces_justificatives": [
                    "Copie demande d'adhesion",
                    "Tableau d'amortissement",
                    "Copie offre ou contrat de pret",
                    "Attestation medicale (medecin traitant + assure)",
                    "Si accident : PV police/gendarmerie, preuve lien causal",
                    "Salaries : justificatifs remunerations, bulletins paie, bordereaux prestations sociales",
                    "TNS : certificat non radiation, certificats medicaux (validite 3 mois)",
                    "Sans activite : certificats medicaux d'incapacite totale",
                ],
                "cautions_garants": "Acquise uniquement si insolvabilite emprunteur principal ET preuve paiement regulier du pret depuis >= 3 mois",
            },
            "IPT": {
                "definition": "A la consolidation (ou au plus tard 3 ans apres debut ITT), le medecin-conseil fixe le taux d'incapacite permanente. Pour actifs : croisement taux fonctionnel + taux professionnel. Pour inactifs : taux fonctionnel seul.",
                "conditions": ["Consolidation (max 3 ans apres debut ITT)", "Taux >= 66%"],
                "age_limite": "65 ans",
                "franchise": "Identique ITT (90 jours)",
                "seuils": "Taux >= 66% (tableau croise fonctionnel/professionnel)",
                "mode_evaluation": "Identique ITT (echeances de pret, plafonds journaliers)",
                "exclusions": ["Identiques a l'ITT"],
                "note_importante": "Le taux fonctionnel est evalue selon le bareme du droit commun. Le taux professionnel selon le degre d'incapacite par rapport a la profession. Les deux sont croises dans un tableau. Si taux final < 66%, AUCUNE prestation n'est due.",
            },
            "INVALIDITE_AERAS": {
                "definition": "Garantie specifique proposee si les garanties ITT/IPT sont refusees pour raisons medicales. Conditions : interruption totale de toute activite + etat definitif et consolide + taux fonctionnel >= 70% + justification d'incapacite professionnelle. Avant 65 ans.",
                "conditions": [
                    "Garantie ITT/IPT refusee ou avec exclusion de pathologies",
                    "5 conditions cumulatives : interruption totale, etat definitif, taux fonctionnel >= 70%, incapacite professionnelle justifiee, avant 65 ans",
                ],
                "age_limite": "65 ans",
                "franchise": "Identique ITT (90 jours)",
                "seuils": "Taux fonctionnel >= 70% (bareme Pensions Civiles et Militaires)",
                "mode_evaluation": "Identique ITT/IPT",
                "exclusions": ["Identiques a l'ITT/IPT"],
                "note_importante": "Garantie de dernier recours pour les profils risque aggrave de sante. Conditions extremement strictes.",
            },
        },

        "red_flags": [
            "EXCLUSION PSYCHIQUE TRES STRICTE : Hospitalisation > 15 JOURS continus OU mise sous tutelle/curatelle. Le burnout, la depression ambulatoire ou l'anxiete chronique ne sont pas couverts.",
            "EXCLUSION VERTEBRALE : Seule l'intervention chirurgicale pendant l'incapacite leve l'exclusion. L'hospitalisation ne suffit PAS (contrairement a Generali et Groupama).",
            "PTIA EXCLUE EN PRERETRAITE/RETRAITE : Meme si l'assure est en PTIA reelle, s'il est en preretraite ou retraite (y compris pour inaptitude), AUCUNE indemnisation.",
            "PLAFONDS JOURNALIERS : 166 euros/jour (1 pret) ou 233 euros/jour (plusieurs prets). Si les echeances depassent ces montants, la difference reste a la charge de l'assure.",
            "LIMITATION PERTE DE REVENU : Les prestations ITT/IPT ne peuvent pas depasser la perte de revenu reelle. Si le revenu de remplacement (SS + employeur + prevoyance) couvre deja l'essentiel, les prestations sont reduites ou nulles.",
            "SANS ACTIVITE = 50% seulement de la base de calcul.",
            "CO-ASSUREURS SANS SOLIDARITE : CNP et BPCE Vie sont co-assureurs mais pas solidaires. Chacun ne repond que de sa quote-part.",
            "TAUX IPT : Si le taux croise (fonctionnel x professionnel) est < 66%, ZERO prestation. Pas de prorata. C'est tout ou rien.",
            "CAUTIONS/GARANTS : La garantie ITT n'est acquise que si l'emprunteur principal est insolvable ET que la caution paie depuis >= 3 mois.",
            "DELAI DECLARATION : 180 jours pour declarer le sinistre. Au-dela, risque de decheance partielle.",
        ],

        "strategic_reading": {
            "what_to_check_first": [
                "Quelle formule a ete souscrite (Standard 2252Y ou Senior 2253Z) ?",
                "L'assure est-il en preretraite/retraite (exclut la PTIA chez CNP) ?",
                "L'affection releve-t-elle d'une exclusion vertebrale (seule la chirurgie leve l'exclusion) ?",
                "L'affection releve-t-elle d'une exclusion psychiatrique (> 15 jours hospitalisation ou tutelle) ?",
                "Les plafonds journaliers (166/233 euros) couvrent-ils les echeances reelles du pret ?",
                "La perte de revenu reelle est-elle superieure aux echeances du pret ?",
            ],
            "what_strengthens_claim": [
                "Intervention chirurgicale pour affection vertebrale (unique moyen de lever l'exclusion CNP)",
                "Hospitalisation psychiatrique > 15 jours continus ou mise sous tutelle/curatelle",
                "Taux fonctionnel >= 70% pour la garantie Invalidite AERAS",
                "Coherence entre le diagnostic, le taux fonctionnel et le taux professionnel",
                "Perte de revenu documentee et superieure aux echeances",
            ],
            "what_weakens_claim": [
                "Hospitalisation vertebrale sans chirurgie (insuffisant chez CNP)",
                "Depression ambulatoire ou < 15 jours d'hospitalisation",
                "Taux croise < 66% pour l'IPT (pas de prorata, zero prestation)",
                "Revenus de remplacement couvrant deja la quasi-totalite du salaire",
                "Preretraite ou retraite au moment du sinistre PTIA",
            ],
            "common_disputes": [
                "Refus vertebral : hospitalisation mais pas de chirurgie — contestation sur la nature de l'exclusion",
                "Divergence entre le taux SS et le taux medecin-conseil CNP",
                "Exclusion PTIA pour preretraite alors que l'assure est reellement dependant",
                "Limitation des prestations pour 'perte de revenu insuffisante' alors que l'assure est en difficulte financiere",
                "Co-assurance : difficulte a identifier l'interlocuteur correct entre CNP et BPCE Vie",
            ],
        },

        "global_notes": [
            "Contrat emprunteur avec les exclusions les plus strictes des 3 assureurs sur le vertebral (chirurgie uniquement).",
            "Exclusion PTIA en preretraite/retraite = piege specifique a CNP, absent chez Generali et Groupama.",
            "La garantie Invalidite AERAS est un filet de securite pour les risques aggraves, mais ses conditions (taux >= 70%) sont tres elevees.",
            "Les plafonds journaliers (166/233 euros) peuvent etre insuffisants pour les prets importants.",
            "Pas de garantie PE dans ce contrat.",
        ],
    },
}


# =============================================================================
# TABLEAU COMPARATIF INTER-ASSUREURS
# =============================================================================

COMPARAISON_ASSUREURS = {
    "exclusion_dorsale": {
        "generali": "Hospitalisation >= 4 jours OU chirurgie",
        "groupama": "Hospitalisation > 7 jours OU chirurgie",
        "cnp": "Chirurgie UNIQUEMENT (hospitalisation ne suffit pas)",
        "commentaire": "CNP est le plus strict, Generali le plus souple. Point de litige frequent.",
    },
    "exclusion_psychique": {
        "generali": "Hospitalisation >= 5 jours en etablissement specialise",
        "groupama": "Hospitalisation psychiatrique > 15 jours",
        "cnp": "Hospitalisation > 15 jours continus OU tutelle/curatelle",
        "commentaire": "Generali est le plus souple (5 jours). Groupama et CNP tres restrictifs (15 jours).",
    },
    "age_limite_itt": {
        "generali": "70 ans",
        "groupama": "65 ans",
        "cnp": "65 ans",
        "commentaire": "Generali couvre 5 ans de plus pour l'ITT.",
    },
    "age_limite_deces": {
        "generali": "85 ans",
        "groupama": "80 ans",
        "cnp": "75 ans (Formule Senior)",
        "commentaire": "Generali offre la meilleure couverture deces dans le temps.",
    },
    "franchise_itt": {
        "generali": "90 jours",
        "groupama": "90 jours",
        "cnp": "90 jours",
        "commentaire": "Identique chez les 3 assureurs.",
    },
    "ptia_preretraite": {
        "generali": "Non exclue",
        "groupama": "Non exclue",
        "cnp": "EXCLUE (y compris inaptitude)",
        "commentaire": "Piege specifique a CNP. Point de vigilance majeur.",
    },
    "garantie_pe": {
        "generali": "Oui (franchise 180 jours, 75% echeances, max 12/24 mois)",
        "groupama": "Non proposee dans ce contrat",
        "cnp": "Non proposee dans ce contrat",
        "commentaire": "Seul Generali propose la Perte d'Emploi dans les contrats analyses.",
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_assurance_context(assureur: str = None, garantie: str = None) -> str:
    """
    Genere un contexte textuel exploitable par StrategiIA pour un litige assurantiel.

    Args:
        assureur: Nom de l'assureur (generali, groupama_gan_vie, cnp_assurances) ou None pour tous
        garantie: Type de garantie (ITT, ITP, IPT, IPP, PTIA, PE, DECES) ou None pour toutes

    Returns:
        Texte structure injectable dans le prompt StrategiIA
    """
    context_parts = []

    # Definitions normalisees
    if garantie and garantie.upper() in GARANTIES_DEFINITIONS:
        g = GARANTIES_DEFINITIONS[garantie.upper()]
        context_parts.append(f"DEFINITION NORMALISEE — {g['nom_complet']} ({garantie.upper()}) :")
        context_parts.append(f"  {g['description']}")
        context_parts.append(f"  Nature : {g['nature']}")
        context_parts.append(f"  Attention : {g['confusion_frequente']}")
        context_parts.append("")

    # Contexte assureur specifique
    assureurs_to_check = [assureur] if assureur else list(ASSURANCE_KNOWLEDGE.keys())

    for a_key in assureurs_to_check:
        a = ASSURANCE_KNOWLEDGE.get(a_key)
        if not a:
            continue

        context_parts.append(f"=== {a['assureur']} ({a['reference']}, {a['version']}) ===")

        if garantie and garantie.upper() in a.get("guarantees", {}):
            g = a["guarantees"][garantie.upper()]
            context_parts.append(f"Garantie {garantie.upper()} :")
            context_parts.append(f"  Definition : {g.get('definition', 'Non precisee')}")
            if g.get("conditions"):
                context_parts.append(f"  Conditions : {', '.join(g['conditions'])}")
            if g.get("seuils"):
                context_parts.append(f"  Seuils : {g['seuils']}")
            context_parts.append(f"  Age limite : {g.get('age_limite', 'Non precise')}")
            context_parts.append(f"  Franchise : {g.get('franchise', 'Non precisee')}")
            if g.get("duree_max") or g.get("duree_max_indemnisation"):
                context_parts.append(f"  Duree max : {g.get('duree_max') or g.get('duree_max_indemnisation')}")
            context_parts.append(f"  Mode evaluation : {g.get('mode_evaluation', 'Non precise')}")
            if g.get("exclusions"):
                context_parts.append("  Exclusions :")
                for exc in g["exclusions"]:
                    context_parts.append(f"    - {exc}")
            context_parts.append("")

        # Red flags
        if a.get("red_flags"):
            context_parts.append(f"Red flags {a['assureur']} :")
            for rf in a["red_flags"][:5]:
                context_parts.append(f"  - {rf}")
            context_parts.append("")

        # Strategic reading
        sr = a.get("strategic_reading", {})
        if sr.get("what_to_check_first"):
            context_parts.append("A verifier en priorite :")
            for item in sr["what_to_check_first"][:3]:
                context_parts.append(f"  - {item}")
        if sr.get("what_strengthens_claim"):
            context_parts.append("Ce qui renforce le recours :")
            for item in sr["what_strengthens_claim"][:3]:
                context_parts.append(f"  - {item}")
        if sr.get("what_weakens_claim"):
            context_parts.append("Ce qui fragilise le recours :")
            for item in sr["what_weakens_claim"][:3]:
                context_parts.append(f"  - {item}")
        context_parts.append("")

    # Comparaison inter-assureurs si pas d'assureur specifique
    if not assureur and garantie:
        gkey = garantie.upper()
        relevant_comparisons = {
            "ITT": ["exclusion_dorsale", "exclusion_psychique", "age_limite_itt", "franchise_itt"],
            "ITP": ["exclusion_dorsale", "exclusion_psychique"],
            "IPT": ["exclusion_dorsale", "exclusion_psychique", "age_limite_itt"],
            "IPP": ["exclusion_dorsale", "exclusion_psychique"],
            "PTIA": ["ptia_preretraite"],
            "PE": ["garantie_pe"],
            "DECES": ["age_limite_deces"],
        }
        comp_keys = relevant_comparisons.get(gkey, [])
        if comp_keys:
            context_parts.append("=== COMPARAISON INTER-ASSUREURS ===")
            for ck in comp_keys:
                comp = COMPARAISON_ASSUREURS.get(ck, {})
                if comp:
                    context_parts.append(f"{ck} :")
                    for assureur_name in ["generali", "groupama", "cnp"]:
                        if assureur_name in comp:
                            context_parts.append(f"  {assureur_name.upper()} : {comp[assureur_name]}")
                    if comp.get("commentaire"):
                        context_parts.append(f"  => {comp['commentaire']}")
            context_parts.append("")

    return "\n".join(context_parts)


def detect_insurer_from_text(text: str) -> dict:
    """
    Detecte automatiquement l'assureur mentionne dans un texte libre.
    Recherche simple par mots-cles, non bloquante.

    Args:
        text: Texte libre (situation, documents, etc.)

    Returns:
        {"assureur": "generali"|"groupama_gan_vie"|"cnp_assurances"|None,
         "confidence": "high"|"medium"|None,
         "matched_term": str|None}
    """
    if not text:
        return {"assureur": None, "confidence": None, "matched_term": None}

    text_lower = text.lower()

    # Patterns de detection par assureur — ordre : specifique d'abord
    INSURER_PATTERNS = {
        "generali": [
            "generali", "généréli", "generali vie", "generali iard",
            "contrat 7270", "contrat n°7270", "ddp7270",
        ],
        "groupama_gan_vie": [
            "groupama", "gan vie", "groupama gan", "gan assurance",
            "contrat 6092", "contrat 200140",
        ],
        "cnp_assurances": [
            "cnp", "cnp assurances", "bpce vie", "cnp/bpce",
            "contrat 2252", "contrat 2253", "2252y", "2253z",
        ],
    }

    matches = []
    for assureur_key, patterns in INSURER_PATTERNS.items():
        for pattern in patterns:
            if pattern in text_lower:
                # Confiance haute si nom exact ou reference contrat
                confidence = "high" if len(pattern) >= 6 else "medium"
                matches.append({
                    "assureur": assureur_key,
                    "confidence": confidence,
                    "matched_term": pattern,
                })
                break  # Un match par assureur suffit

    if not matches:
        return {"assureur": None, "confidence": None, "matched_term": None}

    # Si un seul assureur detecte : retourner directement
    if len(matches) == 1:
        return matches[0]

    # Si plusieurs : prendre celui avec la confiance la plus haute
    high_conf = [m for m in matches if m["confidence"] == "high"]
    if len(high_conf) == 1:
        return high_conf[0]

    # Ambigu : retourner le premier detecte (prudent)
    return matches[0]


def get_all_garantie_types() -> list:
    """Retourne la liste des types de garanties disponibles."""
    return list(GARANTIES_DEFINITIONS.keys())


def get_all_assureurs() -> list:
    """Retourne la liste des assureurs dans la base."""
    return [
        {"key": k, "name": v["assureur"], "contract": v["contract_name"]}
        for k, v in ASSURANCE_KNOWLEDGE.items()
    ]
