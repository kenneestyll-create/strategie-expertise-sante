/**
 * Extract text from files using backend API
 * Pipeline: PDF texte (pdfplumber) -> PDF scanne (OCR tesseract) -> Images (OCR)
 * Supports chunked upload for files > 20 MB
 */
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const CHUNK_THRESHOLD = 5 * 1024 * 1024; // 5 MB — lowered from 20 MB to ensure reliable uploads on slow connections
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
      timeout: 60000,
    });
    return res.data;
  } catch (err) {
    if (retries < MAX_RETRIES) {
      const delay = 1000 * Math.pow(2, retries);
      await new Promise(r => setTimeout(r, delay));
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
  let storedFiles = [];

  try {
    const res = await axios.post(`${API}/upload/extract`, {
      upload_id: uploadId,
      files: allFiles,
    }, { timeout: 300000 });

    // Capture stored files from response
    storedFiles = res.data.stored_files || [];

    // Check if server returned async mode for large files
    if (res.data.async && res.data.extraction_id) {
      const extractionId = res.data.extraction_id;
      // For async, stored_files may come with the initial response
      storedFiles = res.data.stored_files || [];
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('upload-progress', { detail: { percent: 95, phase: 'extracting-large', message: 'Extraction en cours — fichier volumineux, veuillez patienter...' } }));
      }
      // Poll for result
      let pollResult = null;
      for (let attempt = 0; attempt < 120; attempt++) {
        await new Promise(r => setTimeout(r, 2000));
        try {
          const pollRes = await axios.get(`${API}/upload/extract-status/${extractionId}`, { timeout: 15000 });
          if (pollRes.data.status === 'done') {
            pollResult = pollRes.data;
            break;
          } else if (pollRes.data.status === 'error') {
            console.warn('Async extraction error:', pollRes.data.error);
            break;
          }
        } catch (e) { /* poll retry */ }
      }
      if (pollResult) {
        combinedText = pollResult.extracted_text || '';
        details = pollResult.details || [];
        extractedCount = details.filter(d => d.has_text).length;
        if (pollResult.stored_files) storedFiles = pollResult.stored_files;
      } else {
        for (const f of allFiles) {
          combinedText += `\n--- ${f.name} ---\n[Extraction en cours — délai dépassé]\n`;
        }
      }
    } else {
      combinedText = res.data.extracted_text || '';
      details = res.data.details || [];
      extractedCount = details.filter(d => d.has_text).length;
    }
  } catch (err) {
    // Retry once on timeout/network errors
    if (err.code === 'ECONNABORTED' || err.message?.includes('timeout') || !err.response) {
      try {
        const res2 = await axios.post(`${API}/upload/extract`, {
          upload_id: uploadId,
          files: allFiles,
        }, { timeout: 300000 });
        combinedText = res2.data.extracted_text || '';
        details = res2.data.details || [];
        extractedCount = details.filter(d => d.has_text).length;
      } catch (retryErr) {
        console.warn('Chunked extraction retry failed:', retryErr.message);
        for (const f of allFiles) {
          combinedText += `\n--- ${f.name} ---\n[Extraction serveur indisponible]\n`;
        }
      }
    } else {
      console.warn('Chunked extraction failed:', err.message);
      for (const f of allFiles) {
        combinedText += `\n--- ${f.name} ---\n[Extraction serveur indisponible]\n`;
      }
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
    storedFiles,
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
  let storedFiles = [];

  if (filesToExtract.some(f => f.data)) {
    // Dispatch periodic progress events while waiting for server (Gemini Vision can take 60-90s per scanned PDF)
    let extractionTimerId = null;
    const startExtractionTimer = () => {
      const startTime = Date.now();
      const totalScannableFiles = filesToExtract.filter(f => f.data && (f.type === 'application/pdf' || f.name?.toLowerCase().endsWith('.pdf'))).length;
      extractionTimerId = setInterval(() => {
        if (typeof window === 'undefined') return;
        const elapsed = Math.round((Date.now() - startTime) / 1000);
        let msg;
        if (elapsed < 5) {
          msg = 'Préparation de l\'extraction…';
        } else if (totalScannableFiles > 1) {
          msg = `Lecture IA des PDFs en cours (~${Math.max(60, totalScannableFiles * 60)}s estimées) — ${elapsed}s écoulées`;
        } else {
          msg = `Lecture IA en cours (~60-90s pour PDFs scannés) — ${elapsed}s écoulées`;
        }
        window.dispatchEvent(new CustomEvent('upload-progress', { detail: { phase: 'extraction', message: msg, elapsed } }));
      }, 2000);
    };
    const stopExtractionTimer = () => {
      if (extractionTimerId) { clearInterval(extractionTimerId); extractionTimerId = null; }
    };

    try {
      const res = await axios.post(`${API}/extract-document-text`, { files: filesToExtract }, {
        timeout: 300000,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const pct = Math.round((progressEvent.loaded / progressEvent.total) * 100);
            if (typeof window !== 'undefined') {
              window.dispatchEvent(new CustomEvent('upload-progress', { detail: { percent: pct, phase: 'upload' } }));
            }
            if (pct >= 100 && !extractionTimerId) startExtractionTimer();
          }
        },
      });
      stopExtractionTimer();

      // Async mode: server returned a polling ID (heavy payload, multiple PDFs)
      if (res.data.async && res.data.extraction_id) {
        const extractionId = res.data.extraction_id;
        storedFiles = res.data.stored_files || [];
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('upload-progress', { detail: { phase: 'extraction', message: 'Extraction IA en parallèle — PDFs multiples détectés...' } }));
        }
        startExtractionTimer();
        let pollResult = null;
        for (let attempt = 0; attempt < 180; attempt++) {
          await new Promise(r => setTimeout(r, 2000));
          try {
            const pollRes = await axios.get(`${API}/upload/extract-status/${extractionId}`, { timeout: 15000 });
            if (pollRes.data.status === 'done') {
              pollResult = pollRes.data;
              break;
            } else if (pollRes.data.status === 'error') {
              console.warn('Async base64 extraction error:', pollRes.data.error);
              break;
            }
          } catch (e) { /* poll retry */ }
        }
        stopExtractionTimer();
        if (pollResult) {
          combinedText = pollResult.extracted_text || '';
          details = pollResult.details || [];
          if (pollResult.stored_files && pollResult.stored_files.length) storedFiles = pollResult.stored_files;
          extractedCount = details.filter(d => d.has_text).length;
        } else {
          for (const f of filesToExtract) {
            combinedText += `\n--- ${f.name} ---\n[Extraction en cours — délai dépassé]\n`;
          }
        }
      } else {
        combinedText = res.data.extracted_text || '';
        details = res.data.details || [];
        storedFiles = res.data.stored_files || [];
        extractedCount = details.filter(d => d.has_text).length;
      }
    } catch (err) {
      stopExtractionTimer();
      // Retry once on timeout/network error
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout') || !err.response) {
        try {
          const res2 = await axios.post(`${API}/extract-document-text`, { files: filesToExtract }, { timeout: 300000 });
          combinedText = res2.data.extracted_text || '';
          details = res2.data.details || [];
          storedFiles = res2.data.stored_files || [];
          extractedCount = details.filter(d => d.has_text).length;
        } catch (retryErr) {
          console.warn('Base64 extraction retry failed:', retryErr.message);
          for (const f of filesToExtract) {
            combinedText += `\n--- ${f.name} ---\n[Extraction serveur indisponible — veuillez réessayer]\n`;
          }
        }
      } else {
        console.warn('Server-side extraction failed:', err.message);
        for (const f of filesToExtract) {
          combinedText += `\n--- ${f.name} ---\n[Extraction serveur indisponible]\n`;
        }
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
    storedFiles,
    fileCount: files.length,
    extractedCount,
  };
}
