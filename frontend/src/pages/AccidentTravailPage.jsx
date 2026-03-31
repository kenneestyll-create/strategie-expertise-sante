import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { 
  ArrowRight, 
  AlertCircle, 
  FileCheck, 
  Stethoscope, 
  Building2,
  CheckCircle,
  ClipboardList,
  Heart
} from 'lucide-react';

export const AccidentTravailPage = () => {
  const etapesAT = [
    "Déclaration de l'accident",
    "Suivi médical",
    "Expertise médicale",
    "Consolidation",
    "Évaluation du taux d'incapacité permanente"
  ];

  const etapesMP = [
    "Un dossier médical solide",
    "Des expertises médicales",
    "Des échanges avec les organismes sociaux"
  ];

  const accompagnement = [
    { icon: FileCheck, text: "Comprendre les démarches" },
    { icon: ClipboardList, text: "Analyser les décisions administratives" },
    { icon: Stethoscope, text: "Préparer certaines étapes importantes du dossier" }
  ];

  return (
    <main className="page-transition pt-20">
      <SEO title="Accident du travail et maladie professionnelle" description="Conseil expert en accident du travail (AT) et maladie professionnelle (MP). Faites valoir vos droits." path="/accident-travail-maladie-professionnelle" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Vos droits</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="atmp-title">
              Accident du travail et maladie professionnelle : comprendre vos droits
            </h1>
            <p className="text-lg text-muted-foreground">
              Un accident du travail ou une maladie professionnelle peut bouleverser toute une vie.
              Au-delà des douleurs physiques, les démarches administratives et médicales peuvent 
              devenir complexes : expertises, reconnaissance de l'origine professionnelle, taux 
              d'incapacité, relations avec l'employeur ou l'assurance.
            </p>
          </div>
        </div>
      </section>

      {/* Accident du travail Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-accent" strokeWidth={1.5} />
                </div>
                <h2 className="text-3xl font-semibold">Accident du travail</h2>
              </div>
              
              <p className="text-muted-foreground mb-6">
                Un accident du travail est un événement soudain survenu pendant l'activité 
                professionnelle ou à l'occasion du travail et ayant entraîné une lésion.
              </p>

              <Card className="border-border">
                <CardHeader>
                  <CardTitle className="text-lg">Les étapes peuvent inclure :</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {etapesAT.map((etape, index) => (
                      <div key={index} className="flex items-start gap-3" data-testid={`etape-at-${index}`}>
                        <div className="w-6 h-6 bg-muted rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-xs font-medium text-muted-foreground">{index + 1}</span>
                        </div>
                        <span>{etape}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/5699456/pexels-photo-5699456.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Accident du travail"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Maladie professionnelle Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            <div className="order-2 lg:order-1">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/7089020/pexels-photo-7089020.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Maladie professionnelle"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            <div className="order-1 lg:order-2">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-accent" strokeWidth={1.5} />
                </div>
                <h2 className="text-3xl font-semibold">Maladie professionnelle</h2>
              </div>
              
              <p className="text-muted-foreground mb-6">
                Une maladie professionnelle est une pathologie directement liée aux conditions de travail.
              </p>

              <Card className="border-border">
                <CardHeader>
                  <CardTitle className="text-lg">Sa reconnaissance peut nécessiter :</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {etapesMP.map((etape, index) => (
                      <div key={index} className="flex items-start gap-3" data-testid={`etape-mp-${index}`}>
                        <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                        <span>{etape}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
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
              Mon accompagnement
            </h2>
            <p className="text-primary-foreground/70">
              Je propose un accompagnement pour vous aider dans ces démarches souvent complexes.
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-6 mb-10">
            {accompagnement.map((item, index) => (
              <div 
                key={index} 
                className="bg-primary-foreground/10 rounded-xl p-6 text-center"
                data-testid={`accompagnement-atmp-${index}`}
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
                data-testid="atmp-cta-button"
              >
                Me contacter
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>

          {/* Encarts IP & PGPF */}
          <div className="grid sm:grid-cols-2 gap-6 mt-12">
            <div className="bg-primary-foreground/10 rounded-xl p-6" data-testid="atmp-ip-card">
              <h3 className="text-lg font-semibold text-primary-foreground mb-3">Incidence Professionnelle (IP)</h3>
              <p className="text-sm text-primary-foreground/70 mb-4">
                Vos séquelles impactent votre carrière ? Vous avez peut-être droit à une indemnisation complémentaire au titre de l'incidence professionnelle : pénibilité accrue, dévalorisation, reconversion...
              </p>
              <Link to="/ressources" className="text-sm text-accent hover:underline font-medium">
                En savoir plus sur l'IP →
              </Link>
            </div>
            <div className="bg-primary-foreground/10 rounded-xl p-6" data-testid="atmp-pgpf-card">
              <h3 className="text-lg font-semibold text-primary-foreground mb-3">Perte de Gains Futurs (PGPF)</h3>
              <p className="text-sm text-primary-foreground/70 mb-4">
                Votre accident ou maladie réduit durablement vos revenus ? La PGPF compense cette perte définitive par capitalisation. Découvrez la méthode de calcul et les justificatifs.
              </p>
              <Link to="/ressources" className="text-sm text-accent hover:underline font-medium">
                En savoir plus sur la PGPF →
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};
