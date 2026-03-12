"""
Phase 6 Feature Tests: Pass Urgent Section + Admin Parrainage Dashboard
- Tests urgent payment packages (4 new packages: 250€, 400€, 320€, 750€)
- Tests admin referral dashboard endpoint /api/admin/referrals
"""

import pytest
import requests
import os
import random
import string

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Urgent packages configuration
URGENT_PACKAGES = {
    "urgent_analyse_dossier": {"name": "Analyse de dossier URGENT 48h", "amount": 250.0},
    "urgent_preparation_expertise": {"name": "Préparation expertise URGENT 48h", "amount": 400.0},
    "urgent_accompagnement_mdph": {"name": "Accompagnement MDPH URGENT 48h", "amount": 320.0},
    "urgent_accompagnement_complet": {"name": "Accompagnement complet URGENT 48h", "amount": 750.0},
}

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@accompagn-sante.fr",
        "password": "Admin2024!"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed - skipping admin tests")

@pytest.fixture(scope="module")
def admin_client(api_client, admin_token):
    """Session with admin auth header"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


class TestHealthAndPackages:
    """Basic health and package validation tests"""
    
    def test_health_check(self, api_client):
        """Test API health endpoint"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")

    def test_all_packages_registered(self, api_client):
        """Test all 9 packages (5 standard + 4 urgent) are registered"""
        response = api_client.get(f"{BASE_URL}/api/payments/packages")
        assert response.status_code == 200
        packages = response.json()
        assert len(packages) == 9, f"Expected 9 packages, got {len(packages)}"
        
        package_ids = [p["id"] for p in packages]
        
        # Verify standard packages
        standard_ids = ["analyse_dossier", "preparation_expertise", "accompagnement_mdph", 
                       "protection_juridique", "accompagnement_complet"]
        for std_id in standard_ids:
            assert std_id in package_ids, f"Missing standard package: {std_id}"
        
        # Verify urgent packages
        for urgent_id in URGENT_PACKAGES.keys():
            assert urgent_id in package_ids, f"Missing urgent package: {urgent_id}"
        
        print(f"✓ All 9 packages registered: {package_ids}")


class TestUrgentPackages:
    """Tests for urgent payment packages"""

    def test_urgent_analyse_dossier_registered(self, api_client):
        """Test urgent_analyse_dossier package (250€)"""
        response = api_client.get(f"{BASE_URL}/api/payments/packages")
        packages = {p["id"]: p for p in response.json()}
        
        pkg = packages.get("urgent_analyse_dossier")
        assert pkg is not None, "urgent_analyse_dossier not found"
        assert pkg["amount"] == 250.0, f"Expected 250€, got {pkg['amount']}€"
        assert "URGENT" in pkg["name"], "Package name should contain URGENT"
        print("✓ urgent_analyse_dossier: 250€")

    def test_urgent_preparation_expertise_registered(self, api_client):
        """Test urgent_preparation_expertise package (400€)"""
        response = api_client.get(f"{BASE_URL}/api/payments/packages")
        packages = {p["id"]: p for p in response.json()}
        
        pkg = packages.get("urgent_preparation_expertise")
        assert pkg is not None, "urgent_preparation_expertise not found"
        assert pkg["amount"] == 400.0, f"Expected 400€, got {pkg['amount']}€"
        print("✓ urgent_preparation_expertise: 400€")

    def test_urgent_accompagnement_mdph_registered(self, api_client):
        """Test urgent_accompagnement_mdph package (320€)"""
        response = api_client.get(f"{BASE_URL}/api/payments/packages")
        packages = {p["id"]: p for p in response.json()}
        
        pkg = packages.get("urgent_accompagnement_mdph")
        assert pkg is not None, "urgent_accompagnement_mdph not found"
        assert pkg["amount"] == 320.0, f"Expected 320€, got {pkg['amount']}€"
        print("✓ urgent_accompagnement_mdph: 320€")

    def test_urgent_accompagnement_complet_registered(self, api_client):
        """Test urgent_accompagnement_complet package (750€)"""
        response = api_client.get(f"{BASE_URL}/api/payments/packages")
        packages = {p["id"]: p for p in response.json()}
        
        pkg = packages.get("urgent_accompagnement_complet")
        assert pkg is not None, "urgent_accompagnement_complet not found"
        assert pkg["amount"] == 750.0, f"Expected 750€, got {pkg['amount']}€"
        print("✓ urgent_accompagnement_complet: 750€")


