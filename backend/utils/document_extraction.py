"""
CONSOLIDATION_ARCHITECTURE — Extraction documentaire centralisee.
Fournit les fonctions d'extraction texte (PDF, images, OCR).
Consommateurs : routes/dossier_express.py
"""
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


def extract_pdf_full_pipeline(file_bytes: bytes, name: str):
    """4-level cascade PDF extraction with page-by-page evaluation."""
    import io
    from PIL import Image

    total_pages = 0

    # === TENTATIVE 1: Extraction texte native (pdfplumber) ===
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
            logger.info(f"PDF '{name}': extraction texte partielle ({readable}/{total_pages}), tentative OCR pour le reste")
    except Exception as e:
        logger.warning(f"PDF '{name}': pdfplumber failed: {e}")

    # === TENTATIVE 2: OCR standard (pypdfium2 + tesseract) ===
    try:
        import pypdfium2
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
            method = f"PDF scanne — {total_pages} page{'s' if total_pages > 1 else ''}, OCR standard ({readable_ocr}/{pages_to_ocr} pages lisibles)"
            logger.info(f"PDF '{name}': OCR standard reussi ({len(extracted)} chars, {readable_ocr}/{pages_to_ocr} pages)")
            pdf_doc.close()
            return extracted, method, total_pages, "ocr_extracted"

        # === TENTATIVE 3: OCR apres pre-traitement renforce ===
        logger.info(f"PDF '{name}': OCR standard faible ({readable_ocr}/{pages_to_ocr}), tentative avec pre-traitement renforce")

        enhanced_pages = []
        enhanced_quality = []

        for i in range(pages_to_ocr):
            page = pdf_doc[i]
            bitmap = page.render(scale=3)
            pil_image = bitmap.to_pil()
            text, quality = ocr_page(pil_image, i + 1, name, enhanced=True)
            if text:
                enhanced_pages.append(f"[Page {i+1}] {text}")
            enhanced_quality.append(quality)
            pil_image.close()

        readable_enhanced = sum(1 for q in enhanced_quality if q == "lisible")

        if enhanced_pages:
            if len("\n".join(enhanced_pages)) > len("\n".join(ocr_pages)):
                final_pages = enhanced_pages
                final_readable = readable_enhanced
                ocr_type = "OCR renforce"
            else:
                final_pages = ocr_pages if ocr_pages else enhanced_pages
                final_readable = max(readable_ocr, readable_enhanced)
                ocr_type = "OCR standard" if ocr_pages else "OCR renforce"

            extracted = "\n\n".join(final_pages)
            partially = sum(1 for q in (enhanced_quality if final_pages == enhanced_pages else ocr_quality) if q == "partiellement lisible")
            method = f"PDF scanne — {total_pages} page{'s' if total_pages > 1 else ''}, {ocr_type} ({final_readable} lisibles, {partially} partielles)"
            status = "ocr_extracted" if final_readable > 0 else "partially_readable"
            logger.info(f"PDF '{name}': {ocr_type} ({len(extracted)} chars, {final_readable} lisibles, {partially} partielles)")
            pdf_doc.close()
            return extracted, method, total_pages, status

        pdf_doc.close()

        # === TENTATIVE 4: Fallback pdf2image + tesseract ===
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(file_bytes, dpi=300, first_page=1, last_page=min(total_pages, 10))
            fallback_pages = []
            for i, img in enumerate(images):
                text, quality = ocr_page(img, i + 1, name, enhanced=True)
                if text:
                    fallback_pages.append(f"[Page {i+1}] {text}")
                img.close()

            if fallback_pages:
                extracted = "\n\n".join(fallback_pages)
                method = f"PDF scanne — {total_pages} page{'s' if total_pages > 1 else ''}, OCR fallback ({len(fallback_pages)} pages recuperees)"
                logger.info(f"PDF '{name}': OCR fallback reussi ({len(extracted)} chars)")
                return extracted, method, total_pages, "ocr_extracted"
        except Exception as e:
            logger.warning(f"PDF '{name}': pdf2image fallback failed: {e}")

        method = f"PDF scanne — {total_pages} page{'s' if total_pages > 1 else ''}, OCR sans resultat exploitable"
        logger.warning(f"PDF '{name}': all OCR attempts returned no text")
        return "", method, total_pages, "ocr_empty"

    except Exception as e:
        logger.error(f"PDF '{name}': OCR pipeline failed: {e}")

    method = f"PDF — {total_pages} page{'s' if total_pages > 1 else ''}, contenu non extractible"
    return "", method, total_pages, "extraction_failed"


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
