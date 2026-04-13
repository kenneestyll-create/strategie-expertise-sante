from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import PlainTextResponse, Response
from datetime import datetime, timezone, timedelta
import asyncio
import os
import re
import uuid

from config import db, PAYMENT_PACKAGES, AVAILABLE_SLOTS, CALL_TYPES, RESEND_AVAILABLE, SENDER_EMAIL, NOTIFICATION_EMAIL, SITE_URL, SITEMAP_PAGES, STRIPE_API_KEY, logger
from models import Booking, BookingCreate, SimulatorResult, AbandonedCheckout, FAQItem, AdminUser
from utils.auth import get_current_admin, hash_password

try:
    import resend
except ImportError:
    pass

router = APIRouter()


# ==================== BOOKING ====================

import stripe as stripe_sdk

PENDING_EXPIRY_MINUTES = 15

@router.get("/bookings/call-types")
async def get_call_types():
    """Return available call type configs for frontend."""
    result = {}
    for key, ct in CALL_TYPES.items():
        result[key] = {
            "name": ct["name"],
            "duration": ct["duration"],
            "price": ct["price"],
            "slots": ct["slots"],
        }
    return result

@router.get("/bookings/slots/{date}")
async def get_available_slots(date: str, call_type: str = "decouverte"):
    ct = CALL_TYPES.get(call_type)
    if not ct:
        return {"date": date, "slots": []}

    type_slots = ct["slots"]
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=PENDING_EXPIRY_MINUTES)
    booked = await db.bookings.find(
        {"date": date, "status": {"$ne": "annule"},
         "$nor": [{"status": "pending_payment", "created_at": {"$lt": cutoff.isoformat()}}]},
        {"_id": 0, "time_slot": 1}
    ).to_list(100)
    booked_slots = {b["time_slot"] for b in booked}
    available = [s for s in type_slots if s not in booked_slots]
    return {"date": date, "slots": available, "call_type": call_type}

@router.post("/bookings")
async def create_booking(data: BookingCreate):
    """Create a free discovery booking (direct confirmation)."""
    if data.call_type != "decouverte":
        raise HTTPException(status_code=400, detail="Les appels payants doivent passer par /bookings/checkout")

    existing_discovery = await db.bookings.find_one(
        {"email": data.email.lower(), "call_type": "decouverte", "status": {"$in": ["confirme", "pending_payment"]}},
        {"_id": 0}
    )
    if existing_discovery:
        raise HTTPException(status_code=409, detail="Vous avez deja utilise votre appel decouverte gratuit. Vous pouvez reserver un Appel Conseil.")

    existing_slot = await db.bookings.find_one(
        {"date": data.date, "time_slot": data.time_slot, "status": {"$ne": "annule"}},
        {"_id": 0}
    )
    if existing_slot:
        raise HTTPException(status_code=409, detail="Ce creneau n'est plus disponible")

    booking = Booking(**data.model_dump(), payment_status="na")
    doc = booking.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.bookings.insert_one(doc)
    return {"success": True, "booking_id": booking.id, "message": "Rendez-vous confirme"}


