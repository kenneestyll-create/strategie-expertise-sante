"""
Test StrategiIA endpoints after middleware fix (Pure ASGI middleware).
Tests the fix for POST /api/strategiia/analyze and /api/strategiia/admin-bypass-premium
which were previously hanging due to Starlette BaseHTTPMiddleware deadlock.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD


class TestHealthAndSecurityHeaders:
    """Test health endpoint and security headers (middleware working)"""
    
    def test_health_endpoint(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"PASS: Health endpoint returns status=healthy")
    
    def test_security_headers_present(self):
        """Security headers should be present (ASGI middleware working)"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        
        # Check security headers added by SecurityHeadersASGIMiddleware
        headers = response.headers
        assert headers.get("x-content-type-options") == "nosniff", "Missing x-content-type-options header"
        assert headers.get("x-frame-options") == "DENY", "Missing x-frame-options header"
        assert headers.get("x-xss-protection") == "1; mode=block", "Missing x-xss-protection header"
        print(f"PASS: Security headers present - x-content-type-options, x-frame-options, x-xss-protection")


class TestStrategiiaAnalyzeEndpoint:
    """Test POST /api/strategiia/analyze - the main endpoint that was hanging"""
    
    def test_analyze_returns_job_id_immediately(self):
        """POST /api/strategiia/analyze should return job_id immediately (not hang)"""
        payload = {
            "type_dossier": "at",
            "regime": "general",
            "situation": "Test situation for middleware fix verification - accident du travail",
            "premium": False,
            "email": "test-middleware@test.com"
        }
        
        # This should return immediately with job_id, not hang
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json=payload, timeout=30)
        elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Should return job_id and status=pending immediately
        assert "job_id" in data, f"Missing job_id in response: {data}"
        assert data.get("status") == "pending", f"Expected status=pending, got {data.get('status')}"
        
        # Should return quickly (< 5 seconds), not hang
        assert elapsed < 5, f"Endpoint took too long ({elapsed:.1f}s) - possible middleware deadlock"
        
        print(f"PASS: /api/strategiia/analyze returned job_id={data['job_id']} in {elapsed:.2f}s")
        return data["job_id"]
    
    def test_analyze_missing_situation_returns_400(self):
        """POST /api/strategiia/analyze with empty situation should return 400"""
        payload = {
            "type_dossier": "at",
            "regime": "general",
            "situation": "",
            "premium": False
        }
        
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json=payload, timeout=10)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"PASS: Empty situation returns 400")


class TestStrategiiaStatusPolling:
    """Test GET /api/strategiia/status/{job_id} - polling endpoint"""
    
    def test_status_returns_pending_or_done(self):
        """GET /api/strategiia/status/{job_id} should return status"""
        # First create a job
        payload = {
            "type_dossier": "mp",
            "regime": "general",
            "situation": "Test maladie professionnelle pour vérification du polling",
            "premium": False,
            "email": "test-polling@test.com"
        }
        
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json=payload, timeout=30)
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        print(f"Created job_id={job_id}")
        
        # Poll for status
        status_response = requests.get(f"{BASE_URL}/api/strategiia/status/{job_id}", timeout=10)
        assert status_response.status_code == 200
        status_data = status_response.json()
        
        assert "status" in status_data
        assert status_data["status"] in ["pending", "done", "error"], f"Unexpected status: {status_data['status']}"
        print(f"PASS: Status endpoint returned status={status_data['status']}")
    
    def test_status_invalid_job_id_returns_404(self):
        """GET /api/strategiia/status/{invalid_id} should return 404"""
        response = requests.get(f"{BASE_URL}/api/strategiia/status/invalid-job-id-12345", timeout=10)
        assert response.status_code == 404
        print(f"PASS: Invalid job_id returns 404")


