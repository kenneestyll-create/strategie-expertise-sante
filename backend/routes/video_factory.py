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
from typing import Optional, List, Dict

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from config import db, logger
from utils.auth import get_current_admin
from utils.video_agent import (
    DEFAULT_MODEL,
    MAX_BATCH_SIZE,
    FORMAT_LABELS,
    build_user_prompt,
    call_video_factory_llm,
    safe_parse_json,
    validate_and_normalize,
    estimate_cost_eur,
    build_seo_landing_user_prompt,
    call_seo_landing_llm,
    validate_and_normalize_seo_landing,
    estimate_seo_landing_cost_eur,
)
from utils.video_performance import (
    ALL_FORMATS,
    pick_format_weighted,
    pick_format_excluding,
    pick_format_uniform,
    recompute_and_save_weights,
    get_latest_weights,
    get_weights_summary,
    get_recent_format_usage_7d,
    is_format_overused,
)
import json as _json_log

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
    use_performance_weights: bool = Field(
        True,
        description=(
            "Si True et qu'un snapshot de poids existe, le backend choisit le "
            "format dominant pondéré et l'impose au LLM via forced_format."
        ),
    )
    forced_format: Optional[str] = Field(
        None,
        description="Force un format F1-F7 (override de la pondération).",
    )
    pdf_enabled: bool = Field(
        False,
        description="Si True, génère en plus une page SEO d'atterrissage (markdown + meta) "
                    "strictement dérivée de la 1re vidéo générée (anti-divergence garantie).",
    )


