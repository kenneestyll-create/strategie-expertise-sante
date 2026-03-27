"""PDF guide generator — Premium S.E.S identity (Noir #1A1A1A / Or #C9A84C / Ivoire).

Uses fpdf2 with DejaVu Sans for full Unicode support (French accents).
"""
from fpdf import FPDF
import io
import os
from datetime import datetime
import random

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
_LOGO_PATH = os.path.join(os.path.dirname(__file__), "shield_logo.png")

# ── Premium palette (identical to pdf.py) ──
_BLACK = (26, 26, 26)
_GOLD = (201, 168, 76)
_GOLD_LIGHT = (218, 195, 130)
_IVORY = (250, 248, 243)
_DARK_TEXT = (35, 35, 35)
_BODY_TEXT = (55, 55, 55)
_MUTED = (130, 125, 118)
_LIGHT_LINE = (220, 215, 205)

LM = 16
RM = 16
CW = 210 - LM - RM


def _report_number():
    year = datetime.now().year
    seq = random.randint(10000, 99999)
    return f"SES-GUIDE-{year}-{seq}"


GUIDES = {
    "guide_mp": {
        "title": "Déclarer une maladie professionnelle",
        "subtitle": "Feuille de route complète : de la constatation à l'indemnisation",
        "category": "AT/MP",
        "sections": [
            {
                "heading": "1. Vérifier l'éligibilité de votre maladie",
                "paragraphs": [
                    "Avant toute démarche, identifiez si votre pathologie figure dans l'un des tableaux des maladies professionnelles du Code de la Sécurité sociale. Ces tableaux définissent trois critères : la maladie elle-même, le délai de prise en charge et la liste des travaux susceptibles de la provoquer.",
                    "Si votre maladie figure dans un tableau et que TOUTES les conditions sont réunies (délai, exposition, travaux), la reconnaissance est automatique — c'est la « présomption d'origine ».",
                    "Si une condition manque, ou si la maladie n'est pas dans un tableau, votre dossier sera transmis au CRRMP (Comité Régional de Reconnaissance des Maladies Professionnelles). Vous devrez alors prouver un lien « direct et essentiel » entre votre travail et la maladie.",
                    "Exemples courants : canal carpien (Tableau 57C), surdité (Tableau 42), asthme professionnel (Tableau 66), lombalgie (Tableau 98), atteinte de l'épaule (Tableau 57A), troubles psychiques (hors tableau — CRRMP obligatoire)."
                ]
            },
            {
                "heading": "2. Obtenir le certificat médical initial (CMI)",
                "paragraphs": [
                    "Le CMI est la pièce maîtresse de votre dossier. Il doit être rédigé par votre médecin traitant ou un spécialiste (rhumatologue, pneumologue, ORL…).",
                    "Le document doit préciser : le diagnostic exact, la localisation anatomique, les symptômes constatés, la date de première constatation médicale, et le lien supposé avec l'activité professionnelle.",
                    "Points clés à vérifier : le CMI doit être daté, signé, et mentionner explicitement le numéro du tableau de MP si applicable. Demandez à votre médecin de joindre les résultats d'examens (IRM, EMG, radiographies) pour renforcer le dossier.",
                    "Attention : la date du CMI fixe le point de départ du délai de prise en charge. Ne tardez pas à le faire établir."
                ]
            },
            {
                "heading": "3. Constituer et envoyer le dossier complet",
                "paragraphs": [
                    "Remplissez le formulaire Cerfa n° 60-3950 (S6100), disponible sur ameli.fr ou en agence CPAM. Joignez systématiquement :",
                    "• Certificat médical initial (original ou copie)\n• Formulaire Cerfa rempli, daté et signé\n• Copie recto-verso de la carte Vitale\n• Attestation(s) de salaire des 12 derniers mois\n• Fiches de paie couvrant la période d'exposition\n• Fiche(s) de poste détaillant les tâches et expositions\n• Résultats d'examens médicaux complémentaires\n• Tout document prouvant l'exposition (photos, rapports CHSCT, mesures de bruit…)",
                    "Délai : la déclaration doit parvenir à la CPAM dans les 15 jours suivant la cessation du travail ou la constatation. Toutefois, le droit à réparation est ouvert pendant 2 ans à compter de la connaissance du lien maladie-travail.",
                    "Mode d'envoi : toujours en recommandé avec accusé de réception. Conservez une copie complète du dossier et l'accusé de réception."
                ]
            },
            {
                "heading": "4. La phase d'instruction par la CPAM",
                "paragraphs": [
                    "Depuis la réforme, la CPAM dispose de 120 jours francs (environ 4 mois) pour statuer, à compter de la réception du dossier complet.",
                    "Pendant l'instruction : le médecin-conseil vous convoquera probablement pour un examen. Préparez-vous comme pour une expertise (voir notre guide dédié). La CPAM peut aussi demander des informations à votre employeur.",
                    "Au bout de 100 jours maximum, la CPAM met le dossier à disposition des parties (vous et l'employeur) pour consultation. Vous avez alors 10 jours francs pour formuler vos observations écrites.",
                    "Si le dossier est transmis au CRRMP (cas hors tableau ou conditions incomplètes), comptez 4 à 6 mois supplémentaires. Au total : 8 à 10 mois."
                ]
            },
            {
                "heading": "5. Décision et indemnisation",
                "paragraphs": [
                    "En cas de reconnaissance : vous bénéficiez de la prise en charge à 100 % des soins liés à la MP, d'indemnités journalières majorées (90 % du salaire brut pendant 30 jours, puis 66,66 %), et d'une indemnité en capital ou d'une rente selon votre taux d'IPP.",
                    "Indemnités journalières : elles sont versées dès le premier jour d'arrêt (pas de délai de carence, contrairement à la maladie ordinaire). Elles sont exonérées de CSG/CRDS.",
                    "Barème d'indemnité en capital (IPP < 10 %, montants 2025) : 1 % = 479 €, 3 % = 1 280 €, 5 % = 2 222 €, 7 % = 3 424 €, 9 % = 4 795 €. Ces montants sont versés en une seule fois.",
                    "Rente viagère (IPP ≥ 10 %) : calculée sur le salaire annuel brut des 12 derniers mois × le taux utile. Le taux utile = moitié du taux jusqu'à 50 %, puis totalité au-delà. Exemple : IPP 30 %, salaire 25 000 € → taux utile 15 % → rente annuelle 3 750 €.",
                    "En cas de refus : vous avez 2 mois pour saisir la CRA (Commission de Recours Amiable). Si la CRA rejette aussi, vous pouvez saisir le tribunal judiciaire (pôle social) dans un nouveau délai de 2 mois."
                ]
            }
        ]
    },
    "guide_expertise": {
        "title": "Se préparer à une expertise médicale",
        "subtitle": "Check-list complète pour maximiser vos chances lors de l'examen",
        "category": "Expertises",
        "sections": [
            {
                "heading": "1. Avant l'expertise : constituer votre dossier",
                "paragraphs": [
                    "Rassemblez la totalité de vos documents médicaux par ordre chronologique : comptes rendus de consultations, résultats d'examens (IRM, scanner, EMG, radiographies), ordonnances, bilans biologiques, courriers entre médecins.",
                    "Préparez un résumé chronologique sur une feuille A4 : dates clés (début des symptômes, premiers arrêts, traitements, interventions chirurgicales, rechutes). Ce document sera très apprécié par l'expert.",
                    "Listez vos doléances : décrivez précisément chaque douleur ou gêne, sa fréquence, son intensité (échelle 1 à 10), les gestes impossibles ou douloureux, et l'impact sur votre vie quotidienne.",
                    "Incluez les conséquences psychologiques : troubles du sommeil, anxiété, dépression, isolement social, impact sur la vie familiale et sociale."
                ]
            },
            {
                "heading": "2. Documents professionnels à apporter",
                "paragraphs": [
                    "• Fiches de poste détaillant les tâches réalisées\n• Attestations d'exposition (bruit, produits chimiques, postures…)\n• Planning type montrant la répétitivité des gestes\n• Photos du poste de travail si possible\n• Rapports du CHSCT ou du médecin du travail\n• Fiches de données de sécurité des produits manipulés",
                    "Ces documents permettent à l'expert de comprendre le lien entre votre travail et votre pathologie. Sans eux, l'expertise repose uniquement sur vos déclarations."
                ]
            },
            {
                "heading": "3. Le jour de l'expertise : conseils pratiques",
                "paragraphs": [
                    "Vous avez le droit d'être accompagné par votre médecin traitant ou un médecin-conseil de victime. C'est fortement recommandé : il pourra poser des questions techniques et veiller à ce que tous les éléments soient notés.",
                    "Soyez honnête et précis. Décrivez vos douleurs TELLES QU'ELLES SONT au quotidien, sans minimiser ni exagérer. L'expert est entraîné à détecter les incohérences.",
                    "Prenez vos traitements habituels avant de venir — l'expertise doit évaluer votre état « traité ». N'arrêtez pas vos médicaments pour paraître plus atteint.",
                    "Notez le nom de l'expert, la durée de l'examen, les tests réalisés et les questions posées. Ces notes vous seront utiles en cas de contestation du rapport."
                ]
            },
            {
                "heading": "4. Pendant l'examen clinique",
                "paragraphs": [
                    "L'expert mesurera vos amplitudes articulaires, testera votre force musculaire, évaluera vos réflexes et votre sensibilité. Il peut aussi vous demander de réaliser des gestes du quotidien.",
                    "Si un mouvement vous fait mal, dites-le immédiatement et précisément (localisation, type de douleur, intensité). Ne serrez pas les dents en silence.",
                    "Si l'expert vous pose des questions sur votre vie quotidienne, soyez concret : « Je ne peux plus porter mes courses au-delà de 2 kg », « Je me réveille 3 fois par nuit à cause de la douleur ».",
                    "Vérifiez avant de partir que l'expert a bien noté vos principales doléances. Vous pouvez lui demander de relire les points essentiels."
                ]
            },
            {
                "heading": "5. Après l'expertise : que faire ?",
                "paragraphs": [
                    "Le rapport d'expertise sera transmis à l'organisme demandeur (CPAM, assureur, tribunal) dans un délai de quelques semaines à quelques mois.",
                    "Vous avez le droit de demander une copie du rapport. Lisez-le attentivement et comparez avec vos notes prises le jour de l'examen.",
                    "Si le rapport comporte des erreurs factuelles ou si le taux proposé vous semble insuffisant, vous pouvez demander une contre-expertise ou contester la décision (voir notre guide « Contester un refus »).",
                    "Conservez l'intégralité du dossier (convocation, rapport, notes personnelles) : il pourra servir en cas d'aggravation future."
                ]
            }
        ]
    },
    "guide_mdph": {
        "title": "Constituer un dossier MDPH",
        "subtitle": "Guide pratique complet : formulaires, documents, projet de vie et recours",
        "category": "MDPH",
        "sections": [
            {
                "heading": "1. Comprendre les droits que vous pouvez demander",
                "paragraphs": [
                    "Un seul formulaire MDPH permet de solliciter plusieurs droits simultanément. Identifiez ceux qui vous concernent :",
                    "• RQTH (Reconnaissance Qualité Travailleur Handicapé) : accès à des aides à l'emploi, obligation d'emploi, aménagements de poste\n• AAH (Allocation Adultes Handicapés) : aide financière si taux d'incapacité ≥ 50 % (montant max. 1 016 € /mois en 2025). Attribuée si taux ≥ 80 % ou entre 50 et 79 % avec restriction substantielle d'accès à l'emploi\n• CMI (Carte Mobilité Inclusion) : priorité, invalidité ou stationnement\n• PCH (Prestation de Compensation du Handicap) : aide humaine, technique, aménagement du logement\n• Orientation professionnelle : ESAT, entreprise adaptée, formation",
                    "Conseil : cochez toutes les cases pertinentes dès la première demande. Ajouter un droit ultérieurement nécessite un nouveau dossier complet."
                ]
            },
            {
                "heading": "2. Remplir le formulaire Cerfa n° 15692*01",
                "paragraphs": [
                    "Téléchargeable sur monparcourshandicap.gouv.fr ou disponible à votre MDPH. Vous pouvez aussi déposer en ligne sur mdphenligne.cnsa.fr.",
                    "Les parties essentielles à soigner :",
                    "• Partie A : Identité — vérifiez que les informations correspondent exactement à votre pièce d'identité.\n• Partie B : Vie quotidienne — décrivez très concrètement vos limitations (mobilité, communication, orientation dans le temps et l'espace).\n• Partie E : Projet de vie — c'est la partie la plus importante (voir section dédiée ci-dessous).\n• Partie F : Demandes précises — cochez chaque droit souhaité."
                ]
            },
            {
                "heading": "3. Le certificat médical Cerfa n° 15695*01",
                "paragraphs": [
                    "Ce certificat doit être daté de moins de 6 mois au moment du dépôt (attention aux délais de traitement !). Il est rempli par votre médecin traitant ou spécialiste.",
                    "Le médecin doit détailler : les diagnostics posés, l'historique de la maladie, les traitements en cours et leur efficacité, les limitations fonctionnelles observées, et le pronostic d'évolution.",
                    "Astuce : joignez en complément tous les comptes rendus de spécialistes, bilans de kinésithérapie/ergothérapie, et résultats d'examens. Plus le dossier médical est étoffé, plus l'évaluation du taux d'incapacité sera juste."
                ]
            },
            {
                "heading": "4. Rédiger un projet de vie percutant",
                "paragraphs": [
                    "Le projet de vie est lu par l'équipe pluridisciplinaire qui évalue votre dossier. C'est votre opportunité de montrer la réalité de votre quotidien.",
                    "Structure recommandée :\n1. Décrivez une journée type : réveil difficile, douleurs au lever, aide nécessaire pour la toilette/habillage, difficultés de transport…\n2. Listez ce que vous ne pouvez PLUS faire : porter des charges, rester debout, vous concentrer longtemps…\n3. Expliquez l'impact sur votre emploi : arrêts fréquents, reclassement impossible, licenciement pour inaptitude…\n4. Mentionnez les aides dont vous avez besoin : aide humaine, aménagement du domicile, fauteuil roulant…\n5. Formulez vos souhaits : retrouver un emploi adapté, accéder à une formation, obtenir une aide financière…",
                    "Conseil : faites relire votre projet de vie par une assistante sociale ou une association de patients. Un témoignage de proche peut aussi être joint."
                ]
            },
            {
                "heading": "5. Pièces justificatives et envoi",
                "paragraphs": [
                    "Checklist des pièces à joindre :\n• Formulaire Cerfa 15692*01 rempli et signé\n• Certificat médical Cerfa 15695*01 (< 6 mois)\n• Photocopie recto-verso carte d'identité ou titre de séjour\n• Justificatif de domicile de moins de 3 mois\n• Photo d'identité récente\n• Dernier avis d'imposition\n• Justificatifs d'emploi ou attestation Pôle Emploi / France Travail\n• Comptes rendus médicaux et bilans complémentaires\n• Attestation de jugement de protection juridique (si applicable)",
                    "Envoi : recommandé avec AR à la MDPH de votre département, ou dépôt en ligne sur mdphenligne.cnsa.fr.",
                    "Délai de traitement : environ 4 mois. En cas de refus, vous disposez de 2 mois pour un RAPO (Recours Administratif Préalable Obligatoire) auprès de la MDPH, puis tribunal judiciaire si nécessaire."
                ]
            }
        ]
    },
    "guide_recours": {
        "title": "Contester un refus d'indemnisation",
        "subtitle": "Stratégie de recours étape par étape : amiable, médiateur et judiciaire",
        "category": "Recours",
        "sections": [
            {
                "heading": "1. Analyser la décision de refus",
                "paragraphs": [
                    "Dès réception de la notification, lisez attentivement les motifs du refus. Ils sont obligatoirement mentionnés. Les motifs courants sont : conditions du tableau non remplies (délai de prise en charge dépassé, travaux non listés), dossier médical insuffisant, ou pas de lien direct reconnu.",
                    "Demandez immédiatement par courrier recommandé la communication complète de votre dossier (rapport du médecin-conseil, avis du CRRMP le cas échéant, enquête administrative). Vous y avez droit.",
                    "Vérifiez la régularité de la procédure : la notification a-t-elle été envoyée dans les délais ? Avez-vous été informé de la mise à disposition du dossier ? Avez-vous pu formuler vos observations ? Un vice de procédure peut justifier l'annulation de la décision."
                ]
            },
            {
                "heading": "2. Le recours amiable : CRA ou RAPO",
                "paragraphs": [
                    "Pour un refus CPAM (AT/MP) : saisissez la Commission de Recours Amiable (CRA) dans les 2 mois suivant la notification. Adressez un courrier recommandé AR à votre CPAM, avec l'objet « Recours devant la CRA », en joignant la décision contestée et vos arguments.",
                    "Renforcez votre dossier : joignez de nouveaux éléments médicaux (avis d'un spécialiste, résultats d'examens complémentaires, attestations de collègues sur vos conditions de travail).",
                    "Pour un refus MDPH : le RAPO (Recours Administratif Préalable Obligatoire) est à adresser à la MDPH dans les 2 mois. C'est un passage obligé avant toute action judiciaire.",
                    "Délai de réponse : la CRA dispose de 2 mois. L'absence de réponse vaut rejet implicite, ouvrant la voie au recours judiciaire."
                ]
            },
            {
                "heading": "3. Le médiateur et l'expertise amiable",
                "paragraphs": [
                    "Pour les litiges avec un assureur (PJ, prévoyance) : saisissez d'abord le service réclamation de l'assureur, puis le médiateur de l'assurance (mediation-assurance.org). La médiation est gratuite et suspend les délais de prescription.",
                    "Expertise médicale amiable : vous pouvez demander une contre-expertise par un médecin-conseil de victime (à vos frais, 300 à 800 €, mais souvent pris en charge par votre protection juridique). Son rapport peut inverser la décision.",
                    "Conseil : ne négligez jamais la phase amiable. Elle est souvent plus rapide (2-4 mois) et moins coûteuse qu'une action judiciaire. Plus de 40 % des recours amiables aboutissent favorablement."
                ]
            },
            {
                "heading": "4. L'action judiciaire",
                "paragraphs": [
                    "Si le recours amiable échoue, vous pouvez saisir le tribunal judiciaire (pôle social) dans un délai de 2 mois après la décision de la CRA ou du RAPO.",
                    "La saisine se fait par requête (formulaire Cerfa ou courrier libre) déposée au greffe du tribunal. Vous pouvez vous représenter seul, mais un avocat spécialisé est fortement recommandé.",
                    "Aide juridictionnelle : si vos revenus sont modestes, vous pouvez bénéficier de l'aide juridictionnelle (prise en charge totale ou partielle des frais d'avocat). Renseignez-vous auprès du bureau d'aide juridictionnelle de votre tribunal.",
                    "Le juge peut ordonner une expertise judiciaire (médecin expert indépendant désigné par le tribunal). Cette expertise est déterminante : préparez-la minutieusement (voir notre guide expertise).",
                    "Délai moyen d'un jugement : 12 à 18 mois. Le jugement est susceptible d'appel dans un délai d'un mois."
                ]
            },
            {
                "heading": "5. Récapitulatif des délais à retenir",
                "paragraphs": [
                    "• Notification de refus → CRA/RAPO : 2 mois\n• CRA/RAPO → Réponse : 2 mois (silence = rejet)\n• Rejet CRA/RAPO → Tribunal judiciaire : 2 mois\n• Jugement → Appel : 1 mois\n• Délai total moyen (amiable + judiciaire) : 18 à 24 mois",
                    "Important : tous les délais sont de rigueur. Un recours hors délai est irrecevable. Notez les dates dès réception de chaque notification et agissez rapidement."
                ]
            }
        ]
    },
    "guide_ipp": {
        "title": "Comprendre le taux d'IPP",
        "subtitle": "Barème, calcul de la rente et stratégies de contestation",
        "category": "AT/MP",
        "sections": [
            {
                "heading": "1. Qu'est-ce que l'IPP ?",
                "paragraphs": [
                    "L'Incapacité Permanente Partielle (IPP) est un pourcentage mesurant les séquelles définitives d'un accident du travail ou d'une maladie professionnelle, fixé à la date de consolidation (stabilisation de votre état de santé).",
                    "Le taux est fixé par le médecin-conseil de la CPAM en tenant compte de : la nature de l'infirmité, l'état général du patient, l'âge, les facultés physiques et mentales, les aptitudes et qualifications professionnelles.",
                    "Le barème indicatif d'invalidité (annexe du Code de la Sécurité sociale) sert de référence, mais le médecin-conseil dispose d'une marge d'appréciation. Un coefficient professionnel peut être ajouté si la maladie impacte spécifiquement votre capacité à exercer votre métier."
                ]
            },
            {
                "heading": "2. Indemnisation : capital ou rente ?",
                "paragraphs": [
                    "Taux d'IPP < 10 % → Indemnité en capital versée en une seule fois :",
                    "• 1 % = 479,55 € | 2 % = 780,34 € | 3 % = 1 139,74 €\n• 4 % = 1 798,22 € | 5 % = 2 222,11 € | 6 % = 2 748,72 €\n• 7 % = 3 352,61 € | 8 % = 4 034,31 € | 9 % = 4 794,83 €\n(Montants au 1er avril 2025, revalorisés chaque année)",
                    "Taux d'IPP ≥ 10 % → Rente viagère calculée ainsi :\n• Salaire annuel de référence = salaire brut des 12 derniers mois (min. 21 327,85 €, plafond 170 622,80 €)\n• Taux utile = (taux IPP ÷ 2) pour la partie ≤ 50 %, + totalité pour la partie > 50 %\n• Rente annuelle = salaire de référence × taux utile",
                    "Exemples concrets :\n• IPP 15 %, salaire 25 000 € → taux utile 7,5 % → rente 1 875 €/an (156 €/mois)\n• IPP 30 %, salaire 30 000 € → taux utile 15 % → rente 4 500 €/an (375 €/mois)\n• IPP 60 %, salaire 30 000 € → taux utile 35 % (25+10) → rente 10 500 €/an (875 €/mois)",
                    "La rente est versée trimestriellement si IPP < 50 %, mensuellement si ≥ 50 %. Elle est exonérée d'impôt sur le revenu et de CSG/CRDS."
                ]
            },
            {
                "heading": "3. Taux habituels par pathologie",
                "paragraphs": [
                    "• Canal carpien bilatéral (Tableau 57C) : 5 à 15 %\n• Épicondylite (Tableau 57B) : 3 à 10 %\n• Tendinopathie de l'épaule (Tableau 57A) : 8 à 25 %\n• Surdité professionnelle (Tableau 42) : 10 à 30 %\n• Asthme professionnel (Tableau 66) : 5 à 40 %\n• Lombalgie chronique (Tableau 98) : 5 à 20 %\n• Mésothéliome (Tableau 30) : 67 à 100 %\n• Troubles psychiques (hors tableau) : 10 à 25 %",
                    "Ces fourchettes sont indicatives. Le taux réel dépend de la gravité des séquelles, des examens complémentaires et de l'impact professionnel."
                ]
            },
            {
                "heading": "4. Contester le taux d'IPP",
                "paragraphs": [
                    "Si vous estimez le taux insuffisant, saisissez la CMRA (Commission Médicale de Recours Amiable) dans les 2 mois suivant la notification. Adressez un courrier recommandé AR à votre CPAM.",
                    "Procédure CMRA : la commission (2 médecins indépendants, hors médecin-conseil initial) examine votre dossier. Vous recevez le rapport médical du médecin-conseil et disposez de 20 jours pour transmettre vos observations (via votre médecin-conseil de victime).",
                    "La CMRA rend sa décision sous 4 mois. Si elle vous est défavorable, vous pouvez saisir le tribunal judiciaire dans les 2 mois. Le juge ordonnera une expertise judiciaire.",
                    "Conseil clé : faites-vous accompagner par un médecin-conseil de victime (200 à 500 € la consultation). Son expertise technique fait souvent la différence, tant devant la CMRA que devant le tribunal."
                ]
            },
            {
                "heading": "5. Révision et aggravation",
                "paragraphs": [
                    "Si votre état s'aggrave après la consolidation, vous pouvez demander une révision du taux d'IPP. La demande est faite auprès de la CPAM, accompagnée d'un certificat médical d'aggravation.",
                    "La révision peut être demandée à tout moment, sans limitation de durée. Le nouveau taux s'applique à compter de la date de la demande.",
                    "En cas de rechute (reprise de la maladie initiale), la CPAM ouvre un nouveau volet d'indemnisation avec prise en charge des soins et éventuellement de nouvelles indemnités journalières."
                ]
            }
        ]
    },
    "guide_assurance": {
        "title": "Activer sa protection juridique",
        "subtitle": "Trouver, déclarer et utiliser votre protection juridique (PJ) efficacement",
        "category": "Assurances",
        "sections": [
            {
                "heading": "1. Où se cache votre protection juridique ?",
                "paragraphs": [
                    "La protection juridique est souvent incluse (parfois sans que vous le sachiez) dans vos contrats suivants :",
                    "• Assurance habitation (multirisque) — la plus fréquente\n• Assurance auto ou moto\n• Carte bancaire haut de gamme (Visa Premier, Gold Mastercard…)\n• Mutuelle santé ou prévoyance\n• Contrat spécifique de protection juridique\n• Assurance emprunteur (crédit immobilier)",
                    "Action : rassemblez TOUS vos contrats d'assurance et vérifiez les conditions particulières. Cherchez les termes « protection juridique », « défense-recours », « assistance juridique ». Contactez chaque assureur par téléphone si nécessaire.",
                    "Certaines PJ couvrent spécifiquement les litiges de sécurité sociale et de droit du travail — vérifiez le périmètre exact."
                ]
            },
            {
                "heading": "2. Déclarer le litige à votre assureur PJ",
                "paragraphs": [
                    "La déclaration doit être faite par courrier recommandé avec AR. Indiquez clairement : la nature du litige, les parties adverses, le montant en jeu, la chronologie des faits.",
                    "Pièces à joindre : décision de refus contestée, courriers échangés avec l'organisme, certificats médicaux principaux, tout document utile.",
                    "L'assureur dispose de 15 jours pour accuser réception et vous informer de la prise en charge ou du refus. En cas de refus de prise en charge, demandez les motifs par écrit et vérifiez qu'ils sont conformes au contrat.",
                    "Attention au délai de carence : certains contrats excluent les litiges nés dans les 3 premiers mois après la souscription. Vérifiez la date du fait générateur du litige par rapport à la date de souscription."
                ]
            },
            {
                "heading": "3. Le libre choix de l'avocat",
                "paragraphs": [
                    "C'est un droit légal (article L. 127-3 du Code des assurances) : vous choisissez librement votre avocat, même si l'assureur vous en propose un de son réseau.",
                    "Conseil : privilégiez un avocat spécialisé en droit de la sécurité sociale ou en droit du dommage corporel. Demandez des références et vérifiez son expérience sur les contentieux AT/MP.",
                    "L'assureur PJ prend en charge les honoraires d'avocat dans la limite du plafond contractuel. Demandez un devis à l'avocat choisi et transmettez-le à l'assureur AVANT de signer la convention d'honoraires.",
                    "Si les honoraires dépassent le plafond PJ, la différence reste à votre charge. Négociez avec l'avocat un forfait ou vérifiez votre éligibilité à l'aide juridictionnelle en complément."
                ]
            },
            {
                "heading": "4. Plafonds, exclusions et limites",
                "paragraphs": [
                    "Plafonds de prise en charge habituels : de 10 000 € à 50 000 € selon les contrats (souvent 15 000 à 20 000 € pour un contrat standard). Ce montant couvre les honoraires d'avocat, les frais d'expertise et les frais de procédure.",
                    "Exclusions fréquentes : litiges fiscaux, litiges liés au divorce ou à la famille, litiges avec l'assureur PJ lui-même, amendes pénales, litiges commerciaux professionnels.",
                    "Franchise : certains contrats prévoient une franchise (montant minimal non remboursé). Vérifiez ce point dans les conditions particulières.",
                    "Seuil d'intervention : certains contrats ne couvrent que les litiges dépassant un montant minimum (souvent 500 € ou 1 000 €). En deçà, l'assureur peut refuser d'intervenir."
                ]
            },
            {
                "heading": "5. Maximiser l'utilisation de votre PJ",
                "paragraphs": [
                    "Cumulez les PJ : si vous avez plusieurs contrats avec PJ (habitation + mutuelle par exemple), vous pouvez solliciter les deux. La prise en charge se cumule.",
                    "Demandez une consultation juridique gratuite : la plupart des PJ offrent un accès téléphonique à un juriste. Utilisez ce service dès le début pour valider votre stratégie.",
                    "Gardez une trace écrite de TOUTES vos communications avec l'assureur PJ (courriers, emails, notes d'appels téléphoniques avec date et nom de l'interlocuteur).",
                    "Si l'assureur refuse de prendre en charge votre litige ou conteste la stratégie proposée par votre avocat, vous pouvez demander un arbitrage par un tiers désigné (article L. 127-4 du Code des assurances)."
                ]
            }
        ]
    }
}


