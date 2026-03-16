"""PDF guide generator using fpdf2 with DejaVu Sans Unicode font."""
from fpdf import FPDF
import io

FONT_DIR = "/usr/share/fonts/truetype/dejavu"

GUIDES = {
    "guide_mp": {
        "title": "Déclarer une maladie professionnelle",
        "subtitle": "Les étapes essentielles pour faire reconnaître votre maladie",
        "category": "AT/MP",
        "sections": [
            {
                "heading": "1. Obtenir un certificat médical initial (CMI)",
                "paragraphs": [
                    "Le certificat médical initial est la première pièce indispensable de votre dossier. Il doit être rédigé par votre médecin traitant ou un médecin spécialiste.",
                    "Ce document doit décrire précisément la pathologie constatée, sa localisation, les symptômes et leur lien possible avec votre activité professionnelle.",
                    "Le CMI doit mentionner la date de première constatation médicale de la maladie, qui servira de point de départ pour le calcul du délai de prise en charge.",
                    "Conseil : demandez à votre médecin d'être le plus précis possible dans la description des lésions et de leur localisation anatomique."
                ]
            },
            {
                "heading": "2. Remplir le formulaire Cerfa n° 60-3950",
                "paragraphs": [
                    "Le formulaire Cerfa n° 60-3950 (ou S6100) est le document officiel de déclaration de maladie professionnelle.",
                    "Vous devez y indiquer vos informations personnelles, la nature de la maladie, les conditions de travail et les expositions subies.",
                    "Joignez le certificat médical initial, ainsi que toute pièce justificative (attestation employeur, fiches de poste, etc.).",
                    "Conseil : conservez une copie de l'ensemble du dossier avant envoi."
                ]
            },
            {
                "heading": "3. Envoyer à votre CPAM sous 15 jours",
                "paragraphs": [
                    "La déclaration doit être adressée à votre Caisse Primaire d'Assurance Maladie (CPAM) dans un délai de 15 jours suivant la cessation du travail ou la constatation de la maladie.",
                    "Privilégiez un envoi en recommandé avec accusé de réception pour conserver une preuve de la date d'envoi.",
                    "La CPAM accusera réception de votre dossier et lancera l'instruction dans un délai de 3 mois."
                ]
            },
            {
                "heading": "4. Attendre la décision (3 mois maximum)",
                "paragraphs": [
                    "La CPAM dispose de 3 mois (renouvelables de 3 mois supplémentaires en cas de complexité) pour rendre sa décision.",
                    "Durant cette période, un médecin-conseil examinera votre dossier et pourra vous convoquer pour un examen médical.",
                    "Si votre maladie figure dans un tableau et que toutes les conditions sont réunies, la reconnaissance est de droit.",
                    "En cas de refus, vous disposez de 2 mois pour contester la décision auprès de la Commission de Recours Amiable (CRA) de la CPAM."
                ]
            },
            {
                "heading": "5. Documents à préparer",
                "paragraphs": [
                    "• Certificat médical initial (original)\n• Formulaire Cerfa rempli et signé\n• Copie de la carte Vitale\n• Attestation d'emploi ou fiches de paie\n• Fiches de poste ou description du travail\n• Éventuels rapports d'expertise ou bilans complémentaires",
                ]
            }
        ]
    },
    "guide_expertise": {
        "title": "Se préparer à une expertise médicale",
        "subtitle": "Conseils pratiques pour aborder sereinement cette étape décisive",
        "category": "Expertises",
        "sections": [
            {
                "heading": "1. Rassembler vos documents médicaux",
                "paragraphs": [
                    "Réunissez l'ensemble de votre dossier médical : comptes rendus de consultations, résultats d'examens (IRM, radiographies, analyses), ordonnances et certificats.",
                    "Organisez-les par ordre chronologique pour permettre à l'expert de suivre l'évolution de votre pathologie.",
                    "N'oubliez pas les documents relatifs à votre activité professionnelle : fiches de poste, attestations d'exposition, etc."
                ]
            },
            {
                "heading": "2. Lister vos symptômes au quotidien",
                "paragraphs": [
                    "Préparez une liste détaillée de vos symptômes, leur fréquence, leur intensité et leur impact sur votre vie quotidienne.",
                    "Notez les activités que vous ne pouvez plus réaliser ou qui sont devenues pénibles : port de charges, station debout prolongée, mouvements répétitifs, etc.",
                    "Mentionnez également les conséquences psychologiques : troubles du sommeil, anxiété, isolement social."
                ]
            },
            {
                "heading": "3. Préparer une chronologie",
                "paragraphs": [
                    "Établissez un historique clair de votre parcours : date de début des symptômes, premiers traitements, arrêts de travail, interventions chirurgicales.",
                    "Cette chronologie permet à l'expert de comprendre la progression de votre état de santé et d'évaluer les séquelles.",
                    "Incluez les dates des événements professionnels marquants (changement de poste, exposition à un risque spécifique)."
                ]
            },
            {
                "heading": "4. Pendant l'expertise",
                "paragraphs": [
                    "Soyez honnête et précis dans vos réponses. Ne minimisez pas vos douleurs, mais n'exagérez pas non plus.",
                    "Vous avez le droit d'être accompagné par votre médecin traitant ou un médecin-conseil de votre choix.",
                    "Demandez à l'expert de noter vos observations si vous estimez qu'un élément important a été omis.",
                    "Conseil : notez le nom de l'expert, la durée de l'examen et les tests réalisés pour vos archives personnelles."
                ]
            }
        ]
    },
    "guide_mdph": {
        "title": "Constituer un dossier MDPH",
        "subtitle": "Formulaire, documents requis et astuces pour un dossier solide",
        "category": "MDPH",
        "sections": [
            {
                "heading": "1. Le formulaire Cerfa n° 15692*01",
                "paragraphs": [
                    "Le formulaire unique de demande MDPH permet de solliciter plusieurs droits simultanément : RQTH, AAH, CMI, PCH, orientation professionnelle.",
                    "Remplissez-le soigneusement en détaillant vos difficultés au quotidien. Plus vous êtes précis, mieux le médecin évaluera vos besoins.",
                    "La partie « projet de vie » est essentielle : décrivez votre situation, vos besoins et vos attentes en termes concrets."
                ]
            },
            {
                "heading": "2. Le certificat médical MDPH",
                "paragraphs": [
                    "Le certificat médical (Cerfa n° 15695*01) doit être rempli par votre médecin. Il est valable 12 mois.",
                    "Demandez à votre médecin de détailler les diagnostics, les traitements en cours, les limitations fonctionnelles et le pronostic.",
                    "Joignez les comptes rendus de spécialistes, les bilans fonctionnels (kinésithérapeute, ergothérapeute) et les résultats d'examens complémentaires."
                ]
            },
            {
                "heading": "3. Les pièces justificatives",
                "paragraphs": [
                    "• Photocopie recto-verso de la carte d'identité\n• Justificatif de domicile de moins de 3 mois\n• Photo d'identité\n• Attestation de jugement de protection juridique (si applicable)\n• Dernier avis d'imposition\n• Justificatifs d'emploi ou Pôle Emploi",
                ]
            },
            {
                "heading": "4. Conseils pour un dossier solide",
                "paragraphs": [
                    "Rédigez un projet de vie détaillé : décrivez une journée type, les difficultés rencontrées, l'aide dont vous avez besoin.",
                    "Ajoutez des témoignages de proches ou de professionnels de santé qui vous suivent.",
                    "Envoyez le dossier en recommandé et conservez une copie complète. Le délai de traitement est de 4 à 6 mois.",
                    "En cas de refus, vous disposez de 2 mois pour exercer un recours auprès du tribunal judiciaire."
                ]
            }
        ]
    },
    "guide_recours": {
        "title": "Contester un refus d'indemnisation",
        "subtitle": "Vos droits et voies de recours face à une décision défavorable",
        "category": "Recours",
        "sections": [
            {
                "heading": "1. Demander les motifs par écrit",
                "paragraphs": [
                    "Dès réception d'une décision de refus, demandez par courrier recommandé les motifs détaillés de la décision.",
                    "L'organisme (CPAM, MDPH, assureur) est tenu de vous communiquer les raisons précises du refus.",
                    "Analysez ces motifs attentivement : ils orientent votre stratégie de contestation."
                ]
            },
            {
                "heading": "2. Vérifier la conformité légale",
                "paragraphs": [
                    "Vérifiez que la procédure a été respectée : délais, notification, droit de consultation du dossier.",
                    "Tout vice de procédure peut constituer un motif d'annulation de la décision.",
                    "Consultez un professionnel si vous avez un doute sur la régularité de la procédure."
                ]
            },
            {
                "heading": "3. Saisir le médiateur ou la commission de recours",
                "paragraphs": [
                    "Pour un refus CPAM : saisissez la Commission de Recours Amiable (CRA) dans les 2 mois suivant la notification.",
                    "Pour un refus MDPH : exercez un recours administratif préalable obligatoire (RAPO) auprès de la MDPH.",
                    "Pour un refus d'assurance : contactez le médiateur de l'assurance (gratuit) après avoir épuisé les voies internes."
                ]
            },
            {
                "heading": "4. L'action judiciaire",
                "paragraphs": [
                    "Si le recours amiable échoue, vous pouvez saisir le tribunal judiciaire (pôle social) pour les litiges CPAM.",
                    "Pour les litiges MDPH, le tribunal est également compétent après le RAPO.",
                    "L'aide juridictionnelle peut être accordée si vos ressources sont insuffisantes.",
                    "Conseil : un avocat spécialisé en droit de la sécurité sociale améliorera significativement vos chances de succès."
                ]
            }
        ]
    },
    "guide_ipp": {
        "title": "Comprendre le taux d'IPP",
        "subtitle": "Comment le taux est fixé et ses impacts sur votre indemnisation",
        "category": "AT/MP",
        "sections": [
            {
                "heading": "1. Qu'est-ce que l'IPP ?",
                "paragraphs": [
                    "L'Incapacité Permanente Partielle (IPP) est un taux, exprimé en pourcentage, qui mesure les séquelles définitives d'un accident du travail ou d'une maladie professionnelle.",
                    "Ce taux est fixé par le médecin-conseil de la Sécurité sociale à la date de consolidation (stabilisation de l'état de santé).",
                    "Il prend en compte : la nature de l'infirmité, l'état général, les facultés physiques et mentales, les aptitudes professionnelles et l'âge."
                ]
            },
            {
                "heading": "2. Indemnisation selon le taux",
                "paragraphs": [
                    "Taux < 10 % : Vous recevez un capital forfaitaire unique. Exemples : 1 % = 452 €, 5 % = 2 222 €, 9 % = 5 012 €.",
                    "Taux ≥ 10 % : Vous recevez une rente viagère (trimestrielle ou mensuelle) calculée sur votre salaire de référence.",
                    "Le calcul de la rente utilise le « taux utile » : la moitié du taux jusqu'à 50 %, puis la totalité au-delà. Exemple : un taux de 60 % donne un taux utile de 35 % (25 + 10)."
                ]
            },
            {
                "heading": "3. Contestation du taux",
                "paragraphs": [
                    "Si vous estimez que le taux fixé est insuffisant, vous pouvez le contester dans un délai de 2 mois.",
                    "Le recours passe par la CRA (Commission de Recours Amiable), puis le tribunal judiciaire.",
                    "Une contre-expertise médicale peut être demandée pour réévaluer vos séquelles.",
                    "Important : faites-vous accompagner par un médecin-conseil de victime pour maximiser vos chances."
                ]
            },
            {
                "heading": "4. Exemples concrets",
                "paragraphs": [
                    "• Canal carpien bilatéral (Tableau 57C) : taux habituel 5 à 15 %\n• Surdité professionnelle (Tableau 42) : taux habituel 10 à 30 %\n• Asthme professionnel (Tableau 66) : taux habituel 5 à 40 %\n• Lombalgie chronique (Tableau 98) : taux habituel 5 à 20 %\n• Atteinte de l'épaule (Tableau 57A) : taux habituel 8 à 25 %",
                ]
            }
        ]
    },
    "guide_assurance": {
        "title": "Activer sa protection juridique",
        "subtitle": "Identifier et activer votre protection juridique (PJ)",
        "category": "Assurances",
        "sections": [
            {
                "heading": "1. Identifier votre protection juridique",
                "paragraphs": [
                    "La protection juridique (PJ) est souvent incluse dans vos contrats d'assurance : habitation, auto, carte bancaire, mutuelle santé.",
                    "Vérifiez l'ensemble de vos contrats pour repérer les clauses de protection juridique. Elle est parfois présente sans que vous le sachiez.",
                    "La PJ couvre généralement les frais d'avocat, d'expertise et de procédure judiciaire."
                ]
            },
            {
                "heading": "2. Déclarer le litige",
                "paragraphs": [
                    "Contactez votre assureur PJ par courrier recommandé en décrivant le litige : nature du conflit, parties en cause, montant en jeu.",
                    "Joignez les pièces justificatives principales : décision de refus, courriers échangés, documents médicaux.",
                    "L'assureur dispose de 15 jours pour accuser réception et vous informer de la prise en charge ou du refus."
                ]
            },
            {
                "heading": "3. Le libre choix de l'avocat",
                "paragraphs": [
                    "Vous avez le droit de choisir librement votre avocat, même si l'assureur vous en propose un.",
                    "L'assureur doit prendre en charge les honoraires dans la limite du plafond prévu au contrat.",
                    "Privilégiez un avocat spécialisé en droit de la sécurité sociale ou en droit du dommage corporel."
                ]
            },
            {
                "heading": "4. Plafonds et limites",
                "paragraphs": [
                    "Vérifiez les plafonds de prise en charge : ils varient généralement entre 10 000 € et 50 000 € selon les contrats.",
                    "Attention aux franchises et aux délais de carence (souvent 3 mois après la souscription).",
                    "Certains litiges sont exclus : vérifiez les exclusions spécifiques de votre contrat (litiges fiscaux, divorces, etc.)."
                ]
            }
        ]
    }
}


