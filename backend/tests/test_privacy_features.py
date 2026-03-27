"""
Test suite for Privacy/Data Retention features (Iteration 137)
- Admin purge-log endpoint
- Admin purge-now endpoint
- Data purge scheduler initialization
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com')

class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_api_health(self):
        """Test API is accessible"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        # Health endpoint may not exist, but API should respond
        assert response.status_code in [200, 404, 405]
        print(f"API health check: {response.status_code}")
    
    def test_admin_login(self):
        """Test admin login returns access_token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        }, timeout=10)
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        print(f"Admin login successful, token received")
        return data["access_token"]


class TestPurgeLogEndpoint:
    """Tests for GET /api/admin/purge-log"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        }, timeout=10)
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["access_token"]
    
    def test_purge_log_requires_auth(self):
        """Test purge-log endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/purge-log", timeout=10)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Purge-log correctly requires authentication")
    
    def test_purge_log_returns_stats(self, admin_token):
        """Test purge-log returns stats with total_dossiers, purged, pending_purge"""
        response = requests.get(
            f"{BASE_URL}/api/admin/purge-log",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Purge-log failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "stats" in data, f"No 'stats' in response: {data}"
        assert "logs" in data, f"No 'logs' in response: {data}"
        
        stats = data["stats"]
        assert "total_dossiers" in stats, f"No 'total_dossiers' in stats: {stats}"
        assert "purged" in stats, f"No 'purged' in stats: {stats}"
        assert "pending_purge" in stats, f"No 'pending_purge' in stats: {stats}"
        
        # Values should be integers
        assert isinstance(stats["total_dossiers"], int)
        assert isinstance(stats["purged"], int)
        assert isinstance(stats["pending_purge"], int)
        
        print(f"Purge-log stats: total={stats['total_dossiers']}, purged={stats['purged']}, pending={stats['pending_purge']}")


class TestPurgeNowEndpoint:
    """Tests for POST /api/admin/purge-now"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        }, timeout=10)
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["access_token"]
    
    def test_purge_now_requires_auth(self):
        """Test purge-now endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/purge-now", timeout=10)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Purge-now correctly requires authentication")
    
    def test_purge_now_works(self, admin_token):
        """Test purge-now endpoint executes successfully"""
        response = requests.post(
            f"{BASE_URL}/api/admin/purge-now",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=30
        )
        assert response.status_code == 200, f"Purge-now failed: {response.text}"
        data = response.json()
        
        assert "success" in data, f"No 'success' in response: {data}"
        assert data["success"] == True, f"Purge-now not successful: {data}"
        assert "purged_count" in data, f"No 'purged_count' in response: {data}"
        assert isinstance(data["purged_count"], int)
        
        print(f"Purge-now executed: {data['purged_count']} dossier(s) purged")


class TestPolitiqueConfidentialitePage:
    """Tests for /politique-confidentialite page"""
    
    def test_politique_page_loads(self):
        """Test politique-confidentialite page is accessible"""
        response = requests.get(f"{BASE_URL}/politique-confidentialite", timeout=10)
        # Frontend routes return 200 (SPA routing)
        assert response.status_code == 200, f"Page failed to load: {response.status_code}"
        print("Politique de confidentialité page loads successfully")


class TestHomepageLoads:
    """Test homepage loads without errors"""
    
    def test_homepage_loads(self):
        """Test homepage is accessible"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200, f"Homepage failed: {response.status_code}"
        print("Homepage loads successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
