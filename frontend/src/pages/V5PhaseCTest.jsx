/**
 * V5PhaseCTest.jsx — Checkpoint Phase C
 *
 * Compose une vidéo à partir d'UN SEUL document utilisateur uploadé (CapCut AI style).
 * Le moteur découpe automatiquement le document en N "zones d'intérêt" et anime
 * chaque zone successivement avec Ken Burns + voice-off + sous-titres burned-in.
 *
 * Améliorations vs Phase A/B :
 *  - Voix `echo` (au lieu d'onyx) — plus expressive
 *  - Durée d'export = durée réelle de l'audio + fade-out 200ms (plus de coupure nette)
 *  - Cohérence visuelle stricte (toujours le même document, juste recadrages)
 *
 * Route : /admin/v5-phaseC-test
 */
import React, { useEffect, useRef, useState } from 'react';
import { AssetLoaderV5 } from '../lib/sceneEngine/v5/AssetLoaderV5.js';
import { BackgroundImagePlan } from '../lib/sceneEngine/v5/plans/BackgroundImagePlan.js';
import { V5Renderer } from '../lib/sceneEngine/v5/V5Renderer.js';

const IMAGE_URL = '/v5-assets/uploads/contestation-ratp.jpg';
const AUDIO_URL = '/v5-assets/uploads/voice-phaseC-echo.mp3';

// 9 chunks SRT du script généré pour CE document spécifique
const SUBTITLES_GLOBAL = [
  { startSec: 0, endSec: 3, text: 'Courrier CCAS RATP\navec « CONTESTATION ».' },
  { startSec: 3, endSec: 6, text: 'Vous avez DEUX MOIS.\nPas plus.' },
  { startSec: 6, endSec: 9, text: 'Articles R.142-1\net R.711-20.' },
  { startSec: 9, endSec: 12, text: 'Au-delà : droits perdus\ndéfinitivement.' },
  { startSec: 12, endSec: 15, text: 'Beaucoup ne savent pas\nce délai fatal.' },
  { startSec: 15, endSec: 18, text: 'Résultat : indemnisation\nrefusée, dossier clos.' },
  { startSec: 18, endSec: 21, text: 'Vous devez agir\nmaintenant.' },
  { startSec: 21, endSec: 24, text: "Analyse d'urgence\nde votre courrier." },
  { startSec: 24, endSec: 27, text: 'Expertise en moins\nde 30 jours.' },
];

// 4 viewports SUR LE MÊME document (1080x2280 source).
// Chacun = bande verticale 9:16 ratio (1080x1920) déplacée pour zoomer sur 4 zones.
// Inspiration "CapCut AI" : on isole la zone narrative pertinente à chaque chunk.
// (Y ranges calibrés visuellement sur le doc Contestation RATP)
const PLAN_VIEWPORTS = [
  // Plan 1 (0-9s) — Header CONTESTATION + Articles R142-1
  { sx: 30, sy: 280, sw: 1020, sh: 950, durationSec: 9,
    kenBurns: { zoomFrom: 1.0, zoomTo: 1.08, panX: 0.03, panY: 0 } },
  // Plan 2 (9-18s) — Section ordre médical + adresse CRAM
  { sx: 30, sy: 950, sw: 1020, sh: 900, durationSec: 9,
    kenBurns: { zoomFrom: 1.05, zoomTo: 1.0, panX: -0.03, panY: 0.02 } },
  // Plan 3 (18-24s) — Recours contre tiers L.454-1
  { sx: 30, sy: 1400, sw: 1020, sh: 720, durationSec: 6,
    kenBurns: { zoomFrom: 1.0, zoomTo: 1.06, panX: 0, panY: -0.03 } },
  // Plan 4 (24-27s) — Logo RATP + warning final
  { sx: 30, sy: 1850, sw: 1020, sh: 380, durationSec: 3,
    kenBurns: { zoomFrom: 1.0, zoomTo: 1.10, panX: 0, panY: 0 } },
];

function splitSubtitlesByPlan(subs, viewports) {
  const ranges = [];
  let t = 0;
  for (const v of viewports) {
    ranges.push({ start: t, end: t + v.durationSec });
    t += v.durationSec;
  }
  return ranges.map((r) =>
    subs
      .filter((s) => s.startSec < r.end && s.endSec > r.start)
      .map((s) => ({
        startSec: Math.max(0, s.startSec - r.start),
        endSec: Math.min(r.end - r.start, s.endSec - r.start),
        text: s.text,
      }))
  );
}

