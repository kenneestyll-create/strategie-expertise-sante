from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import asyncio
import uuid
import base64
import os

from emergentintegrations.llm.chat import LlmChat, UserMessage

from config import db, EMERGENT_LLM_KEY, STRIPE_API_KEY, RESEND_AVAILABLE, SENDER_EMAIL, logger
from utils.auth import get_current_admin
from utils.email import notify_admin_premium_analysis
from utils.pdf import generate_secured_pdf, generate_dossier_pdf

from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest

try:
    import resend
except ImportError:
    pass

router = APIRouter()

STRATEGIIA_SYSTEM_PROMPT = """Tu es StratégiIA, l'outil d'analyse stratégique exclusif de Stratégie & Expertise Santé.

Tu analyses les dossiers de victimes d'accidents du travail, maladies professionnelles, litiges assurantiels et demandes MDPH en t'appuyant sur :

1. JURISPRUDENCES DE RÉFÉRENCE :
- Cass. soc. 2019 : L'employeur doit prouver qu'il a pris les mesures de prévention (obligation de sécurité de résultat → obligation de moyens renforcée depuis 2015)
- Cass. 2e civ. 2020 : Le taux d'IPP doit tenir compte de l'incidence professionnelle réelle
- CE 2018 : La MDPH doit motiver ses décisions de refus et répondre sous 4 mois
- Cass. 2e civ. 2021 : La faute inexcusable peut être reconnue même en cas de respect partiel des normes
- Cass. 2e civ. 2022 : Le silence de la CPAM au-delà du délai vaut acceptation implicite
- TA/CAA multiples : Le CRRMP doit examiner le lien direct et essentiel avec le travail habituel

2. STATISTIQUES CNAM (données publiques) :
- ~650 000 AT/an, ~50 000 MP/an reconnues
- TMS (Tableau 57) = 87% des MP reconnues
- Taux moyen d'IPP AT : 9%, MP : 14%
- Délai moyen instruction CPAM : 3-4 mois
- Taux de contestation aboutissant : ~35% en CRA, ~45% au tribunal
- Faute inexcusable reconnue dans ~60% des cas portés en justice

3. BARÈMES IPP OFFICIELS :
- Taux < 10% : capital forfaitaire (barème annexe Code SS)
- Taux ≥ 10% : rente = salaire × taux utile (moitié jusqu'à 50%, totalité au-delà)
- Barème indicatif d'invalidité AT/MP (annexe à l'art. R434-32 du Code SS)

RÈGLES :
- Réponds TOUJOURS en français
- Structure ta réponse en sections claires : Analyse de la situation, Jurisprudences applicables, Stratégie recommandée, Chances de succès estimées, Prochaines étapes
- Donne un score de pertinence sur 100 basé sur la similarité avec des cas similaires
- Sois précis et factuel, cite les textes et jurisprudences pertinents
- Rappelle TOUJOURS que c'est un outil d'aide à la décision et non un conseil juridique
- Si des cas anonymisés similaires existent dans la base, mentionne les statistiques de résultats"""

STRATEGIIA_BASIC_PROMPT = """Analyse BASIQUE demandée. Fournis :
1. Une synthèse courte de la situation (3-4 lignes)
2. Les principaux droits identifiés (liste à puces, max 4)
3. La première démarche prioritaire à effectuer
4. Un score de pertinence approximatif sur 100

Reste concis (max 300 mots). Mentionne qu'un rapport complet est disponible pour une analyse approfondie."""

STRATEGIIA_PREMIUM_PROMPT = """Analyse COMPLÈTE demandée. Fournis un rapport détaillé structuré :

## Analyse de votre situation
(Résumé détaillé en 5-6 lignes)

## Jurisprudences applicables
(2-3 jurisprudences pertinentes avec références et ce qu'elles impliquent)

## Vos droits identifiés
(Liste exhaustive avec explications)

## Stratégie recommandée
(Plan d'action en étapes numérotées avec justification)

## Estimation des chances de succès
(Score sur 100 avec explication des facteurs pris en compte)

## Délais importants
(Dates limites et échéances à respecter)

## Prochaines étapes immédiates
(3 actions concrètes à réaliser dans les prochains jours)

Sois exhaustif et précis (600-800 mots)."""

