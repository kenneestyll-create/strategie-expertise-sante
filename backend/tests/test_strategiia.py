"""
StrategiIA Feature Tests
- POST /api/strategiia/analyze: Free AI analysis
- POST /api/strategiia/checkout: Stripe checkout for premium
- Admin CRUD for cas_anonymises
- Admin stats endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"

@pytest.fixture(scope="module")
def admin_token():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin authentication failed: {response.status_code} - {response.text}")

@pytest.fixture
def admin_headers(admin_token):
    """Headers with admin auth"""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


class TestStrategiiaAnalyze:
    """POST /api/strategiia/analyze tests"""
    
    def test_analyze_basic_success(self):
        """Test free (basic) analysis with valid inputs"""
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json={
            "type_dossier": "at",
            "regime": "general",
            "situation": "J'ai eu un accident du travail et je cherche à comprendre mes droits.",
            "premium": False,
            "email": "test@example.com"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "analysis" in data, "Response should contain 'analysis' field"
        assert isinstance(data["analysis"], str), "Analysis should be a string"
        assert len(data["analysis"]) > 50, "Analysis should have meaningful content"
        assert "cases_found" in data, "Response should contain 'cases_found' field"
        print(f"PASS: Basic analysis returned {len(data['analysis'])} chars, {data.get('cases_found', 0)} similar cases found")

    def test_analyze_missing_type_dossier(self):
        """Test analysis without type_dossier (should still work, but may be less targeted)"""
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json={
            "situation": "Je veux comprendre mes droits.",
            "premium": False
        })
        # Server may still process this - check response
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"
        print(f"Response status: {response.status_code}")

    def test_analyze_empty_situation(self):
        """Test analysis with empty situation"""
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json={
            "type_dossier": "mp",
            "situation": "",
            "premium": False
        })
        # May return error or minimal analysis
        print(f"Empty situation response: {response.status_code}")

    def test_analyze_premium_flag(self):
        """Test analysis with premium=True (more detailed response)"""
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json={
            "type_dossier": "mdph",
            "regime": "general",
            "situation": "Je souhaite faire une demande MDPH pour reconnaissance de handicap suite à une maladie chronique.",
            "premium": True,
            "email": "premium@test.com"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "analysis" in data
        # Premium analysis should be longer/more detailed
        print(f"PASS: Premium analysis returned {len(data.get('analysis', ''))} chars")


class TestStrategiiaCheckout:
    """POST /api/strategiia/checkout tests"""
    
    def test_checkout_creates_stripe_session(self):
        """Test that checkout returns a Stripe URL"""
        response = requests.post(f"{BASE_URL}/api/strategiia/checkout", json={
            "origin_url": "https://sante-aide.preview.emergentagent.com",
            "email": "buyer@test.com",
            "context": "AT - Accident du travail test"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data, "Response should contain Stripe checkout URL"
        assert data["url"].startswith("https://checkout.stripe.com"), f"URL should be Stripe checkout, got: {data['url'][:50]}"
        print(f"PASS: Checkout URL generated: {data['url'][:60]}...")

    def test_checkout_missing_origin_url(self):
        """Test checkout without origin_url"""
        response = requests.post(f"{BASE_URL}/api/strategiia/checkout", json={
            "email": "test@test.com"
        })
        # Should fail gracefully
        assert response.status_code in [400, 422, 500], f"Expected error, got {response.status_code}"
        print(f"Missing origin_url correctly returns error: {response.status_code}")


class TestAdminCasAnonymises:
    """Admin CRUD for cas_anonymises"""
    
    def test_get_cas_anonymises_list(self, admin_headers):
        """GET /api/admin/cas-anonymises returns list"""
        response = requests.get(f"{BASE_URL}/api/admin/cas-anonymises", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "items" in data, "Response should have 'items' key"
        assert "total" in data, "Response should have 'total' key"
        assert isinstance(data["items"], list), "items should be a list"
        print(f"PASS: Got {data['total']} anonymized cases")

    def test_create_cas_anonymise(self, admin_headers):
        """POST /api/admin/cas-anonymises creates new case"""
        test_case = {
            "type_dossier": "TEST_AT",
            "regime": "Général",
            "duree": "12 mois",
            "strategie": "Recours CPAM + expertise contradictoire",
            "resultat": "Favorable",
            "score_pertinence": 85,
            "notes": "Test case for StrategiIA testing"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/cas-anonymises", json=test_case, headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True or "id" in data, "Should return success or id"
        print(f"PASS: Created anonymized case")
        
        # Store case_id for cleanup/delete test
        if "id" in data:
            return data["id"]
        return None

    def test_create_and_delete_cas_anonymise(self, admin_headers):
        """Create then delete a case"""
        # Create
        test_case = {
            "type_dossier": "TEST_DELETE",
            "regime": "MSA",
            "duree": "6 mois",
            "strategie": "Test strategy",
            "resultat": "En cours",
            "score_pertinence": 50
        }
        
        create_resp = requests.post(f"{BASE_URL}/api/admin/cas-anonymises", json=test_case, headers=admin_headers)
        assert create_resp.status_code == 200
        
        # Get list to find our case
        list_resp = requests.get(f"{BASE_URL}/api/admin/cas-anonymises", headers=admin_headers)
        cases = list_resp.json().get("items", [])
        test_case_entry = next((c for c in cases if c.get("type_dossier") == "TEST_DELETE"), None)
        
        if test_case_entry:
            case_id = test_case_entry.get("id")
            # Delete
            delete_resp = requests.delete(f"{BASE_URL}/api/admin/cas-anonymises/{case_id}", headers=admin_headers)
            assert delete_resp.status_code == 200, f"Delete failed: {delete_resp.status_code}"
            print(f"PASS: Successfully created and deleted case {case_id}")
        else:
            print("Created case but couldn't find it to delete")


class TestAdminStrategiiaStats:
    """GET /api/admin/strategiia/stats"""
    
    def test_get_strategiia_stats(self, admin_headers):
        """Get StrategiIA statistics"""
        response = requests.get(f"{BASE_URL}/api/admin/strategiia/stats", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Check expected fields
        assert "total_analyses" in data, "Should have total_analyses"
        assert "premium" in data, "Should have premium count"
        assert "total_cases" in data, "Should have total_cases (cas anonymisés)"
        
        print(f"PASS: Stats - {data.get('total_analyses', 0)} analyses, {data.get('premium', 0)} premium, {data.get('total_cases', 0)} cases")


class TestStrategiiaUnauthorized:
    """Test admin endpoints without auth"""
    
    def test_cas_anonymises_requires_auth(self):
        """GET cas-anonymises without token should fail"""
        response = requests.get(f"{BASE_URL}/api/admin/cas-anonymises")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: cas-anonymises requires authentication")

    def test_strategiia_stats_requires_auth(self):
        """GET strategiia/stats without token should fail"""
        response = requests.get(f"{BASE_URL}/api/admin/strategiia/stats")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: strategiia/stats requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
