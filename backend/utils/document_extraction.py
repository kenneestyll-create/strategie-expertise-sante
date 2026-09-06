"""
CONSOLIDATION_ARCHITECTURE — Extraction documentaire centralisee.
Fournit les fonctions d'extraction texte (PDF, images, OCR).
Consommateurs : routes/dossier_express.py
"""
import os
import asyncio
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


GEMINI_CALL_TIMEOUT_S = 150  # hard cap per Gemini call — a hung HTTP call must not freeze the pipeline


async def extract_pdf_with_gemini(file_bytes: bytes, name: str, progress_cb=None) -> tuple[str, str, int, str]:
    """Cloud-based PDF extraction via Gemini 2.5 Pro (native PDF support).

    Robust against missing system binaries (no Tesseract/Poppler dependency).
    Auto-chunks heavy PDFs (>3MB or >6 pages) into smaller batches to avoid 502 errors.

    Returns: (extracted_text, method_label, page_count, status)
    """
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
    except ImportError as e:
        logger.error(f"PDF '{name}': emergentintegrations IMPORT FAILED: type={type(e).__name__} msg={e}", exc_info=True)
        return "", f"Gemini Vision lib manquante: {type(e).__name__}: {str(e)[:80]}", 0, "extraction_failed"

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
    return await _gemini_extract_chunked(file_bytes, name, total_pages, api_key, chunk_size=4, progress_cb=progress_cb)


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
        response = await asyncio.wait_for(
            chat.send_message(UserMessage(text=prompt, file_contents=[pdf_file])),
            timeout=GEMINI_CALL_TIMEOUT_S,
        )

        if response and len(response.strip()) > 50:
            method = f"PDF — {total_pages} page{'s' if total_pages > 1 else ''}, extraction Gemini Vision"
            logger.info(f"PDF '{name}': Gemini Vision OK ({len(response)} chars, {total_pages} pages)")
            return response.strip(), method, total_pages, "vision_extracted"

        logger.warning(f"PDF '{name}': Gemini returned empty/too short response (len={len(response) if response else 0})")
        return "", f"PDF — {total_pages} page{'s' if total_pages > 1 else ''}, Gemini reponse vide", total_pages, "vision_empty"
    except Exception as e:
        err_type = type(e).__name__
        logger.error(f"PDF '{name}': Gemini Vision (single) FAILED: type={err_type} msg={e}", exc_info=True)
        return "", f"Gemini Vision erreur ({err_type}): {str(e)[:100]}", total_pages, "vision_error"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


def _pdf_page_count_sync(file_bytes: bytes) -> int:
    import io as _io
    from pypdf import PdfReader
    return len(PdfReader(_io.BytesIO(file_bytes)).pages)


def _build_sub_pdf_sync(file_bytes: bytes, start: int, end: int) -> bytes:
    """CPU-bound sub-PDF build — must run off the event loop (asyncio.to_thread)."""
    import io as _io
    from pypdf import PdfReader, PdfWriter
    src = PdfReader(_io.BytesIO(file_bytes))
    writer = PdfWriter()
    for p in range(start, end):
        writer.add_page(src.pages[p])
    buf = _io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


