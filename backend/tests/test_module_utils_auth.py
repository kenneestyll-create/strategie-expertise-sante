"""Tests for utils/auth.py — password hashing, token creation, auth dependencies."""
import pytest
import jwt
from datetime import datetime, timezone
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import (
    hash_password, verify_password,
    create_token, create_forum_token, create_client_token,
)
from config import JWT_SECRET, JWT_ALGORITHM


class TestPasswordHashing:
    def test_hash_and_verify(self):
        pw = "MySecure123!"
        h = hash_password(pw)
        assert h != pw
        assert verify_password(pw, h)

    def test_wrong_password_fails(self):
        h = hash_password("correct")
        assert not verify_password("wrong", h)

    def test_different_hashes(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # bcrypt uses random salt

    def test_empty_password(self):
        h = hash_password("")
        assert verify_password("", h)


class TestTokenCreation:
    def test_admin_token(self):
        token = create_token("admin-1", "admin@test.com", is_admin=True)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["sub"] == "admin-1"
        assert payload["email"] == "admin@test.com"
        assert payload["is_admin"] is True
        assert "exp" in payload

    def test_non_admin_token(self):
        token = create_token("user-1", "user@test.com", is_admin=False)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["is_admin"] is False

    def test_forum_token(self):
        token = create_forum_token("forum-1", "TestPseudo", False)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["sub"] == "forum-1"
        assert payload["pseudo"] == "TestPseudo"
        assert payload["is_forum_user"] is True
        assert payload["is_anonymous"] is False

    def test_forum_token_anonymous(self):
        token = create_forum_token("forum-2", "Anon", True)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["is_anonymous"] is True

    def test_client_token(self):
        token = create_client_token("client-1", "client@test.com", "Jean")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["sub"] == "client-1"
        assert payload["email"] == "client@test.com"
        assert payload["name"] == "Jean"
        assert payload["is_client"] is True

    def test_token_has_expiry(self):
        token = create_token("u1", "e@t.com")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert exp > datetime.now(timezone.utc)
