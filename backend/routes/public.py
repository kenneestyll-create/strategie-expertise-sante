from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from datetime import datetime, timezone
import asyncio
import uuid

from config import db
from models import (
    ContactRequest, ContactRequestCreate, FAQItem,
    Avis, AvisCreate,
    VisitorCount, ReferralCode, ReferralUse, CreateReferralRequest
)
from utils.email import send_notification_email

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Stratégie & Expertise Santé"}

@router.get("/health")
async def health_check(request: Request):
    fonts = getattr(request.app.state, "pdf_fonts_report", {"ok": False, "error": "non verifie"})
    return {
        "status": "healthy" if fonts.get("ok") else "critical",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pdf_fonts": fonts,
    }


# ==================== CONTACT ====================

@router.post("/contact", response_model=dict)
async def create_contact(input_data: ContactRequestCreate):
    contact_dict = input_data.model_dump()
    contact_obj = ContactRequest(**contact_dict)
    doc = contact_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.contacts.insert_one(doc)
    asyncio.create_task(send_notification_email(contact_obj))
    return {
        "success": True,
        "message": "Votre demande a été envoyée avec succès. Nous vous recontacterons rapidement.",
        "id": contact_obj.id
    }


# ==================== FAQ ====================

@router.get("/faq", response_model=List[FAQItem])
async def get_faq():
    faqs = await db.faq.find({}, {"_id": 0}).sort("ordre", 1).to_list(100)
    return faqs

@router.get("/faq/category/{categorie:path}", response_model=List[FAQItem])
async def get_faq_by_category(categorie: str):
    from urllib.parse import unquote
    decoded_categorie = unquote(categorie)
    faqs = await db.faq.find({"categorie": decoded_categorie}, {"_id": 0}).sort("ordre", 1).to_list(100)
    return faqs


# ==================== AVIS (Public) ====================

@router.get("/avis", response_model=List[Avis])
async def get_published_avis():
    avis_list = await db.avis.find({"status": "publie"}, {"_id": 0}).sort("created_at", -1).to_list(100)
    for avis in avis_list:
        if isinstance(avis.get('created_at'), str):
            avis['created_at'] = datetime.fromisoformat(avis['created_at'])
        # Handle legacy field name: temoignage -> commentaire
        if 'temoignage' in avis and 'commentaire' not in avis:
            avis['commentaire'] = avis.pop('temoignage')
    return avis_list

@router.post("/avis", response_model=dict)
async def create_avis(input_data: AvisCreate):
    # RGPD compliance: explicit consents are mandatory (art. 7 & 9 RGPD — données de santé possibles)
    if not input_data.consent_publication:
        raise HTTPException(status_code=422, detail="Le consentement à la publication est obligatoire.")
    if not input_data.consent_data_processing:
        raise HTTPException(status_code=422, detail="Le consentement au traitement des données est obligatoire.")

    avis_obj = Avis(
        **input_data.model_dump(),
        consent_date=datetime.now(timezone.utc),
        consent_version="v1.0-2026-02"
    )
    doc = avis_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('consent_date'):
        doc['consent_date'] = doc['consent_date'].isoformat()
    await db.avis.insert_one(doc)
    return {
        "success": True,
        "message": "Votre témoignage a été soumis et sera publié après validation.",
        "id": avis_obj.id
    }


# ==================== VISITORS ====================

@router.get("/visitors/count")
async def get_visitor_count():
    counter = await db.visitor_counter.find_one({"id": "visitor_counter"}, {"_id": 0})
    if not counter:
        return {"count": 0}
    return {"count": counter.get("count", 0)}

@router.post("/visitors/increment")
async def increment_visitor_count():
    result = await db.visitor_counter.find_one_and_update(
        {"id": "visitor_counter"},
        {"$inc": {"count": 1}, "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
        return_document=True
    )
    count = result.get("count", 1) if result else 1
    return {"count": count}


# ==================== REFERRAL & DISCOUNT ====================

@router.post("/referral/create")
async def create_referral_code(request: CreateReferralRequest):
    existing = await db.referral_codes.find_one({"owner_email": request.email}, {"_id": 0})
    if existing:
        return {"code": existing["code"], "message": "Code existant récupéré"}

    import random
    import string
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    referral = ReferralCode(code=code, owner_email=request.email, owner_name=request.name)
    doc = referral.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.referral_codes.insert_one(doc)
    return {"success": True, "code": code, "message": "Votre code parrainage a été créé. Partagez-le pour offrir 10% de réduction !"}

@router.get("/referral/validate/{code}")
async def validate_referral_code(code: str):
    referral = await db.referral_codes.find_one({"code": code.upper(), "is_active": True}, {"_id": 0})
    if not referral:
        return {"valid": False, "message": "Code invalide ou expiré"}
    return {"valid": True, "discount": 10, "message": "Code valide ! 10% de réduction appliquée."}

@router.get("/client/discount/{email}")
async def get_client_discount(email: str):
    client = await db.client_history.find_one({"email": email.lower()}, {"_id": 0})
    orders_count = client.get("orders_count", 0) if client else 0
    loyalty_discount = 15 if orders_count >= 1 else 0
    return {
        "orders_count": orders_count,
        "loyalty_discount": loyalty_discount,
        "message": f"{'15% de fidélité appliqués !' if loyalty_discount else 'Première commande'}"
    }

@router.post("/client/record-order")
async def record_client_order(email: str, name: Optional[str] = None):
    await db.client_history.update_one(
        {"email": email.lower()},
        {
            "$inc": {"orders_count": 1},
            "$set": {"last_order_at": datetime.now(timezone.utc).isoformat(), "name": name},
            "$setOnInsert": {"id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat()}
        },
        upsert=True
    )
    return {"success": True}



# ── Partner / Sponsor requests ──
@router.post("/partner-request")
async def submit_partner_request(data: dict):
    name = (data.get("name") or "").strip()
    company = (data.get("company") or "").strip()
    email = (data.get("email") or "").strip()
    partner_type = (data.get("partner_type") or "").strip()
    message = (data.get("message") or "").strip()
    if not name or not email or not partner_type:
        raise HTTPException(status_code=400, detail="Nom, email et type de partenariat requis")
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "id": str(uuid.uuid4()),
        "name": name,
        "company": company,
        "email": email,
        "partner_type": partner_type,
        "message": message,
        "status": "new",
        "created_at": now,
    }
    await db.partner_requests.insert_one(entry)
    try:
        await send_notification_email(
            to_email="contact@strategie-expertise-sante.fr",
            subject=f"Nouvelle demande de partenariat — {name}",
            body=f"Nom : {name}\nSociété : {company}\nEmail : {email}\nType : {partner_type}\nMessage : {message}"
        )
    except Exception:
        pass
    return {"success": True, "message": "Votre demande a bien été envoyée. Nous vous recontacterons rapidement."}
