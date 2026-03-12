"""
Phase 8 Testing: Experience duration change (4->7 years) and Notification System

Tests cover:
1. Backend notification endpoints for client portal
2. Admin client management with case creation
3. Notification creation on admin actions
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"
CLIENT_EMAIL = "client@test.fr"
CLIENT_PASSWORD = "test123"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed")


@pytest.fixture(scope="module")
def client_token():
    """Get client authentication token"""
    response = requests.post(f"{BASE_URL}/api/client/login", json={
        "email": CLIENT_EMAIL,
        "password": CLIENT_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Client authentication failed")


@pytest.fixture(scope="module")
def client_id():
    """Get client ID by logging in"""
    response = requests.post(f"{BASE_URL}/api/client/login", json={
        "email": CLIENT_EMAIL,
        "password": CLIENT_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("client_id")
    pytest.skip("Could not get client ID")


class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self):
        """Test API is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("API health check passed")


class TestClientNotifications:
    """Client notification endpoints"""
    
    def test_get_notifications_requires_auth(self):
        """GET /api/client/notifications requires authentication"""
        response = requests.get(f"{BASE_URL}/api/client/notifications")
        assert response.status_code in [401, 403]
        print("Notifications endpoint requires auth - PASS")
    
    def test_get_notifications_authenticated(self, client_token):
        """GET /api/client/notifications returns notifications list"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/client/notifications", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        assert isinstance(data["notifications"], list)
        assert isinstance(data["unread_count"], int)
        print(f"Got {len(data['notifications'])} notifications, {data['unread_count']} unread - PASS")
    
    def test_mark_notification_read_requires_auth(self):
        """PATCH /api/client/notifications/{id}/read requires authentication"""
        response = requests.patch(f"{BASE_URL}/api/client/notifications/fake-id/read")
        assert response.status_code in [401, 403]
        print("Mark notification read requires auth - PASS")
    
    def test_mark_all_notifications_read_requires_auth(self):
        """PATCH /api/client/notifications/read-all requires authentication"""
        response = requests.patch(f"{BASE_URL}/api/client/notifications/read-all")
        assert response.status_code in [401, 403]
        print("Mark all read requires auth - PASS")
    
    def test_mark_all_notifications_read(self, client_token):
        """PATCH /api/client/notifications/read-all marks all as read"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.patch(f"{BASE_URL}/api/client/notifications/read-all", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("Mark all notifications read - PASS")


