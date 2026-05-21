/**
 * V5PhaseBTest.jsx — Page isolée Phase B checkpoint
 *
 * UNIQUEMENT : 1 vraie vidéo Mixkit (Pexels-like libre) en background +
 * Ken Burns zoom léger + voice-off Onyx + sous-titres burned-in + filtre navy/or
 * + export .webm.
 *
 * Aucune nouvelle classe créée. Aucun motion design ajouté. Aucune UI admin.
 *
 * Route : /admin/v5-phaseB-test
 */
import React, { useEffect, useRef, useState } from 'react';
import { AssetLoaderV5 } from '../lib/sceneEngine/v5/AssetLoaderV5.js';
import { BackgroundVideoPlan } from '../lib/sceneEngine/v5/plans/BackgroundVideoPlan.js';
import { V5Renderer } from '../lib/sceneEngine/v5/V5Renderer.js';

const VIDEO_URL = '/v5-assets/phaseB-bureau.webm';
const AUDIO_URL = '/v5-assets/phaseA-voice.mp3';

// Mêmes chunks SRT que Phase A (cohérence + base comparable)
const SUBTITLES = [
  { startSec: 0, endSec: 4, text: "500€ d'indus CPAM ?\nTrois erreurs vous coûtent." },
  { startSec: 4, endSec: 6, text: "Erreur 1 : changement\nde situation non déclaré." },
  { startSec: 6, endSec: 9, text: "Mariage, emploi, adresse.\nLa CPAM réclame 6 mois après." },
  { startSec: 9, endSec: 12, text: "Erreur 2 : confusion\narrêt maladie vs AT." },
  { startSec: 12, endSec: 15, text: "L'indemnité change tout.\nVérifiez votre courrier." },
  { startSec: 15, endSec: 18, text: "Erreur 3 : justificatif\nmanquant = indus." },
  { startSec: 18, endSec: 21, text: "Vous avez 30 jours\npour contester." },
  { startSec: 21, endSec: 26, text: "Faites vérifier votre dossier\npar un expert." },
];

const PLAN_DURATION = 26; // s — la vidéo Mixkit fait ~19s, on la met en loop

export default function V5PhaseBTest() {
  const previewCanvasRef = useRef(null);
  const audioRef = useRef(null);
  const rendererRef = useRef(null);
  const rafRef = useRef(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [loadMs, setLoadMs] = useState(0);

  useEffect(() => {
    (async () => {
      try {
        setStatus('loading');
        const t0 = performance.now();
        const video = await AssetLoaderV5.loadVideo(VIDEO_URL, { loop: true });
        const elapsed = performance.now() - t0;
        setLoadMs(Math.round(elapsed));
        console.info(`[v5-phaseB] video loaded in ${elapsed.toFixed(0)}ms (videoW=${video.videoWidth} videoH=${video.videoHeight} duration=${video.duration.toFixed(1)}s)`);

        const plan = new BackgroundVideoPlan({
          asset: video,
          durationSec: PLAN_DURATION,
          subtitles: SUBTITLES,
          kenBurns: { zoomFrom: 1.0, zoomTo: 1.05, panX: 0, panY: 0 },
        });
        rendererRef.current = new V5Renderer([plan], { transition: 'cut' });
        setStatus('ready');
      } catch (e) {
        console.error('[v5-phaseB] boot error:', e);
        setError(String(e));
        setStatus('error');
      }
    })();
  }, []);

  // Preview live calé sur l'audio
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
        videoBitsPerSecond: 2_800_000,
      });
      const chunks = [];
      recorder.ondataavailable = (e) => e.data.size > 0 && chunks.push(e.data);

      // Restart the background video from start for clean export
      const bgVid = rendererRef.current.plans[0].asset;
      bgVid.currentTime = 0;
      try { await bgVid.play(); } catch (_) {}

      const start = performance.now();
      let stopped = false;
      const renderLoop = () => {
        const elapsed = (performance.now() - start) / 1000;
        if (elapsed >= PLAN_DURATION + 0.1) {
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
      a.download = `ses-v5-phaseB-${Date.now()}.webm`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      console.info(`[v5-phaseB] export done size=${(blob.size / 1024).toFixed(1)}KB`);
    } catch (e) {
      console.error('[v5-phaseB] export error:', e);
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
      data-testid="v5-phaseB-page"
    >
      <h1 style={{ color: '#C9A84C', fontWeight: 500, letterSpacing: '0.12em', marginBottom: 24 }}>
        V5 PHASE B — CHECKPOINT VIDÉO RÉELLE
      </h1>
      <p style={{ opacity: 0.7, fontSize: 13, marginBottom: 24 }}>
        1 vidéo Mixkit (libre de droits) en background + Ken Burns zoom 1.0→1.05 + voice-off Onyx + sous-titres burned-in + filtre navy/or.
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
            data-testid="v5b-preview-canvas"
          />
          <audio
            ref={audioRef}
            src={AUDIO_URL}
            controls
            style={{ width: 360, marginTop: 12 }}
            data-testid="v5b-audio"
          />
          <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
            <button
              onClick={() => audioRef.current?.play()}
              style={btnStyle('#1f2940')}
              data-testid="v5b-play"
            >
              Lecture preview
            </button>
            <button
              onClick={() => {
                audioRef.current.pause();
                audioRef.current.currentTime = 0;
              }}
              style={btnStyle('#1f2940')}
              data-testid="v5b-reset"
            >
              Reset
            </button>
            <button
              onClick={handleExport}
              disabled={status !== 'ready' || exporting}
              style={btnStyle('#C9A84C', '#0a0e1c')}
              data-testid="v5b-export"
            >
              {exporting ? 'Export en cours…' : 'Exporter .webm'}
            </button>
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{ color: '#C9A84C', marginBottom: 8, fontSize: 14, letterSpacing: '0.1em' }}>
            STATUS PHASE B
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
            data-testid="v5b-status"
          >
{`status: ${status}
asset: 1 vidéo Mixkit MP4 (~6.4MB H.264, ${loadMs}ms loaded)
duration: ${PLAN_DURATION}s
transition: cut (single plan)
filter: saturate(0.78) contrast(1.06) brightness(0.96) hue-rotate(-4deg)
kenBurns: zoom 1.00 → 1.05 (subtle)
audio: Onyx TTS HD MP3 (~770 KB)
${error ? '\nERROR: ' + error : ''}`}
          </pre>
          <h3 style={{ color: '#C9A84C', marginTop: 16, marginBottom: 8, fontSize: 14, letterSpacing: '0.1em' }}>
            COMPARAISON CAPCUT (référence)
          </h3>
          <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 8 }}>
            Critère unique de validation : <em>"Le rendu commence-t-il à ressembler à votre CapCut ?"</em>
          </div>
          <video
            src="/livraison-v5-phaseA/capcut-user-reference.mp4"
            controls
            muted
            playsInline
            style={{ width: 240, borderRadius: 8, border: '1px solid #1f2940' }}
            data-testid="v5b-capcut-ref"
          />
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
