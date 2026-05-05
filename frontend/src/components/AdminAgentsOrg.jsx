import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Crown, Phone, Sparkles, FileSearch, ClipboardList, PenTool, ShieldAlert, Layers, Copy, X, Download, Loader2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ICONS = {
  strate: Phone,
  strategiia: Sparkles,
  dossier_express: FileSearch,
  editorial_planner: ClipboardList,
  editorial_writer: PenTool,
  editorial_critic: ShieldAlert,
  editorial_structurer: Layers,
};

const COLORS = {
  strate: { bg: 'bg-blue-50', border: 'border-blue-200', accent: 'text-blue-700', dot: 'bg-blue-500' },
  strategiia: { bg: 'bg-amber-50', border: 'border-amber-200', accent: 'text-amber-700', dot: 'bg-amber-500' },
  dossier_express: { bg: 'bg-indigo-50', border: 'border-indigo-200', accent: 'text-indigo-700', dot: 'bg-indigo-500' },
  editorial_planner: { bg: 'bg-emerald-50', border: 'border-emerald-200', accent: 'text-emerald-700', dot: 'bg-emerald-500' },
  editorial_writer: { bg: 'bg-emerald-50', border: 'border-emerald-200', accent: 'text-emerald-700', dot: 'bg-emerald-500' },
  editorial_critic: { bg: 'bg-red-50', border: 'border-red-200', accent: 'text-red-700', dot: 'bg-red-500' },
  editorial_structurer: { bg: 'bg-emerald-50', border: 'border-emerald-200', accent: 'text-emerald-700', dot: 'bg-emerald-500' },
};

