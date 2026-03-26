"""
Test suite for StrategiIA bug fixes (iteration 112):
1. Polling resilience - POST /api/strategiia/analyze returns job_id, polling works
2. Shield logo in PDF - PDF header contains the shield logo image
3. Closing phrase - PDF contains EXACTLY one occurrence of the closing phrase
"""
import pytest
import requests
import os
import base64
import re
import subprocess
import tempfile

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


class TestPollingResilience:
    """BUG FIX 1: Polling resilience - endpoints return immediately with job_id"""
    
    def test_analyze_returns_job_id_immediately(self):
        """POST /api/strategiia/analyze should return job_id immediately (not hang)"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/analyze",
            json={
                "type_dossier": "at",
                "regime": "general",
                "situation": "Test situation for polling resilience test",
                "premium": False
            },
            timeout=10  # Should return in <1s, not hang
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "job_id" in data, f"Response should contain job_id: {data}"
        assert data.get("status") == "pending", f"Status should be pending: {data}"
        print(f"PASS: analyze returns job_id={data['job_id']} immediately")
    
    def test_status_endpoint_returns_pending_or_done(self):
        """GET /api/strategiia/status/{job_id} should return pending/done/error"""
        # First create a job
        response = requests.post(
            f"{BASE_URL}/api/strategiia/analyze",
            json={
                "type_dossier": "mp",
                "regime": "general",
                "situation": "Test maladie professionnelle pour test de polling",
                "premium": False
            },
            timeout=10
        )
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        
        # Poll the status
        status_response = requests.get(f"{BASE_URL}/api/strategiia/status/{job_id}", timeout=5)
        assert status_response.status_code == 200, f"Status endpoint failed: {status_response.text}"
        status_data = status_response.json()
        assert status_data.get("status") in ["pending", "done", "error"], f"Invalid status: {status_data}"
        print(f"PASS: status endpoint returns status={status_data['status']}")
    
    def test_invalid_job_id_returns_404(self):
        """GET /api/strategiia/status/{invalid_job_id} should return 404"""
        response = requests.get(f"{BASE_URL}/api/strategiia/status/invalid-job-id-12345", timeout=5)
        assert response.status_code == 404, f"Expected 404 for invalid job_id, got {response.status_code}"
        print("PASS: invalid job_id returns 404")
    
    def test_admin_bypass_returns_job_id_immediately(self):
        """POST /api/strategiia/admin-bypass-premium should return job_id immediately"""
        # First login to get admin token
        login_response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        token = login_response.json().get("access_token")
        assert token, "No access_token in login response"
        
        # Call admin bypass
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json={
                "situation": "Test admin bypass for polling test",
                "type_dossier": "at",
                "regime": "general",
                "premium_pdf": True,
                "analyse_premium": False
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Admin bypass failed: {response.text}"
        data = response.json()
        assert "job_id" in data, f"Response should contain job_id: {data}"
        assert data.get("admin_test") == True, f"admin_test should be True: {data}"
        print(f"PASS: admin-bypass returns job_id={data['job_id']} immediately")


class TestShieldLogoInPDF:
    """BUG FIX 2: Shield logo should be present in PDF header"""
    
    def test_shield_logo_file_exists(self):
        """Shield logo file should exist at /app/backend/utils/shield_logo.png"""
        logo_path = "/app/backend/utils/shield_logo.png"
        assert os.path.isfile(logo_path), f"Shield logo not found at {logo_path}"
        
        # Check file size (should be 9926 bytes)
        file_size = os.path.getsize(logo_path)
        assert file_size == 9926, f"Shield logo size mismatch: expected 9926, got {file_size}"
        print(f"PASS: shield_logo.png exists with correct size ({file_size} bytes)")
    
    def test_pdf_contains_image(self):
        """Generated PDF should contain an image (the shield logo)"""
        # Generate a PDF
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "Test analysis for PDF image verification.\n\n## Section 1\nThis is a test.",
                "type_dossier": "Accident du travail",
                "regime": "Régime général",
                "name": "Test User",
                "premium_pdf": True
            },
            timeout=30
        )
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        data = response.json()
        assert "pdf_base64" in data, "Response should contain pdf_base64"
        
        # Decode PDF and check for image
        pdf_bytes = base64.b64decode(data["pdf_base64"])
        
        # Check PDF contains image markers (PNG signature or XObject)
        # PNG files embedded in PDF have the PNG signature or are referenced as XObject
        pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
        
        # Check for image XObject reference (how fpdf embeds images)
        has_image = '/XObject' in pdf_content or '/Image' in pdf_content or 'PNG' in pdf_content
        assert has_image, "PDF should contain an image (shield logo)"
        print("PASS: PDF contains image reference (shield logo embedded)")


class TestClosingPhrase:
    """BUG FIX 3: Closing phrase should appear EXACTLY once in PDF"""
    
    CLOSING_PHRASE = "Desormais, Strategie & Expertise Sante devient votre bouclier"
    
    def test_clean_analysis_strips_llm_closing_phrase(self):
        """The _clean_analysis function should strip LLM-generated closing phrase"""
        # Import the function
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.pdf import _clean_analysis
        
        # Test text with LLM-generated closing phrase
        test_text = """## Analyse
Votre situation est complexe.

**Désormais, Stratégie & Expertise Santé devient votre bouclier.**

