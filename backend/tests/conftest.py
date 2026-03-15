import pytest
import uuid
from starlette.testclient import TestClient

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

API = "/api"


@pytest.fixture(scope="session")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(scope="session")
def admin_token(client):
    resp = client.post(f"{API}/auth/login", json={"email": "admin@accompagn-sante.fr", "password": "Admin2024!"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def test_client_user(client):
    email = f"pytest-{uuid.uuid4().hex[:8]}@test.com"
    resp = client.post(f"{API}/client/register", json={
        "email": email, "password": "TestPass123!", "name": "PyTest User",
        "phone": "0600000000", "notifications_email": True, "notifications_push": False
    })
    assert resp.status_code == 200
    data = resp.json()
    info = {"token": data["access_token"], "id": data["client_id"], "email": email, "name": "PyTest User"}
    yield info
    # Cleanup via API-level delete (if exists) or leave for manual cleanup


@pytest.fixture
def client_headers(test_client_user):
    return {"Authorization": f"Bearer {test_client_user['token']}"}


@pytest.fixture
def forum_user(client):
    pseudo = f"pytest-{uuid.uuid4().hex[:6]}"
    email = f"{pseudo}@test.com"
    resp = client.post(f"{API}/forum/register", json={
        "pseudo": pseudo, "email": email, "password": "ForumPass123!", "is_anonymous": False
    })
    assert resp.status_code == 200
    data = resp.json()
    return {"token": data["access_token"], "user_id": data["user_id"], "pseudo": pseudo, "email": email}


@pytest.fixture
def forum_headers(forum_user):
    return {"Authorization": f"Bearer {forum_user['token']}"}
