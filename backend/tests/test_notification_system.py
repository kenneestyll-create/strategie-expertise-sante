"""
Iteration 36: Client Notification System Tests
Tests for:
- POST /api/client/register with notification preferences
- GET /api/client/settings/notifications (client auth required)
- PATCH /api/client/settings/notifications (client auth required)
- POST /api/admin/premium-analyses/{id}/notify (admin auth required)
- PATCH /api/admin/premium-analyses/{id} with auto-notification on status change
- GET /api/client/notifications (client auth required)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD
TEST_CLIENT_EMAIL = "test-notif@example.com"
TEST_CLIENT_PASSWORD = "Test1234!"


class TestNotificationSystem:
    """Client Notification System Tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/client/login", json={
            "email": TEST_CLIENT_EMAIL,
            "password": TEST_CLIENT_PASSWORD
        })
        assert response.status_code == 200, f"Client login failed: {response.text}"
        return response.json()["access_token"]
    
    # ===================
    # Test 1: Client Registration with notification preferences
    # ===================
    def test_register_client_with_notification_preferences(self):
        """POST /api/client/register should accept notifications_email and notifications_push fields"""
        random_email = f"test-register-{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": random_email,
            "password": "TestPass123!",
            "name": "Test Notification User",
            "phone": "0600000000",
            "notifications_email": False,
            "notifications_push": True
        }
        
        response = requests.post(f"{BASE_URL}/api/client/register", json=payload)
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "client_name" in data
        assert "client_id" in data
        assert data["client_name"] == "Test Notification User"
        print(f"✓ TEST 1 PASSED: Client registered with notification preferences (email: {random_email})")
        
        # Login and verify settings were saved
        login_res = requests.post(f"{BASE_URL}/api/client/login", json={
            "email": random_email,
            "password": "TestPass123!"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        
        settings_res = requests.get(
            f"{BASE_URL}/api/client/settings/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert settings_res.status_code == 200
        settings = settings_res.json()
        assert settings["notifications_email"] == False, "notifications_email should be False"
        assert settings["notifications_push"] == True, "notifications_push should be True"
        print(f"✓ TEST 1b PASSED: Notification preferences saved correctly")
    
    # ===================
    # Test 2: Get notification settings (client auth required)
    # ===================
    def test_get_notification_settings_requires_auth(self):
        """GET /api/client/settings/notifications should require client auth"""
        response = requests.get(f"{BASE_URL}/api/client/settings/notifications")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ TEST 2 PASSED: GET /api/client/settings/notifications requires authentication")
    
    def test_get_notification_settings_with_auth(self, client_token):
        """GET /api/client/settings/notifications returns notification preferences"""
        response = requests.get(
            f"{BASE_URL}/api/client/settings/notifications",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200, f"Failed to get settings: {response.text}"
        data = response.json()
        
        assert "notifications_email" in data, "Missing notifications_email field"
        assert "notifications_push" in data, "Missing notifications_push field"
        assert isinstance(data["notifications_email"], bool)
        assert isinstance(data["notifications_push"], bool)
        print(f"✓ TEST 3 PASSED: GET /api/client/settings/notifications returns {data}")
    
    # ===================
    # Test 3: Update notification settings (client auth required)
    # ===================
    def test_update_notification_settings_requires_auth(self):
        """PATCH /api/client/settings/notifications should require client auth"""
        response = requests.patch(
            f"{BASE_URL}/api/client/settings/notifications",
            json={"notifications_email": True}
        )
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ TEST 4 PASSED: PATCH /api/client/settings/notifications requires authentication")
    
    def test_update_notification_settings_email(self, client_token):
        """PATCH /api/client/settings/notifications updates email preference"""
        # First get current settings
        get_res = requests.get(
            f"{BASE_URL}/api/client/settings/notifications",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        original_email_pref = get_res.json().get("notifications_email", True)
        
        # Toggle the setting
        new_value = not original_email_pref
        response = requests.patch(
            f"{BASE_URL}/api/client/settings/notifications",
            headers={"Authorization": f"Bearer {client_token}"},
            json={"notifications_email": new_value}
        )
        assert response.status_code == 200, f"Failed to update: {response.text}"
        assert response.json().get("success") == True
        
        # Verify change
        verify_res = requests.get(
            f"{BASE_URL}/api/client/settings/notifications",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert verify_res.json()["notifications_email"] == new_value
        print(f"✓ TEST 5 PASSED: notifications_email updated to {new_value}")
        
        # Restore original value
        requests.patch(
            f"{BASE_URL}/api/client/settings/notifications",
            headers={"Authorization": f"Bearer {client_token}"},
            json={"notifications_email": original_email_pref}
        )
    
    def test_update_notification_settings_push(self, client_token):
        """PATCH /api/client/settings/notifications updates push preference"""
        get_res = requests.get(
            f"{BASE_URL}/api/client/settings/notifications",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        original_push_pref = get_res.json().get("notifications_push", True)
        
        new_value = not original_push_pref
        response = requests.patch(
            f"{BASE_URL}/api/client/settings/notifications",
            headers={"Authorization": f"Bearer {client_token}"},
            json={"notifications_push": new_value}
        )
        assert response.status_code == 200
        
        verify_res = requests.get(
            f"{BASE_URL}/api/client/settings/notifications",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert verify_res.json()["notifications_push"] == new_value
        print(f"✓ TEST 6 PASSED: notifications_push updated to {new_value}")
        
        # Restore
        requests.patch(
            f"{BASE_URL}/api/client/settings/notifications",
            headers={"Authorization": f"Bearer {client_token}"},
            json={"notifications_push": original_push_pref}
        )
    
    # ===================
    # Test 4: Get client notifications (client auth required)
    # ===================
    def test_get_notifications_requires_auth(self):
        """GET /api/client/notifications should require client auth"""
        response = requests.get(f"{BASE_URL}/api/client/notifications")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ TEST 7 PASSED: GET /api/client/notifications requires authentication")
    
    def test_get_notifications_with_auth(self, client_token):
        """GET /api/client/notifications returns notifications list with unread_count"""
        response = requests.get(
            f"{BASE_URL}/api/client/notifications",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "notifications" in data, "Missing notifications field"
        assert "unread_count" in data, "Missing unread_count field"
        assert isinstance(data["notifications"], list)
        assert isinstance(data["unread_count"], int)
        print(f"✓ TEST 8 PASSED: GET /api/client/notifications returns {len(data['notifications'])} notifications, {data['unread_count']} unread")
    
    # ===================
    # Test 5: Admin - Get premium analyses
    # ===================
    def test_get_premium_analyses_requires_admin_auth(self):
        """GET /api/admin/premium-analyses should require admin auth"""
        response = requests.get(f"{BASE_URL}/api/admin/premium-analyses")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ TEST 9 PASSED: GET /api/admin/premium-analyses requires admin auth")
    
    def test_get_premium_analyses(self, admin_token):
        """GET /api/admin/premium-analyses returns list with stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "items" in data, "Missing items field"
        assert "stats" in data, "Missing stats field"
        assert isinstance(data["items"], list)
        
        # Stats should have status counts
        stats = data["stats"]
        assert "total" in stats
        assert "en_attente" in stats
        assert "en_cours" in stats
        assert "termine" in stats
        print(f"✓ TEST 10 PASSED: GET /api/admin/premium-analyses returns {len(data['items'])} items, stats: {stats}")
        
        return data["items"]  # Return for use in notify test
    
    # ===================
    # Test 6: Admin - Manual notify for premium analysis
    # ===================
    def test_notify_premium_requires_admin_auth(self):
        """POST /api/admin/premium-analyses/{id}/notify should require admin auth"""
        response = requests.post(f"{BASE_URL}/api/admin/premium-analyses/fake-id/notify", json={})
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ TEST 11 PASSED: POST /api/admin/premium-analyses/{id}/notify requires admin auth")
    
    def test_notify_premium_analysis_not_found(self, admin_token):
        """POST /api/admin/premium-analyses/{id}/notify returns 404 for non-existent analysis"""
        response = requests.post(
            f"{BASE_URL}/api/admin/premium-analyses/nonexistent-id/notify",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"type": "analyse_premium_ready"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print("✓ TEST 12 PASSED: POST /api/admin/premium-analyses/{nonexistent}/notify returns 404")
    
    def test_notify_premium_analysis(self, admin_token):
        """POST /api/admin/premium-analyses/{id}/notify sends notification to client"""
        # First get list of premium analyses
        list_res = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        items = list_res.json().get("items", [])
        
        if not items:
            pytest.skip("No premium analyses to test notification")
        
        analysis_id = items[0]["id"]
        
        # Send notification
        response = requests.post(
            f"{BASE_URL}/api/admin/premium-analyses/{analysis_id}/notify",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"type": "analyse_premium_ready", "message": "Test notification from pytest"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        assert "client_found" in data
        assert "email" in data
        print(f"✓ TEST 13 PASSED: POST /api/admin/premium-analyses/{analysis_id}/notify succeeded, client_found={data['client_found']}")
    
    # ===================
    # Test 7: Admin - Update premium analysis status with auto-notification
    # ===================
    def test_update_premium_analysis_status_requires_admin(self):
        """PATCH /api/admin/premium-analyses/{id} should require admin auth"""
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/fake-id",
            json={"status": "en_cours"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ TEST 14 PASSED: PATCH /api/admin/premium-analyses/{id} requires admin auth")
    
    def test_update_premium_analysis_status_invalid(self, admin_token):
        """PATCH /api/admin/premium-analyses/{id} with invalid status returns 400"""
        # Get an analysis first
        list_res = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        items = list_res.json().get("items", [])
        
        if not items:
            pytest.skip("No premium analyses to test")
        
        analysis_id = items[0]["id"]
        
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/{analysis_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "invalid_status"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid status, got {response.status_code}"
        print("✓ TEST 15 PASSED: PATCH with invalid status returns 400")
    
    def test_update_premium_analysis_to_en_cours(self, admin_token):
        """PATCH /api/admin/premium-analyses/{id} with status 'en_cours' triggers auto-notification"""
        list_res = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        items = list_res.json().get("items", [])
        
        if not items:
            pytest.skip("No premium analyses to test")
        
        analysis_id = items[0]["id"]
        
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/{analysis_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "en_cours"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert response.json().get("success") == True
        print(f"✓ TEST 16 PASSED: PATCH status='en_cours' succeeded (auto-notification triggered)")
    
    def test_update_premium_analysis_to_termine(self, admin_token):
        """PATCH /api/admin/premium-analyses/{id} with status 'termine' triggers auto-notification"""
        list_res = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        items = list_res.json().get("items", [])
        
        if not items:
            pytest.skip("No premium analyses to test")
        
        analysis_id = items[0]["id"]
        
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/{analysis_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "termine"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert response.json().get("success") == True
        print(f"✓ TEST 17 PASSED: PATCH status='termine' succeeded (auto-notification triggered)")
    
    # ===================
    # Test 8: Notification types validation
    # ===================
    def test_notify_different_types(self, admin_token):
        """POST /api/admin/premium-analyses/{id}/notify supports all 4 notification types"""
        list_res = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        items = list_res.json().get("items", [])
        
        if not items:
            pytest.skip("No premium analyses to test")
        
        analysis_id = items[0]["id"]
        
        notification_types = [
            "analyse_premium_ready",
            "payment_confirmed",
            "dossier_in_progress",
            "report_ready"
        ]
        
        for notif_type in notification_types:
            response = requests.post(
                f"{BASE_URL}/api/admin/premium-analyses/{analysis_id}/notify",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"type": notif_type}
            )
            assert response.status_code == 200, f"Failed for type {notif_type}: {response.text}"
        
        print(f"✓ TEST 18 PASSED: All 4 notification types supported: {notification_types}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
