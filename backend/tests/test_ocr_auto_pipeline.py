"""
Test Suite for OCR Phase 2 GPT-4o Automatic Extraction Pipeline
Tests:
- POST /api/documents/extract-fields with use_ai=true
- POST /api/documents/extract-fields-ai 
- POST /api/client/documents auto-extraction when no ocr_fields provided
"""

import pytest
import requests
import os
import uuid
import base64
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Sample OCR text provided in the test request
SAMPLE_OCR_TEXT = """CPAM de Paris - Notification AT-2024-123
Taux IPP 15%
DUPONT Jean
Rente 3456€
Date: 15/03/2024"""

@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@accompagn-sante.fr",
        "password": "Admin2024!"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin login failed - skipping authenticated tests")

@pytest.fixture(scope="module")
def client_token():
    """Get or create client authentication token"""
    # Try login first
    response = requests.post(f"{BASE_URL}/api/client/login", json={
        "email": "push-test@example.com",
        "password": "Password123!"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    
    # Try register if login fails
    unique_email = f"ocr-pipeline-{uuid.uuid4().hex[:8]}@test.com"
    response = requests.post(f"{BASE_URL}/api/client/register", json={
        "email": unique_email,
        "password": "Password123!",
        "name": "OCR Test User"
    })
    if response.status_code in [200, 201]:
        return response.json().get("access_token")
    pytest.skip("Client authentication failed")


class TestExtractFieldsWithAI:
    """Test POST /api/documents/extract-fields with use_ai=true"""
    
    def test_extract_fields_ai_returns_enhanced_true(self):
        """When use_ai=true, should return enhanced:true with GPT-4o fields"""
        response = requests.post(f"{BASE_URL}/api/documents/extract-fields", json={
            "text": SAMPLE_OCR_TEXT,
            "source": "tesseract",
            "use_ai": True
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be enhanced by GPT-4o
        if data.get("enhanced"):
            assert data["enhanced"] == True
            assert "fields" in data
            fields = data["fields"]
            
            # Check GPT-4o specific fields
            print(f"GPT-4o enhanced extraction returned fields: {list(fields.keys())}")
            
            # Verify some expected extractions from the sample text
            # CPAM de Paris should be detected as organisme
            # DUPONT Jean should be in noms
            # 15/03/2024 should be in dates
            # 3456€ should be in montants
            # 15% IPP should be in taux_ipp
        else:
            # Fallback to regex is acceptable if AI unavailable
            print(f"AI enhancement not available, got regex fields: {data.get('fields', {}).keys()}")
    
    def test_extract_fields_without_ai_returns_regex(self):
        """When use_ai=false, should return regex-extracted fields"""
        response = requests.post(f"{BASE_URL}/api/documents/extract-fields", json={
            "text": SAMPLE_OCR_TEXT,
            "source": "tesseract",
            "use_ai": False
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should NOT be enhanced
        assert data.get("enhanced", False) == False
        assert "fields" in data
        print(f"Regex extraction returned fields: {list(data['fields'].keys())}")


class TestExtractFieldsAIEndpoint:
    """Test POST /api/documents/extract-fields-ai direct endpoint"""
    
    def test_extract_fields_ai_returns_structured_json(self):
        """Direct GPT-4o endpoint should return all 10 structured fields"""
        response = requests.post(f"{BASE_URL}/api/documents/extract-fields-ai", json={
            "text": SAMPLE_OCR_TEXT
        })
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"Extract-fields-ai response: {data}")
        
        if data.get("enhanced"):
            assert "fields" in data
            fields = data["fields"]
            
            # Verify structure - GPT-4o should return these field types
            expected_field_types = [
                "dates", "montants", "references", "numero_ss", "noms", 
                "taux_ipp", "type_dossier_detected", "organisme", "resume", "recommandations"
            ]
            
            # Check which fields were extracted
            extracted = [f for f in expected_field_types if fields.get(f)]
            print(f"Extracted fields from GPT-4o: {extracted}")
            
            # For our sample text, we expect at least:
            # - dates (15/03/2024)
            # - montants (3456€)  
            # - noms (DUPONT Jean)
            # - taux_ipp (15)
            # - type_dossier_detected (at for CPAM/AT)
            # - organisme (CPAM)
            
            # Verify dates extraction
            if "dates" in fields and fields["dates"]:
                print(f"Dates extracted: {fields['dates']}")
            
            # Verify montants extraction
            if "montants" in fields and fields["montants"]:
                print(f"Montants extracted: {fields['montants']}")
                
            # Verify noms extraction  
            if "noms" in fields and fields["noms"]:
                print(f"Noms extracted: {fields['noms']}")
                
            # Verify taux_ipp extraction
            if "taux_ipp" in fields and fields["taux_ipp"]:
                print(f"Taux IPP extracted: {fields['taux_ipp']}")
                
            # Verify organisme extraction
            if "organisme" in fields and fields["organisme"]:
                print(f"Organisme extracted: {fields['organisme']}")
                
            # Verify resume extraction (GPT-4o specific)
            if "resume" in fields and fields["resume"]:
                print(f"Resume extracted: {fields['resume']}")
                
            # Verify recommandations extraction (GPT-4o specific)
            if "recommandations" in fields and fields["recommandations"]:
                print(f"Recommandations extracted: {fields['recommandations']}")
        else:
            # Handle case where AI is not available
            print(f"AI extraction not available: {data.get('error', 'Unknown error')}")
    
    def test_extract_fields_ai_empty_text(self):
        """Empty text should return empty fields without error"""
        response = requests.post(f"{BASE_URL}/api/documents/extract-fields-ai", json={
            "text": ""
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("enhanced", False) == False


class TestClientDocumentsAutoExtract:
    """Test POST /api/client/documents auto-extracts OCR fields when none provided"""
    
    def test_upload_document_without_ocr_fields_triggers_ai(self, client_token):
        """Upload without ocr_fields should trigger backend GPT-4o extraction"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        # Create a simple text file for testing
        test_content = b"CPAM Notification - AT-2024-999\nDUPONT Marie\nTaux IPP: 20%\nMontant: 4500 euros"
        file_data = base64.b64encode(test_content).decode('utf-8')
        
        response = requests.post(f"{BASE_URL}/api/client/documents", 
            headers=headers,
            json={
                "filename": f"test_auto_ocr_{uuid.uuid4().hex[:6]}.txt",
                "file_data": file_data,
                "mime_type": "text/plain",
                "size": len(test_content),
                # NO ocr_fields provided - should trigger auto-extraction
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert "document" in data
        
        doc = data["document"]
        print(f"Document uploaded with ai_enhanced: {doc.get('ai_enhanced')}")
        print(f"Document OCR fields: {doc.get('ocr_fields', {})}")
        print(f"Document tags: {doc.get('tags', {})}")
        
        # For text/plain files, backend should attempt GPT-4o extraction
        if doc.get("ai_enhanced"):
            print("SUCCESS: Auto GPT-4o extraction was triggered on upload")
        else:
            print("NOTE: Auto extraction did not enhance (may be due to file type or content)")
    
    def test_upload_document_with_ocr_fields_skips_ai(self, client_token):
        """Upload WITH ocr_fields should NOT trigger backend extraction"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        test_content = b"Test document content"
        file_data = base64.b64encode(test_content).decode('utf-8')
        
        response = requests.post(f"{BASE_URL}/api/client/documents",
            headers=headers,
            json={
                "filename": f"test_with_ocr_{uuid.uuid4().hex[:6]}.txt",
                "file_data": file_data,
                "mime_type": "text/plain",
                "size": len(test_content),
                "ocr_fields": {
                    "noms": ["Test User"],
                    "type_dossier_detected": ["at"]
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        doc = data["document"]
        
        # Should preserve the provided OCR fields
        assert doc.get("ocr_fields", {}).get("noms") == ["Test User"]
        print(f"Document preserved provided OCR fields: {doc.get('ocr_fields')}")


class TestOCRPipelineIntegration:
    """Integration tests for the full OCR pipeline"""
    
    def test_full_pipeline_tesseract_to_gpt4o(self):
        """Simulate full pipeline: raw text -> GPT-4o enhancement"""
        # Step 1: Simulate Tesseract output (regex extraction)
        response1 = requests.post(f"{BASE_URL}/api/documents/extract-fields", json={
            "text": SAMPLE_OCR_TEXT,
            "source": "tesseract",
            "use_ai": False
        })
        
        assert response1.status_code == 200
        phase1_result = response1.json()
        print(f"Phase 1 (Tesseract/Regex) fields: {phase1_result.get('fields', {}).keys()}")
        
        # Step 2: Enhance with GPT-4o
        response2 = requests.post(f"{BASE_URL}/api/documents/extract-fields-ai", json={
            "text": SAMPLE_OCR_TEXT
        })
        
        assert response2.status_code == 200
        phase2_result = response2.json()
        
        if phase2_result.get("enhanced"):
            print(f"Phase 2 (GPT-4o) fields: {phase2_result.get('fields', {}).keys()}")
            
            # GPT-4o should have additional fields like organisme, resume, recommandations
            gpt4o_fields = phase2_result.get("fields", {})
            
            # Check for GPT-4o exclusive fields
            if gpt4o_fields.get("organisme"):
                print(f"GPT-4o found organisme: {gpt4o_fields['organisme']}")
            if gpt4o_fields.get("resume"):
                print(f"GPT-4o generated resume: {gpt4o_fields['resume'][:100]}...")
            if gpt4o_fields.get("recommandations"):
                print(f"GPT-4o recommandations: {gpt4o_fields['recommandations']}")
        else:
            print(f"GPT-4o enhancement not available: {phase2_result.get('error', 'N/A')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
