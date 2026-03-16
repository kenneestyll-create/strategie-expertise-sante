"""
Test suite to validate server refactoring from monolithic (4327 lines) to modular structure.
Tests all endpoints to ensure they work identically after the refactoring.
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ocr-scanner-7.preview.emergentagent.com').rstrip('/')


class TestPublicEndpoints:
    """Public routes from routes/public.py"""
    
    def test_root_endpoint(self):
        """GET /api/ - welcome message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Bienvenue" in data["message"]
        print(f"✓ Root endpoint returns: {data['message']}")
    
    def test_health_endpoint(self):
        """GET /api/health - health status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print(f"✓ Health check: {data['status']}")
    
    def test_faq_endpoint(self):
        """GET /api/faq - FAQ list"""
        response = requests.get(f"{BASE_URL}/api/faq")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ FAQ endpoint returns {len(data)} items")
    
    def test_avis_endpoint(self):
        """GET /api/avis - published reviews"""
        response = requests.get(f"{BASE_URL}/api/avis")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Avis endpoint returns {len(data)} published reviews")
    
    def test_contact_create(self):
        """POST /api/contact - create contact request"""
        payload = {
            "nom": "Test",
            "prenom": "Refactoring",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "sujet": "Test refactoring validation",
            "message": "This is a test contact from refactoring validation"
        }
        response = requests.post(f"{BASE_URL}/api/contact", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "id" in data
        print(f"✓ Contact created with id: {data['id']}")
    
    def test_visitors_count(self):
        """GET /api/visitors/count"""
        response = requests.get(f"{BASE_URL}/api/visitors/count")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        print(f"✓ Visitor count: {data['count']}")


class TestAdminAuth:
    """Admin authentication from routes/admin.py"""
    
    def test_admin_login_success(self):
        """POST /api/auth/login - admin login"""
        payload = {
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "admin_name" in data
        print(f"✓ Admin login successful, admin_name: {data['admin_name']}")
        return data["access_token"]
    
    def test_admin_login_wrong_password(self):
        """POST /api/auth/login - wrong password"""
        payload = {
            "email": "admin@accompagn-sante.fr",
            "password": "WrongPassword123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 401
        print("✓ Wrong password correctly rejected with 401")


class TestAdminProtectedEndpoints:
    """Admin-protected routes from routes/admin.py"""
    
    @pytest.fixture
    def admin_token(self):
        payload = {
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        return response.json()["access_token"]
    
    def test_admin_stats(self, admin_token):
        """GET /api/admin/stats - contact stats"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "nouveau" in data
        assert "en_cours" in data
        assert "traite" in data
        print(f"✓ Admin stats: total={data['total']}, nouveau={data['nouveau']}")
    
    def test_admin_analytics(self, admin_token):
        """GET /api/admin/analytics?period=30d - analytics with kpis and time_series"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/analytics?period=30d", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "kpis" in data
        assert "time_series" in data
        assert "total_contacts" in data["kpis"]
        print(f"✓ Analytics: total_contacts={data['kpis']['total_contacts']}, time_series has {len(data['time_series'])} days")
    
    def test_admin_stats_without_auth(self):
        """GET /api/admin/stats - requires auth (should fail without token)"""
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code in [401, 403]
        print("✓ Admin stats correctly requires authentication")


class TestForumEndpoints:
    """Forum routes from routes/forum.py"""
    
    def test_forum_categories(self):
        """GET /api/forum/categories - returns 6 categories"""
        response = requests.get(f"{BASE_URL}/api/forum/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 6
        category_names = [c["name"] for c in data]
        print(f"✓ Forum categories: {len(data)} categories")
        assert "Accident du travail" in category_names
        assert "Maladie professionnelle" in category_names
    
    def test_forum_topics(self):
        """GET /api/forum/topics"""
        response = requests.get(f"{BASE_URL}/api/forum/topics")
        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
        assert "total" in data
        print(f"✓ Forum topics: {data['total']} total topics")


class TestPaymentEndpoints:
    """Payment routes from routes/payments.py"""
    
    def test_payment_packages(self):
        """GET /api/payments/packages - returns 10 packages"""
        response = requests.get(f"{BASE_URL}/api/payments/packages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10
        # Check structure
        for pkg in data:
            assert "id" in pkg
            assert "name" in pkg
            assert "amount" in pkg
            assert "currency" in pkg
        print(f"✓ Payment packages: {len(data)} packages")
        # Print first package as sample
        print(f"  Sample: {data[0]['id']} - {data[0]['name']} - {data[0]['amount']}€")


class TestClientPortal:
    """Client portal routes from routes/client.py"""
    
    @pytest.fixture
    def test_client_email(self):
        return f"test_refactor_{uuid.uuid4().hex[:8]}@example.com"
    
    def test_client_register(self, test_client_email):
        """POST /api/client/register - register new client"""
        payload = {
            "email": test_client_email,
            "password": "TestPass123!",
            "name": "Test Refactor Client"
        }
        response = requests.post(f"{BASE_URL}/api/client/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["client_name"] == "Test Refactor Client"
        print(f"✓ Client registered: {test_client_email}")
        return data
    
    def test_client_login(self, test_client_email):
        """POST /api/client/login after registration"""
        # First register
        reg_payload = {
            "email": test_client_email,
            "password": "TestPass123!",
            "name": "Test Client Login"
        }
        requests.post(f"{BASE_URL}/api/client/register", json=reg_payload)
        
        # Then login
        login_payload = {
            "email": test_client_email,
            "password": "TestPass123!"
        }
        response = requests.post(f"{BASE_URL}/api/client/login", json=login_payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print(f"✓ Client login successful")
        return data["access_token"]
    
    def test_client_profile(self):
        """GET /api/client/profile - requires client token"""
        # Register and get token
        email = f"test_profile_{uuid.uuid4().hex[:8]}@example.com"
        reg = requests.post(f"{BASE_URL}/api/client/register", json={
            "email": email,
            "password": "TestPass123!",
            "name": "Test Profile Client"
        })
        token = reg.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/client/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["name"] == "Test Profile Client"
        print(f"✓ Client profile retrieved: {data['name']}")
    
    def test_client_progress(self):
        """GET /api/client/progress - client progress dashboard"""
        email = f"test_progress_{uuid.uuid4().hex[:8]}@example.com"
        reg = requests.post(f"{BASE_URL}/api/client/register", json={
            "email": email,
            "password": "TestPass123!",
            "name": "Test Progress Client"
        })
        token = reg.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/client/progress", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "progress_pct" in data
        assert "steps" in data
        assert len(data["steps"]) == 6
        print(f"✓ Client progress: {data['progress_pct']}%")
    
    def test_client_documents(self):
        """GET /api/client/documents - list client documents"""
        email = f"test_docs_{uuid.uuid4().hex[:8]}@example.com"
        reg = requests.post(f"{BASE_URL}/api/client/register", json={
            "email": email,
            "password": "TestPass123!",
            "name": "Test Docs Client"
        })
        token = reg.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/client/documents", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
        print(f"✓ Client documents: {data['total']} documents")
    
    def test_client_notifications(self):
        """GET /api/client/notifications"""
        email = f"test_notif_{uuid.uuid4().hex[:8]}@example.com"
        reg = requests.post(f"{BASE_URL}/api/client/register", json={
            "email": email,
            "password": "TestPass123!",
            "name": "Test Notifications Client"
        })
        token = reg.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/client/notifications", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        print(f"✓ Client notifications: {data['unread_count']} unread")


class TestBookingEndpoints:
    """Booking routes from routes/misc.py"""
    
    def test_booking_slots(self):
        """GET /api/bookings/slots/{date} - available slots"""
        response = requests.get(f"{BASE_URL}/api/bookings/slots/2026-04-01")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "slots" in data
        assert isinstance(data["slots"], list)
        print(f"✓ Booking slots for 2026-04-01: {len(data['slots'])} available")


class TestStrategiiaEndpoints:
    """StrategiIA routes from routes/strategiia.py"""
    
    def test_strategiia_score(self):
        """GET /api/strategiia/score?type_dossier=at - relevance score"""
        response = requests.get(f"{BASE_URL}/api/strategiia/score?type_dossier=at")
        assert response.status_code == 200
        data = response.json()
        # Can have score=None if no cases exist, or a valid response
        assert "confidence" in data
        assert "total_cases" in data
        print(f"✓ StrategiIA score: total_cases={data['total_cases']}, confidence={data['confidence']}")


class TestDocumentEndpoints:
    """Document validation from routes/misc.py"""
    
    def test_document_validate(self):
        """POST /api/documents/validate - validate document"""
        payload = {
            "filename": "test_document.pdf",
            "size": 500000,
            "mime_type": "application/pdf"
        }
        response = requests.post(f"{BASE_URL}/api/documents/validate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "errors" in data
        assert data["valid"] == True
        print(f"✓ Document validation: valid={data['valid']}")
    
    def test_document_validate_invalid_format(self):
        """POST /api/documents/validate - invalid format"""
        payload = {
            "filename": "test.exe",
            "size": 500000,
            "mime_type": "application/octet-stream"
        }
        response = requests.post(f"{BASE_URL}/api/documents/validate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == False
        assert len(data["errors"]) > 0
        print(f"✓ Invalid format rejected: {data['errors'][0]}")


class TestChatbotEndpoints:
    """Chatbot routes from routes/chatbot.py"""
    
    def test_chatbot_message(self):
        """POST /api/chatbot - send message"""
        payload = {
            "message": "Qu'est-ce qu'une maladie professionnelle ?",
            "session_id": str(uuid.uuid4())
        }
        response = requests.post(f"{BASE_URL}/api/chatbot", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        print(f"✓ Chatbot response received (is_faq={data.get('is_faq', False)})")
    
    def test_chatbot_quota(self):
        """GET /api/chatbot/quota/{session_id}"""
        session_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/chatbot/quota/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert "remaining" in data
        assert "limit" in data
        assert data["limit"] == 5
        print(f"✓ Chatbot quota: {data['remaining']}/{data['limit']} remaining")


class TestSEOEndpoints:
    """SEO routes from routes/misc.py"""
    
    def test_sitemap_xml(self):
        """GET /api/sitemap.xml"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        assert "xml" in response.headers.get("content-type", "")
        assert "<urlset" in response.text
        print(f"✓ Sitemap.xml generated successfully")
    
    def test_robots_txt(self):
        """GET /api/robots.txt"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        assert "User-agent" in response.text
        print(f"✓ Robots.txt generated successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
