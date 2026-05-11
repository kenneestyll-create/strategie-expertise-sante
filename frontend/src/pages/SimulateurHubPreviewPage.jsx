import { useState, useMemo, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Calculator, Briefcase, Stethoscope, HeartPulse, Scale, ChevronRight, ShieldAlert, Sparkles } from 'lucide-react';

const PROD_HUB_URL = 'https://strategie-expertise-sante.fr/simulateur';

// ============================================================
// FAQ — 5 questions enrichies (~1000 mots cumulés)
// Schema.org FAQPage compatible
// ============================================================
const FAQ_ITEMS = [
  {
    q: "Quelle est la différence entre l'IPP et la rente d'incapacité ?",
    a: "L'IPP (Incapacité Permanente Partielle) désigne le taux d'incapacité fixé après consolidation par le médecin-conseil de la CPAM ou par expertise. C'est un pourcentage qui reflète l'atteinte définitive de votre intégrité physique ou psychique. La rente, elle, est la prestation financière qui découle de ce taux : à partir de 10 %, l'indemnisation prend la forme d'une rente trimestrielle viagère ; en dessous de 10 %, elle est versée sous forme d'un capital unique. Le calcul de la rente repose sur deux variables : le taux IPP et le salaire annuel de référence des 12 mois précédant l'arrêt de travail. La rente est revalorisée chaque année par décret. Au-delà du calcul mathématique, la précision de l'expertise médicale qui fixe le taux est le facteur déterminant : un taux sous-évalué de 5 points peut représenter plusieurs dizaines de milliers d'euros sur une vie."
  },
  {
    q: "Accident du travail ou maladie professionnelle : comment savoir quelle catégorie s'applique à ma situation ?",
    a: "L'accident du travail (AT) est un événement soudain et identifiable dans le temps survenu par le fait ou à l'occasion du travail. La présomption d'imputabilité joue automatiquement si l'accident survient au temps et au lieu de travail. La maladie professionnelle (MP) est une affection contractée progressivement en raison d'une exposition à un risque professionnel : les pathologies reconnues figurent dans des tableaux numérotés (RG 57 pour les TMS, RG 30 pour l'amiante, etc.). Si votre pathologie est inscrite dans un tableau et que vous remplissez les conditions médicales, administratives et d'exposition, la reconnaissance est de droit. Sinon, vous pouvez saisir le Comité Régional de Reconnaissance des Maladies Professionnelles (CRRMP) avec un taux d'IPP prévisible d'au moins 25 %. Le régime d'indemnisation est identique (rente, frais médicaux, capital décès), mais les démarches diffèrent radicalement : déclaration immédiate pour l'AT, dossier médico-administratif lourd pour la MP."
  },
  {
    q: "Puis-je cumuler l'AAH avec un salaire ?",
    a: "Oui, le cumul AAH-salaire est possible mais encadré. Depuis 2022, la déconjugalisation a transformé le calcul : seuls vos revenus personnels sont pris en compte (plus ceux du conjoint). Pour 2026, le montant maximum AAH est de 1 041,59 € par mois pour une personne seule. En cas d'activité professionnelle en milieu ordinaire, un abattement progressif s'applique : 80 % de votre salaire est neutralisé sur les premiers 487 € mensuels, puis 40 % au-delà. Concrètement, pour un salaire de 800 € net mensuel, l'AAH est réduite d'environ 300 €, vous percevez donc cumulativement ~1 540 € (salaire + AAH résiduelle). Pour un travail en ESAT, le calcul est plus favorable encore. La condition fondamentale reste le taux d'incapacité : ≥ 80 % ou compris entre 50 % et 79 % avec restriction substantielle et durable d'accès à l'emploi (RSDAE)."
  },
  {
    q: "Qu'est-ce que la faute inexcusable de l'employeur et que change-t-elle pour mon indemnisation ?",
    a: "La faute inexcusable est reconnue lorsque l'employeur avait — ou aurait dû avoir — conscience du danger auquel il exposait son salarié, sans prendre les mesures nécessaires pour l'en préserver. Elle s'applique aussi bien aux accidents du travail qu'aux maladies professionnelles. Sa reconnaissance, prononcée par le pôle social du tribunal judiciaire, ouvre droit à une majoration substantielle de la rente AT/MP (jusqu'à doubler), ainsi qu'à la réparation intégrale des préjudices personnels non couverts par le régime forfaitaire : souffrances physiques et morales, préjudice esthétique, préjudice d'agrément, préjudice sexuel, perte de chance professionnelle. Cette procédure suppose une démonstration rigoureuse fondée sur des éléments objectifs : signalements antérieurs, alertes du CSE, documents internes, expertises. Le délai de prescription est de deux ans à compter de la consolidation ou de la connaissance du lien entre la pathologie et le travail."
  },
  {
    q: "Les résultats des simulateurs ont-ils une valeur juridique ?",
    a: "Non, et il est essentiel de le comprendre. Les simulateurs proposés sur ce site sont des outils d'aide à la compréhension. Ils donnent une estimation indicative fondée sur les formules légales en vigueur, mais ils ne tiennent pas compte de l'ensemble des paramètres qui peuvent influencer votre dossier réel : antériorité de pathologies, contestation médicale, application de barèmes spécifiques, requalifications administratives, éventuelle faute inexcusable, prise en charge mutuelle complémentaire, fiscalité applicable. Pour obtenir une analyse juridiquement opposable, deux voies existent : l'examen contradictoire par le médecin-conseil de votre CPAM (gratuit mais purement administratif) ou l'analyse stratégique de votre dossier par un professionnel qui croisera l'ensemble des pièces médico-administratives. Notre service Dossier Express est conçu pour cette seconde voie : une lecture experte qui identifie les leviers d'optimisation et les angles morts qui échappent à une simple simulation chiffrée."
  }
];

