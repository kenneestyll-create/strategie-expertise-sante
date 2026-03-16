"""PDF guide generator using fpdf2."""
from fpdf import FPDF
import io

GUIDES = {
    "guide_mp": {
        "title": "Declarer une maladie professionnelle",
        "subtitle": "Les etapes essentielles pour faire reconnaitre votre maladie",
        "category": "AT/MP",
        "sections": [
            {
                "heading": "1. Obtenir un certificat medical initial (CMI)",
                "paragraphs": [
                    "Le certificat medical initial est la premiere piece indispensable de votre dossier. Il doit etre redige par votre medecin traitant ou un medecin specialiste.",
                    "Ce document doit decrire precisement la pathologie constatee, sa localisation, les symptomes et leur lien possible avec votre activite professionnelle.",
                    "Le CMI doit mentionner la date de premiere constatation medicale de la maladie, qui servira de point de depart pour le calcul du delai de prise en charge.",
                    "Conseil : demandez a votre medecin d'etre le plus precis possible dans la description des lesions et de leur localisation anatomique."
                ]
            },
            {
                "heading": "2. Remplir le formulaire Cerfa n 60-3950",
                "paragraphs": [
                    "Le formulaire Cerfa n 60-3950 (ou S6100) est le document officiel de declaration de maladie professionnelle.",
                    "Vous devez y indiquer vos informations personnelles, la nature de la maladie, les conditions de travail et les expositions subies.",
                    "Joignez le certificat medical initial, ainsi que toute piece justificative (attestation employeur, fiches de poste, etc.).",
                    "Conseil : conservez une copie de l'ensemble du dossier avant envoi."
                ]
            },
            {
                "heading": "3. Envoyer a votre CPAM sous 15 jours",
                "paragraphs": [
                    "La declaration doit etre adressee a votre Caisse Primaire d'Assurance Maladie (CPAM) dans un delai de 15 jours suivant la cessation du travail ou la constatation de la maladie.",
                    "Privilegiez un envoi en recommande avec accuse de reception pour conserver une preuve de la date d'envoi.",
                    "La CPAM accusera reception de votre dossier et lancera l'instruction dans un delai de 3 mois."
                ]
            },
            {
                "heading": "4. Attendre la decision (3 mois maximum)",
                "paragraphs": [
                    "La CPAM dispose de 3 mois (renouvelables de 3 mois supplementaires en cas de complexite) pour rendre sa decision.",
                    "Durant cette periode, un medecin-conseil examinera votre dossier et pourra vous convoquer pour un examen medical.",
                    "Si votre maladie figure dans un tableau et que toutes les conditions sont reunies, la reconnaissance est de droit.",
                    "En cas de refus, vous disposez de 2 mois pour contester la decision aupres de la Commission de Recours Amiable (CRA) de la CPAM."
                ]
            },
            {
                "heading": "5. Documents a preparer",
                "paragraphs": [
                    "- Certificat medical initial (original)\n- Formulaire Cerfa rempli et signe\n- Copie de la carte Vitale\n- Attestation d'emploi ou fiches de paie\n- Fiches de poste ou description du travail\n- Eventuels rapports d'expertise ou bilans complementaires",
                ]
            }
        ]
    },
    "guide_expertise": {
        "title": "Se preparer a une expertise medicale",
        "subtitle": "Conseils pratiques pour aborder sereinement cette etape decisive",
        "category": "Expertises",
        "sections": [
            {
                "heading": "1. Rassembler vos documents medicaux",
                "paragraphs": [
                    "Reunissez l'ensemble de votre dossier medical : comptes rendus de consultations, resultats d'examens (IRM, radiographies, analyses), ordonnances et certificats.",
                    "Organisez-les par ordre chronologique pour permettre a l'expert de suivre l'evolution de votre pathologie.",
                    "N'oubliez pas les documents relatifs a votre activite professionnelle : fiches de poste, attestations d'exposition, etc."
                ]
            },
            {
                "heading": "2. Lister vos symptomes au quotidien",
                "paragraphs": [
                    "Preparez une liste detaillee de vos symptomes, leur frequence, leur intensite et leur impact sur votre vie quotidienne.",
                    "Notez les activites que vous ne pouvez plus realiser ou qui sont devenues penibles : port de charges, station debout prolongee, mouvements repetitifs, etc.",
                    "Mentionnez egalement les consequences psychologiques : troubles du sommeil, anxiete, isolement social."
                ]
            },
            {
                "heading": "3. Preparer une chronologie",
                "paragraphs": [
                    "Etablissez un historique clair de votre parcours : date de debut des symptomes, premiers traitements, arrets de travail, interventions chirurgicales.",
                    "Cette chronologie permet a l'expert de comprendre la progression de votre etat de sante et d'evaluer les sequelles.",
                    "Incluez les dates des evenements professionnels marquants (changement de poste, exposition a un risque specifique)."
                ]
            },
            {
                "heading": "4. Pendant l'expertise",
                "paragraphs": [
                    "Soyez honnete et precis dans vos reponses. Ne minimisez pas vos douleurs, mais n'exagerez pas non plus.",
                    "Vous avez le droit d'etre accompagne par votre medecin traitant ou un medecin-conseil de votre choix.",
                    "Demandez a l'expert de noter vos observations si vous estimez qu'un element important a ete omis.",
                    "Conseil : notez le nom de l'expert, la duree de l'examen et les tests realises pour vos archives personnelles."
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
                "heading": "1. Le formulaire Cerfa n 15692*01",
                "paragraphs": [
                    "Le formulaire unique de demande MDPH permet de solliciter plusieurs droits simultanement : RQTH, AAH, CMI, PCH, orientation professionnelle.",
                    "Remplissez-le soigneusement en detaillant vos difficultes au quotidien. Plus vous etes precis, mieux le medecin evaluera vos besoins.",
                    "La partie 'projet de vie' est essentielle : decrivez votre situation, vos besoins et vos attentes en termes concrets."
                ]
            },
            {
                "heading": "2. Le certificat medical MDPH",
                "paragraphs": [
                    "Le certificat medical (Cerfa n 15695*01) doit etre rempli par votre medecin. Il est valable 12 mois.",
                    "Demandez a votre medecin de detailler les diagnostics, les traitements en cours, les limitations fonctionnelles et le pronostic.",
                    "Joignez les comptes rendus de specialistes, les bilans fonctionnels (kinesitherapeute, ergotherapeute) et les resultats d'examens complementaires."
                ]
            },
            {
                "heading": "3. Les pieces justificatives",
                "paragraphs": [
                    "- Photocopie recto-verso de la carte d'identite\n- Justificatif de domicile de moins de 3 mois\n- Photo d'identite\n- Attestation de jugement de protection juridique (si applicable)\n- Dernier avis d'imposition\n- Justificatifs d'emploi ou Pole Emploi",
                ]
            },
            {
                "heading": "4. Conseils pour un dossier solide",
                "paragraphs": [
                    "Redigez un projet de vie detaille : decrivez une journee type, les difficultes rencontrees, l'aide dont vous avez besoin.",
                    "Ajoutez des temoignages de proches ou de professionnels de sante qui vous suivent.",
                    "Envoyez le dossier en recommande et conservez une copie complete. Le delai de traitement est de 4 a 6 mois.",
                    "En cas de refus, vous disposez de 2 mois pour exercer un recours aupres du tribunal judiciaire."
                ]
            }
        ]
    },
    "guide_recours": {
        "title": "Contester un refus d'indemnisation",
        "subtitle": "Vos droits et voies de recours face a une decision defavorable",
        "category": "Recours",
        "sections": [
            {
                "heading": "1. Demander les motifs par ecrit",
                "paragraphs": [
                    "Des reception d'une decision de refus, demandez par courrier recommande les motifs detailles de la decision.",
                    "L'organisme (CPAM, MDPH, assureur) est tenu de vous communiquer les raisons precises du refus.",
                    "Analysez ces motifs attentivement : ils orientent votre strategie de contestation."
                ]
            },
            {
                "heading": "2. Verifier la conformite legale",
                "paragraphs": [
                    "Verifiez que la procedure a ete respectee : delais, notification, droit de consultation du dossier.",
                    "Tout vice de procedure peut constituer un motif d'annulation de la decision.",
                    "Consultez un professionnel si vous avez un doute sur la regularite de la procedure."
                ]
            },
            {
                "heading": "3. Saisir le mediateur ou la commission de recours",
                "paragraphs": [
                    "Pour un refus CPAM : saisissez la Commission de Recours Amiable (CRA) dans les 2 mois suivant la notification.",
                    "Pour un refus MDPH : exercez un recours administratif prealable obligatoire (RAPO) aupres de la MDPH.",
                    "Pour un refus d'assurance : contactez le mediateur de l'assurance (gratuit) apres avoir epuise les voies internes."
                ]
            },
            {
                "heading": "4. L'action judiciaire",
                "paragraphs": [
                    "Si le recours amiable echoue, vous pouvez saisir le tribunal judiciaire (pole social) pour les litiges CPAM.",
                    "Pour les litiges MDPH, le tribunal est egalement competent apres le RAPO.",
                    "L'aide juridictionnelle peut etre accordee si vos ressources sont insuffisantes.",
                    "Conseil : un avocat specialise en droit de la securite sociale ameliorera significativement vos chances de succes."
                ]
            }
        ]
    },
    "guide_ipp": {
        "title": "Comprendre le taux d'IPP",
        "subtitle": "Comment le taux est fixe et ses impacts sur votre indemnisation",
        "category": "AT/MP",
        "sections": [
            {
                "heading": "1. Qu'est-ce que l'IPP ?",
                "paragraphs": [
                    "L'Incapacite Permanente Partielle (IPP) est un taux, exprime en pourcentage, qui mesure les sequelles definitives d'un accident du travail ou d'une maladie professionnelle.",
                    "Ce taux est fixe par le medecin-conseil de la Securite sociale a la date de consolidation (stabilisation de l'etat de sante).",
                    "Il prend en compte : la nature de l'infirmite, l'etat general, les facultes physiques et mentales, les aptitudes professionnelles et l'age."
                ]
            },
            {
                "heading": "2. Indemnisation selon le taux",
                "paragraphs": [
                    "Taux < 10% : Vous recevez un capital forfaitaire unique. Exemples : 1% = 452 euros, 5% = 2 222 euros, 9% = 5 012 euros.",
                    "Taux >= 10% : Vous recevez une rente viagere (trimestrielle ou mensuelle) calculee sur votre salaire de reference.",
                    "Le calcul de la rente utilise le 'taux utile' : la moitie du taux jusqu'a 50%, puis la totalite au-dela. Exemple : un taux de 60% donne un taux utile de 35% (25 + 10)."
                ]
            },
            {
                "heading": "3. Contestation du taux",
                "paragraphs": [
                    "Si vous estimez que le taux fixe est insuffisant, vous pouvez le contester dans un delai de 2 mois.",
                    "Le recours passe par la CRA (Commission de Recours Amiable), puis le tribunal judiciaire.",
                    "Une contre-expertise medicale peut etre demandee pour reevaluer vos sequelles.",
                    "Important : faites-vous accompagner par un medecin-conseil de victime pour maximiser vos chances."
                ]
            },
            {
                "heading": "4. Exemples concrets",
                "paragraphs": [
                    "- Canal carpien bilateral (Tableau 57C) : taux habituel 5 a 15%\n- Surdite professionnelle (Tableau 42) : taux habituel 10 a 30%\n- Asthme professionnel (Tableau 66) : taux habituel 5 a 40%\n- Lombalgie chronique (Tableau 98) : taux habituel 5 a 20%\n- Atteinte de l'epaule (Tableau 57A) : taux habituel 8 a 25%",
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
                    "La protection juridique (PJ) est souvent incluse dans vos contrats d'assurance : habitation, auto, carte bancaire, mutuelle sante.",
                    "Verifiez l'ensemble de vos contrats pour reperer les clauses de protection juridique. Elle est parfois presente sans que vous le sachiez.",
                    "La PJ couvre generalement les frais d'avocat, d'expertise et de procedure judiciaire."
                ]
            },
            {
                "heading": "2. Declarer le litige",
                "paragraphs": [
                    "Contactez votre assureur PJ par courrier recommande en decrivant le litige : nature du conflit, parties en cause, montant en jeu.",
                    "Joignez les pieces justificatives principales : decision de refus, courriers echanges, documents medicaux.",
                    "L'assureur dispose de 15 jours pour accuser reception et vous informer de la prise en charge ou du refus."
                ]
            },
            {
                "heading": "3. Le libre choix de l'avocat",
                "paragraphs": [
                    "Vous avez le droit de choisir librement votre avocat, meme si l'assureur vous en propose un.",
                    "L'assureur doit prendre en charge les honoraires dans la limite du plafond prevu au contrat.",
                    "Privilegiez un avocat specialise en droit de la securite sociale ou en droit du dommage corporel."
                ]
            },
            {
                "heading": "4. Plafonds et limites",
                "paragraphs": [
                    "Verifiez les plafonds de prise en charge : ils varient generalement entre 10 000 et 50 000 euros selon les contrats.",
                    "Attention aux franchises et aux delais de carence (souvent 3 mois apres la souscription).",
                    "Certains litiges sont exclus : verifiez les exclusions specifiques de votre contrat (litiges fiscaux, divorces, etc.)."
                ]
            }
        ]
    }
}


def generate_guide_pdf(guide_id: str) -> bytes | None:
    """Generate a PDF for a given guide ID. Returns bytes or None."""
    guide = GUIDES.get(guide_id)
    if not guide:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()

    # Header bar
    pdf.set_fill_color(26, 26, 46)
    pdf.rect(0, 0, 210, 40, "F")
    pdf.set_text_color(212, 164, 74)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_y(10)
    pdf.cell(0, 10, "Strategie & Expertise Sante", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 6, "www.strategie-expertise-sante.fr", align="C", new_x="LMARGIN", new_y="NEXT")

    # Category badge
    pdf.set_y(50)
    pdf.set_text_color(212, 164, 74)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, guide["category"].upper(), new_x="LMARGIN", new_y="NEXT")

    # Title
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "B", 22)
    pdf.multi_cell(0, 10, guide["title"])
    pdf.ln(2)

    # Subtitle
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("Helvetica", "I", 12)
    pdf.multi_cell(0, 7, guide["subtitle"])
    pdf.ln(4)

    # Separator
    pdf.set_draw_color(212, 164, 74)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    # Sections
    for section in guide["sections"]:
        pdf.set_text_color(26, 26, 46)
        pdf.set_font("Helvetica", "B", 13)
        pdf.multi_cell(0, 8, section["heading"])
        pdf.ln(3)

        pdf.set_text_color(60, 60, 60)
        pdf.set_font("Helvetica", "", 10)
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
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 5, "Ce guide est fourni a titre informatif par Strategie & Expertise Sante. Il ne constitue pas un avis juridique ou medical. Pour un accompagnement personnalise, contactez-nous sur notre site web.")

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
