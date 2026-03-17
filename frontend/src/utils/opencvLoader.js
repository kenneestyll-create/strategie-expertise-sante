/**
 * OpenCV.js — Robust non-blocking lazy loader
 * Timeout 5s, full fallback, console logging
 */
let cvInstance = null;
let loadPromise = null;

export function loadOpenCV() {
  if (cvInstance) return Promise.resolve(cvInstance);
  if (loadPromise) return loadPromise;

  loadPromise = new Promise((resolve, reject) => {
    // Already loaded from a previous session
    if (window.cv && window.cv.Mat) {
      console.log('[OpenCV] Déjà chargé, réutilisation');
      cvInstance = window.cv;
      return resolve(cvInstance);
    }

    const TIMEOUT_MS = 5000;

    const timeout = setTimeout(() => {
      console.warn('[OpenCV] Timeout après 5s — fallback mode simple');
      loadPromise = null;
      reject(new Error('OpenCV load timeout'));
    }, TIMEOUT_MS);

    const script = document.createElement('script');
    script.src = 'https://docs.opencv.org/4.x/opencv.js';
    script.async = true;

    script.onload = () => {
      console.log('[OpenCV] Script chargé, attente initialisation runtime...');
      // cv is now a global but runtime may not be initialized yet
      if (typeof cv !== 'undefined') {
        cv['onRuntimeInitialized'] = () => {
          clearTimeout(timeout);
          console.log('[OpenCV] Runtime initialisé avec succès');
          cvInstance = cv;
          resolve(cv);
        };
      } else {
        clearTimeout(timeout);
        console.error('[OpenCV] cv non défini après chargement script');
        loadPromise = null;
        reject(new Error('cv undefined after script load'));
      }
    };

    script.onerror = () => {
      clearTimeout(timeout);
      console.error('[OpenCV] Échec chargement script (réseau/CDN)');
      loadPromise = null;
      reject(new Error('OpenCV script load error'));
    };

    document.body.appendChild(script);
  });

  return loadPromise;
}

export function getCV() {
  return cvInstance;
}

export function isOpenCVReady() {
  return !!cvInstance;
}
