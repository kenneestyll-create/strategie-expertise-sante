"""Resolution des polices PDF — correctif definitif (ordre executif 08/2026).

Les polices LiberationSans sont embarquees dans le repo (backend/fonts/) pour
ne plus dependre des paquets systeme de l'image de deploiement. Le dossier
systeme reste un repli.
"""
import os
import logging

logger = logging.getLogger(__name__)

BUNDLED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
SYSTEM_DIR = "/usr/share/fonts/truetype/liberation"
REQUIRED_FONTS = [
    "LiberationSans-Regular.ttf",
    "LiberationSans-Bold.ttf",
    "LiberationSans-Italic.ttf",
    "LiberationSans-BoldItalic.ttf",
]


def _dir_ok(d: str) -> bool:
    return all(
        os.path.isfile(os.path.join(d, f)) and os.access(os.path.join(d, f), os.R_OK)
        for f in REQUIRED_FONTS
    )


def get_liberation_dir() -> str:
    """Polices embarquees du repo en priorite, repli sur le dossier systeme."""
    if _dir_ok(BUNDLED_DIR):
        return BUNDLED_DIR
    if _dir_ok(SYSTEM_DIR):
        logger.warning("PDF fonts: polices embarquees absentes, repli systeme %s", SYSTEM_DIR)
        return SYSTEM_DIR
    raise RuntimeError(
        f"Polices PDF introuvables: {REQUIRED_FONTS} absentes de {BUNDLED_DIR} et {SYSTEM_DIR}"
    )


def check_pdf_fonts() -> dict:
    """Controle de demarrage: presence + accessibilite + droits de lecture."""
    report = {"ok": False, "dir": None, "files": {}}
    for d in (BUNDLED_DIR, SYSTEM_DIR):
        if _dir_ok(d):
            report["ok"] = True
            report["dir"] = d
            report["files"] = {f: "ok" for f in REQUIRED_FONTS}
            return report
    for f in REQUIRED_FONTS:
        p = os.path.join(BUNDLED_DIR, f)
        if not os.path.isfile(p):
            report["files"][f] = "MANQUANTE"
        elif not os.access(p, os.R_OK):
            report["files"][f] = "ILLISIBLE (droits)"
        else:
            report["files"][f] = "ok"
    return report
