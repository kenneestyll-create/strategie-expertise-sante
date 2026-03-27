"""
Test suite for Conversion & ROI features:
- PATCH /api/admin/contacts/{id} with status=converti, conversion_montant, conversion_prestation, conversion_date
- GET /api/admin/stats returns 'converti' count and 'total_revenue'
- GET /api/tracking/conversion-analytics returns channels with conversions, revenue, close_rate
- GET /api/tracking/conversion-analytics returns 'prestations' array
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


class TestConversionROI:
    """Test conversion and ROI features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token = None
        self.test_contact_id = None
    
    def get_auth_token(self):
        """Get admin authentication token"""
        if self.token:
            return self.token
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            return self.token
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_01_admin_login(self):
        """Test admin login works"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        print("PASS: Admin login successful")
    
    def test_02_get_stats_returns_converti_and_revenue(self):
        """Test GET /api/admin/stats returns converti count and total_revenue"""
        self.get_auth_token()
        response = self.session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        
        # Verify required fields exist
        assert "total" in data, "Missing 'total' field"
        assert "nouveau" in data, "Missing 'nouveau' field"
        assert "en_cours" in data, "Missing 'en_cours' field"
        assert "traite" in data, "Missing 'traite' field"
        assert "converti" in data, "Missing 'converti' field"
        assert "total_revenue" in data, "Missing 'total_revenue' field"
        
        # Verify types
        assert isinstance(data["converti"], int), "converti should be int"
        assert isinstance(data["total_revenue"], (int, float)), "total_revenue should be numeric"
        
        print(f"PASS: Stats returned - converti={data['converti']}, total_revenue={data['total_revenue']}")
    
    def test_03_create_test_contact_for_conversion(self):
        """Create a test contact to convert"""
        response = self.session.post(f"{BASE_URL}/api/contact", json={
            "nom": "TEST_ConversionTest",
            "prenom": "ROI",
            "email": "test_conversion_roi@test.com",
            "telephone": "0600000000",
            "sujet": "Test conversion ROI",
            "message": "Test message for conversion testing",
            "tracking_via": "qr",
            "tracking_source": "dossier_express"
        })
        assert response.status_code in [200, 201], f"Contact creation failed: {response.text}"
        data = response.json()
        self.__class__.test_contact_id = data.get("id")
        assert self.__class__.test_contact_id, "Contact ID not returned"
        print(f"PASS: Test contact created with ID: {self.__class__.test_contact_id}")
    
    def test_04_patch_contact_with_conversion_fields(self):
        """Test PATCH /api/admin/contacts/{id} accepts conversion fields"""
        self.get_auth_token()
        contact_id = getattr(self.__class__, 'test_contact_id', None)
        if not contact_id:
            pytest.skip("No test contact ID available")
        
        today = datetime.now().strftime("%Y-%m-%d")
        response = self.session.patch(f"{BASE_URL}/api/admin/contacts/{contact_id}", json={
            "status": "converti",
            "conversion_montant": 350.0,
            "conversion_prestation": "accompagnement_mp",
            "conversion_date": today
        })
        assert response.status_code == 200, f"Patch failed: {response.text}"
        data = response.json()
        
        # Verify conversion fields are returned
        assert data.get("status") == "converti", "Status not updated to converti"
        assert data.get("conversion_montant") == 350.0, "conversion_montant not set"
        assert data.get("conversion_prestation") == "accompagnement_mp", "conversion_prestation not set"
        assert data.get("conversion_date") == today, "conversion_date not set"
        
        print(f"PASS: Contact converted with montant=350, prestation=accompagnement_mp")
    
    def test_05_get_contact_shows_conversion_data(self):
        """Verify GET contact returns conversion data"""
        self.get_auth_token()
        contact_id = getattr(self.__class__, 'test_contact_id', None)
        if not contact_id:
            pytest.skip("No test contact ID available")
        
        response = self.session.get(f"{BASE_URL}/api/admin/contacts/{contact_id}")
        assert response.status_code == 200, f"Get contact failed: {response.text}"
        data = response.json()
        
        assert data.get("status") == "converti"
        assert data.get("conversion_montant") == 350.0
        assert data.get("conversion_prestation") == "accompagnement_mp"
        assert data.get("conversion_date") is not None
        
        print("PASS: GET contact returns conversion data correctly")
    
    def test_06_stats_include_converted_contact(self):
        """Verify stats include the converted contact"""
        self.get_auth_token()
        response = self.session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Should have at least 1 converted contact (our test + any existing)
        assert data["converti"] >= 1, f"Expected at least 1 converti, got {data['converti']}"
        # Revenue should include our 350
        assert data["total_revenue"] >= 350, f"Expected revenue >= 350, got {data['total_revenue']}"
        
        print(f"PASS: Stats show converti={data['converti']}, revenue={data['total_revenue']}")
    
    def test_07_conversion_analytics_returns_channels(self):
        """Test GET /api/tracking/conversion-analytics returns channels with required fields"""
        self.get_auth_token()
        response = self.session.get(f"{BASE_URL}/api/tracking/conversion-analytics?period=30d")
        assert response.status_code == 200, f"Analytics failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "channels" in data, "Missing 'channels' field"
        assert "totals" in data, "Missing 'totals' field"
        assert "timeseries" in data, "Missing 'timeseries' field"
        assert "prestations" in data, "Missing 'prestations' field"
        
        # Verify totals have required fields
        totals = data["totals"]
        assert "conversions" in totals, "Missing 'conversions' in totals"
        assert "revenue" in totals, "Missing 'revenue' in totals"
        assert "close_rate" in totals, "Missing 'close_rate' in totals"
        
        print(f"PASS: Conversion analytics structure valid - totals: {totals}")
    
    def test_08_conversion_analytics_channels_have_revenue(self):
        """Test channels in conversion-analytics have conversions, revenue, close_rate"""
        self.get_auth_token()
        response = self.session.get(f"{BASE_URL}/api/tracking/conversion-analytics?period=30d")
        assert response.status_code == 200
        data = response.json()
        
        channels = data.get("channels", [])
        if len(channels) > 0:
            for ch in channels:
                assert "via" in ch, "Channel missing 'via'"
                assert "conversions" in ch, "Channel missing 'conversions'"
                assert "revenue" in ch, "Channel missing 'revenue'"
                assert "close_rate" in ch, "Channel missing 'close_rate'"
            print(f"PASS: {len(channels)} channels have required fields (conversions, revenue, close_rate)")
        else:
            print("PASS: No channels yet (empty but structure valid)")
    
    def test_09_conversion_analytics_prestations_array(self):
        """Test conversion-analytics returns prestations array with prestation/count/revenue"""
        self.get_auth_token()
        response = self.session.get(f"{BASE_URL}/api/tracking/conversion-analytics?period=30d")
        assert response.status_code == 200
        data = response.json()
        
        prestations = data.get("prestations", [])
        assert isinstance(prestations, list), "prestations should be a list"
        
        if len(prestations) > 0:
            for p in prestations:
                assert "prestation" in p, "Prestation item missing 'prestation'"
                assert "count" in p, "Prestation item missing 'count'"
                assert "revenue" in p, "Prestation item missing 'revenue'"
            print(f"PASS: {len(prestations)} prestations found with required fields")
        else:
            print("PASS: No prestations yet (empty but structure valid)")
    
    def test_10_conversion_analytics_7d_period(self):
        """Test conversion-analytics with 7d period"""
        self.get_auth_token()
        response = self.session.get(f"{BASE_URL}/api/tracking/conversion-analytics?period=7d")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("period") == "7d", "Period should be 7d"
        assert "totals" in data
        assert "channels" in data
        
        print("PASS: 7d period analytics works")
    
    def test_11_homepage_loads(self):
        """Test homepage loads correctly"""
        response = self.session.get(f"{BASE_URL}/")
        assert response.status_code == 200, f"Homepage failed: {response.status_code}"
        print("PASS: Homepage loads correctly")
    
    def test_12_cleanup_test_contact(self):
        """Cleanup: Delete test contact"""
        self.get_auth_token()
        contact_id = getattr(self.__class__, 'test_contact_id', None)
        if contact_id:
            response = self.session.delete(f"{BASE_URL}/api/admin/contacts/{contact_id}")
            if response.status_code in [200, 204]:
                print(f"PASS: Test contact {contact_id} deleted")
            else:
                print(f"WARNING: Could not delete test contact: {response.status_code}")
        else:
            print("SKIP: No test contact to delete")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