DOSSIER_EXPRESS_PROMPT = """Tu es un expert en droit de la sécurité sociale, accidents du travail, maladies professionnelles et handicap (MDPH).
On te fournit les documents et la description d'un dossier client. Rédige un RAPPORT D'ANALYSE COMPLET et PROFESSIONNEL.

Structure ton rapport ainsi :

# RAPPORT D'ANALYSE - DOSSIER EXPRESS
## Stratégie & Expertise Santé

### 1. SYNTHÈSE DU DOSSIER
(Résumé factuel de la situation en 5-6 lignes)

### 2. ANALYSE DES DOCUMENTS
(Analyse détaillée de chaque document fourni, points forts et faiblesses)

### 3. CADRE JURIDIQUE APPLICABLE
(Textes de loi, articles du Code de la Sécurité Sociale, jurisprudences pertinentes)

### 4. DROITS IDENTIFIÉS
(Liste exhaustive des droits avec explications claires)

### 5. POINTS DE VIGILANCE
(Faiblesses du dossier, pièces manquantes, risques identifiés)

### 6. STRATÉGIE RECOMMANDÉE
(Plan d'action en étapes numérotées avec justification et délais)

### 7. ESTIMATION DES CHANCES DE SUCCÈS
(Score sur 100 avec explication des facteurs)

### 8. PROCHAINES ÉTAPES IMMÉDIATES
(5 actions concrètes prioritaires à réaliser)

### 9. CONCLUSION ET RECOMMANDATIONS
(Synthèse finale et orientation vers un accompagnement personnalisé si nécessaire)

Sois exhaustif, précis et professionnel (1000-1500 mots).
Rappelle que ce rapport est un outil d'aide à la décision et ne constitue pas un avis juridique.
Mentionne que pour un accompagnement personnalisé, le client peut contacter Stratégie & Expertise Santé."""


# ==================== DOSSIER EXPRESS ====================

