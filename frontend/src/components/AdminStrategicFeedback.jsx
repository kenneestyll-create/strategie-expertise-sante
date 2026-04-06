import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, RefreshCw, MessageCircle, AlertTriangle, HelpCircle, Briefcase, Heart, Filter } from 'lucide-react';
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
