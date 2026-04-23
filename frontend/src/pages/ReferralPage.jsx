import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { SEO } from '@/components/SEO';
import { toast } from 'sonner';
import { 
  Gift, 
  Copy, 
  CheckCircle, 
  ArrowRight, 
  Users, 
  Percent,
  Share2,
  Loader2,
  ChevronDown
} from 'lucide-react';
import axios from 'axios';
import { useEffect } from 'react';

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
      <SEO title="Parrainage — Recommandez Stratégie Expertise Santé" description="Parrainez vos proches et offrez-leur 10% de réduction sur leur première prestation. Programme de parrainage simple et gratuit." path="/parrainage" />
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

      {/* SEO Content Section */}
      <section className="section-padding" data-testid="parrainage-seo-content">
        <div className="max-w-3xl mx-auto">
          <div className="prose prose-sm max-w-none text-foreground/80 space-y-4">
            <p>
              Le parrainage permet de recommander Stratégie Expertise Santé à une personne de votre entourage confrontée à une maladie professionnelle, un accident du travail ou une situation d'expertise médicale complexe.
            </p>
            <p>
              De nombreuses personnes rencontrent des difficultés pour faire valoir leurs droits face à des situations administratives et médicales souvent difficiles à comprendre.
            </p>
            <p>
              En partageant notre contact, vous permettez à ces personnes de bénéficier d'un accompagnement personnalisé, adapté à leur situation.
            </p>
            <p className="font-medium text-foreground">Le parrainage repose sur une démarche simple :</p>
            <ul className="space-y-2 list-none pl-0">
              <li className="flex items-start gap-2 text-sm">
                <span className="text-accent mt-0.5">–</span>
                <span>vous recommandez Stratégie Expertise Santé à une personne concernée</span>
              </li>
              <li className="flex items-start gap-2 text-sm">
                <span className="text-accent mt-0.5">–</span>
                <span>cette personne prend contact avec notre cabinet</span>
              </li>
              <li className="flex items-start gap-2 text-sm">
                <span className="text-accent mt-0.5">–</span>
                <span>nous analysons sa situation et proposons un accompagnement adapté</span>
              </li>
            </ul>
            <p>
              Notre priorité reste la qualité de l'accompagnement et la compréhension des enjeux spécifiques à chaque dossier.
            </p>
            <p>
              Chaque situation étant unique, nous étudions chaque demande avec attention et confidentialité.
            </p>
            <p>
              Pour toute recommandation ou demande d'information, vous pouvez <Link to="/contact" className="text-accent hover:underline">nous contacter directement</Link>.
            </p>
            <div className="mt-6 p-4 bg-accent/5 rounded-xl border border-accent/10">
              <p className="text-sm text-foreground">
                <strong>Rappel des avantages :</strong> votre filleul bénéficie de <strong>10% de réduction</strong> sur sa première prestation grâce à votre code parrainage. De plus, tous nos clients bénéficient de <strong>15% de réduction de fidélité</strong> dès leur deuxième prestation.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <ParrainageFAQ />

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


const parrainageFaqData = [
  {
    question: "À qui s'adresse le parrainage ?",
    answer: "Le parrainage s'adresse à toute personne souhaitant recommander un accompagnement dans le cadre d'une maladie professionnelle ou d'un accident du travail."
  },
  {
    question: "Le parrainage est-il obligatoire pour être accompagné ?",
    answer: "Non, toute personne peut contacter directement Stratégie Expertise Santé sans passer par un parrain."
  },
  {
    question: "Quels sont les avantages du parrainage ?",
    answer: "Le principal avantage est de permettre à une personne en difficulté d'être orientée vers un accompagnement adapté et spécialisé. Le filleul bénéficie de 10% de réduction sur sa première prestation, et tous les clients profitent de 15% de réduction de fidélité dès leur deuxième prestation."
  }
];

const ParrainageFAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);

  useEffect(() => {
    const existing = document.getElementById('parrainage-faq-schema');
    if (existing) existing.remove();
    const script = document.createElement('script');
    script.id = 'parrainage-faq-schema';
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": parrainageFaqData.map(f => ({
        "@type": "Question",
        "name": f.question,
        "acceptedAnswer": { "@type": "Answer", "text": f.answer }
      }))
    });
    document.head.appendChild(script);
    return () => { const el = document.getElementById('parrainage-faq-schema'); if (el) el.remove(); };
  }, []);

  return (
    <section className="section-padding bg-card" data-testid="parrainage-faq">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-semibold mb-6">Questions fréquentes</h2>
        <div className="space-y-3">
          {parrainageFaqData.map((faq, i) => (
            <div key={i} className="border border-border rounded-xl overflow-hidden">
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
                data-testid={`parrainage-faq-${i}`}
              >
                <span className="font-medium text-sm text-foreground pr-4">{faq.question}</span>
                <ChevronDown className={`w-4 h-4 text-muted-foreground shrink-0 transition-transform ${openIndex === i ? 'rotate-180' : ''}`} />
              </button>
              {openIndex === i && (
                <div className="px-4 pb-4">
                  <p className="text-sm text-muted-foreground leading-relaxed">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
