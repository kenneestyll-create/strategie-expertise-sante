/**
 * Scanner Worker Manager — Stateful pattern
 * Worker keeps image in memory. Operations don't re-transfer data.
 * API: initScanWorker → scanDocument → filter/rotate/crop/adjust → save
 */

let worker = null;
let ready = false;
let initFailed = false;
let msgId = 0;
const pending = new Map();

function getWorker() {
  if (worker) return worker;
  try {
    worker = new Worker('/scanner.worker.js?v=4');
    worker.onmessage = (e) => {
      const { id } = e.data;
      const cb = pending.get(id);
      if (cb) {
        pending.delete(id);
        cb(e.data);
      }
      if (e.data.type === 'init') {
        ready = e.data.success;
        if (!ready) initFailed = true;
        console.log(ready ? '[ScanWorker] Scanner prêt' : '[ScanWorker] Scanner init échoué');
      }
    };
    worker.onerror = (err) => {
      console.error('[ScanWorker] Worker error:', err.message);
      initFailed = true;
      for (const [, cb] of pending) cb({ type: 'error', error: 'Worker crashed' });
      pending.clear();
    };
    return worker;
  } catch (e) {
    console.error('[ScanWorker] Cannot create worker:', e);
    initFailed = true;
    return null;
  }
}

function sendMessage(data, transfer = [], timeoutMs = 8000) {
  return new Promise((resolve, reject) => {
    const w = getWorker();
    if (!w) return reject(new Error('No worker'));
    const id = ++msgId;
    const timer = setTimeout(() => { pending.delete(id); reject(new Error('Worker timeout')); }, timeoutMs);
    pending.set(id, (response) => {
      clearTimeout(timer);
      if (response.type === 'error') reject(new Error(response.error));
      else resolve(response);
    });
    w.postMessage({ ...data, id }, transfer);
  });
}

/** Parse preview response → ImageData + metadata */
function parsePreview(res) {
  return {
    imageData: new ImageData(new Uint8ClampedArray(res.imageData), res.width, res.height),
    width: res.width,
    height: res.height,
    corners: res.corners || null,
    autoDetected: !!res.autoDetected,
    originalWidth: res.originalWidth,
    originalHeight: res.originalHeight,
    filter: res.filter,
  };
}

/* ══════════════════════ PUBLIC API ══════════════════════ */

/** Initialize worker (call once, non-blocking) */
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

export function isScanReady() { return ready; }
export function isScanFailed() { return initFailed; }

/**
 * SCAN — Send image to worker for auto-detection + perspective correction
 * This is the initial capture. Image is stored in worker memory.
 * @param {ImageData} imageData - from canvas.getImageData()
 * @param {string} filter - 'document' | 'bw' | 'original'
 */
export async function scanDocument(imageData, filter = 'document') {
  const buffer = imageData.data.buffer.slice(0);
  const res = await sendMessage(
    { type: 'scan', imageData: buffer, width: imageData.width, height: imageData.height, filter },
    [buffer],
    15000
  );
  return parsePreview(res);
}

/**
 * FILTER — Change filter on stored image (no data transfer)
 * @param {string} filter - 'document' | 'bw' | 'original'
 */
export async function applyFilter(filter = 'document') {
  const res = await sendMessage({ type: 'filter', filter });
  return parsePreview(res);
}

/**
 * ROTATE — Rotate stored image 90° left or right
 * @param {string} direction - 'left' | 'right'
 */
export async function rotateImage(direction = 'right') {
  const res = await sendMessage({ type: 'rotate', direction });
  return parsePreview(res);
}

/**
 * CROP — Crop with rectangle {x0,y0,x1,y1} or 4-point {corners:[...]}
 * Coordinates are normalized [0..1] relative to original image.
 * @param {object} coords - { x0, y0, x1, y1 } or { corners: [{x,y},...] }
 */
export async function cropImage(coords) {
  const res = await sendMessage({ type: 'crop', coords });
  return parsePreview(res);
}

/**
 * ADJUST — Brightness/Contrast on stored image (no data transfer)
 * @param {number} brightness - [-100, 100]
 * @param {number} contrast - [-100, 100]
 */
export async function adjustImage(brightness = 0, contrast = 0) {
  const res = await sendMessage({ type: 'adjust', brightness, contrast });
  return parsePreview(res);
}

/**
 * SAVE — Finalize and return the current image
 * @returns {Promise<{imageData: ImageData, width, height}>}
 */
export async function saveImage() {
  const res = await sendMessage({ type: 'save' });
  return {
    imageData: new ImageData(new Uint8ClampedArray(res.imageData), res.width, res.height),
    width: res.width,
    height: res.height,
  };
}

/** Terminate worker and release memory */
export function terminateScanWorker() {
  if (worker) {
    worker.terminate();
    worker = null;
    ready = false;
    pending.clear();
  }
}
