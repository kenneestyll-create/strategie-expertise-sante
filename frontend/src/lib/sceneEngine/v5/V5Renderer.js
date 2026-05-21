/**
 * V5Renderer.js — Phase A
 *
 * Orchestrateur de plans : timeline globale calée sur audio TTS, transitions
 * cut/crossfade entre plans, draw du plan actif (+ overlay du plan suivant
 * pendant crossfade).
 *
 * Garde-fou contrat V5 : transitions limitées à 'cut' et 'crossfade' (200ms).
 */

const CROSSFADE_MS = 200;

export class V5Renderer {
  /**
   * @param {PlanV5[]} plans - séquence de plans
   * @param {object} opts - {transition: 'cut'|'crossfade', totalDuration?: number}
   */
  constructor(plans, opts = {}) {
    if (!Array.isArray(plans) || plans.length === 0) {
      throw new Error('V5Renderer requires at least 1 plan.');
    }
    if (plans.length > 8) {
      throw new Error('V5_CONSTRAINTS: hard-cap 8 plans per video.');
    }
    this.plans = plans;
    this.transition = opts.transition || 'cut';
    if (!['cut', 'crossfade'].includes(this.transition)) {
      throw new Error(
        `V5_CONSTRAINTS §transitions: only 'cut' or 'crossfade' allowed, got '${this.transition}'`
      );
    }
    this._buildRanges();
    this.totalDuration = opts.totalDuration || this.ranges[this.ranges.length - 1].end;
  }

  _buildRanges() {
    let t = 0;
    this.ranges = this.plans.map((p) => {
      const start = t;
      const end = t + p.duration;
      t = end;
      return { start, end };
    });
  }

  /** Trouve l'index du plan actif à audioTime (binary search inutile, 8 max). */
  _activeIdx(audioTime) {
    for (let i = 0; i < this.ranges.length; i++) {
      if (audioTime >= this.ranges[i].start && audioTime < this.ranges[i].end) return i;
    }
    return this.ranges.length - 1;
  }

  /**
   * Update tous les plans nécessaires (actif + suivant si crossfade).
   * draw du plan actif + crossfade si applicable.
   */
  render(ctx, audioTime, w, h) {
    const idx = this._activeIdx(audioTime);
    const range = this.ranges[idx];
    const planTime = audioTime - range.start;
    const plan = this.plans[idx];
    plan.update(planTime);

    // Detect crossfade zone : 200ms avant la fin (côté plan actif)
    const crossfadeStart = range.end - CROSSFADE_MS / 1000;
    const inCrossfade =
      this.transition === 'crossfade' &&
      idx < this.plans.length - 1 &&
      audioTime >= crossfadeStart;

    if (inCrossfade) {
      const nextPlan = this.plans[idx + 1];
      const nextRange = this.ranges[idx + 1];
      // Le next plan commence dans CROSSFADE_MS — son temps local est négatif
      // pendant la fin du courant. On l'affiche avec un planTime à 0.
      nextPlan.update(0);
      // Alpha interpolation
      const fadeT = (audioTime - crossfadeStart) / (CROSSFADE_MS / 1000);
      const alphaNext = Math.max(0, Math.min(1, fadeT));
      // 1) plan courant à pleine opacité
      plan.draw(ctx, w, h);
      // 2) plan suivant en overlay avec alpha croissant
      ctx.save();
      ctx.globalAlpha = alphaNext;
      nextPlan.draw(ctx, w, h);
      ctx.restore();
    } else {
      plan.draw(ctx, w, h);
    }
  }
}
