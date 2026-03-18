"""
Test cases for StrategiIA and Chatbot quota/rate limiting features.
Tests the new quota enforcement for:
- StrategiIA: 3 free analyses per month per email
- Chatbot: 5 free questions per session
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://non-blocking-ocr.preview.emergentagent.com').rstrip('/')


class TestStrategiIAQuota:
    """Test StrategiIA quota endpoints (3 analyses/month per email)"""

    def test_strategiia_quota_new_email_returns_3_remaining(self):
        """GET /api/strategiia/quota/{email} for new user should return 3/3/0"""
        test_email = f"test_quota_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.get(f"{BASE_URL}/api/strategiia/quota/{test_email}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "remaining" in data, "Response should have 'remaining' field"
        assert "limit" in data, "Response should have 'limit' field"
        assert "used" in data, "Response should have 'used' field"
        
        # Validate values for new email
        assert data["remaining"] == 3, f"New email should have 3 remaining, got {data['remaining']}"
        assert data["limit"] == 3, f"Limit should be 3, got {data['limit']}"
        assert data["used"] == 0, f"Used should be 0 for new email, got {data['used']}"
        print(f"✅ StrategiIA quota for new email: {data}")

    def test_strategiia_analyze_requires_email(self):
        """POST /api/strategiia/analyze without email should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/analyze",
            json={
                "type_dossier": "at",
                "regime": "general",
                "situation": "Test situation description"
                # No email field
            }
        )
        
        assert response.status_code == 400, f"Expected 400 without email, got {response.status_code}"
        data = response.json()
        assert "email" in data.get("detail", "").lower() or "obligatoire" in data.get("detail", "").lower(), \
            f"Error should mention email is required: {data}"
        print(f"✅ StrategiIA analyze requires email - error: {data}")

    def test_strategiia_analyze_with_email_field(self):
        """POST /api/strategiia/analyze with email should proceed (may fail due to LLM budget but validates email check)"""
        test_email = f"test_analyze_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(
            f"{BASE_URL}/api/strategiia/analyze",
            json={
                "type_dossier": "at",
                "regime": "general",
                "situation": "Test situation for quota validation",
                "email": test_email,
                "premium": False
            }
        )
        
        # May return 500 due to LLM budget exceeded, but should not return 400 for email
        assert response.status_code != 400, f"Should not fail email validation: {response.text}"
        print(f"✅ StrategiIA analyze with email accepted (status: {response.status_code})")


class TestChatbotQuota:
    """Test Chatbot quota endpoints (5 questions per session)"""

    def test_chatbot_quota_new_session_returns_5_remaining(self):
        """GET /api/chatbot/quota/{session_id} for new session should return 5/5/0"""
        test_session = f"test_session_{uuid.uuid4().hex[:8]}"
        response = requests.get(f"{BASE_URL}/api/chatbot/quota/{test_session}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "remaining" in data, "Response should have 'remaining' field"
        assert "limit" in data, "Response should have 'limit' field"
        assert "used" in data, "Response should have 'used' field"
        
        # Validate values for new session
        assert data["remaining"] == 5, f"New session should have 5 remaining, got {data['remaining']}"
        assert data["limit"] == 5, f"Limit should be 5, got {data['limit']}"
        assert data["used"] == 0, f"Used should be 0 for new session, got {data['used']}"
        print(f"✅ Chatbot quota for new session: {data}")

    def test_chatbot_message_returns_session_id(self):
        """POST /api/chatbot should return session_id in response"""
        response = requests.post(
            f"{BASE_URL}/api/chatbot",
            json={"message": "Bonjour, test question 1"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "session_id" in data, "Response should have 'session_id' field"
        assert "response" in data, "Response should have 'response' field"
        assert "is_faq" in data, "Response should have 'is_faq' field"
        print(f"✅ Chatbot message returns session_id: {data['session_id'][:20]}...")

    def test_chatbot_6th_message_blocked(self):
        """POST /api/chatbot 6th message in same session should return 'limite' text"""
        # Create a new session
        session_id = None
        
        # Send 5 messages to use up quota
        for i in range(5):
            response = requests.post(
                f"{BASE_URL}/api/chatbot",
                json={"message": f"Test question {i+1}", "session_id": session_id}
            )
            assert response.status_code == 200, f"Message {i+1} failed: {response.text}"
            data = response.json()
            session_id = data.get("session_id")
            print(f"  Message {i+1}/5 sent, session: {session_id[:20]}...")
        
        # Send 6th message - should be blocked
        response = requests.post(
            f"{BASE_URL}/api/chatbot",
            json={"message": "This should be blocked", "session_id": session_id}
        )
        
        assert response.status_code == 200, f"Expected 200 with limit message, got {response.status_code}"
        data = response.json()
        response_text = data.get("response", "").lower()
        
        # Should contain "limite" or redirect message
        assert "limite" in response_text or "5 questions" in response_text, \
            f"6th message should indicate limit reached: {data['response'][:100]}"
        print(f"✅ Chatbot 6th message blocked with limit message")

    def test_chatbot_quota_after_messages(self):
        """Verify quota decreases after sending messages"""
        test_session = f"test_session_quota_{uuid.uuid4().hex[:8]}"
        
        # Check initial quota
        quota_response = requests.get(f"{BASE_URL}/api/chatbot/quota/{test_session}")
        initial_quota = quota_response.json()
        assert initial_quota["remaining"] == 5, f"Initial should be 5, got {initial_quota}"
        
        # Send 2 messages
        for i in range(2):
            requests.post(
                f"{BASE_URL}/api/chatbot",
                json={"message": f"Test {i+1}", "session_id": test_session}
            )
        
        # Check quota again
        quota_response = requests.get(f"{BASE_URL}/api/chatbot/quota/{test_session}")
        updated_quota = quota_response.json()
        
        assert updated_quota["remaining"] == 3, f"After 2 messages should have 3 remaining, got {updated_quota}"
        assert updated_quota["used"] == 2, f"Should show 2 used, got {updated_quota}"
        print(f"✅ Chatbot quota tracking works: initial=5, after 2 messages={updated_quota['remaining']}")


class TestHealthEndpoint:
    """Basic health check to verify API is running"""

    def test_health_endpoint(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Expected healthy status: {data}"
        print(f"✅ Health endpoint OK: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
