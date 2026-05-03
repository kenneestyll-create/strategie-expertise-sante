import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { toast } from 'sonner';
import { Heart, LogIn, Loader2, ArrowLeft } from 'lucide-react';
import { useForumAuth } from '@/context/ForumAuthContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ForumLoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const { login } = useForumAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error("Veuillez remplir tous les champs");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/forum/login`, { email, password });
      
      login(response.data.access_token, {
        id: response.data.user_id,
        pseudo: response.data.pseudo,
        is_anonymous: response.data.is_anonymous
      });
      
      toast.success(`Bienvenue, ${response.data.pseudo} !`);
      navigate('/forum');
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.response?.data?.detail || "Email ou mot de passe incorrect");
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
            <CardTitle className="text-2xl">Connexion</CardTitle>
            <CardDescription>
              Accédez à votre compte forum
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-4" data-testid="forum-login-form">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="votre@email.fr"
                  required
                  data-testid="forum-login-email"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Mot de passe</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  data-testid="forum-login-password"
                />
              </div>

              <Button 
                type="submit" 
                className="w-full rounded-lg gap-2"
                disabled={loading}
                data-testid="forum-login-submit"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Connexion...
                  </>
                ) : (
                  <>
                    <LogIn className="w-4 h-4" />
                    Se connecter
                  </>
                )}
              </Button>
            </form>

            <p className="text-center text-sm text-muted-foreground mt-6">
              Pas encore de compte ?{' '}
              <Link to="/forum/inscription" className="text-accent hover:underline">
                S'inscrire
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </main>
  );
};
