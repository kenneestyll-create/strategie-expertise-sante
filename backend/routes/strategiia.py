from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import asyncio
import uuid
import base64
import os
import jwt

from emergentintegrations.llm.chat import LlmChat, UserMessage

from config import db, EMERGENT_LLM_KEY, STRIPE_API_KEY, RESEND_AVAILABLE, SENDER_EMAIL, logger, JWT_SECRET, JWT_ALGORITHM
from utils.auth import get_current_admin, get_optional_admin
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

4. INCIDENCE PROFESSIONNELLE (IP) :
- Poste de préjudice indemnisant les conséquences sur la vie professionnelle au-delà de la simple perte de revenus
- Critères d'évaluation : pénibilité accrue au poste, dévalorisation sur le marché du travail, perte d'opportunités professionnelles (promotions, formations), nécessité de reconversion
- Justificatifs clés : rapports médicaux, expertises, attestations employeur, éléments de carrière
- Indemnisation variable selon le profil : de 15 000€ (reclassement simple) à 100 000€+ (reconversion totale)

5. PERTE DE GAINS PROFESSIONNELS FUTURS (PGPF) :
- Poste de préjudice (nomenclature Dintilhac) compensant la réduction définitive de revenus après consolidation
- Distinction avec PGPA (perte de gains actuels, avant consolidation)
- Méthode de calcul : (salaire annuel sans accident - salaire annuel avec séquelles) × euro de rente (barème de capitalisation Gazette du Palais selon âge)
- Éléments de projection : carrière hypothétique, évolution salariale prévisible, impact du handicap, conventions collectives
- Justificatifs : bulletins de salaire (12-36 mois), contrats de travail, expertises économiques et médicales

RÈGLES :
- Réponds TOUJOURS en français
- Structure ta réponse en sections claires : Analyse de la situation, Jurisprudences applicables, Stratégie recommandée, Chances de succès estimées, Prochaines étapes
- Donne un score de pertinence sur 100 basé sur la similarité avec des cas similaires
- Sois précis et factuel, cite les textes et jurisprudences pertinents
- Évalue systématiquement l'incidence professionnelle (IP) et la perte de gains professionnels futurs (PGPF) quand le dossier concerne un AT/MP avec séquelles professionnelles
- Pour l'IP : identifie les critères applicables (pénibilité, dévalorisation, reconversion, perte d'opportunités)
- Pour la PGPF : estime si une perte de revenus future est caractérisée et suggère la méthode de calcul
- Rappelle TOUJOURS que c'est un outil d'aide à la décision et non un conseil juridique
- Si des cas anonymisés similaires existent dans la base, mentionne les statistiques de résultats
- NE GÉNÈRE JAMAIS d'URL, de lien hypertexte, d'adresse web ou de nom de domaine dans ta réponse. Pas de https://, pas de .fr, pas de .com. Le bloc contact est géré automatiquement par le système."""

STRATEGIIA_BASIC_PROMPT = """Tu rediges un rapport de pre-analyse PREMIUM pour un client de Strategie & Expertise Sante. Ton style doit etre chaleureux, humain, professionnel et rassurant -- comme un expert bienveillant qui s'adresse personnellement a quelqu'un.

CONTRAINTES STRICTES :
- Maximum 350 mots au total (le rapport doit tenir sur UNE page PDF)
- Pas de formulations robotiques ou froides
- Pas de listes a rallonge
- Chaque phrase doit apporter de la valeur concrete
- Ton chaleureux de cabinet d'accompagnement premium

STRUCTURE EXACTE (respecte les marqueurs) :

---SECTION_1---
## Votre situation analysee
(3-4 lignes. Montre que tu as compris la situation. Ton empathique et rassurant. Commence par "Votre situation..." ou "Au regard de..." -- jamais par "Vous avez decrit...")

## Ce que revele votre dossier
(3-4 lignes. Lecture strategique : enjeux, points forts, elements sensibles. Formule comme un expert qui eclaire.)

---SECTION_2---
## Niveau d'attention recommande
(1-2 lignes. Synthese claire : "Ce dossier merite une attention particuliere car..." ou "La situation presente un potentiel notable...")

## Points de vigilance
- (2-3 points maximum, concrets et utiles)

---SECTION_3---
## Prochaines etapes recommandees
- (3 actions concretes maximum, formulees de maniere actionnable : document a reunir, demarche a anticiper, point a verifier)

## Notre engagement
(2-3 lignes de conclusion humaine et rassurante. Termine par :)
**Vous n'etes plus seul(e) face a votre situation. Strategie & Expertise Sante est a vos cotes.**

Ne genere aucune URL, aucun lien web ni aucun nom de domaine."""

