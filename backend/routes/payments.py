from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import uuid

import stripe as stripe_sdk

from config import db, PAYMENT_PACKAGES, STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_MODE, PAYPAL_CLIENT_ID, PAYPAL_SECRET, PAYPAL_BASE_URL, logger
from models import PaymentTransaction, CreateCheckoutRequest, ReferralUse
from utils.auth import get_current_admin

router = APIRouter()


@router.get("/payments/packages")
async def get_payment_packages():
    return [{"id": k, "name": v["name"], "amount": v["amount"], "currency": v["currency"]} for k, v in PAYMENT_PACKAGES.items()]

@router.post("/payments/checkout")
async def create_checkout_session(request_data: CreateCheckoutRequest, request: Request):
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    if request_data.package_id not in PAYMENT_PACKAGES:
        raise HTTPException(status_code=400, detail="Forfait invalide")

    package = PAYMENT_PACKAGES[request_data.package_id]
    base_amount = package["amount"]
    discount_percent = 0
    discount_type = ""

    if request_data.customer_email:
        client = await db.client_history.find_one({"email": request_data.customer_email.lower()}, {"_id": 0})
        if client and client.get("orders_count", 0) >= 1:
            discount_percent = 15
            discount_type = "fidélité"

    if discount_percent == 0 and request_data.referral_code:
        referral = await db.referral_codes.find_one({"code": request_data.referral_code.upper(), "is_active": True}, {"_id": 0})
        if referral:
            discount_percent = 10
            discount_type = "parrainage"
            referral_use = ReferralUse(referral_code=request_data.referral_code.upper(), referred_email=request_data.customer_email or "", referred_name=request_data.customer_name, discount_applied=10.0)
            doc_ref = referral_use.model_dump()
            doc_ref['created_at'] = doc_ref['created_at'].isoformat()
            await db.referral_uses.insert_one(doc_ref)
            await db.referral_codes.update_one({"code": request_data.referral_code.upper()}, {"$inc": {"uses_count": 1}})

    final_amount = round(base_amount * (1 - discount_percent / 100), 2)

    origin_url = request_data.origin_url.rstrip('/')
    success_url = f"{origin_url}/tarifs?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/tarifs?payment=cancelled"

    stripe_sdk.api_key = STRIPE_API_KEY

    metadata = {
        "package_id": request_data.package_id, "package_name": package["name"],
        "customer_email": request_data.customer_email or "", "customer_name": request_data.customer_name or "",
        "discount_percent": str(discount_percent), "discount_type": discount_type, "original_amount": str(base_amount)
    }

    try:
        session = stripe_sdk.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": package["currency"],
                    "product_data": {"name": package["name"]},
                    "unit_amount": int(final_amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata,
        )

        if request_data.customer_email:
            await db.client_history.update_one(
                {"email": request_data.customer_email.lower()},
                {"$inc": {"orders_count": 1}, "$set": {"last_order_at": datetime.now(timezone.utc).isoformat(), "name": request_data.customer_name},
                 "$setOnInsert": {"id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True
            )

        transaction = PaymentTransaction(
            session_id=session.id, package_id=request_data.package_id, package_name=package["name"],
            amount=final_amount, currency=package["currency"], email=request_data.customer_email,
            customer_name=request_data.customer_name, status="pending", payment_status="initiated", metadata=metadata
        )
        doc = transaction.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.payment_transactions.insert_one(doc)

        return {"url": session.url, "session_id": session.id, "discount_applied": discount_percent, "discount_type": discount_type, "original_amount": base_amount, "final_amount": final_amount}
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création du paiement")

@router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, request: Request):
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if transaction and transaction.get("payment_status") == "paid":
        return {"status": "complete", "payment_status": "paid", "package_name": transaction.get("package_name"), "amount": transaction.get("amount"), "currency": transaction.get("currency")}

    stripe_sdk.api_key = STRIPE_API_KEY
    try:
        session = stripe_sdk.checkout.Session.retrieve(session_id)
        payment_status = session.payment_status or "unknown"
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"status": session.status, "payment_status": payment_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        amount_total = session.amount_total or 0
        return {"status": session.status, "payment_status": payment_status, "amount": amount_total / 100, "currency": session.currency, "metadata": dict(session.metadata or {})}
    except Exception as e:
        logger.error(f"Payment status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la vérification du paiement")

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    body = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    stripe_sdk.api_key = STRIPE_API_KEY
    try:
        event = stripe_sdk.Webhook.construct_event(body, sig_header, STRIPE_WEBHOOK_SECRET)
    except stripe_sdk.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Webhook construct error: {e}")
        raise HTTPException(status_code=400, detail="Webhook error")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id", "")
        payment_status = session.get("payment_status", "unknown")
        now = datetime.now(timezone.utc).isoformat()
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"status": "complete", "payment_status": payment_status, "updated_at": now}}
        )
        if payment_status == "paid":
            result = await db.dossier_express.update_many(
                {"session_id": session_id, "payment_verified": False},
                {"$set": {"payment_verified": True, "payment_confirmed_at": now}}
            )
            if result.modified_count > 0:
                logger.info(f"Webhook: marked {result.modified_count} dossier(s) as payment_verified for session {session_id}")

            booking_result = await db.bookings.update_one(
                {"payment_session_id": session_id, "status": "pending_payment"},
                {"$set": {"status": "confirme", "payment_status": "paid"}}
            )
            if booking_result.modified_count > 0:
                logger.info(f"Webhook: confirmed booking payment for session {session_id}")

    return {"received": True}


