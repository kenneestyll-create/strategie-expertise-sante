"""LOT 1 PHASE B — Écran qualité documentaire client (backend part).

Covers:
- POST /api/extract-document-text with clean PDF (expects quality_report with pages_ok=3, Excellent).
- Same endpoint with degraded PDF (some pages 'x') → pages_unusable>0.
- POST /api/dossier-express/admin-bypass with quality_choice/quality_summary → 200, log [QUALITY-CHOICE],
  Mongo document stores quality_choice/quality_summary.
"""
import base64
import io
import os
import re
import time

import pytest
import requests
from fpdf import FPDF
from pymongo import MongoClient

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


def _make_pdf(pages_content):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    for content in pages_content:
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, content)
    out = pdf.output(dest="S")
    if isinstance(out, str):
        out = out.encode("latin-1")
    return bytes(out)


CLEAN_TEXT = (
    "Rapport medical du patient concernant sa situation professionnelle actuelle. "
    "Le patient exerce en qualite de cadre depuis 15 ans et rencontre des difficultes "
    "importantes liees a une pathologie chronique qui limite son activite quotidienne. "
    "Les traitements engages n'ont pas permis une amelioration significative de son etat "
    "et une reconnaissance MDPH est envisagee afin d'obtenir des amenagements de poste ainsi "
    "qu'une compensation adaptee au regime general de la securite sociale."
)


@pytest.fixture(scope="session")
def clean_pdf_b64():
    data = _make_pdf([CLEAN_TEXT, CLEAN_TEXT + " Deuxieme page.", CLEAN_TEXT + " Troisieme page."])
    return base64.b64encode(data).decode()


@pytest.fixture(scope="session")
def degraded_pdf_b64():
    # 3 pages OK + 1 page 'x' → 75% readable, stays in pdfplumber (>=60%)
    data = _make_pdf([CLEAN_TEXT, CLEAN_TEXT + " P2", CLEAN_TEXT + " P3", "x"])
    return base64.b64encode(data).decode()


@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(
        f"{API}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    token = r.json().get("access_token") or r.json().get("token")
    assert token, f"No token in login response: {r.json()}"
    return token


def _extract_with_polling(files_payload, timeout=180):
    r = requests.post(f"{API}/extract-document-text", json={"files": files_payload}, timeout=60)
    assert r.status_code == 200, f"extract-document-text failed: {r.status_code} {r.text[:500]}"
    data = r.json()
    if not data.get("async"):
        return data
    extraction_id = data["extraction_id"]
    start = time.time()
    while time.time() - start < timeout:
        pr = requests.get(f"{API}/upload/extract-status/{extraction_id}", timeout=30)
        assert pr.status_code == 200, f"poll failed {pr.status_code}"
        pd = pr.json()
        if pd.get("status") == "done":
            return pd
        if pd.get("status") == "error":
            pytest.fail(f"Extraction error: {pd}")
        time.sleep(3)
    pytest.fail("Extraction polling timed out")


class TestExtractQuality:
    def test_clean_pdf_quality_report_excellent(self, clean_pdf_b64):
        payload = [{"name": "clean.pdf", "type": "application/pdf", "data": clean_pdf_b64}]
        result = _extract_with_polling(payload)
        qr = result.get("quality_report")
        assert qr is not None, f"quality_report missing. Keys: {list(result.keys())}"
        assert qr["pages_total"] == 3, f"pages_total={qr['pages_total']} expected 3"
        assert qr["pages_ok"] == 3, f"pages_ok={qr['pages_ok']} expected 3 | qr={qr}"
        assert qr["pages_unusable"] == 0
        assert qr["confidence_level"] == "Excellent", f"level={qr['confidence_level']}"

    def test_degraded_pdf_quality_report_unusable(self, degraded_pdf_b64):
        payload = [{"name": "degraded.pdf", "type": "application/pdf", "data": degraded_pdf_b64}]
        result = _extract_with_polling(payload)
        qr = result.get("quality_report")
        assert qr is not None
        assert qr["pages_total"] == 4
        assert qr["pages_unusable"] >= 1, f"expected >=1 unusable page, got qr={qr}"
        assert qr["confidence_level"] in ("Bon", "Moyen", "Faible", "Élevé"), qr["confidence_level"]
        # per_document unusable_pages should point to page 4
        per_doc = qr.get("per_document") or []
        assert per_doc, f"per_document empty: {qr}"
        unusable_pages = per_doc[0].get("unusable_pages") or []
        assert 4 in unusable_pages or any(p >= 3 for p in unusable_pages), \
            f"unusable_pages={unusable_pages}"


class TestAdminBypassQualityChoice:
    def test_admin_bypass_records_quality_choice(self, admin_token):
        payload = {
            "situation": "Situation de test admin bypass avec un texte suffisant pour valider (plus de vingt caracteres).",
            "name": "TEST Quality Gate",
            "email": "test-quality-gate@example.com",
            "type_dossier": "MDPH",
            "regime": "general",
            "documents_text": "Contenu texte des documents extraits pour test admin bypass quality choice.",
            "quality_choice": "continue_degraded",
            "quality_summary": {
                "confidence_score": 50,
                "confidence_level": "Moyen",
                "pages_total": 4,
                "pages_unusable": 2,
                "pages_ok": 2,
                "pages_partial": 0,
                "alerts": [],
                "per_document": [],
            },
        }
        r = requests.post(
            f"{API}/dossier-express/admin-bypass",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=30,
        )
        assert r.status_code == 200, f"admin-bypass failed: {r.status_code} {r.text[:500]}"
        data = r.json()
        dossier_id = data.get("dossier_id")
        assert dossier_id, f"dossier_id missing: {data}"

        # Verify Mongo persistence
        mongo_url = os.environ["MONGO_URL"]
        db_name = os.environ["DB_NAME"]
        client = MongoClient(mongo_url)
        doc = client[db_name].dossier_express.find_one({"id": dossier_id})
        assert doc is not None, f"dossier {dossier_id} not found in Mongo"
        assert doc.get("quality_choice") == "continue_degraded"
        qs = doc.get("quality_summary") or {}
        assert qs.get("confidence_level") == "Moyen"
        assert qs.get("pages_unusable") == 2
        client.close()

        # Verify log line [QUALITY-CHOICE]
        time.sleep(1)
        log_paths = [
            "/var/log/supervisor/backend.out.log",
            "/var/log/supervisor/backend.err.log",
        ]
        found = False
        for lp in log_paths:
            if not os.path.exists(lp):
                continue
            with open(lp, "r", errors="ignore") as f:
                content = f.read()
            pattern = rf"\[QUALITY-CHOICE\]\[{re.escape(dossier_id)}\].*continue_degraded"
            if re.search(pattern, content):
                found = True
                break
        assert found, f"[QUALITY-CHOICE] log line not found for {dossier_id}"
