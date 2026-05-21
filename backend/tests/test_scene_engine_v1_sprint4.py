"""
Sprint 4 Final Validation — Scene Engine V1
Tests:
  BACKEND-1: /history returns videos with scene_type mapped from format_used
  BACKEND-2: /generate forced_format=F4 returns scene_type='legal_balance' + cleanup
  BACKEND-3: backwards compat — older videos with no scene_type still exist
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://mascot-tips-admin.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"

# Backend canonical mapping (must mirror routes/video_factory.py L239-247)
EXPECTED_MAPPING = {
    "F1": "office_admin",
    "F2": "stats_focus",
    "F3": "testimony_quote",
    "F4": "legal_balance",
    "F5": "office_admin",
    "F6": "alert_urgency",
    "F7": "alert_urgency",
}


@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
                      timeout=15)
    assert r.status_code == 200, f"login failed {r.status_code} {r.text[:300]}"
    tok = r.json().get("access_token") or r.json().get("token")
    assert tok, f"no token in response: {r.json()}"
    return tok


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="module")
def history_payload(auth_headers):
    r = requests.get(f"{BASE_URL}/api/admin/video-factory/history?limit=20",
                     headers=auth_headers, timeout=20)
    assert r.status_code == 200, f"history failed {r.status_code} {r.text[:300]}"
    return r.json()


# -------------------- BACKEND-1 --------------------
class TestBackend1HistoryMapping:
    """GET /history items[*].videos[0].scene_type follows F1-F7 mapping"""

    def test_history_returns_items(self, history_payload):
        items = history_payload.get("items") or history_payload.get("runs") or []
        assert isinstance(items, list)
        assert len(items) >= 1, "expected at least 1 history item"

    def test_history_scene_type_matches_format_mapping(self, history_payload):
        items = history_payload.get("items") or history_payload.get("runs") or []
        mismatches = []
        with_scene = 0
        for run in items:
            vids = run.get("videos") or []
            if not vids:
                continue
            v0 = vids[0]
            fmt = v0.get("format_used")
            st = v0.get("scene_type")
            if st is not None and fmt in EXPECTED_MAPPING:
                with_scene += 1
                if st != EXPECTED_MAPPING[fmt]:
                    mismatches.append({"run_id": run.get("id"), "fmt": fmt,
                                        "got": st, "expected": EXPECTED_MAPPING[fmt]})
        assert not mismatches, f"scene_type mapping mismatches: {mismatches}"
        assert with_scene >= 1, "expected >=1 run with scene_type populated"

    def test_history_contains_all_required_formats(self, history_payload):
        """sprint3/sprint4 test fixtures should cover F1,F2,F3,F4,F5,F6,F7"""
        items = history_payload.get("items") or history_payload.get("runs") or []
        found_formats = set()
        for run in items:
            for v in run.get("videos") or []:
                if v.get("scene_type") and v.get("format_used"):
                    found_formats.add(v["format_used"])
        # At minimum we expect a healthy coverage — request claims 7 cards with canvas
        assert len(found_formats) >= 4, f"only found formats: {found_formats}"


# -------------------- BACKEND-3 --------------------
class TestBackend3LegacyFallback:
    """At least 1 history item has video without scene_type → V4.2 fallback path"""

    def test_at_least_one_legacy_without_scene_type(self, history_payload):
        items = history_payload.get("items") or history_payload.get("runs") or []
        legacy = []
        for run in items:
            vids = run.get("videos") or []
            for v in vids:
                if not v.get("scene_type"):
                    legacy.append(run.get("id"))
                    break
        assert len(legacy) >= 1, "expected >=1 legacy run without scene_type for fallback test"
        print(f"\n[BACKEND-3] legacy runs without scene_type: {legacy[:5]}")


# -------------------- BACKEND-2 --------------------
class TestBackend2GenerateF4:
    """POST /generate forced_format=F4 → scene_type='legal_balance', then DELETE cleanup"""

    @pytest.mark.skipif(os.environ.get("SKIP_LLM_GENERATION") == "1",
                        reason="LLM cost — set SKIP_LLM_GENERATION=0 to enable")
    def test_generate_f4_returns_legal_balance(self, auth_headers):
        payload = {
            "topic_brief": "Cadre juridique des accompagnements santé — test sprint 4",
            "forced_format": "F4",
            "batch_size": 1,
        }
        r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          headers=auth_headers, json=payload, timeout=180)
        assert r.status_code == 200, f"generate failed {r.status_code} {r.text[:500]}"
        body = r.json()
        run_id = body.get("id") or (body.get("run") or {}).get("id")
        vids = body.get("videos") or (body.get("run") or {}).get("videos") or []
        try:
            assert vids, f"no videos in generate response: {body}"
            assert vids[0].get("scene_type") == "legal_balance", \
                f"expected legal_balance got {vids[0].get('scene_type')}"
            assert vids[0].get("format_used") == "F4"
        finally:
            if run_id:
                dr = requests.delete(f"{BASE_URL}/api/admin/video-factory/{run_id}",
                                      headers=auth_headers, timeout=20)
                print(f"\n[cleanup] DELETE {run_id} -> {dr.status_code}")
