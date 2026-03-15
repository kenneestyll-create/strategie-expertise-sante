import { useState, useRef, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Camera, X, RotateCcw, Check, Smartphone, Sun,
  Eye, Maximize2, ZapOff, Loader2
} from 'lucide-react';

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

  // Sharpen pass
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
            const idx = ((y + ky) * w + (x + kx)) * 4 + c;
            val += src.data[idx] * kernel[(ky + 1) * 3 + (kx + 1)];
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

export const DocumentScanner = ({ onCapture, onClose }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [phase, setPhase] = useState('guide'); // guide | camera | preview | processing
  const [capturedImage, setCapturedImage] = useState(null);
  const [error, setError] = useState('');
  const [facingMode, setFacingMode] = useState('environment');

  const startCamera = useCallback(async () => {
    setError('');
    try {
      const constraints = {
        video: {
          facingMode,
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
        audio: false,
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setPhase('camera');
    } catch (err) {
      if (err.name === 'NotAllowedError') {
        setError('Accès caméra refusé. Autorisez l\'accès dans les paramètres du navigateur.');
      } else if (err.name === 'NotFoundError') {
        setError('Aucune caméra détectée sur cet appareil.');
      } else {
        setError(`Erreur caméra : ${err.message}`);
      }
    }
  }, [facingMode]);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => stopCamera();
  }, [stopCamera]);

  const capture = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    enhanceImage(canvas);

    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
    setCapturedImage(dataUrl);
    stopCamera();
    setPhase('preview');
  }, [stopCamera]);

  const retake = useCallback(() => {
    setCapturedImage(null);
    startCamera();
  }, [startCamera]);

  const confirm = useCallback(async () => {
    if (!capturedImage) return;
    setPhase('processing');

    // Convert dataURL to File
    const res = await fetch(capturedImage);
    const blob = await res.blob();
    const file = new File([blob], `scan_${Date.now()}.jpg`, { type: 'image/jpeg' });

    stopCamera();
    onCapture(file);
  }, [capturedImage, onCapture, stopCamera]);

  const switchCamera = useCallback(() => {
    stopCamera();
    setFacingMode(prev => prev === 'environment' ? 'user' : 'environment');
    setTimeout(() => startCamera(), 100);
  }, [stopCamera, startCamera]);

  const handleClose = useCallback(() => {
    stopCamera();
    onClose();
  }, [stopCamera, onClose]);

  return (
    <div className="fixed inset-0 z-50 bg-black/95 flex flex-col" data-testid="document-scanner">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-black/80 backdrop-blur-sm">
        <h3 className="text-white text-sm font-medium">Scanner un document</h3>
        <Button variant="ghost" size="sm" onClick={handleClose} className="text-white hover:bg-white/10" data-testid="scanner-close">
          <X className="w-5 h-5" />
        </Button>
      </div>

      {/* Guide Phase */}
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
          <Button onClick={startCamera} className="w-full max-w-xs gap-2 h-12 text-base" data-testid="scanner-start-btn">
            <Camera className="w-5 h-5" /> Ouvrir la caméra
          </Button>
          {error && (
            <p className="text-red-400 text-sm text-center max-w-xs" data-testid="scanner-error">{error}</p>
          )}
        </div>
      )}

      {/* Camera Phase */}
      {phase === 'camera' && (
        <div className="flex-1 relative overflow-hidden">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            data-testid="scanner-video"
          />
          {/* Document guide overlay */}
          <div className="absolute inset-0 pointer-events-none" data-testid="scanner-overlay">
            {/* Dark edges */}
            <div className="absolute inset-0 bg-black/40" />
            {/* Clear center window */}
            <div className="absolute inset-[8%] sm:inset-[12%] rounded-2xl border-2 border-white/80 bg-transparent" style={{ boxShadow: '0 0 0 9999px rgba(0,0,0,0.4)' }} />
            {/* Corner markers */}
            <div className="absolute top-[8%] left-[8%] sm:top-[12%] sm:left-[12%] w-8 h-8 border-t-4 border-l-4 border-accent rounded-tl-lg" />
            <div className="absolute top-[8%] right-[8%] sm:top-[12%] sm:right-[12%] w-8 h-8 border-t-4 border-r-4 border-accent rounded-tr-lg" />
            <div className="absolute bottom-[8%] left-[8%] sm:bottom-[12%] sm:left-[12%] w-8 h-8 border-b-4 border-l-4 border-accent rounded-bl-lg" />
            <div className="absolute bottom-[8%] right-[8%] sm:bottom-[12%] sm:right-[12%] w-8 h-8 border-b-4 border-r-4 border-accent rounded-br-lg" />
            {/* Center text */}
            <div className="absolute top-[calc(8%+12px)] sm:top-[calc(12%+12px)] left-0 right-0 text-center">
              <span className="text-white/80 text-xs bg-black/50 px-3 py-1 rounded-full">Centrez le document dans le cadre</span>
            </div>
          </div>
          {/* Controls */}
          <div className="absolute bottom-0 left-0 right-0 flex items-center justify-center gap-6 pb-8 pt-4 bg-gradient-to-t from-black/80 to-transparent">
            <Button variant="ghost" size="sm" onClick={switchCamera} className="text-white hover:bg-white/10 rounded-full w-12 h-12" data-testid="scanner-switch-camera">
              <RotateCcw className="w-5 h-5" />
            </Button>
            <button
              onClick={capture}
              className="w-16 h-16 rounded-full border-4 border-white bg-white/20 hover:bg-white/40 transition-colors flex items-center justify-center active:scale-95"
              data-testid="scanner-capture-btn"
            >
              <div className="w-12 h-12 rounded-full bg-white" />
            </button>
            <div className="w-12 h-12" /> {/* Spacer for alignment */}
          </div>
        </div>
      )}

      {/* Preview Phase */}
      {phase === 'preview' && capturedImage && (
        <div className="flex-1 flex flex-col">
          <div className="flex-1 relative overflow-hidden bg-black flex items-center justify-center p-4">
            <img src={capturedImage} alt="Document scanné" className="max-w-full max-h-full object-contain rounded-lg" data-testid="scanner-preview-img" />
            <div className="absolute top-3 left-3 bg-green-500/90 text-white text-[10px] font-medium px-2 py-1 rounded-full flex items-center gap-1">
              <Eye className="w-3 h-3" /> Contraste et netteté améliorés
            </div>
          </div>
          <div className="flex gap-3 p-4 bg-black/80">
            <Button variant="outline" onClick={retake} className="flex-1 gap-2 border-white/20 text-white hover:bg-white/10" data-testid="scanner-retake-btn">
              <RotateCcw className="w-4 h-4" /> Reprendre
            </Button>
            <Button onClick={confirm} className="flex-1 gap-2" data-testid="scanner-confirm-btn">
              <Check className="w-4 h-4" /> Utiliser cette photo
            </Button>
          </div>
        </div>
      )}

      {/* Processing Phase */}
      {phase === 'processing' && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <Loader2 className="w-12 h-12 text-accent animate-spin" />
          <p className="text-white text-sm">Traitement du document en cours...</p>
          <p className="text-white/50 text-xs">Amélioration de l'image + extraction OCR GPT-4o</p>
        </div>
      )}

      {/* Hidden canvas for image processing */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};
