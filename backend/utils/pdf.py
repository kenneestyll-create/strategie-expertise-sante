import re
import os
from datetime import datetime

_LOGO_PATH = os.path.join(os.path.dirname(__file__), "shield_logo.png")


def generate_report_number():
    import random
    year = datetime.now().year
    seq = random.randint(10000, 99999)
    return f"SES-{year}-{seq}"


_STRIP_PATTERNS = [
    re.compile(r'https?://[^\s)]+'),
    re.compile(r'(?i)prendre\s+rendez[- ]?vous.*$'),
    re.compile(r'(?i)premi.re\s+consultation.*gratuit.*$'),
    re.compile(r'(?i)^\W*strat.gie\s*&?\s*expertise\s*sant[eé]?\s*\.?\s*$'),
    re.compile(r'(?i)strategie-expertise-sante\.fr.*$'),
    re.compile(r'(?i)mascot-tips-admin\.preview.*$'),
    re.compile(r'^---+$'),
    # Strip LLM-generated closing phrase (it's hardcoded in the PDF template)
    re.compile(r'(?i)^\W*vous\s+n.{0,3}tes\s+plus\s+seul'),
    re.compile(r'(?i)^\W*d.sormais.*devient\s+votre\s+bouclier'),
]


def _clean_analysis(text: str) -> str:
    cleaned_lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue
        skip = False
        for pat in _STRIP_PATTERNS:
            if pat.search(stripped):
                skip = True
                break
        if skip:
            continue
        cleaned = re.sub(r'https?://[^\s)]+', 'strategie-expertise-sante.fr', stripped)
        cleaned_lines.append(cleaned)
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()
    return "\n".join(cleaned_lines)


# ── Premium color palette ──
_BLACK = (26, 26, 26)        # #1A1A1A
_GOLD = (201, 168, 76)       # #C9A84C
_GOLD_LIGHT = (218, 195, 130)
_IVORY = (250, 248, 243)     # warm cream
_DARK_TEXT = (35, 35, 35)
_BODY_TEXT = (55, 55, 55)
_MUTED = (130, 125, 118)
_LIGHT_LINE = (220, 215, 205)


