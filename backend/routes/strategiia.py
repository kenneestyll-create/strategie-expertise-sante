from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import asyncio
import uuid
import base64
import os
import jwt

import stripe as stripe_sdk

try:
    import anthropic
except ImportError:
    pass

from config import db, STRIPE_API_KEY, RESEND_AVAILABLE, SENDER_EMAIL, logger, JWT_SECRET, JWT_ALGORITHM, SITE_URL
from utils.auth import get_current_admin, get_optional_admin
from utils.email import notify_admin_premium_analysis
from utils.pdf import generate_secured_pdf
from utils.storage import put_object
from constants.statuses import Service, PremiumStatus, JobStatus
from constants.workflows import LLM_MAX_RETRIES, LLM_RETRY_DELAY_SECONDS, LLM_MIN_ANALYSIS_LENGTH, STRATEGIIA_FREE_MONTHLY_QUOTA
from constants.guards import assert_valid_service, assert_premium_analyses_entry
from constants.prompts import STRATEGIIA_SYSTEM_PROMPT, STRATEGIIA_BASIC_PROMPT, STRATEGIIA_PREMIUM_PROMPT
from utils.llm import has_llm_key as _has_llm_key, llm_call, ANTHROPIC_API_KEY, EMERGENT_LLM_KEY
from utils.notifications import notify_admin_incident as _notify_admin_incident

STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
NOTIFICATION_EMAIL = os.environ.get("NOTIFICATION_EMAIL", "")

try:
    import resend
except ImportError:
    pass

router = APIRouter()


# ==================== LLM HEALTH CHECK ====================

# _has_llm_key -> imported from utils/llm.py


async def _check_llm_health():
    """Verify LLM availability. Returns (ok: bool, error: str)."""
    if not _has_llm_key():
        return False, "cle_absente"
    # Try native Anthropic key first
    if ANTHROPIC_API_KEY:
        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            resp = await asyncio.to_thread(
                client.messages.create,
                model="claude-sonnet-4-5-20250929",
                max_tokens=10,
                messages=[{"role": "user", "content": "OK"}],
            )
            if resp and resp.content:
                return True, ""
            return False, "reponse_vide"
        except anthropic.AuthenticationError:
            if EMERGENT_LLM_KEY:
                return True, "fallback_emergent"
            return False, "cle_invalide"
        except anthropic.RateLimitError:
            return False, "quota_depasse"
        except Exception as e:
            err = str(e).lower()
            if "budget" in err or "exceeded" in err:
                return False, "budget_depasse"
            if EMERGENT_LLM_KEY:
                return True, "fallback_emergent"
            return False, f"erreur: {str(e)[:100]}"
    # Emergent fallback key available
    if EMERGENT_LLM_KEY:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id="health_check", system_message="OK")
            chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
            chat.with_params(timeout=30, max_tokens=10)
            resp = await chat.send_message(UserMessage(text="OK"))
            if resp:
                return True, ""
            return False, "reponse_vide"
        except Exception as e:
            return False, f"erreur_emergent: {str(e)[:100]}"
    return False, "aucune_cle"


@router.get("/health/llm")
async def health_llm():
    """Public endpoint for frontend to check if LLM service is operational before checkout."""
    ok, reason = await _check_llm_health()
    return {"operational": ok, "reason": reason}



# Notifications: imported from utils/notifications.py -> _notify_admin_incident, _notify_client_delay
# Prompts: imported from constants/prompts.py -> STRATEGIIA_SYSTEM_PROMPT, STRATEGIIA_BASIC_PROMPT, STRATEGIIA_PREMIUM_PROMPT, DOSSIER_EXPRESS_SYSTEM_PROMPT, DOSSIER_EXPRESS_PROMPT




# ==================== DOSSIER EXPRESS — EXTRACTED ====================
# All Dossier Express routes moved to /app/backend/routes/dossier_express.py
# See CONSOLIDATION_ARCHITECTURE.md for isolation rules


# ==================== STRATEGIIA ====================

