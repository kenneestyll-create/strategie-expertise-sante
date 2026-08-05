"""
LOT 1 — PHASE A : Rapport qualité documentaire (module quality_report, SF1+SF2 fusionnés).

CONTRAT A — Qualité par page (schéma stable, OCR-agnostique) :
  {doc_index, doc_name, page, exploitability: 'ok'|'partial'|'unusable', chars, illisible_marks, weight}
  Tout futur moteur OCR (Mistral, Document AI...) doit produire ce schéma via un adaptateur.

CONTRAT B — Fiche structurée (posé, implémentation Lot 2) :
  {acteurs: {employeur, assureur, organisme, expert}, dates: [...], taux: [...], garanties: [...], delais: [...]}

Garanties zéro régression :
  - Dérivé UNIQUEMENT des sorties d'extraction existantes (texte balisé [Page N], statuts, comptes de pages).
  - AUCUN appel LLM, AUCUNE modification du prompt d'extraction ni du moteur d'analyse.
  - Toute erreur interne → quality_report = None (le pipeline continue à l'identique).
"""
import re
from config import logger

FORMULA_VERSION = "1.1"

# Seuils v1 (calibrage prévu après 50-100 dossiers réels — cf. étude d'architecture)
CHARS_OK = 150          # page considérée exploitable
CHARS_MIN = 20          # en-dessous : inexploitable
LETTER_RATIO_MIN = 0.5  # ratio de caractères alphanumériques minimal (bruit OCR)

# v1.1 — Pondération par importance de pièce (déterministe, mots-clés, aucun appel LLM)
ESSENTIAL_WEIGHT = 1.5
_ESSENTIAL_KEYWORDS = (
    "expertise", "conclusions de l'expert",
    "taux d'incapacité", "taux d'ipp", "taux ipp", "consolidation",
    "notification", "décision", "decision", "cdaph", "cpam", "caisse primaire",
    "contrat d'assurance", "conditions générales", "avenant", "tableau des garanties",
)

LEVELS = [(97, "Excellent"), (90, "Élevé"), (75, "Bon"), (50, "Moyen"), (0, "Faible")]

_PAGE_RE = re.compile(r"\[Page\s+(\d+)\]", re.IGNORECASE)
_ILLISIBLE_RE = re.compile(r"\[illisible\]", re.IGNORECASE)

# Statuts fichier → exploitabilité par défaut quand aucune granularité page n'est disponible
_STATUS_FALLBACK = {
    "text_extracted": "ok",
    "vision_extracted": "ok",
    "ocr_extracted": "ok",
    "vision_partial": "partial",
    "partially_readable": "partial",
}


def _split_pages(text: str) -> dict:
    """Découpe le texte extrait en blocs par numéro de page via le balisage [Page N] existant."""
    if not text:
        return {}
    matches = list(_PAGE_RE.finditer(text))
    if not matches:
        return {}
    blocks = {}
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        page_num = int(m.group(1))
        blocks[page_num] = blocks.get(page_num, "") + text[start:end]
    return blocks


def _classify_block(block: str) -> tuple:
    """Retourne (exploitability, chars, illisible_marks) pour un bloc de page."""
    clean = block.strip()
    chars = len(clean)
    illisible = len(_ILLISIBLE_RE.findall(clean))
    if chars < CHARS_MIN:
        return "unusable", chars, illisible
    letters = len(re.findall(r"[0-9A-Za-zÀ-ÿ]", clean))
    noisy = (letters / chars) < LETTER_RATIO_MIN if chars else True
    if chars >= CHARS_OK and illisible == 0 and not noisy:
        return "ok", chars, illisible
    return "partial", chars, illisible


def _doc_weight(name: str, text: str) -> float:
    """Poids déterministe : 1.5 si la pièce paraît essentielle (expertise, notification,
    décision, contrat), 1.0 sinon. Basé sur le nom de fichier + le début du texte extrait."""
    probe = f"{name} {text[:3000]}".lower().replace("_", " ").replace("-", " ")
    return ESSENTIAL_WEIGHT if any(k in probe for k in _ESSENTIAL_KEYWORDS) else 1.0


def _score_to_level(score: float) -> str:
    for threshold, label in LEVELS:
        if score >= threshold:
            return label
    return "Faible"


