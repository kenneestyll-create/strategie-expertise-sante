/**
 * camera.js — Scene Engine V1
 * Camera 2.5D simulée : pan (x,y) + zoom + shake.
 * Appliquée sur le canvas via ctx.translate + ctx.scale.
 *
 * NE PAS oublier ctx.save() / ctx.restore() autour de l'application.
 */
import { easingPresets, lerp } from './easing.js';

export class Camera {
  constructor({ width, height }) {
    this.width = width;
    this.height = height;
    this.reset();
  }

  reset() {
    this.x = 0;
    this.y = 0;
    this.zoom = 1;
    this.shakeAmplitude = 0;
    this.shakeStartTime = 0;
    this.shakeDuration = 0;
    this._activeMove = null;
  }

  /**
   * Lance un mouvement de caméra continu.
   * @param {Object} opts {toX, toY, toZoom, duration (s), startTime (s), easing}
   */
  startMove({ toX = this.x, toY = this.y, toZoom = this.zoom, duration = 1, startTime = 0, easing = 'calm' }) {
    this._activeMove = {
      fromX: this.x,
      fromY: this.y,
      fromZoom: this.zoom,
      toX, toY, toZoom,
      duration,
      startTime,
      ease: easingPresets[easing] || easingPresets.calm,
    };
  }

  /**
   * Lance un shake court (V1: pour alert_urgency F6/F7).
   * @param {Object} opts {amplitude (px), duration (s), startTime (s)}
   */
  startShake({ amplitude = 3, duration = 0.15, startTime = 0 }) {
    this.shakeAmplitude = Math.min(amplitude, 3); // strict cap ±3px
    this.shakeDuration = Math.min(duration, 0.15); // strict cap 150ms
    this.shakeStartTime = startTime;
  }

  /** Avancer la caméra en fonction du temps absolu (audioTime ou elapsed) */
  update(audioTime) {
    if (this._activeMove) {
      const m = this._activeMove;
      const t = Math.max(0, Math.min(1, (audioTime - m.startTime) / m.duration));
      this.x = lerp(m.fromX, m.toX, t, m.ease);
      this.y = lerp(m.fromY, m.toY, t, m.ease);
      this.zoom = lerp(m.fromZoom, m.toZoom, t, m.ease);
      if (t >= 1) this._activeMove = null;
    }
  }

  /** Décalage shake actif pour la frame courante (px) — décroissant */
  getShakeOffset(audioTime) {
    if (!this.shakeDuration) return { dx: 0, dy: 0 };
    const t = (audioTime - this.shakeStartTime) / this.shakeDuration;
    if (t < 0 || t > 1) return { dx: 0, dy: 0 };
    const decay = 1 - t; // décroissance linéaire
    const amp = this.shakeAmplitude * decay;
    return {
      dx: (Math.random() - 0.5) * 2 * amp,
      dy: (Math.random() - 0.5) * 2 * amp,
    };
  }

  /**
   * Applique la transformation caméra au context.
   * Utilisation : ctx.save(); camera.apply(ctx, audioTime); ... ctx.restore();
   */
  apply(ctx, audioTime) {
    const shake = this.getShakeOffset(audioTime);
    const cx = this.width / 2;
    const cy = this.height / 2;
    ctx.translate(cx + this.x + shake.dx, cy + this.y + shake.dy);
    ctx.scale(this.zoom, this.zoom);
    ctx.translate(-cx, -cy);
  }
}
