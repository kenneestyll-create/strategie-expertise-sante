/**
 * BackgroundImagePlan.js — Phase A + extension Phase C (crop region)
 *
 * Plan = 1 image (fullscreen OU zone croppée 9:16) + Ken Burns + filtre navy/or + sous-titres.
 *
 * cropRegion (optionnel, Phase C) : {sx, sy, sw, sh} en pixels source. Si défini, on dessine
 * uniquement cette zone de l'image au lieu de toute l'image. Permet d'afficher plusieurs
 * "plans cinématiques" sur le MÊME asset uploadé par l'utilisateur (style CapCut AI).
 *
 * Garde-fou contrat V5 §3 : asset OBLIGATOIRE.
 * Garde-fou contrat V5 §1 : pas de ctx.arc / ctx.fillRect géométrique.
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
    // Crop region optionnelle (Phase C : pour zoom multi-zones sur 1 même image)
    this.cropRegion = opts.cropRegion || null;
  }

  draw(ctx, w, h) {
    const aw = this.asset.naturalWidth || this.asset.width;
    const ah = this.asset.naturalHeight || this.asset.height;

    // Si cropRegion défini : on utilise une sous-zone de l'image comme "source virtuelle"
    let sx = 0, sy = 0, sw = aw, sh = ah;
    if (this.cropRegion) {
      sx = this.cropRegion.sx;
      sy = this.cropRegion.sy;
      sw = this.cropRegion.sw;
      sh = this.cropRegion.sh;
    }

    // Ken Burns appliqué SUR cette source virtuelle
    const { dx, dy, dw, dh } = this.computeKenBurnsRect(w, h, sw, sh);

    ctx.save();
    this.applyColorGrade(ctx);
    // 9-args drawImage : (img, sx, sy, sw, sh, dx, dy, dw, dh)
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

    // Sous-titres
    this.drawSubtitle(ctx, w, h);
  }
}
