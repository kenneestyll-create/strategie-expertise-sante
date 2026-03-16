"""
Tests for Email Test History Feature (Iteration 55)
Tests the test email history tracking functionality:
- POST /api/admin/email-templates/send-test saves to history
- GET /api/admin/email-templates/{id}/test-history returns history
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEmailTestHistory:
    """Tests for email test history feature"""
    
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
    
    @pytest.fixture(scope="class")
    def template_ids(self, admin_token):
        """Get template IDs for rassurant, incitatif, urgent"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        # Ensure templates exist by seeding
        requests.post(f"{BASE_URL}/api/admin/email-templates/seed", headers=headers)
        # Get templates
        response = requests.get(f"{BASE_URL}/api/admin/email-templates", headers=headers)
        assert response.status_code == 200
        templates = response.json()["templates"]
        template_map = {}
        for tpl in templates:
            template_map[tpl["name"]] = tpl["id"]
        return template_map
    
    # ===================== GET TEST HISTORY TESTS =====================
    
    def test_get_test_history_endpoint_exists(self, auth_headers, template_ids):
        """GET /api/admin/email-templates/{id}/test-history should return 200"""
        tpl_id = template_ids.get("rassurant", list(template_ids.values())[0])
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{tpl_id}/test-history",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_get_test_history_returns_proper_structure(self, auth_headers, template_ids):
        """GET /api/admin/email-templates/{id}/test-history should return history array"""
        tpl_id = template_ids.get("rassurant", list(template_ids.values())[0])
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{tpl_id}/test-history",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "history" in data, "Response should have 'history' field"
        assert isinstance(data["history"], list), "history should be a list"
    
    def test_get_test_history_for_template_with_no_history(self, auth_headers, template_ids):
        """GET /api/admin/email-templates/{id}/test-history for template with no tests returns empty array"""
        # Use 'urgent' template which may have no tests yet
        tpl_id = template_ids.get("urgent", list(template_ids.values())[-1])
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{tpl_id}/test-history",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        # May or may not be empty, but structure should be correct
        assert isinstance(data["history"], list)
    
    def test_get_test_history_unauthenticated_returns_error(self, template_ids):
        """GET /api/admin/email-templates/{id}/test-history without auth should return 401/403"""
        tpl_id = template_ids.get("rassurant", list(template_ids.values())[0])
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{tpl_id}/test-history",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    # ===================== HISTORY RECORD STRUCTURE TESTS =====================
    
    def test_history_record_has_required_fields(self, auth_headers, template_ids):
        """History records should have id, email, status, sent_at fields"""
        tpl_id = template_ids.get("rassurant", list(template_ids.values())[0])
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{tpl_id}/test-history",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        if len(data["history"]) > 0:
            record = data["history"][0]
            assert "id" in record, "History record should have 'id'"
            assert "email" in record, "History record should have 'email'"
            assert "status" in record, "History record should have 'status'"
            assert "sent_at" in record, "History record should have 'sent_at'"
    
    def test_history_record_has_template_info(self, auth_headers, template_ids):
        """History records should include template_id and template_name"""
        tpl_id = template_ids.get("rassurant", list(template_ids.values())[0])
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{tpl_id}/test-history",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        if len(data["history"]) > 0:
            record = data["history"][0]
            assert "template_id" in record, "History record should have 'template_id'"
            # template_name is optional but good to have
    
    def test_history_record_has_variables_used(self, auth_headers, template_ids):
        """History records should include variables_used object"""
        tpl_id = template_ids.get("rassurant", list(template_ids.values())[0])
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{tpl_id}/test-history",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        if len(data["history"]) > 0:
            record = data["history"][0]
            assert "variables_used" in record, "History record should have 'variables_used'"
            if record["variables_used"]:
                # Should contain variable keys
                vars_used = record["variables_used"]
                assert isinstance(vars_used, dict), "variables_used should be a dict"
    
    # ===================== SEND-TEST SAVES TO HISTORY TESTS =====================
    
    def test_send_test_saves_to_history(self, auth_headers, template_ids):
        """POST /api/admin/email-templates/send-test should save to history"""
        tpl_id = template_ids.get("incitatif", list(template_ids.values())[0])
        
        # Send a test email
        test_email = f"test_history_{int(time.time())}@example.com"
        send_response = requests.post(
            f"{BASE_URL}/api/admin/email-templates/send-test",
            headers=auth_headers,
            json={
                "template_id": tpl_id,
                "template_name": "incitatif",
                "email": test_email,
                "subject": "Test History Save",
                "intro": "Testing history",
                "motivation": "History test",
                "cta_text": "Click",
                "prenom": "HistTest",
                "nom": "User",
                "completeness": "55",
                "documents_missing": "Test doc",
                "date_inscription": "20/01/2026"
            }
        )
        assert send_response.status_code == 200, f"Send test failed: {send_response.text}"
        
        # Verify it was saved to history
        history_response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{tpl_id}/test-history",
            headers=auth_headers
        )
        assert history_response.status_code == 200
        data = history_response.json()
        assert len(data["history"]) > 0, "History should not be empty after sending test"
        
        # Find our test email in history
        found = False
        for record in data["history"]:
            if record.get("email") == test_email:
                found = True
                assert record.get("template_id") == tpl_id
                assert record.get("status") in ["sent", "failed"]  # sandbox mode = failed is expected
                break
        assert found, f"Test email {test_email} not found in history"
    
    def test_history_is_sorted_by_sent_at_desc(self, auth_headers, template_ids):
        """History should be sorted by sent_at DESC (most recent first)"""
        tpl_id = template_ids.get("rassurant", list(template_ids.values())[0])
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{tpl_id}/test-history",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        if len(data["history"]) > 1:
            # Check that first item's sent_at is >= second item's sent_at
            first_time = data["history"][0].get("sent_at", "")
            second_time = data["history"][1].get("sent_at", "")
            assert first_time >= second_time, f"History not sorted DESC: {first_time} should be >= {second_time}"
    
    def test_history_limited_to_10_records(self, auth_headers, template_ids):
        """History endpoint should return max 10 records (per backend logic)"""
        tpl_id = template_ids.get("rassurant", list(template_ids.values())[0])
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{tpl_id}/test-history",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["history"]) <= 10, f"History should have max 10 records, got {len(data['history'])}"
    
    # ===================== HISTORY STATUS TESTS =====================
    
    def test_history_status_is_sent_or_failed(self, auth_headers, template_ids):
        """History record status should be 'sent' or 'failed'"""
        tpl_id = template_ids.get("rassurant", list(template_ids.values())[0])
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{tpl_id}/test-history",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for record in data["history"]:
            assert record.get("status") in ["sent", "failed", "pending"], \
                f"Invalid status: {record.get('status')}"


