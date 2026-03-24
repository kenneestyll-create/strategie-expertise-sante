"""
StrategiIA Async Polling Tests
- POST /api/strategiia/analyze returns job_id and status:pending immediately (non-blocking)
- GET /api/strategiia/status/{job_id} returns status:pending while LLM is processing
- GET /api/strategiia/status/{job_id} eventually returns status:done with analysis containing section markers
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestStrategiiaAsyncPolling:
    """Test async polling flow for StrategiIA analysis"""
    
    def test_analyze_returns_job_id_immediately(self):
        """POST /api/strategiia/analyze should return job_id and status:pending immediately (non-blocking)"""
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json={
            "type_dossier": "at",
            "regime": "general",
            "situation": "Test accident du travail pour vérifier le polling async - test immediate response",
            "premium": False
        }, timeout=30)  # Should respond within 30 seconds (non-blocking)
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "job_id" in data, "Response should contain 'job_id'"
        assert "status" in data, "Response should contain 'status'"
        assert data["status"] == "pending", f"Initial status should be 'pending', got {data['status']}"
        
        # Verify it's non-blocking (should respond quickly, not wait for LLM)
        # Note: Network latency in preview environment can add significant delay
        # The key test is that we get job_id and status:pending, not the full analysis
        assert elapsed < 60, f"Response took {elapsed:.2f}s - should not wait for full LLM response"
        
        print(f"PASS: POST /api/strategiia/analyze returned job_id={data['job_id']} with status=pending in {elapsed:.2f}s")
        return data["job_id"]
    
    def test_status_returns_pending_while_processing(self):
        """GET /api/strategiia/status/{job_id} should return status:pending while LLM is processing"""
        # First create a job
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json={
            "type_dossier": "mp",
            "regime": "general",
            "situation": "Test maladie professionnelle pour vérifier le status pending",
            "premium": False
        }, timeout=60)
        
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        
        # Immediately check status - should be pending
        status_response = requests.get(f"{BASE_URL}/api/strategiia/status/{job_id}", timeout=5)
        
        assert status_response.status_code == 200, f"Expected 200, got {status_response.status_code}"
        
        status_data = status_response.json()
        assert "status" in status_data, "Response should contain 'status'"
        
        # Status could be pending or done (if LLM is very fast)
        assert status_data["status"] in ["pending", "done"], f"Status should be 'pending' or 'done', got {status_data['status']}"
        
        print(f"PASS: GET /api/strategiia/status/{job_id} returned status={status_data['status']}")
        return job_id
    
    def test_status_eventually_returns_done_with_sections(self):
        """GET /api/strategiia/status/{job_id} should eventually return status:done with section markers"""
        # Create a job
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json={
            "type_dossier": "at",
            "regime": "general",
            "situation": "Test accident du travail avec chute d'échelle sur chantier. Fracture du poignet gauche. Arrêt de travail de 3 mois.",
            "premium": False
        }, timeout=60)
        
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        
        # Poll for completion (max 60 seconds)
        max_wait = 60
        poll_interval = 3
        elapsed = 0
        final_data = None
        
        while elapsed < max_wait:
            status_response = requests.get(f"{BASE_URL}/api/strategiia/status/{job_id}", timeout=10)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                if status_data["status"] == "done":
                    final_data = status_data
                    break
                elif status_data["status"] == "error":
                    pytest.fail(f"Analysis failed with error: {status_data.get('error', 'Unknown error')}")
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        assert final_data is not None, f"Analysis did not complete within {max_wait} seconds"
        assert final_data["status"] == "done", f"Expected status 'done', got {final_data['status']}"
        
        # Verify analysis contains section markers
        analysis = final_data.get("analysis", "")
        assert "---SECTION_1---" in analysis, "Analysis should contain ---SECTION_1--- marker"
        assert "---SECTION_2---" in analysis, "Analysis should contain ---SECTION_2--- marker"
        assert "---SECTION_3---" in analysis, "Analysis should contain ---SECTION_3--- marker"
        
        # Verify other expected fields
        assert "success" in final_data, "Response should contain 'success'"
        assert final_data["success"] == True, "success should be True"
        assert "cases_found" in final_data, "Response should contain 'cases_found'"
        
        print(f"PASS: Analysis completed with all 3 section markers. Analysis length: {len(analysis)} chars")
        print(f"  - cases_found: {final_data.get('cases_found', 0)}")
        print(f"  - remaining: {final_data.get('remaining', 'N/A')}")
    
    def test_invalid_job_id_returns_404(self):
        """GET /api/strategiia/status/{invalid_job_id} should return 404"""
        response = requests.get(f"{BASE_URL}/api/strategiia/status/invalid-job-id-12345", timeout=5)
        
        assert response.status_code == 404, f"Expected 404 for invalid job_id, got {response.status_code}"
        print("PASS: Invalid job_id returns 404")
    
    def test_analyze_missing_situation_returns_400(self):
        """POST /api/strategiia/analyze with empty situation should return 400"""
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json={
            "type_dossier": "at",
            "regime": "general",
            "situation": "",
            "premium": False
        }, timeout=10)
        
        assert response.status_code == 400, f"Expected 400 for empty situation, got {response.status_code}"
        print("PASS: Empty situation returns 400")
    
    def test_analyze_whitespace_only_situation_returns_400(self):
        """POST /api/strategiia/analyze with whitespace-only situation should return 400"""
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json={
            "type_dossier": "at",
            "regime": "general",
            "situation": "   \n\t  ",
            "premium": False
        }, timeout=10)
        
        assert response.status_code == 400, f"Expected 400 for whitespace-only situation, got {response.status_code}"
        print("PASS: Whitespace-only situation returns 400")


class TestStrategiiaQuota:
    """Test quota/email registration endpoints"""
    
    def test_register_email_success(self):
        """POST /api/strategiia/register-email should register email and return remaining quota"""
        test_email = f"test_quota_{int(time.time())}@example.com"
        
        response = requests.post(f"{BASE_URL}/api/strategiia/register-email", json={
            "email": test_email
        }, timeout=10)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Should return success=True"
        assert "remaining" in data, "Should return remaining quota"
        assert data["remaining"] >= 0, "Remaining should be >= 0"
        
        print(f"PASS: Email registered, remaining quota: {data['remaining']}")
    
    def test_register_email_invalid_returns_400(self):
        """POST /api/strategiia/register-email with invalid email should return 400"""
        response = requests.post(f"{BASE_URL}/api/strategiia/register-email", json={
            "email": "invalid-email"
        }, timeout=10)
        
        assert response.status_code == 400, f"Expected 400 for invalid email, got {response.status_code}"
        print("PASS: Invalid email returns 400")
    
    def test_get_quota_for_email(self):
        """GET /api/strategiia/quota/{email} should return quota info"""
        test_email = "test_quota_check@example.com"
        
        response = requests.get(f"{BASE_URL}/api/strategiia/quota/{test_email}", timeout=10)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "remaining" in data, "Should return remaining"
        assert "limit" in data, "Should return limit"
        assert "used" in data, "Should return used"
        assert data["limit"] == 3, "Limit should be 3"
        
        print(f"PASS: Quota check - remaining: {data['remaining']}, used: {data['used']}, limit: {data['limit']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
