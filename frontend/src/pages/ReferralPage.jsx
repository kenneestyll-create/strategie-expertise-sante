import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { 
  Gift, 
  Copy, 
  CheckCircle, 
  ArrowRight, 
  Users, 
  Percent,
  Share2,
  Loader2
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ReferralPage = () => {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [referralCode, setReferralCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerateCode = async (e) => {
    e.preventDefault();
    if (!email) {
      toast.error("Veuillez entrer votre email");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/referral/create`, { email, name });
      setReferralCode(response.data.code);
      toast.success(response.data.message);
    } catch (error) {
      console.error('Referral error:', error);
      toast.error("Erreur lors de la création du code");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(referralCode);
    setCopied(true);
    toast.success("Code copié !");
    setTimeout(() => setCopied(false), 2000);
  };

  const steps = [
    {
      icon: Gift,
      title: "Obtenez votre code",
      description: "Entrez votre email pour recevoir votre code parrainage unique."
    },
    {
      icon: Share2,
      title: "Partagez-le",
      description: "Envoyez votre code à vos proches qui pourraient bénéficier de nos services."
    },
    {
      icon: Percent,
      title: "Profitez de la réduction",
      description: "Votre filleul bénéficie de 10% de réduction sur sa première prestation."
    }
  ];

  return (
    <main className="page-transition pt-20">
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Parrainage</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="referral-title">
              Parrainez vos proches
            </h1>
            <p className="text-lg text-muted-foreground">
              Vous avez bénéficié de nos services ? Faites-en profiter vos proches ! 
              Partagez votre code parrainage et offrez-leur <strong>10% de réduction</strong> sur 
              leur première prestation.
            </p>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-semibold mb-4">Comment ça marche ?</h2>
            <p className="text-muted-foreground">En 3 étapes simples</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {steps.map((step, index) => (
              <div 
                key={index} 
                className="text-center"
                data-testid={`referral-step-${index}`}
              >
                <div className="w-16 h-16 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <step.icon className="w-8 h-8 text-accent" strokeWidth={1.5} />
                </div>
                <h3 className="font-semibold text-lg mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </div>
            ))}
          </div>

          {/* Generate Code Form */}
          <div className="max-w-lg mx-auto">
            <Card className="border-border" data-testid="referral-card">
              <CardHeader className="text-center">
                <CardTitle className="flex items-center justify-center gap-2">
                  <Gift className="w-5 h-5 text-accent" />
                  Générer votre code
                </CardTitle>
                <CardDescription>
                  Entrez vos informations pour obtenir votre code parrainage unique.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!referralCode ? (
                  <form onSubmit={handleGenerateCode} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="referral-email">Email *</Label>
                      <Input
                        id="referral-email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="votre@email.fr"
                        required
                        data-testid="referral-email-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="referral-name">Nom (optionnel)</Label>
                      <Input
                        id="referral-name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Prénom Nom"
                        data-testid="referral-name-input"
                      />
                    </div>
                    <Button 
                      type="submit" 
                      className="w-full rounded-lg gap-2" 
                      disabled={loading}
                      data-testid="generate-referral-button"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Génération...
                        </>
                      ) : (
                        <>
                          <Gift className="w-4 h-4" />
                          Obtenir mon code
                        </>
                      )}
                    </Button>
                  </form>
                ) : (
                  <div className="text-center space-y-4" data-testid="referral-code-display">
                    <p className="text-sm text-muted-foreground">Votre code parrainage :</p>
                    <div className="flex items-center justify-center gap-3">
                      <span className="text-3xl font-bold tracking-widest text-foreground bg-muted px-6 py-3 rounded-xl">
                        {referralCode}
                      </span>
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={copyToClipboard}
                        data-testid="copy-referral-button"
                      >
                        {copied ? (
                          <CheckCircle className="w-4 h-4 text-green-600" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Partagez ce code avec vos proches. Ils bénéficieront de <strong>10% de réduction</strong> en 
                      le saisissant lors de leur paiement sur la page <Link to="/tarifs" className="text-accent underline">Tarifs</Link>.
                    </p>
                    <Button
                      variant="outline"
                      className="rounded-lg gap-2 mt-4"
                      onClick={() => { setReferralCode(''); setEmail(''); setName(''); }}
                      data-testid="new-referral-button"
                    >
                      Générer un autre code
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Advantages Section */}
      <section className="section-padding bg-card">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-semibold mb-4">Les avantages</h2>
          </div>
          <div className="grid sm:grid-cols-2 gap-6">
            <div className="bg-background p-6 rounded-xl border border-border" data-testid="advantage-referrer">
              <Users className="w-8 h-8 text-accent mb-3" strokeWidth={1.5} />
              <h3 className="font-semibold mb-2">Pour le parrain</h3>
              <p className="text-sm text-muted-foreground">
                Aidez vos proches à bénéficier d'un accompagnement de qualité à moindre coût.
              </p>
            </div>
            <div className="bg-background p-6 rounded-xl border border-border" data-testid="advantage-référée">
              <Percent className="w-8 h-8 text-accent mb-3" strokeWidth={1.5} />
              <h3 className="font-semibold mb-2">Pour le filleul</h3>
              <p className="text-sm text-muted-foreground">
                10% de réduction immédiate sur la première prestation choisie.
              </p>
            </div>
          </div>
          <div className="mt-8 p-4 bg-accent/10 rounded-xl text-center">
            <p className="text-sm text-foreground">
              De plus, bénéficiez de <strong>15% de réduction de fidélité</strong> dès votre deuxième prestation !
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-semibold mb-6">
            Besoin d'un accompagnement ?
          </h2>
          <p className="text-primary-foreground/70 mb-8">
            Première consultation gratuite — 10 minutes, sans engagement.
          </p>
          <Link to="/contact">
            <Button 
              size="lg" 
              className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="referral-cta-button"
            >
              Prendre contact
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </main>
  );
};
