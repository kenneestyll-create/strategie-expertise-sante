"""
Tests for Scheduled Email Campaigns Feature
- POST /api/admin/campaigns/schedule - Create scheduled campaign
- GET /api/admin/campaigns - List campaigns  
- PUT /api/admin/campaigns/{id}/cancel - Cancel campaign
- DELETE /api/admin/campaigns/{id} - Delete campaign
"""
import pytest
import requests
import os
from datetime import datetime, timedelta, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD


@pytest.fixture(scope="module")
def auth_token():
    """Get admin authentication token."""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json().get("access_token")


@pytest.fixture(scope="module")
def headers(auth_token):
    """Headers with auth token."""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def template_id(headers):
    """Get or create a template for testing."""
    # First try to get existing templates
    response = requests.get(f"{BASE_URL}/api/admin/email-templates", headers=headers)
    if response.status_code == 200:
        templates = response.json().get("templates", [])
        if templates:
            return templates[0]["id"]
    
    # Seed default templates if none exist
    requests.post(f"{BASE_URL}/api/admin/email-templates/seed", headers=headers)
    response = requests.get(f"{BASE_URL}/api/admin/email-templates", headers=headers)
    templates = response.json().get("templates", [])
    assert len(templates) > 0, "No templates available for testing"
    return templates[0]["id"]


