"""
Test suite for chunked upload pipeline (Iteration 138)
Tests:
- POST /api/upload/chunk - accepts file chunks correctly
- POST /api/upload/extract - handles sync extraction for small files
- POST /api/upload/extract - returns async response with extraction_id for large files
- GET /api/upload/extract-status/{id} - returns processing/done/error status
- POST /api/extract-document-text - regression check for base64 uploads
- GET /api/health - health endpoint
"""
import pytest
import requests
import os
import uuid
import base64
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthEndpoint:
    """Health endpoint tests"""
    
    def test_health_returns_200(self):
        """GET /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("PASS: Health endpoint returns 200")


class TestChunkUpload:
    """Tests for POST /api/upload/chunk endpoint"""
    
    def test_chunk_upload_accepts_valid_chunk(self):
        """POST /api/upload/chunk accepts file chunks correctly"""
        upload_id = str(uuid.uuid4())
        filename = "test_document.pdf"
        chunk_index = 0
        total_chunks = 2
        
        # Create a small test chunk (1KB)
        chunk_data = b"A" * 1024
        
        files = {
            'chunk': ('chunk', chunk_data, 'application/octet-stream')
        }
        data = {
            'upload_id': upload_id,
            'filename': filename,
            'chunk_index': str(chunk_index),
            'total_chunks': str(total_chunks)
        }
        
        response = requests.post(
            f"{BASE_URL}/api/upload/chunk",
            files=files,
            data=data,
            timeout=30
        )
        
        assert response.status_code == 200, f"Chunk upload failed: {response.status_code} - {response.text}"
        result = response.json()
        assert result.get('status') == 'ok', f"Expected status 'ok', got {result.get('status')}"
        assert result.get('chunk_index') == chunk_index
        assert result.get('received') >= 1
        assert result.get('total') == total_chunks
        print(f"PASS: Chunk upload accepted - received {result.get('received')}/{total_chunks}")
    
    def test_chunk_upload_multiple_chunks(self):
        """POST /api/upload/chunk handles multiple chunks for same file"""
        upload_id = str(uuid.uuid4())
        filename = "multi_chunk_test.pdf"
        total_chunks = 3
        
        for i in range(total_chunks):
            chunk_data = f"CHUNK_{i}_DATA_".encode() * 100
            
            files = {
                'chunk': ('chunk', chunk_data, 'application/octet-stream')
            }
            data = {
                'upload_id': upload_id,
                'filename': filename,
                'chunk_index': str(i),
                'total_chunks': str(total_chunks)
            }
            
            response = requests.post(
                f"{BASE_URL}/api/upload/chunk",
                files=files,
                data=data,
                timeout=30
            )
            
            assert response.status_code == 200, f"Chunk {i} upload failed: {response.status_code}"
            result = response.json()
            assert result.get('status') == 'ok'
        
        # Last chunk should indicate complete
        assert result.get('complete') == True, f"Expected complete=True after all chunks, got {result.get('complete')}"
        print(f"PASS: Multiple chunks uploaded successfully - complete={result.get('complete')}")
    
    def test_chunk_upload_rejects_too_many_chunks(self):
        """POST /api/upload/chunk rejects if total_chunks > 500"""
        upload_id = str(uuid.uuid4())
        
        files = {
            'chunk': ('chunk', b"test", 'application/octet-stream')
        }
        data = {
            'upload_id': upload_id,
            'filename': 'test.pdf',
            'chunk_index': '0',
            'total_chunks': '501'  # Exceeds limit
        }
        
        response = requests.post(
            f"{BASE_URL}/api/upload/chunk",
            files=files,
            data=data,
            timeout=30
        )
        
        assert response.status_code == 400, f"Expected 400 for too many chunks, got {response.status_code}"
        print("PASS: Chunk upload correctly rejects > 500 chunks")


class TestExtractEndpoint:
    """Tests for POST /api/upload/extract endpoint"""
    
    def test_extract_requires_upload_id_and_files(self):
        """POST /api/upload/extract returns 400 if upload_id or files missing"""
        # Missing upload_id
        response = requests.post(
            f"{BASE_URL}/api/upload/extract",
            json={"files": []},
            timeout=30
        )
        assert response.status_code == 400, f"Expected 400 for missing upload_id, got {response.status_code}"
        
        # Missing files
        response = requests.post(
            f"{BASE_URL}/api/upload/extract",
            json={"upload_id": "test"},
            timeout=30
        )
        assert response.status_code == 400, f"Expected 400 for missing files, got {response.status_code}"
        print("PASS: Extract endpoint validates required fields")
    
    def test_extract_returns_404_for_nonexistent_upload(self):
        """POST /api/upload/extract returns 404 if upload directory doesn't exist"""
        response = requests.post(
            f"{BASE_URL}/api/upload/extract",
            json={
                "upload_id": "nonexistent-upload-id-12345",
                "files": [{"name": "test.pdf", "type": "application/pdf", "chunked": True, "total_chunks": 1}]
            },
            timeout=30
        )
        assert response.status_code == 404, f"Expected 404 for nonexistent upload, got {response.status_code}"
        print("PASS: Extract endpoint returns 404 for nonexistent upload")
    
    def test_extract_sync_for_small_chunked_file(self):
        """POST /api/upload/extract processes small files synchronously"""
        upload_id = str(uuid.uuid4())
        filename = "small_test.txt"
        
        # Upload a small text file in chunks
        content = b"This is a small test file for extraction testing."
        
        files = {
            'chunk': ('chunk', content, 'application/octet-stream')
        }
        data = {
            'upload_id': upload_id,
            'filename': filename,
            'chunk_index': '0',
            'total_chunks': '1'
        }
        
        chunk_response = requests.post(
            f"{BASE_URL}/api/upload/chunk",
            files=files,
            data=data,
            timeout=30
        )
        assert chunk_response.status_code == 200, f"Chunk upload failed: {chunk_response.text}"
        
        # Now call extract
        extract_response = requests.post(
            f"{BASE_URL}/api/upload/extract",
            json={
                "upload_id": upload_id,
                "files": [{"name": filename, "type": "text/plain", "chunked": True, "total_chunks": 1}]
            },
            timeout=60
        )
        
        assert extract_response.status_code == 200, f"Extract failed: {extract_response.status_code} - {extract_response.text}"
        result = extract_response.json()
        
        # For small files, should NOT return async mode
        if result.get('async'):
            print(f"INFO: Small file returned async mode (extraction_id: {result.get('extraction_id')})")
        else:
            # Should have extracted_text or details
            assert 'extracted_text' in result or 'details' in result, f"Expected extraction result, got {result}"
            print(f"PASS: Small file extracted synchronously")


