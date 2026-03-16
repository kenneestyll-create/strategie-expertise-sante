import asyncio
import os
import uuid
from datetime import datetime, timezone

from config import db, RESEND_AVAILABLE, SENDER_EMAIL, NOTIFICATION_EMAIL, SITE_URL, logger

try:
    import resend
except ImportError:
    pass

try:
    from utils.push import send_push_to_client
    PUSH_AVAILABLE = True
except Exception:
    PUSH_AVAILABLE = False


async def send_notification_email(contact):
    if not RESEND_AVAILABLE or not os.environ.get('RESEND_API_KEY') or not NOTIFICATION_EMAIL:
        logger.info("Email notification skipped - Resend not configured")
        return False

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2D2A26;">Nouvelle demande de contact</h2>
        <div style="background: #F9F7F2; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Nom:</strong> {contact.prenom} {contact.nom}</p>
            <p><strong>Email:</strong> {contact.email}</p>
            <p><strong>Téléphone:</strong> {contact.telephone or 'Non renseigné'}</p>
            <p><strong>Type d'accompagnement:</strong> {contact.type_accompagnement or 'Non spécifié'}</p>
            <p><strong>Sujet:</strong> {contact.sujet}</p>
            <hr style="border: 1px solid #E5E0D6;">
            <p><strong>Message:</strong></p>
            <p>{contact.message}</p>
        </div>
    </body>
    </html>
    """

    params = {
        "from": SENDER_EMAIL,
        "to": [NOTIFICATION_EMAIL],
        "subject": f"Nouvelle demande: {contact.sujet}",
        "html": html_content
    }

    try:
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Notification email sent for contact {contact.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification email: {str(e)}")
        return False


async def notify_admin_premium_analysis(analysis_type: str, email: str, name: str, amount: float):
    if not RESEND_AVAILABLE or not os.environ.get('RESEND_API_KEY') or not NOTIFICATION_EMAIL:
        logger.info("Premium analysis notification skipped - Resend not configured")
        return
    type_label = "StrategiIA" if analysis_type == "strategiia" else "Dossier Express"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #1a1a2e; color: #fff; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
            <h2 style="margin: 0; color: #d4a44a;">Nouvelle Analyse Premium</h2>
        </div>
        <div style="background: #F9F7F2; padding: 20px; border-radius: 0 0 8px 8px; border: 1px solid #E5E0D6;">
            <p style="font-size: 16px;"><strong>Type :</strong> {type_label}</p>
            <p><strong>Client :</strong> {name or 'Non renseigne'}</p>
            <p><strong>Email :</strong> {email}</p>
            <p><strong>Montant :</strong> {amount:.0f} EUR</p>
            <p><strong>Date :</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <hr style="border: 1px solid #E5E0D6;">
            <p style="color: #b94e48; font-weight: bold;">Action requise : relecture et enrichissement expert du rapport.</p>
        </div>
    </body>
    </html>
    """
    try:
        await asyncio.to_thread(resend.Emails.send, {
            "from": SENDER_EMAIL,
            "to": [NOTIFICATION_EMAIL],
            "subject": f"[PREMIUM] Nouvelle analyse {type_label} - {name or email}",
            "html": html_content
        })
        logger.info(f"Premium analysis notification sent for {email}")
    except Exception as e:
        logger.error(f"Failed to send premium notification: {e}")


async def create_client_notification(client_id: str, notif_type: str, title: str, message: str, case_id: str = None, send_email: bool = True):
    notif = {
        "id": str(uuid.uuid4()),
        "client_id": client_id,
        "type": notif_type,
        "title": title,
        "message": message,
        "case_id": case_id,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.client_notifications.insert_one(notif)

    # Push notification
    if PUSH_AVAILABLE:
        try:
            client_user = await db.client_users.find_one({"id": client_id}, {"_id": 0, "notifications_push": 1})
            if client_user and client_user.get("notifications_push", True):
                url = f"/espace-client"
                await send_push_to_client(db, client_id, title=title, body=message, url=url, tag=notif_type)
                logger.info(f"Push notification sent to client {client_id}: {title}")
        except Exception as e:
            logger.error(f"Push notification failed for client {client_id}: {e}")

    if send_email:
        client = await db.client_users.find_one({"id": client_id}, {"_id": 0, "email": 1, "name": 1, "notifications_email": 1})
        if client and client.get("notifications_email", True) and RESEND_AVAILABLE and os.environ.get('RESEND_API_KEY'):
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [client["email"]],
                    "subject": f"Stratégie & Expertise Santé — {title}",
                    "html": f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background: #1a1a2e; color: #fff; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
                            <h2 style="margin: 0; color: #d4a44a;">{title}</h2>
                        </div>
                        <div style="background: #F9F7F2; padding: 20px; border-radius: 0 0 8px 8px; border: 1px solid #E5E0D6;">
                            <p>Bonjour {client.get('name', '')},</p>
                            <p>{message}</p>
                            <p style="margin-top: 20px;">
                                <a href="{os.environ.get('FRONTEND_URL', 'https://strategie-expertise-sante.fr')}/espace-client"
                                   style="background: #1a1a2e; color: #d4a44a; padding: 12px 24px; border-radius: 6px; text-decoration: none; display: inline-block;">
                                    Accéder à mon espace client
                                </a>
                            </p>
                            <p style="color: #888; font-size: 12px; margin-top: 20px;">
                                Cet email a été envoyé automatiquement. Vous pouvez désactiver les notifications email dans votre espace client.
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                })
                logger.info(f"Notification email sent to {client['email']}: {title}")
            except Exception as e:
                logger.error(f"Failed to send notification email to {client.get('email')}: {e}")


