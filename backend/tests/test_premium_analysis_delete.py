"""
Test DELETE /api/admin/premium-analyses/{id} endpoint
Tests:
- Delete returns 200 with success:true
- Delete also removes linked dossier_express document
- Delete with fake-id returns 404
- Delete requires admin auth (401 without token)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    """Headers with admin auth token"""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


class TestDeletePremiumAnalysisAuth:
    """Test authentication requirements for delete endpoint"""
    
    def test_delete_without_auth_returns_401_or_403(self):
        """DELETE without token should return 401 or 403"""
        # Use a random ID - doesn't matter since auth check happens first
        fake_id = str(uuid.uuid4())
        response = requests.delete(f"{BASE_URL}/api/admin/premium-analyses/{fake_id}")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}: {response.text}"
        print(f"PASS: DELETE without auth returns {response.status_code}")
    
    def test_delete_with_invalid_token_returns_401(self):
        """DELETE with invalid token should return 401"""
        fake_id = str(uuid.uuid4())
        headers = {"Authorization": "Bearer invalid-token-12345"}
        response = requests.delete(f"{BASE_URL}/api/admin/premium-analyses/{fake_id}", headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: DELETE with invalid token returns 401")


class TestDeletePremiumAnalysisNotFound:
    """Test 404 response for non-existent entries"""
    
    def test_delete_fake_id_returns_404(self, auth_headers):
        """DELETE with non-existent ID should return 404"""
        fake_id = "fake-id-does-not-exist-12345"
        response = requests.delete(f"{BASE_URL}/api/admin/premium-analyses/{fake_id}", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data or "message" in data, "Expected error message in response"
        print(f"PASS: DELETE fake-id returns 404 with message: {data}")
    
    def test_delete_random_uuid_returns_404(self, auth_headers):
        """DELETE with random UUID should return 404"""
        random_id = str(uuid.uuid4())
        response = requests.delete(f"{BASE_URL}/api/admin/premium-analyses/{random_id}", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"PASS: DELETE random UUID {random_id} returns 404")


class TestDeletePremiumAnalysisSuccess:
    """Test successful deletion of premium analysis entries"""
    
    def test_get_premium_analyses_list(self, auth_headers):
        """First verify we can get the list of premium analyses"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "items" in data, "Expected 'items' in response"
        print(f"PASS: GET premium-analyses returns {len(data['items'])} items")
        return data
    
    def test_delete_existing_entry_returns_200(self, auth_headers):
        """DELETE existing entry should return 200 with success:true"""
        # First get list to find an entry with admin_test=true
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        items = data.get("items", [])
        
        # Find a test entry (admin_test=true) or create one for testing
        test_entry = None
        for item in items:
            if item.get("admin_test") == True:
                test_entry = item
                break
        
        if not test_entry:
            # No test entry found - skip this test
            pytest.skip("No admin_test=true entry found to delete. Create one first.")
        
        entry_id = test_entry["id"]
        has_dossier = bool(test_entry.get("dossier_id"))
        
        # Delete the entry
        delete_response = requests.delete(f"{BASE_URL}/api/admin/premium-analyses/{entry_id}", headers=auth_headers)
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
        
        delete_data = delete_response.json()
        assert delete_data.get("success") == True, f"Expected success:true, got {delete_data}"
        assert "deleted_dossier" in delete_data, "Expected 'deleted_dossier' field in response"
        
        print(f"PASS: DELETE {entry_id} returns 200 with success:true, deleted_dossier={delete_data['deleted_dossier']}")
        
        # Verify entry is actually deleted
        verify_response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=auth_headers)
        verify_data = verify_response.json()
        remaining_ids = [i["id"] for i in verify_data.get("items", [])]
        assert entry_id not in remaining_ids, f"Entry {entry_id} should be deleted but still exists"
        print(f"PASS: Entry {entry_id} verified as deleted from list")


class TestDeleteLinkedDossierExpress:
    """Test that deleting premium_analysis also deletes linked dossier_express"""
    
    def test_delete_with_linked_dossier(self, auth_headers):
        """DELETE entry with dossier_id should also delete the linked dossier_express"""
        # Get list and find entry with dossier_id
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        items = data.get("items", [])
        
        # Find entry with dossier_id and admin_test=true
        test_entry = None
        for item in items:
            if item.get("dossier_id") and item.get("admin_test") == True:
                test_entry = item
                break
        
        if not test_entry:
            pytest.skip("No admin_test=true entry with dossier_id found. Skipping linked dossier test.")
        
        entry_id = test_entry["id"]
        dossier_id = test_entry["dossier_id"]
        
        # Verify dossier exists before delete
        dossier_check = requests.get(f"{BASE_URL}/api/admin/dossier-express/{dossier_id}/analysis", headers=auth_headers)
        if dossier_check.status_code != 200:
            pytest.skip(f"Linked dossier {dossier_id} not found. Skipping linked dossier test.")
        
        print(f"Found entry {entry_id} with linked dossier {dossier_id}")
        
        # Delete the premium analysis
        delete_response = requests.delete(f"{BASE_URL}/api/admin/premium-analyses/{entry_id}", headers=auth_headers)
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert delete_data.get("deleted_dossier") == True, f"Expected deleted_dossier:true, got {delete_data}"
        
        print(f"PASS: DELETE returned deleted_dossier=true")
        
        # Verify linked dossier is also deleted
        dossier_verify = requests.get(f"{BASE_URL}/api/admin/dossier-express/{dossier_id}/analysis", headers=auth_headers)
        assert dossier_verify.status_code == 404, f"Linked dossier should be deleted but got {dossier_verify.status_code}"
        
        print(f"PASS: Linked dossier {dossier_id} verified as deleted")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
