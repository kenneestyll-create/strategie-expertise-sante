import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Loader2, Plus, Search, Download, FileSearch, Copy, X, ChevronLeft, ChevronRight, Camera } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const PAGE_SIZE = 10;

const SourceBadge = ({ source }) => {
  if (source === 'auto_startup') return <Badge variant="outline" className="text-xs gap-1"><Camera className="w-3 h-3" /> Auto démarrage</Badge>;
  return <Badge className="text-xs gap-1 bg-[#1a1a2e] hover:bg-[#1a1a2e]"><Plus className="w-3 h-3" /> Manuel</Badge>;
};

const formatDate = (iso) => {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch { return iso.slice(0, 16).replace('T', ' '); }
};

const VersionDetailModal = ({ version, onClose }) => {
  if (!version) return null;
  const state = version.state || {};

  const copyConfig = () => {
    const text = JSON.stringify({
      version: version.seq,
      created_at: version.created_at,
      hash: version.hash,
      agents: state.agents,
      red_flag_patterns: state.red_flag_patterns,
      workflow_config: state.workflow_config,
      legal_refs_count: state.legal_refs_count,
    }, null, 2);
    navigator.clipboard.writeText(text);
    toast.success('Configuration copiée — collez-la dans une demande à l\'agent dev pour restauration manuelle');
  };

  return (
    <Dialog open={!!version} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-4xl max-h-[85vh] overflow-y-auto" data-testid="version-detail-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileSearch className="w-5 h-5 text-[#C9A84C]" />
            Version v{version.seq} — {formatDate(version.created_at)}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 mt-2">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div><span className="text-muted-foreground">Auteur :</span> <span className="font-medium">{version.created_by}</span></div>
            <div><span className="text-muted-foreground">Source :</span> <SourceBadge source={version.source} /></div>
            <div className="col-span-2"><span className="text-muted-foreground">Note :</span> <span className="italic">{version.notes || '(aucune note)'}</span></div>
            <div className="col-span-2 text-xs"><span className="text-muted-foreground">Empreinte SHA-256 :</span> <code className="bg-muted/50 px-1.5 py-0.5 rounded text-[10px] break-all">{version.hash}</code></div>
          </div>

          <section>
            <h4 className="text-xs uppercase tracking-wider text-muted-foreground mb-2 font-semibold">Modifications majeures</h4>
            <ul className="space-y-1.5 bg-muted/30 rounded-lg p-3">
              {(version.changes_summary || []).map((c, i) => (
                <li key={i} className="text-sm flex items-start gap-2"><span className="text-[#C9A84C] mt-0.5">▸</span><span>{c}</span></li>
              ))}
            </ul>
          </section>

          <section>
            <h4 className="text-xs uppercase tracking-wider text-muted-foreground mb-2 font-semibold">Agents IA archivés ({(state.agents || []).length})</h4>
            <div className="space-y-2">
              {(state.agents || []).map((a) => (
                <div key={a.id} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-sm">{a.name}</span>
                    <Badge variant="outline" className="text-[10px]">{a.model}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mb-1.5">{a.role}</p>
                  <details>
                    <summary className="text-xs text-[#C9A84C] cursor-pointer hover:underline">Voir le prompt système ({(a.prompt || '').length} caractères)</summary>
                    <pre className="text-[10px] bg-muted/50 rounded p-2 mt-1.5 max-h-60 overflow-y-auto whitespace-pre-wrap">{a.prompt || '(vide)'}</pre>
                  </details>
                </div>
              ))}
            </div>
          </section>

          <section className="grid sm:grid-cols-2 gap-3">
            <div className="border rounded-lg p-3">
              <h4 className="text-xs uppercase tracking-wider text-muted-foreground mb-1.5 font-semibold">Red Flags ({state.red_flag_count || 0} règles)</h4>
              <ul className="text-xs space-y-1 max-h-40 overflow-y-auto">
                {(state.red_flag_patterns || []).map((p, i) => (
                  <li key={i} className="flex items-start gap-1.5"><Badge variant="outline" className="text-[9px] uppercase">{p.severity}</Badge><span className="text-muted-foreground">{p.kind}</span></li>
                ))}
              </ul>
            </div>
            <div className="border rounded-lg p-3">
              <h4 className="text-xs uppercase tracking-wider text-muted-foreground mb-1.5 font-semibold">Workflow & Base juridique</h4>
              <div className="text-xs space-y-1">
                <div><span className="text-muted-foreground">Références juridiques en base :</span> <span className="font-semibold">{state.legal_refs_count || 0}</span></div>
                {Object.entries(state.workflow_config || {}).map(([k, v]) => (
                  <div key={k}><span className="text-muted-foreground">{k} :</span> <span className="font-mono">{v}</span></div>
                ))}
              </div>
            </div>
          </section>

          <div className="flex flex-col sm:flex-row gap-2 pt-3 border-t">
            <Button onClick={copyConfig} className="gap-2 flex-1" data-testid="version-copy-btn">
              <Copy className="w-4 h-4" /> Copier cette configuration
            </Button>
            <Button variant="outline" onClick={onClose} className="gap-2 sm:w-auto" data-testid="version-close-btn">
              <X className="w-4 h-4" /> Fermer
            </Button>
          </div>
          <p className="text-[11px] text-muted-foreground text-center italic">
            Restauration : copiez la configuration ci-dessus puis demandez à l'agent dev S.E.S de la réinjecter dans le code source. Aucune modification automatique pour préserver l'intégrité Git.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export const AdminAgentsVersions = () => {
  const { token } = useAuth();
  const cfg = { headers: { Authorization: `Bearer ${token}` } };
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [noteInput, setNoteInput] = useState('');
  const [showSnapshotForm, setShowSnapshotForm] = useState(false);
  const [selected, setSelected] = useState(null);

  const fetchVersions = useCallback(async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/admin/agents/versions`, {
        ...cfg,
        params: { page, limit: PAGE_SIZE, q: search || undefined },
      });
      setItems(r.data.items || []);
      setTotal(r.data.total || 0);
    } catch {
      toast.error('Erreur chargement des versions');
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, search]);

  useEffect(() => { fetchVersions(); }, [fetchVersions]);

  const createSnapshot = async () => {
    setCreating(true);
    try {
      const r = await axios.post(`${API}/admin/agents/versions`, { notes: noteInput }, cfg);
      if (r.data.created) {
        toast.success(`Snapshot v${r.data.version.seq} créé`);
        setNoteInput('');
        setShowSnapshotForm(false);
        setPage(1);
        fetchVersions();
      } else {
        toast.info('Aucun changement détecté depuis la dernière version — pas de nouveau snapshot');
      }
    } catch {
      toast.error('Erreur création snapshot');
    } finally {
      setCreating(false);
    }
  };

  const openDetail = async (version_id) => {
    try {
      const r = await axios.get(`${API}/admin/agents/versions/${version_id}`, cfg);
      setSelected(r.data);
    } catch {
      toast.error('Erreur chargement détail version');
    }
  };

  const exportAuditPdf = async () => {
    setExporting(true);
    try {
      const r = await axios.get(`${API}/admin/agents/versions/audit/pdf`, { ...cfg, responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([r.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-ia-ses-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Rapport d\'audit exporté');
    } catch {
      toast.error('Erreur export PDF');
    } finally {
      setExporting(false);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="space-y-5" data-testid="admin-agents-versions">
      <Card className="border-[#C9A84C]/30 bg-gradient-to-br from-[#FAF8F3] to-white">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2"><FileSearch className="w-4 h-4 text-[#C9A84C]" /> Versions & Audit</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-foreground/70 mb-4">
            Historique des évolutions de la configuration IA (prompts, modèles, red flags, base juridique, workflow).
            Snapshot automatique à chaque démarrage si modification détectée. Restauration "copy-only" pour préserver l'intégrité Git.
          </p>
          <div className="flex flex-col sm:flex-row gap-2">
            <Button onClick={() => setShowSnapshotForm(s => !s)} className="gap-2 bg-[#1a1a2e] hover:bg-[#2a2a3e] text-white" data-testid="snapshot-create-btn">
              <Plus className="w-4 h-4" /> Capturer l'état actuel
            </Button>
            <Button onClick={exportAuditPdf} disabled={exporting || total === 0} variant="outline" className="gap-2" data-testid="audit-pdf-btn">
              {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />} Exporter le rapport d'audit
            </Button>
          </div>

          {showSnapshotForm && (
            <div className="mt-3 p-3 border rounded-lg bg-white space-y-2" data-testid="snapshot-form">
              <Textarea
                value={noteInput}
                onChange={(e) => setNoteInput(e.target.value.slice(0, 500))}
                placeholder="Note de modification (optionnel) — ex : 'Ajout du Critic juridique pour réduire les hallucinations'"
                className="text-sm min-h-[70px]"
                data-testid="snapshot-note-input"
              />
              <div className="flex justify-end gap-2">
                <Button variant="ghost" onClick={() => { setShowSnapshotForm(false); setNoteInput(''); }} size="sm">Annuler</Button>
                <Button onClick={createSnapshot} disabled={creating} size="sm" className="gap-1.5" data-testid="snapshot-confirm-btn">
                  {creating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />} Créer le snapshot
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:justify-between">
            <CardTitle className="text-sm">Historique ({total} version{total > 1 ? 's' : ''})</CardTitle>
            <div className="relative w-full sm:w-72">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                placeholder="Filtrer (date YYYY-MM-DD, auteur, note)"
                className="pl-8 h-9 text-xs"
                data-testid="versions-search-input"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-10"><Loader2 className="w-5 h-5 animate-spin text-muted-foreground" /></div>
          ) : items.length === 0 ? (
            <p className="text-center py-8 text-sm text-muted-foreground">Aucune version trouvée</p>
          ) : (
            <div className="space-y-2" data-testid="versions-list">
              {items.map((v) => (
                <button
                  key={v.version_id}
                  onClick={() => openDetail(v.version_id)}
                  className="w-full text-left p-3 rounded-lg border hover:border-[#C9A84C]/50 hover:bg-[#FAF8F3]/50 transition-all"
                  data-testid={`version-item-${v.seq}`}
                >
                  <div className="flex items-start justify-between gap-3 mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm">v{v.seq}</span>
                      <SourceBadge source={v.source} />
                    </div>
                    <span className="text-xs text-muted-foreground whitespace-nowrap">{formatDate(v.created_at)}</span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-1.5">{v.created_by}</p>
                  {v.notes && <p className="text-xs italic text-foreground/70 mb-1.5 line-clamp-1">« {v.notes} »</p>}
                  <ul className="text-[11px] space-y-0.5">
                    {(v.changes_summary || []).slice(0, 3).map((c, i) => (
                      <li key={i} className="flex items-start gap-1.5"><span className="text-[#C9A84C]">▸</span><span className="text-foreground/80">{c}</span></li>
                    ))}
                    {(v.changes_summary || []).length > 3 && (
                      <li className="text-muted-foreground italic">+ {v.changes_summary.length - 3} autre{v.changes_summary.length - 3 > 1 ? 's' : ''}</li>
                    )}
                  </ul>
                </button>
              ))}
            </div>
          )}

          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 pt-3 border-t">
              <Button variant="ghost" size="sm" disabled={page === 1} onClick={() => setPage(p => Math.max(1, p - 1))} className="gap-1" data-testid="versions-prev-page">
                <ChevronLeft className="w-3.5 h-3.5" /> Précédent
              </Button>
              <span className="text-xs text-muted-foreground">Page {page} / {totalPages}</span>
              <Button variant="ghost" size="sm" disabled={page === totalPages} onClick={() => setPage(p => Math.min(totalPages, p + 1))} className="gap-1" data-testid="versions-next-page">
                Suivant <ChevronRight className="w-3.5 h-3.5" />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <VersionDetailModal version={selected} onClose={() => setSelected(null)} />
    </div>
  );
};

export default AdminAgentsVersions;
