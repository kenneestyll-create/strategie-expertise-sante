"""
Test suite for S3 Storage Alerts feature (Iteration 182)
Tests the new storage alerts system with configurable thresholds (500 Mo, 1 Go, 5 Go)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD


@pytest.fixture(scope="module")
def auth_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestStorageAlertsConfig:
    """Tests for GET/PUT /api/documents/storage-alerts/config"""

    def test_get_config_requires_auth(self):
        """GET /api/documents/storage-alerts/config requires authentication"""
        response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/config")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: GET /api/documents/storage-alerts/config requires auth")

    def test_get_config_returns_default_structure(self, auth_headers):
        """GET /api/documents/storage-alerts/config returns default config with enabled, thresholds, notify_email"""
        response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/config", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify structure
        assert "enabled" in data, "Missing 'enabled' field"
        assert "thresholds" in data, "Missing 'thresholds' field"
        assert "notify_email" in data, "Missing 'notify_email' field"
        
        # Verify thresholds structure
        thresholds = data["thresholds"]
        assert isinstance(thresholds, list), "thresholds should be a list"
        assert len(thresholds) == 3, f"Expected 3 thresholds, got {len(thresholds)}"
        
        # Verify each threshold has required fields
        for t in thresholds:
            assert "label" in t, "Threshold missing 'label'"
            assert "bytes" in t, "Threshold missing 'bytes'"
            assert "active" in t, "Threshold missing 'active'"
        
        # Verify default threshold labels (500 Mo, 1 Go, 5 Go)
        labels = [t["label"] for t in thresholds]
        assert "500 Mo" in labels, "Missing '500 Mo' threshold"
        assert "1 Go" in labels, "Missing '1 Go' threshold"
        assert "5 Go" in labels, "Missing '5 Go' threshold"
        
        print(f"PASS: GET config returns correct structure: enabled={data['enabled']}, thresholds={len(thresholds)}, notify_email={data['notify_email']}")

    def test_put_config_requires_auth(self):
        """PUT /api/documents/storage-alerts/config requires authentication"""
        response = requests.put(f"{BASE_URL}/api/documents/storage-alerts/config", json={"enabled": False})
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: PUT /api/documents/storage-alerts/config requires auth")

    def test_put_config_toggle_enabled(self, auth_headers):
        """PUT /api/documents/storage-alerts/config can toggle enabled state"""
        # Get current config
        get_response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/config", headers=auth_headers)
        original_config = get_response.json()
        original_enabled = original_config.get("enabled", True)
        
        # Toggle enabled
        new_enabled = not original_enabled
        update_response = requests.put(
            f"{BASE_URL}/api/documents/storage-alerts/config",
            headers=auth_headers,
            json={
                "enabled": new_enabled,
                "thresholds": original_config.get("thresholds", []),
                "notify_email": original_config.get("notify_email", True)
            }
        )
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}: {update_response.text}"
        
        # Verify update
        verify_response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/config", headers=auth_headers)
        updated_config = verify_response.json()
        assert updated_config["enabled"] == new_enabled, f"Expected enabled={new_enabled}, got {updated_config['enabled']}"
        
        # Restore original state
        requests.put(
            f"{BASE_URL}/api/documents/storage-alerts/config",
            headers=auth_headers,
            json=original_config
        )
        
        print(f"PASS: PUT config toggle enabled: {original_enabled} -> {new_enabled} -> {original_enabled}")

    def test_put_config_toggle_threshold(self, auth_headers):
        """PUT /api/documents/storage-alerts/config can toggle individual threshold active state"""
        # Get current config
        get_response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/config", headers=auth_headers)
        original_config = get_response.json()
        original_thresholds = original_config.get("thresholds", [])
        
        if len(original_thresholds) == 0:
            pytest.skip("No thresholds to toggle")
        
        # Toggle first threshold
        new_thresholds = [dict(t) for t in original_thresholds]
        original_active = new_thresholds[0].get("active", True)
        new_thresholds[0]["active"] = not original_active
        
        update_response = requests.put(
            f"{BASE_URL}/api/documents/storage-alerts/config",
            headers=auth_headers,
            json={
                "enabled": original_config.get("enabled", True),
                "thresholds": new_thresholds,
                "notify_email": original_config.get("notify_email", True)
            }
        )
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}"
        
        # Verify update
        verify_response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/config", headers=auth_headers)
        updated_config = verify_response.json()
        assert updated_config["thresholds"][0]["active"] == (not original_active), "Threshold active state not updated"
        
        # Restore original state
        requests.put(
            f"{BASE_URL}/api/documents/storage-alerts/config",
            headers=auth_headers,
            json=original_config
        )
        
        print(f"PASS: PUT config toggle threshold[0] active: {original_active} -> {not original_active} -> {original_active}")


class TestStorageAlertsCheck:
    """Tests for GET /api/documents/storage-alerts/check"""

    def test_check_requires_auth(self):
        """GET /api/documents/storage-alerts/check requires authentication"""
        response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/check")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: GET /api/documents/storage-alerts/check requires auth")

    def test_check_returns_alerts_structure(self, auth_headers):
        """GET /api/documents/storage-alerts/check returns alerts array with status, current_size, total_files"""
        response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/check", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify structure
        assert "alerts" in data, "Missing 'alerts' field"
        assert "current_size" in data, "Missing 'current_size' field"
        assert "total_files" in data, "Missing 'total_files' field"
        assert "enabled" in data, "Missing 'enabled' field"
        
        # Verify alerts is a list
        alerts = data["alerts"]
        assert isinstance(alerts, list), "alerts should be a list"
        
        # Verify current_size is a number
        assert isinstance(data["current_size"], (int, float)), "current_size should be a number"
        
        print(f"PASS: GET check returns correct structure: alerts={len(alerts)}, current_size={data['current_size']}, total_files={data['total_files']}, enabled={data['enabled']}")

    def test_check_alert_structure(self, auth_headers):
        """Each alert in the response has label, threshold_bytes, current_pct, status"""
        response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/check", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        alerts = data.get("alerts", [])
        
        if len(alerts) == 0:
            # If no alerts, check if alerts are disabled
            if not data.get("enabled", True):
                print("PASS: No alerts returned because alerts are disabled")
                return
            pytest.skip("No alerts returned to verify structure")
        
        for i, alert in enumerate(alerts):
            assert "label" in alert, f"Alert {i} missing 'label'"
            assert "threshold_bytes" in alert, f"Alert {i} missing 'threshold_bytes'"
            assert "current_pct" in alert, f"Alert {i} missing 'current_pct'"
            assert "status" in alert, f"Alert {i} missing 'status'"
            
            # Verify status is one of expected values
            assert alert["status"] in ["ok", "warning", "exceeded"], f"Alert {i} has invalid status: {alert['status']}"
            
            # Verify current_pct is a number
            assert isinstance(alert["current_pct"], (int, float)), f"Alert {i} current_pct should be a number"
        
        print(f"PASS: All {len(alerts)} alerts have correct structure with valid status values")

    def test_check_status_values(self, auth_headers):
        """Verify status values are correct based on current storage (should be 'ok' for ~45 Ko)"""
        response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/check", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        current_size = data.get("current_size", 0)
        alerts = data.get("alerts", [])
        
        # Current storage is ~45 Ko which is well below all thresholds
        # All statuses should be 'ok'
        for alert in alerts:
            # With ~45 Ko storage, all thresholds (500 Mo, 1 Go, 5 Go) should show 'ok'
            # and percentage should be very low (close to 0%)
            if current_size < 500 * 1024 * 1024:  # Less than 500 Mo
                assert alert["status"] == "ok", f"Expected 'ok' status for {alert['label']} with {current_size} bytes, got {alert['status']}"
                assert alert["current_pct"] < 1, f"Expected <1% for {alert['label']}, got {alert['current_pct']}%"
        
        print(f"PASS: All alerts show 'ok' status with current_size={current_size} bytes ({current_size/1024:.1f} Ko)")

    def test_check_when_disabled(self, auth_headers):
        """When alerts are disabled, check returns empty alerts array"""
        # Get current config
        config_response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/config", headers=auth_headers)
        original_config = config_response.json()
        
        # Disable alerts
        requests.put(
            f"{BASE_URL}/api/documents/storage-alerts/config",
            headers=auth_headers,
            json={**original_config, "enabled": False}
        )
        
        # Check alerts
        check_response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/check", headers=auth_headers)
        assert check_response.status_code == 200
        
        data = check_response.json()
        assert data["enabled"] == False, "Expected enabled=False"
        assert data["alerts"] == [], f"Expected empty alerts array when disabled, got {data['alerts']}"
        
        # Restore original config
        requests.put(
            f"{BASE_URL}/api/documents/storage-alerts/config",
            headers=auth_headers,
            json=original_config
        )
        
        print("PASS: When disabled, check returns empty alerts array and enabled=False")


class TestStorageAlertsIntegration:
    """Integration tests for storage alerts feature"""

    def test_toggle_threshold_affects_check(self, auth_headers):
        """Toggling a threshold inactive removes it from check results"""
        # Get current config
        config_response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/config", headers=auth_headers)
        original_config = config_response.json()
        
        # Ensure alerts are enabled
        if not original_config.get("enabled", True):
            requests.put(
                f"{BASE_URL}/api/documents/storage-alerts/config",
                headers=auth_headers,
                json={**original_config, "enabled": True}
            )
        
        # Get initial check
        check_response = requests.get(f"{BASE_URL}/api/documents/storage-alerts/check", headers=auth_headers)
        initial_alerts = check_response.json().get("alerts", [])
        initial_count = len(initial_alerts)
        
        if initial_count == 0:
            pytest.skip("No alerts to test with")
        
        # Disable first threshold
        new_thresholds = [dict(t) for t in original_config.get("thresholds", [])]
        if len(new_thresholds) > 0:
            new_thresholds[0]["active"] = False
        
        requests.put(
            f"{BASE_URL}/api/documents/storage-alerts/config",
            headers=auth_headers,
            json={**original_config, "thresholds": new_thresholds}
        )
        
        # Check again
        check_response2 = requests.get(f"{BASE_URL}/api/documents/storage-alerts/check", headers=auth_headers)
        new_alerts = check_response2.json().get("alerts", [])
        
        # Should have one less alert
        assert len(new_alerts) == initial_count - 1, f"Expected {initial_count - 1} alerts after disabling one, got {len(new_alerts)}"
        
        # Restore original config
        requests.put(
            f"{BASE_URL}/api/documents/storage-alerts/config",
            headers=auth_headers,
            json=original_config
        )
        
        print(f"PASS: Disabling threshold reduces alert count from {initial_count} to {initial_count - 1}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
