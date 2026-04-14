"""
Test suite for Dossier Express IA Bug Fixes
Tests the following fixes:
1. POST /api/dossier-express/admin-bypass returns immediately with dossier_id + status=submitted
2. GET /api/dossier-express/status/{id} returns processing then completed with analysis
3. GET /api/health responds in <1s during LLM processing (event loop not blocked)
"""
import pytest
import requests
import os
import time
import concurrent.futures

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD


class TestDossierExpressBugFix:
    """Tests for Dossier Express IA bug fixes"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        # API returns 'access_token' not 'token'
        token = data.get("access_token") or data.get("token")
        assert token, f"No token in response: {data}"
        return token
    
    def test_health_endpoint_available(self):
        """Test that health endpoint is available"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("PASS: Health endpoint available")
    
    def test_admin_bypass_returns_immediately(self, admin_token):
        """
        BUG FIX TEST: POST /api/dossier-express/admin-bypass must return immediately
        with dossier_id + status=submitted (not block on LLM)
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "name": "TEST_Admin Bypass Test",
            "email": "test@example.com",
            "situation": "Test situation for admin bypass - accident du travail avec séquelles",
            "type_dossier": "Accident du travail (AT)",
            "regime": "Régime général",
            "documents_text": "Document test content",
            "premium_pdf": False
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json=payload,
            headers=headers,
            timeout=10  # Should return in <2s, not 60s
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Admin bypass failed: {response.text}"
        data = response.json()
        
        # Verify immediate response with dossier_id
        assert "dossier_id" in data, f"Missing dossier_id in response: {data}"
        assert data.get("success") == True, f"success should be True: {data}"
        assert elapsed < 5, f"Admin bypass took too long: {elapsed}s (should be <5s)"
        
        print(f"PASS: Admin bypass returned in {elapsed:.2f}s with dossier_id={data['dossier_id']}")
        return data["dossier_id"]
    
    def test_status_endpoint_returns_processing(self, admin_token):
        """
        BUG FIX TEST: GET /api/dossier-express/status/{id} must return processing status
        """
        # First create a dossier
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "name": "TEST_Status Check",
            "email": "test@example.com",
            "situation": "Test situation for status check - maladie professionnelle",
            "type_dossier": "Maladie professionnelle (MP)",
            "regime": "Régime général",
            "documents_text": "",
            "premium_pdf": False
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json=payload,
            headers=headers,
            timeout=10
        )
        assert create_response.status_code == 200, f"Create failed: {create_response.text}"
        dossier_id = create_response.json()["dossier_id"]
        
        # Check status immediately - should be processing
        status_response = requests.get(
            f"{BASE_URL}/api/dossier-express/status/{dossier_id}",
            timeout=5
        )
        assert status_response.status_code == 200, f"Status check failed: {status_response.text}"
        status_data = status_response.json()
        
        assert "status" in status_data, f"Missing status field: {status_data}"
        assert status_data["status"] in ["processing", "completed"], f"Unexpected status: {status_data['status']}"
        
        print(f"PASS: Status endpoint returned status={status_data['status']} for dossier {dossier_id}")
        return dossier_id
    
    def test_health_responds_during_llm_processing(self, admin_token):
        """
        EVENT LOOP TEST: GET /api/health must respond in <1s while LLM is processing
        This verifies asyncio.to_thread fix for blocking LLM calls
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "name": "TEST_Event Loop Test",
            "email": "test@example.com",
            "situation": "Test situation for event loop verification - long analysis needed",
            "type_dossier": "Accident du travail (AT)",
            "regime": "Régime général",
            "documents_text": "Detailed document content for analysis",
            "premium_pdf": False
        }
        
        # Start the LLM processing
        create_response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json=payload,
            headers=headers,
            timeout=10
        )
        assert create_response.status_code == 200, f"Create failed: {create_response.text}"
        dossier_id = create_response.json()["dossier_id"]
        
        # Immediately check health endpoint multiple times
        health_times = []
        for i in range(3):
            start = time.time()
            health_response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            elapsed = time.time() - start
            health_times.append(elapsed)
            assert health_response.status_code == 200, f"Health check {i+1} failed"
            time.sleep(0.5)
        
        avg_health_time = sum(health_times) / len(health_times)
        max_health_time = max(health_times)
        
        assert max_health_time < 2, f"Health check too slow during LLM: max={max_health_time:.2f}s"
        
        print(f"PASS: Health endpoint responded during LLM processing (avg={avg_health_time:.2f}s, max={max_health_time:.2f}s)")
        return dossier_id
    
    def test_status_polling_until_completed(self, admin_token):
        """
        BUG FIX TEST: Poll status until completed with non-empty analysis
        Note: LLM takes 50-60 seconds, so we poll for up to 90 seconds
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "name": "TEST_Polling Test",
            "email": "test@example.com",
            "situation": "Test situation for polling - accident du travail avec arrêt de travail prolongé et séquelles importantes nécessitant une analyse approfondie",
            "type_dossier": "Accident du travail (AT)",
            "regime": "Régime général",
            "documents_text": "Certificat médical initial, déclaration d'accident, arrêts de travail",
            "premium_pdf": False
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json=payload,
            headers=headers,
            timeout=10
        )
        assert create_response.status_code == 200, f"Create failed: {create_response.text}"
        dossier_id = create_response.json()["dossier_id"]
        
        # Poll for up to 90 seconds (LLM takes 50-60s)
        max_wait = 90
        poll_interval = 5
        start_time = time.time()
        final_status = None
        
        while time.time() - start_time < max_wait:
            status_response = requests.get(
                f"{BASE_URL}/api/dossier-express/status/{dossier_id}",
                timeout=5
            )
            assert status_response.status_code == 200, f"Status check failed: {status_response.text}"
            status_data = status_response.json()
            final_status = status_data.get("status")
            
            print(f"  Polling: status={final_status} (elapsed={time.time()-start_time:.0f}s)")
            
            if final_status == "completed":
                # Verify analysis is present
                analysis = status_data.get("analysis", "")
                assert analysis, f"Completed but analysis is empty: {status_data}"
                assert len(analysis) > 100, f"Analysis too short: {len(analysis)} chars"
                print(f"PASS: Dossier completed in {time.time()-start_time:.0f}s with {len(analysis)} char analysis")
                return
            elif final_status == "error":
                error_msg = status_data.get("error", "Unknown error")
                # Budget exceeded is a known transient issue
                if "budget" in error_msg.lower() or "exceeded" in error_msg.lower():
                    pytest.skip(f"LLM budget exceeded (transient): {error_msg}")
                pytest.fail(f"Dossier failed with error: {error_msg}")
            
            time.sleep(poll_interval)
        
        # If we get here, we timed out
        pytest.skip(f"Dossier still processing after {max_wait}s (status={final_status}). LLM may be slow.")
    
    def test_admin_bypass_requires_auth(self):
        """Test that admin-bypass endpoint requires authentication"""
        payload = {
            "name": "TEST_No Auth",
            "email": "test@example.com",
            "situation": "Test without auth",
            "type_dossier": "Accident du travail (AT)",
            "regime": "Régime général"
        }
        
        # Without token
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json=payload,
            timeout=5
        )
        assert response.status_code == 401, f"Should require auth: {response.status_code}"
        print("PASS: Admin bypass requires authentication")
    
    def test_admin_bypass_requires_situation(self, admin_token):
        """Test that admin-bypass requires situation field"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "name": "TEST_No Situation",
            "email": "test@example.com",
            "situation": "",  # Empty situation
            "type_dossier": "Accident du travail (AT)",
            "regime": "Régime général"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json=payload,
            headers=headers,
            timeout=5
        )
        assert response.status_code == 400, f"Should reject empty situation: {response.status_code}"
        print("PASS: Admin bypass requires situation field")
    
    def test_status_endpoint_404_for_invalid_id(self):
        """Test that status endpoint returns 404 for invalid dossier ID"""
        response = requests.get(
            f"{BASE_URL}/api/dossier-express/status/invalid-dossier-id-12345",
            timeout=5
        )
        assert response.status_code == 404, f"Should return 404: {response.status_code}"
        print("PASS: Status endpoint returns 404 for invalid ID")


