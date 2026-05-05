"""Test data cleanup — endpoints for sections that didn't have a purge yet.

Strategy:
- Detect test data via patterns (test emails, test names, admin email).
- Two-step API: GET /preview returns matching items with count; POST /purge actually deletes.
- Existing /admin/cleanup/* endpoints are NOT touched.
"""
import re
from fastapi import APIRouter, Depends, HTTPException, Body
from config import db, logger
from utils.auth import get_current_admin

router = APIRouter()

# ──────────────────────────── Detection patterns ────────────────────────────
TEST_EMAIL_PATTERNS = [
    r"@test\.[a-z]{2,4}$",       # @test.com, @test.fr, @test.io, etc.
    r"@example\.[a-z]{2,4}$",    # @example.com, @example.org, etc.
    r"@(localhost|fake|dummy|mock)",
    r"\+test[@.]",
    r"^test[._-]",
    r"_test[._-]",
    r"pytest",
    r"playwright",
]
TEST_NAME_PATTERNS = [
    r"^test\s",
    r"\stest$",
    r"pytest",
    r"playwright",
    r"^demo\s",
    r"\bautotest\b",
]
ADMIN_EMAIL_BLACKLIST = {
    "admin@accompagn-sante.fr",
    "admin@strategie-expertise-sante.fr",
}


def _is_test_email(email: str | None) -> bool:
    if not email:
        return False
    e = email.lower().strip()
    if e in ADMIN_EMAIL_BLACKLIST:
        return True
    return any(re.search(p, e) for p in TEST_EMAIL_PATTERNS)


def _is_test_name(name: str | None) -> bool:
    if not name:
        return False
    n = name.lower().strip()
    return any(re.search(p, n) for p in TEST_NAME_PATTERNS)


def _is_test_record(rec: dict, *, name_keys=("nom", "name", "full_name", "title", "topic")) -> bool:
    """Generic detector across multiple field shapes."""
    email_keys = ("email", "user_email", "client_email")
    for k in email_keys:
        if k in rec and _is_test_email(rec.get(k)):
            return True
    for k in name_keys:
        v = rec.get(k)
        if isinstance(v, str) and _is_test_name(v):
            return True
    if rec.get("is_test") is True:
        return True
    return False


# ──────────────────────────── Helpers ────────────────────────────
async def _scan(collection_name: str, name_keys: tuple[str, ...] = ("nom", "name")) -> list[dict]:
    docs = await db[collection_name].find({}, {"_id": 0}).to_list(2000)
    return [d for d in docs if _is_test_record(d, name_keys=name_keys)]


async def _delete_by_ids(collection_name: str, ids: list[str], id_field: str = "id") -> int:
    if not ids:
        return 0
    res = await db[collection_name].delete_many({id_field: {"$in": ids}})
    return res.deleted_count


def _confirm_or_400(payload: dict | None) -> None:
    code = (payload or {}).get("confirm", "").strip()
    if code != "PURGER":
        raise HTTPException(
            status_code=400,
            detail="Confirmation requise : envoyer {\"confirm\": \"PURGER\"} dans le body.",
        )


# ──────────────────────────── CLIENTS (client_users) ────────────────────────────
@router.get("/admin/test-cleanup/clients/preview")
async def preview_clients(admin: dict = Depends(get_current_admin)):
    items = await _scan("client_users", name_keys=("nom", "name", "full_name"))
    sample = [{
        "id": i.get("id"),
        "email": i.get("email"),
        "nom": i.get("nom") or i.get("name") or i.get("full_name"),
    } for i in items[:50]]
    return {"count": len(items), "sample": sample}


