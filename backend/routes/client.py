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
