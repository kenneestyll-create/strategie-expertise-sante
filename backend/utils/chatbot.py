from typing import Optional

from emergentintegrations.llm.chat import LlmChat, UserMessage

from config import EMERGENT_LLM_KEY, logger


# ── FAQ limitee aux questions PUREMENT generales (tarifs, contact, RDV) ──
FAQ_DATABASE = {
    "tarifs": {
        "keywords": ["tarif", "prix", "coût", "combien ça coûte", "prestation"],
        "must_not_contain": ["ipp", "taux", "indemnisation", "maladie", "accident", "expertise", "calcul", "rente", "toucher", "recevoir"],
        "response": """**Nos tarifs**

- **Analyse de dossier** : a partir de 150 euros
- **Preparation a expertise medicale** : a partir de 250 euros
- **Accompagnement MDPH** : a partir de 200 euros
- **Protection juridique** : a partir de 200 euros
- **Accompagnement complet** : a partir de 500 euros (sur devis)
- **Seminaires / Formations** : sur devis
- **Conseil entreprises** : sur devis

**Le premier echange telephonique est gratuit et sans engagement.**

Pour en savoir plus : [Voir tous nos tarifs](/tarifs)"""
    },
    "contact": {
        "keywords": ["contacter", "rendez-vous", "joindre", "téléphone", "email", "appeler", "écrire"],
        "must_not_contain": ["expertise", "mdph", "maladie", "accident", "ipp", "droit"],
        "response": """**Comment nous contacter ?**

Vous pouvez me contacter pour un premier echange gratuit et sans engagement :

- **Par le formulaire de contact** sur notre site
- **Par email** : contact@accompagn-sante.fr
- **Par telephone** : 06 00 00 00 00

Je vous repondrai dans les 24 a 48 heures.

Pour en savoir plus : [Acceder au formulaire de contact](/contact)"""
    },
}


def find_faq_response(message: str) -> Optional[str]:
    """Match FAQ uniquement pour les questions generales simples.
    Toute question medicale/juridique specifique va directement a Claude."""
    msg = message.lower()

    # Si la question contient des termes medicaux specifiques, JAMAIS la FAQ
    MEDICAL_SIGNALS = [
        "tableau", "coccyg", "lombalgie", "hernie", "canal carpien", "tendinite",
        "sciatique", "amiante", "silicose", "tms", "surdite", "syndrome",
        "pathologie", "diagnostic", "symptome", "consolidation", "rechute",
        "maladie professionnelle", "faute inexcusable", "pgpf", "ip ",
        "incidence professionnelle", "perte de gains", "capitalisation",
        "burn out", "burnout", "depression", "epuisement",
        "inaptitude", "reclassement", "licenciement", "rente", "bareme",
        "hors tableau", "crrmp", "alinea", "est-elle", "est-il", "peut-on",
        "comment contester", "comment calculer", "quel taux", "combien toucher",
        "combien recevoir", "quelle indemnisation", "quels droits",
    ]
    for signal in MEDICAL_SIGNALS:
        if signal in msg:
            return None

    # Questions avec "?" contenant plus de 8 mots → probablement specifique → Claude
    word_count = len(msg.split())
    if "?" in msg and word_count > 8:
        return None

    # FAQ match stricte
    for topic, data in FAQ_DATABASE.items():
        has_keyword = any(kw in msg for kw in data["keywords"])
        has_exclusion = any(exc in msg for exc in data.get("must_not_contain", []))
        if has_keyword and not has_exclusion:
            return data["response"]

    return None


