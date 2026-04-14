"""
Phase 1-C Refactoring Non-Regression Tests
Tests to verify the monolithic strategiia.py split into 6 files didn't break anything.

Key structural changes:
- strategiia.py: 2274 -> 590 lines (StrategiIA only)
- dossier_express.py: ~695 lines (Dossier Express only)
- utils/llm.py: Centralized LLM functions
- constants/prompts.py: All prompts
- constants/guards.py: Assertions + transition guards
- utils/document_extraction.py: OCR/PDF
- utils/notifications.py: Admin/client notifications
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD

# Existing completed dossier IDs for GET tests
COMPLETED_DOSSIER_ID_1 = "bfc7d774-b9c5-4134-962d-65a3934ae940"
COMPLETED_DOSSIER_ID_2 = "bb543247-f7f3-4a1a-8d03-93d217cc1400"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed")


@pytest.fixture
def auth_headers(admin_token):
    """Headers with admin auth token."""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


class TestLLMHealthCheck:
    """Test LLM health check endpoint."""
    
    def test_llm_health_returns_operational(self):
        """GET /api/health/llm — LLM health check returns operational=True"""
        response = requests.get(f"{BASE_URL}/api/health/llm")
        assert response.status_code == 200
        data = response.json()
        assert "operational" in data
        assert data["operational"] is True
        print(f"LLM Health: operational={data['operational']}, reason={data.get('reason', '')}")


class TestStrategiIAQuota:
    """Test StrategiIA quota endpoint."""
    
    def test_quota_returns_data(self):
        """GET /api/strategiia/quota/demo@test.com — returns quota data"""
        response = requests.get(f"{BASE_URL}/api/strategiia/quota/demo@test.com")
        assert response.status_code == 200
        data = response.json()
        assert "remaining" in data
        assert "limit" in data
        assert "used" in data
        assert data["limit"] == 3
        print(f"Quota: remaining={data['remaining']}, limit={data['limit']}, used={data['used']}")


class TestStrategiIAAdminBypass:
    """Test StrategiIA admin-bypass endpoint."""
    
    def test_admin_bypass_creates_analysis(self, auth_headers):
        """POST /api/strategiia/admin-bypass — creates StrategiIA analysis (admin auth required)"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            headers=auth_headers,
            json={
                "situation": "Test situation for non-regression testing - Phase 1-C refactoring verification",
                "type_dossier": "at",
                "regime": "general"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data.get("status") == "pending"
        assert data.get("admin_test") is True
        print(f"StrategiIA Admin Bypass: job_id={data['job_id']}, status={data['status']}")


class TestDossierExpressStatus:
    """Test Dossier Express status endpoints."""
    
    def test_status_returns_completed(self):
        """GET /api/dossier-express/status/{id} — returns completed"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/{COMPLETED_DOSSIER_ID_1}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "completed"
        assert "id" in data
        assert "email" in data
        print(f"Dossier Status: id={data['id']}, status={data['status']}")
    
    def test_suivi_returns_7_steps(self):
        """GET /api/dossier-express/suivi/{id} — returns 7 steps all completed"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{COMPLETED_DOSSIER_ID_1}")
        assert response.status_code == 200
        data = response.json()
        assert "steps" in data
        assert len(data["steps"]) == 7
        # All steps should be completed for a completed dossier
        completed_steps = [s for s in data["steps"] if s.get("status") == "completed"]
        assert len(completed_steps) == 7
        print(f"Suivi: {len(data['steps'])} steps, all completed={len(completed_steps)==7}")
    
    def test_weekly_count_returns_count(self):
        """GET /api/dossier-express/weekly-count — returns count"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/weekly-count")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "period" in data
        assert data["period"] == "week"
        assert isinstance(data["count"], int)
        print(f"Weekly Count: {data['count']} dossiers this week")


class TestAdminEndpoints:
    """Test admin endpoints for Dossier Express and Premium Analyses."""
    
    def test_admin_dossier_express_list(self, auth_headers):
        """GET /api/admin/dossier-express — lists DE dossiers with correct statuses"""
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "stats" in data
        stats = data["stats"]
        assert "total" in stats
        assert "completed" in stats
        assert "processing" in stats
        print(f"Admin DE: total={stats['total']}, completed={stats['completed']}, processing={stats['processing']}")
    
    def test_admin_premium_analyses_list(self, auth_headers):
        """GET /api/admin/premium-analyses — lists analyses with type='strategiia' AND type='dossier_express'"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        items = data["items"]
        types = set(item.get("type") for item in items)
        # Both types should be present
        assert "strategiia" in types, "Missing 'strategiia' type in premium_analyses"
        assert "dossier_express" in types, "Missing 'dossier_express' type in premium_analyses"
        print(f"Admin Premium Analyses: total={len(items)}, types={types}")


