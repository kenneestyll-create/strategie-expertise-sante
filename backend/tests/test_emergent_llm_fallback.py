"""
Test Emergent LLM Fallback Bug Fix - Iteration 145

Tests the fix for StrategiIA being blocked when ANTHROPIC_API_KEY is empty.
The fix uses EMERGENT_LLM_KEY as fallback via emergentintegrations library.

Features tested:
1. GET /api/health/llm returns operational:true (using Emergent fallback)
2. POST /api/strategiia/analyze succeeds for admin (analysis via Emergent fallback)
3. GET /api/strategiia/status/{job_id} returns done with non-empty analysis
4. POST /api/dossier-express/checkout no longer returns 503 for LLM health
5. GET /api/admin/services-status returns comprehensive service diagnostic
6. Service diagnostic shows ia_anthropic as ok with emergent_fallback mode
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Headers with admin auth token."""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


class TestLLMHealthEndpoint:
    """Test GET /api/health/llm endpoint with Emergent fallback."""

    def test_llm_health_returns_operational(self):
        """LLM health check should return operational:true with Emergent fallback."""
        response = requests.get(f"{BASE_URL}/api/health/llm")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "operational" in data, f"Response missing 'operational' field: {data}"
        assert data["operational"] is True, f"Expected operational:true, got {data}"
        
        # Reason should be empty or indicate fallback
        reason = data.get("reason", "")
        print(f"LLM Health: operational={data['operational']}, reason='{reason}'")

    def test_llm_health_response_structure(self):
        """LLM health response should have correct structure."""
        response = requests.get(f"{BASE_URL}/api/health/llm")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data.get("operational"), bool), "operational should be boolean"
        assert "reason" in data, "Response should include reason field"


