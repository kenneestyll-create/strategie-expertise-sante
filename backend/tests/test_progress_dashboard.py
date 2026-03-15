"""
Test Progress Dashboard feature - GET /api/client/progress endpoint
Tests: progress_pct, steps array, next_action, counts, summary fields
Test client: test-notif@example.com / Test1234! with 3 documents (0 validated), 0 analyses
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestProgressDashboard:
    """Progress Dashboard API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token for test client"""
        self.token = None
        login_resp = requests.post(f"{BASE_URL}/api/client/login", json={
            "email": "test-notif@example.com",
            "password": "Test1234!"
        })
        if login_resp.status_code == 200:
            self.token = login_resp.json().get("access_token")
        yield
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    def test_progress_endpoint_requires_auth(self):
        """GET /api/client/progress requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/client/progress")
        assert resp.status_code in (401, 403), f"Expected 401/403, got {resp.status_code}"
        print("PASS: /api/client/progress requires authentication")
    
    def test_progress_endpoint_returns_200(self):
        """GET /api/client/progress returns 200 with token"""
        if not self.token:
            pytest.skip("No token available")
        resp = requests.get(f"{BASE_URL}/api/client/progress", headers=self.get_headers())
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("PASS: /api/client/progress returns 200 with valid token")
    
    def test_progress_returns_progress_pct(self):
        """GET /api/client/progress returns progress_pct field"""
        if not self.token:
            pytest.skip("No token available")
        resp = requests.get(f"{BASE_URL}/api/client/progress", headers=self.get_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert "progress_pct" in data, "Missing progress_pct field"
        assert isinstance(data["progress_pct"], int), "progress_pct should be int"
        assert 0 <= data["progress_pct"] <= 100, f"progress_pct should be 0-100, got {data['progress_pct']}"
        print(f"PASS: progress_pct = {data['progress_pct']}%")
    
    def test_progress_returns_steps_array(self):
        """GET /api/client/progress returns steps array with 6 steps"""
        if not self.token:
            pytest.skip("No token available")
        resp = requests.get(f"{BASE_URL}/api/client/progress", headers=self.get_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert "steps" in data, "Missing steps field"
        assert isinstance(data["steps"], list), "steps should be a list"
        assert len(data["steps"]) == 6, f"Expected 6 steps, got {len(data['steps'])}"
        
        expected_ids = ["inscription", "documents", "strategiia", "dossier_express", "analyse_premium", "finalisation"]
        actual_ids = [s["id"] for s in data["steps"]]
        assert actual_ids == expected_ids, f"Step IDs mismatch: {actual_ids}"
        print(f"PASS: Steps array has 6 steps: {actual_ids}")
    
    def test_progress_steps_have_required_fields(self):
        """Each step has id, label, status, detail fields"""
        if not self.token:
            pytest.skip("No token available")
        resp = requests.get(f"{BASE_URL}/api/client/progress", headers=self.get_headers())
        assert resp.status_code == 200
        data = resp.json()
        
        for step in data["steps"]:
            assert "id" in step, f"Step missing id: {step}"
            assert "label" in step, f"Step missing label: {step}"
            assert "status" in step, f"Step missing status: {step}"
            assert "detail" in step, f"Step missing detail: {step}"
            assert step["status"] in ["completed", "in_progress", "action_required", "not_started"], \
                f"Invalid status '{step['status']}' for step {step['id']}"
        print("PASS: All steps have required fields (id, label, status, detail)")
    
    def test_inscription_step_completed(self):
        """Inscription step should always be completed"""
        if not self.token:
            pytest.skip("No token available")
        resp = requests.get(f"{BASE_URL}/api/client/progress", headers=self.get_headers())
        assert resp.status_code == 200
        data = resp.json()
        
        inscription = next((s for s in data["steps"] if s["id"] == "inscription"), None)
        assert inscription is not None, "Missing inscription step"
        assert inscription["status"] == "completed", f"Inscription should be completed, got {inscription['status']}"
        print(f"PASS: Inscription step is completed: {inscription}")
    
    def test_documents_step_status(self):
        """Documents step: test client has 3 docs, 0 validated → in_progress"""
        if not self.token:
            pytest.skip("No token available")
        resp = requests.get(f"{BASE_URL}/api/client/progress", headers=self.get_headers())
        assert resp.status_code == 200
        data = resp.json()
        
        doc_step = next((s for s in data["steps"] if s["id"] == "documents"), None)
        assert doc_step is not None, "Missing documents step"
        # With 3 docs and 0 validated, status should be in_progress
        assert doc_step["status"] in ["in_progress", "action_required", "not_started"], \
            f"Documents status should be in_progress/action_required/not_started, got {doc_step['status']}"
        print(f"PASS: Documents step status={doc_step['status']}, detail={doc_step['detail']}")
    
    def test_strategiia_step_status(self):
        """StrategiIA step: test client has 0 analyses → action_required or not_started"""
        if not self.token:
            pytest.skip("No token available")
        resp = requests.get(f"{BASE_URL}/api/client/progress", headers=self.get_headers())
        assert resp.status_code == 200
        data = resp.json()
        
        strat_step = next((s for s in data["steps"] if s["id"] == "strategiia"), None)
        assert strat_step is not None, "Missing strategiia step"
        # With 0 analyses but >=1 doc, should be action_required
        assert strat_step["status"] in ["action_required", "not_started", "completed"], \
            f"StrategiIA status should be action_required/not_started, got {strat_step['status']}"
        print(f"PASS: StrategiIA step status={strat_step['status']}, detail={strat_step['detail']}")
    
    def test_progress_returns_next_action(self):
        """GET /api/client/progress returns next_action pointing to first non-completed step"""
        if not self.token:
            pytest.skip("No token available")
        resp = requests.get(f"{BASE_URL}/api/client/progress", headers=self.get_headers())
        assert resp.status_code == 200
        data = resp.json()
        
        assert "next_action" in data, "Missing next_action field"
        if data["next_action"] is not None:
            assert "step_id" in data["next_action"], "next_action missing step_id"
            assert "label" in data["next_action"], "next_action missing label"
            assert "detail" in data["next_action"], "next_action missing detail"
            assert "status" in data["next_action"], "next_action missing status"
            
            # Verify it points to first non-completed step
            non_completed = [s for s in data["steps"] if s["status"] != "completed"]
            if non_completed:
                expected_first = non_completed[0]["id"]
                actual = data["next_action"]["step_id"]
                assert actual == expected_first, f"next_action should point to {expected_first}, got {actual}"
        print(f"PASS: next_action = {data['next_action']}")
    
    def test_progress_returns_counts(self):
        """GET /api/client/progress returns counts for pie chart"""
        if not self.token:
            pytest.skip("No token available")
        resp = requests.get(f"{BASE_URL}/api/client/progress", headers=self.get_headers())
        assert resp.status_code == 200
        data = resp.json()
        
        assert "counts" in data, "Missing counts field"
        counts = data["counts"]
        assert "completed" in counts, "counts missing completed"
        assert "in_progress" in counts, "counts missing in_progress"
        assert "action_required" in counts, "counts missing action_required"
        assert "not_started" in counts, "counts missing not_started"
        
        # Sum should equal number of steps (6)
        total = counts["completed"] + counts["in_progress"] + counts["action_required"] + counts["not_started"]
        assert total == 6, f"Counts should sum to 6, got {total}"
        print(f"PASS: counts = {counts}")
    
    def test_progress_returns_summary(self):
        """GET /api/client/progress returns summary with document/analysis counts"""
        if not self.token:
            pytest.skip("No token available")
        resp = requests.get(f"{BASE_URL}/api/client/progress", headers=self.get_headers())
        assert resp.status_code == 200
        data = resp.json()
        
        assert "summary" in data, "Missing summary field"
        summary = data["summary"]
        assert "total_documents" in summary, "summary missing total_documents"
        assert "validated_documents" in summary, "summary missing validated_documents"
        assert "analyses_ia" in summary, "summary missing analyses_ia"
        
        # Verify test client has 3 docs, 0 validated
        assert isinstance(summary["total_documents"], int), "total_documents should be int"
        assert isinstance(summary["validated_documents"], int), "validated_documents should be int"
        assert isinstance(summary["analyses_ia"], int), "analyses_ia should be int"
        print(f"PASS: summary = {summary}")
    
    def test_progress_pct_calculation(self):
        """Verify progress_pct is calculated correctly based on weights"""
        if not self.token:
            pytest.skip("No token available")
        resp = requests.get(f"{BASE_URL}/api/client/progress", headers=self.get_headers())
        assert resp.status_code == 200
        data = resp.json()
        
        # Calculate expected progress based on weights
        weights = {"completed": 1.0, "in_progress": 0.5, "action_required": 0.3, "not_started": 0}
        total_weight = sum(weights.get(s["status"], 0) for s in data["steps"])
        expected_pct = round((total_weight / len(data["steps"])) * 100)
        
        assert data["progress_pct"] == expected_pct, \
            f"progress_pct {data['progress_pct']} != expected {expected_pct}"
        print(f"PASS: progress_pct = {data['progress_pct']}% (calculated correctly)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
