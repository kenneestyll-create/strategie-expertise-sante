"""Seed 15 SEO guide pages — Phase 2 complete content overhaul."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid, os

PAGES = [
# ═══════════════════════════════════════════════════════════════
# BLOC A — 5 PAGES EXISTANTES ÉTOFFÉES
# ═══════════════════════════════════════════════════════════════
{
    "slug": "refus-mdph-aah-que-faire",
    "title": "Refus MDPH pour l'AAH : que faire concrètement pour débloquer la situation ?",
    "meta_description": "Votre demande d'AAH a été refusée par la MDPH ? Au-delà des textes officiels, découvrez les véritables raisons des refus et la stratégie concrète pour obtenir une issue favorable.",
    "category": "mdph",
    "intention": "refus_droits",
    "priority": "p0",
    "cta_type": "dossier_express",
    "cta_label": "Faire analyser mon dossier MDPH",
    "content": {
        "contexte": "L'Allocation aux Adultes Handicapés (AAH) est attribuée par la Commission des Droits et de l'Autonomie des Personnes Handicapées (CDAPH), sur avis de l'équipe pluridisciplinaire de la MDPH. Pour en bénéficier, il faut justifier d'un taux d'incapacité d'au moins 80%, ou d'un taux compris entre 50% et 79% assorti d'une restriction substantielle et durable pour l'accès à l'emploi (RSDAE). Le refus survient quand l'un de ces critères n'est pas reconnu par l'équipe d'évaluation. Ce refus n'est pas définitif : vous disposez de voies de recours clairement encadrées par la loi.",
        "limites": "Les sites institutionnels (Ameli, Service-public.fr, MDPH) vous expliquent les conditions d'éligibilité et la procédure de recours. Ce qu'ils ne vous disent pas, c'est pourquoi votre dossier a échoué alors que votre handicap est réel. La MDPH évalue sur pièces, dans un temps limité, avec des critères qui privilégient les preuves médicales objectives aux réalités de terrain. Un certificat médical qui mentionne une pathologie sans décrire ses conséquences fonctionnelles quotidiennes n'a quasiment aucun poids. Le projet de vie — document pourtant central — est négligé par la majorité des demandeurs, alors qu'il constitue souvent le facteur déterminant pour la RSDAE.",
        "blocages": [
            "Le certificat médical est trop succinct : il mentionne un diagnostic mais pas les limitations fonctionnelles précises (difficultés à la marche, à la concentration, à la station debout prolongée, etc.). L'équipe pluridisciplinaire ne peut pas évaluer ce qu'elle ne peut pas lire.",
            "Le projet de vie est absent ou rédigé en quelques lignes : c'est pourtant le seul document où vous pouvez décrire concrètement l'impact de votre handicap sur votre quotidien. Sans lui, la CDAPH ne dispose que du certificat médical pour statuer.",
            "Les pièces justificatives manquent de cohérence : des rapports de spécialistes contradictoires, des dates incohérentes, ou des bilans trop anciens affaiblissent le dossier. La MDPH cherche une image claire et actualisée de votre situation.",
            "La RSDAE est mal argumentée : pour un taux entre 50% et 79%, il ne suffit pas de dire que vous ne travaillez pas. Il faut démontrer que vos limitations empêchent structurellement l'accès à un emploi durable, avec des éléments médicaux et professionnels à l'appui.",
            "Le recours reproduit le dossier initial : renvoyer les mêmes pièces au RAPO sans modification ni renforcement conduit mécaniquement au même refus."
        ],
        "erreurs": [
            "Laisser passer le délai de 2 mois sans réagir : votre droit de recours est définitivement perdu, sans possibilité de rattrapage.",
            "Rédiger le projet de vie comme un CV ou une lettre de motivation : ce document doit décrire votre journée type, vos difficultés concrètes, ce que vous ne pouvez plus faire seul(e).",
            "Se fier uniquement au médecin traitant : un certificat de spécialiste (psychiatre, rhumatologue, neurologue) qui détaille les limitations fonctionnelles a beaucoup plus de poids.",
            "Minimiser les difficultés par pudeur : la MDPH évalue sur ce qui est écrit, pas sur ce que vous vivez. Si vous ne décrivez pas vos difficultés, elles n'existent pas dans votre dossier.",
            "Confondre taux d'incapacité et taux d'invalidité : ce sont deux notions distinctes évaluées par des organismes différents (MDPH vs CPAM). Un taux d'invalidité de catégorie 2 ne garantit pas un taux MDPH de 80%."
        ],
        "strategie": "La clé d'un recours efficace n'est pas juridique — elle est documentaire. Un dossier MDPH se gagne sur la qualité des preuves médicales et la précision du projet de vie. Notre approche consiste à analyser votre notification de refus pour identifier exactement ce qui a manqué, puis à structurer un dossier de recours qui répond point par point aux critères de la CDAPH. Nous vérifions la cohérence entre le certificat médical, les bilans de spécialistes et le projet de vie. Nous identifions les pièces manquantes et vous orientons vers les examens complémentaires nécessaires. Cette lecture stratégique transforme un dossier « incomplet aux yeux de la MDPH » en un dossier qui remplit objectivement les critères d'attribution.",
        "orientation": [
            "Lisez attentivement votre notification de refus : elle indique le motif précis (taux insuffisant, RSDAE non reconnue) et le délai de recours de 2 mois.",
            "Déposez un recours administratif préalable obligatoire (RAPO) par courrier recommandé à la MDPH. Ce recours est gratuit et suspend le délai contentieux.",
            "Faites rédiger des certificats médicaux détaillés par vos spécialistes, en insistant sur les conséquences fonctionnelles quotidiennes de votre pathologie.",
            "Rédigez un projet de vie complet et structuré : journée type, aide nécessaire, impact sur l'emploi, isolement social.",
            "Si le RAPO est rejeté, saisissez le tribunal judiciaire (pôle social) dans les 2 mois. Une expertise médicale judiciaire est souvent ordonnée."
        ],
        "reassurance": "Le refus d'AAH est l'une des situations les plus fréquentes que nous accompagnons. Plus de 40% des recours RAPO aboutissent à une révision favorable lorsque le dossier est correctement restructuré. Vous avez des droits, et une stratégie documentaire rigoureuse peut changer l'issue de votre demande.",
        "maillage": [
            {"slug": "taux-ipp-5-pourcent-contester", "text": "Taux d'IPP fixé trop bas : comment contester l'évaluation ?"},
            {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Recours devant le tribunal judiciaire : procédure et enjeux"},
            {"slug": "comment-demander-rqth-strategic", "text": "RQTH : au-delà de la demande, la stratégie d'accès aux droits"}
        ],
        "faq": [
            {"question": "Quel est le délai pour contester un refus MDPH ?", "answer": "Vous disposez de 2 mois à compter de la notification de refus pour déposer un recours administratif préalable obligatoire (RAPO) auprès de la MDPH, puis de 2 mois supplémentaires pour saisir le tribunal judiciaire si le RAPO est rejeté."},
            {"question": "Peut-on obtenir l'AAH avec un taux entre 50% et 79% ?", "answer": "Oui, à condition de démontrer une restriction substantielle et durable pour l'accès à l'emploi (RSDAE). Cela nécessite des preuves médicales détaillées et un projet de vie argumenté."}
        ]
    },
},
{
    "slug": "taux-ipp-5-pourcent-contester",
    "title": "Taux d'IPP fixé à 5% alors que vous ne pouvez plus travailler : comment contester efficacement ?",
    "meta_description": "Votre taux d'IPP est sous-évalué malgré des séquelles importantes ? Découvrez les mécanismes réels de fixation du taux et la stratégie pour obtenir une réévaluation juste.",
    "category": "indemnisation",
    "intention": "contestation",
    "priority": "p0",
    "cta_type": "dossier_express",
    "cta_label": "Analyser mon taux d'IPP",
    "content": {
        "contexte": "Le taux d'Incapacité Permanente Partielle (IPP) est fixé par le médecin conseil de la CPAM à la consolidation de votre état de santé, suite à un accident du travail ou une maladie professionnelle. Ce taux détermine directement votre indemnisation : en dessous de 10%, vous percevez un capital forfaitaire unique. Au-dessus de 10%, vous avez droit à une rente viagère. La différence financière entre 9% et 10% se chiffre en dizaines de milliers d'euros sur une vie. Le taux est fixé sur la base du barème indicatif des accidents du travail et maladies professionnelles, mais l'application de ce barème laisse une marge d'appréciation importante au médecin conseil.",
        "limites": "Le barème indicatif AT/MP est public et consultable. Les sites officiels vous expliquent que le taux est fixé en fonction des séquelles fonctionnelles et qu'un coefficient professionnel peut être appliqué. Ce qu'ils ne vous disent pas, c'est que l'examen médical dure rarement plus de 15 à 20 minutes, que le médecin conseil défend les intérêts financiers de l'organisme, et que le coefficient professionnel — qui peut faire basculer un taux de 7% à 12% — est régulièrement sous-évalué ou simplement omis. Le taux médical seul reflète les séquelles anatomiques, pas l'impact réel sur votre capacité à exercer votre métier.",
        "blocages": [
            "L'examen est trop court pour évaluer la complexité des séquelles : en 15 minutes, un médecin ne peut pas apprécier des douleurs chroniques, une fatigue invalidante ou un retentissement psychologique. Il se base principalement sur l'amplitude articulaire et les examens d'imagerie.",
            "Le coefficient professionnel est ignoré : ce coefficient doit majorer le taux médical lorsque les séquelles empêchent la reprise du poste habituel. En pratique, il est souvent fixé à 0% ou 1-2%, même pour des salariés déclarés inaptes.",
            "Les séquelles invisibles ne sont pas prises en compte : douleurs neuropathiques, troubles du sommeil, syndrome anxio-dépressif réactionnel, troubles cognitifs post-traumatiques — ces séquelles sont sous-évaluées car elles ne se « voient » pas sur une radiographie.",
            "Le dossier médical transmis à la CPAM est incomplet : si vos spécialistes n'ont pas transmis l'ensemble de leurs conclusions, le médecin conseil statue sur un dossier partiel.",
            "La victime accepte le taux sans comprendre ses enjeux financiers : la notification ne mentionne pas clairement que la différence entre 9% et 10% représente le passage d'un capital unique à une rente à vie."
        ],
        "erreurs": [
            "Accepter le taux comme définitif : vous disposez de 2 mois pour contester devant la Commission Médicale de Recours Amiable (CMRA).",
            "Se rendre seul à l'expertise CMRA : le médecin conseil de la CPAM sera présent pour défendre le taux initial. Vous devez être accompagné par un médecin de recours (médecin conseil de victime).",
            "Minimiser vos symptômes lors de l'examen : décrivez précisément ce que vous ne pouvez plus faire au quotidien et dans votre travail.",
            "Oublier de demander l'application du coefficient professionnel : si vous êtes inapte ou si vos séquelles vous empêchent de reprendre votre poste, ce coefficient doit être appliqué.",
            "Ne pas vérifier la cohérence entre le taux et le barème : comparez le taux fixé avec le barème indicatif pour votre type de séquelles."
        ],
        "strategie": "La contestation d'un taux d'IPP ne se résume pas à dire « je ne suis pas d'accord ». Elle exige une analyse médicale contradictoire structurée. Notre approche consiste à comparer le taux fixé avec le barème indicatif, à identifier les séquelles non prises en compte ou sous-évaluées, à vérifier l'application du coefficient professionnel, et à constituer un dossier médical argumenté pour la CMRA ou le tribunal. Le médecin de recours, que nous vous orientons à choisir, établit un rapport contradictoire qui reprend chaque séquelle et la positionne dans le barème. C'est cette lecture technique qui fait la différence entre un recours qui aboutit et un recours qui échoue.",
        "orientation": [
            "Vérifiez le délai : vous avez 2 mois à compter de la notification pour saisir la CMRA de votre CPAM par courrier recommandé.",
            "Comparez votre taux avec le barème AT/MP : vérifiez que chaque séquelle a été prise en compte et correctement cotée.",
            "Rassemblez les certificats de vos spécialistes décrivant précisément vos limitations fonctionnelles et l'impact sur votre activité professionnelle.",
            "Faites-vous accompagner par un médecin de recours pour l'expertise CMRA : c'est un investissement qui change souvent le résultat.",
            "Si la CMRA rejette votre recours, saisissez le pôle social du tribunal judiciaire dans les 2 mois. Une expertise judiciaire indépendante sera ordonnée."
        ],
        "reassurance": "La contestation du taux d'IPP est un droit fondamental exercé par des milliers de victimes chaque année. Les réévaluations à la hausse sont fréquentes, et certains taux passent du simple au triple après une expertise contradictoire bien préparée. Votre situation mérite d'être évaluée avec rigueur et défendue avec les bons arguments.",
        "maillage": [
            {"slug": "rente-accident-travail-calcul-contestation", "text": "Rente accident du travail : comprendre le calcul et les moyens de contestation"},
            {"slug": "expertise-medicale-defavorable-recours", "text": "Expertise médicale défavorable : comment contester le rapport ?"},
            {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Saisir le tribunal judiciaire : procédure et stratégie"}
        ],
        "faq": [
            {"question": "Quelle est la différence entre un taux d'IPP de 9% et 10% ?", "answer": "En dessous de 10%, vous recevez un capital forfaitaire unique. À partir de 10%, vous percevez une rente viagère versée tous les trimestres. La différence financière sur une vie peut dépasser 100 000 euros."},
            {"question": "Qu'est-ce que le coefficient professionnel ?", "answer": "C'est un coefficient qui majore le taux médical lorsque les séquelles empêchent la reprise du poste habituel ou réduisent les possibilités professionnelles. Il est souvent sous-évalué ou omis."}
        ]
    },
},
{
    "slug": "expertise-medicale-defavorable-recours",
    "title": "Expertise médicale défavorable : vos séquelles ont été minimisées, quels sont vos recours concrets ?",
    "meta_description": "L'expert a sous-évalué vos séquelles ? Découvrez les mécanismes de contestation et la stratégie pour obtenir une expertise contradictoire efficace.",
    "category": "expertise",
    "intention": "desaccord_medical",
    "priority": "p0",
    "cta_type": "accompagnement",
    "cta_label": "Être accompagné pour contester",
    "content": {
        "contexte": "L'expertise médicale est une étape décisive dans tout litige médico-légal : accident du travail, maladie professionnelle, accident de la route, faute médicale. L'expert, désigné par un tribunal ou une compagnie d'assurance, évalue vos séquelles et rédige un rapport qui servira de base à la décision d'indemnisation. Ce rapport a un poids considérable : les juges s'en écartent rarement. Lorsque l'expert minimise vos séquelles, c'est l'ensemble de votre indemnisation qui est compromise.",
        "limites": "Les textes vous informent que vous pouvez être assisté lors de l'expertise et que vous pouvez formuler des observations (dires) après réception du rapport. Ce qu'ils ne précisent pas, c'est que l'expertise est un exercice asymétrique : l'expert a une mission technique, un cadre temporel limité, et parfois une approche conservatrice. Il n'a pas vocation à défendre vos intérêts. Les compagnies d'assurance, elles, envoient systématiquement leur propre médecin conseil pour orienter l'évaluation. Si vous n'êtes pas accompagné, vous êtes seul face à deux médecins qui ne sont pas de votre côté.",
        "blocages": [
            "L'examen dure souvent moins de 30 minutes : impossible d'évaluer correctement des séquelles complexes, multiples ou invisibles dans ce temps.",
            "Les séquelles psychologiques sont sous-évaluées : syndrome de stress post-traumatique, anxiété, dépression réactionnelle — ces séquelles sont souvent qualifiées de « préexistantes » ou « sans lien direct » avec l'événement.",
            "L'expert ne dispose pas de tout le dossier : si vos pièces médicales ne sont pas classées chronologiquement et transmises complètement, l'expert travaille sur un dossier partiel.",
            "Le médecin conseil de l'assurance oriente l'expertise : présent lors de l'examen, il pose des questions orientées et influence subtilement les conclusions.",
            "Le rapport contient des erreurs factuelles : dates incorrectes, antécédents confondus, symptômes omis — ces erreurs passent souvent inaperçues si le rapport n'est pas lu avec attention."
        ],
        "erreurs": [
            "Ne pas lire le rapport d'expertise en détail : vérifiez chaque date, chaque antécédent, chaque conclusion. Les erreurs factuelles sont un levier de contestation puissant.",
            "Ne pas formuler de dire dans les délais impartis : c'est votre seul moyen officiel de contester le rapport avant la décision.",
            "Se rendre à l'expertise sans dossier médical organisé : apportez tous vos documents classés par date, avec un récapitulatif écrit de vos séquelles.",
            "Ne pas se faire accompagner par un médecin de recours : c'est l'erreur la plus coûteuse. Seul un professionnel peut contrebalancer techniquement les conclusions de l'expert.",
            "Accepter les conclusions sans contester : un rapport d'expertise n'est pas une décision définitive. Vous avez des voies de recours."
        ],
        "strategie": "La contestation d'une expertise défavorable repose sur trois piliers : le dire médical argumenté, le rapport critique du médecin de recours, et la demande de contre-expertise ou d'expertise complémentaire. Notre approche consiste à analyser le rapport ligne par ligne, à identifier les incohérences, les omissions et les sous-évaluations, puis à structurer un dire technique qui pointe précisément les failles. Nous vous orientons vers un médecin de recours spécialisé dans votre type de séquelles, qui rédigera un rapport contradictoire positionné sur le barème. C'est cette argumentation médico-légale structurée qui permet au juge d'ordonner une nouvelle mesure d'expertise.",
        "orientation": [
            "Demandez communication du rapport d'expertise complet — c'est votre droit. Lisez-le intégralement et relevez les erreurs factuelles.",
            "Rédigez un dire (observations écrites) dans le délai imparti, en pointant les inexactitudes, omissions et contradictions du rapport.",
            "Faites rédiger un rapport critique par un médecin de recours qui analysera point par point les conclusions de l'expert.",
            "Si l'expertise est judiciaire, demandez au tribunal une contre-expertise avec un autre expert ou une expertise complémentaire.",
            "Rassemblez les attestations de votre entourage et de vos soignants décrivant l'impact réel de vos séquelles sur votre quotidien."
        ],
        "reassurance": "Une expertise défavorable n'est jamais une fin de parcours. Les dires, rapports critiques et contre-expertises permettent régulièrement de rétablir une évaluation juste. Le rapport d'expertise est un avis technique, pas un jugement. Avec les bons arguments médicaux et une stratégie documentaire solide, il est possible de faire réviser des conclusions qui ne reflètent pas votre réalité.",
        "maillage": [
            {"slug": "taux-ipp-5-pourcent-contester", "text": "Taux d'IPP sous-évalué : stratégie de contestation"},
            {"slug": "comment-preparer-expertise-medicale", "text": "Comment préparer une expertise médicale : les clés d'un dossier solide"},
            {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Recours devant le tribunal : quand et comment saisir le juge"}
        ],
        "faq": [
            {"question": "Peut-on contester un rapport d'expertise médicale ?", "answer": "Oui, vous pouvez formuler des dires (observations écrites), faire rédiger un rapport critique par un médecin de recours, et demander une contre-expertise ou expertise complémentaire au tribunal."},
            {"question": "Faut-il se faire accompagner à une expertise médicale ?", "answer": "C'est fortement recommandé. Un médecin de recours (médecin conseil de victime) rééquilibre l'expertise face au médecin conseil de l'assurance et veille à ce que toutes vos séquelles soient correctement évaluées."}
        ]
    },
},
{
    "slug": "accident-travail-non-declare-employeur",
    "title": "Accident du travail non déclaré par l'employeur : comment protéger vos droits et obtenir réparation ?",
    "meta_description": "Votre employeur refuse ou oublie de déclarer votre accident du travail ? Découvrez vos droits réels, les blocages fréquents et la stratégie pour obtenir la prise en charge.",
    "category": "accident_travail",
    "intention": "urgence",
    "priority": "p0",
    "cta_type": "dossier_express",
    "cta_label": "Faire analyser ma situation",
    "content": {
        "contexte": "L'employeur a l'obligation légale de déclarer tout accident du travail à la CPAM dans les 48 heures suivant sa connaissance des faits (article L.441-2 du Code de la Sécurité sociale). Cette déclaration conditionne votre prise en charge : soins remboursés à 100% sans avance de frais, indemnités journalières majorées (sans délai de carence), et reconnaissance officielle de l'origine professionnelle de votre accident. Sans déclaration, vous êtes traité comme un arrêt maladie ordinaire — avec toutes les conséquences financières et juridiques que cela implique.",
        "limites": "Les textes officiels vous disent que l'employeur doit déclarer et que vous pouvez le faire vous-même à défaut. Ce qu'ils ne vous expliquent pas, c'est pourquoi l'employeur ne déclare pas et comment réagir stratégiquement. Le refus de déclaration n'est jamais anodin : il peut viser à éviter une hausse du taux de cotisation AT/MP de l'entreprise, à contester le caractère professionnel de l'accident, ou à masquer des conditions de travail dangereuses. Comprendre la motivation de l'employeur permet d'adapter votre stratégie.",
        "blocages": [
            "L'employeur minimise l'événement : « ce n'est qu'une petite chute », « tu n'as rien de grave » — ces phrases visent à vous dissuader de faire constater médicalement l'accident et à laisser passer les délais.",
            "L'employeur propose un arrangement : arrêt maladie au lieu d'arrêt AT, maintien de salaire « sous le manteau », promesse de régularisation. Ces arrangements vous pénalisent systématiquement à moyen terme.",
            "Le certificat médical initial n'est pas établi le jour même : plus le temps passe entre l'accident et la constatation médicale, plus la CPAM peut contester le lien entre les lésions et l'accident.",
            "Les témoins ne veulent pas témoigner : collègues sous pression, peur de représailles. C'est un blocage fréquent qui affaiblit le dossier.",
            "La CPAM mène une enquête contradictoire : elle interroge l'employeur qui conteste les circonstances. Si votre version n'est pas étayée par des preuves, la CPAM peut refuser la prise en charge."
        ],
        "erreurs": [
            "Attendre que l'employeur finisse par déclarer : chaque jour qui passe affaiblit votre dossier. Agissez vous-même dans les meilleurs délais.",
            "Accepter un arrêt maladie classique : la différence d'indemnisation est considérable (pas de délai de carence en AT, indemnités plus élevées, soins 100%).",
            "Ne pas faire constater les lésions le jour même ou le lendemain : le certificat médical initial est la pièce maîtresse de votre dossier.",
            "Ne pas conserver les preuves : SMS, emails, témoignages écrits de collègues, photos des lieux, registre des accidents bénins — tout est utile.",
            "Hésiter par peur de représailles : un salarié ne peut pas être sanctionné pour avoir déclaré un accident du travail. C'est un droit protégé par la loi."
        ],
        "strategie": "Face à un employeur qui ne déclare pas, la stratégie doit être rapide et documentée. Notre approche consiste à vérifier que le certificat médical initial a bien été établi, à constituer un dossier de preuves solide avant la déclaration directe à la CPAM, et à anticiper l'enquête contradictoire que la CPAM pourrait mener. Nous vérifions la cohérence entre vos déclarations, les pièces médicales et les circonstances de l'accident. Si l'employeur conteste, nous vous préparons à répondre point par point. L'objectif est que la CPAM dispose de tous les éléments pour reconnaître le caractère professionnel de l'accident, malgré l'absence de déclaration employeur.",
        "orientation": [
            "Consultez un médecin immédiatement et obtenez un certificat médical initial (CMI) décrivant les lésions et mentionnant qu'elles résultent d'un accident du travail.",
            "Déclarez vous-même l'accident à votre CPAM par courrier recommandé — vous avez 2 ans pour le faire (article L.441-2 CSS).",
            "Rassemblez toutes les preuves disponibles : témoignages écrits de collègues, SMS/emails, photos, registre des accidents bénins de l'entreprise.",
            "Adressez une mise en demeure à votre employeur par courrier recommandé, rappelant son obligation de déclaration et les sanctions encourues.",
            "Si la CPAM refuse la prise en charge, contestez devant la Commission de Recours Amiable (CRA) dans les 2 mois."
        ],
        "reassurance": "La non-déclaration par l'employeur est un problème que nous rencontrons régulièrement. La loi vous protège pleinement : vous pouvez déclarer l'accident vous-même, et les tribunaux sont très vigilants sur ce type de situation. Un dossier bien préparé, déposé dans les temps, aboutit très majoritairement à la reconnaissance du caractère professionnel.",
        "maillage": [
            {"slug": "faute-inexcusable-employeur", "text": "Faute inexcusable de l'employeur : une indemnisation complémentaire possible"},
            {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus de maladie professionnelle par la CPAM : vos recours"},
            {"slug": "delai-prescription-maladie-professionnelle", "text": "Délais de prescription : ne perdez pas vos droits"}
        ],
        "faq": [
            {"question": "Un salarié peut-il déclarer lui-même un accident du travail ?", "answer": "Oui, le salarié ou ses ayants droit peuvent déclarer l'accident directement auprès de la CPAM dans un délai de 2 ans suivant l'accident."},
            {"question": "Quelles sanctions pour un employeur qui ne déclare pas un AT ?", "answer": "L'employeur s'expose à une contravention de 4e classe. De plus, la CPAM peut lui imputer les frais de prise en charge et les indemnités versées au salarié."}
        ]
    },
},
{
    "slug": "refus-maladie-professionnelle-cpam-recours",
    "title": "Refus de maladie professionnelle par la CPAM : vous avez 2 mois pour agir, voici comment",
    "meta_description": "La CPAM refuse de reconnaître votre maladie professionnelle ? Comprenez les véritables raisons du refus et la stratégie pour obtenir la reconnaissance.",
    "category": "accident_travail",
    "intention": "urgence",
    "priority": "p0",
    "cta_type": "dossier_express",
    "cta_label": "Analyser mon dossier de refus",
    "content": {
        "contexte": "La reconnaissance d'une maladie professionnelle suit une procédure stricte définie par le Code de la Sécurité sociale. Si votre pathologie figure dans l'un des tableaux de maladies professionnelles et que toutes les conditions sont remplies (délai de prise en charge, durée d'exposition, travaux effectués), la reconnaissance est en principe automatique — c'est la présomption d'origine professionnelle. Lorsque la CPAM refuse, c'est qu'elle estime qu'une condition du tableau n'est pas remplie, ou que la maladie ne figure pas dans les tableaux. Le refus déclenche un délai de recours de 2 mois qui court à compter de la notification.",
        "limites": "Les sites institutionnels vous expliquent les conditions des tableaux et la procédure de recours. Ce qu'ils ne vous montrent pas, c'est la complexité réelle de la preuve. Les tableaux de maladies professionnelles sont rédigés dans un langage technique qui laisse place à l'interprétation. La CPAM peut considérer que votre poste ne figure pas dans la « liste limitative des travaux » du tableau, que votre durée d'exposition est insuffisante, ou que le délai de prise en charge est dépassé — alors même que votre maladie est directement liée à votre activité. Par ailleurs, pour les pathologies hors tableau, la procédure CRRMP est méconnue et sous-utilisée.",
        "blocages": [
            "Une condition du tableau n'est pas strictement remplie : par exemple, la liste des travaux mentionne « manipulation de charges lourdes » et votre fiche de poste ne le précise pas, alors que vous portiez quotidiennement des charges de 25 kg.",
            "Le délai de prise en charge est dépassé de quelques mois : le tableau fixe un délai strict entre la fin de l'exposition et l'apparition de la maladie. Un dépassement même minime peut entraîner un refus.",
            "La CPAM conteste le lien entre la maladie et l'exposition professionnelle : le médecin conseil de la CPAM estime que la pathologie a une cause extra-professionnelle (âge, mode de vie, antécédents).",
            "Les fiches d'exposition aux risques professionnels sont incomplètes ou inexistantes : l'employeur n'a pas documenté les expositions, ce qui affaiblit la preuve.",
            "La procédure CRRMP n'est pas demandée : pour les maladies hors tableau ou lorsque les conditions du tableau ne sont pas toutes remplies, le Comité Régional de Reconnaissance des Maladies Professionnelles peut reconnaître la maladie si elle est directement causée par le travail."
        ],
        "erreurs": [
            "Laisser passer le délai de 2 mois : c'est le piège le plus fréquent et le plus grave. Passé ce délai, votre droit de recours est éteint définitivement.",
            "Ne pas demander le dossier complet à la CPAM : vous avez le droit d'accéder à l'intégralité de votre dossier, y compris les avis du médecin conseil et les résultats de l'enquête.",
            "Oublier de mentionner des expositions chez d'anciens employeurs : le cumul d'exposition sur l'ensemble de la carrière professionnelle est pris en compte.",
            "Confondre arrêt maladie et maladie professionnelle : les enjeux financiers, juridiques et professionnels sont radicalement différents.",
            "Ne pas solliciter le CRRMP quand les conditions du tableau ne sont pas toutes remplies : c'est une voie de reconnaissance trop souvent ignorée."
        ],
        "strategie": "Le recours contre un refus de maladie professionnelle exige une analyse technique précise du motif de refus. Notre approche consiste à identifier exactement quelle condition fait défaut, à évaluer si cette condition peut être prouvée autrement (attestations, fiches de poste, études épidémiologiques), et à structurer un dossier qui comble les lacunes identifiées par la CPAM. Pour les cas hors tableau ou les conditions non remplies, nous vérifions l'opportunité d'une saisine du CRRMP et constituons un dossier médical et professionnel argumenté. Cette analyse stratégique permet d'orienter le recours vers la voie la plus favorable.",
        "orientation": [
            "Saisissez la Commission de Recours Amiable (CRA) de votre CPAM dans les 2 mois par courrier recommandé — c'est gratuit.",
            "Identifiez le motif précis du refus : condition du tableau non remplie, pathologie hors tableau, lien causal contesté.",
            "Demandez l'accès complet à votre dossier CPAM : avis du médecin conseil, rapport d'enquête, colloque médico-administratif.",
            "Reconstituez votre historique d'exposition : tous les postes, tous les employeurs, toutes les tâches impliquant l'exposition au risque.",
            "En cas de rejet par la CRA, saisissez le pôle social du tribunal judiciaire dans les 2 mois."
        ],
        "reassurance": "Le refus de reconnaissance de maladie professionnelle est une situation que nous traitons quotidiennement. De nombreux refus sont infirmés en recours — devant la CRA, le CRRMP ou le tribunal. Le plus important est de réagir dans les délais et de structurer votre dossier avec rigueur. Les voies de reconnaissance existent, y compris pour les situations atypiques.",
        "maillage": [
            {"slug": "delai-prescription-maladie-professionnelle", "text": "Délai de prescription maladie professionnelle : les erreurs qui vous font perdre vos droits"},
            {"slug": "accident-travail-non-declare-employeur", "text": "Accident du travail non déclaré : protéger vos droits"},
            {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Tribunal judiciaire pôle social : procédure et enjeux"}
        ],
        "faq": [
            {"question": "Qu'est-ce que le CRRMP ?", "answer": "Le Comité Régional de Reconnaissance des Maladies Professionnelles examine les demandes lorsque la maladie ne figure pas dans les tableaux ou lorsque les conditions du tableau ne sont pas toutes remplies. Il peut reconnaître la maladie si elle est directement causée par le travail et a entraîné une IPP d'au moins 25%."},
            {"question": "Peut-on contester un refus de maladie professionnelle après 2 mois ?", "answer": "Non, le délai de 2 mois pour saisir la CRA est un délai de forclusion. Passé ce délai, vous perdez définitivement votre droit de recours contre cette décision."}
        ]
    },
},
# ═══════════════════════════════════════════════════════════════
# BLOC B — 5 NOUVELLES PAGES SEO
# ═══════════════════════════════════════════════════════════════
{
    "slug": "faute-inexcusable-employeur",
    "title": "Faute inexcusable de l'employeur : comment agir concrètement pour obtenir une indemnisation complémentaire",
    "meta_description": "Votre employeur connaissait le danger et n'a rien fait ? Découvrez les conditions réelles de la faute inexcusable et la stratégie pour obtenir une réparation intégrale.",
    "category": "accident_travail",
    "intention": "perte_financiere",
    "priority": "p0",
    "cta_type": "accompagnement",
    "cta_label": "Évaluer ma situation",
    "content": {
        "contexte": "La faute inexcusable de l'employeur est un mécanisme juridique qui permet à la victime d'un accident du travail ou d'une maladie professionnelle d'obtenir une indemnisation complémentaire, au-delà des prestations versées par la CPAM. Elle est reconnue lorsque l'employeur avait ou aurait dû avoir conscience du danger auquel le salarié était exposé, et qu'il n'a pas pris les mesures nécessaires pour l'en protéger (article L.452-1 CSS). Depuis la jurisprudence constante de la Cour de cassation, cette définition s'est élargie : l'obligation de sécurité de l'employeur est une obligation de résultat.",
        "limites": "Les textes officiels vous donnent la définition légale et la procédure. Ce qu'ils ne vous montrent pas, c'est que la reconnaissance de la faute inexcusable est un combat judiciaire qui nécessite de prouver deux éléments cumulatifs : la conscience du danger par l'employeur ET l'absence de mesures de prévention. En pratique, la conscience du danger est présumée dès lors que le risque était connu (document unique d'évaluation des risques, signalement au CHSCT, précédents dans l'entreprise). Mais l'employeur se défend systématiquement en affirmant avoir pris toutes les mesures nécessaires. C'est sur ce terrain que se joue réellement la procédure.",
        "blocages": [
            "Le document unique d'évaluation des risques (DUERP) ne mentionne pas le risque en cause : l'employeur argue qu'il n'avait pas conscience du danger. Or, l'absence du risque dans le DUERP peut aussi démontrer une carence dans l'évaluation des risques.",
            "L'employeur produit des attestations de formation : il tente de prouver qu'il a pris des mesures préventives, même si ces formations étaient insuffisantes ou inadaptées au risque réel.",
            "Le salarié a lui-même commis une imprudence : la faute de la victime ne supprime pas la faute inexcusable de l'employeur, sauf si cette faute est la cause exclusive de l'accident (ce qui est très rarement reconnu).",
            "La procédure est longue : tentative de conciliation devant la CPAM, puis tribunal judiciaire pôle social. L'employeur fait souvent traîner la procédure.",
            "L'évaluation des préjudices complémentaires est complexe : souffrances physiques et morales, préjudice esthétique, préjudice d'agrément, perte de possibilité de promotion — chaque poste doit être évalué et prouvé."
        ],
        "erreurs": [
            "Croire que la faute inexcusable est réservée aux accidents graves : même un accident « mineur » peut donner lieu à reconnaissance si l'employeur n'a pas respecté son obligation de sécurité.",
            "Ne pas conserver les preuves de la connaissance du danger par l'employeur : comptes-rendus de CHSCT, alertes syndicales, signalements au registre des dangers, emails d'alerte.",
            "Engager la procédure sans évaluation préalable des chances de succès : la faute inexcusable est un mécanisme technique qui nécessite des preuves spécifiques.",
            "Oublier de demander la majoration de rente : en cas de faute inexcusable reconnue, votre rente est majorée à son maximum. C'est un droit, pas une option.",
            "Ne pas demander l'indemnisation de tous les préjudices complémentaires : souffrances, esthétique, agrément, adaptation du logement — chaque poste de préjudice doit être réclamé."
        ],
        "strategie": "La faute inexcusable se prépare comme un dossier judiciaire : il faut des preuves, une chronologie, et une argumentation juridique solide. Notre approche consiste à rechercher tous les éléments prouvant la conscience du danger par l'employeur (DUERP, CHSCT, accidents antérieurs, signalements) et l'insuffisance des mesures de prévention. Nous évaluons les chances de succès avant d'engager la procédure, et nous vous orientons vers les experts médicaux capables d'évaluer précisément chaque poste de préjudice. L'objectif est d'obtenir une réparation intégrale : majoration de rente + indemnisation de tous les préjudices personnels.",
        "orientation": [
            "Rassemblez les preuves de la connaissance du danger : DUERP, PV de CHSCT/CSE, signalements, accidents précédents sur le même poste.",
            "Engagez une tentative de conciliation devant votre CPAM — c'est un préalable obligatoire avant la saisine du tribunal.",
            "En l'absence d'accord, saisissez le pôle social du tribunal judiciaire. Le délai est de 2 ans à compter de la reconnaissance de l'AT/MP.",
            "Faites évaluer vos préjudices par un médecin de recours : souffrances, esthétique, agrément, perte de promotion, aménagement du logement.",
            "Demandez la majoration de la rente au maximum légal et l'indemnisation de chaque poste de préjudice complémentaire."
        ],
        "reassurance": "La faute inexcusable est un droit fondamental des victimes d'accidents du travail et de maladies professionnelles. Elle permet une réparation bien plus complète que les seules prestations CPAM. Avec un dossier correctement constitué et une stratégie argumentée, la reconnaissance est obtenue dans une majorité de cas.",
        "maillage": [
            {"slug": "accident-travail-non-declare-employeur", "text": "Accident du travail non déclaré : comment protéger vos droits"},
            {"slug": "rente-accident-travail-calcul-contestation", "text": "Rente accident du travail : comprendre le calcul et contester"},
            {"slug": "taux-ipp-5-pourcent-contester", "text": "Taux d'IPP sous-évalué : stratégie de contestation"}
        ],
        "faq": [
            {"question": "Quel est le délai pour agir en faute inexcusable ?", "answer": "Vous disposez de 2 ans à compter de la reconnaissance du caractère professionnel de l'accident ou de la maladie pour engager la procédure de faute inexcusable."},
            {"question": "La faute inexcusable augmente-t-elle ma rente ?", "answer": "Oui, en cas de faute inexcusable reconnue, votre rente est majorée à son montant maximum. De plus, vous pouvez obtenir l'indemnisation de préjudices complémentaires non couverts par la rente."}
        ]
    },
},
{
    "slug": "inaptitude-travail-droits-recours",
    "title": "Inaptitude au travail : vos droits réels, les blocages et les recours face à l'employeur",
    "meta_description": "Déclaré inapte par le médecin du travail ? Découvrez vos droits concrets, les obligations réelles de l'employeur et les recours en cas de blocage.",
    "category": "emploi",
    "intention": "urgence",
    "priority": "p0",
    "cta_type": "accompagnement",
    "cta_label": "Analyser ma situation d'inaptitude",
    "content": {
        "contexte": "L'inaptitude au travail est prononcée par le médecin du travail lorsqu'il constate que l'état de santé du salarié est incompatible avec son poste de travail. Cette décision déclenche une obligation de reclassement pour l'employeur (article L.1226-2 et L.1226-10 du Code du travail). Si aucun reclassement n'est possible, l'employeur peut procéder au licenciement pour inaptitude. Les droits du salarié varient selon que l'inaptitude est d'origine professionnelle (AT/MP) ou non professionnelle — une distinction cruciale que beaucoup de salariés ignorent.",
        "limites": "Les textes officiels décrivent la procédure : visite médicale, avis d'inaptitude, recherche de reclassement, licenciement éventuel. Ce qu'ils ne vous montrent pas, c'est que l'obligation de reclassement est souvent traitée comme une formalité par les employeurs. Certains envoient une lettre type de recherche de reclassement, reçoivent une réponse négative de leurs établissements, et procèdent au licenciement — le tout en quelques jours. Or, l'obligation de reclassement est une obligation sérieuse et loyale qui impose à l'employeur de rechercher activement des postes compatibles, y compris avec des aménagements ou des mutations.",
        "blocages": [
            "L'employeur expédie la recherche de reclassement : une simple lettre circulaire ne suffit pas. L'employeur doit rechercher loyalement des postes compatibles dans l'entreprise et le groupe, avec aménagements si nécessaire.",
            "Le salarié ne connaît pas la distinction AT/MP vs non professionnel : en cas d'inaptitude d'origine professionnelle, les indemnités de licenciement sont doublées et une indemnité compensatrice de préavis est due.",
            "L'employeur tarde à agir : après l'avis d'inaptitude, l'employeur a 1 mois pour reclasser ou licencier. Passé ce délai, il doit reprendre le versement du salaire.",
            "L'avis d'inaptitude ne mentionne pas toutes les restrictions : si le médecin du travail n'a pas précisé suffisamment les contre-indications, l'employeur peut proposer un reclassement inadapté.",
            "Le salarié conteste l'avis d'inaptitude au lieu de contester le licenciement : les deux recours existent mais n'ont pas les mêmes effets ni les mêmes délais."
        ],
        "erreurs": [
            "Accepter un licenciement pour inaptitude sans vérifier que l'obligation de reclassement a été respectée : c'est le motif de contestation le plus fréquent et le plus efficace.",
            "Ne pas faire requalifier l'inaptitude en origine professionnelle quand elle résulte d'un AT/MP : la différence d'indemnisation est considérable.",
            "Signer une rupture conventionnelle au lieu d'un licenciement pour inaptitude : vous perdez les indemnités spéciales d'inaptitude professionnelle.",
            "Ne pas consulter le CSE : l'avis du Comité Social et Économique est obligatoire avant tout licenciement pour inaptitude. Son absence rend le licenciement nul.",
            "Ignorer le délai d'1 mois : si l'employeur ne vous a ni reclassé ni licencié dans le mois suivant l'avis d'inaptitude, il doit reprendre le versement de votre salaire."
        ],
        "strategie": "L'inaptitude au travail est un moment critique qui détermine vos droits pour les mois et années à venir. Notre approche consiste à vérifier trois points essentiels : l'origine de l'inaptitude (professionnelle ou non), la réalité de la recherche de reclassement par l'employeur, et la conformité de la procédure de licenciement. Si l'inaptitude est d'origine professionnelle, nous vérifions que l'indemnité spéciale de licenciement (double de l'indemnité légale) et l'indemnité compensatrice de préavis ont bien été versées. Si la recherche de reclassement est insuffisante, le licenciement peut être contesté devant le Conseil de Prud'hommes avec des dommages et intérêts significatifs.",
        "orientation": [
            "Vérifiez l'origine de votre inaptitude : résulte-t-elle d'un accident du travail, d'une maladie professionnelle, ou d'une cause non professionnelle ? Cela change vos droits.",
            "Demandez une copie de l'avis d'inaptitude et des propositions de reclassement faites par l'employeur.",
            "Vérifiez que le CSE a bien été consulté avant le licenciement.",
            "Contrôlez le montant des indemnités : indemnité spéciale de licenciement (double si origine pro) + indemnité compensatrice de préavis (si origine pro).",
            "En cas de doute sur la loyauté du reclassement, consultez un avocat en droit du travail dans les 12 mois suivant la notification du licenciement."
        ],
        "reassurance": "L'inaptitude au travail est une situation que nous accompagnons régulièrement. Les irrégularités dans la procédure de reclassement et de licenciement sont fréquentes et ouvrent droit à des indemnisations substantielles. Vos droits existent — l'enjeu est de les identifier et de les faire valoir au bon moment.",
        "maillage": [
            {"slug": "faute-inexcusable-employeur", "text": "Faute inexcusable de l'employeur : obtenir une indemnisation complémentaire"},
            {"slug": "rente-accident-travail-calcul-contestation", "text": "Rente accident du travail : ce que vous devez savoir"},
            {"slug": "accident-travail-non-declare-employeur", "text": "Accident du travail non déclaré : protéger vos droits en amont"}
        ],
        "faq": [
            {"question": "Quelle indemnité en cas de licenciement pour inaptitude professionnelle ?", "answer": "En cas d'inaptitude d'origine professionnelle (AT/MP), vous avez droit à une indemnité spéciale de licenciement égale au double de l'indemnité légale, plus une indemnité compensatrice de préavis."},
            {"question": "L'employeur peut-il licencier immédiatement après un avis d'inaptitude ?", "answer": "Non, il doit d'abord rechercher loyalement un reclassement, consulter le CSE, et ce n'est qu'en cas d'impossibilité avérée de reclassement qu'il peut procéder au licenciement."}
        ]
    },
},
{
    "slug": "rente-accident-travail-calcul-contestation",
    "title": "Rente accident du travail : comprendre le calcul réel, ses limites et les moyens de contestation",
    "meta_description": "Votre rente AT semble trop basse ? Découvrez comment le calcul est réellement effectué, les erreurs fréquentes et la stratégie pour obtenir une réévaluation.",
    "category": "indemnisation",
    "intention": "perte_financiere",
    "priority": "p0",
    "cta_type": "dossier_express",
    "cta_label": "Vérifier le calcul de ma rente",
    "content": {
        "contexte": "La rente accident du travail ou maladie professionnelle est versée lorsque le taux d'IPP est fixé à 10% ou plus. Son montant est calculé à partir de deux éléments : votre salaire annuel de référence et votre taux d'IPP. Mais le calcul n'est pas linéaire : le taux est réduit de moitié pour la partie inférieure à 50%, puis multiplié par 1,5 pour la partie supérieure à 50%. Cette formule, peu intuitive, produit des montants souvent inférieurs aux attentes des victimes.",
        "limites": "Les sites officiels vous donnent la formule de calcul et les modalités de versement. Ce qu'ils ne vous expliquent pas, c'est que le salaire de référence est plafonné et que des erreurs de calcul existent. Le salaire pris en compte est celui des 12 mois précédant l'arrêt de travail, avec un minimum et un maximum fixés par la Sécurité sociale. Si vous avez été en temps partiel, en arrêt maladie, ou en chômage partiel pendant cette période, votre salaire de référence peut être artificiellement bas. Par ailleurs, le coefficient professionnel appliqué au taux d'IPP impacte directement le montant de la rente, mais ses modalités d'application sont rarement expliquées.",
        "blocages": [
            "Le salaire de référence est calculé sur une période défavorable : temps partiel, maladie, chômage technique — ces périodes abaissent artificiellement le salaire annuel de référence.",
            "Le taux d'IPP est sous-évalué : un taux de 9% au lieu de 12% change radicalement l'indemnisation (capital unique vs rente à vie).",
            "Le coefficient professionnel n'est pas appliqué ou est sous-évalué : ce coefficient peut augmenter significativement le taux servant au calcul de la rente.",
            "La rente n'est pas revalorisée correctement : les rentes doivent être revalorisées chaque année selon un coefficient fixé par arrêté. Vérifiez que vos versements suivent ces revalorisations.",
            "La victime ne sait pas que la rente est cumulable avec d'autres prestations : pension d'invalidité, AAH sous conditions, allocations chômage — les règles de cumul sont complexes mais des droits existent."
        ],
        "erreurs": [
            "Ne pas vérifier le salaire de référence retenu par la CPAM : demandez le détail du calcul et comparez avec vos bulletins de paie.",
            "Accepter un taux d'IPP de 9% sans contester : la différence entre 9% et 10% est un capital unique vs une rente à vie.",
            "Ignorer la possibilité de demander une révision du taux : si votre état de santé s'aggrave, vous pouvez demander une révision du taux d'IPP.",
            "Confondre rente AT et pension d'invalidité : ce sont deux prestations distinctes versées par des organismes différents.",
            "Ne pas demander le rachat partiel de la rente : sous certaines conditions, une partie de la rente peut être convertie en capital."
        ],
        "strategie": "L'analyse d'une rente AT nécessite de vérifier trois éléments : le taux d'IPP (est-il correctement fixé ?), le salaire de référence (la période retenue est-elle la plus favorable ?), et le coefficient professionnel (est-il appliqué et correctement évalué ?). Notre approche consiste à recalculer votre rente à partir des données brutes pour identifier les écarts entre ce que vous percevez et ce que vous devriez percevoir. Si le taux d'IPP est contestable, nous orientons vers une procédure de contestation. Si le salaire de référence est défavorable, nous vérifions les possibilités de correction.",
        "orientation": [
            "Demandez à votre CPAM le détail du calcul de votre rente : salaire de référence, taux retenu, coefficient professionnel appliqué.",
            "Comparez le salaire de référence avec vos 12 derniers bulletins de paie avant l'arrêt.",
            "Si votre taux d'IPP est inférieur à 10%, contestez-le dans les délais (voir notre guide sur la contestation du taux d'IPP).",
            "Si votre état s'aggrave, demandez une révision du taux d'IPP auprès de votre CPAM.",
            "Vérifiez que votre rente est correctement revalorisée chaque année."
        ],
        "reassurance": "La rente AT est un droit acquis qui vous accompagne tout au long de votre vie. Son montant peut être contesté et réévalué si le taux d'IPP ou le salaire de référence sont incorrects. De nombreuses victimes perçoivent une rente inférieure à ce qu'elles devraient recevoir — une vérification rigoureuse peut révéler des écarts significatifs.",
        "maillage": [
            {"slug": "taux-ipp-5-pourcent-contester", "text": "Taux d'IPP sous-évalué : la stratégie de contestation"},
            {"slug": "faute-inexcusable-employeur", "text": "Faute inexcusable : une indemnisation complémentaire à la rente"},
            {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Tribunal judiciaire : contester les décisions de la CPAM"}
        ],
        "faq": [
            {"question": "Comment est calculée la rente accident du travail ?", "answer": "La rente est calculée sur le salaire annuel de référence multiplié par le taux utile. Le taux utile correspond au taux d'IPP réduit de moitié pour la partie inférieure à 50% et majoré de moitié pour la partie supérieure à 50%."},
            {"question": "Peut-on cumuler rente AT et pension d'invalidité ?", "answer": "Oui, mais sous certaines conditions et avec des règles de cumul spécifiques. Le cumul est possible si les deux prestations portent sur des risques différents."}
        ]
    },
},
{
    "slug": "recours-tribunal-judiciaire-pole-social",
    "title": "Recours devant le tribunal judiciaire pôle social : comprendre la procédure et les enjeux réels",
    "meta_description": "Vous devez saisir le tribunal pour contester une décision CPAM ou MDPH ? Découvrez la procédure réelle, les délais et la stratégie pour maximiser vos chances.",
    "category": "indemnisation",
    "intention": "contestation",
    "priority": "p0",
    "cta_type": "accompagnement",
    "cta_label": "Préparer mon recours",
    "content": {
        "contexte": "Le pôle social du tribunal judiciaire (anciennement TASS - Tribunal des Affaires de Sécurité Sociale) est la juridiction compétente pour les litiges entre les assurés et les organismes de sécurité sociale (CPAM, MDPH, MSA). C'est devant ce tribunal que vous contestez un refus de reconnaissance d'AT/MP, un taux d'IPP, un refus d'AAH après RAPO, ou toute autre décision d'un organisme social. La procédure est gratuite et ne nécessite pas obligatoirement un avocat, mais elle obéit à des règles strictes.",
        "limites": "Les sites officiels vous indiquent comment saisir le tribunal et les délais à respecter. Ce qu'ils ne vous montrent pas, c'est que cette juridiction a ses propres codes, ses pratiques, et que la qualité de votre dossier détermine directement l'issue de la procédure. Le juge statue principalement sur pièces : vos certificats médicaux, les avis d'experts, les attestations. L'audience elle-même est souvent courte. C'est en amont, dans la constitution du dossier, que la procédure se gagne ou se perd.",
        "blocages": [
            "Le dossier est déposé sans pièces médicales suffisantes : le juge ne peut pas aller au-delà de ce que le dossier contient. Un recours sans preuves médicales solides est un recours perdu.",
            "Le recours préalable obligatoire n'a pas été effectué : la saisine du tribunal sans recours préalable (CRA pour la CPAM, RAPO pour la MDPH) est irrecevable.",
            "Les délais ne sont pas respectés : 2 mois après la décision de la CRA ou du RAPO pour saisir le tribunal. Ce délai est strict et non prorogeable.",
            "La demande est mal formulée : le tribunal statue dans les limites de la demande. Si vous demandez uniquement la reconnaissance de votre AT, vous ne pouvez pas obtenir la faute inexcusable dans la même procédure.",
            "L'expertise judiciaire est mal préparée : le juge ordonne souvent une expertise médicale. Si vous n'êtes pas accompagné par un médecin de recours lors de cette expertise, vous subissez les conclusions de l'expert sans pouvoir les contrebalancer."
        ],
        "erreurs": [
            "Saisir le tribunal sans avoir épuisé les voies de recours amiable : CRA obligatoire pour la CPAM, RAPO obligatoire pour la MDPH.",
            "Rédiger la requête sans préciser exactement ce que vous demandez : le tribunal statue dans les limites de votre demande.",
            "Se présenter à l'audience sans dossier organisé : classez vos pièces chronologiquement, numérotez-les, rédigez un bordereau.",
            "Refuser l'expertise judiciaire ordonnée par le juge : c'est un moyen de preuve essentiel qui joue souvent en votre faveur.",
            "Ne pas se faire accompagner par un médecin de recours lors de l'expertise judiciaire : l'expert est neutre, mais le médecin conseil de la CPAM sera présent."
        ],
        "strategie": "Le recours devant le pôle social se prépare en amont de la saisine. Notre approche consiste à structurer le dossier selon les attentes du tribunal : chronologie des faits, pièces médicales classées et numérotées, argumentation ciblée sur le motif de contestation, et anticipation de l'expertise judiciaire. Nous vous orientons vers les bons professionnels (médecin de recours, avocat spécialisé si nécessaire) et nous préparons les arguments techniques qui permettront au juge de trancher en votre faveur.",
        "orientation": [
            "Vérifiez que le recours préalable obligatoire a bien été effectué et que le délai de 2 mois n'est pas dépassé.",
            "Rédigez une requête claire précisant votre demande exacte (reconnaissance d'AT, réévaluation du taux, attribution de l'AAH, etc.).",
            "Constituez un dossier organisé : pièces numérotées, bordereau, chronologie des faits, certificats médicaux récents.",
            "Si une expertise judiciaire est ordonnée, faites-vous accompagner par un médecin de recours.",
            "Présentez-vous à l'audience avec vos pièces et une synthèse écrite de vos arguments."
        ],
        "reassurance": "Le tribunal judiciaire pôle social est une juridiction accessible, gratuite et qui rend des décisions motivées. De nombreuses contestations aboutissent favorablement lorsque le dossier est correctement constitué. Le juge est attentif aux réalités des victimes et dispose de moyens d'investigation (expertise judiciaire) que les commissions administratives n'ont pas.",
        "maillage": [
            {"slug": "taux-ipp-5-pourcent-contester", "text": "Contestation du taux d'IPP : préparer votre dossier"},
            {"slug": "refus-mdph-aah-que-faire", "text": "Refus MDPH pour l'AAH : contester efficacement"},
            {"slug": "delai-prescription-maladie-professionnelle", "text": "Délais de prescription : ne pas perdre vos droits"}
        ],
        "faq": [
            {"question": "Faut-il un avocat pour saisir le tribunal judiciaire pôle social ?", "answer": "Non, la représentation par avocat n'est pas obligatoire devant le pôle social. Vous pouvez vous défendre seul. Cependant, pour les dossiers complexes, l'assistance d'un avocat spécialisé en droit de la sécurité sociale est recommandée."},
            {"question": "Combien de temps dure une procédure devant le pôle social ?", "answer": "La procédure dure généralement entre 6 et 18 mois, selon la complexité du dossier et la nécessité d'une expertise judiciaire. La saisine est gratuite."}
        ]
    },
},
{
    "slug": "delai-prescription-maladie-professionnelle",
    "title": "Délai de prescription maladie professionnelle : les erreurs qui vous font perdre définitivement vos droits",
    "meta_description": "Les délais en maladie professionnelle sont stricts et souvent mal compris. Découvrez les pièges fréquents et la stratégie pour préserver vos droits.",
    "category": "accident_travail",
    "intention": "urgence",
    "priority": "p0",
    "cta_type": "dossier_express",
    "cta_label": "Vérifier mes délais",
    "content": {
        "contexte": "En matière de maladie professionnelle, plusieurs délais s'appliquent et leur non-respect peut entraîner la perte définitive de vos droits. Le délai de déclaration est de 2 ans à compter de la date à laquelle vous avez été informé du lien possible entre votre maladie et votre activité professionnelle (article L.461-1 CSS). Le délai de prise en charge, inscrit dans les tableaux de maladies professionnelles, fixe la durée maximale entre la fin de l'exposition au risque et l'apparition de la maladie. Enfin, le délai de recours contre les décisions de la CPAM est de 2 mois.",
        "limites": "Les textes officiels listent les différents délais sans expliquer comment ils s'articulent ni comment les calculer correctement. Ce qu'ils ne vous disent pas, c'est que le point de départ du délai de déclaration est une notion subjective : « la date à laquelle la victime est informée du lien possible ». Cette date peut être un certificat médical, un diagnostic, ou même une information reçue par un tiers. Les organismes de sécurité sociale retiennent souvent la date la plus ancienne pour réduire votre délai. Par ailleurs, le délai de prise en charge inscrit dans les tableaux est une condition de la présomption d'origine professionnelle — son dépassement ne signifie pas que la maladie n'est pas professionnelle, mais qu'il faudra passer par le CRRMP.",
        "blocages": [
            "La date de première constatation médicale est contestée : la CPAM peut considérer que votre maladie a été diagnostiquée plus tôt que ce que vous déclarez, réduisant ainsi votre délai de déclaration.",
            "Le délai de prise en charge du tableau est dépassé de quelques mois : la CPAM refuse automatiquement la prise en charge par le tableau, sans orienter vers le CRRMP.",
            "Le salarié n'a pas été informé du lien professionnel par son médecin : certains médecins traitants ne font pas le lien entre la pathologie et l'exposition professionnelle, retardant la déclaration.",
            "Les expositions chez d'anciens employeurs ne sont pas documentées : reconstituer un historique d'exposition sur 20 ou 30 ans de carrière est complexe mais nécessaire.",
            "Le délai de recours de 2 mois passe inaperçu : la notification de refus arrive par courrier simple, le salarié ne réagit pas dans les temps."
        ],
        "erreurs": [
            "Confondre le délai de déclaration (2 ans) et le délai de prise en charge (variable selon les tableaux) : ce sont deux notions distinctes qui s'appliquent indépendamment.",
            "Dater la déclaration à partir du diagnostic médical alors que le lien professionnel n'a été établi que plus tard : le délai court à partir de la connaissance du lien, pas du diagnostic.",
            "Ne pas faire de déclaration parce que le délai de prise en charge est dépassé : la voie du CRRMP reste ouverte.",
            "Oublier que le délai de recours de 2 mois est un délai de forclusion : passé ce délai, aucun rattrapage n'est possible.",
            "Ne pas conserver les courriers de la CPAM : la date de notification conditionne le point de départ du délai de recours."
        ],
        "strategie": "La gestion des délais en maladie professionnelle est un exercice technique qui nécessite une analyse précise de votre chronologie personnelle. Notre approche consiste à retracer l'historique de votre maladie (premiers symptômes, diagnostic, information du lien professionnel), à vérifier les délais applicables selon le tableau concerné, et à identifier la voie de reconnaissance la plus adaptée (tableau, CRRMP, ou les deux). Si un délai est proche d'expirer, nous priorisons les actions urgentes. Si un délai est dépassé, nous évaluons les alternatives juridiques possibles.",
        "orientation": [
            "Identifiez la date exacte à laquelle vous avez été informé du lien entre votre maladie et votre travail : certificat médical, diagnostic, information d'un médecin.",
            "Vérifiez le tableau de maladie professionnelle applicable : délai de prise en charge, durée d'exposition, liste des travaux.",
            "Si le délai de prise en charge est dépassé, demandez la saisine du CRRMP — ne renoncez pas à la déclaration.",
            "Déposez votre déclaration le plus rapidement possible — le délai de 2 ans court et ne peut pas être suspendu.",
            "Conservez précieusement tous les courriers CPAM et notez les dates de réception."
        ],
        "reassurance": "Les questions de délai en maladie professionnelle sont parmi les plus techniques du droit de la sécurité sociale. De nombreuses victimes perdent leurs droits non par manque de fondement, mais par méconnaissance des délais applicables. Une analyse rigoureuse de votre chronologie permet souvent d'identifier des solutions, même dans des situations qui semblent prescrites.",
        "maillage": [
            {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus de maladie professionnelle : les recours concrets"},
            {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Saisir le tribunal : procédure et enjeux"},
            {"slug": "accident-travail-non-declare-employeur", "text": "Accident du travail non déclaré : agir rapidement"}
        ],
        "faq": [
            {"question": "Quel est le délai pour déclarer une maladie professionnelle ?", "answer": "Vous disposez de 2 ans à compter de la date à laquelle vous avez été informé du lien possible entre votre maladie et votre activité professionnelle. Ce délai court à partir de la connaissance du lien, pas nécessairement du diagnostic."},
            {"question": "Que faire si le délai de prise en charge du tableau est dépassé ?", "answer": "Vous pouvez demander la reconnaissance via le CRRMP (Comité Régional de Reconnaissance des Maladies Professionnelles), qui peut reconnaître la maladie si elle est directement causée par le travail."}
        ]
    },
},
# ═══════════════════════════════════════════════════════════════
# BLOC C — 5 FAQ TRANSFORMÉES EN PAGES SEO
# ═══════════════════════════════════════════════════════════════
{
    "slug": "comment-preparer-expertise-medicale",
    "title": "Comment se préparer à une expertise médicale : les clés d'un dossier solide et d'un examen maîtrisé",
    "meta_description": "Expertise médicale prochaine ? Découvrez comment préparer votre dossier, vous comporter lors de l'examen et éviter les erreurs qui affaiblissent votre évaluation.",
    "category": "expertise",
    "intention": "urgence",
    "priority": "p0",
    "cta_type": "accompagnement",
    "cta_label": "Préparer mon expertise avec un spécialiste",
    "content": {
        "contexte": "L'expertise médicale est un moment clé dans tout dossier d'indemnisation : accident du travail, maladie professionnelle, accident de la route, responsabilité médicale. L'expert évalue vos séquelles, fixe les postes de préjudice, et rédige un rapport qui influence directement le montant de votre indemnisation. Cette expertise peut être amiable (organisée par une assurance), judiciaire (ordonnée par un tribunal), ou administrative (médecin conseil CPAM). Dans chaque cas, votre préparation détermine le résultat.",
        "limites": "Les guides officiels vous conseillent d'apporter votre dossier médical et d'être ponctuel. Ce conseil est insuffisant. L'expertise est un exercice technique codifié, avec des enjeux financiers considérables, où les parties adverses (assureurs, CPAM) sont représentées par des professionnels. Arriver avec un dossier non classé, sans synthèse, sans médecin de recours, c'est accepter de jouer un match décisif sans préparation face à des adversaires rodés.",
        "blocages": [
            "Le dossier médical est incomplet ou non classé : l'expert ne passera pas 2 heures à chercher les informations dans un sac de documents. Ce qu'il ne trouve pas, il ne l'évalue pas.",
            "Les séquelles invisibles ne sont pas documentées : douleurs chroniques, fatigue, troubles du sommeil, anxiété — sans certificats de spécialistes, ces séquelles sont systématiquement sous-évaluées.",
            "Le patient minimise ses symptômes : par habitude, par pudeur, ou pour ne pas « exagérer ». L'expertise n'est pas le moment d'être stoïque — c'est le moment de décrire précisément vos limitations.",
            "Le médecin conseil de l'assurance oriente l'examen : il pose des questions dirigées, suggère des interprétations. Sans médecin de recours, ses interventions passent inaperçues.",
            "Les doléances ne sont pas préparées par écrit : l'émotion du jour J fait oublier des symptômes importants. Une liste écrite et structurée est indispensable."
        ],
        "erreurs": [
            "Arriver sans dossier organisé : classez vos pièces par date, rédigez une synthèse chronologique, numérotez les documents.",
            "Ne pas se faire accompagner par un médecin de recours : c'est l'erreur la plus coûteuse. Le médecin de recours veille à ce que toutes vos séquelles soient évaluées et contrebalance le médecin conseil adverse.",
            "Exagérer ou simuler des symptômes : les experts sont formés à détecter l'exagération. Restez factuel et précis.",
            "Ne pas mentionner les retentissements psychologiques : syndrome anxio-dépressif, PTSD, troubles du sommeil — ce sont des postes de préjudice à part entière.",
            "Accepter les conclusions sans formuler de dire : après réception du rapport, vous avez un délai pour faire des observations écrites. Utilisez-le."
        ],
        "strategie": "La préparation d'une expertise médicale est un travail structuré qui commence plusieurs semaines avant l'examen. Notre approche consiste à analyser votre dossier médical, identifier les séquelles à faire évaluer, rédiger vos doléances structurées, et vous orienter vers un médecin de recours spécialisé dans votre type de séquelles. Le jour de l'expertise, votre médecin de recours sera présent pour rééquilibrer l'examen, poser les bonnes questions, et veiller à ce que le rapport reflète fidèlement votre état.",
        "orientation": [
            "Classez votre dossier médical par date : tous les certificats, bilans, comptes-rendus, ordonnances.",
            "Rédigez une synthèse chronologique de votre parcours médical depuis l'accident/la maladie.",
            "Préparez une liste écrite de vos doléances : chaque douleur, chaque limitation, chaque difficulté quotidienne.",
            "Prenez rendez-vous avec un médecin de recours au moins 2 semaines avant l'expertise pour préparer ensemble.",
            "Après l'expertise, demandez communication du rapport et formulez des dires si les conclusions ne reflètent pas votre état."
        ],
        "reassurance": "L'expertise médicale est un moment stressant mais qui peut jouer en votre faveur si vous êtes bien préparé. Un dossier complet, des doléances structurées et l'accompagnement d'un médecin de recours changent significativement le résultat. Nous accompagnons régulièrement des personnes dans cette préparation, et la différence entre un patient préparé et un patient non préparé est considérable.",
        "maillage": [
            {"slug": "expertise-medicale-defavorable-recours", "text": "Expertise défavorable : les recours pour contester le rapport"},
            {"slug": "taux-ipp-5-pourcent-contester", "text": "Taux d'IPP sous-évalué : comment contester ?"},
            {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Saisir le tribunal : quand l'expertise ne suffit pas"}
        ],
        "faq": [
            {"question": "Combien coûte un médecin de recours ?", "answer": "Les honoraires d'un médecin de recours varient entre 300 et 1 500 euros selon la complexité du dossier et la durée de l'expertise. C'est un investissement qui se traduit directement par une meilleure évaluation de vos préjudices."},
            {"question": "Peut-on refuser une expertise médicale ?", "answer": "En matière judiciaire, le refus de se soumettre à l'expertise peut être interprété défavorablement par le juge. En matière amiable (assurance), le refus peut bloquer le processus d'indemnisation. Il est préférable de s'y soumettre en étant bien préparé."}
        ]
    },
},
{
    "slug": "comment-demander-rqth-strategic",
    "title": "RQTH : au-delà de la demande administrative, la stratégie d'accès aux droits",
    "meta_description": "La RQTH n'est pas qu'une formalité. Découvrez comment cette reconnaissance ouvre concrètement des droits et comment structurer votre demande pour maximiser son impact.",
    "category": "mdph",
    "intention": "refus_droits",
    "priority": "p1",
    "cta_type": "dossier_express",
    "cta_label": "Analyser mon dossier RQTH",
    "content": {
        "contexte": "La Reconnaissance de la Qualité de Travailleur Handicapé (RQTH) est attribuée par la CDAPH de la MDPH. Elle concerne toute personne dont les possibilités d'obtenir ou de conserver un emploi sont réduites par suite de l'altération d'une ou plusieurs fonctions physique, sensorielle, mentale ou psychique (article L.5213-1 du Code du travail). La RQTH ouvre des droits concrets : obligation d'emploi pour les entreprises, aides à l'adaptation du poste, accès à des dispositifs spécifiques de maintien dans l'emploi, et possibilité de départ anticipé à la retraite sous conditions.",
        "limites": "Les sites institutionnels vous expliquent comment remplir le formulaire Cerfa et déposer votre dossier. Ce qu'ils ne vous disent pas, c'est que la RQTH est souvent traitée comme une case à cocher, alors qu'elle devrait s'inscrire dans une stratégie globale d'accès aux droits. Beaucoup de personnes obtiennent la RQTH sans en exploiter les bénéfices, ou la demandent isolément alors qu'elle pourrait être couplée avec d'autres demandes (AAH, carte mobilité inclusion, PCH). Par ailleurs, la RQTH est parfois refusée alors que le handicap est réel, simplement parce que le dossier ne met pas en évidence le lien entre la pathologie et les limitations professionnelles.",
        "blocages": [
            "Le certificat médical ne décrit pas les limitations professionnelles : il mentionne un diagnostic mais pas en quoi la pathologie impacte la capacité à travailler.",
            "La demande est faite isolément : la RQTH devrait s'intégrer dans une stratégie globale incluant, le cas échéant, l'AAH, la carte mobilité inclusion, ou la prestation de compensation du handicap.",
            "Le projet de vie n'est pas rédigé ou ne mentionne pas l'impact professionnel : la CDAPH évalue la restriction d'accès à l'emploi — si rien n'est écrit sur ce sujet, l'évaluation est lacunaire.",
            "La RQTH est obtenue mais non utilisée : l'employeur n'est pas informé (ce n'est pas obligatoire), les aides à l'adaptation ne sont pas sollicitées, les dispositifs de maintien dans l'emploi sont ignorés.",
            "Le renouvellement est négligé : la RQTH est attribuée pour une durée limitée. Si le renouvellement n'est pas anticipé, les droits sont interrompus."
        ],
        "erreurs": [
            "Demander la RQTH sans préparer le volet professionnel du dossier : la MDPH doit comprendre en quoi votre handicap limite votre accès à l'emploi.",
            "Penser que la RQTH suffit pour être protégé : elle ouvre des droits mais ne protège pas automatiquement contre un licenciement.",
            "Ne pas informer Cap Emploi ou l'AGEFIPH de votre RQTH : ces organismes proposent des aides et des accompagnements spécifiques aux travailleurs handicapés.",
            "Ne pas coupler la RQTH avec d'autres demandes MDPH quand c'est pertinent : AAH, carte mobilité, PCH.",
            "Attendre d'être en difficulté professionnelle pour demander la RQTH : anticiper permet de bénéficier des dispositifs de maintien dans l'emploi."
        ],
        "strategie": "La RQTH doit être pensée comme un levier stratégique dans un parcours de droits. Notre approche consiste à évaluer si la RQTH seule suffit ou si elle doit être couplée avec d'autres demandes, à structurer le dossier pour mettre en évidence les limitations professionnelles, et à planifier l'utilisation concrète de la reconnaissance une fois obtenue. Nous vérifions également l'accès aux dispositifs de maintien dans l'emploi (aménagement de poste, temps partiel thérapeutique, reclassement) et les aides financières mobilisables.",
        "orientation": [
            "Faites rédiger un certificat médical détaillant les limitations fonctionnelles et leur impact sur votre activité professionnelle.",
            "Rédigez un projet de vie centré sur les difficultés professionnelles liées à votre handicap.",
            "Évaluez si la RQTH doit être couplée avec d'autres demandes MDPH (AAH, carte mobilité, PCH).",
            "Contactez Cap Emploi ou l'AGEFIPH après obtention pour mobiliser les aides à l'adaptation de poste.",
            "Anticipez le renouvellement 6 mois avant l'expiration de la RQTH."
        ],
        "reassurance": "La RQTH est un droit accessible à toute personne dont le handicap impacte l'emploi. Correctement préparée et stratégiquement utilisée, elle ouvre des droits concrets qui facilitent le maintien dans l'emploi et l'accès aux dispositifs d'accompagnement. C'est un outil puissant quand il est mobilisé intelligemment.",
        "maillage": [
            {"slug": "refus-mdph-aah-que-faire", "text": "Refus d'AAH : stratégie de recours MDPH"},
            {"slug": "inaptitude-travail-droits-recours", "text": "Inaptitude au travail : vos droits et les recours"},
            {"slug": "comment-faire-reconnaitre-maladie-professionnelle", "text": "Reconnaissance de maladie professionnelle : la stratégie complète"}
        ],
        "faq": [
            {"question": "La RQTH est-elle obligatoirement communiquée à l'employeur ?", "answer": "Non, la RQTH relève de la vie privée. Vous n'êtes pas obligé d'informer votre employeur. Cependant, la communiquer permet à l'employeur de remplir son obligation d'emploi de travailleurs handicapés et peut déclencher des aides à l'adaptation de votre poste."},
            {"question": "La RQTH protège-t-elle contre le licenciement ?", "answer": "Non, la RQTH ne confère pas de protection spécifique contre le licenciement. En revanche, le statut de travailleur handicapé peut être pris en compte dans certaines procédures (doublement du préavis dans la limite de 3 mois)."}
        ]
    },
},
{
    "slug": "comment-faire-reconnaitre-maladie-professionnelle",
    "title": "Comment faire reconnaître une maladie professionnelle : la stratégie au-delà de la simple déclaration",
    "meta_description": "La reconnaissance d'une maladie professionnelle ne se résume pas à remplir un formulaire. Découvrez la stratégie documentaire pour maximiser vos chances.",
    "category": "accident_travail",
    "intention": "refus_droits",
    "priority": "p0",
    "cta_type": "dossier_express",
    "cta_label": "Analyser mon dossier de maladie professionnelle",
    "content": {
        "contexte": "La déclaration de maladie professionnelle auprès de la CPAM est une procédure qui peut suivre deux voies : la voie des tableaux (présomption d'origine professionnelle si toutes les conditions sont remplies) ou la voie du CRRMP (pour les pathologies hors tableaux ou les conditions non entièrement remplies). La CPAM dispose de 120 jours (plus un délai complémentaire de 120 jours en cas d'enquête) pour statuer. Le certificat médical initial, les fiches d'exposition, et la description des postes occupés constituent les pièces maîtresses du dossier.",
        "limites": "Les sites officiels vous indiquent la liste des tableaux de maladies professionnelles et la procédure de déclaration. Ce qu'ils ne montrent pas, c'est la complexité réelle de la preuve. Les tableaux de maladies professionnelles sont rédigés avec une précision technique qui laisse place à l'interprétation. La CPAM peut contester que vos travaux entrent dans la « liste limitative des travaux » du tableau, que votre durée d'exposition est suffisante, ou que le délai de prise en charge est respecté. Par ailleurs, le médecin conseil de la CPAM évalue le lien de causalité avec ses propres critères, qui peuvent différer de ceux de votre médecin traitant.",
        "blocages": [
            "Le certificat médical initial ne fait pas le lien explicite avec l'exposition professionnelle : le médecin note un diagnostic mais n'établit pas clairement le lien avec les conditions de travail.",
            "L'historique des postes est incomplet : pour prouver la durée d'exposition, il faut reconstituer l'ensemble des postes exposant au risque sur toute la carrière, y compris chez d'anciens employeurs.",
            "L'employeur conteste l'exposition : lors de l'enquête de la CPAM, l'employeur peut minimiser les conditions d'exposition. Vos éléments de preuve doivent contrebalancer cette version.",
            "La CPAM ne vous informe pas de la possibilité de saisir le CRRMP : si les conditions du tableau ne sont pas toutes remplies, cette voie est rarement proposée spontanément.",
            "Le délai d'instruction est dépassé sans réponse : passé le délai de 120 jours (+ 120 jours si enquête complémentaire), l'absence de réponse vaut reconnaissance. Mais les victimes ne le savent pas toujours."
        ],
        "erreurs": [
            "Déposer la déclaration sans avoir préparé les pièces justificatives d'exposition : attestations d'anciens collègues, fiches de données de sécurité, fiches de poste.",
            "Se contenter du tableau sans vérifier les conditions une par une : chaque condition (délai de prise en charge, durée d'exposition, liste des travaux) doit être documentée.",
            "Ne pas anticiper l'enquête contradictoire de la CPAM : préparez votre version des faits avant d'être contacté par l'enquêteur.",
            "Abandonner la procédure si la voie du tableau échoue : le CRRMP offre une seconde chance de reconnaissance.",
            "Ne pas conserver le récépissé de déclaration : c'est la preuve de la date de dépôt, essentielle pour le calcul des délais."
        ],
        "strategie": "La reconnaissance d'une maladie professionnelle se construit en amont de la déclaration. Notre approche consiste à vérifier les conditions du tableau applicable, à reconstituer l'historique d'exposition avec les preuves nécessaires, et à anticiper les objections de la CPAM. Si les conditions du tableau ne sont pas entièrement remplies, nous évaluons l'opportunité d'une double stratégie : déclaration par le tableau ET préparation d'un dossier CRRMP en parallèle. L'objectif est de ne laisser aucune chance au hasard dans un processus où la charge de la preuve pèse sur la victime.",
        "orientation": [
            "Identifiez le tableau de maladie professionnelle correspondant à votre pathologie et vérifiez chaque condition une par une.",
            "Reconstituez votre historique d'exposition : tous les postes, employeurs, durées, et tâches exposant au risque.",
            "Rassemblez les preuves d'exposition : fiches de poste, attestations de collègues, fiches de données de sécurité, photos des conditions de travail.",
            "Faites rédiger le certificat médical initial par un médecin qui établit explicitement le lien entre la pathologie et l'exposition professionnelle.",
            "Déposez votre déclaration et conservez le récépissé — le délai d'instruction de 120 jours commence à courir."
        ],
        "reassurance": "La reconnaissance de maladie professionnelle est une procédure technique mais accessible. La présomption d'origine professionnelle joue en votre faveur lorsque les conditions du tableau sont remplies. Et même en dehors des tableaux, le CRRMP offre une voie de reconnaissance pour les pathologies directement liées au travail. Un dossier bien préparé est le meilleur atout.",
        "maillage": [
            {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus de maladie professionnelle : les recours après un refus CPAM"},
            {"slug": "delai-prescription-maladie-professionnelle", "text": "Délais de prescription : ne perdez pas vos droits"},
            {"slug": "accident-travail-non-declare-employeur", "text": "AT non déclaré par l'employeur : protéger vos droits"}
        ],
        "faq": [
            {"question": "Combien de temps la CPAM a-t-elle pour répondre ?", "answer": "La CPAM dispose de 120 jours pour statuer. Elle peut prolonger ce délai de 120 jours supplémentaires en cas de nécessité d'examen complémentaire ou d'enquête. L'absence de réponse dans ces délais vaut reconnaissance de la maladie professionnelle."},
            {"question": "Peut-on déclarer une maladie professionnelle après avoir quitté l'entreprise ?", "answer": "Oui, la déclaration peut être faite dans un délai de 2 ans après la cessation d'exposition ou après la date à laquelle vous avez été informé du lien entre votre maladie et votre activité professionnelle."}
        ]
    },
},
{
    "slug": "maladie-professionnelle-definition-droits",
    "title": "Maladie professionnelle : ce que la définition officielle ne vous dit pas sur vos droits réels",
    "meta_description": "Qu'est-ce qu'une maladie professionnelle au-delà de la définition administrative ? Découvrez vos droits concrets et les pièges à éviter dans la procédure.",
    "category": "accident_travail",
    "intention": "refus_droits",
    "priority": "p1",
    "cta_type": "dossier_express",
    "cta_label": "Évaluer mes droits",
    "content": {
        "contexte": "Une maladie professionnelle est une pathologie contractée dans le cadre de l'activité professionnelle, reconnue par la Sécurité sociale selon des critères précis. Il existe deux voies de reconnaissance : les tableaux de maladies professionnelles (qui listent les pathologies, les conditions d'exposition et les délais) et la voie complémentaire via le CRRMP pour les maladies hors tableaux. La reconnaissance ouvre des droits spécifiques : prise en charge à 100% des soins, indemnités journalières majorées, rente en cas de séquelles, et possibilité de faire reconnaître la faute inexcusable de l'employeur.",
        "limites": "La définition officielle est claire mais trompeuse dans sa simplicité. En pratique, faire reconnaître une maladie professionnelle implique de naviguer dans un système complexe de tableaux, de conditions, de délais et de procédures. Les textes officiels vous donnent la mécanique mais pas la stratégie. Ils ne vous disent pas que certaines maladies professionnelles sont systématiquement sous-déclarées (troubles musculo-squelettiques, burn-out, pathologies liées aux agents chimiques), que les employeurs ont un intérêt financier à contester la reconnaissance, et que la CPAM applique les critères avec une rigueur qui peut jouer en votre défaveur.",
        "blocages": [
            "La sous-déclaration systématique : de nombreuses maladies professionnelles ne sont jamais déclarées parce que le lien avec le travail n'est pas identifié par le médecin traitant.",
            "La complexité des tableaux : chaque tableau comporte des conditions cumulatives (pathologie, délai de prise en charge, durée d'exposition, liste des travaux) qui doivent toutes être remplies pour bénéficier de la présomption.",
            "Le burn-out et les pathologies psychiques ne figurent pas dans les tableaux : la reconnaissance passe obligatoirement par le CRRMP et nécessite de prouver un lien direct et essentiel avec le travail + un taux d'IPP d'au moins 25%.",
            "L'employeur conteste systématiquement : lors de l'enquête CPAM, l'employeur produit des éléments pour minimiser l'exposition ou contester le lien causal.",
            "Le passage de la maladie ordinaire à la maladie professionnelle n'est pas anticipé : des salariés sont en arrêt maladie depuis des mois pour une pathologie professionnelle, perdant ainsi les avantages de la prise en charge AT/MP."
        ],
        "erreurs": [
            "Rester en arrêt maladie ordinaire alors que la pathologie est d'origine professionnelle : les conséquences financières sont majeures (pas de délai de carence, indemnités plus élevées en AT/MP).",
            "Ne pas demander à son médecin si la pathologie peut avoir un lien avec le travail : c'est la première question à poser.",
            "Penser que le burn-out ne peut pas être reconnu comme maladie professionnelle : c'est possible via le CRRMP, à condition que le dossier soit solide.",
            "Attendre trop longtemps pour déclarer : le délai de 2 ans court à partir de la connaissance du lien professionnel.",
            "Confondre maladie professionnelle et invalidité : ce sont deux régimes distincts avec des droits différents."
        ],
        "strategie": "La première étape est de déterminer si votre pathologie peut être qualifiée de maladie professionnelle et quelle voie de reconnaissance est la plus adaptée. Notre approche consiste à analyser votre situation médicale et professionnelle pour identifier le tableau applicable (ou l'opportunité d'un CRRMP), évaluer les chances de reconnaissance, et constituer le dossier en conséquence. Nous anticipons les objections de la CPAM et préparons les preuves d'exposition nécessaires. L'objectif est de sécuriser la reconnaissance dès la première instruction, sans avoir à passer par un recours contentieux.",
        "orientation": [
            "Demandez à votre médecin traitant ou spécialiste si votre pathologie peut avoir un lien avec votre activité professionnelle.",
            "Identifiez le tableau de maladie professionnelle potentiellement applicable à votre pathologie.",
            "Si votre pathologie ne figure pas dans les tableaux (burn-out, pathologies psychiques), évaluez la possibilité d'une reconnaissance via le CRRMP.",
            "Constituez votre dossier de preuves d'exposition avant de déposer la déclaration.",
            "Si vous êtes actuellement en arrêt maladie pour une pathologie professionnelle, envisagez de faire requalifier votre arrêt en AT/MP."
        ],
        "reassurance": "La maladie professionnelle est un droit fondamental des salariés exposés à des risques dans leur travail. Sa reconnaissance ouvre des droits significatifs qui dépassent largement ceux de la maladie ordinaire. Même les pathologies complexes (burn-out, troubles psychiques) peuvent être reconnues avec un dossier solide. La première étape est d'identifier le lien avec votre travail — nous pouvons vous y aider.",
        "maillage": [
            {"slug": "comment-faire-reconnaitre-maladie-professionnelle", "text": "Faire reconnaître une maladie professionnelle : la stratégie complète"},
            {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus CPAM : les recours après un refus de reconnaissance"},
            {"slug": "delai-prescription-maladie-professionnelle", "text": "Délais de prescription : les erreurs qui vous font perdre vos droits"}
        ],
        "faq": [
            {"question": "Le burn-out peut-il être reconnu comme maladie professionnelle ?", "answer": "Oui, mais il ne figure pas dans les tableaux de maladies professionnelles. La reconnaissance passe par le CRRMP qui doit constater que la pathologie est essentiellement et directement causée par le travail, avec un taux d'IPP prévisible d'au moins 25%."},
            {"question": "Quelle est la différence entre maladie professionnelle et invalidité ?", "answer": "La maladie professionnelle est reconnue par la CPAM comme étant causée par le travail, avec une prise en charge à 100% et des indemnités spécifiques. L'invalidité est une pension versée quand la capacité de travail est réduite d'au moins 2/3, quelle que soit l'origine de la maladie."}
        ]
    },
},
{
    "slug": "ptia-definition-droits-strategie",
    "title": "PTIA (Perte Totale et Irréversible d'Autonomie) : comprendre vos droits et la stratégie de reconnaissance",
    "meta_description": "La PTIA est souvent mal comprise et mal évaluée. Découvrez ce que recouvre réellement cette notion, vos droits concrets et les blocages fréquents.",
    "category": "indemnisation",
    "intention": "perte_financiere",
    "priority": "p1",
    "cta_type": "accompagnement",
    "cta_label": "Évaluer ma situation PTIA",
    "content": {
        "contexte": "La Perte Totale et Irréversible d'Autonomie (PTIA) est une notion utilisée principalement dans le domaine de l'assurance emprunteur et de la prévoyance. Elle désigne l'état d'une personne qui, par suite de maladie ou d'accident, se trouve dans l'impossibilité absolue et définitive d'exercer toute activité rémunératrice et qui nécessite l'assistance d'une tierce personne pour effectuer les actes ordinaires de la vie courante. La reconnaissance de la PTIA déclenche le remboursement du capital restant dû d'un prêt immobilier ou le versement d'un capital par un contrat de prévoyance.",
        "limites": "Les contrats d'assurance définissent la PTIA mais chaque assureur applique ses propres critères d'évaluation. Les textes officiels sont peu précis sur les modalités de reconnaissance. Ce que les conditions générales de votre contrat ne vous disent pas clairement, c'est que la PTIA est une notion extrêmement restrictive : l'impossibilité doit être « absolue et définitive » d'exercer « toute » activité rémunératrice. Les assureurs interprètent cette définition de manière très stricte, excluant des situations où la personne ne peut plus exercer son métier mais pourrait théoriquement effectuer une activité adaptée, même si cette activité est fictive.",
        "blocages": [
            "L'assureur conteste le caractère « total » de la perte d'autonomie : il argue que vous pouvez encore exercer une activité rémunératrice, même théorique et inadaptée à votre situation réelle.",
            "Le médecin conseil de l'assureur minimise les séquelles : son rapport conclut à une incapacité partielle plutôt que totale.",
            "Les actes de la vie courante sont interprétés restrictivement : l'assureur considère que vous pouvez accomplir certains actes seul, même si c'est avec une difficulté considérable.",
            "Le caractère « irréversible » est contesté : l'assureur demande des examens complémentaires pour évaluer les possibilités d'amélioration, retardant la décision.",
            "Les exclusions contractuelles sont invoquées : certains contrats excluent la PTIA résultant de pathologies préexistantes, d'activités à risque, ou de conditions spécifiques."
        ],
        "erreurs": [
            "Ne pas relire les conditions générales de votre contrat : les définitions, exclusions et conditions de mise en jeu varient d'un assureur à l'autre.",
            "Accepter le refus de l'assureur sans contester : les refus initiaux sont fréquents et souvent réversibles avec un dossier médical renforcé.",
            "Ne pas faire évaluer votre situation par un médecin indépendant : le médecin conseil de l'assureur défend les intérêts de l'assureur, pas les vôtres.",
            "Déclarer le sinistre tardivement : la plupart des contrats imposent un délai de déclaration. Un retard peut être invoqué pour refuser la prise en charge.",
            "Confondre PTIA et invalidité de catégorie 3 : ce sont des notions proches mais distinctes. L'invalidité est évaluée par la CPAM, la PTIA par l'assureur."
        ],
        "strategie": "La reconnaissance de la PTIA est un combat contre l'interprétation restrictive de l'assureur. Notre approche consiste à analyser votre contrat (définition exacte de la PTIA, exclusions, délais), à évaluer si votre situation médicale correspond aux critères contractuels, et à constituer un dossier médical qui ne laisse aucune place à la contestation. Nous identifions les certificats médicaux nécessaires, les bilans fonctionnels à réaliser, et nous vous orientons vers un médecin de recours capable de rédiger un rapport qui répond point par point aux critères de votre contrat.",
        "orientation": [
            "Relisez les conditions générales de votre contrat d'assurance : définition exacte de la PTIA, exclusions, délai de déclaration.",
            "Déclarez le sinistre à votre assureur dans les délais contractuels, par courrier recommandé.",
            "Rassemblez les certificats médicaux de vos spécialistes décrivant le caractère total et irréversible de votre perte d'autonomie.",
            "Si l'assureur refuse, demandez communication du rapport de son médecin conseil et faites-le analyser par un médecin indépendant.",
            "En cas de persistance du refus, saisissez le médiateur de l'assurance, puis le tribunal compétent si nécessaire."
        ],
        "reassurance": "La PTIA est une notion exigeante mais votre contrat d'assurance vous confère des droits. Les refus initiaux des assureurs sont fréquents et ne doivent pas vous décourager. Un dossier médical solide, une lecture attentive des conditions contractuelles, et un accompagnement adapté permettent souvent de faire reconnaître la PTIA et de déclencher les garanties prévues.",
        "maillage": [
            {"slug": "taux-ipp-5-pourcent-contester", "text": "Taux d'IPP et indemnisation : comprendre les évaluations"},
            {"slug": "expertise-medicale-defavorable-recours", "text": "Expertise médicale défavorable : les recours"},
            {"slug": "inaptitude-travail-droits-recours", "text": "Inaptitude au travail : droits et recours concrets"}
        ],
        "faq": [
            {"question": "Quelle différence entre PTIA et invalidité catégorie 3 ?", "answer": "L'invalidité de catégorie 3 est attribuée par la CPAM quand la personne est incapable d'exercer une activité professionnelle et nécessite l'aide d'un tiers. La PTIA est une notion contractuelle d'assurance, dont la définition varie selon les contrats. Les deux notions sont proches mais indépendantes."},
            {"question": "L'assureur peut-il refuser la PTIA malgré une invalidité catégorie 3 ?", "answer": "Oui, car ce sont deux évaluations distinctes avec des critères différents. Cependant, la reconnaissance d'une invalidité catégorie 3 constitue un argument fort pour la reconnaissance de la PTIA."}
        ]
    },
},
]

async def seed():
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.environ.get("DB_NAME", "test_database")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    created = 0
    updated = 0
    for page_data in PAGES:
        slug = page_data["slug"]
        existing = await db.seo_pages.find_one({"slug": slug})
        doc = {
            **page_data,
            "active": True,
            "views": existing.get("views", 0) if existing else 0,
            "cta_clicks": existing.get("cta_clicks", 0) if existing else 0,
            "conversions": existing.get("conversions", 0) if existing else 0,
            "revenue": existing.get("revenue", 0) if existing else 0,
        }
        if existing:
            doc["id"] = existing.get("id", str(uuid.uuid4()))
            doc["created_at"] = existing.get("created_at", datetime.now(timezone.utc).isoformat())
            await db.seo_pages.replace_one({"slug": slug}, doc)
            updated += 1
            print(f"  Updated: /guide/{slug}")
        else:
            doc["id"] = str(uuid.uuid4())
            doc["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.seo_pages.insert_one(doc)
            created += 1
            print(f"  Created: /guide/{slug}")

    print(f"\nDone. {created} created, {updated} updated. Total: {len(PAGES)} pages.")

if __name__ == "__main__":
    asyncio.run(seed())
