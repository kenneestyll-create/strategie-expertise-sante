/**
 * BackgroundImagePlan.js — Phase A
 *
 * Plan = 1 image fullscreen 9:16 + Ken Burns (zoom + pan) + filtre colorimétrique
 * navy/or + overlay sous-titres burned-in. RIEN d'autre.
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
  }

  draw(ctx, w, h) {
    const { dx, dy, dw, dh } = this.computeKenBurnsRect(
      w, h, this.asset.naturalWidth || this.asset.width, this.asset.naturalHeight || this.asset.height
    );
    // 1) image avec filter colorimétrique
    ctx.save();
    this.applyColorGrade(ctx);
    ctx.drawImage(this.asset, dx, dy, dw, dh);
    this.resetFilter(ctx);
    ctx.restore();

    // 2) Vignettage léger (vraie photo doc style)
    const grad = ctx.createRadialGradient(
      w / 2, h / 2, Math.min(w, h) * 0.4,
      w / 2, h / 2, Math.max(w, h) * 0.85
    );
    grad.addColorStop(0, 'rgba(0,0,0,0)');
    grad.addColorStop(1, 'rgba(0,0,0,0.55)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // 3) Sous-titres burned-in (overlay au-dessus de tout)
    this.drawSubtitle(ctx, w, h);
  }
}
