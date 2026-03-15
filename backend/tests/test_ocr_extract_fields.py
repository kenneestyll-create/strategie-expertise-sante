"""
Test OCR Field Extraction - Iteration 38

Tests for POST /api/documents/extract-fields endpoint
This is Phase 1 Tesseract.js OCR with backend field extraction
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestOCRExtractFieldsBasic:
    """Basic OCR field extraction tests"""

    def test_extract_fields_empty_text(self):
        """POST /api/documents/extract-fields with empty text returns empty fields"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "", "source": "tesseract"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["fields"] == {}, f"Expected empty fields, got {data['fields']}"
        assert data["source"] == "tesseract"
        assert data["enhanced"] == False
        print("✓ TEST 1: Empty text returns empty fields")

    def test_extract_fields_whitespace_only(self):
        """POST /api/documents/extract-fields with whitespace only returns empty fields"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "   \n\t   ", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["fields"] == {}
        assert data["enhanced"] == False
        print("✓ TEST 2: Whitespace-only text returns empty fields")


class TestOCRExtractDates:
    """Date extraction tests"""

    def test_extract_date_slash_format(self):
        """Extracts dates in dd/mm/yyyy format"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Accident du travail du 12/01/2024", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "dates" in data["fields"], f"Expected dates field, got {data['fields']}"
        assert "12/01/2024" in data["fields"]["dates"]
        print("✓ TEST 3: Extracts dates in dd/mm/yyyy format")

    def test_extract_date_dash_format(self):
        """Extracts dates in dd-mm-yyyy format"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Date de naissance: 15-03-1975", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "dates" in data["fields"]
        assert "15-03-1975" in data["fields"]["dates"]
        print("✓ TEST 4: Extracts dates in dd-mm-yyyy format")

    def test_extract_multiple_dates(self):
        """Extracts multiple dates from text"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Né le 15/03/1975\nAccident du 12/01/2024\nConsolidation le 30/06/2024", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "dates" in data["fields"]
        dates = data["fields"]["dates"]
        assert len(dates) >= 2, f"Expected at least 2 dates, got {dates}"
        print("✓ TEST 5: Extracts multiple dates from text")


class TestOCRExtractAmounts:
    """Amount extraction tests (Euro format)"""

    def test_extract_amount_euro_symbol(self):
        """Extracts amounts with € symbol"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Montant: 1.500,00 €", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "montants" in data["fields"], f"Expected montants field, got {data['fields']}"
        print("✓ TEST 6: Extracts amounts with € symbol")

    def test_extract_simple_amount(self):
        """Extracts simple amounts like 97€"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Prix: 97€", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "montants" in data["fields"]
        assert any("97" in m for m in data["fields"]["montants"]), f"Expected 97€, got {data['fields']['montants']}"
        print("✓ TEST 7: Extracts simple amounts like 97€")


class TestOCRExtractReferences:
    """Reference number extraction tests"""

    def test_extract_reference_at_format(self):
        """Extracts reference with AT- format"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Réf dossier: AT-2024-0042", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "references" in data["fields"], f"Expected references field, got {data['fields']}"
        assert "AT-2024-0042" in data["fields"]["references"]
        print("✓ TEST 8: Extracts reference with AT- format")

    def test_extract_reference_numero(self):
        """Extracts reference with N° prefix"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "N° dossier: MP-2024-1234", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "references" in data["fields"]
        print("✓ TEST 9: Extracts reference with N° prefix")


class TestOCRExtractSocialSecurity:
    """Social Security Number extraction tests"""

    def test_extract_ss_number_with_spaces(self):
        """Extracts SS number in French format with spaces"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "N° SS: 1 75 03 75 123 456 78", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "numero_ss" in data["fields"], f"Expected numero_ss field, got {data['fields']}"
        # Should be cleaned to 175037512345678
        assert data["fields"]["numero_ss"] == "175037512345678"
        print("✓ TEST 10: Extracts SS number in French format with spaces")

    def test_extract_ss_number_continuous(self):
        """Extracts SS number without spaces"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Numéro SS: 275047512345678", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "numero_ss" in data["fields"]
        print("✓ TEST 11: Extracts SS number without spaces")


