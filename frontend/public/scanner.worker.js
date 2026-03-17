/**
 * Pure-JS Document Scanner Worker — STATEFUL
 * Keeps currentImage in worker memory. Operations chain without re-transfer.
 * Pattern: scan → filter/rotate/crop/adjust → save
 */

/* ════════════════════ STATE ════════════════════ */
self.originalImage = null;   // Raw capture RGBA buffer
self.originalW = 0;
self.originalH = 0;
self.baseImage = null;       // After scan/crop (warped or cropped)
self.baseW = 0;
self.baseH = 0;
self.currentImage = null;    // After filter/adjust (what user sees)
self.currentW = 0;
self.currentH = 0;
self.detectedCorners = null;
self.currentFilter = 'document';

/* ════════════════════ IMAGE PROCESSING PRIMITIVES ════════════════════ */

function toGray(data, w, h) {
  const out = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) {
    const j = i * 4;
    out[i] = 0.299 * data[j] + 0.587 * data[j + 1] + 0.114 * data[j + 2];
  }
  return out;
}

function gaussianBlur(gray, w, h) {
  const k = [0.06136, 0.24477, 0.38774, 0.24477, 0.06136];
  const tmp = new Float32Array(w * h);
  const out = new Float32Array(w * h);
  for (let y = 0; y < h; y++)
    for (let x = 0; x < w; x++) {
      let s = 0;
      for (let ki = -2; ki <= 2; ki++) s += gray[y * w + Math.min(w - 1, Math.max(0, x + ki))] * k[ki + 2];
      tmp[y * w + x] = s;
    }
  for (let y = 0; y < h; y++)
    for (let x = 0; x < w; x++) {
      let s = 0;
      for (let ki = -2; ki <= 2; ki++) s += tmp[Math.min(h - 1, Math.max(0, y + ki)) * w + x] * k[ki + 2];
      out[y * w + x] = s;
    }
  return out;
}

function sobel(gray, w, h) {
  const mag = new Float32Array(w * h);
  const dir = new Float32Array(w * h);
  for (let y = 1; y < h - 1; y++)
    for (let x = 1; x < w - 1; x++) {
      const i = y * w + x;
      const gx = -gray[(y-1)*w+(x-1)] + gray[(y-1)*w+(x+1)] - 2*gray[y*w+(x-1)] + 2*gray[y*w+(x+1)] - gray[(y+1)*w+(x-1)] + gray[(y+1)*w+(x+1)];
      const gy = -gray[(y-1)*w+(x-1)] - 2*gray[(y-1)*w+x] - gray[(y-1)*w+(x+1)] + gray[(y+1)*w+(x-1)] + 2*gray[(y+1)*w+x] + gray[(y+1)*w+(x+1)];
      mag[i] = Math.sqrt(gx * gx + gy * gy);
      dir[i] = Math.atan2(gy, gx);
    }
  return { mag, dir };
}

function cannyEdges(gray, w, h, lo, hi) {
  const blurred = gaussianBlur(gray, w, h);
  const { mag, dir } = sobel(blurred, w, h);
  const nms = new Float32Array(w * h);
  for (let y = 1; y < h - 1; y++)
    for (let x = 1; x < w - 1; x++) {
      const i = y * w + x;
      const angle = ((dir[i] * 180 / Math.PI) + 180) % 180;
      let n1 = 0, n2 = 0;
      if (angle < 22.5 || angle >= 157.5) { n1 = mag[i-1]; n2 = mag[i+1]; }
      else if (angle < 67.5) { n1 = mag[(y-1)*w+(x+1)]; n2 = mag[(y+1)*w+(x-1)]; }
      else if (angle < 112.5) { n1 = mag[(y-1)*w+x]; n2 = mag[(y+1)*w+x]; }
      else { n1 = mag[(y-1)*w+(x-1)]; n2 = mag[(y+1)*w+(x+1)]; }
      nms[i] = (mag[i] >= n1 && mag[i] >= n2) ? mag[i] : 0;
    }
  const edges = new Uint8Array(w * h);
  for (let i = 0; i < w * h; i++) {
    if (nms[i] >= hi) edges[i] = 255;
    else if (nms[i] >= lo) edges[i] = 128;
  }
  let changed = true;
  while (changed) {
    changed = false;
    for (let y = 1; y < h - 1; y++)
      for (let x = 1; x < w - 1; x++) {
        const i = y * w + x;
        if (edges[i] !== 128) continue;
        for (let dy = -1; dy <= 1; dy++)
          for (let dx = -1; dx <= 1; dx++)
            if (edges[(y+dy)*w+(x+dx)] === 255) { edges[i] = 255; changed = true; }
      }
  }
  for (let i = 0; i < w * h; i++) if (edges[i] !== 255) edges[i] = 0;
  return edges;
}

