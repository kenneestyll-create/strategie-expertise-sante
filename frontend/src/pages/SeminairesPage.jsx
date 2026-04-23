import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { 
  ArrowRight, 
  Users, 
  Building2, 
  Stethoscope, 
  GraduationCap,
  CheckCircle,
  Video,
  MapPin,
  Presentation
} from 'lucide-react';

export const SeminairesPage = () => {
  const publics = [
    { icon: Users, label: "Particuliers confrontés à ces démarches" },
    { icon: Building2, label: "Associations" },
    { icon: Stethoscope, label: "Professionnels de santé" },
    { icon: Building2, label: "Entreprises" }
  ];

  const objectifs = [
    "Comprendre les mécanismes des expertises médicales",
    "Mieux connaître les démarches administratives",
    "Anticiper certaines difficultés",
    "Améliorer l'accompagnement des personnes concernées"
  ];

  const formats = [
    { icon: MapPin, title: "En présentiel", description: "Interventions sur site, en salle de réunion ou amphithéâtre" },
    { icon: Video, title: "En visioconférence", description: "Sessions à distance via les outils de votre choix" },
    { icon: Presentation, title: "Conférences ou ateliers", description: "Format adapté selon vos objectifs et votre public" }
  ];

  return (
    <main className="page-transition pt-20">
      <SEO title="Séminaires et formations — AT/MP, expertise médicale" description="Séminaires et sessions d'information sur les accidents du travail, maladies professionnelles et expertises médicales. Formats adaptés aux professionnels." path="/seminaires" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Formation</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="seminaires-title">
              Séminaires et formations
            </h1>
            <p className="text-lg text-muted-foreground">
              Dans de nombreux domaines liés au handicap, aux accidents du travail ou aux 
              expertises médicales, l'information reste difficile d'accès. C'est pourquoi 
              je propose également des séminaires et sessions d'information.
            </p>
          </div>
        </div>
      </section>

      {/* Publics Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-semibold mb-6">À qui s'adressent ces formations ?</h2>
              <p className="text-muted-foreground mb-8">
                Ces sessions d'information sont destinées à tous ceux qui souhaitent 
                mieux comprendre les enjeux liés aux expertises médicales, aux accidents 
                du travail et aux démarches administratives.
              </p>
              <div className="grid sm:grid-cols-2 gap-4">
                {publics.map((item, index) => (
                  <div 
                    key={index} 
                    className="flex items-center gap-3 bg-card p-4 rounded-xl border border-border"
                    data-testid={`public-${index}`}
                  >
                    <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                      <item.icon className="w-5 h-5 text-accent" strokeWidth={1.5} />
                    </div>
                    <span className="font-medium text-sm">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/7688336/pexels-photo-7688336.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Formation en salle"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Objectifs Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-10">
              <GraduationCap className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
              <h2 className="text-3xl font-semibold mb-4">Objectifs des séminaires</h2>
              <p className="text-muted-foreground">
                Chaque session est conçue pour apporter des réponses concrètes et pratiques.
              </p>
            </div>

            <div className="space-y-4">
              {objectifs.map((objectif, index) => (
                <div 
                  key={index} 
                  className="flex items-start gap-4 bg-background p-5 rounded-xl border border-border"
                  data-testid={`objectif-${index}`}
                >
                  <CheckCircle className="w-6 h-6 text-accent flex-shrink-0" strokeWidth={1.5} />
                  <span className="text-lg">{objectif}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Formats Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-semibold mb-4">Formats d'intervention</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Ces interventions peuvent être organisées selon différents formats, 
              adaptés à vos besoins et contraintes.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {formats.map((format, index) => (
              <Card key={index} className="card-lift border-border text-center" data-testid={`format-${index}`}>
                <CardContent className="p-8">
                  <div className="w-16 h-16 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <format.icon className="w-8 h-8 text-accent" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-semibold text-xl mb-3">{format.title}</h3>
                  <p className="text-muted-foreground">{format.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="text-center mt-10">
            <p className="text-muted-foreground mb-6">
              Un programme détaillé pourra être proposé en fonction de vos besoins spécifiques.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
            Organiser une session de formation
          </h2>
          <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
            Vous souhaitez organiser un séminaire ou une formation pour votre structure ? 
            Contactez-moi pour discuter de vos besoins et établir un programme adapté.
          </p>
          <Link to="/contact">
            <Button 
              size="lg" 
              className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="seminaires-cta"
            >
              Demander un devis
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </main>
  );
};
