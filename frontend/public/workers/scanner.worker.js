/**
 * scanner.worker.js — Stateful Worker avec OffscreenCanvas
 * Actions : scan, filter, rotate, save
 * Aucun appel bloquant dans le thread principal
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
    const gray = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
    const val = gray > threshold ? 255 : 0;
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