@router.post("/bookings/checkout")
async def create_booking_checkout(request: Request):
    """Create a pending booking + Stripe checkout for paid calls."""
    body = await request.json()
    call_type = body.get("call_type", "conseil")
    ct = CALL_TYPES.get(call_type)
    if not ct or ct["price"] <= 0:
        raise HTTPException(status_code=400, detail="Type d'appel invalide pour le paiement")
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configure")

    date = body.get("date", "")
    time_slot = body.get("time_slot", "")
    name = body.get("name", "")
    email = body.get("email", "")
    phone = body.get("phone", "")
    message = body.get("message", "")
    origin_url = body.get("origin_url", "").rstrip("/")

    if not date or not time_slot or not name or not email:
        raise HTTPException(status_code=400, detail="Champs obligatoires manquants")

    if time_slot not in ct["slots"]:
        raise HTTPException(status_code=400, detail="Creneau non autorise pour ce type d'appel")

    existing_slot = await db.bookings.find_one(
        {"date": date, "time_slot": time_slot, "status": {"$in": ["confirme", "pending_payment"]}},
        {"_id": 0}
    )
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=PENDING_EXPIRY_MINUTES)
    if existing_slot:
        if existing_slot.get("status") == "pending_payment":
            created = existing_slot.get("created_at", "")
            if isinstance(created, str) and created > cutoff.isoformat():
                raise HTTPException(status_code=409, detail="Ce creneau est temporairement reserve. Reessayez dans quelques minutes.")
        else:
            raise HTTPException(status_code=409, detail="Ce creneau n'est plus disponible")

    booking = Booking(
        date=date, time_slot=time_slot, name=name, email=email.lower(),
        phone=phone, call_type=call_type, message=message,
        status="pending_payment", payment_status="pending"
    )
    doc = booking.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.bookings.insert_one(doc)

    package_id = f"appel_{call_type}"
    PAYMENT_PACKAGES.get(package_id)  # validate exists

    success_url = f"{origin_url}/agenda?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/agenda?payment=cancelled&booking_id={booking.id}"

    stripe_sdk.api_key = STRIPE_API_KEY
    try:
        session = stripe_sdk.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": f"{ct['name']} — {ct['duration']} min ({date} a {time_slot})"},
                    "unit_amount": int(ct["price"] * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"booking_id": booking.id, "call_type": call_type, "type": "booking"},
            customer_email=email.lower(),
        )

        await db.bookings.update_one(
            {"id": booking.id},
            {"$set": {"payment_session_id": session.id}}
        )

        return {"url": session.url, "session_id": session.id, "booking_id": booking.id}
    except Exception as e:
        await db.bookings.delete_one({"id": booking.id})
        logger.error(f"Stripe booking checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la creation du paiement")


@router.post("/bookings/paypal")
async def record_booking_paypal(request: Request):
    """Record a PayPal payment for booking."""
    body = await request.json()
    order_id = body.get("order_id", "")
    call_type = body.get("call_type", "conseil")
    ct = CALL_TYPES.get(call_type)
    if not ct:
        raise HTTPException(status_code=400, detail="Type d'appel invalide")

    date = body.get("date", "")
    time_slot = body.get("time_slot", "")
    name = body.get("name", "")
    email = body.get("email", "")
    phone = body.get("phone", "")
    message = body.get("message", "")
    amount = body.get("amount", ct["price"])

    booking = Booking(
        date=date, time_slot=time_slot, name=name, email=email.lower(),
        phone=phone, call_type=call_type, message=message,
        status="confirme", payment_status="paid"
    )
    doc = booking.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['payment_method'] = 'paypal'
    doc['payment_order_id'] = order_id
    await db.bookings.insert_one(doc)

    from models import PaymentTransaction
    tx = PaymentTransaction(
        session_id=order_id, package_id=f"appel_{call_type}",
        package_name=f"{ct['name']} — {ct['duration']} min",
        amount=amount, currency="eur", email=email.lower(), customer_name=name,
        status="completed", payment_status="paid",
        metadata={"payment_method": "paypal", "booking_id": booking.id, "call_type": call_type}
    )
    tx_doc = tx.model_dump()
    tx_doc['created_at'] = tx_doc['created_at'].isoformat()
    tx_doc['updated_at'] = tx_doc['updated_at'].isoformat()
    await db.payment_transactions.insert_one(tx_doc)

    logger.info(f"Booking PayPal recorded: {booking.id} for {email}")
    return {"success": True, "booking_id": booking.id}


