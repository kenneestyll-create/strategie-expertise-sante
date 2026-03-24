import { Link } from 'react-router-dom';
import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import {
  ArrowRight,
  Stethoscope,
  AlertTriangle,
  Shield,
  Target,
  Users,
  CheckCircle,
  CircleDollarSign,
  FileSearch,
  Phone
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const trackClick = (action) => {
  axios.post(`${API}/tracking/event`, {
    page: 'medecin-conseil',
    action,
    timestamp: new Date().toISOString()
  }).catch(() => {});
};

export default function MedecinConseilPage() {
  useEffect(() => {
    trackClick('page-view');
  }, []);
  const enjeux = [
    { icon: Target, title: "Taux d'IPP", desc: "Un médecin conseil adapté peut faire la différence entre un taux sous-évalué et une juste reconnaissance de vos séquelles." },
    { icon: CircleDollarSign, title: "Indemnisation globale", desc: "L'évaluation de l'incidence professionnelle, de la PGPF et des préjudices extra-patrimoniaux dépend directement de la qualité de l'expertise." },
    { icon: Shield, title: "Stratégie juridique", desc: "Le médecin conseil travaille en coordination avec votre avocat. Un choix cohérent renforce l'ensemble de votre défense." },
  ];

  const erreurs = [
    "Choisir un médecin conseil uniquement sur la base d'une recommandation générique",
    "Confondre médecin traitant et médecin conseil de victime",
    "Ne pas vérifier la spécialité médicale par rapport à votre pathologie",
    "Négliger l'expérience du médecin en matière de dommage corporel",
    "Attendre le dernier moment pour constituer le dossier médical",
  ];

  const approche = [
    { step: "01", title: "Analyse de votre situation", desc: "Nous étudions votre pathologie, votre contexte professionnel et les enjeux financiers pour comprendre précisément vos besoins." },
    { step: "02", title: "Orientation personnalisée", desc: "Nous vous orientons vers le médecin conseil dont la spécialité et l'expérience correspondent le mieux à votre dossier." },
    { step: "03", title: "Préparation du dossier", desc: "Nous vous aidons à constituer un dossier médical complet et structuré pour optimiser le déroulement de l'expertise." },
    { step: "04", title: "Suivi post-expertise", desc: "Nous analysons les conclusions du rapport et vous conseillons sur les suites à donner : acceptation, contestation ou complément." },
  ];

  return (
    <main className="page-transition pt-20">
      <SEO
        title="Choisir le bon médecin conseil | Stratégie & Expertise Santé"
        description="Le choix du médecin conseil est déterminant pour votre indemnisation. Expertise en dommage corporel, accident du travail, maladie professionnelle. Orientation personnalisée."
        path="/medecin-conseil"
      />

      {/* ── HERO ── */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Expertise stratégique</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="medecin-conseil-title">
              Choisir le bon médecin conseil : un enjeu déterminant pour votre indemnisation
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Dans toute procédure d'indemnisation du dommage corporel, le choix du médecin conseil
              de victime est une décision stratégique majeure. Ce choix influence directement
              l'évaluation de vos séquelles, votre taux d'incapacité et, in fine,
              le montant de votre indemnisation.
            </p>
            <p className="text-base text-muted-foreground mt-4 leading-relaxed">
              Un accompagnement éclairé en amont de cette étape peut faire une différence
              considérable sur l'issue de votre dossier.
            </p>
            <div className="mt-8">
              <Button asChild size="lg" className="gap-2 bg-accent text-accent-foreground hover:bg-accent/90 rounded-full px-8" data-testid="medecin-conseil-hero-cta" onClick={() => trackClick('hero-cta-click')}>
                <Link to="/contact">
                  <Phone className="w-4 h-4" />
                  Être accompagné dans le choix de mon médecin conseil
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* ── ENJEUX ── */}
      <section className="section-padding" data-testid="medecin-conseil-enjeux">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-semibold mb-3">Pourquoi ce choix est-il si déterminant ?</h2>
          <p className="text-muted-foreground mb-10 max-w-2xl">
            Le médecin conseil de victime n'est pas un simple médecin. C'est un expert
            en évaluation du dommage corporel dont la mission est de défendre
            vos intérêts face au médecin de la partie adverse.
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            {enjeux.map((e, i) => (
              <Card key={i} className="border-border/50 hover:border-accent/30 transition-colors">
                <CardContent className="pt-6">
                  <e.icon className="w-8 h-8 text-accent mb-4" />
                  <h3 className="font-semibold text-lg mb-2">{e.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{e.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ── PROBLÉMATIQUE ── */}
      <section className="section-padding bg-secondary" data-testid="medecin-conseil-problematique">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            <div>
              <h2 className="text-2xl sm:text-3xl font-semibold mb-4">
                Un choix complexe qui ne s'improvise pas
              </h2>
              <p className="text-muted-foreground leading-relaxed mb-4">
                Il existe de nombreux médecins conseils en France, avec des spécialités,
                des méthodes et des niveaux d'expérience très variables. Tous ne sont pas
                adaptés à chaque situation.
              </p>
              <p className="text-muted-foreground leading-relaxed mb-4">
                Chaque dossier est unique : la pathologie en cause, le contexte professionnel,
                la stratégie juridique adoptée et les enjeux financiers nécessitent une
                orientation sur mesure.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Un médecin conseil spécialisé en orthopédie ne sera pas le plus pertinent
                pour un dossier de maladie professionnelle liée à l'amiante. De même,
                un expert généraliste ne pourra pas défendre avec la même précision
                qu'un spécialiste de votre pathologie.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                Les erreurs les plus fréquentes
              </h3>
              <div className="space-y-3">
                {erreurs.map((e, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-background/60 border border-border/40">
                    <span className="text-amber-500 font-bold text-sm mt-0.5">{i + 1}.</span>
                    <p className="text-sm text-muted-foreground">{e}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── POSITIONNEMENT EXPERT ── */}
      <section className="section-padding" data-testid="medecin-conseil-positionnement">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <Stethoscope className="w-10 h-10 text-accent mx-auto mb-4" />
            <h2 className="text-2xl sm:text-3xl font-semibold mb-4">
              Notre positionnement
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Nous ne sommes ni un annuaire, ni une plateforme de mise en relation.
              Nous sommes un service d'accompagnement expert qui place la stratégie
              au cœur de chaque décision.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <Card className="border-accent/20 bg-accent/5">
              <CardContent className="pt-6">
                <Shield className="w-7 h-7 text-accent mb-3" />
                <h3 className="font-semibold mb-3">Nous ne diffusons pas de liste publique de médecins conseils</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  La publication d'une liste générique serait contraire à notre approche.
                  Chaque victime mérite une orientation personnalisée, fondée sur
                  l'analyse approfondie de son dossier et de ses enjeux spécifiques.
                </p>
              </CardContent>
            </Card>
            <Card className="border-accent/20 bg-accent/5">
              <CardContent className="pt-6">
                <Users className="w-7 h-7 text-accent mb-3" />
                <h3 className="font-semibold mb-3">Notre expertise : vous orienter vers le professionnel le plus adapté</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Grâce à notre connaissance approfondie du réseau de médecins conseils
                  de victimes et des spécificités de chaque pathologie, nous identifions
                  pour vous le professionnel dont le profil correspond précisément
                  à votre situation.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* ── COÛT ── */}
      <section className="section-padding bg-secondary" data-testid="medecin-conseil-cout">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl mx-auto">
            <CircleDollarSign className="w-10 h-10 text-accent mb-4" />
            <h2 className="text-2xl sm:text-3xl font-semibold mb-6">
              Le coût d'un médecin conseil : un investissement, pas une dépense
            </h2>
            <div className="space-y-4 text-muted-foreground leading-relaxed">
              <p>
                Le recours à un médecin conseil de victime représente un investissement
                financier significatif, souvent compris entre <strong className="text-foreground">800 et 3 000 euros</strong> selon
                la complexité du dossier et la spécialité requise.
              </p>
              <p>
                Ce montant peut sembler élevé. Pourtant, il est à mettre en perspective
                avec les enjeux d'indemnisation qui se chiffrent fréquemment en dizaines,
                voire en centaines de milliers d'euros.
              </p>
              <Card className="border-accent/20">
                <CardContent className="py-5">
                  <p className="text-base text-foreground font-medium leading-relaxed italic">
                    "Une expertise médicale représente un investissement significatif.
                    Un mauvais choix peut compromettre durablement votre indemnisation.
                    Être accompagné en amont permet d'éviter des erreurs aux conséquences
                    financières majeures."
                  </p>
                </CardContent>
              </Card>
              <p>
                Un taux d'IPP sous-évalué de quelques points, une incidence professionnelle
                mal argumentée ou une PGPF insuffisamment documentée peuvent représenter
                une perte de plusieurs dizaines de milliers d'euros sur votre indemnisation finale.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── NOTRE APPROCHE ── */}
      <section className="section-padding" data-testid="medecin-conseil-approche">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-semibold mb-3">Notre approche en 4 étapes</h2>
          <p className="text-muted-foreground mb-10 max-w-2xl">
            Un accompagnement structuré pour vous guider à chaque étape,
            de l'analyse initiale au suivi post-expertise.
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {approche.map((a, i) => (
              <div key={i} className="relative">
                <span className="text-5xl font-bold text-accent/10 absolute -top-2 -left-1">{a.step}</span>
                <div className="pt-8">
                  <h3 className="font-semibold mb-2">{a.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{a.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="section-padding bg-accent/5 border-y border-accent/10" data-testid="medecin-conseil-cta">
        <div className="max-w-7xl mx-auto text-center">
          <FileSearch className="w-10 h-10 text-accent mx-auto mb-4" />
          <h2 className="text-2xl sm:text-3xl font-semibold mb-4">
            Avant toute démarche, faites analyser votre situation
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto mb-8 leading-relaxed">
            Il est fortement recommandé de bénéficier d'une analyse personnalisée
            de votre situation avant de vous engager dans le choix d'un médecin conseil.
            Cette étape préalable peut faire toute la différence.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="gap-2 bg-accent text-accent-foreground hover:bg-accent/90" data-testid="medecin-conseil-cta-accompagnement" onClick={() => trackClick('cta-accompagnement-click')}>
              <Link to="/contact">
                <Phone className="w-4 h-4" />
                Être accompagné dans le choix de mon médecin conseil
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="gap-2" data-testid="medecin-conseil-cta-analyse" onClick={() => trackClick('cta-analyse-click')}>
              <Link to="/simulateur">
                Obtenir ma pré-analyse gratuite <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* ── MENTIONS ── */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-start gap-3 p-4 rounded-lg border border-border/50 bg-muted/30">
              <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
              <p className="text-xs text-muted-foreground leading-relaxed">
                <strong>Note importante :</strong> les informations présentées sur cette page
                ont un caractère général et informatif. Chaque situation étant unique,
                seule une analyse personnalisée de votre dossier permet de formuler
                des recommandations adaptées. N'hésitez pas à nous consulter
                pour un accompagnement sur mesure.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
