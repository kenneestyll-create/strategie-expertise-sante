/**
 * Scanner Web Worker — OpenCV.js isolé du thread principal
 * Chargé uniquement ici, jamais dans le bundle React
 */

let cvReady = false;
let cv = null;

/* ── Load OpenCV inside worker ── */
async function initOpenCV() {
  if (cvReady) return true;
  try {
    self.Module = {
      onRuntimeInitialized: () => {
        cv = self.cv;
        cvReady = true;
      }
    };
    importScripts('https://docs.opencv.org/4.9.0/opencv.js');

    // Wait for runtime init (max 8s)
    let waited = 0;
    while (!cvReady && waited < 8000) {
      await new Promise(r => setTimeout(r, 100));
      waited += 100;
      // Some builds set cv directly
      if (!cvReady && self.cv && self.cv.Mat) {
        cv = self.cv;
        cvReady = true;
      }
    }
    return cvReady;
  } catch (e) {
    console.error('[Worker] OpenCV load failed:', e);
    return false;
  }
}

/* ── Helpers ── */
function orderPoints(pts) {
  const sorted = [...pts];
  sorted.sort((a, b) => (a.x + a.y) - (b.x + b.y));
  const tl = sorted[0], br = sorted[3];
  sorted.sort((a, b) => (a.y - a.x) - (b.y - b.x));
  const tr = sorted[0], bl = sorted[3];
  return [tl, tr, br, bl];
}

function dist(a, b) { return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2); }

/* ── Detect document edges ── */
function detectDocument(src) {
  const gray = new cv.Mat();
  const blurred = new cv.Mat();
  const edges = new cv.Mat();

  try {
    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);
    cv.GaussianBlur(gray, blurred, new cv.Size(5, 5), 0);

    for (const [lo, hi] of [[50, 150], [30, 100], [75, 200]]) {
      cv.Canny(blurred, edges, lo, hi);
      const k = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(3, 3));
      cv.dilate(edges, edges, k);
      k.delete();

      const contours = new cv.MatVector();
      const hier = new cv.Mat();
      cv.findContours(edges, contours, hier, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);

      const area = src.rows * src.cols;
      let best = null, bestA = 0;

      for (let i = 0; i < contours.size(); i++) {
        const c = contours.get(i);
        const a = cv.contourArea(c);
        if (a < area * 0.1) continue;
        const approx = new cv.Mat();
        cv.approxPolyDP(c, approx, 0.02 * cv.arcLength(c, true), true);
        if (approx.rows === 4 && a > bestA) {
          const pts = [];
          for (let j = 0; j < 4; j++) pts.push({ x: approx.data32S[j * 2], y: approx.data32S[j * 2 + 1] });
          best = orderPoints(pts);
          bestA = a;
        }
        approx.delete();
      }
      contours.delete();
      hier.delete();
      if (best) return best;
    }
    return null;
  } finally {
    gray.delete();
    blurred.delete();
    edges.delete();
  }
}

/* ── Perspective warp ── */
function warpDocument(src, corners) {
  const [tl, tr, br, bl] = corners;
  const maxW = Math.round(Math.max(dist(tl, tr), dist(bl, br)));
  const maxH = Math.round(Math.max(dist(tl, bl), dist(tr, br)));

  const srcPts = cv.matFromArray(4, 1, cv.CV_32FC2, [tl.x, tl.y, tr.x, tr.y, br.x, br.y, bl.x, bl.y]);
  const dstPts = cv.matFromArray(4, 1, cv.CV_32FC2, [0, 0, maxW, 0, maxW, maxH, 0, maxH]);
  const M = cv.getPerspectiveTransform(srcPts, dstPts);
  const warped = new cv.Mat();
  cv.warpPerspective(src, warped, M, new cv.Size(maxW, maxH));
  srcPts.delete(); dstPts.delete(); M.delete();
  return warped;
}

