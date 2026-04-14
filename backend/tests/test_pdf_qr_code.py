"""
Test PDF QR Code Implementation for Dossier Express IA
Tests the QR code generation, embedding, and related text elements in the PDF.
"""
import pytest
import requests
import os
import sys
import io

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD
KNOWN_DOSSIER_ID = "91dbe566-cd80-4cab-be2c-96e27daa1e73"


class TestPDFQRCodeGeneration:
    """Tests for QR code generation in PDF"""
    
    def test_qrcode_library_installed(self):
        """Verify qrcode library is available"""
        try:
            import qrcode
            print("SUCCESS: qrcode library is installed")
            assert True
        except ImportError:
            pytest.fail("qrcode library is not installed")
    
    def test_pdf_generation_with_qr_code(self):
        """Test PDF generation includes QR code without errors"""
        from utils.pdf import generate_secured_pdf
        
        # Generate PDF with sample analysis
        analysis = """## Votre situation analysee
        Test situation pour verification du QR code.
        
        ## Ce que revele votre dossier
        Points importants identifies.
        
        ## Prochaines etapes recommandees
        - Action 1
        - Action 2
        """
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Test User",
            email="test@example.com",
            type_dossier="at",
            regime="general",
            with_watermark=False,
            document_details=None
        )
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        print(f"SUCCESS: PDF generated with {len(pdf_bytes)} bytes")
    
    def test_pdf_contains_qr_code_image(self):
        """Test PDF contains at least 2 images (logo + QR code)"""
        from utils.pdf import generate_secured_pdf
        import pdfplumber
        
        analysis = "## Test\nSimple test content for QR verification."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="QR Test User",
            email="qr@test.com",
            type_dossier="mp",
            regime="general",
            with_watermark=False
        )
        
        # Use pdfplumber to count images
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            total_images = 0
            for page in pdf.pages:
                images = page.images
                total_images += len(images)
            
            print(f"Total images found in PDF: {total_images}")
            # Should have at least 2 images: logo + QR code
            assert total_images >= 2, f"Expected at least 2 images (logo + QR), found {total_images}"
            print(f"SUCCESS: PDF contains {total_images} images (logo + QR code)")
    
    def test_pdf_contains_qr_label_text(self):
        """Test PDF contains 'Prochaine etape recommandee' QR label"""
        from utils.pdf import generate_secured_pdf
        import pdfplumber
        
        analysis = "## Test\nContent for QR label verification."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Label Test",
            email="label@test.com",
            type_dossier="at",
            regime="general",
            with_watermark=False
        )
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += text + "\n"
            
            # Check for QR label
            assert "Prochaine etape recommandee" in full_text, "QR label 'Prochaine etape recommandee' not found"
            print("SUCCESS: PDF contains QR label 'Prochaine etape recommandee'")
    
    def test_pdf_contains_qr_description(self):
        """Test PDF contains QR description about 'accompagnement expert personnalise'"""
        from utils.pdf import generate_secured_pdf
        import pdfplumber
        
        analysis = "## Test\nContent for QR description verification."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Desc Test",
            email="desc@test.com",
            type_dossier="mp",
            regime="general",
            with_watermark=False
        )
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += text + "\n"
            
            # Check for QR description (partial match due to text extraction variations)
            assert "accompagnement expert personnalise" in full_text.lower(), \
                "QR description about 'accompagnement expert personnalise' not found"
            print("SUCCESS: PDF contains QR description about 'accompagnement expert personnalise'")
    
    def test_pdf_contains_text_link_fallback(self):
        """Test PDF contains text link fallback 'Premiere consultation offerte'"""
        from utils.pdf import generate_secured_pdf
        import pdfplumber
        
        analysis = "## Test\nContent for fallback link verification."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Fallback Test",
            email="fallback@test.com",
            type_dossier="at",
            regime="general",
            with_watermark=False
        )
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += text + "\n"
            
            # Check for fallback text link
            assert "Premiere consultation offerte" in full_text, \
                "Fallback text 'Premiere consultation offerte' not found"
            print("SUCCESS: PDF contains fallback text 'Premiere consultation offerte'")
    
    def test_pdf_contains_et_maintenant_section(self):
        """Test PDF contains 'Et maintenant' section title"""
        from utils.pdf import generate_secured_pdf
        import pdfplumber
        
        analysis = "## Test\nContent for Et maintenant section verification."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Section Test",
            email="section@test.com",
            type_dossier="mp",
            regime="general",
            with_watermark=False
        )
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += text + "\n"
            
            # Check for Et maintenant section
            assert "Et maintenant" in full_text, "'Et maintenant' section title not found"
            print("SUCCESS: PDF contains 'Et maintenant' section title")
    
    def test_pdf_contains_signature_votre_bouclier(self):
        """Test PDF contains signature 'Votre bouclier'"""
        from utils.pdf import generate_secured_pdf
        import pdfplumber
        
        analysis = "## Test\nContent for signature verification."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Signature Test",
            email="signature@test.com",
            type_dossier="at",
            regime="general",
            with_watermark=False
        )
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += text + "\n"
            
            # Check for signature
            assert "Votre bouclier" in full_text, "Signature 'Votre bouclier' not found"
            print("SUCCESS: PDF contains signature 'Votre bouclier'")


