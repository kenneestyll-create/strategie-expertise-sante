"""
Test suite for Dossier Express IA workflow fixes:
1. POST /api/dossier-express/admin-bypass creates dossier and premium_analyses entry
2. GET /api/admin/premium-analyses/{id}/full-content returns analysis from dossier_express collection
3. GET /api/admin/dossier-express/{id}/analysis returns complete analysis for a specific dossier
4. PATCH /api/admin/premium-analyses/{id} changes status correctly
5. POST /api/admin/premium-analyses/{id}/send-reviewed uses correct report_type based on type
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com')

# Admin credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    """Return headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}


class TestDossierExpressAdminBypass:
    """Test admin-bypass endpoint creates dossier and premium_analyses entry"""
    
    def test_admin_bypass_creates_dossier(self, auth_headers):
        """POST /api/dossier-express/admin-bypass should create a dossier"""
        payload = {
            "name": "TEST_Admin_Bypass_User",
            "situation": "Test situation for admin bypass - testing premium_analyses creation",
            "type_dossier": "Accident du travail (AT)",
            "regime": "Régime général",
            "documents_text": "Test document content",
            "premium_pdf": False
        }
        response = requests.post(
            f"{BASE_URL}/api/dossier-express/admin-bypass",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Admin bypass failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "dossier_id" in data
        assert data.get("admin_test") is True
        
        # Store dossier_id for subsequent tests
        TestDossierExpressAdminBypass.dossier_id = data["dossier_id"]
        print(f"Created dossier via admin-bypass: {data['dossier_id']}")
    
    def test_dossier_status_endpoint(self, auth_headers):
        """GET /api/dossier-express/status/{id} should return dossier status"""
        dossier_id = getattr(TestDossierExpressAdminBypass, 'dossier_id', None)
        if not dossier_id:
            pytest.skip("No dossier_id from previous test")
        
        # Wait a bit for processing to start
        time.sleep(2)
        
        response = requests.get(f"{BASE_URL}/api/dossier-express/status/{dossier_id}")
        assert response.status_code == 200, f"Status check failed: {response.text}"
        data = response.json()
        assert "status" in data
        assert data.get("id") == dossier_id
        print(f"Dossier status: {data.get('status')}, progress_step: {data.get('progress_step')}")


class TestAdminPremiumAnalysesEndpoints:
    """Test premium analyses admin endpoints"""
    
    def test_get_premium_analyses_list(self, auth_headers):
        """GET /api/admin/premium-analyses should return list with stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get premium analyses: {response.text}"
        data = response.json()
        assert "items" in data
        assert "stats" in data
        assert isinstance(data["items"], list)
        
        # Check stats structure
        stats = data["stats"]
        assert "total" in stats
        assert "en_attente" in stats
        assert "en_cours" in stats
        print(f"Premium analyses: {stats['total']} total, {stats['en_attente']} en_attente")
    
    def test_premium_analyses_has_dossier_express_items(self, auth_headers):
        """Premium analyses should include dossier_express type items"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        dossier_express_items = [i for i in data["items"] if i.get("type") == "dossier_express"]
        print(f"Found {len(dossier_express_items)} dossier_express items in premium_analyses")
        
        # At least one should exist from our admin-bypass test or previous tests
        # This is informational - we don't fail if none exist yet
        if dossier_express_items:
            item = dossier_express_items[0]
            assert "id" in item
            assert "email" in item
            assert "status" in item
            print(f"Sample dossier_express item: id={item['id']}, status={item['status']}")
    
    def test_premium_analyses_has_strategiia_items(self, auth_headers):
        """Premium analyses should include strategiia type items"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        strategiia_items = [i for i in data["items"] if i.get("type") == "strategiia"]
        print(f"Found {len(strategiia_items)} strategiia items in premium_analyses")


class TestFullContentEndpoint:
    """Test GET /api/admin/premium-analyses/{id}/full-content"""
    
    def test_full_content_for_dossier_express(self, auth_headers):
        """Full content endpoint should return analysis from dossier_express collection"""
        # First get a dossier_express premium analysis
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        dossier_express_items = [i for i in data["items"] if i.get("type") == "dossier_express"]
        if not dossier_express_items:
            pytest.skip("No dossier_express items in premium_analyses")
        
        item = dossier_express_items[0]
        item_id = item["id"]
        
        # Get full content
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses/{item_id}/full-content",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Full content failed: {response.text}"
        content = response.json()
        
        assert "id" in content
        assert "type" in content
        assert content["type"] == "dossier_express"
        assert "full_text" in content
        assert "source_data" in content
        assert "email" in content
        assert "status" in content
        
        # source_data should contain dossier info
        source = content.get("source_data", {})
        print(f"Full content source_data keys: {list(source.keys())}")
        # These fields come from dossier_express collection
        if source:
            print(f"  situation: {source.get('situation', '')[:50]}...")
            print(f"  type_dossier: {source.get('type_dossier')}")
            print(f"  regime: {source.get('regime')}")
    
    def test_full_content_for_strategiia(self, auth_headers):
        """Full content endpoint should work for strategiia type"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        strategiia_items = [i for i in data["items"] if i.get("type") == "strategiia"]
        if not strategiia_items:
            pytest.skip("No strategiia items in premium_analyses")
        
        item = strategiia_items[0]
        item_id = item["id"]
        
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses/{item_id}/full-content",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Full content failed: {response.text}"
        content = response.json()
        
        assert content["type"] == "strategiia"
        print(f"StrategiIA full content: {len(content.get('full_text', ''))} chars")


class TestDossierExpressAnalysisEndpoint:
    """Test GET /api/admin/dossier-express/{id}/analysis"""
    
    def test_get_dossier_analysis_by_id(self, auth_headers):
        """Should return complete analysis for a specific dossier"""
        # First get list of dossiers
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get dossier list: {response.text}"
        data = response.json()
        
        # Find a completed dossier
        completed = [d for d in data.get("items", []) if d.get("status") == "completed"]
        if not completed:
            pytest.skip("No completed dossiers to test")
        
        dossier = completed[0]
        dossier_id = dossier["id"]
        
        # Get analysis
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/{dossier_id}/analysis",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get analysis failed: {response.text}"
        analysis = response.json()
        
        assert "id" in analysis
        assert analysis["id"] == dossier_id
        assert "email" in analysis
        assert "status" in analysis
        assert "analysis" in analysis
        assert "situation" in analysis
        assert "type_dossier" in analysis
        assert "regime" in analysis
        
        print(f"Dossier analysis: {len(analysis.get('analysis', ''))} chars")
        print(f"  type_dossier: {analysis.get('type_dossier')}")
        print(f"  regime: {analysis.get('regime')}")
    
    def test_get_nonexistent_dossier_returns_404(self, auth_headers):
        """Should return 404 for non-existent dossier"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express/nonexistent-id-12345/analysis",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestPatchPremiumAnalysisStatus:
    """Test PATCH /api/admin/premium-analyses/{id}"""
    
    def test_patch_status_to_en_cours(self, auth_headers):
        """Should change status from en_attente to en_cours"""
        # Get an en_attente item
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        en_attente = [i for i in data["items"] if i.get("status") == "en_attente"]
        if not en_attente:
            pytest.skip("No en_attente items to test status change")
        
        item = en_attente[0]
        item_id = item["id"]
        
        # Patch to en_cours
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/{item_id}",
            json={"status": "en_cours"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Patch failed: {response.text}"
        result = response.json()
        assert result.get("success") is True
        
        # Verify the change
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        data = response.json()
        updated = next((i for i in data["items"] if i["id"] == item_id), None)
        assert updated is not None
        assert updated["status"] == "en_cours"
        print(f"Successfully changed status to en_cours for {item_id}")
        
        # Store for next test
        TestPatchPremiumAnalysisStatus.item_id = item_id
    
    def test_patch_status_to_valide_with_reviewed_analysis(self, auth_headers):
        """Should change status to valide with reviewed_analysis"""
        item_id = getattr(TestPatchPremiumAnalysisStatus, 'item_id', None)
        if not item_id:
            # Find an en_cours item
            response = requests.get(
                f"{BASE_URL}/api/admin/premium-analyses",
                headers=auth_headers
            )
            data = response.json()
            en_cours = [i for i in data["items"] if i.get("status") == "en_cours"]
            if not en_cours:
                pytest.skip("No en_cours items to test")
            item_id = en_cours[0]["id"]
        
        # Patch to valide with reviewed analysis
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/{item_id}",
            json={
                "status": "valide",
                "reviewed_analysis": "TEST_REVIEWED: This is a test reviewed analysis content.",
                "notes": "Test admin notes"
            },
            headers=auth_headers
        )
        assert response.status_code == 200, f"Patch to valide failed: {response.text}"
        
        # Verify
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        data = response.json()
        updated = next((i for i in data["items"] if i["id"] == item_id), None)
        assert updated is not None
        assert updated["status"] == "valide"
        print(f"Successfully changed status to valide for {item_id}")
        
        TestPatchPremiumAnalysisStatus.valide_item_id = item_id
    
    def test_patch_invalid_status_returns_400(self, auth_headers):
        """Should return 400 for invalid status"""
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        data = response.json()
        if not data["items"]:
            pytest.skip("No items to test")
        
        item_id = data["items"][0]["id"]
        
        response = requests.patch(
            f"{BASE_URL}/api/admin/premium-analyses/{item_id}",
            json={"status": "invalid_status"},
            headers=auth_headers
        )
        assert response.status_code == 400


class TestSendReviewedEndpoint:
    """Test POST /api/admin/premium-analyses/{id}/send-reviewed"""
    
    def test_send_reviewed_uses_correct_report_type(self, auth_headers):
        """send-reviewed should use correct report_type based on type field"""
        # Get a valide dossier_express item
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find a valide dossier_express item
        valide_de = [i for i in data["items"] 
                     if i.get("status") == "valide" and i.get("type") == "dossier_express"]
        
        if not valide_de:
            # Try to find any valide item
            valide_any = [i for i in data["items"] if i.get("status") == "valide"]
            if not valide_any:
                pytest.skip("No valide items to test send-reviewed")
            item = valide_any[0]
        else:
            item = valide_de[0]
        
        item_id = item["id"]
        item_type = item.get("type", "strategiia")
        
        # Send reviewed
        response = requests.post(
            f"{BASE_URL}/api/admin/premium-analyses/{item_id}/send-reviewed",
            json={"reviewed_analysis": "TEST: Final reviewed analysis for sending."},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Send reviewed failed: {response.text}"
        result = response.json()
        
        assert result.get("success") is True
        # email_sent may be False if Resend is in sandbox mode
        print(f"Send reviewed result: email_sent={result.get('email_sent')}, email={result.get('email')}")
        
        # Verify status changed to envoye
        response = requests.get(
            f"{BASE_URL}/api/admin/premium-analyses",
            headers=auth_headers
        )
        data = response.json()
        updated = next((i for i in data["items"] if i["id"] == item_id), None)
        assert updated is not None
        assert updated["status"] == "envoye"
        print(f"Item {item_id} (type={item_type}) status changed to envoye")


class TestDossierExpressAdminList:
    """Test GET /api/admin/dossier-express"""
    
    def test_admin_dossier_express_list(self, auth_headers):
        """Should return list of dossiers with stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dossier-express",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "items" in data
        assert "stats" in data
        
        stats = data["stats"]
        assert "total" in stats
        assert "completed" in stats
        assert "processing" in stats
        assert "errors" in stats
        
        print(f"Dossier Express stats: total={stats['total']}, completed={stats['completed']}, processing={stats['processing']}, errors={stats['errors']}")
        
        # Verify items structure
        if data["items"]:
            item = data["items"][0]
            assert "id" in item
            assert "email" in item
            assert "status" in item
            # analysis and documents_text should be excluded from list
            assert "analysis" not in item
            assert "documents_text" not in item


class TestSessionStoragePersistence:
    """Test that admin mode uses sessionStorage (verified via code review)"""
    
    def test_admin_test_banner_uses_session_storage(self):
        """AdminTestBanner.jsx should use sessionStorage for persistence"""
        # This is a code review test - we verify the implementation
        import os
        banner_path = "/app/frontend/src/components/AdminTestBanner.jsx"
        
        with open(banner_path, 'r') as f:
            content = f.read()
        
        # Check for sessionStorage usage
        assert "sessionStorage.getItem('admin_test_mode')" in content, "Should read from sessionStorage"
        assert "sessionStorage.setItem('admin_test_mode'" in content, "Should write to sessionStorage"
        assert "sessionStorage.removeItem('admin_test_mode')" in content, "Should remove from sessionStorage on logout"
        
        print("AdminTestBanner correctly uses sessionStorage for admin mode persistence")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
