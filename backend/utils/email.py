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


# ==================== DYNAMIC TEMPLATE VARIABLES ====================

TEMPLATE_VARIABLES = [
    {"key": "prenom", "label": "Prénom du client", "sample": "Marie"},
    {"key": "nom", "label": "Nom de famille", "sample": "Dupont"},
    {"key": "completeness", "label": "% de complétude", "sample": "42"},
    {"key": "documents_missing", "label": "Documents manquants", "sample": "Attestation employeur, Certificat médical initial"},
    {"key": "date_inscription", "label": "Date d'inscription", "sample": "15/01/2026"},
]

SAMPLE_CONTEXT = {v["key"]: v["sample"] for v in TEMPLATE_VARIABLES}


def resolve_template_variables(text: str, context: dict) -> str:
    """Replace {{variable}} placeholders with actual values from context."""
    if not text:
        return text
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def build_missing_docs_html(missing_docs: list) -> str:
    """Convert a list of missing docs into a readable string for template variables."""
    if not missing_docs:
        return "Aucun"
    labels = []
    for d in missing_docs[:5]:
        labels.append(d.get("label", d) if isinstance(d, dict) else str(d))
    return ", ".join(labels)


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
                url = "/espace-client"
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

        # Record the notification (create before HTML so we have the ID for tracking)
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
                    <a href="{site_url}/api/track/click/{notif_record['id']}"
                       style="background:#1a1a2e;color:#d4a44a;padding:14px 28px;border-radius:6px;text-decoration:none;display:inline-block;font-weight:600;font-size:14px;">
                        {"Voir mon dossier complet" if threshold_pct == 100 else "Compléter mon dossier"}
                    </a>
                </div>
                <p style="color:#888;font-size:11px;text-align:center;margin-top:20px;">
                    Stratégie &amp; Expertise Santé — Cet email est envoyé automatiquement.
                </p>
            </div>
            <img src="{site_url}/api/track/open/{notif_record['id']}" width="1" height="1" style="display:none;" alt="" />
        </body>
        </html>
        """

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

# A/B test variant content overrides
AB_VARIANT_CONTENT = {
    "rassurant": {
        "subjects": {1: "Votre dossier vous attend", 2: "Nous sommes là pour vous accompagner", 3: "Votre dossier mérite d'être finalisé"},
        "intros": {
            1: "Nous avons remarqué que vous n'avez pas ajouté de documents récemment. Votre dossier est actuellement à <strong>{pct}%</strong> de complétude. Prenez quelques minutes pour le compléter.",
            2: "Votre dossier est toujours en attente. Il est complété à <strong>{pct}%</strong>. Nous sommes à vos côtés pour vous aider.",
            3: "Votre dossier est à <strong>{pct}%</strong>. Nous restons disponibles pour vous accompagner jusqu'à la finalisation.",
        },
        "motivations": {
            1: "En complétant votre dossier, vous profiterez d'une analyse StratégiIA plus précise et de recommandations personnalisées.",
            2: "Chaque document ajouté renforce la qualité de notre analyse. Nous sommes là pour vous accompagner.",
            3: "Finalisez votre dossier pour bénéficier de toute notre expertise. Nous restons à votre écoute.",
        },
    },
    "incitatif": {
        "subjects": {1: "Plus que quelques documents pour une analyse complète !", 2: "Boostez votre dossier — il ne manque presque rien !", 3: "Dernière ligne droite pour votre dossier !"},
        "intros": {
            1: "Bonne nouvelle ! Votre dossier est déjà à <strong>{pct}%</strong>. Il ne manque que quelques documents pour débloquer une analyse complète.",
            2: "Vous y êtes presque ! À <strong>{pct}%</strong>, votre dossier est sur la bonne voie. Ajoutez les dernières pièces pour maximiser vos résultats.",
            3: "C'est le moment d'agir ! Votre dossier à <strong>{pct}%</strong> est si proche d'être complet.",
        },
        "motivations": {
            1: "Chaque document supplémentaire améliore significativement la précision de votre analyse StratégiIA et vos chances de succès.",
            2: "Les clients qui complètent leur dossier obtiennent des recommandations 3x plus précises. Ne manquez pas cette opportunité !",
            3: "Un dossier complet = une analyse optimale = les meilleures recommandations. Franchissez cette dernière étape !",
        },
    },
    "urgent": {
        "subjects": {1: "Action requise : complétez votre dossier", 2: "Votre dossier attend vos documents depuis 2 semaines", 3: "Dernière relance : ne laissez pas votre dossier en suspens"},
        "intros": {
            1: "Votre dossier est à <strong>{pct}%</strong> de complétude et attend vos documents. Sans les pièces manquantes, l'analyse ne peut pas être optimale.",
            2: "Cela fait maintenant 2 semaines que votre dossier est en attente à <strong>{pct}%</strong>. Les délais de traitement augmentent avec le temps.",
            3: "C'est notre dernière relance. Votre dossier à <strong>{pct}%</strong> risque de ne pas bénéficier d'une analyse complète sans action de votre part.",
        },
        "motivations": {
            1: "Sans les documents essentiels, notre analyse reste incomplète. Agissez maintenant pour ne rien manquer.",
            2: "Plus vous attendez, plus les délais s'allongent. Complétez votre dossier aujourd'hui pour avancer sereinement.",
            3: "C'est votre dernière chance de compléter votre dossier avant la clôture du suivi automatique. Agissez maintenant.",
        },
    },
}


async def _get_ab_variant_for_reminder(level: int) -> dict | None:
    """Select an A/B test variant for this reminder level, or None if no active test."""
    import random
    test = await db.ab_tests.find_one({"status": "active"}, {"_id": 0})
    if not test:
        return None

    # If a winner was already promoted, use it
    if test.get("promoted_variant"):
        variant_name = test["promoted_variant"]
    else:
        # Random selection among variants
        variants = test.get("variants", [])
        if not variants:
            return None
        variant = random.choice(variants)
        variant_name = variant["name"]

    content = AB_VARIANT_CONTENT.get(variant_name)
    if not content:
        return None

    return {
        "test_id": test["id"],
        "variant_name": variant_name,
        "subject": content["subjects"].get(level, REMINDER_LEVELS[level - 1]["subject"]),
        "intro": content["intros"].get(level, ""),
        "motivation": content["motivations"].get(level, ""),
    }


def _build_reminder_html(prenom: str, completeness_pct: int, missing_docs: list, level: int, site_url: str, reminder_id: str = "", ab_override: dict = None, custom_template: dict = None) -> str:
    missing_count = len(missing_docs)

    # Build variable context for resolution
    var_context = {
        "prenom": prenom,
        "nom": "",
        "completeness": str(completeness_pct),
        "documents_missing": build_missing_docs_html(missing_docs),
        "date_inscription": "",
    }

    # Use custom template if provided (from email_templates collection)
    if custom_template and custom_template.get("intro"):
        intro = resolve_template_variables(custom_template["intro"], var_context)
        motivation = resolve_template_variables(custom_template.get("motivation", ""), var_context)
        cta_text = resolve_template_variables(custom_template.get("cta_text", "Compléter mon dossier"), var_context)
    elif ab_override and ab_override.get("intro"):
        intro = ab_override["intro"].replace("{pct}", str(completeness_pct))
        motivation = ab_override.get("motivation", "")
        cta_text = "Compléter mon dossier"
    elif level == 1:
        intro = f"Nous avons remarqué que vous n'avez pas ajouté de documents récemment. Votre dossier est actuellement à <strong>{completeness_pct}%</strong> de complétude."
        motivation = "En complétant votre dossier, vous profiterez d'une analyse StratégiIA plus précise et de recommandations personnalisées."
        cta_text = "Compléter mon dossier"
    elif level == 2:
        intro = f"Votre dossier est toujours en attente de documents. Il est actuellement complété à <strong>{completeness_pct}%</strong>."
        motivation = "Chaque document ajouté renforce la qualité de notre analyse et nous permet de mieux vous accompagner dans vos démarches."
        cta_text = "Compléter mon dossier"
    else:
        intro = f"C'est notre dernière relance automatique. Votre dossier est à <strong>{completeness_pct}%</strong> et attend vos documents."
        motivation = "Finalisez votre dossier maintenant pour bénéficier de toute la puissance de notre expertise et de StratégiIA."
        cta_text = "Compléter mon dossier"

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
                <a href="{site_url}/api/track/click/{reminder_id}"
                   style="background:#1a1a2e;color:#d4a44a;padding:14px 28px;border-radius:6px;text-decoration:none;display:inline-block;font-weight:600;font-size:14px;">
                    {cta_text}
                </a>
            </div>
            <p style="color:#888;font-size:11px;text-align:center;margin-top:20px;">
                Stratégie &amp; Expertise Santé — Cet email est envoyé automatiquement.
                <br/>Si vous ne souhaitez plus recevoir ces relances, contactez-nous.
            </p>
        </div>
        <img src="{site_url}/api/track/open/{reminder_id}" width="1" height="1" style="display:none;" alt="" />
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

        # Check for A/B test variant
        ab_variant = await _get_ab_variant_for_reminder(target_level["level"])
        if ab_variant:
            record["ab_test_id"] = ab_variant["test_id"]
            record["ab_variant"] = ab_variant["variant_name"]
            email_subject = f"Stratégie & Expertise Santé — {ab_variant['subject']}"
        else:
            email_subject = f"Stratégie & Expertise Santé — {target_level['subject']}"

        html = _build_reminder_html(prenom, comp_pct, missing, target_level["level"], site_url, record["id"], ab_variant)

        if RESEND_AVAILABLE and os.environ.get('RESEND_API_KEY'):
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [email],
                    "subject": email_subject,
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
