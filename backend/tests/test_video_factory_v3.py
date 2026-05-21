"""Video Factory V3 — Tests d'extension SEO landing page (pdf_enabled).

Couvre :
- pdf_enabled=true happy path : content_id, seo_pdf, compliance_passed
- Anti-divergence CTA (override Python)
- UTM différencié seo&organic
- Compliance racine ET logique
- pdf_enabled=false (V2 par défaut)
- Coût estimé
- Validation slug
- Markdown export
- Mongo persist + _id exclu
- Organigramme IA — carte video_factory
- Non-régression V2 (forced_format, mode, schéma CTA vidéo)
"""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # fallback frontend/.env
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


# ------------------------------------------------------------------
# Auth helpers
# ------------------------------------------------------------------
@pytest.fixture(scope="module")
def admin_token():
    s = requests.Session()
    for path in ("/api/admin/login", "/api/auth/admin/login", "/api/auth/login"):
        try:
            r = s.post(f"{BASE_URL}{path}",
                       json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
                       timeout=20)
            if r.status_code == 200:
                data = r.json()
                tok = data.get("token") or data.get("access_token") or data.get("admin_token")
                if tok:
                    return tok
        except Exception:
            continue
    pytest.skip("Admin login failed on all known paths")


@pytest.fixture(scope="module")
def admin_client(admin_token):
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {admin_token}",
                      "Content-Type": "application/json"})
    return s


# ------------------------------------------------------------------
# Shared : LLM call expensive → faire 1 seul appel pdf_enabled=True
# ------------------------------------------------------------------
@pytest.fixture(scope="module")
def gen_pdf_enabled(admin_client):
    payload = {
        "topic_brief": "Erreurs fréquentes face au médecin-conseil CPAM lors d'une expertise",
        "service_target": "auto",
        "intention": "autorité",
        "urgence": "critique",
        "plateforme": "TikTok",
        "batch_size": 1,
        "use_performance_weights": False,
        "forced_format": "F1",
        "pdf_enabled": True,
    }
    r = admin_client.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          json=payload, timeout=180)
    assert r.status_code == 200, f"generate failed: {r.status_code} {r.text[:300]}"
    return r.json()


@pytest.fixture(scope="module")
def gen_pdf_disabled(admin_client):
    payload = {
        "topic_brief": "Préparer son dossier expertise médicale en 5 étapes",
        "service_target": "auto",
        "intention": "éducatif",
        "urgence": "moyen",
        "plateforme": "YouTube Shorts",
        "batch_size": 1,
        "use_performance_weights": False,
        "forced_format": "F7",
        "pdf_enabled": False,
    }
    r = admin_client.post(f"{BASE_URL}/api/admin/video-factory/generate",
                          json=payload, timeout=180)
    assert r.status_code == 200, f"generate failed: {r.status_code} {r.text[:300]}"
    return r.json()


# ==================================================================
# T1 — pdf_enabled=true happy path : présence des champs racine
# ==================================================================
class TestPdfEnabledHappyPath:

    def test_content_id_equals_run_id(self, gen_pdf_enabled):
        assert gen_pdf_enabled.get("content_id") == gen_pdf_enabled.get("run_id")
        assert isinstance(gen_pdf_enabled.get("content_id"), str)

    def test_seo_pdf_present(self, gen_pdf_enabled):
        assert gen_pdf_enabled.get("seo_pdf") is not None
        assert isinstance(gen_pdf_enabled["seo_pdf"], dict)

    def test_compliance_passed_root(self, gen_pdf_enabled):
        assert "compliance_passed" in gen_pdf_enabled
        assert isinstance(gen_pdf_enabled["compliance_passed"], bool)

    def test_seo_pdf_structure(self, gen_pdf_enabled):
        seo = gen_pdf_enabled["seo_pdf"]
        # slug kebab-case ASCII
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", seo["slug"])
        assert len(seo["slug"]) <= 80
        # h1 non vide
        assert seo["h1"].strip()
        assert "meta_title" in seo and "meta_description" in seo
        # intro >= 60 mots (warning autorisé sinon)
        wc = len(re.findall(r"\b\w+\b", seo["intro"]))
        assert wc >= 40, f"intro trop courte ({wc} mots)"
        # blocks 3-5
        assert 3 <= len(seo["blocks"]) <= 5
        for b in seo["blocks"]:
            assert "h2" in b and "body" in b
        # faq jusqu'à 5
        assert isinstance(seo["faq"], list) and len(seo["faq"]) <= 5
        assert "keywords" in seo and isinstance(seo["keywords"], list)
        assert "internal_links_suggestions" in seo
        assert "video_embed_placeholder" in seo
        # cta_block
        cb = seo["cta_block"]
        assert {"text", "target_service", "url_with_utm"} <= set(cb.keys())
        assert "compliance_passed" in seo
        assert isinstance(seo.get("word_count"), int)
        assert isinstance(seo.get("markdown"), str) and seo["markdown"].startswith("# ")


