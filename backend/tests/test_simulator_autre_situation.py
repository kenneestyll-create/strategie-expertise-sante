"""
Test suite for Simulator 'Autre situation' feature.
Tests that POST /api/simulator/result accepts and stores the autre_situation field.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSimulatorAutreSituation:
    """Tests for 'Autre situation' feature in simulator"""
    
    def test_simulator_result_with_autre_situation(self):
        """Test simulator result submission with autre_situation field"""
        payload = {
            "answers": {
                "situation": "autre",
                "demarche": "debut",
                "anciennete": "recent",
                "accompagnement": "seul",
                "besoin": "comprendre"
            },
            "autre_situation": "Mon problème spécifique avec mon employeur suite à un reclassement",
            "email": "test_autre_situation@example.com",
            "profile": "Situation spécifique : Mon problème spécifique avec mon employeur suite à un reclassement",
            "recommendations": [
                "Votre situation mérite une analyse personnalisée lors d'une première consultation gratuite de 10 minutes.",
                "Vous avez décrit votre situation comme suit : « Mon problème spécifique avec mon employeur suite à un reclassement ». Un expert pourra analyser votre cas en détail."
            ],
            "droits": [],
            "demarches": ["Prendre contact pour une première consultation gratuite de 10 minutes, sans engagement"],
            "delais": [],
            "prestation": "Consultation personnalisée"
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
        
        print(f"✓ Autre situation test passed - Result ID: {data['id']}")
    
    def test_simulator_result_autre_situation_empty(self):
        """Test simulator result with empty autre_situation (normal flow)"""
        payload = {
            "answers": {
                "situation": "at",
                "demarche": "debut",
                "anciennete": "recent",
                "accompagnement": "seul",
                "besoin": "comprendre"
            },
            "email": "test_normal_flow@example.com",
            "profile": "Victime d'accident du travail",
            "recommendations": ["Bien démarrer vos démarches avec un dossier solide dès le début est essentiel pour la suite."],
            "droits": ["Prise en charge à 100% des soins liés à l'AT/MP"],
            "demarches": ["Faire constater l'accident par votre employeur"],
            "delais": ["Déclaration employeur : 48h après l'accident"],
            "prestation": "Analyse de dossier AT/MP"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        
        print(f"✓ Normal flow (no autre_situation) test passed - Result ID: {data['id']}")
    
    def test_simulator_result_requires_email(self):
        """Test that email is required (no skip option)"""
        payload = {
            "answers": {
                "situation": "autre",
                "demarche": "debut",
                "anciennete": "recent",
                "accompagnement": "seul",
                "besoin": "comprendre"
            },
            "autre_situation": "Test situation",
            "email": "required_email@test.com",  # Email is now mandatory
            "profile": "Situation spécifique",
            "recommendations": ["Test recommendation"],
            "droits": [],
            "demarches": [],
            "delais": [],
            "prestation": "Consultation personnalisée"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        
        print(f"✓ Email required test passed - Result ID: {data['id']}")
    
    def test_simulator_result_autre_situation_long_text(self):
        """Test simulator with long autre_situation text (up to 200 chars)"""
        long_text = "Ceci est une description détaillée de ma situation particulière qui nécessite une analyse approfondie par un expert. Je souhaite comprendre mes droits et les démarches à entreprendre."
        
        payload = {
            "answers": {
                "situation": "autre",
                "demarche": "en_cours",
                "anciennete": "moyen",
                "accompagnement": "seul",
                "besoin": "global"
            },
            "autre_situation": long_text,
            "email": "test_long_text@example.com",
            "profile": f"Situation spécifique : {long_text}",
            "recommendations": [
                "Votre situation mérite une analyse personnalisée.",
                f"Vous avez décrit votre situation comme suit : « {long_text} »."
            ],
            "droits": [],
            "demarches": ["Prendre contact pour une première consultation gratuite"],
            "delais": [],
            "prestation": "Consultation personnalisée"
        }
        
        response = requests.post(f"{BASE_URL}/api/simulator/result", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        
        print(f"✓ Long text autre_situation test passed - Result ID: {data['id']}")


class TestHealthEndpoint:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        
        print("✓ Health endpoint test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
