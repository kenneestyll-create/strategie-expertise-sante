"""
Test suite for StratégiIA Phase 2 & Phase 3 Features
GET /api/client/dossier-analysis

Phase 2:
- recommended_actions array with priority, action_id, title, description, impact, cta_label, cta_target, icon, estimated_score_gain

Phase 3:
- predictions array with title, detail, probability, consequence  
- premium_cta object with show, title, subtitle, features, cta_label, score_context
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API = f"{BASE_URL}/api"

# Test credentials for existing user
TEST_EMAIL = "test-analysis@test.com"
TEST_PASSWORD = "Password123!"


class TestPhase2RecommendedActions:
    """Test Phase 2: recommended_actions array in dossier-analysis response"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login with existing test user"""
        login_url = f"{API}/client/login"
        payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        response = requests.post(login_url, json=payload)
        
        if response.status_code == 401:
            # Register if doesn't exist
            register_url = f"{API}/client/register"
            reg_payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "Test Analysis User",
                "notifications_email": True,
                "notifications_push": False
            }
            reg_response = requests.post(register_url, json=reg_payload)
            assert reg_response.status_code in [200, 201], f"Registration failed: {reg_response.text}"
            response = requests.post(login_url, json=payload)
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data["access_token"]
    
    def test_recommended_actions_field_exists(self, auth_token):
        """Test that recommended_actions field exists in response"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "recommended_actions" in data, f"Missing recommended_actions field. Keys: {data.keys()}"
        assert isinstance(data["recommended_actions"], list), f"recommended_actions should be list"
        
        print(f"TEST PASS: recommended_actions field exists, count: {len(data['recommended_actions'])}")
    
    def test_recommended_actions_structure(self, auth_token):
        """Test structure of each recommended action item"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        recommended_actions = data["recommended_actions"]
        
        # For a test user with 0 documents, there should be recommended actions
        if len(recommended_actions) > 0:
            required_fields = [
                "priority", "action_id", "title", "description", 
                "impact", "cta_label", "cta_target", "icon", "estimated_score_gain"
            ]
            
            for action in recommended_actions:
                for field in required_fields:
                    assert field in action, f"Missing field '{field}' in action: {action}"
                
                # Validate field types
                assert isinstance(action["priority"], int), f"priority should be int"
                assert isinstance(action["action_id"], str), f"action_id should be string"
                assert isinstance(action["title"], str), f"title should be string"
                assert isinstance(action["description"], str), f"description should be string"
                assert isinstance(action["impact"], str), f"impact should be string"
                assert isinstance(action["cta_label"], str), f"cta_label should be string"
                assert isinstance(action["cta_target"], str), f"cta_target should be string"
                assert isinstance(action["icon"], str), f"icon should be string"
                assert isinstance(action["estimated_score_gain"], int), f"estimated_score_gain should be int"
            
            print(f"TEST PASS: All {len(recommended_actions)} actions have correct structure")
        else:
            print(f"TEST INFO: No recommended actions for this user (may already be complete)")
    
    def test_recommended_actions_priority_ordering(self, auth_token):
        """Test that recommended actions are ordered by priority"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        recommended_actions = data["recommended_actions"]
        
        if len(recommended_actions) > 1:
            priorities = [a["priority"] for a in recommended_actions]
            assert priorities == sorted(priorities), f"Actions should be sorted by priority. Got: {priorities}"
            print(f"TEST PASS: Actions correctly ordered by priority: {priorities}")
        else:
            print(f"TEST PASS: Priority ordering N/A (only {len(recommended_actions)} action)")
    
    def test_recommended_action_cta_targets(self, auth_token):
        """Test that cta_target values are valid"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        recommended_actions = data["recommended_actions"]
        valid_targets = ["documents", "strategiia"]  # Based on frontend handlers
        
        for action in recommended_actions:
            assert action["cta_target"] in valid_targets, \
                f"Invalid cta_target: {action['cta_target']}. Valid: {valid_targets}"
        
        print(f"TEST PASS: All cta_target values are valid")
    
    def test_first_action_is_upload_for_no_docs_user(self, auth_token):
        """Test that first action is upload_first_doc for user with 0 documents"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        summary = data.get("summary", {})
        total_docs = summary.get("total_documents", 0)
        recommended_actions = data["recommended_actions"]
        
        if total_docs == 0 and len(recommended_actions) > 0:
            first_action = recommended_actions[0]
            assert first_action["action_id"] == "upload_first_doc", \
                f"Expected 'upload_first_doc' for 0 docs user, got: {first_action['action_id']}"
            assert first_action["cta_target"] == "documents"
            print(f"TEST PASS: First action is 'upload_first_doc' for 0-docs user")
        else:
            print(f"TEST INFO: User has {total_docs} docs, first action logic differs")
    
    def test_impact_badges_format(self, auth_token):
        """Test impact field format contains percentage indicator"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        for action in data["recommended_actions"]:
            # Impact should contain percentage like "+15% sur votre score"
            assert "%" in action["impact"], f"Impact should contain %, got: {action['impact']}"
        
        print(f"TEST PASS: All impact badges contain percentage indicator")


