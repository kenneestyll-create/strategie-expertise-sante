/**
 * scanner.worker.js — Web Worker avec OffscreenCanvas + OpenCV.js
 * Auto-crop robuste : segmentation par luminosite + detection de contours
 */

let currentCanvas = null;
let currentCtx = null;
let originalImage = null;
let cvReady = false;

/* =========================================================
 * INITIALISATION OPENCV
 * ========================================================= */
(async function initOpenCV() {
  try {
    importScripts('/workers/opencv.js');

    if (typeof cv !== 'undefined') {
      if (typeof cv === 'function' || (cv && typeof cv.then === 'function')) {
        cv = await cv;
      }
      if (cv && typeof cv.Mat === 'function' && typeof cv.findContours === 'function') {
        cvReady = true;
      } else if (cv && cv.onRuntimeInitialized !== undefined) {
        await new Promise((resolve, reject) => {
          const timeout = setTimeout(() => reject(new Error('timeout')), 30000);
          cv['onRuntimeInitialized'] = () => { clearTimeout(timeout); resolve(); };
        });
        cvReady = typeof cv.findContours === 'function';
      }
    }
  } catch (e) {
    console.warn('[scanner.worker] OpenCV unavailable:', e.message);
    cvReady = false;
  }

  self.postMessage({ type: 'ready', cvReady });
})();

function debug(msg) {
  self.postMessage({ type: 'debug', message: msg });
}

/* =========================================================
 * MESSAGE HANDLER
 * ========================================================= */
self.onmessage = async function (e) {
  const msg = e.data;

  if (msg.type === 'scan') {
    try {
      const bitmap = await createImageBitmap(msg.blob);
      currentCanvas = new OffscreenCanvas(bitmap.width, bitmap.height);
      currentCtx = currentCanvas.getContext('2d');
      currentCtx.drawImage(bitmap, 0, 0);
      bitmap.close();

      if (msg.autoCrop && cvReady) {
        try {
          debug('Auto-crop starting (' + currentCanvas.width + 'x' + currentCanvas.height + ')');
          const cropped = autoCropOpenCV(currentCanvas, currentCtx);
          if (cropped) {
            debug('Auto-crop success: ' + cropped.canvas.width + 'x' + cropped.canvas.height);
            currentCanvas = cropped.canvas;
            currentCtx = cropped.ctx;
          } else {
            debug('Auto-crop: no document detected, keeping original');
          }
        } catch (err) {
          debug('Auto-crop error: ' + err.message);
        }
      } else if (msg.autoCrop && !cvReady) {
        debug('Auto-crop skipped: OpenCV not loaded');
      }

      originalImage = currentCtx.getImageData(0, 0, currentCanvas.width, currentCanvas.height);
      await sendPreview();
    } catch (err) {
      self.postMessage({ type: 'error', error: err.message });
    }
    return;
  }

  if (msg.type === 'filter' && currentCanvas && originalImage) {
    let data = new ImageData(
      new Uint8ClampedArray(originalImage.data),
      originalImage.width, originalImage.height
    );
    if (msg.filter === 'bw') binarize(data);
    else if (msg.filter === 'enhanced') adjustContrast(data, 50);
    currentCanvas.width = data.width;
    currentCanvas.height = data.height;
    currentCtx = currentCanvas.getContext('2d');
    currentCtx.putImageData(data, 0, 0);
    await sendPreview();
    return;
  }

  if (msg.type === 'rotate' && currentCanvas) {
    const r = rotateCanvas(currentCanvas, msg.direction === 'left' ? -90 : 90);
    currentCanvas = r.canvas;
    currentCtx = r.ctx;
    originalImage = currentCtx.getImageData(0, 0, currentCanvas.width, currentCanvas.height);
    await sendPreview();
    return;
  }

  if (msg.type === 'save' && currentCanvas) {
    const blob = await currentCanvas.convertToBlob({ type: 'image/jpeg', quality: 0.95 });
    const buffer = await blob.arrayBuffer();
    self.postMessage({ type: 'saved', data: buffer }, [buffer]);
    return;
  }
};

/* =========================================================
 * AUTO-CROP — Strategie multi-approche
 * 1) Segmentation par luminosite (document blanc/clair)
 * 2) Detection de contours Canny (fallback)
 * 3) Rectangle englobant (dernier recours)
 * ========================================================= */

