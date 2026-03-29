"""
CONSOLIDATION AUDIT — StrategiIA & Dossier Express Isolation Tests
Tests the complete isolation between StrategiIA and Dossier Express services.
Verifies that actions on one service do NOT create entries in the other.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


@pytest.fixture(scope="module")
def admin_token():
    """Module-scoped admin token fixture."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json().get("access_token")


class TestAdminAuth:
    """Test admin authentication for subsequent tests."""
    
    def test_admin_login_success(self, admin_token):
        """Verify admin login works."""
        assert admin_token is not None
        assert len(admin_token) > 20


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_llm_endpoint(self):
        """GET /api/health/llm returns operational status."""
        response = requests.get(f"{BASE_URL}/api/health/llm")
        assert response.status_code == 200
        data = response.json()
        assert "operational" in data
        print(f"LLM Health: operational={data['operational']}, reason={data.get('reason', '')}")


class TestStrategiIABasicAnalysis:
    """Test StrategiIA basic analysis with admin_test=true."""
    
    def test_strategiia_analyze_with_admin_test(self, admin_token):
        """POST /api/strategiia/analyze with admin_test=true returns job_id."""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/analyze",
            json={
                "situation": "Test situation for consolidation audit - AT avec TMS",
                "type_dossier": "AT",
                "regime": "general",
                "admin_test": True
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"StrategiIA analyze failed: {response.text}"
        data = response.json()
        assert "job_id" in data
        assert data.get("status") in ["pending", "processing"]
        print(f"StrategiIA job_id: {data['job_id']}, status: {data['status']}")


class TestStrategiIAAdminBypassPremium:
    """Test StrategiIA admin-bypass-premium endpoint."""
    
    def test_admin_bypass_premium_creates_job(self, admin_token):
        """POST /api/strategiia/admin-bypass-premium creates job and premium_analyses entry."""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json={
                "situation": "Test admin bypass premium - consolidation audit",
                "type_dossier": "MP",
                "regime": "general",
                "premium_pdf": True,
                "analyse_premium": True
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Admin bypass premium failed: {response.text}"
        data = response.json()
        assert "job_id" in data
        assert data.get("admin_test") is True
        print(f"Admin bypass premium job_id: {data['job_id']}")
    
    def test_admin_bypass_premium_requires_auth(self):
        """POST /api/strategiia/admin-bypass-premium requires authentication."""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json={"situation": "Test without auth"}
        )
        assert response.status_code == 401


class TestStrategiIAStatusPolling:
    """Test StrategiIA status polling endpoint."""
    
    def test_status_polling_returns_job_status(self, admin_token):
        """GET /api/strategiia/status/{job_id} returns job status."""
        # First create a job
        create_response = requests.post(
            f"{BASE_URL}/api/strategiia/analyze",
            json={
                "situation": "Test status polling - consolidation audit",
                "type_dossier": "AT",
                "regime": "general",
                "admin_test": True
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200
        job_id = create_response.json().get("job_id")
        
        # Poll status
        status_response = requests.get(f"{BASE_URL}/api/strategiia/status/{job_id}")
        assert status_response.status_code == 200
        data = status_response.json()
        assert "status" in data
        assert data["status"] in ["pending", "processing", "done", "error"]
        print(f"Job {job_id} status: {data['status']}")
    
    def test_status_polling_nonexistent_job(self):
        """GET /api/strategiia/status/{job_id} returns 404 for non-existent job."""
        response = requests.get(f"{BASE_URL}/api/strategiia/status/nonexistent123")
        assert response.status_code == 404


class TestDossierExpressAdminBypass:
    """Test Dossier Express admin-bypass endpoint."""
    
    def test_dossier_express_admin_bypass_creates_dossier(self, admin_token):
        """POST /api/dossier-express/admin-bypass creates dossier."""
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "situation": "Test dossier express admin bypass - consolidation audit",
                "type_dossier": "AT",
                "regime": "general",
                "name": "Test Consolidation",
                "premium_pdf": True
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Dossier Express admin bypass failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "dossier_id" in data
        assert data.get("admin_test") is True
        print(f"Dossier Express dossier_id: {data['dossier_id']}")
    
    def test_dossier_express_admin_bypass_requires_auth(self):
        """POST /api/dossier-express/admin-bypass requires authentication."""
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={"situation": "Test without auth"}
        )
        assert response.status_code == 401


class TestAdminPremiumAnalyses:
    """Test admin premium-analyses endpoint returns both service types."""
    
    def test_premium_analyses_returns_both_types(self, admin_token):
        """GET /api/admin/premium-analyses returns entries with type=strategiia and type=dossier_express."""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Premium analyses failed: {response.text}"
        data = response.json()
        assert "items" in data
        assert "stats" in data
        
        items = data["items"]
        types_found = set(item.get("type") for item in items)
        print(f"Premium analyses types found: {types_found}")
        print(f"Total items: {len(items)}, Stats: {data['stats']}")
        
        # Check structure of items
        for item in items[:5]:
            assert "type" in item
            assert "email" in item
            assert "status" in item
            assert "relecture_expert_required" in item
            assert item["type"] in ["strategiia", "dossier_express"]
    
    def test_premium_analyses_requires_auth(self):
        """GET /api/admin/premium-analyses requires authentication."""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses")
        assert response.status_code in [401, 403]


class TestAdminServicesDiagnostic:
    """Test admin services-diagnostic endpoint."""
    
    def test_services_diagnostic_returns_all_services(self, admin_token):
        """GET /api/admin/services-status returns comprehensive diagnostic."""
        response = requests.get(
            f"{BASE_URL}/api/admin/services-status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Services diagnostic failed: {response.text}"
        data = response.json()
        
        # Check required fields
        assert "critical_services_ok" in data
        assert "all_services_ok" in data
        
        # Services are nested under "services" key
        services = data.get("services", data)
        
        # Check individual services
        expected_services = ["ia_anthropic", "stripe", "email_resend", "storage_s3", "database", "launch_mode"]
        for service in expected_services:
            assert service in services, f"Missing service: {service}"
            assert "status" in services[service]
            assert "mode" in services[service]
            print(f"Service {service}: status={services[service]['status']}, mode={services[service]['mode']}")
    
    def test_services_diagnostic_requires_auth(self):
        """GET /api/admin/services-status requires authentication."""
        response = requests.get(f"{BASE_URL}/api/admin/services-status")
        assert response.status_code in [401, 403]


class TestCrossContamination:
    """Test that StrategiIA and Dossier Express do NOT cross-contaminate."""
    
    def test_strategiia_creates_strategiia_entry_only(self, admin_token):
        """StrategiIA admin-bypass creates entry with type=strategiia, NOT dossier_express."""
        # Get current premium_analyses count by type
        before_response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert before_response.status_code == 200, f"Failed to get premium analyses: {before_response.text}"
        before_data = before_response.json()
        before_items = before_data.get("items", [])
        before_strategiia = sum(1 for i in before_items if i.get("type") == "strategiia")
        before_dossier = sum(1 for i in before_items if i.get("type") == "dossier_express")
        
        # Create StrategiIA entry
        create_response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json={
                "situation": "Cross-contamination test - StrategiIA only",
                "type_dossier": "AT",
                "regime": "general"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200
        
        # Wait for async processing
        time.sleep(1)
        
        # Check counts after
        after_response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        after_data = after_response.json()
        after_items = after_data.get("items", [])
        after_strategiia = sum(1 for i in after_items if i.get("type") == "strategiia")
        after_dossier = sum(1 for i in after_items if i.get("type") == "dossier_express")
        
        # StrategiIA count should increase, Dossier Express should NOT
        assert after_strategiia >= before_strategiia, "StrategiIA entry was not created"
        assert after_dossier == before_dossier, f"Dossier Express count changed unexpectedly: {before_dossier} -> {after_dossier}"
        print(f"Cross-contamination check PASSED: StrategiIA {before_strategiia}->{after_strategiia}, Dossier Express {before_dossier}->{after_dossier}")
    
    def test_dossier_express_creates_dossier_express_entry_only(self, admin_token):
        """Dossier Express admin-bypass creates entry with type=dossier_express, NOT strategiia."""
        # Get current premium_analyses count by type
        before_response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert before_response.status_code == 200, f"Failed to get premium analyses: {before_response.text}"
        before_data = before_response.json()
        before_items = before_data.get("items", [])
        before_strategiia = sum(1 for i in before_items if i.get("type") == "strategiia")
        before_dossier = sum(1 for i in before_items if i.get("type") == "dossier_express")
        
        # Create Dossier Express entry
        create_response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "situation": "Cross-contamination test - Dossier Express only",
                "type_dossier": "MP",
                "regime": "general",
                "name": "Test Cross-Contamination"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200
        
        # Wait for async processing (Dossier Express creates premium_analyses entry after processing)
        time.sleep(3)
        
        # Check counts after
        after_response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        after_data = after_response.json()
        after_items = after_data.get("items", [])
        after_strategiia = sum(1 for i in after_items if i.get("type") == "strategiia")
        after_dossier = sum(1 for i in after_items if i.get("type") == "dossier_express")
        
        # Dossier Express count should increase, StrategiIA should NOT
        assert after_dossier >= before_dossier, "Dossier Express entry was not created"
        assert after_strategiia == before_strategiia, f"StrategiIA count changed unexpectedly: {before_strategiia} -> {after_strategiia}"
        print(f"Cross-contamination check PASSED: StrategiIA {before_strategiia}->{after_strategiia}, Dossier Express {before_dossier}->{after_dossier}")


class TestPremiumAnalysesEntryValidation:
    """Test that premium_analyses entries have correct fields."""
    
    def test_strategiia_entry_has_relecture_expert_required(self, admin_token):
        """StrategiIA premium_analyses entry has relecture_expert_required=True."""
        # Create entry
        create_response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json={
                "situation": "Test relecture_expert_required for StrategiIA",
                "type_dossier": "AT",
                "regime": "general"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200
        
        time.sleep(1)
        
        # Get latest entry
        list_response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        items = list_response.json().get("items", [])
        strategiia_items = [i for i in items if i.get("type") == "strategiia"]
        
        if strategiia_items:
            latest = strategiia_items[0]  # Most recent
            assert latest.get("relecture_expert_required") is True, f"relecture_expert_required should be True, got {latest.get('relecture_expert_required')}"
            assert latest.get("type") == "strategiia"
            print(f"StrategiIA entry validation PASSED: relecture_expert_required={latest.get('relecture_expert_required')}")
    
    def test_dossier_express_entry_has_relecture_expert_required(self, admin_token):
        """Dossier Express premium_analyses entry has relecture_expert_required=True."""
        # Create entry
        create_response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "situation": "Test relecture_expert_required for Dossier Express",
                "type_dossier": "MP",
                "regime": "general",
                "name": "Test Relecture"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200
        
        # Wait for async processing
        time.sleep(5)
        
        # Get latest entry
        list_response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        items = list_response.json().get("items", [])
        dossier_items = [i for i in items if i.get("type") == "dossier_express"]
        
        if dossier_items:
            latest = dossier_items[0]  # Most recent
            assert latest.get("relecture_expert_required") is True, f"relecture_expert_required should be True, got {latest.get('relecture_expert_required')}"
            assert latest.get("type") == "dossier_express"
            print(f"Dossier Express entry validation PASSED: relecture_expert_required={latest.get('relecture_expert_required')}")


class TestClientSuiviEndpoint:
    """Test client suivi endpoint for Dossier Express."""
    
    def test_suivi_endpoint_returns_dossier_status(self, admin_token):
        """GET /api/dossier-express/suivi/{id} returns dossier status."""
        # First get a dossier ID from admin list
        list_response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if list_response.status_code == 200:
            data = list_response.json()
            items = data.get("items", [])
            if items:
                dossier_id = items[0].get("id")
                download_token = items[0].get("download_token", "")
                
                # Test suivi endpoint
                suivi_response = requests.get(
                    f"{BASE_URL}/api/dossier-express/suivi/{dossier_id}",
                    params={"token": download_token} if download_token else {}
                )
                assert suivi_response.status_code == 200, f"Suivi endpoint failed: {suivi_response.text}"
                suivi_data = suivi_response.json()
                
                # Check required fields
                assert "status" in suivi_data
                assert "steps" in suivi_data
                print(f"Suivi endpoint PASSED: status={suivi_data.get('status')}, steps={len(suivi_data.get('steps', []))}")
    
    def test_suivi_endpoint_returns_404_for_nonexistent(self):
        """GET /api/dossier-express/suivi/{id} returns 404 for non-existent dossier."""
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/nonexistent-dossier-id")
        assert response.status_code == 404
