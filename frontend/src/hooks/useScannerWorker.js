import { useRef, useCallback, useEffect, useState } from 'react';

/**
 * MobileScanner — Classe gerant le Worker OffscreenCanvas.
 * Pattern: capture(blob) → applyFilter/rotate → save()
 * Le Worker garde l'image en memoire, le main thread recoit des previews JPEG.
 */
class MobileScanner {
  constructor() {
    this.worker = new Worker('/workers/scanner.worker.js');
    this.onPreview = null;
    this.onError = null;
    this._setupWorker();
  }

  _setupWorker() {
    this.worker.onmessage = (e) => {
      const { type, data, error } = e.data;
      if (type === 'preview' && this.onPreview) {
        const blob = new Blob([data], { type: 'image/jpeg' });
        const url = URL.createObjectURL(blob);
        this.onPreview(url);
      }
      if (type === 'error' && this.onError) {
        this.onError(error);
      }
      // 'saved' is handled by the save() promise
    };
    this.worker.onerror = (err) => {
      if (this.onError) this.onError(err.message);
    };
  }

  capture(blob) {
    this.worker.postMessage({ type: 'scan', imageBlob: blob });
  }

  applyFilter(filter) {
    this.worker.postMessage({ type: 'filter', filter });
  }

  rotate(direction) {
    this.worker.postMessage({ type: 'rotate', direction });
  }

  save() {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.worker.removeEventListener('message', handler);
        reject(new Error('Save timeout'));
      }, 10000);

      const handler = (e) => {
        if (e.data.type === 'saved') {
          clearTimeout(timeout);
          this.worker.removeEventListener('message', handler);
          resolve(e.data.data);
        }
        if (e.data.type === 'error') {
          clearTimeout(timeout);
          this.worker.removeEventListener('message', handler);
          reject(new Error(e.data.error));
        }
      };
      this.worker.addEventListener('message', handler);
      this.worker.postMessage({ type: 'save' });
    });
  }

  terminate() {
    this.worker.terminate();
  }
}

/**
 * React hook wrapping MobileScanner.
 * Returns: { previewUrl, capture, applyFilter, rotate, save, error, isProcessing }
 */
export function useScannerWorker() {
  const scannerRef = useRef(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSimpleMode, setIsSimpleMode] = useState(true);
  const prevUrlRef = useRef(null);

  useEffect(() => {
    const scanner = new MobileScanner();
    scanner.onPreview = (url) => {
      // Revoke previous URL to avoid memory leaks
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
      prevUrlRef.current = url;
      setPreviewUrl(url);
      setIsProcessing(false);
    };
    scanner.onError = (msg) => {
      setError(msg);
      setIsProcessing(false);
    };
    scannerRef.current = scanner;

    return () => {
      scanner.terminate();
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
    };
  }, []);

  const capture = useCallback((blob) => {
    setIsProcessing(true);
    setError(null);
    scannerRef.current?.capture(blob);
  }, []);

  const applyFilter = useCallback((filter) => {
    setIsProcessing(true);
    scannerRef.current?.applyFilter(filter);
  }, []);

  const rotate = useCallback((direction) => {
    setIsProcessing(true);
    scannerRef.current?.rotate(direction);
  }, []);

  const save = useCallback(async () => {
    if (!scannerRef.current) throw new Error('Scanner not initialized');
    const arrayBuffer = await scannerRef.current.save();
    return new Blob([arrayBuffer], { type: 'image/jpeg' });
  }, []);

  const reset = useCallback(() => {
    if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
    prevUrlRef.current = null;
    setPreviewUrl(null);
    setError(null);
    setIsProcessing(false);
    // Recreate worker for clean state
    scannerRef.current?.terminate();
    const scanner = new MobileScanner();
    scanner.onPreview = (url) => {
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
      prevUrlRef.current = url;
      setPreviewUrl(url);
      setIsProcessing(false);
    };
    scanner.onError = (msg) => {
      setError(msg);
      setIsProcessing(false);
    };
    scannerRef.current = scanner;
  }, []);

  return { previewUrl, capture, applyFilter, rotate, save, reset, error, isProcessing, isSimpleMode, setIsSimpleMode };
}
