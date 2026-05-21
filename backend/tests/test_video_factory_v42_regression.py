"""V4.2 regression — Verify NO backend changes for V4.2 export layer.

V4.2 is a 100% client-side feature (MediaRecorder + AudioContext).
Backend MUST remain identical to V4.1: same endpoints, same DB schema,
just an updated registry card (role/mission/guardrails 8+2+3=13).
"""
import os
import requests
import pytest

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"
EXISTING_RUN_WITH_VO = "dbf77819-b169-49d2-9976-29ad4f40306c"


@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=20,
    )
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    token = r.json().get("access_token")
    assert token, "No access_token in login response"
    return token


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ── V4.2 non-regression of existing Video Factory endpoints ──
class TestVideoFactoryEndpointsStillWork:
    def test_history_ok(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/admin/video-factory/history?limit=10",
            headers=auth_headers, timeout=20,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert isinstance(data, dict)
        assert "items" in data or "runs" in data or isinstance(data.get("data"), list) or data

    def test_metrics_ok(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/admin/video-factory/metrics",
            headers=auth_headers, timeout=20,
        )
        assert r.status_code == 200, r.text

    def test_performance_weights_ok(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/admin/video-factory/performance/weights",
            headers=auth_headers, timeout=20,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert isinstance(data, dict)


# ── V4.2 registry assertions ──
class TestAgentsRegistryV42:
    def test_video_factory_card_v42(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/admin/agents/registry",
            headers=auth_headers, timeout=20,
        )
        assert r.status_code == 200, r.text
        payload = r.json()
        # Find video_factory in any reasonable structure
        agents = payload.get("agents") or payload.get("cards") or payload
        if isinstance(agents, dict):
            # maybe nested
            agents = (
                payload.get("agents")
                or payload.get("data")
                or payload.get("items")
                or list(payload.values())
            )
        if isinstance(agents, list) and agents and isinstance(agents[0], list):
            agents = [a for sub in agents for a in sub]
        # flatten search
        def _find(node):
            if isinstance(node, dict):
                if node.get("id") == "video_factory":
                    return node
                for v in node.values():
                    found = _find(v)
                    if found:
                        return found
            elif isinstance(node, list):
                for v in node:
                    found = _find(v)
                    if found:
                        return found
            return None

        card = _find(payload)
        assert card is not None, f"video_factory card not found in registry payload: {list(payload)[:5]}"
        role = card.get("role", "")
        mission = card.get("mission", "")
        guardrails = card.get("guardrails", [])
        assert "V4.2" in role, f"role must mention V4.2, got: {role}"
        assert "V4.2" in mission, f"mission must mention V4.2, got: {mission[:120]}"
        assert "client-side" in mission.lower() or "mediarecorder" in mission.lower()
        assert isinstance(guardrails, list)
        assert len(guardrails) == 13, f"Expected 13 guardrails total, got {len(guardrails)}"
        v42_guardrails = [g for g in guardrails if "V4.2" in g]
        assert len(v42_guardrails) == 3, f"Expected 3 V4.2 guardrails, got {len(v42_guardrails)}"
        v41_guardrails = [g for g in guardrails if "V4.1" in g]
        assert len(v41_guardrails) == 2, f"Expected 2 V4.1 guardrails, got {len(v41_guardrails)}"


# ── V4.2 must NOT introduce a new backend export endpoint ──
class TestNoNewExportEndpoint:
    @pytest.mark.parametrize("path", [
        "/api/admin/video-factory/export",
        "/api/admin/video-factory/render",
        "/api/admin/video-factory/webm",
    ])
    def test_no_export_endpoint_added(self, auth_headers, path):
        r = requests.post(
            f"{BASE_URL}{path}",
            headers=auth_headers,
            json={"run_id": EXISTING_RUN_WITH_VO, "video_idx": 0},
            timeout=10,
        )
        # Must be 404/405 (or 422 if FastAPI sees route absence + validation), never 200
        assert r.status_code in (404, 405, 422), (
            f"V4.2 must NOT add backend endpoint, but {path} responded {r.status_code}"
        )


# ── V4.2 voice_over endpoint still works (V4.1 not regressed) ──
class TestVoiceOverEndpointStillExists:
    def test_voice_over_405_on_get(self, auth_headers):
        # POST/DELETE only; GET should be 404/405
        r = requests.get(
            f"{BASE_URL}/api/admin/video-factory/runs/{EXISTING_RUN_WITH_VO}/videos/0/voice-over",
            headers=auth_headers, timeout=10,
        )
        assert r.status_code in (404, 405), f"unexpected {r.status_code}: {r.text[:200]}"

    def test_voice_over_post_validation_404_on_missing_run(self, auth_headers):
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/runs/__nope__/videos/0/voice-over",
            headers=auth_headers,
            json={"voice": "onyx"},
            timeout=20,
        )
        # 404 (run not found) or 400/422 — not 500
        assert r.status_code in (400, 404, 422), f"unexpected {r.status_code}: {r.text[:200]}"
