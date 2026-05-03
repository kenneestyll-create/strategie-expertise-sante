import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { ChevronLeft, Send, Loader2 } from 'lucide-react';
import { useForumAuth } from '@/context/ForumAuthContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ForumNewTopicPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    category_id: searchParams.get('category') || '',
    title: '',
    content: ''
  });
  const { isAuthenticated, token, user } = useForumAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      toast.error("Connectez-vous pour créer un sujet");
      navigate('/forum/connexion');
      return;
    }
    fetchCategories();
  }, [isAuthenticated]);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/forum/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.category_id || !formData.title || !formData.content) {
      toast.error("Veuillez remplir tous les champs");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API}/forum/topics`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success("Sujet créé avec succès !");
      navigate(`/forum/sujet/${response.data.topic_id}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors de la création");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page-transition pt-20">
      <section className="section-padding">
        <div className="max-w-3xl mx-auto">
          <Link 
            to="/forum" 
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Retour au forum
          </Link>

          <Card>
            <CardHeader>
              <CardTitle>Créer un nouveau sujet</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6" data-testid="new-topic-form">
                <div className="space-y-2">
                  <Label htmlFor="category">Catégorie *</Label>
                  <Select 
                    value={formData.category_id} 
                    onValueChange={(value) => setFormData(prev => ({ ...prev, category_id: value }))}
                  >
                    <SelectTrigger data-testid="category-select">
                      <SelectValue placeholder="Choisir une catégorie" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((cat) => (
                        <SelectItem key={cat.id} value={cat.id}>
                          {cat.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="title">Titre du sujet *</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Un titre clair et descriptif"
                    required
                    data-testid="topic-title-input"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="content">Votre message *</Label>
                  <Textarea
                    id="content"
                    value={formData.content}
                    onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                    placeholder="Décrivez votre situation, posez vos questions..."
                    rows={8}
                    required
                    data-testid="topic-content-input"
                  />
                </div>

                {user?.is_anonymous && (
                  <div className="bg-accent/10 p-4 rounded-lg text-sm">
                    <p className="text-muted-foreground">
                      Votre message sera publié avec le badge <strong>"Anonyme"</strong> pour protéger votre identité.
                    </p>
                  </div>
                )}

                <div className="flex gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => navigate('/forum')}
                    className="rounded-full"
                  >
                    Annuler
                  </Button>
                  <Button 
                    type="submit" 
                    className="rounded-full gap-2"
                    disabled={loading}
                    data-testid="submit-topic-button"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Publication...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        Publier le sujet
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
};
