"""
Test PDF Footer Fix - Iteration 106
Tests that PDF generation uses correct domain (strategie-expertise-sante.fr)
and does NOT include preview URLs (mascot-tips-admin.preview.emergentagent.com)
"""
import pytest
import requests
import base64
import os
import io

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


def extract_pdf_text(pdf_bytes):
    """Extract text from PDF bytes using PyPDF2 if available, else raw decode"""
    if HAS_PYPDF2:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception:
            pass
    # Fallback to raw decode
    return pdf_bytes.decode('latin-1', errors='ignore')


class TestStrategiIAPDFGeneration:
    """Tests for StrategiIA PDF generation endpoint"""
    
    def test_strategiia_pdf_endpoint_returns_pdf(self):
        """Test that /api/strategiia/generate-pdf returns a valid PDF"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "## Test Analysis\nThis is a test analysis.",
                "type_dossier": "at",
                "regime": "general",
                "name": "Test User"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "pdf_base64" in data, "Response should contain pdf_base64"
        assert "filename" in data, "Response should contain filename"
        
        # Verify it's valid base64
        try:
            pdf_bytes = base64.b64decode(data["pdf_base64"])
            assert pdf_bytes[:4] == b'%PDF', "Should be a valid PDF file"
        except Exception as e:
            pytest.fail(f"Invalid base64 PDF: {e}")
    
    def test_strategiia_pdf_contains_correct_domain(self):
        """Test that generated PDF contains strategie-expertise-sante.fr domain"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "## Analyse de votre situation\nVoici une analyse test.",
                "type_dossier": "mp",
                "regime": "general",
                "name": "Test Domain Check"
            }
        )
        assert response.status_code == 200
        
        pdf_bytes = base64.b64decode(response.json()["pdf_base64"])
        pdf_text = extract_pdf_text(pdf_bytes)
        
        # Check for correct domain
        assert "strategie-expertise-sante.fr" in pdf_text, \
            f"PDF should contain strategie-expertise-sante.fr domain. Got text: {pdf_text[:500]}"
    
    def test_strategiia_pdf_no_preview_urls(self):
        """Test that generated PDF does NOT contain preview URLs"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "## Test\nAnalysis with potential URL injection https://mascot-tips-admin.preview.emergentagent.com/test",
                "type_dossier": "at",
                "regime": "general",
                "name": "Test No Preview URLs"
            }
        )
        assert response.status_code == 200
        
        pdf_bytes = base64.b64decode(response.json()["pdf_base64"])
        pdf_text = extract_pdf_text(pdf_bytes).lower()
        
        # Check that preview URLs are NOT present
        assert "mascot-tips-admin" not in pdf_text, \
            "PDF should NOT contain mascot-tips-admin preview URL"
        assert "preview.emergentagent" not in pdf_text, \
            "PDF should NOT contain preview.emergentagent URL"
    
    def test_strategiia_pdf_strips_urls_from_analysis(self):
        """Test that URLs in analysis text are stripped/replaced"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": """## Analyse
Voici une analyse avec des URLs:
- https://example.com/test
- https://mascot-tips-admin.preview.emergentagent.com/contact
- Prendre rendez-vous sur strategie-expertise-sante.fr
""",
                "type_dossier": "mdph",
                "regime": "general",
                "name": "Test URL Stripping"
            }
        )
        assert response.status_code == 200
        
        pdf_bytes = base64.b64decode(response.json()["pdf_base64"])
        pdf_text = extract_pdf_text(pdf_bytes).lower()
        
        # Preview URLs should be stripped
        assert "mascot-tips-admin" not in pdf_text
        assert "example.com" not in pdf_text or "strategie-expertise-sante.fr" in pdf_text
    
    def test_strategiia_pdf_with_premium_flag(self):
        """Test PDF generation with premium_pdf flag (no watermark)"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "## Premium Analysis\nThis is a premium analysis.",
                "type_dossier": "at",
                "regime": "general",
                "name": "Premium User",
                "premium_pdf": True
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "pdf_base64" in data
        
        # Verify it's a valid PDF
        pdf_bytes = base64.b64decode(data["pdf_base64"])
        assert pdf_bytes[:4] == b'%PDF'


class TestSimulatorResultAPI:
    """Tests for simulator result API"""
    
    def test_simulator_result_submission(self):
        """Test that simulator results can be submitted"""
        response = requests.post(
            f"{BASE_URL}/api/simulator/result",
            json={
                "answers": {
                    "situation": "at",
                    "demarche": "debut",
                    "anciennete": "recent",
                    "accompagnement": "seul",
                    "besoin": "comprendre"
                },
                "email": "test_pdf_footer@test.com",
                "profile": "Victime d'accident du travail",
                "recommendations": ["Recommendation 1"],
                "droits": ["Droit 1"],
                "demarches": ["Demarche 1"],
                "delais": ["Delai 1"],
                "prestation": "Analyse de dossier AT/MP"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True or "id" in data, "Should return success or id"


class TestPDFUtilsCleanAnalysis:
    """Tests for PDF utils clean_analysis function behavior via API"""
    
    def test_pdf_cleans_raw_urls(self):
        """Test that raw URLs are cleaned from analysis"""
        analysis_with_urls = """## Analyse
Consultez https://some-random-site.com pour plus d'infos.
Ou visitez https://mascot-tips-admin.preview.emergentagent.com/contact
"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": analysis_with_urls,
                "type_dossier": "at",
                "name": "URL Test"
            }
        )
        assert response.status_code == 200
        
        pdf_bytes = base64.b64decode(response.json()["pdf_base64"])
        pdf_text = extract_pdf_text(pdf_bytes).lower()
        
        # Should not contain the injected URLs
        assert "some-random-site.com" not in pdf_text
        assert "mascot-tips-admin" not in pdf_text
    
    def test_pdf_footer_has_correct_copyright(self):
        """Test that PDF footer contains correct copyright with domain"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "## Test\nSimple test.",
                "type_dossier": "at",
                "name": "Footer Test"
            }
        )
        assert response.status_code == 200
        
        pdf_bytes = base64.b64decode(response.json()["pdf_base64"])
        pdf_text = extract_pdf_text(pdf_bytes)
        
        # Check for copyright with correct domain
        assert "Strategie & Expertise Sante" in pdf_text or "Stratégie & Expertise Santé" in pdf_text
        assert "strategie-expertise-sante.fr" in pdf_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
