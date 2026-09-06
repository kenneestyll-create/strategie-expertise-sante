"""SEUL E2E post-fix — dossier réel 108 pages via la chaîne de production modifiée. Un seul run."""
import asyncio, base64, json, sys, time

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

OUT = "/app/memory/benchmarks/LONGCTX_2026-09-06"


async def main():
    from routes.dossier_express import _process_files_payload, _process_dossier_express
    from config import db
    import uuid
    from datetime import datetime, timezone

    with open(f"{OUT}/dossier_108p.pdf", "rb") as f:
        raw = f.read()
    files_data = [{"name": "Rapport d'analyse medical OCR-page numerote.pdf",
                   "type": "application/pdf", "data": base64.b64encode(raw).decode()}]
    t0 = time.monotonic()
    res = await _process_files_payload(files_data, source_type="test")
    t_extract = round(time.monotonic() - t0, 1)
    docs = res["extracted_text"]
    d0 = res["details"][0]
    print("EXTRACTION", json.dumps({"duree_s": t_extract, "chars": len(docs),
          "method": d0["method"], "status": d0["status"], "pages": d0["pages"]}, ensure_ascii=False))
    with open(f"{OUT}/texte_extrait_postfix.txt", "w") as f:
        f.write(docs)

    dossier_id = "testfix-" + str(uuid.uuid4())[:5]
    situation = ("Je conteste les conclusions de l'expertise medicale me concernant. "
                 "Je transmets l'integralite de mon dossier medical (rapport d'expertise de 108 pages) "
                 "pour analyse complete : identification des points contestables, coherence des evaluations, "
                 "et strategie de recours.")
    entry = {"id": dossier_id, "session_id": "test_fix", "email": "delivered@resend.dev",
             "name": "TEST FIX LONGCTX", "situation": situation,
             "type_dossier": "contestation_expertise", "regime": "regime_general",
             "documents_text": docs, "document_details": res["details"], "original_documents": [],
             "status": "processing", "delivery_status": "en_attente_traitement",
             "processing_step": "checkout_valide", "premium_pdf": False, "payment_verified": False,
             "source_type": "test", "improvement_optout": False,
             "created_at": datetime.now(timezone.utc).isoformat()}
    await db.dossier_express.insert_one(entry)
    t0 = time.monotonic()
    await _process_dossier_express(dossier_id, entry["email"], entry["name"], situation,
                                   "contestation_expertise", "regime_general", docs,
                                   premium_pdf=False, improvement_optout=False)
    t_pipe = round(time.monotonic() - t0, 1)
    doc = await db.dossier_express.find_one({"id": dossier_id})
    analysis = doc.get("analysis", "") or ""
    with open(f"{OUT}/rapport_POSTFIX.md", "w") as f:
        f.write(analysis)
    print("PIPELINE", json.dumps({"dossier_id": dossier_id, "duree_s": t_pipe,
          "status": doc.get("status"), "delivery": doc.get("delivery_status"),
          "timings": doc.get("timings"), "chars_rapport": len(analysis),
          "sections": analysis.count("### ")}, ensure_ascii=False, default=str))

    # Tokens réels du payload exact (count_tokens Anthropic) — aucun appel de génération
    import anthropic, os
    from constants.prompts import DOSSIER_EXPRESS_SYSTEM_PROMPT, DOSSIER_EXPRESS_PROMPT
    from routes.knowledge_patterns import get_knowledge_patterns_context
    enhanced = DOSSIER_EXPRESS_SYSTEM_PROMPT
    try:
        kc = await get_knowledge_patterns_context(categorie="contestation_expertise", metier="regime_general",
                                                  type_sinistre="contestation_expertise", type_garantie="regime_general",
                                                  blocage=None, situation_text=situation)
        if kc:
            enhanced = DOSSIER_EXPRESS_SYSTEM_PROMPT + kc
    except Exception:
        pass
    user_msg = f"""DOSSIER EXPRESS IA - Analyse complete demandee

Client : TEST FIX LONGCTX
Type de dossier : contestation_expertise
Regime : regime_general

DESCRIPTION DE LA SITUATION :
{situation}

CONTENU DES DOCUMENTS FOURNIS :
{docs[:800000]}

{DOSSIER_EXPRESS_PROMPT}"""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=120.0)
    ct = client.messages.count_tokens(model="claude-sonnet-5", system=enhanced,
                                      messages=[{"role": "user", "content": user_msg}])
    ot = client.messages.count_tokens(model="claude-sonnet-5",
                                      messages=[{"role": "user", "content": analysis or "x"}])
    print("TOKENS", json.dumps({"chars_transmis": min(len(docs), 800000),
          "input_tokens": ct.input_tokens, "output_tokens_approx": ot.input_tokens,
          "cout_llm_usd": round(ct.input_tokens/1e6*2 + ot.input_tokens/1e6*10, 4)}))
    print("DONE")

asyncio.run(main())
