"""BENCHMARK E2E RÉEL — dossier 108 pages via la VRAIE chaîne de production (préversion = code identique prod).
AUCUNE modification de code de production. Résultats: /app/memory/benchmarks/LONGCTX_2026-09-06/
Run 1 = pipeline production tel quel (troncature éventuelle mesurée, pas contournée).
Run 2 = comparaison long contexte (texte intégral) via appel direct hors pipeline, mêmes prompts.
"""
import asyncio, base64, json, os, sys, time

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

OUT = "/app/memory/benchmarks/LONGCTX_2026-09-06"
PDF = f"{OUT}/dossier_108p.pdf"
EMAIL = "delivered@resend.dev"
NAME = "TEST LONGCTX"
SITUATION = ("Je conteste les conclusions de l'expertise medicale me concernant. "
             "Je transmets l'integralite de mon dossier medical (rapport d'expertise de 108 pages) "
             "pour analyse complete : identification des points contestables, coherence des evaluations, "
             "et strategie de recours.")
TYPE_DOSSIER = "contestation_expertise"
REGIME = "regime_general"

M = {}

async def main():
    from routes.dossier_express import _process_files_payload, _process_dossier_express
    from config import db

    # ===== PHASE 1 : EXTRACTION (vraie chaine) =====
    with open(PDF, "rb") as f:
        raw = f.read()
    files_data = [{"name": "Rapport d'analyse medical OCR-page numerote.pdf",
                   "type": "application/pdf",
                   "data": base64.b64encode(raw).decode()}]
    t0 = time.monotonic()
    res = await _process_files_payload(files_data, source_type="test")
    M["extraction_s"] = round(time.monotonic() - t0, 1)
    docs = res["extracted_text"]
    d0 = res["details"][0]
    M["extraction"] = {"pages": d0["pages"], "method": d0["method"], "status": d0["status"],
                       "chars_extraits": len(docs)}
    with open(f"{OUT}/texte_extrait.txt", "w") as f:
        f.write(docs)
    print("PHASE1", json.dumps(M, ensure_ascii=False))

    # ===== PHASE 2 : ANALYSE via _process_dossier_express (vraie fonction de prod) =====
    import uuid
    from datetime import datetime, timezone
    dossier_id = "testlc-" + str(uuid.uuid4())[:5]
    entry = {
        "id": dossier_id, "session_id": "test_longctx", "email": EMAIL, "name": NAME,
        "situation": SITUATION, "type_dossier": TYPE_DOSSIER, "regime": REGIME,
        "documents_text": docs, "document_details": res["details"], "original_documents": [],
        "status": "processing", "delivery_status": "en_attente_traitement",
        "processing_step": "checkout_valide", "premium_pdf": False, "payment_verified": False,
        "source_type": "test", "improvement_optout": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.dossier_express.insert_one(entry)
    t0 = time.monotonic()
    await _process_dossier_express(dossier_id, EMAIL, NAME, SITUATION, TYPE_DOSSIER, REGIME, docs,
                                   premium_pdf=False, improvement_optout=False)
    M["e2e_analyse_s"] = round(time.monotonic() - t0, 1)

    doc = await db.dossier_express.find_one({"id": dossier_id})
    analysis = doc.get("analysis", "") or ""
    M["run1_prod"] = {
        "dossier_id": dossier_id, "status": doc.get("status"),
        "delivery_status": doc.get("delivery_status"),
        "llm_path_used": doc.get("llm_path_used", "NON MESURÉ"),
        "timings_db": doc.get("timings", "NON MESURÉ"),
        "chars_rapport": len(analysis),
        "citation_validation": (doc.get("citation_validation") or {}).get("summary", "NON MESURÉ") if isinstance(doc.get("citation_validation"), dict) else doc.get("citation_validation", "NON MESURÉ"),
    }
    with open(f"{OUT}/rapport_RUN1_prod_120k.md", "w") as f:
        f.write(analysis)
    print("PHASE2", json.dumps(M["run1_prod"], ensure_ascii=False, default=str))

    # ===== PHASE 3 : tokens réels du payload prod (Anthropic count_tokens, mesure officielle) =====
    import anthropic
    from constants.prompts import DOSSIER_EXPRESS_SYSTEM_PROMPT
    from utils.knowledge_patterns import get_knowledge_patterns_context
    enhanced = DOSSIER_EXPRESS_SYSTEM_PROMPT
    try:
        kc = await get_knowledge_patterns_context(categorie=TYPE_DOSSIER, metier=REGIME,
                                                  type_sinistre=TYPE_DOSSIER, type_garantie=REGIME,
                                                  blocage=None, situation_text=SITUATION)
        if kc:
            enhanced = DOSSIER_EXPRESS_SYSTEM_PROMPT + kc
    except Exception:
        pass
    from constants.prompts import DOSSIER_EXPRESS_PROMPT

    def build_user(docs_slice):
        return f"""DOSSIER EXPRESS IA - Analyse complete demandee

Client : {NAME}
Type de dossier : {TYPE_DOSSIER}
Regime : {REGIME}

DESCRIPTION DE LA SITUATION :
{SITUATION}

CONTENU DES DOCUMENTS FOURNIS :
{docs_slice}

{DOSSIER_EXPRESS_PROMPT}"""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=300.0)
    user_120k = build_user(docs[:120000])
    ct1 = client.messages.count_tokens(model="claude-sonnet-5", system=enhanced,
                                       messages=[{"role": "user", "content": user_120k}])
    out1 = client.messages.count_tokens(model="claude-sonnet-5",
                                        messages=[{"role": "user", "content": analysis or "x"}])
    M["run1_tokens"] = {"chars_docs_envoyes": min(len(docs), 120000),
                        "troncature_120k": len(docs) > 120000,
                        "input_tokens_count_api": ct1.input_tokens,
                        "output_tokens_count_api": out1.input_tokens}
    print("PHASE3", json.dumps(M["run1_tokens"], ensure_ascii=False))

    # ===== PHASE 4 : RUN 2 — texte INTÉGRAL (comparaison, hors pipeline, mêmes prompts) =====
    user_full = build_user(docs)
    t0 = time.monotonic(); ttft = None; parts = []
    with client.messages.stream(model="claude-sonnet-5", max_tokens=8000,
                                thinking={"type": "disabled"}, system=enhanced,
                                messages=[{"role": "user", "content": user_full}]) as s:
        for c in s.text_stream:
            if ttft is None:
                ttft = round(time.monotonic() - t0, 1)
            parts.append(c)
        fm = s.get_final_message()
    run2_text = "".join(parts)
    M["run2_fulltext"] = {"chars_docs_envoyes": len(docs), "ttft_s": ttft,
                          "llm_s": round(time.monotonic() - t0, 1),
                          "input_tokens_api": fm.usage.input_tokens,
                          "output_tokens_api": fm.usage.output_tokens,
                          "stop_reason": fm.stop_reason, "chars_rapport": len(run2_text),
                          "cost_usd": round(fm.usage.input_tokens/1e6*2 + fm.usage.output_tokens/1e6*10, 4)}
    with open(f"{OUT}/rapport_RUN2_fulltext.md", "w") as f:
        f.write(run2_text)
    print("PHASE4", json.dumps(M["run2_fulltext"], ensure_ascii=False))

    with open(f"{OUT}/metrics_e2e.json", "w") as f:
        json.dump(M, f, ensure_ascii=False, indent=1, default=str)
    print("DONE")

asyncio.run(main())
