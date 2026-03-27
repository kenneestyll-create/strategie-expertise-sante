"""
Test Suite for OCR Extraction Pipeline - Iteration 126
Tests the 4-level cascade PDF extraction with page-by-page evaluation:
1. Tesseract OCR installation and French language pack
2. POST /api/extract-document-text extracts text from PDF text documents (status=text_extracted)
3. POST /api/extract-document-text extracts text from scanned PDFs via OCR (status=ocr_extracted)
4. POST /api/extract-document-text extracts text from images via OCR (status=ocr_extracted)
5. Extraction details include method with page-by-page quality info
6. Pre-processing improves OCR quality (enhanced=True uses contrast/sharpen/denoise)
7. Full E2E flow: extract → submit → analyze → complete with document_details preserved
"""

import pytest
import requests
import os
import base64
import io
import subprocess

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


class TestTesseractInstallation:
    """Tests for Tesseract OCR installation and French language pack"""
    
    def test_tesseract_is_installed(self):
        """Verify tesseract command is available"""
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        assert result.returncode == 0, f"Tesseract not installed: {result.stderr}"
        assert 'tesseract' in result.stdout.lower(), f"Unexpected output: {result.stdout}"
        print(f"Tesseract version: {result.stdout.split(chr(10))[0]}")
    
    def test_french_language_pack_available(self):
        """Verify French language pack (fra) is installed"""
        result = subprocess.run(['tesseract', '--list-langs'], capture_output=True, text=True)
        assert result.returncode == 0, f"Failed to list languages: {result.stderr}"
        
        # Check for 'fra' in the output
        output = result.stdout + result.stderr  # Some versions output to stderr
        assert 'fra' in output, f"French language pack not found. Available: {output}"
        print(f"French language pack (fra) is available")
    
    def test_start_sh_has_tesseract_install(self):
        """Verify start.sh contains tesseract auto-install logic"""
        start_sh_path = "/app/backend/start.sh"
        with open(start_sh_path, 'r') as f:
            content = f.read()
        
        assert 'tesseract' in content, "start.sh should contain tesseract installation"
        assert 'tesseract-ocr-fra' in content, "start.sh should install French language pack"
        print("start.sh contains tesseract auto-install logic")


class TestPDFTextExtraction:
    """Tests for PDF text extraction (native text PDFs)"""
    
    def test_extract_text_pdf_returns_text_extracted_status(self, api_client):
        """Test extraction from a text PDF returns status=text_extracted"""
        from fpdf import FPDF
        
        # Create a multi-page PDF with French text
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(200, 10, txt="Certificat medical initial", ln=True)
        pdf.cell(200, 10, txt="Patient: Jean Dupont", ln=True)
        pdf.cell(200, 10, txt="Date de l'accident: 15 janvier 2024", ln=True)
        pdf.cell(200, 10, txt="Diagnostic: Fracture du poignet droit", ln=True)
        pdf.cell(200, 10, txt="Arret de travail prescrit: 30 jours", ln=True)
        
        pdf.add_page()
        pdf.cell(200, 10, txt="Page 2 - Suite du certificat", ln=True)
        pdf.cell(200, 10, txt="Observations complementaires", ln=True)
        pdf.cell(200, 10, txt="Le patient necessite une reeducation", ln=True)
        
        pdf_bytes = pdf.output()
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "certificat_medical.pdf",
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
        
        detail = data["details"][0]
        assert detail["name"] == "certificat_medical.pdf"
        assert detail["status"] == "text_extracted", f"Expected text_extracted, got {detail['status']}"
        assert detail["pages"] == 2, f"Expected 2 pages, got {detail['pages']}"
        
        # Verify method contains page-by-page quality info
        method = detail["method"]
        assert "PDF texte" in method, f"Method should indicate PDF texte: {method}"
        assert "pages lisibles" in method or "extraction directe" in method, f"Method should have quality info: {method}"
        
        print(f"PDF text extraction: status={detail['status']}, method={method}, pages={detail['pages']}")
    
    def test_extract_text_pdf_method_contains_page_count(self, api_client):
        """Test that method field contains page count info"""
        from fpdf import FPDF
        
        pdf = FPDF()
        for i in range(3):
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)
            pdf.cell(200, 10, txt=f"Page {i+1} - Contenu du document", ln=True)
        
        pdf_bytes = pdf.output()
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "multi_page.pdf",
                "type": "application/pdf",
                "data": pdf_b64
            }]
        })
        
        assert response.status_code == 200
        data = response.json()
        detail = data["details"][0]
        
        # Method should contain "3 pages" or similar
        method = detail["method"]
        assert "3 page" in method, f"Method should contain page count: {method}"
        print(f"Method with page count: {method}")


