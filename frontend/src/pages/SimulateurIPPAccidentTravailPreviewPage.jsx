import { useState, useMemo, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Calculator, ShieldAlert, AlertCircle, FileText, Scale, ChevronRight } from 'lucide-react';

const PROD_URL = 'https://strategie-expertise-sante.fr/simulateur-rente-ipp-accident-travail';

// Note: tant que cette page reste en preview (route -preview), elle reste noindex.
// Au déploiement Vague 1 production, l'URL canonique deviendra la PROD_URL et le
// noindex sera retiré.

function MiniSimuAT() {
  const [taux, setTaux] = useState('');
  const [salaire, setSalaire] = useState('');
  const [salaireType, setSalaireType] = useState('annual');
  const [fauteInex, setFauteInex] = useState(false);

  const result = useMemo(() => {
    const t = parseFloat(taux);
    const s = parseFloat(salaire);
    if (isNaN(t) || isNaN(s) || t < 0 || s < 0) return null;

    const salaireAnnuel = salaireType === 'monthly' ? s * 12 : s;

    if (t >= 10) {
      // Taux utile = taux/2 pour la fraction <=50%, puis taux*1.5 pour la fraction >50%
      // Formule officielle : pour partie <=50% → taux/2 ; partie >50% → (taux-50)*1.5 + 25
      const tauxUtile = t <= 50 ? t / 2 : 25 + (t - 50) * 1.5;
      const rente = salaireAnnuel * (tauxUtile / 100);
      const renteFI = fauteInex ? rente * 2 : null;
      return {
        type: 'rente',
        rente,
        renteFI,
        tauxUtile,
        salaireAnnuel,
      };
    }
    // Taux < 10% → capital unique (barème indicatif)
    const capital = salaireAnnuel * (t / 100) * 0.4;
    return {
      type: 'capital',
      capital,
      salaireAnnuel,
    };
  }, [taux, salaire, salaireType, fauteInex]);

  return (
    <Card data-testid="at-mini-simu" className="bg-zinc-900/70 border-amber-500/20 backdrop-blur-sm">
      <CardContent className="p-6 sm:p-8">
        <div className="flex items-center gap-3 mb-5">
          <div className="h-10 w-10 rounded-xl bg-amber-500/10 border border-amber-500/30 grid place-items-center">
            <Calculator className="h-5 w-5 text-amber-400" />
          </div>
          <div>
            <h2 className="text-lg sm:text-xl font-semibold text-zinc-100">Simulateur Rente IPP — Accident du Travail</h2>
            <p className="text-sm text-zinc-400">Calcul détaillé selon les règles légales en vigueur</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="at-taux" className="text-zinc-300 text-sm">Taux IPP (%)</Label>
            <Input
              id="at-taux"
              data-testid="at-mini-taux"
              type="number"
              min="0"
              max="100"
              placeholder="Ex. 25"
              value={taux}
              onChange={(e) => setTaux(e.target.value)}
              className="mt-1 bg-zinc-950 border-zinc-700 text-zinc-100"
            />
          </div>
          <div>
            <Label htmlFor="at-salaire" className="text-zinc-300 text-sm">Salaire de référence (€)</Label>
            <Input
              id="at-salaire"
              data-testid="at-mini-salaire"
              type="number"
              min="0"
              placeholder="Ex. 30 000"
              value={salaire}
              onChange={(e) => setSalaire(e.target.value)}
              className="mt-1 bg-zinc-950 border-zinc-700 text-zinc-100"
            />
          </div>
          <div>
            <Label htmlFor="at-type" className="text-zinc-300 text-sm">Période du salaire</Label>
            <select
              id="at-type"
              data-testid="at-mini-type"
              value={salaireType}
              onChange={(e) => setSalaireType(e.target.value)}
              className="mt-1 w-full h-10 rounded-md bg-zinc-950 border border-zinc-700 text-zinc-100 px-3 text-sm focus:outline-none focus:border-amber-500/60"
            >
              <option value="annual">Annuel brut</option>
              <option value="monthly">Mensuel brut</option>
            </select>
          </div>
        </div>

        <label className="mt-4 inline-flex items-center gap-2 text-sm text-zinc-400 cursor-pointer">
          <input
            type="checkbox"
            data-testid="at-mini-fi"
            checked={fauteInex}
            onChange={(e) => setFauteInex(e.target.checked)}
            className="rounded border-zinc-600 bg-zinc-950 text-amber-500"
          />
          <span>Faute inexcusable reconnue (majoration jusqu'à 2x)</span>
        </label>

        {result && (
          <div
            data-testid="at-mini-result"
            className="mt-6 rounded-lg border border-amber-500/30 bg-gradient-to-br from-amber-500/5 to-transparent p-5 space-y-3"
          >
            {result.type === 'rente' ? (
              <>
                <div>
                  <p className="text-xs uppercase tracking-wider text-amber-400/80 mb-1">Rente AT annuelle estimée</p>
                  <p className="text-3xl font-light text-amber-300">
                    {result.rente.toLocaleString('fr-FR', { maximumFractionDigits: 2 })}{' '}
                    <span className="text-base text-zinc-400">€/an</span>
                  </p>
                </div>
                {result.renteFI && (
                  <div className="pt-3 border-t border-amber-500/20">
                    <p className="text-xs uppercase tracking-wider text-amber-400/80 mb-1">Avec faute inexcusable (majoration)</p>
                    <p className="text-2xl font-light text-amber-200">
                      jusqu'à {result.renteFI.toLocaleString('fr-FR', { maximumFractionDigits: 2 })}{' '}
                      <span className="text-base text-zinc-400">€/an</span>
                    </p>
                  </div>
                )}
                <p className="text-xs text-zinc-500">
                  Taux utile appliqué : <strong>{result.tauxUtile.toFixed(1)}%</strong> · Salaire annuel retenu : {result.salaireAnnuel.toLocaleString('fr-FR')} €
                </p>
              </>
            ) : (
              <>
                <p className="text-xs uppercase tracking-wider text-amber-400/80 mb-1">Capital unique estimé (IPP &lt; 10%)</p>
                <p className="text-3xl font-light text-amber-300">
                  {result.capital.toLocaleString('fr-FR', { maximumFractionDigits: 2 })}{' '}
                  <span className="text-base text-zinc-400">€ (capital)</span>
                </p>
                <p className="text-xs text-zinc-500">
                  En deçà de 10% d'IPP, indemnisation versée en capital unique selon barème CPAM.
                </p>
              </>
            )}
          </div>
        )}

        <p className="mt-5 text-xs text-zinc-500 italic flex items-start gap-2">
          <ShieldAlert className="h-4 w-4 text-amber-500/70 shrink-0 mt-0.5" />
          Résultat strictement indicatif. Le taux IPP réel est fixé par expertise médicale et peut être contesté.
        </p>
      </CardContent>
    </Card>
  );
}

function StructuredDataAT() {
  useEffect(() => {
    const breadcrumb = {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Accueil', item: 'https://strategie-expertise-sante.fr/' },
        { '@type': 'ListItem', position: 2, name: 'Simulateurs', item: 'https://strategie-expertise-sante.fr/simulateur' },
        { '@type': 'ListItem', position: 3, name: 'Rente IPP — Accident du Travail', item: PROD_URL },
      ],
    };
    const id = 'at-breadcrumb-schema';
    const existing = document.getElementById(id);
    if (existing) existing.remove();
    const s = document.createElement('script');
    s.id = id;
    s.type = 'application/ld+json';
    s.text = JSON.stringify(breadcrumb);
    document.head.appendChild(s);
    return () => {
      const el = document.getElementById(id);
      if (el) el.remove();
    };
  }, []);
  return null;
}