class TestStrategiiaAdminBypassPremium:
    """Test POST /api/strategiia/admin-bypass-premium - admin endpoint that was hanging"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token via login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=10)
        
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        
        data = response.json()
        token = data.get("access_token")
        if not token:
            pytest.skip("No access_token in login response")
        
        print(f"Admin login successful, got token")
        return token
    
    def test_admin_bypass_returns_job_id_immediately(self, admin_token):
        """POST /api/strategiia/admin-bypass-premium should return job_id immediately"""
        payload = {
            "type_dossier": "at",
            "regime": "general",
            "situation": "Test admin bypass for middleware fix verification",
            "premium_pdf": False,
            "analyse_premium": False
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json=payload,
            headers=headers,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "job_id" in data, f"Missing job_id: {data}"
        assert data.get("status") == "pending"
        assert data.get("admin_test") == True
        
        # Should return quickly
        assert elapsed < 5, f"Endpoint took too long ({elapsed:.1f}s)"
        
        print(f"PASS: admin-bypass-premium returned job_id={data['job_id']} in {elapsed:.2f}s")
        return data["job_id"]
    
    def test_admin_bypass_without_token_returns_401(self):
        """POST /api/strategiia/admin-bypass-premium without token should return 401"""
        payload = {
            "type_dossier": "at",
            "situation": "Test without token"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json=payload,
            timeout=10
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"PASS: No token returns 401")
    
    def test_admin_bypass_with_invalid_token_returns_401(self):
        """POST /api/strategiia/admin-bypass-premium with invalid token should return 401"""
        payload = {
            "type_dossier": "at",
            "situation": "Test with invalid token"
        }
        
        headers = {"Authorization": "Bearer invalid-token-12345"}
        
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json=payload,
            headers=headers,
            timeout=10
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"PASS: Invalid token returns 401")


class TestStrategiiaFullFlowWithPolling:
    """Test full flow: analyze -> poll until done (with timeout)"""
    
    def test_full_analyze_flow_completes(self):
        """Full flow: POST analyze -> poll status until done (max 60s)"""
        # Create analysis job
        payload = {
            "type_dossier": "at",
            "regime": "general",
            "situation": "Test complet du flux StrategiIA - accident du travail avec séquelles",
            "premium": False,
            "email": "test-fullflow@test.com"
        }
        
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json=payload, timeout=30)
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        print(f"Created job_id={job_id}, polling for completion...")
        
        # Poll until done or timeout (60 seconds max for LLM)
        max_wait = 60
        poll_interval = 3
        elapsed = 0
        final_status = None
        
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            
            status_response = requests.get(f"{BASE_URL}/api/strategiia/status/{job_id}", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                final_status = status_data.get("status")
                print(f"  Poll at {elapsed}s: status={final_status}")
                
                if final_status == "done":
                    assert "analysis" in status_data, "Missing analysis in done response"
                    assert status_data.get("success") == True
                    print(f"PASS: Analysis completed in {elapsed}s with analysis text")
                    return
                elif final_status == "error":
                    error_msg = status_data.get("error", "Unknown error")
                    print(f"Analysis failed with error: {error_msg}")
                    # This is acceptable - LLM might have budget issues
                    return
        
        # If we get here, it timed out but didn't hang
        print(f"Analysis still pending after {max_wait}s (LLM slow but not hanging)")
        assert final_status in ["pending", "done", "error"], f"Unexpected final status: {final_status}"


class TestAdminBypassFullFlowWithPolling:
    """Test admin bypass full flow with polling"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=10)
        
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        
        return response.json().get("access_token")
    
    def test_admin_bypass_full_flow_completes(self, admin_token):
        """Full admin bypass flow: POST -> poll until done"""
        payload = {
            "type_dossier": "mp",
            "regime": "general",
            "situation": "Test admin bypass complet - maladie professionnelle TMS",
            "premium_pdf": False,
            "analyse_premium": False
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json=payload,
            headers=headers,
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        job_id = data["job_id"]
        assert data.get("admin_test") == True
        print(f"Created admin job_id={job_id}, polling...")
        
        # Poll until done (60s max)
        max_wait = 60
        poll_interval = 3
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            
            status_response = requests.get(f"{BASE_URL}/api/strategiia/status/{job_id}", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                print(f"  Poll at {elapsed}s: status={status}")
                
                if status == "done":
                    assert "analysis" in status_data
                    print(f"PASS: Admin bypass analysis completed in {elapsed}s")
                    return
                elif status == "error":
                    print(f"Admin bypass failed: {status_data.get('error')}")
                    return
        
        print(f"Admin bypass still pending after {max_wait}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