/* ── Enhance document ── */
function enhance(src, mode) {
  const result = new cv.Mat();
  if (mode === 'original') { src.copyTo(result); return result; }

  const gray = new cv.Mat();
  if (src.channels() === 4) cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);
  else if (src.channels() === 3) cv.cvtColor(src, gray, cv.COLOR_RGB2GRAY);
  else src.copyTo(gray);

  const morphed = new cv.Mat();
  const kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, new cv.Size(21, 21));
  cv.morphologyEx(gray, morphed, cv.MORPH_CLOSE, kernel);
  const norm = new cv.Mat();
  cv.divide(gray, morphed, norm, 255.0);

  if (mode === 'bw') {
    cv.adaptiveThreshold(norm, result, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 21, 10);
  } else {
    const mm = cv.minMaxLoc(norm);
    const alpha = 255.0 / Math.max(1, mm.maxVal - mm.minVal);
    norm.convertTo(result, -1, alpha * 1.3, -mm.minVal * alpha + 10);
    const blur = new cv.Mat();
    cv.GaussianBlur(result, blur, new cv.Size(0, 0), 2.0);
    cv.addWeighted(result, 1.5, blur, -0.5, 0, result);
    blur.delete();
  }

  gray.delete(); morphed.delete(); kernel.delete(); norm.delete();
  return result;
}

/* ── Convert Mat to ImageData ── */
function matToImageData(mat) {
  let rgba;
  if (mat.type() === cv.CV_8UC1) {
    rgba = new cv.Mat();
    cv.cvtColor(mat, rgba, cv.COLOR_GRAY2RGBA);
  } else if (mat.type() === cv.CV_8UC3) {
    rgba = new cv.Mat();
    cv.cvtColor(mat, rgba, cv.COLOR_RGB2RGBA);
  } else {
    rgba = mat;
  }
  const data = new Uint8ClampedArray(rgba.data);
  const w = rgba.cols, h = rgba.rows;
  if (rgba !== mat) rgba.delete();
  return { data, width: w, height: h };
}

/* ── Full pipeline ── */
function processImage(imageData, width, height, filterMode) {
  const src = cv.matFromImageData(new ImageData(new Uint8ClampedArray(imageData), width, height));

  let corners = null;
  let autoDetected = false;
  try { corners = detectDocument(src); } catch (e) { console.warn('[Worker] detect failed:', e); }

  let processed;
  if (corners) {
    autoDetected = true;
    const warped = warpDocument(src, corners);
    processed = enhance(warped, filterMode);
    warped.delete();
  } else {
    processed = enhance(src, filterMode);
  }

  const result = matToImageData(processed);
  src.delete();
  processed.delete();

  return {
    imageData: result.data.buffer,
    width: result.width,
    height: result.height,
    corners,
    autoDetected,
    originalWidth: width,
    originalHeight: height,
  };
}

function reprocessWithCorners(imageData, width, height, corners, filterMode) {
  const src = cv.matFromImageData(new ImageData(new Uint8ClampedArray(imageData), width, height));
  const warped = warpDocument(src, corners);
  const processed = enhance(warped, filterMode);
  const result = matToImageData(processed);
  src.delete(); warped.delete(); processed.delete();
  return { imageData: result.data.buffer, width: result.width, height: result.height };
}

/* ── Message handler ── */
self.onmessage = async (e) => {
  const { type, id } = e.data;

  if (type === 'init') {
    const ok = await initOpenCV();
    self.postMessage({ id, type: 'init', success: ok });
    return;
  }

  if (!cvReady) {
    self.postMessage({ id, type: 'error', error: 'OpenCV not initialized' });
    return;
  }

  try {
    if (type === 'process') {
      const { imageData, width, height, filter } = e.data;
      const result = processImage(imageData, width, height, filter || 'document');
      self.postMessage({ id, type: 'result', ...result }, [result.imageData]);
    } else if (type === 'reprocess') {
      const { imageData, width, height, corners, filter } = e.data;
      const result = reprocessWithCorners(imageData, width, height, corners, filter || 'document');
      self.postMessage({ id, type: 'result', ...result }, [result.imageData]);
    }
  } catch (err) {
    self.postMessage({ id, type: 'error', error: err.message });
  }
};
