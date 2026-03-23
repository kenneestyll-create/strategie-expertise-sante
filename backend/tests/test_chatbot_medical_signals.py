"""
Test suite for Chatbot Medical Signal Detection and Restricted FAQ
Tests the fix: FAQ restricted to general questions (tarifs, contact), 
medical/legal questions bypass FAQ and go to Claude AI with enriched prompt.

Key changes tested:
- MEDICAL_SIGNALS list bypasses FAQ for medical/legal questions
- FAQ entries have must_not_contain exclusions
- Claude system prompt includes complete tableaux MP data
- AI responses include actionable links
"""
import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestMedicalSignalDetection:
    """Tests that medical/legal questions bypass FAQ and get AI responses"""
    
    def test_coccygodynie_returns_ai_not_faq(self):
        """
        CRITICAL: 'la coccygodynie est-elle dans un tableau de maladies professionnelles'
        Should return AI response mentioning 'hors tableau' and 'CRRMP', NOT generic FAQ
        """
        session_id = f"test_coccyg_{uuid.uuid4()}"
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "la coccygodynie est-elle dans un tableau de maladies professionnelles",
            "session_id": session_id
        }, timeout=60)
        
        assert response.status_code == 200
        data = response.json()
        
        # MUST NOT be FAQ response
        assert data["is_faq"] == False, f"Expected AI response, got FAQ: {data['response'][:200]}"
        
        # AI response should mention hors tableau or CRRMP
        response_lower = data["response"].lower()
        has_hors_tableau = "hors tableau" in response_lower
        has_crrmp = "crrmp" in response_lower
        
        assert has_hors_tableau or has_crrmp, \
            f"AI response should mention 'hors tableau' or 'CRRMP'. Got: {data['response'][:500]}"
        
        print(f"✓ Coccygodynie correctly returns AI response mentioning hors tableau/CRRMP")
        print(f"  Response preview: {data['response'][:200]}...")
    
    def test_canal_carpien_returns_tableau_57c(self):
        """
        'le canal carpien est dans quel tableau' should return AI response mentioning Tableau 57C
        """
        session_id = f"test_carpien_{uuid.uuid4()}"
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "le canal carpien est dans quel tableau",
            "session_id": session_id
        }, timeout=60)
        
        assert response.status_code == 200
        data = response.json()
        
        # MUST NOT be FAQ
        assert data["is_faq"] == False, f"Expected AI response, got FAQ"
        
        # Should mention Tableau 57 or 57C
        response_text = data["response"]
        has_tableau_57 = "57" in response_text
        
        assert has_tableau_57, \
            f"AI response should mention Tableau 57/57C. Got: {response_text[:500]}"
        
        print(f"✓ Canal carpien correctly returns AI response mentioning Tableau 57")
    
    def test_burn_out_returns_ai_with_crrmp(self):
        """
        'le burn out peut-il etre reconnu comme maladie professionnelle' 
        Should return AI response mentioning CRRMP or hors tableau
        """
        session_id = f"test_burnout_{uuid.uuid4()}"
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "le burn out peut-il etre reconnu comme maladie professionnelle",
            "session_id": session_id
        }, timeout=60)
        
        assert response.status_code == 200
        data = response.json()
        
        # MUST NOT be FAQ
        assert data["is_faq"] == False, f"Expected AI response, got FAQ"
        
        response_lower = data["response"].lower()
        has_crrmp = "crrmp" in response_lower
        has_hors_tableau = "hors tableau" in response_lower
        has_alinea = "alinéa" in response_lower or "alinea" in response_lower
        
        assert has_crrmp or has_hors_tableau or has_alinea, \
            f"AI response should mention CRRMP/hors tableau/alinéa. Got: {data['response'][:500]}"
        
        print(f"✓ Burn out correctly returns AI response about CRRMP procedure")
    
    def test_contester_expertise_returns_ai(self):
        """
        'comment contester une expertise medicale' should return AI response, NOT FAQ
        """
        session_id = f"test_contester_{uuid.uuid4()}"
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "comment contester une expertise medicale",
            "session_id": session_id
        }, timeout=60)
        
        assert response.status_code == 200
        data = response.json()
        
        # MUST NOT be FAQ - "comment contester" is a MEDICAL_SIGNAL
        assert data["is_faq"] == False, \
            f"Expected AI response for 'comment contester', got FAQ: {data['response'][:200]}"
        
        # Should have substantial AI response
        assert len(data["response"]) > 100, "AI response should be substantial"
        
        print(f"✓ 'Comment contester expertise' correctly returns AI response")
    
    def test_taux_ipp_lombalgie_returns_ai_with_tableau_97(self):
        """
        'quel taux IPP pour une lombalgie' should return AI response mentioning tableau 97
        """
        session_id = f"test_ipp_lomb_{uuid.uuid4()}"
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "quel taux IPP pour une lombalgie",
            "session_id": session_id
        }, timeout=60)
        
        assert response.status_code == 200
        data = response.json()
        
        # MUST NOT be FAQ - "quel taux" and "lombalgie" are MEDICAL_SIGNALS
        assert data["is_faq"] == False, f"Expected AI response, got FAQ"
        
        # Should mention tableau 97 or 98 (lombalgie/hernie)
        response_text = data["response"]
        has_tableau_97 = "97" in response_text
        has_tableau_98 = "98" in response_text
        
        assert has_tableau_97 or has_tableau_98, \
            f"AI response should mention Tableau 97 or 98. Got: {response_text[:500]}"
        
        print(f"✓ IPP lombalgie correctly returns AI response mentioning Tableau 97/98")
    
    def test_droits_apres_accident_returns_ai(self):
        """
        'quels sont mes droits apres un accident' should return AI response
        The word 'accident' alone no longer triggers FAQ because of specific context ('quels droits')
        """
        session_id = f"test_droits_acc_{uuid.uuid4()}"
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "quels sont mes droits apres un accident",
            "session_id": session_id
        }, timeout=60)
        
        assert response.status_code == 200
        data = response.json()
        
        # "quels droits" is a MEDICAL_SIGNAL, should bypass FAQ
        assert data["is_faq"] == False, \
            f"Expected AI response for 'quels droits', got FAQ: {data['response'][:200]}"
        
        print(f"✓ 'Quels droits après accident' correctly returns AI response")
    
    def test_combien_toucher_ipp_returns_ai_not_tarifs(self):
        """
        'combien vais-je toucher pour mon IPP' should return AI response
        NOT FAQ tarifs because of IPP context
        """
        session_id = f"test_toucher_ipp_{uuid.uuid4()}"
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "combien vais-je toucher pour mon IPP",
            "session_id": session_id
        }, timeout=60)
        
        assert response.status_code == 200
        data = response.json()
        
        # "combien toucher" and "ipp" are MEDICAL_SIGNALS, should bypass FAQ
        assert data["is_faq"] == False, \
            f"Expected AI response, got FAQ tarifs: {data['response'][:200]}"
        
        # Should NOT contain tarifs FAQ content
        response_lower = data["response"].lower()
        is_tarifs_faq = "analyse de dossier" in response_lower and "150 euros" in response_lower
        
        assert not is_tarifs_faq, \
            f"Should NOT return tarifs FAQ for IPP question. Got: {data['response'][:300]}"
        
        print(f"✓ 'Combien toucher IPP' correctly returns AI response, not tarifs FAQ")


