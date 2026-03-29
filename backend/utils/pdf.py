import re
import os
import tempfile
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
    re.compile(r'(?i)preview\.emergentagent\.com.*$'),
    re.compile(r'^---+$'),
    re.compile(r'(?i)^\W*vous\s+n.{0,3}tes\s+plus\s+seul'),
    re.compile(r'(?i)^\W*d.sormais.*devient\s+votre\s+bouclier'),
    re.compile(r'(?i)^\W*d.r.navant.*bouclier'),
    re.compile(r'(?i)^\W*et\s+maintenant\s*\??'),
    re.compile(r'(?i)^\W*vous\s+souhaitez\s+aller\s+plus\s+loin'),
    re.compile(r'(?i)^\W*premi.re\s+consultation\s+offerte'),
    re.compile(r'(?i)^\W*votre\s+bouclier\.?\s*$'),
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
_BLACK = (26, 26, 26)
_GOLD = (201, 168, 76)
_GOLD_LIGHT = (218, 195, 130)
_GOLD_SUBTLE = (235, 225, 200)
_IVORY = (250, 248, 243)
_IVORY_WARM = (247, 244, 237)
_DARK_TEXT = (35, 35, 35)
_BODY_TEXT = (55, 55, 55)
_MUTED = (130, 125, 118)
_LIGHT_LINE = (220, 215, 205)
# StrategiIA accent — deep warm black with gold highlights
_STRAT_ACCENT = (45, 38, 28)
_STRAT_BG = (252, 250, 246)
# Dossier Express accent — authoritative navy
_DE_ACCENT = (26, 35, 58)
_DE_ACCENT_LIGHT = (42, 55, 85)
_DE_BG = (245, 247, 252)


def _safe(text: str) -> str:
    return text.encode("latin-1", "replace").decode("latin-1")


def _detect_vigilance_level(analysis: str) -> tuple:
    """Detect the sensitivity level of a dossier from analysis content."""
    text = analysis.lower()
    high_kw = ["faute inexcusable", "contentieux", "tribunal", "expertise judiciaire",
               "recours", "contestation", "urgence", "danger", "amiante", "deces",
               "mesotheliome", "cancer", "incapacite permanente", "licenciement",
               "inaptitude", "refus cpam", "refus cra"]
    med_kw = ["expertise medicale", "consolidation", "rechute", "aggravation",
              "ipp", "rente", "prejudice", "indemnisation", "sous-evalue",
              "taux conteste", "prolongation", "mi-temps therapeutique"]
    high_count = sum(1 for kw in high_kw if kw in text)
    med_count = sum(1 for kw in med_kw if kw in text)
    if high_count >= 3:
        return ("Vigilance elevee", 3, "Ce dossier presente des enjeux significatifs qui meritent une attention prioritaire.")
    elif high_count >= 1 or med_count >= 3:
        return ("Attention soutenue", 2, "Plusieurs elements de ce dossier necessitent une analyse approfondie.")
    else:
        return ("Suivi recommande", 1, "Ce dossier contient des elements a structurer pour securiser votre situation.")


