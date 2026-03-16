import asyncio
import os
import uuid
from datetime import datetime, timezone, timedelta

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


# ==================== INACTIVITY REMINDERS ====================

REMINDER_LEVELS = [
    {"level": 1, "days": 7, "subject": "Votre dossier vous attend", "tone": "douce"},
    {"level": 2, "days": 14, "subject": "N'oubliez pas de compléter votre dossier", "tone": "motivante"},
    {"level": 3, "days": 21, "subject": "Dernière relance — Finalisez votre dossier", "tone": "urgente"},
]


def _build_reminder_html(prenom: str, completeness_pct: int, missing_docs: list, level: int, site_url: str) -> str:
    missing_count = len(missing_docs)

    if level == 1:
        intro = f"Nous avons remarqué que vous n'avez pas ajouté de documents récemment. Votre dossier est actuellement à <strong>{completeness_pct}%</strong> de complétude."
        motivation = "En complétant votre dossier, vous profiterez d'une analyse StratégiIA plus précise et de recommandations personnalisées."
    elif level == 2:
        intro = f"Votre dossier est toujours en attente de documents. Il est actuellement complété à <strong>{completeness_pct}%</strong>."
        motivation = "Chaque document ajouté renforce la qualité de notre analyse et nous permet de mieux vous accompagner dans vos démarches."
    else:
        intro = f"C'est notre dernière relance automatique. Votre dossier est à <strong>{completeness_pct}%</strong> et attend vos documents."
        motivation = "Finalisez votre dossier maintenant pour bénéficier de toute la puissance de notre expertise et de StratégiIA."

    if missing_docs:
        items = "".join(f'<li style="margin:4px 0;color:#5D4E1A;">{d.get("label", d) if isinstance(d, dict) else d}</li>' for d in missing_docs[:5])
        extra = f'<p style="color:#7B6B2E;font-size:12px;margin-top:4px;">et {missing_count - 5} autre(s)...</p>' if missing_count > 5 else ""
        missing_html = f"""
        <div style="background:#FFF8E1;padding:12px 16px;border-radius:6px;border-left:4px solid #d4a44a;margin:16px 0;">
            <p style="margin:0 0 8px;font-weight:600;color:#7B6B2E;">Il manque encore {missing_count} document(s) :</p>
            <ul style="margin:0;padding-left:20px;">{items}</ul>
            {extra}
        </div>"""
    else:
        missing_html = ""

    urgency_bar = ""
    if level >= 2:
        color = "#ea580c" if level == 3 else "#f59e0b"
        urgency_bar = f'<div style="background:{color};color:#fff;text-align:center;padding:8px;font-size:13px;font-weight:600;">Relance {level}/3 — {"Dernière relance" if level == 3 else "Pensez à compléter votre dossier"}</div>'

    return f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:0;background:#f5f5f5;">
        <div style="background:#1a1a2e;color:#fff;padding:24px;text-align:center;">
            <h1 style="margin:0;color:#d4a44a;font-size:20px;">Stratégie &amp; Expertise Santé</h1>
            <p style="margin:8px 0 0;color:#ccc;font-size:13px;">Votre dossier attend vos documents</p>
        </div>
        {urgency_bar}
        <div style="background:#FFFFFF;padding:24px;border:1px solid #E5E0D6;">
            <p style="font-size:16px;">Bonjour <strong>{prenom}</strong>,</p>
            <p>{intro}</p>
            <div style="background:#F0F7F0;padding:16px;border-radius:8px;text-align:center;margin:20px 0;">
                <p style="margin:0;font-size:36px;font-weight:bold;color:{'#ea580c' if completeness_pct < 30 else '#f59e0b'}">{completeness_pct}%</p>
                <p style="margin:4px 0 0;color:#666;font-size:13px;">de complétude</p>
            </div>
            {missing_html}
            <p style="color:#555;font-size:14px;">{motivation}</p>
            <div style="text-align:center;margin:24px 0;">
                <a href="{site_url}/espace-client?tab=documents"
                   style="background:#1a1a2e;color:#d4a44a;padding:14px 28px;border-radius:6px;text-decoration:none;display:inline-block;font-weight:600;font-size:14px;">
                    Compléter mon dossier
                </a>
            </div>
            <p style="color:#888;font-size:11px;text-align:center;margin-top:20px;">
                Stratégie &amp; Expertise Santé — Cet email est envoyé automatiquement.
                <br/>Si vous ne souhaitez plus recevoir ces relances, contactez-nous.
            </p>
        </div>
    </body>
    </html>
    """


async def run_inactivity_reminders(inactivity_days: int = 7, max_completeness: int = 50):
    """Scan all clients and send inactivity reminders for those below completeness threshold."""
    from routes.client import ESSENTIAL_DOCS, _match_doc_to_essential

    now = datetime.now(timezone.utc)
    site_url = os.environ.get("FRONTEND_URL", SITE_URL)
    results = {"scanned": 0, "eligible": 0, "sent": 0, "failed": 0, "skipped": 0, "already_reminded": 0}

    clients = await db.client_users.find(
        {"reminders_paused": {"$ne": True}},
        {"_id": 0, "id": 1, "email": 1, "name": 1}
    ).to_list(1000)

    for client in clients:
        results["scanned"] += 1
        cid = client["id"]
        email = client["email"]
        name = client.get("name", "")
        prenom = name.split()[0] if name else ""

        # Get latest document upload date
        latest_doc = await db.client_documents.find_one(
            {"client_id": cid}, {"_id": 0, "uploaded_at": 1, "created_at": 1},
            sort=[("uploaded_at", -1)]
        )
        last_upload = None
        if latest_doc:
            ts = latest_doc.get("uploaded_at") or latest_doc.get("created_at")
            if ts:
                if isinstance(ts, str):
                    last_upload = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                elif isinstance(ts, datetime):
                    last_upload = ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)

        # If uploaded recently, skip
        if last_upload and (now - last_upload).days < inactivity_days:
            continue

        # Calculate completeness
        docs = await db.client_documents.find({"client_id": cid}, {"_id": 0, "category": 1, "name": 1}).to_list(500)
        doc_categories = [d.get("category", "") for d in docs] + [d.get("name", "") for d in docs]

        # Detect case type
        case_type = None
        la = await db.strategiia_analyses.find_one({"email": email}, {"_id": 0, "type_dossier": 1}, sort=[("created_at", -1)])
        if la:
            case_type = la.get("type_dossier")
        if not case_type:
            ld = await db.dossier_express.find_one({"email": email}, {"_id": 0, "type_dossier": 1}, sort=[("created_at", -1)])
            if ld:
                case_type = ld.get("type_dossier")

        essential_list = ESSENTIAL_DOCS.get(case_type, ESSENTIAL_DOCS.get("at", []))
        found = 0
        missing = []
        for ed in essential_list:
            if _match_doc_to_essential(doc_categories, ed["key"], ed["category"]):
                found += 1
            else:
                missing.append(ed)
        comp_pct = round((found / len(essential_list)) * 100) if essential_list else 100

        if comp_pct >= max_completeness:
            continue

        results["eligible"] += 1

        # Determine days since last upload (or account creation)
        if last_upload:
            days_inactive = (now - last_upload).days
        else:
            # Use account creation or assume long inactivity
            days_inactive = inactivity_days + 1

        # Determine which reminder level to send
        target_level = None
        for rl in REMINDER_LEVELS:
            if days_inactive >= rl["days"]:
                target_level = rl

        if not target_level:
            continue

        # Check if already sent this level
        already = await db.inactivity_reminders.find_one({
            "client_id": cid,
            "level": target_level["level"],
            "created_at": {"$gte": (now - timedelta(days=7)).isoformat()}
        }, {"_id": 0, "id": 1})
        if already:
            results["already_reminded"] += 1
            continue

        # Build and send email
        html = _build_reminder_html(prenom, comp_pct, missing, target_level["level"], site_url)

        record = {
            "id": str(uuid.uuid4()),
            "client_id": cid,
            "client_email": email,
            "client_name": name,
            "level": target_level["level"],
            "days_inactive": days_inactive,
            "completeness_pct": comp_pct,
            "missing_docs_count": len(missing),
            "case_type": case_type,
            "status": "pending",
            "created_at": now.isoformat(),
        }

        if RESEND_AVAILABLE and os.environ.get('RESEND_API_KEY'):
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [email],
                    "subject": f"Stratégie & Expertise Santé — {target_level['subject']}",
                    "html": html
                })
                record["status"] = "sent"
                results["sent"] += 1
                logger.info(f"Inactivity reminder L{target_level['level']} sent to {email} (inactive {days_inactive}d, {comp_pct}%)")
            except Exception as e:
                record["status"] = "failed"
                record["error"] = str(e)
                results["failed"] += 1
                logger.error(f"Failed inactivity reminder to {email}: {e}")
        else:
            record["status"] = "skipped"
            results["skipped"] += 1

        await db.inactivity_reminders.insert_one(record)

    return results
