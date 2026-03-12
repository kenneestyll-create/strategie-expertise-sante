import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  MessageSquare, 
  ChevronLeft,
  Plus,
  Eye,
  Heart,
  Clock
} from 'lucide-react';
import { useForumAuth } from '@/context/ForumAuthContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ForumCategoryPage = () => {
  const { slug } = useParams();
  const [category, setCategory] = useState(null);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const { isAuthenticated } = useForumAuth();

  useEffect(() => {
    fetchData();
  }, [slug, page]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [catRes, topicsRes] = await Promise.all([
        axios.get(`${API}/forum/categories`),
        axios.get(`${API}/forum/topics?category_id=${slug}&page=${page}`)
      ]);
      
      const foundCategory = catRes.data.find(c => c.slug === slug || c.id === slug);
      setCategory(foundCategory);
      setTopics(topicsRes.data.topics || []);
      setTotalPages(topicsRes.data.pages || 1);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return "À l'instant";
    if (diff < 3600000) return `Il y a ${Math.floor(diff / 60000)} min`;
    if (diff < 86400000) return `Il y a ${Math.floor(diff / 3600000)} h`;
    
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  return (
    <main className="page-transition pt-20">
      <section className="section-padding">
        <div className="max-w-5xl mx-auto">
          {/* Breadcrumb */}
          <Link 
            to="/forum" 
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Retour au forum
          </Link>

          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
            <div>
              <h1 className="text-3xl font-semibold" data-testid="category-title">
                {category?.name || 'Catégorie'}
              </h1>
              <p className="text-muted-foreground mt-1">
                {category?.description}
              </p>
            </div>
            {isAuthenticated && (
              <Link to={`/forum/nouveau?category=${slug}`}>
                <Button className="rounded-full gap-2">
                  <Plus className="w-4 h-4" />
                  Nouveau sujet
                </Button>
              </Link>
            )}
          </div>

          {/* Topics List */}
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">
              Chargement...
            </div>
          ) : topics.length === 0 ? (
            <Card className="text-center py-12">
              <CardContent>
                <MessageSquare className="w-12 h-12 text-muted-foreground/50 mx-auto mb-4" />
                <p className="text-muted-foreground mb-4">
                  Aucune discussion dans cette catégorie.
                </p>
                {isAuthenticated && (
                  <Link to={`/forum/nouveau?category=${slug}`}>
                    <Button className="rounded-full">
                      Créer le premier sujet
                    </Button>
                  </Link>
                )}
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {topics.map((topic) => (
                <Link 
                  key={topic.id} 
                  to={`/forum/sujet/${topic.id}`}
                  data-testid={`topic-item-${topic.id}`}
                >
                  <Card className="hover:bg-muted/30 transition-colors">
                    <CardContent className="p-4">
                      <div className="flex items-start gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1 flex-wrap">
                            <h3 className="font-semibold">{topic.title}</h3>
                            {topic.is_anonymous && (
                              <Badge variant="secondary" className="text-xs">Anonyme</Badge>
                            )}
                            {topic.is_pinned && (
                              <Badge className="text-xs bg-accent">Épinglé</Badge>
                            )}
                            {topic.is_locked && (
                              <Badge variant="outline" className="text-xs">Verrouillé</Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                            {topic.content}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span>Par <strong>{topic.author_pseudo}</strong></span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatDate(topic.created_at)}
                            </span>
                            <span className="flex items-center gap-1">
                              <MessageSquare className="w-3 h-3" />
                              {topic.replies_count}
                            </span>
                            <span className="flex items-center gap-1">
                              <Eye className="w-3 h-3" />
                              {topic.views}
                            </span>
                            <span className="flex items-center gap-1">
                              <Heart className="w-3 h-3" />
                              {topic.likes?.length || 0}
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              <Button
                variant="outline"
                disabled={page === 1}
                onClick={() => setPage(p => p - 1)}
              >
                Précédent
              </Button>
              <span className="flex items-center px-4 text-sm text-muted-foreground">
                Page {page} sur {totalPages}
              </span>
              <Button
                variant="outline"
                disabled={page === totalPages}
                onClick={() => setPage(p => p + 1)}
              >
                Suivant
              </Button>
            </div>
          )}
        </div>
      </section>
    </main>
  );
};
