import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import {
  PenTool, Sparkles, FileText, AlertTriangle, CheckCircle2, Calendar, Settings,
  Loader2, ArrowRight, BarChart3, RefreshCw, BookOpen, Plus, Archive, Eye, Send, ExternalLink,
  Trash2, RotateCcw, Layers, GitBranch,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { GuidePreviewBody } from '@/components/GuidePreviewBody';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const flagSeverityColor = (sev) => sev === 'high' ? 'bg-red-100 text-red-800 border-red-200'
  : sev === 'medium' ? 'bg-amber-100 text-amber-800 border-amber-200'
  : 'bg-slate-100 text-slate-700 border-slate-200';

const flagTypeLabel = {
  loi: 'Article de loi', jurisprudence: 'Jurisprudence', chiffre: 'Chiffre',
  delai: 'Délai', medical_sensitive: 'Donnée médicale', explicit_marker: 'À vérifier',
  nom_propre: 'Nom propre',
};

// Légifrance/Ameli quick-search URL builder
const verifyUrl = (flag) => {
  const q = encodeURIComponent(flag.value);
  if (flag.type === 'loi' || flag.type === 'jurisprudence') return `https://www.legifrance.gouv.fr/search/all?query=${q}`;
  if (flag.type === 'chiffre' || flag.type === 'delai') return `https://www.service-public.fr/recherche?q=${q}`;
  return `https://www.google.com/search?q=${q}`;
};

export const AdminEditorialStudio = () => {
  const { token } = useAuth();
  const cfg = { headers: { Authorization: `Bearer ${token}` } };

  const [view, setView] = useState('home'); // home | editor | settings
  const [editorArticleId, setEditorArticleId] = useState(null);
  const [stats, setStats] = useState(null);
  const [proposals, setProposals] = useState([]);
  const [allArticles, setAllArticles] = useState([]);
  const [poolTopics, setPoolTopics] = useState([]);
  const [config, setConfig] = useState(null);
  const [needsReval, setNeedsReval] = useState([]);
  const [customTitle, setCustomTitle] = useState('');
  const [showPoolFull, setShowPoolFull] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadHome = useCallback(async () => {
    setLoading(true);
    try {
      const [s, p, a, t, c, r] = await Promise.all([
        axios.get(`${API}/admin/editorial/stats`, cfg),
        axios.get(`${API}/admin/editorial/topics/proposals?count=3`, cfg),
        axios.get(`${API}/admin/editorial/articles`, cfg),
        axios.get(`${API}/admin/editorial/topics/all`, cfg),
        axios.get(`${API}/admin/editorial/config`, cfg),
        axios.get(`${API}/admin/editorial/needs-revalidation`, cfg),
      ]);
      setStats(s.data); setProposals(p.data.proposals); setAllArticles(a.data.items);
      setPoolTopics(t.data.topics); setConfig(c.data); setNeedsReval(r.data.items);
    } catch (e) { toast.error("Chargement du Studio Éditorial impossible"); }
    finally { setLoading(false); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => { if (token) loadHome(); }, [token, loadHome]);

  const startFromTopic = async (topicTitle) => {
    try {
      const r = await axios.post(`${API}/admin/editorial/articles/start`, { topic_id: topicTitle }, cfg);
      toast.success("Brouillon créé");
      setEditorArticleId(r.data.id); setView('editor');
      loadHome();
    } catch (e) { toast.error(e?.response?.data?.detail || "Erreur création brouillon"); }
  };

  const startCustom = async () => {
    if (!customTitle.trim() || customTitle.trim().length < 10) { toast.error("Titre trop court"); return; }
    try {
      const r = await axios.post(`${API}/admin/editorial/articles/start`, { custom_title: customTitle.trim() }, cfg);
      toast.success("Brouillon créé");
      setCustomTitle(''); setEditorArticleId(r.data.id); setView('editor');
      loadHome();
    } catch (e) { toast.error(e?.response?.data?.detail || "Erreur"); }
  };

  if (view === 'editor' && editorArticleId) {
    return <EditorView articleId={editorArticleId} onBack={() => { setEditorArticleId(null); setView('home'); loadHome(); }} cfg={cfg} />;
  }

  if (view === 'settings') {
    return <SettingsView config={config} onBack={() => { setView('home'); loadHome(); }} cfg={cfg} />;
  }

  if (loading || !stats) return <div className="flex items-center justify-center py-10 text-muted-foreground"><Loader2 className="w-5 h-5 animate-spin mr-2" /> Chargement…</div>;

  const reminderDue = stats.weekly_reminder_due;

  return (
    <div className="space-y-6" data-testid="editorial-studio-root">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h3 className="text-base font-semibold flex items-center gap-2">
            <PenTool className="w-4 h-4 text-[#C9A84C]" /> Studio Éditorial
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">Production de guides SEO premium — IA contrainte + 7 garde-fous + validation ciblée.</p>
        </div>
        <Button variant="outline" onClick={() => setView('settings')} size="sm" data-testid="editorial-settings-btn"><Settings className="w-4 h-4 mr-1.5" /> Paramètres &amp; Base légale</Button>
      </div>

      {/* Weekly reminder */}
      {reminderDue && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 flex items-start gap-2.5 text-sm" data-testid="editorial-reminder">
          <Calendar className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-amber-900">📝 Rythme éditorial — pas d'article publié cette semaine</p>
            <p className="text-amber-800 text-xs mt-0.5">Maintenir la fréquence de 1 article par semaine est essentiel pour faire monter vos impressions Google. Choisissez un sujet ci-dessous.</p>
          </div>
        </div>
      )}

      {/* Revalidation alert */}
      {stats.needs_revalidation > 0 && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 flex items-start gap-2.5 text-sm" data-testid="editorial-reval-alert">
          <RefreshCw className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-blue-900">🔄 {stats.needs_revalidation} article(s) à revalider</p>
            <p className="text-blue-800 text-xs mt-0.5">Publié(s) il y a plus de 6 mois. Vérifiez que les chiffres et lois cités sont toujours à jour.</p>
            {needsReval.slice(0, 3).map(it => (
              <button key={it.id} onClick={() => { setEditorArticleId(it.id); setView('editor'); }} className="block text-xs text-blue-700 underline mt-1" data-testid={`reval-link-${it.id}`}>
                → {it.title}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3" data-testid="editorial-kpis">
        <Kpi label="Publiés" value={stats.articles.published} sub="articles en ligne" />
        <Kpi label="Brouillons" value={stats.articles.drafts} sub="en cours" />
        <Kpi label="7 derniers jours" value={stats.articles.published_last_7d} sub="publications" tone={reminderDue ? 'amber' : 'default'} />
        <Kpi label="Sujets disponibles" value={stats.topics_pool.available} sub={`sur ${stats.topics_pool.total}`} />
        <Kpi label="Base légale" value={stats.legal_refs_count} sub="références vérifiées" />
      </div>

      {/* Proposals */}
      <Card data-testid="editorial-proposals">
        <CardHeader>
          <CardTitle className="text-sm flex items-center justify-between">
            <span>3 sujets proposés cette session</span>
            <Button size="sm" variant="outline" onClick={loadHome} data-testid="reroll-btn"><RefreshCw className="w-3.5 h-3.5 mr-1" /> Re-tirer</Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {proposals.length === 0 ? (
            <p className="text-xs text-muted-foreground italic">Pool de sujets épuisé. Ajoutez vos propres sujets ou contactez l'équipe.</p>
          ) : (
            <div className="grid lg:grid-cols-3 gap-3">
              {proposals.map((p, i) => (
                <button key={i} onClick={() => startFromTopic(p.title)}
                  className="text-left p-4 rounded-lg border bg-card hover:border-[#C9A84C] hover:bg-[#C9A84C]/5 transition-all group"
                  data-testid={`proposal-${i}`}>
                  <div className="flex items-center gap-1.5 mb-2">
                    <Badge variant="outline" className="text-[10px]">{p.category}</Badge>
                    <Badge className={`text-[10px] ${p.potential === 'haut' ? 'bg-emerald-100 text-emerald-800 border-emerald-200' : 'bg-slate-100 text-slate-700 border-slate-200'}`}>
                      {p.potential === 'haut' ? '🎯 Potentiel haut' : 'Potentiel moyen'}
                    </Badge>
                  </div>
                  <p className="text-sm font-semibold text-foreground leading-snug">{p.title}</p>
                  <p className="text-[11px] text-muted-foreground mt-1.5 line-clamp-2">💡 {p.angle}</p>
                  <p className="text-[10px] text-[#C9A84C] mt-2 group-hover:underline">Démarrer ce sujet →</p>
                </button>
              ))}
            </div>
          )}

          <div className="pt-2 flex items-center gap-2 flex-wrap">
            <Button variant="outline" size="sm" onClick={() => setShowPoolFull(!showPoolFull)} data-testid="show-pool-btn">
              <BookOpen className="w-3.5 h-3.5 mr-1.5" /> {showPoolFull ? 'Masquer' : 'Voir tout le pool'} ({stats.topics_pool.available} dispo.)
            </Button>
          </div>

          {showPoolFull && (
            <div className="grid sm:grid-cols-2 gap-2 mt-3 max-h-[400px] overflow-y-auto" data-testid="pool-full">
              {poolTopics.filter(t => !t.used).map((t, i) => (
                <button key={i} onClick={() => startFromTopic(t.title)}
                  className="text-left p-2.5 rounded-md border bg-card hover:border-[#C9A84C] transition-colors"
                  data-testid={`pool-item-${i}`}>
                  <p className="text-xs font-medium text-foreground leading-snug">{t.title}</p>
                  <p className="text-[10px] text-muted-foreground mt-0.5">{t.category} · {t.potential}</p>
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Custom topic */}
      <Card data-testid="editorial-custom-topic">
        <CardHeader><CardTitle className="text-sm flex items-center gap-2"><Plus className="w-4 h-4 text-[#C9A84C]" /> Mon propre sujet</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input value={customTitle} onChange={(e) => setCustomTitle(e.target.value)} placeholder="Ex. : Comment contester un refus de RQTH en 2026 ?" className="flex-1" data-testid="custom-title-input" maxLength={150} />
            <Button onClick={startCustom} disabled={!customTitle.trim()} className="bg-[#C9A84C] hover:bg-[#B89640] text-[#0a0a08] font-semibold" data-testid="custom-start-btn">Démarrer →</Button>
          </div>
        </CardContent>
      </Card>

      {/* Articles list */}
      <Card data-testid="editorial-articles-list">
        <CardHeader><CardTitle className="text-sm">Mes articles ({allArticles.length})</CardTitle></CardHeader>
        <CardContent>
          {allArticles.length === 0 ? (
            <p className="text-xs text-muted-foreground italic">Aucun article pour le moment. Choisissez un sujet ci-dessus pour démarrer.</p>
          ) : (
            <div className="space-y-2">
              {allArticles.map(a => (
                <div key={a.id} className="flex items-center justify-between gap-3 p-3 rounded-lg border bg-card hover:border-[#C9A84C]/40 transition-all" data-testid={`article-${a.id}`}>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <Badge className={`text-[10px] ${a.status === 'published' ? 'bg-emerald-100 text-emerald-800 border-emerald-200' : a.status === 'archived' ? 'bg-slate-200 text-slate-700' : 'bg-amber-100 text-amber-800 border-amber-200'}`}>
                        {a.status === 'published' ? 'Publié' : a.status === 'archived' ? 'Archivé' : 'Brouillon'}
                      </Badge>
                      {a.category && <Badge variant="outline" className="text-[10px]">{a.category}</Badge>}
                      {a.red_flags && a.red_flags.length > 0 && a.status !== 'published' && (
                        <Badge className="bg-red-100 text-red-800 border-red-200 text-[10px]">
                          ⚠ {a.red_flags.filter(f => !f.validated).length} à valider
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm font-medium text-foreground truncate">{a.title}</p>
                    <p className="text-[10px] text-muted-foreground mt-0.5">
                      MAJ {new Date(a.updated_at).toLocaleString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Button size="sm" variant="outline" onClick={() => { setEditorArticleId(a.id); setView('editor'); }} data-testid={`open-${a.id}`}>
                      <PenTool className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

const Kpi = ({ label, value, sub, tone = 'default' }) => (
  <div className="rounded-lg border bg-card p-3.5">
    <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide">{label}</p>
    <p className={`text-2xl font-semibold ${tone === 'amber' ? 'text-amber-600' : 'text-foreground'} mt-1`}>{value}</p>
    {sub && <p className="text-[10px] text-muted-foreground mt-0.5">{sub}</p>}
  </div>
);


// ===================== EDITOR VIEW =====================

const EditorView = ({ articleId, onBack, cfg }) => {
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiBusy, setAiBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/admin/editorial/articles/${articleId}`, cfg);
      setArticle(r.data);
    } catch { toast.error("Article introuvable"); onBack(); }
    finally { setLoading(false); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [articleId]);

  useEffect(() => { load(); }, [load]);

  const generatePlan = async () => {
    setAiBusy(true);
    try {
      const r = await axios.post(`${API}/admin/editorial/articles/${articleId}/generate-plan`, {}, cfg);
      toast.success("Plan généré");
      setArticle({ ...article, ...r.data });
    } catch (e) { toast.error(e?.response?.data?.detail || "Erreur génération plan"); }
    finally { setAiBusy(false); }
  };

  const generateDraft = async () => {
    setAiBusy(true);
    try {
      const r = await axios.post(`${API}/admin/editorial/articles/${articleId}/generate-draft`, {}, cfg);
      toast.success("Brouillon généré");
      setArticle({ ...article, content: r.data.content, red_flags: r.data.red_flags });
    } catch (e) { toast.error(e?.response?.data?.detail || "Erreur génération brouillon"); }
    finally { setAiBusy(false); }
  };

  const saveContent = async (newContent) => {
    try {
      const r = await axios.post(`${API}/admin/editorial/articles/${articleId}/save`, { content: newContent }, cfg);
      setArticle({ ...article, content: newContent, red_flags: r.data.red_flags || article.red_flags });
    } catch (e) { toast.error("Sauvegarde échouée"); }
  };

  const validateFlag = async (flagId, validated) => {
    try {
      await axios.post(`${API}/admin/editorial/articles/${articleId}/validate-flag`, { flag_id: flagId, validated }, cfg);
      const flags = article.red_flags.map(f => f.id === flagId ? { ...f, validated } : f);
      setArticle({ ...article, red_flags: flags });
    } catch { toast.error("Erreur validation"); }
  };

  const publish = async () => {
    if (!window.confirm("Publier cet article ? Cette action le met en ligne sur le preview (pour aperçu). Pour pousser en production, utilisez 'Migrer vers le seed' après.")) return;
    try {
      const r = await axios.post(`${API}/admin/editorial/articles/${articleId}/publish`, {}, cfg);
      toast.success(`Publié (preview) : ${r.data.url}`);
      load();
    } catch (e) { toast.error(e?.response?.data?.detail || "Erreur publication"); }
  };

  const archive = async () => {
    if (!window.confirm("Archiver cet article (suppression douce) ? Le sujet sera remis dans le pool.")) return;
    try {
      await axios.delete(`${API}/admin/editorial/articles/${articleId}`, cfg);
      toast.success("Archivé — sujet remis dans le pool"); onBack();
    } catch { toast.error("Erreur archivage"); }
  };

  const hardDelete = async () => {
    if (!window.confirm("⚠️ SUPPRIMER DÉFINITIVEMENT ce brouillon ?\n\nCette action est irréversible. Le sujet retournera dans le pool.")) return;
    try {
      await axios.delete(`${API}/admin/editorial/articles/${articleId}?hard=true`, cfg);
      toast.success("Brouillon supprimé — sujet remis dans le pool"); onBack();
    } catch { toast.error("Erreur suppression"); }
  };

  const changeTopic = async () => {
    if (!window.confirm("Abandonner ce sujet et en choisir un autre ?\n\nLe brouillon sera supprimé et le sujet remis dans le pool.")) return;
    try {
      await axios.delete(`${API}/admin/editorial/articles/${articleId}?hard=true`, cfg);
      toast.success("Sujet abandonné — choisissez-en un nouveau"); onBack();
    } catch { toast.error("Erreur"); }
  };

  const [structuring, setStructuring] = useState(false);
  const generateStructure = async () => {
    setStructuring(true);
    try {
      const r = await axios.post(`${API}/admin/editorial/articles/${articleId}/structure`, {}, cfg);
      toast.success("Structure générée — révisez chaque bloc");
      setArticle({ ...article, structured_content: r.data.structured_content });
      if (r.data.missing_keys?.length) {
        toast.warning(`Champs manquants : ${r.data.missing_keys.join(', ')}`);
      }
    } catch (e) { toast.error(e?.response?.data?.detail || "Erreur structuration"); }
    finally { setStructuring(false); }
  };

  const saveStructured = async (newStructured) => {
    try {
      await axios.post(`${API}/admin/editorial/articles/${articleId}/save`, { structured_content: newStructured }, cfg);
      setArticle({ ...article, structured_content: newStructured });
    } catch { /* silent */ }
  };

  const [showPreview, setShowPreview] = useState(false);
  const [migrating, setMigrating] = useState(false);
  const migrateToSeed = async () => {
    if (!window.confirm("Migrer cet article vers le fichier seed_seo_pages.py ?\n\nProchaines étapes :\n1. Cliquer 'Save to GitHub' dans Emergent\n2. Cliquer 'Deploy'\n→ Article live en production en ~30 secondes.")) return;
    setMigrating(true);
    try {
      const r = await axios.post(`${API}/admin/editorial/articles/${articleId}/migrate-to-seed`, {
        cta_type: article.cta_type || 'dossier_express',
        cta_label: article.cta_label || 'Analyser mon dossier maintenant',
        intention: article.intention || '',
        priority: article.priority || 'p1',
      }, cfg);
      toast.success(`✅ Article migré vers le seed (${r.data.slug})`);
      window.alert("Migration réussie !\n\n1. Cliquez 'Save to GitHub' dans Emergent\n2. Puis 'Deploy'\n\nL'article sera live à :\nhttps://strategie-expertise-sante.fr/guide/" + r.data.slug);
      load();
    } catch (e) { toast.error(e?.response?.data?.detail || "Erreur migration"); }
    finally { setMigrating(false); }
  };

  if (loading || !article) return <div className="flex items-center justify-center py-10"><Loader2 className="w-5 h-5 animate-spin mr-2" /> Chargement…</div>;

  const flags = article.red_flags || [];
  const unvalidated = flags.filter(f => !f.validated);
  const canPublish = article.content && unvalidated.length === 0 && article.status !== 'published';

  return (
    <div className="space-y-4" data-testid="editor-view-root">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <Button variant="outline" size="sm" onClick={onBack} data-testid="editor-back">← Retour</Button>
        <div className="flex items-center gap-2 flex-wrap">
          {article.status === 'published' && (
            <a href={`/guide/${article.slug}`} target="_blank" rel="noopener noreferrer" className="text-xs text-[#C9A84C] underline inline-flex items-center gap-1">
              <ExternalLink className="w-3 h-3" /> Voir en ligne
            </a>
          )}
          {article.structured_content && (
            <Button variant="outline" size="sm" onClick={() => setShowPreview(true)} data-testid="editor-preview-btn" className="border-[#C9A84C]/30">
              <Eye className="w-3.5 h-3.5 mr-1.5" /> Aperçu Web
            </Button>
          )}
          {article.status !== 'archived' && (
            <>
              <Button variant="outline" size="sm" onClick={changeTopic} data-testid="editor-change-topic" className="border-amber-300 text-amber-700 hover:bg-amber-50">
                <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Changer de sujet
              </Button>
              <Button variant="outline" size="sm" onClick={archive} data-testid="editor-archive">
                <Archive className="w-3.5 h-3.5 mr-1.5" /> Archiver
              </Button>
              <Button variant="outline" size="sm" onClick={hardDelete} data-testid="editor-hard-delete" className="border-red-300 text-red-700 hover:bg-red-50">
                <Trash2 className="w-3.5 h-3.5 mr-1.5" /> Supprimer
              </Button>
            </>
          )}
          <Button onClick={publish} disabled={!canPublish} className="bg-[#C9A84C] hover:bg-[#B89640] text-[#0a0a08] font-semibold" data-testid="editor-publish">
            <Send className="w-3.5 h-3.5 mr-1.5" /> Publier (preview){unvalidated.length > 0 ? ` (${unvalidated.length} à valider)` : ''}
          </Button>
          {article.structured_content && unvalidated.length === 0 && !article.migrated_to_seed && (
            <Button onClick={migrateToSeed} disabled={migrating} className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold" data-testid="editor-migrate-seed">
              {migrating ? <><Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" /> Migration…</> : <><GitBranch className="w-3.5 h-3.5 mr-1.5" /> Migrer vers production</>}
            </Button>
          )}
          {article.migrated_to_seed && (
            <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">
              <GitBranch className="w-3 h-3 mr-1" /> Migré → Save to GitHub + Deploy
            </Badge>
          )}
        </div>
      </div>

      <h2 className="text-xl font-semibold font-serif">{article.title}</h2>

      <Tabs defaultValue="content" data-testid="editor-tabs">
        <TabsList>
          <TabsTrigger value="content" data-testid="tab-content">📝 Brouillon</TabsTrigger>
          <TabsTrigger value="structured" data-testid="tab-structured">
            <Layers className="w-3.5 h-3.5 mr-1" /> Structurer
            {article.structured_content && <Badge className="ml-1 bg-emerald-100 text-emerald-800 border-emerald-200 text-[10px]">✓</Badge>}
          </TabsTrigger>
          <TabsTrigger value="flags" data-testid="tab-flags">
            <AlertTriangle className="w-3.5 h-3.5 mr-1" /> À valider {unvalidated.length > 0 && <Badge className="ml-1 bg-red-100 text-red-800 border-red-200 text-[10px]">{unvalidated.length}</Badge>}
          </TabsTrigger>
          <TabsTrigger value="meta" data-testid="tab-meta">⚙️ Méta</TabsTrigger>
          <TabsTrigger value="perf" data-testid="tab-perf"><BarChart3 className="w-3.5 h-3.5 mr-1" /> Perf</TabsTrigger>
        </TabsList>

        <TabsContent value="content" className="space-y-3">
          {!article.plan || article.plan.length === 0 ? (
            <Button onClick={generatePlan} disabled={aiBusy} className="bg-[#C9A84C] hover:bg-[#B89640] text-[#0a0a08]" data-testid="generate-plan-btn">
              {aiBusy ? <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Génération…</> : <><Sparkles className="w-4 h-4 mr-2" /> Étape 1 — Générer le plan</>}
            </Button>
          ) : !article.content ? (
            <Button onClick={generateDraft} disabled={aiBusy} className="bg-[#C9A84C] hover:bg-[#B89640] text-[#0a0a08]" data-testid="generate-draft-btn">
              {aiBusy ? <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Rédaction IA en cours…</> : <><Sparkles className="w-4 h-4 mr-2" /> Étape 2 — Générer le brouillon</>}
            </Button>
          ) : null}

          {article.plan && article.plan.length > 0 && (
            <Card data-testid="plan-display">
              <CardHeader><CardTitle className="text-sm">Plan généré ({article.plan.length} sections + {article.faq?.length || 0} FAQ)</CardTitle></CardHeader>
              <CardContent>
                <ol className="text-xs space-y-1 list-decimal list-inside text-foreground/80">
                  {article.plan.map((s, i) => <li key={i}>{s.h2}</li>)}
                </ol>
              </CardContent>
            </Card>
          )}

          {article.content && (
            <div data-testid="content-editor">
              <p className="text-[11px] text-muted-foreground mb-1.5">
                Éditer librement. Auto-save sur clic du bouton « Sauvegarder ». Markdown supporté.
              </p>
              <Textarea
                value={article.content}
                onChange={(e) => setArticle({ ...article, content: e.target.value })}
                rows={28}
                className="font-mono text-xs"
                data-testid="content-textarea"
              />
              <div className="flex justify-end mt-2">
                <Button size="sm" variant="outline" onClick={() => saveContent(article.content)} data-testid="save-content-btn">
                  💾 Sauvegarder &amp; rescanner
                </Button>
              </div>
            </div>
          )}
        </TabsContent>

        <TabsContent value="structured" data-testid="structured-tab-panel" className="space-y-3">
          {!article.content ? (
            <p className="text-sm text-muted-foreground italic mt-4">
              Générez d'abord le brouillon (onglet « Brouillon ») avant de structurer.
            </p>
          ) : !article.structured_content ? (
            <div className="rounded-xl border border-[#C9A84C]/20 bg-amber-50/30 p-5">
              <p className="text-sm text-foreground/80 mb-3">
                <strong>Étape 3 — Structurer pour publication.</strong> L'IA va transformer le brouillon markdown en blocs prêts à publier (réponse rapide, contexte, blocages, erreurs, stratégie, orientation, FAQ, maillage). Le rendu sera <em>identique</em> aux pages publiées.
              </p>
              <Button onClick={generateStructure} disabled={structuring} className="bg-[#C9A84C] hover:bg-[#B89640] text-[#0a0a08]" data-testid="generate-structure-btn">
                {structuring ? <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Structuration…</> : <><Layers className="w-4 h-4 mr-2" /> Générer la structure publiable</>}
              </Button>
            </div>
          ) : (
            <StructuredEditor
              structured={article.structured_content}
              onChange={(s) => setArticle({ ...article, structured_content: s })}
              onSave={saveStructured}
              onRegenerate={generateStructure}
              regenerating={structuring}
            />
          )}
        </TabsContent>


        <TabsContent value="flags" data-testid="flags-tab-panel">
          {flags.length === 0 ? (
            <p className="text-sm text-muted-foreground italic mt-4">Aucun drapeau à valider. (Générez d'abord le brouillon.)</p>
          ) : (
            <div className="space-y-2 mt-2">
              <div className="flex justify-between items-center">
                <p className="text-xs text-muted-foreground">{flags.length} drapeau(x) — {unvalidated.length} non validés</p>
                {unvalidated.length === 0 && (
                  <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200"><CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Prêt à publier</Badge>
                )}
              </div>
              {flags.map(f => (
                <div key={f.id} className={`p-3 rounded-lg border ${f.validated ? 'bg-emerald-50/50 border-emerald-200' : 'bg-card'}`} data-testid={`flag-${f.id}`}>
                  <div className="flex items-start justify-between gap-3 flex-wrap">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-1">
                        <Badge variant="outline" className={`text-[10px] ${flagSeverityColor(f.severity)}`}>{flagTypeLabel[f.type] || f.type}</Badge>
                        {f.validated && <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200 text-[10px]"><CheckCircle2 className="w-3 h-3 mr-1" /> Validé</Badge>}
                      </div>
                      <p className="text-xs font-semibold text-foreground"><code className="bg-muted px-1.5 py-0.5 rounded text-[11px]">{f.value}</code></p>
                      <p className="text-[10px] text-muted-foreground mt-1 italic">…{f.context}…</p>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      <a href={verifyUrl(f)} target="_blank" rel="noopener noreferrer">
                        <Button size="sm" variant="outline" data-testid={`verify-${f.id}`}><Eye className="w-3.5 h-3.5 mr-1" /> Vérifier</Button>
                      </a>
                      {!f.validated ? (
                        <Button size="sm" onClick={() => validateFlag(f.id, true)} className="bg-emerald-600 hover:bg-emerald-700 text-white" data-testid={`validate-${f.id}`}>
                          <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Valider
                        </Button>
                      ) : (
                        <Button size="sm" variant="outline" onClick={() => validateFlag(f.id, false)} data-testid={`unvalidate-${f.id}`}>Annuler</Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="meta" data-testid="meta-tab-panel">
          <div className="space-y-3 mt-2">
            <div>
              <label className="text-xs font-medium">Titre H1</label>
              <Input value={article.title} onChange={(e) => setArticle({ ...article, title: e.target.value })} onBlur={() => axios.post(`${API}/admin/editorial/articles/${articleId}/save`, { title: article.title }, cfg)} data-testid="meta-title" />
            </div>
            <div>
              <label className="text-xs font-medium">Slug URL</label>
              <Input value={article.slug || ''} onChange={(e) => setArticle({ ...article, slug: e.target.value })} onBlur={() => axios.post(`${API}/admin/editorial/articles/${articleId}/save`, { slug: article.slug }, cfg)} data-testid="meta-slug" />
              <p className="text-[10px] text-muted-foreground mt-0.5">URL finale : /guide/{article.slug || '...'}</p>
            </div>
            <div>
              <label className="text-xs font-medium">Méta-description (150-160 car.)</label>
              <Textarea value={article.meta_description || ''} onChange={(e) => setArticle({ ...article, meta_description: e.target.value })} onBlur={() => axios.post(`${API}/admin/editorial/articles/${articleId}/save`, { meta_description: article.meta_description }, cfg)} rows={3} maxLength={170} data-testid="meta-description" />
              <p className="text-[10px] text-muted-foreground mt-0.5">{(article.meta_description || '').length}/160</p>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="perf" data-testid="perf-tab-panel">
          <PerfPanel article={article} cfg={cfg} onUpdate={load} />
        </TabsContent>
      </Tabs>

      {/* PREVIEW MODAL — pixel-perfect mirror of /guide/{slug} */}
      {showPreview && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-start justify-center p-4 overflow-y-auto" onClick={() => setShowPreview(false)} data-testid="preview-modal-overlay">
          <div className="relative my-8 bg-background rounded-2xl shadow-2xl w-full max-w-4xl" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-background border-b border-border/50 rounded-t-2xl px-6 py-3 flex items-center justify-between z-10">
              <div className="flex items-center gap-3">
                <Eye className="w-4 h-4 text-[#C9A84C]" />
                <p className="text-sm font-semibold">Aperçu Web — rendu identique à la page publiée</p>
                <Badge variant="outline" className="text-[10px]">PREVIEW</Badge>
              </div>
              <Button variant="outline" size="sm" onClick={() => setShowPreview(false)} data-testid="preview-modal-close">Fermer</Button>
            </div>
            <div className="px-6 py-8">
              <GuidePreviewBody
                page={{
                  title: article.title,
                  meta_description: article.meta_description,
                  cta_type: article.cta_type || 'dossier_express',
                  cta_label: article.cta_label || 'Analyser mon dossier maintenant',
                  content: article.structured_content || {},
                }}
                slug={article.slug}
                currentYear={new Date().getFullYear()}
                onCtaClick={() => {}}
                isPreview={true}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const PerfPanel = ({ article, cfg, onUpdate }) => {
  const [period, setPeriod] = useState(new Date().toISOString().slice(0, 7));
  const [imp, setImp] = useState(''); const [clicks, setClicks] = useState(''); const [pos, setPos] = useState('');

  const submit = async () => {
    if (!imp || !clicks || !pos) { toast.error("Remplissez les 3 champs"); return; }
    try {
      await axios.post(`${API}/admin/editorial/articles/${article.id}/perf`, {
        period_label: period, impressions: parseInt(imp), clicks: parseInt(clicks), avg_position: parseFloat(pos),
      }, cfg);
      toast.success("Chiffres ajoutés");
      setImp(''); setClicks(''); setPos(''); onUpdate();
    } catch { toast.error("Erreur"); }
  };

  return (
    <div className="space-y-4 mt-2" data-testid="perf-panel">
      <Card>
        <CardHeader><CardTitle className="text-sm">Saisir les chiffres Search Console (mensuel)</CardTitle></CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-5 gap-2">
            <div><label className="text-[10px]">Période</label><Input value={period} onChange={e => setPeriod(e.target.value)} placeholder="2026-05" data-testid="perf-period" /></div>
            <div><label className="text-[10px]">Impressions</label><Input type="number" value={imp} onChange={e => setImp(e.target.value)} data-testid="perf-imp" /></div>
            <div><label className="text-[10px]">Clics</label><Input type="number" value={clicks} onChange={e => setClicks(e.target.value)} data-testid="perf-clicks" /></div>
            <div><label className="text-[10px]">Position moy.</label><Input type="number" step="0.1" value={pos} onChange={e => setPos(e.target.value)} data-testid="perf-pos" /></div>
            <div className="flex items-end"><Button onClick={submit} className="w-full" data-testid="perf-save">Sauvegarder</Button></div>
          </div>
        </CardContent>
      </Card>

      {article.perf && article.perf.length > 0 ? (
        <Card>
          <CardHeader><CardTitle className="text-sm">Historique ({article.perf.length} périodes)</CardTitle></CardHeader>
          <CardContent>
            <table className="w-full text-xs">
              <thead><tr className="text-left text-muted-foreground border-b"><th className="py-1.5">Période</th><th>Imp.</th><th>Clics</th><th>CTR</th><th>Pos. moy.</th></tr></thead>
              <tbody>
                {article.perf.map((p, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="py-1.5 font-medium">{p.period_label}</td><td>{p.impressions}</td><td>{p.clicks}</td><td>{p.ctr}%</td><td>{p.avg_position}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      ) : (
        <p className="text-xs text-muted-foreground italic">Aucun chiffre saisi pour le moment.</p>
      )}
    </div>
  );
};


// ===================== SETTINGS VIEW =====================

const SettingsView = ({ config, onBack, cfg }) => {
  const [local, setLocal] = useState(config || { rag_live_web_enabled: false, dynamic_topics_enabled: false });
  const [legalRefs, setLegalRefs] = useState([]);
  const [loadingRefs, setLoadingRefs] = useState(false);

  useEffect(() => {
    setLoadingRefs(true);
    axios.get(`${API}/admin/editorial/legal-refs`, cfg).then(r => setLegalRefs(r.data.items)).finally(() => setLoadingRefs(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const toggle = async (key, val) => {
    try {
      await axios.post(`${API}/admin/editorial/config`, { [key]: val }, cfg);
      setLocal({ ...local, [key]: val });
      toast.success(val ? "Activé" : "Désactivé");
    } catch { toast.error("Erreur"); }
  };

  return (
    <div className="space-y-5" data-testid="editorial-settings-root">
      <Button variant="outline" size="sm" onClick={onBack} data-testid="settings-back">← Retour Studio</Button>

      <Card>
        <CardHeader><CardTitle className="text-sm">Modules avancés (mode veille)</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <ToggleRow label="RAG live web (Légifrance / Ameli temps réel)" desc="Active la vérification temps réel des sources officielles. Désactivé par défaut (~10-30€/mois en API si activé)." checked={local.rag_live_web_enabled} onChange={(v) => toggle('rag_live_web_enabled', v)} testid="toggle-rag" />
          <ToggleRow label="Génération dynamique de sujets IA" desc="L'IA propose des sujets sur-mesure selon vos performances Search Console. Désactivé par défaut (~5-15€/mois en API si activé)." checked={local.dynamic_topics_enabled} onChange={(v) => toggle('dynamic_topics_enabled', v)} testid="toggle-dynamic" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">Base de référence légale ({legalRefs.length} entrées)</CardTitle></CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground mb-3">L'IA n'a le droit de citer QUE ces références. Tout autre élément est marqué « À VÉRIFIER » dans les drapeaux rouges.</p>
          {loadingRefs ? <Loader2 className="w-4 h-4 animate-spin" /> : (
            <div className="max-h-[400px] overflow-y-auto space-y-1.5">
              {legalRefs.map((r, i) => (
                <div key={i} className="text-xs p-2 rounded border bg-card" data-testid={`ref-${r.ref_key}`}>
                  <div className="flex items-center gap-1.5 mb-1">
                    <Badge variant="outline" className="text-[10px]">{r.kind}</Badge>
                    <span className="font-semibold">{r.label}</span>
                  </div>
                  <p className="text-[11px] text-muted-foreground">{r.text}</p>
                  <a href={r.source} target="_blank" rel="noopener noreferrer" className="text-[10px] text-[#C9A84C] underline">Source</a>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

const ToggleRow = ({ label, desc, checked, onChange, testid }) => (
  <div className="flex items-start justify-between gap-4 p-3 rounded-lg border bg-card">
    <div className="flex-1 min-w-0">
      <p className="text-sm font-medium">{label}</p>
      <p className="text-[11px] text-muted-foreground mt-0.5">{desc}</p>
    </div>
    <button onClick={() => onChange(!checked)} className={`relative inline-flex h-6 w-11 flex-shrink-0 rounded-full transition-colors ${checked ? 'bg-[#C9A84C]' : 'bg-slate-300'}`} data-testid={testid}>
      <span className={`inline-block h-5 w-5 rounded-full bg-white shadow transform transition-transform ${checked ? 'translate-x-5' : 'translate-x-0.5'} mt-0.5`} />
    </button>
  </div>
);


// ===================== STRUCTURED EDITOR (Phase 2) =====================

const StructuredEditor = ({ structured, onChange, onSave, onRegenerate, regenerating }) => {
  const [s, setS] = useState(structured);

  useEffect(() => { setS(structured); }, [structured]);

  const update = (patch) => {
    const next = { ...s, ...patch };
    setS(next);
    onChange(next);
  };

  const updateArrayItem = (key, idx, value) => {
    const arr = [...(s[key] || [])];
    arr[idx] = value;
    update({ [key]: arr });
  };

  const addArrayItem = (key, defaultVal = '') => {
    update({ [key]: [...(s[key] || []), defaultVal] });
  };

  const removeArrayItem = (key, idx) => {
    const arr = [...(s[key] || [])];
    arr.splice(idx, 1);
    update({ [key]: arr });
  };

  const updateMaillage = (idx, field, value) => {
    const arr = [...(s.maillage || [])];
    arr[idx] = { ...arr[idx], [field]: value };
    update({ maillage: arr });
  };

  const updateFaq = (idx, field, value) => {
    const arr = [...(s.faq || [])];
    arr[idx] = { ...arr[idx], [field]: value };
    update({ faq: arr });
  };

  return (
    <div className="space-y-4 mt-2" data-testid="structured-editor">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          Éditez chaque bloc. L'aperçu Web (bouton en haut) affiche exactement ce qui sera publié.
        </p>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={onRegenerate} disabled={regenerating} data-testid="regenerate-structure-btn">
            {regenerating ? <><Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" /> Régénération…</> : <><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Régénérer</>}
          </Button>
          <Button size="sm" variant="outline" onClick={() => onSave(s)} data-testid="save-structured-btn">💾 Sauvegarder</Button>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-sm">Réponse rapide (haut de page)</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <Input value={s.reponse_rapide_titre || ''} onChange={(e) => update({ reponse_rapide_titre: e.target.value })} placeholder="Titre court de la réponse" data-testid="structured-rr-titre" />
          <Textarea value={s.reponse_rapide || ''} onChange={(e) => update({ reponse_rapide: e.target.value })} rows={5} placeholder="Réponse synthétique 4-7 phrases" data-testid="structured-rr-text" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">Contexte et situation</CardTitle></CardHeader>
        <CardContent>
          <Textarea value={s.contexte || ''} onChange={(e) => update({ contexte: e.target.value })} rows={5} data-testid="structured-contexte" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">Limites des textes officiels</CardTitle></CardHeader>
        <CardContent>
          <Textarea value={s.limites || ''} onChange={(e) => update({ limites: e.target.value })} rows={4} data-testid="structured-limites" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center justify-between">
            <span>Blocages réels ({(s.blocages || []).length})</span>
            <Button size="sm" variant="outline" onClick={() => addArrayItem('blocages')}><Plus className="w-3 h-3 mr-1" /> Ajouter</Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {(s.blocages || []).map((b, i) => (
            <div key={i} className="flex gap-2 items-start">
              <span className="text-xs font-bold w-5 mt-2">{i + 1}.</span>
              <Textarea value={b} onChange={(e) => updateArrayItem('blocages', i, e.target.value)} rows={2} className="flex-1" data-testid={`structured-blocage-${i}`} />
              <Button size="sm" variant="ghost" onClick={() => removeArrayItem('blocages', i)}><Trash2 className="w-3.5 h-3.5 text-red-500" /></Button>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center justify-between">
            <span>Erreurs fréquentes ({(s.erreurs || []).length})</span>
            <Button size="sm" variant="outline" onClick={() => addArrayItem('erreurs')}><Plus className="w-3 h-3 mr-1" /> Ajouter</Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {(s.erreurs || []).map((b, i) => (
            <div key={i} className="flex gap-2 items-start">
              <span className="text-xs font-bold w-5 mt-2">{i + 1}.</span>
              <Textarea value={b} onChange={(e) => updateArrayItem('erreurs', i, e.target.value)} rows={2} className="flex-1" data-testid={`structured-erreur-${i}`} />
              <Button size="sm" variant="ghost" onClick={() => removeArrayItem('erreurs', i)}><Trash2 className="w-3.5 h-3.5 text-red-500" /></Button>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">Lecture stratégique</CardTitle></CardHeader>
        <CardContent>
          <Textarea value={s.strategie || ''} onChange={(e) => update({ strategie: e.target.value })} rows={6} data-testid="structured-strategie" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center justify-between">
            <span>Orientation concrète ({(s.orientation || []).length})</span>
            <Button size="sm" variant="outline" onClick={() => addArrayItem('orientation')}><Plus className="w-3 h-3 mr-1" /> Ajouter</Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {(s.orientation || []).map((b, i) => (
            <div key={i} className="flex gap-2 items-start">
              <span className="text-xs font-bold w-5 mt-2">{i + 1}.</span>
              <Textarea value={b} onChange={(e) => updateArrayItem('orientation', i, e.target.value)} rows={2} className="flex-1" data-testid={`structured-orientation-${i}`} />
              <Button size="sm" variant="ghost" onClick={() => removeArrayItem('orientation', i)}><Trash2 className="w-3.5 h-3.5 text-red-500" /></Button>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">Réassurance</CardTitle></CardHeader>
        <CardContent>
          <Textarea value={s.reassurance || ''} onChange={(e) => update({ reassurance: e.target.value })} rows={4} data-testid="structured-reassurance" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center justify-between">
            <span>Maillage interne ({(s.maillage || []).length})</span>
            <Button size="sm" variant="outline" onClick={() => update({ maillage: [...(s.maillage || []), { slug: '', text: '' }] })}><Plus className="w-3 h-3 mr-1" /> Ajouter</Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {(s.maillage || []).map((m, i) => (
            <div key={i} className="grid grid-cols-[1fr_2fr_auto] gap-2 items-center">
              <Input value={m.slug} onChange={(e) => updateMaillage(i, 'slug', e.target.value)} placeholder="slug-guide" data-testid={`structured-maillage-slug-${i}`} />
              <Input value={m.text} onChange={(e) => updateMaillage(i, 'text', e.target.value)} placeholder="Titre humain" data-testid={`structured-maillage-text-${i}`} />
              <Button size="sm" variant="ghost" onClick={() => removeArrayItem('maillage', i)}><Trash2 className="w-3.5 h-3.5 text-red-500" /></Button>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center justify-between">
            <span>FAQ ({(s.faq || []).length})</span>
            <Button size="sm" variant="outline" onClick={() => update({ faq: [...(s.faq || []), { question: '', answer: '' }] })}><Plus className="w-3 h-3 mr-1" /> Ajouter</Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {(s.faq || []).map((q, i) => (
            <div key={i} className="space-y-1.5 p-3 rounded-lg border border-border/50">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold">Q{i + 1}.</span>
                <Input value={q.question} onChange={(e) => updateFaq(i, 'question', e.target.value)} placeholder="Question" className="flex-1" data-testid={`structured-faq-q-${i}`} />
                <Button size="sm" variant="ghost" onClick={() => removeArrayItem('faq', i)}><Trash2 className="w-3.5 h-3.5 text-red-500" /></Button>
              </div>
              <Textarea value={q.answer} onChange={(e) => updateFaq(i, 'answer', e.target.value)} rows={3} placeholder="Réponse" data-testid={`structured-faq-a-${i}`} />
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};


export default AdminEditorialStudio;
