"""Admin destructive actions — individual deletes and bulk purges.

Used for production go-live cleanup. All purge-all endpoints require confirmation.
Individual deletes do NOT require confirmation (single-item precision click).

Tab coverage:
  - Bookings (RDV) : delete one + purge all
  - Clients : delete one + purge all
  - Abandoned checkouts (Relance) : list + delete one + purge all
  - Alertes urgentes : delete one + purge all
  - Referral codes (Parrainage) : delete one code + purge all codes + purge all uses
  - StrategiIA analyses : purge all (reset stats)
  - Completeness notifications : purge all
  - Strategic feedback : delete one + purge all
  - Admin documents : delete one + purge all

Existing endpoints are NOT touched.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from config import db, logger
from utils.auth import get_current_admin

router = APIRouter()


def _confirm_or_400(payload: dict | None) -> None:
    code = (payload or {}).get("confirm", "").strip()
    if code != "PURGER":
        raise HTTPException(
            status_code=400,
            detail='Confirmation requise : envoyer {"confirm": "PURGER"} dans le body.',
        )


# ────────────────── BOOKINGS (RDV) ──────────────────
@router.delete("/admin/bookings/{booking_id}")
async def delete_booking(booking_id: str, admin: dict = Depends(get_current_admin)):
    res = await db.bookings.delete_one({"id": booking_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="RDV introuvable")
    logger.info(f"admin_cleanup: booking {booking_id} deleted by {admin.get('email')}")
    return {"deleted": res.deleted_count}


@router.post("/admin/bookings/purge-all")
async def purge_all_bookings(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    res = await db.bookings.delete_many({})
    logger.info(f"admin_cleanup: ALL bookings purged ({res.deleted_count}) by {admin.get('email')}")
    return {"deleted": res.deleted_count}


# ────────────────── CLIENTS ──────────────────
@router.delete("/admin/clients/{client_id}")
async def delete_client(client_id: str, admin: dict = Depends(get_current_admin)):
    res = await db.client_users.delete_one({"id": client_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Client introuvable")
    # Cascade: remove their cases too
    await db.client_cases.delete_many({"client_id": client_id})
    logger.info(f"admin_cleanup: client {client_id} + cases deleted by {admin.get('email')}")
    return {"deleted": res.deleted_count}


@router.post("/admin/clients/purge-all")
async def purge_all_clients(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    res = await db.client_users.delete_many({})
    cases_res = await db.client_cases.delete_many({})
    logger.info(f"admin_cleanup: ALL clients purged ({res.deleted_count}) + {cases_res.deleted_count} cases by {admin.get('email')}")
    return {"deleted": res.deleted_count, "cases_deleted": cases_res.deleted_count}


# ────────────────── ABANDONED CHECKOUTS (Relance) ──────────────────
@router.get("/admin/abandoned-checkouts")
async def list_abandoned_checkouts(admin: dict = Depends(get_current_admin)):
    items = await db.abandoned_checkouts.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return {"items": items, "total": len(items)}


@router.delete("/admin/abandoned-checkouts/{abandon_id}")
async def delete_abandoned(abandon_id: str, admin: dict = Depends(get_current_admin)):
    res = await db.abandoned_checkouts.delete_one({"id": abandon_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Entrée introuvable")
    return {"deleted": res.deleted_count}


@router.post("/admin/abandoned-checkouts/purge-all")
async def purge_all_abandoned(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    res = await db.abandoned_checkouts.delete_many({})
    logger.info(f"admin_cleanup: ALL abandoned_checkouts purged ({res.deleted_count}) by {admin.get('email')}")
    return {"deleted": res.deleted_count}


# ────────────────── ALERTES URGENTES (collection: urgent_alerts) ──────────────────
@router.delete("/admin/alertes-urgentes/{alert_id}")
async def delete_alert(alert_id: str, admin: dict = Depends(get_current_admin)):
    res = await db.urgent_alerts.delete_one({"id": alert_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alerte introuvable")
    logger.info(f"admin_cleanup: urgent_alert {alert_id} deleted by {admin.get('email')}")
    return {"deleted": res.deleted_count}


@router.post("/admin/alertes-urgentes/purge-all")
async def purge_all_alerts(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    res = await db.urgent_alerts.delete_many({})
    logger.info(f"admin_cleanup: ALL urgent_alerts purged ({res.deleted_count}) by {admin.get('email')}")
    return {"deleted": res.deleted_count}


# ────────────────── REFERRALS (Parrainage) ──────────────────
@router.delete("/admin/referrals/codes/{code_id}")
async def delete_referral_code(code_id: str, admin: dict = Depends(get_current_admin)):
    res = await db.referral_codes.delete_one({"id": code_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Code introuvable")
    return {"deleted": res.deleted_count}


@router.post("/admin/referrals/purge-all")
async def purge_all_referrals(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    codes_res = await db.referral_codes.delete_many({})
    uses_res = await db.referral_uses.delete_many({})
    logger.info(f"admin_cleanup: ALL referrals purged ({codes_res.deleted_count} codes + {uses_res.deleted_count} uses) by {admin.get('email')}")
    return {"codes_deleted": codes_res.deleted_count, "uses_deleted": uses_res.deleted_count}


# ────────────────── STRATEGIIA (reset stats) ──────────────────
@router.post("/admin/strategiia-analyses/purge-all")
async def purge_all_strategiia(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    res = await db.strategiia_analyses.delete_many({})
    # Also clean related premium_analyses tied to strategiia
    pr_res = await db.premium_analyses.delete_many({"type": "strategiia"})
    cas_res = await db.cas_anonymises.delete_many({}) if "cas_anonymises" in await db.list_collection_names() else None
    logger.info(f"admin_cleanup: ALL strategiia_analyses ({res.deleted_count}) + {pr_res.deleted_count} premium purged by {admin.get('email')}")
    return {
        "analyses_deleted": res.deleted_count,
        "premium_deleted": pr_res.deleted_count,
        "cas_deleted": cas_res.deleted_count if cas_res else 0,
    }


# ────────────────── COMPLETENESS NOTIFICATIONS ──────────────────
@router.post("/admin/completeness-notifications/purge-all")
async def purge_all_completeness(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    res = await db.completeness_notifications.delete_many({})
    logger.info(f"admin_cleanup: ALL completeness_notifications purged ({res.deleted_count}) by {admin.get('email')}")
    return {"deleted": res.deleted_count}


# ────────────────── STRATEGIC FEEDBACK ──────────────────
@router.delete("/admin/strategic-feedback/{feedback_id}")
async def delete_feedback(feedback_id: str, admin: dict = Depends(get_current_admin)):
    res = await db.strategic_feedback.delete_one({"id": feedback_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Feedback introuvable")
    return {"deleted": res.deleted_count}


@router.post("/admin/strategic-feedback/purge-all")
async def purge_all_feedback(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    res = await db.strategic_feedback.delete_many({})
    logger.info(f"admin_cleanup: ALL strategic_feedback purged ({res.deleted_count}) by {admin.get('email')}")
    return {"deleted": res.deleted_count}


# ────────────────── ADMIN DOCUMENTS (client_documents collection) ──────────────────
@router.delete("/admin/documents/{doc_id}")
async def delete_admin_doc(doc_id: str, admin: dict = Depends(get_current_admin)):
    res = await db.client_documents.delete_one({"id": doc_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document introuvable")
    logger.info(f"admin_cleanup: client_document {doc_id} deleted by {admin.get('email')}")
    return {"deleted": res.deleted_count}


@router.post("/admin/documents/purge-all")
async def purge_all_admin_docs(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    res = await db.client_documents.delete_many({})
    logger.info(f"admin_cleanup: ALL client_documents purged ({res.deleted_count}) by {admin.get('email')}")
    return {"deleted": res.deleted_count}


@router.get("/admin/documents/test-preview")
async def preview_test_docs(admin: dict = Depends(get_current_admin)):
    """Detect test documents by filename pattern."""
    import re as _re
    docs = await db.client_documents.find(
        {}, {"_id": 0, "id": 1, "filename": 1, "client_id": 1, "status": 1, "created_at": 1}
    ).limit(2000).to_list(2000)
    pat = _re.compile(r"(?:^test[_-]|test_document|test\.pdf|sample|dummy|playwright|pytest)", _re.I)
    items = [d for d in docs if pat.search(d.get("filename") or "")]
    sample = [{"id": i.get("id"), "filename": i.get("filename"), "status": i.get("status")} for i in items[:50]]
    return {"count": len(items), "sample": sample}


@router.post("/admin/documents/purge-tests")
async def purge_test_docs(payload: dict = Body(default=None), admin: dict = Depends(get_current_admin)):
    _confirm_or_400(payload)
    import re as _re
    docs = await db.client_documents.find(
        {}, {"_id": 0, "id": 1, "filename": 1}
    ).limit(2000).to_list(2000)
    pat = _re.compile(r"(?:^test[_-]|test_document|test\.pdf|sample|dummy|playwright|pytest)", _re.I)
    ids = [d["id"] for d in docs if pat.search(d.get("filename") or "") and d.get("id")]
    if not ids:
        return {"deleted": 0}
    res = await db.client_documents.delete_many({"id": {"$in": ids}})
    logger.info(f"admin_cleanup: {res.deleted_count} test documents purged by {admin.get('email')}")
    return {"deleted": res.deleted_count}
