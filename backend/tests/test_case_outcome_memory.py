"""
Test Case Outcome Memory Module
================================
Tests for the silent V2 preparation module that extracts structured features
from StrategiIA/Dossier Express analyses and stores them in MongoDB.

Features tested:
- extract_case_features() detection of blocages, pieces_manquantes, leviers, familles
- store_case_outcome() RGPD compliance (improvement_optout flag)
- Admin endpoint /api/knowledge-patterns/case-outcomes/stats
- Prompt integrity verification (SHA-256)
"""

import pytest
import requests
import os
import hashlib

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@accompagn-sante.fr"
ADMIN_PASSWORD = "Admin2024!"


class TestExtractCaseFeatures:
    """Tests for extract_case_features() function"""
    
    def test_detect_blocages_at_mp_probatoire(self):
        """Test detection of probatoire blocage from AT/MP text"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        L'analyse révèle un problème probatoire majeur. Le bénéficiaire doit prouver 
        le lien causal avec son accident du travail. Les justificatifs sont insuffisants.
        """
        result = extract_case_features(text, type_dossier='at', regime='regime_general')
        
        assert 'probatoire' in result['blocages_detectes'], "Should detect probatoire blocage"
        assert result['niveau_complexite'] in ['faible', 'moyen', 'eleve']
    
    def test_detect_blocages_at_mp_medical(self):
        """Test detection of medical blocage from AT/MP text"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Le certificat médical initial est incomplet. L'expertise médicale n'a pas 
        été réalisée correctement. Le médecin conseil conteste la consolidation.
        """
        result = extract_case_features(text, type_dossier='at', regime='regime_general')
        
        assert 'medical' in result['blocages_detectes'], "Should detect medical blocage"
    
    def test_detect_blocages_mdph_traduction_fonctionnelle(self):
        """Test detection of traduction_fonctionnelle blocage from MDPH text"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Le dossier MDPH présente un déficit de traduction fonctionnelle. 
        Le retentissement sur le quotidien et l'autonomie n'est pas documenté.
        Les actes essentiels de la vie quotidienne ne sont pas décrits.
        """
        result = extract_case_features(text, type_dossier='mdph', regime='aah')
        
        assert 'traduction_fonctionnelle' in result['blocages_detectes'], \
            "Should detect traduction_fonctionnelle blocage"
    
    def test_detect_pieces_manquantes_certificat(self):
        """Test detection of certificat_medical_detaille in pieces_manquantes"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Le certificat médical est manquant. Le cerfa 15695 n'a pas été fourni.
        Un certificat détaillé serait nécessaire pour compléter le dossier.
        """
        result = extract_case_features(text)
        
        assert 'certificat_medical_detaille' in result['pieces_manquantes_detectees'], \
            "Should detect certificat_medical_detaille as missing"
    
    def test_detect_pieces_manquantes_bilan(self):
        """Test detection of bilan_fonctionnel in pieces_manquantes"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Un bilan fonctionnel serait nécessaire. Le bilan ergothérapique 
        et le bilan neuropsychologique permettraient de mieux documenter le dossier.
        """
        result = extract_case_features(text)
        
        assert 'bilan_fonctionnel' in result['pieces_manquantes_detectees'], \
            "Should detect bilan_fonctionnel as missing"
    
    def test_detect_pieces_manquantes_projet_de_vie(self):
        """Test detection of projet_de_vie in pieces_manquantes"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Le projet de vie est incomplet. La journée type n'est pas décrite.
        """
        result = extract_case_features(text)
        
        assert 'projet_de_vie' in result['pieces_manquantes_detectees'], \
            "Should detect projet_de_vie as missing"
    
    def test_detect_leviers_expertise_amiable(self):
        """Test detection of expertise_amiable lever"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Une expertise amiable pourrait être envisagée. Une contre-expertise 
        ou expertise contradictoire permettrait de contester les conclusions.
        """
        result = extract_case_features(text)
        
        assert 'expertise_amiable' in result['leviers_detectes'], \
            "Should detect expertise_amiable lever"
    
    def test_detect_leviers_reclassification(self):
        """Test detection of reclassification lever"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Une reclassification du taux pourrait être demandée. 
        La revalorisation est possible en cas d'aggravation.
        """
        result = extract_case_features(text)
        
        assert 'reclassification' in result['leviers_detectes'], \
            "Should detect reclassification lever"
    
    def test_detect_leviers_rapo_mdph(self):
        """Test detection of rapo_mdph lever"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Un RAPO (recours administratif préalable) pourrait être déposé 
        auprès de la MDPH pour contester la décision.
        """
        result = extract_case_features(text)
        
        assert 'rapo_mdph' in result['leviers_detectes'], \
            "Should detect rapo_mdph lever"
    
    def test_detect_familles_at_mp(self):
        """Test detection of at_mp famille_situation"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Dossier concernant un accident du travail. La maladie professionnelle 
        est également évoquée (AT/MP). Le tableau MP pourrait s'appliquer.
        """
        result = extract_case_features(text)
        
        assert 'at_mp' in result['familles_situation'], \
            "Should detect at_mp famille"
    
    def test_detect_familles_mdph_aah(self):
        """Test detection of mdph_aah famille_situation"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Demande MDPH pour l'AAH (allocation adulte handicapé). 
        Le taux d'incapacité est en cours d'évaluation.
        """
        result = extract_case_features(text)
        
        assert 'mdph_aah' in result['familles_situation'], \
            "Should detect mdph_aah famille"
    
    def test_detect_familles_assurance_emprunteur(self):
        """Test detection of assurance_emprunteur famille_situation"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Litige assurance emprunteur. La garantie ITT du prêt immobilier 
        est contestée par l'assureur.
        """
        result = extract_case_features(text)
        
        assert 'assurance_emprunteur' in result['familles_situation'], \
            "Should detect assurance_emprunteur famille"
    
    def test_complexite_faible(self):
        """Test complexite level faible (signal_count < 4)"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = "Dossier simple sans blocage particulier identifié."
        result = extract_case_features(text)
        
        assert result['niveau_complexite'] == 'faible', \
            f"Expected faible, got {result['niveau_complexite']}"
        assert result['signal_count'] < 4
    
    def test_complexite_moyen(self):
        """Test complexite level moyen (4 <= signal_count < 8)"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Problème probatoire avec certificat médical manquant. 
        Expertise amiable possible. Accident du travail concerné.
        """
        result = extract_case_features(text)
        
        assert result['niveau_complexite'] == 'moyen', \
            f"Expected moyen, got {result['niveau_complexite']}"
        assert 4 <= result['signal_count'] < 8
    
    def test_complexite_eleve(self):
        """Test complexite level eleve (signal_count >= 8)"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import extract_case_features
        
        text = """
        Dossier complexe: problème probatoire, médical et administratif. 
        Certificat médical, bilan fonctionnel, projet de vie manquants. 
        Expertise amiable, recours CRA, RAPO MDPH possibles. 
        AT/MP et MDPH AAH concernés. Consolidation contestée.
        """
        result = extract_case_features(text)
        
        assert result['niveau_complexite'] == 'eleve', \
            f"Expected eleve, got {result['niveau_complexite']}"
        assert result['signal_count'] >= 8


