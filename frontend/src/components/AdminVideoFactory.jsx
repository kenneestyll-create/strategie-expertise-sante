import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Copy, Download, Video as VideoIcon, Sparkles, Trash2, RefreshCw, CheckCircle2, AlertTriangle, BarChart3, TrendingUp } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SERVICES = [
  { value: 'auto', label: 'Auto (selon urgence)' },
  { value: '0€', label: '0€ — StratégiIA (gratuit)' },
  { value: '29€', label: '29€ — Analyse PDF' },
  { value: '97€', label: '97€ — Dossier Express' },
];
const INTENTIONS = ['émotion', 'autorité', 'éducatif'];
const URGENCES = ['faible', 'moyen', 'critique'];
const PLATEFORMES = ['TikTok', 'YouTube Shorts', 'Facebook Reels', 'Instagram Reels'];
const FORMATS = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'];
const FORMAT_LABELS_FR = {
  F1: 'Erreurs en expertise',
  F2: 'Explications chiffrées',
  F3: 'Cas réel anonymisé',
  F4: 'Analyse CPAM',
  F5: 'Réaction à un courrier',
  F6: 'Erreurs de vocabulaire',
  F7: 'Checklist dossier',
};

const MODE_BADGES = {
  forced: { label: 'Forcé manuellement', className: 'bg-violet-500/10 text-violet-700 border-violet-500/30' },
  weighted: { label: 'Pondéré performance', className: 'bg-amber-500/10 text-amber-700 border-amber-500/30' },
  fallback: { label: 'Fallback aléatoire', className: 'bg-slate-500/10 text-slate-700 border-slate-500/30' },
  free: { label: 'Libre IA', className: 'bg-sky-500/10 text-sky-700 border-sky-500/30' },
};

const copyToClipboard = (text, label) => {
  navigator.clipboard.writeText(text || '').then(
    () => toast.success(`${label} copié`),
    () => toast.error('Échec copie'),
  );
};

