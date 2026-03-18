"""
Backend tests for Dossier Express feature - Iteration 19
Tests:
- POST /api/dossier-express/checkout - Create Stripe checkout session
- POST /api/dossier-express/submit - Submit dossier for analysis
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDossierExpressAPI:
    """Dossier Express endpoint tests"""
    
    def test_dossier_express_checkout_success(self):
        """Test POST /api/dossier-express/checkout returns success with url and session_id"""
        response = requests.post(f"{BASE_URL}/api/dossier-express/checkout", json={
            "email": "test@example.com",
            "name": "Test User",
            "origin_url": "https://occupational-scan.preview.emergentagent.com"
        })
        
        # Should return 200 with checkout url
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data, f"Response missing 'url' field: {data}"
        assert "session_id" in data, f"Response missing 'session_id' field: {data}"
        assert data.get("success") == True, f"Expected success=True: {data}"
        
        # URL should be a Stripe checkout URL
        assert data["url"].startswith("https://"), f"URL should be HTTPS: {data['url']}"
        print(f"✓ Dossier Express checkout successful - session_id: {data['session_id'][:20]}...")

    def test_dossier_express_checkout_without_email(self):
        """Test checkout still works with minimal data"""
        response = requests.post(f"{BASE_URL}/api/dossier-express/checkout", json={
            "origin_url": "https://occupational-scan.preview.emergentagent.com"
        })
        
        # Should still succeed (email is optional for checkout creation)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "url" in data
        print("✓ Dossier Express checkout works without email")

    def test_dossier_express_submit_success(self):
        """Test POST /api/dossier-express/submit returns success with dossier_id"""
        response = requests.post(f"{BASE_URL}/api/dossier-express/submit", json={
            "session_id": "test_session_123",
            "email": "testuser@example.com",
            "name": "Test User",
            "situation": "Je suis victime d'un accident du travail. Mon employeur conteste la déclaration AT. Je cherche à comprendre mes droits et les recours possibles.",
            "type_dossier": "Accident du travail (AT)",
            "regime": "Régime général",
            "documents_text": ""
        })
        
        # Should return 200 with dossier_id
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "dossier_id" in data, f"Response missing 'dossier_id' field: {data}"
        assert data.get("success") == True, f"Expected success=True: {data}"
        
        print(f"✓ Dossier Express submit successful - dossier_id: {data['dossier_id'][:20]}...")
        
        return data["dossier_id"]

    def test_dossier_express_submit_missing_email(self):
        """Test submit fails without required email"""
        response = requests.post(f"{BASE_URL}/api/dossier-express/submit", json={
            "session_id": "test_session_123",
            "name": "Test User",
            "situation": "Ma situation de test",
            "type_dossier": "Accident du travail (AT)",
            "regime": "Régime général"
        })
        
        # Should return 400 (email required)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("✓ Submit correctly rejects request without email")

    def test_dossier_express_submit_missing_situation(self):
        """Test submit fails without required situation"""
        response = requests.post(f"{BASE_URL}/api/dossier-express/submit", json={
            "session_id": "test_session_123",
            "email": "test@example.com",
            "name": "Test User",
            "type_dossier": "Accident du travail (AT)",
            "regime": "Régime général"
        })
        
        # Should return 400 (situation required)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("✓ Submit correctly rejects request without situation")

    def test_dossier_express_status_not_found(self):
        """Test GET /api/dossier-express/status returns 404 for non-existent dossier"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/nonexistent123")
        
        # Should return 404
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print("✓ Status endpoint correctly returns 404 for non-existent dossier")


class TestTarifsPaymentPackages:
    """Test payment packages defined on backend"""
    
    def test_dossier_express_package_exists(self):
        """Verify dossier_express package exists in payment packages"""
        response = requests.get(f"{BASE_URL}/api/payments/packages")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        packages = response.json()
        package_ids = [p["id"] for p in packages]
        
        assert "dossier_express" in package_ids, f"'dossier_express' not in packages: {package_ids}"
        
        # Check dossier_express has correct amount (97 EUR)
        dossier_pkg = next((p for p in packages if p["id"] == "dossier_express"), None)
        assert dossier_pkg is not None
        assert dossier_pkg["amount"] == 97.00, f"Expected 97.00, got {dossier_pkg['amount']}"
        assert dossier_pkg["currency"] == "eur"
        
        print(f"✓ Dossier Express package verified: {dossier_pkg['name']} - {dossier_pkg['amount']}€")


class TestHealthAndBasicEndpoints:
    """Basic health checks"""
    
    def test_api_health(self):
        """Test API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ API health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
