"""S.E.S Autonomous Video Factory — single-call LLM agent.

Architecture validée (voir échanges du 20/05/2026) :
- 1 endpoint, 1 appel LLM, 6 personas simulés dans un prompt unique
- Modèle par défaut : Claude Haiku 4.5 (via Anthropic SDK natif si clé, sinon Emergent proxy)
- Sortie JSON strict, validée par un audit Python (compliance + structure)
- Coût cible : <0,01€/vidéo (atteint à ~0,006€ batch 5 + cache)

Garde-fous activés :
- Auto-check LLM (discipline interne) + validateur Python (objectif)
- Mots interdits, mapping CTA dur, 7 formats verrouillés
- Retry unique sur JSON malformé (température 0.1)
"""
import os
import re
import json as json_mod
from typing import Dict, List, Any, Optional, Tuple

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
MAX_BATCH_SIZE = 5
SITE_URL = "https://strategie-expertise-sante.fr"

# ============================================================================
# SYSTEM PROMPT — Statique, cache-friendly (~2400 tokens)
# ============================================================================

SYSTEM_PROMPT = """# IDENTITÉ
Tu es S.E.S Video Factory Engine.
Tu génères des vidéos courtes (30-60s) pour un cabinet français spécialisé en
accidents du travail (AT), maladies professionnelles (MP), invalidité / IPP,
MDPH et litiges assurantiels.

Tu n'es PAS :
- avocat
- médecin
- conseiller financier

Tu produis uniquement du contenu informatif grand public.

# OBJECTIF PRINCIPAL
CONVERSION > CLARTÉ > VIRALITÉ

Maximiser les actions (clic, prise de contact, simulateur), sans promesse garantie.

# PUBLIC
Personnes 35-65 ans :
- douleur administrative ou médicale réelle
- forte méfiance institutionnelle
- besoin de clarté simple et directe

# FORMATS AUTORISÉS (STRICT — CHOISIR UN SEUL)
F1 — Erreurs en expertise médicale (ne jamais dire ça au médecin-conseil)
F2 — Explications chiffrées (IPP, indemnisation, droits)
F3 — Cas réel anonymisé
F4 — Analyse CPAM / médecin-conseil (ce qu'ils regardent vraiment)
F5 — Réaction à un courrier administratif
F6 — Erreurs de vocabulaire qui font perdre des droits
F7 — Checklist préparation dossier / expertise

INTERDICTION : inventer un format, fusionner plusieurs formats.

# MAPPING SERVICE → CTA → URL (1 SEUL CTA PAR VIDÉO)
- service "0€" (StratégiIA gratuit) :
    CTA  = "Diagnostic gratuit 2 min, lien en bio"
    URL  = "https://strategie-expertise-sante.fr/simulateur"
- service "29€" (Analyse PDF) :
    CTA  = "Le PDF d'analyse complet est en bio — 29€"
    URL  = "https://strategie-expertise-sante.fr/analyse-pdf"
- service "97€" (Dossier Express IA) :
    CTA  = "Expertise dans moins de 30 jours ? Rapport en 2h, 97€"
    URL  = "https://strategie-expertise-sante.fr/dossier-express"

Si "service_target = auto", choisir selon urgence :
    critique → 97€   |   moyen → 29€   |   faible → 0€

UTM à ajouter automatiquement à l'URL :
    ?utm_source={plateforme_lower}&utm_medium=short&utm_campaign={format_id}

# PERFORMANCE INPUT (BACKEND-ONLY, OPTIONNEL)
Tu peux recevoir dans le user prompt :
- forced_format : F1-F7 → l'utiliser obligatoirement, ne pas réinterpréter
- performance_weights : informationnel uniquement (la pondération est appliquée
  côté backend). Si forced_format absent, choisis librement parmi F1-F7
  selon le topic_brief.

Le LLM ne fait AUCUN calcul de probabilité.

# RÈGLES DURES (NON NÉGOCIABLES)
- Langue : français uniquement, registre parlé naturel
- Hook : ≤ 12 mots, idéal 5-8 mots
- Script total : 70 à 150 mots (≈ 30-60 secondes parlé)
- Phrases courtes (≤ 15 mots). Vouvoiement si urgence=critique, sinon tutoiement OK.
- 1 SEUL CTA en fin de script
- Storyboard : 6 plans maximum
- Sous-titres .srt : ≤ 7-10 mots par segment, ≤ 2 lignes, durée 1-3s par segment
- Sortie : JSON STRICT uniquement. Aucun texte hors JSON. Aucun markdown.

# COMPLIANCE (STRICT)
INTERDIT :
- "garanti", "garantie", "100%", "sûr à 100%", "assuré"
- "vous allez gagner X €" (toujours conditionnel)
- "remboursement automatique", "gain assuré"
- "la CPAM ment", "les médecins mentent", dénigrement institutionnel direct
- diagnostic médical personnalisé ("vous avez une lombalgie")
- promesses chiffrées non sourcées
- manipulation émotionnelle extrême, catastrophisme irréaliste

AUTORISÉ :
- pédagogie, cas anonymisés, explications générales
- "vous pourriez", "dans certains cas", "selon votre situation"
- chiffres contextualisés ("en moyenne", "selon les cas")

# AUTO-CHECK INTERNE (avant de finaliser le JSON)
Vérifie silencieusement :
✔ Exactement 1 CTA par vidéo (jamais 2)
✔ Aucun mot interdit dans hook/script/sous-titres
✔ Format choisi parmi F1-F7 uniquement
✔ Storyboard ≤ 6 plans
✔ Script entre 70 et 150 mots
✔ Hook ≤ 12 mots
✔ URL avec UTM correct
✔ JSON parsable strictement
✔ compliance_passed = true uniquement si TOUT respecté

# SCHEMA JSON DE SORTIE (RESPECT ABSOLU)
{
  "videos": [
    {
      "format_used": "F1",
      "format_label": "Erreurs en expertise médicale",
      "viral_score": 4,
      "conversion_score": 4,
      "hook_variants": [
        "Hook variante A (≤12 mots).",
        "Hook variante B (≤12 mots).",
        "Hook variante C (≤12 mots)."
      ],
      "script": "Texte complet 70-150 mots, ton parlé naturel.",
      "storyboard": [
        {
          "plan": 1,
          "type": "face-cam",
          "description": "Plan poitrine, regard caméra, ton grave.",
          "ambiance": "intérieur neutre, éclairage doux",
          "duree_sec": 3,
          "broll_search_term": null
        }
      ],
      "subtitles_srt": "1\\n00:00:00,000 --> 00:00:03,000\\nTexte ≤7 mots.\\n\\n2\\n00:00:03,000 --> 00:00:06,000\\nSuite.",
      "seo": {
        "title": "Titre <60 caractères, optimisé plateforme",
        "description": "Description <200 caractères avec hashtags incorporés.",
        "hashtags": ["#expertisemedicale", "#ipp", "#cpam", "#maladiepro", "#droits"]
      },
      "cta": {
        "text": "Texte du CTA pris dans le mapping ci-dessus",
        "target_service": "0€",
        "url_with_utm": "https://strategie-expertise-sante.fr/simulateur?utm_source=tiktok&utm_medium=short&utm_campaign=F1"
      },
      "disclaimer_text": "Contenu informatif, ne constitue pas un conseil médical ou juridique personnalisé.",
      "compliance_passed": true
    }
  ]
}

# Types de plans autorisés dans storyboard : face-cam | broll | texte
# Chaque plan doit être simple, concret, filmable avec un téléphone.

# INSTRUCTION FINALE
- Génère exactement le nombre de vidéos demandé (1 à 5).
- Aucun texte hors JSON. Pas de ```json, pas de commentaires.
- Si compromis nécessaire, priorité : conversion > clarté > viralité > SEO.
"""