function autoCropOpenCV(canvas, ctx) {
  const w = canvas.width;
  const h = canvas.height;
  if (w < 100 || h < 100) return null;

  const imageData = ctx.getImageData(0, 0, w, h);

  // Downscale for faster detection
  const MAX_DETECT = 800;
  const scale = Math.min(1, MAX_DETECT / Math.max(w, h));
  const dw = Math.round(w * scale);
  const dh = Math.round(h * scale);

  let src = new cv.Mat(h, w, cv.CV_8UC4);
  src.data.set(imageData.data);

  let small = new cv.Mat();
  if (scale < 1) {
    cv.resize(src, small, new cv.Size(dw, dh), 0, 0, cv.INTER_AREA);
  } else {
    src.copyTo(small);
  }

  // Strategy 1: Brightness segmentation (best for white docs on darker backgrounds)
  debug('Trying brightness segmentation...');
  let corners = detectByBrightness(small, dw, dh);

  // Strategy 2: Edge detection with Canny
  if (!corners) {
    debug('Trying edge detection...');
    corners = detectByEdges(small, dw, dh);
  }

  // Strategy 3: Rotated bounding rect of bright region
  if (!corners) {
    debug('Trying bounding rect fallback...');
    corners = detectByBoundingRect(small, dw, dh);
  }

  small.delete();

  if (!corners) {
    src.delete();
    return null;
  }

  // Scale corners back to full resolution
  const scaledCorners = corners.map(p => ({
    x: Math.round(p.x / scale),
    y: Math.round(p.y / scale)
  }));

  debug('Document detected at: ' + scaledCorners.map(p => `(${p.x},${p.y})`).join(' '));

  const result = perspectiveTransform(src, scaledCorners);
  src.delete();
  return result;
}

/* ---------------------------------------------------------
 * Strategy 1: Brightness-based segmentation
 * Works for white/light documents on darker backgrounds
 * --------------------------------------------------------- */
function detectByBrightness(mat, w, h) {
  const imgArea = w * h;
  let gray = new cv.Mat();
  let blurred = new cv.Mat();
  let thresh = new cv.Mat();
  let closed = new cv.Mat();

  cv.cvtColor(mat, gray, cv.COLOR_RGBA2GRAY);

  // Large blur to smooth out texture (wood grain, text, etc.)
  cv.GaussianBlur(gray, blurred, new cv.Size(15, 15), 0);

  // Otsu threshold: automatically separates bright (paper) from dark (background)
  cv.threshold(blurred, thresh, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU);

  // Morphological close: fill gaps in the document (text, lines, etc.)
  let kernelClose = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(25, 25));
  cv.morphologyEx(thresh, closed, cv.MORPH_CLOSE, kernelClose);

  // Morphological open: remove small bright noise spots
  let kernelOpen = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(11, 11));
  cv.morphologyEx(closed, closed, cv.MORPH_OPEN, kernelOpen);

  let corners = findBestQuadrilateral(closed, w, h, imgArea);

  gray.delete(); blurred.delete(); thresh.delete(); closed.delete();
  kernelClose.delete(); kernelOpen.delete();

  if (corners) debug('Brightness segmentation: found document');
  return corners;
}

/* ---------------------------------------------------------
 * Strategy 2: Edge detection (Canny)
 * --------------------------------------------------------- */
function detectByEdges(mat, w, h) {
  const imgArea = w * h;
  let gray = new cv.Mat();
  let blurred = new cv.Mat();

  cv.cvtColor(mat, gray, cv.COLOR_RGBA2GRAY);
  cv.GaussianBlur(gray, blurred, new cv.Size(5, 5), 0);

  const thresholdSets = [[75, 200], [50, 150], [30, 100]];
  let bestCorners = null;
  let bestArea = 0;

  for (const [lo, hi] of thresholdSets) {
    let edges = new cv.Mat();
    cv.Canny(blurred, edges, lo, hi);

    let dilated = new cv.Mat();
    let kernel = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(5, 5));
    cv.dilate(edges, dilated, kernel, new cv.Point(-1, -1), 3);

    let corners = findBestQuadrilateral(dilated, w, h, imgArea);

    edges.delete(); dilated.delete(); kernel.delete();

    if (corners) {
      let area = quadArea(corners);
      if (area > bestArea) {
        bestCorners = corners;
        bestArea = area;
      }
      if (bestArea > imgArea * 0.2) break;
    }
  }

  gray.delete(); blurred.delete();

  if (bestCorners) debug('Edge detection: found document');
  return bestCorners;
}

/* ---------------------------------------------------------
 * Strategy 3: Rotated bounding rect of the bright region
 * Last resort - gives a rectangular crop even if edges aren't clean
 * --------------------------------------------------------- */
