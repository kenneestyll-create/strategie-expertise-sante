/**
 * Scanner Web Worker — OffscreenCanvas stateful
 * Receives: scan (blob), filter (bw/enhanced/original), rotate (left/right), save
 * Sends: ready, preview (JPEG ArrayBuffer), saved, error
 */

let canvas = null;
let ctx = null;
let originalData = null; // raw ImageData backup for filter switching
let currentWidth = 0;
let currentHeight = 0;

function sendPreview() {
  if (!canvas || !currentWidth || !currentHeight) return;
  canvas.convertToBlob({ type: 'image/jpeg', quality: 0.85 }).then(blob => {
    blob.arrayBuffer().then(buf => {
      self.postMessage({ type: 'preview', data: buf, width: currentWidth, height: currentHeight }, [buf]);
    });
  }).catch(err => {
    self.postMessage({ type: 'error', error: 'Preview generation failed: ' + err.message });
  });
}

function applyFilter(filterName) {
  if (!canvas || !originalData) return;
  // Restore original pixels first
  const imgData = new ImageData(new Uint8ClampedArray(originalData.data), originalData.width, originalData.height);

  if (filterName === 'bw') {
    const d = imgData.data;
    for (let i = 0; i < d.length; i += 4) {
      const gray = d[i] * 0.299 + d[i+1] * 0.587 + d[i+2] * 0.114;
      d[i] = d[i+1] = d[i+2] = gray;
    }
  } else if (filterName === 'enhanced') {
    const d = imgData.data;
    const contrast = 1.4;
    const offset = 128 * (1 - contrast);
    for (let i = 0; i < d.length; i += 4) {
      d[i]   = Math.min(255, Math.max(0, d[i] * contrast + offset));
      d[i+1] = Math.min(255, Math.max(0, d[i+1] * contrast + offset));
      d[i+2] = Math.min(255, Math.max(0, d[i+2] * contrast + offset));
    }
  }
  // 'original' — just use the restored data as-is

  canvas.width = imgData.width;
  canvas.height = imgData.height;
  currentWidth = imgData.width;
  currentHeight = imgData.height;
  ctx.putImageData(imgData, 0, 0);
  sendPreview();
}

function rotateImage(direction) {
  if (!canvas || !currentWidth || !currentHeight) return;
  const srcData = ctx.getImageData(0, 0, currentWidth, currentHeight);
  const newW = currentHeight;
  const newH = currentWidth;
  const dest = ctx.createImageData(newW, newH);
  const src = srcData.data;
  const dst = dest.data;

  for (let y = 0; y < currentHeight; y++) {
    for (let x = 0; x < currentWidth; x++) {
      const si = (y * currentWidth + x) * 4;
      let dx, dy;
      if (direction === 'right') {
        dx = currentHeight - 1 - y;
        dy = x;
      } else {
        dx = y;
        dy = currentWidth - 1 - x;
      }
      const di = (dy * newW + dx) * 4;
      dst[di] = src[si];
      dst[di+1] = src[si+1];
      dst[di+2] = src[si+2];
      dst[di+3] = src[si+3];
    }
  }

  canvas.width = newW;
  canvas.height = newH;
  currentWidth = newW;
  currentHeight = newH;
  ctx.putImageData(dest, 0, 0);
  // Update originalData for filter switching after rotation
  originalData = { data: new Uint8ClampedArray(dest.data), width: newW, height: newH };
  sendPreview();
}

self.onmessage = async function(e) {
  const { type } = e.data;

  try {
    if (type === 'scan') {
      const blob = e.data.blob;
      const bmp = await createImageBitmap(blob);
      currentWidth = bmp.width;
      currentHeight = bmp.height;
      canvas = new OffscreenCanvas(currentWidth, currentHeight);
      ctx = canvas.getContext('2d');
      ctx.drawImage(bmp, 0, 0);
      bmp.close();
      // Store original pixel data for filter switching
      const imgData = ctx.getImageData(0, 0, currentWidth, currentHeight);
      originalData = { data: new Uint8ClampedArray(imgData.data), width: currentWidth, height: currentHeight };
      sendPreview();
      return;
    }

    if (type === 'filter') {
      applyFilter(e.data.filter);
      return;
    }

    if (type === 'rotate') {
      rotateImage(e.data.direction);
      return;
    }

    if (type === 'save') {
      if (!canvas) {
        self.postMessage({ type: 'error', error: 'No image loaded' });
        return;
      }
      const blob = await canvas.convertToBlob({ type: 'image/jpeg', quality: 0.92 });
      const buf = await blob.arrayBuffer();
      self.postMessage({ type: 'saved', data: buf }, [buf]);
      return;
    }
  } catch (err) {
    self.postMessage({ type: 'error', error: err.message || 'Worker error' });
  }
};

// Signal ready
self.postMessage({ type: 'ready' });
