import { useState, useRef, useCallback } from 'react';
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
};
const ACCEPTED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.docx'];
const MAX_SIZE = 10 * 1024 * 1024; // 10MB
const MAX_FILES = 5;

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
    return { valid: false, error: `Format "${ext}" non accepté. Formats autorisés : PDF, JPG, PNG, DOCX.` };
  }
  if (file.size > MAX_SIZE) {
    return { valid: false, error: `Fichier trop volumineux (${formatSize(file.size)}). Taille maximale : 10 Mo.` };
  }
  if (file.size < 100) {
    return { valid: false, error: 'Ce document semble illisible ou corrompu. Merci de le scanner à nouveau en haute qualité.' };
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
          {file._validated && (
            <Badge className="bg-green-100 text-green-700 border-green-200 text-[9px] gap-0.5 px-1.5" data-testid={`file-validated-${index}`}>
              <Shield className="w-2.5 h-2.5" /> Qualité vérifiée
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
          <span className={`text-sm transition-colors ${checks[item.key] ? 'text-foreground' : 'text-muted-foreground'}`}>{item.label}</span>
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

  const allChecked = checks.readable && checks.personal_info && checks.dates_signatures;
  const hasFiles = files.length > 0;

  const handleFiles = useCallback(async (newFiles) => {
    const fileList = Array.from(newFiles);
    const validFiles = [];
    const newErrors = [];

    for (const file of fileList) {
      if (files.length + validFiles.length >= maxFiles) {
        newErrors.push(`Maximum ${maxFiles} fichiers atteint.`);
        break;
      }
      const result = validateFile(file);
      if (result.valid) {
        file._validated = false;
        validFiles.push(file);
      } else {
        newErrors.push(`${file.name} : ${result.error}`);
      }
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
      const updated = files.map(f => ({ ...f, _validated: true }));
      onFilesChange(updated);
    }
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

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
          className="flex-1 border-2 border-dashed border-border rounded-xl p-6 text-center hover:border-accent/50 transition-colors cursor-pointer relative"
          onDrop={handleDrop}
          onDragOver={e => e.preventDefault()}
          onClick={() => inputRef.current?.click()}
          data-testid="upload-dropzone"
        >
          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,.jpg,.jpeg,.png,.docx"
            onChange={e => { handleFiles(e.target.files); e.target.value = ''; }}
            className="hidden"
            data-testid="file-input"
          />
          <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Glissez vos fichiers ou cliquez pour sélectionner</p>
          <p className="text-xs text-muted-foreground mt-1">PDF, JPG, PNG, DOCX — Max 10 Mo — Max {maxFiles} fichiers</p>
        </div>
        {enableOCR && (
          <button
            onClick={(e) => { e.stopPropagation(); setShowScanner(true); }}
            className="flex flex-col items-center justify-center gap-2 w-28 sm:w-32 rounded-xl border-2 border-dashed border-accent/40 hover:border-accent hover:bg-accent/5 transition-all cursor-pointer group"
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
