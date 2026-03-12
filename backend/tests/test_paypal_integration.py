"""
Test PayPal Integration - Phase 9 Testing
Tests the PayPal payment endpoints: /api/paypal/calculate and /api/paypal/record
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPayPalCalculate:
    """Tests for POST /api/paypal/calculate endpoint - calculates discounts"""
    
    def test_calculate_basic_package(self):
        """Test calculate endpoint returns correct amount for a basic package"""
        response = requests.post(f"{BASE_URL}/api/paypal/calculate", json={
            "package_id": "analyse_dossier"
        })
        assert response.status_code == 200
        data = response.json()
        assert "final_amount" in data
        assert "base_amount" in data
        assert "package_name" in data
        assert data["base_amount"] == 150.0
        assert data["final_amount"] == 150.0
        assert data["discount_percent"] == 0
        print(f"PASS: Basic package calculation works - {data}")

    def test_calculate_invalid_package(self):
        """Test calculate endpoint returns 400 for invalid package"""
        response = requests.post(f"{BASE_URL}/api/paypal/calculate", json={
            "package_id": "invalid_package_xyz"
        })
        assert response.status_code == 400
        print("PASS: Invalid package returns 400")

    def test_calculate_preparation_expertise(self):
        """Test calculation for preparation_expertise package (250 EUR)"""
        response = requests.post(f"{BASE_URL}/api/paypal/calculate", json={
            "package_id": "preparation_expertise"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["base_amount"] == 250.0
        assert data["final_amount"] == 250.0
        assert data["package_name"] == "Préparation expertise médicale"
        print(f"PASS: preparation_expertise calculation works - {data}")

    def test_calculate_urgent_package(self):
        """Test calculation for urgent package"""
        response = requests.post(f"{BASE_URL}/api/paypal/calculate", json={
            "package_id": "urgent_analyse_dossier"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["base_amount"] == 250.0
        assert data["final_amount"] == 250.0
        print(f"PASS: Urgent package calculation works - {data}")

    def test_calculate_with_referral_code(self):
        """Test calculate endpoint applies 10% referral discount for valid codes"""
        # First create a test referral code
        unique_email = f"TEST_paypal_{uuid.uuid4().hex[:8]}@test.com"
        create_response = requests.post(f"{BASE_URL}/api/referral/create", json={
            "email": unique_email,
            "name": "Test Referrer"
        })
        assert create_response.status_code == 200
        referral_code = create_response.json()["code"]
        
        # Now test calculation with referral code
        response = requests.post(f"{BASE_URL}/api/paypal/calculate", json={
            "package_id": "analyse_dossier",
            "customer_email": "newcustomer@test.com",
            "referral_code": referral_code
        })
        assert response.status_code == 200
        data = response.json()
        assert data["discount_percent"] == 10
        assert data["discount_type"] == "parrainage"
        # 150 * 0.90 = 135
        assert data["final_amount"] == 135.0
        print(f"PASS: Referral code discount applied - {data}")


class TestPayPalRecord:
    """Tests for POST /api/paypal/record endpoint - records completed payments"""
    
    def test_record_payment(self):
        """Test recording a PayPal payment"""
        unique_email = f"TEST_paypal_record_{uuid.uuid4().hex[:8]}@test.com"
        order_id = f"TEST_ORDER_{uuid.uuid4().hex[:12]}"
        
        response = requests.post(f"{BASE_URL}/api/paypal/record", json={
            "order_id": order_id,
            "package_id": "analyse_dossier",
            "customer_email": unique_email,
            "customer_name": "Test PayPal Customer",
            "amount": 150.0
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["order_id"] == order_id
        print(f"PASS: PayPal payment recorded - {data}")

    def test_record_payment_increments_client_history(self):
        """Test that recording payment increments client_history orders_count"""
        unique_email = f"TEST_paypal_loyalty_{uuid.uuid4().hex[:8]}@test.com"
        
        # Check initial discount (should be 0 for new customer)
        discount_response = requests.get(f"{BASE_URL}/api/client/discount/{unique_email}")
        assert discount_response.status_code == 200
        initial_discount = discount_response.json()
        assert initial_discount["loyalty_discount"] == 0
        
        # Record first payment
        order_id_1 = f"TEST_ORDER_{uuid.uuid4().hex[:12]}"
        response = requests.post(f"{BASE_URL}/api/paypal/record", json={
            "order_id": order_id_1,
            "package_id": "analyse_dossier",
            "customer_email": unique_email,
            "customer_name": "Test Loyalty Customer",
            "amount": 150.0
        })
        assert response.status_code == 200
        
        # Check discount again (should now be 15% for returning customer)
        discount_response2 = requests.get(f"{BASE_URL}/api/client/discount/{unique_email}")
        assert discount_response2.status_code == 200
        updated_discount = discount_response2.json()
        assert updated_discount["loyalty_discount"] == 15
        assert updated_discount["orders_count"] == 1
        print(f"PASS: Client history incremented after PayPal payment - {updated_discount}")

    def test_record_payment_with_referral(self):
        """Test recording payment with referral code"""
        # Create referral code
        referrer_email = f"TEST_referrer_{uuid.uuid4().hex[:8]}@test.com"
        create_response = requests.post(f"{BASE_URL}/api/referral/create", json={
            "email": referrer_email,
            "name": "Test Referrer"
        })
        assert create_response.status_code == 200
        referral_code = create_response.json()["code"]
        
        # Record payment with referral
        unique_email = f"TEST_referred_{uuid.uuid4().hex[:8]}@test.com"
        order_id = f"TEST_ORDER_{uuid.uuid4().hex[:12]}"
        
        response = requests.post(f"{BASE_URL}/api/paypal/record", json={
            "order_id": order_id,
            "package_id": "analyse_dossier",
            "customer_email": unique_email,
            "customer_name": "Test Referred Customer",
            "amount": 135.0,
            "referral_code": referral_code
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"PASS: PayPal payment with referral recorded - {data}")


class TestPayPalLoyaltyDiscount:
    """Tests for loyalty discount (15%) applied to returning customers"""
    
    def test_loyalty_discount_applied_in_calculate(self):
        """Test that 15% loyalty discount is applied for returning customers in calculate"""
        # Create a returning customer with order history
        unique_email = f"TEST_returning_{uuid.uuid4().hex[:8]}@test.com"
        
        # Record first order to make them a returning customer
        order_id = f"TEST_ORDER_{uuid.uuid4().hex[:12]}"
        requests.post(f"{BASE_URL}/api/paypal/record", json={
            "order_id": order_id,
            "package_id": "analyse_dossier",
            "customer_email": unique_email,
            "customer_name": "Returning Customer",
            "amount": 150.0
        })
        
        # Now calculate for second order - should get 15% loyalty discount
        response = requests.post(f"{BASE_URL}/api/paypal/calculate", json={
            "package_id": "preparation_expertise",
            "customer_email": unique_email
        })
        assert response.status_code == 200
        data = response.json()
        assert data["discount_percent"] == 15
        assert data["discount_type"] == "fidélité"
        # 250 * 0.85 = 212.50
        assert data["final_amount"] == 212.5
        print(f"PASS: Loyalty discount applied for returning customer - {data}")


class TestAllPackagesCalculation:
    """Tests to verify all package prices are correctly calculated"""
    
    def test_all_standard_packages(self):
        """Test calculation for all standard packages"""
        packages = {
            "analyse_dossier": 150.0,
            "preparation_expertise": 250.0,
            "accompagnement_mdph": 200.0,
            "protection_juridique": 200.0,
            "accompagnement_complet": 500.0
        }
        
        for pkg_id, expected_amount in packages.items():
            response = requests.post(f"{BASE_URL}/api/paypal/calculate", json={
                "package_id": pkg_id
            })
            assert response.status_code == 200, f"Failed for {pkg_id}"
            data = response.json()
            assert data["base_amount"] == expected_amount, f"Wrong amount for {pkg_id}"
            print(f"PASS: {pkg_id} = {expected_amount} EUR")
        
        print("PASS: All standard package calculations correct")

    def test_all_urgent_packages(self):
        """Test calculation for all urgent packages"""
        packages = {
            "urgent_analyse_dossier": 250.0,
            "urgent_preparation_expertise": 400.0,
            "urgent_accompagnement_mdph": 320.0,
            "urgent_accompagnement_complet": 750.0
        }
        
        for pkg_id, expected_amount in packages.items():
            response = requests.post(f"{BASE_URL}/api/paypal/calculate", json={
                "package_id": pkg_id
            })
            assert response.status_code == 200, f"Failed for {pkg_id}"
            data = response.json()
            assert data["base_amount"] == expected_amount, f"Wrong amount for {pkg_id}"
            print(f"PASS: {pkg_id} = {expected_amount} EUR")
        
        print("PASS: All urgent package calculations correct")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