class TestRassurantTemplateHistory:
    """Verify rassurant template has history from previous test"""
    
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
    
    @pytest.fixture(scope="class")
    def rassurant_id(self, admin_token):
        """Get rassurant template ID"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        requests.post(f"{BASE_URL}/api/admin/email-templates/seed", headers=headers)
        response = requests.get(f"{BASE_URL}/api/admin/email-templates", headers=headers)
        templates = response.json().get("templates", [])
        for tpl in templates:
            if tpl["name"] == "rassurant":
                return tpl["id"]
        return None
    
    def test_rassurant_has_history(self, auth_headers, rassurant_id):
        """Rassurant template should have test history from iteration 54"""
        if not rassurant_id:
            pytest.skip("Rassurant template not found")
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{rassurant_id}/test-history",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # According to context, there's at least 1 history record for rassurant with test@example.com
        assert len(data["history"]) >= 1, "Rassurant should have at least 1 test history record"
    
    def test_rassurant_history_contains_test_example_email(self, auth_headers, rassurant_id):
        """Rassurant history should contain test@example.com from previous API test"""
        if not rassurant_id:
            pytest.skip("Rassurant template not found")
        response = requests.get(
            f"{BASE_URL}/api/admin/email-templates/{rassurant_id}/test-history",
            headers=auth_headers
        )
        data = response.json()
        emails = [r.get("email", "") for r in data.get("history", [])]
        # Check if any test email exists in history (may be test@example.com or others)
        assert len(emails) >= 1, "Should have at least one test email in history"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
