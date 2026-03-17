import { useState, useRef, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import {
  Camera, X, RotateCcw, Check, Smartphone, Sun,
  Eye, Maximize2, ZapOff, Loader2, Plus,
  FileText, ChevronLeft, ChevronRight, Layers,
  Crop, Contrast, ScanLine, AlertCircle,
  RotateCw, SunMedium, ImageUp
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import {
  initScanWorker, isScanReady, isScanFailed,
  scanDocument, applyFilter as workerFilter, rotateImage as workerRotate,
  cropImage as workerCrop, adjustImage as workerAdjust,
  terminateScanWorker
} from '@/utils/opencvLoader';

/* ── Fallback grayscale (aucune dépendance worker) ── */
function fallbackGrayscale(canvas) {
  if (!canvas || !canvas.width || !canvas.height) {
    console.warn('[Fallback] Canvas non prêt, skip');
    return canvas ? canvas.toDataURL('image/jpeg', 0.92) : '';
  }
  const ctx = canvas.getContext('2d');
  const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const d = img.data;
  for (let i = 0; i < d.length; i += 4) {
    const gray = d[i] * 0.299 + d[i + 1] * 0.587 + d[i + 2] * 0.114;
    const enhanced = Math.min(255, Math.max(0, (gray - 128) * 1.3 + 128 + 10));
    d[i] = d[i + 1] = d[i + 2] = enhanced;
  }
  ctx.putImageData(img, 0, 0);
  return canvas.toDataURL('image/jpeg', 0.92);
}

function lightEnhance(canvas) {
  if (!canvas || !canvas.width || !canvas.height) {
    console.warn('[lightEnhance] Canvas non prêt, skip');
    return canvas ? canvas.toDataURL('image/jpeg', 0.92) : '';
  }
  const ctx = canvas.getContext('2d');
  const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const d = img.data;
  for (let i = 0; i < d.length; i += 4) {
    d[i]     = Math.min(255, Math.max(0, (d[i]     - 128) * 1.3 + 128 + 12));
    d[i + 1] = Math.min(255, Math.max(0, (d[i + 1] - 128) * 1.3 + 128 + 12));
    d[i + 2] = Math.min(255, Math.max(0, (d[i + 2] - 128) * 1.3 + 128 + 12));
  }
  ctx.putImageData(img, 0, 0);
  return canvas.toDataURL('image/jpeg', 0.92);
}

function imageDataToUrl(imgData) {
  const c = document.createElement('canvas');
  c.width = imgData.width; c.height = imgData.height;
  c.getContext('2d').putImageData(imgData, 0, 0);
  return c.toDataURL('image/jpeg', 0.92);
}

async function buildPdf(pages) {
  const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  for (let i = 0; i < pages.length; i++) {
    if (i > 0) pdf.addPage();
    const img = new Image();
    img.src = pages[i];
    await new Promise(r => { img.onload = r; img.onerror = r; });
    if (!img.width) continue;
    const ratio = Math.min(210 / img.width, 297 / img.height);
    pdf.addImage(pages[i], 'JPEG', (210 - img.width * ratio) / 2, (297 - img.height * ratio) / 2, img.width * ratio, img.height * ratio);
  }
  return pdf;
}

const FILTERS = [
  { id: 'bw', label: 'Noir & Blanc', icon: Contrast },
  { id: 'document', label: 'Contraste+', icon: Eye },
  { id: 'original', label: 'Original', icon: FileText },
];

/* ── Small helper components ── */
const PageStrip = ({ pages, activeIndex, onSelect, onRemove }) => (
  <div className="flex gap-2 px-3 py-2 bg-black/70 overflow-x-auto flex-shrink-0" data-testid="page-strip">
    {pages.map((url, i) => (
      <div key={i} onClick={() => onSelect(i)} className={`relative flex-shrink-0 w-14 h-18 rounded-lg overflow-hidden border-2 cursor-pointer ${i === activeIndex ? 'border-accent' : 'border-white/20'}`}>
        <img src={url} alt={`P${i + 1}`} className="w-full h-full object-cover" />
        <div className="absolute top-0 left-0 bg-black/60 text-white text-[9px] px-1 rounded-br">{i + 1}</div>
        {onRemove && <button onClick={(e) => { e.stopPropagation(); onRemove(i); }} className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-red-500 text-white rounded-full text-[10px] flex items-center justify-center">×</button>}
      </div>
    ))}
  </div>
);

const CornerAdjuster = ({ corners, setCorners, imageRef }) => {
  const handleDrag = (index, startEvent) => {
    startEvent.preventDefault();
    const rect = imageRef.current?.getBoundingClientRect();
    if (!rect) return;
    const move = (e) => {
      const pt = e.touches ? e.touches[0] : e;
      setCorners(prev => prev.map((c, i) => i !== index ? c : { x: Math.max(0, Math.min(1, (pt.clientX - rect.left) / rect.width)), y: Math.max(0, Math.min(1, (pt.clientY - rect.top) / rect.height)) }));
    };
    const up = () => { document.removeEventListener('mousemove', move); document.removeEventListener('touchmove', move); document.removeEventListener('mouseup', up); document.removeEventListener('touchend', up); };
    document.addEventListener('mousemove', move); document.addEventListener('touchmove', move); document.addEventListener('mouseup', up); document.addEventListener('touchend', up);
  };
  const labels = ['HG', 'HD', 'BD', 'BG'];
  return (
    <div className="absolute inset-0" data-testid="corner-adjuster">
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 1 1" preserveAspectRatio="none">
        <polygon points={corners.map(c => `${c.x},${c.y}`).join(' ')} fill="rgba(16,185,129,0.15)" stroke="rgba(16,185,129,0.8)" strokeWidth="0.003" />
      </svg>
      {corners.map((c, i) => (
        <div key={i} className="absolute w-9 h-9 cursor-grab active:cursor-grabbing" style={{ left: `${c.x * 100}%`, top: `${c.y * 100}%`, transform: 'translate(-50%,-50%)' }}
          onMouseDown={(e) => handleDrag(i, e)} onTouchStart={(e) => handleDrag(i, e)} aria-label={`Coin ${labels[i]}`} role="slider">
          <div className="w-full h-full rounded-full bg-emerald-500 border-2 border-white shadow-lg flex items-center justify-center">
            <span className="text-white text-[8px] font-bold">{labels[i]}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

/* ══════════════════════ MAIN SCANNER ══════════════════════ */
export const DocumentScanner = ({ onCapture, onClose }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const previewCanvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const streamRef = useRef(null);
  const adjustImgRef = useRef(null);

  const [phase, setPhase] = useState('guide');
  const [pages, setPages] = useState([]);
  const [rawDataUrl, setRawDataUrl] = useState(null);
  const [processedUrl, setProcessedUrl] = useState(null);
  const [autoDetected, setAutoDetected] = useState(false);
  const [manualCorners, setManualCorners] = useState(null);
  const [showManualMode, setShowManualMode] = useState(false);
  const [filter, setFilter] = useState('document');
  const [activePageIndex, setActivePageIndex] = useState(0);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [facingMode, setFacingMode] = useState('environment');
  const [error, setError] = useState('');
  const [workerReady, setWorkerReady] = useState(false);
  const [workerLoading, setWorkerLoading] = useState(false);
  const [workerFailed, setWorkerFailed] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [showAdjust, setShowAdjust] = useState(false);
  const [brightness, setBrightness] = useState(0);
  const [contrast, setContrast] = useState(0);
  const [stepLog, setStepLog] = useState('');
  const [simpleMode, setSimpleMode] = useState(false);
  const [imageReady, setImageReady] = useState(false); // ← NOUVEAU: image chargée et prête

  /* ── Init worker ── */
  useEffect(() => {
    if (workerReady || workerFailed) return;
    setWorkerLoading(true);
    const t0 = performance.now();
    initScanWorker().then((ok) => {
      setWorkerReady(ok);
      setWorkerFailed(!ok);
      setWorkerLoading(false);
      console.log(ok ? `[Scanner] Worker prêt (${Math.round(performance.now() - t0)}ms)` : '[Scanner] Fallback mode simple');
    });
  }, [workerReady, workerFailed]);

  /* ── Cleanup on unmount only ── */
  useEffect(() => {
    return () => terminateScanWorker();
  }, []);

  /* ── Draw processedUrl onto preview canvas ── */
  useEffect(() => {
    if (!processedUrl || !previewCanvasRef.current || showManualMode) return;
    const img = new Image();
    img.onload = () => {
      const c = previewCanvasRef.current;
      if (!c) return;
      c.width = img.width;
      c.height = img.height;
      c.getContext('2d').drawImage(img, 0, 0);
    };
    img.onerror = () => console.warn('[Preview] Erreur chargement image preview');
    img.src = processedUrl;
  }, [processedUrl, showManualMode]);

  /* ── Stop camera helper ── */
  const stopCamera = useCallback(() => {
    if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }
  }, []);

  /* ══════════════════════ HANDLE FILE INPUT ══════════════════════ */
  const handleFileInput = useCallback(async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = '';
    stopCamera();
    setImageReady(false);
    setProcessing(true);
    setError('');

    const img = new Image();
    img.onload = async () => {
      console.log('[Scanner] Image chargée:', img.width, 'x', img.height);

      // Guard canvas width=0
      if (!img.width || !img.height) {
        console.warn('[Scanner] Image non prête — dimensions 0');
        setError("L'image n'a pas pu être chargée correctement.");
        setProcessing(false);
        return;
      }

      const canvas = canvasRef.current;
      if (!canvas) { setProcessing(false); return; }
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      setRawDataUrl(canvas.toDataURL('image/jpeg', 0.95));

      if (simpleMode || !isScanReady()) {
        console.log('[Scanner] Mode simple — fichier');
        setStepLog('Image chargée (mode simple)');
        setProcessedUrl(lightEnhance(canvas));
        setAutoDetected(false); setManualCorners(null);
        setImageReady(true);
        setPhase('preview');
        setProcessing(false);
        return;
      }

      setPhase('processing');
      setStepLog('Analyse de l\'image...');
      try {
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const t0 = performance.now();
        const result = await scanDocument(imageData, filter);
        const elapsed = Math.round(performance.now() - t0);
        setProcessedUrl(imageDataToUrl(result.imageData));
        setAutoDetected(result.autoDetected);
        if (result.corners) {
          setManualCorners(result.corners.map(c => ({ x: c.x / result.originalWidth, y: c.y / result.originalHeight })));
        } else {
          setManualCorners([{ x: 0.05, y: 0.05 }, { x: 0.95, y: 0.05 }, { x: 0.95, y: 0.95 }, { x: 0.05, y: 0.95 }]);
        }
        setStepLog(result.autoDetected ? `Document détecté (${elapsed}ms)` : `Traité (${elapsed}ms)`);
        setImageReady(true);
        setPhase('preview');
      } catch (err) {
        console.warn('[Scanner] Scan failed, fallback grayscale:', err.message);
        setProcessedUrl(fallbackGrayscale(canvas));
        setAutoDetected(false);
        setStepLog('Fallback: amélioration simple');
        setImageReady(true);
        setPhase('preview');
      }
      setProcessing(false);
    };
    img.onerror = () => {
      setError("Impossible de lire cette image.");
      setProcessing(false);
    };
    img.src = URL.createObjectURL(file);
  }, [filter, simpleMode, stopCamera]);

  /* ══════════════════════ CAMERA ══════════════════════ */
  const startCamera = useCallback(async () => {
    setError(''); setStepLog(''); setBrightness(0); setContrast(0); setShowAdjust(false); setShowManualMode(false);
    setImageReady(false);
    setPhase('camera');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode, width: { ideal: 1920 }, height: { ideal: 1080 } }, audio: false });
      streamRef.current = stream;
    } catch (err) {
      if (err.name === 'NotAllowedError') setError("Autorisez l'accès caméra. Vous pouvez choisir une photo depuis la galerie.");
      else if (err.name === 'NotFoundError') setError('Aucune caméra détectée. Utilisez la galerie.');
      else setError(`Erreur caméra : ${err.message}`);
    }
  }, [facingMode]);

  useEffect(() => {
    if (phase === 'camera' && streamRef.current && videoRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch(() => {});
    }
  }, [phase]);

  useEffect(() => () => { stopCamera(); if (pdfUrl) URL.revokeObjectURL(pdfUrl); }, [stopCamera, pdfUrl]);

  const switchCamera = useCallback(() => { stopCamera(); setFacingMode(p => p === 'environment' ? 'user' : 'environment'); }, [stopCamera]);

  useEffect(() => { if (phase === 'camera' && !streamRef.current) startCamera(); }, [facingMode, phase, startCamera]);

  /* ══════════════════════ CAPTURE (caméra) ══════════════════════ */
  const capture = useCallback(async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    // 🔴 Guard: attendre que la vidéo ait des frames
    if (!video.videoWidth || !video.videoHeight) {
      console.warn('[Scanner] Image non prête — video dimensions 0');
      setError("Patientez, la caméra n'est pas encore prête.");
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    setRawDataUrl(canvas.toDataURL('image/jpeg', 0.95));
    stopCamera();
    setImageReady(false);

    if (simpleMode || !isScanReady()) {
      console.log('[Scanner] Mode simple — capture directe');
      setStepLog('Capture directe (mode simple)');
      setProcessedUrl(lightEnhance(canvas));
      setAutoDetected(false); setManualCorners(null);
      setImageReady(true);
      setPhase('preview');
      return;
    }

    setPhase('processing');
    setProcessing(true);
    setStepLog('Détection des contours...');
    try {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const t0 = performance.now();
      const result = await scanDocument(imageData, filter);
      const elapsed = Math.round(performance.now() - t0);
      setProcessedUrl(imageDataToUrl(result.imageData));
      setAutoDetected(result.autoDetected);
      if (result.corners) {
        setManualCorners(result.corners.map(c => ({ x: c.x / result.originalWidth, y: c.y / result.originalHeight })));
      } else {
        setManualCorners([{ x: 0.05, y: 0.05 }, { x: 0.95, y: 0.05 }, { x: 0.95, y: 0.95 }, { x: 0.05, y: 0.95 }]);
      }
      setStepLog(result.autoDetected ? `Document détecté (${elapsed}ms)` : `Traité (${elapsed}ms)`);
      setImageReady(true);
      setPhase('preview');
    } catch (e) {
      console.warn('[Scanner] Scan failed, fallback:', e.message);
      setProcessedUrl(fallbackGrayscale(canvas));
      setAutoDetected(false);
      setStepLog('Fallback: amélioration simple');
      setImageReady(true);
      setPhase('preview');
    }
    setProcessing(false);
  }, [stopCamera, filter, simpleMode]);

  /* ══════════════════════ ACTIONS AVANCÉES ══════════════════════ */

  // 🔴 Guard global: bloquer si image non prête
  const canEdit = imageReady && !processing && workerReady && !simpleMode;

  /* ── Filter ── */
  const handleFilter = useCallback(async (newFilter) => {
    if (!imageReady || processing || !isScanReady() || simpleMode) {
      console.warn('[Scanner] Image non prête, filtre ignoré');
      return;
    }
    setFilter(newFilter);
    setProcessing(true);
    setStepLog('Application du filtre...');
    const t0 = performance.now();
    try {
      const result = await workerFilter(newFilter);
      setProcessedUrl(imageDataToUrl(result.imageData));
      const label = newFilter === 'bw' ? 'Noir & Blanc' : newFilter === 'original' ? 'Original' : 'Contraste+';
      setStepLog(`Filtre ${label} appliqué (${Math.round(performance.now() - t0)}ms)`);
    } catch (err) {
      console.warn('[Scanner] Filtre échoué:', err.message);
      setStepLog('Erreur filtre — image conservée');
    }
    setProcessing(false);
  }, [imageReady, processing, simpleMode]);

  /* ── Rotate ── */
  const handleRotate = useCallback(async (direction = 'right') => {
    if (!imageReady || processing || !isScanReady()) {
      console.warn('[Scanner] Image non prête, rotation ignorée');
      return;
    }
    setProcessing(true);
    setStepLog(direction === 'left' ? 'Rotation gauche...' : 'Rotation droite...');
    const t0 = performance.now();
    try {
      const result = await workerRotate(direction);
      setProcessedUrl(imageDataToUrl(result.imageData));
      setStepLog(`Rotation ${direction === 'left' ? 'gauche' : 'droite'} (${Math.round(performance.now() - t0)}ms)`);
    } catch (err) {
      console.warn('[Scanner] Rotation échouée:', err.message);
      setStepLog('Erreur rotation — image conservée');
    }
    setProcessing(false);
  }, [imageReady, processing]);

  /* ── Crop ── */
  const applyManualCorners = useCallback(async () => {
    if (!imageReady || processing || !isScanReady() || !manualCorners) {
      console.warn('[Scanner] Image non prête, crop ignoré');
      return;
    }
    setProcessing(true);
    setStepLog('Recadrage...');
    const t0 = performance.now();
    try {
      const xs = manualCorners.map(c => c.x);
      const ys = manualCorners.map(c => c.y);
      const result = await workerCrop({ x0: Math.min(...xs), y0: Math.min(...ys), x1: Math.max(...xs), y1: Math.max(...ys) });
      setProcessedUrl(imageDataToUrl(result.imageData));
      setShowManualMode(false);
      setAutoDetected(true);
      setStepLog(`Recadrage appliqué (${Math.round(performance.now() - t0)}ms)`);
    } catch (err) {
      console.warn('[Scanner] Crop échoué:', err.message);
      setStepLog('Erreur recadrage — image conservée');
    }
    setProcessing(false);
  }, [imageReady, processing, manualCorners]);

  /* ── Brightness/Contrast ── */
  const adjustTimeoutRef = useRef(null);
  const handleAdjust = useCallback(async (b, c) => {
    if (!imageReady || !isScanReady()) return;
    const t0 = performance.now();
    try {
      const result = await workerAdjust(b, c);
      setProcessedUrl(imageDataToUrl(result.imageData));
      setStepLog(`Luminosité ${b > 0 ? '+' : ''}${b} / Contraste ${c > 0 ? '+' : ''}${c} (${Math.round(performance.now() - t0)}ms)`);
    } catch (err) {
      console.warn('[Scanner] Adjust échoué:', err.message);
    }
  }, [imageReady]);

  const onSliderChange = useCallback((newB, newC) => {
    setBrightness(newB); setContrast(newC);
    if (adjustTimeoutRef.current) clearTimeout(adjustTimeoutRef.current);
    adjustTimeoutRef.current = setTimeout(() => handleAdjust(newB, newC), 200);
  }, [handleAdjust]);

  /* ── Simple mode ── */
  const switchToSimple = useCallback(() => {
    setSimpleMode(true);
    if (rawDataUrl && canvasRef.current) {
      const img = new Image();
      img.onload = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        canvas.width = img.width; canvas.height = img.height;
        canvas.getContext('2d').drawImage(img, 0, 0);
        setProcessedUrl(lightEnhance(canvas));
        setAutoDetected(false); setShowManualMode(false);
        setStepLog('Mode simple activé');
      };
      img.src = rawDataUrl;
    }
  }, [rawDataUrl]);

  /* ══════════════════════ PAGE MANAGEMENT ══════════════════════ */
  const addPageAndContinue = useCallback(async () => {
    if (!processedUrl) return;
    setPages(p => [...p, processedUrl]);
    setActivePageIndex(pages.length);
    setProcessedUrl(null); setRawDataUrl(null); setShowManualMode(false); setShowAdjust(false); setBrightness(0); setContrast(0);
    setImageReady(false);
    startCamera();
  }, [processedUrl, pages.length, startCamera]);

  const addPageAndFinish = useCallback(async () => {
    if (!processedUrl) return;
    setPages(p => [...p, processedUrl]);
    setActivePageIndex(0);
    setProcessedUrl(null); setImageReady(false); setPhase('pages');
  }, [processedUrl]);

  const confirmSingle = useCallback(async () => {
    if (!processedUrl) return;
    setPhase('finalizing');
    try {
      const r = await fetch(processedUrl);
      const b = await r.blob();
      onCapture(new File([b], `scan_${Date.now()}.jpg`, { type: 'image/jpeg' }));
    } catch {
      setError('Erreur lors de la sauvegarde');
      setPhase('preview');
    }
  }, [processedUrl, onCapture]);

  const removePage = useCallback((i) => {
    const np = pages.filter((_, j) => j !== i);
    setPages(np);
    if (!np.length) startCamera(); else setActivePageIndex(Math.min(i, np.length - 1));
  }, [pages, startCamera]);

  const confirmMulti = useCallback(async () => {
    setPhase('finalizing');
    try {
      const pdf = await buildPdf(pages);
      const b = pdf.output('blob');
      const imgs = await Promise.all(pages.map(async (u, i) => { const r = await fetch(u); const bl = await r.blob(); return new File([bl], `page${i + 1}.jpg`, { type: 'image/jpeg' }); }));
      stopCamera();
      onCapture(new File([b], `scan_${pages.length}p_${Date.now()}.pdf`, { type: 'application/pdf' }), imgs);
    } catch { setError('Erreur PDF'); setPhase('pages'); }
  }, [pages, onCapture, stopCamera]);

  const retake = useCallback(() => {
    setProcessedUrl(null); setRawDataUrl(null); setShowManualMode(false); setShowAdjust(false); setBrightness(0); setContrast(0);
    setImageReady(false);
    startCamera();
  }, [startCamera]);

  /* ══════════════════════ RENDER ══════════════════════ */
  return (
    <div className="fixed inset-0 z-50 bg-black flex flex-col" data-testid="document-scanner">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-black/80 backdrop-blur-sm flex-shrink-0">
        <h3 className="text-white text-sm font-semibold flex items-center gap-2">
          {pages.length > 0 && <span className="bg-accent text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full" data-testid="page-counter">{pages.length}</span>}
          <ScanLine className="w-4 h-4 text-emerald-400" />
          <span>CamScanner</span>
          {simpleMode && <span className="text-[10px] text-amber-400 font-normal ml-1">(Simple)</span>}
        </h3>
        <Button variant="ghost" size="sm" onClick={() => { stopCamera(); terminateScanWorker(); onClose(); }} className="text-white hover:bg-white/10 min-h-[44px] min-w-[44px]" data-testid="scanner-close" aria-label="Fermer le scanner">
          <X className="w-5 h-5" />
        </Button>
      </div>

      {pages.length > 0 && (phase === 'camera' || phase === 'preview') && (
        <PageStrip pages={pages} activeIndex={-1} onSelect={() => setPhase('pages')} onRemove={() => {}} />
      )}

      {stepLog && phase !== 'guide' && phase !== 'camera' && (
        <div className="px-4 py-1.5 bg-black/60 text-center" data-testid="step-log">
          <span className="text-white/50 text-[11px]">{stepLog}</span>
        </div>
      )}

      {/* ═══ GUIDE ═══ */}
      {phase === 'guide' && (
        <div className="flex-1 flex flex-col items-center justify-center px-6 gap-5 overflow-y-auto">
          <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center">
            <ScanLine className="w-8 h-8 text-emerald-400" />
          </div>
          <div className="text-center">
            <h2 className="text-white text-lg font-semibold mb-1" data-testid="scanner-title">CamScanner</h2>
            <p className="text-white/50 text-sm">{workerReady ? 'Détection et recadrage automatiques' : workerFailed ? 'Mode capture simple' : 'Préparation...'}</p>
          </div>
          <div className="w-full max-w-xs space-y-2.5">
            {[
              { icon: Smartphone, text: 'Tenez le téléphone bien droit', color: 'text-blue-400' },
              { icon: Maximize2, text: 'Tout le document doit être visible', color: 'text-emerald-400' },
              { icon: Sun, text: 'Bonne luminosité, évitez les ombres', color: 'text-amber-400' },
              { icon: ZapOff, text: 'Évitez les reflets et le flash', color: 'text-purple-400' },
            ].map((tip, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10" data-testid={`scanner-tip-${i}`}>
                <tip.icon className={`w-5 h-5 flex-shrink-0 ${tip.color}`} />
                <span className="text-white/80 text-sm">{tip.text}</span>
              </div>
            ))}
          </div>
          {workerLoading && (
            <div className="w-full max-w-xs flex items-center gap-2 p-3 rounded-xl bg-accent/10 border border-accent/20">
              <Loader2 className="w-4 h-4 text-accent animate-spin flex-shrink-0" />
              <span className="text-accent/80 text-xs">Préparation du scanner...</span>
            </div>
          )}
          {workerReady && !simpleMode && (
            <div className="w-full max-w-xs flex items-center gap-2 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20" data-testid="scanner-ready-badge">
              <Check className="w-5 h-5 text-emerald-400 flex-shrink-0" />
              <span className="text-emerald-400/80 text-xs font-medium">Cadrage automatique + correction perspective activés</span>
            </div>
          )}
          {(workerFailed || simpleMode) && (
            <div className="w-full max-w-xs flex items-center gap-2 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20" data-testid="scanner-failed-badge">
              <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0" />
              <span className="text-amber-400/80 text-xs font-medium">Mode simple — capture directe</span>
            </div>
          )}
          <div className="w-full max-w-xs pt-2 space-y-2">
            <Button onClick={startCamera} className="w-full gap-2 h-14 text-base font-semibold" data-testid="scanner-start-btn">
              <Camera className="w-5 h-5" /> Ouvrir la caméra
            </Button>
            <Button variant="outline" onClick={() => fileInputRef.current?.click()} className="w-full gap-2 h-12 text-sm border-white/20 text-white hover:bg-white/10" data-testid="scanner-file-btn" aria-label="Choisir une photo depuis la galerie">
              <ImageUp className="w-5 h-5" /> Choisir une photo
            </Button>
            {workerReady && (
              <button onClick={() => setSimpleMode(p => !p)} className="w-full text-center text-white/40 text-xs py-3 min-h-[44px] hover:text-white/60 transition-colors" data-testid="toggle-simple-mode">
                {simpleMode ? 'Réactiver le mode automatique' : 'Utiliser le mode simple (sans détection)'}
              </button>
            )}
          </div>
          {error && <p className="text-red-400 text-sm text-center max-w-xs" data-testid="scanner-error">{error}</p>}
        </div>
      )}

      {/* ═══ CAMERA ═══ */}
      {phase === 'camera' && (
        <div className="flex-1 relative overflow-hidden">
          <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" data-testid="scanner-video" />
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute inset-[6%] rounded-2xl border-2 border-white/70" style={{ boxShadow: '0 0 0 9999px rgba(0,0,0,0.35)' }} />
            <div className="absolute top-[6%] left-[6%] w-8 h-8 border-t-4 border-l-4 border-emerald-400 rounded-tl-lg" />
            <div className="absolute top-[6%] right-[6%] w-8 h-8 border-t-4 border-r-4 border-emerald-400 rounded-tr-lg" />
            <div className="absolute bottom-[6%] left-[6%] w-8 h-8 border-b-4 border-l-4 border-emerald-400 rounded-bl-lg" />
            <div className="absolute bottom-[6%] right-[6%] w-8 h-8 border-b-4 border-r-4 border-emerald-400 rounded-br-lg" />
            <div className="absolute top-[calc(6%+12px)] left-0 right-0 text-center">
              <span className="text-white/80 text-xs bg-black/50 px-3 py-1.5 rounded-full">
                {simpleMode ? 'Mode simple — cadrez manuellement' : pages.length === 0 ? 'Cadrez le document — détection auto' : `Page ${pages.length + 1}`}
              </span>
            </div>
          </div>
          {error && (
            <div className="absolute top-1/2 left-0 right-0 -translate-y-1/2 px-6 text-center" data-testid="camera-error">
              <p className="text-red-400 text-sm bg-black/80 rounded-xl p-4">{error}</p>
            </div>
          )}
          <div className="absolute bottom-0 left-0 right-0 flex items-center justify-center gap-6 pb-8 pt-4 bg-gradient-to-t from-black/80 to-transparent">
            <div className="flex flex-col items-center gap-1.5">
              <Button variant="ghost" size="sm" onClick={switchCamera} className="text-white hover:bg-white/10 rounded-full w-14 h-14 min-h-[56px]" data-testid="scanner-switch-camera" aria-label="Changer de caméra">
                <RotateCcw className="w-5 h-5" />
              </Button>
              <button onClick={() => fileInputRef.current?.click()} className="text-white/60 text-[10px] hover:text-white/80 min-h-[32px] px-2" data-testid="camera-gallery-btn" aria-label="Choisir depuis la galerie">
                <ImageUp className="w-4 h-4 mx-auto" />
              </button>
            </div>
            <button onClick={capture} className="rounded-full border-4 border-white bg-white/20 hover:bg-white/40 transition-colors flex items-center justify-center active:scale-95" data-testid="scanner-capture-btn" aria-label="Prendre la photo" style={{ width: 72, height: 72 }}>
              <div className="rounded-full bg-white" style={{ width: 56, height: 56 }} />
            </button>
            {pages.length > 0 ? (
              <Button variant="ghost" size="sm" onClick={() => { stopCamera(); setPhase('pages'); }} className="text-white hover:bg-white/10 rounded-full w-14 h-14 min-h-[56px]" aria-label="Voir les pages">
                <Check className="w-5 h-5" />
              </Button>
            ) : <div style={{ width: 56, height: 56 }} />}
          </div>
        </div>
      )}

      {/* ═══ PROCESSING ═══ */}
      {phase === 'processing' && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <div className="relative"><Loader2 className="w-16 h-16 text-emerald-400 animate-spin" /><ScanLine className="w-7 h-7 text-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" /></div>
          <p className="text-white text-base font-medium">Analyse du document...</p>
          <div className="flex flex-col items-center gap-1 text-white/40 text-xs"><span>Détection des contours</span><span>Correction de perspective</span><span>Optimisation lisibilité</span></div>
        </div>
      )}

      {/* ═══ PREVIEW ═══ */}
      {phase === 'preview' && processedUrl && (
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex-1 relative overflow-hidden bg-neutral-900 flex items-center justify-center p-3 min-h-0">
            {showManualMode ? (
              <div className="relative max-w-full max-h-full" ref={adjustImgRef}>
                <img src={rawDataUrl} alt="Original" className="max-w-full max-h-full object-contain rounded-lg select-none" draggable={false} />
                {manualCorners && <CornerAdjuster corners={manualCorners} setCorners={setManualCorners} imageRef={adjustImgRef} />}
              </div>
            ) : (
              <canvas ref={previewCanvasRef} className="max-w-full max-h-full object-contain rounded-lg" data-testid="preview-canvas" style={{ imageRendering: 'auto' }} />
            )}
            <div className="absolute top-2 left-2 flex flex-col gap-1.5">
              {processing && <span className="bg-amber-500/90 text-white text-[11px] font-medium px-2.5 py-1 rounded-full flex items-center gap-1.5"><Loader2 className="w-3 h-3 animate-spin" /> Traitement...</span>}
              {!processing && autoDetected && !showManualMode && <span className="bg-emerald-500/90 text-white text-[11px] font-medium px-2.5 py-1 rounded-full flex items-center gap-1.5" data-testid="auto-detected-badge"><Check className="w-3 h-3" /> Document détecté</span>}
              {!processing && !autoDetected && !showManualMode && <span className="bg-amber-500/80 text-white text-[11px] font-medium px-2.5 py-1 rounded-full flex items-center gap-1.5" data-testid="simple-mode-badge"><AlertCircle className="w-3 h-3" /> Mode simple</span>}
              {showManualMode && <span className="bg-blue-500/90 text-white text-[11px] font-medium px-2.5 py-1 rounded-full flex items-center gap-1.5" data-testid="manual-mode-badge"><Crop className="w-3 h-3" /> Déplacez les coins</span>}
            </div>
          </div>

          <div className="bg-black/90 border-t border-white/10 flex-shrink-0">
            {/* Toolbar */}
            <div className="flex items-center gap-1.5 px-3 py-2 border-b border-white/5 overflow-x-auto">
              {FILTERS.map(f => (
                <button key={f.id} onClick={() => handleFilter(f.id)} disabled={!canEdit}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium transition-all min-h-[40px] whitespace-nowrap ${filter === f.id && canEdit ? 'bg-emerald-500 text-white' : 'bg-white/8 text-white/60 hover:bg-white/15'} ${!canEdit ? 'opacity-40' : ''}`}
                  data-testid={`filter-${f.id}`} aria-label={`Filtre ${f.label}`}>
                  <f.icon className="w-3.5 h-3.5" /> {f.label}
                </button>
              ))}
              <div className="w-px h-7 bg-white/10 mx-0.5 flex-shrink-0" />
              <button onClick={() => handleRotate('left')} disabled={!canEdit}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium bg-white/8 text-white/60 hover:bg-white/15 min-h-[40px] whitespace-nowrap ${!canEdit ? 'opacity-30' : ''}`}
                data-testid="rotate-left-btn" aria-label="Rotation gauche">
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
              <button onClick={() => handleRotate('right')} disabled={!canEdit}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium bg-white/8 text-white/60 hover:bg-white/15 min-h-[40px] whitespace-nowrap ${!canEdit ? 'opacity-30' : ''}`}
                data-testid="rotate-right-btn" aria-label="Rotation droite">
                <RotateCw className="w-3.5 h-3.5" />
              </button>
              <div className="w-px h-7 bg-white/10 mx-0.5 flex-shrink-0" />
              {!showManualMode ? (
                <button onClick={() => setShowManualMode(true)} disabled={!canEdit}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium bg-white/8 text-white/60 hover:bg-white/15 min-h-[40px] whitespace-nowrap ${!canEdit ? 'opacity-30' : ''}`}
                  data-testid="manual-crop-btn" aria-label="Recadrer manuellement">
                  <Crop className="w-3.5 h-3.5" /> Recadrer
                </button>
              ) : (
                <button onClick={applyManualCorners} disabled={processing}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium bg-emerald-500 text-white min-h-[40px] whitespace-nowrap"
                  data-testid="apply-crop-btn" aria-label="Appliquer le recadrage">
                  <Check className="w-3.5 h-3.5" /> Appliquer
                </button>
              )}
              <button onClick={() => setShowAdjust(p => !p)} disabled={!canEdit}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium min-h-[40px] whitespace-nowrap ${showAdjust ? 'bg-blue-500 text-white' : 'bg-white/8 text-white/60 hover:bg-white/15'} ${!canEdit ? 'opacity-30' : ''}`}
                data-testid="adjust-toggle-btn" aria-label="Réglages luminosité et contraste">
                <SunMedium className="w-3.5 h-3.5" /> Réglages
              </button>
            </div>

            {/* Sliders */}
            {showAdjust && canEdit && (
              <div className="px-4 py-3 border-b border-white/5 space-y-3" data-testid="adjust-panel">
                <div className="flex items-center gap-3">
                  <Sun className="w-4 h-4 text-amber-400 flex-shrink-0" />
                  <span className="text-white/60 text-xs w-20">Luminosité</span>
                  <Slider min={-80} max={80} step={1} value={[brightness]} onValueChange={(v) => onSliderChange(v[0], contrast)} className="flex-1" data-testid="brightness-slider" />
                  <span className="text-white/50 text-xs w-8 text-right">{brightness}</span>
                </div>
                <div className="flex items-center gap-3">
                  <Contrast className="w-4 h-4 text-blue-400 flex-shrink-0" />
                  <span className="text-white/60 text-xs w-20">Contraste</span>
                  <Slider min={-80} max={80} step={1} value={[contrast]} onValueChange={(v) => onSliderChange(brightness, v[0])} className="flex-1" data-testid="contrast-slider" />
                  <span className="text-white/50 text-xs w-8 text-right">{contrast}</span>
                </div>
                {(brightness !== 0 || contrast !== 0) && (
                  <button onClick={() => onSliderChange(0, 0)} className="text-white/40 text-xs hover:text-white/60 transition-colors" data-testid="reset-adjust-btn">Réinitialiser</button>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="p-3 space-y-2">
              {pages.length === 0 ? (
                <Button onClick={confirmSingle} disabled={processing} className="w-full gap-2 h-14 text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 min-h-[56px]" data-testid="preview-confirm-btn" aria-label="Valider ce document">
                  <Check className="w-5 h-5" /> Valider / Sauvegarder
                </Button>
              ) : (
                <Button onClick={addPageAndFinish} disabled={processing} className="w-full gap-2 h-14 text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 min-h-[56px]" data-testid="preview-finish-btn" aria-label={`Terminer avec ${pages.length + 1} pages`}>
                  <Layers className="w-5 h-5" /> Terminer ({pages.length + 1} pages)
                </Button>
              )}
              <div className="flex gap-2">
                <Button variant="outline" onClick={retake} className="flex-1 gap-2 h-12 border-white/20 text-white hover:bg-white/10 text-sm min-h-[48px]" data-testid="preview-retake-btn" aria-label="Reprendre la photo">
                  <RotateCcw className="w-4 h-4" /> Reprendre
                </Button>
                <Button variant="outline" onClick={addPageAndContinue} className="flex-1 gap-2 h-12 border-white/20 text-white hover:bg-white/10 text-sm min-h-[48px]" data-testid="preview-add-page-btn" aria-label="Page suivante">
                  <Plus className="w-4 h-4" /> Page suivante
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ═══ PAGES ═══ */}
      {phase === 'pages' && pages.length > 0 && (
        <div className="flex-1 flex flex-col">
          <PageStrip pages={pages} activeIndex={activePageIndex} onSelect={setActivePageIndex} onRemove={removePage} />
          <div className="flex-1 relative overflow-hidden bg-black flex items-center justify-center p-4">
            <img src={pages[activePageIndex]} alt={`Page ${activePageIndex + 1}`} className="max-w-full max-h-full object-contain rounded-lg" data-testid="pages-active-preview" />
            {pages.length > 1 && activePageIndex > 0 && <button onClick={() => setActivePageIndex(p => p - 1)} className="absolute left-2 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/60 flex items-center justify-center min-h-[48px]" aria-label="Page précédente"><ChevronLeft className="w-5 h-5 text-white" /></button>}
            {pages.length > 1 && activePageIndex < pages.length - 1 && <button onClick={() => setActivePageIndex(p => p + 1)} className="absolute right-2 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/60 flex items-center justify-center min-h-[48px]" aria-label="Page suivante"><ChevronRight className="w-5 h-5 text-white" /></button>}
            <div className="absolute top-3 left-3 bg-accent/90 text-white text-[11px] font-medium px-2.5 py-1 rounded-full">Page {activePageIndex + 1} / {pages.length}</div>
          </div>
          <div className="p-4 bg-black/80 space-y-2 flex-shrink-0">
            <div className="flex gap-2">
              <Button variant="outline" onClick={startCamera} className="flex-1 gap-2 h-12 min-h-[48px] border-white/20 text-white hover:bg-white/10" aria-label="Ajouter une page"><Plus className="w-4 h-4" /> Ajouter</Button>
              <Button onClick={async () => { setPhase('finalizing'); const pdf = await buildPdf(pages); const b = pdf.output('blob'); if (pdfUrl) URL.revokeObjectURL(pdfUrl); setPdfUrl(URL.createObjectURL(b)); setPhase('pdfPreview'); }} className="flex-1 gap-2 h-12 min-h-[48px]" aria-label="Aperçu PDF"><Eye className="w-4 h-4" /> Aperçu PDF</Button>
            </div>
            <Button onClick={confirmMulti} className="w-full gap-2 h-14 min-h-[56px] bg-emerald-600 hover:bg-emerald-500 font-semibold" aria-label={`Fusionner ${pages.length} pages`}><Layers className="w-4 h-4" /> Fusionner ({pages.length} pages)</Button>
          </div>
        </div>
      )}

      {/* ═══ PDF PREVIEW ═══ */}
      {phase === 'pdfPreview' && pdfUrl && (
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-hidden bg-white"><iframe src={pdfUrl} title="Aperçu PDF" className="w-full h-full border-0" /></div>
          <div className="p-4 bg-black/80 flex gap-2 flex-shrink-0">
            <Button variant="outline" onClick={() => setPhase('pages')} className="flex-1 gap-2 h-12 min-h-[48px] border-white/20 text-white hover:bg-white/10" aria-label="Retour"><ChevronLeft className="w-4 h-4" /> Retour</Button>
            <Button onClick={confirmMulti} className="flex-1 gap-2 h-12 min-h-[48px] bg-emerald-600 hover:bg-emerald-500" aria-label="Valider"><Check className="w-4 h-4" /> Valider</Button>
          </div>
        </div>
      )}

      {/* ═══ FINALIZING ═══ */}
      {phase === 'finalizing' && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <Loader2 className="w-14 h-14 text-emerald-400 animate-spin" />
          <p className="text-white text-base font-medium">Préparation du document...</p>
        </div>
      )}

      <canvas ref={canvasRef} className="hidden" />
      <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileInput} className="hidden" data-testid="scanner-file-input" />
    </div>
  );
};
