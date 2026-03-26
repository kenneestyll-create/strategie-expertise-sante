/**
 * Extract text from files using backend API
 * Pipeline: PDF texte (pdfplumber) → PDF scanné (OCR tesseract) → Images (OCR)
 */
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

async function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export async function extractTextFromFiles(files, existingOcrText = '') {
  const filesToExtract = [];

  for (const file of files) {
    if (!file || !file.name) continue;

    const isPdf = file.type === 'application/pdf' || file.name?.toLowerCase().endsWith('.pdf');
    const isText = file.type === 'text/plain' || file.name?.toLowerCase().endsWith('.txt');
    const isImage = file.type?.startsWith('image/');

    if (isPdf || isText || isImage) {
      try {
        const data = await fileToBase64(file);
        filesToExtract.push({ name: file.name, type: file.type || '', data });
      } catch {
        filesToExtract.push({ name: file.name, type: file.type || '', data: '' });
      }
    } else {
      filesToExtract.push({ name: file.name, type: file.type || '', data: '' });
    }
  }

  let combinedText = '';
  let extractedCount = 0;
  let details = [];

  if (filesToExtract.some(f => f.data)) {
    try {
      const res = await axios.post(`${API}/extract-document-text`, { files: filesToExtract });
      combinedText = res.data.extracted_text || '';
      details = res.data.details || [];
      extractedCount = details.filter(d => d.has_text).length;
    } catch (err) {
      console.warn('Server-side extraction failed:', err.message);
      for (const f of filesToExtract) {
        combinedText += `\n--- ${f.name} ---\n[Extraction serveur indisponible]\n`;
      }
    }
  } else {
    for (const f of filesToExtract) {
      combinedText += `\n--- ${f.name} (${f.type || 'inconnu'}) ---\n[Document joint]\n`;
    }
  }

  // Append frontend OCR text for images if available and not already processed
  if (existingOcrText && existingOcrText.trim()) {
    const hasImageOcr = details.some(d => d.status === 'ocr_extracted' && d.name?.match(/\.(jpg|jpeg|png|gif|webp|heic)$/i));
    if (!hasImageOcr) {
      combinedText += `\n\n--- Contenu extrait par OCR (images) ---\n${existingOcrText.substring(0, 4000)}\n`;
      if (!extractedCount) extractedCount = 1;
    }
  }

  return {
    combinedText: combinedText.trim(),
    results: details,
    fileCount: files.length,
    extractedCount
  };
}
