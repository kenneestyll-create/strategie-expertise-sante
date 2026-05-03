import pytest
import uuid
import re
from starlette.testclient import TestClient

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

API = "/api"

TEST_ADMIN_EMAIL = os.environ.get("TEST_ADMIN_EMAIL", "admin@accompagn-sante.fr")
TEST_ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "Admin2024!")

# Patterns used to identify ANY pytest-generated data that may have leaked into
# the database during a test session. These are used by the session-scoped
# autouse teardown fixture to scrub the DB at the end of the run.
_PYTEST_PSEUDO_REGEX = r'^(pytest-|TestUser\d+|AnonUser\d+|anon-)'
_PYTEST_EMAIL_REGEX = r'(@test\.com$|@example\.com$|^pytest-.*@)'
_PYTEST_TITLE_MARKERS = [
    'Test pytest topic', 'Test Topic from API', 'Reply test',
    'Like test', 'Report test',
]
_PYTEST_CONTENT_MARKERS = [
    'Pytest reply', 'Content from pytest',
    'This is a test topic created during API testing',
]
_PYTEST_REPORT_REASONS = ['Spam test']


@pytest.fixture(scope="session")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(scope="session")
def admin_token(client):
    resp = client.post(f"{API}/auth/login", json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ---------------------------------------------------------------------------
# Pytest-created user fixtures: each tracks the created user/forum entity so
# that the session-scoped teardown below can remove every pytest artifact.
# ---------------------------------------------------------------------------

_created_client_emails: list[str] = []
_created_forum_user_ids: list[str] = []


@pytest.fixture
def test_client_user(client):
    email = f"pytest-{uuid.uuid4().hex[:8]}@test.com"
    resp = client.post(f"{API}/client/register", json={
        "email": email, "password": "TestPass123!", "name": "PyTest User",
        "phone": "0600000000", "notifications_email": True, "notifications_push": False
    })
    assert resp.status_code == 200
    data = resp.json()
    _created_client_emails.append(email)
    info = {"token": data["access_token"], "id": data["client_id"], "email": email, "name": "PyTest User"}
    yield info


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
    _created_forum_user_ids.append(data["user_id"])
    return {"token": data["access_token"], "user_id": data["user_id"], "pseudo": pseudo, "email": email}


@pytest.fixture
def forum_headers(forum_user):
    return {"Authorization": f"Bearer {forum_user['token']}"}


# ---------------------------------------------------------------------------
# Session-scoped autouse teardown: wipes every pytest-generated row from the
# production database at the end of the test run. This is the safety net that
# prevents the forum from being polluted with "Test Topic from API" / pytest
# fixtures seen in previous runs.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _cleanup_pytest_db_artifacts():
    """Runs ONCE at end of the test session; strips pytest leftovers."""
    yield
    try:
        import asyncio
        from motor.motor_asyncio import AsyncIOMotorClient
        from dotenv import load_dotenv
        load_dotenv('/app/backend/.env')

        async def _scrub():
            mongo_url = os.environ.get('MONGO_URL')
            db_name = os.environ.get('DB_NAME')
            if not mongo_url or not db_name:
                return
            mclient = AsyncIOMotorClient(mongo_url)
            db = mclient[db_name]

            # ---- FORUM collections ----
            users = await db.forum_users.find(
                {}, {'_id': 0, 'id': 1, 'pseudo': 1, 'email': 1}
            ).to_list(length=None)
            pytest_user_ids = set(_created_forum_user_ids)
            for u in users:
                p = u.get('pseudo') or ''
                e = u.get('email') or ''
                if re.match(_PYTEST_PSEUDO_REGEX, p) or (e and re.search(_PYTEST_EMAIL_REGEX, e)):
                    pytest_user_ids.add(u['id'])

            topic_ids = set()
            if pytest_user_ids:
                topics = await db.forum_topics.find(
                    {'author_id': {'$in': list(pytest_user_ids)}}, {'_id': 0, 'id': 1}
                ).to_list(length=None)
                topic_ids.update(t['id'] for t in topics)

                await db.forum_topics.delete_many({'author_id': {'$in': list(pytest_user_ids)}})
                await db.forum_replies.delete_many({'author_id': {'$in': list(pytest_user_ids)}})
                await db.forum_reports.delete_many({'reporter_id': {'$in': list(pytest_user_ids)}})

            await db.forum_topics.delete_many({
                '$or': [{'title': {'$regex': f'^{re.escape(m)}$'}} for m in _PYTEST_TITLE_MARKERS]
            })
            await db.forum_replies.delete_many({
                '$or': [{'content': {'$regex': f'^{re.escape(m)}$'}} for m in _PYTEST_CONTENT_MARKERS]
            })
            await db.forum_reports.delete_many({'reason': {'$in': _PYTEST_REPORT_REASONS}})

            if topic_ids:
                await db.forum_replies.delete_many({'topic_id': {'$in': list(topic_ids)}})
                await db.forum_reports.delete_many({
                    'target_type': 'topic', 'target_id': {'$in': list(topic_ids)}
                })

            if pytest_user_ids:
                await db.forum_users.delete_many({'id': {'$in': list(pytest_user_ids)}})

            # ---- CLIENT accounts created by pytest ----
            if _created_client_emails:
                # The clients collection stores registered users of the main app.
                # Only remove emails explicitly created by pytest fixtures.
                for coll_name in ('clients', 'client_users', 'users'):
                    try:
                        await db[coll_name].delete_many({'email': {'$in': _created_client_emails}})
                    except Exception:
                        pass

        asyncio.run(_scrub())
    except Exception as exc:
        # Never fail the test session because of cleanup issues.
        print(f"[conftest teardown] cleanup skipped: {exc}")