const AgentCard = ({ agent, onClick }) => {
  const Icon = ICONS[agent.id] || PenTool;
  const c = COLORS[agent.id] || COLORS.editorial_writer;
  return (
    <button
      onClick={onClick}
      className={`group text-left rounded-xl border-2 ${c.border} ${c.bg} p-4 hover:shadow-md hover:-translate-y-0.5 transition-all w-full`}
      data-testid={`agent-card-${agent.id}`}
    >
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 rounded-lg ${c.bg} ${c.border} border flex items-center justify-center shrink-0`}>
          <Icon className={`w-5 h-5 ${c.accent}`} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm text-foreground">{agent.name}</h3>
          <p className={`text-[11px] ${c.accent} font-medium mb-1`}>{agent.role}</p>
          <p className="text-xs text-foreground/70 line-clamp-2">{agent.mission}</p>
        </div>
      </div>
    </button>
  );
};

const AgentDetailModal = ({ agent, onClose }) => {
  if (!agent) return null;
  const Icon = ICONS[agent.id] || PenTool;
  const c = COLORS[agent.id] || COLORS.editorial_writer;

  const copyPrompt = () => {
    navigator.clipboard.writeText(agent.prompt || '');
    toast.success("Prompt copié dans le presse-papier");
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 flex items-start justify-center p-4 overflow-y-auto" onClick={onClose} data-testid="agent-modal-overlay">
      <div className="relative my-8 bg-background rounded-2xl shadow-2xl w-full max-w-3xl" onClick={(e) => e.stopPropagation()}>
        <div className={`sticky top-0 ${c.bg} border-b ${c.border} rounded-t-2xl px-6 py-4 flex items-center justify-between z-10`}>
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg bg-white ${c.border} border flex items-center justify-center`}>
              <Icon className={`w-5 h-5 ${c.accent}`} />
            </div>
            <div>
              <h3 className="font-semibold text-base">{agent.name}</h3>
              <p className={`text-xs ${c.accent}`}>{agent.role}</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} data-testid="agent-modal-close"><X className="w-4 h-4" /></Button>
        </div>

        <div className="p-6 space-y-5">
          <section>
            <h4 className="text-xs uppercase tracking-wider text-muted-foreground mb-1.5 font-semibold">Mission</h4>
            <p className="text-sm text-foreground/80 leading-relaxed">{agent.mission}</p>
          </section>

          <section>
            <h4 className="text-xs uppercase tracking-wider text-muted-foreground mb-1.5 font-semibold">Modèle utilisé</h4>
            <Badge variant="outline" className="text-xs">{agent.model}</Badge>
          </section>

          <section>
            <h4 className="text-xs uppercase tracking-wider text-muted-foreground mb-2 font-semibold">Garde-fous actifs ({agent.guardrails?.length || 0})</h4>
            <ul className="space-y-1.5">
              {(agent.guardrails || []).map((g, i) => (
                <li key={i} className="text-xs text-foreground/80 flex items-start gap-2">
                  <span className="text-emerald-600 mt-0.5">✓</span>
                  <span>{g}</span>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">Prompt système (lecture seule)</h4>
              <Button variant="outline" size="sm" onClick={copyPrompt} data-testid="agent-modal-copy-prompt">
                <Copy className="w-3.5 h-3.5 mr-1.5" /> Copier
              </Button>
            </div>
            <pre className="text-[11px] bg-muted/50 border border-border/60 rounded-lg p-3 overflow-x-auto whitespace-pre-wrap max-h-[400px] overflow-y-auto" data-testid="agent-modal-prompt">
              {agent.prompt || '(prompt non disponible)'}
            </pre>
            <p className="text-[10px] text-muted-foreground mt-2">
              Source : <code className="bg-muted/50 px-1 rounded">{agent.file_path}</code> → <code className="bg-muted/50 px-1 rounded">{agent.prompt_var}</code>
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export const AdminAgentsOrg = () => {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [selected, setSelected] = useState(null);
  const [exporting, setExporting] = useState(false);
  const cfg = { headers: { Authorization: `Bearer ${token}` } };

  useEffect(() => {
    axios.get(`${API}/admin/agents/registry`, cfg)
      .then(r => setData(r.data))
      .catch(() => toast.error("Erreur chargement organigramme"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const exportPdf = async () => {
    setExporting(true);
    try {
      const r = await axios.get(`${API}/admin/agents/registry/pdf`, { ...cfg, responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([r.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      a.download = `organigramme-ia-ses-${today}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.success("Organigramme exporté en PDF");
    } catch {
      toast.error("Erreur lors de l'export PDF");
    } finally {
      setExporting(false);
    }
  };

  if (!data) return <p className="text-sm text-muted-foreground">Chargement de l'organigramme…</p>;

  // Group agents
  const strate = data.agents.find(a => a.id === 'strate');
  const strategiia = data.agents.find(a => a.id === 'strategiia');
  const dossierExpress = data.agents.find(a => a.id === 'dossier_express');
  const editorialAgents = data.agents.filter(a => a.id.startsWith('editorial_'));

  return (
    <div className="space-y-6" data-testid="admin-agents-org">
      <Card className="border-[#C9A84C]/30 bg-gradient-to-br from-[#FAF8F3] to-white">
        <CardHeader><CardTitle className="text-lg flex items-center gap-2"><Crown className="w-5 h-5 text-[#C9A84C]" /> Organigramme IA</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <p className="text-sm text-foreground/70 flex-1">
              Visualisez l'ensemble de votre équipe d'agents IA, leurs rôles et leurs garde-fous.
              Cliquez sur une carte pour consulter le prompt système complet (lecture seule).
            </p>
            <Button
              onClick={exportPdf}
              disabled={exporting}
              size="sm"
              className="bg-[#1a1a2e] text-white hover:bg-[#2a2a3e] gap-2 shrink-0"
              data-testid="agents-org-export-pdf"
            >
              {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              Exporter en PDF
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* PDG niveau 0 */}
      <div className="flex justify-center">
        <div className="rounded-xl border-2 border-[#C9A84C] bg-gradient-to-br from-[#1a1a2e] to-[#0a0a14] text-white p-5 max-w-md text-center shadow-lg" data-testid="ceo-card">
          <Crown className="w-8 h-8 text-[#C9A84C] mx-auto mb-2" />
          <h3 className="font-semibold text-base">{data.ceo.name}</h3>
          <p className="text-xs text-[#C9A84C] mt-1">{data.ceo.role}</p>
        </div>
      </div>

      {/* Connector visual */}
      <div className="flex justify-center"><div className="w-px h-6 bg-[#C9A84C]/40" /></div>

      {/* Agents niveau 1 */}
      <div>
        <h4 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 font-semibold">Agents en contact direct visiteur / client</h4>
        <div className="grid sm:grid-cols-3 gap-3">
          {strate && <AgentCard agent={strate} onClick={() => setSelected(strate)} />}
          {strategiia && <AgentCard agent={strategiia} onClick={() => setSelected(strategiia)} />}
          {dossierExpress && <AgentCard agent={dossierExpress} onClick={() => setSelected(dossierExpress)} />}
        </div>
      </div>

      {/* Editorial team */}
      {editorialAgents.length > 0 && (
        <div>
          <h4 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 font-semibold">Équipe éditoriale (Studio SEO)</h4>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {editorialAgents.map(a => <AgentCard key={a.id} agent={a} onClick={() => setSelected(a)} />)}
          </div>
        </div>
      )}

      <AgentDetailModal agent={selected} onClose={() => setSelected(null)} />
    </div>
  );
};

export default AdminAgentsOrg;