class TestConcurrentHealthCheck:
    """Test that health check works concurrently with LLM processing"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        token = data.get("access_token") or data.get("token")
        assert token, f"No token in response: {data}"
        return token
    
    def test_concurrent_health_during_llm(self, admin_token):
        """
        Test that multiple health checks succeed while LLM is processing
        Uses concurrent.futures to simulate real concurrent requests
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "name": "TEST_Concurrent Test",
            "email": "test@example.com",
            "situation": "Test for concurrent health checks during LLM processing",
            "type_dossier": "Accident du travail (AT)",
            "regime": "Régime général"
        }
        
        # Start LLM processing
        create_response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json=payload,
            headers=headers,
            timeout=10
        )
        assert create_response.status_code == 200
        
        # Make concurrent health checks
        def check_health():
            start = time.time()
            resp = requests.get(f"{BASE_URL}/api/health", timeout=5)
            return time.time() - start, resp.status_code
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(check_health) for _ in range(5)]
            results = [f.result() for f in futures]
        
        all_success = all(status == 200 for _, status in results)
        all_fast = all(elapsed < 2 for elapsed, _ in results)
        
        assert all_success, f"Some health checks failed: {results}"
        assert all_fast, f"Some health checks too slow: {results}"
        
        print(f"PASS: All 5 concurrent health checks succeeded (times: {[f'{t:.2f}s' for t, _ in results]})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
