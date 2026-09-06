"""Test E2E post-migration : exécute le code de PRODUCTION migré (utils.llm.llm_call)
avec les mêmes entrées que le benchmark. + test du fallback proxy migré."""
import asyncio, json, sys, time

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

OUT_DIR = "/app/memory/benchmarks/SONNET5_2026-09-06"

with open(f"{OUT_DIR}/documents_text.txt") as f:
    documents_text = f.read()
from tests.benchmark_sonnet5_vs_45 import build_prompts  # noqa
system, user_msg = build_prompts(documents_text)


async def main():
    from utils.llm import llm_call, llm_stream_call
    from config import ANTHROPIC_API_KEY

    # 1. Voie NATIVE de production (exactement l'appel de dossier_express.py l.626)
    t0 = time.monotonic()
    text = await llm_call(ANTHROPIC_API_KEY, "e2e_migration_test", system, user_msg,
                          "anthropic", "claude-sonnet-5", max_tokens=8000)
    t_native = round(time.monotonic() - t0, 1)
    with open(f"{OUT_DIR}/rapport_E2E_prod.md", "w") as f:
        f.write(text)
    complete = text.rstrip().endswith((".", "»", "!", "?")) and "13" in text[-4000:]
    print(json.dumps({"voie": "native_prod", "temps_s": t_native, "chars": len(text),
                      "fin_propre": complete, "sections": text.count("### ")}, ensure_ascii=False))

    # 2. Voie FALLBACK proxy migrée (llm_stream_call avec thinking disabled auto)
    t0 = time.monotonic()
    fb = await llm_stream_call(
        [{"role": "system", "content": "Tu es un assistant juridique."},
         {"role": "user", "content": "En 3 phrases, quel est le délai de saisine de la CRA après un refus CPAM ?"}],
        "claude-sonnet-5", max_tokens=500)
    print(json.dumps({"voie": "fallback_proxy", "temps_s": round(time.monotonic() - t0, 1),
                      "chars": len(fb), "extrait": fb[:150]}, ensure_ascii=False))

asyncio.run(main())
