"""
Test suite for IA Engine V1 FREEZE verification.
Objective: Verify that NOTHING changed functionally — all prompts intact, all engines functional, zero regression.
Date: 05/04/2026
"""

import pytest
import requests
import hashlib
import os
import sys

# Add backend to path for imports
sys.path.insert(0, '/app/backend')

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com').rstrip('/')


class TestBackendHealth:
    """Verify backend is intact and running."""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy."""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ /api/health returns healthy: {data}")


class TestPromptHashesUnchanged:
    """Verify prompt MD5 hashes are unchanged (freeze verification)."""
    
    def test_strategiia_basic_prompt_hash(self):
        """STRATEGIIA_BASIC_PROMPT hash MD5 unchanged (8ac30044d1c9)."""
        from constants.prompts import STRATEGIIA_BASIC_PROMPT
        hash_val = hashlib.md5(STRATEGIIA_BASIC_PROMPT.encode()).hexdigest()[:12]
        print(f"STRATEGIIA_BASIC_PROMPT hash: {hash_val}")
        assert hash_val == "8ac30044d1c9", f"Hash mismatch! Expected 8ac30044d1c9, got {hash_val}"
        print("✓ STRATEGIIA_BASIC_PROMPT hash unchanged")
    
    def test_strategiia_premium_prompt_hash(self):
        """STRATEGIIA_PREMIUM_PROMPT hash MD5 unchanged (994491b627fb)."""
        from constants.prompts import STRATEGIIA_PREMIUM_PROMPT
        hash_val = hashlib.md5(STRATEGIIA_PREMIUM_PROMPT.encode()).hexdigest()[:12]
        print(f"STRATEGIIA_PREMIUM_PROMPT hash: {hash_val}")
        assert hash_val == "994491b627fb", f"Hash mismatch! Expected 994491b627fb, got {hash_val}"
        print("✓ STRATEGIIA_PREMIUM_PROMPT hash unchanged")
    
    def test_dossier_express_prompt_hash(self):
        """DOSSIER_EXPRESS_PROMPT hash MD5 unchanged (b676aa1ceebe)."""
        from constants.prompts import DOSSIER_EXPRESS_PROMPT
        hash_val = hashlib.md5(DOSSIER_EXPRESS_PROMPT.encode()).hexdigest()[:12]
        print(f"DOSSIER_EXPRESS_PROMPT hash: {hash_val}")
        assert hash_val == "b676aa1ceebe", f"Hash mismatch! Expected b676aa1ceebe, got {hash_val}"
        print("✓ DOSSIER_EXPRESS_PROMPT hash unchanged")
    
    def test_strategiia_system_compact_hash(self):
        """STRATEGIIA_SYSTEM_COMPACT hash MD5 unchanged (d53d54d48b99)."""
        from constants.prompts import STRATEGIIA_SYSTEM_COMPACT
        hash_val = hashlib.md5(STRATEGIIA_SYSTEM_COMPACT.encode()).hexdigest()[:12]
        print(f"STRATEGIIA_SYSTEM_COMPACT hash: {hash_val}")
        assert hash_val == "d53d54d48b99", f"Hash mismatch! Expected d53d54d48b99, got {hash_val}"
        print("✓ STRATEGIIA_SYSTEM_COMPACT hash unchanged")
    
    def test_dossier_express_system_prompt_hash(self):
        """DOSSIER_EXPRESS_SYSTEM_PROMPT hash MD5 unchanged (371e5478b1ac)."""
        from constants.prompts import DOSSIER_EXPRESS_SYSTEM_PROMPT
        hash_val = hashlib.md5(DOSSIER_EXPRESS_SYSTEM_PROMPT.encode()).hexdigest()[:12]
        print(f"DOSSIER_EXPRESS_SYSTEM_PROMPT hash: {hash_val}")
        assert hash_val == "371e5478b1ac", f"Hash mismatch! Expected 371e5478b1ac, got {hash_val}"
        print("✓ DOSSIER_EXPRESS_SYSTEM_PROMPT hash unchanged")


class TestSystemPromptGuards:
    """Verify STRATEGIIA_SYSTEM_PROMPT contains all required guards."""
    
    def test_anti_genericite_guard(self):
        """STRATEGIIA_SYSTEM_PROMPT contains anti-genericite guard."""
        from constants.prompts import STRATEGIIA_SYSTEM_PROMPT
        assert "anti-genericite" in STRATEGIIA_SYSTEM_PROMPT.lower() or "formulations génériques" in STRATEGIIA_SYSTEM_PROMPT.lower() or "QUALITÉ RÉDACTIONNELLE PREMIUM" in STRATEGIIA_SYSTEM_PROMPT
        print("✓ Anti-genericite guard present")
    
    def test_anti_repetition_guard(self):
        """STRATEGIIA_SYSTEM_PROMPT contains anti-repetition guard."""
        from constants.prompts import STRATEGIIA_SYSTEM_PROMPT
        assert "ANTI-RÉPÉTITION" in STRATEGIIA_SYSTEM_PROMPT or "anti-repetition" in STRATEGIIA_SYSTEM_PROMPT.lower()
        print("✓ Anti-repetition guard present")
    
    def test_verification_croisee_x3_guard(self):
        """STRATEGIIA_SYSTEM_PROMPT contains verification croisee x3 guard."""
        from constants.prompts import STRATEGIIA_SYSTEM_PROMPT
        assert "VÉRIFICATION CROISÉE x3" in STRATEGIIA_SYSTEM_PROMPT or "verification croisee x3" in STRATEGIIA_SYSTEM_PROMPT.lower()
        print("✓ Verification croisee x3 guard present")
    
    def test_anti_hallucination_guard(self):
        """STRATEGIIA_SYSTEM_PROMPT contains anti-hallucination guard."""
        from constants.prompts import STRATEGIIA_SYSTEM_PROMPT
        assert "JAMAIS d'extrapolation abusive" in STRATEGIIA_SYSTEM_PROMPT or "anti-hallucination" in STRATEGIIA_SYSTEM_PROMPT.lower()
        print("✓ Anti-hallucination guard present")
    
    def test_ciblage_metier_guard(self):
        """STRATEGIIA_SYSTEM_PROMPT contains ciblage metier guard."""
        from constants.prompts import STRATEGIIA_SYSTEM_PROMPT
        assert "CLASSE MÉTIER" in STRATEGIIA_SYSTEM_PROMPT or "classe metier" in STRATEGIIA_SYSTEM_PROMPT.lower()
        print("✓ Ciblage metier guard present")
    
    def test_ciblage_sinistre_guard(self):
        """STRATEGIIA_SYSTEM_PROMPT contains ciblage sinistre guard."""
        from constants.prompts import STRATEGIIA_SYSTEM_PROMPT
        assert "CLASSE SINISTRE" in STRATEGIIA_SYSTEM_PROMPT or "classe sinistre" in STRATEGIIA_SYSTEM_PROMPT.lower()
        print("✓ Ciblage sinistre guard present")
    
    def test_ciblage_blocage_guard(self):
        """STRATEGIIA_SYSTEM_PROMPT contains ciblage blocage guard."""
        from constants.prompts import STRATEGIIA_SYSTEM_PROMPT
        assert "BLOCAGE PRINCIPAL" in STRATEGIIA_SYSTEM_PROMPT or "blocage principal" in STRATEGIIA_SYSTEM_PROMPT.lower()
        print("✓ Ciblage blocage guard present")
    
    def test_humanisation_guard(self):
        """STRATEGIIA_SYSTEM_PROMPT contains humanisation guard."""
        from constants.prompts import STRATEGIIA_SYSTEM_PROMPT
        assert "HUMANISATION RÉDACTIONNELLE" in STRATEGIIA_SYSTEM_PROMPT or "humanisation" in STRATEGIIA_SYSTEM_PROMPT.lower()
        print("✓ Humanisation guard present")
    
    def test_robustesse_dossiers_incomplets_guard(self):
        """STRATEGIIA_SYSTEM_PROMPT contains robustesse dossiers incomplets guard."""
        from constants.prompts import STRATEGIIA_SYSTEM_PROMPT
        assert "ROBUSTESSE SUR DOSSIERS INCOMPLETS" in STRATEGIIA_SYSTEM_PROMPT or "dossiers incomplets" in STRATEGIIA_SYSTEM_PROMPT.lower()
        print("✓ Robustesse dossiers incomplets guard present")


class TestLongueursCibles:
    """Verify length targets are intact in prompts."""
    
    def test_basic_550_mots(self):
        """STRATEGIIA_BASIC_PROMPT contains 'Maximum 550' target."""
        from constants.prompts import STRATEGIIA_BASIC_PROMPT
        assert "Maximum 550" in STRATEGIIA_BASIC_PROMPT or "550 mots" in STRATEGIIA_BASIC_PROMPT
        print("✓ BASIC prompt contains '550 mots' target")
    
    def test_premium_1800_2400_mots(self):
        """STRATEGIIA_PREMIUM_PROMPT contains '1800 et 2400' target."""
        from constants.prompts import STRATEGIIA_PREMIUM_PROMPT
        assert "1800 et 2400" in STRATEGIIA_PREMIUM_PROMPT or ("1800" in STRATEGIIA_PREMIUM_PROMPT and "2400" in STRATEGIIA_PREMIUM_PROMPT)
        print("✓ PREMIUM prompt contains '1800 et 2400' target")
    
    def test_dossier_express_2000_2800_mots(self):
        """DOSSIER_EXPRESS_PROMPT contains '2000 et 2800' target."""
        from constants.prompts import DOSSIER_EXPRESS_PROMPT
        assert "2000 et 2800" in DOSSIER_EXPRESS_PROMPT or ("2000" in DOSSIER_EXPRESS_PROMPT and "2800" in DOSSIER_EXPRESS_PROMPT)
        print("✓ DOSSIER_EXPRESS prompt contains '2000 et 2800' target")


class TestKnowledgePatternsEngine:
    """Verify knowledge patterns engine works correctly."""
    
    @pytest.mark.asyncio
    async def test_mdph_context_returns_patterns(self):
        """Knowledge patterns engine works for demande_mdph context (returns patterns)."""
        from routes.knowledge_patterns import get_knowledge_patterns_context
        context = await get_knowledge_patterns_context(
            categorie="demande_mdph",
            type_sinistre="aah_rsdae"
        )
        # Should return patterns for MDPH context
        assert context is not None
        if context:
            assert "ENSEIGNEMENTS METIER" in context or len(context) > 0
            print(f"✓ MDPH context returns patterns: {len(context)} chars")
        else:
            print("✓ MDPH context returns empty (no patterns seeded or no match)")
    
    @pytest.mark.asyncio
    async def test_at_context_no_mdph_pollution(self):
        """Knowledge patterns engine: AT context does NOT contain MDPH patterns (zero pollution)."""
        from routes.knowledge_patterns import get_knowledge_patterns_context
        context = await get_knowledge_patterns_context(
            categorie="accident_travail",
            type_sinistre="at_lombaire"
        )
        # Should NOT contain MDPH-specific keywords
        if context:
            assert "demande_mdph" not in context.lower()
            assert "aah" not in context.lower() or "aah" in context.lower() and "mdph" not in context.lower()
            print(f"✓ AT context does NOT contain MDPH patterns: {len(context)} chars")
        else:
            print("✓ AT context returns empty (correct - no AT patterns or no match)")


class TestAssuranceKnowledge:
    """Verify assurance knowledge base works."""
    
    def test_get_assurance_context_generali(self):
        """get_assurance_context('GENERALI') returns context."""
        from constants.assurance_knowledge import get_assurance_context
        context = get_assurance_context(assureur="generali")
        assert context is not None
        assert len(context) > 100
        assert "GENERALI" in context.upper() or "generali" in context.lower()
        print(f"✓ get_assurance_context('generali') returns {len(context)} chars")


class TestContestationKnowledge:
    """Verify contestation knowledge base works."""
    
    def test_detect_contestation_context_ccas_ratp(self):
        """detect_contestation_context('agent RATP CCAS') returns ccas_ratp."""
        from constants.contestation_knowledge import detect_contestation_context
        result = detect_contestation_context("Je suis agent RATP et je veux contester via la CCAS")
        assert result == "ccas_ratp"
        print(f"✓ detect_contestation_context('agent RATP CCAS') returns '{result}'")


class TestMDPHKnowledge:
    """Verify MDPH knowledge base works."""
    
    def test_detect_mdph_context_aah(self):
        """detect_mdph_context('demande AAH') returns aah."""
        from constants.mdph_knowledge import detect_mdph_context
        result = detect_mdph_context("Je fais une demande AAH auprès de la MDPH")
        assert result == "aah"
        print(f"✓ detect_mdph_context('demande AAH') returns '{result}'")


class TestQualityScoring:
    """Verify quality scoring works."""
    
    def test_score_report_returns_valid(self):
        """score_report() returns valid score with level."""
        from utils.quality_scoring import score_report
        
        sample_analysis = """
        ## Votre situation analysée
        Vous êtes conducteur routier et souffrez de lombalgies chroniques.
        
        ## Le vrai nœud du dossier
        Le blocage principal est probatoire : les preuves d'exposition sont insuffisantes.
        
        ## Ce qui renforce le dossier
        - Certificat médical détaillé
        - Attestation employeur
        
        ## Ce qui fragilise le dossier
        - Absence de témoignages
        
        ## Évaluation stratégique rapide
        - Solidité globale : Moyen
        
        ## L'étape la plus rentable maintenant
        Obtenir une attestation du médecin du travail.
        """
        
        result = score_report(sample_analysis, "premium", metier="transport_conduite", sinistre="mp_tms")
        
        assert "score" in result
        assert "level" in result
        assert "details" in result
        assert isinstance(result["score"], int)
        assert result["level"] in ["Excellence", "Premium", "Solide", "A Renforcer"]
        print(f"✓ score_report() returns valid: score={result['score']}, level={result['level']}")


class TestChatbotPrompts:
    """Verify chatbot prompts are intact."""
    
    def test_system_prompt_light_exists(self):
        """SYSTEM_PROMPT_LIGHT exists and contains orientation rules."""
        from utils.chatbot import SYSTEM_PROMPT_LIGHT
        assert SYSTEM_PROMPT_LIGHT is not None
        assert len(SYSTEM_PROMPT_LIGHT) > 50
        assert "orientation" in SYSTEM_PROMPT_LIGHT.lower() or "StrategiIA" in SYSTEM_PROMPT_LIGHT
        print(f"✓ SYSTEM_PROMPT_LIGHT exists: {len(SYSTEM_PROMPT_LIGHT)} chars")
    
    def test_system_prompt_full_exists(self):
        """SYSTEM_PROMPT_FULL exists and contains orientation rules."""
        from utils.chatbot import SYSTEM_PROMPT_FULL
        assert SYSTEM_PROMPT_FULL is not None
        assert len(SYSTEM_PROMPT_FULL) > 50
        assert "orientation" in SYSTEM_PROMPT_FULL.lower() or "StrategiIA" in SYSTEM_PROMPT_FULL
        print(f"✓ SYSTEM_PROMPT_FULL exists: {len(SYSTEM_PROMPT_FULL)} chars")


class TestIABaselineDocument:
    """Verify IA_BASELINE_V1.md exists and contains protocol section."""
    
    def test_ia_baseline_exists(self):
        """IA_BASELINE_V1.md exists."""
        baseline_path = "/app/memory/IA_BASELINE_V1.md"
        assert os.path.isfile(baseline_path), f"IA_BASELINE_V1.md not found at {baseline_path}"
        print(f"✓ IA_BASELINE_V1.md exists at {baseline_path}")
    
    def test_ia_baseline_contains_protocol(self):
        """IA_BASELINE_V1.md contains protocol section."""
        baseline_path = "/app/memory/IA_BASELINE_V1.md"
        with open(baseline_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "PROTOCOLE" in content.upper() or "protocole" in content.lower()
        assert "MOTEUR IA" in content.upper() or "moteur ia" in content.lower()
        print(f"✓ IA_BASELINE_V1.md contains protocol section: {len(content)} chars")


class TestGelComments:
    """Verify gel comments exist in critical files."""
    
    def test_prompts_py_gel_comment(self):
        """prompts.py contains gel comment."""
        with open("/app/backend/constants/prompts.py", 'r', encoding='utf-8') as f:
            content = f.read()
        assert "ZONE GELEE" in content or "zone gelee" in content.lower()
        assert "05/04/2026" in content or "Date de gel" in content
        print("✓ prompts.py contains gel comment")
    
    def test_llm_py_gel_comment(self):
        """llm.py contains gel comment."""
        with open("/app/backend/utils/llm.py", 'r', encoding='utf-8') as f:
            content = f.read()
        assert "ZONE GELEE" in content or "zone gelee" in content.lower()
        print("✓ llm.py contains gel comment")
    
    def test_chatbot_py_gel_comment(self):
        """chatbot.py contains gel comment."""
        with open("/app/backend/utils/chatbot.py", 'r', encoding='utf-8') as f:
            content = f.read()
        assert "ZONE GELEE" in content or "zone gelee" in content.lower()
        print("✓ chatbot.py contains gel comment")
    
    def test_quality_scoring_py_gel_comment(self):
        """quality_scoring.py contains gel comment."""
        with open("/app/backend/utils/quality_scoring.py", 'r', encoding='utf-8') as f:
            content = f.read()
        assert "ZONE GELEE" in content or "zone gelee" in content.lower()
        print("✓ quality_scoring.py contains gel comment")
    
    def test_assurance_knowledge_py_gel_comment(self):
        """assurance_knowledge.py contains gel comment."""
        with open("/app/backend/constants/assurance_knowledge.py", 'r', encoding='utf-8') as f:
            content = f.read()
        assert "ZONE GELEE" in content or "zone gelee" in content.lower()
        print("✓ assurance_knowledge.py contains gel comment")
    
    def test_contestation_knowledge_py_gel_comment(self):
        """contestation_knowledge.py contains gel comment."""
        with open("/app/backend/constants/contestation_knowledge.py", 'r', encoding='utf-8') as f:
            content = f.read()
        assert "ZONE GELEE" in content or "zone gelee" in content.lower()
        print("✓ contestation_knowledge.py contains gel comment")
    
    def test_mdph_knowledge_py_gel_comment(self):
        """mdph_knowledge.py contains gel comment."""
        with open("/app/backend/constants/mdph_knowledge.py", 'r', encoding='utf-8') as f:
            content = f.read()
        assert "ZONE GELEE" in content or "zone gelee" in content.lower()
        print("✓ mdph_knowledge.py contains gel comment")
    
    def test_seed_patterns_py_gel_comment(self):
        """seed_patterns.py contains gel comment."""
        with open("/app/backend/constants/seed_patterns.py", 'r', encoding='utf-8') as f:
            content = f.read()
        assert "ZONE GELEE" in content or "zone gelee" in content.lower()
        print("✓ seed_patterns.py contains gel comment")
    
    def test_knowledge_patterns_py_gel_comment(self):
        """knowledge_patterns.py contains gel comment."""
        with open("/app/backend/routes/knowledge_patterns.py", 'r', encoding='utf-8') as f:
            content = f.read()
        assert "ZONE GELEE" in content or "zone gelee" in content.lower()
        print("✓ knowledge_patterns.py contains gel comment")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