# ============================================================================
# FORMAT LABELS (utilisés par le validator pour normaliser)
# ============================================================================

FORMAT_LABELS = {
    "F1": "Erreurs en expertise médicale",
    "F2": "Explications chiffrées (IPP, indemnisation)",
    "F3": "Cas réel anonymisé",
    "F4": "Analyse CPAM / médecin-conseil",
    "F5": "Réaction à un courrier administratif",
    "F6": "Erreurs de vocabulaire",
    "F7": "Checklist préparation dossier",
}

# Mapping service → texte CTA + URL de base (pour validation)
SERVICE_MAPPING = {
    "0€": {
        "text": "Diagnostic gratuit 2 min, lien en bio",
        "base_url": f"{SITE_URL}/simulateur",
    },
    "29€": {
        "text": "Le PDF d'analyse complet est en bio — 29€",
        "base_url": f"{SITE_URL}/analyse-pdf",
    },
    "97€": {
        "text": "Expertise dans moins de 30 jours ? Rapport en 2h, 97€",
        "base_url": f"{SITE_URL}/dossier-express",
    },
}

URGENCE_TO_SERVICE = {
    "faible": "0€",
    "moyen": "29€",
    "critique": "97€",
}

# Mots/regex interdits (audit Python objectif côté backend)
FORBIDDEN_PATTERNS = [
    r"\bgarantit?e?s?\b",
    r"\b100\s*%\b",
    r"\bsûr\s+à\s+100\b",
    r"la\s+CPAM\s+ment",
    r"les\s+médecins\s+mentent",
    r"\bils\s+vous\s+arnaquent\b",
    r"remboursement\s+automatique",
    r"\bgain\s+assuré\b",
]


