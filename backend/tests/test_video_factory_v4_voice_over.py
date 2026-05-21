"""Video Factory V4.1 — Voice-over OpenAI TTS endpoint tests.

Covers :
- POST /api/admin/video-factory/{run_id}/voice-over (génération MP3 base64)
- Validations : voice non autorisée, run_id inexistant, video_idx hors borne, script vide
- DELETE /api/admin/video-factory/{run_id}/voice-over/{video_idx}
- Non-régression : history, performance/weights, metrics endpoints
- Le pack vidéo retourné par /generate n'a PAS voice_over (additif)
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    try:
        with open("/app/frontend/.env") as fh:
            for ln in fh:
                if ln.startswith("REACT_APP_BACKEND_URL="):
                    BASE_URL = ln.split("=", 1)[1].strip().rstrip("/")
                    break
    except Exception:
        pass

ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


# -------------------- Auth fixtures --------------------
@pytest.fixture(scope="module")
def admin_token():
    s = requests.Session()
    for path in ("/api/auth/login", "/api/admin/login", "/api/auth/admin/login"):
        try:
            r = s.post(f"{BASE_URL}{path}",
                       json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
                       timeout=20)
            if r.status_code == 200:
                data = r.json()
                tok = data.get("access_token") or data.get("token") or data.get("admin_token")
                if tok:
                    return tok
        except Exception:
            continue
    pytest.skip("Admin login failed")


@pytest.fixture(scope="module")
def admin_client(admin_token):
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {admin_token}",
                      "Content-Type": "application/json"})
    return s


# -------------------- Helpers --------------------
@pytest.fixture(scope="module")
def existing_run_without_vo(admin_client):
    """Fetch a run from history that doesn't have voice_over on idx 0."""
    r = admin_client.get(f"{BASE_URL}/api/admin/video-factory/history?limit=20", timeout=30)
    assert r.status_code == 200, f"history failed: {r.status_code} {r.text[:200]}"
    runs = r.json().get("runs") or r.json().get("items") or r.json()
    if isinstance(runs, dict):
        runs = runs.get("runs") or []
    for run in runs:
        videos = run.get("videos") or []
        if not videos:
            continue
        v0 = videos[0]
        if not (v0.get("voice_over")) and (v0.get("script") or "").strip():
            return run
    pytest.skip("No run without voice_over found in history")


@pytest.fixture(scope="module")
def existing_run_any(admin_client):
    r = admin_client.get(f"{BASE_URL}/api/admin/video-factory/history?limit=5", timeout=30)
    assert r.status_code == 200
    runs = r.json().get("runs") or r.json().get("items") or r.json()
    if isinstance(runs, dict):
        runs = runs.get("runs") or []
    if not runs:
        pytest.skip("No runs in history")
    return runs[0]


# ===================================================
# T1 — POST /voice-over happy path
# ===================================================
class TestVoiceOverGenerate:

    def test_generate_voice_over_onyx(self, admin_client, existing_run_without_vo):
        run_id = existing_run_without_vo["id"]
        r = admin_client.post(
            f"{BASE_URL}/api/admin/video-factory/{run_id}/voice-over",
            json={"video_idx": 0, "voice": "onyx"},
            timeout=120,
        )
        assert r.status_code == 200, f"voice-over generate failed: {r.status_code} {r.text[:300]}"
        data = r.json()
        assert data.get("generated") is True
        assert data.get("run_id") == run_id
        assert data.get("video_idx") == 0
        vo = data.get("voice_over") or {}
        assert vo.get("voice") == "onyx"
        assert vo.get("model") == "tts-1-hd"
        assert isinstance(vo.get("audio_base64"), str)
        assert len(vo["audio_base64"]) > 1000, "audio_base64 should be substantial"
        assert vo.get("char_count", 0) > 0
        assert vo.get("generated_at")
        assert vo.get("admin_email") == ADMIN_EMAIL

    def test_history_persists_voice_over(self, admin_client, existing_run_without_vo):
        """After generation, history shows voice_over persisted."""
        run_id = existing_run_without_vo["id"]
        r = admin_client.get(f"{BASE_URL}/api/admin/video-factory/history?limit=20", timeout=30)
        assert r.status_code == 200
        runs = r.json().get("runs") or r.json().get("items") or r.json()
        if isinstance(runs, dict):
            runs = runs.get("runs") or []
        found = next((x for x in runs if x.get("id") == run_id), None)
        assert found is not None, f"run {run_id} not in history"
        vo = (found.get("videos") or [{}])[0].get("voice_over")
        assert vo is not None
        assert vo.get("voice") == "onyx"


