from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import asyncio
import uuid

from config import db, logger
from models import (
    ContactRequest, ContactRequestUpdate,
    FAQItem, FAQItemCreate,
    Avis, AvisUpdate,
    TokenResponse, AdminLogin
)
from utils.auth import get_current_admin, verify_password, create_token
from utils.email import create_client_notification

router = APIRouter()


# ==================== AUTH ====================

@router.post("/auth/login", response_model=TokenResponse)
async def admin_login(credentials: AdminLogin):
    admin = await db.admins.find_one({"email": credentials.email}, {"_id": 0})
    if not admin:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    if not verify_password(credentials.password, admin['password_hash']):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    token = create_token(admin['id'], admin['email'], is_admin=True)
    return TokenResponse(access_token=token, admin_name=admin['nom'])

@router.get("/auth/me")
async def get_current_user(admin: dict = Depends(get_current_admin)):
    return {"email": admin.get("email"), "id": admin.get("sub")}


# ==================== CONTACTS ====================

@router.get("/admin/contacts", response_model=List[ContactRequest])
async def get_all_contacts(status: Optional[str] = None, admin: dict = Depends(get_current_admin)):
    query = {}
    if status:
        query["status"] = status
    contacts = await db.contacts.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for contact in contacts:
        if isinstance(contact.get('created_at'), str):
            contact['created_at'] = datetime.fromisoformat(contact['created_at'])
    return contacts

@router.get("/admin/contacts/{contact_id}", response_model=ContactRequest)
async def get_contact(contact_id: str, admin: dict = Depends(get_current_admin)):
    contact = await db.contacts.find_one({"id": contact_id}, {"_id": 0})
    if not contact:
        raise HTTPException(status_code=404, detail="Contact non trouvé")
    if isinstance(contact.get('created_at'), str):
        contact['created_at'] = datetime.fromisoformat(contact['created_at'])
    return contact

