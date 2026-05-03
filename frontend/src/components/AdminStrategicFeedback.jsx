import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, RefreshCw, MessageCircle, AlertTriangle, HelpCircle, Briefcase, Heart, Filter, Zap, TrendingUp, Eye, BarChart3 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CATEGORY_LABELS = {
  juridique: { label: 'Juridique', color: 'bg-blue-100 text-blue-700 border-blue-200' },
  medical: { label: 'Medical', color: 'bg-red-100 text-red-700 border-red-200' },
  administratif: { label: 'Administratif', color: 'bg-amber-100 text-amber-700 border-amber-200' },
  assurantiel: { label: 'Assurantiel', color: 'bg-purple-100 text-purple-700 border-purple-200' },
  mdph: { label: 'MDPH', color: 'bg-teal-100 text-teal-700 border-teal-200' },
  accompagnement: { label: 'Accompagnement', color: 'bg-pink-100 text-pink-700 border-pink-200' },
  incomprehension_offre: { label: 'Incomprehension offre', color: 'bg-orange-100 text-orange-700 border-orange-200' },
  non_categorise: { label: 'Non categorise', color: 'bg-gray-100 text-gray-600 border-gray-200' },
};

const CLARTE_LABELS = {
  oui: { label: 'Oui, clairement', icon: '✓', color: 'text-emerald-600' },
  partiellement: { label: 'Partiellement', icon: '~', color: 'text-amber-600' },
  non: { label: 'Non, pas assez', icon: '✗', color: 'text-red-600' },
};