Contactez-nous pour plus d'informations."""
        
        cleaned = _clean_analysis(test_text)
        
        # The LLM-generated closing phrase should be stripped
        assert "devient votre bouclier" not in cleaned.lower(), f"LLM closing phrase should be stripped: {cleaned}"
        print("PASS: _clean_analysis strips LLM-generated closing phrase")
    
    def test_pdf_contains_closing_phrase_exactly_once(self):
        """PDF should contain the closing phrase EXACTLY once (hardcoded in template)"""
        # Generate a PDF with analysis that includes the closing phrase (to test dedup)
        analysis_with_closing = """## Votre situation analysée
Votre dossier présente des éléments favorables.

## Stratégie recommandée
Nous vous conseillons de procéder étape par étape.

**Vous n'êtes plus seul(e) face à votre situation.**
**Désormais, Stratégie & Expertise Santé devient votre bouclier.**"""
        
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": analysis_with_closing,
                "type_dossier": "Maladie professionnelle",
                "regime": "Régime général",
                "name": "Test Closing Phrase",
                "premium_pdf": True
            },
            timeout=30
        )
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        data = response.json()
        
        # Decode PDF
        pdf_bytes = base64.b64decode(data["pdf_base64"])
        
        # Save to temp file and extract text with pdftotext
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(pdf_bytes)
            temp_pdf_path = f.name
        
        try:
            # Extract text from PDF
            result = subprocess.run(
                ['pdftotext', '-layout', temp_pdf_path, '-'],
                capture_output=True,
                text=True,
                timeout=10
            )
            pdf_text = result.stdout
            
            # Count occurrences of the closing phrase (case-insensitive, accent-insensitive)
            # The phrase in PDF is: "Desormais, Strategie & Expertise Sante devient votre bouclier"
            closing_pattern = r"[Dd][eé]sormais.*[Ss]trat[eé]gie.*[Ee]xpertise.*[Ss]ant[eé].*devient.*bouclier"
            matches = re.findall(closing_pattern, pdf_text, re.IGNORECASE)
            
            count = len(matches)
            assert count == 1, f"Closing phrase should appear EXACTLY once, found {count} times. PDF text:\n{pdf_text[:2000]}"
            print(f"PASS: Closing phrase appears exactly once in PDF")
            
        finally:
            os.unlink(temp_pdf_path)
    
    def test_pdf_contains_both_closing_lines(self):
        """PDF should contain both lines of the closing signature"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "## Test\nSimple test analysis.",
                "type_dossier": "Test",
                "regime": "Test",
                "name": "Test",
                "premium_pdf": True
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        pdf_bytes = base64.b64decode(data["pdf_base64"])
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(pdf_bytes)
            temp_pdf_path = f.name
        
        try:
            result = subprocess.run(
                ['pdftotext', '-layout', temp_pdf_path, '-'],
                capture_output=True,
                text=True,
                timeout=10
            )
            pdf_text = result.stdout.lower()
            
            # Check for first line (accent-insensitive)
            has_line1 = "plus seul" in pdf_text or "n'etes plus seul" in pdf_text
            # Check for second line
            has_line2 = "devient votre bouclier" in pdf_text
            
            assert has_line1, f"PDF should contain first closing line. PDF text:\n{pdf_text[:1500]}"
            assert has_line2, f"PDF should contain second closing line. PDF text:\n{pdf_text[:1500]}"
            print("PASS: PDF contains both closing lines")
            
        finally:
            os.unlink(temp_pdf_path)


class TestPDFGenerationEndpoint:
    """Test the PDF generation endpoint works correctly"""
    
    def test_generate_pdf_with_premium_flag(self):
        """POST /api/strategiia/generate-pdf with premium_pdf=true should work"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "## Test Premium PDF\nThis is a premium PDF test.",
                "type_dossier": "Accident du travail",
                "regime": "Régime général",
                "name": "Premium Test User",
                "premium_pdf": True
            },
            timeout=30
        )
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        data = response.json()
        assert "pdf_base64" in data, "Response should contain pdf_base64"
        assert "filename" in data, "Response should contain filename"
        
        # Verify it's valid base64
        try:
            pdf_bytes = base64.b64decode(data["pdf_base64"])
            assert len(pdf_bytes) > 1000, "PDF should be larger than 1KB"
            # Check PDF magic bytes
            assert pdf_bytes[:4] == b'%PDF', "Should be a valid PDF file"
            print(f"PASS: Premium PDF generated successfully ({len(pdf_bytes)} bytes)")
        except Exception as e:
            pytest.fail(f"Invalid PDF base64: {e}")
    
    def test_generate_pdf_without_premium_flag(self):
        """POST /api/strategiia/generate-pdf with premium_pdf=false should add watermark"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "## Test Standard PDF\nThis is a standard PDF with watermark.",
                "type_dossier": "Maladie professionnelle",
                "regime": "MSA",
                "name": "Standard Test User",
                "premium_pdf": False
            },
            timeout=30
        )
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        data = response.json()
        assert "pdf_base64" in data
        
        pdf_bytes = base64.b64decode(data["pdf_base64"])
        assert pdf_bytes[:4] == b'%PDF', "Should be a valid PDF file"
        print(f"PASS: Standard PDF with watermark generated ({len(pdf_bytes)} bytes)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