class GenerateOutput(BaseModel):
    run_id: str
    content_id: str  # V3 alias : content_id = run_id (1 doc Mongo unifié vidéo + SEO)
    model_used: str
    estimated_cost_eur: float
    videos: list
    warnings: list
    created_at: str
    forced_format: Optional[str] = None
    used_weights: bool = False
    mode: str = "free"  # forced | weighted | fallback | free
    seo_pdf: Optional[Dict] = None
    compliance_passed: bool = True  # ET logique : video.compliance_passed ET seo_pdf.compliance_passed


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

    # --- 1b. Validate optional forced_format ---
    if req.forced_format is not None and req.forced_format not in FORMAT_LABELS:
        raise HTTPException(400, f"forced_format invalide. Valeurs : {list(FORMAT_LABELS.keys())}")

    # --- 1c. Performance loop V2 Final : déterminer le mode + format ---
    # Modes possibles : forced | weighted | fallback | free
    chosen_forced: Optional[str] = req.forced_format
    perf_weights: Optional[Dict[str, float]] = None
    used_weights = False
    mode = "free"

    if chosen_forced is not None:
        mode = "forced"
    elif req.use_performance_weights:
        weights = await get_latest_weights()
        if weights:
            perf_weights = weights
            chosen_forced = pick_format_weighted(weights)
            used_weights = True
            mode = "weighted"

            # Garde anti-monoculture (fenêtre 7j glissante, min 5 runs)
            usage_7d = await get_recent_format_usage_7d()
            if usage_7d and is_format_overused(chosen_forced, usage_7d):
                logger.info(
                    f"[video-factory] monoculture guard triggered: "
                    f"format={chosen_forced} usage={usage_7d}"
                )
                chosen_forced = pick_format_excluding(weights, chosen_forced)
        else:
            # Snapshot absent → fallback uniforme contrôlé
            chosen_forced = pick_format_uniform()
            mode = "fallback"
    # else: free (LLM choisira librement, chosen_forced reste None)

    # --- 2. Build prompt ---
    user_prompt = build_user_prompt(
        topic_brief=req.topic_brief,
        service_target=req.service_target,
        intention=req.intention,
        urgence=req.urgence,
        plateforme=req.plateforme,
        batch_size=req.batch_size,
        forced_format=chosen_forced,
        performance_weights=perf_weights,
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

    # --- 4b. (V3) SEO Landing synchronisé — uniquement si pdf_enabled=true ---
    seo_pdf = None
    seo_warnings: List[str] = []
    if req.pdf_enabled and normalized.get("videos"):
        first_video = normalized["videos"][0]
        try:
            seo_user_prompt = build_seo_landing_user_prompt(first_video, req.plateforme)
            seo_raw = await call_seo_landing_llm(
                user_prompt=seo_user_prompt,
                model=DEFAULT_MODEL,
                max_tokens=6000,
                temperature=0.5,
            )
            seo_parsed = safe_parse_json(seo_raw)
            seo_pdf, seo_warnings = validate_and_normalize_seo_landing(
                parsed=seo_parsed,
                video=first_video,
                format_id=first_video.get("format_used", "F1"),
            )
            warnings = list(warnings) + [f"seo: {w}" for w in seo_warnings]
        except json_mod.JSONDecodeError as e:
            logger.warning(f"[video-factory] SEO JSON parse error: {e}")
            warnings.append("seo: JSON malformé (page SEO ignorée)")
        except Exception as e:
            logger.error(f"[video-factory] SEO landing generation failed: {e}")
            warnings.append(f"seo: échec génération ({str(e)[:80]})")

    # Compliance racine = ET logique (vidéo + seo_pdf si présent)
    all_videos_pass = all(v.get("compliance_passed", True) for v in normalized.get("videos", []))
    seo_passes = (seo_pdf is None) or bool(seo_pdf.get("compliance_passed", True))
    root_compliance = bool(all_videos_pass and seo_passes)

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
        "estimated_cost_eur": estimate_cost_eur(req.batch_size, DEFAULT_MODEL)
            + (estimate_seo_landing_cost_eur(DEFAULT_MODEL) if seo_pdf else 0.0),
        "status": "draft",
        "forced_format_resolved": chosen_forced,
        "used_weights": used_weights,
        "mode": mode,
        "seo_pdf": seo_pdf,
        "compliance_passed": root_compliance,
    }
    try:
        await db.video_factory_runs.insert_one(record)
    except Exception as e:
        logger.error(f"[video-factory] Mongo insert failed: {e}")
        # Ne bloque pas le retour à l'admin (output déjà valide en mémoire)

    # --- 5b. Log JSON structuré (1 ligne par vidéo générée, info-level) ---
    weights_snapshot = perf_weights or {}
    for vid_idx, vid in enumerate(normalized.get("videos", [])):
        try:
            logger.info(_json_log.dumps({
                "evt": "video_factory_generation",
                "video_id": f"{run_id}#{vid_idx}",
                "run_id": run_id,
                "format": vid.get("format_used"),
                "mode": mode,
                "weights_snapshot": weights_snapshot,
                "conversion_score": vid.get("conversion_score", 0),
                "timestamp": created_at,
            }, ensure_ascii=False))
        except Exception:
            pass  # log best-effort

    return GenerateOutput(
        run_id=run_id,
        content_id=run_id,
        model_used=DEFAULT_MODEL,
        estimated_cost_eur=record["estimated_cost_eur"],
        videos=normalized.get("videos", []),
        warnings=warnings,
        created_at=created_at,
        forced_format=chosen_forced,
        used_weights=used_weights,
        mode=mode,
        seo_pdf=seo_pdf,
        compliance_passed=root_compliance,
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


# ============================================================================
# V2 — PERFORMANCE LOOP
# ============================================================================

class MetricsInput(BaseModel):
    run_id: str
    video_idx: int = Field(0, ge=0, le=4)
    views: float = Field(..., ge=0)
    ctr: float = Field(..., ge=0, le=100, description="CTR en pourcentage (0-100)")
    conversion: float = Field(..., ge=0, le=100, description="Conversion en pourcentage")
    plateforme: Optional[str] = None
    note: Optional[str] = None


@router.post("/metrics")
async def save_metrics(body: MetricsInput, admin=Depends(get_current_admin)):
    """Saisie des métriques d'une vidéo publiée. Recalcule auto les poids."""
    run = await db.video_factory_runs.find_one({"id": body.run_id}, {"_id": 0})
    if not run:
        raise HTTPException(404, "Run introuvable.")
    videos = run.get("videos") or []
    if body.video_idx >= len(videos):
        raise HTTPException(400, "video_idx hors borne.")
    fmt = videos[body.video_idx].get("format_used")
    if fmt not in ALL_FORMATS:
        raise HTTPException(400, f"Format invalide dans le run : {fmt}")

    metric_doc = {
        "run_id": body.run_id,
        "video_idx": body.video_idx,
        "format_used": fmt,
        "views": float(body.views),
        "ctr": float(body.ctr),
        "conversion": float(body.conversion),
        "plateforme": body.plateforme or (run.get("input", {}).get("plateforme")),
        "note": body.note,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "admin_email": admin.get("email"),
    }
    # Upsert on (run_id, video_idx) to allow correction
    await db.video_metrics.update_one(
        {"run_id": body.run_id, "video_idx": body.video_idx},
        {"$set": metric_doc},
        upsert=True,
    )
    weights = await recompute_and_save_weights()
    return {"saved": True, "format_used": fmt, "weights_updated": True, "weights": weights}


@router.get("/metrics")
async def list_metrics(
    limit: int = Query(50, ge=1, le=500),
    admin=Depends(get_current_admin),
):
    """Liste les métriques saisies, plus récentes d'abord. _id exclu."""
    cursor = (
        db.video_metrics
        .find({}, {"_id": 0})
        .sort("created_at", -1)
        .limit(limit)
    )
    items = await cursor.to_list(length=limit)
    return {"items": items, "count": len(items)}


@router.get("/performance/weights")
async def get_performance_weights(admin=Depends(get_current_admin)):
    """Snapshot complet : poids actuels + agrégats par format + total samples."""
    return await get_weights_summary()


@router.post("/performance/recompute")
async def force_recompute(admin=Depends(get_current_admin)):
    """Force le recalcul du snapshot de poids (utile après suppression métrique)."""
    weights = await recompute_and_save_weights()
    return {"recomputed": True, "weights": weights}
