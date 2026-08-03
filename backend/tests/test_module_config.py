"""Tests for config.py — constants, DB connection, env vars."""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_db_connection():
    from config import db, client
    assert db is not None
    assert client is not None


def test_payment_packages_complete():
    from config import PAYMENT_PACKAGES
    assert len(PAYMENT_PACKAGES) == 11
    for key, pkg in PAYMENT_PACKAGES.items():
        assert "name" in pkg
        assert "amount" in pkg
        assert "currency" in pkg
        assert pkg["amount"] > 0
        assert pkg["currency"] == "eur"


def test_payment_packages_keys():
    from config import PAYMENT_PACKAGES
    expected = {"dossier_express", "analyse_dossier", "preparation_expertise",
                "accompagnement_mdph", "protection_juridique", "accompagnement_complet",
                "urgent_analyse_dossier", "urgent_preparation_expertise",
                "urgent_accompagnement_mdph", "urgent_accompagnement_complet",
                "appel_conseil"}
    assert set(PAYMENT_PACKAGES.keys()) == expected


def test_available_slots():
    from config import AVAILABLE_SLOTS
    assert len(AVAILABLE_SLOTS) == 8
    for slot in AVAILABLE_SLOTS:
        h, m = slot.split(":")
        assert 0 <= int(h) <= 23
        assert int(m) in (0, 15, 30)


def test_document_categories():
    from config import DOCUMENT_CATEGORIES, DOCUMENT_STATUSES
    assert "at" in DOCUMENT_CATEGORIES
    assert "mp" in DOCUMENT_CATEGORIES
    assert "mdph" in DOCUMENT_CATEGORIES
    assert len(DOCUMENT_STATUSES) == 4


def test_sitemap_pages():
    from config import SITEMAP_PAGES, SITE_URL
    assert len(SITEMAP_PAGES) > 20
    assert SITE_URL.startswith("https://")
    for path, priority, freq in SITEMAP_PAGES:
        assert path.startswith("/")
        assert 0 < float(priority) <= 1.0
        assert freq in ("daily", "weekly", "monthly", "yearly")


def test_security_objects():
    from config import security, security_optional
    assert security is not None
    assert security_optional is not None


def test_jwt_constants():
    from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS
    assert JWT_SECRET
    assert JWT_ALGORITHM == "HS256"
    assert JWT_EXPIRATION_HOURS == 24
