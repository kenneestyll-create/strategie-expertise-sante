"""P3 — Test automatise du systeme PDF (ordre executif 08/2026).

A executer avant chaque mise en production :
    cd /app/backend && python -m pytest tests/test_pdf_system.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_fonts import BUNDLED_DIR, REQUIRED_FONTS, check_pdf_fonts, get_liberation_dir
from utils.pdf import generate_dossier_pdf

_ANALYSIS = """## Synthèse de votre situation
Votre dossier concerne une expertise médicale suite à un accident du travail.
Les éléments transmis révèlent des séquelles évaluées à 12 % d'IPP.

## Points de vigilance
- Le délai de contestation de 2 mois court à compter de la notification.
- Le coefficient professionnel n'a pas été appliqué.

## Stratégie recommandée
Saisir la CMRA par courrier recommandé et préparer un dossier médical
contradictoire avec accents : é è à ù ç œ — caractères spéciaux € « » testés.
"""


def _make_pdf():
    return generate_dossier_pdf(
        "Jean Testeur", "test@example.com", "Expertise médicale", "general",
        _ANALYSIS, premium_pdf=False, document_details=None,
    )


def test_bundled_fonts_present_and_readable():
    for f in REQUIRED_FONTS:
        path = os.path.join(BUNDLED_DIR, f)
        assert os.path.isfile(path), f"Police embarquee manquante: {path}"
        assert os.access(path, os.R_OK), f"Police non lisible: {path}"
        assert os.path.getsize(path) > 100_000, f"Police corrompue (taille anormale): {path}"


def test_font_check_reports_ok():
    report = check_pdf_fonts()
    assert report["ok"] is True, f"check_pdf_fonts KO: {report}"
    assert report["dir"] == BUNDLED_DIR, "Les polices embarquees doivent etre prioritaires"


def test_get_liberation_dir_returns_bundled():
    assert get_liberation_dir() == BUNDLED_DIR


def test_generate_full_pdf_not_empty():
    pdf = _make_pdf()
    assert pdf is not None, "PDF non genere"
    data = bytes(pdf)
    assert len(data) > 10_000, f"PDF anormalement petit: {len(data)} bytes"
    assert data[:5] == b"%PDF-", "Signature PDF invalide"
    assert b"%%EOF" in data[-1024:], "Fin de fichier PDF invalide"


def test_fonts_embedded_in_pdf():
    data = bytes(_make_pdf())
    assert b"LiberationSans" in data, "Polices LiberationSans non integrees au PDF"


def test_premium_pdf_variant():
    pdf = generate_dossier_pdf(
        "Marie Testeuse", "test2@example.com", "Demande MDPH / AAH", "general",
        _ANALYSIS, premium_pdf=True, document_details=[{"filename": "certificat.pdf", "pages": 3}],
    )
    data = bytes(pdf)
    assert len(data) > 10_000 and data[:5] == b"%PDF-"
