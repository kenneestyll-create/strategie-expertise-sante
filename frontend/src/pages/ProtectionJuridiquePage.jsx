import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { DossierExpressCTA } from '@/components/DossierExpressCTA';
import { TerrainNote } from '@/components/TerrainNote';
import { 
  ArrowRight, 
  Shield, 
  FileText, 
  Scale, 
  Users,
  CheckCircle,
  AlertCircle,
  BookOpen,
  Search,
  Phone,
  Briefcase,
  HelpCircle,
  ChevronDown
} from 'lucide-react';

export const ProtectionJuridiquePage = () => {
  const etapesActivation = [
    {
      step: "1",
      title: "Identifiez vos contrats",
      description: "La protection juridique peut être incluse dans votre assurance habitation, auto, santé ou dans un contrat dédié. Vérifiez l'ensemble de vos contrats."
    },
    {
      step: "2",
      title: "Consultez les garanties",
      description: "Lisez les conditions générales pour comprendre les domaines couverts, les plafonds de prise en charge et les exclusions éventuelles."
    },
    {
      step: "3",
      title: "Déclarez votre litige",
      description: "Contactez votre assureur par écrit (courrier recommandé ou espace client) en exposant clairement votre situation et le litige concerné."
    },
    {
      step: "4",
      title: "Constituez votre dossier",
      description: "Rassemblez tous les documents utiles : contrats, courriers, certificats médicaux, décisions administratives..."
    },
    {
      step: "5",
      title: "Suivez votre dossier",
      description: "Restez en contact avec votre assureur et l'avocat désigné. N'hésitez pas à demander des comptes rendus réguliers."
    }
  ];

  const droits = [
    {
      icon: AlertCircle,
      title: "Droit à l'information",
      description: "Vous avez le droit d'être informé de vos droits, des procédures en cours et des décisions vous concernant."
    },
    {
      icon: FileText,
      title: "Droit à la contestation",
      description: "Vous pouvez contester toute décision administrative ou médicale que vous estimez injuste ou erronée."
    },
    {
      icon: Users,
      title: "Droit à l'accompagnement",
      description: "Vous pouvez vous faire accompagner lors des expertises et dans vos démarches administratives."
    },
    {
      icon: Scale,
      title: "Droit à la réparation",
      description: "En cas de préjudice reconnu, vous avez droit à une indemnisation juste et complète."
    }
  ];

  return (
    <main className="page-transition pt-20">
      <SEO title="Protection juridique : l'outil méconnu qui change tout en cas de litige" description="Pourquoi la protection juridique est capitale avant un litige : délai de carence, antériorité du sinistre, contrats qui la contiennent déjà. Le guide stratégique." path="/protection-juridique" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="text-sm font-medium text-accent uppercase tracking-wider">Guide & Accompagnement</span>
              <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="protection-juridique-title">
                Protection juridique : vos droits et comment les faire valoir
              </h1>
              <p className="text-lg text-muted-foreground mb-6">
                La protection juridique est un mécanisme souvent méconnu qui peut pourtant vous aider 
                à faire valoir vos droits en cas de litige. Découvrez comment l'activer et comment 
                je peux vous accompagner.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/contact">
                  <Button size="lg" className="rounded-full px-8 gap-2">
                    Être accompagné
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </Link>
                <a href="#activation">
                  <Button variant="outline" size="lg" className="rounded-full px-8">
                    Guide d'activation
                  </Button>
                </a>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/5668858/pexels-photo-5668858.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Protection juridique"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 1 - Qu'est-ce que la protection juridique */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <HelpCircle className="w-12 h-12 text-accent mb-4" strokeWidth={1.5} />
              <h2 className="text-3xl font-semibold mb-6">
                Qu'est-ce que la protection juridique ?
              </h2>
              <p className="text-muted-foreground mb-6">
                La protection juridique est une garantie d'assurance qui vous permet de bénéficier 
                d'une assistance juridique en cas de litige. Elle peut couvrir :
              </p>
              <ul className="space-y-3 mb-6">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Les frais d'avocat et de procédure</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Les honoraires d'experts</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>L'information et le conseil juridique</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>La négociation amiable avec la partie adverse</span>
                </li>
              </ul>
              <Card className="bg-muted/30 border-border">
                <CardContent className="p-4">
                  <p className="text-sm text-muted-foreground">
                    <strong>Bon à savoir :</strong> Vous avez peut-être déjà une protection juridique 
                    sans le savoir. Elle est souvent incluse dans vos contrats d'assurance habitation, 
                    automobile ou santé complémentaire.
                  </p>
                </CardContent>
              </Card>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Card className="border-border">
                <CardContent className="p-6 text-center">
                  <Shield className="w-10 h-10 text-accent mx-auto mb-3" strokeWidth={1.5} />
                  <h4 className="font-semibold mb-1">Litiges du travail</h4>
                  <p className="text-sm text-muted-foreground">Conflits avec l'employeur, licenciement</p>
                </CardContent>
              </Card>
              <Card className="border-border">
                <CardContent className="p-6 text-center">
                  <Scale className="w-10 h-10 text-accent mx-auto mb-3" strokeWidth={1.5} />
                  <h4 className="font-semibold mb-1">Litiges assurance</h4>
                  <p className="text-sm text-muted-foreground">Refus d'indemnisation, contestation</p>
                </CardContent>
              </Card>
              <Card className="border-border">
                <CardContent className="p-6 text-center">
                  <FileText className="w-10 h-10 text-accent mx-auto mb-3" strokeWidth={1.5} />
                  <h4 className="font-semibold mb-1">Litiges administratifs</h4>
                  <p className="text-sm text-muted-foreground">CPAM, MDPH, organismes sociaux</p>
                </CardContent>
              </Card>
              <Card className="border-border">
                <CardContent className="p-6 text-center">
                  <Briefcase className="w-10 h-10 text-accent mx-auto mb-3" strokeWidth={1.5} />
                  <h4 className="font-semibold mb-1">AT / MP</h4>
                  <p className="text-sm text-muted-foreground">Accidents du travail, maladies pro</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Section 2 - Comment activer */}
      <section id="activation" className="section-padding bg-card">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <Search className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="text-3xl font-semibold mb-4">
              Comment activer votre protection juridique ?
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Guide pratique étape par étape pour identifier et déclencher votre protection juridique 
              auprès de votre assurance.
            </p>
          </div>

          <div className="space-y-6">
            {etapesActivation.map((etape, index) => (
              <div 
                key={index}
                className="flex gap-6 bg-background p-6 rounded-xl border border-border"
                data-testid={`etape-activation-${index}`}
              >
                <div className="w-12 h-12 bg-accent text-accent-foreground rounded-full flex items-center justify-center flex-shrink-0 font-bold text-lg">
                  {etape.step}
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2">{etape.title}</h3>
                  <p className="text-muted-foreground">{etape.description}</p>
                </div>
              </div>
            ))}
          </div>

          <Card className="mt-8 bg-accent/10 border-accent/20">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-accent flex-shrink-0 mt-1" strokeWidth={1.5} />
                <div>
                  <h4 className="font-semibold mb-2">Important : le libre choix de l'avocat</h4>
                  <p className="text-sm text-muted-foreground">
                    Vous avez le droit de choisir votre propre avocat, même si votre assurance 
                    vous en propose un. C'est un droit garanti par la loi. N'hésitez pas à faire 
                    appel à un avocat spécialisé dans votre domaine de litige.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Section 3 - Vos droits */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <BookOpen className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="text-3xl font-semibold mb-4">
              Vos droits en cas d'AT/MP et litige
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              En cas d'accident du travail, de maladie professionnelle ou de litige avec 
              un employeur ou une assurance, vous disposez de droits fondamentaux.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {droits.map((droit, index) => (
              <Card key={index} className="card-lift border-border" data-testid={`droit-${index}`}>
                <CardContent className="p-6">
                  <droit.icon className="w-10 h-10 text-accent mb-4" strokeWidth={1.5} />
                  <h3 className="font-semibold text-lg mb-2">{droit.title}</h3>
                  <p className="text-sm text-muted-foreground">{droit.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ENRICHMENT — Antériorité, carence, pièges réels */}
      <section className="section-padding bg-secondary/30">
        <div className="max-w-4xl mx-auto space-y-10">

          {/* L'essentiel */}
          <div className="p-5 rounded-xl bg-[#1a1a2e]/[0.03] border border-[#C9A84C]/20" data-testid="pj-essentiel">
            <h2 className="font-semibold text-base mb-3 text-foreground">L'essentiel à retenir</h2>
            <ul className="space-y-1.5 list-none pl-0 text-sm text-muted-foreground">
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>La protection juridique <strong className="text-foreground">n'est jamais rétroactive</strong> : elle ne couvre que les litiges nés après sa souscription</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Un <strong className="text-foreground">délai de carence</strong> de 2 à 24 mois s'applique sur la plupart des domaines (travail, voisinage, santé)</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Beaucoup de Français en ont une <strong className="text-foreground">sans le savoir</strong> (incluse dans habitation, auto, carte bancaire premium, mutuelle)</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Coût d'un contrat dédié : <strong className="text-foreground">15 à 80 €/an</strong> — à mettre en regard de 3 000 à 15 000 € d'honoraires d'avocat potentiels</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>En cas de refus pour antériorité, <strong className="text-foreground">vérifiez vos anciens contrats</strong> : la PJ de l'ancien contrat peut couvrir si le fait générateur date de sa période d'effet</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Droit fondamental : vous pouvez <strong className="text-foreground">choisir librement votre avocat</strong>, même si l'assureur en propose un</span></li>
            </ul>
            <p className="text-xs text-muted-foreground mt-3 italic">Code des assurances, articles L. 127-1 et suivants — règles applicables en 2026.</p>
          </div>

          {/* L'erreur qui coûte cher */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Pourquoi souscrire après un litige ne sert à rien</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              C'est le piège n°1 de la protection juridique et la raison pour laquelle tant de personnes découvrent son existence <strong className="text-foreground">trop tard</strong>. L'assurance protection juridique fonctionne sur le principe du <strong className="text-foreground">fait générateur</strong> : l'événement à l'origine du litige (accident, refus d'indemnisation, décision CPAM défavorable, licenciement) doit être survenu <strong className="text-foreground">après la date de prise d'effet du contrat</strong> et après le délai de carence applicable. Souscrire une PJ le lendemain d'un accident du travail ou d'un refus MDPH ne vous permettra pas d'obtenir la prise en charge des frais d'avocat pour ce dossier. L'assureur refusera systématiquement, et cette exclusion est parfaitement légale.
            </p>
          </div>

          {/* Délais de carence */}
          <div>
            <h2 className="text-lg font-semibold mb-3">Les délais de carence : ce qu'aucun vendeur ne dit spontanément</h2>
            <p className="text-sm text-muted-foreground leading-relaxed mb-4">
              Même après souscription, la couverture n'est pas immédiate sur tous les domaines. Chaque contrat prévoit un délai pendant lequel certains types de litiges restent exclus. Les seuils typiques observés chez les principaux assureurs :
            </p>
            <div className="overflow-hidden rounded-xl border border-border">
              <table className="w-full text-sm">
                <thead className="bg-muted/40">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-foreground">Domaine de litige</th>
                    <th className="text-left px-4 py-3 font-medium text-foreground">Délai de carence typique</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  <tr>
                    <td className="px-4 py-3 text-muted-foreground">Consommation, défense pénale courante</td>
                    <td className="px-4 py-3 text-foreground font-medium">Aucun ou 1 à 2 mois</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 text-muted-foreground">Litiges d'assurance (refus indemnisation, expertise)</td>
                    <td className="px-4 py-3 text-foreground font-medium">2 à 3 mois</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 text-muted-foreground">Litiges du travail (licenciement, harcèlement, contentieux CPAM)</td>
                    <td className="px-4 py-3 text-foreground font-medium">3 à 6 mois</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 text-muted-foreground">Litiges immobiliers, voisinage</td>
                    <td className="px-4 py-3 text-foreground font-medium">6 à 12 mois</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 text-muted-foreground">Divorce, successions, fiscalité</td>
                    <td className="px-4 py-3 text-foreground font-medium">12 à 24 mois (ou exclus)</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="text-xs text-muted-foreground mt-3 italic">Données consolidées à partir des conditions générales AXA, GMF, MAIF, Macif, Matmut — vérifier le contrat précis avant souscription.</p>
          </div>

          {/* Contrats qui la contiennent déjà */}
          <div className="p-4 rounded-xl bg-muted/30 border border-border">
            <h3 className="font-medium text-sm text-foreground mb-2">Vérifiez d'abord ce que vous avez déjà</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Avant de souscrire un contrat dédié, ouvrez vos contrats existants. Une protection juridique est fréquemment incluse, parfois gratuitement, dans : l'<strong className="text-foreground">assurance habitation</strong> (MRH), l'<strong className="text-foreground">assurance auto</strong>, les <strong className="text-foreground">cartes bancaires premium</strong> (Gold, Visa Premier, Platinum, Infinite), certaines <strong className="text-foreground">mutuelles santé</strong>, les <strong className="text-foreground">comités d'entreprise</strong>, et les contrats d'<strong className="text-foreground">assurance emprunteur</strong>. Les plafonds et domaines couverts varient, mais pour un litige ponctuel CPAM, MDPH ou d'indemnisation, ces couvertures sont souvent suffisantes. Demandez à chaque assureur une attestation écrite listant les garanties actives.
            </p>
          </div>

          {/* Cas concret vécu */}
          <div className="p-4 rounded-xl bg-accent/5 border border-accent/20" data-testid="pj-cas-concret">
            <h3 className="font-medium text-sm text-foreground mb-2">Cas concret — La PJ découverte trop tard</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Un salarié victime d'un accident du travail engage une procédure de reconnaissance qui se complique : refus initial de la CPAM, besoin d'une expertise contradictoire, orientation vers un avocat. Confronté à des honoraires d'avocat estimés à 4 000 €, il découvre par hasard l'existence des protections juridiques et décide d'en souscrire une. Quelques semaines plus tard, il déclare son litige à son nouvel assureur. La réponse tombe : <strong className="text-foreground">refus de prise en charge au motif que le fait générateur du litige — l'accident du travail — est antérieur à la date de souscription</strong>. La décision est juridiquement incontestable. Ce qu'il aurait dû faire avant : éplucher son contrat d'assurance habitation et celui de sa carte bancaire premium. La première contenait une PJ incluse avec un plafond de 15 000 €/litige, applicable aux contentieux sociaux — elle aurait couvert l'intégralité des honoraires. <strong className="text-foreground">Enseignement : la protection juridique ne se souscrit pas quand on en a besoin, elle se vérifie avant tout litige — idéalement maintenant.</strong>
            </p>
          </div>

          {/* Erreurs */}
          <div>
            <h3 className="font-medium text-sm text-foreground mb-3">Erreurs les plus coûteuses autour de la protection juridique</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Souscrire une PJ en urgence, après un litige déjà né</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Le principe du fait générateur antérieur exclut toute prise en charge. L'assureur refusera et c'est parfaitement légal. Aucun recours n'aboutit sur ce point.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Ignorer ses contrats existants et souscrire un contrat doublon</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ 60 à 80 % des assurés ont déjà une PJ dans habitation, auto, carte bancaire ou mutuelle. Faites un audit écrit auprès de chaque assureur avant toute nouvelle souscription.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Accepter l'avocat imposé par l'assureur sans discuter</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ La loi vous garantit le libre choix. L'avocat du réseau de l'assureur n'est pas toujours le plus spécialisé dans votre domaine (AT/MP, sécurité sociale, dommage corporel). Exercez ce droit par courrier écrit.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Déclarer son litige trop tard à l'assureur</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ La plupart des contrats imposent une déclaration dans les 5 à 15 jours suivant la connaissance du litige. Passé ce délai, la garantie peut être déchue même si toutes les autres conditions sont remplies.</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* Encart conversion */}
      <DossierExpressCTA
        testId="pj-cta-dossier"
        title="Litige en cours ou à venir ? Faites l'audit de votre couverture"
        text="La majorité des Français disposent d'une protection juridique sans le savoir — à condition de l'activer avant le litige. Le Dossier Express IA identifie vos couvertures existantes, leurs plafonds, leurs exclusions et la stratégie pour en tirer le maximum."
        ctaLabel="Faire mon audit PJ"
      />

      {/* FAQ */}
      <PJFaq />

      <TerrainNote
        testId="pj-terrain-note"
        text="Cette page est née d'un cas personnel vécu : avoir découvert la protection juridique trop tard. Elle rassemble ce qu'il aurait fallu que je sache, appliqué à chaque situation que j'accompagne."
      />

      {/* Section 4 - Avocats partenaires */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/5668473/pexels-photo-5668473.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Avocats partenaires"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
            <div>
              <Users className="w-12 h-12 text-accent mb-4" strokeWidth={1.5} />
              <h2 className="text-3xl font-semibold mb-6">
                Orientation vers des avocats partenaires
              </h2>
              <p className="text-muted-foreground mb-6">
                Au cours de mon parcours, j'ai constitué un réseau de professionnels du domaine 
                judiciaire spécialisés dans les litiges liés au travail, à la santé et aux assurances.
              </p>
              <p className="text-muted-foreground mb-6">
                Selon votre situation, je peux vous orienter vers des avocats partenaires compétents 
                dans les domaines suivants :
              </p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Droit de la sécurité sociale (AT/MP, invalidité)</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Droit du travail (licenciement, harcèlement)</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Droit des assurances (refus d'indemnisation)</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <span>Réparation du préjudice corporel</span>
                </li>
              </ul>
              <Link to="/partenaires">
                <Button variant="outline" className="rounded-full px-6 gap-2">
                  Découvrir le réseau de partenaires
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Section 5 - Accompagnement payant */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <Shield className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
              Accompagnement personnalisé
            </h2>
            <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
              Pour les personnes souhaitant être accompagnées dans l'activation et le suivi 
              de leur protection juridique, je propose une prestation dédiée.
            </p>
          </div>

          <Card className="bg-primary-foreground/10 border-primary-foreground/20">
            <CardContent className="p-8">
              <div className="grid md:grid-cols-2 gap-8 items-center">
                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary-foreground">
                    Accompagnement Protection Juridique
                  </h3>
                  <ul className="space-y-3 text-primary-foreground/80">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                      <span>Identification de vos garanties</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                      <span>Aide à la déclaration du litige</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                      <span>Suivi des échanges avec l'assureur</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                      <span>Orientation vers un avocat spécialisé</span>
                    </li>
                  </ul>
                </div>
                <div className="text-center md:text-right">
                  <p className="text-sm text-primary-foreground/60 mb-2">À partir de</p>
                  <p className="text-5xl font-bold text-primary-foreground mb-2">200 €</p>
                  <p className="text-sm text-primary-foreground/60 mb-6">Devis personnalisé selon situation</p>
                  <Link to="/contact">
                    <Button 
                      size="lg"
                      className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
                    >
                      Demander un devis
                      <ArrowRight className="w-4 h-4" />
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>

          <p className="text-center text-primary-foreground/50 text-sm mt-6">
            Première consultation téléphonique gratuite — 10 minutes pour évaluer votre situation
          </p>
        </div>
      </section>
    </main>
  );
};

const pjFaqData = [
  {
    question: "Puis-je souscrire une protection juridique maintenant si j'ai déjà un litige en cours ?",
    answer: "Non. La protection juridique fonctionne sur le principe du fait générateur : l'événement à l'origine du litige doit être survenu après la date de souscription et après le délai de carence applicable. Souscrire après la survenance du litige entraîne systématiquement un refus de prise en charge, parfaitement légal. La seule voie de recours consiste à vérifier vos anciens contrats d'assurance : si le fait générateur s'est produit pendant la période d'effet d'un contrat antérieur, cette ancienne PJ peut être activée."
  },
  {
    question: "Comment savoir si j'ai déjà une protection juridique sans le savoir ?",
    answer: "Vérifiez méthodiquement : votre contrat d'assurance habitation (MRH), votre contrat d'assurance auto, les conditions de votre carte bancaire (Gold, Visa Premier, Platinum, Infinite incluent très souvent une PJ), votre mutuelle santé, vos contrats d'assurance emprunteur. Demandez par écrit à chaque assureur une attestation listant les garanties PJ actives, leurs plafonds par litige, leurs franchises et les domaines couverts. 60 à 80 % des assurés disposent déjà d'une PJ qu'ils n'ont jamais activée."
  },
  {
    question: "Qu'est-ce qu'un délai de carence et combien de temps dure-t-il ?",
    answer: "Le délai de carence est une période initiale, après la souscription, pendant laquelle certaines garanties ne s'activent pas encore — même si le fait générateur est postérieur au contrat. Les seuils varient : aucun délai ou 1 à 2 mois pour la consommation, 2 à 3 mois pour les litiges d'assurance, 3 à 6 mois pour les litiges du travail, 6 à 12 mois pour l'immobilier, jusqu'à 24 mois pour divorce, successions et fiscalité. Vérifiez les conditions générales précises de votre contrat."
  },
  {
    question: "Combien coûte une protection juridique et est-ce rentable ?",
    answer: "Un contrat dédié coûte entre 15 et 80 €/an pour un particulier, selon l'étendue des garanties et les plafonds. À mettre en perspective avec les honoraires potentiels d'un avocat : 3 000 à 15 000 € pour une procédure prud'homale, 2 000 à 8 000 € pour un contentieux CPAM, 1 500 à 5 000 € pour une contestation d'expertise. Même une année de cotisation couvre largement les honoraires d'une seule procédure."
  },
  {
    question: "Mon assureur me refuse la prise en charge : quels sont mes recours ?",
    answer: "Demandez d'abord une motivation écrite du refus (courrier recommandé). Vérifiez si le motif est juridiquement fondé (antériorité du fait générateur, carence non écoulée, exclusion contractuelle, seuil d'intervention non atteint). Si vous estimez le refus injustifié, adressez une réclamation formelle au service réclamations de l'assureur. En cas de rejet maintenu, saisissez gratuitement le Médiateur de l'Assurance dans l'année suivant votre réclamation. En dernier recours, le tribunal judiciaire peut être saisi."
  },
  {
    question: "Puis-je choisir mon propre avocat ou dois-je prendre celui de l'assureur ?",
    answer: "Vous avez un droit fondamental de libre choix de l'avocat, garanti par le Code des assurances. L'assureur peut vous en proposer un via son réseau — ce n'est pas une obligation pour vous. Exercez votre droit par écrit, idéalement en précisant le nom de l'avocat choisi et sa spécialité (droit de la sécurité sociale, dommage corporel, droit du travail). L'assureur devra prendre en charge les honoraires dans la limite de son barème contractuel."
  },
  {
    question: "Combien de temps ai-je pour déclarer un litige à mon assureur ?",
    answer: "La plupart des contrats imposent une déclaration dans les 5 à 15 jours suivant la connaissance du litige. Ce délai est généralement précisé dans les conditions générales. Passé ce délai, l'assureur peut invoquer la déchéance de garantie — sauf cas de force majeure dûment justifié. En pratique, déclarez dès que vous avez connaissance du refus, de la décision défavorable ou du courrier litigieux, même si votre dossier n'est pas encore complet."
  }
];

const PJFaq = () => {
  const [openIndex, setOpenIndex] = useState(null);

  useEffect(() => {
    document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
      try { if (JSON.parse(s.textContent)['@type'] === 'FAQPage') s.remove(); } catch {}
    });
    const script = document.createElement('script');
    script.id = 'pj-faq-schema';
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": pjFaqData.map(f => ({
        "@type": "Question",
        "name": f.question,
        "acceptedAnswer": { "@type": "Answer", "text": f.answer }
      }))
    });
    document.head.appendChild(script);
    return () => { const el = document.getElementById('pj-faq-schema'); if (el) el.remove(); };
  }, []);

  return (
    <section className="section-padding bg-secondary/20" data-testid="pj-faq">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold mb-8 text-center">Questions fréquentes sur la protection juridique</h2>
        <div className="space-y-2">
          {pjFaqData.map((faq, i) => (
            <div key={i} className="border border-border rounded-xl overflow-hidden bg-background">
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
                data-testid={`pj-faq-${i}`}
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
