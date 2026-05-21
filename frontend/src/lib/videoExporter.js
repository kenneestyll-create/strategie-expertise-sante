/**
 * videoExporter.js — V4.2 + Scene Engine V1 (Sprint 2)
 * Exporte la preview V4.1 en .webm 9:16 720×1280 VP9 client-side.
 *
 * V4.2 : drawFrame() = renderer texte+gradient existant (fallback intact)
 * V4.4 : si video.scene_type est défini et supporté → SceneEngine.render()
 *        sinon → fallback drawFrame V4.2 (zéro régression sur les 9 anciennes vidéos)
 *
 * ZÉRO endpoint backend. ZÉRO touche à V1/V2/V3.
 */

import { SceneFactory } from './sceneEngine/register.js';

export const EXPORT_WIDTH = 720;
export const EXPORT_HEIGHT = 1280;
export const EXPORT_FPS = 30;
export const EXPORT_MAX_DURATION_SEC = 60;
export const GOLD = '#C9A84C';

// 7 gradients identiques à ceux du VideoPreviewPlayer
const GRADIENTS = [
  ['#0f172a', '#1e293b'],
  ['#1a1a2e', '#16213e'],
  ['#2d1b3d', '#1a1a2e'],
  ['#c9a84c', '#8b6f1e'],
  ['#0f172a', '#c9a84c'],
  ['#1e293b', '#475569'],
  ['#422006', '#1a1a2e'],
];

/**
 * Détecte si un mot doit être surligné en or :
 *  - contient au moins un chiffre
 *  - OU est entièrement en MAJUSCULES (≥ 2 lettres, ex : ATTENTION, CPAM)
 */
export function shouldHighlight(word) {
  const stripped = (word || '').replace(/[^A-Za-zÀ-ÿ0-9]/g, '');
  if (!stripped) return false;
  if (/\d/.test(stripped)) return true;
  if (stripped.length >= 2) {
    const hasLetter = /[A-ZÀ-Ÿa-zà-ÿ]/.test(stripped);
    if (hasLetter && stripped === stripped.toUpperCase()) return true;
  }
  return false;
}

/** Choisit le meilleur codec WebM disponible (VP9 préféré, fallback VP8) */
function pickMimeType() {
  const candidates = [
    'video/webm;codecs=vp9,opus',
    'video/webm;codecs=vp9',
    'video/webm;codecs=vp8,opus',
    'video/webm;codecs=vp8',
    'video/webm',
  ];
  for (const m of candidates) {
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(m)) return m;
  }
  return 'video/webm';
}

function drawGradientBg(ctx, idx) {
  const [c1, c2] = GRADIENTS[idx % GRADIENTS.length];
  const grad = ctx.createLinearGradient(0, 0, EXPORT_WIDTH, EXPORT_HEIGHT);
  grad.addColorStop(0, c1);
  grad.addColorStop(1, c2);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, EXPORT_WIDTH, EXPORT_HEIGHT);
}

function drawTopHud(ctx, elapsed, total) {
  ctx.font = '500 22px Inter, system-ui, -apple-system, sans-serif';
  ctx.fillStyle = 'rgba(255,255,255,0.65)';
  ctx.fillText('9:16 · TikTok', 32, 50);
  const chrono = `${Math.floor(elapsed)}s / ${Math.floor(total)}s`;
  const cw = ctx.measureText(chrono).width;
  ctx.fillText(chrono, EXPORT_WIDTH - 32 - cw, 50);
}

function drawBottomVignette(ctx) {
  const vig = ctx.createLinearGradient(0, EXPORT_HEIGHT - 420, 0, EXPORT_HEIGHT);
  vig.addColorStop(0, 'rgba(0,0,0,0)');
  vig.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.fillStyle = vig;
  ctx.fillRect(0, EXPORT_HEIGHT - 420, EXPORT_WIDTH, 420);
}

function drawTimeline(ctx, elapsed, total) {
  const barX = 28;
  const barY = EXPORT_HEIGHT - 28;
  const barW = EXPORT_WIDTH - 56;
  ctx.fillStyle = 'rgba(255,255,255,0.18)';
  ctx.fillRect(barX, barY, barW, 6);
  ctx.fillStyle = GOLD;
  ctx.fillRect(barX, barY, barW * Math.min(1, elapsed / total), 6);
}

/** Wrap a single text into lines fitting maxWidth. Returns string[]. */
function wrapLines(ctx, text, maxWidth) {
  const words = (text || '').split(/\s+/).filter(Boolean);
  const lines = [];
  let current = '';
  for (const w of words) {
    const test = current ? `${current} ${w}` : w;
    if (ctx.measureText(test).width > maxWidth && current) {
      lines.push(current);
      current = w;
    } else {
      current = test;
    }
  }
  if (current) lines.push(current);
  return lines;
}

