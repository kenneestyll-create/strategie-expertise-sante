"""Test de charge raisonnable — extractions simultanées via l'API réelle (texte natif, 0 coût LLM)."""
import asyncio, base64, json, os, time, statistics
import httpx, psutil

API = open("/app/frontend/.env").read().split("REACT_APP_BACKEND_URL=")[1].splitlines()[0].strip()
CORPUS = "/app/backend/tests/corpus"


def payload(name):
    data = base64.b64encode(open(f"{CORPUS}/{name}", "rb").read()).decode()
    return {"files": [{"name": name, "type": "application/pdf", "data": data}]}


async def one_request(client, name, idx):
    t0 = time.time()
    r = await client.post(f"{API}/api/extract-document-text", json=payload(name), timeout=120)
    body = r.json()
    if body.get("async"):
        eid = body["extraction_id"]
        for _ in range(40):
            await asyncio.sleep(3)
            s = (await client.get(f"{API}/api/upload/extract-status/{eid}", timeout=30)).json()
            if s.get("status") in ("done", "error"):
                body = s
                break
    qr = body.get("quality_report") or {}
    return {"idx": idx, "file": name, "http": r.status_code, "elapsed_s": round(time.time() - t0, 1),
            "status": body.get("status", "sync"), "score": qr.get("confidence_score"), "level": qr.get("confidence_level")}


async def main():
    backend_pid = None
    for p in psutil.process_iter(["pid", "cmdline"]):
        cmd = " ".join(p.info["cmdline"] or [])
        if "uvicorn" in cmd and "8001" in cmd:
            backend_pid = p.info["pid"]
            break
    mem_before = psutil.Process(backend_pid).memory_info().rss / 1024 / 1024 if backend_pid else None

    jobs = [("R1_complet_lisible.pdf", 1), ("R2_volumineux.pdf", 2), ("R5_qualite_variable.pdf", 3),
            ("R3a_expertise.pdf", 4), ("R1_complet_lisible.pdf", 5), ("R2_volumineux.pdf", 6)]
    async with httpx.AsyncClient() as client:
        t0 = time.time()
        results = await asyncio.gather(*[one_request(client, n, i) for n, i in jobs], return_exceptions=True)
        total = round(time.time() - t0, 1)

    mem_after = psutil.Process(backend_pid).memory_info().rss / 1024 / 1024 if backend_pid else None
    ok = [r for r in results if isinstance(r, dict) and r["http"] == 200]
    times = [r["elapsed_s"] for r in ok]
    print(json.dumps({
        "simultaneous_requests": len(jobs), "success": len(ok), "failures": len(jobs) - len(ok),
        "total_wall_s": total, "avg_s": round(statistics.mean(times), 1) if times else None,
        "max_s": max(times) if times else None,
        "backend_mem_before_mb": round(mem_before, 1) if mem_before else "n/a",
        "backend_mem_after_mb": round(mem_after, 1) if mem_after else "n/a",
        "details": [r if isinstance(r, dict) else str(r) for r in results],
    }, ensure_ascii=False, indent=1))

asyncio.run(main())
