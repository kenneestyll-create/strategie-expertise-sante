/**
 * office_admin.js — Scene Engine V1 (Sprint 3)
 *
 * Format cible : F1 (pédagogique) + F5 (administratif).
 * Pattern visuel : 1 document central + 1 tampon qui s'appose progressivement.
 * Aucun effet PowerPoint cheap, aucun wipe agressif. Mouvement lent, hiérarchie claire.
 *
 * Contraintes user :
 *   - 4 objets max simultanés : background grid + document + tampon + 1 ligne de texte
 *   - 1 accent or dominant (texte de validation), reste navy
 *   - 1 SEUL mouvement caméra actif (slow zoom 1.00 → 1.06)
 *   - Pas plus de 1 objet qui apparaît à la fois
 *
 * Approche "administratif sérieux" : reposant, mature, sans gimmick.
 */
import { Scene, LAYER } from '../Scene.js';
import { easings, lerp } from '../easing.js';
import { CueTracker, chunksToCues } from '../timeline.js';
import { drawCaptionBox } from './stats_focus.js';
import { wrapTwoLines } from './legal_balance.js';

const GOLD = '#C9A84C';
const NAVY_DEEP = '#0a0e1c';
const NAVY = '#162136';
const INDIGO = '#6366f1';

export class OfficeAdminScene extends Scene {
  init() {
    super.init();
    this.tracker = new CueTracker(chunksToCues(this.chunks));
    const totalDur = this.chunks.length ? this.chunks[this.chunks.length - 1].endSec : 20;
    const zoomMax = this.motionRule?.camera?.zoomRange?.[1] || 1.06;
    const speed = this.motionRule?.speed || 1.0;
    // 1 SEUL mouvement caméra : slow zoom continu (durée fixe, plus de speed sur camera pour rester sobre)
    this.camera.startMove({
      toX: 0, toY: 0, toZoom: zoomMax,
      duration: totalDur, startTime: 0, easing: this.motionRule?.easing || 'calm',
    });

    // Timings d'apparition séquentielle (en s) — pas plus de 1 nouveau objet à la fois.
    // F1 (pédagogique, speed=0.75) => plus lent ; F5 (administratif, speed=1.0) => standard.
    this.t_doc_in = 0.3 / speed;
    this.t_stamp_in = Math.min(2.5 / speed, totalDur * 0.40);
    this.t_text_in = Math.min(3.5 / speed, totalDur * 0.55);

    this.layers = [
      { z: LAYER.DECOR,   draw: (ctx) => this._drawGridFloor(ctx) },
      { z: LAYER.OBJECTS, draw: (ctx) => this._drawDocument(ctx) },
      { z: LAYER.OBJECTS, draw: (ctx) => this._drawStamp(ctx) },
      { z: LAYER.TEXT,    draw: (ctx) => this._drawHookLine(ctx) },
      { z: LAYER.OVERLAY, draw: (ctx) => this._drawCaption(ctx) },
    ];
  }

