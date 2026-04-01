import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import {
  Zap, Eye, Bell, Send, CheckCircle, PenTool, Loader2, Brain, FileSearch, Clock, Trash2, Calendar, Download
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
      {/* Premium Stats Row */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <Card className="border-border/60 hover:shadow-sm transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Total</p>
                <p className="text-2xl font-bold mt-1.5">{filteredStats.total}</p>
              </div>
              <div className="w-9 h-9 rounded-lg bg-muted/60 flex items-center justify-center">
                <Icon className={`w-4 h-4 ${accentColor}`} />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className={`border-amber-200/60 hover:shadow-sm transition-shadow ${filteredStats.en_attente > 0 ? 'ring-1 ring-amber-200/50' : ''}`}>
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">En attente</p>
                <p className="text-2xl font-bold mt-1.5 text-amber-600">{filteredStats.en_attente}</p>
              </div>
              <div className="w-9 h-9 rounded-lg bg-amber-50 flex items-center justify-center">
                <Clock className="w-4 h-4 text-amber-500" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-blue-200/60 hover:shadow-sm transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">En cours</p>
                <p className="text-2xl font-bold mt-1.5 text-blue-600">{filteredStats.en_cours}</p>
              </div>
              <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center">
                <Eye className="w-4 h-4 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-green-200/60 hover:shadow-sm transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Validé</p>
                <p className="text-2xl font-bold mt-1.5 text-green-600">{filteredStats.valide}</p>
              </div>
              <div className="w-9 h-9 rounded-lg bg-green-50 flex items-center justify-center">
                <CheckCircle className="w-4 h-4 text-green-500" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-emerald-200/60 hover:shadow-sm transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Envoyé</p>
                <p className="text-2xl font-bold mt-1.5 text-emerald-600">{filteredStats.envoye}</p>
              </div>
              <div className="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center">
                <Send className="w-4 h-4 text-emerald-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Items list — Decision Center */}
      <Card className="border-border/60">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2.5 text-lg" data-testid={`premium-${productType}-title`}>
            <Icon className={`w-5 h-5 ${accentColor}`} />
            Relecture expert — {productLabel}
            {filteredStats.en_attente > 0 && (
              <Badge className="bg-amber-100 text-amber-700 border-amber-200 text-[10px] ml-1">{filteredStats.en_attente} en attente</Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-3">
            {filteredItems.map(item => {
              const sc = STATUS_CONFIG[item.status] || STATUS_CONFIG.en_attente;
              return (
                <div key={item.id} className={`group p-4 rounded-xl border ${sc.border} hover:shadow-sm transition-all`} data-testid={`premium-item-${item.id}`}>
                  <div className="flex items-start gap-3.5">
                    {/* Status indicator */}
                    <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${item.status === 'en_attente' ? 'bg-amber-100' : item.status === 'en_cours' ? 'bg-blue-100' : item.status === 'valide' ? 'bg-green-100' : 'bg-emerald-100'}`}>
                      {item.status === 'en_attente' && <Clock className="w-4 h-4 text-amber-600" />}
                      {item.status === 'en_cours' && <PenTool className="w-4 h-4 text-blue-600" />}
                      {item.status === 'valide' && <CheckCircle className="w-4 h-4 text-green-600" />}
                      {(item.status === 'envoye' || item.status === 'termine') && <Send className="w-4 h-4 text-emerald-600" />}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className="font-semibold text-sm">{item.email || item.name || 'Client'}</span>
                        <Badge className={`text-[10px] ${sc.color}`}>{sc.label}</Badge>
                        <Badge variant="outline" className="text-[10px]">{productLabel}</Badge>
                        {item.premium_pdf && <Badge className="bg-accent/10 text-accent border-accent/20 text-[10px]">PDF Pro</Badge>}
                        {item.relecture_expert_required && <Badge className="bg-red-500/10 text-red-600 border-red-500/20 text-[10px] font-bold">Relecture Expert</Badge>}
                        {item.admin_test && <Badge className="bg-zinc-100 text-zinc-500 border-zinc-200 text-[10px]">Test Admin</Badge>}
                        <span className="text-[11px] text-muted-foreground font-medium">{item.amount}€</span>
                      </div>
                      {item.name && item.email && <p className="text-xs text-muted-foreground">Client : {item.name}</p>}
                      {item.context && <p className="text-xs text-muted-foreground mt-0.5 truncate max-w-md">{item.context}</p>}
                      <div className="flex items-center gap-3 mt-1.5 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {new Date(item.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                        {item.sent_at && <span className="flex items-center gap-1 text-green-600"><Send className="w-3 h-3" /> Envoyé le {new Date(item.sent_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</span>}
                      </div>
                    </div>

                    {/* Actions column */}
                    <div className="flex gap-1.5 flex-shrink-0 flex-wrap items-start">
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
                      {/* Supprimer */}
                      <Button size="sm" variant="ghost" className="text-xs h-7 w-7 p-0 text-muted-foreground/50 hover:text-red-600 hover:bg-red-50"
                        onClick={() => {
                          if (window.confirm(`Supprimer le dossier de ${item.name || item.email} ? Cette action est irréversible.`)) {
                            axios.delete(`${API}/admin/premium-analyses/${item.id}`, axiosConfig)
                              .then(() => { toast.success('Dossier supprimé'); onRefresh(); })
                              .catch(() => toast.error('Erreur lors de la suppression'));
                          }
                        }}
                        data-testid={`premium-delete-${item.id}`}>
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
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
              {/* PDF Preview/Download button */}
              <Button
                variant="outline"
                className="gap-1.5 border-accent/30 text-accent hover:bg-accent/5"
                data-testid="review-pdf-btn"
                disabled={reviewDialog._loading || !reviewDialog.reviewed_analysis?.trim()}
                onClick={async () => {
                  try {
                    toast.info("Génération du PDF en cours...");
                    const pdfEndpoint = productType === 'dossier_express' && reviewDialog.dossier_id
                      ? `${API}/admin/dossier-express/${reviewDialog.dossier_id}/preview-pdf`
                      : `${API}/admin/strategiia/${reviewDialog.id}/preview-pdf`;
                    const token = axiosConfig?.headers?.Authorization?.replace('Bearer ', '') || '';
                    const response = await fetch(pdfEndpoint, {
                      headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (!response.ok) throw new Error('Erreur PDF');
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    window.open(url, '_blank');
                    toast.success("PDF généré avec succès");
                  } catch (err) {
                    toast.error("Erreur lors de la génération du PDF");
                  }
                }}>
                <Download className="w-4 h-4" /> Voir le PDF final
              </Button>
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
