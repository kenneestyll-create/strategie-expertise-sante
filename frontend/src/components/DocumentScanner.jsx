import { useState, useRef, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Camera, X, RotateCcw, Check, Smartphone, Sun,
  Eye, Maximize2, ZapOff, Loader2, Plus, Trash2,
  FileText, ChevronLeft, ChevronRight, Layers,
  RotateCw, Wand2, Crop, SunMedium, Contrast
} from 'lucide-react';
import { jsPDF } from 'jspdf';

/* ── Enhancement filters (canvas-based) ── */
function applyFilter(canvas, mode) {
  const ctx = canvas.getContext('2d');
  const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const d = img.data;

  if (mode === 'document') {
    // High contrast + sharpening for OCR
    const contrast = 1.5, brightness = 15;
    for (let i = 0; i < d.length; i += 4) {
      d[i]     = Math.min(255, Math.max(0, (d[i]     - 128) * contrast + 128 + brightness));
      d[i + 1] = Math.min(255, Math.max(0, (d[i + 1] - 128) * contrast + 128 + brightness));
      d[i + 2] = Math.min(255, Math.max(0, (d[i + 2] - 128) * contrast + 128 + brightness));
    }
    ctx.putImageData(img, 0, 0);
    // Unsharp mask
    const w = canvas.width, h = canvas.height;
    const src = ctx.getImageData(0, 0, w, h);
    const dst = ctx.createImageData(w, h);
    const k = [0, -0.7, 0, -0.7, 3.8, -0.7, 0, -0.7, 0];
    for (let y = 1; y < h - 1; y++) {
      for (let x = 1; x < w - 1; x++) {
        for (let c = 0; c < 3; c++) {
          let v = 0;
          for (let ky = -1; ky <= 1; ky++)
            for (let kx = -1; kx <= 1; kx++)
              v += src.data[((y + ky) * w + (x + kx)) * 4 + c] * k[(ky + 1) * 3 + (kx + 1)];
          dst.data[(y * w + x) * 4 + c] = Math.min(255, Math.max(0, v));
        }
        dst.data[(y * w + x) * 4 + 3] = 255;
      }
    }
    ctx.putImageData(dst, 0, 0);
  } else if (mode === 'bw') {
    // Adaptive black & white for documents
    for (let i = 0; i < d.length; i += 4) {
      const gray = d[i] * 0.299 + d[i + 1] * 0.587 + d[i + 2] * 0.114;
      const val = gray > 140 ? 255 : 0;
      d[i] = d[i + 1] = d[i + 2] = val;
    }
    ctx.putImageData(img, 0, 0);
  }
  // 'original' → no processing
  return canvas;
}

function rotateCanvas(sourceCanvas, degrees) {
  const c = document.createElement('canvas');
  const ctx = c.getContext('2d');
  if (degrees === 90 || degrees === -90 || degrees === 270) {
    c.width = sourceCanvas.height;
    c.height = sourceCanvas.width;
  } else {
    c.width = sourceCanvas.width;
    c.height = sourceCanvas.height;
  }
  ctx.translate(c.width / 2, c.height / 2);
  ctx.rotate((degrees * Math.PI) / 180);
  ctx.drawImage(sourceCanvas, -sourceCanvas.width / 2, -sourceCanvas.height / 2);
  return c;
}

async function buildPdf(pages) {
  const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const A4_W = 210, A4_H = 297;
  for (let i = 0; i < pages.length; i++) {
    if (i > 0) pdf.addPage();
    const img = new Image();
    img.src = pages[i];
    await new Promise(r => { img.onload = r; });
    const ratio = Math.min(A4_W / img.width, A4_H / img.height);
    const w = img.width * ratio, h = img.height * ratio;
    pdf.addImage(pages[i], 'JPEG', (A4_W - w) / 2, (A4_H - h) / 2, w, h);
  }
  return pdf;
}