# In-memory job store for async polling
_jobs = {}


# LLM functions: imported from utils/llm.py -> llm_call, llm_sync_call, llm_stream_call, llm_async_call

async def _run_analysis(job_id, type_dossier, regime, situation, is_premium, email, similar_cases, case_context, is_admin_test=False):
    """Background task for LLM analysis with retry."""
    last_error = ""

    # ARTICULATION: If Dossier Express analysis exists for this email, inject as enriched context
    dossier_express_context = ""
    if email and is_premium:
        try:
            de_doc = await db.dossier_express.find_one(
                {"email": email.lower(), "status": "completed"},
                {"_id": 0, "analysis": 1, "document_details": 1}
            )
            if de_doc and de_doc.get("analysis"):
                dossier_express_context = f"""

CONTEXTE DOCUMENTAIRE ENRICHI (issu d'un Dossier Express IA precedemment realise pour ce client) :
{de_doc['analysis'][:4000]}

INSTRUCTION : Utilise cette matiere documentaire structuree pour affiner ta lecture strategique. Les pieces ont deja ete analysees par Dossier Express IA — tu peux t'appuyer sur ses conclusions pour produire une orientation plus precise et plus profonde. Ne repete pas l'analyse documentaire, concentre-toi sur la strategie et le pilotage."""
                logger.info(f"StrategiIA {job_id}: Enriched with Dossier Express context for {email}")
        except Exception as e:
            logger.warning(f"StrategiIA {job_id}: Failed to fetch Dossier Express context: {e}")

    for attempt in range(3):
        try:
            analysis_prompt = STRATEGIIA_PREMIUM_PROMPT if is_premium else STRATEGIIA_BASIC_PROMPT
            user_msg = f"""Type de dossier : {type_dossier}\nRegime : {regime}\nDescription de la situation : {situation}\n{case_context}{dossier_express_context}\n\n{analysis_prompt}"""
            session_id = f"strategiia_{str(uuid.uuid4())[:8]}"
            response = await llm_call(
                ANTHROPIC_API_KEY, session_id, STRATEGIIA_SYSTEM_PROMPT, user_msg, "anthropic", "claude-sonnet-4-5-20250929"
            )
            analysis_doc = {"id": str(uuid.uuid4()), "type_dossier": type_dossier, "regime": regime, "situation": situation[:500], "is_premium": is_premium, "email": email if email else "", "admin_test": is_admin_test, "created_at": datetime.now(timezone.utc).isoformat()}
            await db.strategiia_analyses.insert_one(analysis_doc)
            remaining = 3
            if not is_premium and email:
                now = datetime.now(timezone.utc)
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
                usage_count = await db.strategiia_analyses.count_documents({"email": email, "is_premium": False, "created_at": {"$gte": month_start}})
                remaining = max(0, 3 - usage_count)
            _jobs[job_id] = {"status": "done", "result": {"success": True, "analysis": response, "cases_found": len(similar_cases), "remaining": remaining}}
            return
        except Exception as e:
            last_error = str(e)
            logger.warning(f"StratégiIA attempt {attempt+1}/3 failed: {last_error}")
            if attempt < 2:
                await asyncio.sleep(3)
    logger.error(f"StratégiIA all 3 attempts failed: {last_error}")
    if "budget" in last_error.lower() or "exceeded" in last_error.lower():
        _jobs[job_id] = {"status": "error", "error": "Le service d'analyse IA est temporairement indisponible."}
    else:
        _jobs[job_id] = {"status": "error", "error": "L'analyse a échoué après plusieurs tentatives. Veuillez réessayer."}


