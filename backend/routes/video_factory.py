"""S.E.S Autonomous Video Factory — API routes.

Endpoints :
- POST /api/admin/video-factory/generate    → génère 1 à 5 vidéos
- GET  /api/admin/video-factory/history     → historique (lecture seule, V1+D2)
- DELETE /api/admin/video-factory/{id}      → suppression entrée historique

Auth : admin uniquement. Module isolé, ne touche à aucun pipeline existant.
"""
import uuid
import json as json_mod
import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from config import db, logger
from utils.auth import get_current_admin
from utils.video_agent import (
    DEFAULT_MODEL,
    MAX_BATCH_SIZE,
    build_user_prompt,
    call_video_factory_llm,
    safe_parse_json,
    validate_and_normalize,
    estimate_cost_eur,
)

router = APIRouter(prefix="/admin/video-factory", tags=["video-factory"])


# ============================================================================
# MODELS
# ============================================================================

ALLOWED_SERVICES = {"0€", "29€", "97€", "auto"}
ALLOWED_INTENTIONS = {"émotion", "autorité", "éducatif"}
ALLOWED_URGENCES = {"faible", "moyen", "critique"}
ALLOWED_PLATFORMS = {"TikTok", "YouTube Shorts", "Facebook Reels", "Instagram Reels"}


class GenerateInput(BaseModel):
    topic_brief: str = Field(..., min_length=5, max_length=500)
    service_target: str = Field("auto")
    intention: str = Field("autorité")
    urgence: str = Field("moyen")
    plateforme: str = Field("TikTok")
    batch_size: int = Field(1, ge=1, le=MAX_BATCH_SIZE)


class GenerateOutput(BaseModel):
    run_id: str
    model_used: str
    estimated_cost_eur: float
    videos: list
    warnings: list
    created_at: str


# ============================================================================
# POST /generate
# ============================================================================

@router.post("/generate", response_model=GenerateOutput)
async def generate_videos(req: GenerateInput, admin=Depends(get_current_admin)):
    """Génère 1 à 5 vidéos en 1 appel LLM unique. Sauvegarde MongoDB."""
    # --- 1. Validate enums (cheap, fail-fast) ---
    if req.service_target not in ALLOWED_SERVICES:
        raise HTTPException(400, f"service_target invalide. Valeurs : {ALLOWED_SERVICES}")
    if req.intention not in ALLOWED_INTENTIONS:
        raise HTTPException(400, f"intention invalide. Valeurs : {ALLOWED_INTENTIONS}")
    if req.urgence not in ALLOWED_URGENCES:
        raise HTTPException(400, f"urgence invalide. Valeurs : {ALLOWED_URGENCES}")
    if req.plateforme not in ALLOWED_PLATFORMS:
        raise HTTPException(400, f"plateforme invalide. Valeurs : {ALLOWED_PLATFORMS}")

    # --- 2. Build prompt ---
    user_prompt = build_user_prompt(
        topic_brief=req.topic_brief,
        service_target=req.service_target,
        intention=req.intention,
        urgence=req.urgence,
        plateforme=req.plateforme,
        batch_size=req.batch_size,
    )

    # --- 3. LLM call (with 1 retry on JSON malformé) ---
    raw_text = None
    parsed = None
    last_err = None
    for attempt in (1, 2):
        try:
            temp = 0.7 if attempt == 1 else 0.1
            raw_text = await call_video_factory_llm(
                user_prompt=user_prompt,
                model=DEFAULT_MODEL,
                max_tokens=9000,
                temperature=temp,
            )
            parsed = safe_parse_json(raw_text)
            break
        except json_mod.JSONDecodeError as e:
            last_err = f"JSON parse error (attempt {attempt}): {e}"
            logger.warning(f"[video-factory] {last_err}")
            continue
        except Exception as e:
            last_err = f"LLM error (attempt {attempt}): {e}"
            logger.error(f"[video-factory] {last_err}")
            if attempt == 2:
                raise HTTPException(502, f"Erreur génération IA : {str(e)[:200]}")

    if parsed is None:
        raise HTTPException(502, f"Sortie LLM invalide après 2 tentatives. {last_err}")

    # --- 4. Validation & normalisation ---
    try:
        normalized, warnings = validate_and_normalize(
            parsed=parsed,
            service_target=req.service_target,
            urgence=req.urgence,
            plateforme=req.plateforme,
        )
    except ValueError as e:
        raise HTTPException(502, f"Sortie LLM invalide : {e}")

    # --- 5. Sauvegarde Mongo ---
    run_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    record = {
        "id": run_id,
        "created_at": created_at,
        "admin_email": admin.get("email"),
        "input": req.model_dump(),
        "model_used": DEFAULT_MODEL,
        "videos": normalized.get("videos", []),
        "warnings": warnings,
        "estimated_cost_eur": estimate_cost_eur(req.batch_size, DEFAULT_MODEL),
        "status": "draft",
    }
    try:
        await db.video_factory_runs.insert_one(record)
    except Exception as e:
        logger.error(f"[video-factory] Mongo insert failed: {e}")
        # Ne bloque pas le retour à l'admin (output déjà valide en mémoire)

    return GenerateOutput(
        run_id=run_id,
        model_used=DEFAULT_MODEL,
        estimated_cost_eur=record["estimated_cost_eur"],
        videos=normalized.get("videos", []),
        warnings=warnings,
        created_at=created_at,
    )


# ============================================================================
# GET /history
# ============================================================================

@router.get("/history")
async def list_history(
    limit: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin),
):
    """Historique des générations, plus récentes d'abord. _id exclu."""
    cursor = (
        db.video_factory_runs
        .find({}, {"_id": 0})
        .sort("created_at", -1)
        .limit(limit)
    )
    items = await cursor.to_list(length=limit)
    return {"items": items, "count": len(items)}


# ============================================================================
# DELETE /{run_id}
# ============================================================================

@router.delete("/{run_id}")
async def delete_run(run_id: str, admin=Depends(get_current_admin)):
    """Supprime une entrée historique."""
    res = await db.video_factory_runs.delete_one({"id": run_id})
    if res.deleted_count == 0:
        raise HTTPException(404, "Run introuvable.")
    return {"deleted": True, "run_id": run_id}


# ============================================================================
# PATCH /{run_id}/status — Marquer publié / brouillon (V1+ optionnel)
# ============================================================================

class StatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(draft|published|archived)$")


@router.patch("/{run_id}/status")
async def update_status(run_id: str, body: StatusUpdate, admin=Depends(get_current_admin)):
    res = await db.video_factory_runs.update_one(
        {"id": run_id},
        {"$set": {"status": body.status, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    if res.matched_count == 0:
        raise HTTPException(404, "Run introuvable.")
    return {"updated": True, "run_id": run_id, "status": body.status}
