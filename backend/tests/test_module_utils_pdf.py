"""Tests for utils/pdf.py — PDF generation."""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf import generate_report_number, generate_secured_pdf, generate_dossier_pdf


class TestReportNumber:
    def test_format(self):
        num = generate_report_number()
        assert num.startswith("SES-")
        parts = num.split("-")
        assert len(parts) == 3
        assert parts[1].isdigit()
        assert len(parts[2]) == 5

    def test_uniqueness(self):
        numbers = {generate_report_number() for _ in range(50)}
        assert len(numbers) >= 45  # Very high probability of uniqueness


class TestSecuredPDF:
    def test_generates_bytes(self):
        pdf = generate_secured_pdf(
            analysis="## Test\nCeci est un test.",
            report_type="Test Report",
            name="Jean Dupont",
            email="jean@test.com",
        )
        assert isinstance(pdf, bytes)
        assert len(pdf) > 1000
        assert pdf[:5] == b"%PDF-"

    def test_with_all_params(self):
        pdf = generate_secured_pdf(
            analysis="# Rapport\n## Section 1\n- Point 1\n- Point 2\n\n### Sous-section\nTexte normal.\n\n**Texte gras**",
            report_type="StrategiIA",
            name="Marie Martin",
            email="marie@test.com",
            type_dossier="Accident du travail",
            regime="Général",
            with_watermark=True,
            report_number="SES-2026-12345",
        )
        assert isinstance(pdf, bytes)
        assert len(pdf) > 2000

    def test_without_watermark(self):
        pdf = generate_secured_pdf(
            analysis="Test content.",
            with_watermark=False,
        )
        assert isinstance(pdf, bytes)
        assert pdf[:5] == b"%PDF-"

    def test_empty_analysis(self):
        pdf = generate_secured_pdf(analysis="")
        assert isinstance(pdf, bytes)

    def test_special_characters(self):
        pdf = generate_secured_pdf(
            analysis="Résumé: éàü ö ñ — test spéciaux € £",
            name="Müller-Straße",
        )
        assert isinstance(pdf, bytes)

    def test_long_analysis(self):
        long_text = "## Section\n" + ("Ceci est un paragraphe de test assez long.\n" * 100)
        pdf = generate_secured_pdf(analysis=long_text)
        assert isinstance(pdf, bytes)
        assert len(pdf) > 5000


class TestDossierPDF:
    def test_generates_pdf(self):
        pdf = generate_dossier_pdf(
            name="Test",
            email="test@test.com",
            type_dossier="AT",
            regime="Général",
            analysis="## Analyse\nContenu du rapport.",
        )
        assert isinstance(pdf, bytes)
        assert pdf[:5] == b"%PDF-"

    def test_premium_no_watermark(self):
        pdf = generate_dossier_pdf(
            name="Test", email="t@t.com", type_dossier="MP",
            regime="Agricole", analysis="Content", premium_pdf=True
        )
        assert isinstance(pdf, bytes)
