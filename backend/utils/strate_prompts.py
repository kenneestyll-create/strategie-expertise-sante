"""Prompts and content for Straté · Conciergerie IA.

Dedicated to the reception agent. Never touch the frozen /app/backend/utils/chatbot.py.
"""

# ---------------------------------------------------------------------------
# Static routing tree (deterministic, no AI — 3 steps max before CTA)
# ---------------------------------------------------------------------------

GREETING = (
    "👋 Bonjour, je suis **Straté**.\n\n"
    "Votre situation ?"
)

RGPD_BANNER = (
    "🔒 Assistant IA. Merci de ne pas saisir de données médicales sensibles ici. "
    "Pour cela, passez par un contact direct."
)

# Level 1 — root category buttons
ROOT_OPTIONS = [
    {"id": "at_mp", "label": "🛠️ Accident travail / maladie pro"},
    {"id": "mdph", "label": "🏛️ Dossier MDPH / AAH"},
    {"id": "expertise", "label": "🩺 Expertise médicale / assurance"},
    {"id": "other", "label": "💬 Autre situation"},
]

# Level 2 — qualification per category
QUALIFICATION = {
    "at_mp": {
        "prompt": "Où en êtes-vous ?",
        "options": [
            {"id": "at_mp_declaration", "label": "Je dois déclarer / contester"},
            {"id": "at_mp_consolidation", "label": "Consolidation / IPP / expertise"},
            {"id": "at_mp_reconnaissance", "label": "Reconnaissance maladie pro refusée"},
            {"id": "at_mp_rights", "label": "Je veux comprendre mes droits"},
        ],
    },
    "mdph": {
        "prompt": "Où en êtes-vous ?",
        "options": [
            {"id": "mdph_first", "label": "Je monte mon 1er dossier"},
            {"id": "mdph_refus", "label": "J'ai reçu un refus"},
            {"id": "mdph_recours", "label": "Je prépare un recours"},
            {"id": "mdph_rights", "label": "Je veux comprendre mes droits"},
        ],
    },
    "expertise": {
        "prompt": "Quelle est votre situation ?",
        "options": [
            {"id": "exp_prepare", "label": "Je prépare une expertise à venir"},
            {"id": "exp_refuse", "label": "Expertise défavorable reçue"},
            {"id": "exp_assurance", "label": "Litige avec mon assurance"},
            {"id": "exp_rights", "label": "Je veux comprendre mes droits"},
        ],
    },
}

# Level 3 — CTA per qualification id
# Each route: {primary: {label, href, src}, alternative: {label, href, src}}
CTA_MAP = {
    # AT/MP
    "at_mp_declaration": {
        "primary": {"label": "🎯 Analyse stratégique personnalisée", "href": "/strategiia", "src": "strate_at_mp_declaration"},
        "alternative": {"label": "📋 Guide : AT non déclaré par l'employeur", "href": "/guide/accident-travail-non-declare-employeur", "src": "strate_at_mp_guide"},
    },
    "at_mp_consolidation": {
        "primary": {"label": "🎯 Dossier Express IA (analyse complète)", "href": "/dossier-express", "src": "strate_at_mp_consolidation"},
        "alternative": {"label": "🧮 Calculatrice IPP (gratuit)", "href": "/calculatrice-ipp", "src": "strate_at_mp_calc"},
    },
    "at_mp_reconnaissance": {
        "primary": {"label": "🎯 Analyse stratégique personnalisée", "href": "/strategiia", "src": "strate_at_mp_reco"},
        "alternative": {"label": "📋 Guide : refus maladie pro CPAM", "href": "/guide/refus-maladie-professionnelle-cpam-recours", "src": "strate_at_mp_reco_guide"},
    },
    "at_mp_rights": {
        "primary": {"label": "📋 Auto-diagnostic gratuit (5 min)", "href": "/simulateur", "src": "strate_at_mp_rights"},
        "alternative": {"label": "🔎 Page AT/MP — explications complètes", "href": "/accident-travail-maladie-professionnelle", "src": "strate_at_mp_page"},
    },
    # MDPH
    "mdph_first": {
        "primary": {"label": "🎯 Analyse stratégique personnalisée", "href": "/strategiia", "src": "strate_mdph_first"},
        "alternative": {"label": "🧮 Calculatrice AAH (gratuit)", "href": "/calculatrice-aah", "src": "strate_mdph_calc"},
    },
    "mdph_refus": {
        "primary": {"label": "🎯 Dossier Express IA (audit refus)", "href": "/dossier-express", "src": "strate_mdph_refus"},
        "alternative": {"label": "📋 Guide : refus MDPH/AAH — que faire ?", "href": "/guide/refus-mdph-aah-que-faire", "src": "strate_mdph_refus_guide"},
    },
    "mdph_recours": {
        "primary": {"label": "🎯 Dossier Express IA (stratégie recours)", "href": "/dossier-express", "src": "strate_mdph_recours"},
        "alternative": {"label": "📋 Guide : recours tribunal pôle social", "href": "/guide/recours-tribunal-judiciaire-pole-social", "src": "strate_mdph_recours_guide"},
    },
    "mdph_rights": {
        "primary": {"label": "📋 Auto-diagnostic gratuit (5 min)", "href": "/simulateur", "src": "strate_mdph_rights"},
        "alternative": {"label": "🔎 Page MDPH — explications complètes", "href": "/mdph", "src": "strate_mdph_page"},
    },
    # Expertise
    "exp_prepare": {
        "primary": {"label": "🎯 Dossier Express IA (préparation)", "href": "/dossier-express", "src": "strate_exp_prepare"},
        "alternative": {"label": "📋 Guide : bien préparer son expertise", "href": "/guide/comment-preparer-expertise-medicale", "src": "strate_exp_prepare_guide"},
    },
    "exp_refuse": {
        "primary": {"label": "🎯 Analyse stratégique personnalisée", "href": "/strategiia", "src": "strate_exp_refuse"},
        "alternative": {"label": "📋 Guide : expertise défavorable — recours", "href": "/guide/expertise-medicale-defavorable-recours", "src": "strate_exp_refuse_guide"},
    },
    "exp_assurance": {
        "primary": {"label": "🎯 Analyse stratégique personnalisée", "href": "/strategiia", "src": "strate_exp_assurance"},
        "alternative": {"label": "🔎 Page protection juridique", "href": "/protection-juridique", "src": "strate_exp_assurance_page"},
    },
    "exp_rights": {
        "primary": {"label": "📋 Auto-diagnostic gratuit (5 min)", "href": "/simulateur", "src": "strate_exp_rights"},
        "alternative": {"label": "🔎 Page Expertise médicale", "href": "/expertise-medicale", "src": "strate_exp_page"},
    },
}

