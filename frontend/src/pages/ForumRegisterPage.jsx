import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';
import { Heart, Users, Shield, Loader2, ArrowLeft } from 'lucide-react';
import { useForumAuth } from '@/context/ForumAuthContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ForumRegisterPage = () => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    pseudo: '',
    email: '',
    password: '',
    confirmPassword: '',
    acceptRules: false
  });
  const [activeTab, setActiveTab] = useState('email');
  
  const navigate = useNavigate();
  const { login } = useForumAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.pseudo) {
      toast.error("Veuillez choisir un pseudonyme");
      return;
    }
    
    if (!formData.acceptRules) {
      toast.error("Veuillez accepter les règles du forum");
      return;
    }
    
    if (activeTab === 'email') {
      if (!formData.email || !formData.password) {
        toast.error("Email et mot de passe requis");
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        toast.error("Les mots de passe ne correspondent pas");
        return;
      }
      if (formData.password.length < 6) {
        toast.error("Le mot de passe doit contenir au moins 6 caractères");
        return;
      }
    }

    setLoading(true);
    try {
      const payload = {
        pseudo: formData.pseudo,
        is_anonymous: activeTab === 'anonymous'
      };
      
      if (activeTab === 'email') {
        payload.email = formData.email;
        payload.password = formData.password;
      }
      
      const response = await axios.post(`${API}/forum/register`, payload);
      
      login(response.data.access_token, {
        id: response.data.user_id,
        pseudo: response.data.pseudo,
        is_anonymous: response.data.is_anonymous
      });
      
      toast.success("Inscription réussie ! Bienvenue sur le forum.");
      navigate('/forum');
    } catch (error) {
      console.error('Registration error:', error);
      toast.error(error.response?.data?.detail || "Erreur lors de l'inscription");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-background flex items-center justify-center p-4 pt-24">
      <div className="w-full max-w-md">
        <Link 
          to="/forum" 
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour au forum
        </Link>

        <Card className="border-border">
          <CardHeader className="text-center pb-2">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Heart className="w-8 h-8 text-accent" strokeWidth={1.5} />
              <span className="font-semibold text-xl" style={{ fontFamily: "'Playfair Display', serif" }}>
                Forum Stratégie & Expertise Santé
              </span>
            </div>
            <CardTitle className="text-2xl">Inscription</CardTitle>
            <CardDescription>
              Rejoignez notre communauté d'entraide
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger value="email" className="gap-2">
                  <Users className="w-4 h-4" />
                  Avec email
                </TabsTrigger>
                <TabsTrigger value="anonymous" className="gap-2">
                  <Shield className="w-4 h-4" />
                  Anonyme
                </TabsTrigger>
              </TabsList>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="pseudo">Pseudonyme *</Label>
                  <Input
                    id="pseudo"
                    value={formData.pseudo}
                    onChange={(e) => setFormData(prev => ({ ...prev, pseudo: e.target.value }))}
                    placeholder="Votre pseudonyme"
                    required
                    data-testid="register-pseudo"
                  />
                  <p className="text-xs text-muted-foreground">
                    Ce nom sera affiché sur vos messages
                  </p>
                </div>

                <TabsContent value="email" className="space-y-4 mt-0">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="votre@email.fr"
                      data-testid="register-email"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Mot de passe *</Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                      placeholder="••••••••"
                      data-testid="register-password"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirmer le mot de passe *</Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      value={formData.confirmPassword}
                      onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                      placeholder="••••••••"
                      data-testid="register-confirm-password"
                    />
                  </div>
                </TabsContent>

                <TabsContent value="anonymous" className="mt-0">
                  <Card className="bg-accent/5 border-accent/20">
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <Shield className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                        <div className="text-sm">
                          <p className="font-medium text-foreground mb-1">Inscription anonyme</p>
                          <p className="text-muted-foreground">
                            Vous pourrez participer aux discussions sans fournir d'email. 
                            Attention : si vous perdez l'accès à ce navigateur, vous ne pourrez 
                            pas récupérer votre compte.
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <div className="flex items-start gap-2">
                  <Checkbox
                    id="acceptRules"
                    checked={formData.acceptRules}
                    onCheckedChange={(checked) => setFormData(prev => ({ ...prev, acceptRules: checked }))}
                    data-testid="accept-rules"
                  />
                  <Label htmlFor="acceptRules" className="text-sm text-muted-foreground leading-tight">
                    J'accepte les règles du forum et je m'engage à respecter les autres membres
                  </Label>
                </div>

                <Button 
                  type="submit" 
                  className="w-full rounded-lg gap-2"
                  disabled={loading}
                  data-testid="register-submit"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Inscription...
                    </>
                  ) : (
                    <>
                      <Users className="w-4 h-4" />
                      S'inscrire
                    </>
                  )}
                </Button>
              </form>
            </Tabs>

            <p className="text-center text-sm text-muted-foreground mt-6">
              Déjà inscrit ?{' '}
              <Link to="/forum/connexion" className="text-accent hover:underline">
                Se connecter
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </main>
  );
};
