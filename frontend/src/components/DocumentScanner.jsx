import { useState, useRef, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Camera, X, RotateCcw, Check, Smartphone, Sun,
  Eye, Maximize2, ZapOff, Loader2, Plus, Trash2,
  FileText, ChevronLeft, ChevronRight, Layers
} from 'lucide-react';
import { jsPDF } from 'jspdf';

const GUIDE_TIPS = [
  { icon: Smartphone, text: 'Tenez le téléphone bien droit', color: 'text-blue-500' },
  { icon: Maximize2, text: 'Document entièrement visible', color: 'text-emerald-500' },
  { icon: Sun, text: 'Bonne luminosité', color: 'text-amber-500' },
  { icon: ZapOff, text: 'Évitez les reflets', color: 'text-purple-500' },
];

function enhanceImage(canvas) {
  const ctx = canvas.getContext('2d');
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;
  const contrast = 1.3;
  const brightness = 10;
  for (let i = 0; i < data.length; i += 4) {
    data[i] = Math.min(255, Math.max(0, (data[i] - 128) * contrast + 128 + brightness));
    data[i + 1] = Math.min(255, Math.max(0, (data[i + 1] - 128) * contrast + 128 + brightness));
    data[i + 2] = Math.min(255, Math.max(0, (data[i + 2] - 128) * contrast + 128 + brightness));
  }
  ctx.putImageData(imageData, 0, 0);
  const w = canvas.width, h = canvas.height;
  const src = ctx.getImageData(0, 0, w, h);
  const dst = ctx.createImageData(w, h);
  const kernel = [0, -0.5, 0, -0.5, 3, -0.5, 0, -0.5, 0];
  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      for (let c = 0; c < 3; c++) {
        let val = 0;
        for (let ky = -1; ky <= 1; ky++) {
          for (let kx = -1; kx <= 1; kx++) {
            val += src.data[((y + ky) * w + (x + kx)) * 4 + c] * kernel[(ky + 1) * 3 + (kx + 1)];
          }
        }
        dst.data[(y * w + x) * 4 + c] = Math.min(255, Math.max(0, val));
      }
      dst.data[(y * w + x) * 4 + 3] = 255;
    }
  }
  ctx.putImageData(dst, 0, 0);
  return canvas;
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
    const w = img.width * ratio;
    const h = img.height * ratio;
    const x = (A4_W - w) / 2;
    const y = (A4_H - h) / 2;
    pdf.addImage(pages[i], 'JPEG', x, y, w, h);
  }
  return pdf;
}

// Page thumbnail strip
const PageStrip = ({ pages, activeIndex, onSelect, onRemove }) => (
  <div className="flex gap-2 px-4 py-2 overflow-x-auto bg-black/60 backdrop-blur-sm" data-testid="page-strip">
    {pages.map((src, i) => (
      <div
        key={i}
        onClick={() => onSelect(i)}
        className={`relative flex-shrink-0 w-14 h-20 rounded-lg overflow-hidden border-2 cursor-pointer transition-all ${
          i === activeIndex ? 'border-accent scale-105' : 'border-white/20 opacity-70'
        }`}
        data-testid={`page-thumb-${i}`}
      >
        <img src={src} alt={`Page ${i + 1}`} className="w-full h-full object-cover" />
        <span className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-[9px] text-center py-0.5">{i + 1}</span>
        {pages.length > 1 && (
          <button
            onClick={(e) => { e.stopPropagation(); onRemove(i); }}
            className="absolute top-0.5 right-0.5 w-4 h-4 rounded-full bg-red-500 flex items-center justify-center"
            data-testid={`page-remove-${i}`}
          >
            <X className="w-2.5 h-2.5 text-white" />
          </button>
        )}
      </div>
    ))}
  </div>
);

