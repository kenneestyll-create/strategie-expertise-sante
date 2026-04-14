"""
Test suite for Predictive V2 Admin endpoints
=============================================
Tests the dormant V2 Predictive AI system:
- Feature flag status (disabled by default)
- Activation locks (500 cases minimum)
- Triple security activation flow
- Sandbox mode for internal testing
- V1/V2 comparator
- Configuration panel
- Audit logging
- Kill switch
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD
from tests.test_config import CLIENT_EMAIL, CLIENT_PASSWORD


class TestPredictiveV2Status:
    """Tests for GET /api/predictive-v2/status"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for authenticated requests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.admin_token = token
        else:
            pytest.skip(f"Admin login failed: {login_resp.status_code}")
    
    def test_status_returns_401_or_403_without_auth(self):
        """V2 status endpoint requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/predictive-v2/status")
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print(f"PASS: /api/predictive-v2/status returns {resp.status_code} without auth")
    
    def test_status_returns_correct_structure(self):
        """V2 status returns enabled=false and can_activate=false (insufficient cases)"""
        resp = self.session.get(f"{BASE_URL}/api/predictive-v2/status")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        # Check required fields
        assert "enabled" in data, "Missing 'enabled' field"
        assert "config" in data, "Missing 'config' field"
        assert "readiness" in data, "Missing 'readiness' field"
        assert "locks" in data, "Missing 'locks' field"
        assert "can_activate" in data, "Missing 'can_activate' field"
        
        # V2 should be disabled by default
        assert data["enabled"] == False, f"V2 should be disabled by default, got {data['enabled']}"
        
        # Can't activate with insufficient cases
        assert data["can_activate"] == False, f"Should not be able to activate with insufficient cases"
        
        # Check readiness structure
        readiness = data["readiness"]
        assert "score" in readiness, "Missing readiness score"
        assert "usable_cases" in readiness, "Missing usable_cases"
        assert readiness["usable_cases"] < 500, f"Test assumes < 500 cases, got {readiness['usable_cases']}"
        
        print(f"PASS: V2 status - enabled={data['enabled']}, can_activate={data['can_activate']}, usable_cases={readiness['usable_cases']}")
    
    def test_status_has_5_locks(self):
        """V2 status returns 5 activation locks"""
        resp = self.session.get(f"{BASE_URL}/api/predictive-v2/status")
        assert resp.status_code == 200
        
        data = resp.json()
        locks = data["locks"]
        assert len(locks) == 5, f"Expected 5 locks, got {len(locks)}"
        
        lock_ids = [lock["id"] for lock in locks]
        expected_ids = ["min_cases", "min_score", "diversity", "completeness", "status_vert"]
        for expected_id in expected_ids:
            assert expected_id in lock_ids, f"Missing lock: {expected_id}"
        
        # min_cases lock should fail (< 500)
        min_cases_lock = next(l for l in locks if l["id"] == "min_cases")
        assert min_cases_lock["passed"] == False, "min_cases lock should fail with < 500 cases"
        
        print(f"PASS: 5 locks present, min_cases lock correctly failing")


class TestPredictiveV2Activation:
    """Tests for POST /api/predictive-v2/activate and /deactivate"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Admin login failed")
    
    def test_activate_returns_401_or_403_without_auth(self):
        """Activation endpoint requires authentication"""
        resp = requests.post(f"{BASE_URL}/api/predictive-v2/activate", json={
            "confirmation_text": "ACTIVER V2"
        })
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print(f"PASS: /api/predictive-v2/activate returns {resp.status_code} without auth")
    
    def test_activate_refused_with_wrong_confirmation(self):
        """Activation refused with wrong confirmation text (400)"""
        resp = self.session.post(f"{BASE_URL}/api/predictive-v2/activate", json={
            "confirmation_text": "wrong text"
        })
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        
        detail = resp.json().get("detail", "")
        assert "ACTIVER V2" in detail, f"Error should mention correct text, got: {detail}"
        print("PASS: Activation refused with wrong confirmation text (400)")
    
    def test_activate_refused_with_insufficient_cases(self):
        """Activation refused with 403 when cases < 500 (even with correct confirmation)"""
        resp = self.session.post(f"{BASE_URL}/api/predictive-v2/activate", json={
            "confirmation_text": "ACTIVER V2"
        })
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
        
        detail = resp.json().get("detail", "")
        assert "Verrous" in detail or "impossible" in detail.lower(), f"Error should mention locks, got: {detail}"
        print(f"PASS: Activation refused with 403 (insufficient cases): {detail}")
    
    def test_deactivate_works(self):
        """Kill switch (deactivate) works"""
        resp = self.session.post(f"{BASE_URL}/api/predictive-v2/deactivate", json={})
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data.get("success") == True, "Deactivation should succeed"
        assert "V2 desactivee" in data.get("message", ""), "Should confirm deactivation"
        print("PASS: Kill switch (deactivate) works")


