/**
 * Scene.js — interface de base pour toutes les scènes du Scene Engine V1.
 *
 * Chaque scene concrète doit étendre cette classe et implémenter :
 *   - update(delta, audioTime)
 *   - draw(ctx)
 *   - reset()
 *
 * Layers (z-index simple) :
 *   - 0 : background
 *   - 1 : decor
 *   - 2 : objets animés
 *   - 3 : texte
 *   - 4 : overlay (captions, vignettes, HUD)
 */

export const LAYER = {
  BACKGROUND: 0,
  DECOR: 1,
  OBJECTS: 2,
  TEXT: 3,
  OVERLAY: 4,
};

export class Scene {
  /**
   * @param {Object} props
   * @param {number} props.width - canvas width
   * @param {number} props.height - canvas height
   * @param {Object} props.motionRule - profil Motion Rules (motionRules.js)
   * @param {Array}  props.chunks - chunks audio (timeline.js)
   * @param {Object} props.video - pack vidéo (hook, cta, etc.)
   * @param {Object} props.camera - instance Camera
   * @param {Object} props.assetLoader - instance AssetLoader
   */
  constructor(props) {
    this.width = props.width;
    this.height = props.height;
    this.motionRule = props.motionRule;
    this.chunks = props.chunks || [];
    this.video = props.video || {};
    this.camera = props.camera;
    this.assetLoader = props.assetLoader;
    this.layers = []; // tableau d'objets {z, draw(ctx, audioTime)}
    this.audioTime = 0;
    this._initialized = false;
  }

  /** À surcharger : initialiser les layers/animations en fonction des chunks */
  init() {
    this._initialized = true;
  }

  /** À surcharger : avancer animations en fonction du temps */
  update(delta, audioTime) {
    this.audioTime = audioTime;
    if (this.camera) this.camera.update(audioTime);
  }

  /** Dessine toutes les layers triées par z-index. À surcharger si besoin. */
  draw(ctx) {
    if (!this._initialized) this.init();
    // Background sans camera transform
    ctx.save();
    this.drawBackground(ctx);
    ctx.restore();
    // Layers avec camera transform
    ctx.save();
    if (this.camera) this.camera.apply(ctx, this.audioTime);
    const sorted = [...this.layers].sort((a, b) => (a.z || 0) - (b.z || 0));
    for (const layer of sorted) {
      try {
        layer.draw(ctx, this.audioTime);
      } catch (_) { /* ignore layer-level errors */ }
    }
    ctx.restore();
  }

  /** À surcharger pour fond gradient ou autre */
  drawBackground(ctx) {
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, this.width, this.height);
  }

  /** Reset état pour replay */
  reset() {
    this._initialized = false;
    this.layers = [];
    this.audioTime = 0;
    if (this.camera) this.camera.reset();
  }
}
