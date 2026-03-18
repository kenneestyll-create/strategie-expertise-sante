/**
 * scanner.worker.js — Stateful Worker avec OffscreenCanvas
 * Actions : scan, filter, rotate, save
 * Auto-crop : detection du document par contraste fond/contenu
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
      try {
        const cropped = autoCrop(currentCanvas, currentCtx);
        if (cropped) {
          currentCanvas = cropped.canvas;
          currentCtx = cropped.ctx;
        }
      } catch (err) {
        // Si l'auto-crop echoue, on garde l'original
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

// === AUTO-CROP : detection du document par contraste fond/contenu ===

function autoCrop(canvas, ctx) {
  const w = canvas.width;
  const h = canvas.height;
  const imageData = ctx.getImageData(0, 0, w, h);
  const data = imageData.data;

  // Helper: grayscale a (x, y)
  function grayAt(x, y) {
    const i = (y * w + x) * 4;
    return 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
  }

  // Etape 1: echantillonner le fond depuis les bords exterieurs (3%)
  const borderSize = Math.max(8, Math.round(Math.min(w, h) * 0.03));
  const sampleGap = 3;
  let bgSum = 0, bgCount = 0;

  for (let y = 0; y < borderSize; y += sampleGap) {
    for (let x = 0; x < w; x += sampleGap) { bgSum += grayAt(x, y); bgCount++; }
  }
  for (let y = h - borderSize; y < h; y += sampleGap) {
    for (let x = 0; x < w; x += sampleGap) { bgSum += grayAt(x, y); bgCount++; }
  }
  for (let y = borderSize; y < h - borderSize; y += sampleGap) {
    for (let x = 0; x < borderSize; x += sampleGap) { bgSum += grayAt(x, y); bgCount++; }
    for (let x = w - borderSize; x < w; x += sampleGap) { bgSum += grayAt(x, y); bgCount++; }
  }

  if (bgCount === 0) return null;
  const bgAvg = bgSum / bgCount;

  // Etape 2: compter pixels "contenu" par ligne et colonne
  // Un pixel est "contenu" si sa luminosite differe du fond de plus de 30
  const contrastThreshold = 30;
  const scanStep = Math.max(1, Math.round(Math.min(w, h) / 300));

  const rowContent = new Float32Array(h);
  const colContent = new Float32Array(w);

  for (let y = 0; y < h; y += scanStep) {
    let cnt = 0;
    for (let x = 0; x < w; x += scanStep) {
      if (Math.abs(grayAt(x, y) - bgAvg) > contrastThreshold) cnt++;
    }
    rowContent[y] = cnt;
  }

  for (let x = 0; x < w; x += scanStep) {
    let cnt = 0;
    for (let y = 0; y < h; y += scanStep) {
      if (Math.abs(grayAt(x, y) - bgAvg) > contrastThreshold) cnt++;
    }
    colContent[x] = cnt;
  }

  // Etape 3: trouver les limites (15% des pixels d'une ligne/colonne = contenu)
  const samplesPerRow = Math.ceil(w / scanStep);
  const samplesPerCol = Math.ceil(h / scanStep);
  const rowThresh = samplesPerRow * 0.15;
  const colThresh = samplesPerCol * 0.15;

  let top = 0, bottom = h - 1, left = 0, right = w - 1;

  // Scan a step=1 sur le tableau pre-calcule (O(n) lectures, pas de recalcul)
  for (let y = 0; y < h; y++) { if (rowContent[y] >= rowThresh) { top = y; break; } }
  for (let y = h - 1; y >= 0; y--) { if (rowContent[y] >= rowThresh) { bottom = y; break; } }
  for (let x = 0; x < w; x++) { if (colContent[x] >= colThresh) { left = x; break; } }
  for (let x = w - 1; x >= 0; x--) { if (colContent[x] >= colThresh) { right = x; break; } }

  // Padding leger (0.5%)
  const pad = Math.round(Math.max(w, h) * 0.005);
  left = Math.max(0, left - pad);
  top = Math.max(0, top - pad);
  right = Math.min(w - 1, right + pad);
  bottom = Math.min(h - 1, bottom + pad);

  const cropW = right - left + 1;
  const cropH = bottom - top + 1;

  // Securite: ne pas recadrer si resultat trop petit (<30%) ou quasi identique (>95%)
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
