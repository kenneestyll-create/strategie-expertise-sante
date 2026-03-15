"""Tests for routes/public.py — public endpoints."""
import pytest
import uuid

API = "/api"


class TestRootAndHealth:
    def test_root(self, client):
        resp = client.get(f"{API}/")
        assert resp.status_code == 200
        assert "Bienvenue" in resp.json()["message"]

    def test_health(self, client):
        resp = client.get(f"{API}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestContact:
    def test_create_contact(self, client):
        resp = client.post(f"{API}/contact", json={
            "nom": "TestPytest", "prenom": "Auto", "email": f"pytest-{uuid.uuid4().hex[:6]}@test.com",
            "sujet": "Test automatisé", "message": "Ceci est un test pytest."
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "id" in data

    def test_create_contact_with_optional(self, client):
        resp = client.post(f"{API}/contact", json={
            "nom": "Test", "prenom": "Tel", "email": "t@t.com",
            "telephone": "0612345678", "sujet": "Test",
            "message": "Msg", "type_accompagnement": "AT"
        })
        assert resp.status_code == 200

    def test_create_contact_missing_fields(self, client):
        resp = client.post(f"{API}/contact", json={"nom": "Test"})
        assert resp.status_code == 422


class TestFAQ:
    def test_get_faq(self, client):
        resp = client.get(f"{API}/faq")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        for item in data:
            assert "question" in item
            assert "reponse" in item

    def test_faq_by_category(self, client):
        resp = client.get(f"{API}/faq/category/AT%2FMP")
        assert resp.status_code == 200


class TestAvis:
    def test_get_avis(self, client):
        resp = client.get(f"{API}/avis")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_avis(self, client):
        resp = client.post(f"{API}/avis", json={
            "nom": "PyTestUser", "note": 4, "commentaire": "Très bon service pytest."
        })
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_avis_invalid_note(self, client):
        resp = client.post(f"{API}/avis", json={
            "nom": "X", "note": 10, "commentaire": "Invalid"
        })
        assert resp.status_code == 422


class TestVisitors:
    def test_get_count(self, client):
        resp = client.get(f"{API}/visitors/count")
        assert resp.status_code == 200
        assert "count" in resp.json()

    def test_increment(self, client):
        resp = client.post(f"{API}/visitors/increment")
        assert resp.status_code == 200
        assert "count" in resp.json()


class TestReferral:
    def test_create_referral(self, client):
        email = f"pytest-ref-{uuid.uuid4().hex[:6]}@test.com"
        resp = client.post(f"{API}/referral/create", json={"email": email})
        assert resp.status_code == 200
        assert "code" in resp.json()

    def test_validate_invalid_code(self, client):
        resp = client.get(f"{API}/referral/validate/INVALIDCODE999")
        assert resp.status_code == 200
        assert resp.json()["valid"] is False

    def test_client_discount_new(self, client):
        resp = client.get(f"{API}/client/discount/newemail@test.com")
        assert resp.status_code == 200
        assert resp.json()["loyalty_discount"] == 0