@router.post("/admin/test-cleanup/clients/purge")
async def purge_clients(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    items = await _scan("client_users", name_keys=("nom", "name", "full_name"))
    ids = [i["id"] for i in items if i.get("id")]
    deleted = await _delete_by_ids("client_users", ids)
    logger.info(f"test-cleanup/clients: {deleted} deleted by {admin.get('email')}")
    return {"deleted": deleted}


# ──────────────────────────── RDV (bookings) ────────────────────────────
@router.get("/admin/test-cleanup/bookings/preview")
async def preview_bookings(admin: dict = Depends(get_current_admin)):
    items = await _scan("bookings", name_keys=("nom", "name", "full_name"))
    sample = [{
        "id": i.get("id"),
        "email": i.get("email"),
        "nom": i.get("nom") or i.get("name"),
        "date": i.get("date") or i.get("created_at"),
    } for i in items[:50]]
    return {"count": len(items), "sample": sample}


@router.post("/admin/test-cleanup/bookings/purge")
async def purge_bookings(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    items = await _scan("bookings", name_keys=("nom", "name", "full_name"))
    ids = [i["id"] for i in items if i.get("id")]
    deleted = await _delete_by_ids("bookings", ids)
    logger.info(f"test-cleanup/bookings: {deleted} deleted by {admin.get('email')}")
    return {"deleted": deleted}


# ──────────────────────────── FEEDBACK (strategic_feedback) ────────────────────────────
@router.get("/admin/test-cleanup/feedback/preview")
async def preview_feedback(admin: dict = Depends(get_current_admin)):
    items = await _scan("strategic_feedback", name_keys=("nom", "name", "topic"))
    sample = [{
        "id": i.get("id"),
        "email": i.get("email"),
        "frein": (i.get("frein") or "")[:100],
        "besoin": (i.get("besoin") or "")[:100],
    } for i in items[:50]]
    return {"count": len(items), "sample": sample}


@router.post("/admin/test-cleanup/feedback/purge")
async def purge_feedback(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    items = await _scan("strategic_feedback", name_keys=("nom", "name", "topic"))
    ids = [i["id"] for i in items if i.get("id")]
    deleted = await _delete_by_ids("strategic_feedback", ids)
    logger.info(f"test-cleanup/feedback: {deleted} deleted by {admin.get('email')}")
    return {"deleted": deleted}


# ──────────────────────────── EDITORIAL DRAFTS ────────────────────────────
def _is_test_editorial(rec: dict) -> bool:
    """Editorial drafts: detect by title/topic containing test keywords."""
    for k in ("topic", "title", "h1", "subject"):
        v = rec.get(k)
        if isinstance(v, str) and re.search(r"\b(test|pytest|playwright|smoke|demo)\b", v.lower()):
            return True
    if rec.get("is_test") is True:
        return True
    return False


@router.get("/admin/test-cleanup/editorial/preview")
async def preview_editorial(admin: dict = Depends(get_current_admin)):
    docs = await db.editorial_articles.find({}, {"_id": 0}).to_list(500)
    items = [d for d in docs if _is_test_editorial(d)]
    sample = [{
        "id": i.get("id"),
        "topic": i.get("topic") or i.get("title"),
        "status": i.get("status"),
        "created_at": i.get("created_at"),
    } for i in items[:50]]
    return {"count": len(items), "sample": sample}


@router.post("/admin/test-cleanup/editorial/purge")
async def purge_editorial(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    docs = await db.editorial_articles.find({}, {"_id": 0, "id": 1, "topic": 1, "title": 1, "h1": 1, "subject": 1, "is_test": 1}).to_list(500)
    ids = [d["id"] for d in docs if d.get("id") and _is_test_editorial(d)]
    deleted = await _delete_by_ids("editorial_articles", ids)
    logger.info(f"test-cleanup/editorial: {deleted} deleted by {admin.get('email')}")
    return {"deleted": deleted}


# ──────────────────────────── RELANCE (alias of contacts purge) ────────────────────────────
# Relance UI is computed from contacts. The existing /admin/cleanup/contacts already covers this.
# We expose a preview endpoint so the Relance tab can show "0 test items" or "X test items"
# pointing back to the existing contact purge.
@router.get("/admin/test-cleanup/relance/preview")
async def preview_relance(admin: dict = Depends(get_current_admin)):
    docs = await db.contacts.find({}, {"_id": 0}).to_list(2000)
    items = [d for d in docs if _is_test_record(d, name_keys=("nom", "name", "prenom"))]
    sample = [{
        "id": i.get("id"),
        "email": i.get("email"),
        "nom": f"{i.get('prenom', '')} {i.get('nom', '')}".strip(),
    } for i in items[:50]]
    return {
        "count": len(items),
        "sample": sample,
        "note": "Les relances sont calculées depuis les contacts. Utilisez « Purger contacts » dans Config pour les supprimer.",
    }
