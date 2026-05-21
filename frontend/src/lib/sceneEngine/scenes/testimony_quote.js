/**
 * testimony_quote.js — Scene Engine V1 (Sprint 3)
 *
 * Format cible : F3 (témoignage).
 * Approche "documentaire" : silhouette d'arrière-plan très subtile, typo
 * dominante en serif italique, guillemets dorés en grand, signature anonyme.
 *
 * Contraintes user :
 *   - éviter l'effet "citation Instagram" (palette flashy, gradient, emoji)
 *   - sobre, presque documentaire
 *   - typographie dominante
 *   - silhouette secondaire (jamais frontale)
 */
import { Scene, LAYER } from '../Scene.js';
import { easings, lerp } from '../easing.js';
import { CueTracker, chunksToCues } from '../timeline.js';
import { drawCaptionBox } from './stats_focus.js';
import { wrapTwoLines } from './legal_balance.js';

const GOLD = '#C9A84C';
const GOLD_SOFT = 'rgba(201,168,76,0.85)';
const NAVY_DEEP = '#0a0e1c';
const NAVY = '#1a1f33';

export class TestimonyQuoteScene extends Scene {
  init() {
    super.init();
    this.tracker = new CueTracker(chunksToCues(this.chunks));
    const totalDur = this.chunks.length ? this.chunks[this.chunks.length - 1].endSec : 20;
    const zoomMax = this.motionRule?.camera?.zoomRange?.[1] || 1.04;
    // Camera très très lente (0.5% zoom/sec environ)
    this.camera.startMove({
      toX: 0, toY: 0, toZoom: zoomMax,
      duration: totalDur, startTime: 0, easing: 'calm',
    });

    this.layers = [
      { z: LAYER.DECOR,   draw: (ctx) => this._drawSilhouette(ctx) },
      { z: LAYER.OBJECTS, draw: (ctx) => this._drawQuoteMarks(ctx) },
      { z: LAYER.TEXT,    draw: (ctx) => this._drawQuoteText(ctx) },
      { z: LAYER.TEXT,    draw: (ctx) => this._drawSignature(ctx) },
      { z: LAYER.OVERLAY, draw: (ctx) => this._drawCaption(ctx) },
    ];
  }

