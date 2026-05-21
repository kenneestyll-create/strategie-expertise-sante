/**
 * V5PhaseATest.jsx — Page isolée Phase A
 *
 * Charge 3 photos Pexels locales + voice-over MP3 + SRT chunks hardcodés,
 * compose 3 BackgroundImagePlan en V5Renderer avec crossfade, preview live
 * + bouton export .webm via MediaRecorder.
 *
 * Route : /admin/v5-phaseA-test (admin-protected via AdminDashboard guard).
 */
import React, { useEffect, useRef, useState } from 'react';
import { AssetLoaderV5 } from '../lib/sceneEngine/v5/AssetLoaderV5.js';
import { BackgroundImagePlan } from '../lib/sceneEngine/v5/plans/BackgroundImagePlan.js';
import { V5Renderer } from '../lib/sceneEngine/v5/V5Renderer.js';

const ASSETS = [
  '/v5-assets/plan-01-bureau-portable.jpg',
  '/v5-assets/plan-02-document-grave.jpg',
  '/v5-assets/plan-03-openspace-mains.jpg',
];

const AUDIO_URL = '/v5-assets/phaseA-voice.mp3';

// SRT chunks réels du voice-over (parsés du record F2 stats_focus 18091833).
// On découpe la timeline en 3 plans visuels :
//   Plan 1 : 0-9s  (intro + erreur 1)        → bureau-portable (femme tape laptop, ambiance admin)
//   Plan 2 : 9-18s (erreur 2 + erreur 3)     → document-grave (femme étudie document)
//   Plan 3 : 18-26s (alerte + outro)         → openspace-mains (bureaux open-space)
const PLAN_DURATIONS = [9, 9, 8]; // total = 26s, calé sur audio ~30s

const SUBTITLES_GLOBAL = [
  { startSec: 0, endSec: 4, text: "500€ d'indus CPAM ?\nTrois erreurs vous coûtent." },
  { startSec: 4, endSec: 6, text: "Erreur 1 : changement\nde situation non déclaré." },
  { startSec: 6, endSec: 9, text: "Mariage, emploi, adresse.\nLa CPAM réclame 6 mois après." },
  { startSec: 9, endSec: 12, text: "Erreur 2 : confusion\narrêt maladie vs AT." },
  { startSec: 12, endSec: 15, text: "L'indemnité change tout.\nVérifiez votre courrier." },
  { startSec: 15, endSec: 18, text: "Erreur 3 : justificatif\nmanquant = indus." },
  { startSec: 18, endSec: 21, text: "Vous avez 30 jours\npour contester." },
  { startSec: 21, endSec: 26, text: "Faites vérifier votre dossier\npar un expert." },
];