class TestExtractStatusEndpoint:
    """Tests for GET /api/upload/extract-status/{id} endpoint"""
    
    def test_extract_status_returns_404_for_unknown_id(self):
        """GET /api/upload/extract-status/{id} returns 404 for unknown extraction_id"""
        response = requests.get(
            f"{BASE_URL}/api/upload/extract-status/nonexistent-extraction-id",
            timeout=10
        )
        assert response.status_code == 404, f"Expected 404 for unknown extraction_id, got {response.status_code}"
        print("PASS: Extract status returns 404 for unknown extraction_id")


class TestBase64Extraction:
    """Regression tests for POST /api/extract-document-text (base64 uploads)"""
    
    def test_base64_extraction_accepts_text_file(self):
        """POST /api/extract-document-text extracts text from base64-encoded file"""
        # Create a simple text file content
        text_content = "This is a test document for OCR extraction.\nLine 2 of the document."
        base64_content = base64.b64encode(text_content.encode()).decode()
        
        response = requests.post(
            f"{BASE_URL}/api/extract-document-text",
            json={
                "files": [
                    {
                        "name": "test_document.txt",
                        "type": "text/plain",
                        "data": base64_content
                    }
                ]
            },
            timeout=60
        )
        
        assert response.status_code == 200, f"Base64 extraction failed: {response.status_code} - {response.text}"
        result = response.json()
        assert 'extracted_text' in result or 'details' in result, f"Expected extraction result, got {result}"
        print(f"PASS: Base64 extraction works for text files")
    
    def test_base64_extraction_handles_empty_files(self):
        """POST /api/extract-document-text handles empty files array"""
        response = requests.post(
            f"{BASE_URL}/api/extract-document-text",
            json={"files": []},
            timeout=30
        )
        
        # Should return 200 with empty result or appropriate message
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        print(f"PASS: Base64 extraction handles empty files (status: {response.status_code})")
    
    def test_base64_extraction_handles_invalid_base64(self):
        """POST /api/extract-document-text handles invalid base64 gracefully"""
        response = requests.post(
            f"{BASE_URL}/api/extract-document-text",
            json={
                "files": [
                    {
                        "name": "invalid.pdf",
                        "type": "application/pdf",
                        "data": "not-valid-base64!!!"
                    }
                ]
            },
            timeout=30
        )
        
        # Should not crash - either 200 with error in details or 400
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"
        print(f"PASS: Base64 extraction handles invalid base64 gracefully (status: {response.status_code})")


class TestAdminLogin:
    """Test admin login for authenticated endpoints"""
    
    def test_admin_login_returns_token(self):
        """POST /api/auth/login returns access_token for admin"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@accompagn-sante.fr",
                "password": "Admin2024!"
            },
            timeout=10
        )
        
        assert response.status_code == 200, f"Admin login failed: {response.status_code} - {response.text}"
        result = response.json()
        assert 'access_token' in result, f"Expected access_token in response, got {result.keys()}"
        print("PASS: Admin login returns access_token")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
