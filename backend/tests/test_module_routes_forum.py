"""Tests for routes/forum.py — forum CRUD + admin forum."""
import pytest
import uuid

API = "/api"


class TestForumCategories:
    def test_list_categories(self, client):
        resp = client.get(f"{API}/forum/categories")
        assert resp.status_code == 200
        cats = resp.json()
        assert len(cats) == 6
        slugs = {c["slug"] for c in cats}
        assert "accident-travail" in slugs
        assert "mdph" in slugs

    def test_category_fields(self, client):
        resp = client.get(f"{API}/forum/categories")
        cat = resp.json()[0]
        for field in ("id", "name", "slug", "description", "icon", "order"):
            assert field in cat


class TestForumAuth:
    def test_register(self, client):
        pseudo = f"pytest-{uuid.uuid4().hex[:6]}"
        resp = client.post(f"{API}/forum/register", json={
            "pseudo": pseudo, "email": f"{pseudo}@test.com",
            "password": "TestPass!", "is_anonymous": False
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["pseudo"] == pseudo
        assert "access_token" in data

    def test_register_anonymous(self, client):
        pseudo = f"anon-{uuid.uuid4().hex[:6]}"
        resp = client.post(f"{API}/forum/register", json={
            "pseudo": pseudo, "is_anonymous": True
        })
        assert resp.status_code == 200
        assert resp.json()["is_anonymous"] is True

    def test_duplicate_pseudo(self, client, forum_user):
        resp = client.post(f"{API}/forum/register", json={
            "pseudo": forum_user["pseudo"], "email": "dup@test.com",
            "password": "Pass!", "is_anonymous": False
        })
        assert resp.status_code == 400

    def test_login(self, client, forum_user):
        resp = client.post(f"{API}/forum/login", json={
            "email": forum_user["email"], "password": "ForumPass123!"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client, forum_user):
        resp = client.post(f"{API}/forum/login", json={
            "email": forum_user["email"], "password": "Wrong!"
        })
        assert resp.status_code == 401


class TestForumTopics:
    def test_list_topics(self, client):
        resp = client.get(f"{API}/forum/topics")
        assert resp.status_code == 200
        data = resp.json()
        assert "topics" in data
        assert "total" in data

    def test_create_and_get_topic(self, client, forum_headers):
        resp = client.post(f"{API}/forum/topics", json={
            "category_id": "accident-travail", "title": "Test pytest topic",
            "content": "Content from pytest"
        }, headers=forum_headers)
        assert resp.status_code == 200
        topic_id = resp.json()["topic_id"]

        resp2 = client.get(f"{API}/forum/topics/{topic_id}")
        assert resp2.status_code == 200
        assert resp2.json()["topic"]["title"] == "Test pytest topic"

    def test_create_topic_invalid_category(self, client, forum_headers):
        resp = client.post(f"{API}/forum/topics", json={
            "category_id": "nonexistent", "title": "Bad", "content": "X"
        }, headers=forum_headers)
        assert resp.status_code == 400

    def test_create_topic_unauthorized(self, client):
        resp = client.post(f"{API}/forum/topics", json={
            "category_id": "mdph", "title": "X", "content": "Y"
        })
        assert resp.status_code == 403


class TestForumReplies:
    def test_reply_to_topic(self, client, forum_headers):
        resp = client.post(f"{API}/forum/topics", json={
            "category_id": "mdph", "title": "Reply test", "content": "Topic"
        }, headers=forum_headers)
        topic_id = resp.json()["topic_id"]

        resp2 = client.post(f"{API}/forum/topics/{topic_id}/replies", json={
            "content": "Pytest reply"
        }, headers=forum_headers)
        assert resp2.status_code == 200
        assert "reply_id" in resp2.json()


class TestForumLikes:
    def test_like_topic_toggle(self, client, forum_headers):
        resp = client.post(f"{API}/forum/topics", json={
            "category_id": "invalidite", "title": "Like test", "content": "X"
        }, headers=forum_headers)
        topic_id = resp.json()["topic_id"]

        resp2 = client.post(f"{API}/forum/topics/{topic_id}/like", headers=forum_headers)
        assert resp2.status_code == 200
        assert resp2.json()["liked"] is True

        resp3 = client.post(f"{API}/forum/topics/{topic_id}/like", headers=forum_headers)
        assert resp3.json()["liked"] is False


class TestForumReport:
    def test_report_content(self, client, forum_headers):
        resp = client.post(f"{API}/forum/topics", json={
            "category_id": "mdph", "title": "Report test", "content": "X"
        }, headers=forum_headers)
        topic_id = resp.json()["topic_id"]

        resp2 = client.post(f"{API}/forum/report", json={
            "target_type": "topic", "target_id": topic_id, "reason": "Spam test"
        }, headers=forum_headers)
        assert resp2.status_code == 200


class TestForumAdmin:
    def test_forum_stats(self, client, admin_headers):
        resp = client.get(f"{API}/admin/forum/stats", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        for key in ("total_users", "total_topics", "total_replies", "pending_reports"):
            assert key in data

    def test_forum_users_list(self, client, admin_headers):
        resp = client.get(f"{API}/admin/forum/users", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_forum_reports(self, client, admin_headers):
        resp = client.get(f"{API}/admin/forum/reports", headers=admin_headers)
        assert resp.status_code == 200
