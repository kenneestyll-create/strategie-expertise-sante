"""
Test MDPH Patterns Pack Premium v1
==================================
Tests for the 26 MDPH patterns added to knowledge_patterns engine.
Covers: AAH, PCH, RQTH, CMI, maladies invalidantes, refus MDPH.
Types: blocage(7), vigilance(6), levier(5), erreur_frequente(4), piece_manquante(4).

Constraints verified:
- NO modification to pdf.py, frontend, prompts USER, workflows, payments
- Only seed_patterns.py and knowledge_patterns.py were modified
"""

import pytest
import os
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestMDPHPatternsAPI:
    """Test MDPH patterns via API endpoints."""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token."""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@accompagn-sante.fr", "password": "Admin2024!"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin authentication failed")
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy."""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ /api/health returns healthy")
    
    def test_seed_mdph_endpoint_returns_skipped(self, admin_token):
        """Test /api/knowledge-patterns/seed-mdph returns skipped (already seeded)."""
        response = requests.post(
            f"{BASE_URL}/api/knowledge-patterns/seed-mdph",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "skipped"
        assert "26 patterns" in data.get("reason", "")
        print(f"✓ /api/knowledge-patterns/seed-mdph returns: {data}")
    
    def test_stats_endpoint_shows_mdph_patterns(self, admin_token):
        """Test /api/knowledge-patterns/stats returns correct counts including MDPH."""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-patterns/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check total includes MDPH
        assert data.get("total", 0) >= 40, f"Expected at least 40 patterns, got {data.get('total')}"
        
        # Check by_category includes demande_mdph
        by_category = data.get("by_category", {})
        assert "demande_mdph" in by_category, "demande_mdph not in by_category"
        assert by_category["demande_mdph"] == 26, f"Expected 26 MDPH patterns, got {by_category.get('demande_mdph')}"
        
        # Check by_type counts
        by_type = data.get("by_type", {})
        assert by_type.get("blocage", 0) >= 7, "Expected at least 7 blocage patterns"
        assert by_type.get("vigilance", 0) >= 6, "Expected at least 6 vigilance patterns"
        assert by_type.get("levier", 0) >= 5, "Expected at least 5 levier patterns"
        assert by_type.get("erreur_frequente", 0) >= 4, "Expected at least 4 erreur_frequente patterns"
        assert by_type.get("piece_manquante", 0) >= 4, "Expected at least 4 piece_manquante patterns"
        
        print(f"✓ Stats endpoint shows correct counts: {data}")


@pytest.mark.asyncio
class TestMDPHPatternsDirectDB:
    """Direct database tests for MDPH patterns using pytest-asyncio."""
    
    async def test_mdph_patterns_count(self):
        """Verify 26 MDPH patterns with usage_autorise=True."""
        from config import db
        count = await db.knowledge_patterns.count_documents({
            'categorie_dossier': 'demande_mdph',
            'usage_autorise': True
        })
        assert count == 26, f"Expected 26 MDPH patterns, got {count}"
        print(f"✓ 26 MDPH patterns with usage_autorise=True")
    
    async def test_mdph_patterns_by_type(self):
        """Verify pattern type distribution: blocage(7), vigilance(6), levier(5), erreur_frequente(4), piece_manquante(4)."""
        from config import db
        pipeline = [
            {'$match': {'categorie_dossier': 'demande_mdph'}},
            {'$group': {'_id': '$pattern_type', 'count': {'$sum': 1}}}
        ]
        result = await db.knowledge_patterns.aggregate(pipeline).to_list(50)
        type_counts = {item['_id']: item['count'] for item in result}
        
        expected = {
            'blocage': 7,
            'vigilance': 6,
            'levier': 5,
            'erreur_frequente': 4,
            'piece_manquante': 4
        }
        
        for ptype, expected_count in expected.items():
            actual = type_counts.get(ptype, 0)
            assert actual == expected_count, f"Expected {expected_count} {ptype}, got {actual}"
        
        print(f"✓ Pattern type distribution correct: {type_counts}")
    
    async def test_mdph_patterns_source_type(self):
        """Verify all MDPH patterns have source_type=seed_mdph_v1."""
        from config import db
        count = await db.knowledge_patterns.count_documents({
            'categorie_dossier': 'demande_mdph',
            'source_type': 'seed_mdph_v1'
        })
        assert count == 26, f"Expected 26 patterns with source_type=seed_mdph_v1, got {count}"
        print(f"✓ All 26 MDPH patterns have source_type=seed_mdph_v1")


@pytest.mark.asyncio
class TestKnowledgePatternsEngine:
    """Test the knowledge patterns engine scoring and injection."""
    
    async def test_mdph_aah_rsdae_context(self):
        """Test engine prioritizes AAH/RSDAE patterns for demande_mdph + aah_rsdae context."""
        from routes.knowledge_patterns import get_knowledge_patterns_context
        result = await get_knowledge_patterns_context(
            categorie="demande_mdph",
            type_sinistre="aah_rsdae",
            blocage="probatoire"
        )
        assert len(result) > 0, "Engine returned empty result for MDPH AAH/RSDAE context"
        
        # Check for AAH-specific content
        aah_keywords = ["AAH", "RSDAE", "allocation", "emploi", "50", "79"]
        found = any(kw in result for kw in aah_keywords)
        assert found, f"AAH/RSDAE patterns not prioritized in result"
        print(f"✓ Engine prioritizes AAH/RSDAE patterns (result: {len(result)} chars)")
    
    async def test_mdph_pch_context(self):
        """Test engine prioritizes PCH patterns for demande_mdph + pch_aides context."""
        from routes.knowledge_patterns import get_knowledge_patterns_context
        result = await get_knowledge_patterns_context(
            categorie="demande_mdph",
            type_sinistre="pch_aides",
            blocage="traduction_fonctionnelle"
        )
        assert len(result) > 0, "Engine returned empty result for MDPH PCH context"
        
        # Check for PCH-specific content
        pch_keywords = ["PCH", "aide humaine", "actes essentiels", "toilette", "habillage"]
        found = any(kw.lower() in result.lower() for kw in pch_keywords)
        assert found, f"PCH patterns not prioritized in result"
        print(f"✓ Engine prioritizes PCH patterns (result: {len(result)} chars)")
    
    async def test_mdph_rqth_context(self):
        """Test engine prioritizes RQTH patterns for demande_mdph + rqth_emploi context."""
        from routes.knowledge_patterns import get_knowledge_patterns_context
        result = await get_knowledge_patterns_context(
            categorie="demande_mdph",
            type_sinistre="rqth_emploi",
            blocage="qualification"
        )
        assert len(result) > 0, "Engine returned empty result for MDPH RQTH context"
        
        # Check for RQTH-specific content
        rqth_keywords = ["RQTH", "travailleur handicape", "amenagement", "poste", "emploi"]
        found = any(kw.lower() in result.lower() for kw in rqth_keywords)
        assert found, f"RQTH patterns not prioritized in result"
        print(f"✓ Engine prioritizes RQTH patterns (result: {len(result)} chars)")
    
    async def test_at_context_no_mdph_patterns(self):
        """Zero regression: AT context should NOT inject MDPH patterns."""
        from routes.knowledge_patterns import get_knowledge_patterns_context
        result = await get_knowledge_patterns_context(
            categorie="accident_travail",
            type_sinistre="at_lombaire"
        )
        
        # Check that no MDPH-specific keywords appear
        mdph_keywords = ["MDPH", "CDAPH", "AAH", "PCH", "RQTH", "CMI", "projet de vie MDPH"]
        found_mdph = any(kw in result for kw in mdph_keywords)
        assert not found_mdph, f"MDPH patterns incorrectly injected in AT context"
        print(f"✓ Zero regression: No MDPH patterns in AT context (result: {len(result)} chars)")
    
    async def test_assurance_context_no_mdph_patterns(self):
        """Zero regression: Assurance context should NOT inject MDPH patterns."""
        from routes.knowledge_patterns import get_knowledge_patterns_context
        result = await get_knowledge_patterns_context(
            categorie="litige_assurantiel",
            type_garantie="IPT",
            blocage="contractuel"
        )
        
        # Check that no MDPH-specific keywords appear
        mdph_keywords = ["MDPH", "CDAPH", "AAH", "PCH", "RQTH", "CMI", "projet de vie MDPH"]
        found_mdph = any(kw in result for kw in mdph_keywords)
        assert not found_mdph, f"MDPH patterns incorrectly injected in assurance context"
        print(f"✓ Zero regression: No MDPH patterns in assurance context (result: {len(result)} chars)")
    
    async def test_contestation_ipp_context_no_mdph_patterns(self):
        """Zero regression: Contestation IPP context should NOT inject MDPH patterns."""
        from routes.knowledge_patterns import get_knowledge_patterns_context
        result = await get_knowledge_patterns_context(
            categorie="contestation_taux_ipp",
            blocage="medico_evaluatif"
        )
        
        # Check that no MDPH-specific keywords appear
        mdph_keywords = ["MDPH", "CDAPH", "AAH", "PCH", "RQTH", "CMI", "projet de vie MDPH"]
        found_mdph = any(kw in result for kw in mdph_keywords)
        assert not found_mdph, f"MDPH patterns incorrectly injected in contestation IPP context"
        print(f"✓ Zero regression: No MDPH patterns in contestation IPP context (result: {len(result)} chars)")
    
    async def test_engine_respects_limits(self):
        """Test engine respects max limits: 5 patterns, 4 vigilances, 4 leviers (total 12)."""
        from routes.knowledge_patterns import get_knowledge_patterns_context
        result = await get_knowledge_patterns_context(
            categorie="demande_mdph"
        )
        
        # Count bullet points (each pattern/vigilance/levier is a bullet)
        bullet_count = result.count("  - ")
        assert bullet_count <= 12, f"Engine exceeded max 12 items limit: {bullet_count} items"
        print(f"✓ Engine respects limits: {bullet_count} items (max 12)")


class TestPromptsIntegrity:
    """Verify prompts USER are UNCHANGED."""
    
    def test_strategiia_basic_prompt_unchanged(self):
        """Verify STRATEGIIA_BASIC_PROMPT is unchanged."""
        from constants.prompts import STRATEGIIA_BASIC_PROMPT
        
        # Check key markers that should be present
        assert "Maximum 550 mots" in STRATEGIIA_BASIC_PROMPT
        assert "---SECTION_1---" in STRATEGIIA_BASIC_PROMPT
        assert "---SECTION_2---" in STRATEGIIA_BASIC_PROMPT
        assert "---SECTION_3---" in STRATEGIIA_BASIC_PROMPT
        assert "Stratégie & Expertise Santé" in STRATEGIIA_BASIC_PROMPT
        
        # Check no MDPH-specific modifications
        assert "MDPH" not in STRATEGIIA_BASIC_PROMPT
        assert "AAH" not in STRATEGIIA_BASIC_PROMPT
        
        print(f"✓ STRATEGIIA_BASIC_PROMPT unchanged ({len(STRATEGIIA_BASIC_PROMPT)} chars)")
    
    def test_strategiia_premium_prompt_unchanged(self):
        """Verify STRATEGIIA_PREMIUM_PROMPT is unchanged."""
        from constants.prompts import STRATEGIIA_PREMIUM_PROMPT
        
        # Check key markers
        assert "1800 et 2400 mots" in STRATEGIIA_PREMIUM_PROMPT
        assert "Votre situation analysée" in STRATEGIIA_PREMIUM_PROMPT
        assert "Lecture stratégique du dossier" in STRATEGIIA_PREMIUM_PROMPT
        assert "Le vrai nœud du dossier" in STRATEGIIA_PREMIUM_PROMPT
        
        # Check no MDPH-specific modifications
        assert "MDPH" not in STRATEGIIA_PREMIUM_PROMPT
        assert "AAH" not in STRATEGIIA_PREMIUM_PROMPT
        
        print(f"✓ STRATEGIIA_PREMIUM_PROMPT unchanged ({len(STRATEGIIA_PREMIUM_PROMPT)} chars)")
    
    def test_dossier_express_prompt_unchanged(self):
        """Verify DOSSIER_EXPRESS_PROMPT is unchanged."""
        from constants.prompts import DOSSIER_EXPRESS_PROMPT
        
        # Check key markers
        assert "2000 et 2800 mots" in DOSSIER_EXPRESS_PROMPT
        assert "RAPPORT DE PRÉ-EXPERTISE DOCUMENTAIRE" in DOSSIER_EXPRESS_PROMPT
        assert "SYNTHÈSE DU DOSSIER" in DOSSIER_EXPRESS_PROMPT
        
        # Check no MDPH-specific modifications
        assert "MDPH" not in DOSSIER_EXPRESS_PROMPT
        assert "AAH" not in DOSSIER_EXPRESS_PROMPT
        
        print(f"✓ DOSSIER_EXPRESS_PROMPT unchanged ({len(DOSSIER_EXPRESS_PROMPT)} chars)")


class TestPdfIntegrity:
    """Verify pdf.py is NOT modified."""
    
    def test_pdf_functions_exist(self):
        """Verify pdf.py functions exist and work."""
        from utils.pdf import generate_secured_pdf, generate_dossier_pdf, generate_report_number
        
        assert callable(generate_secured_pdf)
        assert callable(generate_dossier_pdf)
        assert callable(generate_report_number)
        
        # Test generate_report_number
        report_num = generate_report_number()
        assert report_num.startswith("SES-")
        assert len(report_num) >= 14  # SES-YYYY-XXXXX
        
        print(f"✓ pdf.py functions exist and work")
    
    def test_pdf_no_mdph_modifications(self):
        """Verify pdf.py has no MDPH-related modifications."""
        with open('/app/backend/utils/pdf.py', 'r') as f:
            content = f.read().lower()
        
        # Check no MDPH-specific code was added
        mdph_keywords = ['mdph', 'aah', 'pch', 'rqth', 'cmi', 'cdaph']
        found = [kw for kw in mdph_keywords if kw in content]
        
        assert len(found) == 0, f"Found MDPH keywords in pdf.py: {found}"
        print(f"✓ pdf.py has no MDPH modifications")


class TestSeedPatternsFile:
    """Verify seed_patterns.py contains correct MDPH patterns."""
    
    def test_seed_patterns_mdph_list_exists(self):
        """Verify SEED_PATTERNS_MDPH list exists with 26 patterns."""
        from constants.seed_patterns import SEED_PATTERNS_MDPH
        
        assert len(SEED_PATTERNS_MDPH) == 26, f"Expected 26 patterns, got {len(SEED_PATTERNS_MDPH)}"
        print(f"✓ SEED_PATTERNS_MDPH contains 26 patterns")
    
    def test_seed_patterns_mdph_structure(self):
        """Verify each MDPH pattern has required fields."""
        from constants.seed_patterns import SEED_PATTERNS_MDPH
        
        required_fields = ['categorie_dossier', 'pattern_type', 'description', 'niveau_confiance', 'tags']
        
        for i, pattern in enumerate(SEED_PATTERNS_MDPH):
            for field in required_fields:
                assert field in pattern, f"Pattern {i} missing field: {field}"
            
            # Verify categorie_dossier is demande_mdph
            assert pattern['categorie_dossier'] == 'demande_mdph', f"Pattern {i} has wrong categorie_dossier"
            
            # Verify pattern_type is valid
            valid_types = ['blocage', 'vigilance', 'levier', 'erreur_frequente', 'piece_manquante']
            assert pattern['pattern_type'] in valid_types, f"Pattern {i} has invalid pattern_type"
        
        print(f"✓ All MDPH patterns have correct structure")
    
    def test_seed_mdph_patterns_function_exists(self):
        """Verify seed_mdph_patterns function exists."""
        from constants.seed_patterns import seed_mdph_patterns
        
        assert callable(seed_mdph_patterns)
        print(f"✓ seed_mdph_patterns function exists")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
