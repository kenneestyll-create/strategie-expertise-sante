import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Mail, MailCheck, BarChart3 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const KpiCard = ({ icon: Icon, label, value, sub, testid }) => (
  <div className="rounded-lg border bg-card p-4" data-testid={testid}>
    <div className="flex items-center gap-2 text-muted-foreground text-xs font-medium mb-2">
      <Icon className="w-3.5 h-3.5" /> {label}
    </div>
    <p className="text-2xl font-semibold text-foreground">{value}</p>
    {sub && <p className="text-[11px] text-muted-foreground mt-0.5">{sub}</p>}
  </div>
);

export const AdminPillarLeads = () => {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    axios.get(`${API}/admin/leads/pillar-stats`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then((r) => setData(r.data))
      .catch(() => { /* silent */ })
      .finally(() => setLoading(false));
  }, [token]);

  const formatDate = (iso) => {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
    } catch { return '—'; }
  };

  return (
    <div className="space-y-6" data-testid="admin-pillar-leads-root">
      <div>
        <h3 className="text-base font-semibold flex items-center gap-2">
          <Mail className="w-4 h-4 text-[#C9A84C]" /> Leads SEO — Pages piliers
        </h3>
        <p className="text-xs text-muted-foreground mt-1">
          Emails captés sur les 5 pages stratégiques (MDPH, AT/MP, Expertise médicale, Calculatrice IPP, Calculatrice AAH)
          via les blocs « Mémo gratuit ». Chaque lead reçoit automatiquement le mémo associé par email.
        </p>
      </div>

      {loading || !data ? (
        <div className="flex items-center justify-center py-10 text-muted-foreground">
          <Loader2 className="w-5 h-5 animate-spin mr-2" /> Chargement…
        </div>
      ) : (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3" data-testid="pillar-leads-kpis">
            <KpiCard icon={Mail} label="Total leads"
              value={data.total_leads}
              sub="depuis l'origine"
              testid="kpi-pillar-total" />
            <KpiCard icon={MailCheck} label="Mémos envoyés"
              value={data.email_sent}
              sub={`${data.send_rate}% taux d'envoi`}
              testid="kpi-pillar-sent" />
            <KpiCard icon={BarChart3} label="7 derniers jours"
              value={data.last_7d}
              sub="nouveaux leads"
              testid="kpi-pillar-7d" />
            <KpiCard icon={BarChart3} label="Pages actives"
              value={data.by_page.length}
              sub="sur 5 pages piliers"
              testid="kpi-pillar-pages" />
          </div>

          {/* By page breakdown */}
          <Card data-testid="pillar-leads-by-page">
            <CardHeader>
              <CardTitle className="text-sm">Répartition par page pilier</CardTitle>
            </CardHeader>
            <CardContent>
              {data.by_page.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">
                  Aucun lead capté pour le moment. Patience — Google ramène progressivement les visiteurs.
                </p>
              ) : (
                <div className="space-y-2">
                  {data.by_page.map((row, i) => {
                    const max = data.by_page[0]?.count || 1;
                    const pct = Math.round((row.count / max) * 100);
                    return (
                      <div key={i} className="flex items-center gap-3" data-testid={`pillar-row-${row.page_id}`}>
                        <div className="w-44 text-xs text-foreground/80 truncate" title={row.label}>
                          {row.label || row.page_id}
                        </div>
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

          {/* Recent leads */}
          <Card data-testid="pillar-leads-recent">
            <CardHeader>
              <CardTitle className="text-sm">Leads récents (50 derniers)</CardTitle>
            </CardHeader>
            <CardContent>
              {data.recent.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">Aucun lead pour l'instant.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-left text-muted-foreground border-b">
                        <th className="py-2 pr-3 font-medium">Date</th>
                        <th className="py-2 pr-3 font-medium">Email</th>
                        <th className="py-2 pr-3 font-medium">Page pilier</th>
                        <th className="py-2 font-medium">Email envoyé</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.recent.map((l, i) => (
                        <tr key={i} className="border-b border-border/40 last:border-0" data-testid={`pillar-recent-${i}`}>
                          <td className="py-2 pr-3 text-muted-foreground whitespace-nowrap">{formatDate(l.created_at)}</td>
                          <td className="py-2 pr-3 font-medium">{l.email}</td>
                          <td className="py-2 pr-3 text-foreground/80">{l.page_label || l.page_id}</td>
                          <td className="py-2">
                            {l.email_sent
                              ? <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">Envoyé</Badge>
                              : <Badge variant="destructive">Échec</Badge>
                            }
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default AdminPillarLeads;