@router.get("/bookings/confirm-payment/{session_id}")
async def confirm_booking_payment(session_id: str):
    """Verify Stripe payment and confirm booking."""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configure")

    booking = await db.bookings.find_one({"payment_session_id": session_id}, {"_id": 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Reservation non trouvee")
    if booking.get("status") == "confirme":
        return {"success": True, "booking_id": booking["id"], "already_confirmed": True}

    stripe_sdk.api_key = STRIPE_API_KEY
    try:
        session = stripe_sdk.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            await db.bookings.update_one(
                {"payment_session_id": session_id},
                {"$set": {"status": "confirme", "payment_status": "paid"}}
            )
            return {"success": True, "booking_id": booking["id"],
                    "date": booking["date"], "time_slot": booking["time_slot"],
                    "call_type": booking.get("call_type", "conseil")}
        else:
            return {"success": False, "payment_status": session.payment_status}
    except Exception as e:
        logger.error(f"Confirm booking payment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur de verification du paiement")


@router.delete("/bookings/cancel-pending/{booking_id}")
async def cancel_pending_booking(booking_id: str):
    """Cancel a pending booking (payment cancelled/abandoned)."""
    result = await db.bookings.update_one(
        {"id": booking_id, "status": "pending_payment"},
        {"$set": {"status": "annule"}}
    )
    return {"success": result.modified_count > 0}

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
    doc['autre_situation'] = body.get("autre_situation", "")  # Store 'Autre situation' text
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

URGENT_PRICES = {"2h": 5000, "30min": 8000}  # centimes

@router.post("/alerte-urgente")
async def create_urgent_alert_checkout(request: Request):
    """Create a pending urgent alert + Stripe checkout session."""
    body = await request.json()
    if not body.get("nom") or not body.get("telephone") or not body.get("email"):
        raise HTTPException(status_code=400, detail="Nom, téléphone et email requis")

    formule = body.get("formule", "2h")
    if formule not in URGENT_PRICES:
        raise HTTPException(status_code=400, detail="Formule invalide")

    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré")

    alert = {
        "id": str(uuid.uuid4()),
        "nom": body["nom"],
        "telephone": body["telephone"],
        "email": body.get("email", ""),
        "message": body.get("message", ""),
        "formule": formule,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending_payment",
        "payment_status": "pending",
        "traite": False,
    }
    await db.urgent_alerts.insert_one(alert)

    prix_label = "80€" if formule == "30min" else "50€"
    delai_label = "30 minutes" if formule == "30min" else "2 heures"
    origin_url = body.get("origin_url", "").rstrip("/")
    success_url = f"{origin_url}/?urgent_payment=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/?urgent_payment=cancelled&alert_id={alert['id']}"

    stripe_sdk.api_key = STRIPE_API_KEY
    try:
        session = stripe_sdk.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": f"Question urgente — Réponse sous {delai_label} ({prix_label})"},
                    "unit_amount": URGENT_PRICES[formule],
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"alert_id": alert["id"], "formule": formule, "type": "alerte_urgente"},
            customer_email=body["email"].lower(),
        )
        await db.urgent_alerts.update_one(
            {"id": alert["id"]},
            {"$set": {"payment_session_id": session.id}}
        )
        return {"url": session.url, "session_id": session.id, "alert_id": alert["id"]}
    except Exception as e:
        await db.urgent_alerts.delete_one({"id": alert["id"]})
        logger.error(f"Stripe urgent alert checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création du paiement")


