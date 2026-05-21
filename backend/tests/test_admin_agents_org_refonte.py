"""Backend tests for the Organigramme IA refonte (iteration 199).

Validates GET /api/admin/agents/registry:
- 8 agents (incl. video_factory) + 1 internal_agent (kit_professionnel)
- video_factory prompt is concatenated from SYSTEM_PROMPT + SEO_LANDING_SYSTEM_PROMPT
  (multi-variable prompt_var separated by '|') and exceeds 5000 chars.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/") or \
    open("/app/frontend/.env").read().split("REACT_APP_BACKEND_URL=")[1].split("\n")[0].strip().strip('"')

ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=20,
    )
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    data = r.json()
    tok = data.get("access_token") or data.get("token")
    assert tok, f"no token in login response: {data}"
    return tok


@pytest.fixture(scope="module")
def registry(admin_token):
    r = requests.get(
        f"{BASE_URL}/api/admin/agents/registry",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=20,
    )
    assert r.status_code == 200, f"registry failed: {r.status_code} {r.text}"
    return r.json()


# ── Registry structure ────────────────────────────────────────────────
class TestRegistryStructure:
    def test_ceo_present(self, registry):
        assert "ceo" in registry
        assert registry["ceo"].get("name")
        assert registry["ceo"].get("role")

    def test_agents_count_is_8(self, registry):
        assert len(registry["agents"]) == 8, [a["id"] for a in registry["agents"]]

    def test_internal_agents_count_is_1(self, registry):
        ia = registry.get("internal_agents", [])
        assert len(ia) == 1
        assert ia[0]["id"] == "kit_professionnel"

    def test_expected_agent_ids(self, registry):
        ids = {a["id"] for a in registry["agents"]}
        expected = {
            "strate", "strategiia", "dossier_express",
            "video_factory",
            "editorial_planner", "editorial_writer",
            "editorial_critic", "editorial_structurer",
        }
        assert ids == expected, f"unexpected ids: {ids ^ expected}"


# ── video_factory multi-variable prompt ───────────────────────────────
class TestVideoFactoryAgent:
    @pytest.fixture
    def vf(self, registry):
        matches = [a for a in registry["agents"] if a["id"] == "video_factory"]
        assert matches, "video_factory missing from registry"
        return matches[0]

    def test_metadata(self, vf):
        assert vf["name"] == "Video Factory Engine"
        assert "Claude Haiku 4.5" in vf["model"]
        assert len(vf.get("guardrails", [])) == 8

    def test_prompt_var_is_multi(self, vf):
        assert "|" in vf.get("prompt_var", "")
        assert "SYSTEM_PROMPT" in vf["prompt_var"]
        assert "SEO_LANDING_SYSTEM_PROMPT" in vf["prompt_var"]

    def test_prompt_concatenated_and_large(self, vf):
        p = vf.get("prompt", "")
        assert len(p) > 5000, f"prompt too short ({len(p)})"
        assert "=== SYSTEM_PROMPT ===" in p
        assert "=== SEO_LANDING_SYSTEM_PROMPT ===" in p


# ── kit_professionnel internal agent ──────────────────────────────────
class TestKitProfessionnel:
    def test_internal_agent_has_prompt(self, registry):
        ia = registry["internal_agents"][0]
        assert ia["id"] == "kit_professionnel"
        assert len(ia.get("prompt", "")) > 100
