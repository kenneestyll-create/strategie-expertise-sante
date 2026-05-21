/**
 * PlanV5.js — Base class (Phase A minimal)
 *
 * Différent de Scene.js (V1-V4.4 abstrait). Un Plan = 1 mini-séquence avec
 * 1 asset externe + Ken Burns + overlay sous-titres.
 *
 * GARDE-FOU CONTRAT V5 (V5_CONSTRAINTS.md §1) :
 *   - PAS de ctx.arc, ctx.fillRect géométrique, ctx.fillText pour bar charts.
 *   - Autorisé : drawImage, fillText pour subs/titres, filter, globalAlpha.
 *
 * Interface attendue par V5Renderer :
 *   - constructor({asset, durationSec, subtitles, colorGrade, kenBurns})
 *   - update(planTime)  // planTime ∈ [0, durationSec]
 *   - draw(ctx, w, h)
 *   - get duration()
 */

export class PlanV5 {
  constructor({ asset, durationSec, subtitles = [], colorGrade = null, kenBurns = null }) {
    if (this.constructor === PlanV5) {
      throw new Error('PlanV5 is abstract; use a concrete plan class.');
    }
    this.asset = asset;
    this.durationSec = durationSec;
    this.subtitles = subtitles; // array of {startSec, endSec, text} (relative to plan)
    // GARDE-FOU §3 : plans qui requièrent un asset doivent vérifier dans leur init
    this.colorGrade = colorGrade || {
      saturate: 0.78,
      contrast: 1.06,
      brightness: 0.96,
      hueRotate: -4,
    };
    this.kenBurns = kenBurns || { zoomFrom: 1.0, zoomTo: 1.08, panX: 0.03, panY: 0 };
    this.planTime = 0;
  }

  get duration() {
    return this.durationSec;
  }

  /** Appelé par V5Renderer chaque frame, planTime borné [0, durationSec]. */
  update(planTime) {
    this.planTime = Math.max(0, Math.min(this.durationSec, planTime));
  }

  /** À overrider par les classes concrètes. */
  draw(_ctx, _w, _h) {
    throw new Error('PlanV5.draw must be overridden.');
  }

  /** Helper colorimétrique (réutilisé par tous les plans avec asset). */
  applyColorGrade(ctx) {
    const cg = this.colorGrade;
    ctx.filter = `saturate(${cg.saturate}) contrast(${cg.contrast}) brightness(${cg.brightness}) hue-rotate(${cg.hueRotate}deg)`;
  }

  resetFilter(ctx) {
    ctx.filter = 'none';
  }

  /** Helper Ken Burns : retourne {dx, dy, dw, dh} pour drawImage. */
  computeKenBurnsRect(w, h, assetW, assetH) {
    const t = this.durationSec > 0 ? this.planTime / this.durationSec : 0;
    const easeT = 1 - Math.pow(1 - t, 2); // easeOutQuad
    const { zoomFrom, zoomTo, panX, panY } = this.kenBurns;
    const zoom = zoomFrom + (zoomTo - zoomFrom) * easeT;
    // Cover behaviour : on remplit 9:16, on crop la dimension excédentaire.
    const targetRatio = w / h;
    const assetRatio = assetW / assetH;
    let drawW, drawH;
    if (assetRatio > targetRatio) {
      drawH = h * zoom;
      drawW = drawH * assetRatio;
    } else {
      drawW = w * zoom;
      drawH = drawW / assetRatio;
    }
    // Pan progressif (horizontal et vertical)
    const offsetX = (w - drawW) / 2 + panX * w * (easeT - 0.5);
    const offsetY = (h - drawH) / 2 + panY * h * (easeT - 0.5);
    return { dx: offsetX, dy: offsetY, dw: drawW, dh: drawH };
  }

  /** Sous-titre actif pour ce plan à planTime. */
  getCurrentSubtitle() {
    return this.subtitles.find(
      (s) => this.planTime >= s.startSec && this.planTime < s.endSec
    );
  }

  /** Dessine le sous-titre style TikTok burned-in, alignment bas-centre. */
  drawSubtitle(ctx, w, h) {
    const sub = this.getCurrentSubtitle();
    if (!sub || !sub.text) return;
    const lines = sub.text.split('\n').map((l) => l.trim()).filter(Boolean);
    ctx.save();
    ctx.font = '700 38px "Inter", system-ui, -apple-system, sans-serif';
    ctx.textAlign = 'center';
    ctx.lineJoin = 'round';
    const yBase = h * 0.84;
    const lineH = 50;
    const totalH = lines.length * lineH;
    lines.forEach((ln, i) => {
      const y = yBase - totalH / 2 + i * lineH + lineH / 2;
      // shadow (1px black, double) pour lisibilité sur photo
      ctx.shadowColor = 'rgba(0,0,0,0.85)';
      ctx.shadowBlur = 8;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 2;
      ctx.lineWidth = 6;
      ctx.strokeStyle = 'rgba(0,0,0,0.7)';
      ctx.strokeText(ln, w / 2, y);
      ctx.fillStyle = '#ffffff';
      ctx.fillText(ln, w / 2, y);
      // Highlight gold sur chiffres + UPPER (très simple regex)
      const goldRegex = /(\b[A-ZÉÈÀ]{3,}\b|\b\d+[€%]?\b)/g;
      const matches = [...ln.matchAll(goldRegex)];
      if (matches.length > 0) {
        ctx.fillStyle = '#C9A84C';
        const metrics = ctx.measureText(ln);
        const fullW = metrics.width;
        let curX = w / 2 - fullW / 2;
        let i2 = 0;
        for (const seg of ln.split(goldRegex)) {
          const segW = ctx.measureText(seg).width;
          if (goldRegex.test(seg)) {
            ctx.fillStyle = '#C9A84C';
            ctx.fillText(seg, curX + segW / 2, y);
          }
          curX += segW;
          i2++;
        }
      }
    });
    ctx.restore();
  }
}
