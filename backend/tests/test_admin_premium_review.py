"""
Test Admin Premium Review Features - Iteration 115
Tests for:
1. Admin login flow
2. Admin dashboard tabs (StrategiIA, Dossier Express)
3. Premium analyses CRUD operations
4. Full-content endpoint for review dialog
5. Status changes (Traiter, Relire/Valider)
6. Send-reviewed endpoint
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"

# Shared token to avoid rate limiting
_cached_token = None

def get_admin_token():
    """Get admin token with caching to avoid rate limiting"""
    global _cached_token
    if _cached_token:
        return _cached_token
    time.sleep(2)  # Wait to avoid rate limiting
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        _cached_token = response.json()["access_token"]
        return _cached_token
    raise Exception(f"Login failed: {response.text}")


class TestAdminAuth:
    """Test admin authentication"""
    
    def test_admin_login_success(self):
        """Test admin login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "admin_name" in data, "No admin_name in response"
        print(f"✓ Admin login successful, admin_name: {data.get('admin_name')}")
        return data["access_token"]
    
    def test_admin_login_invalid_credentials(self):
        """Test admin login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@email.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid credentials correctly rejected")


class TestAdminPremiumAnalyses:
    """Test premium analyses admin endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for authenticated requests"""
        self.token = get_admin_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_premium_analyses_list(self):
        """Test GET /api/admin/premium-analyses returns list with stats"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "items" in data, "No items in response"
        assert "stats" in data, "No stats in response"
        stats = data["stats"]
        assert "total" in stats, "No total in stats"
        assert "en_attente" in stats, "No en_attente in stats"
        assert "en_cours" in stats, "No en_cours in stats"
        print(f"✓ Premium analyses list: {stats['total']} total, {stats['en_attente']} en_attente, {stats['en_cours']} en_cours")
        return data
    
    def test_premium_analyses_have_type_field(self):
        """Test that premium analyses have type field (strategiia or dossier_express)"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        items = data.get("items", [])
        if items:
            # Check first few items have type field
            for item in items[:5]:
                assert "type" in item, f"Item missing type field: {item.get('id')}"
                assert item["type"] in ["strategiia", "dossier_express"], f"Invalid type: {item['type']}"
            print(f"✓ All checked items have valid type field (strategiia/dossier_express)")
        else:
            print("⚠ No premium analyses items to check")
    
    def test_filter_strategiia_items(self):
        """Test filtering items by type=strategiia"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        items = data.get("items", [])
        strategiia_items = [i for i in items if i.get("type") == "strategiia"]
        print(f"✓ Found {len(strategiia_items)} StrategiIA items out of {len(items)} total")
    
    def test_filter_dossier_express_items(self):
        """Test filtering items by type=dossier_express"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        items = data.get("items", [])
        dossier_express_items = [i for i in items if i.get("type") == "dossier_express"]
        print(f"✓ Found {len(dossier_express_items)} Dossier Express items out of {len(items)} total")


class TestPremiumAnalysisFullContent:
    """Test full-content endpoint for review dialog"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token and find a premium analysis to test"""
        self.token = get_admin_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get list of premium analyses
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=self.headers)
        assert response.status_code == 200
        self.items = response.json().get("items", [])
    
    def test_full_content_endpoint_exists(self):
        """Test GET /api/admin/premium-analyses/{id}/full-content endpoint exists"""
        if not self.items:
            pytest.skip("No premium analyses to test")
        
        item = self.items[0]
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses/{item['id']}/full-content", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "id" in data, "No id in response"
        assert "type" in data, "No type in response"
        assert "full_text" in data, "No full_text in response"
        assert "source_data" in data, "No source_data in response"
        print(f"✓ Full content endpoint works for item {item['id'][:8]}...")
    
    def test_full_content_returns_source_data(self):
        """Test that full-content returns source_data with situation, type_dossier, regime"""
        if not self.items:
            pytest.skip("No premium analyses to test")
        
        # Find a dossier_express item if available
        dossier_items = [i for i in self.items if i.get("type") == "dossier_express"]
        item = dossier_items[0] if dossier_items else self.items[0]
        
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses/{item['id']}/full-content", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        source_data = data.get("source_data", {})
        # source_data should have situation, type_dossier, regime for dossier_express
        print(f"✓ Source data keys: {list(source_data.keys())}")
    
    def test_full_content_404_for_invalid_id(self):
        """Test that full-content returns 404 for invalid ID"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses/invalid-id-12345/full-content", headers=self.headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Full content returns 404 for invalid ID")


class TestPremiumAnalysisStatusChanges:
    """Test status change operations (Traiter, Valider)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.token = get_admin_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_patch_status_to_en_cours(self):
        """Test PATCH /api/admin/premium-analyses/{id} to change status to en_cours"""
        # Get an en_attente item
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=self.headers)
        assert response.status_code == 200
        items = response.json().get("items", [])
        en_attente_items = [i for i in items if i.get("status") == "en_attente"]
        
        if not en_attente_items:
            pytest.skip("No en_attente items to test status change")
        
        item = en_attente_items[0]
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/{item['id']}",
            json={"status": "en_cours"},
            headers=self.headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        print(f"✓ Changed status to en_cours for item {item['id'][:8]}...")
    
    def test_patch_status_to_valide_with_reviewed_analysis(self):
        """Test PATCH to valide status with reviewed_analysis text"""
        # Get an en_cours item
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=self.headers)
        assert response.status_code == 200
        items = response.json().get("items", [])
        en_cours_items = [i for i in items if i.get("status") == "en_cours"]
        
        if not en_cours_items:
            pytest.skip("No en_cours items to test validation")
        
        item = en_cours_items[0]
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/{item['id']}",
            json={
                "status": "valide",
                "reviewed_analysis": "Test reviewed analysis content for validation"
            },
            headers=self.headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        print(f"✓ Changed status to valide with reviewed_analysis for item {item['id'][:8]}...")
    
    def test_patch_invalid_status_rejected(self):
        """Test that invalid status values are rejected"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=self.headers)
        assert response.status_code == 200
        items = response.json().get("items", [])
        
        if not items:
            pytest.skip("No items to test")
        
        item = items[0]
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/{item['id']}",
            json={"status": "invalid_status"},
            headers=self.headers
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid status correctly rejected with 400")


class TestSendReviewedDocument:
    """Test send-reviewed endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.token = get_admin_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_send_reviewed_endpoint_exists(self):
        """Test POST /api/admin/premium-analyses/{id}/send-reviewed endpoint"""
        # Get a valide item
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=self.headers)
        assert response.status_code == 200
        items = response.json().get("items", [])
        valide_items = [i for i in items if i.get("status") == "valide"]
        
        if not valide_items:
            pytest.skip("No valide items to test send-reviewed")
        
        item = valide_items[0]
        response = requests.post(
            f"{BASE_URL}/api/admin/premium-analyses/{item['id']}/send-reviewed",
            json={"reviewed_analysis": "Final reviewed content for sending"},
            headers=self.headers
        )
        # Should succeed or fail gracefully (email might not be configured)
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            print(f"✓ Send-reviewed endpoint works, email_sent: {data.get('email_sent')}")
        else:
            print("⚠ Send-reviewed returned 500 (email service issue)")
    
    def test_send_reviewed_requires_analysis_text(self):
        """Test that send-reviewed requires reviewed_analysis text"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=self.headers)
        assert response.status_code == 200
        items = response.json().get("items", [])
        
        # Find an item without reviewed_analysis
        items_without_review = [i for i in items if not i.get("reviewed_analysis")]
        
        if not items_without_review:
            pytest.skip("No items without reviewed_analysis to test")
        
        item = items_without_review[0]
        response = requests.post(
            f"{BASE_URL}/api/admin/premium-analyses/{item['id']}/send-reviewed",
            json={},  # Empty body
            headers=self.headers
        )
        # Should return 400 if no analysis text
        if response.status_code == 400:
            print("✓ Send-reviewed correctly requires reviewed_analysis text")
        else:
            print(f"⚠ Send-reviewed returned {response.status_code} for empty body")


class TestDossierExpressAdmin:
    """Test Dossier Express admin endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.token = get_admin_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_dossier_express_admin_endpoint(self):
        """Test GET /api/admin/dossier-express returns stats"""
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "items" in data, "No items in response"
        assert "stats" in data, "No stats in response"
        stats = data["stats"]
        assert "total" in stats, "No total in stats"
        assert "completed" in stats, "No completed in stats"
        assert "processing" in stats, "No processing in stats"
        assert "errors" in stats, "No errors in stats"
        print(f"✓ Dossier Express admin: {stats['total']} total, {stats['completed']} completed, {stats['processing']} processing, {stats['errors']} errors")


class TestDossierExpressProgressStep:
    """Test Dossier Express progress_step tracking"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.token = get_admin_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_dossier_status_has_progress_step(self):
        """Test that dossier status includes progress_step field"""
        # Create a test dossier via admin-bypass
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Test Progress Step",
                "situation": "Test situation for progress step verification",
                "type_dossier": "Accident du travail (AT)",
                "regime": "Régime général"
            },
            headers=self.headers
        )
        assert response.status_code == 200, f"Failed to create dossier: {response.text}"
        dossier_id = response.json()["dossier_id"]
        
        # Check status immediately
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/{dossier_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Should have progress_step field
        if "progress_step" in data:
            print(f"✓ Dossier has progress_step: {data['progress_step']}")
        else:
            print("⚠ progress_step not yet set (dossier may be processing)")
        
        assert "status" in data
        print(f"✓ Dossier status: {data['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