class TestPDFWithDocumentDetails:
    """Tests for PDF generation with document_details parameter"""
    
    def test_pdf_with_document_details_generates_correctly(self):
        """Test PDF with document_details generates correctly with QR code"""
        from utils.pdf import generate_secured_pdf
        import pdfplumber
        
        analysis = "## Test\nContent with document details."
        
        document_details = [
            {"name": "certificat_medical.pdf", "pages": 2, "status": "text_extracted"},
            {"name": "declaration_at.pdf", "pages": 1, "status": "ocr_extracted"},
        ]
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="DocDetails Test",
            email="docdetails@test.com",
            type_dossier="at",
            regime="general",
            with_watermark=False,
            document_details=document_details
        )
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        # Verify QR code is still present
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            total_images = 0
            full_text = ""
            for page in pdf.pages:
                images = page.images
                total_images += len(images)
                text = page.extract_text() or ""
                full_text += text + "\n"
            
            # Should have at least 2 images: logo + QR code
            assert total_images >= 2, f"Expected at least 2 images with document_details, found {total_images}"
            
            # Verify document details section is present
            assert "Base documentaire" in full_text or "Documents analyses" in full_text, \
                "Document details section not found in PDF"
            
            # Verify QR elements still present
            assert "Prochaine etape recommandee" in full_text
            assert "Premiere consultation offerte" in full_text
            
            print(f"SUCCESS: PDF with document_details contains {total_images} images and all QR elements")
    
    def test_pdf_without_document_details_generates_correctly(self):
        """Test PDF without document_details generates correctly with QR code"""
        from utils.pdf import generate_secured_pdf
        import pdfplumber
        
        analysis = "## Test\nContent without document details."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="NoDocDetails Test",
            email="nodocdetails@test.com",
            type_dossier="mp",
            regime="general",
            with_watermark=False,
            document_details=None
        )
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            total_images = 0
            full_text = ""
            for page in pdf.pages:
                images = page.images
                total_images += len(images)
                text = page.extract_text() or ""
                full_text += text + "\n"
            
            # Should have at least 2 images: logo + QR code
            assert total_images >= 2, f"Expected at least 2 images without document_details, found {total_images}"
            
            # Verify QR elements present
            assert "Prochaine etape recommandee" in full_text
            assert "Premiere consultation offerte" in full_text
            
            print(f"SUCCESS: PDF without document_details contains {total_images} images and all QR elements")


class TestQRCodeURL:
    """Tests for QR code URL configuration"""
    
    def test_qr_url_constant_in_pdf_module(self):
        """Verify QR URL constant has correct tracking params"""
        # Read the pdf.py source to verify the URL
        pdf_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'pdf.py')
        with open(pdf_path, 'r') as f:
            content = f.read()
        
        expected_url = "https://strategie-expertise-sante.fr/contact?src=pdf&type=dossier_express&via=qr"
        assert expected_url in content, f"Expected QR URL '{expected_url}' not found in pdf.py"
        print(f"SUCCESS: QR URL with tracking params found: {expected_url}")
    
    def test_qr_code_colors_in_pdf_module(self):
        """Verify QR code uses correct colors (#1a1a1a fill, #FAF8F3 background)"""
        pdf_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'pdf.py')
        with open(pdf_path, 'r') as f:
            content = f.read()
        
        assert '#1a1a1a' in content.lower() or '1a1a1a' in content.lower(), \
            "QR fill color #1a1a1a not found"
        assert '#FAF8F3' in content or 'FAF8F3' in content, \
            "QR background color #FAF8F3 not found"
        print("SUCCESS: QR code colors (#1a1a1a fill, #FAF8F3 background) found in pdf.py")


class TestDownloadEndpoint:
    """Tests for download endpoint functionality"""
    
    def test_download_endpoint_returns_400_without_token(self):
        """Test download endpoint returns 400 when token is missing"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/{KNOWN_DOSSIER_ID}/download")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("SUCCESS: Download endpoint returns 400 without token")
    
    def test_download_endpoint_returns_404_with_invalid_token(self):
        """Test download endpoint returns 404 with invalid token"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/{KNOWN_DOSSIER_ID}/download?token=invalid-token-xyz")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("SUCCESS: Download endpoint returns 404 with invalid token")


class TestAdminEndpoints:
    """Tests for admin-related endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin authentication failed")
    
    def test_admin_login_works(self):
        """Test admin login endpoint works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.status_code}"
        data = response.json()
        assert "access_token" in data, "access_token not in response"
        print("SUCCESS: Admin login works")
    
    def test_conseils_api_works(self):
        """Test conseils API endpoint works"""
        response = requests.get(f"{BASE_URL}/api/conseils/today")
        assert response.status_code == 200, f"Conseils API failed: {response.status_code}"
        print("SUCCESS: Conseils API works")
    
    def test_admin_pdf_preview_returns_200(self, admin_token):
        """Test admin PDF preview endpoint returns 200"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{KNOWN_DOSSIER_ID}/preview-pdf",
            headers=headers
        )
        # May return 404 if dossier doesn't exist, but should not return 500
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        print(f"SUCCESS: Admin PDF preview returns {response.status_code}")


class TestHomepageLoads:
    """Test frontend homepage loads"""
    
    def test_homepage_loads(self):
        """Test homepage loads correctly"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200, f"Homepage failed to load: {response.status_code}"
        assert len(response.text) > 1000, "Homepage content too short"
        print("SUCCESS: Homepage loads correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
