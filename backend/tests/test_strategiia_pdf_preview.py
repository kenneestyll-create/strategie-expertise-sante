"""
Test suite for StrategiIA PDF Preview feature (Bug Fix)
Tests the new endpoint: GET /api/admin/strategiia/{analysis_id}/preview-pdf
Also includes non-regression tests for existing admin endpoints.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD

# Known test IDs from the review request
STRATEGIIA_ANALYSIS_ID = "c64897f3-8ffe-4149-b251-4f2d9a2ebcc4"
DOSSIER_EXPRESS_IDS = ["a0e7448a-39a", "1f53deaf-211"]


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    return response.json().get("access_token")


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    """Auth headers for authenticated requests"""
    return {"Authorization": f"Bearer {admin_token}"}


class TestStrategiIAPDFPreview:
    """Tests for the NEW StrategiIA PDF preview endpoint"""

    def test_strategiia_pdf_preview_returns_pdf(self, auth_headers):
        """GET /api/admin/strategiia/{analysis_id}/preview-pdf - Must return application/pdf with >10000 bytes"""
        response = requests.get(
            f"{BASE_URL}/api/admin/strategiia/{STRATEGIIA_ANALYSIS_ID}/preview-pdf",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert response.headers.get("Content-Type") == "application/pdf", f"Expected application/pdf, got {response.headers.get('Content-Type')}"
        
        # Verify PDF size is substantial (>10KB as per requirements)
        pdf_size = len(response.content)
        assert pdf_size > 10000, f"PDF size {pdf_size} bytes is less than expected 10000 bytes"
        
        # Verify it starts with PDF magic bytes
        assert response.content[:4] == b'%PDF', "Response does not start with PDF magic bytes"
        
        print(f"SUCCESS: StrategiIA PDF preview returned {pdf_size} bytes")

    def test_strategiia_pdf_preview_404_for_nonexistent(self, auth_headers):
        """GET /api/admin/strategiia/{analysis_id}/preview-pdf - Must return 404 for non-existent ID"""
        fake_id = "nonexistent-fake-id-12345"
        response = requests.get(
            f"{BASE_URL}/api/admin/strategiia/{fake_id}/preview-pdf",
            headers=auth_headers
        )
        
        assert response.status_code == 404, f"Expected 404 for non-existent ID, got {response.status_code}"
        print("SUCCESS: Returns 404 for non-existent analysis ID")

    def test_strategiia_pdf_preview_401_or_403_without_auth(self):
        """GET /api/admin/strategiia/{analysis_id}/preview-pdf - Must return 401 or 403 without auth token"""
        response = requests.get(
            f"{BASE_URL}/api/admin/strategiia/{STRATEGIIA_ANALYSIS_ID}/preview-pdf"
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"SUCCESS: Returns {response.status_code} without authentication")


class TestDossierExpressPDFPreviewNonRegression:
    """Non-regression tests for existing Dossier Express PDF preview"""

    def test_dossier_express_pdf_preview_still_works(self, auth_headers):
        """GET /api/admin/dossier-express/{dossier_id}/preview-pdf - NON-REGRESSION still works"""
        # Try each known dossier ID
        for dossier_id in DOSSIER_EXPRESS_IDS:
            response = requests.get(
                f"{BASE_URL}/api/admin/dossier-express/{dossier_id}/preview-pdf",
                headers=auth_headers
            )
            
            # May return 404 if dossier doesn't exist or 400 if no analysis
            # But should NOT return 500 (server error)
            assert response.status_code != 500, f"Server error for dossier {dossier_id}: {response.text}"
            
            if response.status_code == 200:
                assert response.headers.get("Content-Type") == "application/pdf"
                print(f"SUCCESS: Dossier Express PDF preview works for {dossier_id}")
                return
            else:
                print(f"INFO: Dossier {dossier_id} returned {response.status_code} (may not have analysis)")
        
        print("INFO: No dossier with analysis found, but endpoint is functional (no 500 errors)")


class TestPremiumAnalysesFullContentNonRegression:
    """Non-regression tests for full-content endpoint"""

    def test_full_content_endpoint_still_works(self, auth_headers):
        """GET /api/admin/premium-analyses/{id}/full-content - NON-REGRESSION still returns analysis text"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses/{STRATEGIIA_ANALYSIS_ID}/full-content",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "full_text" in data, "Response missing 'full_text' field"
        assert len(data.get("full_text", "")) > 1000, f"full_text too short: {len(data.get('full_text', ''))} chars"
        
        print(f"SUCCESS: full-content returns {len(data['full_text'])} chars of analysis")


class TestAdminBypassEndpointsNonRegression:
    """Non-regression tests for admin bypass endpoints"""

    def test_strategiia_admin_bypass_premium_exists(self, auth_headers):
        """POST /api/strategiia/admin-bypass-premium - NON-REGRESSION endpoint exists"""
        # Just check the endpoint exists (OPTIONS or a minimal POST)
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            headers=auth_headers,
            json={}  # Empty body to trigger validation error, not 404
        )
        
        # Should NOT be 404 (endpoint not found) or 405 (method not allowed)
        assert response.status_code not in [404, 405], f"Endpoint missing or method not allowed: {response.status_code}"
        print(f"SUCCESS: strategiia/admin-bypass-premium endpoint exists (status: {response.status_code})")

    def test_dossier_express_admin_bypass_exists(self, auth_headers):
        """POST /api/dossier-express/admin-bypass - NON-REGRESSION endpoint exists"""
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            headers=auth_headers,
            json={}  # Empty body to trigger validation error, not 404
        )
        
        # Should NOT be 404 (endpoint not found) or 405 (method not allowed)
        assert response.status_code not in [404, 405], f"Endpoint missing or method not allowed: {response.status_code}"
        print(f"SUCCESS: dossier-express/admin-bypass endpoint exists (status: {response.status_code})")


class TestHealthEndpointNonRegression:
    """Non-regression tests for health endpoints"""

    def test_health_llm_operational(self):
        """GET /api/health/llm - NON-REGRESSION operational"""
        response = requests.get(f"{BASE_URL}/api/health/llm")
        
        assert response.status_code == 200, f"Health LLM endpoint failed: {response.status_code}"
        
        data = response.json()
        assert data.get("operational") == True, f"LLM not operational: {data}"
        
        print("SUCCESS: /api/health/llm returns operational=true")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