function dilate3x3(edges, w, h) {
  const out = new Uint8Array(w * h);
  for (let y = 1; y < h - 1; y++)
    for (let x = 1; x < w - 1; x++) {
      let v = 0;
      for (let dy = -1; dy <= 1; dy++)
        for (let dx = -1; dx <= 1; dx++)
          if (edges[(y+dy)*w+(x+dx)]) { v = 255; break; }
      out[y * w + x] = v;
    }
  return out;
}

/* ════════════════════ CONTOUR DETECTION ════════════════════ */

function findContours(edges, w, h) {
  const visited = new Uint8Array(w * h);
  const contours = [];
  for (let y = 0; y < h; y++)
    for (let x = 0; x < w; x++) {
      if (!edges[y * w + x] || visited[y * w + x]) continue;
      const points = [];
      const queue = [{ x, y }];
      visited[y * w + x] = 1;
      while (queue.length) {
        const p = queue.shift();
        points.push(p);
        for (const [dx, dy] of [[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[1,-1],[-1,1],[1,1]]) {
          const nx = p.x + dx, ny = p.y + dy;
          if (nx >= 0 && nx < w && ny >= 0 && ny < h && !visited[ny * w + nx] && edges[ny * w + nx]) {
            visited[ny * w + nx] = 1;
            queue.push({ x: nx, y: ny });
          }
        }
      }
      if (points.length > 50) contours.push(points);
    }
  return contours;
}

function convexHull(points) {
  if (points.length <= 3) return [...points];
  const sorted = [...points].sort((a, b) => a.x - b.x || a.y - b.y);
  const cross = (O, A, B) => (A.x - O.x) * (B.y - O.y) - (A.y - O.y) * (B.x - O.x);
  const lower = [];
  for (const p of sorted) { while (lower.length >= 2 && cross(lower[lower.length-2], lower[lower.length-1], p) <= 0) lower.pop(); lower.push(p); }
  const upper = [];
  for (let i = sorted.length - 1; i >= 0; i--) { const p = sorted[i]; while (upper.length >= 2 && cross(upper[upper.length-2], upper[upper.length-1], p) <= 0) upper.pop(); upper.push(p); }
  return lower.slice(0, -1).concat(upper.slice(0, -1));
}

function rdp(points, epsilon) {
  if (points.length <= 2) return points;
  let maxDist = 0, maxIdx = 0;
  const first = points[0], last = points[points.length - 1];
  for (let i = 1; i < points.length - 1; i++) {
    const num = Math.abs((last.y - first.y) * points[i].x - (last.x - first.x) * points[i].y + last.x * first.y - last.y * first.x);
    const den = Math.sqrt((last.y - first.y) ** 2 + (last.x - first.x) ** 2) || 1;
    const d = num / den;
    if (d > maxDist) { maxDist = d; maxIdx = i; }
  }
  if (maxDist > epsilon) {
    const left = rdp(points.slice(0, maxIdx + 1), epsilon);
    const right = rdp(points.slice(maxIdx), epsilon);
    return left.slice(0, -1).concat(right);
  }
  return [first, last];
}

function approxPoly(points, epsilon) {
  return rdp(convexHull(points), epsilon);
}

function polygonArea(pts) {
  let a = 0;
  for (let i = 0; i < pts.length; i++) { const j = (i + 1) % pts.length; a += pts[i].x * pts[j].y - pts[j].x * pts[i].y; }
  return Math.abs(a) / 2;
}

function polyPerimeter(pts) {
  let p = 0;
  for (let i = 0; i < pts.length; i++) { const j = (i + 1) % pts.length; p += Math.sqrt((pts[j].x - pts[i].x) ** 2 + (pts[j].y - pts[i].y) ** 2); }
  return p;
}

function orderCorners(pts) {
  const s = [...pts];
  s.sort((a, b) => (a.x + a.y) - (b.x + b.y));
  const tl = s[0], br = s[3];
  s.sort((a, b) => (a.y - a.x) - (b.y - b.x));
  return [tl, s[0], br, s[3]];
}

function detectDocument(edges, w, h, imgArea) {
  const contours = findContours(edges, w, h);
  let bestCorners = null, bestArea = 0;
  for (const contour of contours) {
    const hull = convexHull(contour);
    const area = polygonArea(hull);
    if (area < imgArea * 0.08) continue;
    const perim = polyPerimeter(hull);
    const approx = approxPoly(contour, 0.02 * perim);
    if (approx.length === 4 && area > bestArea) {
      bestCorners = orderCorners(approx);
      bestArea = area;
    }
  }
  return bestCorners;
}

/* ════════════════════ PERSPECTIVE TRANSFORM ════════════════════ */

function dist(a, b) { return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2); }