# ==================== PAYPAL ====================

@router.post("/paypal/calculate")
async def calculate_paypal_amount(request: Request):
    body = await request.json()
    package_id = body.get("package_id")
    if package_id not in PAYMENT_PACKAGES:
        raise HTTPException(status_code=400, detail="Forfait invalide")
    package = PAYMENT_PACKAGES[package_id]
    base_amount = package["amount"]
    discount_percent = 0
    discount_type = ""
    customer_email = body.get("customer_email", "")
    referral_code = body.get("referral_code")
    if customer_email:
        client_doc = await db.client_history.find_one({"email": customer_email.lower()}, {"_id": 0})
        if client_doc and client_doc.get("orders_count", 0) >= 1:
            discount_percent = 15
            discount_type = "fidélité"
    if discount_percent == 0 and referral_code:
        referral = await db.referral_codes.find_one({"code": referral_code.upper(), "is_active": True}, {"_id": 0})
        if referral:
            discount_percent = 10
            discount_type = "parrainage"
    final_amount = round(base_amount * (1 - discount_percent / 100), 2)
    return {"package_name": package["name"], "base_amount": base_amount, "discount_percent": discount_percent, "discount_type": discount_type, "final_amount": final_amount}

@router.post("/paypal/record")
async def record_paypal_payment(request: Request):
    body = await request.json()
    order_id = body.get("order_id", "")
    package_id = body.get("package_id", "")
    customer_email = body.get("customer_email", "")
    customer_name = body.get("customer_name", "")
    amount = body.get("amount", 0)
    referral_code = body.get("referral_code")
    package = PAYMENT_PACKAGES.get(package_id, {})

    if PAYPAL_CLIENT_ID and PAYPAL_SECRET and order_id:
        import httpx
        try:
            async with httpx.AsyncClient() as http_client:
                token_resp = await http_client.post(
                    f"{PAYPAL_BASE_URL}/v1/oauth2/token",
                    data={"grant_type": "client_credentials"},
                    auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
                )
                if token_resp.status_code == 200:
                    access_token = token_resp.json()["access_token"]
                    order_resp = await http_client.get(
                        f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}",
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    if order_resp.status_code == 200:
                        order_data = order_resp.json()
                        if order_data.get("status") != "COMPLETED":
                            raise HTTPException(status_code=402, detail="Paiement PayPal non confirmé")
                    else:
                        raise HTTPException(status_code=402, detail="Impossible de vérifier le paiement PayPal")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"PayPal verification error: {e}")

    transaction = PaymentTransaction(
        session_id=order_id, package_id=package_id, package_name=package.get("name", package_id),
        amount=amount, currency="eur", email=customer_email, customer_name=customer_name,
        status="completed", payment_status="paid", metadata={"payment_method": "paypal"}
    )
    doc = transaction.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.payment_transactions.insert_one(doc)

    if customer_email:
        await db.client_history.update_one(
            {"email": customer_email.lower()},
            {"$inc": {"orders_count": 1}, "$set": {"last_order_at": datetime.now(timezone.utc).isoformat(), "name": customer_name},
             "$setOnInsert": {"id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )

    if referral_code:
        referral = await db.referral_codes.find_one({"code": referral_code.upper(), "is_active": True}, {"_id": 0})
        if referral:
            referral_use = ReferralUse(referral_code=referral_code.upper(), referred_email=customer_email, referred_name=customer_name, discount_applied=10.0)
            doc_ref = referral_use.model_dump()
            doc_ref['created_at'] = doc_ref['created_at'].isoformat()
            await db.referral_uses.insert_one(doc_ref)
            await db.referral_codes.update_one({"code": referral_code.upper()}, {"$inc": {"uses_count": 1}})

    return {"success": True, "order_id": order_id}
