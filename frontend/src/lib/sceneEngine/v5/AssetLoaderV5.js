/**
 * AssetLoaderV5.js — Phase A minimal
 *
 * Charge des images réelles (Pexels CDN ou /public/v5-assets/) en HTMLImageElement
 * prêts pour ctx.drawImage(). Aucun cache, aucune API, aucune dépendance.
 *
 * Phase A scope : loadImage uniquement.
 * Phase B+ : ajouter loadVideo, preloadStoryboard, getMemoryFootprint.
 */

export class AssetLoaderV5 {
  /**
   * Charge une image et retourne un HTMLImageElement utilisable par drawImage.
   * @param {string} url - URL absolue ou relative
   * @param {number} timeoutMs - default 8000
   * @returns {Promise<HTMLImageElement>}
   */
  static loadImage(url, timeoutMs = 8000) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous'; // requis pour canvas tainted check
      let done = false;
      const t = setTimeout(() => {
        if (done) return;
        done = true;
        reject(new Error(`AssetLoaderV5.loadImage timeout (${timeoutMs}ms): ${url}`));
      }, timeoutMs);
      img.onload = () => {
        if (done) return;
        done = true;
        clearTimeout(t);
        resolve(img);
      };
      img.onerror = (e) => {
        if (done) return;
        done = true;
        clearTimeout(t);
        reject(new Error(`AssetLoaderV5.loadImage error: ${url}`));
      };
      img.src = url;
    });
  }

  /**
   * Charge plusieurs images séquentiellement (pas en parallèle pour ménager 4G).
   * @param {string[]} urls
   * @returns {Promise<HTMLImageElement[]>}
   */
  static async loadImages(urls) {
    const results = [];
    for (const u of urls) {
      results.push(await AssetLoaderV5.loadImage(u));
    }
    return results;
  }

  /**
   * Charge une vidéo et retourne un HTMLVideoElement prêt pour drawImage.
   * La vidéo est muted (pas d'audio, on a la voix-off TTS), playsInline,
   * loop si la durée du plan dépasse la vidéo. Attend readyState >= 2 (HAVE_CURRENT_DATA).
   * @param {string} url - URL MP4
   * @param {object} opts - {loop: boolean, timeoutMs: number}
   * @returns {Promise<HTMLVideoElement>}
   */
  static loadVideo(url, opts = {}) {
    const { loop = true, timeoutMs = 15000 } = opts;
    return new Promise((resolve, reject) => {
      const v = document.createElement('video');
      try {
        const isCrossOrigin = url.startsWith('http') && !url.startsWith(window.location.origin);
        if (isCrossOrigin) v.crossOrigin = 'anonymous';
      } catch (_) { /* ignore */ }
      v.muted = true;
      v.defaultMuted = true;
      v.setAttribute('muted', '');
      v.setAttribute('playsinline', '');
      v.playsInline = true;
      v.loop = loop;
      v.preload = 'auto';
      v.autoplay = true;
      let done = false;
      const finish = (ok, value) => {
        if (done) return;
        done = true;
        clearTimeout(t);
        ok ? resolve(value) : reject(value);
      };
      const t = setTimeout(() => {
        finish(false, new Error(`AssetLoaderV5.loadVideo timeout (${timeoutMs}ms): ${url}`));
      }, timeoutMs);
      // 'loadeddata' déclenche dès la 1ère frame décodée (suffisant pour drawImage).
      // Plus fiable que 'canplaythrough' en hidden DOM ou throttled.
      v.addEventListener('loadeddata', () => {
        // tentative de play (silencieuse sur Chromium en muted)
        v.play().catch(() => { /* OK même sans play, drawImage marche */ });
        finish(true, v);
      });
      v.addEventListener('error', (e) => {
        const code = v.error ? v.error.code : 'unknown';
        const msg = v.error ? v.error.message : '';
        finish(false, new Error(`AssetLoaderV5.loadVideo error code=${code} msg=${msg} url=${url}`));
      });
      // Mount hidden but with non-zero dimensions to ensure browser allocates decoder
      v.style.position = 'fixed';
      v.style.left = '-9999px';
      v.style.top = '0';
      v.style.width = '64px';
      v.style.height = '64px';
      v.style.opacity = '0';
      v.style.pointerEvents = 'none';
      document.body.appendChild(v);
      v.src = url;
      v.load();
    });
  }
}
