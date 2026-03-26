/**
 * Extract text from files using backend API (pdfplumber for PDFs)
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

    if (isPdf || isText) {
      try {
        const data = await fileToBase64(file);
        filesToExtract.push({ name: file.name, type: file.type || '', data });
      } catch {
        filesToExtract.push({ name: file.name, type: file.type || '', data: '' });
      }
    } else if (isImage) {
      // Images use OCR (already done by DocumentUploader)
      filesToExtract.push({ name: file.name, type: file.type || '', data: '' });
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
      // Fallback: just record file names
      for (const f of filesToExtract) {
        combinedText += `\n--- ${f.name} ---\n[Extraction serveur indisponible]\n`;
      }
    }
  } else {
    // No files with extractable data — just list them
    for (const f of filesToExtract) {
      combinedText += `\n--- ${f.name} (${f.type || 'inconnu'}) ---\n[Document joint]\n`;
    }
  }

  // Append OCR text for images if available
  if (existingOcrText && existingOcrText.trim()) {
    combinedText += `\n\n--- Contenu extrait par OCR (images) ---\n${existingOcrText.substring(0, 4000)}\n`;
    if (!extractedCount) extractedCount = 1;
  }

  return {
    combinedText: combinedText.trim(),
    results: details,
    fileCount: files.length,
    extractedCount
  };
}
