"""
Test StrategiIA Analysis Storage Bug Fix
=========================================
Bug: StrategiIA premium analysis was NOT being stored in the database.
When admin clicked 'Relire/Valider', only the raw client situation text appeared.

Fix: 
1) Store analysis text in strategiia_analyses with job_id link
2) Update premium_analyses entry with the analysis text
3) Improve full-content endpoint to look up via job_id first

Test cases:
- Verify full-content endpoint returns analysis (>1000 chars) for known entry
- Verify strategiia_analyses and premium_analyses have correct fields
- Non-regression tests for health/llm, dossier-express/weekly-count, admin-bypass
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Known test data from the bug fix
KNOWN_PREMIUM_ANALYSES_ID = "c64897f3-8ffe-4149-b251-4f2d9a2ebcc4"
KNOWN_JOB_ID = "4a60398e-4ba"

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")


@pytest.fixture
def auth_headers(admin_token):
    """Headers with admin auth token"""
    return {"Authorization": f"Bearer {admin_token}"}


class TestStrategiIAAnalysisStorageFix:
    """Tests for the StrategiIA analysis storage bug fix"""

    def test_full_content_returns_analysis_not_raw_situation(self, auth_headers):
        """
        CRITICAL: full-content endpoint must return actual AI analysis (>1000 chars)
        NOT just the raw client situation text
        """
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses/{KNOWN_PREMIUM_ANALYSES_ID}/full-content",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        full_text = data.get("full_text", "")
        
        # Must have substantial analysis content (>1000 chars)
        assert len(full_text) > 1000, f"full_text too short ({len(full_text)} chars), expected >1000"
        
        # Analysis should start with proper heading, NOT raw situation
        assert "## Votre situation analysée" in full_text or "##" in full_text[:100], \
            f"Analysis should start with proper heading, got: {full_text[:200]}"
        
        # Should NOT be just the raw situation (which would be <500 chars typically)
        source_situation = data.get("source_data", {}).get("situation", "")
        assert full_text != source_situation, "full_text should NOT be just the raw situation"
        
        print(f"✓ full_text length: {len(full_text)} chars")
        print(f"✓ Analysis starts with: {full_text[:100]}...")

    def test_full_content_has_correct_type(self, auth_headers):
        """Verify the entry is correctly identified as strategiia type"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses/{KNOWN_PREMIUM_ANALYSES_ID}/full-content",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("type") == "strategiia", f"Expected type 'strategiia', got {data.get('type')}"
        assert data.get("id") == KNOWN_PREMIUM_ANALYSES_ID

    def test_full_content_has_source_data(self, auth_headers):
        """Verify source_data is populated with original context"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses/{KNOWN_PREMIUM_ANALYSES_ID}/full-content",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        source_data = data.get("source_data", {})
        
        # Should have type_dossier, regime, situation
        assert source_data.get("type_dossier"), "source_data should have type_dossier"
        assert source_data.get("situation"), "source_data should have situation"
        
        print(f"✓ source_data: {source_data}")


class TestPremiumAnalysesCollection:
    """Tests for premium_analyses collection data integrity"""

    def test_premium_analyses_has_analysis_field(self, auth_headers):
        """Verify premium_analyses entry has analysis field stored"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        items = data.get("items", [])
        
        # Find our known entry
        target = next((i for i in items if i.get("id") == KNOWN_PREMIUM_ANALYSES_ID), None)
        assert target is not None, f"Entry {KNOWN_PREMIUM_ANALYSES_ID} not found in premium_analyses"
        
        # Check job_id is present
        assert target.get("job_id") == KNOWN_JOB_ID, f"Expected job_id {KNOWN_JOB_ID}, got {target.get('job_id')}"
        
        # Check analysis field exists and has content
        analysis = target.get("analysis", "")
        assert len(analysis) > 1000, f"analysis field too short ({len(analysis)} chars)"
        
        print(f"✓ premium_analyses entry has analysis: {len(analysis)} chars")
        print(f"✓ job_id: {target.get('job_id')}")


class TestNonRegression:
    """Non-regression tests for existing functionality"""

    def test_health_llm_endpoint(self):
        """GET /api/health/llm should return operational status"""
        response = requests.get(f"{BASE_URL}/api/health/llm")
        assert response.status_code == 200
        
        data = response.json()
        assert "operational" in data
        print(f"✓ LLM health: operational={data.get('operational')}, reason={data.get('reason')}")

    def test_dossier_express_weekly_count(self):
        """GET /api/dossier-express/weekly-count should return count"""
        response = requests.get(f"{BASE_URL}/api/dossier-express/weekly-count")
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert "period" in data
        print(f"✓ Weekly count: {data.get('count')} ({data.get('period')})")

    def test_dossier_express_admin_bypass_endpoint_exists(self, auth_headers):
        """POST /api/dossier-express/admin-bypass should exist (not 404)"""
        # Just verify endpoint exists - don't actually run analysis
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            headers=auth_headers,
            json={}  # Empty body to trigger validation error, not 404
        )
        # Should get 400 (validation error) or 422, NOT 404
        assert response.status_code != 404, "Endpoint should exist"
        print(f"✓ dossier-express/admin-bypass endpoint exists (status: {response.status_code})")

    def test_strategiia_admin_bypass_premium_endpoint_exists(self, auth_headers):
        """POST /api/strategiia/admin-bypass-premium should exist"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/admin-bypass-premium",
            headers=auth_headers,
            json={}  # Empty body to trigger validation error
        )
        # Should get 400 (validation error), NOT 404
        assert response.status_code != 404, "Endpoint should exist"
        print(f"✓ strategiia/admin-bypass-premium endpoint exists (status: {response.status_code})")


class TestAdminPremiumAnalysesList:
    """Tests for admin premium analyses list endpoint"""

    def test_get_premium_analyses_list(self, auth_headers):
        """GET /api/admin/premium-analyses should return items and stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "stats" in data
        
        items = data.get("items", [])
        stats = data.get("stats", {})
        
        print(f"✓ Total items: {len(items)}")
        print(f"✓ Stats: {stats}")
        
        # Find strategiia items
        strategiia_items = [i for i in items if i.get("type") == "strategiia"]
        print(f"✓ StrategiIA items: {len(strategiia_items)}")

    def test_premium_analyses_has_en_attente_items(self, auth_headers):
        """Verify there are items in en_attente status for testing"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        items = data.get("items", [])
        
        en_attente = [i for i in items if i.get("status") == "en_attente"]
        print(f"✓ Items en_attente: {len(en_attente)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