@router.get("/alerte-urgente/confirm-payment/{session_id}")
async def confirm_urgent_alert_payment(session_id: str):
    """Verify Stripe payment and confirm urgent alert + send notification."""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré")

    alert = await db.urgent_alerts.find_one({"payment_session_id": session_id}, {"_id": 0})
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    if alert.get("payment_status") == "paid":
        return {"success": True, "alert_id": alert["id"], "already_confirmed": True}

    stripe_sdk.api_key = STRIPE_API_KEY
    try:
        session = stripe_sdk.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            await db.urgent_alerts.update_one(
                {"payment_session_id": session_id},
                {"$set": {"status": "nouveau", "payment_status": "paid"}}
            )
            # Send notification email to admin
            if RESEND_AVAILABLE and os.environ.get('RESEND_API_KEY') and NOTIFICATION_EMAIL:
                try:
                    prix = "80€" if alert["formule"] == "30min" else "50€"
                    await asyncio.to_thread(resend.Emails.send, {
                        "from": SENDER_EMAIL,
                        "to": [NOTIFICATION_EMAIL],
                        "subject": f"ALERTE URGENTE PAYÉE - {alert['nom']} ({prix})",
                        "html": f"""<h2 style="color:red;">Demande urgente — PAIEMENT CONFIRMÉ</h2>
                        <p><strong>Formule:</strong> Réponse sous {alert['formule']} — {prix}</p>
                        <p><strong>Nom:</strong> {alert['nom']}</p>
                        <p><strong>Téléphone:</strong> {alert['telephone']}</p>
                        <p><strong>Email:</strong> {alert.get('email', 'Non renseigné')}</p>
                        <p><strong>Message:</strong> {alert.get('message', 'Aucun')}</p>
                        <hr/><p style="color:green;font-weight:bold;">Paiement reçu via Stripe.</p>"""
                    })
                except Exception as e:
                    logger.error(f"Urgent alert email error: {e}")
            return {"success": True, "alert_id": alert["id"], "formule": alert["formule"]}
        else:
            return {"success": False, "payment_status": session.payment_status}
    except Exception as e:
        logger.error(f"Confirm urgent payment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur de vérification du paiement")

@router.delete("/alerte-urgente/cancel/{alert_id}")
async def cancel_pending_urgent_alert(alert_id: str):
    """Cancel a pending urgent alert (payment cancelled/abandoned)."""
    await db.urgent_alerts.delete_one({"id": alert_id, "payment_status": "pending"})
    return {"success": True}

@router.post("/alerte-urgente/paypal")
async def record_urgent_paypal(request: Request):
    """Record a PayPal payment for urgent questions."""
    body = await request.json()
    order_id = body.get("order_id", "")
    nom = body.get("nom", "")
    telephone = body.get("telephone", "")
    email = body.get("email", "")
    message = body.get("message", "")
    formule = body.get("formule", "2h")
    amount = body.get("amount", 50)

    alert_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.urgent_alerts.insert_one({
        "id": alert_id, "nom": nom, "telephone": telephone, "email": email,
        "message": message, "formule": formule, "payment_method": "paypal",
        "payment_order_id": order_id, "payment_status": "paid", "amount": amount,
        "traite": False, "status": "nouveau", "created_at": now,
    })

    # Record payment transaction
    from models import PaymentTransaction
    tx = PaymentTransaction(
        session_id=order_id, package_id=f"urgent_{formule}",
        package_name=f"Question urgente — {'30 min' if formule == '30min' else '2h'}",
        amount=amount, currency="eur", email=email, customer_name=nom,
        status="completed", payment_status="paid",
        metadata={"payment_method": "paypal", "formule": formule}
    )
    doc = tx.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.payment_transactions.insert_one(doc)

    logger.info(f"Urgent alert PayPal recorded: {alert_id} for {email} ({formule})")
    return {"success": True, "alert_id": alert_id}


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
            resend.Emails.send({"from": SENDER_EMAIL, "to": item["email"], "subject": "Stratégie & Expertise Santé - Finalisez votre démarche", "html": f"""<h2>Bonjour {item.get('name', '')},</h2><p>Vous aviez commencé à réserver notre prestation <strong>{item.get('package_name', '')}</strong>.</p><p>N'hésitez pas à finaliser votre inscription ou à nous contacter si vous avez des questions.</p><p>Première consultation gratuite — 10 minutes, sans engagement.</p><p>Cordialement,<br>Stratégie & Expertise Santé</p>"""})
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


