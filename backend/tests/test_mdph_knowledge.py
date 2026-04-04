"""
Test suite for MDPH Knowledge Base (mdph_knowledge.py)
Tests:
- detect_mdph_context() for all MDPH subtypes (AAH, PCH, RQTH, CMI, invalidité, maladies invalidantes)
- detect_mdph_context() returns None for non-MDPH texts
- get_mdph_context() returns valid content for each demande_type
- Legal references in output (L.821-1, L.245-1, L.5213-1, etc.)
- Backend imports verification in strategiia.py and dossier_express.py
- Regression check: contestation_knowledge still works
"""
import pytest
import requests
import os
import sys

# Add backend to path for direct imports
sys.path.insert(0, '/app/backend')

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ============================================================================
# UNIT TESTS: detect_mdph_context()
# ============================================================================

class TestDetectMdphContext:
    """Test detect_mdph_context() keyword detection for all MDPH subtypes"""
    
    def test_detect_aah_keywords(self):
        """AAH keywords should return 'aah'"""
        from constants.mdph_knowledge import detect_mdph_context
        
        aah_texts = [
            "Je souhaite demander l'AAH",
            "allocation adulte handicapé",
            "allocation aux adultes handicapés",
            "déconjugalisation de l'AAH",
            "majoration vie autonome",
            "MVA handicap",
            "RSDAE restriction substantielle",
            "restriction substantielle et durable pour l'accès à l'emploi",
        ]
        
        for text in aah_texts:
            result = detect_mdph_context(text)
            assert result == "aah", f"Expected 'aah' for text: '{text}', got: {result}"
        print(f"PASS: All {len(aah_texts)} AAH keywords detected correctly")
    
    def test_detect_pch_keywords(self):
        """PCH keywords should return 'pch'"""
        from constants.mdph_knowledge import detect_mdph_context
        
        pch_texts = [
            "demande de PCH",
            "prestation de compensation du handicap",
            "prestation compensation handicap",
            "aide humaine PCH",
            "aides humaines handicap",
            "aménagement logement handicap",
            "aménagement véhicule handicap",
            "tierce personne handicap",
            "aidant familial PCH",
        ]
        
        for text in pch_texts:
            result = detect_mdph_context(text)
            assert result == "pch", f"Expected 'pch' for text: '{text}', got: {result}"
        print(f"PASS: All {len(pch_texts)} PCH keywords detected correctly")
    
    def test_detect_rqth_keywords(self):
        """RQTH keywords should return 'rqth'"""
        from constants.mdph_knowledge import detect_mdph_context
        
        rqth_texts = [
            "demande de RQTH",
            "reconnaissance travailleur handicapé",
            "qualité travailleur handicapé",
            "travailleur handicapé emploi",
            "AGEFIPH aide",
            "FIPHFP fonction publique",
            "Cap Emploi handicap",
            "obligation emploi handicapé",
            "OETH entreprise",
            "aménagement poste handicap",
        ]
        
        for text in rqth_texts:
            result = detect_mdph_context(text)
            assert result == "rqth", f"Expected 'rqth' for text: '{text}', got: {result}"
        print(f"PASS: All {len(rqth_texts)} RQTH keywords detected correctly")
    
    def test_detect_cmi_keywords(self):
        """CMI keywords should return 'cmi'"""
        from constants.mdph_knowledge import detect_mdph_context
        
        cmi_texts = [
            "carte mobilité inclusion",
            "CMI invalidité",
            "CMI priorité",
            "CMI stationnement",
            "carte invalidité handicap",
            "carte stationnement handicap",
        ]
        
        for text in cmi_texts:
            result = detect_mdph_context(text)
            assert result == "cmi", f"Expected 'cmi' for text: '{text}', got: {result}"
        print(f"PASS: All {len(cmi_texts)} CMI keywords detected correctly")
    
    def test_detect_invalidite_keywords(self):
        """Invalidité keywords should return 'invalidite'"""
        from constants.mdph_knowledge import detect_mdph_context
        
        # Pure invalidité keywords (no AAH overlap)
        invalidite_texts = [
            "pension invalidité catégorie 2",
            "pension d'invalidité",
            "invalidité catégorie 1",
            "invalide catégorie 3",
        ]
        
        for text in invalidite_texts:
            result = detect_mdph_context(text)
            assert result == "invalidite", f"Expected 'invalidite' for text: '{text}', got: {result}"
        
        # Note: "cumul AAH pension" returns 'aah' because AAH keywords are checked first
        # This is by design - the detection prioritizes more specific keywords
        cumul_aah_result = detect_mdph_context("cumul AAH pension")
        assert cumul_aah_result == "aah", "cumul AAH pension should match AAH first"
        
        print(f"PASS: All {len(invalidite_texts)} invalidité keywords detected correctly")
    
    def test_detect_maladie_invalidante_keywords(self):
        """Maladie invalidante keywords should return 'maladie_invalidante'"""
        from constants.mdph_knowledge import detect_mdph_context
        
        maladie_texts = [
            "maladie invalidante MDPH",
            "maladies invalidantes reconnaissance",
            "fibromyalgie MDPH",
            "sclérose en plaques MDPH",
            "SEP MDPH",
            "Crohn MDPH",
            "épilepsie MDPH",
            "endométriose MDPH",
            "fatigue chronique MDPH",
            "handicap invisible",
        ]
        
        for text in maladie_texts:
            result = detect_mdph_context(text)
            assert result == "maladie_invalidante", f"Expected 'maladie_invalidante' for text: '{text}', got: {result}"
        print(f"PASS: All {len(maladie_texts)} maladie invalidante keywords detected correctly")
    
    def test_detect_general_mdph_keywords(self):
        """General MDPH keywords should return 'general'"""
        from constants.mdph_knowledge import detect_mdph_context
        
        general_texts = [
            "dossier MDPH",
            "demande MDPH",
            "maison départementale des personnes handicapées",
            "CDAPH décision",
            "commission des droits",
            "équipe pluridisciplinaire MDPH",
            "plan personnalisé de compensation",
            "PPC handicap",
            "Cerfa 15692",
            "Cerfa 15695",
            "projet de vie MDPH",
            "projet de vie handicap",
            "renouvellement MDPH",
            "recours MDPH",
            "RAPO MDPH",
            "contestation MDPH",
        ]
        
        for text in general_texts:
            result = detect_mdph_context(text)
            assert result == "general", f"Expected 'general' for text: '{text}', got: {result}"
        print(f"PASS: All {len(general_texts)} general MDPH keywords detected correctly")
    
    def test_detect_none_for_non_mdph_texts(self):
        """Non-MDPH texts should return None"""
        from constants.mdph_knowledge import detect_mdph_context
        
        non_mdph_texts = [
            "accident du travail CPAM",
            "maladie professionnelle tableau",
            "RATP agent",
            "CCAS contestation",
            "assurance ITT",
            "Generali contrat",
            "licenciement abusif",
            "prud'hommes",
            "retraite anticipée",
            "chômage ARE",
            "RSA demande",
            "prime d'activité",
            "",  # Empty string
            "bonjour",  # Generic text
        ]
        
        for text in non_mdph_texts:
            result = detect_mdph_context(text)
            assert result is None, f"Expected None for non-MDPH text: '{text}', got: {result}"
        print(f"PASS: All {len(non_mdph_texts)} non-MDPH texts correctly return None")
    
    def test_unicode_normalization(self):
        """Test that accented characters are handled correctly"""
        from constants.mdph_knowledge import detect_mdph_context
        
        # Test with accents
        assert detect_mdph_context("déconjugalisation") == "aah"
        assert detect_mdph_context("DÉCONJUGALISATION") == "aah"
        assert detect_mdph_context("préstation de compensation") == "pch"
        assert detect_mdph_context("épilepsie MDPH") == "maladie_invalidante"
        print("PASS: Unicode normalization works correctly")


