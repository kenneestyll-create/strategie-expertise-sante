"""Editorial Studio — IA writer routes (chirurgical, isolated module).

Garde-fous des 7 couches activés par défaut. Toggles 5 (RAG live web) et "génération
dynamique" en veille (off par défaut). Aucun coût récurrent dans l'état initial.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import os
import re
import json as json_mod
import random
import uuid

from config import db, logger
from utils.auth import get_current_admin
from utils.editorial_seed_data import SEED_LEGAL_REFS, SEED_TOPICS

router = APIRouter()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

# ==================== SEEDING (idempotent on every boot) ====================

_seeded = False


async def _ensure_seeded():
    """Upsert seed data once per process. Idempotent."""
    global _seeded
    if _seeded:
        return
    try:
        for ref in SEED_LEGAL_REFS:
            await db.editorial_legal_refs.update_one(
                {"ref_key": ref["ref_key"]}, {"$setOnInsert": ref}, upsert=True
            )
        for t in SEED_TOPICS:
            await db.editorial_topics.update_one(
                {"title": t["title"]}, {"$setOnInsert": {**t, "used": False, "created_at": datetime.now(timezone.utc).isoformat()}}, upsert=True
            )
        # Default config
        await db.editorial_config.update_one(
            {"_id": "main"},
            {"$setOnInsert": {
                "rag_live_web_enabled": False,
                "dynamic_topics_enabled": False,
                "weekly_reminder_day": "monday",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }},
            upsert=True,
        )
        _seeded = True
    except Exception as e:
        logger.error(f"[editorial] seed failed: {e}")


# ==================== MODELS ====================

class StartArticleInput(BaseModel):
    topic_id: Optional[str] = None  # if from pool
    custom_title: Optional[str] = None  # if user-provided
    category: Optional[str] = None


class GeneratePlanInput(BaseModel):
    pass


class GenerateDraftInput(BaseModel):
    pass


class SaveArticleInput(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    meta_description: Optional[str] = None
    content: Optional[str] = None  # markdown
    plan: Optional[List[dict]] = None
    terrain_notes: Optional[List[str]] = None
    faq: Optional[List[dict]] = None
    structured_content: Optional[dict] = None


class ValidateFlagInput(BaseModel):
    flag_id: str
    validated: bool


class PublishInput(BaseModel):
    pass


class PerfInput(BaseModel):
    impressions: int
    clicks: int
    avg_position: float
    period_label: str  # ex "2026-05"


class ConfigToggleInput(BaseModel):
    rag_live_web_enabled: Optional[bool] = None
    dynamic_topics_enabled: Optional[bool] = None
    weekly_reminder_day: Optional[str] = None


class LegalRefInput(BaseModel):
    ref_key: str
    kind: str
    label: str
    text: str
    source: str
    tags: List[str] = []


# ==================== HELPERS ====================

def _slugify(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[àâä]", "a", s)
    s = re.sub(r"[éèêë]", "e", s)
    s = re.sub(r"[îï]", "i", s)
    s = re.sub(r"[ôö]", "o", s)
    s = re.sub(r"[ùûü]", "u", s)
    s = re.sub(r"[ç]", "c", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80]


SYSTEM_PROMPT_PLAN = """Tu es l'éditorialiste IA de Stratégie & Expertise Santé, plateforme française d'analyse stratégique en droits santé (MDPH, AT/MP, expertise médicale, invalidité).

CONTEXTE : tu rédiges des guides SEO premium qui aident les visiteurs à comprendre leur situation et à agir. Le ton est professionnel, factuel, stratégique, jamais anxiogène.

MISSION : pour le sujet fourni, génère un PLAN COMPLET au format JSON :

{
  "h1_options": ["3 variantes de H1 SEO punchy entre 50-65 caractères"],
  "slug": "url-slug-court-pertinent",
  "meta_description": "description SEO 150-160 caractères avec call-to-action",
  "plan": [
    {"h2": "Section 1", "h3": ["sous-section 1", "sous-section 2"], "intent": "ce que la section apporte"},
    ...
  ],
  "faq": [
    {"q": "Question 1", "intent": "ce que la réponse doit clarifier"},
    ...
  ]
}

CONTRAINTES ABSOLUES :
- 5 à 7 sections H2 maximum
- 5 à 8 questions FAQ
- Aucune jurisprudence inventée, aucun chiffre fantaisiste
- Réponds UNIQUEMENT en JSON valide, AUCUN autre texte avant/après."""


SYSTEM_PROMPT_DRAFT = """Tu es l'éditorialiste IA de Stratégie & Expertise Santé. Tu rédiges UNE section d'un guide SEO juridique-santé.

RÈGLES STRICTES :
1. Ton : professionnel, premium, factuel. Jamais alarmiste, jamais commercial.
2. Aucune jurisprudence inventée — utilise UNIQUEMENT les références fournies dans le contexte. Si tu veux citer autre chose, écris "[À VÉRIFIER]" en clair.
3. Aucun chiffre précis (montants, taux, pourcentage, délais) si non fourni dans le contexte. Sinon écris "selon le barème en vigueur" ou "[À VÉRIFIER]". JAMAIS de pourcentage inventé (type « 95 % des postes »).
4. Aucun nom propre (médecin, avocat, juge).
5. Aucune donnée médicale précise (cancer, métastase, NIR).
6. Phrases courtes (15-25 mots max). Paragraphes de 2-4 phrases.
7. Format Markdown : **gras**, *italique*, listes - et 1. quand pertinent.
8. Longueur : 250-380 mots STRICT par section H2 (ne dépasse JAMAIS 400 mots — termine la section avant d'atteindre la limite de tokens).
9. FIN DE SECTION — OBLIGATOIRE :
   a) La dernière phrase doit être COMPLÈTE et se terminer par un point, un point d'exclamation ou d'interrogation.
   b) Si tu ajoutes un hook terrain, il doit être écrit EXACTEMENT au format suivant, clé en ASCII (sans accents), sur une ligne dédiée à la toute fin : `<!-- TERRAIN_HOOK: cle_ascii_en_minuscules -->`
   c) Le commentaire HTML doit être PARFAITEMENT fermé avec `-->`. Ne jamais laisser un hook ouvert.

