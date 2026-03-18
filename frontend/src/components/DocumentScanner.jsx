import { useState, useRef, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Camera, X, RotateCcw, Check, Smartphone, Sun,
  Eye, Maximize2, ZapOff, Loader2, Plus,
  FileText, ChevronLeft, ChevronRight, Layers,
  Contrast, ScanLine, RotateCw, ImageUp
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import { useScannerWorker } from '@/hooks/useScannerWorker';

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

const PageStrip = ({ pages, activeIndex, onSelect, onRemove }) => (
  <div className="flex gap-2 px-3 py-2 bg-black/70 overflow-x-auto flex-shrink-0" data-testid="page-strip">
    {pages.map((url, i) => (
      <div key={i} onClick={() => onSelect(i)} className={`relative flex-shrink-0 w-14 h-18 rounded-lg overflow-hidden border-2 cursor-pointer ${i === activeIndex ? 'border-accent' : 'border-white/20'}`}>
        <img src={url} alt={`P${i + 1}`} className="w-full h-full object-cover" />
        <div className="absolute top-0 left-0 bg-black/60 text-white text-[9px] px-1 rounded-br">{i + 1}</div>
        {onRemove && <button onClick={(e) => { e.stopPropagation(); onRemove(i); }} className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-red-500 text-white rounded-full text-[10px] flex items-center justify-center">x</button>}
      </div>
    ))}
  </div>
);

/* ====== MAIN SCANNER ====== */
export const DocumentScanner = ({ onCapture, onClose }) => {
  const cameraInputRef = useRef(null);
  const galleryInputRef = useRef(null);

  const { previewUrl, isReady, isProcessing, error: workerError, scan, filter, rotate, save, reset } = useScannerWorker();

  const [phase, setPhase] = useState('guide');
  const [isSimpleMode, setIsSimpleMode] = useState(false);
  const [pages, setPages] = useState([]);
  const [activePageIndex, setActivePageIndex] = useState(0);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [error, setError] = useState('');
  const [activeFilter, setActiveFilter] = useState('original');

  useEffect(() => () => { if (pdfUrl) URL.revokeObjectURL(pdfUrl); }, [pdfUrl]);

  useEffect(() => {
    if (previewUrl && phase === 'processing') setPhase('preview');
  }, [previewUrl, phase]);

  useEffect(() => { if (workerError) setError(workerError); }, [workerError]);

  /* -- Send blob to worker -- */
  const processBlob = useCallback((blob) => {
    setPhase('processing');
    setError('');
    setActiveFilter('original');
    scan(blob);
  }, [scan]);

  /* ====== PHOTO via appareil natif ====== */
  const handleCameraCapture = useCallback((e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = '';
    processBlob(file);
  }, [processBlob]);

  /* ====== PHOTO depuis galerie ====== */
  const handleGalleryInput = useCallback((e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = '';
    processBlob(file);
  }, [processBlob]);

  /* ====== Ouvrir l'appareil photo natif ====== */
  const openNativeCamera = useCallback(() => {
    cameraInputRef.current?.click();
  }, []);

  /* ====== FILTER / ROTATE ====== */
  const handleFilter = useCallback((f) => { if (isProcessing) return; setActiveFilter(f); filter(f); }, [filter, isProcessing]);
  const handleRotate = useCallback((dir) => { if (isProcessing) return; rotate(dir); }, [rotate, isProcessing]);

  /* ====== PAGE MANAGEMENT ====== */
  const addPageAndContinue = useCallback(() => {
    if (!previewUrl) return;
    setPages(p => [...p, previewUrl]);
    setActivePageIndex(pages.length);
    reset();
    // Rouvrir l'appareil photo natif pour la page suivante
    setTimeout(() => openNativeCamera(), 100);
  }, [previewUrl, pages.length, reset, openNativeCamera]);

  const addPageAndFinish = useCallback(() => {
    if (!previewUrl) return;
    setPages(p => [...p, previewUrl]);
    reset(); setPhase('pages');
  }, [previewUrl, reset]);

  const confirmSingle = useCallback(async () => {
    if (!previewUrl) return;
    setPhase('finalizing');
    try {
      const buf = await save();
      onCapture(new File([buf], `scan_${Date.now()}.jpg`, { type: 'image/jpeg' }));
    } catch (err) { setError('Erreur sauvegarde: ' + err.message); setPhase('preview'); }
  }, [previewUrl, save, onCapture]);

  const removePage = useCallback((i) => {
    const np = pages.filter((_, j) => j !== i);
    setPages(np);
    if (!np.length) setPhase('guide'); else setActivePageIndex(Math.min(i, np.length - 1));
  }, [pages]);

  const confirmMulti = useCallback(async () => {
    setPhase('finalizing');
    try {
      const pdf = await buildPdf(pages);
      const b = pdf.output('blob');
      const imgs = await Promise.all(pages.map(async (u, i) => {
        const r = await fetch(u); const bl = await r.blob();
        return new File([bl], `page${i + 1}.jpg`, { type: 'image/jpeg' });
      }));
      onCapture(new File([b], `scan_${pages.length}p_${Date.now()}.pdf`, { type: 'application/pdf' }), imgs);
    } catch { setError('Erreur PDF'); setPhase('pages'); }
  }, [pages, onCapture]);

  const retake = useCallback(() => {
    reset();
    setPhase('guide');
  }, [reset]);

  /* ====== RENDER ====== */
  return (
    <div className="fixed inset-0 bg-black flex flex-col" style={{ zIndex: 999999 }} data-testid="document-scanner">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-black/80 backdrop-blur-sm flex-shrink-0">
        <h3 className="text-white text-sm font-semibold flex items-center gap-2">
          {pages.length > 0 && <span className="bg-accent text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full" data-testid="page-counter">{pages.length}</span>}
          <ScanLine className="w-4 h-4 text-emerald-400" />
          <span>CamScanner</span>
          <span className={`text-[10px] font-normal ml-1 ${isSimpleMode ? 'text-amber-400' : 'text-emerald-400'}`}>
            {isSimpleMode ? '(Simple)' : '(Avance)'}
          </span>
        </h3>
        <Button variant="ghost" size="sm" onClick={onClose}
          className="text-white hover:bg-white/10 min-h-[44px] min-w-[44px]" data-testid="scanner-close">
          <X className="w-5 h-5" />
        </Button>
      </div>

      {!isSimpleMode && pages.length > 0 && phase === 'preview' && (
        <PageStrip pages={pages} activeIndex={-1} onSelect={() => setPhase('pages')} />
      )}

      {/* === GUIDE === */}
      {phase === 'guide' && (
        <div className="flex-1 flex flex-col items-center justify-center px-6 gap-5 overflow-y-auto">
          <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center">
            <ScanLine className="w-8 h-8 text-emerald-400" />
          </div>
          <div className="text-center">
            <h2 className="text-white text-lg font-semibold mb-1" data-testid="scanner-title">CamScanner</h2>
            <p className="text-white/50 text-sm">Appareil photo natif — qualite maximale</p>
          </div>
          <div className="w-full max-w-xs space-y-2.5">
            {[
              { icon: Smartphone, text: 'Tenez le telephone bien droit', color: 'text-blue-400' },
              { icon: Maximize2, text: 'Tout le document doit etre visible', color: 'text-emerald-400' },
              { icon: Sun, text: 'Bonne luminosite, evitez les ombres', color: 'text-amber-400' },
              { icon: ZapOff, text: 'Evitez les reflets et le flash', color: 'text-purple-400' },
            ].map((tip, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10" data-testid={`scanner-tip-${i}`}>
                <tip.icon className={`w-5 h-5 flex-shrink-0 ${tip.color}`} />
                <span className="text-white/80 text-sm">{tip.text}</span>
              </div>
            ))}
          </div>
          <div className="w-full max-w-xs flex items-center gap-2 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20" data-testid="scanner-ready-badge">
            {isReady
              ? <Check className="w-5 h-5 text-emerald-400 flex-shrink-0" />
              : <Loader2 className="w-5 h-5 text-amber-400 flex-shrink-0 animate-spin" />}
            <span className={`text-xs font-medium ${isReady ? 'text-emerald-400/80' : 'text-amber-400/80'}`}>
              {isReady
                ? (isSimpleMode ? 'Mode simple — capture photo directe' : 'Mode avance — filtres, rotation, multi-pages')
                : 'Initialisation du scanner...'}
            </span>
          </div>
          <div className="w-full max-w-xs pt-2 space-y-2">
            <Button onClick={openNativeCamera} className="w-full gap-2 h-14 text-base font-semibold" data-testid="scanner-start-btn">
              <Camera className="w-5 h-5" /> Prendre une photo
            </Button>
            <Button variant="outline" onClick={() => galleryInputRef.current?.click()}
              className="w-full gap-2 h-12 text-sm border-white/20 text-white hover:bg-white/10" data-testid="scanner-file-btn">
              <ImageUp className="w-5 h-5" /> Choisir depuis la galerie
            </Button>
            <button onClick={() => setIsSimpleMode(p => !p)}
              className="w-full text-center text-white/40 text-xs py-3 min-h-[44px] hover:text-white/60 transition-colors" data-testid="toggle-mode-btn">
              {isSimpleMode ? 'Activer le mode avance (filtres, rotation...)' : 'Revenir au mode simple'}
            </button>
          </div>
          {error && <p className="text-red-400 text-sm text-center max-w-xs" data-testid="scanner-error">{error}</p>}
        </div>
      )}

      {/* === PROCESSING === */}
      {phase === 'processing' && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <Loader2 className="w-14 h-14 text-emerald-400 animate-spin" />
          <p className="text-white text-base font-medium">Traitement de l'image...</p>
          <p className="text-white/40 text-xs">OffscreenCanvas — UI non bloquee</p>
        </div>
      )}

      {/* === PREVIEW === */}
      {phase === 'preview' && previewUrl && (
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex-1 overflow-auto bg-neutral-900 flex items-center justify-center p-2 min-h-0">
            <img
              src={previewUrl}
              alt="Preview"
              data-testid="preview-image"
              style={{ width: '100%', height: 'auto', objectFit: 'contain', display: 'block' }}
            />
            {isProcessing && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
              </div>
            )}
          </div>

          <div className="bg-black/90 border-t border-white/10 flex-shrink-0">
            {!isSimpleMode && isReady && (
              <div className="flex items-center gap-1.5 px-3 py-2 border-b border-white/5 overflow-x-auto" data-testid="advanced-toolbar">
                {[
                  { id: 'bw', label: 'N&B', icon: Contrast },
                  { id: 'enhanced', label: 'Contraste+', icon: Eye },
                  { id: 'original', label: 'Original', icon: FileText },
                ].map(f => (
                  <button key={f.id} onClick={() => handleFilter(f.id)} disabled={isProcessing}
                    className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium transition-all min-h-[40px] whitespace-nowrap ${activeFilter === f.id ? 'bg-emerald-500 text-white' : 'bg-white/8 text-white/60 hover:bg-white/15'} ${isProcessing ? 'opacity-40' : ''}`}
                    data-testid={`filter-${f.id}`}>
                    <f.icon className="w-3.5 h-3.5" /> {f.label}
                  </button>
                ))}
                <div className="w-px h-7 bg-white/10 mx-0.5 flex-shrink-0" />
                <button onClick={() => handleRotate('left')} disabled={isProcessing}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium bg-white/8 text-white/60 hover:bg-white/15 min-h-[40px] ${isProcessing ? 'opacity-30' : ''}`}
                  data-testid="rotate-left-btn">
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
                <button onClick={() => handleRotate('right')} disabled={isProcessing}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium bg-white/8 text-white/60 hover:bg-white/15 min-h-[40px] ${isProcessing ? 'opacity-30' : ''}`}
                  data-testid="rotate-right-btn">
                  <RotateCw className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            <div className="p-3 space-y-2">
              {isSimpleMode ? (
                <>
                  <Button onClick={confirmSingle} disabled={isProcessing} className="w-full gap-2 h-14 text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 min-h-[56px]" data-testid="preview-confirm-btn">
                    <Check className="w-5 h-5" /> Valider / Sauvegarder
                  </Button>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={retake} className="flex-1 gap-2 h-12 border-white/20 text-white hover:bg-white/10 text-sm min-h-[48px]" data-testid="preview-retake-btn">
                      <RotateCcw className="w-4 h-4" /> Reprendre
                    </Button>
                    <Button variant="outline" onClick={() => setIsSimpleMode(false)}
                      className="flex-1 gap-2 h-12 border-white/20 text-white hover:bg-white/10 text-sm min-h-[48px]" data-testid="switch-advanced-btn">
                      <Eye className="w-4 h-4" /> Mode avance
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  {pages.length === 0 ? (
                    <Button onClick={confirmSingle} disabled={isProcessing} className="w-full gap-2 h-14 text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 min-h-[56px]" data-testid="preview-confirm-btn">
                      <Check className="w-5 h-5" /> Valider / Sauvegarder
                    </Button>
                  ) : (
                    <Button onClick={addPageAndFinish} disabled={isProcessing} className="w-full gap-2 h-14 text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 min-h-[56px]" data-testid="preview-finish-btn">
                      <Layers className="w-5 h-5" /> Terminer ({pages.length + 1} pages)
                    </Button>
                  )}
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={retake} className="flex-1 gap-2 h-12 border-white/20 text-white hover:bg-white/10 text-sm min-h-[48px]" data-testid="preview-retake-btn">
                      <RotateCcw className="w-4 h-4" /> Reprendre
                    </Button>
                    <Button variant="outline" onClick={addPageAndContinue} disabled={isProcessing} className="flex-1 gap-2 h-12 border-white/20 text-white hover:bg-white/10 text-sm min-h-[48px]" data-testid="preview-add-page-btn">
                      <Plus className="w-4 h-4" /> Page suivante
                    </Button>
                  </div>
                  <button onClick={() => setIsSimpleMode(true)}
                    className="w-full text-center text-white/40 text-xs py-2 min-h-[36px] hover:text-white/60 transition-colors" data-testid="switch-simple-btn">
                    Revenir au mode simple
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* === PAGES === */}
      {phase === 'pages' && pages.length > 0 && (
        <div className="flex-1 flex flex-col">
          <PageStrip pages={pages} activeIndex={activePageIndex} onSelect={setActivePageIndex} onRemove={removePage} />
          <div className="flex-1 relative overflow-hidden bg-black flex items-center justify-center p-4">
            <img src={pages[activePageIndex]} alt={`Page ${activePageIndex + 1}`} style={{ width: '100%', height: 'auto', objectFit: 'contain' }} data-testid="pages-active-preview" />
            {pages.length > 1 && activePageIndex > 0 && <button onClick={() => setActivePageIndex(p => p - 1)} className="absolute left-2 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/60 flex items-center justify-center"><ChevronLeft className="w-5 h-5 text-white" /></button>}
            {pages.length > 1 && activePageIndex < pages.length - 1 && <button onClick={() => setActivePageIndex(p => p + 1)} className="absolute right-2 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/60 flex items-center justify-center"><ChevronRight className="w-5 h-5 text-white" /></button>}
            <div className="absolute top-3 left-3 bg-accent/90 text-white text-[11px] font-medium px-2.5 py-1 rounded-full">Page {activePageIndex + 1} / {pages.length}</div>
          </div>
          <div className="p-4 bg-black/80 space-y-2 flex-shrink-0">
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => { reset(); openNativeCamera(); }} className="flex-1 gap-2 h-12 min-h-[48px] border-white/20 text-white hover:bg-white/10"><Plus className="w-4 h-4" /> Ajouter</Button>
              <Button onClick={async () => { setPhase('finalizing'); const pdf = await buildPdf(pages); const b = pdf.output('blob'); if (pdfUrl) URL.revokeObjectURL(pdfUrl); setPdfUrl(URL.createObjectURL(b)); setPhase('pdfPreview'); }} className="flex-1 gap-2 h-12 min-h-[48px]"><Eye className="w-4 h-4" /> Apercu PDF</Button>
            </div>
            <Button onClick={confirmMulti} className="w-full gap-2 h-14 min-h-[56px] bg-emerald-600 hover:bg-emerald-500 font-semibold"><Layers className="w-4 h-4" /> Fusionner ({pages.length} pages)</Button>
          </div>
        </div>
      )}

      {/* === PDF PREVIEW === */}
      {phase === 'pdfPreview' && pdfUrl && (
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-hidden bg-white"><iframe src={pdfUrl} title="Apercu PDF" className="w-full h-full border-0" /></div>
          <div className="p-4 bg-black/80 flex gap-2 flex-shrink-0">
            <Button variant="outline" onClick={() => setPhase('pages')} className="flex-1 gap-2 h-12 min-h-[48px] border-white/20 text-white hover:bg-white/10"><ChevronLeft className="w-4 h-4" /> Retour</Button>
            <Button onClick={confirmMulti} className="flex-1 gap-2 h-12 min-h-[48px] bg-emerald-600 hover:bg-emerald-500"><Check className="w-4 h-4" /> Valider</Button>
          </div>
        </div>
      )}

      {/* === FINALIZING === */}
      {phase === 'finalizing' && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <Loader2 className="w-14 h-14 text-emerald-400 animate-spin" />
          <p className="text-white text-base font-medium">Preparation du document...</p>
        </div>
      )}

      {/* Input appareil photo natif — capture="environment" ouvre la camera arriere */}
      <input ref={cameraInputRef} type="file" accept="image/*" capture="environment" onChange={handleCameraCapture} className="hidden" data-testid="scanner-camera-input" />
      {/* Input galerie — pas de capture attribute */}
      <input ref={galleryInputRef} type="file" accept="image/*" onChange={handleGalleryInput} className="hidden" data-testid="scanner-file-input" />
    </div>
  );
};