const downloadFile = (filename, content, mime = 'text/plain') => {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

const VideoCard = ({ video, idx, runId, onMarkPublished, onOpenMetrics }) => {
  const fullPack = JSON.stringify(video, null, 2);
  const safeSlug = (video.format_used || `v${idx + 1}`).toLowerCase();

  return (
    <Card data-testid={`video-card-${idx}`} className="border-border/60">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="outline" className="font-mono text-xs">{video.format_used}</Badge>
              <CardTitle className="text-base">{video.format_label}</CardTitle>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Conversion ★{video.conversion_score || 0}/5 · Viral ★{video.viral_score || 0}/5 <span className="italic">(estimatif IA)</span>
            </p>
          </div>
          <div className="flex items-center gap-2">
            {video.compliance_passed ? (
              <Badge className="bg-emerald-500/10 text-emerald-700 border-emerald-500/30 gap-1">
                <CheckCircle2 className="w-3 h-3" /> Compliance OK
              </Badge>
            ) : (
              <Badge className="bg-amber-500/10 text-amber-700 border-amber-500/30 gap-1" data-testid="compliance-warning">
                <AlertTriangle className="w-3 h-3" /> À relire
              </Badge>
            )}
          </div>
        </div>
        {video.compliance_notes && (
          <p className="text-xs text-amber-700 mt-2" data-testid="compliance-notes">{video.compliance_notes}</p>
        )}
      </CardHeader>

      <CardContent className="space-y-4">
        {/* HOOKS */}
        <section data-testid={`section-hooks-${idx}`}>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold uppercase tracking-wide">Hooks (3 variantes)</h4>
            <Button variant="ghost" size="sm" onClick={() => copyToClipboard(video.hook_variants?.join('\n'), 'Hooks')} data-testid={`copy-hooks-${idx}`}>
              <Copy className="w-3.5 h-3.5 mr-1" /> Copier
            </Button>
          </div>
          <ul className="space-y-1.5">
            {(video.hook_variants || []).map((h, i) => (
              <li key={i} className="text-sm bg-muted/40 rounded-md px-3 py-2 flex items-start gap-2">
                <span className="font-mono text-xs text-muted-foreground mt-0.5">{String.fromCharCode(65 + i)}.</span>
                <span>{h}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* SCRIPT */}
        <section data-testid={`section-script-${idx}`}>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold uppercase tracking-wide">Script ({(video.script || '').split(/\s+/).filter(Boolean).length} mots)</h4>
            <Button variant="ghost" size="sm" onClick={() => copyToClipboard(video.script, 'Script')} data-testid={`copy-script-${idx}`}>
              <Copy className="w-3.5 h-3.5 mr-1" /> Copier
            </Button>
          </div>
          <p className="text-sm bg-muted/40 rounded-md px-3 py-3 whitespace-pre-wrap leading-relaxed">{video.script}</p>
        </section>

        {/* STORYBOARD */}
        <section data-testid={`section-storyboard-${idx}`}>
          <h4 className="text-sm font-semibold uppercase tracking-wide mb-2">Storyboard ({(video.storyboard || []).length} plans)</h4>
          <div className="space-y-2">
            {(video.storyboard || []).map((p, i) => (
              <div key={i} className="text-sm border border-border/50 rounded-md px-3 py-2">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="secondary" className="text-xs">Plan {p.plan || i + 1}</Badge>
                  <Badge variant="outline" className="text-xs">{p.type}</Badge>
                  <span className="text-xs text-muted-foreground">{p.duree_sec}s</span>
                </div>
                <p className="text-sm">{p.description}</p>
                {p.ambiance && <p className="text-xs text-muted-foreground italic mt-0.5">Ambiance : {p.ambiance}</p>}
                {p.broll_search_term && (
                  <p className="text-xs text-muted-foreground mt-0.5">
                    B-roll Pexels : <span className="font-mono">{p.broll_search_term}</span>
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* SUBTITLES */}
        <section data-testid={`section-srt-${idx}`}>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold uppercase tracking-wide">Sous-titres .srt</h4>
            <div className="flex gap-1">
              <Button variant="ghost" size="sm" onClick={() => copyToClipboard(video.subtitles_srt, 'Sous-titres')} data-testid={`copy-srt-${idx}`}>
                <Copy className="w-3.5 h-3.5 mr-1" /> Copier
              </Button>
              <Button variant="ghost" size="sm" onClick={() => downloadFile(`ses-video-${safeSlug}-${idx + 1}.srt`, video.subtitles_srt || '')} data-testid={`download-srt-${idx}`}>
                <Download className="w-3.5 h-3.5 mr-1" /> .srt
              </Button>
            </div>
          </div>
          <pre className="text-xs bg-muted/40 rounded-md px-3 py-2 overflow-x-auto whitespace-pre-wrap max-h-40">{video.subtitles_srt}</pre>
        </section>

        {/* SEO */}
        <section data-testid={`section-seo-${idx}`}>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold uppercase tracking-wide">Pack SEO</h4>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(
                `${video.seo?.title}\n\n${video.seo?.description}\n\n${(video.seo?.hashtags || []).join(' ')}`,
                'Pack SEO',
              )}
              data-testid={`copy-seo-${idx}`}
            >
              <Copy className="w-3.5 h-3.5 mr-1" /> Copier
            </Button>
          </div>
          <div className="space-y-1.5 text-sm">
            <p><span className="text-muted-foreground text-xs uppercase mr-2">Titre</span>{video.seo?.title}</p>
            <p><span className="text-muted-foreground text-xs uppercase mr-2">Description</span>{video.seo?.description}</p>
            <div className="flex flex-wrap gap-1.5">
              {(video.seo?.hashtags || []).map((h, i) => (
                <Badge key={i} variant="outline" className="text-xs font-mono">{h}</Badge>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section data-testid={`section-cta-${idx}`} className="rounded-md bg-foreground/5 border border-border/60 px-3 py-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground mb-1">CTA unique → {video.cta?.target_service}</p>
              <p className="text-sm font-medium">{video.cta?.text}</p>
              <a
                href={video.cta?.url_with_utm}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-accent hover:underline font-mono break-all"
                data-testid={`cta-url-${idx}`}
              >
                {video.cta?.url_with_utm}
              </a>
            </div>
            <Button variant="ghost" size="sm" onClick={() => copyToClipboard(video.cta?.url_with_utm, 'Lien CTA')} data-testid={`copy-cta-${idx}`}>
              <Copy className="w-3.5 h-3.5 mr-1" /> Copier le lien
            </Button>
          </div>
        </section>

        {/* GLOBAL ACTIONS */}
        <div className="flex flex-wrap gap-2 pt-2 border-t border-border/40">
          <Button variant="outline" size="sm" onClick={() => copyToClipboard(fullPack, 'Pack complet (JSON)')} data-testid={`copy-all-${idx}`}>
            <Copy className="w-3.5 h-3.5 mr-1" /> Copier pack complet
          </Button>
          <Button variant="outline" size="sm" onClick={() => downloadFile(`ses-video-${safeSlug}-${idx + 1}.json`, fullPack, 'application/json')} data-testid={`download-json-${idx}`}>
            <Download className="w-3.5 h-3.5 mr-1" /> Export JSON
          </Button>
          {onOpenMetrics && (
            <Button variant="outline" size="sm" onClick={() => onOpenMetrics(runId, idx, video.format_used)} data-testid={`save-metrics-${idx}`}>
              <BarChart3 className="w-3.5 h-3.5 mr-1" /> Saisir métriques
            </Button>
          )}
          {onMarkPublished && (
            <Button variant="default" size="sm" onClick={() => onMarkPublished(runId)} data-testid={`mark-published-${idx}`}>
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Marquer publié
            </Button>
          )}
        </div>

        {video.disclaimer_text && (
          <p className="text-xs text-muted-foreground italic pt-1" data-testid={`disclaimer-${idx}`}>
            {video.disclaimer_text}
          </p>
        )}
      </CardContent>
    </Card>
  );
};

export const AdminVideoFactory = () => {
  const [form, setForm] = useState({
    topic_brief: '',
    service_target: 'auto',
    intention: 'autorité',
    urgence: 'moyen',
    plateforme: 'TikTok',
    batch_size: 1,
    forced_format: '',
    use_performance_weights: true,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('generate');

  // V2 — Performances
  const [weightsSnapshot, setWeightsSnapshot] = useState(null);
  const [weightsLoading, setWeightsLoading] = useState(false);
  const [metricsList, setMetricsList] = useState([]);
  const [metricsModal, setMetricsModal] = useState(null); // {runId, videoIdx, formatUsed}
  const [metricsForm, setMetricsForm] = useState({ views: '', ctr: '', conversion: '', note: '' });
  const [savingMetrics, setSavingMetrics] = useState(false);

  const axiosConfig = useCallback(() => {
    const token = localStorage.getItem('admin_token') || localStorage.getItem('adminToken') || localStorage.getItem('token');
    return { headers: { Authorization: `Bearer ${token}` } };
  }, []);

  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const r = await axios.get(`${API}/admin/video-factory/history?limit=20`, axiosConfig());
      setHistory(r.data?.items || []);
    } catch (e) {
      toast.error('Échec chargement historique');
    } finally {
      setHistoryLoading(false);
    }
  }, [axiosConfig]);

  useEffect(() => {
    if (activeTab === 'history') fetchHistory();
    if (activeTab === 'performance') {
      fetchWeights();
      fetchMetrics();
    }
  }, [activeTab, fetchHistory]);  // eslint-disable-line react-hooks/exhaustive-deps

  const fetchWeights = async () => {
    setWeightsLoading(true);
    try {
      const r = await axios.get(`${API}/admin/video-factory/performance/weights`, axiosConfig());
      setWeightsSnapshot(r.data);
    } catch (e) {
      toast.error('Échec chargement poids');
    } finally {
      setWeightsLoading(false);
    }
  };

  const fetchMetrics = async () => {
    try {
      const r = await axios.get(`${API}/admin/video-factory/metrics?limit=50`, axiosConfig());
      setMetricsList(r.data?.items || []);
    } catch (e) {
      // silent
    }
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!form.topic_brief.trim() || form.topic_brief.trim().length < 5) {
      toast.error('Topic trop court (min 5 caractères)');
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const payload = { ...form };
      if (!payload.forced_format) delete payload.forced_format;
      const r = await axios.post(`${API}/admin/video-factory/generate`, payload, axiosConfig());
      setResult(r.data);
      const tag = r.data.used_weights ? ` · format auto-pondéré ${r.data.forced_format}` : (r.data.forced_format ? ` · ${r.data.forced_format} forcé` : '');
      toast.success(`${r.data.videos.length} vidéo(s) générée(s) — coût ${r.data.estimated_cost_eur}€${tag}`);
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message;
      toast.error(`Échec génération : ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const markPublished = async (runId) => {
    try {
      await axios.patch(
        `${API}/admin/video-factory/${runId}/status`,
        { status: 'published' },
        axiosConfig(),
      );
      toast.success('Marqué publié');
      if (activeTab === 'history') fetchHistory();
    } catch (e) {
      toast.error('Échec mise à jour');
    }
  };

  const deleteRun = async (runId) => {
    if (!window.confirm('Supprimer cette génération ?')) return;
    try {
      await axios.delete(`${API}/admin/video-factory/${runId}`, axiosConfig());
      toast.success('Supprimé');
      fetchHistory();
    } catch (e) {
      toast.error('Échec suppression');
    }
  };

  const openMetricsModal = (runId, videoIdx, formatUsed) => {
    setMetricsModal({ runId, videoIdx, formatUsed });
    setMetricsForm({ views: '', ctr: '', conversion: '', note: '' });
  };

  const submitMetrics = async (e) => {
    e.preventDefault();
    if (!metricsModal) return;
    const views = Number(metricsForm.views);
    const ctr = Number(metricsForm.ctr);
    const conversion = Number(metricsForm.conversion);
    if (!Number.isFinite(views) || views < 0 || !Number.isFinite(ctr) || ctr < 0 || !Number.isFinite(conversion) || conversion < 0) {
      toast.error('Valeurs invalides (views, CTR, conversion ≥ 0)');
      return;
    }
    setSavingMetrics(true);
    try {
      await axios.post(
        `${API}/admin/video-factory/metrics`,
        {
          run_id: metricsModal.runId,
          video_idx: metricsModal.videoIdx,
          views,
          ctr,
          conversion,
          note: metricsForm.note || null,
        },
        axiosConfig(),
      );
      toast.success(`Métriques enregistrées (${metricsModal.formatUsed}) — poids recalculés`);
      setMetricsModal(null);
      if (activeTab === 'performance') {
        fetchWeights();
        fetchMetrics();
      }
    } catch (err) {
      toast.error(`Échec : ${err?.response?.data?.detail || err.message}`);
    } finally {
      setSavingMetrics(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="admin-video-factory">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <VideoIcon className="w-5 h-5 text-accent" />
            Video Factory — Génération IA autonome
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            1 brief → 1 pack vidéo complet (hook, script, storyboard, .srt, SEO, CTA). Modèle : Claude Haiku 4.5. Coût ~0,006€/vidéo.
          </p>
        </CardHeader>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList data-testid="video-factory-tabs">
          <TabsTrigger value="generate" data-testid="tab-generate">
            <Sparkles className="w-4 h-4 mr-1.5" /> Générer
          </TabsTrigger>
          <TabsTrigger value="history" data-testid="tab-history">
            <RefreshCw className="w-4 h-4 mr-1.5" /> Historique
          </TabsTrigger>
          <TabsTrigger value="performance" data-testid="tab-performance">
            <TrendingUp className="w-4 h-4 mr-1.5" /> Performances
          </TabsTrigger>
        </TabsList>

        <TabsContent value="generate" className="space-y-5">
          <Card>
            <CardContent className="pt-6">
              <form onSubmit={onSubmit} className="space-y-5" data-testid="video-factory-form">
                <div>
                  <Label htmlFor="vf-topic">Topic / Brief</Label>
                  <Textarea
                    id="vf-topic"
                    data-testid="input-topic"
                    placeholder="Ex : Erreur fréquente face à un médecin-conseil CPAM lors d'expertise IPP"
                    value={form.topic_brief}
                    onChange={(e) => setForm({ ...form, topic_brief: e.target.value })}
                    rows={3}
                    maxLength={500}
                  />
                  <p className="text-xs text-muted-foreground mt-1">{form.topic_brief.length}/500</p>
                </div>

                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <Label>Service cible</Label>
                    <Select value={form.service_target} onValueChange={(v) => setForm({ ...form, service_target: v })}>
                      <SelectTrigger data-testid="select-service"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {SERVICES.map((s) => (<SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Intention</Label>
                    <Select value={form.intention} onValueChange={(v) => setForm({ ...form, intention: v })}>
                      <SelectTrigger data-testid="select-intention"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {INTENTIONS.map((s) => (<SelectItem key={s} value={s}>{s}</SelectItem>))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Urgence</Label>
                    <Select value={form.urgence} onValueChange={(v) => setForm({ ...form, urgence: v })}>
                      <SelectTrigger data-testid="select-urgence"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {URGENCES.map((s) => (<SelectItem key={s} value={s}>{s}</SelectItem>))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Plateforme</Label>
                    <Select value={form.plateforme} onValueChange={(v) => setForm({ ...form, plateforme: v })}>
                      <SelectTrigger data-testid="select-plateforme"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {PLATEFORMES.map((s) => (<SelectItem key={s} value={s}>{s}</SelectItem>))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex flex-wrap items-end gap-4 pt-2 border-t border-border/40">
                  <div className="w-40">
                    <Label htmlFor="vf-batch">Nb vidéos (1-5)</Label>
                    <Input
                      id="vf-batch"
                      type="number"
                      min={1}
                      max={5}
                      value={form.batch_size}
                      onChange={(e) => setForm({ ...form, batch_size: Math.max(1, Math.min(5, Number(e.target.value) || 1)) })}
                      data-testid="input-batch"
                    />
                  </div>
                  <div className="w-44">
                    <Label>Forcer un format (optionnel)</Label>
                    <Select value={form.forced_format || 'auto'} onValueChange={(v) => setForm({ ...form, forced_format: v === 'auto' ? '' : v })}>
                      <SelectTrigger data-testid="select-forced-format"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="auto">Auto (laisser IA / poids)</SelectItem>
                        {FORMATS.map((f) => (
                          <SelectItem key={f} value={f}>{f} — {FORMAT_LABELS_FR[f]}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <label className="flex items-center gap-2 text-sm pb-2" data-testid="toggle-use-weights">
                    <input
                      type="checkbox"
                      checked={form.use_performance_weights}
                      onChange={(e) => setForm({ ...form, use_performance_weights: e.target.checked })}
                    />
                    Utiliser les poids de performance (si dispos)
                  </label>
                  <Button type="submit" disabled={loading} className="gap-2 ml-auto" data-testid="btn-generate">
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                    {loading ? 'Génération…' : 'Générer le pack vidéo'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {result && (
            <div className="space-y-4" data-testid="generation-result">
              <Card>
                <CardContent className="py-4 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="secondary">{result.model_used}</Badge>
                    <Badge variant="outline">Coût ~{result.estimated_cost_eur}€</Badge>
                    <Badge variant="outline">{result.videos.length} vidéo(s)</Badge>
                    {result.mode && MODE_BADGES[result.mode] && (
                      <Badge className={MODE_BADGES[result.mode].className} data-testid={`mode-badge-${result.mode}`}>
                        {MODE_BADGES[result.mode].label}{result.forced_format ? ` · ${result.forced_format}` : ''}
                      </Badge>
                    )}
                  </div>
                  {result.warnings?.length > 0 && (
                    <p className="text-xs text-amber-700" data-testid="warnings-list">
                      {result.warnings.length} avertissement(s) IA : {result.warnings.slice(0, 2).join(' · ')}{result.warnings.length > 2 ? '…' : ''}
                    </p>
                  )}
                </CardContent>
              </Card>
              {result.videos.map((v, i) => (
                <VideoCard key={i} video={v} idx={i} runId={result.run_id} onMarkPublished={markPublished} onOpenMetrics={openMetricsModal} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <div className="flex justify-end">
            <Button variant="outline" size="sm" onClick={fetchHistory} disabled={historyLoading} data-testid="btn-refresh-history">
              <RefreshCw className={`w-3.5 h-3.5 mr-1 ${historyLoading ? 'animate-spin' : ''}`} /> Rafraîchir
            </Button>
          </div>
          {history.length === 0 && !historyLoading && (
            <Card><CardContent className="py-8 text-center text-sm text-muted-foreground">Aucune génération à ce jour.</CardContent></Card>
          )}
          {history.map((run) => (
            <Card key={run.id} data-testid={`history-item-${run.id}`}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div>
                    <CardTitle className="text-sm">
                      {(run.input?.topic_brief || '').slice(0, 80)}{(run.input?.topic_brief || '').length > 80 ? '…' : ''}
                    </CardTitle>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <Badge variant="outline" className="text-xs">{run.videos?.length || 0} vidéo(s)</Badge>
                      <Badge variant="outline" className="text-xs">{run.input?.plateforme}</Badge>
                      <Badge variant="outline" className="text-xs">{run.input?.urgence}</Badge>
                      <Badge variant="secondary" className="text-xs">{run.status}</Badge>
                      <span className="text-xs text-muted-foreground">{new Date(run.created_at).toLocaleString('fr-FR')}</span>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="sm" onClick={() => deleteRun(run.id)} data-testid={`delete-run-${run.id}`}>
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {(run.videos || []).map((v, i) => (
                  <VideoCard key={i} video={v} idx={i} runId={run.id} onMarkPublished={markPublished} onOpenMetrics={openMetricsModal} />
                ))}
              </CardContent>
            </Card>
          ))}
        </TabsContent>
        <TabsContent value="performance" className="space-y-4" data-testid="performance-tab-content">
          <Card>
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-base flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-accent" />
                  Poids par format (boucle d'apprentissage V2)
                </CardTitle>
                <p className="text-xs text-muted-foreground mt-1">
                  Calculés à partir de vos métriques saisies. Floor exploration 10% par format. Formule : 0.5×conversion + 0.3×CTR + 0.2×views (normalisé).
                </p>
              </div>
              <Button variant="outline" size="sm" onClick={fetchWeights} disabled={weightsLoading} data-testid="btn-refresh-weights">
                <RefreshCw className={`w-3.5 h-3.5 mr-1 ${weightsLoading ? 'animate-spin' : ''}`} /> Rafraîchir
              </Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {weightsSnapshot && weightsSnapshot.total_samples === 0 && (
                <p className="text-sm text-muted-foreground" data-testid="weights-empty">
                  Aucune métrique saisie. Génère une vidéo, publie-la, puis clique sur <strong>Saisir métriques</strong> dans l'historique. Dès la 1ère métrique, les poids s'activeront pour les prochaines générations.
                </p>
              )}
              {weightsSnapshot && (
                <div className="space-y-2" data-testid="weights-list">
                  {(() => {
                    const ws = weightsSnapshot.weights || {};
                    const values = FORMATS.map(f => Number(ws[f] || 0));
                    const avg = values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
                    const dominantThreshold = avg * 1.5;
                    return FORMATS.map((f) => {
                      const w = Number(ws[f] || 0);
                      const m = weightsSnapshot.metrics_by_format?.[f];
                      const pct = Math.round(w * 100);
                      const isDominant = avg > 0 && w > dominantThreshold;
                      return (
                        <div key={f} data-testid={`weight-row-${f}`}>
                          <div className="flex items-center justify-between text-sm mb-0.5 flex-wrap gap-1">
                            <span className="font-mono flex items-center gap-1.5">
                              {f} — {FORMAT_LABELS_FR[f]}
                              {isDominant && (
                                <Badge className="bg-orange-500/10 text-orange-700 border-orange-500/30 text-[10px] px-1.5 py-0" data-testid={`dominant-badge-${f}`}>
                                  🔥 Format dominant
                                </Badge>
                              )}
                            </span>
                            <span className="font-mono text-xs">
                              {m ? `views ${Math.round(m.views)} · CTR ${m.ctr.toFixed(1)}% · conv ${m.conversion.toFixed(1)}% · n=${m.samples}` : '— pas encore de métrique'}
                            </span>
                          </div>
                          <div className="w-full bg-muted/40 rounded-full h-2 overflow-hidden">
                            <div
                              className={`h-2 transition-all ${isDominant ? 'bg-orange-500' : 'bg-accent'}`}
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                          <p className="text-xs text-muted-foreground mt-0.5">Poids : {(w * 100).toFixed(1)}%</p>
                        </div>
                      );
                    });
                  })()}
                </div>
              )}
              {weightsSnapshot?.updated_at && (
                <p className="text-xs text-muted-foreground">
                  Dernier recalcul : {new Date(weightsSnapshot.updated_at).toLocaleString('fr-FR')} · Total samples : {weightsSnapshot.total_samples}
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Métriques saisies (50 plus récentes)</CardTitle>
            </CardHeader>
            <CardContent>
              {metricsList.length === 0 ? (
                <p className="text-sm text-muted-foreground" data-testid="metrics-empty">Aucune métrique pour le moment.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs" data-testid="metrics-table">
                    <thead className="text-left text-muted-foreground border-b border-border/40">
                      <tr>
                        <th className="py-1.5 pr-2">Date</th>
                        <th className="py-1.5 pr-2">Format</th>
                        <th className="py-1.5 pr-2">Plateforme</th>
                        <th className="py-1.5 pr-2 text-right">Views</th>
                        <th className="py-1.5 pr-2 text-right">CTR</th>
                        <th className="py-1.5 pr-2 text-right">Conv.</th>
                      </tr>
                    </thead>
                    <tbody>
                      {metricsList.map((m, i) => (
                        <tr key={i} className="border-b border-border/20">
                          <td className="py-1 pr-2">{new Date(m.created_at).toLocaleDateString('fr-FR')}</td>
                          <td className="py-1 pr-2 font-mono">{m.format_used}</td>
                          <td className="py-1 pr-2">{m.plateforme || '—'}</td>
                          <td className="py-1 pr-2 text-right">{Math.round(m.views)}</td>
                          <td className="py-1 pr-2 text-right">{Number(m.ctr).toFixed(1)}%</td>
                          <td className="py-1 pr-2 text-right">{Number(m.conversion).toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Modal saisie métriques */}
      {metricsModal && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setMetricsModal(null)}
          data-testid="metrics-modal-backdrop"
        >
          <Card
            className="w-full max-w-md"
            onClick={(e) => e.stopPropagation()}
            data-testid="metrics-modal"
          >
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <BarChart3 className="w-4 h-4" /> Saisir les métriques
              </CardTitle>
              <p className="text-xs text-muted-foreground">
                Format <strong>{metricsModal.formatUsed}</strong> · vidéo #{metricsModal.videoIdx + 1}
              </p>
            </CardHeader>
            <CardContent>
              <form onSubmit={submitMetrics} className="space-y-3" data-testid="metrics-form">
                <div>
                  <Label htmlFor="mf-views">Vues</Label>
                  <Input
                    id="mf-views"
                    type="number"
                    min={0}
                    step={1}
                    placeholder="ex : 12000"
                    value={metricsForm.views}
                    onChange={(e) => setMetricsForm({ ...metricsForm, views: e.target.value })}
                    data-testid="metrics-input-views"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="mf-ctr">CTR (%)</Label>
                  <Input
                    id="mf-ctr"
                    type="number"
                    min={0}
                    max={100}
                    step={0.1}
                    placeholder="ex : 3.2"
                    value={metricsForm.ctr}
                    onChange={(e) => setMetricsForm({ ...metricsForm, ctr: e.target.value })}
                    data-testid="metrics-input-ctr"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="mf-conv">Taux de conversion (%)</Label>
                  <Input
                    id="mf-conv"
                    type="number"
                    min={0}
                    max={100}
                    step={0.1}
                    placeholder="ex : 1.1"
                    value={metricsForm.conversion}
                    onChange={(e) => setMetricsForm({ ...metricsForm, conversion: e.target.value })}
                    data-testid="metrics-input-conversion"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="mf-note">Note (optionnel)</Label>
                  <Input
                    id="mf-note"
                    type="text"
                    placeholder="ex : virale TikTok jeudi"
                    value={metricsForm.note}
                    onChange={(e) => setMetricsForm({ ...metricsForm, note: e.target.value })}
                    data-testid="metrics-input-note"
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <Button type="button" variant="outline" onClick={() => setMetricsModal(null)} data-testid="metrics-cancel">
                    Annuler
                  </Button>
                  <Button type="submit" disabled={savingMetrics} data-testid="metrics-submit">
                    {savingMetrics ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <CheckCircle2 className="w-4 h-4 mr-1" />}
                    Enregistrer
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AdminVideoFactory;