DEFAULT_DISCLAIMER = (
    "Contenu informatif, ne constitue pas un conseil médical ou juridique personnalisé."
)


# ============================================================================
# BUILDER — Assemblage du user prompt
# ============================================================================

def build_user_prompt(
    topic_brief: str,
    service_target: str,
    intention: str,
    urgence: str,
    plateforme: str,
    batch_size: int,
    forced_format: Optional[str] = None,
    performance_weights: Optional[Dict[str, float]] = None,
) -> str:
    """Construit la portion 'user' du prompt (dynamique, non cachée).
    V2 : injecte forced_format et performance_weights si fournis.
    """
    parts = [
        f"Génère {batch_size} vidéo(s) avec ces paramètres :",
        f"- topic_brief : \"{topic_brief}\"",
        f"- service_target : {service_target}",
        f"- intention : {intention}",
        f"- urgence : {urgence}",
        f"- plateforme : {plateforme}",
    ]
    if forced_format and forced_format in FORMAT_LABELS:
        parts.append(
            f"- forced_format : {forced_format} "
            f"(OBLIGATOIRE — utiliser ce format, ne pas réinterpréter)"
        )
    if performance_weights:
        weights_str = ", ".join(
            f"{k}={v:.2f}" for k, v in sorted(performance_weights.items())
        )
        parts.append(f"- performance_weights (informationnel) : {weights_str}")
    parts.append("")
    parts.append("Réponds uniquement avec le JSON strict, aucun texte autour.")
    return "\n".join(parts)


# ============================================================================
# LLM CALL — Single shot, Haiku 4.5, JSON strict
# ============================================================================

async def call_video_factory_llm(
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 9000,
    temperature: float = 0.7,
) -> str:
    """Appel LLM unique. Anthropic SDK natif si clé présente, sinon Emergent proxy.
    Retourne le raw text. Caching prompt activé côté SDK Anthropic via cache_control.
    """
    if ANTHROPIC_API_KEY:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY, timeout=90.0)
        resp = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
        )
        return resp.content[0].text.strip()

    if EMERGENT_LLM_KEY:
        import httpx
        from emergentintegrations.llm.utils import get_integration_proxy_url
        proxy_url = get_integration_proxy_url()
        url = f"{proxy_url}/llm/chat/completions"
        headers = {
            "Authorization": f"Bearer {EMERGENT_LLM_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=15.0)) as h:
            r = await h.post(url, headers=headers, json=payload)
            if r.status_code != 200:
                raise RuntimeError(f"LLM proxy {r.status_code}: {r.text[:200]}")
            return r.json()["choices"][0]["message"]["content"].strip()

    raise RuntimeError("Aucune clé LLM disponible (ANTHROPIC_API_KEY ou EMERGENT_LLM_KEY).")


# ============================================================================
# PARSE & VALIDATE — JSON strict + compliance audit
# ============================================================================

def safe_parse_json(raw: str) -> Dict[str, Any]:
    """Parse JSON tolérant : enlève blocs ```json...``` si présents."""
    text = raw.strip()
    if text.startswith("```"):
        # remove leading ```json or ``` and trailing ```
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json_mod.loads(text)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def _contains_forbidden(text: str) -> List[str]:
    """Retourne la liste des patterns interdits trouvés (vide si OK)."""
    found = []
    low = (text or "").lower()
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, low, flags=re.IGNORECASE):
            found.append(pat)
    return found