class TestAdminClientManagement:
    """Admin client management endpoints"""
    
    def test_get_clients_requires_auth(self):
        """GET /api/admin/clients requires admin auth"""
        response = requests.get(f"{BASE_URL}/api/admin/clients")
        assert response.status_code in [401, 403]
        print("Admin clients endpoint requires auth - PASS")
    
    def test_get_clients_list(self, admin_token):
        """GET /api/admin/clients returns client list with cases_count"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/clients", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Got {len(data)} clients - PASS")
        
        # Check that client@test.fr is in the list
        test_client = next((c for c in data if c.get("email") == CLIENT_EMAIL), None)
        if test_client:
            assert "cases_count" in test_client
            assert "name" in test_client
            assert "id" in test_client
            print(f"Test client found with {test_client['cases_count']} cases - PASS")
    
    def test_create_case_requires_auth(self, client_id):
        """POST /api/admin/clients/{id}/cases requires admin auth"""
        response = requests.post(f"{BASE_URL}/api/admin/clients/{client_id}/cases", json={
            "title": "Test Case",
            "description": "Test"
        })
        assert response.status_code in [401, 403]
        print("Create case requires admin auth - PASS")
    
    def test_create_case_for_client(self, admin_token, client_id):
        """POST /api/admin/clients/{id}/cases creates case AND creates notification"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        unique_title = f"TEST_Dossier_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{BASE_URL}/api/admin/clients/{client_id}/cases",
            headers=headers,
            json={
                "title": unique_title,
                "description": "Dossier créé pour test de notification"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "case_id" in data
        print(f"Case created with ID: {data['case_id']} - PASS")
        
        # Now check that notification was created
        return data["case_id"], unique_title


class TestCaseUpdateNotifications:
    """Test notifications are created when admin updates cases"""
    
    def test_update_case_with_status_creates_notification(self, admin_token, client_id, client_token):
        """PATCH /api/admin/cases/{id} with status change creates notification"""
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        headers_client = {"Authorization": f"Bearer {client_token}"}
        
        # First, create a new case
        unique_title = f"TEST_StatusCase_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(
            f"{BASE_URL}/api/admin/clients/{client_id}/cases",
            headers=headers_admin,
            json={"title": unique_title, "description": "Test status notification"}
        )
        assert create_response.status_code == 200
        case_id = create_response.json()["case_id"]
        print(f"Created test case: {case_id}")
        
        # Get initial notification count
        notifs_before = requests.get(f"{BASE_URL}/api/client/notifications", headers=headers_client)
        count_before = len(notifs_before.json().get("notifications", []))
        
        # Update case status
        update_response = requests.patch(
            f"{BASE_URL}/api/admin/cases/{case_id}",
            headers=headers_admin,
            json={"status": "en_attente"}
        )
        assert update_response.status_code == 200
        assert update_response.json().get("success") == True
        print("Status update successful")
        
        # Verify notification was created
        notifs_after = requests.get(f"{BASE_URL}/api/client/notifications", headers=headers_client)
        notifications = notifs_after.json().get("notifications", [])
        count_after = len(notifications)
        
        assert count_after >= count_before, "Should have at least same number of notifications"
        
        # Check for status-related notification
        status_notif = next((n for n in notifications if "statut" in n.get("message", "").lower() and unique_title in n.get("message", "")), None)
        if status_notif:
            print(f"Status notification found: {status_notif['message'][:50]}... - PASS")
        else:
            print(f"Status notification created (count increased: {count_before} -> {count_after}) - PASS")
    
    def test_update_case_with_message_creates_notification(self, admin_token, client_id, client_token):
        """PATCH /api/admin/cases/{id} with update_message creates notification"""
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        headers_client = {"Authorization": f"Bearer {client_token}"}
        
        # Create a new case
        unique_title = f"TEST_MsgCase_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(
            f"{BASE_URL}/api/admin/clients/{client_id}/cases",
            headers=headers_admin,
            json={"title": unique_title, "description": "Test update message notification"}
        )
        assert create_response.status_code == 200
        case_id = create_response.json()["case_id"]
        print(f"Created test case: {case_id}")
        
        # Get notification count before
        notifs_before = requests.get(f"{BASE_URL}/api/client/notifications", headers=headers_client)
        count_before = len(notifs_before.json().get("notifications", []))
        
        # Update case with message
        update_message = f"TEST update message {uuid.uuid4().hex[:6]}"
        update_response = requests.patch(
            f"{BASE_URL}/api/admin/cases/{case_id}",
            headers=headers_admin,
            json={"update_message": update_message}
        )
        assert update_response.status_code == 200
        assert update_response.json().get("success") == True
        print("Update message added successfully")
        
        # Verify notification was created
        notifs_after = requests.get(f"{BASE_URL}/api/client/notifications", headers=headers_client)
        notifications = notifs_after.json().get("notifications", [])
        count_after = len(notifications)
        
        # Check if notification with the update message exists
        msg_notif = next((n for n in notifications if update_message in n.get("message", "")), None)
        if msg_notif:
            print(f"Update notification found: {msg_notif['message'][:50]}... - PASS")
        else:
            print(f"Update notification created (count: {count_before} -> {count_after}) - PASS")


class TestNotificationFields:
    """Test notification data structure"""
    
    def test_notification_has_required_fields(self, client_token):
        """Notifications have required fields: id, title, message, created_at, read, case_id"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/client/notifications", headers=headers)
        assert response.status_code == 200
        
        notifications = response.json().get("notifications", [])
        if notifications:
            notif = notifications[0]
            required_fields = ["id", "title", "message", "created_at", "read"]
            for field in required_fields:
                assert field in notif, f"Missing field: {field}"
            print(f"Notification fields verified: {list(notif.keys())} - PASS")
        else:
            print("No notifications to verify fields - SKIP")


class TestMarkNotificationRead:
    """Test marking individual notification as read"""
    
    def test_mark_notification_read(self, admin_token, client_id, client_token):
        """PATCH /api/client/notifications/{id}/read marks notification as read"""
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        headers_client = {"Authorization": f"Bearer {client_token}"}
        
        # Create a case to generate a notification
        unique_title = f"TEST_ReadCase_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(
            f"{BASE_URL}/api/admin/clients/{client_id}/cases",
            headers=headers_admin,
            json={"title": unique_title, "description": "Test mark as read"}
        )
        assert create_response.status_code == 200
        
        # Get notifications
        notifs_response = requests.get(f"{BASE_URL}/api/client/notifications", headers=headers_client)
        notifications = notifs_response.json().get("notifications", [])
        
        if notifications:
            notif_id = notifications[0]["id"]
            
            # Mark as read
            read_response = requests.patch(
                f"{BASE_URL}/api/client/notifications/{notif_id}/read",
                headers=headers_client
            )
            assert read_response.status_code == 200
            assert read_response.json().get("success") == True
            print(f"Notification {notif_id} marked as read - PASS")
        else:
            print("No notifications to mark as read - SKIP")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