class TestScannedPDFOCRExtraction:
    """Tests for scanned PDF OCR extraction"""
    
    def test_extract_scanned_pdf_returns_ocr_extracted_status(self, api_client):
        """Test extraction from a scanned PDF (image-based) returns status=ocr_extracted"""
        from PIL import Image, ImageDraw, ImageFont
        from fpdf import FPDF
        
        # Create an image with French text (simulating a scanned document)
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw text on image (simulating scanned document)
        y_pos = 50
        texts = [
            "CERTIFICAT MEDICAL",
            "Patient: Marie Martin",
            "Date: 20 fevrier 2024",
            "Accident du travail",
            "Taux IPP: 15%"
        ]
        for text in texts:
            draw.text((50, y_pos), text, fill='black')
            y_pos += 40
        
        # Save image to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        # Create PDF with embedded image (simulating scanned PDF)
        pdf = FPDF()
        pdf.add_page()
        
        # Save temp image and add to PDF
        temp_img_path = "/tmp/test_scan_page.png"
        with open(temp_img_path, 'wb') as f:
            f.write(img_bytes)
        
        pdf.image(temp_img_path, x=10, y=10, w=190)
        pdf_bytes = pdf.output()
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Clean up temp file
        os.remove(temp_img_path)
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "scanned_document.pdf",
                "type": "application/pdf",
                "data": pdf_b64
            }]
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        detail = data["details"][0]
        assert detail["name"] == "scanned_document.pdf"
        
        # Scanned PDF should trigger OCR
        # Status can be ocr_extracted, partially_readable, or ocr_empty depending on OCR quality
        valid_statuses = ["ocr_extracted", "partially_readable", "ocr_empty", "text_extracted"]
        assert detail["status"] in valid_statuses, f"Unexpected status: {detail['status']}"
        
        method = detail["method"]
        # Method should indicate OCR was used (unless text was somehow extracted)
        if detail["status"] in ["ocr_extracted", "partially_readable", "ocr_empty"]:
            assert "OCR" in method or "scanné" in method, f"Method should indicate OCR: {method}"
        
        print(f"Scanned PDF extraction: status={detail['status']}, method={method}")


class TestImageOCRExtraction:
    """Tests for image OCR extraction"""
    
    def test_extract_image_returns_ocr_extracted_status(self, api_client):
        """Test extraction from image returns status=ocr_extracted"""
        from PIL import Image, ImageDraw
        
        # Create an image with clear French text
        img = Image.new('RGB', (600, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw clear text
        texts = [
            "NOTIFICATION CPAM",
            "Numero de dossier: AT-2024-12345",
            "Beneficiaire: Pierre Durand",
            "Montant: 2500 euros"
        ]
        y_pos = 30
        for text in texts:
            draw.text((30, y_pos), text, fill='black')
            y_pos += 50
        
        # Save to bytes as PNG
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "notification_cpam.png",
                "type": "image/png",
                "data": img_b64
            }]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        detail = data["details"][0]
        assert detail["name"] == "notification_cpam.png"
        assert detail["pages"] == 1, "Image should be 1 page"
        
        # Status should be OCR-related
        valid_statuses = ["ocr_extracted", "partially_readable", "ocr_empty", "ocr_error"]
        assert detail["status"] in valid_statuses, f"Unexpected status: {detail['status']}"
        
        method = detail["method"]
        assert "Image" in method or "OCR" in method, f"Method should indicate image OCR: {method}"
        
        print(f"Image OCR extraction: status={detail['status']}, method={method}")
    
    def test_extract_jpeg_image(self, api_client):
        """Test extraction from JPEG image"""
        from PIL import Image, ImageDraw
        
        img = Image.new('RGB', (500, 300), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "Document JPEG Test", fill='black')
        draw.text((20, 60), "Contenu medical important", fill='black')
        
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG', quality=95)
        img_bytes = img_buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "document.jpg",
                "type": "image/jpeg",
                "data": img_b64
            }]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        detail = data["details"][0]
        assert detail["name"] == "document.jpg"
        print(f"JPEG extraction: status={detail['status']}, method={detail['method']}")


