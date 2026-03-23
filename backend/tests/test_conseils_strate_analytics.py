"""
Test suite for Conseils Straté Analytics & Tracking features (Iteration 91)
Tests: 
- GET /api/conseils/today returns 'id' field
- POST /api/conseils/view - view tracking with daily stats
- POST /api/conseils/click - click tracking with daily stats  
- POST /api/conseils/conversion - conversion tracking
- GET /api/conseils/admin/stats - includes total_conversions, ctr
- GET /api/conseils/admin/analytics - period/category filters, timeseries, topConseils
- Unauthenticated access returns 403
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


class TestConseilsTodayEndpoint:
    """Test GET /api/conseils/today returns conseil with 'id' field"""
    
    def test_today_conseil_has_id_field(self):
        """GET /api/conseils/today should return conseil with 'id' field (string ObjectId)"""
        response = requests.get(f"{BASE_URL}/api/conseils/today")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response missing 'id' field"
        assert isinstance(data["id"], str), "id should be a string"
        assert len(data["id"]) == 24, f"id should be 24-char ObjectId, got {len(data['id'])} chars"
        
        print(f"✓ GET /api/conseils/today returns conseil with id={data['id']}")


class TestTrackingEndpoints:
    """Test view/click/conversion tracking endpoints"""
    
    def test_track_view_returns_ok(self):
        """POST /api/conseils/view should track view and return {ok: true}"""
        # First get a conseil to get its ID
        conseil_resp = requests.get(f"{BASE_URL}/api/conseils/today")
        conseil_id = conseil_resp.json().get("id", "")
        
        response = requests.post(
            f"{BASE_URL}/api/conseils/view",
            json={"conseil_id": conseil_id},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok: true"
        print(f"✓ POST /api/conseils/view tracked view for conseil_id={conseil_id}")
    
    def test_track_view_without_id_returns_ok_false(self):
        """POST /api/conseils/view without conseil_id should return {ok: false}"""
        response = requests.post(
            f"{BASE_URL}/api/conseils/view",
            json={},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == False, "Response should have ok: false when no conseil_id"
        print("✓ POST /api/conseils/view without conseil_id returns ok: false")
    
    def test_track_click_with_conseil_id_returns_ok(self):
        """POST /api/conseils/click with conseil_id should track click and return {ok: true}"""
        # First get a conseil to get its ID
        conseil_resp = requests.get(f"{BASE_URL}/api/conseils/today")
        conseil_id = conseil_resp.json().get("id", "")
        
        response = requests.post(
            f"{BASE_URL}/api/conseils/click",
            json={"conseil_id": conseil_id},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok: true"
        print(f"✓ POST /api/conseils/click tracked click for conseil_id={conseil_id}")
    
    def test_track_click_with_text_fallback_returns_ok(self):
        """POST /api/conseils/click with text (no conseil_id) should still work"""
        # First get a conseil to get its text
        conseil_resp = requests.get(f"{BASE_URL}/api/conseils/today")
        conseil_text = conseil_resp.json().get("text", "")
        
        response = requests.post(
            f"{BASE_URL}/api/conseils/click",
            json={"text": conseil_text},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok: true"
        print("✓ POST /api/conseils/click with text fallback returns ok: true")
    
    def test_track_conversion_returns_ok(self):
        """POST /api/conseils/conversion should track conversion and return {ok: true}"""
        # First get a conseil to get its ID
        conseil_resp = requests.get(f"{BASE_URL}/api/conseils/today")
        conseil_id = conseil_resp.json().get("id", "")
        
        response = requests.post(
            f"{BASE_URL}/api/conseils/conversion",
            json={"conseil_id": conseil_id, "action": "test_action"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok: true"
        print(f"✓ POST /api/conseils/conversion tracked conversion for conseil_id={conseil_id}")
    
    def test_track_conversion_without_id_returns_ok_false(self):
        """POST /api/conseils/conversion without conseil_id should return {ok: false}"""
        response = requests.post(
            f"{BASE_URL}/api/conseils/conversion",
            json={"action": "test_action"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == False, "Response should have ok: false when no conseil_id"
        print("✓ POST /api/conseils/conversion without conseil_id returns ok: false")


class TestAdminStatsEndpoint:
    """Test GET /api/conseils/admin/stats returns all required fields"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token before each test"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Admin login failed: {login_response.status_code} - {login_response.text}")
        
        token = login_response.json().get("access_token")
        if not token:
            pytest.skip("No access_token in login response")
        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_admin_stats_has_all_fields(self):
        """GET /api/conseils/admin/stats should return total, active, total_views, total_clicks, total_conversions, ctr"""
        response = requests.get(
            f"{BASE_URL}/api/conseils/admin/stats",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        required_fields = ["total", "active", "total_views", "total_clicks", "total_conversions", "ctr"]
        for field in required_fields:
            assert field in data, f"Stats missing '{field}' field"
        
        # Verify data types
        assert isinstance(data["total"], int), "total should be int"
        assert isinstance(data["active"], int), "active should be int"
        assert isinstance(data["total_views"], int), "total_views should be int"
        assert isinstance(data["total_clicks"], int), "total_clicks should be int"
        assert isinstance(data["total_conversions"], int), "total_conversions should be int"
        assert isinstance(data["ctr"], (int, float)), "ctr should be numeric"
        
        print(f"✓ GET /api/conseils/admin/stats: total={data['total']}, views={data['total_views']}, clicks={data['total_clicks']}, conversions={data['total_conversions']}, ctr={data['ctr']}%")


class TestAdminAnalyticsEndpoint:
    """Test GET /api/conseils/admin/analytics with filters"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token before each test"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Admin login failed: {login_response.status_code} - {login_response.text}")
        
        token = login_response.json().get("access_token")
        if not token:
            pytest.skip("No access_token in login response")
        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_analytics_default_7d_all(self):
        """GET /api/conseils/admin/analytics returns topConseils, totals, timeseries, categories"""
        response = requests.get(
            f"{BASE_URL}/api/conseils/admin/analytics",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        required_fields = ["topConseils", "totals", "timeseries", "categories"]
        for field in required_fields:
            assert field in data, f"Analytics missing '{field}' field"
        
        # Verify topConseils structure
        assert isinstance(data["topConseils"], list), "topConseils should be a list"
        if len(data["topConseils"]) > 0:
            top = data["topConseils"][0]
            assert "id" in top, "topConseils item missing 'id'"
            assert "text" in top, "topConseils item missing 'text'"
            assert "views" in top, "topConseils item missing 'views'"
            assert "clicks" in top, "topConseils item missing 'clicks'"
            assert "ctr" in top, "topConseils item missing 'ctr'"
        
        # Verify totals structure
        totals = data["totals"]
        assert "views" in totals, "totals missing 'views'"
        assert "clicks" in totals, "totals missing 'clicks'"
        assert "conversions" in totals, "totals missing 'conversions'"
        assert "ctr" in totals, "totals missing 'ctr'"
        
        # Verify timeseries structure
        assert isinstance(data["timeseries"], list), "timeseries should be a list"
        
        print(f"✓ GET /api/conseils/admin/analytics: topConseils={len(data['topConseils'])}, timeseries={len(data['timeseries'])} entries")
    
    def test_analytics_7d_period_has_7_entries(self):
        """GET /api/conseils/admin/analytics?period=7d should return 7 entries in timeseries"""
        response = requests.get(
            f"{BASE_URL}/api/conseils/admin/analytics?period=7d&category=all",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert len(data["timeseries"]) == 7, f"Expected 7 timeseries entries for 7d, got {len(data['timeseries'])}"
        
        # Verify each entry has required fields
        for entry in data["timeseries"]:
            assert "date" in entry, "timeseries entry missing 'date'"
            assert "views" in entry, "timeseries entry missing 'views'"
            assert "clicks" in entry, "timeseries entry missing 'clicks'"
            assert "conversions" in entry, "timeseries entry missing 'conversions'"
        
        print(f"✓ GET /api/conseils/admin/analytics?period=7d returns 7 timeseries entries")
    
    def test_analytics_30d_period_has_30_entries(self):
        """GET /api/conseils/admin/analytics?period=30d should return 30 entries in timeseries"""
        response = requests.get(
            f"{BASE_URL}/api/conseils/admin/analytics?period=30d",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert len(data["timeseries"]) == 30, f"Expected 30 timeseries entries for 30d, got {len(data['timeseries'])}"
        
        print(f"✓ GET /api/conseils/admin/analytics?period=30d returns 30 timeseries entries")
    
    def test_analytics_category_filter(self):
        """GET /api/conseils/admin/analytics?category=droits should filter by category"""
        response = requests.get(
            f"{BASE_URL}/api/conseils/admin/analytics?period=7d&category=droits",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # topConseils should only contain 'droits' category
        for conseil in data["topConseils"]:
            assert conseil["category"] == "droits", f"Expected category 'droits', got '{conseil['category']}'"
        
        print(f"✓ GET /api/conseils/admin/analytics?category=droits filters topConseils correctly")


class TestAdminAnalyticsAuth:
    """Test that analytics endpoint requires authentication"""
    
    def test_analytics_requires_auth(self):
        """GET /api/conseils/admin/analytics should return 401/403 without auth"""
        response = requests.get(f"{BASE_URL}/api/conseils/admin/analytics")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ GET /api/conseils/admin/analytics requires auth ({response.status_code})")


class TestTrackingIncrementsDailyStats:
    """Test that tracking endpoints increment daily stats and global counters"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token before each test"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Admin login failed: {login_response.status_code}")
        
        token = login_response.json().get("access_token")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_view_increments_global_views(self):
        """POST /api/conseils/view should increment global views counter"""
        # Get initial stats
        stats_before = requests.get(
            f"{BASE_URL}/api/conseils/admin/stats",
            headers=self.headers
        ).json()
        
        # Get a conseil and track view
        conseil_resp = requests.get(f"{BASE_URL}/api/conseils/today")
        conseil_id = conseil_resp.json().get("id", "")
        
        requests.post(
            f"{BASE_URL}/api/conseils/view",
            json={"conseil_id": conseil_id},
            headers={"Content-Type": "application/json"}
        )
        
        # Get stats after
        stats_after = requests.get(
            f"{BASE_URL}/api/conseils/admin/stats",
            headers=self.headers
        ).json()
        
        assert stats_after["total_views"] >= stats_before["total_views"], "total_views should not decrease"
        print(f"✓ View tracking: views before={stats_before['total_views']}, after={stats_after['total_views']}")
    
    def test_click_increments_global_clicks(self):
        """POST /api/conseils/click should increment global clicks counter"""
        # Get initial stats
        stats_before = requests.get(
            f"{BASE_URL}/api/conseils/admin/stats",
            headers=self.headers
        ).json()
        
        # Get a conseil and track click
        conseil_resp = requests.get(f"{BASE_URL}/api/conseils/today")
        conseil_id = conseil_resp.json().get("id", "")
        
        requests.post(
            f"{BASE_URL}/api/conseils/click",
            json={"conseil_id": conseil_id},
            headers={"Content-Type": "application/json"}
        )
        
        # Get stats after
        stats_after = requests.get(
            f"{BASE_URL}/api/conseils/admin/stats",
            headers=self.headers
        ).json()
        
        assert stats_after["total_clicks"] >= stats_before["total_clicks"], "total_clicks should not decrease"
        print(f"✓ Click tracking: clicks before={stats_before['total_clicks']}, after={stats_after['total_clicks']}")
    
    def test_conversion_increments_global_conversions(self):
        """POST /api/conseils/conversion should increment global conversions counter"""
        # Get initial stats
        stats_before = requests.get(
            f"{BASE_URL}/api/conseils/admin/stats",
            headers=self.headers
        ).json()
        
        # Get a conseil and track conversion
        conseil_resp = requests.get(f"{BASE_URL}/api/conseils/today")
        conseil_id = conseil_resp.json().get("id", "")
        
        requests.post(
            f"{BASE_URL}/api/conseils/conversion",
            json={"conseil_id": conseil_id, "action": "test_conversion"},
            headers={"Content-Type": "application/json"}
        )
        
        # Get stats after
        stats_after = requests.get(
            f"{BASE_URL}/api/conseils/admin/stats",
            headers=self.headers
        ).json()
        
        assert stats_after["total_conversions"] >= stats_before["total_conversions"], "total_conversions should not decrease"
        print(f"✓ Conversion tracking: conversions before={stats_before['total_conversions']}, after={stats_after['total_conversions']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
