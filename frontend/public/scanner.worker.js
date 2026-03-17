/**
 * Pure-JS Document Scanner Worker
 * No OpenCV, no WASM — just math on pixel arrays.
 * Provides: edge detection, rectangle finding, perspective correction, enhancement.
 */

/* ════════════════════ IMAGE PROCESSING PRIMITIVES ════════════════════ */

/** RGBA ImageData → grayscale Float32Array */
function toGray(data, w, h) {
  const out = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) {
    const j = i * 4;
    out[i] = 0.299 * data[j] + 0.587 * data[j + 1] + 0.114 * data[j + 2];
  }
  return out;
}

/** Gaussian blur (separable, σ ≈ 1.4, kernel size 5) */
function gaussianBlur(gray, w, h) {
  const k = [0.06136, 0.24477, 0.38774, 0.24477, 0.06136];
  const tmp = new Float32Array(w * h);
  const out = new Float32Array(w * h);
  // Horizontal
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      let s = 0;
      for (let ki = -2; ki <= 2; ki++) {
        const cx = Math.min(w - 1, Math.max(0, x + ki));
        s += gray[y * w + cx] * k[ki + 2];
      }
      tmp[y * w + x] = s;
    }
  }
  // Vertical
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      let s = 0;
      for (let ki = -2; ki <= 2; ki++) {
        const cy = Math.min(h - 1, Math.max(0, y + ki));
        s += tmp[cy * w + x] * k[ki + 2];
      }
      out[y * w + x] = s;
    }
  }
  return out;
}

/** Sobel gradients → magnitude + direction */
function sobel(gray, w, h) {
  const mag = new Float32Array(w * h);
  const dir = new Float32Array(w * h);
  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      const i = y * w + x;
      const gx =
        -gray[(y - 1) * w + (x - 1)] + gray[(y - 1) * w + (x + 1)]
        - 2 * gray[y * w + (x - 1)] + 2 * gray[y * w + (x + 1)]
        - gray[(y + 1) * w + (x - 1)] + gray[(y + 1) * w + (x + 1)];
      const gy =
        -gray[(y - 1) * w + (x - 1)] - 2 * gray[(y - 1) * w + x] - gray[(y - 1) * w + (x + 1)]
        + gray[(y + 1) * w + (x - 1)] + 2 * gray[(y + 1) * w + x] + gray[(y + 1) * w + (x + 1)];
      mag[i] = Math.sqrt(gx * gx + gy * gy);
      dir[i] = Math.atan2(gy, gx);
    }
  }
  return { mag, dir };
}

/** Canny-like edge detection */
function cannyEdges(gray, w, h, lo, hi) {
  const blurred = gaussianBlur(gray, w, h);
  const { mag, dir } = sobel(blurred, w, h);

  // Non-maximum suppression
  const nms = new Float32Array(w * h);
  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      const i = y * w + x;
      const angle = ((dir[i] * 180 / Math.PI) + 180) % 180;
      let n1 = 0, n2 = 0;
      if (angle < 22.5 || angle >= 157.5) { n1 = mag[i - 1]; n2 = mag[i + 1]; }
      else if (angle < 67.5) { n1 = mag[(y - 1) * w + (x + 1)]; n2 = mag[(y + 1) * w + (x - 1)]; }
      else if (angle < 112.5) { n1 = mag[(y - 1) * w + x]; n2 = mag[(y + 1) * w + x]; }
      else { n1 = mag[(y - 1) * w + (x - 1)]; n2 = mag[(y + 1) * w + (x + 1)]; }
      nms[i] = (mag[i] >= n1 && mag[i] >= n2) ? mag[i] : 0;
    }
  }

  // Double threshold + hysteresis
  const edges = new Uint8Array(w * h);
  for (let i = 0; i < w * h; i++) {
    if (nms[i] >= hi) edges[i] = 255;
    else if (nms[i] >= lo) edges[i] = 128;
  }
  // Simple hysteresis: promote weak edges adjacent to strong
  let changed = true;
  while (changed) {
    changed = false;
    for (let y = 1; y < h - 1; y++) {
      for (let x = 1; x < w - 1; x++) {
        const i = y * w + x;
        if (edges[i] !== 128) continue;
        for (let dy = -1; dy <= 1; dy++) {
          for (let dx = -1; dx <= 1; dx++) {
            if (edges[(y + dy) * w + (x + dx)] === 255) {
              edges[i] = 255;
              changed = true;
              break;
            }
          }
          if (edges[i] === 255) break;
        }
      }
    }
  }
  // Remove weak edges
  for (let i = 0; i < w * h; i++) if (edges[i] !== 255) edges[i] = 0;
  return edges;
}

