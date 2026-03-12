import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { 
  ArrowRight, 
  FileSearch, 
  Shield, 
  Users, 
  BookOpen, 
  Heart, 
  CheckCircle, 
  Lightbulb,
  Sparkles,
  Stethoscope,
  Scale,
  Building2,
  Star
} from 'lucide-react';

export const HomePage = () => {
  const services = [
    {
      icon: FileSearch,
      title: "Analyse de dossier",
      description: "Étude approfondie de votre situation médicale, administrative et assurantielle."
    },
    {
      icon: Shield,
      title: "Préparation aux expertises",
      description: "Accompagnement personnalisé pour aborder sereinement vos expertises médicales."
    },
    {
      icon: Users,
      title: "Stratégie AT/MP",
      description: "Conseil sur les démarches de reconnaissance en maladie professionnelle."
    },
    {
      icon: BookOpen,
      title: "Aide assurantielle",
      description: "Décryptage de vos contrats et accompagnement dans vos relations avec les assureurs."
    }
  ];

  const values = [
    "Une écoute bienveillante et sans jugement",
    "Des conseils clairs, sans jargon",
    "Une expérience vécue de l'intérieur",
    "Un accompagnement à votre rythme"
  ];

  const innovationPoints = [
    "Un accompagnement personnalisé",
    "Une expertise issue de l'expérience du terrain",
    "Une approche humaine et pédagogique",
    "Un service encore peu développé en France"
  ];

  const partenaires = [
    { icon: Stethoscope, title: "Médecins experts" },
    { icon: Scale, title: "Avocats spécialisés" },
    { icon: FileSearch, title: "Experts en assurance" },
    { icon: Building2, title: "Associations de victimes" }
  ];

  return (
    <main className="page-transition">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center pt-20">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ 
            backgroundImage: `url('https://images.unsplash.com/photo-1598016677484-ad34c3fd766e?auto=format&fit=crop&w=1920&q=80')`,
          }}
        />
        <div className="absolute inset-0 hero-overlay" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="max-w-3xl">
            {/* Badge innovant */}
            <div className="inline-flex items-center gap-2 bg-accent/10 text-accent px-4 py-2 rounded-full mb-6">
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-medium">Service pionnier en France</span>
            </div>
            
            <h1 
              className="text-4xl sm:text-5xl lg:text-6xl font-semibold text-foreground leading-tight mb-6"
              data-testid="hero-title"
            >
              Vous n'êtes plus seul face à la maladie professionnelle
            </h1>
            <p className="text-base sm:text-lg text-muted-foreground mb-8 max-w-2xl">
              Un service innovant dédié à l'accompagnement des personnes confrontées à des démarches 
              complexes liées au handicap, aux expertises médicales et aux procédures d'assurance.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/contact">
                <Button 
                  size="lg" 
                  className="btn-scale rounded-full px-8 gap-2"
                  data-testid="hero-cta-primary"
                >
                  Prendre rendez-vous
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Link to="/a-propos">
                <Button 
                  variant="outline" 
                  size="lg" 
                  className="rounded-full px-8"
                  data-testid="hero-cta-secondary"
                >
                  Mon parcours
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Approche Innovante Section */}
      <section className="section-padding bg-accent/5">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 text-accent mb-4">
                <Lightbulb className="w-5 h-5" strokeWidth={1.5} />
                <span className="text-sm font-medium uppercase tracking-wider">Innovation</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
                Une approche innovante
              </h2>
              <p className="text-muted-foreground mb-6">
                Ce service repose sur une approche encore peu développée en France : 
                <strong> l'accompagnement stratégique et pédagogique</strong> des personnes 
                confrontées à des procédures médicales, administratives ou assurantielles complexes.
              </p>
              <p className="text-muted-foreground mb-8">
                L'objectif est de permettre aux personnes concernées de mieux comprendre leur 
                situation, leurs droits et les étapes importantes de leur parcours. Cette approche 
                vise à offrir un accompagnement humain, accessible et structuré dans des démarches 
                souvent difficiles à appréhender.
              </p>
              <div className="grid sm:grid-cols-2 gap-3">
                {innovationPoints.map((point, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    <span className="text-sm text-foreground">{point}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="aspect-square rounded-2xl overflow-hidden">
                <img 
                  src="https://images.pexels.com/photos/7176026/pexels-photo-7176026.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Approche innovante"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="absolute -bottom-4 -right-4 bg-foreground text-primary-foreground p-4 rounded-xl shadow-lg">
                <p className="text-2xl font-bold">+4 ans</p>
                <p className="text-sm text-primary-foreground/70">d'expérience terrain</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            <div>
              <span className="text-sm font-medium text-accent uppercase tracking-wider">Notre mission</span>
              <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-6">
                Comprendre, accompagner, défendre vos droits
              </h2>
              <p className="text-muted-foreground mb-6">
                Quand la maladie ou l'accident survient dans le cadre professionnel, le parcours administratif 
                peut sembler insurmontable. Entre les formulaires, les expertises, les délais et le jargon technique, 
                beaucoup abandonnent leurs droits.
              </p>
              <p className="text-muted-foreground mb-8">
                <strong>Accompagn'Santé</strong> est né de cette réalité vécue. Mon rôle : vous aider à comprendre 
                chaque étape, à préparer vos dossiers et à défendre vos intérêts face aux organismes et assureurs.
              </p>
              <div className="space-y-3">
                {values.map((value, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    <span className="text-foreground">{value}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="aspect-[4/5] rounded-2xl overflow-hidden">
                <img 
                  src="https://images.pexels.com/photos/7111462/pexels-photo-7111462.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Accompagnement personnalisé"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="absolute -bottom-6 -left-6 bg-accent text-accent-foreground p-6 rounded-xl shadow-lg max-w-xs">
                <Heart className="w-8 h-8 mb-2" strokeWidth={1.5} />
                <p className="text-sm font-medium">
                  "Une personne blessée par le système qui aide d'autres blessés à se relever."
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Preview */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Accompagnements</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">
              Comment puis-je vous aider ?
            </h2>
            <p className="text-muted-foreground">
              Des services adaptés à votre situation, pour vous guider pas à pas dans vos démarches.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {services.map((service, index) => (
              <Card 
                key={index} 
                className="card-lift border-border bg-card"
                data-testid={`service-card-${index}`}
              >
                <CardContent className="p-6">
                  <service.icon className="w-10 h-10 text-accent mb-4" strokeWidth={1.5} />
                  <h3 className="font-semibold text-lg mb-2">{service.title}</h3>
                  <p className="text-sm text-muted-foreground">{service.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="text-center mt-10">
            <Link to="/accompagnements">
              <Button variant="outline" className="rounded-full px-8 gap-2" data-testid="services-link">
                Découvrir tous les accompagnements
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Réseau Partenaires Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="text-sm font-medium text-accent uppercase tracking-wider">Réseau</span>
              <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-6">
                Un réseau de professionnels partenaires
              </h2>
              <p className="text-muted-foreground mb-6">
                Au cours de mon parcours, j'ai collaboré avec de nombreux professionnels de santé 
                et du domaine judiciaire. Ce réseau me permet aujourd'hui de vous orienter vers 
                les interlocuteurs les plus adaptés à votre situation.
              </p>
              <div className="grid grid-cols-2 gap-4 mb-8">
                {partenaires.map((item, index) => (
                  <div key={index} className="flex items-center gap-3 bg-card p-4 rounded-xl border border-border">
                    <item.icon className="w-6 h-6 text-accent" strokeWidth={1.5} />
                    <span className="text-sm font-medium">{item.title}</span>
                  </div>
                ))}
              </div>
              <Link to="/partenaires">
                <Button variant="outline" className="rounded-full px-6 gap-2">
                  Découvrir le réseau
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img 
                  src="https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Réseau de partenaires"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Avis Section Preview */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto text-center">
          <Star className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
          <h2 className="text-3xl font-semibold mb-4">Ce qu'ils en disent</h2>
          <p className="text-muted-foreground mb-8">
            Découvrez les témoignages des personnes que j'ai accompagnées.
          </p>
          <Link to="/avis">
            <Button variant="outline" className="rounded-full px-8 gap-2">
              Voir les témoignages
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
            Besoin d'aide pour y voir plus clair ?
          </h2>
          <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
            Chaque situation est unique. Contactez-moi pour un premier échange gratuit 
            et sans engagement. Ensemble, nous verrons comment je peux vous accompagner.
          </p>
          <Link to="/contact">
            <Button 
              size="lg" 
              variant="secondary"
              className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="cta-contact-button"
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
