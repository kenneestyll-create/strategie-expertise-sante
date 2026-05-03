import { useState, useCallback, useRef } from 'react';
import { createWorker } from 'tesseract.js';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/**
 * Hook for OCR text extraction using Tesseract.js (Phase 1)
 * + GPT-4o AI-enhanced extraction (Phase 2)
 */
export const useOCR = () => {
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const workerRef = useRef(null);

  const extractText = useCallback(async (file) => {
    if (!file) return null;

    const isImage = file.type?.startsWith('image/');
    if (!isImage) {
      return { raw: '', fields: {}, source: 'skip', message: 'OCR disponible uniquement pour les images (JPG, PNG)' };
    }

    setProcessing(true);
    setProgress(0);
    setError(null);

    let objectUrl = null;
    try {
      const worker = await createWorker('fra', 1, {
        logger: (m) => {
          if (m.status === 'recognizing text') {
            setProgress(Math.round(m.progress * 100));
          }
        }
      });
      workerRef.current = worker;

      // Convertir File en blob URL pour éviter DataCloneError
      objectUrl = URL.createObjectURL(file);
      const { data: { text, confidence } } = await worker.recognize(objectUrl);
      await worker.terminate();
      workerRef.current = null;

      const fields = parseFields(text);

      setProcessing(false);
      setProgress(100);

      return {
        raw: text,
        fields,
        confidence: Math.round(confidence),
        source: 'tesseract',
      };
    } catch (err) {
      setError(err.message);
      setProcessing(false);
      if (workerRef.current) {
        try { await workerRef.current.terminate(); } catch {}
        workerRef.current = null;
      }
      return null;
    } finally {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    }
  }, []);

  const extractFromMultiple = useCallback(async (files) => {
    const imageFiles = files.filter(f => f.type?.startsWith('image/'));
    if (imageFiles.length === 0) return { raw: '', fields: {}, source: 'skip' };

    setProcessing(true);
    setProgress(0);
    setError(null);

    const objectUrls = [];
    try {
      const worker = await createWorker('fra', 1, {
        logger: (m) => {
          if (m.status === 'recognizing text') {
            setProgress(Math.round(m.progress * 100));
          }
        }
      });
      workerRef.current = worker;

      let allText = '';
      for (let i = 0; i < imageFiles.length; i++) {
        // Convertir File en blob URL pour éviter DataCloneError
        const url = URL.createObjectURL(imageFiles[i]);
        objectUrls.push(url);
        const { data: { text } } = await worker.recognize(url);
        allText += `\n--- ${imageFiles[i].name} ---\n${text}\n`;
        setProgress(Math.round(((i + 1) / imageFiles.length) * 100));
      }

      await worker.terminate();
      workerRef.current = null;

      const fields = parseFields(allText);
      setProcessing(false);
      return { raw: allText, fields, source: 'tesseract' };
    } catch (err) {
      setError(err.message);
      setProcessing(false);
      if (workerRef.current) {
        try { await workerRef.current.terminate(); } catch {}
        workerRef.current = null;
      }
      return null;
    } finally {
      objectUrls.forEach(u => URL.revokeObjectURL(u));
    }
  }, []);

  const cancel = useCallback(async () => {
    if (workerRef.current) {
      try { await workerRef.current.terminate(); } catch {}
      workerRef.current = null;
    }
    setProcessing(false);
    setProgress(0);
  }, []);

  const enhanceWithAI = useCallback(async (rawText) => {
    if (!rawText || rawText.trim().length < 10) return null;
    try {
      const res = await axios.post(`${API}/documents/extract-fields-ai`, { text: rawText });
      if (res.data?.enhanced && res.data?.fields) {
        return { fields: res.data.fields, source: 'gpt-4o', enhanced: true };
      }
      return null;
    } catch {
      return null;
    }
  }, []);

  return { extractText, extractFromMultiple, enhanceWithAI, cancel, processing, progress, error };
};

// ==================== FIELD EXTRACTION (Regex-based, Phase 1) ====================

const MONTHS_FR = {
  'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
  'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
  'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
};

