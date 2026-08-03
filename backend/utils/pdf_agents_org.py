"""PDF generator for the AI Agents Org Chart.

Produces a sober, premium PDF aligned on S.E.S brand identity.
"""
import os
from datetime import datetime


_LOGO_PATH = os.path.join(os.path.dirname(__file__), "shield_logo.png")

from utils.pdf_fonts import get_liberation_dir

_BLACK = (26, 26, 26)
_GOLD = (201, 168, 76)
_GOLD_LIGHT = (218, 195, 130)
_IVORY = (250, 248, 243)
_IVORY_WARM = (247, 244, 237)
_DARK_TEXT = (35, 35, 35)
_BODY_TEXT = (55, 55, 55)
_MUTED = (130, 125, 118)
_LIGHT_LINE = (220, 215, 205)
_RED = (180, 60, 60)


def _agent_color(agent_id: str) -> tuple:
    """Return (accent, accent_light) for an agent."""
    if agent_id == "editorial_critic":
        return (_RED, (235, 200, 200))
    if agent_id.startswith("editorial_"):
        return ((46, 125, 100), (180, 220, 200))
    if agent_id == "strate":
        return ((45, 80, 140), (175, 200, 230))
    if agent_id == "strategiia":
        return (_GOLD, _GOLD_LIGHT)
    if agent_id == "dossier_express":
        return ((90, 65, 130), (200, 180, 220))
    return (_BLACK, _IVORY_WARM)


