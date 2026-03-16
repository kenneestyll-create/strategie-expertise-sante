import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { CalendarClock, Trash2, XCircle, Loader2, Send, FlaskConical, Users, Clock } from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STATUS_MAP = {
  scheduled: { label: 'Programmé', class: 'bg-amber-100 text-amber-700' },
  executing: { label: 'En cours...', class: 'bg-blue-100 text-blue-700' },
  sent: { label: 'Envoyé', class: 'bg-green-100 text-green-700' },
  cancelled: { label: 'Annulé', class: 'bg-gray-100 text-gray-500' },
  failed: { label: 'Échoué', class: 'bg-red-100 text-red-600' },
};

const formatDate = (iso) => {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
};

export const CampaignsDashboard = ({ token }) => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cancelId, setCancelId] = useState(null);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchCampaigns = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/admin/campaigns`, { headers });
      setCampaigns(res.data.campaigns || []);
    } catch {
      toast.error('Erreur chargement des campagnes');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchCampaigns(); }, [fetchCampaigns]);

  const cancelCampaign = async () => {
    if (!cancelId) return;
    try {
      await axios.put(`${API}/admin/campaigns/${cancelId}/cancel`, {}, { headers });
      toast.success('Campagne annulée');
      setCancelId(null);
      fetchCampaigns();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erreur');
    }
  };

  const deleteCampaign = async (id) => {
    try {
      await axios.delete(`${API}/admin/campaigns/${id}`, { headers });
      toast.success('Campagne supprimée');
      fetchCampaigns();
    } catch {
      toast.error('Erreur lors de la suppression');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8" data-testid="campaigns-loading">
        <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const scheduled = campaigns.filter(c => c.status === 'scheduled');
  const past = campaigns.filter(c => c.status !== 'scheduled');

  return (
    <div className="space-y-4" data-testid="campaigns-dashboard">
      <div className="flex items-center gap-2">
        <CalendarClock className="w-4 h-4 text-violet-500" />
        <h3 className="text-sm font-semibold">Campagnes programmées</h3>
        <Badge variant="outline" className="text-[10px]">{scheduled.length} en attente</Badge>
      </div>

      {campaigns.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center">
            <CalendarClock className="w-8 h-8 text-muted-foreground mx-auto mb-2 opacity-40" />
            <p className="text-sm text-muted-foreground">Aucune campagne programmée. Utilisez le bouton calendrier sur un template pour en créer une.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {campaigns.map(c => {
            const st = STATUS_MAP[c.status] || STATUS_MAP.scheduled;
            return (
              <div
                key={c.id}
                className="flex items-center justify-between p-3 rounded-lg border bg-card text-sm"
                data-testid={`campaign-row-${c.id}`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <Badge className={`text-[10px] ${st.class}`}>{st.label}</Badge>
                  <div className="min-w-0">
                    <p className="font-medium text-xs truncate">{c.template_label}</p>
                    <div className="flex items-center gap-2 text-[10px] text-muted-foreground mt-0.5">
                      <span className="flex items-center gap-0.5"><Clock className="w-3 h-3" />{formatDate(c.scheduled_at)}</span>
                      <span className="flex items-center gap-0.5"><Users className="w-3 h-3" />{c.target === 'all_clients' ? 'Tous' : 'Inactifs'}</span>
                      {c.ab_test_id && <span className="flex items-center gap-0.5"><FlaskConical className="w-3 h-3" />A/B</span>}
                      {c.status === 'sent' && <span className="flex items-center gap-0.5"><Send className="w-3 h-3" />{c.sent_count}/{c.recipients_count}</span>}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  {c.status === 'scheduled' && (
                    <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={() => setCancelId(c.id)} data-testid={`cancel-campaign-${c.id}`} title="Annuler">
                      <XCircle className="w-3.5 h-3.5 text-orange-500" />
                    </Button>
                  )}
                  {(c.status === 'cancelled' || c.status === 'sent' || c.status === 'failed') && (
                    <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={() => deleteCampaign(c.id)} data-testid={`delete-campaign-${c.id}`} title="Supprimer">
                      <Trash2 className="w-3.5 h-3.5 text-red-400" />
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Cancel Confirmation */}
      <Dialog open={!!cancelId} onOpenChange={(o) => { if (!o) setCancelId(null); }}>
        <DialogContent data-testid="cancel-campaign-dialog">
          <DialogHeader>
            <DialogTitle>Annuler la campagne ?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">La campagne ne sera pas envoyée. Cette action est irréversible.</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCancelId(null)}>Non</Button>
            <Button variant="destructive" className="gap-1.5" onClick={cancelCampaign} data-testid="confirm-cancel-campaign-btn">
              <XCircle className="w-3.5 h-3.5" /> Annuler la campagne
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
