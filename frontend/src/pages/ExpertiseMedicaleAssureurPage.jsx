import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { SEO } from '@/components/SEO';
import { Button } from '@/components/ui/button';
import { FileText, AlertTriangle, Scale, ArrowRight, ChevronRight } from 'lucide-react';

const FAQ_ITEMS = [
  {
    question: "Puis-je refuser l'expertise médicale demandée par mon assureur ?",
    answer: "Le refus est possible mais rarement opportun : la plupart des contrats en font une condition d'instruction du dossier, et un refus non motivé peut entraîner la suspension de l'indemnisation. La bonne stratégie n'est pas de refuser l'expertise, mais de s'y présenter préparé, si possible assisté d'un médecin de recours."
  },
  {
    question: "Qui paie le médecin de recours qui m'assiste ?",
    answer: "Ses honoraires (de l'ordre de 300 à 800 € en moyenne pour une assistance à expertise) restent à votre charge, sauf si vous disposez d'une garantie protection juridique : la plupart de ces contrats prennent en charge tout ou partie de ces frais. Vérifiez votre contrat avant l'expertise."
  },
  {
    question: "Quel délai pour contester les conclusions de l'expertise ?",
    answer: "Il n'existe pas de délai unique : la contestation amiable doit intervenir rapidement après notification du rapport (idéalement sous 30 jours), et l'action judiciaire est encadrée par la prescription biennale de l'article L.114-1 du Code des assurances — deux ans à compter de l'événement qui y donne naissance. Chaque situation mérite une analyse des délais applicables."
  },
  {
    question: "L'assureur peut-il suspendre mes indemnités pendant l'expertise ?",
    answer: "Certains assureurs suspendent le versement dans l'attente des conclusions. Cette pratique dépend des stipulations contractuelles et n'est pas toujours fondée. Si la suspension se prolonge de manière injustifiée, une mise en demeure puis une action en référé peuvent être envisagées."
  },
  {
    question: "Quelle différence entre expertise amiable et expertise judiciaire ?",
    answer: "L'expertise amiable est organisée par l'assureur avec un médecin qu'il mandate ; l'expertise judiciaire est ordonnée par le juge (souvent en référé sur le fondement de l'article 145 du Code de procédure civile) et confiée à un expert indépendant inscrit sur une liste de cour d'appel. Les conclusions d'une expertise judiciaire ont un poids nettement supérieur en cas de litige."
  }
];

