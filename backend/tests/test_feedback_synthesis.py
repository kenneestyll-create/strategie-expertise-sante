"""
Test suite for Feedback Synthesis endpoint (GET /api/feedback/synthesis)
Tests the rule-based intelligent synthesis of collected feedbacks.
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestFeedbackSynthesis:
    """Tests for GET /api/feedback/synthesis endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for authenticated requests"""
        self.admin_token = None
        try:
            login_res = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": "admin@accompagn-sante.fr", "password": "Admin2024!"}
            )
            if login_res.status_code == 200:
                self.admin_token = login_res.json().get("access_token")
        except Exception as e:
            print(f"Login failed: {e}")
    
    def test_synthesis_requires_auth(self):
        """GET /api/feedback/synthesis should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/feedback/synthesis")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Synthesis endpoint requires authentication")
    
    def test_synthesis_with_invalid_token(self):
        """GET /api/feedback/synthesis should return 401 with invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/feedback/synthesis",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Synthesis endpoint rejects invalid token")
    
    def test_synthesis_returns_structured_response(self):
        """GET /api/feedback/synthesis should return structured synthesis data"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/feedback/synthesis",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check required top-level fields
        assert "irritants" in data, "Missing 'irritants' field"
        assert "besoins" in data, "Missing 'besoins' field"
        assert "clarte" in data, "Missing 'clarte' field"
        assert "recommandations" in data, "Missing 'recommandations' field"
        assert "sources" in data, "Missing 'sources' field"
        assert "total" in data, "Missing 'total' field"
        assert "seuil_signal_fort" in data, "Missing 'seuil_signal_fort' field"
        
        print(f"PASS: Synthesis returns all required fields (total={data['total']})")
    
    def test_synthesis_irritants_have_signal_field(self):
        """Irritants should have 'signal' field with 'fort' or 'faible' value"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/feedback/synthesis",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        irritants = data.get("irritants", [])
        
        for irritant in irritants:
            assert "signal" in irritant, f"Irritant missing 'signal' field: {irritant}"
            assert irritant["signal"] in ["fort", "faible"], f"Invalid signal value: {irritant['signal']}"
            assert "theme" in irritant, "Irritant missing 'theme' field"
            assert "count" in irritant, "Irritant missing 'count' field"
            assert "pct" in irritant, "Irritant missing 'pct' field"
        
        print(f"PASS: All {len(irritants)} irritants have valid 'signal' field")
    
    def test_synthesis_besoins_have_signal_field(self):
        """Besoins should have 'signal' field with 'fort' or 'faible' value"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/feedback/synthesis",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        besoins = data.get("besoins", [])
        
        for besoin in besoins:
            assert "signal" in besoin, f"Besoin missing 'signal' field: {besoin}"
            assert besoin["signal"] in ["fort", "faible"], f"Invalid signal value: {besoin['signal']}"
            assert "theme" in besoin, "Besoin missing 'theme' field"
            assert "count" in besoin, "Besoin missing 'count' field"
            assert "pct" in besoin, "Besoin missing 'pct' field"
        
        print(f"PASS: All {len(besoins)} besoins have valid 'signal' field")
    
    def test_synthesis_clarte_structure(self):
        """Clarte should have oui/partiellement/non percentages and alerte boolean"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/feedback/synthesis",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        clarte = data.get("clarte", {})
        
        # Check clarte structure if there's data
        if clarte:
            # Check for oui/partiellement/non with count and pct
            for key in ["oui", "partiellement", "non"]:
                if key in clarte:
                    assert "count" in clarte[key], f"Clarte '{key}' missing 'count'"
                    assert "pct" in clarte[key], f"Clarte '{key}' missing 'pct'"
            
            # Check for alerte boolean
            assert "alerte" in clarte, "Clarte missing 'alerte' field"
            assert isinstance(clarte["alerte"], bool), "Clarte 'alerte' should be boolean"
            
            print(f"PASS: Clarte structure valid (alerte={clarte['alerte']})")
        else:
            print("PASS: Clarte is empty (no clarte data)")
    
    def test_synthesis_seuil_signal_fort_calculation(self):
        """Seuil signal fort should be max(2, 15% of total)"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/feedback/synthesis",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        total = data.get("total", 0)
        seuil = data.get("seuil_signal_fort", 0)
        
        expected_seuil = max(2, int(total * 0.15))
        assert seuil == expected_seuil, f"Expected seuil {expected_seuil}, got {seuil}"
        
        print(f"PASS: Seuil signal fort correctly calculated ({seuil} for {total} feedbacks)")


class TestFeedbackDossierExpressSource:
    """Tests for POST /api/feedback with source='dossier_express'"""
    
    def test_submit_feedback_with_dossier_express_source(self):
        """POST /api/feedback should accept feedback with source='dossier_express'"""
        unique_id = str(uuid.uuid4())[:8]
        
        response = requests.post(
            f"{BASE_URL}/api/feedback",
            json={
                "frein": f"TEST_DOSSIER_EXPRESS_{unique_id} - Frein test",
                "besoin": "Besoin test dossier express",
                "clarte": "oui",
                "commentaire": "Test commentaire",
                "source": "dossier_express",
                "type_dossier": "MDPH"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        
        print("PASS: Feedback with source='dossier_express' accepted")
    
    def test_dossier_express_feedback_appears_in_synthesis_sources(self):
        """Dossier express feedbacks should appear in synthesis sources"""
        # First submit a feedback
        unique_id = str(uuid.uuid4())[:8]
        submit_res = requests.post(
            f"{BASE_URL}/api/feedback",
            json={
                "frein": f"TEST_SYNTH_SOURCE_{unique_id}",
                "clarte": "partiellement",
                "source": "dossier_express"
            }
        )
        assert submit_res.status_code == 200
        
        # Get admin token
        login_res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@accompagn-sante.fr", "password": "Admin2024!"}
        )
        if login_res.status_code != 200:
            pytest.skip("Admin login failed")
        
        token = login_res.json().get("access_token")
        
        # Check synthesis
        synth_res = requests.get(
            f"{BASE_URL}/api/feedback/synthesis",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert synth_res.status_code == 200
        
        data = synth_res.json()
        sources = data.get("sources", {})
        
        assert "dossier_express" in sources, "dossier_express not in synthesis sources"
        assert sources["dossier_express"] > 0, "dossier_express count should be > 0"
        
        print(f"PASS: dossier_express appears in synthesis sources (count={sources['dossier_express']})")


class TestFeedbackSynthesisRecommandations:
    """Tests for synthesis recommandations generation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.admin_token = None
        try:
            login_res = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": "admin@accompagn-sante.fr", "password": "Admin2024!"}
            )
            if login_res.status_code == 200:
                self.admin_token = login_res.json().get("access_token")
        except:
            pass
    
    def test_synthesis_generates_recommandations(self):
        """Synthesis should generate strategic recommandations"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/feedback/synthesis",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        recommandations = data.get("recommandations", [])
        
        # Should have recommandations if there's data
        if data.get("total", 0) > 0:
            assert isinstance(recommandations, list), "Recommandations should be a list"
            # Check recommandations are strings
            for r in recommandations:
                assert isinstance(r, str), f"Recommandation should be string: {r}"
            
            print(f"PASS: Synthesis generated {len(recommandations)} recommandations")
        else:
            print("PASS: No recommandations (no feedback data)")