@router.post("/resources/request-guide")
async def request_guide_by_email(request: Request):
    """Collect email before allowing PDF download — lead generation."""
    body = await request.json()
    email = (body.get("email") or "").strip().lower()
    guide_id = body.get("guide_id", "")
    guide_title = body.get("guide_title", "")
    category = body.get("category", "")

    if not email or "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail="Adresse email invalide")
    if not guide_id:
        raise HTTPException(status_code=400, detail="Guide non spécifié")

    # Store lead with category for segmentation
    await db.guide_leads.insert_one({
        "email": email,
        "guide_id": guide_id,
        "guide_title": guide_title,
        "category": category,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    # Also track the download
    await db.resource_downloads.insert_one({
        "resource_id": guide_id,
        "resource_title": guide_title,
        "email": email,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"success": True, "guide_id": guide_id}


@router.get("/resources/pdf/{guide_id}")
async def download_guide_pdf(guide_id: str):
    """Generate and serve a PDF guide."""
    from utils.pdf_guides import generate_guide_pdf
    pdf_bytes = generate_guide_pdf(guide_id)
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="Guide non trouvé")

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


@router.get("/admin/guide-leads/stats")
async def get_guide_leads_stats(admin: dict = Depends(get_current_admin)):
    """Stats for guide email leads and followup emails."""
    total_leads = await db.guide_leads.count_documents({})
    followup_sent = await db.guide_leads.count_documents({"followup_sent": True})
    pending_followup = await db.guide_leads.count_documents({"followup_sent": {"$ne": True}})

    # By category
    cat_pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
    by_category = await db.guide_leads.aggregate(cat_pipeline).to_list(20)

    # By guide
    guide_pipeline = [{"$group": {"_id": "$guide_id", "title": {"$first": "$guide_title"}, "category": {"$first": "$category"}, "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
    by_guide = await db.guide_leads.aggregate(guide_pipeline).to_list(20)

    # Followup email performance
    total_followups = await db.guide_followups.count_documents({})
    opened = await db.guide_followups.count_documents({"opened": True})
    clicked = await db.guide_followups.count_documents({"clicked": True})

    # Recent leads
    recent = await db.guide_leads.find({}, {"_id": 0}).sort("created_at", -1).to_list(20)

    return {
        "total_leads": total_leads,
        "followup_sent": followup_sent,
        "pending_followup": pending_followup,
        "by_category": by_category,
        "by_guide": by_guide,
        "followup_emails": {
            "total_sent": total_followups,
            "opened": opened,
            "clicked": clicked,
            "open_rate": round(opened / total_followups * 100, 1) if total_followups else 0,
            "click_rate": round(clicked / total_followups * 100, 1) if total_followups else 0,
        },
        "recent_leads": recent,
    }


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
    # Add dynamic SEO guide pages
    seo_pages = await db.seo_pages.find({"active": True}, {"_id": 0, "slug": 1}).to_list(500)
    for page in seo_pages:
        urls += f"""  <url>\n    <loc>{SITE_URL}/guide/{page['slug']}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n"""
    if seo_pages:
        urls += f"""  <url>\n    <loc>{SITE_URL}/guides-pratiques</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.6</priority>\n  </url>\n"""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>"""
    return Response(content=xml, media_type="application/xml")

@router.get("/robots.txt")
async def robots_txt():
    content = f"""User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /admin/login\nDisallow: /espace-client\n\nSitemap: {SITE_URL}/api/sitemap.xml\n"""
    return PlainTextResponse(content=content)


# ==================== CONSENT LOG ====================

@router.post("/consent-log")
async def log_consent(request: Request):
    """Log CGV/retractation consent before payment — legally required."""
    body = await request.json()
    if not body.get("email") or not body.get("service"):
        raise HTTPException(status_code=400, detail="Email et service requis")
    consent = {
        "id": str(uuid.uuid4()),
        "email": body["email"].lower().strip(),
        "service": body["service"],
        "cgv_accepted": body.get("cgv_accepted", False),
        "retractation_waived": body.get("retractation_waived", False),
        "cgv_version": "2026-04-11",
        "ip_address": request.client.host if request.client else "",
        "user_agent": request.headers.get("user-agent", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.consent_logs.insert_one(consent)
    return {"success": True, "consent_id": consent["id"]}


