"""
CONSOLIDATION_ARCHITECTURE — Extraction documentaire centralisee.
Fournit les fonctions d'extraction texte (PDF, images, OCR).
Consommateurs : routes/dossier_express.py
"""
import os
import tempfile
from config import logger


def preprocess_image(pil_image):
    """Pre-process image for better OCR: contrast, sharpen, denoise, deskew."""
    from PIL import ImageEnhance, ImageFilter, Image as PILImage

    img = pil_image
    if img.mode != 'RGB':
        img = img.convert('RGB')

    try:
        from PIL import ImageOps
        img = ImageOps.autocontrast(img, cutoff=0.5)
    except Exception:
        pass

    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = img.filter(ImageFilter.MedianFilter(size=3))

    w, h = img.size
    if w < 1500:
        scale = 1500 / w
        img = img.resize((int(w * scale), int(h * scale)), PILImage.LANCZOS)

    return img


async def extract_pdf_with_gemini(file_bytes: bytes, name: str) -> tuple[str, str, int, str]:
    """Cloud-based PDF extraction via Gemini 2.5 Pro (native PDF support).

    Robust against missing system binaries (no Tesseract/Poppler dependency).
    Auto-chunks heavy PDFs (>3MB or >6 pages) into smaller batches to avoid 502 errors.

    Returns: (extracted_text, method_label, page_count, status)
    """
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
    except ImportError as e:
        logger.error(f"PDF '{name}': emergentintegrations not available: {e}")
        return "", "Gemini Vision indisponible (lib manquante)", 0, "extraction_failed"

    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        logger.error(f"PDF '{name}': EMERGENT_LLM_KEY missing in env")
        return "", "Cle Emergent LLM manquante", 0, "extraction_failed"

    # Probe page count
    total_pages = 0
    try:
        import pypdfium2
        import io as _io
        pdf_doc = pypdfium2.PdfDocument(_io.BytesIO(file_bytes))
        total_pages = len(pdf_doc)
        pdf_doc.close()
    except Exception:
        pass

    # Decide whether to chunk
    HEAVY_THRESHOLD_BYTES = 3 * 1024 * 1024  # 3MB
    HEAVY_PAGES = 6
    needs_chunking = len(file_bytes) > HEAVY_THRESHOLD_BYTES or total_pages > HEAVY_PAGES

    if not needs_chunking:
        return await _gemini_extract_single(file_bytes, name, total_pages, api_key)

    # Heavy PDF: split by pages and process in chunks
    logger.info(f"PDF '{name}' is heavy ({len(file_bytes)//1024}KB, {total_pages}p) → chunking")
    return await _gemini_extract_chunked(file_bytes, name, total_pages, api_key, chunk_size=4)


