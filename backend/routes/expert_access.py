"""Module Accès Expert — statut évaluateur/partenaire pérenne pour Dossier Express IA.
Dossiers marqués eval_test=True, exclus de tous les KPIs commerciaux."""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone, timedelta
import asyncio
import secrets
import uuid

from config import db, logger
from utils.auth import get_current_admin

router = APIRouter(prefix="/expert-access", tags=["expert-access"])
admin_router = APIRouter(prefix="/admin/expert-access", tags=["admin-expert-access"])

PROFILE_TYPES = ["medecin_expert", "avocat", "association", "comite_scientifique", "beta_privee", "partenaire", "autre"]
CONFIG_ID = "expert_access_config"


async def _get_config():
    cfg = await db.site_settings.find_one({"_id": CONFIG_ID})
    if not cfg:
        cfg = {"_id": CONFIG_ID, "default_quota": 3, "default_validity_days": 30}
        await db.site_settings.insert_one(cfg)
    return cfg


def _serialize(e: dict) -> dict:
    return {
        "id": e["id"], "name": e["name"], "email": e["email"],
        "profile_type": e.get("profile_type", "autre"),
        "token": e["token"],
        "quota_analyses": e["quota_analyses"], "analyses_used": e.get("analyses_used", 0),
        "expires_at": e["expires_at"], "active": e.get("active", True),
        "notes": e.get("notes", ""), "created_at": e.get("created_at"),
        "last_login_at": e.get("last_login_at"),
        "invitation_sent_at": e.get("invitation_sent_at"),
    }


# ==================== ADMIN ====================

@admin_router.get("/config")
async def get_expert_access_config(admin: dict = Depends(get_current_admin)):
    cfg = await _get_config()
    return {"default_quota": cfg["default_quota"], "default_validity_days": cfg["default_validity_days"]}