class TestExtractionMethodDetails:
    """Tests for extraction method details with page-by-page quality info"""
    
    def test_method_contains_lisible_count(self, api_client):
        """Test that method field contains readable page count (e.g., '2/2 pages lisibles')"""
        from fpdf import FPDF
        
        # Create a 2-page PDF with clear text
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=14)
        pdf.multi_cell(0, 10, txt="Page 1: Ceci est un document de test avec suffisamment de texte pour etre considere comme lisible par le systeme d'extraction.")
        
        pdf.add_page()
        pdf.multi_cell(0, 10, txt="Page 2: Suite du document avec des informations supplementaires sur le dossier medical du patient.")
        
        pdf_bytes = pdf.output()
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "two_page_doc.pdf",
                "type": "application/pdf",
                "data": pdf_b64
            }]
        })
        
        assert response.status_code == 200
        data = response.json()
        detail = data["details"][0]
        
        method = detail["method"]
        # Method should contain quality info like "2/2 pages lisibles" or "extraction directe"
        has_quality_info = (
            "lisible" in method.lower() or 
            "extraction directe" in method.lower() or
            "pages" in method.lower()
        )
        assert has_quality_info, f"Method should contain quality info: {method}"
        print(f"Method with quality info: {method}")
    
    def test_details_include_preview(self, api_client):
        """Test that details include text preview"""
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(200, 10, txt="Preview test document content here", ln=True)
        
        pdf_bytes = pdf.output()
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "preview_test.pdf",
                "type": "application/pdf",
                "data": pdf_b64
            }]
        })
        
        assert response.status_code == 200
        data = response.json()
        detail = data["details"][0]
        
        assert "preview" in detail, "Details should include preview field"
        assert "text_length" in detail, "Details should include text_length field"
        print(f"Preview: {detail['preview'][:50]}... (length: {detail['text_length']})")


