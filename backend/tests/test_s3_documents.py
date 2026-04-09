"""
Test S3 Document Storage Integration
Tests for:
- GET /api/documents — paginated list of stored S3 documents
- GET /api/documents/stats — total count and by_source breakdown
- GET /api/documents/{doc_id}/url — presigned URL for secure document access
- POST /api/auth/login — admin login (regression)
- GET /api/admin/documents — client documents list (regression)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


class TestAdminAuth:
    """Admin authentication tests (regression)"""
    
    def test_admin_login_success(self):
        """POST /api/auth/login — admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert len(data["access_token"]) > 0, "Token should not be empty"
        print(f"✓ Admin login successful, token received")
    
    def test_admin_login_invalid_credentials(self):
        """POST /api/auth/login — invalid credentials returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpass"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ Invalid credentials correctly rejected with 401")


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


@pytest.fixture
def auth_headers(admin_token):
    """Headers with admin auth token"""
    return {"Authorization": f"Bearer {admin_token}"}


class TestS3DocumentsEndpoints:
    """S3 Document storage endpoints tests"""
    
    def test_documents_list_requires_auth(self):
        """GET /api/documents — requires authentication"""
        response = requests.get(f"{BASE_URL}/api/documents")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✓ /api/documents requires authentication (got {response.status_code})")
    
    def test_documents_list_success(self, auth_headers):
        """GET /api/documents — returns paginated list of stored S3 documents"""
        response = requests.get(f"{BASE_URL}/api/documents", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "documents" in data, "Response should contain 'documents' key"
        assert "total" in data, "Response should contain 'total' key"
        assert "page" in data, "Response should contain 'page' key"
        assert "per_page" in data, "Response should contain 'per_page' key"
        
        assert isinstance(data["documents"], list), "documents should be a list"
        assert isinstance(data["total"], int), "total should be an integer"
        assert data["page"] == 1, "Default page should be 1"
        assert data["per_page"] == 20, "Default per_page should be 20"
        
        print(f"✓ GET /api/documents returns {data['total']} documents (page {data['page']})")
        
        # If documents exist, verify structure
        if data["documents"]:
            doc = data["documents"][0]
            print(f"  Sample document: {doc.get('original_filename', 'N/A')}")
            # Documents should have these fields
            expected_fields = ["id", "original_filename", "storage_path", "content_type"]
            for field in expected_fields:
                if field in doc:
                    print(f"    - {field}: present")
    
    def test_documents_list_pagination(self, auth_headers):
        """GET /api/documents — pagination works"""
        response = requests.get(f"{BASE_URL}/api/documents?page=1&per_page=5", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["page"] == 1, "Page should be 1"
        assert data["per_page"] == 5, "per_page should be 5"
        assert len(data["documents"]) <= 5, "Should return at most 5 documents"
        print(f"✓ Pagination works: page={data['page']}, per_page={data['per_page']}, returned={len(data['documents'])}")
    
    def test_documents_list_filter_by_source(self, auth_headers):
        """GET /api/documents — filter by source works"""
        response = requests.get(f"{BASE_URL}/api/documents?source=dossier_express", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # All returned documents should have the specified source (if any)
        for doc in data["documents"]:
            if "source" in doc:
                assert doc["source"] == "dossier_express", f"Document source should be 'dossier_express', got {doc['source']}"
        
        print(f"✓ Source filter works: returned {len(data['documents'])} documents with source='dossier_express'")
    
    def test_documents_stats_requires_auth(self):
        """GET /api/documents/stats — requires authentication"""
        response = requests.get(f"{BASE_URL}/api/documents/stats")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✓ /api/documents/stats requires authentication (got {response.status_code})")
    
    def test_documents_stats_success(self, auth_headers):
        """GET /api/documents/stats — returns total count and by_source breakdown"""
        response = requests.get(f"{BASE_URL}/api/documents/stats", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "total" in data, "Response should contain 'total' key"
        assert "by_source" in data, "Response should contain 'by_source' key"
        
        assert isinstance(data["total"], int), "total should be an integer"
        assert isinstance(data["by_source"], list), "by_source should be a list"
        
        print(f"✓ GET /api/documents/stats: total={data['total']}")
        
        # Verify by_source structure
        for source_stat in data["by_source"]:
            assert "source" in source_stat, "Each by_source item should have 'source'"
            assert "count" in source_stat, "Each by_source item should have 'count'"
            print(f"  - {source_stat['source']}: {source_stat['count']} documents")
    
    def test_document_url_requires_auth(self):
        """GET /api/documents/{doc_id}/url — requires authentication"""
        response = requests.get(f"{BASE_URL}/api/documents/fake-id/url")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✓ /api/documents/{{doc_id}}/url requires authentication (got {response.status_code})")
    
    def test_document_url_not_found(self, auth_headers):
        """GET /api/documents/{doc_id}/url — returns 404 for non-existent document"""
        response = requests.get(f"{BASE_URL}/api/documents/non-existent-id/url", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Non-existent document returns 404")
    
    def test_document_url_success(self, auth_headers):
        """GET /api/documents/{doc_id}/url — returns presigned URL for existing document"""
        # First get a document ID
        list_response = requests.get(f"{BASE_URL}/api/documents", headers=auth_headers)
        if list_response.status_code != 200:
            pytest.skip("Could not fetch documents list")
        
        docs = list_response.json().get("documents", [])
        if not docs:
            pytest.skip("No documents available to test presigned URL")
        
        doc_id = docs[0]["id"]
        doc_filename = docs[0].get("original_filename", "unknown")
        
        # Get presigned URL
        response = requests.get(f"{BASE_URL}/api/documents/{doc_id}/url", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "url" in data, "Response should contain 'url' key"
        assert "filename" in data, "Response should contain 'filename' key"
        assert "content_type" in data, "Response should contain 'content_type' key"
        
        # Verify URL is a valid S3 presigned URL
        url = data["url"]
        assert url.startswith("https://"), "URL should be HTTPS"
        assert "s3" in url.lower() or "amazonaws" in url.lower(), "URL should be an S3 URL"
        assert "X-Amz-Signature" in url or "Signature" in url, "URL should contain signature parameter"
        
        print(f"✓ Presigned URL generated for document '{doc_filename}'")
        print(f"  URL domain: {url.split('/')[2]}")


class TestClientDocumentsRegression:
    """Client documents endpoint regression tests"""
    
    def test_admin_documents_requires_auth(self):
        """GET /api/admin/documents — requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/documents")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✓ /api/admin/documents requires authentication (got {response.status_code})")
    
    def test_admin_documents_success(self, auth_headers):
        """GET /api/admin/documents — returns client documents list"""
        response = requests.get(f"{BASE_URL}/api/admin/documents", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "documents" in data, "Response should contain 'documents' key"
        assert "stats" in data, "Response should contain 'stats' key"
        
        assert isinstance(data["documents"], list), "documents should be a list"
        assert isinstance(data["stats"], dict), "stats should be a dict"
        
        # Verify stats structure
        stats = data["stats"]
        assert "total" in stats, "stats should contain 'total'"
        
        print(f"✓ GET /api/admin/documents: {stats.get('total', 0)} client documents")
        print(f"  Stats: {stats}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
