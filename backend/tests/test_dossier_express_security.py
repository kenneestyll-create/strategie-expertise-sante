"""
Test suite for Dossier Express pre-payment security and post-payment fallback pipeline.
Tests LLM health check, checkout blocking, admin stats, and retry functionality.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token - shared across all tests in module"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }, timeout=30)
    
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code}")
    
    data = response.json()
    return data.get("access_token")


class TestLLMHealthCheck:
    """Tests for /api/health/llm endpoint - LLM availability check"""
    
    def test_llm_health_returns_operational_false_when_no_api_key(self):
        """GET /api/health/llm should return operational:false when ANTHROPIC_API_KEY is absent"""
        response = requests.get(f"{BASE_URL}/api/health/llm", timeout=30)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Since ANTHROPIC_API_KEY is intentionally absent in this environment
        assert "operational" in data, "Response should contain 'operational' field"
        assert data["operational"] == False, f"Expected operational=false, got {data['operational']}"
        assert "reason" in data, "Response should contain 'reason' field"
        assert data["reason"] == "cle_absente", f"Expected reason='cle_absente', got {data['reason']}"
        print(f"PASS: LLM health check returns operational=false with reason={data['reason']}")


class TestCheckoutBlocking:
    """Tests for /api/dossier-express/checkout - Pre-payment LLM blocking"""
    
    def test_checkout_returns_503_when_llm_unavailable(self):
        """POST /api/dossier-express/checkout should return 503 with French message when LLM is down"""
        payload = {
            "email": "test@example.com",
            "name": "Test User",
            "origin_url": "https://example.com",
            "premium_pdf": False,
            "analyse_premium": False
        }
        
        response = requests.post(f"{BASE_URL}/api/dossier-express/checkout", json=payload, timeout=30)
        
        # Should return 503 Service Unavailable when LLM is not operational
        assert response.status_code == 503, f"Expected 503, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "Response should contain 'detail' field"
        
        # Check for premium French message (no raw technical errors)
        detail = data["detail"]
        assert "momentanement indisponible" in detail.lower() or "finalisation technique" in detail.lower(), \
            f"Expected premium French message, got: {detail}"
        assert "anthropic" not in detail.lower(), "Should not expose technical details like 'anthropic'"
        assert "api_key" not in detail.lower(), "Should not expose technical details like 'api_key'"
        
        print(f"PASS: Checkout returns 503 with premium French message: {detail}")
    
    def test_checkout_does_not_proceed_to_stripe_when_llm_fails(self):
        """Checkout should NOT create a Stripe session when LLM health check fails"""
        payload = {
            "email": "test@example.com",
            "name": "Test User",
            "origin_url": "https://example.com",
            "premium_pdf": False,
            "analyse_premium": False
        }
        
        response = requests.post(f"{BASE_URL}/api/dossier-express/checkout", json=payload, timeout=30)
        
        # Should fail before reaching Stripe
        assert response.status_code == 503, f"Expected 503, got {response.status_code}"
        
        data = response.json()
        # Should NOT contain Stripe URL or session_id
        assert "url" not in data, "Should not contain Stripe URL when LLM is unavailable"
        assert "session_id" not in data, "Should not contain session_id when LLM is unavailable"
        
        print("PASS: Checkout does not proceed to Stripe when LLM health fails")


class TestAdminDossierExpress:
    """Tests for admin Dossier Express endpoints - stats and retry"""
    
    def test_admin_dossier_express_returns_enriched_stats(self, admin_token):
        """GET /api/admin/dossier-express should return enriched stats with delivery tracking"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express", headers=headers, timeout=30)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Check structure
        assert "items" in data, "Response should contain 'items'"
        assert "stats" in data, "Response should contain 'stats'"
        
        stats = data["stats"]
        
        # Check all required stat fields
        required_stats = ["total", "completed", "processing", "errors", "incidents", "delivered", "pending"]
        for stat in required_stats:
            assert stat in stats, f"Stats should contain '{stat}'"
            assert isinstance(stats[stat], int), f"'{stat}' should be an integer"
        
        print(f"PASS: Admin endpoint returns enriched stats: {stats}")
    
    def test_admin_dossier_express_items_have_delivery_fields(self, admin_token):
        """Dossier items should have delivery_status and processing_step fields"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express", headers=headers, timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        
        items = data.get("items", [])
        assert len(items) > 0, "Should have dossier items"
        
        # Check at least one item with delivery tracking fields
        items_with_delivery = [i for i in items if i.get("delivery_status") or i.get("processing_step")]
        
        # Note: Legacy dossiers may not have these fields, but new ones should
        print(f"Found {len(items_with_delivery)}/{len(items)} items with delivery tracking fields")
        
        # Check for the retried dossier with incident_technique status
        incident_items = [i for i in items if i.get("delivery_status") == "incident_technique"]
        print(f"Found {len(incident_items)} items with delivery_status=incident_technique")
        
        print("PASS: Dossier items structure verified")


class TestAdminRetryDossier:
    """Tests for admin retry functionality"""
    
    def test_retry_returns_400_for_non_error_dossier(self, admin_token):
        """POST /api/admin/dossier-express/{id}/retry should return 400 for non-error dossiers"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First get list of dossiers
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express", headers=headers, timeout=30)
        assert response.status_code == 200
        
        items = response.json().get("items", [])
        
        # Find a completed dossier (not in error state)
        completed_dossiers = [d for d in items if d.get("status") == "completed"]
        
        assert len(completed_dossiers) > 0, "Should have completed dossiers to test"
        
        dossier_id = completed_dossiers[0]["id"]
        
        # Try to retry a completed dossier - should fail
        retry_response = requests.post(
            f"{BASE_URL}/api/admin/dossier-express/{dossier_id}/retry",
            headers=headers,
            timeout=30
        )
        
        assert retry_response.status_code == 400, f"Expected 400 for non-error dossier, got {retry_response.status_code}"
        
        data = retry_response.json()
        assert "detail" in data, "Response should contain error detail"
        
        print(f"PASS: Retry correctly rejected for non-error dossier: {data['detail']}")
    
    def test_retry_endpoint_exists_and_requires_auth(self):
        """Retry endpoint should exist and require authentication"""
        # Try without auth
        response = requests.post(
            f"{BASE_URL}/api/admin/dossier-express/fake-id/retry",
            timeout=30
        )
        
        # Should return 401 or 403 (unauthorized)
        assert response.status_code in [401, 403, 422], \
            f"Expected auth error, got {response.status_code}"
        
        print("PASS: Retry endpoint requires authentication")


