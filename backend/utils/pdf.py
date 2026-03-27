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
    re.compile(r'(?i)mascot-tips-admin\.preview.*$'),
    re.compile(r'^---+$'),
    # Strip LLM-generated closing phrase (it's hardcoded in the PDF template)
    re.compile(r'(?i)^\W*vous\s+n.{0,3}tes\s+plus\s+seul'),
    re.compile(r'(?i)^\W*d.sormais.*devient\s+votre\s+bouclier'),
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
    relecture_expert: bool = False,
    document_details: list = None,
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

    # ── Relecture expert badge ──
    if relecture_expert:
        ry = pdf.get_y()
        pdf.set_fill_color(26, 26, 46)  # dark navy
        pdf.rect(LM, ry, CW, 8, "F")
        pdf.set_xy(LM + 4, ry + 1.5)
        pdf.set_font("Helvetica", "BI", 7)
        pdf.set_text_color(*_GOLD)
        pdf.cell(0, 5, _safe("Document relu et finalise dans le cadre de l'option Relecture expert personnalisee"))
        pdf.set_xy(LM, ry + 8)

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

    # ── Base documentaire prise en compte ──
    if document_details:
        total_docs = len(document_details)
        total_pages = sum(d.get("pages", 0) for d in document_details)
        statuses = [d.get("status", "") for d in document_details]

        # Readability level
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

        # Ensure enough space
        space_doc = pdf.h - 16 - pdf.get_y()
        if space_doc < 42:
            pdf.add_page()

        pdf.ln(5)
        # Subtle separator
        sep_y = pdf.get_y()
        pdf.set_draw_color(*_LIGHT_LINE)
        pdf.set_line_width(0.2)
        pdf.line(LM + 10, sep_y, LM + CW - 10, sep_y)
        pdf.ln(4)

        # Title with gold accent
        ty = pdf.get_y()
        pdf.set_fill_color(*_GOLD)
        pdf.rect(LM, ty, 1.5, 4.5, "F")
        pdf.set_x(LM + 4)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_DARK_TEXT)
        pdf.cell(CW - 4, 4.5, _safe("Base documentaire prise en compte"))
        pdf.ln(7)

        # Intro line
        pdf.set_x(LM + 4)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*_BODY_TEXT)
        pdf.multi_cell(CW - 8, 3.5, _safe(
            "Ce rapport a ete etabli a partir des pieces transmises au moment de votre demande."
        ))
        pdf.ln(2)

        # Metrics row inside a light box
        by = pdf.get_y()
        box_h = 11
        pdf.set_fill_color(*_IVORY)
        pdf.rect(LM + 4, by, CW - 8, box_h, "F")

        col_w = (CW - 8) / 3
        for i, (label, value) in enumerate([
            ("Documents analyses", str(total_docs)),
            ("Pages exploitees", str(total_pages)),
            ("Lisibilite documentaire", level),
        ]):
            cx = LM + 4 + col_w * i
            pdf.set_xy(cx, by + 1.5)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*_DARK_TEXT)
            pdf.cell(col_w, 4, _safe(value), align="C")
            pdf.set_xy(cx, by + 5.5)
            pdf.set_font("Helvetica", "", 6)
            pdf.set_text_color(*_MUTED)
            pdf.cell(col_w, 3.5, _safe(label), align="C")

        pdf.set_y(by + box_h + 3)

        # Reassurance note
        pdf.set_x(LM + 4)
        pdf.set_font("Helvetica", "I", 6.5)
        pdf.set_text_color(*_MUTED)
        pdf.multi_cell(CW - 8, 3.2, _safe(
            "Certaines pieces peuvent necessiter une relecture humaine complementaire "
            "lorsqu'elles sont scannees, manuscrites ou de qualite inegale."
        ))
        pdf.ln(2)

    # ── Et maintenant ? — Bloc de conversion stratégique en 3 parties ──
    space = pdf.h - 16 - pdf.get_y()
    if space < 80:
        pdf.add_page()

    pdf.ln(6)

    # ── Titre de section "Et maintenant ?" ──
    ty = pdf.get_y()
    pdf.set_fill_color(*_GOLD)
    pdf.rect(LM, ty, 2.5, 7, "F")
    pdf.set_x(LM + 6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW - 6, 7, _safe("Et maintenant ?"))
    pdf.ln(10)

    # ── Partie 1 : Cloture emotionnelle ──
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(*_BODY_TEXT)
    pdf.set_x(LM)
    pdf.multi_cell(CW, 4.2, _safe(
        "Si vous lisez ces lignes, c'est que vous traversez une epreuve "
        "que personne ne devrait affronter seul(e). Ce rapport a ete concu "
        "pour poser un premier eclairage clair et structure sur votre situation. "
        "C'est deja un pas important."
    ))
    pdf.ln(3)

    # ── Partie 2 : Transition strategique ──
    # Subtle separator
    sep_y = pdf.get_y()
    pdf.set_draw_color(*_LIGHT_LINE)
    pdf.set_line_width(0.2)
    pdf.line(LM + 15, sep_y, LM + CW - 15, sep_y)
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*_BODY_TEXT)
    pdf.set_x(LM)
    pdf.multi_cell(CW, 4.2, _safe(
        "Mais un rapport, aussi precis soit-il, reste un point de depart. "
        "Chaque dossier comporte des subtilites que seule une analyse humaine "
        "approfondie peut reveler : des leviers juridiques inexploites, "
        "des erreurs de consolidation, des prejudices sous-evalues."
    ))
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*_BLACK)
    pdf.set_x(LM)
    pdf.multi_cell(CW, 4.2, _safe(
        "Ce que ce rapport vous montre, c'est le potentiel de votre dossier. "
        "Ce qu'un accompagnement personnalise vous apporte, c'est la capacite "
        "de le transformer en resultat concret."
    ))
    pdf.ln(3)

    # ── Partie 3 : Orientation vers l'offre finale ──
    # Elegant box
    sep_y2 = pdf.get_y()
    pdf.set_draw_color(*_LIGHT_LINE)
    pdf.set_line_width(0.2)
    pdf.line(LM + 15, sep_y2, LM + CW - 15, sep_y2)
    pdf.ln(4)

    box_y = pdf.get_y()
    pdf.set_fill_color(*_IVORY)
    box_h = 26
    pdf.rect(LM, box_y, CW, box_h, "F")
    # Gold left accent on the box
    pdf.set_fill_color(*_GOLD)
    pdf.rect(LM, box_y, 2, box_h, "F")

    pdf.set_xy(LM + 6, box_y + 3)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*_BLACK)
    pdf.cell(CW - 10, 4.5, _safe("Vous souhaitez aller plus loin ?"))

    pdf.set_xy(LM + 6, box_y + 9)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*_BODY_TEXT)
    pdf.multi_cell(CW - 10, 3.8, _safe(
        "Nos experts vous proposent un accompagnement sur mesure : "
        "relecture approfondie de votre dossier, strategie de recours, "
        "preparation d'expertise medicale, et defense de vos interets "
        "a chaque etape."
    ))

    pdf.set_y(box_y + box_h + 4)

    # ── QR Code + Lien discret — Conversion depuis le PDF ──
    qr_url = "https://strategie-expertise-sante.fr/contact?via=qr&source=dossier_express"
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

    # Check space for QR block (~45mm)
    space_qr = pdf.h - 16 - pdf.get_y()
    if space_qr < 48:
        pdf.add_page()
        pdf.ln(4)

    # Subtle separator
    sep_qr = pdf.get_y()
    pdf.set_draw_color(*_LIGHT_LINE)
    pdf.set_line_width(0.2)
    pdf.line(LM + 20, sep_qr, LM + CW - 20, sep_qr)
    pdf.ln(5)

    if qr_tmp_path and os.path.isfile(qr_tmp_path):
        # QR label
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*_MUTED)
        pdf.cell(CW, 3.5, _safe("Prochaine etape recommandee"), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # QR code — centered, 22mm
        qr_size = 22
        qr_x = LM + (CW - qr_size) / 2
        pdf.image(qr_tmp_path, x=qr_x, y=pdf.get_y(), w=qr_size, h=qr_size)
        pdf.set_y(pdf.get_y() + qr_size + 2)

        # QR description
        pdf.set_font("Helvetica", "I", 6.5)
        pdf.set_text_color(*_MUTED)
        pdf.cell(CW, 3, _safe("Scannez pour acceder a l'accompagnement expert personnalise S.E.S"), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)

        # Cleanup temp file
        try:
            os.unlink(qr_tmp_path)
        except Exception:
            pass
    else:
        pdf.ln(2)

    # Text link fallback (always present)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(*_MUTED)
    pdf.cell(CW, 3, _safe("Premiere consultation offerte  |  strategie-expertise-sante.fr/contact"), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)

    # ── Signature de marque finale ──
    sep_y3 = pdf.get_y()
    pdf.set_draw_color(*_GOLD)
    pdf.set_line_width(0.3)
    pdf.line(65, sep_y3, 145, sep_y3)
    pdf.ln(4)

    pdf.set_font("Helvetica", "BI", 8.5)
    pdf.set_text_color(*_GOLD)
    pdf.cell(CW, 4.5, _safe("Strategie & Expertise Sante — Votre bouclier."), align="C")

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
