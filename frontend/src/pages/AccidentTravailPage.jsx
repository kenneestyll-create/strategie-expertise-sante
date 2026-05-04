import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { DossierExpressCTA } from '@/components/DossierExpressCTA';
import { PillarLeadMagnet } from '@/components/PillarLeadMagnet';
import { TerrainNote } from '@/components/TerrainNote';
import { 
  ArrowRight, 
  AlertCircle, 
  FileCheck, 
  Stethoscope, 
  Building2,
  CheckCircle,
  ClipboardList,
  Heart,
  ChevronDown
} from 'lucide-react';

export const AccidentTravailPage = () => {
  const etapesAT = [
    "Déclaration de l'accident",
    "Suivi médical",
    "Expertise médicale",
    "Consolidation",
    "Évaluation du taux d'incapacité permanente"
  ];

  const etapesMP = [
    "Un dossier médical solide",
    "Des expertises médicales",
    "Des échanges avec les organismes sociaux"
  ];

  const accompagnement = [
    { icon: FileCheck, text: "Comprendre les démarches" },
    { icon: ClipboardList, text: "Analyser les décisions administratives" },
    { icon: Stethoscope, text: "Préparer certaines étapes importantes du dossier" }
  ];

  return (
    <main className="page-transition pt-20">
      <SEO title="Accident du travail et maladie professionnelle : droits et recours" description="AT ou maladie professionnelle ? Vos droits, les délais stricts, les erreurs à éviter et les recours pour faire valoir vos droits efficacement." path="/accident-travail-maladie-professionnelle" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Vos droits</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="atmp-title">
              Accident du travail et maladie professionnelle : comprendre vos droits et vos recours
            </h1>
            <p className="text-lg text-muted-foreground">
              Un accident du travail ou une maladie professionnelle peut bouleverser toute une vie.
              Au-delà des douleurs physiques, les démarches administratives et médicales peuvent 
              devenir complexes : expertises, reconnaissance de l'origine professionnelle, taux 
              d'incapacité, relations avec l'employeur ou l'assurance.
            </p>
          </div>
        </div>
      </section>

      {/* Accident du travail Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-accent" strokeWidth={1.5} />
                </div>
                <h2 className="text-3xl font-semibold">Accident du travail</h2>
              </div>
              
              <p className="text-muted-foreground mb-6">
                Un accident du travail est un événement soudain survenu pendant l'activité 
                professionnelle ou à l'occasion du travail et ayant entraîné une lésion.
              </p>

              <Card className="border-border">
                <CardHeader>
                  <CardTitle className="text-lg">Les étapes peuvent inclure :</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {etapesAT.map((etape, index) => (
                      <div key={index} className="flex items-start gap-3" data-testid={`etape-at-${index}`}>
                        <div className="w-6 h-6 bg-muted rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-xs font-medium text-muted-foreground">{index + 1}</span>
                        </div>
                        <span>{etape}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/5699456/pexels-photo-5699456.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Accident du travail"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Maladie professionnelle Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            <div className="order-2 lg:order-1">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/7089020/pexels-photo-7089020.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Maladie professionnelle"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            <div className="order-1 lg:order-2">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-accent" strokeWidth={1.5} />
                </div>
                <h2 className="text-3xl font-semibold">Maladie professionnelle</h2>
              </div>
              
              <p className="text-muted-foreground mb-6">
                Une maladie professionnelle est une pathologie directement liée aux conditions de travail.
              </p>

              <Card className="border-border">
                <CardHeader>
                  <CardTitle className="text-lg">Sa reconnaissance peut nécessiter :</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {etapesMP.map((etape, index) => (
                      <div key={index} className="flex items-start gap-3" data-testid={`etape-mp-${index}`}>
                        <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                        <span>{etape}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* SEO Content */}
      <section className="section-padding" data-testid="atmp-seo-content">
        <div className="max-w-3xl mx-auto space-y-8">

          {/* L'essentiel */}
          <div className="p-5 rounded-xl bg-[#1a1a2e]/[0.03] border border-[#C9A84C]/20">
            <h2 className="font-semibold text-base mb-3 text-foreground">L'essentiel à retenir</h2>
            <ul className="space-y-1.5 list-none pl-0 text-sm text-muted-foreground">
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>AT : informer l'employeur sous <strong className="text-foreground">24h</strong> — l'employeur déclare à la CPAM sous <strong className="text-foreground">48h</strong></span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>MP : déclarer à la CPAM dans les <strong className="text-foreground">2 ans</strong> — la CPAM statue en <strong className="text-foreground">120 jours</strong></span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Soins pris en charge à <strong className="text-foreground">100%</strong> sans avance de frais</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Indemnités journalières : <strong className="text-foreground">60%</strong> les 28 premiers jours, puis <strong className="text-foreground">80%</strong></span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Après consolidation : taux d'IPP → capital (&lt; 10%) ou rente viagère (≥ 10%)</span></li>
              <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Tout refus est contestable : CRA ou CMRA dans les <strong className="text-foreground">2 mois</strong></span></li>
            </ul>
            <p className="text-xs text-muted-foreground mt-3 italic">Informations basées sur le Code de la Sécurité sociale et les procédures CPAM en vigueur en 2026.</p>
          </div>

          {/* Pourquoi certains dossiers bloquent */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Pourquoi certains dossiers AT/MP bloquent</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              La majorité des blocages ne viennent pas de l'absence de droits, mais de <strong className="text-foreground">failles dans le dossier initial</strong>. Un employeur qui émet des réserves déclenche automatiquement une enquête CPAM qui rallonge les délais de plusieurs mois. Un certificat médical initial qui ne mentionne pas toutes les lésions — même secondaires — ferme la porte à leur prise en charge ultérieure. Une consolidation fixée alors que des soins sont encore en cours fige un taux d'IPP sous-évalué. Pour les maladies hors tableau, le seuil de 25% d'IPP requis par le CRRMP constitue un obstacle fréquent.
            </p>
          </div>

          {/* Consolidation */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Consolidation : l'étape décisive</h2>
            <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
              <p>
                La consolidation marque le moment où votre état de santé est considéré comme stabilisé. <strong className="text-foreground">Stabilisé ne signifie pas guéri</strong> — vous pouvez conserver des séquelles importantes. C'est à cette date que le médecin conseil fixe votre taux d'IPP, qui détermine votre indemnisation. Le piège le plus fréquent : une consolidation prématurée, alors que des soins sont encore en cours ou qu'une intervention est programmée. Le taux est alors évalué sur un état incomplet et ne reflète pas vos séquelles réelles.
              </p>
              <p>
                En cas de désaccord, vous pouvez saisir la Commission Médicale de Recours Amiable (CMRA) dans les 2 mois. L'accompagnement par un médecin de recours lors de cette contestation change significativement le résultat.
              </p>
            </div>
          </div>

          {/* Après la consolidation */}
          <div className="p-4 rounded-xl bg-muted/30 border border-border">
            <h3 className="font-medium text-sm text-foreground mb-1.5">Après la consolidation : les recours restent possibles</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              La consolidation ne ferme pas les portes. En cas d'aggravation, vous pouvez déclarer une rechute. Le taux d'IPP reste contestable. La faute inexcusable de l'employeur peut être engagée après consolidation. Et si vous êtes déclaré inapte, des indemnités spécifiques s'appliquent.
            </p>
          </div>

          {/* Faute inexcusable */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Faute inexcusable de l'employeur</h2>
            <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
              <p>
                Si votre employeur avait ou aurait dû avoir conscience du danger et n'a pas pris les mesures de prévention nécessaires, vous pouvez engager une procédure en <strong className="text-foreground">faute inexcusable</strong>. Les conséquences sont concrètes : votre rente AT/MP est majorée à son taux maximum, et vous obtenez la réparation de préjudices complémentaires — souffrances endurées, préjudice esthétique, perte de gains, préjudice d'agrément.
              </p>
              <p>
                C'est le levier principal pour passer d'une indemnisation forfaitaire à une réparation intégrale. Cette procédure se fait devant le tribunal judiciaire (pôle social) et nécessite un dossier documenté.
              </p>
            </div>
          </div>

          {/* Employeur ne déclare pas */}
          <div className="p-5 rounded-xl bg-accent/5 border border-accent/15">
            <h2 className="text-lg font-semibold mb-2 text-foreground">Votre employeur ne déclare pas l'accident ?</h2>
            <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
              <p>
                C'est une situation fréquente — pression, minimisation, ou simple négligence. <strong className="text-foreground">Vous pouvez déclarer vous-même l'accident directement auprès de la CPAM</strong>, par courrier recommandé, dans un délai de 2 ans. L'employeur s'expose à une amende pouvant atteindre 3 750 €. Dès les premières heures : conservez toutes les preuves (témoignages de collègues, SMS, photos du lieu, rapport des secours).
              </p>
            </div>
          </div>

          {/* Pathologies psychiques */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Pathologies psychiques et reconnaissance professionnelle</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Certaines pathologies psychiques — burn-out, anxiété généralisée, dépression réactionnelle, stress post-traumatique — peuvent être reconnues en maladie professionnelle sous conditions. Elles ne figurent pas dans les tableaux officiels, ce qui implique un passage devant le CRRMP avec un seuil d'IPP de 25%. La constitution du dossier est plus exigeante, mais la reconnaissance est possible lorsque le lien direct avec les conditions de travail est démontré.
            </p>
          </div>

          {/* Cas concrets */}
          <div>
            <h2 className="text-lg font-semibold mb-3">Cas concrets</h2>
            <div className="space-y-3">
              <div className="p-4 rounded-xl bg-muted/30 border border-border">
                <p className="font-medium text-sm text-foreground mb-1.5">Cas 1 — Chute sur chantier, employeur ne déclare pas</p>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Un ouvrier chute d'un échafaudage. L'employeur minimise l'incident et ne fait pas la déclaration. Le salarié consulte un médecin le jour même (certificat médical initial décrivant fracture et lésions), rassemble les témoignages de collègues, et déclare lui-même l'accident à la CPAM par recommandé. La CPAM reconnaît l'AT sous 30 jours. Après consolidation, un taux de 18% est fixé ouvrant droit à une rente viagère.
                </p>
              </div>
              <div className="p-4 rounded-xl bg-muted/30 border border-border">
                <p className="font-medium text-sm text-foreground mb-1.5">Cas 2 — Canal carpien, maladie professionnelle tableau 57</p>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Une aide-soignante développe un syndrome du canal carpien bilatéral après 12 ans de manutention. L'employeur conteste le lien professionnel. Elle déclare la maladie à la CPAM avec certificat médical et bilans spécialisés. La pathologie correspond au tableau 57C — la reconnaissance est obtenue après enquête. Le médecin conseil fixe un taux de 8% (capital). La salariée conteste avec un médecin de recours et obtient 12% au tribunal — passant du capital à la rente.
                </p>
              </div>
            </div>
          </div>

          {/* Erreurs fréquentes */}
          <div>
            <h2 className="text-lg font-semibold mb-3">Erreurs fréquentes</h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Ne pas déclarer dans les 24 heures</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Un retard de déclaration donne à l'employeur un argument pour contester le caractère professionnel. Déclarez immédiatement, même si les symptômes semblent mineurs.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Un certificat médical initial qui ne mentionne pas toutes les lésions</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Seules les lésions inscrites sur le CMI seront prises en charge. Une douleur cervicale non mentionnée le jour de l'accident ne pourra pas être rattachée ensuite. Décrivez tout, même les douleurs secondaires.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Accepter une consolidation prématurée sans contester</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Si des soins sont encore en cours ou qu'une intervention est programmée, contestez dans les 2 mois auprès de la CMRA. Une consolidation prématurée fige un taux d'IPP qui ne reflète pas vos séquelles réelles.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                <div>
                  <p className="font-medium text-foreground">Ne pas contester un refus de reconnaissance</p>
                  <p className="text-muted-foreground text-xs mt-0.5">→ Le recours devant la CRA est gratuit et doit être déposé dans les 2 mois. Un dossier renforcé avec des éléments médicaux nouveaux aboutit régulièrement à une issue favorable.</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* Encart conversion */}
      <PillarLeadMagnet
        pageId="accident-travail-maladie-professionnelle"
        memoTitle="Check-list : les 7 réflexes immédiats après un accident du travail"
        bulletPoints={[
          "Les 24 premières heures qui décident de tout votre dossier",
          "La preuve testimoniale : l'arme oubliée par 90 % des dossiers",
          "Le silence de la CPAM : présomption acceptée, mais piège possible",
          "Les pièces à exiger immédiatement, avant qu'elles deviennent introuvables",
        ]}
      />

      <DossierExpressCTA
        testId="atmp-cta-dossier"
        title={"AT non déclaré, MP refusée, IPP sous-évalué\u00A0?"}
        text="La majorité des dossiers AT/MP bloquent sur des failles dans le dossier initial : certificat médical incomplet, déclaration tardive, consolidation prématurée. Le Dossier Express IA identifie précisément où votre dossier perd de la valeur et la stratégie pour le redresser."
        ctaLabel="Analyser mon dossier AT/MP"
      />

      {/* FAQ */}
      <ATMPFaq />

      <TerrainNote
        testId="atmp-terrain-note"
        text="Ce contenu est issu des dossiers AT/MP que j'accompagne concrètement : consolidations anticipées, refus CPAM, rechutes, fautes inexcusables, maladies hors tableau."
      />

      {/* Accompagnement Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <Heart className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="text-3xl font-semibold mb-4">
              Mon accompagnement
            </h2>
            <p className="text-primary-foreground/70">
              Je propose un accompagnement pour vous aider dans ces démarches souvent complexes.
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-6 mb-10">
            {accompagnement.map((item, index) => (
              <div 
                key={index} 
                className="bg-primary-foreground/10 rounded-xl p-6 text-center"
                data-testid={`accompagnement-atmp-${index}`}
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
                data-testid="atmp-cta-button"
              >
                Me contacter
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>

          {/* Encarts IP & PGPF */}
          <div className="grid sm:grid-cols-2 gap-6 mt-12">
            <div className="bg-primary-foreground/10 rounded-xl p-6" data-testid="atmp-ip-card">
              <h3 className="text-lg font-semibold text-primary-foreground mb-3">Incidence Professionnelle (IP)</h3>
              <p className="text-sm text-primary-foreground/70 mb-4">
                Vos séquelles impactent votre carrière ? Vous avez peut-être droit à une indemnisation complémentaire au titre de l'incidence professionnelle : pénibilité accrue, dévalorisation, reconversion...
              </p>
              <Link to="/ressources" className="text-sm text-accent hover:underline font-medium">
                En savoir plus sur l'IP →
              </Link>
            </div>
            <div className="bg-primary-foreground/10 rounded-xl p-6" data-testid="atmp-pgpf-card">
              <h3 className="text-lg font-semibold text-primary-foreground mb-3">Perte de Gains Futurs (PGPF)</h3>
              <p className="text-sm text-primary-foreground/70 mb-4">
                Votre accident ou maladie réduit durablement vos revenus ? La PGPF compense cette perte définitive par capitalisation. Découvrez la méthode de calcul et les justificatifs.
              </p>
              <Link to="/ressources" className="text-sm text-accent hover:underline font-medium">
                En savoir plus sur la PGPF →
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};

const atmpFaqData = [
  {
    question: "Mon employeur refuse de déclarer mon accident du travail. Que faire ?",
    answer: "L'employeur dispose de 48h pour déclarer l'accident à la CPAM. S'il refuse, vous pouvez déclarer vous-même l'accident directement à votre CPAM dans un délai de 2 ans, à l'aide du formulaire S6201. Joignez le certificat médical initial et tout élément de preuve (témoignages, échanges écrits). Le refus de déclaration par l'employeur n'éteint pas vos droits."
  },
  {
    question: "Comment contester un refus de reconnaissance d'accident du travail ?",
    answer: "Vous disposez de 2 mois à compter de la notification du refus pour saisir la Commission de Recours Amiable (CRA) de la CPAM. Le recours est gratuit, écrit et motivé. Renforcez votre dossier avec des éléments médicaux nouveaux, des témoignages et des écrits faisant le lien entre l'événement et l'activité professionnelle. En cas de rejet de la CRA, vous pouvez ensuite saisir le pôle social du Tribunal Judiciaire."
  },
  {
    question: "Qu'est-ce que la consolidation et pourquoi est-ce une étape décisive ?",
    answer: "La consolidation est la date à laquelle votre état de santé est considéré comme stabilisé — pas guéri. C'est à cette date que le médecin conseil fixe votre taux d'IPP, qui détermine votre indemnisation. Une consolidation prématurée, fixée alors que des soins sont encore en cours ou qu'une intervention est programmée, fige un taux sous-évalué. Vous pouvez la contester dans les 2 mois auprès de la CMRA."
  },
  {
    question: "Quelle est la différence entre une rente et un capital après un accident du travail ?",
    answer: "Si votre taux d'IPP est inférieur à 10 %, vous percevez un capital versé en une fois. Si votre taux est supérieur ou égal à 10 %, vous percevez une rente viagère, versée trimestriellement (et mensuellement si IPP ≥ 50 %). Le montant dépend du taux d'IPP et de votre salaire annuel de référence des 12 mois précédant l'arrêt."
  },
  {
    question: "Qu'est-ce que la faute inexcusable de l'employeur et comment l'engager ?",
    answer: "La faute inexcusable est reconnue lorsque l'employeur avait conscience du danger et n'a pas pris les mesures nécessaires pour en préserver le salarié. Sa reconnaissance ouvre droit à une majoration de la rente et à l'indemnisation de préjudices spécifiques (souffrances physiques et morales, préjudice esthétique, préjudice d'agrément, perte de chance professionnelle). La procédure se mène devant le pôle social du Tribunal Judiciaire dans un délai de 2 ans."
  },
  {
    question: "Comment faire reconnaître une maladie hors tableau ?",
    answer: "Si votre maladie n'est pas inscrite aux tableaux de maladies professionnelles, ou si toutes les conditions du tableau ne sont pas remplies, votre dossier est transmis au Comité Régional de Reconnaissance des Maladies Professionnelles (CRRMP). La reconnaissance hors tableau exige notamment un taux d'IPP prévisionnel d'au moins 25 %. La constitution du dossier est déterminante : justificatifs médicaux, descriptif des expositions, lien direct avec l'activité professionnelle."
  },
  {
    question: "Puis-je déclarer une rechute après consolidation ?",
    answer: "Oui. La rechute correspond à une aggravation de votre état en lien direct avec l'accident ou la maladie initiale, après la date de consolidation. Elle doit être attestée par un certificat médical de rechute établi par votre médecin. Une fois reconnue, elle réouvre vos droits aux soins à 100 % et aux indemnités journalières. Une nouvelle évaluation du taux d'IPP peut être demandée."
  },
  {
    question: "Quels sont les délais à respecter en accident du travail et maladie professionnelle ?",
    answer: "Pour un AT : informer l'employeur sous 24h, l'employeur déclare à la CPAM sous 48h, la CPAM statue en 30 jours (extensible à 90 en cas d'investigation). Pour une MP : déclaration à la CPAM dans les 2 ans suivant la cessation du travail liée à la maladie ou la première constatation médicale, instruction en 120 jours. Pour contester un refus : 2 mois pour saisir la CRA. Pour engager une faute inexcusable : 2 ans."
  }
];

const ATMPFaq = () => {
  const [openIndex, setOpenIndex] = useState(null);

  useEffect(() => {
    document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
      try { if (JSON.parse(s.textContent)['@type'] === 'FAQPage') s.remove(); } catch {}
    });
    const script = document.createElement('script');
    script.id = 'atmp-faq-schema';
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": atmpFaqData.map(f => ({
        "@type": "Question",
        "name": f.question,
        "acceptedAnswer": { "@type": "Answer", "text": f.answer }
      }))
    });
    document.head.appendChild(script);
    return () => { const el = document.getElementById('atmp-faq-schema'); if (el) el.remove(); };
  }, []);

  return (
    <section className="section-padding bg-secondary/30" data-testid="atmp-faq">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold mb-8 text-center">Questions fréquentes AT/MP</h2>
        <div className="space-y-2">
          {atmpFaqData.map((faq, i) => (
            <div key={i} className="border border-border rounded-xl overflow-hidden bg-background">
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
                data-testid={`atmp-faq-${i}`}
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
