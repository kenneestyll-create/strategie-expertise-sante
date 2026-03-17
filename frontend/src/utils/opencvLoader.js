/**
 * Scanner Worker Manager
 * Pure-JS scanner runs ONLY inside the Web Worker — never in main thread.
 * Communication via postMessage, 5s timeout per operation, guaranteed fallback.
 */

let worker = null;
let ready = false;
let initFailed = false;
let msgId = 0;
const pending = new Map();

function getWorker() {
  if (worker) return worker;
  try {
    // Cache-bust to ensure latest worker version
    worker = new Worker('/scanner.worker.js?v=2');
    worker.onmessage = (e) => {
      const { id, type } = e.data;
      const cb = pending.get(id);
      if (cb) {
        pending.delete(id);
        cb(e.data);
      }
      if (type === 'init') {
        ready = e.data.success;
        if (!ready) initFailed = true;
        console.log(ready ? '[ScanWorker] Scanner prêt' : '[ScanWorker] Scanner init échoué');
      }
    };
    worker.onerror = (err) => {
      console.error('[ScanWorker] Worker error:', err.message);
      initFailed = true;
      for (const [, cb] of pending) {
        cb({ type: 'error', error: 'Worker crashed' });
      }
      pending.clear();
    };
    return worker;
  } catch (e) {
    console.error('[ScanWorker] Cannot create worker:', e);
    initFailed = true;
    return null;
  }
}

function sendMessage(data, transfer = [], timeoutMs = 5000) {
  return new Promise((resolve, reject) => {
    const w = getWorker();
    if (!w) return reject(new Error('No worker'));

    const id = ++msgId;
    const timer = setTimeout(() => {
      pending.delete(id);
      reject(new Error('Worker timeout'));
    }, timeoutMs);

    pending.set(id, (response) => {
      clearTimeout(timer);
      if (response.type === 'error') reject(new Error(response.error));
      else resolve(response);
    });

    w.postMessage({ ...data, id }, transfer);
  });
}

/** Initialize scanner worker (non-blocking, call early) */
export async function initScanWorker() {
  if (ready) return true;
  if (initFailed) return false;
  try {
    const res = await sendMessage({ type: 'init' }, [], 10000);
    return res.success;
  } catch {
    initFailed = true;
    return false;
  }
}

/** Check if worker is ready */
export function isScanReady() {
  return ready;
}

/** Check if init was attempted and failed */
export function isScanFailed() {
  return initFailed;
}

/**
 * Process image in worker
 * @param {ImageData} imageData - from canvas.getImageData()
 * @param {string} filter - 'document' | 'bw' | 'original'
 * @returns {Promise<{imageData, width, height, corners, autoDetected}>}
 */
export async function processInWorker(imageData, filter = 'document') {
  const buffer = imageData.data.buffer.slice(0);
  const res = await sendMessage(
    { type: 'process', imageData: buffer, width: imageData.width, height: imageData.height, filter },
    [buffer],
    8000
  );
  return {
    imageData: new ImageData(new Uint8ClampedArray(res.imageData), res.width, res.height),
    width: res.width,
    height: res.height,
    corners: res.corners,
    autoDetected: res.autoDetected,
    originalWidth: res.originalWidth,
    originalHeight: res.originalHeight,
  };
}

/**
 * Reprocess with manual corners
 */
export async function reprocessInWorker(imageData, corners, filter = 'document') {
  const buffer = imageData.data.buffer.slice(0);
  const res = await sendMessage(
    { type: 'reprocess', imageData: buffer, width: imageData.width, height: imageData.height, corners, filter },
    [buffer],
    8000
  );
  return {
    imageData: new ImageData(new Uint8ClampedArray(res.imageData), res.width, res.height),
    width: res.width,
    height: res.height,
  };
}

/**
 * Adjust brightness/contrast on image
 * @param {ImageData} imageData
 * @param {number} brightness - [-100, 100]
 * @param {number} contrast - [-100, 100]
 */
export async function adjustInWorker(imageData, brightness = 0, contrast = 0) {
  const buffer = imageData.data.buffer.slice(0);
  const res = await sendMessage(
    { type: 'adjust', imageData: buffer, width: imageData.width, height: imageData.height, brightness, contrast },
    [buffer],
    5000
  );
  return {
    imageData: new ImageData(new Uint8ClampedArray(res.imageData), res.width, res.height),
    width: res.width,
    height: res.height,
  };
}

/**
 * Rotate image by 90° increments
 * @param {ImageData} imageData
 * @param {number} degrees - 90, 180, 270
 */
export async function rotateInWorker(imageData, degrees = 90) {
  const buffer = imageData.data.buffer.slice(0);
  const res = await sendMessage(
    { type: 'rotate', imageData: buffer, width: imageData.width, height: imageData.height, degrees },
    [buffer],
    5000
  );
  return {
    imageData: new ImageData(new Uint8ClampedArray(res.imageData), res.width, res.height),
    width: res.width,
    height: res.height,
  };
}

/** Terminate worker */
export function terminateScanWorker() {
  if (worker) {
    worker.terminate();
    worker = null;
    ready = false;
    pending.clear();
  }
}
