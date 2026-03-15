import asyncio
import os
import uuid
from datetime import datetime, timezone

from config import db, RESEND_AVAILABLE, SENDER_EMAIL, NOTIFICATION_EMAIL, logger

try:
    import resend
except ImportError:
    pass


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
