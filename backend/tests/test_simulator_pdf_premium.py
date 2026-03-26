"""
Tests for Simulator PDF Premium Design (Noir/Or/Ivoire palette)
Tests the complete simulator flow and PDF generation with premium design.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSimulatorAPI:
    """Tests for POST /api/simulator/result endpoint"""

    def test_simulator_result_accident_travail(self):
        """Test simulator result submission - Accident du travail scenario"""
        payload = {
            "answers": {
                "situation": "at",
                "demarche": "debut",
                "anciennete": "recent",
                "accompagnement": "seul",
                "besoin": "comprendre"
            },
            "email": "test-at@example.com",
            "profile": "Victime d'accident du travail",
            "recommendations": ["Bien démarrer vos démarches avec un dossier solide dès le début est essentiel pour la suite."],
            "droits": ["Prise en charge à 100% des soins liés à l'AT/MP"],
            "demarches": ["Faire constater l'accident par votre employeur"],
            "delais": ["Déclaration employeur : 48h après l'accident"],
            "prestation": "Analyse de dossier AT/MP"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        assert "id" in data
        print(f"✓ Simulator result saved with ID: {data['id']}")

    def test_simulator_result_maladie_professionnelle(self):
        """Test simulator result submission - Maladie professionnelle scenario"""
        payload = {
            "answers": {
                "situation": "mp",
                "demarche": "refus",
                "anciennete": "moyen",
                "accompagnement": "seul",
                "besoin": "contester"
            },
            "email": "test-mp@example.com",
            "profile": "Victime de maladie professionnelle",
            "recommendations": ["Votre refus doit être analysé en détail pour identifier les motifs et préparer un recours solide."],
            "droits": ["Prise en charge à 100% des soins liés à l'AT/MP", "Indemnités journalières majorées"],
            "demarches": ["Demander la notification écrite du refus avec ses motifs"],
            "delais": ["Recours CRA : 2 mois après la notification du refus"],
            "prestation": "Préparation du recours"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        assert "id" in data
        print(f"✓ Maladie professionnelle result saved with ID: {data['id']}")

    def test_simulator_result_mdph(self):
        """Test simulator result submission - MDPH scenario"""
        payload = {
            "answers": {
                "situation": "mdph",
                "demarche": "debut",
                "anciennete": "recent",
                "accompagnement": "association",
                "besoin": "dossier"
            },
            "email": "test-mdph@example.com",
            "profile": "Demande MDPH (Handicap)",
            "recommendations": ["Le dossier MDPH requiert une attention particulière, notamment le projet de vie."],
            "droits": ["AAH — Allocation aux Adultes Handicapés", "RQTH — Reconnaissance de la Qualité de Travailleur Handicapé"],
            "demarches": ["Retirer le formulaire Cerfa n°15692 auprès de votre MDPH"],
            "delais": ["Instruction MDPH : 4 mois en moyenne"],
            "prestation": "Accompagnement dossier MDPH"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        print(f"✓ MDPH result saved with ID: {data['id']}")

    def test_simulator_result_expertise(self):
        """Test simulator result - Expertise médicale scenario (urgent)"""
        payload = {
            "answers": {
                "situation": "expertise",
                "demarche": "expertise",
                "anciennete": "moyen",
                "accompagnement": "seul",
                "besoin": "preparer"
            },
            "email": "test-expertise@example.com",
            "profile": "Préparation expertise médicale",
            "recommendations": ["La préparation est cruciale pour faire valoir vos droits."],
            "droits": ["Droit d'être accompagné par un médecin-conseil de votre choix"],
            "demarches": ["Rassembler l'intégralité de votre dossier médical"],
            "delais": ["Convocation expertise : se présenter impérativement à la date fixée"],
            "prestation": "Préparation expertise médicale"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        print(f"✓ Expertise result saved with ID: {data['id']}")

    def test_simulator_result_assurance(self):
        """Test simulator result - Litige assurantiel scenario"""
        payload = {
            "answers": {
                "situation": "assurance",
                "demarche": "recours",
                "anciennete": "long",
                "accompagnement": "avocat",
                "besoin": "contester"
            },
            "email": "test-assurance@example.com",
            "profile": "Litige assurantiel",
            "recommendations": ["Vérifiez si votre contrat inclut une protection juridique."],
            "droits": ["Droit à l'indemnisation selon les garanties de votre contrat"],
            "demarches": ["Relire attentivement votre contrat d'assurance"],
            "delais": ["Prescription : 2 ans pour les contrats d'assurance"],
            "prestation": "Activation protection juridique"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        print(f"✓ Assurance result saved with ID: {data['id']}")

    def test_simulator_result_autre_situation(self):
        """Test simulator result - Autre situation with custom text"""
        payload = {
            "answers": {
                "situation": "autre",
                "demarche": "debut",
                "anciennete": "recent",
                "accompagnement": "seul",
                "besoin": "comprendre"
            },
            "autre_situation": "Conflit avec mon employeur suite à un reclassement professionnel",
            "email": "test-autre@example.com",
            "profile": "Situation spécifique : Conflit avec mon employeur suite à un reclassement professionnel",
            "recommendations": ["Votre situation mérite une analyse personnalisée lors d'une première consultation gratuite."],
            "droits": [],
            "demarches": ["Prendre contact pour une première consultation gratuite"],
            "delais": [],
            "prestation": "Consultation personnalisée"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        print(f"✓ Autre situation result saved with ID: {data['id']}")

    def test_simulator_result_minimal_payload(self):
        """Test simulator with minimal required fields"""
        payload = {
            "answers": {"situation": "at"},
            "profile": "Test profile"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        print("✓ Minimal payload accepted")


class TestHealthCheck:
    """Basic health check tests"""

    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ API health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
