"""Tests for utils/chatbot.py — FAQ matching logic."""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chatbot import find_faq_response, FAQ_DATABASE


class TestFAQDatabase:
    def test_has_entries(self):
        # Depuis la refonte Straté, la FAQ ne couvre que tarifs + contact ;
        # les questions de fond sont routees vers le LLM.
        assert len(FAQ_DATABASE) >= 2

    def test_each_entry_has_keywords(self):
        for topic, data in FAQ_DATABASE.items():
            assert "keywords" in data
            assert "response" in data
            assert len(data["keywords"]) > 0
            assert len(data["response"]) > 50


class TestFindFAQResponse:
    def test_expertise_routed_to_llm(self):
        # Question de fond : ne doit PAS etre captee par la FAQ statique
        r = find_faq_response("Comment préparer une expertise médicale ?")
        assert r is None

    def test_mdph_routed_to_llm(self):
        r = find_faq_response("Je veux des infos sur la MDPH et l'AAH")
        assert r is None

    def test_tarifs_match(self):
        r = find_faq_response("Quel est le tarif de vos services ?")
        assert r is not None
        assert "tarif" in r.lower() or "euros" in r.lower()

    def test_contact_match(self):
        r = find_faq_response("Comment vous contacter ?")
        assert r is not None

    def test_no_match(self):
        r = find_faq_response("Bonjour, je cherche une recette de cuisine")
        assert r is None

    def test_empty_message(self):
        r = find_faq_response("")
        assert r is None

    def test_case_insensitive(self):
        r = find_faq_response("QUELS SONT VOS TARIFS ?")
        assert r is not None