def _resolve_service(service_target: str, urgence: str) -> str:
    """Résout 'auto' en service concret selon urgence."""
    if service_target in SERVICE_MAPPING:
        return service_target
    return URGENCE_TO_SERVICE.get(urgence, "0€")


def _build_utm_url(base_url: str, plateforme: str, format_id: str) -> str:
    plat = (plateforme or "tiktok").lower().replace(" ", "")
    return f"{base_url}?utm_source={plat}&utm_medium=short&utm_campaign={format_id}"


def validate_and_normalize(
    parsed: Dict[str, Any],
    service_target: str,
    urgence: str,
    plateforme: str,
) -> Tuple[Dict[str, Any], List[str]]:
    """Audit objectif Python. Retourne (data_normalisée, warnings).
    Lève ValueError si la structure est invalide au-delà de toute récupération.
    """
    warnings: List[str] = []

    if not isinstance(parsed, dict) or "videos" not in parsed:
        raise ValueError("JSON invalide : clé 'videos' manquante.")

    videos = parsed.get("videos") or []
    if not isinstance(videos, list) or not videos:
        raise ValueError("JSON invalide : 'videos' doit être une liste non vide.")

    resolved_service = _resolve_service(service_target, urgence)
    mapping = SERVICE_MAPPING[resolved_service]

    for idx, v in enumerate(videos):
        if not isinstance(v, dict):
            raise ValueError(f"Vidéo #{idx+1} : structure invalide.")

        # Format
        fmt = v.get("format_used", "")
        if fmt not in FORMAT_LABELS:
            warnings.append(f"v{idx+1}: format '{fmt}' inconnu, normalisé en F1.")
            v["format_used"] = "F1"
            fmt = "F1"
        v["format_label"] = FORMAT_LABELS[fmt]

        # Viral score
        try:
            vs = int(v.get("viral_score", 3))
            v["viral_score"] = max(1, min(5, vs))
        except (TypeError, ValueError):
            v["viral_score"] = 3

        # Conversion score (V2)
        try:
            cs = int(v.get("conversion_score", 3))
            v["conversion_score"] = max(1, min(5, cs))
        except (TypeError, ValueError):
            v["conversion_score"] = 3

        # Disclaimer (V2) — toujours renseigné côté backend
        dt = (v.get("disclaimer_text") or "").strip()
        v["disclaimer_text"] = dt or DEFAULT_DISCLAIMER

        # Hook variants
        hooks = v.get("hook_variants") or []
        if not isinstance(hooks, list):
            hooks = []
        cleaned = []
        for h in hooks:
            if isinstance(h, str) and h.strip():
                wc = _word_count(h)
                if wc > 12:
                    warnings.append(f"v{idx+1}: hook '{h[:30]}...' dépasse 12 mots ({wc}).")
                cleaned.append(h.strip())
        if len(cleaned) < 3:
            while len(cleaned) < 3:
                cleaned.append("Hook à reformuler.")
            warnings.append(f"v{idx+1}: <3 hooks valides, padding appliqué.")
        v["hook_variants"] = cleaned[:3]

        # Script
        script = (v.get("script") or "").strip()
        wc = _word_count(script)
        if wc < 50:
            warnings.append(f"v{idx+1}: script trop court ({wc} mots).")
        if wc > 180:
            warnings.append(f"v{idx+1}: script trop long ({wc} mots).")
        v["script"] = script

        # Storyboard
        sb = v.get("storyboard") or []
        if not isinstance(sb, list):
            sb = []
        if len(sb) > 6:
            warnings.append(f"v{idx+1}: storyboard >6 plans, tronqué.")
            sb = sb[:6]
        for i, plan in enumerate(sb):
            if isinstance(plan, dict):
                plan.setdefault("plan", i + 1)
                plan.setdefault("type", "face-cam")
                plan.setdefault("description", "")
                plan.setdefault("ambiance", None)
                try:
                    plan["duree_sec"] = int(plan.get("duree_sec", 5))
                except (TypeError, ValueError):
                    plan["duree_sec"] = 5
                plan.setdefault("broll_search_term", None)
        v["storyboard"] = sb

        # Subtitles
        v["subtitles_srt"] = (v.get("subtitles_srt") or "").strip()

        # SEO
        seo = v.get("seo") or {}
        if not isinstance(seo, dict):
            seo = {}
        seo.setdefault("title", "")
        seo.setdefault("description", "")
        hashtags = seo.get("hashtags") or []
        if not isinstance(hashtags, list):
            hashtags = []
        seo["hashtags"] = [h for h in hashtags if isinstance(h, str)]
        v["seo"] = seo

        # CTA — OVERRIDE total côté backend pour garantie 100%
        cta = v.get("cta") or {}
        if not isinstance(cta, dict):
            cta = {}
        cta["target_service"] = resolved_service
        cta["text"] = mapping["text"]
        cta["url_with_utm"] = _build_utm_url(mapping["base_url"], plateforme, fmt)
        v["cta"] = cta

        # Compliance audit objectif
        all_text = " ".join([
            script,
            " ".join(cleaned),
            v.get("subtitles_srt", ""),
            seo.get("title", ""),
            seo.get("description", ""),
        ])
        forbidden = _contains_forbidden(all_text)
        v["compliance_passed"] = (len(forbidden) == 0)
        if forbidden:
            v["compliance_notes"] = f"Mots/formules suspectes détectées : {forbidden}"
            warnings.append(f"v{idx+1}: compliance FAIL ({len(forbidden)} pattern(s)).")
        else:
            v["compliance_notes"] = None

    return parsed, warnings


