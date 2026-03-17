/**
 * Scanner Worker Manager — Stateful pattern with mandatory timeouts
 * Every promise MUST resolve or reject. No hanging allowed.
 */

let worker = null;
let ready = false;
let initFailed = false;
let msgId = 0;
const pending = new Map();

/* ── Timeout built into sendMessage — no promise hangs ever ── */

function getWorker() {
  if (worker) return worker;
  try {
    worker = new Worker('/scanner.worker.js?v=5');
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
        console.error(`[ScanWorker] Rejecting pending id=${id}`);
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

function sendMessage(data, transfer = [], timeoutMs = 8000) {
  const label = data.type || 'unknown';
  console.log(`[ScanWorker] SEND type=${label}`);
  return new Promise((resolve, reject) => {
    const w = getWorker();
    if (!w) return reject(new Error('No worker'));
    const id = ++msgId;
    const timer = setTimeout(() => {
      pending.delete(id);
      console.error(`[ScanWorker] TIMEOUT ${timeoutMs}ms on ${label} id=${id}`);
      reject(new Error(`Timeout ${timeoutMs}ms on ${label}`));
    }, timeoutMs);
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

export async function initScanWorker() {
  if (ready) { console.log('[ScanWorker] Already ready'); return true; }
  if (initFailed) { console.log('[ScanWorker] Already failed'); return false; }
  console.log('INIT START');
  try {
    const res = await sendMessage({ type: 'init' }, [], 10000);
    console.log('INIT DONE success=' + res.success);
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
  try {
    const buffer = imageData.data.buffer.slice(0);
    const res = await sendMessage(
      { type: 'scan', imageData: buffer, width: imageData.width, height: imageData.height, filter },
      [buffer],
      15000
    );
    console.log('SCAN DONE');
    return parsePreview(res);
  } catch (err) {
    console.error('SCAN FAIL:', err.message);
    throw err;
  }
}

export async function applyFilter(filter = 'document') {
  console.log('FILTER START:', filter);
  try {
    const res = await sendMessage({ type: 'filter', filter }, [], 5000);
    console.log('FILTER DONE');
    return parsePreview(res);
  } catch (err) {
    console.error('FILTER FAIL:', err.message);
    throw err;
  }
}

export async function rotateImage(direction = 'right') {
  console.log('ROTATE START:', direction);
  try {
    const res = await sendMessage({ type: 'rotate', direction }, [], 5000);
    console.log('ROTATE DONE');
    return parsePreview(res);
  } catch (err) {
    console.error('ROTATE FAIL:', err.message);
    throw err;
  }
}

export async function cropImage(coords) {
  console.log('CROP START');
  try {
    const res = await sendMessage({ type: 'crop', coords }, [], 5000);
    console.log('CROP DONE');
    return parsePreview(res);
  } catch (err) {
    console.error('CROP FAIL:', err.message);
    throw err;
  }
}

export async function adjustImage(brightness = 0, contrast = 0) {
  console.log('ADJUST START b=' + brightness + ' c=' + contrast);
  try {
    const res = await sendMessage({ type: 'adjust', brightness, contrast }, [], 5000);
    console.log('ADJUST DONE');
    return parsePreview(res);
  } catch (err) {
    console.error('ADJUST FAIL:', err.message);
    throw err;
  }
}

export async function saveImage() {
  console.log('SAVE START');
  try {
    const res = await sendMessage({ type: 'save' }, [], 5000);
    console.log('SAVE DONE');
    return {
      imageData: new ImageData(new Uint8ClampedArray(res.imageData), res.width, res.height),
      width: res.width,
      height: res.height,
    };
  } catch (err) {
    console.error('SAVE FAIL:', err.message);
    throw err;
  }
}

export function terminateScanWorker() {
  console.log('[ScanWorker] TERMINATE');
  if (worker) {
    worker.terminate();
    worker = null;
    ready = false;
    for (const [id, cb] of pending) {
      console.log(`[ScanWorker] Cancelling pending id=${id}`);
      cb({ type: 'error', error: 'Worker terminated' });
    }
    pending.clear();
  }
}