// ============================================================
// Mini-simulateur Light : 3 champs, calcul local
// Formules indicatives — disclaimer obligatoire
// ============================================================
function MiniSimuLight() {
  const [type, setType] = useState('at');
  const [taux, setTaux] = useState('');
  const [salaire, setSalaire] = useState('');

  const result = useMemo(() => {
    const t = parseFloat(taux);
    const s = parseFloat(salaire);
    if (isNaN(t) || isNaN(s) || t < 0 || s < 0) return null;

    if (type === 'aah') {
      // AAH : revenus mensuels → abattement 80% sur 487€, puis 40%
      const revMensuel = s / 12;
      const tranche1 = Math.min(revMensuel, 487) * 0.20; // 80% neutralisé → 20% pris
      const tranche2 = Math.max(0, revMensuel - 487) * 0.60; // 40% neutralisé → 60% pris
      const baseAbattue = tranche1 + tranche2;
      const aahMensuel = Math.max(0, 1041.59 - baseAbattue);
      return {
        label: 'AAH mensuelle estimée (2026, hors avantage logement)',
        value: aahMensuel,
        suffix: '€/mois',
        detail: `Plafond maximum 2026 : 1 041,59 €/mois. Abattement appliqué sur vos revenus déclarés.`
      };
    }
    // AT / MP
    if (t >= 10) {
      const rente = s * (t / 2 / 100);
      return {
        label: `Rente ${type === 'mp' ? 'MP' : 'AT'} annuelle estimée`,
        value: rente,
        suffix: '€/an',
        detail: `Formule : Salaire annuel × (Taux IPP / 2). Versée trimestriellement à vie.`
      };
    }
    const capital = s * (t / 100) * 0.4;
    return {
      label: `Capital ${type === 'mp' ? 'MP' : 'AT'} estimé (taux < 10%)`,
      value: capital,
      suffix: '€ (capital unique)',
      detail: `En dessous de 10 % d'IPP, indemnisation versée en capital unique.`
    };
  }, [type, taux, salaire]);

  return (
    <Card data-testid="hub-mini-simu" className="bg-zinc-900/70 border-amber-500/20 backdrop-blur-sm">
      <CardContent className="p-6 sm:p-8">
        <div className="flex items-center gap-3 mb-5">
          <div className="h-10 w-10 rounded-xl bg-amber-500/10 border border-amber-500/30 grid place-items-center">
            <Calculator className="h-5 w-5 text-amber-400" />
          </div>
          <div>
            <h2 className="text-lg sm:text-xl font-semibold text-zinc-100">Estimation rapide</h2>
            <p className="text-sm text-zinc-400">3 champs — résultat indicatif immédiat</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="hub-type" className="text-zinc-300 text-sm">Type d'indemnisation</Label>
            <select
              id="hub-type"
              data-testid="hub-mini-simu-type"
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="mt-1 w-full h-10 rounded-md bg-zinc-950 border border-zinc-700 text-zinc-100 px-3 text-sm focus:outline-none focus:border-amber-500/60"
            >
              <option value="at">Accident du travail (AT)</option>
              <option value="mp">Maladie professionnelle (MP)</option>
              <option value="aah">AAH (revenus annuels)</option>
            </select>
          </div>
          <div>
            <Label htmlFor="hub-taux" className="text-zinc-300 text-sm">
              {type === 'aah' ? 'Non utilisé pour l\'AAH' : 'Taux IPP (%)'}
            </Label>
            <Input
              id="hub-taux"
              data-testid="hub-mini-simu-taux"
              type="number"
              min="0"
              max="100"
              placeholder={type === 'aah' ? '—' : 'Ex. 15'}
              value={taux}
              onChange={(e) => setTaux(e.target.value)}
              disabled={type === 'aah'}
              className="mt-1 bg-zinc-950 border-zinc-700 text-zinc-100 disabled:opacity-40"
            />
          </div>
          <div>
            <Label htmlFor="hub-salaire" className="text-zinc-300 text-sm">
              {type === 'aah' ? 'Revenus annuels (€)' : 'Salaire annuel brut (€)'}
            </Label>
            <Input
              id="hub-salaire"
              data-testid="hub-mini-simu-salaire"
              type="number"
              min="0"
              placeholder="Ex. 24 000"
              value={salaire}
              onChange={(e) => setSalaire(e.target.value)}
              className="mt-1 bg-zinc-950 border-zinc-700 text-zinc-100"
            />
          </div>
        </div>

        {result && (
          <div
            data-testid="hub-mini-simu-result"
            className="mt-6 rounded-lg border border-amber-500/30 bg-gradient-to-br from-amber-500/5 to-transparent p-5"
          >
            <p className="text-xs uppercase tracking-wider text-amber-400/80 mb-1">{result.label}</p>
            <p className="text-3xl font-light text-amber-300">
              {result.value.toLocaleString('fr-FR', { maximumFractionDigits: 2 })}{' '}
              <span className="text-base text-zinc-400">{result.suffix}</span>
            </p>
            <p className="text-xs text-zinc-500 mt-2">{result.detail}</p>
          </div>
        )}

        <p className="mt-5 text-xs text-zinc-500 italic flex items-start gap-2">
          <ShieldAlert className="h-4 w-4 text-amber-500/70 shrink-0 mt-0.5" />
          Résultat strictement indicatif. Pour un chiffrage opposable, utilisez nos simulateurs spécialisés ou faites analyser votre dossier.
        </p>
      </CardContent>
    </Card>
  );
}