CONNAISSANCES JURIDIQUES CRITIQUES À NE JAMAIS INVERSER :
- Silence de la MDPH pendant 2 mois sur un RAPO = REJET implicite (jamais acceptation). Réf. article R.421-2 CJA par renvoi.
- Restriction « durable » au sens RSDAE (article L.821-2 CSS) = au moins 1 an (jamais 5 ans).
- Délai RAPO MDPH = 2 mois à compter de la notification.
- Délai saisine pôle social du tribunal judiciaire = 2 mois après rejet (explicite ou implicite) du RAPO.
- IPP ≥ 10 % = rente viagère ; IPP < 10 % = capital unique.
- Délai déclaration AT par employeur = 48 heures.

Réponds UNIQUEMENT avec le contenu Markdown de la section, AUCUN autre texte."""


async def _call_claude(system_prompt: str, user_message: str, max_tokens: int = 1500) -> str:
    """Call Claude Haiku 4.5 via Anthropic SDK or Emergent LLM proxy. Returns raw text."""
    try:
        if ANTHROPIC_API_KEY:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            resp = await client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return resp.content[0].text.strip()
        else:
            import httpx
            from emergentintegrations.llm.utils import get_integration_proxy_url
            proxy_url = get_integration_proxy_url()
            url = f"{proxy_url}/llm/chat/completions"
            headers = {"Authorization": f"Bearer {EMERGENT_LLM_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "claude-haiku-4-5-20251001",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": max_tokens,
            }
            async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, connect=10.0)) as h:
                r = await h.post(url, headers=headers, json=payload)
                if r.status_code != 200:
                    raise RuntimeError(f"LLM proxy {r.status_code}: {r.text[:200]}")
                return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"[editorial] LLM call failed: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur IA : {str(e)[:120]}")


async def _scan_red_flags(text: str) -> list:
    """Detect red flags in content. Returns list of {id, type, value, context, severity}."""
    if not text:
        return []
    flags = []

    patterns = [
        # Articles de loi
        (r"\b(?:article\s+)?[LRD]\.?\s?\d{3,4}-\d+(?:-\d+)?(?:\s+(?:du\s+)?(?:CSS|CASF|CCH|CT))?", "loi", "high"),
        # Jurisprudences
        (r"Cass\.\s*[a-z]+\.?\s*(?:du\s+)?\d+(?:er|e)?\s+\w+\s+\d{4}(?:\s+n[°ºo]?\s*\d+[-.]?\d+)?", "jurisprudence", "high"),
        (r"n[°ºo]\s*\d{2}-\d{3}\.?\d{0,3}", "jurisprudence", "high"),
        # Chiffres financiers
        (r"\b\d{1,3}(?:[ \u00A0]\d{3})*(?:[,.]\d+)?\s?€", "chiffre", "high"),
        (r"\b\d+\s?%", "chiffre", "medium"),
        # Délais
        (r"\b\d+\s+(?:jour|mois|année|an|semaine)s?\b", "delai", "low"),
        # Termes médicaux sensibles
        (r"\b(?:cancer|métastase|métastases|VIH|sida|hépatite|schizophrénie|bipolaire|alzheimer|parkinson|sclérose en plaques)\b", "medical_sensitive", "high"),
        # Drapeau explicite
        (r"\[À\s*VÉRIFIER\]", "explicit_marker", "high"),
        # Noms propres (médecin/avocat/juge potentiel — heuristique simple)
        (r"\b(?:Dr|Docteur|Maître|Me|Pr|Professeur)\.?\s+[A-Z][a-zàâäéèêëîïôöùûüç]+(?:\s+[A-Z][a-zàâäéèêëîïôöùûüç]+)?", "nom_propre", "high"),
    ]

    for pat, kind, severity in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            value = m.group(0)
            start = max(0, m.start() - 40)
            end = min(len(text), m.end() + 40)
            context = text[start:end].replace("\n", " ")
            flags.append({
                "id": str(uuid.uuid4())[:8],
                "type": kind,
                "value": value.strip(),
                "context": context.strip(),
                "severity": severity,
                "validated": False,
            })

    # Dedupe by (type, value)
    seen = set()
    unique = []
    for f in flags:
        k = (f["type"], f["value"].lower())
        if k not in seen:
            seen.add(k)
            unique.append(f)
    return unique[:60]  # safety cap


# ==================== ENDPOINTS — TOPICS POOL ====================

@router.get("/admin/editorial/topics/proposals")
async def get_topic_proposals(count: int = 3, admin: dict = Depends(get_current_admin)):
    """Return N random unused topics from the pool. Default N=3."""
    await _ensure_seeded()
    available = await db.editorial_topics.find({"used": False}, {"_id": 0}).to_list(200)
    if len(available) <= count:
        return {"proposals": available, "exhausted": True, "remaining": len(available)}
    return {"proposals": random.sample(available, count), "exhausted": False, "remaining": len(available)}


@router.get("/admin/editorial/topics/all")
async def list_all_topics(admin: dict = Depends(get_current_admin)):
    """Full pool, including used ones."""
    await _ensure_seeded()
    topics = await db.editorial_topics.find({}, {"_id": 0}).sort("used", 1).to_list(500)
    return {"topics": topics, "total": len(topics), "used_count": sum(1 for t in topics if t.get("used"))}


# ==================== ENDPOINTS — ARTICLES ====================

@router.post("/admin/editorial/articles/start")
async def start_article(input_data: StartArticleInput, admin: dict = Depends(get_current_admin)):
    """Create a draft from a pool topic OR a custom title."""
    await _ensure_seeded()
    actor = admin.get("sub") or admin.get("email") or "admin"

    if input_data.topic_id:
        topic = await db.editorial_topics.find_one({"title": input_data.topic_id}, {"_id": 0})
        if not topic:
            raise HTTPException(status_code=404, detail="Sujet inconnu")
        title = topic["title"]
        category = topic.get("category", "")
        angle = topic.get("angle", "")
        # Mark topic as used
        await db.editorial_topics.update_one({"title": title}, {"$set": {"used": True, "used_at": datetime.now(timezone.utc).isoformat()}})
    elif input_data.custom_title and input_data.custom_title.strip():
        title = input_data.custom_title.strip()
        category = input_data.category or "perso"
        angle = "Sujet personnel."
    else:
        raise HTTPException(status_code=400, detail="Fournissez un topic_id OU un custom_title")

    article_id = str(uuid.uuid4())
    doc = {
        "id": article_id,
        "title": title,
        "category": category,
        "angle": angle,
        "slug": _slugify(title),
        "meta_description": "",
        "content": "",
        "plan": [],
        "faq": [],
        "terrain_notes": [],
        "red_flags": [],
        "status": "draft",  # draft | ready | published | archived
        "versions": [],
        "perf": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": actor,
        "published_at": None,
        "last_revalidated_at": None,
    }
    await db.editorial_articles.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/admin/editorial/articles")
async def list_articles(
    status: Optional[str] = None,
    admin: dict = Depends(get_current_admin),
):
    """List articles, optionally filtered by status."""
    q = {}
    if status:
        q["status"] = status
    items = await db.editorial_articles.find(q, {"_id": 0}).sort("updated_at", -1).limit(200).to_list(200)
    return {"items": items, "total": len(items)}


@router.get("/admin/editorial/articles/{article_id}")
async def get_article(article_id: str, admin: dict = Depends(get_current_admin)):
    art = await db.editorial_articles.find_one({"id": article_id}, {"_id": 0})
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return art


@router.post("/admin/editorial/articles/{article_id}/generate-plan")
async def generate_plan(article_id: str, admin: dict = Depends(get_current_admin)):
    """Step 2 — IA generates plan, FAQ, slug, meta-description."""
    art = await db.editorial_articles.find_one({"id": article_id}, {"_id": 0})
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")

    user_msg = (
        f"SUJET : {art['title']}\n"
        f"CATÉGORIE : {art.get('category')}\n"
        f"ANGLE STRATÉGIQUE : {art.get('angle')}\n\n"
        "Génère le plan complet."
    )
    raw = await _call_claude(SYSTEM_PROMPT_PLAN, user_msg, max_tokens=3000)
    # Strip optional markdown code fences (``` or ```json) — single-line patterns, not multiline
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        # remove first fence line
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        # remove trailing fence
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    cleaned = cleaned.strip()
    try:
        parsed = json_mod.loads(cleaned)
    except Exception as e:
        logger.error(f"[editorial] plan JSON parse failed: {e} | raw[:200]={raw[:200]}")
        raise HTTPException(status_code=500, detail="Plan IA non parsable, réessayez.")

    update = {
        "plan": parsed.get("plan", []),
        "faq": parsed.get("faq", []),
        "h1_options": parsed.get("h1_options", []),
        "slug": parsed.get("slug") or _slugify(art["title"]),
        "meta_description": parsed.get("meta_description", ""),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.editorial_articles.update_one({"id": article_id}, {"$set": update})
    return {"success": True, **update}


@router.post("/admin/editorial/articles/{article_id}/generate-draft")
async def generate_draft(article_id: str, admin: dict = Depends(get_current_admin)):
    """Step 3 — IA generates section-by-section content based on the plan."""
    art = await db.editorial_articles.find_one({"id": article_id}, {"_id": 0})
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")
    if not art.get("plan"):
        raise HTTPException(status_code=400, detail="Générez d'abord le plan")

    # Pull legal refs to include in context
    legal_refs = await db.editorial_legal_refs.find({}, {"_id": 0}).limit(80).to_list(80)
    refs_text = "\n".join(f"- {r['label']}: {r['text']}" for r in legal_refs[:30])

    sections_md = []
    # Parallelize to keep total < 30s even with 7 sections
    import asyncio as _asyncio
    section_tasks = []
    for idx, section in enumerate(art["plan"]):
        h2 = section.get("h2", f"Section {idx+1}")
        intent = section.get("intent", "")
        h3_list = section.get("h3", [])
        section_prompt = (
            f"SUJET GLOBAL : {art['title']}\n"
            f"CATÉGORIE : {art.get('category')}\n"
            f"SECTION ACTUELLE : {h2}\n"
            f"OBJECTIF DE LA SECTION : {intent}\n"
            f"SOUS-SECTIONS H3 (si pertinentes) : {', '.join(h3_list) if h3_list else '(libre)'}\n\n"
            f"RÉFÉRENCES LÉGALES VÉRIFIÉES DISPONIBLES :\n{refs_text}\n\n"
            f"Rédige la section au format Markdown (commence par `## {h2}`). "
            f"IMPÉRATIF : termine la section par une phrase complète se finissant par un point, "
            f"puis (si pertinent) un hook terrain formaté `<!-- TERRAIN_HOOK: cle_ascii -->` parfaitement fermé."
        )
        section_tasks.append(_call_claude(SYSTEM_PROMPT_DRAFT, section_prompt, max_tokens=1400))

    results = await _asyncio.gather(*section_tasks, return_exceptions=True)

    # Patch (c) — post-check + auto-retry of faulty sections
    def _section_is_faulty(md: str) -> str | None:
        """Return a short reason string if the section looks broken, else None."""
        if not md or len(md.strip()) < 60:
            return "section trop courte"
        stripped = md.rstrip()
        # Unclosed terrain hook
        if "<!-- TERRAIN_HOOK:" in stripped and not re.search(r"<!--\s*TERRAIN_HOOK:[^>]*-->", stripped):
            return "hook terrain non fermé"
        # Non-ASCII key inside hook
        for m in re.finditer(r"<!--\s*TERRAIN_HOOK:\s*([^\s>]+)\s*-->", stripped):
            key = m.group(1)
            if not re.fullmatch(r"[a-z0-9_]+", key):
                return f"clé hook non-ASCII ({key})"
        # Final character must be punctuation or a closed hook
        # Strip trailing hook to inspect the last content character
        tail_stripped = re.sub(r"<!--\s*TERRAIN_HOOK:[^>]*-->\s*$", "", stripped).rstrip()
        if tail_stripped and tail_stripped[-1] not in ".!?»)\"":
            return f"fin abrupte (‘…{tail_stripped[-40:]}’)"
        return None

    async def _retry_section(idx: int) -> str:
        section = art["plan"][idx]
        h2 = section.get("h2", f"Section {idx+1}")
        intent = section.get("intent", "")
        h3_list = section.get("h3", [])
        retry_prompt = (
            f"SUJET GLOBAL : {art['title']}\n"
            f"SECTION : {h2}\n"
            f"OBJECTIF : {intent}\n"
            f"SOUS-SECTIONS : {', '.join(h3_list) if h3_list else '(libre)'}\n\n"
            f"RÉFÉRENCES LÉGALES :\n{refs_text}\n\n"
            f"RETRY — la précédente tentative était invalide (tronquée ou hook mal formé). "
            f"Rédige une section CONCISE (260-320 mots) au format Markdown, commence par `## {h2}`, "
            f"termine par une phrase complète + point final, puis un unique hook `<!-- TERRAIN_HOOK: cle_ascii -->` "
            f"parfaitement fermé si pertinent. Reste STRICTEMENT sous 320 mots."
        )
        return await _call_claude(SYSTEM_PROMPT_DRAFT, retry_prompt, max_tokens=1400)

    faulty_indices: list[int] = []
    initial_md: list[str] = []
    for idx, r in enumerate(results):
        if isinstance(r, Exception):
            faulty_indices.append(idx)
            initial_md.append("")
        else:
            reason = _section_is_faulty(r)
            if reason:
                faulty_indices.append(idx)
                logger.info(f"[editorial] section {idx} flagged for retry: {reason}")
            initial_md.append(r)

    if faulty_indices:
        retries = await _asyncio.gather(*[_retry_section(i) for i in faulty_indices], return_exceptions=True)
        for pos, idx in enumerate(faulty_indices):
            r = retries[pos]
            if isinstance(r, Exception) or _section_is_faulty(r):
                h2 = art["plan"][idx].get("h2", f"Section {idx+1}")
                fallback_reason = r if isinstance(r, Exception) else _section_is_faulty(r)
                logger.warning(f"[editorial] section {h2} retry still faulty: {fallback_reason}")
                initial_md[idx] = f"## {h2}\n\n*[Section à rédiger — l'IA a rencontré une erreur, relancez ou rédigez manuellement]*"
            else:
                initial_md[idx] = r

    sections_md = initial_md

    # Add FAQ section
    if art.get("faq"):
        faq_md = "## FAQ\n\n"
        for q in art["faq"]:
            faq_md += f"### {q.get('q', '')}\n\n*[Réponse à compléter — intent : {q.get('intent', '')}]*\n\n"
        sections_md.append(faq_md)

    full_md = "\n\n".join(sections_md)
    red_flags = await _scan_red_flags(full_md)
    update = {
        "content": full_md,
        "red_flags": red_flags,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.editorial_articles.update_one({"id": article_id}, {"$set": update})
    return {"success": True, "content": full_md, "red_flags": red_flags}


@router.post("/admin/editorial/articles/{article_id}/save")
async def save_article(article_id: str, input_data: SaveArticleInput, admin: dict = Depends(get_current_admin)):
    """Save edits + rescan red flags + version snapshot."""
    art = await db.editorial_articles.find_one({"id": article_id}, {"_id": 0})
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")

    update = {}
    fields = ["title", "slug", "meta_description", "content", "plan", "terrain_notes", "faq", "structured_content"]
    for f in fields:
        v = getattr(input_data, f, None)
        if v is not None:
            update[f] = v

    if "content" in update:
        update["red_flags"] = await _scan_red_flags(update["content"])
    update["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Version snapshot (lightweight — last 10 only)
    await db.editorial_articles.update_one(
        {"id": article_id},
        {
            "$set": update,
            "$push": {"versions": {"$each": [{"snapshot_at": update["updated_at"], "content_len": len(update.get("content", art.get("content", "")) or "")}], "$slice": -10}},
        },
    )
    return {"success": True, **update}


@router.post("/admin/editorial/articles/{article_id}/validate-flag")
async def validate_flag(article_id: str, input_data: ValidateFlagInput, admin: dict = Depends(get_current_admin)):
    art = await db.editorial_articles.find_one({"id": article_id}, {"_id": 0})
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")
    flags = art.get("red_flags", [])
    found = False
    for f in flags:
        if f.get("id") == input_data.flag_id:
            f["validated"] = bool(input_data.validated)
            f["validated_at"] = datetime.now(timezone.utc).isoformat()
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Drapeau introuvable")
    await db.editorial_articles.update_one(
        {"id": article_id},
        {"$set": {"red_flags": flags, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    all_validated = all(f.get("validated") for f in flags)
    return {"success": True, "all_validated": all_validated, "remaining": sum(1 for f in flags if not f.get("validated"))}


@router.post("/admin/editorial/articles/{article_id}/publish")
async def publish_article(article_id: str, admin: dict = Depends(get_current_admin)):
    art = await db.editorial_articles.find_one({"id": article_id}, {"_id": 0})
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")
    if not art.get("content") or not art.get("title"):
        raise HTTPException(status_code=400, detail="Titre et contenu requis")

    flags = art.get("red_flags", [])
    if any(not f.get("validated") for f in flags):
        not_val = [f["value"] for f in flags if not f.get("validated")]
        raise HTTPException(
            status_code=400,
            detail=f"{len(not_val)} drapeau(x) non validé(s). Valider tous les éléments avant publication.",
        )

    now = datetime.now(timezone.utc).isoformat()
    update = {"status": "published", "published_at": now, "last_revalidated_at": now, "updated_at": now}
    await db.editorial_articles.update_one({"id": article_id}, {"$set": update})

    # Patch (e) — bridge to public seo_pages collection so the article is actually rendered on /guide/{slug}
    slug = art.get("slug") or _slugify(art["title"])
    structured = art.get("structured_content")

    if structured:
        # Phase 2 — use structured fields for pixel-perfect rendering identical to manual articles
        seo_content = {
            "reponse_rapide_titre": structured.get("reponse_rapide_titre", ""),
            "reponse_rapide": structured.get("reponse_rapide", ""),
            "contexte": structured.get("contexte", ""),
            "limites": structured.get("limites", ""),
            "blocages": structured.get("blocages", []),
            "erreurs": structured.get("erreurs", []),
            "strategie": structured.get("strategie", ""),
            "orientation": structured.get("orientation", []),
            "reassurance": structured.get("reassurance", ""),
            "maillage": structured.get("maillage", []),
            "faq": structured.get("faq", []),
        }
    else:
        # Fallback — markdown body rendering (still usable but not pixel-perfect)
        faq_payload = []
        for q in (art.get("faq") or []):
            faq_payload.append({
                "question": q.get("q") or q.get("question", ""),
                "answer": q.get("answer") or q.get("a") or "",
            })
        seo_content = {
            "markdown_body": art.get("content", ""),
            "faq": faq_payload,
        }
        if art.get("terrain_notes"):
            seo_content["terrain_notes"] = art["terrain_notes"]

    existing_seo = await db.seo_pages.find_one({"slug": slug}, {"_id": 0, "id": 1, "views": 1, "cta_clicks": 1, "conversions": 1, "revenue": 1, "created_at": 1})
    seo_doc = {
        "slug": slug,
        "title": art.get("title", ""),
        "meta_description": art.get("meta_description", ""),
        "category": art.get("category", ""),
        "intention": "",
        "priority": "p1",
        "cta_type": "dossier_express",
        "cta_label": "Analyser mon dossier maintenant",
        "active": True,
        "content": seo_content,
        "updated_at": now,
        "source": "editorial_studio",
        "editorial_article_id": art.get("id"),
    }
    if existing_seo:
        # Preserve analytics counters + created_at
        for k in ("views", "cta_clicks", "conversions", "revenue", "created_at", "id"):
            if existing_seo.get(k) is not None:
                seo_doc[k] = existing_seo[k]
        await db.seo_pages.update_one({"slug": slug}, {"$set": seo_doc})
    else:
        seo_doc["id"] = str(uuid.uuid4())
        seo_doc["views"] = 0
        seo_doc["cta_clicks"] = 0
        seo_doc["conversions"] = 0
        seo_doc["revenue"] = 0
        seo_doc["created_at"] = now
        await db.seo_pages.insert_one(seo_doc)

    return {"success": True, "published_at": now, "url": f"/guide/{slug}"}


@router.delete("/admin/editorial/articles/{article_id}")
async def delete_article(article_id: str, hard: bool = False, admin: dict = Depends(get_current_admin)):
    """Delete an article. ?hard=true → permanent removal + topic restored to pool.
    Default (?hard=false) → soft archive (status=archived) + topic restored to pool.
    """
    art = await db.editorial_articles.find_one({"id": article_id}, {"_id": 0})
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")

    # Restore topic to pool (if the draft was based on a seed topic)
    if art.get("title"):
        topic = await db.editorial_topics.find_one({"title": art["title"]}, {"_id": 0})
        if topic:
            await db.editorial_topics.update_one(
                {"title": art["title"]},
                {"$set": {"used": False}, "$unset": {"used_at": ""}},
            )

    if hard:
        await db.editorial_articles.delete_one({"id": article_id})
        return {"success": True, "deleted": "hard", "topic_restored": True}

    await db.editorial_articles.update_one(
        {"id": article_id},
        {"$set": {"status": "archived", "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"success": True, "deleted": "soft", "topic_restored": True}


# ==================== STRUCTURED OUTPUT (Phase 2) ====================

class StructureInput(BaseModel):
    pass


SYSTEM_PROMPT_STRUCTURE = """Tu es l'éditorialiste IA de Stratégie & Expertise Santé.

