/**
 * easing.js — Scene Engine V1
 * Cubic-bezier presets pour Canvas 2D (pas de transition CSS, on calcule).
 * Toutes fonctions reçoivent t ∈ [0,1] et retournent y ∈ [0,1].
 */

export const easings = {
  linear: (t) => t,
  // Calm — fluide, lent, type pédagogique (F1)
  easeOutCalm: (t) => 1 - Math.pow(1 - t, 3),
  easeInOutCalm: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  // Punchy — vif, accent net (F2, F5)
  easeOutPunch: (t) => 1 - Math.pow(1 - t, 4),
  easeBackOut: (t) => {
    const c1 = 1.70158;
    const c3 = c1 + 1;
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
  },
  // Dramatic — accélération forte puis stabilisation (F4, F6, F7)
  easeOutDramatic: (t) => 1 - Math.pow(1 - t, 5),
  easeInExpo: (t) => (t === 0 ? 0 : Math.pow(2, 10 * t - 10)),
  // Bounce — pour shake/impact (F6, F7)
  bounceOut: (t) => {
    const n1 = 7.5625, d1 = 2.75;
    if (t < 1 / d1) return n1 * t * t;
    if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
    if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
    return n1 * (t -= 2.625 / d1) * t + 0.984375;
  },
};

/** Interpolation 1D avec easing */
export function lerp(from, to, t, ease = easings.linear) {
  return from + (to - from) * ease(Math.max(0, Math.min(1, t)));
}

/** Map d'alias style "calm / punch / dramatic" vers une fonction d'easing */
export const easingPresets = {
  calm: easings.easeInOutCalm,
  punch: easings.easeOutPunch,
  dramatic: easings.easeOutDramatic,
  back: easings.easeBackOut,
  bounce: easings.bounceOut,
  linear: easings.linear,
};