/** Simple dilation (3x3) */
function dilate(edges, w, h) {
  const out = new Uint8Array(w * h);
  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      let v = 0;
      for (let dy = -1; dy <= 1; dy++)
        for (let dx = -1; dx <= 1; dx++)
          if (edges[(y + dy) * w + (x + dx)]) { v = 255; break; }
      out[y * w + x] = v;
    }
  }
  return out;
}

/* ════════════════════ CONTOUR DETECTION ════════════════════ */

/** Find connected components and extract contour polygons from binary edge image */
function findContours(edges, w, h) {
  const visited = new Uint8Array(w * h);
  const contours = [];

  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      if (edges[y * w + x] === 0 || visited[y * w + x]) continue;
      // BFS to trace contour
      const points = [];
      const queue = [{ x, y }];
      visited[y * w + x] = 1;
      while (queue.length > 0) {
        const p = queue.shift();
        points.push(p);
        for (const [dx, dy] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, -1], [-1, 1], [1, 1]]) {
          const nx = p.x + dx, ny = p.y + dy;
          if (nx >= 0 && nx < w && ny >= 0 && ny < h && !visited[ny * w + nx] && edges[ny * w + nx]) {
            visited[ny * w + nx] = 1;
            queue.push({ x: nx, y: ny });
          }
        }
      }
      if (points.length > 50) contours.push(points);
    }
  }
  return contours;
}

/** Approximate a contour to fewer points (Ramer-Douglas-Peucker) */
function approxPoly(points, epsilon) {
  if (points.length <= 2) return points;

  // Find convex hull first for better approximation
  const hull = convexHull(points);
  if (hull.length <= 2) return hull;

  return rdp(hull, epsilon);
}

function rdp(points, epsilon) {
  if (points.length <= 2) return points;
  let maxDist = 0, maxIdx = 0;
  const first = points[0], last = points[points.length - 1];
  for (let i = 1; i < points.length - 1; i++) {
    const d = pointLineDistance(points[i], first, last);
    if (d > maxDist) { maxDist = d; maxIdx = i; }
  }
  if (maxDist > epsilon) {
    const left = rdp(points.slice(0, maxIdx + 1), epsilon);
    const right = rdp(points.slice(maxIdx), epsilon);
    return left.slice(0, -1).concat(right);
  }
  return [first, last];
}

function pointLineDistance(p, a, b) {
  const num = Math.abs((b.y - a.y) * p.x - (b.x - a.x) * p.y + b.x * a.y - b.y * a.x);
  const den = Math.sqrt((b.y - a.y) ** 2 + (b.x - a.x) ** 2);
  return den === 0 ? Math.sqrt((p.x - a.x) ** 2 + (p.y - a.y) ** 2) : num / den;
}

/** Simple convex hull (Graham scan) */
function convexHull(points) {
  if (points.length <= 3) return [...points];

  const sorted = [...points].sort((a, b) => a.x - b.x || a.y - b.y);
  const cross = (O, A, B) => (A.x - O.x) * (B.y - O.y) - (A.y - O.y) * (B.x - O.x);

  const lower = [];
  for (const p of sorted) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) lower.pop();
    lower.push(p);
  }
  const upper = [];
  for (let i = sorted.length - 1; i >= 0; i--) {
    const p = sorted[i];
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) upper.pop();
    upper.push(p);
  }
  return lower.slice(0, -1).concat(upper.slice(0, -1));
}

