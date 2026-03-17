/**
 * Lazy loader for OpenCV.js — loaded only when scanner opens
 */
let cvReady = false;
let cvPromise = null;

export function loadOpenCV() {
  if (cvReady && window.cv) return Promise.resolve(window.cv);
  if (cvPromise) return cvPromise;

  cvPromise = new Promise((resolve, reject) => {
    // Check if already loaded
    if (window.cv && window.cv.Mat) {
      cvReady = true;
      resolve(window.cv);
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://docs.opencv.org/4.9.0/opencv.js';
    script.async = true;

    // OpenCV.js sets window.cv and calls onOpenCvReady when ready
    window.onOpenCvReady = () => {
      cvReady = true;
      resolve(window.cv);
    };

    script.onerror = () => {
      cvPromise = null;
      reject(new Error('Impossible de charger OpenCV.js'));
    };

    // Timeout fallback (OpenCV.js can take time on mobile)
    const timeout = setTimeout(() => {
      if (!cvReady) {
        // Check if cv is available even without callback
        if (window.cv && window.cv.Mat) {
          cvReady = true;
          resolve(window.cv);
        }
      }
    }, 15000);

    script.onload = () => {
      // Some builds don't use onOpenCvReady callback
      const check = setInterval(() => {
        if (window.cv && window.cv.Mat) {
          clearInterval(check);
          clearTimeout(timeout);
          cvReady = true;
          resolve(window.cv);
        }
      }, 100);
      // Give up after 20s
      setTimeout(() => { clearInterval(check); clearTimeout(timeout); }, 20000);
    };

    document.head.appendChild(script);
  });

  return cvPromise;
}

export function isOpenCVReady() {
  return cvReady && !!window.cv;
}
