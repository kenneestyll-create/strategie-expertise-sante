import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, BookOpen, AlertCircle, FileText, Shield, HelpCircle, Download, Eye } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ResourcesPage = () => {
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState("AT/MP");

  const categories = ["AT/MP", "Expertises", "Assurances", "MDPH"];

  useEffect(() => {
    fetchFaqs();
  }, []);

  const fetchFaqs = async () => {
    try {
      const response = await axios.get(`${API}/faq`);
      setFaqs(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des FAQ:', error);
    } finally {
      setLoading(false);
    }
  };

  const getFaqsByCategory = (category) => {
    return faqs.filter(faq => faq.categorie === category);
  };

  const glossary = [
    {
      term: "IPP",
      fullName: "Incapacité Permanente Partielle",
      definition: "Taux exprimé en pourcentage qui évalue les séquelles définitives d'un accident du travail ou d'une maladie professionnelle. Ce taux détermine le montant de l'indemnisation versée par la Sécurité sociale."
    },
    {
      term: "PTIA",
      fullName: "Perte Totale et Irréversible d'Autonomie",
      definition: "Garantie d'assurance couvrant l'état d'une personne qui ne peut plus exercer aucune activité professionnelle et qui nécessite l'assistance d'une tierce personne pour les actes de la vie quotidienne."
    },
    {
      term: "CRRMP",
      fullName: "Comité Régional de Reconnaissance des Maladies Professionnelles",
      definition: "Instance composée de médecins qui statue sur les demandes de reconnaissance de maladie professionnelle lorsque la pathologie ne figure pas dans un tableau ou que les conditions du tableau ne sont pas remplies."
    },
    {
      term: "AT/MP",
      fullName: "Accident du Travail / Maladie Professionnelle",
      definition: "Régime spécifique de la Sécurité sociale qui couvre les accidents survenus au travail ou sur le trajet, ainsi que les maladies contractées du fait de l'activité professionnelle."
    },
    {
      term: "RQTH",
      fullName: "Reconnaissance de la Qualité de Travailleur Handicapé",
      definition: "Décision administrative qui reconnaît le handicap d'une personne et lui ouvre des droits spécifiques en matière d'emploi (aménagement de poste, priorité à l'embauche, etc.)."
    },
    {
      term: "MDPH",
      fullName: "Maison Départementale des Personnes Handicapées",
      definition: "Guichet unique pour toutes les démarches liées au handicap : RQTH, AAH, cartes d'invalidité, prestations de compensation, etc."
    },
    {
      term: "AAH",
      fullName: "Allocation aux Adultes Handicapés",
      definition: "Aide financière versée aux personnes handicapées ayant un taux d'incapacité d'au moins 80%, ou entre 50% et 79% avec une restriction substantielle d'accès à l'emploi."
    },
    {
      term: "CMI",
      fullName: "Certificat Médical Initial",
      definition: "Document médical établi par un médecin qui constate les lésions ou la maladie et leur lien avec l'activité professionnelle. C'est le point de départ de toute demande de reconnaissance."
    }
  ];

  const guides = [
    {
      icon: FileText,
      title: "Déclarer une maladie professionnelle",
      description: "Les étapes essentielles pour faire reconnaître votre maladie par la CPAM.",
      points: [
        "Obtenir un certificat médical initial de votre médecin",
        "Remplir le formulaire de déclaration (cerfa n°60-3950)",
        "Envoyer le dossier à votre CPAM dans les 15 jours",
        "Attendre la décision (3 mois maximum)"
      ]
    },
    {
      icon: Shield,
      title: "Se préparer à une expertise médicale",
      description: "Conseils pratiques pour aborder sereinement cette étape importante.",
      points: [
        "Rassembler tous vos documents médicaux",
        "Lister vos symptômes au quotidien",
        "Préparer une chronologie de votre parcours",
        "Rester honnête et précis dans vos réponses"
      ]
    },
    {
      icon: AlertCircle,
      title: "Contester un refus d'indemnisation",
      description: "Vos recours face à un refus de votre assurance ou de la Sécurité sociale.",
      points: [
        "Demander les motifs précis du refus par écrit",
        "Vérifier la conformité avec votre contrat ou la loi",
        "Saisir le médiateur ou la commission de recours",
        "Envisager une action judiciaire si nécessaire"
      ]
    }
  ];

  return (
    <main className="page-transition pt-20">
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Ressources</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="resources-title">
              Comprendre pour mieux agir
            </h1>
            <p className="text-lg text-muted-foreground">
              Des explications simples et accessibles pour vous aider à naviguer 
              dans le monde complexe des maladies professionnelles, des expertises 
              et des assurances. Sans jargon, sans langue de bois.
            </p>
          </div>
        </div>
      </section>

      {/* Glossary Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Lexique</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">
              Les termes à connaître
            </h2>
            <p className="text-muted-foreground max-w-2xl">
              Ces acronymes et termes reviennent souvent dans vos démarches. 
              Voici ce qu'ils signifient concrètement.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {glossary.map((item, index) => (
              <Card 
                key={index} 
                className="card-lift border-border"
                data-testid={`glossary-item-${item.term.toLowerCase()}`}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl font-bold text-accent">{item.term}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">{item.fullName}</p>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-foreground">{item.definition}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Guides Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Guides pratiques</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">
              Par où commencer ?
            </h2>
            <p className="text-muted-foreground max-w-2xl">
              Des guides étape par étape pour vous orienter dans vos démarches.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            {guides.map((guide, index) => (
              <Card 
                key={index} 
                className="border-border"
                data-testid={`guide-${index}`}
              >
                <CardHeader>
                  <guide.icon className="w-10 h-10 text-accent mb-4" strokeWidth={1.5} />
                  <CardTitle className="text-xl">{guide.title}</CardTitle>
                  <p className="text-sm text-muted-foreground">{guide.description}</p>
                </CardHeader>
                <CardContent>
                  <ol className="space-y-3">
                    {guide.points.map((point, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <span className="flex-shrink-0 w-6 h-6 bg-muted rounded-full flex items-center justify-center text-sm font-medium text-muted-foreground">
                          {i + 1}
                        </span>
                        <span className="text-sm">{point}</span>
                      </li>
                    ))}
                  </ol>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="section-padding" id="faq">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <HelpCircle className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <span className="text-sm font-medium text-accent uppercase tracking-wider">FAQ</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">
              Questions fréquentes
            </h2>
            <p className="text-muted-foreground">
              Les réponses aux questions que vous vous posez.
            </p>
          </div>

          {loading ? (
            <div className="text-center text-muted-foreground" data-testid="faq-loading">
              Chargement des questions...
            </div>
          ) : (
            <Tabs defaultValue="AT/MP" className="w-full" data-testid="faq-tabs">
              <TabsList className="w-full flex-wrap h-auto gap-2 bg-muted/50 p-2 rounded-xl mb-8">
                {categories.map((category) => (
                  <TabsTrigger 
                    key={category} 
                    value={category}
                    className="flex-1 min-w-[100px] rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-sm"
                    data-testid={`faq-tab-${category.toLowerCase().replace('/', '-')}`}
                  >
                    {category}
                  </TabsTrigger>
                ))}
              </TabsList>

              {categories.map((category) => (
                <TabsContent key={category} value={category}>
                  <Accordion type="single" collapsible className="w-full">
                    {getFaqsByCategory(category).map((faq, index) => (
                      <AccordionItem 
                        key={faq.id} 
                        value={faq.id}
                        className="border-border"
                        data-testid={`faq-item-${index}`}
                      >
                        <AccordionTrigger className="text-left hover:no-underline hover:text-accent">
                          {faq.question}
                        </AccordionTrigger>
                        <AccordionContent className="text-muted-foreground">
                          {faq.reponse}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                    {getFaqsByCategory(category).length === 0 && (
                      <p className="text-muted-foreground text-center py-8">
                        Aucune question dans cette catégorie pour le moment.
                      </p>
                    )}
                  </Accordion>
                </TabsContent>
              ))}
            </Tabs>
          )}
        </div>
      </section>

      {/* Downloadable Guides Library */}
      <section className="section-padding" id="bibliotheque">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Bibliothèque</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">
              Guides PDF téléchargeables
            </h2>
            <p className="text-muted-foreground max-w-2xl">
              Des guides pratiques gratuits pour vous accompagner dans vos démarches. 
              Téléchargez-les et consultez-les à votre rythme.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                id: 'guide_mp',
                title: "Guide : Déclarer une maladie professionnelle",
                description: "Toutes les étapes pour faire reconnaître votre maladie professionnelle auprès de la CPAM, avec les formulaires nécessaires et les délais à respecter.",
                category: "AT/MP",
                pages: "12 pages"
              },
              {
                id: 'guide_expertise',
                title: "Guide : Se préparer à une expertise médicale",
                description: "Conseils pratiques et liste de contrôle pour aborder sereinement votre expertise médicale et faire valoir vos droits.",
                category: "Expertises",
                pages: "8 pages"
              },
              {
                id: 'guide_mdph',
                title: "Guide : Constituer un dossier MDPH",
                description: "Comment remplir le formulaire MDPH, quels documents joindre et comment maximiser vos chances d'obtenir une réponse favorable.",
                category: "MDPH",
                pages: "15 pages"
              },
              {
                id: 'guide_recours',
                title: "Guide : Contester un refus",
                description: "Vos droits face à un refus de la CPAM ou de votre assurance. Les différentes voies de recours et les délais à respecter.",
                category: "Recours",
                pages: "10 pages"
              },
              {
                id: 'guide_ipp',
                title: "Guide : Comprendre le taux d'IPP",
                description: "Tout savoir sur l'Incapacité Permanente Partielle : comment le taux est fixé, comment le contester, et son impact sur votre indemnisation.",
                category: "AT/MP",
                pages: "8 pages"
              },
              {
                id: 'guide_assurance',
                title: "Guide : Activer sa protection juridique",
                description: "Comment identifier et activer votre protection juridique pour financer vos démarches et frais d'avocat.",
                category: "Assurances",
                pages: "6 pages"
              }
            ].map((guide) => (
              <Card key={guide.id} className="border-border flex flex-col" data-testid={`library-guide-${guide.id}`}>
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center mb-3">
                      <FileText className="w-6 h-6 text-accent" strokeWidth={1.5} />
                    </div>
                    <Badge variant="secondary">{guide.category}</Badge>
                  </div>
                  <CardTitle className="text-base leading-tight">{guide.title}</CardTitle>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col">
                  <p className="text-sm text-muted-foreground flex-1">{guide.description}</p>
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
                    <span className="text-xs text-muted-foreground">PDF — {guide.pages}</span>
                    <Button
                      variant="outline"
                      size="sm"
                      className="gap-1.5 rounded-lg"
                      onClick={() => {
                        axios.post(`${API}/resources/download`, { resource_id: guide.id, resource_title: guide.title }).catch(() => {});
                        toast.info("Ce guide sera bientôt disponible au téléchargement.");
                      }}
                      data-testid={`download-${guide.id}`}
                    >
                      <Download className="w-3.5 h-3.5" />
                      Télécharger
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <BookOpen className="w-12 h-12 text-accent mx-auto mb-6" strokeWidth={1.5} />
          <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
            Une question spécifique ?
          </h2>
          <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
            Ces ressources sont générales. Votre situation est unique et mérite 
            une analyse personnalisée. Contactez-moi pour en discuter.
          </p>
          <Link to="/contact">
            <Button 
              size="lg" 
              className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="resources-cta-button"
            >
              Me poser votre question
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </main>
  );
};
