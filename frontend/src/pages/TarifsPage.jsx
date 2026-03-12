import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowRight, 
  FileSearch, 
  Shield, 
  Users, 
  Briefcase,
  CheckCircle,
  Star,
  GraduationCap,
  Building2
} from 'lucide-react';

export const TarifsPage = () => {
  const prestationsParticuliers = [
    {
      icon: FileSearch,
      title: "Analyse de dossier",
      description: "Étude personnalisée du dossier médical et administratif. Identification des points forts, des faiblesses et des éléments manquants.",
      price: "150",
      priceNote: "à partir de",
      features: [
        "Lecture complète du dossier",
        "Rapport d'analyse détaillé",
        "Recommandations personnalisées",
        "Échange téléphonique de restitution"
      ]
    },
    {
      icon: Shield,
      title: "Préparation à expertise médicale",
      description: "Accompagnement pour aborder sereinement une expertise médicale. Préparation du dossier et conseils stratégiques.",
      price: "250",
      priceNote: "à partir de",
      features: [
        "Analyse du dossier médical",
        "Préparation des arguments",
        "Simulation d'entretien",
        "Liste des documents à apporter"
      ],
      popular: true
    },
    {
      icon: Users,
      title: "Accompagnement MDPH",
      description: "Aide à la compréhension et structuration du dossier MDPH. Orientation vers les droits possibles.",
      price: "200",
      priceNote: "à partir de",
      features: [
        "Analyse de votre situation",
        "Aide au formulaire",
        "Conseils sur les pièces justificatives",
        "Suivi de la demande"
      ]
    },
    {
      icon: Briefcase,
      title: "Accompagnement complet",
      description: "Suivi global dans les démarches administratives et médicales. Accompagnement personnalisé sur la durée.",
      price: "500",
      priceNote: "à partir de",
      badge: "Sur devis",
      features: [
        "Analyse complète de la situation",
        "Stratégie personnalisée",
        "Suivi des démarches",
        "Disponibilité continue"
      ]
    }
  ];

  const prestationsPro = [
    {
      icon: GraduationCap,
      title: "Séminaires et formations",
      description: "Sessions d'information et de formation pour particuliers, associations, professionnels de santé et entreprises.",
      price: "Sur devis",
      priceNote: "selon format et public",
      features: [
        "En présentiel ou visioconférence",
        "Conférences ou ateliers",
        "Programme personnalisé",
        "Supports pédagogiques"
      ]
    },
    {
      icon: Building2,
      title: "Conseil aux entreprises",
      description: "Accompagnement des structures sur les enjeux liés aux AT/MP, au handicap et à la gestion des situations sensibles.",
      price: "Sur devis",
      priceNote: "",
      features: [
        "Sessions d'information RH",
        "Conférences de sensibilisation",
        "Analyse de situations spécifiques",
        "Accompagnement sur-mesure"
      ]
    }
  ];

  return (
    <main className="page-transition pt-20">
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Tarifs</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="tarifs-title">
              Des prestations adaptées à vos besoins
            </h1>
            <p className="text-lg text-muted-foreground">
              Des tarifs transparents pour un accompagnement de qualité. 
              Chaque situation étant unique, un devis personnalisé peut être établi 
              après un premier échange gratuit.
            </p>
          </div>
        </div>
      </section>

      {/* Prestations Particuliers */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h2 className="text-3xl font-semibold mb-4">Accompagnement des particuliers</h2>
            <p className="text-muted-foreground max-w-2xl">
              Des services pensés pour vous accompagner à chaque étape de vos démarches.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {prestationsParticuliers.map((prestation, index) => (
              <Card 
                key={index} 
                className={`relative border-border ${prestation.popular ? 'ring-2 ring-accent' : ''}`}
                data-testid={`tarif-card-${index}`}
              >
                {prestation.popular && (
                  <div className="absolute -top-3 left-6">
                    <Badge className="bg-accent text-accent-foreground gap-1">
                      <Star className="w-3 h-3" fill="currentColor" />
                      Plus demandé
                    </Badge>
                  </div>
                )}
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center">
                        <prestation.icon className="w-6 h-6 text-accent" strokeWidth={1.5} />
                      </div>
                      <div>
                        <CardTitle className="text-xl">{prestation.title}</CardTitle>
                        {prestation.badge && (
                          <Badge variant="secondary" className="mt-1">{prestation.badge}</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  <CardDescription className="mt-3">{prestation.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="mb-6">
                    <p className="text-sm text-muted-foreground">{prestation.priceNote}</p>
                    <p className="text-4xl font-bold text-foreground">
                      {prestation.price}
                      {prestation.price !== "Sur devis" && <span className="text-lg font-normal text-muted-foreground"> €</span>}
                    </p>
                  </div>
                  <ul className="space-y-3">
                    {prestation.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter>
                  <Link to="/contact" className="w-full">
                    <Button className="w-full rounded-lg" variant={prestation.popular ? "default" : "outline"}>
                      Demander un devis
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Prestations Pro */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h2 className="text-3xl font-semibold mb-4">Séminaires et conseil aux entreprises</h2>
            <p className="text-muted-foreground max-w-2xl">
              Des interventions sur-mesure pour les organisations et les professionnels.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {prestationsPro.map((prestation, index) => (
              <Card key={index} className="border-border" data-testid={`tarif-pro-${index}`}>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center">
                      <prestation.icon className="w-6 h-6 text-accent" strokeWidth={1.5} />
                    </div>
                    <CardTitle className="text-xl">{prestation.title}</CardTitle>
                  </div>
                  <CardDescription className="mt-3">{prestation.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="mb-6">
                    {prestation.priceNote && (
                      <p className="text-sm text-muted-foreground">{prestation.priceNote}</p>
                    )}
                    <p className="text-3xl font-bold text-foreground">{prestation.price}</p>
                  </div>
                  <ul className="space-y-3">
                    {prestation.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter>
                  <Link to="/contact" className="w-full">
                    <Button className="w-full rounded-lg" variant="outline">
                      Nous contacter
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Note Section */}
      <section className="section-padding">
        <div className="max-w-3xl mx-auto text-center">
          <h3 className="text-2xl font-semibold mb-4">Premier échange gratuit</h3>
          <p className="text-muted-foreground mb-8">
            Chaque situation est unique. Avant tout engagement, je vous propose un premier 
            échange téléphonique gratuit de 20 minutes pour comprendre votre situation 
            et voir comment je peux vous accompagner.
          </p>
          <Link to="/contact">
            <Button size="lg" className="rounded-full px-8 gap-2" data-testid="tarifs-cta">
              Prendre rendez-vous
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </main>
  );
};
