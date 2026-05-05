"""Agents Versions — V1 versioning/audit system for the AI agents ecosystem.

Endpoints:
  POST /admin/agents/versions          → manual snapshot (with optional note)
  GET  /admin/agents/versions          → paginated list (newest first, optional date filter)
  GET  /admin/agents/versions/{id}     → full snapshot detail
  GET  /admin/agents/versions/audit/pdf → audit report PDF (all versions)

Auto-snapshot on backend startup is handled in server.py via maybe_auto_snapshot().
"""
import io
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from config import db, logger
from utils.auth import get_current_admin
from utils.agents_snapshot import capture_state, compute_hash, compute_diff, now_iso

router = APIRouter()


COLLECTION = "agents_versions"


async def _latest_snapshot() -> dict | None:
    return await db[COLLECTION].find_one({}, {"_id": 0}, sort=[("seq", -1)])


async def _next_seq() -> int:
    last = await _latest_snapshot()
    return (last.get("seq", 0) + 1) if last else 1


async def _create_snapshot(*, source: str, created_by: str, notes: str = "") -> dict:
    """Create a snapshot and return it. Skip if hash matches latest (idempotent)."""
    state = await capture_state(db)
    h = compute_hash(state)

    latest = await _latest_snapshot()
    if latest and latest.get("hash") == h:
        return {"created": False, "reason": "no_change", "version": latest}

    changes = compute_diff(latest, state)
    seq = await _next_seq()
    doc = {
        "version_id": str(uuid.uuid4()),
        "seq": seq,
        "created_at": now_iso(),
        "created_by": created_by,
        "source": source,  # "manual" | "auto_startup"
        "notes": notes or "",
        "hash": h,
        "changes_summary": changes,
        "state": state,
    }
    await db[COLLECTION].insert_one(dict(doc))  # copy to avoid _id mutation
    doc.pop("_id", None)
    logger.info(f"agents_versions: snapshot v{seq} created (source={source}, by={created_by})")
    return {"created": True, "version": doc}


# ──────────────────── Public hook used by server.py ────────────────────
async def maybe_auto_snapshot():
    """Called once on backend startup. Creates a snapshot only if the hash differs."""
    try:
        result = await _create_snapshot(
            source="auto_startup",
            created_by="system@startup",
            notes="Snapshot automatique au démarrage du backend (modification détectée)",
        )
        if result.get("created"):
            logger.info("agents_versions: auto-snapshot created on startup")
        else:
            logger.info("agents_versions: no change detected on startup, no snapshot")
    except Exception as e:
        logger.warning(f"agents_versions: auto-snapshot failed (non-blocking): {e}")


# ──────────────────── Endpoints ────────────────────
@router.post("/admin/agents/versions")
async def create_version(payload: dict, admin: dict = Depends(get_current_admin)):
    notes = (payload or {}).get("notes", "").strip()[:500]
    result = await _create_snapshot(
        source="manual",
        created_by=admin.get("email", "admin"),
        notes=notes,
    )
    return result


@router.get("/admin/agents/versions")
async def list_versions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    q: str = Query("", description="Filter by date (YYYY-MM-DD) or author substring"),
    admin: dict = Depends(get_current_admin),
):
    query = {}
    if q:
        q = q.strip()
        # Try date prefix first, then author/notes substring
        if len(q) >= 4 and q[:4].isdigit():
            query["created_at"] = {"$regex": f"^{q}"}
        else:
            query["$or"] = [
                {"created_by": {"$regex": q, "$options": "i"}},
                {"notes": {"$regex": q, "$options": "i"}},
            ]

    total = await db[COLLECTION].count_documents(query)
    skip = (page - 1) * limit
    cursor = db[COLLECTION].find(
        query,
        {"_id": 0, "state": 0},  # omit heavy state on list
    ).sort("seq", -1).skip(skip).limit(limit)
    items = await cursor.to_list(limit)
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/admin/agents/versions/audit/pdf")
async def export_audit_pdf(admin: dict = Depends(get_current_admin)):
    """Audit PDF — all versions, newest first."""
    from utils.pdf_agents_audit import generate_audit_pdf

    items = await db[COLLECTION].find({}, {"_id": 0}).sort("seq", -1).to_list(None)
    try:
        pdf_bytes = generate_audit_pdf(items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

    filename = f"audit-ia-ses-{datetime.now().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/admin/agents/versions/{version_id}")
async def get_version_detail(version_id: str, admin: dict = Depends(get_current_admin)):
    doc = await db[COLLECTION].find_one({"version_id": version_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Version introuvable")
    return doc
