from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import Response
from datetime import datetime, timezone
import uuid
import base64
import logging

from config import db, DOCUMENT_CATEGORIES, DOCUMENT_STATUSES
from models import ClientUser, ClientRegister, ClientLogin, ClientCase
from utils.auth import hash_password, verify_password, create_client_token, get_current_client

logger = logging.getLogger(__name__)
router = APIRouter()

STORAGE_AVAILABLE = False
try:
    from utils.storage import upload_file, download_file, init_storage
    STORAGE_AVAILABLE = True
except Exception:
    pass


# ==================== CLIENT AUTH ====================

@router.post("/client/register")
async def register_client(data: ClientRegister):
    existing = await db.client_users.find_one({"email": data.email.lower()}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cet email")
    client = ClientUser(email=data.email.lower(), password_hash=hash_password(data.password), name=data.name, phone=data.phone, notifications_email=data.notifications_email, notifications_push=data.notifications_push)
    doc = client.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.client_users.insert_one(doc)
    token = create_client_token(client.id, client.email, client.name)
    return {"access_token": token, "token_type": "bearer", "client_name": client.name, "client_id": client.id}

@router.post("/client/login")
async def login_client(data: ClientLogin):
    client = await db.client_users.find_one({"email": data.email.lower()}, {"_id": 0})
    if not client or not verify_password(data.password, client["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    token = create_client_token(client["id"], client["email"], client["name"])
    return {"access_token": token, "token_type": "bearer", "client_name": client["name"], "client_id": client["id"]}


# ==================== CLIENT PROFILE ====================

@router.get("/client/profile")
async def get_client_profile(client: dict = Depends(get_current_client)):
    user = await db.client_users.find_one({"id": client["sub"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return user


# ==================== PROGRESS ====================

# Essential documents by case type
ESSENTIAL_DOCS = {
    "at": [
        {"key": "cmi", "label": "Certificat médical initial (CMI)", "category": "medical"},
        {"key": "declaration_at", "label": "Déclaration d'accident du travail", "category": "administratif"},
        {"key": "arret_travail", "label": "Arrêt de travail", "category": "medical"},
        {"key": "notification_cpam", "label": "Notification CPAM", "category": "administratif"},
        {"key": "bulletin_salaire", "label": "Bulletins de salaire", "category": "administratif"},
    ],
    "mp": [
        {"key": "cmi", "label": "Certificat médical initial (CMI)", "category": "medical"},
        {"key": "declaration_mp", "label": "Déclaration de maladie professionnelle", "category": "administratif"},
        {"key": "attestation_exposition", "label": "Attestation d'exposition", "category": "administratif"},
        {"key": "notification_cpam", "label": "Notification CPAM", "category": "administratif"},
        {"key": "examens_medicaux", "label": "Examens médicaux / bilans", "category": "medical"},
        {"key": "fiche_poste", "label": "Fiche de poste", "category": "administratif"},
    ],
    "mdph": [
        {"key": "cerfa", "label": "Formulaire Cerfa MDPH", "category": "administratif"},
        {"key": "certificat_medical", "label": "Certificat médical récent", "category": "medical"},
        {"key": "justificatif_identite", "label": "Justificatif d'identité", "category": "administratif"},
        {"key": "justificatif_domicile", "label": "Justificatif de domicile", "category": "administratif"},
        {"key": "bilans_medicaux", "label": "Bilans médicaux et comptes rendus", "category": "medical"},
    ],
    "assurance": [
        {"key": "contrat", "label": "Contrat d'assurance", "category": "administratif"},
        {"key": "declaration_sinistre", "label": "Déclaration de sinistre", "category": "administratif"},
        {"key": "courriers_assureur", "label": "Courriers de l'assureur", "category": "administratif"},
        {"key": "certificat_medical", "label": "Certificat médical", "category": "medical"},
        {"key": "expertise", "label": "Rapport d'expertise", "category": "medical"},
    ],
    "expertise": [
        {"key": "convocation", "label": "Convocation à l'expertise", "category": "administratif"},
        {"key": "certificat_medical", "label": "Certificats médicaux", "category": "medical"},
        {"key": "historique_medical", "label": "Historique médical complet", "category": "medical"},
        {"key": "notification_taux", "label": "Notification de taux IPP", "category": "administratif"},
    ],
}
ESSENTIAL_DOCS["faute_inex"] = ESSENTIAL_DOCS["at"] + [{"key": "preuve_faute", "label": "Preuves de la faute de l'employeur", "category": "administratif"}]
ESSENTIAL_DOCS["recours"] = [
    {"key": "decision_contestee", "label": "Décision contestée", "category": "administratif"},
    {"key": "courrier_recours", "label": "Courrier de recours", "category": "administratif"},
    {"key": "certificat_medical", "label": "Certificat médical", "category": "medical"},
    {"key": "pieces_justificatives", "label": "Pièces justificatives", "category": "administratif"},
]

def _match_doc_to_essential(doc_categories: list, essential_key: str, essential_category: str) -> bool:
    """Heuristic matching: does any uploaded doc category match this essential doc?"""
    key_lower = essential_key.lower()
    for cat in doc_categories:
        cat_lower = cat.lower() if cat else ""
        if key_lower in cat_lower or cat_lower in key_lower:
            return True
        if essential_category == "medical" and cat_lower in ("medical", "médical", "certificat", "examen", "bilan", "expertise"):
            return True
        if essential_category == "administratif" and cat_lower in ("administratif", "notification", "déclaration", "courrier", "justificatif", "cerfa", "contrat"):
            return True
    return False

@router.get("/client/progress")
async def get_client_progress(client: dict = Depends(get_current_client)):
    cid = client["sub"]
    email = client.get("email", "")

    registration = {"id": "inscription", "label": "Inscription", "status": "completed", "detail": "Compte créé"}

    docs = await db.client_documents.find({"client_id": cid}, {"_id": 0, "status": 1, "category": 1, "name": 1}).to_list(500)
    total_docs = len(docs)
    validated_docs = sum(1 for d in docs if d.get("status") == "valide")
    pending_docs = sum(1 for d in docs if d.get("status") == "en_attente")
    illisible_docs = sum(1 for d in docs if d.get("status") == "illisible")
    min_required = 3

    # Document status breakdown
    document_status = {
        "total": total_docs,
        "valide": validated_docs,
        "en_attente": pending_docs,
        "illisible": illisible_docs,
    }

    # Detect case type from analyses or docs
    case_type = None
    latest_analysis = await db.strategiia_analyses.find_one({"email": email}, {"_id": 0, "type_dossier": 1}, sort=[("created_at", -1)])
    if latest_analysis:
        case_type = latest_analysis.get("type_dossier")
    if not case_type:
        latest_dossier = await db.dossier_express.find_one({"email": email}, {"_id": 0, "type_dossier": 1}, sort=[("created_at", -1)])
        if latest_dossier:
            case_type = latest_dossier.get("type_dossier")

    # Missing essential documents
    doc_categories = [d.get("category", "") for d in docs] + [d.get("name", "") for d in docs]
    essential_list = ESSENTIAL_DOCS.get(case_type, ESSENTIAL_DOCS.get("at", []))
    missing_docs = []
    found_count = 0
    for ed in essential_list:
        if _match_doc_to_essential(doc_categories, ed["key"], ed["category"]):
            found_count += 1
        else:
            missing_docs.append({"key": ed["key"], "label": ed["label"], "category": ed["category"]})

    completeness_pct = round((found_count / len(essential_list)) * 100) if essential_list else 100

    if total_docs == 0:
        doc_step = {"id": "documents", "label": "Documents collectés", "status": "not_started", "detail": f"Aucun document — {min_required} recommandés", "count": 0, "required": min_required}
    elif illisible_docs > 0:
        doc_step = {"id": "documents", "label": "Documents collectés", "status": "action_required", "detail": f"{total_docs} uploadés, {illisible_docs} illisible(s) à renvoyer", "count": total_docs, "required": min_required}
    elif validated_docs >= min_required:
        doc_step = {"id": "documents", "label": "Documents collectés", "status": "completed", "detail": f"{validated_docs}/{total_docs} validés", "count": total_docs, "required": min_required}
    else:
        doc_step = {"id": "documents", "label": "Documents collectés", "status": "in_progress", "detail": f"{total_docs} uploadés ({validated_docs} validés)", "count": total_docs, "required": min_required}

    strat_analyses = await db.strategiia_analyses.count_documents({"email": email})
    if strat_analyses > 0:
        strat_step = {"id": "strategiia", "label": "Analyse StratégiIA", "status": "completed", "detail": f"{strat_analyses} analyse(s) réalisée(s)"}
    elif total_docs >= 1:
        strat_step = {"id": "strategiia", "label": "Analyse StratégiIA", "status": "action_required", "detail": "Documents prêts — lancez votre analyse IA"}
    else:
        strat_step = {"id": "strategiia", "label": "Analyse StratégiIA", "status": "not_started", "detail": "Uploadez vos documents puis lancez l'analyse"}

    dossiers = await db.dossier_express.count_documents({"email": email})
    if dossiers > 0:
        dossier_step = {"id": "dossier_express", "label": "Dossier Express", "status": "completed", "detail": f"{dossiers} dossier(s) traité(s)"}
    else:
        dossier_step = {"id": "dossier_express", "label": "Dossier Express", "status": "not_started", "detail": "Analyse approfondie de votre dossier par IA"}

    premiums = await db.premium_analyses.find({"email": email}, {"_id": 0, "status": 1, "type": 1}).to_list(20)
    premium_done = sum(1 for p in premiums if p.get("status") == "termine")
    premium_pending = sum(1 for p in premiums if p.get("status") in ("en_attente", "en_cours"))
    if premium_done > 0:
        premium_step = {"id": "analyse_premium", "label": "Analyse Premium Expert", "status": "completed", "detail": f"{premium_done} analyse(s) finalisée(s)"}
    elif premium_pending > 0:
        premium_step = {"id": "analyse_premium", "label": "Analyse Premium Expert", "status": "in_progress", "detail": f"{premium_pending} en cours de traitement par l'expert"}
    else:
        premium_step = {"id": "analyse_premium", "label": "Analyse Premium Expert", "status": "not_started", "detail": "Relecture et enrichissement par un expert humain"}

    cases = await db.client_cases.find({"client_id": cid}, {"_id": 0, "status": 1}).to_list(50)
    completed_cases = sum(1 for c in cases if c.get("status") == "termine")
    if completed_cases > 0:
        final_step = {"id": "finalisation", "label": "Dossier finalisé", "status": "completed", "detail": f"{completed_cases} dossier(s) clôturé(s)"}
    elif premium_done > 0 or dossiers > 0:
        final_step = {"id": "finalisation", "label": "Dossier finalisé", "status": "in_progress", "detail": "Suivi en cours — résultats bientôt disponibles"}
    else:
        final_step = {"id": "finalisation", "label": "Dossier finalisé", "status": "not_started", "detail": "Dernière étape après analyse et relecture"}

    steps = [registration, doc_step, strat_step, dossier_step, premium_step, final_step]
    weights = {"completed": 1.0, "in_progress": 0.5, "action_required": 0.3, "not_started": 0}
    total_weight = sum(weights.get(s["status"], 0) for s in steps)
    progress_pct = round((total_weight / len(steps)) * 100)

    # Build actionable next actions list
    next_actions = []
    for s in steps:
        if s["status"] in ("action_required", "not_started", "in_progress"):
            action = {"step_id": s["id"], "label": s["label"], "detail": s["detail"], "status": s["status"]}
            if s["id"] == "documents" and missing_docs:
                action["cta"] = "Ajouter un document"
                action["cta_link"] = "/espace-client?tab=documents"
            elif s["id"] == "strategiia":
                action["cta"] = "Lancer l'analyse"
                action["cta_link"] = "/espace-client"
            elif s["id"] == "dossier_express":
                action["cta"] = "Commander"
                action["cta_link"] = "/dossier-express"
            next_actions.append(action)
            if len(next_actions) >= 3:
                break

    next_action = next_actions[0] if next_actions else None

    counts = {"completed": 0, "in_progress": 0, "action_required": 0, "not_started": 0}
    for s in steps:
        counts[s["status"]] = counts.get(s["status"], 0) + 1

    return {
        "progress_pct": progress_pct,
        "steps": steps,
        "next_action": next_action,
        "next_actions": next_actions,
        "counts": counts,
        "document_status": document_status,
        "missing_documents": missing_docs,
        "completeness_pct": completeness_pct,
        "case_type": case_type,
        "summary": {"total_documents": total_docs, "validated_documents": validated_docs, "analyses_ia": strat_analyses, "dossiers_express": dossiers, "analyses_premium": len(premiums)},
    }



# ==================== DOSSIER ANALYSIS (StratégiIA Phase 1) ====================

# Risk alerts by case type — specific, actionable warnings
RISK_ALERTS = {
    "at": [
        {"key": "cmi", "condition": "missing", "severity": "critical",
         "message": "Sans certificat médical initial (CMI), la CPAM peut rejeter votre demande de prise en charge. Ce document est la pierre angulaire de votre dossier.",
         "action": "Consultez votre médecin traitant pour obtenir un CMI décrivant précisément les lésions et leur lien avec l'accident."},
        {"key": "declaration_at", "condition": "missing", "severity": "critical",
         "message": "L'absence de déclaration d'accident du travail peut être utilisée pour contester la matérialité de l'accident. Le délai légal est de 48h.",
         "action": "Vérifiez que votre employeur a bien effectué la déclaration. À défaut, vous pouvez la faire vous-même auprès de la CPAM."},
        {"key": "notification_cpam", "condition": "missing", "severity": "warning",
         "message": "Sans notification CPAM, il est impossible de connaître la décision prise sur votre dossier et les voies de recours disponibles.",
         "action": "Contactez votre CPAM pour obtenir la notification de décision si vous ne l'avez pas reçue."},
    ],
    "mp": [
        {"key": "cmi", "condition": "missing", "severity": "critical",
         "message": "Le certificat médical initial est indispensable pour établir le lien entre votre pathologie et votre activité professionnelle.",
         "action": "Faites établir un CMI par votre médecin mentionnant explicitement le lien avec votre activité professionnelle."},
        {"key": "attestation_exposition", "condition": "missing", "severity": "critical",
         "message": "L'attestation d'exposition est un élément clé. Son absence fragilise considérablement la reconnaissance de la maladie professionnelle, surtout hors tableau.",
         "action": "Demandez à votre employeur ou médecin du travail une attestation d'exposition aux risques professionnels."},
        {"key": "fiche_poste", "condition": "missing", "severity": "warning",
         "message": "La fiche de poste permet de démontrer l'exposition aux risques. Sans elle, le CRRMP peut avoir des difficultés à établir le lien causal.",
         "action": "Récupérez votre fiche de poste auprès de votre employeur ou des ressources humaines."},
    ],
    "mdph": [
        {"key": "cerfa", "condition": "missing", "severity": "critical",
         "message": "Le formulaire Cerfa est obligatoire pour toute demande MDPH. Sans lui, votre dossier ne peut pas être instruit.",
         "action": "Téléchargez le formulaire Cerfa n°15692*01 sur le site service-public.fr ou retirez-le à votre MDPH."},
        {"key": "certificat_medical", "condition": "missing", "severity": "critical",
         "message": "Le certificat médical MDPH (Cerfa n°15695*01) est obligatoire. Il doit être rempli par votre médecin et dater de moins de 6 mois.",
         "action": "Prenez rendez-vous avec votre médecin pour remplir le certificat médical MDPH."},
    ],
    "assurance": [
        {"key": "contrat", "condition": "missing", "severity": "critical",
         "message": "Sans votre contrat d'assurance, il est impossible de vérifier les garanties souscrites et les exclusions applicables.",
         "action": "Demandez une copie de votre contrat à votre assureur ou courtier."},
        {"key": "declaration_sinistre", "condition": "missing", "severity": "critical",
         "message": "La déclaration de sinistre doit être faite dans les délais contractuels (généralement 5 jours). Un retard peut justifier un refus de prise en charge.",
         "action": "Effectuez votre déclaration de sinistre par lettre recommandée avec AR dès que possible."},
    ],
    "expertise": [
        {"key": "convocation", "condition": "missing", "severity": "warning",
         "message": "La convocation à l'expertise contient des informations essentielles sur le médecin expert et les modalités de l'examen.",
         "action": "Vérifiez vos courriers ou contactez l'organisme qui a ordonné l'expertise."},
        {"key": "historique_medical", "condition": "missing", "severity": "critical",
         "message": "Un historique médical incomplet peut conduire à une sous-évaluation de votre taux d'IPP. L'expert se base sur les documents fournis.",
         "action": "Rassemblez tous vos comptes rendus médicaux, imageries et prescriptions depuis l'accident/maladie."},
    ],
    "faute_inex": [
        {"key": "preuve_faute", "condition": "missing", "severity": "critical",
         "message": "La reconnaissance de la faute inexcusable repose sur la preuve que l'employeur avait conscience du danger et n'a pas pris les mesures nécessaires.",
         "action": "Rassemblez tout élément prouvant la connaissance du risque par l'employeur : alertes CHSCT/CSE, courriers, témoignages, PV d'inspection."},
    ],
    "recours": [
        {"key": "decision_contestee", "condition": "missing", "severity": "critical",
         "message": "La décision contestée est indispensable pour identifier les motifs de refus et construire votre argumentation.",
         "action": "Retrouvez la notification de décision ou demandez-en une copie à l'organisme concerné."},
        {"key": "courrier_recours", "condition": "missing", "severity": "warning",
         "message": "Le courrier de recours doit être envoyé dans les délais légaux (2 mois pour la CRA, 2 mois pour le tribunal). Un dépassement peut rendre le recours irrecevable.",
         "action": "Rédigez votre courrier de recours en mentionnant les références de la décision et vos arguments."},
    ],
}

# Dynamic messages based on score thresholds
def _get_dynamic_message(score: int, case_type: str) -> dict:
    if score < 30:
        return {
            "title": "Votre dossier nécessite une attention immédiate",
            "message": "Plusieurs éléments essentiels sont manquants. Sans action rapide, votre dossier risque d'être rejeté ou considérablement affaibli.",
            "tone": "urgent",
            "color": "red"
        }
    elif score < 50:
        return {
            "title": "Votre dossier est en cours de structuration",
            "message": "Les bases sont posées mais des documents clés manquent encore. Concentrez-vous sur les éléments critiques identifiés ci-dessous.",
            "tone": "attention",
            "color": "orange"
        }
    elif score < 70:
        return {
            "title": "Votre dossier progresse bien",
            "message": "Vous êtes sur la bonne voie. Quelques éléments supplémentaires permettront de consolider significativement votre position.",
            "tone": "encouraging",
            "color": "amber"
        }
    elif score < 85:
        return {
            "title": "Votre dossier est solide",
            "message": "La majorité des éléments essentiels sont réunis. Les derniers ajustements renforceront encore votre dossier pour un résultat optimal.",
            "tone": "positive",
            "color": "blue"
        }
    else:
        return {
            "title": "Votre dossier atteint un niveau expert",
            "message": "Votre dossier est particulièrement bien constitué. Vous disposez d'un socle solide pour faire valoir vos droits.",
            "tone": "excellent",
            "color": "green"
        }


@router.get("/client/dossier-analysis")
async def get_dossier_analysis(client: dict = Depends(get_current_client)):
    """Comprehensive dossier analysis: score, weak points, risk alerts, dynamic messages.
    Full data only for clients with a completed Dossier Express."""
    cid = client["sub"]
    email = client.get("email", "")

    # Check if client has a completed Dossier Express (paid service)
    dossier_express_entry = await db.dossier_express.find_one(
        {"email": email, "status": "completed"},
        {"_id": 0, "id": 1}
    )
    has_dossier_express = dossier_express_entry is not None

    # 1. Fetch all client data
    docs = await db.client_documents.find(
        {"client_id": cid},
        {"_id": 0, "status": 1, "category": 1, "filename": 1, "tags": 1, "created_at": 1}
    ).to_list(500)

    total_docs = len(docs)
    validated = sum(1 for d in docs if d.get("status") == "valide")
    pending = sum(1 for d in docs if d.get("status") == "en_attente")
    illisible = sum(1 for d in docs if d.get("status") == "illisible")

    # Detect case type
    case_type = None
    latest_analysis = await db.strategiia_analyses.find_one(
        {"email": email}, {"_id": 0, "type_dossier": 1}, sort=[("created_at", -1)]
    )
    if latest_analysis:
        case_type = latest_analysis.get("type_dossier")
    if not case_type:
        latest_dossier = await db.dossier_express.find_one(
            {"email": email}, {"_id": 0, "type_dossier": 1}, sort=[("created_at", -1)]
        )
        if latest_dossier:
            case_type = latest_dossier.get("type_dossier")

    essential_list = ESSENTIAL_DOCS.get(case_type, ESSENTIAL_DOCS.get("at", []))

    # 2. Document completeness analysis
    doc_categories = [d.get("category", "") for d in docs] + [d.get("filename", "") for d in docs]
    found_docs = []
    missing_docs = []
    for ed in essential_list:
        if _match_doc_to_essential(doc_categories, ed["key"], ed["category"]):
            found_docs.append(ed)
        else:
            missing_docs.append(ed)

    completeness_score = round((len(found_docs) / len(essential_list)) * 100) if essential_list else 100

    # 3. Document quality score
    if total_docs == 0:
        quality_score = 0
    else:
        quality_score = round(((validated * 1.0 + pending * 0.5) / total_docs) * 100)

    # 4. StrategiIA analysis richness
    strat_count = await db.strategiia_analyses.count_documents({"email": email})
    dossier_count = await db.dossier_express.count_documents({"email": email})
    premium_count = await db.premium_analyses.count_documents({"email": email})

    analysis_score = min(100, strat_count * 25 + dossier_count * 40 + premium_count * 35)

    # 3b. Cohérence score — alignment between docs, case type, and analyses
    coherence_parts = []
    if case_type and total_docs > 0:
        matching_cats = sum(1 for d in docs if d.get("category", "") == case_type or d.get("tags", {}).get("type_document") == case_type)
        cat_ratio = min(1.0, matching_cats / max(1, total_docs) + 0.3) if total_docs > 0 else 0
        coherence_parts.append(cat_ratio * 40)
        coherence_parts.append(30 if strat_count > 0 else 0)
        coherence_parts.append((len(found_docs) / max(1, len(essential_list))) * 30)
    elif total_docs > 0:
        coherence_parts.append(20)
        coherence_parts.append(15 if strat_count > 0 else 0)
    coherence_score = min(100, round(sum(coherence_parts))) if coherence_parts else 0

    # 5. Overall progress (steps)
    cases = await db.client_cases.find({"client_id": cid}, {"_id": 0, "status": 1}).to_list(50)
    completed_cases = sum(1 for c in cases if c.get("status") == "termine")
    progress_score = min(100, 20 + completed_cases * 30 + (30 if strat_count > 0 else 0) + (30 if total_docs >= 3 else total_docs * 10))

    # 6. Composite score: Solidité du dossier
    composite = round(
        completeness_score * 0.40 +
        quality_score * 0.20 +
        analysis_score * 0.15 +
        progress_score * 0.15 +
        min(100, total_docs * 15) * 0.10  # raw document count bonus
    )
    composite = min(100, max(0, composite))

    # 7. Weak points detection
    weak_points = []
    if completeness_score < 60:
        weak_points.append({
            "id": "low_completeness",
            "severity": "critical",
            "title": "Documents essentiels manquants",
            "detail": f"Seulement {len(found_docs)}/{len(essential_list)} documents essentiels sont présents dans votre dossier.",
            "impact": "Cela réduit significativement vos chances de succès."
        })
    if illisible > 0:
        weak_points.append({
            "id": "illisible_docs",
            "severity": "critical",
            "title": f"{illisible} document(s) illisible(s)",
            "detail": "Des documents illisibles ne peuvent pas être pris en compte dans l'analyse de votre dossier.",
            "impact": "Renvoyez une version lisible pour éviter tout rejet."
        })
    if total_docs > 0 and validated == 0:
        weak_points.append({
            "id": "no_validated",
            "severity": "warning",
            "title": "Aucun document validé",
            "detail": "Tous vos documents sont en attente de validation.",
            "impact": "La validation permet de s'assurer que les documents sont exploitables."
        })
    if strat_count == 0 and total_docs >= 1:
        weak_points.append({
            "id": "no_analysis",
            "severity": "info",
            "title": "Aucune analyse IA réalisée",
            "detail": "Lancez une analyse StratégiIA pour obtenir une évaluation stratégique de votre situation.",
            "impact": "L'analyse permet d'identifier les forces et faiblesses de votre dossier."
        })
    if total_docs == 0:
        weak_points.append({
            "id": "no_documents",
            "severity": "critical",
            "title": "Aucun document déposé",
            "detail": "Votre dossier ne contient aucun document. Sans pièces justificatives, aucune démarche ne peut aboutir.",
            "impact": "Commencez par déposer vos documents les plus importants."
        })

    # 8. Risk alerts — case-type specific
    risk_alerts = []
    case_risks = RISK_ALERTS.get(case_type, RISK_ALERTS.get("at", []))
    missing_keys = {d["key"] for d in missing_docs}
    for risk in case_risks:
        if risk["condition"] == "missing" and risk["key"] in missing_keys:
            risk_alerts.append({
                "severity": risk["severity"],
                "message": risk["message"],
                "action": risk["action"]
            })

    # Add quality-based risk alerts
    if illisible > 0:
        risk_alerts.append({
            "severity": "warning",
            "message": f"{illisible} document(s) marqué(s) comme illisible(s). Ces documents ne seront pas pris en compte lors de l'examen de votre dossier.",
            "action": "Renumérisez les documents concernés avec une meilleure résolution et renvoyez-les."
        })

    # 9. Dynamic message
    dynamic_message = _get_dynamic_message(composite, case_type)

    # 10. Actionable count
    actionable_count = len(missing_docs) + illisible + (1 if strat_count == 0 and total_docs >= 1 else 0)

    # 11. Score breakdown for UI
    score_breakdown = {
        "completeness": {"score": completeness_score, "label": "Complétude documentaire", "weight": 40, "found": len(found_docs), "total": len(essential_list)},
        "quality": {"score": quality_score, "label": "Qualité des documents", "weight": 20, "validated": validated, "pending": pending, "illisible": illisible},
        "coherence": {"score": coherence_score, "label": "Cohérence du dossier", "weight": 0},
        "analysis": {"score": analysis_score, "label": "Analyses réalisées", "weight": 15, "strategiia": strat_count, "dossier_express": dossier_count, "premium": premium_count},
        "progress": {"score": progress_score, "label": "Progression globale", "weight": 15},
        "volume": {"score": min(100, total_docs * 15), "label": "Volume de pièces", "weight": 10, "count": total_docs},
    }

    # Top-level key metrics visible without expanding
    key_metrics = {
        "completeness": completeness_score,
        "quality": quality_score,
        "coherence": coherence_score,
    }

    # 12. Recommended actions — Phase 2: prioritized, clickable CTAs (max 3)
    all_actions = []
    priority = 1
    if total_docs == 0:
        all_actions.append({
            "priority": priority, "priority_level": "haute", "action_id": "upload_first_doc",
            "title": "Déposez votre premier document",
            "description": "Commencez par les pièces les plus importantes de votre dossier.",
            "impact": "+15% sur votre score", "cta_label": "Déposer un document",
            "cta_target": "documents", "icon": "upload",
            "estimated_score_gain": 15
        })
        priority += 1
    elif len(missing_docs) > 0:
        top_missing = missing_docs[0]
        all_actions.append({
            "priority": priority, "priority_level": "haute", "action_id": f"upload_{top_missing['key']}",
            "title": f"Ajoutez : {top_missing['label']}",
            "description": f"Ce document est essentiel pour votre dossier {case_type or 'AT'}. Sans lui, votre demande risque d'être fragilisée.",
            "impact": f"+{max(5, round(40 / len(essential_list)))}% sur votre score",
            "cta_label": "Ajouter ce document", "cta_target": "documents", "icon": "file",
            "estimated_score_gain": max(5, round(40 / len(essential_list)))
        })
        priority += 1

    if illisible > 0:
        all_actions.append({
            "priority": priority, "priority_level": "haute", "action_id": "fix_illisible",
            "title": f"Corrigez {illisible} document(s) illisible(s)",
            "description": "Des documents illisibles ne sont pas pris en compte. Renumérisez-les en meilleure qualité.",
            "impact": f"+{min(10, illisible * 5)}% sur votre score",
            "cta_label": "Voir les documents", "cta_target": "documents", "icon": "scan",
            "estimated_score_gain": min(10, illisible * 5)
        })
        priority += 1

    if strat_count == 0:
        all_actions.append({
            "priority": priority, "priority_level": "moyenne", "action_id": "launch_strategiia",
            "title": "Lancez une analyse StratégiIA",
            "description": "L'IA analysera votre situation et identifiera les forces et faiblesses de votre dossier.",
            "impact": "+25% sur votre score", "cta_label": "Lancer l'analyse",
            "cta_target": "strategiia", "icon": "brain",
            "estimated_score_gain": 25
        })
        priority += 1

    if dossier_count == 0 and strat_count > 0:
        all_actions.append({
            "priority": priority, "priority_level": "faible", "action_id": "dossier_express",
            "title": "Complétez un Dossier Express",
            "description": "Un dossier express consolide votre analyse et facilite le suivi de votre parcours.",
            "impact": "+15% sur votre score", "cta_label": "Créer un dossier express",
            "cta_target": "strategiia", "icon": "zap",
            "estimated_score_gain": 15
        })
        priority += 1

    if len(missing_docs) > 1:
        remaining = missing_docs[1:min(4, len(missing_docs))]
        for md in remaining:
            all_actions.append({
                "priority": priority, "priority_level": "faible", "action_id": f"upload_{md['key']}",
                "title": f"Ajoutez : {md['label']}",
                "description": "Document important pour renforcer votre dossier.",
                "impact": f"+{max(3, round(40 / len(essential_list)))}% estimé",
                "cta_label": "Ajouter", "cta_target": "documents", "icon": "file",
                "estimated_score_gain": max(3, round(40 / len(essential_list)))
            })
            priority += 1

    # Limit to top 3 actions only
    recommended_actions = all_actions[:3]

    # 13. Predictive refusal logic — Phase 3
    predictions = []
    REFUSAL_PATTERNS = {
        "at": [
            {"condition": "no_cmi", "check": "cmi" in missing_keys,
             "title": "Risque de contestation de la matérialité",
             "detail": "Sans certificat médical initial, la CPAM pourrait contester la réalité de l'accident en invoquant l'absence de preuve médicale contemporaine des faits.",
             "probability": "Élevée", "consequence": "Rejet de la prise en charge ou contestation lors de la phase amiable."},
            {"condition": "no_declaration", "check": "declaration_at" in missing_keys,
             "title": "Risque de forclusion pour déclaration tardive",
             "detail": "La déclaration d'AT doit être faite dans les 48h. Un retard important peut être invoqué pour remettre en cause le lien avec le travail.",
             "probability": "Moyenne", "consequence": "L'employeur ou la CPAM peut argumenter que le délai prouve l'absence de lien professionnel."},
        ],
        "mp": [
            {"condition": "no_attestation", "check": "attestation_exposition" in missing_keys,
             "title": "Risque de refus pour défaut de preuve d'exposition",
             "detail": "Le CRRMP exige des preuves d'exposition professionnelle. Sans attestation, la reconnaissance hors tableau devient très difficile.",
             "probability": "Élevée", "consequence": "Refus de reconnaissance de la maladie professionnelle par le CRRMP."},
            {"condition": "no_fiche_poste", "check": "fiche_poste" in missing_keys,
             "title": "Risque de sous-évaluation du lien causal",
             "detail": "Sans description précise du poste, le médecin conseil peut minimiser l'exposition aux risques professionnels.",
             "probability": "Moyenne", "consequence": "Taux d'IPP inférieur à la réalité ou refus de reconnaissance."},
        ],
        "mdph": [
            {"condition": "no_cerfa", "check": "cerfa" in missing_keys,
             "title": "Irrecevabilité de la demande",
             "detail": "Le formulaire Cerfa est une condition de recevabilité. Sans lui, la MDPH ne peut pas instruire votre demande.",
             "probability": "Certaine", "consequence": "Retour du dossier sans instruction. Perte de temps de plusieurs mois."},
        ],
        "assurance": [
            {"condition": "no_contrat", "check": "contrat" in missing_keys,
             "title": "Application d'exclusions non vérifiées",
             "detail": "Sans le contrat, il est impossible de vérifier si l'assureur applique correctement les garanties et exclusions.",
             "probability": "Moyenne", "consequence": "Refus de prise en charge basé sur des exclusions potentiellement inapplicables."},
        ],
        "expertise": [
            {"condition": "no_historique", "check": "historique_medical" in missing_keys,
             "title": "Sous-évaluation du taux d'IPP",
             "detail": "L'expert médical se fonde sur les documents présentés. Un dossier médical incomplet mène systématiquement à une évaluation inférieure.",
             "probability": "Élevée", "consequence": "Taux d'IPP et indemnisation inférieurs à ce que votre état justifie."},
        ],
        "recours": [
            {"condition": "no_decision", "check": "decision_contestee" in missing_keys,
             "title": "Recours mal fondé ou irrecevable",
             "detail": "Sans la décision contestée, il est impossible de construire une argumentation juridique ciblée et pertinente.",
             "probability": "Élevée", "consequence": "Rejet du recours pour défaut de motivation ou irrecevabilité."},
        ],
    }
    case_predictions = REFUSAL_PATTERNS.get(case_type, REFUSAL_PATTERNS.get("at", []))
    for pred in case_predictions:
        if pred["check"]:
            predictions.append({
                "title": pred["title"],
                "detail": pred["detail"],
                "probability": pred["probability"],
                "consequence": pred["consequence"],
            })

    # 14. Premium CTA — Phase 3
    premium_cta = {
        "show": composite < 85 and premium_count == 0,
        "title": "Analyse Expert Personnalisée",
        "subtitle": "Faites examiner votre dossier par un expert en droit social",
        "features": [
            "Audit complet de votre dossier par un spécialiste",
            "Identification des points forts et axes d'amélioration",
            "Recommandations personnalisées et stratégie sur mesure",
            "Rapport détaillé avec plan d'action concret",
        ],
        "cta_label": "Demander une analyse expert",
        "score_context": f"Votre dossier est à {composite}%. Un expert peut vous aider à atteindre un niveau optimal.",
    }

    # If client has no Dossier Express, return limited data with upsell
    if not has_dossier_express:
        return {
            "has_dossier_express": False,
            "score": composite,
            "dynamic_message": dynamic_message,
            "actionable_count": actionable_count,
            "case_type": case_type,
            "summary": {
                "total_documents": total_docs,
                "validated": validated,
                "pending": pending,
                "illisible": illisible,
                "analyses_ia": strat_count,
                "dossier_express": dossier_count,
                "premium": premium_count,
            },
        }

    # Full data for Dossier Express clients
    return {
        "has_dossier_express": True,
        "score": composite,
        "key_metrics": key_metrics,
        "dynamic_message": dynamic_message,
        "score_breakdown": score_breakdown,
        "weak_points": weak_points,
        "risk_alerts": risk_alerts,
        "missing_documents": [{"key": d["key"], "label": d["label"], "category": d["category"]} for d in missing_docs],
        "found_documents": [{"key": d["key"], "label": d["label"], "category": d["category"]} for d in found_docs],
        "actionable_count": actionable_count,
        "case_type": case_type,
        "recommended_actions": recommended_actions,
        "predictions": predictions,
        "premium_cta": premium_cta,
        "summary": {
            "total_documents": total_docs,
            "validated": validated,
            "pending": pending,
            "illisible": illisible,
            "analyses_ia": strat_count,
            "dossier_express": dossier_count,
            "premium": premium_count,
        },
    }


# ==================== CASES ====================

@router.get("/client/cases")
async def get_client_cases(client: dict = Depends(get_current_client)):
    cases = await db.client_cases.find({"client_id": client["sub"]}, {"_id": 0}).sort("updated_at", -1).to_list(100)
    return cases

@router.get("/client/cases/{case_id}")
async def get_client_case(case_id: str, client: dict = Depends(get_current_client)):
    case = await db.client_cases.find_one({"id": case_id, "client_id": client["sub"]}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    return case


# ==================== DOCUMENTS ====================

@router.post("/client/documents")
async def upload_client_document(request: Request, client: dict = Depends(get_current_client)):
    body = await request.json()
    filename = body.get("filename", "")
    file_data = body.get("file_data", "")
    mime_type = body.get("mime_type", "")
    size = body.get("size", 0)
    ocr_fields = body.get("ocr_fields", {})
    manual_tags = body.get("tags", {})

    if not filename or not file_data:
        raise HTTPException(status_code=400, detail="Fichier requis")
    if size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 10 Mo)")

    # Auto-extract with GPT-4o if no OCR fields provided and AI-extractable content exists
    ai_enhanced = False
    if not ocr_fields or not any(ocr_fields.get(k) for k in ["type_dossier_detected", "noms", "dates", "organisme"]):
        try:
            # For PDFs: extract raw text from base64 data and send to GPT-4o
            file_bytes = base64.b64decode(file_data)
            raw_text = ""
            if mime_type == "application/pdf":
                try:
                    import io
                    # Try simple text extraction from PDF
                    text_content = file_bytes.decode('latin-1', errors='ignore')
                    # Extract text between stream/endstream markers (basic PDF text)
                    import re
                    text_parts = re.findall(r'\(([^)]+)\)', text_content)
                    raw_text = ' '.join(text_parts)[:5000]
                except Exception:
                    pass
            elif mime_type and mime_type.startswith("text/"):
                raw_text = file_bytes.decode('utf-8', errors='ignore')[:5000]

            if raw_text and len(raw_text.strip()) > 20:
                from utils.ocr_gpt import extract_fields_gpt4o
                ai_result = await extract_fields_gpt4o(raw_text)
                if ai_result.get("enhanced") and ai_result.get("fields"):
                    ocr_fields = ai_result["fields"]
                    ai_enhanced = True
                    logger.info(f"Auto GPT-4o extraction for {filename}: {list(ocr_fields.keys())}")
        except Exception as e:
            logger.warning(f"Auto GPT-4o extraction failed for {filename}: {e}")

    # Use organisme from GPT-4o if available
    if ocr_fields.get("organisme") and not manual_tags.get("organisme"):
        manual_tags["organisme"] = ocr_fields["organisme"]

    category = manual_tags.get("categorie", "autre")
    if category == "autre" and ocr_fields.get("type_dossier_detected"):
        type_map = {"at": "at", "mp": "mp", "mdph": "mdph", "expertise": "expertise", "ipp": "expertise"}
        for t in ocr_fields["type_dossier_detected"]:
            if t in type_map:
                category = type_map[t]
                break

    organisme = manual_tags.get("organisme", "")
    if not organisme and ocr_fields.get("organisme"):
        organisme = ocr_fields["organisme"]
    if not organisme and ocr_fields:
        text_lower = ocr_fields.get("contexte", "").lower()
        for org in ["CPAM", "CRAMIF", "MSA", "MDPH", "CNSA", "TASS", "TCI"]:
            if org.lower() in text_lower:
                organisme = org
                break

    storage_path = None
    if STORAGE_AVAILABLE and file_data:
        try:
            file_bytes = base64.b64decode(file_data)
            result = upload_file(client["sub"], filename, file_bytes, mime_type)
            storage_path = result["storage_path"]
        except Exception as e:
            logger.warning(f"Object storage upload failed, falling back to DB: {e}")

    doc = {
        "id": str(uuid.uuid4()), "client_id": client["sub"], "filename": filename,
        "mime_type": mime_type, "size": size, "category": category,
        "storage_path": storage_path,
        "file_data": file_data if not storage_path else None,
        "tags": {"type_document": manual_tags.get("type_document", category), "date_document": manual_tags.get("date_document", ocr_fields.get("dates", [None])[0] if ocr_fields.get("dates") else None), "organisme": organisme, "noms": ocr_fields.get("noms", []), "references": ocr_fields.get("references", []), "montants": ocr_fields.get("montants", []), "numero_ss": ocr_fields.get("numero_ss"), "taux_ipp": ocr_fields.get("taux_ipp", [])},
        "ocr_fields": ocr_fields, "ai_enhanced": ai_enhanced, "status": "en_attente",
        "versions": [{"version": 1, "filename": filename, "uploaded_at": datetime.now(timezone.utc).isoformat()}],
        "created_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.client_documents.insert_one(doc)
    doc.pop("_id", None)
    doc.pop("file_data", None)

    # Check completeness and send notification if threshold reached
    try:
        from utils.email import check_and_send_completeness_notification
        all_docs = await db.client_documents.find({"client_id": client["sub"]}, {"_id": 0, "category": 1, "name": 1}).to_list(500)
        doc_categories = [d.get("category", "") for d in all_docs] + [d.get("name", "") for d in all_docs]
        email = client.get("email", "")
        # Detect case type
        ct = None
        la = await db.strategiia_analyses.find_one({"email": email}, {"_id": 0, "type_dossier": 1}, sort=[("created_at", -1)])
        if la:
            ct = la.get("type_dossier")
        if not ct:
            ld = await db.dossier_express.find_one({"email": email}, {"_id": 0, "type_dossier": 1}, sort=[("created_at", -1)])
            if ld:
                ct = ld.get("type_dossier")
        essential_list = ESSENTIAL_DOCS.get(ct, ESSENTIAL_DOCS.get("at", []))
        found_count = 0
        missing_list = []
        for ed in essential_list:
            if _match_doc_to_essential(doc_categories, ed["key"], ed["category"]):
                found_count += 1
            else:
                missing_list.append(ed)
        comp_pct = round((found_count / len(essential_list)) * 100) if essential_list else 100
        await check_and_send_completeness_notification(client["sub"], comp_pct, missing_list, ct)
    except Exception as e:
        logger.warning(f"Completeness notification check failed: {e}")

    return {"success": True, "document": doc}

@router.get("/client/documents")
async def list_client_documents(client: dict = Depends(get_current_client), category: str = None, status: str = None, organisme: str = None, search: str = None):
    query = {"client_id": client["sub"]}
    if category:
        query["category"] = category
    if status:
        query["status"] = status
    if organisme:
        query["tags.organisme"] = {"$regex": organisme, "$options": "i"}
    if search:
        query["$or"] = [{"filename": {"$regex": search, "$options": "i"}}, {"tags.organisme": {"$regex": search, "$options": "i"}}, {"tags.references": {"$elemMatch": {"$regex": search, "$options": "i"}}}]
    docs = await db.client_documents.find(query, {"_id": 0, "file_data": 0}).sort("created_at", -1).to_list(200)
    all_docs = await db.client_documents.find({"client_id": client["sub"]}, {"_id": 0, "category": 1, "status": 1}).to_list(500)
    by_category = {}
    by_status = {"en_attente": 0, "valide": 0, "illisible": 0, "corrige": 0}
    for d in all_docs:
        cat = d.get("category", "autre")
        by_category[cat] = by_category.get(cat, 0) + 1
        st = d.get("status", "en_attente")
        if st in by_status:
            by_status[st] += 1
    return {"documents": docs, "total": len(all_docs), "by_category": by_category, "by_status": by_status}

@router.get("/client/documents/{doc_id}")
async def get_client_document(doc_id: str, client: dict = Depends(get_current_client)):
    doc = await db.client_documents.find_one({"id": doc_id, "client_id": client["sub"]}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return doc

@router.get("/client/documents/{doc_id}/download")
async def download_client_document(doc_id: str, client: dict = Depends(get_current_client)):
    doc = await db.client_documents.find_one({"id": doc_id, "client_id": client["sub"]}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    if doc.get("storage_path") and STORAGE_AVAILABLE:
        try:
            data, content_type = download_file(doc["storage_path"])
            return Response(content=data, media_type=doc.get("mime_type", content_type), headers={"Content-Disposition": f'attachment; filename="{doc["filename"]}"'})
        except Exception as e:
            logger.error(f"Storage download failed: {e}")
    if doc.get("file_data"):
        file_bytes = base64.b64decode(doc["file_data"])
        return Response(content=file_bytes, media_type=doc.get("mime_type", "application/octet-stream"), headers={"Content-Disposition": f'attachment; filename="{doc["filename"]}"'})
    raise HTTPException(status_code=404, detail="Fichier non disponible")

@router.patch("/client/documents/{doc_id}")
async def update_client_document(doc_id: str, request: Request, client: dict = Depends(get_current_client)):
    body = await request.json()
    update = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if "category" in body and body["category"] in DOCUMENT_CATEGORIES:
        update["category"] = body["category"]
    if "status" in body and body["status"] in DOCUMENT_STATUSES:
        update["status"] = body["status"]
    if "tags" in body and isinstance(body["tags"], dict):
        for k, v in body["tags"].items():
            update[f"tags.{k}"] = v
    result = await db.client_documents.update_one({"id": doc_id, "client_id": client["sub"]}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return {"success": True}

@router.delete("/client/documents/{doc_id}")
async def delete_client_document(doc_id: str, client: dict = Depends(get_current_client)):
    result = await db.client_documents.delete_one({"id": doc_id, "client_id": client["sub"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return {"success": True}

@router.post("/client/documents/{doc_id}/version")
async def add_document_version(doc_id: str, request: Request, client: dict = Depends(get_current_client)):
    body = await request.json()
    filename = body.get("filename", "")
    file_data = body.get("file_data", "")
    if not filename or not file_data:
        raise HTTPException(status_code=400, detail="Fichier requis")
    doc = await db.client_documents.find_one({"id": doc_id, "client_id": client["sub"]}, {"_id": 0, "versions": 1, "mime_type": 1})
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    new_version = len(doc.get("versions", [])) + 1
    storage_path = None
    if STORAGE_AVAILABLE and file_data:
        try:
            file_bytes = base64.b64decode(file_data)
            mime_type = body.get("mime_type", doc.get("mime_type", "application/octet-stream"))
            result = upload_file(client["sub"], filename, file_bytes, mime_type)
            storage_path = result["storage_path"]
        except Exception as e:
            logger.warning(f"Object storage version upload failed: {e}")
    update_data = {
        "filename": filename,
        "status": "corrige",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if storage_path:
        update_data["storage_path"] = storage_path
        update_data["file_data"] = None
    else:
        update_data["file_data"] = file_data
    await db.client_documents.update_one(
        {"id": doc_id, "client_id": client["sub"]},
        {"$set": update_data,
         "$push": {"versions": {"version": new_version, "filename": filename, "uploaded_at": datetime.now(timezone.utc).isoformat()}}}
    )
    return {"success": True, "version": new_version}


# ==================== NOTIFICATIONS ====================

@router.get("/client/notifications")
async def get_client_notifications(client: dict = Depends(get_current_client)):
    notifs = await db.client_notifications.find({"client_id": client["sub"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
    unread = sum(1 for n in notifs if not n.get("read"))
    return {"notifications": notifs, "unread_count": unread}

@router.patch("/client/notifications/{notif_id}/read")
async def mark_notification_read(notif_id: str, client: dict = Depends(get_current_client)):
    await db.client_notifications.update_one({"id": notif_id, "client_id": client["sub"]}, {"$set": {"read": True}})
    return {"success": True}

@router.patch("/client/notifications/read-all")
async def mark_all_notifications_read(client: dict = Depends(get_current_client)):
    await db.client_notifications.update_many({"client_id": client["sub"], "read": False}, {"$set": {"read": True}})
    return {"success": True}

@router.get("/client/settings/notifications")
async def get_notification_settings(client: dict = Depends(get_current_client)):
    user = await db.client_users.find_one({"id": client["sub"]}, {"_id": 0, "notifications_email": 1, "notifications_push": 1})
    return {"notifications_email": user.get("notifications_email", True) if user else True, "notifications_push": user.get("notifications_push", True) if user else True}

@router.patch("/client/settings/notifications")
async def update_notification_settings(request: Request, client: dict = Depends(get_current_client)):
    body = await request.json()
    update = {}
    if "notifications_email" in body:
        update["notifications_email"] = bool(body["notifications_email"])
    if "notifications_push" in body:
        update["notifications_push"] = bool(body["notifications_push"])
    if update:
        await db.client_users.update_one({"id": client["sub"]}, {"$set": update})
    return {"success": True}


# ==================== PUSH SUBSCRIPTIONS ====================

@router.get("/push/vapid-key")
async def get_vapid_public_key():
    import os
    key = os.environ.get("VAPID_PUBLIC_KEY", "")
    return {"public_key": key}

@router.post("/push/subscribe")
async def push_subscribe(request: Request, client: dict = Depends(get_current_client)):
    body = await request.json()
    subscription = body.get("subscription")
    if not subscription or not subscription.get("endpoint"):
        raise HTTPException(status_code=400, detail="Subscription invalide")
    existing = await db.push_subscriptions.find_one(
        {"client_id": client["sub"], "subscription.endpoint": subscription["endpoint"]},
        {"_id": 0}
    )
    if existing:
        return {"success": True, "message": "Déjà abonné"}
    doc = {
        "id": str(uuid.uuid4()),
        "client_id": client["sub"],
        "subscription": subscription,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.push_subscriptions.insert_one(doc)
    return {"success": True, "message": "Abonnement push activé"}

@router.delete("/push/unsubscribe")
async def push_unsubscribe(request: Request, client: dict = Depends(get_current_client)):
    body = await request.json()
    endpoint = body.get("endpoint", "")
    if endpoint:
        await db.push_subscriptions.delete_many(
            {"client_id": client["sub"], "subscription.endpoint": endpoint}
        )
    else:
        await db.push_subscriptions.delete_many({"client_id": client["sub"]})
    return {"success": True, "message": "Abonnement push désactivé"}

@router.post("/push/test")
async def test_push_notification(client: dict = Depends(get_current_client)):
    from utils.push import send_push_to_client
    await send_push_to_client(
        db, client["sub"],
        title="Test de notification",
        body="Les notifications push fonctionnent correctement !",
        url="/espace-client",
        tag="test"
    )
    return {"success": True, "message": "Notification test envoyée"}


# ==================== STORAGE STATUS ====================

@router.get("/storage/status")
async def get_storage_status():
    return {
        "object_storage_available": STORAGE_AVAILABLE,
        "provider": "Emergent Object Storage" if STORAGE_AVAILABLE else "MongoDB (base64 fallback)",
    }
