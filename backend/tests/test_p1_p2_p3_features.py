"""
Test P1, P2, P3 Features - Iteration 51
P1: Client progress dashboard - enriched data with document_status, missing_documents, completeness_pct, next_actions
P2: Dossier quality score in StrategiIA modal - POST /api/strategiia/dossier-score
P3: Admin analytics tab - enriched with service_utilization and new KPIs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestP2DossierScore:
    """P2: Test POST /api/strategiia/dossier-score endpoint"""
    
    def test_dossier_score_basic(self):
        """Test dossier score with basic input"""
        response = requests.post(f"{BASE_URL}/api/strategiia/dossier-score", json={
            "type_dossier": "at",
            "regime": "general",
            "situation": "J'ai eu un accident du travail le 15 janvier 2025 en tombant dans un escalier au bureau. J'ai été arrêté pendant 3 semaines.",
            "doc_count": 2,
            "doc_names": ["certificat_medical.pdf", "declaration_at.pdf"]
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify score structure
        assert "score" in data, "Missing 'score' field"
        assert "level" in data, "Missing 'level' field"
        assert "level_label" in data, "Missing 'level_label' field"
        assert "level_color" in data, "Missing 'level_color' field"
        assert "details" in data, "Missing 'details' field"
        assert "tips" in data, "Missing 'tips' field"
        
        # Verify score is between 0 and 100
        assert 0 <= data["score"] <= 100, f"Score {data['score']} not in range 0-100"
        
        # Verify details breakdown
        details = data["details"]
        assert "completeness" in details, "Missing completeness in details"
        assert "coherence" in details, "Missing coherence in details"
        assert "key_documents" in details, "Missing key_documents in details"
        
        # Each detail should have score and label
        for key in ["completeness", "coherence", "key_documents"]:
            assert "score" in details[key], f"Missing score in {key}"
            assert "label" in details[key], f"Missing label in {key}"
        
        print(f"✓ Dossier score: {data['score']}/100 - {data['level_label']}")
        print(f"  Details: completeness={details['completeness']['score']}, coherence={details['coherence']['score']}, key_docs={details['key_documents']['score']}")
    
    def test_dossier_score_minimal(self):
        """Test dossier score with minimal input"""
        response = requests.post(f"{BASE_URL}/api/strategiia/dossier-score", json={
            "type_dossier": "mp",
            "regime": "",
            "situation": "test",
            "doc_count": 0,
            "doc_names": []
        })
        assert response.status_code == 200
        data = response.json()
        
        # Score should be low with minimal input
        assert data["score"] < 60, f"Score should be low with minimal input, got {data['score']}"
        assert data["level_color"] in ["orange", "red"], f"Level color should be orange/red for low score"
        assert len(data.get("tips", [])) > 0, "Should have tips for improvement"
        
        print(f"✓ Minimal input score: {data['score']}/100 - Tips provided: {len(data['tips'])}")
    
    def test_dossier_score_complete(self):
        """Test dossier score with complete input"""
        response = requests.post(f"{BASE_URL}/api/strategiia/dossier-score", json={
            "type_dossier": "at",
            "regime": "general",
            "situation": """J'ai subi un accident du travail le 12 mars 2024 alors que je travaillais sur un chantier comme maçon depuis 8 ans pour l'entreprise BTP Construction.
            L'accident s'est produit lorsque l'échafaudage sur lequel je me trouvais s'est effondré, provoquant une chute de 4 mètres.
            J'ai été transporté aux urgences où un diagnostic de fracture du fémur gauche et de deux côtes a été établi.
            J'ai été arrêté 6 mois et j'ai des séquelles permanentes (boiterie, douleurs chroniques).
            La CPAM a reconnu l'AT mais propose un taux d'IPP de seulement 8% que je conteste.""",
            "doc_count": 5,
            "doc_names": ["certificat_medical_initial.pdf", "declaration_at.pdf", "arret_travail.pdf", "notification_cpam.pdf", "bulletins_salaire.pdf"]
        })
        assert response.status_code == 200
        data = response.json()
        
        # Score should be high with complete input
        assert data["score"] >= 60, f"Score should be high with complete input, got {data['score']}"
        
        print(f"✓ Complete input score: {data['score']}/100 - {data['level_label']}")


class TestP1ClientProgress:
    """P1: Test GET /api/client/progress endpoint"""
    
    @pytest.fixture
    def client_token(self):
        """Login as client and get token"""
        response = requests.post(f"{BASE_URL}/api/client/login", json={
            "email": "demo@test.com",
            "password": "Demo1234!"
        })
        if response.status_code != 200:
            pytest.skip("Client login failed - user may not exist")
        return response.json().get("access_token")
    
    def test_client_progress_enriched(self, client_token):
        """Test client progress returns enriched data"""
        response = requests.get(f"{BASE_URL}/api/client/progress", headers={
            "Authorization": f"Bearer {client_token}"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # P1: Verify new fields exist
        assert "progress_pct" in data, "Missing progress_pct"
        assert "steps" in data, "Missing steps"
        assert "counts" in data, "Missing counts"
        
        # P1 enriched fields
        assert "document_status" in data, "Missing document_status (P1 feature)"
        assert "missing_documents" in data, "Missing missing_documents (P1 feature)"
        assert "completeness_pct" in data, "Missing completeness_pct (P1 feature)"
        assert "next_actions" in data, "Missing next_actions (P1 feature)"
        
        # Verify document_status structure
        doc_status = data["document_status"]
        assert "total" in doc_status, "Missing total in document_status"
        assert "valide" in doc_status, "Missing valide in document_status"
        assert "en_attente" in doc_status, "Missing en_attente in document_status"
        assert "illisible" in doc_status, "Missing illisible in document_status"
        
        # Verify next_actions structure
        next_actions = data["next_actions"]
        assert isinstance(next_actions, list), "next_actions should be a list"
        
        if len(next_actions) > 0:
            action = next_actions[0]
            assert "step_id" in action or "label" in action, "Next action should have step_id or label"
        
        print(f"✓ Client progress enriched:")
        print(f"  Progress: {data['progress_pct']}%, Completeness: {data['completeness_pct']}%")
        print(f"  Documents: total={doc_status['total']}, validated={doc_status['valide']}, pending={doc_status['en_attente']}")
        print(f"  Missing documents: {len(data['missing_documents'])}")
        print(f"  Next actions: {len(next_actions)}")
    
    def test_client_progress_steps_timeline(self, client_token):
        """Test client progress steps timeline structure"""
        response = requests.get(f"{BASE_URL}/api/client/progress", headers={
            "Authorization": f"Bearer {client_token}"
        })
        assert response.status_code == 200
        data = response.json()
        
        steps = data["steps"]
        assert len(steps) >= 4, f"Should have at least 4 steps, got {len(steps)}"
        
        # Verify each step has required fields
        for step in steps:
            assert "id" in step, "Step missing 'id'"
            assert "label" in step, "Step missing 'label'"
            assert "status" in step, "Step missing 'status'"
            assert step["status"] in ["completed", "in_progress", "action_required", "not_started"], f"Invalid status: {step['status']}"
        
        print(f"✓ Steps timeline: {[s['id'] for s in steps]}")


class TestP3AdminAnalytics:
    """P3: Test GET /api/admin/analytics endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Login as admin and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json().get("access_token")
    
    def test_admin_analytics_enriched(self, admin_token):
        """Test admin analytics returns enriched data with service_utilization"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics?period=30d", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Basic fields
        assert "kpis" in data, "Missing kpis"
        assert "time_series" in data, "Missing time_series"
        assert "packages" in data, "Missing packages"
        assert "analyse_types" in data, "Missing analyse_types"
        
        # P3: service_utilization
        assert "service_utilization" in data, "Missing service_utilization (P3 feature)"
        
        service_util = data["service_utilization"]
        assert "strategiia" in service_util, "Missing strategiia in service_utilization"
        assert "dossier_express" in service_util, "Missing dossier_express in service_utilization"
        assert "premium" in service_util, "Missing premium in service_utilization"
        assert "chatbot" in service_util, "Missing chatbot in service_utilization"
        
        # Each service should have total, this_month, label
        for svc_name, svc_data in service_util.items():
            assert "total" in svc_data, f"Missing total in {svc_name}"
            assert "this_month" in svc_data, f"Missing this_month in {svc_name}"
            assert "label" in svc_data, f"Missing label in {svc_name}"
        
        print(f"✓ Service utilization:")
        for svc_name, svc_data in service_util.items():
            print(f"  {svc_data['label']}: {svc_data['total']} total, {svc_data['this_month']} this month")
    
    def test_admin_analytics_extra_kpis(self, admin_token):
        """Test admin analytics returns extra KPIs"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics?period=30d", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        
        kpis = data["kpis"]
        
        # P3: Extra KPIs
        assert "active_dossiers" in kpis, "Missing active_dossiers KPI (P3 feature)"
        assert "total_documents" in kpis, "Missing total_documents KPI (P3 feature)"
        assert "pending_documents" in kpis, "Missing pending_documents KPI (P3 feature)"
        assert "analyses_this_month" in kpis, "Missing analyses_this_month KPI (P3 feature)"
        assert "dossiers_this_month" in kpis, "Missing dossiers_this_month KPI (P3 feature)"
        
        print(f"✓ Extra KPIs:")
        print(f"  Active dossiers: {kpis['active_dossiers']}")
        print(f"  Documents: {kpis['total_documents']} total, {kpis['pending_documents']} pending")
        print(f"  This month: {kpis['analyses_this_month']} analyses, {kpis['dossiers_this_month']} dossiers")
    
    def test_admin_analytics_period_filter(self, admin_token):
        """Test analytics period filter works"""
        for period in ["7d", "30d", "90d"]:
            response = requests.get(f"{BASE_URL}/api/admin/analytics?period={period}", headers={
                "Authorization": f"Bearer {admin_token}"
            })
            assert response.status_code == 200, f"Period {period} failed"
            data = response.json()
            assert len(data["time_series"]) > 0, f"Time series empty for {period}"
        
        print("✓ All period filters work (7d, 30d, 90d)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
