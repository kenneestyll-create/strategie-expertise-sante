"""V4.3 — Light tracking on PATCH /status (rétro-compat + nouveaux champs).
Tests:
 1) Rétro-compat: body {status:'published'} seul → 200, video_idx/platform/public_url=null
 2) Enrichi: body avec video_idx + platform + public_url → response + persistance Mongo via GET /history
 3) Validation Pydantic 422 sur platform hors whitelist, video_idx>4, public_url>500 chars, status inconnu
 4) Garde-fou: status='draft' avec video_idx → ne doit PAS marquer published/publish_platform
 5) Registry agents : video_factory role V4.3, 16 garde-fous (8+2+3+3)
"""
import os
import pytest
import requests

def _load_frontend_url():
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        return None
    return None

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or _load_frontend_url() or "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL introuvable"


@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@accompagn-sante.fr", "password": "Admin2024!"},
        timeout=20,
    )
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text[:200]}"
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="module")
def existing_run_id(headers):
    r = requests.get(f"{BASE_URL}/api/admin/video-factory/history?limit=20", headers=headers, timeout=20)
    assert r.status_code == 200
    items = r.json().get("items", [])
    assert len(items) > 0, "Aucun run en historique pour tester V4.3"
    # Choisir un run avec au moins 1 vidéo
    for it in items:
        if it.get("videos"):
            return it["id"]
    pytest.skip("Pas de run avec vidéos")


