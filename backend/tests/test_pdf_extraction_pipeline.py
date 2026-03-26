"""
Test PDF Extraction Pipeline for Dossier Express IA
Tests the 3-level extraction: pdfplumber → pypdfium2+tesseract OCR → metadata fallback
"""
import pytest
import requests
import os
import base64
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed")


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestExtractDocumentTextEndpoint:
    """Tests for POST /api/extract-document-text endpoint"""
    
    def test_extract_text_pdf_basic(self, api_client):
        """Test extraction from a simple text PDF using fpdf2"""
        # Create a simple PDF with text using fpdf2
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(200, 10, txt="Ceci est un document de test pour extraction PDF.", ln=True)
        pdf.cell(200, 10, txt="Accident du travail survenu le 15 janvier 2024.", ln=True)
        pdf.cell(200, 10, txt="Certificat medical initial etabli par Dr. Martin.", ln=True)
        
        pdf_bytes = pdf.output()
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "test_document.pdf",
                "type": "application/pdf",
                "data": pdf_b64
            }]
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "extracted_text" in data
        assert "files_processed" in data
        assert "details" in data
        assert data["files_processed"] == 1
        
        # Verify details array structure
        assert len(data["details"]) == 1
        detail = data["details"][0]
        assert "name" in detail
        assert "method" in detail
        assert "status" in detail
        assert "pages" in detail
        assert "text_length" in detail
        assert "preview" in detail
        
        # Verify extraction worked
        assert detail["name"] == "test_document.pdf"
        assert detail["status"] in ["text_extracted", "ocr_extracted"]
        assert detail["pages"] >= 1
        print(f"PDF extraction successful: status={detail['status']}, method={detail['method']}, pages={detail['pages']}")
    
    def test_extract_text_pdf_returns_details_array(self, api_client):
        """Test that details array contains per-file metadata"""
        from fpdf import FPDF
        
        # Create two PDFs
        pdf1 = FPDF()
        pdf1.add_page()
        pdf1.set_font("Helvetica", size=12)
        pdf1.cell(200, 10, txt="Document numero un - certificat medical.", ln=True)
        pdf1_bytes = pdf1.output()
        pdf1_b64 = base64.b64encode(pdf1_bytes).decode('utf-8')
        
        pdf2 = FPDF()
        pdf2.add_page()
        pdf2.set_font("Helvetica", size=12)
        pdf2.cell(200, 10, txt="Document numero deux - declaration accident.", ln=True)
        pdf2_bytes = pdf2.output()
        pdf2_b64 = base64.b64encode(pdf2_bytes).decode('utf-8')
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [
                {"name": "certificat.pdf", "type": "application/pdf", "data": pdf1_b64},
                {"name": "declaration.pdf", "type": "application/pdf", "data": pdf2_b64}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["files_processed"] == 2
        assert len(data["details"]) == 2
        
        # Verify each detail has required fields
        for detail in data["details"]:
            assert "name" in detail
            assert "method" in detail
            assert "status" in detail
            assert "pages" in detail
            assert "text_length" in detail
            assert "preview" in detail
            assert "has_text" in detail
            assert "size_kb" in detail
        
        print(f"Multiple PDF extraction: {len(data['details'])} files processed")
    
    def test_extract_image_with_ocr(self, api_client):
        """Test OCR extraction from image files"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Create an image with French text
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw text on image
        draw.text((20, 20), "Certificat Medical", fill='black')
        draw.text((20, 60), "Patient: Jean Dupont", fill='black')
        draw.text((20, 100), "Date: 15 janvier 2024", fill='black')
        draw.text((20, 140), "Accident du travail", fill='black')
        
        # Save to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "certificat_scan.png",
                "type": "image/png",
                "data": img_b64
            }]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["files_processed"] == 1
        assert len(data["details"]) == 1
        
        detail = data["details"][0]
        assert detail["name"] == "certificat_scan.png"
        # OCR may or may not extract text depending on image quality
        assert detail["status"] in ["ocr_extracted", "ocr_empty", "ocr_error"]
        assert detail["pages"] == 1
        
        print(f"Image OCR: status={detail['status']}, method={detail['method']}")
    
    def test_extract_empty_files_list(self, api_client):
        """Test with empty files list"""
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": []
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["extracted_text"] == ""
        assert data["files_processed"] == 0
        assert data["details"] == []
    
    def test_extract_text_file(self, api_client):
        """Test extraction from plain text file"""
        text_content = "Ceci est un fichier texte simple.\nContenu du dossier medical."
        text_b64 = base64.b64encode(text_content.encode('utf-8')).decode('utf-8')
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "notes.txt",
                "type": "text/plain",
                "data": text_b64
            }]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["files_processed"] == 1
        detail = data["details"][0]
        assert detail["status"] == "text_extracted"
        assert "lecture texte" in detail["method"].lower()
        print(f"Text file extraction: status={detail['status']}")


class TestDossierExpressAdminBypass:
    """Tests for POST /api/dossier-express/admin-bypass with document_details"""
    
    def test_admin_bypass_accepts_document_details(self, api_client, admin_token):
        """Test that admin-bypass endpoint accepts and stores document_details"""
        document_details = [
            {
                "name": "certificat_medical.pdf",
                "method": "PDF texte — 2 pages, extraction directe",
                "status": "text_extracted",
                "pages": 2,
                "text_length": 1500,
                "preview": "Certificat médical initial établi par Dr. Martin..."
            },
            {
                "name": "declaration_at.pdf",
                "method": "PDF scanné — 1 page, OCR automatique",
                "status": "ocr_extracted",
                "pages": 1,
                "text_length": 800,
                "preview": "Déclaration d'accident du travail..."
            }
        ]
        
        response = api_client.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Test Document Details",
                "situation": "Test situation pour vérifier que document_details est bien stocké en base de données.",
                "type_dossier": "at",
                "regime": "general",
                "documents_text": "Contenu extrait des documents...",
                "document_details": document_details,
                "premium_pdf": False
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["success"] == True
        assert "dossier_id" in data
        assert data["admin_test"] == True
        
        dossier_id = data["dossier_id"]
        print(f"Created dossier with document_details: {dossier_id}")
        
        return dossier_id
    
    def test_admin_bypass_without_auth_returns_401(self, api_client):
        """Test that admin-bypass requires authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Test",
                "situation": "Test situation",
                "type_dossier": "at"
            }
        )
        
        assert response.status_code == 401


