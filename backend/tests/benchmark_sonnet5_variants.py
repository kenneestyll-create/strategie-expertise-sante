"""Benchmark complément : Sonnet 5 sans thinking (drop-in) + Sonnet 5 thinking 16k.
Réutilise documents_text.txt du run initial (entrées STRICTEMENT identiques)."""
import asyncio, json, os, sys, time

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

OUT_DIR = "/app/memory/benchmarks/SONNET5_2026-09-06"

with open(f"{OUT_DIR}/documents_text.txt") as f:
    documents_text = f.read()

from tests.benchmark_sonnet5_vs_45 import build_prompts, SITUATION  # noqa
system, user_msg = build_prompts(documents_text)

VARIANTS = [
    ("sonnet_5_nothink", "claude-sonnet-5", {"thinking": {"type": "disabled"}}, 8000),
    ("sonnet_5_think16k", "claude-sonnet-5", {}, 16000),
]


def run(label, model_id, extra, max_tokens):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=600.0)
    t0 = time.monotonic()
    parts = []
    with client.messages.stream(
        model=model_id, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": user_msg}], **extra,
    ) as stream:
        for chunk in stream.text_stream:
            parts.append(chunk)
        final = stream.get_final_message()
    elapsed = round(time.monotonic() - t0, 1)
    text = "".join(parts)
    u = final.usage
    details = getattr(u, "output_tokens_details", None)
    thinking = getattr(details, "thinking_tokens", None) if details else None
    res = {"model": model_id, "variant": label, "elapsed_s": elapsed,
           "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
           "thinking_tokens": thinking, "chars": len(text), "stop_reason": final.stop_reason,
           "cost_usd": round(u.input_tokens / 1e6 * 2.0 + u.output_tokens / 1e6 * 10.0, 4)}
    with open(f"{OUT_DIR}/rapport_{label}.md", "w") as f:
        f.write(text)
    print(json.dumps(res, ensure_ascii=False))
    return res


results = [run(*v) for v in VARIANTS]
with open(f"{OUT_DIR}/metrics_variants.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("DONE")
