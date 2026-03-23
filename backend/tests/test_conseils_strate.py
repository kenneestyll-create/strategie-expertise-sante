"""
Test suite for Conseils Straté API endpoints
Tests: GET /api/conseils/today, POST /api/conseils/click, 
       Admin CRUD: list, create, update, delete, highlight, stats
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


class TestConseilsPublicEndpoints:
    """Public endpoints - no auth required"""
    
    def test_get_today_conseil_returns_200(self):
        """GET /api/conseils/today should return a conseil object"""
        response = requests.get(f"{BASE_URL}/api/conseils/today")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify required fields
        assert "text" in data, "Response missing 'text' field"
        assert "category" in data, "Response missing 'category' field"
        assert "link" in data, "Response missing 'link' field"
        assert "link_label" in data, "Response missing 'link_label' field"
        assert "active" in data, "Response missing 'active' field"
        
        # Verify data types
        assert isinstance(data["text"], str), "text should be string"
        assert isinstance(data["category"], str), "category should be string"
        assert len(data["text"]) >= 5, "text should be at least 5 chars"
        print(f"✓ GET /api/conseils/today returned conseil: {data['text'][:50]}...")
    
    def test_get_today_conseil_has_valid_category(self):
        """Conseil category should be one of the valid categories"""
        response = requests.get(f"{BASE_URL}/api/conseils/today")
        assert response.status_code == 200
        
        data = response.json()
        valid_categories = ["droits", "expertise", "indemnisation", "emploi", "demarches", "strategie", "actualite"]
        assert data["category"] in valid_categories, f"Invalid category: {data['category']}"
        print(f"✓ Category '{data['category']}' is valid")
    
    def test_track_click_returns_ok(self):
        """POST /api/conseils/click should track clicks"""
        # First get a conseil to get its text
        conseil_resp = requests.get(f"{BASE_URL}/api/conseils/today")
        conseil_text = conseil_resp.json().get("text", "Test conseil")
        
        response = requests.post(
            f"{BASE_URL}/api/conseils/click",
            json={"text": conseil_text},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok: true"
        print(f"✓ POST /api/conseils/click tracked click successfully")


class TestConseilsAdminAuth:
    """Test that admin endpoints require authentication"""
    
    def test_admin_list_requires_auth(self):
        """GET /api/conseils/admin/list should return 401/403 without auth"""
        response = requests.get(f"{BASE_URL}/api/conseils/admin/list")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ GET /api/conseils/admin/list requires auth ({response.status_code})")
    
    def test_admin_create_requires_auth(self):
        """POST /api/conseils/admin/create should return 401/403 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/conseils/admin/create",
            json={"text": "Test conseil", "category": "droits"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ POST /api/conseils/admin/create requires auth ({response.status_code})")
    
    def test_admin_stats_requires_auth(self):
        """GET /api/conseils/admin/stats should return 401/403 without auth"""
        response = requests.get(f"{BASE_URL}/api/conseils/admin/stats")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ GET /api/conseils/admin/stats requires auth ({response.status_code})")


class TestConseilsAdminCRUD:
    """Admin CRUD operations - requires authentication"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token before each test"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Admin login failed: {login_response.status_code} - {login_response.text}")
        
        token = login_response.json().get("access_token")
        if not token:
            pytest.skip("No access_token in login response")
        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.token = token
    
    def test_admin_list_conseils(self):
        """GET /api/conseils/admin/list should return array of conseils"""
        response = requests.get(
            f"{BASE_URL}/api/conseils/admin/list",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one conseil (seed data)"
        
        # Verify first conseil has required fields
        conseil = data[0]
        required_fields = ["id", "text", "category", "views", "clicks"]
        for field in required_fields:
            assert field in conseil, f"Conseil missing '{field}' field"
        
        print(f"✓ GET /api/conseils/admin/list returned {len(data)} conseils")
    
    def test_admin_stats(self):
        """GET /api/conseils/admin/stats should return stats object"""
        response = requests.get(
            f"{BASE_URL}/api/conseils/admin/stats",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        required_fields = ["total", "active", "total_views", "total_clicks"]
        for field in required_fields:
            assert field in data, f"Stats missing '{field}' field"
        
        assert isinstance(data["total"], int), "total should be int"
        assert isinstance(data["active"], int), "active should be int"
        assert data["total"] >= data["active"], "total should be >= active"
        
        print(f"✓ GET /api/conseils/admin/stats: total={data['total']}, active={data['active']}")
    
    def test_admin_create_conseil(self):
        """POST /api/conseils/admin/create should create a new conseil"""
        test_text = "TEST_Conseil de test pour validation automatique"
        payload = {
            "text": test_text,
            "category": "strategie",
            "link": "/ressources",
            "link_label": "Test Label",
            "active": True,
            "priority": False,
            "tts_enabled": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/conseils/admin/create",
            json=payload,
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should have 'id'"
        assert data.get("ok") == True, "Response should have ok: true"
        
        # Store ID for cleanup
        self.created_id = data["id"]
        print(f"✓ POST /api/conseils/admin/create created conseil with id={data['id']}")
        
        # Cleanup - delete the test conseil
        requests.delete(
            f"{BASE_URL}/api/conseils/admin/{data['id']}",
            headers=self.headers
        )
    
    def test_admin_create_conseil_text_validation_min(self):
        """POST /api/conseils/admin/create should reject text < 5 chars"""
        payload = {
            "text": "abc",  # Too short
            "category": "droits"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/conseils/admin/create",
            json=payload,
            headers=self.headers
        )
        assert response.status_code == 422, f"Expected 422 for short text, got {response.status_code}"
        print("✓ Text validation: rejected text < 5 chars (422)")
    
    def test_admin_create_conseil_text_validation_max(self):
        """POST /api/conseils/admin/create should reject text > 200 chars"""
        payload = {
            "text": "x" * 201,  # Too long
            "category": "droits"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/conseils/admin/create",
            json=payload,
            headers=self.headers
        )
        assert response.status_code == 422, f"Expected 422 for long text, got {response.status_code}"
        print("✓ Text validation: rejected text > 200 chars (422)")
    
    def test_admin_update_conseil(self):
        """PUT /api/conseils/admin/{id} should update a conseil"""
        # First create a conseil to update
        create_payload = {
            "text": "TEST_Conseil a modifier pour test",
            "category": "droits"
        }
        create_resp = requests.post(
            f"{BASE_URL}/api/conseils/admin/create",
            json=create_payload,
            headers=self.headers
        )
        assert create_resp.status_code == 200
        conseil_id = create_resp.json()["id"]
        
        # Update it
        update_payload = {
            "text": "TEST_Conseil modifie avec succes",
            "category": "expertise"
        }
        response = requests.put(
            f"{BASE_URL}/api/conseils/admin/{conseil_id}",
            json=update_payload,
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok: true"
        print(f"✓ PUT /api/conseils/admin/{conseil_id} updated successfully")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/conseils/admin/{conseil_id}",
            headers=self.headers
        )
    
    def test_admin_delete_conseil(self):
        """DELETE /api/conseils/admin/{id} should delete a conseil"""
        # First create a conseil to delete
        create_payload = {
            "text": "TEST_Conseil a supprimer pour test",
            "category": "droits"
        }
        create_resp = requests.post(
            f"{BASE_URL}/api/conseils/admin/create",
            json=create_payload,
            headers=self.headers
        )
        assert create_resp.status_code == 200
        conseil_id = create_resp.json()["id"]
        
        # Delete it
        response = requests.delete(
            f"{BASE_URL}/api/conseils/admin/{conseil_id}",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok: true"
        print(f"✓ DELETE /api/conseils/admin/{conseil_id} deleted successfully")
        
        # Verify it's gone
        list_resp = requests.get(
            f"{BASE_URL}/api/conseils/admin/list",
            headers=self.headers
        )
        conseils = list_resp.json()
        ids = [c["id"] for c in conseils]
        assert conseil_id not in ids, "Deleted conseil should not be in list"
        print("✓ Verified conseil no longer in list after delete")
    
    def test_admin_highlight_conseil(self):
        """POST /api/conseils/admin/{id}/highlight should set priority"""
        # Get list of conseils
        list_resp = requests.get(
            f"{BASE_URL}/api/conseils/admin/list",
            headers=self.headers
        )
        conseils = list_resp.json()
        assert len(conseils) > 0, "Need at least one conseil"
        
        conseil_id = conseils[0]["id"]
        
        # Highlight it
        response = requests.post(
            f"{BASE_URL}/api/conseils/admin/{conseil_id}/highlight",
            json={},
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok: true"
        print(f"✓ POST /api/conseils/admin/{conseil_id}/highlight set priority")
        
        # Verify it's now priority
        list_resp2 = requests.get(
            f"{BASE_URL}/api/conseils/admin/list",
            headers=self.headers
        )
        conseils2 = list_resp2.json()
        highlighted = [c for c in conseils2 if c["id"] == conseil_id][0]
        assert highlighted.get("priority") == True, "Conseil should have priority=True"
        print("✓ Verified conseil has priority=True after highlight")
    
    def test_admin_delete_nonexistent_conseil(self):
        """DELETE /api/conseils/admin/{id} should return 404 for invalid id"""
        fake_id = "000000000000000000000000"  # Valid ObjectId format but doesn't exist
        
        response = requests.delete(
            f"{BASE_URL}/api/conseils/admin/{fake_id}",
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ DELETE nonexistent conseil returns 404")


class TestConseilsDataPersistence:
    """Test that data persists correctly"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token before each test"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Admin login failed: {login_response.status_code}")
        
        token = login_response.json().get("access_token")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_create_and_verify_persistence(self):
        """Create conseil and verify it appears in list"""
        unique_text = f"TEST_Conseil unique {os.urandom(4).hex()}"
        
        # Create
        create_resp = requests.post(
            f"{BASE_URL}/api/conseils/admin/create",
            json={"text": unique_text, "category": "actualite"},
            headers=self.headers
        )
        assert create_resp.status_code == 200
        conseil_id = create_resp.json()["id"]
        
        # Verify in list
        list_resp = requests.get(
            f"{BASE_URL}/api/conseils/admin/list",
            headers=self.headers
        )
        conseils = list_resp.json()
        found = [c for c in conseils if c["id"] == conseil_id]
        assert len(found) == 1, "Created conseil should be in list"
        assert found[0]["text"] == unique_text, "Text should match"
        assert found[0]["category"] == "actualite", "Category should match"
        
        print(f"✓ Created conseil persisted correctly with id={conseil_id}")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/conseils/admin/{conseil_id}",
            headers=self.headers
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
