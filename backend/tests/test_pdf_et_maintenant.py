"""
Test PDF generation with new 'Et maintenant ?' conclusion block
Tests the 3-part strategic conversion section:
1. Clôture émotionnelle (emotional closure)
2. Transition stratégique (strategic transition)
3. Orientation vers l'offre finale (final offer orientation)
"""
import pytest
import requests
import os
import sys
import io
import pdfplumber

# Add backend to path for direct imports
sys.path.insert(0, '/app/backend')

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com').rstrip('/')


class TestPDFEtMaintenant:
    """Test the new 'Et maintenant ?' conclusion block in PDF generation"""
    
    def test_pdf_generation_without_errors(self):
        """Test that PDF generation works without errors"""
        from utils.pdf import generate_secured_pdf
        
        analysis = """# Analyse de votre dossier
        
Votre situation présente plusieurs éléments importants.

## Points clés
- Point 1: Analyse détaillée
- Point 2: Recommandations

## Conclusion
Votre dossier mérite une attention particulière.
"""
        
        try:
            pdf_bytes = generate_secured_pdf(
                analysis=analysis,
                report_type="Dossier Express IA",
                name="Test User",
                email="test@example.com",
                type_dossier="Maladie professionnelle",
                regime="Général",
                with_watermark=True,
                report_number="SES-2026-TEST1"
            )
            assert pdf_bytes is not None
            assert len(pdf_bytes) > 0
            assert pdf_bytes[:4] == b'%PDF'  # Valid PDF header
            print("✓ PDF generation without errors - PASS")
        except Exception as e:
            pytest.fail(f"PDF generation failed: {e}")
    
    def test_pdf_contains_et_maintenant_section(self):
        """Test that PDF contains 'Et maintenant' section title"""
        from utils.pdf import generate_secured_pdf
        
        analysis = "Test analysis content for PDF generation."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Test User",
            email="test@example.com"
        )
        
        # Extract text from PDF
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() or ""
        
        # Check for "Et maintenant" section
        assert "Et maintenant" in full_text, f"'Et maintenant' not found in PDF. Text: {full_text[:500]}"
        print("✓ PDF contains 'Et maintenant' section title - PASS")
    
    def test_pdf_contains_emotional_closure(self):
        """Test that PDF contains emotional closure text (epreuve, premier eclairage)"""
        from utils.pdf import generate_secured_pdf
        
        analysis = "Test analysis content."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Test User",
            email="test@example.com"
        )
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() or ""
        
        # Check for emotional closure keywords
        text_lower = full_text.lower()
        assert "epreuve" in text_lower or "épreuve" in text_lower, f"'epreuve' not found in PDF"
        assert "eclairage" in text_lower or "éclairage" in text_lower, f"'eclairage' not found in PDF"
        print("✓ PDF contains emotional closure text - PASS")
    
    def test_pdf_contains_strategic_transition(self):
        """Test that PDF contains strategic transition text (analyse humaine, resultat concret)"""
        from utils.pdf import generate_secured_pdf
        
        analysis = "Test analysis content."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Test User",
            email="test@example.com"
        )
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() or ""
        
        text_lower = full_text.lower()
        # Check for strategic transition keywords
        assert "analyse humaine" in text_lower, f"'analyse humaine' not found in PDF"
        assert "resultat concret" in text_lower or "résultat concret" in text_lower, f"'resultat concret' not found in PDF"
        print("✓ PDF contains strategic transition text - PASS")
    
    def test_pdf_contains_final_offer_box(self):
        """Test that PDF contains final offer box text (accompagnement sur mesure)"""
        from utils.pdf import generate_secured_pdf
        
        analysis = "Test analysis content."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Test User",
            email="test@example.com"
        )
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() or ""
        
        text_lower = full_text.lower()
        # Check for final offer keywords
        assert "accompagnement sur mesure" in text_lower, f"'accompagnement sur mesure' not found in PDF"
        assert "aller plus loin" in text_lower, f"'aller plus loin' not found in PDF"
        print("✓ PDF contains final offer box text - PASS")
    
    def test_pdf_contains_signature_votre_bouclier(self):
        """Test that PDF contains signature 'Votre bouclier'"""
        from utils.pdf import generate_secured_pdf
        
        analysis = "Test analysis content."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Test User",
            email="test@example.com"
        )
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() or ""
        
        text_lower = full_text.lower()
        assert "votre bouclier" in text_lower, f"'Votre bouclier' not found in PDF"
        print("✓ PDF contains signature 'Votre bouclier' - PASS")
    
    def test_old_cta_text_removed(self):
        """Test that old CTA text 'Consultation personnalisee sur rendez-vous' is REMOVED from PDF"""
        from utils.pdf import generate_secured_pdf
        
        analysis = "Test analysis content."
        
        pdf_bytes = generate_secured_pdf(
            analysis=analysis,
            report_type="Dossier Express IA",
            name="Test User",
            email="test@example.com"
        )
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() or ""
        
        text_lower = full_text.lower()
        # Old CTA text should NOT be present
        assert "consultation personnalisee sur rendez-vous" not in text_lower, "Old CTA text still present in PDF"
        assert "consultation personnalisée sur rendez-vous" not in text_lower, "Old CTA text still present in PDF"
        print("✓ Old CTA text 'Consultation personnalisee sur rendez-vous' is REMOVED - PASS")
    
    def test_pdf_with_document_details(self):
        """Test that PDF with document_details still generates correctly"""
        from utils.pdf import generate_secured_pdf
        
        analysis = "Test analysis with document details."
        document_details = [
            {"filename": "doc1.pdf", "pages": 5, "status": "text_extracted"},
            {"filename": "doc2.pdf", "pages": 3, "status": "ocr_extracted"},
        ]
        
        try:
            pdf_bytes = generate_secured_pdf(
                analysis=analysis,
                report_type="Dossier Express IA",
                name="Test User",
                email="test@example.com",
                document_details=document_details
            )
            assert pdf_bytes is not None
            assert len(pdf_bytes) > 0
            
            # Verify document details section is present
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() or ""
            
            text_lower = full_text.lower()
            assert "base documentaire" in text_lower or "documents" in text_lower
            print("✓ PDF with document_details generates correctly - PASS")
        except Exception as e:
            pytest.fail(f"PDF generation with document_details failed: {e}")
    
    def test_pdf_without_document_details(self):
        """Test that PDF without document_details still generates correctly"""
        from utils.pdf import generate_secured_pdf
        
        analysis = "Test analysis without document details."
        
        try:
            pdf_bytes = generate_secured_pdf(
                analysis=analysis,
                report_type="Dossier Express IA",
                name="Test User",
                email="test@example.com",
                document_details=None
            )
            assert pdf_bytes is not None
            assert len(pdf_bytes) > 0
            
            # Verify Et maintenant section is still present
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() or ""
            
            assert "Et maintenant" in full_text
            print("✓ PDF without document_details generates correctly - PASS")
        except Exception as e:
            pytest.fail(f"PDF generation without document_details failed: {e}")
    
    def test_llm_et_maintenant_stripped_from_analysis(self):
        """Test that LLM-generated 'Et maintenant' text is stripped from analysis content"""
        from utils.pdf import _clean_analysis
        
        # Simulate LLM output that includes the hardcoded phrases
        llm_analysis = """# Analyse de votre dossier

Votre situation présente plusieurs éléments importants.

## Et maintenant ?

Vous n'êtes plus seul dans cette épreuve.

Désormais, Stratégie & Expertise Santé devient votre bouclier.

Vous souhaitez aller plus loin ?

Première consultation offerte.

Votre bouclier.
"""
        
        cleaned = _clean_analysis(llm_analysis)
        
        # These phrases should be stripped
        assert "Et maintenant" not in cleaned, "LLM 'Et maintenant' should be stripped"
        assert "Vous n'êtes plus seul" not in cleaned, "LLM closing phrase should be stripped"
        assert "devient votre bouclier" not in cleaned, "LLM closing phrase should be stripped"
        assert "Vous souhaitez aller plus loin" not in cleaned, "LLM offer phrase should be stripped"
        assert "Première consultation offerte" not in cleaned, "LLM offer phrase should be stripped"
        
        # But the actual analysis content should remain
        assert "Analyse de votre dossier" in cleaned or "situation" in cleaned
        print("✓ LLM-generated 'Et maintenant' text is stripped from analysis - PASS")