class PremiumGuidePDF(FPDF):
    """Premium-styled PDF matching the S.E.S identity standard."""

    def __init__(self, guide_data, report_num, gen_date, year):
        super().__init__()
        self._guide = guide_data
        self._report_num = report_num
        self._gen_date = gen_date
        self._year = year

        self.set_auto_page_break(auto=True, margin=18)
        self.set_left_margin(LM)
        self.set_right_margin(RM)

        # Register Unicode-capable font
        self.add_font("DejaVu", "", f"{FONT_DIR}/DejaVuSans.ttf")
        self.add_font("DejaVu", "B", f"{FONT_DIR}/DejaVuSans-Bold.ttf")

    def header(self):
        # Dark header band
        self.set_fill_color(*_BLACK)
        self.rect(0, 0, 210, 22, "F")

        # Gold accent line
        self.set_fill_color(*_GOLD)
        self.rect(0, 22, 210, 0.6, "F")

        # Shield logo
        if os.path.isfile(_LOGO_PATH):
            self.image(_LOGO_PATH, LM, 3, 9, 9)
            text_x = LM + 11
        else:
            text_x = LM

        # Brand name
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVu", "B", 10)
        self.set_xy(text_x, 4)
        self.cell(80, 5, "Stratégie & Expertise Santé")

        # Subtitle
        self.set_font("DejaVu", "", 6)
        self.set_text_color(*_GOLD_LIGHT)
        self.set_xy(text_x, 10)
        self.cell(80, 4, "PIONNIER EN FRANCE")

        # Right side: date & report number
        self.set_font("DejaVu", "", 6.5)
        self.set_text_color(180, 180, 180)
        self.set_xy(-RM - 60, 5)
        self.cell(60, 4, self._gen_date, align="R")
        self.set_xy(-RM - 60, 10)
        self.set_text_color(*_GOLD_LIGHT)
        self.cell(60, 4, self._report_num, align="R")

        self.set_xy(LM, 26)

    def footer(self):
        self.set_y(-14)
        # Gold line
        self.set_draw_color(*_GOLD)
        self.set_line_width(0.3)
        self.line(LM, self.get_y(), 210 - RM, self.get_y())
        self.ln(2)
        self.set_font("DejaVu", "", 5.5)
        self.set_text_color(*_MUTED)
        self.cell(
            CW, 4,
            f"\u00a9 {self._year} Stratégie & Expertise Santé  \u2014  strategie-expertise-sante.fr  \u2014  Document confidentiel",
            align="C",
        )


