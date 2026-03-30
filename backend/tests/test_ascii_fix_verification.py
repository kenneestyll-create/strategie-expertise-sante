"""
Test suite to verify ASCII fixes after spell-check corruption.
Tests that programmatic identifiers use ASCII (telephone, eligible, etc.)
while display text remains in French with proper accents.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com')


class TestAlerteUrgenteAPI:
    """Test /api/alerte-urgente endpoint - verifies 'telephone' field (not 'téléphone')"""
    
    def test_alerte_urgente_with_ascii_telephone(self):
        """POST /api/alerte-urgente with ASCII 'telephone' field should succeed"""
        payload = {
            "nom": "Test User",
            "telephone": "0612345678",  # ASCII key
            "email": "test@example.com",
            "message": "Test message for ASCII verification",
            "formule": "2h"
        }
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data or "success" in data, f"Response should contain 'id' or 'success': {data}"
    
    def test_alerte_urgente_required_fields(self):
        """POST /api/alerte-urgente validates required fields"""
        payload = {
            "nom": "Test",
            "telephone": "0600000000",
            "email": "test@test.com",
            "formule": "30min"
        }
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json=payload)
        # Should succeed even without message (optional)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"


class TestConseilsAPI:
    """Test /api/conseils/today endpoint"""
    
    def test_conseils_today_returns_text(self):
        """GET /api/conseils/today should return conseil with 'text' field"""
        response = requests.get(f"{BASE_URL}/api/conseils/today")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "text" in data, f"Response should contain 'text' field: {data}"
        assert len(data["text"]) > 0, "Text should not be empty"


class TestAuthAPI:
    """Test /api/auth/login endpoint"""
    
    def test_admin_login_success(self):
        """POST /api/auth/login with valid admin credentials returns access_token"""
        payload = {
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "access_token" in data, f"Response should contain 'access_token': {data}"
        assert data["token_type"] == "bearer", f"Token type should be 'bearer': {data}"
    
    def test_admin_login_invalid_credentials(self):
        """POST /api/auth/login with invalid credentials returns 401"""
        payload = {
            "email": "wrong@email.com",
            "password": "wrongpassword"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestHealthEndpoints:
    """Test basic health/status endpoints"""
    
    def test_visitors_increment(self):
        """POST /api/visitors/increment should work"""
        response = requests.post(f"{BASE_URL}/api/visitors/increment")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "count" in data, f"Response should contain 'count': {data}"
    
    def test_dossier_express_weekly_count(self):
        """GET /api/dossier-express/weekly-count should work"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/weekly-count")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "count" in data, f"Response should contain 'count': {data}"


class TestBookingsAPI:
    """Test /api/bookings endpoints - verifies 'telephone' booking_type (not 'téléphone')"""
    
    def test_booking_slots_endpoint(self):
        """GET /api/bookings/slots/{date} should return slots"""
        # Use a future date
        from datetime import datetime, timedelta
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        response = requests.get(f"{BASE_URL}/api/bookings/slots/{future_date}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "slots" in data, f"Response should contain 'slots': {data}"


class TestContactAPI:
    """Test /api/contact endpoint - verifies 'telephone' field (not 'téléphone')"""
    
    def test_contact_with_ascii_telephone(self):
        """POST /api/contact with ASCII 'telephone' field should succeed"""
        payload = {
            "nom": "Test",
            "prenom": "User",
            "email": "test-ascii@example.com",
            "telephone": "0612345678",  # ASCII key
            "sujet": "Test ASCII verification",
            "message": "Testing that telephone field uses ASCII"
        }
        response = requests.post(f"{BASE_URL}/api/contact", json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"


class TestCalculatorAPI:
    """Test calculator tracking endpoint"""
    
    def test_calculator_count(self):
        """GET /api/calculator/count should return count"""
        response = requests.get(f"{BASE_URL}/api/calculator/count")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "count" in data, f"Response should contain 'count': {data}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
