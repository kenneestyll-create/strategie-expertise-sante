"""Tests for routes/client.py — client portal: auth, profile, documents, notifications, progress."""
import pytest
import uuid

API = "/api"


class TestClientAuth:
    def test_register(self, client):
        email = f"pytest-reg-{uuid.uuid4().hex[:6]}@test.com"
        resp = client.post(f"{API}/client/register", json={
            "email": email, "password": "TestPass123!", "name": "Pytest User"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["client_name"] == "Pytest User"

    def test_register_duplicate(self, client, test_client_user):
        resp = client.post(f"{API}/client/register", json={
            "email": test_client_user["email"], "password": "Pass!", "name": "Dup"
        })
        assert resp.status_code == 409

    def test_login(self, client, test_client_user):
        resp = client.post(f"{API}/client/login", json={
            "email": test_client_user["email"], "password": "TestPass123!"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client, test_client_user):
        resp = client.post(f"{API}/client/login", json={
            "email": test_client_user["email"], "password": "Wrong!"
        })
        assert resp.status_code == 401


class TestClientProfile:
    def test_get_profile(self, client, client_headers, test_client_user):
        resp = client.get(f"{API}/client/profile", headers=client_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == test_client_user["email"]
        assert data["name"] == "PyTest User"
        assert "password_hash" not in data

    def test_profile_unauthorized(self, client):
        resp = client.get(f"{API}/client/profile")
        assert resp.status_code == 403


class TestClientProgress:
    def test_get_progress(self, client, client_headers):
        resp = client.get(f"{API}/client/progress", headers=client_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "progress_pct" in data
        assert "steps" in data
        assert "next_action" in data
        assert "counts" in data
        assert "summary" in data
        assert len(data["steps"]) == 6

    def test_progress_first_step_completed(self, client, client_headers):
        resp = client.get(f"{API}/client/progress", headers=client_headers)
        steps = resp.json()["steps"]
        assert steps[0]["id"] == "inscription"
        assert steps[0]["status"] == "completed"


class TestClientCases:
    def test_list_cases_empty(self, client, client_headers):
        resp = client.get(f"{API}/client/cases", headers=client_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestClientDocuments:
    def test_upload_document(self, client, client_headers):
        resp = client.post(f"{API}/client/documents", json={
            "filename": "test.pdf", "file_data": "base64_fake_data",
            "mime_type": "application/pdf", "size": 5000,
            "tags": {"categorie": "at"}
        }, headers=client_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        doc_id = data["document"]["id"]

        # List documents
        resp2 = client.get(f"{API}/client/documents", headers=client_headers)
        assert resp2.status_code == 200
        assert resp2.json()["total"] >= 1

        # Get single document
        resp3 = client.get(f"{API}/client/documents/{doc_id}", headers=client_headers)
        assert resp3.status_code == 200
        assert resp3.json()["filename"] == "test.pdf"

        # Update document
        resp4 = client.patch(f"{API}/client/documents/{doc_id}", json={
            "category": "mp"
        }, headers=client_headers)
        assert resp4.status_code == 200

        # Delete document
        resp5 = client.delete(f"{API}/client/documents/{doc_id}", headers=client_headers)
        assert resp5.status_code == 200

    def test_upload_too_large(self, client, client_headers):
        resp = client.post(f"{API}/client/documents", json={
            "filename": "big.pdf", "file_data": "data",
            "size": 20 * 1024 * 1024
        }, headers=client_headers)
        assert resp.status_code == 400

    def test_upload_missing_file(self, client, client_headers):
        resp = client.post(f"{API}/client/documents", json={
            "filename": "", "file_data": ""
        }, headers=client_headers)
        assert resp.status_code == 400

    def test_list_with_filters(self, client, client_headers):
        resp = client.get(f"{API}/client/documents?category=at&status=en_attente", headers=client_headers)
        assert resp.status_code == 200


class TestClientNotifications:
    def test_list_notifications(self, client, client_headers):
        resp = client.get(f"{API}/client/notifications", headers=client_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "notifications" in data
        assert "unread_count" in data

    def test_mark_all_read(self, client, client_headers):
        resp = client.patch(f"{API}/client/notifications/read-all", headers=client_headers)
        assert resp.status_code == 200


class TestNotificationSettings:
    def test_get_settings(self, client, client_headers):
        resp = client.get(f"{API}/client/settings/notifications", headers=client_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "notifications_email" in data
        assert "notifications_push" in data

    def test_update_settings(self, client, client_headers):
        resp = client.patch(f"{API}/client/settings/notifications", json={
            "notifications_email": False, "notifications_push": True
        }, headers=client_headers)
        assert resp.status_code == 200

        resp2 = client.get(f"{API}/client/settings/notifications", headers=client_headers)
        data = resp2.json()
        assert data["notifications_email"] is False
        assert data["notifications_push"] is True
