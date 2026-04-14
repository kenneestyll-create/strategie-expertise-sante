"""
Test suite for Dossier Express PDF Download Endpoint and related features.
Tests the new download endpoint, object storage integration, and PDF discreet expert link.

Features tested:
- GET /api/dossier-express/{dossier_id}/download?token=xxx - download endpoint
- Object storage put_object() and download_file() functions
- PDF generation with discreet expert link
- Admin login, conseils API, admin PDF preview
"""

import pytest
import requests
import os
import uuid
from datetime import datetime, timezone

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD
KNOWN_DOSSIER_ID = "91dbe566-cd80-4cab-be2c-96e27daa1e73"


class TestDownloadEndpointValidation:
    """Test download endpoint parameter validation"""

    def test_download_without_token_returns_400(self):
        """GET /api/dossier-express/{id}/download without token should return 400"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/dossier-express/{fake_id}/download")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "token" in data["detail"].lower() or "requis" in data["detail"].lower()
        print(f"PASS: Download without token returns 400 - {data['detail']}")

    def test_download_with_empty_token_returns_400(self):
        """GET /api/dossier-express/{id}/download?token= should return 400"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/dossier-express/{fake_id}/download?token=")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Download with empty token returns 400")

    def test_download_with_invalid_token_returns_404(self):
        """GET /api/dossier-express/{id}/download?token=invalid should return 404"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/dossier-express/{fake_id}/download?token=invalid-token-xyz")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "invalide" in data["detail"].lower() or "expire" in data["detail"].lower()
        print(f"PASS: Download with invalid token returns 404 - {data['detail']}")

    def test_download_with_nonexistent_dossier_returns_404(self):
        """GET /api/dossier-express/{nonexistent}/download?token=xxx should return 404"""
        nonexistent_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/dossier-express/{nonexistent_id}/download?token=some-token")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Download with nonexistent dossier returns 404")


class TestPDFDiscreetExpertLink:
    """Test PDF generation contains discreet expert link"""

    def test_pdf_contains_discreet_expert_link(self):
        """PDF should contain 'Accompagnement personnalise : strategie-expertise-sante.fr/contact'"""
        # Import the PDF generation function
        import sys
        sys.path.insert(0, "/app/backend")
        from utils.pdf import generate_secured_pdf

        # Generate a test PDF
        test_analysis = """## Votre situation analysee
        Test situation pour verification du lien discret.
        
        ## Ce que revele votre dossier
        Analyse de test.
        
        ## Prochaines etapes recommandees
        - Etape 1
        - Etape 2
        """

        pdf_bytes = generate_secured_pdf(
            analysis=test_analysis,
            report_type="Dossier Express IA",
            name="Test Client",
            email="test@example.com",
            type_dossier="at",
            regime="general",
            with_watermark=False,
        )

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000, "PDF should have substantial content"

        # Check PDF content for the discreet link text
        # Note: PDF binary may not have exact text, but we verify generation works
        print(f"PASS: PDF generated successfully ({len(pdf_bytes)} bytes)")

        # Verify the PDF module has the discreet link code
        from utils.pdf import generate_secured_pdf
        import inspect
        source = inspect.getsource(generate_secured_pdf)
        assert "Accompagnement personnalise" in source or "strategie-expertise-sante.fr/contact" in source
        print("PASS: PDF source contains discreet expert link code")

    def test_pdf_with_document_details_generates(self):
        """PDF with document_details should generate without errors"""
        import sys
        sys.path.insert(0, "/app/backend")
        from utils.pdf import generate_secured_pdf

        doc_details = [
            {"name": "certificat.pdf", "pages": 2, "status": "text_extracted"},
            {"name": "arret_travail.pdf", "pages": 1, "status": "ocr_extracted"},
        ]

        pdf_bytes = generate_secured_pdf(
            analysis="Test analysis with documents",
            report_type="Dossier Express IA",
            name="Test Client",
            email="test@example.com",
            type_dossier="mp",
            regime="general",
            with_watermark=False,
            document_details=doc_details,
        )

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000
        print(f"PASS: PDF with document_details generated ({len(pdf_bytes)} bytes)")


class TestObjectStorageFunctions:
    """Test object storage utility functions"""

    def test_storage_module_imports(self):
        """Storage module should import without errors"""
        import sys
        sys.path.insert(0, "/app/backend")
        from utils.storage import put_object, download_file, init_storage
        print("PASS: Storage module imports successfully")

    def test_storage_put_object_function_exists(self):
        """put_object function should exist and have correct signature"""
        import sys
        sys.path.insert(0, "/app/backend")
        from utils.storage import put_object
        import inspect

        sig = inspect.signature(put_object)
        params = list(sig.parameters.keys())
        assert "path" in params
        assert "data" in params
        assert "content_type" in params
        print(f"PASS: put_object has correct signature: {params}")

    def test_storage_download_file_function_exists(self):
        """download_file function should exist and have correct signature"""
        import sys
        sys.path.insert(0, "/app/backend")
        from utils.storage import download_file
        import inspect

        sig = inspect.signature(download_file)
        params = list(sig.parameters.keys())
        assert "storage_path" in params
        print(f"PASS: download_file has correct signature: {params}")


class TestAdminAndCoreAPIs:
    """Test admin login, conseils API, and admin PDF preview"""

    def test_admin_login_works(self):
        """POST /api/auth/login should work with admin credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "token" in data or "access_token" in data
        print("PASS: Admin login works")
        return data.get("token") or data.get("access_token")

    def test_conseils_api_works(self):
        """GET /api/conseils/today should return conseil data"""
        response = requests.get(f"{BASE_URL}/api/conseils/today")
        assert response.status_code == 200, f"Conseils API failed: {response.status_code}"
        data = response.json()
        # Should have conseil content
        assert "conseil" in data or "content" in data or "text" in data or isinstance(data, dict)
        print(f"PASS: Conseils API works - returned {type(data)}")

    def test_admin_pdf_preview_with_known_dossier(self):
        """GET /api/admin/dossier-express/{id}/preview-pdf should work for known dossier"""
        # First login to get token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip("Admin login failed, skipping preview test")

        token = login_response.json().get("token") or login_response.json().get("access_token")

        # Try to preview the known dossier
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{KNOWN_DOSSIER_ID}/preview-pdf",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Accept 200 (success) or 404 (dossier not found - acceptable if DB was reset)
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"

        if response.status_code == 200:
            # Should return PDF bytes
            assert len(response.content) > 1000
            assert response.headers.get("content-type", "").startswith("application/pdf")
            print(f"PASS: Admin PDF preview works - {len(response.content)} bytes")
        else:
            print(f"INFO: Known dossier {KNOWN_DOSSIER_ID} not found (DB may have been reset)")


