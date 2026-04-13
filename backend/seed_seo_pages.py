"""Seed 5 SEO guide pages for Phase 1."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

PAGES = [
    {
        "slug": "refus-mdph-aah-que-faire",
        "title": "Refus MDPH pour l'AAH : que faire concrètement pour débloquer la situation ?",
        "meta_description": "Votre demande d'AAH a été refusée par la MDPH ? Découvrez les étapes concrètes pour contester cette décision et faire valoir vos droits.",
        "category": "mdph",
        "intention": "refus_droits",
        "priority": "p0",
        "cta_type": "dossier_express",
        "cta_label": "Faire analyser mon dossier MDPH",
        "content": {
            "situation": "Vous venez de recevoir une notification de la MDPH : votre demande d'Allocation aux Adultes Handicapés (AAH) est refusée. Le courrier mentionne un taux d'incapacité insuffisant ou une restriction substantielle et durable non reconnue. Vous ne comprenez pas cette décision, surtout quand votre quotidien est impacté au point de ne plus pouvoir travailler normalement.",
            "explication": "La MDPH évalue votre dossier sur pièces, à partir des certificats médicaux et du projet de vie que vous avez transmis. Dans la majorité des cas, un refus d'AAH ne signifie pas que votre handicap n'est pas réel. Il signifie que le dossier tel qu'il a été présenté n'a pas permis à l'équipe pluridisciplinaire de mesurer pleinement l'impact de votre situation sur votre autonomie et votre capacité de travail. Un certificat médical trop succinct, un projet de vie absent ou trop vague, ou des pièces justificatives manquantes sont les causes les plus fréquentes.",
            "solutions": [
                "Lisez attentivement la notification de refus : elle indique le motif précis (taux d'incapacité, restriction substantielle) et le délai de recours.",
                "Déposez un recours administratif préalable obligatoire (RAPO) dans les 2 mois suivant la notification. Ce recours est gratuit et se fait par courrier recommandé à la MDPH.",
                "Renforcez votre dossier médical : demandez à votre médecin traitant et à vos spécialistes des certificats détaillés décrivant précisément les limitations fonctionnelles au quotidien.",
                "Rédigez un projet de vie complet : décrivez concrètement votre journée type, vos difficultés, ce que vous ne pouvez plus faire seul(e).",
                "Si le RAPO est rejeté, saisissez le tribunal judiciaire (pôle social) dans un délai de 2 mois. Vous pouvez vous faire accompagner gratuitement par une association ou un délégué du Défenseur des droits."
            ],
            "erreurs": [
                "Laisser passer le délai de 2 mois sans réagir : votre droit de recours est définitivement perdu.",
                "Renvoyer le même dossier sans modification : le RAPO sera rejeté pour les mêmes raisons.",
                "Ne pas rédiger de projet de vie : c'est pourtant l'élément clé que la CDAPH examine pour évaluer la restriction substantielle.",
                "Se décourager après un premier refus : statistiquement, de nombreux recours aboutissent à une révision favorable."
            ],
            "reassurance": "Le refus d'AAH est l'une des situations les plus fréquentes que nous accompagnons. Dans la grande majorité des cas, un dossier mieux structuré et des pièces médicales précises permettent d'obtenir une issue favorable au recours. Vous avez des droits, et des solutions existent pour les faire valoir."
        },
    },
    {
        "slug": "taux-ipp-5-pourcent-contester",
        "title": "Taux d'IPP fixé à 5% alors que vous ne pouvez plus travailler : comment contester ?",
        "meta_description": "Votre taux d'IPP a été fixé trop bas malgré des séquelles importantes ? Voici comment contester cette évaluation et obtenir une juste indemnisation.",
        "category": "indemnisation",
        "intention": "contestation",
        "priority": "p0",
        "cta_type": "dossier_express",
        "cta_label": "Analyser mon taux d'IPP",
        "content": {
            "situation": "Vous avez reçu la notification de votre taux d'Incapacité Permanente Partielle (IPP) suite à un accident du travail ou une maladie professionnelle. Le taux fixé — souvent entre 3% et 9% — vous semble dérisoire au regard de vos séquelles réelles. Vous souffrez au quotidien, vous ne pouvez plus exercer votre métier, et pourtant le chiffre inscrit sur le papier ne reflète pas votre réalité.",
            "explication": "Le taux d'IPP est fixé par le médecin conseil de la CPAM sur la base d'un barème indicatif (barème AT/MP). Ce barème évalue les séquelles physiques, mais ne prend pas toujours en compte l'impact professionnel et personnel réel. De plus, l'examen dure rarement plus de 15 à 20 minutes, ce qui laisse peu de place pour expliquer l'ensemble de vos limitations. Un coefficient professionnel devrait être appliqué lorsque les séquelles empêchent la reprise du poste, mais il est souvent sous-évalué ou oublié.",
            "solutions": [
                "Contestez la décision dans les 2 mois en demandant une expertise médicale auprès de la Commission Médicale de Recours Amiable (CMRA) de votre CPAM.",
                "Faites-vous accompagner par un médecin de recours (médecin conseil de victime) lors de l'expertise. C'est votre droit et cela change souvent le résultat.",
                "Rassemblez tous les certificats médicaux détaillant vos séquelles fonctionnelles : limitations de mouvement, douleurs chroniques, impact sur les gestes quotidiens.",
                "Demandez explicitement l'application du coefficient professionnel si vous ne pouvez plus exercer votre métier ou avez été déclaré(e) inapte.",
                "En cas de rejet par la CMRA, saisissez le pôle social du tribunal judiciaire. Une expertise judiciaire indépendante sera ordonnée."
            ],
            "erreurs": [
                "Accepter le taux sans contester parce qu'il semble « officiel » ou « définitif » : vous avez toujours un droit de recours.",
                "Se rendre seul(e) à l'expertise sans préparation : le médecin conseil de la CPAM défend les intérêts de l'organisme, pas les vôtres.",
                "Minimiser vos symptômes lors de l'examen par pudeur ou habitude : décrivez précisément ce que vous ne pouvez plus faire.",
                "Ignorer le coefficient professionnel : c'est souvent lui qui fait basculer le taux au-dessus du seuil de 10% ouvrant droit à une rente."
            ],
            "reassurance": "La contestation d'un taux d'IPP est une démarche courante et légitime. De nombreuses réévaluations aboutissent à un taux significativement revu à la hausse, parfois du simple au triple. Votre situation mérite d'être défendue avec les bons arguments et les bonnes preuves."
        },
    },
    {
        "slug": "expertise-medicale-defavorable-recours",
        "title": "Expertise médicale défavorable : vos séquelles ont été minimisées, quels recours ?",
        "meta_description": "L'expert médical a sous-évalué vos séquelles ? Découvrez vos recours concrets pour contester une expertise médicale défavorable.",
        "category": "expertise",
        "intention": "desaccord_medical",
        "priority": "p0",
        "cta_type": "accompagnement",
        "cta_label": "Être accompagné pour contester",
        "content": {
            "situation": "Vous êtes sorti(e) d'une expertise médicale avec un sentiment d'injustice. L'expert a passé peu de temps avec vous, n'a pas pris en compte certains de vos symptômes, ou a rédigé un rapport qui minimise clairement vos séquelles. Le rapport conclut à des séquelles « modérées » ou « sans retentissement fonctionnel significatif », alors que votre quotidien est profondément affecté.",
            "explication": "L'expertise médicale est un exercice codifié : l'expert répond à une mission précise, dans un temps limité. Il arrive fréquemment que des séquelles invisibles (douleurs chroniques, fatigue, troubles cognitifs, impact psychologique) soient sous-évaluées car elles ne se « voient » pas lors de l'examen. De plus, certains experts adoptent une approche conservatrice, ce qui peut conduire à une sous-estimation systématique. Enfin, si vous n'étiez pas accompagné(e) par un médecin de recours, vos arguments médicaux n'ont peut-être pas été portés avec le poids nécessaire.",
            "solutions": [
                "Demandez communication du rapport d'expertise complet : vous avez le droit de le lire et de le contester.",
                "Rédigez un dire (observations écrites) dans le délai imparti, en pointant les inexactitudes, omissions ou contradictions du rapport.",
                "Faites rédiger un rapport critique par un médecin de recours (médecin conseil de victime) qui analysera point par point les conclusions de l'expert.",
                "Si l'expertise est judiciaire, demandez au tribunal une contre-expertise ou une expertise complémentaire avec un autre expert.",
                "Rassemblez des attestations de votre entourage, de votre médecin traitant et de vos spécialistes décrivant votre état réel."
            ],
            "erreurs": [
                "Ne pas lire le rapport d'expertise en détail : des erreurs factuelles (dates, antécédents, symptômes) sont fréquentes.",
                "Ne pas formuler de dire dans les délais : c'est votre seul moyen officiel de contester le rapport.",
                "Se rendre à l'expertise sans dossier médical organisé : apportez tous vos documents classés chronologiquement.",
                "Accepter les conclusions sans les contester : un rapport d'expertise n'est pas une décision définitive."
            ],
            "reassurance": "Une expertise défavorable n'est pas une fin de parcours. Les dires, rapports critiques et contre-expertises permettent régulièrement de rétablir une évaluation juste de vos séquelles. Vous avez le droit de faire entendre votre réalité médicale."
        },
    },
    {
        "slug": "accident-travail-non-declare-employeur",
        "title": "Accident du travail non déclaré par l'employeur : comment protéger vos droits ?",
        "meta_description": "Votre employeur refuse ou oublie de déclarer votre accident du travail ? Voici les étapes pour protéger vos droits et obtenir la prise en charge.",
        "category": "accident_travail",
        "intention": "urgence",
        "priority": "p0",
        "cta_type": "dossier_express",
        "cta_label": "Faire analyser ma situation",
        "content": {
            "situation": "Vous avez eu un accident sur votre lieu de travail ou sur le trajet, et votre employeur n'a pas effectué la déclaration d'accident du travail (DAT) auprès de la CPAM. Peut-être vous a-t-il dit que « ce n'était pas nécessaire », que « c'est un simple arrêt maladie », ou peut-être n'a-t-il tout simplement pas répondu à votre demande. Sans cette déclaration, vos soins ne sont pas pris en charge à 100%, et vos indemnités journalières sont calculées comme un arrêt maladie ordinaire.",
            "explication": "L'employeur a l'obligation légale de déclarer tout accident du travail dans les 48 heures (article L.441-2 du Code de la Sécurité sociale). En pratique, certains employeurs ne déclarent pas l'accident pour éviter une hausse de leur taux de cotisation AT/MP, parce qu'ils contestent le caractère professionnel de l'accident, ou par simple négligence administrative. Quelle que soit la raison, cette absence de déclaration vous pénalise directement.",
            "solutions": [
                "Déclarez vous-même l'accident auprès de votre CPAM : vous avez 2 ans pour le faire (article L.441-2 CSS). Envoyez un courrier recommandé avec le récit des faits, la date, le lieu et les témoins éventuels.",
                "Faites constater vos lésions par un médecin dès que possible et obtenez un certificat médical initial (CMI) mentionnant le lien avec l'accident.",
                "Conservez toutes les preuves : témoignages de collègues, échanges de mails/SMS avec l'employeur, photos du lieu, registre des accidents bénins.",
                "Adressez une mise en demeure écrite à votre employeur lui rappelant son obligation de déclaration et les sanctions encourues (contravention de 4e classe).",
                "Si la CPAM refuse la prise en charge, contestez la décision devant la Commission de Recours Amiable (CRA) dans les 2 mois."
            ],
            "erreurs": [
                "Attendre que l'employeur finisse par déclarer : plus le temps passe, plus il sera difficile de prouver les circonstances.",
                "Accepter un arrêt maladie classique au lieu d'un arrêt AT : la différence d'indemnisation est significative (pas de délai de carence, prise en charge à 100%).",
                "Ne pas faire constater les lésions rapidement : le CMI doit être établi le plus proche possible de la date de l'accident.",
                "Hésiter par peur de représailles : votre employeur ne peut pas vous sanctionner pour avoir déclaré un accident du travail."
            ],
            "reassurance": "La non-déclaration par l'employeur est un problème que nous rencontrons régulièrement. La loi vous protège : vous pouvez déclarer l'accident vous-même, et les tribunaux sont particulièrement attentifs à ces situations. Ne laissez pas le silence de votre employeur vous priver de vos droits."
        },
    },
    {
        "slug": "refus-maladie-professionnelle-cpam-recours",
        "title": "Refus de maladie professionnelle par la CPAM : vous avez 2 mois pour agir",
        "meta_description": "La CPAM a refusé de reconnaître votre maladie professionnelle ? Découvrez les recours disponibles et les délais à respecter impérativement.",
        "category": "accident_travail",
        "intention": "urgence",
        "priority": "p0",
        "cta_type": "dossier_express",
        "cta_label": "Analyser mon dossier de refus",
        "content": {
            "situation": "Vous avez reçu un courrier de la CPAM vous informant que votre demande de reconnaissance de maladie professionnelle est rejetée. La notification indique que le lien entre votre pathologie et votre activité professionnelle n'est pas établi, ou que votre maladie ne figure pas dans les tableaux de maladies professionnelles. Le délai de recours de 2 mois court à partir de cette notification.",
            "explication": "La reconnaissance d'une maladie professionnelle suit un processus strict. Si votre pathologie figure dans un tableau de maladies professionnelles et que toutes les conditions sont remplies (délai de prise en charge, durée d'exposition, travaux effectués), la reconnaissance est en principe automatique. Le refus survient quand une condition du tableau n'est pas remplie, quand la maladie n'est pas dans les tableaux (procédure hors tableau via le CRRMP), ou quand le médecin conseil estime que le lien professionnel n'est pas suffisamment documenté.",
            "solutions": [
                "Saisissez la Commission de Recours Amiable (CRA) de votre CPAM dans les 2 mois suivant la notification de refus. C'est un recours gratuit, par courrier recommandé.",
                "Identifiez précisément le motif du refus : condition du tableau non remplie, pathologie hors tableau, lien causal contesté. La stratégie de recours dépend du motif.",
                "Faites compléter votre dossier médical : certificats de spécialistes établissant le lien entre votre pathologie et votre exposition professionnelle, historique des postes occupés, fiches de données de sécurité des produits manipulés.",
                "Si votre maladie est hors tableau, demandez la saisine du Comité Régional de Reconnaissance des Maladies Professionnelles (CRRMP) : ce comité peut reconnaître la maladie si elle est directement causée par le travail.",
                "En cas de rejet par la CRA, saisissez le pôle social du tribunal judiciaire dans un délai de 2 mois. Une expertise médicale judiciaire sera souvent ordonnée."
            ],
            "erreurs": [
                "Laisser passer le délai de 2 mois : c'est le piège le plus fréquent et le plus grave. Passé ce délai, vous perdez tout droit de recours.",
                "Ne pas contester un refus fondé sur une condition du tableau : parfois, la condition est en réalité remplie mais mal documentée dans le dossier.",
                "Oublier de mentionner des expositions professionnelles antérieures chez d'anciens employeurs : le cumul d'exposition compte.",
                "Confondre arrêt maladie et maladie professionnelle : les enjeux financiers et juridiques sont très différents."
            ],
            "reassurance": "Le refus de reconnaissance de maladie professionnelle est une situation que nous traitons quotidiennement. De nombreux refus sont infirmés en recours, que ce soit devant la CRA, le CRRMP ou le tribunal. Le plus important est de réagir dans les délais et de structurer votre dossier avec les bonnes pièces médicales."
        },
    },
]

async def seed():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]

    for page_data in PAGES:
        existing = await db.seo_pages.find_one({"slug": page_data["slug"]})
        if existing:
            print(f"  Skip (exists): {page_data['slug']}")
            continue
        doc = {
            "id": str(uuid.uuid4()),
            **page_data,
            "active": True,
            "views": 0,
            "cta_clicks": 0,
            "conversions": 0,
            "revenue": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.seo_pages.insert_one(doc)
        print(f"  Created: /guide/{page_data['slug']}")

    print(f"\nDone. {len(PAGES)} pages processed.")

if __name__ == "__main__":
    asyncio.run(seed())