STRATEGIIA_PREMIUM_PROMPT = """Tu rediges un rapport d'analyse APPROFONDI ET PREMIUM pour un client de Strategie & Expertise Sante. Tu es un expert reconnu en droit de la securite sociale. Ton style est celui d'un conseiller de confiance : expert, humain, chaleureux, strategique et rassurant.

CONTRAINTES STRICTES :
- Entre 700 et 900 mots (le rapport doit faire environ une page et demie : dense, riche, utile)
- Chaque section doit apporter une vraie valeur concrete et personnalisee
- Ton de cabinet d'accompagnement haut de gamme
- Formulations incarnees, jamais robotiques
- Cite des references juridiques reelles (articles de loi, jurisprudences) quand pertinent
- Personnalise selon le type de dossier, le regime et la situation specifique

STRUCTURE EXACTE A RESPECTER :

## Votre situation analysee
(5-6 lignes. Reformulation empathique et precise de la situation. Montre une comprehension fine des enjeux personnels et professionnels. Commence par une phrase d'ouverture rassurante comme "A la lecture attentive de votre situation..." ou "Votre dossier revele une situation qui merite toute notre attention...")

## Ce que revele votre dossier
(6-8 lignes. Analyse strategique approfondie : enjeux juridiques, points forts a exploiter, failles a anticiper. Reference aux textes applicables : Code de la securite sociale, Code du travail, nomenclature Dintilhac si applicable. Mentionne l'incidence professionnelle (IP) et la PGPF si pertinent.)

## Cadre juridique applicable
(4-5 lignes. Cite les articles de loi, decrets ou jurisprudences applicables a cette situation precise. Par exemple : Art. L.461-1 CSS pour maladie professionnelle, Art. L.434-2 pour la rente, jurisprudences Cour de cassation ou TASS pertinentes.)

## Evaluation et perspectives
(5-6 lignes. Estimation nuancee des chances de succes. Fourchettes d'indemnisation si applicable. Elements favorables vs defavorables. Comparaison avec des cas similaires si des donnees sont disponibles.)

## Points de vigilance
- (4-5 points concrets : delais de prescription, risques specifiques, erreurs frequentes a eviter, elements manquants critiques, pieces a rassembler en priorite)

## Strategie recommandee
(4-5 lignes. Plan d'action clair et ordonne. Quelles demarches en premier, dans quel ordre, avec quels delais. Formule de maniere actionnable et concrete.)

## Prochaines etapes concretes
1. (action immediate avec delai)
2. (action a court terme)
3. (action a moyen terme)
4. (action optionnelle si applicable)

## Notre engagement a vos cotes
(4-5 lignes. Conclusion humaine, chaleureuse et rassurante. Vision d'ensemble et perspective d'accompagnement. Termine TOUJOURS par exactement ces deux lignes sur des lignes separees :)

**Vous n'etes plus seul(e) face a votre situation.**
**Desormais, Strategie & Expertise Sante devient votre bouclier.**

---

*Selon les elements identifies dans votre dossier, [recommande de maniere naturelle et elegante le service le plus adapte parmi : une analyse StrategiIA approfondie, un Dossier Express pour un traitement complet, un accompagnement personnalise, ou une prise de rendez-vous pour un premier echange gratuit]. Formule comme un conseil bienveillant, pas comme une publicite.*

Sois exhaustif, precis et concret tout en restant fluide et elegant.
Ne genere aucune URL, aucun lien web ni aucun nom de domaine."""

DOSSIER_EXPRESS_PROMPT = """Tu es un expert en droit de la sécurité sociale, accidents du travail, maladies professionnelles et handicap (MDPH).
On te fournit les documents et la description d'un dossier client. Rédige un RAPPORT D'ANALYSE COMPLET et PROFESSIONNEL.

Structure ton rapport ainsi :

# RAPPORT D'ANALYSE - DOSSIER EXPRESS
## Stratégie & Expertise Santé

### 1. SYNTHÈSE DU DOSSIER
(Résumé factuel de la situation, cadre juridique applicable, textes de loi pertinents)

### 2. DROITS ET INDEMNISATIONS IDENTIFIÉS
(Liste exhaustive des droits, incluant l'incidence professionnelle et la perte de gains futurs si applicable)

### 3. FORCES ET POINTS DE VIGILANCE
(Points forts du dossier, pièces manquantes, risques identifiés)

### 4. STRATÉGIE RECOMMANDÉE ET PROCHAINES ÉTAPES
(Plan d'action en étapes numérotées avec délais, estimation des chances de succès)

### 5. CONCLUSION
(Synthèse finale et orientation vers un accompagnement personnalisé si nécessaire)

Sois exhaustif, précis et professionnel (800 mots maximum).
Rappelle que ce rapport est un outil d'aide à la décision et ne constitue pas un avis juridique.
Mentionne que pour un accompagnement personnalisé, le client peut contacter Stratégie & Expertise Santé.
Ne génère aucune URL, aucun lien web ni aucun nom de domaine dans ta réponse."""


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
        analysis = await asyncio.to_thread(
            _llm_sync_call, EMERGENT_LLM_KEY, session_id_llm, STRATEGIIA_SYSTEM_PROMPT, user_msg, "anthropic", "claude-sonnet-4-5-20250929"
        )

        pdf_bytes = generate_dossier_pdf(name, email, type_dossier, regime, analysis, premium_pdf=premium_pdf)

        email_sent = False
        if RESEND_AVAILABLE and resend.api_key:
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [email],
                    "subject": "Votre Rapport Dossier Express IA - Stratégie & Expertise Santé",
                    "html": f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h1 style="color: #1a1a2e;">Votre Rapport Dossier Express IA</h1>
                        <p>Bonjour {name or 'Madame, Monsieur'},</p>
                        <p>Merci pour votre confiance. Veuillez trouver ci-joint votre rapport d'analyse complet réalisé par notre outil StratégiIA.</p>
                        <p>Ce rapport contient :</p><ul><li>L'analyse détaillée de votre situation</li><li>Le cadre juridique applicable</li><li>Vos droits identifiés</li><li>La stratégie recommandée</li><li>Les prochaines étapes à suivre</li></ul>
                        <p>Pour un accompagnement personnalisé, n'hésitez pas à nous contacter :</p>
                        <p><a href="https://mascot-tips-admin.preview.emergentagent.com/contact" style="color: #0f3460;">Prendre rendez-vous</a></p>
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
        await db.premium_analyses.insert_one({"id": str(uuid.uuid4()), "type": "dossier_express", "email": email, "name": name, "status": "en_attente", "relecture_expert_required": True, "premium_pdf": premium_pdf, "amount": amount, "created_at": datetime.now(timezone.utc).isoformat()})
        asyncio.create_task(notify_admin_premium_analysis("dossier_express", email, name, amount, options={"analyse_premium": True, "premium_pdf": premium_pdf}))
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

