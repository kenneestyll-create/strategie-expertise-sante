"""CORPUS DE RÉFÉRENCE PERMANENT — Dossier Express IA (base de non-régression).
Génère les PDF du corpus dans /app/backend/tests/corpus/ (une seule fois, fichiers conservés).
R* = dossiers de référence · D* = dossiers volontairement dégradés."""
import io, os, random
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

CORPUS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus")

EXPERTISE = ("RAPPORT D'EXPERTISE MEDICALE\n\nMission confiee par la compagnie d'assurance. "
             "Examen clinique du 12 mars 2026. L'etat de l'assure est declare consolide au 12 mars 2026. "
             "Le taux d'incapacite permanente partielle (IPP) est evalue a 8 pour cent selon le bareme AIPP. "
             "Les douleurs residuelles de l'epaule droite limitent l'elevation anterieure a 90 degres. ") * 2
CERTIFICAT = ("CERTIFICAT MEDICAL\n\nJe soussigne, Docteur Martin, certifie suivre le patient pour une "
              "limitation fonctionnelle de l'epaule droite consecutive a l'accident du 3 janvier 2026. "
              "Les soins restent en cours, la reeducation se poursuit a raison de deux seances par semaine. ") * 2
NOTIFICATION = ("NOTIFICATION DE DECISION - CAISSE PRIMAIRE D'ASSURANCE MALADIE\n\nLa CPAM vous notifie la "
                "decision suivante : date de consolidation fixee au 12 mars 2026, taux d'incapacite permanente "
                "de 8 pour cent, rente annuelle calculee sur le salaire de reference. Voies de recours : deux mois. ") * 2
COURRIER = ("Courrier d'accompagnement.\n\nMadame, Monsieur, veuillez trouver ci-joint les pieces demandees "
            "dans le cadre du dossier. Je reste a votre disposition pour tout complement. ") * 2


def _text_pdf(pages):
    pdf = FPDF()
    for content in pages:
        pdf.add_page()
        pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 6, content)
    return bytes(pdf.output())


def _text_image(content, w=1000, h=1400):
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    y = 60
    words = content.split()
    line = ""
    for word in words:
        if len(line) + len(word) > 70:
            d.text((60, y), line, fill=(10, 10, 10), font=font)
            y += 34
            line = word
            if y > h - 80:
                break
        else:
            line = f"{line} {word}".strip()
    if y <= h - 80:
        d.text((60, y), line, fill=(10, 10, 10), font=font)
    return img


def _img_pdf(images):
    pdf = FPDF()
    for i, img in enumerate(images):
        tmp = f"/tmp/_corpus_{i}.jpg"
        img.convert("RGB").save(tmp, "JPEG", quality=60)
        pdf.add_page()
        pdf.image(tmp, x=5, y=5, w=200)
        os.unlink(tmp)
    return bytes(pdf.output())


def build_corpus():
    os.makedirs(CORPUS_DIR, exist_ok=True)
    rnd = random.Random(7)
    files = {}

    # ---- RÉFÉRENCE ----
    files["R1_complet_lisible.pdf"] = _text_pdf([EXPERTISE, EXPERTISE, CERTIFICAT, NOTIFICATION])
    files["R2_volumineux.pdf"] = _text_pdf([f"Piece {i+1}. {EXPERTISE if i % 3 == 0 else COURRIER}" for i in range(30)])
    files["R3a_expertise.pdf"] = _text_pdf([EXPERTISE, EXPERTISE])
    files["R3b_certificat.pdf"] = _text_pdf([CERTIFICAT])
    files["R3c_notification.pdf"] = _text_pdf([NOTIFICATION])
    files["R3d_courrier.pdf"] = _text_pdf([COURRIER])
    files["R4_pieces_manquantes.pdf"] = _text_pdf([CERTIFICAT])  # certificat seul, pas d'expertise ni notification
    files["R5_qualite_variable.pdf"] = _text_pdf([EXPERTISE, "petit fragment", CERTIFICAT, "x", NOTIFICATION])

    # ---- DÉGRADÉS (images → chemin Gemini Vision) ----
    base = _text_image(EXPERTISE)
    files["D1_flou_fort.pdf"] = _img_pdf([base.filter(ImageFilter.GaussianBlur(7))])
    cropped = base.crop((0, 0, 1000, 500)).resize((1000, 1400))  # moitié basse perdue puis étirée
    files["D2_page_coupee.pdf"] = _img_pdf([cropped])
    files["D3_contraste_faible.pdf"] = _img_pdf([ImageEnhance.Contrast(base).enhance(0.08)])
    files["D4_rotation_90.pdf"] = _img_pdf([base.rotate(90, expand=True, fillcolor="white")])
    files["D5_page_blanche.pdf"] = _text_pdf([EXPERTISE, " ", CERTIFICAT])
    files["D6_incomplet.pdf"] = _text_pdf(["Page 3 sur 12 du rapport d'expertise. " + EXPERTISE[:200]])
    files["D7_ordre_incorrect.pdf"] = _text_pdf([NOTIFICATION, EXPERTISE, CERTIFICAT])  # ordre illogique
    noisy = base.copy()
    px = noisy.load()
    for _ in range(int(1000 * 1400 * 0.22)):
        x, y = rnd.randrange(1000), rnd.randrange(1400)
        g = rnd.randrange(0, 120)
        px[x, y] = (g, g, g)
    files["D8_ocr_partiel.pdf"] = _img_pdf([base, noisy.filter(ImageFilter.GaussianBlur(4))])

    for name, data in files.items():
        path = os.path.join(CORPUS_DIR, name)
        if not os.path.exists(path):
            open(path, "wb").write(data)
    return sorted(files)


if __name__ == "__main__":
    for f in build_corpus():
        print(f)
