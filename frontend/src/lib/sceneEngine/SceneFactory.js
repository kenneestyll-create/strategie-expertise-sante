/**
 * SceneFactory.js — Scene Engine V1
 *
 * Factory centralisée : crée une scene concrète selon scene_type.
 * Sprint 1 : factory vide (registry préparé). Sprint 2-3 enregistrent les scenes.
 *
 * Si scene_type est inconnu ou null → renvoie null → l'appelant fait un
 * fallback vers le renderer V4.2 existant (videoExporter.drawFrame).
 *
 * Usage :
 *   import { SceneFactory } from '@/lib/sceneEngine/SceneFactory';
 *   const scene = SceneFactory.create('stats_focus', props);
 *   if (!scene) { ... fallback V4.2 ... }
 *   else { scene.init(); ... ; scene.draw(ctx); }
 */

import { Camera } from './camera.js';
import { AssetLoader } from './AssetLoader.js';
import { getMotionRule } from './motionRules.js';
import { buildChunksFromAudio } from './timeline.js';

class _SceneFactory {
  constructor() {
    this._registry = new Map(); // scene_type -> ctor
  }

  /** Sprint 2-3 : chaque scene s'enregistre via register() */
  register(sceneType, ctor) {
    this._registry.set(sceneType, ctor);
  }

  /** Liste des scene_types disponibles */
  available() {
    return [...this._registry.keys()];
  }

  /**
   * Crée une instance de scene.
   * @param {string} sceneType - 'stats_focus' | 'alert_urgency' | 'legal_balance' | 'office_admin' | 'testimony_quote'
   * @param {Object} options
   * @param {Object} options.video - pack vidéo (script, hook, cta, storyboard, voice_over...)
   * @param {string} options.format - F1..F7
   * @param {number} options.width - canvas width (720)
   * @param {number} options.height - canvas height (1280)
   * @param {number} options.audioDurationSec - durée TTS réelle (P1.B)
   * @param {AssetLoader} [options.assetLoader] - shared loader (optional)
   * @returns {Scene|null} - null si type inconnu (=> fallback V4.2)
   */
  create(sceneType, options = {}) {
    const Ctor = this._registry.get(sceneType);
    if (!Ctor) return null;

    const motionRule = getMotionRule(options.format);
    const chunks = buildChunksFromAudio(
      options.video?.script || '',
      options.audioDurationSec || 0,
    );
    const camera = new Camera({
      width: options.width || 720,
      height: options.height || 1280,
    });
    const assetLoader = options.assetLoader || new AssetLoader();

    return new Ctor({
      width: options.width || 720,
      height: options.height || 1280,
      motionRule,
      chunks,
      video: options.video || {},
      camera,
      assetLoader,
    });
  }
}

export const SceneFactory = new _SceneFactory();
