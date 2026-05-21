/**
 * BackgroundImagePlan.js — Phase A + extension Phase C (crop region) + Phase D (highlight)
 *
 * Plan = 1 image (fullscreen OU zone croppée 9:16) + Ken Burns + filtre navy/or + sous-titres
 *      + (Phase D) highlight rectangle dessiné progressivement sur mot-clé.
 *
 * cropRegion (Phase C) : {sx, sy, sw, sh} en pixels SOURCE (image).
 * highlight (Phase D) : {sx, sy, sw, sh, appearAt, holdFor} en pixels SOURCE.
 *   - appearAt (s) : moment dans le plan où le highlight commence à se dessiner
 *   - holdFor (s) : durée de maintien après dessin complet (~600ms typique)
 *
 * Garde-fou contrat V5 §1 : un rectangle 2px or autour d'un mot-clé n'est PAS
 * un dessin géométrique "abstrait" — c'est un overlay de pointage (équivalent
 * au "pointage" CapCut sur un asset réel). Reste sobre.
 */
import { PlanV5 } from '../PlanV5.js';

export class BackgroundImagePlan extends PlanV5 {
  constructor(opts) {
    super(opts);
    if (!this.asset || !(this.asset instanceof HTMLImageElement)) {
      throw new Error(
        'V5_CONSTRAINTS §3: BackgroundImagePlan requires an HTMLImageElement asset.'
      );
    }
    this.cropRegion = opts.cropRegion || null;
    // Phase D : highlight overlay sur mot-clé (coordonnées en pixels SOURCE)
    this.highlight = opts.highlight || null;
  }

  /** Mappe un rectangle en pixels SOURCE vers les coordonnées DISPLAY courantes
   *  (en tenant compte de cropRegion + Ken Burns). */
  _mapSourceRectToDisplay(srcRect, w, h) {
    const aw = this.asset.naturalWidth || this.asset.width;
    const ah = this.asset.naturalHeight || this.asset.height;
    let cropSx = 0, cropSy = 0, cropSw = aw, cropSh = ah;
    if (this.cropRegion) {
      cropSx = this.cropRegion.sx;
      cropSy = this.cropRegion.sy;
      cropSw = this.cropRegion.sw;
      cropSh = this.cropRegion.sh;
    }
    // Position du rect SOURCE dans la sous-image croppée (en coordonnées source)
    const rectInCropX = srcRect.sx - cropSx;
    const rectInCropY = srcRect.sy - cropSy;
    // Ratio dans la sous-image
    const rxRatio = rectInCropX / cropSw;
    const ryRatio = rectInCropY / cropSh;
    const rwRatio = srcRect.sw / cropSw;
    const rhRatio = srcRect.sh / cropSh;
    // Application au draw rect courant (avec Ken Burns)
    const { dx, dy, dw, dh } = this.computeKenBurnsRect(w, h, cropSw, cropSh);
    return {
      x: dx + rxRatio * dw,
      y: dy + ryRatio * dh,
      w: rwRatio * dw,
      h: rhRatio * dh,
    };
  }

  /** Dessine le highlight Phase D si configuré et dans la fenêtre temporelle. */
  _drawHighlight(ctx, w, h) {
    if (!this.highlight) return;
    const { appearAt = 0.5, holdFor = 1.5, sx, sy, sw, sh } = this.highlight;
    const localT = this.planTime - appearAt;
    if (localT < 0) return;
    // Phase 1: stroke draw progressive 0→1 over 350ms (4 côtés)
    const DRAW_MS = 350;
    const drawProgress = Math.min(1, localT / (DRAW_MS / 1000));
    // Phase 2: hold (full visible)
    // Phase 3: après holdFor + DRAW_MS, fade-out 250ms
    const totalVisible = (DRAW_MS / 1000) + holdFor;
    let alpha = 1;
    if (localT > totalVisible) {
      const fadeT = (localT - totalVisible) / 0.25;
      alpha = Math.max(0, 1 - fadeT);
      if (alpha === 0) return;
    }

    const d = this._mapSourceRectToDisplay({ sx, sy, sw, sh }, w, h);
    // Padding visuel léger autour du mot-clé
    const PAD = 14;
    const rx = d.x - PAD;
    const ry = d.y - PAD;
    const rw = d.w + PAD * 2;
    const rh = d.h + PAD * 2;

    ctx.save();
    ctx.globalAlpha = alpha;
    // Rectangle dessiné progressivement (les 4 côtés en séquence)
    ctx.strokeStyle = '#C9A84C';
    ctx.lineWidth = 3.5;
    ctx.lineCap = 'round';
    ctx.shadowColor = 'rgba(201,168,76,0.5)';
    ctx.shadowBlur = 8;
    const perim = 2 * (rw + rh);
    const drawnLen = perim * drawProgress;
    let remaining = drawnLen;
    ctx.beginPath();
    ctx.moveTo(rx, ry);
    // Top edge
    const seg1 = Math.min(remaining, rw); ctx.lineTo(rx + seg1, ry); remaining -= seg1;
    // Right edge
    if (remaining > 0) { const seg2 = Math.min(remaining, rh); ctx.lineTo(rx + rw, ry + seg2); remaining -= seg2; }
    // Bottom edge
    if (remaining > 0) { const seg3 = Math.min(remaining, rw); ctx.lineTo(rx + rw - seg3, ry + rh); remaining -= seg3; }
    // Left edge
    if (remaining > 0) { const seg4 = Math.min(remaining, rh); ctx.lineTo(rx, ry + rh - seg4); remaining -= seg4; }
    ctx.stroke();
    ctx.restore();
  }

  draw(ctx, w, h) {
    const aw = this.asset.naturalWidth || this.asset.width;
    const ah = this.asset.naturalHeight || this.asset.height;
    let sx = 0, sy = 0, sw = aw, sh = ah;
    if (this.cropRegion) {
      sx = this.cropRegion.sx;
      sy = this.cropRegion.sy;
      sw = this.cropRegion.sw;
      sh = this.cropRegion.sh;
    }
    const { dx, dy, dw, dh } = this.computeKenBurnsRect(w, h, sw, sh);

    // Background noir d'abord pour éviter rendu vide si crop ne couvre pas
    ctx.fillStyle = '#0a0e1c';
    ctx.fillRect(0, 0, w, h);

    ctx.save();
    this.applyColorGrade(ctx);
    ctx.drawImage(this.asset, sx, sy, sw, sh, dx, dy, dw, dh);
    this.resetFilter(ctx);
    ctx.restore();

    // Vignettage
    const grad = ctx.createRadialGradient(
      w / 2, h / 2, Math.min(w, h) * 0.4,
      w / 2, h / 2, Math.max(w, h) * 0.85
    );
    grad.addColorStop(0, 'rgba(0,0,0,0)');
    grad.addColorStop(1, 'rgba(0,0,0,0.55)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Phase D : highlight overlay sur mot-clé (avant les sous-titres)
    this._drawHighlight(ctx, w, h);

    // Sous-titres burned-in
    this.drawSubtitle(ctx, w, h);
  }
}
