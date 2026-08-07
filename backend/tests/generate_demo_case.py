"""Génère le cas fictif de démonstration (Mme DEMONSTRATION Claire) — programme Évaluateur Expert."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = "/app/frontend/public/cas-demonstration"
os.makedirs(OUT, exist_ok=True)
W, H = A4

def watermark(c):
    c.saveState()
    c.setFont("Helvetica-Bold", 32)
    c.setFillColorRGB(0.85, 0.1, 0.1, alpha=0.15)
    c.translate(W / 2, H / 2)
    c.rotate(40)
    c.drawCentredString(0, 0, "CAS FICTIF DE DÉMONSTRATION")
    c.drawCentredString(0, -120, "CAS FICTIF DE DÉMONSTRATION")
    c.drawCentredString(0, 120, "CAS FICTIF DE DÉMONSTRATION")
    c.restoreState()
    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(0.7, 0.1, 0.1)
    c.drawCentredString(W / 2, H - 12 * mm, "⚠ CAS FICTIF DE DÉMONSTRATION — Aucune personne réelle. Document créé pour l'évaluation de Dossier Express IA.")

def doc(filename, title, lines, sender=""):
    c = canvas.Canvas(f"{OUT}/{filename}", pagesize=A4)
    watermark(c)
    y = H - 25 * mm
    c.setFillColorRGB(0, 0, 0)
    if sender:
        c.setFont("Helvetica", 9)
        for s in sender.split("\n"):
            c.drawString(20 * mm, y, s); y -= 4.5 * mm
        y -= 6 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20 * mm, y, title); y -= 10 * mm
    for line in lines:
        if y < 25 * mm:
            c.showPage(); watermark(c); c.setFillColorRGB(0, 0, 0); y = H - 25 * mm
        if line.startswith("**"):
            c.setFont("Helvetica-Bold", 10); line = line[2:]
        else:
            c.setFont("Helvetica", 10)
        c.drawString(20 * mm, y, line); y -= 5.5 * mm
    c.save()
    print("OK", filename)

# 1. Certificat médical initial
doc("1-certificat-medical-initial.pdf",
    "CERTIFICAT MÉDICAL INITIAL — Maladie professionnelle (Cerfa fictif)",
    ["Je soussigné, Dr Paul EXEMPLE, médecin généraliste (RPPS fictif 99999999901),",
     "certifie avoir examiné ce jour :",
     "**Mme DEMONSTRATION Claire, née le 12/03/1981 (identité fictive)",
     "Profession déclarée : cadre de proximité en établissement médico-social.",
     "",
     "**Constatations :",
     "Syndrome dépressif caractérisé d'intensité sévère : humeur triste permanente,",
     "anhédonie, troubles du sommeil majeurs, ruminations anxieuses centrées sur le travail,",
     "perte de poids (6 kg en 3 mois), idéation suicidaire passive sans scénario.",
     "Symptomatologie apparue progressivement dans un contexte décrit de surcharge",
     "professionnelle durable, d'objectifs contradictoires et d'isolement managérial.",
     "",
     "**Diagnostic évoqué : épisode dépressif caractérisé sévère, sans symptôme psychotique,",
     "en lien évoqué avec l'activité professionnelle (maladie hors tableau).",
     "Date de première constatation médicale : 18/02/2026.",
     "Arrêt de travail initial prescrit. Orientation vers suivi psychiatrique spécialisé.",
     "",
     "Fait à Villefictive, le 18/02/2026 — Dr Paul EXEMPLE (signature fictive)"],
    sender="Dr Paul EXEMPLE — Cabinet médical fictif\n12 rue de la Démonstration, 99000 Villefictive")

# 2. Notification refus CPAM
doc("2-notification-refus-cpam.pdf",
    "NOTIFICATION DE DÉCISION — Refus de reconnaissance de maladie professionnelle",
    ["Dossier n° MP-FICTIF-2026-00427",
     "Assurée : Mme DEMONSTRATION Claire (NIR fictif 2 81 03 99 999 999)",
     "",
     "Madame,",
     "Vous avez déclaré le 24/02/2026 une maladie « épisode dépressif sévère » que vous",
     "estimez d'origine professionnelle.",
     "",
     "**Après instruction, votre maladie ne figure dans aucun tableau de maladies",
     "**professionnelles du régime général.",
     "",
     "Conformément à l'article L.461-1 du code de la sécurité sociale, la reconnaissance",
     "au titre du système complémentaire nécessite que l'incapacité permanente prévisible",
     "soit au moins égale à 25 % et que le lien direct et essentiel avec le travail habituel",
     "soit établi par le Comité Régional de Reconnaissance des Maladies Professionnelles (CRRMP).",
     "",
     "Le médecin-conseil a évalué votre taux d'incapacité permanente prévisible à 20 %,",
     "taux inférieur au seuil requis. En conséquence, votre dossier n'a pas été transmis",
     "au CRRMP et votre demande est REJETÉE.",
     "",
     "**Voies de recours : vous disposez de deux mois pour saisir la Commission de Recours",
     "Amiable (CRA) de notre organisme, et/ou de contester l'évaluation médicale.",
     "",
     "Villefictive, le 12/05/2026 — CPAM fictive de la Démonstration"],
    sender="CPAM FICTIVE DE LA DÉMONSTRATION\nService Risques Professionnels — 99000 Villefictive")

# 3. Compte rendu psychiatrique
doc("3-compte-rendu-psychiatrique.pdf",
    "COMPTE RENDU DE SUIVI PSYCHIATRIQUE",
    ["Patiente : Mme DEMONSTRATION Claire, 45 ans (identité fictive)",
     "Suivie depuis le 03/03/2026 — 6 consultations à ce jour.",
     "",
     "**Anamnèse : cadre de proximité depuis 2015, décrit depuis 2023 une dégradation",
     "continue des conditions d'exercice : sous-effectif chronique, injonctions",
     "contradictoires, astreintes non compensées, alerte adressée à la direction en 09/2025",
     "restée sans réponse. Pas d'antécédent psychiatrique personnel ou familial.",
     "Pas de facteur de vulnérabilité extra-professionnel identifié à ce jour.",
     "",
     "**Clinique actuelle : épisode dépressif caractérisé d'intensité sévère (PHQ-9 : 21/27).",
     "Ruminations exclusivement centrées sur la sphère professionnelle, reviviscences",
     "anxieuses à l'évocation du lieu de travail, évitement. Amélioration partielle depuis",
     "l'éloignement du poste (arrêt de travail continu).",
     "",
     "**Traitement : sertraline 100 mg/j (fictif), psychothérapie hebdomadaire.",
     "**Évolution : stabilisation lente ; incapacité durable prévisible en l'état.",
     "L'imputabilité professionnelle apparaît cliniquement prépondérante.",
     "",
     "Villefictive, le 20/06/2026 — Dr Anne SPECIMEN, psychiatre (RPPS fictif 99999999902)"],
    sender="Dr Anne SPECIMEN — Psychiatre (cabinet fictif)\n4 avenue de l'Exemple, 99000 Villefictive")

# 4. Arrêt de travail — version DÉGRADÉE (scan flou volontaire)
img = Image.new("RGB", (1240, 1754), "#f4f1ea")
d = ImageDraw.Draw(img)
try:
    f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
    f_txt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    f_wm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
except Exception:
    f_big = f_txt = f_wm = ImageFont.load_default()
d.text((80, 60), "AVIS D'ARRÊT DE TRAVAIL (prolongation)", font=f_big, fill="#222")
lines4 = ["Cerfa fictif n° 10170*07", "", "Patiente : Mme DEMONSTRATION Claire (identité fictive)",
          "Prolongation du 15/04/2026 au 15/06/2026 inclus",
          "Motif : épisode dépressif sévère — lien professionnel évoqué",
          "Sorties autorisées : oui, en dehors des heures de présence obligatoire",
          "", "Dr Paul EXEMPLE — 18/04/2026 (signature fictive illisible)"]
y = 160
for l in lines4:
    d.text((80, y), l, font=f_txt, fill="#333"); y += 48
wm = Image.new("RGBA", img.size, (0, 0, 0, 0))
dw = ImageDraw.Draw(wm)
dw.text((150, 700), "CAS FICTIF DE DÉMONSTRATION", font=f_wm, fill=(200, 30, 30, 60))
img = Image.alpha_composite(img.convert("RGBA"), wm.rotate(30, center=(620, 877))).convert("RGB")
img = img.rotate(-2, expand=False, fillcolor="#e8e4da")
img = img.filter(ImageFilter.GaussianBlur(3.2)).resize((520, 736)).resize((1240, 1754))
img.save(f"{OUT}/4-arret-travail-scan-degrade.pdf", "PDF", resolution=100)
print("OK 4-arret-travail-scan-degrade.pdf (volontairement flou)")

# 5. Attestation employeur / contexte
doc("5-elements-contexte-professionnel.pdf",
    "ATTESTATION ET ÉLÉMENTS DE CONTEXTE PROFESSIONNEL",
    ["Je soussignée, Mme Sophie MODELE, déléguée du personnel (fictive) de l'établissement",
     "« Résidence de la Démonstration » (structure fictive), atteste des faits suivants :",
     "",
     "**1. Depuis janvier 2023, le service encadré par Mme DEMONSTRATION fonctionne en",
     "sous-effectif permanent (2 postes vacants non remplacés sur 8).",
     "**2. Un signalement écrit sur la surcharge de l'encadrement a été transmis à la",
     "direction le 14/09/2025 (copie jointe au CSE fictif). Aucune mesure n'a suivi.",
     "**3. Les astreintes de week-end ont doublé entre 2024 et 2026 sans compensation.",
     "**4. Deux autres salariés du même service sont en arrêt pour des motifs similaires.",
     "",
     "Fiche de poste jointe : encadrement d'équipe, continuité de service, gestion des",
     "situations de crise, disponibilité permanente téléphonique.",
     "",
     "Fait pour servir et valoir ce que de droit (document fictif de démonstration).",
     "Villefictive, le 02/04/2026 — Mme Sophie MODELE"],
    sender="Résidence de la Démonstration (établissement fictif)\nInstance représentative du personnel")

# 6. Courrier médecin conseil
doc("6-courrier-medecin-conseil.pdf",
    "COURRIER DU SERVICE MÉDICAL — Évaluation du taux d'incapacité prévisible",
    ["Réf. dossier MP-FICTIF-2026-00427 — Mme DEMONSTRATION Claire",
     "",
     "Madame,",
     "À la suite de l'examen du 28/04/2026, le service médical retient :",
     "",
     "**- épisode dépressif caractérisé, d'intensité jugée « modérée à sévère » à l'examen ;",
     "**- retentissement socioprofessionnel présent mais estimé « partiellement réversible » ;",
     "**- taux d'incapacité permanente PRÉVISIBLE évalué à 20 %.",
     "",
     "Ce taux étant inférieur au seuil de 25 % prévu à l'article R.461-8 du code de la",
     "sécurité sociale, les conditions de saisine du CRRMP ne sont pas réunies.",
     "",
     "Il vous est loisible de produire tout élément médical nouveau de nature à modifier",
     "cette évaluation (expertise psychiatrique détaillée, échelles d'évaluation,",
     "retentissement fonctionnel documenté).",
     "",
     "Villefictive, le 05/05/2026 — Dr Marc TYPE, médecin-conseil (fictif)"],
    sender="SERVICE MÉDICAL — CPAM fictive de la Démonstration")

# ZIP
import zipfile
with zipfile.ZipFile(f"{OUT}/cas-demonstration-complet.zip", "w") as z:
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".pdf"):
            z.write(f"{OUT}/{f}", f)
print("ZIP OK —", os.listdir(OUT))
