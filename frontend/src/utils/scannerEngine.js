/**
 * ScannerEngine — Moteur de traitement d'image pur JS, synchrone.
 * Basé sur le modèle ScannerUltime. Zéro Worker, zéro promesse.
 * Toutes les opérations sont < 50ms et s'exécutent sur le main thread.
 */
export class ScannerEngine {
  constructor() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });
    this.originalData = null; // image brute APRÈS auto-crop, AVANT filtres
    this.currentFilter = 'document';
    this.brightness = 0;
    this.contrast = 0;
    this.ready = false;
  }

  /**
   * Charge une image depuis un canvas source, détecte le document, recadre, applique le filtre.
   * @returns {{ url: string, autoDetected: boolean, corners: Array|null }}
   */
  scan(sourceCanvas, filter = 'document') {
    console.log('SCAN START');
    const t0 = performance.now();

    if (!sourceCanvas || !sourceCanvas.width || !sourceCanvas.height) {
      console.warn('[Engine] Canvas source invalide (width=0)');
      return null;
    }

    // Copier le canvas source
    this.canvas.width = sourceCanvas.width;
    this.canvas.height = sourceCanvas.height;
    this.ctx.drawImage(sourceCanvas, 0, 0);

    const fullW = this.canvas.width;
    const fullH = this.canvas.height;

    // Détection automatique de document
    const detection = this._autoDetect();

    if (detection.rect) {
      this._cropRect(detection.rect);
    }

    // Stocker l'image de base (après crop, avant filtre)
    this.originalData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);

    // Appliquer le filtre initial
    this.currentFilter = filter;
    this.brightness = 0;
    this.contrast = 0;
    this._render();

    this.ready = true;
    const url = this.canvas.toDataURL('image/jpeg', 0.92);
    console.log('SCAN DONE', Math.round(performance.now() - t0), 'ms');

    return {
      url,
      autoDetected: !!detection.rect,
      corners: detection.corners
        ? detection.corners.map(c => ({ x: c.x / fullW, y: c.y / fullH }))
        : null,
    };
  }

  /** Applique un filtre (bw | document | original). Synchrone. */
  applyFilter(type) {
    if (!this.ready || !this.originalData) return null;
    console.log('FILTER START:', type);
    const t0 = performance.now();
    this.currentFilter = type;
    this._render();
    const url = this.canvas.toDataURL('image/jpeg', 0.92);
    console.log('FILTER DONE', Math.round(performance.now() - t0), 'ms');
    return url;
  }

  /** Rotation 90° gauche ou droite. Met à jour originalData. */
  rotate(direction = 'right') {
    if (!this.ready) return null;
    console.log('ROTATE START:', direction);
    const t0 = performance.now();

    const w = this.canvas.width;
    const h = this.canvas.height;
    const temp = document.createElement('canvas');
    temp.width = h;
    temp.height = w;
    const tCtx = temp.getContext('2d');

    tCtx.translate(h / 2, w / 2);
    tCtx.rotate(direction === 'left' ? -Math.PI / 2 : Math.PI / 2);
    tCtx.drawImage(this.canvas, -w / 2, -h / 2);

    this.canvas.width = h;
    this.canvas.height = w;
    this.ctx.drawImage(temp, 0, 0);

    // Mettre à jour la base
    this.originalData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
    this._render();

    const url = this.canvas.toDataURL('image/jpeg', 0.92);
    console.log('ROTATE DONE', Math.round(performance.now() - t0), 'ms');
    return url;
  }

  /** Recadrage avec coordonnées normalisées {x0, y0, x1, y1}. Met à jour originalData. */
  crop(coords) {
    if (!this.ready) return null;
    console.log('CROP START');
    const t0 = performance.now();

    const { x0, y0, x1, y1 } = coords;
    const sx = Math.round(x0 * this.canvas.width);
    const sy = Math.round(y0 * this.canvas.height);
    const sw = Math.max(1, Math.round((x1 - x0) * this.canvas.width));
    const sh = Math.max(1, Math.round((y1 - y0) * this.canvas.height));

    const cropped = this.ctx.getImageData(sx, sy, sw, sh);
    this.canvas.width = sw;
    this.canvas.height = sh;
    this.ctx.putImageData(cropped, 0, 0);

    this.originalData = this.ctx.getImageData(0, 0, sw, sh);
    this._render();

    const url = this.canvas.toDataURL('image/jpeg', 0.92);
    console.log('CROP DONE', Math.round(performance.now() - t0), 'ms');
    return url;
  }

  /** Luminosité et contraste. Re-rend depuis originalData. */
  adjust(brightness, contrast) {
    if (!this.ready || !this.originalData) return null;
    console.log('ADJUST START b=' + brightness + ' c=' + contrast);
    const t0 = performance.now();
    this.brightness = brightness;
    this.contrast = contrast;
    this._render();
    const url = this.canvas.toDataURL('image/jpeg', 0.92);
    console.log('ADJUST DONE', Math.round(performance.now() - t0), 'ms');
    return url;
  }

  getDataUrl() {
    return this.canvas.toDataURL('image/jpeg', 0.92);
  }

  reset() {
    this.originalData = null;
    this.currentFilter = 'document';
    this.brightness = 0;
    this.contrast = 0;
    this.ready = false;
  }

  /* ════════════════ PRIVATE ════════════════ */

  /** Reconstruit l'image : originalData → filtre → luminosité/contraste → canvas */
  _render() {
    if (!this.originalData) return;
    const imgData = new ImageData(
      new Uint8ClampedArray(this.originalData.data),
      this.originalData.width,
      this.originalData.height
    );
    const d = imgData.data;

    // Filtre
    if (this.currentFilter === 'bw') {
      for (let i = 0; i < d.length; i += 4) {
        const g = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
        const val = g > 128 ? 255 : 0;
        d[i] = d[i + 1] = d[i + 2] = val;
      }
    } else if (this.currentFilter === 'document') {
      const f = (259 * (50 + 255)) / (255 * (259 - 50));
      for (let i = 0; i < d.length; i += 4) {
        d[i]     = Math.min(255, Math.max(0, f * (d[i]     - 128) + 128 + 12));
        d[i + 1] = Math.min(255, Math.max(0, f * (d[i + 1] - 128) + 128 + 12));
        d[i + 2] = Math.min(255, Math.max(0, f * (d[i + 2] - 128) + 128 + 12));
      }
    }
    // 'original' → pas de transformation

    // Luminosité / Contraste
    if (this.brightness !== 0 || this.contrast !== 0) {
      const cf = this.contrast !== 0 ? (259 * (this.contrast + 255)) / (255 * (259 - this.contrast)) : 1;
      for (let i = 0; i < d.length; i += 4) {
        d[i]     = Math.min(255, Math.max(0, cf * (d[i]     - 128) + 128 + this.brightness));
        d[i + 1] = Math.min(255, Math.max(0, cf * (d[i + 1] - 128) + 128 + this.brightness));
        d[i + 2] = Math.min(255, Math.max(0, cf * (d[i + 2] - 128) + 128 + this.brightness));
      }
    }

    this.canvas.width = imgData.width;
    this.canvas.height = imgData.height;
    this.ctx.putImageData(imgData, 0, 0);
  }

  /** Détection automatique : grayscale → edges → plus grand rectangle */
  _autoDetect() {
    const data = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
    const w = data.width;
    const h = data.height;
    const gray = this._grayscaleArray(data);
    const edges = this._cannyEdge(gray, w, h);
    const rect = this._detectLargestRect(edges, w, h);

    if (rect) {
      return {
        rect,
        corners: [
          { x: rect.left, y: rect.top },
          { x: rect.right, y: rect.top },
          { x: rect.right, y: rect.bottom },
          { x: rect.left, y: rect.bottom },
        ],
      };
    }
    return { rect: null, corners: null };
  }

  _cropRect(rect) {
    const { top, bottom, left, right } = rect;
    const w = right - left;
    const h = bottom - top;
    if (w <= 0 || h <= 0) return;
    const cropped = this.ctx.getImageData(left, top, w, h);
    this.canvas.width = w;
    this.canvas.height = h;
    this.ctx.putImageData(cropped, 0, 0);
  }

  _grayscaleArray(imgData) {
    const gray = new Uint8ClampedArray(imgData.width * imgData.height);
    const d = imgData.data;
    for (let i = 0, j = 0; i < d.length; i += 4, j++) {
      gray[j] = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
    }
    return gray;
  }

  _cannyEdge(gray, w, h) {
    const edges = new Uint8ClampedArray(w * h);
    for (let y = 1; y < h - 1; y++) {
      for (let x = 1; x < w - 1; x++) {
        const idx = y * w + x;
        const gx = gray[idx + 1] - gray[idx - 1];
        const gy = gray[idx + w] - gray[idx - w];
        const mag = Math.sqrt(gx * gx + gy * gy);
        edges[idx] = mag > 50 ? 255 : 0;
      }
    }
    return edges;
  }

  _detectLargestRect(edges, w, h) {
    let top = 0, bottom = h - 1, left = 0, right = w - 1;
    const threshold = 20 * 255;

    for (let y = 0; y < h; y++) {
      let s = 0; for (let x = 0; x < w; x++) s += edges[y * w + x];
      if (s > threshold) { top = y; break; }
    }
    for (let y = h - 1; y >= 0; y--) {
      let s = 0; for (let x = 0; x < w; x++) s += edges[y * w + x];
      if (s > threshold) { bottom = y; break; }
    }
    for (let x = 0; x < w; x++) {
      let s = 0; for (let y = 0; y < h; y++) s += edges[y * w + x];
      if (s > threshold) { left = x; break; }
    }
    for (let x = w - 1; x >= 0; x--) {
      let s = 0; for (let y = 0; y < h; y++) s += edges[y * w + x];
      if (s > threshold) { right = x; break; }
    }

    const cw = right - left;
    const ch = bottom - top;
    if (cw > w * 0.1 && ch > h * 0.1 && cw < w * 0.98 && ch < h * 0.98) {
      return { top, bottom, left, right };
    }
    return null;
  }
}
