import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import {
  User,
  FolderOpen,
  Clock,
  CheckCircle,
  AlertCircle,
  LogOut,
  Loader2,
  ArrowRight,
  FileText,
  Calendar,
  MessageSquare,
  Bell,
  BellDot,
  X,
  Settings,
  Mail,
  Smartphone,
  Archive,
  BellRing,
  Send,
  TrendingUp,
  Shield
} from 'lucide-react';
import axios from 'axios';
import { DataConsentBox } from '@/components/DataConsentBox';
import { ClientDocuments } from '@/components/ClientDocuments';
import { ProgressDashboard } from '@/components/ProgressDashboard';
import { DossierAnalysis } from '@/components/DossierAnalysis';
import { usePushNotifications } from '@/hooks/usePushNotifications';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const useClientAuth = () => {
  const [token, setToken] = useState(localStorage.getItem('client_token'));
  const [clientName, setClientName] = useState(localStorage.getItem('client_name'));
  const [clientId, setClientId] = useState(localStorage.getItem('client_id'));

  const login = (data) => {
    localStorage.setItem('client_token', data.access_token);
    localStorage.setItem('client_name', data.client_name);
    localStorage.setItem('client_id', data.client_id);
    setToken(data.access_token);
    setClientName(data.client_name);
    setClientId(data.client_id);
  };

  const logout = () => {
    localStorage.removeItem('client_token');
    localStorage.removeItem('client_name');
    localStorage.removeItem('client_id');
    setToken(null);
    setClientName(null);
    setClientId(null);
  };

  return { token, clientName, clientId, login, logout, isLoggedIn: !!token };
};

const LoginForm = ({ onLogin }) => {
  const [mode, setMode] = useState('login');
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ email: '', password: '', name: '', phone: '', notifications_email: true, notifications_push: true });
  const [consent, setConsent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const endpoint = mode === 'login' ? '/client/login' : '/client/register';
      const payload = mode === 'login' 
        ? { email: form.email, password: form.password } 
        : { email: form.email, password: form.password, name: form.name, phone: form.phone, notifications_email: form.notifications_email, notifications_push: form.notifications_push };
      const res = await axios.post(`${API}${endpoint}`, payload);
      onLogin(res.data);
      toast.success(mode === 'login' ? 'Connexion réussie' : 'Compte créé avec succès');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erreur de connexion');
    } finally { setLoading(false); }
  };

  return (
    <main className="page-transition pt-20 min-h-screen flex items-center justify-center px-4">
      <Card className="w-full max-w-md border-border" data-testid="client-auth-card">
        <CardHeader className="text-center">
          <div className="w-16 h-16 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <User className="w-8 h-8 text-accent" strokeWidth={1.5} />
          </div>
          <CardTitle className="text-2xl">Espace client</CardTitle>
          <CardDescription>
            {mode === 'login' ? 'Connectez-vous pour suivre vos dossiers' : 'Créez votre compte client'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="client-name">Nom complet *</Label>
                  <Input id="client-name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Prénom Nom" required data-testid="client-name-input" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="client-phone">Téléphone</Label>
                  <Input id="client-phone" value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))} placeholder="06 00 00 00 00" data-testid="client-phone-input" />
                </div>
              </>
            )}
            <div className="space-y-2">
              <Label htmlFor="client-email">Email *</Label>
              <Input id="client-email" type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} placeholder="votre@email.fr" required data-testid="client-email-input" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="client-password">Mot de passe *</Label>
              <Input id="client-password" type="password" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} placeholder="Votre mot de passe" required data-testid="client-password-input" />
            </div>
            {mode === 'register' && (
              <>
                <div className="p-3 rounded-lg bg-accent/5 border border-accent/20 space-y-2" data-testid="notification-preferences">
                  <p className="text-sm font-medium flex items-center gap-2"><Bell className="w-4 h-4 text-accent" />Préférences de notifications</p>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={form.notifications_email} onChange={e => setForm(f => ({ ...f, notifications_email: e.target.checked }))} className="accent-accent" data-testid="notif-email-checkbox" />
                    <span className="text-sm">Recevoir les notifications par email</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={form.notifications_push} onChange={e => setForm(f => ({ ...f, notifications_push: e.target.checked }))} className="accent-accent" data-testid="notif-push-checkbox" />
                    <span className="text-sm">Recevoir les notifications du navigateur</span>
                  </label>
                  <p className="text-xs text-muted-foreground">Vous serez notifié des mises à jour de vos dossiers, paiements et rapports.</p>
                </div>
                <DataConsentBox checked={consent} onChange={setConsent} />
              </>
            )}
            <Button type="submit" className="w-full rounded-lg gap-2" disabled={loading || (mode === 'register' && !consent)} data-testid="client-submit-button">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              {mode === 'login' ? 'Se connecter' : 'Créer mon compte'}
            </Button>
          </form>
          <div className="text-center mt-4">
            <button
              onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
              className="text-sm text-accent hover:underline"
              data-testid="toggle-auth-mode"
            >
              {mode === 'login' ? "Pas encore de compte ? S'inscrire" : 'Déjà un compte ? Se connecter'}
            </button>
          </div>
        </CardContent>
      </Card>
    </main>
  );
};

