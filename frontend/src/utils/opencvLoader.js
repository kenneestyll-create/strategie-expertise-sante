/**
 * Scanner Worker Manager — Timeouts obligatoires 2s max
 * Chaque promesse DOIT résoudre ou rejeter. Zéro blocage.
 */

let worker = null;
let ready = false;
let initFailed = false;
let msgId = 0;
const pending = new Map();

const TIMEOUT_MS = 2000; // 2 secondes max pour TOUTE opération

function getWorker() {
  if (worker) return worker;
  try {
    worker = new Worker('/scanner.worker.js?v=6');
    worker.onmessage = (e) => {
      const { id, type } = e.data;
      console.log(`[ScanWorker] RECV type=${type} id=${id}`);
      const cb = pending.get(id);
      if (cb) {
        pending.delete(id);
        cb(e.data);
      }
      if (type === 'init') {
        ready = e.data.success;
        if (!ready) initFailed = true;
        console.log(ready ? '[ScanWorker] INIT OK' : '[ScanWorker] INIT FAIL');
      }
    };
    worker.onerror = (err) => {
      console.error('[ScanWorker] WORKER CRASH:', err.message);
      initFailed = true;
      for (const [id, cb] of pending) {
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

function sendMessage(data, transfer = [], timeoutMs = TIMEOUT_MS) {
  const label = data.type || 'unknown';
  console.log(`[ScanWorker] SEND ${label}`);
  return new Promise((resolve, reject) => {
    const w = getWorker();
    if (!w) return reject(new Error('No worker'));
    const id = ++msgId;
    const timer = setTimeout(() => {
      pending.delete(id);
      console.error(`[ScanWorker] TIMEOUT ${timeoutMs}ms on ${label} id=${id}`);
      reject(new Error(`Timeout ${label}`));
    }, timeoutMs);
    pending.set(id, (response) => {
      clearTimeout(timer);
      if (response.type === 'error') reject(new Error(response.error));
      else resolve(response);
    });
    w.postMessage({ ...data, id }, transfer);
  });
}

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

export async function initScanWorker() {
  if (ready) return true;
  if (initFailed) return false;
  console.log('INIT START');
  try {
    const res = await sendMessage({ type: 'init' }, [], TIMEOUT_MS);
    console.log('INIT DONE');
    return res.success;
  } catch (err) {
    console.error('INIT FAIL:', err.message);
    initFailed = true;
    return false;
  }
}

export function isScanReady() { return ready; }
export function isScanFailed() { return initFailed; }

export async function scanDocument(imageData, filter = 'document') {
  console.log('SCAN START');
  const buffer = imageData.data.buffer.slice(0);
  const res = await sendMessage(
    { type: 'scan', imageData: buffer, width: imageData.width, height: imageData.height, filter },
    [buffer],
    TIMEOUT_MS
  );
  console.log('SCAN DONE');
  return parsePreview(res);
}

export async function applyFilter(filter = 'document') {
  console.log('FILTER START:', filter);
  const res = await sendMessage({ type: 'filter', filter }, [], TIMEOUT_MS);
  console.log('FILTER DONE');
  return parsePreview(res);
}

export async function rotateImage(direction = 'right') {
  console.log('ROTATE START:', direction);
  const res = await sendMessage({ type: 'rotate', direction }, [], TIMEOUT_MS);
  console.log('ROTATE DONE');
  return parsePreview(res);
}

export async function cropImage(coords) {
  console.log('CROP START');
  const res = await sendMessage({ type: 'crop', coords }, [], TIMEOUT_MS);
  console.log('CROP DONE');
  return parsePreview(res);
}

export async function adjustImage(brightness = 0, contrast = 0) {
  console.log('ADJUST START b=' + brightness + ' c=' + contrast);
  const res = await sendMessage({ type: 'adjust', brightness, contrast }, [], TIMEOUT_MS);
  console.log('ADJUST DONE');
  return parsePreview(res);
}

export async function saveImage() {
  console.log('SAVE START');
  const res = await sendMessage({ type: 'save' }, [], TIMEOUT_MS);
  console.log('SAVE DONE');
  return {
    imageData: new ImageData(new Uint8ClampedArray(res.imageData), res.width, res.height),
    width: res.width,
    height: res.height,
  };
}

export function terminateScanWorker() {
  console.log('[ScanWorker] TERMINATE');
  if (worker) {
    worker.terminate();
    worker = null;
    ready = false;
    for (const [, cb] of pending) {
      cb({ type: 'error', error: 'Worker terminated' });
    }
    pending.clear();
  }
}