def build_quality_report(results: list) -> dict:
    """Construit le rapport qualité documentaire (Contrat A + agrégat SF2) depuis les
    résultats d'extraction existants. Pur, synchrone, sans effet de bord."""
    pages_records = []
    per_document = []

    for doc_index, r in enumerate(results):
        name = r.get("name", "?")
        declared_pages = r.get("pages", 0) or 0
        status = r.get("status", "")
        text = r.get("text", "") or ""
        blocks = _split_pages(text)
        weight = _doc_weight(name, text)

        doc_pages = []
        if declared_pages and blocks:
            for p in range(1, declared_pages + 1):
                if p in blocks:
                    exploit, chars, ill = _classify_block(blocks[p])
                else:
                    exploit, chars, ill = "unusable", 0, 0
                doc_pages.append({"page": p, "exploitability": exploit, "chars": chars, "illisible_marks": ill})
            # Pages balisées au-delà du compte déclaré (rare) : on les intègre
            for p in sorted(blocks):
                if p > declared_pages:
                    exploit, chars, ill = _classify_block(blocks[p])
                    doc_pages.append({"page": p, "exploitability": exploit, "chars": chars, "illisible_marks": ill})
        else:
            # Pas de granularité page (image, txt, extraction sans balise) → fallback statut fichier
            fallback = _STATUS_FALLBACK.get(status, "unusable" if not text.strip() else "partial")
            n = max(declared_pages, 1)
            for p in range(1, n + 1):
                doc_pages.append({"page": p, "exploitability": fallback, "chars": len(text) // n, "illisible_marks": 0})

        for pr in doc_pages:
            pages_records.append({"doc_index": doc_index, "doc_name": name, "weight": weight, **pr})

        per_document.append({
            "name": name,
            "status": status,
            "weight": weight,
            "essential": weight > 1.0,
            "pages_total": len(doc_pages),
            "pages_ok": sum(1 for p in doc_pages if p["exploitability"] == "ok"),
            "pages_partial": sum(1 for p in doc_pages if p["exploitability"] == "partial"),
            "pages_unusable": sum(1 for p in doc_pages if p["exploitability"] == "unusable"),
            "partial_pages": [p["page"] for p in doc_pages if p["exploitability"] == "partial"],
            "unusable_pages": [p["page"] for p in doc_pages if p["exploitability"] == "unusable"],
        })

    pages_total = len(pages_records)
    pages_ok = sum(1 for p in pages_records if p["exploitability"] == "ok")
    pages_partial = sum(1 for p in pages_records if p["exploitability"] == "partial")
    pages_unusable = pages_total - pages_ok - pages_partial

    # v1.1 — Score pondéré par importance de pièce
    _VALUE = {"ok": 1.0, "partial": 0.5, "unusable": 0.0}
    weight_sum = sum(p["weight"] for p in pages_records)
    if weight_sum:
        score = round(sum(p["weight"] * _VALUE[p["exploitability"]] for p in pages_records) / weight_sum * 100, 1)
    else:
        score = 0.0
    level = _score_to_level(score)

    # v1.1 — Alertes pièces essentielles dégradées + plafonnement anti-score-artificiel
    alerts = []
    for d in per_document:
        if d["essential"] and d["pages_unusable"] > 0:
            alerts.append({"type": "essential_degraded", "doc": d["name"], "unusable_pages": d["unusable_pages"]})
            if d["pages_unusable"] > d["pages_total"] * 0.5 and level in ("Excellent", "Élevé", "Bon"):
                level = "Moyen"  # une pièce essentielle majoritairement illisible plafonne le niveau

    return {
        "formula_version": FORMULA_VERSION,
        "files": len(results),
        "pages_total": pages_total,
        "pages_ok": pages_ok,
        "pages_partial": pages_partial,
        "pages_unusable": pages_unusable,
        "confidence_score": score,
        "confidence_level": level,
        "alerts": alerts,
        "per_document": per_document,
        "pages": pages_records,
    }


def stats_record(quality_report: dict) -> dict:
    """Enregistrement anonymisé pour docchain_stats — AUCUN texte, AUCUN identifiant, AUCUN nom de fichier."""
    return {
        "formula_version": quality_report.get("formula_version"),
        "files": quality_report.get("files"),
        "pages_total": quality_report.get("pages_total"),
        "pages_ok": quality_report.get("pages_ok"),
        "pages_partial": quality_report.get("pages_partial"),
        "pages_unusable": quality_report.get("pages_unusable"),
        "confidence_score": quality_report.get("confidence_score"),
        "confidence_level": quality_report.get("confidence_level"),
        "alerts_count": len(quality_report.get("alerts", [])),
        "statuses": [d.get("status") for d in quality_report.get("per_document", [])],
    }
