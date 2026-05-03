import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Activity, MousePointerClick, Target, Radio } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const PERIODS = [
  { value: '7d', label: '7 jours' },
  { value: '30d', label: '30 jours' },
  { value: 'all', label: 'Tout' },
];

const KpiCard = ({ icon: Icon, label, value, sub, tone = 'default', testid }) => (
  <div className="rounded-lg border bg-card p-4" data-testid={testid}>
    <div className="flex items-center gap-2 text-muted-foreground text-xs font-medium mb-2">
      <Icon className="w-3.5 h-3.5" /> {label}
    </div>
    <p className={`text-2xl font-semibold ${tone === 'accent' ? 'text-[#C9A84C]' : 'text-foreground'}`}>
      {value}
    </p>
    {sub && <p className="text-[11px] text-muted-foreground mt-0.5">{sub}</p>}
  </div>
);

export const AdminStrateKpis = () => {
  const { token } = useAuth();
  const [period, setPeriod] = useState('30d');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [enabled, setEnabled] = useState(true);
  const [toggling, setToggling] = useState(false);

  const authCfg = { headers: { Authorization: `Bearer ${token}` } };

  const load = useCallback(async (p = period) => {
    setLoading(true);
    try {
      const [kpisRes, cfgRes] = await Promise.all([
        axios.get(`${API}/admin/strate/kpis?period=${p}`, authCfg),
        axios.get(`${API}/admin/strate/config`, authCfg),
      ]);
      setData(kpisRes.data);
      setEnabled(!!cfgRes.data.enabled);
    } catch (e) { /* silent */ }
    finally { setLoading(false); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period, token]);

  useEffect(() => { if (token) load(period); }, [token, period, load]);

  const toggleKillSwitch = async () => {
    setToggling(true);
    try {
      await axios.post(`${API}/admin/strate/toggle`, { enabled: !enabled }, authCfg);
      setEnabled(!enabled);
    } catch (e) { /* silent */ }
    finally { setToggling(false); }
  };

  return (
    <div className="space-y-6" data-testid="admin-strate-kpis-root">
      {/* Header with kill switch */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold flex items-center gap-2">
            <Radio className="w-4 h-4 text-[#C9A84C]" /> Straté · Conciergerie IA
          </h3>
          <p className="text-xs text-muted-foreground">
            Suivi du réceptionniste IA — orientation visiteurs vers StratégiIA, Dossier Express, RDV, guides.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-muted rounded-md p-0.5" data-testid="strate-period-selector">
            {PERIODS.map((p) => (
              <button key={p.value}
                onClick={() => setPeriod(p.value)}
                className={`px-3 py-1 text-xs rounded ${period === p.value ? 'bg-background shadow-sm font-medium' : 'text-muted-foreground hover:text-foreground'}`}
                data-testid={`strate-period-${p.value}`}>
                {p.label}
              </button>
            ))}
          </div>
          <Button
            onClick={toggleKillSwitch}
            variant={enabled ? 'outline' : 'default'}
            size="sm"
            disabled={toggling}
            className={enabled ? '' : 'bg-emerald-600 hover:bg-emerald-700 text-white'}
            data-testid="strate-killswitch-btn"
          >
            {toggling ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : null}
            {enabled ? 'Désactiver Straté' : 'Réactiver Straté'}
          </Button>
        </div>
      </div>

      <div className="text-[11px] text-muted-foreground" data-testid="strate-status-line">
        Statut : {enabled ? <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">Actif</Badge> : <Badge variant="destructive">Désactivé</Badge>}
        {' '}— kill switch immédiat, aucun déploiement nécessaire.
      </div>

      {loading || !data ? (
        <div className="flex items-center justify-center py-10 text-muted-foreground">
          <Loader2 className="w-5 h-5 animate-spin mr-2" /> Chargement…
        </div>
      ) : (
        <>
          {/* Main KPIs */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3" data-testid="strate-main-kpis">
            <KpiCard icon={Activity} label="Sessions totales"
              value={data.totals.sessions}
              sub={`${data.totals.opened} ouvertes`}
              testid="kpi-sessions" />
            <KpiCard icon={MousePointerClick} label="Taux d'ouverture"
              value={`${data.rates.open_rate}%`}
              sub={`${data.totals.opened} / ${data.totals.sessions}`}
              testid="kpi-open-rate" />
            <KpiCard icon={Activity} label="Taux de qualification"
              value={`${data.rates.qualification_rate}%`}
              sub={`${data.totals.qualified} / ${data.totals.opened}`}
              testid="kpi-qualification-rate" />
            <KpiCard icon={Target} label="Taux de routage" tone="accent"
              value={`${data.rates.routing_rate}%`}
              sub={`${data.totals.routed} CTA cliqués`}
              testid="kpi-routing-rate" />
          </div>

          {/* Routing breakdown */}
          <Card data-testid="strate-routing-breakdown">
            <CardHeader>
              <CardTitle className="text-sm">Répartition du routage</CardTitle>
            </CardHeader>
            <CardContent>
              {data.routing_breakdown.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">
                  Aucun routage enregistré sur cette période.
                </p>
              ) : (
                <div className="space-y-2">
                  {data.routing_breakdown.map((row, i) => {
                    const max = data.routing_breakdown[0]?.count || 1;
                    const pct = Math.round((row.count / max) * 100);
                    return (
                      <div key={i} className="flex items-center gap-3" data-testid={`routing-row-${row.src}`}>
                        <div className="w-40 text-xs text-foreground/80 truncate" title={row.src}>{row.src}</div>
                        <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                          <div className="h-full bg-[#C9A84C]" style={{ width: `${pct}%` }} />
                        </div>
                        <div className="w-10 text-right text-xs font-medium text-foreground">{row.count}</div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Opens per page */}
          <Card data-testid="strate-opens-per-page">
            <CardHeader>
              <CardTitle className="text-sm">Ouvertures par page</CardTitle>
            </CardHeader>
            <CardContent>
              {data.opens_per_page.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">Aucune ouverture enregistrée.</p>
              ) : (
                <ul className="space-y-1 text-xs">
                  {data.opens_per_page.map((row, i) => (
                    <li key={i} className="flex justify-between border-b border-border/40 py-1 last:border-0">
                      <span className="text-foreground/80 truncate">{row.page || '(inconnu)'}</span>
                      <span className="font-medium text-foreground">{row.count}</span>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default AdminStrateKpis;
