import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Pin, PinOff, Trash2, Send, Loader2, MessageSquare, ExternalLink, Sparkles } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CATEGORIES = [
  { id: 'accident-travail', label: 'Accident du travail' },
  { id: 'maladie-professionnelle', label: 'Maladie professionnelle' },
  { id: 'expertise-medicale', label: 'Expertise médicale' },
  { id: 'invalidite', label: 'Invalidité' },
  { id: 'mdph', label: 'Démarches MDPH' },
  { id: 'protection-juridique', label: 'Protection juridique' },
];

const DEFAULT_PSEUDO = 'Équipe S.E.S';
const CONTENT_MIN = 80;

export const AdminForumSeed = () => {
  const { token } = useAuth();
  const authConfig = { headers: { Authorization: `Bearer ${token}` } };

  const [categoryId, setCategoryId] = useState('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [pseudo, setPseudo] = useState(DEFAULT_PSEUDO);
  const [isPinned, setIsPinned] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [seedTopics, setSeedTopics] = useState([]);
  const [loadingList, setLoadingList] = useState(false);

  const loadSeedTopics = useCallback(async () => {
    setLoadingList(true);
    try {
      const { data } = await axios.get(`${API}/admin/forum/seed-topics`, authConfig);
      setSeedTopics(data || []);
    } catch (e) {
      toast.error("Impossible de charger les sujets éditoriaux");
    } finally {
      setLoadingList(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    if (token) loadSeedTopics();
  }, [token, loadSeedTopics]);

  const reset = () => {
    setCategoryId('');
    setTitle('');
    setContent('');
    setPseudo(DEFAULT_PSEUDO);
    setIsPinned(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!categoryId) return toast.error("Sélectionnez une catégorie");
    if (title.trim().length < 10) return toast.error("Titre trop court (10 caractères min.)");
    if (content.trim().length < CONTENT_MIN) return toast.error(`Contenu trop court (${CONTENT_MIN} caractères min.)`);

    setSubmitting(true);
    try {
      await axios.post(
        `${API}/admin/forum/seed-topic`,
        { category_id: categoryId, title: title.trim(), content: content.trim() },
        {
          ...authConfig,
          params: { pseudo: pseudo.trim() || DEFAULT_PSEUDO, is_pinned: isPinned },
        }
      );
      toast.success("Sujet éditorial publié");
      reset();
      loadSeedTopics();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Erreur lors de la publication");
    } finally {
      setSubmitting(false);
    }
  };

  const togglePin = async (topicId, currentPinned) => {
    try {
      await axios.patch(
        `${API}/admin/forum/topics/${topicId}/pin`,
        null,
        { ...authConfig, params: { is_pinned: !currentPinned } }
      );
      toast.success(!currentPinned ? "Sujet épinglé" : "Sujet désépinglé");
      loadSeedTopics();
    } catch {
      toast.error("Action impossible");
    }
  };

  const deleteSeed = async (topicId) => {
    if (!window.confirm("Supprimer définitivement ce sujet ? Cette action est irréversible.")) return;
    try {
      await axios.delete(`${API}/admin/forum/topics/${topicId}`, authConfig);
      toast.success("Sujet retiré du forum");
      loadSeedTopics();
    } catch {
      toast.error("Suppression impossible");
    }
  };

  const formatDate = (d) => {
    if (!d) return '—';
    try {
      return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch { return '—'; }
  };

  const remaining = Math.max(0, CONTENT_MIN - content.trim().length);

  return (
    <div className="space-y-6" data-testid="admin-forum-seed-root">
      {/* Intro */}
      <div className="rounded-xl border border-amber-200/60 bg-amber-50/40 px-5 py-4 flex items-start gap-3" data-testid="forum-seed-intro">
        <Sparkles className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-foreground/80 leading-relaxed">
          <p className="font-semibold text-foreground mb-1">Amorcer la communauté</p>
          <p>
            Publiez des <strong>sujets&nbsp;graines</strong> signés <em>{DEFAULT_PSEUDO}</em> pour lancer les discussions
            sans passer par l'inscription publique. Chaque sujet est épinglé par défaut&nbsp;; il apparaît en tête de sa
            catégorie et reste pleinement modérable.
          </p>
          <p className="mt-2 text-xs text-muted-foreground">
            Rédigez avec votre expertise réelle (aucun faux témoignage, aucune personne identifiable). Ces sujets renforcent
            votre E-E-A-T SEO et invitent les visiteurs à répondre.
          </p>
        </div>
      </div>

      {/* Formulaire */}
      <Card data-testid="forum-seed-form-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <MessageSquare className="w-4 h-4 text-accent" />
            Publier un sujet éditorial
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4" data-testid="forum-seed-form">
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="seed-category">Catégorie *</Label>
                <Select value={categoryId} onValueChange={setCategoryId}>
                  <SelectTrigger id="seed-category" data-testid="seed-category-trigger">
                    <SelectValue placeholder="Choisir une catégorie" />
                  </SelectTrigger>
                  <SelectContent>
                    {CATEGORIES.map(c => (
                      <SelectItem key={c.id} value={c.id}>{c.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="seed-pseudo">Signature (auteur affiché)</Label>
                <Input
                  id="seed-pseudo"
                  value={pseudo}
                  onChange={(e) => setPseudo(e.target.value)}
                  placeholder={DEFAULT_PSEUDO}
                  data-testid="seed-pseudo-input"
                />
                <p className="text-[11px] text-muted-foreground">Conseil&nbsp;: garder « {DEFAULT_PSEUDO} » pour la cohérence.</p>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="seed-title">Titre du sujet *</Label>
              <Input
                id="seed-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Ex. : Comment bien préparer son expertise médicale ?"
                maxLength={200}
                data-testid="seed-title-input"
              />
              <p className="text-[11px] text-muted-foreground">{title.length}/200 caractères</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="seed-content">Contenu du sujet *</Label>
              <Textarea
                id="seed-content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder={"Présentez le contexte, les questions fréquentes et invitez la communauté à partager son expérience.\n\nExemple :\n- Les 3 erreurs les plus courantes avant l'expertise\n- Ce que personne ne vous dira en amont\n- Question ouverte : quelle a été votre expérience ?"}
                rows={10}
                data-testid="seed-content-textarea"
              />
              <p className="text-[11px] text-muted-foreground">
                {content.trim().length} caractères
                {remaining > 0 && <span className="text-amber-600"> — encore {remaining} pour publier</span>}
              </p>
            </div>

            <label className="flex items-center gap-2 text-sm cursor-pointer select-none" data-testid="seed-pinned-label">
              <input
                type="checkbox"
                checked={isPinned}
                onChange={(e) => setIsPinned(e.target.checked)}
                className="w-4 h-4 rounded border-border accent-amber-600"
                data-testid="seed-pinned-checkbox"
              />
              <Pin className="w-3.5 h-3.5 text-amber-600" />
              Épingler en tête de catégorie (recommandé pour les sujets fondateurs)
            </label>

            <div className="flex items-center gap-3 pt-2">
              <Button type="submit" disabled={submitting} data-testid="seed-submit-btn">
                {submitting ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Publication…</>
                ) : (
                  <><Send className="w-4 h-4 mr-2" /> Publier le sujet</>
                )}
              </Button>
              <Button type="button" variant="outline" onClick={reset} disabled={submitting} data-testid="seed-reset-btn">
                Réinitialiser
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Liste des seed topics */}
      <Card data-testid="forum-seed-list-card">
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-base">
            <span>Sujets éditoriaux publiés</span>
            <Badge variant="outline" data-testid="seed-count-badge">{seedTopics.length}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadingList ? (
            <div className="flex items-center justify-center py-10 text-muted-foreground" data-testid="seed-loading">
              <Loader2 className="w-5 h-5 animate-spin mr-2" /> Chargement…
            </div>
          ) : seedTopics.length === 0 ? (
            <div className="text-center py-10 text-sm text-muted-foreground" data-testid="seed-empty">
              Aucun sujet éditorial pour le moment. Publiez le premier pour amorcer la communauté.
            </div>
          ) : (
            <div className="space-y-3" data-testid="seed-list">
              {seedTopics.map((t) => {
                const cat = CATEGORIES.find(c => c.id === t.category_id);
                const isDeleted = t.status === 'deleted';
                return (
                  <div
                    key={t.id}
                    className={`rounded-lg border p-4 transition-all ${isDeleted ? 'opacity-60 bg-muted/30' : 'bg-card hover:border-accent/40'}`}
                    data-testid={`seed-item-${t.id}`}
                  >
                    <div className="flex items-start justify-between gap-3 flex-wrap">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          {t.is_pinned && <Badge className="bg-amber-100 text-amber-800 border-amber-200 gap-1"><Pin className="w-3 h-3" /> Épinglé</Badge>}
                          {cat && <Badge variant="outline" className="text-[11px]">{cat.label}</Badge>}
                          {isDeleted && <Badge variant="destructive" className="text-[11px]">Supprimé</Badge>}
                          <span className="text-[11px] text-muted-foreground">{formatDate(t.created_at)}</span>
                        </div>
                        <p className="font-semibold text-sm text-foreground truncate" title={t.title}>{t.title}</p>
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{t.content}</p>
                        <p className="text-[11px] text-muted-foreground mt-1">
                          Par <span className="font-medium">{t.author_pseudo}</span> · {t.views || 0} vues · {t.replies_count || 0} réponses
                        </p>
                      </div>
                      <div className="flex items-center gap-1.5 flex-shrink-0">
                        {!isDeleted && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => togglePin(t.id, t.is_pinned)}
                              title={t.is_pinned ? "Désépingler" : "Épingler"}
                              data-testid={`seed-pin-btn-${t.id}`}
                            >
                              {t.is_pinned ? <PinOff className="w-3.5 h-3.5" /> : <Pin className="w-3.5 h-3.5" />}
                            </Button>
                            <a
                              href={`/forum/sujet/${t.id}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center justify-center rounded-md border border-input bg-background h-8 px-2 text-xs hover:bg-muted transition-colors"
                              title="Voir sur le forum"
                              data-testid={`seed-view-btn-${t.id}`}
                            >
                              <ExternalLink className="w-3.5 h-3.5" />
                            </a>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => deleteSeed(t.id)}
                              title="Supprimer"
                              className="text-destructive hover:text-destructive"
                              data-testid={`seed-delete-btn-${t.id}`}
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminForumSeed;
