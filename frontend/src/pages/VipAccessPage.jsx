import { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { SEO } from '@/components/SEO';
import { toast } from 'sonner';
import { ShieldCheck, ArrowRight, Loader2, CheckCircle } from 'lucide-react';
import { useVip } from '@/context/VipContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const VipAccessPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refreshVip } = useVip();
  const token = searchParams.get('token') || '';
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [guestName, setGuestName] = useState('');

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!email || !token) {
      toast.error("Veuillez saisir votre email");
      return;
    }
    setLoading(true);
    try {
      const res = await axios.post(`${API}/vip/verify`, { token, email }, { withCredentials: true });
      setSuccess(true);
      setGuestName(res.data.name);
      toast.success(`Bienvenue ${res.data.name}`);
      await refreshVip();
      setTimeout(() => navigate('/'), 2000);
    } catch (err) {
      const msg = err.response?.data?.detail || "Accès refusé";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <main className="page-transition pt-20 min-h-screen flex items-center justify-center px-4">
        <SEO title="Accès partenaire" description="Accès partenaire sécurisé" path="/acces-invite" noindex={true} />
        <Card className="w-full max-w-md border-border" data-testid="vip-no-token">
          <CardContent className="p-8 text-center">
            <ShieldCheck className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h1 className="text-xl font-semibold mb-2">Accès partenaire</h1>
            <p className="text-sm text-muted-foreground">
              Cette page nécessite un lien d'invitation valide. Si vous avez reçu une invitation, utilisez le lien complet qui vous a été communiqué.
            </p>
          </CardContent>
        </Card>
      </main>
    );
  }

  if (success) {
    return (
      <main className="page-transition pt-20 min-h-screen flex items-center justify-center px-4">
        <SEO title="Accès partenaire" description="Accès partenaire sécurisé" path="/acces-invite" noindex={true} />
        <Card className="w-full max-w-md border-border" data-testid="vip-success">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-emerald-600" />
            </div>
            <h1 className="text-xl font-semibold mb-2">Bienvenue, {guestName}</h1>
            <p className="text-sm text-muted-foreground mb-4">
              Votre accès partenaire est activé. Vous allez être redirigé vers le site.
            </p>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-100 text-amber-800 text-xs font-medium">
              <ShieldCheck className="w-3.5 h-3.5" />
              Accès Partenaire VIP
            </div>
          </CardContent>
        </Card>
      </main>
    );
  }

  return (
    <main className="page-transition pt-20 min-h-screen flex items-center justify-center px-4">
      <SEO title="Accès partenaire" description="Accès partenaire sécurisé" path="/acces-invite" noindex={true} />
      <Card className="w-full max-w-md border-border" data-testid="vip-login-card">
        <CardHeader className="text-center">
          <div className="w-16 h-16 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <ShieldCheck className="w-8 h-8 text-accent" strokeWidth={1.5} />
          </div>
          <CardTitle className="text-xl">Accès partenaire sécurisé</CardTitle>
          <CardDescription>
            Confirmez votre identité pour accéder au site en tant que partenaire invité.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleVerify} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="vip-email">Votre adresse email</Label>
              <Input
                id="vip-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="votre@email.fr"
                required
                data-testid="vip-email-input"
              />
              <p className="text-xs text-muted-foreground">
                L'email doit correspondre exactement à celui communiqué lors de l'invitation.
              </p>
            </div>
            <Button
              type="submit"
              className="w-full rounded-lg gap-2"
              disabled={loading}
              data-testid="vip-verify-button"
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Vérification...</>
              ) : (
                <><ShieldCheck className="w-4 h-4" /> Confirmer mon accès</>
              )}
            </Button>
          </form>
          <p className="text-[10px] text-muted-foreground text-center mt-4">
            Accès personnel et confidentiel. Ne partagez pas ce lien.
          </p>
        </CardContent>
      </Card>
    </main>
  );
};

export default VipAccessPage;
