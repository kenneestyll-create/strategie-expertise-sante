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
3. Aucun chiffre précis (montants, taux, délais) si non fourni. Sinon écris "selon le barème en vigueur" ou "[À VÉRIFIER]".
4. Aucun nom propre (médecin, avocat, juge).
5. Aucune donnée médicale précise (cancer, métastase, NIR).
6. Phrases courtes (15-25 mots max). Paragraphes de 2-4 phrases.
7. Format Markdown : **gras**, *italique*, listes - et 1. quand pertinent.
8. Longueur : 200-400 mots par section H2.
9. SI une section pourrait bénéficier d'un cas terrain, ajoute en fin de section : `<!-- TERRAIN_HOOK: [thème] -->` (sera remplacé par l'utilisateur).

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
            f"Rédige la section au format Markdown (commence par `## {h2}`)."
        )
        section_tasks.append(_call_claude(SYSTEM_PROMPT_DRAFT, section_prompt, max_tokens=900))

    results = await _asyncio.gather(*section_tasks, return_exceptions=True)
    for idx, r in enumerate(results):
        if isinstance(r, Exception):
            h2 = art["plan"][idx].get("h2", f"Section {idx+1}")
            logger.warning(f"[editorial] section {h2} failed: {r}")
            sections_md.append(f"## {h2}\n\n*[Section à rédiger — l'IA a rencontré une erreur, relancez ou rédigez manuellement]*")
        else:
            sections_md.append(r)

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
    fields = ["title", "slug", "meta_description", "content", "plan", "terrain_notes", "faq"]
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
    return {"success": True, "published_at": now, "url": f"/guide/{art.get('slug')}"}


@router.delete("/admin/editorial/articles/{article_id}")
async def archive_article(article_id: str, admin: dict = Depends(get_current_admin)):
    """Soft-delete (archive)."""
    res = await db.editorial_articles.update_one(
        {"id": article_id}, {"$set": {"status": "archived", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return {"success": True}


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
