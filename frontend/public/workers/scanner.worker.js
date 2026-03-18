/**
 * scanner.worker.js — Stateful Worker avec OffscreenCanvas
 * Actions : scan, filter, rotate, save
 * Auto-crop : detection des bords du document via Sobel + projection
 */

let currentCanvas = null;
let currentCtx = null;
let originalImage = null;

self.onmessage = async function (e) {
  const msg = e.data;

  if (msg.type === 'scan') {
    const bitmap = await createImageBitmap(msg.blob);
    currentCanvas = new OffscreenCanvas(bitmap.width, bitmap.height);
    currentCtx = currentCanvas.getContext('2d');
    currentCtx.drawImage(bitmap, 0, 0);
    bitmap.close();

    // Auto-crop si la source est la camera
    if (msg.autoCrop) {
      const cropped = autoCrop(currentCanvas);
      if (cropped) {
        currentCanvas = cropped.canvas;
        currentCtx = cropped.ctx;
      }
    }

    originalImage = currentCtx.getImageData(0, 0, currentCanvas.width, currentCanvas.height);
    await sendPreview();
    return;
  }

  if (msg.type === 'filter' && currentCanvas && originalImage) {
    let data = new ImageData(
      new Uint8ClampedArray(originalImage.data),
      originalImage.width,
      originalImage.height
    );
    if (msg.filter === 'bw') data = binarize(data);
    else if (msg.filter === 'enhanced') data = adjustContrast(data, 50);
    currentCanvas.width = data.width;
    currentCanvas.height = data.height;
    currentCtx = currentCanvas.getContext('2d');
    currentCtx.putImageData(data, 0, 0);
    await sendPreview();
    return;
  }

  if (msg.type === 'rotate' && currentCanvas) {
    const rotated = rotateCanvas(currentCanvas, msg.direction === 'left' ? -90 : 90);
    currentCanvas = rotated.canvas;
    currentCtx = rotated.ctx;
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

// === AUTO-CROP : detection du document via Sobel edge detection ===

function autoCrop(canvas) {
  const w = canvas.width;
  const h = canvas.height;

  // Travailler sur une version reduite pour la vitesse
  const maxDim = 400;
  const scale = Math.min(1, maxDim / Math.max(w, h));
  const sw = Math.round(w * scale);
  const sh = Math.round(h * scale);

  const small = new OffscreenCanvas(sw, sh);
  const sCtx = small.getContext('2d');
  sCtx.drawImage(canvas, 0, 0, sw, sh);
  const sData = sCtx.getImageData(0, 0, sw, sh);
  const pixels = sData.data;

  // Grayscale
  const gray = new Float32Array(sw * sh);
  for (let i = 0; i < sw * sh; i++) {
    gray[i] = 0.299 * pixels[i * 4] + 0.587 * pixels[i * 4 + 1] + 0.114 * pixels[i * 4 + 2];
  }

  // Sobel edge detection
  const edges = new Float32Array(sw * sh);
  for (let y = 1; y < sh - 1; y++) {
    for (let x = 1; x < sw - 1; x++) {
      const idx = y * sw + x;
      const gx =
        -gray[(y - 1) * sw + x - 1] - 2 * gray[idx - 1] - gray[(y + 1) * sw + x - 1]
        + gray[(y - 1) * sw + x + 1] + 2 * gray[idx + 1] + gray[(y + 1) * sw + x + 1];
      const gy =
        -gray[(y - 1) * sw + x - 1] - 2 * gray[(y - 1) * sw + x] - gray[(y - 1) * sw + x + 1]
        + gray[(y + 1) * sw + x - 1] + 2 * gray[(y + 1) * sw + x] + gray[(y + 1) * sw + x + 1];
      edges[idx] = Math.sqrt(gx * gx + gy * gy);
    }
  }

  // Projection des bords sur les axes X et Y
  const colSum = new Float32Array(sw);
  const rowSum = new Float32Array(sh);
  for (let y = 0; y < sh; y++) {
    for (let x = 0; x < sw; x++) {
      const e = edges[y * sw + x];
      colSum[x] += e;
      rowSum[y] += e;
    }
  }

  // Seuil : moyenne des projections
  let colTotal = 0, rowTotal = 0;
  for (let x = 0; x < sw; x++) colTotal += colSum[x];
  for (let y = 0; y < sh; y++) rowTotal += rowSum[y];
  const colThresh = (colTotal / sw) * 0.4;
  const rowThresh = (rowTotal / sh) * 0.4;

  // Trouver les limites du document
  let left = 0, right = sw - 1, top = 0, bottom = sh - 1;
  for (let x = 0; x < sw; x++) { if (colSum[x] > colThresh) { left = x; break; } }
  for (let x = sw - 1; x >= 0; x--) { if (colSum[x] > colThresh) { right = x; break; } }
  for (let y = 0; y < sh; y++) { if (rowSum[y] > rowThresh) { top = y; break; } }
  for (let y = sh - 1; y >= 0; y--) { if (rowSum[y] > rowThresh) { bottom = y; break; } }

  // Remettre aux dimensions originales
  left = Math.round(left / scale);
  right = Math.round(right / scale);
  top = Math.round(top / scale);
  bottom = Math.round(bottom / scale);

  // Padding leger (0.5%)
  const pad = Math.round(Math.max(w, h) * 0.005);
  left = Math.max(0, left - pad);
  top = Math.max(0, top - pad);
  right = Math.min(w - 1, right + pad);
  bottom = Math.min(h - 1, bottom + pad);

  const cropW = right - left + 1;
  const cropH = bottom - top + 1;

  // Securite : ne pas recadrer si le resultat est trop petit (<30%) ou quasi identique (>95%)
  if (cropW < w * 0.3 || cropH < h * 0.3) return null;
  if (cropW > w * 0.95 && cropH > h * 0.95) return null;

  // Creer le canvas recadre
  const cropped = new OffscreenCanvas(cropW, cropH);
  const cropCtx = cropped.getContext('2d');
  cropCtx.drawImage(canvas, left, top, cropW, cropH, 0, 0, cropW, cropH);

  return { canvas: cropped, ctx: cropCtx };
}

// === FONCTIONS EXISTANTES ===

async function sendPreview() {
  const blob = await currentCanvas.convertToBlob({ type: 'image/jpeg', quality: 0.9 });
  const buffer = await blob.arrayBuffer();
  self.postMessage(
    { type: 'preview', data: buffer, width: currentCanvas.width, height: currentCanvas.height },
    [buffer]
  );
}

function binarize(imageData, threshold) {
  if (threshold === undefined) threshold = 128;
  const d = imageData.data;
  for (let i = 0; i < d.length; i += 4) {
    const g = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
    const val = g > threshold ? 255 : 0;
    d[i] = d[i + 1] = d[i + 2] = val;
  }
  return imageData;
}

function adjustContrast(imageData, contrast) {
  const factor = (259 * (contrast + 255)) / (255 * (259 - contrast));
  const d = imageData.data;
  for (let i = 0; i < d.length; i += 4) {
    d[i] = Math.min(255, Math.max(0, factor * (d[i] - 128) + 128));
    d[i + 1] = Math.min(255, Math.max(0, factor * (d[i + 1] - 128) + 128));
    d[i + 2] = Math.min(255, Math.max(0, factor * (d[i + 2] - 128) + 128));
  }
  return imageData;
}

function rotateCanvas(canvas, angle) {
  const rad = (angle * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  const newW = Math.round(Math.abs(canvas.width * cos) + Math.abs(canvas.height * sin));
  const newH = Math.round(Math.abs(canvas.width * sin) + Math.abs(canvas.height * cos));
  const rotated = new OffscreenCanvas(newW, newH);
  const ctx = rotated.getContext('2d');
  ctx.translate(newW / 2, newH / 2);
  ctx.rotate(rad);
  ctx.drawImage(canvas, -canvas.width / 2, -canvas.height / 2);
  return { canvas: rotated, ctx };
}

self.postMessage({ type: 'ready' });
