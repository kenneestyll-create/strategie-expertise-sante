"""S.E.S Video Factory V2 — Performance Optimizer.

Calcule les poids normalisés par format à partir des métriques saisies par
l'admin (views / CTR / conversion). Applique un floor d'exploration ε-greedy
de 10% par format pour éviter la monoculture.

V2 Final Stabilisation :
- Clamp weights ∈ [0, 1] systématique (anti-dérive numérique)
- Helper get_recent_format_usage_7d() pour garde monoculture (fenêtre glissante)

Persistence :
- collection `video_metrics` : 1 doc par vidéo publiée (views, ctr, conversion)
- collection `video_format_weights` : 1 doc unique (`_id="latest"`) avec les
  poids agrégés par format.
- collection `video_factory_runs` : 1 doc par génération (sert à la garde
  monoculture via agrégation du `videos[].format_used` sur 7j glissants).
"""
import random
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

from config import db, logger

ALL_FORMATS = ["F1", "F2", "F3", "F4", "F5", "F6", "F7"]
EXPLORATION_FLOOR = 0.10  # 10% — chaque format garanti au moins ce poids
MONOCULTURE_THRESHOLD = 0.65  # >65% sur 7j → reroll
MONOCULTURE_MIN_RUNS = 5  # <5 runs sur 7j → garde désactivée (signal insuffisant)


