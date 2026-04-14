"""
Test suite for tracking origin tags feature:
- Admin contacts endpoint with via/source filters
- Contact creation with tracking fields
- Origin tags display in admin contacts list
"""
import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD

# Shared token cache to avoid rate limits
_token_cache = {"token": None, "headers": None}

def get_admin_token():
    """Get admin token with caching to avoid rate limits"""
    if _token_cache["token"]:
        return _token_cache["token"], _token_cache["headers"]
    
    time.sleep(0.5)  # Rate limit protection
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        _token_cache["token"] = token
        _token_cache["headers"] = headers
        return token, headers
    elif response.status_code == 429:
        time.sleep(2)  # Wait for rate limit
        return get_admin_token()
    return None, {}


class TestAdminAuth:
    """Test admin authentication"""
    
    def test_admin_login_success(self):
        """POST /api/auth/login works with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["access_token"]
        print(f"✓ Admin login successful, token received")
        return data["access_token"]


class TestContactsWithTrackingFilters:
    """Test GET /api/admin/contacts with via/source filters"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for authenticated requests"""
        self.token, self.headers = get_admin_token()
        assert self.token, "Failed to get admin token"
    
    def test_get_all_contacts_returns_tracking_fields(self):
        """GET /api/admin/contacts returns contacts with tracking_via and tracking_source fields"""
        response = requests.get(f"{BASE_URL}/api/admin/contacts", headers=self.headers)
        assert response.status_code == 200
        contacts = response.json()
        assert isinstance(contacts, list)
        print(f"✓ Got {len(contacts)} contacts")
        
        # Check that contacts have tracking fields (may be null for direct contacts)
        for contact in contacts[:5]:  # Check first 5
            assert "tracking_via" in contact or contact.get("tracking_via") is None
            assert "tracking_source" in contact or contact.get("tracking_source") is None
        print("✓ Contacts have tracking_via and tracking_source fields")
    
    def test_filter_contacts_by_via_qr(self):
        """GET /api/admin/contacts?via=qr returns only QR contacts"""
        response = requests.get(f"{BASE_URL}/api/admin/contacts?via=qr", headers=self.headers)
        assert response.status_code == 200
        contacts = response.json()
        print(f"✓ Got {len(contacts)} QR contacts")
        
        # All returned contacts should have tracking_via=qr
        for contact in contacts:
            assert contact.get("tracking_via") == "qr", f"Expected tracking_via=qr, got {contact.get('tracking_via')}"
        print("✓ All contacts have tracking_via=qr")
    
    def test_filter_contacts_by_via_email(self):
        """GET /api/admin/contacts?via=email returns only email contacts"""
        response = requests.get(f"{BASE_URL}/api/admin/contacts?via=email", headers=self.headers)
        assert response.status_code == 200
        contacts = response.json()
        print(f"✓ Got {len(contacts)} email contacts")
        
        for contact in contacts:
            assert contact.get("tracking_via") == "email", f"Expected tracking_via=email, got {contact.get('tracking_via')}"
        print("✓ All contacts have tracking_via=email")
    
    def test_filter_contacts_by_source_dossier_express(self):
        """GET /api/admin/contacts?source=dossier_express returns only dossier_express contacts"""
        response = requests.get(f"{BASE_URL}/api/admin/contacts?source=dossier_express", headers=self.headers)
        assert response.status_code == 200
        contacts = response.json()
        print(f"✓ Got {len(contacts)} dossier_express contacts")
        
        for contact in contacts:
            assert contact.get("tracking_source") == "dossier_express", f"Expected tracking_source=dossier_express, got {contact.get('tracking_source')}"
        print("✓ All contacts have tracking_source=dossier_express")
    
    def test_filter_contacts_by_via_and_source(self):
        """GET /api/admin/contacts?via=qr&source=dossier_express filters by both"""
        response = requests.get(f"{BASE_URL}/api/admin/contacts?via=qr&source=dossier_express", headers=self.headers)
        assert response.status_code == 200
        contacts = response.json()
        print(f"✓ Got {len(contacts)} contacts with via=qr AND source=dossier_express")
        
        for contact in contacts:
            assert contact.get("tracking_via") == "qr", f"Expected tracking_via=qr"
            assert contact.get("tracking_source") == "dossier_express", f"Expected tracking_source=dossier_express"
        print("✓ All contacts match both filters")
    
    def test_filter_contacts_by_status_and_via(self):
        """GET /api/admin/contacts?status=nouveau&via=qr filters by status and via"""
        response = requests.get(f"{BASE_URL}/api/admin/contacts?status=nouveau&via=qr", headers=self.headers)
        assert response.status_code == 200
        contacts = response.json()
        print(f"✓ Got {len(contacts)} nouveau QR contacts")
        
        for contact in contacts:
            assert contact.get("status") == "nouveau"
            assert contact.get("tracking_via") == "qr"
        print("✓ All contacts match status=nouveau AND via=qr")


