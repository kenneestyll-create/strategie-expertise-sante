"""
Test Analytics Dashboard API endpoints
Tests for GET /api/admin/analytics with different period parameters
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAnalyticsEndpoint:
    """Test GET /api/admin/analytics endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as admin to get token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Admin login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.token = token
        else:
            pytest.skip(f"Admin login failed: {login_response.status_code}")

    def test_analytics_30d_default(self):
        """Test analytics with default 30d period"""
        response = self.session.get(f"{BASE_URL}/api/admin/analytics?period=30d")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert "kpis" in data, "Response should contain 'kpis'"
        assert "time_series" in data, "Response should contain 'time_series'"
        assert "packages" in data, "Response should contain 'packages'"
        assert "analyse_types" in data, "Response should contain 'analyse_types'"
        
        # Verify KPIs structure
        kpis = data["kpis"]
        assert "total_contacts" in kpis, "KPIs should contain 'total_contacts'"
        assert "total_clients" in kpis, "KPIs should contain 'total_clients'"
        assert "total_analyses" in kpis, "KPIs should contain 'total_analyses'"
        assert "total_revenue" in kpis, "KPIs should contain 'total_revenue'"
        assert "pending_revenue" in kpis, "KPIs should contain 'pending_revenue'"
        assert "conversion_rate" in kpis, "KPIs should contain 'conversion_rate'"
        
        # Verify time_series has correct length (should have 30 days)
        time_series = data["time_series"]
        assert isinstance(time_series, list), "time_series should be a list"
        assert len(time_series) >= 1, "time_series should have at least 1 entry"
        assert len(time_series) <= 31, "time_series should have at most 31 entries for 30d"
        
        # Verify time_series entry structure
        if time_series:
            entry = time_series[0]
            assert "date" in entry, "time_series entry should have 'date'"
            assert "contacts" in entry, "time_series entry should have 'contacts'"
            assert "revenue" in entry, "time_series entry should have 'revenue'"
            assert "analyses" in entry, "time_series entry should have 'analyses'"
            assert "clients" in entry, "time_series entry should have 'clients'"
        
        print(f"Analytics 30d: {len(time_series)} days, {kpis['total_contacts']} contacts, {kpis['total_revenue']}€ revenue")

    def test_analytics_7d_period(self):
        """Test analytics with 7d period - should return shorter time series"""
        response = self.session.get(f"{BASE_URL}/api/admin/analytics?period=7d")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert "kpis" in data
        assert "time_series" in data
        
        # Verify time_series has correct length for 7 days
        time_series = data["time_series"]
        assert isinstance(time_series, list)
        assert len(time_series) >= 1, "time_series should have at least 1 entry for 7d"
        assert len(time_series) <= 8, "time_series should have at most 8 entries for 7d"
        
        print(f"Analytics 7d: {len(time_series)} days in time series")

    def test_analytics_90d_period(self):
        """Test analytics with 90d period - should return longer time series"""
        response = self.session.get(f"{BASE_URL}/api/admin/analytics?period=90d")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert "kpis" in data
        assert "time_series" in data
        
        # Verify time_series has correct length for 90 days
        time_series = data["time_series"]
        assert isinstance(time_series, list)
        assert len(time_series) >= 1, "time_series should have at least 1 entry for 90d"
        assert len(time_series) <= 91, "time_series should have at most 91 entries for 90d"
        
        print(f"Analytics 90d: {len(time_series)} days in time series")

    def test_analytics_packages_structure(self):
        """Test packages distribution in analytics response"""
        response = self.session.get(f"{BASE_URL}/api/admin/analytics?period=30d")
        
        assert response.status_code == 200
        data = response.json()
        
        packages = data.get("packages", [])
        assert isinstance(packages, list), "packages should be a list"
        
        # If there are packages, verify structure
        for pkg in packages:
            assert "name" in pkg, "Package should have 'name'"
            assert "count" in pkg, "Package should have 'count'"
            assert "revenue" in pkg, "Package should have 'revenue'"
            assert isinstance(pkg["count"], int), "Package count should be an integer"
            assert isinstance(pkg["revenue"], (int, float)), "Package revenue should be a number"
        
        print(f"Analytics packages: {len(packages)} package types found")

    def test_analytics_analyse_types_structure(self):
        """Test analyse_types distribution in analytics response"""
        response = self.session.get(f"{BASE_URL}/api/admin/analytics?period=30d")
        
        assert response.status_code == 200
        data = response.json()
        
        analyse_types = data.get("analyse_types", [])
        assert isinstance(analyse_types, list), "analyse_types should be a list"
        
        # If there are analyse types, verify structure
        for at in analyse_types:
            assert "type" in at, "Analyse type should have 'type'"
            assert "count" in at, "Analyse type should have 'count'"
            assert isinstance(at["count"], int), "Analyse type count should be an integer"
        
        print(f"Analytics analyse_types: {len(analyse_types)} types found")

    def test_analytics_requires_auth(self):
        """Test that analytics endpoint requires authentication"""
        # Create a new session without auth
        unauth_session = requests.Session()
        response = unauth_session.get(f"{BASE_URL}/api/admin/analytics?period=30d")
        
        # Should return 401 or 403 without authentication
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("Analytics endpoint correctly requires authentication")

    def test_analytics_kpis_values_are_numbers(self):
        """Test that KPI values are proper numbers"""
        response = self.session.get(f"{BASE_URL}/api/admin/analytics?period=30d")
        
        assert response.status_code == 200
        kpis = response.json().get("kpis", {})
        
        # All KPI values should be numbers
        numeric_fields = [
            "total_contacts", "total_clients", "total_analyses", 
            "total_dossiers", "total_forum_users", "total_chatbot_sessions",
            "total_revenue", "pending_revenue", "conversion_rate"
        ]
        
        for field in numeric_fields:
            value = kpis.get(field)
            assert value is not None, f"KPI '{field}' should exist"
            assert isinstance(value, (int, float)), f"KPI '{field}' should be a number, got {type(value)}"
        
        print(f"All KPI values are valid numbers")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