  drawBackground(ctx) {
    // Navy uni profond, vignette douce
    ctx.fillStyle = NAVY_DEEP;
    ctx.fillRect(0, 0, this.width, this.height);
    const g = ctx.createRadialGradient(
      this.width / 2, this.height * 0.42, 80,
      this.width / 2, this.height * 0.42, this.width * 0.85,
    );
    g.addColorStop(0, 'rgba(40,46,72,0.6)');
    g.addColorStop(1, 'rgba(10,14,28,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, this.width, this.height);
  }

  /** Silhouette anonyme (3/4 dos, jamais frontale) — très basse opacité */
  _drawSilhouette(ctx) {
    const t = Math.min(1, this.audioTime / 2);
    const alpha = lerp(0, 0.12, t, easings.easeOutCalm);
    ctx.save();
    ctx.globalAlpha = alpha;
    // Tête (ovale)
    const cx = this.width / 2;
    const cy = this.height * 0.32;
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.ellipse(cx, cy, 90, 110, 0, 0, Math.PI * 2);
    ctx.fill();
    // Épaules (trapèze arrondi)
    ctx.beginPath();
    ctx.moveTo(cx - 200, cy + 360);
    ctx.lineTo(cx - 170, cy + 110);
    ctx.quadraticCurveTo(cx, cy + 70, cx + 170, cy + 110);
    ctx.lineTo(cx + 200, cy + 360);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  /** Guillemets dorés (ouvrant haut-gauche, fermant bas-droit) */
  _drawQuoteMarks(ctx) {
    const t = Math.min(1, this.audioTime / 1.2);
    const alpha = lerp(0, 1, t, easings.easeOutCalm);
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = GOLD;
    ctx.font = 'bold 220px Georgia, "Times New Roman", serif';

    // Ouvrant
    ctx.fillText('“', this.width * 0.06, this.height * 0.32);
    // Fermant (mirror visuel)
    const closingW = ctx.measureText('”').width;
    ctx.fillText('”', this.width - this.width * 0.06 - closingW, this.height * 0.82);

    ctx.restore();
  }

  /** Citation centrale en serif italique, dévoilement progressif (chunks) */
  _drawQuoteText(ctx) {
    const chunk = this.chunks.find((c) => this.audioTime >= c.startSec && this.audioTime < c.endSec);
    const fallback = (this.video?.hook_variants?.[0] || this.video?.script || '').slice(0, 160);
    const txt = (chunk?.text || fallback).replace(/[«»"]/g, '').trim();
    if (!txt) return;

    // Fade entre chunks (200ms à chaque transition)
    const localT = chunk ? (this.audioTime - chunk.startSec) : 0;
    const alpha = Math.min(1, localT / 0.4);

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.font = 'italic 600 38px Georgia, "Times New Roman", serif';
    ctx.fillStyle = 'rgba(255,255,255,0.96)';
    const maxW = this.width - 120;
    const lines = wrapTwoLines(ctx, txt, maxW);
    // Si > 80 chars, accepter 3 lignes pour ne pas tronquer (override sober)
    if (txt.length > 80 && lines.length === 2 && lines[1].endsWith('…')) {
      // recalcul avec 3 lignes max
      const words = txt.split(/\s+/);
      const tri = [];
      let cur = '';
      for (const w of words) {
        const tst = cur ? `${cur} ${w}` : w;
        if (ctx.measureText(tst).width > maxW && cur) { tri.push(cur); cur = w; if (tri.length === 3) break; }
        else cur = tst;
      }
      if (cur && tri.length < 3) tri.push(cur);
      lines.length = 0;
      tri.forEach((l) => lines.push(l));
    }
    const lineH = 50;
    const yStart = this.height * 0.46 - (lines.length - 1) * lineH / 2;
    for (let i = 0; i < lines.length; i++) {
      const lw = ctx.measureText(lines[i]).width;
      ctx.fillText(lines[i], (this.width - lw) / 2, yStart + i * lineH);
    }
    ctx.restore();
  }

  /** Signature anonyme + ligne dorée fine séparatrice (accent ambre F3 si défini) */
  _drawSignature(ctx) {
    const t = Math.min(1, (this.audioTime - 1.5) / 0.8);
    if (t <= 0) return;
    const alpha = easings.easeOutCalm(t);
    ctx.save();
    ctx.globalAlpha = alpha;
    // Couleur d'accent : F3 ambre #f59e0b, fallback or
    const accent = this.motionRule?.accent || GOLD_SOFT;
    // Ligne accent fine
    ctx.strokeStyle = accent;
    ctx.globalAlpha = alpha * 0.7;
    ctx.lineWidth = 1;
    const lw = 100;
    const yLine = this.height * 0.74;
    ctx.beginPath();
    ctx.moveTo((this.width - lw) / 2, yLine);
    ctx.lineTo((this.width + lw) / 2, yLine);
    ctx.stroke();
    // Signature texte (typo sobre)
    ctx.globalAlpha = alpha;
    ctx.font = '500 18px Inter, system-ui, sans-serif';
    ctx.fillStyle = accent;
    ctx.letterSpacing = '0.14em';
    const sig = 'TÉMOIGNAGE ANONYMISÉ';
    const sw = ctx.measureText(sig).width;
    ctx.fillText(sig, (this.width - sw) / 2, yLine + 22);
    ctx.restore();
  }

  _drawCaption(ctx) {
    const c = this.chunks.find((c) => this.audioTime >= c.startSec && this.audioTime < c.endSec);
    if (!c) return;
    drawCaptionBox(ctx, c.text, this.width, this.height);
  }
}