/** Texte centré multi-lignes avec wrap, fill blanc */
function drawCenteredText(ctx, text, centerY, fontSize, weight = 'bold') {
  ctx.font = `${weight} ${fontSize}px Inter, system-ui, -apple-system, sans-serif`;
  ctx.fillStyle = '#ffffff';
  const maxWidth = EXPORT_WIDTH - 96;
  const lines = wrapLines(ctx, text, maxWidth);
  const lineHeight = fontSize * 1.2;
  const total = lines.length * lineHeight;
  const startY = centerY - total / 2 + fontSize;
  // Shadow for legibility
  ctx.shadowColor = 'rgba(0,0,0,0.5)';
  ctx.shadowBlur = 12;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const w = ctx.measureText(line).width;
    ctx.fillText(line, (EXPORT_WIDTH - w) / 2, startY + i * lineHeight);
  }
  ctx.shadowBlur = 0;
}

function drawLabel(ctx, label, color = 'rgba(255,255,255,0.7)') {
  ctx.font = '600 18px Inter, system-ui, sans-serif';
  ctx.fillStyle = color;
  const w = ctx.measureText(label).width;
  ctx.fillText(label, (EXPORT_WIDTH - w) / 2, 220);
}

function drawSceneTag(ctx, tag) {
  ctx.font = '600 16px Inter, system-ui, sans-serif';
  const padding = 14;
  const w = ctx.measureText(tag).width + padding * 2;
  const x = 36;
  const y = 100;
  ctx.fillStyle = 'rgba(255,255,255,0.12)';
  // rounded rect
  const r = 14;
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + 28 - r);
  ctx.quadraticCurveTo(x + w, y + 28, x + w - r, y + 28);
  ctx.lineTo(x + r, y + 28);
  ctx.quadraticCurveTo(x, y + 28, x, y + 28 - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
  ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,0.85)';
  ctx.fillText(tag, x + padding, y + 20);
}

/**
 * Caption burned-in mode D1 : phrase complète par scène, centrée bas,
 * fond noir translucide, highlights or sur MAJUSCULES et chiffres.
 */
function drawBurnedCaption(ctx, text) {
  if (!text) return;
  const fontSize = 32;
  const lineHeight = fontSize * 1.32;
  const maxWidth = EXPORT_WIDTH - 96;
  const padding = 14;

  ctx.font = `bold ${fontSize}px Inter, system-ui, sans-serif`;
  const lines = wrapLines(ctx, text, maxWidth).slice(0, 3); // 3 lignes max
  const totalH = lines.length * lineHeight;
  const startY = EXPORT_HEIGHT - 120 - totalH;

  // Background boxes per line
  for (let i = 0; i < lines.length; i++) {
    const w = ctx.measureText(lines[i]).width;
    const x = (EXPORT_WIDTH - w) / 2;
    const y = startY + i * lineHeight;
    ctx.fillStyle = 'rgba(0,0,0,0.72)';
    const boxX = x - padding;
    const boxY = y - fontSize + 4;
    const boxW = w + padding * 2;
    const boxH = lineHeight - 6;
    const r = 8;
    ctx.beginPath();
    ctx.moveTo(boxX + r, boxY);
    ctx.lineTo(boxX + boxW - r, boxY);
    ctx.quadraticCurveTo(boxX + boxW, boxY, boxX + boxW, boxY + r);
    ctx.lineTo(boxX + boxW, boxY + boxH - r);
    ctx.quadraticCurveTo(boxX + boxW, boxY + boxH, boxX + boxW - r, boxY + boxH);
    ctx.lineTo(boxX + r, boxY + boxH);
    ctx.quadraticCurveTo(boxX, boxY + boxH, boxX, boxY + boxH - r);
    ctx.lineTo(boxX, boxY + r);
    ctx.quadraticCurveTo(boxX, boxY, boxX + r, boxY);
    ctx.closePath();
    ctx.fill();
  }

  // Text per word with highlight
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const tokens = line.split(/(\s+)/);
    const totalWidth = tokens.reduce((sum, t) => sum + ctx.measureText(t).width, 0);
    let x = (EXPORT_WIDTH - totalWidth) / 2;
    const y = startY + i * lineHeight;
    for (const t of tokens) {
      const ww = ctx.measureText(t).width;
      const isHL = shouldHighlight(t);
      ctx.fillStyle = isHL ? GOLD : '#ffffff';
      ctx.fillText(t, x, y);
      x += ww;
    }
  }
}

