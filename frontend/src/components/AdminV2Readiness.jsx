import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, RefreshCw, Lock, Database, Layers, CheckCircle, AlertTriangle, ShieldAlert } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STATUS_CONFIG = {
  vert: {
    color: 'bg-emerald-500',
    glow: 'shadow-emerald-500/40',
    border: 'border-emerald-500/30',
    bg: 'bg-emerald-500/5',
    text: 'text-emerald-600',
    label: 'Pret pour V2',
    icon: CheckCircle,
  },
  orange: {
    color: 'bg-amber-500',
    glow: 'shadow-amber-500/40',
    border: 'border-amber-500/30',
    bg: 'bg-amber-500/5',
    text: 'text-amber-600',
    label: 'En progression',
    icon: AlertTriangle,
  },
  rouge: {
    color: 'bg-red-500',
    glow: 'shadow-red-500/40',
    border: 'border-red-500/30',
    bg: 'bg-red-500/5',
    text: 'text-red-600',
    label: 'Collecte insuffisante',
    icon: ShieldAlert,
  },
};

const ProgressSegment = ({ label, value, max, color }) => {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{value}/{max} pts</span>
      </div>
      <div className="h-1.5 rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
};

export const AdminV2Readiness = ({ axiosConfig }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchReadiness = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/knowledge-patterns/v2-readiness`, axiosConfig);
      setData(res.data);
    } catch {
      toast.error("Erreur chargement statut V2");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchReadiness(); }, []);

  if (loading) {
    return (
      <Card data-testid="v2-readiness-card">
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const cfg = STATUS_CONFIG[data.status] || STATUS_CONFIG.rouge;
  const StatusIcon = cfg.icon;
  const progressPct = Math.min((data.usable_cases / data.minimum_green) * 100, 100);

  return (
    <Card className={`${cfg.border} border`} data-testid="v2-readiness-card">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Lock className="w-4 h-4 text-muted-foreground" />
            IA V2 Predictive — Statut de preparation
          </CardTitle>
          <Button size="sm" variant="ghost" onClick={fetchReadiness} className="h-7 w-7 p-0" data-testid="v2-readiness-refresh">
            <RefreshCw className="w-3.5 h-3.5" />
          </Button>
        </div>
        <p className="text-[11px] text-muted-foreground">
          Indicateur interne. Invisible pour les clients. Minimum 500 cas exploitables pour activer V2.
        </p>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Traffic light + Score */}
        <div className={`flex items-center gap-5 p-4 rounded-xl ${cfg.bg} ${cfg.border} border`} data-testid="v2-readiness-status-block">
          {/* Traffic light */}
          <div className="flex flex-col items-center gap-1.5 flex-shrink-0" data-testid="v2-traffic-light">
            <div className={`w-5 h-5 rounded-full ${data.status === 'rouge' ? 'bg-red-500 shadow-lg shadow-red-500/50' : 'bg-red-500/20'} transition-all`} />
            <div className={`w-5 h-5 rounded-full ${data.status === 'orange' ? 'bg-amber-500 shadow-lg shadow-amber-500/50' : 'bg-amber-500/20'} transition-all`} />
            <div className={`w-5 h-5 rounded-full ${data.status === 'vert' ? 'bg-emerald-500 shadow-lg shadow-emerald-500/50' : 'bg-emerald-500/20'} transition-all`} />
          </div>

          {/* Score */}
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className={`text-4xl font-bold tracking-tight ${cfg.text}`} data-testid="v2-readiness-score">
                {data.score}
              </span>
              <span className="text-lg text-muted-foreground font-light">/100</span>
              <Badge className={`${cfg.color} text-white ml-auto`} data-testid="v2-readiness-badge">
                <StatusIcon className="w-3 h-3 mr-1" />
                {cfg.label}
              </Badge>
            </div>
            {/* Progress bar */}
            <div className="space-y-1">
              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <div
                  className={`h-full rounded-full ${cfg.color} transition-all duration-700 ease-out`}
                  style={{ width: `${progressPct}%` }}
                  data-testid="v2-readiness-progress"
                />
              </div>
              <p className="text-xs text-muted-foreground">
                {data.usable_cases} / {data.minimum_green} cas exploitables
                {data.usable_cases < data.minimum_green && (
                  <span className="ml-1">({data.minimum_green - data.usable_cases} restants)</span>
                )}
              </p>
            </div>
          </div>
        </div>

        {/* Score breakdown */}
        <div className="space-y-3">
          <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide">Decomposition du score</p>
          <div className="grid gap-2.5">
            <ProgressSegment label="Volume de cas" value={data.breakdown.volume} max={50} color="bg-blue-500" />
            <ProgressSegment label="Diversite (familles + categories)" value={data.breakdown.diversity} max={20} color="bg-purple-500" />
            <ProgressSegment label="Completude (blocages documentes)" value={data.breakdown.completeness} max={15} color="bg-amber-500" />
            <ProgressSegment label="Qualite (leviers + quality level)" value={data.breakdown.quality} max={15} color="bg-emerald-500" />
          </div>
        </div>

        {/* Statistics grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg border text-center" data-testid="v2-stat-total">
            <Database className="w-4 h-4 mx-auto mb-1 text-muted-foreground" />
            <p className="text-xl font-bold">{data.total_cases}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Total cas</p>
          </div>
          <div className="p-3 rounded-lg border text-center" data-testid="v2-stat-usable">
            <CheckCircle className="w-4 h-4 mx-auto mb-1 text-emerald-500" />
            <p className="text-xl font-bold">{data.usable_cases}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Exploitables</p>
          </div>
          <div className="p-3 rounded-lg border text-center" data-testid="v2-stat-families">
            <Layers className="w-4 h-4 mx-auto mb-1 text-purple-500" />
            <p className="text-xl font-bold">{data.details.unique_families}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Familles</p>
          </div>
          <div className="p-3 rounded-lg border text-center" data-testid="v2-stat-blocages">
            <AlertTriangle className="w-4 h-4 mx-auto mb-1 text-amber-500" />
            <p className="text-xl font-bold">{data.details.with_blocage}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Avec blocage</p>
          </div>
        </div>

        {/* Distributions */}
        {(data.complexity_distribution?.length > 0 || data.source_distribution?.length > 0) && (
          <div className="grid sm:grid-cols-2 gap-4">
            {data.complexity_distribution?.length > 0 && (
              <div className="space-y-2" data-testid="v2-complexity-dist">
                <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide">Complexite</p>
                {data.complexity_distribution.map(c => (
                  <div key={c.niveau} className="flex items-center justify-between text-sm px-2 py-1 rounded border">
                    <span className="capitalize">{c.niveau}</span>
                    <span className="font-medium">{c.count}</span>
                  </div>
                ))}
              </div>
            )}
            {data.source_distribution?.length > 0 && (
              <div className="space-y-2" data-testid="v2-source-dist">
                <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide">Sources</p>
                {data.source_distribution.map(s => (
                  <div key={s.source} className="flex items-center justify-between text-sm px-2 py-1 rounded border">
                    <span className="capitalize">{s.source}</span>
                    <span className="font-medium">{s.count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Rules reminder */}
        <div className="p-3 rounded-lg border border-dashed border-muted-foreground/20 bg-muted/30">
          <p className="text-[10px] text-muted-foreground leading-relaxed">
            <strong>Regles :</strong> Rouge = &lt;200 cas ou donnees insuffisantes. Orange = 200-499 cas + bonne structuration. Vert = 500+ cas exploitables + diversite reelle + V1 stable. Le score ne peut jamais passer au vert avant 500 cas, quelle que soit la qualite des donnees.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
