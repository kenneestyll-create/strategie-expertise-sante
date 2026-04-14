"""
Test Admin Bypass Features for StrategiIA, Dossier Express, and Auto-diagnostic
Tests the admin mode toggle functionality that allows testing without paywalls.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD


class TestAdminAuthentication:
    """Test admin login and token generation"""
    
    def test_admin_login_success(self):
        """Admin login should return access_token with is_admin=true"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert len(data["access_token"]) > 0, "Token should not be empty"
        print(f"PASS: Admin login successful, token received")
        return data["access_token"]
    
    def test_admin_login_invalid_credentials(self):
        """Invalid credentials should return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@email.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"PASS: Invalid credentials correctly rejected with 401")


class TestStrategiIAAdminBypass:
    """Test StrategiIA admin bypass endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed - skipping authenticated tests")
        return response.json()["access_token"]
    
    def test_register_email_with_admin_test_flag(self, admin_token):
        """POST /api/strategiia/register-email with admin_test=true should return remaining=999"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/register-email",
            json={"email": "test@example.com", "admin_test": True},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Response should have success=true"
        assert data.get("remaining") == 999, f"Admin test should return remaining=999, got {data.get('remaining')}"
        assert data.get("admin_test") == True, "Response should have admin_test=true"
        print(f"PASS: register-email with admin_test returns remaining=999 and admin_test=true")
    
    def test_register_email_without_admin_token(self):
        """POST /api/strategiia/register-email without admin token should work normally (not admin_test)"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/register-email",
            json={"email": "normaluser@example.com", "admin_test": True}  # admin_test ignored without token
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        # Without admin token, admin_test flag should be ignored
        assert data.get("remaining") != 999 or data.get("admin_test") != True, \
            "Without admin token, should not get admin_test=true with remaining=999"
        print(f"PASS: register-email without admin token works normally (remaining={data.get('remaining')})")
    
    def test_admin_bypass_premium_with_token(self, admin_token):
        """POST /api/strategiia/admin-bypass-premium with admin token should return job_id"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json={
                "situation": "Test situation for admin bypass - accident du travail",
                "type_dossier": "at",
                "regime": "general"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "job_id" in data, "Response should contain job_id"
        assert data.get("admin_test") == True, "Response should have admin_test=true"
        assert data.get("status") == "pending", "Status should be pending"
        print(f"PASS: admin-bypass-premium returns job_id={data['job_id']} and admin_test=true")
    
    def test_admin_bypass_premium_without_token(self):
        """POST /api/strategiia/admin-bypass-premium without token should return 401/403"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json={
                "situation": "Test situation",
                "type_dossier": "at",
                "regime": "general"
            }
        )
        assert response.status_code in [401, 403], \
            f"Expected 401 or 403 without admin token, got {response.status_code}"
        print(f"PASS: admin-bypass-premium correctly rejects request without token ({response.status_code})")
    
    def test_admin_bypass_premium_with_invalid_token(self):
        """POST /api/strategiia/admin-bypass-premium with invalid token should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json={
                "situation": "Test situation",
                "type_dossier": "at",
                "regime": "general"
            },
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code == 401, \
            f"Expected 401 with invalid token, got {response.status_code}"
        print(f"PASS: admin-bypass-premium correctly rejects invalid token (401)")


class TestDossierExpressAdminBypass:
    """Test Dossier Express admin bypass endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed - skipping authenticated tests")
        return response.json()["access_token"]
    
    def test_dossier_express_admin_bypass_with_token(self, admin_token):
        """POST /api/dossier-express/admin-bypass with admin token should return dossier_id"""
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Admin Test User",
                "situation": "Test situation for dossier express admin bypass - maladie professionnelle",
                "type_dossier": "Maladie professionnelle (MP)",
                "regime": "Régime général",
                "documents_text": "Test document content",
                "premium_pdf": False
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Response should have success=true"
        assert "dossier_id" in data, "Response should contain dossier_id"
        assert data.get("admin_test") == True, "Response should have admin_test=true"
        print(f"PASS: dossier-express/admin-bypass returns dossier_id={data['dossier_id']} and admin_test=true")
        return data["dossier_id"]
    
    def test_dossier_express_admin_bypass_without_token(self):
        """POST /api/dossier-express/admin-bypass without token should return 401/403"""
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Test User",
                "situation": "Test situation",
                "type_dossier": "Accident du travail (AT)",
                "regime": "Régime général"
            }
        )
        assert response.status_code in [401, 403], \
            f"Expected 401 or 403 without admin token, got {response.status_code}"
        print(f"PASS: dossier-express/admin-bypass correctly rejects request without token ({response.status_code})")
    
    def test_dossier_express_admin_bypass_with_invalid_token(self):
        """POST /api/dossier-express/admin-bypass with invalid token should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Test User",
                "situation": "Test situation",
                "type_dossier": "Accident du travail (AT)",
                "regime": "Régime général"
            },
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code == 401, \
            f"Expected 401 with invalid token, got {response.status_code}"
        print(f"PASS: dossier-express/admin-bypass correctly rejects invalid token (401)")
    
    def test_dossier_express_status_polling(self, admin_token):
        """Test that dossier status can be polled after admin bypass submission"""
        # First create a dossier via admin bypass
        create_response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Status Test User",
                "situation": "Test situation for status polling",
                "type_dossier": "Accident du travail (AT)",
                "regime": "Régime général"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200
        dossier_id = create_response.json()["dossier_id"]
        
        # Poll status
        status_response = requests.get(f"{BASE_URL}/api/dossier-express/status/{dossier_id}")
        assert status_response.status_code == 200, f"Expected 200, got {status_response.status_code}"
        data = status_response.json()
        assert "status" in data, "Response should contain status"
        assert data["status"] in ["processing", "completed", "error"], \
            f"Status should be processing/completed/error, got {data['status']}"
        print(f"PASS: dossier-express status polling works, status={data['status']}")


class TestNormalUserBehavior:
    """Test that normal users (without admin token) have normal behavior"""
    
    def test_register_email_normal_quota(self):
        """Normal user should get quota < 999"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/register-email",
            json={"email": "normaluser123@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        remaining = data.get("remaining")
        assert remaining is not None, "Response should contain remaining"
        assert remaining <= 3, f"Normal user should have remaining <= 3, got {remaining}"
        assert data.get("admin_test") != True, "Normal user should not have admin_test=true"
        print(f"PASS: Normal user gets normal quota (remaining={remaining})")
    
    def test_strategiia_analyze_normal_flow(self):
        """Normal analyze endpoint should work without admin token"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/analyze",
            json={
                "situation": "Test situation for normal analysis",
                "type_dossier": "at",
                "regime": "general",
                "premium": False,
                "email": "normaltest@example.com"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Should return job_id for async processing
        assert "job_id" in data or "quota_exceeded" in data, \
            "Response should contain job_id or quota_exceeded"
        print(f"PASS: Normal analyze flow works, response keys: {list(data.keys())}")


class TestStrategiIAStatusPolling:
    """Test StrategiIA job status polling"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed - skipping authenticated tests")
        return response.json()["access_token"]
    
    def test_strategiia_status_polling(self, admin_token):
        """Test that job status can be polled after admin bypass submission"""
        # First create a job via admin bypass
        create_response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            json={
                "situation": "Test situation for status polling - accident du travail avec séquelles",
                "type_dossier": "at",
                "regime": "general"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]
        
        # Poll status
        status_response = requests.get(f"{BASE_URL}/api/strategiia/status/{job_id}")
        assert status_response.status_code == 200, f"Expected 200, got {status_response.status_code}"
        data = status_response.json()
        assert "status" in data, "Response should contain status"
        assert data["status"] in ["pending", "done", "error"], \
            f"Status should be pending/done/error, got {data['status']}"
        print(f"PASS: strategiia status polling works, status={data['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