/** Determine current scene based on elapsed time */
function getCurrentScene(scenes, elapsed) {
  let acc = 0;
  for (let i = 0; i < scenes.length; i++) {
    const next = acc + scenes[i].duration;
    if (elapsed < next) return { scene: scenes[i], idx: i, sceneStart: acc };
    acc = next;
  }
  const last = scenes[scenes.length - 1];
  return { scene: last, idx: scenes.length - 1, sceneStart: acc - (last?.duration || 0) };
}

function drawFrame(ctx, scenes, elapsed, totalDuration) {
  const { scene, idx } = getCurrentScene(scenes, elapsed);
  drawGradientBg(ctx, idx);
  drawBottomVignette(ctx);
  drawTopHud(ctx, elapsed, totalDuration);

  if (!scene) return;

  if (scene.kind === 'hook') {
    drawLabel(ctx, 'HOOK');
    drawCenteredText(ctx, scene.text || '', EXPORT_HEIGHT * 0.42, 56);
  } else if (scene.kind === 'cta') {
    drawLabel(ctx, 'CTA', GOLD);
    drawCenteredText(ctx, scene.text || '', EXPORT_HEIGHT * 0.4, 48);
    if (scene.url) {
      ctx.font = '500 20px ui-monospace, Menlo, monospace';
      const u = scene.url;
      const uw = ctx.measureText(u).width;
      ctx.fillStyle = GOLD;
      ctx.fillText(u, (EXPORT_WIDTH - uw) / 2, EXPORT_HEIGHT * 0.55);
    }
  } else {
    drawSceneTag(ctx, `PLAN ${scene.plan || idx + 1} · ${(scene.type || 'face-cam').toUpperCase()}`);
    drawCenteredText(ctx, scene.text || '', EXPORT_HEIGHT * 0.42, 42);
  }

  // Captions burned-in (sauf sur la scène CTA pour ne pas dupliquer le texte)
  if (scene.kind !== 'cta') {
    drawBurnedCaption(ctx, scene.text || '');
  }

  drawTimeline(ctx, elapsed, totalDuration);
}

/**
 * Export d'une vidéo .webm 9:16.
 *
 * V4.2 mode : passe `scenes` + `voiceOverBase64` → drawFrame V4.2.
 * V4.4 mode : passe en plus `video` (qui contient scene_type, format_used, script)
 *             + `audioDurationSec` (durée réelle du MP3) →
 *             si scene_type supporté par SceneFactory, on bascule sur Scene Engine.
 *             Sinon fallback automatique drawFrame V4.2.
 *
 * @param {Object} params
 * @param {Array}  params.scenes - liste V4.2 {kind, text, duration, ...}
 * @param {string} params.voiceOverBase64 - MP3 base64 (sans préfixe data:)
 * @param {Function} params.onProgress - (pct 0-100) => void
 * @param {Object} [params.video] - V4.4 : pack vidéo complet (scene_type, format_used, script, hook_variants, cta, voice_over)
 * @param {number} [params.audioDurationSec] - V4.4 : durée TTS réelle (sinon = somme scenes.duration)
 * @returns {Promise<Blob>}
 */