@router.patch("/admin/contacts/{contact_id}", response_model=ContactRequest)
async def update_contact(contact_id: str, update_data: ContactRequestUpdate, admin: dict = Depends(get_current_admin)):
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
    result = await db.contacts.update_one({"id": contact_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Contact non trouvé")
    contact = await db.contacts.find_one({"id": contact_id}, {"_id": 0})
    if isinstance(contact.get('created_at'), str):
        contact['created_at'] = datetime.fromisoformat(contact['created_at'])
    return contact

@router.delete("/admin/contacts/{contact_id}")
async def delete_contact(contact_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.contacts.delete_one({"id": contact_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact non trouvé")
    return {"success": True, "message": "Contact supprimé"}

@router.get("/admin/stats")
async def get_stats(admin: dict = Depends(get_current_admin)):
    total = await db.contacts.count_documents({})
    nouveau = await db.contacts.count_documents({"status": "nouveau"})
    en_cours = await db.contacts.count_documents({"status": "en_cours"})
    traite = await db.contacts.count_documents({"status": "traite"})
    return {"total": total, "nouveau": nouveau, "en_cours": en_cours, "traite": traite}


# ==================== ANALYTICS ====================

@router.get("/admin/analytics")
async def get_analytics(period: str = "30d", admin: dict = Depends(get_current_admin)):
    days = 30 if period == "30d" else (7 if period == "7d" else 90)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    total_contacts = await db.contacts.count_documents({})
    total_clients = await db.client_users.count_documents({})
    total_analyses = await db.strategiia_analyses.count_documents({})
    total_dossiers = await db.dossier_express.count_documents({})
    total_forum_users = await db.forum_users.count_documents({})
    total_chatbot = await db.chatbot_sessions.count_documents({})

    revenue_pipeline = [{"$match": {"payment_status": {"$in": ["completed", "paid"]}}}, {"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
    revenue_result = await db.payment_transactions.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0

    pending_pipeline = [{"$match": {"payment_status": {"$in": ["pending", "initiated"]}}}, {"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
    pending_result = await db.payment_transactions.aggregate(pending_pipeline).to_list(1)
    pending_revenue = pending_result[0]["total"] if pending_result else 0

    contacts_all = await db.contacts.find({"created_at": {"$gte": cutoff}}, {"_id": 0, "created_at": 1}).to_list(1000)
    contacts_by_day = {}
    for c in contacts_all:
        day = str(c.get("created_at", ""))[:10]
        if day:
            contacts_by_day[day] = contacts_by_day.get(day, 0) + 1

    payments_all = await db.payment_transactions.find({"created_at": {"$gte": cutoff}}, {"_id": 0, "created_at": 1, "amount": 1, "payment_status": 1}).to_list(1000)
    revenue_by_day = {}
    for p in payments_all:
        day = str(p.get("created_at", ""))[:10]
        if day and p.get("payment_status") in ("completed", "paid"):
            revenue_by_day[day] = revenue_by_day.get(day, 0) + p.get("amount", 0)

    analyses_all = await db.strategiia_analyses.find({"created_at": {"$gte": cutoff}}, {"_id": 0, "created_at": 1}).to_list(1000)
    analyses_by_day = {}
    for a in analyses_all:
        day = str(a.get("created_at", ""))[:10]
        if day:
            analyses_by_day[day] = analyses_by_day.get(day, 0) + 1

    clients_all = await db.client_users.find({"created_at": {"$gte": cutoff}}, {"_id": 0, "created_at": 1}).to_list(1000)
    clients_by_day = {}
    for cl in clients_all:
        day = str(cl.get("created_at", ""))[:10]
        if day:
            clients_by_day[day] = clients_by_day.get(day, 0) + 1

    all_days = set()
    all_days.update(contacts_by_day.keys(), revenue_by_day.keys(), analyses_by_day.keys(), clients_by_day.keys())
    for i in range(days):
        d = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        all_days.add(d)
    time_series = sorted([{"date": d, "contacts": contacts_by_day.get(d, 0), "revenue": revenue_by_day.get(d, 0), "analyses": analyses_by_day.get(d, 0), "clients": clients_by_day.get(d, 0)} for d in all_days], key=lambda x: x["date"])

    package_pipeline = [{"$group": {"_id": "$package_name", "count": {"$sum": 1}, "revenue": {"$sum": "$amount"}}}, {"$sort": {"revenue": -1}}]
    package_dist = await db.payment_transactions.aggregate(package_pipeline).to_list(20)
    packages = [{"name": p["_id"] or "Inconnu", "count": p["count"], "revenue": p["revenue"]} for p in package_dist]

    type_pipeline = [{"$group": {"_id": "$type_dossier", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
    type_dist = await db.strategiia_analyses.aggregate(type_pipeline).to_list(20)
    analyse_types = [{"type": t["_id"] or "Inconnu", "count": t["count"]} for t in type_dist]

    conversion_rate = round((total_clients / total_contacts * 100), 1) if total_contacts > 0 else 0
    calc_count = await db.calculator_usage.count_documents({})

    return {
        "kpis": {"total_contacts": total_contacts, "total_clients": total_clients, "total_analyses": total_analyses, "total_dossiers": total_dossiers, "total_forum_users": total_forum_users, "total_chatbot_sessions": total_chatbot, "total_revenue": total_revenue, "pending_revenue": pending_revenue, "conversion_rate": conversion_rate, "calculator_usage": calc_count},
        "time_series": time_series, "packages": packages, "analyse_types": analyse_types,
    }


# ==================== FAQ ADMIN ====================

@router.post("/admin/faq", response_model=FAQItem)
async def create_faq(input_data: FAQItemCreate, admin: dict = Depends(get_current_admin)):
    faq_obj = FAQItem(**input_data.model_dump())
    doc = faq_obj.model_dump()
    await db.faq.insert_one(doc)
    return faq_obj

@router.delete("/admin/faq/{faq_id}")
async def delete_faq(faq_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.faq.delete_one({"id": faq_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="FAQ non trouvée")
    return {"success": True, "message": "FAQ supprimée"}


# ==================== AVIS ADMIN ====================

@router.get("/admin/avis", response_model=List[Avis])
async def get_all_avis(status: Optional[str] = None, admin: dict = Depends(get_current_admin)):
    query = {}
    if status:
        query["status"] = status
    avis_list = await db.avis.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for avis in avis_list:
        if isinstance(avis.get('created_at'), str):
            avis['created_at'] = datetime.fromisoformat(avis['created_at'])
    return avis_list

@router.get("/admin/avis/stats")
async def get_avis_stats(admin: dict = Depends(get_current_admin)):
    total = await db.avis.count_documents({})
    en_attente = await db.avis.count_documents({"status": "en_attente"})
    publie = await db.avis.count_documents({"status": "publie"})
    rejete = await db.avis.count_documents({"status": "rejete"})
    return {"total": total, "en_attente": en_attente, "publie": publie, "rejete": rejete}

@router.patch("/admin/avis/{avis_id}")
async def update_avis_status(avis_id: str, update_data: AvisUpdate, admin: dict = Depends(get_current_admin)):
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
    result = await db.avis.update_one({"id": avis_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Avis non trouvé")
    return {"success": True, "message": "Avis mis à jour"}

@router.delete("/admin/avis/{avis_id}")
async def delete_avis(avis_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.avis.delete_one({"id": avis_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Avis non trouvé")
    return {"success": True, "message": "Avis supprimé"}


# ==================== REFERRAL STATS ====================

@router.get("/admin/referrals")
async def get_admin_referrals(admin: dict = Depends(get_current_admin)):
    codes = await db.referral_codes.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    uses = await db.referral_uses.find({}, {"_id": 0}).sort("created_at", -1).to_list(5000)
    total_codes = len(codes)
    active_codes = sum(1 for c in codes if c.get("is_active", True))
    total_uses = sum(c.get("uses_count", 0) for c in codes)
    total_discount_given = sum(u.get("discount_applied", 0) for u in uses)
    return {"codes": codes, "recent_uses": uses[:50], "stats": {"total_codes": total_codes, "active_codes": active_codes, "total_uses": total_uses, "total_discount_given": total_discount_given}}


# ==================== CLIENT MANAGEMENT (Admin) ====================

@router.get("/admin/clients")
async def get_admin_clients(admin: dict = Depends(get_current_admin)):
    clients = await db.client_users.find({}, {"_id": 0, "password_hash": 0}).sort("created_at", -1).to_list(500)
    for c in clients:
        c["cases_count"] = await db.client_cases.count_documents({"client_id": c["id"]})
    return clients

@router.post("/admin/clients/{client_id}/cases")
async def create_client_case(client_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    from models import ClientCase
    body = await request.json()
    client_exists = await db.client_users.find_one({"id": client_id}, {"_id": 0})
    if not client_exists:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    case = ClientCase(client_id=client_id, title=body.get("title", ""), description=body.get("description", ""))
    doc = case.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.client_cases.insert_one(doc)
    notif = {"id": str(uuid.uuid4()), "client_id": client_id, "type": "case_created", "title": "Nouveau dossier créé", "message": f"Votre dossier \"{case.title}\" a été créé par votre accompagnant.", "case_id": case.id, "read": False, "created_at": datetime.now(timezone.utc).isoformat()}
    await db.client_notifications.insert_one(notif)
    return {"success": True, "case_id": case.id}

@router.patch("/admin/cases/{case_id}")
async def update_client_case(case_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    case = await db.client_cases.find_one({"id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    notification_message = ""
    if "status" in body:
        update_data["status"] = body["status"]
        status_labels = {"en_cours": "en cours", "en_attente": "en attente", "termine": "terminé"}
        notification_message = f"Le statut de votre dossier \"{case.get('title', '')}\" est passé à : {status_labels.get(body['status'], body['status'])}."
    if "notes" in body:
        update_data["notes"] = body["notes"]
    if "update_message" in body:
        new_update = {"message": body["update_message"], "date": datetime.now(timezone.utc).isoformat(), "author": "Administrateur"}
        await db.client_cases.update_one({"id": case_id}, {"$push": {"updates": new_update}})
        notification_message = f"Nouvelle mise à jour sur votre dossier \"{case.get('title', '')}\" : {body['update_message']}"
    await db.client_cases.update_one({"id": case_id}, {"$set": update_data})
    if notification_message and case.get("client_id"):
        notif = {"id": str(uuid.uuid4()), "client_id": case["client_id"], "type": "case_updated", "title": "Dossier mis à jour", "message": notification_message, "case_id": case_id, "read": False, "created_at": datetime.now(timezone.utc).isoformat()}
        await db.client_notifications.insert_one(notif)
    return {"success": True}


# ==================== PREMIUM ANALYSES ADMIN ====================

@router.get("/admin/premium-analyses")
async def get_premium_analyses(admin: dict = Depends(get_current_admin)):
    items = await db.premium_analyses.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    stats = {"total": len(items), "en_attente": sum(1 for i in items if i.get("status") == "en_attente"), "en_cours": sum(1 for i in items if i.get("status") == "en_cours"), "termine": sum(1 for i in items if i.get("status") == "termine")}
    return {"items": items, "stats": stats}

@router.patch("/admin/premium-analyses/{analysis_id}")
async def update_premium_analysis(analysis_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    new_status = body.get("status", "")
    if new_status not in ("en_attente", "en_cours", "termine"):
        raise HTTPException(status_code=400, detail="Statut invalide")
    update_fields = {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}
    if body.get("notes"):
        update_fields["admin_notes"] = body["notes"]
    result = await db.premium_analyses.update_one({"id": analysis_id}, {"$set": update_fields})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")

    analysis = await db.premium_analyses.find_one({"id": analysis_id}, {"_id": 0})
    if analysis:
        email = analysis.get("email", "")
        type_label = "StrategiIA" if analysis.get("type") == "strategiia" else "Dossier Express"
        client_user = await db.client_users.find_one({"email": email.lower()}, {"_id": 0, "id": 1}) if email else None
        if client_user:
            if new_status == "en_cours":
                asyncio.create_task(create_client_notification(client_id=client_user["id"], notif_type="dossier_in_progress", title="Votre dossier est en cours de traitement", message=f"Notre expert a commencé l'analyse de votre dossier ({type_label}). Vous serez notifié dès que le rapport sera disponible."))
            elif new_status == "termine":
                asyncio.create_task(create_client_notification(client_id=client_user["id"], notif_type="analyse_premium_ready", title="Votre Analyse Premium est prête", message=f"Votre Analyse Premium ({type_label}) a été finalisée par notre expert. Consultez votre rapport dans votre espace client."))
    return {"success": True}

@router.post("/admin/premium-analyses/{analysis_id}/notify")
async def notify_client_premium(analysis_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    analysis = await db.premium_analyses.find_one({"id": analysis_id}, {"_id": 0})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    body = await request.json()
    custom_message = body.get("message", "")
    notif_type = body.get("type", "analyse_premium_ready")
    email = analysis.get("email", "")
    type_label = "StrategiIA" if analysis.get("type") == "strategiia" else "Dossier Express"
    client_user = await db.client_users.find_one({"email": email.lower()}, {"_id": 0, "id": 1}) if email else None
    notif_messages = {
        "analyse_premium_ready": {"title": "Votre Analyse Premium est prête", "message": custom_message or f"Votre Analyse Premium ({type_label}) a été finalisée par notre expert. Consultez votre rapport dans votre espace client."},
        "payment_confirmed": {"title": "Paiement confirmé", "message": custom_message or f"Votre paiement pour l'Analyse Premium ({type_label}) a bien été reçu. Notre expert commence l'analyse de votre dossier."},
        "dossier_in_progress": {"title": "Votre dossier est en cours de traitement", "message": custom_message or f"Notre expert a commencé l'analyse de votre dossier ({type_label}). Vous serez notifié dès que le rapport sera disponible."},
        "report_ready": {"title": "Votre rapport est prêt", "message": custom_message or f"Votre rapport ({type_label}) est maintenant disponible dans votre espace client."}
    }
    notif_config = notif_messages.get(notif_type, notif_messages["analyse_premium_ready"])
    if client_user:
        await create_client_notification(client_id=client_user["id"], notif_type=notif_type, title=notif_config["title"], message=notif_config["message"], send_email=True)
    await db.premium_analyses.update_one({"id": analysis_id}, {"$set": {"client_notified": True, "notified_at": datetime.now(timezone.utc).isoformat(), "notification_type": notif_type}})
    return {"success": True, "client_found": client_user is not None, "email": email}

@router.post("/admin/notify-document-rejected/{client_id}")
async def notify_document_rejected(client_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    custom_message = body.get("message", "")
    message = custom_message or "Un ou plusieurs documents de votre dossier sont illisibles — merci de les renvoyer pour que nous puissions traiter votre analyse."
    await create_client_notification(client_id=client_id, notif_type="document_rejected", title="Documents à renvoyer", message=message, send_email=True)
    return {"success": True}
