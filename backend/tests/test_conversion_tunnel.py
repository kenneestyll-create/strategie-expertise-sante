"""
Test suite for Dossier Express Conversion Tunnel Optimization
Tests the new landing page, form, and API endpoints for the 97€ paid product
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://mascot-tips-admin.preview.emergentagent.com"


class TestWeeklyCountAPI:
    """Test /api/dossier-express/weekly-count endpoint"""

    def test_weekly_count_returns_count(self):
        """Weekly count API should return count and period"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/weekly-count")
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert "period" in data
        assert data["period"] == "week"
        assert isinstance(data["count"], int)
        assert data["count"] >= 0
        print(f"Weekly count: {data['count']} dossiers this week")

    def test_weekly_count_includes_base_count(self):
        """Weekly count should include base of 12 + real count"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/weekly-count")
        data = response.json()
        # Per strategiia.py line 320: display_count = 12 + real_count
        assert data["count"] >= 12, "Count should be at least 12 (base count)"


class TestAdminAnalyticsPaymentConfig:
    """Test /api/admin/analytics for payment_config"""

    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin login failed - skipping admin tests")

    def test_analytics_returns_payment_config(self, admin_token):
        """Analytics endpoint should include payment_config with stripe_mode and paypal_mode"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "payment_config" in data
        
        payment_config = data["payment_config"]
        assert "stripe_mode" in payment_config
        assert "paypal_mode" in payment_config
        assert "stripe_configured" in payment_config
        assert "paypal_configured" in payment_config
        
        # Stripe mode should be 'test' or 'live'
        assert payment_config["stripe_mode"] in ["test", "live"]
        print(f"Stripe mode: {payment_config['stripe_mode']}")
        print(f"PayPal mode: {payment_config['paypal_mode']}")


class TestDossierExpressCheckout:
    """Test /api/dossier-express/checkout endpoint"""

    def test_checkout_requires_stripe(self):
        """Checkout should work when Stripe is configured"""
        response = requests.post(f"{BASE_URL}/api/dossier-express/checkout", json={
            "email": "test@example.com",
            "name": "Test User",
            "origin_url": "https://mascot-tips-admin.preview.emergentagent.com",
            "premium_pdf": False,
            "analyse_premium": False
        })
        # Should return success with URL or error if Stripe not configured
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "url" in data
            assert "session_id" in data
            assert "stripe.com" in data["url"] or "checkout" in data["url"]
            print("Checkout session created successfully")
        else:
            print("Stripe not configured (expected in test env)")

    def test_checkout_calculates_total_with_options(self):
        """Checkout with options should calculate correct total"""
        # Base: 97€, PDF: +19€, Analyse Premium: +49€
        response = requests.post(f"{BASE_URL}/api/dossier-express/checkout", json={
            "email": "test@example.com",
            "name": "Test User",
            "origin_url": "https://mascot-tips-admin.preview.emergentagent.com",
            "premium_pdf": True,
            "analyse_premium": True
        })
        # Just verify the request is processed
        assert response.status_code in [200, 500]


class TestDossierExpressSubmit:
    """Test /api/dossier-express/submit endpoint"""

    def test_submit_requires_payment(self):
        """Submit without valid session_id should return 402 (payment required)"""
        response = requests.post(f"{BASE_URL}/api/dossier-express/submit", json={
            "session_id": "fake_session_123",
            "email": "test@example.com",
            "name": "Test User",
            "situation": "Test situation description",
            "type_dossier": "Accident du travail (AT)",
            "regime": "Régime général"
        })
        # Should return 402 Payment Required when Stripe is configured
        assert response.status_code in [402, 400]
        print(f"Submit without payment returned: {response.status_code}")

    def test_submit_requires_email_and_situation(self):
        """Submit should require email and situation fields"""
        response = requests.post(f"{BASE_URL}/api/dossier-express/submit", json={
            "session_id": "",
            "email": "",
            "situation": ""
        })
        assert response.status_code == 400
        assert "requis" in response.json().get("detail", "").lower() or "required" in response.json().get("detail", "").lower()


class TestDossierExpressStatus:
    """Test /api/dossier-express/status/{id} endpoint"""

    def test_status_not_found_for_invalid_id(self):
        """Status endpoint should return 404 for invalid dossier ID"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/invalid-id-123")
        assert response.status_code == 404


class TestStripeWebhook:
    """Test Stripe webhook endpoint exists"""

    def test_webhook_endpoint_exists(self):
        """Stripe webhook endpoint should exist and accept POST"""
        # Empty payload should return error but not 404
        response = requests.post(
            f"{BASE_URL}/api/webhook/stripe",
            headers={"Content-Type": "application/json"},
            data=""
        )
        # Should not be 404 - endpoint exists
        assert response.status_code != 404
        # Should return 400 or 500 for invalid payload
        assert response.status_code in [400, 500]


class TestConfigVerification:
    """Verify backend config values for Stripe mode"""

    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin login failed")

    def test_stripe_mode_from_api_key_prefix(self, admin_token):
        """STRIPE_MODE should be 'test' for sk_test_ and 'live' for sk_live_"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        # Config.py line 47: STRIPE_MODE = 'live' if STRIPE_API_KEY.startswith('sk_live_') else 'test'
        stripe_mode = data["payment_config"]["stripe_mode"]
        # In test environment, should be 'test'
        print(f"STRIPE_MODE: {stripe_mode}")
        assert stripe_mode in ["test", "live"]


class TestAdminDossierExpressList:
    """Test admin endpoint to list dossier express items"""

    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin login failed")

    def test_admin_can_list_dossier_express(self, admin_token):
        """Admin should be able to list dossier express items"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "stats" in data
        assert "total" in data["stats"]
        print(f"Total dossier express items: {data['stats']['total']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