function perspectiveWarp(srcData, srcW, srcH, corners) {
  const [tl, tr, br, bl] = corners;
  const outW = Math.round(Math.max(dist(tl, tr), dist(bl, br)));
  const outH = Math.round(Math.max(dist(tl, bl), dist(tr, br)));
  const M = computePerspectiveMatrix(
    [tl.x, tl.y, tr.x, tr.y, br.x, br.y, bl.x, bl.y],
    [0, 0, outW, 0, outW, outH, 0, outH]
  );
  const Mi = invert3x3(M);
  if (!Mi) return { data: srcData, width: srcW, height: srcH };

  const out = new Uint8ClampedArray(outW * outH * 4);
  for (let y = 0; y < outH; y++)
    for (let x = 0; x < outW; x++) {
      const denom = Mi[6] * x + Mi[7] * y + Mi[8];
      const sx = (Mi[0] * x + Mi[1] * y + Mi[2]) / denom;
      const sy = (Mi[3] * x + Mi[4] * y + Mi[5]) / denom;
      const ix = Math.floor(sx), iy = Math.floor(sy);
      if (ix < 0 || ix >= srcW - 1 || iy < 0 || iy >= srcH - 1) continue;
      const fx = sx - ix, fy = sy - iy;
      const di = (y * outW + x) * 4;
      for (let c = 0; c < 4; c++) {
        out[di + c] = Math.round(
          srcData[(iy * srcW + ix) * 4 + c] * (1 - fx) * (1 - fy) +
          srcData[(iy * srcW + ix + 1) * 4 + c] * fx * (1 - fy) +
          srcData[((iy + 1) * srcW + ix) * 4 + c] * (1 - fx) * fy +
          srcData[((iy + 1) * srcW + ix + 1) * 4 + c] * fx * fy
        );
      }
    }
  return { data: out, width: outW, height: outH };
}

function computePerspectiveMatrix(src, dst) {
  const A = [], b = [];
  for (let i = 0; i < 4; i++) {
    const sx = src[i*2], sy = src[i*2+1], dx = dst[i*2], dy = dst[i*2+1];
    A.push([sx, sy, 1, 0, 0, 0, -dx*sx, -dx*sy]); b.push(dx);
    A.push([0, 0, 0, sx, sy, 1, -dy*sx, -dy*sy]); b.push(dy);
  }
  const h = solveLinear8(A, b);
  return [h[0], h[1], h[2], h[3], h[4], h[5], h[6], h[7], 1];
}

function solveLinear8(A, b) {
  const n = 8;
  const aug = A.map((row, i) => [...row, b[i]]);
  for (let col = 0; col < n; col++) {
    let maxRow = col;
    for (let row = col + 1; row < n; row++) if (Math.abs(aug[row][col]) > Math.abs(aug[maxRow][col])) maxRow = row;
    [aug[col], aug[maxRow]] = [aug[maxRow], aug[col]];
    if (Math.abs(aug[col][col]) < 1e-10) return [1, 0, 0, 0, 1, 0, 0, 0];
    for (let row = col + 1; row < n; row++) { const f = aug[row][col] / aug[col][col]; for (let j = col; j <= n; j++) aug[row][j] -= f * aug[col][j]; }
  }
  const x = new Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) { x[i] = aug[i][n]; for (let j = i + 1; j < n; j++) x[i] -= aug[i][j] * x[j]; x[i] /= aug[i][i]; }
  return x;
}

function invert3x3(m) {
  const [a,b,c,d,e,f,g,h,i] = m;
  const det = a*(e*i-f*h) - b*(d*i-f*g) + c*(d*h-e*g);
  if (Math.abs(det) < 1e-10) return null;
  const inv = 1 / det;
  return [(e*i-f*h)*inv,(c*h-b*i)*inv,(b*f-c*e)*inv,(f*g-d*i)*inv,(a*i-c*g)*inv,(c*d-a*f)*inv,(d*h-e*g)*inv,(b*g-a*h)*inv,(a*e-b*d)*inv];
}

