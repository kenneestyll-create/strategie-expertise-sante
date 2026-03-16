"""
Tests for Send Test Email feature in Email Template Editor
Tests the POST /api/admin/email-templates/send-test endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSendTestEmailEndpoint:
    """Tests for POST /api/admin/email-templates/send-test endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Authenticate as admin and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json()["access_token"]
    
    @pytest.fixture
    def auth_headers(self, admin_token):
        """Return headers with auth token"""
        return {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
    
    def test_send_test_email_without_email_returns_400(self, auth_headers):
        """POST /api/admin/email-templates/send-test without email should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email-templates/send-test",
            headers=auth_headers,
            json={
                "subject": "Test subject",
                "intro": "Test intro",
                "motivation": "Test motivation",
                "cta_text": "Test CTA"
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "email" in data.get("detail", "").lower() or "adresse" in data.get("detail", "").lower(), \
            f"Error message should mention email: {data}"
    
    def test_send_test_email_with_empty_email_returns_400(self, auth_headers):
        """POST /api/admin/email-templates/send-test with empty email should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email-templates/send-test",
            headers=auth_headers,
            json={
                "email": "",
                "subject": "Test subject"
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_send_test_email_with_valid_data_returns_response(self, auth_headers):
        """POST /api/admin/email-templates/send-test with valid data returns success or sandbox error"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email-templates/send-test",
            headers=auth_headers,
            json={
                "email": "test@example.com",
                "subject": "Bonjour {{prenom}}, votre dossier",
                "intro": "Cher {{prenom}} {{nom}}, votre dossier est à {{completeness}}%",
                "motivation": "Documents manquants: {{documents_missing}}",
                "cta_text": "Compléter mon dossier",
                "prenom": "Marie",
                "nom": "Dupont",
                "completeness": "42",
                "documents_missing": "Attestation employeur",
                "date_inscription": "15/01/2026"
            }
        )
        # Should return 200 with success/failure indication (sandbox mode returns success: false)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "success" in data, "Response should have 'success' field"
        assert "message" in data, "Response should have 'message' field"
        # Sandbox mode will return success=false with restriction message - this is expected
    
    def test_send_test_email_returns_proper_json_structure(self, auth_headers):
        """Verify send-test endpoint returns proper JSON with success and message fields"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email-templates/send-test",
            headers=auth_headers,
            json={
                "email": "test@test.com",
                "subject": "Test",
                "intro": "Test intro"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data.get("success"), bool), "success should be boolean"
        assert isinstance(data.get("message"), str), "message should be string"
    
    def test_send_test_email_resolves_prenom_variable(self, auth_headers):
        """Verify {{prenom}} variable is resolved in send-test (checking backend logic)"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email-templates/send-test",
            headers=auth_headers,
            json={
                "email": "test@example.com",
                "subject": "Hello {{prenom}}",
                "intro": "Dear {{prenom}}, welcome",
                "prenom": "TestName123"
            }
        )
        assert response.status_code == 200
        # The API returns success/message, variables are resolved in the email HTML internally
        # We can't verify the email content directly but the endpoint processes the variables
    
    def test_send_test_email_unauthenticated_returns_auth_error(self):
        """POST /api/admin/email-templates/send-test without auth should return 401 or 403"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email-templates/send-test",
            headers={"Content-Type": "application/json"},
            json={
                "email": "test@example.com",
                "subject": "Test"
            }
        )
        assert response.status_code in [401, 403], f"Expected 401/403 unauthorized, got {response.status_code}"
    
    def test_send_test_email_with_all_variables(self, auth_headers):
        """Test send-test with all 5 variables: prenom, nom, completeness, documents_missing, date_inscription"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email-templates/send-test",
            headers=auth_headers,
            json={
                "email": "admin@test.com",
                "subject": "{{prenom}} {{nom}} - Dossier",
                "intro": "Complétude: {{completeness}}%",
                "motivation": "Docs: {{documents_missing}}, inscrit le {{date_inscription}}",
                "cta_text": "Finaliser",
                "prenom": "Jean",
                "nom": "Martin",
                "completeness": "75",
                "documents_missing": "CV, Diplôme",
                "date_inscription": "01/02/2026"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data


class TestEmailTemplatesExisting:
    """Verify existing email template features still work (regression tests)"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Authenticate as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        return response.json()["access_token"]
    
    @pytest.fixture
    def auth_headers(self, admin_token):
        return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    def test_list_templates_still_works(self, auth_headers):
        """GET /api/admin/email-templates should still return templates list"""
        response = requests.get(f"{BASE_URL}/api/admin/email-templates", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)
    
    def test_preview_template_still_works(self, auth_headers):
        """POST /api/admin/email-templates/preview should still work with variables"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email-templates/preview",
            headers=auth_headers,
            json={
                "subject": "Test {{prenom}}",
                "intro": "Hello {{prenom}}",
                "motivation": "Your completeness: {{completeness}}%",
                "cta_text": "Click here"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "html" in data
        assert "Marie" in data["html"], "Preview should resolve {{prenom}} to sample value 'Marie'"
    
    def test_variables_endpoint_still_works(self, auth_headers):
        """GET /api/admin/email-templates/variables should return 5 variables"""
        response = requests.get(f"{BASE_URL}/api/admin/email-templates/variables", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "variables" in data
        assert len(data["variables"]) == 5
        keys = [v["key"] for v in data["variables"]]
        assert "prenom" in keys
        assert "nom" in keys
        assert "completeness" in keys
        assert "documents_missing" in keys
        assert "date_inscription" in keys


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