const GUIDE_TIPS = [
  { icon: Smartphone, text: 'Tenez le téléphone bien droit', color: 'text-blue-500' },
  { icon: Maximize2, text: 'Document entièrement visible', color: 'text-emerald-500' },
  { icon: Sun, text: 'Bonne luminosité', color: 'text-amber-500' },
  { icon: ZapOff, text: 'Évitez les reflets', color: 'text-purple-500' },
];

const FILTERS = [
  { id: 'original', label: 'Original', icon: Eye },
  { id: 'document', label: 'Document', icon: Contrast },
  { id: 'bw', label: 'Noir & Blanc', icon: FileText },
];

/* ── Page thumbnail strip ── */
const PageStrip = ({ pages, activeIndex, onSelect, onRemove }) => (
  <div className="flex gap-2 px-4 py-2 overflow-x-auto bg-black/60 backdrop-blur-sm" data-testid="page-strip">
    {pages.map((src, i) => (
      <div key={i} onClick={() => onSelect(i)}
        className={`relative flex-shrink-0 w-14 h-20 rounded-lg overflow-hidden border-2 cursor-pointer transition-all ${i === activeIndex ? 'border-accent scale-105' : 'border-white/20 opacity-70'}`}
        data-testid={`page-thumb-${i}`}>
        <img src={src} alt={`Page ${i + 1}`} className="w-full h-full object-cover" />
        <span className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-[9px] text-center py-0.5">{i + 1}</span>
        {pages.length > 1 && (
          <button onClick={(e) => { e.stopPropagation(); onRemove(i); }}
            className="absolute top-0.5 right-0.5 w-5 h-5 rounded-full bg-red-500 flex items-center justify-center" data-testid={`page-remove-${i}`}>
            <X className="w-3 h-3 text-white" />
          </button>
        )}
      </div>
    ))}
  </div>
);

/* ── Draggable Crop Overlay ── */
const CropOverlay = ({ corners, setCorners, containerRef }) => {
  const dragging = useRef(null);

  const getPos = useCallback((e) => {
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return { x: 0, y: 0 };
    const touch = e.touches ? e.touches[0] : e;
    return {
      x: Math.max(0, Math.min(1, (touch.clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (touch.clientY - rect.top) / rect.height)),
    };
  }, [containerRef]);

  const onStart = useCallback((idx, e) => {
    e.preventDefault();
    e.stopPropagation();
    dragging.current = idx;
  }, []);

  useEffect(() => {
    const onMove = (e) => {
      if (dragging.current === null) return;
      e.preventDefault();
      const pos = getPos(e);
      setCorners(prev => prev.map((c, i) => i === dragging.current ? pos : c));
    };
    const onEnd = () => { dragging.current = null; };
    window.addEventListener('mousemove', onMove, { passive: false });
    window.addEventListener('mouseup', onEnd);
    window.addEventListener('touchmove', onMove, { passive: false });
    window.addEventListener('touchend', onEnd);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onEnd);
      window.removeEventListener('touchmove', onMove);
      window.removeEventListener('touchend', onEnd);
    };
  }, [getPos, setCorners]);

  const [tl, tr, br, bl] = corners;
  const points = `${tl.x * 100}%,${tl.y * 100}% ${tr.x * 100}%,${tr.y * 100}% ${br.x * 100}%,${br.y * 100}% ${bl.x * 100}%,${bl.y * 100}%`;

  return (
    <div className="absolute inset-0" data-testid="crop-overlay">
      {/* Dimmed area outside crop */}
      <svg className="absolute inset-0 w-full h-full">
        <defs>
          <mask id="cropMask">
            <rect width="100%" height="100%" fill="white" />
            <polygon points={points} fill="black" />
          </mask>
        </defs>
        <rect width="100%" height="100%" fill="rgba(0,0,0,0.5)" mask="url(#cropMask)" />
        <polygon points={points} fill="none" stroke="#22c55e" strokeWidth="2" strokeDasharray="6 3" />
      </svg>
      {/* Corner handles */}
      {corners.map((c, i) => (
        <div key={i}
          onMouseDown={(e) => onStart(i, e)}
          onTouchStart={(e) => onStart(i, e)}
          className="absolute w-11 h-11 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center cursor-grab active:cursor-grabbing touch-none"
          style={{ left: `${c.x * 100}%`, top: `${c.y * 100}%` }}
          data-testid={`crop-handle-${i}`}>
          <div className="w-5 h-5 rounded-full bg-emerald-500 border-[3px] border-white shadow-lg shadow-black/40" />
        </div>
      ))}
    </div>
  );
};

