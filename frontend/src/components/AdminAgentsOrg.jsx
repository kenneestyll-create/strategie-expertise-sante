import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import {
  Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription,
} from '@/components/ui/sheet';
import {
  Collapsible, CollapsibleContent, CollapsibleTrigger,
} from '@/components/ui/collapsible';
import {
  Crown, Phone, Sparkles, FileSearch, ClipboardList, PenTool, ShieldAlert,
  Layers, Copy, Download, Loader2, History, Lock, ChevronDown, Clapperboard,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { AdminAgentsVersions } from './AdminAgentsVersions';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/* ──────────────────────────────────────────────────────────────────────
   Visual tokens — Stratégie & Expertise Santé charter (or doré + navy)
   Each agent gets an icon + a unified accent colour for the avatar pill.
   ────────────────────────────────────────────────────────────────────── */
const AGENT_META = {
  strate:                { icon: Phone,         accent: '#3b82f6', tint: 'rgba(59,130,246,0.10)' },
  strategiia:            { icon: Sparkles,      accent: '#C9A84C', tint: 'rgba(201,168,76,0.12)' },
  dossier_express:       { icon: FileSearch,    accent: '#6366f1', tint: 'rgba(99,102,241,0.10)' },
  video_factory:         { icon: Clapperboard,  accent: '#f97316', tint: 'rgba(249,115,22,0.10)' },
  editorial_planner:     { icon: ClipboardList, accent: '#10b981', tint: 'rgba(16,185,129,0.10)' },
  editorial_writer:      { icon: PenTool,       accent: '#10b981', tint: 'rgba(16,185,129,0.10)' },
  editorial_critic:      { icon: ShieldAlert,   accent: '#ef4444', tint: 'rgba(239,68,68,0.10)' },
  editorial_structurer:  { icon: Layers,        accent: '#10b981', tint: 'rgba(16,185,129,0.10)' },
  kit_professionnel:     { icon: Lock,          accent: '#b45309', tint: 'rgba(180,83,9,0.10)' },
};

/* ──────────────────────────────────────────────────────────────────────
   Connector — fine vertical line in S.E.S gold
   ────────────────────────────────────────────────────────────────────── */
const Connector = ({ height = 24 }) => (
  <div className="flex justify-center" aria-hidden="true">
    <div className="w-px bg-gradient-to-b from-[#C9A84C]/0 via-[#C9A84C]/50 to-[#C9A84C]/0" style={{ height }} />
  </div>
);

/* ──────────────────────────────────────────────────────────────────────
   AgentCard — compact (≤ 110px), expanded (adds 2-line mission)
   ────────────────────────────────────────────────────────────────────── */
const AgentCard = ({ agent, onClick, compact = true }) => {
  const meta = AGENT_META[agent.id] || AGENT_META.editorial_writer;
  const Icon = meta.icon;
  return (
    <button
      onClick={onClick}
      className="group relative text-left w-full rounded-xl border border-border/60 bg-white/95 hover:bg-white hover:border-[#C9A84C]/60 hover:-translate-y-0.5 hover:shadow-[0_8px_24px_-12px_rgba(201,168,76,0.35)] transition-all duration-200 overflow-hidden"
      data-testid={`agent-card-${agent.id}`}
    >
      {/* Accent line left */}
      <div className="absolute inset-y-0 left-0 w-[3px]" style={{ backgroundColor: meta.accent }} />
      <div className={`flex items-start gap-3 ${compact ? 'p-3' : 'p-3.5'}`}>
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
          style={{ backgroundColor: meta.tint }}
        >
          <Icon className="w-4 h-4" style={{ color: meta.accent }} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-[13px] text-foreground truncate">{agent.name}</h3>
          </div>
          <p className="text-[11px] font-medium truncate" style={{ color: meta.accent }}>{agent.role}</p>
          {!compact && (
            <p className="text-[11px] text-foreground/65 leading-snug line-clamp-2 mt-1">{agent.mission}</p>
          )}
        </div>
      </div>
    </button>
  );
};

/* ──────────────────────────────────────────────────────────────────────
   GroupSection — collapsible, with chevron + agent count badge
   ────────────────────────────────────────────────────────────────────── */
const GroupSection = ({ id, title, count, locked = false, children, defaultOpen = true }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <Collapsible open={open} onOpenChange={setOpen} data-testid={`agents-group-${id}`}>
      <CollapsibleTrigger asChild>
        <button
          className="w-full group flex items-center gap-2 text-left mb-3 select-none"
          data-testid={`agents-group-toggle-${id}`}
        >
          <ChevronDown
            className={`w-3.5 h-3.5 text-muted-foreground transition-transform ${open ? '' : '-rotate-90'}`}
            aria-hidden="true"
          />
          {locked && <Lock className="w-3 h-3 text-amber-700" />}
          <h4 className={`text-[11px] uppercase tracking-[0.12em] font-semibold ${locked ? 'text-amber-800' : 'text-muted-foreground'}`}>
            {title}
          </h4>
          <span className="inline-flex items-center justify-center min-w-[18px] h-[18px] px-1.5 rounded-full bg-muted/70 text-[10px] font-semibold text-foreground/70">
            {count}
          </span>
          {locked && (
            <span className="text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
              Confidentiel
            </span>
          )}
          <div className="flex-1 h-px bg-border/60 ml-2" />
        </button>
      </CollapsibleTrigger>
      <CollapsibleContent>
        {children}
      </CollapsibleContent>
    </Collapsible>
  );
};

