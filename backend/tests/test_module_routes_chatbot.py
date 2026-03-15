"""Tests for routes/chatbot.py — chatbot endpoint."""
import pytest
import uuid

API = "/api"


class TestChatbot:
    def test_faq_response(self, client):
        sid = f"pytest-faq-{uuid.uuid4().hex[:8]}"
        resp = client.post(f"{API}/chatbot", json={
            "message": "Comment se préparer à une expertise médicale ?",
            "session_id": sid
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_faq"] is True
        assert len(data["response"]) > 50
        assert data["session_id"] == sid

    def test_ai_response_fallback(self, client):
        sid = f"pytest-ai-{uuid.uuid4().hex[:8]}"
        resp = client.post(f"{API}/chatbot", json={
            "message": "Bonjour, je cherche une recette de cuisine",
            "session_id": sid
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["response"]) > 10

    def test_auto_session_id(self, client):
        resp = client.post(f"{API}/chatbot", json={"message": "Test"})
        assert resp.status_code == 200
        assert len(resp.json()["session_id"]) > 10

    def test_quota(self, client):
        resp = client.get(f"{API}/chatbot/quota/pytest-quota-session")
        assert resp.status_code == 200
        data = resp.json()
        assert data["limit"] == 5
        assert "remaining" in data
        assert "used" in data
