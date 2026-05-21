"""V2 Final Stabilisation — Video Factory.

Covers:
- mode='forced' on /generate with forced_format=F6
- mode='free' on /generate with use_performance_weights=False
- mode='weighted' with snapshot existing
- mode='fallback' after purging snapshot
- Clamp weights ∈ [0,1] after injecting big conversion
- Monoculture guard reroll when one format >65% on 7d window with >=5 runs
- Structured JSON log emitted ("video_factory_generation")
- Non-regression: GenerateOutput schema unchanged (mode field present)
"""
import os
import json
import time
import pytest
import requests
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"
ALL_FMTS = {"F1", "F2", "F3", "F4", "F5", "F6", "F7"}
LOG_FILE = "/var/log/supervisor/backend.err.log"


@pytest.fixture(scope="module")
def admin_headers():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=30,
    )
    if r.status_code != 200:
        pytest.skip(f"Admin login failed: {r.status_code} {r.text[:200]}")
    data = r.json()
    tok = data.get("access_token") or data.get("token")
    if not tok:
        pytest.skip("No token")
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def created_ids():
    return []


@pytest.fixture(scope="module", autouse=True)
def cleanup(admin_headers, created_ids):
    yield
    for rid in created_ids:
        try:
            requests.delete(f"{BASE_URL}/api/admin/video-factory/{rid}",
                            headers=admin_headers, timeout=10)
        except Exception:
            pass


def _mongo_db():
    # Read env exactly like backend does
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        # Try loading from backend/.env
        from pathlib import Path
        env_path = Path("/app/backend/.env")
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("MONGO_URL=") and not mongo_url:
                    mongo_url = line.split("=", 1)[1].strip().strip('"')
                if line.startswith("DB_NAME=") and not db_name:
                    db_name = line.split("=", 1)[1].strip().strip('"')
    if not mongo_url or not db_name:
        pytest.skip("MONGO_URL/DB_NAME not available")
    client = AsyncIOMotorClient(mongo_url)
    return client[db_name], client


# ---------- 1. mode='forced' ----------
class TestModeForced:
    def test_forced_mode_F6(self, admin_headers, created_ids):
        payload = {
            "topic_brief": "Test mode forced F6 — règles MDPH",
            "service_target": "auto",
            "intention": "autorité",
            "urgence": "moyen",
            "plateforme": "TikTok",
            "batch_size": 1,
            "forced_format": "F6",
            "use_performance_weights": False,
        }
        r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          json=payload, headers=admin_headers, timeout=120)
        assert r.status_code == 200, r.text[:300]
        d = r.json()
        assert d.get("mode") == "forced", f"mode != forced: {d.get('mode')}"
        assert d.get("forced_format") == "F6"
        assert d.get("used_weights") is False
        assert d["videos"][0]["format_used"] == "F6"
        created_ids.append(d["run_id"])


# ---------- 2. mode='free' ----------
class TestModeFree:
    def test_free_mode(self, admin_headers, created_ids):
        payload = {
            "topic_brief": "Conseils mode libre, LLM choisit",
            "service_target": "auto",
            "urgence": "faible",
            "plateforme": "TikTok",
            "batch_size": 1,
            "use_performance_weights": False,
        }
        r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          json=payload, headers=admin_headers, timeout=120)
        assert r.status_code == 200, r.text[:300]
        d = r.json()
        assert d.get("mode") == "free", f"mode != free: {d.get('mode')}"
        assert d.get("forced_format") is None
        assert d.get("used_weights") is False
        assert d["videos"][0]["format_used"] in ALL_FMTS
        created_ids.append(d["run_id"])


# ---------- 3. mode='weighted' ----------
class TestModeWeighted:
    def test_weighted_mode(self, admin_headers, created_ids):
        # Make sure snapshot exists
        requests.post(f"{BASE_URL}/api/admin/video-factory/performance/recompute",
                      headers=admin_headers, timeout=15)
        payload = {
            "topic_brief": "Test mode weighted, snapshot doit exister",
            "service_target": "auto",
            "urgence": "moyen",
            "plateforme": "TikTok",
            "batch_size": 1,
            "use_performance_weights": True,
        }
        r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          json=payload, headers=admin_headers, timeout=120)
        assert r.status_code == 200, r.text[:300]
        d = r.json()
        assert d.get("mode") == "weighted", f"mode != weighted: {d.get('mode')}"
        assert d.get("used_weights") is True
        assert d.get("forced_format") in ALL_FMTS
        created_ids.append(d["run_id"])


