"""
Test Calculator Counter Feature - Weekly Usage Tracking
Tests:
  - POST /api/calculator/track - tracks calculation usage
  - GET /api/calculator/count - returns weekly count of calculations
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCalculatorCounterAPI:
    """Test calculator counter/tracking endpoints"""
    
    def test_get_calculator_count(self):
        """GET /api/calculator/count should return a count >= 0"""
        response = requests.get(f"{BASE_URL}/api/calculator/count")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "count" in data, "Response should contain 'count' field"
        assert isinstance(data["count"], int), "count should be an integer"
        assert data["count"] >= 0, "count should be >= 0"
        print(f"✓ GET /api/calculator/count returned count={data['count']}")
    
    def test_track_ipp_calculation(self):
        """POST /api/calculator/track with type='ipp' should return success"""
        # Get initial count
        initial_response = requests.get(f"{BASE_URL}/api/calculator/count")
        initial_count = initial_response.json()["count"]
        
        # Track IPP calculation
        response = requests.post(
            f"{BASE_URL}/api/calculator/track",
            json={"type": "ipp"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "success" in data, "Response should contain 'success' field"
        assert data["success"] is True, "success should be True"
        print(f"✓ POST /api/calculator/track (type=ipp) returned success=True")
        
        # Verify count incremented
        new_response = requests.get(f"{BASE_URL}/api/calculator/count")
        new_count = new_response.json()["count"]
        assert new_count == initial_count + 1, f"Count should increment by 1: was {initial_count}, now {new_count}"
        print(f"✓ Count incremented from {initial_count} to {new_count}")
    
    def test_track_aah_calculation(self):
        """POST /api/calculator/track with type='aah' should return success"""
        # Get initial count
        initial_response = requests.get(f"{BASE_URL}/api/calculator/count")
        initial_count = initial_response.json()["count"]
        
        # Track AAH calculation
        response = requests.post(
            f"{BASE_URL}/api/calculator/track",
            json={"type": "aah"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["success"] is True, "success should be True"
        print(f"✓ POST /api/calculator/track (type=aah) returned success=True")
        
        # Verify count incremented
        new_response = requests.get(f"{BASE_URL}/api/calculator/count")
        new_count = new_response.json()["count"]
        assert new_count == initial_count + 1, f"Count should increment by 1: was {initial_count}, now {new_count}"
        print(f"✓ Count incremented from {initial_count} to {new_count}")
    
    def test_track_with_empty_type(self):
        """POST /api/calculator/track with empty body should still work (defaults to 'unknown')"""
        response = requests.post(
            f"{BASE_URL}/api/calculator/track",
            json={},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "success should be True even with empty type"
        print(f"✓ POST /api/calculator/track (empty type) returned success=True")


class TestHealthAndBasics:
    """Basic health and API availability tests"""
    
    def test_health_endpoint(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ GET /api/health returned status=healthy")
    
    def test_api_root(self):
        """GET /api/ should return welcome message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print(f"✓ GET /api/ returned 200")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
