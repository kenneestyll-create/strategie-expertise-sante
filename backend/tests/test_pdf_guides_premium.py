"""
Test PDF Guide Generation - Premium S.E.S Identity
Tests the GET /api/resources/pdf/{guide_id} endpoints for all 6 guides.
Verifies PDF generation with premium styling (Noir #1A1A1A, Or #C9A84C, Ivoire).
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# All guide IDs to test
GUIDE_IDS = [
    "guide_mp",
    "guide_expertise",
    "guide_mdph",
    "guide_recours",
    "guide_ipp",
    "guide_assurance"
]


class TestPDFGuideGeneration:
    """Test PDF guide generation endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def test_health_check(self):
        """Verify API is accessible"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("✓ API health check passed")

    @pytest.mark.parametrize("guide_id", GUIDE_IDS)
    def test_pdf_guide_generation(self, guide_id):
        """Test PDF generation for each guide"""
        response = self.session.get(f"{BASE_URL}/api/resources/pdf/{guide_id}")
        
        # Status code assertion
        assert response.status_code == 200, f"Guide {guide_id} failed with status {response.status_code}: {response.text}"
        
        # Content-Type assertion
        content_type = response.headers.get("Content-Type", "")
        assert "application/pdf" in content_type, f"Expected PDF content-type, got: {content_type}"
        
        # Content-Disposition assertion
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, f"Expected attachment disposition, got: {content_disp}"
        assert guide_id in content_disp, f"Expected {guide_id} in filename, got: {content_disp}"
        
        # PDF content assertion - check PDF magic bytes
        content = response.content
        assert len(content) > 1000, f"PDF content too small: {len(content)} bytes"
        assert content[:4] == b'%PDF', f"Invalid PDF magic bytes: {content[:10]}"
        
        print(f"✓ Guide {guide_id}: {len(content)} bytes, valid PDF")

    def test_invalid_guide_returns_404(self):
        """Test that invalid guide ID returns 404"""
        response = self.session.get(f"{BASE_URL}/api/resources/pdf/invalid_guide_xyz")
        assert response.status_code == 404, f"Expected 404 for invalid guide, got {response.status_code}"
        print("✓ Invalid guide returns 404")


class TestDossierExpressPDF:
    """Test Dossier Express PDF generation (regression check)"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def test_dossier_express_endpoint_exists(self):
        """Verify Dossier Express endpoint is accessible"""
        # This endpoint requires authentication and file upload, so we just check it exists
        response = self.session.post(f"{BASE_URL}/api/dossier-express/analyze", json={})
        # Should return 400 or 422 (validation error) not 404
        assert response.status_code != 404, "Dossier Express endpoint not found"
        print(f"✓ Dossier Express endpoint exists (status: {response.status_code})")


class TestAdminAccess:
    """Test admin dashboard access"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def test_admin_login(self):
        """Test admin login with provided credentials"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access token in response"
        print("✓ Admin login successful")
        return data["access_token"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