const ClientDashboard = ({ token, clientName, logout }) => {
  const [cases, setCases] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifs, setShowNotifs] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [notifSettings, setNotifSettings] = useState({ notifications_email: true, notifications_push: true });
  const [savingSettings, setSavingSettings] = useState(false);
  const [activeTab, setActiveTab] = useState('dossiers');
  const [navScore, setNavScore] = useState(null);
  const [scoreDelta, setScoreDelta] = useState(null);
  const push = usePushNotifications(token);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchNavScore = async () => {
    try {
      const res = await axios.get(`${API}/client/dossier-analysis`, { headers });
      const newScore = res.data.score;
      const prev = sessionStorage.getItem('dossier_prev_score');
      if (prev !== null && newScore > parseInt(prev, 10)) {
        setScoreDelta(newScore - parseInt(prev, 10));
        setTimeout(() => setScoreDelta(null), 5000);
      }
      sessionStorage.setItem('dossier_prev_score', String(newScore));
      setNavScore(res.data);
    } catch {}
  };

  useEffect(() => { fetchData(); fetchNavScore(); }, []);

  // Listen for dossier refresh events (from document upload, etc.)
  useEffect(() => {
    const handleRefresh = () => { fetchNavScore(); };
    window.addEventListener('dossier:refresh', handleRefresh);
    return () => window.removeEventListener('dossier:refresh', handleRefresh);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [casesRes, profileRes, notifsRes, settingsRes] = await Promise.all([
        axios.get(`${API}/client/cases`, { headers }),
        axios.get(`${API}/client/profile`, { headers }),
        axios.get(`${API}/client/notifications`, { headers }).catch(() => ({ data: { notifications: [], unread_count: 0 } })),
        axios.get(`${API}/client/settings/notifications`, { headers }).catch(() => ({ data: { notifications_email: true, notifications_push: true } }))
      ]);
      setCases(casesRes.data);
      setProfile(profileRes.data);
      setNotifications(notifsRes.data.notifications);
      setUnreadCount(notifsRes.data.unread_count);
      setNotifSettings(settingsRes.data);
    } catch (err) {
      if (err.response?.status === 401) { logout(); return; }
      toast.error("Erreur de chargement");
    } finally { setLoading(false); }
  };

  const markAllRead = async () => {
    try {
      await axios.patch(`${API}/client/notifications/read-all`, {}, { headers });
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch {}
  };

  const markRead = async (notifId) => {
    try {
      await axios.patch(`${API}/client/notifications/${notifId}/read`, {}, { headers });
      setNotifications(prev => prev.map(n => n.id === notifId ? { ...n, read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch {}
  };

  const saveNotifSettings = async (key, value) => {
    const updated = { ...notifSettings, [key]: value };
    setNotifSettings(updated);
    setSavingSettings(true);
    try {
      await axios.patch(`${API}/client/settings/notifications`, { [key]: value }, { headers });
      toast.success('Préférences mises à jour');
    } catch {
      toast.error('Erreur lors de la mise à jour');
      setNotifSettings(notifSettings);
    } finally { setSavingSettings(false); }
  };

  const getStatusConfig = (status) => {
    const map = {
      en_cours: { label: 'En cours', icon: Clock, color: 'bg-blue-500 text-white' },
      en_attente: { label: 'En attente', icon: AlertCircle, color: 'bg-amber-500 text-white' },
      termine: { label: 'Terminé', icon: CheckCircle, color: 'bg-green-500 text-white' }
    };
    return map[status] || map.en_cours;
  };

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) : '';

  return (
    <main className="page-transition pt-20 min-h-screen bg-background">
      {/* Header Bar */}
      <div className="bg-foreground text-primary-foreground py-4 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4 min-w-0">
            <div className="min-w-0">
              <p className="text-sm text-primary-foreground/60">Espace client</p>
              <p className="font-semibold">Bonjour, {clientName}</p>
            </div>

            {/* Navbar Score Indicator — only for Dossier Express IA clients */}
            {navScore && navScore.has_dossier_express && (
              <button
                onClick={() => {
                  setActiveTab('dossiers');
                  setTimeout(() => {
                    const el = document.querySelector('[data-testid="dossier-score-card"]');
                    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  }, 100);
                }}
                className="hidden sm:flex items-center gap-2.5 px-3 py-1.5 rounded-full border border-primary-foreground/15 bg-primary-foreground/5 hover:bg-primary-foreground/10 transition-all cursor-pointer group"
                data-testid="navbar-score-indicator"
              >
                {/* Mini ring */}
                <div className="relative w-8 h-8 flex-shrink-0">
                  <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="15" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="3" />
                    <circle
                      cx="18" cy="18" r="15" fill="none"
                      stroke={navScore.score < 50 ? '#ef4444' : navScore.score < 80 ? '#eab308' : '#22c55e'}
                      strokeWidth="3" strokeLinecap="round"
                      strokeDasharray={2 * Math.PI * 15}
                      strokeDashoffset={2 * Math.PI * 15 - (navScore.score / 100) * 2 * Math.PI * 15}
                      className="transition-all duration-700"
                    />
                  </svg>
                  <span className="absolute inset-0 flex items-center justify-center text-[9px] font-bold text-primary-foreground">
                    {navScore.score}
                  </span>
                </div>
                <div className="flex flex-col items-start">
                  <span className="text-[11px] font-medium text-primary-foreground/80 leading-tight">Dossier</span>
                  <span className={`text-[10px] font-semibold leading-tight ${navScore.score < 50 ? 'text-red-400' : navScore.score < 80 ? 'text-yellow-400' : 'text-green-400'}`}>
                    {navScore.score < 50 ? 'Fragile' : navScore.score < 80 ? 'En progression' : 'Solide'}
                  </span>
                </div>
                {navScore.human_reviewed && (
                  <span className="flex items-center gap-0.5 text-[9px] font-bold text-amber-400" title="Relu par un expert" data-testid="navbar-expert-badge">
                    <CheckCircle className="w-3 h-3" />Expert
                  </span>
                )}
                {/* Delta indicator */}
                {scoreDelta && scoreDelta > 0 && (
                  <span className="flex items-center gap-0.5 text-[10px] font-bold text-green-400 animate-bounce" data-testid="navbar-score-delta">
                    <TrendingUp className="w-3 h-3" />+{scoreDelta}%
                  </span>
                )}
              </button>
            )}
            {/* Mobile score - compact — only for Dossier Express IA */}
            {navScore && navScore.has_dossier_express && (
              <button
                onClick={() => {
                  setActiveTab('dossiers');
                  setTimeout(() => {
                    const el = document.querySelector('[data-testid="dossier-score-card"]');
                    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  }, 100);
                }}
                className="sm:hidden flex items-center gap-1.5 px-2 py-1 rounded-full border border-primary-foreground/15 bg-primary-foreground/5"
                data-testid="navbar-score-mobile"
              >
                <Shield className={`w-3.5 h-3.5 ${navScore.score < 50 ? 'text-red-400' : navScore.score < 80 ? 'text-yellow-400' : 'text-green-400'}`} />
                <span className={`text-xs font-bold ${navScore.score < 50 ? 'text-red-400' : navScore.score < 80 ? 'text-yellow-400' : 'text-green-400'}`}>
                  {navScore.score}%
                </span>
                {scoreDelta && scoreDelta > 0 && (
                  <span className="text-[9px] font-bold text-green-400">+{scoreDelta}</span>
                )}
              </button>
            )}
          </div>
          <div className="flex items-center gap-2">
            {/* Notifications Bell */}
            <div className="relative">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => { setShowNotifs(!showNotifs); if (!showNotifs && unreadCount > 0) markAllRead(); }}
                className="text-primary-foreground hover:bg-primary-foreground/10 relative"
                data-testid="notifications-bell"
              >
                {unreadCount > 0 ? <BellDot className="w-5 h-5" /> : <Bell className="w-5 h-5" />}
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-accent text-accent-foreground text-xs font-bold rounded-full flex items-center justify-center" data-testid="notif-badge">
                    {unreadCount}
                  </span>
                )}
              </Button>

              {/* Notification Panel */}
              {showNotifs && (
                <div className="absolute right-0 top-12 w-80 sm:w-96 bg-background text-foreground border border-border rounded-xl shadow-2xl z-50 overflow-hidden" data-testid="notifications-panel">
                  <div className="flex items-center justify-between p-4 border-b border-border">
                    <h3 className="font-semibold text-sm">Notifications</h3>
                    <Button variant="ghost" size="icon" onClick={() => setShowNotifs(false)} className="w-6 h-6">
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="p-6 text-center text-muted-foreground text-sm">
                        <Bell className="w-8 h-8 mx-auto mb-2 opacity-30" />
                        Aucune notification
                      </div>
                    ) : (
                      notifications.map((n) => (
                        <div
                          key={n.id}
                          className={`p-3 border-b border-border/50 last:border-0 cursor-pointer hover:bg-muted/50 transition-colors ${!n.read ? 'bg-accent/5' : ''}`}
                          onClick={() => { markRead(n.id); if (n.case_id) { setShowNotifs(false); const c = cases.find(x => x.id === n.case_id); if (c) setSelectedCase(c); }}}
                          data-testid={`notif-item-${n.id}`}
                        >
                          <div className="flex items-start gap-3">
                            <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${!n.read ? 'bg-accent' : 'bg-transparent'}`} />
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium">{n.title}</p>
                              <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{n.message}</p>
                              <p className="text-xs text-muted-foreground/60 mt-1">{n.created_at ? formatDate(n.created_at) : ''}</p>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
            <Button variant="ghost" size="icon" onClick={() => setShowSettings(!showSettings)} className="text-primary-foreground hover:bg-primary-foreground/10" data-testid="client-settings-btn">
              <Settings className="w-5 h-5" />
            </Button>
            <Button variant="ghost" size="sm" onClick={logout} className="text-primary-foreground hover:bg-primary-foreground/10 gap-2" data-testid="client-logout">
              <LogOut className="w-4 h-4" /> Déconnexion
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>
        ) : (
          <>
            {/* Notification Settings Panel */}
            {showSettings && (
              <Card className="mb-6 border-accent/20" data-testid="notification-settings-panel">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base flex items-center gap-2"><Settings className="w-5 h-5 text-accent" />Préférences de notifications</CardTitle>
                    <Button variant="ghost" size="icon" onClick={() => setShowSettings(false)} className="w-8 h-8"><X className="w-4 h-4" /></Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <label className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-muted/30 cursor-pointer transition-colors" data-testid="settings-email-toggle">
                    <div className="flex items-center gap-3">
                      <Mail className="w-5 h-5 text-accent" />
                      <div>
                        <p className="text-sm font-medium">Notifications par email</p>
                        <p className="text-xs text-muted-foreground">Recevez un email pour chaque mise à jour de vos dossiers</p>
                      </div>
                    </div>
                    <input 
                      type="checkbox" 
                      checked={notifSettings.notifications_email} 
                      onChange={e => saveNotifSettings('notifications_email', e.target.checked)} 
                      disabled={savingSettings}
                      className="w-5 h-5 accent-accent" 
                    />
                  </label>
                  <label className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-muted/30 cursor-pointer transition-colors" data-testid="settings-push-toggle">
                    <div className="flex items-center gap-3">
                      <Smartphone className="w-5 h-5 text-accent" />
                      <div>
                        <p className="text-sm font-medium">Notifications du navigateur</p>
                        <p className="text-xs text-muted-foreground">Recevez des alertes instantanées dans votre navigateur</p>
                      </div>
                    </div>
                    <input 
                      type="checkbox" 
                      checked={notifSettings.notifications_push} 
                      onChange={e => saveNotifSettings('notifications_push', e.target.checked)} 
                      disabled={savingSettings}
                      className="w-5 h-5 accent-accent" 
                    />
                  </label>
                  {/* Push Notification Subscription */}
                  {push.isSupported && (
                    <div className="p-3 rounded-lg border border-accent/20 bg-accent/5 space-y-3" data-testid="push-subscription-panel">
                      <div className="flex items-center gap-3">
                        <BellRing className="w-5 h-5 text-accent" />
                        <div className="flex-1">
                          <p className="text-sm font-medium">Notifications push</p>
                          <p className="text-xs text-muted-foreground">
                            {push.isSubscribed 
                              ? 'Actif — vous recevrez des alertes en temps réel' 
                              : push.permission === 'denied' 
                                ? 'Bloqué — autorisez les notifications dans les paramètres du navigateur' 
                                : 'Activez pour recevoir des alertes même quand la page est fermée'}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {!push.isSubscribed ? (
                          <Button 
                            size="sm" 
                            onClick={async () => { 
                              const ok = await push.subscribe(); 
                              if (ok) toast.success('Notifications push activées'); 
                              else if (push.permission === 'denied') toast.error('Notifications bloquées par le navigateur');
                            }}
                            disabled={push.loading || push.permission === 'denied'}
                            className="gap-2"
                            data-testid="push-subscribe-btn"
                          >
                            {push.loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Bell className="w-3 h-3" />}
                            Activer les push
                          </Button>
                        ) : (
                          <>
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={async () => { await push.testPush(); toast.success('Notification test envoyée'); }}
                              className="gap-2"
                              data-testid="push-test-btn"
                            >
                              <Send className="w-3 h-3" /> Tester
                            </Button>
                            <Button 
                              size="sm" 
                              variant="ghost"
                              onClick={async () => { await push.unsubscribe(); toast.success('Notifications push désactivées'); }}
                              disabled={push.loading}
                              className="gap-2 text-muted-foreground"
                              data-testid="push-unsubscribe-btn"
                            >
                              Désactiver
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground">
                    Vous serez notifié pour : analyse premium prête, paiement confirmé, dossier en cours, rapport disponible.
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Tabs: Dossiers / Documents */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full max-w-xs grid-cols-2 mb-6">
                <TabsTrigger value="dossiers" className="gap-1.5 text-xs" data-testid="tab-dossiers">
                  <FolderOpen className="w-3.5 h-3.5" /> Mes Dossiers
                </TabsTrigger>
                <TabsTrigger value="documents" className="gap-1.5 text-xs" data-testid="tab-documents">
                  <Archive className="w-3.5 h-3.5" /> Mes Documents
                </TabsTrigger>
              </TabsList>

              <TabsContent value="dossiers">
                {/* Progress Dashboard */}
                <ProgressDashboard token={token} />

                {/* Dossier Analysis - StratégiIA Phase 1 */}
                <DossierAnalysis token={token} />

                {/* Stats */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <FolderOpen className="w-8 h-8 text-accent" strokeWidth={1.5} />
                  <div><p className="text-2xl font-bold">{cases.length}</p><p className="text-xs text-muted-foreground">Dossiers</p></div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <Clock className="w-8 h-8 text-blue-500" strokeWidth={1.5} />
                  <div><p className="text-2xl font-bold">{cases.filter(c => c.status === 'en_cours').length}</p><p className="text-xs text-muted-foreground">En cours</p></div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <AlertCircle className="w-8 h-8 text-amber-500" strokeWidth={1.5} />
                  <div><p className="text-2xl font-bold">{cases.filter(c => c.status === 'en_attente').length}</p><p className="text-xs text-muted-foreground">En attente</p></div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <CheckCircle className="w-8 h-8 text-green-500" strokeWidth={1.5} />
                  <div><p className="text-2xl font-bold">{cases.filter(c => c.status === 'termine').length}</p><p className="text-xs text-muted-foreground">Terminés</p></div>
                </CardContent>
              </Card>
            </div>

            {/* Cases List */}
            {cases.length === 0 ? (
              <Card className="border-border">
                <CardContent className="p-12 text-center">
                  <FolderOpen className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" strokeWidth={1} />
                  <h3 className="font-semibold text-lg mb-2">Aucun dossier pour le moment</h3>
                  <p className="text-sm text-muted-foreground mb-6">
                    Votre espace est prêt. Vos dossiers apparaîtront ici dès qu'ils seront créés par votre accompagnant.
                  </p>
                  <Link to="/contact">
                    <Button className="rounded-lg gap-2"><MessageSquare className="w-4 h-4" />Prendre contact</Button>
                  </Link>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4" data-testid="client-cases-list">
                {selectedCase ? (
                  /* Case Detail */
                  <div data-testid="case-detail">
                    <Button variant="ghost" onClick={() => setSelectedCase(null)} className="mb-4 gap-2 text-sm">
                      Retour aux dossiers
                    </Button>
                    <Card className="border-border">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle>{selectedCase.title}</CardTitle>
                            <CardDescription className="mt-1">{selectedCase.description}</CardDescription>
                          </div>
                          {(() => { const s = getStatusConfig(selectedCase.status); return (
                            <Badge className={`${s.color} gap-1`}><s.icon className="w-3 h-3" />{s.label}</Badge>
                          ); })()}
                        </div>
                      </CardHeader>
                      <CardContent>
                        {selectedCase.notes && (
                          <div className="bg-muted/30 p-4 rounded-lg mb-6">
                            <p className="text-sm font-medium mb-1">Notes</p>
                            <p className="text-sm text-muted-foreground">{selectedCase.notes}</p>
                          </div>
                        )}
                        <h4 className="font-semibold mb-3 flex items-center gap-2"><Calendar className="w-4 h-4 text-accent" />Historique du suivi</h4>
                        {selectedCase.updates && selectedCase.updates.length > 0 ? (
                          <div className="space-y-3 border-l-2 border-accent/20 pl-4 ml-2">
                            {selectedCase.updates.map((u, i) => (
                              <div key={i} className="relative">
                                <div className="absolute -left-[22px] top-1 w-3 h-3 bg-accent rounded-full border-2 border-background" />
                                <p className="text-xs text-muted-foreground">{formatDate(u.date)} — {u.author}</p>
                                <p className="text-sm mt-1">{u.message}</p>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-muted-foreground">Aucune mise à jour pour le moment.</p>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  /* Cases Grid */
                  cases.map(c => {
                    const s = getStatusConfig(c.status);
                    return (
                      <Card key={c.id} className="border-border cursor-pointer hover:shadow-md transition-shadow" onClick={() => setSelectedCase(c)} data-testid={`case-card-${c.id}`}>
                        <CardContent className="p-5 flex items-center justify-between">
                          <div className="flex items-center gap-4 flex-1 min-w-0">
                            <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
                              <FileText className="w-5 h-5 text-accent" strokeWidth={1.5} />
                            </div>
                            <div className="min-w-0">
                              <p className="font-semibold truncate">{c.title}</p>
                              <p className="text-sm text-muted-foreground truncate">{c.description}</p>
                              <p className="text-xs text-muted-foreground mt-1">{formatDate(c.created_at)}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-3 ml-4">
                            <Badge className={`${s.color} gap-1`}><s.icon className="w-3 h-3" />{s.label}</Badge>
                            <ArrowRight className="w-4 h-4 text-muted-foreground" />
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })
                )}
              </div>
            )}
              </TabsContent>

              <TabsContent value="documents" data-testid="documents-tab-content">
                <ClientDocuments token={token} onDocumentsChange={() => { window.dispatchEvent(new Event('dossier:refresh')); }} />
              </TabsContent>
            </Tabs>
          </>
        )}
      </div>
    </main>
  );
};

export const EspaceClientPage = () => {
  const auth = useClientAuth();

  if (!auth.isLoggedIn) {
    return <LoginForm onLogin={auth.login} />;
  }

  return <ClientDashboard token={auth.token} clientName={auth.clientName} logout={auth.logout} />;
};
