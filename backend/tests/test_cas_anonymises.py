"""
Backend tests for StrategiIA Phase 2 — cas-anonymises CRUD, import, stats endpoints
Iteration 33 testing
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCasAnonymises:
    """Test cas-anonymises CRUD endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login as admin and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        assert response.status_code == 200, f"Auth failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Return headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    # ============== TEST 1: POST /api/admin/cas-anonymises ==============
    def test_create_cas_at_favorable(self, auth_headers):
        """Test 1: POST creates a case with type_dossier=AT, resultat=Favorable"""
        payload = {
            "type_dossier": "AT",
            "resultat": "Favorable",
            "regime": "Général",
            "duree": "12 mois",
            "strategie": "TEST_Contestation initiale",
            "score_pertinence": 85,
            "notes": "TEST_Cas test iteration 33"
        }
        response = requests.post(f"{BASE_URL}/api/admin/cas-anonymises", json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Create failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "id" in data
        # Store for later tests
        TestCasAnonymises.created_case_id = data["id"]
        print(f"✓ Created case with ID: {data['id']}")
    
    # ============== TEST 2: PATCH /api/admin/cas-anonymises/{id} ==============
    def test_update_cas_defavorable(self, auth_headers):
        """Test 2: PATCH updates the case (change resultat to Défavorable)"""
        case_id = getattr(TestCasAnonymises, 'created_case_id', None)
        assert case_id, "No case_id from previous test"
        
        payload = {"resultat": "Défavorable"}
        response = requests.patch(f"{BASE_URL}/api/admin/cas-anonymises/{case_id}", json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Update failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print(f"✓ Updated case {case_id} to resultat=Défavorable")
    
    # ============== TEST 3: GET /api/admin/cas-anonymises ==============
    def test_get_cas_list_returns_created_case(self, auth_headers):
        """Test 3: GET returns the created case in items array"""
        response = requests.get(f"{BASE_URL}/api/admin/cas-anonymises", headers=auth_headers)
        assert response.status_code == 200, f"GET failed: {response.text}"
        data = response.json()
        assert "items" in data, "Response missing 'items'"
        assert "total" in data, "Response missing 'total'"
        
        # Find the test case
        case_id = getattr(TestCasAnonymises, 'created_case_id', None)
        found_case = next((c for c in data["items"] if c.get("id") == case_id), None)
        assert found_case is not None, f"Created case {case_id} not found in list"
        assert found_case.get("type_dossier") == "AT"
        assert found_case.get("resultat") == "Défavorable"  # Should be updated
        print(f"✓ GET returned {data['total']} cases, found test case with type_dossier=AT, resultat=Défavorable")
    
    # ============== TEST 4: POST /api/admin/cas-anonymises/import ==============
    def test_import_cas_mp_msa(self, auth_headers):
        """Test 4: POST import with {cases:[{type_dossier:'MP',resultat:'En cours',regime:'MSA'}]} imports 1 case"""
        payload = {
            "cases": [
                {
                    "type_dossier": "MP",
                    "resultat": "En cours",
                    "regime": "MSA",
                    "duree": "6 mois",
                    "strategie": "TEST_Import iteration 33",
                    "score_pertinence": 70,
                    "notes": "TEST_Imported via bulk import"
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/api/admin/cas-anonymises/import", json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Import failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert data.get("imported") == 1, f"Expected 1 imported, got {data.get('imported')}"
        print(f"✓ Imported 1 case via bulk import endpoint")
    
    # ============== TEST 5: GET /api/admin/cas-anonymises/stats ==============
    def test_get_cas_stats(self, auth_headers):
        """Test 5: GET stats returns total count and by_type breakdown"""
        response = requests.get(f"{BASE_URL}/api/admin/cas-anonymises/stats", headers=auth_headers)
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        assert "total" in data, "Response missing 'total'"
        assert "by_type" in data, "Response missing 'by_type'"
        assert "by_regime" in data, "Response missing 'by_regime'"
        assert data["total"] >= 2, f"Expected at least 2 cases (created + imported), got {data['total']}"
        print(f"✓ Stats returned total={data['total']}, by_type={data['by_type']}")
    
    # ============== CLEANUP: Delete test cases ==============
    def test_cleanup_delete_created_case(self, auth_headers):
        """Cleanup: Delete the test case we created"""
        case_id = getattr(TestCasAnonymises, 'created_case_id', None)
        if case_id:
            response = requests.delete(f"{BASE_URL}/api/admin/cas-anonymises/{case_id}", headers=auth_headers)
            assert response.status_code == 200, f"Delete failed: {response.text}"
            print(f"✓ Deleted test case {case_id}")
    
    def test_cleanup_delete_imported_cases(self, auth_headers):
        """Cleanup: Delete imported test cases by searching for TEST_ prefix in notes"""
        response = requests.get(f"{BASE_URL}/api/admin/cas-anonymises", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            test_cases = [c for c in data.get("items", []) if c.get("notes", "").startswith("TEST_")]
            for case in test_cases:
                requests.delete(f"{BASE_URL}/api/admin/cas-anonymises/{case['id']}", headers=auth_headers)
            print(f"✓ Cleaned up {len(test_cases)} test cases")


class TestSearchIndexEntries:
    """Test that search index includes enriched entries"""
    
    def test_search_glossaire_entry(self):
        """Verify searchIndex.js includes 'Glossaire santé & droit' entry"""
        # This is a static frontend test - we verify the file content contains the entry
        # The actual search behavior will be tested via Playwright
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "glossaire", "/app/frontend/src/data/searchIndex.js"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.returncode == 0 else 0
        assert count > 0, "searchIndex.js should contain 'glossaire' entries"
        print(f"✓ searchIndex.js contains {count} glossaire references")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
