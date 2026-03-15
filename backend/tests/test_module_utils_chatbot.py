"""Tests for utils/chatbot.py — FAQ matching logic."""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chatbot import find_faq_response, FAQ_DATABASE


class TestFAQDatabase:
    def test_has_entries(self):
        assert len(FAQ_DATABASE) >= 6

    def test_each_entry_has_keywords(self):
        for topic, data in FAQ_DATABASE.items():
            assert "keywords" in data
            assert "response" in data
            assert len(data["keywords"]) > 0
            assert len(data["response"]) > 50


class TestFindFAQResponse:
    def test_expertise_match(self):
        r = find_faq_response("Comment préparer une expertise médicale ?")
        assert r is not None
        assert "expertise" in r.lower() or "préparer" in r.lower()

    def test_mdph_match(self):
        r = find_faq_response("Je veux des infos sur la MDPH et l'AAH")
        assert r is not None
        assert "mdph" in r.lower() or "MDPH" in r

    def test_accident_travail_match(self):
        r = find_faq_response("J'ai eu un accident du travail")
        assert r is not None

    def test_tarifs_match(self):
        r = find_faq_response("Quel est le tarif de vos services ?")
        assert r is not None
        assert "tarif" in r.lower() or "€" in r

    def test_contact_match(self):
        r = find_faq_response("Comment vous contacter ?")
        assert r is not None

    def test_protection_juridique_match(self):
        r = find_faq_response("J'ai besoin de protection juridique")
        assert r is not None

    def test_no_match(self):
        r = find_faq_response("Bonjour, je cherche une recette de cuisine")
        assert r is None

    def test_empty_message(self):
        r = find_faq_response("")
        assert r is None

    def test_case_insensitive(self):
        r = find_faq_response("EXPERTISE MÉDICALE")
        assert r is not None