# ==================== COMPLETENESS NOTIFICATIONS ====================

COMPLETENESS_THRESHOLDS = [
    {"pct": 50, "title": "Votre dossier avance bien !", "emoji": "📊"},
    {"pct": 80, "title": "Votre dossier est presque complet !", "emoji": "🎯"},
    {"pct": 100, "title": "Félicitations, dossier complet !", "emoji": "🎉"},
]


async def check_and_send_completeness_notification(client_id: str, completeness_pct: int, missing_docs: list, case_type: str = None):
    """Check if a completeness threshold has been newly reached and send email notification."""
    if completeness_pct <= 0:
        return

    client_user = await db.client_users.find_one({"id": client_id}, {"_id": 0, "email": 1, "name": 1, "notifications_email": 1})
    if not client_user or not client_user.get("notifications_email", True):
        return

    for threshold in COMPLETENESS_THRESHOLDS:
        if completeness_pct < threshold["pct"]:
            continue

        # Check if already sent for this threshold
        already_sent = await db.completeness_notifications.find_one(
            {"client_id": client_id, "threshold_pct": threshold["pct"]}, {"_id": 0, "id": 1}
        )
        if already_sent:
            continue

        # New threshold reached - send notification
        name = client_user.get("name", "")
        email = client_user["email"]
        prenom = name.split()[0] if name else ""
        missing_count = len(missing_docs)
        threshold_pct = threshold["pct"]

        if threshold_pct == 100:
            body_text = "Tous les documents essentiels ont été fournis. Votre dossier est prêt pour une analyse complète."
            missing_html = ""
        else:
            body_text = f"Votre dossier est désormais complété à {completeness_pct}%."
            if missing_docs:
                missing_items = "".join(f'<li style="margin:4px 0;">{d.get("label", d) if isinstance(d, dict) else d}</li>' for d in missing_docs[:5])
                missing_html = f"""
                <div style="background:#FFF8E1;padding:12px 16px;border-radius:6px;border-left:4px solid #d4a44a;margin:16px 0;">
                    <p style="margin:0 0 8px;font-weight:600;color:#7B6B2E;">Documents encore manquants ({missing_count}) :</p>
                    <ul style="margin:0;padding-left:20px;color:#5D4E1A;">{missing_items}</ul>
                </div>"""
            else:
                missing_html = ""

        site_url = os.environ.get("FRONTEND_URL", SITE_URL)
        html_content = f"""
        <html>
        <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:0;background:#f5f5f5;">
            <div style="background:#1a1a2e;color:#fff;padding:24px;text-align:center;">
                <h1 style="margin:0;color:#d4a44a;font-size:22px;">{threshold["emoji"]} {threshold["title"]}</h1>
            </div>
            <div style="background:#FFFFFF;padding:24px;border:1px solid #E5E0D6;">
                <p style="font-size:16px;">Bonjour <strong>{prenom}</strong>,</p>
                <p>{body_text}</p>
                <div style="background:#F0F7F0;padding:16px;border-radius:8px;text-align:center;margin:20px 0;">
                    <p style="margin:0;font-size:36px;font-weight:bold;color:#16a34a;">{completeness_pct}%</p>
                    <p style="margin:4px 0 0;color:#666;font-size:13px;">de complétude</p>
                </div>
                {missing_html}
                <div style="text-align:center;margin:24px 0;">
                    <a href="{site_url}/espace-client?tab=documents"
                       style="background:#1a1a2e;color:#d4a44a;padding:14px 28px;border-radius:6px;text-decoration:none;display:inline-block;font-weight:600;font-size:14px;">
                        {"Voir mon dossier complet" if threshold_pct == 100 else "Compléter mon dossier"}
                    </a>
                </div>
                <p style="color:#888;font-size:11px;text-align:center;margin-top:20px;">
                    Stratégie &amp; Expertise Santé — Cet email est envoyé automatiquement.
                </p>
            </div>
        </body>
        </html>
        """

        # Record the notification
        notif_record = {
            "id": str(uuid.uuid4()),
            "client_id": client_id,
            "client_email": email,
            "client_name": name,
            "threshold_pct": threshold_pct,
            "actual_pct": completeness_pct,
            "case_type": case_type,
            "missing_docs_count": missing_count,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Send email
        if RESEND_AVAILABLE and os.environ.get('RESEND_API_KEY'):
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [email],
                    "subject": f"Stratégie & Expertise Santé — {threshold['title']}",
                    "html": html_content
                })
                notif_record["status"] = "sent"
                logger.info(f"Completeness notification sent to {email}: {threshold_pct}% threshold (actual: {completeness_pct}%)")
            except Exception as e:
                notif_record["status"] = "failed"
                notif_record["error"] = str(e)
                logger.error(f"Failed to send completeness notification to {email}: {e}")
        else:
            notif_record["status"] = "skipped"
            logger.info(f"Completeness notification skipped (Resend not configured): {email} at {threshold_pct}%")

        await db.completeness_notifications.insert_one(notif_record)

        # Also create in-app notification
        if threshold_pct < 100:
            msg = f"Votre dossier est complété à {completeness_pct}%. Il manque encore {missing_count} document(s) essentiels."
        else:
            msg = "Tous vos documents essentiels sont fournis. Votre dossier est prêt pour une analyse approfondie !"
        await create_client_notification(client_id, "completeness", threshold["title"], msg)