# ============================================================================
# UNIT TESTS: get_mdph_context()
# ============================================================================

class TestGetMdphContext:
    """Test get_mdph_context() returns valid content for each demande_type"""
    
    def test_get_context_aah(self):
        """get_mdph_context('aah') should return AAH-specific content"""
        from constants.mdph_knowledge import get_mdph_context
        
        context = get_mdph_context(demande_type="aah")
        
        assert context is not None
        assert len(context) > 1000, f"Context too short: {len(context)} chars"
        assert "AAH" in context
        assert "L.821-1" in context, "Missing legal reference L.821-1"
        assert "allocation" in context.lower()
        assert "déconjugalisation" in context.lower() or "deconjugalisation" in context.lower()
        print(f"PASS: get_mdph_context('aah') returns {len(context)} chars with AAH content")
    
    def test_get_context_pch(self):
        """get_mdph_context('pch') should return PCH-specific content"""
        from constants.mdph_knowledge import get_mdph_context
        
        context = get_mdph_context(demande_type="pch")
        
        assert context is not None
        assert len(context) > 1000
        assert "PCH" in context
        assert "L.245-1" in context, "Missing legal reference L.245-1"
        assert "compensation" in context.lower()
        assert "aide" in context.lower()
        print(f"PASS: get_mdph_context('pch') returns {len(context)} chars with PCH content")
    
    def test_get_context_rqth(self):
        """get_mdph_context('rqth') should return RQTH-specific content"""
        from constants.mdph_knowledge import get_mdph_context
        
        context = get_mdph_context(demande_type="rqth")
        
        assert context is not None
        assert len(context) > 1000
        assert "RQTH" in context
        assert "L.5213-1" in context, "Missing legal reference L.5213-1"
        assert "travailleur" in context.lower()
        print(f"PASS: get_mdph_context('rqth') returns {len(context)} chars with RQTH content")
    
    def test_get_context_cmi(self):
        """get_mdph_context('cmi') should return CMI-specific content"""
        from constants.mdph_knowledge import get_mdph_context
        
        context = get_mdph_context(demande_type="cmi")
        
        assert context is not None
        assert len(context) > 1000
        assert "CMI" in context
        assert "carte" in context.lower() or "mobilité" in context.lower() or "mobilite" in context.lower()
        print(f"PASS: get_mdph_context('cmi') returns {len(context)} chars with CMI content")
    
    def test_get_context_invalidite(self):
        """get_mdph_context('invalidite') should return pension invalidité content"""
        from constants.mdph_knowledge import get_mdph_context
        
        context = get_mdph_context(demande_type="invalidite")
        
        assert context is not None
        assert len(context) > 1000
        assert "invalidité" in context.lower() or "invalidite" in context.lower()
        assert "catégorie" in context.lower() or "categorie" in context.lower()
        assert "L.341-1" in context, "Missing legal reference L.341-1"
        print(f"PASS: get_mdph_context('invalidite') returns {len(context)} chars with invalidité content")
    
    def test_get_context_general(self):
        """get_mdph_context('general') should return general MDPH content"""
        from constants.mdph_knowledge import get_mdph_context
        
        context = get_mdph_context(demande_type="general")
        
        assert context is not None
        assert len(context) > 2000
        assert "MDPH" in context
        assert "CDAPH" in context
        assert "RAPO" in context or "recours" in context.lower()
        print(f"PASS: get_mdph_context('general') returns {len(context)} chars with general MDPH content")
    
    def test_get_context_none_returns_full(self):
        """get_mdph_context(None) should return full comprehensive content"""
        from constants.mdph_knowledge import get_mdph_context
        
        context = get_mdph_context(demande_type=None)
        
        assert context is not None
        assert len(context) > 5000, f"Full context too short: {len(context)} chars"
        
        # Should contain all sections
        assert "AAH" in context
        assert "PCH" in context
        assert "RQTH" in context
        assert "CMI" in context
        assert "invalidité" in context.lower() or "invalidite" in context.lower()
        assert "RAPO" in context
        print(f"PASS: get_mdph_context(None) returns {len(context)} chars with full content")
    
    def test_legal_references_present(self):
        """Verify key legal references are present in full context"""
        from constants.mdph_knowledge import get_mdph_context
        
        context = get_mdph_context(demande_type=None)
        
        legal_refs = [
            "L.821-1",   # AAH conditions
            "L.245-1",   # PCH conditions
            "L.5213-1",  # RQTH definition
            "L.341-1",   # Pension invalidité
        ]
        
        for ref in legal_refs:
            assert ref in context, f"Missing legal reference: {ref}"
        
        print(f"PASS: All {len(legal_refs)} key legal references present in context")


