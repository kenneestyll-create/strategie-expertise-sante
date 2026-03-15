"""
Test Document Quality Control System
Tests for:
- POST /api/documents/validate (public endpoint)
- POST /api/admin/notify-document-rejected/{client_id} (admin endpoint)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json().get("access_token")


@pytest.fixture(scope="module")
def admin_client(api_client, admin_token):
    """Session with admin auth header"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


class TestDocumentValidation:
    """Tests for POST /api/documents/validate endpoint"""
    
    def test_validate_valid_pdf(self, api_client):
        """TEST 1: Valid PDF returns valid=true"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "test_document.pdf",
            "size": 500000,  # 500KB
            "mime_type": "application/pdf"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["errors"] == []
        print("✓ TEST 1 PASSED: Valid PDF returns valid=true")
    
    def test_validate_valid_jpg(self, api_client):
        """TEST 2: Valid JPG returns valid=true"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "photo.jpg",
            "size": 2000000,  # 2MB
            "mime_type": "image/jpeg"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["errors"] == []
        print("✓ TEST 2 PASSED: Valid JPG returns valid=true")
    
    def test_validate_valid_png(self, api_client):
        """TEST 3: Valid PNG returns valid=true"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "scan.png",
            "size": 1500000,  # 1.5MB
            "mime_type": "image/png"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["errors"] == []
        print("✓ TEST 3 PASSED: Valid PNG returns valid=true")
    
    def test_validate_valid_docx(self, api_client):
        """TEST 4: Valid DOCX returns valid=true"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "rapport.docx",
            "size": 300000,  # 300KB
            "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["errors"] == []
        print("✓ TEST 4 PASSED: Valid DOCX returns valid=true")
    
    def test_validate_invalid_exe_format(self, api_client):
        """TEST 5: .exe file returns valid=false with format error"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "malware.exe",
            "size": 500000,
            "mime_type": "application/x-msdownload"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0
        assert any("non accepté" in err.lower() or "format" in err.lower() for err in data["errors"])
        print("✓ TEST 5 PASSED: .exe file returns valid=false with format error")
    
    def test_validate_invalid_txt_format(self, api_client):
        """TEST 6: .txt file returns valid=false with format error"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "document.txt",
            "size": 500000,
            "mime_type": "text/plain"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0
        print("✓ TEST 6 PASSED: .txt file returns valid=false with format error")
    
    def test_validate_oversized_file(self, api_client):
        """TEST 7: >10MB file returns valid=false with size error"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "large_file.pdf",
            "size": 15 * 1024 * 1024,  # 15MB
            "mime_type": "application/pdf"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0
        assert any("volumineux" in err.lower() or "taille" in err.lower() or "10" in err for err in data["errors"])
        print("✓ TEST 7 PASSED: >10MB file returns valid=false with size error")
    
    def test_validate_tiny_file_corrupted(self, api_client):
        """TEST 8: <100 bytes file returns valid=false with corruption error"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "tiny.pdf",
            "size": 50,  # 50 bytes
            "mime_type": "application/pdf"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0
        assert any("illisible" in err.lower() or "corrompu" in err.lower() for err in data["errors"])
        print("✓ TEST 8 PASSED: <100 bytes file returns valid=false with corruption error")
    
    def test_validate_zero_size_file(self, api_client):
        """TEST 9: Zero-size file returns valid=false"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "empty.pdf",
            "size": 0,
            "mime_type": "application/pdf"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0
        print("✓ TEST 9 PASSED: Zero-size file returns valid=false")
    
    def test_validate_exactly_10mb(self, api_client):
        """TEST 10: Exactly 10MB file is valid (boundary test)"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "exact_10mb.pdf",
            "size": 10 * 1024 * 1024,  # Exactly 10MB
            "mime_type": "application/pdf"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        print("✓ TEST 10 PASSED: Exactly 10MB file is valid")
    
    def test_validate_uppercase_extension(self, api_client):
        """TEST 11: Uppercase extension (e.g., .PDF) is valid"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "DOCUMENT.PDF",
            "size": 500000,
            "mime_type": "application/pdf"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        print("✓ TEST 11 PASSED: Uppercase extension .PDF is valid")
    
    def test_validate_jpeg_extension(self, api_client):
        """TEST 12: .jpeg extension (not just .jpg) is valid"""
        response = api_client.post(f"{BASE_URL}/api/documents/validate", json={
            "filename": "photo.jpeg",
            "size": 1000000,
            "mime_type": "image/jpeg"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        print("✓ TEST 12 PASSED: .jpeg extension is valid")


class TestDocumentRejectionNotification:
    """Tests for POST /api/admin/notify-document-rejected/{client_id} endpoint"""
    
    def test_notify_rejected_requires_auth(self, api_client):
        """TEST 13: Notify endpoint requires admin auth (401 without token)"""
        api_client.headers.pop("Authorization", None)
        response = api_client.post(f"{BASE_URL}/api/admin/notify-document-rejected/test-client-id", json={})
        assert response.status_code == 401 or response.status_code == 403
        print("✓ TEST 13 PASSED: Notify endpoint requires admin auth")
    
    def test_notify_rejected_with_admin_auth(self, admin_client):
        """TEST 14: Admin can notify client about rejected documents"""
        # First, get a client ID from the clients list
        clients_response = admin_client.get(f"{BASE_URL}/api/admin/clients")
        assert clients_response.status_code == 200
        clients = clients_response.json()
        
        if len(clients) > 0:
            client_id = clients[0]["id"]
            response = admin_client.post(f"{BASE_URL}/api/admin/notify-document-rejected/{client_id}", json={})
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            print(f"✓ TEST 14 PASSED: Admin can notify client {client_id} about rejected documents")
        else:
            # If no clients exist, create one for testing
            test_email = f"test-doc-{uuid.uuid4().hex[:8]}@example.com"
            reg_response = admin_client.post(f"{BASE_URL}/api/client/register", json={
                "email": test_email,
                "password": "Test1234!",
                "name": "Test Doc Client"
            })
            if reg_response.status_code in [200, 201]:
                client_id = reg_response.json().get("client_id") or reg_response.json().get("id")
                response = admin_client.post(f"{BASE_URL}/api/admin/notify-document-rejected/{client_id}", json={})
                assert response.status_code == 200
                data = response.json()
                assert data.get("success") is True
                print(f"✓ TEST 14 PASSED: Admin can notify newly created client about rejected documents")
            else:
                pytest.skip("No clients available and couldn't create test client")
    
    def test_notify_rejected_with_custom_message(self, admin_client):
        """TEST 15: Admin can send custom message for document rejection"""
        clients_response = admin_client.get(f"{BASE_URL}/api/admin/clients")
        clients = clients_response.json()
        
        if len(clients) > 0:
            client_id = clients[0]["id"]
            custom_msg = "Votre justificatif d'identité est flou. Merci de le renvoyer."
            response = admin_client.post(f"{BASE_URL}/api/admin/notify-document-rejected/{client_id}", json={
                "message": custom_msg
            })
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            print("✓ TEST 15 PASSED: Admin can send custom message for document rejection")
        else:
            pytest.skip("No clients available for testing")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