class TestScheduleCampaign:
    """Test campaign scheduling endpoint."""
    
    def test_schedule_campaign_success(self, headers, template_id):
        """POST /api/admin/campaigns/schedule creates a campaign with status 'scheduled'."""
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        response = requests.post(f"{BASE_URL}/api/admin/campaigns/schedule", headers=headers, json={
            "template_id": template_id,
            "scheduled_at": tomorrow,
            "target": "inactive_clients"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "id" in data, "Response should contain campaign id"
        assert data["template_id"] == template_id, "template_id should match"
        assert data["status"] == "scheduled", "Status should be 'scheduled'"
        assert data["target"] == "inactive_clients", "Target should match"
        assert "scheduled_at" in data, "Should contain scheduled_at"
        assert "created_at" in data, "Should contain created_at"
        
        # Store for cleanup
        TestScheduleCampaign.created_campaign_id = data["id"]
    
    def test_schedule_campaign_with_past_date_returns_400(self, headers, template_id):
        """POST /api/admin/campaigns/schedule with past date returns 400 error."""
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        response = requests.post(f"{BASE_URL}/api/admin/campaigns/schedule", headers=headers, json={
            "template_id": template_id,
            "scheduled_at": yesterday,
            "target": "inactive_clients"
        })
        
        assert response.status_code == 400, f"Expected 400 for past date, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Should have error detail"
    
    def test_schedule_campaign_without_template_id_returns_400(self, headers):
        """POST /api/admin/campaigns/schedule without template_id returns 400."""
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        response = requests.post(f"{BASE_URL}/api/admin/campaigns/schedule", headers=headers, json={
            "scheduled_at": tomorrow,
            "target": "all_clients"
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_schedule_campaign_with_invalid_template_returns_404(self, headers):
        """POST /api/admin/campaigns/schedule with non-existent template returns 404."""
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        response = requests.post(f"{BASE_URL}/api/admin/campaigns/schedule", headers=headers, json={
            "template_id": "non-existent-template-id",
            "scheduled_at": tomorrow,
            "target": "inactive_clients"
        })
        
        assert response.status_code == 404, f"Expected 404 for invalid template, got {response.status_code}"
    
    def test_schedule_campaign_with_ab_test(self, headers, template_id):
        """POST /api/admin/campaigns/schedule with A/B test integration."""
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        
        # First check if there are any A/B tests
        ab_response = requests.get(f"{BASE_URL}/api/admin/ab-tests", headers=headers)
        ab_tests = ab_response.json().get("tests", [])
        
        payload = {
            "template_id": template_id,
            "scheduled_at": tomorrow,
            "target": "all_clients",
        }
        
        # If we have an active AB test, include it
        active_tests = [t for t in ab_tests if t.get("status") == "active"]
        if active_tests:
            payload["ab_test_id"] = active_tests[0]["id"]
        
        response = requests.post(f"{BASE_URL}/api/admin/campaigns/schedule", headers=headers, json=payload)
        
        assert response.status_code == 200, f"Schedule with target 'all_clients' should work: {response.text}"
        data = response.json()
        assert data["target"] == "all_clients", "Target should be 'all_clients'"
        
        # Cleanup
        if "id" in data:
            requests.delete(f"{BASE_URL}/api/admin/campaigns/{data['id']}", headers=headers)
    
    def test_schedule_campaign_requires_auth(self, template_id):
        """POST /api/admin/campaigns/schedule without auth returns 401/403."""
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        response = requests.post(f"{BASE_URL}/api/admin/campaigns/schedule", json={
            "template_id": template_id,
            "scheduled_at": tomorrow,
            "target": "inactive_clients"
        })
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"


class TestListCampaigns:
    """Test campaigns list endpoint."""
    
    def test_list_campaigns_success(self, headers):
        """GET /api/admin/campaigns returns list of campaigns with proper structure."""
        response = requests.get(f"{BASE_URL}/api/admin/campaigns", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "campaigns" in data, "Response should contain 'campaigns' array"
        assert isinstance(data["campaigns"], list), "campaigns should be a list"
        
        # Check campaign structure if any exist
        if data["campaigns"]:
            campaign = data["campaigns"][0]
            required_fields = ["id", "template_id", "status", "scheduled_at", "target"]
            for field in required_fields:
                assert field in campaign, f"Campaign should contain '{field}'"
    
    def test_list_campaigns_requires_auth(self):
        """GET /api/admin/campaigns without auth returns 401/403."""
        response = requests.get(f"{BASE_URL}/api/admin/campaigns")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"


class TestCancelCampaign:
    """Test cancel campaign endpoint."""
    
    def test_cancel_scheduled_campaign_success(self, headers, template_id):
        """PUT /api/admin/campaigns/{id}/cancel changes status to 'cancelled'."""
        # First create a campaign to cancel
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        create_response = requests.post(f"{BASE_URL}/api/admin/campaigns/schedule", headers=headers, json={
            "template_id": template_id,
            "scheduled_at": tomorrow,
            "target": "inactive_clients"
        })
        
        assert create_response.status_code == 200, "Should create campaign first"
        campaign_id = create_response.json()["id"]
        
        # Now cancel it
        response = requests.put(f"{BASE_URL}/api/admin/campaigns/{campaign_id}/cancel", headers=headers)
        
        assert response.status_code == 200, f"Cancel should succeed: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Should return success=True"
        
        # Verify status changed
        list_response = requests.get(f"{BASE_URL}/api/admin/campaigns", headers=headers)
        campaigns = list_response.json().get("campaigns", [])
        cancelled = [c for c in campaigns if c["id"] == campaign_id]
        assert len(cancelled) == 1, "Should find the cancelled campaign"
        assert cancelled[0]["status"] == "cancelled", "Status should be 'cancelled'"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/campaigns/{campaign_id}", headers=headers)
    
    def test_cancel_non_scheduled_campaign_returns_400(self, headers, template_id):
        """PUT /api/admin/campaigns/{id}/cancel on non-scheduled campaign returns 400."""
        # Create and cancel a campaign first
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        create_response = requests.post(f"{BASE_URL}/api/admin/campaigns/schedule", headers=headers, json={
            "template_id": template_id,
            "scheduled_at": tomorrow,
            "target": "inactive_clients"
        })
        campaign_id = create_response.json()["id"]
        
        # Cancel it once
        requests.put(f"{BASE_URL}/api/admin/campaigns/{campaign_id}/cancel", headers=headers)
        
        # Try to cancel again (now it's 'cancelled' not 'scheduled')
        response = requests.put(f"{BASE_URL}/api/admin/campaigns/{campaign_id}/cancel", headers=headers)
        
        assert response.status_code == 400, f"Expected 400 for already cancelled, got {response.status_code}"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/campaigns/{campaign_id}", headers=headers)
    
    def test_cancel_nonexistent_campaign_returns_404(self, headers):
        """PUT /api/admin/campaigns/{id}/cancel on non-existent campaign returns 404."""
        response = requests.put(f"{BASE_URL}/api/admin/campaigns/nonexistent-id/cancel", headers=headers)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestDeleteCampaign:
    """Test delete campaign endpoint."""
    
    def test_delete_campaign_success(self, headers, template_id):
        """DELETE /api/admin/campaigns/{id} removes the campaign."""
        # Create a campaign to delete
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        create_response = requests.post(f"{BASE_URL}/api/admin/campaigns/schedule", headers=headers, json={
            "template_id": template_id,
            "scheduled_at": tomorrow,
            "target": "inactive_clients"
        })
        campaign_id = create_response.json()["id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/admin/campaigns/{campaign_id}", headers=headers)
        
        assert response.status_code == 200, f"Delete should succeed: {response.text}"
        assert response.json().get("success") == True, "Should return success=True"
        
        # Verify it's gone
        list_response = requests.get(f"{BASE_URL}/api/admin/campaigns", headers=headers)
        campaigns = list_response.json().get("campaigns", [])
        assert all(c["id"] != campaign_id for c in campaigns), "Campaign should be deleted"
    
    def test_delete_nonexistent_campaign_returns_404(self, headers):
        """DELETE /api/admin/campaigns/{id} on non-existent campaign returns 404."""
        response = requests.delete(f"{BASE_URL}/api/admin/campaigns/nonexistent-id-12345", headers=headers)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestCampaignStatusFlow:
    """Test campaign status transitions and data integrity."""
    
    def test_campaign_has_all_required_fields(self, headers, template_id):
        """Verify campaign record contains all required fields."""
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        response = requests.post(f"{BASE_URL}/api/admin/campaigns/schedule", headers=headers, json={
            "template_id": template_id,
            "scheduled_at": tomorrow,
            "target": "inactive_clients"
        })
        
        data = response.json()
        
        required_fields = [
            "id", "template_id", "template_name", "template_label",
            "scheduled_at", "target", "status", "recipients_count",
            "sent_count", "failed_count", "created_at"
        ]
        
        for field in required_fields:
            assert field in data, f"Campaign should have '{field}' field"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/campaigns/{data['id']}", headers=headers)
    
    def test_campaign_valid_statuses(self, headers):
        """Verify campaigns only have valid status values."""
        response = requests.get(f"{BASE_URL}/api/admin/campaigns", headers=headers)
        campaigns = response.json().get("campaigns", [])
        
        valid_statuses = ["scheduled", "executing", "sent", "cancelled", "failed"]
        
        for campaign in campaigns:
            assert campaign["status"] in valid_statuses, f"Invalid status: {campaign['status']}"


# Cleanup fixture to remove test campaigns after all tests
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_campaigns(headers):
    """Cleanup test campaigns after module completes."""
    yield
    
    # Get all campaigns and delete test ones
    try:
        response = requests.get(f"{BASE_URL}/api/admin/campaigns", headers=headers)
        campaigns = response.json().get("campaigns", [])
        
        for campaign in campaigns:
            # Delete campaigns created in the last hour (likely test data)
            created_at = campaign.get("created_at", "")
            if created_at:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) - created < timedelta(hours=1):
                    requests.delete(f"{BASE_URL}/api/admin/campaigns/{campaign['id']}", headers=headers)
    except Exception:
        pass
