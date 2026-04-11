# Test consent-log endpoint for CGV legal compliance
# Iteration 186 - Legal compliance testing

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestConsentLogEndpoint:
    """Tests for POST /api/consent-log endpoint - CGV legal compliance"""
    
    def test_consent_log_success(self):
        """Test successful consent logging with all required fields"""
        response = requests.post(f"{BASE_URL}/api/consent-log", json={
            "email": "test_cgv@example.com",
            "service": "question_urgente_2h",
            "cgv_accepted": True,
            "retractation_waived": True
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "consent_id" in data
        print(f"PASS: Consent logged successfully with ID: {data['consent_id']}")
    
    def test_consent_log_missing_email(self):
        """Test consent-log returns 400 when email is missing"""
        response = requests.post(f"{BASE_URL}/api/consent-log", json={
            "service": "question_urgente_2h",
            "cgv_accepted": True,
            "retractation_waived": True
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("PASS: Returns 400 when email is missing")
    
    def test_consent_log_missing_service(self):
        """Test consent-log returns 400 when service is missing"""
        response = requests.post(f"{BASE_URL}/api/consent-log", json={
            "email": "test_cgv@example.com",
            "cgv_accepted": True,
            "retractation_waived": True
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("PASS: Returns 400 when service is missing")
    
    def test_consent_log_empty_email(self):
        """Test consent-log returns 400 when email is empty string"""
        response = requests.post(f"{BASE_URL}/api/consent-log", json={
            "email": "",
            "service": "question_urgente_2h",
            "cgv_accepted": True,
            "retractation_waived": True
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("PASS: Returns 400 when email is empty")
    
    def test_consent_log_empty_service(self):
        """Test consent-log returns 400 when service is empty string"""
        response = requests.post(f"{BASE_URL}/api/consent-log", json={
            "email": "test_cgv@example.com",
            "service": "",
            "cgv_accepted": True,
            "retractation_waived": True
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("PASS: Returns 400 when service is empty")
    
    def test_consent_log_booking_conseil(self):
        """Test consent logging for booking_conseil service"""
        response = requests.post(f"{BASE_URL}/api/consent-log", json={
            "email": "test_booking@example.com",
            "service": "booking_conseil",
            "cgv_accepted": True,
            "retractation_waived": True
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print(f"PASS: Consent logged for booking_conseil with ID: {data['consent_id']}")
    
    def test_consent_log_30min_formule(self):
        """Test consent logging for question_urgente_30min service"""
        response = requests.post(f"{BASE_URL}/api/consent-log", json={
            "email": "test_30min@example.com",
            "service": "question_urgente_30min",
            "cgv_accepted": True,
            "retractation_waived": True
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print(f"PASS: Consent logged for question_urgente_30min with ID: {data['consent_id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