# ============================================================================
# COST ESTIMATION (informatif — affiché côté admin UI)
# ============================================================================

def estimate_cost_eur(batch_size: int, model: str = DEFAULT_MODEL) -> float:
    """Estimation grossière du coût en euros (Haiku 4.5, batch + cache).
    Calibré sur token math validé en phase étude.
    """
    if model.startswith("claude-haiku"):
        # ~0.006€/vidéo avec cache+batch
        return round(0.006 * batch_size, 4)
    if model.startswith("claude-sonnet"):
        return round(0.020 * batch_size, 4)
    # Fallback conservateur
    return round(0.010 * batch_size, 4)


# ============================================================================
# V3 — SEO LANDING SYNCHRONISATION
# ============================================================================
# Génère une page SEO (markdown + métadonnées) STRICTEMENT dérivée du pack
# vidéo : aucun nouveau message, aucune divergence. Le CTA et le service
# cible sont copiés depuis la vidéo (override backend = garantie 100%).
#
# UTM différencié : utm_source=seo&utm_medium=organic (vs vidéo TikTok/short)
# pour permettre l'attribution Analytics distincte SEO vs vidéo.

SEO_LANDING_SYSTEM_PROMPT = """# IDENTITÉ
Tu es S.E.S SEO Landing Engine.
Tu produis des pages web (markdown structuré) destinées à être publiées sur
strategie-expertise-sante.fr/guide/{slug} en tant que page d'atterrissage
SEO d'une vidéo courte (TikTok/Shorts/Reels).

# PUBLIC
Personnes 35-65 ans, recherche organique Google :
- mots-clés douleur AT/MP/MDPH/IPP/CPAM/expertise médicale
- méfiance institutionnelle
- besoin de réponses claires et factuelles

# OBJECTIF
Transformer un pack vidéo existant en page SEO complète, SANS DIVERGENCE
de message. Tu RÉUTILISES :
- le hook (transformé en intro accrocheuse)
- le script (développé en blocs H2/H3 avec phrases pleines)
- le CTA (verbatim, jamais modifié)
- les hashtags (transformés en mots-clés SEO contextuels)

INTERDICTION ABSOLUE :
- inventer des chiffres absents de la vidéo
- inventer des jurisprudences ou références légales non présentes
- changer le service cible (0€/29€/97€) ou le CTA
- ajouter de nouvelles promesses

# RÈGLES DE QUALITÉ SEO
- meta_title : 50-60 caractères, mot-clé principal en début
- meta_description : 140-160 caractères, action + bénéfice + nuance
- h1 : ≤70 caractères, percutant, contient le mot-clé principal
- intro : 100-180 mots, accroche reprenant le hook vidéo + promesse
- 3 à 5 blocs H2 (chacun 80-150 mots, sans bullet excessif)
- 3 à 5 questions FAQ (questions réelles que se pose la cible)
- slug : kebab-case, 3-7 mots, sans accent, sans stopword inutile
- internal_links_suggestions : 2 à 4 chemins internes pertinents (ex /expertise-medicale, /calculatrice-ipp, /guide/comment-contester-decision-cpam)

# COMPLIANCE (STRICT, IDENTIQUE VIDÉO)
INTERDIT : "garanti", "100%", "assuré", "vous allez gagner X €",
"la CPAM ment", "remboursement automatique", diagnostic médical personnalisé.
AUTORISÉ : "vous pourriez", "dans certains cas", "selon votre situation",
"en moyenne", chiffres contextualisés.

# UTM (OBLIGATOIRE, DIFFÉRENT DE LA VIDÉO)
Format strict : ?utm_source=seo&utm_medium=organic&utm_campaign={format_used}

# SCHEMA JSON DE SORTIE (RESPECT ABSOLU)
{
  "seo_pdf": {
    "slug": "kebab-case-3-7-mots",
    "h1": "≤70 caractères",
    "meta_title": "50-60 caractères",
    "meta_description": "140-160 caractères",
    "intro": "100-180 mots de paragraphe d'ouverture",
    "blocks": [
      {"h2": "...", "body": "80-150 mots"}
    ],
    "faq": [
      {"q": "Question utilisateur réelle ?", "a": "Réponse 40-80 mots."}
    ],
    "internal_links_suggestions": ["/expertise-medicale", "/calculatrice-ipp"],
    "keywords": ["mot-clé 1", "mot-clé 2", "mot-clé 3"],
    "video_embed_placeholder": "<!-- COLLER L'URL YOUTUBE OU TIKTOK ICI APRES PUBLICATION -->",
    "compliance_passed": true
  }
}

# INSTRUCTION FINALE
Aucun texte hors JSON. Pas de markdown autour du JSON. Pas de commentaires.
Si compromis nécessaire, priorité : fidélité au pack vidéo > SEO > style.
"""


