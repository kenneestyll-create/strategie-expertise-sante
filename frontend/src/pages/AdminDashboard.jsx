import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
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
  X
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { BarChart3 } from 'lucide-react';

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
        <KpiCard label="Analyses IA" value={kpis.total_analyses} sub={`${kpis.total_dossiers} dossiers express`} />
        <KpiCard label="Forum" value={kpis.total_forum_users} sub={`${kpis.total_chatbot_sessions} sessions chatbot`} />
      </div>

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
  const [premiumAnalyses, setPremiumAnalyses] = useState({ items: [], stats: { total: 0, en_attente: 0, en_cours: 0, termine: 0 } });
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

  const navigate = useNavigate();
  const { token, adminName, logout } = useAuth();

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    fetchData();
  }, []);

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
        axios.get(`${API}/admin/cas-anonymises`, axiosConfig).catch(() => ({ data: { items: [], total: 0 } })),
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
      traite: { variant: "outline", icon: CheckCircle, label: "Traité" }
    };
    const config = styles[status] || styles.nouveau;
    return (
      <Badge variant={config.variant} className="gap-1">
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
    
    return matchesSearch && matchesStatus;
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
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-foreground text-primary-foreground sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link to="/" className="flex items-center gap-2">
                <Heart className="w-6 h-6 text-accent" strokeWidth={1.5} />
                <span className="font-semibold" style={{ fontFamily: "'Playfair Display', serif" }}>
                  Stratégie & Expertise Santé
                </span>
              </Link>
              <span className="text-primary-foreground/50 hidden sm:inline">|</span>
              <span className="text-sm text-primary-foreground/70 hidden sm:inline">Administration</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm hidden sm:inline">Bonjour, {adminName}</span>
              <Link to="/">
                <Button variant="ghost" size="sm" className="text-primary-foreground hover:bg-primary-foreground/10" data-testid="admin-home-button">
                  <Home className="w-4 h-4" />
                </Button>
              </Link>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={handleLogout}
                className="text-primary-foreground hover:bg-primary-foreground/10 gap-2"
                data-testid="admin-logout-button"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Déconnexion</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full max-w-6xl" style={{gridTemplateColumns: 'repeat(10, 1fr)'}}>
            <TabsTrigger value="contacts" className="gap-1 text-xs sm:text-sm">
              <Users className="w-3 h-3 sm:w-4 sm:h-4" />
              Contacts
            </TabsTrigger>
            <TabsTrigger value="avis" className="gap-1 text-xs sm:text-sm">
              <MessageSquare className="w-3 h-3 sm:w-4 sm:h-4" />
              Avis
            </TabsTrigger>
            <TabsTrigger value="referrals" className="gap-1 text-xs sm:text-sm" data-testid="tab-referrals">
              <Gift className="w-3 h-3 sm:w-4 sm:h-4" />
              Parrainage
            </TabsTrigger>
            <TabsTrigger value="bookings" className="gap-1 text-xs sm:text-sm" data-testid="tab-bookings">
              <Calendar className="w-3 h-3 sm:w-4 sm:h-4" />
              RDV
            </TabsTrigger>
            <TabsTrigger value="clients" className="gap-1 text-xs sm:text-sm" data-testid="tab-clients">
              <FolderOpen className="w-3 h-3 sm:w-4 sm:h-4" />
              Clients
            </TabsTrigger>
            <TabsTrigger value="relance" className="gap-1 text-xs sm:text-sm" data-testid="tab-relance">
              <Send className="w-3 h-3 sm:w-4 sm:h-4" />
              Relance
            </TabsTrigger>
            <TabsTrigger value="alertes" className="gap-1 text-xs sm:text-sm relative" data-testid="tab-alertes">
              <Zap className="w-3 h-3 sm:w-4 sm:h-4" />
              Alertes
              {urgentAlerts.non_traite > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center">{urgentAlerts.non_traite}</span>
              )}
            </TabsTrigger>
            <TabsTrigger value="strategiia" className="gap-1 text-xs sm:text-sm" data-testid="tab-strategiia">
              <Brain className="w-3 h-3 sm:w-4 sm:h-4" />
              StratégiIA
            </TabsTrigger>
            <TabsTrigger value="premium" className="gap-1 text-xs sm:text-sm relative" data-testid="tab-premium">
              <Zap className="w-3 h-3 sm:w-4 sm:h-4 text-amber-500" />
              Premium
              {premiumAnalyses.stats.en_attente > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-amber-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center">{premiumAnalyses.stats.en_attente}</span>
              )}
            </TabsTrigger>
            <TabsTrigger value="analytics" className="gap-1 text-xs sm:text-sm" data-testid="tab-analytics">
              <BarChart3 className="w-3 h-3 sm:w-4 sm:h-4 text-emerald-600" />
              Analytique
            </TabsTrigger>
          </TabsList>

          {/* Contacts Tab */}
          <TabsContent value="contacts" className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
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
                    <p className="text-sm text-muted-foreground">Traités</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col sm:flex-row gap-4">
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
                    <SelectTrigger className="w-full sm:w-48" data-testid="status-filter">
                      <SelectValue placeholder="Filtrer par statut" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Tous les statuts</SelectItem>
                      <SelectItem value="nouveau">Nouveaux</SelectItem>
                      <SelectItem value="en_cours">En cours</SelectItem>
                      <SelectItem value="traite">Traités</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="outline" onClick={fetchData} className="gap-2" data-testid="refresh-button">
                    <RefreshCw className="w-4 h-4" />
                    Actualiser
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
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-semibold truncate">
                                {contact.prenom} {contact.nom}
                              </h3>
                              {getStatusBadge(contact.status)}
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
                              "{item.temoignage}"
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
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center">
                              <User className="w-5 h-5 text-accent" strokeWidth={1.5} />
                            </div>
                            <div>
                              <p className="font-semibold">{client.name}</p>
                              <p className="text-sm text-muted-foreground">{client.email}</p>
                            </div>
                          </div>
                          <Badge variant="secondary">{client.cases_count || 0} dossier(s)</Badge>
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
            <div className="grid grid-cols-3 gap-4">
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
                      <div key={i} className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/30">
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
                        <div className="flex items-center gap-2 ml-4">
                          {item.relance_sent ? (
                            <Badge className="bg-green-100 text-green-800 gap-1"><CheckCircle className="w-3 h-3" />Relancé</Badge>
                          ) : (
                            <Button
                              variant="outline"
                              size="sm"
                              className="gap-1"
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
                      <div key={alert.id} className={`p-4 rounded-lg border ${alert.traite ? 'bg-muted/30 border-border' : 'bg-red-50 border-red-200'}`} data-testid={`alert-item-${alert.id}`}>
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 space-y-1">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-semibold">{alert.nom}</span>
                              <Badge variant={alert.formule === '30min' ? 'destructive' : 'secondary'}>
                                {alert.formule === '30min' ? '30min — 80€' : '2h — 50€'}
                              </Badge>
                              {alert.traite ? (
                                <Badge variant="outline" className="text-green-600 border-green-300">Traité</Badge>
                              ) : (
                                <Badge variant="destructive">Nouveau</Badge>
                              )}
                            </div>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1"><Phone className="w-3 h-3" />{alert.telephone}</span>
                              {alert.email && <span className="flex items-center gap-1"><Mail className="w-3 h-3" />{alert.email}</span>}
                            </div>
                            {alert.message && <p className="text-sm mt-1">{alert.message}</p>}
                            <p className="text-xs text-muted-foreground">{new Date(alert.created_at).toLocaleString('fr-FR')}</p>
                          </div>
                          {!alert.traite && (
                            <Button
                              size="sm"
                              variant="outline"
                              className="gap-1 text-green-600 border-green-300 hover:bg-green-50"
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
                            const res = await axios.post(`${API}/admin/cas-anonymises/import`, { cases }, axiosConfig);
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
                      await axios.post(`${API}/admin/cas-anonymises`, newCas, axiosConfig);
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
                                try { await axios.delete(`${API}/admin/cas-anonymises/${c.id}`, axiosConfig); toast.success('Cas supprimé'); fetchData(); }
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
                          await axios.patch(`${API}/admin/cas-anonymises/${editCas.id}`, editCas, axiosConfig);
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
          </TabsContent>

          {/* Premium Analyses Tab */}
          <TabsContent value="premium" className="space-y-6" data-testid="premium-tab-content">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold">{premiumAnalyses.stats.total}</p><p className="text-xs text-muted-foreground">Total commandes</p></CardContent></Card>
              <Card className="border-amber-500/30"><CardContent className="p-4 text-center"><p className="text-2xl font-bold text-amber-500">{premiumAnalyses.stats.en_attente}</p><p className="text-xs text-muted-foreground">En attente</p></CardContent></Card>
              <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold text-blue-500">{premiumAnalyses.stats.en_cours}</p><p className="text-xs text-muted-foreground">En cours</p></CardContent></Card>
              <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold text-green-600">{premiumAnalyses.stats.termine}</p><p className="text-xs text-muted-foreground">Terminées</p></CardContent></Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Zap className="w-5 h-5 text-amber-500" />
                  Analyses Premium en attente
                </CardTitle>
              </CardHeader>
              <CardContent>
                {premiumAnalyses.items.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">Aucune analyse Premium pour le moment.</p>
                ) : (
                  <div className="space-y-3">
                    {premiumAnalyses.items.map(item => (
                      <div key={item.id} className={`p-4 rounded-xl border ${item.status === 'en_attente' ? 'border-amber-500/30 bg-amber-50/50' : item.status === 'en_cours' ? 'border-blue-500/30 bg-blue-50/50' : 'border-green-500/30 bg-green-50/50'}`} data-testid={`premium-item-${item.id}`}>
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <Badge variant={item.status === 'en_attente' ? 'warning' : item.status === 'en_cours' ? 'default' : 'success'} className={`text-[10px] ${item.status === 'en_attente' ? 'bg-amber-500/10 text-amber-600 border-amber-500/20' : item.status === 'en_cours' ? 'bg-blue-500/10 text-blue-600 border-blue-500/20' : 'bg-green-500/10 text-green-600 border-green-500/20'}`}>
                                {item.status === 'en_attente' ? 'En attente' : item.status === 'en_cours' ? 'En cours' : 'Terminée'}
                              </Badge>
                              <Badge variant="outline" className="text-[10px]">{item.type === 'strategiia' ? 'StrategiIA' : 'Dossier Express'}</Badge>
                              {item.premium_pdf && <Badge className="bg-accent/10 text-accent border-accent/20 text-[10px]">PDF Pro</Badge>}
                              <span className="text-xs text-muted-foreground">{item.amount}€</span>
                            </div>
                            <p className="font-medium text-sm mt-1.5">{item.email || item.name || 'Client'}</p>
                            {item.context && <p className="text-xs text-muted-foreground mt-0.5 truncate">{item.context}</p>}
                            <p className="text-xs text-muted-foreground mt-1">{new Date(item.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
                          </div>
                          <div className="flex gap-1.5 flex-shrink-0">
                            {item.status === 'en_attente' && (
                              <Button size="sm" variant="outline" className="text-xs h-7 gap-1 border-blue-500/30 text-blue-600 hover:bg-blue-50"
                                onClick={async () => {
                                  await axios.patch(`${API}/admin/premium-analyses/${item.id}`, { status: 'en_cours' }, axiosConfig);
                                  fetchData(); toast.success("Statut mis à jour");
                                }} data-testid={`premium-start-${item.id}`}>
                                <Eye className="w-3 h-3" /> Traiter
                              </Button>
                            )}
                            {item.status === 'en_cours' && (
                              <Button size="sm" variant="outline" className="text-xs h-7 gap-1 border-green-500/30 text-green-600 hover:bg-green-50"
                                onClick={async () => {
                                  await axios.patch(`${API}/admin/premium-analyses/${item.id}`, { status: 'termine' }, axiosConfig);
                                  fetchData(); toast.success("Analyse marquée comme terminée");
                                }} data-testid={`premium-done-${item.id}`}>
                                <CheckCircle className="w-3 h-3" /> Terminé
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
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
                      Traité
                    </Button>
                  </div>
                </div>
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
                    <p className="whitespace-pre-wrap italic">"{selectedAvis.temoignage}"</p>
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
    </div>
  );
};
