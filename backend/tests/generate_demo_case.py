"""Génère le cas fictif de démonstration (Mme DEMONSTRATION Claire) — programme Évaluateur Expert.
V2 esthétique : mises en page réalistes (en-têtes, références, encadrés), contenu inchangé."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = "/app/frontend/public/cas-demonstration"
os.makedirs(OUT, exist_ok=True)
W, H = A4
ML, MR = 22 * mm, 22 * mm
BODY_W = W - ML - MR


def watermark(c):
    c.saveState()
    c.setFont("Helvetica-Bold", 32)
    c.setFillColorRGB(0.85, 0.1, 0.1, alpha=0.13)
    c.translate(W / 2, H / 2)
    c.rotate(40)
    for dy in (-120, 0, 120):
        c.drawCentredString(0, dy, "CAS FICTIF DE DÉMONSTRATION")
    c.restoreState()
    c.setFillColorRGB(0.98, 0.93, 0.93)
    c.rect(0, H - 9 * mm, W, 9 * mm, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(0.66, 0.08, 0.08)
    c.drawCentredString(W / 2, H - 6.2 * mm, "CAS FICTIF DE DÉMONSTRATION — Aucune personne réelle. Document créé pour l'évaluation de Dossier Express IA.")


class Doc:
    def __init__(self, filename, accent=(0.11, 0.30, 0.54)):
        self.c = canvas.Canvas(f"{OUT}/{filename}", pagesize=A4)
        self.filename = filename
        self.accent = accent
        watermark(self.c)
        self.y = H - 18 * mm

    def _check_page(self, needed=12 * mm):
        if self.y < 25 * mm + needed:
            self.c.showPage()
            watermark(self.c)
            self.y = H - 18 * mm

    def letterhead(self, org, sub_lines, right_lines=None):
        c = self.c
        c.setFillColorRGB(*self.accent)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(ML, self.y, org)
        c.setFont("Helvetica", 8.5)
        c.setFillColorRGB(0.25, 0.25, 0.25)
        yy = self.y - 5 * mm
        for s in sub_lines:
            c.drawString(ML, yy, s)
            yy -= 4 * mm
        if right_lines:
            ry = self.y
            c.setFont("Helvetica", 9)
            for s in right_lines:
                c.drawRightString(W - MR, ry, s)
                ry -= 4.5 * mm
        self.y = min(yy, (ry if right_lines else yy)) - 3 * mm
        c.setStrokeColorRGB(*self.accent)
        c.setLineWidth(1.2)
        c.line(ML, self.y, W - MR, self.y)
        self.y -= 10 * mm

    def title(self, text, sub=None):
        c = self.c
        c.setFillColorRGB(0.08, 0.08, 0.08)
        c.setFont("Helvetica-Bold", 12.5)
        for line in simpleSplit(text, "Helvetica-Bold", 12.5, BODY_W):
            c.drawCentredString(W / 2, self.y, line)
            self.y -= 6 * mm
        if sub:
            c.setFont("Helvetica-Oblique", 9)
            c.setFillColorRGB(0.35, 0.35, 0.35)
            c.drawCentredString(W / 2, self.y, sub)
            self.y -= 6 * mm
        self.y -= 4 * mm

    def para(self, text, bold=False, size=10, indent=0, color=(0.13, 0.13, 0.13), leading=None):
        font = "Helvetica-Bold" if bold else "Helvetica"
        leading = leading or size * 0.52 * mm
        self.c.setFont(font, size)
        self.c.setFillColorRGB(*color)
        for line in simpleSplit(text, font, size, BODY_W - indent):
            self._check_page()
            self.c.setFont(font, size)
            self.c.setFillColorRGB(*color)
            self.c.drawString(ML + indent, self.y, line)
            self.y -= leading
        self.y -= 2.2 * mm

    def section(self, label):
        self._check_page(16 * mm)
        self.c.setFillColorRGB(*self.accent)
        self.c.setFont("Helvetica-Bold", 10.5)
        self.c.drawString(ML, self.y, label)
        self.c.setStrokeColorRGB(*self.accent)
        self.c.setLineWidth(0.5)
        tw = self.c.stringWidth(label, "Helvetica-Bold", 10.5)
        self.c.line(ML + tw + 3 * mm, self.y + 1.2 * mm, W - MR, self.y + 1.2 * mm)
        self.y -= 7 * mm

    def box(self, title_text, lines, fill=(0.93, 0.95, 0.98)):
        pad = 4 * mm
        font_h = 4.6 * mm
        wrapped = []
        for ln in lines:
            wrapped += simpleSplit(ln, "Helvetica", 9.5, BODY_W - 2 * pad)
        box_h = pad * 2 + 5.5 * mm + len(wrapped) * font_h
        self._check_page(box_h)
        top = self.y + 3 * mm
        self.c.setFillColorRGB(*fill)
        self.c.setStrokeColorRGB(*self.accent)
        self.c.setLineWidth(0.8)
        self.c.roundRect(ML, top - box_h, BODY_W, box_h, 2 * mm, stroke=1, fill=1)
        yy = top - pad - 3 * mm
        self.c.setFillColorRGB(*self.accent)
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawString(ML + pad, yy, title_text)
        yy -= 6 * mm
        self.c.setFillColorRGB(0.13, 0.13, 0.13)
        self.c.setFont("Helvetica", 9.5)
        for ln in wrapped:
            self.c.drawString(ML + pad, yy, ln)
            yy -= font_h
        self.y = top - box_h - 8 * mm

    def signature(self, place_date, name_lines):
        self._check_page(28 * mm)
        x = W - MR - 70 * mm
        self.c.setFont("Helvetica", 9.5)
        self.c.setFillColorRGB(0.13, 0.13, 0.13)
        self.c.drawString(x, self.y, place_date)
        self.y -= 6 * mm
        for i, nl in enumerate(name_lines):
            self.c.setFont("Helvetica-Bold" if i == 0 else "Helvetica-Oblique", 9.5 if i == 0 else 8.5)
            self.c.drawString(x, self.y, nl)
            self.y -= 4.8 * mm

    def save(self):
        self.c.save()
        print("OK", self.filename)


MED = (0.18, 0.34, 0.30)
ADM = (0.11, 0.30, 0.54)
ATT = (0.36, 0.28, 0.16)

# ============ 1. Certificat médical initial ============
d = Doc("1-certificat-medical-initial.pdf", accent=MED)
d.letterhead("Dr Paul EXEMPLE", ["Médecin généraliste — RPPS fictif 99999999901",
                                 "Cabinet médical fictif — 12 rue de la Démonstration, 99000 Villefictive",
                                 "Tél. fictif : 09 99 99 99 99 — Conventionné secteur 1"],
             right_lines=["Villefictive, le 18/02/2026"])
d.title("CERTIFICAT MÉDICAL INITIAL", sub="Maladie professionnelle — formulaire type Cerfa (document fictif)")
d.para("Je soussigné, Dr Paul EXEMPLE, médecin généraliste (RPPS fictif 99999999901), certifie avoir examiné ce jour :")
d.para("Mme DEMONSTRATION Claire, née le 12/03/1981 (identité fictive)", bold=True, size=11)
d.para("Profession déclarée : cadre de proximité en établissement médico-social.")
d.section("CONSTATATIONS")
d.para("Syndrome dépressif caractérisé d'intensité sévère : humeur triste permanente, anhédonie, troubles du sommeil majeurs, ruminations anxieuses centrées sur le travail, perte de poids (6 kg en 3 mois), idéation suicidaire passive sans scénario.")
d.para("Symptomatologie apparue progressivement dans un contexte décrit de surcharge professionnelle durable, d'objectifs contradictoires et d'isolement managérial.")
d.section("DIAGNOSTIC ÉVOQUÉ")
d.para("Épisode dépressif caractérisé sévère, sans symptôme psychotique, en lien évoqué avec l'activité professionnelle (maladie hors tableau).", bold=True)
d.para("Date de première constatation médicale : 18/02/2026.", bold=True)
d.para("Arrêt de travail initial prescrit. Orientation vers suivi psychiatrique spécialisé.")
d.signature("Fait à Villefictive, le 18/02/2026", ["Dr Paul EXEMPLE", "(signature fictive)"])
d.save()

# ============ 2. Notification refus CPAM ============
d = Doc("2-notification-refus-cpam.pdf", accent=ADM)
d.letterhead("CPAM FICTIVE DE LA DÉMONSTRATION", ["Service Risques Professionnels",
                                                  "99 avenue de l'Administration, 99000 Villefictive",
                                                  "www.cpam-fictive-demonstration.example (site fictif)"],
             right_lines=["Villefictive, le 12/05/2026",
                          "Dossier n° MP-FICTIF-2026-00427",
                          "NIR fictif : 2 81 03 99 999 999"])
d.para("Mme DEMONSTRATION Claire", bold=True)
d.para("Objet : notification de décision — refus de reconnaissance du caractère professionnel de votre maladie", bold=True, color=ADM)
d.para("Lettre recommandée avec accusé de réception (fictive)", size=8.5, color=(0.4, 0.4, 0.4))
d.para("Madame,")
d.para("Vous avez déclaré le 24/02/2026 une maladie « épisode dépressif sévère » que vous estimez d'origine professionnelle.")
d.para("Après instruction, votre maladie ne figure dans aucun tableau de maladies professionnelles du régime général.", bold=True)
d.para("Conformément à l'article L.461-1 du code de la sécurité sociale, la reconnaissance au titre du système complémentaire nécessite que l'incapacité permanente prévisible soit au moins égale à 25 % et que le lien direct et essentiel avec le travail habituel soit établi par le Comité Régional de Reconnaissance des Maladies Professionnelles (CRRMP).")
d.para("Le médecin-conseil a évalué votre taux d'incapacité permanente prévisible à 20 %, taux inférieur au seuil requis. En conséquence, votre dossier n'a pas été transmis au CRRMP et votre demande est REJETÉE.", bold=True)
d.box("VOIES ET DÉLAIS DE RECOURS",
      ["Vous disposez d'un délai de DEUX MOIS à compter de la réception de la présente pour saisir la",
       "Commission de Recours Amiable (CRA) de notre organisme.",
       "Vous pouvez également contester l'évaluation médicale (taux d'incapacité prévisible) selon les",
       "modalités prévues par le code de la sécurité sociale."])
d.signature("Villefictive, le 12/05/2026", ["Le Directeur (fictif)", "CPAM fictive de la Démonstration"])
d.save()

# ============ 3. Compte rendu psychiatrique ============
d = Doc("3-compte-rendu-psychiatrique.pdf", accent=MED)
d.letterhead("Dr Anne SPECIMEN — Psychiatre", ["RPPS fictif 99999999902 — Cabinet fictif",
                                               "4 avenue de l'Exemple, 99000 Villefictive",
                                               "Consultations sur rendez-vous (fictif)"],
             right_lines=["Villefictive, le 20/06/2026"])
d.title("COMPTE RENDU DE SUIVI PSYCHIATRIQUE", sub="Document fictif établi pour la démonstration")
d.para("Patiente : Mme DEMONSTRATION Claire, 45 ans (identité fictive)", bold=True)
d.para("Suivie depuis le 03/03/2026 — 6 consultations à ce jour.")
d.section("ANAMNÈSE")
d.para("Cadre de proximité depuis 2015, décrit depuis 2023 une dégradation continue des conditions d'exercice : sous-effectif chronique, injonctions contradictoires, astreintes non compensées, alerte adressée à la direction en 09/2025 restée sans réponse.")
d.para("Pas d'antécédent psychiatrique personnel ou familial. Pas de facteur de vulnérabilité extra-professionnel identifié à ce jour.")
d.section("CLINIQUE ACTUELLE")
d.para("Épisode dépressif caractérisé d'intensité sévère (PHQ-9 : 21/27). Ruminations exclusivement centrées sur la sphère professionnelle, reviviscences anxieuses à l'évocation du lieu de travail, évitement. Amélioration partielle depuis l'éloignement du poste (arrêt de travail continu).")
d.section("TRAITEMENT")
d.para("Sertraline 100 mg/j (fictif), psychothérapie hebdomadaire.")
d.section("ÉVOLUTION")
d.para("Stabilisation lente ; incapacité durable prévisible en l'état. L'imputabilité professionnelle apparaît cliniquement prépondérante.", bold=True)
d.signature("Villefictive, le 20/06/2026", ["Dr Anne SPECIMEN, psychiatre", "RPPS fictif 99999999902 (signature fictive)"])
d.save()

# ============ 4. Arrêt de travail — version DÉGRADÉE (scan flou volontaire) ============
img = Image.new("RGB", (1240, 1754), "#f4f1ea")
dr = ImageDraw.Draw(img)
try:
    f_big = ImageFont.truetype("/app/backend/fonts/DejaVuSans-Bold.ttf", 34)
    f_txt = ImageFont.truetype("/app/backend/fonts/DejaVuSans.ttf", 26)
    f_wm = ImageFont.truetype("/app/backend/fonts/DejaVuSans-Bold.ttf", 48)
except Exception:
    f_big = f_txt = f_wm = ImageFont.load_default()
dr.rectangle([60, 40, 1180, 130], outline="#555", width=3)
dr.text((80, 62), "AVIS D'ARRÊT DE TRAVAIL (prolongation)", font=f_big, fill="#222")
lines4 = ["Cerfa fictif n° 10170*07", "", "Patiente : Mme DEMONSTRATION Claire (identité fictive)",
          "Prolongation du 15/04/2026 au 15/06/2026 inclus",
          "Motif : épisode dépressif sévère — lien professionnel évoqué",
          "Sorties autorisées : oui, en dehors des heures de présence obligatoire",
          "", "Dr Paul EXEMPLE — 18/04/2026 (signature fictive illisible)"]
y = 180
for l in lines4:
    dr.text((80, y), l, font=f_txt, fill="#333")
    y += 48
dr.rectangle([60, 620, 1180, 624], fill="#888")
img = img.rotate(-2, expand=False, fillcolor="#e8e4da")
img = img.filter(ImageFilter.GaussianBlur(3.2)).resize((520, 736)).resize((1240, 1754))
wm = Image.new("RGBA", img.size, (0, 0, 0, 0))
dw = ImageDraw.Draw(wm)
dw.text((150, 700), "CAS FICTIF DE DÉMONSTRATION", font=f_wm, fill=(200, 30, 30, 110))
wm = wm.rotate(30, center=(620, 877))
dwb = ImageDraw.Draw(wm)
try:
    f_band = ImageFont.truetype("/app/backend/fonts/DejaVuSans-Bold.ttf", 26)
except Exception:
    f_band = f_txt
dwb.text((70, 30), "CAS FICTIF DE DÉMONSTRATION — Aucune personne réelle.", font=f_band, fill=(170, 20, 20, 230))
img = Image.alpha_composite(img.convert("RGBA"), wm).convert("RGB")
img.save(f"{OUT}/4-arret-travail-scan-degrade.pdf", "PDF", resolution=100)
print("OK 4-arret-travail-scan-degrade.pdf (volontairement flou)")

# ============ 5. Attestation contexte professionnel ============
d = Doc("5-elements-contexte-professionnel.pdf", accent=ATT)
d.letterhead("RÉSIDENCE DE LA DÉMONSTRATION", ["Établissement médico-social fictif",
                                               "Instance représentative du personnel",
                                               "7 chemin du Modèle, 99000 Villefictive"],
             right_lines=["Villefictive, le 02/04/2026"])
d.title("ATTESTATION ET ÉLÉMENTS DE CONTEXTE PROFESSIONNEL", sub="Document fictif établi pour la démonstration")
d.para("Je soussignée, Mme Sophie MODELE, déléguée du personnel (fictive) de l'établissement « Résidence de la Démonstration » (structure fictive), atteste des faits suivants :")
d.para("1.  Depuis janvier 2023, le service encadré par Mme DEMONSTRATION fonctionne en sous-effectif permanent (2 postes vacants non remplacés sur 8).", bold=True, indent=3 * mm)
d.para("2.  Un signalement écrit sur la surcharge de l'encadrement a été transmis à la direction le 14/09/2025 (copie jointe au CSE fictif). Aucune mesure n'a suivi.", bold=True, indent=3 * mm)
d.para("3.  Les astreintes de week-end ont doublé entre 2024 et 2026 sans compensation.", bold=True, indent=3 * mm)
d.para("4.  Deux autres salariés du même service sont en arrêt pour des motifs similaires.", bold=True, indent=3 * mm)
d.box("PIÈCE JOINTE — FICHE DE POSTE (extrait)",
      ["Encadrement d'équipe, continuité de service, gestion des situations de crise,",
       "disponibilité permanente téléphonique."],
      fill=(0.97, 0.95, 0.91))
d.para("Fait pour servir et valoir ce que de droit (document fictif de démonstration).")
d.signature("Villefictive, le 02/04/2026", ["Mme Sophie MODELE", "Déléguée du personnel (fictive)"])
d.save()

# ============ 6. Courrier médecin conseil ============
d = Doc("6-courrier-medecin-conseil.pdf", accent=ADM)
d.letterhead("SERVICE MÉDICAL", ["CPAM fictive de la Démonstration",
                                 "Échelon local du service médical (fictif)",
                                 "99 avenue de l'Administration, 99000 Villefictive"],
             right_lines=["Villefictive, le 05/05/2026",
                          "Réf. dossier MP-FICTIF-2026-00427"])
d.para("Mme DEMONSTRATION Claire", bold=True)
d.para("Objet : évaluation du taux d'incapacité permanente prévisible", bold=True, color=ADM)
d.para("Madame,")
d.para("À la suite de l'examen du 28/04/2026, le service médical retient :")
d.para("—  épisode dépressif caractérisé, d'intensité jugée « modérée à sévère » à l'examen ;", bold=True, indent=3 * mm)
d.para("—  retentissement socioprofessionnel présent mais estimé « partiellement réversible » ;", bold=True, indent=3 * mm)
d.para("—  taux d'incapacité permanente PRÉVISIBLE évalué à 20 %.", bold=True, indent=3 * mm)
d.para("Ce taux étant inférieur au seuil de 25 % prévu à l'article R.461-8 du code de la sécurité sociale, les conditions de saisine du CRRMP ne sont pas réunies.")
d.box("ÉLÉMENTS NOUVEAUX RECEVABLES",
      ["Il vous est loisible de produire tout élément médical nouveau de nature à modifier cette",
       "évaluation : expertise psychiatrique détaillée, échelles d'évaluation, retentissement",
       "fonctionnel documenté."])
d.signature("Villefictive, le 05/05/2026", ["Dr Marc TYPE, médecin-conseil (fictif)", "Service médical — CPAM fictive"])
d.save()

# ============ ZIP ============
import zipfile
with zipfile.ZipFile(f"{OUT}/cas-demonstration-complet.zip", "w") as z:
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".pdf"):
            z.write(f"{OUT}/{f}", f)
print("ZIP OK —", sorted(f for f in os.listdir(OUT) if f.endswith(('.pdf', '.zip'))))
