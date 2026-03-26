"""
Test Dossier Express Processing View UX - Backend API Tests
Tests for admin-bypass endpoint and status polling with progress_step updates
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDossierExpressProcessingAPI:
    """Tests for Dossier Express processing flow backend APIs"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json().get("access_token")
    
    def test_admin_bypass_creates_dossier(self, admin_token):
        """Test that admin-bypass endpoint creates a dossier and returns dossier_id"""
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "TEST_ProcessingView User",
                "email": "test_processing@example.com",
                "situation": "Test situation for processing view UX verification",
                "type_dossier": "Accident du travail (AT)",
                "regime": "Régime général",
                "documents_text": "",
                "premium_pdf": False
            }
        )
        assert response.status_code == 200, f"Admin bypass failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "dossier_id" in data, "Response should contain dossier_id"
        assert data.get("success") == True, "Response should indicate success"
        assert data.get("admin_test") == True, "Response should indicate admin_test mode"
        
        print(f"Created dossier: {data['dossier_id']}")
        return data["dossier_id"]
    
    def test_status_returns_progress_step(self, admin_token):
        """Test that status endpoint returns progress_step field"""
        # First create a dossier
        create_response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "TEST_ProgressStep User",
                "email": "test_progress@example.com",
                "situation": "Test situation for progress step verification",
                "type_dossier": "Maladie professionnelle (MP)",
                "regime": "Régime général",
                "documents_text": "",
                "premium_pdf": False
            }
        )
        assert create_response.status_code == 200
        dossier_id = create_response.json()["dossier_id"]
        
        # Poll status
        status_response = requests.get(f"{BASE_URL}/api/dossier-express/status/{dossier_id}")
        assert status_response.status_code == 200, f"Status check failed: {status_response.text}"
        
        data = status_response.json()
        
        # Verify progress_step field exists
        assert "progress_step" in data, "Status should contain progress_step field"
        assert "status" in data, "Status should contain status field"
        
        # progress_step should be one of the valid values
        valid_steps = ['uploading', 'reading', 'analyzing', 'generating', 'sending', 'completed', 'error']
        assert data["progress_step"] in valid_steps, f"progress_step should be one of {valid_steps}, got {data['progress_step']}"
        
        print(f"Dossier {dossier_id} - status: {data['status']}, progress_step: {data['progress_step']}")
    
    def test_status_polling_shows_progress_updates(self, admin_token):
        """Test that polling status shows progress updates over time"""
        # Create a dossier
        create_response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "TEST_PollingProgress User",
                "email": "test_polling@example.com",
                "situation": "Test situation for polling progress verification - this is a detailed description to trigger full analysis",
                "type_dossier": "Demande MDPH / AAH",
                "regime": "Régime général",
                "documents_text": "Document content for analysis",
                "premium_pdf": False
            }
        )
        assert create_response.status_code == 200
        dossier_id = create_response.json()["dossier_id"]
        
        # Poll multiple times to see progress
        progress_steps_seen = set()
        for i in range(6):  # Poll 6 times over 30 seconds
            status_response = requests.get(f"{BASE_URL}/api/dossier-express/status/{dossier_id}")
            if status_response.status_code == 200:
                data = status_response.json()
                progress_steps_seen.add(data.get("progress_step"))
                print(f"Poll {i+1}: status={data.get('status')}, progress_step={data.get('progress_step')}")
                
                # If completed or error, stop polling
                if data.get("status") in ["completed", "error"]:
                    break
            time.sleep(5)
        
        # Verify we saw at least one progress step
        assert len(progress_steps_seen) >= 1, "Should see at least one progress step"
        print(f"Progress steps seen: {progress_steps_seen}")
    
    def test_status_invalid_dossier_returns_404(self):
        """Test that status endpoint returns 404 for invalid dossier ID"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/invalid-dossier-id-12345")
        assert response.status_code == 404, f"Expected 404 for invalid dossier, got {response.status_code}"
    
    def test_admin_bypass_without_auth_returns_401(self):
        """Test that admin-bypass endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Unauthorized User",
                "email": "unauth@example.com",
                "situation": "Test",
                "type_dossier": "Autre",
                "regime": "Autre",
                "documents_text": "",
                "premium_pdf": False
            }
        )
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
    
    def test_weekly_count_endpoint(self):
        """Test weekly count endpoint returns count and period"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/weekly-count")
        assert response.status_code == 200, f"Weekly count failed: {response.text}"
        
        data = response.json()
        assert "count" in data, "Response should contain count"
        assert isinstance(data["count"], int), "Count should be an integer"
        print(f"Weekly count: {data['count']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
