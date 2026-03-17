/**
 * Non-blocking lazy loader for OpenCV.js
 * Loads in background, never blocks UI
 */
let cvInstance = null;
let loadPromise = null;
let loadFailed = false;

export function loadOpenCV() {
  if (cvInstance) return Promise.resolve(cvInstance);
  if (loadFailed) return Promise.reject(new Error('OpenCV load failed'));
  if (loadPromise) return loadPromise;

  loadPromise = new Promise((resolve, reject) => {
    // Already available
    if (window.cv && window.cv.Mat) {
      cvInstance = window.cv;
      return resolve(cvInstance);
    }

    const TIMEOUT = 12000;
    let resolved = false;

    const done = (cv) => {
      if (resolved) return;
      resolved = true;
      cvInstance = cv;
      resolve(cv);
    };

    const fail = (reason) => {
      if (resolved) return;
      resolved = true;
      loadFailed = true;
      loadPromise = null;
      reject(new Error(reason));
    };

    // Timeout
    const timer = setTimeout(() => fail('Délai dépassé'), TIMEOUT);

    // onRuntimeInitialized is the correct OpenCV.js callback
    window.Module = window.Module || {};
    window.Module.onRuntimeInitialized = () => {
      clearTimeout(timer);
      if (window.cv && window.cv.Mat) {
        done(window.cv);
      } else {
        fail('cv.Mat indisponible après init');
      }
    };

    const script = document.createElement('script');
    script.src = 'https://docs.opencv.org/4.9.0/opencv.js';
    script.async = true;

    script.onerror = () => {
      clearTimeout(timer);
      fail('Échec réseau');
    };

    // Polling fallback (some builds skip onRuntimeInitialized)
    script.onload = () => {
      let attempts = 0;
      const poll = setInterval(() => {
        attempts++;
        if (window.cv && window.cv.Mat) {
          clearInterval(poll);
          clearTimeout(timer);
          done(window.cv);
        } else if (attempts > 60) {
          clearInterval(poll);
          clearTimeout(timer);
          fail('Init timeout après chargement');
        }
      }, 200);
    };

    document.head.appendChild(script);
  });

  return loadPromise;
}

export function isOpenCVReady() {
  return !!cvInstance;
}

export function getCV() {
  return cvInstance;
}
