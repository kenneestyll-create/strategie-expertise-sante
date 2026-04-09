"""
CONSOLIDATION_ARCHITECTURE — Routes Dossier Express IA.
Responsabilite unique : pipeline Dossier Express (formulaire, extraction, analyse, PDF, admin, suivi).
ISOLE de StrategiIA. Aucune contamination croisee.

Collections MongoDB : dossier_express, premium_analyses
Dependances : utils/llm.py, utils/document_extraction.py, utils/notifications.py, constants/prompts.py
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import asyncio
import uuid
import base64
import os

from config import db, STRIPE_API_KEY, RESEND_AVAILABLE, SENDER_EMAIL, logger, JWT_SECRET, JWT_ALGORITHM, SITE_URL
from utils.auth import get_current_admin, get_optional_admin
from utils.email import notify_admin_premium_analysis
from utils.pdf import generate_dossier_pdf
from utils.storage import put_object
from constants.statuses import Service, DossierStatus, DossierDelivery, DossierStep, PremiumStatus, DOSSIER_STEP_CLIENT_MAP, CLIENT_STEPS_DISPLAY
from constants.workflows import LLM_MAX_RETRIES, LLM_RETRY_DELAY_SECONDS, MAX_FILE_SIZE, MAX_TOTAL_SIZE, MAX_FILES
from constants.guards import assert_valid_service, assert_premium_analyses_entry
from constants.prompts import DOSSIER_EXPRESS_SYSTEM_PROMPT, DOSSIER_EXPRESS_PROMPT
from constants.assurance_knowledge import get_assurance_context, detect_insurer_from_text
from constants.contestation_knowledge import get_contestation_context, detect_contestation_context
from constants.mdph_knowledge import get_mdph_context, detect_mdph_context
from routes.knowledge_patterns import get_knowledge_patterns_context
from utils.llm import (
    has_llm_key as _has_llm_key,
    check_llm_health as _check_llm_health,
    llm_call,
    generate_dossier_report_multistage as _generate_dossier_report_multistage,
    ANTHROPIC_API_KEY, EMERGENT_LLM_KEY,
)
from utils.notifications import notify_admin_incident as _notify_admin_incident, notify_client_delay as _notify_client_delay
from utils.document_extraction import extract_pdf_full_pipeline as _extract_pdf_full_pipeline, extract_image_ocr as _extract_image_ocr

try:
    import resend
except ImportError:
    pass

import stripe as stripe_sdk

NOTIFICATION_EMAIL = os.environ.get("NOTIFICATION_EMAIL", "")

router = APIRouter()


# ==================== DOSSIER EXPRESS ====================

@router.post("/extract-document-text")
async def extract_document_text(request: Request):
    """Extract text from uploaded documents with full pipeline: pdfplumber → OCR → metadata."""
    import io
    body = await request.json()
    files_data = body.get("files", [])
    if not files_data:
        return {"extracted_text": "", "files_processed": 0, "details": []}

    MAX_FILE_SIZE_LOCAL = MAX_FILE_SIZE
    MAX_TOTAL_SIZE_LOCAL = MAX_TOTAL_SIZE
    MAX_FILES_LOCAL = MAX_FILES

    if len(files_data) > MAX_FILES_LOCAL:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_FILES_LOCAL} fichiers autorises")

    results = []
    total_size = 0
    for file_info in files_data[:MAX_FILES_LOCAL]:
        name = file_info.get("name", "unknown")
        file_type = file_info.get("type", "")
        data_b64 = file_info.get("data", "")
        if not data_b64:
            results.append({"name": name, "text": "", "method": "pas de données", "pages": 0, "size_kb": 0, "status": "no_data"})
            continue

        try:
            file_bytes = base64.b64decode(data_b64)
        except Exception:
            results.append({"name": name, "text": "", "method": "erreur decodage", "pages": 0, "size_kb": 0, "status": "decode_error"})
            continue

        if len(file_bytes) > MAX_FILE_SIZE_LOCAL:
            results.append({"name": name, "text": "", "method": "fichier trop volumineux", "pages": 0, "size_kb": round(len(file_bytes) / 1024, 1), "status": "too_large"})
            continue

        total_size += len(file_bytes)
        if total_size > MAX_TOTAL_SIZE_LOCAL:
            results.append({"name": name, "text": "", "method": "taille totale depassee", "pages": 0, "size_kb": round(len(file_bytes) / 1024, 1), "status": "total_exceeded"})
            continue

        size_kb = round(len(file_bytes) / 1024, 1)
        extracted = ""
        method = "non supporté"
        pages = 0
        status = "unsupported"

        if file_type == "application/pdf" or name.lower().endswith(".pdf"):
            extracted, method, pages, status = await asyncio.to_thread(
                _extract_pdf_full_pipeline, file_bytes, name
            )

        elif file_type and file_type.startswith("image/"):
            extracted, method, status = await asyncio.to_thread(
                _extract_image_ocr, file_bytes, name
            )
            pages = 1

        elif file_type in ("text/plain",) or name.lower().endswith(".txt"):
            try:
                extracted = file_bytes.decode("utf-8", errors="replace")
                method = "lecture texte directe"
                status = "text_extracted"
            except Exception:
                method = "erreur lecture texte"
                status = "text_error"

        preview = extracted[:200].strip() if extracted else ""
        results.append({
            "name": name,
            "text": extracted[:8000],
            "method": method,
            "pages": pages,
            "size_kb": size_kb,
            "status": status,
            "preview": preview,
            "text_length": len(extracted)
        })

    combined = ""
    for r in results:
        combined += f"\n--- {r['name']} ({r['method']}) ---\n"
        if r["text"]:
            combined += r["text"] + "\n"
        else:
            combined += "[Contenu non extractible]\n"

    # Store original files to Object Storage (best-effort)
    stored_files = []
    try:
        from utils.storage import upload_file as storage_upload
        for file_info in files_data[:MAX_FILES_LOCAL]:
            data_b64 = file_info.get("data", "")
            if not data_b64:
                continue
            try:
                raw_bytes = base64.b64decode(data_b64)
                fname = file_info.get("name", "unknown")
                ftype = file_info.get("type", "application/octet-stream")
                result = storage_upload("dossier-originals", fname, raw_bytes, ftype)
                doc_id = str(uuid.uuid4())
                result["file_id"] = doc_id

                doc_meta = {
                    "id": doc_id,
                    "original_filename": fname,
                    "content_type": ftype,
                    "size": len(raw_bytes),
                    "storage_path": result.get("storage_path", ""),
                    "source": "dossier_express",
                    "user_email": "",
                    "dossier_id": "",
                    "status": "stored",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                await db.documents.insert_one(doc_meta)
                stored_files.append(result)
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Object storage not available for base64 file persistence: {e}")

    return {
        "extracted_text": combined.strip(),
        "files_processed": len(results),
        "details": [{
            "name": r["name"],
            "method": r["method"],
            "has_text": len(r["text"]) > 10,
            "pages": r["pages"],
            "size_kb": r["size_kb"],
            "status": r["status"],
            "preview": r.get("preview", ""),
            "text_length": r.get("text_length", 0)
        } for r in results],
        "stored_files": stored_files
    }



# OCR/Extraction: imported from utils/document_extraction.py -> _extract_pdf_full_pipeline, _extract_image_ocr
# LLM multi-stage: imported from utils/llm.py -> _generate_dossier_report_multistage, generate_section_llmchat

async def _update_dossier_step(dossier_id: str, processing_step: str, delivery_status: str = None, extra: dict = None):
    """Atomic helper to update processing step and optionally delivery status."""
    update = {"processing_step": processing_step, "updated_at": datetime.now(timezone.utc).isoformat()}
    if delivery_status:
        update["delivery_status"] = delivery_status
    if extra:
        update.update(extra)
    await db.dossier_express.update_one({"id": dossier_id}, {"$set": update})



# _generate_section_llmchat -> imported from utils/llm.py
# _generate_dossier_report_multistage -> imported from utils/llm.py

async def _process_dossier_express(dossier_id: str, email: str, name: str, situation: str, type_dossier: str, regime: str, documents_text: str, premium_pdf: bool = False, improvement_optout: bool = False):
    """Full pipeline with granular step tracking, timing instrumentation, and fail-safe notifications."""
    import time
    t_start = time.monotonic()
    timings = {}
    logger.info(f"[DOSSIER_EXPRESS][{dossier_id}][START] email={email} type={type_dossier} regime={regime} premium_pdf={premium_pdf}")

    # === STEP 1: Documents received ===
    await _update_dossier_step(dossier_id, "documents_recus", "en_attente_traitement")

    # === STEP 2: Check LLM availability ===
    if not _has_llm_key():
        logger.error("Dossier Express IA: aucune cle IA disponible")
        await _update_dossier_step(dossier_id, "erreur_ia", "incident_technique", {"status": "error", "error": "Service IA non disponible"})
        await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Verification cle API", "Aucune cle IA configuree (ANTHROPIC_API_KEY et EMERGENT_LLM_KEY absentes)")
        await _notify_client_delay(email, name, "Dossier Express IA")
        return

    # === STEP 3: Context preparation ===
    t_ctx = time.monotonic()
    await _update_dossier_step(dossier_id, "extraction_en_cours", "en_attente_traitement", {"progress_step": "reading"})

    similar_cases = []
    try:
        if type_dossier:
            similar_cases = await db.cas_anonymises.find({"type_dossier": type_dossier}, {"_id": 0}).sort("score_pertinence", -1).to_list(5)
    except Exception as e:
        logger.warning(f"Dossier Express {dossier_id}: cas similaires lookup failed (non-blocking): {e}")

    case_context = ""
    if similar_cases:
        case_context = "\n\nCAS SIMILAIRES DANS LA BASE :\n"
        for c in similar_cases:
            case_context += f"- Type: {c.get('type_dossier')}, Regime: {c.get('regime')}, Strategie: {c.get('strategie')}, Resultat: {c.get('resultat')}\n"

    timings["context_prep"] = round(time.monotonic() - t_ctx, 2)

    # INJECTION CONTEXTE ASSURANTIEL — si litige assurantiel
    assurance_context = ""
    type_dossier_lower = (type_dossier or "").lower()
    if "assurance" in type_dossier_lower or "litige" in type_dossier_lower:
        try:
            # Priorité 1 : garantie sélectionnée par l'utilisateur
            garantie = regime.upper() if regime and regime.upper() in ("ITT", "ITP", "IPT", "IPP", "PTIA", "PE", "DECES") else None
            # Priorité 2 : assureur détecté dans le texte (situation + documents)
            combined_text = f"{situation} {documents_text[:3000] if documents_text else ''}"
            detected = detect_insurer_from_text(combined_text)
            detected_assureur = detected.get("assureur")
            # Priorité 3 : fallback générique
            assurance_context = "\n\nBASE DE CONNAISSANCES ASSURANTIELLE"
            if detected_assureur:
                assureur_label = {"generali": "GENERALI", "groupama_gan_vie": "GROUPAMA GAN VIE", "cnp_assurances": "CNP ASSURANCES", "gmf_vie": "GMF VIE"}.get(detected_assureur, detected_assureur.upper())
                assurance_context += f" (assureur détecté : {assureur_label})"
            else:
                assurance_context += " (contrats analysés : GENERALI, GROUPAMA GAN VIE, CNP ASSURANCES, GMF VIE)"
            assurance_context += " :\n"
            assurance_context += get_assurance_context(assureur=detected_assureur, garantie=garantie)
            assurance_context += "\nINSTRUCTION : Utilise cette base de connaissances pour identifier les exclusions, red flags, et leviers stratégiques spécifiques au contrat et à la garantie concernés. Compare les assureurs si pertinent. Cite les seuils et conditions exactes."
            logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] Assurance context injected ({len(assurance_context)} chars, garantie={garantie}, detected_insurer={detected_assureur}, confidence={detected.get('confidence')})")
        except Exception as e:
            logger.warning(f"[DOSSIER_EXPRESS][{dossier_id}] Assurance context injection failed (non-blocking): {e}")

    # INJECTION CONTEXTE CONTESTATION IPP
    contestation_context = ""
    try:
        all_text = f"{situation} {documents_text or ''}"
        detected_regime = detect_contestation_context(all_text)
        if detected_regime or (type_dossier or "").lower() in ("contestation_taux_ipp", "contestation taux ipp"):
            regime_key = detected_regime or "regime_general"
            contestation_context = "\n\n" + get_contestation_context(regime=regime_key)
            contestation_context += "\nINSTRUCTION : Utilise ces procedures de contestation pour orienter le beneficiaire. Cite les delais, instances, adresses et erreurs a eviter."
            logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] Contestation context injected ({len(contestation_context)} chars, regime={regime_key})")
    except Exception as e:
        logger.warning(f"[DOSSIER_EXPRESS][{dossier_id}] Contestation context injection failed (non-blocking): {e}")

    # INJECTION CONTEXTE MDPH — si demande MDPH detectee
    mdph_context = ""
    try:
        detected_mdph = detect_mdph_context(all_text)
        if detected_mdph or (type_dossier or "").lower() in ("demande_mdph", "demande mdph", "mdph"):
            demande_key = detected_mdph or "general"
            mdph_context = "\n\n" + get_mdph_context(demande_type=demande_key)
            mdph_context += "\nINSTRUCTION : Utilise cette base de connaissances MDPH pour orienter le beneficiaire. Cite les conditions, delais, montants, voies de recours et erreurs a eviter."
            logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] MDPH context injected ({len(mdph_context)} chars, type={demande_key})")
    except Exception as e:
        logger.warning(f"[DOSSIER_EXPRESS][{dossier_id}] MDPH context injection failed (non-blocking): {e}")

    # === STEP 4: AI Generation ===
    t_llm = time.monotonic()
    await _update_dossier_step(dossier_id, "analyse_ia", "en_attente_traitement", {"progress_step": "analyzing"})

    analysis = None
    last_error = ""
    llm_path_used = "none"

    # PATH A: Native Anthropic SDK — single direct call, no proxy, no batching
    # INJECTION KNOWLEDGE PATTERNS — couche d'enrichissement metier (non bloquant)
    enhanced_de_system = DOSSIER_EXPRESS_SYSTEM_PROMPT
    if not improvement_optout:
        try:
            knowledge_context = await get_knowledge_patterns_context(
                categorie=type_dossier, metier=regime,
                type_sinistre=type_dossier, type_garantie=regime,
                blocage=None, situation_text=situation
            )
            if knowledge_context:
                enhanced_de_system = DOSSIER_EXPRESS_SYSTEM_PROMPT + knowledge_context
                logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] Knowledge patterns injected ({len(knowledge_context)} chars)")
        except Exception as e:
            logger.warning(f"[DOSSIER_EXPRESS][{dossier_id}] Knowledge patterns injection failed (non-blocking): {e}")

    if ANTHROPIC_API_KEY:
        llm_path_used = "native_anthropic"
        user_msg = f"""DOSSIER EXPRESS IA - Analyse complete demandee