/** Area of polygon using shoelace formula */
function polygonArea(pts) {
  let a = 0;
  for (let i = 0; i < pts.length; i++) {
    const j = (i + 1) % pts.length;
    a += pts[i].x * pts[j].y - pts[j].x * pts[i].y;
  }
  return Math.abs(a) / 2;
}

/** Perimeter of polygon */
function polyPerimeter(pts) {
  let p = 0;
  for (let i = 0; i < pts.length; i++) {
    const j = (i + 1) % pts.length;
    p += Math.sqrt((pts[j].x - pts[i].x) ** 2 + (pts[j].y - pts[i].y) ** 2);
  }
  return p;
}

/** Order 4 corner points: [topLeft, topRight, bottomRight, bottomLeft] */
function orderCorners(pts) {
  const s = [...pts];
  // Sort by sum (x+y): smallest = TL, largest = BR
  s.sort((a, b) => (a.x + a.y) - (b.x + b.y));
  const tl = s[0], br = s[3];
  // Sort by difference (y-x): smallest = TR, largest = BL
  s.sort((a, b) => (a.y - a.x) - (b.y - b.x));
  const tr = s[0], bl = s[3];
  return [tl, tr, br, bl];
}

/** Detect document rectangle in edge image */
function detectDocument(edges, w, h, imgArea) {
  const contours = findContours(edges, w, h);
  let bestCorners = null, bestArea = 0;

  for (const contour of contours) {
    const area = polygonArea(convexHull(contour));
    if (area < imgArea * 0.08) continue; // Too small

    const perim = polyPerimeter(convexHull(contour));
    const epsilon = 0.02 * perim;
    const approx = approxPoly(contour, epsilon);

    if (approx.length === 4 && area > bestArea) {
      bestCorners = orderCorners(approx);
      bestArea = area;
    }
  }
  return bestCorners;
}

/* ════════════════════ PERSPECTIVE TRANSFORM ════════════════════ */

function dist(a, b) { return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2); }

/**
 * 4-point perspective transform using bilinear interpolation.
 * corners = [TL, TR, BR, BL]
 */
function perspectiveWarp(srcData, srcW, srcH, corners) {
  const [tl, tr, br, bl] = corners;
  const outW = Math.round(Math.max(dist(tl, tr), dist(bl, br)));
  const outH = Math.round(Math.max(dist(tl, bl), dist(tr, br)));

  // Compute 3x3 perspective matrix via DLT (Direct Linear Transform)
  const M = computePerspectiveMatrix(
    [tl.x, tl.y, tr.x, tr.y, br.x, br.y, bl.x, bl.y],
    [0, 0, outW, 0, outW, outH, 0, outH]
  );

  // Invert to map destination → source
  const Mi = invert3x3(M);
  if (!Mi) return { data: srcData, width: srcW, height: srcH };

  const out = new Uint8ClampedArray(outW * outH * 4);
  for (let y = 0; y < outH; y++) {
    for (let x = 0; x < outW; x++) {
      // Map (x, y) in dst to (sx, sy) in src
      const denom = Mi[6] * x + Mi[7] * y + Mi[8];
      const sx = (Mi[0] * x + Mi[1] * y + Mi[2]) / denom;
      const sy = (Mi[3] * x + Mi[4] * y + Mi[5]) / denom;

      // Bilinear interpolation
      const ix = Math.floor(sx), iy = Math.floor(sy);
      if (ix < 0 || ix >= srcW - 1 || iy < 0 || iy >= srcH - 1) continue;

      const fx = sx - ix, fy = sy - iy;
      const di = (y * outW + x) * 4;
      for (let c = 0; c < 4; c++) {
        const v00 = srcData[(iy * srcW + ix) * 4 + c];
        const v10 = srcData[(iy * srcW + ix + 1) * 4 + c];
        const v01 = srcData[((iy + 1) * srcW + ix) * 4 + c];
        const v11 = srcData[((iy + 1) * srcW + ix + 1) * 4 + c];
        out[di + c] = Math.round(v00 * (1 - fx) * (1 - fy) + v10 * fx * (1 - fy) + v01 * (1 - fx) * fy + v11 * fx * fy);
      }
    }
  }
  return { data: out, width: outW, height: outH };
}