class TestUrgentCheckout:
    """Tests for urgent package checkout flow"""

    def test_checkout_urgent_analyse_250(self, api_client):
        """Test checkout with urgent_analyse_dossier (250€)"""
        response = api_client.post(f"{BASE_URL}/api/payments/checkout", json={
            "package_id": "urgent_analyse_dossier",
            "origin_url": "https://test.com",
            "customer_email": f"TEST_urgent_checkout_{random.randint(1000,9999)}@test.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["final_amount"] == 250.0
        assert data["url"].startswith("https://checkout.stripe.com")
        print("✓ Checkout urgent_analyse_dossier: 250€")

    def test_checkout_urgent_preparation_400(self, api_client):
        """Test checkout with urgent_preparation_expertise (400€)"""
        response = api_client.post(f"{BASE_URL}/api/payments/checkout", json={
            "package_id": "urgent_preparation_expertise",
            "origin_url": "https://test.com",
            "customer_email": f"TEST_urgent_prep_{random.randint(1000,9999)}@test.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["final_amount"] == 400.0
        print("✓ Checkout urgent_preparation_expertise: 400€")

    def test_checkout_urgent_mdph_320(self, api_client):
        """Test checkout with urgent_accompagnement_mdph (320€)"""
        response = api_client.post(f"{BASE_URL}/api/payments/checkout", json={
            "package_id": "urgent_accompagnement_mdph",
            "origin_url": "https://test.com",
            "customer_email": f"TEST_urgent_mdph_{random.randint(1000,9999)}@test.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["final_amount"] == 320.0
        print("✓ Checkout urgent_accompagnement_mdph: 320€")

    def test_checkout_urgent_complet_750(self, api_client):
        """Test checkout with urgent_accompagnement_complet (750€)"""
        response = api_client.post(f"{BASE_URL}/api/payments/checkout", json={
            "package_id": "urgent_accompagnement_complet",
            "origin_url": "https://test.com",
            "customer_email": f"TEST_urgent_complet_{random.randint(1000,9999)}@test.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["final_amount"] == 750.0
        print("✓ Checkout urgent_accompagnement_complet: 750€")


class TestAdminReferralsDashboard:
    """Tests for admin referral stats endpoint"""

    def test_admin_referrals_requires_auth(self, api_client):
        """Test that /api/admin/referrals requires authentication"""
        # Remove auth header for this test
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/admin/referrals", headers=headers)
        assert response.status_code == 403 or response.status_code == 401
        print("✓ Admin referrals endpoint requires authentication")

    def test_admin_referrals_returns_data(self, admin_client):
        """Test admin referrals endpoint returns expected structure"""
        response = admin_client.get(f"{BASE_URL}/api/admin/referrals")
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "codes" in data, "Response should contain 'codes'"
        assert "recent_uses" in data, "Response should contain 'recent_uses'"
        assert "stats" in data, "Response should contain 'stats'"
        
        print(f"✓ Admin referrals endpoint returns expected structure")

    def test_admin_referrals_stats_fields(self, admin_client):
        """Test admin referrals stats contains required fields"""
        response = admin_client.get(f"{BASE_URL}/api/admin/referrals")
        data = response.json()
        stats = data["stats"]
        
        required_fields = ["total_codes", "active_codes", "total_uses", "total_discount_given"]
        for field in required_fields:
            assert field in stats, f"Stats should contain '{field}'"
        
        print(f"✓ Stats fields: total_codes={stats['total_codes']}, active_codes={stats['active_codes']}, total_uses={stats['total_uses']}, total_discount_given={stats['total_discount_given']}")

    def test_admin_referrals_codes_list(self, admin_client):
        """Test admin referrals codes list structure"""
        response = admin_client.get(f"{BASE_URL}/api/admin/referrals")
        data = response.json()
        
        if len(data["codes"]) > 0:
            code = data["codes"][0]
            required_fields = ["code", "owner_email", "uses_count", "is_active", "created_at"]
            for field in required_fields:
                assert field in code, f"Code item should contain '{field}'"
            print(f"✓ Codes list structure validated ({len(data['codes'])} codes)")
        else:
            print("⚠ No referral codes in database to validate structure")

    def test_admin_referrals_recent_uses_list(self, admin_client):
        """Test admin referrals recent_uses list structure"""
        response = admin_client.get(f"{BASE_URL}/api/admin/referrals")
        data = response.json()
        
        if len(data["recent_uses"]) > 0:
            use = data["recent_uses"][0]
            required_fields = ["referral_code", "referred_email", "discount_applied", "created_at"]
            for field in required_fields:
                assert field in use, f"Use item should contain '{field}'"
            print(f"✓ Recent uses list structure validated ({len(data['recent_uses'])} uses)")
        else:
            print("⚠ No recent uses in database to validate structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
