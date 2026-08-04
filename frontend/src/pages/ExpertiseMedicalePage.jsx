import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { DossierExpressCTA } from '@/components/DossierExpressCTA';
import { PillarLeadMagnet } from '@/components/PillarLeadMagnet';
import { TerrainNote } from '@/components/TerrainNote';
import { 
  ArrowRight, 
  Stethoscope, 
  FileText, 
  ClipboardList, 
  UserCheck,
  CheckCircle,
  AlertTriangle,
  BookOpen,
  Phone,
  ChevronDown
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
      <SEO title="Expertise Médicale : Stratégie Assureur, MDPH, Tribunal" description="Stratégie pour une expertise médicale face à l'assureur, en procédure MDPH ou au tribunal. Préparation, dires contradictoires, contre-expertise." path="/expertise-medicale" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Guide pratique</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="expertise-title">
              Expertise médicale : stratégie face à l'assureur et au tribunal
            </h1>
            <p className="text-lg text-muted-foreground">
              Une expertise médicale est une étape déterminante dans les procédures face à un assureur, en démarche MDPH ou devant le tribunal.
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
                  loading="lazy" 
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
              Une expertise médicale se déroule généralement en plusieurs etapes.
            </p>
          </div>

          <div className="max-w-3xl mx-auto">
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-6 top-0 bottom-0 w-px bg-border" />

              {etapes.map((étape, index) => (
                <div 
                  key={index} 
                  className="relative flex items-start gap-6 pb-8 last:pb-0"
                  data-testid={`etape-${index}`}
                >
                  <div className="relative z-10 w-12 h-12 bg-background border-2 border-accent rounded-full flex items-center justify-center flex-shrink-0">
                    <étape.icon className="w-5 h-5 text-accent" strokeWidth={1.5} />
                  </div>
                  <div className="pt-3">
                    <p className="font-medium text-lg">{étape.text}</p>
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

      {/* ENRICHMENT — Préparation stratégique */}
      <section className="section-padding bg-secondary/30">
        <div className="max-w-4xl mx-auto space-y-10">

          {/* L'essentiel */}
          <div className="p-5 rounded-xl bg-[#1a1a2e]/[0.03] border border-[#C9A84C]/20" data-testid="expertise-essentiel">
            <h2 className="font-semibold text-base mb-3 text-foreground">L'essentiel à retenir</h2>
            <ul className="space-y-1.5 list-none pl-0 text-sm text-muted-foreground">
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Une expertise n'est pas un examen médical neutre : c'est un <strong className="text-foreground">acte juridique</strong> qui détermine votre indemnisation</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>L'expert est mandaté par <strong className="text-foreground">l'assureur ou le tribunal</strong> — il n'est pas votre médecin</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Le rapport produit fait <strong className="text-foreground">force probante</strong> : un oubli ou une minimisation devient quasi irréversible</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Vous avez le droit d'être assisté par un <strong className="text-foreground">médecin de recours</strong> et de produire des dires contradictoires</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Le pré-rapport peut être contesté avant signature ; après, seule la <strong className="text-foreground">contre-expertise</strong> reste possible</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Une expertise mal préparée se solde fréquemment par une indemnisation <strong className="text-foreground">sous-évaluée de plusieurs dizaines de milliers d'euros</strong></span></li>
            </ul>
            <p className="text-xs text-muted-foreground mt-3 italic">Référentiel : nomenclature Dintilhac, Code de procédure civile, jurisprudence des Cours d'appel 2024-2026.</p>
          </div>

          {/* Pourquoi c'est un acte stratégique */}
          <div>
            <h2 className="text-lg font-semibold mb-2">L'expertise médicale n'est pas un examen, c'est une procédure</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              La majorité des victimes abordent l'expertise comme une consultation médicale ordinaire. C'est précisément ce qui crée les indemnisations sous-évaluées. L'expert, choisi par l'assureur ou le juge, suit une mission écrite — il ne cherche pas à comprendre votre histoire, il <strong className="text-foreground">remplit une grille d'évaluation</strong>. Tout ce qui n'est pas explicitement dit, documenté et insisté ne figurera pas dans son rapport. Et tout ce qui figure dans son rapport devient la base juridique de votre indemnisation pour les années à venir.
            </p>
          </div>

          {/* Avant l'expertise */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Avant : la phase qui détermine 80% du résultat</h2>
            <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
              <p>
                La préparation se joue sur trois plans. <strong className="text-foreground">Le dossier médical</strong> doit être chronologique, exhaustif, et inclure tous les comptes rendus, examens et certificats — y compris les douleurs secondaires souvent négligées (lombaires après un coup du lapin, troubles du sommeil, retentissement psy). <strong className="text-foreground">Le carnet de doléances</strong> liste précisément ce que vous ne pouvez plus faire au quotidien : porter vos enfants, conduire plus de 20 minutes, dormir plus de 4h d'affilée. <strong className="text-foreground">Le médecin de recours</strong>, médecin spécialisé en réparation du dommage corporel, vous prépare et vous accompagne le jour J.
              </p>
              <p>
                Coût d'un médecin de recours : entre 800 et 3 000 € selon la complexité. Cet honoraire est souvent pris en charge par votre protection juridique, ou intégré aux indemnisations finales selon la nomenclature Dintilhac.
              </p>
            </div>
          </div>

          {/* Pendant l'expertise */}
          <div className="p-4 rounded-xl bg-muted/30 border border-border">
            <h3 className="font-medium text-sm text-foreground mb-1.5">Pendant : ce qui se joue vraiment ce jour-là</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              L'expert ouvre presque toujours par une question apparemment anodine : <em>"Comment ça va ?"</em> Répondre <em>"ça va"</em> par politesse coûte en moyenne 5 à 15 % de votre indemnisation finale. Décrivez objectivement : douleurs chroniques, limitations, fatigue, retentissement professionnel et familial. Ne minimisez rien, n'exagérez rien. Si une manipulation déclenche une douleur, dites-le — l'expert doit le consigner. Les émotions authentiques (larmes liées à la perte d'autonomie) documentent un préjudice psychologique réel, ne les retenez pas par pudeur.
            </p>
          </div>

          {/* Après — recours */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Après : pré-rapport, dires et contre-expertise</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Dans la majorité des procédures contradictoires, l'expert produit d'abord un <strong className="text-foreground">pré-rapport</strong>. C'est le moment décisif. Vous disposez généralement de 4 à 6 semaines pour produire des <strong className="text-foreground">dires contradictoires</strong> : observations écrites argumentant les points de désaccord. Une fois le rapport définitif déposé, seule la <strong className="text-foreground">contre-expertise judiciaire</strong> permet de le remettre en cause — procédure plus lourde, mais parfois indispensable. La contestation d'une expertise unilatérale d'assureur passe par une demande d'expertise contradictoire, refusable seulement avec motif sérieux.
            </p>
          </div>

          {/* Cas concret */}
          <div className="p-4 rounded-xl bg-accent/5 border border-accent/20" data-testid="expertise-cas-concret">
            <h3 className="font-medium text-sm text-foreground mb-2">Cas concret — Consolidation sans séquelles reconnues</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Un salarié victime d'un accident du travail au dos se présente seul à l'expertise 14 mois après les faits. L'expert constate "absence de séquelles objectivables" et propose une consolidation sans IPP. Le salarié signe le rapport, soulagé. Six mois plus tard, ses douleurs chroniques empirent et l'empêchent de tenir son poste. <strong className="text-foreground">Sans dires contradictoires déposés à l'époque</strong>, ses recours sont quasi épuisés. Il finira par obtenir, après 2 ans de procédure, une révision IPP à 8 % via une contre-expertise judiciaire — pour un préjudice réel évalué par un médecin de recours indépendant à 18 %. Une préparation initiale lui aurait évité 2 ans de procédure et plusieurs dizaines de milliers d'euros de manque à gagner.
            </p>
          </div>

          {/* Erreurs à éviter */}
          <div>
            <h3 className="font-medium text-sm text-foreground mb-3">Erreurs à éviter le jour de l'expertise</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Y aller seul, sans médecin de recours</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Face au médecin expert de l'assureur, vous êtes désarmé techniquement et juridiquement. Le médecin de recours impose le contradictoire et fait acter ce qui sinon serait minimisé.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Minimiser ses douleurs par pudeur ou par peur d'en faire trop</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ "Ça va à peu près" devient "absence de gêne fonctionnelle" dans le rapport. Décrivez ce que vous ne pouvez plus faire concrètement, avec exemples du quotidien.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Signer le rapport sans avoir produit de dires contradictoires</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Une fois le rapport définitif, seule la contre-expertise permet de le contester. Profitez de la phase pré-rapport pour faire acter par écrit chaque désaccord médical et chaque oubli.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Omettre les préjudices psychologiques et le retentissement professionnel</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Anxiété, troubles du sommeil, perte de confiance, reconversion forcée : tout cela relève d'un préjudice indemnisable distinct. Sans documentation médicale (psychologue, psychiatre), il sera ignoré.</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* Encart conversion */}
      <PillarLeadMagnet
        pageId="expertise-medicale"
        memoTitle="La phrase à NE JAMAIS dire au médecin expert"
        bulletPoints={[
          "L'expertise médicale n'est PAS un examen de soins — c'est un acte juridique",
          "La formule qui fait perdre votre IPP en 30 secondes",
          "Le journal des douleurs sur 4 semaines : votre meilleure arme",
          "Les dires sous 8 jours : votre seule contre-attaque écrite",
        ]}
      />

      <DossierExpressCTA
        testId="expertise-cta-dossier"
        title={"Expertise prochaine ou rapport déjà reçu\u00A0?"}
        text="Préparer une expertise demande 3 à 6 semaines de travail méthodique sur votre dossier. Contester un rapport défavorable exige une argumentation médicale et juridique précise. Le Dossier Express IA structure votre préparation ou votre contestation."
        ctaLabel="Préparer mon expertise"
      />

      {/* FAQ */}
      <ExpertiseFaq />

      <TerrainNote
        testId="expertise-terrain-note"
        text="Cette page condense ce que j'observe réellement en expertise : pré-rapports, dires contradictoires et contre-expertises suivis pas à pas avec mes accompagnés."
      />

      {/* Phase 2 — Sections enrichies Assureur + MDPH (déployées 2026-06-16) */}
      <ExpertisePhase2Sections />


      {/* Médecin Conseil — Strategic Link */}
      <section className="section-padding bg-accent/5 border-y border-accent/10" data-testid="expertise-médecin-conseil">
        <div className="max-w-4xl mx-auto">
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                <span className="text-sm font-medium text-accent uppercase tracking-wider">Choix stratégique</span>
              </div>
              <h2 className="text-2xl font-semibold mb-3">
                Comment choisir le bon médecin conseil ?
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Le médecin conseil de victime joue un rôle déterminant lors de l'expertise.
                Un choix inadapté peut compromettre votre indemnisation de manière irréversible.
                Découvrez notre approche pour vous orienter vers le bon professionnel.
              </p>
            </div>
            <div className="flex-shrink-0">
              <Link to="/medecin-conseil">
                <Button size="lg" className="rounded-full gap-2 bg-accent hover:bg-accent/90 text-accent-foreground" data-testid="expertise-médecin-conseil-cta">
                  <Phone className="w-4 h-4" />
                  En savoir plus
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
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

const expertiseFaqData = [
  {
    question: "Que dire et que ne pas dire lors d'une expertise médicale ?",
    answer: "Dites tout ce qui limite votre quotidien : douleurs chroniques, fatigue, troubles du sommeil, retentissement familial et professionnel. Décrivez ce que vous ne pouvez plus faire (porter, conduire longtemps, dormir sans réveil). Ne dites jamais 'ça va' par politesse — c'est l'erreur n°1, qui se traduit dans le rapport par 'absence de gêne fonctionnelle'. Ne minimisez ni n'exagérez. Si une manipulation est douloureuse, dites-le et faites-le consigner."
  },
  {
    question: "Puis-je refuser une manipulation douloureuse ou un examen invasif ?",
    answer: "Oui. Vous avez le droit absolu de refuser tout examen que vous jugez excessif ou douloureux. Faites consigner par écrit dans le rapport votre refus et son motif (douleur intense, antécédent médical, absence de pertinence). Ce refus motivé ne vous est pas opposable s'il est documenté."
  },
  {
    question: "Combien coûte un médecin de recours et qui paie ?",
    answer: "Les honoraires d'un médecin de recours (médecin conseil de victime) varient selon la complexité : 800 à 1 800 € pour un dossier classique, 1 800 à 4 000 € pour un dossier complexe avec plusieurs séquelles. Ces honoraires sont fréquemment pris en charge par votre assurance protection juridique. Selon la nomenclature Dintilhac, ils peuvent également être inclus dans les frais divers indemnisables au titre du préjudice corporel — l'avance reste à votre charge mais est récupérable."
  },
  {
    question: "Qu'est-ce qu'un dire contradictoire et à quoi sert-il ?",
    answer: "Un 'dire' est une observation écrite, signée par votre conseil ou votre médecin de recours, déposée auprès de l'expert pendant la phase de pré-rapport. Il sert à argumenter chaque désaccord médical, à demander des examens complémentaires, à faire acter une omission. L'expert a l'obligation d'y répondre dans son rapport définitif. C'est le seul moyen efficace d'influencer le contenu final d'une expertise."
  },
  {
    question: "Comment contester une expertise unilatérale d'assureur ?",
    answer: "Toute expertise réalisée par le seul médecin de l'assureur, sans contradictoire, peut être contestée. Vous pouvez demander une expertise médicale contradictoire (votre médecin de recours assiste l'examen et co-signe ou conteste les conclusions), refuser de signer un rapport unilatéral, ou saisir le tribunal pour obtenir une expertise judiciaire. La jurisprudence des Cours d'appel sanctionne régulièrement les rapports non contradictoires."
  },
  {
    question: "Quelle est la différence entre une expertise amiable et une expertise judiciaire ?",
    answer: "L'expertise amiable est demandée et organisée hors procédure judiciaire, généralement par l'assureur. Elle est plus rapide mais l'expert n'est pas désigné par un juge — sa partialité peut être plus marquée. L'expertise judiciaire est ordonnée par le tribunal qui désigne lui-même l'expert sur une liste agréée. Elle offre des garanties procédurales fortes (contradictoire obligatoire, dires opposables, sanctions en cas de manquement) mais prend 6 à 18 mois."
  },
  {
    question: "L'expertise est terminée et le rapport me semble injuste : que faire ?",
    answer: "Si vous êtes encore en phase de pré-rapport, déposez immédiatement des dires contradictoires argumentés. Si le rapport est définitif et déjà déposé, vous pouvez demander une contre-expertise (amiable si l'assureur l'accepte, judiciaire sinon). Joignez à votre demande un certificat médical critique rédigé par un médecin de recours, listant points par points les omissions, les évaluations sous-cotées et les éléments médicaux ignorés. La contre-expertise judiciaire est accordée si la demande est sérieusement motivée."
  }
];

const ExpertiseFaq = () => {
  const [openIndex, setOpenIndex] = useState(null);

  useEffect(() => {
    document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
      try { if (JSON.parse(s.textContent)['@type'] === 'FAQPage') s.remove(); } catch {}
    });
    const script = document.createElement('script');
    script.id = 'expertise-faq-schema';
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": expertiseFaqData.map(f => ({
        "@type": "Question",
        "name": f.question,
        "acceptedAnswer": { "@type": "Answer", "text": f.answer }
      }))
    });
    document.head.appendChild(script);
    return () => { const el = document.getElementById('expertise-faq-schema'); if (el) el.remove(); };
  }, []);

  return (
    <section className="section-padding bg-secondary/20" data-testid="expertise-faq">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold mb-8 text-center">Questions fréquentes sur l'expertise médicale</h2>
        <div className="space-y-2">
          {expertiseFaqData.map((faq, i) => (
            <div key={i} className="border border-border rounded-xl overflow-hidden bg-background">
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
                data-testid={`expertise-faq-${i}`}
              >
                <span className="font-medium text-sm text-foreground pr-4">{faq.question}</span>
                <ChevronDown className={`w-4 h-4 text-muted-foreground shrink-0 transition-transform ${openIndex === i ? 'rotate-180' : ''}`} />
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


// ─────────────────────────────────────────────────────────────────────────────
// PHASE 2 — Sections enrichies (déployées 2026-06-16)
// Ordre exécutif validé : ton factuel, neutre, juridiquement prudent.
// Aucune modification : Title / Meta / H1 / structure globale / maillage existant.
// Schemas ajoutés : MedicalScholarlyArticle + HowTo + BreadcrumbList
// ─────────────────────────────────────────────────────────────────────────────

const ExpertisePhase2Sections = () => {
  useEffect(() => {
    // Nettoyage des éventuels schemas Phase 2 résiduels
    ['expertise-howto-schema', 'expertise-breadcrumb-schema', 'expertise-medical-article-schema'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.remove();
    });

    // 2. BreadcrumbList Schema
    const breadcrumbScript = document.createElement('script');
    breadcrumbScript.id = 'expertise-breadcrumb-schema';
    breadcrumbScript.type = 'application/ld+json';
    breadcrumbScript.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Accueil", "item": "https://strategie-expertise-sante.fr/" },
        { "@type": "ListItem", "position": 2, "name": "Expertise médicale", "item": "https://strategie-expertise-sante.fr/expertise-medicale" }
      ]
    });
    document.head.appendChild(breadcrumbScript);

    // 3. MedicalScholarlyArticle Schema (author = Organization, signal E-E-A-T)
    const articleScript = document.createElement('script');
    articleScript.id = 'expertise-medical-article-schema';
    articleScript.type = 'application/ld+json';
    articleScript.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "MedicalScholarlyArticle",
      "headline": "Expertise médicale stratégique : assureur, AT, MDPH",
      "description": "Guide stratégique pour préparer une expertise médicale dans le cadre d'un contrat d'assurance, d'un dossier d'accident du travail ou d'une demande MDPH.",
      "author": {
        "@type": "Organization",
        "name": "Stratégie & Expertise Santé",
        "url": "https://strategie-expertise-sante.fr/"
      },
      "publisher": {
        "@type": "Organization",
        "name": "Stratégie & Expertise Santé",
        "url": "https://strategie-expertise-sante.fr/"
      },
      "datePublished": "2026-05-17",
      "dateModified": "2026-08-04",
      "about": [
        { "@type": "MedicalProcedure", "name": "Expertise médicale" }
      ],
      "audience": {
        "@type": "PeopleAudience",
        "audienceType": "Personnes engagées dans un dossier d'expertise médicale (assureur, CPAM, MDPH, juridiction)"
      },
      "mainEntityOfPage": "https://strategie-expertise-sante.fr/expertise-medicale"
    });
    document.head.appendChild(articleScript);

    return () => {
      ['expertise-howto-schema', 'expertise-breadcrumb-schema', 'expertise-medical-article-schema'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.remove();
      });
    };
  }, []);

  return (
    <>
      {/* SECTION ASSUREUR — synthèse, contenu détaillé sur /expertise-medicale/assureur */}
      <section className="section-padding bg-secondary/30" data-testid="expertise-phase2-assureur">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="w-5 h-5 text-accent" />
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Volet assureur</span>
          </div>
          <h2 className="text-3xl font-semibold mb-6" data-testid="expertise-phase2-assureur-h2">
            Expertise médicale et assureur&nbsp;: l'essentiel à retenir
          </h2>
          <div className="space-y-4 text-foreground/90 leading-relaxed">
            <p>
              Le médecin expert mandaté par votre assureur évalue votre état selon les <strong>définitions contractuelles</strong> de votre contrat — invalidité, ITT, taux d'incapacité — généralement plus restrictives que celles du régime général de la sécurité sociale. Trois points concentrent l'essentiel des litiges&nbsp;: une <strong>consolidation</strong> prononcée alors que l'état demeure évolutif, le taux retenu selon le <strong>barème AIPP</strong> (distinct du barème utilisé devant les juridictions) et l'<strong>imputabilité</strong> des troubles au sinistre, dont la remise en cause peut exclure tout ou partie de la garantie.
            </p>
            <p>
              Vous conservez des droits effectifs&nbsp;: être assisté le jour de l'expertise par un <strong>médecin de recours</strong> de votre choix, produire des <strong>dires contradictoires</strong> que l'expert doit discuter point par point, puis contester des conclusions défavorables par une contre-expertise amiable ou une expertise judiciaire — en surveillant la prescription biennale de deux ans (article L.114-1 du Code des assurances).
            </p>
          </div>
          <Link
            to="/expertise-medicale/assureur"
            className="group mt-6 flex items-start justify-between gap-4 border border-accent/30 bg-accent/5 rounded-xl p-5 hover:border-accent/60 hover:bg-accent/10 transition-colors"
            data-testid="expertise-assureur-guide-link"
          >
            <span>
              <span className="block font-semibold text-foreground group-hover:text-accent transition-colors">
                Expertise médicale demandée par votre assureur&nbsp;: le guide stratégique complet
              </span>
              <span className="block text-sm text-muted-foreground mt-1">
                Pièges spécifiques à l'expertise d'assurance, préparation en 5 étapes, voies de contestation détaillées.
              </span>
            </span>
            <ArrowRight className="w-5 h-5 text-accent shrink-0 mt-1 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </section>

      {/* SECTION MDPH */}
      <section className="section-padding" data-testid="expertise-phase2-mdph">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-2 mb-3">
            <UserCheck className="w-5 h-5 text-accent" />
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Volet MDPH</span>
          </div>
          <h2 className="text-3xl font-semibold mb-3" data-testid="expertise-phase2-mdph-h2">
            Évaluation MDPH&nbsp;: comment se construit réellement la décision
          </h2>
          <p className="text-muted-foreground mb-8 text-lg">
            L'équipe pluridisciplinaire d'évaluation, le certificat médical, le projet de vie et les voies de recours&nbsp;: comprendre ce qui se joue sur pièces.
          </p>

          <div className="space-y-6 text-foreground/90 leading-relaxed">
            <div>
              <h3 className="text-xl font-semibold mb-2">Une évaluation principalement effectuée sur pièces</h3>
              <p>
                À la différence d'un médecin conseil de la CPAM ou d'un médecin expert d'assurance, la MDPH ne convoque que très rarement le demandeur pour une expertise médicale en présentiel. L'évaluation est généralement réalisée sur pièces par l'équipe pluridisciplinaire d'évaluation (EPE), composée notamment d'un médecin, d'un travailleur social et, selon les cas, d'un ergothérapeute ou d'un psychologue.
              </p>
              <p className="mt-2">
                Cette particularité a une conséquence stratégique majeure&nbsp;: le dossier déposé est, pour l'essentiel, la seule pièce sur laquelle l'EPE fonde son appréciation.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-2">Les trois documents structurants</h3>
              <ul className="list-disc pl-6 space-y-3">
                <li>
                  <strong>Le certificat médical Cerfa n°15695*01.</strong> Rédigé par le médecin traitant ou un spécialiste. Les sections fréquemment sous-développées concernent les répercussions fonctionnelles dans la vie quotidienne, la nature du retentissement (cognitif, psychique, physique) et les limitations professionnelles.
                </li>
                <li>
                  <strong>Le projet de vie.</strong> Espace dédié à la description subjective du quotidien, des difficultés rencontrées et des besoins. Un projet de vie structuré et précis peut modifier sensiblement l'évaluation faite par l'EPE.
                </li>
                <li>
                  <strong>Les pièces complémentaires.</strong> Comptes-rendus de spécialistes, bilans neuropsychologiques, bilans ergothérapiques, fiches de poste, certificats d'arrêts maladie, attestations d'aidants. Une documentation complète apporte une matière objective utile à l'évaluation.
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-2">Les cas où une véritable expertise intervient</h3>
              <p>
                Une expertise médicale ou judiciaire peut intervenir dans trois configurations principales&nbsp;:
              </p>
              <ul className="list-disc pl-6 space-y-2 mt-2">
                <li><strong>Allocation d'éducation de l'enfant handicapé (AEEH)</strong>, en particulier complément 5 ou 6&nbsp;: une visite à domicile par un évaluateur MDPH peut être réalisée.</li>
                <li><strong>Recours après refus, devant le tribunal judiciaire (pôle social)</strong>&nbsp;: une expertise médicale judiciaire peut être ordonnée par le juge.</li>
                <li><strong>Renouvellement d'AAH avec changement de situation</strong>&nbsp;: l'appel à un ergothérapeute ou à un médecin du travail peut, selon les cas, être envisagé.</li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-2">La voie du recours après refus</h3>
              <p>
                En cas de refus de l'AAH (première demande ou renouvellement), le demandeur dispose d'un délai de <strong>deux mois</strong> pour déposer un recours administratif préalable obligatoire (RAPO). Ce recours gagne à reposer sur des éléments nouveaux&nbsp;: certificats médicaux actualisés et détaillés, projet de vie réécrit avec une description précise de la restriction substantielle et durable d'accès à l'emploi (RSDAE), pièces complémentaires (bilans neuropsychologiques, ergothérapiques).
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-2">Vers une expertise médicale judiciaire</h3>
              <p>
                Si le RAPO est rejeté, le tribunal judiciaire pôle social peut être saisi. Le juge ordonne fréquemment une expertise médicale judiciaire confiée à un médecin inscrit sur la liste de la cour d'appel. C'est à ce stade qu'intervient, au sens strict, une expertise médicale dans le cadre d'un litige MDPH&nbsp;: la décision de la MDPH est alors réexaminée à la lumière d'un avis médical indépendant.
              </p>
            </div>
          </div>

          <p className="mt-8 text-xs text-muted-foreground italic">
            Cadre légal mobilisé&nbsp;: Code de l'action sociale et des familles, articles L.146-3 et suivants&nbsp;; Code de la sécurité sociale (procédures juridictionnelles pôle social)&nbsp;; Code de déontologie médicale.
          </p>
        </div>
      </section>
    </>
  );
};