# ---------- 4. mode='fallback' (after purging snapshot) ----------
class TestModeFallback:
    @pytest.mark.asyncio
    async def test_fallback_mode_after_purge(self, admin_headers, created_ids):
        db, client = _mongo_db()
        # Backup current snapshot
        snap = await db.video_format_weights.find_one({"_id": "latest"})
        try:
            await db.video_format_weights.delete_many({})
            # Now call /generate with use_performance_weights=True; should fallback
            payload = {
                "topic_brief": "Test mode fallback sans snapshot",
                "service_target": "auto",
                "urgence": "moyen",
                "plateforme": "TikTok",
                "batch_size": 1,
                "use_performance_weights": True,
            }
            r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                              json=payload, headers=admin_headers, timeout=120)
            assert r.status_code == 200, r.text[:300]
            d = r.json()
            assert d.get("mode") == "fallback", f"mode != fallback: {d.get('mode')} (full: {d})"
            assert d.get("used_weights") is False
            assert d.get("forced_format") in ALL_FMTS
            created_ids.append(d["run_id"])
        finally:
            # Restore snapshot
            if snap:
                snap.pop("_id", None)
                await db.video_format_weights.update_one(
                    {"_id": "latest"}, {"$set": snap}, upsert=True
                )
            client.close()


# ---------- 5. Clamp weights ∈ [0, 1] ----------
class TestClampWeights:
    @pytest.mark.asyncio
    async def test_clamp_after_huge_conversion(self, admin_headers):
        db, client = _mongo_db()
        try:
            # Inject extreme metric
            await db.video_metrics.insert_one({
                "run_id": "TEST_CLAMP_RUN",
                "video_idx": 0,
                "format_used": "F5",
                "views": 999999,
                "ctr": 99.0,
                "conversion": 9999.0,
                "plateforme": "TikTok",
                "note": "TEST_clamp",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "admin_email": "TEST",
            })
            # Force recompute via API
            rr = requests.post(f"{BASE_URL}/api/admin/video-factory/performance/recompute",
                               headers=admin_headers, timeout=15)
            assert rr.status_code == 200
            # Verify weights all in [0,1]
            rg = requests.get(f"{BASE_URL}/api/admin/video-factory/performance/weights",
                              headers=admin_headers, timeout=15)
            assert rg.status_code == 200
            w = rg.json().get("weights") or {}
            for fmt, val in w.items():
                assert 0.0 <= val <= 1.0, f"weight {fmt}={val} out of [0,1]"
            # The maximum should be exactly 1.0 (cap)
            assert max(w.values()) <= 1.0
        finally:
            # cleanup injected doc
            await db.video_metrics.delete_many({"run_id": "TEST_CLAMP_RUN"})
            # Trigger recompute to restore snapshot to real state
            requests.post(f"{BASE_URL}/api/admin/video-factory/performance/recompute",
                          headers=admin_headers, timeout=15)
            client.close()