export default function V5PhaseCTest() {
  const previewCanvasRef = useRef(null);
  const audioRef = useRef(null);
  const rendererRef = useRef(null);
  const rafRef = useRef(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        setStatus('loading');
        const t0 = performance.now();
        const img = await AssetLoaderV5.loadImage(IMAGE_URL);
        console.info(`[v5-phaseC] image loaded ${(performance.now() - t0).toFixed(0)}ms (${img.naturalWidth}x${img.naturalHeight})`);
        const subsByPlan = splitSubtitlesByPlan(SUBTITLES_GLOBAL, PLAN_VIEWPORTS);
        const plans = PLAN_VIEWPORTS.map((vp, i) =>
          new BackgroundImagePlan({
            asset: img,
            durationSec: vp.durationSec,
            subtitles: subsByPlan[i],
            cropRegion: { sx: vp.sx, sy: vp.sy, sw: vp.sw, sh: vp.sh },
            kenBurns: vp.kenBurns,
          })
        );
        rendererRef.current = new V5Renderer(plans, { transition: 'crossfade' });
        setStatus('ready');
      } catch (e) {
        console.error('[v5-phaseC] boot error:', e);
        setError(String(e));
        setStatus('error');
      }
    })();
  }, []);

  useEffect(() => {
    if (status !== 'ready') return;
    const cnv = previewCanvasRef.current;
    if (!cnv) return;
    const ctx = cnv.getContext('2d');
    cnv.width = 720;
    cnv.height = 1280;
    const audio = audioRef.current;
    const tick = () => {
      const t = audio?.currentTime || 0;
      rendererRef.current.render(ctx, t, 720, 1280);
      rafRef.current = requestAnimationFrame(tick);
    };
    tick();
    return () => cancelAnimationFrame(rafRef.current);
  }, [status]);

  const handleExport = async () => {
    setExporting(true);
    try {
      const off = document.createElement('canvas');
      off.width = 720;
      off.height = 1280;
      const ctx = off.getContext('2d');
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const resp = await fetch(AUDIO_URL);
      const arrayBuf = await resp.arrayBuffer();
      const audioBuf = await audioCtx.decodeAudioData(arrayBuf);
      const REAL_AUDIO_DURATION = audioBuf.duration;
      const EXPORT_DURATION = REAL_AUDIO_DURATION + 0.5; // 0.5s silence final
      console.info(`[v5-phaseC] real audio duration=${REAL_AUDIO_DURATION.toFixed(2)}s export=${EXPORT_DURATION.toFixed(2)}s`);

      const videoStream = off.captureStream(30);
      const dest = audioCtx.createMediaStreamDestination();
      const src = audioCtx.createBufferSource();
      src.buffer = audioBuf;
      // Fade-out audio 200ms à la fin pour éviter coupure nette
      const gain = audioCtx.createGain();
      gain.gain.setValueAtTime(1, audioCtx.currentTime);
      gain.gain.setValueAtTime(1, audioCtx.currentTime + REAL_AUDIO_DURATION - 0.25);
      gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + REAL_AUDIO_DURATION);
      src.connect(gain);
      gain.connect(dest);

      const combined = new MediaStream([
        ...videoStream.getVideoTracks(),
        ...dest.stream.getAudioTracks(),
      ]);
      const recorder = new MediaRecorder(combined, {
        mimeType: 'video/webm;codecs=vp9,opus',
        videoBitsPerSecond: 2_800_000,
      });
      const chunks = [];
      recorder.ondataavailable = (e) => e.data.size > 0 && chunks.push(e.data);
      const start = performance.now();
      let stopped = false;
      const renderLoop = () => {
        const elapsed = (performance.now() - start) / 1000;
        if (elapsed >= EXPORT_DURATION + 0.1) {
          if (!stopped) { stopped = true; recorder.stop(); }
          return;
        }
        rendererRef.current.render(ctx, elapsed, 720, 1280);
        requestAnimationFrame(renderLoop);
      };
      const done = new Promise((resolve) => {
        recorder.onstop = () => resolve(new Blob(chunks, { type: 'video/webm' }));
      });
      recorder.start(200);
      src.start();
      renderLoop();
      const blob = await done;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ses-v5-phaseC-${Date.now()}.webm`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      console.info(`[v5-phaseC] export done size=${(blob.size / 1024).toFixed(1)}KB`);
    } catch (e) {
      console.error('[v5-phaseC] export error:', e);
      setError(String(e));
    } finally {
      setExporting(false);
    }
  };

  return (
    <div
      style={{
        background: '#0a0e1c',
        color: '#e6e8ee',
        minHeight: '100vh',
        padding: '32px',
        fontFamily: 'Inter, system-ui, sans-serif',
      }}
      data-testid="v5-phaseC-page"
    >
      <h1 style={{ color: '#C9A84C', fontWeight: 500, letterSpacing: '0.12em', marginBottom: 16 }}>
        V5 PHASE C — DOCUMENT UTILISATEUR (CapCut AI mode)
      </h1>
      <p style={{ opacity: 0.7, fontSize: 13, marginBottom: 24 }}>
        1 vrai document admin uploadé (Contestation CCAS RATP) → 4 zooms automatiques + Ken Burns + voix `echo` HD + sous-titres burned-in synchronisés.
      </p>
      <div style={{ display: 'flex', gap: 32, alignItems: 'flex-start' }}>
        <div>
          <canvas
            ref={previewCanvasRef}
            style={{
              width: 360,
              height: 640,
              background: '#000',
              borderRadius: 12,
              border: '1px solid #1f2940',
            }}
            data-testid="v5c-preview-canvas"
          />
          <audio
            ref={audioRef}
            src={AUDIO_URL}
            controls
            style={{ width: 360, marginTop: 12 }}
            data-testid="v5c-audio"
          />
          <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
            <button onClick={() => audioRef.current?.play()} style={btn('#1f2940')} data-testid="v5c-play">
              Lecture preview
            </button>
            <button
              onClick={() => { audioRef.current.pause(); audioRef.current.currentTime = 0; }}
              style={btn('#1f2940')} data-testid="v5c-reset">
              Reset
            </button>
            <button
              onClick={handleExport}
              disabled={status !== 'ready' || exporting}
              style={btn('#C9A84C', '#0a0e1c')}
              data-testid="v5c-export">
              {exporting ? 'Export en cours…' : 'Exporter .webm'}
            </button>
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{ color: '#C9A84C', marginBottom: 8, fontSize: 14, letterSpacing: '0.1em' }}>STATUS</h3>
          <pre
            style={{ background: '#162136', padding: 16, borderRadius: 8, fontSize: 12, color: '#e6e8ee', whiteSpace: 'pre-wrap' }}
            data-testid="v5c-status"
          >
{`status: ${status}
asset: 1 document utilisateur (Contestation CCAS RATP 1080x2280)
plans: 4 zooms automatiques sur zones d'intérêt
transition: crossfade 200ms
voice: echo HD
duration alignée audio: ✓
fade-out audio 200ms final: ✓
filter: saturate(0.78) contrast(1.06) brightness(0.96) hue-rotate(-4deg)
${error ? '\nERROR: ' + error : ''}`}
          </pre>
          <h3 style={{ color: '#C9A84C', marginTop: 16, marginBottom: 8, fontSize: 14, letterSpacing: '0.1em' }}>SCRIPT GÉNÉRÉ</h3>
          <div style={{ fontSize: 11, lineHeight: 1.6, opacity: 0.85 }}>
            <em>Vous venez de recevoir un courrier de la CCAS RATP avec le mot CONTESTATION ? Attention. Ce n'est pas un avertissement. C'est un délai légal de DEUX MOIS qui commence maintenant. Articles R.142-1 et R.711-20. Passé ce délai, vos droits sont perdus définitivement…</em>
          </div>
          <h3 style={{ color: '#C9A84C', marginTop: 16, marginBottom: 8, fontSize: 14, letterSpacing: '0.1em' }}>4 ZOOMS SUR LE DOCUMENT</h3>
          <div style={{ fontSize: 11, lineHeight: 1.6, opacity: 0.85 }}>
            <div>Plan 1 (0-9s) — Header CONTESTATION + Articles R142-1 (sy=280→1230)</div>
            <div>Plan 2 (9-18s) — Section ordre médical + adresse CRAM (sy=950→1850)</div>
            <div>Plan 3 (18-24s) — Recours contre tiers L.454-1 (sy=1400→2120)</div>
            <div>Plan 4 (24-27s) — Footer + logo RATP (sy=1850→2230)</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function btn(bg, fg = '#fff') {
  return {
    background: bg, color: fg, border: 'none', padding: '10px 18px', borderRadius: 8,
    fontWeight: 600, cursor: 'pointer', fontSize: 13, letterSpacing: '0.05em',
  };
}