# ==================================================================
# T2 — Anti-divergence CTA (override Python verbatim)
# ==================================================================
class TestAntiDivergenceCta:

    def test_cta_target_service_match(self, gen_pdf_enabled):
        v_cta = gen_pdf_enabled["videos"][0]["cta"]
        s_cta = gen_pdf_enabled["seo_pdf"]["cta_block"]
        assert s_cta["target_service"] == v_cta["target_service"]

    def test_cta_text_match_verbatim(self, gen_pdf_enabled):
        v_cta = gen_pdf_enabled["videos"][0]["cta"]
        s_cta = gen_pdf_enabled["seo_pdf"]["cta_block"]
        assert s_cta["text"] == v_cta["text"]


# ==================================================================
# T3 — UTM différencié
# ==================================================================
class TestUtmDifferentiation:

    def test_video_utm_unchanged(self, gen_pdf_enabled):
        url = gen_pdf_enabled["videos"][0]["cta"]["url_with_utm"]
        assert "utm_source=tiktok" in url
        assert "utm_medium=short" in url
        assert "utm_campaign=F1" in url

    def test_seo_utm_organic(self, gen_pdf_enabled):
        url = gen_pdf_enabled["seo_pdf"]["cta_block"]["url_with_utm"]
        assert "utm_source=seo" in url
        assert "utm_medium=organic" in url
        assert "utm_campaign=F1" in url

    def test_seo_and_video_same_base_url(self, gen_pdf_enabled):
        v = gen_pdf_enabled["videos"][0]["cta"]["url_with_utm"].split("?")[0]
        s = gen_pdf_enabled["seo_pdf"]["cta_block"]["url_with_utm"].split("?")[0]
        assert v == s


# ==================================================================
# T4 — Compliance racine ET logique
# ==================================================================
class TestComplianceRootLogic:

    def test_root_compliance_is_and_of_video_and_seo(self, gen_pdf_enabled):
        v_ok = all(v.get("compliance_passed", True) for v in gen_pdf_enabled["videos"])
        s_ok = gen_pdf_enabled["seo_pdf"].get("compliance_passed", True)
        assert gen_pdf_enabled["compliance_passed"] == (v_ok and s_ok)


# ==================================================================
# T5 — pdf_enabled=false (V2 default)
# ==================================================================
class TestPdfDisabled:

    def test_seo_pdf_is_null(self, gen_pdf_disabled):
        assert gen_pdf_disabled.get("seo_pdf") is None

    def test_content_id_present_and_equals_run_id(self, gen_pdf_disabled):
        assert gen_pdf_disabled.get("content_id") == gen_pdf_disabled.get("run_id")

    def test_compliance_reflects_video_only(self, gen_pdf_disabled):
        v_ok = all(v.get("compliance_passed", True) for v in gen_pdf_disabled["videos"])
        assert gen_pdf_disabled["compliance_passed"] == v_ok


