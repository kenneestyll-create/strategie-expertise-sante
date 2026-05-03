import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { 
  ChevronLeft,
  Heart,
  MessageSquare,
  Flag,
  Send,
  Loader2,
  Clock,
  Eye,
  Lock
} from 'lucide-react';
import { useForumAuth } from '@/context/ForumAuthContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ForumTopicPage = () => {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [topic, setTopic] = useState(null);
  const [replies, setReplies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [replyContent, setReplyContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportTarget, setReportTarget] = useState(null);
  const [reportReason, setReportReason] = useState('');
  const { isAuthenticated, token, user } = useForumAuth();

  useEffect(() => {
    fetchTopic();
  }, [topicId]);

  const fetchTopic = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/forum/topics/${topicId}`);
      setTopic(response.data.topic);
      setReplies(response.data.replies || []);
    } catch (error) {
      console.error('Error:', error);
      if (error.response?.status === 404) {
        toast.error("Sujet non trouvé");
        navigate('/forum');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLikeTopic = async () => {
    if (!isAuthenticated) {
      toast.error("Connectez-vous pour aimer ce sujet");
      return;
    }
    
    try {
      const response = await axios.post(
        `${API}/forum/topics/${topicId}/like`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTopic(prev => ({
        ...prev,
        likes: response.data.liked 
          ? [...(prev.likes || []), user.id]
          : (prev.likes || []).filter(id => id !== user.id)
      }));
    } catch (error) {
      toast.error("Erreur lors du like");
    }
  };

  const handleLikeReply = async (replyId) => {
    if (!isAuthenticated) {
      toast.error("Connectez-vous pour aimer cette réponse");
      return;
    }
    
    try {
      const response = await axios.post(
        `${API}/forum/replies/${replyId}/like`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setReplies(prev => prev.map(r => 
        r.id === replyId 
          ? { 
              ...r, 
              likes: response.data.liked 
                ? [...(r.likes || []), user.id]
                : (r.likes || []).filter(id => id !== user.id)
            }
          : r
      ));
    } catch (error) {
      toast.error("Erreur lors du like");
    }
  };

  const handleSubmitReply = async (e) => {
    e.preventDefault();
    
    if (!replyContent.trim()) {
      toast.error("Veuillez écrire une réponse");
      return;
    }

    setSubmitting(true);
    try {
      await axios.post(
        `${API}/forum/topics/${topicId}/replies`,
        { content: replyContent },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success("Réponse publiée !");
      setReplyContent('');
      fetchTopic();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors de la publication");
    } finally {
      setSubmitting(false);
    }
  };

  const handleReport = async () => {
    if (!reportReason.trim()) {
      toast.error("Veuillez indiquer la raison du signalement");
      return;
    }

    try {
      await axios.post(
        `${API}/forum/report`,
        {
          target_type: reportTarget.type,
          target_id: reportTarget.id,
          reason: reportReason
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success("Signalement envoyé. Merci de votre vigilance.");
      setShowReportModal(false);
      setReportTarget(null);
      setReportReason('');
    } catch (error) {
      toast.error("Erreur lors du signalement");
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <main className="page-transition pt-20">
        <div className="max-w-4xl mx-auto px-4 py-12 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-muted-foreground" />
        </div>
      </main>
    );
  }

  if (!topic) {
    return null;
  }

  const isLiked = topic.likes?.includes(user?.id);

  return (
    <main className="page-transition pt-20">
      <section className="section-padding">
        <div className="max-w-4xl mx-auto">
          {/* Breadcrumb */}
          <Link 
            to="/forum" 
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Retour au forum
          </Link>

          {/* Topic */}
          <Card className="mb-8">
            <CardContent className="p-6">
              <div className="flex items-start gap-2 mb-4 flex-wrap">
                <h1 className="text-2xl font-semibold" data-testid="topic-title">
                  {topic.title}
                </h1>
                {topic.is_anonymous && (
                  <Badge variant="secondary">Anonyme</Badge>
                )}
                {topic.is_pinned && (
                  <Badge className="bg-accent">Épinglé</Badge>
                )}
                {topic.is_locked && (
                  <Badge variant="outline" className="gap-1">
                    <Lock className="w-3 h-3" />
                    Verrouillé
                  </Badge>
                )}
              </div>

              <div className="prose prose-sm max-w-none text-foreground mb-6">
                <p className="whitespace-pre-wrap">{topic.content}</p>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-border">
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span>Par <strong>{topic.author_pseudo}</strong></span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {formatDate(topic.created_at)}
                  </span>
                  <span className="flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    {topic.views} vues
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleLikeTopic}
                    className={`gap-1 ${isLiked ? 'text-red-500' : ''}`}
                    data-testid="like-topic-button"
                  >
                    <Heart className={`w-4 h-4 ${isLiked ? 'fill-current' : ''}`} />
                    {topic.likes?.length || 0}
                  </Button>
                  {isAuthenticated && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setReportTarget({ type: 'topic', id: topic.id });
                        setShowReportModal(true);
                      }}
                      className="gap-1 text-muted-foreground"
                    >
                      <Flag className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Replies */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              {replies.length} réponse{replies.length !== 1 ? 's' : ''}
            </h2>

            {replies.length === 0 ? (
              <Card className="text-center py-8">
                <CardContent>
                  <p className="text-muted-foreground">
                    Aucune réponse pour le moment. Soyez le premier à répondre !
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {replies.map((reply) => {
                  const replyLiked = reply.likes?.includes(user?.id);
                  return (
                    <Card key={reply.id} data-testid={`reply-${reply.id}`}>
                      <CardContent className="p-4">
                        <div className="prose prose-sm max-w-none text-foreground mb-4">
                          <p className="whitespace-pre-wrap">{reply.content}</p>
                        </div>

                        <div className="flex items-center justify-between pt-3 border-t border-border">
                          <div className="flex items-center gap-3 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              {reply.is_anonymous && (
                                <Badge variant="secondary" className="text-xs mr-1">Anonyme</Badge>
                              )}
                              <strong>{reply.author_pseudo}</strong>
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatDate(reply.created_at)}
                            </span>
                          </div>

                          <div className="flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleLikeReply(reply.id)}
                              className={`gap-1 ${replyLiked ? 'text-red-500' : ''}`}
                            >
                              <Heart className={`w-4 h-4 ${replyLiked ? 'fill-current' : ''}`} />
                              {reply.likes?.length || 0}
                            </Button>
                            {isAuthenticated && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setReportTarget({ type: 'reply', id: reply.id });
                                  setShowReportModal(true);
                                }}
                                className="gap-1 text-muted-foreground"
                              >
                                <Flag className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>

          {/* Reply Form */}
          {topic.is_locked ? (
            <Card className="bg-muted/50">
              <CardContent className="p-6 text-center">
                <Lock className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">
                  Ce sujet est verrouillé. Aucune nouvelle réponse n'est acceptée.
                </p>
              </CardContent>
            </Card>
          ) : isAuthenticated ? (
            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold mb-4">Votre réponse</h3>
                <form onSubmit={handleSubmitReply}>
                  <Textarea
                    value={replyContent}
                    onChange={(e) => setReplyContent(e.target.value)}
                    placeholder="Partagez votre expérience ou vos conseils..."
                    rows={4}
                    className="mb-4"
                    data-testid="reply-textarea"
                  />
                  <Button 
                    type="submit" 
                    className="rounded-full gap-2"
                    disabled={submitting}
                    data-testid="submit-reply-button"
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Publication...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        Publier
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          ) : (
            <Card className="bg-muted/50">
              <CardContent className="p-6 text-center">
                <p className="text-muted-foreground mb-4">
                  Connectez-vous pour participer à la discussion.
                </p>
                <div className="flex justify-center gap-3">
                  <Link to="/forum/connexion">
                    <Button variant="outline" className="rounded-full">
                      Se connecter
                    </Button>
                  </Link>
                  <Link to="/forum/inscription">
                    <Button className="rounded-full">
                      S'inscrire
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </section>

      {/* Report Modal */}
      <Dialog open={showReportModal} onOpenChange={setShowReportModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Signaler un contenu</DialogTitle>
            <DialogDescription>
              Indiquez la raison de votre signalement. Notre équipe de modération examinera le contenu.
            </DialogDescription>
          </DialogHeader>
          <Textarea
            value={reportReason}
            onChange={(e) => setReportReason(e.target.value)}
            placeholder="Expliquez pourquoi ce contenu pose problème..."
            rows={4}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowReportModal(false)}>
              Annuler
            </Button>
            <Button onClick={handleReport}>
              Envoyer le signalement
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </main>
  );
};
