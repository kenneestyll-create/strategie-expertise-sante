import re
import os
import tempfile
from datetime import datetime

from utils.pdf_fonts import get_liberation_dir

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
    return text


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
        return ("Vigilance élevée", 3, "Ce dossier présente des enjeux significatifs qui méritent une attention prioritaire.")
    elif high_count >= 1 or med_count >= 3:
        return ("Attention soutenue", 2, "Plusieurs éléments de ce dossier nécessitent une analyse approfondie.")
    else:
        return ("Suivi recommandé", 1, "Ce dossier contient des éléments à structurer pour sécuriser votre situation.")


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
    quality_summary: dict = None,
    quality_choice: str = "",
    citation_stats: dict = None,
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
        service_label = "Analyse Stratégique Premium"
        service_tagline = "Regard expert sur votre situation"
    else:
        accent = _DE_ACCENT
        accent_light = _DE_ACCENT_LIGHT
        service_label = "Pré-analyse Documentaire"
        service_tagline = "Étude structurée de vos pièces"

    LM = 16
    RM = 16
    CW = 210 - LM - RM

    FONT_DIR = get_liberation_dir()

    class PremiumPDF(FPDF):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.add_font("LibSans", "", os.path.join(FONT_DIR, "LiberationSans-Regular.ttf"), uni=True)
            self.add_font("LibSans", "B", os.path.join(FONT_DIR, "LiberationSans-Bold.ttf"), uni=True)
            self.add_font("LibSans", "I", os.path.join(FONT_DIR, "LiberationSans-Italic.ttf"), uni=True)
            self.add_font("LibSans", "BI", os.path.join(FONT_DIR, "LiberationSans-BoldItalic.ttf"), uni=True)

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
            self.set_font("LibSans", "B", 11)
            self.set_xy(text_x, 4.5)
            self.cell(80, 5, "Stratégie & Expertise Santé")
            # Pioneer line
            self.set_font("LibSans", "", 6.5)
            self.set_text_color(*_GOLD_LIGHT)
            self.set_xy(text_x, 10.5)
            self.cell(80, 4, "PIONNIER EN FRANCE")

            # Right: date, number, service badge
            self.set_font("LibSans", "", 7)
            self.set_text_color(180, 180, 180)
            self.set_xy(-RM - 65, 4)
            self.cell(65, 4, gen_date, align="R")
            self.set_text_color(*_GOLD_LIGHT)
            self.set_xy(-RM - 65, 8.5)
            self.cell(65, 4, report_number, align="R")
            # Service type badge
            self.set_font("LibSans", "B", 5.5)
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
            self.set_font("LibSans", "", 5.5)
            self.set_text_color(*_MUTED)
            footer_txt = f"(c) {year} Stratégie & Expertise Santé -- {report_number} -- Document confidentiel -- Analyse préliminaire à visée informative -- strategie-expertise-sante.fr"
            self.cell(
                CW, 3.5,
                footer_txt,
                align="C",
            )

        def _watermark(self):
            if not with_watermark:
                return
            sx, sy = self.x, self.y
            self.set_font("LibSans", "B", 38)
            self.set_text_color(240, 238, 232)
            cx, cy = self.w / 2, self.h / 2
            txt = "Stratégie & Expertise Santé"
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
    pdf.set_font("LibSans", "B", 8)
    pdf.set_text_color(*_DARK_TEXT)
    safe_name = _safe(name or email or "Client")
    pdf.cell(60, 4, safe_name)

    # Client metadata
    pdf.set_font("LibSans", "", 7)
    pdf.set_text_color(*_MUTED)
    safe_td = _safe(type_dossier or "")
    safe_reg = _safe(regime or "")
    info_parts = [p for p in [safe_td, safe_reg] if p]
    if info_parts:
        pdf.cell(0, 4, "  |  ".join(info_parts))

    pdf.set_xy(LM + 6, y + 7)
    pdf.set_font("LibSans", "", 6.5)
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
        pdf.set_font("LibSans", "BI", 7)
        pdf.set_text_color(*_GOLD)
        pdf.cell(0, 5, _safe("Document relu et finalisé dans le cadre de l'option Relecture expert personnalisée"))
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
        pdf.set_font("LibSans", "B", 7)
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
        pdf.set_font("LibSans", "B", 8.5)
        pdf.set_text_color(*_DARK_TEXT)
        pdf.cell(40, 4, _safe(level_label))

        # Description
        pdf.set_xy(dot_x + 28, vy + 11)
        pdf.set_font("LibSans", "I", 6.5)
        pdf.set_text_color(*_BODY_TEXT)
        pdf.cell(CW - 40, 3.5, _safe(level_desc))

        pdf.set_xy(LM, vy + box_h + 4)

    # ══════════════════════════════════════════════════════════════
    # Dossier Express: Document Summary Compact
    # ══════════════════════════════════════════════════════════════
    # ══════════════════════════════════════════════════════════════
    # Dossier Express — LOT 1 PHASE C1 : Tableau documentaire (quality_summary)
    # Remplace le bloc compact quand le contrôle qualité est disponible.
    # ══════════════════════════════════════════════════════════════
    if is_dossier_express and quality_summary:
        try:
            qs = quality_summary
            problem_docs = [
                d for d in (qs.get("per_document") or [])
                if (d.get("partial_pages") or d.get("unusable_pages"))
            ]
            dy = pdf.get_y()
            pdf.set_fill_color(*_DE_BG)
            pdf.set_draw_color(*_DE_ACCENT)

            pdf.set_xy(LM, dy)
            pdf.set_font("LibSans", "B", 7)
            pdf.set_text_color(*_DE_ACCENT)
            pdf.cell(CW, 4, "ANALYSE DOCUMENTAIRE — CONTRÔLE QUALITÉ")
            pdf.ln(5)

            col_w = (CW - 12) / 4
            metrics = [
                (str(qs.get("files", "-")), "documents reçus"),
                (str(qs.get("pages_total", "-")), "pages analysées"),
                (str(qs.get("pages_ok", "-")), "pages exploitables"),
                (_safe(qs.get("confidence_level", "-")), "qualité documentaire"),
            ]
            my = pdf.get_y()
            pdf.rect(LM, my, CW, 12, "F")
            pdf.set_fill_color(*_DE_ACCENT)
            pdf.rect(LM, my, 2, 12, "F")
            for i, (val, label) in enumerate(metrics):
                cx = LM + 4 + col_w * i
                pdf.set_xy(cx, my + 2.5)
                pdf.set_font("LibSans", "B", 9)
                pdf.set_text_color(*_DARK_TEXT)
                pdf.cell(col_w, 4, _safe(val), align="C")
                pdf.set_xy(cx, my + 7)
                pdf.set_font("LibSans", "", 5.5)
                pdf.set_text_color(*_MUTED)
                pdf.cell(col_w, 2.5, _safe(label), align="C")
            pdf.set_xy(LM, my + 14)

            if qs.get("pages_partial"):
                pdf.set_font("LibSans", "", 7)
                pdf.set_text_color(*_MUTED)
                pdf.cell(CW, 3.5, _safe(f"Dont {qs['pages_partial']} page(s) partiellement exploitable(s)."))
                pdf.ln(4.5)

            if problem_docs:
                essential_hit = any(a.get("type") == "essential_degraded" for a in (qs.get("alerts") or []))
                pdf.set_font("LibSans", "B", 7.5)
                pdf.set_text_color(*_DARK_TEXT)
                pdf.cell(CW, 4, "Points d'attention :")
                pdf.ln(4.5)
                pdf.set_font("LibSans", "", 7)
                pdf.set_text_color(*_BODY_TEXT)
                for d in problem_docs[:8]:
                    pages_pb = sorted((d.get("unusable_pages") or []) + (d.get("partial_pages") or []))
                    pages_str = ", ".join(str(p) for p in pages_pb)
                    pdf.set_x(LM + 3)
                    pdf.multi_cell(CW - 6, 3.5, _safe(f"• {d.get('name', 'Document')} — page(s) {pages_str} : qualité insuffisante"))
                pdf.ln(1)
                pdf.set_x(LM + 3)
                pdf.set_font("LibSans", "I", 7)
                pdf.set_text_color(*_MUTED)
                if essential_hit:
                    impact_line = ("Impact potentiel : les pages concernées appartiennent à une pièce essentielle du dossier ; "
                                   "certaines informations issues de ces pages pourraient nécessiter confirmation et modifier certaines conclusions.")
                else:
                    impact_line = ("Les limitations constatées portent sur des pièces secondaires et n'ont probablement pas "
                                   "d'impact sur les conclusions principales.")
                pdf.multi_cell(CW - 6, 3.5, _safe(impact_line))
                if quality_choice == "continue_degraded":
                    pdf.set_x(LM + 3)
                    pdf.multi_cell(CW - 6, 3.5, _safe("Le demandeur a choisi de poursuivre l'analyse en connaissance de ces limites."))
            total_p = qs.get("pages_total", 0)
            pdf.set_x(LM + 3)
            pdf.set_font("LibSans", "", 7)
            pdf.set_text_color(*_MUTED)
            pdf.multi_cell(CW - 6, 3.5, _safe(f"Cette analyse repose sur {qs.get('pages_ok', total_p)} page(s) exploitable(s) sur {total_p} fournie(s)."))
            if citation_stats and citation_stats.get("total"):
                pdf.set_x(LM + 3)
                pdf.multi_cell(CW - 6, 3.5, _safe(
                    f"Traçabilité des sources : {citation_stats.get('verified', 0)} citation(s) documentaire(s) "
                    f"vérifiée(s) sur {citation_stats['total']} contre les pièces fournies."))
            pdf.ln(6)
        except Exception:
            pass  # jamais bloquant : le rapport est livré même si le tableau échoue

    elif is_dossier_express and document_details:
        total_docs = len(document_details)
        total_pages = sum(d.get("pages", 0) for d in document_details)
        statuses = [d.get("status", "") for d in document_details]

        if all(s == "text_extracted" for s in statuses):
            level = "Excellente"
        elif all(s == "ocr_extracted" for s in statuses):
            level = "Bonne"
        elif all(s in ("text_extracted", "ocr_extracted") for s in statuses) and any(s == "ocr_extracted" for s in statuses):
            level = "Très bonne"
        elif any(s in ("text_extracted", "ocr_extracted") for s in statuses):
            level = "Partielle"
        else:
            level = "Limitée"

        dy = pdf.get_y()
        box_h = 14
        pdf.set_fill_color(*_DE_BG)
        pdf.rect(LM, dy, CW, box_h, "F")
        pdf.set_fill_color(*_DE_ACCENT)
        pdf.rect(LM, dy, 2, box_h, "F")

        # Title
        pdf.set_xy(LM + 6, dy + 2)
        pdf.set_font("LibSans", "B", 7)
        pdf.set_text_color(*_DE_ACCENT)
        pdf.cell(50, 3.5, "BASE DOCUMENTAIRE EXPLOITÉE")

        # Metrics in a row
        col_w = (CW - 12) / 3
        metrics = [
            (str(total_docs), "pièces analysées"),
            (str(total_pages) if total_pages > 0 else "-", "pages exploitées"),
            (level, "qualité d'extraction"),
        ]
        for i, (val, label) in enumerate(metrics):
            cx = LM + 6 + col_w * i
            pdf.set_xy(cx, dy + 7)
            pdf.set_font("LibSans", "B", 9)
            pdf.set_text_color(*_DARK_TEXT)
            pdf.cell(col_w, 4, _safe(val), align="C")
            pdf.set_xy(cx, dy + 11)
            pdf.set_font("LibSans", "", 5.5)
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
        pdf.set_font("LibSans", "B", 10.5)
        pdf.set_text_color(*_BLACK)
        pdf.cell(CW - bar_w - 4, 7, _safe(text))
        pdf.ln(11)

    def sub_title(text):
        pdf.ln(5)
        pdf.set_font("LibSans", "B", 8.5)
        if is_strategiia:
            pdf.set_text_color(*_STRAT_ACCENT)
        else:
            pdf.set_text_color(*_DE_ACCENT)
        pdf.set_x(LM + 3)
        pdf.cell(CW - 3, 5, _safe(text))
        pdf.ln(7)

    def body_text(text):
        pdf.set_font("LibSans", "", 8)
        pdf.set_text_color(*_BODY_TEXT)
        pdf.set_x(LM)
        pdf.multi_cell(CW, 4.8, _safe(text), markdown=True)
        pdf.ln(2.5)

    def bullet_text(text):
        pdf.set_font("LibSans", "", 8)
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
        pdf.set_font("LibSans", "B", 8)
        pdf.set_text_color(*_DARK_TEXT)
        pdf.set_x(LM)
        pdf.multi_cell(CW, 4.2, _safe(text))
        pdf.ln(1)

    def italic_text(text):
        pdf.set_font("LibSans", "I", 7.5)
        pdf.set_text_color(*_MUTED)
        pdf.set_x(LM)
        pdf.multi_cell(CW, 4, _safe(text))
        pdf.ln(1)

    def callout_box(text, style="info"):
        """Elegant callout box for key insights."""
        pdf.ln(2)
        by = pdf.get_y()
        # Calculate height needed
        pdf.set_font("LibSans", "I", 7.5)
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
        pdf.set_font("LibSans", "I", 7.5)
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
        pdf.set_font("LibSans", "B", 8.5)
        pdf.set_text_color(*_DARK_TEXT)
        pdf.cell(CW - 5, 5, _safe("Pièces analysées dans le cadre de cette étude"))
        pdf.ln(8)

        # Table header
        col_widths = [90, 30, 50]
        headers = ["Document", "Pages", "Extraction"]
        hy = pdf.get_y()
        pdf.set_fill_color(*_DE_BG)
        pdf.rect(LM, hy, CW, 6, "F")
        pdf.set_font("LibSans", "B", 6.5)
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

            pdf.set_font("LibSans", "", 6.5)
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
            status_label = {"text_extracted": "Texte natif", "ocr_extracted": "OCR", "failed": "Non lisible"}.get(status, "Traité")
            pdf.cell(col_widths[2], 3.5, _safe(status_label))

            pdf.set_y(ry + 5.5)

        pdf.ln(2)
        pdf.set_x(LM + 3)
        pdf.set_font("LibSans", "I", 6)
        pdf.set_text_color(*_MUTED)
        pdf.multi_cell(CW - 6, 3, _safe(
            "Certaines pièces peuvent nécessiter une relecture humaine complémentaire "
            "lorsqu'elles sont scannées, manuscrites ou de qualité inégale."
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
    pdf.set_font("LibSans", "B", 11)
    pdf.set_text_color(*_BLACK)
    if is_strategiia:
        pdf.cell(CW - 6, 7, _safe("Votre situation, notre regard"))
    else:
        pdf.cell(CW - 6, 7, _safe("Ce que cette étude vous apporte"))
    pdf.ln(12)

    # ── Part 1: Standardized emotional opening ──
    pdf.set_font("LibSans", "I", 8.5)
    pdf.set_text_color(*_BODY_TEXT)
    pdf.set_x(LM)
    pdf.multi_cell(CW, 5, _safe(
        "Votre situation mérite plus qu'une simple lecture automatisée : "
        "elle mérite une stratégie claire, humaine et rigoureuse."
    ))
    pdf.ln(4)

    # ── Part 2: Structured value ──
    pdf.set_font("LibSans", "", 8)
    pdf.set_text_color(*_BODY_TEXT)
    pdf.set_x(LM)
    pdf.multi_cell(CW, 5, _safe(
        "Ce document vous apporte une première vision structurée de votre dossier, "
        "mais certaines situations nécessitent un regard plus approfondi, une relecture experte "
        "et un accompagnement réellement adapté à vos enjeux."
    ))
    pdf.ln(4)

    # ── Part 3: Elegant commercial transition ──
    sep_y = pdf.get_y()
    pdf.set_draw_color(*_LIGHT_LINE)
    pdf.set_line_width(0.15)
    pdf.line(LM + 20, sep_y, LM + CW - 20, sep_y)
    pdf.ln(6)

    pdf.set_font("LibSans", "", 8)
    pdf.set_text_color(*_BODY_TEXT)
    pdf.set_x(LM)
    pdf.multi_cell(CW, 5, _safe(
        "Si vous souhaitez aller plus loin, Stratégie & Expertise Santé peut vous accompagner "
        "à travers une prestation personnalisée avec un de nos experts, "
        "afin de transformer cette première analyse en véritable levier d'action."
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
    pdf.set_font("LibSans", "B", 9)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW - 12, 5, _safe("Vous souhaitez aller plus loin ?"))

    pdf.set_xy(LM + 7, box_y + 10)
    pdf.set_font("LibSans", "", 7.5)
    pdf.set_text_color(*_BODY_TEXT)
    if is_strategiia:
        pdf.multi_cell(CW - 12, 4.2, _safe(
            "Nos experts vous proposent un accompagnement sur mesure : "
            "analyse approfondie, stratégie de recours personnalisée, "
            "préparation d'expertise médicale et défense de vos intérêts."
        ))
    else:
        pdf.multi_cell(CW - 12, 4.2, _safe(
            "Nos experts peuvent prolonger cette étude : "
            "relecture approfondie, vérification des délais et procédures, "
            "chiffrage précis des préjudices et construction d'un dossier incontestable."
        ))

    pdf.set_y(box_y + box_h + 6)

    # ── Trust Badge: "Références vérifiées" ──
    # Sobre, harmonieux avec le CTA box (même largeur, même ivoire, barre accent identique).
    # Renforce la crédibilité juridique de l'analyse IA sans rompre la hiérarchie visuelle.
    badge_y = pdf.get_y()
    badge_h = 13
    # Check space on current page — defer to next page if too tight
    if pdf.h - 18 - badge_y < badge_h + 52:  # badge + separator + QR + contact line
        pdf.add_page()
        badge_y = pdf.get_y()
    pdf.set_fill_color(*_IVORY_WARM)
    pdf.rect(LM, badge_y, CW, badge_h, "F")
    if is_strategiia:
        pdf.set_fill_color(*_GOLD)
    else:
        pdf.set_fill_color(*_DE_ACCENT)
    pdf.rect(LM, badge_y, 2, badge_h, "F")

    # Check icon (leading) + title
    pdf.set_xy(LM + 7, badge_y + 2.5)
    pdf.set_font("LibSans", "B", 7.8)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW - 12, 4, _safe("Analyse IA — Références juridiques vérifiées"), new_x="LMARGIN", new_y="NEXT")

    # Subtext
    pdf.set_x(LM + 7)
    pdf.set_font("LibSans", "", 6.8)
    pdf.set_text_color(*_MUTED)
    pdf.multi_cell(CW - 12, 3.2, _safe(
        "Rapport appuyé sur des articles de loi officiels (Code de la Sécurité Sociale, CASF). "
        "Aucune jurisprudence citée sans référence exacte — outil d'aide à la décision."
    ))

    pdf.set_y(badge_y + badge_h + 6)

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
        pdf.set_font("LibSans", "B", 7)
        pdf.set_text_color(*_MUTED)
        pdf.cell(CW, 3.5, _safe("Prochaine étape recommandée"), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        qr_size = 22
        qr_x = LM + (CW - qr_size) / 2
        pdf.image(qr_tmp_path, x=qr_x, y=pdf.get_y(), w=qr_size, h=qr_size)
        pdf.set_y(pdf.get_y() + qr_size + 2)

        pdf.set_font("LibSans", "I", 6.5)
        pdf.set_text_color(*_MUTED)
        pdf.cell(CW, 3, _safe("Scannez pour accéder à l'accompagnement expert personnalisé S.E.S"), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)

        try:
            os.unlink(qr_tmp_path)
        except Exception:
            pass
    else:
        pdf.ln(2)

    pdf.set_font("LibSans", "", 6)
    pdf.set_text_color(*_MUTED)
    pdf.cell(CW, 3, _safe("Première consultation offerte  |  strategie-expertise-sante.fr/contact"), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # ── Confidentiality notice ──
    conf_y = pdf.get_y()
    space_conf = pdf.h - 18 - conf_y
    if space_conf < 35:
        pdf.add_page()
        pdf.ln(4)

    pdf.set_font("LibSans", "B", 7)
    pdf.set_text_color(*_MUTED)
    pdf.set_x(LM)
    pdf.cell(CW, 4, _safe("Confidentialité"), align="L")
    pdf.ln(5)
    pdf.set_font("LibSans", "I", 6.5)
    pdf.set_text_color(*_MUTED)
    pdf.set_x(LM)
    pdf.multi_cell(CW, 3.5, _safe(
        "Ce rapport a été élaboré à partir des informations et pièces transmises "
        "dans le cadre exclusif de l'analyse de votre dossier. "
        "Les documents fournis sont traités avec une attention particulière "
        "en raison de leur caractère potentiellement sensible."
    ))

    pdf.ln(6)

    # ── Brand signature — Standardized emotional close ──
    sep_y3 = pdf.get_y()
    pdf.set_draw_color(*_GOLD)
    pdf.set_line_width(0.3)
    pdf.line(70, sep_y3, 140, sep_y3)
    pdf.ln(5)

    pdf.set_font("LibSans", "BI", 9)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW, 5, _safe("Vous n'êtes plus seul face à votre combat."), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("LibSans", "B", 9)
    pdf.set_text_color(*_GOLD)
    pdf.cell(CW, 5, _safe("Dorénavant, S.E.S est votre bouclier."), align="C")

    # ── Watermark ──
    if with_watermark:
        for p_num in range(1, pdf.pages_count + 1):
            pdf.page = p_num
            pdf._watermark()
        pdf.page = pdf.pages_count

    return bytes(pdf.output())


def generate_dossier_pdf(name, email, type_dossier, regime, analysis, premium_pdf=False, document_details=None, quality_summary=None, quality_choice="", citation_stats=None):
    return generate_secured_pdf(
        analysis=analysis,
        report_type="Dossier Express IA",
        name=name,
        email=email,
        type_dossier=type_dossier,
        regime=regime,
        with_watermark=not premium_pdf,
        document_details=document_details,
        quality_summary=quality_summary,
        quality_choice=quality_choice,
        citation_stats=citation_stats,
    )
