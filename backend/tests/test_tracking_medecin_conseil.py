"""
Test suite for tracking API endpoints - medecin-conseil page integration
Tests POST /api/tracking/event and GET /api/tracking/stats
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestTrackingAPI:
    """Tests for tracking endpoints used by medecin-conseil page"""
    
    def test_tracking_event_post_success(self):
        """Test POST /api/tracking/event returns status ok"""
        response = requests.post(
            f"{BASE_URL}/api/tracking/event",
            json={
                "page": "medecin-conseil",
                "action": "pytest-test-event",
                "timestamp": datetime.now().isoformat()
            },
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print(f"✓ POST /api/tracking/event returned: {data}")
    
    def test_tracking_event_page_view(self):
        """Test tracking page-view action"""
        response = requests.post(
            f"{BASE_URL}/api/tracking/event",
            json={
                "page": "medecin-conseil",
                "action": "page-view",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        assert response.status_code == 200
        assert response.json().get("status") == "ok"
        print("✓ page-view tracking works")
    
    def test_tracking_event_hero_cta_click(self):
        """Test tracking hero-cta-click action"""
        response = requests.post(
            f"{BASE_URL}/api/tracking/event",
            json={
                "page": "medecin-conseil",
                "action": "hero-cta-click",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        assert response.status_code == 200
        assert response.json().get("status") == "ok"
        print("✓ hero-cta-click tracking works")
    
    def test_tracking_event_cta_accompagnement_click(self):
        """Test tracking cta-accompagnement-click action"""
        response = requests.post(
            f"{BASE_URL}/api/tracking/event",
            json={
                "page": "medecin-conseil",
                "action": "cta-accompagnement-click",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        assert response.status_code == 200
        assert response.json().get("status") == "ok"
        print("✓ cta-accompagnement-click tracking works")
    
    def test_tracking_stats_get_all(self):
        """Test GET /api/tracking/stats returns stats array"""
        response = requests.get(f"{BASE_URL}/api/tracking/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert isinstance(data["stats"], list)
        print(f"✓ GET /api/tracking/stats returned {len(data['stats'])} stat entries")
    
    def test_tracking_stats_filter_by_page(self):
        """Test GET /api/tracking/stats?page=medecin-conseil filters correctly"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/stats",
            params={"page": "medecin-conseil"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        
        # All returned stats should be for medecin-conseil page
        for stat in data["stats"]:
            assert stat.get("page") == "medecin-conseil"
        
        print(f"✓ Filtered stats for medecin-conseil: {len(data['stats'])} entries")
        for stat in data["stats"]:
            print(f"  - {stat['action']}: {stat['count']} events")
    
    def test_tracking_stats_structure(self):
        """Test that stats have correct structure"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/stats",
            params={"page": "medecin-conseil"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["stats"]:
            stat = data["stats"][0]
            assert "page" in stat
            assert "action" in stat
            assert "count" in stat
            assert isinstance(stat["count"], int)
            print(f"✓ Stats structure is correct: {stat}")


class TestMedecinConseilPageRoutes:
    """Tests for medecin-conseil page accessibility"""
    
    def test_medecin_conseil_page_loads(self):
        """Test that /medecin-conseil page is accessible"""
        response = requests.get(f"{BASE_URL}/medecin-conseil")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        print("✓ /medecin-conseil page loads successfully")
    
    def test_homepage_loads(self):
        """Test that homepage is accessible"""
        response = requests.get(f"{BASE_URL}/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        print("✓ Homepage loads successfully")
    
    def test_services_page_loads(self):
        """Test that /accompagnements page is accessible"""
        response = requests.get(f"{BASE_URL}/accompagnements")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        print("✓ /accompagnements page loads successfully")
    
    def test_expertise_medicale_page_loads(self):
        """Test that /expertise-medicale page is accessible"""
        response = requests.get(f"{BASE_URL}/expertise-medicale")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        print("✓ /expertise-medicale page loads successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