@router.post("/dossier-express/submit")
async def dossier_express_submit(request: Request):
    body = await request.json()
    session_id = body.get("session_id", "")
    email = body.get("email", "")
    name = body.get("name", "")
    situation = body.get("situation", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    documents_text = body.get("documents_text", "")
    premium_pdf = body.get("premium_pdf", False)

    if not email or not situation:
        raise HTTPException(status_code=400, detail="Email et description requis")

    # SECURITY FIX V13/V14: Verify payment before processing
    payment_verified = False
    if session_id:
        # Step 1: Check DB for confirmed payment
        payment = await db.payment_transactions.find_one(
            {"session_id": session_id, "payment_status": "paid"},
            {"_id": 0, "session_id": 1}
        )
        if payment:
            payment_verified = True
        else:
            # Step 2: Live Stripe check (handles webhook race condition)
            if STRIPE_API_KEY:
                try:
                    host_url = str(request.base_url).rstrip('/')
                    webhook_url = f"{host_url}/api/webhook/stripe"
                    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
                    status = await stripe_checkout.get_checkout_status(session_id)
                    if status.payment_status == "paid":
                        payment_verified = True
                        # Update DB to reflect confirmed payment
                        await db.payment_transactions.update_one(
                            {"session_id": session_id},
                            {"$set": {"payment_status": "paid", "status": status.status, "updated_at": datetime.now(timezone.utc).isoformat()}}
                        )
                        logger.info(f"Dossier Express IA: live Stripe check confirmed payment for session {session_id}")
                except Exception as e:
                    logger.warning(f"Dossier Express IA: live Stripe check failed for session {session_id}: {e}")

    if not payment_verified:
        if STRIPE_API_KEY:
            raise HTTPException(status_code=402, detail="Paiement requis. Veuillez compléter le paiement avant de soumettre votre dossier.")
        else:
            logger.warning(f"Dossier Express IA submitted without payment verification (Stripe not configured) for {email}")

    dossier_id = str(uuid.uuid4())
    dossier = {
        "id": dossier_id, "session_id": session_id, "email": email, "name": name,
        "situation": situation, "type_dossier": type_dossier, "regime": regime,
        "documents_text": documents_text[:10000], "premium_pdf": premium_pdf,
        "status": "processing", "payment_verified": payment_verified,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.dossier_express.insert_one(dossier)
    asyncio.create_task(_process_dossier_express(dossier_id, email, name, situation, type_dossier, regime, documents_text, premium_pdf=premium_pdf))
    return {"success": True, "dossier_id": dossier_id, "message": "Votre dossier est en cours d'analyse. Vous recevrez le rapport par email sous 2 heures."}


async def _process_dossier_express(dossier_id: str, email: str, name: str, situation: str, type_dossier: str, regime: str, documents_text: str, premium_pdf: bool = False):
    try:
        if not EMERGENT_LLM_KEY:
            logger.error("Dossier Express IA: EMERGENT_LLM_KEY not available")
            await db.dossier_express.update_one({"id": dossier_id}, {"$set": {"status": "error", "error": "Service IA non disponible"}})
            return

        similar_cases = []
        if type_dossier:
            similar_cases = await db.cas_anonymises.find({"type_dossier": type_dossier}, {"_id": 0}).sort("score_pertinence", -1).to_list(5)

        case_context = ""
        if similar_cases:
            case_context = "\n\nCAS SIMILAIRES DANS LA BASE :\n"
            for c in similar_cases:
                case_context += f"- Type: {c.get('type_dossier')}, Régime: {c.get('regime')}, Stratégie: {c.get('strategie')}, Résultat: {c.get('resultat')}\n"

        user_msg = f"""DOSSIER EXPRESS - Analyse complète demandée

Client : {name}
Type de dossier : {type_dossier}
Régime : {regime}

DESCRIPTION DE LA SITUATION :
{situation}

CONTENU DES DOCUMENTS FOURNIS :
{documents_text[:8000] if documents_text else "(Aucun document textuel fourni)"}
{case_context}

{DOSSIER_EXPRESS_PROMPT}"""

        session_id_llm = f"dossier_{dossier_id[:8]}"
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=session_id_llm, system_message=STRATEGIIA_SYSTEM_PROMPT).with_model("anthropic", "claude-sonnet-4-5-20250929")
        analysis = await chat.send_message(UserMessage(text=user_msg))

        pdf_bytes = generate_dossier_pdf(name, email, type_dossier, regime, analysis, premium_pdf=premium_pdf)

        email_sent = False
        if RESEND_AVAILABLE and resend.api_key:
            try:
                resend.Emails.send({
                    "from": SENDER_EMAIL,
                    "to": [email],
                    "subject": "Votre Rapport Dossier Express IA - Stratégie & Expertise Santé",
                    "html": f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h1 style="color: #1a1a2e;">Votre Rapport Dossier Express IA</h1>
                        <p>Bonjour {name or 'Madame, Monsieur'},</p>
                        <p>Merci pour votre confiance. Veuillez trouver ci-joint votre rapport d'analyse complet réalisé par notre outil StratégiIA.</p>
                        <p>Ce rapport contient :</p><ul><li>L'analyse détaillée de votre situation</li><li>Le cadre juridique applicable</li><li>Vos droits identifiés</li><li>La stratégie recommandée</li><li>Les prochaines étapes à suivre</li></ul>
                        <p>Pour un accompagnement personnalisé, n'hésitez pas à nous contacter :</p>
                        <p><a href="https://non-blocking-ocr.preview.emergentagent.com/contact" style="color: #0f3460;">Prendre rendez-vous</a></p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="font-size: 12px; color: #666;">Ce rapport est un outil d'aide à la décision et ne constitue pas un avis juridique.<br>Stratégie & Expertise Santé</p></div>""",
                    "attachments": [{"filename": f"Rapport_Dossier_Express_{dossier_id[:8]}.pdf", "content": list(pdf_bytes)}]
                })
                email_sent = True
                logger.info(f"Dossier Express IA {dossier_id}: email sent to {email}")
            except Exception as e:
                logger.error(f"Dossier Express IA email error: {e}")

        await db.dossier_express.update_one({"id": dossier_id}, {"$set": {"status": "completed", "analysis": analysis[:5000], "email_sent": email_sent, "completed_at": datetime.now(timezone.utc).isoformat()}})
    except Exception as e:
        logger.error(f"Dossier Express IA processing error: {e}")
        await db.dossier_express.update_one({"id": dossier_id}, {"$set": {"status": "error", "error": str(e)}})


@router.post("/dossier-express/checkout")
async def dossier_express_checkout(request: Request):
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configure")
    body = await request.json()
    origin_url = body.get("origin_url", "").rstrip('/')
    email = body.get("email", "")
    name = body.get("name", "")
    premium_pdf = body.get("premium_pdf", False)
    analyse_premium = body.get("analyse_premium", False)
    amount = 97.00
    if premium_pdf:
        amount += 19.00
    if analyse_premium:
        amount += 49.00
    params = f"premium_pdf={'1' if premium_pdf else '0'}&analyse_premium={'1' if analyse_premium else '0'}"
    success_url = f"{origin_url}/dossier-express?payment=success&session_id={{CHECKOUT_SESSION_ID}}&{params}"
    cancel_url = f"{origin_url}/dossier-express?payment=cancelled"
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    tag = "dossier_express"
    if premium_pdf and analyse_premium:
        tag = "dossier_express_full"
    elif premium_pdf:
        tag = "dossier_express_pdf_pro"
    elif analyse_premium:
        tag = "dossier_express_analyse_premium"
    checkout_request = CheckoutSessionRequest(amount=amount, currency="eur", success_url=success_url, cancel_url=cancel_url, metadata={"package_id": tag, "package_name": f"Dossier Express IA ({amount:.0f}€)", "customer_email": email, "customer_name": name, "premium_pdf": "1" if premium_pdf else "0", "analyse_premium": "1" if analyse_premium else "0"})
    if analyse_premium:
        await db.premium_analyses.insert_one({"id": str(uuid.uuid4()), "type": "dossier_express", "email": email, "name": name, "status": "en_attente", "premium_pdf": premium_pdf, "amount": amount, "created_at": datetime.now(timezone.utc).isoformat()})
        asyncio.create_task(notify_admin_premium_analysis("dossier_express", email, name, amount))
    try:
        session = await stripe_checkout.create_checkout_session(checkout_request)
        return {"success": True, "url": session.url, "session_id": session.session_id}
    except Exception as e:
        logger.error(f"Dossier Express IA checkout error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")

@router.get("/dossier-express/status/{dossier_id}")
async def dossier_express_status(dossier_id: str):
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0, "documents_text": 0})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouve")
    return dossier

