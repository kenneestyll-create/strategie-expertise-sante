/**
 * BackgroundVideoPlan.js — Phase B checkpoint
 *
 * Plan = 1 vidéo fullscreen 9:16 (HTMLVideoElement joué muted en arrière-plan
 * DOM puis sampled par ctx.drawImage chaque frame) + filtre colorimétrique
 * navy/or + overlay sous-titres burned-in.
 *
 * Garde-fou contrat V5 §3 : asset OBLIGATOIRE (HTMLVideoElement).
 * Garde-fou contrat V5 §1 : pas de ctx.arc / ctx.fillRect géométrique.
 */
import { PlanV5 } from '../PlanV5.js';

export class BackgroundVideoPlan extends PlanV5 {
  constructor(opts) {
    super(opts);
    if (!this.asset || !(this.asset instanceof HTMLVideoElement)) {
      throw new Error(
        'V5_CONSTRAINTS §3: BackgroundVideoPlan requires an HTMLVideoElement asset.'
      );
    }
    // Ken Burns optionnel sur vidéo (zoom léger uniquement, pas de pan pour rester sobre)
    this.kenBurns = opts.kenBurns || { zoomFrom: 1.0, zoomTo: 1.04, panX: 0, panY: 0 };
  }

  draw(ctx, w, h) {
    // 1) Vidéo de fond — drawImage(videoElement, ...) est le natif Canvas 2D
    //    qui sample la frame courante de la vidéo
    const vw = this.asset.videoWidth || 1280;
    const vh = this.asset.videoHeight || 720;
    const { dx, dy, dw, dh } = this.computeKenBurnsRect(w, h, vw, vh);

    ctx.save();
    this.applyColorGrade(ctx);
    try {
      ctx.drawImage(this.asset, dx, dy, dw, dh);
    } catch (e) {
      // Si la vidéo n'est pas encore prête (readyState < 2), on dessine du noir
      ctx.fillStyle = '#0a0e1c';
      ctx.fillRect(0, 0, w, h);
    }
    this.resetFilter(ctx);
    ctx.restore();

    // 2) Vignettage léger (cohérence avec BackgroundImagePlan)
    const grad = ctx.createRadialGradient(
      w / 2, h / 2, Math.min(w, h) * 0.4,
      w / 2, h / 2, Math.max(w, h) * 0.85
    );
    grad.addColorStop(0, 'rgba(0,0,0,0)');
    grad.addColorStop(1, 'rgba(0,0,0,0.55)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // 3) Sous-titres burned-in (au-dessus de tout)
    this.drawSubtitle(ctx, w, h);
  }
}