/* ── Main Scanner Component ── */
export const DocumentScanner = ({ onCapture, onClose }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const cropContainerRef = useRef(null);

  const [phase, setPhase] = useState('guide');
  const [pages, setPages] = useState([]);
  const [rawCapture, setRawCapture] = useState(null);
  const [adjustedCapture, setAdjustedCapture] = useState(null);
  const [currentCapture, setCurrentCapture] = useState(null);
  const [activePageIndex, setActivePageIndex] = useState(0);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [error, setError] = useState('');
  const [facingMode, setFacingMode] = useState('environment');
  const [filter, setFilter] = useState('document');
  const [rotation, setRotation] = useState(0);
  const [cropCorners, setCropCorners] = useState([
    { x: 0.05, y: 0.05 }, { x: 0.95, y: 0.05 },
    { x: 0.95, y: 0.95 }, { x: 0.05, y: 0.95 },
  ]);
  const [showCrop, setShowCrop] = useState(false);

  /* ── Camera lifecycle ── */
  const startCamera = useCallback(async () => {
    setError('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 1920 }, height: { ideal: 1080 } },
        audio: false,
      });
      streamRef.current = stream;
      setPhase('camera');
    } catch (err) {
      if (err.name === 'NotAllowedError') setError("Accès caméra refusé. Autorisez l'accès dans les paramètres.");
      else if (err.name === 'NotFoundError') setError('Aucune caméra détectée.');
      else setError(`Erreur caméra : ${err.message}`);
    }
  }, [facingMode]);

  useEffect(() => {
    if (phase === 'camera' && streamRef.current && videoRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch(() => {});
    }
  }, [phase]);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
  }, []);

  useEffect(() => () => {
    stopCamera();
    if (pdfUrl) URL.revokeObjectURL(pdfUrl);
  }, [stopCamera, pdfUrl]);

  const switchCamera = useCallback(() => {
    stopCamera();
    setFacingMode(prev => prev === 'environment' ? 'user' : 'environment');
  }, [stopCamera]);

  useEffect(() => {
    if (phase === 'camera' && !streamRef.current) startCamera();
  }, [facingMode, phase, startCamera]);

  /* ── Capture → Adjust ── */
  const capture = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
    setRawCapture(dataUrl);
    setAdjustedCapture(dataUrl);
    setFilter('document');
    setRotation(0);
    setCropCorners([
      { x: 0.04, y: 0.04 }, { x: 0.96, y: 0.04 },
      { x: 0.96, y: 0.96 }, { x: 0.04, y: 0.96 },
    ]);
    setShowCrop(false);
    stopCamera();
    setPhase('adjust');
  }, [stopCamera]);

  /* ── Apply filter preview ── */
  useEffect(() => {
    if (phase !== 'adjust' || !rawCapture) return;
    const img = new Image();
    img.onload = () => {
      const c = document.createElement('canvas');
      c.width = img.width;
      c.height = img.height;
      c.getContext('2d').drawImage(img, 0, 0);

      // Rotate
      let result = c;
      if (rotation !== 0) result = rotateCanvas(c, rotation);

      // Filter
      applyFilter(result, filter);
      setAdjustedCapture(result.toDataURL('image/jpeg', 0.92));
    };
    img.src = rawCapture;
  }, [rawCapture, filter, rotation, phase]);

  /* ── Finalize adjusted image (with crop) ── */
  const finalizeAdjust = useCallback(() => {
    const img = new Image();
    img.onload = () => {
      const c = document.createElement('canvas');
      c.width = img.width;
      c.height = img.height;
      c.getContext('2d').drawImage(img, 0, 0);

      // Rotate
      let result = c;
      if (rotation !== 0) result = rotateCanvas(c, rotation);

      // Apply filter
      applyFilter(result, filter);

      // Crop
      if (showCrop) {
        const [tl, tr, br, bl] = cropCorners;
        const minX = Math.min(tl.x, bl.x);
        const maxX = Math.max(tr.x, br.x);
        const minY = Math.min(tl.y, tr.y);
        const maxY = Math.max(bl.y, br.y);
        const sx = minX * result.width;
        const sy = minY * result.height;
        const sw = (maxX - minX) * result.width;
        const sh = (maxY - minY) * result.height;
        const cropped = document.createElement('canvas');
        cropped.width = sw;
        cropped.height = sh;
        cropped.getContext('2d').drawImage(result, sx, sy, sw, sh, 0, 0, sw, sh);
        result = cropped;
      }

      setCurrentCapture(result.toDataURL('image/jpeg', 0.92));
      setPhase('preview');
    };
    img.src = rawCapture;
  }, [rawCapture, filter, rotation, showCrop, cropCorners]);

  /* ── Auto-adjust (applies Document filter + resets crop) ── */
  const autoAdjust = useCallback(() => {
    setFilter('document');
    setRotation(0);
    setShowCrop(false);
    setCropCorners([
      { x: 0.04, y: 0.04 }, { x: 0.96, y: 0.04 },
      { x: 0.96, y: 0.96 }, { x: 0.04, y: 0.96 },
    ]);
  }, []);

  /* ── Page management ── */
  const addPageAndContinue = useCallback(() => {
    if (!currentCapture) return;
    setPages(prev => [...prev, currentCapture]);
    setActivePageIndex(pages.length);
    setCurrentCapture(null);
    setRawCapture(null);
    startCamera();
  }, [currentCapture, pages.length, startCamera]);

  const addPageAndFinish = useCallback(() => {
    if (!currentCapture) return;
    const newPages = [...pages, currentCapture];
    setPages(newPages);
    setActivePageIndex(0);
    setCurrentCapture(null);
    setRawCapture(null);
    setPhase('pages');
  }, [currentCapture, pages]);

  const confirmSinglePage = useCallback(async () => {
    if (!currentCapture) return;
    setPhase('processing');
    const res = await fetch(currentCapture);
    const blob = await res.blob();
    const file = new File([blob], `scan_${Date.now()}.jpg`, { type: 'image/jpeg' });
    onCapture(file);
  }, [currentCapture, onCapture]);

  const removePage = useCallback((index) => {
    const newPages = pages.filter((_, i) => i !== index);
    setPages(newPages);
    if (newPages.length === 0) startCamera();
    else setActivePageIndex(Math.min(index, newPages.length - 1));
  }, [pages, startCamera]);

  const generatePdfPreview = useCallback(async () => {
    if (pages.length === 0) return;
    setPhase('processing');
    try {
      const pdf = await buildPdf(pages);
      const blob = pdf.output('blob');
      const url = URL.createObjectURL(blob);
      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
      setPdfUrl(url);
      setPhase('pdfPreview');
    } catch {
      setError('Erreur lors de la génération du PDF');
      setPhase('pages');
    }
  }, [pages, pdfUrl]);

  const confirmMultiScan = useCallback(async () => {
    setPhase('processing');
    try {
      const pdf = await buildPdf(pages);
      const blob = pdf.output('blob');
      const file = new File([blob], `scan_${pages.length}pages_${Date.now()}.pdf`, { type: 'application/pdf' });
      const imageFiles = await Promise.all(pages.map(async (dataUrl, i) => {
        const r = await fetch(dataUrl);
        const b = await r.blob();
        return new File([b], `scan_page${i + 1}.jpg`, { type: 'image/jpeg' });
      }));
      stopCamera();
      onCapture(file, imageFiles);
    } catch {
      setError('Erreur lors de la création du PDF');
      setPhase('pages');
    }
  }, [pages, onCapture, stopCamera]);

  const retake = useCallback(() => {
    setCurrentCapture(null);
    setRawCapture(null);
    setAdjustedCapture(null);
    startCamera();
  }, [startCamera]);

  /* ── Render ── */
  return (
    <div className="fixed inset-0 z-50 bg-black flex flex-col" data-testid="document-scanner">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-black/80 backdrop-blur-sm flex-shrink-0">
        <h3 className="text-white text-sm font-medium flex items-center gap-2">
          {pages.length > 0 && <span className="bg-accent text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full" data-testid="page-counter">{pages.length}</span>}
          Scanner un document
        </h3>
        <Button variant="ghost" size="sm" onClick={() => { stopCamera(); onClose(); }} className="text-white hover:bg-white/10" data-testid="scanner-close">
          <X className="w-5 h-5" />
        </Button>
      </div>

      {pages.length > 0 && (phase === 'camera' || phase === 'adjust' || phase === 'preview') && (
        <PageStrip pages={pages} activeIndex={-1} onSelect={() => {}} onRemove={() => {}} />
      )}

      {/* ====== GUIDE ====== */}
      {phase === 'guide' && (
        <div className="flex-1 flex flex-col items-center justify-center px-6 gap-6">
          <div className="w-20 h-20 rounded-full bg-accent/20 flex items-center justify-center">
            <Camera className="w-10 h-10 text-accent" />
          </div>
          <div className="text-center">
            <h2 className="text-white text-lg font-semibold mb-1">Scanner un document</h2>
            <p className="text-white/60 text-sm">Pour un meilleur résultat :</p>
          </div>
          <div className="w-full max-w-xs space-y-3">
            {GUIDE_TIPS.map((tip, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10" data-testid={`scanner-tip-${i}`}>
                <tip.icon className={`w-5 h-5 flex-shrink-0 ${tip.color}`} />
                <span className="text-white text-sm">{tip.text}</span>
              </div>
            ))}
          </div>
          <div className="w-full max-w-xs p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
            <p className="text-blue-300 text-xs flex items-center gap-2">
              <Layers className="w-4 h-4 flex-shrink-0" />
              Multi-pages : scannez plusieurs pages pour un seul PDF.
            </p>
          </div>
          <Button onClick={startCamera} className="w-full max-w-xs gap-2 h-12 text-base" data-testid="scanner-start-btn">
            <Camera className="w-5 h-5" /> Ouvrir la caméra
          </Button>
          {error && <p className="text-red-400 text-sm text-center max-w-xs" data-testid="scanner-error">{error}</p>}
        </div>
      )}

      {/* ====== CAMERA ====== */}
      {phase === 'camera' && (
        <div className="flex-1 relative overflow-hidden">
          <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" data-testid="scanner-video" />
          <div className="absolute inset-0 pointer-events-none" data-testid="scanner-overlay">
            <div className="absolute inset-[8%] sm:inset-[12%] rounded-2xl border-2 border-white/80 bg-transparent" style={{ boxShadow: '0 0 0 9999px rgba(0,0,0,0.4)' }} />
            <div className="absolute top-[8%] left-[8%] sm:top-[12%] sm:left-[12%] w-8 h-8 border-t-4 border-l-4 border-accent rounded-tl-lg" />
            <div className="absolute top-[8%] right-[8%] sm:top-[12%] sm:right-[12%] w-8 h-8 border-t-4 border-r-4 border-accent rounded-tr-lg" />
            <div className="absolute bottom-[8%] left-[8%] sm:bottom-[12%] sm:left-[12%] w-8 h-8 border-b-4 border-l-4 border-accent rounded-bl-lg" />
            <div className="absolute bottom-[8%] right-[8%] sm:bottom-[12%] sm:right-[12%] w-8 h-8 border-b-4 border-r-4 border-accent rounded-br-lg" />
            <div className="absolute top-[calc(8%+12px)] sm:top-[calc(12%+12px)] left-0 right-0 text-center">
              <span className="text-white/80 text-xs bg-black/50 px-3 py-1 rounded-full">
                {pages.length === 0 ? 'Centrez le document dans le cadre' : `Page ${pages.length + 1}`}
              </span>
            </div>
          </div>
          <div className="absolute bottom-0 left-0 right-0 flex items-center justify-center gap-6 pb-8 pt-4 bg-gradient-to-t from-black/80 to-transparent">
            <Button variant="ghost" size="sm" onClick={switchCamera} className="text-white hover:bg-white/10 rounded-full w-12 h-12" data-testid="scanner-switch-camera">
              <RotateCcw className="w-5 h-5" />
            </Button>
            <button onClick={capture} className="w-16 h-16 rounded-full border-4 border-white bg-white/20 hover:bg-white/40 transition-colors flex items-center justify-center active:scale-95" data-testid="scanner-capture-btn">
              <div className="w-12 h-12 rounded-full bg-white" />
            </button>
            {pages.length > 0 ? (
              <Button variant="ghost" size="sm" onClick={() => { stopCamera(); setPhase('pages'); }} className="text-white hover:bg-white/10 rounded-full w-12 h-12" data-testid="scanner-done-camera">
                <Check className="w-5 h-5" />
              </Button>
            ) : <div className="w-12 h-12" />}
          </div>
        </div>
      )}

      {/* ====== ADJUST PHASE ====== */}
      {phase === 'adjust' && adjustedCapture && (
        <div className="flex-1 flex flex-col min-h-0">
          {/* Image area with optional crop */}
          <div className="flex-1 relative overflow-hidden bg-black/90 flex items-center justify-center p-3 min-h-0" ref={cropContainerRef}>
            <img
              src={adjustedCapture}
              alt="Document"
              className="max-w-full max-h-full object-contain rounded-lg select-none"
              draggable={false}
              data-testid="adjust-preview-img"
            />
            {showCrop && (
              <div className="absolute inset-3">
                <div className="relative w-full h-full">
                  <CropOverlay corners={cropCorners} setCorners={setCropCorners} containerRef={cropContainerRef} />
                </div>
              </div>
            )}
            {/* Status badge */}
            <div className="absolute top-2 left-2 flex gap-1.5">
              <span className="bg-emerald-500/90 text-white text-[10px] font-medium px-2 py-1 rounded-full flex items-center gap-1">
                <Wand2 className="w-3 h-3" /> {FILTERS.find(f => f.id === filter)?.label}
              </span>
              {rotation !== 0 && (
                <span className="bg-blue-500/90 text-white text-[10px] font-medium px-2 py-1 rounded-full">
                  {rotation}°
                </span>
              )}
            </div>
          </div>

          {/* Tools bar */}
          <div className="bg-black/90 border-t border-white/10 flex-shrink-0">
            {/* Filter buttons */}
            <div className="flex items-center justify-center gap-2 px-4 py-2.5 border-b border-white/5">
              {FILTERS.map(f => (
                <button
                  key={f.id}
                  onClick={() => setFilter(f.id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                    filter === f.id ? 'bg-emerald-500 text-white' : 'bg-white/8 text-white/60 hover:bg-white/15'
                  }`}
                  data-testid={`filter-${f.id}`}
                >
                  <f.icon className="w-3.5 h-3.5" />
                  {f.label}
                </button>
              ))}
            </div>

            {/* Tool buttons row */}
            <div className="flex items-center justify-center gap-3 px-4 py-2.5 border-b border-white/5">
              <button onClick={() => setRotation(r => (r - 90 + 360) % 360)}
                className="flex flex-col items-center gap-0.5 text-white/60 hover:text-white transition-colors px-3 py-1"
                data-testid="rotate-left-btn">
                <RotateCcw className="w-5 h-5" />
                <span className="text-[10px]">Gauche</span>
              </button>
              <button onClick={() => setRotation(r => (r + 90) % 360)}
                className="flex flex-col items-center gap-0.5 text-white/60 hover:text-white transition-colors px-3 py-1"
                data-testid="rotate-right-btn">
                <RotateCw className="w-5 h-5" />
                <span className="text-[10px]">Droite</span>
              </button>
              <div className="w-px h-8 bg-white/10" />
              <button onClick={() => setShowCrop(v => !v)}
                className={`flex flex-col items-center gap-0.5 transition-colors px-3 py-1 ${showCrop ? 'text-emerald-400' : 'text-white/60 hover:text-white'}`}
                data-testid="crop-toggle-btn">
                <Crop className="w-5 h-5" />
                <span className="text-[10px]">Recadrer</span>
              </button>
              <div className="w-px h-8 bg-white/10" />
              <button onClick={autoAdjust}
                className="flex flex-col items-center gap-0.5 text-amber-400 hover:text-amber-300 transition-colors px-3 py-1"
                data-testid="auto-adjust-btn">
                <Wand2 className="w-5 h-5" />
                <span className="text-[10px]">Auto</span>
              </button>
            </div>

            {/* Action buttons */}
            <div className="p-3 space-y-2">
              <div className="flex gap-2">
                <Button variant="outline" onClick={retake} className="flex-1 gap-2 h-11 border-white/20 text-white hover:bg-white/10 text-sm" data-testid="adjust-retake-btn">
                  <RotateCcw className="w-4 h-4" /> Reprendre
                </Button>
                <Button onClick={finalizeAdjust} className="flex-1 gap-2 h-11 bg-emerald-600 hover:bg-emerald-500 text-sm font-semibold" data-testid="adjust-validate-btn">
                  <Check className="w-4 h-4" /> Valider
                </Button>
              </div>
              <p className="text-white/30 text-[10px] text-center">
                Vous pouvez valider directement, les ajustements sont optionnels
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ====== PREVIEW (post-adjust) ====== */}
      {phase === 'preview' && currentCapture && (
        <div className="flex-1 flex flex-col">
          <div className="flex-1 relative overflow-hidden bg-black flex items-center justify-center p-4">
            <img src={currentCapture} alt="Document scanné" className="max-w-full max-h-full object-contain rounded-lg" data-testid="scanner-preview-img" />
            <div className="absolute top-3 left-3 bg-green-500/90 text-white text-[10px] font-medium px-2 py-1 rounded-full flex items-center gap-1">
              <Check className="w-3 h-3" /> Prêt
            </div>
          </div>
          <div className="p-4 bg-black/80 space-y-2 flex-shrink-0">
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setPhase('adjust')} className="flex-1 gap-2 border-white/20 text-white hover:bg-white/10" data-testid="preview-readjust-btn">
                <Wand2 className="w-4 h-4" /> Réajuster
              </Button>
              <Button onClick={addPageAndContinue} className="flex-1 gap-2 bg-blue-600 hover:bg-blue-700" data-testid="scanner-add-page-btn">
                <Plus className="w-4 h-4" /> Ajouter une page
              </Button>
            </div>
            <div className="flex gap-2">
              {pages.length === 0 ? (
                <Button onClick={confirmSinglePage} className="flex-1 gap-2 h-11" data-testid="scanner-confirm-btn">
                  <Check className="w-4 h-4" /> Utiliser cette photo
                </Button>
              ) : (
                <Button onClick={addPageAndFinish} className="flex-1 gap-2 h-11" data-testid="scanner-finish-multi-btn">
                  <Layers className="w-4 h-4" /> Terminer ({pages.length + 1} pages)
                </Button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ====== PAGES REVIEW ====== */}
      {phase === 'pages' && pages.length > 0 && (
        <div className="flex-1 flex flex-col">
          <PageStrip pages={pages} activeIndex={activePageIndex} onSelect={setActivePageIndex} onRemove={removePage} />
          <div className="flex-1 relative overflow-hidden bg-black flex items-center justify-center p-4">
            <img src={pages[activePageIndex]} alt={`Page ${activePageIndex + 1}`} className="max-w-full max-h-full object-contain rounded-lg" data-testid="pages-active-preview" />
            {pages.length > 1 && (
              <>
                {activePageIndex > 0 && (
                  <button onClick={() => setActivePageIndex(p => p - 1)} className="absolute left-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/60 flex items-center justify-center" data-testid="pages-prev">
                    <ChevronLeft className="w-5 h-5 text-white" />
                  </button>
                )}
                {activePageIndex < pages.length - 1 && (
                  <button onClick={() => setActivePageIndex(p => p + 1)} className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/60 flex items-center justify-center" data-testid="pages-next">
                    <ChevronRight className="w-5 h-5 text-white" />
                  </button>
                )}
              </>
            )}
            <div className="absolute top-3 left-3 bg-accent/90 text-white text-[10px] font-medium px-2 py-1 rounded-full flex items-center gap-1">
              <FileText className="w-3 h-3" /> Page {activePageIndex + 1} / {pages.length}
            </div>
          </div>
          <div className="p-4 bg-black/80 space-y-2 flex-shrink-0">
            <div className="flex gap-2">
              <Button variant="outline" onClick={startCamera} className="flex-1 gap-2 border-white/20 text-white hover:bg-white/10" data-testid="pages-add-more">
                <Plus className="w-4 h-4" /> Ajouter une page
              </Button>
              <Button onClick={generatePdfPreview} className="flex-1 gap-2" data-testid="pages-preview-pdf">
                <Eye className="w-4 h-4" /> Aperçu PDF
              </Button>
            </div>
            <Button onClick={confirmMultiScan} className="w-full gap-2 h-11" data-testid="pages-confirm-multi">
              <Layers className="w-4 h-4" /> Fusionner et analyser ({pages.length} pages)
            </Button>
          </div>
        </div>
      )}

      {/* ====== PDF PREVIEW ====== */}
      {phase === 'pdfPreview' && pdfUrl && (
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-hidden bg-white">
            <iframe src={pdfUrl} title="Aperçu PDF" className="w-full h-full border-0" data-testid="pdf-preview-iframe" />
          </div>
          <div className="p-4 bg-black/80 flex gap-2 flex-shrink-0">
            <Button variant="outline" onClick={() => setPhase('pages')} className="flex-1 gap-2 border-white/20 text-white hover:bg-white/10" data-testid="pdf-preview-back">
              <ChevronLeft className="w-4 h-4" /> Retour
            </Button>
            <Button onClick={confirmMultiScan} className="flex-1 gap-2" data-testid="pdf-preview-confirm">
              <Check className="w-4 h-4" /> Valider et analyser
            </Button>
          </div>
        </div>
      )}

      {/* ====== PROCESSING ====== */}
      {phase === 'processing' && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <Loader2 className="w-12 h-12 text-accent animate-spin" />
          <p className="text-white text-sm">{pages.length > 1 ? `Fusion de ${pages.length} pages...` : 'Traitement en cours...'}</p>
          <p className="text-white/50 text-xs">Amélioration + extraction OCR</p>
        </div>
      )}

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};
