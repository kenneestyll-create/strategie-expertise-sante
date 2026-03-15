"""
Tests for Push Notifications and Object Storage Features
- GET /api/push/vapid-key - VAPID public key retrieval
- POST /api/push/subscribe - Push subscription registration
- DELETE /api/push/unsubscribe - Push subscription removal
- POST /api/push/test - Test push notification
- GET /api/storage/status - Object storage status check
- POST /api/client/documents - Document upload with storage_path
- GET /api/client/documents/{doc_id}/download - Document download
- GET /api/client/settings/notifications - Get notification settings
- PATCH /api/client/settings/notifications - Update notification settings
"""

import pytest
import requests
import os
import uuid
import base64

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ==================== FIXTURES ====================

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="module")
def test_client_credentials():
    """Test client registration/login credentials"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test-push-{unique_id}@example.com",
        "password": "TestPassword123!",
        "name": f"Test Push User {unique_id}",
        "phone": "0600000000",
        "notifications_email": True,
        "notifications_push": True
    }

@pytest.fixture(scope="module")
def client_token(api_client, test_client_credentials):
    """Get a valid client auth token by registering a new user"""
    # Try to register
    response = api_client.post(
        f"{BASE_URL}/api/client/register",
        json=test_client_credentials
    )
    if response.status_code == 201 or response.status_code == 200:
        return response.json().get("access_token")
    
    # If registration fails (user exists), try login
    response = api_client.post(
        f"{BASE_URL}/api/client/login",
        json={
            "email": test_client_credentials["email"],
            "password": test_client_credentials["password"]
        }
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    
    pytest.skip(f"Could not authenticate test client: {response.text}")

@pytest.fixture
def auth_headers(client_token):
    """Authorization headers for authenticated requests"""
    return {"Authorization": f"Bearer {client_token}"}


# ==================== PUSH NOTIFICATION TESTS ====================

class TestVapidKey:
    """Test VAPID public key endpoint"""
    
    def test_get_vapid_key_success(self, api_client):
        """GET /api/push/vapid-key should return non-empty public_key"""
        response = api_client.get(f"{BASE_URL}/api/push/vapid-key")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "public_key" in data, "Response should contain public_key"
        assert data["public_key"], "public_key should not be empty"
        assert len(data["public_key"]) > 50, "public_key should be a valid VAPID key"
        print(f"VAPID public key retrieved successfully: {data['public_key'][:30]}...")


class TestPushSubscribe:
    """Test push subscription endpoint"""
    
    def test_push_subscribe_success(self, api_client, auth_headers):
        """POST /api/push/subscribe should accept subscription and store it"""
        # Mock subscription object (similar to what browser returns)
        subscription = {
            "endpoint": f"https://fcm.googleapis.com/fcm/send/test-{uuid.uuid4()}",
            "expirationTime": None,
            "keys": {
                "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
                "auth": "tBHItJI5svbpez7KI4CCXg"
            }
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/push/subscribe",
            json={"subscription": subscription},
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Subscribe should return success=True"
        print(f"Push subscription registered: {data}")

    def test_push_subscribe_invalid_subscription(self, api_client, auth_headers):
        """POST /api/push/subscribe should reject invalid subscription"""
        response = api_client.post(
            f"{BASE_URL}/api/push/subscribe",
            json={"subscription": {}},  # Empty subscription
            headers=auth_headers
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid subscription, got {response.status_code}"
        print("Invalid subscription correctly rejected")

    def test_push_subscribe_requires_auth(self, api_client):
        """POST /api/push/subscribe should require authentication"""
        subscription = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test-unauth",
            "keys": {"p256dh": "test", "auth": "test"}
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/push/subscribe",
            json={"subscription": subscription}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Unauthenticated subscribe correctly rejected")


class TestPushUnsubscribe:
    """Test push unsubscribe endpoint"""
    
    def test_push_unsubscribe_success(self, api_client, auth_headers):
        """DELETE /api/push/unsubscribe should remove subscription"""
        # First subscribe
        endpoint = f"https://fcm.googleapis.com/fcm/send/test-unsub-{uuid.uuid4()}"
        subscription = {
            "endpoint": endpoint,
            "keys": {"p256dh": "testkey", "auth": "testauth"}
        }
        
        api_client.post(
            f"{BASE_URL}/api/push/subscribe",
            json={"subscription": subscription},
            headers=auth_headers
        )
        
        # Then unsubscribe
        response = api_client.delete(
            f"{BASE_URL}/api/push/unsubscribe",
            json={"endpoint": endpoint},
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Unsubscribe should return success=True"
        print(f"Push subscription removed: {data}")

    def test_push_unsubscribe_requires_auth(self, api_client):
        """DELETE /api/push/unsubscribe should require authentication"""
        response = api_client.delete(
            f"{BASE_URL}/api/push/unsubscribe",
            json={"endpoint": "https://test.com"}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Unauthenticated unsubscribe correctly rejected")


class TestPushTestNotification:
    """Test the test push notification endpoint"""
    
    def test_push_test_requires_auth(self, api_client):
        """POST /api/push/test should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/push/test")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Unauthenticated test push correctly rejected")

    def test_push_test_success(self, api_client, auth_headers):
        """POST /api/push/test should send a test notification"""
        response = api_client.post(
            f"{BASE_URL}/api/push/test",
            headers=auth_headers
        )
        
        # Should succeed even if no subscriptions exist (just won't deliver)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Test push should return success=True"
        print(f"Test push notification sent: {data}")


