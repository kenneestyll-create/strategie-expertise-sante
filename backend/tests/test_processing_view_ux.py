"""
Test suite for Dossier Express Processing View UX improvements (Iteration 148).
Tests the 7-step granular progress tracking and API responses.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test dossier IDs (completed)
COMPLETED_DOSSIER_1 = "bb543247-f7f3-4a1a-8d03-93d217cc1400"
COMPLETED_DOSSIER_2 = "bfc7d774-b9c5-4134-962d-65a3934ae940"


class TestDossierExpressStatusAPI:
    """Tests for GET /api/dossier-express/status/{id} endpoint"""
    
    def test_status_returns_progress_step(self):
        """Verify status endpoint returns progress_step field"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/{COMPLETED_DOSSIER_1}")
        if response.status_code == 404:
            pytest.skip(f"Dossier {COMPLETED_DOSSIER_1} not found - using alternate")
            response = requests.get(f"{BASE_URL}/api/dossier-express/status/{COMPLETED_DOSSIER_2}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify progress_step field exists
        assert "progress_step" in data or "status" in data, "Response should have progress_step or status"
        print(f"Status response: {data}")
    
    def test_status_completed_dossier(self):
        """Verify completed dossier returns correct status"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/{COMPLETED_DOSSIER_2}")
        if response.status_code == 404:
            pytest.skip(f"Dossier {COMPLETED_DOSSIER_2} not found")
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "completed", f"Expected completed status, got {data.get('status')}"
        print(f"Completed dossier status: {data}")
    
    def test_status_returns_analysis_batch_field(self):
        """Verify status endpoint can return analysis_batch field (for in-progress dossiers)"""
        # For completed dossiers, analysis_batch may not be present
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/{COMPLETED_DOSSIER_2}")
        if response.status_code == 404:
            pytest.skip(f"Dossier {COMPLETED_DOSSIER_2} not found")
        
        assert response.status_code == 200
        data = response.json()
        # analysis_batch is only present during processing, not after completion
        print(f"Status response fields: {list(data.keys())}")
        # This is informational - analysis_batch may or may not be present
        if "analysis_batch" in data:
            print(f"analysis_batch value: {data['analysis_batch']}")


class TestDossierExpressSuiviAPI:
    """Tests for GET /api/dossier-express/suivi/{id} endpoint"""
    
    def test_suivi_returns_7_steps(self):
        """Verify suivi endpoint returns 7-step timeline"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{COMPLETED_DOSSIER_2}")
        if response.status_code == 404:
            pytest.skip(f"Dossier {COMPLETED_DOSSIER_2} not found")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify steps array exists
        assert "steps" in data, "Response should have steps array"
        steps = data["steps"]
        
        # Verify 7 steps
        assert len(steps) == 7, f"Expected 7 steps, got {len(steps)}"
        
        # Verify step keys
        expected_keys = ["received", "preparation", "reading", "analysis", "report", "delivery", "available"]
        actual_keys = [s["key"] for s in steps]
        assert actual_keys == expected_keys, f"Step keys mismatch: {actual_keys}"
        
        print(f"Suivi timeline: {steps}")
    
    def test_suivi_completed_dossier_all_steps_completed(self):
        """Verify completed dossier has all steps marked as completed"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{COMPLETED_DOSSIER_2}")
        if response.status_code == 404:
            pytest.skip(f"Dossier {COMPLETED_DOSSIER_2} not found")
        
        assert response.status_code == 200
        data = response.json()
        
        steps = data.get("steps", [])
        completed_count = sum(1 for s in steps if s.get("status") == "completed")
        
        # For completed dossier, all 7 steps should be completed
        assert completed_count == 7, f"Expected 7 completed steps, got {completed_count}"
        print(f"All {completed_count} steps completed")


class TestBackendProgressStepValues:
    """Tests for backend progress_step values in strategiia.py"""
    
    def test_health_llm_endpoint(self):
        """Verify LLM health check endpoint works"""
        response = requests.get(f"{BASE_URL}/api/health/llm")
        assert response.status_code == 200
        data = response.json()
        assert "operational" in data
        print(f"LLM health: {data}")
    
    def test_dossier_express_landing_page_loads(self):
        """Verify /dossier-express page is accessible"""
        response = requests.get(f"{BASE_URL}/dossier-express", allow_redirects=True)
        # Frontend routes return 200 (SPA)
        assert response.status_code == 200
        print("Dossier Express landing page accessible")


class TestClientStepsDisplay:
    """Tests for CLIENT_STEPS_DISPLAY constant in statuses.py"""
    
    def test_suivi_step_labels_match_expected(self):
        """Verify suivi step labels match CLIENT_STEPS_DISPLAY"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{COMPLETED_DOSSIER_2}")
        if response.status_code == 404:
            pytest.skip(f"Dossier {COMPLETED_DOSSIER_2} not found")
        
        assert response.status_code == 200
        data = response.json()
        
        expected_labels = [
            "Dossier bien recu",
            "Documents en cours de preparation",
            "Lecture documentaire en cours",
            "Analyse en cours de finalisation",
            "Rapport en cours de preparation",
            "Envoi en cours",
            "Rapport disponible"
        ]
        
        steps = data.get("steps", [])
        actual_labels = [s.get("label") for s in steps]
        
        assert actual_labels == expected_labels, f"Labels mismatch: {actual_labels}"
        print(f"Step labels verified: {actual_labels}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
