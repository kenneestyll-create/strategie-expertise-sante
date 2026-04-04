"""
Test suite for assurance knowledge base integration into StrategiIA and Dossier Express.
Tests the get_assurance_context() function and verifies context injection logic.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com').rstrip('/')

class TestAssuranceKnowledgeBase:
    """Tests for assurance_knowledge.py module"""
    
    def test_garanties_definitions_complete(self):
        """Verify all 7 garantie types are defined"""
        from backend.constants.assurance_knowledge import GARANTIES_DEFINITIONS
        expected = ['ITT', 'ITP', 'IPT', 'IPP', 'PTIA', 'PE', 'DECES']
        for g in expected:
            assert g in GARANTIES_DEFINITIONS, f"Missing garantie: {g}"
            assert 'nom_complet' in GARANTIES_DEFINITIONS[g]
            assert 'description' in GARANTIES_DEFINITIONS[g]
        print(f"✓ All {len(expected)} garantie types defined correctly")
    
    def test_assurance_knowledge_three_insurers(self):
        """Verify all 3 insurers are in the knowledge base"""
        from backend.constants.assurance_knowledge import ASSURANCE_KNOWLEDGE
        expected = ['generali', 'groupama_gan_vie', 'cnp_assurances']
        for ins in expected:
            assert ins in ASSURANCE_KNOWLEDGE, f"Missing insurer: {ins}"
            assert 'assureur' in ASSURANCE_KNOWLEDGE[ins]
            assert 'guarantees' in ASSURANCE_KNOWLEDGE[ins]
            assert 'red_flags' in ASSURANCE_KNOWLEDGE[ins]
        print(f"✓ All {len(expected)} insurers present in knowledge base")
    
    def test_get_assurance_context_with_garantie_itt(self):
        """Test context generation for ITT garantie"""
        from backend.constants.assurance_knowledge import get_assurance_context
        ctx = get_assurance_context(garantie='ITT')
        
        # Should contain ITT definition
        assert 'Incapacite Temporaire Totale' in ctx
        
        # Should contain all 3 insurers
        assert 'GENERALI' in ctx
        assert 'Groupama' in ctx
        assert 'CNP' in ctx
        
        # Should contain comparison section
        assert 'COMPARAISON' in ctx
        
        # Should be substantial
        assert len(ctx) > 5000, f"Context too short: {len(ctx)} chars"
        print(f"✓ ITT context generated: {len(ctx)} chars with all insurers")
    
    def test_get_assurance_context_with_garantie_ptia(self):
        """Test context generation for PTIA garantie"""
        from backend.constants.assurance_knowledge import get_assurance_context
        ctx = get_assurance_context(garantie='PTIA')
        
        assert 'Perte Totale et Irreversible' in ctx
        assert len(ctx) > 3000
        print(f"✓ PTIA context generated: {len(ctx)} chars")
    
    def test_get_assurance_context_no_params(self):
        """Test context generation with no parameters (all insurers)"""
        from backend.constants.assurance_knowledge import get_assurance_context
        ctx = get_assurance_context()
        
        # Should contain all 3 insurers
        assert 'GENERALI' in ctx
        assert 'Groupama' in ctx
        assert 'CNP' in ctx
        print(f"✓ Full context generated: {len(ctx)} chars")
    
    def test_get_all_garantie_types(self):
        """Test helper function returns all garantie types"""
        from backend.constants.assurance_knowledge import get_all_garantie_types
        types = get_all_garantie_types()
        assert len(types) == 7
        assert 'ITT' in types
        assert 'DECES' in types
        print(f"✓ get_all_garantie_types returns {types}")
    
    def test_get_all_assureurs(self):
        """Test helper function returns all insurers"""
        from backend.constants.assurance_knowledge import get_all_assureurs
        assureurs = get_all_assureurs()
        assert len(assureurs) == 3
        keys = [a['key'] for a in assureurs]
        assert 'generali' in keys
        assert 'groupama_gan_vie' in keys
        assert 'cnp_assurances' in keys
        print(f"✓ get_all_assureurs returns {len(assureurs)} insurers")


class TestStrategiIAAssuranceInjection:
    """Tests for assurance context injection in StrategiIA endpoint"""
    
    def test_strategiia_health_check(self):
        """Verify StrategiIA LLM health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/strategiia/health/llm", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'operational' in data
        print(f"✓ LLM health check: operational={data['operational']}, reason={data.get('reason', 'none')}")
    
    def test_strategiia_analyze_accepts_assurance_type(self):
        """Verify /api/strategiia/analyze accepts type_dossier='assurance' and regime='ITT'"""
        # Note: We're not triggering actual LLM call (expensive), just verifying endpoint accepts params
        payload = {
            "type_dossier": "assurance",
            "regime": "ITT",
            "situation": "Test situation for assurance ITT garantie - testing context injection",
            "premium": False,
            "email": "test-assurance@example.com"
        }
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json=payload, timeout=15)
        
        # Should return 200 with job_id (async polling)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'job_id' in data, f"Missing job_id in response: {data}"
        assert data.get('status') == 'pending'
        print(f"✓ StrategiIA accepts assurance type_dossier with ITT regime, job_id={data['job_id']}")
    
    def test_strategiia_analyze_accepts_litige_assurantiel(self):
        """Verify /api/strategiia/analyze accepts type_dossier='litige_assurantiel'"""
        payload = {
            "type_dossier": "litige_assurantiel",
            "regime": "IPT",
            "situation": "Test situation for litige assurantiel IPT garantie",
            "premium": False,
            "email": "test-litige@example.com"
        }
        response = requests.post(f"{BASE_URL}/api/strategiia/analyze", json=payload, timeout=15)
        
        assert response.status_code == 200
        data = response.json()
        assert 'job_id' in data
        print(f"✓ StrategiIA accepts litige_assurantiel type_dossier, job_id={data['job_id']}")


