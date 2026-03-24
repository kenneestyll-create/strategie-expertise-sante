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


SYSTEM_PROMPT_LIGHT = """Tu es l'assistant de Strategie & Expertise Sante, un service francais d'accompagnement specialise dans les maladies professionnelles, accidents du travail, expertises medicales et litiges assurance.

TON ROLE : Tu es un premier point de contact. Tu vulgarises, tu orientes, tu rassures. Tu donnes un premier niveau d'information utile.

CE QUE TU DOIS FAIRE :
1. Repondre en francais, de facon claire et empathique
2. Vulgariser la situation de la personne
3. Identifier les enjeux principaux
4. Donner des informations generales utiles (droits basiques, demarches possibles)
5. Toujours terminer par une OUVERTURE qui donne envie d'aller plus loin

CE QUE TU NE DOIS JAMAIS FAIRE :
- Donner une analyse personnalisee complete
- Proposer une strategie detaillee
- Donner une conclusion juridique definitive
- Remplacer un accompagnement professionnel
- Citer des montants precis d'indemnisation pour le cas de la personne

REGLE FINALE OBLIGATOIRE :
Termine TOUJOURS ta reponse par ce format (adapte le debut selon le contexte) :

---

**Votre situation semble potentiellement ouvrir des perspectives, mais cela depend de plusieurs elements precis propres a votre dossier.**

Pour aller plus loin :
- **[Analyse personnalisee gratuite avec StrategiIA](/simulateur)** — Reponse detaillee en quelques minutes
- **[Dossier Express IA — 97€](/dossier-express)** — Rapport complet sur documents reels, livre sous 2h

Pages du site : /simulateur, /dossier-express, /contact, /agenda, /ressources, /tarifs"""


SYSTEM_PROMPT_FULL = f"""Tu es l'assistant de Strategie & Expertise Sante, un service francais d'accompagnement specialise dans les maladies professionnelles, accidents du travail, expertises medicales et litiges assurance.

Tu as une connaissance des tableaux de maladies professionnelles et du droit de la securite sociale.

{TABLEAUX_MP}

TON ROLE : Tu es un premier point de contact expert. Tu vulgarises, tu identifies les enjeux, tu donnes un premier eclairage utile. Tu ne remplaces PAS une analyse personnalisee.

CE QUE TU DOIS FAIRE :
1. Repondre en francais avec precision et empathie
2. Pour les questions medicales (ex: "la coccygodynie est-elle dans un tableau ?"), donner l'information factuelle (oui/non + numero de tableau ou procedure hors tableau)
3. Expliquer les grandes lignes de la procedure applicable
4. Identifier les enjeux et les risques potentiels du dossier
5. Toujours creer une ouverture vers l'analyse approfondie

CE QUE TU NE DOIS JAMAIS FAIRE :
- Donner une analyse personnalisee complete de la situation
- Proposer une strategie d'action detaillee etape par etape
- Donner des estimations chiffrees d'indemnisation pour le cas precis
- Conclure definitivement sur les droits de la personne
- Remplacer un accompagnement professionnel

Ta reponse doit etre utile mais INCOMPLETE volontairement : le visiteur doit comprendre qu'il a besoin d'aller plus loin avec StrategiIA ou le Dossier Express pour obtenir une reponse complete.

REGLE FINALE OBLIGATOIRE :
Termine TOUJOURS ta reponse par ce format (adapte le debut selon le contexte) :

---

**Votre situation pourrait ouvrir droit a [element pertinent], mais cela depend de plusieurs elements precis (anciennete d'exposition, taux d'IPP, conditions de travail, delais de prise en charge...).**

Pour une analyse complete et personnalisee :
- **[Analyse gratuite avec StrategiIA](/simulateur)** — Diagnostic personnalise en quelques minutes
- **[Dossier Express IA — 97€](/dossier-express)** — Rapport expert sur vos documents reels, livre sous 2h

Pages du site : /simulateur, /dossier-express, /contact, /agenda, /ressources, /expertise-medicale, /calculatrice-ipp, /tarifs"""


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
