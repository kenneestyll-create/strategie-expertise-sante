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
      <SEO title="MDPH : droits, démarches et stratégie dossier" description="Dossier MDPH : comprendre vos droits (AAH, RQTH, PCH), éviter les erreurs fréquentes et structurer votre demande. Guide stratégique adultes et enfants." path="/mdph" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Vos droits</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="mdph-title">
              MDPH : comprendre vos droits et structurer votre dossier
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
        <div className="max-w-3xl mx-auto space-y-8">

          {/* L'essentiel */}
          <div className="p-5 rounded-xl bg-[#1a1a2e]/[0.03] border border-[#C9A84C]/20">
            <h2 className="font-semibold text-base mb-3 text-foreground">L'essentiel à retenir</h2>
            <ul className="space-y-1.5 list-none pl-0 text-sm text-muted-foreground">
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>La MDPH est le guichet unique pour tous les droits liés au handicap (adultes et enfants)</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Principales prestations : <strong className="text-foreground">AAH, RQTH, PCH, CMI</strong> (adultes) — <strong className="text-foreground">AEEH, AESH, orientation scolaire</strong> (enfants)</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Délai légal : 4 mois — en pratique <strong className="text-foreground">4 à 12 mois</strong> selon les départements</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Les deux pièces qui font la différence : le <strong className="text-foreground">certificat médical</strong> et le <strong className="text-foreground">projet de vie</strong></span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Déconjugalisation AAH : seuls vos revenus personnels comptent depuis octobre 2023</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Tout refus peut être contesté : RAPO gratuit dans les 2 mois</span></li>
            </ul>
            <p className="text-xs text-muted-foreground mt-3 italic">Informations basées sur les règles MDPH et CAF en vigueur en 2026.</p>
          </div>

          {/* Structure dossier */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Ce que l'équipe pluridisciplinaire cherche dans votre dossier</h2>
            <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
              <p>
                L'équipe pluridisciplinaire ne cherche pas un diagnostic — elle en reçoit des centaines. Ce qu'elle évalue, c'est <strong className="text-foreground">l'impact concret de votre handicap sur votre vie quotidienne</strong> : vos limitations fonctionnelles, votre capacité à vous déplacer, travailler, vous concentrer, gérer le quotidien. Le formulaire Cerfa seul ne suffit pas. Ce sont le certificat médical et le projet de vie qui permettent à l'évaluateur de comprendre votre réalité.
              </p>
            </div>
          </div>

          {/* Certificat médical */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Le certificat médical : la pièce maîtresse</h2>
            <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
              <p>
                Un diagnostic seul ne suffit pas. Votre médecin doit décrire les <strong className="text-foreground">conséquences fonctionnelles concrètes</strong> : difficultés à la marche, fatigue invalidante, troubles de la concentration, douleurs chroniques, incapacité à maintenir une posture prolongée. Les effets secondaires des traitements sont souvent oubliés alors qu'ils pèsent parfois plus lourd que la pathologie elle-même dans l'évaluation.
              </p>
              <p>
                Joignez systématiquement les bilans spécialisés (psychiatre, rhumatologue, ergothérapeute) — ils étayent le certificat et donnent à l'équipe pluridisciplinaire une vision complète de votre situation.
              </p>
            </div>
          </div>

          {/* RSDAE */}
          <div>
            <h2 className="text-lg font-semibold mb-2">RSDAE : la clé pour le taux 50-79%</h2>
            <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
              <p>
                Si votre taux d'incapacité est entre 50% et 79%, l'AAH n'est accordée que si la CDAPH reconnaît une <strong className="text-foreground">Restriction Substantielle et Durable d'Accès à l'Emploi (RSDAE)</strong>. Dire "je ne travaille pas" ne suffit pas. Il faut démontrer que vos limitations — douleurs, fatigabilité, effets des traitements, troubles cognitifs — empêchent structurellement l'accès à un emploi durable. Le projet de vie est le document central pour cette démonstration.
              </p>
            </div>
          </div>

          {/* Enfant / mineur */}
          <div className="p-5 rounded-xl bg-accent/5 border border-accent/15">
            <h2 className="text-lg font-semibold mb-2 text-foreground">Dossier MDPH enfant et mineur</h2>
            <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
              <p>
                Les enfants de moins de 20 ans relèvent de l'<strong className="text-foreground">AEEH</strong> (Allocation d'Éducation de l'Enfant Handicapé), et non de l'AAH. Le dossier inclut les mêmes pièces, complétées par le <strong className="text-foreground">GEVA-Sco</strong> pour les demandes scolaires (AESH, orientation ULIS, PPS). Depuis 2024, la RQTH est automatique pour les jeunes de 15 à 20 ans bénéficiant de l'AEEH, de la PCH ou d'un PPS.
              </p>
              <p>
                De nombreux dossiers MDPH concernent des <strong className="text-foreground">troubles invisibles ou neurodéveloppementaux</strong> (TSA, TDAH, troubles dys, épilepsie), même sans handicap moteur. Ces situations nécessitent des bilans spécialisés récents et un certificat médical qui décrit précisément les retentissements fonctionnels.
              </p>
              <p className="text-xs italic">Conseil : anticipez le dossier 6 mois avant chaque rentrée scolaire. Les droits sont désormais alignés sur les cycles scolaires depuis 2026.</p>
            </div>
          </div>

          {/* Pourquoi certains dossiers sont refusés */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Pourquoi certains dossiers MDPH sont refusés</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              La majorité des refus ne viennent pas de l'absence de handicap, mais d'un <strong className="text-foreground">dossier qui ne traduit pas la réalité vécue</strong> : limitations mal décrites, certificat trop médical et pas assez fonctionnel, absence de projet de vie, manque d'éléments sur l'impact concret au quotidien. L'équipe pluridisciplinaire ne peut reconnaître ce qu'elle ne lit pas dans le dossier.
            </p>
          </div>

          {/* AAH + travail */}
          <div>
            <h2 className="text-lg font-semibold mb-2">AAH et travail : le cumul est possible</h2>
            <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
              <p>
                Contrairement à une idée répandue, <strong className="text-foreground">travailler ne supprime pas automatiquement l'AAH</strong>. L'allocation fonctionne en différentiel : un abattement est appliqué sur vos revenus d'activité, et l'AAH complète la différence. Vous pouvez estimer le montant avec notre <Link to="/calculatrice-aah" className="text-accent hover:underline">simulateur AAH</Link>.
              </p>
            </div>
          </div>

          {/* Invalidité CPAM vs MDPH */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Invalidité CPAM et taux MDPH : deux systèmes différents</h2>
            <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
              <p>
                La pension d'invalidité (versée par la CPAM) et le taux d'incapacité (évalué par la MDPH) sont <strong className="text-foreground">deux dispositifs distincts</strong> avec des barèmes différents. L'un ne garantit pas l'autre. En revanche, ils peuvent se cumuler sous conditions de plafond. Une personne en invalidité catégorie 2 peut très bien avoir un taux MDPH inférieur à 50%, et inversement.
              </p>
            </div>
          </div>

          {/* Erreurs fréquentes */}
          <div>
            <h2 className="text-lg font-semibold mb-3">Erreurs fréquentes</h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Déposer un dossier sans projet de vie</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ C'est le seul document où vous décrivez l'impact réel du handicap sur votre quotidien. Sans lui, la CDAPH ne voit que le diagnostic.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Un certificat médical qui liste les pathologies sans décrire les limitations</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ L'équipe pluridisciplinaire évalue les conséquences fonctionnelles, pas les diagnostics. Décrivez ce que vous ne pouvez plus faire.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Attendre le dernier moment pour renouveler</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Déposez votre renouvellement 6 mois avant l'échéance. Un retard peut entraîner une rupture de droits et de versements.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Penser que le refus est définitif</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Le RAPO est gratuit, dans les 2 mois, et aboutit régulièrement. Renforcez votre dossier avec des éléments nouveaux avant de le redéposer.</p>
                </div>
              </div>
            </div>
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
    answer: "Oui, vous disposez de 2 mois après la notification pour déposer un recours administratif préalable obligatoire (RAPO) auprès de la MDPH. Ce recours est gratuit. Si le RAPO est rejeté, vous avez 2 mois pour saisir le tribunal judiciaire (pôle social). Renforcez votre dossier avec des éléments nouveaux avant de redéposer."
  },
  {
    question: "Le projet de vie est-il obligatoire ?",
    answer: "Le projet de vie n'est pas juridiquement obligatoire, mais il est fortement recommandé. C'est le seul document où vous pouvez décrire concrètement l'impact du handicap sur votre quotidien. Son absence affaiblit significativement le dossier, notamment pour la reconnaissance de la RSDAE (taux 50-79%)."
  },
  {
    question: "L'AAH est-elle cumulable avec un salaire ?",
    answer: "Oui. L'AAH fonctionne en différentiel : un abattement est appliqué sur vos revenus d'activité, et l'allocation complète la différence. Travailler ne supprime pas l'AAH. Vous pouvez estimer le montant avec le simulateur AAH du site."
  },
  {
    question: "Quelle différence entre invalidité CPAM et taux MDPH ?",
    answer: "Ce sont deux systèmes distincts avec des barèmes différents. La pension d'invalidité est versée par la CPAM suite à une maladie ou un accident non professionnel. Le taux d'incapacité est évalué par la MDPH pour l'accès aux droits handicap. Ils peuvent se cumuler, mais l'un ne garantit pas l'autre."
  },
  {
    question: "Mon enfant peut-il bénéficier d'un dossier MDPH ?",
    answer: "Oui. Les enfants de moins de 20 ans relèvent de l'AEEH (Allocation d'Éducation de l'Enfant Handicapé). Le dossier MDPH enfant couvre aussi les aides scolaires (AESH, orientation ULIS) via le GEVA-Sco. Depuis 2024, la RQTH est automatique pour les 15-20 ans sous AEEH, PCH ou PPS. Les troubles invisibles (TSA, TDAH, troubles dys) sont éligibles."
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