class TestFAQStillWorksForGeneralQuestions:
    """Tests that FAQ still works for pure general questions (tarifs, contact)"""
    
    def test_tarifs_simple_returns_faq(self):
        """
        'quels sont vos tarifs' should return FAQ response with prices
        """
        session_id = f"test_tarifs_{uuid.uuid4()}"
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "quels sont vos tarifs",
            "session_id": session_id
        }, timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be FAQ response
        assert data["is_faq"] == True, \
            f"Expected FAQ for 'quels sont vos tarifs', got AI: {data['response'][:200]}"
        
        # Should contain price info
        response_text = data["response"]
        has_prices = "150" in response_text or "250" in response_text or "euros" in response_text.lower()
        
        assert has_prices, f"FAQ should contain prices. Got: {response_text}"
        
        print(f"✓ 'Quels sont vos tarifs' correctly returns FAQ with prices")
    
    def test_contact_simple_returns_faq(self):
        """
        'comment vous contacter' should return FAQ response with contact info
        """
        session_id = f"test_contact_{uuid.uuid4()}"
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "comment vous contacter",
            "session_id": session_id
        }, timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be FAQ response
        assert data["is_faq"] == True, \
            f"Expected FAQ for 'comment vous contacter', got AI: {data['response'][:200]}"
        
        # Should contain contact info
        response_text = data["response"].lower()
        has_contact = "email" in response_text or "telephone" in response_text or "contact" in response_text
        
        assert has_contact, f"FAQ should contain contact info. Got: {data['response']}"
        
        print(f"✓ 'Comment vous contacter' correctly returns FAQ with contact info")


class TestAIResponsesIncludeActionableLinks:
    """Tests that AI responses include actionable links to site pages"""
    
    def test_ai_response_includes_links(self):
        """
        AI responses should include actionable links (simulateur, dossier-express, calculatrice-ipp)
        """
        session_id = f"test_links_{uuid.uuid4()}"
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "comment faire reconnaitre ma maladie professionnelle",
            "session_id": session_id
        }, timeout=60)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be AI response
        assert data["is_faq"] == False
        
        response_text = data["response"]
        
        # Check for actionable links
        has_simulateur = "/simulateur" in response_text or "StrategiIA" in response_text
        has_dossier = "/dossier-express" in response_text or "Dossier Express" in response_text
        has_calculatrice = "/calculatrice-ipp" in response_text
        has_agenda = "/agenda" in response_text
        has_ressources = "/ressources" in response_text
        
        has_any_link = has_simulateur or has_dossier or has_calculatrice or has_agenda or has_ressources
        
        assert has_any_link, \
            f"AI response should include actionable links. Got: {response_text[-500:]}"
        
        print(f"✓ AI response includes actionable links")
        if has_simulateur:
            print("  - Found /simulateur or StrategiIA link")
        if has_dossier:
            print("  - Found /dossier-express link")
        if has_calculatrice:
            print("  - Found /calculatrice-ipp link")


class TestQuotaEndpoint:
    """Tests the quota endpoint"""
    
    def test_quota_returns_correct_structure(self):
        """
        GET /api/chatbot/quota returns correct structure with remaining, limit, used
        """
        session_id = f"test_quota_{uuid.uuid4()}"
        
        # First make a request to create session
        requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "test",
            "session_id": session_id
        }, timeout=30)
        
        # Check quota
        response = requests.get(f"{BASE_URL}/api/chatbot/quota/{session_id}", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "remaining" in data
        assert "limit" in data
        assert "used" in data
        
        # Verify values
        assert data["limit"] == 5
        assert data["used"] >= 1
        assert data["remaining"] == 5 - data["used"]
        
        print(f"✓ Quota endpoint returns correct structure: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
