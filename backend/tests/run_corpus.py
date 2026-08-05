"""RUNNER DE NON-RÉGRESSION — corpus permanent Dossier Express IA.
Passe chaque dossier du corpus dans le pipeline réel (_process_files_payload),
compare aux attentes humaines (EXPECTATIONS) et liste faux positifs / faux négatifs.
Usage : cd /app/backend && python3 tests/run_corpus.py [--only R1,D5]"""
import asyncio, base64, json, os, sys, time

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND)
from dotenv import load_dotenv
load_dotenv(os.path.join(BACKEND, ".env"))

from tests.build_corpus import build_corpus, CORPUS_DIR

# Attente humaine par dossier : pages problématiques attendues (partial+unusable), niveau minimal/maximal
EXPECTATIONS = {
    # nom : {pages, bad_expected: [pages problématiques attendues], level_in: niveaux acceptables, note}
    "R1_complet_lisible.pdf": {"pages": 4, "bad_expected": [], "level_in": ["Excellent"], "essential": True},
    "R2_volumineux.pdf": {"pages": 30, "bad_expected": [], "level_in": ["Excellent"], "essential": True},
    "R3_multi_pieces": {"files": ["R3a_expertise.pdf", "R3b_certificat.pdf", "R3c_notification.pdf", "R3d_courrier.pdf"],
                         "pages": 5, "bad_expected": [], "level_in": ["Excellent"], "essential": True},
    "R4_pieces_manquantes.pdf": {"pages": 1, "bad_expected": [], "level_in": ["Excellent"],
                                  "note": "Qualité OK attendue — la détection de pièce MANQUANTE relève de SF5 (Phase D), hors périmètre qualité"},
    "R5_qualite_variable.pdf": {"pages": 5, "bad_expected": [2, 4], "level_in": ["Moyen", "Bon"], "essential": True},
    "D1_flou_fort.pdf": {"pages": 1, "bad_expected": "tolerant", "level_in": ["Excellent", "Élevé", "Bon", "Moyen", "Faible"],
                          "note": "Si Gemini lit le texte malgré le flou → OK est correct (exploitabilité, pas esthétique)"},
    "D2_page_coupee.pdf": {"pages": 1, "bad_expected": "tolerant", "level_in": ["Excellent", "Élevé", "Bon", "Moyen", "Faible"],
                            "note": "Texte partiellement perdu — partial attendu si extraction incomplète"},
    "D3_contraste_faible.pdf": {"pages": 1, "bad_expected": [1], "level_in": ["Moyen", "Faible"],
                                 "note": "Contraste 8 % — extraction attendue impossible ou très partielle"},
    "D4_rotation_90.pdf": {"pages": 1, "bad_expected": "tolerant", "level_in": ["Excellent", "Élevé", "Bon", "Moyen", "Faible"],
                            "note": "Gemini lit généralement à travers la rotation → OK correct"},
    "D5_page_blanche.pdf": {"pages": 3, "bad_expected": [2], "level_in": ["Bon", "Moyen"]},
    "D6_incomplet.pdf": {"pages": 1, "bad_expected": [], "level_in": ["Excellent", "Élevé"],
                          "note": "Page lisible : qualité OK. L'incomplétude du DOSSIER relève de SF5"},
    "D7_ordre_incorrect.pdf": {"pages": 3, "bad_expected": [], "level_in": ["Excellent"],
                                "note": "LIMITE DOCUMENTÉE : l'ordre des pages n'est pas détectable par le module qualité (Lot 2, fiche structurée)"},
    "D8_ocr_partiel.pdf": {"pages": 2, "bad_expected": [2], "level_in": ["Bon", "Moyen", "Élevé"],
                            "note": "Page 1 nette, page 2 bruitée+floue → page 2 partial/unusable attendue"},
}


def _payload(names):
    files = []
    for n in names:
        data = open(os.path.join(CORPUS_DIR, n), "rb").read()
        files.append({"name": n, "type": "application/pdf", "data": base64.b64encode(data).decode()})
    return files


async def main():
    import psutil
    from routes.dossier_express import _process_files_payload
    build_corpus()
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].split(",")

    proc = psutil.Process()
    results, fp_total, fn_total = {}, 0, 0
    for key, exp in EXPECTATIONS.items():
        if only and not any(key.startswith(o) for o in only):
            continue
        names = exp.get("files", [key])
        t0 = time.time()
        mem0 = proc.memory_info().rss / 1024 / 1024
        try:
            out = await _process_files_payload(_payload(names))
            qr = out.get("quality_report") or {}
            elapsed = round(time.time() - t0, 1)
            bad_detected = sorted(set(
                p["page"] for p in qr.get("pages", []) if p["exploitability"] != "ok"
            )) if len(names) == 1 else [
                f"{d['name']}:{p}" for d in qr.get("per_document", []) for p in d["partial_pages"] + d["unusable_pages"]
            ]
            fp = fn = "n/a (tolérant)"
            if isinstance(exp["bad_expected"], list):
                expected = set(exp["bad_expected"])
                detected = set(bad_detected) if len(names) == 1 else set()
                fp = sorted(detected - expected)
                fn = sorted(expected - detected)
                fp_total += len(fp)
                fn_total += len(fn)
            level_ok = qr.get("confidence_level") in exp["level_in"]
            results[key] = {
                "pages_total": qr.get("pages_total"), "pages_attendues": exp["pages"],
                "pages_problematiques_detectees": bad_detected,
                "score": qr.get("confidence_score"), "niveau": qr.get("confidence_level"),
                "niveau_conforme_attente": level_ok, "alerts": qr.get("alerts"),
                "faux_positifs": fp, "faux_negatifs": fn,
                "temps_s": elapsed, "mem_delta_mb": round(proc.memory_info().rss / 1024 / 1024 - mem0, 1),
                "statuses": [d["status"] for d in out.get("details", [])],
                "note": exp.get("note", ""),
            }
        except Exception as e:
            results[key] = {"FAILED": f"{type(e).__name__}: {e}"}
        print(f"=== {key} ===\n{json.dumps(results[key], ensure_ascii=False, indent=1)}\n", flush=True)

    failures = sum(1 for r in results.values() if "FAILED" in r)
    conform = sum(1 for r in results.values() if r.get("niveau_conforme_attente"))
    print(f"\nBILAN: {len(results)} dossiers | {failures} échec(s) technique(s) | "
          f"{conform}/{len(results) - failures} niveaux conformes | FP={fp_total} FN={fn_total}")
    json.dump(results, open("/tmp/corpus_results.json", "w"), ensure_ascii=False, indent=1)

asyncio.run(main())