function detectByBoundingRect(mat, w, h) {
  const imgArea = w * h;
  let gray = new cv.Mat();
  let blurred = new cv.Mat();
  let thresh = new cv.Mat();
  let closed = new cv.Mat();

  cv.cvtColor(mat, gray, cv.COLOR_RGBA2GRAY);
  cv.GaussianBlur(gray, blurred, new cv.Size(21, 21), 0);
  cv.threshold(blurred, thresh, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU);

  let kernel = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(31, 31));
  cv.morphologyEx(thresh, closed, cv.MORPH_CLOSE, kernel);

  let contours = new cv.MatVector();
  let hierarchy = new cv.Mat();
  cv.findContours(closed, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);

  let bestCorners = null;
  let bestArea = 0;

  for (let i = 0; i < contours.size(); i++) {
    const area = cv.contourArea(contours.get(i));
    if (area > imgArea * 0.08 && area < imgArea * 0.98 && area > bestArea) {
      let cnt = contours.get(i);
      let rect = cv.minAreaRect(cnt);
      let vertices = cv.RotatedRect.points(rect);
      let points = vertices.map(v => ({ x: Math.round(v.x), y: Math.round(v.y) }));
      let ordered = orderPoints(points);
      let qArea = quadArea(ordered);
      if (qArea > imgArea * 0.08 && qArea < imgArea * 0.98) {
        bestCorners = ordered;
        bestArea = qArea;
      }
    }
  }

  gray.delete(); blurred.delete(); thresh.delete(); closed.delete();
  kernel.delete(); contours.delete(); hierarchy.delete();

  if (bestCorners) debug('Bounding rect fallback: found document');
  return bestCorners;
}

/* ---------------------------------------------------------
 * Find the best 4-point quadrilateral in a binary image
 * --------------------------------------------------------- */
function findBestQuadrilateral(binaryMat, w, h, imgArea) {
  let contours = new cv.MatVector();
  let hierarchy = new cv.Mat();
  cv.findContours(binaryMat, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);

  // Collect candidates sorted by area
  let candidates = [];
  for (let i = 0; i < contours.size(); i++) {
    const area = cv.contourArea(contours.get(i));
    if (area > imgArea * 0.08) candidates.push({ idx: i, area });
  }
  candidates.sort((a, b) => b.area - a.area);

  let bestCorners = null;
  let bestArea = 0;

  for (const { idx } of candidates.slice(0, 5)) {
    let cnt = contours.get(idx);
    let peri = cv.arcLength(cnt, true);
    let approx = new cv.Mat();

    // Try multiple epsilon values
    for (const eps of [0.02, 0.03, 0.04, 0.05, 0.06, 0.08]) {
      cv.approxPolyDP(cnt, approx, eps * peri, true);

      if (approx.rows === 4) {
        const approxArea = cv.contourArea(approx);
        if (approxArea > imgArea * 0.08 && approxArea < imgArea * 0.98 && approxArea > bestArea) {
          let points = [];
          for (let j = 0; j < 4; j++) {
            points.push({ x: approx.data32S[j * 2], y: approx.data32S[j * 2 + 1] });
          }
          if (isConvexQuad(points)) {
            bestCorners = orderPoints(points);
            bestArea = approxArea;
          }
        }
        break; // Found 4 points at this epsilon
      }
    }

    // If no 4-point found, try minAreaRect on this contour
    if (!bestCorners && cv.contourArea(cnt) > imgArea * 0.1) {
      let rect = cv.minAreaRect(cnt);
      let vertices = cv.RotatedRect.points(rect);
      let points = vertices.map(v => ({ x: Math.round(v.x), y: Math.round(v.y) }));
      let ordered = orderPoints(points);
      let qArea = quadArea(ordered);
      if (qArea > imgArea * 0.08 && qArea < imgArea * 0.98 && qArea > bestArea) {
        bestCorners = ordered;
        bestArea = qArea;
      }
    }

    approx.delete();
  }

  contours.delete(); hierarchy.delete();
  return bestCorners;
}

/* =========================================================
 * PERSPECTIVE TRANSFORM
 * ========================================================= */
