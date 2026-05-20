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
import { Loader2, Copy, Download, Video as VideoIcon, Sparkles, Trash2, RefreshCw, CheckCircle2, AlertTriangle } from 'lucide-react';

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

const VideoCard = ({ video, idx, runId, onMarkPublished }) => {
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
              Score viral IA (indicatif) : {'★'.repeat(video.viral_score || 0)}{'☆'.repeat(5 - (video.viral_score || 0))}
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
          {onMarkPublished && (
            <Button variant="default" size="sm" onClick={() => onMarkPublished(runId)} data-testid={`mark-published-${idx}`}>
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Marquer publié
            </Button>
          )}
        </div>
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
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('generate');

  const axiosConfig = useCallback(() => {
    const token = localStorage.getItem('adminToken') || localStorage.getItem('token');
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
  }, [activeTab, fetchHistory]);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!form.topic_brief.trim() || form.topic_brief.trim().length < 5) {
      toast.error('Topic trop court (min 5 caractères)');
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const r = await axios.post(`${API}/admin/video-factory/generate`, form, axiosConfig());
      setResult(r.data);
      toast.success(`${r.data.videos.length} vidéo(s) générée(s) — coût ${r.data.estimated_cost_eur}€`);
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

                <div className="flex items-end justify-between flex-wrap gap-3">
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
                  <Button type="submit" disabled={loading} className="gap-2" data-testid="btn-generate">
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
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">{result.model_used}</Badge>
                    <Badge variant="outline">Coût ~{result.estimated_cost_eur}€</Badge>
                    <Badge variant="outline">{result.videos.length} vidéo(s)</Badge>
                  </div>
                  {result.warnings?.length > 0 && (
                    <p className="text-xs text-amber-700" data-testid="warnings-list">
                      {result.warnings.length} avertissement(s) IA : {result.warnings.slice(0, 2).join(' · ')}{result.warnings.length > 2 ? '…' : ''}
                    </p>
                  )}
                </CardContent>
              </Card>
              {result.videos.map((v, i) => (
                <VideoCard key={i} video={v} idx={i} runId={result.run_id} onMarkPublished={markPublished} />
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
                  <VideoCard key={i} video={v} idx={i} runId={run.id} onMarkPublished={markPublished} />
                ))}
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminVideoFactory;
