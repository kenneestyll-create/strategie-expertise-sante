/**
 * VideoPreviewPlayer — V4.1
 * Lecteur 9:16 TikTok-style pour previews de Video Factory.
 *  - Gradients minimalistes par scène (B1)
 *  - Voix-off OpenAI TTS via base64 audio (A2)
 *  - Hook intro + scènes storyboard + sous-titres simulés + CTA outro
 *  - Play/Pause + timeline + scrub
 *  - 100% additif : ne touche pas Video Factory V1/V2/V3
 */
import { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Play, Pause, RotateCcw, Mic, Loader2, VolumeX, Volume2, Download, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';
import { exportVideoAsWebm, downloadBlob, EXPORT_MAX_DURATION_SEC } from '@/lib/videoExporter';

// 7 gradients minimalistes (cycliques selon format / index scène)
const GRADIENTS = [
  'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',       // navy deep
  'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',                     // ses navy
  'linear-gradient(135deg, #2d1b3d 0%, #1a1a2e 100%)',                     // purple muted
  'linear-gradient(135deg, #c9a84c 0%, #8b6f1e 100%)',                     // ses gold
  'linear-gradient(135deg, #0f172a 0%, #c9a84c 100%)',                     // dark→gold
  'linear-gradient(135deg, #1e293b 0%, #475569 100%)',                     // slate
  'linear-gradient(135deg, #422006 0%, #1a1a2e 100%)',                     // amber→navy
];

const VOICES = [
  { value: 'onyx',   label: 'Onyx — grave, autoritaire (FR)' },
  { value: 'sage',   label: 'Sage — sage, mesurée' },
  { value: 'alloy',  label: 'Alloy — neutre, équilibrée' },
  { value: 'nova',   label: 'Nova — énergique' },
  { value: 'coral',  label: 'Coral — chaleureuse' },
];

const SCENE_TARGET_SEC = 5; // durée par défaut si aucune donnée

const splitScriptToScenes = (script, storyboardLen) => {
  if (!script) return [];
  const sentences = script.split(/(?<=[.!?])\s+/).filter(Boolean);
  if (sentences.length === 0) return [script];
  if (sentences.length <= storyboardLen) return sentences;
  // Regroup sentences in N chunks
  const N = Math.max(2, Math.min(storyboardLen || 5, 6));
  const chunkSize = Math.ceil(sentences.length / N);
  const chunks = [];
  for (let i = 0; i < sentences.length; i += chunkSize) {
    chunks.push(sentences.slice(i, i + chunkSize).join(' '));
  }
  return chunks;
};

export const VideoPreviewPlayer = ({ video, runId, videoIdx, onVoiceOverGenerated, generateVoiceOver }) => {
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [voice, setVoice] = useState('onyx');
  const [generating, setGenerating] = useState(false);
  const [muted, setMuted] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportPct, setExportPct] = useState(0);
  const audioRef = useRef(null);
  const rafRef = useRef(null);
  const startTsRef = useRef(0);
  const offsetRef = useRef(0); // seconds when paused, to resume

  // ── Build scene list ──
  const hookText = (video.hook_variants && video.hook_variants[0]) || '';
  const ctaText = video?.cta?.text || video?.cta_text || 'Découvrez votre situation';
  const ctaUrl = video?.cta?.url_ready || video?.cta_url || '';
  const storyboard = video.storyboard || [];
  const scriptChunks = useMemo(
    () => splitScriptToScenes(video.script || '', storyboard.length || 5),
    [video.script, storyboard.length],
  );

  // Compose timeline : intro (hook) + scenes storyboard + outro CTA
  const scenes = useMemo(() => {
    const list = [];
    // Intro : hook
    if (hookText) list.push({ kind: 'hook', text: hookText, duration: 3 });
    // Scenes from storyboard with script chunks overlaid
    const usedDurations = storyboard.map(s => Number(s.duree_sec) || SCENE_TARGET_SEC);
    storyboard.forEach((s, i) => {
      list.push({
        kind: 'scene',
        type: s.type || 'face-cam',
        plan: s.plan || i + 1,
        description: s.description || '',
        ambiance: s.ambiance || '',
        text: scriptChunks[i] || s.description || '',
        duration: usedDurations[i] || SCENE_TARGET_SEC,
      });
    });
    // If no storyboard, fallback to script chunks alone
    if (storyboard.length === 0) {
      scriptChunks.forEach((c, i) => {
        list.push({ kind: 'scene', type: 'texte', plan: i + 1, description: '', text: c, duration: SCENE_TARGET_SEC });
      });
    }
    // Outro CTA
    list.push({ kind: 'cta', text: ctaText, url: ctaUrl, duration: 3 });
    return list;
  }, [hookText, storyboard, scriptChunks, ctaText, ctaUrl]);

  const totalDuration = useMemo(() => scenes.reduce((s, sc) => s + sc.duration, 0), [scenes]);
  const audioBase64 = video?.voice_over?.audio_base64 || null;
  const hasAudio = Boolean(audioBase64);

  // ── Determine current scene from currentTime ──
  const currentScene = useMemo(() => {
    let acc = 0;
    for (let i = 0; i < scenes.length; i++) {
      const next = acc + scenes[i].duration;
      if (currentTime < next) return { idx: i, scene: scenes[i], sceneStart: acc };
      acc = next;
    }
    return { idx: scenes.length - 1, scene: scenes[scenes.length - 1] || null, sceneStart: acc - (scenes[scenes.length - 1]?.duration || 0) };
  }, [currentTime, scenes]);

  // ── RAF loop for time advancement (when no audio or audio not playing) ──
  const tick = useCallback(() => {
    const now = performance.now() / 1000;
    const t = offsetRef.current + (now - startTsRef.current);
    if (t >= totalDuration) {
      setCurrentTime(totalDuration);
      setPlaying(false);
      offsetRef.current = 0;
      return;
    }
    setCurrentTime(t);
    rafRef.current = requestAnimationFrame(tick);
  }, [totalDuration]);

  useEffect(() => {
    if (playing) {
      startTsRef.current = performance.now() / 1000;
      rafRef.current = requestAnimationFrame(tick);
      if (audioRef.current && hasAudio) {
        audioRef.current.currentTime = offsetRef.current;
        audioRef.current.muted = muted;
        audioRef.current.play().catch(() => {});
      }
    } else {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      offsetRef.current = currentTime;
      if (audioRef.current) audioRef.current.pause();
    }
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playing, tick, hasAudio]);

  // Sync mute live
  useEffect(() => {
    if (audioRef.current) audioRef.current.muted = muted;
  }, [muted]);

  const handlePlayPause = () => {
    if (currentTime >= totalDuration) {
      // restart from 0
      offsetRef.current = 0;
      setCurrentTime(0);
    }
    setPlaying(p => !p);
  };

  const handleReset = () => {
    setPlaying(false);
    offsetRef.current = 0;
    setCurrentTime(0);
    if (audioRef.current) audioRef.current.currentTime = 0;
  };

  const handleGenerateVoice = async () => {
    setGenerating(true);
    try {
      const data = await generateVoiceOver({ runId, videoIdx, voice });
      onVoiceOverGenerated?.(videoIdx, data?.voice_over || null);
      toast.success('Voix off générée');
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Génération voix off échouée');
    } finally {
      setGenerating(false);
    }
  };

  // ── V4.2 — Export .webm ──
  const handleExport = async () => {
    if (!hasAudio) {
      toast.error('Générez d\'abord la voix off (V4.1).');
      return;
    }
    setExporting(true);
    setExportPct(0);
    // Stop preview playback during export to free AudioContext
    setPlaying(false);
    if (totalDuration > EXPORT_MAX_DURATION_SEC) {
      toast.warning(`Vidéo > ${EXPORT_MAX_DURATION_SEC}s : tronquée à ${EXPORT_MAX_DURATION_SEC}s à l'export.`);
    }
    try {
      const blob = await exportVideoAsWebm({
        scenes,
        voiceOverBase64: audioBase64,
        onProgress: (pct) => setExportPct(pct),
      });
      const fmt = (video.format_used || `v${videoIdx + 1}`).toLowerCase();
      const stamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      downloadBlob(blob, `ses-video-${fmt}-${stamp}.webm`);
      toast.success(`Vidéo exportée (${(blob.size / 1024 / 1024).toFixed(1)} Mo)`);
    } catch (e) {
      toast.error(e?.message || 'Export vidéo échoué');
    } finally {
      setExporting(false);
      setExportPct(0);
    }
  };

  // ── Visuals ──
  const sceneBgIdx = Math.min(currentScene.idx, GRADIENTS.length - 1);
  const fmt = (s) => `${Math.floor(s)}s`;
  const progressPct = totalDuration ? Math.min(100, (currentTime / totalDuration) * 100) : 0;

  return (
    <div className="flex flex-col items-center gap-4" data-testid={`video-preview-${videoIdx}`}>
      {/* 9:16 Phone frame */}
      <div
        className="relative w-full max-w-[320px] aspect-[9/16] rounded-[28px] overflow-hidden shadow-2xl border-[8px] border-[#0a0a0a]"
        style={{ background: GRADIENTS[sceneBgIdx] }}
        data-testid="preview-stage"
      >
        {/* Notch */}
        <div className="absolute top-2 left-1/2 -translate-x-1/2 w-20 h-5 bg-black rounded-full z-30" aria-hidden="true" />

        {/* Top HUD : platform + duration */}
        <div className="absolute top-3 left-3 right-3 flex items-center justify-between z-20 text-white/80 text-[10px] tracking-wider font-medium">
          <span className="px-2 py-0.5 rounded-full bg-black/40 backdrop-blur-sm">9:16 · TikTok</span>
          <span className="px-2 py-0.5 rounded-full bg-black/40 backdrop-blur-sm font-mono">
            {fmt(currentTime)} / {fmt(totalDuration)}
          </span>
        </div>

        {/* Subtle vignette */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/0 via-black/0 to-black/50 pointer-events-none" />

        {/* Scene content */}
        {currentScene.scene && (
          <div key={currentScene.idx} className="absolute inset-0 flex flex-col justify-center px-6 z-10 animate-fade-in">
            {currentScene.scene.kind === 'hook' && (
              <div className="text-center">
                <div className="text-[10px] uppercase tracking-[0.3em] text-white/60 mb-3">Hook</div>
                <p className="text-white text-2xl font-bold leading-tight drop-shadow-lg">
                  {currentScene.scene.text}
                </p>
              </div>
            )}
            {currentScene.scene.kind === 'scene' && (
              <div>
                <div className="absolute top-12 left-4 flex items-center gap-1.5 z-20">
                  <span className="text-[9px] uppercase tracking-wider text-white/70 px-2 py-0.5 rounded-full bg-white/10 backdrop-blur-sm border border-white/20">
                    Plan {currentScene.scene.plan} · {currentScene.scene.type}
                  </span>
                </div>
                <p className="text-white text-lg font-semibold leading-snug text-center drop-shadow-lg">
                  {currentScene.scene.text}
                </p>
                {currentScene.scene.ambiance && (
                  <p className="text-white/50 text-[10px] italic text-center mt-2">{currentScene.scene.ambiance}</p>
                )}
              </div>
            )}
            {currentScene.scene.kind === 'cta' && (
              <div className="text-center">
                <div className="text-[10px] uppercase tracking-[0.3em] text-[#C9A84C] mb-3">CTA</div>
                <p className="text-white text-xl font-bold leading-tight mb-2 drop-shadow-lg">
                  {currentScene.scene.text}
                </p>
                {currentScene.scene.url && (
                  <p className="text-[#C9A84C] text-[10px] font-mono break-all">{currentScene.scene.url}</p>
                )}
              </div>
            )}
          </div>
        )}

        {/* Simulated captions (bottom) */}
        {currentScene.scene && currentScene.scene.kind !== 'cta' && (
          <div className="absolute bottom-12 left-4 right-4 z-20">
            <p className="text-white text-[13px] font-semibold text-center bg-black/55 rounded-md px-2 py-1.5 leading-snug backdrop-blur-sm">
              {(currentScene.scene.text || '').slice(0, 90)}
              {(currentScene.scene.text || '').length > 90 ? '…' : ''}
            </p>
          </div>
        )}

        {/* Timeline */}
        <div className="absolute bottom-3 left-3 right-3 z-20">
          <div className="h-1 rounded-full bg-white/15 overflow-hidden">
            <div
              className="h-full bg-[#C9A84C] transition-[width] duration-100 ease-linear"
              style={{ width: `${progressPct}%` }}
              data-testid="preview-progress"
            />
          </div>
        </div>

        {/* Hidden audio element for voice-off sync */}
        {hasAudio && (
          <audio
            ref={audioRef}
            src={`data:audio/mp3;base64,${audioBase64}`}
            preload="auto"
            onEnded={() => { /* let RAF finish the visual timer */ }}
            data-testid="preview-audio"
          />
        )}
      </div>

      {/* Controls */}
      <div className="w-full max-w-[360px] flex items-center justify-center gap-2">
        <Button
          size="sm"
          onClick={handlePlayPause}
          className="bg-[#1a1a2e] hover:bg-[#2a2a3e] text-white gap-1.5"
          data-testid="preview-play-pause"
        >
          {playing ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          {playing ? 'Pause' : (currentTime > 0 && currentTime < totalDuration ? 'Reprendre' : 'Lecture')}
        </Button>
        <Button size="sm" variant="outline" onClick={handleReset} data-testid="preview-reset">
          <RotateCcw className="w-4 h-4" />
        </Button>
        {hasAudio && (
          <Button size="sm" variant="ghost" onClick={() => setMuted(m => !m)} data-testid="preview-mute">
            {muted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </Button>
        )}
      </div>

      {/* Voice-over generator */}
      <div className="w-full max-w-[360px] rounded-lg border border-border/60 p-3 bg-muted/30 space-y-2">
        <div className="flex items-center gap-2">
          <Mic className="w-4 h-4 text-[#C9A84C]" />
          <span className="text-xs font-semibold uppercase tracking-wider text-foreground/80">Voix off</span>
          {hasAudio && (
            <Badge variant="outline" className="text-[10px]" data-testid="voice-over-status">
              ✓ {video.voice_over?.voice || 'générée'}
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Select value={voice} onValueChange={setVoice}>
            <SelectTrigger className="h-8 text-xs flex-1" data-testid="preview-voice-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {VOICES.map(v => (
                <SelectItem key={v.value} value={v.value} className="text-xs">{v.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            size="sm"
            onClick={handleGenerateVoice}
            disabled={generating}
            className="bg-[#C9A84C] hover:bg-[#b59440] text-[#1a1a2e] font-semibold gap-1.5"
            data-testid="preview-generate-voice"
          >
            {generating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Mic className="w-3.5 h-3.5" />}
            {hasAudio ? 'Régénérer' : 'Générer voix off'}
          </Button>
        </div>
        <p className="text-[10px] text-muted-foreground leading-relaxed">
          OpenAI TTS HD · synchronisée à la lecture. Coût ~0,003 €/vidéo.
        </p>
      </div>

      {/* V4.2 — Export vidéo finale (.webm 9:16, sous-titres burned-in, audio synchronisé) */}
      <div className="w-full max-w-[360px] rounded-lg border border-border/60 p-3 bg-muted/30 space-y-2" data-testid="export-section">
        <div className="flex items-center gap-2">
          <Download className="w-4 h-4 text-[#C9A84C]" />
          <span className="text-xs font-semibold uppercase tracking-wider text-foreground/80">Export vidéo finale</span>
          <Badge variant="outline" className="text-[10px] font-normal">V4.2</Badge>
        </div>

        {totalDuration > EXPORT_MAX_DURATION_SEC && (
          <div className="flex items-start gap-1.5 text-[10px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1.5" data-testid="export-duration-warning">
            <AlertTriangle className="w-3 h-3 mt-0.5 shrink-0" />
            <span>Durée {Math.ceil(totalDuration)}s &gt; {EXPORT_MAX_DURATION_SEC}s — la vidéo sera tronquée à {EXPORT_MAX_DURATION_SEC}s.</span>
          </div>
        )}

        <Button
          size="sm"
          onClick={handleExport}
          disabled={!hasAudio || exporting}
          className="w-full bg-[#1a1a2e] hover:bg-[#2a2a3e] text-white font-semibold gap-1.5 disabled:opacity-50"
          data-testid="export-button"
        >
          {exporting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
          {exporting ? `Rendering ${Math.round(exportPct)}%` : '📥 Exporter vidéo finale'}
        </Button>

        {exporting && (
          <div className="h-1.5 rounded-full bg-muted overflow-hidden" data-testid="export-progress">
            <div
              className="h-full bg-[#C9A84C] transition-[width] duration-100"
              style={{ width: `${exportPct}%` }}
            />
          </div>
        )}

        <p className="text-[10px] text-muted-foreground leading-relaxed">
          {hasAudio
            ? '.webm 9:16 (720×1280, VP9), sous-titres incrustés style TikTok, audio synchronisé. Prêt à publier.'
            : 'Activé après génération de la voix off.'}
        </p>
      </div>
    </div>
  );
};

export default VideoPreviewPlayer;