/** Découpe subtitles globaux en chunks locaux par plan. */
function splitSubtitlesByPlan(subs, durations) {
  const ranges = [];
  let t = 0;
  for (const d of durations) {
    ranges.push({ start: t, end: t + d });
    t += d;
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

export default function V5PhaseATest() {
  const previewCanvasRef = useRef(null);
  const audioRef = useRef(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);
  const rendererRef = useRef(null);
  const rafRef = useRef(null);

  // Boot : charge images + audio
  useEffect(() => {
    (async () => {
      try {
        setStatus('loading');
        const t0 = performance.now();
        const imgs = await AssetLoaderV5.loadImages(ASSETS);
        const loadMs = performance.now() - t0;
        console.info(`[v5-phaseA] images loaded in ${loadMs.toFixed(0)}ms (${imgs.length} assets)`);

        const subsByPlan = splitSubtitlesByPlan(SUBTITLES_GLOBAL, PLAN_DURATIONS);
        const plans = imgs.map(
          (img, i) =>
            new BackgroundImagePlan({
              asset: img,
              durationSec: PLAN_DURATIONS[i],
              subtitles: subsByPlan[i],
              // alternance Ken Burns : pan gauche / pan droite / zoom centré
              kenBurns: [
                { zoomFrom: 1.0, zoomTo: 1.08, panX: 0.04, panY: 0 },
                { zoomFrom: 1.05, zoomTo: 1.0, panX: -0.04, panY: 0 },
                { zoomFrom: 1.0, zoomTo: 1.1, panX: 0, panY: -0.02 },
              ][i],
            })
        );
        rendererRef.current = new V5Renderer(plans, { transition: 'crossfade' });
        setStatus('ready');
      } catch (e) {
        console.error('[v5-phaseA] boot error:', e);
        setError(String(e));
        setStatus('error');
      }
    })();
  }, []);

  // Preview loop : tape sur le temps de l'audio
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
      // Canvas offscreen 720x1280
      const off = document.createElement('canvas');
      off.width = 720;
      off.height = 1280;
      const ctx = off.getContext('2d');

      // Audio via fetch + AudioContext for sync recording
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const resp = await fetch(AUDIO_URL);
      const arrayBuf = await resp.arrayBuffer();
      const audioBuf = await audioCtx.decodeAudioData(arrayBuf);

      // Streams
      const videoStream = off.captureStream(30);
      const dest = audioCtx.createMediaStreamDestination();
      const src = audioCtx.createBufferSource();
      src.buffer = audioBuf;
      src.connect(dest);
      const combined = new MediaStream([
        ...videoStream.getVideoTracks(),
        ...dest.stream.getAudioTracks(),
      ]);
      const recorder = new MediaRecorder(combined, {
        mimeType: 'video/webm;codecs=vp9,opus',
        videoBitsPerSecond: 2_500_000,
      });
      const chunks = [];
      recorder.ondataavailable = (e) => e.data.size > 0 && chunks.push(e.data);
      const total = PLAN_DURATIONS.reduce((a, b) => a + b, 0);
      const start = performance.now();
      let stopped = false;
      const renderLoop = () => {
        const elapsed = (performance.now() - start) / 1000;
        if (elapsed >= total + 0.1) {
          if (!stopped) {
            stopped = true;
            recorder.stop();
          }
          return;
        }
        rendererRef.current.render(ctx, elapsed, 720, 1280);
        requestAnimationFrame(renderLoop);
      };

      const done = new Promise((resolve) => {
        recorder.onstop = () => {
          const blob = new Blob(chunks, { type: 'video/webm' });
          resolve(blob);
        };
      });
      recorder.start(200);
      src.start();
      renderLoop();
      const blob = await done;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ses-v5-phaseA-${Date.now()}.webm`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      console.info(`[v5-phaseA] export done size=${(blob.size / 1024).toFixed(1)}KB`);
    } catch (e) {
      console.error('[v5-phaseA] export error:', e);
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
      data-testid="v5-phaseA-page"
    >
      <h1 style={{ color: '#C9A84C', fontWeight: 500, letterSpacing: '0.12em', marginBottom: 24 }}>
        V5 PHASE A — CHECKPOINT VISUEL
      </h1>
      <p style={{ opacity: 0.7, fontSize: 13, marginBottom: 24 }}>
        3 photos Pexels + Ken Burns + crossfade + voice-off Onyx + sous-titres burned-in. Filtre
        colorimétrique navy/or. Aucune forme géométrique dessinée.
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
            data-testid="v5-preview-canvas"
          />
          <audio
            ref={audioRef}
            src={AUDIO_URL}
            controls
            style={{ width: 360, marginTop: 12 }}
            data-testid="v5-audio"
          />
          <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
            <button
              onClick={() => audioRef.current?.play()}
              style={btnStyle('#1f2940')}
              data-testid="v5-play"
            >
              Lecture preview
            </button>
            <button
              onClick={() => {
                audioRef.current.pause();
                audioRef.current.currentTime = 0;
              }}
              style={btnStyle('#1f2940')}
              data-testid="v5-reset"
            >
              Reset
            </button>
            <button
              onClick={handleExport}
              disabled={status !== 'ready' || exporting}
              style={btnStyle('#C9A84C', '#0a0e1c')}
              data-testid="v5-export"
            >
              {exporting ? 'Export en cours…' : 'Exporter .webm'}
            </button>
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{ color: '#C9A84C', marginBottom: 8, fontSize: 14, letterSpacing: '0.1em' }}>
            STATUS
          </h3>
          <pre
            style={{
              background: '#162136',
              padding: 16,
              borderRadius: 8,
              fontSize: 12,
              color: '#e6e8ee',
              whiteSpace: 'pre-wrap',
            }}
            data-testid="v5-status"
          >
{`status: ${status}
plans: 3 (durations ${PLAN_DURATIONS.join('s + ')}s = ${PLAN_DURATIONS.reduce((a, b) => a + b, 0)}s)
transition: crossfade 200ms
filter: saturate(0.78) contrast(1.06) brightness(0.96) hue-rotate(-4deg)
assets: 3 photos Pexels (~525 KB total)
audio: Onyx TTS HD MP3 (~770 KB)
${error ? '\nERROR: ' + error : ''}`}
          </pre>
          <h3 style={{ color: '#C9A84C', marginTop: 16, marginBottom: 8, fontSize: 14, letterSpacing: '0.1em' }}>
            SOUS-TITRES TIMELINE
          </h3>
          <div style={{ fontSize: 11, lineHeight: 1.6, opacity: 0.85 }}>
            {SUBTITLES_GLOBAL.map((s, i) => (
              <div key={i} data-testid={`v5-sub-${i}`}>
                <span style={{ color: '#C9A84C' }}>{s.startSec}s–{s.endSec}s</span> : {s.text.replace(/\n/g, ' / ')}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function btnStyle(bg, fg = '#fff') {
  return {
    background: bg,
    color: fg,
    border: 'none',
    padding: '10px 18px',
    borderRadius: 8,
    fontWeight: 600,
    cursor: 'pointer',
    fontSize: 13,
    letterSpacing: '0.05em',
  };
}
