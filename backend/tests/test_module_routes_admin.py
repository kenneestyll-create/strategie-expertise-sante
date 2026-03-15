"""Tests for routes/admin.py — admin auth + dashboard endpoints."""
import pytest
import uuid

API = "/api"


class TestAdminAuth:
    def test_login_success(self, client):
        resp = client.post(f"{API}/auth/login", json={
            "email": "admin@accompagn-sante.fr", "password": "Admin2024!"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["admin_name"] == "Administrateur"

    def test_login_wrong_email(self, client):
        resp = client.post(f"{API}/auth/login", json={
            "email": "wrong@test.com", "password": "Admin2024!"
        })
        assert resp.status_code == 401

    def test_login_wrong_password(self, client):
        resp = client.post(f"{API}/auth/login", json={
            "email": "admin@accompagn-sante.fr", "password": "wrong"
        })
        assert resp.status_code == 401

    def test_auth_me(self, client, admin_headers):
        resp = client.get(f"{API}/auth/me", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "admin@accompagn-sante.fr"

    def test_protected_route_no_token(self, client):
        resp = client.get(f"{API}/admin/stats")
        assert resp.status_code == 403

    def test_protected_route_invalid_token(self, client):
        resp = client.get(f"{API}/admin/stats", headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401


class TestAdminContacts:
    def test_list_contacts(self, client, admin_headers):
        resp = client.get(f"{API}/admin/contacts", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_filter_by_status(self, client, admin_headers):
        resp = client.get(f"{API}/admin/contacts?status=nouveau", headers=admin_headers)
        assert resp.status_code == 200

    def test_get_stats(self, client, admin_headers):
        resp = client.get(f"{API}/admin/stats", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        for key in ("total", "nouveau", "en_cours", "traite"):
            assert key in data


class TestAdminAnalytics:
    def test_analytics_30d(self, client, admin_headers):
        resp = client.get(f"{API}/admin/analytics?period=30d", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "kpis" in data
        assert "time_series" in data
        assert "packages" in data
        kpis = data["kpis"]
        for key in ("total_contacts", "total_clients", "total_revenue", "conversion_rate"):
            assert key in kpis

    def test_analytics_7d(self, client, admin_headers):
        resp = client.get(f"{API}/admin/analytics?period=7d", headers=admin_headers)
        assert resp.status_code == 200

    def test_analytics_time_series_sorted(self, client, admin_headers):
        resp = client.get(f"{API}/admin/analytics?period=30d", headers=admin_headers)
        ts = resp.json()["time_series"]
        dates = [t["date"] for t in ts]
        assert dates == sorted(dates)


class TestAdminFAQ:
    def test_create_and_delete_faq(self, client, admin_headers):
        resp = client.post(f"{API}/admin/faq", json={
            "question": "Pytest FAQ?", "reponse": "Pytest answer.", "categorie": "Test"
        }, headers=admin_headers)
        assert resp.status_code == 200
        faq_id = resp.json()["id"]

        resp2 = client.delete(f"{API}/admin/faq/{faq_id}", headers=admin_headers)
        assert resp2.status_code == 200


class TestAdminAvis:
    def test_list_avis(self, client, admin_headers):
        resp = client.get(f"{API}/admin/avis", headers=admin_headers)
        assert resp.status_code == 200

    def test_avis_stats(self, client, admin_headers):
        resp = client.get(f"{API}/admin/avis/stats", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        for key in ("total", "en_attente", "publie", "rejete"):
            assert key in data


class TestAdminClients:
    def test_list_clients(self, client, admin_headers):
        resp = client.get(f"{API}/admin/clients", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestAdminReferrals:
    def test_get_referrals(self, client, admin_headers):
        resp = client.get(f"{API}/admin/referrals", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "codes" in data
        assert "stats" in data


class TestAdminPremiumAnalyses:
    def test_list_premium(self, client, admin_headers):
        resp = client.get(f"{API}/admin/premium-analyses", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "stats" in data
