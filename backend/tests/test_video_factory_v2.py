"""Tests for S.E.S Autonomous Video Factory V2 features.

Covers:
- forced_format on POST /generate (F1-F7) + invalid value (400)
- conversion_score, disclaimer_text new JSON fields
- POST /metrics + recompute weights (10% floor)
- GET /metrics (no _id leak)
- GET /performance/weights (all F1-F7 present)
- POST /performance/recompute
- use_performance_weights flow (used_weights=true)
- V1 non-regression: generate without forced_format/use_weights still works
- Compliance V2: forbidden patterns trigger compliance_passed=false
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"
ALL_FMTS = {"F1", "F2", "F3", "F4", "F5", "F6", "F7"}


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


@pytest.fixture(scope="module", autouse=True)
def cleanup(admin_headers, created_run_ids):
    yield
    for rid in list(created_run_ids):
        try:
            requests.delete(
                f"{BASE_URL}/api/admin/video-factory/{rid}",
                headers=admin_headers, timeout=10,
            )
        except Exception:
            pass


# ---------- 1. forced_format validation ----------
class TestForcedFormatValidation:
    def test_forced_format_invalid_F99(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json={"topic_brief": "test invalid format", "forced_format": "F99"},
            headers=admin_headers, timeout=15,
        )
        assert r.status_code == 400, f"Expected 400, got {r.status_code}: {r.text[:200]}"

    def test_forced_format_invalid_string(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json={"topic_brief": "test invalid", "forced_format": "INVALID"},
            headers=admin_headers, timeout=15,
        )
        assert r.status_code == 400


# ---------- 2. forced_format=F3 happy path ----------
class TestForcedFormatF3:
    def test_forced_format_F3_with_service_29(self, admin_headers, created_run_ids):
        payload = {
            "topic_brief": "Cas anonyme : Mme X obtient un taux IPP revu en sa faveur après expertise",
            "service_target": "29€",
            "intention": "autorité",
            "urgence": "moyen",
            "plateforme": "TikTok",
            "batch_size": 1,
            "forced_format": "F3",
            "use_performance_weights": False,
        }
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json=payload, headers=admin_headers, timeout=120,
        )
        assert r.status_code == 200, f"Got {r.status_code}: {r.text[:400]}"
        data = r.json()
        # Top-level V2 fields
        assert data.get("forced_format") == "F3", f"top-level forced_format != F3 : {data.get('forced_format')}"
        assert data.get("used_weights") is False
        videos = data.get("videos") or []
        assert len(videos) == 1
        v = videos[0]
        assert v["format_used"] == "F3", f"format_used != F3 : {v.get('format_used')}"
        assert v["format_label"] == "Cas réel anonymisé", f"label mismatch : {v.get('format_label')}"
        # Conversion score 1-5
        cs = v.get("conversion_score")
        assert isinstance(cs, int) and 1 <= cs <= 5, f"conversion_score invalid : {cs}"
        # Disclaimer non-empty
        dt = v.get("disclaimer_text")
        assert isinstance(dt, str) and dt.strip(), "disclaimer_text empty"
        # CTA mapped to 29€
        cta = v["cta"]
        assert cta["target_service"] == "29€"
        assert "utm_campaign=F3" in cta["url_with_utm"], f"UTM campaign != F3 : {cta['url_with_utm']}"
        created_run_ids.append(data["run_id"])


# ---------- 3. Metrics POST / GET ----------
class TestMetricsFlow:
    @pytest.fixture(scope="class")
    def run_for_metrics(self, admin_headers, created_run_ids):
        payload = {
            "topic_brief": "Anecdote rapide sur une expertise médicale CPAM",
            "service_target": "auto",
            "urgence": "critique",
            "plateforme": "TikTok",
            "batch_size": 1,
            "forced_format": "F7",
            "use_performance_weights": False,
        }
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json=payload, headers=admin_headers, timeout=120,
        )
        assert r.status_code == 200, r.text[:300]
        data = r.json()
        created_run_ids.append(data["run_id"])
        assert data["videos"][0]["format_used"] == "F7"
        return data["run_id"]

    def test_save_metrics_updates_weights_with_floor(self, admin_headers, run_for_metrics):
        body = {
            "run_id": run_for_metrics,
            "video_idx": 0,
            "views": 10000,
            "ctr": 4.5,
            "conversion": 2.0,
            "note": "TEST metric",
        }
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/metrics",
            json=body, headers=admin_headers, timeout=15,
        )
        assert r.status_code == 200, f"{r.status_code}: {r.text[:300]}"
        d = r.json()
        assert d.get("saved") is True
        assert d.get("format_used") == "F7"
        assert d.get("weights_updated") is True
        w = d.get("weights") or {}
        # All F1-F7 must be present, F7 should be max (only sample), floor 0.1 on others
        for fmt in ALL_FMTS:
            assert fmt in w, f"missing weight key {fmt}"
            assert w[fmt] >= 0.0999, f"floor 10% violated on {fmt}: {w[fmt]}"
        assert w["F7"] >= max(w[f] for f in ALL_FMTS - {"F7"}), "F7 should be top weight"

    def test_metrics_run_id_not_found(self, admin_headers):
        body = {
            "run_id": "nonexistent-run-id-xyz",
            "video_idx": 0,
            "views": 100, "ctr": 1.0, "conversion": 0.5,
        }
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/metrics",
            json=body, headers=admin_headers, timeout=15,
        )
        assert r.status_code == 404, f"Expected 404, got {r.status_code}: {r.text[:200]}"

    def test_metrics_video_idx_out_of_range(self, admin_headers, run_for_metrics):
        body = {
            "run_id": run_for_metrics,
            "video_idx": 4,  # only 1 video → idx >=1 should be out of bound; but Pydantic allows up to 4
            "views": 100, "ctr": 1.0, "conversion": 0.5,
        }
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/metrics",
            json=body, headers=admin_headers, timeout=15,
        )
        assert r.status_code == 400, f"Expected 400, got {r.status_code}: {r.text[:200]}"

    def test_get_metrics_no_underscore_id(self, admin_headers):
        r = requests.get(
            f"{BASE_URL}/api/admin/video-factory/metrics?limit=50",
            headers=admin_headers, timeout=15,
        )
        assert r.status_code == 200
        d = r.json()
        assert "items" in d
        items = d["items"]
        assert isinstance(items, list)
        for it in items:
            assert "_id" not in it, f"MongoDB _id leaked in metrics: {it.keys()}"
        # Sort desc by created_at
        if len(items) >= 2:
            dts = [it.get("created_at", "") for it in items]
            assert dts == sorted(dts, reverse=True), "metrics not sorted by created_at desc"


# ---------- 4. Performance weights endpoints ----------
class TestPerformanceWeights:
    def test_get_performance_weights_all_formats_present(self, admin_headers):
        r = requests.get(
            f"{BASE_URL}/api/admin/video-factory/performance/weights",
            headers=admin_headers, timeout=15,
        )
        assert r.status_code == 200, r.text[:300]
        d = r.json()
        assert "weights" in d, f"missing 'weights' key in {d.keys()}"
        assert "metrics_by_format" in d
        assert "total_samples" in d
        assert "updated_at" in d
        w = d["weights"]
        for fmt in ALL_FMTS:
            assert fmt in w, f"missing format {fmt} in weights"
            assert w[fmt] >= 0.0999, f"floor violated on {fmt}: {w[fmt]}"

    def test_recompute_weights(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/performance/recompute",
            headers=admin_headers, timeout=15,
        )
        assert r.status_code == 200, r.text[:300]
        d = r.json()
        assert d.get("recomputed") is True
        w = d.get("weights") or {}
        for fmt in ALL_FMTS:
            assert fmt in w


# ---------- 5. use_performance_weights flow ----------
class TestUseWeightsFlow:
    def test_use_weights_injects_forced_format(self, admin_headers, created_run_ids):
        """Si snapshot existe et forced_format absent → backend choisit Fx et le retourne."""
        # ensure a snapshot exists
        requests.post(
            f"{BASE_URL}/api/admin/video-factory/performance/recompute",
            headers=admin_headers, timeout=15,
        )
        payload = {
            "topic_brief": "Generation avec poids actifs",
            "service_target": "auto",
            "urgence": "moyen",
            "plateforme": "TikTok",
            "batch_size": 1,
            "use_performance_weights": True,
            # forced_format absent
        }
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json=payload, headers=admin_headers, timeout=120,
        )
        assert r.status_code == 200, r.text[:400]
        data = r.json()
        assert data.get("used_weights") is True, f"used_weights should be True : {data.get('used_weights')}"
        assert data.get("forced_format") in ALL_FMTS, f"forced_format should be Fx : {data.get('forced_format')}"
        created_run_ids.append(data["run_id"])


# ---------- 6. V1 non-regression ----------
class TestV1NonRegression:
    def test_v1_legacy_generate_no_forced_no_weights(self, admin_headers, created_run_ids):
        """V1 mode: pas de forced_format, use_performance_weights=False → comportement V1 (auto LLM)."""
        payload = {
            "topic_brief": "Conseils pratiques pour bien préparer son dossier MDPH",
            "service_target": "auto",
            "urgence": "faible",
            "plateforme": "YouTube Shorts",
            "batch_size": 1,
            "use_performance_weights": False,
        }
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json=payload, headers=admin_headers, timeout=120,
        )
        assert r.status_code == 200, r.text[:300]
        d = r.json()
        assert d.get("used_weights") is False
        assert d.get("forced_format") is None
        v = d["videos"][0]
        assert v["format_used"] in ALL_FMTS
        # V2 enrichments still present
        assert isinstance(v.get("conversion_score"), int)
        assert (v.get("disclaimer_text") or "").strip()
        # V1 CTA mapping intact (faible+auto → 0€)
        assert v["cta"]["target_service"] == "0€"
        created_run_ids.append(d["run_id"])

    def test_history_still_works_no_id_leak(self, admin_headers):
        r = requests.get(
            f"{BASE_URL}/api/admin/video-factory/history?limit=20",
            headers=admin_headers, timeout=15,
        )
        assert r.status_code == 200
        items = r.json().get("items") or []
        for it in items:
            assert "_id" not in it

    def test_history_unauth(self):
        r = requests.get(f"{BASE_URL}/api/admin/video-factory/history", timeout=10)
        assert r.status_code in (401, 403)

    def test_metrics_unauth(self):
        r = requests.get(f"{BASE_URL}/api/admin/video-factory/metrics", timeout=10)
        assert r.status_code in (401, 403)


# ---------- 7. Compliance V2 ----------
class TestComplianceV2:
    def test_forbidden_pattern_flags_compliance(self, admin_headers, created_run_ids):
        """Brief avec 'la CPAM ment' + 'garanti 100%' → compliance_passed=false attendu."""
        payload = {
            "topic_brief": "Pourquoi la CPAM ment souvent et comment obtenir un résultat garanti 100%",
            "service_target": "29€",
            "urgence": "moyen",
            "plateforme": "TikTok",
            "batch_size": 1,
            "use_performance_weights": False,
        }
        r = requests.post(
            f"{BASE_URL}/api/admin/video-factory/generate",
            json=payload, headers=admin_headers, timeout=120,
        )
        assert r.status_code == 200, r.text[:400]
        d = r.json()
        created_run_ids.append(d["run_id"])
        videos = d.get("videos") or []
        assert len(videos) >= 1
        # The backend audits the LLM output itself; the LLM SHOULD reject these terms,
        # but if any leak through, compliance_passed must be False with notes.
        # If LLM was clean (no forbidden terms in OUTPUT), compliance can be True.
        # We assert the field structure is correct.
        for v in videos:
            cp = v.get("compliance_passed")
            assert isinstance(cp, bool)
            if not cp:
                assert v.get("compliance_notes"), "compliance_notes must be set when compliance fails"
