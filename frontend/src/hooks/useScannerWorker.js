import { useRef, useState, useCallback, useEffect } from 'react';

/**
 * Hook simplifie — pas de classe, juste un Worker + refs.
 * Le Worker garde l'image en memoire (OffscreenCanvas stateful).
 * Le main thread recoit des previews JPEG via ArrayBuffer transferable.
 */
export function useScannerWorker() {
  const workerRef = useRef(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [previewSize, setPreviewSize] = useState({ width: 0, height: 0 });
  const [isReady, setIsReady] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [cvReady, setCvReady] = useState(false);
  const [autoCropApplied, setAutoCropApplied] = useState(null);
  const prevUrlRef = useRef(null);
  const inputSizeRef = useRef(null);

  const handleMessage = useCallback((e) => {
    const { type, data, width, height, error: err, cvReady: cv } = e.data;

    if (type === 'ready') {
      setIsReady(true);
      if (cv !== undefined) setCvReady(cv);
      return;
    }

    if (type === 'preview') {
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
      const blob = new Blob([data], { type: 'image/jpeg' });
      const url = URL.createObjectURL(blob);
      prevUrlRef.current = url;
      setPreviewUrl(url);
      if (width && height) {
        setPreviewSize({ width, height });
        // Check if dimensions changed (auto-crop applied)
        if (inputSizeRef.current) {
          const { w: inW, h: inH } = inputSizeRef.current;
          setAutoCropApplied(width !== inW || height !== inH);
          inputSizeRef.current = null;
        }
      }
      setIsProcessing(false);
      return;
    }

    if (type === 'error') {
      setError(err);
      setIsProcessing(false);
      return;
    }
    // 'saved' handled by save() promise
    // 'debug' messages are logged but not displayed
  }, []);

  const createWorker = useCallback(() => {
    const w = new Worker(`/workers/scanner.worker.js?v=${Date.now()}`);
    w.onmessage = handleMessage;
    w.onerror = (err) => { setError(err.message); setIsProcessing(false); };
    workerRef.current = w;
    setIsReady(false);
    setCvReady(false);
  }, [handleMessage]);

  useEffect(() => {
    createWorker();
    return () => {
      workerRef.current?.terminate();
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
    };
  }, [createWorker]);

  const scan = useCallback((blob, autoCrop) => {
    setIsProcessing(true);
    setError(null);
    setAutoCropApplied(null);
    // Track input size to detect crop
    if (blob instanceof Blob) {
      createImageBitmap(blob).then(bmp => {
        inputSizeRef.current = { w: bmp.width, h: bmp.height };
        bmp.close();
      }).catch(() => {});
    }
    workerRef.current?.postMessage({ type: 'scan', blob, autoCrop: !!autoCrop });
  }, []);

  const filter = useCallback((name) => {
    setIsProcessing(true);
    workerRef.current?.postMessage({ type: 'filter', filter: name });
  }, []);

  const rotate = useCallback((direction) => {
    setIsProcessing(true);
    workerRef.current?.postMessage({ type: 'rotate', direction });
  }, []);

  const save = useCallback(() => {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        workerRef.current?.removeEventListener('message', handler);
        reject(new Error('Save timeout'));
      }, 10000);

      const handler = (e) => {
        if (e.data.type === 'saved') {
          clearTimeout(timeout);
          workerRef.current?.removeEventListener('message', handler);
          resolve(e.data.data);
        }
        if (e.data.type === 'error') {
          clearTimeout(timeout);
          workerRef.current?.removeEventListener('message', handler);
          reject(new Error(e.data.error));
        }
      };
      workerRef.current?.addEventListener('message', handler);
      workerRef.current?.postMessage({ type: 'save' });
    });
  }, []);

  const reset = useCallback(() => {
    if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
    prevUrlRef.current = null;
    setPreviewUrl(null);
    setPreviewSize({ width: 0, height: 0 });
    setError(null);
    setIsProcessing(false);
    setAutoCropApplied(null);
    workerRef.current?.terminate();
    createWorker();
  }, [createWorker]);

  return { previewUrl, previewSize, isReady, isProcessing, error, cvReady, autoCropApplied, scan, filter, rotate, save, reset };
}
