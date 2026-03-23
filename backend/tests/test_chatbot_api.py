"""
Test suite for Chatbot API endpoints
Tests: POST /api/chatbot, GET /api/chatbot/quota/{session_id}
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestChatbotAPI:
    """Chatbot endpoint tests"""
    
    def test_chatbot_faq_response(self):
        """Test chatbot returns FAQ response for known keywords"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "Comment preparer une expertise medicale ?",
            "session_id": None
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "response" in data
        assert "is_faq" in data
        assert "session_id" in data
        
        # Verify FAQ was matched
        assert data["is_faq"] == True
        assert "expertise" in data["response"].lower() or "médical" in data["response"].lower()
        assert len(data["session_id"]) > 0
        print(f"FAQ response received, session_id: {data['session_id']}")
    
    def test_chatbot_ai_response(self):
        """Test chatbot returns AI response for non-FAQ questions"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "Bonjour, comment fonctionne votre service ?",
            "session_id": None
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "response" in data
        assert "is_faq" in data
        assert "session_id" in data
        
        # This should NOT be a FAQ response
        assert data["is_faq"] == False
        assert len(data["response"]) > 50  # AI response should be substantial
        print(f"AI response received, length: {len(data['response'])} chars")
    
    def test_chatbot_session_persistence(self):
        """Test chatbot maintains session across requests"""
        # First request - get session_id
        response1 = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "Qu'est-ce que la MDPH ?",
            "session_id": None
        })
        
        assert response1.status_code == 200
        data1 = response1.json()
        session_id = data1["session_id"]
        
        # Second request - use same session_id
        response2 = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "Et pour les tarifs ?",
            "session_id": session_id
        })
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Session should be maintained
        assert data2["session_id"] == session_id
        print(f"Session maintained: {session_id}")
    
    def test_chatbot_quota_endpoint(self):
        """Test quota endpoint returns correct structure"""
        # Create a session first
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "Test question",
            "session_id": None
        })
        
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        
        # Check quota
        quota_response = requests.get(f"{BASE_URL}/api/chatbot/quota/{session_id}")
        
        assert quota_response.status_code == 200
        quota_data = quota_response.json()
        
        # Verify quota structure
        assert "remaining" in quota_data
        assert "limit" in quota_data
        assert "used" in quota_data
        assert quota_data["limit"] == 5
        assert quota_data["used"] >= 1
        assert quota_data["remaining"] == 5 - quota_data["used"]
        print(f"Quota: {quota_data['remaining']}/{quota_data['limit']} remaining")
    
    def test_chatbot_quota_nonexistent_session(self):
        """Test quota endpoint for non-existent session"""
        fake_session = str(uuid.uuid4())
        
        quota_response = requests.get(f"{BASE_URL}/api/chatbot/quota/{fake_session}")
        
        assert quota_response.status_code == 200
        quota_data = quota_response.json()
        
        # New session should have full quota
        assert quota_data["remaining"] == 5
        assert quota_data["used"] == 0
        print("Non-existent session returns full quota")
    
    def test_chatbot_mdph_faq(self):
        """Test MDPH FAQ keyword matching"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "Comment faire un dossier MDPH ?",
            "session_id": None
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_faq"] == True
        assert "mdph" in data["response"].lower() or "handicap" in data["response"].lower()
        print("MDPH FAQ matched correctly")
    
    def test_chatbot_tarifs_faq(self):
        """Test tarifs FAQ keyword matching"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "Quels sont vos tarifs ?",
            "session_id": None
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_faq"] == True
        assert "tarif" in data["response"].lower() or "€" in data["response"]
        print("Tarifs FAQ matched correctly")
    
    def test_chatbot_accident_travail_faq(self):
        """Test accident du travail FAQ keyword matching"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "Quels sont mes droits apres un accident du travail ?",
            "session_id": None
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_faq"] == True
        assert "accident" in data["response"].lower() or "travail" in data["response"].lower()
        print("Accident du travail FAQ matched correctly")
    
    def test_chatbot_empty_message(self):
        """Test chatbot handles empty message gracefully"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "",
            "session_id": None
        })
        
        # Should either return 422 (validation error) or handle gracefully
        assert response.status_code in [200, 422]
        print(f"Empty message handled with status: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