# -------- 1) RÉTRO-COMPAT --------
def test_patch_status_backward_compatible_no_video_idx(headers, existing_run_id):
    """Body {status:'published'} seul → 200, video_idx/platform/public_url=null."""
    r = requests.patch(
        f"{BASE_URL}/api/admin/video-factory/{existing_run_id}/status",
        json={"status": "published"},
        headers=headers,
        timeout=15,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["updated"] is True
    assert data["status"] == "published"
    assert data["video_idx"] is None
    assert data["platform"] is None
    assert data["public_url"] is None


def test_patch_status_draft_back(headers, existing_run_id):
    """Repasser draft sans toucher autres champs."""
    r = requests.patch(
        f"{BASE_URL}/api/admin/video-factory/{existing_run_id}/status",
        json={"status": "draft"},
        headers=headers,
        timeout=15,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "draft"


# -------- 2) V4.3 ENRICHI --------
def test_patch_status_v43_enriched_with_platform_and_url(headers, existing_run_id):
    payload = {
        "status": "published",
        "video_idx": 0,
        "platform": "tiktok",
        "public_url": "https://tiktok.com/@ses/video/123",
    }
    r = requests.patch(
        f"{BASE_URL}/api/admin/video-factory/{existing_run_id}/status",
        json=payload,
        headers=headers,
        timeout=15,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["platform"] == "tiktok"
    assert data["public_url"] == payload["public_url"]
    assert data["video_idx"] == 0

    # GET /history → vérifie persistance
    h = requests.get(f"{BASE_URL}/api/admin/video-factory/history?limit=50", headers=headers, timeout=20)
    assert h.status_code == 200
    items = h.json()["items"]
    run = next((it for it in items if it["id"] == existing_run_id), None)
    assert run is not None
    v0 = run["videos"][0]
    assert v0.get("published") is True
    assert "published_at" in v0 and v0["published_at"]
    assert v0.get("publish_platform") == "tiktok"
    assert v0.get("publish_public_url") == payload["public_url"]


def test_patch_status_v43_no_public_url(headers, existing_run_id):
    """public_url absent → stocké à None côté API, pas écrit côté Mongo (set conditionnel)."""
    r = requests.patch(
        f"{BASE_URL}/api/admin/video-factory/{existing_run_id}/status",
        json={"status": "published", "video_idx": 0, "platform": "youtube"},
        headers=headers,
        timeout=15,
    )
    assert r.status_code == 200, r.text
    assert r.json()["platform"] == "youtube"
    assert r.json()["public_url"] is None


# -------- 3) VALIDATION 422 --------
@pytest.mark.parametrize("payload", [
    {"status": "published", "video_idx": 0, "platform": "facebook"},  # platform hors whitelist
    {"status": "published", "video_idx": 10, "platform": "tiktok"},  # video_idx > 4
    {"status": "published", "video_idx": 0, "platform": "tiktok", "public_url": "https://x.com/" + "a" * 501},
    {"status": "inexistant"},  # status invalide
])
def test_patch_status_validation_422(headers, existing_run_id, payload):
    r = requests.patch(
        f"{BASE_URL}/api/admin/video-factory/{existing_run_id}/status",
        json=payload,
        headers=headers,
        timeout=15,
    )
    assert r.status_code == 422, f"expected 422 for {payload}, got {r.status_code} {r.text[:300]}"


# -------- 4) GARDE-FOU draft+video_idx --------
def test_draft_with_video_idx_does_not_mark_published(headers, existing_run_id):
    """status=draft avec video_idx → ne doit PAS écrire publish_platform / published=true."""
    # 1) Reset run to known state via published youtube
    requests.patch(
        f"{BASE_URL}/api/admin/video-factory/{existing_run_id}/status",
        json={"status": "published", "video_idx": 0, "platform": "youtube"},
        headers=headers,
        timeout=15,
    )
    h0 = requests.get(f"{BASE_URL}/api/admin/video-factory/history?limit=50", headers=headers, timeout=20).json()
    run0 = next(it for it in h0["items"] if it["id"] == existing_run_id)
    before_platform = run0["videos"][0].get("publish_platform")

    # 2) Tentative malicieuse : draft + platform=instagram → ne doit PAS écraser
    r = requests.patch(
        f"{BASE_URL}/api/admin/video-factory/{existing_run_id}/status",
        json={"status": "draft", "video_idx": 0, "platform": "instagram", "public_url": "https://insta.com/x"},
        headers=headers,
        timeout=15,
    )
    assert r.status_code == 200, r.text

    h = requests.get(f"{BASE_URL}/api/admin/video-factory/history?limit=50", headers=headers, timeout=20).json()
    run2 = next(it for it in h["items"] if it["id"] == existing_run_id)
    v0 = run2["videos"][0]
    # Le draft ne doit pas avoir écrasé publish_platform vers 'instagram'
    assert v0.get("publish_platform") != "instagram", (
        f"draft+video_idx ne doit pas écrire publish_platform=instagram, got {v0.get('publish_platform')}"
    )
    # publish_platform doit rester ce qu'il était avant
    assert v0.get("publish_platform") == before_platform


# -------- 5) REGISTRY agents --------
def test_agents_registry_video_factory_v43(headers):
    r = requests.get(f"{BASE_URL}/api/admin/agents/registry", headers=headers, timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    # structure: { agents: [...] } ou { items: [...] } — on cherche video_factory
    pool = data.get("agents") or data.get("items") or data
    if isinstance(pool, dict):
        # peut-être un mapping
        pool_list = []
        for v in pool.values():
            if isinstance(v, list):
                pool_list.extend(v)
        pool = pool_list
    vf = None
    for a in pool:
        if isinstance(a, dict) and a.get("id") == "video_factory":
            vf = a
            break
    assert vf is not None, f"agent video_factory introuvable. keys: {list(data.keys())[:10]}"
    assert "V4.3" in vf.get("role", ""), f"role manque V4.3 : {vf.get('role')}"
    assert "V4.3" in vf.get("mission", ""), "mission manque V4.3"
    guardrails = vf.get("guardrails", [])
    assert len(guardrails) == 16, f"expected 16 guardrails, got {len(guardrails)}"
    v43_count = sum(1 for g in guardrails if "V4.3" in g)
    assert v43_count == 3, f"expected 3 V4.3 guardrails, got {v43_count}"


# -------- Cleanup --------
def test_cleanup_restore_draft(headers, existing_run_id):
    r = requests.patch(
        f"{BASE_URL}/api/admin/video-factory/{existing_run_id}/status",
        json={"status": "draft"},
        headers=headers,
        timeout=15,
    )
    assert r.status_code == 200
