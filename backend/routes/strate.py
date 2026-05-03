"""Straté · Conciergerie IA — structured reception agent.

Dedicated router with deterministic 3-step flow + free-text intent detection
for the "Autre situation" branch. Tracks every event in `strate_sessions`
for the admin KPIs. Admin kill switch stored in `strate_config` single doc.

Never touches the frozen /app/backend/utils/chatbot.py nor chatbot_sessions.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import os
import json as json_mod
import uuid
import re

from config import db, logger
from utils.auth import get_current_admin
from utils.strate_prompts import (
    GREETING, RGPD_BANNER, ROOT_OPTIONS, QUALIFICATION, CTA_MAP, EXPERT_CTA,
    FREE_TEXT_SYSTEM_PROMPT, FREE_TEXT_FALLBACK, contains_sensitive_data,
)

router = APIRouter()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

MAX_WORDS_PER_MESSAGE = 60  # hard limit


# ==================== MODELS ====================

class StrateChatInput(BaseModel):
    session_id: Optional[str] = None
    step: str = Field(..., description="greeting | qualify | route | free_text | confirm")
    category_id: Optional[str] = None       # chosen at step 1
    qualification_id: Optional[str] = None  # chosen at step 2
    text: Optional[str] = None              # free-text (step 'free_text')
    page: Optional[str] = None              # current page path (for tracking)


class StrateToggleInput(BaseModel):
    enabled: bool


class StrateConfig(BaseModel):
    enabled: bool = True
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None


# ==================== CONFIG / KILL SWITCH ====================

async def _get_config() -> dict:
    doc = await db.strate_config.find_one({"_id": "main"})
    if not doc:
        return {"enabled": True}
    return {"enabled": doc.get("enabled", True), "updated_at": doc.get("updated_at"), "updated_by": doc.get("updated_by")}


@router.get("/strate/config")
async def get_strate_public_config():
    """Public endpoint — frontend checks if Straté should be active at all."""
    cfg = await _get_config()
    return {"enabled": cfg.get("enabled", True)}


@router.post("/admin/strate/toggle")
async def admin_toggle_strate(input_data: StrateToggleInput, admin: dict = Depends(get_current_admin)):
    now = datetime.now(timezone.utc).isoformat()
    actor = admin.get("sub") or admin.get("email") or "admin"
    await db.strate_config.update_one(
        {"_id": "main"},
        {"$set": {"enabled": bool(input_data.enabled), "updated_at": now, "updated_by": actor}},
        upsert=True,
    )
    return {"success": True, "enabled": bool(input_data.enabled), "updated_at": now}


@router.get("/admin/strate/config")
async def admin_get_strate_config(admin: dict = Depends(get_current_admin)):
    return await _get_config()


# ==================== SESSIONS / TRACKING ====================

async def _track_event(session_id: str, event_type: str, payload: Optional[dict] = None, page: Optional[str] = None):
    """Append-only event log + upsert session summary."""
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "session_id": session_id,
        "event": event_type,
        "payload": payload or {},
        "page": page,
        "created_at": now,
    }
    await db.strate_events.insert_one(doc)

    # Update session summary
    update = {"$set": {"last_event": event_type, "last_at": now, "last_page": page},
              "$setOnInsert": {"session_id": session_id, "created_at": now}}
    if event_type == "open":
        update["$set"]["opened"] = True
    if event_type == "qualify":
        update["$set"]["qualified"] = True
    if event_type == "route_click":
        update["$set"]["routed"] = True
        update["$set"]["routed_to"] = (payload or {}).get("href")
        update["$set"]["routed_src"] = (payload or {}).get("src")
    await db.strate_sessions.update_one({"session_id": session_id}, update, upsert=True)


# ==================== CHAT FLOW ====================

def _truncate_words(text: str, limit: int = MAX_WORDS_PER_MESSAGE) -> str:
    """Hard-limit reply length in words."""
    if not text:
        return text
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + "…"


@router.post("/strate/chat")
async def strate_chat(chat_input: StrateChatInput):
    """Main reception flow. Deterministic for steps 1-2, AI only for free_text."""
    # Kill switch
    cfg = await _get_config()
    if not cfg.get("enabled", True):
        raise HTTPException(status_code=503, detail="Conciergerie désactivée par l'administrateur")

    session_id = chat_input.session_id or str(uuid.uuid4())
    step = chat_input.step
    page = chat_input.page

    # ---------- STEP: greeting (initial opening) ----------
    if step == "greeting":
        await _track_event(session_id, "open", {"page": page}, page=page)
        return {
            "session_id": session_id,
            "step": "greeting",
            "message": GREETING,
            "rgpd_notice": RGPD_BANNER,
            "options": ROOT_OPTIONS,
            "expert_cta": EXPERT_CTA,
        }

    # ---------- STEP: qualify (after category click) ----------
    if step == "qualify":
        cat = chat_input.category_id
        if cat == "other":
            # Ask free-text
            await _track_event(session_id, "qualify", {"category": "other"}, page=page)
            return {
                "session_id": session_id,
                "step": "free_text",
                "message": "Résumez votre situation en une phrase.",
                "expert_cta": EXPERT_CTA,
            }
        if cat not in QUALIFICATION:
            raise HTTPException(status_code=400, detail="Catégorie invalide")

        qdata = QUALIFICATION[cat]
        await _track_event(session_id, "qualify", {"category": cat}, page=page)
        return {
            "session_id": session_id,
            "step": "qualify",
            "category_id": cat,
            "message": _truncate_words(qdata["prompt"]),
            "options": qdata["options"],
            "expert_cta": EXPERT_CTA,
        }

    # ---------- STEP: route (final CTA after qualification click) ----------
    if step == "route":
        qid = chat_input.qualification_id
        if not qid or qid not in CTA_MAP:
            raise HTTPException(status_code=400, detail="Qualification invalide")

        ctas = CTA_MAP[qid]
        await _track_event(session_id, "route_shown", {"qualification": qid}, page=page)
        return {
            "session_id": session_id,
            "step": "route",
            "qualification_id": qid,
            "message": "Voici ce que je vous recommande :",
            "primary_cta": ctas["primary"],
            "alternative_cta": ctas["alternative"],
            "expert_cta": EXPERT_CTA,
        }

    # ---------- STEP: free_text (Autre situation → AI detect intent) ----------
    if step == "free_text":
        text = (chat_input.text or "").strip()
        if len(text) < 3:
            raise HTTPException(status_code=400, detail="Message trop court")

        # Pre-filter sensitive data
        if contains_sensitive_data(text):
            await _track_event(session_id, "sensitive_detected", {"len": len(text)}, page=page)
            return {
                "session_id": session_id,
                "step": "sensitive",
                "message": ("Pour votre protection, ne partagez pas de données médicales ici. "
                            "Passons par un contact direct."),
                "expert_cta": EXPERT_CTA,
            }

        result = await _detect_intent_free_text(text)
        if result.get("out_of_scope"):
            await _track_event(session_id, "out_of_scope", {"text_len": len(text)}, page=page)
            return {
                "session_id": session_id,
                "step": "out_of_scope",
                "message": ("Ce point sort de notre expertise (droits MDPH / AT-MP / expertise médicale). "
                            "Souhaitez-vous recentrer ou parler à un expert ?"),
                "options": [
                    {"id": "at_mp_rights", "label": "Recentrer sur mes droits"},
                ],
                "expert_cta": EXPERT_CTA,
            }

        suggestions = result.get("suggestions") or FREE_TEXT_FALLBACK["suggestions"]
        # Build 3 option cards from suggestion IDs
        option_cards = []
        for sid in suggestions[:3]:
            if sid in CTA_MAP:
                option_cards.append({"id": sid, "label": _label_for(sid)})

        await _track_event(session_id, "free_text_intent", {"suggestions": suggestions}, page=page)
        return {
            "session_id": session_id,
            "step": "confirm",
            "message": "Votre situation ressemble à :",
            "options": option_cards,
            "expert_cta": EXPERT_CTA,
        }

    # ---------- STEP: route_click (visitor clicked a CTA) ----------
    if step == "route_click":
        href = chat_input.text  # reuse text field for href
        src = chat_input.category_id  # reuse category_id for src
        await _track_event(session_id, "route_click", {"href": href, "src": src}, page=page)
        return {"session_id": session_id, "success": True}

    raise HTTPException(status_code=400, detail=f"Étape inconnue : {step}")


def _label_for(qid: str) -> str:
    """Human label for a qualification id."""
    labels = {
        "at_mp_declaration": "Déclaration AT / contestation CPAM",
        "at_mp_consolidation": "Consolidation / IPP / expertise AT",
        "at_mp_reconnaissance": "Refus maladie professionnelle",
        "at_mp_rights": "Comprendre mes droits AT/MP",
        "mdph_first": "Premier dossier MDPH / AAH",
        "mdph_refus": "Refus MDPH ou AAH",
        "mdph_recours": "Préparer un recours MDPH",
        "mdph_rights": "Comprendre mes droits MDPH",
        "exp_prepare": "Préparer une expertise",
        "exp_refuse": "Expertise défavorable",
        "exp_assurance": "Litige avec mon assurance",
        "exp_rights": "Comprendre l'expertise médicale",
    }
    return labels.get(qid, qid)


# ==================== AI INTENT DETECTION ====================

async def _detect_intent_free_text(text: str) -> dict:
    """Call Claude with a tightly constrained JSON prompt. Fallback: default 3 rights options."""
    if not ANTHROPIC_API_KEY and not EMERGENT_LLM_KEY:
        return FREE_TEXT_FALLBACK

    try:
        if ANTHROPIC_API_KEY:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            resp = await client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,
                system=FREE_TEXT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": text}],
            )
            raw = resp.content[0].text.strip()
        else:
            import httpx
            from emergentintegrations.llm.utils import get_integration_proxy_url
            proxy_url = get_integration_proxy_url()
            url = f"{proxy_url}/llm/chat/completions"
            headers = {"Authorization": f"Bearer {EMERGENT_LLM_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "claude-haiku-4-5-20251001",
                "messages": [
                    {"role": "system", "content": FREE_TEXT_SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                "max_tokens": 200,
            }
            async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=8.0)) as h:
                r = await h.post(url, headers=headers, json=payload)
                if r.status_code != 200:
                    return FREE_TEXT_FALLBACK
                raw = r.json()["choices"][0]["message"]["content"].strip()

        # Parse JSON
        cleaned = raw
        # Strip markdown code fences if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.MULTILINE).strip()
        parsed = json_mod.loads(cleaned)
        if not isinstance(parsed, dict):
            return FREE_TEXT_FALLBACK
        # Validate shape
        suggestions = parsed.get("suggestions") or []
        if not isinstance(suggestions, list):
            suggestions = []
        # Keep only known IDs
        suggestions = [s for s in suggestions if s in CTA_MAP][:3]
        return {
            "suggestions": suggestions,
            "out_of_scope": bool(parsed.get("out_of_scope", False)),
        }
    except Exception as e:
        logger.error(f"[strate] free-text detection failed: {e}")
        return FREE_TEXT_FALLBACK


# ==================== ADMIN KPIs ====================

@router.get("/admin/strate/kpis")
async def admin_strate_kpis(
    period: str = Query("30d", description="7d | 30d | all"),
    admin: dict = Depends(get_current_admin),
):
    now = datetime.now(timezone.utc)
    if period == "7d":
        since = (now - timedelta(days=7)).isoformat()
    elif period == "30d":
        since = (now - timedelta(days=30)).isoformat()
    else:
        since = None

    match = {}
    if since:
        match["created_at"] = {"$gte": since}

    total_sessions = await db.strate_sessions.count_documents(match)
    opened = await db.strate_sessions.count_documents({**match, "opened": True})
    qualified = await db.strate_sessions.count_documents({**match, "qualified": True})
    routed = await db.strate_sessions.count_documents({**match, "routed": True})

    # Routing breakdown by src
    pipeline = [
        {"$match": {**match, "routed": True}},
        {"$group": {"_id": "$routed_src", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ]
    breakdown = await db.strate_sessions.aggregate(pipeline).to_list(50)

    # Opens per page (for diagnostic)
    page_pipeline = [
        {"$match": {**match, "opened": True}},
        {"$group": {"_id": "$last_page", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    opens_per_page = await db.strate_sessions.aggregate(page_pipeline).to_list(10)

    def rate(a, b):
        return round((a / b * 100), 1) if b > 0 else 0.0
    return {
        "period": period,
        "totals": {
            "sessions": total_sessions,
            "opened": opened,
            "qualified": qualified,
            "routed": routed,
        },
        "rates": {
            "open_rate": rate(opened, total_sessions),
            "qualification_rate": rate(qualified, opened),
            "routing_rate": rate(routed, opened),  # KPI principal
        },
        "routing_breakdown": [{"src": b["_id"] or "unknown", "count": b["count"]} for b in breakdown],
        "opens_per_page": [{"page": p["_id"] or "unknown", "count": p["count"]} for p in opens_per_page],
    }
