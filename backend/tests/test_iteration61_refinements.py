"""
Iteration 61: Testing the 3 refinements for StratégiIA dossier analysis:
1. Key metrics (Complétude, Qualité, Cohérence) always visible in score card
2. Score change feedback toast showing '+X%' after actions
3. Priority badges (haute=red, moyenne=amber, faible=green) on recommended actions, max 3
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test-analysis@test.com"
TEST_PASSWORD = "Password123!"


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for test user"""
    response = requests.post(
        f"{BASE_URL}/api/client/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code != 200:
        pytest.skip(f"Login failed: {response.status_code}")
    return response.json().get("access_token")


class TestRefinement1KeyMetrics:
    """Test 1: key_metrics field with completeness, quality, coherence as integers"""

    def test_key_metrics_field_exists(self, auth_token):
        """key_metrics should be present in response"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "key_metrics" in data, "key_metrics field missing from response"
        print(f"✓ key_metrics field exists: {data['key_metrics']}")

    def test_key_metrics_has_completeness(self, auth_token):
        """key_metrics should have completeness as integer"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        key_metrics = data.get("key_metrics", {})
        assert "completeness" in key_metrics, "completeness missing from key_metrics"
        assert isinstance(key_metrics["completeness"], int), "completeness should be integer"
        print(f"✓ completeness: {key_metrics['completeness']}")

    def test_key_metrics_has_quality(self, auth_token):
        """key_metrics should have quality as integer"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        key_metrics = data.get("key_metrics", {})
        assert "quality" in key_metrics, "quality missing from key_metrics"
        assert isinstance(key_metrics["quality"], int), "quality should be integer"
        print(f"✓ quality: {key_metrics['quality']}")

    def test_key_metrics_has_coherence(self, auth_token):
        """key_metrics should have coherence as integer"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        key_metrics = data.get("key_metrics", {})
        assert "coherence" in key_metrics, "coherence missing from key_metrics"
        assert isinstance(key_metrics["coherence"], int), "coherence should be integer"
        print(f"✓ coherence: {key_metrics['coherence']}")

    def test_score_breakdown_includes_coherence(self, auth_token):
        """score_breakdown should include coherence entry"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        score_breakdown = data.get("score_breakdown", {})
        assert "coherence" in score_breakdown, "coherence missing from score_breakdown"
        coherence = score_breakdown["coherence"]
        assert "score" in coherence, "coherence.score missing"
        assert "label" in coherence, "coherence.label missing"
        print(f"✓ coherence in score_breakdown: {coherence}")


class TestRefinement3PriorityBadgesMax3:
    """Test 3: recommended_actions with priority_level badges, limited to max 3"""

    def test_recommended_actions_max_3(self, auth_token):
        """recommended_actions should have max 3 items"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        actions = data.get("recommended_actions", [])
        assert len(actions) <= 3, f"Expected max 3 actions, got {len(actions)}"
        print(f"✓ recommended_actions count: {len(actions)} (max 3)")

    def test_each_action_has_priority_level(self, auth_token):
        """Each recommended_action should have priority_level field"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        actions = data.get("recommended_actions", [])
        
        for i, action in enumerate(actions):
            assert "priority_level" in action, f"Action {i} missing priority_level"
            print(f"  Action {i}: {action.get('action_id')} - priority_level: {action['priority_level']}")
        print(f"✓ All {len(actions)} actions have priority_level")

    def test_priority_level_valid_values(self, auth_token):
        """priority_level should be one of: haute, moyenne, faible"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        actions = data.get("recommended_actions", [])
        
        valid_levels = {"haute", "moyenne", "faible"}
        for action in actions:
            level = action.get("priority_level")
            assert level in valid_levels, f"Invalid priority_level: {level}"
        print(f"✓ All priority_levels are valid (haute/moyenne/faible)")

    def test_actions_priority_ordering(self, auth_token):
        """Actions should be ordered by priority (haute first)"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        actions = data.get("recommended_actions", [])
        
        # Check that first action has highest priority
        if len(actions) >= 1:
            first_level = actions[0].get("priority_level")
            # For test user with no docs, first should be haute (upload_first_doc)
            print(f"  First action priority: {first_level}")
            # Just verify ordering makes sense - haute should come before faible
            priority_order = {"haute": 1, "moyenne": 2, "faible": 3}
            priorities = [priority_order.get(a.get("priority_level"), 99) for a in actions]
            # At least verify first action is not lower priority than last
            if len(priorities) >= 2:
                assert priorities[0] <= priorities[-1], "Actions not in priority order"
        print(f"✓ Actions appear to be priority ordered")


class TestRegressionPhase1Phase2Phase3:
    """Regression tests for existing Phase 1-3 features"""

    def test_score_field_exists(self, auth_token):
        """score field should exist"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert "score" in data
        assert isinstance(data["score"], int)
        print(f"✓ score: {data['score']}")

    def test_weak_points_exist(self, auth_token):
        """weak_points should exist"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert "weak_points" in data
        print(f"✓ weak_points count: {len(data['weak_points'])}")

    def test_risk_alerts_exist(self, auth_token):
        """risk_alerts should exist"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert "risk_alerts" in data
        print(f"✓ risk_alerts count: {len(data['risk_alerts'])}")

    def test_predictions_exist(self, auth_token):
        """predictions (Phase 3) should exist"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert "predictions" in data
        print(f"✓ predictions count: {len(data['predictions'])}")

    def test_premium_cta_exists(self, auth_token):
        """premium_cta (Phase 3) should exist"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert "premium_cta" in data
        assert "show" in data["premium_cta"]
        print(f"✓ premium_cta.show: {data['premium_cta']['show']}")

    def test_dynamic_message_exists(self, auth_token):
        """dynamic_message should exist"""
        response = requests.get(
            f"{BASE_URL}/api/client/dossier-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert "dynamic_message" in data
        dm = data["dynamic_message"]
        assert "title" in dm
        assert "message" in dm
        assert "tone" in dm
        print(f"✓ dynamic_message tone: {dm['tone']}")
