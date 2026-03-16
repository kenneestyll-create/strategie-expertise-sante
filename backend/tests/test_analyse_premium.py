"""
Test Analyse Premium feature:
1. POST /api/dossier-express/checkout with analyse_premium flag
2. GET /api/admin/premium-analyses returns stats with en_attente/en_cours/termine
3. PATCH /api/admin/premium-analyses/{id} updates status (test invalid id returns 404)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


class TestAnalysePremium:
    """Test suite for Analyse Premium feature"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        """Auth headers for admin requests"""
        return {"Authorization": f"Bearer {admin_token}"}

    # Test 1: Dossier Express checkout accepts analyse_premium flag
    def test_dossier_express_checkout_with_analyse_premium(self):
        """Test POST /api/dossier-express/checkout accepts analyse_premium and adjusts amount"""
        # Base price: 97€
        # With analyse_premium (+49€): 146€
        # With both analyse_premium (+49€) + premium_pdf (+19€): 165€
        
        payload = {
            "email": "test-premium@example.com",
            "name": "Test User Premium",
            "origin_url": "https://engage-suite-3.preview.emergentagent.com",
            "premium_pdf": False,
            "analyse_premium": True  # +49€
        }
        
        response = requests.post(f"{BASE_URL}/api/dossier-express/checkout", json=payload)
        assert response.status_code == 200, f"Checkout failed: {response.text}"
        
        data = response.json()
        assert "url" in data, "No Stripe URL in response"
        assert data.get("success") == True, "success should be True"
        print(f"TEST 1 PASSED: Dossier Express checkout with analyse_premium accepted")

    def test_dossier_express_checkout_both_options(self):
        """Test checkout with both analyse_premium and premium_pdf options"""
        payload = {
            "email": "test-both@example.com",
            "name": "Test Both Options",
            "origin_url": "https://engage-suite-3.preview.emergentagent.com",
            "premium_pdf": True,      # +19€
            "analyse_premium": True   # +49€
            # Total: 97 + 19 + 49 = 165€
        }
        
        response = requests.post(f"{BASE_URL}/api/dossier-express/checkout", json=payload)
        assert response.status_code == 200, f"Checkout failed: {response.text}"
        
        data = response.json()
        assert "url" in data, "No Stripe URL in response"
        print(f"TEST 2 PASSED: Dossier Express checkout with both options accepted")

    # Test 2: Admin premium-analyses GET returns stats
    def test_admin_premium_analyses_returns_stats(self, auth_headers):
        """Test GET /api/admin/premium-analyses returns stats with en_attente/en_cours/termine"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses", headers=auth_headers)
        assert response.status_code == 200, f"Failed to get premium analyses: {response.text}"
        
        data = response.json()
        
        # Check structure
        assert "items" in data, "Response should have 'items'"
        assert "stats" in data, "Response should have 'stats'"
        
        stats = data["stats"]
        assert "total" in stats, "Stats should have 'total'"
        assert "en_attente" in stats, "Stats should have 'en_attente'"
        assert "en_cours" in stats, "Stats should have 'en_cours'"
        assert "termine" in stats, "Stats should have 'termine'"
        
        # Validate stats are integers
        assert isinstance(stats["total"], int), "total should be int"
        assert isinstance(stats["en_attente"], int), "en_attente should be int"
        assert isinstance(stats["en_cours"], int), "en_cours should be int"
        assert isinstance(stats["termine"], int), "termine should be int"
        
        print(f"TEST 3 PASSED: Admin premium-analyses returns stats: {stats}")

    # Test 3: PATCH with invalid ID returns 404
    def test_admin_premium_analyses_patch_invalid_id_returns_404(self, auth_headers):
        """Test PATCH /api/admin/premium-analyses/{id} with invalid id returns 404"""
        fake_id = "non-existent-id-12345"
        
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/{fake_id}",
            headers=auth_headers,
            json={"status": "en_cours"}
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"TEST 4 PASSED: PATCH with invalid ID returns 404")

    # Test 4: PATCH with invalid status returns 400
    def test_admin_premium_analyses_patch_invalid_status(self, auth_headers):
        """Test PATCH /api/admin/premium-analyses/{id} with invalid status returns 400"""
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/some-id",
            headers=auth_headers,
            json={"status": "invalid_status"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print(f"TEST 5 PASSED: PATCH with invalid status returns 400")

    # Test 5: Require auth for premium-analyses endpoints
    def test_admin_premium_analyses_requires_auth(self):
        """Test that admin endpoints require authentication"""
        # No auth header
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses")
        assert response.status_code in (401, 403), f"Expected 401/403, got {response.status_code}"
        print(f"TEST 6 PASSED: Admin premium-analyses requires auth")


class TestStrategiIACheckout:
    """Test StrategiIA checkout with analyse_premium option"""
    
    def test_strategiia_checkout_with_analyse_premium(self):
        """Test POST /api/strategiia/checkout accepts analyse_premium flag"""
        # Base price: 29€
        # With analyse_premium (+29€): 58€
        payload = {
            "origin_url": "https://engage-suite-3.preview.emergentagent.com",
            "email": "test-strategiia@example.com",
            "context": "Test case for analyse premium",
            "premium_pdf": False,
            "analyse_premium": True  # +29€
        }
        
        response = requests.post(f"{BASE_URL}/api/strategiia/checkout", json=payload)
        assert response.status_code == 200, f"Checkout failed: {response.text}"
        
        data = response.json()
        assert "url" in data, "No Stripe URL in response"
        print(f"TEST 7 PASSED: StrategiIA checkout with analyse_premium accepted")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