  drawBackground(ctx) {
    const g = ctx.createLinearGradient(0, 0, 0, this.height);
    g.addColorStop(0, NAVY_DEEP);
    g.addColorStop(1, NAVY);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, this.width, this.height);
  }

  /** Très subtile grille de fond (suggère "table de bureau") */
  _drawGridFloor(ctx) {
    ctx.strokeStyle = 'rgba(201,168,76,0.04)';
    ctx.lineWidth = 1;
    const step = 80;
    for (let x = 0; x < this.width; x += step) {
      ctx.beginPath(); ctx.moveTo(x, this.height * 0.72); ctx.lineTo(x, this.height); ctx.stroke();
    }
    for (let y = this.height * 0.72; y < this.height; y += step / 1.5) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(this.width, y); ctx.stroke();
    }
  }

  /** Document central avec lignes de texte abstraites */
  _drawDocument(ctx) {
    const t = (this.audioTime - this.t_doc_in);
    if (t < 0) return;
    const fadeT = Math.min(1, t / 0.6);
    const alpha = easings.easeOutCalm(fadeT);
    const slideY = (1 - alpha) * 30; // slide-in up

    const cx = this.width / 2;
    const cy = this.height * 0.42 + slideY;
    const docW = 320;
    const docH = 440;

    ctx.save();
    ctx.globalAlpha = alpha;
    // ombre douce
    ctx.shadowColor = 'rgba(0,0,0,0.35)';
    ctx.shadowBlur = 18;
    ctx.shadowOffsetY = 8;
    // page
    ctx.fillStyle = '#f4ecd6';
    ctx.fillRect(cx - docW / 2, cy - docH / 2, docW, docH);
    ctx.shadowBlur = 0;
    ctx.shadowOffsetY = 0;
    // coin replié (fold)
    ctx.fillStyle = '#e2d8b8';
    ctx.beginPath();
    ctx.moveTo(cx + docW / 2 - 36, cy - docH / 2);
    ctx.lineTo(cx + docW / 2, cy - docH / 2);
    ctx.lineTo(cx + docW / 2, cy - docH / 2 + 36);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = 'rgba(122,99,40,0.4)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cx + docW / 2 - 36, cy - docH / 2);
    ctx.lineTo(cx + docW / 2 - 36, cy - docH / 2 + 36);
    ctx.lineTo(cx + docW / 2, cy - docH / 2 + 36);
    ctx.stroke();

    // lignes de contenu (4)
    ctx.strokeStyle = 'rgba(40,30,15,0.45)';
    ctx.lineWidth = 2;
    const padX = 36;
    const lineY = [cy - docH / 2 + 80, cy - docH / 2 + 140, cy - docH / 2 + 200, cy - docH / 2 + 260];
    const widths = [docW - padX * 2, docW - padX * 2, docW - padX * 2, docW * 0.55];
    for (let i = 0; i < 4; i++) {
      ctx.beginPath();
      ctx.moveTo(cx - docW / 2 + padX, lineY[i]);
      ctx.lineTo(cx - docW / 2 + padX + widths[i], lineY[i]);
      ctx.stroke();
    }
    ctx.restore();
  }

  /** Tampon qui descend et s'appose ; "thump" (zoom 1.4 → 1.0) sur impact.
   *  La vitesse + intensité du thump suivent motionRule.speed/intensity (signature F1 vs F5).
   */
  _drawStamp(ctx) {
    const t = (this.audioTime - this.t_stamp_in);
    if (t < 0) return;
    const speed = this.motionRule?.speed || 1.0;
    const intensity = this.motionRule?.intensity || 'medium';
    const dur = 0.8 / speed;
    const tt = Math.min(1, t / dur);
    // scale anim : intensity high → bounce + large, low → calmer
    const startScale = intensity === 'high' ? 1.7 : (intensity === 'low' ? 1.35 : 1.5);
    const scale = lerp(startScale, 1.0, tt, easings.easeBackOut);
    // alpha fade-in rapide
    const alpha = Math.min(1, t / (0.25 / speed));
    // post-impact pulse subtle (1 cycle léger, plus marqué si high)
    const pulseAmp = intensity === 'high' ? 0.06 : 0.04;
    const postPulse = tt >= 1 ? (1 - pulseAmp) + pulseAmp * Math.cos((t - dur) * 10) * Math.exp(-(t - dur) * 5) : 1;
    const finalScale = scale * postPulse;

    const cx = this.width / 2 + 80; // décalé bas-droit sur le document
    const cy = this.height * 0.52;
    const r = 60 * finalScale;

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(cx, cy);
    // tampon : double cercle + "✓" central, palette accent
    const accent = this.motionRule?.accent || GOLD;
    ctx.strokeStyle = accent;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(0, 0, r, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0, 0, r * 0.75, 0, Math.PI * 2);
    ctx.stroke();
    // check
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(-r * 0.32, 0);
    ctx.lineTo(-r * 0.08, r * 0.28);
    ctx.lineTo(r * 0.42, -r * 0.30);
    ctx.stroke();
    ctx.restore();
  }

  /** 1 ligne de texte clé (hook) en haut, typo sobre */
  _drawHookLine(ctx) {
    const t = (this.audioTime - this.t_text_in);
    if (t < 0) return;
    const alpha = Math.min(1, t / 0.5);
    ctx.save();
    ctx.globalAlpha = alpha;
    const hook = (this.video?.hook_variants?.[0] || this.video?.script || '').trim();
    ctx.font = '600 30px Inter, system-ui, sans-serif';
    ctx.fillStyle = '#ffffff';
    const maxW = this.width - 100;
    const lines = wrapTwoLines(ctx, hook, maxW);
    const lineH = 38;
    const yStart = this.height * 0.16;
    for (let i = 0; i < lines.length; i++) {
      const lw = ctx.measureText(lines[i]).width;
      ctx.fillText(lines[i], (this.width - lw) / 2, yStart + i * lineH);
    }
    // Underline gold subtle below text
    ctx.strokeStyle = GOLD;
    ctx.lineWidth = 2;
    const underLW = Math.min(120, this.width * 0.2);
    ctx.beginPath();
    ctx.moveTo((this.width - underLW) / 2, yStart + lines.length * lineH + 4);
    ctx.lineTo((this.width + underLW) / 2, yStart + lines.length * lineH + 4);
    ctx.stroke();
    ctx.restore();
  }

  _drawCaption(ctx) {
    const c = this.chunks.find((c) => this.audioTime >= c.startSec && this.audioTime < c.endSec);
    if (!c) return;
    drawCaptionBox(ctx, c.text, this.width, this.height);
  }
}
