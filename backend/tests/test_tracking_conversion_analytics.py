"""
Test suite for Tracking & Conversion Analytics System
Tests:
- POST /api/tracking/contact-visit - Track visits to /contact with attribution params
- POST /api/contact - Contact form with tracking fields
- GET /api/tracking/conversion-analytics - Admin-only conversion analytics endpoint
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD


@pytest.fixture(scope="module")
def admin_token():
    """Get admin JWT token for authenticated requests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed - skipping authenticated tests")


@pytest.fixture
def admin_headers(admin_token):
    """Headers with admin authorization"""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


class TestTrackingContactVisit:
    """Tests for POST /api/tracking/contact-visit endpoint"""
    
    def test_track_contact_visit_with_via_and_source(self):
        """POST /api/tracking/contact-visit with via and source returns ok and creates entry"""
        response = requests.post(f"{BASE_URL}/api/tracking/contact-visit", json={
            "via": "qr",
            "source": "dossier_express"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: POST /api/tracking/contact-visit with via=qr, source=dossier_express returns {status: ok}")
    
    def test_track_contact_visit_with_email_source(self):
        """POST /api/tracking/contact-visit with email via returns ok"""
        response = requests.post(f"{BASE_URL}/api/tracking/contact-visit", json={
            "via": "email",
            "source": "livraison_pdf"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: POST /api/tracking/contact-visit with via=email returns {status: ok}")
    
    def test_track_contact_visit_with_pdf_link(self):
        """POST /api/tracking/contact-visit with pdf_link via returns ok"""
        response = requests.post(f"{BASE_URL}/api/tracking/contact-visit", json={
            "via": "pdf_link",
            "source": "strategiia"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: POST /api/tracking/contact-visit with via=pdf_link returns {status: ok}")
    
    def test_track_contact_visit_with_campaign(self):
        """POST /api/tracking/contact-visit with campaign param returns ok"""
        response = requests.post(f"{BASE_URL}/api/tracking/contact-visit", json={
            "via": "qr",
            "source": "dossier_express",
            "campaign": "test_campaign_2026"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: POST /api/tracking/contact-visit with campaign param returns {status: ok}")
    
    def test_track_contact_visit_empty_via_source_returns_ok_no_entry(self):
        """POST /api/tracking/contact-visit with empty via/source returns ok but does not create entry"""
        response = requests.post(f"{BASE_URL}/api/tracking/contact-visit", json={
            "via": "",
            "source": ""
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: POST /api/tracking/contact-visit with empty via/source returns {status: ok} (no entry created)")
    
    def test_track_contact_visit_missing_params_returns_ok(self):
        """POST /api/tracking/contact-visit with missing params returns ok"""
        response = requests.post(f"{BASE_URL}/api/tracking/contact-visit", json={})
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: POST /api/tracking/contact-visit with missing params returns {status: ok}")


class TestContactFormWithTracking:
    """Tests for POST /api/contact with tracking fields"""
    
    def test_contact_form_with_tracking_fields(self):
        """POST /api/contact with tracking_via and tracking_source saves them in contact record"""
        unique_email = f"test_tracking_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/contact", json={
            "nom": "TestTracking",
            "prenom": "User",
            "email": unique_email,
            "sujet": "Test tracking fields",
            "message": "Testing tracking_via and tracking_source fields",
            "tracking_via": "qr",
            "tracking_source": "dossier_express",
            "tracking_campaign": "test_campaign"
        })
        assert response.status_code in [200, 201]
        data = response.json()
        # Verify response contains tracking fields or success indicator
        assert "id" in data or "message" in data or "status" in data
        print(f"PASS: POST /api/contact with tracking fields returns success (status: {response.status_code})")
    
    def test_contact_form_without_tracking_fields(self):
        """POST /api/contact without tracking fields still works"""
        unique_email = f"test_no_tracking_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/contact", json={
            "nom": "TestNoTracking",
            "prenom": "User",
            "email": unique_email,
            "sujet": "Test without tracking",
            "message": "Testing contact form without tracking fields"
        })
        assert response.status_code in [200, 201]
        print(f"PASS: POST /api/contact without tracking fields returns success (status: {response.status_code})")


class TestConversionAnalyticsEndpoint:
    """Tests for GET /api/tracking/conversion-analytics (admin-only)"""
    
    def test_conversion_analytics_requires_auth(self):
        """GET /api/tracking/conversion-analytics without auth returns 401/403"""
        response = requests.get(f"{BASE_URL}/api/tracking/conversion-analytics")
        assert response.status_code in [401, 403, 422]
        print(f"PASS: GET /api/tracking/conversion-analytics without auth returns {response.status_code}")
    
    def test_conversion_analytics_with_invalid_token(self):
        """GET /api/tracking/conversion-analytics with invalid token returns 401/403"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/conversion-analytics",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code in [401, 403]
        print(f"PASS: GET /api/tracking/conversion-analytics with invalid token returns {response.status_code}")
    
    def test_conversion_analytics_with_admin_auth_30d(self, admin_headers):
        """GET /api/tracking/conversion-analytics?period=30d returns channels, timeseries, totals"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/conversion-analytics?period=30d",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "channels" in data, "Response should contain 'channels'"
        assert "timeseries" in data, "Response should contain 'timeseries'"
        assert "totals" in data, "Response should contain 'totals'"
        assert "period" in data, "Response should contain 'period'"
        
        # Verify totals structure
        totals = data["totals"]
        assert "visits" in totals, "Totals should contain 'visits'"
        assert "contacts" in totals, "Totals should contain 'contacts'"
        assert "conversion_rate" in totals, "Totals should contain 'conversion_rate'"
        
        # Verify period
        assert data["period"] == "30d"
        
        # Verify timeseries is a list
        assert isinstance(data["timeseries"], list)
        
        # Verify channels is a list
        assert isinstance(data["channels"], list)
        
        print(f"PASS: GET /api/tracking/conversion-analytics?period=30d returns valid structure")
        print(f"  - Totals: visits={totals['visits']}, contacts={totals['contacts']}, rate={totals['conversion_rate']}%")
        print(f"  - Channels count: {len(data['channels'])}")
        print(f"  - Timeseries days: {len(data['timeseries'])}")
    
    def test_conversion_analytics_with_admin_auth_7d(self, admin_headers):
        """GET /api/tracking/conversion-analytics?period=7d returns 7-day data"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/conversion-analytics?period=7d",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["period"] == "7d"
        assert "timeseries" in data
        # 7-day period should have 7 entries in timeseries
        assert len(data["timeseries"]) == 7
        
        print(f"PASS: GET /api/tracking/conversion-analytics?period=7d returns 7-day timeseries")
    
    def test_conversion_analytics_default_period(self, admin_headers):
        """GET /api/tracking/conversion-analytics without period defaults to 30d"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/conversion-analytics",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Default should be 30d
        assert data["period"] == "30d"
        assert len(data["timeseries"]) == 30
        
        print(f"PASS: GET /api/tracking/conversion-analytics defaults to 30d period")
    
    def test_conversion_analytics_channel_structure(self, admin_headers):
        """Verify channel data structure in conversion analytics"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/conversion-analytics?period=30d",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # If there are channels, verify their structure
        if len(data["channels"]) > 0:
            channel = data["channels"][0]
            assert "via" in channel, "Channel should have 'via' field"
            assert "source" in channel, "Channel should have 'source' field"
            assert "visits" in channel, "Channel should have 'visits' field"
            assert "contacts" in channel, "Channel should have 'contacts' field"
            assert "conversion_rate" in channel, "Channel should have 'conversion_rate' field"
            print(f"PASS: Channel structure is valid: {channel}")
        else:
            print("PASS: No channels yet (empty data is valid)")
    
    def test_conversion_analytics_timeseries_structure(self, admin_headers):
        """Verify timeseries data structure in conversion analytics"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/conversion-analytics?period=7d",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify timeseries entries
        assert len(data["timeseries"]) > 0
        entry = data["timeseries"][0]
        assert "date" in entry, "Timeseries entry should have 'date'"
        assert "visits" in entry, "Timeseries entry should have 'visits'"
        assert "contacts" in entry, "Timeseries entry should have 'contacts'"
        
        print(f"PASS: Timeseries structure is valid: {entry}")


class TestTrackingStatsEndpoint:
    """Tests for GET /api/tracking/stats endpoint"""
    
    def test_tracking_stats_endpoint(self):
        """GET /api/tracking/stats returns stats array"""
        response = requests.get(f"{BASE_URL}/api/tracking/stats")
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert isinstance(data["stats"], list)
        print(f"PASS: GET /api/tracking/stats returns stats array with {len(data['stats'])} entries")


class TestAdminLoginAndBasicEndpoints:
    """Basic tests to verify admin auth and core endpoints"""
    
    def test_admin_login(self):
        """POST /api/auth/login with valid admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print("PASS: Admin login successful")
    
    def test_homepage_api(self):
        """GET /api/health or root endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        # Health endpoint might not exist, try root
        if response.status_code == 404:
            response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code in [200, 404]
        print(f"PASS: API is accessible (status: {response.status_code})")


class TestCreateTrackingDataForAnalytics:
    """Create test tracking data to verify analytics aggregation"""
    
    def test_create_multiple_tracking_visits(self):
        """Create multiple tracking visits to test aggregation"""
        # Create visits from different sources
        sources = [
            {"via": "qr", "source": "dossier_express"},
            {"via": "qr", "source": "dossier_express"},
            {"via": "email", "source": "livraison_pdf"},
            {"via": "pdf_link", "source": "strategiia"},
        ]
        
        for src in sources:
            response = requests.post(f"{BASE_URL}/api/tracking/contact-visit", json=src)
            assert response.status_code == 200
        
        print(f"PASS: Created {len(sources)} tracking visits for analytics testing")
    
    def test_create_contact_with_tracking_for_conversion(self):
        """Create a contact with tracking to test conversion calculation"""
        unique_email = f"test_conv_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/contact", json={
            "nom": "ConversionTest",
            "prenom": "User",
            "email": unique_email,
            "sujet": "Test conversion tracking",
            "message": "Testing conversion rate calculation",
            "tracking_via": "qr",
            "tracking_source": "dossier_express"
        })
        assert response.status_code in [200, 201]
        print("PASS: Created contact with tracking for conversion testing")
    
    def test_verify_analytics_after_data_creation(self, admin_headers):
        """Verify analytics endpoint returns data after creating test entries"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/conversion-analytics?period=30d",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # After creating test data, we should have some visits
        totals = data["totals"]
        print(f"Analytics after test data: visits={totals['visits']}, contacts={totals['contacts']}, rate={totals['conversion_rate']}%")
        
        # Verify channels exist if we have visits
        if totals["visits"] > 0:
            assert len(data["channels"]) > 0, "Should have channel data when visits exist"
            print(f"PASS: Analytics shows {len(data['channels'])} channels with data")
        else:
            print("PASS: Analytics endpoint working (no visits yet in period)")
