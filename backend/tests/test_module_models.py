"""Tests for models.py — Pydantic model validation."""
import pytest
from datetime import datetime, timezone
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    ContactRequest, ContactRequestCreate,
    FAQItem, FAQItemCreate,
    Avis, AvisCreate,
    AdminLogin, TokenResponse,
    ForumUser, ForumUserRegister, ForumTopicCreate, ForumReplyCreate,
    ChatMessage, ChatResponse,
    PaymentTransaction, CreateCheckoutRequest,
    VisitorCount, ReferralCode, CreateReferralRequest,
    Booking, BookingCreate,
    ClientUser, ClientRegister, ClientLogin, ClientCase,
    SimulatorResult, AbandonedCheckout,
)


class TestContactModels:
    def test_contact_request_create(self):
        c = ContactRequestCreate(nom="Dupont", prenom="Jean", email="j@test.com", sujet="Test", message="Hello")
        assert c.nom == "Dupont"
        assert c.telephone is None

    def test_contact_request_auto_id(self):
        c = ContactRequest(nom="X", prenom="Y", email="a@b.com", sujet="S", message="M")
        assert c.id is not None
        assert c.status == "nouveau"

    def test_contact_update_optional(self):
        from models import ContactRequestUpdate
        u = ContactRequestUpdate()
        assert u.status is None
        assert u.notes is None


class TestFAQModels:
    def test_faq_item_defaults(self):
        f = FAQItem(question="Q?", reponse="A.")
        assert f.categorie == "Général"
        assert f.ordre == 0

    def test_faq_create(self):
        f = FAQItemCreate(question="Q?", reponse="A.", categorie="MDPH", ordre=5)
        assert f.categorie == "MDPH"


class TestAvisModels:
    def test_avis_valid(self):
        a = AvisCreate(nom="Test", note=5, commentaire="Super")
        assert a.note == 5

    def test_avis_note_out_of_range(self):
        with pytest.raises(Exception):
            AvisCreate(nom="Test", note=6, commentaire="Oops")

    def test_avis_note_zero(self):
        with pytest.raises(Exception):
            AvisCreate(nom="Test", note=0, commentaire="Oops")


class TestForumModels:
    def test_forum_user_defaults(self):
        u = ForumUser(pseudo="testuser", password_hash="hash")
        assert u.is_anonymous is False
        assert u.is_banned is False
        assert u.posts_count == 0

    def test_forum_register_anonymous(self):
        r = ForumUserRegister(pseudo="anon", is_anonymous=True)
        assert r.email is None
        assert r.is_anonymous is True

    def test_topic_create(self):
        t = ForumTopicCreate(category_id="mdph", title="Help", content="I need help")
        assert t.category_id == "mdph"

    def test_reply_create(self):
        r = ForumReplyCreate(content="Reply text")
        assert r.content == "Reply text"


class TestPaymentModels:
    def test_payment_transaction_defaults(self):
        p = PaymentTransaction(session_id="s1", package_id="test", package_name="Test", amount=100)
        assert p.status == "pending"
        assert p.currency == "eur"

    def test_checkout_request(self):
        c = CreateCheckoutRequest(package_id="analyse_dossier", origin_url="https://example.com")
        assert c.customer_email is None
        assert c.referral_code is None


class TestClientModels:
    def test_client_register(self):
        c = ClientRegister(email="test@t.com", password="pass", name="Test", notifications_email=True, notifications_push=False)
        assert c.notifications_push is False

    def test_client_case_defaults(self):
        c = ClientCase(client_id="c1", title="Mon dossier")
        assert c.status == "en_cours"
        assert c.updates == []


class TestMiscModels:
    def test_booking_create(self):
        b = BookingCreate(date="2026-04-01", time_slot="09:00", name="Test", email="t@t.com")
        assert b.phone is None

    def test_simulator_result(self):
        s = SimulatorResult(answers={"q1": "a1"}, profile="AT", recommendations=["R1"])
        assert len(s.recommendations) == 1

    def test_abandoned_checkout(self):
        a = AbandonedCheckout(email="t@t.com")
        assert a.relance_sent is False
        assert a.amount == 0

    def test_referral_code(self):
        r = ReferralCode(code="ABC123", owner_email="t@t.com")
        assert r.uses_count == 0
        assert r.is_active is True

    def test_chat_message(self):
        m = ChatMessage(message="Bonjour")
        assert m.session_id is None

    def test_chat_response(self):
        r = ChatResponse(response="Bonjour !")
        assert r.is_faq is False

    def test_admin_login(self):
        a = AdminLogin(email="admin@test.com", password="pass")
        assert a.email == "admin@test.com"

    def test_token_response(self):
        t = TokenResponse(access_token="tok123")
        assert t.token_type == "bearer"
        assert t.admin_name == ""