export async function exportVideoAsWebm({ scenes, voiceOverBase64, onProgress, video, audioDurationSec }) {
  if (!Array.isArray(scenes) || scenes.length === 0) {
    throw new Error('Scenes vides — preview V4.1 absente.');
  }
  if (!voiceOverBase64) {
    throw new Error('Voice-over absente — générez d\'abord la voix-off (V4.1).');
  }
  if (typeof MediaRecorder === 'undefined') {
    throw new Error('MediaRecorder non supporté dans ce navigateur (utilisez Chrome/Edge/Firefox desktop).');
  }

  const totalDuration = Math.min(
    EXPORT_MAX_DURATION_SEC,
    scenes.reduce((s, sc) => s + (sc.duration || 0), 0),
  );

  // V4.4 — Tentative de bascule Scene Engine (si video.scene_type fourni et supporté)
  const sceneType = video?.scene_type;
  const format = video?.format_used;
  const sceneEngine = sceneType
    ? SceneFactory.create(sceneType, {
        video,
        format,
        width: EXPORT_WIDTH,
        height: EXPORT_HEIGHT,
        audioDurationSec: audioDurationSec || totalDuration,
      })
    : null;
  if (sceneEngine) sceneEngine.init();
  const useSceneEngine = Boolean(sceneEngine);

  // Canvas offscreen
  const canvas = document.createElement('canvas');
  canvas.width = EXPORT_WIDTH;
  canvas.height = EXPORT_HEIGHT;
  const ctx = canvas.getContext('2d');
  // First frame pre-render
  if (useSceneEngine) {
    sceneEngine.update(0, 0);
    sceneEngine.draw(ctx);
  } else {
    drawFrame(ctx, scenes, 0, totalDuration);
  }

  const videoStream = canvas.captureStream(EXPORT_FPS);

  // Audio pipeline
  const audioEl = new Audio(`data:audio/mp3;base64,${voiceOverBase64}`);
  audioEl.crossOrigin = 'anonymous';
  audioEl.preload = 'auto';
  await new Promise((resolve, reject) => {
    audioEl.addEventListener('canplaythrough', () => resolve(), { once: true });
    audioEl.addEventListener('error', () => reject(new Error('Chargement audio voice-over échoué')), { once: true });
    audioEl.load();
  });

  const AudioCtor = window.AudioContext || window.webkitAudioContext;
  const audioCtx = new AudioCtor();
  const srcNode = audioCtx.createMediaElementSource(audioEl);
  const destNode = audioCtx.createMediaStreamDestination();
  srcNode.connect(destNode);
  // (Pas de connect(destination) → silencieux pendant l'export, pas d'écho)

  const mixedStream = new MediaStream([
    ...videoStream.getVideoTracks(),
    ...destNode.stream.getAudioTracks(),
  ]);

  const mimeType = pickMimeType();
  const recorder = new MediaRecorder(mixedStream, {
    mimeType,
    videoBitsPerSecond: 2_500_000,
    audioBitsPerSecond: 128_000,
  });

  const chunks = [];
  recorder.ondataavailable = (e) => { if (e.data && e.data.size > 0) chunks.push(e.data); };

  return await new Promise((resolve, reject) => {
    let stopped = false;
    let rafHandle = null;

    const cleanup = () => {
      if (rafHandle) cancelAnimationFrame(rafHandle);
      try { audioCtx.close(); } catch (_) { /* ignore */ }
      try { videoStream.getTracks().forEach(t => t.stop()); } catch (_) { /* ignore */ }
    };

    recorder.onstop = () => {
      stopped = true;
      cleanup();
      const blob = new Blob(chunks, { type: mimeType });
      resolve(blob);
    };
    recorder.onerror = (e) => {
      cleanup();
      reject(e.error || new Error('MediaRecorder error'));
    };

    try {
      recorder.start(200); // collect chunks every 200ms
      audioEl.play().catch(() => { /* silent ok */ });
    } catch (err) {
      cleanup();
      reject(err);
      return;
    }

    const startTs = performance.now();
    const tick = () => {
      if (stopped) return;
      const elapsed = (performance.now() - startTs) / 1000;
      if (elapsed >= totalDuration) {
        // Render last frame at exact end
        if (useSceneEngine) {
          sceneEngine.update(0, totalDuration);
          sceneEngine.draw(ctx);
        } else {
          drawFrame(ctx, scenes, totalDuration, totalDuration);
        }
        if (onProgress) { try { onProgress(100); } catch (_) {} }
        try { recorder.stop(); } catch (_) { /* already stopping */ }
        return;
      }
      if (useSceneEngine) {
        sceneEngine.update(0, elapsed);
        sceneEngine.draw(ctx);
      } else {
        drawFrame(ctx, scenes, elapsed, totalDuration);
      }
      if (onProgress) {
        try { onProgress(Math.min(99, (elapsed / totalDuration) * 100)); } catch (_) {}
      }
      rafHandle = requestAnimationFrame(tick);
    };
    rafHandle = requestAnimationFrame(tick);
  });
}

/** Helper download a Blob to disk */
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}


/* ────────────────────────────────────────────────────────────────────────
 * V4.4 — Shared renderer (preview ↔ export même code)
 *
 * Crée et conserve une instance de SceneEngine pour une vidéo donnée.
 * Utilisé par VideoPreviewPlayer pour AFFICHER en temps réel le même
 * rendu que celui qui sera exporté.
 * ──────────────────────────────────────────────────────────────────────── */

/**
 * @param {Object} video - pack vidéo (avec scene_type, format_used, script, voice_over)
 * @param {number} audioDurationSec
 * @returns {Object|null} scene engine instance (avec .update(0, audioTime), .draw(ctx)) ou null si fallback
 */
export function buildSceneEngineFor(video, audioDurationSec) {
  const sceneType = video?.scene_type;
  if (!sceneType) return null;
  const engine = SceneFactory.create(sceneType, {
    video,
    format: video?.format_used,
    width: EXPORT_WIDTH,
    height: EXPORT_HEIGHT,
    audioDurationSec: audioDurationSec || 1,
  });
  if (engine) engine.init();
  return engine;
}

/**
 * Dessine une frame sur un canvas (preview ou export).
 * Si engine != null → Scene Engine, sinon → drawFrame V4.2.
 */
export function renderSceneFrame(ctx, engine, scenes, audioTime, totalDuration) {
  if (engine) {
    engine.update(0, audioTime);
    engine.draw(ctx);
  } else {
    drawFrame(ctx, scenes, audioTime, totalDuration);
  }
}