def generate_guide_pdf(guide_id: str) -> bytes | None:
    """Generate a PDF for a given guide ID with DejaVu Sans Unicode font."""
    guide = GUIDES.get(guide_id)
    if not guide:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=25)

    # Register DejaVu Sans Unicode font
    pdf.add_font("DejaVu", "", f"{FONT_DIR}/DejaVuSans.ttf")
    pdf.add_font("DejaVu", "B", f"{FONT_DIR}/DejaVuSans-Bold.ttf")

    pdf.add_page()

    # Header bar
    pdf.set_fill_color(26, 26, 46)
    pdf.rect(0, 0, 210, 40, "F")
    pdf.set_text_color(212, 164, 74)
    pdf.set_font("DejaVu", "B", 18)
    pdf.set_y(10)
    pdf.cell(0, 10, "Stratégie & Expertise Santé", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 6, "www.strategie-expertise-sante.fr", align="C", new_x="LMARGIN", new_y="NEXT")

    # Category badge
    pdf.set_y(50)
    pdf.set_text_color(212, 164, 74)
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(0, 6, guide["category"].upper(), new_x="LMARGIN", new_y="NEXT")

    # Title
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("DejaVu", "B", 22)
    pdf.multi_cell(0, 10, guide["title"])
    pdf.ln(2)

    # Subtitle
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(0, 7, guide["subtitle"])
    pdf.ln(4)

    # Separator line
    pdf.set_draw_color(212, 164, 74)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    # Sections
    for section in guide["sections"]:
        pdf.set_text_color(26, 26, 46)
        pdf.set_font("DejaVu", "B", 13)
        pdf.multi_cell(0, 8, section["heading"])
        pdf.ln(3)

        pdf.set_text_color(60, 60, 60)
        pdf.set_font("DejaVu", "", 10)
        for para in section["paragraphs"]:
            pdf.multi_cell(0, 6, para)
            pdf.ln(3)
        pdf.ln(3)

    # Footer
    pdf.ln(5)
    pdf.set_draw_color(212, 164, 74)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_text_color(130, 130, 130)
    pdf.set_font("DejaVu", "", 8)
    pdf.multi_cell(0, 5, "Ce guide est fourni à titre informatif par Stratégie & Expertise Santé. Il ne constitue pas un avis juridique ou médical. Pour un accompagnement personnalisé, contactez-nous sur notre site web.")

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
