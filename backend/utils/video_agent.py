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