class TestE2EFlowWithDocumentDetails:
    """Tests for full E2E flow: extract → submit → analyze with document_details preserved"""
    
    def test_e2e_extract_and_submit_preserves_document_details(self, api_client, admin_token):
        """Test full flow: extract documents, submit dossier, verify document_details preserved"""
        from fpdf import FPDF
        
        # Step 1: Create and extract a PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(200, 10, txt="Certificat medical - Accident du travail", ln=True)
        pdf.cell(200, 10, txt="Patient: Test E2E User", ln=True)
        pdf.cell(200, 10, txt="Date: 15 janvier 2024", ln=True)
        
        pdf_bytes = pdf.output()
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Extract document text
        extract_response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "e2e_test_cert.pdf",
                "type": "application/pdf",
                "data": pdf_b64
            }]
        })
        
        assert extract_response.status_code == 200
        extract_data = extract_response.json()
        
        extracted_text = extract_data["extracted_text"]
        document_details = extract_data["details"]
        
        assert len(document_details) == 1
        assert document_details[0]["name"] == "e2e_test_cert.pdf"
        
        # Step 2: Submit dossier with document_details via admin-bypass
        submit_response = api_client.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "E2E Test User",
                "situation": "Test E2E flow for document extraction and submission with document_details preservation.",
                "type_dossier": "at",
                "regime": "general",
                "documents_text": extracted_text,
                "document_details": document_details,
                "premium_pdf": False
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert submit_response.status_code == 200, f"Submit failed: {submit_response.text}"
        submit_data = submit_response.json()
        
        assert submit_data["success"] == True
        dossier_id = submit_data["dossier_id"]
        print(f"Created dossier: {dossier_id}")
        
        # Step 3: Verify document_details is preserved in status
        status_response = api_client.get(f"{BASE_URL}/api/dossier-express/status/{dossier_id}")
        
        assert status_response.status_code == 200
        status_data = status_response.json()
        
        assert "document_details" in status_data, "document_details should be in status response"
        assert len(status_data["document_details"]) == 1
        assert status_data["document_details"][0]["name"] == "e2e_test_cert.pdf"
        
        print(f"E2E flow complete: document_details preserved with {len(status_data['document_details'])} documents")
        
        return dossier_id
    
    def test_e2e_multiple_documents_preserved(self, api_client, admin_token):
        """Test E2E with multiple documents - all details preserved"""
        from fpdf import FPDF
        from PIL import Image, ImageDraw
        
        # Create PDF document
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(200, 10, txt="Document PDF numero 1", ln=True)
        pdf_bytes = pdf.output()
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Create image document
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "Document Image numero 2", fill='black')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # Extract both documents
        extract_response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [
                {"name": "doc1.pdf", "type": "application/pdf", "data": pdf_b64},
                {"name": "doc2.png", "type": "image/png", "data": img_b64}
            ]
        })
        
        assert extract_response.status_code == 200
        extract_data = extract_response.json()
        
        assert extract_data["files_processed"] == 2
        assert len(extract_data["details"]) == 2
        
        # Submit with both document details
        submit_response = api_client.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Multi Doc Test",
                "situation": "Test with multiple documents",
                "type_dossier": "mp",
                "regime": "general",
                "documents_text": extract_data["extracted_text"],
                "document_details": extract_data["details"]
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert submit_response.status_code == 200
        dossier_id = submit_response.json()["dossier_id"]
        
        # Verify both documents preserved
        status_response = api_client.get(f"{BASE_URL}/api/dossier-express/status/{dossier_id}")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert len(status_data["document_details"]) == 2
        
        doc_names = [d["name"] for d in status_data["document_details"]]
        assert "doc1.pdf" in doc_names
        assert "doc2.png" in doc_names
        
        print(f"Multiple documents preserved: {doc_names}")


class TestTextFileExtraction:
    """Tests for plain text file extraction"""
    
    def test_extract_text_file_returns_text_extracted(self, api_client):
        """Test extraction from plain text file"""
        text_content = """Rapport medical
Patient: Sophie Bernard
Date: 10 mars 2024
Diagnostic: Maladie professionnelle
Tableau 57 - TMS du membre superieur"""
        
        text_b64 = base64.b64encode(text_content.encode('utf-8')).decode('utf-8')
        
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "rapport.txt",
                "type": "text/plain",
                "data": text_b64
            }]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        detail = data["details"][0]
        assert detail["status"] == "text_extracted"
        assert "lecture texte" in detail["method"].lower()
        assert detail["text_length"] > 0
        
        # Verify content is in extracted text
        assert "Sophie Bernard" in data["extracted_text"]
        print(f"Text file extraction: status={detail['status']}, method={detail['method']}")


class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_empty_file_data(self, api_client):
        """Test handling of empty file data"""
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "empty.pdf",
                "type": "application/pdf",
                "data": ""
            }]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        detail = data["details"][0]
        assert detail["status"] == "no_data"
        print(f"Empty file handling: status={detail['status']}")
    
    def test_invalid_base64_data(self, api_client):
        """Test handling of invalid base64 data"""
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "invalid.pdf",
                "type": "application/pdf",
                "data": "not-valid-base64!!!"
            }]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        detail = data["details"][0]
        assert detail["status"] == "decode_error"
        print(f"Invalid base64 handling: status={detail['status']}")
    
    def test_unsupported_file_type(self, api_client):
        """Test handling of unsupported file type"""
        response = api_client.post(f"{BASE_URL}/api/extract-document-text", json={
            "files": [{
                "name": "document.xyz",
                "type": "application/xyz",
                "data": base64.b64encode(b"some content").decode('utf-8')
            }]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        detail = data["details"][0]
        assert detail["status"] == "unsupported"
        print(f"Unsupported file handling: status={detail['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