export const DocumentScanner = ({ onCapture, onClose }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  // guide | camera | preview | pages | pdfPreview | processing
  const [phase, setPhase] = useState('guide');
  const [pages, setPages] = useState([]);
  const [currentCapture, setCurrentCapture] = useState(null);
  const [activePageIndex, setActivePageIndex] = useState(0);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [error, setError] = useState('');
  const [facingMode, setFacingMode] = useState('environment');

  const startCamera = useCallback(async () => {
    setError('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 1920 }, height: { ideal: 1080 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setPhase('camera');
    } catch (err) {
      if (err.name === 'NotAllowedError') setError('Accès caméra refusé. Autorisez l\'accès dans les paramètres du navigateur.');
      else if (err.name === 'NotFoundError') setError('Aucune caméra détectée sur cet appareil.');
      else setError(`Erreur caméra : ${err.message}`);
    }
  }, [facingMode]);

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

  const capture = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    enhanceImage(canvas);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
    setCurrentCapture(dataUrl);
    stopCamera();
    setPhase('preview');
  }, [stopCamera]);

  const addPageAndContinue = useCallback(() => {
    if (!currentCapture) return;
    const newPages = [...pages, currentCapture];
    setPages(newPages);
    setActivePageIndex(newPages.length - 1);
    setCurrentCapture(null);
    startCamera();
  }, [currentCapture, pages, startCamera]);

  const addPageAndFinish = useCallback(() => {
    if (!currentCapture) return;
    const newPages = [...pages, currentCapture];
    setPages(newPages);
    setActivePageIndex(0);
    setCurrentCapture(null);
    setPhase('pages');
  }, [currentCapture, pages]);

  const confirmSinglePage = useCallback(async () => {
    if (!currentCapture) return;
    setPhase('processing');
    const res = await fetch(currentCapture);
    const blob = await res.blob();
    const file = new File([blob], `scan_${Date.now()}.jpg`, { type: 'image/jpeg' });
    stopCamera();
    onCapture(file);
  }, [currentCapture, onCapture, stopCamera]);

  const removePage = useCallback((index) => {
    const newPages = pages.filter((_, i) => i !== index);
    setPages(newPages);
    if (newPages.length === 0) {
      startCamera();
    } else {
      setActivePageIndex(Math.min(index, newPages.length - 1));
    }
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
      // Also pass the individual page images for OCR (Tesseract needs images)
      const imageFiles = await Promise.all(pages.map(async (dataUrl, i) => {
        const res = await fetch(dataUrl);
        const b = await res.blob();
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
    startCamera();
  }, [startCamera]);

  const switchCamera = useCallback(() => {
    stopCamera();
    setFacingMode(prev => prev === 'environment' ? 'user' : 'environment');
    setTimeout(() => startCamera(), 100);
  }, [stopCamera, startCamera]);

  return (
    <div className="fixed inset-0 z-50 bg-black/95 flex flex-col" data-testid="document-scanner">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-black/80 backdrop-blur-sm">
        <h3 className="text-white text-sm font-medium flex items-center gap-2">
          {pages.length > 0 && <span className="bg-accent text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full" data-testid="page-counter">{pages.length}</span>}
          Scanner un document
        </h3>
        <Button variant="ghost" size="sm" onClick={() => { stopCamera(); onClose(); }} className="text-white hover:bg-white/10" data-testid="scanner-close">
          <X className="w-5 h-5" />
        </Button>
      </div>

      {/* Page thumbnails strip (visible when we have pages and in camera/preview) */}
      {pages.length > 0 && (phase === 'camera' || phase === 'preview') && (
        <PageStrip pages={pages} activeIndex={-1} onSelect={() => {}} onRemove={() => {}} />
      )}

      {/* ====== GUIDE PHASE ====== */}
      {phase === 'guide' && (
        <div className="flex-1 flex flex-col items-center justify-center px-6 gap-6">
          <div className="w-20 h-20 rounded-full bg-accent/20 flex items-center justify-center">
            <Camera className="w-10 h-10 text-accent" />
          </div>
          <div className="text-center">
            <h2 className="text-white text-lg font-semibold mb-1">Scanner un document</h2>
            <p className="text-white/60 text-sm">Pour un meilleur résultat, suivez ces conseils :</p>
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
              Mode multi-pages : scannez plusieurs pages, elles seront fusionnées en un seul PDF.
            </p>
          </div>
          <Button onClick={startCamera} className="w-full max-w-xs gap-2 h-12 text-base" data-testid="scanner-start-btn">
            <Camera className="w-5 h-5" /> Ouvrir la caméra
          </Button>
          {error && <p className="text-red-400 text-sm text-center max-w-xs" data-testid="scanner-error">{error}</p>}
        </div>
      )}

      {/* ====== CAMERA PHASE ====== */}
      {phase === 'camera' && (
        <div className="flex-1 relative overflow-hidden">
          <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" data-testid="scanner-video" />
          {/* Guide overlay */}
          <div className="absolute inset-0 pointer-events-none" data-testid="scanner-overlay">
            <div className="absolute inset-0 bg-black/40" />
            <div className="absolute inset-[8%] sm:inset-[12%] rounded-2xl border-2 border-white/80 bg-transparent" style={{ boxShadow: '0 0 0 9999px rgba(0,0,0,0.4)' }} />
            <div className="absolute top-[8%] left-[8%] sm:top-[12%] sm:left-[12%] w-8 h-8 border-t-4 border-l-4 border-accent rounded-tl-lg" />
            <div className="absolute top-[8%] right-[8%] sm:top-[12%] sm:right-[12%] w-8 h-8 border-t-4 border-r-4 border-accent rounded-tr-lg" />
            <div className="absolute bottom-[8%] left-[8%] sm:bottom-[12%] sm:left-[12%] w-8 h-8 border-b-4 border-l-4 border-accent rounded-bl-lg" />
            <div className="absolute bottom-[8%] right-[8%] sm:bottom-[12%] sm:right-[12%] w-8 h-8 border-b-4 border-r-4 border-accent rounded-br-lg" />
            <div className="absolute top-[calc(8%+12px)] sm:top-[calc(12%+12px)] left-0 right-0 text-center">
              <span className="text-white/80 text-xs bg-black/50 px-3 py-1 rounded-full">
                {pages.length === 0 ? 'Centrez le document dans le cadre' : `Page ${pages.length + 1} — Centrez la page suivante`}
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
              <Button variant="ghost" size="sm" onClick={() => { stopCamera(); setPhase('pages'); }} className="text-white hover:bg-white/10 rounded-full w-12 h-12 text-xs" data-testid="scanner-done-camera">
                <Check className="w-5 h-5" />
              </Button>
            ) : (
              <div className="w-12 h-12" />
            )}
          </div>
        </div>
      )}

      {/* ====== PREVIEW PHASE (single capture) ====== */}
      {phase === 'preview' && currentCapture && (
        <div className="flex-1 flex flex-col">
          <div className="flex-1 relative overflow-hidden bg-black flex items-center justify-center p-4">
            <img src={currentCapture} alt="Document scanné" className="max-w-full max-h-full object-contain rounded-lg" data-testid="scanner-preview-img" />
            <div className="absolute top-3 left-3 bg-green-500/90 text-white text-[10px] font-medium px-2 py-1 rounded-full flex items-center gap-1">
              <Eye className="w-3 h-3" /> Contraste et netteté améliorés
            </div>
          </div>
          <div className="p-4 bg-black/80 space-y-2">
            {/* Multi-page action row */}
            <div className="flex gap-2">
              <Button variant="outline" onClick={retake} className="flex-1 gap-2 border-white/20 text-white hover:bg-white/10" data-testid="scanner-retake-btn">
                <RotateCcw className="w-4 h-4" /> Reprendre
              </Button>
              <Button onClick={addPageAndContinue} className="flex-1 gap-2 bg-blue-600 hover:bg-blue-700" data-testid="scanner-add-page-btn">
                <Plus className="w-4 h-4" /> Ajouter une page
              </Button>
            </div>
            <div className="flex gap-2">
              {pages.length === 0 ? (
                <Button onClick={confirmSinglePage} className="flex-1 gap-2" data-testid="scanner-confirm-btn">
                  <Check className="w-4 h-4" /> Utiliser cette photo
                </Button>
              ) : (
                <Button onClick={addPageAndFinish} className="flex-1 gap-2" data-testid="scanner-finish-multi-btn">
                  <Layers className="w-4 h-4" /> Terminer ({pages.length + 1} pages)
                </Button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ====== PAGES REVIEW PHASE (multi-scan) ====== */}
      {phase === 'pages' && pages.length > 0 && (
        <div className="flex-1 flex flex-col">
          {/* Page thumbnails */}
          <PageStrip pages={pages} activeIndex={activePageIndex} onSelect={setActivePageIndex} onRemove={removePage} />
          {/* Active page preview */}
          <div className="flex-1 relative overflow-hidden bg-black flex items-center justify-center p-4">
            <img src={pages[activePageIndex]} alt={`Page ${activePageIndex + 1}`} className="max-w-full max-h-full object-contain rounded-lg" data-testid="pages-active-preview" />
            {/* Page nav arrows */}
            {pages.length > 1 && (
              <>
                {activePageIndex > 0 && (
                  <button onClick={() => setActivePageIndex(prev => prev - 1)} className="absolute left-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/60 flex items-center justify-center" data-testid="pages-prev">
                    <ChevronLeft className="w-5 h-5 text-white" />
                  </button>
                )}
                {activePageIndex < pages.length - 1 && (
                  <button onClick={() => setActivePageIndex(prev => prev + 1)} className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/60 flex items-center justify-center" data-testid="pages-next">
                    <ChevronRight className="w-5 h-5 text-white" />
                  </button>
                )}
              </>
            )}
            <div className="absolute top-3 left-3 bg-accent/90 text-white text-[10px] font-medium px-2 py-1 rounded-full flex items-center gap-1">
              <FileText className="w-3 h-3" /> Page {activePageIndex + 1} / {pages.length}
            </div>
          </div>
          {/* Actions */}
          <div className="p-4 bg-black/80 space-y-2">
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

      {/* ====== PDF PREVIEW PHASE ====== */}
      {phase === 'pdfPreview' && pdfUrl && (
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-hidden bg-white">
            <iframe src={pdfUrl} title="Aperçu PDF" className="w-full h-full border-0" data-testid="pdf-preview-iframe" />
          </div>
          <div className="p-4 bg-black/80 flex gap-2">
            <Button variant="outline" onClick={() => setPhase('pages')} className="flex-1 gap-2 border-white/20 text-white hover:bg-white/10" data-testid="pdf-preview-back">
              <ChevronLeft className="w-4 h-4" /> Retour aux pages
            </Button>
            <Button onClick={confirmMultiScan} className="flex-1 gap-2" data-testid="pdf-preview-confirm">
              <Check className="w-4 h-4" /> Valider et analyser
            </Button>
          </div>
        </div>
      )}

      {/* ====== PROCESSING PHASE ====== */}
      {phase === 'processing' && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <Loader2 className="w-12 h-12 text-accent animate-spin" />
          <p className="text-white text-sm">
            {pages.length > 1 ? `Fusion de ${pages.length} pages et analyse OCR GPT-4o...` : 'Traitement du document en cours...'}
          </p>
          <p className="text-white/50 text-xs">Amélioration de l'image + extraction OCR GPT-4o</p>
        </div>
      )}

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};