# ==================== STORAGE STATUS TESTS ====================

class TestStorageStatus:
    """Test object storage status endpoint"""
    
    def test_storage_status_available(self, api_client):
        """GET /api/storage/status should return object_storage_available: true"""
        response = api_client.get(f"{BASE_URL}/api/storage/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "object_storage_available" in data, "Response should contain object_storage_available"
        assert data["object_storage_available"] == True, "Object storage should be available"
        assert "provider" in data, "Response should contain provider info"
        print(f"Storage status: {data}")


# ==================== DOCUMENT UPLOAD/DOWNLOAD TESTS ====================

class TestDocumentUpload:
    """Test document upload with object storage"""
    
    def test_document_upload_success(self, api_client, auth_headers):
        """POST /api/client/documents should upload document with storage_path"""
        # Create a simple test file content
        test_content = b"This is a test document for storage testing."
        base64_content = base64.b64encode(test_content).decode('utf-8')
        
        payload = {
            "filename": f"test-doc-{uuid.uuid4()}.txt",
            "file_data": base64_content,
            "mime_type": "text/plain",
            "size": len(test_content),
            "ocr_fields": {},
            "tags": {"type_document": "autre"}
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/client/documents",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Upload should return success=True"
        assert "document" in data, "Response should contain document"
        
        doc = data["document"]
        assert "id" in doc, "Document should have an ID"
        assert doc.get("storage_path"), "Document should have storage_path (object storage)"
        assert doc.get("file_data") is None, "file_data should be None when using object storage"
        
        print(f"Document uploaded with storage_path: {doc.get('storage_path')}")
        return doc["id"]

    def test_document_upload_requires_auth(self, api_client):
        """POST /api/client/documents should require authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/client/documents",
            json={"filename": "test.txt", "file_data": "dGVzdA=="}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Unauthenticated upload correctly rejected")


class TestDocumentDownload:
    """Test document download from object storage"""
    
    def test_document_download_success(self, api_client, auth_headers):
        """GET /api/client/documents/{doc_id}/download should return file content"""
        # First upload a document
        test_content = b"Download test content: Hello World!"
        base64_content = base64.b64encode(test_content).decode('utf-8')
        
        upload_response = api_client.post(
            f"{BASE_URL}/api/client/documents",
            json={
                "filename": f"download-test-{uuid.uuid4()}.txt",
                "file_data": base64_content,
                "mime_type": "text/plain",
                "size": len(test_content),
                "ocr_fields": {},
                "tags": {}
            },
            headers=auth_headers
        )
        
        assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
        doc_id = upload_response.json()["document"]["id"]
        
        # Now download
        download_response = api_client.get(
            f"{BASE_URL}/api/client/documents/{doc_id}/download",
            headers=auth_headers
        )
        
        assert download_response.status_code == 200, f"Expected 200, got {download_response.status_code}: {download_response.text}"
        assert download_response.content == test_content, "Downloaded content should match uploaded content"
        
        print(f"Document downloaded successfully, size: {len(download_response.content)} bytes")

    def test_document_download_not_found(self, api_client, auth_headers):
        """GET /api/client/documents/{doc_id}/download should return 404 for non-existent doc"""
        response = api_client.get(
            f"{BASE_URL}/api/client/documents/nonexistent-doc-id-12345/download",
            headers=auth_headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Non-existent document download correctly returns 404")

    def test_document_download_requires_auth(self, api_client):
        """GET /api/client/documents/{doc_id}/download should require authentication"""
        response = api_client.get(
            f"{BASE_URL}/api/client/documents/any-doc-id/download"
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Unauthenticated download correctly rejected")


# ==================== NOTIFICATION SETTINGS TESTS ====================

class TestNotificationSettings:
    """Test notification settings endpoints"""
    
    def test_get_notification_settings(self, api_client, auth_headers):
        """GET /api/client/settings/notifications should return preferences"""
        response = api_client.get(
            f"{BASE_URL}/api/client/settings/notifications",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "notifications_email" in data, "Response should contain notifications_email"
        assert "notifications_push" in data, "Response should contain notifications_push"
        assert isinstance(data["notifications_email"], bool), "notifications_email should be boolean"
        assert isinstance(data["notifications_push"], bool), "notifications_push should be boolean"
        
        print(f"Notification settings: {data}")

    def test_update_notification_settings(self, api_client, auth_headers):
        """PATCH /api/client/settings/notifications should update preferences"""
        # Update settings
        response = api_client.patch(
            f"{BASE_URL}/api/client/settings/notifications",
            json={"notifications_email": False, "notifications_push": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Update should return success=True"
        
        # Verify the update persisted
        get_response = api_client.get(
            f"{BASE_URL}/api/client/settings/notifications",
            headers=auth_headers
        )
        
        get_data = get_response.json()
        assert get_data["notifications_email"] == False, "notifications_email should be updated to False"
        assert get_data["notifications_push"] == True, "notifications_push should remain True"
        
        print(f"Notification settings updated and verified: {get_data}")
        
        # Reset back for clean state
        api_client.patch(
            f"{BASE_URL}/api/client/settings/notifications",
            json={"notifications_email": True},
            headers=auth_headers
        )

    def test_notification_settings_requires_auth(self, api_client):
        """Notification settings endpoints should require authentication"""
        get_response = api_client.get(
            f"{BASE_URL}/api/client/settings/notifications"
        )
        assert get_response.status_code in [401, 403], f"GET should require auth, got {get_response.status_code}"
        
        patch_response = api_client.patch(
            f"{BASE_URL}/api/client/settings/notifications",
            json={"notifications_email": True}
        )
        assert patch_response.status_code in [401, 403], f"PATCH should require auth, got {patch_response.status_code}"
        
        print("Unauthenticated settings access correctly rejected")


# ==================== INTEGRATION TESTS ====================

class TestPushStorageIntegration:
    """Integration tests for push and storage features together"""
    
    def test_full_push_flow(self, api_client, auth_headers):
        """Test complete push notification flow: subscribe -> test -> unsubscribe"""
        # 1. Get VAPID key
        vapid_response = api_client.get(f"{BASE_URL}/api/push/vapid-key")
        assert vapid_response.status_code == 200
        vapid_key = vapid_response.json()["public_key"]
        assert vapid_key
        
        # 2. Subscribe
        endpoint = f"https://fcm.googleapis.com/fcm/send/integration-test-{uuid.uuid4()}"
        subscribe_response = api_client.post(
            f"{BASE_URL}/api/push/subscribe",
            json={"subscription": {"endpoint": endpoint, "keys": {"p256dh": "test", "auth": "test"}}},
            headers=auth_headers
        )
        assert subscribe_response.status_code == 200
        
        # 3. Test push
        test_response = api_client.post(
            f"{BASE_URL}/api/push/test",
            headers=auth_headers
        )
        assert test_response.status_code == 200
        
        # 4. Unsubscribe
        unsub_response = api_client.delete(
            f"{BASE_URL}/api/push/unsubscribe",
            json={"endpoint": endpoint},
            headers=auth_headers
        )
        assert unsub_response.status_code == 200
        
        print("Full push notification flow completed successfully")

    def test_full_document_storage_flow(self, api_client, auth_headers):
        """Test complete document flow: upload -> list -> download -> delete"""
        # 1. Upload document
        test_content = f"Integration test document {uuid.uuid4()}"
        upload_response = api_client.post(
            f"{BASE_URL}/api/client/documents",
            json={
                "filename": f"integration-test-{uuid.uuid4()}.txt",
                "file_data": base64.b64encode(test_content.encode()).decode(),
                "mime_type": "text/plain",
                "size": len(test_content),
                "ocr_fields": {},
                "tags": {}
            },
            headers=auth_headers
        )
        assert upload_response.status_code == 200
        doc_id = upload_response.json()["document"]["id"]
        storage_path = upload_response.json()["document"].get("storage_path")
        assert storage_path, "Document should be stored in object storage"
        
        # 2. List documents
        list_response = api_client.get(
            f"{BASE_URL}/api/client/documents",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        docs = list_response.json()["documents"]
        assert any(d["id"] == doc_id for d in docs), "Uploaded document should appear in list"
        
        # 3. Download document
        download_response = api_client.get(
            f"{BASE_URL}/api/client/documents/{doc_id}/download",
            headers=auth_headers
        )
        assert download_response.status_code == 200
        assert download_response.content.decode() == test_content
        
        # 4. Delete document
        delete_response = api_client.delete(
            f"{BASE_URL}/api/client/documents/{doc_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200
        
        print("Full document storage flow completed successfully")
