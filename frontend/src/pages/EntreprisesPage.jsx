import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { 
  ArrowRight, 
  Building2, 
  Users, 
  FileText, 
  MessageSquare,
  CheckCircle,
  Target,
  Lightbulb,
  Shield
} from 'lucide-react';

export const EntreprisesPage = () => {
  const enjeux = [
    "Mieux comprendre les mécanismes des accidents du travail et maladies professionnelles",
    "Anticiper certaines situations complexes",
    "Améliorer la gestion des dossiers sensibles",
    "Favoriser un dialogue plus constructif avec les salariés concernés"
  ];

  const formats = [
    { 
      icon: Users, 
      title: "Sessions d'information pour les équipes RH",
      description: "Formation pratique pour vos équipes ressources humaines sur les enjeux AT/MP."
    },
    { 
      icon: MessageSquare, 
      title: "Conférences de sensibilisation",
      description: "Interventions pour sensibiliser vos équipes aux problématiques du handicap au travail."
    },
    { 
      icon: FileText, 
      title: "Analyse de situations spécifiques",
      description: "Étude de cas concrets rencontrés dans votre structure."
    },
    { 
      icon: Target, 
      title: "Accompagnement sur-mesure",
      description: "Suivi personnalisé adapté aux besoins spécifiques de votre organisation."
    }
  ];

  return (
    <main className="page-transition pt-20">
      <SEO title="Entreprises — Sensibilisation AT/MP et maladies professionnelles" description="Formations et sensibilisation pour les entreprises : gestion des accidents du travail, maladies professionnelles, prévention des risques. Formats adaptés à vos équipes." path="/entreprises" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="text-sm font-medium text-accent uppercase tracking-wider">Entreprises</span>
              <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="entreprises-title">
                Accompagnement des entreprises
              </h1>
              <p className="text-lg text-muted-foreground mb-6">
                Les accidents du travail, les maladies professionnelles et les situations 
                d'invalidité représentent un enjeu humain, social et économique important 
                pour les entreprises.
              </p>
              <p className="text-muted-foreground">
                Je propose un accompagnement destiné aux structures souhaitant mieux 
                appréhender ces problématiques et améliorer leur gestion des situations sensibles.
              </p>
            </div>
            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Réunion d'entreprise"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Enjeux Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-10">
              <Lightbulb className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
              <h2 className="text-3xl font-semibold mb-4">
                Pourquoi faire appel à cet accompagnement ?
              </h2>
              <p className="text-muted-foreground">
                Un accompagnement pour mieux comprendre et gérer les situations complexes.
              </p>
            </div>

            <div className="space-y-4">
              {enjeux.map((enjeu, index) => (
                <div 
                  key={index} 
                  className="flex items-start gap-4 bg-card p-5 rounded-xl border border-border"
                  data-testid={`enjeu-${index}`}
                >
                  <CheckCircle className="w-6 h-6 text-accent flex-shrink-0" strokeWidth={1.5} />
                  <span className="text-lg">{enjeu}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Formats Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-semibold mb-4">
              Différentes formes d'accompagnement
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Cet accompagnement peut prendre différentes formes selon vos besoins.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 gap-6">
            {formats.map((format, index) => (
              <Card key={index} className="card-lift border-border" data-testid={`format-entreprise-${index}`}>
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center flex-shrink-0">
                      <format.icon className="w-6 h-6 text-accent" strokeWidth={1.5} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg mb-2">{format.title}</h3>
                      <p className="text-muted-foreground text-sm">{format.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Objectif Section */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto text-center">
          <Shield className="w-12 h-12 text-accent mx-auto mb-6" strokeWidth={1.5} />
          <h2 className="text-3xl font-semibold mb-6">
            Un objectif : mieux comprendre pour mieux accompagner
          </h2>
          <p className="text-muted-foreground text-lg mb-8">
            L'objectif est de contribuer à une meilleure compréhension des enjeux humains 
            et administratifs liés à ces situations, pour permettre aux entreprises de 
            mieux accompagner leurs collaborateurs tout en sécurisant leurs pratiques.
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <Building2 className="w-12 h-12 text-accent mx-auto mb-6" strokeWidth={1.5} />
          <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
            Vous êtes une entreprise ?
          </h2>
          <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
            Contactez-moi pour discuter de vos besoins et voir comment je peux 
            accompagner votre structure dans ces problématiques.
          </p>
          <Link to="/contact">
            <Button 
              size="lg" 
              className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="entreprises-cta"
            >
              Nous contacter
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </main>
  );
};
