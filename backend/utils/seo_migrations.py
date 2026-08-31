"""SEO title/description migrations — idempotent.

Each migration has a unique ID. On boot, we check the `seo_migrations` collection.
If the migration ID has already been applied (=> a doc with that id exists), we skip.
Otherwise we apply the update_one operations and persist a marker.

This is the safe way to propagate optimized titles/meta_descriptions to production
without overwriting analytics or any unrelated fields, and without re-running the
full seed (which would replace fields). Adding a new migration = appending a dict
to MIGRATIONS list below.
"""
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


# Each migration is a list of {"slug": ..., "title": ..., "meta_description": ...}
MIGRATIONS = [
    {
        "id": "2026-05-17-quick-wins-vague2",
        "description": "SEO Quick Wins Vague 2 — titles + meta descriptions optimisés sur 3 pages /guide/* (faute inexcusable, AT non déclaré, délai prescription MP)",
        "updates": [
            {
                "slug": "accident-travail-non-declare-employeur",
                "title": "Accident du Travail Non Déclaré par l'Employeur : Vos Recours",
                "meta_description": "Employeur qui refuse la déclaration AT ? Procédure CPAM, sanctions employeur, mise en demeure. Délai 2 ans pour faire valoir vos droits.",
            },
            {
                "slug": "faute-inexcusable-employeur",
                "title": "Faute Inexcusable de l'Employeur : Conditions + Indemnités",
                "meta_description": "Faute inexcusable : 3 conditions à prouver, indemnisation complémentaire CPAM + employeur. Délai 2 ans. Guide étape par étape pour saisir le pôle social.",
            },
            {
                "slug": "delai-prescription-maladie-professionnelle",
                "title": "Délai de Prescription Maladie Professionnelle CPAM",
                "meta_description": "Combien de temps pour déclarer une maladie professionnelle ? Délais CPAM (2 ans), prescription civile (5 ans), cas particuliers et erreurs à éviter.",
            },
        ],
    },
    {
        "id": "2026-08-06-phase1-maillage-guides",
        "description": "Phase 1 SEO — Maillage interne des 17 guides (cocons sémantiques). Cibles gelées exclues (/expertise-medicale, /expertise-medicale/assureur, /dossier-express) jusqu'à J+28.",
        "updates": [
            {"slug": "refus-mdph-aah-que-faire", "content.maillage": [
                {"slug": "refus-aah-rsdae-non-reconnue", "text": "Refus AAH pour RSDAE non reconnue : la stratégie de recours"},
                {"slug": "comment-demander-rqth-strategic", "text": "Demander la RQTH : démarches et stratégie complètes"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Saisir le pôle social du tribunal judiciaire après un refus"},
                {"href": "/mdph", "text": "MDPH : comprendre vos droits et structurer votre dossier"},
                {"href": "/calculatrice-aah", "text": "Simulateur AAH : estimez le montant de vos droits"},
            ]},
            {"slug": "taux-ipp-5-pourcent-contester", "content.maillage": [
                {"slug": "rente-accident-travail-calcul-contestation", "text": "Rente accident du travail : calcul, montant et contestation"},
                {"slug": "ipp-fonction-publique-hospitaliere", "text": "IPP fonction publique hospitalière : ATI et recours"},
                {"slug": "expertise-medicale-defavorable-recours", "text": "Expertise médicale défavorable : les recours possibles"},
                {"href": "/calculatrice-ipp", "text": "Simulateur rente IPP : calculez votre indemnisation"},
            ]},
            {"slug": "expertise-medicale-defavorable-recours", "content.maillage": [
                {"slug": "comment-preparer-expertise-medicale", "text": "Bien préparer son expertise médicale : le guide complet"},
                {"slug": "taux-ipp-5-pourcent-contester", "text": "Contester un taux IPP trop bas après l'expertise"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Le recours devant le pôle social du tribunal judiciaire"},
                {"href": "/medecin-conseil", "text": "Médecin conseil CPAM : rôle, convocation et contestation"},
            ]},
            {"slug": "accident-travail-non-declare-employeur", "content.maillage": [
                {"slug": "faute-inexcusable-employeur", "text": "Faute inexcusable de l'employeur : conditions et indemnités"},
                {"slug": "rente-accident-travail-calcul-contestation", "text": "Rente accident du travail : calcul et contestation"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Saisir le pôle social du tribunal judiciaire"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "refus-maladie-professionnelle-cpam-recours", "content.maillage": [
                {"slug": "comment-faire-reconnaitre-maladie-professionnelle", "text": "Faire reconnaître une maladie professionnelle : les étapes"},
                {"slug": "delai-prescription-maladie-professionnelle", "text": "Délai de prescription maladie professionnelle : ne perdez pas vos droits"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Contester devant le pôle social du tribunal judiciaire"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "faute-inexcusable-employeur", "content.maillage": [
                {"slug": "accident-travail-non-declare-employeur", "text": "Accident du travail non déclaré par l'employeur : vos recours"},
                {"slug": "rente-accident-travail-calcul-contestation", "text": "Rente accident du travail : calcul de l'indemnisation"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "La procédure devant le pôle social du tribunal judiciaire"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
                {"href": "/calculatrice-ipp", "text": "Simulateur rente IPP : estimez l'indemnisation complémentaire"},
            ]},
            {"slug": "inaptitude-travail-droits-recours", "content.maillage": [
                {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus de maladie professionnelle par la CPAM : les recours"},
                {"slug": "comment-demander-rqth-strategic", "text": "Demander la RQTH après une inaptitude"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits"},
                {"href": "/mdph", "text": "MDPH : structurer votre dossier de compensation"},
            ]},
            {"slug": "rente-accident-travail-calcul-contestation", "content.maillage": [
                {"slug": "taux-ipp-5-pourcent-contester", "text": "Taux IPP de 5 % : comment le contester"},
                {"slug": "faute-inexcusable-employeur", "text": "Faute inexcusable : obtenir une indemnisation complémentaire"},
                {"href": "/calculatrice-ipp", "text": "Simulateur rente IPP : calculez votre rente en ligne"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "recours-tribunal-judiciaire-pole-social", "content.maillage": [
                {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus de maladie professionnelle CPAM : préparer le recours"},
                {"slug": "refus-mdph-aah-que-faire", "text": "Refus MDPH ou AAH : les recours possibles"},
                {"slug": "expertise-medicale-defavorable-recours", "text": "Expertise médicale défavorable : contester les conclusions"},
                {"slug": "faute-inexcusable-employeur", "text": "Faute inexcusable de l'employeur : saisir le pôle social"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
                {"href": "/mdph", "text": "MDPH : comprendre vos droits avant le contentieux"},
            ]},
            {"slug": "delai-prescription-maladie-professionnelle", "content.maillage": [
                {"slug": "comment-faire-reconnaitre-maladie-professionnelle", "text": "Faire reconnaître une maladie professionnelle : la procédure"},
                {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus CPAM : les recours contre une décision défavorable"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "comment-preparer-expertise-medicale", "content.maillage": [
                {"slug": "expertise-medicale-defavorable-recours", "text": "Expertise médicale défavorable : les recours après coup"},
                {"slug": "taux-ipp-5-pourcent-contester", "text": "Contester le taux IPP fixé après l'expertise"},
                {"href": "/medecin-conseil", "text": "Médecin conseil CPAM : rôle, convocation et contestation"},
                {"href": "/calculatrice-ipp", "text": "Simulateur IPP : anticipez l'enjeu financier de l'expertise"},
            ]},
            {"slug": "comment-demander-rqth-strategic", "content.maillage": [
                {"slug": "refus-mdph-aah-que-faire", "text": "Refus MDPH / AAH : que faire en cas de rejet"},
                {"slug": "refus-aah-rsdae-non-reconnue", "text": "RSDAE non reconnue : la stratégie de recours AAH"},
                {"href": "/mdph", "text": "MDPH : comprendre vos droits et monter votre dossier"},
                {"href": "/calculatrice-aah", "text": "Simulateur AAH : vérifiez votre éligibilité"},
            ]},
            {"slug": "comment-faire-reconnaitre-maladie-professionnelle", "content.maillage": [
                {"slug": "delai-prescription-maladie-professionnelle", "text": "Délais de prescription : déclarez votre maladie professionnelle à temps"},
                {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus de la CPAM : les recours qui fonctionnent"},
                {"slug": "maladie-professionnelle-definition-droits", "text": "Maladie professionnelle : définition et droits ouverts"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "maladie-professionnelle-definition-droits", "content.maillage": [
                {"slug": "comment-faire-reconnaitre-maladie-professionnelle", "text": "Faire reconnaître votre maladie professionnelle : les étapes"},
                {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus maladie professionnelle CPAM : recours et délais"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "ptia-definition-droits-strategie", "content.maillage": [
                {"slug": "comment-preparer-expertise-medicale", "text": "Préparer l'expertise médicale demandée par l'assureur"},
                {"slug": "expertise-medicale-defavorable-recours", "text": "Expertise défavorable : contester les conclusions"},
                {"href": "/protection-juridique", "text": "Protection juridique : faire valoir vos droits face à l'assureur"},
            ]},
            {"slug": "refus-aah-rsdae-non-reconnue", "content.maillage": [
                {"slug": "refus-mdph-aah-que-faire", "text": "Refus MDPH AAH : recours, délais et solutions"},
                {"slug": "comment-demander-rqth-strategic", "text": "Demander la RQTH en parallèle de l'AAH"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Saisir le pôle social après un refus définitif"},
                {"href": "/mdph", "text": "MDPH : structurer un dossier solide"},
                {"href": "/calculatrice-aah", "text": "Simulateur AAH : estimez vos droits"},
            ]},
            {"slug": "ipp-fonction-publique-hospitaliere", "content.maillage": [
                {"slug": "taux-ipp-5-pourcent-contester", "text": "Contester un taux IPP trop bas"},
                {"slug": "rente-accident-travail-calcul-contestation", "text": "Rente accident du travail : calcul et contestation"},
                {"href": "/calculatrice-ipp", "text": "Simulateur rente IPP : calculez votre indemnisation"},
            ]},
        ],
    },
    {
        "id": "2026-08-31-chantier1-enrichissement-refus-mdph",
        "description": "Chantier 1 GSC — Enrichissement /guide/refus-mdph-aah-que-faire (position ~16 → page 1) : intentions secondaires (recours gracieux, lettre RAPO, délais de réponse, montant AAH 2026), FAQ +4, meta affinée. H1/title conservés.",
        "updates": [
            {
                "slug": "refus-mdph-aah-que-faire",
                "meta_description": "Refus MDPH ou AAH refusée ? Recours RAPO en 2 mois, modèle de démarche, délais de réponse et solutions concrètes pour faire reconnaître vos droits.",
                "content.strategie": "La clé d'un recours efficace n'est pas juridique — elle est documentaire. Un dossier MDPH se gagne sur la qualité des preuves médicales et la précision du projet de vie. Notre approche consiste à analyser votre notification de refus pour identifier exactement ce qui a manqué, puis à structurer un dossier de recours qui répond point par point aux critères de la CDAPH. Nous vérifions la cohérence entre le certificat médical, les bilans de spécialistes et le projet de vie. Nous identifions les pièces manquantes et vous orientons vers les examens complémentaires nécessaires. Attention à la terminologie : depuis 2019, le « recours gracieux » n'existe plus pour les décisions MDPH — il a été remplacé par le RAPO (recours administratif préalable obligatoire), passage obligé avant toute saisine du tribunal. Cette lecture stratégique transforme un dossier « incomplet aux yeux de la MDPH » en un dossier qui remplit objectivement les critères d'attribution.",
                "content.faq": [
                    {
                        "question": "Quel est le délai pour contester un refus MDPH ?",
                        "answer": "Vous disposez de 2 mois à compter de la notification de refus pour déposer un recours administratif préalable obligatoire (RAPO) auprès de la MDPH, puis de 2 mois supplémentaires pour saisir le tribunal judiciaire si le RAPO est rejeté."
                    },
                    {
                        "question": "Peut-on obtenir l'AAH avec un taux entre 50% et 79% ?",
                        "answer": "Oui, à condition de démontrer une restriction substantielle et durable pour l'accès à l'emploi (RSDAE). Cela nécessite des preuves médicales détaillées et un projet de vie argumenté."
                    },
                    {
                        "question": "Mon renouvellement AAH a été refusé, que faire ?",
                        "answer": "Le refus de renouvellement AAH suit la même procédure de recours qu'un refus initial : RAPO dans les 2 mois, puis tribunal. L'erreur la plus courante est de redéposer le même dossier sans l'actualiser. Fournissez des certificats médicaux récents décrivant l'évolution ou la persistance de vos limitations, et mettez à jour votre projet de vie."
                    },
                    {
                        "question": "Recours gracieux ou RAPO : quelle différence pour un refus MDPH ?",
                        "answer": "Depuis le 1er janvier 2019, le recours gracieux n'existe plus pour les décisions MDPH : il a été remplacé par le RAPO (recours administratif préalable obligatoire). C'est un passage obligé avant toute saisine du tribunal judiciaire. Il se dépose par courrier recommandé avec accusé de réception auprès de la MDPH, dans les 2 mois suivant la notification, et il est entièrement gratuit."
                    },
                    {
                        "question": "Comment rédiger la lettre de recours (RAPO) à la MDPH ?",
                        "answer": "La lettre doit rappeler la référence de la décision contestée, le motif exact du refus mentionné sur la notification, et surtout apporter des éléments nouveaux : certificats médicaux détaillant les limitations fonctionnelles, bilans de spécialistes récents, projet de vie actualisé. Une lettre qui se contente d'exprimer un désaccord sans pièces nouvelles conduit quasi systématiquement au même refus. Joignez la copie de la notification et envoyez le tout en recommandé avec accusé de réception."
                    },
                    {
                        "question": "Combien de temps la MDPH met-elle à répondre à un RAPO ?",
                        "answer": "La MDPH dispose de 2 mois pour répondre à votre RAPO. Passé ce délai, le silence vaut rejet implicite : vous pouvez alors saisir le tribunal judiciaire (pôle social) dans un nouveau délai de 2 mois. Conservez l'accusé de réception de votre envoi : c'est lui qui fait courir les délais."
                    },
                    {
                        "question": "Quel est le montant de l'AAH en 2026 ?",
                        "answer": "Le montant de l'AAH à taux plein est de 1041,59 € par mois en 2026. Depuis la déconjugalisation (octobre 2023), les revenus de votre conjoint ne sont plus pris en compte dans le calcul. Le montant peut être réduit si vous percevez d'autres ressources (pension d'invalidité, revenus d'activité). Utilisez notre simulateur AAH pour estimer vos droits."
                    }
                ],
                "content.maillage": [
                    {"slug": "refus-aah-rsdae-non-reconnue", "text": "Refus AAH pour RSDAE non reconnue : la stratégie de recours"},
                    {"slug": "rsdae-definition-criteres-conditions", "text": "RSDAE : définition, critères et conditions de reconnaissance"},
                    {"slug": "comment-prouver-rsdae", "text": "Comment prouver une RSDAE : éléments, preuves et recours"},
                    {"slug": "comment-demander-rqth-strategic", "text": "Demander la RQTH : démarches et stratégie complètes"},
                    {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Saisir le pôle social du tribunal judiciaire après un refus"},
                    {"href": "/mdph", "text": "MDPH : comprendre vos droits et structurer votre dossier"},
                    {"href": "/calculatrice-aah", "text": "Simulateur AAH : estimez le montant de vos droits"},
                ],
            },
        ],
    },
    {
        "id": "2026-08-31-chantier2-cluster-rsdae",
        "description": "Chantier 2 GSC — Cluster RSDAE : création de 2 articles satellites (définition/critères + preuves) et maillage bidirectionnel avec le pilier /guide/refus-aah-rsdae-non-reconnue.",
        "updates": [
            {
                "slug": "rsdae-definition-criteres-conditions",
                "_upsert": True,
                "id": "7f3c2a91-5e84-4b6d-9c1a-2d8f4e6b0a53",
                "title": "RSDAE : définition, critères et conditions de reconnaissance",
                "meta_description": "Qu'est-ce que la RSDAE ? Définition légale, critères d'évaluation de la CDAPH et conditions pour obtenir l'AAH avec un taux d'incapacité de 50 à 79 %.",
                "category": "mdph",
                "intention": "refus_droits",
                "priority": "p0",
                "cta_type": "dossier_express",
                "cta_label": "Faire analyser mon refus AAH",
                "active": True,
                "views": 0,
                "cta_clicks": 0,
                "conversions": 0,
                "revenue": 0,
                "created_at": "2026-08-31T00:00:00+00:00",
                "content": {
                    "reponse_rapide_titre": "Qu'est-ce que la RSDAE ?",
                    "reponse_rapide": "La RSDAE (Restriction Substantielle et Durable pour l'Accès à l'Emploi) est la condition qui permet d'obtenir l'AAH lorsque votre taux d'incapacité est compris entre 50 % et 79 %. Définie par le décret n°2011-974 du 16 août 2011, elle est reconnue lorsque votre handicap entraîne des difficultés importantes d'accès à l'emploi, qui ne peuvent pas être compensées par des aménagements de poste, et qui sont prévisibles pour au moins un an. C'est la CDAPH qui l'apprécie, sur la base de votre dossier médical et de votre projet de vie. En 2026, l'AAH à taux plein s'élève à 1041,59 € par mois.",
                    "contexte": "L'AAH peut être attribuée par deux voies distinctes (article L.821-2 du Code de la Sécurité Sociale) : soit un taux d'incapacité d'au moins 80 %, soit un taux compris entre 50 % et 79 % assorti d'une RSDAE. Dans ce second cas, le taux seul ne suffit jamais : la CDAPH doit constater que votre handicap restreint de façon « substantielle et durable » votre accès à l'emploi. La restriction est « substantielle » lorsque vous rencontrez des difficultés importantes d'accès à l'emploi qui ne peuvent être compensées ni par des aménagements de poste, ni par des mesures d'accompagnement (reconnaissance RQTH, orientation professionnelle). Elle est « durable » lorsqu'elle est d'une durée prévisible d'au moins un an à compter du dépôt de la demande. La RSDAE est de très loin le motif le plus fréquent de refus d'AAH pour les taux 50-79 % : elle repose sur une appréciation, pas sur un simple calcul.",
                    "limites": "Les sites institutionnels (Service-public.fr, CNSA, MDPH) citent la définition réglementaire de la RSDAE mais n'expliquent jamais comment la CDAPH l'apprécie concrètement. Or l'évaluation se fait sur pièces : l'équipe pluridisciplinaire ne vous rencontre généralement pas. Elle croise le certificat médical, le projet de vie et votre parcours professionnel pour répondre à une question unique : cette personne peut-elle, de manière réaliste, occuper un emploi ordinaire, même aménagé ? Si votre dossier ne démontre pas explicitement l'impossibilité de compenser vos limitations par un aménagement, la RSDAE est écartée — même si votre handicap est bien réel. Le fait de ne pas travailler actuellement ne prouve rien en soi : c'est l'impossibilité structurelle d'accéder durablement à l'emploi qu'il faut établir.",
                    "blocages": [
                        "Le certificat médical mentionne un diagnostic sans décrire les répercussions sur la capacité de travail : fatigabilité, troubles de concentration, station debout impossible, absentéisme prévisible. Sans cette traduction fonctionnelle, la CDAPH ne peut pas caractériser la restriction.",
                        "Le dossier ne traite pas la question de la « compensation » : la CDAPH vérifie si des aménagements de poste ou un accompagnement (RQTH, orientation) suffiraient à rendre l'emploi accessible. Si rien dans votre dossier ne démontre le contraire, elle conclut que la restriction n'est pas substantielle.",
                        "Une activité conservée est mal contextualisée : un mi-temps thérapeutique, un emploi en milieu protégé (ESAT) ou un temps très partiel subi ne sont pas incompatibles avec la RSDAE, mais si le dossier ne l'explique pas, la CDAPH y voit la preuve d'une capacité de travail.",
                        "Le caractère « durable » n'est pas établi : des pièces médicales anciennes ou un pronostic flou ne permettent pas d'affirmer que la restriction persistera au moins un an. La CDAPH tranche alors dans le sens du refus.",
                        "Le projet de vie est vide ou générique : c'est pourtant le seul document où vous pouvez relier vos limitations quotidiennes à l'impossibilité de tenir un emploi (rythme, déplacements, relations de travail, régularité)."
                    ],
                    "erreurs": [
                        "Croire que le taux d'incapacité de 50-79 % suffit : sans démonstration de la RSDAE, l'AAH est systématiquement refusée par cette voie.",
                        "Penser qu'être au chômage ou sans activité prouve la RSDAE : la CDAPH évalue une impossibilité structurelle d'accès à l'emploi, pas une situation conjoncturelle.",
                        "Cacher une activité partielle par peur du refus : si elle est découverte, le dossier perd toute crédibilité. Il faut au contraire l'expliquer (temps partiel subi, poste aménagé, épuisement).",
                        "Confondre RSDAE et inaptitude au poste prononcée par le médecin du travail : l'inaptitude vise un poste précis, la RSDAE vise l'accès à l'emploi en général. L'une ne vaut pas l'autre, même si l'avis d'inaptitude est une pièce utile.",
                        "Négliger la RQTH : demander la RQTH en parallèle ne contredit pas la RSDAE, contrairement à une idée reçue. Les deux reconnaissances sont compatibles et souvent complémentaires."
                    ],
                    "strategie": "La RSDAE se démontre, elle ne se constate pas. Notre lecture stratégique consiste à reconstruire le raisonnement que tiendra la CDAPH : chaque limitation fonctionnelle décrite par le médecin doit être reliée à une exigence concrète de l'emploi (régularité, rythme, port de charges, interactions, déplacements), puis le dossier doit démontrer pourquoi aucun aménagement raisonnable ne compense ces limitations. Nous vérifions la cohérence entre le certificat médical, les bilans de spécialistes, le parcours professionnel et le projet de vie — car c'est la convergence de ces pièces qui emporte la décision. Un dossier RSDAE solide raconte une seule et même histoire à travers des documents différents.",
                    "orientation": [
                        "Vérifiez votre notification MDPH : si un taux de 50-79 % est reconnu mais l'AAH refusée, c'est que la RSDAE n'a pas été retenue — c'est elle qu'il faut cibler.",
                        "Demandez à vos médecins des certificats décrivant les conséquences de votre pathologie sur la capacité de travail : fatigabilité, concentration, station assise/debout, absences prévisibles.",
                        "Rédigez ou actualisez votre projet de vie en reliant chaque difficulté quotidienne à une exigence de l'emploi ordinaire.",
                        "Documentez vos tentatives professionnelles : arrêts répétés, inaptitudes, licenciements pour raison de santé, échecs de reprise — elles matérialisent la restriction.",
                        "En cas de refus, déposez un RAPO dans les 2 mois en apportant des pièces nouvelles ciblées sur la RSDAE, pas une simple copie du dossier initial."
                    ],
                    "reassurance": "La RSDAE est le critère le plus subjectif du droit de l'AAH — c'est précisément pour cela que les refus sont contestables. Un dossier restructuré autour de la démonstration fonctionnelle obtient fréquemment gain de cause en RAPO ou devant le pôle social. Vous n'avez pas à prouver que vous êtes incapable de tout : seulement que l'accès durable à un emploi ordinaire vous est fermé.",
                    "maillage": [
                        {"slug": "refus-aah-rsdae-non-reconnue", "text": "Refus AAH pour RSDAE non reconnue : la stratégie de recours"},
                        {"slug": "comment-prouver-rsdae", "text": "Comment prouver une RSDAE : éléments, preuves et recours"},
                        {"slug": "refus-mdph-aah-que-faire", "text": "Refus MDPH AAH : que faire ? Recours, délais et solutions"},
                        {"slug": "comment-demander-rqth-strategic", "text": "Demander la RQTH : démarches et stratégie complètes"},
                        {"href": "/calculatrice-aah", "text": "Simulateur AAH : estimez le montant de vos droits"},
                        {"href": "/mdph", "text": "MDPH : comprendre vos droits et structurer votre dossier"},
                    ],
                    "faq": [
                        {
                            "question": "Que signifie RSDAE ?",
                            "answer": "RSDAE signifie Restriction Substantielle et Durable pour l'Accès à l'Emploi. C'est la condition supplémentaire exigée pour obtenir l'AAH lorsque le taux d'incapacité reconnu par la MDPH est compris entre 50 % et 79 %. Elle est définie par le décret n°2011-974 du 16 août 2011."
                        },
                        {
                            "question": "Quelle différence entre « substantielle » et « durable » ?",
                            "answer": "« Substantielle » signifie que vos difficultés d'accès à l'emploi sont importantes et ne peuvent pas être compensées par des aménagements de poste ou des mesures d'accompagnement. « Durable » signifie que cette restriction est d'une durée prévisible d'au moins un an à compter du dépôt de votre demande. Les deux conditions doivent être réunies."
                        },
                        {
                            "question": "Peut-on cumuler RSDAE et RQTH ?",
                            "answer": "Oui. La RQTH (Reconnaissance de la Qualité de Travailleur Handicapé) et la RSDAE ne sont pas contradictoires : la RQTH vise à faciliter l'accès à l'emploi avec des aménagements, la RSDAE constate que malgré ces mesures, l'accès durable à l'emploi reste restreint. De nombreux bénéficiaires de l'AAH au titre de la RSDAE ont également la RQTH."
                        },
                        {
                            "question": "Peut-on travailler et avoir la RSDAE ?",
                            "answer": "Oui, dans certaines limites. Le travail en milieu protégé (ESAT) est compatible avec la RSDAE. Un emploi en milieu ordinaire à temps très partiel (moins d'un mi-temps) subi en raison du handicap ne fait pas obstacle à la reconnaissance, à condition que le dossier explique ce caractère subi. En revanche, un emploi stable à mi-temps ou plus rend la reconnaissance très difficile."
                        },
                        {
                            "question": "Le mi-temps thérapeutique empêche-t-il la RSDAE ?",
                            "answer": "Non, pas automatiquement. Le mi-temps thérapeutique est une mesure temporaire de reprise : il peut au contraire illustrer l'impossibilité de tenir un temps plein. Mais le dossier doit le contextualiser clairement (prescription médicale, échecs de reprise antérieurs), faute de quoi la CDAPH peut y voir une capacité de travail."
                        },
                        {
                            "question": "Quel est le montant de l'AAH obtenue au titre de la RSDAE ?",
                            "answer": "Le montant est identique quelle que soit la voie d'attribution : 1041,59 € par mois à taux plein en 2026. La différence porte sur la durée d'attribution : au titre de la RSDAE (taux 50-79 %), l'AAH est accordée pour 1 à 2 ans en général, contre des durées plus longues (voire sans limitation) pour un taux d'au moins 80 %."
                        },
                        {
                            "question": "Que faire si la RSDAE n'est pas reconnue ?",
                            "answer": "Vous disposez de 2 mois pour déposer un RAPO (recours administratif préalable obligatoire) auprès de la MDPH, en apportant des éléments nouveaux ciblés : certificats fonctionnels détaillés, preuves professionnelles, projet de vie actualisé. En cas de rejet du RAPO, vous pouvez saisir le tribunal judiciaire (pôle social) dans un nouveau délai de 2 mois."
                        }
                    ]
                },
            },
            {
                "slug": "comment-prouver-rsdae",
                "_upsert": True,
                "id": "b2e9d4c7-1a36-4f8e-8d52-6c0a9e3f7b14",
                "title": "Comment prouver une RSDAE : éléments, preuves et recours",
                "meta_description": "Comment prouver la RSDAE à la MDPH ? Certificat médical fonctionnel, projet de vie, preuves professionnelles : la méthode pour obtenir l'AAH à 50-79 %.",
                "category": "mdph",
                "intention": "refus_droits",
                "priority": "p0",
                "cta_type": "dossier_express",
                "cta_label": "Faire analyser mon refus AAH",
                "active": True,
                "views": 0,
                "cta_clicks": 0,
                "conversions": 0,
                "revenue": 0,
                "created_at": "2026-08-31T00:00:01+00:00",
                "content": {
                    "reponse_rapide_titre": "Comment prouver une RSDAE à la MDPH ?",
                    "reponse_rapide": "Prouver une RSDAE repose sur trois familles de preuves convergentes : un certificat médical qui décrit les limitations fonctionnelles au travail (et pas seulement le diagnostic), un projet de vie qui relie ces limitations aux exigences concrètes d'un emploi, et des preuves professionnelles (inaptitudes, arrêts répétés, échecs de reprise, licenciements pour raison de santé). La CDAPH évalue sur pièces : ce qui n'est pas écrit et documenté n'existe pas dans votre dossier. Un dossier bien construit démontre aussi pourquoi aucun aménagement de poste ne peut compenser vos limitations.",
                    "contexte": "La RSDAE (Restriction Substantielle et Durable pour l'Accès à l'Emploi) conditionne l'attribution de l'AAH lorsque votre taux d'incapacité est compris entre 50 % et 79 % (article L.821-2 du Code de la Sécurité Sociale, décret n°2011-974 du 16 août 2011). Contrairement au taux d'incapacité, qui découle d'un barème, la RSDAE relève d'une appréciation globale par la CDAPH : elle se prouve, dossier à l'appui. L'équipe pluridisciplinaire ne vous reçoit généralement pas — elle statue sur ce que contiennent vos pièces. La charge de la démonstration vous incombe donc entièrement, aussi bien lors de la demande initiale que lors d'un recours après refus.",
                    "limites": "Aucun site officiel ne fournit de « liste des preuves » de la RSDAE, car il n'en existe pas de définition fermée : c'est un faisceau d'indices. En pratique, la CDAPH cherche des réponses à trois questions : quelles sont les limitations fonctionnelles concrètes ? Empêchent-elles de tenir un emploi ordinaire, même aménagé ? Cette situation va-t-elle durer au moins un an ? Les dossiers refusés sont presque toujours ceux qui laissent l'une de ces trois questions sans réponse documentée. Le formulaire MDPH standard, rempli sans stratégie, ne suffit presque jamais à établir la RSDAE.",
                    "blocages": [
                        "Le certificat médical (Cerfa 15695) coche des cases sans rédiger la partie « retentissement fonctionnel » : c'est pourtant la seule section que l'équipe pluridisciplinaire exploite pour évaluer la capacité de travail.",
                        "Les preuves professionnelles sont absentes du dossier : avis d'inaptitude, arrêts de travail répétés, ruptures de contrat pour raison de santé, échecs de formation ou de reclassement dorment dans vos archives alors qu'ils matérialisent la restriction.",
                        "Le dossier ne répond pas à la question de la compensation : il faut expliquer pourquoi ni un poste aménagé, ni un temps partiel, ni un accompagnement RQTH ne rendent l'emploi durablement accessible dans votre cas.",
                        "Les pièces se contredisent : un certificat qui évoque une « amélioration », un projet de vie qui mentionne des activités exigeantes, ou un CV récent orienté recherche d'emploi active peuvent ruiner la démonstration.",
                        "Le caractère durable n'est pas daté : sans pronostic médical explicite sur au moins un an, la CDAPH ne peut pas retenir la durabilité de la restriction."
                    ],
                    "erreurs": [
                        "Envoyer le dossier avec le seul certificat du médecin traitant : un bilan de spécialiste (psychiatre, rhumatologue, neurologue) décrivant les limitations fonctionnelles a un poids décisif.",
                        "Rédiger le projet de vie comme une biographie : il doit être orienté « emploi » — journée type, fatigabilité, concentration, déplacements, régularité, relations de travail.",
                        "Minimiser vos difficultés par pudeur ou par peur d'être jugé(e) : la CDAPH statue sur ce qui est écrit, pas sur ce que vous vivez réellement.",
                        "Redéposer les mêmes pièces en recours après un refus : sans élément nouveau ciblé sur la RSDAE, le RAPO aboutit mécaniquement au même refus.",
                        "Attendre le dernier moment : rassembler bilans, attestations et certificats prend plusieurs semaines, alors que le délai de RAPO n'est que de 2 mois."
                    ],
                    "strategie": "Notre méthode consiste à construire la preuve de la RSDAE comme un dossier de démonstration en trois étages. Étage médical : obtenir des certificats qui traduisent chaque pathologie en limitations fonctionnelles mesurables face aux exigences d'un poste (rythme, posture, charge cognitive, absentéisme prévisible). Étage professionnel : rassembler les pièces qui matérialisent l'échec ou l'impossibilité de l'emploi — inaptitudes, arrêts itératifs, ruptures pour raison de santé, tentatives avortées. Étage narratif : un projet de vie qui fait converger les deux premiers étages et répond explicitement à la question de la compensation. Nous analysons votre notification de refus pour identifier l'étage défaillant et reconstruire le dossier là où il a échoué.",
                    "orientation": [
                        "Relisez votre notification : si le taux 50-79 % est reconnu mais l'AAH refusée, la RSDAE est le seul verrou à faire sauter.",
                        "Demandez à chaque médecin un certificat « fonctionnel » : conséquences concrètes sur la capacité de travail, avec un pronostic de durée (au moins un an).",
                        "Rassemblez toutes vos preuves professionnelles : avis d'inaptitude, arrêts de travail, licenciements, échecs de reprise ou de formation, attestations d'employeurs.",
                        "Réécrivez votre projet de vie en reliant chaque limitation à une exigence de l'emploi, et en expliquant pourquoi les aménagements ne suffisent pas.",
                        "Déposez votre demande ou votre RAPO en recommandé avec accusé de réception, et conservez une copie intégrale du dossier transmis."
                    ],
                    "reassurance": "La preuve de la RSDAE n'exige pas de démontrer une incapacité totale : il s'agit d'établir, pièces à l'appui, que l'accès durable à un emploi ordinaire vous est fermé malgré les aménagements possibles. C'est un exercice de construction documentaire — et c'est exactement pour cela qu'un dossier refusé peut être gagné en recours une fois restructuré. Plus de 40 % des RAPO aboutissent favorablement lorsque le dossier est correctement repris.",
                    "maillage": [
                        {"slug": "rsdae-definition-criteres-conditions", "text": "RSDAE : définition, critères et conditions de reconnaissance"},
                        {"slug": "refus-aah-rsdae-non-reconnue", "text": "Refus AAH pour RSDAE non reconnue : la stratégie de recours"},
                        {"slug": "refus-mdph-aah-que-faire", "text": "Refus MDPH AAH : que faire ? Recours, délais et solutions"},
                        {"slug": "comment-demander-rqth-strategic", "text": "Demander la RQTH : démarches et stratégie complètes"},
                        {"href": "/mdph", "text": "MDPH : structurer un dossier solide"},
                        {"href": "/calculatrice-aah", "text": "Simulateur AAH : estimez vos droits"},
                    ],
                    "faq": [
                        {
                            "question": "Quels documents prouvent une RSDAE ?",
                            "answer": "Il n'existe pas de liste officielle : la RSDAE s'établit par un faisceau d'indices. Les pièces les plus déterminantes sont les certificats médicaux décrivant les limitations fonctionnelles au travail, les bilans de spécialistes, les avis d'inaptitude du médecin du travail, les arrêts de travail répétés, les ruptures de contrat pour raison de santé et un projet de vie détaillé orienté sur l'emploi."
                        },
                        {
                            "question": "Le médecin du travail peut-il aider à prouver la RSDAE ?",
                            "answer": "Oui, indirectement. Un avis d'inaptitude, des restrictions d'aptitude répétées ou un échec de reclassement documenté sont des pièces très utiles : elles montrent qu'en situation réelle de travail, votre état de santé a fait obstacle à l'emploi. Attention toutefois : l'inaptitude à un poste précis ne vaut pas RSDAE à elle seule, elle doit s'intégrer dans une démonstration plus large."
                        },
                        {
                            "question": "Comment prouver la RSDAE quand on n'a jamais travaillé ?",
                            "answer": "L'absence de parcours professionnel n'empêche pas la reconnaissance. La démonstration repose alors davantage sur les pièces médicales (limitations fonctionnelles, hospitalisations, suivis) et sur le projet de vie : difficultés de formation, échecs scolaires liés au handicap, impossibilité de tenir des stages, besoins d'aide au quotidien incompatibles avec un emploi régulier."
                        },
                        {
                            "question": "Un refus RSDAE peut-il être contesté sans nouvelles preuves ?",
                            "answer": "C'est fortement déconseillé. Le RAPO qui reproduit le dossier initial aboutit presque toujours au même refus, puisque la CDAPH réexamine les mêmes pièces. L'efficacité du recours tient aux éléments nouveaux : certificat fonctionnel plus précis, bilan de spécialiste, preuves professionnelles jusque-là absentes, projet de vie restructuré."
                        },
                        {
                            "question": "Qui décide de la reconnaissance de la RSDAE ?",
                            "answer": "C'est la CDAPH (Commission des Droits et de l'Autonomie des Personnes Handicapées) qui décide, sur proposition de l'équipe pluridisciplinaire de la MDPH qui a évalué votre dossier sur pièces. En cas de recours contentieux, c'est le tribunal judiciaire (pôle social) qui tranche, souvent après une expertise médicale judiciaire."
                        },
                        {
                            "question": "Combien de temps faut-il pour constituer un dossier RSDAE solide ?",
                            "answer": "Comptez 3 à 6 semaines en pratique : obtention des rendez-vous médicaux, rédaction des certificats fonctionnels, collecte des pièces professionnelles et rédaction du projet de vie. En cas de refus, anticipez immédiatement : le délai de RAPO n'est que de 2 mois à compter de la notification."
                        }
                    ]
                },
            },
            {
                "slug": "refus-aah-rsdae-non-reconnue",
                "content.maillage": [
                    {"slug": "rsdae-definition-criteres-conditions", "text": "RSDAE : définition, critères et conditions de reconnaissance"},
                    {"slug": "comment-prouver-rsdae", "text": "Comment prouver une RSDAE : éléments, preuves et recours"},
                    {"slug": "refus-mdph-aah-que-faire", "text": "Refus MDPH AAH : recours, délais et solutions"},
                    {"slug": "comment-demander-rqth-strategic", "text": "Demander la RQTH en parallèle de l'AAH"},
                    {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Saisir le pôle social après un refus définitif"},
                    {"href": "/mdph", "text": "MDPH : structurer un dossier solide"},
                    {"href": "/calculatrice-aah", "text": "Simulateur AAH : estimez vos droits"},
                ],
            },
        ],
    },
]


async def apply_pending_migrations(db) -> dict:
    """Run any migration whose id is not yet recorded in `seo_migrations`.

    Returns a small report: {applied: [...], skipped: [...], errors: [...]}
    """
    report = {"applied": [], "skipped": [], "errors": []}
    for migration in MIGRATIONS:
        mid = migration["id"]
        existing = await db.seo_migrations.find_one({"id": mid}, {"_id": 0, "id": 1})
        if existing:
            report["skipped"].append(mid)
            continue
        try:
            modified = 0
            for upd in migration["updates"]:
                slug = upd["slug"]
                set_fields = {k: v for k, v in upd.items() if k not in ("slug", "_upsert")}
                res = await db.seo_pages.update_one({"slug": slug}, {"$set": set_fields}, upsert=upd.get("_upsert", False))
                modified += res.modified_count
            await db.seo_migrations.insert_one({
                "id": mid,
                "description": migration.get("description", ""),
                "applied_at": datetime.now(timezone.utc).isoformat(),
                "updates_count": len(migration["updates"]),
                "modified_count": modified,
            })
            report["applied"].append({"id": mid, "modified": modified, "total_updates": len(migration["updates"])})
            logger.info(f"SEO migration applied: {mid} → {modified}/{len(migration['updates'])} pages modified")
        except Exception as e:
            report["errors"].append({"id": mid, "error": str(e)})
            logger.error(f"SEO migration {mid} failed: {e}")
    return report