def _clamp01(value: float) -> float:
    """Clamp strict d'une valeur dans [0.0, 1.0]."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, v))


# ============================================================================
# COMPUTE WEIGHTS
# ============================================================================

def _safe_max(values: List[float]) -> float:
    """Max strictement positif (évite division par 0)."""
    m = max(values) if values else 0.0
    return m if m > 0 else 1.0


def compute_format_weights(metrics_by_format: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """À partir d'agrégats par format, calcule un score normalisé puis applique
    le floor d'exploration.

    metrics_by_format = {
        "F1": {"views": 12000, "ctr": 3.2, "conversion": 1.1, "samples": 4},
        ...
    }

    Formule : 0.5 × norm_conv + 0.3 × norm_ctr + 0.2 × norm_views
    Normalisation : chaque métrique divisée par son max observé tous formats.
    Puis floor : weight = max(weight_brut, EXPLORATION_FLOOR).
    """
    # Init weights at floor for all formats (so absent ones still get explored)
    weights = {f: EXPLORATION_FLOOR for f in ALL_FORMATS}

    if not metrics_by_format:
        return weights

    conv_vals = [m.get("conversion", 0.0) for m in metrics_by_format.values()]
    ctr_vals = [m.get("ctr", 0.0) for m in metrics_by_format.values()]
    view_vals = [m.get("views", 0.0) for m in metrics_by_format.values()]
    max_conv = _safe_max(conv_vals)
    max_ctr = _safe_max(ctr_vals)
    max_views = _safe_max(view_vals)

    for fmt, m in metrics_by_format.items():
        if fmt not in ALL_FORMATS:
            continue
        norm_conv = (m.get("conversion", 0.0) / max_conv) if max_conv > 0 else 0.0
        norm_ctr = (m.get("ctr", 0.0) / max_ctr) if max_ctr > 0 else 0.0
        norm_views = (m.get("views", 0.0) / max_views) if max_views > 0 else 0.0
        raw = 0.5 * norm_conv + 0.3 * norm_ctr + 0.2 * norm_views
        weights[fmt] = max(raw, EXPLORATION_FLOOR)

    # Final clamp ∈ [0, 1] — anti-dérive numérique (V2 final stabilisation)
    return {f: _clamp01(w) for f, w in weights.items()}


def pick_format_weighted(weights: Dict[str, float]) -> str:
    """Tire un format au hasard pondéré par les weights fournis.
    Garantit la cohérence ε-greedy via le floor déjà appliqué.
    """
    formats = list(weights.keys()) or ALL_FORMATS
    w = [weights.get(f, EXPLORATION_FLOOR) for f in formats]
    if sum(w) <= 0:
        return random.choice(formats)
    return random.choices(formats, weights=w, k=1)[0]


# ============================================================================
# AGGREGATION FROM MONGO
# ============================================================================

async def aggregate_metrics_by_format() -> Dict[str, Dict[str, float]]:
    """Agrège la collection video_metrics par format (moyennes views/ctr/conv).
    Retourne {} si aucune métrique enregistrée.
    """
    pipeline = [
        {"$group": {
            "_id": "$format_used",
            "views": {"$avg": "$views"},
            "ctr": {"$avg": "$ctr"},
            "conversion": {"$avg": "$conversion"},
            "samples": {"$sum": 1},
        }}
    ]
    out = {}
    try:
        async for doc in db.video_metrics.aggregate(pipeline):
            fmt = doc.get("_id")
            if fmt in ALL_FORMATS:
                out[fmt] = {
                    "views": float(doc.get("views") or 0),
                    "ctr": float(doc.get("ctr") or 0),
                    "conversion": float(doc.get("conversion") or 0),
                    "samples": int(doc.get("samples") or 0),
                }
    except Exception as e:
        logger.error(f"[video-perf] aggregate failed: {e}")
    return out


async def recompute_and_save_weights() -> Dict[str, float]:
    """Recalcule les poids depuis les métriques et persiste un snapshot.
    Appelé après chaque saisie de métrique côté admin.
    """
    metrics = await aggregate_metrics_by_format()
    weights = compute_format_weights(metrics)
    snapshot = {
        "_id": "latest",
        "weights": weights,
        "metrics_by_format": metrics,
        "total_samples": sum(int(m.get("samples", 0)) for m in metrics.values()),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await db.video_format_weights.update_one(
            {"_id": "latest"}, {"$set": snapshot}, upsert=True
        )
    except Exception as e:
        logger.error(f"[video-perf] save weights failed: {e}")
    return weights


async def get_latest_weights() -> Optional[Dict[str, float]]:
    """Retourne les poids persistés ou None si aucun snapshot."""
    try:
        doc = await db.video_format_weights.find_one({"_id": "latest"})
        if doc and isinstance(doc.get("weights"), dict):
            return doc["weights"]
    except Exception as e:
        logger.error(f"[video-perf] get weights failed: {e}")
    return None


async def get_weights_summary() -> Dict:
    """Snapshot complet pour affichage admin (poids + métriques + total samples)."""
    try:
        doc = await db.video_format_weights.find_one(
            {"_id": "latest"}, {"_id": 0}
        )
        if not doc:
            return {
                "weights": {f: EXPLORATION_FLOOR for f in ALL_FORMATS},
                "metrics_by_format": {},
                "total_samples": 0,
                "updated_at": None,
            }
        # Re-clamp défensif au cas où un snapshot ancien serait corrompu
        if isinstance(doc.get("weights"), dict):
            doc["weights"] = {f: _clamp01(w) for f, w in doc["weights"].items()}
        return doc
    except Exception as e:
        logger.error(f"[video-perf] summary failed: {e}")
        return {
            "weights": {f: EXPLORATION_FLOOR for f in ALL_FORMATS},
            "metrics_by_format": {},
            "total_samples": 0,
            "updated_at": None,
        }


# ============================================================================
# GARDE MONOCULTURE (V2 Final Stabilisation)
# ============================================================================

async def get_recent_format_usage_7d() -> Optional[Dict[str, int]]:
    """Compte le nombre de runs par format sur les 7 derniers jours glissants.

    Retourne {format: count} ou None si <MONOCULTURE_MIN_RUNS sur la fenêtre
    (signal statistique insuffisant pour appliquer la garde).
    """
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$unwind": "$videos"},
        {"$group": {"_id": "$videos.format_used", "count": {"$sum": 1}}},
    ]
    counts: Dict[str, int] = {}
    total = 0
    try:
        async for doc in db.video_factory_runs.aggregate(pipeline):
            fmt = doc.get("_id")
            c = int(doc.get("count") or 0)
            if fmt in ALL_FORMATS:
                counts[fmt] = c
                total += c
    except Exception as e:
        logger.error(f"[video-perf] usage_7d failed: {e}")
        return None

    if total < MONOCULTURE_MIN_RUNS:
        return None  # Signal insuffisant — garde désactivée
    return counts


def is_format_overused(format_id: str, usage: Dict[str, int]) -> bool:
    """True si ce format a été utilisé >MONOCULTURE_THRESHOLD (65%) sur la fenêtre."""
    total = sum(usage.values()) or 0
    if total <= 0:
        return False
    return (usage.get(format_id, 0) / total) > MONOCULTURE_THRESHOLD


def pick_format_excluding(weights: Dict[str, float], excluded: str) -> str:
    """Tire un format pondéré en excluant strictement `excluded`.
    Si le seul format restant après exclusion a poids 0, retombe en uniforme."""
    candidates = [f for f in ALL_FORMATS if f != excluded]
    w = [weights.get(f, EXPLORATION_FLOOR) for f in candidates]
    if sum(w) <= 0:
        return random.choice(candidates)
    return random.choices(candidates, weights=w, k=1)[0]


def pick_format_uniform() -> str:
    """Tirage uniforme parmi F1-F7 (mode fallback)."""
    return random.choice(ALL_FORMATS)
