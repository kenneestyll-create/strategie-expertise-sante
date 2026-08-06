import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { DossierExpressCTA } from '@/components/DossierExpressCTA';
import { TerrainNote } from '@/components/TerrainNote';
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
  Phone,
  ChevronDown
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const trackClick = (action) => {
  axios.post(`${API}/tracking/event`, {
    page: 'médecin-conseil',
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
    { step: "04", title: "Suivi post-expertise", desc: "Nous analysons les conclusions du rapport et vous conseillons sur les suites à donner : acceptation, contestation ou complément." },
  ];

  return (
    <main className="page-transition pt-20">
      <SEO
        title="Médecin conseil CPAM : rôle, convocation, avis et recours"
        description="Médecin conseil de la CPAM : son rôle, la convocation à l'examen, la portée de son avis et comment contester une décision défavorable. Conseils pour vous préparer et défendre votre indemnisation."
        path="/medecin-conseil"
      />

      {/* ── HERO ── */}
      <section className="px-4 sm:px-6 lg:px-8 py-10 sm:py-12 lg:py-14 bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Expertise stratégique</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="médecin-conseil-title">
              Médecin conseil CPAM ou médecin conseil de victime : comprendre les rôles, défendre votre indemnisation
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
              <Button asChild size="lg" className="gap-2 bg-accent text-accent-foreground hover:bg-accent/90 rounded-full px-6 sm:px-8 text-sm sm:text-base" data-testid="médecin-conseil-hero-cta" onClick={() => trackClick('hero-cta-click')}>
                <Link to="/contact">
                  <Phone className="w-4 h-4 flex-shrink-0" />
                  <span className="sm:hidden">Être accompagné</span>
                  <span className="hidden sm:inline">Être accompagné dans le choix de mon médecin conseil</span>
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* ── MÉDECIN CONSEIL CPAM — bloc informationnel (Phase 1 SEO, ajout additif) ── */}
      <section className="section-padding" data-testid="médecin-conseil-cpam-info">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl mb-8">
            <h2 className="text-2xl sm:text-3xl font-semibold mb-3">Médecin conseil CPAM : rôle, convocation, avis et recours</h2>
            <p className="text-muted-foreground leading-relaxed">
              Avant de parler du médecin conseil de victime, il faut comprendre celui que vous ne choisissez pas :
              le médecin conseil de la CPAM. C'est lui qui rend les avis qui conditionnent vos indemnités journalières,
              votre consolidation et votre taux d'IPP.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="p-5 rounded-xl border border-border bg-card" data-testid="mc-cpam-role">
              <h3 className="font-semibold text-sm mb-2">Son rôle</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Le médecin conseil du service médical de la CPAM contrôle la justification médicale de vos arrêts,
                fixe la date de consolidation et évalue vos séquelles. Son avis s'impose à la caisse : c'est lui qui
                détermine en pratique votre taux d'incapacité permanente et donc le montant de votre rente.
              </p>
            </div>
            <div className="p-5 rounded-xl border border-border bg-card" data-testid="mc-cpam-convocation">
              <h3 className="font-semibold text-sm mb-2">La convocation</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                La convocation à l'examen est obligatoire : ne pas s'y rendre peut suspendre vos indemnités.
                Préparez ce rendez-vous comme une expertise : dossier médical complet, liste des séquelles et de leurs
                répercussions concrètes, comptes rendus récents. L'examen dure souvent moins de 20 minutes — chaque élément compte.
              </p>
            </div>
            <div className="p-5 rounded-xl border border-border bg-card" data-testid="mc-cpam-avis">
              <h3 className="font-semibold text-sm mb-2">La portée de son avis</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Consolidation, taux d'IPP, aptitude : ces décisions ont des conséquences financières majeures.
                Un écart de quelques points d'IPP peut représenter des milliers d'euros.{' '}
                <Link to="/calculatrice-ipp" className="text-accent hover:underline font-medium">Estimez l'enjeu avec le simulateur rente IPP</Link>.
              </p>
            </div>
            <div className="p-5 rounded-xl border border-border bg-card" data-testid="mc-cpam-recours">
              <h3 className="font-semibold text-sm mb-2">Contester une décision</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                L'avis du médecin conseil se conteste : expertise médicale technique (CMRA) puis, si nécessaire,{' '}
                <Link to="/guide/recours-tribunal-judiciaire-pole-social" className="text-accent hover:underline font-medium">recours devant le pôle social du tribunal judiciaire</Link>.
                En cas de conclusions défavorables, consultez notre guide{' '}
                <Link to="/guide/expertise-medicale-defavorable-recours" className="text-accent hover:underline font-medium">expertise médicale défavorable : les recours</Link>.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── ENJEUX ── */}
      <section className="section-padding" data-testid="médecin-conseil-enjeux">
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
      <section className="section-padding bg-secondary" data-testid="médecin-conseil-problematique">
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
      <section className="section-padding" data-testid="médecin-conseil-positionnement">
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
      <section className="section-padding bg-secondary" data-testid="médecin-conseil-cout">
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
      <section className="section-padding" data-testid="médecin-conseil-approche">
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

      {/* ENRICHMENT — Clarification & cas terrain */}
      <section className="section-padding bg-secondary/30">
        <div className="max-w-4xl mx-auto space-y-10">

          {/* L'essentiel */}
          <div className="p-5 rounded-xl bg-[#1a1a2e]/[0.03] border border-[#C9A84C]/20" data-testid="médecin-conseil-essentiel">
            <h2 className="font-semibold text-base mb-3 text-foreground">L'essentiel à retenir</h2>
            <ul className="space-y-1.5 list-none pl-0 text-sm text-muted-foreground">
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Il existe <strong className="text-foreground">3 types de médecins conseils</strong> : CPAM (sécurité sociale), assureur privé, et médecin de recours (médecin conseil de victime)</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Le médecin conseil <strong className="text-foreground">n'est jamais votre médecin</strong> — son rôle est d'évaluer votre dossier au regard d'une mission précise</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>CPAM : convocation fréquente après <strong className="text-foreground">6 ou 12 mois d'arrêt</strong>, ou pour invalidité, ALD, AT/MP</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Tout avis défavorable du médecin conseil CPAM est contestable dans les <strong className="text-foreground">2 mois</strong> (CRA pour décisions administratives, CMRA pour décisions médicales)</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Manquer une convocation expose à une <strong className="text-foreground">suspension immédiate des indemnités journalières</strong> — sauf motif légitime documenté</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Pour une indemnisation, le choix du <strong className="text-foreground">médecin de recours</strong> peut représenter plusieurs dizaines de milliers d'euros sur le résultat final</span></li>
            </ul>
            <p className="text-xs text-muted-foreground mt-3 italic">Code de la Sécurité sociale, articles L. 142-1 et suivants — procédures CPAM en vigueur en 2026.</p>
          </div>

          {/* 3 types de médecins conseils */}
          <div>
            <h2 className="text-lg font-semibold mb-3">Trois médecins conseils, trois stratégies différentes</h2>
            <p className="text-sm text-muted-foreground leading-relaxed mb-4">
              La confusion entre ces trois rôles produit la majorité des erreurs stratégiques. Chacun défend des intérêts différents — comprendre lequel vous avez en face change radicalement votre préparation.
            </p>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div className="p-4 rounded-xl bg-background border border-border">
                <h3 className="font-medium text-foreground mb-2">Médecin conseil CPAM</h3>
                <p className="text-muted-foreground text-xs leading-relaxed">Mandaté par la Sécurité sociale. Évalue la justification médicale d'un arrêt, d'une demande d'invalidité, d'une reconnaissance d'AT/MP. Peut prescrire la reprise du travail. <strong className="text-foreground">Décisions contestables</strong> via CRA / CMRA.</p>
              </div>
              <div className="p-4 rounded-xl bg-background border border-border">
                <h3 className="font-medium text-foreground mb-2">Médecin de l'assureur</h3>
                <p className="text-muted-foreground text-xs leading-relaxed">Mandaté par votre assureur ou celui du tiers responsable. Évalue les séquelles pour fixer l'indemnisation. <strong className="text-foreground">N'est pas neutre</strong> : sa mission est de chiffrer le préjudice du point de vue de l'assureur qui le rémunère.</p>
              </div>
              <div className="p-4 rounded-xl bg-accent/5 border border-accent/30">
                <h3 className="font-medium text-foreground mb-2">Médecin de recours (médecin conseil de victime)</h3>
                <p className="text-muted-foreground text-xs leading-relaxed">Choisi et rémunéré par vous. Indépendant des assureurs. Diplômé en réparation du dommage corporel. <strong className="text-foreground">Défend vos intérêts</strong> face au médecin de l'assureur ou de l'expert judiciaire.</p>
              </div>
            </div>
          </div>

          {/* Convocation CPAM */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Convocation par le médecin conseil CPAM : ce qui se joue</h2>
            <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
              <p>
                Au-delà de 6 mois d'arrêt continu, la convocation par le médecin conseil devient quasi systématique. Son objet n'est pas de douter de vous, mais de <strong className="text-foreground">vérifier la justification médicale du maintien des indemnités journalières</strong>, d'orienter vers une éventuelle invalidité ou inaptitude, ou de fixer une consolidation pour un AT/MP. La convocation est obligatoire : ne pas s'y rendre suspend les IJ jusqu'à régularisation.
              </p>
              <p>
                Préparation : apportez l'ensemble de vos certificats récents, les comptes rendus d'examens, les ordonnances en cours, et un courrier de votre médecin traitant détaillant les limitations actuelles. Vous pouvez être accompagné d'un proche pour le soutien moral, mais l'examen lui-même reste individuel.
              </p>
              <p>
                À l'issue du rendez-vous, trois décisions principales sont possibles : prolongation des IJ, mise en invalidité (catégorie 1, 2 ou 3), ou avis favorable à la reprise. Tout avis défavorable doit vous être notifié par écrit par la CPAM avec mention des voies de recours.
              </p>
            </div>
          </div>

          {/* Cas concret CPAM */}
          <div className="p-4 rounded-xl bg-accent/5 border border-accent/20" data-testid="médecin-conseil-cas-concret">
            <h3 className="font-medium text-sm text-foreground mb-2">Cas concret — Reprise imposée malgré l'avis du médecin traitant</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Une assistante administrative en arrêt depuis 9 mois pour syndrome dépressif est convoquée par le médecin conseil CPAM. Son médecin traitant et son psychiatre maintiennent une incapacité totale. Le médecin conseil estime qu'une reprise à temps partiel thérapeutique est possible et émet un avis favorable à la reprise. Notifiée le 15 du mois, la CPAM coupe les IJ au 1er du mois suivant.
              La salariée saisit la <strong className="text-foreground">Commission Médicale de Recours Amiable (CMRA)</strong> dans les 2 mois en joignant les certificats détaillés de ses médecins, un courrier confraternel motivé, et un complément médical d'un psychiatre tiers. Quatre mois plus tard, la CMRA infirme l'avis du médecin conseil et rétablit les IJ avec rappel rétroactif. <strong className="text-foreground">Sans recours dans les délais</strong>, la décision serait devenue définitive et les IJ perdues. Cette procédure est gratuite.
            </p>
          </div>

          {/* Erreurs */}
          <div>
            <h3 className="font-medium text-sm text-foreground mb-3">Erreurs les plus coûteuses face au médecin conseil</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Confondre médecin conseil CPAM et médecin de l'assureur</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Les enjeux, les délais et les recours sont totalement différents. Une stratégie efficace face au médecin CPAM est inadaptée face à un médecin d'assureur, et inversement.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Manquer un rendez-vous sans justificatif</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ La CPAM suspend immédiatement les IJ. Un report est possible mais doit être demandé en amont, par écrit, avec un motif sérieux (hospitalisation, déplacement programmé, certificat médical).</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Ne pas contester un avis défavorable dans les 2 mois</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Passé ce délai, la décision devient définitive. La CMRA est gratuite, accessible, et donne fréquemment raison aux assurés lorsque le dossier est solidement complété d'éléments médicaux nouveaux.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Confondre invalidité (CPAM) et inaptitude (médecine du travail)</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ L'invalidité est prononcée par le médecin conseil CPAM et ouvre droit à pension. L'inaptitude est prononcée par le médecin du travail et concerne le poste. Les deux sont indépendants et peuvent se cumuler. Méconnaître cette différence prive de droits cumulables.</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* Encart conversion */}
      <DossierExpressCTA
        testId="médecin-conseil-cta-dossier"
        title={"Convocation reçue ou avis défavorable\u00A0?"}
        text="Une convocation par le médecin conseil CPAM ou un avis défavorable se prépare et se conteste sur dossier médical solide. Le Dossier Express IA identifie les éléments manquants, structure votre argumentation et le calendrier exact de vos recours (CRA, CMRA, Tribunal)."
        ctaLabel="Préparer mon dossier"
      />

      {/* FAQ */}
      <MedecinConseilFaq />

      <TerrainNote
        testId="médecin-conseil-terrain-note"
        text="Ce guide est construit à partir des convocations et avis défavorables que je décortique avec les assurés : CPAM, CMRA, CRA, saisines du Pôle social."
      />

      {/* ── CTA ── */}
      <section className="section-padding bg-accent/5 border-y border-accent/10" data-testid="médecin-conseil-cta">
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
            <Button asChild size="lg" className="gap-2 bg-accent text-accent-foreground hover:bg-accent/90 text-sm sm:text-base" data-testid="médecin-conseil-cta-accompagnement" onClick={() => trackClick('cta-accompagnement-click')}>
              <Link to="/contact">
                <Phone className="w-4 h-4 flex-shrink-0" />
                <span className="sm:hidden">Être accompagné</span>
                <span className="hidden sm:inline">Être accompagné dans le choix de mon médecin conseil</span>
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="gap-2" data-testid="médecin-conseil-cta-analyse" onClick={() => trackClick('cta-analyse-click')}>
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

const medecinConseilFaqData = [
  {
    question: "Pourquoi je suis convoqué par le médecin conseil CPAM après 6 mois d'arrêt ?",
    answer: "La convocation est une procédure standard, pas une suspicion. Elle vise à vérifier que la justification médicale de l'arrêt est toujours réunie, à orienter éventuellement vers une mise en invalidité, ou à fixer une consolidation pour un AT/MP. Préparez votre dossier avec tous vos certificats récents, comptes rendus d'examens et un courrier confraternel de votre médecin traitant détaillant les limitations actuelles."
  },
  {
    question: "Que se passe-t-il si je ne peux pas me rendre au rendez-vous ?",
    answer: "Le rendez-vous avec le médecin conseil est obligatoire. Une absence non justifiée entraîne la suspension immédiate des indemnités journalières. Si vous êtes dans l'impossibilité de vous y rendre (hospitalisation, déplacement programmé, état de santé incompatible), demandez un report en amont par écrit avec justificatif. Le report est presque toujours accordé pour motif sérieux."
  },
  {
    question: "Le médecin conseil peut-il imposer ma reprise du travail malgré l'avis de mon médecin traitant ?",
    answer: "Oui, le médecin conseil CPAM peut émettre un avis favorable à la reprise même contre l'avis du médecin traitant. Mais cet avis n'est pas définitif : vous disposez de 2 mois pour saisir la Commission Médicale de Recours Amiable (CMRA), procédure gratuite. Joignez à votre recours les certificats détaillés de votre médecin traitant, un complément médical d'un spécialiste tiers, et tout élément médical nouveau. La CMRA infirme régulièrement l'avis du médecin conseil lorsque le dossier est solide."
  },
  {
    question: "Quelle différence entre la Commission de Recours Amiable (CRA) et la Commission Médicale de Recours Amiable (CMRA) ?",
    answer: "La CRA traite les décisions administratives de la CPAM (refus d'indemnités, calcul du salaire de référence, refus de reconnaissance AT/MP sur le plan administratif). La CMRA traite uniquement les contestations d'ordre médical (taux d'IPP, date de consolidation, avis sur la justification de l'arrêt). Les deux ont un délai de saisine de 2 mois, sont gratuites, et précèdent toute saisine du Pôle social du Tribunal Judiciaire."
  },
  {
    question: "Quelle différence entre invalidité (CPAM) et inaptitude (médecine du travail) ?",
    answer: "L'invalidité est prononcée par le médecin conseil CPAM lorsque votre capacité de travail ou de gain est réduite d'au moins 2/3. Elle ouvre droit à une pension d'invalidité (catégorie 1, 2 ou 3 selon la gravité). L'inaptitude est prononcée par le médecin du travail et concerne uniquement votre poste actuel : elle peut conduire à un licenciement pour inaptitude. Les deux sont indépendantes et peuvent se cumuler — une personne en invalidité peut être déclarée apte à un autre poste, et inversement."
  },
  {
    question: "Puis-je être accompagné lors d'un rendez-vous avec le médecin conseil ?",
    answer: "Vous pouvez être accompagné par un proche dans la salle d'attente et pour le soutien moral. L'examen lui-même se déroule en principe en tête-à-tête avec le médecin conseil. Pour les recours médicaux (CMRA notamment), vous pouvez vous faire assister par un médecin de votre choix qui pourra présenter votre dossier."
  },
  {
    question: "Combien coûte un médecin de recours pour une indemnisation d'assurance et qui paie ?",
    answer: "Les honoraires d'un médecin de recours (médecin conseil de victime, distinct du médecin conseil CPAM) varient entre 800 et 3 000 € selon la complexité du dossier. Cette dépense est fréquemment prise en charge par votre assurance protection juridique. Selon la nomenclature Dintilhac, ces honoraires peuvent également être inclus dans les frais divers indemnisables au titre du préjudice corporel — ils sont alors récupérés sur l'indemnisation finale obtenue auprès de l'assureur du tiers responsable."
  }
];

const MedecinConseilFaq = () => {
  const [openIndex, setOpenIndex] = useState(null);

  useEffect(() => {
    document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
      try { if (JSON.parse(s.textContent)['@type'] === 'FAQPage') s.remove(); } catch {}
    });
    const script = document.createElement('script');
    script.id = 'médecin-conseil-faq-schema';
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": medecinConseilFaqData.map(f => ({
        "@type": "Question",
        "name": f.question,
        "acceptedAnswer": { "@type": "Answer", "text": f.answer }
      }))
    });
    document.head.appendChild(script);
    return () => { const el = document.getElementById('médecin-conseil-faq-schema'); if (el) el.remove(); };
  }, []);

  return (
    <section className="section-padding bg-secondary/20" data-testid="médecin-conseil-faq">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold mb-8 text-center">Questions fréquentes sur le médecin conseil</h2>
        <div className="space-y-2">
          {medecinConseilFaqData.map((faq, i) => (
            <div key={i} className="border border-border rounded-xl overflow-hidden bg-background">
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
                data-testid={`médecin-conseil-faq-${i}`}
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