MISSION : à partir d'un brouillon markdown, produire un OBJET JSON STRUCTURÉ aligné sur le format de publication SEO de la plateforme.

Schéma JSON STRICT à respecter (toutes les clés sont obligatoires, valeurs non vides) :
{
  "reponse_rapide_titre": "Titre court de la réponse rapide (12-15 mots)",
  "reponse_rapide": "Paragraphe synthétique 4-7 phrases répondant à la question principale, avec article de loi clé et délai si pertinent",
  "contexte": "1 ou 2 paragraphes de mise en contexte juridique et stratégique (rattachés au cas du visiteur)",
  "limites": "1 paragraphe expliquant ce que les sites institutionnels n'expliquent pas (angle morts, lacunes documentaires)",
  "blocages": ["Point de blocage 1 — phrase 1-2", "Point 2", "Point 3", "Point 4", "Point 5"],
  "erreurs": ["Erreur fréquente 1", "Erreur 2", "Erreur 3", "Erreur 4", "Erreur 5"],
  "strategie": "1 long paragraphe stratégique synthétisant l'approche recommandée (avec piliers ou méthode si pertinent)",
  "orientation": ["Action 1 datée et concrète", "Action 2", "Action 3", "Action 4", "Action 5"],
  "reassurance": "1 paragraphe de réassurance non commercial (pas de promesse, pas de garantie)",
  "maillage": [
    {"slug": "guide-existant-1", "text": "Titre humain 1"},
    {"slug": "guide-existant-2", "text": "Titre humain 2"},
    {"slug": "guide-existant-3", "text": "Titre humain 3"}
  ],
  "faq": [
    {"question": "Question 1 ?", "answer": "Réponse complète, 3-6 phrases, avec article de loi si pertinent"},
    {"question": "Q2 ?", "answer": "..."},
    ... 6 à 8 FAQ
  ]
}

