import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { 
  ArrowRight, 
  Shield, 
  FileText, 
  Scale, 
  Users,
  CheckCircle,
  AlertCircle,
  BookOpen,
  Search,
  Phone,
  Briefcase,
  HelpCircle
} from 'lucide-react';

export const ProtectionJuridiquePage = () => {
  const etapesActivation = [
    {
      step: "1",
      title: "Identifiez vos contrats",
      description: "La protection juridique peut être incluse dans votre assurance habitation, auto, santé ou dans un contrat dédié. Vérifiez l'ensemble de vos contrats."
    },
    {
      step: "2",
      title: "Consultez les garanties",
      description: "Lisez les conditions générales pour comprendre les domaines couverts, les plafonds de prise en charge et les exclusions éventuelles."
    },
    {
      step: "3",
      title: "Déclarez votre litige",
      description: "Contactez votre assureur par écrit (courrier recommandé ou espace client) en exposant clairement votre situation et le litige concerné."
    },
    {
      step: "4",
      title: "Constituez votre dossier",
      description: "Rassemblez tous les documents utiles : contrats, courriers, certificats médicaux, décisions administratives..."
    },
    {
      step: "5",
      title: "Suivez votre dossier",
      description: "Restez en contact avec votre assureur et l'avocat désigné. N'hésitez pas à demander des comptes rendus réguliers."
    }
  ];

  const droits = [
    {
      icon: AlertCircle,
      title: "Droit à l'information",
      description: "Vous avez le droit d'être informé de vos droits, des procédures en cours et des décisions vous concernant."
    },
    {
      icon: FileText,
      title: "Droit à la contestation",
      description: "Vous pouvez contester toute décision administrative ou médicale que vous estimez injuste ou erronée."
    },
    {
      icon: Users,
      title: "Droit à l'accompagnement",
      description: "Vous pouvez vous faire accompagner lors des expertises et dans vos démarches administratives."
    },
    {
      icon: Scale,
      title: "Droit à la réparation",
      description: "En cas de préjudice reconnu, vous avez droit à une indemnisation juste et complète."
    }
  ];

  return (
    <main className="page-transition pt-20">
      <SEO title="Protection juridique" description="Activez votre protection juridique pour faire valoir vos droits en cas de litige avec un assureur ou employeur." path="/protection-juridique" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="text-sm font-medium text-accent uppercase tracking-wider">Guide & Accompagnement</span>
              <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="protection-juridique-title">
                Protection juridique : vos droits et comment les faire valoir
              </h1>
              <p className="text-lg text-muted-foreground mb-6">
                La protection juridique est un mécanisme souvent méconnu qui peut pourtant vous aider 
                à faire valoir vos droits en cas de litige. Découvrez comment l'activer et comment 
                je peux vous accompagner.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/contact">
                  <Button size="lg" className="rounded-full px-8 gap-2">
                    Être accompagné
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </Link>
                <a href="#activation">
                  <Button variant="outline" size="lg" className="rounded-full px-8">
                    Guide d'activation
                  </Button>
                </a>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/5668858/pexels-photo-5668858.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Protection juridique"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 1 - Qu'est-ce que la protection juridique */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <HelpCircle className="w-12 h-12 text-accent mb-4" strokeWidth={1.5} />
              <h2 className="text-3xl font-semibold mb-6">
                Qu'est-ce que la protection juridique ?
              </h2>
              <p className="text-muted-foreground mb-6">
                La protection juridique est une garantie d'assurance qui vous permet de bénéficier 
                d'une assistance juridique en cas de litige. Elle peut couvrir :
              </p>
              <ul className="space-y-3 mb-6">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Les frais d'avocat et de procédure</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Les honoraires d'experts</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>L'information et le conseil juridique</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>La négociation amiable avec la partie adverse</span>
                </li>
              </ul>
              <Card className="bg-muted/30 border-border">
                <CardContent className="p-4">
                  <p className="text-sm text-muted-foreground">
                    <strong>Bon à savoir :</strong> Vous avez peut-être déjà une protection juridique 
                    sans le savoir. Elle est souvent incluse dans vos contrats d'assurance habitation, 
                    automobile ou santé complémentaire.
                  </p>
                </CardContent>
              </Card>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Card className="border-border">
                <CardContent className="p-6 text-center">
                  <Shield className="w-10 h-10 text-accent mx-auto mb-3" strokeWidth={1.5} />
                  <h4 className="font-semibold mb-1">Litiges du travail</h4>
                  <p className="text-sm text-muted-foreground">Conflits avec l'employeur, licenciement</p>
                </CardContent>
              </Card>
              <Card className="border-border">
                <CardContent className="p-6 text-center">
                  <Scale className="w-10 h-10 text-accent mx-auto mb-3" strokeWidth={1.5} />
                  <h4 className="font-semibold mb-1">Litiges assurance</h4>
                  <p className="text-sm text-muted-foreground">Refus d'indemnisation, contestation</p>
                </CardContent>
              </Card>
              <Card className="border-border">
                <CardContent className="p-6 text-center">
                  <FileText className="w-10 h-10 text-accent mx-auto mb-3" strokeWidth={1.5} />
                  <h4 className="font-semibold mb-1">Litiges administratifs</h4>
                  <p className="text-sm text-muted-foreground">CPAM, MDPH, organismes sociaux</p>
                </CardContent>
              </Card>
              <Card className="border-border">
                <CardContent className="p-6 text-center">
                  <Briefcase className="w-10 h-10 text-accent mx-auto mb-3" strokeWidth={1.5} />
                  <h4 className="font-semibold mb-1">AT / MP</h4>
                  <p className="text-sm text-muted-foreground">Accidents du travail, maladies pro</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Section 2 - Comment activer */}
      <section id="activation" className="section-padding bg-card">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <Search className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="text-3xl font-semibold mb-4">
              Comment activer votre protection juridique ?
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Guide pratique étape par étape pour identifier et déclencher votre protection juridique 
              auprès de votre assurance.
            </p>
          </div>

          <div className="space-y-6">
            {etapesActivation.map((etape, index) => (
              <div 
                key={index}
                className="flex gap-6 bg-background p-6 rounded-xl border border-border"
                data-testid={`etape-activation-${index}`}
              >
                <div className="w-12 h-12 bg-accent text-accent-foreground rounded-full flex items-center justify-center flex-shrink-0 font-bold text-lg">
                  {etape.step}
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2">{etape.title}</h3>
                  <p className="text-muted-foreground">{etape.description}</p>
                </div>
              </div>
            ))}
          </div>

          <Card className="mt-8 bg-accent/10 border-accent/20">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-accent flex-shrink-0 mt-1" strokeWidth={1.5} />
                <div>
                  <h4 className="font-semibold mb-2">Important : le libre choix de l'avocat</h4>
                  <p className="text-sm text-muted-foreground">
                    Vous avez le droit de choisir votre propre avocat, même si votre assurance 
                    vous en propose un. C'est un droit garanti par la loi. N'hésitez pas à faire 
                    appel à un avocat spécialisé dans votre domaine de litige.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Section 3 - Vos droits */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <BookOpen className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="text-3xl font-semibold mb-4">
              Vos droits en cas d'AT/MP et litige
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              En cas d'accident du travail, de maladie professionnelle ou de litige avec 
              un employeur ou une assurance, vous disposez de droits fondamentaux.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {droits.map((droit, index) => (
              <Card key={index} className="card-lift border-border" data-testid={`droit-${index}`}>
                <CardContent className="p-6">
                  <droit.icon className="w-10 h-10 text-accent mb-4" strokeWidth={1.5} />
                  <h3 className="font-semibold text-lg mb-2">{droit.title}</h3>
                  <p className="text-sm text-muted-foreground">{droit.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Section 4 - Avocats partenaires */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/5668473/pexels-photo-5668473.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Avocats partenaires"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
            <div>
              <Users className="w-12 h-12 text-accent mb-4" strokeWidth={1.5} />
              <h2 className="text-3xl font-semibold mb-6">
                Orientation vers des avocats partenaires
              </h2>
              <p className="text-muted-foreground mb-6">
                Au cours de mon parcours, j'ai constitué un réseau de professionnels du domaine 
                judiciaire spécialisés dans les litiges liés au travail, à la santé et aux assurances.
              </p>
              <p className="text-muted-foreground mb-6">
                Selon votre situation, je peux vous orienter vers des avocats partenaires compétents 
                dans les domaines suivants :
              </p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Droit de la sécurité sociale (AT/MP, invalidité)</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Droit du travail (licenciement, harcèlement)</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Droit des assurances (refus d'indemnisation)</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Réparation du préjudice corporel</span>
                </li>
              </ul>
              <Link to="/partenaires">
                <Button variant="outline" className="rounded-full px-6 gap-2">
                  Découvrir le réseau de partenaires
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Section 5 - Accompagnement payant */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <Shield className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
              Accompagnement personnalisé
            </h2>
            <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
              Pour les personnes souhaitant être accompagnées dans l'activation et le suivi 
              de leur protection juridique, je propose une prestation dédiée.
            </p>
          </div>

          <Card className="bg-primary-foreground/10 border-primary-foreground/20">
            <CardContent className="p-8">
              <div className="grid md:grid-cols-2 gap-8 items-center">
                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary-foreground">
                    Accompagnement Protection Juridique
                  </h3>
                  <ul className="space-y-3 text-primary-foreground/80">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                      <span>Identification de vos garanties</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                      <span>Aide à la déclaration du litige</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                      <span>Suivi des échanges avec l'assureur</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                      <span>Orientation vers un avocat spécialisé</span>
                    </li>
                  </ul>
                </div>
                <div className="text-center md:text-right">
                  <p className="text-sm text-primary-foreground/60 mb-2">À partir de</p>
                  <p className="text-5xl font-bold text-primary-foreground mb-2">200 €</p>
                  <p className="text-sm text-primary-foreground/60 mb-6">Devis personnalisé selon situation</p>
                  <Link to="/contact">
                    <Button 
                      size="lg"
                      className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
                    >
                      Demander un devis
                      <ArrowRight className="w-4 h-4" />
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>

          <p className="text-center text-primary-foreground/50 text-sm mt-6">
            Premier échange téléphonique gratuit et sans engagement
          </p>
        </div>
      </section>
    </main>
  );
};
