from fastapi import APIRouter, HTTPException, Request, Depends
from config import db, logger
from utils.auth import get_current_admin
from datetime import datetime, timezone
import uuid

router = APIRouter()


# ==================== PUBLIC ENDPOINTS ====================

@router.get("/guide/{slug}")
async def get_guide_page(slug: str):
    """Public: fetch a single SEO guide page by slug."""
    page = await db.seo_pages.find_one({"slug": slug, "active": True}, {"_id": 0})
    if not page:
        raise HTTPException(status_code=404, detail="Page non trouvée")
    # Increment view count
    await db.seo_pages.update_one({"slug": slug}, {"$inc": {"views": 1}})
    return page


@router.get("/guides")
async def get_all_guides():
    """Public: list all active guide pages (for hub)."""
    pages = await db.seo_pages.find(
        {"active": True},
        {"_id": 0, "slug": 1, "title": 1, "meta_description": 1, "category": 1, "cta_type": 1}
    ).sort("created_at", -1).to_list(500)
    return pages


@router.post("/guide/{slug}/cta-click")
async def track_cta_click(slug: str):
    """Track a CTA click on a guide page."""
    result = await db.seo_pages.update_one(
        {"slug": slug, "active": True},
        {"$inc": {"cta_clicks": 1}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Page non trouvée")
    return {"success": True}


# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/seo-pages")
async def admin_list_seo_pages(admin: dict = Depends(get_current_admin)):
    """Admin: list all SEO pages."""
    pages = await db.seo_pages.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return pages


@router.post("/admin/seo-pages")
async def admin_create_seo_page(request: Request, admin: dict = Depends(get_current_admin)):
    """Admin: create a new SEO page."""
    body = await request.json()
    slug = body.get("slug", "")
    if not slug:
        raise HTTPException(status_code=400, detail="Slug requis")

    existing = await db.seo_pages.find_one({"slug": slug}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Ce slug existe déjà")

    page = {
        "id": str(uuid.uuid4()),
        "slug": slug,
        "title": body.get("title", ""),
        "meta_description": body.get("meta_description", ""),
        "category": body.get("category", ""),
        "intention": body.get("intention", ""),
        "priority": body.get("priority", "p0"),
        "content": body.get("content", {}),
        "cta_type": body.get("cta_type", "dossier_express"),
        "cta_label": body.get("cta_label", "Analyser mon dossier maintenant"),
        "active": body.get("active", True),
        "views": 0,
        "cta_clicks": 0,
        "conversions": 0,
        "revenue": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.seo_pages.insert_one(page)
    logger.info(f"SEO page created: {slug}")
    return {"success": True, "id": page["id"], "slug": slug}


@router.put("/admin/seo-pages/{slug}")
async def admin_update_seo_page(slug: str, request: Request, admin: dict = Depends(get_current_admin)):
    """Admin: update an SEO page."""
    body = await request.json()
    update = {}
    for field in ["title", "meta_description", "category", "intention", "priority", "content", "cta_type", "cta_label", "active"]:
        if field in body:
            update[field] = body[field]
    if not update:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")
    result = await db.seo_pages.update_one({"slug": slug}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Page non trouvée")
    return {"success": True}


@router.delete("/admin/seo-pages/{slug}")
async def admin_delete_seo_page(slug: str, admin: dict = Depends(get_current_admin)):
    """Admin: delete an SEO page."""
    result = await db.seo_pages.delete_one({"slug": slug})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page non trouvée")
    logger.info(f"SEO page deleted: {slug}")
    return {"success": True}
