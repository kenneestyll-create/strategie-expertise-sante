"""
Test suite for Weekly Report feature (Iteration 183)
Tests:
- GET /api/weekly-report/config — returns default config (enabled, day=monday, hour=8, email)
- PUT /api/weekly-report/config — updates config (toggle enabled, change day/hour/email)
- GET /api/weekly-report/preview — returns report data with all metrics for last 7 days
- POST /api/weekly-report/send — sends email and returns success (may fail with sandbox Resend)
- All weekly-report endpoints require authentication
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user."""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data, "No access_token in login response"
    return data["access_token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with auth token."""
    return {"Authorization": f"Bearer {auth_token}"}


class TestWeeklyReportAuth:
    """Test that all weekly-report endpoints require authentication."""

    def test_get_config_requires_auth(self):
        """GET /api/weekly-report/config should return 401/403 without auth."""
        response = requests.get(f"{BASE_URL}/api/weekly-report/config")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: GET /api/weekly-report/config requires authentication")

    def test_put_config_requires_auth(self):
        """PUT /api/weekly-report/config should return 401/403 without auth."""
        response = requests.put(f"{BASE_URL}/api/weekly-report/config", json={"enabled": True})
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: PUT /api/weekly-report/config requires authentication")

    def test_get_preview_requires_auth(self):
        """GET /api/weekly-report/preview should return 401/403 without auth."""
        response = requests.get(f"{BASE_URL}/api/weekly-report/preview")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: GET /api/weekly-report/preview requires authentication")

    def test_post_send_requires_auth(self):
        """POST /api/weekly-report/send should return 401/403 without auth."""
        response = requests.post(f"{BASE_URL}/api/weekly-report/send")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: POST /api/weekly-report/send requires authentication")


class TestWeeklyReportConfig:
    """Test GET and PUT /api/weekly-report/config endpoints."""

    def test_get_config_returns_default(self, auth_headers):
        """GET /api/weekly-report/config should return default config structure."""
        response = requests.get(f"{BASE_URL}/api/weekly-report/config", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify required fields exist
        assert "enabled" in data, "Missing 'enabled' field"
        assert "day" in data, "Missing 'day' field"
        assert "hour" in data, "Missing 'hour' field"
        assert "email" in data, "Missing 'email' field"
        
        # Verify types
        assert isinstance(data["enabled"], bool), "enabled should be boolean"
        assert isinstance(data["day"], str), "day should be string"
        assert isinstance(data["hour"], int), "hour should be integer"
        assert isinstance(data["email"], str), "email should be string"
        
        # Verify default values (if not modified)
        assert data["day"] in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], \
            f"Invalid day value: {data['day']}"
        assert 0 <= data["hour"] <= 23, f"Hour should be 0-23, got {data['hour']}"
        
        print(f"PASS: GET /api/weekly-report/config returns valid config: enabled={data['enabled']}, day={data['day']}, hour={data['hour']}")

    def test_put_config_toggle_enabled(self, auth_headers):
        """PUT /api/weekly-report/config should toggle enabled state."""
        # Get current config
        get_response = requests.get(f"{BASE_URL}/api/weekly-report/config", headers=auth_headers)
        current_enabled = get_response.json().get("enabled", True)
        
        # Toggle enabled
        new_enabled = not current_enabled
        put_response = requests.put(
            f"{BASE_URL}/api/weekly-report/config",
            headers=auth_headers,
            json={"enabled": new_enabled, "day": "monday", "hour": 8, "email": "test@example.com"}
        )
        assert put_response.status_code == 200, f"Expected 200, got {put_response.status_code}: {put_response.text}"
        
        put_data = put_response.json()
        assert put_data.get("success") == True, "Expected success: true"
        
        # Verify change persisted
        verify_response = requests.get(f"{BASE_URL}/api/weekly-report/config", headers=auth_headers)
        verify_data = verify_response.json()
        assert verify_data["enabled"] == new_enabled, f"Expected enabled={new_enabled}, got {verify_data['enabled']}"
        
        # Restore original state
        requests.put(
            f"{BASE_URL}/api/weekly-report/config",
            headers=auth_headers,
            json={"enabled": current_enabled, "day": "monday", "hour": 8, "email": "admin@accompagn-sante.fr"}
        )
        
        print(f"PASS: PUT /api/weekly-report/config toggles enabled from {current_enabled} to {new_enabled}")

    def test_put_config_change_day(self, auth_headers):
        """PUT /api/weekly-report/config should change day."""
        # Update to Wednesday
        put_response = requests.put(
            f"{BASE_URL}/api/weekly-report/config",
            headers=auth_headers,
            json={"enabled": True, "day": "wednesday", "hour": 10, "email": "admin@accompagn-sante.fr"}
        )
        assert put_response.status_code == 200, f"Expected 200, got {put_response.status_code}"
        
        # Verify change
        verify_response = requests.get(f"{BASE_URL}/api/weekly-report/config", headers=auth_headers)
        verify_data = verify_response.json()
        assert verify_data["day"] == "wednesday", f"Expected day=wednesday, got {verify_data['day']}"
        assert verify_data["hour"] == 10, f"Expected hour=10, got {verify_data['hour']}"
        
        # Restore default
        requests.put(
            f"{BASE_URL}/api/weekly-report/config",
            headers=auth_headers,
            json={"enabled": True, "day": "monday", "hour": 8, "email": "admin@accompagn-sante.fr"}
        )
        
        print("PASS: PUT /api/weekly-report/config changes day and hour")

    def test_put_config_change_email(self, auth_headers):
        """PUT /api/weekly-report/config should change email."""
        test_email = "test-weekly@example.com"
        
        put_response = requests.put(
            f"{BASE_URL}/api/weekly-report/config",
            headers=auth_headers,
            json={"enabled": True, "day": "monday", "hour": 8, "email": test_email}
        )
        assert put_response.status_code == 200, f"Expected 200, got {put_response.status_code}"
        
        # Verify change
        verify_response = requests.get(f"{BASE_URL}/api/weekly-report/config", headers=auth_headers)
        verify_data = verify_response.json()
        assert verify_data["email"] == test_email, f"Expected email={test_email}, got {verify_data['email']}"
        
        # Restore default
        requests.put(
            f"{BASE_URL}/api/weekly-report/config",
            headers=auth_headers,
            json={"enabled": True, "day": "monday", "hour": 8, "email": "admin@accompagn-sante.fr"}
        )
        
        print("PASS: PUT /api/weekly-report/config changes email")


class TestWeeklyReportPreview:
    """Test GET /api/weekly-report/preview endpoint."""

    def test_preview_returns_all_metrics(self, auth_headers):
        """GET /api/weekly-report/preview should return all report metrics."""
        response = requests.get(f"{BASE_URL}/api/weekly-report/preview", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify all required metrics are present
        required_fields = [
            "period",
            "contacts_7d",
            "analyses_7d",
            "dossiers_7d",
            "clients_7d",
            "bookings_7d",
            "revenue_7d",
            "chatbot_7d",
            "s3_total_size",
            "s3_total_files",
            "s3_exceeded_thresholds",
            "v2_status",
            "conversion_rate",
            "generated_at"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify types
        assert isinstance(data["period"], str), "period should be string"
        assert isinstance(data["contacts_7d"], int), "contacts_7d should be int"
        assert isinstance(data["analyses_7d"], int), "analyses_7d should be int"
        assert isinstance(data["dossiers_7d"], int), "dossiers_7d should be int"
        assert isinstance(data["clients_7d"], int), "clients_7d should be int"
        assert isinstance(data["bookings_7d"], int), "bookings_7d should be int"
        assert isinstance(data["revenue_7d"], (int, float)), "revenue_7d should be numeric"
        assert isinstance(data["chatbot_7d"], int), "chatbot_7d should be int"
        assert isinstance(data["s3_total_size"], int), "s3_total_size should be int"
        assert isinstance(data["s3_total_files"], int), "s3_total_files should be int"
        assert isinstance(data["s3_exceeded_thresholds"], list), "s3_exceeded_thresholds should be list"
        assert isinstance(data["v2_status"], str), "v2_status should be string"
        assert isinstance(data["conversion_rate"], (int, float)), "conversion_rate should be numeric"
        
        print(f"PASS: GET /api/weekly-report/preview returns all 14 metrics")
        print(f"  - period: {data['period']}")
        print(f"  - contacts_7d: {data['contacts_7d']}")
        print(f"  - analyses_7d: {data['analyses_7d']}")
        print(f"  - dossiers_7d: {data['dossiers_7d']}")
        print(f"  - clients_7d: {data['clients_7d']}")
        print(f"  - revenue_7d: {data['revenue_7d']}")
        print(f"  - s3_total_size: {data['s3_total_size']}")
        print(f"  - v2_status: {data['v2_status']}")


class TestWeeklyReportSend:
    """Test POST /api/weekly-report/send endpoint."""

    def test_send_returns_response(self, auth_headers):
        """POST /api/weekly-report/send should return success or error (sandbox may fail)."""
        response = requests.post(f"{BASE_URL}/api/weekly-report/send", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Should have success field
        assert "success" in data, "Missing 'success' field in response"
        
        if data["success"]:
            # If success, should have sent_to
            assert "sent_to" in data, "Missing 'sent_to' field when success=true"
            print(f"PASS: POST /api/weekly-report/send succeeded, sent to: {data['sent_to']}")
        else:
            # If failed, should have error
            assert "error" in data, "Missing 'error' field when success=false"
            print(f"PASS: POST /api/weekly-report/send returned error (expected in sandbox): {data['error']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
