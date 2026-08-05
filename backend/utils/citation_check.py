"""
LOT 1 — PHASE C3 : Validateur programmatique de citations (anti-hallucination).

Principe : toute citation entre guillemets français « … » présente dans le rapport
doit exister verbatim (à la normalisation près) dans le texte extrait des documents.
- Citation retrouvée → référence (document, page) déterminée depuis les balises existantes.
- Citation introuvable → annotée « [référence non vérifiée] » dans le rapport.
Jamais bloquant : en cas d'erreur interne, le rapport est livré inchangé.
"""
import re
import unicodedata
from config import logger

MIN_CITATION_LEN = 20   # en-dessous : trop court pour être une citation documentaire significative
MAX_CITATION_LEN = 400

_CITATION_RE = re.compile(r"«\s*([^«»]{%d,%d}?)\s*»" % (MIN_CITATION_LEN, MAX_CITATION_LEN))
_PAGE_RE = re.compile(r"\[Page\s+(\d+)\]", re.IGNORECASE)
_DOC_HEADER_RE = re.compile(r"---\s*(.+?)\s*(?:\([^)]*\))?\s*---")


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def _locate(citation_norm: str, source_norm: str, source_raw: str) -> dict:
    """Retourne {found, doc, page} en localisant la citation normalisée dans la source."""
    idx = source_norm.find(citation_norm)
    if idx < 0:
        return {"found": False}
    # Approximation de la position dans le texte brut (ratio de longueur)
    ratio = idx / max(len(source_norm), 1)
    raw_idx = int(ratio * len(source_raw))
    before = source_raw[:raw_idx + len(citation_norm)]
    pages = _PAGE_RE.findall(before)
    docs = _DOC_HEADER_RE.findall(before)
    return {
        "found": True,
        "doc": docs[-1].strip() if docs else None,
        "page": int(pages[-1]) if pages else None,
    }


def verify_citations(analysis: str, documents_text: str) -> tuple:
    """Vérifie chaque citation « … » du rapport contre le texte des documents.
    Retourne (analysis annoté, stats)."""
    stats = {"total": 0, "verified": 0, "unverified": 0, "details": []}
    if not documents_text or not documents_text.strip():
        return analysis, stats

    source_norm = _normalize(documents_text)

    def _check(match):
        citation = match.group(1).strip()
        stats["total"] += 1
        loc = _locate(_normalize(citation), source_norm, documents_text)
        if loc["found"]:
            stats["verified"] += 1
            stats["details"].append({"citation": citation[:120], "verified": True,
                                     "doc": loc.get("doc"), "page": loc.get("page")})
            return match.group(0)
        stats["unverified"] += 1
        stats["details"].append({"citation": citation[:120], "verified": False})
        return f"{match.group(0)} [référence non vérifiée]"

    annotated = _CITATION_RE.sub(_check, analysis)
    return annotated, stats