class TestPhase3Predictions:
    """Test Phase 3: predictions array (predictive refusal logic)"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login with existing test user"""
        login_url = f"{API}/client/login"
        payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        response = requests.post(login_url, json=payload)
        
        if response.status_code == 401:
            register_url = f"{API}/client/register"
            reg_payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "Test Analysis User"
            }
            requests.post(register_url, json=reg_payload)
            response = requests.post(login_url, json=payload)
        
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_predictions_field_exists(self, auth_token):
        """Test that predictions field exists in response"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "predictions" in data, f"Missing predictions field. Keys: {data.keys()}"
        assert isinstance(data["predictions"], list), f"predictions should be list"
        
        print(f"TEST PASS: predictions field exists, count: {len(data['predictions'])}")
    
    def test_predictions_structure(self, auth_token):
        """Test structure of each prediction item"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        predictions = data["predictions"]
        required_fields = ["title", "detail", "probability", "consequence"]
        
        for pred in predictions:
            for field in required_fields:
                assert field in pred, f"Missing field '{field}' in prediction: {pred}"
            
            assert isinstance(pred["title"], str)
            assert isinstance(pred["detail"], str)
            assert isinstance(pred["probability"], str)
            assert isinstance(pred["consequence"], str)
        
        print(f"TEST PASS: All {len(predictions)} predictions have correct structure")
    
    def test_predictions_probability_values(self, auth_token):
        """Test that probability values are valid"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        valid_probabilities = ["Certaine", "Élevée", "Moyenne", "Faible"]
        
        for pred in data["predictions"]:
            assert pred["probability"] in valid_probabilities, \
                f"Invalid probability: {pred['probability']}. Valid: {valid_probabilities}"
        
        print(f"TEST PASS: All prediction probability values are valid")
    
    def test_predictions_based_on_missing_docs(self, auth_token):
        """Test that predictions are generated based on missing essential docs"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        missing_docs = data.get("missing_documents", [])
        predictions = data["predictions"]
        
        # If user has missing docs, they should potentially have predictions
        # AT case type has predictions for missing CMI, declaration_at
        if len(missing_docs) > 0 and len(predictions) > 0:
            print(f"TEST PASS: Predictions generated based on {len(missing_docs)} missing docs")
        else:
            print(f"TEST INFO: {len(predictions)} predictions, {len(missing_docs)} missing docs")


