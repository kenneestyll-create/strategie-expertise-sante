import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { 
  ArrowRight, 
  FileSearch, 
  Shield, 
  Users, 
  BookOpen, 
  CheckCircle,
  Clock,
  MessageCircle,
  Train,
  Bus,
  Stethoscope,
  Phone
} from 'lucide-react';

export const ServicesPage = () => {
  const services = [
    {
      icon: FileSearch,
      title: "Analyse de dossier médical et administratif",
      description: "Je passe en revue l'ensemble de vos documents : certificats médicaux, rapports d'expertise, courriers de la CPAM, contrats d'assurance. L'objectif est de comprendre votre situation dans sa globalité et d'identifier les points forts et les failles de votre dossier.",
      includes: [
        "Lecture complète de votre dossier",
        "Identification des documents manquants",
        "Repérage des incohérences ou erreurs",
        "Recommandations personnalisées"
      ],
      duration: "Selon la complexité du dossier"
    },
    {
      icon: Shield,
      title: "Préparation aux expertises médicales",
      description: "L'expertise médicale est souvent un moment stressant et décisif. Je vous aide à vous y préparer : quoi apporter, comment présenter vos symptômes, quels pièges éviter, et comment rester serein face à l'expert.",
      includes: [
        "Simulation d'entretien d'expertise",
        "Liste des documents à préparer",
        "Conseils sur la présentation de vos symptômes",
        "Aide à la rédaction de vos observations"
      ],
      duration: "1 à 2 séances de préparation"
    },
    {
      icon: Users,
      title: "Stratégie AT/MP et CRRMP",
      description: "La reconnaissance d'une maladie professionnelle est un parcours semé d'embûches. Je vous guide dans les démarches : déclaration initiale, constitution du dossier, passage devant le CRRMP, et suivi de votre demande.",
      includes: [
        "Aide à la déclaration de maladie professionnelle",
        "Préparation du dossier CRRMP",
        "Suivi des délais et relances",
        "Conseils en cas de refus"
      ],
      duration: "Accompagnement sur plusieurs mois"
    },
    {
      icon: BookOpen,
      title: "Accompagnement assurantiel",
      description: "Face à votre assurance prévoyance ou emprunteur, vous n'êtes pas seul. Je vous aide à décrypter vos contrats, à comprendre les garanties (PTIA, invalidité), et à défendre vos droits en cas de refus d'indemnisation.",
      includes: [
        "Analyse de vos contrats d'assurance",
        "Décryptage des conditions générales",
        "Aide à la rédaction de courriers de contestation",
        "Conseils pour la négociation"
      ],
      duration: "Variable selon les procédures"
    }
  ];

  const process = [
    {
      step: "1",
      title: "Premier contact gratuit",
      description: "Première consultation téléphonique gratuite — 10 minutes pour évaluer votre situation."
    },
    {
      step: "2",
      title: "Analyse de votre dossier",
      description: "Envoi de vos documents, que j'étudie en détail. Je prépare un compte-rendu avec mes observations."
    },
    {
      step: "3",
      title: "Plan d'action personnalisé",
      description: "Nous définissons ensemble les étapes à suivre, adaptées à votre situation et vos priorités."
    },
    {
      step: "4",
      title: "Accompagnement continu",
      description: "Je reste disponible pour répondre à vos questions, relire vos courriers et vous soutenir dans vos démarches."
    }
  ];

  return (
    <main className="page-transition pt-20">
      <SEO title="Nos accompagnements" description="Accompagnement personnalisé en maladie professionnelle, accident du travail, MDPH et expertise médicale." path="/accompagnements" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Accompagnements</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="services-title">
              Des services adaptés à votre parcours
            </h1>
            <p className="text-lg text-muted-foreground mb-6">
              Chaque situation est unique. Je propose un accompagnement personnalisé, 
              à votre rythme, pour vous aider à traverser les épreuves administratives 
              et médicales liées à la maladie professionnelle ou à l'accident du travail.
            </p>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-accent" />
                <span>Consultation gratuite — 10 min</span>
              </div>
              <div className="flex items-center gap-2">
                <MessageCircle className="w-4 h-4 text-accent" />
                <span>Suivi personnalisé</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="section-padding" id="services-liste">
        <div className="max-w-7xl mx-auto">
          <div className="grid gap-8">
            {services.map((service, index) => (
              <Card 
                key={index} 
                className="overflow-hidden border-border"
                data-testid={`service-detail-${index}`}
              >
                <div className="grid lg:grid-cols-3">
                  <CardHeader className="lg:col-span-1 bg-muted/30 p-8">
                    <service.icon className="w-12 h-12 text-accent mb-4" strokeWidth={1.5} />
                    <CardTitle className="text-2xl mb-2">{service.title}</CardTitle>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mt-4">
                      <Clock className="w-4 h-4" />
                      <span>{service.duration}</span>
                    </div>
                  </CardHeader>
                  <CardContent className="lg:col-span-2 p-8">
                    <p className="text-muted-foreground mb-6">{service.description}</p>
                    <h4 className="font-semibold mb-4">Ce que comprend cet accompagnement :</h4>
                    <ul className="space-y-3">
                      {service.includes.map((item, i) => (
                        <li key={i} className="flex items-start gap-3">
                          <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Comment ça marche</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">
              Un accompagnement en 4 étapes
            </h2>
            <p className="text-muted-foreground">
              Simple, transparent et adapté à votre rythme.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {process.map((item, index) => (
              <div 
                key={index} 
                className="relative bg-background p-6 rounded-xl border border-border"
                data-testid={`process-step-${index}`}
              >
                <div className="absolute -top-4 left-6 w-8 h-8 bg-accent text-accent-foreground rounded-full flex items-center justify-center font-semibold text-sm">
                  {item.step}
                </div>
                <h3 className="font-semibold mt-4 mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Régimes Spéciaux Section */}
      <section id="regimes-speciaux" className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="text-sm font-medium text-accent uppercase tracking-wider">Spécialisation</span>
              <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-6">
                Régimes spéciaux
              </h2>
              <p className="text-primary-foreground/70 mb-6">
                Au-delà du régime général, j'accompagné également les agents relevant de régimes 
                spéciaux, qui ont des spécificités propres en matière de reconnaissance des 
                maladies professionnelles et d'accidents du travail.
              </p>
              <p className="text-primary-foreground/70 mb-8">
                Les démarches, les interlocuteurs et les droits peuvent différer significativement. 
                Mon expérience me permet de vous guider dans ces procédures particulières.
              </p>
            </div>
            <div className="space-y-4">
              <div className="bg-primary-foreground/10 p-6 rounded-xl border border-primary-foreground/10" data-testid="regime-sncf">
                <div className="flex items-center gap-4 mb-3">
                  <div className="w-12 h-12 bg-accent rounded-xl flex items-center justify-center">
                    <Train className="w-6 h-6 text-accent-foreground" strokeWidth={1.5} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">SNCF</h3>
                    <p className="text-sm text-primary-foreground/60">Cheminots et agents SNCF</p>
                  </div>
                </div>
                <ul className="space-y-2 ml-16">
                  <li className="flex items-start gap-2 text-sm text-primary-foreground/70">
                    <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    Spécificités du régime spécial SNCF
                  </li>
                  <li className="flex items-start gap-2 text-sm text-primary-foreground/70">
                    <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    Reconnaissance des maladies professionnelles
                  </li>
                  <li className="flex items-start gap-2 text-sm text-primary-foreground/70">
                    <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    Accompagnement des expertises
                  </li>
                </ul>
              </div>
              <div className="bg-primary-foreground/10 p-6 rounded-xl border border-primary-foreground/10" data-testid="regime-ratp">
                <div className="flex items-center gap-4 mb-3">
                  <div className="w-12 h-12 bg-accent rounded-xl flex items-center justify-center">
                    <Bus className="w-6 h-6 text-accent-foreground" strokeWidth={1.5} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">RATP</h3>
                    <p className="text-sm text-primary-foreground/60">Agents RATP</p>
                  </div>
                </div>
                <ul className="space-y-2 ml-16">
                  <li className="flex items-start gap-2 text-sm text-primary-foreground/70">
                    <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    Procédures propres au régime RATP
                  </li>
                  <li className="flex items-start gap-2 text-sm text-primary-foreground/70">
                    <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    Droits spécifiques des agents
                  </li>
                  <li className="flex items-start gap-2 text-sm text-primary-foreground/70">
                    <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    Aide à la constitution du dossier
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Médecin Conseil — Strategic CTA */}
      <section className="section-padding bg-accent/5 border-y border-accent/10" data-testid="services-médecin-conseil">
        <div className="max-w-4xl mx-auto text-center">
          <Stethoscope className="w-10 h-10 text-accent mx-auto mb-4" />
          <h2 className="text-2xl sm:text-3xl font-semibold mb-4">
            Besoin d'un médecin conseil adapté à votre situation ?
          </h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto leading-relaxed">
            Le choix du médecin conseil de victime est une décision stratégique majeure
            qui influence directement votre taux d'IPP et votre indemnisation.
            Ne laissez pas le hasard décider.
          </p>
          <Link to="/medecin-conseil">
            <Button size="lg" className="w-full sm:w-auto rounded-full px-6 sm:px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground whitespace-normal h-auto py-4 text-center leading-tight max-w-full" data-testid="services-médecin-conseil-cta">
              <Phone className="w-4 h-4 flex-shrink-0" />
              <span className="sm:hidden">Être accompagné</span>
              <span className="hidden sm:inline">Être accompagné dans le choix de mon médecin conseil</span>
              <ArrowRight className="w-4 h-4 flex-shrink-0" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Disclaimer Section */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto">
          <Card className="bg-muted/30 border-border">
            <CardContent className="p-8">
              <h3 className="text-xl font-semibold mb-4">Important à savoir</h3>
              <p className="text-muted-foreground mb-4">
                Je ne suis ni médecin, ni avocat, ni expert agréé. Mon accompagnement repose sur mon expérience 
                personnelle et ne se substitue pas aux conseils médicaux ou juridiques professionnels.
              </p>
              <p className="text-muted-foreground">
                Pour les questions juridiques complexes ou les procédures contentieuses, je vous orienterai 
                vers les professionnels compétents (avocats spécialisés, associations de victimes, etc.).
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
            Besoin d'un accompagnement personnalisé ?
          </h2>
          <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
            Contactez-moi pour une première consultation gratuite de 10 minutes. Nous verrons ensemble 
            comment je peux vous aider dans votre situation.
          </p>
          <Link to="/contact">
            <Button 
              size="lg" 
              className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="services-cta-button"
            >
              Prendre rendez-vous
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </main>
  );
};