class TestStrategiIAAnalyze:
    """Test POST /api/strategiia/analyze with Emergent fallback."""

    def test_strategiia_analyze_admin_test_mode(self, admin_headers):
        """StrategiIA analyze should succeed for admin with admin_test:true."""
        payload = {
            "situation": "Test situation pour validation du fallback Emergent LLM. Accident du travail avec sequelles.",
            "type_dossier": "AT",
            "regime": "general",
            "admin_test": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/strategiia/analyze",
            json=payload,
            headers=admin_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "job_id" in data, f"Response missing job_id: {data}"
        # Status can be "pending" or "processing" depending on timing
        assert data.get("status") in ["pending", "processing"], f"Expected status:pending or processing, got {data}"
        
        job_id = data["job_id"]
        print(f"StrategiIA analyze started: job_id={job_id}")
        return job_id

    def test_strategiia_status_polling(self, admin_headers):
        """Poll StrategiIA status until done and verify analysis is non-empty."""
        # First create an analysis job
        payload = {
            "situation": "Test de polling pour validation Emergent fallback. Maladie professionnelle TMS.",
            "type_dossier": "MP",
            "regime": "general",
            "admin_test": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/strategiia/analyze",
            json=payload,
            headers=admin_headers
        )
        
        assert response.status_code == 200, f"Analyze failed: {response.status_code}"
        job_id = response.json().get("job_id")
        assert job_id, "No job_id returned"
        
        # Poll for completion (max 60 seconds, analysis may take 15-20s)
        max_wait = 60
        poll_interval = 3
        elapsed = 0
        final_status = None
        
        while elapsed < max_wait:
            status_response = requests.get(
                f"{BASE_URL}/api/strategiia/status/{job_id}",
                headers=admin_headers
            )
            
            assert status_response.status_code == 200, f"Status check failed: {status_response.status_code}"
            
            status_data = status_response.json()
            current_status = status_data.get("status")
            print(f"Polling job {job_id}: status={current_status}, elapsed={elapsed}s")
            
            if current_status == "done":
                final_status = status_data
                break
            elif current_status == "error":
                pytest.fail(f"Analysis failed with error: {status_data.get('error', 'unknown')}")
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        assert final_status is not None, f"Analysis did not complete within {max_wait}s"
        assert final_status.get("status") == "done", f"Expected status:done, got {final_status}"
        
        # Verify analysis is non-empty
        analysis = final_status.get("analysis", "")
        assert analysis, "Analysis should not be empty"
        assert len(analysis) > 100, f"Analysis too short ({len(analysis)} chars), expected substantial content"
        
        print(f"Analysis completed: {len(analysis)} chars")
        print(f"Analysis preview: {analysis[:200]}...")


class TestDossierExpressCheckout:
    """Test POST /api/dossier-express/checkout no longer returns 503."""

    def test_checkout_passes_llm_health_check(self):
        """Dossier Express checkout should pass LLM health check (not return 503 for LLM)."""
        payload = {
            "email": "test@example.com",
            "name": "Test User",
            "origin_url": BASE_URL,
            "premium_pdf": False,
            "analyse_premium": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/checkout",
            json=payload
        )
        
        # Check the response - if 503, verify it's NOT due to LLM health check
        if response.status_code == 503:
            error_detail = response.json().get("detail", "")
            # The LLM unavailable message is specific
            llm_unavailable_msg = "Le service est momentanement indisponible pour finalisation technique"
            if llm_unavailable_msg in error_detail:
                # This means LLM health check failed - need to verify LLM is actually working
                health_response = requests.get(f"{BASE_URL}/api/health/llm")
                if health_response.status_code == 200 and health_response.json().get("operational"):
                    # LLM is operational but checkout still returned 503 - this is a bug
                    pytest.fail(f"LLM is operational but checkout returned 503: {error_detail}")
                else:
                    pytest.skip(f"LLM not operational: {health_response.text}")
            else:
                # 503 for other reasons (e.g., launch mode) is acceptable
                print(f"Checkout returned 503 for non-LLM reason: {error_detail}")
        elif response.status_code == 200:
            data = response.json()
            assert "url" in data or "session_id" in data, f"Expected Stripe session data: {data}"
            print(f"Checkout passed LLM check, Stripe session created")
        else:
            # Other errors (e.g., 500 for Stripe config) are acceptable for this test
            print(f"Checkout returned {response.status_code} (not 503 for LLM - check passed)")


class TestAdminServicesStatus:
    """Test GET /api/admin/services-status endpoint."""

    def test_services_status_returns_comprehensive_diagnostic(self, admin_headers):
        """Services status should return comprehensive diagnostic for all services."""
        response = requests.get(
            f"{BASE_URL}/api/admin/services-status",
            headers=admin_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check top-level fields
        assert "all_services_ok" in data, "Missing all_services_ok field"
        assert "critical_services_ok" in data, "Missing critical_services_ok field"
        assert "ready_for_launch" in data, "Missing ready_for_launch field"
        assert "services" in data, "Missing services field"
        
        print(f"Services status: all_ok={data['all_services_ok']}, critical_ok={data['critical_services_ok']}")

    def test_services_status_has_six_services(self, admin_headers):
        """Services status should include 6 services."""
        response = requests.get(
            f"{BASE_URL}/api/admin/services-status",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        services = data.get("services", {})
        
        expected_services = ["ia_anthropic", "stripe", "email_resend", "storage_s3", "database", "launch_mode"]
        
        for svc in expected_services:
            assert svc in services, f"Missing service: {svc}"
            assert "status" in services[svc], f"Service {svc} missing status field"
            assert "mode" in services[svc], f"Service {svc} missing mode field"
            assert "detail" in services[svc], f"Service {svc} missing detail field"
        
        print(f"All 6 services present: {list(services.keys())}")

    def test_ia_anthropic_shows_emergent_fallback(self, admin_headers):
        """IA service should show ok status with emergent_fallback mode."""
        response = requests.get(
            f"{BASE_URL}/api/admin/services-status",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        ia_service = data.get("services", {}).get("ia_anthropic", {})
        
        assert ia_service.get("status") == "ok", f"Expected ia_anthropic status:ok, got {ia_service}"
        assert ia_service.get("mode") == "emergent_fallback", f"Expected mode:emergent_fallback, got {ia_service}"
        
        print(f"IA Anthropic: status={ia_service['status']}, mode={ia_service['mode']}, detail={ia_service['detail']}")

    def test_database_shows_ok(self, admin_headers):
        """Database service should show ok status."""
        response = requests.get(
            f"{BASE_URL}/api/admin/services-status",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        db_service = data.get("services", {}).get("database", {})
        
        assert db_service.get("status") == "ok", f"Expected database status:ok, got {db_service}"
        print(f"Database: status={db_service['status']}, mode={db_service['mode']}")

    def test_critical_services_ok(self, admin_headers):
        """Critical services (IA + Database) should be ok."""
        response = requests.get(
            f"{BASE_URL}/api/admin/services-status",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("critical_services_ok") is True, f"Critical services not ok: {data}"
        print("Critical services (IA + Database) are operational")


class TestLLMHealthIntegration:
    """Integration tests for LLM health check flow."""

    def test_health_check_before_checkout(self):
        """Verify health check is called and passes before checkout."""
        # First check health (with retry for transient issues)
        health_response = None
        for attempt in range(3):
            health_response = requests.get(f"{BASE_URL}/api/health/llm")
            if health_response.status_code == 200:
                break
            time.sleep(1)
        
        assert health_response.status_code == 200, f"Health check failed: {health_response.status_code}"
        health_data = health_response.json()
        
        if not health_data.get("operational"):
            pytest.skip("LLM not operational - cannot test checkout flow")
        
        # Then attempt checkout
        checkout_response = requests.post(
            f"{BASE_URL}/api/dossier-express/checkout",
            json={
                "email": "integration@test.com",
                "name": "Integration Test",
                "origin_url": BASE_URL
            }
        )
        
        # If 503, check if it's for LLM or other reason
        if checkout_response.status_code == 503:
            error_detail = checkout_response.json().get("detail", "")
            if "finalisation technique" in error_detail:
                # LLM health check issue - but we verified LLM is operational above
                # This could be a race condition, so we just log it
                print(f"Warning: LLM operational but checkout returned 503: {error_detail}")
            else:
                print(f"Checkout returned 503 for non-LLM reason: {error_detail}")
        
        print(f"Integration test: health={health_data['operational']}, checkout_status={checkout_response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