/** Compute 3x3 perspective matrix from 4 point correspondences using DLT */
function computePerspectiveMatrix(src, dst) {
  // Build 8x8 system: A * h = b
  const A = [];
  const b = [];
  for (let i = 0; i < 4; i++) {
    const sx = src[i * 2], sy = src[i * 2 + 1];
    const dx = dst[i * 2], dy = dst[i * 2 + 1];
    A.push([sx, sy, 1, 0, 0, 0, -dx * sx, -dx * sy]);
    b.push(dx);
    A.push([0, 0, 0, sx, sy, 1, -dy * sx, -dy * sy]);
    b.push(dy);
  }
  const h = solveLinear8(A, b);
  return [h[0], h[1], h[2], h[3], h[4], h[5], h[6], h[7], 1];
}

/** Solve 8x8 linear system via Gaussian elimination */
function solveLinear8(A, b) {
  const n = 8;
  const aug = A.map((row, i) => [...row, b[i]]);
  for (let col = 0; col < n; col++) {
    let maxRow = col;
    for (let row = col + 1; row < n; row++)
      if (Math.abs(aug[row][col]) > Math.abs(aug[maxRow][col])) maxRow = row;
    [aug[col], aug[maxRow]] = [aug[maxRow], aug[col]];
    if (Math.abs(aug[col][col]) < 1e-10) return [1, 0, 0, 0, 1, 0, 0, 0]; // fallback identity
    for (let row = col + 1; row < n; row++) {
      const f = aug[row][col] / aug[col][col];
      for (let j = col; j <= n; j++) aug[row][j] -= f * aug[col][j];
    }
  }
  const x = new Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    x[i] = aug[i][n];
    for (let j = i + 1; j < n; j++) x[i] -= aug[i][j] * x[j];
    x[i] /= aug[i][i];
  }
  return x;
}

/** Invert a 3x3 matrix */
function invert3x3(m) {
  const [a, b, c, d, e, f, g, h, i] = m;
  const det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
  if (Math.abs(det) < 1e-10) return null;
  const inv = 1 / det;
  return [
    (e * i - f * h) * inv, (c * h - b * i) * inv, (b * f - c * e) * inv,
    (f * g - d * i) * inv, (a * i - c * g) * inv, (c * d - a * f) * inv,
    (d * h - e * g) * inv, (b * g - a * h) * inv, (a * e - b * d) * inv,
  ];
}

/* ════════════════════ IMAGE ENHANCEMENT ════════════════════ */

/** Document-mode enhancement: normalize lighting + sharpen */
function enhanceDocument(srcData, w, h) {
  // Convert to grayscale
  const gray = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) {
    const j = i * 4;
    gray[i] = 0.299 * srcData[j] + 0.587 * srcData[j + 1] + 0.114 * srcData[j + 2];
  }

  // Estimate background via large-kernel box blur (morphology-like)
  const bgRadius = Math.max(10, Math.round(Math.min(w, h) / 30));
  const bg = boxBlur(gray, w, h, bgRadius);

  // Normalize: pixel / background * 255
  const norm = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) {
    norm[i] = bg[i] > 1 ? Math.min(255, (gray[i] / bg[i]) * 255) : gray[i];
  }

  // Contrast stretch
  let min = 255, max = 0;
  for (let i = 0; i < w * h; i++) { if (norm[i] < min) min = norm[i]; if (norm[i] > max) max = norm[i]; }
  const range = Math.max(1, max - min);

  // Unsharp mask
  const blurred = boxBlur(norm, w, h, 2);

  const out = new Uint8ClampedArray(w * h * 4);
  for (let i = 0; i < w * h; i++) {
    const stretched = ((norm[i] - min) / range) * 255;
    const sharp = Math.min(255, Math.max(0, stretched * 1.5 - blurred[i] * 0.5 + 10));
    const v = Math.round(sharp);
    const j = i * 4;
    out[j] = out[j + 1] = out[j + 2] = v;
    out[j + 3] = 255;
  }
  return out;
}