def generate_secured_pdf(
    analysis: str,
    report_type: str = "Dossier Express IA",
    name: str = "",
    email: str = "",
    type_dossier: str = "",
    regime: str = "",
    with_watermark: bool = True,
    report_number: str = "",
    relecture_expert: bool = False,
    document_details: list = None,
) -> bytes:
    from fpdf import FPDF

    if not report_number:
        report_number = generate_report_number()
    gen_date = datetime.now().strftime("%d/%m/%Y")
    year = datetime.now().year
    analysis = _clean_analysis(analysis)

    is_strategiia = "strategi" in report_type.lower()
    is_dossier_express = not is_strategiia

    # Service-specific identity
    if is_strategiia:
        accent = _STRAT_ACCENT
        accent_light = _GOLD_LIGHT
        service_label = "Analyse Strategique Premium"
        service_tagline = "Regard expert sur votre situation"
    else:
        accent = _DE_ACCENT
        accent_light = _DE_ACCENT_LIGHT
        service_label = "Pre-analyse Documentaire"
        service_tagline = "Etude structuree de vos pieces"

    LM = 16
    RM = 16
    CW = 210 - LM - RM

    class PremiumPDF(FPDF):
        def header(self):
            # Dark header band
            self.set_fill_color(*_BLACK)
            self.rect(0, 0, 210, 23, "F")

            # Service-specific accent line
            self.set_fill_color(*_GOLD)
            self.rect(0, 23, 210, 0.7, "F")

            # Logo
            if os.path.isfile(_LOGO_PATH):
                self.image(_LOGO_PATH, LM, 3.5, 9, 9)
                text_x = LM + 12
            else:
                text_x = LM

            # Brand name
            self.set_text_color(255, 255, 255)
            self.set_font("Helvetica", "B", 11)
            self.set_xy(text_x, 4.5)
            self.cell(80, 5, "Strategie & Expertise Sante")
            # Pioneer line
            self.set_font("Helvetica", "", 6.5)
            self.set_text_color(*_GOLD_LIGHT)
            self.set_xy(text_x, 10.5)
            self.cell(80, 4, "PIONNIER EN FRANCE")

            # Right: date, number, service badge
            self.set_font("Helvetica", "", 7)
            self.set_text_color(180, 180, 180)
            self.set_xy(-RM - 65, 4)
            self.cell(65, 4, gen_date, align="R")
            self.set_text_color(*_GOLD_LIGHT)
            self.set_xy(-RM - 65, 8.5)
            self.cell(65, 4, report_number, align="R")
            # Service type badge
            self.set_font("Helvetica", "B", 5.5)
            self.set_text_color(200, 200, 200)
            self.set_xy(-RM - 65, 14)
            self.cell(65, 4, _safe(service_label.upper()), align="R")

            self.set_xy(LM, 27)

        def footer(self):
            self.set_y(-13)
            # Gold thin line
            self.set_draw_color(*_GOLD)
            self.set_line_width(0.3)
            self.line(LM, self.get_y(), 210 - RM, self.get_y())
            self.ln(2.5)
            self.set_font("Helvetica", "", 5.5)
            self.set_text_color(*_MUTED)
            footer_txt = f"(c) {year} Strategie & Expertise Sante -- {report_number} -- Document confidentiel -- Analyse preliminaire a visee informative -- strategie-expertise-sante.fr"
            self.cell(
                CW, 3.5,
                footer_txt,
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
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_left_margin(LM)
    pdf.set_right_margin(RM)
    pdf.add_page()

    # ── Client info bar ──
    y = pdf.get_y()
    pdf.set_fill_color(*_IVORY)
    pdf.rect(LM, y, CW, 12, "F")
    # Left accent bar
    if is_strategiia:
        pdf.set_fill_color(*_GOLD)
    else:
        pdf.set_fill_color(*_DE_ACCENT)
    pdf.rect(LM, y, 2, 12, "F")

    pdf.set_xy(LM + 6, y + 2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*_DARK_TEXT)
    safe_name = _safe(name or email or "Client")
    pdf.cell(60, 4, safe_name)

    # Client metadata
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*_MUTED)
    safe_td = _safe(type_dossier or "")
    safe_reg = _safe(regime or "")
    info_parts = [p for p in [safe_td, safe_reg] if p]
    if info_parts:
        pdf.cell(0, 4, "  |  ".join(info_parts))

    pdf.set_xy(LM + 6, y + 7)
    pdf.set_font("Helvetica", "", 6.5)
    if is_strategiia:
        pdf.set_text_color(*_GOLD)
    else:
        pdf.set_text_color(*_DE_ACCENT)
    safe_rt = _safe(report_type)
    pdf.cell(60, 3, f"Rapport {safe_rt}")
    pdf.set_text_color(*_MUTED)
    pdf.cell(0, 3, f"  |  {gen_date}")
    pdf.set_xy(LM, y + 14)

    # ── Relecture expert badge ──
    if relecture_expert:
        ry = pdf.get_y()
        pdf.set_fill_color(26, 26, 46)
        pdf.rect(LM, ry, CW, 9, "F")
        pdf.set_fill_color(*_GOLD)
        pdf.rect(LM, ry, 2, 9, "F")
        pdf.set_xy(LM + 6, ry + 2)
        pdf.set_font("Helvetica", "BI", 7)
        pdf.set_text_color(*_GOLD)
        pdf.cell(0, 5, _safe("Document relu et finalise dans le cadre de l'option Relecture expert personnalisee"))
        pdf.set_xy(LM, ry + 11)

    pdf.ln(3)

    # ══════════════════════════════════════════════════════════════
    # StrategiIA: Vigilance Level Indicator
    # ══════════════════════════════════════════════════════════════
    if is_strategiia:
        level_label, level_num, level_desc = _detect_vigilance_level(analysis)
        vy = pdf.get_y()
        box_h = 16
        pdf.set_fill_color(*_STRAT_BG)
        pdf.rect(LM, vy, CW, box_h, "F")
        pdf.set_fill_color(*_GOLD)
        pdf.rect(LM, vy, CW, 0.4, "F")
        pdf.rect(LM, vy + box_h - 0.4, CW, 0.4, "F")

        # Label
        pdf.set_xy(LM + 5, vy + 2)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*_MUTED)
        pdf.cell(30, 3.5, "NIVEAU DE VIGILANCE")

        # Gauge dots
        dot_x = LM + 5
        dot_y = vy + 7
        dot_r = 2.2
        for i in range(3):
            if i < level_num:
                pdf.set_fill_color(*_GOLD)
            else:
                pdf.set_fill_color(*_GOLD_SUBTLE)
            pdf.ellipse(dot_x + i * 8, dot_y, dot_r * 2, dot_r * 2, "F")

        # Level text
        pdf.set_xy(dot_x + 28, vy + 6.5)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*_DARK_TEXT)
        pdf.cell(40, 4, _safe(level_label))

        # Description
        pdf.set_xy(dot_x + 28, vy + 11)
        pdf.set_font("Helvetica", "I", 6.5)
        pdf.set_text_color(*_BODY_TEXT)
        pdf.cell(CW - 40, 3.5, _safe(level_desc))

        pdf.set_xy(LM, vy + box_h + 4)

    # ══════════════════════════════════════════════════════════════
    # Dossier Express: Document Summary Compact
    # ══════════════════════════════════════════════════════════════
    if is_dossier_express and document_details:
        total_docs = len(document_details)
        total_pages = sum(d.get("pages", 0) for d in document_details)
        statuses = [d.get("status", "") for d in document_details]

        if all(s == "text_extracted" for s in statuses):
            level = "Excellente"
        elif all(s == "ocr_extracted" for s in statuses):
            level = "Bonne"
        elif all(s in ("text_extracted", "ocr_extracted") for s in statuses) and any(s == "ocr_extracted" for s in statuses):
            level = "Tres bonne"
        elif any(s in ("text_extracted", "ocr_extracted") for s in statuses):
            level = "Partielle"
        else:
            level = "Limitee"

        dy = pdf.get_y()
        box_h = 14
        pdf.set_fill_color(*_DE_BG)
        pdf.rect(LM, dy, CW, box_h, "F")
        pdf.set_fill_color(*_DE_ACCENT)
        pdf.rect(LM, dy, 2, box_h, "F")

        # Title
        pdf.set_xy(LM + 6, dy + 2)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*_DE_ACCENT)
        pdf.cell(50, 3.5, "BASE DOCUMENTAIRE EXPLOITEE")

        # Metrics in a row
        col_w = (CW - 12) / 3
        metrics = [
            (str(total_docs), "pieces analysees"),
            (str(total_pages) if total_pages > 0 else "-", "pages exploitees"),
            (level, "qualite d'extraction"),
        ]
        for i, (val, label) in enumerate(metrics):
            cx = LM + 6 + col_w * i
            pdf.set_xy(cx, dy + 7)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*_DARK_TEXT)
            pdf.cell(col_w, 4, _safe(val), align="C")
            pdf.set_xy(cx, dy + 11)
            pdf.set_font("Helvetica", "", 5.5)
            pdf.set_text_color(*_MUTED)
            pdf.cell(col_w, 2.5, _safe(label), align="C")

        pdf.set_xy(LM, dy + box_h + 4)

    # ══════════════════════════════════════════════════════════════
    # Render analysis — enhanced typography
    # ══════════════════════════════════════════════════════════════
    section_count = 0

    def section_title(text):
        nonlocal section_count
        section_count += 1
        # Generous breathing between major sections
        if section_count > 1:
            pdf.ln(8)
            # Subtle separator
            sep_y = pdf.get_y()
            pdf.set_draw_color(*_LIGHT_LINE)
            pdf.set_line_width(0.15)
            pdf.line(LM + 5, sep_y, LM + CW - 5, sep_y)
            pdf.ln(8)
        else:
            pdf.ln(5)

        # Accent bar — service-specific color
        sy = pdf.get_y()
        if is_strategiia:
            pdf.set_fill_color(*_GOLD)
            bar_w = 2.5
        else:
            pdf.set_fill_color(*_DE_ACCENT)
            bar_w = 2.5
        pdf.rect(LM, sy, bar_w, 7, "F")

        # Section title — larger, bolder
        pdf.set_x(LM + bar_w + 4)
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(*_BLACK)
        pdf.cell(CW - bar_w - 4, 7, _safe(text))
        pdf.ln(11)

    def sub_title(text):
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 8.5)
        if is_strategiia:
            pdf.set_text_color(*_STRAT_ACCENT)
        else:
            pdf.set_text_color(*_DE_ACCENT)
        pdf.set_x(LM + 3)
        pdf.cell(CW - 3, 5, _safe(text))
        pdf.ln(7)

    def body_text(text):
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*_BODY_TEXT)
        pdf.set_x(LM)
        pdf.multi_cell(CW, 4.8, _safe(text), markdown=True)
        pdf.ln(2.5)

    def bullet_text(text):
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*_BODY_TEXT)
        pdf.set_x(LM + 5)
        bx, by = pdf.get_x(), pdf.get_y() + 1.5
        if is_strategiia:
            pdf.set_fill_color(*_GOLD)
        else:
            pdf.set_fill_color(*_DE_ACCENT)
        pdf.rect(bx - 3.5, by, 1.3, 1.3, "F")
        pdf.multi_cell(CW - 7, 4.8, _safe(text), markdown=True)
        pdf.ln(1.5)

    def bold_text(text):
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_DARK_TEXT)
        pdf.set_x(LM)
        pdf.multi_cell(CW, 4.2, _safe(text))
        pdf.ln(1)

    def italic_text(text):
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(*_MUTED)
        pdf.set_x(LM)
        pdf.multi_cell(CW, 4, _safe(text))
        pdf.ln(1)

    def callout_box(text, style="info"):
        """Elegant callout box for key insights."""
        pdf.ln(2)
        by = pdf.get_y()
        # Calculate height needed
        pdf.set_font("Helvetica", "I", 7.5)
        # Estimate lines needed
        line_h = 3.8
        text_w = CW - 14
        safe_t = _safe(text)
        n_lines = max(1, len(safe_t) / (text_w / 2.5))
        box_h = max(10, n_lines * line_h + 6)

        # Background
        if is_strategiia:
            pdf.set_fill_color(*_STRAT_BG)
            pdf.set_fill_color(252, 250, 244)
            bar_color = _GOLD
        else:
            pdf.set_fill_color(*_DE_BG)
            bar_color = _DE_ACCENT

        # Draw background rect, then write text, then adjust
        pdf.set_fill_color(252, 250, 244) if is_strategiia else pdf.set_fill_color(*_DE_BG)
        # We'll draw the box after knowing the height
        start_y = pdf.get_y()
        pdf.set_x(LM + 8)
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(*_BODY_TEXT)
        bottom_before = pdf.get_y()
        pdf.multi_cell(CW - 14, 3.8, safe_t, markdown=True)
        end_y = pdf.get_y()
        actual_h = end_y - start_y + 4

        # Draw background behind text (on current page)
        pdf.set_fill_color(252, 250, 244) if is_strategiia else pdf.set_fill_color(245, 247, 252)
        # Can't draw behind already-written text in fpdf2, so skip background for now
        # Just draw the accent bar
        pdf.set_fill_color(*bar_color)
        pdf.rect(LM + 3, start_y - 1, 1.5, actual_h + 2, "F")
        pdf.ln(2)

    def gold_separator():
        sep_y = pdf.get_y()
        pdf.set_draw_color(*_GOLD)
        pdf.set_line_width(0.3)
        pdf.line(LM + 25, sep_y, LM + CW - 25, sep_y)
        pdf.ln(4)

    # Parse and render analysis
    lines = analysis.split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        if not stripped:
            pdf.ln(2.5)
            i += 1
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
        elif stripped.startswith("**") and stripped.endswith("**") and len(stripped) > 4:
            # Full-line bold — check if it's a key insight
            inner = stripped.strip("*").strip()
            if any(kw in inner.lower() for kw in ["important", "attention", "essentiel", "cle", "crucial", "priorite"]):
                callout_box(inner)
            else:
                bold_text(inner)
        elif stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            italic_text(stripped.strip("*"))
        elif re.match(r'^\d+\.\s', stripped):
            bullet_text(stripped)
        else:
            body_text(stripped)

        i += 1

    # ══════════════════════════════════════════════════════════════
    # Dossier Express: Detailed document table (if details available)
    # ══════════════════════════════════════════════════════════════
    if is_dossier_express and document_details and len(document_details) > 0:
        space_doc = pdf.h - 18 - pdf.get_y()
        if space_doc < 40:
            pdf.add_page()

        pdf.ln(6)
        sep_y = pdf.get_y()
        pdf.set_draw_color(*_LIGHT_LINE)
        pdf.set_line_width(0.15)
        pdf.line(LM + 10, sep_y, LM + CW - 10, sep_y)
        pdf.ln(5)

        # Title
        ty = pdf.get_y()
        pdf.set_fill_color(*_DE_ACCENT)
        pdf.rect(LM, ty, 2, 5, "F")
        pdf.set_x(LM + 5)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*_DARK_TEXT)
        pdf.cell(CW - 5, 5, _safe("Pieces analysees dans le cadre de cette etude"))
        pdf.ln(8)

        # Table header
        col_widths = [90, 30, 50]
        headers = ["Document", "Pages", "Extraction"]
        hy = pdf.get_y()
        pdf.set_fill_color(*_DE_BG)
        pdf.rect(LM, hy, CW, 6, "F")
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(*_DE_ACCENT)
        cx = LM + 3
        for j, (hdr, w) in enumerate(zip(headers, col_widths)):
            pdf.set_xy(cx, hy + 1)
            pdf.cell(w, 4, _safe(hdr))
            cx += w
        pdf.set_y(hy + 7)

        # Table rows
        for idx, doc in enumerate(document_details[:12]):
            ry = pdf.get_y()
            if ry > pdf.h - 25:
                pdf.add_page()
                ry = pdf.get_y()

            if idx % 2 == 0:
                pdf.set_fill_color(*_IVORY)
                pdf.rect(LM, ry, CW, 5.5, "F")

            pdf.set_font("Helvetica", "", 6.5)
            pdf.set_text_color(*_BODY_TEXT)
            cx = LM + 3
            doc_name = doc.get("filename", doc.get("name", f"Document {idx+1}"))
            if len(doc_name) > 45:
                doc_name = doc_name[:42] + "..."
            pdf.set_xy(cx, ry + 1)
            pdf.cell(col_widths[0], 3.5, _safe(doc_name))
            cx += col_widths[0]

            pdf.set_xy(cx, ry + 1)
            pages = doc.get("pages", "-")
            pdf.cell(col_widths[1], 3.5, _safe(str(pages)), align="C")
            cx += col_widths[1]

            pdf.set_xy(cx, ry + 1)
            status = doc.get("status", "")
            status_label = {"text_extracted": "Texte natif", "ocr_extracted": "OCR", "failed": "Non lisible"}.get(status, "Traite")
            pdf.cell(col_widths[2], 3.5, _safe(status_label))

            pdf.set_y(ry + 5.5)

        pdf.ln(2)
        pdf.set_x(LM + 3)
        pdf.set_font("Helvetica", "I", 6)
        pdf.set_text_color(*_MUTED)
        pdf.multi_cell(CW - 6, 3, _safe(
            "Certaines pieces peuvent necessiter une relecture humaine complementaire "
            "lorsqu'elles sont scannees, manuscrites ou de qualite inegale."
        ))
        pdf.ln(3)

    # ══════════════════════════════════════════════════════════════
    # Closing section — Premium Signature S.E.S (standardized)
    # ══════════════════════════════════════════════════════════════
    space = pdf.h - 18 - pdf.get_y()
    if space < 95:
        pdf.add_page()

    pdf.ln(8)

    # Section title
    ty = pdf.get_y()
    if is_strategiia:
        pdf.set_fill_color(*_GOLD)
    else:
        pdf.set_fill_color(*_DE_ACCENT)
    pdf.rect(LM, ty, 2.5, 7, "F")
    pdf.set_x(LM + 6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*_BLACK)
    if is_strategiia:
        pdf.cell(CW - 6, 7, _safe("Votre situation, notre regard"))
    else:
        pdf.cell(CW - 6, 7, _safe("Ce que cette etude vous apporte"))
    pdf.ln(12)

    # ── Part 1: Standardized emotional opening ──
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(*_BODY_TEXT)
    pdf.set_x(LM)
    pdf.multi_cell(CW, 5, _safe(
        "Votre situation merite plus qu'une simple lecture automatisee : "
        "elle merite une strategie claire, humaine et rigoureuse."
    ))
    pdf.ln(4)

    # ── Part 2: Structured value ──
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*_BODY_TEXT)
    pdf.set_x(LM)
    pdf.multi_cell(CW, 5, _safe(
        "Ce document vous apporte une premiere vision structuree de votre dossier, "
        "mais certaines situations necessitent un regard plus approfondi, une relecture experte "
        "et un accompagnement reellement adapte a vos enjeux."
    ))
    pdf.ln(4)

    # ── Part 3: Elegant commercial transition ──
    sep_y = pdf.get_y()
    pdf.set_draw_color(*_LIGHT_LINE)
    pdf.set_line_width(0.15)
    pdf.line(LM + 20, sep_y, LM + CW - 20, sep_y)
    pdf.ln(6)

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*_BODY_TEXT)
    pdf.set_x(LM)
    pdf.multi_cell(CW, 5, _safe(
        "Si vous souhaitez aller plus loin, Strategie & Expertise Sante peut vous accompagner "
        "a travers une prestation personnalisee avec un de nos experts, "
        "afin de transformer cette premiere analyse en veritable levier d'action."
    ))
    pdf.ln(4)

    # ── Part 4: CTA box ──
    box_y = pdf.get_y()
    pdf.set_fill_color(*_IVORY)
    box_h = 24
    pdf.rect(LM, box_y, CW, box_h, "F")
    if is_strategiia:
        pdf.set_fill_color(*_GOLD)
    else:
        pdf.set_fill_color(*_DE_ACCENT)
    pdf.rect(LM, box_y, 2, box_h, "F")

    pdf.set_xy(LM + 7, box_y + 3)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW - 12, 5, _safe("Vous souhaitez aller plus loin ?"))

    pdf.set_xy(LM + 7, box_y + 10)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*_BODY_TEXT)
    if is_strategiia:
        pdf.multi_cell(CW - 12, 4.2, _safe(
            "Nos experts vous proposent un accompagnement sur mesure : "
            "analyse approfondie, strategie de recours personnalisee, "
            "preparation d'expertise medicale et defense de vos interets."
        ))
    else:
        pdf.multi_cell(CW - 12, 4.2, _safe(
            "Nos experts peuvent prolonger cette etude : "
            "relecture approfondie, verification des delais et procedures, "
            "chiffrage precis des prejudices et construction d'un dossier incontestable."
        ))

    pdf.set_y(box_y + box_h + 6)

    # ── QR Code + Contact ──
    qr_url = "https://strategie-expertise-sante.fr/contact?via=qr&source=" + ("strategiia" if is_strategiia else "dossier_express")
    qr_tmp_path = None
    try:
        import qrcode
        from io import BytesIO
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#1a1a1a", back_color="#FAF8F3")
        qr_buf = BytesIO()
        qr_img.save(qr_buf, format="PNG")
        qr_buf.seek(0)
        fd, qr_tmp_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        with open(qr_tmp_path, "wb") as f:
            f.write(qr_buf.getvalue())
    except Exception:
        qr_tmp_path = None

    space_qr = pdf.h - 18 - pdf.get_y()
    if space_qr < 48:
        pdf.add_page()
        pdf.ln(4)

    sep_qr = pdf.get_y()
    pdf.set_draw_color(*_LIGHT_LINE)
    pdf.set_line_width(0.15)
    pdf.line(LM + 25, sep_qr, LM + CW - 25, sep_qr)
    pdf.ln(5)

    if qr_tmp_path and os.path.isfile(qr_tmp_path):
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*_MUTED)
        pdf.cell(CW, 3.5, _safe("Prochaine etape recommandee"), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        qr_size = 22
        qr_x = LM + (CW - qr_size) / 2
        pdf.image(qr_tmp_path, x=qr_x, y=pdf.get_y(), w=qr_size, h=qr_size)
        pdf.set_y(pdf.get_y() + qr_size + 2)

        pdf.set_font("Helvetica", "I", 6.5)
        pdf.set_text_color(*_MUTED)
        pdf.cell(CW, 3, _safe("Scannez pour acceder a l'accompagnement expert personnalise S.E.S"), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)

        try:
            os.unlink(qr_tmp_path)
        except Exception:
            pass
    else:
        pdf.ln(2)

    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(*_MUTED)
    pdf.cell(CW, 3, _safe("Premiere consultation offerte  |  strategie-expertise-sante.fr/contact"), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # ── Confidentiality notice ──
    conf_y = pdf.get_y()
    space_conf = pdf.h - 18 - conf_y
    if space_conf < 35:
        pdf.add_page()
        pdf.ln(4)

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*_MUTED)
    pdf.set_x(LM)
    pdf.cell(CW, 4, _safe("Confidentialite"), align="L")
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 6.5)
    pdf.set_text_color(*_MUTED)
    pdf.set_x(LM)
    pdf.multi_cell(CW, 3.5, _safe(
        "Ce rapport a ete elabore a partir des informations et pieces transmises "
        "dans le cadre exclusif de l'analyse de votre dossier. "
        "Les documents fournis sont traites avec une attention particuliere "
        "en raison de leur caractere potentiellement sensible."
    ))

    pdf.ln(6)

    # ── Brand signature — Standardized emotional close ──
    sep_y3 = pdf.get_y()
    pdf.set_draw_color(*_GOLD)
    pdf.set_line_width(0.3)
    pdf.line(70, sep_y3, 140, sep_y3)
    pdf.ln(5)

    pdf.set_font("Helvetica", "BI", 9)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW, 5, _safe("Vous n'etes plus seul face a votre combat."), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*_GOLD)
    pdf.cell(CW, 5, _safe("Dorenavant, S.E.S est votre bouclier."), align="C")

    # ── Watermark ──
    if with_watermark:
        for p_num in range(1, pdf.pages_count + 1):
            pdf.page = p_num
            pdf._watermark()
        pdf.page = pdf.pages_count

    return bytes(pdf.output())


def generate_dossier_pdf(name, email, type_dossier, regime, analysis, premium_pdf=False, document_details=None):
    return generate_secured_pdf(
        analysis=analysis,
        report_type="Dossier Express IA",
        name=name,
        email=email,
        type_dossier=type_dossier,
        regime=regime,
        with_watermark=not premium_pdf,
        document_details=document_details,
    )
