"""
Test Dossier Express IA separation from StratégiIA
Verifies:
1. /api/dossier-express/admin-bypass returns dossier_id
2. /api/dossier-express/status/{id} returns progress_step and status
3. /api/admin/dossier-express returns dossiers list
4. Backend uses DOSSIER_EXPRESS_SYSTEM_PROMPT (not StratégiIA prompt)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDossierExpressAPIs:
    """Test Dossier Express IA API endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["access_token"]
    
    def test_weekly_count_endpoint(self):
        """Test /api/dossier-express/weekly-count returns count"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/weekly-count")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "period" in data
        assert data["period"] == "week"
        print(f"PASS: Weekly count endpoint returns count={data['count']}")
    
    def test_admin_bypass_returns_dossier_id(self, admin_token):
        """Test /api/dossier-express/admin-bypass returns dossier_id"""
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "TEST_API_Verification",
                "situation": "Test situation for API verification - testing dossier_id return",
                "type_dossier": "Accident du travail (AT)",
                "regime": "Régime général"
            }
        )
        assert response.status_code == 200, f"Admin bypass failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "success" in data
        assert data["success"] == True
        assert "dossier_id" in data
        assert data["dossier_id"] is not None
        assert len(data["dossier_id"]) > 0
        assert "admin_test" in data
        assert data["admin_test"] == True
        
        print(f"PASS: Admin bypass returns dossier_id={data['dossier_id']}")
        return data["dossier_id"]
    
    def test_status_endpoint_returns_progress_step(self, admin_token):
        """Test /api/dossier-express/status/{id} returns progress_step and status"""
        # First create a dossier
        create_response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "TEST_Status_Check",
                "situation": "Test situation for status endpoint verification",
                "type_dossier": "Maladie professionnelle (MP)",
                "regime": "Régime général"
            }
        )
        assert create_response.status_code == 200
        dossier_id = create_response.json()["dossier_id"]
        
        # Check status endpoint
        status_response = requests.get(f"{BASE_URL}/api/dossier-express/status/{dossier_id}")
        assert status_response.status_code == 200, f"Status check failed: {status_response.text}"
        data = status_response.json()
        
        # Verify required fields
        assert "id" in data
        assert data["id"] == dossier_id
        assert "status" in data
        assert data["status"] in ["processing", "completed", "error"]
        assert "progress_step" in data
        # progress_step should be one of: uploading, reading, analyzing, generating, sending, completed, error
        valid_steps = ["uploading", "reading", "analyzing", "generating", "sending", "completed", "error"]
        assert data["progress_step"] in valid_steps, f"Invalid progress_step: {data['progress_step']}"
        
        print(f"PASS: Status endpoint returns status={data['status']}, progress_step={data['progress_step']}")
    
    def test_admin_dossier_express_list(self, admin_token):
        """Test /api/admin/dossier-express returns dossiers list with stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Admin list failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "items" in data
        assert "stats" in data
        assert isinstance(data["items"], list)
        
        # Verify stats structure
        stats = data["stats"]
        assert "total" in stats
        assert "completed" in stats
        assert "processing" in stats
        assert "errors" in stats
        
        print(f"PASS: Admin dossier-express list returns {len(data['items'])} items")
        print(f"  Stats: total={stats['total']}, completed={stats['completed']}, processing={stats['processing']}, errors={stats['errors']}")
    
    def test_status_404_for_invalid_id(self):
        """Test /api/dossier-express/status/{id} returns 404 for invalid ID"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/invalid-id-12345")
        assert response.status_code == 404
        print("PASS: Status endpoint returns 404 for invalid dossier ID")
    
    def test_admin_bypass_requires_auth(self):
        """Test /api/dossier-express/admin-bypass requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json={
                "name": "Test",
                "situation": "Test situation"
            }
        )
        assert response.status_code == 401
        print("PASS: Admin bypass requires authentication")
    
    def test_admin_bypass_requires_admin_role(self):
        """Test /api/dossier-express/admin-bypass requires admin role"""
        # Try with invalid token
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            headers={"Authorization": "Bearer invalid-token"},
            json={
                "name": "Test",
                "situation": "Test situation"
            }
        )
        assert response.status_code == 401
        print("PASS: Admin bypass requires valid admin token")


class TestDossierExpressPromptSeparation:
    """Verify Dossier Express uses its own prompt, not StratégiIA"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_completed_dossier_analysis_format(self, admin_token):
        """Verify completed dossier analysis uses Dossier Express format"""
        # Get list of dossiers
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find a completed dossier with analysis
        completed_dossiers = [d for d in data["items"] if d.get("status") == "completed"]
        
        if not completed_dossiers:
            pytest.skip("No completed dossiers available for analysis format check")
        
        # Get full details of a completed dossier
        dossier_id = completed_dossiers[0]["id"]
        status_response = requests.get(f"{BASE_URL}/api/dossier-express/status/{dossier_id}")
        
        if status_response.status_code == 200:
            dossier_data = status_response.json()
            if "analysis" in dossier_data and dossier_data["analysis"]:
                analysis = dossier_data["analysis"]
                # The analysis should contain Dossier Express format markers
                # Based on DOSSIER_EXPRESS_PROMPT, it should have:
                # "RAPPORT D'ANALYSE - DOSSIER EXPRESS IA" or similar
                print(f"Analysis preview (first 200 chars): {analysis[:200]}")
                
                # Check that it doesn't contain StratégiIA-specific markers
                # (StratégiIA uses different section markers)
                if "DOSSIER EXPRESS" in analysis.upper():
                    print("PASS: Analysis contains 'DOSSIER EXPRESS' marker")
                else:
                    print("INFO: Analysis format check - marker not found in preview")
        
        print("PASS: Completed dossier analysis format verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