function parseFields(text) {
  if (!text) return {};
  const fields = {};
  const t = text.replace(/\r\n/g, '\n');

  // Dates (dd/mm/yyyy or dd-mm-yyyy or "12 janvier 2024")
  const datePatterns = [
    /(\d{2})[\/\-.](\d{2})[\/\-.](\d{4})/g,
    new RegExp(`(\\d{1,2})\\s+(${Object.keys(MONTHS_FR).join('|')})\\s+(\\d{4})`, 'gi'),
  ];

  const dates = new Set();
  for (const pat of datePatterns) {
    let m;
    while ((m = pat.exec(t)) !== null) {
      if (m[0].includes('/') || m[0].includes('-') || m[0].includes('.')) {
        dates.add(m[0]);
      } else {
        const month = MONTHS_FR[m[2].toLowerCase()];
        if (month) dates.add(`${m[1].padStart(2, '0')}/${month}/${m[3]}`);
      }
    }
  }
  if (dates.size > 0) fields.dates = [...dates];

  // Amounts (Euro)
  const amountPattern = /(\d[\d\s\.]*[\d][,]\d{2})\s*(?:€|EUR|euros?)/gi;
  const amounts = new Set();
  let am;
  while ((am = amountPattern.exec(t)) !== null) {
    amounts.add(am[1].replace(/\s/g, '') + '€');
  }
  // Also catch simple amounts like "97€"
  const simpleAmount = /(?<!\d)(\d{2,6})\s*€/g;
  while ((am = simpleAmount.exec(t)) !== null) {
    amounts.add(am[1] + '€');
  }
  if (amounts.size > 0) fields.montants = [...amounts];

  // Références / Dossier numbers
  const refPatterns = [
    /(?:N°|n°|Réf|réf|référence|dossier)\s*[:\s]?\s*([A-Z0-9][A-Z0-9\-\/]{3,20})/gi,
    /(?:CPAM|CRAMIF|MSA)\s*[:\s]?\s*([A-Z0-9\-\/]{4,20})/gi,
  ];
  const refs = new Set();
  for (const pat of refPatterns) {
    let rm;
    while ((rm = pat.exec(t)) !== null) {
      refs.add(rm[1].trim());
    }
  }
  if (refs.size > 0) fields.référénces = [...refs];

  // Social Security Number (N° SS: 1 XX XX XX XXX XXX XX)
  const ssPattern = /[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}/g;
  const ss = t.match(ssPattern);
  if (ss) fields.numero_ss = ss[0].replace(/\s/g, '');

  // Names (after "Nom :", "Patient :", "Assuré :")
  const namePatterns = [
    /(?:Nom|Patient|Assuré|Bénéficiaire|Demandeur)\s*[:\s]\s*([A-ZÀ-Ü][a-zà-ü]+(?:\s+[A-ZÀ-Ü][a-zà-ü]+){0,3})/g,
    /(?:M\.|Mme|Mr|Madame|Monsieur)\s+([A-ZÀ-Ü][a-zà-ü]+(?:\s+[A-ZÀ-Ü][a-zà-ü]+){0,3})/g,
  ];
  const names = new Set();
  for (const pat of namePatterns) {
    let nm;
    while ((nm = pat.exec(t)) !== null) {
      const name = nm[1].trim();
      if (name.length > 2 && name.length < 60) names.add(name);
    }
  }
  if (names.size > 0) fields.noms = [...names];

  // IPP / Taux
  const ippPattern = /(?:taux|IPP|incapacité)\s*[:\s]?\s*(\d{1,3})\s*%/gi;
  const ipps = [];
  let ip;
  while ((ip = ippPattern.exec(t)) !== null) {
    ipps.push(parseInt(ip[1]));
  }
  if (ipps.length > 0) fields.taux_ipp = ipps;

  // Document type detection
  const typeKeywords = {
    'accident du travail': 'at',
    'accident de travail': 'at',
    'maladie professionnelle': 'mp',
    'tableau des maladies': 'mp',
    'MDPH': 'mdph',
    'AAH': 'mdph',
    'handicap': 'mdph',
    'expertise médicale': 'expertise',
    'expertise': 'expertise',
    'IPP': 'ipp',
    'incapacité permanente': 'ipp',
    'CPAM': 'at',
    'CRAMIF': 'at',
  };
  const detectedTypes = new Set();
  for (const [keyword, type] of Object.entries(typeKeywords)) {
    if (t.toLowerCase().includes(keyword.toLowerCase())) {
      detectedTypes.add(type);
    }
  }
  if (detectedTypes.size > 0) fields.type_dossier_detected = [...detectedTypes];

  // Extract key phrases/context
  const lines = t.split('\n').filter(l => l.trim().length > 10);
  if (lines.length > 0) {
    fields.contexte = lines.slice(0, 5).join(' ').substring(0, 500);
  }

  return fields;
}