class TestOCRExtractNames:
    """Name extraction tests"""

    def test_extract_name_patient(self):
        """Extracts name after Patient: prefix"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Patient: Jean Dupont", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "noms" in data["fields"], f"Expected noms field, got {data['fields']}"
        assert "Jean Dupont" in data["fields"]["noms"]
        print("✓ TEST 12: Extracts name after Patient: prefix")

    def test_extract_name_assure(self):
        """Extracts name after Assuré: prefix"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Assuré: Marie Martin", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "noms" in data["fields"]
        print("✓ TEST 13: Extracts name after Assuré: prefix")


class TestOCRExtractIPP:
    """IPP rate extraction tests"""

    def test_extract_taux_ipp(self):
        """Extracts IPP rate percentage"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Taux IPP: 25%", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "taux_ipp" in data["fields"], f"Expected taux_ipp field, got {data['fields']}"
        assert 25 in data["fields"]["taux_ipp"]
        print("✓ TEST 14: Extracts IPP rate percentage")

    def test_extract_incapacite_rate(self):
        """Extracts taux incapacité rate"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "taux incapacité : 15%", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "taux_ipp" in data["fields"]
        assert 15 in data["fields"]["taux_ipp"]
        print("✓ TEST 15: Extracts taux incapacité rate")


class TestOCRExtractDocumentType:
    """Document type detection tests"""

    def test_detect_type_at(self):
        """Detects Accident du travail document type"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Déclaration d'accident du travail", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "type_dossier_detected" in data["fields"]
        assert "at" in data["fields"]["type_dossier_detected"]
        print("✓ TEST 16: Detects Accident du travail document type")

    def test_detect_type_mp(self):
        """Detects Maladie professionnelle document type"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Maladie professionnelle reconnue", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "type_dossier_detected" in data["fields"]
        assert "mp" in data["fields"]["type_dossier_detected"]
        print("✓ TEST 17: Detects Maladie professionnelle document type")

    def test_detect_type_mdph(self):
        """Detects MDPH document type"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Notification MDPH - AAH accordée", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "type_dossier_detected" in data["fields"]
        assert "mdph" in data["fields"]["type_dossier_detected"]
        print("✓ TEST 18: Detects MDPH document type")

    def test_detect_type_ipp(self):
        """Detects IPP contestation document type"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Contestation taux IPP - incapacité permanente", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "type_dossier_detected" in data["fields"]
        assert "ipp" in data["fields"]["type_dossier_detected"]
        print("✓ TEST 19: Detects IPP contestation document type")


class TestOCRExtractComplex:
    """Complex text extraction tests with multiple fields"""

    def test_extract_complete_french_medical_text(self):
        """Extracts all fields from complete French medical document text"""
        test_text = """Patient: Jean Dupont
N° SS: 1 75 03 75 123 456 78
Accident du travail du 12/01/2024
Taux IPP: 25%
Montant: 1.500,00 €
Réf dossier: AT-2024-0042"""

        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": test_text, "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        fields = data["fields"]
        
        # Verify all expected fields are extracted
        assert "dates" in fields, f"Expected dates field, got {fields}"
        assert "12/01/2024" in fields["dates"], f"Expected date 12/01/2024, got {fields['dates']}"
        
        assert "numero_ss" in fields, f"Expected numero_ss field"
        assert fields["numero_ss"] == "175037512345678"
        
        assert "noms" in fields, f"Expected noms field"
        assert "Jean Dupont" in fields["noms"]
        
        assert "taux_ipp" in fields, f"Expected taux_ipp field"
        assert 25 in fields["taux_ipp"]
        
        assert "references" in fields, f"Expected references field"
        assert "AT-2024-0042" in fields["references"]
        
        assert "type_dossier_detected" in fields
        assert "at" in fields["type_dossier_detected"] or "ipp" in fields["type_dossier_detected"]
        
        # Verify enhanced is False for Phase 1
        assert data["enhanced"] == False
        
        print("✓ TEST 20: Complete French medical text extraction - ALL fields extracted correctly")

    def test_extract_phase1_returns_enhanced_false(self):
        """Phase 1 always returns enhanced=false"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Test text", "source": "tesseract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["enhanced"] == False, "Phase 1 should return enhanced=false"
        print("✓ TEST 21: Phase 1 returns enhanced=false")

    def test_source_parameter_preserved(self):
        """Source parameter is preserved in response"""
        response = requests.post(
            f"{BASE_URL}/api/documents/extract-fields",
            json={"text": "Test text", "source": "gpt4o"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "gpt4o"
        print("✓ TEST 22: Source parameter preserved in response")


# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