# ==================================================================
# T6 — Coût estimé
# ==================================================================
class TestEstimatedCost:

    def test_cost_with_pdf(self, gen_pdf_enabled):
        c = gen_pdf_enabled["estimated_cost_eur"]
        assert 0.010 <= c <= 0.013, f"cost pdf=true should ≈0.011, got {c}"

    def test_cost_without_pdf(self, gen_pdf_disabled):
        c = gen_pdf_disabled["estimated_cost_eur"]
        assert 0.005 <= c <= 0.007, f"cost pdf=false should ≈0.006, got {c}"


# ==================================================================
# T7 — Slug regex + length
# ==================================================================
class TestSlugValidation:

    def test_slug_matches_regex(self, gen_pdf_enabled):
        slug = gen_pdf_enabled["seo_pdf"]["slug"]
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug)
        assert len(slug) <= 80


# ==================================================================
# T8 — Markdown export
# ==================================================================
class TestMarkdownExport:

    def test_markdown_structure(self, gen_pdf_enabled):
        md = gen_pdf_enabled["seo_pdf"]["markdown"]
        assert md.startswith("# ")
        assert "## " in md
        # CTA link en fin
        cta = gen_pdf_enabled["seo_pdf"]["cta_block"]
        assert cta["url_with_utm"] in md
        assert cta["text"] in md


# ==================================================================
# T9 — Mongo persistence (GET /history)
# ==================================================================
class TestMongoPersistence:

    def test_history_contains_run_with_seo_pdf(self, admin_client, gen_pdf_enabled):
        r = admin_client.get(f"{BASE_URL}/api/admin/video-factory/history?limit=20",
                             timeout=30)
        assert r.status_code == 200
        items = r.json().get("items", [])
        found = next((it for it in items if it.get("id") == gen_pdf_enabled["run_id"]), None)
        assert found is not None, "run not persisted"
        assert found.get("seo_pdf") is not None
        # No mongo _id leaked
        assert "_id" not in found


# ==================================================================
# T10 — Organigramme IA video_factory
# ==================================================================
class TestAgentsRegistryVideoFactory:

    def test_registry_includes_video_factory(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/admin/agents/registry", timeout=20)
        assert r.status_code == 200, r.text[:200]
        data = r.json()
        # Find agent with id=video_factory anywhere in payload
        flat = []
        def walk(o):
            if isinstance(o, dict):
                flat.append(o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        walk(data)
        vf = next((d for d in flat if d.get("id") == "video_factory"), None)
        assert vf is not None, "video_factory agent not found in registry"
        assert "Video Factory Engine" in vf.get("name", "")
        assert "Claude Haiku 4.5" in vf.get("model", "")
        assert "SEO_LANDING_SYSTEM_PROMPT" in (vf.get("prompt_var") or "")
        gj = " ".join(vf.get("guardrails") or [])
        assert "verbatim" in gj.lower() or "anti-divergence" in gj.lower()
        assert "floor" in gj.lower() or "exploration" in gj.lower()


# ==================================================================
# T11 — Non-régression V2 (CTA vidéo schema inchangé)
# ==================================================================
class TestV2NonRegression:

    def test_video_cta_schema_intact(self, gen_pdf_enabled):
        v = gen_pdf_enabled["videos"][0]
        cta = v["cta"]
        assert set(cta.keys()) >= {"text", "target_service", "url_with_utm"}
        # service critique → 97€
        assert cta["target_service"] == "97€"
        assert "97€" in cta["text"]

    def test_mode_field_present(self, gen_pdf_enabled, gen_pdf_disabled):
        assert gen_pdf_enabled.get("mode") in ("forced", "weighted", "fallback", "free")
        assert gen_pdf_disabled.get("mode") in ("forced", "weighted", "fallback", "free")

    def test_forced_format_resolved(self, gen_pdf_enabled):
        assert gen_pdf_enabled.get("forced_format") == "F1"
        assert gen_pdf_enabled["videos"][0]["format_used"] == "F1"

    def test_metrics_endpoint_exists(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/admin/video-factory/metrics?limit=5",
                             timeout=20)
        assert r.status_code == 200

    def test_performance_weights_endpoint(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/admin/video-factory/performance/weights",
                             timeout=20)
        assert r.status_code == 200