/* ════════════════════ ENHANCEMENT FILTERS ════════════════════ */

function boxBlur(gray, w, h, radius) {
  const integral = new Float64Array((w + 1) * (h + 1));
  for (let y = 0; y < h; y++) {
    let rowSum = 0;
    for (let x = 0; x < w; x++) { rowSum += gray[y * w + x]; integral[(y+1)*(w+1)+(x+1)] = rowSum + integral[y*(w+1)+(x+1)]; }
  }
  const out = new Float32Array(w * h);
  for (let y = 0; y < h; y++)
    for (let x = 0; x < w; x++) {
      const x1 = Math.max(0, x - radius), y1 = Math.max(0, y - radius);
      const x2 = Math.min(w - 1, x + radius), y2 = Math.min(h - 1, y + radius);
      const area = (x2 - x1 + 1) * (y2 - y1 + 1);
      out[y * w + x] = (integral[(y2+1)*(w+1)+(x2+1)] - integral[y1*(w+1)+(x2+1)] - integral[(y2+1)*(w+1)+x1] + integral[y1*(w+1)+x1]) / area;
    }
  return out;
}

function enhanceDocument(srcData, w, h) {
  const gray = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) { const j = i * 4; gray[i] = 0.299 * srcData[j] + 0.587 * srcData[j+1] + 0.114 * srcData[j+2]; }
  const bgRadius = Math.max(10, Math.round(Math.min(w, h) / 30));
  const bg = boxBlur(gray, w, h, bgRadius);
  const norm = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) norm[i] = bg[i] > 1 ? Math.min(255, (gray[i] / bg[i]) * 255) : gray[i];
  let min = 255, max = 0;
  for (let i = 0; i < w * h; i++) { if (norm[i] < min) min = norm[i]; if (norm[i] > max) max = norm[i]; }
  const range = Math.max(1, max - min);
  const blurred = boxBlur(norm, w, h, 2);
  const out = new Uint8ClampedArray(w * h * 4);
  for (let i = 0; i < w * h; i++) {
    const stretched = ((norm[i] - min) / range) * 255;
    const v = Math.round(Math.min(255, Math.max(0, stretched * 1.5 - blurred[i] * 0.5 + 10)));
    const j = i * 4; out[j] = out[j+1] = out[j+2] = v; out[j+3] = 255;
  }
  return out;
}

function enhanceBW(srcData, w, h) {
  const gray = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) { const j = i * 4; gray[i] = 0.299 * srcData[j] + 0.587 * srcData[j+1] + 0.114 * srcData[j+2]; }
  const bg = boxBlur(gray, w, h, Math.max(10, Math.round(Math.min(w, h) / 25)));
  const out = new Uint8ClampedArray(w * h * 4);
  for (let i = 0; i < w * h; i++) {
    const v = gray[i] < (bg[i] - 10) ? 0 : 255;
    const j = i * 4; out[j] = out[j+1] = out[j+2] = v; out[j+3] = 255;
  }
  return out;
}

/* ════════════════════ STATEFUL OPERATIONS ════════════════════ */

/** Apply current filter to base image → updates currentImage */
function applyCurrentFilter() {
  if (!self.baseImage) return;
  const src = new Uint8ClampedArray(self.baseImage);
  if (self.currentFilter === 'bw') {
    self.currentImage = enhanceBW(src, self.baseW, self.baseH).buffer;
  } else if (self.currentFilter === 'original') {
    self.currentImage = src.buffer.slice(0);
  } else {
    self.currentImage = enhanceDocument(src, self.baseW, self.baseH).buffer;
  }
  self.currentW = self.baseW;
  self.currentH = self.baseH;
}

/** Return a preview snapshot (copy of current state) */
function getPreview() {
  return {
    imageData: new Uint8ClampedArray(self.currentImage).buffer.slice(0),
    width: self.currentW,
    height: self.currentH,
    corners: self.detectedCorners,
    autoDetected: !!self.detectedCorners,
    originalWidth: self.originalW,
    originalHeight: self.originalH,
    filter: self.currentFilter,
  };
}

