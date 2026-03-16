"""
Test PDF guide download endpoints - Bug fix verification
Tests GET /api/resources/pdf/{guide_id} endpoint that generates PDFs on-the-fly
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# All valid guide IDs as defined in pdf_guides.py
GUIDE_IDS = [
    "guide_mp",
    "guide_expertise", 
    "guide_mdph",
    "guide_recours",
    "guide_ipp",
    "guide_assurance"
]


class TestPDFGuideDownload:
    """Tests for PDF guide download endpoints - No authentication required"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/pdf"})

    # Test each guide returns 200 with PDF content
    @pytest.mark.parametrize("guide_id", GUIDE_IDS)
    def test_guide_pdf_returns_200(self, guide_id):
        """Each valid guide ID should return HTTP 200"""
        response = self.session.get(f"{BASE_URL}/api/resources/pdf/{guide_id}")
        assert response.status_code == 200, f"Expected 200 for {guide_id}, got {response.status_code}"
        print(f"PASS: {guide_id} returns 200")

    @pytest.mark.parametrize("guide_id", GUIDE_IDS)
    def test_guide_pdf_content_type(self, guide_id):
        """Each guide should return application/pdf content type"""
        response = self.session.get(f"{BASE_URL}/api/resources/pdf/{guide_id}")
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type, f"Expected application/pdf, got {content_type}"
        print(f"PASS: {guide_id} has correct content-type: {content_type}")

    @pytest.mark.parametrize("guide_id", GUIDE_IDS) 
    def test_guide_pdf_content_disposition(self, guide_id):
        """Each guide should have Content-Disposition with attachment filename"""
        response = self.session.get(f"{BASE_URL}/api/resources/pdf/{guide_id}")
        disposition = response.headers.get("content-disposition", "")
        assert "attachment" in disposition, f"Expected attachment in disposition, got {disposition}"
        assert f'filename="{guide_id}.pdf"' in disposition, f"Expected filename {guide_id}.pdf in {disposition}"
        print(f"PASS: {guide_id} has correct Content-Disposition: {disposition}")

    @pytest.mark.parametrize("guide_id", GUIDE_IDS)
    def test_guide_pdf_size_not_empty(self, guide_id):
        """Each PDF should be > 1000 bytes (not empty)"""
        response = self.session.get(f"{BASE_URL}/api/resources/pdf/{guide_id}")
        size = len(response.content)
        assert size > 1000, f"PDF {guide_id} is too small ({size} bytes), expected > 1000"
        print(f"PASS: {guide_id} has size {size} bytes (> 1000)")

    @pytest.mark.parametrize("guide_id", GUIDE_IDS)
    def test_guide_pdf_starts_with_pdf_header(self, guide_id):
        """Each PDF should start with %PDF magic bytes"""
        response = self.session.get(f"{BASE_URL}/api/resources/pdf/{guide_id}")
        # PDF files start with %PDF
        assert response.content[:4] == b'%PDF', f"PDF {guide_id} doesn't start with %PDF header"
        print(f"PASS: {guide_id} has valid PDF header")

    def test_invalid_guide_returns_404(self):
        """Invalid guide ID should return 404"""
        response = self.session.get(f"{BASE_URL}/api/resources/pdf/invalid_id")
        assert response.status_code == 404, f"Expected 404 for invalid_id, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print(f"PASS: invalid_id returns 404 with message: {data['detail']}")

    def test_nonexistent_guide_returns_404(self):
        """Non-existent guide ID should return 404"""
        response = self.session.get(f"{BASE_URL}/api/resources/pdf/guide_xyz_not_exist")
        assert response.status_code == 404
        print("PASS: non-existent guide returns 404")


class TestResourceDownloadTracking:
    """Tests that PDF downloads are tracked in the database"""
    
    def test_download_creates_tracking_record(self):
        """Downloading a PDF should create a record in resource_downloads"""
        session = requests.Session()
        
        # Download a guide - the endpoint tracks the download
        response = session.get(f"{BASE_URL}/api/resources/pdf/guide_mp")
        assert response.status_code == 200
        
        # Note: We can't directly verify the DB record without admin access,
        # but we can verify the endpoint completed successfully
        print("PASS: PDF download completed (tracking should be recorded)")

    def test_resource_download_tracking_endpoint(self):
        """POST /api/resources/download should track downloads"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Test the explicit tracking endpoint
        response = session.post(
            f"{BASE_URL}/api/resources/download",
            json={
                "resource_id": "test_resource",
                "resource_title": "Test Resource"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("PASS: Resource download tracking endpoint works")