class TestStoreCaseOutcome:
    """Tests for store_case_outcome() function and RGPD compliance"""
    
    @pytest.fixture
    def db_connection(self):
        """Create async MongoDB connection"""
        import asyncio
        from motor.motor_asyncio import AsyncIOMotorClient
        
        MONGO_URL = os.environ.get('MONGO_URL')
        DB_NAME = os.environ.get('DB_NAME', 'strategie_sante')
        
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        yield db
        client.close()
    
    def test_store_with_optout_false(self, db_connection):
        """Test that records ARE stored when improvement_optout=False"""
        import asyncio
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import store_case_outcome
        
        features = {
            'blocages_detectes': ['probatoire'],
            'pieces_manquantes_detectees': ['certificat_medical_detaille'],
            'leviers_detectes': ['expertise_amiable'],
            'familles_situation': ['at_mp'],
            'niveau_complexite': 'moyen',
            'signal_count': 4
        }
        
        async def run_test():
            result = await store_case_outcome(
                db_connection, 'test_pytest', 'at', 'regime_general',
                features, quality_score={'level': 'bon', 'score': 75},
                improvement_optout=False
            )
            
            assert result is not None, "Should return record ID when optout=False"
            
            # Verify record exists
            record = await db_connection.case_outcomes.find_one({'id': result}, {'_id': 0})
            assert record is not None, "Record should exist in database"
            
            # Cleanup
            await db_connection.case_outcomes.delete_one({'id': result})
            
            return result
        
        asyncio.get_event_loop().run_until_complete(run_test())
    
    def test_store_with_optout_true_rgpd(self, db_connection):
        """Test that records are NOT stored when improvement_optout=True (RGPD compliance)"""
        import asyncio
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import store_case_outcome
        
        features = {
            'blocages_detectes': ['probatoire'],
            'pieces_manquantes_detectees': [],
            'leviers_detectes': [],
            'familles_situation': [],
            'niveau_complexite': 'faible',
            'signal_count': 1
        }
        
        async def run_test():
            result = await store_case_outcome(
                db_connection, 'test_pytest_optout', 'at', 'regime_general',
                features, quality_score={'level': 'bon', 'score': 75},
                improvement_optout=True
            )
            
            assert result is None, "Should return None when optout=True (RGPD)"
            
            # Verify no record was created
            count = await db_connection.case_outcomes.count_documents({'source': 'test_pytest_optout'})
            assert count == 0, "No record should be created when optout=True"
        
        asyncio.get_event_loop().run_until_complete(run_test())
    
    def test_stored_records_no_personal_data(self, db_connection):
        """Test that stored records contain NO personal data"""
        import asyncio
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.case_outcome_memory import store_case_outcome
        
        features = {
            'blocages_detectes': ['medical'],
            'pieces_manquantes_detectees': [],
            'leviers_detectes': [],
            'familles_situation': [],
            'niveau_complexite': 'faible',
            'signal_count': 1
        }
        
        async def run_test():
            result = await store_case_outcome(
                db_connection, 'test_no_personal', 'at', 'regime_general',
                features, improvement_optout=False
            )
            
            record = await db_connection.case_outcomes.find_one({'id': result}, {'_id': 0})
            
            # Check NO personal data fields
            forbidden_fields = ['name', 'email', 'raw_text', 'situation', 'address', 
                              'phone', 'matricule', 'ssn', 'medical_text']
            for field in forbidden_fields:
                assert field not in record, f"Record should NOT contain {field}"
            
            # Verify expected anonymized fields exist
            expected_fields = ['id', 'source', 'categorie_dossier', 'blocage_principal',
                             'niveau_complexite', 'improvement_optout', 'created_at']
            for field in expected_fields:
                assert field in record, f"Record should contain {field}"
            
            # Cleanup
            await db_connection.case_outcomes.delete_one({'id': result})
        
        asyncio.get_event_loop().run_until_complete(run_test())


