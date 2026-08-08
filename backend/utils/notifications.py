"""
CONSOLIDATION_ARCHITECTURE — Notifications centralisees.
Fonctions d'alerte admin et client partagees par StrategiIA et Dossier Express.
"""
import os
import asyncio
from config import RESEND_AVAILABLE, SENDER_EMAIL, logger, SITE_URL

try:
    import resend
except ImportError:
    pass

NOTIFICATION_EMAIL = os.environ.get("NOTIFICATION_EMAIL", "")


async def notify_admin_incident(dossier_id: str, email: str, name: str, service: str, step: str, error: str):
    """Send admin notification about a delivery incident."""
    try:
        if RESEND_AVAILABLE and resend.api_key and NOTIFICATION_EMAIL:
            admin_html = f"""<h2>Incident de livraison — {service}</h2>
<p><strong>Client :</strong> {name} ({email})</p>
<p><strong>Dossier :</strong> {dossier_id}</p>
<p><strong>Etape en echec :</strong> {step}</p>
<p><strong>Erreur :</strong> {error[:500]}</p>
<p><strong>Action requise :</strong> Verifier le dossier dans l'admin et relancer si necessaire.</p>
<p><a href="{SITE_URL}/admin">Acceder a l'admin</a></p>"""
            await asyncio.to_thread(resend.Emails.send, {
                "from": SENDER_EMAIL,
                "to": [NOTIFICATION_EMAIL],
                "subject": f"[INCIDENT] {service} — {name} — Echec etape: {step}",
                "html": admin_html,
            })
            logger.info(f"Admin notified of incident for dossier {dossier_id}")
    except Exception as e:
        logger.error(f"Failed to notify admin of incident: {e}")


async def notify_admin_expert_feedback(evaluator_name: str, profile_type: str, average: str, n_ratings: int, comments: dict, benefits: list = None):
    """Alerte admin : une grille d'evaluation expert vient d'etre soumise."""
    try:
        if RESEND_AVAILABLE and resend.api_key and NOTIFICATION_EMAIL:
            benefit_labels = {"gain_temps": "Gain de temps", "comprehension_initiale": "Comprehension initiale",
                              "pieces_manquantes": "Pieces manquantes", "chronologie": "Chronologie",
                              "incoherences": "Incoherences", "tracabilite_sources": "Tracabilite des sources",
                              "hierarchisation": "Hierarchisation"}
            benefits_html = ("<p><strong>Benefices constates :</strong> " + ", ".join(benefit_labels.get(b, b) for b in benefits) + "</p>") if benefits else "<p><strong>Benefices constates :</strong> <em>aucun coche</em></p>"
            comments_html = "".join(
                f"<p style='margin:6px 0;'><strong>{label} :</strong> {str(comments[key])[:400]}</p>"
                for key, label in [("points_forts", "Points forts"), ("mises_en_defaut", "Mises en defaut"), ("reserves", "Reserves")]
                if comments.get(key)
            ) or "<p><em>Aucun commentaire libre.</em></p>"
            html = f"""<h2>Retour d'evaluateur expert recu</h2>
<p><strong>Evaluateur :</strong> {evaluator_name} ({profile_type})</p>
<p><strong>Moyenne :</strong> {average} / 5 ({n_ratings} critere(s) note(s))</p>
{benefits_html}
{comments_html}
<p><strong>Action recommandee :</strong> consulter le retour complet et repondre rapidement a l'expert.</p>
<p><a href="{SITE_URL}/admin">Ouvrir l'admin — onglet Dossier Express → carte Evaluateurs</a></p>"""
            await asyncio.to_thread(resend.Emails.send, {
                "from": SENDER_EMAIL,
                "to": [NOTIFICATION_EMAIL],
                "subject": f"[EVALUATEUR] Retour recu — {evaluator_name} ({average}/5)",
                "html": html,
            })
            logger.info(f"[EXPERT-FEEDBACK-ALERT] Admin notifie du retour de {evaluator_name}")
    except Exception as e:
        logger.error(f"Failed to notify admin of expert feedback: {e}")


async def notify_client_delay(email: str, name: str, service: str):
    """Send professional delay notification to client."""
    try:
        if RESEND_AVAILABLE and resend.api_key:
            safe_name = name or "Madame, Monsieur"
            client_html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f2ed;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f2ed;padding:32px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;">
<tr><td style="background:#1a1a1a;padding:24px 32px;border-radius:8px 8px 0 0;">
  <span style="color:#fff;font-size:18px;font-weight:bold;">Strategie & Expertise Sante</span><br/>
  <span style="color:#c9a84c;font-size:11px;letter-spacing:3px;text-transform:uppercase;">VOTRE BOUCLIER</span>
</td></tr>
<tr><td style="background:#fff;padding:32px;">
  <p style="font-size:15px;color:#333;">Bonjour {safe_name},</p>
  <p style="font-size:14px;color:#555;line-height:1.7;">
    Votre demande de <strong>{service}</strong> necessite un traitement complementaire
    afin de vous garantir la meilleure qualite d'analyse possible.
  </p>
  <p style="font-size:14px;color:#555;line-height:1.7;">
    Notre equipe a ete automatiquement informee et reviendra vers vous
    dans les meilleurs delais avec votre rapport complet.
  </p>
  <p style="font-size:14px;color:#555;line-height:1.7;">
    Nous vous remercions pour votre confiance et votre patience.
  </p>
  <div style="border-left:3px solid #c9a84c;padding:12px 16px;margin:20px 0;background:#faf8f3;">
    <p style="font-size:13px;color:#333;margin:0;font-weight:600;">
      Aucune action n'est requise de votre part. Votre dossier est entre de bonnes mains.
    </p>
  </div>
  <p style="font-size:13px;color:#888;">Cordialement,<br/>L'equipe Strategie & Expertise Sante</p>
</td></tr>
<tr><td style="background:#1a1a1a;padding:16px 32px;border-radius:0 0 8px 8px;text-align:center;">
  <p style="color:#c9a84c;font-size:12px;margin:0;">Strategie & Expertise Sante — Votre bouclier.</p>
</td></tr>
</table></td></tr></table></body></html>"""
            await asyncio.to_thread(resend.Emails.send, {
                "from": SENDER_EMAIL,
                "to": [email],
                "subject": f"Votre {service} — Traitement complementaire en cours",
                "html": client_html,
            })
            logger.info(f"Client {email} notified of delay for {service}")
    except Exception as e:
        logger.error(f"Failed to notify client of delay: {e}")
