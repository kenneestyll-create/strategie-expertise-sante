import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { 
  ArrowRight, 
  Home, 
  BadgeCheck, 
  CreditCard, 
  Users,
  CheckCircle,
  FileText,
  Heart,
  Compass
} from 'lucide-react';

export const MDPHPage = () => {
  const aides = [
    { icon: CreditCard, title: "AAH", description: "Allocation aux Adultes Handicapés" },
    { icon: BadgeCheck, title: "RQTH", description: "Reconnaissance de la Qualité de Travailleur Handicapé" },
    { icon: CreditCard, title: "CMI", description: "Carte mobilité inclusion (invalidité, priorité, stationnement)" },
    { icon: Users, title: "Aide humaine", description: "Aide humaine ou tierce personne" }
  ];

  const avantages = [
    "Faire reconnaître officiellement un handicap",
    "Obtenir des aides financières ou humaines",
    "Faciliter certaines démarches administratives"
  ];

  const accompagnement = [
    { icon: Compass, text: "Mieux comprendre les démarches MDPH" },
    { icon: FileText, text: "Analyser les droits possibles" },
    { icon: Users, text: "Orienter vers les professionnels adaptés si nécessaire" }
  ];

  return (
    <main className="page-transition pt-20">
      <SEO title="MDPH — Droits et démarches" description="Guide complet MDPH : démarches, droits, AAH, RQTH. Accompagnement personnalisé pour votre dossier handicap." path="/mdph" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Vos droits</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="mdph-title">
              MDPH : comprendre vos droits et vos démarches
            </h1>
            <p className="text-lg text-muted-foreground">
              La MDPH (Maison Départementale des Personnes Handicapées) accompagné les personnes 
              en situation de handicap dans leurs démarches administratives et l'accès à leurs droits.
            </p>
          </div>
        </div>
      </section>

      {/* Aides Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-semibold mb-4">Principales aides possibles</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              La MDPH peut vous permettre d'accéder à différentes aides et reconnaissances.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {aides.map((aide, index) => (
              <Card 
                key={index} 
                className="card-lift border-border text-center"
                data-testid={`aide-${index}`}
              >
                <CardContent className="p-6">
                  <div className="w-14 h-14 bg-accent/10 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <aide.icon className="w-7 h-7 text-accent" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-semibold text-xl mb-2">{aide.title}</h3>
                  <p className="text-sm text-muted-foreground">{aide.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pourquoi Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-semibold mb-6">
                Pourquoi constituer un dossier MDPH
              </h2>
              <p className="text-muted-foreground mb-6">
                Un dossier MDPH permet notamment :
              </p>
              <div className="space-y-4">
                {avantages.map((avantage, index) => (
                  <div 
                    key={index} 
                    className="flex items-start gap-3 bg-background p-4 rounded-xl"
                    data-testid={`avantage-${index}`}
                  >
                    <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    <span className="font-medium">{avantage}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/7176319/pexels-photo-7176319.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Démarches administratives"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Accompagnement Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <Heart className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="text-3xl font-semibold mb-4">
              Accompagnement
            </h2>
            <p className="text-primary-foreground/70">
              Je propose un accompagnement afin de :
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-6 mb-10">
            {accompagnement.map((item, index) => (
              <div 
                key={index} 
                className="bg-primary-foreground/10 rounded-xl p-6 text-center"
                data-testid={`accompagnement-mdph-${index}`}
              >
                <item.icon className="w-10 h-10 text-accent mx-auto mb-4" strokeWidth={1.5} />
                <p className="text-primary-foreground">{item.text}</p>
              </div>
            ))}
          </div>

          <div className="text-center">
            <Link to="/contact">
              <Button 
                size="lg" 
                className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
                data-testid="mdph-cta-button"
              >
                Me contacter
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
};
