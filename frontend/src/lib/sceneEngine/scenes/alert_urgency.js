/**
 * alert_urgency.js — Scene Engine V1
 *
 * Pattern : flash rouge subtil + shake (P2.A) + warning icon pulsating + texte court.
 * Adapté F6 (urgence) et F7 (mix alerte/info via accent moins agressif).
 *
 * Shake : ±2-3px (selon motionRule.camera.shakeAmp), 150ms max,
 * déclenché uniquement sur le changement de chunk audio (impact synchrone).
 */
import { Scene, LAYER } from '../Scene.js';
import { easings, lerp } from '../easing.js';
import { CueTracker, chunksToCues } from '../timeline.js';
import { drawCaptionBox } from './stats_focus.js';

export class AlertUrgencyScene extends Scene {
  init() {
    super.init();
    this.tracker = new CueTracker(chunksToCues(this.chunks));
    this.lastShakeAt = -10;
    this.flashFiredAt = -10;
    this.pulsePhase = 0;

    // Camera zoom minimal continu (F6/F7 plus rapide)
    const totalDur = this.chunks.length ? this.chunks[this.chunks.length - 1].endSec : 20;
    const zoomMax = this.motionRule?.camera?.zoomRange?.[1] || 1.10;
    const easeName = this.motionRule?.easing || 'dramatic';
    this.camera.startMove({ toX: 0, toY: 0, toZoom: zoomMax, duration: totalDur, startTime: 0, easing: easeName });

    this.layers = [
      { z: LAYER.DECOR,   draw: (ctx) => this._drawWarningRing(ctx) },
      { z: LAYER.OBJECTS, draw: (ctx) => this._drawWarningIcon(ctx) },
      { z: LAYER.TEXT,    draw: (ctx) => this._drawAlertLabel(ctx) },
      { z: LAYER.TEXT,    draw: (ctx) => this._drawCountdown(ctx) },
      { z: LAYER.OVERLAY, draw: (ctx) => this._drawFlashOverlay(ctx) },
      { z: LAYER.OVERLAY, draw: (ctx) => this._drawCaption(ctx) },
    ];
  }

  update(delta, audioTime) {
    super.update(delta, audioTime);
    // Déclenche shake + flash au début de chaque chunk (impact narratif)
    const curIdx = this.tracker.current(audioTime);
    if (curIdx >= 0 && curIdx !== this._lastChunkIdx) {
      this._lastChunkIdx = curIdx;
      this.lastShakeAt = audioTime;
      this.flashFiredAt = audioTime;
      if (this.motionRule?.camera?.allowShake && this.camera) {
        this.camera.startShake({
          amplitude: this.motionRule.camera.shakeAmp || 3, // strict ±2-3px
          duration: this.motionRule.camera.shakeDur || 0.15, // strict ≤150ms
          startTime: audioTime,
        });
      }
    }
    this.pulsePhase = audioTime * 2; // 2 Hz pulse
  }

  drawBackground(ctx) {
    // Navy avec gradient subtil rougeoyant
    const g = ctx.createRadialGradient(this.width / 2, this.height / 2, 200, this.width / 2, this.height / 2, this.width * 0.9);
    g.addColorStop(0, '#1a0a0a');
    g.addColorStop(1, '#0a0a0a');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, this.width, this.height);
  }

  _drawWarningRing(ctx) {
    // Ring pulsant autour du centre
    const accent = this.motionRule?.accent || '#dc2626';
    const pulse = 0.5 + 0.5 * Math.sin(this.pulsePhase);
    const r = 200 + pulse * 12;
    ctx.strokeStyle = accent;
    ctx.globalAlpha = 0.35 + pulse * 0.25;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(this.width / 2, this.height * 0.42, r, 0, Math.PI * 2);
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  _drawWarningIcon(ctx) {
    // Triangle warning vectoriel (pas d'asset externe en V1)
    const cx = this.width / 2;
    const cy = this.height * 0.42;
    const size = 120;
    const pulse = 0.92 + 0.08 * Math.sin(this.pulsePhase);
    const scale = size * pulse;
    const accent = this.motionRule?.accent || '#dc2626';

    ctx.save();
    ctx.translate(cx, cy);
    ctx.shadowColor = 'rgba(220,38,38,0.5)';
    ctx.shadowBlur = 22;
    // Triangle
    ctx.fillStyle = accent;
    ctx.beginPath();
    ctx.moveTo(0, -scale);
    ctx.lineTo(scale * 0.866, scale * 0.5);
    ctx.lineTo(-scale * 0.866, scale * 0.5);
    ctx.closePath();
    ctx.fill();
    ctx.shadowBlur = 0;
    // "!" intérieur
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${Math.round(scale * 1.0)}px Inter, sans-serif`;
    const w = ctx.measureText('!').width;
    ctx.fillText('!', -w / 2, scale * 0.35);
    ctx.restore();
  }

  _drawAlertLabel(ctx) {
    ctx.font = '700 26px Inter, system-ui, sans-serif';
    ctx.fillStyle = this.motionRule?.accent || '#dc2626';
    const label = 'ALERTE';
    const w = ctx.measureText(label).width;
    ctx.fillText(label, (this.width - w) / 2, this.height * 0.62);
  }

  _drawCountdown(ctx) {
    // Détecte un nombre + "h" ou "j" dans le hook ou script
    const hook = this.video?.hook_variants?.[0] || this.video?.script || '';
    const m = hook.match(/(\d{1,3})\s*(h|j|jours?)/i);
    if (!m) return;
    ctx.font = 'bold 80px Inter, system-ui, sans-serif';
    ctx.fillStyle = '#ffffff';
    ctx.shadowColor = 'rgba(0,0,0,0.5)';
    ctx.shadowBlur = 12;
    const t = `${m[1]}${m[2].toLowerCase()}`;
    const w = ctx.measureText(t).width;
    ctx.fillText(t, (this.width - w) / 2, this.height * 0.72);
    ctx.shadowBlur = 0;
  }

  _drawFlashOverlay(ctx) {
    if (this.flashFiredAt < 0) return;
    const dt = this.audioTime - this.flashFiredAt;
    if (dt < 0 || dt > 0.25) return;
    const a = 0.18 * (1 - dt / 0.25);
    ctx.fillStyle = `rgba(220, 38, 38, ${a})`;
    ctx.fillRect(0, 0, this.width, this.height);
  }

  _drawCaption(ctx) {
    const c = this.chunks.find((c) => this.audioTime >= c.startSec && this.audioTime < c.endSec);
    if (!c) return;
    drawCaptionBox(ctx, c.text, this.width, this.height);
  }
}
