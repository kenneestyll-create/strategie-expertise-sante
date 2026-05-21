/**
 * legal_balance.js — Scene Engine V1 (Sprint 3)
 *
 * Format cible : F4 (juridique).
 * Pattern visuel : balance de justice dorée centrale qui s'incline progressivement
 * selon le poids narratif des chunks. Lignes verticales sobres en arrière-plan
 * suggérant des colonnes de tribunal. Référence article de loi sobre en haut.
 *
 * Charte stricte : navy + or + bordeaux discret. Aucune dramatisation gratuite.
 * Max 4 objets animés : balance, label article, citation, caption.
 * Camera : zoom calme 1.00 → 1.05.
 */
import { Scene, LAYER } from '../Scene.js';
import { easings, lerp } from '../easing.js';
import { CueTracker, chunksToCues } from '../timeline.js';
import { drawCaptionBox } from './stats_focus.js';

const GOLD = '#C9A84C';
const NAVY_DEEP = '#0a0e1c';
const NAVY = '#162136';
const BORDEAUX = '#7a1a1a';
const WHITE_SOFT = 'rgba(255,255,255,0.92)';

/** Extrait une référence d'article de loi du script si présente. */
function extractLegalRef(script) {
  if (!script) return null;
  const m = script.match(/(?:Art(?:icle)?\.?\s+)([LRD]?\.?\s?\d{1,4}[-–]?\d{0,3})\s*(CSS|CASF|Code\s+\w+)?/i);
  if (!m) return null;
  const ref = `Art. ${m[1].replace(/\s+/g, '').replace(/[–-]/g, '-')}`;
  return m[2] ? `${ref} ${m[2].toUpperCase()}` : ref;
}

export class LegalBalanceScene extends Scene {
  init() {
    super.init();
    this.tracker = new CueTracker(chunksToCues(this.chunks));
    this.legalRef = extractLegalRef(this.video?.script) || 'JURISPRUDENCE';
    this.tiltAngle = 0;     // radians ; ±0.10 max
    this.tiltTarget = 0;
    this._lastChunkIdx = -1;

    const totalDur = this.chunks.length ? this.chunks[this.chunks.length - 1].endSec : 20;
    const zoomMax = this.motionRule?.camera?.zoomRange?.[1] || 1.05;
    this.camera.startMove({
      toX: 0, toY: 0, toZoom: zoomMax,
      duration: totalDur, startTime: 0, easing: 'calm',
    });

    this.layers = [
      { z: LAYER.DECOR,   draw: (ctx) => this._drawColumns(ctx) },
      { z: LAYER.OBJECTS, draw: (ctx) => this._drawBalance(ctx) },
      { z: LAYER.TEXT,    draw: (ctx) => this._drawLegalRef(ctx) },
      { z: LAYER.OVERLAY, draw: (ctx) => this._drawCaption(ctx) },
    ];
  }

  update(delta, audioTime) {
    super.update(delta, audioTime);
    // Tilt narratif : alterne tilt gauche / droite / centre selon le chunk courant.
    const curIdx = this.tracker.current(audioTime);
    if (curIdx !== this._lastChunkIdx) {
      this._lastChunkIdx = curIdx;
      // alternance sobre : -0.08 / +0.08 / 0 / -0.05 / +0.05
      const seq = [-0.08, 0.08, 0, -0.05, 0.05, 0];
      this.tiltTarget = seq[Math.max(0, curIdx) % seq.length] || 0;
    }
    // Easing vers le target (transition douce)
    this.tiltAngle += (this.tiltTarget - this.tiltAngle) * 0.06;
  }

