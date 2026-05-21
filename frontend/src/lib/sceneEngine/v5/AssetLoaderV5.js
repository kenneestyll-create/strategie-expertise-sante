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
}
