"""Lead magnet capture for SEO pillar pages.

Surgical, isolated module. Does not touch existing routes/misc.py guide-leads.
Captures email + RGPD consent on top SEO pages and sends a confirmation email
with a tailored "memo" content via Resend (already verified domain).
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone, timedelta
import os
import asyncio
import re

from config import db, RESEND_AVAILABLE, SENDER_EMAIL, SITE_URL, logger
from utils.auth import get_current_admin

if RESEND_AVAILABLE:
    import resend
    resend.api_key = os.environ.get("RESEND_API_KEY", "")

router = APIRouter()

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

# ==================== LEAD MAGNETS PER PAGE ====================
# Each pillar page captures with a tailored memo. Subject + body kept SHORT,
# professional, valuable. No fluff. Aligned with brand tone "Stratégie & Expertise Santé".

LEAD_MAGNETS = {
    "mdph": {
        "label": "Mémo MDPH",
        "title": "Les 5 erreurs qui font perdre 6 mois sur un dossier MDPH",
        "subject": "📋 Votre Mémo MDPH — 5 erreurs à éviter",
        "intro": "Voici les 5 erreurs les plus fréquentes que nous voyons dans les dossiers MDPH refusés ou rejetés. Identifiez celles qui s'appliquent à votre situation pour gagner plusieurs mois.",
        "bullets": [
            "Joindre le certificat médical Cerfa générique au lieu d'un certificat circonstancié rédigé selon les retentissements fonctionnels.",
            "Décrire ses pathologies en termes médicaux abstraits au lieu de retentissements concrets sur le quotidien (ce que la CDAPH évalue réellement).",
            "Oublier de demander explicitement chaque droit (AAH, RQTH, PCH, CMI) — la MDPH n'attribue que ce qui est demandé.",
            "Envoyer un dossier sans preuve de réception (LRAR ou suivi d'huissier numérique) — impossibilité de prouver les délais en cas de recours.",
            "Renoncer après le 1er refus alors que le RAPO et le pôle social du tribunal judiciaire ouvrent une seconde voie sous 2 mois.",
        ],
        "cta_label": "Lancer une analyse stratégique de mon dossier",
        "cta_url": "/strategiia",
    },
    "accident-travail-maladie-professionnelle": {
        "label": "Mémo AT/MP",
        "title": "Check-list : les 7 réflexes immédiats après un accident du travail",
        "subject": "🛠️ Votre Mémo AT/MP — 7 réflexes immédiats",
        "intro": "Les 7 actions à effectuer dans les 48 premières heures après un accident du travail ou un diagnostic de maladie professionnelle. Chaque action évite un préjudice durable sur votre dossier.",
        "bullets": [
            "Faire constater médicalement les lésions le jour même : le certificat médical initial conditionne toute l'instruction CPAM.",
            "Notifier l'employeur sous 24h par écrit (mail, LRAR) — sa déclaration sous 48h ouvre vos droits.",
            "Conserver l'arrêt de travail initial : sans interruption d'activité = présomption d'imputabilité fragilisée.",
            "Recueillir les coordonnées des témoins et des collègues présents — la preuve testimoniale est décisive en cas de contestation.",
            "Photographier le poste, l'équipement, les conditions matérielles si pertinent — preuve impossible à reconstituer plus tard.",
            "Demander la copie de votre dossier médical d'entreprise et du registre des AT bénins — droit légal souvent ignoré.",
            "Vérifier sous 30 jours la décision CPAM : silence = acceptation tacite, mais une décision implicite défavorable est attaquable sous 2 mois.",
        ],
        "cta_label": "Auditer mon dossier AT/MP",
        "cta_url": "/dossier-express",
    },
    "expertise-medicale": {
        "label": "Mémo Expertise médicale",
        "title": "La phrase à ne JAMAIS dire au médecin expert",
        "subject": "🩺 Votre Mémo Expertise — la phrase à éviter absolument",
        "intro": "L'expertise médicale est un acte juridique, pas un examen de soins. Voici ce qu'il faut comprendre avant le rendez-vous, et la formule qui vous fait perdre votre dossier en 30 secondes.",
        "bullets": [
            "Ne JAMAIS dire « ça va mieux » même si c'est partiellement vrai : l'expert retient cette phrase et minimise l'IPP. Décrivez les jours difficiles, pas les bonnes journées.",
            "Préparer un journal des douleurs sur 4 semaines avant le rendez-vous : retentissements concrets sur le sommeil, les déplacements, le travail, la vie sociale.",
            "Apporter TOUS les documents (compte-rendus, IRM, ordonnances, arrêts) — l'expert ne consulte JAMAIS le dossier CPAM en amont.",
            "Connaître le barème indicatif appliqué (concours médical pour AT-MP, barème assurance pour expertises privées) : le même handicap = des taux différents selon le barème.",
            "Demander toujours la communication écrite des dires (observations) — vous avez 8 jours pour les ajouter au rapport, c'est votre seule contre-attaque écrite.",
        ],
        "cta_label": "Préparer mon expertise avec un rapport stratégique",
        "cta_url": "/strategiia",
    },
    "calculatrice-ipp": {
        "label": "Mémo IPP",
        "title": "Comprendre le calcul IPP réel et les marges de négociation",
        "subject": "🧮 Votre Mémo IPP — calcul réel + marges",
        "intro": "Le taux d'IPP n'est jamais purement médical. Il dépend du barème appliqué, du contexte professionnel et de la qualité des dires. Voici comment comprendre votre marge de négociation.",
        "bullets": [
            "Le barème AT-MP (Concours Médical, fascicule 1) prévoit des fourchettes : un même handicap peut donner 8% à 15% selon l'évaluation des retentissements.",
            "Le coefficient socio-professionnel peut majorer un taux médical : âge, qualification, possibilité de reclassement, perte de gains effective.",
            "Le rapport doit individualiser : taux pour chaque séquelle + taux global. Si l'expert globalise sans détail, il devient inattaquable.",
            "Les dires (observations écrites) permettent de demander explicitement la majoration socio-pro et de pointer les insuffisances du rapport.",
            "Pour les rentes : 10%+ ouvre une rente viagère ; sous 10% = capital unique. Connaître le seuil change la stratégie de défense.",
        ],
        "cta_label": "Faire calculer mon dossier complet",
        "cta_url": "/dossier-express",
    },
    "calculatrice-aah": {
        "label": "Mémo AAH",
        "title": "Décrypter le motif de refus AAH et préparer le RAPO",
        "subject": "🏛️ Votre Mémo AAH — décrypter le refus + RAPO",
        "intro": "Un refus AAH se construit sur 1 ou 2 motifs précis (taux d'incapacité, RSDAE, conditions administratives). Identifier le motif = construire un RAPO ciblé qui passe.",
        "bullets": [
            "Motif n°1 : taux d'incapacité < 50% — contestable avec un certificat circonstancié + journal des retentissements + témoignages d'aidants.",
            "Motif n°2 : taux 50-79% sans RSDAE — le plus fréquent. La RSDAE (Restriction Substantielle et Durable d'Accès à l'Emploi) doit être prouvée par l'historique professionnel et les arrêts.",
            "Motif n°3 : conditions de ressources / résidence / âge — vérifier le calcul exact, les CAF se trompent fréquemment sur les ressources prises en compte.",
            "RAPO obligatoire avant tout recours contentieux : 2 mois après notification, courrier RAR à la MDPH avec arguments + pièces nouvelles.",
            "Si RAPO refusé ou silence > 2 mois : pôle social du tribunal judiciaire, sans avocat obligatoire, mais expertise stratégique recommandée.",
        ],
        "cta_label": "Auditer mon refus AAH",
        "cta_url": "/dossier-express",
    },
}


# ==================== MODELS ====================

class PillarLeadInput(BaseModel):
    email: str
    page_id: str = Field(..., description="mdph | accident-travail-maladie-professionnelle | expertise-medicale | calculatrice-ipp | calculatrice-aah")
    consent: bool = False
    page_url: Optional[str] = None


# ==================== HELPERS ====================

def _build_email_html(magnet: dict) -> str:
    bullets_html = "".join(
        f'<li style="margin-bottom: 12px; padding-left: 6px;">{b}</li>' for b in magnet["bullets"]
    )
    cta_url = magnet["cta_url"]
    if not cta_url.startswith("http"):
        cta_url = f"{SITE_URL.rstrip('/')}{cta_url}"
    return f"""
    <html>
    <body style="font-family: Georgia, 'Times New Roman', serif; max-width: 620px; margin: 0 auto; padding: 24px; color: #1f1d18; line-height: 1.55;">
      <div style="text-align: center; padding-bottom: 20px; border-bottom: 1px solid #E5E0D6;">
        <p style="margin: 0; color: #C9A84C; letter-spacing: 2px; font-size: 11px; text-transform: uppercase;">Stratégie &amp; Expertise Santé</p>
        <h1 style="margin: 8px 0 0 0; font-size: 22px; color: #1f1d18;">{magnet['title']}</h1>
      </div>

      <p style="margin-top: 24px; font-size: 15px;">{magnet['intro']}</p>

      <ol style="font-size: 14px; padding-left: 20px;">
        {bullets_html}
      </ol>

      <div style="margin-top: 32px; padding: 20px; background: #F9F7F2; border-left: 3px solid #C9A84C; border-radius: 4px;">
        <p style="margin: 0 0 12px 0; font-size: 14px;">Vous reconnaissez votre situation&nbsp;? Trois niveaux d'aide possibles selon votre urgence&nbsp;:</p>
        <p style="margin: 6px 0; font-size: 13px;">📋 <a href="{SITE_URL}/simulateur" style="color: #1f1d18;">Auto-diagnostic gratuit (5 min)</a></p>
        <p style="margin: 6px 0; font-size: 13px;">🎯 <a href="{cta_url}" style="color: #C9A84C; font-weight: bold;">{magnet['cta_label']}</a></p>
        <p style="margin: 6px 0; font-size: 13px;">📞 <a href="{SITE_URL}/rdv" style="color: #1f1d18;">Échange humain de 15 minutes (gratuit)</a></p>
      </div>

      <p style="margin-top: 32px; font-size: 12px; color: #6b675f; border-top: 1px solid #E5E0D6; padding-top: 16px;">
        Vous recevez ce mémo car vous l'avez explicitement demandé sur notre site.
        Vos données sont traitées conformément au RGPD&nbsp;: désinscription en répondant simplement à ce mail avec « stop ».
        <br><br>
        <em>L'équipe Stratégie &amp; Expertise Santé</em>
      </p>
    </body>
    </html>
    """


# ==================== ENDPOINTS ====================

@router.post("/leads/pillar-subscribe")
async def pillar_subscribe(input_data: PillarLeadInput, request: Request):
    """Capture email from a pillar SEO page + send the corresponding memo."""
    email = (input_data.email or "").strip().lower()
    if not email or not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=400, detail="Adresse email invalide")
    if not input_data.consent:
        raise HTTPException(status_code=400, detail="Consentement RGPD requis")

    page_id = input_data.page_id.strip()
    magnet = LEAD_MAGNETS.get(page_id)
    if not magnet:
        raise HTTPException(status_code=400, detail="Page inconnue")

    now_iso = datetime.now(timezone.utc).isoformat()
    consent_record = {
        "rgpd_consent": True,
        "consent_date": now_iso,
        "consent_version": "v1.0",
        "ip_hint": (request.headers.get("x-forwarded-for") or request.client.host or "")[:64] if request else None,
    }

    # Idempotence: if same (email, page_id) already exists in last 7 days, skip new insert+email
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    existing = await db.pillar_leads.find_one({
        "email": email, "page_id": page_id, "created_at": {"$gte": seven_days_ago}
    })
    if existing:
        return {"success": True, "already_subscribed": True, "label": magnet["label"]}

    # Persist lead
    lead_doc = {
        "email": email,
        "page_id": page_id,
        "page_label": magnet["label"],
        "page_url": input_data.page_url,
        "magnet_title": magnet["title"],
        "created_at": now_iso,
        "email_sent": False,
        **consent_record,
    }
    await db.pillar_leads.insert_one(lead_doc)

    # Try to send the memo email (non-blocking failure)
    sent = False
    if RESEND_AVAILABLE and os.environ.get("RESEND_API_KEY") and SENDER_EMAIL:
        try:
            await asyncio.to_thread(
                resend.Emails.send,
                {
                    "from": SENDER_EMAIL,
                    "to": [email],
                    "subject": magnet["subject"],
                    "html": _build_email_html(magnet),
                },
            )
            sent = True
        except Exception as e:
            logger.error(f"[pillar_lead] resend send failed for {email}: {e}")

    if sent:
        await db.pillar_leads.update_one(
            {"email": email, "page_id": page_id, "created_at": now_iso},
            {"$set": {"email_sent": True, "email_sent_at": datetime.now(timezone.utc).isoformat()}},
        )

    return {"success": True, "email_sent": sent, "label": magnet["label"]}


@router.get("/leads/pillar-magnets")
async def list_pillar_magnets():
    """Public read-only list of available magnets (used by frontend if needed)."""
    return [
        {"page_id": pid, "label": m["label"], "title": m["title"], "cta_label": m["cta_label"]}
        for pid, m in LEAD_MAGNETS.items()
    ]


# ==================== ADMIN ====================

@router.get("/admin/leads/pillar-stats")
async def pillar_leads_stats(admin: dict = Depends(get_current_admin)):
    """Stats for the pillar lead magnets — surfaced in Analytique sub-tab."""
    total = await db.pillar_leads.count_documents({})
    sent = await db.pillar_leads.count_documents({"email_sent": True})

    pipeline = [
        {"$group": {"_id": "$page_id", "count": {"$sum": 1}, "label": {"$first": "$page_label"}}},
        {"$sort": {"count": -1}},
    ]
    by_page = await db.pillar_leads.aggregate(pipeline).to_list(20)

    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    last_7d = await db.pillar_leads.count_documents({"created_at": {"$gte": seven_days_ago}})

    recent = await db.pillar_leads.find(
        {}, {"_id": 0, "email": 1, "page_id": 1, "page_label": 1, "created_at": 1, "email_sent": 1}
    ).sort("created_at", -1).limit(50).to_list(50)

    return {
        "total_leads": total,
        "email_sent": sent,
        "send_rate": round(sent / total * 100, 1) if total else 0.0,
        "last_7d": last_7d,
        "by_page": [{"page_id": b["_id"], "label": b.get("label"), "count": b["count"]} for b in by_page],
        "recent": recent,
    }