/** Black & white threshold enhancement */
function enhanceBW(srcData, w, h) {
  const gray = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) {
    const j = i * 4;
    gray[i] = 0.299 * srcData[j] + 0.587 * srcData[j + 1] + 0.114 * srcData[j + 2];
  }
  const bg = boxBlur(gray, w, h, Math.max(10, Math.round(Math.min(w, h) / 25)));
  const out = new Uint8ClampedArray(w * h * 4);
  for (let i = 0; i < w * h; i++) {
    const threshold = bg[i] - 10;
    const v = gray[i] < threshold ? 0 : 255;
    const j = i * 4;
    out[j] = out[j + 1] = out[j + 2] = v;
    out[j + 3] = 255;
  }
  return out;
}

/** Fast box blur (integral image approach) */
function boxBlur(gray, w, h, radius) {
  // Build integral image
  const integral = new Float64Array((w + 1) * (h + 1));
  for (let y = 0; y < h; y++) {
    let rowSum = 0;
    for (let x = 0; x < w; x++) {
      rowSum += gray[y * w + x];
      integral[(y + 1) * (w + 1) + (x + 1)] = rowSum + integral[y * (w + 1) + (x + 1)];
    }
  }

  const out = new Float32Array(w * h);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const x1 = Math.max(0, x - radius), y1 = Math.max(0, y - radius);
      const x2 = Math.min(w - 1, x + radius), y2 = Math.min(h - 1, y + radius);
      const area = (x2 - x1 + 1) * (y2 - y1 + 1);
      const sum = integral[(y2 + 1) * (w + 1) + (x2 + 1)]
                - integral[y1 * (w + 1) + (x2 + 1)]
                - integral[(y2 + 1) * (w + 1) + x1]
                + integral[y1 * (w + 1) + x1];
      out[y * w + x] = sum / area;
    }
  }
  return out;
}

/* ════════════════════ MAIN PIPELINE ════════════════════ */

function processImage(buffer, width, height, filterMode) {
  const srcData = new Uint8ClampedArray(buffer);
  const gray = toGray(srcData, width, height);
  const imgArea = width * height;

  // Detect document edges
  let corners = null;
  let autoDetected = false;

  // Try multiple thresholds
  for (const [lo, hi] of [[30, 90], [50, 150], [70, 200]]) {
    const edges = cannyEdges(gray, width, height, lo, hi);
    const dilated = dilate(edges, width, height);
    corners = detectDocument(dilated, width, height, imgArea);
    if (corners) { autoDetected = true; break; }
  }

  let resultData, resultW, resultH;

  if (corners) {
    // Perspective correction
    const warped = perspectiveWarp(srcData, width, height, corners);
    resultW = warped.width;
    resultH = warped.height;
    // Apply filter
    if (filterMode === 'bw') resultData = enhanceBW(warped.data, resultW, resultH);
    else if (filterMode === 'original') resultData = warped.data;
    else resultData = enhanceDocument(warped.data, resultW, resultH);
  } else {
    resultW = width;
    resultH = height;
    if (filterMode === 'bw') resultData = enhanceBW(srcData, width, height);
    else if (filterMode === 'original') { resultData = new Uint8ClampedArray(srcData); }
    else resultData = enhanceDocument(srcData, width, height);
  }

  const outBuffer = resultData.buffer.slice(0);
  return {
    imageData: outBuffer,
    width: resultW,
    height: resultH,
    corners: corners,
    autoDetected: autoDetected,
    originalWidth: width,
    originalHeight: height,
  };
}

function reprocessWithCorners(buffer, width, height, corners, filterMode) {
  const srcData = new Uint8ClampedArray(buffer);
  const warped = perspectiveWarp(srcData, width, height, corners);
  let resultData;
  if (filterMode === 'bw') resultData = enhanceBW(warped.data, warped.width, warped.height);
  else if (filterMode === 'original') resultData = warped.data;
  else resultData = enhanceDocument(warped.data, warped.width, warped.height);

  return {
    imageData: resultData.buffer.slice(0),
    width: warped.width,
    height: warped.height,
  };
}