@router.get("/admin/dossier-express")
async def admin_dossier_express(admin: dict = Depends(get_current_admin)):
    dossiers = await db.dossier_express.find({}, {"_id": 0, "documents_text": 0, "analysis": 0}).sort("created_at", -1).to_list(100)
    stats = {"total": len(dossiers), "completed": sum(1 for d in dossiers if d.get("status") == "completed"), "processing": sum(1 for d in dossiers if d.get("status") == "processing"), "errors": sum(1 for d in dossiers if d.get("status") == "error")}
    return {"items": dossiers, "stats": stats}

@router.get("/dossier-express/weekly-count")
async def dossier_express_weekly_count():
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    real_count = await db.dossier_express.count_documents({"created_at": {"$gte": week_start}})
    display_count = 12 + real_count
    return {"count": display_count, "period": "week"}


# ==================== STRATEGIIA ====================

@router.post("/strategiia/analyze")
async def strategiia_analyze(request: Request):
    body = await request.json()
    situation = body.get("situation", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    is_premium = body.get("premium", False)
    email = body.get("email", "").strip().lower()
    if not situation.strip():
        raise HTTPException(status_code=400, detail="Description de la situation requise")
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=503, detail="Service IA non disponible")
    if not is_premium and email:
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        usage_count = await db.strategiia_analyses.count_documents({"email": email, "is_premium": False, "created_at": {"$gte": month_start}})
        if usage_count >= 3:
            return {"success": False, "quota_exceeded": True, "remaining": 0, "message": "Vous avez utilisé vos 3 analyses gratuites ce mois-ci. Passez au Dossier Express IA pour une analyse complète."}

    similar_cases = []
    if type_dossier:
        similar_cases = await db.cas_anonymises.find({"type_dossier": type_dossier}, {"_id": 0}).sort("score_pertinence", -1).to_list(5)
    case_context = ""
    if similar_cases:
        case_context = "\n\nCAS SIMILAIRES ANONYMISÉS DANS LA BASE :\n"
        for c in similar_cases:
            case_context += f"- Type: {c.get('type_dossier')}, Régime: {c.get('regime')}, Durée: {c.get('duree')}, Stratégie: {c.get('strategie')}, Résultat: {c.get('resultat')}, Score: {c.get('score_pertinence', 'N/A')}/100\n"

    analysis_prompt = STRATEGIIA_PREMIUM_PROMPT if is_premium else STRATEGIIA_BASIC_PROMPT
    user_msg = f"""Type de dossier : {type_dossier}\nRégime : {regime}\nDescription de la situation : {situation}\n{case_context}\n\n{analysis_prompt}"""

    try:
        session_id = f"strategiia_{str(uuid.uuid4())[:8]}"
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=session_id, system_message=STRATEGIIA_SYSTEM_PROMPT).with_model("anthropic", "claude-sonnet-4-5-20250929")
        response = await chat.send_message(UserMessage(text=user_msg))
        analysis_doc = {"id": str(uuid.uuid4()), "type_dossier": type_dossier, "regime": regime, "situation": situation[:500], "is_premium": is_premium, "email": email if email else "", "created_at": datetime.now(timezone.utc).isoformat()}
        await db.strategiia_analyses.insert_one(analysis_doc)
        remaining = 3
        if not is_premium and email:
            now = datetime.now(timezone.utc)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
            usage_count = await db.strategiia_analyses.count_documents({"email": email, "is_premium": False, "created_at": {"$gte": month_start}})
            remaining = max(0, 3 - usage_count)
        return {"success": True, "analysis": response, "cases_found": len(similar_cases), "remaining": remaining}
    except Exception as e:
        logger.error(f"StratégiIA error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'analyse IA")

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
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Email invalide")
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
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    product_tag = "strategiia_premium"
    if premium_pdf and analyse_premium:
        product_tag = "strategiia_premium_full"
    elif premium_pdf:
        product_tag = "strategiia_premium_pdf"
    elif analyse_premium:
        product_tag = "strategiia_analyse_premium"
    checkout_request = CheckoutSessionRequest(amount=amount, currency="eur", success_url=success_url, cancel_url=cancel_url, metadata={"product": product_tag, "customer_email": email, "context": analysis_context[:200], "premium_pdf": "1" if premium_pdf else "0", "analyse_premium": "1" if analyse_premium else "0"})
    if analyse_premium:
        await db.premium_analyses.insert_one({"id": str(uuid.uuid4()), "type": "strategiia", "email": email, "context": analysis_context[:500], "status": "en_attente", "premium_pdf": premium_pdf, "amount": amount, "created_at": datetime.now(timezone.utc).isoformat()})
        asyncio.create_task(notify_admin_premium_analysis("strategiia", email, "", amount))
    try:
        session = await stripe_checkout.create_checkout_session(checkout_request)
        return {"url": session.url, "session_id": session.session_id}
    except Exception as e:
        logger.error(f"StratégiIA checkout error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")

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