Client : {name}
Type de dossier : {type_dossier}
Regime : {regime}

DESCRIPTION DE LA SITUATION :
{situation}

CONTENU DES DOCUMENTS FOURNIS :
{documents_text[:12000] if documents_text else "(Aucun document textuel fourni)"}
{case_context}{assurance_context}{contestation_context}{mdph_context}

{DOSSIER_EXPRESS_PROMPT}"""

        # Step updates during single call for UX feedback
        await _update_dossier_step(dossier_id, "analyse_ia", "en_attente_traitement", {"progress_step": "analyzing_1"})

        for attempt in range(3):
            try:
                session_id_llm = f"dexpress_{dossier_id[:8]}_{attempt}"
                analysis = await llm_call(
                    ANTHROPIC_API_KEY, session_id_llm, enhanced_de_system, user_msg,
                    "anthropic", "claude-sonnet-4-5-20250929", max_tokens=8000
                )
                logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] PATH A native reussie (tentative {attempt+1}, {len(analysis or '')} chars)")
                break
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[DOSSIER_EXPRESS][{dossier_id}] PATH A native tentative {attempt+1}/3 echouee: {last_error[:120]}")
                if attempt < 2:
                    await asyncio.sleep(3)

    # PATH B: Emergent proxy — multi-stage pipeline (handles 60s timeout structurally)
    if not analysis and EMERGENT_LLM_KEY:
        llm_path_used = "emergent_multistage"
        for attempt in range(2):
            try:
                analysis = await _generate_dossier_report_multistage(
                    dossier_id, name, type_dossier, regime, situation, documents_text, case_context
                )
                logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] PATH B multi-stage reussie (tentative {attempt+1})")
                break
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[DOSSIER_EXPRESS][{dossier_id}] PATH B multi-stage tentative {attempt+1}/2 echouee: {last_error[:150]}")
                if attempt < 1:
                    await asyncio.sleep(8)

    timings["llm_generation"] = round(time.monotonic() - t_llm, 2)

    if not analysis:
        error_label = "Echec generation IA"
        if "budget" in last_error.lower() or "exceeded" in last_error.lower():
            error_label = "Budget IA epuise"
        logger.error(f"[DOSSIER_EXPRESS][{dossier_id}] ECHEC TOTAL: {last_error[:200]}")
        await _update_dossier_step(dossier_id, "erreur_ia", "incident_technique", {"status": "error", "error": error_label})
        await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Generation IA", f"{error_label}: {last_error[:300]}")
        await _notify_client_delay(email, name, "Dossier Express IA")
        return

    # Validate analysis is substantial
    if len(analysis.strip()) < 500:
        logger.error(f"[DOSSIER_EXPRESS][{dossier_id}] analyse trop courte ({len(analysis)} chars)")
        await _update_dossier_step(dossier_id, "erreur_ia", "incident_technique", {"status": "error", "error": "Analyse insuffisante"})
        await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Validation analyse", f"Analyse trop courte: {len(analysis)} caracteres")
        await _notify_client_delay(email, name, "Dossier Express IA")
        return

    # === STEP 5: Quality Scoring (internal admin) ===
    quality_score = None
    try:
        from utils.quality_scoring import score_report
        quality_score = score_report(analysis, "dossier_express", metier=type_dossier, sinistre=type_dossier)
        logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] Quality={quality_score['level']} ({quality_score['score']}/100)")
    except Exception as qs_err:
        logger.warning(f"[DOSSIER_EXPRESS][{dossier_id}] Quality scoring failed (non-blocking): {qs_err}")

    # Case Outcome Memory — collecte silencieuse (V2 preparation, non bloquant)
    try:
        if not improvement_optout:
            from utils.case_outcome_memory import extract_case_features, store_case_outcome
            features = extract_case_features(analysis, type_dossier=type_dossier, regime=regime, situation=situation)
            await store_case_outcome(db, "dossier_express", type_dossier, regime, features, quality_score=quality_score, improvement_optout=improvement_optout)
    except Exception as com_err:
        logger.debug(f"[DOSSIER_EXPRESS][{dossier_id}] Case outcome memory failed (non-blocking): {com_err}")
    # V2 Predictive hook dormant — conditionne au feature flag (OFF par defaut = aucun impact)
    try:
        from utils.predictive_v2 import is_v2_enabled, run_predictive_analysis
        if await is_v2_enabled(db):
            v2_features = features if 'features' in dir() else None
            v2_result = run_predictive_analysis(situation or "", type_dossier, regime, case_features=v2_features)
            await db.dossier_express.update_one({"id": dossier_id}, {"$set": {
                "v2_predictive": {
                    "robustness_score": v2_result["robustness_score"],
                    "robustness_level": v2_result["robustness_level"],
                    "alert_count": v2_result["alert_count"],
                    "version": v2_result["analysis_version"],
                },
            }})
            logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] V2 robustness={v2_result['robustness_score']}/100 alerts={v2_result['alert_count']}")
    except Exception as v2_err:
        logger.debug(f"[DOSSIER_EXPRESS][{dossier_id}] V2 hook (non-blocking): {v2_err}")

    # === STEP 6: PDF Generation ===
    t_pdf = time.monotonic()
    await _update_dossier_step(dossier_id, "pdf_en_cours", "en_attente_traitement", {"progress_step": "generating", "analysis": analysis[:30000]})

    dossier_doc = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0, "document_details": 1})
    doc_details = dossier_doc.get("document_details", []) if dossier_doc else []

    pdf_bytes = None
    try:
        pdf_bytes = generate_dossier_pdf(name, email, type_dossier, regime, analysis, premium_pdf=premium_pdf, document_details=doc_details)
        if not pdf_bytes or len(pdf_bytes) < 100:
            raise ValueError("PDF vide ou corrompu")
        logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] PDF genere ({len(pdf_bytes)} bytes)")
    except Exception as e:
        logger.error(f"[DOSSIER_EXPRESS][{dossier_id}] PDF generation failed: {e}")
        await _update_dossier_step(dossier_id, "erreur_pdf", "incident_technique", {"status": "error", "error": "Echec generation PDF"})
        await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Generation PDF", str(e)[:300])
        await _notify_client_delay(email, name, "Dossier Express IA")
        return
    timings["pdf_generation"] = round(time.monotonic() - t_pdf, 2)

    # === STEP 6: Storage ===
    t_storage = time.monotonic()
    await _update_dossier_step(dossier_id, "stockage_en_cours", "en_attente_traitement", {"progress_step": "generating"})

    download_token = str(uuid.uuid4())
    pdf_storage_path = None
    download_url = None
    try:
        storage_path = f"strategie-expertise-sante/dossiers/{dossier_id}/{download_token}.pdf"
        put_object(storage_path, pdf_bytes, "application/pdf")
        pdf_storage_path = storage_path
        download_url = f"{SITE_URL}/api/dossier-express/{dossier_id}/download?token={download_token}"
        await db.dossier_express.update_one({"id": dossier_id}, {"$set": {
            "pdf_storage_path": pdf_storage_path,
            "download_token": download_token,
        }})
        logger.info(f"Dossier Express {dossier_id}: PDF uploaded to storage")
    except Exception as e:
        logger.error(f"[DOSSIER_EXPRESS][{dossier_id}] PDF storage upload failed (non-blocking): {e}")
        # S3 failure is NOT fatal — PDF exists in memory, continue with email + admin registration
        await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Stockage PDF", str(e)[:300])
    timings["storage"] = round(time.monotonic() - t_storage, 2)

    # === STEP 7: Email delivery ===
    t_email = time.monotonic()
    await _update_dossier_step(dossier_id, "email_en_cours", "en_attente_traitement", {"progress_step": "sending"})

    expert_url = f"{SITE_URL}/contact?via=email&source=dossier_express"
    safe_display_name = name or "Madame, Monsieur"

    email_html = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f4f2ed;font-family:Arial,'Helvetica Neue',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f2ed;padding:32px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
<tr><td style="background:#1a1a1a;padding:28px 32px;border-radius:8px 8px 0 0;">
  <table width="100%"><tr>
    <td><span style="color:#ffffff;font-size:18px;font-weight:bold;letter-spacing:0.5px;">Strategie & Expertise Sante</span><br/>
    <span style="color:#c9a84c;font-size:11px;letter-spacing:3px;text-transform:uppercase;">PIONNIER EN FRANCE</span></td>
    <td align="right"><span style="color:#999;font-size:12px;">Dossier Express IA</span></td>
  </tr></table>
</td></tr>
<tr><td style="background:#ffffff;padding:36px 32px 24px;">
  <p style="font-size:15px;color:#1a1a1a;margin:0 0 20px;">Bonjour {safe_display_name},</p>
  <p style="font-size:15px;color:#333;line-height:1.6;margin:0 0 8px;">
    Votre analyse personnalisee a bien ete finalisee.
  </p>
  <p style="font-size:15px;color:#333;line-height:1.6;margin:0 0 28px;">
    Vous pouvez desormais consulter et telecharger votre rapport en toute simplicite.
  </p>
  <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:8px 0 32px;">
    <a href="{download_url or '#'}" target="_blank"
       style="display:inline-block;background:#1a1a1a;color:#ffffff;font-size:15px;font-weight:bold;
              padding:15px 40px;border-radius:6px;text-decoration:none;letter-spacing:0.5px;
              border:2px solid #c9a84c;">
      Telecharger mon rapport PDF
    </a>
  </td></tr></table>
  <div style="border-left:3px solid #c9a84c;padding:16px 20px;margin:0 0 28px;background:#faf8f3;">
    <p style="font-size:14px;color:#555;line-height:1.6;margin:0 0 12px;">
      Ce document constitue une premiere lecture structuree de votre situation
      a partir des elements transmis.
    </p>
    <p style="font-size:14px;color:#333;line-height:1.6;margin:0;font-weight:500;">
      Si vous souhaitez aller plus loin, une prestation personnalisee avec
      suivi humain peut ensuite vous etre proposee.
    </p>
  </div>
  <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:0 0 12px;">
    <a href="{expert_url}" target="_blank"
       style="display:inline-block;background:transparent;color:#1a1a1a;font-size:13px;font-weight:600;
              padding:11px 28px;border-radius:6px;text-decoration:none;
              border:1.5px solid #c9a84c;">
      Etre accompagne par un expert
    </a>
  </td></tr></table>
  <div style="border-top:1px solid #e8e3d6;padding:14px 0 0;margin:16px 0 0;">
    <p style="font-size:11px;color:#888;line-height:1.6;margin:0;text-align:center;">
      &#128274; Vos documents sont traites dans un cadre strictement confidentiel,
      uniquement pour repondre a votre demande. L'acces a vos donnees est limite
      a l'equipe en charge de votre accompagnement.
    </p>
  </div>
</td></tr>
<tr><td style="background:#1a1a1a;padding:20px 32px;border-radius:0 0 8px 8px;text-align:center;">
  <p style="color:#c9a84c;font-size:13px;font-style:italic;margin:0 0 8px;font-weight:600;">
    Strategie & Expertise Sante — Votre bouclier.
  </p>
  <p style="color:#888;font-size:11px;margin:0;">
    strategie-expertise-sante.fr &nbsp;|&nbsp; Ce rapport est un outil d'aide a la decision.
  </p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""

    email_sent = False
    if RESEND_AVAILABLE and resend.api_key:
        try:
            email_params = {
                "from": SENDER_EMAIL,
                "to": [email],
                "subject": "Votre Rapport Dossier Express IA est pret - Strategie & Expertise Sante",
                "html": email_html,
                "attachments": [{"filename": f"Rapport_Dossier_Express_{dossier_id[:8]}.pdf", "content": list(pdf_bytes)}]
            }
            await asyncio.to_thread(resend.Emails.send, email_params)
            email_sent = True
            logger.info(f"Dossier Express IA {dossier_id}: email envoye a {email}")
        except Exception as e:
            logger.error(f"Dossier Express IA {dossier_id} email error: {e}")
            # Email failure is NOT fatal — PDF is already stored, admin is notified
            await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Envoi email", str(e)[:300])

    # === STEP 8: Final — mark as delivered ===
    timings["email"] = round(time.monotonic() - t_email, 2)
    t_total = round(time.monotonic() - t_start, 2)
    timings["total"] = t_total

    final_delivery = "livre_client" if email_sent else "genere_sans_email"
    final_step = "termine" if email_sent else "erreur_email"
    final_update = {
        "status": "completed",
        "email_sent": email_sent,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "progress_step": "completed",
        "timings": timings,
        "llm_path": llm_path_used,
        "analysis_chars": len(analysis),
    }
    if quality_score:
        final_update["quality_score"] = quality_score
    await _update_dossier_step(dossier_id, final_step, final_delivery, final_update)

    logger.info(f"[DOSSIER_EXPRESS][{dossier_id}][COMPLETE] path={llm_path_used} total={t_total}s | context={timings.get('context_prep',0)}s llm={timings.get('llm_generation',0)}s pdf={timings.get('pdf_generation',0)}s storage={timings.get('storage',0)}s email={timings.get('email',0)}s | chars={len(analysis)} pdf={len(pdf_bytes)}B")

    if not email_sent:
        # Partial success — PDF exists but email failed. Notify client via fallback
        await _notify_client_delay(email, name, "Dossier Express IA")

    # Auto-register in premium_analyses for admin review workflow
    try:
        existing_pa = await db.premium_analyses.find_one({"type": Service.DOSSIER_EXPRESS, "email": email, "dossier_id": {"$exists": False}})
        if existing_pa:
            await db.premium_analyses.update_one({"id": existing_pa["id"]}, {"$set": {"dossier_id": dossier_id}})
            logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] linked to existing premium_analyses {existing_pa['id']}")
        else:
            pa_entry = {
                "id": str(uuid.uuid4()), "type": Service.DOSSIER_EXPRESS, "email": email, "name": name,
                "dossier_id": dossier_id, "status": PremiumStatus.EN_ATTENTE,
                "relecture_expert_required": True, "premium_pdf": premium_pdf,
                "amount": 0, "admin_test": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            assert_premium_analyses_entry(pa_entry, f"dossier_express_auto_register_{dossier_id}")
            await db.premium_analyses.insert_one(pa_entry)
            logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] created premium_analyses entry {pa_entry['id']}")
    except Exception as e:
        logger.warning(f"[DOSSIER_EXPRESS][{dossier_id}] premium_analyses registration failed (non-blocking): {e}")


@router.get("/dossier-express/{dossier_id}/download")
async def download_dossier_pdf(dossier_id: str, token: str = ""):
    """Public endpoint to download the Dossier Express PDF via a secure token."""
    if not token:
        raise HTTPException(status_code=400, detail="Token requis")
    dossier = await db.dossier_express.find_one(
        {"id": dossier_id, "download_token": token},
        {"_id": 0, "pdf_storage_path": 1, "status": 1, "name": 1}
    )
    if not dossier:
        raise HTTPException(status_code=404, detail="Lien de téléchargement invalide ou expiré")
    if dossier.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Le rapport n'est pas encore prêt")
    storage_path = dossier.get("pdf_storage_path")
    if not storage_path:
        raise HTTPException(status_code=404, detail="PDF non disponible")
    try:
        from utils.storage import download_file
        pdf_data, content_type = download_file(storage_path)
        from fastapi.responses import Response
        safe_name = (dossier.get("name") or "rapport").replace(" ", "-")
        filename = f"Rapport-Dossier-Express-{safe_name}.pdf"
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "private, max-age=3600",
            },
        )
    except Exception as e:
        logger.error(f"PDF download error for {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du téléchargement")


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

    # ====== LAUNCH MODE CHECK — SOFT LAUNCH GATING ======
    launch_config = await db.system_config.find_one({"key": "launch_mode"}, {"_id": 0})
    launch_mode = launch_config.get("value", "ouvert") if launch_config else "ouvert"
    if launch_mode == "indisponible":
        custom_msg = launch_config.get("message", "") if launch_config else ""
        raise HTTPException(
            status_code=503,
            detail=custom_msg or "Le service est temporairement suspendu pour maintenance programmee. Nous serons de retour tres prochainement."
        )

    # ====== PRE-PAYMENT LLM HEALTH CHECK — STRICTLY BLOCKING ======
    llm_ok, llm_reason = await _check_llm_health()
    if not llm_ok:
        logger.warning(f"Dossier Express checkout BLOCKED: LLM unavailable ({llm_reason}) for {email}")
        raise HTTPException(
            status_code=503,
            detail="Le service est momentanement indisponible pour finalisation technique. Merci de reessayer dans quelques instants."
        )

    amount = 97.00
    if premium_pdf:
        amount += 19.00
    if analyse_premium:
        amount += 49.00
    params = f"premium_pdf={'1' if premium_pdf else '0'}&analyse_premium={'1' if analyse_premium else '0'}"
    success_url = f"{origin_url}/dossier-express?payment=success&session_id={{CHECKOUT_SESSION_ID}}&{params}"
    cancel_url = f"{origin_url}/dossier-express?payment=cancelled"
    stripe_sdk.api_key = STRIPE_API_KEY
    tag = "dossier_express"
    if premium_pdf and analyse_premium:
        tag = "dossier_express_full"
    elif premium_pdf:
        tag = "dossier_express_pdf_pro"
    elif analyse_premium:
        tag = "dossier_express_analyse_premium"
    metadata = {"package_id": tag, "package_name": f"Dossier Express IA ({amount:.0f}€)", "customer_email": email, "customer_name": name, "premium_pdf": "1" if premium_pdf else "0", "analyse_premium": "1" if analyse_premium else "0"}
    if analyse_premium:
        pa_entry = {"id": str(uuid.uuid4()), "type": Service.DOSSIER_EXPRESS, "email": email, "name": name, "status": PremiumStatus.EN_ATTENTE, "relecture_expert_required": True, "premium_pdf": premium_pdf, "amount": amount, "created_at": datetime.now(timezone.utc).isoformat()}
        assert_premium_analyses_entry(pa_entry, "dossier_express_checkout")
        await db.premium_analyses.insert_one(pa_entry)
        logger.info(f"[DOSSIER_EXPRESS][checkout] premium_analyses entry {pa_entry['id']} created for {email}")
        asyncio.create_task(notify_admin_premium_analysis(Service.DOSSIER_EXPRESS, email, name, amount, options={"analyse_premium": True, "premium_pdf": premium_pdf}))
    try:
        session = await asyncio.to_thread(
            stripe_sdk.checkout.Session.create,
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "eur", "product_data": {"name": metadata["package_name"]}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata,
        )
        return {"success": True, "url": session.url, "session_id": session.id}
    except Exception as e:
        logger.error(f"Dossier Express IA checkout error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")

@router.get("/dossier-express/suivi/{dossier_id}")
async def dossier_express_suivi(dossier_id: str, token: str = ""):
    """Public client-facing tracker — returns only premium, human-readable status."""
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouve")
    # Security: require download_token match
    if token and dossier.get("download_token") and token != dossier.get("download_token"):
        raise HTTPException(status_code=403, detail="Acces non autorise")

    # Map internal steps to premium client-facing labels (from centralized constants)
    STEP_MAP = {k: {"order": v["order"], "label": v["label"], "done": True} for k, v in DOSSIER_STEP_CLIENT_MAP.items()}

    CLIENT_STEPS = CLIENT_STEPS_DISPLAY

    current_step = dossier.get("processing_step", "checkout_valide")
    status = dossier.get("status", "processing")
    delivery_status = dossier.get("delivery_status", "en_attente_traitement")
    step_info = STEP_MAP.get(current_step, {"order": 1, "label": "Dossier en cours de traitement", "done": True})

    is_incident = delivery_status == "incident_technique"
    is_completed = status == "completed"

    # Build steps with progress
    step_order = step_info["order"]
    if is_completed:
        step_order = 8

    steps_with_status = []
    order_map = [1, 2, 3, 4, 5, 7, 8]
    for i, s in enumerate(CLIENT_STEPS):
        s_order = order_map[i]
        if is_incident and s_order > step_order:
            steps_with_status.append({**s, "status": "waiting"})
        elif s_order < step_order:
            steps_with_status.append({**s, "status": "completed"})
        elif s_order == step_order:
            steps_with_status.append({**s, "status": "active" if not is_completed else "completed"})
        else:
            steps_with_status.append({**s, "status": "waiting"})

    # Client-facing message
    if is_completed:
        client_message = "Votre rapport est disponible. Vous pouvez le telecharger ci-dessous."
    elif is_incident:
        client_message = "Votre dossier est bien pris en charge. Un traitement complementaire est en cours pour vous garantir la meilleure qualite d'analyse."
    else:
        client_message = step_info["label"]

    result = {
        "dossier_id": dossier_id,
        "name": dossier.get("name", ""),
        "status": "completed" if is_completed else ("incident" if is_incident else "processing"),
        "message": client_message,
        "current_label": step_info["label"] if not is_completed else "Rapport disponible",
        "steps": steps_with_status,
        "created_at": dossier.get("created_at"),
        "completed_at": dossier.get("completed_at"),
    }

    if is_completed and dossier.get("download_token"):
        result["download_url"] = f"{SITE_URL}/api/dossier-express/{dossier_id}/download?token={dossier.get('download_token')}"

    return result


@router.get("/dossier-express/status/{dossier_id}")
async def dossier_express_status(dossier_id: str):
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0, "documents_text": 0})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouve")
    return dossier

@router.get("/admin/dossier-express")
async def admin_dossier_express(admin: dict = Depends(get_current_admin)):
    dossiers = await db.dossier_express.find({}, {"_id": 0, "documents_text": 0, "analysis": 0}).sort("created_at", -1).to_list(100)
    stats = {
        "total": len(dossiers),
        "completed": sum(1 for d in dossiers if d.get("status") == "completed"),
        "processing": sum(1 for d in dossiers if d.get("status") == "processing"),
        "errors": sum(1 for d in dossiers if d.get("status") == "error"),
        "incidents": sum(1 for d in dossiers if d.get("delivery_status") == "incident_technique"),
        "delivered": sum(1 for d in dossiers if d.get("delivery_status") == "livre_client" or (d.get("status") == "completed" and not d.get("delivery_status"))),
        "pending": sum(1 for d in dossiers if d.get("delivery_status") == "en_attente_traitement" or (d.get("status") == "processing" and not d.get("delivery_status"))),
    }
    return {"items": dossiers, "stats": stats}


@router.post("/admin/dossier-express/{dossier_id}/retry")
async def admin_retry_dossier(dossier_id: str, admin: dict = Depends(get_current_admin)):
    """Admin endpoint to retry a failed dossier processing from scratch."""
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouve")
    if dossier.get("status") not in ("error",):
        raise HTTPException(status_code=400, detail="Seuls les dossiers en erreur peuvent etre relances")

    # Reset status
    await db.dossier_express.update_one({"id": dossier_id}, {"$set": {
        "status": "processing",
        "delivery_status": "en_attente_traitement",
        "processing_step": "relance_admin",
        "error": None,
        "retry_count": (dossier.get("retry_count", 0) + 1),
        "last_retry_at": datetime.now(timezone.utc).isoformat(),
        "retried_by": admin.get("email", "admin"),
    }})

    # Re-launch processing
    asyncio.create_task(_process_dossier_express(
        dossier_id,
        dossier.get("email", ""),
        dossier.get("name", ""),
        dossier.get("situation", ""),
        dossier.get("type_dossier", ""),
        dossier.get("regime", ""),
        dossier.get("documents_text", ""),
        premium_pdf=dossier.get("premium_pdf", False),
        improvement_optout=dossier.get("improvement_optout", False),
    ))

    logger.info(f"Admin retry launched for dossier {dossier_id} by {admin.get('email')}")
    return {"success": True, "message": "Relance en cours"}

@router.post("/dossier-express/admin-bypass")
async def dossier_express_admin_bypass(request: Request):
    """Admin bypass: skips Stripe checkout and runs Dossier Express pipeline directly for testing."""
    import jwt as pyjwt
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="Non autorise")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")

    body = await request.json()
    situation = body.get("situation", "")
    name = body.get("name", "Admin Test")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    documents_text = body.get("documents_text", "")
    premium_pdf = body.get("premium_pdf", False)
    improvement_optout = body.get("improvement_optout", False)
    email = payload.get("email", "admin@test")

    if not situation.strip():
        raise HTTPException(status_code=400, detail="Situation requise")
    if not _has_llm_key():
        raise HTTPException(status_code=503, detail="Service IA non disponible")

    dossier_id = str(uuid.uuid4())[:12]
    dossier_entry = {
        "id": dossier_id,
        "email": email,
        "name": name,
        "situation": situation,
        "type_dossier": type_dossier,
        "regime": regime,
        "documents_text": documents_text,
        "status": "processing",
        "delivery_status": "en_attente_traitement",
        "processing_step": "checkout_valide",
        "premium_pdf": premium_pdf,
        "admin_test": True,
        "improvement_optout": improvement_optout,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.dossier_express.insert_one(dossier_entry)

    # Launch async pipeline
    asyncio.create_task(_process_dossier_express(
        dossier_id, email, name, situation, type_dossier, regime, documents_text, premium_pdf=premium_pdf, improvement_optout=improvement_optout
    ))

    logger.info(f"[DOSSIER_EXPRESS][admin-bypass][{dossier_id}] Pipeline lance par {email}")
    return {"dossier_id": dossier_id, "status": "processing", "admin_test": True}


@router.get("/dossier-express/weekly-count")
async def dossier_express_weekly_count():
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    real_count = await db.dossier_express.count_documents({"created_at": {"$gte": week_start}})
    setting = await db.site_settings.find_one({"id": "dossiers_weekly_base"}, {"_id": 0})
    base = setting.get("value", 12) if setting else 12
    display_count = base + real_count
    return {"count": display_count, "period": "week"}