export const AdminStrategicFeedback = ({ axiosConfig }) => {
  const [feedbacks, setFeedbacks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [synthesis, setSynthesis] = useState(null);
  const [synthLoading, setSynthLoading] = useState(false);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const catParam = filter === 'all' ? '' : `?category=${filter}`;
      const [fbRes, stRes] = await Promise.all([
        axios.get(`${API}/feedback${catParam}`, axiosConfig),
        axios.get(`${API}/feedback/stats`, axiosConfig),
      ]);
      setFeedbacks(fbRes.data.feedbacks || []);
      setStats(stRes.data);
    } catch {
      toast.error("Erreur chargement feedbacks");
    } finally {
      setLoading(false);
    }
  };

  const fetchSynthesis = async () => {
    setSynthLoading(true);
    try {
      const res = await axios.get(`${API}/feedback/synthesis`, axiosConfig);
      setSynthesis(res.data);
    } catch {
      toast.error("Erreur lors de la synthese");
    } finally {
      setSynthLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, [filter]);

  if (loading && !stats) {
    return <Card><CardContent className="flex items-center justify-center py-12"><Loader2 className="w-5 h-5 animate-spin" /></CardContent></Card>;
  }

  return (
    <div className="space-y-4" data-testid="admin-feedback-panel">
      {/* Stats overview */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Card>
            <CardContent className="p-3 text-center">
              <MessageCircle className="w-4 h-4 mx-auto mb-1 text-muted-foreground" />
              <p className="text-2xl font-bold" data-testid="feedback-stat-total">{stats.total}</p>
              <p className="text-[10px] text-muted-foreground uppercase">Total retours</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <AlertTriangle className="w-4 h-4 mx-auto mb-1 text-amber-500" />
              <p className="text-2xl font-bold">{stats.with_frein}</p>
              <p className="text-[10px] text-muted-foreground uppercase">Avec frein</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <HelpCircle className="w-4 h-4 mx-auto mb-1 text-blue-500" />
              <p className="text-2xl font-bold">{stats.with_besoin}</p>
              <p className="text-[10px] text-muted-foreground uppercase">Avec besoin</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <Heart className="w-4 h-4 mx-auto mb-1 text-emerald-500" />
              <p className="text-2xl font-bold">
                {stats.clarte_distribution?.find(c => c.label === 'oui')?.count || 0}
              </p>
              <p className="text-[10px] text-muted-foreground uppercase">Offre claire</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Distributions */}
      {stats && (stats.category_distribution?.length > 0 || stats.clarte_distribution?.length > 0) && (
        <div className="grid sm:grid-cols-2 gap-3">
          {stats.category_distribution?.length > 0 && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-xs flex items-center gap-1.5"><Briefcase className="w-3.5 h-3.5" /> Categories detectees</CardTitle></CardHeader>
              <CardContent className="space-y-1">
                {stats.category_distribution.map(c => {
                  const cfg = CATEGORY_LABELS[c.category] || CATEGORY_LABELS.non_categorise;
                  return (
                    <div key={c.category} className="flex items-center justify-between text-xs px-2 py-1.5 rounded border">
                      <Badge variant="outline" className={`text-[9px] ${cfg.color}`}>{cfg.label}</Badge>
                      <span className="font-medium">{c.count}</span>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          )}
          {stats.clarte_distribution?.length > 0 && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-xs flex items-center gap-1.5"><HelpCircle className="w-3.5 h-3.5" /> Comprehension de l'offre</CardTitle></CardHeader>
              <CardContent className="space-y-1">
                {stats.clarte_distribution.map(c => {
                  const cfg = CLARTE_LABELS[c.label] || {};
                  return (
                    <div key={c.label} className="flex items-center justify-between text-xs px-2 py-1.5 rounded border">
                      <span className={cfg.color}>{cfg.label || c.label}</span>
                      <span className="font-medium">{c.count}</span>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Synthese Intelligente */}
      <Card data-testid="synthesis-panel">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-amber-500" /> Synthese Intelligente
            </CardTitle>
            <Button
              size="sm"
              onClick={fetchSynthesis}
              disabled={synthLoading}
              className="h-7 text-xs gap-1.5"
              data-testid="synthesis-generate-btn"
            >
              {synthLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <BarChart3 className="w-3 h-3" />}
              {synthesis ? 'Actualiser' : 'Generer'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {!synthesis && !synthLoading && (
            <p className="text-xs text-muted-foreground py-4 text-center">
              Cliquez sur "Generer" pour analyser les retours et extraire les signaux forts.
            </p>
          )}
          {synthLoading && (
            <div className="flex justify-center py-6"><Loader2 className="w-5 h-5 animate-spin" /></div>
          )}
          {synthesis && !synthLoading && (
            <div className="space-y-4 mt-2">
              {/* Meta */}
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span>{synthesis.total} retours analyses</span>
                <span>|</span>
                <span>Seuil signal fort : {synthesis.seuil_signal_fort}+ mentions</span>
                {synthesis.sources && Object.keys(synthesis.sources).length > 0 && (
                  <>
                    <span>|</span>
                    <span>Sources : {Object.entries(synthesis.sources).map(([k, v]) => `${k} (${v})`).join(', ')}</span>
                  </>
                )}
              </div>

              {/* Irritants */}
              {synthesis.irritants?.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold flex items-center gap-1.5 mb-2">
                    <AlertTriangle className="w-3.5 h-3.5 text-red-500" /> Top irritants / freins
                  </h4>
                  <div className="space-y-1.5">
                    {synthesis.irritants.map((item, i) => (
                      <div key={i} className="flex items-start gap-2 p-2 rounded-lg border text-xs" data-testid={`synthesis-irritant-${i}`}>
                        <Badge variant="outline" className={`text-[9px] flex-shrink-0 ${item.signal === 'fort' ? 'bg-red-100 text-red-700 border-red-200' : 'bg-gray-100 text-gray-600 border-gray-200'}`}>
                          {item.signal === 'fort' ? 'SIGNAL FORT' : 'Bruit'}
                        </Badge>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{item.theme}</span>
                            <span className="text-muted-foreground">{item.count}x ({item.pct}%)</span>
                          </div>
                          {item.verbatims?.length > 0 && (
                            <div className="mt-1 space-y-0.5">
                              {item.verbatims.map((v, vi) => (
                                <p key={vi} className="text-muted-foreground italic text-[11px] truncate">"{v}"</p>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Besoins */}
              {synthesis.besoins?.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold flex items-center gap-1.5 mb-2">
                    <TrendingUp className="w-3.5 h-3.5 text-blue-500" /> Besoins non couverts
                  </h4>
                  <div className="space-y-1.5">
                    {synthesis.besoins.map((item, i) => (
                      <div key={i} className="flex items-start gap-2 p-2 rounded-lg border text-xs" data-testid={`synthesis-besoin-${i}`}>
                        <Badge variant="outline" className={`text-[9px] flex-shrink-0 ${item.signal === 'fort' ? 'bg-blue-100 text-blue-700 border-blue-200' : 'bg-gray-100 text-gray-600 border-gray-200'}`}>
                          {item.signal === 'fort' ? 'SIGNAL FORT' : 'Bruit'}
                        </Badge>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{item.theme}</span>
                            <span className="text-muted-foreground">{item.count}x ({item.pct}%)</span>
                          </div>
                          {item.verbatims?.length > 0 && (
                            <div className="mt-1 space-y-0.5">
                              {item.verbatims.map((v, vi) => (
                                <p key={vi} className="text-muted-foreground italic text-[11px] truncate">"{v}"</p>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Clarte */}
              {synthesis.clarte && Object.keys(synthesis.clarte).length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold flex items-center gap-1.5 mb-2">
                    <Eye className="w-3.5 h-3.5 text-amber-500" /> Comprehension de l'offre
                  </h4>
                  <div className="p-3 rounded-lg border space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-3 bg-muted rounded-full overflow-hidden flex">
                        {synthesis.clarte.oui?.pct > 0 && (
                          <div className="bg-emerald-500 h-full transition-all" style={{ width: `${synthesis.clarte.oui.pct}%` }} />
                        )}
                        {synthesis.clarte.partiellement?.pct > 0 && (
                          <div className="bg-amber-400 h-full transition-all" style={{ width: `${synthesis.clarte.partiellement.pct}%` }} />
                        )}
                        {synthesis.clarte.non?.pct > 0 && (
                          <div className="bg-red-500 h-full transition-all" style={{ width: `${synthesis.clarte.non.pct}%` }} />
                        )}
                      </div>
                    </div>
                    <div className="flex justify-between text-[10px] text-muted-foreground">
                      <span className="text-emerald-600">Oui : {synthesis.clarte.oui?.pct || 0}%</span>
                      <span className="text-amber-600">Partiellement : {synthesis.clarte.partiellement?.pct || 0}%</span>
                      <span className="text-red-600">Non : {synthesis.clarte.non?.pct || 0}%</span>
                    </div>
                    {synthesis.clarte.alerte && (
                      <div className="flex items-center gap-1.5 text-[11px] text-red-600 font-medium mt-1" data-testid="synthesis-clarte-alerte">
                        <AlertTriangle className="w-3 h-3" />
                        Alerte : {(synthesis.clarte.non?.pct || 0) + (synthesis.clarte.partiellement?.pct || 0)}% des clients ne comprennent pas clairement l'offre
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Recommandations */}
              {synthesis.recommandations?.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold flex items-center gap-1.5 mb-2">
                    <Zap className="w-3.5 h-3.5 text-amber-500" /> Recommandations strategiques
                  </h4>
                  <div className="space-y-1">
                    {synthesis.recommandations.map((r, i) => (
                      <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-amber-50/50 border border-amber-200/40 text-xs" data-testid={`synthesis-reco-${i}`}>
                        <span className="text-amber-600 font-bold flex-shrink-0">{i + 1}.</span>
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Empty state */}
              {synthesis.irritants?.length === 0 && synthesis.besoins?.length === 0 && (
                <p className="text-xs text-muted-foreground text-center py-4">
                  Pas assez de donnees pour extraire des signaux. Continuez a collecter des retours.
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Filter + List */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm flex items-center gap-1.5">
              <MessageCircle className="w-4 h-4" /> Retours d'experience ({feedbacks.length})
            </CardTitle>
            <div className="flex items-center gap-2">
              <Select value={filter} onValueChange={setFilter}>
                <SelectTrigger className="h-7 w-40 text-xs" data-testid="feedback-filter">
                  <Filter className="w-3 h-3 mr-1" /><SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous</SelectItem>
                  {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
                    <SelectItem key={k} value={k}>{v.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button size="sm" variant="ghost" onClick={fetchAll} className="h-7 w-7 p-0" data-testid="feedback-refresh">
                <RefreshCw className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8"><Loader2 className="w-5 h-5 animate-spin" /></div>
          ) : feedbacks.length === 0 ? (
            <p className="text-xs text-muted-foreground py-6 text-center">Aucun retour pour le moment</p>
          ) : (
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {feedbacks.map((fb, i) => (
                <div key={fb.id || i} className="p-3 rounded-lg border text-xs space-y-2" data-testid={`feedback-item-${i}`}>
                  <div className="flex items-center justify-between flex-wrap gap-1">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      {fb.categories?.map(cat => {
                        const cfg = CATEGORY_LABELS[cat] || CATEGORY_LABELS.non_categorise;
                        return <Badge key={cat} variant="outline" className={`text-[8px] ${cfg.color}`}>{cfg.label}</Badge>;
                      })}
                      {fb.source && <Badge variant="outline" className="text-[8px]">{fb.source}</Badge>}
                    </div>
                    <span className="text-[10px] text-muted-foreground">
                      {fb.created_at ? new Date(fb.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' }) : ''}
                    </span>
                  </div>
                  {fb.frein && (
                    <div>
                      <span className="text-muted-foreground font-medium">Frein :</span>
                      <span className="ml-1">{fb.frein}</span>
                    </div>
                  )}
                  {fb.besoin && (
                    <div>
                      <span className="text-muted-foreground font-medium">Besoin :</span>
                      <span className="ml-1">{fb.besoin}</span>
                    </div>
                  )}
                  {fb.clarte && (
                    <div>
                      <span className="text-muted-foreground font-medium">Clarte :</span>
                      <span className={`ml-1 ${CLARTE_LABELS[fb.clarte]?.color || ''}`}>
                        {CLARTE_LABELS[fb.clarte]?.label || fb.clarte}
                      </span>
                    </div>
                  )}
                  {fb.commentaire && (
                    <div className="italic text-muted-foreground">"{fb.commentaire}"</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
