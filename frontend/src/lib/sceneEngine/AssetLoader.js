/**
 * AssetLoader.js — Scene Engine V1
 *
 * Preload SVG → cache HTMLImageElement.
 * Fallback gracieux : si l'asset n'existe pas, retourne null sans crash.
 *
 * Usage :
 *   const loader = new AssetLoader();
 *   await loader.preload(['/scene-assets/balance.svg', ...]);
 *   const img = loader.get('/scene-assets/balance.svg'); // HTMLImageElement ou null
 *   if (img) ctx.drawImage(img, x, y, w, h);
 */

export class AssetLoader {
  constructor() {
    this.cache = new Map(); // path -> HTMLImageElement
    this.failures = new Set();
  }

  /**
   * Charge une liste d'URLs SVG/PNG. Résolu quand tout est tenté.
   * @param {string[]} paths
   */
  async preload(paths) {
    const promises = (paths || []).map((p) => this._loadOne(p));
    await Promise.all(promises);
    return {
      loaded: this.cache.size,
      failed: this.failures.size,
      total: paths.length,
    };
  }

  _loadOne(path) {
    return new Promise((resolve) => {
      if (this.cache.has(path) || this.failures.has(path)) {
        resolve();
        return;
      }
      const img = new Image();
      img.onload = () => {
        this.cache.set(path, img);
        resolve();
      };
      img.onerror = () => {
        this.failures.add(path);
        resolve(); // ne rejette PAS : fallback gracieux
      };
      img.src = path;
    });
  }

  /** Retourne l'image cachée ou null */
  get(path) {
    return this.cache.get(path) || null;
  }

  /** True si toutes les paths demandées ont été chargées sans échec */
  isReady(paths) {
    return (paths || []).every((p) => this.cache.has(p));
  }
}
