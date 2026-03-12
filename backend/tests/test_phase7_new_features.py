"""
Test Phase 7 - New Features Testing
Tests for: Agenda/Booking, Simulateur, Client Portal, Resources PDF Library, Relance System, Admin Tabs
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ==================== FIXTURES ====================

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@accompagn-sante.fr",
        "password": "Admin2024!"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed")

@pytest.fixture
def admin_headers(admin_token):
    """Headers with admin auth"""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}

@pytest.fixture
def test_client_credentials():
    """Test client credentials - use existing or create new"""
    return {
        "email": f"testclient_{uuid.uuid4().hex[:8]}@test.fr",
        "password": "testpass123",
        "name": "Test Client Phase7"
    }


# ==================== BOOKING / AGENDA TESTS ====================

class TestBookingSlots:
    """Test booking slot availability endpoint"""
    
    def test_get_slots_for_date(self, api_client):
        """GET /api/bookings/slots/{date} returns available slots"""
        # Use a future date
        import datetime
        future_date = (datetime.date.today() + datetime.timedelta(days=7))
        # Skip to next weekday if weekend
        while future_date.weekday() >= 5:
            future_date += datetime.timedelta(days=1)
        date_str = future_date.strftime("%Y-%m-%d")
        
        response = api_client.get(f"{BASE_URL}/api/bookings/slots/{date_str}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "date" in data
        assert "slots" in data
        assert isinstance(data["slots"], list)
        print(f"PASS: GET /api/bookings/slots/{date_str} returned {len(data['slots'])} slots")


class TestBookingCRUD:
    """Test booking creation endpoint"""
    
    def test_create_booking(self, api_client):
        """POST /api/bookings creates a new booking"""
        import datetime
        future_date = (datetime.date.today() + datetime.timedelta(days=10))
        # Skip to next weekday
        while future_date.weekday() >= 5:
            future_date += datetime.timedelta(days=1)
        date_str = future_date.strftime("%Y-%m-%d")
        
        # Get available slots first
        slots_res = api_client.get(f"{BASE_URL}/api/bookings/slots/{date_str}")
        slots = slots_res.json().get("slots", [])
        
        if not slots:
            pytest.skip("No available slots for test date")
        
        booking_data = {
            "name": "TEST_BookingUser",
            "email": f"testbooking_{uuid.uuid4().hex[:6]}@test.fr",
            "phone": "0600000000",
            "booking_type": "telephone",
            "date": date_str,
            "time_slot": slots[0],
            "message": "Test booking from automated tests"
        }
        
        response = api_client.post(f"{BASE_URL}/api/bookings", json=booking_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "booking_id" in data
        print(f"PASS: POST /api/bookings created booking {data['booking_id']}")


# ==================== CLIENT PORTAL TESTS ====================

class TestClientRegistration:
    """Test client registration and login"""
    
    def test_register_client(self, api_client, test_client_credentials):
        """POST /api/client/register creates new client account"""
        response = api_client.post(f"{BASE_URL}/api/client/register", json=test_client_credentials)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert "client_name" in data
        assert "client_id" in data
        assert data["client_name"] == test_client_credentials["name"]
        print(f"PASS: POST /api/client/register created client {data['client_id']}")
        return data
    
    def test_register_duplicate_email(self, api_client):
        """POST /api/client/register rejects duplicate email"""
        # First registration
        email = f"dup_{uuid.uuid4().hex[:6]}@test.fr"
        api_client.post(f"{BASE_URL}/api/client/register", json={
            "email": email, "password": "test123", "name": "Dup Test"
        })
        
        # Second registration with same email
        response = api_client.post(f"{BASE_URL}/api/client/register", json={
            "email": email, "password": "test123", "name": "Dup Test 2"
        })
        assert response.status_code == 409, f"Expected 409 for duplicate email"
        print("PASS: Duplicate email registration rejected with 409")


class TestClientLogin:
    """Test client login endpoint"""
    
    def test_login_client(self, api_client):
        """POST /api/client/login returns JWT token"""
        # First create a client
        email = f"login_{uuid.uuid4().hex[:6]}@test.fr"
        password = "logintest123"
        
        reg_res = api_client.post(f"{BASE_URL}/api/client/register", json={
            "email": email, "password": password, "name": "Login Test"
        })
        assert reg_res.status_code == 200
        
        # Now login
        response = api_client.post(f"{BASE_URL}/api/client/login", json={
            "email": email, "password": password
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        print("PASS: POST /api/client/login returned JWT token")
    
    def test_login_invalid_credentials(self, api_client):
        """POST /api/client/login rejects invalid credentials"""
        response = api_client.post(f"{BASE_URL}/api/client/login", json={
            "email": "nonexistent@test.fr",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Invalid credentials rejected with 401")


class TestClientPortal:
    """Test client portal authenticated endpoints"""
    
    def test_get_client_profile(self, api_client):
        """GET /api/client/profile returns profile (authenticated)"""
        # Create and login client
        email = f"profile_{uuid.uuid4().hex[:6]}@test.fr"
        reg_res = api_client.post(f"{BASE_URL}/api/client/register", json={
            "email": email, "password": "test123", "name": "Profile Test"
        })
        token = reg_res.json().get("access_token")
        
        response = api_client.get(
            f"{BASE_URL}/api/client/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["email"] == email
        assert data["name"] == "Profile Test"
        print("PASS: GET /api/client/profile returned client data")
    
    def test_get_client_cases(self, api_client):
        """GET /api/client/cases returns case list (authenticated)"""
        email = f"cases_{uuid.uuid4().hex[:6]}@test.fr"
        reg_res = api_client.post(f"{BASE_URL}/api/client/register", json={
            "email": email, "password": "test123", "name": "Cases Test"
        })
        token = reg_res.json().get("access_token")
        
        response = api_client.get(
            f"{BASE_URL}/api/client/cases",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list)  # Empty list for new client
        print(f"PASS: GET /api/client/cases returned {len(data)} cases")
    
    def test_client_profile_requires_auth(self, api_client):
        """GET /api/client/profile requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/client/profile")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth"
        print("PASS: /api/client/profile requires authentication")