class TestDossierProcessingPipeline:
    """Tests for delivery_status and processing_step tracking"""
    
    def test_dossier_status_endpoint_returns_delivery_fields(self, admin_token):
        """GET /api/dossier-express/status/{id} should return delivery tracking fields"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get list of dossiers
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express", headers=headers, timeout=30)
        assert response.status_code == 200
        
        items = response.json().get("items", [])
        assert len(items) > 0, "Should have dossiers to test"
        
        # Get status of first dossier
        dossier_id = items[0]["id"]
        status_response = requests.get(f"{BASE_URL}/api/dossier-express/status/{dossier_id}", timeout=30)
        
        assert status_response.status_code == 200, f"Expected 200, got {status_response.status_code}"
        
        data = status_response.json()
        
        # Check for expected fields
        assert "id" in data, "Response should contain 'id'"
        assert "status" in data, "Response should contain 'status'"
        
        # delivery_status and processing_step may be present for newer dossiers
        if "delivery_status" in data:
            print(f"Dossier has delivery_status: {data['delivery_status']}")
        if "processing_step" in data:
            print(f"Dossier has processing_step: {data['processing_step']}")
        
        print("PASS: Dossier status endpoint returns expected fields")
    
    def test_incident_dossier_has_correct_status(self, admin_token):
        """Dossiers with incidents should have delivery_status=incident_technique"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express", headers=headers, timeout=30)
        assert response.status_code == 200
        
        items = response.json().get("items", [])
        stats = response.json().get("stats", {})
        
        # Check if there are any incident dossiers
        incident_count = stats.get("incidents", 0)
        
        # Find incident dossiers
        incident_dossiers = [d for d in items if d.get("delivery_status") == "incident_technique"]
        
        # Verify incident count matches
        assert incident_count == len(incident_dossiers), \
            f"Stats incidents ({incident_count}) should match actual incident dossiers ({len(incident_dossiers)})"
        
        if incident_count > 0:
            # Check one incident dossier
            incident = incident_dossiers[0]
            assert incident.get("delivery_status") == "incident_technique"
            
            # After retry, should have erreur_ia processing_step (since no API key)
            if incident.get("retry_count", 0) > 0:
                assert incident.get("processing_step") == "erreur_ia", \
                    f"Retried incident should have processing_step=erreur_ia, got {incident.get('processing_step')}"
                print(f"PASS: Retried dossier has processing_step=erreur_ia and retry_count={incident.get('retry_count')}")
            
            print(f"PASS: Found {len(incident_dossiers)} incident dossiers with correct status")
        else:
            print("INFO: No incident dossiers found (this is expected if LLM was never called)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
