import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { 
  ArrowRight, 
  Stethoscope, 
  Scale, 
  FileText, 
  Users,
  UserCheck,
  Briefcase,
  Heart
} from 'lucide-react';

export const PartenairesPage = () => {
  const partenaires = [
    {
      icon: Stethoscope,
      title: "Médecins experts",
      description: "Médecins spécialisés dans l'évaluation du dommage corporel, pouvant réaliser des expertises ou contre-expertises médicales."
    },
    {
      icon: Scale,
      title: "Avocats spécialisés",
      description: "Avocats en droit de la sécurité sociale, droit du travail et réparation du préjudice corporel."
    },
    {
      icon: FileText,
      title: "Experts en assurance",
      description: "Professionnels spécialisés dans l'analyse des contrats d'assurance et la défense des assurés."
    },
    {
      icon: UserCheck,
      title: "Médecins conseils",
      description: "Médecins pouvant vous accompagner et vous conseiller dans vos démarches médicales."
    },
    {
      icon: Users,
      title: "Associations de victimes",
      description: "Structures d'aide et de soutien pour les victimes d'accidents du travail et de maladies professionnelles."
    },
    {
      icon: Briefcase,
      title: "Ergonomes et spécialistes",
      description: "Professionnels de l'adaptation du poste de travail et de l'accompagnement au retour à l'emploi."
    }
  ];

  return (
    <main className="page-transition pt-20">
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Réseau</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="partenaires-title">
              Un réseau de professionnels à votre service
            </h1>
            <p className="text-lg text-muted-foreground">
              Au fil de mon parcours, j'ai pu collaborer avec de nombreux professionnels 
              de santé et du domaine judiciaire. Ce réseau me permet aujourd'hui de vous 
              orienter vers les interlocuteurs les plus adaptés à votre situation.
            </p>
          </div>
        </div>
      </section>

      {/* Réseau Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-semibold mb-4">
              Les professionnels de notre réseau
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Selon vos besoins, je peux vous orienter vers différents types de professionnels 
              avec lesquels j'ai établi des relations de confiance.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {partenaires.map((partenaire, index) => (
              <Card 
                key={index} 
                className="card-lift border-border"
                data-testid={`partenaire-${index}`}
              >
                <CardContent className="p-6">
                  <div className="w-14 h-14 bg-accent/10 rounded-xl flex items-center justify-center mb-4">
                    <partenaire.icon className="w-7 h-7 text-accent" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-semibold text-xl mb-3">{partenaire.title}</h3>
                  <p className="text-muted-foreground text-sm">{partenaire.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Comment ça marche Section */}
      <section className="section-padding bg-card">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <Heart className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="text-3xl font-semibold mb-4">
              Comment fonctionne l'orientation ?
            </h2>
          </div>

          <div className="space-y-6">
            <div className="flex items-start gap-6">
              <div className="w-10 h-10 bg-accent text-accent-foreground rounded-full flex items-center justify-center flex-shrink-0 font-semibold">
                1
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">Analyse de votre situation</h3>
                <p className="text-muted-foreground">
                  Lors de notre échange, j'identifie les besoins spécifiques de votre dossier 
                  et les compétences professionnelles requises.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-6">
              <div className="w-10 h-10 bg-accent text-accent-foreground rounded-full flex items-center justify-center flex-shrink-0 font-semibold">
                2
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">Orientation personnalisée</h3>
                <p className="text-muted-foreground">
                  Je vous oriente vers le professionnel le plus adapté à votre situation 
                  parmi mon réseau de partenaires de confiance.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-6">
              <div className="w-10 h-10 bg-accent text-accent-foreground rounded-full flex items-center justify-center flex-shrink-0 font-semibold">
                3
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">Mise en relation</h3>
                <p className="text-muted-foreground">
                  Je facilite la mise en relation et reste disponible pour coordonner 
                  l'accompagnement si nécessaire.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Note importante */}
      <section className="section-padding">
        <div className="max-w-3xl mx-auto">
          <Card className="bg-muted/30 border-border">
            <CardContent className="p-8 text-center">
              <h3 className="text-xl font-semibold mb-4">Important</h3>
              <p className="text-muted-foreground">
                L'orientation vers ces professionnels se fait en fonction de votre situation 
                et de vos besoins. Chaque professionnel exerce de manière indépendante et 
                applique ses propres conditions d'intervention et tarifs.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
            Besoin d'être orienté vers un professionnel ?
          </h2>
          <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
            Contactez-moi pour discuter de votre situation et voir vers quel 
            professionnel je peux vous orienter.
          </p>
          <Link to="/contact">
            <Button 
              size="lg" 
              className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="partenaires-cta"
            >
              Me contacter
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </main>
  );
};
