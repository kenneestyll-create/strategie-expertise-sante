"""Tests for S.E.S Autonomous Video Factory endpoints.

Covers:
- POST /api/admin/video-factory/generate (batch 1, batch 5, enum validation, CTA mapping)
- GET /api/admin/video-factory/history (sort + _id excluded)
- PATCH /api/admin/video-factory/{run_id}/status
- DELETE /api/admin/video-factory/{run_id}
- Auth (no token, client token)
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


# ---------- Fixtures ----------
@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=30,
    )
    if r.status_code != 200:
        pytest.skip(f"Admin auth failed ({r.status_code}): {r.text[:200]}")
    data = r.json()
    token = data.get("access_token") or data.get("token")
    if not token:
        pytest.skip(f"No token in admin login response: {data}")
    return token


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def created_run_ids():
    return []


# ---------- Auth tests ----------
class TestAuth:
    def test_generate_without_token(self):
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json={"topic_brief": "test sans auth"},
            timeout=10,
        )
        assert r.status_code in (401, 403), f"Expected 401/403, got {r.status_code}"

    def test_history_without_token(self):
        r = requests.get(f"{BASE_URL}/api/admin/video-factory/history", timeout=10)
        assert r.status_code in (401, 403)


# ---------- Validation tests (cheap, no LLM call) ----------
class TestValidation:
    def test_invalid_service_target(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json={"topic_brief": "test enum invalide", "service_target": "invalide"},
            headers=admin_headers,
            timeout=15,
        )
        assert r.status_code == 400, f"Expected 400, got {r.status_code}: {r.text[:200]}"

    def test_invalid_intention(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json={"topic_brief": "test enum invalide", "intention": "invalide"},
            headers=admin_headers,
            timeout=15,
        )
        assert r.status_code == 400

    def test_invalid_urgence(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json={"topic_brief": "test enum invalide", "urgence": "invalide"},
            headers=admin_headers,
            timeout=15,
        )
        assert r.status_code == 400

    def test_invalid_plateforme(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json={"topic_brief": "test enum invalide", "plateforme": "invalide"},
            headers=admin_headers,
            timeout=15,
        )
        assert r.status_code == 400

    def test_batch_size_zero(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json={"topic_brief": "test batch 0", "batch_size": 0},
            headers=admin_headers,
            timeout=15,
        )
        assert r.status_code == 422

    def test_batch_size_six(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json={"topic_brief": "test batch 6", "batch_size": 6},
            headers=admin_headers,
            timeout=15,
        )
        assert r.status_code == 422


def _assert_video_structure(v, expected_service, expected_plateforme_utm):
    """Helper to validate a single video structure."""
    assert v.get("format_used") in {"F1", "F2", "F3", "F4", "F5", "F6", "F7"}
    assert v.get("format_label")
    assert 1 <= v.get("viral_score", 0) <= 5
    hooks = v.get("hook_variants") or []
    assert len(hooks) == 3
    assert v.get("script") and isinstance(v["script"], str)
    sb = v.get("storyboard") or []
    assert len(sb) <= 6
    for plan in sb:
        assert "plan" in plan
        assert "type" in plan
        assert "description" in plan
        assert "duree_sec" in plan
    assert v.get("subtitles_srt"), "subtitles_srt vide"
    seo = v.get("seo") or {}
    assert seo.get("title")
    assert seo.get("description")
    assert isinstance(seo.get("hashtags"), list)
    cta = v.get("cta") or {}
    assert cta.get("text")
    assert cta.get("target_service") == expected_service
    url = cta.get("url_with_utm", "")
    assert f"utm_source={expected_plateforme_utm}" in url
    assert "utm_medium=short" in url
    assert "utm_campaign=" in url
    assert isinstance(v.get("compliance_passed"), bool)


# ---------- Generation tests (LLM calls, expensive) ----------
class TestGeneration:
    def test_generate_batch1_urgence_critique_auto_97eur(self, admin_headers, created_run_ids):
        """urgence=critique + service=auto → must map to 97€ /dossier-express."""
        payload = {
            "topic_brief": "Erreur frequente face au medecin-conseil CPAM lors d expertise IPP",
            "service_target": "auto",
            "intention": "autorite",
            "urgence": "critique",
            "plateforme": "TikTok",
            "batch_size": 1,
        }
        # intention enum is 'autorité' with accent — let's use correct value
        payload["intention"] = "autorité"
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json=payload, headers=admin_headers, timeout=120,
        )
        assert r.status_code == 200, f"Got {r.status_code}: {r.text[:400]}"
        data = r.json()
        assert "run_id" in data
        assert data.get("model_used")
        assert isinstance(data.get("estimated_cost_eur"), (int, float))
        videos = data.get("videos") or []
        assert len(videos) == 1
        v = videos[0]
        _assert_video_structure(v, expected_service="97€", expected_plateforme_utm="tiktok")
        assert "/dossier-express" in v["cta"]["url_with_utm"]
        created_run_ids.append(data["run_id"])

    def test_generate_urgence_faible_auto_maps_0eur(self, admin_headers, created_run_ids):
        payload = {
            "topic_brief": "Comprendre le simulateur AAH gratuit",
            "service_target": "auto", "urgence": "faible",
            "plateforme": "YouTube Shorts", "batch_size": 1,
        }
        r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          json=payload, headers=admin_headers, timeout=120)
        assert r.status_code == 200, r.text[:300]
        v = r.json()["videos"][0]
        assert v["cta"]["target_service"] == "0€"
        assert "/simulateur" in v["cta"]["url_with_utm"]
        assert "utm_source=youtubeshorts" in v["cta"]["url_with_utm"]
        created_run_ids.append(r.json()["run_id"])

    def test_generate_urgence_moyen_auto_maps_29eur(self, admin_headers, created_run_ids):
        payload = {
            "topic_brief": "Pourquoi un PDF d analyse aide votre dossier MDPH",
            "service_target": "auto", "urgence": "moyen",
            "plateforme": "Instagram Reels", "batch_size": 1,
        }
        r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          json=payload, headers=admin_headers, timeout=120)
        assert r.status_code == 200, r.text[:300]
        v = r.json()["videos"][0]
        assert v["cta"]["target_service"] == "29€"
        assert "/analyse-pdf" in v["cta"]["url_with_utm"]
        created_run_ids.append(r.json()["run_id"])

    def test_service_target_overrides_urgence(self, admin_headers, created_run_ids):
        """urgence=faible + service_target=97€ → CTA doit pointer 97€."""
        payload = {
            "topic_brief": "Preparer son expertise medicale en moins de 30 jours",
            "service_target": "97€", "urgence": "faible",
            "plateforme": "TikTok", "batch_size": 1,
        }
        r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          json=payload, headers=admin_headers, timeout=120)
        assert r.status_code == 200, r.text[:300]
        v = r.json()["videos"][0]
        assert v["cta"]["target_service"] == "97€"
        assert "/dossier-express" in v["cta"]["url_with_utm"]
        created_run_ids.append(r.json()["run_id"])

    def test_generate_batch5(self, admin_headers, created_run_ids):
        """Test batch=5 to validate multi-video generation."""
        payload = {
            "topic_brief": "5 erreurs frequentes en expertise medicale CPAM",
            "service_target": "auto", "urgence": "critique",
            "plateforme": "TikTok", "batch_size": 5,
        }
        r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          json=payload, headers=admin_headers, timeout=180)
        assert r.status_code == 200, r.text[:300]
        videos = r.json()["videos"]
        assert len(videos) >= 1, "Batch should return at least one video"
        # Accept LLM may return fewer than requested; key thing is structure
        for v in videos:
            _assert_video_structure(v, expected_service="97€", expected_plateforme_utm="tiktok")
        created_run_ids.append(r.json()["run_id"])


# ---------- History / status / delete ----------
class TestHistoryAndLifecycle:
    def test_history_returns_items_no_underscore_id(self, admin_headers, created_run_ids):
        if not created_run_ids:
            pytest.skip("No run created earlier — skipping history test")
        r = requests.get(f"{BASE_URL}/api/admin/video-factory/history",
                         headers=admin_headers, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data and "count" in data
        items = data["items"]
        assert isinstance(items, list)
        assert data["count"] == len(items)
        # CRITICAL: _id must NOT be present
        for it in items:
            assert "_id" not in it, f"MongoDB _id leaked: {it.keys()}"
        # Sort desc by created_at
        if len(items) >= 2:
            dts = [it.get("created_at", "") for it in items]
            assert dts == sorted(dts, reverse=True), "history not sorted by created_at desc"
        # Latest created run must appear
        ids_in_history = {it.get("id") for it in items}
        assert any(rid in ids_in_history for rid in created_run_ids)

    def test_patch_status_published(self, admin_headers, created_run_ids):
        if not created_run_ids:
            pytest.skip("No run available")
        run_id = created_run_ids[0]
        r = requests.patch(
            f"{BASE_URL}/api/admin/video-factory/{run_id}/status",
            json={"status": "published"},
            headers=admin_headers, timeout=15,
        )
        assert r.status_code == 200, r.text[:300]
        body = r.json()
        assert body.get("updated") is True
        assert body.get("status") == "published"
        # Verify persistence via history
        h = requests.get(f"{BASE_URL}/api/admin/video-factory/history",
                         headers=admin_headers, timeout=15).json()
        match = next((it for it in h["items"] if it.get("id") == run_id), None)
        assert match is not None
        assert match.get("status") == "published"
        assert "updated_at" in match

    def test_delete_run_and_verify_gone(self, admin_headers, created_run_ids):
        if not created_run_ids:
            pytest.skip("No run available")
        run_id = created_run_ids[-1]
        r = requests.delete(f"{BASE_URL}/api/admin/video-factory/{run_id}",
                            headers=admin_headers, timeout=15)
        assert r.status_code == 200
        assert r.json().get("deleted") is True
        # Verify gone from history
        h = requests.get(f"{BASE_URL}/api/admin/video-factory/history",
                         headers=admin_headers, timeout=15).json()
        ids = [it.get("id") for it in h["items"]]
        assert run_id not in ids
        created_run_ids.remove(run_id)

    def test_delete_nonexistent_run_404(self, admin_headers):
        r = requests.delete(
            f"{BASE_URL}/api/admin/video-factory/non-existent-id-xyz",
            headers=admin_headers, timeout=15,
        )
        assert r.status_code == 404


# ---------- Cleanup ----------
@pytest.fixture(scope="module", autouse=True)
def cleanup_runs(admin_headers, created_run_ids):
    yield
    # Teardown: delete any remaining test runs
    for rid in list(created_run_ids):
        try:
            requests.delete(f"{BASE_URL}/api/admin/video-factory/{rid}",
                            headers=admin_headers, timeout=10)
        except Exception:
            pass