def _safe(text: str) -> str:
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_secured_pdf(
    analysis: str,
    report_type: str = "Dossier Express IA",
    name: str = "",
    email: str = "",
    type_dossier: str = "",
    regime: str = "",
    with_watermark: bool = True,
    report_number: str = "",
) -> bytes:
    from fpdf import FPDF

    if not report_number:
        report_number = generate_report_number()
    gen_date = datetime.now().strftime("%d/%m/%Y")
    year = datetime.now().year
    analysis = _clean_analysis(analysis)

    LM = 16   # left margin
    RM = 16   # right margin
    CW = 210 - LM - RM   # content width = 178mm

    class PremiumPDF(FPDF):
        def header(self):
            # ── Elegant dark header band ──
            self.set_fill_color(*_BLACK)
            self.rect(0, 0, 210, 22, "F")

            # Gold accent line
            self.set_fill_color(*_GOLD)
            self.rect(0, 22, 210, 0.6, "F")

            # Shield logo (left)
            if os.path.isfile(_LOGO_PATH):
                self.image(_LOGO_PATH, LM, 3, 9, 9)
                text_x = LM + 11
            else:
                text_x = LM

            # Left: brand name
            self.set_text_color(255, 255, 255)
            self.set_font("Helvetica", "B", 11)
            self.set_xy(text_x, 4)
            self.cell(80, 5, "Strategie & Expertise Sante")
            # Subtitle
            self.set_font("Helvetica", "", 6.5)
            self.set_text_color(*_GOLD_LIGHT)
            self.set_xy(text_x, 10)
            self.cell(80, 4, "PIONNIER EN FRANCE")

            # Right: date & report number
            self.set_font("Helvetica", "", 7)
            self.set_text_color(180, 180, 180)
            self.set_xy(-RM - 60, 5)
            self.cell(60, 4, gen_date, align="R")
            self.set_xy(-RM - 60, 10)
            self.set_text_color(*_GOLD_LIGHT)
            self.cell(60, 4, report_number, align="R")

            # Reset position
            self.set_xy(LM, 26)

        def footer(self):
            self.set_y(-12)
            # Gold thin line
            self.set_draw_color(*_GOLD)
            self.set_line_width(0.3)
            self.line(LM, self.get_y(), 210 - RM, self.get_y())
            self.ln(2)
            self.set_font("Helvetica", "", 6)
            self.set_text_color(*_MUTED)
            self.cell(
                CW, 4,
                f"(c) {year} Strategie & Expertise Sante  --  strategie-expertise-sante.fr  --  Document confidentiel",
                align="C",
            )

        def _watermark(self):
            if not with_watermark:
                return
            sx, sy = self.x, self.y
            self.set_font("Helvetica", "B", 38)
            self.set_text_color(240, 238, 232)
            cx, cy = self.w / 2, self.h / 2
            txt = "Strategie & Expertise Sante"
            tw = self.get_string_width(txt)
            with self.rotation(35, cx, cy):
                self.text(cx - tw / 2, cy, txt)
            self.set_xy(sx, sy)

    pdf = PremiumPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_left_margin(LM)
    pdf.set_right_margin(RM)
    pdf.add_page()

    # ── Client info bar ──
    y = pdf.get_y()
    pdf.set_fill_color(*_IVORY)
    pdf.rect(LM, y, CW, 10, "F")
    pdf.set_xy(LM + 4, y + 2)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*_DARK_TEXT)
    safe_name = _safe(name or email or "Client")
    pdf.cell(50, 3, safe_name)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*_MUTED)
    safe_td = _safe(type_dossier or "")
    safe_reg = _safe(regime or "")
    info_parts = [p for p in [safe_td, safe_reg, gen_date] if p]
    pdf.cell(0, 3, "  |  ".join(info_parts))
    pdf.set_xy(LM + 4, y + 6)
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*_GOLD)
    safe_rt = _safe(report_type)
    pdf.cell(0, 3, f"Rapport {safe_rt}")
    pdf.set_xy(LM, y + 12)

    pdf.ln(2)

    # ── Render analysis content with premium typography ──
    def section_title(text):
        pdf.ln(3)
        # Gold left accent
        sy = pdf.get_y()
        pdf.set_fill_color(*_GOLD)
        pdf.rect(LM, sy, 2, 5.5, "F")
        pdf.set_x(LM + 5)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*_BLACK)
        pdf.cell(CW - 5, 5.5, _safe(text))
        pdf.ln(7)

    def sub_title(text):
        pdf.ln(1.5)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*_DARK_TEXT)
        pdf.set_x(LM)
        pdf.cell(CW, 5, _safe(text))
        pdf.ln(5.5)

    def body_text(text):
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*_BODY_TEXT)
        pdf.set_x(LM)
        pdf.multi_cell(CW, 4, _safe(text))
        pdf.ln(0.5)

    def bullet_text(text):
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*_BODY_TEXT)
        pdf.set_x(LM + 4)
        # Gold bullet
        bx, by = pdf.get_x(), pdf.get_y() + 1.5
        pdf.set_fill_color(*_GOLD)
        pdf.rect(bx - 3, by, 1.2, 1.2, "F")
        pdf.multi_cell(CW - 6, 4, _safe(text))
        pdf.ln(0.3)

    def bold_text(text):
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_DARK_TEXT)
        pdf.set_x(LM)
        pdf.multi_cell(CW, 4, _safe(text))
        pdf.ln(0.5)

    def italic_text(text):
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(*_MUTED)
        pdf.set_x(LM)
        pdf.multi_cell(CW, 3.8, _safe(text))
        pdf.ln(0.5)

    def gold_separator():
        sep_y = pdf.get_y()
        pdf.set_draw_color(*_GOLD)
        pdf.set_line_width(0.3)
        pdf.line(LM + 20, sep_y, LM + CW - 20, sep_y)
        pdf.ln(3)

    for line in analysis.split("\n"):
        stripped = line.strip()
        if not stripped:
            pdf.ln(1.5)
            continue
        if stripped == "---" or stripped == "***":
            gold_separator()
        elif stripped.startswith("# "):
            section_title(stripped[2:])
        elif stripped.startswith("## "):
            section_title(stripped[3:])
        elif stripped.startswith("### "):
            sub_title(stripped[4:])
        elif stripped.startswith("- ") or stripped.startswith("* "):
            bullet_text(stripped[2:])
        elif stripped.startswith("**") and stripped.endswith("**"):
            bold_text(stripped.strip("*"))
        elif (stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**")):
            italic_text(stripped.strip("*"))
        elif re.match(r'^\d+\.\s', stripped):
            bullet_text(stripped)
        else:
            body_text(stripped)

    # ── Signature emotionnelle de marque ──
    space = pdf.h - 16 - pdf.get_y()
    if space < 35:
        pdf.add_page()

    pdf.ln(4)
    # Gold thin separator
    sep_y = pdf.get_y()
    pdf.set_draw_color(*_GOLD)
    pdf.set_line_width(0.3)
    pdf.line(55, sep_y, 155, sep_y)
    pdf.ln(5)

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW, 5, _safe("Vous n'etes plus seul(e) face a votre situation."), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "BI", 9)
    pdf.set_text_color(*_GOLD)
    pdf.cell(CW, 5, _safe("Desormais, Strategie & Expertise Sante devient votre bouclier."), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    # Second gold separator
    sep_y2 = pdf.get_y()
    pdf.set_draw_color(*_GOLD)
    pdf.line(55, sep_y2, 155, sep_y2)
    pdf.ln(4)

    # ── Contact & CTA block ──
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW, 4, "Strategie & Expertise Sante", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*_MUTED)
    pdf.cell(CW, 3.5, "Prendre rendez-vous : strategie-expertise-sante.fr/contact", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 6.5)
    pdf.cell(CW, 3.5, "Consultation personnalisee sur rendez-vous  --  Premiere consultation gratuite", align="C")

    # ── Watermark ──
    if with_watermark:
        for p_num in range(1, pdf.pages_count + 1):
            pdf.page = p_num
            pdf._watermark()
        pdf.page = pdf.pages_count

    return bytes(pdf.output())


def generate_dossier_pdf(name, email, type_dossier, regime, analysis, premium_pdf=False):
    return generate_secured_pdf(
        analysis=analysis,
        report_type="Dossier Express IA",
        name=name,
        email=email,
        type_dossier=type_dossier,
        regime=regime,
        with_watermark=not premium_pdf,
    )
