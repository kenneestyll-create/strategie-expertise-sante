"""
Test Alerte Urgente (Urgent Alert) feature
- POST /api/alerte-urgente: Create urgent alert (public)
- GET /api/admin/alertes-urgentes: List alerts (admin)
- PUT /api/admin/alertes-urgentes/{id}: Mark as treated (admin)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials (seeded in server.py)
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


class TestAlerteUrgentePublic:
    """Test public endpoint for creating urgent alerts"""

    def test_create_alerte_2h_formule(self):
        """Test creating an urgent alert with '2h' formule"""
        payload = {
            "nom": f"TEST_User_{uuid.uuid4().hex[:6]}",
            "telephone": "0612345678",
            "email": "test@example.com",
            "message": "Test urgent alert - 2h formule",
            "formule": "2h"
        }
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "id" in data
        print(f"PASS: Created urgent alert with 2h formule, id={data['id']}")
        return data["id"]

    def test_create_alerte_30min_formule(self):
        """Test creating an urgent alert with '30min' formule (premium)"""
        payload = {
            "nom": f"TEST_User_30min_{uuid.uuid4().hex[:6]}",
            "telephone": "0698765432",
            "email": "test30min@example.com",
            "message": "Test urgent alert - 30min premium formule",
            "formule": "30min"
        }
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "id" in data
        print(f"PASS: Created urgent alert with 30min formule, id={data['id']}")
        return data["id"]

    def test_create_alerte_minimal_fields(self):
        """Test creating an urgent alert with only required fields (nom, telephone)"""
        payload = {
            "nom": f"TEST_Minimal_{uuid.uuid4().hex[:6]}",
            "telephone": "0600112233"
        }
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print(f"PASS: Created alert with minimal fields")

    def test_create_alerte_missing_nom(self):
        """Test validation - missing nom should return 400"""
        payload = {
            "telephone": "0600112233",
            "formule": "2h"
        }
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json=payload)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print(f"PASS: Missing nom returns 400 as expected")

    def test_create_alerte_missing_telephone(self):
        """Test validation - missing telephone should return 400"""
        payload = {
            "nom": "Test User",
            "formule": "2h"
        }
        response = requests.post(f"{BASE_URL}/api/alerte-urgente", json=payload)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print(f"PASS: Missing telephone returns 400 as expected")


class TestAlerteUrgenteAdmin:
    """Test admin endpoints for managing urgent alerts"""

    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json()["access_token"]

    @pytest.fixture
    def auth_headers(self, admin_token):
        """Auth headers with admin token"""
        return {"Authorization": f"Bearer {admin_token}"}

    def test_get_alertes_list(self, auth_headers):
        """Test retrieving list of urgent alerts"""
        response = requests.get(f"{BASE_URL}/api/admin/alertes-urgentes", headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check response structure
        assert "items" in data, "Response should have 'items' key"
        assert "total" in data, "Response should have 'total' key"
        assert "non_traite" in data, "Response should have 'non_traite' key"
        
        # Check data types
        assert isinstance(data["items"], list), "'items' should be a list"
        assert isinstance(data["total"], int), "'total' should be an int"
        assert isinstance(data["non_traite"], int), "'non_traite' should be an int"
        
        print(f"PASS: Retrieved {data['total']} alerts ({data['non_traite']} untreated)")

    def test_get_alertes_requires_auth(self):
        """Test that listing alerts requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/alertes-urgentes")
        
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422, got {response.status_code}"
        print(f"PASS: Alerts list requires authentication (returned {response.status_code})")

    def test_mark_alerte_as_treated(self, auth_headers):
        """Test marking an alert as treated"""
        # First create a new alert
        payload = {
            "nom": f"TEST_ToTreat_{uuid.uuid4().hex[:6]}",
            "telephone": "0699887766",
            "formule": "2h"
        }
        create_response = requests.post(f"{BASE_URL}/api/alerte-urgente", json=payload)
        assert create_response.status_code == 200
        alert_id = create_response.json()["id"]
        
        # Verify it appears in the list as untreated
        list_response = requests.get(f"{BASE_URL}/api/admin/alertes-urgentes", headers=auth_headers)
        assert list_response.status_code == 200
        alerts = list_response.json()["items"]
        new_alert = next((a for a in alerts if a["id"] == alert_id), None)
        assert new_alert is not None, f"New alert {alert_id} not found in list"
        assert new_alert.get("traite") is False, "New alert should not be treated"
        
        # Mark it as treated
        update_response = requests.put(
            f"{BASE_URL}/api/admin/alertes-urgentes/{alert_id}",
            json={"traite": True, "status": "traité"},
            headers=auth_headers
        )
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}: {update_response.text}"
        
        # Verify it's now treated
        list_response2 = requests.get(f"{BASE_URL}/api/admin/alertes-urgentes", headers=auth_headers)
        assert list_response2.status_code == 200
        alerts2 = list_response2.json()["items"]
        updated_alert = next((a for a in alerts2 if a["id"] == alert_id), None)
        assert updated_alert is not None
        assert updated_alert.get("traite") is True, "Alert should now be treated"
        
        print(f"PASS: Marked alert {alert_id} as treated and verified")

    def test_update_alerte_requires_auth(self):
        """Test that updating alert requires authentication"""
        fake_id = "non-existent-id"
        response = requests.put(
            f"{BASE_URL}/api/admin/alertes-urgentes/{fake_id}",
            json={"traite": True}
        )
        
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422, got {response.status_code}"
        print(f"PASS: Update alert requires authentication (returned {response.status_code})")


class TestAlertDataIntegrity:
    """Test data integrity of urgent alerts"""

    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]

    @pytest.fixture
    def auth_headers(self, admin_token):
        return {"Authorization": f"Bearer {admin_token}"}

    def test_alert_fields_persisted(self, auth_headers):
        """Test that all alert fields are correctly persisted"""
        unique_name = f"TEST_DataCheck_{uuid.uuid4().hex[:6]}"
        payload = {
            "nom": unique_name,
            "telephone": "0611223344",
            "email": "datacheck@test.com",
            "message": "Testing data persistence",
            "formule": "30min"
        }
        create_response = requests.post(f"{BASE_URL}/api/alerte-urgente", json=payload)
        assert create_response.status_code == 200
        alert_id = create_response.json()["id"]
        
        # Fetch and verify
        list_response = requests.get(f"{BASE_URL}/api/admin/alertes-urgentes", headers=auth_headers)
        assert list_response.status_code == 200
        
        alerts = list_response.json()["items"]
        our_alert = next((a for a in alerts if a["id"] == alert_id), None)
        
        assert our_alert is not None, f"Alert {alert_id} not found"
        assert our_alert["nom"] == unique_name, f"Expected nom={unique_name}, got {our_alert['nom']}"
        assert our_alert["telephone"] == "0611223344"
        assert our_alert["email"] == "datacheck@test.com"
        assert our_alert["message"] == "Testing data persistence"
        assert our_alert["formule"] == "30min"
        assert our_alert["traite"] is False
        assert "created_at" in our_alert
        
        print(f"PASS: All alert fields persisted correctly for {alert_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