async def _gemini_extract_single(file_bytes: bytes, name: str, total_pages: int, api_key: str) -> tuple[str, str, int, str]:
    """Send a small PDF to Gemini in a single shot."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        chat = LlmChat(
            api_key=api_key,
            session_id=f"pdf-extract-{name}",
            system_message=(
                "Tu es un expert en extraction de texte depuis des documents medicaux et juridiques en francais. "
                "Tu extrais TOUT le texte visible d'un PDF (texte natif ET texte scanne par OCR), incluant "
                "en-tetes, pieds de page, tampons, signatures dechiffrables, tableaux, listes, et notes manuscrites lisibles. "
                "Tu preserves la structure (paragraphes, listes, sections). Tu n'inventes RIEN. "
                "Si certaines parties sont illisibles, tu indiques [illisible]."
            ),
        ).with_model("gemini", "gemini-2.5-pro")

        pdf_file = FileContentWithMimeType(file_path=tmp_path, mime_type="application/pdf")
        prompt = (
            "Extrais l'INTEGRALITE du texte de ce PDF page par page. Format :\n"
            "[Page 1]\n<texte>\n\n[Page 2]\n<texte>\n\n...\n\n"
            "IMPORTANT : aucun commentaire, aucune analyse, aucun resume. Uniquement le texte brut."
        )
        response = await chat.send_message(UserMessage(text=prompt, file_contents=[pdf_file]))

        if response and len(response.strip()) > 50:
            method = f"PDF — {total_pages} page{'s' if total_pages > 1 else ''}, extraction Gemini Vision"
            logger.info(f"PDF '{name}': Gemini Vision OK ({len(response)} chars, {total_pages} pages)")
            return response.strip(), method, total_pages, "vision_extracted"

        logger.warning(f"PDF '{name}': Gemini returned empty/too short response")
        return "", f"PDF — {total_pages} page{'s' if total_pages > 1 else ''}, Gemini sans resultat", total_pages, "vision_empty"
    except Exception as e:
        logger.error(f"PDF '{name}': Gemini Vision (single) failed: {e}")
        return "", f"Gemini Vision erreur: {str(e)[:80]}", total_pages, "vision_error"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


async def _gemini_extract_chunked(file_bytes: bytes, name: str, total_pages: int, api_key: str, chunk_size: int = 4) -> tuple[str, str, int, str]:
    """Split heavy PDF into chunks of N pages and call Gemini for each chunk."""
    import pypdfium2
    import io as _io
    from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
    from pypdf import PdfReader, PdfWriter

    src = PdfReader(_io.BytesIO(file_bytes))
    src_pages = len(src.pages)
    if total_pages == 0:
        total_pages = src_pages

    chunks_text: list[str] = []
    failures = 0

    for chunk_start in range(0, src_pages, chunk_size):
        chunk_end = min(chunk_start + chunk_size, src_pages)
        # Build sub-PDF
        writer = PdfWriter()
        for p in range(chunk_start, chunk_end):
            writer.add_page(src.pages[p])
        sub_buf = _io.BytesIO()
        writer.write(sub_buf)
        sub_bytes = sub_buf.getvalue()

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(sub_bytes)
                tmp_path = tmp.name

            chat = LlmChat(
                api_key=api_key,
                session_id=f"pdf-chunk-{name}-{chunk_start}",
                system_message=(
                    "Tu extrais le texte brut d'un PDF medical/juridique francais (natif ET scanne). "
                    "Aucune analyse, aucun commentaire, aucun resume. Texte uniquement, structure par page."
                ),
            ).with_model("gemini", "gemini-2.5-pro")

            pdf_file = FileContentWithMimeType(file_path=tmp_path, mime_type="application/pdf")
            prompt = (
                f"Extrais l'INTEGRALITE du texte de ces pages (numerotees a partir de {chunk_start + 1}).\n"
                f"Format :\n[Page {chunk_start + 1}]\n<texte>\n\n"
                "IMPORTANT : aucun commentaire, aucune analyse. Uniquement le texte brut."
            )
            response = await chat.send_message(UserMessage(text=prompt, file_contents=[pdf_file]))

            if response and len(response.strip()) > 30:
                chunks_text.append(response.strip())
                logger.info(f"PDF '{name}': chunk {chunk_start+1}-{chunk_end} OK ({len(response)} chars)")
            else:
                failures += 1
                logger.warning(f"PDF '{name}': chunk {chunk_start+1}-{chunk_end} empty")
        except Exception as e:
            failures += 1
            logger.error(f"PDF '{name}': chunk {chunk_start+1}-{chunk_end} failed: {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    if not chunks_text:
        return "", f"PDF — {total_pages} pages, Gemini Vision chunked echoue", total_pages, "vision_error"

    extracted = "\n\n".join(chunks_text)
    chunks_done = len(chunks_text)
    chunks_total = (src_pages + chunk_size - 1) // chunk_size
    method = f"PDF — {total_pages} pages, Gemini Vision ({chunks_done}/{chunks_total} chunks OK)"
    status = "vision_extracted" if failures == 0 else "vision_partial"
    logger.info(f"PDF '{name}': Gemini chunked OK ({len(extracted)} chars, {chunks_done}/{chunks_total} chunks)")
    return extracted, method, total_pages, status


def ocr_page(pil_image, page_num, name, enhanced=False):
    """OCR a single page image, return (text, quality_label)."""
    import pytesseract

    try:
        if enhanced:
            pil_image = preprocess_image(pil_image)

        text = pytesseract.image_to_string(pil_image, lang='fra+eng', config='--psm 6')

        if text and text.strip():
            clean = text.strip()
            if len(clean) > 50:
                return clean, "lisible"
            elif len(clean) > 10:
                return clean, "partiellement lisible"
        return "", "non lisible"
    except Exception as e:
        logger.warning(f"OCR page {page_num} of '{name}' failed: {e}")
        return "", "non lisible"


async def extract_pdf_full_pipeline(file_bytes: bytes, name: str):
    """Production-grade PDF extraction with cloud Vision fallback.

    Architecture (no system binary dependency required):
      Level 1: pdfplumber (Python pur, gratuit, instantané) — pour PDFs avec texte natif
      Level 2: Gemini Vision (cloud, ~0.05€/PDF, robuste) — pour PDFs scannés
      Level 3: Tesseract OCR (legacy, optionnel) — fallback de dernier recours si Gemini indisponible
    """
    import io

    total_pages = 0

    # === LEVEL 1: Native text extraction (pdfplumber) ===
    try:
        import pdfplumber
        pdf = pdfplumber.open(io.BytesIO(file_bytes))
        total_pages = len(pdf.pages)
        pages_text = []
        pages_quality = []
        for i, page in enumerate(pdf.pages[:30]):
            text = page.extract_text()
            if text and text.strip() and len(text.strip()) > 20:
                pages_text.append(f"[Page {i+1}] {text.strip()}")
                pages_quality.append("lisible")
            else:
                pages_quality.append("non lisible")
        pdf.close()

        readable = sum(1 for q in pages_quality if q == "lisible")
        if readable >= total_pages * 0.6:
            extracted = "\n\n".join(pages_text)
            method = f"PDF texte — {total_pages} page{'s' if total_pages > 1 else ''}, extraction directe ({readable}/{total_pages} pages lisibles)"
            logger.info(f"PDF '{name}': extraction texte reussie ({len(extracted)} chars, {readable}/{total_pages} pages)")
            return extracted, method, total_pages, "text_extracted"
        elif readable > 0:
            logger.info(f"PDF '{name}': pdfplumber partiel ({readable}/{total_pages}), bascule sur Gemini Vision")
        else:
            logger.info(f"PDF '{name}': pdfplumber 0 pages lisibles, bascule sur Gemini Vision")
    except Exception as e:
        logger.warning(f"PDF '{name}': pdfplumber failed: {e}")

    # === LEVEL 2: Gemini Vision (cloud, robust to missing binaries) ===
    text, method, pages, status = await extract_pdf_with_gemini(file_bytes, name)
    if status == "vision_extracted" and text:
        return text, method, pages or total_pages, status

    logger.warning(f"PDF '{name}': Gemini Vision a echoue (status={status}), tentative Tesseract local")

    # === LEVEL 3: Tesseract OCR fallback (only if Gemini fails AND Tesseract is installed) ===
    try:
        import pypdfium2
        import pytesseract
        # Probe Tesseract availability
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            logger.warning(f"PDF '{name}': Tesseract not installed, skipping OCR fallback")
            return "", f"PDF — {total_pages} page{'s' if total_pages > 1 else ''}, extraction impossible (Vision IA + Tesseract indisponibles)", total_pages, "extraction_failed"

        pdf_doc = pypdfium2.PdfDocument(io.BytesIO(file_bytes))
        total_pages = len(pdf_doc)
        pages_to_ocr = min(total_pages, 20)

        ocr_pages = []
        ocr_quality = []
        for i in range(pages_to_ocr):
            page = pdf_doc[i]
            bitmap = page.render(scale=2)
            pil_image = bitmap.to_pil()
            text, quality = ocr_page(pil_image, i + 1, name, enhanced=False)
            if text:
                ocr_pages.append(f"[Page {i+1}] {text}")
            ocr_quality.append(quality)
            pil_image.close()

        readable_ocr = sum(1 for q in ocr_quality if q == "lisible")
        if readable_ocr >= pages_to_ocr * 0.5:
            extracted = "\n\n".join(ocr_pages)
            method = f"PDF — {total_pages} page{'s' if total_pages > 1 else ''}, OCR Tesseract de secours ({readable_ocr}/{pages_to_ocr} pages)"
            logger.info(f"PDF '{name}': Tesseract fallback OK ({len(extracted)} chars)")
            pdf_doc.close()
            return extracted, method, total_pages, "ocr_extracted"

        # Enhanced OCR last attempt
        enhanced_pages = []
        for i in range(pages_to_ocr):
            page = pdf_doc[i]
            bitmap = page.render(scale=3)
            pil_image = bitmap.to_pil()
            text, quality = ocr_page(pil_image, i + 1, name, enhanced=True)
            if text:
                enhanced_pages.append(f"[Page {i+1}] {text}")
            pil_image.close()
        pdf_doc.close()

        if enhanced_pages:
            extracted = "\n\n".join(enhanced_pages)
            method = f"PDF — {total_pages} page{'s' if total_pages > 1 else ''}, OCR renforce de secours"
            return extracted, method, total_pages, "ocr_extracted"

    except Exception as e:
        logger.error(f"PDF '{name}': Tesseract fallback failed: {e}")

    return "", f"PDF — {total_pages} page{'s' if total_pages > 1 else ''}, contenu non extractible", total_pages, "extraction_failed"


def extract_image_ocr(file_bytes: bytes, name: str):
    """Multi-attempt OCR on image files: standard -> enhanced -> high-res."""
    import io
    from PIL import Image

    try:
        img = Image.open(io.BytesIO(file_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Attempt 1: Standard OCR
        text, quality = ocr_page(img, 1, name, enhanced=False)
        if quality == "lisible":
            logger.info(f"Image '{name}': OCR standard reussi ({len(text)} chars)")
            return text, "Image — OCR standard", "ocr_extracted"

        # Attempt 2: Enhanced OCR (pre-processed)
        text2, quality2 = ocr_page(img, 1, name, enhanced=True)
        best_text = text2 if len(text2) > len(text) else text
        best_quality = quality2 if len(text2) > len(text) else quality

        if best_quality in ("lisible", "partiellement lisible") and len(best_text) > 10:
            method_label = "OCR renforce" if len(text2) > len(text) else "OCR standard"
            logger.info(f"Image '{name}': {method_label} ({len(best_text)} chars, {best_quality})")
            return best_text, f"Image — {method_label}", "ocr_extracted" if best_quality == "lisible" else "partially_readable"

        img.close()
        return "", "Image — OCR sans resultat exploitable", "ocr_empty"
    except Exception as e:
        logger.error(f"Image '{name}': OCR pipeline failed: {e}")
        return "", f"Image — erreur OCR: {str(e)[:50]}", "ocr_error"
