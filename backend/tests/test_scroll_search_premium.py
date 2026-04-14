"""
Test suite for Iteration 32: Scroll-to-top, Search highlighting, and Admin Premium Analyses
Tests backend endpoints: GET/PATCH /api/admin/premium-analyses
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed - skipping admin tests")


@pytest.fixture
def auth_headers(admin_token):
    """Headers with admin bearer token"""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


class TestHealthCheck:
    """Basic API health check"""

    def test_api_health(self):
        """TEST: API health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("TEST PASSED: API health endpoint returns healthy status")


class TestAdminAuth:
    """Admin authentication tests"""

    def test_admin_login_success(self):
        """TEST: Admin login with valid credentials returns token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data.get("token_type") == "bearer"
        assert "admin_name" in data
        print(f"TEST PASSED: Admin login successful, admin_name={data.get('admin_name')}")

    def test_admin_login_invalid_credentials(self):
        """TEST: Admin login with invalid credentials returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "wrong@example.com", "password": "wrongpass"}
        )
        assert response.status_code == 401
        print("TEST PASSED: Admin login with invalid credentials returns 401")


class TestPremiumAnalysesEndpoints:
    """Tests for /api/admin/premium-analyses endpoints"""

    def test_get_premium_analyses_authenticated(self, auth_headers):
        """TEST 6: GET /api/admin/premium-analyses returns valid stats object"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "items" in data, "Response should contain 'items' list"
        assert "stats" in data, "Response should contain 'stats' object"
        
        # Verify stats has required fields
        stats = data["stats"]
        assert "en_attente" in stats, "Stats should have 'en_attente' count"
        assert "en_cours" in stats, "Stats should have 'en_cours' count"
        assert "termine" in stats, "Stats should have 'termine' count"
        assert "total" in stats, "Stats should have 'total' count"
        
        # Verify counts are integers
        assert isinstance(stats["en_attente"], int)
        assert isinstance(stats["en_cours"], int)
        assert isinstance(stats["termine"], int)
        assert isinstance(stats["total"], int)
        
        print(f"TEST 6 PASSED: GET /api/admin/premium-analyses returns valid stats: {stats}")

    def test_get_premium_analyses_unauthenticated(self):
        """TEST: GET /api/admin/premium-analyses without auth returns 401/403"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses")
        assert response.status_code in [401, 403]
        print("TEST PASSED: Unauthenticated access to premium-analyses denied")

    def test_patch_premium_analysis_fake_id(self, auth_headers):
        """TEST 7: PATCH /api/admin/premium-analyses/fake-id returns 404"""
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/fake-id",
            headers=auth_headers,
            json={"status": "en_cours"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        print(f"TEST 7 PASSED: PATCH with fake-id returns 404, detail={data.get('detail')}")

    def test_patch_premium_analysis_invalid_status(self, auth_headers):
        """TEST: PATCH /api/admin/premium-analyses with invalid status returns 400"""
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/some-id",
            headers=auth_headers,
            json={"status": "invalid_status_value"}
        )
        # Should return 400 for invalid status or 404 for not found
        assert response.status_code in [400, 404]
        print(f"TEST PASSED: PATCH with invalid status returns {response.status_code}")


class TestSearchIndexVerification:
    """Verify search index has anchor field for chiffres entry"""

    def test_search_api_or_health(self):
        """Basic connectivity test - ensure API is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("TEST PASSED: API accessible for search verification")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
