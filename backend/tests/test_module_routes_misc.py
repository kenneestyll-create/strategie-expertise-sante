"""Tests for routes/misc.py — booking, simulator, alerts, SEO, document validation, seed."""
import pytest
import uuid
import os

API = "/api"


class TestBooking:
    def test_get_slots(self, client):
        resp = client.get(f"{API}/bookings/slots/2026-05-01")
        assert resp.status_code == 200
        data = resp.json()
        assert data["date"] == "2026-05-01"
        assert isinstance(data["slots"], list)
        assert len(data["slots"]) > 0

    def test_create_booking(self, client):
        import random
        day = random.randint(1, 28)
        month = random.randint(8, 12)
        resp = client.post(f"{API}/bookings", json={
            "date": f"2027-{month:02d}-{day:02d}", "time_slot": "09:00",
            "name": "PyTest Booking", "email": f"booking-{uuid.uuid4().hex[:6]}@test.com"
        })
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_double_booking(self, client):
        date_slot = f"2026-07-{uuid.uuid4().hex[:2].replace('a','1').replace('b','2').replace('c','3').replace('d','4').replace('e','5').replace('f','6')[:2]}"
        data = {"date": "2026-07-20", "time_slot": "16:30", "name": "A", "email": "a@t.com"}
        resp1 = client.post(f"{API}/bookings", json=data)
        if resp1.status_code == 200:
            resp2 = client.post(f"{API}/bookings", json={**data, "name": "B", "email": "b@t.com"})
            assert resp2.status_code == 409

    def test_admin_bookings(self, client, admin_headers):
        resp = client.get(f"{API}/admin/bookings", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestSimulator:
    def test_save_result(self, client):
        resp = client.post(f"{API}/simulator/result", json={
            "answers": {"q1": "a1"}, "profile": "AT", "recommendations": ["R1"]
        })
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_admin_simulator_stats(self, client, admin_headers):
        resp = client.get(f"{API}/admin/simulator/stats", headers=admin_headers)
        assert resp.status_code == 200
        assert "total" in resp.json()


class TestCalculator:
    def test_track_usage(self, client):
        resp = client.post(f"{API}/calculator/track", json={"type": "ipp"})
        assert resp.status_code == 200

    def test_weekly_count(self, client):
        resp = client.get(f"{API}/calculator/count")
        assert resp.status_code == 200
        assert "count" in resp.json()


class TestUrgentAlerts:
    @pytest.mark.skipif(
        os.environ.get("STRIPE_API_KEY", "").endswith("emergent"),
        reason="Cle Stripe factice en preview — teste uniquement avec une vraie cle test/live",
    )
    def test_create_alert(self, client):
        resp = client.post(f"{API}/alerte-urgente", json={
            "nom": "PyTest Alert", "telephone": "0600000000",
            "email": "alert@test.com", "message": "Urgent test",
            "origin_url": "https://strategie-expertise-sante.fr"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "url" in data and "session_id" in data and "alert_id" in data

    def test_create_alert_missing_fields(self, client):
        resp = client.post(f"{API}/alerte-urgente", json={"nom": ""})
        assert resp.status_code == 400

    def test_admin_alerts(self, client, admin_headers):
        resp = client.get(f"{API}/admin/alertes-urgentes", headers=admin_headers)
        assert resp.status_code == 200
        assert "items" in resp.json()


class TestDocumentValidation:
    def test_valid_pdf(self, client):
        resp = client.post(f"{API}/documents/validate", json={
            "filename": "test.pdf", "size": 500000, "mime_type": "application/pdf"
        })
        assert resp.status_code == 200
        assert resp.json()["valid"] is True

    def test_valid_image(self, client):
        resp = client.post(f"{API}/documents/validate", json={
            "filename": "scan.jpg", "size": 200000, "mime_type": "image/jpeg"
        })
        assert resp.status_code == 200
        assert resp.json()["valid"] is True

    def test_invalid_format(self, client):
        resp = client.post(f"{API}/documents/validate", json={
            "filename": "virus.exe", "size": 1000, "mime_type": "application/octet-stream"
        })
        assert resp.status_code == 200
        assert resp.json()["valid"] is False
        assert len(resp.json()["errors"]) > 0

    def test_too_large(self, client):
        resp = client.post(f"{API}/documents/validate", json={
            "filename": "huge.pdf", "size": 20 * 1024 * 1024
        })
        assert resp.status_code == 200
        assert resp.json()["valid"] is False

    def test_too_small(self, client):
        resp = client.post(f"{API}/documents/validate", json={
            "filename": "tiny.pdf", "size": 10
        })
        assert resp.status_code == 200
        assert resp.json()["valid"] is False


class TestExtractFields:
    def test_extract_dates(self, client):
        resp = client.post(f"{API}/documents/extract-fields", json={
            "text": "Date de l'accident: 15/03/2025. Consolidation: 20/09/2025."
        })
        assert resp.status_code == 200
        fields = resp.json()["fields"]
        assert "dates" in fields
        assert len(fields["dates"]) >= 2

    def test_extract_amounts(self, client):
        resp = client.post(f"{API}/documents/extract-fields", json={
            "text": "Indemnité: 1 500,00 € et remboursement de 250 €"
        })
        assert resp.status_code == 200
        fields = resp.json()["fields"]
        assert "montants" in fields

    def test_extract_references(self, client):
        resp = client.post(f"{API}/documents/extract-fields", json={
            "text": "Dossier N° AT-2025-12345 Réf. MP-67890"
        })
        assert resp.status_code == 200
        fields = resp.json()["fields"]
        assert "references" in fields

    def test_extract_ss_number(self, client):
        resp = client.post(f"{API}/documents/extract-fields", json={
            "text": "Numéro de sécurité sociale: 1 85 12 75 123 456 78"
        })
        assert resp.status_code == 200
        fields = resp.json()["fields"]
        assert "numero_ss" in fields

    def test_extract_type_detection(self, client):
        resp = client.post(f"{API}/documents/extract-fields", json={
            "text": "Suite à votre accident du travail survenu le 15/03/2025"
        })
        assert resp.status_code == 200
        fields = resp.json()["fields"]
        assert "type_dossier_detected" in fields
        assert "at" in fields["type_dossier_detected"]

    def test_empty_text(self, client):
        resp = client.post(f"{API}/documents/extract-fields", json={"text": ""})
        assert resp.status_code == 200
        assert resp.json()["fields"] == {}


class TestAbandonedCheckout:
    def test_track(self, client):
        resp = client.post(f"{API}/relance/track", json={
            "email": "abandoned@test.com", "package_id": "analyse_dossier"
        })
        assert resp.status_code == 200

    def test_track_no_email(self, client):
        resp = client.post(f"{API}/relance/track", json={"email": ""})
        assert resp.status_code == 400

    def test_admin_relance(self, client, admin_headers):
        resp = client.get(f"{API}/admin/relance", headers=admin_headers)
        assert resp.status_code == 200
        assert "items" in resp.json()


class TestResources:
    def test_track_download(self, client):
        resp = client.post(f"{API}/resources/download", json={
            "resource_id": "test-guide", "resource_title": "Guide AT"
        })
        assert resp.status_code == 200

    def test_admin_resource_stats(self, client, admin_headers):
        resp = client.get(f"{API}/admin/resources/stats", headers=admin_headers)
        assert resp.status_code == 200
        assert "total_downloads" in resp.json()


class TestSEO:
    def test_sitemap(self, client):
        resp = client.get(f"{API}/sitemap.xml")
        assert resp.status_code == 200
        body = resp.text
        assert "<?xml" in body
        assert "<urlset" in body

    def test_robots(self, client):
        resp = client.get(f"{API}/robots.txt")
        assert resp.status_code == 200
        body = resp.text
        assert "User-agent" in body
        assert "Disallow: /admin" in body


class TestSeed:
    def test_seed_idempotent(self, client):
        resp = client.post(f"{API}/seed")
        assert resp.status_code == 200
        assert resp.json()["success"] is True


class TestEmailAdmin:
    def test_email_status(self, client, admin_headers):
        resp = client.get(f"{API}/admin/email/status", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "resend_installed" in data
        assert "api_key_configured" in data
