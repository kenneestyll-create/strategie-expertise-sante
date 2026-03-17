"""
Iteration 62: Test FREE vs PREMIUM separation for StratégiIA/Dossier Express

Features tested:
- Backend: GET /api/client/dossier-analysis returns has_dossier_express: false for free client
- Backend: Free client response only contains limited fields (no premium data)
- Backend: Premium fields are NOT in free response
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials for FREE client (no completed dossier_express)
FREE_CLIENT_EMAIL = "test-analysis@test.com"
FREE_CLIENT_PASSWORD = "Password123!"

# Expected fields for FREE client response
FREE_CLIENT_EXPECTED_FIELDS = {
    "has_dossier_express",
    "score",
    "dynamic_message",
    "actionable_count", 
    "case_type",
    "summary"
}

# Premium fields that should NOT be in FREE response
PREMIUM_ONLY_FIELDS = {
    "key_metrics",
    "score_breakdown",
    "weak_points",
    "risk_alerts",
    "predictions",
    "recommended_actions",
    "premium_cta",
    "missing_documents",
    "found_documents"
}


@pytest.fixture(scope="module")
def free_client_token():
    """Get auth token for free client (no completed dossier_express)"""
    response = requests.post(
        f"{BASE_URL}/api/client/login",
        json={"email": FREE_CLIENT_EMAIL, "password": FREE_CLIENT_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def free_client_dossier_analysis(free_client_token):
    """Fetch dossier analysis for free client"""
    response = requests.get(
        f"{BASE_URL}/api/client/dossier-analysis",
        headers={"Authorization": f"Bearer {free_client_token}"}
    )
    assert response.status_code == 200, f"Dossier analysis failed: {response.text}"
    return response.json()


class TestFreeClientDossierAnalysis:
    """Test that free client gets limited response without premium features"""
    
    def test_has_dossier_express_is_false(self, free_client_dossier_analysis):
        """Free client should have has_dossier_express: false"""
        data = free_client_dossier_analysis
        assert "has_dossier_express" in data, "has_dossier_express field missing"
        assert data["has_dossier_express"] is False, f"Expected has_dossier_express=False, got {data['has_dossier_express']}"
    
    def test_score_field_present(self, free_client_dossier_analysis):
        """Free client should have score field"""
        data = free_client_dossier_analysis
        assert "score" in data, "score field missing"
        assert isinstance(data["score"], int), f"score should be int, got {type(data['score'])}"
    
    def test_dynamic_message_present(self, free_client_dossier_analysis):
        """Free client should have dynamic_message field"""
        data = free_client_dossier_analysis
        assert "dynamic_message" in data, "dynamic_message field missing"
        assert isinstance(data["dynamic_message"], dict), "dynamic_message should be dict"
    
    def test_actionable_count_present(self, free_client_dossier_analysis):
        """Free client should have actionable_count field"""
        data = free_client_dossier_analysis
        assert "actionable_count" in data, "actionable_count field missing"
    
    def test_case_type_present(self, free_client_dossier_analysis):
        """Free client should have case_type field"""
        data = free_client_dossier_analysis
        assert "case_type" in data, "case_type field missing"
    
    def test_summary_present(self, free_client_dossier_analysis):
        """Free client should have summary field"""
        data = free_client_dossier_analysis
        assert "summary" in data, "summary field missing"
        assert isinstance(data["summary"], dict), "summary should be dict"
    
    def test_only_expected_fields_returned(self, free_client_dossier_analysis):
        """Free client response should only contain expected fields"""
        data = free_client_dossier_analysis
        response_fields = set(data.keys())
        
        # All expected fields should be present
        missing_fields = FREE_CLIENT_EXPECTED_FIELDS - response_fields
        assert not missing_fields, f"Missing expected fields: {missing_fields}"
        
        # No extra fields beyond expected
        extra_fields = response_fields - FREE_CLIENT_EXPECTED_FIELDS
        assert not extra_fields, f"Unexpected fields in free client response: {extra_fields}"


class TestPremiumFieldsNotInFreeResponse:
    """Test that premium-only fields are NOT present in free client response"""
    
    def test_key_metrics_not_present(self, free_client_dossier_analysis):
        """key_metrics should NOT be in free client response"""
        assert "key_metrics" not in free_client_dossier_analysis, "key_metrics should not be in free response"
    
    def test_score_breakdown_not_present(self, free_client_dossier_analysis):
        """score_breakdown should NOT be in free client response"""
        assert "score_breakdown" not in free_client_dossier_analysis, "score_breakdown should not be in free response"
    
    def test_weak_points_not_present(self, free_client_dossier_analysis):
        """weak_points should NOT be in free client response"""
        assert "weak_points" not in free_client_dossier_analysis, "weak_points should not be in free response"
    
    def test_risk_alerts_not_present(self, free_client_dossier_analysis):
        """risk_alerts should NOT be in free client response"""
        assert "risk_alerts" not in free_client_dossier_analysis, "risk_alerts should not be in free response"
    
    def test_predictions_not_present(self, free_client_dossier_analysis):
        """predictions should NOT be in free client response"""
        assert "predictions" not in free_client_dossier_analysis, "predictions should not be in free response"
    
    def test_recommended_actions_not_present(self, free_client_dossier_analysis):
        """recommended_actions should NOT be in free client response"""
        assert "recommended_actions" not in free_client_dossier_analysis, "recommended_actions should not be in free response"
    
    def test_premium_cta_not_present(self, free_client_dossier_analysis):
        """premium_cta should NOT be in free client response"""
        assert "premium_cta" not in free_client_dossier_analysis, "premium_cta should not be in free response"
    
    def test_missing_documents_not_present(self, free_client_dossier_analysis):
        """missing_documents should NOT be in free client response"""
        assert "missing_documents" not in free_client_dossier_analysis, "missing_documents should not be in free response"
    
    def test_found_documents_not_present(self, free_client_dossier_analysis):
        """found_documents should NOT be in free client response"""
        assert "found_documents" not in free_client_dossier_analysis, "found_documents should not be in free response"


class TestFreeClientResponseIntegrity:
    """Test the structure and content of free client response fields"""
    
    def test_dynamic_message_has_required_keys(self, free_client_dossier_analysis):
        """dynamic_message should have title, message, tone, color"""
        dm = free_client_dossier_analysis.get("dynamic_message", {})
        assert "title" in dm, "dynamic_message missing 'title'"
        assert "message" in dm, "dynamic_message missing 'message'"
        assert "tone" in dm, "dynamic_message missing 'tone'"
        assert "color" in dm, "dynamic_message missing 'color'"
    
    def test_summary_has_required_keys(self, free_client_dossier_analysis):
        """summary should have document count fields"""
        summary = free_client_dossier_analysis.get("summary", {})
        expected_keys = {"total_documents", "validated", "pending", "illisible", "analyses_ia", "dossier_express", "premium"}
        missing = expected_keys - set(summary.keys())
        assert not missing, f"summary missing keys: {missing}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
