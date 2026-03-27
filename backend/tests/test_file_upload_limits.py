"""
Test file upload size limits for Stratégie & Expertise Santé
Tests the POST /api/extract-document-text endpoint with various file sizes
"""
import pytest
import requests
import base64
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestFileUploadLimits:
    """Test file upload size validation on /api/extract-document-text"""
    
    def test_health_check(self):
        """Verify API is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("PASS: API health check")
    
    def test_normal_5mb_file_accepted(self):
        """Test that a normal 5 MB file is accepted"""
        # Create 5 MB of base64 data (simulating a file)
        file_size = 5 * 1024 * 1024  # 5 MB
        file_content = b'A' * file_size
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        payload = {
            "files": [{
                "name": "test_5mb.pdf",
                "type": "application/pdf",
                "data": file_b64
            }]
        }
        
        response = requests.post(f"{BASE_URL}/api/extract-document-text", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "details" in data
        assert len(data["details"]) == 1
        # File should be processed (not rejected as too_large)
        assert data["details"][0]["status"] != "too_large", "5 MB file should not be rejected as too_large"
        print(f"PASS: 5 MB file accepted, status: {data['details'][0]['status']}")
    
    def test_50mb_file_at_limit_accepted(self):
        """Test that a 50 MB file (at the limit) is accepted"""
        # Create exactly 50 MB of data
        file_size = 50 * 1024 * 1024  # 50 MB
        file_content = b'B' * file_size
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        payload = {
            "files": [{
                "name": "test_50mb.pdf",
                "type": "application/pdf",
                "data": file_b64
            }]
        }
        
        response = requests.post(f"{BASE_URL}/api/extract-document-text", json=payload, timeout=120)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "details" in data
        assert len(data["details"]) == 1
        # File at exactly 50 MB should be accepted
        assert data["details"][0]["status"] != "too_large", "50 MB file (at limit) should be accepted"
        print(f"PASS: 50 MB file at limit accepted, status: {data['details'][0]['status']}")
    
    def test_file_over_50mb_rejected_with_too_large_status(self):
        """Test that a file > 50 MB is rejected with status 'too_large'"""
        # Create 51 MB of data (over the limit)
        file_size = 51 * 1024 * 1024  # 51 MB
        file_content = b'C' * file_size
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        payload = {
            "files": [{
                "name": "test_51mb.pdf",
                "type": "application/pdf",
                "data": file_b64
            }]
        }
        
        response = requests.post(f"{BASE_URL}/api/extract-document-text", json=payload, timeout=120)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "details" in data
        assert len(data["details"]) == 1
        # File over 50 MB should be rejected with status 'too_large'
        assert data["details"][0]["status"] == "too_large", f"Expected status 'too_large', got '{data['details'][0]['status']}'"
        print(f"PASS: 51 MB file rejected with status 'too_large'")
    
    def test_more_than_10_files_rejected_with_400(self):
        """Test that more than 10 files returns HTTP 400"""
        # Create 11 small files
        files_data = []
        for i in range(11):
            file_content = b'X' * 1000  # 1 KB each
            file_b64 = base64.b64encode(file_content).decode('utf-8')
            files_data.append({
                "name": f"test_file_{i+1}.pdf",
                "type": "application/pdf",
                "data": file_b64
            })
        
        payload = {"files": files_data}
        
        response = requests.post(f"{BASE_URL}/api/extract-document-text", json=payload)
        assert response.status_code == 400, f"Expected 400 for >10 files, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data
        assert "10" in data["detail"], f"Error message should mention 10 files limit: {data['detail']}"
        print(f"PASS: 11 files rejected with HTTP 400, message: {data['detail']}")
    
    def test_exactly_10_files_accepted(self):
        """Test that exactly 10 files are accepted"""
        # Create exactly 10 small files
        files_data = []
        for i in range(10):
            file_content = b'Y' * 1000  # 1 KB each
            file_b64 = base64.b64encode(file_content).decode('utf-8')
            files_data.append({
                "name": f"test_file_{i+1}.pdf",
                "type": "application/pdf",
                "data": file_b64
            })
        
        payload = {"files": files_data}
        
        response = requests.post(f"{BASE_URL}/api/extract-document-text", json=payload)
        assert response.status_code == 200, f"Expected 200 for 10 files, got {response.status_code}"
        
        data = response.json()
        assert "files_processed" in data
        assert data["files_processed"] == 10, f"Expected 10 files processed, got {data['files_processed']}"
        print(f"PASS: 10 files accepted, processed: {data['files_processed']}")
    
    def test_total_size_exceeded_rejected(self):
        """Test that total size > 100 MB is rejected"""
        # Create 3 files of 40 MB each = 120 MB total (over 100 MB limit)
        files_data = []
        for i in range(3):
            file_size = 40 * 1024 * 1024  # 40 MB each
            file_content = b'Z' * file_size
            file_b64 = base64.b64encode(file_content).decode('utf-8')
            files_data.append({
                "name": f"test_40mb_{i+1}.pdf",
                "type": "application/pdf",
                "data": file_b64
            })
        
        payload = {"files": files_data}
        
        response = requests.post(f"{BASE_URL}/api/extract-document-text", json=payload, timeout=180)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "details" in data
        
        # At least one file should have status 'total_exceeded'
        statuses = [d["status"] for d in data["details"]]
        has_total_exceeded = "total_exceeded" in statuses
        assert has_total_exceeded, f"Expected at least one file with status 'total_exceeded', got statuses: {statuses}"
        print(f"PASS: Total size exceeded detected, statuses: {statuses}")
    
    def test_empty_files_array_returns_empty_result(self):
        """Test that empty files array returns empty result"""
        payload = {"files": []}
        
        response = requests.post(f"{BASE_URL}/api/extract-document-text", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["files_processed"] == 0
        assert data["extracted_text"] == ""
        print("PASS: Empty files array handled correctly")


class TestAdminLogin:
    """Test admin login still works"""
    
    def test_admin_login(self):
        """Test admin login with correct credentials"""
        payload = {
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 200, f"Admin login failed: {response.status_code}"
        
        data = response.json()
        assert "access_token" in data, "Login response should contain access_token"
        print("PASS: Admin login works")


class TestHomepage:
    """Test homepage loads"""
    
    def test_homepage_loads(self):
        """Test that homepage returns 200"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200, f"Homepage failed to load: {response.status_code}"
        print("PASS: Homepage loads correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
