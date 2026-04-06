"""
V2 Readiness Status (Traffic Light) API Tests
==============================================
Tests for the V2 Readiness scoring system that evaluates if enough data
has been collected in case_outcomes to start building V2 Predictive AI.

Rules:
- Red (rouge): < 200 cases
- Orange: 200-499 cases  
- Green (vert): >= 500 cases minimum

Score breakdown:
- Volume: 50 pts max
- Diversity: 20 pts max
- Completeness: 15 pts max
- Quality: 15 pts max
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestV2ReadinessAPI:
    """V2 Readiness endpoint tests"""
    
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
    
    def test_v2_readiness_requires_authentication(self):
        """Test that /api/knowledge-patterns/v2-readiness returns 401/403 without auth"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns/v2-readiness")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: V2 Readiness endpoint requires authentication")
    
    def test_v2_readiness_returns_correct_structure(self):
        """Test that V2 Readiness returns all required fields"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness",
            headers=self.auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check required top-level fields
        required_fields = [
            "score", "status", "total_cases", "usable_cases",
            "minimum_green", "minimum_orange", "breakdown", "details",
            "complexity_distribution", "source_distribution"
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check breakdown structure
        breakdown_fields = ["volume", "diversity", "completeness", "quality"]
        for field in breakdown_fields:
            assert field in data["breakdown"], f"Missing breakdown field: {field}"
        
        # Check details structure
        details_fields = ["unique_families", "unique_categories", "with_blocage", "with_quality", "with_leviers"]
        for field in details_fields:
            assert field in data["details"], f"Missing details field: {field}"
        
        print(f"PASS: V2 Readiness returns correct structure with all required fields")
        print(f"  Score: {data['score']}, Status: {data['status']}")
    
    def test_v2_readiness_score_range(self):
        """Test that score is between 0 and 100"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 0 <= data["score"] <= 100, f"Score {data['score']} out of range [0, 100]"
        print(f"PASS: Score {data['score']} is within valid range [0, 100]")
    
    def test_v2_readiness_status_rouge_when_low_cases(self):
        """Test that status is 'rouge' when case count < 200"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # With current 3 cases, status should be 'rouge'
        if data["usable_cases"] < 200:
            assert data["status"] == "rouge", f"Expected 'rouge' for {data['usable_cases']} cases, got '{data['status']}'"
            print(f"PASS: Status is 'rouge' for {data['usable_cases']} cases (< 200)")
        else:
            print(f"SKIP: Cannot verify rouge status - {data['usable_cases']} cases >= 200")
    
    def test_v2_readiness_breakdown_max_values(self):
        """Test that breakdown values don't exceed their max"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        breakdown = data["breakdown"]
        
        # Volume max 50, Diversity max 20, Completeness max 15, Quality max 15
        assert breakdown["volume"] <= 50, f"Volume {breakdown['volume']} exceeds max 50"
        assert breakdown["diversity"] <= 20, f"Diversity {breakdown['diversity']} exceeds max 20"
        assert breakdown["completeness"] <= 15, f"Completeness {breakdown['completeness']} exceeds max 15"
        assert breakdown["quality"] <= 15, f"Quality {breakdown['quality']} exceeds max 15"
        
        print(f"PASS: All breakdown values within limits")
        print(f"  Volume: {breakdown['volume']}/50, Diversity: {breakdown['diversity']}/20")
        print(f"  Completeness: {breakdown['completeness']}/15, Quality: {breakdown['quality']}/15")
    
    def test_v2_readiness_score_equals_breakdown_sum(self):
        """Test that score approximately equals sum of breakdown components"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        breakdown = data["breakdown"]
        
        breakdown_sum = (
            breakdown["volume"] + 
            breakdown["diversity"] + 
            breakdown["completeness"] + 
            breakdown["quality"]
        )
        
        # Score is rounded, so allow small difference
        assert abs(data["score"] - round(breakdown_sum)) <= 1, \
            f"Score {data['score']} doesn't match breakdown sum {breakdown_sum}"
        
        print(f"PASS: Score {data['score']} matches breakdown sum {round(breakdown_sum)}")
    
    def test_v2_readiness_minimum_thresholds(self):
        """Test that minimum thresholds are correctly set"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        
        assert data["minimum_green"] == 500, f"Expected minimum_green=500, got {data['minimum_green']}"
        assert data["minimum_orange"] == 200, f"Expected minimum_orange=200, got {data['minimum_orange']}"
        
        print(f"PASS: Minimum thresholds correct (green=500, orange=200)")
    
    def test_v2_readiness_distributions_format(self):
        """Test that distributions have correct format"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Check complexity distribution format
        for item in data["complexity_distribution"]:
            assert "niveau" in item, "Missing 'niveau' in complexity distribution"
            assert "count" in item, "Missing 'count' in complexity distribution"
            assert isinstance(item["count"], int), "Count should be integer"
        
        # Check source distribution format
        for item in data["source_distribution"]:
            assert "source" in item, "Missing 'source' in source distribution"
            assert "count" in item, "Missing 'count' in source distribution"
            assert isinstance(item["count"], int), "Count should be integer"
        
        print(f"PASS: Distributions have correct format")
        print(f"  Complexity: {data['complexity_distribution']}")
        print(f"  Source: {data['source_distribution']}")
    
    def test_v2_readiness_details_non_negative(self):
        """Test that all detail values are non-negative"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        details = data["details"]
        
        for key, value in details.items():
            assert value >= 0, f"Detail '{key}' has negative value: {value}"
        
        print(f"PASS: All detail values are non-negative")
        print(f"  Details: {details}")


class TestV2ReadinessStatusLogic:
    """Tests for V2 Readiness status determination logic"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
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
    
    def test_status_logic_current_state(self):
        """Verify current status matches expected based on case count"""
        response = self.session.get(
            f"{BASE_URL}/api/knowledge-patterns/v2-readiness",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        usable = data["usable_cases"]
        score = data["score"]
        status = data["status"]
        
        # Determine expected status based on rules
        if usable >= 500 and score >= 70:
            expected = "vert"
        elif usable >= 200 and score >= 40:
            expected = "orange"
        else:
            expected = "rouge"
        
        assert status == expected, f"Expected status '{expected}' for {usable} cases and score {score}, got '{status}'"
        print(f"PASS: Status '{status}' is correct for {usable} usable cases and score {score}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