def build_seo_landing_user_prompt(video: Dict[str, Any], plateforme: str) -> str:
    """Assemble le prompt utilisateur : le pack vidéo finalisé sert d'input."""
    seo = video.get("seo") or {}
    cta = video.get("cta") or {}
    hooks = " | ".join(video.get("hook_variants") or [])
    parts = [
        "Transforme ce pack vidéo en page SEO d'atterrissage cohérente.",
        "",
        f"FORMAT_VIDEO : {video.get('format_used')} — {video.get('format_label')}",
        f"PLATEFORME_VIDEO_SOURCE : {plateforme}",
        f"HOOKS (à transformer en intro) : {hooks}",
        "",
        "SCRIPT VIDÉO (référence absolue, à développer en blocs H2) :",
        f"\"\"\"{video.get('script', '')}\"\"\"",
        "",
        f"SEO_TITRE_VIDEO : {seo.get('title', '')}",
        f"SEO_DESCRIPTION_VIDEO : {seo.get('description', '')}",
        f"HASHTAGS : {', '.join(seo.get('hashtags') or [])}",
        "",
        "CTA À REPRENDRE VERBATIM (interdit de le modifier) :",
        f"  text = \"{cta.get('text', '')}\"",
        f"  target_service = \"{cta.get('target_service', '')}\"",
        f"  base_url = \"{(cta.get('url_with_utm') or '').split('?')[0]}\"",
        "",
        "Réponds uniquement avec le JSON strict, aucun texte autour.",
    ]
    return "\n".join(parts)


