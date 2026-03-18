/**
 * Scanner Worker — OffscreenCanvas + Stateful
 * Architecture definitive: toutes les operations graphiques dans le Worker.
 * Le main thread ne fait JAMAIS de traitement d'image.
 */

let currentCanvas = null;
let currentCtx = null;
let originalImageData = null;

self.onmessage = async (e) => {
  const msg = e.data;

  if (msg.type === 'scan') {
    try {
      const bitmap = await createImageBitmap(msg.imageBlob);
      currentCanvas = new OffscreenCanvas(bitmap.width, bitmap.height);
      currentCtx = currentCanvas.getContext('2d');
      currentCtx.drawImage(bitmap, 0, 0);
      bitmap.close();

      // Stocker l'image originale pour les filtres
      originalImageData = currentCtx.getImageData(0, 0, currentCanvas.width, currentCanvas.height);

      await sendPreview('original');
    } catch (err) {
      self.postMessage({ type: 'error', error: err.message });
    }
    return;
  }

  if (msg.type === 'filter' && currentCanvas) {
    await applyFilter(msg.filter);
    return;
  }

  if (msg.type === 'rotate' && currentCanvas) {
    await rotateCanvas(msg.direction);
    return;
  }

  if (msg.type === 'save' && currentCanvas) {
    try {
      const blob = await currentCanvas.convertToBlob({ type: 'image/jpeg', quality: 0.95 });
      const buffer = await blob.arrayBuffer();
      self.postMessage({ type: 'saved', data: buffer }, [buffer]);
    } catch (err) {
      self.postMessage({ type: 'error', error: err.message });
    }
    return;
  }
};

// === Fonctions internes ===

async function applyFilter(filter) {
  if (!originalImageData) return;

  let imageData;
  if (filter === 'original') {
    imageData = new ImageData(
      new Uint8ClampedArray(originalImageData.data),
      originalImageData.width,
      originalImageData.height
    );
  } else {
    imageData = new ImageData(
      new Uint8ClampedArray(originalImageData.data),
      originalImageData.width,
      originalImageData.height
    );
    if (filter === 'bw') binarize(imageData);
    if (filter === 'enhanced') adjustContrast(imageData, 50);
  }

  currentCanvas.width = imageData.width;
  currentCanvas.height = imageData.height;
  currentCtx = currentCanvas.getContext('2d');
  currentCtx.putImageData(imageData, 0, 0);
  await sendPreview(filter);
}

async function sendPreview() {
  try {
    const blob = await currentCanvas.convertToBlob({ type: 'image/jpeg', quality: 0.9 });
    const buffer = await blob.arrayBuffer();
    self.postMessage({ type: 'preview', data: buffer }, [buffer]);
  } catch (err) {
    self.postMessage({ type: 'error', error: err.message });
  }
}

function binarize(imageData, threshold = 128) {
  const data = imageData.data;
  for (let i = 0; i < data.length; i += 4) {
    const gray = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
    const val = gray > threshold ? 255 : 0;
    data[i] = data[i + 1] = data[i + 2] = val;
  }
}

function adjustContrast(imageData, contrast) {
  const factor = (259 * (contrast + 255)) / (255 * (259 - contrast));
  const data = imageData.data;
  for (let i = 0; i < data.length; i += 4) {
    data[i] = Math.min(255, Math.max(0, factor * (data[i] - 128) + 128));
    data[i + 1] = Math.min(255, Math.max(0, factor * (data[i + 1] - 128) + 128));
    data[i + 2] = Math.min(255, Math.max(0, factor * (data[i + 2] - 128) + 128));
  }
}

async function rotateCanvas(direction) {
  const angle = direction === 'left' ? -90 : 90;
  const rad = angle * Math.PI / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);

  const newWidth = Math.round(Math.abs(currentCanvas.width * cos) + Math.abs(currentCanvas.height * sin));
  const newHeight = Math.round(Math.abs(currentCanvas.width * sin) + Math.abs(currentCanvas.height * cos));

  const rotated = new OffscreenCanvas(newWidth, newHeight);
  const ctx = rotated.getContext('2d');
  ctx.translate(newWidth / 2, newHeight / 2);
  ctx.rotate(rad);
  ctx.drawImage(currentCanvas, -currentCanvas.width / 2, -currentCanvas.height / 2);

  currentCanvas = rotated;
  currentCtx = ctx;

  // Mettre a jour originalImageData apres rotation
  originalImageData = currentCtx.getImageData(0, 0, currentCanvas.width, currentCanvas.height);

  await sendPreview();
}

console.log('[ScannerWorker] OffscreenCanvas worker ready');
