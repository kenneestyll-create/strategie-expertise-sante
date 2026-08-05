"""Phase A — Jeu de tests des 5 profils documentaires + mesures réelles (temps, mémoire, échecs).
Exécution directe de _process_files_payload (même code que la prod, sans HTTP)."""
import asyncio, base64, io, json, os, time, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from fpdf import FPDF
from PIL import Image, ImageDraw
import random

PARA = ("Le rapport d'expertise medicale du 12 mars 2026 conclut a une consolidation avec un taux "
        "d'incapacite permanente partielle de 8 pour cent. Le certificat du medecin traitant du 2 avril 2026 "
        "atteste de soins en cours et d'une limitation fonctionnelle de l'epaule droite. La notification CPAM "
        "du 15 avril 2026 fixe la date de consolidation au 12 mars 2026. ") * 3


def pdf_text(pages_content):
    pdf = FPDF()
    for content in pages_content:
        pdf.add_page()
        pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 6, content)
    return bytes(pdf.output())


def noise_image(w=800, h=1100, caption=None):
    img = Image.new("RGB", (w, h), "white")
    px = img.load()
    rnd = random.Random(42)
    for _ in range(int(w * h * 0.25)):
        x, y = rnd.randrange(w), rnd.randrange(h)
        g = rnd.randrange(0, 130)
        px[x, y] = (g, g, g)
    if caption:
        ImageDraw.Draw(img).text((60, 60), caption, fill=(20, 20, 20))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=40)
    return buf.getvalue()


def pdf_with_images(text_pages, image_pages):
    pdf = FPDF()
    for content in text_pages:
        pdf.add_page()
        pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 6, content)
    for img_bytes in image_pages:
        pdf.add_page()
        tmp = f"/tmp/_qa_img_{id(img_bytes)}.jpg"
        open(tmp, "wb").write(img_bytes)
        pdf.image(tmp, x=5, y=5, w=200)
        os.unlink(tmp)
    return bytes(pdf.output())


PROFILES = {
    "A_parfait_5p": pdf_text([f"Page {i+1}. {PARA}" for i in range(5)]),
    "B_mediocre_6p": pdf_text([f"Page {i+1}. {PARA}" for i in range(4)] + ["ok", "x"]),
    "C_degrade_3p": pdf_with_images([f"Rapport d'expertise. {PARA}"], [noise_image(caption="Certificat medical - Dr Martin"), noise_image()]),
    "D_incomplet_1p": pdf_text(["Certificat medical isole du 3 mai 2026. Patient suivi pour lombalgie chronique. " * 3]),
    "E_volumineux_20p": pdf_text([f"Page {i+1}. {PARA}" for i in range(20)]),
}


async def main():
    import psutil
    from routes.dossier_express import _process_files_payload
    proc = psutil.Process()
    report = {}
    for name, pdf_bytes in PROFILES.items():
        payload = [{"name": f"{name}.pdf", "type": "application/pdf", "data": base64.b64encode(pdf_bytes).decode()}]
        mem_before = proc.memory_info().rss / 1024 / 1024
        t0 = time.time()
        try:
            result = await _process_files_payload(payload)
            elapsed = round(time.time() - t0, 2)
            mem_after = proc.memory_info().rss / 1024 / 1024
            qr = result.get("quality_report") or {}
            report[name] = {
                "elapsed_s": elapsed,
                "mem_delta_mb": round(mem_after - mem_before, 1),
                "extraction_status": [d["status"] for d in result["details"]],
                "extracted_chars": len(result.get("extracted_text", "")),
                "qr_pages_total": qr.get("pages_total"),
                "qr_ok": qr.get("pages_ok"),
                "qr_partial": qr.get("pages_partial"),
                "qr_unusable": qr.get("pages_unusable"),
                "qr_score": qr.get("confidence_score"),
                "qr_level": qr.get("confidence_level"),
                "qr_per_doc": [{k: d[k] for k in ("pages_total", "pages_ok", "partial_pages", "unusable_pages")} for d in qr.get("per_document", [])],
                "legacy_fields_intact": all(k in result for k in ("extracted_text", "files_processed", "details", "stored_files")),
            }
        except Exception as e:
            report[name] = {"FAILED": f"{type(e).__name__}: {e}", "elapsed_s": round(time.time() - t0, 2)}
        print(f"=== {name} ===\n{json.dumps(report[name], ensure_ascii=False, indent=1)}\n", flush=True)
    failures = sum(1 for r in report.values() if "FAILED" in r)
    print(f"\nRESULT: {len(report) - failures}/{len(report)} profils OK, {failures} echec(s)")
    json.dump(report, open("/tmp/phase_a_results.json", "w"), ensure_ascii=False, indent=1)

asyncio.run(main())