@router.post("/strategiia/analyze")
async def strategiia_analyze(request: Request):
    body = await request.json()
    situation = body.get("situation", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    is_premium = body.get("premium", False)
    email = body.get("email", "").strip().lower()
    is_admin_test = body.get("admin_test", False)
    # Check admin token manually if admin_test requested
    if is_admin_test:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                payload = jwt.decode(auth_header.split(" ", 1)[1], JWT_SECRET, algorithms=[JWT_ALGORITHM])
                is_admin_test = payload.get("is_admin", False)
            except Exception:
                is_admin_test = False
        else:
            is_admin_test = False
    if not situation.strip():
        raise HTTPException(status_code=400, detail="Description de la situation requise")
    if not _has_llm_key():
        raise HTTPException(status_code=503, detail="Service IA non disponible — aucune cle configuree")
    # Admin bypass: skip quota check
    if not is_admin_test and not is_premium and email:
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        usage_count = await db.strategiia_analyses.count_documents({"email": email, "is_premium": False, "created_at": {"$gte": month_start}})
        if usage_count >= 3:
            return {"success": False, "quota_exceeded": True, "remaining": 0, "message": "Vous avez utilisé vos 3 analyses gratuites ce mois-ci."}

    similar_cases = []
    if type_dossier:
        similar_cases = await db.cas_anonymises.find({"type_dossier": type_dossier}, {"_id": 0}).sort("score_pertinence", -1).to_list(5)
    case_context = ""
    if similar_cases:
        case_context = "\n\nCAS SIMILAIRES ANONYMISÉS DANS LA BASE :\n"
        for c in similar_cases:
            case_context += f"- Type: {c.get('type_dossier')}, Régime: {c.get('regime')}, Durée: {c.get('duree')}, Stratégie: {c.get('strategie')}, Résultat: {c.get('resultat')}, Score: {c.get('score_pertinence', 'N/A')}/100\n"

    job_id = str(uuid.uuid4())[:12]
    _jobs[job_id] = {"status": "pending"}
    asyncio.create_task(_run_analysis(job_id, type_dossier, regime, situation, is_premium, email, similar_cases, case_context, is_admin_test=is_admin_test))
    return {"job_id": job_id, "status": "pending", "admin_test": is_admin_test}


@router.get("/strategiia/status/{job_id}")
async def strategiia_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    if job["status"] == "done":
        result = job["result"]
        del _jobs[job_id]
        return {"status": "done", **result}
    elif job["status"] == "error":
        error = job["error"]
        del _jobs[job_id]
        return {"status": "error", "error": error}
    return {"status": "pending"}

@router.get("/strategiia/score")
async def get_relevance_score(type_dossier: str, regime: str = ""):
    query = {"type_dossier": type_dossier}
    if regime:
        query["regime"] = regime
    cases = await db.cas_anonymises.find(query, {"_id": 0, "resultat": 1, "score_pertinence": 1, "strategie": 1, "duree": 1}).to_list(500)
    total = len(cases)
    if total == 0 and regime:
        cases = await db.cas_anonymises.find({"type_dossier": type_dossier}, {"_id": 0, "resultat": 1, "score_pertinence": 1, "strategie": 1, "duree": 1}).to_list(500)
        total = len(cases)
    if total == 0:
        return {"score": None, "confidence": "insufficient_data", "total_cases": 0, "message": "Pas assez de cas similaires pour estimer un score de pertinence.", "distribution": {}}
    favorable = sum(1 for c in cases if c.get("resultat", "").lower() in ("favorable", "très favorable", "accepté", "accord"))
    defavorable = sum(1 for c in cases if c.get("resultat", "").lower() in ("défavorable", "refusé", "rejet", "refus"))
    en_cours = sum(1 for c in cases if c.get("resultat", "").lower() in ("en cours", "en attente", "partiel"))
    other = total - favorable - defavorable - en_cours
    scored_cases = [c for c in cases if c.get("score_pertinence") and c["score_pertinence"] > 0]
    avg_admin_score = round(sum(c["score_pertinence"] for c in scored_cases) / len(scored_cases)) if scored_cases else None
    decided = favorable + defavorable
    success_rate = round(favorable / decided * 100) if decided > 0 else None
    if success_rate is not None and avg_admin_score is not None:
        composite = round(success_rate * 0.6 + avg_admin_score * 0.4)
    elif success_rate is not None:
        composite = success_rate
    elif avg_admin_score is not None:
        composite = avg_admin_score
    else:
        composite = None
    confidence = "high" if total >= 20 else ("medium" if total >= 5 else "low")
    favorable_cases = [c for c in cases if c.get("resultat", "").lower() in ("favorable", "très favorable", "accepté", "accord")]
    strategies = {}
    for c in favorable_cases:
        s = c.get("strategie", "").strip()
        if s:
            strategies[s] = strategies.get(s, 0) + 1
    top_strategies = sorted(strategies.items(), key=lambda x: -x[1])[:3]
    return {"score": composite, "success_rate": success_rate, "avg_admin_score": avg_admin_score, "confidence": confidence, "total_cases": total, "distribution": {"favorable": favorable, "defavorable": defavorable, "en_cours": en_cours, "autre": other}, "top_strategies": [{"strategie": s, "count": c} for s, c in top_strategies], "message": f"Score basé sur {total} cas similaires ({confidence} confiance)."}


# ==================== DOSSIER QUALITY SCORE ====================

ESSENTIAL_DOCS_BY_TYPE = {
    "at": ["Certificat médical initial", "Déclaration d'accident", "Arrêt de travail", "Notification CPAM", "Bulletins de salaire"],
    "mp": ["Certificat médical initial", "Déclaration de maladie professionnelle", "Attestation d'exposition", "Notification CPAM", "Examens médicaux", "Fiche de poste"],
    "mdph": ["Formulaire Cerfa", "Certificat médical récent", "Justificatif d'identité", "Justificatif de domicile", "Bilans médicaux"],
    "assurance": ["Contrat d'assurance", "Déclaration de sinistre", "Courriers assureur", "Certificat médical", "Rapport d'expertise"],
    "expertise": ["Convocation expertise", "Certificats médicaux", "Historique médical", "Notification taux IPP"],
    "faute_inex": ["Certificat médical initial", "Déclaration d'accident", "Arrêt de travail", "Notification CPAM", "Preuves faute employeur"],
    "recours": ["Décision contestée", "Courrier de recours", "Certificat médical", "Pièces justificatives"],
}

@router.post("/strategiia/dossier-score")
async def get_dossier_score(request: Request):
    body = await request.json()
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    situation = body.get("situation", "")
    doc_count = body.get("doc_count", 0)
    doc_names = body.get("doc_names", [])

    essential = ESSENTIAL_DOCS_BY_TYPE.get(type_dossier, ESSENTIAL_DOCS_BY_TYPE.get("at", []))

    # 1. Completeness score: documents provided vs essential
    matched = 0
    matched_docs = []
    missing_docs = []
    for ed in essential:
        ed_lower = ed.lower()
        found = False
        for dn in doc_names:
            if any(keyword in dn.lower() for keyword in ed_lower.split()):
                found = True
                break
        if found or doc_count >= len(essential):
            matched += 1
            matched_docs.append(ed)
        else:
            missing_docs.append(ed)

    completeness = round((matched / len(essential)) * 100) if essential else 100

    # 2. Coherence score: situation detail + type match
    coherence = 50
    if situation:
        word_count = len(situation.split())
        if word_count >= 80:
            coherence = 100
        elif word_count >= 40:
            coherence = 80
        elif word_count >= 20:
            coherence = 60
    if type_dossier and regime:
        coherence = min(100, coherence + 10)

    # 3. Key documents presence score
    key_doc_score = 100 if doc_count >= 3 else round((doc_count / 3) * 100)

    # Composite score
    composite = round(completeness * 0.45 + coherence * 0.30 + key_doc_score * 0.25)

    # Pedagogical tips
    tips = []
    if completeness < 80:
        tips.append(f"Ajoutez les documents manquants : {', '.join(missing_docs[:3])}")
    if coherence < 70:
        tips.append("Détaillez davantage votre situation (dates, faits, conséquences) pour une analyse plus précise")
    if key_doc_score < 100:
        tips.append(f"Fournissez au moins 3 pièces justificatives ({doc_count}/3 actuellement)")
    if not tips:
        tips.append("Votre dossier est bien constitué. L'analyse sera optimale.")

    # Score level
    if composite >= 80:
        level = "excellent"
        level_label = "Excellent"
        level_color = "green"
    elif composite >= 60:
        level = "bon"
        level_label = "Bon"
        level_color = "blue"
    elif composite >= 40:
        level = "moyen"
        level_label = "A compléter"
        level_color = "orange"
    else:
        level = "faible"
        level_label = "Insuffisant"
        level_color = "red"

    return {
        "score": composite,
        "level": level,
        "level_label": level_label,
        "level_color": level_color,
        "details": {
            "completeness": {"score": completeness, "label": "Complétude des documents", "matched": len(matched_docs), "total": len(essential)},
            "coherence": {"score": coherence, "label": "Richesse de la description"},
            "key_documents": {"score": key_doc_score, "label": "Pièces justificatives", "count": doc_count},
        },
        "missing_documents": missing_docs,
        "tips": tips,
    }

@router.get("/strategiia/quota/{email}")
async def strategiia_quota(email: str):
    email = email.strip().lower()
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    usage_count = await db.strategiia_analyses.count_documents({"email": email, "is_premium": False, "created_at": {"$gte": month_start}})
    remaining = max(0, 3 - usage_count)
    return {"remaining": remaining, "limit": 3, "used": min(usage_count, 3)}

@router.post("/strategiia/register-email")
async def strategiia_register_email(request: Request):
    body = await request.json()
    email = body.get("email", "").strip().lower()
    is_admin_test = body.get("admin_test", False)
    # Check admin token manually if admin_test requested
    if is_admin_test:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                payload = jwt.decode(auth_header.split(" ", 1)[1], JWT_SECRET, algorithms=[JWT_ALGORITHM])
                is_admin_test = payload.get("is_admin", False)
            except Exception:
                is_admin_test = False
        else:
            is_admin_test = False
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Email invalide")
    # Admin test: don't create leads, return unlimited quota
    if is_admin_test:
        return {"success": True, "email": email, "remaining": 999, "admin_test": True}
    await db.leads.update_one({"email": email}, {"$set": {"email": email, "source": "strategiia_readwall", "updated_at": datetime.now(timezone.utc).isoformat()}, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}}, upsert=True)
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    usage_count = await db.strategiia_analyses.count_documents({"email": email, "is_premium": False, "created_at": {"$gte": month_start}})
    remaining = max(0, 3 - usage_count)
    return {"success": True, "email": email, "remaining": remaining}