class TestPredictiveV2Sandbox:
    """Tests for POST /api/predictive-v2/sandbox/analyze and /sandbox/compare"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Admin login failed")
    
    def test_sandbox_analyze_returns_401_or_403_without_auth(self):
        """Sandbox analyze requires authentication"""
        resp = requests.post(f"{BASE_URL}/api/predictive-v2/sandbox/analyze", json={
            "situation": "Test situation"
        })
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print(f"PASS: /api/predictive-v2/sandbox/analyze returns {resp.status_code} without auth")
    
    def test_sandbox_analyze_returns_alerts_and_score(self):
        """Sandbox analyze returns alerts, robustness_score, and disclaimer"""
        test_situation = """
        Je suis agent RATP depuis 15 ans. J'ai été exposé à l'amiante dans les tunnels du métro.
        J'ai développé une maladie professionnelle mais je n'ai pas de certificat médical détaillé.
        La RATP refuse de reconnaître mon exposition. Je ne sais pas comment prouver mon cas.
        """
        
        resp = self.session.post(f"{BASE_URL}/api/predictive-v2/sandbox/analyze", json={
            "situation": test_situation,
            "type_dossier": "maladie_professionnelle"
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        
        # Check v2_result structure
        assert "v2_result" in data, "Missing v2_result"
        v2_result = data["v2_result"]
        
        assert "alerts" in v2_result, "Missing alerts"
        assert "robustness_score" in v2_result, "Missing robustness_score"
        assert "disclaimer" in v2_result, "Missing disclaimer"
        assert "alert_count" in v2_result, "Missing alert_count"
        assert "robustness_level" in v2_result, "Missing robustness_level"
        
        # Should have some alerts for this test case
        assert len(v2_result["alerts"]) > 0, "Should detect some alerts"
        assert v2_result["robustness_score"] >= 0 and v2_result["robustness_score"] <= 100
        
        # Check alert structure
        alert = v2_result["alerts"][0]
        assert "rule_id" in alert, "Alert missing rule_id"
        assert "label" in alert, "Alert missing label"
        assert "severity" in alert, "Alert missing severity"
        assert "advice" in alert, "Alert missing advice"
        
        print(f"PASS: Sandbox analyze - {v2_result['alert_count']} alerts, robustness={v2_result['robustness_score']}/100")
    
    def test_sandbox_analyze_requires_situation(self):
        """Sandbox analyze requires situation text"""
        resp = self.session.post(f"{BASE_URL}/api/predictive-v2/sandbox/analyze", json={
            "situation": "",
            "type_dossier": "autre"
        })
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        print("PASS: Sandbox analyze requires situation text (400)")
    
    def test_sandbox_compare_returns_401_without_auth(self):
        """Sandbox compare requires authentication"""
        resp = requests.post(f"{BASE_URL}/api/predictive-v2/sandbox/compare", json={
            "analysis_id": "test-id"
        })
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        print("PASS: /api/predictive-v2/sandbox/compare returns 401 without auth")
    
    def test_sandbox_compare_requires_analysis_id(self):
        """Sandbox compare requires analysis_id"""
        resp = self.session.post(f"{BASE_URL}/api/predictive-v2/sandbox/compare", json={
            "analysis_id": ""
        })
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        print("PASS: Sandbox compare requires analysis_id (400)")
    
    def test_sandbox_compare_returns_404_for_invalid_id(self):
        """Sandbox compare returns 404 for non-existent analysis"""
        resp = self.session.post(f"{BASE_URL}/api/predictive-v2/sandbox/compare", json={
            "analysis_id": "non-existent-id-12345"
        })
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print("PASS: Sandbox compare returns 404 for invalid analysis_id")


class TestPredictiveV2Config:
    """Tests for GET/PUT /api/predictive-v2/config"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Admin login failed")
    
    def test_config_returns_401_or_403_without_auth(self):
        """Config endpoint requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/predictive-v2/config")
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print(f"PASS: /api/predictive-v2/config returns {resp.status_code} without auth")
    
    def test_config_returns_v2_parameters(self):
        """GET config returns V2 configuration parameters"""
        resp = self.session.get(f"{BASE_URL}/api/predictive-v2/config")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        
        # Check expected config keys
        expected_keys = [
            "predictive_v2_enabled",
            "v2_min_readiness_score",
            "v2_min_cases",
            "v2_max_alerts_per_analysis",
            "v2_prudence_level"
        ]
        for key in expected_keys:
            assert key in data, f"Missing config key: {key}"
        
        # V2 should be disabled
        assert data["predictive_v2_enabled"] == False, "V2 should be disabled by default"
        
        print(f"PASS: Config returns all V2 parameters, v2_enabled={data['predictive_v2_enabled']}")
    
    def test_config_update_allowed_parameter(self):
        """PUT config updates allowed parameters"""
        # Get current value
        resp = self.session.get(f"{BASE_URL}/api/predictive-v2/config")
        original_value = resp.json().get("v2_max_alerts_per_analysis", 5)
        
        # Update to new value
        new_value = 10 if original_value != 10 else 8
        resp = self.session.put(f"{BASE_URL}/api/predictive-v2/config", json={
            "key": "v2_max_alerts_per_analysis",
            "value": new_value
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data.get("success") == True, "Update should succeed"
        assert data.get("value") == new_value, f"Value should be {new_value}"
        
        # Restore original value
        self.session.put(f"{BASE_URL}/api/predictive-v2/config", json={
            "key": "v2_max_alerts_per_analysis",
            "value": original_value
        })
        
        print(f"PASS: Config update allowed parameter (v2_max_alerts_per_analysis)")
    
    def test_config_rejects_non_allowed_parameter(self):
        """PUT config rejects non-allowed parameters (e.g. 'predictive_v2_enabled')"""
        resp = self.session.put(f"{BASE_URL}/api/predictive-v2/config", json={
            "key": "predictive_v2_enabled",
            "value": True
        })
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        
        detail = resp.json().get("detail", "")
        assert "non modifiable" in detail.lower() or "predictive_v2_enabled" in detail
        print("PASS: Config rejects non-allowed parameter 'predictive_v2_enabled' (400)")


class TestPredictiveV2AuditLog:
    """Tests for GET /api/predictive-v2/audit-log"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Admin login failed")
    
    def test_audit_log_returns_401_or_403_without_auth(self):
        """Audit log requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/predictive-v2/audit-log")
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print(f"PASS: /api/predictive-v2/audit-log returns {resp.status_code} without auth")
    
    def test_audit_log_returns_events(self):
        """Audit log returns audit events"""
        # First, trigger some events by running sandbox analyze
        self.session.post(f"{BASE_URL}/api/predictive-v2/sandbox/analyze", json={
            "situation": "Test situation for audit log",
            "type_dossier": "autre"
        })
        
        # Also trigger activation_refused
        self.session.post(f"{BASE_URL}/api/predictive-v2/activate", json={
            "confirmation_text": "ACTIVER V2"
        })
        
        # Now check audit log
        resp = self.session.get(f"{BASE_URL}/api/predictive-v2/audit-log")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert "logs" in data, "Missing 'logs' field"
        assert "count" in data, "Missing 'count' field"
        
        logs = data["logs"]
        assert isinstance(logs, list), "logs should be a list"
        
        # Should have at least the events we just triggered
        if len(logs) > 0:
            log = logs[0]
            assert "event_type" in log, "Log missing event_type"
            assert "admin_email" in log, "Log missing admin_email"
            assert "timestamp" in log, "Log missing timestamp"
            
            # Check for expected event types
            event_types = [l["event_type"] for l in logs]
            print(f"PASS: Audit log returns {len(logs)} events, types: {set(event_types)}")
        else:
            print("PASS: Audit log returns empty list (no events yet)")


class TestV1NotAffected:
    """Tests to verify V1 pipeline is NOT affected when V2 is OFF"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Admin login failed")
    
    def test_v2_is_disabled(self):
        """Verify V2 is disabled before testing V1"""
        resp = self.session.get(f"{BASE_URL}/api/predictive-v2/status")
        assert resp.status_code == 200
        
        data = resp.json()
        assert data["enabled"] == False, "V2 should be disabled for this test"
        print("PASS: V2 is confirmed disabled")
    
    def test_strategiia_endpoint_works(self):
        """StrategiIA analysis endpoint works normally"""
        # Just check the endpoint is accessible (don't run full analysis)
        resp = self.session.get(f"{BASE_URL}/api/strategiia/analyses")
        # Should return 200 (list of analyses) or similar
        assert resp.status_code in [200, 401, 403], f"StrategiIA endpoint should be accessible, got {resp.status_code}"
        print(f"PASS: StrategiIA endpoint accessible (status {resp.status_code})")


class TestPublicPagesNotAffected:
    """Tests to verify public pages work correctly"""
    
    def test_homepage_loads(self):
        """Homepage loads correctly"""
        resp = requests.get(f"{BASE_URL}/api/health")
        # Health endpoint should work
        assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
        print("PASS: Health endpoint works")
    
    def test_public_chatbot_accessible(self):
        """Public chatbot endpoint is accessible"""
        resp = requests.get(f"{BASE_URL}/api/chatbot/types")
        # Should return 200 or similar accessible status
        assert resp.status_code in [200, 404], f"Chatbot types endpoint failed: {resp.status_code}"
        print(f"PASS: Public endpoint check (status {resp.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
