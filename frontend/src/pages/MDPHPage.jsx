import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { useState, useEffect } from 'react';
import { 
  ArrowRight, 
  Home, 
  BadgeCheck, 
  CreditCard, 
  Users,
  CheckCircle,
  FileText,
  Heart,
  Compass,
  ChevronDown
} from 'lucide-react';

export const MDPHPage = () => {
  const aides = [
    { icon: CreditCard, title: "AAH", description: "Allocation aux Adultes Handicapés" },
    { icon: BadgeCheck, title: "RQTH", description: "Reconnaissance de la Qualité de Travailleur Handicapé" },
    { icon: CreditCard, title: "CMI", description: "Carte mobilité inclusion (invalidité, priorité, stationnement)" },
    { icon: Users, title: "Aide humaine", description: "Aide humaine ou tierce personne" }
  ];

  const avantages = [
    "Faire reconnaître officiellement un handicap",
    "Obtenir des aides financières ou humaines",
    "Faciliter certaines démarches administratives"
  ];

  const accompagnement = [
    { icon: Compass, text: "Mieux comprendre les démarches MDPH" },
    { icon: FileText, text: "Analyser les droits possibles" },
    { icon: Users, text: "Orienter vers les professionnels adaptés si nécessaire" }
  ];

  return (
    <main className="page-transition pt-20">
      <SEO title="MDPH — Droits et démarches" description="Guide complet MDPH : démarches, droits, AAH, RQTH. Accompagnement personnalisé pour votre dossier handicap." path="/mdph" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Vos droits</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="mdph-title">
              MDPH : comprendre vos droits et vos démarches
            </h1>
            <p className="text-lg text-muted-foreground">
              La MDPH (Maison Départementale des Personnes Handicapées) accompagné les personnes 
              en situation de handicap dans leurs démarches administratives et l'accès à leurs droits.
            </p>
          </div>
        </div>
      </section>

      {/* Aides Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-semibold mb-4">Principales aides possibles</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              La MDPH peut vous permettre d'accéder à différentes aides et reconnaissances.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {aides.map((aide, index) => (
              <Card 
                key={index} 
                className="card-lift border-border text-center"
                data-testid={`aide-${index}`}
              >
                <CardContent className="p-6">
                  <div className="w-14 h-14 bg-accent/10 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <aide.icon className="w-7 h-7 text-accent" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-semibold text-xl mb-2">{aide.title}</h3>
                  <p className="text-sm text-muted-foreground">{aide.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pourquoi Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-semibold mb-6">
                Pourquoi constituer un dossier MDPH
              </h2>
              <p className="text-muted-foreground mb-6">
                Un dossier MDPH permet notamment :
              </p>
              <div className="space-y-4">
                {avantages.map((avantage, index) => (
                  <div 
                    key={index} 
                    className="flex items-start gap-3 bg-background p-4 rounded-xl"
                    data-testid={`avantage-${index}`}
                  >
                    <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    <span className="font-medium">{avantage}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/7176319/pexels-photo-7176319.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Démarches administratives"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SEO Content */}
      <section className="section-padding" data-testid="mdph-seo-content">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-xl font-semibold mb-4">Comprendre le rôle de la MDPH</h2>
          <div className="text-sm text-muted-foreground space-y-3 leading-relaxed">
            <p>
              La Maison Départementale des Personnes Handicapées (MDPH) est un guichet unique présent dans chaque département. Elle centralise les demandes liées au handicap et oriente les personnes vers les aides et prestations auxquelles elles peuvent prétendre : AAH, RQTH, carte mobilité inclusion, aide humaine, orientation professionnelle.
            </p>
            <p>
              La demande auprès de la MDPH passe par le dépôt d'un dossier comprenant un formulaire Cerfa, un certificat médical détaillé et un projet de vie. Ce dossier est ensuite évalué par une équipe pluridisciplinaire qui émet un avis transmis à la CDAPH pour décision.
            </p>
            <p>
              La qualité du dossier est déterminante : un certificat médical trop succinct, un projet de vie absent ou mal rédigé, des pièces justificatives incomplètes sont les causes les plus fréquentes de refus ou de sous-évaluation du taux d'incapacité. Un accompagnement en amont permet de structurer le dossier pour maximiser les chances d'obtenir les droits auxquels vous pouvez prétendre.
            </p>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <MDPHPageFAQ />

      {/* Accompagnement Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <Heart className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="text-3xl font-semibold mb-4">
              Accompagnement
            </h2>
            <p className="text-primary-foreground/70">
              Je propose un accompagnement afin de :
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-6 mb-10">
            {accompagnement.map((item, index) => (
              <div 
                key={index} 
                className="bg-primary-foreground/10 rounded-xl p-6 text-center"
                data-testid={`accompagnement-mdph-${index}`}
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
                data-testid="mdph-cta-button"
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


const mdphFaqData = [
  {
    question: "Combien de temps prend le traitement d'un dossier MDPH ?",
    answer: "Le délai légal est de 4 mois à compter du dépôt du dossier complet. En pratique, les délais varient selon les départements et peuvent atteindre 6 à 12 mois. Un dossier complet et bien structuré réduit les risques de demande de pièces complémentaires et accélère le traitement."
  },
  {
    question: "Peut-on contester une décision MDPH ?",
    answer: "Oui, vous disposez de 2 mois après la notification pour déposer un recours administratif préalable obligatoire (RAPO) auprès de la MDPH, puis de 2 mois supplémentaires pour saisir le tribunal judiciaire si le RAPO est rejeté."
  },
  {
    question: "Le projet de vie est-il obligatoire ?",
    answer: "Le projet de vie n'est pas juridiquement obligatoire, mais il est fortement recommandé. C'est le seul document où vous pouvez décrire concrètement l'impact du handicap sur votre quotidien. Son absence affaiblit significativement le dossier, notamment pour la reconnaissance de la RSDAE."
  }
];

const MDPHPageFAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);

  useEffect(() => {
    document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
      try { if (JSON.parse(s.textContent)['@type'] === 'FAQPage') s.remove(); } catch {}
    });
    const script = document.createElement('script');
    script.id = 'mdph-faq-schema';
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": mdphFaqData.map(f => ({
        "@type": "Question",
        "name": f.question,
        "acceptedAnswer": { "@type": "Answer", "text": f.answer }
      }))
    });
    document.head.appendChild(script);
    return () => { const el = document.getElementById('mdph-faq-schema'); if (el) el.remove(); };
  }, []);

  return (
    <section className="section-padding bg-card" data-testid="mdph-faq">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-lg font-semibold mb-4">Questions fréquentes sur la MDPH</h2>
        <div className="space-y-2">
          {mdphFaqData.map((faq, i) => (
            <div key={i} className="border border-border rounded-xl overflow-hidden">
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
                data-testid={`mdph-faq-${i}`}
              >
                <span className="font-medium text-sm text-foreground pr-4">{faq.question}</span>
                <ChevronDown className={`w-4 h-4 text-muted-foreground shrink-0 transition-transform ${openIndex === i ? 'rotate-180' : ''}`} />
              </button>
              {openIndex === i && (
                <div className="px-4 pb-4">
                  <p className="text-sm text-muted-foreground leading-relaxed">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