async def _gemini_extract_chunked(file_bytes: bytes, name: str, total_pages: int, api_key: str, chunk_size: int = 4, progress_cb=None) -> tuple[str, str, int, str]:
    """Split heavy PDF into chunks of N pages and call Gemini for each chunk."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType

    src_pages = await asyncio.to_thread(_pdf_page_count_sync, file_bytes)
    if total_pages == 0:
        total_pages = src_pages

    chunks_text: list[str] = []
    failures = 0
    last_error: str = ""
    chunks_total = (src_pages + chunk_size - 1) // chunk_size

    for chunk_start in range(0, src_pages, chunk_size):
        chunk_end = min(chunk_start + chunk_size, src_pages)
        chunk_num = chunk_start // chunk_size + 1
        if progress_cb:
            try:
                await progress_cb(f"Extraction OCR — {name[:40]} : lot {chunk_num}/{chunks_total} (pages {chunk_start + 1}-{chunk_end})...")
            except Exception:
                pass
        sub_bytes = await asyncio.to_thread(_build_sub_pdf_sync, file_bytes, chunk_start, chunk_end)

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
                resp_len = len(response) if response else 0
                last_error = f"reponse vide (len={resp_len})"
                logger.warning(f"PDF '{name}': chunk {chunk_start+1}-{chunk_end} empty (len={resp_len})")
        except Exception as e:
            failures += 1
            err_type = type(e).__name__
            last_error = f"{err_type}: {str(e)[:120]}"
            logger.error(f"PDF '{name}': chunk {chunk_start+1}-{chunk_end} FAILED: type={err_type} msg={e}", exc_info=True)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            # Release sub-PDF buffer after each chunk (512MB tier: every freed MB matters)
            try:
                del sub_bytes
            except Exception:
                pass
            import gc
            gc.collect()

    if not chunks_text:
        err_suffix = f" — derniere erreur: {last_error}" if last_error else ""
        return "", f"PDF — {total_pages} pages, Gemini Vision chunked echoue{err_suffix}", total_pages, "vision_error"

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


def _pdfplumber_pass_sync(file_bytes: bytes, name: str):
    """Sync Level-1 native text pass — CPU-bound, run via asyncio.to_thread."""
    import io
    import pdfplumber
    pdf = pdfplumber.open(io.BytesIO(file_bytes))
    total_pages = len(pdf.pages)
    pages_text = []
    readable = 0
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and text.strip() and len(text.strip()) > 20:
            pages_text.append(f"[Page {i+1}] {text.strip()}")
            readable += 1
    pdf.close()

    if readable >= total_pages * 0.6:
        extracted = "\n\n".join(pages_text)
        method = f"PDF texte — {total_pages} page{'s' if total_pages > 1 else ''}, extraction directe ({readable}/{total_pages} pages lisibles)"
        return (extracted, method, total_pages, "text_extracted"), total_pages, readable
    return None, total_pages, readable


async def extract_pdf_full_pipeline(file_bytes: bytes, name: str, progress_cb=None):
    """Production-grade PDF extraction with cloud Vision fallback.

    Architecture (no system binary dependency required):
      Level 1: pdfplumber (Python pur, gratuit, instantané) — pour PDFs avec texte natif
      Level 2: Gemini Vision (cloud, ~0.05€/PDF, robuste) — pour PDFs scannés
      Level 3: Tesseract OCR (legacy, optionnel) — fallback de dernier recours si Gemini indisponible

    Tout le travail CPU-bound (pdfplumber, pypdf, Tesseract) est déporté hors de
    l'event loop (asyncio.to_thread) : un pod à CPU limité reste responsive
    (health probes OK → pas de kill Kubernetes pendant l'extraction).
    """
    total_pages = 0

    # === LEVEL 1: Native text extraction (pdfplumber, off-loop) ===
    try:
        result, total_pages, readable = await asyncio.to_thread(_pdfplumber_pass_sync, file_bytes, name)
        if result:
            extracted = result[0]
            logger.info(f"PDF '{name}': extraction texte reussie ({len(extracted)} chars, {readable}/{total_pages} pages)")
            return result
        elif readable > 0:
            logger.info(f"PDF '{name}': pdfplumber partiel ({readable}/{total_pages}), bascule sur Gemini Vision")
        else:
            logger.info(f"PDF '{name}': pdfplumber 0 pages lisibles, bascule sur Gemini Vision")
    except Exception as e:
        logger.warning(f"PDF '{name}': pdfplumber failed: {e}")

    # === LEVEL 2: Gemini Vision (cloud, robust to missing binaries) ===
    text, method, pages, status = await extract_pdf_with_gemini(file_bytes, name, progress_cb=progress_cb)
    if status == "vision_extracted" and text:
        return text, method, pages or total_pages, status

    logger.warning(f"PDF '{name}': Gemini Vision a echoue (status={status}), tentative Tesseract local")

    # === LEVEL 3: Tesseract OCR fallback (off-loop, only if Gemini fails AND Tesseract installed) ===
    try:
        result = await asyncio.to_thread(_tesseract_pass_sync, file_bytes, name, total_pages)
        if result:
            return result
    except Exception as e:
        logger.error(f"PDF '{name}': Tesseract fallback failed: {e}")

    return "", f"PDF — {total_pages} page{'s' if total_pages > 1 else ''}, contenu non extractible", total_pages, "extraction_failed"


def _tesseract_pass_sync(file_bytes: bytes, name: str, total_pages: int):
    """Sync Level-3 Tesseract fallback — returns result tuple or None."""
    import io
    try:
        import pypdfium2
        import pytesseract
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
            # DPI 150 (scale=1.5) instead of 200 (scale=2) → 50% less RAM per bitmap
            # Gemini OCR validated at 150 DPI in research; Tesseract too with lang='fra+eng'
            bitmap = page.render(scale=1.5)
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

        # Enhanced OCR last attempt (DPI 200 scale=2 — was 300/scale=3, halved for 512MB tier)
        enhanced_pages = []
        for i in range(pages_to_ocr):
            page = pdf_doc[i]
            bitmap = page.render(scale=2)
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
    return None


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
