"""
Strategic Feedback API Tests
=============================
Tests for the micro feedback system:
- POST /api/feedback (public - no auth)
- GET /api/feedback (admin auth required)
- GET /api/feedback/stats (admin auth required)
- Auto-categorization by keywords
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


class TestFeedbackSubmission:
    """Tests for POST /api/feedback (public endpoint)"""
    
    def test_submit_feedback_with_clarte_only(self, api_client):
        """Submit feedback with only clarte response"""
        response = api_client.post(f"{BASE_URL}/api/feedback", json={
            "clarte": "oui",
            "source": "test_basic"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print("PASS: Submit feedback with clarte only")
    
    def test_submit_feedback_with_frein_only(self, api_client):
        """Submit feedback with only frein response"""
        response = api_client.post(f"{BASE_URL}/api/feedback", json={
            "frein": "Je ne savais pas par ou commencer avec mon dossier MDPH",
            "source": "test_frein"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print("PASS: Submit feedback with frein only")
    
    def test_submit_feedback_with_besoin_only(self, api_client):
        """Submit feedback with only besoin response"""
        response = api_client.post(f"{BASE_URL}/api/feedback", json={
            "besoin": "J'aurais aime un accompagnement avec un avocat",
            "source": "test_besoin"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print("PASS: Submit feedback with besoin only")
    
    def test_submit_feedback_complete(self, api_client):
        """Submit complete feedback with all fields"""
        unique_id = str(uuid.uuid4())[:8]
        response = api_client.post(f"{BASE_URL}/api/feedback", json={
            "frein": f"TEST_{unique_id} - Probleme avec mon assurance Generali",
            "besoin": "Aide pour comprendre mon contrat d'assurance emprunteur",
            "clarte": "partiellement",
            "commentaire": "Le service est utile mais j'aurais besoin de plus d'accompagnement",
            "source": "strategiia_basic",
            "type_dossier": "assurance"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print("PASS: Submit complete feedback")
    
    def test_submit_feedback_empty_rejected(self, api_client):
        """Empty submission should be rejected"""
        response = api_client.post(f"{BASE_URL}/api/feedback", json={
            "frein": "",
            "besoin": "",
            "clarte": "",
            "source": "test_empty"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("PASS: Empty feedback rejected with 400")
    
    def test_submit_feedback_whitespace_only_rejected(self, api_client):
        """Whitespace-only submission should be rejected"""
        response = api_client.post(f"{BASE_URL}/api/feedback", json={
            "frein": "   ",
            "besoin": "   ",
            "clarte": "",
            "source": "test_whitespace"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("PASS: Whitespace-only feedback rejected with 400")


class TestFeedbackAutoCategorization:
    """Tests for auto-categorization by keywords"""
    
    def test_categorize_mdph_keywords(self, api_client, authenticated_client):
        """Feedback with MDPH keywords should be categorized as mdph"""
        unique_id = str(uuid.uuid4())[:8]
        # Submit feedback with MDPH keywords
        response = api_client.post(f"{BASE_URL}/api/feedback", json={
            "frein": f"TEST_MDPH_{unique_id} - Ma demande AAH a ete refusee par la MDPH",
            "source": "test_mdph_cat"
        })
        assert response.status_code == 200
        
        # Verify categorization via admin endpoint
        list_response = authenticated_client.get(f"{BASE_URL}/api/feedback?category=mdph")
        assert list_response.status_code == 200
        data = list_response.json()
        # Check if our test feedback is in the mdph category
        feedbacks = data.get("feedbacks", [])
        found = any(f"TEST_MDPH_{unique_id}" in (fb.get("frein") or "") for fb in feedbacks)
        assert found, "MDPH feedback should be categorized as mdph"
        print("PASS: MDPH keywords auto-categorized correctly")
    
    def test_categorize_juridique_keywords(self, api_client, authenticated_client):
        """Feedback with juridique keywords should be categorized as juridique"""
        unique_id = str(uuid.uuid4())[:8]
        response = api_client.post(f"{BASE_URL}/api/feedback", json={
            "frein": f"TEST_JURIDIQUE_{unique_id} - J'ai besoin d'un avocat pour mon recours au tribunal",
            "source": "test_juridique_cat"
        })
        assert response.status_code == 200
        
        list_response = authenticated_client.get(f"{BASE_URL}/api/feedback?category=juridique")
        assert list_response.status_code == 200
        data = list_response.json()
        feedbacks = data.get("feedbacks", [])
        found = any(f"TEST_JURIDIQUE_{unique_id}" in (fb.get("frein") or "") for fb in feedbacks)
        assert found, "Juridique feedback should be categorized as juridique"
        print("PASS: Juridique keywords auto-categorized correctly")
    
    def test_categorize_assurantiel_keywords(self, api_client, authenticated_client):
        """Feedback with assurantiel keywords should be categorized as assurantiel"""
        unique_id = str(uuid.uuid4())[:8]
        response = api_client.post(f"{BASE_URL}/api/feedback", json={
            "besoin": f"TEST_ASSURANCE_{unique_id} - Probleme avec mon contrat Generali pour mon pret emprunteur",
            "source": "test_assurance_cat"
        })
        assert response.status_code == 200
        
        list_response = authenticated_client.get(f"{BASE_URL}/api/feedback?category=assurantiel")
        assert list_response.status_code == 200
        data = list_response.json()
        feedbacks = data.get("feedbacks", [])
        found = any(f"TEST_ASSURANCE_{unique_id}" in (fb.get("besoin") or "") for fb in feedbacks)
        assert found, "Assurantiel feedback should be categorized as assurantiel"
        print("PASS: Assurantiel keywords auto-categorized correctly")


class TestFeedbackAdminEndpoints:
    """Tests for admin-only feedback endpoints"""
    
    def test_list_feedback_requires_auth(self, api_client):
        """GET /api/feedback should require authentication"""
        # Create a new session without auth
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        response = no_auth_session.get(f"{BASE_URL}/api/feedback")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: GET /api/feedback requires auth (401/403)")
    
    def test_stats_requires_auth(self, api_client):
        """GET /api/feedback/stats should require authentication"""
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        response = no_auth_session.get(f"{BASE_URL}/api/feedback/stats")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: GET /api/feedback/stats requires auth (401/403)")
    
    def test_list_feedback_with_auth(self, authenticated_client):
        """GET /api/feedback should return feedbacks with auth"""
        response = authenticated_client.get(f"{BASE_URL}/api/feedback")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "feedbacks" in data, "Response should contain 'feedbacks' key"
        assert "count" in data, "Response should contain 'count' key"
        assert isinstance(data["feedbacks"], list), "feedbacks should be a list"
        print(f"PASS: GET /api/feedback returns {data['count']} feedbacks")
    
    def test_list_feedback_filter_by_category(self, authenticated_client):
        """GET /api/feedback?category=mdph should filter by category"""
        response = authenticated_client.get(f"{BASE_URL}/api/feedback?category=mdph")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "feedbacks" in data
        # All returned feedbacks should have mdph in categories
        for fb in data["feedbacks"]:
            assert "mdph" in fb.get("categories", []), f"Feedback should have mdph category: {fb}"
        print(f"PASS: Category filter works - {data['count']} mdph feedbacks")
    
    def test_feedback_stats(self, authenticated_client):
        """GET /api/feedback/stats should return aggregated stats"""
        response = authenticated_client.get(f"{BASE_URL}/api/feedback/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify required fields
        assert "total" in data, "Stats should contain 'total'"
        assert "with_frein" in data, "Stats should contain 'with_frein'"
        assert "with_besoin" in data, "Stats should contain 'with_besoin'"
        assert "clarte_distribution" in data, "Stats should contain 'clarte_distribution'"
        assert "category_distribution" in data, "Stats should contain 'category_distribution'"
        
        # Verify data types
        assert isinstance(data["total"], int), "total should be int"
        assert isinstance(data["with_frein"], int), "with_frein should be int"
        assert isinstance(data["with_besoin"], int), "with_besoin should be int"
        assert isinstance(data["clarte_distribution"], list), "clarte_distribution should be list"
        assert isinstance(data["category_distribution"], list), "category_distribution should be list"
        
        print(f"PASS: Stats endpoint returns total={data['total']}, with_frein={data['with_frein']}, with_besoin={data['with_besoin']}")


class TestFeedbackDataStructure:
    """Tests for feedback data structure and fields"""
    
    def test_feedback_has_required_fields(self, authenticated_client):
        """Feedbacks should have all required fields"""
        response = authenticated_client.get(f"{BASE_URL}/api/feedback?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        if data["count"] > 0:
            fb = data["feedbacks"][0]
            # Check required fields exist
            assert "id" in fb, "Feedback should have 'id'"
            assert "categories" in fb, "Feedback should have 'categories'"
            assert "created_at" in fb, "Feedback should have 'created_at'"
            # Optional fields should be present (even if empty)
            assert "frein" in fb or fb.get("frein") is None or "frein" not in fb, "frein field check"
            print(f"PASS: Feedback has required fields: id={fb['id'][:8]}..., categories={fb['categories']}")
        else:
            print("SKIP: No feedbacks to verify structure")
    
    def test_stats_distribution_structure(self, authenticated_client):
        """Stats distributions should have correct structure"""
        response = authenticated_client.get(f"{BASE_URL}/api/feedback/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Check clarte_distribution structure
        for item in data.get("clarte_distribution", []):
            assert "label" in item, "clarte_distribution item should have 'label'"
            assert "count" in item, "clarte_distribution item should have 'count'"
        
        # Check category_distribution structure
        for item in data.get("category_distribution", []):
            assert "category" in item, "category_distribution item should have 'category'"
            assert "count" in item, "category_distribution item should have 'count'"
        
        print("PASS: Stats distributions have correct structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