RÈGLES :
1. Aucune jurisprudence inventée. N'utilise que les références déjà présentes dans le brouillon.
2. Aucun chiffre/pourcentage non sourcé. Si un % apparaît dans le brouillon, le conserver tel quel ou le retirer si suspect.
3. Préserver le ton premium, factuel, non-commercial.
4. Les `blocages` et `erreurs` doivent être 5 items chacun (pas plus, pas moins).
5. `orientation` : exactement 5 actions, ton actionnable.
6. `faq` : 6 à 8 questions ; les réponses ne doivent jamais contenir « selon nous », « probablement » → toujours factuel.
7. `maillage` : 3 slugs internes pertinents en lien avec le sujet (à partir des suggestions du brouillon ou inférés).
8. Réponds UNIQUEMENT en JSON valide, AUCUN texte avant/après. Échappe correctement les guillemets internes."""


@router.post("/admin/editorial/articles/{article_id}/structure")
async def structure_article(article_id: str, _: StructureInput = None, admin: dict = Depends(get_current_admin)):
    """Phase 2: Transform markdown draft into structured fields aligned with seo_pages schema.

    Stores result in `structured_content` field of the article (does NOT replace `content`).
    """
    art = await db.editorial_articles.find_one({"id": article_id}, {"_id": 0})
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")
    if not art.get("content"):
        raise HTTPException(status_code=400, detail="Aucun brouillon markdown à structurer. Générez d'abord le brouillon.")

    # Strip TERRAIN_HOOK comments before structuring (they're editorial placeholders)
    cleaned_md = re.sub(r"<!--\s*TERRAIN_HOOK:[^>]*-->", "", art["content"])

    user_prompt = (
        f"SUJET : {art['title']}\n"
        f"CATÉGORIE : {art.get('category', '')}\n"
        f"SLUG CIBLE : {art.get('slug', '')}\n\n"
        f"BROUILLON MARKDOWN À TRANSFORMER :\n\n{cleaned_md}\n\n"
        f"Produis maintenant l'objet JSON structuré selon le schéma."
    )

    try:
        raw = await _call_claude(SYSTEM_PROMPT_STRUCTURE, user_prompt, max_tokens=4500)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"IA indisponible : {e}")

    # Robust JSON extraction
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    structured = None
    try:
        structured = json_mod.loads(raw)
    except Exception:
        # Try first {...} block
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                structured = json_mod.loads(m.group(0))
            except Exception:
                structured = None

    # Last-resort tolerant parser for typical AI JSON glitches (trailing commas, missing
    # commas between items, single quotes, unescaped newlines). Standard library cannot.
    if structured is None:
        try:
            from json_repair import repair_json
            repaired = repair_json(raw, return_objects=True)
            if isinstance(repaired, dict):
                structured = repaired
            elif isinstance(repaired, str):
                structured = json_mod.loads(repaired)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"JSON IA non-récupérable : {e}")

    if structured is None:
        raise HTTPException(status_code=500, detail="JSON IA non-récupérable.")

    # Lightweight schema validation (non-blocking but informative)
    required_keys = ["reponse_rapide_titre", "reponse_rapide", "contexte", "limites",
                     "blocages", "erreurs", "strategie", "orientation", "reassurance", "maillage", "faq"]
    missing = [k for k in required_keys if k not in structured]
    if missing:
        logger.warning(f"[editorial.structure] missing keys: {missing}")

    now = datetime.now(timezone.utc).isoformat()
    await db.editorial_articles.update_one(
        {"id": article_id},
        {"$set": {"structured_content": structured, "structured_at": now, "updated_at": now}},
    )
    return {"success": True, "structured_content": structured, "missing_keys": missing}


# ==================== MIGRATE TO SEED (Phase 3) ====================

class MigrateInput(BaseModel):
    cta_type: Optional[str] = "dossier_express"
    cta_label: Optional[str] = "Analyser mon dossier maintenant"
    intention: Optional[str] = ""
    priority: Optional[str] = "p1"


_SEED_FILE = "/app/backend/seed_seo_pages.py"
_SEED_INSERT_MARKER = "]\n\nasync def seed():"


@router.post("/admin/editorial/articles/{article_id}/migrate-to-seed")
async def migrate_to_seed(article_id: str, input_data: MigrateInput, admin: dict = Depends(get_current_admin)):
    """Phase 3: Append the structured article into seed_seo_pages.py PAGES list.

    The user must then click 'Save to GitHub' + 'Deploy' to push to production.
    The manual seed method remains active (idempotent — never overwrites).
    """
    art = await db.editorial_articles.find_one({"id": article_id}, {"_id": 0})
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")

    structured = art.get("structured_content")
    if not structured:
        raise HTTPException(status_code=400, detail="Aucun contenu structuré. Lancez d'abord 'Structurer pour publication'.")

    flags = art.get("red_flags", [])
    if any(not f.get("validated") for f in flags):
        raise HTTPException(status_code=400, detail="Validez tous les drapeaux avant de migrer.")

    slug = art.get("slug") or _slugify(art.get("title", ""))
    title = art.get("title", "").replace('"', '\\"')
    meta = art.get("meta_description", "").replace('"', '\\"')
    category = art.get("category", "") or "general"

    # Read seed file
    if not os.path.isfile(_SEED_FILE):
        raise HTTPException(status_code=500, detail=f"Fichier seed introuvable : {_SEED_FILE}")

    with open(_SEED_FILE, "r", encoding="utf-8") as f:
        seed_text = f.read()

    # Check if slug already in seed
    if f'"slug": "{slug}"' in seed_text:
        raise HTTPException(status_code=409, detail=f"Le slug '{slug}' est déjà présent dans le seed. Modifiez le slug ou retirez l'ancienne version.")

    # Build the Python entry as a JSON-like string (safe via repr-like serialization)
    def _py(s):
        if s is None:
            return '""'
        return json_mod.dumps(s, ensure_ascii=False)

    blocages_lines = ",\n            ".join(_py(b) for b in (structured.get("blocages") or []))
    erreurs_lines = ",\n            ".join(_py(e) for e in (structured.get("erreurs") or []))
    orientation_lines = ",\n            ".join(_py(o) for o in (structured.get("orientation") or []))
    maillage_items = ",\n            ".join(
        '{"slug": ' + _py(m.get("slug", "")) + ', "text": ' + _py(m.get("text", "")) + '}'
        for m in (structured.get("maillage") or [])
    )
    faq_items = ",\n            ".join(
        '{"question": ' + _py(q.get("question", "")) + ', "answer": ' + _py(q.get("answer", "")) + '}'
        for q in (structured.get("faq") or [])
    )

    block = f'''{{
    "slug": "{slug}",
    "title": {_py(title)},
    "meta_description": {_py(meta)},
    "category": "{category}",
    "intention": "{input_data.intention or ''}",
    "priority": "{input_data.priority or 'p1'}",
    "cta_type": "{input_data.cta_type or 'dossier_express'}",
    "cta_label": "{(input_data.cta_label or 'Analyser mon dossier maintenant').replace(chr(34), chr(92)+chr(34))}",
    "content": {{
        "reponse_rapide_titre": {_py(structured.get("reponse_rapide_titre", ""))},
        "reponse_rapide": {_py(structured.get("reponse_rapide", ""))},
        "contexte": {_py(structured.get("contexte", ""))},
        "limites": {_py(structured.get("limites", ""))},
        "blocages": [
            {blocages_lines}
        ],
        "erreurs": [
            {erreurs_lines}
        ],
        "strategie": {_py(structured.get("strategie", ""))},
        "orientation": [
            {orientation_lines}
        ],
        "reassurance": {_py(structured.get("reassurance", ""))},
        "maillage": [
            {maillage_items}
        ],
        "faq": [
            {faq_items}
        ]
    }},
}},
'''

    if _SEED_INSERT_MARKER not in seed_text:
        raise HTTPException(status_code=500, detail="Marqueur d'insertion introuvable dans le seed (fichier modifié manuellement ?)")

    new_text = seed_text.replace(_SEED_INSERT_MARKER, block + _SEED_INSERT_MARKER, 1)

    with open(_SEED_FILE, "w", encoding="utf-8") as f:
        f.write(new_text)

    # Mark article migrated
    await db.editorial_articles.update_one(
        {"id": article_id},
        {"$set": {
            "migrated_to_seed": True,
            "migrated_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
    )

    return {
        "success": True,
        "slug": slug,
        "next_steps": [
            "Cliquez sur 'Save to GitHub' dans Emergent",
            "Cliquez ensuite sur 'Deploy' pour pousser en production",
            f"L'article sera live à https://strategie-expertise-sante.fr/guide/{slug} après ~30 secondes",
        ],
    }


# ==================== ENDPOINTS — PERFORMANCE (manual SC entry) ====================

@router.post("/admin/editorial/articles/{article_id}/perf")
async def add_perf_entry(article_id: str, input_data: PerfInput, admin: dict = Depends(get_current_admin)):
    art = await db.editorial_articles.find_one({"id": article_id}, {"_id": 0})
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")
    entry = {
        "period_label": input_data.period_label,
        "impressions": input_data.impressions,
        "clicks": input_data.clicks,
        "ctr": round((input_data.clicks / input_data.impressions * 100), 2) if input_data.impressions else 0,
        "avg_position": input_data.avg_position,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    # Replace if same period_label exists
    perf = art.get("perf", [])
    perf = [p for p in perf if p.get("period_label") != input_data.period_label]
    perf.append(entry)
    perf.sort(key=lambda p: p.get("period_label", ""))
    await db.editorial_articles.update_one({"id": article_id}, {"$set": {"perf": perf}})
    return {"success": True, "perf": perf}


# ==================== ENDPOINTS — REVALIDATION 6 MOIS ====================

@router.get("/admin/editorial/needs-revalidation")
async def needs_revalidation(admin: dict = Depends(get_current_admin)):
    """List articles published > 6 months ago and not revalidated."""
    six_months_ago = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()
    items = await db.editorial_articles.find(
        {
            "status": "published",
            "$or": [
                {"last_revalidated_at": {"$lt": six_months_ago}},
                {"last_revalidated_at": None},
            ],
        },
        {"_id": 0, "id": 1, "title": 1, "published_at": 1, "last_revalidated_at": 1, "slug": 1},
    ).to_list(100)
    return {"items": items, "count": len(items)}


@router.post("/admin/editorial/articles/{article_id}/revalidate")
async def revalidate(article_id: str, admin: dict = Depends(get_current_admin)):
    res = await db.editorial_articles.update_one(
        {"id": article_id}, {"$set": {"last_revalidated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return {"success": True}


# ==================== ENDPOINTS — LEGAL REFS ====================

@router.get("/admin/editorial/legal-refs")
async def list_legal_refs(admin: dict = Depends(get_current_admin)):
    await _ensure_seeded()
    items = await db.editorial_legal_refs.find({}, {"_id": 0}).sort("kind", 1).to_list(500)
    return {"items": items, "total": len(items)}


@router.post("/admin/editorial/legal-refs")
async def add_legal_ref(input_data: LegalRefInput, admin: dict = Depends(get_current_admin)):
    now = datetime.now(timezone.utc).isoformat()
    await db.editorial_legal_refs.update_one(
        {"ref_key": input_data.ref_key},
        {"$set": {**input_data.model_dump(), "last_verified": now}},
        upsert=True,
    )
    return {"success": True}


# ==================== ENDPOINTS — CONFIG / TOGGLES ====================

@router.get("/admin/editorial/config")
async def get_config(admin: dict = Depends(get_current_admin)):
    await _ensure_seeded()
    cfg = await db.editorial_config.find_one({"_id": "main"})
    if not cfg:
        return {"rag_live_web_enabled": False, "dynamic_topics_enabled": False, "weekly_reminder_day": "monday"}
    cfg.pop("_id", None)
    return cfg


@router.post("/admin/editorial/config")
async def update_config(input_data: ConfigToggleInput, admin: dict = Depends(get_current_admin)):
    update = {k: v for k, v in input_data.model_dump().items() if v is not None}
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.editorial_config.update_one({"_id": "main"}, {"$set": update}, upsert=True)
    return {"success": True, **update}


# ==================== ENDPOINTS — STATS / DASHBOARD ====================

@router.get("/admin/editorial/stats")
async def stats(admin: dict = Depends(get_current_admin)):
    """Quick overview for the calendar/dashboard widget."""
    await _ensure_seeded()
    total = await db.editorial_articles.count_documents({})
    drafts = await db.editorial_articles.count_documents({"status": "draft"})
    published = await db.editorial_articles.count_documents({"status": "published"})
    archived = await db.editorial_articles.count_documents({"status": "archived"})

    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    published_last_7d = await db.editorial_articles.count_documents(
        {"status": "published", "published_at": {"$gte": seven_days_ago}}
    )

    pool_total = await db.editorial_topics.count_documents({})
    pool_used = await db.editorial_topics.count_documents({"used": True})
    pool_available = pool_total - pool_used

    six_months_ago = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()
    needs_reval = await db.editorial_articles.count_documents(
        {"status": "published", "$or": [{"last_revalidated_at": {"$lt": six_months_ago}}, {"last_revalidated_at": None}]}
    )

    refs_total = await db.editorial_legal_refs.count_documents({})

    return {
        "articles": {"total": total, "drafts": drafts, "published": published, "archived": archived, "published_last_7d": published_last_7d},
        "topics_pool": {"total": pool_total, "used": pool_used, "available": pool_available},
        "needs_revalidation": needs_reval,
        "legal_refs_count": refs_total,
        "weekly_reminder_due": published_last_7d == 0,  # true if no article this week → show reminder
    }
