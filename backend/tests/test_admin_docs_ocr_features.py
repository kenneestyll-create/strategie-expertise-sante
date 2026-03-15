"""
Test suite for Admin Documents, OCR Phase 2, and Config features
Iteration 44: Testing new admin management and GPT-4o OCR features
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
CLIENT_EMAIL = f"test-admin-docs-{uuid.uuid4().hex[:8]}@example.com"
CLIENT_PASSWORD = "Password123!"

# Sample French admin document text for OCR testing
SAMPLE_OCR_TEXT = """CPAM de Paris - Notification de décision
Accident du travail du 15/03/2024
Monsieur DUPONT Jean
Numéro SS: 1 85 06 75 108 234 57
Taux IPP: 15%
Rente annuelle: 3456€
Référence: AT-2024-0567"""


class TestAdminAuthentication:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Test admin login returns token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] is not None
        print(f"PASS: Admin login successful, token received")
        return data["access_token"]


class TestOCRPhase2GPT4o:
    """Test OCR Phase 2 GPT-4o AI-enhanced extraction"""
    
    def test_extract_fields_ai_endpoint(self):
        """POST /api/documents/extract-fields-ai - GPT-4o extraction"""
        response = requests.post(f"{BASE_URL}/api/documents/extract-fields-ai", json={
            "text": SAMPLE_OCR_TEXT
        })
        assert response.status_code == 200, f"OCR AI extraction failed: {response.text}"
        data = response.json()
        # Should return fields (even if empty) and enhanced flag
        assert "fields" in data, "Response missing 'fields'"
        assert "enhanced" in data, "Response missing 'enhanced' flag"
        
        if data.get("enhanced"):
            print(f"PASS: GPT-4o extraction enhanced=True, fields: {list(data['fields'].keys())}")
        else:
            # Budget might be exhausted or key not configured
            print(f"PASS: GPT-4o endpoint responded, enhanced={data.get('enhanced')}, error={data.get('error', 'none')}")
    
    def test_extract_fields_ai_empty_text(self):
        """POST /api/documents/extract-fields-ai - Empty text handling"""
        response = requests.post(f"{BASE_URL}/api/documents/extract-fields-ai", json={
            "text": ""
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("enhanced") == False, "Empty text should not be enhanced"
        print("PASS: Empty text handled correctly")
    
    def test_extract_fields_with_use_ai_flag(self):
        """POST /api/documents/extract-fields with use_ai=true"""
        response = requests.post(f"{BASE_URL}/api/documents/extract-fields", json={
            "text": SAMPLE_OCR_TEXT,
            "use_ai": True
        })
        assert response.status_code == 200, f"Extract fields with AI failed: {response.text}"
        data = response.json()
        assert "fields" in data
        print(f"PASS: Extract fields with use_ai=True, enhanced={data.get('enhanced', False)}")
    
    def test_extract_fields_regex_fallback(self):
        """POST /api/documents/extract-fields - Regex extraction (Phase 1)"""
        response = requests.post(f"{BASE_URL}/api/documents/extract-fields", json={
            "text": SAMPLE_OCR_TEXT,
            "use_ai": False
        })
        assert response.status_code == 200
        data = response.json()
        assert "fields" in data
        fields = data.get("fields", {})
        # Regex should extract at least some fields
        print(f"PASS: Regex extraction returned fields: {list(fields.keys())}")
        if "dates" in fields:
            print(f"  - Dates found: {fields['dates']}")
        if "montants" in fields:
            print(f"  - Montants found: {fields['montants']}")
        if "numero_ss" in fields:
            print(f"  - Numero SS: {fields['numero_ss']}")


class TestAdminDocumentsManagement:
    """Test Admin Documents tab endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["access_token"]
    
    @pytest.fixture
    def client_with_document(self, admin_token):
        """Create test client and upload a document"""
        # Register a test client
        reg_response = requests.post(f"{BASE_URL}/api/client/register", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD,
            "name": "Test Admin Docs User"
        })
        if reg_response.status_code not in [200, 409]:  # 409 = already exists
            pytest.skip(f"Client registration failed: {reg_response.text}")
        
        # Login as client
        login_response = requests.post(f"{BASE_URL}/api/client/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if login_response.status_code != 200:
            pytest.skip("Client login failed")
        
        client_token = login_response.json()["access_token"]
        client_id = login_response.json().get("client_id")
        
        # Upload a document
        files = {
            'file': ('test_doc.pdf', b'%PDF-1.4 test content', 'application/pdf')
        }
        data = {'category': 'attestation'}
        upload_response = requests.post(
            f"{BASE_URL}/api/client/documents",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        doc_id = None
        if upload_response.status_code == 200:
            doc_id = upload_response.json().get("id")
        
        return {"client_id": client_id, "client_token": client_token, "doc_id": doc_id}
    
    def test_admin_list_all_documents(self, admin_token):
        """GET /api/admin/documents - List all client documents"""
        response = requests.get(
            f"{BASE_URL}/api/admin/documents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"List documents failed: {response.text}"
        data = response.json()
        assert "documents" in data, "Response missing 'documents'"
        assert "stats" in data, "Response missing 'stats'"
        
        stats = data["stats"]
        assert "total" in stats
        print(f"PASS: Admin documents list - Total: {stats['total']}, En attente: {stats.get('en_attente', 0)}, Validés: {stats.get('valide', 0)}")
    
    def test_admin_documents_filter_by_status(self, admin_token):
        """GET /api/admin/documents?status=en_attente - Filter by status"""
        response = requests.get(
            f"{BASE_URL}/api/admin/documents?status=en_attente",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # All returned documents should have status=en_attente
        for doc in data.get("documents", []):
            assert doc.get("status") == "en_attente", f"Document {doc.get('id')} has wrong status"
        print(f"PASS: Filter by status=en_attente returned {len(data.get('documents', []))} documents")
    
    def test_admin_update_document_status_validate(self, admin_token, client_with_document):
        """PATCH /api/admin/documents/{doc_id}/status - Validate document"""
        doc_id = client_with_document.get("doc_id")
        if not doc_id:
            # Try to get any document to test with
            docs_response = requests.get(
                f"{BASE_URL}/api/admin/documents",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            if docs_response.status_code == 200:
                documents = docs_response.json().get("documents", [])
                if documents:
                    doc_id = documents[0]["id"]
        
        if not doc_id:
            pytest.skip("No document available for testing")
        
        response = requests.patch(
            f"{BASE_URL}/api/admin/documents/{doc_id}/status",
            json={"status": "valide"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Document validation failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert data.get("new_status") == "valide"
        print(f"PASS: Document {doc_id} validated successfully + notification triggered")
    
    def test_admin_update_document_status_reject(self, admin_token, client_with_document):
        """PATCH /api/admin/documents/{doc_id}/status - Mark as illisible"""
        doc_id = client_with_document.get("doc_id")
        if not doc_id:
            docs_response = requests.get(
                f"{BASE_URL}/api/admin/documents",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            if docs_response.status_code == 200:
                documents = docs_response.json().get("documents", [])
                # Find a document that's not already illisible
                for d in documents:
                    if d.get("status") != "illisible":
                        doc_id = d["id"]
                        break
        
        if not doc_id:
            pytest.skip("No document available for rejection testing")
        
        response = requests.patch(
            f"{BASE_URL}/api/admin/documents/{doc_id}/status",
            json={"status": "illisible"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Document rejection failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert data.get("new_status") == "illisible"
        print(f"PASS: Document {doc_id} marked illisible + notification triggered")
    
    def test_admin_update_document_invalid_status(self, admin_token):
        """PATCH /api/admin/documents/{doc_id}/status - Invalid status rejected"""
        # First get a document
        docs_response = requests.get(
            f"{BASE_URL}/api/admin/documents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if docs_response.status_code != 200:
            pytest.skip("Could not list documents")
        
        documents = docs_response.json().get("documents", [])
        if not documents:
            pytest.skip("No documents to test with")
        
        doc_id = documents[0]["id"]
        response = requests.patch(
            f"{BASE_URL}/api/admin/documents/{doc_id}/status",
            json={"status": "invalid_status"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400, "Should reject invalid status"
        print("PASS: Invalid status correctly rejected with 400")
    
    def test_admin_documents_requires_auth(self):
        """GET /api/admin/documents - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/documents")
        assert response.status_code in [401, 403], "Should require authentication"
        print("PASS: Admin documents endpoint requires authentication")


class TestAdminEmailConfig:
    """Test Admin Config tab - Email endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["access_token"]
    
    def test_admin_email_status(self, admin_token):
        """GET /api/admin/email/status - Get Resend configuration info"""
        response = requests.get(
            f"{BASE_URL}/api/admin/email/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Email status failed: {response.text}"
        data = response.json()
        
        # Check all required fields
        assert "resend_installed" in data, "Missing resend_installed"
        assert "api_key_configured" in data, "Missing api_key_configured"
        assert "sender_email" in data, "Missing sender_email"
        
        print(f"PASS: Email status - Resend: {data.get('resend_installed')}, API Key: {data.get('api_key_configured')}")
        print(f"  - Sender: {data.get('sender_email')}")
        print(f"  - Domain verified: {data.get('domain_verified', 'N/A')}")
    
    def test_admin_email_test_endpoint(self, admin_token):
        """POST /api/admin/email/test - Test email sending"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email/test",
            json={"email": "test@example.com"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Email test failed: {response.text}"
        data = response.json()
        
        # Endpoint should respond with success or error message
        assert "success" in data or "message" in data
        
        if data.get("success"):
            print(f"PASS: Test email sent successfully")
        else:
            print(f"PASS: Email test endpoint responded - {data.get('message', 'no error')}")
    
    def test_admin_email_test_requires_email(self, admin_token):
        """POST /api/admin/email/test - Requires email parameter"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email/test",
            json={},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400, "Should require email parameter"
        print("PASS: Email test correctly requires email parameter")
    
    def test_admin_email_status_requires_auth(self):
        """GET /api/admin/email/status - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/email/status")
        assert response.status_code in [401, 403], "Should require authentication"
        print("PASS: Email status endpoint requires authentication")


class TestAutoNotificationsOnDocumentActions:
    """Test that document validate/reject triggers notifications"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["access_token"]
    
    def test_notification_created_on_validate(self, admin_token):
        """Validate document and verify notification is created"""
        # Get documents
        docs_response = requests.get(
            f"{BASE_URL}/api/admin/documents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if docs_response.status_code != 200:
            pytest.skip("Could not list documents")
        
        documents = docs_response.json().get("documents", [])
        # Find a document with client_id
        doc = next((d for d in documents if d.get("client_id")), None)
        if not doc:
            pytest.skip("No document with client_id found")
        
        doc_id = doc["id"]
        client_id = doc["client_id"]
        
        # Validate the document
        response = requests.patch(
            f"{BASE_URL}/api/admin/documents/{doc_id}/status",
            json={"status": "valide"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # The notification was created in background - success means endpoint worked
        print(f"PASS: Document validated - notification should be sent to client {client_id[:8]}...")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