# ============================================================================
# REGRESSION TESTS: contestation_knowledge still works
# ============================================================================

class TestContestationKnowledgeRegression:
    """Regression tests to ensure contestation_knowledge.py still works"""
    
    def test_detect_contestation_ratp(self):
        """RATP keywords should still return 'ccas_ratp'"""
        from constants.contestation_knowledge import detect_contestation_context
        
        ratp_texts = [
            "agent RATP",
            "CCAS contestation",
            "CRAM de la CCAS",
            "rue Championnet",
            "régime spécial RATP",
        ]
        
        for text in ratp_texts:
            result = detect_contestation_context(text)
            assert result == "ccas_ratp", f"Expected 'ccas_ratp' for text: '{text}', got: {result}"
        print(f"PASS: RATP keywords still return 'ccas_ratp' (regression OK)")
    
    def test_detect_contestation_regime_general(self):
        """Contestation keywords should still return 'regime_general'"""
        from constants.contestation_knowledge import detect_contestation_context
        
        contestation_texts = [
            "contestation taux IPP",
            "contester le taux",
            "révision taux",
            "après consolidation",
            "maladie professionnelle",
        ]
        
        for text in contestation_texts:
            result = detect_contestation_context(text)
            assert result == "regime_general", f"Expected 'regime_general' for text: '{text}', got: {result}"
        print(f"PASS: Contestation keywords still return 'regime_general' (regression OK)")
    
    def test_get_contestation_context_works(self):
        """get_contestation_context() should still return valid content"""
        from constants.contestation_knowledge import get_contestation_context
        
        context = get_contestation_context(regime="ccas_ratp")
        assert context is not None
        assert len(context) > 1000
        assert "RATP" in context
        assert "CCAS" in context
        
        context_general = get_contestation_context(regime="regime_general")
        assert context_general is not None
        assert len(context_general) > 500
        print("PASS: get_contestation_context() still works (regression OK)")


