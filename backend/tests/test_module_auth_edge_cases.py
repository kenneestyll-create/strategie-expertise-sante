"""Tests to boost coverage of utils/auth.py — auth dependency edge cases."""
import pytest
import jwt
from datetime import datetime, timezone, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import JWT_SECRET, JWT_ALGORITHM

API = "/api"


class TestAuthDependencyEdgeCases:
    """Test all auth dependency rejection paths."""

    def test_admin_with_forum_token(self, client, forum_user):
        """A forum token should NOT grant admin access."""
        headers = {"Authorization": f"Bearer {forum_user['token']}"}
        resp = client.get(f"{API}/admin/stats", headers=headers)
        assert resp.status_code == 401

    def test_client_with_admin_token(self, client, admin_headers):
        """An admin token should NOT grant client access."""
        resp = client.get(f"{API}/client/profile", headers=admin_headers)
        assert resp.status_code == 401

    def test_forum_with_admin_token(self, client, admin_headers):
        """An admin token should NOT grant forum access."""
        resp = client.post(f"{API}/forum/topics", json={
            "category_id": "mdph", "title": "X", "content": "Y"
        }, headers=admin_headers)
        assert resp.status_code == 401

    def test_expired_token(self, client):
        """An expired token should return 401."""
        expired_payload = {
            "sub": "test-id", "email": "test@test.com", "is_admin": True,
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)
        }
        expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        resp = client.get(f"{API}/admin/stats", headers={"Authorization": f"Bearer {expired_token}"})
        assert resp.status_code == 401

    def test_malformed_token(self, client):
        """Garbage token should return 401."""
        resp = client.get(f"{API}/admin/stats", headers={"Authorization": "Bearer not.a.jwt"})
        assert resp.status_code == 401

    def test_wrong_secret_token(self, client):
        """Token signed with wrong secret should return 401."""
        payload = {"sub": "test", "email": "t@t.com", "is_admin": True,
                   "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
        token = jwt.encode(payload, "wrong-secret-key", algorithm=JWT_ALGORITHM)
        resp = client.get(f"{API}/admin/stats", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401

    def test_client_token_for_forum(self, client, test_client_user):
        """Client token should not access forum-protected routes."""
        headers = {"Authorization": f"Bearer {test_client_user['token']}"}
        resp = client.post(f"{API}/forum/topics", json={
            "category_id": "mdph", "title": "X", "content": "Y"
        }, headers=headers)
        assert resp.status_code == 401

    def test_optional_forum_user_no_token(self, client):
        """Endpoints with optional auth should work without token."""
        resp = client.get(f"{API}/forum/topics")
        assert resp.status_code == 200

    def test_banned_forum_user(self, client, admin_headers, forum_user):
        """Banned forum user should get 403."""
        # Ban the user
        resp = client.post(f"{API}/admin/forum/users/{forum_user['user_id']}/ban",
                          headers=admin_headers, params={"reason": "Test ban"})
        assert resp.status_code == 200

        # Try to access with banned token
        headers = {"Authorization": f"Bearer {forum_user['token']}"}
        resp = client.post(f"{API}/forum/topics", json={
            "category_id": "mdph", "title": "X", "content": "Y"
        }, headers=headers)
        assert resp.status_code == 403

        # Unban
        client.post(f"{API}/admin/forum/users/{forum_user['user_id']}/unban", headers=admin_headers)