  drawBackground(ctx) {
    const g = ctx.createLinearGradient(0, 0, 0, this.height);
    g.addColorStop(0, NAVY_DEEP);
    g.addColorStop(1, NAVY);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, this.width, this.height);
  }

  _drawColumns(ctx) {
    // 2 lignes verticales très subtiles aux 1/4 et 3/4 (colonnes de tribunal)
    ctx.strokeStyle = 'rgba(201,168,76,0.08)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(this.width * 0.18, this.height * 0.10);
    ctx.lineTo(this.width * 0.18, this.height * 0.78);
    ctx.moveTo(this.width * 0.82, this.height * 0.10);
    ctx.lineTo(this.width * 0.82, this.height * 0.78);
    ctx.stroke();
  }

  _drawBalance(ctx) {
    const cx = this.width / 2;
    const cy = this.height * 0.42;
    const scale = 5.5; // (asset 64px → ~352px)
    const angle = this.tiltAngle;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.strokeStyle = GOLD;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = 2.2;

    // Pillar (fixed)
    ctx.beginPath();
    ctx.moveTo(0, -22 * scale * 0.18);
    ctx.lineTo(0, 22 * scale * 0.18);
    ctx.stroke();
    // Base (fixed)
    const baseY = 22 * scale * 0.18;
    ctx.beginPath();
    ctx.moveTo(-12 * scale * 0.18, baseY);
    ctx.lineTo(12 * scale * 0.18, baseY);
    ctx.moveTo(-6 * scale * 0.18, baseY + 4 * scale * 0.18);
    ctx.lineTo(6 * scale * 0.18, baseY + 4 * scale * 0.18);
    ctx.stroke();

    // Top finial
    ctx.beginPath();
    ctx.arc(0, -22 * scale * 0.18, 1.6 * scale * 0.18, 0, Math.PI * 2);
    ctx.stroke();

    // Beam + plates : tilted group
    ctx.save();
    ctx.translate(0, -14 * scale * 0.18);
    ctx.rotate(angle);
    const beamL = 18 * scale * 0.18;
    // beam
    ctx.beginPath();
    ctx.moveTo(-beamL, 0);
    ctx.lineTo(beamL, 0);
    ctx.stroke();
    // left chains + tray
    this._drawTray(ctx, -beamL, scale, angle);
    this._drawTray(ctx, beamL, scale, angle);
    ctx.restore();
    ctx.restore();
  }

  _drawTray(ctx, anchorX, scale, angle) {
    // chains
    const chainL = 12 * scale * 0.18;
    ctx.beginPath();
    ctx.moveTo(anchorX - 2, 0);
    ctx.lineTo(anchorX - 2, chainL);
    ctx.moveTo(anchorX + 2, 0);
    ctx.lineTo(anchorX + 2, chainL);
    ctx.stroke();
    // tray (auto-leveled : compensate beam rotation so tray stays horizontal)
    ctx.save();
    ctx.translate(anchorX, chainL);
    ctx.rotate(-angle); // compensate parent rotation
    ctx.beginPath();
    const trayW = 8 * scale * 0.18;
    ctx.moveTo(-trayW, 0);
    ctx.lineTo(trayW, 0);
    ctx.lineTo(trayW - 2, 3 * scale * 0.18);
    ctx.lineTo(-trayW + 2, 3 * scale * 0.18);
    ctx.closePath();
    ctx.stroke();
    ctx.restore();
  }

  _drawLegalRef(ctx) {
    // Sober legal label, top center, small caps gold
    ctx.font = '600 22px Inter, system-ui, sans-serif';
    ctx.fillStyle = GOLD;
    ctx.letterSpacing = '0.18em';
    const txt = this.legalRef.toUpperCase();
    const w = ctx.measureText(txt).width;
    ctx.fillText(txt, (this.width - w) / 2, this.height * 0.15);

    // Underline subtle
    ctx.strokeStyle = 'rgba(201,168,76,0.5)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo((this.width - w) / 2 - 8, this.height * 0.15 + 8);
    ctx.lineTo((this.width + w) / 2 + 8, this.height * 0.15 + 8);
    ctx.stroke();

    // Sub-anchor citation (italic serif) under balance
    const chunk = this.chunks.find((c) => this.audioTime >= c.startSec && this.audioTime < c.endSec);
    const quote = (chunk?.text || this.video?.hook_variants?.[0] || '').slice(0, 80);
    if (!quote) return;
    ctx.font = 'italic 600 26px Georgia, "Times New Roman", serif';
    ctx.fillStyle = WHITE_SOFT;
    const maxW = this.width - 120;
    const lines = wrapTwoLines(ctx, quote, maxW);
    const lineH = 34;
    const yStart = this.height * 0.66 - (lines.length - 1) * lineH / 2;
    for (let i = 0; i < lines.length; i++) {
      const lw = ctx.measureText(lines[i]).width;
      ctx.fillText(lines[i], (this.width - lw) / 2, yStart + i * lineH);
    }
  }

  _drawCaption(ctx) {
    const c = this.chunks.find((c) => this.audioTime >= c.startSec && this.audioTime < c.endSec);
    if (!c) return;
    drawCaptionBox(ctx, c.text, this.width, this.height);
  }
}

/** Helper local : wrap d'un texte sur au max 2 lignes (3e ligne tronquée par …) */
export function wrapTwoLines(ctx, text, maxWidth) {
  const words = (text || '').split(/\s+/).filter(Boolean);
  const lines = [];
  let cur = '';
  for (const w of words) {
    const t = cur ? `${cur} ${w}` : w;
    if (ctx.measureText(t).width > maxWidth && cur) {
      lines.push(cur);
      cur = w;
      if (lines.length === 2) break;
    } else {
      cur = t;
    }
  }
  if (cur && lines.length < 2) lines.push(cur);
  // If still words remaining, append … on last line
  if (lines.length === 2) {
    const rest = words.slice(lines.join(' ').split(/\s+/).length);
    if (rest.length > 0) {
      // truncate last line to fit + ellipsis
      let last = lines[1];
      while (ctx.measureText(last + '…').width > maxWidth && last.length > 0) {
        last = last.slice(0, -1);
      }
      lines[1] = last.trim() + '…';
    }
  }
  return lines;
}
