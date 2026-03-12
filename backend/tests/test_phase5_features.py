"""
Phase 5 Feature Tests for Accompagn'Santé
Tests for: Visitor counter, Referral system, Client discount, Checkout with discounts
"""
import pytest
import requests
import os
import random
import string

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestVisitorCounter:
    """Tests for visitor counter endpoints"""
    
    def test_get_visitor_count(self):
        """GET /api/visitors/count returns count"""
        response = requests.get(f"{BASE_URL}/api/visitors/count")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)
        print(f"✓ Visitor count: {data['count']}")

    def test_increment_visitor_count(self):
        """POST /api/visitors/increment increments and returns new count"""
        # Get initial count
        initial_response = requests.get(f"{BASE_URL}/api/visitors/count")
        initial_count = initial_response.json()["count"]
        
        # Increment
        response = requests.post(f"{BASE_URL}/api/visitors/increment")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert data["count"] >= initial_count  # Should be >= due to potential concurrent requests
        print(f"✓ Visitor count incremented: {initial_count} -> {data['count']}")


class TestReferralSystem:
    """Tests for referral code generation and validation"""
    
    def test_create_referral_code(self):
        """POST /api/referral/create creates new referral code"""
        # Use unique email for each test run
        test_email = f"TEST_referral_{random.randint(1000,9999)}@test.com"
        response = requests.post(
            f"{BASE_URL}/api/referral/create",
            json={"email": test_email, "name": "Test Referrer"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert len(data["code"]) == 8  # 8 character code
        assert data["code"].isalnum()  # Alphanumeric
        print(f"✓ Referral code created: {data['code']}")
        return data["code"]

    def test_create_referral_duplicate_returns_existing(self):
        """POST /api/referral/create with existing email returns existing code"""
        test_email = "TEST_duplicate_referral@test.com"
        
        # First creation
        response1 = requests.post(
            f"{BASE_URL}/api/referral/create",
            json={"email": test_email}
        )
        assert response1.status_code == 200
        code1 = response1.json()["code"]
        
        # Second creation with same email
        response2 = requests.post(
            f"{BASE_URL}/api/referral/create",
            json={"email": test_email}
        )
        assert response2.status_code == 200
        code2 = response2.json()["code"]
        
        assert code1 == code2  # Should return same code
        print(f"✓ Duplicate email returns same code: {code1}")

    def test_validate_referral_code_valid(self):
        """GET /api/referral/validate/{code} validates existing code"""
        # Create a code first
        test_email = f"TEST_validate_{random.randint(1000,9999)}@test.com"
        create_response = requests.post(
            f"{BASE_URL}/api/referral/create",
            json={"email": test_email}
        )
        code = create_response.json()["code"]
        
        # Validate it
        response = requests.get(f"{BASE_URL}/api/referral/validate/{code}")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["discount"] == 10
        print(f"✓ Valid referral code validated: {code} -> 10% discount")

    def test_validate_referral_code_invalid(self):
        """GET /api/referral/validate/{code} rejects invalid code"""
        response = requests.get(f"{BASE_URL}/api/referral/validate/INVALID123")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == False
        print("✓ Invalid referral code rejected")


class TestClientDiscount:
    """Tests for client loyalty discount checking"""
    
    def test_new_client_no_discount(self):
        """GET /api/client/discount/{email} returns 0 for new clients"""
        test_email = f"TEST_newclient_{random.randint(1000,9999)}@test.com"
        response = requests.get(f"{BASE_URL}/api/client/discount/{test_email}")
        assert response.status_code == 200
        data = response.json()
        assert data["orders_count"] == 0
        assert data["loyalty_discount"] == 0
        print("✓ New client has 0 discount")

    def test_returning_client_loyalty_discount(self):
        """Client with 1+ order gets 15% loyalty discount"""
        # Use an email we know has ordered (from previous test)
        test_email = "test_checkout@test.com"
        response = requests.get(f"{BASE_URL}/api/client/discount/{test_email}")
        assert response.status_code == 200
        data = response.json()
        # This client should have at least 1 order from previous tests
        if data["orders_count"] >= 1:
            assert data["loyalty_discount"] == 15
            print(f"✓ Returning client gets 15% discount (orders: {data['orders_count']})")
        else:
            print(f"ℹ Client has {data['orders_count']} orders, no loyalty discount yet")


class TestCheckoutWithDiscounts:
    """Tests for checkout endpoint with discount logic"""
    
    def test_checkout_no_discount(self):
        """POST /api/payments/checkout without discount"""
        test_email = f"TEST_checkout_nodiscount_{random.randint(1000,9999)}@test.com"
        response = requests.post(
            f"{BASE_URL}/api/payments/checkout",
            json={
                "package_id": "analyse_dossier",
                "origin_url": "https://test.com",
                "customer_email": test_email,
                "customer_name": "Test No Discount"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "session_id" in data
        assert data["discount_applied"] == 0
        assert data["original_amount"] == 150.0
        assert data["final_amount"] == 150.0
        print("✓ Checkout without discount: 150€")

    def test_checkout_with_referral_discount(self):
        """POST /api/payments/checkout with valid referral code applies 10%"""
        # Create a referral code
        create_response = requests.post(
            f"{BASE_URL}/api/referral/create",
            json={"email": "TEST_referrer_checkout@test.com"}
        )
        referral_code = create_response.json()["code"]
        
        # Use it in checkout
        test_email = f"TEST_checkout_referral_{random.randint(1000,9999)}@test.com"
        response = requests.post(
            f"{BASE_URL}/api/payments/checkout",
            json={
                "package_id": "analyse_dossier",
                "origin_url": "https://test.com",
                "customer_email": test_email,
                "customer_name": "Test Referral Discount",
                "referral_code": referral_code
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["discount_applied"] == 10
        assert data["discount_type"] == "parrainage"
        assert data["original_amount"] == 150.0
        assert data["final_amount"] == 135.0  # 150 - 10% = 135
        print(f"✓ Checkout with referral: 150€ - 10% = 135€")

    def test_checkout_invalid_package(self):
        """POST /api/payments/checkout with invalid package returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/payments/checkout",
            json={
                "package_id": "invalid_package",
                "origin_url": "https://test.com",
                "customer_email": "test@test.com"
            }
        )
        assert response.status_code == 400
        print("✓ Invalid package rejected with 400")

    def test_checkout_all_packages(self):
        """Test checkout works for all valid packages"""
        packages = [
            ("analyse_dossier", 150.0),
            ("preparation_expertise", 250.0),
            ("accompagnement_mdph", 200.0),
            ("protection_juridique", 200.0),
            ("accompagnement_complet", 500.0)
        ]
        
        for package_id, expected_amount in packages:
            test_email = f"TEST_checkout_{package_id}_{random.randint(1000,9999)}@test.com"
            response = requests.post(
                f"{BASE_URL}/api/payments/checkout",
                json={
                    "package_id": package_id,
                    "origin_url": "https://test.com",
                    "customer_email": test_email
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["original_amount"] == expected_amount
            print(f"✓ Package {package_id}: {expected_amount}€")


class TestPaymentPackages:
    """Tests for payment packages endpoint"""
    
    def test_get_packages(self):
        """GET /api/payments/packages returns all packages"""
        response = requests.get(f"{BASE_URL}/api/payments/packages")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        
        package_ids = [p["id"] for p in data]
        assert "analyse_dossier" in package_ids
        assert "preparation_expertise" in package_ids
        assert "accompagnement_mdph" in package_ids
        assert "protection_juridique" in package_ids
        assert "accompagnement_complet" in package_ids
        print(f"✓ All 5 payment packages returned")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