@router.post("/strategiia/checkout")
async def strategiia_checkout(request: Request):
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    body = await request.json()
    origin_url = body.get("origin_url", "").rstrip('/')
    email = body.get("email", "")
    analysis_context = body.get("context", "")
    premium_pdf = body.get("premium_pdf", False)
    analyse_premium = body.get("analyse_premium", False)
    amount = 29.00
    if premium_pdf:
        amount += 19.00
    if analyse_premium:
        amount += 29.00
    params = f"premium_pdf={'1' if premium_pdf else '0'}&analyse_premium={'1' if analyse_premium else '0'}"
    success_url = f"{origin_url}/simulateur?strategiia=success&session_id={{CHECKOUT_SESSION_ID}}&{params}"
    cancel_url = f"{origin_url}/simulateur?strategiia=cancelled"
    stripe_sdk.api_key = STRIPE_API_KEY
    product_tag = "strategiia_premium"
    if premium_pdf and analyse_premium:
        product_tag = "strategiia_premium_full"
    elif premium_pdf:
        product_tag = "strategiia_premium_pdf"
    elif analyse_premium:
        product_tag = "strategiia_analyse_premium"
    metadata = {"product": product_tag, "customer_email": email, "context": analysis_context[:200], "premium_pdf": "1" if premium_pdf else "0", "analyse_premium": "1" if analyse_premium else "0"}
    if analyse_premium:
        pa_entry = {"id": str(uuid.uuid4()), "type": Service.STRATEGIIA, "email": email, "context": analysis_context[:500], "status": PremiumStatus.EN_ATTENTE, "premium_pdf": premium_pdf, "analyse_premium": True, "relecture_expert_required": True, "amount": amount, "created_at": datetime.now(timezone.utc).isoformat()}
        assert_premium_analyses_entry(pa_entry, "strategiia_checkout")
        await db.premium_analyses.insert_one(pa_entry)
        logger.info(f"[STRATEGIIA][checkout] premium_analyses entry {pa_entry['id']} created for {email}")
        asyncio.create_task(notify_admin_premium_analysis(Service.STRATEGIIA, email, "", amount, options={"analyse_premium": True, "premium_pdf": premium_pdf, "context": analysis_context[:300]}))
    try:
        session = await asyncio.to_thread(
            stripe_sdk.checkout.Session.create,
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "eur", "product_data": {"name": f"StratégiIA Premium ({amount:.0f}€)"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata,
        )
        return {"url": session.url, "session_id": session.id}
    except Exception as e:
        logger.error(f"StratégiIA checkout error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")


@router.post("/strategiia/admin-bypass-premium")
async def strategiia_admin_bypass(request: Request):
    """Admin bypass: skips Stripe checkout and runs premium analysis directly."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="Non autorisé")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")
    body = await request.json()
    situation = body.get("situation", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    premium_pdf = body.get("premium_pdf", False)
    analyse_premium = body.get("analyse_premium", False)
    email = payload.get("email", "admin@test")
    if not situation.strip() or not _has_llm_key():
        raise HTTPException(status_code=400, detail="Situation requise et service IA actif")
    similar_cases = []
    if type_dossier:
        similar_cases = await db.cas_anonymises.find({"type_dossier": type_dossier}, {"_id": 0}).sort("score_pertinence", -1).to_list(5)
    case_context = ""
    if similar_cases:
        case_context = "\n\nCAS SIMILAIRES ANONYMISÉS DANS LA BASE :\n"
        for c in similar_cases:
            case_context += f"- Type: {c.get('type_dossier')}, Régime: {c.get('regime')}, Durée: {c.get('duree')}, Stratégie: {c.get('strategie')}, Résultat: {c.get('resultat')}, Score: {c.get('score_pertinence', 'N/A')}/100\n"
    job_id = str(uuid.uuid4())[:12]
    _jobs[job_id] = {"status": "pending"}
    asyncio.create_task(_run_analysis(job_id, type_dossier, regime, situation, True, email, similar_cases, case_context, is_admin_test=True))

    # Register in premium_analyses for admin relecture workflow
    pa_entry = {
        "id": str(uuid.uuid4()), "type": Service.STRATEGIIA, "email": email,
        "context": situation[:500], "status": PremiumStatus.EN_ATTENTE,
        "premium_pdf": premium_pdf, "analyse_premium": True,
        "relecture_expert_required": True, "admin_test": True,
        "amount": 0, "job_id": job_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    assert_premium_analyses_entry(pa_entry, f"strategiia_admin_bypass_{job_id}")
    await db.premium_analyses.insert_one(pa_entry)
    logger.info(f"[STRATEGIIA][admin-bypass][{job_id}] premium_analyses entry {pa_entry['id']} created")

    return {"job_id": job_id, "status": "pending", "admin_test": True, "premium_pdf": premium_pdf, "analyse_premium": analyse_premium}



# dossier_express_admin_bypass -> moved to routes/dossier_express.py

@router.post("/strategiia/generate-pdf")
async def strategiia_generate_pdf(request: Request):
    body = await request.json()
    analysis = body.get("analysis", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    name = body.get("name", "")
    premium_pdf = body.get("premium_pdf", False)
    if not analysis:
        raise HTTPException(status_code=400, detail="Analyse requise")
    pdf_bytes = generate_secured_pdf(analysis=analysis, report_type="StrategiIA", name=name, type_dossier=type_dossier, regime=regime, with_watermark=not premium_pdf)
    encoded = base64.b64encode(pdf_bytes).decode("utf-8")
    return {"pdf_base64": encoded, "filename": "strategiia-rapport.pdf"}


# ==================== CAS ANONYMISES ====================

@router.get("/admin/cas-anonymises")
async def get_cas_anonymises(admin: dict = Depends(get_current_admin)):
    cases = await db.cas_anonymises.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return {"items": cases, "total": len(cases)}

@router.post("/admin/cas-anonymises")
async def create_cas_anonymise(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    cas = {"id": str(uuid.uuid4()), "type_dossier": body.get("type_dossier", ""), "regime": body.get("regime", ""), "duree": body.get("duree", ""), "strategie": body.get("strategie", ""), "resultat": body.get("resultat", ""), "score_pertinence": body.get("score_pertinence", 0), "notes": body.get("notes", ""), "created_at": datetime.now(timezone.utc).isoformat()}
    await db.cas_anonymises.insert_one(cas)
    return {"success": True, "id": cas["id"]}

@router.delete("/admin/cas-anonymises/{case_id}")
async def delete_cas_anonymise(case_id: str, admin: dict = Depends(get_current_admin)):
    await db.cas_anonymises.delete_one({"id": case_id})
    return {"success": True}

@router.patch("/admin/cas-anonymises/{case_id}")
async def update_cas_anonymise(case_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    update = {}
    for field in ["type_dossier", "regime", "duree", "strategie", "resultat", "score_pertinence", "notes"]:
        if field in body:
            update[field] = body[field]
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.cas_anonymises.update_one({"id": case_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cas non trouvé")
    return {"success": True}

@router.post("/admin/cas-anonymises/import")
async def import_cas_anonymises(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    cases_data = body.get("cases", [])
    if not cases_data or not isinstance(cases_data, list):
        raise HTTPException(status_code=400, detail="Format invalide: 'cases' doit être une liste")
    imported = 0
    for item in cases_data[:100]:
        cas = {"id": str(uuid.uuid4()), "type_dossier": item.get("type_dossier", ""), "regime": item.get("regime", ""), "duree": item.get("duree", ""), "strategie": item.get("strategie", ""), "resultat": item.get("resultat", ""), "score_pertinence": item.get("score_pertinence", 0), "notes": item.get("notes", ""), "created_at": datetime.now(timezone.utc).isoformat()}
        await db.cas_anonymises.insert_one(cas)
        imported += 1
    return {"success": True, "imported": imported}

@router.get("/admin/cas-anonymises/stats")
async def get_cas_stats(admin: dict = Depends(get_current_admin)):
    total = await db.cas_anonymises.count_documents({})
    pipeline = [{"$group": {"_id": "$type_dossier", "count": {"$sum": 1}}}]
    by_type = await db.cas_anonymises.aggregate(pipeline).to_list(50)
    pipeline_regime = [{"$group": {"_id": "$regime", "count": {"$sum": 1}}}]
    by_regime = await db.cas_anonymises.aggregate(pipeline_regime).to_list(50)
    return {"total": total, "by_type": [{k: v for k, v in d.items() if k != "_id"} | {"label": d["_id"] or "Non précisé"} for d in by_type], "by_regime": [{k: v for k, v in d.items() if k != "_id"} | {"label": d["_id"] or "Non précisé"} for d in by_regime]}

@router.get("/admin/strategiia/stats")
async def get_strategiia_stats(admin: dict = Depends(get_current_admin)):
    total_analyses = await db.strategiia_analyses.count_documents({})
    premium = await db.strategiia_analyses.count_documents({"is_premium": True})
    total_cases = await db.cas_anonymises.count_documents({})
    recent = await db.strategiia_analyses.find({}, {"_id": 0}).sort("created_at", -1).to_list(20)
    return {"total_analyses": total_analyses, "premium": premium, "total_cases": total_cases, "recent": recent}
