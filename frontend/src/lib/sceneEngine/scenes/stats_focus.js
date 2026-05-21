/**
 * stats_focus.js — Scene Engine V1
 *
 * Pattern visuel : chiffre central animé (count-up) + label + bar chart minimaliste.
 * Camera : slow zoom 1.00 → 1.06 sur toute la durée.
 * Adapté F2 (statistiques) et F5 (administratif via fallback).
 *
 * Source des données :
 *  - video.script (texte intégral, fallback hook si absent)
 *  - 1er nombre significatif détecté = "headline figure"
 *  - chunks audio → captions burned-in
 */
import { Scene, LAYER } from '../Scene.js';
import { easings, easingPresets, lerp } from '../easing.js';
import { CueTracker, chunksToCues } from '../timeline.js';

/** Extrait le 1er chiffre significatif du script (avec unité éventuelle) */
function extractHeadlineFigure(script) {
  if (!script) return { num: 48, unit: 'h' };
  const re = /(\d{1,4})\s*(€|%|h|j|jours|mois|ans|EUR|euros)?/i;
  const m = script.match(re);
  if (!m) return { num: 48, unit: 'h' };
  return { num: parseInt(m[1], 10), unit: (m[2] || '').toLowerCase().replace('eur', '€').replace('euros', '€') };
}

const GOLD = '#C9A84C';

export class StatsFocusScene extends Scene {
  init() {
    super.init();
    const { num, unit } = extractHeadlineFigure(this.video?.script);
    this.figureTarget = num;
    this.figureUnit = unit;
    this.figureCurrent = 0;
    this.tracker = new CueTracker(chunksToCues(this.chunks));

    // Slow zoom continu sur toute la durée audio
    const totalDur = this.chunks.length ? this.chunks[this.chunks.length - 1].endSec : 20;
    const zoomMax = this.motionRule?.camera?.zoomRange?.[1] || 1.06;
    this.camera.startMove({ toX: 0, toY: 0, toZoom: zoomMax, duration: totalDur, startTime: 0, easing: 'calm' });

    // Bar chart : 4 barres avec hauteurs cibles (max 6 objets animés total)
    this.bars = [0.4, 0.62, 0.78, 1.0]; // ratios cibles
    this.barHeights = [0, 0, 0, 0];

    // Layers (limite 6 objets/frame)
    this.layers = [
      { z: LAYER.DECOR,   draw: (ctx) => this._drawBarChart(ctx) },
      { z: LAYER.OBJECTS, draw: (ctx) => this._drawHeadline(ctx) },
      { z: LAYER.TEXT,    draw: (ctx) => this._drawLabel(ctx) },
      { z: LAYER.OVERLAY, draw: (ctx) => this._drawCaption(ctx) },
    ];
  }

  update(delta, audioTime) {
    super.update(delta, audioTime);
    const speed = this.motionRule?.speed || 1.0;
    // Count-up sur 1.5s (ajusté par rule.speed)
    const dur = 1.5 / speed;
    const t = Math.min(1, audioTime / dur);
    this.figureCurrent = Math.round(lerp(0, this.figureTarget, t, easings.easeOutPunch));
    // Bar chart staggered : 4 barres apparaissent entre t=0 et t=2.5s
    for (let i = 0; i < this.bars.length; i++) {
      const start = (i * 0.4) / speed;
      const end = start + 0.8 / speed;
      const tb = Math.max(0, Math.min(1, (audioTime - start) / (end - start)));
      this.barHeights[i] = lerp(0, this.bars[i], tb, easings.easeOutCalm);
    }
  }

  drawBackground(ctx) {
    const g = ctx.createLinearGradient(0, 0, this.width, this.height);
    g.addColorStop(0, '#0f172a');
    g.addColorStop(1, '#1e293b');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, this.width, this.height);
  }

  _drawBarChart(ctx) {
    // 4 barres verticales en bas, accent = motionRule.accent
    const accent = this.motionRule?.accent || '#3b82f6';
    const barW = 60;
    const gap = 30;
    const baseY = this.height * 0.7;
    const totalW = this.bars.length * barW + (this.bars.length - 1) * gap;
    const startX = (this.width - totalW) / 2;
    const maxH = 220;
    ctx.fillStyle = accent;
    ctx.globalAlpha = 0.7;
    for (let i = 0; i < this.bars.length; i++) {
      const h = this.barHeights[i] * maxH;
      ctx.fillRect(startX + i * (barW + gap), baseY - h, barW, h);
    }
    ctx.globalAlpha = 1;
  }

  _drawHeadline(ctx) {
    ctx.font = 'bold 180px Inter, system-ui, sans-serif';
    ctx.fillStyle = '#ffffff';
    ctx.shadowColor = 'rgba(0,0,0,0.5)';
    ctx.shadowBlur = 16;
    const text = `${this.figureCurrent}${this.figureUnit ? this.figureUnit : ''}`;
    const w = ctx.measureText(text).width;
    ctx.fillText(text, (this.width - w) / 2, this.height * 0.42);
    ctx.shadowBlur = 0;
  }

  _drawLabel(ctx) {
    const accent = this.motionRule?.accent || '#3b82f6';
    ctx.font = '600 28px Inter, system-ui, sans-serif';
    ctx.fillStyle = accent;
    const label = (this.video?.hook_variants?.[0] || 'STATISTIQUE').slice(0, 36).toUpperCase();
    const w = ctx.measureText(label).width;
    ctx.fillText(label, (this.width - w) / 2, this.height * 0.50);
  }

  _drawCaption(ctx) {
    const c = this.chunks.find((c) => this.audioTime >= c.startSec && this.audioTime < c.endSec);
    if (!c) return;
    drawCaptionBox(ctx, c.text, this.width, this.height);
  }
}

/** Helper partagé : caption bottom-center style TikTok (réutilisable par les scenes) */
export function drawCaptionBox(ctx, text, width, height) {
  if (!text) return;
  ctx.font = 'bold 30px Inter, system-ui, sans-serif';
  const maxW = width - 100;
  const padding = 12;
  const lineH = 38;
  // wrap
  const words = text.split(/\s+/);
  const lines = [];
  let cur = '';
  for (const w of words) {
    const t = cur ? `${cur} ${w}` : w;
    if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t;
  }
  if (cur) lines.push(cur);
  const slice = lines.slice(0, 3);
  const startY = height - 120 - slice.length * lineH;
  for (let i = 0; i < slice.length; i++) {
    const tw = ctx.measureText(slice[i]).width;
    const x = (width - tw) / 2;
    const y = startY + i * lineH;
    ctx.fillStyle = 'rgba(0,0,0,0.72)';
    ctx.fillRect(x - padding, y - 26, tw + padding * 2, lineH - 4);
    ctx.fillStyle = '#ffffff';
    ctx.fillText(slice[i], x, y);
  }
}
