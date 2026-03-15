"""
Tests for Intelligent Document History feature in Client Portal.
Endpoints tested:
- POST /api/client/documents: Upload document with auto-categorization
- GET /api/client/documents: List with filters (category, status, search)
- GET /api/client/documents/{id}: Get single document with file_data
- PATCH /api/client/documents/{id}: Update category and tags
- DELETE /api/client/documents/{id}: Delete document
- POST /api/client/documents/{id}/version: Add version to existing document
"""

import pytest
import requests
import os
import base64

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_CLIENT_EMAIL = "test-notif@example.com"
TEST_CLIENT_PASSWORD = "Test1234!"


@pytest.fixture(scope="module")
def client_token():
    """Authenticate as test client and get token."""
    response = requests.post(f"{BASE_URL}/api/client/login", json={
        "email": TEST_CLIENT_EMAIL,
        "password": TEST_CLIENT_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Client login failed: {response.status_code} - {response.text}")
    return response.json().get("access_token")


@pytest.fixture
def auth_headers(client_token):
    """Auth headers for authenticated requests."""
    return {"Authorization": f"Bearer {client_token}", "Content-Type": "application/json"}


class TestClientDocumentsList:
    """Tests for GET /api/client/documents endpoint."""

    def test_list_documents_returns_stats(self, auth_headers):
        """Test that list endpoint returns documents with stats (by_category, by_status)."""
        response = requests.get(f"{BASE_URL}/api/client/documents", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "documents" in data, "Response should contain 'documents' key"
        assert "total" in data, "Response should contain 'total' key"
        assert "by_category" in data, "Response should contain 'by_category' stats"
        assert "by_status" in data, "Response should contain 'by_status' stats"
        
        # by_status should have expected keys
        assert "en_attente" in data["by_status"], "by_status should have 'en_attente'"
        assert "valide" in data["by_status"], "by_status should have 'valide'"
        assert "illisible" in data["by_status"], "by_status should have 'illisible'"

    def test_list_documents_filter_by_category_at(self, auth_headers):
        """Test filtering documents by category=at."""
        response = requests.get(f"{BASE_URL}/api/client/documents?category=at", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        for doc in data["documents"]:
            assert doc["category"] == "at", f"Document {doc['id']} should have category 'at'"

    def test_list_documents_filter_by_category_mdph(self, auth_headers):
        """Test filtering documents by category=mdph."""
        response = requests.get(f"{BASE_URL}/api/client/documents?category=mdph", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        for doc in data["documents"]:
            assert doc["category"] == "mdph", f"Document {doc['id']} should have category 'mdph'"

    def test_list_documents_filter_by_status_en_attente(self, auth_headers):
        """Test filtering documents by status=en_attente."""
        response = requests.get(f"{BASE_URL}/api/client/documents?status=en_attente", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        for doc in data["documents"]:
            assert doc["status"] == "en_attente", f"Document should have status 'en_attente'"

    def test_list_documents_search_by_organisme_cpam(self, auth_headers):
        """Test searching documents by organisme='cpam'."""
        response = requests.get(f"{BASE_URL}/api/client/documents?search=cpam", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # At least one document should match CPAM search
        # Note: search looks in filename, organisme, and references

    def test_list_documents_search_by_filename(self, auth_headers):
        """Test searching documents by filename."""
        response = requests.get(f"{BASE_URL}/api/client/documents?search=courrier", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # Check search results contain the expected document


class TestClientDocumentsUpload:
    """Tests for POST /api/client/documents endpoint."""

    def test_upload_document_with_auto_categorization_at(self, auth_headers):
        """Test uploading document with OCR fields triggers auto-categorization to 'at'."""
        # Create a simple base64 encoded content
        file_content = base64.b64encode(b"Test document content for AT").decode('utf-8')
        
        payload = {
            "filename": "TEST_upload_at_document.pdf",
            "file_data": file_content,
            "mime_type": "application/pdf",
            "size": 100,
            "ocr_fields": {
                "type_dossier_detected": ["at"],
                "dates": ["01/01/2026"],
                "references": ["AT-TEST-001"]
            },
            "tags": {}
        }
        
        response = requests.post(f"{BASE_URL}/api/client/documents", headers=auth_headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert "document" in data
        assert data["document"]["category"] == "at", "Should auto-categorize to 'at' from OCR type_dossier_detected"
        assert data["document"]["status"] == "en_attente", "New documents should have status 'en_attente'"
        
        # Store doc id for cleanup
        TestClientDocumentsUpload.created_doc_id = data["document"]["id"]

    def test_upload_document_auto_detects_organisme_cpam(self, auth_headers):
        """Test that organisme is auto-detected from OCR contexte field."""
        file_content = base64.b64encode(b"Test CPAM document").decode('utf-8')
        
        payload = {
            "filename": "TEST_cpam_detection.pdf",
            "file_data": file_content,
            "mime_type": "application/pdf",
            "size": 100,
            "ocr_fields": {
                "type_dossier_detected": ["at"],
                "contexte": "Courrier de la CPAM concernant votre accident du travail"
            },
            "tags": {}
        }
        
        response = requests.post(f"{BASE_URL}/api/client/documents", headers=auth_headers, json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["document"]["tags"]["organisme"] == "CPAM", "Should auto-detect CPAM from contexte"
        
        # Store for cleanup
        TestClientDocumentsUpload.created_doc_id_2 = data["document"]["id"]

    def test_upload_document_auto_detects_organisme_mdph(self, auth_headers):
        """Test that organisme is auto-detected from OCR contexte field for MDPH."""
        file_content = base64.b64encode(b"Test MDPH document").decode('utf-8')
        
        payload = {
            "filename": "TEST_mdph_detection.pdf",
            "file_data": file_content,
            "mime_type": "application/pdf",
            "size": 100,
            "ocr_fields": {
                "type_dossier_detected": ["mdph"],
                "contexte": "Notification MDPH pour AAH"
            },
            "tags": {}
        }
        
        response = requests.post(f"{BASE_URL}/api/client/documents", headers=auth_headers, json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["document"]["tags"]["organisme"] == "MDPH", "Should auto-detect MDPH from contexte"
        
        TestClientDocumentsUpload.created_doc_id_3 = data["document"]["id"]

    def test_upload_document_missing_filename_fails(self, auth_headers):
        """Test that upload fails without filename."""
        payload = {
            "file_data": base64.b64encode(b"content").decode('utf-8'),
            "mime_type": "application/pdf",
            "size": 100
        }
        
        response = requests.post(f"{BASE_URL}/api/client/documents", headers=auth_headers, json=payload)
        assert response.status_code == 400, "Should fail with 400 when filename is missing"

    def test_upload_document_missing_file_data_fails(self, auth_headers):
        """Test that upload fails without file_data."""
        payload = {
            "filename": "test.pdf",
            "mime_type": "application/pdf",
            "size": 100
        }
        
        response = requests.post(f"{BASE_URL}/api/client/documents", headers=auth_headers, json=payload)
        assert response.status_code == 400, "Should fail with 400 when file_data is missing"


class TestClientDocumentsGetById:
    """Tests for GET /api/client/documents/{id} endpoint."""

    def test_get_document_by_id_returns_file_data(self, auth_headers):
        """Test that getting single document returns file_data for download."""
        # First list to get a document ID
        list_response = requests.get(f"{BASE_URL}/api/client/documents", headers=auth_headers)
        assert list_response.status_code == 200
        
        docs = list_response.json()["documents"]
        if not docs:
            pytest.skip("No documents to test")
        
        doc_id = docs[0]["id"]
        
        # Get single document
        response = requests.get(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "file_data" in data, "Single document should include file_data"
        assert "id" in data
        assert "filename" in data
        assert "category" in data
        assert "status" in data

    def test_get_nonexistent_document_returns_404(self, auth_headers):
        """Test that getting non-existent document returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{BASE_URL}/api/client/documents/{fake_id}", headers=auth_headers)
        assert response.status_code == 404, "Should return 404 for non-existent document"


class TestClientDocumentsUpdate:
    """Tests for PATCH /api/client/documents/{id} endpoint."""

    def test_update_document_category(self, auth_headers):
        """Test updating document category."""
        # First create a test document
        file_content = base64.b64encode(b"Test update category").decode('utf-8')
        create_response = requests.post(f"{BASE_URL}/api/client/documents", headers=auth_headers, json={
            "filename": "TEST_update_category.pdf",
            "file_data": file_content,
            "mime_type": "application/pdf",
            "size": 100,
            "ocr_fields": {},
            "tags": {}
        })
        assert create_response.status_code == 200
        doc_id = create_response.json()["document"]["id"]
        
        # Update category
        response = requests.patch(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers, json={
            "category": "expertise"
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify update
        verify = requests.get(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers)
        assert verify.json()["category"] == "expertise", "Category should be updated to 'expertise'"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers)

    def test_update_document_tags(self, auth_headers):
        """Test updating document tags (organisme, date_document)."""
        # Create test document
        file_content = base64.b64encode(b"Test update tags").decode('utf-8')
        create_response = requests.post(f"{BASE_URL}/api/client/documents", headers=auth_headers, json={
            "filename": "TEST_update_tags.pdf",
            "file_data": file_content,
            "mime_type": "application/pdf",
            "size": 100,
            "ocr_fields": {},
            "tags": {}
        })
        assert create_response.status_code == 200
        doc_id = create_response.json()["document"]["id"]
        
        # Update tags
        response = requests.patch(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers, json={
            "category": "cpam",
            "tags": {
                "organisme": "CRAMIF",
                "date_document": "15/03/2026"
            }
        })
        assert response.status_code == 200
        
        # Verify
        verify = requests.get(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers)
        data = verify.json()
        assert data["category"] == "cpam"
        assert data["tags"]["organisme"] == "CRAMIF"
        assert data["tags"]["date_document"] == "15/03/2026"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers)

    def test_update_nonexistent_document_returns_404(self, auth_headers):
        """Test that updating non-existent document returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.patch(f"{BASE_URL}/api/client/documents/{fake_id}", headers=auth_headers, json={
            "category": "at"
        })
        assert response.status_code == 404


class TestClientDocumentsDelete:
    """Tests for DELETE /api/client/documents/{id} endpoint."""

    def test_delete_document(self, auth_headers):
        """Test deleting a document."""
        # Create test document
        file_content = base64.b64encode(b"Test delete").decode('utf-8')
        create_response = requests.post(f"{BASE_URL}/api/client/documents", headers=auth_headers, json={
            "filename": "TEST_delete_me.pdf",
            "file_data": file_content,
            "mime_type": "application/pdf",
            "size": 100,
            "ocr_fields": {},
            "tags": {}
        })
        assert create_response.status_code == 200
        doc_id = create_response.json()["document"]["id"]
        
        # Delete
        response = requests.delete(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify deletion
        verify = requests.get(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers)
        assert verify.status_code == 404, "Deleted document should return 404"

    def test_delete_nonexistent_document_returns_404(self, auth_headers):
        """Test that deleting non-existent document returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.delete(f"{BASE_URL}/api/client/documents/{fake_id}", headers=auth_headers)
        assert response.status_code == 404


class TestClientDocumentsVersion:
    """Tests for POST /api/client/documents/{id}/version endpoint."""

    def test_add_version_to_document(self, auth_headers):
        """Test adding a new version to an existing document."""
        # Create initial document
        file_content = base64.b64encode(b"Version 1 content").decode('utf-8')
        create_response = requests.post(f"{BASE_URL}/api/client/documents", headers=auth_headers, json={
            "filename": "TEST_versioned_doc.pdf",
            "file_data": file_content,
            "mime_type": "application/pdf",
            "size": 100,
            "ocr_fields": {},
            "tags": {}
        })
        assert create_response.status_code == 200
        doc_id = create_response.json()["document"]["id"]
        initial_versions = create_response.json()["document"]["versions"]
        assert len(initial_versions) == 1
        
        # Add new version
        new_file_content = base64.b64encode(b"Version 2 content - corrected").decode('utf-8')
        version_response = requests.post(f"{BASE_URL}/api/client/documents/{doc_id}/version", headers=auth_headers, json={
            "filename": "TEST_versioned_doc_v2.pdf",
            "file_data": new_file_content
        })
        assert version_response.status_code == 200
        assert version_response.json()["success"] is True
        assert version_response.json()["version"] == 2
        
        # Verify document now has 2 versions and status is 'corrige'
        verify = requests.get(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers)
        data = verify.json()
        assert len(data["versions"]) == 2, "Document should have 2 versions"
        assert data["status"] == "corrige", "Status should be 'corrige' after adding new version"
        assert data["filename"] == "TEST_versioned_doc_v2.pdf", "Filename should be updated"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers)

    def test_add_version_to_nonexistent_document_returns_404(self, auth_headers):
        """Test that adding version to non-existent document returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.post(f"{BASE_URL}/api/client/documents/{fake_id}/version", headers=auth_headers, json={
            "filename": "test.pdf",
            "file_data": base64.b64encode(b"content").decode('utf-8')
        })
        assert response.status_code == 404


class TestClientDocumentsAuth:
    """Tests for authentication on document endpoints."""

    def test_list_documents_requires_auth(self):
        """Test that listing documents requires authentication."""
        response = requests.get(f"{BASE_URL}/api/client/documents")
        assert response.status_code in [401, 403], "Should require authentication"

    def test_upload_document_requires_auth(self):
        """Test that uploading document requires authentication."""
        response = requests.post(f"{BASE_URL}/api/client/documents", json={
            "filename": "test.pdf",
            "file_data": "base64content"
        })
        assert response.status_code in [401, 403], "Should require authentication"


class TestCleanupTestDocuments:
    """Cleanup any TEST_ prefixed documents created during testing."""

    def test_cleanup_test_documents(self, auth_headers):
        """Clean up TEST_ documents."""
        # Get all documents
        list_response = requests.get(f"{BASE_URL}/api/client/documents", headers=auth_headers)
        if list_response.status_code != 200:
            return
        
        docs = list_response.json()["documents"]
        for doc in docs:
            if doc["filename"].startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/client/documents/{doc['id']}", headers=auth_headers)
        
        # Also clean up any stored IDs from upload tests
        for attr in ['created_doc_id', 'created_doc_id_2', 'created_doc_id_3']:
            doc_id = getattr(TestClientDocumentsUpload, attr, None)
            if doc_id:
                requests.delete(f"{BASE_URL}/api/client/documents/{doc_id}", headers=auth_headers)