# ---------- 6. Monoculture guard ----------
class TestMonocultureGuard:
    @pytest.mark.asyncio
    async def test_guard_reroll_when_F7_dominant(self, admin_headers):
        """Inject 8 fake F7 runs in last 7d, then snapshot makes F7 max.
        Backend should reroll away from F7.
        """
        db, client = _mongo_db()
        injected_ids = []
        try:
            # Force snapshot with F7=1.0, others=floor
            await db.video_format_weights.update_one(
                {"_id": "latest"},
                {"$set": {
                    "_id": "latest",
                    "weights": {"F1": 0.1, "F2": 0.1, "F3": 0.1, "F4": 0.1, "F5": 0.1, "F6": 0.1, "F7": 1.0},
                    "metrics_by_format": {},
                    "total_samples": 0,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }},
                upsert=True,
            )
            # Inject 8 fake runs with F7 in last 7d
            now_iso = datetime.now(timezone.utc).isoformat()
            for i in range(8):
                rid = f"TEST_MONO_{i}"
                await db.video_factory_runs.insert_one({
                    "id": rid,
                    "created_at": now_iso,
                    "admin_email": "TEST",
                    "videos": [{"format_used": "F7"}],
                    "status": "draft",
                    "mode": "forced",
                })
                injected_ids.append(rid)

            # Now generate with use_performance_weights=True
            payload = {
                "topic_brief": "Test garde monoculture",
                "service_target": "auto",
                "urgence": "moyen",
                "plateforme": "TikTok",
                "batch_size": 1,
                "use_performance_weights": True,
            }
            r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                              json=payload, headers=admin_headers, timeout=120)
            assert r.status_code == 200, r.text[:300]
            d = r.json()
            assert d.get("mode") == "weighted"
            # The forced_format chosen must NOT be F7 (guard reroll)
            assert d.get("forced_format") != "F7", (
                f"monoculture guard failed: chose F7 anyway (data={d.get('forced_format')})"
            )
            assert d.get("forced_format") in (ALL_FMTS - {"F7"})
            injected_ids.append(d["run_id"])  # also cleanup the generated run
        finally:
            # cleanup injected runs + the real one
            for rid in injected_ids:
                await db.video_factory_runs.delete_one({"id": rid})
            # restore snapshot via recompute
            requests.post(f"{BASE_URL}/api/admin/video-factory/performance/recompute",
                          headers=admin_headers, timeout=15)
            client.close()


# ---------- 7. JSON log emitted ----------
class TestJsonLog:
    def test_json_log_after_generate(self, admin_headers, created_ids):
        # Trigger a generation
        payload = {
            "topic_brief": "Test log JSON structuré V2 final",
            "service_target": "auto",
            "urgence": "moyen",
            "plateforme": "TikTok",
            "batch_size": 1,
            "forced_format": "F2",
            "use_performance_weights": False,
        }
        r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          json=payload, headers=admin_headers, timeout=120)
        assert r.status_code == 200, r.text[:200]
        d = r.json()
        created_ids.append(d["run_id"])
        run_id = d["run_id"]
        # Give logger a moment to flush
        time.sleep(1.0)
        # Search both .err.log and .out.log for the JSON line
        candidates = [
            "/var/log/supervisor/backend.err.log",
            "/var/log/supervisor/backend.out.log",
        ]
        found_line = None
        for path in candidates:
            if not os.path.exists(path):
                continue
            try:
                # tail last ~1000 lines
                with open(path, "r", errors="ignore") as f:
                    lines = f.readlines()[-2000:]
                for line in lines:
                    if "video_factory_generation" in line and run_id in line:
                        found_line = line
                        break
            except Exception:
                continue
            if found_line:
                break
        assert found_line, (
            f"Structured JSON log not found for run_id={run_id} "
            f"(searched {candidates})"
        )
        # Parse JSON payload from the line (extract braces region)
        start = found_line.find("{")
        end = found_line.rfind("}")
        assert start >= 0 and end > start, f"no JSON in log line: {found_line[:200]}"
        payload_json = json.loads(found_line[start:end + 1])
        assert payload_json.get("evt") == "video_factory_generation"
        assert payload_json.get("run_id") == run_id
        assert payload_json.get("format") == "F2"
        assert payload_json.get("mode") == "forced"
        assert "weights_snapshot" in payload_json
        assert "conversion_score" in payload_json
        assert "timestamp" in payload_json
        assert payload_json.get("video_id", "").startswith(f"{run_id}#")


# ---------- 8. Non-regression: schema additive ----------
class TestSchemaNonRegression:
    def test_generate_response_has_mode_field(self, admin_headers, created_ids):
        payload = {
            "topic_brief": "Smoke test schema",
            "service_target": "auto",
            "urgence": "moyen",
            "plateforme": "TikTok",
            "batch_size": 1,
            "forced_format": "F1",
            "use_performance_weights": False,
        }
        r = requests.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          json=payload, headers=admin_headers, timeout=120)
        assert r.status_code == 200
        d = r.json()
        # All V1+V2 keys still there
        for key in ("run_id", "model_used", "estimated_cost_eur", "videos",
                    "warnings", "created_at", "forced_format", "used_weights", "mode"):
            assert key in d, f"missing key {key} in response"
        # CTA schema unchanged
        cta = d["videos"][0]["cta"]
        for k in ("text", "target_service", "url_with_utm"):
            assert k in cta, f"CTA schema regression: missing {k}"
        created_ids.append(d["run_id"])
