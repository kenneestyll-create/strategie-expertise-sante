from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import Response
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import asyncio
import uuid
import os

try:
    import resend
except ImportError:
    pass

from config import db, logger, limiter, STRIPE_API_KEY, STRIPE_MODE, PAYPAL_CLIENT_ID, PAYPAL_MODE, RESEND_AVAILABLE, SENDER_EMAIL
from models import (
    ContactRequest, ContactRequestUpdate,
    FAQItem, FAQItemCreate,
    Avis, AvisUpdate,
    TokenResponse, AdminLogin
)
from utils.auth import get_current_admin, verify_password, create_token
from utils.email import create_client_notification

router = APIRouter()


# ==================== COMPTEUR HERO ====================

@router.get("/admin/compteur")
async def get_compteur(admin: dict = Depends(get_current_admin)):
    counter = await db.visitor_counter.find_one({"id": "visitor_counter"}, {"_id": 0})
    return {"count": counter.get("count", 0) if counter else 0}

@router.put("/admin/compteur")
async def set_compteur(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    new_count = int(body.get("count", 0))
    await db.visitor_counter.update_one(
        {"id": "visitor_counter"},
        {"$set": {"count": new_count, "last_updated": datetime.now(timezone.utc).isoformat(), "updated_by": "admin"}},
        upsert=True
    )
    return {"success": True, "count": new_count}


# ==================== AUTH ====================

@router.post("/auth/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def admin_login(request: Request, credentials: AdminLogin):
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
async def get_all_contacts(status: Optional[str] = None, via: Optional[str] = None, source: Optional[str] = None, admin: dict = Depends(get_current_admin)):
    query = {}
    if status:
        query["status"] = status
    if via:
        query["tracking_via"] = via
    if source:
        query["tracking_source"] = source
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
    converti = await db.contacts.count_documents({"status": "converti"})
    revenue_agg = await db.contacts.aggregate([
        {"$match": {"status": "converti", "conversion_montant": {"$gt": 0}}},
        {"$group": {"_id": None, "total": {"$sum": "$conversion_montant"}}},
    ]).to_list(1)
    total_revenue = revenue_agg[0]["total"] if revenue_agg else 0
    return {"total": total, "nouveau": nouveau, "en_cours": en_cours, "traite": traite, "converti": converti, "total_revenue": total_revenue}


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

    # P3: Service utilization metrics
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    analyses_this_month = await db.strategiia_analyses.count_documents({"created_at": {"$gte": month_start}})
    premium_analyses_total = await db.strategiia_analyses.count_documents({"is_premium": True})
    premium_this_month = await db.strategiia_analyses.count_documents({"is_premium": True, "created_at": {"$gte": month_start}})
    dossiers_this_month = await db.dossier_express.count_documents({"created_at": {"$gte": month_start}})
    active_dossiers = await db.premium_analyses.count_documents({"status": {"$in": ["en_attente", "en_cours"]}})

    # Documents stats
    total_documents = await db.client_documents.count_documents({})
    pending_documents = await db.client_documents.count_documents({"status": "en_attente"})

    # Dossier express by day
    dossiers_all = await db.dossier_express.find({"created_at": {"$gte": cutoff}}, {"_id": 0, "created_at": 1}).to_list(1000)
    dossiers_by_day = {}
    for de in dossiers_all:
        day = str(de.get("created_at", ""))[:10]
        if day:
            dossiers_by_day[day] = dossiers_by_day.get(day, 0) + 1
    for ts in time_series:
        ts["dossiers"] = dossiers_by_day.get(ts["date"], 0)

    service_utilization = {
        "strategiia": {"total": total_analyses, "this_month": analyses_this_month, "label": "StratégiIA"},
        "dossier_express": {"total": total_dossiers, "this_month": dossiers_this_month, "label": "Dossier Express IA"},
        "premium": {"total": premium_analyses_total, "this_month": premium_this_month, "label": "Analyses Premium"},
        "chatbot": {"total": total_chatbot, "this_month": 0, "label": "Chatbot IA"},
    }

    return {
        "kpis": {"total_contacts": total_contacts, "total_clients": total_clients, "total_analyses": total_analyses, "total_dossiers": total_dossiers, "total_forum_users": total_forum_users, "total_chatbot_sessions": total_chatbot, "total_revenue": total_revenue, "pending_revenue": pending_revenue, "conversion_rate": conversion_rate, "calculator_usage": calc_count, "analyses_this_month": analyses_this_month, "dossiers_this_month": dossiers_this_month, "active_dossiers": active_dossiers, "total_documents": total_documents, "pending_documents": pending_documents},
        "time_series": time_series, "packages": packages, "analyse_types": analyse_types, "service_utilization": service_utilization,
        "payment_config": {"stripe_mode": STRIPE_MODE, "paypal_mode": PAYPAL_MODE, "stripe_configured": bool(STRIPE_API_KEY), "paypal_configured": bool(PAYPAL_CLIENT_ID)},
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
        if 'temoignage' in avis and 'commentaire' not in avis:
            avis['commentaire'] = avis.pop('temoignage')
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
    # Send push notification for new case
    try:
        from utils.push import send_push_to_client
        asyncio.create_task(send_push_to_client(db, client_id, title="Nouveau dossier créé", body=f"Votre dossier \"{case.title}\" a été créé par votre accompagnant.", url="/espace-client", tag="case_created"))
    except Exception:
        pass
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
        # Send push notification for case update
        try:
            from utils.push import send_push_to_client
            asyncio.create_task(send_push_to_client(db, case["client_id"], title="Dossier mis à jour", body=notification_message, url="/espace-client", tag="case_updated"))
        except Exception:
            pass
    return {"success": True}


# ==================== PREMIUM ANALYSES ADMIN ====================

@router.get("/admin/premium-analyses")
async def get_premium_analyses(admin: dict = Depends(get_current_admin)):
    items = await db.premium_analyses.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    stats = {"total": len(items), "en_attente": sum(1 for i in items if i.get("status") == "en_attente"), "en_cours": sum(1 for i in items if i.get("status") == "en_cours"), "valide": sum(1 for i in items if i.get("status") == "valide"), "envoye": sum(1 for i in items if i.get("status") == "envoye"), "termine": sum(1 for i in items if i.get("status") in ("termine", "envoye"))}
    return {"items": items, "stats": stats}

@router.patch("/admin/premium-analyses/{analysis_id}")
async def update_premium_analysis(analysis_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    new_status = body.get("status", "")
    if new_status not in ("en_attente", "en_cours", "valide", "envoye", "termine"):
        raise HTTPException(status_code=400, detail="Statut invalide")
    update_fields = {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}
    if body.get("notes"):
        update_fields["admin_notes"] = body["notes"]
    if body.get("reviewed_analysis"):
        update_fields["reviewed_analysis"] = body["reviewed_analysis"]
        update_fields["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.premium_analyses.update_one({"id": analysis_id}, {"$set": update_fields})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")

    analysis = await db.premium_analyses.find_one({"id": analysis_id}, {"_id": 0})
    if analysis:
        email = analysis.get("email", "")
        type_label = "StrategiIA" if analysis.get("type") == "strategiia" else "Dossier Express IA"
        client_user = await db.client_users.find_one({"email": email.lower()}, {"_id": 0, "id": 1}) if email else None
        if client_user:
            if new_status == "en_cours":
                asyncio.create_task(create_client_notification(client_id=client_user["id"], notif_type="dossier_in_progress", title="Votre dossier est en cours de traitement", message=f"Notre expert a commencé l'analyse de votre dossier ({type_label}). Vous serez notifié dès que le rapport sera disponible."))
            elif new_status == "valide":
                asyncio.create_task(create_client_notification(client_id=client_user["id"], notif_type="dossier_validated", title="Votre relecture expert est finalisée", message=f"La relecture expert de votre dossier ({type_label}) est terminée. Votre document finalisé vous sera transmis très prochainement."))
            elif new_status in ("envoye", "termine"):
                asyncio.create_task(create_client_notification(client_id=client_user["id"], notif_type="analyse_premium_ready", title="Votre rapport expert est prêt", message=f"Votre rapport ({type_label}) relu et finalisé par notre expert est maintenant disponible. Consultez votre espace client."))
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
    type_label = "StrategiIA" if analysis.get("type") == "strategiia" else "Dossier Express IA"
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


@router.get("/admin/premium-analyses/{analysis_id}/full-content")
async def get_premium_analysis_full_content(analysis_id: str, admin: dict = Depends(get_current_admin)):
    """Fetch full analysis content for admin review. Pulls from the correct collection based on type."""
    analysis = await db.premium_analyses.find_one({"id": analysis_id}, {"_id": 0})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    full_text = analysis.get("reviewed_analysis", "")
    source_data = {}
    if analysis.get("type") == "dossier_express":
        # Match by dossier_id (reliable) or fallback to email (legacy)
        match_filter = {"id": analysis["dossier_id"]} if analysis.get("dossier_id") else {"email": analysis.get("email", "")}
        dossier = await db.dossier_express.find_one(match_filter, {"_id": 0, "documents_text": 0})
        if not dossier and analysis.get("dossier_id"):
            # Fallback to email if dossier_id match failed
            dossier = await db.dossier_express.find_one({"email": analysis.get("email", "")}, {"_id": 0, "documents_text": 0})
        if dossier:
            full_text = full_text or dossier.get("analysis", "")
            source_data = {"situation": dossier.get("situation", ""), "type_dossier": dossier.get("type_dossier", ""), "regime": dossier.get("regime", ""), "name": dossier.get("name", ""), "dossier_status": dossier.get("status", ""), "dossier_id": dossier.get("id", "")}
    else:
        # StrategiIA: lookup via job_id (reliable) then fallback to email
        if analysis.get("analysis"):
            full_text = full_text or analysis["analysis"]
        strat = None
        if analysis.get("job_id"):
            strat = await db.strategiia_analyses.find_one({"job_id": analysis["job_id"]}, {"_id": 0})
        if not strat:
            strat = await db.strategiia_analyses.find_one(
                {"email": analysis.get("email", ""), "is_premium": True},
                {"_id": 0},
                sort=[("created_at", -1)]
            )
        if strat:
            full_text = full_text or strat.get("analysis", "") or ""
            source_data = {"type_dossier": strat.get("type_dossier", ""), "regime": strat.get("regime", ""), "situation": strat.get("situation", ""), "name": strat.get("name", "")}
        if not full_text and analysis.get("context"):
            full_text = analysis["context"]
    return {"id": analysis_id, "type": analysis.get("type"), "full_text": full_text, "source_data": source_data, "email": analysis.get("email", ""), "status": analysis.get("status", ""), "admin_notes": analysis.get("admin_notes", "")}



@router.get("/admin/dossier-express/{dossier_id}/analysis")
async def get_dossier_express_analysis(dossier_id: str, admin: dict = Depends(get_current_admin)):
    """Fetch analysis content for a specific dossier express by its ID."""
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0, "documents_text": 0})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    return {
        "id": dossier_id,
        "email": dossier.get("email", ""),
        "name": dossier.get("name", ""),
        "status": dossier.get("status", ""),
        "analysis": dossier.get("analysis", ""),
        "situation": dossier.get("situation", ""),
        "type_dossier": dossier.get("type_dossier", ""),
        "regime": dossier.get("regime", ""),
        "premium_pdf": dossier.get("premium_pdf", False),
        "document_details": dossier.get("document_details", []),
        "original_documents": dossier.get("original_documents", []),
        "human_reviewed": dossier.get("human_reviewed", False),
        "reviewed_at": dossier.get("reviewed_at", ""),
        "admin_notes": dossier.get("admin_notes", ""),
        "created_at": dossier.get("created_at", ""),
        "completed_at": dossier.get("completed_at", ""),
    }


@router.get("/admin/dossier-express/{dossier_id}/preview-pdf")
async def preview_dossier_express_pdf(dossier_id: str, admin: dict = Depends(get_current_admin)):
    """Generate and return the PDF for admin preview/download."""
    from utils.pdf import generate_dossier_pdf
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    analysis = dossier.get("analysis", "")
    if not analysis:
        raise HTTPException(status_code=400, detail="Aucune analyse disponible pour ce dossier")
    pdf_bytes = generate_dossier_pdf(
        name=dossier.get("name", ""),
        email=dossier.get("email", ""),
        type_dossier=dossier.get("type_dossier", ""),
        regime=dossier.get("regime", ""),
        analysis=analysis,
        premium_pdf=dossier.get("premium_pdf", False),
        document_details=dossier.get("document_details", []),
    )
    safe_name = dossier.get("name", "dossier").replace(" ", "_")[:30]
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="Rapport_DossierExpress_{safe_name}_{dossier_id[:8]}.pdf"'}
    )


@router.get("/admin/strategiia/{analysis_id}/preview-pdf")
async def preview_strategiia_pdf(analysis_id: str, admin: dict = Depends(get_current_admin)):
    """Generate and return the StrategiIA PDF for admin preview/download."""
    from utils.pdf import generate_secured_pdf
    pa = await db.premium_analyses.find_one({"id": analysis_id}, {"_id": 0})
    if not pa:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    analysis_text = pa.get("reviewed_analysis") or pa.get("analysis", "")
    if not analysis_text:
        strat = None
        if pa.get("job_id"):
            strat = await db.strategiia_analyses.find_one({"job_id": pa["job_id"]}, {"_id": 0, "analysis": 1})
        if not strat:
            strat = await db.strategiia_analyses.find_one(
                {"email": pa.get("email", ""), "is_premium": True},
                {"_id": 0, "analysis": 1},
                sort=[("created_at", -1)]
            )
        if strat:
            analysis_text = strat.get("analysis", "")
    if not analysis_text and pa.get("context"):
        analysis_text = pa["context"]
    if not analysis_text:
        raise HTTPException(status_code=400, detail="Aucune analyse disponible pour ce dossier")
    strat_data = None
    if pa.get("job_id"):
        strat_data = await db.strategiia_analyses.find_one({"job_id": pa["job_id"]}, {"_id": 0})
    type_dossier = (strat_data or {}).get("type_dossier", pa.get("type_dossier", ""))
    regime = (strat_data or {}).get("regime", pa.get("regime", ""))
    name = pa.get("name", pa.get("email", "Client"))
    pdf_bytes = generate_secured_pdf(
        analysis=analysis_text,
        report_type="StrategiIA",
        name=name,
        type_dossier=type_dossier,
        regime=regime,
        with_watermark=not pa.get("premium_pdf", False),
        relecture_expert=pa.get("relecture_expert_required", False),
    )
    safe_name = name.replace(" ", "_")[:30]
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="Rapport_StrategiIA_{safe_name}_{analysis_id[:8]}.pdf"'}
    )


