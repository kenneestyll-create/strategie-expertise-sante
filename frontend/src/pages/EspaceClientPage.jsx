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
  MessageSquare
} from 'lucide-react';
import axios from 'axios';

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
  const [form, setForm] = useState({ email: '', password: '', name: '', phone: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const endpoint = mode === 'login' ? '/client/login' : '/client/register';
      const payload = mode === 'login' ? { email: form.email, password: form.password } : form;
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
            <Button type="submit" className="w-full rounded-lg gap-2" disabled={loading} data-testid="client-submit-button">
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

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [casesRes, profileRes] = await Promise.all([
        axios.get(`${API}/client/cases`, { headers }),
        axios.get(`${API}/client/profile`, { headers })
      ]);
      setCases(casesRes.data);
      setProfile(profileRes.data);
    } catch (err) {
      if (err.response?.status === 401) { logout(); return; }
      toast.error("Erreur de chargement");
    } finally { setLoading(false); }
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
          <div>
            <p className="text-sm text-primary-foreground/60">Espace client</p>
            <p className="font-semibold">Bonjour, {clientName}</p>
          </div>
          <Button variant="ghost" size="sm" onClick={logout} className="text-primary-foreground hover:bg-primary-foreground/10 gap-2" data-testid="client-logout">
            <LogOut className="w-4 h-4" /> Déconnexion
          </Button>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>
        ) : (
          <>
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