function perspectiveTransform(src, corners) {
  const [tl, tr, br, bl] = corners;

  const wTop = Math.hypot(tr.x - tl.x, tr.y - tl.y);
  const wBot = Math.hypot(br.x - bl.x, br.y - bl.y);
  const dstW = Math.round(Math.max(wTop, wBot));

  const hLeft = Math.hypot(bl.x - tl.x, bl.y - tl.y);
  const hRight = Math.hypot(br.x - tr.x, br.y - tr.y);
  const dstH = Math.round(Math.max(hLeft, hRight));

  if (dstW < 50 || dstH < 50) return null;

  let srcPts = cv.matFromArray(4, 1, cv.CV_32FC2, [
    tl.x, tl.y, tr.x, tr.y, br.x, br.y, bl.x, bl.y
  ]);
  let dstPts = cv.matFromArray(4, 1, cv.CV_32FC2, [
    0, 0, dstW - 1, 0, dstW - 1, dstH - 1, 0, dstH - 1
  ]);

  let M = cv.getPerspectiveTransform(srcPts, dstPts);
  let warped = new cv.Mat();
  cv.warpPerspective(src, warped, M, new cv.Size(dstW, dstH));

  const croppedCanvas = new OffscreenCanvas(dstW, dstH);
  const croppedCtx = croppedCanvas.getContext('2d');
  const resultData = new ImageData(new Uint8ClampedArray(warped.data), dstW, dstH);
  croppedCtx.putImageData(resultData, 0, 0);

  srcPts.delete(); dstPts.delete(); M.delete(); warped.delete();
  return { canvas: croppedCanvas, ctx: croppedCtx };
}

/* =========================================================
 * GEOMETRY HELPERS
 * ========================================================= */

function orderPoints(pts) {
  const sums = pts.map(p => p.x + p.y);
  const diffs = pts.map(p => p.y - p.x);
  return [
    pts[sums.indexOf(Math.min(...sums))],   // TL
    pts[diffs.indexOf(Math.min(...diffs))],  // TR
    pts[sums.indexOf(Math.max(...sums))],    // BR
    pts[diffs.indexOf(Math.max(...diffs))],  // BL
  ];
}

function quadArea(corners) {
  // Shoelace formula for quadrilateral area
  const [a, b, c, d] = corners;
  return 0.5 * Math.abs(
    (a.x * b.y - b.x * a.y) +
    (b.x * c.y - c.x * b.y) +
    (c.x * d.y - d.x * c.y) +
    (d.x * a.y - a.x * d.y)
  );
}

function isConvexQuad(pts) {
  // Check if 4 points form a convex quadrilateral
  if (pts.length !== 4) return false;
  const cross = (o, a, b) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
  const ordered = orderPoints(pts);
  const c1 = cross(ordered[0], ordered[1], ordered[2]);
  const c2 = cross(ordered[1], ordered[2], ordered[3]);
  const c3 = cross(ordered[2], ordered[3], ordered[0]);
  const c4 = cross(ordered[3], ordered[0], ordered[1]);
  return (c1 > 0 && c2 > 0 && c3 > 0 && c4 > 0) || (c1 < 0 && c2 < 0 && c3 < 0 && c4 < 0);
}

/* =========================================================
 * UTILITAIRES
 * ========================================================= */

async function sendPreview() {
  const blob = await currentCanvas.convertToBlob({ type: 'image/jpeg', quality: 0.9 });
  const buffer = await blob.arrayBuffer();
  self.postMessage(
    { type: 'preview', data: buffer, width: currentCanvas.width, height: currentCanvas.height },
    [buffer]
  );
}

function binarize(imageData, thr) {
  if (thr === undefined) thr = 128;
  const d = imageData.data;
  for (let i = 0; i < d.length; i += 4) {
    const g = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
    d[i] = d[i + 1] = d[i + 2] = g > thr ? 255 : 0;
  }
}

function adjustContrast(imageData, contrast) {
  const f = (259 * (contrast + 255)) / (255 * (259 - contrast));
  const d = imageData.data;
  for (let i = 0; i < d.length; i += 4) {
    d[i] = Math.min(255, Math.max(0, f * (d[i] - 128) + 128));
    d[i + 1] = Math.min(255, Math.max(0, f * (d[i + 1] - 128) + 128));
    d[i + 2] = Math.min(255, Math.max(0, f * (d[i + 2] - 128) + 128));
  }
}

function rotateCanvas(canvas, angle) {
  const rad = (angle * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  const nW = Math.round(Math.abs(canvas.width * cos) + Math.abs(canvas.height * sin));
  const nH = Math.round(Math.abs(canvas.width * sin) + Math.abs(canvas.height * cos));
  const r = new OffscreenCanvas(nW, nH);
  const ctx = r.getContext('2d');
  ctx.translate(nW / 2, nH / 2);
  ctx.rotate(rad);
  ctx.drawImage(canvas, -canvas.width / 2, -canvas.height / 2);
  return { canvas: r, ctx };
}
