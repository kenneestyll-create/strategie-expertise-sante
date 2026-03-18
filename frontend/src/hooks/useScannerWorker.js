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
  const prevUrlRef = useRef(null);

  const handleMessage = useCallback((e) => {
    const { type, data, width, height, error: err } = e.data;

    if (type === 'ready') {
      setIsReady(true);
      return;
    }

    if (type === 'preview') {
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
      const blob = new Blob([data], { type: 'image/jpeg' });
      const url = URL.createObjectURL(blob);
      prevUrlRef.current = url;
      setPreviewUrl(url);
      if (width && height) setPreviewSize({ width, height });
      setIsProcessing(false);
      return;
    }

    if (type === 'error') {
      setError(err);
      setIsProcessing(false);
      return;
    }
    // 'saved' handled by save() promise
  }, []);

  const createWorker = useCallback(() => {
    const w = new Worker('/workers/scanner.worker.js');
    w.onmessage = handleMessage;
    w.onerror = (err) => { setError(err.message); setIsProcessing(false); };
    workerRef.current = w;
    setIsReady(false);
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
    workerRef.current?.terminate();
    createWorker();
  }, [createWorker]);

  return { previewUrl, previewSize, isReady, isProcessing, error, scan, filter, rotate, save, reset };
}