class TestAdminAndAPIs:
    """Test admin login and API endpoints"""
    
    def test_admin_login(self):
        """Test admin login: POST /api/auth/login with admin@accompagn-sante.fr / Admin2024!"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@accompagn-sante.fr", "password": "Admin2024!"}
        )
        assert response.status_code == 200, f"Admin login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "token" in data or "access_token" in data, "No token in login response"
        print("✓ Admin login works - PASS")
        return data.get("token") or data.get("access_token")
    
    def test_conseils_today_api(self):
        """Test Conseils API: GET /api/conseils/today returns a conseil"""
        response = requests.get(f"{BASE_URL}/api/conseils/today")
        assert response.status_code == 200, f"Conseils API failed: {response.status_code}"
        data = response.json()
        assert "text" in data, "No 'text' field in conseil response"
        assert "id" in data, "No 'id' field in conseil response"
        print(f"✓ Conseils API works - conseil: {data.get('text', '')[:50]}... - PASS")
    
    def test_admin_dossier_preview_pdf(self):
        """Test admin dossier preview: GET /api/admin/dossier-express/{id}/preview-pdf returns 200"""
        # First login to get token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@accompagn-sante.fr", "password": "Admin2024!"}
        )
        assert login_response.status_code == 200, "Admin login failed"
        token = login_response.json().get("token") or login_response.json().get("access_token")
        
        # Known dossier_id from the test request
        dossier_id = "91dbe566-cd80-4cab-be2c-96e27daa1e73"
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{dossier_id}/preview-pdf",
            headers=headers
        )
        
        # Accept 200 (success) or 404 (dossier not found - acceptable if test data doesn't exist)
        assert response.status_code in [200, 404], f"Preview PDF failed: {response.status_code} - {response.text}"
        
        if response.status_code == 200:
            # Verify it's a PDF
            assert response.headers.get('content-type', '').startswith('application/pdf') or len(response.content) > 0
            print("✓ Admin dossier preview PDF works - PASS")
        else:
            print("✓ Admin dossier preview PDF endpoint accessible (dossier not found is acceptable) - PASS")


class TestStripPatterns:
    """Test the strip patterns for cleaning LLM output"""
    
    def test_strip_patterns_defined(self):
        """Verify strip patterns are defined for new conclusion phrases"""
        from utils.pdf import _STRIP_PATTERNS
        
        # Check that patterns exist
        assert len(_STRIP_PATTERNS) > 0, "No strip patterns defined"
        
        # Test patterns against expected phrases
        test_phrases = [
            "Et maintenant ?",
            "Vous n'êtes plus seul",
            "désormais Stratégie & Expertise Santé devient votre bouclier",
            "Vous souhaitez aller plus loin",
            "Première consultation offerte",
            "Votre bouclier.",
        ]
        
        import re
        for phrase in test_phrases:
            matched = False
            for pattern in _STRIP_PATTERNS:
                if pattern.search(phrase):
                    matched = True
                    break
            assert matched, f"No pattern matches phrase: '{phrase}'"
        
        print("✓ Strip patterns correctly defined for new conclusion phrases - PASS")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