# ==================== ADMIN: HUMAN REVIEW WORKFLOW ====================

@router.get("/admin/dossier-express/{dossier_id}/original-documents")
async def get_dossier_original_documents(dossier_id: str, admin: dict = Depends(get_current_admin)):
    """List original documents stored for a dossier (for admin download)."""
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0, "original_documents": 1, "document_details": 1})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    return {
        "original_documents": dossier.get("original_documents", []),
        "document_details": dossier.get("document_details", []),
    }


@router.get("/admin/dossier-express/{dossier_id}/documents/{file_id}/download")
async def download_dossier_document(dossier_id: str, file_id: str, admin: dict = Depends(get_current_admin)):
    """Download an original client document from Object Storage."""
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0, "original_documents": 1})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    original_docs = dossier.get("original_documents", [])
    target_doc = None
    for doc in original_docs:
        if doc.get("file_id") == file_id:
            target_doc = doc
            break
    if not target_doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    storage_path = target_doc.get("storage_path", "")
    if not storage_path:
        raise HTTPException(status_code=404, detail="Chemin de stockage manquant")
    try:
        from utils.storage import download_file
        content, content_type = download_file(storage_path)
        filename = target_doc.get("original_filename", "document")
        return Response(
            content=content,
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        logger.error(f"Failed to download file {file_id} for dossier {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail="Impossible de télécharger le fichier")


@router.put("/admin/dossier-express/{dossier_id}/analysis")
async def update_dossier_analysis(dossier_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    """Admin edits the AI analysis text (human review)."""
    body = await request.json()
    new_analysis = body.get("analysis", "")
    admin_notes = body.get("admin_notes", "")
    if not new_analysis.strip():
        raise HTTPException(status_code=400, detail="L'analyse ne peut pas être vide")
    update_fields = {
        "analysis": new_analysis,
        "human_reviewed": True,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_by": admin.get("email", "admin"),
    }
    if admin_notes:
        update_fields["admin_notes"] = admin_notes
    result = await db.dossier_express.update_one({"id": dossier_id}, {"$set": update_fields})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    logger.info(f"Admin {admin.get('email')} updated analysis for dossier {dossier_id}")
    return {"success": True, "message": "Analyse mise à jour"}


@router.post("/admin/dossier-express/{dossier_id}/regenerate-pdf")
async def regenerate_dossier_pdf(dossier_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    """Regenerate the PDF with the edited analysis and optionally send it to the client."""
    from utils.pdf import generate_dossier_pdf, generate_secured_pdf
    body = await request.json()
    send_email = body.get("send_email", False)

    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")

    analysis = dossier.get("analysis", "")
    if not analysis:
        raise HTTPException(status_code=400, detail="Aucune analyse disponible")

    # Generate the premium PDF with the expert review marker
    pdf_bytes = generate_secured_pdf(
        analysis=analysis,
        report_type="Dossier Express IA",
        name=dossier.get("name", ""),
        type_dossier=dossier.get("type_dossier", ""),
        regime=dossier.get("regime", ""),
        with_watermark=not dossier.get("premium_pdf", False),
        relecture_expert=dossier.get("human_reviewed", False),
    )

    # Upload the regenerated PDF to Object Storage
    pdf_stored = False
    try:
        from utils.storage import upload_file
        safe_name = dossier.get("name", "dossier").replace(" ", "_")[:30]
        pdf_result = upload_file(
            "dossier-pdfs",
            f"Rapport_Expert_{safe_name}_{dossier_id[:8]}.pdf",
            pdf_bytes,
            "application/pdf"
        )
        await db.dossier_express.update_one({"id": dossier_id}, {"$set": {
            "regenerated_pdf_path": pdf_result.get("storage_path", ""),
            "regenerated_at": datetime.now(timezone.utc).isoformat(),
        }})
        pdf_stored = True
    except Exception as e:
        logger.warning(f"Failed to store regenerated PDF: {e}")

    # Send email if requested
    email_sent = False
    if send_email:
        email = dossier.get("email", "")
        name = dossier.get("name", email)
        if RESEND_AVAILABLE and os.environ.get('RESEND_API_KEY') and email:
            import base64 as b64
            pdf_b64 = b64.b64encode(pdf_bytes).decode()
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [email],
                    "subject": "Votre rapport Dossier Express IA — Version expert finalisée",
                    "html": f"""<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
                        <div style="background:#0a0a08;color:#fff;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
                            <h2 style="margin:0;color:#C9A84C;">Votre rapport expert est prêt</h2>
                        </div>
                        <div style="background:#FAF8F3;padding:20px;border-radius:0 0 8px 8px;border:1px solid #E5E0D6;">
                            <p>Bonjour {name},</p>
                            <p>Votre rapport <strong>Dossier Express IA</strong> a été relu et finalisé par notre expert.</p>
                            <p>Vous trouverez votre document en pièce jointe.</p>
                            <p style="color:#666;font-size:13px;margin-top:20px;">Ce document a fait l'objet d'une relecture humaine approfondie.</p>
                            <hr style="border:1px solid #E5E0D6;">
                            <p style="color:#C9A84C;font-weight:bold;font-style:italic;">Vous n'êtes plus seul(e) face à votre situation.<br/>Désormais, Stratégie & Expertise Santé devient votre bouclier.</p>
                        </div>
                    </body></html>""",
                    "attachments": [{"filename": "rapport-expert-dossier-express.pdf", "content": pdf_b64}]
                })
                email_sent = True
                logger.info(f"Regenerated PDF sent to {email} for dossier {dossier_id}")
            except Exception as e:
                logger.error(f"Failed to send regenerated PDF email: {e}")

        # Update dossier status
        await db.dossier_express.update_one({"id": dossier_id}, {"$set": {
            "expert_email_sent": email_sent,
            "expert_sent_at": datetime.now(timezone.utc).isoformat(),
        }})

        # Notify client via in-app notification
        client_user = await db.client_users.find_one({"email": email.lower()}, {"_id": 0, "id": 1}) if email else None
        if client_user:
            await create_client_notification(
                client_id=client_user["id"],
                notif_type="report_ready",
                title="Votre rapport expert est prêt",
                message="Votre rapport Dossier Express IA relu et finalisé par notre expert vous a été envoyé par email.",
                send_email=False
            )

    return {"success": True, "pdf_stored": pdf_stored, "email_sent": email_sent}
async def send_reviewed_document(analysis_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    """Admin sends the final reviewed document to the client — triggers actual delivery."""
    analysis = await db.premium_analyses.find_one({"id": analysis_id}, {"_id": 0})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    body = await request.json()
    reviewed_text = body.get("reviewed_analysis", analysis.get("reviewed_analysis", ""))
    if not reviewed_text:
        raise HTTPException(status_code=400, detail="Aucune analyse relue à envoyer")
    email = analysis.get("email", "")
    analysis_type = analysis.get("type", "strategiia")
    type_label = "StrategiIA" if analysis_type == "strategiia" else "Dossier Express IA"
    name = analysis.get("name", email)
    type_dossier = ""
    regime = ""
    if analysis_type == "dossier_express":
        match_filter = {"id": analysis["dossier_id"]} if analysis.get("dossier_id") else {"email": email}
        dossier = await db.dossier_express.find_one(match_filter, {"_id": 0, "type_dossier": 1, "regime": 1, "name": 1})
        if dossier:
            type_dossier = dossier.get("type_dossier", "")
            regime = dossier.get("regime", "")
            name = dossier.get("name", name)
    else:
        type_dossier = analysis.get("context", "").split(" - ")[0] if analysis.get("context") else ""
    premium_pdf = analysis.get("premium_pdf", True)
    report_type = "Dossier Express IA" if analysis_type == "dossier_express" else "StrategiIA"
    # Generate the reviewed PDF with expert marker
    from utils.pdf import generate_secured_pdf
    pdf_bytes = generate_secured_pdf(
        analysis=reviewed_text, report_type=report_type, name=name,
        type_dossier=type_dossier, regime=regime, with_watermark=not premium_pdf,
        relecture_expert=True
    )
    # Send the PDF via email to the client
    email_sent = False
    if RESEND_AVAILABLE and os.environ.get('RESEND_API_KEY') and email:
        import base64 as b64
        pdf_b64 = b64.b64encode(pdf_bytes).decode()
        try:
            await asyncio.to_thread(resend.Emails.send, {
                "from": SENDER_EMAIL,
                "to": [email],
                "subject": f"Votre rapport {type_label} — Version expert finalisée",
                "html": f"""<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
                    <div style="background:#1a1a2e;color:#fff;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
                        <h2 style="margin:0;color:#d4a44a;">Votre rapport expert est prêt</h2>
                    </div>
                    <div style="background:#F9F7F2;padding:20px;border-radius:0 0 8px 8px;border:1px solid #E5E0D6;">
                        <p>Bonjour,</p>
                        <p>Votre rapport <strong>{type_label}</strong> a été relu et finalisé par notre expert dans le cadre de votre option <strong>Relecture expert personnalisée</strong>.</p>
                        <p>Vous trouverez votre document en pièce jointe.</p>
                        <p style="color:#666;font-size:13px;margin-top:20px;">Ce document a fait l'objet d'une relecture humaine approfondie. Il constitue une version enrichie et validée de votre analyse initiale.</p>
                        <hr style="border:1px solid #E5E0D6;">
                        <p style="color:#d4a44a;font-weight:bold;font-style:italic;">Vous n'êtes plus seul(e) face à votre situation.<br/>Désormais, Stratégie & Expertise Santé devient votre bouclier.</p>
                    </div>
                </body></html>""",
                "attachments": [{"filename": f"rapport-expert-{type_label.lower().replace(' ', '-')}.pdf", "content": pdf_b64}]
            })
            email_sent = True
            logger.info(f"Reviewed document sent to {email} for analysis {analysis_id}")
        except Exception as e:
            logger.error(f"Failed to send reviewed document: {e}")
    # Update status
    await db.premium_analyses.update_one({"id": analysis_id}, {"$set": {
        "status": "envoye", "reviewed_analysis": reviewed_text,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "email_sent": email_sent, "updated_at": datetime.now(timezone.utc).isoformat()
    }})
    # Client notification
    client_user = await db.client_users.find_one({"email": email.lower()}, {"_id": 0, "id": 1}) if email else None
    if client_user:
        await create_client_notification(client_id=client_user["id"], notif_type="report_ready", title="Votre rapport expert est prêt", message=f"Votre rapport ({type_label}) relu et finalisé par notre expert vous a été envoyé par email.", send_email=False)
    return {"success": True, "email_sent": email_sent, "email": email}



@router.delete("/admin/premium-analyses/{analysis_id}")
async def delete_premium_analysis(analysis_id: str, admin: dict = Depends(get_current_admin)):
    """Delete a premium analysis entry and optionally its linked dossier."""
    analysis = await db.premium_analyses.find_one({"id": analysis_id}, {"_id": 0})
    if not analysis:
        raise HTTPException(status_code=404, detail="Entrée non trouvée")
    # Delete linked dossier_express if exists
    dossier_id = analysis.get("dossier_id")
    if dossier_id:
        await db.dossier_express.delete_one({"id": dossier_id})
    await db.premium_analyses.delete_one({"id": analysis_id})
    logger.info(f"Admin deleted premium_analysis {analysis_id} (dossier: {dossier_id or 'none'})")
    return {"success": True, "deleted_dossier": bool(dossier_id)}


@router.post("/admin/notify-document-rejected/{client_id}")
async def notify_document_rejected(client_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    custom_message = body.get("message", "")
    message = custom_message or "Un ou plusieurs documents de votre dossier sont illisibles — merci de les renvoyer pour que nous puissions traiter votre analyse."
    await create_client_notification(client_id=client_id, notif_type="document_rejected", title="Documents à renvoyer", message=message, send_email=True)
    return {"success": True}


@router.patch("/admin/documents/{doc_id}/status")
async def admin_update_document_status(doc_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    new_status = body.get("status", "")
    if new_status not in ("en_attente", "valide", "illisible", "corrige"):
        raise HTTPException(status_code=400, detail="Statut invalide")

    doc = await db.client_documents.find_one({"id": doc_id}, {"_id": 0, "client_id": 1, "filename": 1, "status": 1})
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")

    await db.client_documents.update_one(
        {"id": doc_id},
        {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    client_id = doc.get("client_id")
    filename = doc.get("filename", "document")
    if client_id and new_status == "valide":
        await create_client_notification(
            client_id=client_id, notif_type="document_validated",
            title="Document validé",
            message=f"Votre document \"{filename}\" a été vérifié et validé par notre équipe.",
            send_email=True
        )
    elif client_id and new_status == "illisible":
        await create_client_notification(
            client_id=client_id, notif_type="document_rejected",
            title="Document illisible",
            message=f"Votre document \"{filename}\" est illisible. Merci de le renvoyer en meilleure qualité.",
            send_email=True
        )

    return {"success": True, "new_status": new_status}

@router.get("/admin/documents")
async def admin_list_all_documents(admin: dict = Depends(get_current_admin), status: str = None, client_id: str = None):
    query = {}
    if status:
        query["status"] = status
    if client_id:
        query["client_id"] = client_id
    docs = await db.client_documents.find(query, {"_id": 0, "file_data": 0}).sort("created_at", -1).to_list(500)
    stats = {
        "total": len(docs),
        "en_attente": sum(1 for d in docs if d.get("status") == "en_attente"),
        "valide": sum(1 for d in docs if d.get("status") == "valide"),
        "illisible": sum(1 for d in docs if d.get("status") == "illisible"),
    }
    return {"documents": docs, "stats": stats}


@router.get("/admin/email/status")
async def admin_email_status(admin: dict = Depends(get_current_admin)):
    import importlib
    resend_installed = importlib.util.find_spec("resend") is not None
    api_key = os.environ.get("RESEND_API_KEY", "")
    return {
        "resend_installed": resend_installed,
        "api_key_configured": bool(api_key),
        "api_key_preview": (api_key[:6] + "..." + api_key[-4:]) if len(api_key) > 10 else ("Oui" if api_key else "Non"),
        "sender_email": os.environ.get("SENDER_EMAIL", "non configuré"),
        "notification_email": os.environ.get("NOTIFICATION_EMAIL", "non configuré"),
        "domain_verified": not os.environ.get("SENDER_EMAIL", "").endswith("resend.dev"),
    }

@router.post("/admin/email/test")
async def admin_email_test(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    email = body.get("email", "")
    if not email:
        raise HTTPException(status_code=400, detail="Email requis")
    try:
        import resend
        resend.api_key = os.environ.get("RESEND_API_KEY", "")
        params = {
            "from": os.environ.get("SENDER_EMAIL", "onboarding@resend.dev"),
            "to": [email],
            "subject": "Test email - Stratégie & Expertise Santé",
            "html": "<h2>Test réussi</h2><p>Ceci est un email de test envoyé depuis le panneau d'administration.</p>"
        }
        await asyncio.to_thread(resend.Emails.send, params)
        return {"success": True, "message": f"Email test envoyé à {email}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ==================== COMPLETENESS NOTIFICATIONS HISTORY ====================

@router.get("/admin/completeness-notifications")
async def get_completeness_notifications(admin: dict = Depends(get_current_admin), limit: int = 50, skip: int = 0):
    notifs = await db.completeness_notifications.find({}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.completeness_notifications.count_documents({})
    stats = {
        "total": total,
        "sent": await db.completeness_notifications.count_documents({"status": "sent"}),
        "failed": await db.completeness_notifications.count_documents({"status": "failed"}),
        "skipped": await db.completeness_notifications.count_documents({"status": "skipped"}),
    }
    by_threshold = {}
    for t in [50, 80, 100]:
        by_threshold[str(t)] = await db.completeness_notifications.count_documents({"threshold_pct": t})
    return {"notifications": notifs, "total": total, "stats": stats, "by_threshold": by_threshold}


# ==================== INACTIVITY REMINDERS ====================

@router.post("/admin/relance-inactivite/run")
async def run_inactivity_reminders_endpoint(admin: dict = Depends(get_current_admin)):
    from utils.email import run_inactivity_reminders
    results = await run_inactivity_reminders()
    return {"success": True, "results": results}

@router.get("/admin/relance-inactivite/history")
async def get_inactivity_reminders(admin: dict = Depends(get_current_admin), limit: int = 50, skip: int = 0):
    reminders = await db.inactivity_reminders.find({}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.inactivity_reminders.count_documents({})
    stats = {
        "total": total,
        "sent": await db.inactivity_reminders.count_documents({"status": "sent"}),
        "failed": await db.inactivity_reminders.count_documents({"status": "failed"}),
        "skipped": await db.inactivity_reminders.count_documents({"status": "skipped"}),
    }
    by_level = {}
    for lvl in [1, 2, 3]:
        by_level[str(lvl)] = await db.inactivity_reminders.count_documents({"level": lvl})
    return {"reminders": reminders, "total": total, "stats": stats, "by_level": by_level}

@router.post("/admin/relance-inactivite/toggle-pause")
async def toggle_client_reminder_pause(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    client_id = body.get("client_id")
    paused = body.get("paused", True)
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id requis")
    await db.client_users.update_one({"id": client_id}, {"$set": {"reminders_paused": paused}})
    return {"success": True, "client_id": client_id, "reminders_paused": paused}


# ==================== CRON CONFIG ====================

@router.get("/admin/reminder-cron/status")
async def get_reminder_cron_status(admin: dict = Depends(get_current_admin)):
    config = await db.app_config.find_one({"key": "reminder_cron"}, {"_id": 0})
    if not config:
        return {"enabled": False, "hour": 9, "minute": 0, "last_run": None, "last_results": None}
    config.pop("key", None)
    return config

@router.post("/admin/reminder-cron/toggle")
async def toggle_reminder_cron(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    enabled = body.get("enabled", True)
    await db.app_config.update_one(
        {"key": "reminder_cron"},
        {"$set": {"enabled": enabled}},
        upsert=True
    )
    return {"success": True, "enabled": enabled}


# ==================== ENGAGEMENT KPIS ====================

@router.get("/admin/engagement-kpis")
async def get_engagement_kpis(admin: dict = Depends(get_current_admin)):
    from datetime import timedelta

    # Inactivity reminders stats
    ir_total = await db.inactivity_reminders.count_documents({"status": {"$in": ["sent", "failed", "skipped"]}})
    ir_opened = await db.inactivity_reminders.count_documents({"opened": True})
    ir_clicked = await db.inactivity_reminders.count_documents({"clicked": True})

    # Completeness notifications stats
    cn_total = await db.completeness_notifications.count_documents({"status": {"$in": ["sent", "failed", "skipped"]}})
    cn_opened = await db.completeness_notifications.count_documents({"opened": True})
    cn_clicked = await db.completeness_notifications.count_documents({"clicked": True})

    total_all = ir_total + cn_total
    opened_all = ir_opened + cn_opened
    clicked_all = ir_clicked + cn_clicked

    open_rate = round((opened_all / total_all) * 100, 1) if total_all > 0 else 0
    click_rate = round((clicked_all / total_all) * 100, 1) if total_all > 0 else 0
    click_to_open = round((clicked_all / opened_all) * 100, 1) if opened_all > 0 else 0

    # By level breakdown (inactivity only)
    by_level = []
    for lvl in [1, 2, 3]:
        total_lvl = await db.inactivity_reminders.count_documents({"level": lvl})
        opened_lvl = await db.inactivity_reminders.count_documents({"level": lvl, "opened": True})
        clicked_lvl = await db.inactivity_reminders.count_documents({"level": lvl, "clicked": True})
        by_level.append({
            "level": lvl,
            "total": total_lvl,
            "opened": opened_lvl,
            "clicked": clicked_lvl,
            "open_rate": round((opened_lvl / total_lvl) * 100, 1) if total_lvl > 0 else 0,
            "click_rate": round((clicked_lvl / total_lvl) * 100, 1) if total_lvl > 0 else 0,
        })

    # Completeness evolution: average completeness of clients who were reminded vs before
    # Get clients who received reminders and clicked
    clicked_clients = await db.inactivity_reminders.find(
        {"clicked": True}, {"_id": 0, "client_id": 1, "completeness_pct": 1}
    ).to_list(200)
    completeness_before = []
    completeness_after = []
    for cc in clicked_clients:
        completeness_before.append(cc.get("completeness_pct", 0))
        # Check current completeness from latest docs
        cid = cc["client_id"]
        docs = await db.client_documents.find({"client_id": cid}, {"_id": 0, "category": 1, "name": 1}).to_list(500)
        doc_cats = [d.get("category", "") for d in docs] + [d.get("name", "") for d in docs]
        from routes.client import ESSENTIAL_DOCS, _match_doc_to_essential
        essential = ESSENTIAL_DOCS.get("at", [])
        found = sum(1 for ed in essential if _match_doc_to_essential(doc_cats, ed["key"], ed["category"]))
        current_pct = round((found / len(essential)) * 100) if essential else 100
        completeness_after.append(current_pct)

    avg_before = round(sum(completeness_before) / len(completeness_before), 1) if completeness_before else 0
    avg_after = round(sum(completeness_after) / len(completeness_after), 1) if completeness_after else 0
    improvement = round(avg_after - avg_before, 1)

    # Timeline: daily counts for last 30 days
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=30)).isoformat()
    recent_reminders = await db.inactivity_reminders.find(
        {"created_at": {"$gte": cutoff}},
        {"_id": 0, "created_at": 1, "opened": 1, "clicked": 1}
    ).to_list(5000)
    recent_notifs = await db.completeness_notifications.find(
        {"created_at": {"$gte": cutoff}},
        {"_id": 0, "created_at": 1, "opened": 1, "clicked": 1}
    ).to_list(5000)

    timeline = {}
    for r in recent_reminders + recent_notifs:
        day = str(r.get("created_at", ""))[:10]
        if day not in timeline:
            timeline[day] = {"date": day, "sent": 0, "opened": 0, "clicked": 0}
        timeline[day]["sent"] += 1
        if r.get("opened"):
            timeline[day]["opened"] += 1
        if r.get("clicked"):
            timeline[day]["clicked"] += 1

    timeline_list = sorted(timeline.values(), key=lambda x: x["date"])

    return {
        "summary": {
            "total_sent": total_all,
            "total_opened": opened_all,
            "total_clicked": clicked_all,
            "open_rate": open_rate,
            "click_rate": click_rate,
            "click_to_open_rate": click_to_open,
        },
        "by_level": by_level,
        "completeness_evolution": {
            "clients_tracked": len(completeness_before),
            "avg_before": avg_before,
            "avg_after": avg_after,
            "improvement": improvement,
        },
        "timeline": timeline_list,
    }


# ==================== CSV EXPORT ====================

@router.get("/admin/export/relances-csv")
async def export_relances_csv(admin: dict = Depends(get_current_admin)):
    from fastapi.responses import StreamingResponse
    import io
    import csv

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["Date", "Client", "Email", "Niveau", "Jours inactif", "Complétude %", "Type dossier", "Statut", "Ouvert", "Cliqué"])

    reminders = await db.inactivity_reminders.find({}, {"_id": 0}).sort("created_at", -1).to_list(10000)
    for r in reminders:
        writer.writerow([
            r.get("created_at", "")[:19],
            r.get("client_name", ""),
            r.get("client_email", ""),
            f"L{r.get('level', '')}",
            r.get("days_inactive", ""),
            r.get("completeness_pct", ""),
            r.get("case_type", ""),
            r.get("status", ""),
            "Oui" if r.get("opened") else "Non",
            "Oui" if r.get("clicked") else "Non",
        ])

    # Add completeness notifications
    writer.writerow([])
    writer.writerow(["--- Notifications de complétude ---"])
    writer.writerow(["Date", "Client", "Email", "Seuil %", "Complétude réelle %", "Type dossier", "Statut", "Ouvert", "Cliqué"])
    notifs = await db.completeness_notifications.find({}, {"_id": 0}).sort("created_at", -1).to_list(10000)
    for n in notifs:
        writer.writerow([
            n.get("created_at", "")[:19],
            n.get("client_name", ""),
            n.get("client_email", ""),
            n.get("threshold_pct", ""),
            n.get("actual_pct", ""),
            n.get("case_type", ""),
            n.get("status", ""),
            "Oui" if n.get("opened") else "Non",
            "Oui" if n.get("clicked") else "Non",
        ])

    # Add KPI summary
    writer.writerow([])
    writer.writerow(["--- KPIs d'engagement ---"])
    total_ir = await db.inactivity_reminders.count_documents({})
    opened_ir = await db.inactivity_reminders.count_documents({"opened": True})
    clicked_ir = await db.inactivity_reminders.count_documents({"clicked": True})
    total_cn = await db.completeness_notifications.count_documents({})
    opened_cn = await db.completeness_notifications.count_documents({"opened": True})
    clicked_cn = await db.completeness_notifications.count_documents({"clicked": True})
    total = total_ir + total_cn
    opened = opened_ir + opened_cn
    clicked = clicked_ir + clicked_cn
    writer.writerow(["Métrique", "Valeur"])
    writer.writerow(["Total emails", total])
    writer.writerow(["Ouvertures", opened])
    writer.writerow(["Clics CTA", clicked])
    writer.writerow(["Taux ouverture", f"{round((opened/total)*100,1)}%" if total else "0%"])
    writer.writerow(["Taux clic", f"{round((clicked/total)*100,1)}%" if total else "0%"])
    writer.writerow(["Clic/ouverture", f"{round((clicked/opened)*100,1)}%" if opened else "0%"])

    content = output.getvalue()
    output.close()

    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=relances_kpis_export.csv"}
    )


# ==================== KPI ALERTS ====================

KPI_ALERT_DEFAULTS = {"open_rate_threshold": 30, "click_rate_threshold": 10, "alerts_enabled": True}

@router.get("/admin/kpi-alerts/config")
async def get_kpi_alert_config(admin: dict = Depends(get_current_admin)):
    config = await db.app_config.find_one({"key": "kpi_alerts"}, {"_id": 0})
    if not config:
        return KPI_ALERT_DEFAULTS
    config.pop("key", None)
    return config

@router.post("/admin/kpi-alerts/config")
async def update_kpi_alert_config(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    update = {
        "open_rate_threshold": body.get("open_rate_threshold", 30),
        "click_rate_threshold": body.get("click_rate_threshold", 10),
        "alerts_enabled": body.get("alerts_enabled", True),
    }
    await db.app_config.update_one({"key": "kpi_alerts"}, {"$set": update}, upsert=True)
    return {"success": True, **update}

@router.get("/admin/kpi-alerts/check")
async def check_kpi_alerts(admin: dict = Depends(get_current_admin)):
    config = await db.app_config.find_one({"key": "kpi_alerts"}, {"_id": 0})
    if not config or not config.get("alerts_enabled", True):
        return {"alerts": [], "checked": True}

    total_ir = await db.inactivity_reminders.count_documents({})
    opened_ir = await db.inactivity_reminders.count_documents({"opened": True})
    clicked_ir = await db.inactivity_reminders.count_documents({"clicked": True})
    total_cn = await db.completeness_notifications.count_documents({})
    opened_cn = await db.completeness_notifications.count_documents({"opened": True})
    clicked_cn = await db.completeness_notifications.count_documents({"clicked": True})

    total = total_ir + total_cn
    opened = opened_ir + opened_cn
    clicked = clicked_ir + clicked_cn

    open_rate = round((opened / total) * 100, 1) if total > 0 else 0
    click_rate = round((clicked / total) * 100, 1) if total > 0 else 0

    alerts = []
    open_threshold = config.get("open_rate_threshold", 30)
    click_threshold = config.get("click_rate_threshold", 10)

    if total >= 10 and open_rate < open_threshold:
        alerts.append({
            "type": "open_rate",
            "severity": "critical" if open_rate < open_threshold / 2 else "warning",
            "message": f"Taux d'ouverture critique : {open_rate}% (seuil : {open_threshold}%)",
            "current_value": open_rate,
            "threshold": open_threshold,
        })
    if total >= 10 and click_rate < click_threshold:
        alerts.append({
            "type": "click_rate",
            "severity": "critical" if click_rate < click_threshold / 2 else "warning",
            "message": f"Taux de clic critique : {click_rate}% (seuil : {click_threshold}%)",
            "current_value": click_rate,
            "threshold": click_threshold,
        })

    return {"alerts": alerts, "checked": True, "open_rate": open_rate, "click_rate": click_rate}


# ==================== A/B TESTING ====================

@router.post("/admin/ab-tests")
async def create_ab_test(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    name = body.get("name", "Test A/B")
    variants = body.get("variants", [])
    if len(variants) < 2:
        raise HTTPException(status_code=400, detail="Au moins 2 variantes requises")

    # Deactivate any existing active test
    await db.ab_tests.update_many({"status": "active"}, {"$set": {"status": "paused"}})

    test = {
        "id": str(uuid.uuid4()),
        "name": name,
        "variants": variants,
        "status": "active",
        "min_sends_per_variant": body.get("min_sends", 50),
        "promoted_variant": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.ab_tests.insert_one(test)
    test.pop("_id", None)
    return test

@router.get("/admin/ab-tests")
async def list_ab_tests(admin: dict = Depends(get_current_admin)):
    tests = await db.ab_tests.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return {"tests": tests}

@router.get("/admin/ab-tests/{test_id}/results")
async def get_ab_test_results(test_id: str, admin: dict = Depends(get_current_admin)):
    test = await db.ab_tests.find_one({"id": test_id}, {"_id": 0})
    if not test:
        raise HTTPException(status_code=404, detail="Test non trouvé")

    variant_names = [v["name"] for v in test.get("variants", [])]
    results = []
    for vn in variant_names:
        sent = await db.inactivity_reminders.count_documents({"ab_test_id": test_id, "ab_variant": vn})
        opened = await db.inactivity_reminders.count_documents({"ab_test_id": test_id, "ab_variant": vn, "opened": True})
        clicked = await db.inactivity_reminders.count_documents({"ab_test_id": test_id, "ab_variant": vn, "clicked": True})
        open_rate = round((opened / sent) * 100, 1) if sent > 0 else 0
        click_rate = round((clicked / sent) * 100, 1) if sent > 0 else 0
        results.append({
            "variant": vn,
            "sent": sent,
            "opened": opened,
            "clicked": clicked,
            "open_rate": open_rate,
            "click_rate": click_rate,
        })

    # Determine winner (highest click_rate among variants with enough sends)
    min_sends = test.get("min_sends_per_variant", 50)
    qualified = [r for r in results if r["sent"] >= min_sends]
    winner = None
    if len(qualified) >= 2:
        winner = max(qualified, key=lambda r: r["click_rate"])

    return {"test": test, "results": results, "winner": winner, "ready_to_promote": winner is not None}

@router.post("/admin/ab-tests/{test_id}/promote")
async def promote_ab_winner(test_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    variant_name = body.get("variant_name")
    if not variant_name:
        raise HTTPException(status_code=400, detail="variant_name requis")

    await db.ab_tests.update_one(
        {"id": test_id},
        {"$set": {"promoted_variant": variant_name, "status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True, "promoted_variant": variant_name}

@router.post("/admin/ab-tests/{test_id}/toggle")
async def toggle_ab_test(test_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    status = body.get("status", "paused")
    if status == "active":
        await db.ab_tests.update_many({"status": "active"}, {"$set": {"status": "paused"}})
    await db.ab_tests.update_one({"id": test_id}, {"$set": {"status": status}})
    return {"success": True, "status": status}


# ==================== EMAIL TEMPLATES ====================

DEFAULT_TEMPLATES = [
    {
        "name": "rassurant",
        "label": "Ton rassurant",
        "subject": "Votre dossier vous attend — nous sommes là pour vous",
        "intro": "Nous avons remarqué que votre dossier est en attente. Pas d'inquiétude, nous sommes là pour vous accompagner à chaque étape.",
        "motivation": "En complétant votre dossier, vous profiterez d'une analyse StratégiIA précise et de recommandations personnalisées pour défendre au mieux vos droits.",
        "cta_text": "Compléter mon dossier",
        "status": "active",
    },
    {
        "name": "incitatif",
        "label": "Ton incitatif",
        "subject": "Plus que quelques documents pour une analyse complète !",
        "intro": "Bonne nouvelle ! Votre dossier avance bien. Il ne manque que quelques documents pour débloquer une analyse complète et maximiser vos résultats.",
        "motivation": "Les clients qui complètent leur dossier obtiennent des recommandations bien plus précises. Ne manquez pas cette opportunité d'optimiser votre accompagnement !",
        "cta_text": "Finaliser mon dossier",
        "status": "active",
    },
    {
        "name": "urgent",
        "label": "Ton urgent",
        "subject": "Action requise : votre dossier attend vos documents",
        "intro": "Votre dossier est en attente depuis plusieurs jours. Sans les pièces manquantes, nous ne pouvons pas vous fournir une analyse optimale.",
        "motivation": "Plus vous attendez, plus les délais s'allongent. Complétez votre dossier maintenant pour avancer sereinement dans vos démarches.",
        "cta_text": "Agir maintenant",
        "status": "active",
    },
]

@router.post("/admin/email-templates/seed")
async def seed_email_templates(admin: dict = Depends(get_current_admin)):
    created = 0
    for tpl in DEFAULT_TEMPLATES:
        exists = await db.email_templates.find_one({"name": tpl["name"]}, {"_id": 0, "id": 1})
        if not exists:
            doc = {**tpl, "id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat()}
            await db.email_templates.insert_one(doc)
            created += 1
    return {"success": True, "created": created}

@router.get("/admin/email-templates")
async def list_email_templates(admin: dict = Depends(get_current_admin)):
    templates = await db.email_templates.find({}, {"_id": 0}).sort("created_at", 1).to_list(50)
    return {"templates": templates}

@router.post("/admin/email-templates")
async def create_email_template(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": str(uuid.uuid4()),
        "name": body.get("name", ""),
        "label": body.get("label", body.get("name", "")),
        "subject": body.get("subject", ""),
        "intro": body.get("intro", ""),
        "motivation": body.get("motivation", ""),
        "cta_text": body.get("cta_text", "Compléter mon dossier"),
        "status": body.get("status", "draft"),
        "created_at": now,
        "updated_at": now,
    }
    await db.email_templates.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.put("/admin/email-templates/{template_id}")
async def update_email_template(template_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    update = {}
    for field in ["name", "label", "subject", "intro", "motivation", "cta_text", "status"]:
        if field in body:
            update[field] = body[field]
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.email_templates.update_one({"id": template_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    return {"success": True, "id": template_id}

@router.delete("/admin/email-templates/{template_id}")
async def delete_email_template(template_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.email_templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    return {"success": True}

@router.post("/admin/email-templates/{template_id}/duplicate")
async def duplicate_email_template(template_id: str, admin: dict = Depends(get_current_admin)):
    tpl = await db.email_templates.find_one({"id": template_id}, {"_id": 0})
    if not tpl:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    now = datetime.now(timezone.utc).isoformat()
    new_doc = {**tpl, "id": str(uuid.uuid4()), "name": tpl["name"] + "_copy", "label": tpl["label"] + " (copie)", "status": "draft", "created_at": now, "updated_at": now}
    await db.email_templates.insert_one(new_doc)
    new_doc.pop("_id", None)
    return new_doc

@router.get("/admin/email-templates/variables")
async def list_template_variables(admin: dict = Depends(get_current_admin)):
    from utils.email import TEMPLATE_VARIABLES
    return {"variables": TEMPLATE_VARIABLES}


@router.post("/admin/email-templates/preview")
async def preview_email_template(request: Request, admin: dict = Depends(get_current_admin)):
    from utils.email import resolve_template_variables, SAMPLE_CONTEXT
    body = await request.json()
    from config import SITE_URL
    site_url = os.environ.get("FRONTEND_URL", SITE_URL)

    # Build preview context with sample values (overridable)
    preview_context = {**SAMPLE_CONTEXT}
    if body.get("prenom"):
        preview_context["prenom"] = body["prenom"]
    if body.get("completeness_pct") is not None:
        preview_context["completeness"] = str(body["completeness_pct"])
    if body.get("documents_missing"):
        preview_context["documents_missing"] = body["documents_missing"]

    subject = resolve_template_variables(body.get("subject", "Objet de l'email"), preview_context)
    intro = resolve_template_variables(body.get("intro", "Introduction..."), preview_context)
    motivation = resolve_template_variables(body.get("motivation", "Motivation..."), preview_context)
    cta_text = resolve_template_variables(body.get("cta_text", "Compléter mon dossier"), preview_context)
    prenom = preview_context["prenom"]
    completeness_pct = preview_context["completeness"]

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:0;background:#f5f5f5;">
        <div style="background:#1a1a2e;color:#fff;padding:24px;text-align:center;">
            <h1 style="margin:0;color:#d4a44a;font-size:20px;">Stratégie &amp; Expertise Santé</h1>
            <p style="margin:8px 0 0;color:#ccc;font-size:13px;">{subject}</p>
        </div>
        <div style="background:#FFFFFF;padding:24px;border:1px solid #E5E0D6;">
            <p style="font-size:16px;">Bonjour <strong>{prenom}</strong>,</p>
            <p>{intro}</p>
            <div style="background:#F0F7F0;padding:16px;border-radius:8px;text-align:center;margin:20px 0;">
                <p style="margin:0;font-size:36px;font-weight:bold;color:#f59e0b;">{completeness_pct}%</p>
                <p style="margin:4px 0 0;color:#666;font-size:13px;">de complétude</p>
            </div>
            <p style="color:#555;font-size:14px;">{motivation}</p>
            <div style="text-align:center;margin:24px 0;">
                <a href="{site_url}/espace-client?tab=documents"
                   style="background:#1a1a2e;color:#d4a44a;padding:14px 28px;border-radius:6px;text-decoration:none;display:inline-block;font-weight:600;font-size:14px;">
                    {cta_text}
                </a>
            </div>
            <p style="color:#888;font-size:11px;text-align:center;margin-top:20px;">
                Stratégie &amp; Expertise Santé — Cet email est envoyé automatiquement.
            </p>
        </div>
    </body>
    </html>
    """
    return {"html": html, "subject": subject}


@router.post("/admin/email-templates/send-test")
async def send_test_email_template(request: Request, admin: dict = Depends(get_current_admin)):
    """Send a test email with resolved variables to a specified address."""
    from utils.email import resolve_template_variables, SAMPLE_CONTEXT
    from config import SITE_URL, RESEND_AVAILABLE, SENDER_EMAIL
    body = await request.json()

    to_email = body.get("email", "")
    if not to_email:
        raise HTTPException(status_code=400, detail="Adresse email requise")

    if not RESEND_AVAILABLE or not os.environ.get("RESEND_API_KEY"):
        raise HTTPException(status_code=503, detail="Resend non configuré. Impossible d'envoyer l'email de test.")

    site_url = os.environ.get("FRONTEND_URL", SITE_URL)

    # Build context with custom or sample values
    ctx = {**SAMPLE_CONTEXT}
    for key in ["prenom", "nom", "documents_missing", "date_inscription"]:
        if body.get(key):
            ctx[key] = body[key]
    if body.get("completeness") is not None:
        ctx["completeness"] = str(body["completeness"])

    subject = resolve_template_variables(body.get("subject", "Email de test"), ctx)
    intro = resolve_template_variables(body.get("intro", ""), ctx)
    motivation = resolve_template_variables(body.get("motivation", ""), ctx)
    cta_text = resolve_template_variables(body.get("cta_text", "Compléter mon dossier"), ctx)
    prenom = ctx["prenom"]
    completeness_pct = ctx["completeness"]

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:0;background:#f5f5f5;">
        <div style="background:#1a1a2e;color:#fff;padding:24px;text-align:center;">
            <h1 style="margin:0;color:#d4a44a;font-size:20px;">Stratégie &amp; Expertise Santé</h1>
            <p style="margin:8px 0 0;color:#ccc;font-size:13px;">{subject}</p>
        </div>
        <div style="background:#fff3cd;padding:8px;text-align:center;font-size:11px;color:#856404;border:1px solid #ffc107;">
            EMAIL DE TEST — Ce message ne sera pas comptabilisé dans les statistiques
        </div>
        <div style="background:#FFFFFF;padding:24px;border:1px solid #E5E0D6;">
            <p style="font-size:16px;">Bonjour <strong>{prenom}</strong>,</p>
            <p>{intro}</p>
            <div style="background:#F0F7F0;padding:16px;border-radius:8px;text-align:center;margin:20px 0;">
                <p style="margin:0;font-size:36px;font-weight:bold;color:#f59e0b;">{completeness_pct}%</p>
                <p style="margin:4px 0 0;color:#666;font-size:13px;">de complétude</p>
            </div>
            <p style="color:#555;font-size:14px;">{motivation}</p>
            <div style="text-align:center;margin:24px 0;">
                <a href="{site_url}/espace-client?tab=documents"
                   style="background:#1a1a2e;color:#d4a44a;padding:14px 28px;border-radius:6px;text-decoration:none;display:inline-block;font-weight:600;font-size:14px;">
                    {cta_text}
                </a>
            </div>
            <p style="color:#888;font-size:11px;text-align:center;margin-top:20px;">
                Stratégie &amp; Expertise Santé — Cet email est envoyé automatiquement.
            </p>
        </div>
    </body>
    </html>
    """

    send_status = "pending"
    send_error = None
    try:
        import resend
        resend.api_key = os.environ.get("RESEND_API_KEY", "")
        await asyncio.to_thread(resend.Emails.send, {
            "from": SENDER_EMAIL,
            "to": [to_email],
            "subject": f"[TEST] {subject}",
            "html": html
        })
        send_status = "sent"
        result = {"success": True, "message": f"Email de test envoyé à {to_email}"}
    except Exception as e:
        send_status = "failed"
        send_error = str(e)
        result = {"success": False, "message": str(e)}

    # Save to test history
    history_record = {
        "id": str(uuid.uuid4()),
        "template_id": body.get("template_id", ""),
        "template_name": body.get("template_name", ""),
        "email": to_email,
        "subject": f"[TEST] {subject}",
        "variables_used": {k: ctx[k] for k in ["prenom", "nom", "completeness", "documents_missing", "date_inscription"]},
        "status": send_status,
        "error": send_error,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.email_test_history.insert_one(history_record)

    return result


@router.get("/admin/email-templates/{template_id}/test-history")
async def get_template_test_history(template_id: str, admin: dict = Depends(get_current_admin)):
    """Get the test email history for a specific template."""
    history = await db.email_test_history.find(
        {"template_id": template_id}, {"_id": 0}
    ).sort("sent_at", -1).limit(10).to_list(10)
    return {"history": history, "total": len(history)}


# ==================== SCHEDULED CAMPAIGNS ====================

@router.post("/admin/campaigns/schedule")
async def schedule_campaign(request: Request, admin: dict = Depends(get_current_admin)):
    """Schedule a campaign to send a template at a specific date/time."""
    body = await request.json()
    template_id = body.get("template_id")
    scheduled_at = body.get("scheduled_at")
    target = body.get("target", "inactive_clients")
    ab_test_id = body.get("ab_test_id")

    if not template_id or not scheduled_at:
        raise HTTPException(status_code=400, detail="template_id et scheduled_at requis")

    # Validate template exists
    tpl = await db.email_templates.find_one({"id": template_id}, {"_id": 0})
    if not tpl:
        raise HTTPException(status_code=404, detail="Template non trouvé")

    # Validate scheduled_at is in the future
    try:
        sched_dt = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Format de date invalide")

    if sched_dt <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="La date doit être dans le futur")

    # Validate AB test if provided
    if ab_test_id:
        ab = await db.ab_tests.find_one({"id": ab_test_id}, {"_id": 0})
        if not ab:
            raise HTTPException(status_code=404, detail="Test A/B non trouvé")

    campaign = {
        "id": str(uuid.uuid4()),
        "template_id": template_id,
        "template_name": tpl.get("name", ""),
        "template_label": tpl.get("label", tpl.get("name", "")),
        "scheduled_at": sched_dt.isoformat(),
        "target": target,
        "ab_test_id": ab_test_id,
        "status": "scheduled",
        "recipients_count": 0,
        "sent_count": 0,
        "failed_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "executed_at": None,
        "error": None,
    }
    await db.scheduled_campaigns.insert_one(campaign)
    campaign.pop("_id", None)
    return campaign


@router.get("/admin/campaigns")
async def list_campaigns(admin: dict = Depends(get_current_admin)):
    """List all scheduled campaigns."""
    campaigns = await db.scheduled_campaigns.find({}, {"_id": 0}).sort("scheduled_at", -1).to_list(50)
    return {"campaigns": campaigns}


@router.put("/admin/campaigns/{campaign_id}/cancel")
async def cancel_campaign(campaign_id: str, admin: dict = Depends(get_current_admin)):
    """Cancel a scheduled campaign."""
    campaign = await db.scheduled_campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campagne non trouvée")
    if campaign["status"] != "scheduled":
        raise HTTPException(status_code=400, detail="Seule une campagne programmée peut être annulée")

    await db.scheduled_campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"status": "cancelled", "executed_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True, "message": "Campagne annulée"}


@router.delete("/admin/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str, admin: dict = Depends(get_current_admin)):
    """Delete a campaign record."""
    result = await db.scheduled_campaigns.delete_one({"id": campaign_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Campagne non trouvée")
    return {"success": True}


# ==================== DATA PURGE ADMIN ====================

@router.get("/admin/purge-log")
async def get_purge_log(admin: dict = Depends(get_current_admin)):
    """View data purge history."""
    logs = await db.purge_log.find({}, {"_id": 0}).sort("executed_at", -1).to_list(50)
    # Stats
    total_dossiers = await db.dossier_express.count_documents({})
    purged = await db.dossier_express.count_documents({"documents_text_purged": True})
    pending = await db.dossier_express.count_documents({
        "status": "completed",
        "documents_text": {"$exists": True, "$ne": ""},
        "documents_text_purged": {"$ne": True},
    })
    return {
        "logs": logs,
        "stats": {
            "total_dossiers": total_dossiers,
            "purged": purged,
            "pending_purge": pending,
        }
    }

@router.post("/admin/purge-now")
async def trigger_manual_purge(admin: dict = Depends(get_current_admin)):
    """Manually trigger immediate purge of OCR text from completed dossiers older than 30 days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    result = await db.dossier_express.update_many(
        {
            "status": "completed",
            "completed_at": {"$lte": cutoff},
            "documents_text": {"$exists": True, "$ne": ""},
        },
        {"$set": {"documents_text": "", "documents_text_purged": True, "purged_at": datetime.now(timezone.utc).isoformat()}}
    )
    await db.purge_log.insert_one({
        "type": "manual_purge",
        "count": result.modified_count,
        "cutoff_date": cutoff,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "triggered_by": admin.get("email", "admin"),
    })
    logger.info(f"MANUAL PURGE by {admin.get('email')}: {result.modified_count} dossier(s) purged")
    return {"success": True, "purged_count": result.modified_count}



# ==================== LAUNCH MODE CONTROL ====================

LAUNCH_MODES = ["ouvert", "controle", "indisponible"]

LAUNCH_MODE_MESSAGES = {
    "ouvert": "",
    "controle": "",
    "indisponible": "Le service est temporairement suspendu pour maintenance programmee. Nous serons de retour tres prochainement.",
}

@router.get("/launch-mode")
async def get_launch_mode_public():
    """Public endpoint — returns current launch mode for frontend gating."""
    config = await db.system_config.find_one({"key": "launch_mode"}, {"_id": 0})
    if not config:
        return {"mode": "ouvert", "message": ""}
    return {"mode": config.get("value", "ouvert"), "message": config.get("message", "")}


@router.get("/admin/launch-mode")
async def admin_get_launch_mode(admin: dict = Depends(get_current_admin)):
    config = await db.system_config.find_one({"key": "launch_mode"}, {"_id": 0})
    if not config:
        return {"mode": "ouvert", "message": "", "updated_at": None, "updated_by": None}
    return {
        "mode": config.get("value", "ouvert"),
        "message": config.get("message", ""),
        "updated_at": config.get("updated_at"),
        "updated_by": config.get("updated_by"),
    }


@router.put("/admin/launch-mode")
async def admin_set_launch_mode(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    mode = body.get("mode", "ouvert")
    custom_message = body.get("message", "")
    if mode not in LAUNCH_MODES:
        raise HTTPException(status_code=400, detail=f"Mode invalide. Options: {', '.join(LAUNCH_MODES)}")
    message = custom_message if custom_message else LAUNCH_MODE_MESSAGES.get(mode, "")
    await db.system_config.update_one(
        {"key": "launch_mode"},
        {"$set": {"value": mode, "message": message, "updated_at": datetime.now(timezone.utc).isoformat(), "updated_by": admin.get("email", "admin")}},
        upsert=True,
    )
    logger.info(f"Launch mode set to '{mode}' by {admin.get('email')}")
    return {"success": True, "mode": mode, "message": message}


# ==================== MONITORING DASHBOARD ====================

@router.get("/admin/monitoring")
async def admin_monitoring(admin: dict = Depends(get_current_admin)):
    """Live KPIs for launch monitoring dashboard."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    seven_days_ago = (now - timedelta(days=7)).isoformat()

    # Fetch all relevant dossiers
    all_dossiers = await db.dossier_express.find({}, {"_id": 0, "documents_text": 0, "analysis": 0}).sort("created_at", -1).to_list(500)

    today_dossiers = [d for d in all_dossiers if (d.get("created_at") or "") >= today_start]
    week_dossiers = [d for d in all_dossiers if (d.get("created_at") or "") >= seven_days_ago]

    completed_all = [d for d in all_dossiers if d.get("status") == "completed"]
    completed_week = [d for d in week_dossiers if d.get("status") == "completed"]

    # Avg delivery time (completed dossiers with both created_at and completed_at)
    delivery_times = []
    for d in completed_all:
        try:
            if d.get("created_at") and d.get("completed_at"):
                start = datetime.fromisoformat(d["created_at"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(d["completed_at"].replace("Z", "+00:00"))
                delta_min = (end - start).total_seconds() / 60
                if 0 < delta_min < 1440:
                    delivery_times.append(delta_min)
        except Exception:
            pass
    avg_delay_min = round(sum(delivery_times) / len(delivery_times), 1) if delivery_times else 0

    total_all = len(all_dossiers) or 1
    total_week = len(week_dossiers) or 1

    incidents_today = [d for d in today_dossiers if d.get("delivery_status") == "incident_technique" or d.get("status") == "error"]
    incidents_week = [d for d in week_dossiers if d.get("delivery_status") == "incident_technique" or d.get("status") == "error"]
    pending = [d for d in all_dossiers if d.get("status") == "processing"]
    intervention = [d for d in all_dossiers if d.get("delivery_status") == "incident_technique"]

    success_rate_all = round((len(completed_all) / total_all) * 100, 1)
    success_rate_week = round((len(completed_week) / total_week) * 100, 1) if week_dossiers else 0

    # Launch mode
    config = await db.system_config.find_one({"key": "launch_mode"}, {"_id": 0})
    launch_mode = config.get("value", "ouvert") if config else "ouvert"

    return {
        "launch_mode": launch_mode,
        "kpis": {
            "orders_today": len(today_dossiers),
            "orders_7_days": len(week_dossiers),
            "success_rate_global": success_rate_all,
            "success_rate_7_days": success_rate_week,
            "incidents_today": len(incidents_today),
            "incidents_7_days": len(incidents_week),
            "avg_delivery_minutes": avg_delay_min,
            "pending_count": len(pending),
            "intervention_required": len(intervention),
            "total_delivered": len(completed_all),
        },
        "recent_incidents": [
            {
                "id": d.get("id"), "name": d.get("name"), "email": d.get("email"),
                "delivery_status": d.get("delivery_status"), "processing_step": d.get("processing_step"),
                "error": d.get("error"), "created_at": d.get("created_at"),
            }
            for d in incidents_week[:10]
        ],
    }



# ==================== SERVICE DIAGNOSTIC ====================

@router.get("/admin/services-status")
async def admin_services_status(admin: dict = Depends(get_current_admin)):
    """Comprehensive diagnostic of all services before live launch."""
    results = {}

    # 1. IA (Anthropic / Emergent fallback)
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    emergent_key = os.environ.get("EMERGENT_LLM_KEY", "")
    if anthropic_key:
        try:
            import anthropic as _anth
            client = _anth.Anthropic(api_key=anthropic_key)
            await asyncio.to_thread(
                client.messages.create, model="claude-sonnet-4-5-20250929", max_tokens=10,
                messages=[{"role": "user", "content": "Ping"}],
            )
            results["ia_anthropic"] = {"status": "ok", "mode": "natif", "detail": "Cle Anthropic valide et operationnelle"}
        except Exception as e:
            results["ia_anthropic"] = {"status": "error", "mode": "natif", "detail": str(e)[:150]}
    elif emergent_key:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(api_key=emergent_key, session_id="diag", system_message="Ping")
            chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
            await chat.send_message(UserMessage(text="Ping"))
            results["ia_anthropic"] = {"status": "ok", "mode": "emergent_fallback", "detail": "Cle Emergent Universal fonctionnelle (fallback)"}
        except Exception as e:
            results["ia_anthropic"] = {"status": "error", "mode": "emergent_fallback", "detail": str(e)[:150]}
    else:
        results["ia_anthropic"] = {"status": "missing", "mode": "aucun", "detail": "Aucune cle IA configuree (ANTHROPIC_API_KEY ou EMERGENT_LLM_KEY)"}

    # 2. Stripe
    stripe_key = os.environ.get("STRIPE_API_KEY", "")
    if stripe_key:
        try:
            import stripe as _stripe
            _stripe.api_key = stripe_key
            await asyncio.to_thread(_stripe.Balance.retrieve)
            is_live = stripe_key.startswith("sk_live_")
            results["stripe"] = {"status": "ok", "mode": "live" if is_live else "test", "detail": f"Stripe {'live' if is_live else 'test'} operationnel"}
        except Exception as e:
            results["stripe"] = {"status": "error", "mode": "unknown", "detail": str(e)[:150]}
    else:
        results["stripe"] = {"status": "missing", "mode": "aucun", "detail": "STRIPE_API_KEY non configuree"}

    # 3. Resend (Email)
    resend_key = os.environ.get("RESEND_API_KEY", "")
    if resend_key and RESEND_AVAILABLE:
        results["email_resend"] = {"status": "ok", "mode": "sandbox" if "re_" in resend_key[:10] else "live", "detail": "Resend configure"}
    else:
        results["email_resend"] = {"status": "missing", "mode": "aucun", "detail": "RESEND_API_KEY non configuree ou Resend non installe"}

    # 4. Object Storage (S3)
    s3_key = os.environ.get("AWS_ACCESS_KEY_ID", "") or os.environ.get("S3_ACCESS_KEY", "")
    if s3_key:
        results["storage_s3"] = {"status": "ok", "mode": "configure", "detail": "Stockage S3 configure"}
    else:
        results["storage_s3"] = {"status": "missing", "mode": "aucun", "detail": "Cles S3 non configurees"}

    # 5. MongoDB
    try:
        await db.command("ping")
        results["database"] = {"status": "ok", "mode": "operationnel", "detail": "MongoDB connecte"}
    except Exception as e:
        results["database"] = {"status": "error", "mode": "unknown", "detail": str(e)[:150]}

    # 6. Launch mode
    config = await db.system_config.find_one({"key": "launch_mode"}, {"_id": 0})
    launch_mode = config.get("value", "ouvert") if config else "ouvert"
    results["launch_mode"] = {"status": "ok", "mode": launch_mode, "detail": f"Mode actuel: {launch_mode}"}

    # Summary
    all_ok = all(r["status"] == "ok" for r in results.values())
    critical_ok = results.get("ia_anthropic", {}).get("status") == "ok" and results.get("database", {}).get("status") == "ok"

    return {
        "all_services_ok": all_ok,
        "critical_services_ok": critical_ok,
        "ready_for_launch": all_ok,
        "services": results,
    }