class TestAdminEndpoint:
    """Tests for admin-only case-outcomes stats endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin authentication failed")
    
    def test_stats_endpoint_returns_401_or_403_without_token(self):
        """Test that /api/knowledge-patterns/case-outcomes/stats returns 401/403 without token"""
        response = requests.get(f"{BASE_URL}/api/knowledge-patterns/case-outcomes/stats")
        
        assert response.status_code in [401, 403], \
            f"Expected 401 or 403, got {response.status_code}"
    
    def test_stats_endpoint_returns_200_with_admin_token(self, admin_token):
        """Test that /api/knowledge-patterns/case-outcomes/stats returns 200 with admin token"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-patterns/case-outcomes/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'total' in data, "Response should contain 'total'"
    
    def test_stats_endpoint_returns_aggregated_data(self, admin_token):
        """Test that stats endpoint returns properly aggregated data"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-patterns/case-outcomes/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check expected aggregation fields
        expected_fields = ['total', 'blocages_frequents', 'pieces_manquantes_frequentes',
                         'leviers_frequents', 'familles_situation', 
                         'repartition_complexite', 'repartition_source']
        
        for field in expected_fields:
            assert field in data, f"Response should contain '{field}'"


class TestPromptIntegrity:
    """Tests for prompt SHA-256 integrity verification"""
    
    def test_strategiia_basic_prompt_sha256(self):
        """Verify STRATEGIIA_BASIC_PROMPT SHA-256 hash"""
        import sys
        sys.path.insert(0, '/app/backend')
        from constants.prompts import STRATEGIIA_BASIC_PROMPT
        
        actual_hash = hashlib.sha256(STRATEGIIA_BASIC_PROMPT.encode()).hexdigest()[:8]
        expected_hash = "8e305f81"
        
        assert actual_hash == expected_hash, \
            f"STRATEGIIA_BASIC_PROMPT hash mismatch: expected {expected_hash}, got {actual_hash}"
    
    def test_strategiia_premium_prompt_sha256(self):
        """Verify STRATEGIIA_PREMIUM_PROMPT SHA-256 hash"""
        import sys
        sys.path.insert(0, '/app/backend')
        from constants.prompts import STRATEGIIA_PREMIUM_PROMPT
        
        actual_hash = hashlib.sha256(STRATEGIIA_PREMIUM_PROMPT.encode()).hexdigest()[:8]
        expected_hash = "be2e9fda"
        
        assert actual_hash == expected_hash, \
            f"STRATEGIIA_PREMIUM_PROMPT hash mismatch: expected {expected_hash}, got {actual_hash}"
    
    def test_dossier_express_prompt_sha256(self):
        """Verify DOSSIER_EXPRESS_PROMPT SHA-256 hash"""
        import sys
        sys.path.insert(0, '/app/backend')
        from constants.prompts import DOSSIER_EXPRESS_PROMPT
        
        actual_hash = hashlib.sha256(DOSSIER_EXPRESS_PROMPT.encode()).hexdigest()[:8]
        expected_hash = "bd26872c"
        
        assert actual_hash == expected_hash, \
            f"DOSSIER_EXPRESS_PROMPT hash mismatch: expected {expected_hash}, got {actual_hash}"


class TestHealthEndpoint:
    """Test API health endpoint"""
    
    def test_health_returns_healthy(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'


class TestNoFrontendModification:
    """Verify frontend was NOT modified"""
    
    def test_no_case_outcome_in_frontend(self):
        """Verify no case_outcome references in frontend code"""
        import subprocess
        
        result = subprocess.run(
            ['grep', '-r', 'case_outcome', '/app/frontend/src/'],
            capture_output=True, text=True
        )
        
        # grep returns 1 if no matches found (which is what we want)
        assert result.returncode == 1, \
            f"Frontend should NOT contain case_outcome references: {result.stdout}"


class TestNoPdfModification:
    """Verify pdf.py was NOT modified"""
    
    def test_no_case_outcome_in_pdf(self):
        """Verify no case_outcome references in pdf.py"""
        import subprocess
        
        result = subprocess.run(
            ['grep', 'case_outcome', '/app/backend/utils/pdf.py'],
            capture_output=True, text=True
        )
        
        # grep returns 1 if no matches found (which is what we want)
        assert result.returncode == 1, \
            f"pdf.py should NOT contain case_outcome references: {result.stdout}"
