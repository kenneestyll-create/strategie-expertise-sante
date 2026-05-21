import { useState, useRef, useCallback, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Upload, FileText, Image, X, AlertTriangle, CheckCircle,
  RefreshCw, Eye, ChevronDown, ChevronUp, Lightbulb,
  Camera, Smartphone, Sun, FileCheck, Shield, ScanLine
} from 'lucide-react';
import { useOCR } from '@/hooks/useOCR';
import { OcrFieldsPreview, OcrProgressBar } from '@/components/OcrFieldsPreview';
import { DocumentScanner } from '@/components/DocumentScanner';

const ACCEPTED_TYPES = {
  'application/pdf': 'PDF',
  'image/jpeg': 'JPG',
  'image/png': 'PNG',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'XLSX',
  'application/msword': 'DOC',
  'application/vnd.ms-excel': 'XLS',
};
const ACCEPTED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.docx', '.xlsx', '.doc', '.xls'];
const MAX_SIZE = 50 * 1024 * 1024; // 50 MB
const MAX_TOTAL_SIZE = 100 * 1024 * 1024; // 100 MB
const MAX_FILES = 10;
const COMPRESS_THRESHOLD = 2 * 1024 * 1024; // 2 MB — compress images above this
const COMPRESS_MAX_DIM = 2400; // Max pixel dimension (sufficient for OCR)
const COMPRESS_QUALITY = 0.82; // JPEG quality (good OCR readability)

/**
 * Compress an image file using Canvas API.
 * Returns { file, originalSize, compressed } or null if compression not needed.
 */
const compressImage = (file) => {
  return new Promise((resolve) => {
    if (!file.type?.startsWith('image/') || file.size < COMPRESS_THRESHOLD) {
      resolve(null); // No compression needed
      return;
    }

    const img = new window.Image();
    const url = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(url);
      let { width, height } = img;

      // Downscale if needed
      if (width > COMPRESS_MAX_DIM || height > COMPRESS_MAX_DIM) {
        const ratio = Math.min(COMPRESS_MAX_DIM / width, COMPRESS_MAX_DIM / height);
        width = Math.round(width * ratio);
        height = Math.round(height * ratio);
      }

      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, width, height);

      canvas.toBlob(
        (blob) => {
          if (!blob || blob.size >= file.size) {
            resolve(null); // Compressed is larger, keep original
            return;
          }
          const ext = file.name.split('.').pop().toLowerCase();
          const newName = ext === 'png'
            ? file.name.replace(/\.png$/i, '.jpg')
            : file.name;
          const compressed = new File([blob], newName, { type: 'image/jpeg' });
          compressed._originalSize = file.size;
          compressed._compressed = true;
          compressed._validated = false;
          resolve({ file: compressed, originalSize: file.size });
        },
        'image/jpeg',
        COMPRESS_QUALITY
      );
    };

    img.onerror = () => {
      URL.revokeObjectURL(url);
      resolve(null);
    };

    img.src = url;
  });
};

const getFileIcon = (file) => {
  if (file.type?.startsWith('image/')) return Image;
  return FileText;
};

const getFileExtLabel = (file) => {
  const ext = file.name?.split('.').pop()?.toUpperCase() || '?';
  return ext;
};

