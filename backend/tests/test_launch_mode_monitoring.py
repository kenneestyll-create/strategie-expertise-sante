"""
Test suite for Commercial Launch Preparation features:
- Launch Mode Control (ouvert/controle/indisponible)
- Admin Monitoring Dashboard with Live KPIs
- Client Dossier Tracker (suivi endpoint)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD

# Test dossier with incident status
TEST_INCIDENT_DOSSIER_ID = "9514180a-aef7-4f68-89b6-ae25278447ea"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        # API returns access_token, not token
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Admin authentication failed: {response.status_code} - {response.text}")


@pytest.fixture
def admin_headers(admin_token):
    """Headers with admin auth token"""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


class TestLaunchModePublic:
    """Tests for public launch mode endpoint"""

    def test_get_launch_mode_public_returns_200(self):
        """GET /api/launch-mode returns current mode (public endpoint)"""
        response = requests.get(f"{BASE_URL}/api/launch-mode")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "mode" in data, "Response should contain 'mode' field"
        assert "message" in data, "Response should contain 'message' field"
        assert data["mode"] in ["ouvert", "controle", "indisponible"], f"Invalid mode: {data['mode']}"
        print(f"✓ Public launch mode: {data['mode']}")

    def test_get_launch_mode_no_auth_required(self):
        """Public endpoint should not require authentication"""
        response = requests.get(f"{BASE_URL}/api/launch-mode")
        assert response.status_code == 200, "Public endpoint should not require auth"


class TestLaunchModeAdmin:
    """Tests for admin launch mode endpoints"""

    def test_admin_get_launch_mode_returns_metadata(self, admin_headers):
        """GET /api/admin/launch-mode returns mode with metadata (admin auth)"""
        response = requests.get(f"{BASE_URL}/api/admin/launch-mode", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "mode" in data, "Response should contain 'mode'"
        assert "message" in data, "Response should contain 'message'"
        assert "updated_at" in data, "Response should contain 'updated_at' metadata"
        assert "updated_by" in data, "Response should contain 'updated_by' metadata"
        print(f"✓ Admin launch mode with metadata: mode={data['mode']}, updated_by={data.get('updated_by')}")

    def test_admin_get_launch_mode_requires_auth(self):
        """Admin endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/launch-mode")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"

    def test_admin_set_launch_mode_ouvert(self, admin_headers):
        """PUT /api/admin/launch-mode changes mode to ouvert"""
        response = requests.put(
            f"{BASE_URL}/api/admin/launch-mode",
            json={"mode": "ouvert"},
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert data.get("mode") == "ouvert", f"Mode should be 'ouvert', got {data.get('mode')}"
        print("✓ Launch mode set to 'ouvert'")

    def test_admin_set_launch_mode_controle(self, admin_headers):
        """PUT /api/admin/launch-mode changes mode to controle"""
        response = requests.put(
            f"{BASE_URL}/api/admin/launch-mode",
            json={"mode": "controle"},
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("mode") == "controle"
        print("✓ Launch mode set to 'controle'")

    def test_admin_set_launch_mode_indisponible(self, admin_headers):
        """PUT /api/admin/launch-mode changes mode to indisponible"""
        response = requests.put(
            f"{BASE_URL}/api/admin/launch-mode",
            json={"mode": "indisponible"},
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("mode") == "indisponible"
        # Should have default message for indisponible
        assert data.get("message"), "Indisponible mode should have a message"
        print(f"✓ Launch mode set to 'indisponible' with message: {data.get('message')[:50]}...")

    def test_admin_set_launch_mode_rejects_invalid(self, admin_headers):
        """PUT /api/admin/launch-mode rejects invalid modes"""
        response = requests.put(
            f"{BASE_URL}/api/admin/launch-mode",
            json={"mode": "invalid_mode"},
            headers=admin_headers
        )
        assert response.status_code == 400, f"Expected 400 for invalid mode, got {response.status_code}"
        print("✓ Invalid mode correctly rejected with 400")

    def test_admin_set_launch_mode_requires_auth(self):
        """PUT endpoint should require authentication"""
        response = requests.put(
            f"{BASE_URL}/api/admin/launch-mode",
            json={"mode": "ouvert"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"


class TestCheckoutLaunchModeGating:
    """Tests for checkout endpoint launch mode gating"""

    def test_checkout_returns_503_when_indisponible(self, admin_headers):
        """POST /api/dossier-express/checkout returns 503 when launch mode is indisponible"""
        # First set mode to indisponible
        set_response = requests.put(
            f"{BASE_URL}/api/admin/launch-mode",
            json={"mode": "indisponible"},
            headers=admin_headers
        )
        assert set_response.status_code == 200, "Failed to set mode to indisponible"
        
        # Now try checkout
        checkout_response = requests.post(
            f"{BASE_URL}/api/dossier-express/checkout",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "origin_url": "https://example.com"
            }
        )
        assert checkout_response.status_code == 503, f"Expected 503 when indisponible, got {checkout_response.status_code}"
        
        # Verify premium French message (no technical jargon)
        data = checkout_response.json()
        detail = data.get("detail", "")
        assert "maintenance" in detail.lower() or "suspendu" in detail.lower(), f"Message should mention maintenance: {detail}"
        assert "error" not in detail.lower(), "Message should not contain technical jargon"
        print(f"✓ Checkout blocked with 503 and premium message: {detail[:60]}...")
        
        # Reset mode to ouvert for other tests
        requests.put(
            f"{BASE_URL}/api/admin/launch-mode",
            json={"mode": "ouvert"},
            headers=admin_headers
        )


class TestAdminMonitoring:
    """Tests for admin monitoring dashboard endpoint"""

    def test_monitoring_returns_live_kpis(self, admin_headers):
        """GET /api/admin/monitoring returns live KPIs with correct structure"""
        response = requests.get(f"{BASE_URL}/api/admin/monitoring", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check top-level structure
        assert "launch_mode" in data, "Response should contain 'launch_mode'"
        assert "kpis" in data, "Response should contain 'kpis'"
        assert "recent_incidents" in data, "Response should contain 'recent_incidents'"
        
        # Check KPIs structure (7 metrics as per requirements)
        kpis = data["kpis"]
        required_kpis = [
            "orders_today",
            "orders_7_days", 
            "success_rate_global",
            "success_rate_7_days",
            "incidents_today",
            "incidents_7_days",
            "avg_delivery_minutes",
            "pending_count",
            "intervention_required",
            "total_delivered"
        ]
        
        for kpi in required_kpis:
            assert kpi in kpis, f"Missing KPI: {kpi}"
        
        print(f"✓ Monitoring KPIs: orders_today={kpis['orders_today']}, success_rate_7d={kpis['success_rate_7_days']}%, incidents_today={kpis['incidents_today']}")

    def test_monitoring_requires_auth(self):
        """Monitoring endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/monitoring")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"

    def test_monitoring_kpi_values_are_numeric(self, admin_headers):
        """KPI values should be numeric types"""
        response = requests.get(f"{BASE_URL}/api/admin/monitoring", headers=admin_headers)
        assert response.status_code == 200
        
        kpis = response.json()["kpis"]
        numeric_kpis = ["orders_today", "orders_7_days", "incidents_today", "incidents_7_days", "pending_count", "intervention_required", "total_delivered"]
        
        for kpi in numeric_kpis:
            assert isinstance(kpis[kpi], (int, float)), f"{kpi} should be numeric, got {type(kpis[kpi])}"
        
        print("✓ All KPI values are numeric")


class TestClientDossierTracker:
    """Tests for client-facing dossier tracker (suivi endpoint)"""

    def test_suivi_returns_premium_labels(self):
        """GET /api/dossier-express/suivi/{id} returns client-facing premium labels"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{TEST_INCIDENT_DOSSIER_ID}")
        
        if response.status_code == 404:
            pytest.skip(f"Test dossier {TEST_INCIDENT_DOSSIER_ID} not found - may need to create test data")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check structure
        assert "dossier_id" in data, "Response should contain 'dossier_id'"
        assert "status" in data, "Response should contain 'status'"
        assert "message" in data, "Response should contain 'message'"
        assert "steps" in data, "Response should contain 'steps'"
        assert "current_label" in data, "Response should contain 'current_label'"
        
        # Verify no technical jargon in labels
        technical_terms = ["processing_step", "erreur_ia", "erreur_pdf", "extraction_en_cours", "checkout_valide"]
        for term in technical_terms:
            assert term not in str(data), f"Technical term '{term}' should not be exposed to client"
        
        print(f"✓ Client tracker returns premium labels: status={data['status']}, message={data['message'][:50]}...")

    def test_suivi_shows_7_steps(self):
        """Client tracker should show 7 steps in timeline"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{TEST_INCIDENT_DOSSIER_ID}")
        
        if response.status_code == 404:
            pytest.skip(f"Test dossier {TEST_INCIDENT_DOSSIER_ID} not found")
        
        assert response.status_code == 200
        
        data = response.json()
        steps = data.get("steps", [])
        
        assert len(steps) == 7, f"Expected 7 steps, got {len(steps)}"
        
        # Verify step keys
        expected_keys = ["received", "preparation", "reading", "analysis", "report", "delivery", "available"]
        actual_keys = [s["key"] for s in steps]
        assert actual_keys == expected_keys, f"Step keys mismatch: {actual_keys}"
        
        # Verify each step has required fields
        for step in steps:
            assert "key" in step, "Step should have 'key'"
            assert "label" in step, "Step should have 'label'"
            assert "status" in step, "Step should have 'status'"
            assert step["status"] in ["completed", "active", "waiting"], f"Invalid step status: {step['status']}"
        
        print(f"✓ Client tracker shows 7 steps: {[s['key'] for s in steps]}")

    def test_suivi_incident_shows_premium_message(self):
        """Incident dossier should show premium reassuring message"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{TEST_INCIDENT_DOSSIER_ID}")
        
        if response.status_code == 404:
            pytest.skip(f"Test dossier {TEST_INCIDENT_DOSSIER_ID} not found")
        
        assert response.status_code == 200
        
        data = response.json()
        
        # If this is an incident dossier, verify premium messaging
        if data.get("status") == "incident":
            message = data.get("message", "")
            # Should have reassuring message, not technical error
            assert "pris en charge" in message.lower() or "qualite" in message.lower(), f"Incident message should be reassuring: {message}"
            assert "error" not in message.lower(), "Message should not contain 'error'"
            assert "erreur" not in message.lower() or "technique" not in message.lower(), "Message should not expose technical errors"
            print(f"✓ Incident dossier shows premium message: {message[:60]}...")
        else:
            print(f"✓ Dossier status is '{data.get('status')}' (not incident)")

    def test_suivi_returns_404_for_nonexistent(self):
        """Client tracker returns 404 for non-existent dossier"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{fake_id}")
        
        assert response.status_code == 404, f"Expected 404 for non-existent dossier, got {response.status_code}"
        print("✓ Non-existent dossier returns 404")

    def test_suivi_completed_dossier_has_download_url(self):
        """Completed dossier should have download_url"""
        # First get a completed dossier from admin endpoint
        admin_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if admin_response.status_code != 200:
            pytest.skip("Could not authenticate as admin")
        
        data = admin_response.json()
        token = data.get("access_token") or data.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        dossiers_response = requests.get(f"{BASE_URL}/api/admin/dossier-express", headers=headers)
        if dossiers_response.status_code != 200:
            pytest.skip("Could not fetch dossiers")
        
        dossiers = dossiers_response.json().get("items", [])
        completed = [d for d in dossiers if d.get("status") == "completed" and d.get("download_token")]
        
        if not completed:
            pytest.skip("No completed dossiers with download_token found")
        
        # Test suivi for completed dossier
        completed_id = completed[0]["id"]
        suivi_response = requests.get(f"{BASE_URL}/api/dossier-express/suivi/{completed_id}")
        
        assert suivi_response.status_code == 200
        data = suivi_response.json()
        
        assert data.get("status") == "completed", f"Expected completed status, got {data.get('status')}"
        assert "download_url" in data, "Completed dossier should have download_url"
        print(f"✓ Completed dossier has download_url: {data['download_url'][:50]}...")


class TestCleanup:
    """Reset launch mode to ouvert after tests"""

    def test_reset_launch_mode_to_ouvert(self, admin_headers):
        """Reset launch mode to ouvert for production safety"""
        response = requests.put(
            f"{BASE_URL}/api/admin/launch-mode",
            json={"mode": "ouvert"},
            headers=admin_headers
        )
        assert response.status_code == 200
        print("✓ Launch mode reset to 'ouvert'")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