# In-memory job store for async polling
_jobs = {}

def _llm_sync_call(api_key, session_id, system_message, user_text, provider, model):
    """Run LLM in a separate thread to avoid blocking the asyncio event loop.
    emergentintegrations uses litellm.completion() (synchronous) internally."""
    import asyncio as _aio
    import litellm as _lt
    _lt.request_timeout = 180
    chat = LlmChat(api_key=api_key, session_id=session_id, system_message=system_message).with_model(provider, model)
    chat.extra_params["timeout"] = 180
    chat.extra_params["request_timeout"] = 180
    return _aio.run(chat.send_message(UserMessage(text=user_text)))


async def _run_analysis(job_id, type_dossier, regime, situation, is_premium, email, similar_cases, case_context, is_admin_test=False):
    """Background task for LLM analysis with retry."""
    last_error = ""
    for attempt in range(3):
        try:
            analysis_prompt = STRATEGIIA_PREMIUM_PROMPT if is_premium else STRATEGIIA_BASIC_PROMPT
            user_msg = f"""Type de dossier : {type_dossier}\nRégime : {regime}\nDescription de la situation : {situation}\n{case_context}\n\n{analysis_prompt}"""
            session_id = f"strategiia_{str(uuid.uuid4())[:8]}"
            response = await asyncio.to_thread(
                _llm_sync_call, EMERGENT_LLM_KEY, session_id, STRATEGIIA_SYSTEM_PROMPT, user_msg, "anthropic", "claude-sonnet-4-5-20250929"
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
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=503, detail="Service IA non disponible")
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
        await db.premium_analyses.insert_one({"id": str(uuid.uuid4()), "type": "strategiia", "email": email, "context": analysis_context[:500], "status": "en_attente", "premium_pdf": premium_pdf, "analyse_premium": True, "relecture_expert_required": True, "amount": amount, "created_at": datetime.now(timezone.utc).isoformat()})
        asyncio.create_task(notify_admin_premium_analysis("strategiia", email, "", amount, options={"analyse_premium": True, "premium_pdf": premium_pdf, "context": analysis_context[:300]}))
    try:
        session = await stripe_checkout.create_checkout_session(checkout_request)
        return {"url": session.url, "session_id": session.session_id}
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
    if not situation.strip() or not EMERGENT_LLM_KEY:
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
    return {"job_id": job_id, "status": "pending", "admin_test": True, "premium_pdf": premium_pdf, "analyse_premium": analyse_premium}


@router.post("/dossier-express/admin-bypass")
async def dossier_express_admin_bypass(request: Request):
    """Admin bypass: process Dossier Express without Stripe payment."""
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
    email = payload.get("email", "admin@test")
    name = body.get("name", "Admin Test")
    situation = body.get("situation", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    documents_text = body.get("documents_text", "")
    premium_pdf = body.get("premium_pdf", False)
    if not situation.strip():
        raise HTTPException(status_code=400, detail="Description requise")
    dossier_id = str(uuid.uuid4())
    dossier_doc = {
        "id": dossier_id, "email": email, "name": name, "situation": situation[:5000],
        "type_dossier": type_dossier, "regime": regime,
        "documents_text": documents_text[:10000], "premium_pdf": premium_pdf,
        "status": "processing", "payment_verified": True, "admin_test": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.dossier_express.insert_one(dossier_doc)
    asyncio.create_task(_process_dossier_express(dossier_id, email, name, situation, type_dossier, regime, documents_text, premium_pdf=premium_pdf))
    return {"success": True, "dossier_id": dossier_id, "admin_test": True}

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
