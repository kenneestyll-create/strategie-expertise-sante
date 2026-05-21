/**
 * motionRules.js — Scene Engine V1
 *
 * 7 profils de "personnalité d'animation" mappés aux formats F1-F7.
 * Chaque rule modifie le comportement des scenes SANS modifier leur structure.
 *
 * Charte S.E.S respectée : navy/or pour fond, accents par format.
 */

export const MOTION_RULES = {
  F1: {
    label: 'pédagogique',
    speed: 0.75,         // multiplicateur : <1 = plus lent
    easing: 'calm',      // 'calm' | 'punch' | 'dramatic' | 'back' | 'bounce'
    intensity: 'low',    // 'low' | 'medium' | 'high'
    accent: '#C9A84C',   // or S.E.S
    camera: { allowShake: false, slowPan: true, zoomRange: [1.0, 1.06] },
    description: 'Calme, fade, slow zoom, lecture sereine',
  },
  F2: {
    label: 'statistique',
    speed: 1.0,
    easing: 'punch',
    intensity: 'medium',
    accent: '#3b82f6',   // bleu lab
    camera: { allowShake: false, slowPan: false, zoomRange: [1.0, 1.10] },
    description: 'Count-up vif, focus chiffres, accent bleu',
  },
  F3: {
    label: 'témoignage',
    speed: 0.85,
    easing: 'calm',
    intensity: 'low',
    accent: '#f59e0b',   // ambre chaleureux
    camera: { allowShake: false, slowPan: true, zoomRange: [1.0, 1.04] },
    description: 'Citation progressive, humain, chaleureux',
  },
  F4: {
    label: 'juridique',
    speed: 0.9,
    easing: 'dramatic',
    intensity: 'medium',
    accent: '#991b1b',   // bordeaux gravité
    camera: { allowShake: false, slowPan: false, zoomRange: [1.0, 1.05] },
    description: 'Balance, gravité, stabilité, bordeaux + or',
  },
  F5: {
    label: 'administratif',
    speed: 1.0,
    easing: 'punch',
    intensity: 'medium',
    accent: '#6366f1',   // indigo dossier
    camera: { allowShake: false, slowPan: true, zoomRange: [1.0, 1.08] },
    description: 'Documents séquentiels, mouvement propre',
  },
  F6: {
    label: 'urgence',
    speed: 1.25,
    easing: 'dramatic',
    intensity: 'high',
    accent: '#dc2626',   // rouge alerte
    camera: { allowShake: true, shakeAmp: 3, shakeDur: 0.15, zoomRange: [1.0, 1.12] },
    description: 'Flash rouge, shake léger, rapide',
  },
  F7: {
    label: 'mix alerte/info',
    speed: 1.15,
    easing: 'punch',
    intensity: 'high',
    accent: '#ea580c',   // orange alerte + info
    camera: { allowShake: true, shakeAmp: 2, shakeDur: 0.12, zoomRange: [1.0, 1.10] },
    description: 'Alerte tempérée, infographique impact',
  },
};

/** Récupère le profil rule pour un format donné, fallback F1 */
export function getMotionRule(format) {
  return MOTION_RULES[format] || MOTION_RULES.F1;
}

/**
 * Applique le multiplicateur de vitesse rule.speed à une durée.
 * Si rule.speed > 1 → animation plus rapide (durée raccourcie).
 */
export function scaleDuration(baseDurationSec, rule) {
  const s = rule?.speed || 1;
  return baseDurationSec / s;
}
