from fastapi import APIRouter, HTTPException, Request, Response, Depends
from config import db, logger
from utils.auth import get_current_admin
from datetime import datetime, timezone, timedelta
import uuid
import secrets

router = APIRouter()


# ==================== ADMIN ENDPOINTS ====================

@router.post("/admin/vip-guests")
async def create_vip_guest(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    name = body.get("name", "").strip()
    email = body.get("email", "").strip().lower()
    motif = body.get("motif", "").strip()
    expires_days = body.get("expires_days", 90)

    if not name or not email:
        raise HTTPException(status_code=400, detail="Nom et email requis")

    existing = await db.vip_guests.find_one({"email": email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Un invité avec cet email existe déjà")

    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc).isoformat()
    expires_at = (datetime.now(timezone.utc) + timedelta(days=expires_days)).isoformat()

    guest = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "motif": motif,
        "token": token,
        "active": True,
        "created_at": now,
        "expires_at": expires_at,
        "last_login": None,
        "login_count": 0,
        "pages_visited": [],
    }
    await db.vip_guests.insert_one(guest)
    logger.info(f"VIP guest created: {name} ({email})")

    return {
        "success": True,
        "id": guest["id"],
        "token": token,
        "name": name,
        "email": email,
        "expires_at": expires_at,
    }


@router.get("/admin/vip-guests")
async def list_vip_guests(admin: dict = Depends(get_current_admin)):
    guests = await db.vip_guests.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return guests


@router.put("/admin/vip-guests/{guest_id}/toggle")
async def toggle_vip_guest(guest_id: str, admin: dict = Depends(get_current_admin)):
    guest = await db.vip_guests.find_one({"id": guest_id}, {"_id": 0, "active": 1})
    if not guest:
        raise HTTPException(status_code=404, detail="Invité non trouvé")
    new_status = not guest["active"]
    await db.vip_guests.update_one({"id": guest_id}, {"$set": {"active": new_status}})
    return {"success": True, "active": new_status}


@router.delete("/admin/vip-guests/{guest_id}")
async def delete_vip_guest(guest_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.vip_guests.delete_one({"id": guest_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Invité non trouvé")
    await db.vip_sessions.delete_many({"guest_id": guest_id})
    return {"success": True}


# ==================== PUBLIC VIP ENDPOINTS ====================

@router.post("/vip/verify")
async def verify_vip_access(request: Request, response: Response):
    body = await request.json()
    token = body.get("token", "").strip()
    email = body.get("email", "").strip().lower()

    if not token or not email:
        raise HTTPException(status_code=400, detail="Token et email requis")

    guest = await db.vip_guests.find_one(
        {"token": token, "email": email, "active": True},
        {"_id": 0}
    )
    if not guest:
        raise HTTPException(status_code=403, detail="Accès refusé — token invalide, email incorrect ou accès désactivé")

    now = datetime.now(timezone.utc)
    if guest.get("expires_at"):
        expires = datetime.fromisoformat(guest["expires_at"].replace("Z", "+00:00")) if isinstance(guest["expires_at"], str) else guest["expires_at"]
        if now > expires:
            raise HTTPException(status_code=403, detail="Accès expiré — veuillez contacter Stratégie Expertise Santé")

    session_id = secrets.token_urlsafe(32)
    await db.vip_sessions.insert_one({
        "session_id": session_id,
        "guest_id": guest["id"],
        "guest_name": guest["name"],
        "guest_email": guest["email"],
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(hours=24)).isoformat(),
    })

    await db.vip_guests.update_one(
        {"id": guest["id"]},
        {"$set": {"last_login": now.isoformat()}, "$inc": {"login_count": 1}}
    )

    response.set_cookie(
        key="vip_session",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=86400,
        path="/",
    )

    logger.info(f"VIP login: {guest['name']} ({guest['email']})")
    return {"success": True, "name": guest["name"], "guest_id": guest["id"]}


@router.get("/vip/session")
async def check_vip_session(request: Request):
    session_id = request.cookies.get("vip_session")
    if not session_id:
        return {"active": False}

    session = await db.vip_sessions.find_one({"session_id": session_id}, {"_id": 0})
    if not session:
        return {"active": False}

    now = datetime.now(timezone.utc)
    if session.get("expires_at"):
        expires = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00")) if isinstance(session["expires_at"], str) else session["expires_at"]
        if now > expires:
            await db.vip_sessions.delete_one({"session_id": session_id})
            return {"active": False}

    guest = await db.vip_guests.find_one({"id": session["guest_id"]}, {"_id": 0, "active": 1, "expires_at": 1})
    if not guest or not guest.get("active"):
        return {"active": False}

    return {
        "active": True,
        "name": session["guest_name"],
        "email": session["guest_email"],
        "guest_id": session["guest_id"],
    }


@router.post("/vip/logout")
async def vip_logout(request: Request, response: Response):
    session_id = request.cookies.get("vip_session")
    if session_id:
        await db.vip_sessions.delete_one({"session_id": session_id})
    response.delete_cookie("vip_session", path="/")
    return {"success": True}


@router.post("/vip/track")
async def track_vip_page(request: Request):
    session_id = request.cookies.get("vip_session")
    if not session_id:
        return {"success": False}

    session = await db.vip_sessions.find_one({"session_id": session_id}, {"_id": 0, "guest_id": 1})
    if not session:
        return {"success": False}

    body = await request.json()
    page = body.get("page", "")
    if page:
        now = datetime.now(timezone.utc).isoformat()
        await db.vip_guests.update_one(
            {"id": session["guest_id"]},
            {"$push": {"pages_visited": {"page": page, "at": now}}}
        )
    return {"success": True}



@router.post("/alerte-urgente/vip")
async def create_vip_urgent_alert(request: Request):
    session_id = request.cookies.get("vip_session")
    if not session_id:
        raise HTTPException(status_code=403, detail="Accès VIP requis")
    session = await db.vip_sessions.find_one({"session_id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=403, detail="Session VIP invalide")

    body = await request.json()
    alert = {
        "id": str(uuid.uuid4()),
        "nom": body.get("nom", ""),
        "telephone": body.get("telephone", ""),
        "email": body.get("email", ""),
        "message": body.get("message", ""),
        "formule": body.get("formule", "2h"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "confirmed",
        "payment_status": "vip_bypass",
        "traite": False,
        "vip_guest": session["guest_name"],
    }
    await db.urgent_alerts.insert_one(alert)
    logger.info(f"VIP urgent alert from {session['guest_name']}")
    return {"success": True}
