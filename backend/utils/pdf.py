from datetime import datetime


def generate_report_number():
    import random
    year = datetime.now().year
    seq = random.randint(10000, 99999)
    return f"SES-{year}-{seq}"


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

    class SecuredPDF(FPDF):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._is_cover = True

        def header(self):
            if self._is_cover:
                return
            self.set_fill_color(26, 26, 46)
            self.rect(0, 0, 210, 18, "F")
            self.set_text_color(255, 255, 255)
            self.set_font("Helvetica", "B", 9)
            self.set_y(4)
            self.set_x(12)
            self.cell(0, 5, "Strategie & Expertise Sante", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 7)
            self.set_x(12)
            self.set_text_color(200, 200, 210)
            self.cell(100, 4, "strategie-expertise-sante.fr")
            self.set_x(-60)
            self.set_font("Helvetica", "", 7)
            self.cell(0, 4, report_number, align="R")
            self.set_xy(self.l_margin, 22)

        def footer(self):
            self.set_y(-14)
            self.set_draw_color(200, 200, 200)
            self.line(12, self.get_y(), 198, self.get_y())
            self.ln(2)
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(140, 140, 140)
            year = datetime.now().year
            self.cell(0, 5, f"(c) {year} Strategie & Expertise Sante -- strategie-expertise-sante.fr", align="C")

        def _draw_watermark(self):
            if not with_watermark:
                return
            saved_x, saved_y = self.x, self.y
            self.set_font("Helvetica", "B", 42)
            self.set_text_color(230, 228, 222)
            cx, cy = self.w / 2, self.h / 2
            text = "Strategie & Expertise Sante"
            tw = self.get_string_width(text)
            with self.rotation(40, cx, cy):
                self.text(cx - tw / 2, cy, text)
            self.set_xy(saved_x, saved_y)

    pdf = SecuredPDF()
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.set_left_margin(12)
    pdf.set_right_margin(12)

    # Cover page
    pdf._is_cover = True
    pdf.add_page()

    pdf.set_fill_color(26, 26, 46)
    pdf.rect(0, 0, 210, 297, "F")

    pdf.set_fill_color(185, 78, 72)
    pdf.rect(0, 85, 210, 4, "F")

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_y(100)
    pdf.cell(0, 14, "Strategie & Expertise Sante", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(200, 200, 210)
    pdf.cell(0, 8, "strategie-expertise-sante.fr", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(15)
    pdf.set_draw_color(185, 78, 72)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    pdf.ln(15)

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    safe_type = report_type.encode("latin-1", "replace").decode("latin-1")
    pdf.cell(0, 10, f"Rapport {safe_type}", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(20)
    box_x, box_y, box_w = 40, pdf.get_y(), 130
    pdf.set_fill_color(40, 40, 60)
    pdf.rect(box_x, box_y, box_w, 48, "F")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(200, 200, 210)
    y_info = box_y + 8
    for label, val in [
        ("Numero du rapport", report_number),
        ("Date de generation", gen_date),
        ("Client / Dossier", (name or email or "N/A").encode("latin-1", "replace").decode("latin-1")),
        ("Type de dossier", (type_dossier or "Non precise").encode("latin-1", "replace").decode("latin-1")),
    ]:
        pdf.set_xy(box_x + 6, y_info)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(50, 5, label + " :")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 5, val)
        pdf.set_text_color(200, 200, 210)
        y_info += 10

    pdf.set_y(265)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(140, 140, 150)
    pdf.cell(0, 5, "Document confidentiel", align="C", new_x="LMARGIN", new_y="NEXT")
    year = datetime.now().year
    pdf.cell(0, 5, f"(c) {year} Strategie & Expertise Sante -- StrategiIA", align="C")

    # Content pages
    pdf._is_cover = False
    pdf.add_page()

    pdf.set_fill_color(245, 243, 238)
    pdf.rect(12, 24, 186, 22, "F")
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_xy(16, 26)
    safe_name = (name or "Non renseigne").encode("latin-1", "replace").decode("latin-1")
    pdf.cell(0, 5, f"Client : {safe_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(16)
    safe_td = (type_dossier or "Non precise").encode("latin-1", "replace").decode("latin-1")
    safe_reg = (regime or "Non precise").encode("latin-1", "replace").decode("latin-1")
    pdf.cell(0, 5, f"Type : {safe_td}  |  Regime : {safe_reg}  |  {gen_date}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    lines = analysis.split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            pdf.ln(3)
            continue
        safe = stripped.encode("latin-1", "replace").decode("latin-1")
        pdf.set_x(pdf.l_margin)
        if stripped.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(26, 26, 46)
            pdf.ln(5)
            pdf.multi_cell(0, 8, safe[2:])
        elif stripped.startswith("## "):
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(26, 26, 46)
            pdf.ln(4)
            pdf.multi_cell(0, 7, safe[3:])
        elif stripped.startswith("### "):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(15, 52, 96)
            pdf.ln(3)
            pdf.multi_cell(0, 7, safe[4:])
        elif stripped.startswith("- ") or stripped.startswith("* "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            pdf.set_x(20)
            pdf.multi_cell(166, 6, f"  {safe[2:]}")
        elif stripped.startswith("**") and stripped.endswith("**"):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 6, safe.strip("*"))
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 6, safe)

    # Legal page
    pdf.add_page()
    pdf.ln(5)
    pdf.set_fill_color(185, 78, 72)
    pdf.rect(12, pdf.get_y(), 3, 8, "F")
    pdf.set_x(18)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 8, "Mentions legales", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(60, 60, 60)

    legal_text = (
        "Ce rapport est fourni a titre d'analyse et d'accompagnement administratif. "
        "Il ne constitue ni un avis medical ni un conseil juridique.\n\n"
        "Ce document est la propriete exclusive de Strategie & Expertise Sante. "
        "Toute reproduction, diffusion ou utilisation commerciale sans autorisation "
        "ecrite prealable est interdite et constitue une contrefacon.\n\n"
        f"(c) {datetime.now().year} Strategie & Expertise Sante -- StrategiIA(TM) outil exclusif.\n\n"
        f"Rapport : {report_number}\n"
        f"Date de generation : {gen_date}"
    )
    pdf.multi_cell(0, 5.5, legal_text)

    if with_watermark:
        total_pages = pdf.pages_count
        for p_num in range(1, total_pages + 1):
            pdf.page = p_num
            pdf._draw_watermark()
        pdf.page = total_pages

    return bytes(pdf.output())


def generate_dossier_pdf(name: str, email: str, type_dossier: str, regime: str, analysis: str, premium_pdf: bool = False) -> bytes:
    return generate_secured_pdf(
        analysis=analysis,
        report_type="Dossier Express IA",
        name=name,
        email=email,
        type_dossier=type_dossier,
        regime=regime,
        with_watermark=not premium_pdf,
    )
