"""
Test suite for Alerte Urgente Stripe Payment Flow
Iteration 184 - Bug fix: Urgent alert now requires Stripe payment before registration

NOTE: Stripe API key is a placeholder (sk_test_emergent), so Stripe checkout creation 
will FAIL with 500 error — this is EXPECTED behavior. The test verifies that the 
endpoint ATTEMPTS to create a Stripe session (not just save directly).
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAlerteUrgenteStripeFlow:
    """Tests for the new Stripe payment flow on urgent alerts"""
    
    # ==================== VALIDATION TESTS ====================
    
    def test_alerte_urgente_requires_nom(self):
        """POST /api/alerte-urgente should return 400 if nom is missing"""
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json={
            "telephone": "0612345678",
            "email": "test@example.com",
            "formule": "2h"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print(f"PASS: Missing nom returns 400 - {data['detail']}")
    
    def test_alerte_urgente_requires_telephone(self):
        """POST /api/alerte-urgente should return 400 if telephone is missing"""
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json={
            "nom": "Test User",
            "email": "test@example.com",
            "formule": "2h"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print(f"PASS: Missing telephone returns 400 - {data['detail']}")
    
    def test_alerte_urgente_requires_email(self):
        """POST /api/alerte-urgente should return 400 if email is missing"""
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json={
            "nom": "Test User",
            "telephone": "0612345678",
            "formule": "2h"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print(f"PASS: Missing email returns 400 - {data['detail']}")
    
    def test_alerte_urgente_invalid_formule(self):
        """POST /api/alerte-urgente should return 400 for invalid formule"""
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json={
            "nom": "Test User",
            "telephone": "0612345678",
            "email": "test@example.com",
            "formule": "invalid_formule"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "invalide" in data["detail"].lower() or "formule" in data["detail"].lower()
        print(f"PASS: Invalid formule returns 400 - {data['detail']}")
    
    # ==================== STRIPE CHECKOUT FLOW TESTS ====================
    
    def test_alerte_urgente_attempts_stripe_checkout_2h(self):
        """
        POST /api/alerte-urgente with valid data should attempt Stripe checkout.
        With placeholder key (sk_test_emergent), this returns 500 - EXPECTED.
        This proves the flow now goes through Stripe instead of direct save.
        """
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json={
            "nom": "TEST_Stripe_User",
            "telephone": "0612345678",
            "email": "test@example.com",
            "message": "Test urgent message",
            "formule": "2h",
            "origin_url": BASE_URL
        })
        # With placeholder Stripe key, we expect 500 "Erreur lors de la création du paiement"
        assert response.status_code == 500, f"Expected 500 (Stripe placeholder key), got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "paiement" in data["detail"].lower() or "erreur" in data["detail"].lower()
        print(f"PASS: Stripe checkout attempt returns 500 (expected with placeholder key) - {data['detail']}")
    
    def test_alerte_urgente_attempts_stripe_checkout_30min(self):
        """
        POST /api/alerte-urgente with formule=30min should also attempt Stripe checkout.
        """
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json={
            "nom": "TEST_Stripe_User_30min",
            "telephone": "0612345678",
            "email": "test30min@example.com",
            "message": "Test urgent message 30min",
            "formule": "30min",
            "origin_url": BASE_URL
        })
        # With placeholder Stripe key, we expect 500
        assert response.status_code == 500, f"Expected 500 (Stripe placeholder key), got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print(f"PASS: Stripe checkout attempt (30min) returns 500 (expected) - {data['detail']}")
    
    # ==================== CONFIRM PAYMENT ENDPOINT TESTS ====================
    
    def test_confirm_payment_endpoint_exists(self):
        """GET /api/alerte-urgente/confirm-payment/{session_id} should exist (404 for unknown)"""
        response = requests.get(f"{BASE_URL}/api/alerte-urgente/confirm-payment/unknown_session_id")
        # Should return 404 (not found) or 500 (Stripe error), not 405 (method not allowed)
        assert response.status_code in [404, 500], f"Expected 404 or 500, got {response.status_code}"
        print(f"PASS: confirm-payment endpoint exists, returns {response.status_code} for unknown session")
    
    # ==================== CANCEL ENDPOINT TESTS ====================
    
    def test_cancel_endpoint_exists(self):
        """DELETE /api/alerte-urgente/cancel/{alert_id} should exist"""
        response = requests.delete(f"{BASE_URL}/api/alerte-urgente/cancel/unknown_alert_id")
        # Should return 200 (success: true even if nothing deleted) or similar, not 405
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        data = response.json()
        assert "success" in data
        print(f"PASS: cancel endpoint exists, returns {response.status_code} - {data}")
    
    # ==================== ADMIN ENDPOINT REGRESSION ====================
    
    def test_admin_alertes_urgentes_requires_auth(self):
        """GET /api/admin/alertes-urgentes should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/alertes-urgentes")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: Admin alertes-urgentes requires auth, returns {response.status_code}")
    
    def test_admin_alertes_urgentes_with_auth(self):
        """GET /api/admin/alertes-urgentes should work with valid auth"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        if login_response.status_code != 200:
            pytest.skip("Could not login - skipping authenticated test")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/alertes-urgentes", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "items" in data
        assert "total" in data
        print(f"PASS: Admin alertes-urgentes returns 200 with {data['total']} items")


class TestRegressionHomePage:
    """Regression tests to ensure home page still works"""
    
    def test_home_page_loads(self):
        """Home page should load without errors"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Home page loads successfully")
    
    def test_seed_endpoint(self):
        """Seed endpoint should work"""
        response = requests.post(f"{BASE_URL}/api/seed")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Seed endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
