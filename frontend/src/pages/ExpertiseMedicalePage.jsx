import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { 
  ArrowRight, 
  Stethoscope, 
  FileText, 
  ClipboardList, 
  UserCheck,
  CheckCircle,
  AlertTriangle,
  BookOpen
} from 'lucide-react';

export const ExpertiseMedicalePage = () => {
  const contexts = [
    "Accident du travail",
    "Maladie professionnelle",
    "Invalidité",
    "Dossier d'assurance",
    "Procédure judiciaire"
  ];

  const consequences = [
    "Reconnaissance ou non d'un handicap",
    "Taux d'incapacité",
    "Indemnisation",
    "Reconnaissance d'une invalidité",
    "Attribution d'une aide tierce personne"
  ];

  const etapes = [
    { icon: FileText, text: "Étude du dossier médical" },
    { icon: UserCheck, text: "Entretien avec la personne concernée" },
    { icon: Stethoscope, text: "Examen clinique" },
    { icon: ClipboardList, text: "Analyse des documents médicaux" },
    { icon: BookOpen, text: "Rédaction d'un rapport" }
  ];

  const accompagnement = [
    "Comprendre les enjeux d'une expertise médicale",
    "Préparer les éléments importants du dossier",
    "Analyser les conclusions d'une expertise"
  ];

  return (
    <main className="page-transition pt-20">
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Guide pratique</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="expertise-title">
              Expertise médicale : comment s'y préparer
            </h1>
            <p className="text-lg text-muted-foreground">
              Une expertise médicale est une étape déterminante dans de nombreuses procédures 
              liées à la santé, au handicap ou à l'indemnisation d'un dommage corporel.
            </p>
          </div>
        </div>
      </section>

      {/* Contextes Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-semibold mb-6">
                Dans quels contextes intervient-elle ?
              </h2>
              <p className="text-muted-foreground mb-6">
                Elle peut intervenir dans différents contextes :
              </p>
              <div className="space-y-3">
                {contexts.map((context, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-accent rounded-full flex-shrink-0" />
                    <span className="text-foreground">{context}</span>
                  </div>
                ))}
              </div>
              <p className="text-muted-foreground mt-6">
                Lors de cette expertise, un médecin expert est chargé d'évaluer l'état de santé 
                et ses conséquences sur la vie quotidienne et professionnelle.
              </p>
            </div>
            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden bg-muted">
                <img 
                  src="https://images.pexels.com/photos/7089401/pexels-photo-7089401.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Consultation médicale"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Importance Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <AlertTriangle className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="text-3xl font-semibold mb-4">
              Pourquoi l'expertise médicale est importante
            </h2>
            <p className="text-muted-foreground">
              Le rapport d'expertise peut avoir des conséquences majeures sur votre situation.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {consequences.map((item, index) => (
              <Card key={index} className="border-border" data-testid={`consequence-${index}`}>
                <CardContent className="p-6 flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>{item}</span>
                </CardContent>
              </Card>
            ))}
          </div>

          <p className="text-center text-muted-foreground mt-8 max-w-2xl mx-auto">
            Il est donc essentiel de bien comprendre le rôle de l'expert et les enjeux de cette étape.
          </p>
        </div>
      </section>

      {/* Déroulement Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-semibold mb-4">
              Comment se déroule une expertise
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Une expertise médicale se déroule généralement en plusieurs étapes.
            </p>
          </div>

          <div className="max-w-3xl mx-auto">
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-6 top-0 bottom-0 w-px bg-border" />

              {etapes.map((etape, index) => (
                <div 
                  key={index} 
                  className="relative flex items-start gap-6 pb-8 last:pb-0"
                  data-testid={`etape-${index}`}
                >
                  <div className="relative z-10 w-12 h-12 bg-background border-2 border-accent rounded-full flex items-center justify-center flex-shrink-0">
                    <etape.icon className="w-5 h-5 text-accent" strokeWidth={1.5} />
                  </div>
                  <div className="pt-3">
                    <p className="font-medium text-lg">{etape.text}</p>
                  </div>
                </div>
              ))}
            </div>

            <p className="text-muted-foreground mt-8 pl-18">
              Le rapport est ensuite transmis à l'organisme ou au tribunal qui a demandé l'expertise.
            </p>
          </div>
        </div>
      </section>

      {/* Accompagnement Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-semibold mb-4">
              Mon accompagnement
            </h2>
            <p className="text-primary-foreground/70">
              Je propose un accompagnement pour :
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-6 mb-10">
            {accompagnement.map((item, index) => (
              <div 
                key={index} 
                className="bg-primary-foreground/10 rounded-xl p-6 text-center"
                data-testid={`accompagnement-${index}`}
              >
                <p className="text-primary-foreground">{item}</p>
              </div>
            ))}
          </div>

          <p className="text-center text-primary-foreground/70 mb-8">
            L'objectif est de permettre aux personnes concernées de mieux appréhender 
            cette étape souvent déterminante.
          </p>

          <div className="text-center">
            <Link to="/contact">
              <Button 
                size="lg" 
                className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
                data-testid="expertise-cta-button"
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