def generate_agents_org_pdf(payload: dict) -> bytes:
    """Build PDF from the registry payload returned by /admin/agents/registry."""
    from fpdf import FPDF

    ceo = payload.get("ceo", {}) or {}
    agents = payload.get("agents", []) or []
    gen_date = datetime.now().strftime("%d/%m/%Y à %Hh%M")
    year = datetime.now().year

    LM = 16
    RM = 16
    CW = 210 - LM - RM

    class OrgPDF(FPDF):
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
            self.cell(80, 4, "ORGANIGRAMME IA — DOCUMENT INTERNE")

            self.set_font("LibSans", "", 7)
            self.set_text_color(180, 180, 180)
            self.set_xy(-RM - 65, 6)
            self.cell(65, 4, gen_date, align="R")
            self.set_text_color(*_GOLD_LIGHT)
            self.set_xy(-RM - 65, 11.5)
            self.cell(65, 4, "Cartographie des agents IA", align="R")
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
                f"(c) {year} Stratégie & Expertise Santé — Organigramme IA — Document interne confidentiel — Page {self.page_no()}",
                align="C",
            )

    pdf = OrgPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_left_margin(LM)
    pdf.set_right_margin(RM)
    pdf.add_page()

    # ── Title ──
    pdf.set_font("LibSans", "B", 18)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW, 9, "Organigramme IA")
    pdf.ln(10)
    pdf.set_font("LibSans", "I", 9)
    pdf.set_text_color(*_MUTED)
    pdf.multi_cell(CW, 4.5,
        "Cartographie complète de l'écosystème d'agents IA de la plateforme S.E.S : "
        "rôles, modèles utilisés, prompts système et garde-fous actifs. "
        "Document destiné à la transparence, à l'audit interne et à la conformité RGPD/déontologique."
    )
    pdf.ln(5)

    # ── PDG block ──
    py = pdf.get_y()
    pdf.set_fill_color(*_BLACK)
    pdf.rect(LM, py, CW, 18, "F")
    pdf.set_fill_color(*_GOLD)
    pdf.rect(LM, py, 2.5, 18, "F")
    pdf.set_xy(LM + 8, py + 3)
    pdf.set_font("LibSans", "B", 11)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(CW - 16, 5, ceo.get("name", "PDG Fondateur"))
    pdf.set_xy(LM + 8, py + 9.5)
    pdf.set_font("LibSans", "", 8)
    pdf.set_text_color(*_GOLD_LIGHT)
    pdf.cell(CW - 16, 4, ceo.get("role", "Vision, stratégie, validation finale"))
    pdf.set_xy(LM + 8, py + 13.5)
    pdf.set_font("LibSans", "I", 6.5)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(CW - 16, 3, "Niveau 0 — Supervision humaine de la chaîne IA")
    pdf.set_y(py + 22)

    # ── Connector ──
    pdf.set_draw_color(*_GOLD)
    pdf.set_line_width(0.4)
    pdf.line(105, pdf.get_y(), 105, pdf.get_y() + 4)
    pdf.ln(8)

    # ── Group 1: Visitor-facing agents ──
    visitor_ids = ("strate", "strategiia", "dossier_express")
    visitor_agents = [a for a in agents if a.get("id") in visitor_ids]
    editorial_agents = [a for a in agents if a.get("id", "").startswith("editorial_")]

    def section_header(label: str):
        pdf.set_font("LibSans", "B", 8)
        pdf.set_text_color(*_MUTED)
        pdf.cell(CW, 5, label.upper())
        pdf.ln(6)
        pdf.set_draw_color(*_LIGHT_LINE)
        pdf.set_line_width(0.2)
        sy = pdf.get_y()
        pdf.line(LM, sy, LM + CW, sy)
        pdf.ln(4)

    def agent_summary_card(a: dict):
        accent, accent_light = _agent_color(a.get("id", ""))
        # Compute height needed
        mission_lines = max(2, int(len(a.get("mission", "")) / 90) + 1)
        guardrails = a.get("guardrails", []) or []
        gf_lines = sum(max(1, int(len(g) / 78) + 1) for g in guardrails)
        h = 12 + mission_lines * 4 + 5 + max(1, len(guardrails)) * 4 + (gf_lines - len(guardrails)) * 4 + 6

        # Page-break if needed
        if pdf.get_y() + h > pdf.h - 22:
            pdf.add_page()

        sy = pdf.get_y()
        pdf.set_fill_color(*_IVORY)
        pdf.rect(LM, sy, CW, h, "F")
        pdf.set_fill_color(*accent)
        pdf.rect(LM, sy, 2.5, h, "F")

        # Name + role
        pdf.set_xy(LM + 7, sy + 3)
        pdf.set_font("LibSans", "B", 10)
        pdf.set_text_color(*_BLACK)
        pdf.cell(110, 5, a.get("name", ""))
        # Right: model
        pdf.set_xy(LM + CW - 70, sy + 3)
        pdf.set_font("LibSans", "", 6.5)
        pdf.set_text_color(*_MUTED)
        pdf.cell(70, 5, a.get("model", ""), align="R")

        pdf.set_xy(LM + 7, sy + 8.5)
        pdf.set_font("LibSans", "I", 7.5)
        pdf.set_text_color(*accent)
        pdf.cell(CW - 14, 4, a.get("role", ""))

        # Mission
        pdf.set_xy(LM + 7, sy + 13)
        pdf.set_font("LibSans", "", 7.5)
        pdf.set_text_color(*_BODY_TEXT)
        pdf.multi_cell(CW - 14, 3.8, a.get("mission", ""))

        # Guardrails
        pdf.ln(1)
        pdf.set_x(LM + 7)
        pdf.set_font("LibSans", "B", 6.5)
        pdf.set_text_color(*_MUTED)
        pdf.cell(CW - 14, 3.5, f"GARDE-FOUS ACTIFS ({len(guardrails)})")
        pdf.ln(4)
        pdf.set_font("LibSans", "", 7)
        pdf.set_text_color(*_BODY_TEXT)
        for g in guardrails:
            pdf.set_x(LM + 11)
            bx = pdf.get_x() - 3
            by = pdf.get_y() + 1.5
            pdf.set_fill_color(*accent)
            pdf.rect(bx, by, 1.2, 1.2, "F")
            pdf.multi_cell(CW - 18, 3.6, g)
        pdf.set_y(sy + h + 2)

    if visitor_agents:
        section_header("Niveau 1 — Agents en contact direct avec le visiteur / client")
        for a in visitor_agents:
            agent_summary_card(a)
        pdf.ln(2)

    if editorial_agents:
        if pdf.get_y() > pdf.h - 60:
            pdf.add_page()
        else:
            pdf.ln(3)
        section_header("Niveau 2 — Équipe éditoriale (Studio SEO)")
        for a in editorial_agents:
            agent_summary_card(a)

    # ── Appendix : full prompts ──
    pdf.add_page()
    pdf.set_font("LibSans", "B", 14)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW, 8, "Annexe — Prompts système intégraux")
    pdf.ln(10)
    pdf.set_font("LibSans", "I", 8)
    pdf.set_text_color(*_MUTED)
    pdf.multi_cell(CW, 4.5,
        "Ci-dessous, les prompts système exacts utilisés par chaque agent en production. "
        "Toute modification passe par le code source (les variables sont indiquées sous chaque prompt)."
    )
    pdf.ln(4)

    for a in agents:
        accent, _ = _agent_color(a.get("id", ""))

        # Title
        if pdf.get_y() > pdf.h - 50:
            pdf.add_page()
        pdf.set_font("LibSans", "B", 10)
        pdf.set_text_color(*_BLACK)
        pdf.set_fill_color(*accent)
        pdf.rect(LM, pdf.get_y(), 2.5, 6, "F")
        pdf.set_x(LM + 6)
        pdf.cell(CW - 6, 6, f"{a.get('name', '')} — {a.get('role', '')}")
        pdf.ln(8)

        # Source
        pdf.set_font("LibSans", "", 6.5)
        pdf.set_text_color(*_MUTED)
        src = f"Source : {a.get('file_path', '')} → variable {a.get('prompt_var', '')}"
        pdf.cell(CW, 3.5, src)
        pdf.ln(4.5)

        # Prompt body
        prompt = a.get("prompt") or "(prompt non disponible)"
        # Cap at ~4000 chars to keep PDF reasonable
        if len(prompt) > 4500:
            prompt = prompt[:4500] + "\n\n[... tronqué — voir code source pour la suite]"
        pdf.set_font("LibSans", "", 6.5)
        pdf.set_text_color(*_BODY_TEXT)
        pdf.multi_cell(CW, 3.2, prompt)
        pdf.ln(5)

    # ── Closing confidentiality ──
    if pdf.get_y() > pdf.h - 35:
        pdf.add_page()
    pdf.ln(4)
    pdf.set_draw_color(*_GOLD)
    pdf.set_line_width(0.3)
    pdf.line(LM + 30, pdf.get_y(), LM + CW - 30, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("LibSans", "B", 7)
    pdf.set_text_color(*_MUTED)
    pdf.cell(CW, 4, "Confidentialité", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("LibSans", "I", 6.5)
    pdf.set_text_color(*_MUTED)
    pdf.multi_cell(CW, 3.5,
        "Document interne S.E.S. Diffusion restreinte aux audits, partenaires sous accord "
        "de confidentialité, et autorités compétentes (RGPD, déontologie). "
        "Les prompts sont la propriété intellectuelle de Stratégie & Expertise Santé.",
        align="C",
    )

    return bytes(pdf.output())
