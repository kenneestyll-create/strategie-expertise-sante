"""
Test suite for Knowledge Patterns Engine (intelligent selection + injection)
Tests: 
- GET /api/knowledge-patterns/stats shows 14 total patterns, 14 validated, 0 pending
- GET /api/knowledge-patterns returns 14 patterns with correct fields
- POST /api/knowledge-patterns/seed returns skipped (base non vide)
- Engine matching logic via direct function testing
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


class TestKnowledgePatternsEngine:
    """Knowledge Patterns Engine tests - seed, stats, matching"""
    
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
    
    # ==================== STATS VERIFICATION (14 patterns) ====================
    
    def test_stats_shows_14_patterns(self, auth_headers):
        """GET /api/knowledge-patterns/stats should show 14 total patterns, 14 validated, 0 pending"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns/stats", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Stats response: total={data.get('total')}, validated={data.get('validated')}, pending={data.get('pending')}")
        
        # Verify 14 seed patterns exist
        assert data["total"] == 14, f"Expected 14 total patterns, got {data['total']}"
        assert data["validated"] == 14, f"Expected 14 validated patterns, got {data['validated']}"
        assert data["pending"] == 0, f"Expected 0 pending patterns, got {data['pending']}"
        
        # Verify by_category and by_type are populated
        assert "by_category" in data, "Response should contain 'by_category'"
        assert "by_type" in data, "Response should contain 'by_type'"
        assert len(data["by_category"]) > 0, "by_category should not be empty"
        assert len(data["by_type"]) > 0, "by_type should not be empty"
        
        print(f"PASS: Stats show 14 total, 14 validated, 0 pending")
        print(f"  by_category: {data['by_category']}")
        print(f"  by_type: {data['by_type']}")
    
    # ==================== LIST VERIFICATION (14 patterns with correct fields) ====================
    
    def test_list_returns_14_patterns_with_correct_fields(self, auth_headers):
        """GET /api/knowledge-patterns should return 14 patterns with all required fields"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["count"] == 14, f"Expected 14 patterns, got {data['count']}"
        
        patterns = data["patterns"]
        assert len(patterns) == 14, f"Expected 14 patterns in list, got {len(patterns)}"
        
        # Required fields for each pattern
        required_fields = [
            "id", "categorie_dossier", "pattern_type", "description",
            "niveau_confiance", "usage_autorise", "source_type", "created_at"
        ]
        
        for i, pattern in enumerate(patterns):
            for field in required_fields:
                assert field in pattern, f"Pattern {i} missing required field: {field}"
            
            # All seed patterns should be validated
            assert pattern["usage_autorise"] == True, f"Pattern {i} should be validated (usage_autorise=True)"
            assert pattern["source_type"] == "seed", f"Pattern {i} should have source_type='seed'"
            assert pattern["validated_by"] == "system_seed", f"Pattern {i} should have validated_by='system_seed'"
        
        print(f"PASS: GET /api/knowledge-patterns returns 14 patterns with all required fields")
        
        # Print pattern types distribution
        pattern_types = {}
        for p in patterns:
            pt = p["pattern_type"]
            pattern_types[pt] = pattern_types.get(pt, 0) + 1
        print(f"  Pattern types: {pattern_types}")
    
    # ==================== SEED ENDPOINT (should skip if base non vide) ====================
    
    def test_seed_endpoint_skips_when_base_not_empty(self, auth_headers):
        """POST /api/knowledge-patterns/seed should return skipped when base is not empty"""
        response = requests.post(f"{BASE_URL}/api/knowledge-patterns/seed", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "skipped", f"Expected status='skipped', got {data.get('status')}"
        assert "reason" in data, "Response should contain 'reason'"
        assert "14" in data["reason"] or "non vide" in data["reason"].lower(), f"Reason should mention 14 patterns or 'non vide': {data['reason']}"
        
        print(f"PASS: POST /api/knowledge-patterns/seed returns skipped: {data['reason']}")
    
    def test_seed_endpoint_requires_auth(self):
        """POST /api/knowledge-patterns/seed without auth should return 401/403"""
        response = requests.post(f"{BASE_URL}/api/knowledge-patterns/seed")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: POST /api/knowledge-patterns/seed requires authentication")
    
    # ==================== PATTERN CONTENT VERIFICATION ====================
    
    def test_patterns_have_expected_categories(self, auth_headers):
        """Verify patterns cover expected categories from seed_patterns.py"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns", headers=auth_headers)
        data = response.json()
        patterns = data["patterns"]
        
        categories = set(p["categorie_dossier"] for p in patterns)
        expected_categories = {
            "maladie_professionnelle",
            "litige_assurantiel", 
            "contestation_taux_ipp",
            "accident_travail"
        }
        
        for cat in expected_categories:
            assert cat in categories, f"Expected category '{cat}' not found in patterns"
        
        print(f"PASS: Patterns cover all expected categories: {categories}")
    
    def test_patterns_have_expected_types(self, auth_headers):
        """Verify patterns cover expected pattern_types from seed_patterns.py"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns", headers=auth_headers)
        data = response.json()
        patterns = data["patterns"]
        
        pattern_types = set(p["pattern_type"] for p in patterns)
        expected_types = {
            "blocage",
            "vigilance",
            "levier",
            "erreur_frequente",
            "piece_manquante"
        }
        
        for pt in expected_types:
            assert pt in pattern_types, f"Expected pattern_type '{pt}' not found in patterns"
        
        print(f"PASS: Patterns cover all expected types: {pattern_types}")
    
    # ==================== PATTERN MATCHING SCENARIOS ====================
    
    def test_patterns_for_mp_conduite_exist(self, auth_headers):
        """Verify patterns exist for MP + transport_conduite scenario"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns", headers=auth_headers)
        data = response.json()
        patterns = data["patterns"]
        
        # Find patterns matching MP + conduite
        mp_conduite_patterns = [
            p for p in patterns 
            if p["categorie_dossier"] == "maladie_professionnelle" 
            and p.get("metier") == "transport_conduite"
        ]
        
        assert len(mp_conduite_patterns) >= 1, "Should have at least 1 pattern for MP + transport_conduite"
        print(f"PASS: Found {len(mp_conduite_patterns)} patterns for MP + transport_conduite")
        for p in mp_conduite_patterns:
            print(f"  - {p['pattern_type']}: {p['description'][:80]}...")
    
    def test_patterns_for_litige_ipt_exist(self, auth_headers):
        """Verify patterns exist for litige_assurantiel + IPT scenario"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns", headers=auth_headers)
        data = response.json()
        patterns = data["patterns"]
        
        # Find patterns matching litige + IPT
        litige_ipt_patterns = [
            p for p in patterns 
            if p["categorie_dossier"] == "litige_assurantiel" 
            and p.get("type_garantie") == "IPT"
        ]
        
        assert len(litige_ipt_patterns) >= 1, "Should have at least 1 pattern for litige_assurantiel + IPT"
        print(f"PASS: Found {len(litige_ipt_patterns)} patterns for litige_assurantiel + IPT")
        for p in litige_ipt_patterns:
            print(f"  - {p['pattern_type']}: {p['description'][:80]}...")
    
    def test_patterns_for_contestation_ipp_exist(self, auth_headers):
        """Verify patterns exist for contestation_taux_ipp scenario"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns", headers=auth_headers)
        data = response.json()
        patterns = data["patterns"]
        
        # Find patterns matching contestation_taux_ipp
        contestation_patterns = [
            p for p in patterns 
            if p["categorie_dossier"] == "contestation_taux_ipp"
        ]
        
        assert len(contestation_patterns) >= 2, "Should have at least 2 patterns for contestation_taux_ipp"
        print(f"PASS: Found {len(contestation_patterns)} patterns for contestation_taux_ipp")
        for p in contestation_patterns:
            print(f"  - {p['pattern_type']}: {p['description'][:80]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