/* ──────────────────────────────────────────────────────────────────────
   AgentDrawer — slide-in right panel with full agent details
   ────────────────────────────────────────────────────────────────────── */
const AgentDrawer = ({ agent, open, onOpenChange }) => {
  if (!agent) return null;
  const meta = AGENT_META[agent.id] || AGENT_META.editorial_writer;
  const Icon = meta.icon;

  const copyPrompt = () => {
    navigator.clipboard.writeText(agent.prompt || '');
    toast.success('Prompt copié dans le presse-papier');
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-xl overflow-y-auto"
        data-testid="agent-drawer"
      >
        <SheetHeader className="text-left space-y-2 pb-2">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: meta.tint }}
            >
              <Icon className="w-5 h-5" style={{ color: meta.accent }} />
            </div>
            <div className="flex-1 min-w-0">
              <SheetTitle className="text-base">{agent.name}</SheetTitle>
              <SheetDescription className="text-xs" style={{ color: meta.accent }}>
                {agent.role}
              </SheetDescription>
            </div>
          </div>
        </SheetHeader>

        <div className="mt-4 space-y-5 text-sm">
          <section>
            <h5 className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1.5 font-semibold">
              Mission
            </h5>
            <p className="text-[13px] text-foreground/80 leading-relaxed">{agent.mission}</p>
          </section>

          <section>
            <h5 className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1.5 font-semibold">
              Modèle utilisé
            </h5>
            <Badge variant="outline" className="text-xs font-normal">{agent.model}</Badge>
          </section>

          <section>
            <h5 className="text-[10px] uppercase tracking-wider text-muted-foreground mb-2 font-semibold">
              Garde-fous actifs ({agent.guardrails?.length || 0})
            </h5>
            <ul className="space-y-1.5">
              {(agent.guardrails || []).map((g, i) => (
                <li key={i} className="text-[12px] text-foreground/80 flex items-start gap-2">
                  <span className="text-emerald-600 mt-0.5 shrink-0">✓</span>
                  <span>{g}</span>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <div className="flex items-center justify-between mb-2">
              <h5 className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
                Prompt système (lecture seule)
              </h5>
              <Button variant="outline" size="sm" onClick={copyPrompt} data-testid="agent-modal-copy-prompt">
                <Copy className="w-3.5 h-3.5 mr-1.5" /> Copier
              </Button>
            </div>
            <pre
              className="text-[11px] bg-muted/50 border border-border/60 rounded-lg p-3 overflow-x-auto whitespace-pre-wrap max-h-[420px] overflow-y-auto leading-relaxed"
              data-testid="agent-modal-prompt"
            >
              {agent.prompt || '(prompt non disponible)'}
            </pre>
            <p className="text-[10px] text-muted-foreground mt-2">
              Source : <code className="bg-muted/50 px-1 rounded">{agent.file_path}</code>
              {' → '}
              <code className="bg-muted/50 px-1 rounded">{agent.prompt_var}</code>
            </p>
          </section>
        </div>
      </SheetContent>
    </Sheet>
  );
};

/* ──────────────────────────────────────────────────────────────────────
   Main component
   ────────────────────────────────────────────────────────────────────── */
export const AdminAgentsOrg = () => {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [selected, setSelected] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [detailed, setDetailed] = useState(false);
  const [exporting, setExporting] = useState(false);
  const cfg = { headers: { Authorization: `Bearer ${token}` } };

  useEffect(() => {
    axios.get(`${API}/admin/agents/registry`, cfg)
      .then(r => setData(r.data))
      .catch(() => toast.error('Erreur chargement organigramme'));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openAgent = (a) => {
    setSelected(a);
    setDrawerOpen(true);
  };

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
      toast.success('Organigramme exporté en PDF');
    } catch {
      toast.error("Erreur lors de l'export PDF");
    } finally {
      setExporting(false);
    }
  };

  if (!data) return <p className="text-sm text-muted-foreground">Chargement de l'organigramme…</p>;

  // ── Group agents by category ──
  const byId = (id) => data.agents.find(a => a.id === id);
  const directContact = ['strate', 'strategiia', 'dossier_express']
    .map(byId)
    .filter(Boolean);
  const marketing = ['video_factory'].map(byId).filter(Boolean);
  const editorial = data.agents.filter(a => a.id.startsWith('editorial_'));
  // Catch-all for any future agent we forgot to map
  const knownIds = new Set([
    ...directContact.map(a => a.id),
    ...marketing.map(a => a.id),
    ...editorial.map(a => a.id),
  ]);
  const others = data.agents.filter(a => !knownIds.has(a.id));
  const internalAgents = data.internal_agents || [];

  const totalAgents = data.agents.length + internalAgents.length;

  return (
    <div className="space-y-6" data-testid="admin-agents-org">
      {/* ─── Header card ─── */}
      <Card className="border-[#C9A84C]/30 bg-gradient-to-br from-[#FAF8F3] to-white">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Crown className="w-5 h-5 text-[#C9A84C]" /> Organigramme IA
            <span className="ml-2 inline-flex items-center justify-center min-w-[22px] h-[22px] px-2 rounded-full bg-[#1a1a2e] text-white text-[11px] font-semibold">
              {totalAgents}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <p className="text-sm text-foreground/70 flex-1">
              Visualisez votre équipe d'agents IA, leurs rôles et garde-fous.
              Cliquez sur une carte pour consulter le prompt système complet.
            </p>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-xs text-foreground/70 select-none cursor-pointer">
                <Switch
                  checked={detailed}
                  onCheckedChange={setDetailed}
                  data-testid="agents-view-toggle"
                  className="data-[state=checked]:bg-[#C9A84C]"
                />
                Vue détaillée
              </label>
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
          </div>
        </CardContent>
      </Card>

      {/* ─── Tabs ─── */}
      <Tabs defaultValue="overview" className="space-y-5">
        <TabsList className="bg-card/80 backdrop-blur border border-border/60 p-1 rounded-lg">
          <TabsTrigger value="overview" className="gap-1.5 text-xs px-3 py-1.5" data-testid="agents-subtab-overview">
            <Crown className="w-3.5 h-3.5" /> Vue générale
          </TabsTrigger>
          <TabsTrigger value="versions" className="gap-1.5 text-xs px-3 py-1.5" data-testid="agents-subtab-versions">
            <History className="w-3.5 h-3.5" /> Versions
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-2 mt-0">
          {/* ── Level 0 : CEO ── */}
          <div className="flex justify-center">
            <div
              className="rounded-xl border border-[#C9A84C]/70 bg-gradient-to-br from-[#1a1a2e] to-[#0a0a14] text-white px-6 py-3.5 text-center shadow-[0_12px_30px_-12px_rgba(201,168,76,0.45)]"
              data-testid="ceo-card"
            >
              <div className="flex items-center justify-center gap-2.5">
                <Crown className="w-5 h-5 text-[#C9A84C]" />
                <h3 className="font-semibold text-[15px] tracking-wide">{data.ceo.name}</h3>
              </div>
              <p className="text-[11px] text-[#C9A84C]/90 mt-0.5">{data.ceo.role}</p>
            </div>
          </div>

          <Connector height={28} />

          {/* ── Group : direct client contact ── */}
          {directContact.length > 0 && (
            <GroupSection id="direct" title="Agents au contact direct client" count={directContact.length}>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {directContact.map(a => (
                  <AgentCard key={a.id} agent={a} onClick={() => openAgent(a)} compact={!detailed} />
                ))}
              </div>
            </GroupSection>
          )}

          <Connector />

          {/* ── Group : Marketing / Acquisition ── */}
          {marketing.length > 0 && (
            <GroupSection id="marketing" title="Studio Marketing IA — Acquisition" count={marketing.length}>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {marketing.map(a => (
                  <AgentCard key={a.id} agent={a} onClick={() => openAgent(a)} compact={!detailed} />
                ))}
              </div>
            </GroupSection>
          )}

          <Connector />

          {/* ── Group : Editorial Studio ── */}
          {editorial.length > 0 && (
            <GroupSection id="editorial" title="Studio Éditorial SEO" count={editorial.length}>
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {editorial.map(a => (
                  <AgentCard key={a.id} agent={a} onClick={() => openAgent(a)} compact={!detailed} />
                ))}
              </div>
            </GroupSection>
          )}

          {/* ── Safety net : any unmapped agent ── */}
          {others.length > 0 && (
            <>
              <Connector />
              <GroupSection id="others" title="Autres agents" count={others.length}>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {others.map(a => (
                    <AgentCard key={a.id} agent={a} onClick={() => openAgent(a)} compact={!detailed} />
                  ))}
                </div>
              </GroupSection>
            </>
          )}

          {/* ── Group : Internal tools (admin confidential) ── */}
          {internalAgents.length > 0 && (
            <>
              <Connector />
              <GroupSection
                id="internal"
                title="Outils internes admin"
                count={internalAgents.length}
                locked
              >
                <div data-testid="internal-agents-section">
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {internalAgents.map(a => (
                      <AgentCard key={a.id} agent={a} onClick={() => openAgent(a)} compact={!detailed} />
                    ))}
                  </div>
                </div>
              </GroupSection>
            </>
          )}
        </TabsContent>

        <TabsContent value="versions" className="mt-0">
          <AdminAgentsVersions />
        </TabsContent>
      </Tabs>

      <AgentDrawer agent={selected} open={drawerOpen} onOpenChange={setDrawerOpen} />
    </div>
  );
};

export default AdminAgentsOrg;