class TestAuthLogin:
    """Test authentication login."""
    
    def test_login_returns_access_token(self):
        """POST /api/auth/login with admin creds — returns access_token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        print(f"Auth Login: token_type={data['token_type']}, admin_name={data.get('admin_name')}")


class TestRouterRegistration:
    """Test that all routers are properly registered."""
    
    def test_strategiia_routes_accessible(self):
        """Verify strategiia routes are accessible"""
        # Test a strategiia-specific route
        response = requests.get(f"{BASE_URL}/api/strategiia/quota/test@test.com")
        assert response.status_code == 200
        print("StrategiIA routes: ACCESSIBLE")
    
    def test_dossier_express_routes_accessible(self):
        """Verify dossier_express routes are accessible"""
        # Test a dossier-express-specific route
        response = requests.get(f"{BASE_URL}/api/dossier-express/weekly-count")
        assert response.status_code == 200
        print("Dossier Express routes: ACCESSIBLE")


class TestCodeStructureVerification:
    """Verify code structure after refactoring."""
    
    def test_strategiia_no_dossier_express_routes(self):
        """Verify strategiia.py NO LONGER contains Dossier Express routes"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "dossier-express", "/app/backend/routes/strategiia.py"],
            capture_output=True, text=True
        )
        # Should only find comments/references, not actual routes
        count = int(result.stdout.strip()) if result.returncode == 0 else 0
        # Check for actual route definitions
        result2 = subprocess.run(
            ["grep", "-c", "@router.*dossier-express", "/app/backend/routes/strategiia.py"],
            capture_output=True, text=True
        )
        route_count = int(result2.stdout.strip()) if result2.returncode == 0 else 0
        assert route_count == 0, f"Found {route_count} Dossier Express routes in strategiia.py"
        print(f"strategiia.py: {route_count} DE routes (expected 0)")
    
    def test_dossier_express_no_strategiia_routes(self):
        """Verify dossier_express.py NO LONGER contains StrategiIA routes"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "@router.*strategiia", "/app/backend/routes/dossier_express.py"],
            capture_output=True, text=True
        )
        route_count = int(result.stdout.strip()) if result.returncode == 0 else 0
        assert route_count == 0, f"Found {route_count} StrategiIA routes in dossier_express.py"
        print(f"dossier_express.py: {route_count} StrategiIA routes (expected 0)")
    
    def test_routes_init_includes_dossier_express_router(self):
        """Verify routes/__init__.py includes dossier_express_router"""
        with open("/app/backend/routes/__init__.py", "r") as f:
            content = f.read()
        assert "dossier_express_router" in content, "dossier_express_router not found in routes/__init__.py"
        assert "from routes.dossier_express import router as dossier_express_router" in content
        print("routes/__init__.py: dossier_express_router INCLUDED")


class TestServerStartup:
    """Test that server starts successfully (no circular imports)."""
    
    def test_server_responds(self):
        """Backend import chain: no circular imports (server starts successfully)"""
        # If we can reach any endpoint, the server started successfully
        response = requests.get(f"{BASE_URL}/api/health/llm")
        assert response.status_code == 200
        print("Server: RUNNING (no circular imports)")


class TestDossierExpressAdminBypass:
    """Test Dossier Express admin-bypass endpoint (NEW - added in iteration 150)."""
    
    def test_admin_bypass_creates_dossier(self, auth_headers):
        """POST /api/dossier-express/admin-bypass — creates Dossier Express analysis (admin auth)
        
        This endpoint was added to dossier_express.py (lines 687-741) to allow admin testing
        without going through Stripe checkout.
        """
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            headers=auth_headers,
            json={
                "situation": "Test situation for admin bypass - iteration 150 verification",
                "name": "Test Admin Bypass",
                "type_dossier": "at",
                "regime": "general"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Verify response structure matches expected format
        assert "dossier_id" in data, "Response must contain dossier_id"
        assert "status" in data, "Response must contain status"
        assert "admin_test" in data, "Response must contain admin_test flag"
        assert data["status"] == "processing", f"Expected status='processing', got '{data['status']}'"
        assert data["admin_test"] is True, "admin_test flag should be True"
        print(f"Dossier Express Admin Bypass: dossier_id={data['dossier_id']}, status={data['status']}, admin_test={data['admin_test']}")