# ============================================================================
# INTEGRATION TESTS: Backend imports verification
# ============================================================================

class TestBackendImports:
    """Verify mdph_knowledge is correctly imported in backend routes"""
    
    def test_strategiia_imports_mdph(self):
        """strategiia.py should import mdph_knowledge functions"""
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("strategiia", "/app/backend/routes/strategiia.py")
        module = importlib.util.module_from_spec(spec)
        
        # Read file content to check imports
        with open("/app/backend/routes/strategiia.py", "r") as f:
            content = f.read()
        
        assert "from constants.mdph_knowledge import" in content, "Missing mdph_knowledge import in strategiia.py"
        assert "get_mdph_context" in content, "Missing get_mdph_context in strategiia.py"
        assert "detect_mdph_context" in content, "Missing detect_mdph_context in strategiia.py"
        print("PASS: strategiia.py correctly imports mdph_knowledge functions")
    
    def test_dossier_express_imports_mdph(self):
        """dossier_express.py should import mdph_knowledge functions"""
        with open("/app/backend/routes/dossier_express.py", "r") as f:
            content = f.read()
        
        assert "from constants.mdph_knowledge import" in content, "Missing mdph_knowledge import in dossier_express.py"
        assert "get_mdph_context" in content, "Missing get_mdph_context in dossier_express.py"
        assert "detect_mdph_context" in content, "Missing detect_mdph_context in dossier_express.py"
        print("PASS: dossier_express.py correctly imports mdph_knowledge functions")
    
    def test_strategiia_mdph_injection_block(self):
        """strategiia.py should have MDPH context injection block"""
        with open("/app/backend/routes/strategiia.py", "r") as f:
            content = f.read()
        
        # Check for MDPH injection block (lines 178-188 per spec)
        assert "detect_mdph_context(situation)" in content, "Missing detect_mdph_context call in strategiia.py"
        assert "get_mdph_context(demande_type=" in content, "Missing get_mdph_context call in strategiia.py"
        assert "mdph_context" in content, "Missing mdph_context variable in strategiia.py"
        print("PASS: strategiia.py has MDPH context injection block")
    
    def test_dossier_express_mdph_injection_block(self):
        """dossier_express.py should have MDPH context injection block"""
        with open("/app/backend/routes/dossier_express.py", "r") as f:
            content = f.read()
        
        # Check for MDPH injection block (lines 269-278 per spec)
        assert "detect_mdph_context(" in content, "Missing detect_mdph_context call in dossier_express.py"
        assert "get_mdph_context(demande_type=" in content, "Missing get_mdph_context call in dossier_express.py"
        assert "mdph_context" in content, "Missing mdph_context variable in dossier_express.py"
        print("PASS: dossier_express.py has MDPH context injection block")


# ============================================================================
# API TESTS: Health endpoint
# ============================================================================

class TestHealthEndpoint:
    """Test /api/health endpoint"""
    
    def test_health_returns_healthy(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Expected 'healthy', got: {data.get('status')}"
        print(f"PASS: /api/health returns healthy status")


# ============================================================================
# Run tests if executed directly
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