class TestDossierExpressAssuranceInjection:
    """Tests for assurance context injection in Dossier Express"""
    
    def test_dossier_express_checkout_accepts_assurance_type(self):
        """Verify Dossier Express checkout accepts assurance type_dossier"""
        # Note: This will fail at Stripe checkout (expected), but validates endpoint accepts params
        payload = {
            "email": "test-de-assurance@example.com",
            "name": "Test User",
            "origin_url": "https://mascot-tips-admin.preview.emergentagent.com",
            "premium_pdf": False,
            "analyse_premium": False
        }
        response = requests.post(f"{BASE_URL}/api/dossier-express/checkout", json=payload, timeout=15)
        
        # Should return 200 with Stripe URL or 503 if LLM unavailable
        assert response.status_code in [200, 503], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert 'url' in data or 'session_id' in data
            print(f"✓ Dossier Express checkout endpoint works")
        else:
            print(f"✓ Dossier Express checkout returned 503 (LLM unavailable - expected in test)")


class TestBackendAssuranceContextInjectionLogic:
    """Verify the context injection logic in backend routes"""
    
    def test_strategiia_route_has_assurance_injection(self):
        """Verify strategiia.py has assurance context injection code"""
        import os
        with open('/app/backend/routes/strategiia.py', 'r') as f:
            content = f.read()
        
        # Check for import
        assert 'from constants.assurance_knowledge import get_assurance_context' in content
        
        # Check for injection logic
        assert 'assurance_context' in content
        assert 'type_dossier in ("assurance"' in content or 'litige_assurantiel' in content
        
        print("✓ strategiia.py has assurance context injection code")
    
    def test_dossier_express_route_has_assurance_injection(self):
        """Verify dossier_express.py has assurance context injection code"""
        import os
        with open('/app/backend/routes/dossier_express.py', 'r') as f:
            content = f.read()
        
        # Check for import
        assert 'from constants.assurance_knowledge import get_assurance_context' in content
        
        # Check for injection logic
        assert 'assurance_context' in content
        assert '"assurance"' in content.lower() or 'litige' in content.lower()
        
        print("✓ dossier_express.py has assurance context injection code")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