export const ExpertiseMedicaleAssureurPage = () => {
  useEffect(() => {
    const scripts = [
      ['assureur-faq-schema', {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": FAQ_ITEMS.map(f => ({
          "@type": "Question",
          "name": f.question,
          "acceptedAnswer": { "@type": "Answer", "text": f.answer }
        }))
      }],
      ['assureur-breadcrumb-schema', {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
          { "@type": "ListItem", "position": 1, "name": "Accueil", "item": "https://strategie-expertise-sante.fr/" },
          { "@type": "ListItem", "position": 2, "name": "Expertise médicale", "item": "https://strategie-expertise-sante.fr/expertise-medicale" },
          { "@type": "ListItem", "position": 3, "name": "Assureur", "item": "https://strategie-expertise-sante.fr/expertise-medicale/assureur" }
        ]
      }],
      ['assureur-article-schema', {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Expertise médicale demandée par votre assureur : la stratégie complète",
        "description": "Pièges spécifiques à l'expertise d'assurance, préparation en 5 étapes, voies de contestation des conclusions.",
        "datePublished": "2026-08-04",
        "dateModified": "2026-08-04",
        "author": { "@type": "Organization", "name": "Stratégie & Expertise Santé", "url": "https://strategie-expertise-sante.fr" },
        "publisher": { "@type": "Organization", "name": "Stratégie & Expertise Santé" },
        "mainEntityOfPage": "https://strategie-expertise-sante.fr/expertise-medicale/assureur"
      }]
    ];
    scripts.forEach(([id, json]) => {
      const s = document.createElement('script');
      s.id = id;
      s.type = 'application/ld+json';
      s.textContent = JSON.stringify(json);
      document.head.appendChild(s);
    });
    return () => scripts.forEach(([id]) => { const el = document.getElementById(id); if (el) el.remove(); });
  }, []);

  return (
    <main className="page-transition pt-20">
      <SEO title="Expertise médicale assureur : stratégie, préparation, recours" description="Convoqué à une expertise médicale par votre assureur ? Pièges à connaître, préparation en 5 étapes, contestation des conclusions — le guide stratégique." path="/expertise-medicale/assureur" />

      {/* Breadcrumb */}
      <nav className="max-w-4xl mx-auto px-6 lg:px-8 pt-6" aria-label="Fil d'Ariane" data-testid="assureur-breadcrumb">
        <ol className="flex items-center gap-1.5 text-sm text-muted-foreground flex-wrap">
          <li><Link to="/" className="hover:text-accent transition-colors">Accueil</Link></li>
          <li><ChevronRight className="w-3.5 h-3.5" /></li>
          <li><Link to="/expertise-medicale" className="hover:text-accent transition-colors">Expertise médicale</Link></li>
          <li><ChevronRight className="w-3.5 h-3.5" /></li>
          <li className="text-foreground font-medium" aria-current="page">Assureur</li>
        </ol>
      </nav>

      {/* Hero */}
      <section className="section-padding pt-8 bg-secondary/40">
        <div className="max-w-4xl mx-auto">
          <span className="text-sm font-medium text-accent uppercase tracking-wider">Guide stratégique</span>
          <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="assureur-title">
            Expertise médicale demandée par votre assureur&nbsp;: la stratégie complète
          </h1>
          {/* Réponse rapide — candidate featured snippet */}
          <div className="border-l-4 border-accent bg-card rounded-r-xl p-5" data-testid="assureur-quick-answer">
            <p className="text-foreground/90 leading-relaxed">
              L'expertise médicale demandée par votre assureur est réalisée par un médecin qu'il mandate et rémunère, selon les définitions de votre contrat — souvent plus restrictives que celles de la sécurité sociale. Vous avez le droit d'être assisté par un médecin de recours de votre choix, de produire des dires contradictoires, et de contester les conclusions par une contre-expertise amiable ou une expertise judiciaire.
            </p>
          </div>
        </div>
      </section>

      {/* Pourquoi */}
      <section className="section-padding" data-testid="assureur-pourquoi">
        <div className="max-w-4xl mx-auto space-y-6 text-foreground/90 leading-relaxed">
          <h2 className="text-3xl font-semibold mb-3">Pourquoi votre assureur demande une expertise médicale</h2>
          <p className="text-muted-foreground">
            Prévoyance, assurance emprunteur, garantie accidents de la vie, contrat invalidité&nbsp;: avant de verser ou de maintenir une indemnisation, l'assureur fait évaluer votre état de santé par un médecin expert. Cette expertise conditionne l'ouverture, le montant et la durée de vos garanties.
          </p>
          <div>
            <h3 className="text-xl font-semibold mb-2">La mission du médecin expert mandaté (et ce qu'elle n'est pas)</h3>
            <p>
              Le médecin expert d'assurance intervient dans le cadre d'une mission rédigée par l'assureur, qui le rémunère. Il ne soigne pas et ne vous conseille pas&nbsp;: il évalue. Ses conclusions peuvent différer sensiblement de celles de votre médecin traitant ou d'un médecin de recours — non par malveillance, mais parce que la grille d'analyse n'est pas la même. Comprendre cette position est le premier pas d'une préparation efficace.
            </p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">Définitions contractuelles ou sécurité sociale&nbsp;: la différence qui change tout</h3>
            <p>
              L'évaluation s'effectue selon les définitions de votre contrat — invalidité, ITT, taux d'incapacité, seuils de déclenchement (33&nbsp;%, 66&nbsp;%)&nbsp;— et non selon les règles du régime général. Un même état de santé peut ainsi ouvrir droit à une pension d'invalidité de la sécurité sociale tout en restant sous le seuil contractuel de votre prévoyance. Avant toute expertise, la lecture précise de ces définitions est indispensable&nbsp;: elle détermine ce que l'expert va réellement mesurer.
            </p>
          </div>
        </div>
      </section>

      {/* 3 pièges */}
      <section className="section-padding bg-card" data-testid="assureur-pieges">
        <div className="max-w-4xl mx-auto space-y-6 text-foreground/90 leading-relaxed">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-accent" strokeWidth={1.5} />
            <h2 className="text-3xl font-semibold">Les 3 pièges spécifiques à l'expertise d'assurance</h2>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">1. La consolidation prononcée trop tôt</h3>
            <p>
              Déclarer votre état «&nbsp;consolidé&nbsp;» fige juridiquement la situation&nbsp;: les prestations sont calculées à cette date, et revenir en arrière exige de démontrer une aggravation médicalement documentée. Si votre état demeure évolutif (soins en cours, intervention programmée, pathologie fluctuante), ce point doit être contesté immédiatement, pièces à l'appui.
            </p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">2. Le barème AIPP n'est pas celui des tribunaux</h3>
            <p>
              En matière d'assurance, l'expert applique le plus souvent le barème indicatif AIPP (droit commun), distinct du barème du Concours Médical utilisé devant les juridictions et de celui de la sécurité sociale. Pour un même préjudice, l'écart de taux entre barèmes peut être significatif — et chaque point d'écart se chiffre. C'est l'un des arguments les plus solides pour solliciter, le cas échéant, une expertise judiciaire. Pour situer les ordres de grandeur, vous pouvez utiliser notre <Link to="/calculatrice-ipp" className="text-accent underline underline-offset-2 hover:no-underline">calculatrice de taux d'IPP</Link>.
            </p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">3. L'imputabilité et l'«&nbsp;état antérieur&nbsp;»</h3>
            <p>
              Conclure que vos troubles préexistaient au sinistre ou en sont indépendants permet d'exclure tout ou partie de la garantie. C'est le terrain de contestation le plus technique&nbsp;: il se gagne avec un dossier médical chronologique complet et une argumentation contradictoire structurée, idéalement portée par un médecin de recours.
            </p>
          </div>
        </div>
      </section>

      {/* Préparation 5 étapes */}
      <section className="section-padding" data-testid="assureur-preparation">
        <div className="max-w-4xl mx-auto space-y-6 text-foreground/90 leading-relaxed">
          <h2 className="text-3xl font-semibold mb-3">Votre préparation en 5 étapes avant le rendez-vous</h2>
          <div>
            <h3 className="text-xl font-semibold mb-2">1. Réunir un dossier médical exhaustif</h3>
            <p>Certificats, comptes-rendus opératoires et d'imagerie, ordonnances, arrêts de travail&nbsp;: ce qui n'est pas communiqué à l'expert n'existera pas dans son rapport. Classez les pièces par ordre chronologique.</p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">2. Décrypter votre contrat</h3>
            <p>Identifiez les définitions applicables (invalidité, ITT, IPP), les exclusions et les seuils de déclenchement. Ces clauses conditionnent la mission de l'expert et donc votre stratégie.</p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">3. Solliciter un médecin de recours</h3>
            <p>Vous pouvez être assisté, le jour de l'expertise, par un médecin de votre choix. Ses honoraires peuvent être pris en charge par une garantie <Link to="/protection-juridique" className="text-accent underline underline-offset-2 hover:no-underline">protection juridique</Link> si vous en disposez. Sa présence rééquilibre le rapport de force technique.</p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">4. Anticiper les dires contradictoires</h3>
            <p>Après l'examen, votre médecin de recours peut produire des observations écrites («&nbsp;dires&nbsp;») que l'expert est tenu d'intégrer et de discuter point par point dans son rapport final.</p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">5. Le jour J&nbsp;: précision et cohérence</h3>
            <p>Décrivez le retentissement réel de votre état sur la vie quotidienne et professionnelle, sans minimiser ni dramatiser. Les réponses vagues ou contradictoires avec le dossier sont systématiquement relevées. Notez, dès la sortie, le déroulé de l'examen&nbsp;: durée, actes pratiqués, questions posées.</p>
          </div>
        </div>
      </section>

      {/* Contestation */}
      <section className="section-padding bg-card" data-testid="assureur-contestation">
        <div className="max-w-4xl mx-auto space-y-6 text-foreground/90 leading-relaxed">
          <div className="flex items-center gap-2">
            <Scale className="w-6 h-6 text-accent" strokeWidth={1.5} />
            <h2 className="text-3xl font-semibold">Conclusions défavorables&nbsp;: les 3 voies de contestation</h2>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">1. La contre-expertise amiable</h3>
            <p>Demandée par écrit à l'assureur, appuyée d'un rapport médical contradictoire. Son acceptation reste discrétionnaire, mais une demande argumentée aboutit plus souvent qu'on ne le croit — l'assureur préfère généralement éviter le judiciaire.</p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">2. L'expertise judiciaire (article 145 CPC)</h3>
            <p>Sollicitée en référé devant le tribunal judiciaire, elle aboutit à la désignation d'un expert indépendant inscrit sur la liste d'une cour d'appel. C'est la voie la plus puissante lorsque l'écart entre les conclusions de l'expert d'assurance et celles de votre médecin de recours est significatif.</p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">3. La réargumentation sur pièces et la médiation</h3>
            <p>Production d'un rapport médical contradictoire détaillé, éventuellement accompagnée d'une saisine de la Médiation de l'Assurance. Utile pour les litiges d'interprétation contractuelle sans divergence médicale majeure.</p>
          </div>
          <div className="border border-accent/30 bg-accent/5 rounded-xl p-4">
            <p className="text-sm">
              <strong>Délai à surveiller&nbsp;:</strong> la prescription biennale (articles L.114-1 et L.114-2 du Code des assurances) enferme la plupart des actions contre l'assureur dans un délai de <strong>deux ans</strong>. Certains actes l'interrompent (lettre recommandée AR relative au règlement de l'indemnité, désignation d'expert, citation en justice). Ne laissez jamais courir ce délai pendant des négociations amiables qui s'enlisent.
            </p>
          </div>
        </div>
      </section>

      {/* Cas concret */}
      <section className="section-padding" data-testid="assureur-cas-concret">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-semibold mb-4">Cas concret (anonymisé)</h2>
          <div className="border border-border rounded-2xl p-6 text-foreground/90 leading-relaxed space-y-3">
            <p>
              Un artisan couvert par un contrat de prévoyance est victime d'une chute avec fracture complexe de l'épaule. L'expert mandaté par l'assureur conclut à une consolidation à 10 mois avec un taux AIPP de 8&nbsp;% — sous le seuil contractuel de déclenchement de la rente (10&nbsp;%). Assisté d'un médecin de recours lors d'une seconde évaluation, il fait valoir des soins toujours en cours et une limitation fonctionnelle sous-évaluée&nbsp;; les dires contradictoires contraignent l'expert à motiver chaque écart. La contre-expertise amiable aboutit à un taux de 12&nbsp;% et au report de la date de consolidation&nbsp;: la garantie se déclenche, avec effet rétroactif sur les indemnités journalières.
            </p>
            <p className="text-sm text-muted-foreground">
              Illustration type construite à partir de situations récurrentes — chaque dossier reste unique et mérite une analyse propre.
            </p>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="section-padding bg-card" data-testid="assureur-faq">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-semibold mb-6">Questions fréquentes — expertise médicale et assureur</h2>
          <div className="space-y-4">
            {FAQ_ITEMS.map((f, i) => (
              <div key={i} className="border border-border rounded-xl p-5" data-testid={`assureur-faq-${i}`}>
                <h3 className="font-semibold mb-2">{f.question}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA + maillage */}
      <section className="section-padding" data-testid="assureur-cta-section">
        <div className="max-w-4xl mx-auto">
          <div className="bg-primary text-primary-foreground rounded-2xl p-8 text-center mb-10">
            <FileText className="w-10 h-10 mx-auto mb-3 opacity-80" strokeWidth={1.5} />
            <h2 className="text-2xl font-semibold mb-2">Vous avez déjà reçu le rapport d'expertise&nbsp;?</h2>
            <p className="opacity-80 mb-5 max-w-xl mx-auto">
              Faites-le analyser&nbsp;: contradictions entre praticiens, taux retenus, date de consolidation, leviers de contestation — rapport complet et personnalisé sous 2&nbsp;h.
            </p>
            <Button asChild size="lg" variant="secondary" data-testid="assureur-cta-dossier">
              <Link to="/dossier-express">Faire analyser mon rapport d'expertise <ArrowRight className="w-4 h-4 ml-1" /></Link>
            </Button>
          </div>
          <h2 className="text-xl font-semibold mb-4">Pour aller plus loin</h2>
          <div className="grid sm:grid-cols-2 gap-3">
            {[
              { to: '/expertise-medicale', label: "Expertise médicale : le guide complet", desc: 'Assureur, MDPH, tribunal — la page pilier' },
              { to: '/guide/expertise-medicale-defavorable-recours', label: 'Expertise défavorable : les recours', desc: 'Guide pratique de contestation' },
              { to: '/protection-juridique', label: 'Mobiliser votre protection juridique', desc: 'Prise en charge du médecin de recours' },
              { to: '/calculatrice-ipp', label: "Calculer votre taux d'IPP", desc: 'Simulateur gratuit — barèmes officiels' },
            ].map((r, i) => (
              <Link key={i} to={r.to} className="group border border-border rounded-xl p-4 hover:border-accent/40 hover:bg-muted/30 transition-colors" data-testid={`assureur-ressource-${i}`}>
                <span className="flex items-start justify-between gap-3">
                  <span>
                    <span className="block font-medium text-sm text-foreground group-hover:text-accent transition-colors">{r.label}</span>
                    <span className="block text-xs text-muted-foreground mt-1">{r.desc}</span>
                  </span>
                  <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-accent shrink-0 mt-0.5 transition-colors" />
                </span>
              </Link>
            ))}
          </div>
          <p className="mt-10 text-xs text-muted-foreground italic">
            Cadre légal mobilisé&nbsp;: Code des assurances, articles L.114-1 et L.114-2&nbsp;; Code de procédure civile, article&nbsp;145&nbsp;; Code de déontologie médicale, articles 105 et 106. Les informations de cette page sont fournies à titre informatif et ne constituent ni un avis médical ni un avis juridique&nbsp;; chaque situation nécessite une analyse individuelle.
          </p>
        </div>
      </section>
    </main>
  );
};

export default ExpertiseMedicaleAssureurPage;