/* ═══ SCAN — initial capture, auto-detect, warp, filter ═══ */
function handleScan(buffer, width, height, filterMode) {
  console.log('[Worker] Scan', width, 'x', height, 'filter:', filterMode);
  const srcData = new Uint8ClampedArray(buffer);
  self.originalImage = srcData.buffer.slice(0);
  self.originalW = width;
  self.originalH = height;
  self.currentFilter = filterMode || 'document';
  self.detectedCorners = null;

  const gray = toGray(srcData, width, height);
  const imgArea = width * height;

  for (const [lo, hi] of [[30, 90], [50, 150], [70, 200]]) {
    const edges = cannyEdges(gray, width, height, lo, hi);
    const dilated = dilate3x3(edges, width, height);
    const corners = detectDocument(dilated, width, height, imgArea);
    if (corners) { self.detectedCorners = corners; break; }
  }

  if (self.detectedCorners) {
    const warped = perspectiveWarp(srcData, width, height, self.detectedCorners);
    self.baseImage = warped.data.buffer.slice(0);
    self.baseW = warped.width;
    self.baseH = warped.height;
  } else {
    self.baseImage = srcData.buffer.slice(0);
    self.baseW = width;
    self.baseH = height;
  }

  applyCurrentFilter();
  return getPreview();
}

/* ═══ FILTER — re-apply filter on base image ═══ */
function handleFilter(filterMode) {
  console.log('[Worker] Filter:', filterMode);
  self.currentFilter = filterMode || 'document';
  applyCurrentFilter();
  return getPreview();
}

/* ═══ ROTATE — rotate current image 90° left or right ═══ */
function handleRotate(direction) {
  const degrees = direction === 'left' ? 270 : 90;
  console.log('[Worker] Rotate', direction, '(' + degrees + '°)');

  // Rotate base image
  const baseResult = rotateBuffer(self.baseImage, self.baseW, self.baseH, degrees);
  self.baseImage = baseResult.buffer;
  self.baseW = baseResult.width;
  self.baseH = baseResult.height;

  // Rotate current image
  const curResult = rotateBuffer(self.currentImage, self.currentW, self.currentH, degrees);
  self.currentImage = curResult.buffer;
  self.currentW = curResult.width;
  self.currentH = curResult.height;

  // Rotate original too (for consistent reprocessing)
  const origResult = rotateBuffer(self.originalImage, self.originalW, self.originalH, degrees);
  self.originalImage = origResult.buffer;
  self.originalW = origResult.width;
  self.originalH = origResult.height;

  self.detectedCorners = null; // Invalidate corners after rotation
  return getPreview();
}

function rotateBuffer(buffer, width, height, degrees) {
  const src = new Uint8ClampedArray(buffer);
  const angle = ((degrees % 360) + 360) % 360;
  if (angle === 0) return { buffer: src.buffer.slice(0), width, height };
  let outW, outH;
  if (angle === 90 || angle === 270) { outW = height; outH = width; } else { outW = width; outH = height; }
  const out = new Uint8ClampedArray(outW * outH * 4);
  for (let y = 0; y < height; y++)
    for (let x = 0; x < width; x++) {
      const si = (y * width + x) * 4;
      let dx, dy;
      if (angle === 90) { dx = height - 1 - y; dy = x; }
      else if (angle === 180) { dx = width - 1 - x; dy = height - 1 - y; }
      else { dx = y; dy = width - 1 - x; }
      const di = (dy * outW + dx) * 4;
      out[di] = src[si]; out[di+1] = src[si+1]; out[di+2] = src[si+2]; out[di+3] = src[si+3];
    }
  return { buffer: out.buffer, width: outW, height: outH };
}

/* ═══ CROP — crop with rectangle or 4-point coords ═══ */
function handleCrop(coords) {
  if (!self.originalImage) return getPreview();

  const srcData = new Uint8ClampedArray(self.originalImage);
  console.log('[Worker] Crop', JSON.stringify(coords));

  if (coords.corners) {
    // 4-point perspective crop (manual corners)
    const warped = perspectiveWarp(srcData, self.originalW, self.originalH, coords.corners);
    self.baseImage = warped.data.buffer.slice(0);
    self.baseW = warped.width;
    self.baseH = warped.height;
  } else {
    // Rectangle crop {x0, y0, x1, y1} — normalized [0..1]
    const x0 = Math.round(coords.x0 * self.originalW);
    const y0 = Math.round(coords.y0 * self.originalH);
    const x1 = Math.round(coords.x1 * self.originalW);
    const y1 = Math.round(coords.y1 * self.originalH);
    const cw = Math.max(1, x1 - x0);
    const ch = Math.max(1, y1 - y0);
    const out = new Uint8ClampedArray(cw * ch * 4);
    for (let y = 0; y < ch; y++)
      for (let x = 0; x < cw; x++) {
        const si = ((y + y0) * self.originalW + (x + x0)) * 4;
        const di = (y * cw + x) * 4;
        out[di] = srcData[si]; out[di+1] = srcData[si+1]; out[di+2] = srcData[si+2]; out[di+3] = srcData[si+3];
      }
    self.baseImage = out.buffer;
    self.baseW = cw;
    self.baseH = ch;
  }

  applyCurrentFilter();
  return getPreview();
}