def generate_guide_pdf(guide_id: str) -> bytes | None:
    """Generate a premium-styled PDF for a given guide ID."""
    guide = GUIDES.get(guide_id)
    if not guide:
        return None

    gen_date = datetime.now().strftime("%d/%m/%Y")
    year = datetime.now().year
    report_num = _report_number()

    pdf = PremiumGuidePDF(guide, report_num, gen_date, year)
    pdf.add_page()

    # ── Category badge ──
    y = pdf.get_y() + 2
    pdf.set_fill_color(*_IVORY)
    pdf.rect(LM, y, CW, 8, "F")
    pdf.set_fill_color(*_GOLD)
    pdf.rect(LM, y, 2, 8, "F")
    pdf.set_xy(LM + 5, y + 1.5)
    pdf.set_font("DejaVu", "B", 7)
    pdf.set_text_color(*_GOLD)
    pdf.cell(CW - 5, 5, guide["category"].upper())
    y += 12

    # ── Title ──
    pdf.set_xy(LM, y)
    pdf.set_text_color(*_BLACK)
    pdf.set_font("DejaVu", "B", 16)
    pdf.multi_cell(CW, 8, guide["title"])
    y = pdf.get_y() + 2

    # ── Subtitle ──
    pdf.set_xy(LM, y)
    pdf.set_text_color(*_BODY_TEXT)
    pdf.set_font("DejaVu", "", 9)
    pdf.multi_cell(CW, 5.5, guide["subtitle"])
    y = pdf.get_y() + 3

    # ── Gold separator ──
    pdf.set_draw_color(*_GOLD)
    pdf.set_line_width(0.4)
    pdf.line(LM, y, LM + 50, y)
    y += 8
    pdf.set_xy(LM, y)

    # ── Sections ──
    for section in guide["sections"]:
        # Check space for heading
        if pdf.get_y() > 250:
            pdf.add_page()

        sy = pdf.get_y()

        # Gold left accent bar
        pdf.set_fill_color(*_GOLD)
        pdf.rect(LM, sy, 2.5, 6, "F")

        pdf.set_x(LM + 6)
        pdf.set_text_color(*_BLACK)
        pdf.set_font("DejaVu", "B", 10.5)
        pdf.multi_cell(CW - 6, 6, section["heading"])
        pdf.ln(3)

        # Paragraphs
        pdf.set_text_color(*_BODY_TEXT)
        pdf.set_font("DejaVu", "", 8.5)
        for para in section["paragraphs"]:
            # Handle bullet lists (lines starting with •)
            lines = para.split("\n")
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("•"):
                    # Bullet point with gold dot
                    bx = LM + 5
                    by_pos = pdf.get_y() + 1.5
                    pdf.set_fill_color(*_GOLD)
                    pdf.rect(bx, by_pos, 1.2, 1.2, "F")
                    pdf.set_x(LM + 8)
                    pdf.set_font("DejaVu", "", 8.5)
                    pdf.set_text_color(*_BODY_TEXT)
                    pdf.multi_cell(CW - 10, 4.2, stripped[1:].strip())
                    pdf.ln(0.5)
                elif stripped and stripped[0].isdigit() and ". " in stripped[:4]:
                    # Numbered item
                    bx = LM + 5
                    by_pos = pdf.get_y() + 1.5
                    pdf.set_fill_color(*_GOLD)
                    pdf.rect(bx, by_pos, 1.2, 1.2, "F")
                    pdf.set_x(LM + 8)
                    pdf.set_font("DejaVu", "", 8.5)
                    pdf.set_text_color(*_BODY_TEXT)
                    pdf.multi_cell(CW - 10, 4.2, stripped)
                    pdf.ln(0.5)
                else:
                    pdf.set_x(LM)
                    pdf.set_font("DejaVu", "", 8.5)
                    pdf.set_text_color(*_BODY_TEXT)
                    pdf.multi_cell(CW, 4.5, stripped)
                    pdf.ln(1)
            pdf.ln(2)

        # Subtle separator between sections
        sep_y = pdf.get_y()
        pdf.set_draw_color(*_LIGHT_LINE)
        pdf.set_line_width(0.2)
        pdf.line(LM + 15, sep_y, LM + CW - 15, sep_y)
        pdf.ln(5)

    # ── Closing signature ──
    space = pdf.h - 18 - pdf.get_y()
    if space < 50:
        pdf.add_page()

    pdf.ln(4)

    # Signature box
    box_y = pdf.get_y()
    pdf.set_fill_color(*_IVORY)
    pdf.rect(LM, box_y, CW, 28, "F")
    pdf.set_fill_color(*_GOLD)
    pdf.rect(LM, box_y, 2.5, 28, "F")

    pdf.set_xy(LM + 7, box_y + 5)
    pdf.set_font("DejaVu", "", 8.5)
    pdf.set_text_color(*_BODY_TEXT)
    pdf.multi_cell(CW - 14, 4.5,
        "Ce guide est fourni par Stratégie & Expertise Santé à titre informatif. "
        "Il ne constitue pas un avis juridique ou médical personnalisé. "
        "Pour un accompagnement adapté à votre situation, contactez-nous."
    )

    pdf.set_xy(LM + 7, box_y + 20)
    pdf.set_font("DejaVu", "B", 8.5)
    pdf.set_text_color(*_GOLD)
    pdf.cell(CW - 14, 5, "Stratégie & Expertise Santé \u2014 Votre bouclier.")

    pdf.ln(10)

    # Final gold separator
    sep_final = pdf.get_y()
    pdf.set_draw_color(*_GOLD)
    pdf.set_line_width(0.3)
    pdf.line(65, sep_final, 145, sep_final)
    pdf.ln(5)

    # Brand closing
    pdf.set_font("DejaVu", "B", 9)
    pdf.set_text_color(*_GOLD)
    pdf.cell(CW, 5, "Vous n'êtes plus seul face à votre combat.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "B", 9)
    pdf.cell(CW, 5, "Désormais, S.E.S est votre bouclier.", align="C")

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
