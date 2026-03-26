import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import {
  Zap, Eye, Bell, Send, CheckCircle, PenTool, Loader2, Brain, FileSearch, Clock
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STATUS_CONFIG = {
  en_attente: { label: 'En attente', color: 'bg-amber-500/10 text-amber-600 border-amber-500/20', border: 'border-amber-500/30 bg-amber-50/50' },
  en_cours: { label: 'En cours', color: 'bg-blue-500/10 text-blue-600 border-blue-500/20', border: 'border-blue-500/30 bg-blue-50/50' },
  valide: { label: 'Validé — prêt', color: 'bg-green-500/10 text-green-600 border-green-500/20', border: 'border-green-500/30 bg-green-50/50' },
  envoye: { label: 'Envoyé', color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20', border: 'border-emerald-500/30 bg-emerald-50/50' },
  termine: { label: 'Terminé', color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20', border: 'border-emerald-500/30 bg-emerald-50/50' },
};

export const AdminPremiumReview = ({ items, stats, productType, productLabel, icon: Icon, accentColor, axiosConfig, onRefresh, onViewDossierAnalysis }) => {
  const [reviewDialog, setReviewDialog] = useState(null);
  const [loadingContent, setLoadingContent] = useState(false);

  const filteredItems = items.filter(i => i.type === productType);
  const filteredStats = {
    total: filteredItems.length,
    en_attente: filteredItems.filter(i => i.status === 'en_attente').length,
    en_cours: filteredItems.filter(i => i.status === 'en_cours').length,
    valide: filteredItems.filter(i => i.status === 'valide').length,
    envoye: filteredItems.filter(i => i.status === 'envoye' || i.status === 'termine').length,
  };

  const openReviewDialog = async (item) => {
    setReviewDialog({ ...item, _loading: true });
    setLoadingContent(true);
    try {
      const res = await axios.get(`${API}/admin/premium-analyses/${item.id}/full-content`, axiosConfig);
      setReviewDialog(prev => ({
        ...prev,
        _loading: false,
        reviewed_analysis: prev?.reviewed_analysis || res.data.full_text || '',
        source_data: res.data.source_data || {},
        _original_text: res.data.full_text || ''
      }));
    } catch {
      setReviewDialog(prev => ({ ...prev, _loading: false }));
      toast.error("Impossible de charger le contenu complet");
    } finally {
      setLoadingContent(false);
    }
  };

  if (filteredItems.length === 0 && filteredStats.total === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          <Icon className={`w-8 h-8 mx-auto mb-3 ${accentColor}`} />
          <p>Aucune demande {productLabel} pour le moment.</p>
          <p className="text-xs mt-1">Les demandes premium apparaîtront ici automatiquement.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold">{filteredStats.total}</p><p className="text-xs text-muted-foreground">Total</p></CardContent></Card>
        <Card className="border-amber-500/30"><CardContent className="p-4 text-center"><p className="text-2xl font-bold text-amber-500">{filteredStats.en_attente}</p><p className="text-xs text-muted-foreground">En attente</p></CardContent></Card>
        <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold text-blue-500">{filteredStats.en_cours}</p><p className="text-xs text-muted-foreground">En cours</p></CardContent></Card>
        <Card className="border-green-500/30"><CardContent className="p-4 text-center"><p className="text-2xl font-bold text-green-600">{filteredStats.valide}</p><p className="text-xs text-muted-foreground">Validé</p></CardContent></Card>
        <Card><CardContent className="p-4 text-center"><p className="text-2xl font-bold text-emerald-600">{filteredStats.envoye}</p><p className="text-xs text-muted-foreground">Envoyé</p></CardContent></Card>
      </div>

      {/* Items list */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg" data-testid={`premium-${productType}-title`}>
            <Icon className={`w-5 h-5 ${accentColor}`} />
            Relecture expert — {productLabel}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {filteredItems.map(item => {
              const sc = STATUS_CONFIG[item.status] || STATUS_CONFIG.en_attente;
              return (
                <div key={item.id} className={`p-4 rounded-xl border ${sc.border}`} data-testid={`premium-item-${item.id}`}>
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge className={`text-[10px] ${sc.color}`}>{sc.label}</Badge>
                        <Badge variant="outline" className="text-[10px]">{productLabel}</Badge>
                        {item.premium_pdf && <Badge className="bg-accent/10 text-accent border-accent/20 text-[10px]">PDF Pro</Badge>}
                        {item.relecture_expert_required && <Badge className="bg-red-500/10 text-red-600 border-red-500/20 text-[10px] font-bold">Relecture Expert</Badge>}
                        {item.admin_test && <Badge className="bg-zinc-500/10 text-zinc-500 border-zinc-500/20 text-[10px]">Test Admin</Badge>}
                        <span className="text-xs text-muted-foreground">{item.amount}€</span>
                      </div>
                      <p className="font-medium text-sm mt-1.5">{item.email || item.name || 'Client'}</p>
                      {item.context && <p className="text-xs text-muted-foreground mt-0.5 truncate">{item.context}</p>}
                      {item.name && !item.context && <p className="text-xs text-muted-foreground mt-0.5">Client : {item.name}</p>}
                      <p className="text-xs text-muted-foreground mt-1">{new Date(item.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
                      {item.sent_at && <p className="text-[10px] text-green-600 mt-0.5">Envoyé le {new Date(item.sent_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</p>}
                    </div>
                    <div className="flex gap-1.5 flex-shrink-0 flex-wrap">
                      {/* Step 1: En attente → En cours */}
                      {item.status === 'en_attente' && (
                        <Button size="sm" variant="outline" className="text-xs h-7 gap-1 border-blue-500/30 text-blue-600 hover:bg-blue-50"
                          onClick={async () => {
                            try {
                              await axios.patch(`${API}/admin/premium-analyses/${item.id}`, { status: 'en_cours' }, axiosConfig);
                              onRefresh(); toast.success("Dossier pris en charge");
                            } catch { toast.error("Erreur de mise à jour"); }
                          }} data-testid={`premium-start-${item.id}`}>
                          <Eye className="w-3 h-3" /> Traiter
                        </Button>
                      )}
                      {/* Step 2: En cours → open review dialog */}
                      {item.status === 'en_cours' && (
                        <Button size="sm" variant="outline" className="text-xs h-7 gap-1 border-green-500/30 text-green-600 hover:bg-green-50"
                          onClick={() => openReviewDialog(item)} data-testid={`premium-review-${item.id}`}>
                          <PenTool className="w-3 h-3" /> Relire / Valider
                        </Button>
                      )}
                      {/* Step 3: Validé → Envoyer */}
                      {item.status === 'valide' && (
                        <Button size="sm" className="text-xs h-7 gap-1 bg-emerald-600 hover:bg-emerald-500 text-white"
                          onClick={async () => {
                            try {
                              const res = await axios.post(`${API}/admin/premium-analyses/${item.id}/send-reviewed`, {
                                reviewed_analysis: item.reviewed_analysis || ''
                              }, axiosConfig);
                              toast.success(res.data.email_sent ? `Document envoyé à ${res.data.email}` : 'Document validé (email non configuré)');
                              onRefresh();
                            } catch { toast.error("Erreur lors de l'envoi"); }
                          }} data-testid={`premium-send-${item.id}`}>
                          <Send className="w-3 h-3" /> Envoyer au client
                        </Button>
                      )}
                      {/* Consulter (always available when reviewed) */}
                      {item.reviewed_analysis && (
                        <Button size="sm" variant="outline" className="text-xs h-7 gap-1"
                          onClick={() => openReviewDialog(item)}>
                          <Eye className="w-3 h-3" /> Consulter
                        </Button>
                      )}
                      {/* Notify */}
                      <Button size="sm" variant="outline" className={`text-xs h-7 gap-1 ${item.client_notified ? 'border-green-500/30 text-green-600' : 'border-accent/30 text-accent hover:bg-accent/5'}`}
                        onClick={async () => {
                          const notifType = item.status === 'envoye' ? 'report_ready' : item.status === 'valide' ? 'analyse_premium_ready' : item.status === 'en_cours' ? 'dossier_in_progress' : 'payment_confirmed';
                          try {
                            const res = await axios.post(`${API}/admin/premium-analyses/${item.id}/notify`, { type: notifType }, axiosConfig);
                            toast.success(res.data.client_found ? 'Notification envoyée' : 'Client non inscrit — notification enregistrée');
                            onRefresh();
                          } catch { toast.error("Erreur d'envoi"); }
                        }} data-testid={`premium-notify-${item.id}`}>
                        <Bell className="w-3 h-3" /> {item.client_notified ? 'Relancer' : 'Notifier'}
                      </Button>
                      {/* Consulter l'analyse (3 onglets) */}
                      {item.dossier_id && onViewDossierAnalysis && (
                        <Button size="sm" variant="outline" className="text-xs h-7 gap-1 border-amber-500/30 text-amber-600 hover:bg-amber-50"
                          onClick={() => onViewDossierAnalysis(item.dossier_id)}
                          data-testid={`premium-view-analysis-${item.id}`}>
                          <FileSearch className="w-3 h-3" /> Consulter l'analyse
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

      {/* Review/Edit Dialog */}
      {reviewDialog && (
        <Dialog open onOpenChange={() => setReviewDialog(null)}>
          <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto" data-testid="review-dialog">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <PenTool className="w-5 h-5 text-accent" />
                Relecture expert — {reviewDialog.email || 'Client'}
              </DialogTitle>
              <DialogDescription>
                Relisez, modifiez si nécessaire, puis validez pour préparer l'envoi.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="flex flex-wrap gap-2 text-xs">
                <Badge variant="outline">{productLabel}</Badge>
                {reviewDialog.source_data?.type_dossier && <Badge variant="outline">{reviewDialog.source_data.type_dossier}</Badge>}
                {reviewDialog.source_data?.regime && <Badge variant="outline">{reviewDialog.source_data.regime}</Badge>}
                {reviewDialog.context && <Badge variant="outline" className="max-w-[300px] truncate">{reviewDialog.context}</Badge>}
                <Badge variant="outline">{reviewDialog.amount}€</Badge>
              </div>

              {reviewDialog.source_data?.situation && (
                <div className="p-3 rounded-lg bg-muted/50 border">
                  <Label className="font-medium text-xs mb-1 block text-muted-foreground">Situation décrite par le client</Label>
                  <p className="text-sm leading-relaxed max-h-[120px] overflow-y-auto">{reviewDialog.source_data.situation}</p>
                </div>
              )}

              <div>
                <Label className="font-medium text-sm mb-2 block">Analyse à relire / modifier</Label>
                {reviewDialog._loading ? (
                  <div className="flex items-center justify-center py-12 border rounded-lg">
                    <Loader2 className="w-6 h-6 animate-spin text-accent mr-2" />
                    <span className="text-sm text-muted-foreground">Chargement du contenu...</span>
                  </div>
                ) : (
                  <textarea
                    className="flex w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring min-h-[350px] resize-y font-mono leading-relaxed"
                    defaultValue={reviewDialog.reviewed_analysis || ''}
                    data-testid="review-textarea"
                    onChange={(e) => setReviewDialog(prev => ({ ...prev, reviewed_analysis: e.target.value }))}
                  />
                )}
              </div>
              <div>
                <Label className="font-medium text-sm mb-2 block">Notes internes (optionnel)</Label>
                <Textarea
                  placeholder="Notes privées sur cette relecture..."
                  defaultValue={reviewDialog.admin_notes || ''}
                  className="min-h-[60px]"
                  onChange={(e) => setReviewDialog(prev => ({ ...prev, admin_notes: e.target.value }))}
                />
              </div>
            </div>
            <DialogFooter className="gap-2 mt-4">
              <Button variant="outline" onClick={() => setReviewDialog(null)}>Annuler</Button>
              <Button
                className="gap-1.5 bg-green-600 hover:bg-green-500"
                data-testid="review-validate-btn"
                disabled={reviewDialog._loading || !reviewDialog.reviewed_analysis?.trim()}
                onClick={async () => {
                  try {
                    await axios.patch(`${API}/admin/premium-analyses/${reviewDialog.id}`, {
                      status: 'valide',
                      reviewed_analysis: reviewDialog.reviewed_analysis || '',
                      notes: reviewDialog.admin_notes || ''
                    }, axiosConfig);
                    toast.success("Dossier validé — prêt à envoyer");
                    setReviewDialog(null);
                    onRefresh();
                  } catch { toast.error("Erreur de validation"); }
                }}>
                <CheckCircle className="w-4 h-4" /> Valider — prêt à envoyer
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};