const formatSize = (bytes) => {
  if (bytes < 1024) return `${bytes} o`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} Ko`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
};

const validateFile = (file) => {
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!ACCEPTED_EXTENSIONS.includes(ext)) {
    return { valid: false, error: `Format "${ext}" non accepte. Formats autorises : PDF, JPG, PNG, DOCX, XLSX.` };
  }
  if (file.size > MAX_SIZE) {
    return { valid: false, error: `Fichier trop volumineux (${formatSize(file.size)}). Taille maximale : 50 Mo. Veuillez reduire la taille du fichier ou le compresser.` };
  }
  if (file.size < 100) {
    return { valid: false, error: 'Ce document semble illisible ou corrompu. Merci de le scanner a nouveau en haute qualité.' };
  }
  return { valid: true };
};

const FilePreview = ({ file, onRemove, index }) => {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const Icon = getFileIcon(file);

  useState(() => {
    if (file.type?.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg border border-border bg-card hover:bg-muted/30 transition-colors group" data-testid={`file-item-${index}`}>
      {/* Thumbnail / Icon */}
      <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center flex-shrink-0 overflow-hidden relative">
        {previewUrl ? (
          <img src={previewUrl} alt={file.name} className="w-full h-full object-cover rounded-lg" />
        ) : (
          <Icon className="w-5 h-5 text-muted-foreground" />
        )}
      </div>

      {/* File info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm truncate font-medium">{file.name}</span>
          <Badge variant="outline" className="text-[9px] px-1.5 flex-shrink-0">{getFileExtLabel(file)}</Badge>
        </div>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-xs text-muted-foreground">{formatSize(file.size)}</span>
          {file._compressed && file._originalSize && (
            <Badge className="bg-blue-50 text-blue-600 border-blue-200 text-[9px] gap-0.5 px-1.5" data-testid={`file-compressed-${index}`}>
              {formatSize(file._originalSize)} → {formatSize(file.size)}
            </Badge>
          )}
          {file._validated && (
            <Badge className="bg-green-100 text-green-700 border-green-200 text-[9px] gap-0.5 px-1.5" data-testid={`file-validated-${index}`}>
              <Shield className="w-2.5 h-2.5" /> Qualite verifiee
            </Badge>
          )}
        </div>
      </div>

      {/* Preview button for images */}
      {previewUrl && (
        <Button variant="ghost" size="icon" className="w-7 h-7 opacity-0 group-hover:opacity-100 transition-opacity" onClick={() => setShowPreview(!showPreview)}>
          <Eye className="w-3.5 h-3.5" />
        </Button>
      )}

      {/* Remove */}
      <Button variant="ghost" size="icon" className="w-7 h-7 text-muted-foreground hover:text-destructive hover:bg-destructive/10" onClick={() => onRemove(index)} data-testid={`file-remove-${index}`}>
        <RefreshCw className="w-3.5 h-3.5" />
      </Button>

      {/* Full preview modal */}
      {showPreview && previewUrl && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-8" style={{ zIndex: 9999 }} onClick={() => setShowPreview(false)}>
          <div className="max-w-3xl max-h-[80vh] relative" onClick={e => e.stopPropagation()}>
            <img src={previewUrl} alt={file.name} className="max-w-full max-h-[80vh] rounded-xl shadow-2xl" />
            <Button size="icon" variant="secondary" className="absolute -top-3 -right-3 rounded-full shadow-lg" onClick={() => setShowPreview(false)}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

const ScanGuide = () => {
  const [open, setOpen] = useState(false);

  const tips = [
    { icon: Sun, label: 'Bonne luminosité', desc: 'Placez le document dans un endroit bien éclairé, sans ombre', good: true },
    { icon: Smartphone, label: 'Téléphone ou scanner droit', desc: 'Gardez l\'appareil parallèle au document, sans angle', good: true },
    { icon: Camera, label: 'Pas de reflets', desc: 'Évitez le flash et les surfaces brillantes', good: true },
    { icon: FileText, label: 'Texte entièrement visible', desc: 'Tout le contenu doit être dans le cadre, sans coupure', good: true },
  ];

  return (
    <div className="border border-border rounded-xl overflow-hidden" data-testid="scan-guide">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-3 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted/30 transition-colors"
        data-testid="scan-guide-toggle"
      >
        <span className="flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-accent" />
          Guide de numérisation — Conseils pour de bons documents
        </span>
        {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>
      {open && (
        <div className="p-4 border-t border-border space-y-3 bg-muted/10" data-testid="scan-guide-content">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {tips.map((tip, i) => (
              <div key={i} className="flex items-start gap-2.5 p-2.5 rounded-lg bg-green-50 border border-green-100">
                <tip.icon className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-xs font-medium text-green-800">{tip.label}</p>
                  <p className="text-[10px] text-green-600/80 leading-relaxed">{tip.desc}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="p-3 rounded-lg bg-green-50 border border-green-200 text-center">
              <CheckCircle className="w-5 h-5 text-green-600 mx-auto mb-1" />
              <p className="text-[10px] font-semibold text-green-700">BON DOCUMENT</p>
              <p className="text-[9px] text-green-600 mt-0.5">Lisible, complet, bien cadré, lumineux</p>
            </div>
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-center">
              <AlertTriangle className="w-5 h-5 text-red-500 mx-auto mb-1" />
              <p className="text-[10px] font-semibold text-red-600">MAUVAIS DOCUMENT</p>
              <p className="text-[9px] text-red-500 mt-0.5">Flou, coupé, sombre, avec reflets</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const QualityChecklist = ({ checks, onChange }) => {
  const items = [
    { key: 'readable', label: 'Les documents sont lisibles et complets' },
    { key: 'personal_info', label: 'Les informations personnelles sont visibles' },
    { key: 'dates_signatures', label: 'Les dates et signatures sont lisibles' },
  ];

  return (
    <div className="space-y-2 p-3 rounded-xl border border-accent/20 bg-accent/5" data-testid="quality-checklist">
      <p className="text-sm font-medium flex items-center gap-2">
        <FileCheck className="w-4 h-4 text-accent" />
        Checklist qualité obligatoire
      </p>
      {items.map(item => (
        <label key={item.key} className="flex items-center gap-2.5 cursor-pointer group" data-testid={`check-${item.key}`}>
          <input
            type="checkbox"
            checked={checks[item.key] || false}
            onChange={e => onChange({ ...checks, [item.key]: e.target.checked })}
            className="w-4 h-4 accent-accent rounded"
          />
          <span className={`text-sm transition-colors ${checks[item.key] ? 'text-foreground' : 'text-muted-foreground'}`}>{item.label}</span>
          {checks[item.key] && <CheckCircle className="w-3.5 h-3.5 text-green-500 ml-auto" />}
        </label>
      ))}
    </div>
  );
};

export const DocumentUploader = ({ files, onFilesChange, maxFiles = MAX_FILES, showChecklist = true, showGuide = true, enableOCR = false, onOcrResult = null, className = '' }) => {
  const inputRef = useRef(null);
  const [errors, setErrors] = useState([]);
  const [checks, setChecks] = useState({ readable: false, personal_info: false, dates_signatures: false });
  const [ocrResult, setOcrResult] = useState(null);
  const [aiEnhancing, setAiEnhancing] = useState(false);
  const [showScanner, setShowScanner] = useState(false);
  const { extractFromMultiple, enhanceWithAI, processing: ocrProcessing, progress: ocrProgress, cancel: cancelOcr } = useOCR();

  const [compressInfo, setCompressInfo] = useState(null); // { count, savedBytes }
  const [dragOver, setDragOver] = useState(false);
  const dropzoneRef = useRef(null);
  const dragCounterRef = useRef(0);
  const lastDropRef = useRef(0);

  const allChecked = checks.readable && checks.personal_info && checks.dates_signatures;
  const hasFiles = files.length > 0;

  const handleFiles = useCallback(async (newFiles) => {
    const fileList = Array.from(newFiles);
    const validFiles = [];
    const newErrors = [];
    const currentTotalSize = files.reduce((sum, f) => sum + (f.size || 0), 0);
    let compressedCount = 0;
    let savedBytes = 0;
    let truncatedCount = 0;

    for (const file of fileList) {
      if (files.length + validFiles.length >= maxFiles) {
        truncatedCount++;
        continue;
      }

      // Attempt compression for images > 2 MB
      let processedFile = file;
      if (file.type?.startsWith('image/') && file.size >= COMPRESS_THRESHOLD) {
        try {
          const result = await compressImage(file);
          if (result) {
            processedFile = result.file;
            compressedCount++;
            savedBytes += result.originalSize - processedFile.size;
          }
        } catch {
          // If compression fails, use original
        }
      }

      const result = validateFile(processedFile);
      if (!result.valid) {
        newErrors.push(`${file.name} : ${result.error}`);
        continue;
      }
      const newTotal = currentTotalSize + validFiles.reduce((s, f) => s + f.size, 0) + processedFile.size;
      if (newTotal > MAX_TOTAL_SIZE) {
        newErrors.push(`Taille totale dépassée (limite : ${formatSize(MAX_TOTAL_SIZE)}). Le fichier "${file.name}" (${formatSize(file.size)}) n'a pas été ajouté.`);
        continue;
      }
      processedFile._validated = false;
      validFiles.push(processedFile);
    }

    if (compressedCount > 0) {
      setCompressInfo({ count: compressedCount, savedBytes });
    }

    if (truncatedCount > 0) {
      newErrors.push(
        `Limite de ${maxFiles} fichiers atteinte : ${truncatedCount} fichier${truncatedCount > 1 ? 's' : ''} non ajouté${truncatedCount > 1 ? 's' : ''}. ` +
        `Astuce : fusionnez plusieurs PDF en un seul (outils gratuits : ilovepdf.com, smallpdf.com) pour transmettre l'intégralité de votre dossier.`
      );
    }

    setErrors(newErrors);
    if (validFiles.length > 0) {
      const allFiles = [...files, ...validFiles];
      onFilesChange(allFiles);

      // Auto-trigger OCR → GPT-4o pipeline on images
      if (enableOCR) {
        const imageFiles = allFiles.filter(f => f.type?.startsWith('image/'));
        if (imageFiles.length > 0) {
          const result = await extractFromMultiple(imageFiles);
          if (result && result.raw && result.raw.trim().length > 10) {
            // Phase 1 done, auto-trigger Phase 2 GPT-4o
            setOcrResult({ ...result, enhancing: true });
            if (onOcrResult) onOcrResult(result);
            setAiEnhancing(true);
            const aiResult = await enhanceWithAI(result.raw);
            if (aiResult && aiResult.enhanced) {
              const merged = { ...result, ...aiResult };
              setOcrResult(merged);
              if (onOcrResult) onOcrResult({ ...merged, applied: true });
            } else {
              setOcrResult(result);
            }
            setAiEnhancing(false);
          } else if (result && result.fields && Object.keys(result.fields).length > 0) {
            setOcrResult(result);
            if (onOcrResult) onOcrResult(result);
          }
        }
      }
    }
  }, [files, maxFiles, onFilesChange, enableOCR, extractFromMultiple, enhanceWithAI, onOcrResult]);

  const removeFile = useCallback((index) => {
    const updated = files.filter((_, i) => i !== index);
    onFilesChange(updated);
    if (updated.length === 0) {
      setChecks({ readable: false, personal_info: false, dates_signatures: false });
    }
  }, [files, onFilesChange]);

  const handleCheckChange = (newChecks) => {
    setChecks(newChecks);
    const allOk = newChecks.readable && newChecks.personal_info && newChecks.dates_signatures;
    if (allOk && files.length > 0) {
      // Mark files as validated without destroying File objects
      files.forEach(f => { f._validated = true; });
      onFilesChange([...files]);
    }
  };

  // Native DOM drag-and-drop — most reliable cross-browser approach
  useEffect(() => {
    const el = dropzoneRef.current;
    if (!el) return;

    const onDragEnter = (e) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounterRef.current += 1;
      if (e.dataTransfer && e.dataTransfer.types && e.dataTransfer.types.indexOf('Files') !== -1) {
        setDragOver(true);
      }
    };
    const onDragOver = (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
    };
    const onDragLeave = (e) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounterRef.current -= 1;
      if (dragCounterRef.current <= 0) {
        dragCounterRef.current = 0;
        setDragOver(false);
      }
    };
    const onDrop = (e) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounterRef.current = 0;
      setDragOver(false);
      lastDropRef.current = Date.now();
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    };

    el.addEventListener('dragenter', onDragEnter);
    el.addEventListener('dragover', onDragOver);
    el.addEventListener('dragleave', onDragLeave);
    el.addEventListener('drop', onDrop);
    return () => {
      el.removeEventListener('dragenter', onDragEnter);
      el.removeEventListener('dragover', onDragOver);
      el.removeEventListener('dragleave', onDragLeave);
      el.removeEventListener('drop', onDrop);
    };
  }, [handleFiles]);

  // Prevent window-level drag from navigating away
  useEffect(() => {
    const prevent = (e) => { e.preventDefault(); };
    window.addEventListener('dragover', prevent);
    window.addEventListener('drop', prevent);
    return () => {
      window.removeEventListener('dragover', prevent);
      window.removeEventListener('drop', prevent);
    };
  }, []);

  // Click handler that prevents opening dialog right after a drop
  const handleDropzoneClick = useCallback(() => {
    if (Date.now() - lastDropRef.current < 500) return;
    inputRef.current?.click();
  }, []);

  const handleScanCapture = useCallback(async (file, imageFiles) => {
    setShowScanner(false);
    if (imageFiles && imageFiles.length > 1) {
      // Multi-scan: PDF file + individual images for OCR
      const allFiles = [...files, file];
      onFilesChange(allFiles);

      if (enableOCR) {
        // Run OCR on individual page images, then GPT-4o on combined text
        const result = await extractFromMultiple(imageFiles);
        if (result && result.raw && result.raw.trim().length > 10) {
          setOcrResult({ ...result, enhancing: true, multiScan: true, pageCount: imageFiles.length });
          if (onOcrResult) onOcrResult(result);
          setAiEnhancing(true);
          const aiResult = await enhanceWithAI(result.raw);
          if (aiResult && aiResult.enhanced) {
            const merged = { ...result, ...aiResult, multiScan: true, pageCount: imageFiles.length };
            setOcrResult(merged);
            if (onOcrResult) onOcrResult({ ...merged, applied: true });
          } else {
            setOcrResult(result);
          }
          setAiEnhancing(false);
        }
      }
    } else {
      // Single scan: treat as regular image file
      handleFiles([file]);
    }
  }, [files, onFilesChange, enableOCR, extractFromMultiple, enhanceWithAI, onOcrResult, handleFiles]);

  return (
    <div className={`space-y-3 ${className}`} data-testid="document-uploader">
      {/* Scanner Modal */}
      {showScanner && (
        <DocumentScanner
          onCapture={handleScanCapture}
          onClose={() => setShowScanner(false)}
        />
      )}

      {/* Drop zone + Scan button */}
      <div className="flex gap-2">
        <div
          ref={dropzoneRef}
          className={`flex-1 border-2 border-dashed rounded-xl p-6 text-center transition-all duration-200 cursor-pointer relative ${dragOver ? 'border-accent bg-accent/5 scale-[1.01] ring-2 ring-accent/20' : 'border-border hover:border-accent/50'}`}
          onClick={handleDropzoneClick}
          data-testid="upload-dropzone"
        >
          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,.jpg,.jpeg,.png,.docx,.xlsx,.doc,.xls"
            onChange={e => { handleFiles(e.target.files); e.target.value = ''; }}
            className="hidden"
            data-testid="file-input"
          />
          <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Glissez vos fichiers ou cliquez pour selectionner</p>
          <p className="text-xs text-muted-foreground mt-1">PDF, JPG, PNG, DOCX, XLSX — Max 50 Mo/fichier — Max {maxFiles} fichiers</p>
          <p className="text-[10px] text-muted-foreground mt-0.5">Les fichiers &gt; 5 Mo sont uploadés automatiquement en mode fractionné sécurisé</p>
          <p className="text-[10px] text-amber-600/80 mt-0.5" data-testid="merge-pdf-hint">Plus de {maxFiles} documents ? Fusionnez vos PDF (ilovepdf.com, smallpdf.com) pour tout transmettre.</p>
          {hasFiles && (
            <p className="text-[10px] text-amber-600 mt-2 flex items-center justify-center gap-1">
              <AlertTriangle className="w-3 h-3" />
              Ne fermez pas la page pendant le telechargement
            </p>
          )}
        </div>
        {enableOCR && (
          <button
            onClick={(e) => { e.stopPropagation(); setShowScanner(true); }}
            className="flex sm:hidden flex-col items-center justify-center gap-2 w-28 rounded-xl border-2 border-dashed border-accent/40 hover:border-accent hover:bg-accent/5 transition-all cursor-pointer group"
            data-testid="scanner-open-btn"
          >
            <div className="w-10 h-10 rounded-full bg-accent/10 group-hover:bg-accent/20 flex items-center justify-center transition-colors">
              <Camera className="w-5 h-5 text-accent" />
            </div>
            <span className="text-[11px] font-medium text-accent leading-tight text-center">Scanner un document</span>
          </button>
        )}
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="space-y-1" data-testid="upload-errors">
          {errors.map((err, i) => (
            <div key={i} className="flex items-start gap-2 p-2.5 rounded-lg bg-destructive/10 border border-destructive/20 text-sm text-destructive">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span className="text-xs">{err}</span>
            </div>
          ))}
        </div>
      )}

      {/* File list */}
      {hasFiles && (
        <div className="space-y-2" data-testid="file-list">
          {files.map((f, i) => (
            <FilePreview key={`${f.name}-${i}`} file={f} onRemove={removeFile} index={i} />
          ))}
          <div className="flex items-center justify-between text-xs text-muted-foreground px-1" data-testid="upload-summary">
            <span>{files.length} fichier{files.length > 1 ? 's' : ''} — {formatSize(files.reduce((s, f) => s + (f.size || 0), 0))} total</span>
            <span className="text-[10px]">Limite : 50 Mo/fichier, 100 Mo total</span>
          </div>
          {compressInfo && compressInfo.savedBytes > 0 && (
            <div className="flex items-center gap-2 px-3 py-2 bg-blue-50/70 rounded-lg border border-blue-100 text-xs text-blue-700" data-testid="compression-info">
              <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />
              <span>
                {compressInfo.count} image{compressInfo.count > 1 ? 's' : ''} compresse{compressInfo.count > 1 ? 'es' : 'e'} automatiquement — {formatSize(compressInfo.savedBytes)} economise{compressInfo.savedBytes > 1024 * 1024 ? 's' : ''}
              </span>
            </div>
          )}
        </div>
      )}

      {/* OCR Progress */}
      {enableOCR && (ocrProcessing || aiEnhancing) && (
        <div className="space-y-2">
          <OcrProgressBar processing={ocrProcessing} progress={ocrProgress} />
          {aiEnhancing && !ocrProcessing && (
            <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-50 border border-blue-200" data-testid="ai-enhancing-progress">
              <ScanLine className="w-4 h-4 text-blue-600 animate-pulse flex-shrink-0" />
              <div className="flex-1">
                <span className="text-xs font-medium text-blue-700">Analyse intelligente GPT-4o en cours...</span>
                <p className="text-[10px] text-blue-500">Extraction des dates, montants, organismes, type de document...</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* OCR Results */}
      {enableOCR && ocrResult && !ocrProcessing && !aiEnhancing && (
        <div className="space-y-2">
          <OcrFieldsPreview
            ocrResult={ocrResult}
            onApplyFields={onOcrResult ? (fields) => onOcrResult({ ...ocrResult, fields, applied: true }) : null}
            onDismiss={() => setOcrResult(null)}
          />
          {!ocrResult.enhanced && (
            <Button
              variant="outline"
              size="sm"
              className="gap-2 text-xs border-blue-300 text-blue-700 hover:bg-blue-50"
              disabled={aiEnhancing}
              onClick={async () => {
                setAiEnhancing(true);
                const aiResult = await enhanceWithAI(ocrResult.raw);
                if (aiResult) {
                  const merged = { ...ocrResult, ...aiResult };
                  setOcrResult(merged);
                  if (onOcrResult) onOcrResult({ ...merged, applied: true });
                }
                setAiEnhancing(false);
              }}
              data-testid="ocr-ai-enhance"
            >
              <ScanLine className="w-3.5 h-3.5" /> Enrichir avec GPT-4o
            </Button>
          )}
          {ocrResult.enhanced && (
            <div className="flex items-center gap-2 p-2 rounded-lg bg-blue-50 border border-blue-200" data-testid="ai-enhanced-badge">
              <CheckCircle className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-medium text-blue-700">
                {ocrResult.multiScan 
                  ? `${ocrResult.pageCount} pages fusionnées — Champs pré-remplis par GPT-4o`
                  : 'Champs pré-remplis automatiquement par GPT-4o'}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Quality checklist */}
      {hasFiles && showChecklist && (
        <QualityChecklist checks={checks} onChange={handleCheckChange} />
      )}

      {/* Scan guide */}
      {showGuide && <ScanGuide />}

      {/* Manual OCR trigger */}
      {enableOCR && hasFiles && !ocrProcessing && !ocrResult && files.some(f => f.type?.startsWith('image/')) && (
        <Button
          variant="outline"
          size="sm"
          className="gap-2 text-xs border-accent/30 text-accent hover:bg-accent/5"
          onClick={async () => {
            const imageFiles = files.filter(f => f.type?.startsWith('image/'));
            const result = await extractFromMultiple(imageFiles);
            if (result && result.fields && Object.keys(result.fields).length > 0) {
              setOcrResult(result);
              if (onOcrResult) onOcrResult(result);
            }
          }}
          data-testid="ocr-manual-trigger"
        >
          <ScanLine className="w-3.5 h-3.5" /> Relancer l'extraction OCR
        </Button>
      )}

      {/* Status badge */}
      {hasFiles && allChecked && showChecklist && (
        <div className="flex items-center gap-2 p-2 rounded-lg bg-green-50 border border-green-200" data-testid="all-validated-badge">
          <Shield className="w-4 h-4 text-green-600" />
          <span className="text-xs font-medium text-green-700">Tous les documents ont passé le contrôle qualité</span>
        </div>
      )}
    </div>
  );
};

// Export checklist state check for parent forms
export const isChecklistComplete = (checks) => {
  return checks?.readable && checks?.personal_info && checks?.dates_signatures;
};