/* ════════════════════ BRIGHTNESS / CONTRAST ════════════════════ */

function adjustBrightnessContrast(buffer, width, height, brightness, contrast) {
  const src = new Uint8ClampedArray(buffer);
  const out = new Uint8ClampedArray(src.length);
  const factor = (259 * (contrast + 255)) / (255 * (259 - contrast));
  for (let i = 0; i < src.length; i += 4) {
    for (let c = 0; c < 3; c++) {
      out[i + c] = Math.min(255, Math.max(0, factor * (src[i + c] - 128) + 128 + brightness));
    }
    out[i + 3] = src[i + 3];
  }
  return { imageData: out.buffer.slice(0), width, height };
}

/* ════════════════════ ROTATION ════════════════════ */

function rotateImage(buffer, width, height, degrees) {
  const src = new Uint8ClampedArray(buffer);
  const angle = ((degrees % 360) + 360) % 360;
  if (angle === 0) return { imageData: src.buffer.slice(0), width, height };

  let outW, outH;
  if (angle === 90 || angle === 270) { outW = height; outH = width; }
  else { outW = width; outH = height; } // 180

  const out = new Uint8ClampedArray(outW * outH * 4);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const si = (y * width + x) * 4;
      let dx, dy;
      if (angle === 90) { dx = height - 1 - y; dy = x; }
      else if (angle === 180) { dx = width - 1 - x; dy = height - 1 - y; }
      else { dx = y; dy = width - 1 - x; } // 270
      const di = (dy * outW + dx) * 4;
      out[di] = src[si]; out[di + 1] = src[si + 1]; out[di + 2] = src[si + 2]; out[di + 3] = src[si + 3];
    }
  }
  return { imageData: out.buffer.slice(0), width: outW, height: outH };
}

/* ════════════════════ MESSAGE HANDLER ════════════════════ */

self.onmessage = (e) => {
  const { type, id } = e.data;
  const t0 = performance.now();
  try {
    if (type === 'init') {
      console.log('[Worker] Init request — Pure JS ready');
      self.postMessage({ id, type: 'init', success: true });
      return;
    }

    if (type === 'process') {
      const { imageData, width, height, filter } = e.data;
      console.log('[Worker] Process', width, 'x', height, 'filter:', filter || 'document');
      const result = processImage(imageData, width, height, filter || 'document');
      console.log('[Worker] Process done in', Math.round(performance.now() - t0), 'ms — detected:', result.autoDetected);
      self.postMessage({ id, type: 'result', ...result }, [result.imageData]);

    } else if (type === 'reprocess') {
      const { imageData, width, height, corners, filter } = e.data;
      console.log('[Worker] Reprocess with corners, filter:', filter || 'document');
      const result = reprocessWithCorners(imageData, width, height, corners, filter || 'document');
      console.log('[Worker] Reprocess done in', Math.round(performance.now() - t0), 'ms');
      self.postMessage({ id, type: 'result', ...result }, [result.imageData]);

    } else if (type === 'adjust') {
      const { imageData, width, height, brightness, contrast } = e.data;
      console.log('[Worker] Adjust brightness:', brightness, 'contrast:', contrast);
      const result = adjustBrightnessContrast(imageData, width, height, brightness || 0, contrast || 0);
      console.log('[Worker] Adjust done in', Math.round(performance.now() - t0), 'ms');
      self.postMessage({ id, type: 'result', ...result }, [result.imageData]);

    } else if (type === 'rotate') {
      const { imageData, width, height, degrees } = e.data;
      console.log('[Worker] Rotate', degrees, 'degrees');
      const result = rotateImage(imageData, width, height, degrees || 90);
      console.log('[Worker] Rotate done in', Math.round(performance.now() - t0), 'ms');
      self.postMessage({ id, type: 'result', ...result }, [result.imageData]);

    } else {
      self.postMessage({ id, type: 'error', error: 'Unknown type: ' + type });
    }
  } catch (err) {
    console.error('[Worker] Error:', err.message);
    self.postMessage({ id, type: 'error', error: err.message });
  }
};

console.log('[Worker] Pure-JS scanner worker ready');
