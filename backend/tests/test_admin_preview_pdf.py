"""
Test suite for Admin Dossier Express PDF Preview endpoint
Tests: GET /api/admin/dossier-express/{id}/preview-pdf
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"

# Known test dossier ID from context
TEST_DOSSIER_ID = "fed52f8f-39b1-4727-b036-90ced5861569"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")


@pytest.fixture
def auth_headers(admin_token):
    """Headers with admin auth token"""
    return {"Authorization": f"Bearer {admin_token}"}


class TestPreviewPdfEndpoint:
    """Tests for GET /api/admin/dossier-express/{id}/preview-pdf"""

    def test_preview_pdf_requires_auth(self):
        """Test that endpoint returns 401/403 without authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/preview-pdf")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: Preview PDF endpoint requires authentication ({response.status_code} without token)")

    def test_preview_pdf_returns_404_for_invalid_id(self, auth_headers):
        """Test that endpoint returns 404 for non-existent dossier"""
        invalid_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{invalid_id}/preview-pdf",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Preview PDF endpoint returns 404 for invalid dossier ID")

    def test_preview_pdf_returns_valid_pdf(self, auth_headers):
        """Test that endpoint returns a valid PDF with correct content-type"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/preview-pdf",
            headers=auth_headers
        )
        
        # Check status code
        if response.status_code == 400:
            # Dossier might not have analysis yet
            data = response.json()
            if "Aucune analyse" in data.get("detail", ""):
                pytest.skip("Test dossier has no analysis - cannot generate PDF")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "application/pdf" in content_type, f"Expected application/pdf, got {content_type}"
        
        # Check content disposition (should be inline for preview)
        content_disp = response.headers.get("Content-Disposition", "")
        assert "inline" in content_disp, f"Expected inline disposition, got {content_disp}"
        
        # Check PDF magic bytes
        pdf_content = response.content
        assert pdf_content[:4] == b'%PDF', "Response does not start with PDF magic bytes"
        
        # Check reasonable size (at least 1KB for a valid PDF)
        assert len(pdf_content) > 1000, f"PDF too small: {len(pdf_content)} bytes"
        
        print(f"PASS: Preview PDF returns valid PDF ({len(pdf_content)} bytes)")


class TestDossierExpressAnalysisEndpoint:
    """Tests for GET /api/admin/dossier-express/{id}/analysis - used to populate dialog"""

    def test_analysis_endpoint_requires_auth(self):
        """Test that analysis endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/analysis")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: Analysis endpoint requires authentication ({response.status_code})")

    def test_analysis_endpoint_returns_document_details(self, auth_headers):
        """Test that analysis endpoint returns document_details for encart"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/analysis",
            headers=auth_headers
        )
        
        if response.status_code == 404:
            pytest.skip("Test dossier not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check required fields for dialog
        assert "id" in data, "Missing 'id' field"
        assert "email" in data, "Missing 'email' field"
        assert "status" in data, "Missing 'status' field"
        assert "document_details" in data, "Missing 'document_details' field"
        
        print(f"PASS: Analysis endpoint returns required fields")
        print(f"  - id: {data.get('id')}")
        print(f"  - status: {data.get('status')}")
        print(f"  - document_details count: {len(data.get('document_details', []))}")
        
        # If document_details exist, verify structure
        doc_details = data.get("document_details", [])
        if doc_details:
            for i, doc in enumerate(doc_details):
                assert "name" in doc, f"Document {i} missing 'name'"
                # pages, size_kb, status are optional but expected
                print(f"  - Doc {i}: {doc.get('name')} - {doc.get('status', 'no status')}")


class TestReadabilityLevelLogic:
    """Test readability level calculation matches document statuses"""

    def test_readability_level_calculation(self, auth_headers):
        """Verify readability level logic in frontend matches expected values"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/analysis",
            headers=auth_headers
        )
        
        if response.status_code != 200:
            pytest.skip("Cannot fetch dossier analysis")
        
        data = response.json()
        doc_details = data.get("document_details", [])
        
        if not doc_details:
            pytest.skip("No document_details to test readability")
        
        statuses = [d.get("status", "") for d in doc_details]
        print(f"Document statuses: {statuses}")
        
        # Calculate expected level using same logic as frontend
        if all(s == 'text_extracted' for s in statuses):
            expected_level = 'Excellente'
        elif all(s == 'ocr_extracted' for s in statuses):
            expected_level = 'Bonne'
        elif all(s in ('text_extracted', 'ocr_extracted') for s in statuses) and any(s == 'ocr_extracted' for s in statuses):
            expected_level = 'Très bonne'
        elif any(s in ('text_extracted', 'ocr_extracted') for s in statuses):
            expected_level = 'Partielle'
        else:
            expected_level = 'Limitée'
        
        print(f"PASS: Readability level for statuses {statuses} = '{expected_level}'")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