# ── Base de connaissances pour le prompt Claude ──
TABLEAUX_MP = """TABLEAUX DES MALADIES PROFESSIONNELLES (extraits principaux) :
- Tableau 4 : Hemopathies provoquees par le benzene (delai 30 ans) — chimie, petrochimie, imprimerie
- Tableau 6 : Affections par rayonnements ionisants (delai 50 ans) — nucleaire, radiologie
- Tableau 16 bis : Cancers par goudrons de houille (delai 20 ans) — travaux routiers
- Tableau 25 : Silicose (delai 35 ans) — mines, carrieres, fonderies, BTP
- Tableau 30 : Affections par amiante (delai 40 ans) — flocage, calorifugeage, isolation
- Tableau 30 bis : Cancer broncho-pulmonaire amiante (delai 40 ans)
- Tableau 36 : Affections par huiles/graisses (delai 7j a 6 mois) — usinage, mecanique
- Tableau 42 : Surdite professionnelle (delai 1 an) — bruits lesionnels
- Tableau 47 : Affections par bois (variable) — menuiserie, scierie
- Tableau 57 : TMS - Affections periarticulaires (variable) — mouvements repetitifs
  - 57A : Epaule (coiffe des rotateurs) — 6 mois a 1 an
  - 57B : Coude (epicondylite, epitrochleite) — 6 mois a 1 an
  - 57C : Poignet/Main (canal carpien) — 6 mois a 1 an
  - 57D : Genou (hygroma, tendinite) — 6 mois a 1 an
  - 57E : Cheville/Pied (tendinite d'Achille) — 6 mois a 1 an
- Tableau 66 : Rhinites et asthmes professionnels (7j a 1 an) — farine, bois, latex
- Tableau 69 : Vibrations (delai 5 ans) — marteaux-piqueurs, tronconneuses
- Tableau 79 : Lesions du menisque (delai 2 ans) — position agenouillee
- Tableau 97 : Lombalgie/Sciatique (delai 6 mois) — manutention charges lourdes
- Tableau 98 : Hernie discale (delai 6 mois) — manutention charges lourdes

PATHOLOGIES HORS TABLEAU :
Si une pathologie n'est pas listee dans un tableau (ex: burn-out, coccygodynie, fibromyalgie, depression...), elle peut QUAND MEME etre reconnue comme maladie professionnelle via la procedure COMPLEMENTAIRE :
- Alinea 3 de l'article L461-1 : maladie hors tableau avec IPP >= 25% + lien direct et essentiel avec le travail → examen par le CRRMP (Comite Regional de Reconnaissance des Maladies Professionnelles)
- Alinea 4 : maladie dans un tableau mais conditions non remplies (delai depasse, travaux differents) → CRRMP aussi

INDEMNISATION :
- IPP < 10% : capital forfaitaire
- IPP >= 10% : rente viagere
- Incidence Professionnelle (IP) : indemnisation des consequences sur la carriere
- PGPF : Perte de Gains Professionnels Futurs — capitalisation des revenus perdus
- Faute inexcusable : majoration de l'indemnisation si l'employeur avait conscience du danger"""


# Mots-clés qui nécessitent la base complète des tableaux MP
COMPLEX_SIGNALS = [
    "tableau", "amiante", "silicose", "tms", "canal carpien", "tendinite",
    "hernie", "lombalgie", "sciatique", "surdite", "crrmp", "alinea",
    "hors tableau", "ipp", "taux", "rente", "indemnisation", "capitalisation",
    "faute inexcusable", "pgpf", "incidence professionnelle", "consolidation",
    "rechute", "bareme", "burn out", "burnout", "depression", "inaptitude",
    "maladie professionnelle", "pathologie", "diagnostic", "epicondylite",
    "fibromyalgie", "coccyg", "menisque",
]