/* ═══ ADJUST — brightness/contrast on current image ═══ */
function handleAdjust(brightness, contrast) {
  console.log('[Worker] Adjust B:', brightness, 'C:', contrast);
  // Always adjust from base+filter, not from already-adjusted image
  applyCurrentFilter();
  if (brightness === 0 && contrast === 0) return getPreview();

  const src = new Uint8ClampedArray(self.currentImage);
  const out = new Uint8ClampedArray(src.length);
  const factor = (259 * (contrast + 255)) / (255 * (259 - contrast));
  for (let i = 0; i < src.length; i += 4) {
    for (let c = 0; c < 3; c++)
      out[i + c] = Math.min(255, Math.max(0, factor * (src[i + c] - 128) + 128 + brightness));
    out[i + 3] = src[i + 3];
  }
  self.currentImage = out.buffer;
  return getPreview();
}

/* ═══ SAVE — finalize and return the current image ═══ */
function handleSave() {
  console.log('[Worker] Save — finalizing');
  return {
    imageData: new Uint8ClampedArray(self.currentImage).buffer.slice(0),
    width: self.currentW,
    height: self.currentH,
    final: true,
  };
}

/* ════════════════════ MESSAGE HANDLER ════════════════════ */

self.onmessage = (e) => {
  const { type, id } = e.data;
  const t0 = performance.now();
  console.log('[Worker] RECV type=' + type + ' id=' + id);
  try {
    switch (type) {
      case 'init': {
        console.log('[Worker] INIT START');
        console.log('[Worker] INIT DONE');
        self.postMessage({ id, type: 'init', success: true });
        return;
      }
      case 'scan': {
        console.log('[Worker] SCAN START');
        const { imageData, width, height, filter } = e.data;
        const result = handleScan(imageData, width, height, filter);
        console.log('[Worker] SCAN DONE in', Math.round(performance.now() - t0), 'ms — detected:', result.autoDetected);
        self.postMessage({ id, type: 'preview', ...result }, [result.imageData]);
        return;
      }
      case 'filter': {
        console.log('[Worker] FILTER START:', e.data.filter);
        const result = handleFilter(e.data.filter);
        console.log('[Worker] FILTER DONE in', Math.round(performance.now() - t0), 'ms');
        self.postMessage({ id, type: 'preview', ...result }, [result.imageData]);
        return;
      }
      case 'rotate': {
        console.log('[Worker] ROTATE START:', e.data.direction);
        const result = handleRotate(e.data.direction || 'right');
        console.log('[Worker] ROTATE DONE in', Math.round(performance.now() - t0), 'ms');
        self.postMessage({ id, type: 'preview', ...result }, [result.imageData]);
        return;
      }
      case 'crop': {
        console.log('[Worker] CROP START');
        const result = handleCrop(e.data.coords);
        console.log('[Worker] CROP DONE in', Math.round(performance.now() - t0), 'ms');
        self.postMessage({ id, type: 'preview', ...result }, [result.imageData]);
        return;
      }
      case 'adjust': {
        console.log('[Worker] ADJUST START b=' + (e.data.brightness||0) + ' c=' + (e.data.contrast||0));
        const result = handleAdjust(e.data.brightness || 0, e.data.contrast || 0);
        console.log('[Worker] ADJUST DONE in', Math.round(performance.now() - t0), 'ms');
        self.postMessage({ id, type: 'preview', ...result }, [result.imageData]);
        return;
      }
      case 'save': {
        console.log('[Worker] SAVE START');
        const result = handleSave();
        console.log('[Worker] SAVE DONE in', Math.round(performance.now() - t0), 'ms');
        self.postMessage({ id, type: 'saved', ...result }, [result.imageData]);
        return;
      }
      default:
        console.error('[Worker] UNKNOWN type=' + type);
        self.postMessage({ id, type: 'error', error: 'Unknown: ' + type });
    }
  } catch (err) {
    console.error('[Worker] ERROR on type=' + type + ':', err.message, err.stack);
    self.postMessage({ id, type: 'error', error: err.message });
  }
};

console.log('[Worker] Pure-JS stateful scanner worker ready v5');
