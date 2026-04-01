from typing import Optional
import os
import httpx
import json as json_mod

from config import logger

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

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

    word_count = len(msg.split())
    if "?" in msg and word_count > 8:
        return None

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


COMPLEX_SIGNALS = [
    "tableau", "amiante", "silicose", "tms", "canal carpien", "tendinite",
    "hernie", "lombalgie", "sciatique", "surdite", "crrmp", "alinea",
    "hors tableau", "ipp", "taux", "rente", "indemnisation", "capitalisation",
    "faute inexcusable", "pgpf", "incidence professionnelle", "consolidation",
    "rechute", "bareme", "burn out", "burnout", "depression", "inaptitude",
    "maladie professionnelle", "pathologie", "diagnostic", "epicondylite",
    "fibromyalgie", "coccyg", "menisque",
]


SYSTEM_PROMPT_LIGHT = """Assistant d'orientation de Strategie & Expertise Sante.

REGLE : 1 seule phrase + 1 lien. JAMAIS plus de 2 lignes. Vouvoiement obligatoire.

Orientation :
- Situation / droits / strategie → **[StrategiIA](/simulateur)** (gratuit)
- Dossier / documents / suivi → **[Dossier Express IA](/dossier-express)**

INTERDIT : reponse longue, analyse, liste, explication, tutoiement, emoji."""


SYSTEM_PROMPT_FULL = """Assistant d'orientation de Strategie & Expertise Sante.

REGLE : 1 seule phrase + 1 lien. JAMAIS plus de 2 lignes. Vouvoiement obligatoire.

Orientation :
- Situation / droits / maladie / accident / expertise / MDPH / taux → **[StrategiIA](/simulateur)** (gratuit)
- Dossier / documents / suivi / recevabilite → **[Dossier Express IA](/dossier-express)**

INTERDIT : reponse longue, analyse, liste, explication, tutoiement, emoji."""


def _is_complex_question(message: str) -> bool:
    msg = message.lower()
    return any(signal in msg for signal in COMPLEX_SIGNALS)


async def get_ai_response(message: str, session_id: str) -> str:
    if not ANTHROPIC_API_KEY and not EMERGENT_LLM_KEY:
        return ("Je vous oriente : pour analyser votre situation → [StrategiIA](/simulateur) (gratuit) | "
                "pour analyser un dossier → [Dossier Express IA](/dossier-express) (rapport sous 2h).")

    try:
        prompt = SYSTEM_PROMPT_FULL if _is_complex_question(message) else SYSTEM_PROMPT_LIGHT

        if ANTHROPIC_API_KEY:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            response = await client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=150,
                system=prompt,
                messages=[{"role": "user", "content": message}],
            )
            return response.content[0].text

        # Fallback: Emergent LLM proxy
        from emergentintegrations.llm.utils import get_integration_proxy_url
        proxy_url = get_integration_proxy_url()
        url = f"{proxy_url}/llm/chat/completions"
        headers = {"Authorization": f"Bearer {EMERGENT_LLM_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "claude-haiku-4-5-20251001",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ],
            "max_tokens": 100
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise Exception(f"LLM proxy error {resp.status_code}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        return ("Je vous oriente : analyse de situation → [StrategiIA](/simulateur) (gratuit) | "
                "analyse de dossier → [Dossier Express IA](/dossier-express).")