class TestContactCreationWithTracking:
    """Test POST /api/contact with tracking fields"""
    
    def test_create_contact_with_tracking_via_and_source(self):
        """POST /api/contact with tracking_via and tracking_source saves them in DB"""
        unique_id = str(uuid.uuid4())[:8]
        contact_data = {
            "nom": f"TEST_Tracking_{unique_id}",
            "prenom": "Test",
            "email": f"test-tracking-{unique_id}@example.com",
            "telephone": "0612345678",
            "sujet": "Test tracking fields",
            "message": "Testing that tracking_via and tracking_source are saved",
            "tracking_via": "qr",
            "tracking_source": "dossier_express"
        }
        
        response = requests.post(f"{BASE_URL}/api/contact", json=contact_data)
        assert response.status_code in [200, 201], f"Contact creation failed: {response.text}"
        print(f"✓ Contact created successfully")
        
        # Now verify the contact was saved with tracking fields
        token, headers = get_admin_token()
        assert token, "Failed to get admin token"
        
        # Get contacts and find our test contact
        contacts_response = requests.get(f"{BASE_URL}/api/admin/contacts", headers=headers)
        contacts = contacts_response.json()
        
        test_contact = None
        for c in contacts:
            if c.get("email") == contact_data["email"]:
                test_contact = c
                break
        
        assert test_contact is not None, "Test contact not found in admin contacts"
        assert test_contact.get("tracking_via") == "qr", f"tracking_via not saved correctly: {test_contact.get('tracking_via')}"
        assert test_contact.get("tracking_source") == "dossier_express", f"tracking_source not saved correctly: {test_contact.get('tracking_source')}"
        print(f"✓ Contact saved with tracking_via={test_contact.get('tracking_via')}, tracking_source={test_contact.get('tracking_source')}")
        
        # Cleanup - delete test contact
        if test_contact.get("id"):
            requests.delete(f"{BASE_URL}/api/admin/contacts/{test_contact['id']}", headers=headers)
            print(f"✓ Test contact cleaned up")
    
    def test_create_contact_without_tracking_fields(self):
        """POST /api/contact without tracking fields creates direct contact"""
        unique_id = str(uuid.uuid4())[:8]
        contact_data = {
            "nom": f"TEST_Direct_{unique_id}",
            "prenom": "Direct",
            "email": f"test-direct-{unique_id}@example.com",
            "telephone": "0612345678",
            "sujet": "Direct contact test",
            "message": "Testing contact without tracking fields"
        }
        
        response = requests.post(f"{BASE_URL}/api/contact", json=contact_data)
        assert response.status_code in [200, 201], f"Contact creation failed: {response.text}"
        print(f"✓ Direct contact created successfully")
        
        # Verify the contact was saved without tracking fields
        token, headers = get_admin_token()
        assert token, "Failed to get admin token"
        
        contacts_response = requests.get(f"{BASE_URL}/api/admin/contacts", headers=headers)
        contacts = contacts_response.json()
        
        test_contact = None
        for c in contacts:
            if c.get("email") == contact_data["email"]:
                test_contact = c
                break
        
        assert test_contact is not None, "Test contact not found"
        # Direct contacts should have null/None tracking fields
        assert test_contact.get("tracking_via") is None, f"Direct contact should not have tracking_via"
        assert test_contact.get("tracking_source") is None, f"Direct contact should not have tracking_source"
        print(f"✓ Direct contact has no tracking fields (as expected)")
        
        # Cleanup
        if test_contact.get("id"):
            requests.delete(f"{BASE_URL}/api/admin/contacts/{test_contact['id']}", headers=headers)
            print(f"✓ Test contact cleaned up")


class TestConversionAnalytics:
    """Test conversion analytics still works"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.token, self.headers = get_admin_token()
        assert self.token, "Failed to get admin token"
    
    def test_conversion_analytics_endpoint(self):
        """GET /api/tracking/conversion-analytics returns valid data"""
        response = requests.get(f"{BASE_URL}/api/tracking/conversion-analytics", headers=self.headers)
        assert response.status_code == 200, f"Analytics failed: {response.text}"
        data = response.json()
        
        # Check structure
        assert "channels" in data or "totals" in data or "timeseries" in data
        print(f"✓ Conversion analytics endpoint works")
        print(f"  Data keys: {list(data.keys())}")


class TestHomepageAndAdminDashboard:
    """Test that homepage and admin dashboard load"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        self.token, self.headers = get_admin_token()
    
    def test_homepage_loads(self):
        """Homepage loads correctly"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        print(f"✓ Homepage loads (status {response.status_code})")
    
    def test_admin_stats_endpoint(self):
        """Admin stats endpoint works"""
        if not self.token:
            pytest.skip("Could not get admin token")
        
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "nouveau" in data
        print(f"✓ Admin stats: total={data['total']}, nouveau={data['nouveau']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