@admin_router.put("/config")
async def update_expert_access_config(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    updates = {}
    if "default_quota" in body:
        updates["default_quota"] = max(1, int(body["default_quota"]))
    if "default_validity_days" in body:
        updates["default_validity_days"] = max(1, int(body["default_validity_days"]))
    if updates:
        await db.site_settings.update_one({"_id": CONFIG_ID}, {"$set": updates}, upsert=True)
    return {"status": "ok", **updates}


TEMPLATE_ID = "expert_invitation_template"
DEFAULT_INVITATION_SUBJECT = "Invitation personnelle — regard d'expert sur Dossier Express IA"
DEFAULT_INVITATION_BODY = """Docteur,

Nous développons un outil d'aide à la structuration de dossiers pour les personnes confrontées à un refus de reconnaissance (maladie professionnelle, MDPH, litige assurantiel) : **Dossier Express IA**. Avant d'aller plus loin, nous avons besoin d'un regard extérieur exigeant — et le vôtre serait particulièrement précieux.

**Notre hypothèse — que nous vous demandons précisément de mettre à l'épreuve :** l'outil peut faire gagner un temps significatif sur le travail documentaire qui précède l'expertise — première lecture d'un dossier volumineux, reconstitution de la chronologie, repérage des pièces manquantes ou illisibles, identification des incohérences entre documents, traçabilité de chaque information vers sa pièce source. Le professionnel consacre alors davantage de son temps à ce qui relève réellement de son jugement.

**Sa limite, assumée et volontaire :** il n'analyse que l'organisation documentaire et les éléments procéduraux. Il ne porte aucun jugement clinique, ne discute aucun diagnostic et ne prétend remplacer ni l'expertise médicale, ni le médecin, ni l'avocat. C'est précisément cette frontière que nous vous demandons d'éprouver.

**Concrètement :**
- Un accès d'évaluation strictement privé, gratuit, valable jusqu'au {DATE_VALIDITE} ({QUOTA} analyses).
- Votre espace contient un **guide de prise en main très court** ainsi qu'un **cas fictif** permettant de réaliser immédiatement un premier test, sans avoir besoin de préparer un dossier réel.
- La possibilité, facultative, de tester ensuite un dossier professionnel **anonymisé par vos soins**.
- Une grille d'évaluation intégrée pour consigner votre retour — **vos critiques sont le livrable attendu**, pas votre approbation.

Il vous suffira de confirmer votre adresse email (celle-ci) pour entrer. Temps total estimé : environ 1 heure, à votre rythme. Votre évaluation restera strictement confidentielle et votre nom ne sera jamais cité sans votre accord écrit. Aucune sollicitation commerciale ne suivra cet essai.

Nous vous remercions sincèrement du temps que vous voudrez bien y consacrer.

Bien respectueusement,
Stratégie & Expertise Santé"""
TEMPLATE_PLACEHOLDERS = ["{NOM}", "{QUOTA}", "{DATE_VALIDITE}"]


async def _get_invitation_template() -> dict:
    saved = await db.site_settings.find_one({"_id": TEMPLATE_ID})
    if saved:
        return {"subject": saved["subject"], "body": saved["body"], "is_default": False}
    return {"subject": DEFAULT_INVITATION_SUBJECT, "body": DEFAULT_INVITATION_BODY, "is_default": True}


def _render_body_html(body_text: str) -> str:
    import html as html_mod
    import re
    text = html_mod.escape(body_text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text, flags=re.DOTALL)
    blocks_html = []
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        if all(l.strip().startswith("- ") for l in lines):
            items = "".join(f"<li>{l.strip()[2:]}</li>" for l in lines)
            blocks_html.append(f'<ul style="font-size:14px;color:#444;line-height:1.75;padding-left:20px;margin:0 0 14px;">{items}</ul>')
        else:
            blocks_html.append(f'<p style="font-size:14px;color:#444;line-height:1.75;">{"<br/>".join(lines)}</p>')
    return "".join(blocks_html)


@admin_router.get("/invitation-template")
async def get_invitation_template(admin: dict = Depends(get_current_admin)):
    tpl = await _get_invitation_template()
    return {**tpl, "placeholders": TEMPLATE_PLACEHOLDERS}


@admin_router.put("/invitation-template")
async def update_invitation_template(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    subject = str(body.get("subject", "")).strip()[:300]
    body_text = str(body.get("body", "")).strip()[:20000]
    if not subject or not body_text:
        raise HTTPException(status_code=400, detail="Objet et corps requis")
    await db.site_settings.update_one(
        {"_id": TEMPLATE_ID},
        {"$set": {"subject": subject, "body": body_text, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return {"status": "ok"}


@admin_router.delete("/invitation-template")
async def reset_invitation_template(admin: dict = Depends(get_current_admin)):
    await db.site_settings.delete_one({"_id": TEMPLATE_ID})
    return {"status": "reset", "subject": DEFAULT_INVITATION_SUBJECT, "body": DEFAULT_INVITATION_BODY}


@admin_router.post("/invitation-template/preview")
async def preview_invitation_template(request: Request, admin: dict = Depends(get_current_admin)):
    """Envoie un aperçu du modèle (valeurs d'exemple) à l'adresse de notification admin."""
    body = await request.json()
    subject = str(body.get("subject", "")).strip() or DEFAULT_INVITATION_SUBJECT
    body_text = str(body.get("body", "")).strip() or DEFAULT_INVITATION_BODY
    from config import RESEND_AVAILABLE, SENDER_EMAIL, SITE_URL, NOTIFICATION_EMAIL
    import resend
    if not (RESEND_AVAILABLE and resend.api_key and NOTIFICATION_EMAIL):
        raise HTTPException(status_code=503, detail="Service email non disponible")
    sample_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%d/%m/%Y")
    filled = body_text.replace("{NOM}", "Dr de Thiballier").replace("{QUOTA}", "3").replace("{DATE_VALIDITE}", sample_date)
    html = _build_invitation_html(_render_body_html(filled), f"{SITE_URL}/evaluation-expert?t=APERCU-LIEN-EXEMPLE")
    try:
        await asyncio.to_thread(resend.Emails.send, {
            "from": SENDER_EMAIL,
            "to": [NOTIFICATION_EMAIL],
            "subject": f"[APERÇU] {subject.replace('{NOM}', 'Dr de Thiballier')}",
            "html": html,
        })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Envoi impossible : {str(e)[:120]}")
    return {"status": "sent", "to": NOTIFICATION_EMAIL}


@admin_router.post("")
async def create_expert_access(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip().lower()
    if not name or not email:
        raise HTTPException(status_code=400, detail="Nom et email requis")
    profile_type = body.get("profile_type") or "medecin_expert"
    if profile_type not in PROFILE_TYPES:
        raise HTTPException(status_code=400, detail="Type de profil invalide")
    cfg = await _get_config()
    quota = max(1, int(body.get("quota_analyses") or cfg["default_quota"]))
    validity_days = max(1, int(body.get("validity_days") or cfg["default_validity_days"]))
    entry = {
        "id": str(uuid.uuid4())[:8],
        "name": name, "email": email, "profile_type": profile_type,
        "token": secrets.token_urlsafe(24),
        "quota_analyses": quota, "analyses_used": 0,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=validity_days)).isoformat(),
        "active": True, "notes": body.get("notes", ""),
        "created_by": admin.get("email", "admin"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.expert_access.insert_one(entry)
    logger.info(f"[EXPERT-ACCESS] Créé: {name} ({profile_type}) quota={quota} validité={validity_days}j")
    return _serialize(entry)


@admin_router.get("")
async def list_expert_access(admin: dict = Depends(get_current_admin)):
    entries = await db.expert_access.find({}).sort("created_at", -1).to_list(200)
    ids = [e["id"] for e in entries]
    feedbacks = await db.expert_feedback.find({"evaluator_id": {"$in": ids}}, {"_id": 0}).to_list(200)
    fb_map = {f["evaluator_id"]: f for f in feedbacks}
    dossier_agg = await db.dossier_express.aggregate([
        {"$match": {"evaluator_id": {"$in": ids}}},
        {"$group": {"_id": "$evaluator_id", "last_dossier_at": {"$max": "$created_at"}, "dossiers_count": {"$sum": 1}}},
    ]).to_list(200)
    d_map = {d["_id"]: d for d in dossier_agg}
    out = []
    for e in entries:
        s = _serialize(e)
        fb = fb_map.get(e["id"])
        d = d_map.get(e["id"], {})
        s["has_feedback"] = bool(fb)
        s["feedback_updated_at"] = (fb or {}).get("updated_at")
        s["last_dossier_at"] = d.get("last_dossier_at")
        s["dossiers_count"] = d.get("dossiers_count", 0)
        activity = [x for x in (s.get("last_login_at"), s["feedback_updated_at"], s["last_dossier_at"]) if x]
        s["last_activity_at"] = max(activity) if activity else None
        out.append(s)
    return {"evaluators": out}


@admin_router.put("/{access_id}")
async def update_expert_access(access_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    updates = {}
    if "quota_analyses" in body:
        updates["quota_analyses"] = max(1, int(body["quota_analyses"]))
    if "expires_at" in body and body["expires_at"]:
        updates["expires_at"] = str(body["expires_at"])
    if "extend_days" in body:
        updates["expires_at"] = (datetime.now(timezone.utc) + timedelta(days=max(1, int(body["extend_days"])))).isoformat()
    if "active" in body:
        updates["active"] = bool(body["active"])
    if "notes" in body:
        updates["notes"] = str(body["notes"])
    if "name" in body and body["name"]:
        updates["name"] = str(body["name"]).strip()
    if "profile_type" in body and body["profile_type"] in PROFILE_TYPES:
        updates["profile_type"] = body["profile_type"]
    if not updates:
        raise HTTPException(status_code=400, detail="Aucune modification fournie")
    res = await db.expert_access.find_one_and_update({"id": access_id}, {"$set": updates}, return_document=True)
    if not res:
        raise HTTPException(status_code=404, detail="Accès introuvable")
    return _serialize(res)


def _build_invitation_html(body_html: str, link: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f2ed;font-family:Georgia,'Times New Roman',serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f2ed;padding:32px 16px;">
<tr><td align="center">
<table width="620" cellpadding="0" cellspacing="0" style="max-width:620px;background:#ffffff;border-radius:8px;overflow:hidden;">
<tr><td style="background:#141410;padding:26px 36px;">
  <span style="color:#f5f0e8;font-size:17px;font-weight:bold;">Strat&eacute;gie &amp; Expertise Sant&eacute;</span><br/>
  <span style="color:#C9A84C;font-size:11px;letter-spacing:3px;text-transform:uppercase;">Programme d'&eacute;valuation expert</span>
</td></tr>
<tr><td style="padding:34px 36px;">
{body_html}
  <table width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0;"><tr><td align="center">
    <a href="{link}" style="display:inline-block;background:#C9A84C;color:#141410;font-size:14px;font-weight:bold;padding:13px 30px;border-radius:6px;text-decoration:none;">Acc&eacute;der &agrave; mon espace d'&eacute;valuation</a>
  </td></tr></table>
</td></tr>
<tr><td style="background:#141410;padding:14px 36px;text-align:center;">
  <p style="color:#C9A84C;font-size:11px;margin:0;">contact@strategie-expertise-sante.fr</p>
</td></tr>
</table></td></tr></table></body></html>"""


@admin_router.post("/{access_id}/send-invitation")
async def send_expert_invitation(access_id: str, admin: dict = Depends(get_current_admin)):
    entry = await db.expert_access.find_one({"id": access_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Accès introuvable")
    if not entry.get("active", True):
        raise HTTPException(status_code=400, detail="Accès désactivé — réactivez-le avant d'inviter")
    from config import RESEND_AVAILABLE, SENDER_EMAIL, SITE_URL
    import resend
    if not (RESEND_AVAILABLE and resend.api_key):
        raise HTTPException(status_code=503, detail="Service email non disponible")
    link = f"{SITE_URL}/evaluation-expert?t={entry['token']}"
    validity_date = datetime.fromisoformat(entry["expires_at"]).strftime("%d/%m/%Y")
    tpl = await _get_invitation_template()
    filled_body = (tpl["body"].replace("{NOM}", entry["name"])
                   .replace("{QUOTA}", str(entry["quota_analyses"]))
                   .replace("{DATE_VALIDITE}", validity_date))
    subject = tpl["subject"].replace("{NOM}", entry["name"])
    html = _build_invitation_html(_render_body_html(filled_body), link)
    try:
        await asyncio.to_thread(resend.Emails.send, {
            "from": SENDER_EMAIL,
            "to": [entry["email"]],
            "subject": subject,
            "html": html,
        })
    except Exception as e:
        logger.error(f"[EXPERT-ACCESS] Envoi invitation échoué pour {entry['name']}: {e}")
        raise HTTPException(status_code=502, detail=f"Envoi impossible : {str(e)[:120]}")
    sent_at = datetime.now(timezone.utc).isoformat()
    await db.expert_access.update_one({"id": access_id}, {"$set": {"invitation_sent_at": sent_at}})
    logger.info(f"[EXPERT-ACCESS] Invitation envoyée à {entry['name']} ({entry['email']})")
    return {"status": "sent", "invitation_sent_at": sent_at}


@admin_router.delete("/feedback/{evaluator_id}")
async def delete_expert_feedback(evaluator_id: str, admin: dict = Depends(get_current_admin)):
    res = await db.expert_feedback.delete_one({"evaluator_id": evaluator_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Feedback introuvable")
    return {"status": "deleted"}


@admin_router.delete("/{access_id}")
async def delete_expert_access(access_id: str, admin: dict = Depends(get_current_admin)):
    res = await db.expert_access.delete_one({"id": access_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Accès introuvable")
    await db.expert_feedback.delete_one({"evaluator_id": access_id})
    return {"status": "deleted"}


# ==================== PUBLIC (évaluateur) ====================

async def _validate_access(token: str, email: str) -> dict:
    entry = await db.expert_access.find_one({"token": token})
    if not entry:
        raise HTTPException(status_code=404, detail="Lien d'accès invalide")
    if (email or "").strip().lower() != entry["email"]:
        raise HTTPException(status_code=403, detail="Cet email ne correspond pas à l'invitation")
    if not entry.get("active", True):
        raise HTTPException(status_code=403, detail="Cet accès a été désactivé")
    if datetime.fromisoformat(entry["expires_at"]) < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Cet accès a expiré")
    return entry


@router.post("/verify")
async def verify_expert_access(request: Request):
    body = await request.json()
    entry = await _validate_access(body.get("token", ""), body.get("email", ""))
    await db.expert_access.update_one({"id": entry["id"]}, {"$set": {"last_login_at": datetime.now(timezone.utc).isoformat()}})
    return {
        "name": entry["name"], "email": entry["email"],
        "profile_type": entry.get("profile_type", "autre"),
        "quota_analyses": entry["quota_analyses"],
        "quota_remaining": max(0, entry["quota_analyses"] - entry.get("analyses_used", 0)),
        "expires_at": entry["expires_at"],
    }


GRID_CRITERIA = ["fidelite_documentaire", "pertinence_procedurale", "respect_perimetre",
                 "detection_qualite", "clarte_rapport", "experience_parcours"]
COMMENT_FIELDS = ["points_forts", "mises_en_defaut", "reserves"]
BENEFIT_KEYS = ["gain_temps", "comprehension_initiale", "pieces_manquantes", "chronologie",
                "incoherences", "tracabilite_sources", "hierarchisation"]


@router.post("/feedback")
async def submit_expert_feedback(request: Request):
    """Grille d'évaluation structurée remplie par l'évaluateur — stockée pour exploitation future."""
    body = await request.json()
    entry = await _validate_access(body.get("token", ""), body.get("email", ""))
    ratings, comments = body.get("ratings") or {}, body.get("comments") or {}
    clean_ratings = {}
    for k in GRID_CRITERIA:
        try:
            v = int(ratings.get(k))
            if 1 <= v <= 5:
                clean_ratings[k] = v
        except (TypeError, ValueError):
            continue
    clean_comments = {k: str(comments[k]).strip()[:5000] for k in COMMENT_FIELDS if comments.get(k) and str(comments[k]).strip()}
    clean_benefits = [b for b in (body.get("benefits") or []) if b in BENEFIT_KEYS]
    if not clean_ratings and not clean_comments and not clean_benefits:
        raise HTTPException(status_code=400, detail="Aucun retour fourni")
    now = datetime.now(timezone.utc).isoformat()
    await db.expert_feedback.update_one(
        {"evaluator_id": entry["id"]},
        {"$set": {
            "evaluator_name": entry["name"], "evaluator_email": entry["email"],
            "profile_type": entry.get("profile_type", "autre"),
            "ratings": clean_ratings, "comments": clean_comments,
            "benefits_observed": clean_benefits,
            "updated_at": now,
        }, "$setOnInsert": {"evaluator_id": entry["id"], "created_at": now}},
        upsert=True,
    )
    logger.info(f"[EXPERT-ACCESS] Grille d'évaluation reçue de {entry['name']} ({entry['id']}) — {len(clean_ratings)} notes")
    from utils.notifications import notify_admin_expert_feedback
    avg = f"{sum(clean_ratings.values()) / len(clean_ratings):.1f}" if clean_ratings else "n/a"
    asyncio.create_task(notify_admin_expert_feedback(
        entry["name"], entry.get("profile_type", "autre"), avg, len(clean_ratings), clean_comments, clean_benefits))
    return {"status": "ok"}


@router.get("/feedback")
async def get_own_expert_feedback(token: str, email: str):
    entry = await _validate_access(token, email)
    fb = await db.expert_feedback.find_one({"evaluator_id": entry["id"]}, {"_id": 0})
    return {"feedback": fb}


@admin_router.get("/feedback")
async def list_expert_feedback(admin: dict = Depends(get_current_admin)):
    items = await db.expert_feedback.find({}, {"_id": 0}).sort("updated_at", -1).to_list(200)
    return {"feedback": items}


@router.post("/submit")
async def expert_access_submit(request: Request):
    from routes.dossier_express import _process_dossier_express, _link_documents_to_dossier, _has_llm_key
    body = await request.json()
    entry = await _validate_access(body.get("token", ""), body.get("email", ""))

    situation = body.get("situation", "")
    if not situation.strip():
        raise HTTPException(status_code=400, detail="Situation requise")
    if not _has_llm_key():
        raise HTTPException(status_code=503, detail="Service IA non disponible")

    # Décrément atomique du quota (protège contre les doubles clics/abus)
    claimed = await db.expert_access.find_one_and_update(
        {"id": entry["id"], "$expr": {"$lt": [{"$ifNull": ["$analyses_used", 0]}, "$quota_analyses"]}},
        {"$inc": {"analyses_used": 1}},
        return_document=True,
    )
    if not claimed:
        raise HTTPException(status_code=403, detail="Quota d'analyses épuisé")

    name = body.get("name") or entry["name"]
    email = entry["email"]
    original_documents = body.get("original_documents", []) or []
    premium_pdf = body.get("premium_pdf", False)
    quality_choice = body.get("quality_choice", "not_available")
    quality_summary = body.get("quality_summary")

    dossier_id = str(uuid.uuid4())[:12]
    dossier_entry = {
        "id": dossier_id,
        "email": email,
        "name": name,
        "situation": situation,
        "type_dossier": body.get("type_dossier", ""),
        "regime": body.get("regime", ""),
        "documents_text": body.get("documents_text", ""),
        "document_details": body.get("document_details", []),
        "original_documents": original_documents,
        "status": "processing",
        "delivery_status": "en_attente_traitement",
        "processing_step": "checkout_valide",
        "premium_pdf": premium_pdf,
        "eval_test": True,
        "source_type": "evaluateur_expert",
        "evaluator_id": entry["id"],
        "evaluator_profile": entry.get("profile_type", "autre"),
        "amount": 0,
        "improvement_optout": body.get("improvement_optout", False),
        "quality_choice": quality_choice,
        "quality_summary": quality_summary,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.dossier_express.insert_one(dossier_entry)
    await _link_documents_to_dossier(dossier_id, email, original_documents)
    asyncio.create_task(_process_dossier_express(
        dossier_id, email, name, situation, dossier_entry["type_dossier"], dossier_entry["regime"],
        dossier_entry["documents_text"], premium_pdf=premium_pdf,
        improvement_optout=dossier_entry["improvement_optout"],
    ))
    remaining = max(0, claimed["quota_analyses"] - claimed.get("analyses_used", 0))
    logger.info(f"[EXPERT-ACCESS][{dossier_id}] Analyse lancée par évaluateur {entry['name']} ({entry['id']}) — quota restant {remaining}")
    return {"dossier_id": dossier_id, "status": "processing", "eval_test": True, "quota_remaining": remaining}
