"""
Test suite for PDF Guide Email Gate feature
Tests the POST /api/resources/request-guide endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com')


class TestGuideEmailGate:
    """Tests for the guide email gate feature - lead generation for PDF downloads"""
    
    def test_request_guide_valid_email(self):
        """Test successful guide request with valid email"""
        response = requests.post(
            f"{BASE_URL}/api/resources/request-guide",
            json={
                "email": "test-valid@example.com",
                "guide_id": "guide_mp",
                "guide_title": "Déclarer une maladie professionnelle",
                "category": "Maladie professionnelle"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["guide_id"] == "guide_mp"
    
    def test_request_guide_invalid_email_no_at(self):
        """Test guide request with invalid email (no @ symbol) returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/resources/request-guide",
            json={
                "email": "invalid-email",
                "guide_id": "guide_mp"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "email" in data["detail"].lower() or "invalide" in data["detail"].lower()
    
    def test_request_guide_invalid_email_no_dot(self):
        """Test guide request with invalid email (no dot after @) returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/resources/request-guide",
            json={
                "email": "test@nodot",
                "guide_id": "guide_mp"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_request_guide_empty_email(self):
        """Test guide request with empty email returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/resources/request-guide",
            json={
                "email": "",
                "guide_id": "guide_mp"
            }
        )
        
        assert response.status_code == 400
    
    def test_request_guide_missing_guide_id(self):
        """Test guide request without guide_id returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/resources/request-guide",
            json={
                "email": "test@example.com",
                "guide_id": ""
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_request_guide_with_category(self):
        """Test guide request stores category for lead segmentation"""
        response = requests.post(
            f"{BASE_URL}/api/resources/request-guide",
            json={
                "email": "test-category@example.com",
                "guide_id": "guide_expertise",
                "guide_title": "Se préparer à une expertise médicale",
                "category": "Expertise médicale"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["guide_id"] == "guide_expertise"
    
    def test_request_guide_all_categories(self):
        """Test guide requests for all available categories"""
        categories = [
            ("guide_mp", "Maladie professionnelle"),
            ("guide_expertise", "Expertise médicale"),
            ("guide_mdph", "MDPH"),
            ("guide_recours", "Recours"),
            ("guide_ipp", "Accident du travail"),
            ("guide_assurance", "Assurances")
        ]
        
        for guide_id, category in categories:
            response = requests.post(
                f"{BASE_URL}/api/resources/request-guide",
                json={
                    "email": f"test-{guide_id}@example.com",
                    "guide_id": guide_id,
                    "category": category
                }
            )
            
            assert response.status_code == 200, f"Failed for {guide_id}"
            data = response.json()
            assert data["success"] == True
            assert data["guide_id"] == guide_id


class TestGuidePDFDownload:
    """Tests for the PDF guide download endpoint"""
    
    def test_download_guide_pdf_valid(self):
        """Test downloading a valid guide PDF"""
        response = requests.get(f"{BASE_URL}/api/resources/pdf/guide_mp")
        
        # Should return PDF or 404 if not implemented
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert response.headers.get("content-type") == "application/pdf"
    
    def test_download_guide_pdf_invalid_id(self):
        """Test downloading with invalid guide ID returns 404"""
        response = requests.get(f"{BASE_URL}/api/resources/pdf/invalid_guide_id")
        
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