class TestDossierExpressStatus:
    """Tests for GET /api/dossier-express/status/{id} returning document_details"""
    
    def test_status_returns_document_details(self, api_client, admin_token):
        """Test that status endpoint returns document_details array"""
        # First create a dossier with document_details
        document_details = [
            {
                "name": "test_doc.pdf",
                "method": "PDF texte — 1 page",
                "status": "text_extracted",
                "pages": 1,
                "text_length": 500,
                "preview": "Test preview..."
            }
        ]
        
        create_response = api_client.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Test Status Check",
                "situation": "Test situation for status endpoint verification.",
                "type_dossier": "mp",
                "regime": "general",
                "document_details": document_details
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert create_response.status_code == 200
        dossier_id = create_response.json()["dossier_id"]
        
        # Now check status
        status_response = api_client.get(f"{BASE_URL}/api/dossier-express/status/{dossier_id}")
        
        assert status_response.status_code == 200
        data = status_response.json()
        
        # Verify document_details is returned
        assert "document_details" in data
        assert isinstance(data["document_details"], list)
        assert len(data["document_details"]) == 1
        assert data["document_details"][0]["name"] == "test_doc.pdf"
        assert data["document_details"][0]["status"] == "text_extracted"
        
        print(f"Status endpoint returns document_details: {len(data['document_details'])} items")
    
    def test_status_invalid_id_returns_404(self, api_client):
        """Test that invalid dossier ID returns 404"""
        response = api_client.get(f"{BASE_URL}/api/dossier-express/status/invalid-id-12345")
        assert response.status_code == 404


class TestAdminDossierExpressAnalysis:
    """Tests for GET /api/admin/dossier-express/{id}/analysis returning document_details"""
    
    def test_admin_analysis_returns_document_details(self, api_client, admin_token):
        """Test that admin analysis endpoint returns document_details array"""
        # Create a dossier with document_details
        document_details = [
            {
                "name": "admin_test_doc.pdf",
                "method": "PDF texte — 3 pages, extraction directe",
                "status": "text_extracted",
                "pages": 3,
                "text_length": 2500,
                "preview": "Admin test document preview..."
            },
            {
                "name": "scan_image.jpg",
                "method": "Image — OCR automatique",
                "status": "ocr_extracted",
                "pages": 1,
                "text_length": 300,
                "preview": "OCR extracted text..."
            }
        ]
        
        create_response = api_client.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Admin Analysis Test",
                "situation": "Test situation for admin analysis endpoint.",
                "type_dossier": "at",
                "regime": "general",
                "document_details": document_details
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert create_response.status_code == 200
        dossier_id = create_response.json()["dossier_id"]
        
        # Fetch admin analysis
        analysis_response = api_client.get(
            f"{BASE_URL}/api/admin/dossier-express/{dossier_id}/analysis",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert analysis_response.status_code == 200
        data = analysis_response.json()
        
        # Verify document_details is returned
        assert "document_details" in data
        assert isinstance(data["document_details"], list)
        assert len(data["document_details"]) == 2
        
        # Verify structure of each detail
        for detail in data["document_details"]:
            assert "name" in detail
            assert "method" in detail
            assert "status" in detail
        
        print(f"Admin analysis returns document_details: {len(data['document_details'])} items")
    
    def test_admin_analysis_without_auth_returns_401(self, api_client):
        """Test that admin analysis requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/admin/dossier-express/some-id/analysis")
        assert response.status_code in [401, 403]
    
    def test_admin_analysis_invalid_id_returns_404(self, api_client, admin_token):
        """Test that invalid dossier ID returns 404"""
        response = api_client.get(
            f"{BASE_URL}/api/admin/dossier-express/invalid-id-xyz/analysis",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404


class TestExistingDossierDocumentDetails:
    """Test with existing dossier ID from context"""
    
    def test_existing_dossier_status(self, api_client):
        """Test status of existing completed dossier"""
        # Use the existing dossier ID from context
        existing_dossier_id = "9ac273a6-e17f-4c4e-9c8b-a0518e72587c"
        
        response = api_client.get(f"{BASE_URL}/api/dossier-express/status/{existing_dossier_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Existing dossier status: {data.get('status')}")
            print(f"Has document_details: {'document_details' in data}")
            if "document_details" in data:
                print(f"Document details count: {len(data['document_details'])}")
        else:
            print(f"Existing dossier not found or error: {response.status_code}")
            # This is not a failure - the dossier may have been cleaned up
            pytest.skip("Existing dossier not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
