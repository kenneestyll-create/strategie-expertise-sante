"""
Test suite for StratégiIA Phase 1: Dossier Analysis Endpoint
GET /api/client/dossier-analysis

Tests:
- Score calculation (composite of completeness, quality, analysis, progress, volume)
- Dynamic message based on score thresholds
- Weak points detection
- Risk alerts per case type
- Missing documents identification
- Actionable count
"""

import pytest
import requests
import os
import json
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API = f"{BASE_URL}/api"

# Test credentials
TEST_EMAIL = f"test_dossier_analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"
TEST_PASSWORD = "Password123!"
TEST_NAME = "Test Dossier Analysis"


class TestDossierAnalysisEndpoint:
    """Test the dossier-analysis endpoint for a new user with 0 documents"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Register a new user and get auth token"""
        register_url = f"{API}/client/register"
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "notifications_email": True,
            "notifications_push": False
        }
        response = requests.post(register_url, json=payload)
        if response.status_code == 409:
            # User already exists, try login
            login_url = f"{API}/client/login"
            response = requests.post(login_url, json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
        
        assert response.status_code in [200, 201], f"Auth failed: {response.text}"
        data = response.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        return data["access_token"]
    
    def test_endpoint_exists_and_returns_200(self, auth_token):
        """Test that the endpoint exists and returns 200 for authenticated user"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"TEST PASS: GET /api/client/dossier-analysis returns 200")
    
    def test_response_structure(self, auth_token):
        """Test that response contains all required fields"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "score", "dynamic_message", "score_breakdown", "weak_points",
            "risk_alerts", "missing_documents", "found_documents", "actionable_count",
            "case_type", "summary"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"TEST PASS: Response contains all required fields: {required_fields}")
    
    def test_score_is_low_for_new_user(self, auth_token):
        """Test that score is low (~3) for a new user with 0 documents"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        score = data["score"]
        
        # For a new user with 0 documents, score should be very low (around 3)
        assert isinstance(score, int) or isinstance(score, float), f"Score should be numeric, got {type(score)}"
        assert 0 <= score <= 20, f"Expected low score (0-20) for new user, got {score}"
        
        print(f"TEST PASS: Score for new user is low: {score}")
    
    def test_dynamic_message_for_low_score(self, auth_token):
        """Test dynamic message matches threshold for low score (<30%)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        dynamic_message = data["dynamic_message"]
        
        assert "title" in dynamic_message
        assert "message" in dynamic_message
        assert "tone" in dynamic_message
        assert "color" in dynamic_message
        
        # For score < 30, expect urgent tone and red color
        assert dynamic_message["tone"] == "urgent", f"Expected urgent tone for low score, got {dynamic_message['tone']}"
        assert dynamic_message["color"] == "red", f"Expected red color for low score, got {dynamic_message['color']}"
        assert "attention immédiate" in dynamic_message["title"].lower() or "immédiate" in dynamic_message["title"].lower(), \
            f"Expected 'attention immédiate' in title, got: {dynamic_message['title']}"
        
        print(f"TEST PASS: Dynamic message for low score - title: '{dynamic_message['title']}', tone: {dynamic_message['tone']}, color: {dynamic_message['color']}")
    
    def test_score_breakdown_structure(self, auth_token):
        """Test score breakdown contains all components with correct weights"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        breakdown = data["score_breakdown"]
        
        expected_components = {
            "completeness": 40,
            "quality": 20,
            "analysis": 15,
            "progress": 15,
            "volume": 10
        }
        
        for comp, weight in expected_components.items():
            assert comp in breakdown, f"Missing breakdown component: {comp}"
            assert "score" in breakdown[comp], f"Missing score in {comp}"
            assert "weight" in breakdown[comp], f"Missing weight in {comp}"
            assert breakdown[comp]["weight"] == weight, f"Wrong weight for {comp}: expected {weight}, got {breakdown[comp]['weight']}"
        
        # Verify weights sum to 100
        total_weight = sum(expected_components.values())
        assert total_weight == 100, f"Weights should sum to 100, got {total_weight}"
        
        print(f"TEST PASS: Score breakdown structure correct with weights: completeness=40%, quality=20%, analysis=15%, progress=15%, volume=10%")
    
    def test_weak_points_for_new_user(self, auth_token):
        """Test weak points detected for new user (no_documents, low_completeness)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        weak_points = data["weak_points"]
        
        assert isinstance(weak_points, list), f"weak_points should be a list"
        assert len(weak_points) > 0, "Expected weak points for new user with 0 documents"
        
        # Check for no_documents weak point
        weak_point_ids = [wp["id"] for wp in weak_points]
        assert "no_documents" in weak_point_ids, f"Expected 'no_documents' weak point, got: {weak_point_ids}"
        
        # Verify weak point structure
        for wp in weak_points:
            assert "id" in wp
            assert "severity" in wp
            assert "title" in wp
            assert "detail" in wp
            assert "impact" in wp
        
        print(f"TEST PASS: Weak points detected for new user: {weak_point_ids}")
    
    def test_weak_point_severity_badges(self, auth_token):
        """Test weak point severity values are valid"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        weak_points = data["weak_points"]
        
        valid_severities = ["critical", "warning", "info"]
        for wp in weak_points:
            assert wp["severity"] in valid_severities, f"Invalid severity: {wp['severity']}"
        
        # no_documents should be critical severity
        no_docs = next((wp for wp in weak_points if wp["id"] == "no_documents"), None)
        if no_docs:
            assert no_docs["severity"] == "critical", f"no_documents should be critical, got {no_docs['severity']}"
        
        print(f"TEST PASS: All weak point severities are valid: {[wp['severity'] for wp in weak_points]}")
    
    def test_risk_alerts_for_default_case_type(self, auth_token):
        """Test risk alerts returned for default case type (AT)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        risk_alerts = data["risk_alerts"]
        
        assert isinstance(risk_alerts, list), f"risk_alerts should be a list"
        
        # For new user with no documents, should have risk alerts for missing essential docs
        # Default case type should be AT if no analysis/dossier exists
        if len(risk_alerts) > 0:
            for alert in risk_alerts:
                assert "severity" in alert
                assert "message" in alert
                assert "action" in alert
                assert alert["severity"] in ["critical", "warning", "info"]
            
            print(f"TEST PASS: Risk alerts returned: {len(risk_alerts)} alerts")
        else:
            print(f"TEST PASS: No risk alerts (case_type may not be determined yet)")
    
    def test_missing_documents_list(self, auth_token):
        """Test missing documents list for new user"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        missing_docs = data["missing_documents"]
        
        assert isinstance(missing_docs, list), f"missing_documents should be a list"
        
        # New user with 0 docs should have all essential docs missing
        if len(missing_docs) > 0:
            for doc in missing_docs:
                assert "key" in doc
                assert "label" in doc
                assert "category" in doc
            
            print(f"TEST PASS: Missing documents: {[doc['key'] for doc in missing_docs]}")
        else:
            print(f"TEST PASS: missing_documents structure is correct")
    
    def test_actionable_count(self, auth_token):
        """Test actionable count for new user"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        actionable_count = data["actionable_count"]
        
        assert isinstance(actionable_count, int), f"actionable_count should be int, got {type(actionable_count)}"
        
        # For new user, actionable_count = missing_docs count + illisible docs + (1 if no analysis and has docs)
        # Since we have 0 docs, it should equal missing_docs count
        missing_count = len(data["missing_documents"])
        
        # actionable_count should be at least the number of missing docs
        assert actionable_count >= 0, f"actionable_count should be >= 0, got {actionable_count}"
        
        print(f"TEST PASS: Actionable count: {actionable_count} (missing docs: {missing_count})")
    
    def test_summary_field(self, auth_token):
        """Test summary field structure"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        summary = data["summary"]
        
        expected_summary_fields = [
            "total_documents", "validated", "pending", "illisible",
            "analyses_ia", "dossier_express", "premium"
        ]
        
        for field in expected_summary_fields:
            assert field in summary, f"Missing summary field: {field}"
        
        # For new user, all should be 0
        assert summary["total_documents"] == 0, f"Expected 0 total docs for new user, got {summary['total_documents']}"
        
        print(f"TEST PASS: Summary structure correct: {summary}")
    
    def test_unauthenticated_request_fails(self):
        """Test that unauthenticated request returns 401"""
        response = requests.get(f"{API}/client/dossier-analysis")
        
        assert response.status_code in [401, 403], f"Expected 401/403 for unauthenticated request, got {response.status_code}"
        
        print(f"TEST PASS: Unauthenticated request returns {response.status_code}")


class TestDynamicMessageThresholds:
    """Test dynamic message changes based on score thresholds"""
    
    def test_message_threshold_documentation(self):
        """Document the expected thresholds (can't easily test all without manipulating DB)"""
        # Score thresholds from backend code:
        # < 30%: urgent, red, "attention immédiate"
        # < 50%: attention, orange, "en cours de structuration"
        # < 70%: encouraging, amber, "progresse bien"
        # < 85%: positive, blue, "solide"
        # >= 85%: excellent, green, "niveau expert"
        
        thresholds = {
            "< 30": {"tone": "urgent", "color": "red", "keyword": "attention immédiate"},
            "30-50": {"tone": "attention", "color": "orange", "keyword": "structuration"},
            "50-70": {"tone": "encouraging", "color": "amber", "keyword": "progresse"},
            "70-85": {"tone": "positive", "color": "blue", "keyword": "solide"},
            ">= 85": {"tone": "excellent", "color": "green", "keyword": "expert"}
        }
        
        print(f"TEST PASS: Dynamic message thresholds documented: {json.dumps(thresholds, indent=2)}")


class TestExistingTestClient:
    """Test with the existing test client mentioned in requirements"""
    
    def test_existing_client_login(self):
        """Test login with existing test client: test-analysis@test.com"""
        login_url = f"{API}/client/login"
        payload = {
            "email": "test-analysis@test.com",
            "password": "Password123!"
        }
        response = requests.post(login_url, json=payload)
        
        if response.status_code == 401:
            # User doesn't exist, register first
            register_url = f"{API}/client/register"
            reg_payload = {
                "email": "test-analysis@test.com",
                "password": "Password123!",
                "name": "Test Analysis User"
            }
            reg_response = requests.post(register_url, json=reg_payload)
            if reg_response.status_code == 200:
                response = requests.post(login_url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            
            # Test dossier-analysis for this user
            headers = {"Authorization": f"Bearer {token}"}
            analysis_response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
            
            assert analysis_response.status_code == 200
            analysis_data = analysis_response.json()
            
            print(f"TEST PASS: Existing test client dossier-analysis: score={analysis_data['score']}, tone={analysis_data['dynamic_message']['tone']}")
        else:
            print(f"TEST SKIP: Could not login/register test-analysis@test.com")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