async def call_seo_landing_llm(
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 6000,
    temperature: float = 0.5,
) -> str:
    """Appel LLM dédié SEO landing — séparé du LLM vidéo pour conserver la
    qualité de chaque livrable. Mêmes patterns d'auth que call_video_factory_llm.
    """
    if ANTHROPIC_API_KEY:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY, timeout=90.0)
        resp = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=[
                {
                    "type": "text",
                    "text": SEO_LANDING_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
        )
        return resp.content[0].text.strip()

    if EMERGENT_LLM_KEY:
        import httpx
        from emergentintegrations.llm.utils import get_integration_proxy_url
        proxy_url = get_integration_proxy_url()
        url = f"{proxy_url}/llm/chat/completions"
        headers = {
            "Authorization": f"Bearer {EMERGENT_LLM_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SEO_LANDING_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=15.0)) as h:
            r = await h.post(url, headers=headers, json=payload)
            if r.status_code != 200:
                raise RuntimeError(f"LLM proxy {r.status_code}: {r.text[:200]}")
            return r.json()["choices"][0]["message"]["content"].strip()

    raise RuntimeError("Aucune clé LLM disponible.")


def _slugify(text: str) -> str:
    """Slug kebab-case ASCII safe, fallback si LLM retourne vide ou casseur."""
    import unicodedata
    norm = unicodedata.normalize("NFKD", (text or "").lower())
    ascii_text = norm.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return cleaned[:80] or "page-seo"


def validate_and_normalize_seo_landing(
    parsed: Dict[str, Any],
    video: Dict[str, Any],
    format_id: str,
) -> Tuple[Dict[str, Any], List[str]]:
    """Audit objectif Python + override CTA pour garantie 100% non-divergence.
    Retourne (seo_pdf normalisé, warnings).
    """
    warnings: List[str] = []
    if not isinstance(parsed, dict) or "seo_pdf" not in parsed:
        raise ValueError("JSON SEO invalide : clé 'seo_pdf' manquante.")

    seo = parsed["seo_pdf"]
    if not isinstance(seo, dict):
        raise ValueError("seo_pdf doit être un objet.")

    # Slug
    slug = (seo.get("slug") or "").strip()
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug or "") or len(slug) > 80:
        fallback = _slugify(seo.get("h1") or video.get("seo", {}).get("title") or format_id)
        warnings.append(f"slug invalide '{slug}', normalisé en '{fallback}'.")
        slug = fallback
    seo["slug"] = slug

    # h1
    seo["h1"] = (seo.get("h1") or "").strip()
    if len(seo["h1"]) > 70:
        warnings.append("h1 >70 caractères.")
    elif not seo["h1"]:
        warnings.append("h1 vide.")

    # Meta
    seo["meta_title"] = (seo.get("meta_title") or "").strip()
    seo["meta_description"] = (seo.get("meta_description") or "").strip()

    # Intro
    seo["intro"] = (seo.get("intro") or "").strip()
    intro_wc = len(re.findall(r"\b\w+\b", seo["intro"]))
    if intro_wc < 60:
        warnings.append(f"intro courte ({intro_wc} mots).")

    # Blocks
    blocks = seo.get("blocks") or []
    if not isinstance(blocks, list):
        blocks = []
    cleaned_blocks = []
    for b in blocks[:5]:
        if isinstance(b, dict):
            cleaned_blocks.append({
                "h2": (b.get("h2") or "").strip(),
                "body": (b.get("body") or "").strip(),
            })
    if len(cleaned_blocks) < 3:
        warnings.append(f"blocks <3 ({len(cleaned_blocks)}).")
    seo["blocks"] = cleaned_blocks

    # FAQ
    faq = seo.get("faq") or []
    if not isinstance(faq, list):
        faq = []
    cleaned_faq = []
    for f in faq[:5]:
        if isinstance(f, dict):
            cleaned_faq.append({
                "q": (f.get("q") or "").strip(),
                "a": (f.get("a") or "").strip(),
            })
    seo["faq"] = cleaned_faq

    # Keywords / internal_links
    seo["keywords"] = [k for k in (seo.get("keywords") or []) if isinstance(k, str)]
    seo["internal_links_suggestions"] = [
        k for k in (seo.get("internal_links_suggestions") or []) if isinstance(k, str)
    ]

    # Video embed placeholder
    seo["video_embed_placeholder"] = (
        seo.get("video_embed_placeholder")
        or "<!-- COLLER L'URL YOUTUBE OU TIKTOK ICI APRES PUBLICATION -->"
    )

    # === CTA OVERRIDE (anti-divergence absolue) ===
    video_cta = video.get("cta") or {}
    base_url = (video_cta.get("url_with_utm") or "").split("?")[0]
    seo["cta_block"] = {
        "text": video_cta.get("text") or "",
        "target_service": video_cta.get("target_service") or "",
        "url_with_utm": f"{base_url}?utm_source=seo&utm_medium=organic&utm_campaign={format_id}" if base_url else "",
    }

    # === Compliance audit (mêmes regex que la vidéo) ===
    all_text = " ".join([
        seo["h1"], seo["meta_title"], seo["meta_description"], seo["intro"],
        " ".join(b.get("body", "") for b in seo["blocks"]),
        " ".join(b.get("h2", "") for b in seo["blocks"]),
        " ".join(f.get("a", "") for f in seo["faq"]),
    ])
    forbidden = _contains_forbidden(all_text)
    seo["compliance_passed"] = (len(forbidden) == 0)
    if forbidden:
        seo["compliance_notes"] = f"Mots/formules suspectes : {forbidden}"
        warnings.append(f"seo_pdf compliance FAIL ({len(forbidden)} pattern(s)).")
    else:
        seo["compliance_notes"] = None

    # Word count info
    full_text = " ".join([
        seo["intro"],
        " ".join(b.get("body", "") for b in seo["blocks"]),
        " ".join(f.get("a", "") for f in seo["faq"]),
    ])
    seo["word_count"] = len(re.findall(r"\b\w+\b", full_text))

    # Markdown export (pratique pour copier-coller dans Studio Éditorial)
    seo["markdown"] = _build_markdown(seo)

    return seo, warnings


def _build_markdown(seo: Dict[str, Any]) -> str:
    """Compile une version markdown de la page SEO pour copier-coller rapide."""
    lines = []
    lines.append(f"# {seo.get('h1', '')}")
    lines.append("")
    lines.append(f"_Meta title:_ {seo.get('meta_title', '')}")
    lines.append(f"_Meta description:_ {seo.get('meta_description', '')}")
    lines.append(f"_Slug:_ /guide/{seo.get('slug', '')}")
    lines.append("")
    embed = seo.get("video_embed_placeholder") or ""
    if embed:
        lines.append(embed)
        lines.append("")
    intro = seo.get("intro", "")
    if intro:
        lines.append(intro)
        lines.append("")
    for b in seo.get("blocks") or []:
        if b.get("h2"):
            lines.append(f"## {b['h2']}")
        if b.get("body"):
            lines.append(b["body"])
        lines.append("")
    faq = seo.get("faq") or []
    if faq:
        lines.append("## Questions fréquentes")
        for f in faq:
            lines.append(f"### {f.get('q', '')}")
            lines.append(f.get("a", ""))
            lines.append("")
    cta = seo.get("cta_block") or {}
    if cta.get("text") and cta.get("url_with_utm"):
        lines.append("---")
        lines.append("")
        lines.append(f"**[{cta['text']}]({cta['url_with_utm']})**")
    return "\n".join(lines).strip()


def estimate_seo_landing_cost_eur(model: str = DEFAULT_MODEL) -> float:
    """Coût supplémentaire pour 1 page SEO en plus de la vidéo."""
    if model.startswith("claude-haiku"):
        return 0.005
    if model.startswith("claude-sonnet"):
        return 0.018
    return 0.008