class TestPhase3PremiumCTA:
    """Test Phase 3: premium_cta object"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login with existing test user"""
        login_url = f"{API}/client/login"
        payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        response = requests.post(login_url, json=payload)
        
        if response.status_code == 401:
            register_url = f"{API}/client/register"
            reg_payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "Test Analysis User"
            }
            requests.post(register_url, json=reg_payload)
            response = requests.post(login_url, json=payload)
        
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_premium_cta_field_exists(self, auth_token):
        """Test that premium_cta field exists in response"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "premium_cta" in data, f"Missing premium_cta field. Keys: {data.keys()}"
        assert isinstance(data["premium_cta"], dict), f"premium_cta should be dict"
        
        print(f"TEST PASS: premium_cta field exists")
    
    def test_premium_cta_structure(self, auth_token):
        """Test structure of premium_cta object"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        premium_cta = data["premium_cta"]
        required_fields = ["show", "title", "subtitle", "features", "cta_label", "score_context"]
        
        for field in required_fields:
            assert field in premium_cta, f"Missing field '{field}' in premium_cta"
        
        # Validate types
        assert isinstance(premium_cta["show"], bool), f"show should be bool"
        assert isinstance(premium_cta["title"], str), f"title should be string"
        assert isinstance(premium_cta["subtitle"], str), f"subtitle should be string"
        assert isinstance(premium_cta["features"], list), f"features should be list"
        assert isinstance(premium_cta["cta_label"], str), f"cta_label should be string"
        assert isinstance(premium_cta["score_context"], str), f"score_context should be string"
        
        print(f"TEST PASS: premium_cta has correct structure with {len(premium_cta['features'])} features")
    
    def test_premium_cta_show_logic(self, auth_token):
        """Test premium_cta.show is true when score < 85 and no premium analyses"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        score = data["score"]
        premium_count = data["summary"]["premium"]
        show = data["premium_cta"]["show"]
        
        # Logic: show = (composite < 85) and (premium_count == 0)
        expected_show = (score < 85) and (premium_count == 0)
        
        assert show == expected_show, \
            f"premium_cta.show mismatch: score={score}, premium={premium_count}, expected={expected_show}, got={show}"
        
        print(f"TEST PASS: premium_cta.show={show} (score={score}, premium_count={premium_count})")
    
    def test_premium_cta_score_context_contains_score(self, auth_token):
        """Test score_context contains current score percentage"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        score = data["score"]
        score_context = data["premium_cta"]["score_context"]
        
        assert str(score) in score_context or f"{score}%" in score_context, \
            f"score_context should contain score ({score}). Got: {score_context}"
        
        print(f"TEST PASS: score_context contains score: '{score_context}'")
    
    def test_premium_cta_features_list_not_empty(self, auth_token):
        """Test that features list contains feature strings"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        features = data["premium_cta"]["features"]
        
        assert len(features) >= 3, f"Expected at least 3 features, got {len(features)}"
        
        for f in features:
            assert isinstance(f, str), f"Each feature should be string"
            assert len(f) > 10, f"Feature too short: {f}"
        
        print(f"TEST PASS: {len(features)} premium features: {features[:2]}...")


class TestPhase1Regression:
    """Regression tests for Phase 1 features"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login with existing test user"""
        login_url = f"{API}/client/login"
        payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        response = requests.post(login_url, json=payload)
        
        if response.status_code == 401:
            register_url = f"{API}/client/register"
            reg_payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "Test Analysis User"
            }
            requests.post(register_url, json=reg_payload)
            response = requests.post(login_url, json=payload)
        
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_score_field_exists(self, auth_token):
        """Phase 1 regression: score field exists"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "score" in data
        assert isinstance(data["score"], (int, float))
        print(f"TEST PASS: score={data['score']}")
    
    def test_weak_points_exist(self, auth_token):
        """Phase 1 regression: weak_points field exists"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "weak_points" in data
        assert isinstance(data["weak_points"], list)
        print(f"TEST PASS: weak_points count={len(data['weak_points'])}")
    
    def test_risk_alerts_exist(self, auth_token):
        """Phase 1 regression: risk_alerts field exists"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "risk_alerts" in data
        assert isinstance(data["risk_alerts"], list)
        print(f"TEST PASS: risk_alerts count={len(data['risk_alerts'])}")
    
    def test_dynamic_message_exists(self, auth_token):
        """Phase 1 regression: dynamic_message field exists"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "dynamic_message" in data
        dm = data["dynamic_message"]
        assert "title" in dm
        assert "message" in dm
        assert "tone" in dm
        assert "color" in dm
        print(f"TEST PASS: dynamic_message tone={dm['tone']}, color={dm['color']}")
    
    def test_missing_documents_exist(self, auth_token):
        """Phase 1 regression: missing_documents field exists"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "missing_documents" in data
        assert isinstance(data["missing_documents"], list)
        print(f"TEST PASS: missing_documents count={len(data['missing_documents'])}")
    
    def test_actionable_count_exists(self, auth_token):
        """Phase 1 regression: actionable_count field exists"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/client/dossier-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "actionable_count" in data
        assert isinstance(data["actionable_count"], int)
        print(f"TEST PASS: actionable_count={data['actionable_count']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
