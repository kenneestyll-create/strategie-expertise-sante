"""
VIP Guest System Tests
Tests for VIP guest management, authentication, and session handling
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"
TEST_VIP_EMAIL = "test_vip_pytest@test.com"
TEST_VIP_NAME = "Test VIP Pytest"


class TestVIPGuestSystem:
    """VIP Guest System API Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session and get admin token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Get admin token
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_res.status_code == 200:
            self.admin_token = login_res.json().get("access_token")
            self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        else:
            pytest.skip(f"Admin login failed: {login_res.status_code}")
        
        yield
        
        # Cleanup: delete test VIP guest if created
        try:
            guests_res = self.session.get(f"{BASE_URL}/api/admin/vip-guests", headers=self.admin_headers)
            if guests_res.status_code == 200:
                for guest in guests_res.json():
                    if guest.get("email") == TEST_VIP_EMAIL:
                        self.session.delete(f"{BASE_URL}/api/admin/vip-guests/{guest['id']}", headers=self.admin_headers)
        except Exception:
            pass

    # ==================== ADMIN ENDPOINTS ====================
    
    def test_create_vip_guest_success(self):
        """POST /api/admin/vip-guests creates a VIP guest with name, email, motif, token, expires_at"""
        payload = {
            "name": TEST_VIP_NAME,
            "email": TEST_VIP_EMAIL,
            "motif": "Test partenaire pytest",
            "expires_days": 30
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json=payload,
            headers=self.admin_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "id" in data
        assert "token" in data
        assert data.get("name") == TEST_VIP_NAME
        assert data.get("email") == TEST_VIP_EMAIL.lower()
        assert "expires_at" in data
        
        # Store for later tests
        self.created_guest_id = data["id"]
        self.created_guest_token = data["token"]
        print(f"✓ VIP guest created: {data['name']} with token {data['token'][:10]}...")

    def test_create_vip_guest_duplicate_email_returns_409(self):
        """POST /api/admin/vip-guests returns 409 if email already exists"""
        # First create a guest
        payload = {
            "name": TEST_VIP_NAME,
            "email": TEST_VIP_EMAIL,
            "motif": "First creation"
        }
        
        first_res = self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json=payload,
            headers=self.admin_headers
        )
        assert first_res.status_code == 200
        
        # Try to create again with same email
        duplicate_res = self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json=payload,
            headers=self.admin_headers
        )
        
        assert duplicate_res.status_code == 409, f"Expected 409, got {duplicate_res.status_code}"
        print("✓ Duplicate email correctly returns 409")

    def test_list_vip_guests(self):
        """GET /api/admin/vip-guests returns list of all VIP guests"""
        # First create a guest
        self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json={"name": TEST_VIP_NAME, "email": TEST_VIP_EMAIL},
            headers=self.admin_headers
        )
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/vip-guests",
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Find our test guest
        test_guest = next((g for g in data if g.get("email") == TEST_VIP_EMAIL.lower()), None)
        assert test_guest is not None, "Test guest not found in list"
        assert "id" in test_guest
        assert "name" in test_guest
        assert "email" in test_guest
        assert "token" in test_guest
        assert "active" in test_guest
        assert "created_at" in test_guest
        assert "expires_at" in test_guest
        print(f"✓ VIP guests list returned {len(data)} guests")

    def test_toggle_vip_guest_status(self):
        """PUT /api/admin/vip-guests/{id}/toggle toggles active status"""
        # Create a guest
        create_res = self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json={"name": TEST_VIP_NAME, "email": TEST_VIP_EMAIL},
            headers=self.admin_headers
        )
        guest_id = create_res.json()["id"]
        
        # Toggle to inactive
        toggle_res = self.session.put(
            f"{BASE_URL}/api/admin/vip-guests/{guest_id}/toggle",
            headers=self.admin_headers
        )
        
        assert toggle_res.status_code == 200
        data = toggle_res.json()
        assert data.get("success") == True
        assert data.get("active") == False
        print("✓ VIP guest toggled to inactive")
        
        # Toggle back to active
        toggle_res2 = self.session.put(
            f"{BASE_URL}/api/admin/vip-guests/{guest_id}/toggle",
            headers=self.admin_headers
        )
        
        assert toggle_res2.status_code == 200
        assert toggle_res2.json().get("active") == True
        print("✓ VIP guest toggled back to active")

    def test_delete_vip_guest(self):
        """DELETE /api/admin/vip-guests/{id} deletes a guest"""
        # Create a guest
        create_res = self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json={"name": TEST_VIP_NAME, "email": TEST_VIP_EMAIL},
            headers=self.admin_headers
        )
        guest_id = create_res.json()["id"]
        
        # Delete the guest
        delete_res = self.session.delete(
            f"{BASE_URL}/api/admin/vip-guests/{guest_id}",
            headers=self.admin_headers
        )
        
        assert delete_res.status_code == 200
        assert delete_res.json().get("success") == True
        print("✓ VIP guest deleted successfully")
        
        # Verify guest is gone
        list_res = self.session.get(
            f"{BASE_URL}/api/admin/vip-guests",
            headers=self.admin_headers
        )
        guests = list_res.json()
        assert not any(g.get("id") == guest_id for g in guests), "Guest still exists after deletion"
        print("✓ Verified guest no longer in list")

    # ==================== PUBLIC VIP ENDPOINTS ====================
    
    def test_vip_verify_success(self):
        """POST /api/vip/verify with correct token + email returns success and sets httpOnly cookie"""
        # Create a guest
        create_res = self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json={"name": TEST_VIP_NAME, "email": TEST_VIP_EMAIL},
            headers=self.admin_headers
        )
        token = create_res.json()["token"]
        
        # Verify with correct credentials
        verify_session = requests.Session()
        verify_res = verify_session.post(
            f"{BASE_URL}/api/vip/verify",
            json={"token": token, "email": TEST_VIP_EMAIL}
        )
        
        assert verify_res.status_code == 200, f"Expected 200, got {verify_res.status_code}: {verify_res.text}"
        data = verify_res.json()
        assert data.get("success") == True
        assert data.get("name") == TEST_VIP_NAME
        assert "guest_id" in data
        
        # Check cookie was set
        cookies = verify_session.cookies.get_dict()
        assert "vip_session" in cookies, "vip_session cookie not set"
        print(f"✓ VIP verify success, cookie set: vip_session={cookies['vip_session'][:20]}...")

    def test_vip_verify_wrong_email_returns_403(self):
        """POST /api/vip/verify with wrong email returns 403"""
        # Create a guest
        create_res = self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json={"name": TEST_VIP_NAME, "email": TEST_VIP_EMAIL},
            headers=self.admin_headers
        )
        token = create_res.json()["token"]
        
        # Verify with wrong email
        verify_res = requests.post(
            f"{BASE_URL}/api/vip/verify",
            json={"token": token, "email": "wrong@email.com"}
        )
        
        assert verify_res.status_code == 403, f"Expected 403, got {verify_res.status_code}"
        print("✓ Wrong email correctly returns 403")

    def test_vip_verify_wrong_token_returns_403(self):
        """POST /api/vip/verify with wrong token returns 403"""
        # Create a guest
        self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json={"name": TEST_VIP_NAME, "email": TEST_VIP_EMAIL},
            headers=self.admin_headers
        )
        
        # Verify with wrong token
        verify_res = requests.post(
            f"{BASE_URL}/api/vip/verify",
            json={"token": "invalid_token_12345", "email": TEST_VIP_EMAIL}
        )
        
        assert verify_res.status_code == 403, f"Expected 403, got {verify_res.status_code}"
        print("✓ Wrong token correctly returns 403")

    def test_vip_session_with_valid_cookie(self):
        """GET /api/vip/session returns active:true when valid cookie present"""
        # Create and verify a guest
        create_res = self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json={"name": TEST_VIP_NAME, "email": TEST_VIP_EMAIL},
            headers=self.admin_headers
        )
        token = create_res.json()["token"]
        
        # Verify to get cookie
        verify_session = requests.Session()
        verify_session.post(
            f"{BASE_URL}/api/vip/verify",
            json={"token": token, "email": TEST_VIP_EMAIL}
        )
        
        # Check session
        session_res = verify_session.get(f"{BASE_URL}/api/vip/session")
        
        assert session_res.status_code == 200
        data = session_res.json()
        assert data.get("active") == True
        assert data.get("name") == TEST_VIP_NAME
        assert data.get("email") == TEST_VIP_EMAIL.lower()
        assert "guest_id" in data
        print("✓ VIP session returns active:true with valid cookie")

    def test_vip_session_without_cookie(self):
        """GET /api/vip/session returns active:false when no cookie"""
        # Fresh session without any cookies
        fresh_session = requests.Session()
        session_res = fresh_session.get(f"{BASE_URL}/api/vip/session")
        
        assert session_res.status_code == 200
        data = session_res.json()
        assert data.get("active") == False
        print("✓ VIP session returns active:false without cookie")

    def test_vip_logout_clears_session(self):
        """POST /api/vip/logout clears the session"""
        # Create and verify a guest
        create_res = self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json={"name": TEST_VIP_NAME, "email": TEST_VIP_EMAIL},
            headers=self.admin_headers
        )
        token = create_res.json()["token"]
        
        # Verify to get cookie
        verify_session = requests.Session()
        verify_session.post(
            f"{BASE_URL}/api/vip/verify",
            json={"token": token, "email": TEST_VIP_EMAIL}
        )
        
        # Confirm session is active
        session_res = verify_session.get(f"{BASE_URL}/api/vip/session")
        assert session_res.json().get("active") == True
        
        # Logout
        logout_res = verify_session.post(f"{BASE_URL}/api/vip/logout")
        assert logout_res.status_code == 200
        assert logout_res.json().get("success") == True
        
        # Verify session is now inactive
        session_res2 = verify_session.get(f"{BASE_URL}/api/vip/session")
        assert session_res2.json().get("active") == False
        print("✓ VIP logout clears session successfully")

    def test_vip_verify_inactive_guest_returns_403(self):
        """POST /api/vip/verify with inactive guest returns 403"""
        # Create a guest
        create_res = self.session.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json={"name": TEST_VIP_NAME, "email": TEST_VIP_EMAIL},
            headers=self.admin_headers
        )
        guest_id = create_res.json()["id"]
        token = create_res.json()["token"]
        
        # Deactivate the guest
        self.session.put(
            f"{BASE_URL}/api/admin/vip-guests/{guest_id}/toggle",
            headers=self.admin_headers
        )
        
        # Try to verify
        verify_res = requests.post(
            f"{BASE_URL}/api/vip/verify",
            json={"token": token, "email": TEST_VIP_EMAIL}
        )
        
        assert verify_res.status_code == 403, f"Expected 403, got {verify_res.status_code}"
        print("✓ Inactive guest correctly returns 403 on verify")


class TestVIPAdminAuth:
    """Test that admin endpoints require authentication"""
    
    def test_list_vip_guests_requires_auth(self):
        """GET /api/admin/vip-guests requires admin auth"""
        response = requests.get(f"{BASE_URL}/api/admin/vip-guests")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ List VIP guests requires auth")

    def test_create_vip_guest_requires_auth(self):
        """POST /api/admin/vip-guests requires admin auth"""
        response = requests.post(
            f"{BASE_URL}/api/admin/vip-guests",
            json={"name": "Test", "email": "test@test.com"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Create VIP guest requires auth")

    def test_toggle_vip_guest_requires_auth(self):
        """PUT /api/admin/vip-guests/{id}/toggle requires admin auth"""
        response = requests.put(f"{BASE_URL}/api/admin/vip-guests/fake-id/toggle")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Toggle VIP guest requires auth")

    def test_delete_vip_guest_requires_auth(self):
        """DELETE /api/admin/vip-guests/{id} requires admin auth"""
        response = requests.delete(f"{BASE_URL}/api/admin/vip-guests/fake-id")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Delete VIP guest requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