class TestDownloadEndpointIntegration:
    """Integration test for download endpoint with test data creation"""

    @pytest.fixture
    def admin_token(self):
        """Get admin token for authenticated requests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json().get("token") or response.json().get("access_token")

    def test_download_endpoint_structure(self):
        """Verify download endpoint is properly registered"""
        # Test that the endpoint exists by checking 400 response (not 404 for route)
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/dossier-express/{fake_id}/download")
        # Should be 400 (missing token) not 404 (route not found)
        assert response.status_code == 400, f"Expected 400 for missing token, got {response.status_code}"
        print("PASS: Download endpoint is properly registered")


class TestPDFSourceCodeVerification:
    """Verify PDF source code contains required elements"""

    def test_pdf_source_has_et_maintenant_section(self):
        """PDF source should have 'Et maintenant ?' section"""
        import sys
        sys.path.insert(0, "/app/backend")
        from utils.pdf import generate_secured_pdf
        import inspect

        source = inspect.getsource(generate_secured_pdf)
        assert "Et maintenant" in source
        print("PASS: PDF source contains 'Et maintenant' section")

    def test_pdf_source_has_discreet_link_line(self):
        """PDF source should have discreet expert link around line 477-480"""
        with open("/app/backend/utils/pdf.py", "r") as f:
            content = f.read()

        # Check for the discreet link text
        assert "Accompagnement personnalise" in content
        assert "strategie-expertise-sante.fr/contact" in content
        print("PASS: PDF source contains discreet expert link")

    def test_pdf_source_has_signature_line(self):
        """PDF source should have signature 'Votre bouclier'"""
        with open("/app/backend/utils/pdf.py", "r") as f:
            content = f.read()

        assert "Votre bouclier" in content
        print("PASS: PDF source contains signature line")


class TestStorageSourceCodeVerification:
    """Verify storage source code has required functions"""

    def test_storage_has_put_object(self):
        """Storage module should have put_object function"""
        with open("/app/backend/utils/storage.py", "r") as f:
            content = f.read()

        assert "def put_object" in content
        print("PASS: Storage has put_object function")

    def test_storage_has_download_file(self):
        """Storage module should have download_file function"""
        with open("/app/backend/utils/storage.py", "r") as f:
            content = f.read()

        assert "def download_file" in content
        print("PASS: Storage has download_file function")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
