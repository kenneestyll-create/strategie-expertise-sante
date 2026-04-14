"""
Test suite for Knowledge Patterns API (RGPD-compliant improvement patterns)
Tests: GET list, POST create, PUT validate, DELETE, GET stats
All endpoints require admin authentication.
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD


class TestKnowledgePatternsAPI:
    """Knowledge Patterns CRUD tests with admin authentication"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in login response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        """Headers with admin Bearer token"""
        return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    # ==================== GET /api/knowledge-patterns ====================
    
    def test_list_patterns_requires_auth(self):
        """GET /api/knowledge-patterns without auth should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: GET /api/knowledge-patterns requires authentication")
    
    def test_list_patterns_with_auth(self, auth_headers):
        """GET /api/knowledge-patterns with admin auth should return list"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "patterns" in data, "Response should contain 'patterns' key"
        assert "count" in data, "Response should contain 'count' key"
        assert isinstance(data["patterns"], list), "patterns should be a list"
        assert isinstance(data["count"], int), "count should be an integer"
        print(f"PASS: GET /api/knowledge-patterns returns {data['count']} patterns")
    
    # ==================== POST /api/knowledge-patterns ====================
    
    def test_create_pattern_requires_auth(self):
        """POST /api/knowledge-patterns without auth should return 401/403"""
        response = requests.post(
            f"{BASE_URL}/api/knowledge-patterns",
            json={"categorie_dossier": "test", "pattern_type": "blocage", "description": "test"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: POST /api/knowledge-patterns requires authentication")
    
    def test_create_pattern_missing_fields(self, auth_headers):
        """POST /api/knowledge-patterns with missing required fields should return 400"""
        # Missing categorie_dossier
        response = requests.post(
            f"{BASE_URL}/api/knowledge-patterns",
            headers=auth_headers,
            json={"pattern_type": "blocage", "description": "test"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        # Missing pattern_type
        response = requests.post(
            f"{BASE_URL}/api/knowledge-patterns",
            headers=auth_headers,
            json={"categorie_dossier": "test", "description": "test"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        # Missing description
        response = requests.post(
            f"{BASE_URL}/api/knowledge-patterns",
            headers=auth_headers,
            json={"categorie_dossier": "test", "pattern_type": "blocage"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: POST /api/knowledge-patterns validates required fields")
    
    def test_create_pattern_description_too_long(self, auth_headers):
        """POST /api/knowledge-patterns with description > 500 chars should return 400"""
        long_description = "A" * 501
        response = requests.post(
            f"{BASE_URL}/api/knowledge-patterns",
            headers=auth_headers,
            json={
                "categorie_dossier": "maladie_professionnelle",
                "pattern_type": "blocage",
                "description": long_description
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: POST /api/knowledge-patterns rejects description > 500 chars")
    
    def test_create_pattern_success(self, auth_headers):
        """POST /api/knowledge-patterns with valid data should create pattern"""
        test_id = str(uuid.uuid4())[:8]
        payload = {
            "categorie_dossier": "maladie_professionnelle",
            "metier": "transport_conduite",
            "type_sinistre": "mp_tableau_57",
            "type_garantie": "IPP",
            "blocage_principal": "probatoire",
            "pattern_type": "blocage",
            "description": f"TEST_{test_id} Pattern de blocage probatoire frequemment rencontre dans les dossiers MP tableau 57",
            "niveau_confiance": "eleve",
            "source_type": "manuel",
            "tags": ["test", "mp", "probatoire"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/knowledge-patterns",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain 'id'"
        assert data["categorie_dossier"] == payload["categorie_dossier"]
        assert data["pattern_type"] == payload["pattern_type"]
        assert data["description"] == payload["description"]
        assert data["usage_autorise"] == False, "New patterns should have usage_autorise=False"
        assert data["validated_by"] is None, "New patterns should have validated_by=None"
        
        # Store pattern_id for later tests
        self.__class__.created_pattern_id = data["id"]
        print(f"PASS: POST /api/knowledge-patterns created pattern {data['id']}")
        return data["id"]
    
    # ==================== PUT /api/knowledge-patterns/{id}/validate ====================
    
    def test_validate_pattern_requires_auth(self):
        """PUT /api/knowledge-patterns/{id}/validate without auth should return 401/403"""
        response = requests.put(f"{BASE_URL}/api/knowledge-patterns/fake-id/validate")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: PUT /api/knowledge-patterns/{id}/validate requires authentication")
    
    def test_validate_pattern_not_found(self, auth_headers):
        """PUT /api/knowledge-patterns/{id}/validate with invalid id should return 404"""
        response = requests.put(
            f"{BASE_URL}/api/knowledge-patterns/nonexistent-id-12345/validate",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: PUT /api/knowledge-patterns/{id}/validate returns 404 for invalid id")
    
    def test_validate_pattern_success(self, auth_headers):
        """PUT /api/knowledge-patterns/{id}/validate should validate pattern"""
        pattern_id = getattr(self.__class__, 'created_pattern_id', None)
        if not pattern_id:
            pytest.skip("No pattern created in previous test")
        
        response = requests.put(
            f"{BASE_URL}/api/knowledge-patterns/{pattern_id}/validate",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "validated"
        assert data["id"] == pattern_id
        
        # Verify pattern is now validated by fetching list
        list_response = requests.get(f"{BASE_URL}/api/knowledge-patterns", headers=auth_headers)
        patterns = list_response.json()["patterns"]
        validated_pattern = next((p for p in patterns if p["id"] == pattern_id), None)
        assert validated_pattern is not None, "Pattern should exist in list"
        assert validated_pattern["usage_autorise"] == True, "Pattern should be validated"
        assert validated_pattern["validated_by"] is not None, "validated_by should be set"
        
        print(f"PASS: PUT /api/knowledge-patterns/{pattern_id}/validate validated pattern")
    
    # ==================== GET /api/knowledge-patterns/stats ====================
    
    def test_stats_requires_auth(self):
        """GET /api/knowledge-patterns/stats without auth should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns/stats")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: GET /api/knowledge-patterns/stats requires authentication")
    
    def test_stats_with_auth(self, auth_headers):
        """GET /api/knowledge-patterns/stats should return aggregated stats"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns/stats", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total" in data, "Response should contain 'total'"
        assert "validated" in data, "Response should contain 'validated'"
        assert "pending" in data, "Response should contain 'pending'"
        assert "by_category" in data, "Response should contain 'by_category'"
        assert "by_type" in data, "Response should contain 'by_type'"
        
        assert isinstance(data["total"], int)
        assert isinstance(data["validated"], int)
        assert isinstance(data["pending"], int)
        assert data["total"] == data["validated"] + data["pending"], "total should equal validated + pending"
        
        print(f"PASS: GET /api/knowledge-patterns/stats returns total={data['total']}, validated={data['validated']}, pending={data['pending']}")
    
    # ==================== DELETE /api/knowledge-patterns/{id} ====================
    
    def test_delete_pattern_requires_auth(self):
        """DELETE /api/knowledge-patterns/{id} without auth should return 401/403"""
        response = requests.delete(f"{BASE_URL}/api/knowledge-patterns/fake-id")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: DELETE /api/knowledge-patterns/{id} requires authentication")
    
    def test_delete_pattern_not_found(self, auth_headers):
        """DELETE /api/knowledge-patterns/{id} with invalid id should return 404"""
        response = requests.delete(
            f"{BASE_URL}/api/knowledge-patterns/nonexistent-id-12345",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: DELETE /api/knowledge-patterns/{id} returns 404 for invalid id")
    
    def test_delete_pattern_success(self, auth_headers):
        """DELETE /api/knowledge-patterns/{id} should delete pattern"""
        pattern_id = getattr(self.__class__, 'created_pattern_id', None)
        if not pattern_id:
            pytest.skip("No pattern created in previous test")
        
        response = requests.delete(
            f"{BASE_URL}/api/knowledge-patterns/{pattern_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "deleted"
        assert data["id"] == pattern_id
        
        # Verify pattern is deleted by fetching list
        list_response = requests.get(f"{BASE_URL}/api/knowledge-patterns", headers=auth_headers)
        patterns = list_response.json()["patterns"]
        deleted_pattern = next((p for p in patterns if p["id"] == pattern_id), None)
        assert deleted_pattern is None, "Pattern should not exist in list after deletion"
        
        print(f"PASS: DELETE /api/knowledge-patterns/{pattern_id} deleted pattern")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