# ==================== SIMULATOR TESTS ====================

class TestSimulator:
    """Test simulator result saving endpoint"""
    
    def test_save_simulator_result(self, api_client):
        """POST /api/simulator/result saves simulation data"""
        result_data = {
            "answers": {
                "situation": "at",
                "demarche": "en_cours",
                "anciennete": "moyen",
                "accompagnement": "seul",
                "besoin": "comprendre"
            },
            "profile": "Victime d'accident du travail",
            "recommendations": ["Test recommendation 1", "Test recommendation 2"],
            "email": f"simulator_{uuid.uuid4().hex[:6]}@test.fr"
        }
        
        response = api_client.post(f"{BASE_URL}/api/simulator/result", json=result_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "id" in data
        print(f"PASS: POST /api/simulator/result saved result {data['id']}")


# ==================== RESOURCES / DOWNLOAD TRACKING TESTS ====================

class TestResourcesDownload:
    """Test resource download tracking endpoint"""
    
    def test_track_resource_download(self, api_client):
        """POST /api/resources/download tracks download"""
        download_data = {
            "resource_id": "guide_mp",
            "resource_title": "Guide : Déclarer une maladie professionnelle"
        }
        
        response = api_client.post(f"{BASE_URL}/api/resources/download", json=download_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True
        print("PASS: POST /api/resources/download tracked download")


# ==================== ABANDONED CHECKOUT / RELANCE TESTS ====================

class TestRelanceTracking:
    """Test abandoned checkout tracking endpoint"""
    
    def test_track_abandoned_checkout(self, api_client):
        """POST /api/relance/track records abandoned checkout"""
        abandoned_data = {
            "email": f"abandoned_{uuid.uuid4().hex[:6]}@test.fr",
            "name": "Test Abandonment",
            "package_id": "analyse_dossier"
        }
        
        response = api_client.post(f"{BASE_URL}/api/relance/track", json=abandoned_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True
        print("PASS: POST /api/relance/track recorded abandoned checkout")
    
    def test_track_requires_email(self, api_client):
        """POST /api/relance/track requires email"""
        response = api_client.post(f"{BASE_URL}/api/relance/track", json={
            "name": "No Email",
            "package_id": "analyse_dossier"
        })
        assert response.status_code == 400, f"Expected 400 without email"
        print("PASS: /api/relance/track requires email")


# ==================== ADMIN ENDPOINTS TESTS ====================

class TestAdminBookings:
    """Test admin bookings endpoint"""
    
    def test_admin_get_bookings(self, api_client, admin_headers):
        """GET /api/admin/bookings returns bookings list"""
        response = api_client.get(f"{BASE_URL}/api/admin/bookings", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET /api/admin/bookings returned {len(data)} bookings")
    
    def test_admin_bookings_requires_auth(self, api_client):
        """GET /api/admin/bookings requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/admin/bookings")
        assert response.status_code in [401, 403]
        print("PASS: /api/admin/bookings requires authentication")


class TestAdminRelance:
    """Test admin relance endpoints"""
    
    def test_admin_get_relance(self, api_client, admin_headers):
        """GET /api/admin/relance returns abandoned checkouts"""
        response = api_client.get(f"{BASE_URL}/api/admin/relance", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "items" in data
        assert "stats" in data
        assert "total" in data["stats"]
        assert "not_sent" in data["stats"]
        assert "sent" in data["stats"]
        print(f"PASS: GET /api/admin/relance returned {len(data['items'])} items")
    
    def test_admin_send_relance(self, api_client, admin_headers):
        """POST /api/admin/relance/send/{id} sends relance"""
        # First create an abandoned checkout
        api_client.post(f"{BASE_URL}/api/relance/track", json={
            "email": f"relance_test_{uuid.uuid4().hex[:6]}@test.fr",
            "name": "Relance Test",
            "package_id": "analyse_dossier"
        })
        
        # Get the list to find the item
        relance_res = api_client.get(f"{BASE_URL}/api/admin/relance", headers=admin_headers)
        items = relance_res.json().get("items", [])
        
        if not items:
            pytest.skip("No abandoned checkouts to test relance")
        
        # Find one that hasn't been sent
        unsent = [i for i in items if not i.get("relance_sent")]
        if not unsent:
            pytest.skip("All items already relanced")
        
        item_id = unsent[0]["id"]
        response = api_client.post(f"{BASE_URL}/api/admin/relance/send/{item_id}", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True
        # Note: email_sent will be false since Resend is not configured
        print(f"PASS: POST /api/admin/relance/send/{item_id} marked as relanced (email_sent={data.get('email_sent')})")


class TestAdminClients:
    """Test admin clients endpoint"""
    
    def test_admin_get_clients(self, api_client, admin_headers):
        """GET /api/admin/clients returns client list"""
        response = api_client.get(f"{BASE_URL}/api/admin/clients", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list)
        # Each client should have cases_count
        if data:
            assert "cases_count" in data[0]
        print(f"PASS: GET /api/admin/clients returned {len(data)} clients")
    
    def test_admin_clients_requires_auth(self, api_client):
        """GET /api/admin/clients requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/admin/clients")
        assert response.status_code in [401, 403]
        print("PASS: /api/admin/clients requires authentication")


class TestAdminSimulatorStats:
    """Test admin simulator stats endpoint"""
    
    def test_admin_get_simulator_stats(self, api_client, admin_headers):
        """GET /api/admin/simulator/stats returns stats"""
        response = api_client.get(f"{BASE_URL}/api/admin/simulator/stats", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "total" in data
        assert "recent" in data
        print(f"PASS: GET /api/admin/simulator/stats returned {data['total']} total results")


# ==================== HEALTH CHECK ====================

class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self, api_client):
        """GET /api/health returns healthy status"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: API health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