// ============================================================
// Arbre de décision — 4 blocs DÉSACTIVÉS (Bientôt disponible)
// ============================================================
const DECISION_BLOCKS = [
  {
    key: 'at',
    icon: Briefcase,
    title: 'Accident du travail (IPP)',
    desc: 'Calcul de rente ou capital après consolidation. Faute inexcusable, recours expertise.',
    futureSlug: 'simulateur-rente-ipp-accident-travail',
  },
  {
    key: 'mp',
    icon: Stethoscope,
    title: 'Maladie professionnelle',
    desc: 'Tableaux RG, reconnaissance CRRMP, calcul rente, contestation taux IPP.',
    futureSlug: 'simulateur-rente-maladie-professionnelle',
  },
  {
    key: 'aah',
    icon: HeartPulse,
    title: 'AAH + cumul salaire',
    desc: 'Calcul après déconjugalisation, abattements progressifs, plafonds 2026.',
    futureSlug: 'simulateur-aah-salaire-cumul',
  },
  {
    key: 'fi',
    icon: Scale,
    title: 'Faute inexcusable',
    desc: 'Majoration de rente, réparation intégrale des préjudices personnels.',
    futureSlug: 'simulateur-rente-ipp-faute-inexcusable',
  },
];

function DecisionTree() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="hub-decision-tree">
      {DECISION_BLOCKS.map((b) => {
        const Icon = b.icon;
        return (
          <div
            key={b.key}
            data-testid={`hub-decision-block-${b.key}`}
            aria-disabled="true"
            className="relative group rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 opacity-60 pointer-events-none select-none transition-colors"
          >
            <div className="flex items-start gap-4">
              <div className="h-11 w-11 rounded-lg bg-zinc-800/60 border border-zinc-700 grid place-items-center shrink-0">
                <Icon className="h-5 w-5 text-zinc-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-3 mb-1">
                  <h3 className="text-base font-medium text-zinc-300">{b.title}</h3>
                  <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full border border-amber-500/30 bg-amber-500/5 text-amber-400">
                    <Sparkles className="h-3 w-3" /> Bientôt
                  </span>
                </div>
                <p className="text-sm text-zinc-500 leading-relaxed">{b.desc}</p>
              </div>
              <ChevronRight className="h-4 w-4 text-zinc-600 self-center" />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ============================================================
// FAQ section
// ============================================================
function FAQSection() {
  return (
    <div className="space-y-4" data-testid="hub-faq">
      {FAQ_ITEMS.map((item, i) => (
        <details
          key={i}
          data-testid={`hub-faq-item-${i}`}
          className="group rounded-xl border border-zinc-800 bg-zinc-900/40 open:border-amber-500/30 open:bg-zinc-900/60 transition-colors"
        >
          <summary className="cursor-pointer list-none px-5 py-4 flex items-start justify-between gap-4">
            <span className="text-base font-medium text-zinc-200 group-open:text-amber-300 transition-colors">
              {item.q}
            </span>
            <ChevronRight className="h-4 w-4 text-zinc-500 shrink-0 mt-1 group-open:rotate-90 transition-transform" />
          </summary>
          <div className="px-5 pb-5 text-sm text-zinc-400 leading-relaxed">
            {item.a}
          </div>
        </details>
      ))}
    </div>
  );
}

// ============================================================
// JSON-LD : BreadcrumbList + FAQPage
// ============================================================
function StructuredData() {
  useEffect(() => {
    const breadcrumb = {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Accueil', item: 'https://strategie-expertise-sante.fr/' },
        { '@type': 'ListItem', position: 2, name: 'Simulateurs', item: PROD_HUB_URL },
      ],
    };
    const faq = {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: FAQ_ITEMS.map((it) => ({
        '@type': 'Question',
        name: it.q,
        acceptedAnswer: { '@type': 'Answer', text: it.a },
      })),
    };

    const make = (id, payload) => {
      const existing = document.getElementById(id);
      if (existing) existing.remove();
      const s = document.createElement('script');
      s.id = id;
      s.type = 'application/ld+json';
      s.text = JSON.stringify(payload);
      document.head.appendChild(s);
    };
    make('hub-breadcrumb-schema', breadcrumb);
    make('hub-faq-schema', faq);
    return () => {
      ['hub-breadcrumb-schema', 'hub-faq-schema'].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.remove();
      });
    };
  }, []);
  return null;
}

// ============================================================
// Page principale
// ============================================================
export default function SimulateurHubPreviewPage() {
  // Override the static <meta name="robots"> from index.html.
  // Helmet alone fails because the tag is already present in HTML and
  // react-helmet-async appends instead of replacing in some cases.
  useEffect(() => {
    const meta = document.querySelector('meta[name="robots"]');
    const previous = meta ? meta.getAttribute('content') : null;
    if (meta) meta.setAttribute('content', 'noindex, nofollow');
    return () => {
      if (meta && previous !== null) meta.setAttribute('content', previous);
    };
  }, []);

  return (
    <>
      <Helmet
        title="Simulateurs d'indemnisation : IPP, AAH, accident du travail | Stratégie & Expertise Santé"
        meta={[
          { name: 'robots', content: 'noindex, nofollow' },
          {
            name: 'description',
            content: "Hub d'orientation vers les simulateurs spécialisés : rente IPP (accident du travail, maladie professionnelle), AAH et cumul revenus, faute inexcusable.",
          },
        ]}
        link={[{ rel: 'canonical', href: PROD_HUB_URL }]}
      />
      <StructuredData />

      <main className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="hub-page">
        {/* Hero */}
        <section className="relative overflow-hidden border-b border-zinc-900">
          <div className="absolute inset-0 bg-gradient-to-br from-amber-500/[0.04] via-transparent to-transparent pointer-events-none" />
          <div className="relative max-w-5xl mx-auto px-5 sm:px-8 pt-16 pb-12">
            <p className="text-xs uppercase tracking-[0.2em] text-amber-400/80 mb-4" data-testid="hub-eyebrow">
              Hub d'orientation
            </p>
            <h1
              className="text-3xl sm:text-4xl lg:text-5xl font-light text-zinc-50 leading-[1.1] tracking-tight max-w-3xl"
              data-testid="hub-h1"
            >
              Simulateurs d'indemnisation : <span className="text-amber-400">IPP, AAH, accident du travail</span>
            </h1>
            <p className="mt-5 text-base sm:text-lg text-zinc-400 max-w-2xl leading-relaxed" data-testid="hub-subtitle">
              Accédez au simulateur adapté à votre situation — accident du travail, maladie professionnelle,
              AAH ou faute inexcusable de l'employeur.
            </p>
          </div>
        </section>

        {/* Mini-simu Light */}
        <section className="max-w-5xl mx-auto px-5 sm:px-8 py-12">
          <MiniSimuLight />
        </section>

        {/* Arbre de décision */}
        <section className="max-w-5xl mx-auto px-5 sm:px-8 py-8">
          <div className="mb-6">
            <h2 className="text-xl sm:text-2xl font-light text-zinc-100" data-testid="hub-tree-title">
              Choisissez votre situation
            </h2>
            <p className="text-sm text-zinc-500 mt-1">
              Chaque simulateur spécialisé arrive prochainement avec ses propres formules et leviers d'optimisation.
            </p>
          </div>
          <DecisionTree />
        </section>

        {/* FAQ */}
        <section className="max-w-5xl mx-auto px-5 sm:px-8 py-12 border-t border-zinc-900 mt-8">
          <div className="mb-6">
            <h2 className="text-xl sm:text-2xl font-light text-zinc-100" data-testid="hub-faq-title">
              Questions fréquentes sur les simulateurs d'indemnisation
            </h2>
            <p className="text-sm text-zinc-500 mt-1">
              Comprendre les notions clés pour utiliser le bon simulateur.
            </p>
          </div>
          <FAQSection />
        </section>

        {/* Footer note preview */}
        <section className="max-w-5xl mx-auto px-5 sm:px-8 py-10 border-t border-zinc-900">
          <p className="text-xs text-zinc-600 italic">
            Page d'orientation. Les simulateurs spécialisés seront accessibles prochainement.
            Pour une analyse personnalisée et opposable, faites étudier votre dossier par notre équipe.
          </p>
        </section>
      </main>
    </>
  );
}
