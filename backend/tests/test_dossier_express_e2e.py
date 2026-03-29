"""
Dossier Express E2E Tests - Iteration 147
Tests the multi-stage LLM pipeline that replaced the single/dual LLM call pattern.
Uses existing completed dossiers (bfc7d774, fd698d45) to avoid triggering new LLM calls.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"

# Existing completed dossiers from previous tests
DOSSIER_ID_1 = "bfc7d774-b9c5-4134-962d-65a3934ae940"  # MP general, completed
DOSSIER_ID_2 = "fd698d45"  # AT agricole, completed (partial ID)


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        # Auth returns 'access_token' not 'token'
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Admin authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    """Headers with admin auth token"""
    return {"Authorization": f"Bearer {admin_token}"}


class TestDossierExpressStatus:
    """Test GET /api/dossier-express/status/{dossier_id}"""
    
    def test_status_completed_dossier(self):
        """Verify status endpoint returns 'completed' for existing dossier"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/{DOSSIER_ID_1}")
        print(f"Status response: {response.status_code} - {response.text[:500]}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify status is completed
        assert data.get("status") == "completed", f"Expected status=completed, got {data.get('status')}"
        assert "id" in data or "dossier_id" in data, "Response should contain dossier ID"
        print(f"PASS: Dossier {DOSSIER_ID_1} status = completed")
    
    def test_status_nonexistent_dossier(self):
        """Verify 404 for non-existent dossier"""
        fake_id = "nonexistent-dossier-12345"
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/{fake_id}")
        
        assert response.status_code == 404, f"Expected 404 for non-existent dossier, got {response.status_code}"
        print("PASS: Non-existent dossier returns 404")


class TestDossierExpressSuivi:
    """Test GET /api/dossier-express/suivi/{dossier_id} - Client tracking endpoint"""
    
    def test_suivi_completed_dossier_7_steps(self):
        """Verify suivi endpoint returns 7 completed steps and 'Rapport disponible' message"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{DOSSIER_ID_1}")
        print(f"Suivi response: {response.status_code} - {response.text[:800]}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify status
        assert data.get("status") == "completed", f"Expected status=completed, got {data.get('status')}"
        
        # Verify 7 steps exist
        steps = data.get("steps", [])
        assert len(steps) == 7, f"Expected 7 steps, got {len(steps)}"
        
        # Verify all steps are completed
        completed_steps = [s for s in steps if s.get("status") == "completed"]
        assert len(completed_steps) == 7, f"Expected 7 completed steps, got {len(completed_steps)}"
        
        # Verify message contains 'Rapport disponible'
        message = data.get("message", "")
        assert "disponible" in message.lower() or "rapport" in message.lower(), \
            f"Expected message about rapport disponible, got: {message}"
        
        # Print step details
        print("Steps:")
        for i, step in enumerate(steps):
            print(f"  {i+1}. {step.get('key')}: {step.get('label')} - {step.get('status')}")
        
        print(f"PASS: Suivi shows 7 completed steps with message: {message[:100]}")
    
    def test_suivi_has_download_url_when_completed(self):
        """Verify completed dossier has download_url in suivi response"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{DOSSIER_ID_1}")
        
        assert response.status_code == 200
        data = response.json()
        
        if data.get("status") == "completed":
            # Download URL may or may not be present depending on S3 config
            # But if present, it should be a valid URL
            download_url = data.get("download_url")
            if download_url:
                assert download_url.startswith("http"), f"Invalid download URL: {download_url}"
                print(f"PASS: Download URL present: {download_url[:80]}...")
            else:
                print("INFO: No download_url (S3 not configured - expected)")
    
    def test_suivi_nonexistent_dossier(self):
        """Verify 404 for non-existent dossier in suivi"""
        fake_id = "nonexistent-suivi-12345"
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{fake_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Non-existent dossier suivi returns 404")


class TestAdminDossierExpress:
    """Test GET /api/admin/dossier-express - Admin list endpoint"""
    
    def test_admin_dossier_list_requires_auth(self):
        """Verify admin endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express")
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("PASS: Admin dossier-express requires auth")
    
    def test_admin_dossier_list_with_auth(self, auth_headers):
        """Verify admin can see dossier list with completed dossiers"""
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express", headers=auth_headers)
        print(f"Admin dossier-express response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify structure
        assert "items" in data, "Response should have 'items' key"
        assert "stats" in data, "Response should have 'stats' key"
        
        items = data.get("items", [])
        stats = data.get("stats", {})
        
        print(f"Stats: {stats}")
        print(f"Total items: {len(items)}")
        
        # Verify at least one completed dossier exists
        completed_count = stats.get("completed", 0)
        assert completed_count > 0, f"Expected at least 1 completed dossier, got {completed_count}"
        
        # Look for our test dossier in the list
        found_dossier = None
        for item in items:
            if DOSSIER_ID_1 in str(item.get("id", "")):
                found_dossier = item
                break
        
        if found_dossier:
            print(f"Found test dossier: {found_dossier.get('id')}")
            assert found_dossier.get("status") == "completed", "Test dossier should be completed"
        else:
            print(f"INFO: Test dossier {DOSSIER_ID_1} not in first page of results")
        
        print(f"PASS: Admin dossier-express returns {len(items)} items, {completed_count} completed")


class TestPremiumAnalysesEntry:
    """Test MongoDB premium_analyses entry for Dossier Express"""
    
    def test_premium_analyses_has_dossier_express_type(self, auth_headers):
        """Verify premium_analyses contains entry with type='dossier_express' and relecture_expert_required=True"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        items = data.get("items", [])
        
        # Find dossier_express entries
        de_entries = [i for i in items if i.get("type") == "dossier_express"]
        
        assert len(de_entries) > 0, "Expected at least 1 dossier_express entry in premium_analyses"
        
        # Verify relecture_expert_required is True
        for entry in de_entries[:3]:  # Check first 3
            relecture = entry.get("relecture_expert_required")
            assert relecture is True, f"Expected relecture_expert_required=True, got {relecture}"
            print(f"  Entry {entry.get('id', 'N/A')[:8]}: type={entry.get('type')}, relecture={relecture}")
        
        print(f"PASS: Found {len(de_entries)} dossier_express entries with relecture_expert_required=True")


class TestLLMHealth:
    """Test LLM health endpoint"""
    
    def test_llm_health_operational(self):
        """Verify LLM service is operational (Emergent fallback)"""
        response = requests.get(f"{BASE_URL}/api/health/llm")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        operational = data.get("operational")
        reason = data.get("reason", "")
        
        assert operational is True, f"LLM should be operational, got operational={operational}, reason={reason}"
        print(f"PASS: LLM health check - operational={operational}, reason={reason}")


class TestServicesStatus:
    """Test admin services status endpoint"""
    
    def test_services_status(self, auth_headers):
        """Verify services-status returns expected services"""
        response = requests.get(f"{BASE_URL}/api/admin/services-status", headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        services = data.get("services", data)  # May be nested or direct
        
        # Expected services
        expected = ["ia_anthropic", "database"]
        
        for svc in expected:
            assert svc in services or any(svc in str(s) for s in services.keys() if isinstance(services, dict)), \
                f"Expected service '{svc}' in response"
        
        # Check IA status
        ia_status = services.get("ia_anthropic", {})
        if isinstance(ia_status, dict):
            print(f"IA Anthropic: status={ia_status.get('status')}, mode={ia_status.get('mode')}")
            assert ia_status.get("status") == "ok", f"IA should be ok, got {ia_status.get('status')}"
        
        print(f"PASS: Services status returned {len(services)} services")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
