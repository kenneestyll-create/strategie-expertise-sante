from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import PlainTextResponse, Response
from datetime import datetime, timezone, timedelta
import asyncio
import os
import re
import uuid

from config import db, PAYMENT_PACKAGES, AVAILABLE_SLOTS, RESEND_AVAILABLE, SENDER_EMAIL, NOTIFICATION_EMAIL, SITE_URL, SITEMAP_PAGES, logger
from models import Booking, BookingCreate, SimulatorResult, AbandonedCheckout, FAQItem, AdminUser
from utils.auth import get_current_admin, hash_password

try:
    import resend
except ImportError:
    pass

router = APIRouter()


# ==================== BOOKING ====================

@router.get("/bookings/slots/{date}")
async def get_available_slots(date: str):
    booked = await db.bookings.find({"date": date, "status": {"$ne": "annule"}}, {"_id": 0, "time_slot": 1}).to_list(100)
    booked_slots = {b["time_slot"] for b in booked}
    available = [s for s in AVAILABLE_SLOTS if s not in booked_slots]
    return {"date": date, "slots": available}

@router.post("/bookings")
async def create_booking(data: BookingCreate):
    existing = await db.bookings.find_one({"date": data.date, "time_slot": data.time_slot, "status": {"$ne": "annule"}}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Ce créneau n'est plus disponible")
    booking = Booking(**data.model_dump())
    doc = booking.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.bookings.insert_one(doc)
    return {"success": True, "booking_id": booking.id, "message": "Rendez-vous confirmé"}

@router.get("/admin/bookings")
async def get_admin_bookings(admin: dict = Depends(get_current_admin)):
    bookings = await db.bookings.find({}, {"_id": 0}).sort("date", -1).to_list(500)
    return bookings

@router.patch("/admin/bookings/{booking_id}")
async def update_booking_status(booking_id: str, status: str, admin: dict = Depends(get_current_admin)):
    result = await db.bookings.update_one({"id": booking_id}, {"$set": {"status": status}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
    return {"success": True}


# ==================== SIMULATOR ====================

@router.post("/simulator/result")
async def save_simulator_result(request: Request):
    body = await request.json()
    result = SimulatorResult(answers=body.get("answers", {}), profile=body.get("profile", ""), recommendations=body.get("recommendations", []), email=body.get("email"))
    doc = result.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['droits'] = body.get("droits", [])
    doc['demarches'] = body.get("demarches", [])
    doc['delais'] = body.get("delais", [])
    doc['prestation'] = body.get("prestation", "")
    await db.simulator_results.insert_one(doc)

    hubspot_portal = os.environ.get('HUBSPOT_PORTAL_ID')
    hubspot_token = os.environ.get('HUBSPOT_ACCESS_TOKEN')
    if hubspot_portal and hubspot_token and body.get("email"):
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    "https://api.hubapi.com/crm/v3/objects/contacts",
                    headers={"Authorization": f"Bearer {hubspot_token}", "Content-Type": "application/json"},
                    json={"properties": {"email": body["email"], "firstname": body.get("nom", ""), "lastname": "", "company": "Simulateur Diagnostic", "lifecyclestage": "lead", "hs_lead_status": "NEW", "notes_last_updated": f"Profil: {body.get('profile', '')}. Recommandations: {'; '.join(body.get('recommendations', []))}"}}
                )
            logger.info(f"HubSpot contact created for {body['email']}")
        except Exception as e:
            logger.error(f"HubSpot sync error: {e}")

    return {"success": True, "id": result.id}

@router.get("/admin/simulator/stats")
async def get_simulator_stats(admin: dict = Depends(get_current_admin)):
    total = await db.simulator_results.count_documents({})
    results = await db.simulator_results.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return {"total": total, "recent": results}


# ==================== CALCULATOR ====================

@router.post("/calculator/track")
async def track_calculator_usage(request: Request):
    body = await request.json()
    calc_type = body.get("type", "unknown")
    await db.calculator_usage.insert_one({"type": calc_type, "created_at": datetime.now(timezone.utc).isoformat()})
    return {"success": True}

@router.get("/calculator/count")
async def get_calculator_weekly_count():
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    count = await db.calculator_usage.count_documents({"created_at": {"$gte": week_ago}})
    return {"count": count}


# ==================== URGENT ALERTS ====================

@router.post("/alerte-urgente")
async def create_urgent_alert(request: Request):
    body = await request.json()
    if not body.get("nom") or not body.get("telephone"):
        raise HTTPException(status_code=400, detail="Nom et téléphone requis")
    alert = {"id": str(uuid.uuid4()), "nom": body["nom"], "telephone": body["telephone"], "email": body.get("email", ""), "message": body.get("message", ""), "formule": body.get("formule", "2h"), "created_at": datetime.now(timezone.utc).isoformat(), "status": "nouveau", "traite": False}
    await db.urgent_alerts.insert_one(alert)
    if RESEND_AVAILABLE and os.environ.get('RESEND_API_KEY') and NOTIFICATION_EMAIL:
        try:
            prix = "80€" if alert["formule"] == "30min" else "50€"
            await asyncio.to_thread(resend.Emails.send, {"from": SENDER_EMAIL, "to": [NOTIFICATION_EMAIL], "subject": f"ALERTE URGENTE - {alert['nom']} ({prix})", "html": f"""<h2 style="color:red;">Demande urgente !</h2><p><strong>Formule:</strong> Réponse sous {alert['formule']} — {prix}</p><p><strong>Nom:</strong> {alert['nom']}</p><p><strong>Téléphone:</strong> {alert['telephone']}</p><p><strong>Email:</strong> {alert.get('email', 'Non renseigné')}</p><p><strong>Message:</strong> {alert.get('message', 'Aucun')}</p>"""})
        except Exception as e:
            logger.error(f"Urgent alert email error: {e}")
    return {"success": True, "id": alert["id"]}

@router.get("/admin/alertes-urgentes")
async def get_urgent_alerts(admin: dict = Depends(get_current_admin)):
    alerts = await db.urgent_alerts.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return {"items": alerts, "total": len(alerts), "non_traite": sum(1 for a in alerts if not a.get("traite"))}

@router.put("/admin/alertes-urgentes/{alert_id}")
async def update_urgent_alert(alert_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    await db.urgent_alerts.update_one({"id": alert_id}, {"$set": {"traite": body.get("traite", True), "status": body.get("status", "traité")}})
    return {"success": True}


# ==================== ABANDONED CHECKOUT ====================

@router.post("/relance/track")
async def track_abandoned_checkout(request: Request):
    body = await request.json()
    if not body.get("email"):
        raise HTTPException(status_code=400, detail="Email requis")
    pkg_id = body.get("package_id", "")
    pkg = PAYMENT_PACKAGES.get(pkg_id, {})
    abandoned = AbandonedCheckout(email=body["email"], name=body.get("name", ""), package_id=pkg_id, package_name=pkg.get("name", pkg_id), amount=pkg.get("amount", 0))
    doc = abandoned.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.abandoned_checkouts.insert_one(doc)
    return {"success": True}

@router.get("/admin/relance")
async def get_abandoned_checkouts(admin: dict = Depends(get_current_admin)):
    abandoned = await db.abandoned_checkouts.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    stats = {"total": len(abandoned), "not_sent": sum(1 for a in abandoned if not a.get("relance_sent")), "sent": sum(1 for a in abandoned if a.get("relance_sent"))}
    return {"items": abandoned, "stats": stats}

@router.post("/admin/relance/send/{item_id}")
async def send_relance_email(item_id: str, admin: dict = Depends(get_current_admin)):
    item = await db.abandoned_checkouts.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Élément non trouvé")
    email_sent = False
    error_detail = ""
    if RESEND_AVAILABLE and resend.api_key and resend.api_key != '':
        try:
            resend.Emails.send({"from": SENDER_EMAIL, "to": item["email"], "subject": "Stratégie & Expertise Santé - Finalisez votre démarche", "html": f"""<h2>Bonjour {item.get('name', '')},</h2><p>Vous aviez commencé à réserver notre prestation <strong>{item.get('package_name', '')}</strong>.</p><p>N'hésitez pas à finaliser votre inscription ou à nous contacter si vous avez des questions.</p><p>Premier échange gratuit et sans engagement.</p><p>Cordialement,<br>Stratégie & Expertise Santé</p>"""})
            email_sent = True
        except Exception as e:
            logger.error(f"Resend error: {e}")
            error_detail = str(e)
    await db.abandoned_checkouts.update_one({"id": item_id}, {"$set": {"relance_sent": True, "relance_sent_at": datetime.now(timezone.utc).isoformat()}})
    if email_sent:
        msg = "Email de relance envoyé avec succès"
    elif error_detail:
        msg = f"Relance marquée mais email échoué : {error_detail}"
    else:
        msg = "Relance marquée (email non configuré)"
    return {"success": True, "email_sent": email_sent, "message": msg}


# ==================== DOCUMENT VALIDATION (public) ====================

@router.post("/documents/validate")
async def validate_document(request: Request):
    body = await request.json()
    filename = body.get("filename", "")
    size = body.get("size", 0)
    mime_type = body.get("mime_type", "")
    accepted_mimes = ["application/pdf", "image/jpeg", "image/png", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    accepted_exts = [".pdf", ".jpg", ".jpeg", ".png", ".docx"]
    max_size = 10 * 1024 * 1024
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    errors = []
    if ext not in accepted_exts:
        errors.append(f"Format '{ext}' non accepté. Formats autorisés : PDF, JPG, PNG, DOCX.")
    if size > max_size:
        errors.append(f"Fichier trop volumineux ({size // (1024*1024)} Mo). Taille maximale : 10 Mo.")
    if size < 100:
        errors.append("Ce document semble illisible ou corrompu. Merci de le scanner à nouveau en haute qualité.")
    if mime_type and mime_type not in accepted_mimes:
        errors.append("Le type MIME du fichier ne correspond pas aux formats acceptés.")
    return {"valid": len(errors) == 0, "errors": errors}


@router.post("/documents/extract-fields")
async def extract_document_fields(request: Request):
    body = await request.json()
    raw_text = body.get("text", "")
    source = body.get("source", "tesseract")
    use_ai = body.get("use_ai", False)
    if not raw_text.strip():
        return {"fields": {}, "source": source, "enhanced": False}

    # Phase 2: Try GPT-4o if requested
    if use_ai:
        try:
            from utils.ocr_gpt import extract_fields_gpt4o
            result = await extract_fields_gpt4o(raw_text)
            if result.get("enhanced"):
                return result
        except Exception as e:
            logger.warning(f"GPT-4o extraction failed, falling back to regex: {e}")

    # Phase 1: Regex extraction

    fields = {}
    date_matches = re.findall(r'\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4}', raw_text)
    if date_matches:
        fields["dates"] = list(set(date_matches))
    amount_matches = re.findall(r'(\d[\d\s\.]*\d[,]\d{2})\s*(?:€|EUR|euros?)', raw_text, re.IGNORECASE)
    simple_amounts = re.findall(r'(?:^|[^\d,.])\s*(\d{2,6})\s*€', raw_text, re.MULTILINE)
    all_amounts = list(set([a.replace(' ', '') + '€' for a in amount_matches] + [a.strip() + '€' for a in simple_amounts]))
    if all_amounts:
        fields["montants"] = all_amounts
    ref_matches = re.findall(r'(?:N°|n°|Réf\.?|réf\.?|référence|dossier)\s*(?:n°\s*)?[:\s]*([A-Z][A-Z0-9\-\/]{3,20})', raw_text)
    if ref_matches:
        fields["references"] = list(set(ref_matches))
    ss_matches = re.findall(r'[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}', raw_text)
    if ss_matches:
        fields["numero_ss"] = ss_matches[0].replace(' ', '')
    name_matches = re.findall(r'(?:Nom|Patient|Assuré|Bénéficiaire)\s*:\s*([A-ZÀ-Ü][a-zà-ü]+(?:[ \t]+[A-ZÀ-Ü][a-zà-ü]+){0,3})', raw_text)
    if name_matches:
        fields["noms"] = list(set(name_matches))
    ipp_matches = re.findall(r'(?:taux|IPP|incapacité)\s*[:\s]?\s*(\d{1,3})\s*%', raw_text, re.IGNORECASE)
    if ipp_matches:
        fields["taux_ipp"] = [int(x) for x in ipp_matches]
    type_keywords = {'accident du travail': 'at', 'accident de travail': 'at', 'maladie professionnelle': 'mp', 'tableau des maladies': 'mp', 'mdph': 'mdph', 'aah': 'mdph', 'handicap': 'mdph', 'expertise médicale': 'expertise', 'expertise': 'expertise', 'ipp': 'ipp', 'incapacité permanente': 'ipp', 'cpam': 'at', 'cramif': 'at'}
    detected_types = list(set(dtype for keyword, dtype in type_keywords.items() if keyword.lower() in raw_text.lower()))
    if detected_types:
        fields["type_dossier_detected"] = detected_types
    return {"fields": fields, "source": source, "enhanced": False, "message": "Extraction regex (Phase 1). Phase 2 GPT-4o disponible."}


@router.post("/documents/extract-fields-ai")
async def extract_document_fields_ai(request: Request):
    """Phase 2: GPT-4o enhanced field extraction from OCR text."""
    body = await request.json()
    raw_text = body.get("text", "")
    if not raw_text.strip():
        return {"fields": {}, "source": "gpt-4o", "enhanced": False}

    try:
        from utils.ocr_gpt import extract_fields_gpt4o
        result = await extract_fields_gpt4o(raw_text)
        return result
    except ImportError:
        return {"fields": {}, "enhanced": False, "error": "Module OCR GPT-4o non disponible"}
    except Exception as e:
        logger.error(f"OCR Phase 2 error: {e}")
        return {"fields": {}, "enhanced": False, "error": str(e)}


# ==================== RESOURCES ====================

@router.post("/resources/download")
async def track_resource_download(request: Request):
    body = await request.json()
    await db.resource_downloads.insert_one({"resource_id": body.get("resource_id", ""), "resource_title": body.get("resource_title", ""), "created_at": datetime.now(timezone.utc).isoformat()})
    return {"success": True}


@router.get("/resources/pdf/{guide_id}")
async def download_guide_pdf(guide_id: str):
    """Generate and serve a PDF guide."""
    from utils.pdf_guides import generate_guide_pdf
    pdf_bytes = generate_guide_pdf(guide_id)
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="Guide non trouvé")

    # Track the download
    await db.resource_downloads.insert_one({
        "resource_id": guide_id,
        "resource_title": guide_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    filename = f"{guide_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/admin/resources/stats")
async def get_resource_stats(admin: dict = Depends(get_current_admin)):
    pipeline = [{"$group": {"_id": "$resource_id", "title": {"$first": "$resource_title"}, "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
    stats = await db.resource_downloads.aggregate(pipeline).to_list(100)
    total = await db.resource_downloads.count_documents({})
    return {"total_downloads": total, "by_resource": stats}


# ==================== EMAIL ADMIN ====================

@router.get("/admin/email/status")
async def get_email_status(admin: dict = Depends(get_current_admin)):
    key = os.environ.get('RESEND_API_KEY', '')
    has_key = bool(key and key.strip())
    return {"resend_installed": RESEND_AVAILABLE, "api_key_configured": has_key, "api_key_preview": f"{key[:8]}...{key[-4:]}" if has_key and len(key) > 12 else ("set" if has_key else "missing"), "sender_email": SENDER_EMAIL, "notification_email": NOTIFICATION_EMAIL or "(non configuré)"}

@router.post("/admin/email/test")
async def test_email(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    to_email = body.get("email", "")
    if not to_email:
        raise HTTPException(status_code=400, detail="Email destinataire requis")
    if not RESEND_AVAILABLE or not resend.api_key:
        return {"success": False, "message": "Resend non configuré"}
    try:
        result = await asyncio.to_thread(resend.Emails.send, {"from": SENDER_EMAIL, "to": [to_email], "subject": "Stratégie & Expertise Santé - Test email", "html": "<h2>Test réussi !</h2><p>Votre configuration email Resend fonctionne correctement.</p>"})
        return {"success": True, "message": "Email de test envoyé", "resend_id": str(result)}
    except Exception as e:
        return {"success": False, "message": f"Erreur Resend : {str(e)}"}


# ==================== SEED ====================

@router.post("/seed")
async def seed_data():
    existing_admin = await db.admins.find_one({"email": "admin@accompagn-sante.fr"})
    if not existing_admin:
        admin = AdminUser(email="admin@accompagn-sante.fr", password_hash=hash_password("Admin2024!"), nom="Administrateur")
        doc = admin.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.admins.insert_one(doc)
        logger.info("Default admin created")
    faq_count = await db.faq.count_documents({})
    if faq_count == 0:
        faqs = [
            FAQItem(question="Qu'est-ce qu'une maladie professionnelle ?", reponse="Une maladie professionnelle est une affection contractée en raison de l'exposition à un risque lors de l'exercice de votre activité professionnelle.", categorie="AT/MP", ordre=1),
            FAQItem(question="Comment faire reconnaître une maladie professionnelle ?", reponse="Vous devez déclarer votre maladie à la CPAM dans les 15 jours suivant la date de cessation de travail.", categorie="AT/MP", ordre=2),
            FAQItem(question="Qu'est-ce que l'IPP ?", reponse="L'Incapacité Permanente Partielle (IPP) est un taux qui évalue vos séquelles définitives.", categorie="AT/MP", ordre=3),
            FAQItem(question="Comment se préparer à une expertise médicale ?", reponse="Préparez un dossier complet avec tous vos documents médicaux, listez vos symptômes au quotidien.", categorie="Expertises", ordre=1),
            FAQItem(question="Qu'est-ce que la PTIA ?", reponse="La Perte Totale et Irréversible d'Autonomie est une garantie d'assurance couvrant l'impossibilité définitive d'exercer toute activité.", categorie="Assurances", ordre=1),
            FAQItem(question="Comment demander la RQTH ?", reponse="La RQTH se demande auprès de la MDPH de votre département.", categorie="MDPH", ordre=1),
        ]
        for faq in faqs:
            await db.faq.insert_one(faq.model_dump())
        logger.info(f"Seeded {len(faqs)} FAQ items")
    return {"success": True, "message": "Données initiales créées"}


# ==================== SEO ====================

@router.get("/sitemap.xml")
async def sitemap_xml():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = ""
    for path, priority, freq in SITEMAP_PAGES:
        urls += f"""  <url>\n    <loc>{SITE_URL}{path}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n  </url>\n"""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>"""
    return Response(content=xml, media_type="application/xml")

@router.get("/robots.txt")
async def robots_txt():
    content = f"""User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /admin/login\nDisallow: /espace-client\n\nSitemap: {SITE_URL}/api/sitemap.xml\n"""
    return PlainTextResponse(content=content)
