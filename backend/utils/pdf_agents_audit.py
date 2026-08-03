"""PDF generator for the AI Agents Audit Report (versioning).

Sober, professional, audit-oriented. Designed for CNIL/déontologie compliance.
"""
import os
from datetime import datetime


_LOGO_PATH = os.path.join(os.path.dirname(__file__), "shield_logo.png")

from utils.pdf_fonts import get_liberation_dir

_BLACK = (26, 26, 26)
_GOLD = (201, 168, 76)
_GOLD_LIGHT = (218, 195, 130)
_IVORY = (250, 248, 243)
_DARK_TEXT = (35, 35, 35)
_BODY_TEXT = (55, 55, 55)
_MUTED = (130, 125, 118)
_LIGHT_LINE = (220, 215, 205)


def generate_audit_pdf(versions: list[dict]) -> bytes:
    """Build an audit PDF from a chronological list of snapshot versions (newest first)."""
    from fpdf import FPDF

    gen_date = datetime.now().strftime("%d/%m/%Y à %Hh%M")
    year = datetime.now().year

    LM = 16
    RM = 16
    CW = 210 - LM - RM

    class AuditPDF(FPDF):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            FONT_DIR = get_liberation_dir()
            self.add_font("LibSans", "", os.path.join(FONT_DIR, "LiberationSans-Regular.ttf"), uni=True)
            self.add_font("LibSans", "B", os.path.join(FONT_DIR, "LiberationSans-Bold.ttf"), uni=True)
            self.add_font("LibSans", "I", os.path.join(FONT_DIR, "LiberationSans-Italic.ttf"), uni=True)

        def header(self):
            self.set_fill_color(*_BLACK)
            self.rect(0, 0, 210, 23, "F")
            self.set_fill_color(*_GOLD)
            self.rect(0, 23, 210, 0.7, "F")

            if os.path.isfile(_LOGO_PATH):
                self.image(_LOGO_PATH, LM, 3.5, 9, 9)
                tx = LM + 12
            else:
                tx = LM
            self.set_text_color(255, 255, 255)
            self.set_font("LibSans", "B", 11)
            self.set_xy(tx, 4.5)
            self.cell(80, 5, "Stratégie & Expertise Santé")
            self.set_font("LibSans", "", 6.5)
            self.set_text_color(*_GOLD_LIGHT)
            self.set_xy(tx, 10.5)
            self.cell(80, 4, "RAPPORT D'AUDIT IA — VERSIONING")

            self.set_font("LibSans", "", 7)
            self.set_text_color(180, 180, 180)
            self.set_xy(-RM - 65, 6)
            self.cell(65, 4, gen_date, align="R")
            self.set_text_color(*_GOLD_LIGHT)
            self.set_xy(-RM - 65, 11.5)
            self.cell(65, 4, f"{len(versions)} version(s) archivée(s)", align="R")
            self.set_xy(LM, 28)

        def footer(self):
            self.set_y(-13)
            self.set_draw_color(*_GOLD)
            self.set_line_width(0.3)
            self.line(LM, self.get_y(), 210 - RM, self.get_y())
            self.ln(2.5)
            self.set_font("LibSans", "", 5.5)
            self.set_text_color(*_MUTED)
            self.cell(
                CW, 3.5,
                f"(c) {year} S.E.S — Rapport d'audit IA — Document interne confidentiel — Page {self.page_no()}",
                align="C",
            )

    pdf = AuditPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_left_margin(LM)
    pdf.set_right_margin(RM)
    pdf.add_page()

    # ── Title ──
    pdf.set_font("LibSans", "B", 18)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW, 9, "Rapport d'audit — Versioning IA")
    pdf.ln(11)
    pdf.set_font("LibSans", "I", 9)
    pdf.set_text_color(*_MUTED)
    pdf.multi_cell(CW, 4.5,
        "Historique chronologique des évolutions des agents IA, prompts système, "
        "règles Red Flags, base juridique et paramètres de workflow. "
        "Document destiné à la gouvernance interne, à l'audit CNIL/déontologique "
        "et à la traçabilité des décisions éditoriales."
    )
    pdf.ln(6)

    # ── Synthesis ──
    sy = pdf.get_y()
    pdf.set_fill_color(*_IVORY)
    pdf.rect(LM, sy, CW, 22, "F")
    pdf.set_fill_color(*_GOLD)
    pdf.rect(LM, sy, 2.5, 22, "F")

    pdf.set_xy(LM + 7, sy + 3)
    pdf.set_font("LibSans", "B", 9)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW - 14, 5, "Synthèse")

    pdf.set_xy(LM + 7, sy + 9)
    pdf.set_font("LibSans", "", 7.5)
    pdf.set_text_color(*_BODY_TEXT)
    if versions:
        first = versions[-1]
        last = versions[0]
        line1 = f"Première version : {first.get('created_at', '')[:16].replace('T', ' ')} — {first.get('created_by', '')}"
        line2 = f"Dernière version : {last.get('created_at', '')[:16].replace('T', ' ')} — {last.get('created_by', '')}"
        line3 = f"Total snapshots : {len(versions)}"
        pdf.cell(CW - 14, 4, line1, new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(LM + 7)
        pdf.cell(CW - 14, 4, line2, new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(LM + 7)
        pdf.cell(CW - 14, 4, line3)
    else:
        pdf.cell(CW - 14, 4, "Aucune version archivée à ce jour")
    pdf.set_y(sy + 26)

    # ── Chronological table of versions ──
    pdf.set_font("LibSans", "B", 8)
    pdf.set_text_color(*_MUTED)
    pdf.cell(CW, 5, "HISTORIQUE CHRONOLOGIQUE (du plus récent au plus ancien)")
    pdf.ln(7)

    for idx, v in enumerate(versions):
        # Page-break safety
        if pdf.get_y() > pdf.h - 70:
            pdf.add_page()

        vy = pdf.get_y()
        pdf.set_fill_color(*_IVORY) if idx % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        # Compute card height based on changes count
        changes = v.get("changes_summary", []) or []
        card_h = 22 + max(1, len(changes)) * 4 + 4

        pdf.set_fill_color(*_IVORY)
        pdf.rect(LM, vy, CW, card_h, "F")
        pdf.set_fill_color(*_GOLD)
        pdf.rect(LM, vy, 2, card_h, "F")

        # Header line: date + author + type
        pdf.set_xy(LM + 7, vy + 2.5)
        pdf.set_font("LibSans", "B", 8.5)
        pdf.set_text_color(*_BLACK)
        date_str = v.get("created_at", "")[:16].replace("T", " ")
        pdf.cell(60, 4, f"v{v.get('seq', '?')} — {date_str}")

        # Source on the right
        pdf.set_xy(LM + CW - 60, vy + 2.5)
        pdf.set_font("LibSans", "", 7)
        pdf.set_text_color(*_MUTED)
        pdf.cell(60, 4, v.get("source", "manual"), align="R")

        # Author + note
        pdf.set_xy(LM + 7, vy + 7)
        pdf.set_font("LibSans", "", 7)
        pdf.set_text_color(*_BODY_TEXT)
        author = v.get("created_by", "—")
        notes = v.get("notes", "") or "(aucune note)"
        pdf.cell(CW - 14, 3.5, f"Auteur : {author}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(LM + 7)
        pdf.set_font("LibSans", "I", 6.8)
        pdf.set_text_color(*_MUTED)
        # Truncate notes safely
        if len(notes) > 130:
            notes = notes[:127] + "..."
        pdf.cell(CW - 14, 3, f"Note : {notes}")

        # Changes list
        cy = vy + 14
        pdf.set_xy(LM + 7, cy)
        pdf.set_font("LibSans", "B", 6.5)
        pdf.set_text_color(*_MUTED)
        pdf.cell(CW - 14, 3.5, "MODIFICATIONS")
        cy += 4

        pdf.set_font("LibSans", "", 6.8)
        pdf.set_text_color(*_BODY_TEXT)
        for ch in changes:
            pdf.set_xy(LM + 11, cy)
            bx = pdf.get_x() - 3
            by = pdf.get_y() + 1
            pdf.set_fill_color(*_GOLD)
            pdf.rect(bx, by, 1.2, 1.2, "F")
            text = ch
            if len(text) > 145:
                text = text[:142] + "..."
            pdf.cell(CW - 18, 3.5, text)
            cy += 4

        pdf.set_y(vy + card_h + 2)

    # ── Appendix: hashes for integrity check ──
    pdf.add_page()
    pdf.set_font("LibSans", "B", 14)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW, 8, "Annexe — Empreintes d'intégrité (SHA-256)")
    pdf.ln(10)
    pdf.set_font("LibSans", "I", 8)
    pdf.set_text_color(*_MUTED)
    pdf.multi_cell(CW, 4.5,
        "Pour chaque version, l'empreinte SHA-256 ci-dessous permet de vérifier qu'aucune "
        "modification a posteriori n'a été apportée au snapshot. Toute différence entre "
        "l'empreinte stockée en base et celle recalculée témoigne d'une altération."
    )
    pdf.ln(4)

    pdf.set_font("LibSans", "B", 6.5)
    pdf.set_text_color(*_MUTED)
    sy = pdf.get_y()
    pdf.set_fill_color(*_IVORY)
    pdf.rect(LM, sy, CW, 6, "F")
    pdf.set_xy(LM + 3, sy + 1)
    pdf.cell(20, 4, "VERSION")
    pdf.set_xy(LM + 25, sy + 1)
    pdf.cell(35, 4, "DATE")
    pdf.set_xy(LM + 60, sy + 1)
    pdf.cell(CW - 60, 4, "EMPREINTE SHA-256")
    pdf.set_y(sy + 7)

    pdf.set_font("LibSans", "", 6)
    pdf.set_text_color(*_BODY_TEXT)
    for v in versions:
        if pdf.get_y() > pdf.h - 18:
            pdf.add_page()
        ry = pdf.get_y()
        pdf.set_xy(LM + 3, ry)
        pdf.cell(20, 3.5, f"v{v.get('seq', '?')}")
        pdf.set_xy(LM + 25, ry)
        pdf.cell(35, 3.5, v.get("created_at", "")[:16].replace("T", " "))
        pdf.set_xy(LM + 60, ry)
        h = v.get("hash", "")
        pdf.cell(CW - 60, 3.5, h)
        pdf.ln(4)

    # ── Closing ──
    if pdf.get_y() > pdf.h - 35:
        pdf.add_page()
    pdf.ln(6)
    pdf.set_draw_color(*_GOLD)
    pdf.set_line_width(0.3)
    pdf.line(LM + 30, pdf.get_y(), LM + CW - 30, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("LibSans", "B", 7)
    pdf.set_text_color(*_MUTED)
    pdf.cell(CW, 4, "Document d'audit interne", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("LibSans", "I", 6.5)
    pdf.set_text_color(*_MUTED)
    pdf.multi_cell(CW, 3.5,
        "Ce rapport établit l'historique des évolutions des composants IA de la plateforme S.E.S. "
        "Il peut être communiqué dans le cadre d'un audit qualité, d'un contrôle CNIL ou d'une "
        "vérification déontologique. Les snapshots sont produits soit manuellement par "
        "l'administrateur, soit automatiquement au démarrage du backend si une modification "
        "de configuration est détectée.",
        align="C",
    )

    return bytes(pdf.output())
