"""Tests for routes/strategiia.py — StrategiIA + Dossier Express + cas anonymisés."""
import pytest
import uuid

API = "/api"


class TestStrategiIAScore:
    def test_score_with_type(self, client):
        resp = client.get(f"{API}/strategiia/score?type_dossier=at")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_cases" in data
        assert "confidence" in data
        assert "distribution" in data

    def test_score_with_regime(self, client):
        resp = client.get(f"{API}/strategiia/score?type_dossier=mp&regime=general")
        assert resp.status_code == 200


class TestStrategiIAQuota:
    def test_quota_new_email(self, client):
        email = f"pytest-{uuid.uuid4().hex[:6]}@test.com"
        resp = client.get(f"{API}/strategiia/quota/{email}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["remaining"] == 3
        assert data["limit"] == 3
        assert data["used"] == 0


class TestStrategiIAEmail:
    def test_register_email(self, client):
        email = f"pytest-lead-{uuid.uuid4().hex[:6]}@test.com"
        resp = client.post(f"{API}/strategiia/register-email", json={"email": email})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["remaining"] == 3

    def test_register_invalid_email(self, client):
        resp = client.post(f"{API}/strategiia/register-email", json={"email": "invalid"})
        assert resp.status_code == 400


class TestStrategiIAAnalyze:
    def test_analyze_empty_situation(self, client):
        resp = client.post(f"{API}/strategiia/analyze", json={
            "situation": "", "type_dossier": "at"
        })
        assert resp.status_code == 400


class TestDossierExpress:
    def test_submit(self, client):
        resp = client.post(f"{API}/dossier-express/submit", json={
            "email": f"pytest-dossier-{uuid.uuid4().hex[:6]}@test.com",
            "name": "Test", "situation": "Test situation", "type_dossier": "at",
            "session_id": f"pytest-session-{uuid.uuid4().hex[:8]}"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "dossier_id" in data
        assert data["status"] == "processing"

    def test_submit_missing_fields(self, client):
        resp = client.post(f"{API}/dossier-express/submit", json={
            "email": "", "situation": ""
        })
        assert resp.status_code == 400

    def test_weekly_count(self, client):
        resp = client.get(f"{API}/dossier-express/weekly-count")
        assert resp.status_code == 200
        assert resp.json()["count"] >= 12


class TestPDFGeneration:
    def test_generate_pdf(self, client):
        resp = client.post(f"{API}/strategiia/generate-pdf", json={
            "analysis": "## Test\nContenu du rapport.",
            "type_dossier": "AT", "name": "Test User"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "pdf_base64" in data
        assert len(data["pdf_base64"]) > 100

    def test_generate_pdf_empty(self, client):
        resp = client.post(f"{API}/strategiia/generate-pdf", json={"analysis": ""})
        assert resp.status_code == 400


class TestCasAnonymises:
    def test_list_cas(self, client, admin_headers):
        resp = client.get(f"{API}/admin/cas-anonymises", headers=admin_headers)
        assert resp.status_code == 200
        assert "items" in resp.json()

    def test_crud_cas(self, client, admin_headers):
        resp = client.post(f"{API}/admin/cas-anonymises", json={
            "type_dossier": "at", "regime": "general", "duree": "6 mois",
            "strategie": "Contestation CRA", "resultat": "favorable",
            "score_pertinence": 85
        }, headers=admin_headers)
        assert resp.status_code == 200
        cas_id = resp.json()["id"]

        resp2 = client.patch(f"{API}/admin/cas-anonymises/{cas_id}", json={
            "resultat": "très favorable", "score_pertinence": 90
        }, headers=admin_headers)
        assert resp2.status_code == 200

        resp3 = client.delete(f"{API}/admin/cas-anonymises/{cas_id}", headers=admin_headers)
        assert resp3.status_code == 200

    def test_cas_stats(self, client, admin_headers):
        resp = client.get(f"{API}/admin/cas-anonymises/stats", headers=admin_headers)
        assert resp.status_code == 200
        assert "total" in resp.json()

    def test_import_cas(self, client, admin_headers):
        resp = client.post(f"{API}/admin/cas-anonymises/import", json={
            "cases": [
                {"type_dossier": "mp", "resultat": "favorable", "score_pertinence": 70},
                {"type_dossier": "at", "resultat": "défavorable", "score_pertinence": 30}
            ]
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["imported"] == 2


class TestAdminStrategiIAStats:
    def test_stats(self, client, admin_headers):
        resp = client.get(f"{API}/admin/strategiia/stats", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_analyses" in data
        assert "total_cases" in data

    def test_admin_dossier_express(self, client, admin_headers):
        resp = client.get(f"{API}/admin/dossier-express", headers=admin_headers)
        assert resp.status_code == 200
        assert "items" in resp.json()
