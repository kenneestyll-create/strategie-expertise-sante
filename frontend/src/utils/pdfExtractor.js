/**
 * Extract text from files using backend API
 * Pipeline: PDF texte (pdfplumber) -> PDF scanne (OCR tesseract) -> Images (OCR)
 * Supports chunked upload for files > 20 MB
 */
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const CHUNK_THRESHOLD = 20 * 1024 * 1024; // 20 MB
const CHUNK_SIZE = 2 * 1024 * 1024; // 2 MB
const MAX_RETRIES = 3;

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

/**
 * Upload a single chunk with retry logic.
 */
async function uploadChunk(uploadId, filename, chunkIndex, totalChunks, chunkBlob, retries = 0) {
  const formData = new FormData();
  formData.append('upload_id', uploadId);
  formData.append('filename', filename);
  formData.append('chunk_index', String(chunkIndex));
  formData.append('total_chunks', String(totalChunks));
  formData.append('chunk', chunkBlob, 'chunk');

  try {
    const res = await axios.post(`${API}/upload/chunk`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
    });
    return res.data;
  } catch (err) {
    if (retries < MAX_RETRIES) {
      await new Promise(r => setTimeout(r, 1000 * (retries + 1)));
      return uploadChunk(uploadId, filename, chunkIndex, totalChunks, chunkBlob, retries + 1);
    }
    throw err;
  }
}

/**
 * Upload a large file using chunked upload.
 * Returns metadata for the extract endpoint.
 */
async function chunkedUpload(file, uploadId, onProgress) {
  const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
  let uploaded = 0;

  for (let i = 0; i < totalChunks; i++) {
    const start = i * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, file.size);
    const blob = file.slice(start, end);

    await uploadChunk(uploadId, file.name, i, totalChunks, blob);
    uploaded++;
    if (onProgress) {
      onProgress(file.name, uploaded, totalChunks);
    }
  }

  return {
    name: file.name,
    type: file.type || '',
    chunked: true,
    total_chunks: totalChunks,
  };
}

/**
 * Extract text from files.
 * Files > CHUNK_THRESHOLD are uploaded in chunks, others use base64.
 * @param {File[]} files
 * @param {string} existingOcrText
 * @param {function} onProgress - (filename, uploadedChunks, totalChunks) callback
 */
export async function extractTextFromFiles(files, existingOcrText = '', onProgress = null) {
  const smallFiles = [];
  const largeFiles = [];

  for (const file of files) {
    if (!file || !file.name) continue;
    if (file.size > CHUNK_THRESHOLD) {
      largeFiles.push(file);
    } else {
      smallFiles.push(file);
    }
  }

  // If no large files, use existing base64 approach (faster for small files)
  if (largeFiles.length === 0) {
    return extractBase64(smallFiles, existingOcrText);
  }

  // Mixed approach: chunk large files + base64 small files
  const uploadId = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`;

  // Upload large files in chunks
  const chunkedMeta = [];
  for (const file of largeFiles) {
    try {
      const meta = await chunkedUpload(file, uploadId, onProgress);
      chunkedMeta.push(meta);
    } catch (err) {
      console.error(`Chunked upload failed for ${file.name}:`, err);
      chunkedMeta.push({ name: file.name, type: file.type || '', chunked: false, data: '' });
    }
  }

  // Convert small files to base64
  const base64Files = [];
  for (const file of smallFiles) {
    const isPdf = file.type === 'application/pdf' || file.name?.toLowerCase().endsWith('.pdf');
    const isText = file.type === 'text/plain' || file.name?.toLowerCase().endsWith('.txt');
    const isImage = file.type?.startsWith('image/');

    if (isPdf || isText || isImage) {
      try {
        const data = await fileToBase64(file);
        base64Files.push({ name: file.name, type: file.type || '', data, chunked: false });
      } catch {
        base64Files.push({ name: file.name, type: file.type || '', data: '', chunked: false });
      }
    } else {
      base64Files.push({ name: file.name, type: file.type || '', data: '', chunked: false });
    }
  }

  // Call the extract endpoint (handles both chunked and base64)
  const allFiles = [...chunkedMeta, ...base64Files];

  let combinedText = '';
  let extractedCount = 0;
  let details = [];

  try {
    const res = await axios.post(`${API}/upload/extract`, {
      upload_id: uploadId,
      files: allFiles,
    }, { timeout: 120000 });

    combinedText = res.data.extracted_text || '';
    details = res.data.details || [];
    extractedCount = details.filter(d => d.has_text).length;
  } catch (err) {
    console.warn('Chunked extraction failed:', err.message);
    for (const f of allFiles) {
      combinedText += `\n--- ${f.name} ---\n[Extraction serveur indisponible]\n`;
    }
  }

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
    extractedCount,
  };
}

/**
 * Original base64 approach for small files.
 */
async function extractBase64(files, existingOcrText = '') {
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
    extractedCount,
  };
}
