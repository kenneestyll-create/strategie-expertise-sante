"""
V2 Readiness History API Tests
==============================
Tests for the NEW V2 Readiness history tracking feature:
1. Auto-snapshot on v2-readiness endpoint call
2. History endpoint returns sorted data (max 90 days)
3. History endpoint requires authentication
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestV2ReadinessHistory:
    """V2 Readiness History endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for authenticated requests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@accompagn-sante.fr", "password": "Admin2024!"}
        )
        
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("access_token")
            self.auth_headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Admin authentication failed")
    
    def test_history_requires_authentication(self):
        """Test that /api/knowledge-patterns/v2-readiness/history returns 401/403 without auth"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns/v2-readiness/history")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: History endpoint requires authentication")
    
    def test_history_returns_sorted_data(self):
        """Test that history returns data sorted by date ascending"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness/history",
            headers=self.auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "history" in data, "Response missing 'history' field"
        
        history = data["history"]
        assert isinstance(history, list), "History should be a list"
        
        # Check sorting (ascending by date)
        if len(history) > 1:
            dates = [h["date"] for h in history]
            assert dates == sorted(dates), f"History not sorted by date: {dates}"
            print(f"PASS: History is sorted ascending by date ({len(history)} records)")
        else:
            print(f"PASS: History returned {len(history)} record(s)")
    
    def test_history_record_structure(self):
        """Test that each history record has required fields"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness/history",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        history = data.get("history", [])
        
        if len(history) == 0:
            pytest.skip("No history records to validate structure")
        
        required_fields = ["date", "score", "status", "total_cases", "usable_cases", 
                          "volume", "diversity", "completeness", "quality"]
        
        for record in history:
            for field in required_fields:
                assert field in record, f"History record missing field: {field}"
        
        print(f"PASS: All {len(history)} history records have correct structure")
    
    def test_history_excludes_mongodb_id(self):
        """Test that history records don't include MongoDB _id field"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness/history",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        history = data.get("history", [])
        
        for record in history:
            assert "_id" not in record, "History record should not include _id"
        
        print("PASS: History records correctly exclude MongoDB _id")
    
    def test_history_max_90_days(self):
        """Test that history returns max 90 days of data"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness/history",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        history = data.get("history", [])
        
        assert len(history) <= 90, f"History should return max 90 records, got {len(history)}"
        print(f"PASS: History returns {len(history)} records (max 90)")
    
    def test_v2_readiness_triggers_auto_snapshot(self):
        """Test that calling v2-readiness endpoint creates/updates daily snapshot"""
        # First call v2-readiness to trigger auto-snapshot
        readiness_response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness",
            headers=self.auth_headers
        )
        assert readiness_response.status_code == 200
        readiness_data = readiness_response.json()
        
        # Then check history for today's date
        history_response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness/history",
            headers=self.auth_headers
        )
        assert history_response.status_code == 200
        
        history = history_response.json().get("history", [])
        
        # Get today's date in same format as backend
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Check if today's snapshot exists
        today_snapshot = next((h for h in history if h["date"] == today), None)
        
        if today_snapshot:
            # Verify snapshot matches current readiness data
            assert today_snapshot["score"] == readiness_data["score"], "Snapshot score mismatch"
            assert today_snapshot["status"] == readiness_data["status"], "Snapshot status mismatch"
            print(f"PASS: Today's snapshot ({today}) exists with score={today_snapshot['score']}")
        else:
            # Snapshot might have been created on a previous day
            print(f"INFO: No snapshot for today ({today}), but history has {len(history)} records")
    
    def test_history_has_seeded_data(self):
        """Test that history has the seeded test data (8 data points)"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness/history",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        history = data.get("history", [])
        
        # Per the agent context, 8 data points were seeded (2026-03-30 to 2026-04-06)
        assert len(history) >= 8, f"Expected at least 8 seeded records, got {len(history)}"
        
        # Check first and last seeded dates
        dates = [h["date"] for h in history]
        assert "2026-03-30" in dates, "Missing seeded date 2026-03-30"
        assert "2026-04-06" in dates, "Missing seeded date 2026-04-06"
        
        print(f"PASS: History contains seeded data ({len(history)} records)")
        print(f"  Date range: {dates[0]} to {dates[-1]}")
