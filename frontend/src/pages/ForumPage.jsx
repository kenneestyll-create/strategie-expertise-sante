import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  MessageSquare, 
  Users, 
  AlertTriangle, 
  Stethoscope, 
  FileSearch, 
  Heart, 
  Building, 
  Shield,
  ChevronRight,
  Plus,
  LogIn
} from 'lucide-react';
import { useForumAuth } from '@/context/ForumAuthContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const iconMap = {
  AlertTriangle,
  Stethoscope,
  FileSearch,
  Heart,
  Building,
  Shield
};

export const ForumPage = () => {
  const [categories, setCategories] = useState([]);
  const [recentTopics, setRecentTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated, user } = useForumAuth();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [catRes, topicsRes] = await Promise.all([
        axios.get(`${API}/forum/categories`),
        axios.get(`${API}/forum/topics?limit=5`)
      ]);
      setCategories(catRes.data);
      setRecentTopics(topicsRes.data.topics || []);
    } catch (error) {
      console.error('Error fetching forum data:', error);
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
    
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
  };

  return (
    <main className="page-transition pt-20">
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="max-w-2xl">
              <span className="text-sm font-medium text-accent uppercase tracking-wider">Communauté</span>
              <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="forum-title">
                Forum d'entraide
              </h1>
              <p className="text-lg text-muted-foreground">
                Échangez avec d'autres personnes confrontées aux mêmes situations. 
                Partagez vos expériences, posez vos questions, entraidez-vous.
              </p>
              <p className="text-sm text-muted-foreground mt-4 flex items-center gap-2">
                <Shield className="w-4 h-4 text-accent" />
                Inscription anonyme possible pour protéger votre identité
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-3">
              {isAuthenticated ? (
                <Link to="/forum/nouveau">
                  <Button size="lg" className="rounded-full px-8 gap-2" data-testid="new-topic-button">
                    <Plus className="w-4 h-4" />
                    Nouveau sujet
                  </Button>
                </Link>
              ) : (
                <>
                  <Link to="/forum/inscription">
                    <Button size="lg" className="rounded-full px-8 gap-2" data-testid="register-button">
                      <Users className="w-4 h-4" />
                      S'inscrire
                    </Button>
                  </Link>
                  <Link to="/forum/connexion">
                    <Button size="lg" variant="outline" className="rounded-full px-8 gap-2" data-testid="login-button">
                      <LogIn className="w-4 h-4" />
                      Se connecter
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-semibold mb-8">Catégories</h2>
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.map((category) => {
              const IconComponent = iconMap[category.icon] || MessageSquare;
              return (
                <Link 
                  key={category.id} 
                  to={`/forum/categorie/${category.slug}`}
                  data-testid={`category-${category.slug}`}
                >
                  <Card className="card-lift h-full border-border hover:border-accent/50 transition-colors">
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center flex-shrink-0">
                          <IconComponent className="w-6 h-6 text-accent" strokeWidth={1.5} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold mb-1">{category.name}</h3>
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {category.description}
                          </p>
                        </div>
                        <ChevronRight className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Recent Topics Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-semibold">Discussions récentes</h2>
            <Link to="/forum/tous">
              <Button variant="outline" className="rounded-full">
                Voir tout
              </Button>
            </Link>
          </div>

          {loading ? (
            <div className="text-center py-12 text-muted-foreground">
              Chargement...
            </div>
          ) : recentTopics.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare className="w-12 h-12 text-muted-foreground/50 mx-auto mb-4" />
              <p className="text-muted-foreground">
                Aucune discussion pour le moment. Soyez le premier à créer un sujet !
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentTopics.map((topic) => (
                <Link 
                  key={topic.id} 
                  to={`/forum/sujet/${topic.id}`}
                  data-testid={`topic-${topic.id}`}
                >
                  <Card className="hover:bg-muted/30 transition-colors">
                    <CardContent className="p-4">
                      <div className="flex items-start gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold truncate">{topic.title}</h3>
                            {topic.is_anonymous && (
                              <Badge variant="secondary" className="text-xs">Anonyme</Badge>
                            )}
                            {topic.is_pinned && (
                              <Badge className="text-xs bg-accent">Épinglé</Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-1 mb-2">
                            {topic.content}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span>Par {topic.author_pseudo}</span>
                            <span>{formatDate(topic.created_at)}</span>
                            <span>{topic.replies_count} réponse{topic.replies_count !== 1 ? 's' : ''}</span>
                            <span>{topic.views} vue{topic.views !== 1 ? 's' : ''}</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Rules Section */}
      <section className="section-padding">
        <div className="max-w-3xl mx-auto">
          <Card className="bg-muted/30 border-border">
            <CardHeader>
              <CardTitle className="text-lg">Règles du forum</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <p>• Restez respectueux et bienveillant envers les autres membres</p>
              <p>• Ne partagez pas d'informations personnelles identifiantes</p>
              <p>• Les conseils partagés ne remplacent pas un avis médical ou juridique professionnel</p>
              <p>• Signalement tout contenu inapproprié aux modérateurs</p>
              <p>• L'anonymat est protégé - ne tentez pas d'identifier les membres anonymes</p>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
};