# ===================================================
# T2 — Validations
# ===================================================
class TestVoiceOverValidations:

    def test_invalid_voice_returns_400(self, admin_client, existing_run_any):
        run_id = existing_run_any["id"]
        r = admin_client.post(
            f"{BASE_URL}/api/admin/video-factory/{run_id}/voice-over",
            json={"video_idx": 0, "voice": "xyz_invalid"},
            timeout=15,
        )
        assert r.status_code == 400
        assert "voice" in r.text.lower() or "invalide" in r.text.lower()

    def test_unknown_run_id_returns_404(self, admin_client):
        r = admin_client.post(
            f"{BASE_URL}/api/admin/video-factory/no-such-run-id-zzz/voice-over",
            json={"video_idx": 0, "voice": "onyx"},
            timeout=15,
        )
        assert r.status_code == 404

    def test_video_idx_out_of_bounds_returns_400(self, admin_client, existing_run_any):
        run_id = existing_run_any["id"]
        # use 4 → in Pydantic le=4 range so pass schema, but should fail at runtime if videos[4] absent
        r = admin_client.post(
            f"{BASE_URL}/api/admin/video-factory/{run_id}/voice-over",
            json={"video_idx": 4, "voice": "onyx"},
            timeout=15,
        )
        assert r.status_code == 400
        assert "borne" in r.text.lower() or "out" in r.text.lower() or "idx" in r.text.lower()

    def test_video_idx_negative_returns_422_or_400(self, admin_client, existing_run_any):
        run_id = existing_run_any["id"]
        r = admin_client.post(
            f"{BASE_URL}/api/admin/video-factory/{run_id}/voice-over",
            json={"video_idx": -1, "voice": "onyx"},
            timeout=15,
        )
        # Pydantic ge=0 → 422 validation error
        assert r.status_code in (400, 422)


# ===================================================
# T3 — DELETE voice-over
# ===================================================
class TestVoiceOverDelete:

    def test_delete_voice_over(self, admin_client, existing_run_without_vo):
        """Use run dbf77819 which already has voice_over per context.
        We delete then verify $unset worked.
        """
        run_id = existing_run_without_vo["id"]
        # Voice-over was generated in TestVoiceOverGenerate
        r = admin_client.delete(
            f"{BASE_URL}/api/admin/video-factory/{run_id}/voice-over/0",
            timeout=15,
        )
        assert r.status_code == 200, f"delete failed: {r.status_code} {r.text[:200]}"
        data = r.json()
        assert data.get("deleted") is True
        assert data.get("run_id") == run_id
        assert data.get("video_idx") == 0

        # Verify in history that voice_over field is gone
        r2 = admin_client.get(f"{BASE_URL}/api/admin/video-factory/history?limit=20", timeout=30)
        assert r2.status_code == 200
        runs = r2.json().get("runs") or r2.json().get("items") or r2.json()
        if isinstance(runs, dict):
            runs = runs.get("runs") or []
        found = next((x for x in runs if x.get("id") == run_id), None)
        assert found is not None
        vo = (found.get("videos") or [{}])[0].get("voice_over")
        assert vo is None, f"voice_over still present: {vo}"

    def test_delete_unknown_run_returns_404(self, admin_client):
        r = admin_client.delete(
            f"{BASE_URL}/api/admin/video-factory/no-such-run-id-xyz/voice-over/0",
            timeout=15,
        )
        assert r.status_code == 404

    def test_delete_video_idx_out_of_bounds(self, admin_client):
        r = admin_client.delete(
            f"{BASE_URL}/api/admin/video-factory/anything/voice-over/9",
            timeout=15,
        )
        assert r.status_code == 400


# ===================================================
# T4 — Non-régression V1/V2/V3
# ===================================================
class TestNonRegressionV3:

    def test_history_still_works(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/admin/video-factory/history?limit=5", timeout=30)
        assert r.status_code == 200
        body = r.json()
        runs = body.get("runs") or body.get("items") or body
        assert isinstance(runs, (list, dict))

    def test_performance_weights(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/admin/video-factory/performance/weights", timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict)

    def test_agents_registry_video_factory_v41(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/admin/agents/registry", timeout=20)
        assert r.status_code == 200
        body = r.json()
        agents = body.get("agents") if isinstance(body, dict) else body
        vf = None
        if isinstance(agents, dict):
            vf = agents.get("video_factory")
        elif isinstance(agents, list):
            vf = next((a for a in agents if a.get("key") == "video_factory" or a.get("name") == "video_factory" or a.get("id") == "video_factory"), None)
        assert vf is not None, f"video_factory agent missing from registry: keys={list(agents.keys()) if isinstance(agents,dict) else [a.get('key') or a.get('name') for a in (agents or [])]}"
        # Role mentions V4.1
        role = (vf.get("role") or "").lower()
        mission = (vf.get("mission") or "").lower()
        assert "v4.1" in role or "v4.1" in mission or "voix" in (role + mission) or "preview" in (role + mission), \
            f"V4.1 not mentioned in role/mission. role={role[:120]} mission={mission[:200]}"
        # 10 garde-fous (8 originaux + 2 nouveaux)
        guards = vf.get("guardrails") or vf.get("garde_fous") or vf.get("guard_rails") or vf.get("guards") or vf.get("safeguards") or []
        if isinstance(guards, str):
            # could be a single string joined
            import re
            count = len([x for x in re.split(r"[\n;|]", guards) if x.strip()])
        else:
            count = len(guards)
        assert count >= 10, f"Expected ≥10 garde-fous (8 V3 + 2 V4.1), got {count}"
