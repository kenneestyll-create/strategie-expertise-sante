"""Suite benchmark : extraction couche texte complète (mesure), tokens RUN1, RUN3 texte intégral."""
import asyncio, io, json, os, sys, time

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

OUT = "/app/memory/benchmarks/LONGCTX_2026-09-06"
NAME = "TEST LONGCTX"
SITUATION = ("Je conteste les conclusions de l'expertise medicale me concernant. "
             "Je transmets l'integralite de mon dossier medical (rapport d'expertise de 108 pages) "
             "pour analyse complete : identification des points contestables, coherence des evaluations, "
             "et strategie de recours.")
TYPE_DOSSIER = "contestation_expertise"
REGIME = "regime_general"


async def main():
    import pdfplumber
    t0 = time.monotonic()
    with open(f"{OUT}/dossier_108p.pdf", "rb") as f:
        b = f.read()
    pdf = pdfplumber.open(io.BytesIO(b))
    pages_text, readable = [], 0
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and text.strip() and len(text.strip()) > 20:
            pages_text.append(f"[Page {i+1}] {text.strip()}")
            readable += 1
    pdf.close()
    full_text = "\n\n".join(pages_text)
    t_extract = round(time.monotonic() - t0, 1)
    print(json.dumps({"couche_texte": {"pages_lisibles": readable, "pages_total": 108,
                      "chars": len(full_text), "duree_s": t_extract}}, ensure_ascii=False))
    with open(f"{OUT}/texte_couche_native_230k.txt", "w") as f:
        f.write(full_text)

    from constants.prompts import DOSSIER_EXPRESS_SYSTEM_PROMPT, DOSSIER_EXPRESS_PROMPT
    from routes.knowledge_patterns import get_knowledge_patterns_context
    enhanced = DOSSIER_EXPRESS_SYSTEM_PROMPT
    try:
        kc = await get_knowledge_patterns_context(categorie=TYPE_DOSSIER, metier=REGIME,
                                                  type_sinistre=TYPE_DOSSIER, type_garantie=REGIME,
                                                  blocage=None, situation_text=SITUATION)
        if kc:
            enhanced = DOSSIER_EXPRESS_SYSTEM_PROMPT + kc
    except Exception as e:
        print("knowledge injection:", e)

    def build_user(d):
        return f"""DOSSIER EXPRESS IA - Analyse complete demandee

Client : {NAME}
Type de dossier : {TYPE_DOSSIER}
Regime : {REGIME}

DESCRIPTION DE LA SITUATION :
{SITUATION}

CONTENU DES DOCUMENTS FOURNIS :
{d}

{DOSSIER_EXPRESS_PROMPT}"""

    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=300.0)

    # Tokens RUN 1 (payload prod réel : texte Gemini 60k, non tronqué car < 120k)
    with open(f"{OUT}/texte_extrait.txt") as f:
        docs_gemini = f.read()
    with open(f"{OUT}/rapport_RUN1_prod_120k.md") as f:
        run1_report = f.read()
    ct = client.messages.count_tokens(model="claude-sonnet-5", system=enhanced,
                                      messages=[{"role": "user", "content": build_user(docs_gemini[:120000])}])
    ot = client.messages.count_tokens(model="claude-sonnet-5",
                                      messages=[{"role": "user", "content": run1_report}])
    print(json.dumps({"run1_tokens": {"chars_docs": len(docs_gemini), "troncature_120k": len(docs_gemini) > 120000,
                      "input_tokens": ct.input_tokens, "output_tokens_approx": ot.input_tokens}}))

    # RUN 3 : texte intégral couche native (~230k chars), mêmes prompts, même config que prod
    user_full = build_user(full_text)
    t0 = time.monotonic(); ttft = None; parts = []
    with client.messages.stream(model="claude-sonnet-5", max_tokens=8000,
                                thinking={"type": "disabled"}, system=enhanced,
                                messages=[{"role": "user", "content": user_full}]) as s:
        for c in s.text_stream:
            if ttft is None:
                ttft = round(time.monotonic() - t0, 1)
            parts.append(c)
        fm = s.get_final_message()
    txt = "".join(parts)
    with open(f"{OUT}/rapport_RUN3_fulltext_230k.md", "w") as f:
        f.write(txt)
    print(json.dumps({"run3_fulltext": {"chars_docs_envoyes": len(full_text), "ttft_s": ttft,
                      "llm_s": round(time.monotonic() - t0, 1), "input_tokens": fm.usage.input_tokens,
                      "output_tokens": fm.usage.output_tokens, "stop_reason": fm.stop_reason,
                      "chars_rapport": len(txt),
                      "cost_usd": round(fm.usage.input_tokens/1e6*2 + fm.usage.output_tokens/1e6*10, 4)}}))
    print("DONE")

asyncio.run(main())
