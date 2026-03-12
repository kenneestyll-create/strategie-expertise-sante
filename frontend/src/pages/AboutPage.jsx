import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowRight, Calendar, FileText, Scale, Heart, Award, Download, ChevronLeft, ChevronRight } from 'lucide-react';

export const AboutPage = () => {
  const [pdfError, setPdfError] = useState(false);
  const timeline = [
    {
      year: "Année 1",
      title: "Le début du parcours",
      description: "Diagnostic d'une maladie professionnelle. Début des démarches de reconnaissance auprès de la CPAM. Premiers pas dans un univers administratif complexe et souvent hostile."
    },
    {
      year: "Année 2",
      title: "Les expertises médicales",
      description: "Multiplication des rendez-vous médicaux et expertises. Découverte du fonctionnement du CRRMP. Apprentissage forcé du vocabulaire médico-administratif."
    },
    {
      year: "Année 3",
      title: "Les combats assurantiels",
      description: "Face à mon assurance prévoyance, début d'un bras de fer pour faire reconnaître mes droits. PTIA, invalidité, refus, recours... Une bataille d'usure."
    },
    {
      year: "Année 4+",
      title: "La reconnaissance et le partage",
      description: "Obtention progressive de mes droits. Décision de mettre cette expérience au service des autres. Naissance d'Accompagn'Santé."
    }
  ];

  const credentials = [
    {
      icon: Calendar,
      title: "4+ années d'expérience",
      description: "De vécu personnel dans les procédures AT/MP et assurantielles"
    },
    {
      icon: FileText,
      title: "Dizaines de dossiers",
      description: "Étudiés, analysés et préparés avec succès"
    },
    {
      icon: Scale,
      title: "Connaissance du système",
      description: "CPAM, MDPH, CRRMP, expertises, assurances"
    },
    {
      icon: Heart,
      title: "Approche humaine",
      description: "Une écoute bienveillante, sans jugement"
    }
  ];

  return (
    <main className="page-transition pt-20">
      {/* Hero Section */}
      <section className="relative section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="text-sm font-medium text-accent uppercase tracking-wider">À propos</span>
              <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="about-title">
                Mon parcours, votre force
              </h1>
              <p className="text-lg text-muted-foreground mb-6">
                Je ne suis ni médecin, ni avocat, ni expert. Je suis quelqu'un qui a vécu de l'intérieur 
                ce que vous traversez peut-être aujourd'hui : la maladie professionnelle, les expertises 
                médicales interminables, et les combats contre les assurances.
              </p>
              <p className="text-muted-foreground">
                Pendant plus de sept ans, j'ai dû apprendre à naviguer dans un système complexe, 
                souvent opaque, parfois injuste. J'ai fait des erreurs, j'ai perdu du temps, 
                mais j'ai aussi compris comment il fonctionne.
              </p>
            </div>
            <div className="relative">
              <div className="aspect-square rounded-2xl overflow-hidden">
                <img 
                  src="https://images.pexels.com/photos/18465014/pexels-photo-18465014.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Parcours personnel"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Timeline Section */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Chronologie</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2">
              7 ans de combat
            </h2>
          </div>

          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-0 md:left-1/2 top-0 bottom-0 w-px bg-border transform md:-translate-x-px" />

            {timeline.map((item, index) => (
              <div 
                key={index}
                className={`relative flex flex-col md:flex-row gap-8 mb-12 last:mb-0 ${
                  index % 2 === 0 ? 'md:flex-row-reverse' : ''
                }`}
                data-testid={`timeline-item-${index}`}
              >
                {/* Content */}
                <div className={`flex-1 ${index % 2 === 0 ? 'md:text-right md:pr-12' : 'md:pl-12'} pl-8 md:pl-0`}>
                  <span className="inline-block text-sm font-semibold text-accent mb-2">
                    {item.year}
                  </span>
                  <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                  <p className="text-muted-foreground">{item.description}</p>
                </div>
                
                {/* Dot */}
                <div className="absolute left-0 md:left-1/2 top-0 w-4 h-4 bg-accent rounded-full transform -translate-x-1.5 md:-translate-x-2" />
                
                {/* Spacer for opposite side */}
                <div className="hidden md:block flex-1" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why Me Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Pourquoi moi ?</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">
              L'expérience au service de l'accompagnement
            </h2>
            <p className="text-muted-foreground">
              Ce que j'ai appris à mes dépens, je le partage aujourd'hui pour vous épargner 
              les erreurs, le stress et l'isolement que j'ai connus.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {credentials.map((item, index) => (
              <div 
                key={index} 
                className="bg-background p-6 rounded-xl border border-border"
                data-testid={`credential-${index}`}
              >
                <item.icon className="w-10 h-10 text-accent mb-4" strokeWidth={1.5} />
                <h3 className="font-semibold mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Document Juridique Section - PDF Viewer */}
      <section className="section-padding bg-secondary" data-testid="pdf-viewer-section">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Document officiel</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">
              Décision du Tribunal de Chartres
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Ce document témoigne de mon parcours juridique et de la reconnaissance obtenue 
              après des années de combat.
            </p>
          </div>

          <Card className="border-border overflow-hidden">
            <CardContent className="p-0">
              {/* PDF Embedded Viewer */}
              <div className="w-full bg-muted/30" data-testid="pdf-embed-container">
                <object
                  data="/decision-tribunal-chartres.pdf"
                  type="application/pdf"
                  className="w-full"
                  style={{ height: '700px' }}
                  data-testid="pdf-object"
                >
                  <div className="p-12 text-center">
                    <FileText className="w-16 h-16 text-accent mx-auto mb-4" strokeWidth={1} />
                    <h3 className="font-semibold text-lg mb-2">Décision du Tribunal Judiciaire de Chartres</h3>
                    <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
                      Votre navigateur ne prend pas en charge l'affichage PDF intégré. 
                      Vous pouvez télécharger le document ci-dessous.
                    </p>
                    <a 
                      href="/decision-tribunal-chartres.pdf" 
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      <Button className="rounded-lg gap-2">
                        <Download className="w-4 h-4" />
                        Ouvrir le PDF
                      </Button>
                    </a>
                  </div>
                </object>
              </div>
              {/* Download bar */}
              <div className="flex items-center justify-between p-4 bg-card border-t border-border">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-accent" strokeWidth={1.5} />
                  <div>
                    <p className="text-sm font-medium">Tribunal Judiciaire de Chartres — N°23/00331</p>
                    <p className="text-xs text-muted-foreground">Décision du 17/10/2025 — PDF, 50 Ko</p>
                  </div>
                </div>
                <a 
                  href="/decision-tribunal-chartres.pdf" 
                  download="Decision-Tribunal-Chartres-2300331.pdf"
                  data-testid="pdf-download-button"
                >
                  <Button variant="outline" className="rounded-lg gap-2">
                    <Download className="w-4 h-4" />
                    Télécharger
                  </Button>
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Quote Section */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto text-center">
          <Award className="w-12 h-12 text-accent mx-auto mb-6" strokeWidth={1.5} />
          <blockquote className="text-2xl sm:text-3xl font-serif italic text-foreground mb-6">
            "Je ne promets pas de tout résoudre. Je promets de vous écouter, de vous expliquer, 
            et de vous accompagner dans ce parcours difficile. Ensemble, nous sommes plus forts."
          </blockquote>
          <p className="text-muted-foreground">— Fondateur d'Accompagn'Santé</p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
            Prêt à être accompagné ?
          </h2>
          <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
            Contactez-moi pour discuter de votre situation. Le premier échange est gratuit et sans engagement.
          </p>
          <Link to="/contact">
            <Button 
              size="lg" 
              className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="about-cta-button"
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
