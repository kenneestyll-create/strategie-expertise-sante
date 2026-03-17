import { useState, useRef, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Camera, X, RotateCcw, Check, Smartphone, Sun,
  Eye, Maximize2, ZapOff, Loader2, Plus, Trash2,
  FileText, ChevronLeft, ChevronRight, Layers,
  RotateCw, Wand2, Crop, Contrast, ScanLine, AlertCircle
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import { loadOpenCV, isOpenCVReady, getCV } from '@/utils/opencvLoader';
import { processDocument, reprocessWithCorners } from '@/utils/documentProcessor';

/* ── PDF builder ── */
async function buildPdf(pages) {
  const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  for (let i = 0; i < pages.length; i++) {
    if (i > 0) pdf.addPage();
    const img = new Image();
    img.src = pages[i];
    await new Promise(r => { img.onload = r; });
    const ratio = Math.min(210 / img.width, 297 / img.height);
    const w = img.width * ratio, h = img.height * ratio;
    pdf.addImage(pages[i], 'JPEG', (210 - w) / 2, (297 - h) / 2, w, h);
  }
  return pdf;
}

const FILTERS = [
  { id: 'document', label: 'Document', icon: Contrast },
  { id: 'bw', label: 'Noir & Blanc', icon: FileText },
  { id: 'original', label: 'Original', icon: Eye },
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

/* ── Manual corner adjustment overlay ── */
const CornerAdjuster = ({ corners, setCorners, imageRef }) => {
  const dragging = useRef(null);

  const getPos = useCallback((e) => {
    const rect = imageRef.current?.getBoundingClientRect();
    if (!rect) return null;
    const touch = e.touches ? e.touches[0] : e;
    return {
      x: Math.max(0, Math.min(1, (touch.clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (touch.clientY - rect.top) / rect.height)),
    };
  }, [imageRef]);

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
      if (pos) setCorners(prev => prev.map((c, i) => i === dragging.current ? pos : c));
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

  const points = corners.map(c => `${c.x * 100}%,${c.y * 100}%`).join(' ');
  const labels = ['HG', 'HD', 'BD', 'BG'];

  return (
    <div className="absolute inset-0" data-testid="corner-adjuster">
      <svg className="absolute inset-0 w-full h-full">
        <defs>
          <mask id="cropMask">
            <rect width="100%" height="100%" fill="white" />
            <polygon points={points} fill="black" />
          </mask>
        </defs>
        <rect width="100%" height="100%" fill="rgba(0,0,0,0.45)" mask="url(#cropMask)" />
        <polygon points={points} fill="none" stroke="#22c55e" strokeWidth="2.5" />
      </svg>
      {corners.map((c, i) => (
        <div key={i}
          onMouseDown={(e) => onStart(i, e)}
          onTouchStart={(e) => onStart(i, e)}
          className="absolute w-12 h-12 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center cursor-grab active:cursor-grabbing touch-none select-none"
          style={{ left: `${c.x * 100}%`, top: `${c.y * 100}%` }}
          data-testid={`corner-handle-${i}`}>
          <div className="w-6 h-6 rounded-full bg-emerald-500 border-[3px] border-white shadow-lg shadow-black/50 flex items-center justify-center">
            <span className="text-[7px] font-bold text-white">{labels[i]}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

/* ── Main Scanner ── */
export const DocumentScanner = ({ onCapture, onClose }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const adjustImgRef = useRef(null);

  const [phase, setPhase] = useState('guide');
  const [pages, setPages] = useState([]);
  const [rawCapture, setRawCapture] = useState(null);
  const [processedCapture, setProcessedCapture] = useState(null);
  const [autoDetected, setAutoDetected] = useState(false);
  const [manualCorners, setManualCorners] = useState(null);
  const [showManualMode, setShowManualMode] = useState(false);
  const [filter, setFilter] = useState('document');
  const [activePageIndex, setActivePageIndex] = useState(0);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [facingMode, setFacingMode] = useState('environment');
  const [error, setError] = useState('');
  const [cvReady, setCvReady] = useState(isOpenCVReady());
  const [cvLoading, setCvLoading] = useState(false);
  const [processing, setProcessing] = useState(false);

  /* ── Load OpenCV in background (non-blocking) ── */
  useEffect(() => {
    if (cvReady) return;
    setCvLoading(true);
    loadOpenCV()
      .then(() => { setCvReady(true); setCvLoading(false); })
      .catch(() => { setCvLoading(false); });
  }, [cvReady]);

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
      if (err.name === 'NotAllowedError') setError("Autorisez l'accès à la caméra dans les paramètres.");
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

  /* ── Capture → Auto process ── */
  const capture = useCallback(async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
    setRawCapture(dataUrl);
    stopCamera();

    const cv = getCV();
    if (cv) {
      setPhase('processing');
      setProcessing(true);
      try {
        const result = await processDocument(cv, dataUrl, filter);
        setProcessedCapture(result.resultDataUrl);
        setAutoDetected(result.autoDetected);
        if (result.corners) {
          const img = new Image();
          img.src = dataUrl;
          await new Promise(r => { img.onload = r; });
          setManualCorners(result.corners.map(c => ({
            x: c.x / img.width,
            y: c.y / img.height,
          })));
        } else {
          setManualCorners([
            { x: 0.05, y: 0.05 }, { x: 0.95, y: 0.05 },
            { x: 0.95, y: 0.95 }, { x: 0.05, y: 0.95 },
          ]);
        }
        setShowManualMode(false);
        setPhase('preview');
      } catch (e) {
        console.warn('OpenCV processing error:', e);
        setProcessedCapture(dataUrl);
        setAutoDetected(false);
        setPhase('preview');
      }
      setProcessing(false);
    } else {
      // No OpenCV — use raw image directly
      setProcessedCapture(dataUrl);
      setAutoDetected(false);
      setManualCorners(null);
      setPhase('preview');
    }
  }, [stopCamera, filter]);

  /* ── Re-process with different filter ── */
  const applyFilter = useCallback(async (newFilter) => {
    setFilter(newFilter);
    const cv = getCV();
    if (!cv || !rawCapture) return;
    setProcessing(true);
    try {
      const result = await processDocument(cv, rawCapture, newFilter);
      setProcessedCapture(result.resultDataUrl);
    } catch { /* keep current */ }
    setProcessing(false);
  }, [rawCapture]);

  /* ── Manual corner re-process ── */
  const applyManualCorners = useCallback(async () => {
    const cv = getCV();
    if (!cv || !rawCapture || !manualCorners) return;
    setProcessing(true);
    try {
      const img = new Image();
      img.src = rawCapture;
      await new Promise(r => { img.onload = r; });
      const pixelCorners = manualCorners.map(c => ({
        x: Math.round(c.x * img.width),
        y: Math.round(c.y * img.height),
      }));
      const resultUrl = await reprocessWithCorners(cv, rawCapture, pixelCorners, filter);
      setProcessedCapture(resultUrl);
      setShowManualMode(false);
      setAutoDetected(true);
    } catch { /* keep current */ }
    setProcessing(false);
  }, [rawCapture, manualCorners, filter]);

  /* ── Page management ── */
  const addPageAndContinue = useCallback(() => {
    if (!processedCapture) return;
    setPages(prev => [...prev, processedCapture]);
    setActivePageIndex(pages.length);
    setProcessedCapture(null);
    setRawCapture(null);
    startCamera();
  }, [processedCapture, pages.length, startCamera]);

  const addPageAndFinish = useCallback(() => {
    if (!processedCapture) return;
    const newPages = [...pages, processedCapture];
    setPages(newPages);
    setActivePageIndex(0);
    setProcessedCapture(null);
    setRawCapture(null);
    setPhase('pages');
  }, [processedCapture, pages]);

  const confirmSinglePage = useCallback(async () => {
    if (!processedCapture) return;
    setPhase('finalizing');
    const res = await fetch(processedCapture);
    const blob = await res.blob();
    const file = new File([blob], `scan_${Date.now()}.jpg`, { type: 'image/jpeg' });
    onCapture(file);
  }, [processedCapture, onCapture]);

  const removePage = useCallback((index) => {
    const newPages = pages.filter((_, i) => i !== index);
    setPages(newPages);
    if (newPages.length === 0) startCamera();
    else setActivePageIndex(Math.min(index, newPages.length - 1));
  }, [pages, startCamera]);

  const confirmMultiScan = useCallback(async () => {
    setPhase('finalizing');
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
      setError('Erreur PDF');
      setPhase('pages');
    }
  }, [pages, onCapture, stopCamera]);

  const retake = useCallback(() => {
    setProcessedCapture(null);
    setRawCapture(null);
    setShowManualMode(false);
    startCamera();
  }, [startCamera]);

  /* ── Render ── */
  return (
    <div className="fixed inset-0 z-50 bg-black flex flex-col" data-testid="document-scanner">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-black/80 backdrop-blur-sm flex-shrink-0">
        <h3 className="text-white text-sm font-medium flex items-center gap-2">
          {pages.length > 0 && <span className="bg-accent text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full" data-testid="page-counter">{pages.length}</span>}
          <ScanLine className="w-4 h-4 text-accent" />
          Scanner
        </h3>
        <Button variant="ghost" size="sm" onClick={() => { stopCamera(); onClose(); }} className="text-white hover:bg-white/10" data-testid="scanner-close">
          <X className="w-5 h-5" />
        </Button>
      </div>

      {pages.length > 0 && (phase === 'camera' || phase === 'preview') && (
        <PageStrip pages={pages} activeIndex={-1} onSelect={() => setPhase('pages')} onRemove={() => {}} />
      )}

      {/* ====== GUIDE ====== */}
      {phase === 'guide' && (
        <div className="flex-1 flex flex-col items-center justify-center px-6 gap-5">
          <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center">
            <ScanLine className="w-8 h-8 text-accent" />
          </div>
          <div className="text-center">
            <h2 className="text-white text-lg font-semibold mb-1" data-testid="scanner-title">Scanner un document</h2>
            <p className="text-white/50 text-sm">
              {cvReady ? 'Détection et recadrage automatiques' : cvLoading ? 'Moteur de scan en préparation...' : 'Mode capture simple'}
            </p>
          </div>
          <div className="w-full max-w-xs space-y-2.5">
            {[
              { icon: Smartphone, text: 'Tenez le téléphone droit', color: 'text-blue-400' },
              { icon: Maximize2, text: 'Document entier visible', color: 'text-emerald-400' },
              { icon: Sun, text: 'Bonne luminosité', color: 'text-amber-400' },
              { icon: ZapOff, text: 'Évitez les reflets', color: 'text-purple-400' },
            ].map((tip, i) => (
              <div key={i} className="flex items-center gap-3 p-2.5 rounded-xl bg-white/5 border border-white/10" data-testid={`scanner-tip-${i}`}>
                <tip.icon className={`w-4 h-4 flex-shrink-0 ${tip.color}`} />
                <span className="text-white/80 text-sm">{tip.text}</span>
              </div>
            ))}
          </div>

          {/* Loading indicator (non-blocking) */}
          {cvLoading && (
            <div className="w-full max-w-xs flex items-center gap-2 p-2.5 rounded-xl bg-accent/10 border border-accent/20">
              <Loader2 className="w-4 h-4 text-accent animate-spin flex-shrink-0" />
              <span className="text-accent/80 text-xs">Chargement du moteur de scan avancé...</span>
            </div>
          )}

          {/* OpenCV ready indicator */}
          {cvReady && (
            <div className="w-full max-w-xs flex items-center gap-2 p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20" data-testid="opencv-ready-badge">
              <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span className="text-emerald-400/80 text-xs">Détection automatique activée</span>
            </div>
          )}

          <div className="w-full max-w-xs space-y-2 pt-2">
            <Button onClick={startCamera} className="w-full gap-2 h-12 text-base" data-testid="scanner-start-btn">
              <Camera className="w-5 h-5" /> Ouvrir la caméra
            </Button>
          </div>
          {error && <p className="text-red-400 text-sm text-center max-w-xs" data-testid="scanner-error">{error}</p>}
        </div>
      )}

      {/* ====== CAMERA ====== */}
      {phase === 'camera' && (
        <div className="flex-1 relative overflow-hidden">
          <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" data-testid="scanner-video" />
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute inset-[6%] sm:inset-[10%] rounded-2xl border-2 border-white/70" style={{ boxShadow: '0 0 0 9999px rgba(0,0,0,0.35)' }} />
            <div className="absolute top-[6%] left-[6%] sm:top-[10%] sm:left-[10%] w-8 h-8 border-t-4 border-l-4 border-emerald-400 rounded-tl-lg" />
            <div className="absolute top-[6%] right-[6%] sm:top-[10%] sm:right-[10%] w-8 h-8 border-t-4 border-r-4 border-emerald-400 rounded-tr-lg" />
            <div className="absolute bottom-[6%] left-[6%] sm:bottom-[10%] sm:left-[10%] w-8 h-8 border-b-4 border-l-4 border-emerald-400 rounded-bl-lg" />
            <div className="absolute bottom-[6%] right-[6%] sm:bottom-[10%] sm:right-[10%] w-8 h-8 border-b-4 border-r-4 border-emerald-400 rounded-br-lg" />
            <div className="absolute top-[calc(6%+12px)] sm:top-[calc(10%+12px)] left-0 right-0 text-center">
              <span className="text-white/80 text-xs bg-black/50 px-3 py-1 rounded-full">
                {pages.length === 0 ? 'Cadrez le document' : `Page ${pages.length + 1}`}
              </span>
            </div>
          </div>
          {/* Controls */}
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

      {/* ====== PROCESSING ====== */}
      {phase === 'processing' && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <div className="relative">
            <Loader2 className="w-14 h-14 text-accent animate-spin" />
            <ScanLine className="w-6 h-6 text-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
          </div>
          <p className="text-white text-sm font-medium">Détection du document...</p>
          <p className="text-white/40 text-xs">Recadrage et amélioration automatiques</p>
        </div>
      )}

      {/* ====== PREVIEW (post-processing) ====== */}
      {phase === 'preview' && processedCapture && (
        <div className="flex-1 flex flex-col min-h-0">
          {/* Image */}
          <div className="flex-1 relative overflow-hidden bg-neutral-900 flex items-center justify-center p-3 min-h-0">
            {showManualMode ? (
              <div className="relative max-w-full max-h-full" ref={adjustImgRef}>
                <img src={rawCapture} alt="Original" className="max-w-full max-h-full object-contain rounded-lg select-none" draggable={false} />
                {manualCorners && (
                  <CornerAdjuster corners={manualCorners} setCorners={setManualCorners} imageRef={adjustImgRef} />
                )}
              </div>
            ) : (
              <img src={processedCapture} alt="Document scanné" className="max-w-full max-h-full object-contain rounded-lg" data-testid="preview-image" />
            )}

            {/* Status badge */}
            <div className="absolute top-2 left-2 flex gap-1.5">
              {processing && (
                <span className="bg-amber-500/90 text-white text-[10px] font-medium px-2 py-1 rounded-full flex items-center gap-1">
                  <Loader2 className="w-3 h-3 animate-spin" /> Traitement...
                </span>
              )}
              {!processing && autoDetected && !showManualMode && (
                <span className="bg-emerald-500/90 text-white text-[10px] font-medium px-2 py-1 rounded-full flex items-center gap-1" data-testid="auto-detected-badge">
                  <Check className="w-3 h-3" /> Document détecté
                </span>
              )}
              {!processing && !autoDetected && !showManualMode && (
                <span className="bg-amber-500/80 text-white text-[10px] font-medium px-2 py-1 rounded-full flex items-center gap-1" data-testid="manual-fallback-badge">
                  <AlertCircle className="w-3 h-3" /> Ajustez manuellement si besoin
                </span>
              )}
              {showManualMode && (
                <span className="bg-blue-500/90 text-white text-[10px] font-medium px-2 py-1 rounded-full flex items-center gap-1">
                  <Crop className="w-3 h-3" /> Déplacez les coins verts
                </span>
              )}
            </div>
          </div>

          {/* Tools */}
          <div className="bg-black/90 border-t border-white/10 flex-shrink-0">
            {/* Filters */}
            <div className="flex items-center justify-center gap-2 px-4 py-2 border-b border-white/5">
              {FILTERS.map(f => (
                <button key={f.id} onClick={() => applyFilter(f.id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                    filter === f.id ? 'bg-emerald-500 text-white' : 'bg-white/8 text-white/60 hover:bg-white/15'
                  }`}
                  disabled={processing}
                  data-testid={`filter-${f.id}`}>
                  <f.icon className="w-3.5 h-3.5" />
                  {f.label}
                </button>
              ))}
              <div className="w-px h-6 bg-white/10 mx-1" />
              {!showManualMode ? (
                <button onClick={() => setShowManualMode(true)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-white/8 text-white/60 hover:bg-white/15 transition-all"
                  data-testid="manual-crop-btn">
                  <Crop className="w-3.5 h-3.5" />
                  Recadrer
                </button>
              ) : (
                <button onClick={applyManualCorners}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-emerald-500 text-white transition-all"
                  disabled={processing}
                  data-testid="apply-crop-btn">
                  <Check className="w-3.5 h-3.5" />
                  Appliquer
                </button>
              )}
            </div>

            {/* Actions */}
            <div className="p-3 space-y-2">
              <div className="flex gap-2">
                <Button variant="outline" onClick={retake} className="flex-1 gap-2 h-11 border-white/20 text-white hover:bg-white/10 text-sm" data-testid="preview-retake-btn">
                  <RotateCcw className="w-4 h-4" /> Reprendre
                </Button>
                <Button onClick={addPageAndContinue} className="flex-1 gap-2 h-11 bg-blue-600 hover:bg-blue-700 text-sm" data-testid="preview-add-page-btn">
                  <Plus className="w-4 h-4" /> Page suivante
                </Button>
              </div>
              {pages.length === 0 ? (
                <Button onClick={confirmSinglePage} disabled={processing} className="w-full gap-2 h-12 text-sm font-semibold bg-emerald-600 hover:bg-emerald-500" data-testid="preview-confirm-btn">
                  <Check className="w-5 h-5" /> Valider ce document
                </Button>
              ) : (
                <Button onClick={addPageAndFinish} disabled={processing} className="w-full gap-2 h-12 text-sm font-semibold bg-emerald-600 hover:bg-emerald-500" data-testid="preview-finish-btn">
                  <Layers className="w-5 h-5" /> Terminer ({pages.length + 1} pages)
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
            <div className="absolute top-3 left-3 bg-accent/90 text-white text-[10px] font-medium px-2 py-1 rounded-full">
              Page {activePageIndex + 1} / {pages.length}
            </div>
          </div>
          <div className="p-4 bg-black/80 space-y-2 flex-shrink-0">
            <div className="flex gap-2">
              <Button variant="outline" onClick={startCamera} className="flex-1 gap-2 border-white/20 text-white hover:bg-white/10" data-testid="pages-add-more">
                <Plus className="w-4 h-4" /> Ajouter une page
              </Button>
              <Button onClick={async () => {
                setPhase('finalizing');
                const pdf = await buildPdf(pages);
                const blob = pdf.output('blob');
                if (pdfUrl) URL.revokeObjectURL(pdfUrl);
                setPdfUrl(URL.createObjectURL(blob));
                setPhase('pdfPreview');
              }} className="flex-1 gap-2" data-testid="pages-preview-pdf">
                <Eye className="w-4 h-4" /> Aperçu PDF
              </Button>
            </div>
            <Button onClick={confirmMultiScan} className="w-full gap-2 h-12 bg-emerald-600 hover:bg-emerald-500 font-semibold" data-testid="pages-confirm-multi">
              <Layers className="w-4 h-4" /> Fusionner ({pages.length} pages)
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
            <Button onClick={confirmMultiScan} className="flex-1 gap-2 bg-emerald-600 hover:bg-emerald-500" data-testid="pdf-preview-confirm">
              <Check className="w-4 h-4" /> Valider
            </Button>
          </div>
        </div>
      )}

      {/* ====== FINALIZING ====== */}
      {phase === 'finalizing' && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <Loader2 className="w-12 h-12 text-emerald-400 animate-spin" />
          <p className="text-white text-sm">Préparation du document...</p>
        </div>
      )}

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};