export default function SimulateurIPPAccidentTravailPreviewPage() {
  // noindex override (preview-only)
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
        title="Simulateur Rente IPP Accident du Travail | Calcul indemnisation 2026"
        meta={[
          { name: 'robots', content: 'noindex, nofollow' },
          {
            name: 'description',
            content: "Calculez votre rente IPP suite à un accident du travail : formule officielle, majoration faute inexcusable, capital pour taux < 10%. Estimation gratuite 2026.",
          },
        ]}
        link={[{ rel: 'canonical', href: PROD_URL }]}
      />
      <StructuredDataAT />

      <main className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="at-page">
        <section className="relative overflow-hidden border-b border-zinc-900">
          <div className="absolute inset-0 bg-gradient-to-br from-amber-500/[0.04] via-transparent to-transparent pointer-events-none" />
          <div className="relative max-w-5xl mx-auto px-5 sm:px-8 pt-16 pb-12">
            <p className="text-xs uppercase tracking-[0.2em] text-amber-400/80 mb-4">Simulateur spécialisé</p>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-light text-zinc-50 leading-[1.1] tracking-tight max-w-3xl" data-testid="at-h1">
              Simulateur rente IPP — <span className="text-amber-400">accident du travail</span>
            </h1>
            <p className="mt-5 text-base sm:text-lg text-zinc-400 max-w-2xl leading-relaxed">
              Calculez en quelques secondes le montant indicatif de votre rente AT, avec ou sans faute inexcusable
              de l'employeur, selon les barèmes légaux 2026.
            </p>
          </div>
        </section>

        <section className="max-w-5xl mx-auto px-5 sm:px-8 py-12">
          <MiniSimuAT />
        </section>

        <section className="max-w-5xl mx-auto px-5 sm:px-8 pb-12 space-y-8">
          <div className="rounded-2xl border border-zinc-900 bg-zinc-900/30 p-6 sm:p-8">
            <h2 className="text-xl sm:text-2xl font-light text-zinc-100 mb-4">Comment se calcule la rente AT en 2026 ?</h2>
            <div className="space-y-3 text-sm sm:text-base text-zinc-400 leading-relaxed">
              <p>
                La rente accident du travail repose sur deux variables : le <strong className="text-zinc-300">taux d'incapacité permanente partielle (IPP)</strong>
                fixé par le médecin-conseil de la CPAM après consolidation, et le <strong className="text-zinc-300">salaire annuel de référence</strong>
                des 12 mois précédant l'arrêt de travail.
              </p>
              <p>
                La formule officielle distingue deux fractions du taux : la part comprise entre 10 % et 50 % est divisée par
                deux, tandis que la part au-delà de 50 % est multipliée par 1,5. Cette mécanique progressive vise à amplifier
                l'indemnisation des incapacités les plus lourdes.
              </p>
              <p>
                En dessous de 10 % d'IPP, l'indemnisation prend la forme d'un <strong className="text-zinc-300">capital unique</strong>,
                calculé selon un barème CPAM réactualisé chaque année. Au-delà, la rente est versée trimestriellement et à vie.
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-6 sm:p-8">
            <div className="flex items-start gap-4">
              <Scale className="h-6 w-6 text-amber-400 shrink-0 mt-1" />
              <div>
                <h2 className="text-xl font-light text-zinc-100 mb-3">Faute inexcusable : majoration substantielle</h2>
                <p className="text-sm text-zinc-300 leading-relaxed mb-3">
                  Lorsque la <strong>faute inexcusable de l'employeur</strong> est reconnue par le pôle social du tribunal
                  judiciaire, la rente AT peut être <strong>majorée jusqu'au double</strong>. S'ajoute la réparation intégrale
                  des préjudices personnels (souffrances, préjudice esthétique, préjudice d'agrément, perte de chance professionnelle).
                </p>
                <p className="text-sm text-zinc-400 leading-relaxed">
                  La démonstration repose sur des éléments objectifs : signalements antérieurs, alertes du CSE, documents internes,
                  expertises. Le délai de prescription est de 2 ans à compter de la consolidation.
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-zinc-900 bg-zinc-900/30 p-6 sm:p-8">
            <h2 className="text-xl sm:text-2xl font-light text-zinc-100 mb-4">Comment contester un taux IPP jugé sous-évalué ?</h2>
            <div className="space-y-3 text-sm sm:text-base text-zinc-400 leading-relaxed">
              <p>
                Le taux notifié par la CPAM n'est <strong className="text-zinc-300">jamais définitif</strong>. Vous disposez de
                deux mois pour saisir la Commission Médicale de Recours Amiable (CMRA), puis le tribunal judiciaire en cas de
                désaccord persistant. Un écart de 5 points entre le taux notifié et le taux réel peut représenter plusieurs
                dizaines de milliers d'euros sur une vie.
              </p>
              <p>
                La stratégie consiste à <strong className="text-zinc-300">étayer le dossier médical</strong> par des expertises
                indépendantes, des bilans neuropsychologiques, et toute pièce démontrant l'impact fonctionnel réel sur la vie
                quotidienne et professionnelle.
              </p>
              <p>
                Notre service <strong className="text-amber-300">Dossier Express IA</strong> analyse votre dossier complet et
                identifie les points d'analyse et de préparation que les outils administratifs ne voient pas.
              </p>
            </div>
            <a
              href="/dossier-express"
              data-testid="at-cta-dossier"
              className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded-lg border border-amber-500/40 bg-amber-500/10 text-amber-300 hover:bg-amber-500/20 transition-colors text-sm font-medium"
            >
              <FileText className="h-4 w-4" /> Faire analyser mon dossier
              <ChevronRight className="h-4 w-4" />
            </a>
          </div>
        </section>

        <section className="max-w-5xl mx-auto px-5 sm:px-8 py-10 border-t border-zinc-900">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-zinc-600 shrink-0 mt-0.5" />
            <p className="text-xs text-zinc-600 italic leading-relaxed">
              Cette simulation est indicative et ne constitue pas un avis juridique opposable. Les montants réels
              dépendent du taux IPP fixé par expertise, du salaire de référence retenu par la CPAM, et de la
              revalorisation annuelle des rentes. Pour une analyse personnalisée, consultez notre service Dossier Express.
            </p>
          </div>
        </section>
      </main>
    </>
  );
}
