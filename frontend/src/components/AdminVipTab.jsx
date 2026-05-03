import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { UserPlus, Copy, Check, Trash2, ToggleLeft, ToggleRight, ShieldCheck, Clock, Eye, Loader2 } from 'lucide-react';
import axios from 'axios';

const SITE_URL = 'https://strategie-expertise-sante.fr';

export const AdminVipTab = ({ axiosConfig }) => {
  const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
  const [guests, setGuests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', motif: '', expires_days: 90 });
  const [copiedId, setCopiedId] = useState(null);

  const fetchGuests = async () => {
    try {
      const res = await axios.get(`${API}/admin/vip-guests`, axiosConfig);
      setGuests(res.data);
    } catch { toast.error("Erreur chargement invités"); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchGuests(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.name || !form.email) { toast.error("Nom et email requis"); return; }
    setCreating(true);
    try {
      const res = await axios.post(`${API}/admin/vip-guests`, form, axiosConfig);
      const link = `${SITE_URL}/acces-invite?token=${res.data.token}`;
      toast.success(`Invité ${res.data.name} créé`);
      setForm({ name: '', email: '', motif: '', expires_days: 90 });
      setShowForm(false);
      fetchGuests();
      navigator.clipboard.writeText(link).then(() => toast.success("Lien copié dans le presse-papier"));
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur création");
    } finally { setCreating(false); }
  };

  const handleToggle = async (id) => {
    try {
      const res = await axios.put(`${API}/admin/vip-guests/${id}/toggle`, {}, axiosConfig);
      toast.success(res.data.active ? "Accès activé" : "Accès désactivé");
      fetchGuests();
    } catch { toast.error("Erreur"); }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Supprimer définitivement l'invité ${name} ?`)) return;
    try {
      await axios.delete(`${API}/admin/vip-guests/${id}`, axiosConfig);
      toast.success("Invité supprimé");
      fetchGuests();
    } catch { toast.error("Erreur suppression"); }
  };

  const copyLink = (token, id) => {
    const link = `${SITE_URL}/acces-invite?token=${token}`;
    navigator.clipboard.writeText(link);
    setCopiedId(id);
    toast.success("Lien copié");
    setTimeout(() => setCopiedId(null), 2000);
  };

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }) : '—';
  const isExpired = (d) => d ? new Date(d) < new Date() : false;

  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-accent" /></div>;

  return (
    <div className="space-y-6" data-testid="admin-vip-tab">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Invités VIP</h2>
          <p className="text-sm text-muted-foreground">{guests.length} invité{guests.length > 1 ? 's' : ''} enregistré{guests.length > 1 ? 's' : ''}</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)} size="sm" className="gap-2 rounded-lg" data-testid="vip-add-button">
          <UserPlus className="w-4 h-4" /> Nouvel invité
        </Button>
      </div>

      {showForm && (
        <Card className="border-accent/20" data-testid="vip-create-form">
          <CardContent className="p-4">
            <form onSubmit={handleCreate} className="grid sm:grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-xs">Nom complet *</Label>
                <Input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Dr. Dupont" required data-testid="vip-form-name" />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Email *</Label>
                <Input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} placeholder="docteur@email.fr" required data-testid="vip-form-email" />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Motif</Label>
                <Input value={form.motif} onChange={e => setForm({...form, motif: e.target.value})} placeholder="Partenaire médical" data-testid="vip-form-motif" />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Expiration (jours)</Label>
                <Input type="number" value={form.expires_days} onChange={e => setForm({...form, expires_days: parseInt(e.target.value) || 90})} min={1} max={365} data-testid="vip-form-expires" />
              </div>
              <div className="sm:col-span-2 flex gap-2 justify-end pt-2">
                <Button type="button" variant="outline" size="sm" onClick={() => setShowForm(false)}>Annuler</Button>
                <Button type="submit" size="sm" className="gap-2" disabled={creating} data-testid="vip-form-submit">
                  {creating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <UserPlus className="w-3.5 h-3.5" />}
                  Créer et copier le lien
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {guests.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground text-sm">Aucun invité VIP pour le moment.</div>
      ) : (
        <div className="space-y-3">
          {guests.map(g => (
            <Card key={g.id} className={`border-border ${!g.active ? 'opacity-60' : ''}`} data-testid={`vip-guest-${g.id}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold text-sm">{g.name}</span>
                      {g.active && !isExpired(g.expires_at) ? (
                        <Badge className="bg-emerald-100 text-emerald-700 text-[10px]">Actif</Badge>
                      ) : isExpired(g.expires_at) ? (
                        <Badge className="bg-red-100 text-red-700 text-[10px]">Expiré</Badge>
                      ) : (
                        <Badge className="bg-gray-100 text-gray-600 text-[10px]">Inactif</Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">{g.email}</p>
                    {g.motif && <p className="text-xs text-muted-foreground/70 mt-0.5">{g.motif}</p>}
                    <div className="flex items-center gap-4 mt-2 text-[10px] text-muted-foreground">
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> Créé : {formatDate(g.created_at)}</span>
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> Expire : {formatDate(g.expires_at)}</span>
                      {g.last_login && <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> Dernière visite : {formatDate(g.last_login)}</span>}
                      {g.login_count > 0 && <span>{g.login_count} connexion{g.login_count > 1 ? 's' : ''}</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => copyLink(g.token, g.id)} title="Copier le lien" data-testid={`vip-copy-${g.id}`}>
                      {copiedId === g.id ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => handleToggle(g.id)} title={g.active ? "Désactiver" : "Activer"} data-testid={`vip-toggle-${g.id}`}>
                      {g.active ? <ToggleRight className="w-4 h-4 text-emerald-600" /> : <ToggleLeft className="w-4 h-4 text-gray-400" />}
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-red-500 hover:text-red-700" onClick={() => handleDelete(g.id, g.name)} title="Supprimer" data-testid={`vip-delete-${g.id}`}>
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card className="border-dashed border-accent/30 bg-accent/5">
        <CardContent className="p-4">
          <h3 className="font-semibold text-sm flex items-center gap-2 mb-2"><ShieldCheck className="w-4 h-4 text-accent" /> Comment inviter un partenaire</h3>
          <ol className="text-xs text-muted-foreground space-y-1 list-decimal pl-4">
            <li>Cliquez "Nouvel invité" et renseignez le nom, email et motif</li>
            <li>Le lien d'invitation est automatiquement copié dans votre presse-papier</li>
            <li>Envoyez ce lien personnellement (WhatsApp, email, SMS)</li>
            <li>L'invité clique sur le lien, confirme son email, et accède au site</li>
            <li>Vous pouvez désactiver ou supprimer l'accès à tout moment</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
};