SYSTEM_PROMPT_LIGHT = """Tu es l'assistant expert de Strategie & Expertise Sante, un service francais d'accompagnement specialise dans les maladies professionnelles, accidents du travail, expertises medicales et litiges assurance.

REGLES DE REPONSE :
1. Reponds TOUJOURS en francais avec precision et expertise
2. Sois empathique mais professionnel
3. Donne des reponses concises et utiles
4. A la fin de ta reponse, suggere UNE action concrete parmi :
   - [Analyser votre situation avec StrategiIA](/simulateur)
   - [Commander un Dossier Express IA](/dossier-express)
   - [Prendre rendez-vous](/agenda)
   - [Consulter nos ressources](/ressources)

Pages du site :
- /expertise-medicale, /accident-travail-maladie-professionnelle, /mdph, /protection-juridique
- /calculatrice-ipp, /simulateur, /dossier-express, /tarifs, /contact, /ressources, /agenda"""


SYSTEM_PROMPT_FULL = f"""Tu es l'assistant expert de Strategie & Expertise Sante, un service francais d'accompagnement specialise dans les maladies professionnelles, accidents du travail, expertises medicales et litiges assurance.

Tu as une connaissance approfondie du droit de la securite sociale, des maladies professionnelles et de l'indemnisation corporelle.

{TABLEAUX_MP}

REGLES DE REPONSE :
1. Reponds TOUJOURS en francais avec precision et expertise
2. Pour les questions medicales specifiques (ex: "la coccygodynie est-elle dans un tableau ?"), donne une reponse PRECISE basee sur ta connaissance des tableaux ci-dessus
3. Si la pathologie N'EST PAS dans un tableau, explique clairement la procedure de reconnaissance hors tableau via le CRRMP (alinea 3 ou 4)
4. Cite les numeros de tableau quand c'est pertinent
5. Donne des informations concretes : delais, conditions, taux, procedures
6. Sois empathique mais professionnel — les personnes qui posent ces questions vivent souvent des situations difficiles
7. A la fin de ta reponse, suggere TOUJOURS une action concrete parmi :
   - [Analyser votre situation avec StrategiIA](/simulateur) pour une analyse personnalisee gratuite
   - [Commander un Dossier Express IA](/dossier-express) pour un rapport complet sous 2h
   - [Estimer votre indemnisation](/calculatrice-ipp) si le sujet est l'IPP
   - [Prendre rendez-vous](/agenda) pour un accompagnement personnalise
   - [Consulter nos ressources](/ressources) pour approfondir

IMPORTANT : Ne dis JAMAIS "je ne peux pas donner de conseil medical ou juridique". Tu ES un expert qui oriente et informe. Donne des reponses precises et utiles. Seul un disclaimer final rappelle que chaque situation est unique et merite un examen personnalise.

Pages du site :
- /expertise-medicale : Preparation aux expertises
- /accident-travail-maladie-professionnelle : Droits AT/MP
- /mdph : Demarches MDPH, AAH, RQTH
- /protection-juridique : Protection juridique
- /calculatrice-ipp : Calculatrice d'indemnisation IPP
- /simulateur : StrategiIA — analyse IA gratuite
- /dossier-express : Dossier Express IA (rapport PDF, 97 euros)
- /tarifs : Nos tarifs
- /contact : Formulaire de contact
- /ressources : FAQ, glossaire, encyclopedie
- /agenda : Prise de rendez-vous"""


def _is_complex_question(message: str) -> bool:
    msg = message.lower()
    return any(signal in msg for signal in COMPLEX_SIGNALS)


async def get_ai_response(message: str, session_id: str) -> str:
    if not EMERGENT_LLM_KEY:
        return ("Je suis desole, le service IA n'est pas disponible actuellement. "
                "Pour une analyse de votre situation, essayez notre [StrategiIA](/simulateur) "
                "ou commandez un [Dossier Express IA](/dossier-express).")

    try:
        prompt = SYSTEM_PROMPT_FULL if _is_complex_question(message) else SYSTEM_PROMPT_LIGHT

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=prompt,
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        user_message = UserMessage(text=message)
        response = await chat.send_message(user_message)
        return response

    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        return ("Je suis desole, une erreur s'est produite. "
                "Vous pouvez analyser votre situation avec [StrategiIA](/simulateur) "
                "ou consulter nos [ressources](/ressources).")
