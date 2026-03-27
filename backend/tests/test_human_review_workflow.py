"""
Test suite for Admin Human Review Workflow endpoints (Iteration 139)
Tests the new endpoints for:
- GET /api/admin/dossier-express/{dossier_id}/original-documents
- GET /api/admin/dossier-express/{dossier_id}/documents/{file_id}/download
- PUT /api/admin/dossier-express/{dossier_id}/analysis
- POST /api/admin/dossier-express/{dossier_id}/regenerate-pdf
- GET /api/admin/dossier-express/{dossier_id}/analysis (verify human_reviewed field)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test dossier ID with original_documents (created by main agent)
TEST_DOSSIER_ID = "5e4aa1ee-084b-44bb-90e3-2977989de0d1"

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


class TestAdminAuth:
    """Test admin authentication for protected endpoints"""
    
    def test_admin_login_success(self):
        """Admin login should return access_token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert len(data["access_token"]) > 0
        print(f"PASS: Admin login successful, token received")


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.text}")
    return response.json().get("access_token")


@pytest.fixture
def auth_headers(admin_token):
    """Headers with admin auth token"""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


class TestOriginalDocumentsEndpoint:
    """Test GET /api/admin/dossier-express/{dossier_id}/original-documents"""
    
    def test_get_original_documents_success(self, auth_headers):
        """Should return original_documents and document_details for valid dossier"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/original-documents",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "original_documents" in data, "Missing original_documents field"
        assert "document_details" in data, "Missing document_details field"
        assert isinstance(data["original_documents"], list)
        assert isinstance(data["document_details"], list)
        print(f"PASS: Got {len(data['original_documents'])} original documents, {len(data['document_details'])} document details")
    
    def test_get_original_documents_not_found(self, auth_headers):
        """Should return 404 for non-existent dossier"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/nonexistent-dossier-id/original-documents",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Returns 404 for non-existent dossier")
    
    def test_get_original_documents_no_auth(self):
        """Should return 401/403 without auth token"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/original-documents"
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Endpoint requires authentication")


class TestDocumentDownloadEndpoint:
    """Test GET /api/admin/dossier-express/{dossier_id}/documents/{file_id}/download"""
    
    def test_download_document_fake_storage_path(self, auth_headers):
        """Should return 500 for fake storage path (expected behavior per main agent)"""
        # The test dossier has a fake storage_path, so download will fail
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/documents/test-file-1/download",
            headers=auth_headers
        )
        # Expected: 500 because storage_path is fake
        assert response.status_code == 500, f"Expected 500 for fake storage, got {response.status_code}"
        print("PASS: Returns 500 for fake storage path (expected)")
    
    def test_download_document_not_found(self, auth_headers):
        """Should return 404 for non-existent file_id"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/documents/nonexistent-file-id/download",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Returns 404 for non-existent file_id")
    
    def test_download_document_dossier_not_found(self, auth_headers):
        """Should return 404 for non-existent dossier"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/nonexistent-dossier/documents/test-file-1/download",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Returns 404 for non-existent dossier")
    
    def test_download_document_no_auth(self):
        """Should return 401/403 without auth token"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/documents/test-file-1/download"
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Download endpoint requires authentication")


class TestUpdateAnalysisEndpoint:
    """Test PUT /api/admin/dossier-express/{dossier_id}/analysis"""
    
    def test_update_analysis_success(self, auth_headers):
        """Should update analysis and set human_reviewed=True"""
        updated_analysis = "TEST_UPDATED_ANALYSIS: This is a test analysis updated by the testing agent."
        response = requests.put(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/analysis",
            headers=auth_headers,
            json={
                "analysis": updated_analysis,
                "admin_notes": "Test notes from testing agent"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        assert "message" in data
        print(f"PASS: Analysis updated successfully - {data.get('message')}")
        
        # Verify the update persisted
        verify_response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}",
            headers=auth_headers
        )
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            assert verify_data.get("human_reviewed") == True, "human_reviewed should be True"
            assert verify_data.get("analysis") == updated_analysis, "Analysis should match updated value"
            print("PASS: Verified analysis persisted with human_reviewed=True")
    
    def test_update_analysis_empty_fails(self, auth_headers):
        """Should return 400 for empty analysis"""
        response = requests.put(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/analysis",
            headers=auth_headers,
            json={"analysis": "   "}  # Empty/whitespace only
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Returns 400 for empty analysis")
    
    def test_update_analysis_not_found(self, auth_headers):
        """Should return 404 for non-existent dossier"""
        response = requests.put(
            f"{BASE_URL}/api/admin/dossier-express/nonexistent-dossier/analysis",
            headers=auth_headers,
            json={"analysis": "Test analysis"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Returns 404 for non-existent dossier")
    
    def test_update_analysis_no_auth(self):
        """Should return 401/403 without auth token"""
        response = requests.put(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/analysis",
            json={"analysis": "Test"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Update analysis endpoint requires authentication")


class TestRegeneratePdfEndpoint:
    """Test POST /api/admin/dossier-express/{dossier_id}/regenerate-pdf"""
    
    def test_regenerate_pdf_success(self, auth_headers):
        """Should regenerate PDF without sending email"""
        response = requests.post(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/regenerate-pdf",
            headers=auth_headers,
            json={"send_email": False}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        assert "pdf_stored" in data, "Missing pdf_stored field"
        assert "email_sent" in data, "Missing email_sent field"
        assert data.get("email_sent") == False, "email_sent should be False when send_email=False"
        print(f"PASS: PDF regenerated - pdf_stored={data.get('pdf_stored')}, email_sent={data.get('email_sent')}")
    
    def test_regenerate_pdf_not_found(self, auth_headers):
        """Should return 404 for non-existent dossier"""
        response = requests.post(
            f"{BASE_URL}/api/admin/dossier-express/nonexistent-dossier/regenerate-pdf",
            headers=auth_headers,
            json={"send_email": False}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Returns 404 for non-existent dossier")
    
    def test_regenerate_pdf_no_auth(self):
        """Should return 401/403 without auth token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/regenerate-pdf",
            json={"send_email": False}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Regenerate PDF endpoint requires authentication")


class TestGetDossierAnalysis:
    """Test GET /api/admin/dossier-express/{dossier_id}/analysis returns human_reviewed and original_documents"""
    
    def test_get_dossier_has_human_reviewed_field(self, auth_headers):
        """Should return dossier with human_reviewed field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{TEST_DOSSIER_ID}/analysis",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "human_reviewed" in data, "Missing human_reviewed field"
        assert "original_documents" in data, "Missing original_documents field"
        print(f"PASS: Dossier has human_reviewed={data.get('human_reviewed')}, original_documents count={len(data.get('original_documents', []))}")
    
    def test_get_dossier_not_found(self, auth_headers):
        """Should return 404 for non-existent dossier"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/nonexistent-dossier/analysis",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Returns 404 for non-existent dossier")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
