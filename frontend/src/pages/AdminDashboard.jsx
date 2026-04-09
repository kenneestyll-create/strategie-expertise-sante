import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { PremiumAnalysisRenderer } from '@/components/PremiumAnalysisRenderer';
import { 
  Heart, 
  LogOut, 
  Search, 
  Mail, 
  Phone, 
  Calendar,
  Users,
  Clock,
  CheckCircle,
  AlertCircle,
  Eye,
  Trash2,
  Loader2,
  RefreshCw,
  Home,
  Star,
  MessageSquare,
  XCircle,
  Gift,
  Percent,
  Hash,
  TrendingUp,
  Send,
  FolderOpen,
  Video,
  User,
  Zap,
  Brain,
  Plus,
  Pencil,
  Upload,
  X,
  Bell,
  AlertTriangle,
  FileText,
  Shield,
  Settings,
  Sun,
  Moon
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { useAdminTest } from '@/components/AdminTestBanner';
import { useAdminTheme } from '@/hooks/useAdminTheme';
import { AdminHelpPanel } from '@/components/AdminHelpPanel';
import { AdminOnboardingTour, TOUR_KEY } from '@/components/AdminOnboardingTour';
import { TarifsEditor, ChiffresClesEditor } from '@/components/ConfigEditors';
import axios from 'axios';
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { BarChart3, BellRing, Download, FlaskConical, PenTool, FileSearch, QrCode, Globe, BadgeCheck, Tag } from 'lucide-react';
import { EmailTemplateEditor } from '@/components/EmailTemplateEditor';
import { AdminConseilsStrate } from '@/components/AdminConseilsStrate';
import { AdminConversionAnalytics } from '@/components/AdminConversionAnalytics';
import { AdminPremiumReview } from '@/components/AdminPremiumReview';
import { AdminV2Readiness } from '@/components/AdminV2Readiness';
import { AdminPredictiveV2 } from '@/components/AdminPredictiveV2';
import { AdminStrategicFeedback } from '@/components/AdminStrategicFeedback';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CHART_COLORS = ['#b8860b', '#1a1a2e', '#d4a843', '#2d2d44', '#e8c547', '#444466', '#c49b2a', '#5a5a7a'];

const formatEuro = (v) => `${Number(v).toLocaleString('fr-FR')}€`;
const formatShortDate = (d) => {
  if (!d) return '';
  const parts = d.split('-');
  return `${parts[2]}/${parts[1]}`;
};

const KpiCard = ({ label, value, sub, color = 'text-foreground' }) => (
  <Card data-testid={`kpi-${label.toLowerCase().replace(/\s+/g, '-')}`}>
    <CardContent className="py-4 px-5">
      <p className="text-xs text-muted-foreground uppercase tracking-wide">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
      {sub && <p className="text-xs text-muted-foreground mt-0.5">{sub}</p>}
    </CardContent>
  </Card>
);

const AnalyticsTab = ({ data, period, onPeriodChange }) => {
  const { kpis, time_series, packages, analyse_types } = data;

  return (
    <div className="space-y-6">
      {/* Period selector */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-emerald-600" />
          Tableau de bord analytique
        </h2>
        <div className="flex gap-1 bg-muted rounded-lg p-1" data-testid="analytics-period-selector">
          {[{v: '7d', l: '7 jours'}, {v: '30d', l: '30 jours'}, {v: '90d', l: '90 jours'}].map(p => (
            <button
              key={p.v}
              onClick={() => onPeriodChange(p.v)}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${period === p.v ? 'bg-background shadow text-foreground font-medium' : 'text-muted-foreground hover:text-foreground'}`}
              data-testid={`period-${p.v}`}
            >
              {p.l}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        <KpiCard label="Revenus" value={formatEuro(kpis.total_revenue)} sub={`${formatEuro(kpis.pending_revenue)} en attente`} color="text-emerald-600" />
        <KpiCard label="Contacts" value={kpis.total_contacts} />
        <KpiCard label="Clients inscrits" value={kpis.total_clients} sub={`Taux conversion: ${kpis.conversion_rate}%`} />
        <KpiCard label="Analyses IA" value={kpis.total_analyses} sub={`${kpis.analyses_this_month || 0} ce mois`} />
        <KpiCard label="Dossiers Express" value={kpis.total_dossiers} sub={`${kpis.dossiers_this_month || 0} ce mois`} />
      </div>

      {/* Service utilization cards */}
      {data.service_utilization && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="service-utilization">
          {Object.entries(data.service_utilization).map(([key, svc]) => (
            <Card key={key}>
              <CardContent className="p-4">
                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">{svc.label}</p>
                <p className="text-2xl font-bold">{svc.total}</p>
                <div className="flex items-center gap-1 mt-1">
                  <span className="text-xs text-accent font-medium">+{svc.this_month}</span>
                  <span className="text-[10px] text-muted-foreground">ce mois</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Extra KPIs row */}
      {(kpis.active_dossiers !== undefined || kpis.total_documents !== undefined) && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <KpiCard label="Dossiers actifs" value={kpis.active_dossiers || 0} sub="en cours de traitement" color="text-blue-600" />
          <KpiCard label="Documents" value={kpis.total_documents || 0} sub={`${kpis.pending_documents || 0} en attente`} />
          <KpiCard label="Forum" value={kpis.total_forum_users} sub={`${kpis.total_chatbot_sessions} sessions chatbot`} />
          <KpiCard label="Calculatrice" value={kpis.calculator_usage || 0} sub="utilisations" />
        </div>
      )}

      {/* Charts row 1: Activity over time */}
      <div className="grid lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Activité (contacts & analyses)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64" data-testid="chart-activity">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={time_series} margin={{ top: 5, right: 5, left: -10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis dataKey="date" tickFormatter={formatShortDate} tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                  <YAxis tick={{ fontSize: 10 }} allowDecimals={false} />
                  <Tooltip labelFormatter={(v) => `Date: ${v}`} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="contacts" name="Contacts" fill="#1a1a2e" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="analyses" name="Analyses" fill="#b8860b" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="clients" name="Inscriptions" fill="#d4a843" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Revenus (€)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64" data-testid="chart-revenue">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={time_series} margin={{ top: 5, right: 5, left: -10, bottom: 5 }}>
                  <defs>
                    <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#b8860b" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#b8860b" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis dataKey="date" tickFormatter={formatShortDate} tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                  <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => `${v}€`} />
                  <Tooltip formatter={(v) => [`${v}€`, 'Revenus']} labelFormatter={(v) => `Date: ${v}`} />
                  <Area type="monotone" dataKey="revenue" stroke="#b8860b" fill="url(#revenueGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts row 2: Distributions */}
      <div className="grid lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Répartition par prestation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64" data-testid="chart-packages">
              {packages.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={packages} dataKey="revenue" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({name, percent}) => `${name.substring(0, 15)}${name.length > 15 ? '...' : ''} (${(percent*100).toFixed(0)}%)`} labelLine={{ strokeWidth: 1 }} style={{ fontSize: 10 }}>
                      {packages.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(v) => [`${v}€`, 'Revenus']} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-center text-muted-foreground pt-20 text-sm">Aucune transaction</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Types d'analyses IA</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64" data-testid="chart-analyse-types">
              {analyse_types.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analyse_types} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis type="number" tick={{ fontSize: 10 }} allowDecimals={false} />
                    <YAxis type="category" dataKey="type" tick={{ fontSize: 10 }} width={60} />
                    <Tooltip />
                    <Bar dataKey="count" name="Analyses" fill="#1a1a2e" radius={[0, 4, 4, 0]}>
                      {analyse_types.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-center text-muted-foreground pt-20 text-sm">Aucune analyse</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Revenue table */}
      {packages.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Détail des prestations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm" data-testid="analytics-packages-table">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 font-medium">Prestation</th>
                    <th className="pb-2 font-medium text-center">Transactions</th>
                    <th className="pb-2 font-medium text-right">Revenus</th>
                  </tr>
                </thead>
                <tbody>
                  {packages.map((pkg, i) => (
                    <tr key={i} className="border-b last:border-0">
                      <td className="py-2">{pkg.name}</td>
                      <td className="py-2 text-center">{pkg.count}</td>
                      <td className="py-2 text-right font-medium">{formatEuro(pkg.revenue)}</td>
                    </tr>
                  ))}
                  <tr className="font-semibold">
                    <td className="pt-3">Total</td>
                    <td className="pt-3 text-center">{packages.reduce((s, p) => s + p.count, 0)}</td>
                    <td className="pt-3 text-right text-emerald-600">{formatEuro(packages.reduce((s, p) => s + p.revenue, 0))}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

const OnboardingStatsCard = ({ axiosConfig, onRestartTour }) => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    axios.get(`${API}/admin/onboarding/stats`, axiosConfig)
      .then(r => setStats(r.data))
      .catch(() => {});
  }, []);

  if (!stats || stats.total_starts === 0) return null;

  return (
    <Card data-testid="config-onboarding-stats">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              <Star className="w-5 h-5 text-[#C9A84C]" /> Tutoriel Straté
            </CardTitle>
            <p className="text-xs text-muted-foreground">Engagement du tutoriel d'onboarding admin.</p>
          </div>
          <Button size="sm" variant="outline" className="gap-1.5 text-xs" onClick={onRestartTour} data-testid="config-restart-tour">
            Relancer
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="p-3 rounded-lg border text-center">
            <p className="text-xl font-bold">{stats.total_starts}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Démarrages</p>
          </div>
          <div className="p-3 rounded-lg border text-center">
            <p className="text-xl font-bold text-emerald-600">{stats.total_completes}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Terminés</p>
          </div>
          <div className="p-3 rounded-lg border text-center">
            <p className="text-xl font-bold">{stats.completion_rate}%</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Taux</p>
          </div>
        </div>
        {stats.step_views.some(s => s.views > 0) && (
          <div className="space-y-1.5">
            <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide">Vues par étape</p>
            {stats.step_views.map(s => (
              <div key={s.step} className="flex items-center gap-2 text-xs">
                <span className="w-28 text-muted-foreground truncate">{s.label}</span>
                <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                  <div
                    className="h-full rounded-full bg-[#C9A84C] transition-all"
                    style={{ width: `${stats.step_views[0].views ? (s.views / stats.step_views[0].views) * 100 : 0}%` }}
                  />
                </div>
                <span className="w-6 text-right font-medium">{s.views}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const CLEANUP_ITEMS = [
  { key: 'contacts', label: 'Demandes de contact', endpoint: '/admin/cleanup/contacts', icon: 'Mail' },
  { key: 'strategiia', label: 'Analyses StratégiIA', endpoint: '/admin/cleanup/strategiia', icon: 'Brain' },
  { key: 'dossier', label: 'Dossiers Express', endpoint: '/admin/cleanup/dossier-express', icon: 'FolderOpen' },
  { key: 'avis', label: 'Avis clients', endpoint: '/admin/cleanup/avis', icon: 'Star' },
  { key: 'chatbot', label: 'Sessions chatbot', endpoint: '/admin/cleanup/chatbot', icon: 'MessageSquare' },
  { key: 'onboarding', label: 'Stats tutoriel', endpoint: '/admin/cleanup/onboarding', icon: 'Zap' },
];

const ProductionCleanupCard = ({ axiosConfig }) => {
  const [confirmTarget, setConfirmTarget] = useState(null);
  const [purging, setPurging] = useState(null);
  const [results, setResults] = useState({});

  const handlePurge = async (item) => {
    setPurging(item.key);
    try {
      const res = await axios.post(`${API}${item.endpoint}`, {}, axiosConfig);
      setResults(prev => ({ ...prev, [item.key]: res.data.deleted }));
      toast.success(`${item.label} : ${res.data.deleted} élément(s) supprimé(s)`);
    } catch {
      toast.error(`Erreur lors de la purge de ${item.label}`);
    }
    setPurging(null);
    setConfirmTarget(null);
  };

  const handleResetCounter = async (type, label) => {
    setPurging(type);
    try {
      await axios.post(`${API}/admin/cleanup/counter-reset`, { type }, axiosConfig);
      toast.success(`${label} remis à zéro`);
      setResults(prev => ({ ...prev, [type]: 0 }));
    } catch {
      toast.error('Erreur lors de la remise à zéro');
    }
    setPurging(null);
  };

  const handleFullPurge = async () => {
    setPurging('full');
    try {
      const res = await axios.post(`${API}/admin/cleanup/full-purge`, {}, axiosConfig);
      const total = Object.values(res.data.purged).filter(v => typeof v === 'number').reduce((a, b) => a + b, 0);
      toast.success(`Purge complète : ${total} élément(s) supprimé(s) + compteurs remis à zéro`);
      setResults({ full: total });
    } catch {
      toast.error('Erreur lors de la purge complète');
    }
    setPurging(null);
    setConfirmTarget(null);
  };

  return (
    <Card data-testid="config-production-cleanup" className="border-red-500/20">
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Shield className="w-5 h-5 text-red-500" /> Préparation Production
        </CardTitle>
        <p className="text-xs text-muted-foreground">Supprimez les données de test et remettez les compteurs à zéro avant le lancement.</p>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Individual purge buttons */}
        <div className="space-y-2">
          <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide">Purge par section</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {CLEANUP_ITEMS.map(item => (
              <div key={item.key} className="flex items-center justify-between p-2.5 rounded-lg border">
                <span className="text-sm">{item.label}</span>
                <div className="flex items-center gap-2">
                  {results[item.key] !== undefined && (
                    <span className="text-[10px] text-emerald-600 font-medium">{results[item.key]} supprimé(s)</span>
                  )}
                  {confirmTarget === item.key ? (
                    <div className="flex items-center gap-1">
                      <Button size="sm" variant="destructive" className="h-7 text-[11px] gap-1" disabled={purging === item.key}
                        onClick={() => handlePurge(item)} data-testid={`confirm-purge-${item.key}`}
                      >
                        {purging === item.key ? <Loader2 className="w-3 h-3 animate-spin" /> : <Trash2 className="w-3 h-3" />}
                        Confirmer
                      </Button>
                      <Button size="sm" variant="ghost" className="h-7 text-[11px]" onClick={() => setConfirmTarget(null)}>
                        <X className="w-3 h-3" />
                      </Button>
                    </div>
                  ) : (
                    <Button size="sm" variant="outline" className="h-7 text-[11px] gap-1 text-red-600 hover:text-red-700 hover:border-red-300"
                      onClick={() => setConfirmTarget(item.key)} data-testid={`purge-${item.key}`}
                    >
                      <Trash2 className="w-3 h-3" /> Purger
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Counter resets */}
        <div className="space-y-2">
          <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide">Remise à zéro des compteurs</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div className="flex items-center justify-between p-2.5 rounded-lg border">
              <span className="text-sm">Compteur visiteurs (Hero)</span>
              <Button size="sm" variant="outline" className="h-7 text-[11px] gap-1 text-orange-600 hover:text-orange-700"
                disabled={purging === 'visitors'}
                onClick={() => handleResetCounter('visitors', 'Compteur visiteurs')}
                data-testid="reset-visitors"
              >
                {purging === 'visitors' ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                Remettre à 0
              </Button>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg border">
              <span className="text-sm">Base dossiers hebdo</span>
              <Button size="sm" variant="outline" className="h-7 text-[11px] gap-1 text-orange-600 hover:text-orange-700"
                disabled={purging === 'dossiers'}
                onClick={() => handleResetCounter('dossiers', 'Base dossiers')}
                data-testid="reset-dossiers"
              >
                {purging === 'dossiers' ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                Remettre à 0
              </Button>
            </div>
          </div>
        </div>

        {/* Full purge */}
        <div className="pt-3 border-t border-red-500/10">
          {confirmTarget === 'full' ? (
            <div className="flex items-center gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/20">
              <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-red-600">Purge complète irréversible</p>
                <p className="text-[11px] text-muted-foreground">Toutes les données de test seront supprimées et les compteurs remis à zéro.</p>
              </div>
              <div className="flex gap-2">
                <Button size="sm" variant="destructive" className="gap-1" disabled={purging === 'full'}
                  onClick={handleFullPurge} data-testid="confirm-full-purge"
                >
                  {purging === 'full' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                  Purger tout
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setConfirmTarget(null)}>Annuler</Button>
              </div>
            </div>
          ) : (
            <Button variant="outline" className="w-full gap-2 text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
              onClick={() => setConfirmTarget('full')} data-testid="full-purge-btn"
            >
              <AlertTriangle className="w-4 h-4" /> Purge complète — Tout supprimer pour la production
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};


export const AdminDashboard = () => {
  const [contacts, setContacts] = useState([]);
  const [avis, setAvis] = useState([]);
  const [stats, setStats] = useState({ total: 0, nouveau: 0, en_cours: 0, traite: 0 });
  const [avisStats, setAvisStats] = useState({ total: 0, en_attente: 0, publie: 0, rejete: 0 });
  const [referralData, setReferralData] = useState({ codes: [], recent_uses: [], stats: { total_codes: 0, active_codes: 0, total_uses: 0, total_discount_given: 0 } });
  const [bookings, setBookings] = useState([]);
  const [relanceData, setRelanceData] = useState({ items: [], stats: { total: 0, not_sent: 0, sent: 0 } });
  const [clients, setClients] = useState([]);
  const [urgentAlerts, setUrgentAlerts] = useState({ items: [], total: 0, non_traite: 0 });
  const [strategiiaData, setStrategiiaData] = useState({ total_analyses: 0, premium: 0, total_cases: 0, recent: [] });
  const [casAnonymises, setCasAnonymises] = useState({ items: [], total: 0 });
  const [premiumAnalyses, setPremiumAnalyses] = useState({ items: [], stats: { total: 0, en_attente: 0, en_cours: 0, valide: 0, envoye: 0, termine: 0 } });
  const [reviewDialog, setReviewDialog] = useState(null);
  const [dossierExpressAdmin, setDossierExpressAdmin] = useState({ items: [], stats: { total: 0, completed: 0, processing: 0, errors: 0, incidents: 0, delivered: 0, pending: 0 } });
  const [dossierViewDialog, setDossierViewDialog] = useState(null);
  const [deFilter, setDeFilter] = useState('all');
  const [monitoring, setMonitoring] = useState(null);
  const [launchMode, setLaunchMode] = useState({ mode: 'ouvert', message: '' });
  const [launchLoading, setLaunchLoading] = useState(false);
  const [servicesStatus, setServicesStatus] = useState(null);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsPeriod, setAnalyticsPeriod] = useState('30d');
  const [newCas, setNewCas] = useState({ type_dossier: '', regime: '', duree: '', strategie: '', resultat: '', score_pertinence: 0, notes: '' });
  const [editCas, setEditCas] = useState(null);
  const [casFilter, setCasFilter] = useState('');
  const [casTypeFilter, setCasTypeFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedContact, setSelectedContact] = useState(null);
  const [selectedAvis, setSelectedAvis] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showAvisModal, setShowAvisModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [contactToDelete, setContactToDelete] = useState(null);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [notesAdmin, setNotesAdmin] = useState('');
  const [activeTab, setActiveTab] = useState('contacts');
  const [canalFilter, setCanalFilter] = useState('all');
  const [sourceFilter, setSourceFilter] = useState('all');
  const [showConversionForm, setShowConversionForm] = useState(false);
  const [conversionMontant, setConversionMontant] = useState('');
  const [conversionPrestation, setConversionPrestation] = useState('');
  const [adminDocs, setAdminDocs] = useState({ documents: [], stats: {} });
  const [s3Docs, setS3Docs] = useState({ documents: [], total: 0 });
  const [s3Stats, setS3Stats] = useState({ total: 0, by_source: [] });
  const [s3Timeline, setS3Timeline] = useState({ timeline: [], total_size: 0, total_files: 0, by_type: [] });
  const [s3AlertConfig, setS3AlertConfig] = useState({ enabled: true, thresholds: [], notify_email: true });
  const [s3AlertCheck, setS3AlertCheck] = useState({ alerts: [], current_size: 0, enabled: true });
  const [emailStatus, setEmailStatus] = useState(null);
  const [docStatusFilter, setDocStatusFilter] = useState('');
  const [completenessNotifs, setCompletenessNotifs] = useState({ notifications: [], total: 0, stats: {}, by_threshold: {} });
  const [inactivityReminders, setInactivityReminders] = useState({ reminders: [], total: 0, stats: {}, by_level: {} });
  const [runningReminders, setRunningReminders] = useState(false);
  const [lastReminderResults, setLastReminderResults] = useState(null);
  const [cronStatus, setCronStatus] = useState({ enabled: true, hour: 9, minute: 0, last_run: null, last_results: null });
  const [engagementKpis, setEngagementKpis] = useState(null);
  const [kpiAlerts, setKpiAlerts] = useState({ alerts: [] });
  const [kpiAlertConfig, setKpiAlertConfig] = useState({ open_rate_threshold: 30, click_rate_threshold: 10, alerts_enabled: true });
  const [abTests, setAbTests] = useState([]);
  const [abResults, setAbResults] = useState({});
  const [creatingAb, setCreatingAb] = useState(false);
  const [showTour, setShowTour] = useState(false);

  const navigate = useNavigate();
  const { token, adminName, logout } = useAuth();
  const { isAdminMode, setIsAdminMode } = useAdminTest();
  const { isDark, toggle: toggleTheme } = useAdminTheme();

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Auto-start onboarding tour on first admin login
  useEffect(() => {
    if (!loading && !localStorage.getItem(TOUR_KEY)) {
      const timer = setTimeout(() => setShowTour(true), 1800);
      return () => clearTimeout(timer);
    }
  }, [loading]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [contactsRes, statsRes, avisRes, avisStatsRes, referralsRes, bookingsRes, relanceRes, clientsRes, alertesRes, strategiiaRes, casRes, premiumRes, analyticsRes] = await Promise.all([
        axios.get(`${API}/admin/contacts`, axiosConfig),
        axios.get(`${API}/admin/stats`, axiosConfig),
        axios.get(`${API}/admin/avis`, axiosConfig),
        axios.get(`${API}/admin/avis/stats`, axiosConfig),
        axios.get(`${API}/admin/referrals`, axiosConfig).catch(() => ({ data: { codes: [], recent_uses: [], stats: { total_codes: 0, active_codes: 0, total_uses: 0, total_discount_given: 0 } } })),
        axios.get(`${API}/admin/bookings`, axiosConfig).catch(() => ({ data: [] })),
        axios.get(`${API}/admin/relance`, axiosConfig).catch(() => ({ data: { items: [], stats: { total: 0, not_sent: 0, sent: 0 } } })),
        axios.get(`${API}/admin/clients`, axiosConfig).catch(() => ({ data: [] })),
        axios.get(`${API}/admin/alertes-urgentes`, axiosConfig).catch(() => ({ data: { items: [], total: 0, non_traite: 0 } })),
        axios.get(`${API}/admin/strategiia/stats`, axiosConfig).catch(() => ({ data: { total_analyses: 0, premium: 0, total_cases: 0, recent: [] } })),
        axios.get(`${API}/admin/cas-anonymisés`, axiosConfig).catch(() => ({ data: { items: [], total: 0 } })),
        axios.get(`${API}/admin/premium-analyses`, axiosConfig).catch(() => ({ data: { items: [], stats: { total: 0, en_attente: 0, en_cours: 0, termine: 0 } } })),
        axios.get(`${API}/admin/analytics?period=30d`, axiosConfig).catch(() => ({ data: null }))
      ]);
      setContacts(contactsRes.data);
      setStats(statsRes.data);
      setAvis(avisRes.data);
      setAvisStats(avisStatsRes.data);
      setReferralData(referralsRes.data);
      setBookings(bookingsRes.data);
      setRelanceData(relanceRes.data);
      setClients(clientsRes.data);
      setUrgentAlerts(alertesRes.data);
      setStrategiiaData(strategiiaRes.data);
      setCasAnonymises(casRes.data);
      setPremiumAnalyses(premiumRes.data);
      setAnalyticsData(analyticsRes.data);
      // Fetch admin docs & email status separately (non-critical)
      axios.get(`${API}/admin/dossier-express`, axiosConfig).then(r => setDossierExpressAdmin(r.data)).catch(() => {});
      axios.get(`${API}/admin/monitoring`, axiosConfig).then(r => setMonitoring(r.data)).catch(() => {});
      axios.get(`${API}/admin/launch-mode`, axiosConfig).then(r => setLaunchMode(r.data)).catch(() => {});
      axios.get(`${API}/admin/services-status`, axiosConfig).then(r => setServicesStatus(r.data)).catch(() => {});
      axios.get(`${API}/admin/documents`, axiosConfig).then(r => setAdminDocs(r.data)).catch(() => {});
      axios.get(`${API}/documents`, axiosConfig).then(r => setS3Docs(r.data)).catch(() => {});
      axios.get(`${API}/documents/stats`, axiosConfig).then(r => setS3Stats(r.data)).catch(() => {});
      axios.get(`${API}/documents/timeline`, axiosConfig).then(r => setS3Timeline(r.data)).catch(() => {});
      axios.get(`${API}/documents/storage-alerts/config`, axiosConfig).then(r => setS3AlertConfig(r.data)).catch(() => {});
      axios.get(`${API}/documents/storage-alerts/check`, axiosConfig).then(r => setS3AlertCheck(r.data)).catch(() => {});
      axios.get(`${API}/admin/email/status`, axiosConfig).then(r => setEmailStatus(r.data)).catch(() => {});
      axios.get(`${API}/admin/completeness-notifications`, axiosConfig).then(r => setCompletenessNotifs(r.data)).catch(() => {});
      axios.get(`${API}/admin/relance-inactivité/history`, axiosConfig).then(r => setInactivityReminders(r.data)).catch(() => {});
      axios.get(`${API}/admin/reminder-cron/status`, axiosConfig).then(r => setCronStatus(r.data)).catch(() => {});
      axios.get(`${API}/admin/engagement-kpis`, axiosConfig).then(r => setEngagementKpis(r.data)).catch(() => {});
      axios.get(`${API}/admin/kpi-alerts/check`, axiosConfig).then(r => setKpiAlerts(r.data)).catch(() => {});
      axios.get(`${API}/admin/kpi-alerts/config`, axiosConfig).then(r => setKpiAlertConfig(r.data)).catch(() => {});
      axios.get(`${API}/admin/ab-tests`, axiosConfig).then(async r => {
        setAbTests(r.data.tests || []);
        const results = {};
        for (const t of (r.data.tests || []).slice(0, 5)) {
          try { const res = await axios.get(`${API}/admin/ab-tests/${t.id}/results`, axiosConfig); results[t.id] = res.data; } catch {}
        }
        setAbResults(results);
      }).catch(() => {});
    } catch (error) {
      console.error('Erreur:', error);
      if (error.response?.status === 401) {
        logout();
        navigate('/admin/login');
      } else {
        toast.error("Erreur lors du chargement des données");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/admin/login');
    toast.success("Déconnexion réussie");
  };

  const handleViewContact = (contact) => {
    setSelectedContact(contact);
    setNotesAdmin(contact.notes_admin || '');
    setShowDetailModal(true);
  };

  const handleViewAvis = (avisItem) => {
    setSelectedAvis(avisItem);
    setShowAvisModal(true);
  };

  const handleUpdateStatus = async (contactId, newStatus) => {
    setUpdatingStatus(true);
    try {
      await axios.patch(
        `${API}/admin/contacts/${contactId}`,
        { status: newStatus, notes_admin: notesAdmin },
        axiosConfig
      );
      toast.success("Statut mis à jour");
      fetchData();
      if (selectedContact?.id === contactId) {
        setSelectedContact(prev => ({ ...prev, status: newStatus, notes_admin: notesAdmin }));
      }
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleConversion = async (contactId) => {
    setUpdatingStatus(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      await axios.patch(
        `${API}/admin/contacts/${contactId}`,
        {
          status: 'converti',
          conversion_montant: parseFloat(conversionMontant) || 0,
          conversion_prestation: conversionPrestation || null,
          conversion_date: today,
          notes: notesAdmin || undefined,
        },
        axiosConfig
      );
      toast.success('Lead marque comme converti');
      setShowConversionForm(false);
      setConversionMontant('');
      setConversionPrestation('');
      fetchData();
      setSelectedContact(prev => ({
        ...prev,
        status: 'converti',
        conversion_montant: parseFloat(conversionMontant) || 0,
        conversion_prestation: conversionPrestation,
        conversion_date: today,
      }));
    } catch {
      toast.error('Erreur lors de la conversion');
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleUpdateAvisStatus = async (avisId, newStatus) => {
    setUpdatingStatus(true);
    try {
      await axios.patch(
        `${API}/admin/avis/${avisId}`,
        { status: newStatus },
        axiosConfig
      );
      toast.success(newStatus === 'publie' ? "Avis publié" : "Avis rejeté");
      fetchData();
      setShowAvisModal(false);
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleDeleteContact = async () => {
    if (!contactToDelete) return;
    
    try {
      await axios.delete(`${API}/admin/contacts/${contactToDelete.id}`, axiosConfig);
      toast.success("Contact supprimé");
      setShowDeleteModal(false);
      setShowDetailModal(false);
      setContactToDelete(null);
      fetchData();
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  const handleDeleteAvis = async (avisId) => {
    try {
      await axios.delete(`${API}/admin/avis/${avisId}`, axiosConfig);
      toast.success("Avis supprimé");
      setShowAvisModal(false);
      fetchData();
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      nouveau: { variant: "default", icon: AlertCircle, label: "Nouveau" },
      en_cours: { variant: "secondary", icon: Clock, label: "En cours" },
      traite: { variant: "outline", icon: CheckCircle, label: "Traite" },
      converti: { variant: "default", icon: BadgeCheck, label: "Converti", className: "bg-emerald-600 text-white" }
    };
    const config = styles[status] || styles.nouveau;
    return (
      <Badge variant={config.variant} className={`gap-1 ${config.className || ''}`}>
        <config.icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };

  const getAvisStatusBadge = (status) => {
    const styles = {
      en_attente: { variant: "default", icon: Clock, label: "En attente", className: "bg-amber-500" },
      publie: { variant: "secondary", icon: CheckCircle, label: "Publié", className: "bg-green-500 text-white" },
      rejete: { variant: "destructive", icon: XCircle, label: "Rejeté" }
    };
    const config = styles[status] || styles.en_attente;
    return (
      <Badge variant={config.variant} className={`gap-1 ${config.className || ''}`}>
        <config.icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };

  const filteredContacts = contacts.filter(contact => {
    const matchesSearch = 
      contact.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.prenom.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.sujet.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || contact.status === statusFilter;
    const matchesCanal = canalFilter === 'all' || (contact.tracking_via || 'direct') === canalFilter;
    const matchesSource = sourceFilter === 'all' || (sourceFilter === 'direct' ? !contact.tracking_source : contact.tracking_source === sourceFilter);
    
    return matchesSearch && matchesStatus && matchesCanal && matchesSource;
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderStars = (note) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star 
        key={i} 
        className={`w-4 h-4 ${i < note ? 'text-amber-400 fill-amber-400' : 'text-gray-300'}`} 
      />
    ));
  };

  return (
    <div className={`min-h-screen bg-background transition-colors duration-300 ${isDark ? 'admin-dark' : ''}`}>
      {/* Header */}
      <header className="bg-foreground text-primary-foreground sticky top-0 z-50 border-b border-white/5 transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-3">
              <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                <Heart className="w-5 h-5 text-accent" strokeWidth={1.5} />
                <span className="font-semibold text-sm" style={{ fontFamily: "'Playfair Display', serif" }}>
                  S.E.S
                </span>
              </Link>
              <div className="w-px h-5 bg-white/15 hidden sm:block" />
              <span className="text-xs text-primary-foreground/50 hidden sm:inline font-medium tracking-wide uppercase">Administration</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs hidden sm:inline text-primary-foreground/70">{adminName}</span>
              <button
                onClick={() => setIsAdminMode(prev => !prev)}
                data-testid="admin-test-toggle"
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium transition-all border ${
                  isAdminMode
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 hover:bg-amber-500/30'
                    : 'bg-white/10 text-primary-foreground/60 border-white/20 hover:bg-white/20'
                }`}
              >
                <Shield className="w-3 h-3" />
                {isAdminMode ? 'Test Admin' : 'Test Client'}
              </button>
              <button
                onClick={toggleTheme}
                data-testid="admin-dark-toggle"
                className={`flex items-center justify-center w-8 h-8 rounded-md transition-all border ${
                  isDark
                    ? 'bg-amber-500/15 text-amber-300 border-amber-500/30 hover:bg-amber-500/25'
                    : 'bg-white/10 text-primary-foreground/60 border-white/20 hover:bg-white/20'
                }`}
                title={isDark ? 'Mode clair' : 'Mode sombre'}
              >
                {isDark ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
              </button>
              <Link to="/">
                <Button variant="ghost" size="sm" className="text-primary-foreground/70 hover:bg-primary-foreground/10 h-8 w-8 p-0" data-testid="admin-home-button">
                  <Home className="w-4 h-4" />
                </Button>
              </Link>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={handleLogout}
                className="text-primary-foreground/70 hover:bg-primary-foreground/10 gap-1.5 h-8 text-xs"
                data-testid="admin-logout-button"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Quitter</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          {/* Mobile: Select dropdown — visible < md */}
          <div className="md:hidden" data-testid="admin-tabs-mobile">
            <select
              value={activeTab}
              onChange={(e) => setActiveTab(e.target.value)}
              className="w-full h-11 px-4 text-sm font-medium rounded-xl border border-border/60 bg-card/80 backdrop-blur shadow-sm appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-accent/40"
              style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 12px center' }}
              data-testid="admin-tab-select"
            >
              <optgroup label="Gestion">
                <option value="contacts">Contacts</option>
                <option value="avis">Avis</option>
                <option value="referrals">Parrainage</option>
                <option value="bookings">RDV</option>
                <option value="clients">Clients</option>
                <option value="relance">Relance</option>
                <option value="alertes">{`Alertes${urgentAlerts.non_traite > 0 ? ` (${urgentAlerts.non_traite})` : ''}`}</option>
              </optgroup>
              <optgroup label="IA & Production">
                <option value="strategiia">{`StrategiIA${premiumAnalyses.items.filter(i => i.type === 'strategiia' && i.status === 'en_attente').length > 0 ? ` (${premiumAnalyses.items.filter(i => i.type === 'strategiia' && i.status === 'en_attente').length})` : ''}`}</option>
                <option value="dossier-express">{`Dossier Express${premiumAnalyses.items.filter(i => i.type === 'dossier_express' && i.status === 'en_attente').length > 0 ? ` (${premiumAnalyses.items.filter(i => i.type === 'dossier_express' && i.status === 'en_attente').length})` : ''}`}</option>
              </optgroup>
              <optgroup label="Suivi">
                <option value="analytics">Analytique</option>
                <option value="documents">Documents</option>
                <option value="conseils-strate">Strate</option>
              </optgroup>
              <optgroup label="Configuration">
                <option value="config">Config</option>
                <option value="notifications">Notifications</option>
                <option value="templates">Templates</option>
              </optgroup>
            </select>
          </div>

          {/* Desktop: Horizontal tabs — visible >= md */}
          <div className="hidden md:block overflow-x-auto -mx-4 px-4 pb-1 scrollbar-thin" data-testid="admin-tabs-nav">
            <TabsList className="inline-flex w-auto min-w-full gap-0.5 bg-card/80 backdrop-blur border border-border/60 p-1.5 rounded-xl shadow-sm">
              <TabsTrigger value="contacts" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all">
                <Users className="w-3.5 h-3.5" />
                Contacts
              </TabsTrigger>
              <TabsTrigger value="avis" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all">
                <MessageSquare className="w-3.5 h-3.5" />
                Avis
              </TabsTrigger>
              <TabsTrigger value="referrals" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all" data-testid="tab-referrals">
                <Gift className="w-3.5 h-3.5" />
                Parrainage
              </TabsTrigger>
              <TabsTrigger value="bookings" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all" data-testid="tab-bookings">
                <Calendar className="w-3.5 h-3.5" />
                RDV
              </TabsTrigger>
              <TabsTrigger value="clients" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all" data-testid="tab-clients">
                <FolderOpen className="w-3.5 h-3.5" />
                Clients
              </TabsTrigger>
              <TabsTrigger value="relance" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all" data-testid="tab-relance">
                <Send className="w-3.5 h-3.5" />
                Relance
              </TabsTrigger>
              <TabsTrigger value="alertes" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all relative" data-testid="tab-alertes">
                <Zap className="w-3.5 h-3.5" />
                Alertes
                {urgentAlerts.non_traité > 0 && (
                  <span className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center ring-2 ring-background">{urgentAlerts.non_traite}</span>
                )}
              </TabsTrigger>

              <div className="w-px h-6 bg-border/60 mx-1 self-center flex-shrink-0" />

              <TabsTrigger value="strategiia" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all relative" data-testid="tab-strategiia">
                <Brain className="w-3.5 h-3.5" />
                StratégiIA
                {premiumAnalyses.items.filter(i => i.type === 'strategiia' && i.status === 'en_attente').length > 0 && (
                  <span className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-amber-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center ring-2 ring-background">{premiumAnalyses.items.filter(i => i.type === 'strategiia' && i.status === 'en_attente').length}</span>
                )}
              </TabsTrigger>
              <TabsTrigger value="dossier-express" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all relative" data-testid="tab-dossier-express">
                <FileSearch className="w-3.5 h-3.5 text-amber-600" />
                Dossier Express
                {premiumAnalyses.items.filter(i => i.type === 'dossier_express' && i.status === 'en_attente').length > 0 && (
                  <span className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-amber-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center ring-2 ring-background">{premiumAnalyses.items.filter(i => i.type === 'dossier_express' && i.status === 'en_attente').length}</span>
                )}
              </TabsTrigger>

              <div className="w-px h-6 bg-border/60 mx-1 self-center flex-shrink-0" />

              <TabsTrigger value="analytics" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all" data-testid="tab-analytics">
                <BarChart3 className="w-3.5 h-3.5 text-emerald-600" />
                Analytique
              </TabsTrigger>
              <TabsTrigger value="documents" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all" data-testid="tab-admin-documents">
                <FileText className="w-3.5 h-3.5 text-teal-600" />
                Documents
              </TabsTrigger>
              <TabsTrigger value="conseils-strate" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all" data-testid="tab-conseils-strate">
                <Star className="w-3.5 h-3.5 text-[#C9A84C]" />
                Straté
              </TabsTrigger>
              <TabsTrigger value="feedback" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all" data-testid="tab-feedback">
                <MessageSquare className="w-3.5 h-3.5 text-indigo-600" />
                Feedback
              </TabsTrigger>

              <div className="w-px h-6 bg-border/60 mx-1 self-center flex-shrink-0" />

              <TabsTrigger value="config" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all" data-testid="tab-config">
                <Settings className="w-3.5 h-3.5 text-gray-500" />
                Config
              </TabsTrigger>
              <TabsTrigger value="notifications" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all" data-testid="tab-notifications">
                <BellRing className="w-3.5 h-3.5 text-amber-500" />
                Notifs
              </TabsTrigger>
              <TabsTrigger value="templates" className="gap-1.5 text-xs whitespace-nowrap px-3 py-2 rounded-lg data-[state=active]:bg-foreground data-[state=active]:text-primary-foreground data-[state=active]:shadow-md transition-all" data-testid="tab-templates">
                <PenTool className="w-3.5 h-3.5 text-violet-500" />
                Templates
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Contacts Tab */}
          <TabsContent value="contacts" className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
              <Card data-testid="stat-total">
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center">
                    <Users className="w-6 h-6 text-foreground" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats.total}</p>
                    <p className="text-sm text-muted-foreground">Total</p>
                  </div>
                </CardContent>
              </Card>
              <Card data-testid="stat-nouveau">
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                    <AlertCircle className="w-6 h-6 text-accent" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats.nouveau}</p>
                    <p className="text-sm text-muted-foreground">Nouveaux</p>
                  </div>
                </CardContent>
              </Card>
              <Card data-testid="stat-en-cours">
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-secondary rounded-lg flex items-center justify-center">
                    <Clock className="w-6 h-6 text-foreground" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats.en_cours}</p>
                    <p className="text-sm text-muted-foreground">En cours</p>
                  </div>
                </CardContent>
              </Card>
              <Card data-testid="stat-traite">
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-foreground" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats.traite}</p>
                    <p className="text-sm text-muted-foreground">Traites</p>
                  </div>
                </CardContent>
              </Card>
              <Card data-testid="stat-converti">
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-emerald-50 rounded-lg flex items-center justify-center">
                    <BadgeCheck className="w-6 h-6 text-emerald-600" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-emerald-600">{stats.converti || 0}</p>
                    <p className="text-sm text-muted-foreground">Convertis</p>
                    {stats.total_revenue > 0 && <p className="text-xs text-emerald-600 font-medium">{formatEuro(stats.total_revenue)}</p>}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col sm:flex-row gap-3">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      placeholder="Rechercher par nom, email ou sujet..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                      data-testid="search-input"
                    />
                  </div>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-full sm:w-36" data-testid="status-filter">
                      <SelectValue placeholder="Statut" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Tous statuts</SelectItem>
                      <SelectItem value="nouveau">Nouveaux</SelectItem>
                      <SelectItem value="en_cours">En cours</SelectItem>
                      <SelectItem value="traite">Traites</SelectItem>
                      <SelectItem value="converti">Convertis</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={canalFilter} onValueChange={setCanalFilter}>
                    <SelectTrigger className="w-full sm:w-36" data-testid="canal-filter">
                      <SelectValue placeholder="Canal" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Tous canaux</SelectItem>
                      <SelectItem value="qr">QR Code</SelectItem>
                      <SelectItem value="email">Email</SelectItem>
                      <SelectItem value="pdf_link">Lien PDF</SelectItem>
                      <SelectItem value="direct">Contact direct</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={sourceFilter} onValueChange={setSourceFilter}>
                    <SelectTrigger className="w-full sm:w-44" data-testid="source-filter">
                      <SelectValue placeholder="Source" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Toutes sources</SelectItem>
                      <SelectItem value="dossier_express">Dossier Express IA</SelectItem>
                      <SelectItem value="strategiia">StrategiIA</SelectItem>
                      <SelectItem value="direct">Contact direct</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="outline" onClick={fetchData} className="gap-2" data-testid="refresh-button">
                    <RefreshCw className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Contacts List */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Demandes de contact</span>
                  <span className="text-sm font-normal text-muted-foreground">
                    {filteredContacts.length} résultat(s)
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center py-12" data-testid="loading-state">
                    <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                  </div>
                ) : filteredContacts.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground" data-testid="empty-state">
                    <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Aucune demande de contact trouvée</p>
                  </div>
                ) : (
                  <div className="space-y-4" data-testid="contacts-list">
                    {filteredContacts.map((contact) => (
                      <div 
                        key={contact.id}
                        className="border border-border rounded-lg p-4 hover:bg-muted/30 transition-colors cursor-pointer"
                        onClick={() => handleViewContact(contact)}
                        data-testid={`contact-item-${contact.id}`}
                      >
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1 flex-wrap">
                              <h3 className="font-semibold truncate">
                                {contact.prenom} {contact.nom}
                              </h3>
                              {getStatusBadge(contact.status)}
                              {contact.tracking_via && (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-50 text-amber-700 border border-amber-200" data-testid={`origin-tag-${contact.id}`}>
                                  {contact.tracking_via === 'qr' && <QrCode className="w-2.5 h-2.5" />}
                                  {contact.tracking_via === 'email' && <Mail className="w-2.5 h-2.5" />}
                                  {contact.tracking_via === 'pdf_link' && <FileText className="w-2.5 h-2.5" />}
                                  {contact.tracking_via === 'qr' ? 'QR PDF' : contact.tracking_via === 'email' ? 'Email' : contact.tracking_via === 'pdf_link' ? 'Lien PDF' : contact.tracking_via}
                                </span>
                              )}
                              {contact.tracking_source && (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-50 text-blue-700 border border-blue-200" data-testid={`source-tag-${contact.id}`}>
                                  {contact.tracking_source === 'dossier_express' ? 'Dossier Express' : contact.tracking_source === 'strategiia' ? 'StrategiIA' : contact.tracking_source}
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-muted-foreground truncate mb-2">
                              {contact.sujet}
                            </p>
                            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <Mail className="w-3 h-3" />
                                {contact.email}
                              </span>
                              {contact.telephone && (
                                <span className="flex items-center gap-1">
                                  <Phone className="w-3 h-3" />
                                  {contact.telephone}
                                </span>
                              )}
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {formatDate(contact.created_at)}
                              </span>
                            </div>
                          </div>
                          <Button variant="ghost" size="sm" className="gap-2">
                            <Eye className="w-4 h-4" />
                            Voir
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Avis Tab */}
          <TabsContent value="avis" className="space-y-6">
            {/* Avis Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center">
                    <MessageSquare className="w-6 h-6 text-foreground" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{avisStats.total}</p>
                    <p className="text-sm text-muted-foreground">Total</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center">
                    <Clock className="w-6 h-6 text-amber-600" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{avisStats.en_attente}</p>
                    <p className="text-sm text-muted-foreground">En attente</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-green-600" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{avisStats.publie}</p>
                    <p className="text-sm text-muted-foreground">Publiés</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                    <XCircle className="w-6 h-6 text-red-600" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{avisStats.rejete}</p>
                    <p className="text-sm text-muted-foreground">Rejetés</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Avis List */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Témoignages</span>
                  <Button variant="outline" size="sm" onClick={fetchData} className="gap-2">
                    <RefreshCw className="w-4 h-4" />
                    Actualiser
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                  </div>
                ) : avis.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Aucun témoignage</p>
                  </div>
                ) : (
                  <div className="space-y-4" data-testid="avis-list">
                    {avis.map((item) => (
                      <div 
                        key={item.id}
                        className="border border-border rounded-lg p-4 hover:bg-muted/30 transition-colors cursor-pointer"
                        onClick={() => handleViewAvis(item)}
                        data-testid={`avis-admin-item-${item.id}`}
                      >
                        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="font-semibold">{item.nom}</span>
                              {getAvisStatusBadge(item.status)}
                            </div>
                            <div className="flex items-center gap-1 mb-2">
                              {renderStars(item.note)}
                            </div>
                            <p className="text-sm text-muted-foreground line-clamp-2">
                              "{item.témoignage}"
                            </p>
                            <p className="text-xs text-muted-foreground mt-2">
                              {formatDate(item.created_at)}
                            </p>
                          </div>
                          {item.status === 'en_attente' && (
                            <div className="flex gap-2">
                              <Button 
                                size="sm" 
                                onClick={(e) => { e.stopPropagation(); handleUpdateAvisStatus(item.id, 'publie'); }}
                                className="gap-1 bg-green-600 hover:bg-green-700"
                              >
                                <CheckCircle className="w-4 h-4" />
                                Publier
                              </Button>
                              <Button 
                                size="sm" 
                                variant="destructive"
                                onClick={(e) => { e.stopPropagation(); handleUpdateAvisStatus(item.id, 'rejete'); }}
                                className="gap-1"
                              >
                                <XCircle className="w-4 h-4" />
                                Rejeter
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          {/* Referrals Tab */}
          <TabsContent value="referrals" className="space-y-6">
            {/* Referral Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <Card data-testid="referral-stat-codes">
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                    <Hash className="w-6 h-6 text-accent" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{referralData.stats.total_codes}</p>
                    <p className="text-sm text-muted-foreground">Codes créés</p>
                  </div>
                </CardContent>
              </Card>
              <Card data-testid="referral-stat-active">
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-green-600" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{referralData.stats.active_codes}</p>
                    <p className="text-sm text-muted-foreground">Codes actifs</p>
                  </div>
                </CardContent>
              </Card>
              <Card data-testid="referral-stat-uses">
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-blue-600" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{referralData.stats.total_uses}</p>
                    <p className="text-sm text-muted-foreground">Utilisations</p>
                  </div>
                </CardContent>
              </Card>
              <Card data-testid="referral-stat-discount">
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center">
                    <Percent className="w-6 h-6 text-amber-600" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{referralData.stats.total_discount_given}%</p>
                    <p className="text-sm text-muted-foreground">Réductions totales</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Referral Codes List */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Codes parrainage</span>
                  <Button variant="outline" size="sm" onClick={fetchData} className="gap-2">
                    <RefreshCw className="w-4 h-4" />
                    Actualiser
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                  </div>
                ) : referralData.codes.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Gift className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Aucun code parrainage généré</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto" data-testid="referral-codes-table">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border">
                          <th className="text-left py-3 px-4 font-medium text-muted-foreground">Code</th>
                          <th className="text-left py-3 px-4 font-medium text-muted-foreground">Parrain</th>
                          <th className="text-left py-3 px-4 font-medium text-muted-foreground">Email</th>
                          <th className="text-center py-3 px-4 font-medium text-muted-foreground">Utilisations</th>
                          <th className="text-center py-3 px-4 font-medium text-muted-foreground">Statut</th>
                          <th className="text-left py-3 px-4 font-medium text-muted-foreground">Créé le</th>
                        </tr>
                      </thead>
                      <tbody>
                        {referralData.codes.map((code, index) => (
                          <tr 
                            key={index} 
                            className="border-b border-border/50 hover:bg-muted/30 transition-colors"
                            data-testid={`referral-row-${code.code}`}
                          >
                            <td className="py-3 px-4">
                              <span className="font-mono font-bold text-foreground bg-muted px-2 py-1 rounded">
                                {code.code}
                              </span>
                            </td>
                            <td className="py-3 px-4">{code.referrer_name || '—'}</td>
                            <td className="py-3 px-4 text-muted-foreground">{code.referrer_email}</td>
                            <td className="py-3 px-4 text-center">
                              <Badge variant={code.uses_count > 0 ? "default" : "secondary"}>
                                {code.uses_count || 0}
                              </Badge>
                            </td>
                            <td className="py-3 px-4 text-center">
                              {code.is_active ? (
                                <Badge className="bg-green-500 text-white gap-1">
                                  <CheckCircle className="w-3 h-3" />
                                  Actif
                                </Badge>
                              ) : (
                                <Badge variant="secondary" className="gap-1">
                                  <XCircle className="w-3 h-3" />
                                  Inactif
                                </Badge>
                              )}
                            </td>
                            <td className="py-3 px-4 text-muted-foreground text-xs">
                              {code.created_at ? formatDate(code.created_at) : '—'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Uses */}
            {referralData.recent_uses.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Dernières utilisations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3" data-testid="referral-uses-list">
                    {referralData.recent_uses.map((use, index) => (
                      <div 
                        key={index} 
                        className="flex items-center justify-between border-b border-border/50 last:border-0 pb-3 last:pb-0"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-accent/10 rounded-lg flex items-center justify-center">
                            <Gift className="w-4 h-4 text-accent" />
                          </div>
                          <div>
                            <p className="text-sm font-medium">
                              <span className="font-mono bg-muted px-1.5 py-0.5 rounded text-xs">{use.referral_code}</span>
                              {' '} utilisé par {use.referred_name || use.referred_email || 'Anonyme'}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {use.created_at ? formatDate(use.created_at) : '—'}
                            </p>
                          </div>
                        </div>
                        <Badge variant="outline" className="text-green-600">
                          -{use.discount_applied}%
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
          {/* Bookings Tab */}
          <TabsContent value="bookings" className="space-y-6">
            <div className="grid grid-cols-3 gap-4">
              <Card><CardContent className="p-4 flex items-center gap-3">
                <Calendar className="w-8 h-8 text-accent" strokeWidth={1.5} />
                <div><p className="text-2xl font-bold">{bookings.length}</p><p className="text-xs text-muted-foreground">Total RDV</p></div>
              </CardContent></Card>
              <Card><CardContent className="p-4 flex items-center gap-3">
                <CheckCircle className="w-8 h-8 text-green-500" strokeWidth={1.5} />
                <div><p className="text-2xl font-bold">{bookings.filter(b => b.status === 'confirme').length}</p><p className="text-xs text-muted-foreground">Confirmés</p></div>
              </CardContent></Card>
              <Card><CardContent className="p-4 flex items-center gap-3">
                <Clock className="w-8 h-8 text-blue-500" strokeWidth={1.5} />
                <div><p className="text-2xl font-bold">{bookings.filter(b => b.status === 'termine').length}</p><p className="text-xs text-muted-foreground">Terminés</p></div>
              </CardContent></Card>
            </div>

            <Card>
              <CardHeader><CardTitle>Rendez-vous</CardTitle></CardHeader>
              <CardContent>
                {bookings.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Aucun rendez-vous</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto" data-testid="bookings-table">
                    <table className="w-full text-sm">
                      <thead><tr className="border-b border-border">
                        <th className="text-left py-3 px-3 font-medium text-muted-foreground">Date</th>
                        <th className="text-left py-3 px-3 font-medium text-muted-foreground">Heure</th>
                        <th className="text-left py-3 px-3 font-medium text-muted-foreground">Type</th>
                        <th className="text-left py-3 px-3 font-medium text-muted-foreground">Client</th>
                        <th className="text-left py-3 px-3 font-medium text-muted-foreground">Email</th>
                        <th className="text-center py-3 px-3 font-medium text-muted-foreground">Statut</th>
                      </tr></thead>
                      <tbody>
                        {bookings.map((b, i) => (
                          <tr key={i} className="border-b border-border/50 hover:bg-muted/30">
                            <td className="py-3 px-3 font-medium">{b.date}</td>
                            <td className="py-3 px-3">{b.time_slot}</td>
                            <td className="py-3 px-3">
                              <span className="flex items-center gap-1">
                                {b.booking_type === 'visio' ? <Video className="w-3 h-3" /> : <Phone className="w-3 h-3" />}
                                {b.booking_type === 'visio' ? 'Visio' : 'Tél.'}
                              </span>
                            </td>
                            <td className="py-3 px-3">{b.name}</td>
                            <td className="py-3 px-3 text-muted-foreground">{b.email}</td>
                            <td className="py-3 px-3 text-center">
                              <Badge className={b.status === 'confirme' ? 'bg-green-500 text-white' : b.status === 'annule' ? 'bg-red-500 text-white' : 'bg-blue-500 text-white'}>
                                {b.status === 'confirme' ? 'Confirmé' : b.status === 'annule' ? 'Annulé' : 'Terminé'}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Clients Tab */}
          <TabsContent value="clients" className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <Card><CardContent className="p-4 flex items-center gap-3">
                <Users className="w-8 h-8 text-accent" strokeWidth={1.5} />
                <div><p className="text-2xl font-bold">{clients.length}</p><p className="text-xs text-muted-foreground">Clients inscrits</p></div>
              </CardContent></Card>
              <Card><CardContent className="p-4 flex items-center gap-3">
                <FolderOpen className="w-8 h-8 text-blue-500" strokeWidth={1.5} />
                <div><p className="text-2xl font-bold">{clients.reduce((s, c) => s + (c.cases_count || 0), 0)}</p><p className="text-xs text-muted-foreground">Dossiers total</p></div>
              </CardContent></Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Gestion des clients</span>
                  <Button variant="outline" size="sm" onClick={fetchData} className="gap-2">
                    <RefreshCw className="w-4 h-4" /> Actualiser
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {clients.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Aucun client inscrit</p>
                  </div>
                ) : (
                  <div className="space-y-4" data-testid="clients-list">
                    {clients.map((client) => (
                      <div key={client.id} className="border border-border rounded-lg p-4" data-testid={`client-row-${client.id}`}>
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-3 gap-2">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                              <User className="w-5 h-5 text-accent" strokeWidth={1.5} />
                            </div>
                            <div className="min-w-0">
                              <p className="font-semibold text-sm truncate">{client.name}</p>
                              <p className="text-xs text-muted-foreground truncate">{client.email}</p>
                            </div>
                          </div>
                          <Badge variant="secondary" className="self-start sm:self-auto">{client.cases_count || 0} dossier(s)</Badge>
                        </div>
                        
                        {/* Quick actions */}
                        <div className="flex flex-wrap gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            className="gap-1 text-xs"
                            onClick={async () => {
                              const title = prompt("Titre du dossier :");
                              if (!title) return;
                              const description = prompt("Description :") || "";
                              try {
                                await axios.post(`${API}/admin/clients/${client.id}/cases`, { title, description }, axiosConfig);
                                toast.success("Dossier créé + notification envoyée au client");
                                fetchData();
                              } catch { toast.error("Erreur"); }
                            }}
                            data-testid={`create-case-${client.id}`}
                          >
                            <FolderOpen className="w-3 h-3" /> Créer un dossier
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="gap-1 text-xs text-amber-600 border-amber-200 hover:bg-amber-50"
                            onClick={async () => {
                              try {
                                await axios.post(`${API}/admin/notify-document-rejected/${client.id}`, {}, axiosConfig);
                                toast.success("Notification de documents refusés envoyée");
                              } catch { toast.error("Erreur d'envoi"); }
                            }}
                            data-testid={`notify-docs-${client.id}`}
                          >
                            <AlertTriangle className="w-3 h-3" /> Documents à renvoyer
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Relance Tab */}
          <TabsContent value="relance" className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card><CardContent className="p-4 flex items-center gap-3">
                <Mail className="w-8 h-8 text-accent" strokeWidth={1.5} />
                <div><p className="text-2xl font-bold">{relanceData.stats.total}</p><p className="text-xs text-muted-foreground">Paniers abandonnés</p></div>
              </CardContent></Card>
              <Card><CardContent className="p-4 flex items-center gap-3">
                <AlertCircle className="w-8 h-8 text-amber-500" strokeWidth={1.5} />
                <div><p className="text-2xl font-bold">{relanceData.stats.not_sent}</p><p className="text-xs text-muted-foreground">Non relancés</p></div>
              </CardContent></Card>
              <Card><CardContent className="p-4 flex items-center gap-3">
                <Send className="w-8 h-8 text-green-500" strokeWidth={1.5} />
                <div><p className="text-2xl font-bold">{relanceData.stats.sent}</p><p className="text-xs text-muted-foreground">Relancés</p></div>
              </CardContent></Card>
            </div>

            <Card>
              <CardHeader><CardTitle>Paniers abandonnés</CardTitle></CardHeader>
              <CardContent>
                {relanceData.items.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Mail className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Aucun panier abandonné</p>
                  </div>
                ) : (
                  <div className="space-y-3" data-testid="relance-list">
                    {relanceData.items.map((item, i) => (
                      <div key={i} className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 sm:p-4 border border-border rounded-lg hover:bg-muted/30 gap-2.5">
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          <div className="w-8 h-8 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
                            <Mail className="w-4 h-4 text-accent" />
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate">{item.name || item.email}</p>
                            <p className="text-xs text-muted-foreground">{item.package_name} — {item.amount}€</p>
                            <p className="text-xs text-muted-foreground">{item.created_at ? formatDate(item.created_at) : ''}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 sm:ml-4">
                          {item.relance_sent ? (
                            <Badge className="bg-green-100 text-green-800 gap-1"><CheckCircle className="w-3 h-3" />Relancé</Badge>
                          ) : (
                            <Button
                              variant="outline"
                              size="sm"
                              className="gap-1 w-full sm:w-auto"
                              onClick={async () => {
                                try {
                                  const res = await axios.post(`${API}/admin/relance/send/${item.id}`, {}, axiosConfig);
                                  toast.success(res.data.message);
                                  fetchData();
                                } catch { toast.error("Erreur"); }
                              }}
                              data-testid={`send-relance-${i}`}
                            >
                              <Send className="w-3 h-3" />Relancer
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Urgent Alerts Tab */}
          <TabsContent value="alertes" className="space-y-6" data-testid="alertes-tab-content">
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
              <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold">{urgentAlerts.total}</p><p className="text-xs text-muted-foreground">Total alertes</p></CardContent></Card>
              <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold text-red-600">{urgentAlerts.non_traite}</p><p className="text-xs text-muted-foreground">Non traitées</p></CardContent></Card>
              <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold text-green-600">{urgentAlerts.total - urgentAlerts.non_traite}</p><p className="text-xs text-muted-foreground">Traitées</p></CardContent></Card>
            </div>
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Zap className="w-5 h-5 text-red-600" />Demandes urgentes</CardTitle></CardHeader>
              <CardContent>
                {urgentAlerts.items?.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">Aucune demande urgente</p>
                ) : (
                  <div className="space-y-3">
                    {urgentAlerts.items?.map((alert) => (
                      <div key={alert.id} className={`p-3 sm:p-4 rounded-lg border ${alert.traité ? 'bg-muted/30 border-border' : 'bg-red-50 border-red-200'}`} data-testid={`alert-item-${alert.id}`}>
                        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2.5 sm:gap-4">
                          <div className="flex-1 space-y-1">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-semibold text-sm">{alert.nom}</span>
                              <Badge variant={alert.formule === '30min' ? 'destructive' : 'secondary'} className="text-[10px]">
                                {alert.formule === '30min' ? '30min — 80€' : '2h — 50€'}
                              </Badge>
                              {alert.traité ? (
                                <Badge variant="outline" className="text-green-600 border-green-300 text-[10px]">Traité</Badge>
                              ) : (
                                <Badge variant="destructive" className="text-[10px]">Nouveau</Badge>
                              )}
                            </div>
                            <div className="flex items-center gap-3 sm:gap-4 text-xs sm:text-sm text-muted-foreground flex-wrap">
                              <span className="flex items-center gap-1"><Phone className="w-3 h-3" />{alert.telephone}</span>
                              {alert.email && <span className="flex items-center gap-1 truncate"><Mail className="w-3 h-3 flex-shrink-0" /><span className="truncate">{alert.email}</span></span>}
                            </div>
                            {alert.message && <p className="text-xs sm:text-sm mt-1">{alert.message}</p>}
                            <p className="text-xs text-muted-foreground">{new Date(alert.created_at).toLocaleString('fr-FR')}</p>
                          </div>
                          {!alert.traité && (
                            <Button
                              size="sm"
                              variant="outline"
                              className="gap-1 text-green-600 border-green-300 hover:bg-green-50 w-full sm:w-auto flex-shrink-0"
                              onClick={async () => {
                                try {
                                  await axios.put(`${API}/admin/alertes-urgentes/${alert.id}`, { traite: true }, axiosConfig);
                                  toast.success('Alerte marquée comme traitée');
                                  fetchData();
                                } catch { toast.error('Erreur'); }
                              }}
                              data-testid={`mark-treated-${alert.id}`}
                            >
                              <CheckCircle className="w-3 h-3" /> Traiter
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* StratégiIA Tab */}
          <TabsContent value="strategiia" className="space-y-6" data-testid="strategiia-tab-content">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold">{strategiiaData.total_analyses}</p><p className="text-xs text-muted-foreground">Analyses totales</p></CardContent></Card>
              <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold text-accent">{strategiiaData.premium}</p><p className="text-xs text-muted-foreground">Analyses premium</p></CardContent></Card>
              <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold">{casAnonymises.total}</p><p className="text-xs text-muted-foreground">Cas anonymisés</p></CardContent></Card>
              <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold text-green-600">{strategiiaData.premium * 29}€</p><p className="text-xs text-muted-foreground">Revenus estimés</p></CardContent></Card>
            </div>

            {/* Add / Import */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <CardTitle className="flex items-center gap-2"><Plus className="w-5 h-5 text-accent" />Gestion des cas anonymisés</CardTitle>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="gap-1.5 text-xs h-8" data-testid="cas-import-btn"
                      onClick={() => {
                        const input = document.createElement('input');
                        input.type = 'file'; input.accept = '.json,.csv';
                        input.onchange = async (e) => {
                          const file = e.target.files[0];
                          if (!file) return;
                          try {
                            const text = await file.text();
                            let cases = [];
                            if (file.name.endsWith('.csv')) {
                              const lines = text.split('\n').filter(l => l.trim());
                              const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
                              for (let i = 1; i < lines.length; i++) {
                                const vals = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
                                const obj = {};
                                headers.forEach((h, j) => { obj[h] = vals[j] || ''; });
                                cases.push(obj);
                              }
                            } else {
                              const parsed = JSON.parse(text);
                              cases = Array.isArray(parsed) ? parsed : parsed.cases || [];
                            }
                            if (cases.length === 0) { toast.error('Aucun cas trouvé dans le fichier'); return; }
                            const res = await axios.post(`${API}/admin/cas-anonymisés/import`, { cases }, axiosConfig);
                            toast.success(`${res.data.imported} cas importés`);
                            fetchData();
                          } catch (err) { toast.error('Erreur lors de l\'import'); }
                        };
                        input.click();
                      }}
                    >
                      <Upload className="w-3.5 h-3.5" /> Importer (JSON/CSV)
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
                  <Select value={newCas.type_dossier} onValueChange={v => setNewCas(p => ({...p, type_dossier: v}))}>
                    <SelectTrigger data-testid="cas-type-select"><SelectValue placeholder="Type de dossier" /></SelectTrigger>
                    <SelectContent>
                      {['AT','MP','MDPH','Assurance','Expertise','Faute inexcusable','Recours','Autre'].map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <Select value={newCas.regime} onValueChange={v => setNewCas(p => ({...p, regime: v}))}>
                    <SelectTrigger data-testid="cas-regime-select"><SelectValue placeholder="Régime" /></SelectTrigger>
                    <SelectContent>
                      {['Général','MSA','Fonction publique','Indépendant','Autre'].map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <Input placeholder="Durée (ex: 18 mois)" value={newCas.duree} onChange={e => setNewCas(p => ({...p, duree: e.target.value}))} data-testid="cas-duree-input" />
                  <Input placeholder="Stratégie utilisée" value={newCas.strategie} onChange={e => setNewCas(p => ({...p, strategie: e.target.value}))} data-testid="cas-strategie-input" />
                  <Select value={newCas.resultat} onValueChange={v => setNewCas(p => ({...p, resultat: v}))}>
                    <SelectTrigger data-testid="cas-resultat-select"><SelectValue placeholder="Résultat obtenu" /></SelectTrigger>
                    <SelectContent>
                      {['Favorable','Partiellement favorable','Défavorable','En cours'].map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <Input type="number" min={0} max={100} placeholder="Score pertinence (0-100)" value={newCas.score_pertinence || ''} onChange={e => setNewCas(p => ({...p, score_pertinence: parseInt(e.target.value) || 0}))} data-testid="cas-score-input" />
                </div>
                <Input placeholder="Notes supplémentaires" value={newCas.notes} onChange={e => setNewCas(p => ({...p, notes: e.target.value}))} className="mb-3" data-testid="cas-notes-input" />
                <Button
                  onClick={async () => {
                    if (!newCas.type_dossier || !newCas.resultat) { toast.error('Type et résultat requis'); return; }
                    try {
                      await axios.post(`${API}/admin/cas-anonymisés`, newCas, axiosConfig);
                      toast.success('Cas ajouté');
                      setNewCas({ type_dossier: '', regime: '', duree: '', strategie: '', resultat: '', score_pertinence: 0, notes: '' });
                      fetchData();
                    } catch { toast.error('Erreur'); }
                  }}
                  className="gap-2 rounded-lg"
                  data-testid="cas-add-button"
                >
                  <Plus className="w-4 h-4" /> Ajouter le cas
                </Button>
              </CardContent>
            </Card>

            {/* Cases list with search/filter */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <CardTitle className="flex items-center gap-2"><Brain className="w-5 h-5 text-accent" />Base de cas anonymisés ({casAnonymises.total})</CardTitle>
                  <div className="flex gap-2 items-center">
                    <Input placeholder="Rechercher..." className="h-8 w-40 text-xs" data-testid="cas-search-input"
                      value={casFilter} onChange={e => setCasFilter(e.target.value)} />
                    <Select value={casTypeFilter} onValueChange={setCasTypeFilter}>
                      <SelectTrigger className="h-8 w-32 text-xs" data-testid="cas-type-filter"><SelectValue placeholder="Tous types" /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Tous types</SelectItem>
                        {['AT','MP','MDPH','Assurance','Expertise','Faute inexcusable','Recours','Autre'].map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {casAnonymises.items?.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">Aucun cas anonymisé. Ajoutez vos premiers cas pour enrichir l'IA.</p>
                ) : (
                  <div className="space-y-2 max-h-[500px] overflow-y-auto">
                    {casAnonymises.items?.filter(c => {
                      if (casTypeFilter && casTypeFilter !== 'all' && c.type_dossier !== casTypeFilter) return false;
                      if (casFilter) {
                        const q = casFilter.toLowerCase();
                        return [c.type_dossier, c.regime, c.duree, c.strategie, c.resultat, c.notes].some(f => (f || '').toLowerCase().includes(q));
                      }
                      return true;
                    }).map(c => (
                      <div key={c.id} className="p-3 rounded-lg border border-border hover:bg-muted/20 transition-colors" data-testid={`cas-item-${c.id}`}>
                        <div className="flex items-center gap-3">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <Badge variant="secondary" className="text-[10px]">{c.type_dossier}</Badge>
                              {c.regime && <Badge variant="outline" className="text-[10px]">{c.regime}</Badge>}
                              <Badge variant={c.resultat === 'Favorable' ? 'default' : c.resultat === 'Défavorable' ? 'destructive' : 'outline'} className={`text-[10px] ${c.resultat === 'Favorable' ? 'bg-green-100 text-green-700 border-green-200' : ''}`}>
                                {c.resultat}
                              </Badge>
                              <span className="text-[10px] font-mono text-muted-foreground bg-muted px-1.5 py-0.5 rounded">{c.score_pertinence}/100</span>
                            </div>
                            <p className="text-sm mt-1 truncate">{c.strategie || 'Pas de stratégie renseignée'}</p>
                            {c.notes && <p className="text-xs text-muted-foreground mt-0.5 truncate">{c.notes}</p>}
                            <p className="text-[10px] text-muted-foreground mt-0.5">{c.duree} {c.created_at ? `— ${new Date(c.created_at).toLocaleDateString('fr-FR')}` : ''}</p>
                          </div>
                          <div className="flex gap-1 flex-shrink-0">
                            <Button size="sm" variant="ghost" className="h-7 w-7 p-0"
                              onClick={() => setEditCas(c)}
                              data-testid={`cas-edit-${c.id}`}
                            ><Pencil className="w-3 h-3" /></Button>
                            <Button size="sm" variant="ghost" className="text-destructive h-7 w-7 p-0"
                              onClick={async () => {
                                try { await axios.delete(`${API}/admin/cas-anonymisés/${c.id}`, axiosConfig); toast.success('Cas supprimé'); fetchData(); }
                                catch { toast.error('Erreur'); }
                              }}
                              data-testid={`cas-delete-${c.id}`}
                            ><Trash2 className="w-3 h-3" /></Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Edit modal */}
            {editCas && (
              <div className="fixed inset-0 flex items-center justify-center p-4" style={{ zIndex: 9999 }}>
                <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setEditCas(null)} />
                <Card className="relative z-10 w-full max-w-lg" data-testid="cas-edit-modal">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">Modifier le cas</CardTitle>
                      <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={() => setEditCas(null)}><X className="w-4 h-4" /></Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <Select value={editCas.type_dossier} onValueChange={v => setEditCas(p => ({...p, type_dossier: v}))}>
                        <SelectTrigger><SelectValue placeholder="Type" /></SelectTrigger>
                        <SelectContent>{['AT','MP','MDPH','Assurance','Expertise','Faute inexcusable','Recours','Autre'].map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent>
                      </Select>
                      <Select value={editCas.regime} onValueChange={v => setEditCas(p => ({...p, regime: v}))}>
                        <SelectTrigger><SelectValue placeholder="Régime" /></SelectTrigger>
                        <SelectContent>{['Général','MSA','Fonction publique','Indépendant','Autre'].map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}</SelectContent>
                      </Select>
                    </div>
                    <Input placeholder="Durée" value={editCas.duree || ''} onChange={e => setEditCas(p => ({...p, duree: e.target.value}))} />
                    <Input placeholder="Stratégie" value={editCas.strategie || ''} onChange={e => setEditCas(p => ({...p, strategie: e.target.value}))} />
                    <Select value={editCas.resultat} onValueChange={v => setEditCas(p => ({...p, resultat: v}))}>
                      <SelectTrigger><SelectValue placeholder="Résultat" /></SelectTrigger>
                      <SelectContent>{['Favorable','Partiellement favorable','Défavorable','En cours'].map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}</SelectContent>
                    </Select>
                    <Input type="number" min={0} max={100} placeholder="Score (0-100)" value={editCas.score_pertinence || ''} onChange={e => setEditCas(p => ({...p, score_pertinence: parseInt(e.target.value) || 0}))} />
                    <Input placeholder="Notes" value={editCas.notes || ''} onChange={e => setEditCas(p => ({...p, notes: e.target.value}))} />
                    <Button className="w-full gap-2 rounded-lg" data-testid="cas-edit-save"
                      onClick={async () => {
                        try {
                          await axios.patch(`${API}/admin/cas-anonymisés/${editCas.id}`, editCas, axiosConfig);
                          toast.success('Cas mis à jour');
                          setEditCas(null);
                          fetchData();
                        } catch { toast.error('Erreur'); }
                      }}
                    >
                      <CheckCircle className="w-4 h-4" /> Enregistrer
                    </Button>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* StrategiIA Premium Review section */}
            <AdminPremiumReview
              items={premiumAnalyses.items}
              stats={premiumAnalyses.stats}
              productType="strategiia"
              productLabel="StrategiIA"
              icon={Brain}
              accentColor="text-accent"
              axiosConfig={axiosConfig}
              onRefresh={fetchData}
            />
          </TabsContent>
          {/* Dossier Express IA Admin Tab — PREMIUM COCKPIT */}
          <TabsContent value="dossier-express" className="space-y-8" data-testid="dossier-express-tab-content">

            {/* ====== LAUNCH MODE CONTROL ====== */}
            <Card className={`border-2 transition-all ${launchMode.mode === 'ouvert' ? 'border-green-300 bg-green-50/20' : launchMode.mode === 'controle' ? 'border-amber-300 bg-amber-50/20' : 'border-red-300 bg-red-50/20'}`} data-testid="launch-mode-card">
              <CardContent className="p-5">
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${launchMode.mode === 'ouvert' ? 'bg-green-500' : launchMode.mode === 'controle' ? 'bg-amber-500' : 'bg-red-500'} animate-pulse`} />
                    <div>
                      <h3 className="text-sm font-bold flex items-center gap-2">
                        Mode de lancement
                        <Badge variant="outline" className={`text-[10px] ${
                          launchMode.mode === 'ouvert' ? 'bg-green-100 text-green-700 border-green-200' :
                          launchMode.mode === 'controle' ? 'bg-amber-100 text-amber-700 border-amber-200' :
                          'bg-red-100 text-red-700 border-red-200'
                        }`} data-testid="launch-mode-badge">
                          {launchMode.mode === 'ouvert' ? 'Ouvert' : launchMode.mode === 'controle' ? 'Ouverture controlee' : 'Temporairement indisponible'}
                        </Badge>
                      </h3>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {launchMode.mode === 'ouvert' ? 'Les clients peuvent commander normalement' : launchMode.mode === 'controle' ? 'Prise de commande active — surveillance renforcee' : 'Prise de commande suspendue'}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2" data-testid="launch-mode-buttons">
                    {['ouvert', 'controle', 'indisponible'].map(m => (
                      <Button key={m} size="sm" variant={launchMode.mode === m ? 'default' : 'outline'}
                        className={`text-xs h-8 ${launchMode.mode === m ? '' : ''}`}
                        disabled={launchLoading}
                        data-testid={`launch-mode-${m}`}
                        onClick={async () => {
                          setLaunchLoading(true);
                          try {
                            const res = await axios.put(`${API}/admin/launch-mode`, { mode: m }, axiosConfig);
                            setLaunchMode({ mode: res.data.mode, message: res.data.message });
                            toast.success(`Mode de lancement : ${m === 'ouvert' ? 'Ouvert' : m === 'controle' ? 'Ouverture controlee' : 'Temporairement indisponible'}`);
                          } catch { toast.error("Erreur lors du changement de mode"); }
                          setLaunchLoading(false);
                        }}>
                        {m === 'ouvert' ? 'Ouvert' : m === 'controle' ? 'Controle' : 'Indisponible'}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ====== MONITORING KPIs ====== */}
            {monitoring && (
              <div data-testid="monitoring-section">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <h3 className="text-sm font-semibold tracking-tight uppercase text-muted-foreground">Monitoring Live</h3>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3" data-testid="monitoring-kpi-grid">
                  {[
                    { label: "Aujourd'hui", value: monitoring.kpis.orders_today, icon: Zap, color: 'text-blue-600', bg: 'bg-blue-50' },
                    { label: "7 jours", value: monitoring.kpis.orders_7_days, icon: BarChart3, color: 'text-indigo-600', bg: 'bg-indigo-50' },
                    { label: "Taux réussite", value: `${monitoring.kpis.success_rate_7_days}%`, icon: TrendingUp, color: monitoring.kpis.success_rate_7_days >= 80 ? 'text-green-600' : 'text-amber-600', bg: monitoring.kpis.success_rate_7_days >= 80 ? 'bg-green-50' : 'bg-amber-50' },
                    { label: "Incidents J", value: monitoring.kpis.incidents_today, icon: AlertTriangle, color: monitoring.kpis.incidents_today > 0 ? 'text-red-600' : 'text-foreground/40', bg: monitoring.kpis.incidents_today > 0 ? 'bg-red-50' : 'bg-muted/40' },
                    { label: "Delai moyen", value: `${monitoring.kpis.avg_delivery_minutes}m`, icon: Clock, color: 'text-teal-600', bg: 'bg-teal-50' },
                    { label: "En attente", value: monitoring.kpis.pending_count, icon: Loader2, color: monitoring.kpis.pending_count > 0 ? 'text-amber-600' : 'text-foreground/40', bg: monitoring.kpis.pending_count > 0 ? 'bg-amber-50' : 'bg-muted/40' },
                    { label: "Intervention", value: monitoring.kpis.intervention_required, icon: Shield, color: monitoring.kpis.intervention_required > 0 ? 'text-red-600' : 'text-foreground/40', bg: monitoring.kpis.intervention_required > 0 ? 'bg-red-50' : 'bg-muted/40' },
                  ].map((kpi, i) => (
                    <Card key={i} className="border-border/40" data-testid={`monitoring-kpi-${i}`}>
                      <CardContent className="p-3">
                        <div className="flex items-center gap-2 mb-1.5">
                          <div className={`w-7 h-7 rounded-lg ${kpi.bg} flex items-center justify-center`}>
                            <kpi.icon className={`w-3.5 h-3.5 ${kpi.color}`} />
                          </div>
                          <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide">{kpi.label}</span>
                        </div>
                        <p className={`text-xl font-bold tracking-tight ${kpi.color}`}>{kpi.value}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}
            {/* ====== SERVICES STATUS ====== */}
            {servicesStatus && (
              <Card className={`border-2 ${servicesStatus.critical_services_ok ? 'border-green-200/60' : 'border-red-300'}`} data-testid="services-status-card">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                      <Shield className="w-3.5 h-3.5" />
                      État des services
                    </h3>
                    <Badge variant="outline" className={`text-[10px] ${servicesStatus.critical_services_ok ? 'bg-green-100 text-green-700 border-green-200' : 'bg-red-100 text-red-700 border-red-200'}`}>
                      {servicesStatus.all_services_ok ? 'Tous operationnels' : servicesStatus.critical_services_ok ? 'Services critiques OK' : 'Attention requise'}
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
                    {Object.entries(servicesStatus.services).map(([key, svc]) => (
                      <div key={key} className={`flex items-center gap-2 p-2 rounded-lg text-xs ${svc.status === 'ok' ? 'bg-green-50/60' : svc.status === 'missing' ? 'bg-amber-50/60' : 'bg-red-50/60'}`}
                        data-testid={`service-${key}`}>
                        <div className={`w-2 h-2 rounded-full flex-shrink-0 ${svc.status === 'ok' ? 'bg-green-500' : svc.status === 'missing' ? 'bg-amber-400' : 'bg-red-500'}`} />
                        <div className="min-w-0">
                          <span className="font-medium block truncate">
                            {key === 'ia_anthropic' ? 'IA' : key === 'stripe' ? 'Paiement' : key === 'email_resend' ? 'Email' : key === 'storage_s3' ? 'Stockage' : key === 'database' ? 'Base' : key === 'launch_mode' ? 'Mode' : key}
                          </span>
                          <span className="text-muted-foreground text-[10px] block truncate">{svc.mode}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Section header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
                  <FileSearch className="w-5 h-5 text-amber-600" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold tracking-tight" style={{ fontFamily: "'Playfair Display', serif" }}>Dossier Express IA</h2>
                  <p className="text-xs text-muted-foreground mt-0.5">Pilotage operationnel de la production</p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={fetchData} className="gap-2 text-xs" data-testid="de-refresh-btn">
                <RefreshCw className="w-3.5 h-3.5" /> Actualiser
              </Button>
            </div>

            {/* Premium KPI Cards — 5 columns with delivery stats */}
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4" data-testid="de-kpi-grid">
              <Card className="relative overflow-hidden border-border/60 hover:shadow-md transition-shadow" data-testid="de-kpi-total">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Total dossiers</p>
                      <p className="text-3xl font-bold mt-2 tracking-tight">{dossierExpressAdmin.stats?.total || 0}</p>
                      <p className="text-[11px] text-muted-foreground mt-1">Tous statuts confondus</p>
                    </div>
                    <div className="w-11 h-11 rounded-xl bg-muted/60 flex items-center justify-center">
                      <FolderOpen className="w-5 h-5 text-foreground/60" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-green-200/60 hover:shadow-md transition-shadow" data-testid="de-kpi-delivered">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Livres</p>
                      <p className="text-3xl font-bold mt-2 tracking-tight text-green-600">{dossierExpressAdmin.stats?.delivered || 0}</p>
                      <p className="text-[11px] text-green-600/70 mt-1">
                        {dossierExpressAdmin.stats?.total > 0
                          ? `${Math.round(((dossierExpressAdmin.stats?.delivered || 0) / dossierExpressAdmin.stats.total) * 100)}% du total`
                          : 'Aucun dossier'
                        }
                      </p>
                    </div>
                    <div className="w-11 h-11 rounded-xl bg-green-50 flex items-center justify-center">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-blue-200/60 hover:shadow-md transition-shadow" data-testid="de-kpi-processing">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">En cours</p>
                      <p className="text-3xl font-bold mt-2 tracking-tight text-blue-600">{dossierExpressAdmin.stats?.processing || 0}</p>
                      <p className="text-[11px] text-blue-600/70 mt-1">Traitement actif</p>
                    </div>
                    <div className="w-11 h-11 rounded-xl bg-blue-50 flex items-center justify-center">
                      <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-amber-200/60 hover:shadow-md transition-shadow" data-testid="de-kpi-pending">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">En attente</p>
                      <p className="text-3xl font-bold mt-2 tracking-tight text-amber-600">{dossierExpressAdmin.stats?.pending || 0}</p>
                      <p className="text-[11px] text-amber-600/70 mt-1">A traiter</p>
                    </div>
                    <div className="w-11 h-11 rounded-xl bg-amber-50 flex items-center justify-center">
                      <Clock className="w-5 h-5 text-amber-500" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className={`relative overflow-hidden hover:shadow-md transition-shadow ${(dossierExpressAdmin.stats?.incidents || 0) > 0 ? 'border-red-300 bg-red-50/30 ring-1 ring-red-200/50' : 'border-border/60'}`} data-testid="de-kpi-incidents">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Incidents</p>
                      <p className={`text-3xl font-bold mt-2 tracking-tight ${(dossierExpressAdmin.stats?.incidents || 0) > 0 ? 'text-red-600' : 'text-foreground/40'}`}>{dossierExpressAdmin.stats?.incidents || 0}</p>
                      <p className="text-[11px] text-red-500/70 mt-1">{(dossierExpressAdmin.stats?.incidents || 0) > 0 ? 'Intervention requise' : 'Aucun incident'}</p>
                    </div>
                    <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${(dossierExpressAdmin.stats?.incidents || 0) > 0 ? 'bg-red-100' : 'bg-muted/60'}`}>
                      <AlertTriangle className={`w-5 h-5 ${(dossierExpressAdmin.stats?.incidents || 0) > 0 ? 'text-red-500' : 'text-foreground/30'}`} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Premium Review section for Dossier Express */}
            <AdminPremiumReview
              items={premiumAnalyses.items}
              stats={premiumAnalyses.stats}
              productType="dossier_express"
              productLabel="Dossier Express IA"
              icon={FileSearch}
              accentColor="text-amber-600"
              axiosConfig={axiosConfig}
              onRefresh={fetchData}
              onViewDossierAnalysis={async (dossierId) => {
                try {
                  const res = await axios.get(`${API}/admin/dossier-express/${dossierId}/analysis`, axiosConfig);
                  setDossierViewDialog(res.data);
                } catch { toast.error("Impossible de charger l'analyse"); }
              }}
            />

            {/* Recent Dossier Express submissions — enriched cards with filters */}
            {dossierExpressAdmin.items?.length > 0 && (
              <Card className="border-border/60">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between flex-wrap gap-3">
                    <CardTitle className="flex items-center gap-2.5 text-lg" data-testid="de-history-title">
                      <FileText className="w-5 h-5 text-teal-600" />
                      Tous les dossiers soumis
                      <Badge variant="outline" className="text-[10px] ml-1 font-normal">{dossierExpressAdmin.items.length}</Badge>
                    </CardTitle>
                    <div className="flex gap-1 bg-muted rounded-lg p-1 overflow-x-auto" data-testid="de-filter-bar">
                      {[
                        { v: 'all', l: 'Tous' },
                        { v: 'delivered', l: 'Livres' },
                        { v: 'processing', l: 'En cours' },
                        { v: 'incidents', l: 'Incidents' },
                        { v: 'pending', l: 'Attente' },
                      ].map(f => (
                        <button key={f.v}
                          onClick={() => setDeFilter(f.v)}
                          className={`px-2.5 sm:px-3 py-1 text-[11px] rounded-md transition-all font-medium whitespace-nowrap ${deFilter === f.v ? 'bg-foreground text-primary-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
                          data-testid={`de-filter-${f.v}`}
                        >{f.l}{f.v === 'incidents' && (dossierExpressAdmin.stats?.incidents || 0) > 0 ? ` (${dossierExpressAdmin.stats.incidents})` : ''}</button>
                      ))}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    {dossierExpressAdmin.items.filter(d => {
                      if (deFilter === 'all') return true;
                      if (deFilter === 'delivered') return d.delivery_status === 'livre_client' || (d.status === 'completed' && !d.delivery_status);
                      if (deFilter === 'processing') return d.status === 'processing';
                      if (deFilter === 'incidents') return d.delivery_status === 'incident_technique' || (d.status === 'error' && d.delivery_status !== 'incident_technique');
                      if (deFilter === 'pending') return d.delivery_status === 'en_attente_traitement' || (d.status === 'processing' && !d.delivery_status);
                      return true;
                    }).slice(0, 30).map(d => {
                      const DELIVERY_CONFIG = {
                        livre_client: { label: 'Livre au client', cls: 'bg-green-100 text-green-700 border-green-200' },
                        généré_sans_email: { label: 'Généré (email echoue)', cls: 'bg-amber-100 text-amber-700 border-amber-200' },
                        en_attente_traitement: { label: 'En attente', cls: 'bg-blue-100 text-blue-700 border-blue-200' },
                        incident_technique: { label: 'Incident technique', cls: 'bg-red-100 text-red-700 border-red-200' },
                      };
                      const STEP_CONFIG = {
                        checkout_valide: 'Paiement confirme',
                        relance_admin: 'Relance admin',
                        documents_recus: 'Documents recus',
                        extraction_en_cours: 'Extraction',
                        analyse_ia: 'Analyse IA',
                        pdf_en_cours: 'Generation PDF',
                        stockage_en_cours: 'Stockage',
                        email_en_cours: 'Envoi email',
                        termine: 'Termine',
                        erreur_ia: 'Erreur IA',
                        erreur_pdf: 'Erreur PDF',
                        erreur_stockage: 'Erreur stockage',
                        erreur_email: 'Erreur email',
                      };
                      const dc = DELIVERY_CONFIG[d.delivery_status] || { label: d.delivery_status || (d.status === 'completed' ? 'Termine' : d.status || 'Inconnu'), cls: 'bg-zinc-100 text-zinc-600 border-zinc-200' };
                      const stepLabel = STEP_CONFIG[d.processing_step] || d.processing_step || d.progress_step || '';
                      const statusConfig = {
                        completed: { label: 'Termine', bg: 'bg-green-50/60', border: 'border-green-200/60', icon: CheckCircle, iconCls: 'text-green-500' },
                        processing: { label: 'En cours', bg: 'bg-blue-50/40', border: 'border-blue-200/60', icon: Clock, iconCls: 'text-blue-500' },
                        error: { label: 'Erreur', bg: 'bg-red-50/40', border: 'border-red-200/60', icon: AlertTriangle, iconCls: 'text-red-500' },
                      };
                      const sc = statusConfig[d.status] || { label: d.status || 'En attente', bg: 'bg-amber-50/40', border: 'border-amber-200/60', icon: Clock, iconCls: 'text-amber-500' };
                      const StatusIcon = sc.icon;
                      return (
                        <div key={d.id} className={`group p-3 sm:p-4 rounded-xl border ${sc.border} ${sc.bg} hover:shadow-sm transition-all`} data-testid={`de-row-${d.id}`}>
                          <div className="flex flex-col sm:flex-row sm:items-start gap-2.5 sm:gap-3.5">
                            {/* Top row mobile: icon + name */}
                            <div className="flex items-center gap-2.5 sm:block sm:flex-shrink-0">
                              <div className={`w-8 h-8 sm:w-9 sm:h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${d.status === 'completed' ? 'bg-green-100' : d.status === 'error' ? 'bg-red-100' : 'bg-blue-100'}`}>
                                <StatusIcon className={`w-4 h-4 ${sc.iconCls}`} />
                              </div>
                              <span className="font-semibold text-sm truncate sm:hidden">{d.name || d.email}</span>
                              <Badge variant="outline" className={`text-[10px] border ${dc.cls} sm:hidden flex-shrink-0`}>{dc.label}</Badge>
                            </div>
                            <div className="flex-1 min-w-0">
                              {/* Desktop badges row */}
                              <div className="hidden sm:flex items-center gap-2 flex-wrap mb-1.5">
                                <span className="font-semibold text-sm truncate max-w-[200px] lg:max-w-none">{d.name || d.email}</span>
                                <Badge variant="outline" className={`text-[10px] border ${dc.cls}`} data-testid={`de-delivery-${d.id}`}>{dc.label}</Badge>
                                {stepLabel && <Badge variant="outline" className="text-[10px] border-zinc-200 text-zinc-500" data-testid={`de-step-${d.id}`}>{stepLabel}</Badge>}
                                {d.type_dossier && <Badge variant="outline" className="text-[10px]">{d.type_dossier}</Badge>}
                                {d.premium_pdf && <Badge className="bg-accent/10 text-accent border-accent/20 text-[10px]">PDF Pro</Badge>}
                                {d.admin_test && <Badge className="bg-zinc-100 text-zinc-500 border-zinc-200 text-[10px]">Test</Badge>}
                                {d.retry_count > 0 && <Badge className="bg-purple-100 text-purple-600 border-purple-200 text-[10px]">Relance x{d.retry_count}</Badge>}
                              </div>
                              {/* Mobile badges row */}
                              <div className="flex items-center gap-1.5 flex-wrap mb-1.5 sm:hidden">
                                {stepLabel && <Badge variant="outline" className="text-[10px] border-zinc-200 text-zinc-500">{stepLabel}</Badge>}
                                {d.type_dossier && <Badge variant="outline" className="text-[10px]">{d.type_dossier}</Badge>}
                                {d.premium_pdf && <Badge className="bg-accent/10 text-accent border-accent/20 text-[10px]">PDF Pro</Badge>}
                                {d.admin_test && <Badge className="bg-zinc-100 text-zinc-500 border-zinc-200 text-[10px]">Test</Badge>}
                              </div>
                              <div className="flex items-center gap-2 sm:gap-3 text-[11px] sm:text-xs text-muted-foreground flex-wrap">
                                <span className="flex items-center gap-1 truncate">
                                  <Mail className="w-3 h-3 flex-shrink-0" />
                                  <span className="truncate">{d.email}</span>
                                </span>
                                <span className="flex items-center gap-1">
                                  <Calendar className="w-3 h-3 flex-shrink-0" />
                                  {d.created_at ? new Date(d.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''}
                                </span>
                              </div>
                              {d.completed_at && <p className="text-[11px] text-green-600 mt-1 flex items-center gap-1"><CheckCircle className="w-3 h-3" /> Livre le {new Date(d.completed_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</p>}
                              {d.email_sent && <p className="text-[11px] text-emerald-600 mt-0.5 flex items-center gap-1"><Send className="w-3 h-3" /> Email envoye</p>}
                              {d.error && d.status === 'error' && <p className="text-[11px] text-red-500 mt-1 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> {d.error}</p>}
                            </div>
                            {/* Actions — below on mobile */}
                            <div className="flex gap-2 flex-wrap sm:flex-shrink-0 sm:items-start pt-1.5 sm:pt-0 border-t sm:border-t-0 border-border/40">
                              {d.status === 'completed' && (
                                <Button size="sm" variant="outline" className="text-xs h-8 gap-1.5 border-green-200 text-green-700 hover:bg-green-50 flex-1 sm:flex-none"
                                  data-testid={`de-view-analysis-${d.id}`}
                                  onClick={async () => {
                                    try {
                                      const res = await axios.get(`${API}/admin/dossier-express/${d.id}/analysis`, axiosConfig);
                                      setDossierViewDialog(res.data);
                                    } catch { toast.error("Impossible de charger l'analyse"); }
                                  }}>
                                  <Eye className="w-3.5 h-3.5" /> Consulter
                                </Button>
                              )}
                              {d.status === 'error' && (
                                <Button size="sm" variant="outline" className="text-xs h-8 gap-1.5 border-amber-200 text-amber-700 hover:bg-amber-50 flex-1 sm:flex-none"
                                  data-testid={`de-retry-${d.id}`}
                                  onClick={async () => {
                                    try {
                                      await axios.post(`${API}/admin/dossier-express/${d.id}/retry`, {}, axiosConfig);
                                      toast.success("Relance lancee avec succes");
                                      fetchData();
                                    } catch (err) {
                                      toast.error(err.response?.data?.detail || "Erreur lors de la relance");
                                    }
                                  }}>
                                  <RefreshCw className="w-3.5 h-3.5" /> Relancer
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Dossier View Dialog — Onglets Analyse / Documents / PDF */}
            {dossierViewDialog && (
              <Dialog open onOpenChange={() => setDossierViewDialog(null)}>
                <DialogContent className="max-w-4xl max-h-[88vh] overflow-y-auto p-0" data-testid="dossier-view-dialog">
                  {/* Header fixe */}
                  <div className="px-6 pt-6 pb-3 border-b sticky top-0 bg-background z-10">
                    <DialogHeader>
                      <DialogTitle className="flex items-center gap-2 text-lg">
                        <FileSearch className="w-5 h-5 text-amber-600" />
                        {dossierViewDialog.name || dossierViewDialog.email}
                      </DialogTitle>
                      <DialogDescription className="flex items-center gap-2 flex-wrap text-xs">
                        <span>Dossier Express IA</span>
                        {dossierViewDialog.completed_at && (
                          <span>— complété le {new Date(dossierViewDialog.completed_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
                        )}
                      </DialogDescription>
                    </DialogHeader>
                    <div className="flex flex-wrap gap-2 mt-2">
                      <Badge variant="outline" className="text-[10px]">{dossierViewDialog.type_dossier}</Badge>
                      {dossierViewDialog.regime && <Badge variant="outline" className="text-[10px]">{dossierViewDialog.regime}</Badge>}
                      {dossierViewDialog.premium_pdf && <Badge className="bg-accent/10 text-accent border-accent/20 text-[10px]">PDF Pro</Badge>}
                    </div>
                  </div>

                  <Tabs defaultValue="analyse" className="px-6 pt-3 pb-4">
                    <TabsList className="w-full justify-start mb-4 bg-muted/50">
                      <TabsTrigger value="analyse" className="gap-1.5 text-xs" data-testid="tab-analyse">
                        <Brain className="w-3.5 h-3.5" /> Analyse
                      </TabsTrigger>
                      <TabsTrigger value="documents" className="gap-1.5 text-xs" data-testid="tab-documents">
                        <FileText className="w-3.5 h-3.5" /> Documents uploadés
                        {dossierViewDialog.document_details?.length > 0 && (
                          <span className="ml-1 text-[10px] bg-amber-100 text-amber-700 rounded-full px-1.5">{dossierViewDialog.document_details.length}</span>
                        )}
                      </TabsTrigger>
                      <TabsTrigger value="pdf" className="gap-1.5 text-xs" data-testid="tab-pdf">
                        <Eye className="w-3.5 h-3.5" /> Prévisualisation PDF
                      </TabsTrigger>
                      <TabsTrigger value="revue-expert" className="gap-1.5 text-xs" data-testid="tab-revue-expert">
                        <PenTool className="w-3.5 h-3.5" /> Revue expert
                        {dossierViewDialog.human_reviewed && (
                          <span className="ml-1 text-[10px] bg-emerald-100 text-emerald-700 rounded-full px-1.5">relu</span>
                        )}
                      </TabsTrigger>
                    </TabsList>

                    {/* ——— TAB: Analyse ——— */}
                    <TabsContent value="analyse" className="space-y-4 mt-0">
                      {dossierViewDialog.situation && (
                        <div className="p-3 rounded-lg bg-muted/50 border">
                          <Label className="font-medium text-xs mb-1 block text-muted-foreground">Situation décrite par le client</Label>
                          <p className="text-sm leading-relaxed max-h-[120px] overflow-y-auto">{dossierViewDialog.situation}</p>
                        </div>
                      )}
                      {/* Encart "Base documentaire prise en compte" */}
                      {dossierViewDialog.document_details?.length > 0 && (() => {
                        const docs = dossierViewDialog.document_details;
                        const totalPages = docs.reduce((s, d) => s + (d.pages || 0), 0);
                        const statuses = docs.map(d => d.status || '');
                        const level = statuses.every(s => s === 'text_extracted') ? 'Excellente'
                          : statuses.every(s => s === 'ocr_extracted') ? 'Bonne'
                          : statuses.every(s => ['text_extracted','ocr_extracted'].includes(s)) && statuses.some(s => s === 'ocr_extracted') ? 'Très bonne'
                          : statuses.some(s => ['text_extracted','ocr_extracted'].includes(s)) ? 'Partielle' : 'Limitée';
                        const levelColor = { Excellente: 'text-emerald-600', 'Très bonne': 'text-emerald-600', Bonne: 'text-blue-600', Partielle: 'text-amber-600', 'Limitée': 'text-red-500' }[level] || '';
                        return (
                          <div className="rounded-xl border border-amber-200/60 bg-gradient-to-b from-amber-50/40 to-transparent p-4" data-testid="base-documentaire-encart">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="w-1 h-5 rounded-full bg-amber-500" />
                              <h4 className="text-sm font-semibold">Base documentaire prise en compte</h4>
                            </div>
                            <p className="text-xs text-muted-foreground mb-3 pl-3">Ce rapport a été établi à partir des pièces transmises au moment de la demande.</p>
                            <div className="grid grid-cols-3 gap-3 pl-3 mb-3">
                              {[
                                { value: String(docs.length), label: 'Documents analysés' },
                                { value: String(totalPages), label: 'Pages exploitées' },
                                { value: level, label: 'Lisibilité documentaire', cls: levelColor },
                              ].map((m, i) => (
                                <div key={i} className="text-center p-2.5 rounded-lg bg-background border">
                                  <span className={`block ${m.cls ? `text-sm font-bold ${m.cls}` : 'text-lg font-bold'}`}>{m.value}</span>
                                  <span className="text-[10px] text-muted-foreground">{m.label}</span>
                                </div>
                              ))}
                            </div>
                            <p className="text-[11px] text-muted-foreground/70 italic pl-3">Certaines pièces peuvent nécessiter une relecture humaine complémentaire lorsqu'elles sont scannées, manuscrites ou de qualité inégale.</p>
                          </div>
                        );
                      })()}
                      <div>
                        <Label className="font-medium text-sm mb-2 block">Analyse générée par Dossier Express IA</Label>
                        {dossierViewDialog.analysis ? (
                          <div className="max-h-[500px] overflow-y-auto pr-1">
                            <PremiumAnalysisRenderer markdown={dossierViewDialog.analysis} testIdPrefix="de-analysis-section" />
                          </div>
                        ) : (
                          <p className="text-sm text-muted-foreground italic p-4 border rounded-lg">Aucune analyse disponible.</p>
                        )}
                      </div>
                    </TabsContent>

                    {/* ——— TAB: Documents uploadés ——— */}
                    <TabsContent value="documents" className="mt-0" data-testid="documents-tab-content">
                      {dossierViewDialog.document_details?.length > 0 ? (
                        <div className="space-y-3">
                          <p className="text-xs text-muted-foreground">{dossierViewDialog.document_details.length} document{dossierViewDialog.document_details.length > 1 ? 's' : ''} uploadé{dossierViewDialog.document_details.length > 1 ? 's' : ''} par le client.</p>
                          {dossierViewDialog.document_details.map((doc, idx) => {
                            const sc = { text_extracted: { l: 'Texte extrait', c: 'bg-emerald-50 text-emerald-700 border-emerald-200' }, ocr_extracted: { l: 'OCR utilisé', c: 'bg-blue-50 text-blue-700 border-blue-200' }, ocr_empty: { l: 'Partiellement lisible', c: 'bg-orange-50 text-orange-600 border-orange-200' } }[doc.status] || { l: 'Non lisible', c: 'bg-red-50 text-red-600 border-red-200' };
                            const ext = doc.name?.match(/\.(\w+)$/)?.[1]?.toUpperCase() || '—';
                            return (
                              <div key={idx} className="p-4 rounded-xl border bg-background" data-testid={`doc-detail-${idx}`}>
                                <div className="flex items-center justify-between gap-3 mb-2">
                                  <div className="flex items-center gap-2.5 min-w-0 flex-1">
                                    <div className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
                                      <FileText className="w-4 h-4 text-muted-foreground" />
                                    </div>
                                    <div className="min-w-0">
                                      <p className="text-sm font-medium truncate">{doc.name}</p>
                                      <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                                        <span>{ext}</span>
                                        {doc.pages > 0 && <><span className="opacity-40">·</span><span>{doc.pages} page{doc.pages > 1 ? 's' : ''}</span></>}
                                        {doc.size_kb > 0 && <><span className="opacity-40">·</span><span>{doc.size_kb} Ko</span></>}
                                        {doc.text_length > 0 && <><span className="opacity-40">·</span><span>{doc.text_length.toLocaleString('fr-FR')} car. extraits</span></>}
                                      </div>
                                    </div>
                                  </div>
                                  <Badge variant="outline" className={`flex-shrink-0 text-[10px] ${sc.c}`}>{sc.l}</Badge>
                                </div>
                                <div className="pl-[46px]">
                                  <p className="text-[11px] text-muted-foreground">{doc.method}</p>
                                  {doc.preview && (
                                    <p className="mt-1.5 text-xs text-muted-foreground/80 italic line-clamp-2 bg-muted/40 rounded px-2.5 py-1.5 border border-border/30">« {doc.preview}… »</p>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <div className="text-center py-10 text-muted-foreground">
                          <FileText className="w-10 h-10 mx-auto mb-3 opacity-30" />
                          <p className="text-sm">Aucun détail de document disponible pour ce dossier.</p>
                        </div>
                      )}
                    </TabsContent>

                    {/* ——— TAB: Prévisualisation PDF ——— */}
                    <TabsContent value="pdf" className="mt-0" data-testid="pdf-tab-content">
                      {dossierViewDialog.analysis ? (
                        <div className="space-y-4">
                          <p className="text-xs text-muted-foreground">Prévisualisez le rapport PDF exactement tel qu'il sera reçu par le client.</p>
                          <div className="flex gap-3">
                            <Button className="gap-2" data-testid="preview-pdf-btn" onClick={async () => {
                              try {
                                toast.info('Génération du PDF…');
                                const response = await fetch(`${API}/admin/dossier-express/${dossierViewDialog.id}/preview-pdf`, { headers: { 'Authorization': `Bearer ${token}` } });
                                if (!response.ok) throw new Error('Erreur PDF');
                                const blob = await response.blob();
                                window.open(URL.createObjectURL(blob), '_blank');
                                toast.success('PDF ouvert dans un nouvel onglet');
                              } catch { toast.error('Erreur lors de la génération du PDF'); }
                            }}>
                              <Eye className="w-4 h-4" /> Visualiser le PDF final
                            </Button>
                            <Button variant="outline" className="gap-2" data-testid="download-pdf-btn" onClick={async () => {
                              try {
                                const response = await fetch(`${API}/admin/dossier-express/${dossierViewDialog.id}/preview-pdf`, { headers: { 'Authorization': `Bearer ${token}` } });
                                if (!response.ok) throw new Error('Erreur PDF');
                                const blob = await response.blob();
                                const a = document.createElement('a');
                                a.href = URL.createObjectURL(blob);
                                a.download = `Rapport_DossierExpress_${(dossierViewDialog.name || 'client').replace(/\s/g, '_')}.pdf`;
                                a.click();
                                toast.success('Téléchargement lancé');
                              } catch { toast.error('Erreur lors du téléchargement'); }
                            }}>
                              <Download className="w-4 h-4" /> Télécharger le PDF
                            </Button>
                          </div>
                          <div className="rounded-xl border bg-muted/30 p-5">
                            <h4 className="text-sm font-semibold mb-3 flex items-center gap-2"><FileSearch className="w-4 h-4 text-amber-600" /> Contenu du rapport</h4>
                            <div className="grid grid-cols-2 gap-3 text-xs mb-4">
                              {[
                                { label: 'Client', value: dossierViewDialog.name || '—' },
                                { label: 'Type', value: dossierViewDialog.type_dossier || '—' },
                                { label: 'Régime', value: dossierViewDialog.regime || '—' },
                                { label: 'Documents', value: `${dossierViewDialog.document_details?.length || 0} fichier${(dossierViewDialog.document_details?.length || 0) > 1 ? 's' : ''}` },
                              ].map((item, i) => (
                                <div key={i} className="p-2.5 rounded-lg bg-background border">
                                  <span className="text-muted-foreground block text-[10px]">{item.label}</span>
                                  <span className="font-medium">{item.value}</span>
                                </div>
                              ))}
                            </div>
                            <p className="text-[11px] text-muted-foreground italic">Le PDF inclut l'analyse complète, l'encart "Base documentaire prise en compte" et la signature de marque.</p>
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-10 text-muted-foreground">
                          <Eye className="w-10 h-10 mx-auto mb-3 opacity-30" />
                          <p className="text-sm">Aucune analyse disponible — le PDF ne peut pas être généré.</p>
                        </div>
                      )}
                    </TabsContent>

                    {/* ——— TAB: Revue Expert (Human Review) ——— */}
                    <TabsContent value="revue-expert" className="mt-0 space-y-5" data-testid="revue-expert-tab-content">
                      {/* Section 1: Documents originaux téléchargeables */}
                      <div className="rounded-xl border p-4 space-y-3">
                        <div className="flex items-center gap-2">
                          <div className="w-1 h-5 rounded-full bg-amber-500" />
                          <h4 className="text-sm font-semibold">Documents clients originaux</h4>
                          {dossierViewDialog.original_documents?.length > 0 && (
                            <Badge variant="outline" className="text-[10px]">{dossierViewDialog.original_documents.length} fichier{dossierViewDialog.original_documents.length > 1 ? 's' : ''}</Badge>
                          )}
                        </div>
                        {dossierViewDialog.original_documents?.length > 0 ? (
                          <div className="space-y-2">
                            {dossierViewDialog.original_documents.map((doc, idx) => (
                              <div key={idx} className="flex items-center justify-between gap-3 p-3 rounded-lg bg-muted/40 border" data-testid={`original-doc-${idx}`}>
                                <div className="flex items-center gap-2.5 min-w-0 flex-1">
                                  <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center flex-shrink-0">
                                    <FileText className="w-4 h-4 text-amber-600" />
                                  </div>
                                  <div className="min-w-0">
                                    <p className="text-sm font-medium truncate">{doc.original_filename || 'Document'}</p>
                                    <p className="text-[11px] text-muted-foreground">{doc.content_type || 'Fichier'}{doc.size ? ` — ${(doc.size / 1024).toFixed(0)} Ko` : ''}</p>
                                  </div>
                                </div>
                                <Button size="sm" variant="outline" className="text-xs h-7 gap-1 flex-shrink-0" data-testid={`download-original-${idx}`}
                                  onClick={async () => {
                                    try {
                                      toast.info('Téléchargement en cours...');
                                      const response = await fetch(`${API}/admin/dossier-express/${dossierViewDialog.id}/documents/${doc.file_id}/download`, { headers: { 'Authorization': `Bearer ${token}` } });
                                      if (!response.ok) throw new Error('Erreur téléchargement');
                                      const blob = await response.blob();
                                      const a = document.createElement('a');
                                      a.href = URL.createObjectURL(blob);
                                      a.download = doc.original_filename || 'document';
                                      a.click();
                                      toast.success('Document téléchargé');
                                    } catch { toast.error('Impossible de télécharger ce document'); }
                                  }}>
                                  <Download className="w-3 h-3" /> Télécharger
                                </Button>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-xs text-muted-foreground italic pl-3">Aucun document original stocké pour ce dossier. Les fichiers soumis avant l'activation du stockage ne sont pas disponibles.</p>
                        )}
                      </div>

                      {/* Section 2: Indicateur de complétude */}
                      {dossierViewDialog.document_details?.length > 0 && (() => {
                        const docs = dossierViewDialog.document_details;
                        const originals = dossierViewDialog.original_documents || [];
                        const totalPages = docs.reduce((s, d) => s + (d.pages || 0), 0);
                        const extracted = docs.filter(d => ['text_extracted', 'ocr_extracted'].includes(d.status)).length;
                        const pct = Math.round((extracted / docs.length) * 100);
                        return (
                          <div className="rounded-xl border p-4 space-y-2">
                            <div className="flex items-center gap-2 mb-1">
                              <div className="w-1 h-5 rounded-full bg-blue-500" />
                              <h4 className="text-sm font-semibold">Indicateur de complétude</h4>
                            </div>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                              <div className="text-center p-2.5 rounded-lg bg-background border">
                                <span className="block text-lg font-bold">{originals.length}</span>
                                <span className="text-[10px] text-muted-foreground">Originaux stockés</span>
                              </div>
                              <div className="text-center p-2.5 rounded-lg bg-background border">
                                <span className="block text-lg font-bold">{docs.length}</span>
                                <span className="text-[10px] text-muted-foreground">Documents analysés</span>
                              </div>
                              <div className="text-center p-2.5 rounded-lg bg-background border">
                                <span className="block text-lg font-bold">{totalPages}</span>
                                <span className="text-[10px] text-muted-foreground">Pages exploitées</span>
                              </div>
                              <div className="text-center p-2.5 rounded-lg bg-background border">
                                <span className={`block text-lg font-bold ${pct === 100 ? 'text-emerald-600' : pct >= 50 ? 'text-blue-600' : 'text-amber-600'}`}>{pct}%</span>
                                <span className="text-[10px] text-muted-foreground">Extraction réussie</span>
                              </div>
                            </div>
                          </div>
                        );
                      })()}

                      {/* Section 3: Éditeur d'analyse */}
                      <div className="rounded-xl border p-4 space-y-3">
                        <div className="flex items-center gap-2 mb-1">
                          <div className="w-1 h-5 rounded-full bg-green-500" />
                          <h4 className="text-sm font-semibold">Modifier l'analyse IA</h4>
                          {dossierViewDialog.human_reviewed && (
                            <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[10px]">Relu par {dossierViewDialog.reviewed_by || 'expert'}</Badge>
                          )}
                        </div>
                        {dossierViewDialog.reviewed_at && (
                          <p className="text-[11px] text-muted-foreground pl-3">Dernière modification : {new Date(dossierViewDialog.reviewed_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
                        )}
                        <textarea
                          className="flex w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring min-h-[300px] resize-y font-mono leading-relaxed"
                          defaultValue={dossierViewDialog.analysis || ''}
                          data-testid="expert-analysis-textarea"
                          onChange={(e) => setDossierViewDialog(prev => ({ ...prev, _editedAnalysis: e.target.value }))}
                        />
                        <div>
                          <Label className="text-xs text-muted-foreground mb-1.5 block">Notes internes (optionnel)</Label>
                          <textarea
                            className="flex w-full rounded-lg border border-input bg-background px-3 py-2 text-sm min-h-[60px] resize-y"
                            defaultValue={dossierViewDialog.admin_notes || ''}
                            placeholder="Notes privées sur cette relecture..."
                            data-testid="expert-notes-textarea"
                            onChange={(e) => setDossierViewDialog(prev => ({ ...prev, _editedNotes: e.target.value }))}
                          />
                        </div>
                        <div className="flex flex-wrap gap-2 pt-1">
                          <Button size="sm" className="gap-1.5 bg-green-600 hover:bg-green-500 text-white" data-testid="save-analysis-btn"
                            onClick={async () => {
                              const newAnalysis = dossierViewDialog._editedAnalysis ?? dossierViewDialog.analysis;
                              const newNotes = dossierViewDialog._editedNotes ?? dossierViewDialog.admin_notes;
                              if (!newAnalysis?.trim()) { toast.error("L'analyse ne peut pas être vide"); return; }
                              try {
                                await axios.put(`${API}/admin/dossier-express/${dossierViewDialog.id}/analysis`, { analysis: newAnalysis, admin_notes: newNotes }, axiosConfig);
                                toast.success("Analyse mise à jour avec succès");
                                setDossierViewDialog(prev => ({ ...prev, analysis: newAnalysis, admin_notes: newNotes, human_reviewed: true }));
                              } catch { toast.error("Erreur lors de la sauvegarde"); }
                            }}>
                            <CheckCircle className="w-3.5 h-3.5" /> Sauvegarder les modifications
                          </Button>
                        </div>
                      </div>

                      {/* Section 4: Regénération PDF + envoi */}
                      <div className="rounded-xl border border-accent/30 bg-accent/5 p-4 space-y-3">
                        <div className="flex items-center gap-2 mb-1">
                          <div className="w-1 h-5 rounded-full bg-accent" />
                          <h4 className="text-sm font-semibold">Regénérer le PDF expert</h4>
                        </div>
                        <p className="text-xs text-muted-foreground pl-3">Générez un nouveau PDF intégrant vos modifications et la mention "Relu par un expert". Vous pouvez aussi l'envoyer directement au client.</p>
                        <div className="flex flex-wrap gap-2 pl-3">
                          <Button size="sm" variant="outline" className="gap-1.5 text-xs" data-testid="regenerate-pdf-btn"
                            onClick={async () => {
                              try {
                                toast.info('Regénération du PDF...');
                                await axios.post(`${API}/admin/dossier-express/${dossierViewDialog.id}/regenerate-pdf`, { send_email: false }, axiosConfig);
                                toast.success("PDF regénéré avec succès");
                              } catch { toast.error("Erreur lors de la regénération"); }
                            }}>
                            <RefreshCw className="w-3 h-3" /> Regénérer le PDF
                          </Button>
                          <Button size="sm" className="gap-1.5 text-xs bg-emerald-600 hover:bg-emerald-500 text-white" data-testid="regenerate-and-send-btn"
                            onClick={async () => {
                              if (!window.confirm(`Envoyer le rapport expert finalisé à ${dossierViewDialog.email} ?`)) return;
                              try {
                                toast.info('Regénération et envoi du PDF...');
                                const res = await axios.post(`${API}/admin/dossier-express/${dossierViewDialog.id}/regenerate-pdf`, { send_email: true }, axiosConfig);
                                if (res.data.email_sent) {
                                  toast.success(`Rapport expert envoyé à ${dossierViewDialog.email}`);
                                } else {
                                  toast.success("PDF regénéré (email non envoyé — vérifiez la configuration)");
                                }
                              } catch { toast.error("Erreur lors de l'envoi"); }
                            }}>
                            <Send className="w-3 h-3" /> Regénérer et envoyer au client
                          </Button>
                        </div>
                      </div>
                    </TabsContent>
                  </Tabs>

                  <div className="px-6 pb-4 flex justify-end border-t pt-3">
                    <Button variant="outline" onClick={() => setDossierViewDialog(null)}>Fermer</Button>
                  </div>
                </DialogContent>
              </Dialog>
            )}
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6" data-testid="analytics-tab-content">
            {analyticsData ? (
              <AnalyticsTab 
                data={analyticsData} 
                period={analyticsPeriod} 
                onPeriodChange={async (p) => {
                  setAnalyticsPeriod(p);
                  try {
                    const res = await axios.get(`${API}/admin/analytics?period=${p}`, axiosConfig);
                    setAnalyticsData(res.data);
                  } catch {}
                }} 
              />
            ) : (
              <Card><CardContent className="py-12 text-center text-muted-foreground">Chargement des analytiques...</CardContent></Card>
            )}

            {/* Conversion Analytics — Origine des leads */}
            <AdminConversionAnalytics axiosConfig={axiosConfig} />
          </TabsContent>

          {/* Admin Documents Tab */}
          <TabsContent value="documents" className="space-y-6" data-testid="admin-documents-tab">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Documents clients</h3>
              <div className="flex gap-2">
                <select
                  value={docStatusFilter}
                  onChange={async (e) => {
                    setDocStatusFilter(e.target.value);
                    try {
                      const params = e.target.value ? `?status=${e.target.value}` : '';
                      const res = await axios.get(`${API}/admin/documents${params}`, axiosConfig);
                      setAdminDocs(res.data);
                    } catch {}
                  }}
                  className="h-8 text-xs border rounded-lg px-2 bg-background"
                  data-testid="admin-doc-status-filter"
                >
                  <option value="">Tous statuts</option>
                  <option value="en_attente">En attente</option>
                  <option value="valide">Validés</option>
                  <option value="illisible">Illisibles</option>
                </select>
                <Button size="sm" variant="outline" onClick={async () => {
                  try { const r = await axios.get(`${API}/admin/documents`, axiosConfig); setAdminDocs(r.data); } catch {}
                }} className="gap-1" data-testid="admin-doc-refresh">
                  <RefreshCw className="w-3 h-3" /> Actualiser
                </Button>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-3">
              <Card><CardContent className="p-3 text-center"><p className="text-xl font-bold">{adminDocs.stats?.total || 0}</p><p className="text-[10px] text-muted-foreground uppercase">Total</p></CardContent></Card>
              <Card><CardContent className="p-3 text-center"><p className="text-xl font-bold text-amber-600">{adminDocs.stats?.en_attente || 0}</p><p className="text-[10px] text-muted-foreground uppercase">En attente</p></CardContent></Card>
              <Card><CardContent className="p-3 text-center"><p className="text-xl font-bold text-green-600">{adminDocs.stats?.valide || 0}</p><p className="text-[10px] text-muted-foreground uppercase">Validés</p></CardContent></Card>
              <Card><CardContent className="p-3 text-center"><p className="text-xl font-bold text-red-600">{adminDocs.stats?.illisible || 0}</p><p className="text-[10px] text-muted-foreground uppercase">Illisibles</p></CardContent></Card>
            </div>
            {adminDocs.documents?.length === 0 ? (
              <Card><CardContent className="py-12 text-center text-muted-foreground">Aucun document client pour le moment</CardContent></Card>
            ) : (
              <Card>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-muted/30 border-b"><tr>
                        <th className="py-2 px-3 text-left font-medium text-muted-foreground">Fichier</th>
                        <th className="py-2 px-3 text-left font-medium text-muted-foreground">Catégorie</th>
                        <th className="py-2 px-3 text-left font-medium text-muted-foreground">Statut</th>
                        <th className="py-2 px-3 text-left font-medium text-muted-foreground">Date</th>
                        <th className="py-2 px-3 text-left font-medium text-muted-foreground">Actions</th>
                      </tr></thead>
                      <tbody>
                        {(adminDocs.documents || []).map((doc) => (
                          <tr key={doc.id} className="border-b last:border-0 hover:bg-muted/20" data-testid={`admin-doc-${doc.id}`}>
                            <td className="py-2 px-3">
                              <p className="font-medium truncate max-w-[200px]">{doc.filename}</p>
                              <p className="text-[10px] text-muted-foreground">{doc.client_id?.slice(0, 8)}...</p>
                            </td>
                            <td className="py-2 px-3"><Badge variant="outline" className="text-[10px]">{doc.category}</Badge></td>
                            <td className="py-2 px-3">
                              <Badge className={`text-[10px] ${doc.status === 'valide' ? 'bg-green-100 text-green-700' : doc.status === 'illisible' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>
                                {doc.status}
                              </Badge>
                            </td>
                            <td className="py-2 px-3 text-muted-foreground text-xs">{doc.created_at ? new Date(doc.created_at).toLocaleDateString('fr-FR') : ''}</td>
                            <td className="py-2 px-3">
                              <div className="flex gap-1">
                                {doc.status !== 'valide' && (
                                  <Button size="sm" variant="ghost" className="h-7 px-2 text-green-600 hover:bg-green-50 text-xs"
                                    onClick={async () => {
                                      try {
                                        await axios.patch(`${API}/admin/documents/${doc.id}/status`, { status: 'valide' }, axiosConfig);
                                        toast.success('Document validé + notification envoyée');
                                        const r = await axios.get(`${API}/admin/documents${docStatusFilter ? `?status=${docStatusFilter}` : ''}`, axiosConfig);
                                        setAdminDocs(r.data);
                                      } catch { toast.error('Erreur'); }
                                    }}
                                    data-testid={`validate-doc-${doc.id}`}
                                  >
                                    <CheckCircle className="w-3 h-3 mr-1" /> Valider
                                  </Button>
                                )}
                                {doc.status !== 'illisible' && (
                                  <Button size="sm" variant="ghost" className="h-7 px-2 text-red-600 hover:bg-red-50 text-xs"
                                    onClick={async () => {
                                      try {
                                        await axios.patch(`${API}/admin/documents/${doc.id}/status`, { status: 'illisible' }, axiosConfig);
                                        toast.success('Document marqué illisible + notification envoyée');
                                        const r = await axios.get(`${API}/admin/documents${docStatusFilter ? `?status=${docStatusFilter}` : ''}`, axiosConfig);
                                        setAdminDocs(r.data);
                                      } catch { toast.error('Erreur'); }
                                    }}
                                    data-testid={`reject-doc-${doc.id}`}
                                  >
                                    <XCircle className="w-3 h-3 mr-1" /> Illisible
                                  </Button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Documents S3 stockés */}
            <div className="mt-8 pt-6 border-t" data-testid="s3-documents-section">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold">Documents stockés (S3)</h3>
                  <p className="text-xs text-muted-foreground">Fichiers uploadés et stockés durablement dans AWS S3</p>
                </div>
                <Button size="sm" variant="outline" onClick={async () => {
                  try {
                    const [d, s, t, ac] = await Promise.all([
                      axios.get(`${API}/documents`, axiosConfig),
                      axios.get(`${API}/documents/stats`, axiosConfig),
                      axios.get(`${API}/documents/timeline`, axiosConfig),
                      axios.get(`${API}/documents/storage-alerts/check`, axiosConfig),
                    ]);
                    setS3Docs(d.data);
                    setS3Stats(s.data);
                    setS3Timeline(t.data);
                    setS3AlertCheck(ac.data);
                  } catch {}
                }} className="gap-1" data-testid="s3-doc-refresh">
                  <RefreshCw className="w-3 h-3" /> Actualiser
                </Button>
              </div>
              
              <div className="grid grid-cols-3 gap-3 mb-4">
                <Card><CardContent className="p-3 text-center"><p className="text-xl font-bold">{s3Stats.total || 0}</p><p className="text-[10px] text-muted-foreground uppercase">Fichiers S3</p></CardContent></Card>
                {(s3Stats.by_source || []).slice(0, 2).map((s, i) => (
                  <Card key={i}><CardContent className="p-3 text-center"><p className="text-xl font-bold">{s.count}</p><p className="text-[10px] text-muted-foreground uppercase">{s.source}</p></CardContent></Card>
                ))}
              </div>

              {/* S3 Dashboard — Graphiques */}
              {(s3Timeline.timeline || []).length > 0 && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4" data-testid="s3-dashboard-charts">
                  {/* AreaChart — Uploads par jour */}
                  <Card className="lg:col-span-2">
                    <CardContent className="p-4">
                      <p className="text-sm font-semibold mb-1">Uploads par jour</p>
                      <p className="text-[10px] text-muted-foreground mb-3">Évolution des documents stockés sur les 30 derniers jours</p>
                      <div className="h-[180px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={s3Timeline.timeline} margin={{ top: 5, right: 5, left: -10, bottom: 5 }}>
                            <defs>
                              <linearGradient id="s3UploadGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#0d9488" stopOpacity={0.4} />
                                <stop offset="95%" stopColor="#0d9488" stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                            <XAxis dataKey="date" tickFormatter={(v) => v.slice(5)} tick={{ fontSize: 9 }} interval="preserveStartEnd" />
                            <YAxis tick={{ fontSize: 9 }} allowDecimals={false} />
                            <Tooltip labelFormatter={(v) => `Date: ${v}`} formatter={(v) => [v, 'Fichiers']} />
                            <Area type="monotone" dataKey="count" stroke="#0d9488" fill="url(#s3UploadGrad)" strokeWidth={2} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Stats + Répartition par type */}
                  <Card>
                    <CardContent className="p-4">
                      <p className="text-sm font-semibold mb-3">Volume stocké</p>
                      <div className="text-center mb-4">
                        <p className="text-3xl font-bold text-[#0d9488]">
                          {s3Timeline.total_size > 1024 * 1024
                            ? `${(s3Timeline.total_size / (1024 * 1024)).toFixed(1)} Mo`
                            : s3Timeline.total_size > 1024
                              ? `${(s3Timeline.total_size / 1024).toFixed(1)} Ko`
                              : `${s3Timeline.total_size || 0} o`}
                        </p>
                        <p className="text-[10px] text-muted-foreground uppercase mt-1">{s3Timeline.total_files || 0} fichiers au total</p>
                      </div>
                      {(s3Timeline.by_type || []).length > 0 && (
                        <>
                          <p className="text-xs font-medium mb-2 text-muted-foreground">Par type de fichier</p>
                          <div className="h-[90px]">
                            <ResponsiveContainer width="100%" height="100%">
                              <PieChart>
                                <Pie
                                  data={s3Timeline.by_type}
                                  dataKey="count"
                                  nameKey="type"
                                  cx="50%"
                                  cy="50%"
                                  innerRadius={20}
                                  outerRadius={38}
                                  paddingAngle={3}
                                >
                                  {(s3Timeline.by_type || []).map((_, idx) => (
                                    <Cell key={idx} fill={['#0d9488', '#C9A84C', '#6366f1', '#ef4444', '#3b82f6', '#f59e0b'][idx % 6]} />
                                  ))}
                                </Pie>
                                <Tooltip formatter={(v, name) => [v, name]} />
                              </PieChart>
                            </ResponsiveContainer>
                          </div>
                          <div className="flex flex-wrap gap-2 mt-1 justify-center">
                            {(s3Timeline.by_type || []).slice(0, 4).map((t, i) => (
                              <span key={i} className="text-[9px] flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: ['#0d9488', '#C9A84C', '#6366f1', '#ef4444'][i % 4] }} />
                                {t.type} ({t.count})
                              </span>
                            ))}
                          </div>
                        </>
                      )}
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Alertes de stockage S3 */}
              <Card className="mb-4" data-testid="s3-storage-alerts">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Shield className="w-4 h-4 text-[#C9A84C]" />
                      <p className="text-sm font-semibold">Alertes de stockage</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <label className="text-[10px] text-muted-foreground">Actif</label>
                      <button
                        onClick={async () => {
                          const newConfig = { ...s3AlertConfig, enabled: !s3AlertConfig.enabled };
                          setS3AlertConfig(newConfig);
                          try {
                            await axios.put(`${API}/documents/storage-alerts/config`, newConfig, axiosConfig);
                            toast.success(newConfig.enabled ? 'Alertes activées' : 'Alertes désactivées');
                            const r = await axios.get(`${API}/documents/storage-alerts/check`, axiosConfig);
                            setS3AlertCheck(r.data);
                          } catch { toast.error('Erreur de sauvegarde'); }
                        }}
                        className={`w-9 h-5 rounded-full transition-colors relative ${s3AlertConfig.enabled ? 'bg-[#0d9488]' : 'bg-gray-300'}`}
                        data-testid="s3-alert-toggle"
                      >
                        <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${s3AlertConfig.enabled ? 'translate-x-4' : 'translate-x-0.5'}`} />
                      </button>
                    </div>
                  </div>

                  {s3AlertConfig.enabled && (
                    <>
                      {/* Threshold bars */}
                      <div className="space-y-2">
                        {(s3AlertCheck.alerts || []).map((alert, i) => (
                          <div key={i} className="flex items-center gap-3" data-testid={`s3-alert-bar-${i}`}>
                            <span className="text-xs w-14 text-right font-medium text-muted-foreground">{alert.label}</span>
                            <div className="flex-1 h-3 bg-muted/40 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all duration-500 ${
                                  alert.status === 'exceeded' ? 'bg-red-500' :
                                  alert.status === 'warning' ? 'bg-amber-500' : 'bg-[#0d9488]'
                                }`}
                                style={{ width: `${Math.min(alert.current_pct, 100)}%` }}
                              />
                            </div>
                            <span className={`text-xs font-bold w-14 ${
                              alert.status === 'exceeded' ? 'text-red-500' :
                              alert.status === 'warning' ? 'text-amber-500' : 'text-[#0d9488]'
                            }`}>
                              {alert.current_pct}%
                            </span>
                            {alert.status === 'exceeded' && <AlertTriangle className="w-3.5 h-3.5 text-red-500" />}
                          </div>
                        ))}
                      </div>

                      {/* Alert messages */}
                      {(s3AlertCheck.alerts || []).some(a => a.status === 'exceeded') && (
                        <div className="mt-3 p-2 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-md flex items-start gap-2">
                          <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-xs font-semibold text-red-700 dark:text-red-400">Seuil(s) dépassé(s)</p>
                            <p className="text-[10px] text-red-600 dark:text-red-400/80">
                              {(s3AlertCheck.alerts || []).filter(a => a.status === 'exceeded').map(a => a.label).join(', ')} — 
                              Volume actuel : {s3AlertCheck.current_size > 1024*1024*1024 
                                ? `${(s3AlertCheck.current_size / (1024*1024*1024)).toFixed(2)} Go`
                                : s3AlertCheck.current_size > 1024*1024 
                                  ? `${(s3AlertCheck.current_size / (1024*1024)).toFixed(1)} Mo`
                                  : `${(s3AlertCheck.current_size / 1024).toFixed(1)} Ko`}
                            </p>
                          </div>
                        </div>
                      )}

                      {(s3AlertCheck.alerts || []).some(a => a.status === 'warning') && !(s3AlertCheck.alerts || []).some(a => a.status === 'exceeded') && (
                        <div className="mt-3 p-2 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-md flex items-start gap-2">
                          <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                          <p className="text-xs text-amber-700 dark:text-amber-400">Approche d'un seuil — surveillez votre consommation S3.</p>
                        </div>
                      )}

                      {(s3AlertCheck.alerts || []).every(a => a.status === 'ok') && (s3AlertCheck.alerts || []).length > 0 && (
                        <p className="mt-2 text-[10px] text-muted-foreground">Aucun seuil atteint. Stockage sous contrôle.</p>
                      )}

                      {/* Threshold config */}
                      <div className="mt-3 pt-3 border-t flex flex-wrap gap-2 items-center">
                        <span className="text-[10px] text-muted-foreground">Seuils :</span>
                        {(s3AlertConfig.thresholds || []).map((t, i) => (
                          <button
                            key={i}
                            onClick={async () => {
                              const newThresholds = [...s3AlertConfig.thresholds];
                              newThresholds[i] = { ...newThresholds[i], active: !newThresholds[i].active };
                              const newConfig = { ...s3AlertConfig, thresholds: newThresholds };
                              setS3AlertConfig(newConfig);
                              try {
                                await axios.put(`${API}/documents/storage-alerts/config`, newConfig, axiosConfig);
                                const r = await axios.get(`${API}/documents/storage-alerts/check`, axiosConfig);
                                setS3AlertCheck(r.data);
                              } catch {}
                            }}
                            className={`text-[10px] px-2 py-0.5 rounded-full border transition-colors ${
                              t.active 
                                ? 'bg-[#0d9488]/10 border-[#0d9488] text-[#0d9488] font-medium' 
                                : 'bg-muted/20 border-muted-foreground/20 text-muted-foreground line-through'
                            }`}
                            data-testid={`s3-threshold-toggle-${i}`}
                          >
                            {t.label}
                          </button>
                        ))}
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>

              {(s3Docs.documents || []).length === 0 ? (
                <Card><CardContent className="py-12 text-center text-muted-foreground">Aucun document stocké dans S3 pour le moment</CardContent></Card>
              ) : (
                <Card>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-muted/30 border-b"><tr>
                          <th className="py-2 px-3 text-left font-medium text-muted-foreground">Fichier</th>
                          <th className="py-2 px-3 text-left font-medium text-muted-foreground">Source</th>
                          <th className="py-2 px-3 text-left font-medium text-muted-foreground">Type</th>
                          <th className="py-2 px-3 text-left font-medium text-muted-foreground">Taille</th>
                          <th className="py-2 px-3 text-left font-medium text-muted-foreground">Date</th>
                          <th className="py-2 px-3 text-left font-medium text-muted-foreground">Actions</th>
                        </tr></thead>
                        <tbody>
                          {(s3Docs.documents || []).map((doc) => (
                            <tr key={doc.id} className="border-b last:border-0 hover:bg-muted/20" data-testid={`s3-doc-${doc.id}`}>
                              <td className="py-2 px-3">
                                <p className="font-medium truncate max-w-[200px]">{doc.original_filename}</p>
                                {doc.user_email && <p className="text-[10px] text-muted-foreground">{doc.user_email}</p>}
                                {doc.dossier_id && <p className="text-[10px] text-muted-foreground">Dossier: {doc.dossier_id.slice(0, 8)}...</p>}
                              </td>
                              <td className="py-2 px-3"><Badge variant="outline" className="text-[10px]">{doc.source || 'upload'}</Badge></td>
                              <td className="py-2 px-3 text-muted-foreground text-xs">{doc.content_type?.split('/')[1] || doc.content_type}</td>
                              <td className="py-2 px-3 text-muted-foreground text-xs">{doc.size ? `${(doc.size / 1024).toFixed(1)} Ko` : '-'}</td>
                              <td className="py-2 px-3 text-muted-foreground text-xs">{doc.created_at ? new Date(doc.created_at).toLocaleDateString('fr-FR') : ''}</td>
                              <td className="py-2 px-3">
                                <div className="flex gap-1">
                                  <Button size="sm" variant="ghost" className="h-7 px-2 text-xs"
                                    onClick={async () => {
                                      try {
                                        const res = await axios.get(`${API}/documents/${doc.id}/url`, axiosConfig);
                                        if (res.data.url) window.open(res.data.url, '_blank');
                                      } catch { toast.error('Erreur de chargement du document'); }
                                    }}
                                    data-testid={`s3-view-${doc.id}`}
                                  >
                                    <Eye className="w-3 h-3 mr-1" /> Voir
                                  </Button>
                                  <Button size="sm" variant="ghost" className="h-7 px-2 text-xs"
                                    onClick={async () => {
                                      try {
                                        const res = await axios.get(`${API}/documents/${doc.id}/url`, axiosConfig);
                                        if (res.data.url) {
                                          const a = document.createElement('a');
                                          a.href = res.data.url;
                                          a.download = res.data.filename || doc.original_filename;
                                          a.click();
                                        }
                                      } catch { toast.error('Erreur de téléchargement'); }
                                    }}
                                    data-testid={`s3-download-${doc.id}`}
                                  >
                                    <Download className="w-3 h-3 mr-1" /> Télécharger
                                  </Button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Config Tab */}
          <TabsContent value="config" className="space-y-6" data-testid="config-tab-content">
            {/* Email Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2"><Mail className="w-5 h-5 text-accent" /> Configuration Email (Resend)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {emailStatus ? (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-3 rounded-lg border">
                        <p className="text-xs text-muted-foreground">Resend installé</p>
                        <p className="font-medium flex items-center gap-2">
                          {emailStatus.resend_installed ? <CheckCircle className="w-4 h-4 text-green-500" /> : <XCircle className="w-4 h-4 text-red-500" />}
                          {emailStatus.resend_installed ? 'Oui' : 'Non'}
                        </p>
                      </div>
                      <div className="p-3 rounded-lg border">
                        <p className="text-xs text-muted-foreground">Clé API</p>
                        <p className="font-medium flex items-center gap-2">
                          {emailStatus.api_key_configured ? <CheckCircle className="w-4 h-4 text-green-500" /> : <XCircle className="w-4 h-4 text-red-500" />}
                          {emailStatus.api_key_preview || 'Non configurée'}
                        </p>
                      </div>
                      <div className="p-3 rounded-lg border">
                        <p className="text-xs text-muted-foreground">Expéditeur</p>
                        <p className="font-medium text-sm">{emailStatus.sender_email}</p>
                      </div>
                      <div className="p-3 rounded-lg border">
                        <p className="text-xs text-muted-foreground">Notification admin</p>
                        <p className="font-medium text-sm">{emailStatus.notification_email}</p>
                      </div>
                    </div>
                    <div className="p-4 rounded-lg border border-accent/20 bg-accent/5 space-y-2">
                      <p className="text-sm font-medium flex items-center gap-2"><Shield className="w-4 h-4 text-accent" /> Vérification de domaine Resend</p>
                      <p className="text-xs text-muted-foreground">Pour envoyer des emails depuis votre propre domaine (au lieu de onboarding@resend.dev), suivez ces étapes :</p>
                      <ol className="text-xs text-muted-foreground space-y-1 list-decimal ml-4">
                        <li>Connectez-vous sur <a href="https://resend.com/domains" target="_blank" rel="noopener noreferrer" className="text-accent hover:underline">resend.com/domains</a></li>
                        <li>Ajoutez votre domaine (ex: accompagn-santé.fr)</li>
                        <li>Ajoutez les enregistrements DNS (SPF, DKIM, DMARC) fournis par Resend</li>
                        <li>Attendez la vérification (quelques minutes à 24h)</li>
                        <li>Mettez à jour SENDER_EMAIL dans la configuration backend</li>
                      </ol>
                    </div>
                    <Button size="sm" variant="outline" className="gap-2"
                      onClick={async () => {
                        try {
                          const res = await axios.post(`${API}/admin/email/test`, { email: emailStatus.notification_email || 'admin@accompagn-santé.fr' }, axiosConfig);
                          if (res.data.success) toast.success('Email test envoyé');
                          else toast.error(res.data.message);
                        } catch { toast.error('Erreur envoi test'); }
                      }}
                      data-testid="email-test-btn"
                    >
                      <Send className="w-3 h-3" /> Envoyer un email test
                    </Button>
                  </>
                ) : (
                  <p className="text-sm text-muted-foreground">Chargement...</p>
                )}
              </CardContent>
            </Card>

            {/* Storage Status */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2"><Upload className="w-5 h-5 text-accent" /> Stockage Objet</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="p-3 rounded-lg border flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <div>
                    <p className="font-medium text-sm">Emergent Object Storage</p>
                    <p className="text-xs text-muted-foreground">Les documents sont stockés de manière sécurisée dans le stockage objet cloud.</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ═══ Chiffres du site ═══ */}
            <Card data-testid="config-chiffres-site">
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2"><BarChart3 className="w-5 h-5 text-accent" /> Chiffres du site</CardTitle>
                <p className="text-xs text-muted-foreground">Contrôlez les chiffres affichés publiquement sur le site.</p>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Compteur Hero */}
                <div className="space-y-2" data-testid="config-compteur-hero">
                  <label className="text-sm font-semibold text-foreground">Compteur visiteurs (Hero)</label>
                  <p className="text-[11px] text-muted-foreground">Affiché sur le Hero : "X+ visiteurs" — s'incrémente automatiquement à chaque visite.</p>
                  <div className="flex items-end gap-3">
                    <input
                      type="number"
                      min="0"
                      data-testid="compteur-hero-input"
                      className="w-40 px-3 py-2 rounded-lg border bg-background text-foreground text-sm"
                      defaultValue=""
                      ref={(el) => {
                        if (el && !el.dataset.loaded) {
                          axios.get(`${API}/admin/compteur`, axiosConfig)
                            .then(res => { el.value = res.data.count; el.dataset.loaded = "true"; })
                            .catch(() => {});
                        }
                      }}
                      id="compteur-hero-input"
                    />
                    <Button
                      size="sm"
                      className="gap-2"
                      data-testid="compteur-hero-save"
                      onClick={async () => {
                        const input = document.getElementById('compteur-hero-input');
                        const val = parseInt(input?.value);
                        if (isNaN(val) || val < 0) { toast.error('Valeur invalide'); return; }
                        try {
                          await axios.put(`${API}/admin/compteur`, { count: val }, axiosConfig);
                          toast.success(`Compteur mis à jour : ${val.toLocaleString('fr-FR')}+`);
                        } catch { toast.error('Erreur lors de la sauvegarde'); }
                      }}
                    >
                      <CheckCircle className="w-3 h-3" /> Enregistrer
                    </Button>
                  </div>
                </div>

                <hr className="border-border/50" />

                {/* Compteur Dossiers hebdo */}
                <div className="space-y-2" data-testid="config-compteur-dossiers">
                  <label className="text-sm font-semibold text-foreground">Dossiers analysés cette semaine (Dossier Express)</label>
                  <p className="text-[11px] text-muted-foreground">Base ajoutée au nombre réel de dossiers. Affiché : "base + vrais dossiers cette semaine"</p>
                  <div className="flex items-end gap-3">
                    <input
                      type="number"
                      min="0"
                      data-testid="compteur-dossiers-input"
                      className="w-40 px-3 py-2 rounded-lg border bg-background text-foreground text-sm"
                      defaultValue=""
                      ref={(el) => {
                        if (el && !el.dataset.loaded) {
                          axios.get(`${API}/admin/compteur-dossiers`, axiosConfig)
                            .then(res => { el.value = res.data.base; el.dataset.loaded = "true"; })
                            .catch(() => {});
                        }
                      }}
                      id="compteur-dossiers-input"
                    />
                    <Button
                      size="sm"
                      className="gap-2"
                      data-testid="compteur-dossiers-save"
                      onClick={async () => {
                        const input = document.getElementById('compteur-dossiers-input');
                        const val = parseInt(input?.value);
                        if (isNaN(val) || val < 0) { toast.error('Valeur invalide'); return; }
                        try {
                          await axios.put(`${API}/admin/compteur-dossiers`, { base: val }, axiosConfig);
                          toast.success(`Base dossiers mis à jour : ${val}`);
                        } catch { toast.error('Erreur lors de la sauvegarde'); }
                      }}
                    >
                      <CheckCircle className="w-3 h-3" /> Enregistrer
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ═══ Le défi en chiffres ═══ */}
            <Card data-testid="config-chiffres-cles">
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2"><BarChart3 className="w-5 h-5 text-accent" /> Le défi en chiffres</CardTitle>
                <p className="text-xs text-muted-foreground">Les 4 statistiques clés affichées sur la page d'accueil.</p>
              </CardHeader>
              <CardContent>
                <ChiffresClesEditor axiosConfig={axiosConfig} />
              </CardContent>
            </Card>

            {/* ═══ Tarifs & Promotions ═══ */}
            <Card data-testid="config-tarifs">
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2"><Tag className="w-5 h-5 text-accent" /> Tarifs & Promotions</CardTitle>
                <p className="text-xs text-muted-foreground">Modifiez les prix et ajoutez des badges promotionnels.</p>
              </CardHeader>
              <CardContent>
                <TarifsEditor axiosConfig={axiosConfig} />
              </CardContent>
            </Card>

            {/* ═══ Onboarding Straté Stats ═══ */}
            <OnboardingStatsCard axiosConfig={axiosConfig} onRestartTour={() => setShowTour(true)} />

            {/* Push Notifications Status */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2"><Bell className="w-5 h-5 text-accent" /> Notifications Push</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="p-3 rounded-lg border flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <div>
                    <p className="font-medium text-sm">Service Worker + VAPID actif</p>
                    <p className="text-xs text-muted-foreground">Les notifications push sont envoyées automatiquement lors des événements suivants : validation/rejet de document, mise à jour de dossier, analyse premium prête.</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ═══ V2 Readiness Status (Feu tricolore) ═══ */}
            <AdminV2Readiness axiosConfig={axiosConfig} />

            {/* ═══ V2 Predictive Module (Dormant) ═══ */}
            <AdminPredictiveV2 axiosConfig={axiosConfig} />

            {/* ═══ Préparation Production ═══ */}
            <ProductionCleanupCard axiosConfig={axiosConfig} />
          </TabsContent>
          <TabsContent value="notifications" className="space-y-6" data-testid="notifications-tab-content">
            {/* Engagement KPIs Dashboard */}
            {engagementKpis && (
              <Card data-testid="engagement-kpis-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-base flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-blue-500" /> KPIs d'engagement
                      </CardTitle>
                      <p className="text-xs text-muted-foreground">Impact des relances automatiques et manuelles sur l'engagement client</p>
                    </div>
                    <Button size="sm" variant="outline" className="gap-1.5 text-xs" data-testid="export-csv-btn"
                      onClick={() => {
                        const link = document.createElement('a');
                        link.href = `${API}/admin/export/relances-csv`;
                        link.download = 'relances_kpis_export.csv';
                        const token = adminToken;
                        fetch(`${API}/admin/export/relances-csv`, { headers: { Authorization: `Bearer ${token}` } })
                          .then(r => r.blob())
                          .then(blob => { link.href = URL.createObjectURL(blob); link.click(); toast.success('Export CSV téléchargé'); })
                          .catch(() => toast.error('Erreur export'));
                      }}
                    >
                      <Download className="w-3.5 h-3.5" /> Exporter CSV
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* KPI Alerts */}
                  {kpiAlerts.alerts?.length > 0 && (
                    <div className="space-y-2" data-testid="kpi-alerts-section">
                      {kpiAlerts.alerts.map((alert, i) => (
                        <div key={i} className={`flex items-center gap-3 p-3 rounded-lg border ${alert.severity === 'critical' ? 'bg-red-50 border-red-200' : 'bg-amber-50 border-amber-200'}`}>
                          <AlertTriangle className={`w-4 h-4 flex-shrink-0 ${alert.severity === 'critical' ? 'text-red-600' : 'text-amber-600'}`} />
                          <div className="flex-1">
                            <p className={`text-xs font-semibold ${alert.severity === 'critical' ? 'text-red-700' : 'text-amber-700'}`}>{alert.message}</p>
                          </div>
                          <Badge variant="outline" className={`text-[10px] ${alert.severity === 'critical' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>
                            {alert.severity === 'critical' ? 'Critique' : 'Attention'}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Alert thresholds config */}
                  <div className="flex flex-wrap items-center gap-3 sm:gap-4 p-3 rounded-lg bg-muted/30 border" data-testid="kpi-alert-config">
                    <span className="text-xs text-muted-foreground whitespace-nowrap">Seuils d'alerte :</span>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] text-muted-foreground">Ouverture &lt;</span>
                      <input type="number" className="w-14 h-7 text-xs text-center rounded border px-1" value={kpiAlertConfig.open_rate_threshold}
                        onChange={e => setKpiAlertConfig(c => ({...c, open_rate_threshold: parseInt(e.target.value) || 0}))} />
                      <span className="text-[10px] text-muted-foreground">%</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] text-muted-foreground">Clic &lt;</span>
                      <input type="number" className="w-14 h-7 text-xs text-center rounded border px-1" value={kpiAlertConfig.click_rate_threshold}
                        onChange={e => setKpiAlertConfig(c => ({...c, click_rate_threshold: parseInt(e.target.value) || 0}))} />
                      <span className="text-[10px] text-muted-foreground">%</span>
                    </div>
                    <Button size="sm" variant="outline" className="h-7 text-[10px] px-3"
                      onClick={async () => {
                        try {
                          await axios.post(`${API}/admin/kpi-alerts/config`, kpiAlertConfig, { headers: { Authorization: `Bearer ${adminToken}` } });
                          const r = await axios.get(`${API}/admin/kpi-alerts/check`, { headers: { Authorization: `Bearer ${adminToken}` } });
                          setKpiAlerts(r.data);
                          toast.success('Seuils mis à jour');
                        } catch { toast.error('Erreur'); }
                      }}
                      data-testid="save-alert-config-btn"
                    >
                      Enregistrer
                    </Button>
                  </div>
                  {/* Main KPI cards */}
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                    <div className="p-3 rounded-lg border text-center">
                      <p className="text-2xl font-bold">{engagementKpis.summary.total_sent}</p>
                      <p className="text-[10px] text-muted-foreground uppercase">Emails envoyés</p>
                    </div>
                    <div className="p-3 rounded-lg border text-center">
                      <p className="text-2xl font-bold text-blue-600">{engagementKpis.summary.total_opened}</p>
                      <p className="text-[10px] text-muted-foreground uppercase">Ouvertures</p>
                    </div>
                    <div className="p-3 rounded-lg border text-center">
                      <p className="text-2xl font-bold text-green-600">{engagementKpis.summary.total_clicked}</p>
                      <p className="text-[10px] text-muted-foreground uppercase">Clics CTA</p>
                    </div>
                    <div className="p-3 rounded-lg border text-center bg-blue-50">
                      <p className="text-2xl font-bold text-blue-700">{engagementKpis.summary.open_rate}%</p>
                      <p className="text-[10px] text-muted-foreground uppercase">Taux d'ouverture</p>
                    </div>
                    <div className="p-3 rounded-lg border text-center bg-green-50">
                      <p className="text-2xl font-bold text-green-700">{engagementKpis.summary.click_rate}%</p>
                      <p className="text-[10px] text-muted-foreground uppercase">Taux de clic</p>
                    </div>
                    <div className="p-3 rounded-lg border text-center bg-amber-50">
                      <p className="text-2xl font-bold text-amber-700">{engagementKpis.summary.click_to_open_rate}%</p>
                      <p className="text-[10px] text-muted-foreground uppercase">Clic / ouverture</p>
                    </div>
                  </div>

                  {/* By level breakdown */}
                  <div>
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Performance par niveau de relance</h4>
                    <div className="grid grid-cols-3 gap-3">
                      {engagementKpis.by_level.map(lvl => (
                        <div key={lvl.level} className="p-3 rounded-lg border">
                          <div className="flex items-center justify-between mb-2">
                            <Badge variant="outline" className={`text-xs ${lvl.level === 3 ? 'bg-red-100 text-red-700' : lvl.level === 2 ? 'bg-orange-100 text-orange-700' : 'bg-amber-100 text-amber-700'}`}>
                              {lvl.level === 1 ? 'J+7' : lvl.level === 2 ? 'J+14' : 'J+21'}
                            </Badge>
                            <span className="text-xs text-muted-foreground">{lvl.total} envoyés</span>
                          </div>
                          <div className="space-y-1.5">
                            <div>
                              <div className="flex justify-between text-[10px] mb-0.5">
                                <span className="text-muted-foreground">Ouverture</span>
                                <span className="font-medium text-blue-600">{lvl.open_rate}%</span>
                              </div>
                              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${Math.min(lvl.open_rate, 100)}%` }} />
                              </div>
                            </div>
                            <div>
                              <div className="flex justify-between text-[10px] mb-0.5">
                                <span className="text-muted-foreground">Clic CTA</span>
                                <span className="font-medium text-green-600">{lvl.click_rate}%</span>
                              </div>
                              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                                <div className="h-full bg-green-500 rounded-full" style={{ width: `${Math.min(lvl.click_rate, 100)}%` }} />
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Completeness evolution */}
                  <div className="p-4 rounded-lg border bg-gradient-to-r from-blue-50 to-green-50" data-testid="completeness-evolution">
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">Évolution de la complétude après relance</h4>
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Complétude avant</p>
                        <p className="text-2xl font-bold text-orange-600">{engagementKpis.completeness_evolution.avg_before}%</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Complétude après</p>
                        <p className="text-2xl font-bold text-green-600">{engagementKpis.completeness_evolution.avg_after}%</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Amélioration</p>
                        <p className={`text-2xl font-bold ${engagementKpis.completeness_evolution.improvement > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                          {engagementKpis.completeness_evolution.improvement > 0 ? '+' : ''}{engagementKpis.completeness_evolution.improvement}%
                        </p>
                      </div>
                    </div>
                    <p className="text-[10px] text-muted-foreground text-center mt-2">
                      Basé sur {engagementKpis.completeness_evolution.clients_tracked} client(s) ayant cliqué sur le CTA
                    </p>
                  </div>

                  {/* Timeline chart */}
                  {engagementKpis.timeline.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Activité des 30 derniers jours</h4>
                      <div className="h-40">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={engagementKpis.timeline}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="date" tick={{ fontSize: 9 }} tickFormatter={v => v.slice(5)} />
                            <YAxis tick={{ fontSize: 9 }} />
                            <Tooltip contentStyle={{ fontSize: 11 }} />
                            <Bar dataKey="sent" fill="#94a3b8" name="Envoyés" radius={[2, 2, 0, 0]} />
                            <Bar dataKey="opened" fill="#3b82f6" name="Ouverts" radius={[2, 2, 0, 0]} />
                            <Bar dataKey="clicked" fill="#16a34a" name="Cliqués" radius={[2, 2, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <BellRing className="w-5 h-5 text-amber-500" /> Notifications de complétude
                </CardTitle>
                <p className="text-xs text-muted-foreground">Emails envoyés automatiquement aux clients lorsqu'ils atteignent 50%, 80% ou 100% de complétude</p>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Stats cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="p-3 rounded-lg border text-center">
                    <p className="text-2xl font-bold">{completenessNotifs.stats.total || 0}</p>
                    <p className="text-[10px] text-muted-foreground uppercase">Total envoyées</p>
                  </div>
                  <div className="p-3 rounded-lg border text-center">
                    <p className="text-2xl font-bold text-green-600">{completenessNotifs.stats.sent || 0}</p>
                    <p className="text-[10px] text-muted-foreground uppercase">Envoyées</p>
                  </div>
                  <div className="p-3 rounded-lg border text-center">
                    <p className="text-2xl font-bold text-red-500">{completenessNotifs.stats.failed || 0}</p>
                    <p className="text-[10px] text-muted-foreground uppercase">Échouées</p>
                  </div>
                  <div className="p-3 rounded-lg border text-center">
                    <p className="text-2xl font-bold text-gray-400">{completenessNotifs.stats.skipped || 0}</p>
                    <p className="text-[10px] text-muted-foreground uppercase">Non envoyées</p>
                  </div>
                </div>

                {/* By threshold */}
                <div className="grid grid-cols-3 gap-3">
                  {[{pct: 50, label: "50% — Mi-chemin", color: "text-amber-600"}, {pct: 80, label: "80% — Presque complet", color: "text-blue-600"}, {pct: 100, label: "100% — Complet", color: "text-green-600"}].map(t => (
                    <div key={t.pct} className="p-3 rounded-lg border">
                      <p className={`text-lg font-bold ${t.color}`}>{completenessNotifs.by_threshold?.[String(t.pct)] || 0}</p>
                      <p className="text-[10px] text-muted-foreground">{t.label}</p>
                    </div>
                  ))}
                </div>

                {/* History table */}
                {completenessNotifs.notifications?.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm" data-testid="completeness-notifs-table">
                      <thead>
                        <tr className="border-b text-left text-muted-foreground">
                          <th className="pb-2 font-medium">Date</th>
                          <th className="pb-2 font-medium">Client</th>
                          <th className="pb-2 font-medium text-center">Seuil</th>
                          <th className="pb-2 font-medium text-center">Complétude</th>
                          <th className="pb-2 font-medium">Type dossier</th>
                          <th className="pb-2 font-medium text-center">Statut</th>
                        </tr>
                      </thead>
                      <tbody>
                        {completenessNotifs.notifications.map((n, i) => (
                          <tr key={n.id || i} className="border-b last:border-0">
                            <td className="py-2 text-xs">{new Date(n.created_at).toLocaleDateString('fr-FR', {day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'})}</td>
                            <td className="py-2">
                              <p className="text-xs font-medium">{n.client_name || 'N/A'}</p>
                              <p className="text-[10px] text-muted-foreground">{n.client_email}</p>
                            </td>
                            <td className="py-2 text-center">
                              <Badge variant="outline" className={`text-xs ${n.threshold_pct === 100 ? 'bg-green-100 text-green-700' : n.threshold_pct === 80 ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>
                                {n.threshold_pct}%
                              </Badge>
                            </td>
                            <td className="py-2 text-center text-xs font-medium">{n.actual_pct}%</td>
                            <td className="py-2 text-xs">{n.case_type || '—'}</td>
                            <td className="py-2 text-center">
                              <Badge variant="outline" className={`text-[10px] ${n.status === 'sent' ? 'bg-green-100 text-green-700' : n.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-500'}`}>
                                {n.status === 'sent' ? 'Envoyé' : n.status === 'failed' ? 'Échoué' : 'Non envoyé'}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8 text-sm">Aucune notification de complétude envoyée pour le moment.</p>
                )}
              </CardContent>
            </Card>

            {/* Inactivity Reminders Section */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Clock className="w-5 h-5 text-orange-500" /> Relances d'inactivité
                    </CardTitle>
                    <p className="text-xs text-muted-foreground mt-1">Emails envoyés aux clients inactifs (&lt; 50% complétude, aucun upload depuis 7+ jours) — J+7, J+14, J+21</p>
                  </div>
                  <div className="flex items-center gap-3">
                    {/* Cron toggle */}
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border bg-muted/30" data-testid="cron-toggle-section">
                      <span className="text-[10px] text-muted-foreground whitespace-nowrap">Cron {cronStatus.hour}h{String(cronStatus.minute).padStart(2,'0')}</span>
                      <button
                        className={`relative w-9 h-5 rounded-full transition-colors ${cronStatus.enabled ? 'bg-green-500' : 'bg-gray-300'}`}
                        data-testid="cron-toggle-btn"
                        onClick={async () => {
                          const newVal = !cronStatus.enabled;
                          try {
                            await axios.post(`${API}/admin/reminder-cron/toggle`, { enabled: newVal }, { headers: { Authorization: `Bearer ${adminToken}` } });
                            setCronStatus(s => ({ ...s, enabled: newVal }));
                            toast.success(newVal ? 'Cron automatique activé' : 'Cron automatique désactivé');
                          } catch { toast.error('Erreur'); }
                        }}
                      >
                        <span className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${cronStatus.enabled ? 'left-[18px]' : 'left-0.5'}`} />
                      </button>
                    </div>
                    <Button
                      size="sm"
                      className="gap-1.5"
                      disabled={runningReminders}
                      data-testid="run-reminders-btn"
                      onClick={async () => {
                        setRunningReminders(true);
                        setLastReminderResults(null);
                        try {
                          const r = await axios.post(`${API}/admin/relance-inactivité/run`, {}, { headers: { Authorization: `Bearer ${adminToken}` } });
                          setLastReminderResults(r.data.results);
                          const h = await axios.get(`${API}/admin/relance-inactivité/history`, { headers: { Authorization: `Bearer ${adminToken}` } });
                          setInactivityReminders(h.data);
                        } catch {}
                        setRunningReminders(false);
                      }}
                    >
                      {runningReminders ? <><Clock className="w-3 h-3 animate-spin" /> Scan...</> : <><Send className="w-3 h-3" /> Lancer les relances</>}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Last cron run info */}
                {cronStatus.last_run && (
                  <div className="p-3 rounded-lg bg-muted/30 border flex items-center justify-between text-xs" data-testid="cron-last-run">
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-muted-foreground" />
                      <span className="text-muted-foreground">Dernière exécution automatique :</span>
                      <span className="font-medium">{new Date(cronStatus.last_run).toLocaleDateString('fr-FR', {day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'})}</span>
                    </div>
                    {cronStatus.last_results && (
                      <div className="flex gap-3">
                        <span>Scannés: <strong>{cronStatus.last_results.scanned}</strong></span>
                        <span>Éligibles: <strong>{cronStatus.last_results.eligible}</strong></span>
                        <span className="text-green-700">Envoyés: <strong>{cronStatus.last_results.sent}</strong></span>
                        <span className="text-red-600">Échoués: <strong>{cronStatus.last_results.failed}</strong></span>
                      </div>
                    )}
                  </div>
                )}
                {lastReminderResults && (
                  <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-sm" data-testid="reminder-results">
                    <p className="font-medium text-blue-800 mb-1">Résultat du scan</p>
                    <div className="grid grid-cols-3 md:grid-cols-6 gap-2 text-xs">
                      <span>Scannés: <strong>{lastReminderResults.scanned}</strong></span>
                      <span>Éligibles: <strong>{lastReminderResults.eligible}</strong></span>
                      <span className="text-green-700">Envoyés: <strong>{lastReminderResults.sent}</strong></span>
                      <span className="text-red-600">Échoués: <strong>{lastReminderResults.failed}</strong></span>
                      <span className="text-gray-500">Non envoyés: <strong>{lastReminderResults.skipped}</strong></span>
                      <span className="text-amber-600">Déjà relancés: <strong>{lastReminderResults.already_reminded}</strong></span>
                    </div>
                  </div>
                )}

                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="p-3 rounded-lg border text-center">
                    <p className="text-2xl font-bold">{inactivityReminders.stats.total || 0}</p>
                    <p className="text-[10px] text-muted-foreground uppercase">Total relances</p>
                  </div>
                  <div className="p-3 rounded-lg border text-center">
                    <p className="text-2xl font-bold text-green-600">{inactivityReminders.stats.sent || 0}</p>
                    <p className="text-[10px] text-muted-foreground uppercase">Envoyées</p>
                  </div>
                  <div className="p-3 rounded-lg border text-center">
                    <p className="text-2xl font-bold text-red-500">{inactivityReminders.stats.failed || 0}</p>
                    <p className="text-[10px] text-muted-foreground uppercase">Échouées</p>
                  </div>
                  <div className="p-3 rounded-lg border text-center">
                    <p className="text-2xl font-bold text-gray-400">{inactivityReminders.stats.skipped || 0}</p>
                    <p className="text-[10px] text-muted-foreground uppercase">Non envoyées</p>
                  </div>
                </div>

                {/* By level */}
                <div className="grid grid-cols-3 gap-3">
                  {[
                    {lvl: 1, label: "J+7 — Relance douce", color: "text-amber-600"},
                    {lvl: 2, label: "J+14 — Relance motivante", color: "text-orange-600"},
                    {lvl: 3, label: "J+21 — Dernière relance", color: "text-red-600"},
                  ].map(t => (
                    <div key={t.lvl} className="p-3 rounded-lg border">
                      <p className={`text-lg font-bold ${t.color}`}>{inactivityReminders.by_level?.[String(t.lvl)] || 0}</p>
                      <p className="text-[10px] text-muted-foreground">{t.label}</p>
                    </div>
                  ))}
                </div>

                {/* History table */}
                {inactivityReminders.reminders?.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm" data-testid="inactivity-reminders-table">
                      <thead>
                        <tr className="border-b text-left text-muted-foreground">
                          <th className="pb-2 font-medium">Date</th>
                          <th className="pb-2 font-medium">Client</th>
                          <th className="pb-2 font-medium text-center">Niveau</th>
                          <th className="pb-2 font-medium text-center">Inactif</th>
                          <th className="pb-2 font-medium text-center">Complétude</th>
                          <th className="pb-2 font-medium text-center">Statut</th>
                          <th className="pb-2 font-medium text-center">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {inactivityReminders.reminders.map((r, i) => (
                          <tr key={r.id || i} className="border-b last:border-0">
                            <td className="py-2 text-xs">{new Date(r.created_at).toLocaleDateString('fr-FR', {day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'})}</td>
                            <td className="py-2">
                              <p className="text-xs font-medium">{r.client_name || 'N/A'}</p>
                              <p className="text-[10px] text-muted-foreground">{r.client_email}</p>
                            </td>
                            <td className="py-2 text-center">
                              <Badge variant="outline" className={`text-xs ${r.level === 3 ? 'bg-red-100 text-red-700' : r.level === 2 ? 'bg-orange-100 text-orange-700' : 'bg-amber-100 text-amber-700'}`}>
                                L{r.level}
                              </Badge>
                            </td>
                            <td className="py-2 text-center text-xs">{r.days_inactive}j</td>
                            <td className="py-2 text-center text-xs font-medium">{r.completeness_pct}%</td>
                            <td className="py-2 text-center">
                              <Badge variant="outline" className={`text-[10px] ${r.status === 'sent' ? 'bg-green-100 text-green-700' : r.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-500'}`}>
                                {r.status === 'sent' ? 'Envoyé' : r.status === 'failed' ? 'Échoué' : 'Non envoyé'}
                              </Badge>
                            </td>
                            <td className="py-2 text-center">
                              <Button size="sm" variant="ghost" className="h-6 px-2 text-[10px]"
                                onClick={async () => {
                                  try {
                                    await axios.post(`${API}/admin/relance-inactivité/toggle-pause`, { client_id: r.client_id, paused: true }, { headers: { Authorization: `Bearer ${adminToken}` } });
                                    toast.success('Relances pausées pour ce client');
                                  } catch { toast.error('Erreur'); }
                                }}
                                data-testid={`pause-reminder-${i}`}
                              >
                                Pause
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8 text-sm">Aucune relance envoyée pour le moment. Cliquez sur "Lancer les relances" pour scanner les clients inactifs.</p>
                )}
              </CardContent>
            </Card>

            {/* A/B Testing Section */}
            <Card data-testid="ab-testing-section">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-base flex items-center gap-2">
                      <FlaskConical className="w-5 h-5 text-purple-500" /> A/B Testing Emails
                    </CardTitle>
                    <p className="text-xs text-muted-foreground mt-1">Testez différentes variantes d'emails pour optimiser l'engagement</p>
                  </div>
                  {!abTests.some(t => t.status === 'active') && (
                    <Button size="sm" className="gap-1.5" disabled={creatingAb} data-testid="create-ab-test-btn"
                      onClick={async () => {
                        setCreatingAb(true);
                        try {
                          await axios.post(`${API}/admin/ab-tests`, {
                            name: `Test A/B — ${new Date().toLocaleDateString('fr-FR')}`,
                            variants: [
                              { name: 'rassurant', label: 'Ton rassurant' },
                              { name: 'incitatif', label: 'Ton incitatif' },
                              { name: 'urgent', label: 'Ton urgent' },
                            ],
                            min_sends: 50,
                          }, { headers: { Authorization: `Bearer ${adminToken}` } });
                          const r = await axios.get(`${API}/admin/ab-tests`, { headers: { Authorization: `Bearer ${adminToken}` } });
                          setAbTests(r.data.tests || []);
                          toast.success('Test A/B créé et activé');
                        } catch { toast.error('Erreur'); }
                        setCreatingAb(false);
                      }}
                    >
                      <FlaskConical className="w-3 h-3" /> Créer un test A/B
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {abTests.length === 0 ? (
                  <p className="text-center text-muted-foreground py-6 text-sm">Aucun test A/B créé. Créez-en un pour comparer les performances des différents tons d'email.</p>
                ) : (
                  abTests.map(test => {
                    const res = abResults[test.id];
                    return (
                      <div key={test.id} className="border rounded-lg overflow-hidden" data-testid={`ab-test-${test.id}`}>
                        <div className="flex items-center justify-between p-3 bg-muted/30 border-b">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold">{test.name}</span>
                            <Badge variant="outline" className={`text-[10px] ${test.status === 'active' ? 'bg-green-100 text-green-700' : test.status === 'completed' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'}`}>
                              {test.status === 'active' ? 'Actif' : test.status === 'completed' ? 'Terminé' : 'Pausé'}
                            </Badge>
                            {test.promoted_variant && (
                              <Badge className="text-[10px] bg-green-600">Gagnant : {test.promoted_variant}</Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] text-muted-foreground">Min. {test.min_sends_per_variant} envois/variante</span>
                            {test.status === 'active' && (
                              <Button size="sm" variant="ghost" className="h-6 px-2 text-[10px]"
                                onClick={async () => {
                                  await axios.post(`${API}/admin/ab-tests/${test.id}/toggle`, { status: 'paused' }, { headers: { Authorization: `Bearer ${adminToken}` } });
                                  const r = await axios.get(`${API}/admin/ab-tests`, { headers: { Authorization: `Bearer ${adminToken}` } });
                                  setAbTests(r.data.tests || []);
                                  toast.success('Test pausé');
                                }}
                              >Pause</Button>
                            )}
                            {test.status === 'paused' && (
                              <Button size="sm" variant="ghost" className="h-6 px-2 text-[10px]"
                                onClick={async () => {
                                  await axios.post(`${API}/admin/ab-tests/${test.id}/toggle`, { status: 'active' }, { headers: { Authorization: `Bearer ${adminToken}` } });
                                  const r = await axios.get(`${API}/admin/ab-tests`, { headers: { Authorization: `Bearer ${adminToken}` } });
                                  setAbTests(r.data.tests || []);
                                  toast.success('Test réactivé');
                                }}
                              >Activer</Button>
                            )}
                          </div>
                        </div>

                        {/* Results grid */}
                        {res && (
                          <div className="p-3 space-y-3">
                            <div className="grid grid-cols-3 gap-3">
                              {res.results.map(v => {
                                const isWinner = res.winner && res.winner.variant === v.variant;
                                return (
                                  <div key={v.variant} className={`p-3 rounded-lg border ${isWinner ? 'bg-green-50 border-green-300 ring-2 ring-green-200' : 'bg-white'}`}>
                                    <div className="flex items-center justify-between mb-2">
                                      <span className="text-xs font-semibold capitalize">{v.variant}</span>
                                      {isWinner && <Badge className="text-[9px] bg-green-600 px-1">Meilleur</Badge>}
                                    </div>
                                    <p className="text-lg font-bold">{v.sent} <span className="text-xs font-normal text-muted-foreground">envoyés</span></p>
                                    <div className="space-y-1.5 mt-2">
                                      <div>
                                        <div className="flex justify-between text-[10px] mb-0.5">
                                          <span className="text-muted-foreground">Ouverture</span>
                                          <span className="font-medium text-blue-600">{v.open_rate}%</span>
                                        </div>
                                        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                                          <div className="h-full bg-blue-500 rounded-full" style={{ width: `${Math.min(v.open_rate, 100)}%` }} />
                                        </div>
                                      </div>
                                      <div>
                                        <div className="flex justify-between text-[10px] mb-0.5">
                                          <span className="text-muted-foreground">Clic CTA</span>
                                          <span className="font-medium text-green-600">{v.click_rate}%</span>
                                        </div>
                                        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                                          <div className="h-full bg-green-500 rounded-full" style={{ width: `${Math.min(v.click_rate, 100)}%` }} />
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                );
                              })}
                            </div>

                            {/* Promote winner button */}
                            {res.ready_to_promote && !test.promoted_variant && (
                              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                                <div>
                                  <p className="text-xs font-semibold text-green-800">Variante gagnante identifiée : <span className="capitalize">{res.winner.variant}</span></p>
                                  <p className="text-[10px] text-green-600">Taux de clic : {res.winner.click_rate}% ({res.winner.sent} envois)</p>
                                </div>
                                <Button size="sm" className="bg-green-600 hover:bg-green-700 text-xs gap-1" data-testid="promote-winner-btn"
                                  onClick={async () => {
                                    await axios.post(`${API}/admin/ab-tests/${test.id}/promote`, { variant_name: res.winner.variant }, { headers: { Authorization: `Bearer ${adminToken}` } });
                                    const r = await axios.get(`${API}/admin/ab-tests`, { headers: { Authorization: `Bearer ${adminToken}` } });
                                    setAbTests(r.data.tests || []);
                                    toast.success(`Variante "${res.winner.variant}" promue comme template principal`);
                                  }}
                                >
                                  Promouvoir gagnant
                                </Button>
                              </div>
                            )}

                            {!res.ready_to_promote && !test.promoted_variant && (
                              <p className="text-center text-[10px] text-muted-foreground py-1">
                                En attente de {test.min_sends_per_variant} envois minimum par variante pour déterminer le gagnant
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Templates Tab */}
          <TabsContent value="templates" className="space-y-6" data-testid="templates-tab-content">
            <EmailTemplateEditor token={token} />
          </TabsContent>

          {/* Conseils Strate Tab */}
          <TabsContent value="conseils-strate" className="space-y-6" data-testid="conseils-strate-tab-content">
            <AdminConseilsStrate axiosConfig={axiosConfig} />
          </TabsContent>

          <TabsContent value="feedback" className="space-y-6" data-testid="feedback-tab-content">
            <AdminStrategicFeedback axiosConfig={axiosConfig} />
          </TabsContent>
        </Tabs>
      </main>

      {/* Contact Detail Modal */}
      <Dialog open={showDetailModal} onOpenChange={setShowDetailModal}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          {selectedContact && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  {selectedContact.prenom} {selectedContact.nom}
                  {getStatusBadge(selectedContact.status)}
                </DialogTitle>
                <DialogDescription>
                  Demande reçue le {formatDate(selectedContact.created_at)}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-6 py-4">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Email</p>
                    <a href={`mailto:${selectedContact.email}`} className="text-accent hover:underline">
                      {selectedContact.email}
                    </a>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Téléphone</p>
                    <p>{selectedContact.telephone || "Non renseigné"}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Type d'accompagnement</p>
                    <p>{selectedContact.type_accompagnement || "Non spécifié"}</p>
                  </div>
                </div>

                {/* Origin tags */}
                {(selectedContact.tracking_via || selectedContact.tracking_source) && (
                  <div className="flex items-center gap-3 p-3 bg-amber-50/60 rounded-lg border border-amber-100" data-testid="contact-origin-block">
                    <Globe className="w-4 h-4 text-amber-600 flex-shrink-0" />
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs text-muted-foreground font-medium">Origine :</span>
                      {selectedContact.tracking_via && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-800" data-testid="detail-canal-tag">
                          {selectedContact.tracking_via === 'qr' && <QrCode className="w-3 h-3" />}
                          {selectedContact.tracking_via === 'email' && <Mail className="w-3 h-3" />}
                          {selectedContact.tracking_via === 'pdf_link' && <FileText className="w-3 h-3" />}
                          Canal : {selectedContact.tracking_via === 'qr' ? 'QR PDF' : selectedContact.tracking_via === 'email' ? 'Email' : selectedContact.tracking_via === 'pdf_link' ? 'Lien PDF' : selectedContact.tracking_via}
                        </span>
                      )}
                      {selectedContact.tracking_source && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-blue-100 text-blue-800" data-testid="detail-source-tag">
                          Source : {selectedContact.tracking_source === 'dossier_express' ? 'Dossier Express IA' : selectedContact.tracking_source === 'strategiia' ? 'StrategiIA' : selectedContact.tracking_source}
                        </span>
                      )}
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Sujet</p>
                  <p className="font-medium">{selectedContact.sujet}</p>
                </div>

                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Message</p>
                  <div className="bg-muted/30 p-4 rounded-lg">
                    <p className="whitespace-pre-wrap">{selectedContact.message}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Notes administrateur</p>
                  <Textarea
                    value={notesAdmin}
                    onChange={(e) => setNotesAdmin(e.target.value)}
                    placeholder="Ajoutez des notes internes..."
                    rows={3}
                    data-testid="admin-notes"
                  />
                </div>

                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Changer le statut</p>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant={selectedContact.status === 'nouveau' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => handleUpdateStatus(selectedContact.id, 'nouveau')}
                      disabled={updatingStatus}
                    >
                      Nouveau
                    </Button>
                    <Button
                      variant={selectedContact.status === 'en_cours' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => handleUpdateStatus(selectedContact.id, 'en_cours')}
                      disabled={updatingStatus}
                    >
                      En cours
                    </Button>
                    <Button
                      variant={selectedContact.status === 'traite' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => handleUpdateStatus(selectedContact.id, 'traite')}
                      disabled={updatingStatus}
                    >
                      Traite
                    </Button>
                    <Button
                      variant={selectedContact.status === 'converti' ? 'default' : 'outline'}
                      size="sm"
                      className={selectedContact.status === 'converti' ? 'bg-emerald-600 hover:bg-emerald-700 text-white' : 'border-emerald-300 text-emerald-700 hover:bg-emerald-50'}
                      onClick={() => {
                        if (selectedContact.status !== 'converti') {
                          setShowConversionForm(true);
                        }
                      }}
                      disabled={updatingStatus}
                      data-testid="btn-converti"
                    >
                      <BadgeCheck className="w-3.5 h-3.5 mr-1" />
                      Converti
                    </Button>
                  </div>
                </div>

                {/* Conversion form */}
                {showConversionForm && selectedContact.status !== 'converti' && (
                  <div className="space-y-3 p-4 bg-emerald-50/60 rounded-lg border border-emerald-200" data-testid="conversion-form">
                    <p className="text-sm font-medium text-emerald-800 flex items-center gap-2">
                      <BadgeCheck className="w-4 h-4" />
                      Marquer comme converti
                    </p>
                    <div className="grid sm:grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <Label className="text-xs text-muted-foreground">Montant facture</Label>
                        <Input
                          type="number"
                          placeholder="0"
                          value={conversionMontant}
                          onChange={(e) => setConversionMontant(e.target.value)}
                          data-testid="conversion-montant"
                          className="h-9"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-xs text-muted-foreground">Type de prestation</Label>
                        <Select value={conversionPrestation} onValueChange={setConversionPrestation}>
                          <SelectTrigger className="h-9" data-testid="conversion-prestation">
                            <SelectValue placeholder="Choisir..." />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="accompagnement_mp">Accompagnement MP</SelectItem>
                            <SelectItem value="protection_juridique">Protection juridique</SelectItem>
                            <SelectItem value="expertise_médicale">Expertise médicale</SelectItem>
                            <SelectItem value="dossier_complet">Dossier complet</SelectItem>
                            <SelectItem value="consultation">Consultation</SelectItem>
                            <SelectItem value="autre">Autre</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="flex gap-2 pt-1">
                      <Button
                        size="sm"
                        className="bg-emerald-600 hover:bg-emerald-700 text-white"
                        onClick={() => handleConversion(selectedContact.id)}
                        disabled={updatingStatus || !conversionMontant}
                        data-testid="confirm-conversion"
                      >
                        Confirmer la conversion
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setShowConversionForm(false)}
                      >
                        Annuler
                      </Button>
                    </div>
                  </div>
                )}

                {/* Show conversion info if already converted */}
                {selectedContact.status === 'converti' && (
                  <div className="p-4 bg-emerald-50/60 rounded-lg border border-emerald-200" data-testid="conversion-info">
                    <p className="text-sm font-medium text-emerald-800 flex items-center gap-2 mb-2">
                      <BadgeCheck className="w-4 h-4" />
                      Lead converti
                    </p>
                    <div className="grid sm:grid-cols-3 gap-3 text-sm">
                      <div>
                        <p className="text-muted-foreground text-xs">Montant</p>
                        <p className="font-semibold text-emerald-700">{selectedContact.conversion_montant ? formatEuro(selectedContact.conversion_montant) : '-'}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground text-xs">Prestation</p>
                        <p className="font-medium">{selectedContact.conversion_prestation || '-'}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground text-xs">Date conversion</p>
                        <p className="font-medium">{selectedContact.conversion_date || '-'}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <DialogFooter className="flex-col sm:flex-row gap-2">
                <Button
                  variant="destructive"
                  onClick={() => {
                    setContactToDelete(selectedContact);
                    setShowDeleteModal(true);
                  }}
                  className="gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Supprimer
                </Button>
                <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                  Fermer
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Avis Detail Modal */}
      <Dialog open={showAvisModal} onOpenChange={setShowAvisModal}>
        <DialogContent className="max-w-lg">
          {selectedAvis && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  Témoignage de {selectedAvis.nom}
                  {getAvisStatusBadge(selectedAvis.status)}
                </DialogTitle>
                <DialogDescription>
                  Reçu le {formatDate(selectedAvis.created_at)}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4 py-4">
                <div className="flex items-center gap-1">
                  {renderStars(selectedAvis.note)}
                  <span className="ml-2 text-sm text-muted-foreground">({selectedAvis.note}/5)</span>
                </div>
                
                {selectedAvis.situation && (
                  <div>
                    <p className="text-sm text-muted-foreground">Situation</p>
                    <p>{selectedAvis.situation}</p>
                  </div>
                )}

                <div>
                  <p className="text-sm text-muted-foreground mb-2">Témoignage</p>
                  <div className="bg-muted/30 p-4 rounded-lg">
                    <p className="whitespace-pre-wrap italic">"{selectedAvis.témoignage}"</p>
                  </div>
                </div>

                {selectedAvis.status === 'en_attente' && (
                  <div className="flex gap-2 pt-4">
                    <Button 
                      className="flex-1 gap-2 bg-green-600 hover:bg-green-700"
                      onClick={() => handleUpdateAvisStatus(selectedAvis.id, 'publie')}
                      disabled={updatingStatus}
                    >
                      <CheckCircle className="w-4 h-4" />
                      Publier
                    </Button>
                    <Button 
                      variant="destructive"
                      className="flex-1 gap-2"
                      onClick={() => handleUpdateAvisStatus(selectedAvis.id, 'rejete')}
                      disabled={updatingStatus}
                    >
                      <XCircle className="w-4 h-4" />
                      Rejeter
                    </Button>
                  </div>
                )}
              </div>

              <DialogFooter className="flex-col sm:flex-row gap-2">
                <Button
                  variant="destructive"
                  onClick={() => handleDeleteAvis(selectedAvis.id)}
                  className="gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Supprimer
                </Button>
                <Button variant="outline" onClick={() => setShowAvisModal(false)}>
                  Fermer
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmer la suppression</DialogTitle>
            <DialogDescription>
              Êtes-vous sûr de vouloir supprimer cette demande de contact ? 
              Cette action est irréversible.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteModal(false)}>
              Annuler
            </Button>
            <Button 
              variant="destructive" 
              onClick={handleDeleteContact}
              data-testid="confirm-delete-button"
            >
              Supprimer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <AdminHelpPanel onNavigateTab={(tab) => setActiveTab(tab)} onRestartTour={() => setShowTour(true)} />
      <AdminOnboardingTour isActive={showTour} onClose={() => setShowTour(false)} token={token} />
    </div>
  );
};
