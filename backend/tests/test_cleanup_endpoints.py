"""
Test suite for Production Cleanup endpoints
Tests the 'Préparation Production' cleanup panel functionality
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com').rstrip('/')

class TestCleanupEndpoints:
    """Test all cleanup endpoints for the Production Cleanup panel"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for authenticated requests"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        data = login_response.json()
        # Note: The endpoint returns 'access_token' not 'token'
        self.token = data.get('access_token')
        assert self.token, f"No access_token in response: {data}"
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cleanup_contacts(self):
        """POST /api/admin/cleanup/contacts - deletes all contacts"""
        response = requests.post(f"{BASE_URL}/api/admin/cleanup/contacts", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "deleted" in data, f"Response missing 'deleted' field: {data}"
        assert "collection" in data, f"Response missing 'collection' field: {data}"
        print(f"PASS: Contacts cleanup - deleted {data['deleted']} items")
    
    def test_cleanup_strategiia(self):
        """POST /api/admin/cleanup/strategiia - deletes analyses"""
        response = requests.post(f"{BASE_URL}/api/admin/cleanup/strategiia", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "deleted" in data, f"Response missing 'deleted' field: {data}"
        print(f"PASS: StrategiIA cleanup - deleted {data['deleted']} items")
    
    def test_cleanup_dossier_express(self):
        """POST /api/admin/cleanup/dossier-express - deletes dossiers"""
        response = requests.post(f"{BASE_URL}/api/admin/cleanup/dossier-express", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "deleted" in data, f"Response missing 'deleted' field: {data}"
        print(f"PASS: Dossier Express cleanup - deleted {data['deleted']} items")
    
    def test_cleanup_avis(self):
        """POST /api/admin/cleanup/avis - deletes avis"""
        response = requests.post(f"{BASE_URL}/api/admin/cleanup/avis", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "deleted" in data, f"Response missing 'deleted' field: {data}"
        print(f"PASS: Avis cleanup - deleted {data['deleted']} items")
    
    def test_cleanup_chatbot(self):
        """POST /api/admin/cleanup/chatbot - deletes chatbot sessions"""
        response = requests.post(f"{BASE_URL}/api/admin/cleanup/chatbot", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "deleted" in data, f"Response missing 'deleted' field: {data}"
        print(f"PASS: Chatbot cleanup - deleted {data['deleted']} items")
    
    def test_cleanup_onboarding(self):
        """POST /api/admin/cleanup/onboarding - deletes onboarding stats"""
        response = requests.post(f"{BASE_URL}/api/admin/cleanup/onboarding", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "deleted" in data, f"Response missing 'deleted' field: {data}"
        print(f"PASS: Onboarding cleanup - deleted {data['deleted']} items")
    
    def test_counter_reset_visitors(self):
        """POST /api/admin/cleanup/counter-reset with type=visitors"""
        response = requests.post(
            f"{BASE_URL}/api/admin/cleanup/counter-reset",
            headers=self.headers,
            json={"type": "visitors"}
        )
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "reset" in data, f"Response missing 'reset' field: {data}"
        assert data.get("value") == 0, f"Counter not reset to 0: {data}"
        print(f"PASS: Visitors counter reset - {data}")
    
    def test_counter_reset_dossiers(self):
        """POST /api/admin/cleanup/counter-reset with type=dossiers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/cleanup/counter-reset",
            headers=self.headers,
            json={"type": "dossiers"}
        )
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "reset" in data, f"Response missing 'reset' field: {data}"
        assert data.get("value") == 0, f"Counter not reset to 0: {data}"
        print(f"PASS: Dossiers counter reset - {data}")
    
    def test_counter_reset_invalid_type(self):
        """POST /api/admin/cleanup/counter-reset with invalid type should fail"""
        response = requests.post(
            f"{BASE_URL}/api/admin/cleanup/counter-reset",
            headers=self.headers,
            json={"type": "invalid"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid type, got: {response.status_code}"
        print("PASS: Invalid counter type correctly rejected with 400")
    
    def test_full_purge(self):
        """POST /api/admin/cleanup/full-purge - deletes all test data"""
        response = requests.post(f"{BASE_URL}/api/admin/cleanup/full-purge", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "purged" in data, f"Response missing 'purged' field: {data}"
        purged = data["purged"]
        assert "counters_reset" in purged, f"Response missing 'counters_reset' field: {purged}"
        assert purged["counters_reset"] == True, f"Counters not reset: {purged}"
        print(f"PASS: Full purge completed - {purged}")
    
    def test_cleanup_requires_auth(self):
        """Cleanup endpoints should require authentication"""
        # Test without auth header
        response = requests.post(f"{BASE_URL}/api/admin/cleanup/contacts")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got: {response.status_code}"
        print("PASS: Cleanup endpoints correctly require authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
