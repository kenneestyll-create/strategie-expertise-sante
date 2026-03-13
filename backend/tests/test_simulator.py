"""
Test suite for the Simulator (Questionnaire) feature.
Tests the POST /api/simulator/result endpoint with various scenarios.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSimulatorEndpoint:
    """Tests for POST /api/simulator/result endpoint"""
    
    def test_simulator_result_with_email_at_scenario(self):
        """Test simulator result submission with email - Accident du travail scenario"""
        payload = {
            "answers": {
                "situation": "at",
                "demarche": "debut", 
                "anciennete": "recent",
                "accompagnement": "seul",
                "besoin": "comprendre"
            },
            "email": "test_at@example.com",
            "profile": "Victime d'accident du travail",
            "recommendations": ["Bien démarrer vos démarches avec un dossier solide dès le début est essentiel pour la suite."],
            "droits": ["Prise en charge à 100% des soins liés à l'AT/MP", "Indemnités journalières majorées pendant l'arrêt de travail"],
            "demarches": ["Faire constater l'accident par votre employeur", "Consulter un médecin pour le certificat médical initial"],
            "delais": ["Déclaration employeur : 48h après l'accident"],
            "prestation": "Analyse de dossier AT/MP"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert "id" in data, "Response should contain result ID"
        assert isinstance(data["id"], str), "ID should be a string"
        assert len(data["id"]) > 0, "ID should not be empty"
        
        print(f"✓ AT scenario test passed - Result ID: {data['id']}")
    
    def test_simulator_result_with_email_mp_scenario(self):
        """Test simulator result submission - Maladie professionnelle scenario"""
        payload = {
            "answers": {
                "situation": "mp",
                "demarche": "refus",
                "anciennete": "moyen",
                "accompagnement": "seul",
                "besoin": "contester"
            },
            "email": "test_mp@example.com",
            "profile": "Victime de maladie professionnelle",
            "recommendations": ["Votre refus doit être analysé en détail"],
            "droits": ["Prise en charge à 100% des soins liés à l'AT/MP"],
            "demarches": ["Obtenir un certificat médical initial", "Remplir la déclaration de maladie professionnelle"],
            "delais": ["Déclaration : dans les 15 jours suivant le certificat médical"],
            "prestation": "Préparation du recours"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        assert "id" in data
        
        print(f"✓ MP scenario test passed - Result ID: {data['id']}")
    
    def test_simulator_result_with_email_mdph_scenario(self):
        """Test simulator result submission - MDPH scenario"""
        payload = {
            "answers": {
                "situation": "mdph",
                "demarche": "en_cours",
                "anciennete": "long",
                "accompagnement": "syndicat",
                "besoin": "dossier"
            },
            "email": "test_mdph@example.com",
            "profile": "Demande MDPH (Handicap)",
            "recommendations": ["Le dossier MDPH requiert une attention particulière"],
            "droits": ["AAH — Allocation aux Adultes Handicapés", "RQTH — Reconnaissance de la Qualité de Travailleur Handicapé"],
            "demarches": ["Retirer le formulaire Cerfa n°15692", "Faire remplir le certificat médical"],
            "delais": ["Instruction MDPH : 4 mois en moyenne"],
            "prestation": "Accompagnement dossier MDPH"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        
        print(f"✓ MDPH scenario test passed - Result ID: {data['id']}")
    
    def test_simulator_result_expertise_scenario(self):
        """Test simulator result - Expertise médicale scenario (urgent)"""
        payload = {
            "answers": {
                "situation": "expertise",
                "demarche": "expertise",
                "anciennete": "recent",
                "accompagnement": "avocat",
                "besoin": "preparer"
            },
            "email": "test_expertise@example.com",
            "profile": "Préparation expertise médicale",
            "recommendations": ["La préparation est cruciale pour faire valoir vos droits"],
            "droits": ["Droit d'être accompagné par un médecin-conseil"],
            "demarches": ["Rassembler l'intégralité de votre dossier médical"],
            "delais": ["Convocation expertise : se présenter impérativement à la date fixée"],
            "prestation": "Préparation expertise médicale"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        
        print(f"✓ Expertise scenario test passed - Result ID: {data['id']}")
    
    def test_simulator_result_assurance_scenario(self):
        """Test simulator result - Litige assurantiel scenario"""
        payload = {
            "answers": {
                "situation": "assurance",
                "demarche": "recours",
                "anciennete": "tres_long",
                "accompagnement": "seul",
                "besoin": "global"
            },
            "email": "test_assurance@example.com",
            "profile": "Litige assurantiel",
            "recommendations": ["Vérifiez si votre contrat inclut une protection juridique"],
            "droits": ["Droit à l'indemnisation selon les garanties de votre contrat"],
            "demarches": ["Relire attentivement votre contrat d'assurance"],
            "delais": ["Prescription : 2 ans pour les contrats d'assurance"],
            "prestation": "Activation protection juridique"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        
        print(f"✓ Assurance scenario test passed - Result ID: {data['id']}")
    
    def test_simulator_result_without_email(self):
        """Test simulator result submission without email (skip email step)"""
        payload = {
            "answers": {
                "situation": "at",
                "demarche": "debut",
                "anciennete": "recent",
                "accompagnement": "seul",
                "besoin": "comprendre"
            },
            "profile": "Victime d'accident du travail",
            "recommendations": ["Premier échange gratuit"],
            "droits": ["Prise en charge à 100%"],
            "demarches": ["Déclarer l'accident"],
            "delais": ["48h pour déclarer"],
            "prestation": "Analyse de dossier AT/MP"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        
        # Should work even without email
        assert response.status_code == 200, f"Should accept without email, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        
        print(f"✓ Skip email test passed - Result ID: {data['id']}")
    
    def test_simulator_result_minimal_payload(self):
        """Test simulator with minimal required fields"""
        payload = {
            "answers": {"situation": "autre"},
            "profile": "Situation spécifique"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        
        assert response.status_code == 200, f"Should accept minimal payload, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        
        print(f"✓ Minimal payload test passed - Result ID: {data['id']}")
    
    def test_simulator_result_all_fields_populated(self):
        """Test simulator with all possible fields populated"""
        payload = {
            "answers": {
                "situation": "at",
                "demarche": "refus",
                "anciennete": "moyen",
                "accompagnement": "seul",
                "besoin": "global"
            },
            "email": "test_full@example.com",
            "profile": "Victime d'accident du travail",
            "recommendations": [
                "Votre refus doit être analysé en détail",
                "Un accompagnement spécialisé peut significativement améliorer vos chances",
                "Vous n'êtes pas accompagné(e)"
            ],
            "droits": [
                "Prise en charge à 100% des soins liés à l'AT/MP",
                "Indemnités journalières majorées pendant l'arrêt de travail",
                "Rente ou capital en cas de séquelles (IPP)",
                "Protection contre le licenciement pendant l'arrêt"
            ],
            "demarches": [
                "Faire constater l'accident par votre employeur",
                "Consulter un médecin pour le certificat médical initial",
                "Vérifier que votre employeur a bien déclaré l'AT à la CPAM",
                "Demander la notification écrite du refus avec ses motifs",
                "Saisir la Commission de Recours Amiable (CRA)"
            ],
            "delais": [
                "Déclaration employeur : 48h après l'accident",
                "Certificat médical : dans les 24h si possible",
                "Contestation : 2 mois après notification",
                "Recours CRA : 2 mois après la notification du refus"
            ],
            "prestation": "Accompagnement complet"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "id" in data
        
        print(f"✓ Full payload test passed - Result ID: {data['id']}")


class TestHealthEndpoint:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data
        
        print("✓ Health endpoint test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