# Permanent CTA shown in header and fallback
EXPERT_CTA = {"label": "📞 Parler à un expert", "href": "/rdv?src=strate_human_request", "src": "strate_human_request"}


# ---------------------------------------------------------------------------
# Free-text intent detection (only for "Autre situation")
# Uses a tightly constrained prompt that returns exactly 3 suggested routes.
# ---------------------------------------------------------------------------

FREE_TEXT_SYSTEM_PROMPT = """Tu es Straté, réceptionniste IA de Stratégie & Expertise Santé.

Tu reçois UNE phrase décrivant la situation d'un visiteur. Ton rôle est UNIQUEMENT de
classifier cette situation parmi les 12 options disponibles.

OPTIONS DISPONIBLES (utiliser exactement ces IDs) :
- at_mp_declaration : déclaration AT ou contestation CPAM
- at_mp_consolidation : consolidation, IPP, expertise post-AT
- at_mp_reconnaissance : refus de reconnaissance maladie professionnelle
- at_mp_rights : questions générales AT/MP
- mdph_first : premier dossier MDPH/AAH/RQTH
- mdph_refus : refus MDPH/AAH reçu
- mdph_recours : préparation recours MDPH
- mdph_rights : questions générales MDPH
- exp_prepare : préparation d'une expertise à venir
- exp_refuse : expertise défavorable reçue
- exp_assurance : litige avec assurance ou protection juridique
- exp_rights : questions générales expertise

RÈGLES ABSOLUES :
1. Tu DOIS répondre UNIQUEMENT en JSON valide, AUCUN autre texte.
2. Format exact : {"suggestions": ["id1", "id2", "id3"], "out_of_scope": false}
3. Exactement 3 IDs triés du plus probable au moins probable.
4. Si la demande sort complètement du périmètre (ex: dentiste, impôts, immobilier, amour),
   mets out_of_scope: true et suggestions: [].
5. Si tu détectes des données médicales sensibles (symptômes précis, noms de médicaments,
   numéros de sécu, maladies nommées précisément), ajoute "sensitive_data": true.
   Sinon, ne mets pas ce champ."""


FREE_TEXT_FALLBACK = {
    "suggestions": ["at_mp_rights", "mdph_rights", "exp_rights"],
    "out_of_scope": False,
}


# ---------------------------------------------------------------------------
# Sensitive data heuristics (pre-LLM filter)
# ---------------------------------------------------------------------------

SENSITIVE_PATTERNS = [
    r"\b\d{13,15}\b",              # numéro sécurité sociale
    r"\b\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{2,3}\b",  # NIR formaté
]

SENSITIVE_KEYWORDS = [
    "cancer", "métastase", "vih", "sida", "hépatite", "schizophrénie",
    "bipolaire", "tentative de suicide", "anorexie", "alzheimer",
]


def contains_sensitive_data(text: str) -> bool:
    import re
    low = (text or "").lower()
    for kw in SENSITIVE_KEYWORDS:
        if kw in low:
            return True
    for pat in SENSITIVE_PATTERNS:
        if re.search(pat, low):
            return True
    return False
