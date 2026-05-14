import { useState, useMemo, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Calculator, ShieldAlert, AlertCircle, FileText, Stethoscope, ChevronRight } from 'lucide-react';

const PROD_URL = 'https://strategie-expertise-sante.fr/simulateur-rente-maladie-professionnelle';

function MiniSimuMP() {
  const [taux, setTaux] = useState('');
  const [salaire, setSalaire] = useState('');
  const [salaireType, setSalaireType] = useState('annual');
  const [tableau, setTableau] = useState('regime-general');

  const result = useMemo(() => {
    const t = parseFloat(taux);
    const s = parseFloat(salaire);
    if (isNaN(t) || isNaN(s) || t < 0 || s < 0) return null;

    const salaireAnnuel = salaireType === 'monthly' ? s * 12 : s;

    if (t >= 10) {
      const tauxUtile = t <= 50 ? t / 2 : 25 + (t - 50) * 1.5;
      const rente = salaireAnnuel * (tauxUtile / 100);
      return {
        type: 'rente',
        rente,
        tauxUtile,
        salaireAnnuel,
      };
    }
    const capital = salaireAnnuel * (t / 100) * 0.4;
    return {
      type: 'capital',
      capital,
      salaireAnnuel,
    };
  }, [taux, salaire, salaireType]);

  return (
    <Card data-testid="mp-mini-simu" className="bg-zinc-900/70 border-amber-500/20 backdrop-blur-sm">
      <CardContent className="p-6 sm:p-8">
        <div className="flex items-center gap-3 mb-5">
          <div className="h-10 w-10 rounded-xl bg-amber-500/10 border border-amber-500/30 grid place-items-center">
            <Calculator className="h-5 w-5 text-amber-400" />
          </div>
          <div>
            <h2 className="text-lg sm:text-xl font-semibold text-zinc-100">Simulateur Rente IPP — Maladie Professionnelle</h2>
            <p className="text-sm text-zinc-400">Calcul selon les tableaux du régime général et complémentaire</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="mp-taux" className="text-zinc-300 text-sm">Taux IPP (%)</Label>
            <Input
              id="mp-taux"
              data-testid="mp-mini-taux"
              type="number"
              min="0"
              max="100"
              placeholder="Ex. 30"
              value={taux}
              onChange={(e) => setTaux(e.target.value)}
              className="mt-1 bg-zinc-950 border-zinc-700 text-zinc-100"
            />
          </div>
          <div>
            <Label htmlFor="mp-salaire" className="text-zinc-300 text-sm">Salaire de référence (€)</Label>
            <Input
              id="mp-salaire"
              data-testid="mp-mini-salaire"
              type="number"
              min="0"
              placeholder="Ex. 28 000"
              value={salaire}
              onChange={(e) => setSalaire(e.target.value)}
              className="mt-1 bg-zinc-950 border-zinc-700 text-zinc-100"
            />
          </div>
          <div>
            <Label htmlFor="mp-tableau" className="text-zinc-300 text-sm">Régime</Label>
            <select
              id="mp-tableau"
              data-testid="mp-mini-tableau"
              value={tableau}
              onChange={(e) => setTableau(e.target.value)}
              className="mt-1 w-full h-10 rounded-md bg-zinc-950 border border-zinc-700 text-zinc-100 px-3 text-sm focus:outline-none focus:border-amber-500/60"
            >
              <option value="regime-general">Régime général (RG)</option>
              <option value="regime-agricole">Régime agricole (RA)</option>
              <option value="hors-tableau">Hors tableau (CRRMP)</option>
            </select>
          </div>
        </div>

        <div className="mt-3 flex items-center gap-2 text-xs text-zinc-500">
          <span className="text-zinc-400">Période :</span>
          <button
            type="button"
            onClick={() => setSalaireType('annual')}
            className={`px-2 py-0.5 rounded ${salaireType === 'annual' ? 'bg-amber-500/20 text-amber-300' : 'text-zinc-500 hover:text-zinc-300'}`}
          >
            Annuel
          </button>
          <button
            type="button"
            onClick={() => setSalaireType('monthly')}
            className={`px-2 py-0.5 rounded ${salaireType === 'monthly' ? 'bg-amber-500/20 text-amber-300' : 'text-zinc-500 hover:text-zinc-300'}`}
          >
            Mensuel
          </button>
        </div>

        {result && (
          <div
            data-testid="mp-mini-result"
            className="mt-6 rounded-lg border border-amber-500/30 bg-gradient-to-br from-amber-500/5 to-transparent p-5 space-y-2"
          >
            {result.type === 'rente' ? (
              <>
                <p className="text-xs uppercase tracking-wider text-amber-400/80 mb-1">Rente MP annuelle estimée</p>
                <p className="text-3xl font-light text-amber-300">
                  {result.rente.toLocaleString('fr-FR', { maximumFractionDigits: 2 })}{' '}
                  <span className="text-base text-zinc-400">€/an</span>
                </p>
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
              </>
            )}
            {tableau === 'hors-tableau' && (
              <p className="text-xs text-amber-300/80 italic mt-2">
                Reconnaissance hors tableau : taux d'IPP prévisible ≥ 25% requis pour saisine du CRRMP.
              </p>
            )}
          </div>
        )}

        <p className="mt-5 text-xs text-zinc-500 italic flex items-start gap-2">
          <ShieldAlert className="h-4 w-4 text-amber-500/70 shrink-0 mt-0.5" />
          Résultat strictement indicatif. La reconnaissance MP et le taux IPP sont fixés par procédures
          médico-administratives spécifiques.
        </p>
      </CardContent>
    </Card>
  );
}

function StructuredDataMP() {
  useEffect(() => {
    const breadcrumb = {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Accueil', item: 'https://strategie-expertise-sante.fr/' },
        { '@type': 'ListItem', position: 2, name: 'Simulateurs', item: 'https://strategie-expertise-sante.fr/simulateur' },
        { '@type': 'ListItem', position: 3, name: 'Rente — Maladie Professionnelle', item: PROD_URL },
      ],
    };
    const id = 'mp-breadcrumb-schema';
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

export default function SimulateurMaladieProfessionnellePreviewPage() {
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
        title="Simulateur Rente Maladie Professionnelle | Calcul indemnisation 2026"
        meta={[
          { name: 'robots', content: 'noindex, nofollow' },
          {
            name: 'description',
            content: "Calculez votre rente maladie professionnelle 2026 : tableaux régime général, hors-tableau CRRMP, capital pour IPP < 10%. Reconnaissance, prescription, recours.",
          },
        ]}
        link={[{ rel: 'canonical', href: PROD_URL }]}
      />
      <StructuredDataMP />

      <main className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="mp-page">
        <section className="relative overflow-hidden border-b border-zinc-900">
          <div className="absolute inset-0 bg-gradient-to-br from-amber-500/[0.04] via-transparent to-transparent pointer-events-none" />
          <div className="relative max-w-5xl mx-auto px-5 sm:px-8 pt-16 pb-12">
            <p className="text-xs uppercase tracking-[0.2em] text-amber-400/80 mb-4">Simulateur spécialisé</p>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-light text-zinc-50 leading-[1.1] tracking-tight max-w-3xl" data-testid="mp-h1">
              Simulateur rente — <span className="text-amber-400">maladie professionnelle</span>
            </h1>
            <p className="mt-5 text-base sm:text-lg text-zinc-400 max-w-2xl leading-relaxed">
              Évaluez le montant indicatif de votre rente MP selon votre taux IPP, votre régime et votre salaire de
              référence. Tableaux RG, RA et procédures hors-tableau CRRMP.
            </p>
          </div>
        </section>

        <section className="max-w-5xl mx-auto px-5 sm:px-8 py-12">
          <MiniSimuMP />
        </section>

        <section className="max-w-5xl mx-auto px-5 sm:px-8 pb-12 space-y-8">
          <div className="rounded-2xl border border-zinc-900 bg-zinc-900/30 p-6 sm:p-8">
            <h2 className="text-xl sm:text-2xl font-light text-zinc-100 mb-4">Reconnaissance d'une maladie professionnelle : 3 voies possibles</h2>
            <div className="space-y-3 text-sm sm:text-base text-zinc-400 leading-relaxed">
              <p>
                Une maladie est reconnue comme professionnelle si elle figure dans un <strong className="text-zinc-300">tableau du régime général ou agricole</strong>
                et que vous remplissez les conditions médicales, administratives et d'exposition. Les tableaux les plus fréquents :
                RG 57 (TMS membres supérieurs), RG 30 (amiante), RG 98 (rachis lombaire et charges lourdes), RG 79 (lésions du ménisque).
              </p>
              <p>
                Si votre pathologie n'est pas inscrite dans un tableau, vous pouvez saisir le
                <strong className="text-zinc-300"> Comité Régional de Reconnaissance des Maladies Professionnelles (CRRMP)</strong>,
                à condition que le taux d'IPP prévisible soit d'au moins 25 % et que le lien direct avec l'activité professionnelle
                soit démontré par expertise.
              </p>
              <p>
                La <strong className="text-zinc-300">date de prescription</strong> court à compter de la connaissance du lien
                entre la pathologie et le travail — un point souvent décisif qui mérite une analyse précise du dossier médical.
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-zinc-900 bg-zinc-900/30 p-6 sm:p-8">
            <h2 className="text-xl sm:text-2xl font-light text-zinc-100 mb-4">Calcul de la rente : règles identiques à l'AT</h2>
            <div className="space-y-3 text-sm sm:text-base text-zinc-400 leading-relaxed">
              <p>
                Une fois la MP reconnue et le taux IPP fixé, le calcul de la rente suit les mêmes règles que pour un accident du
                travail : salaire annuel de référence multiplié par le <strong className="text-zinc-300">taux utile</strong>
                (taux/2 jusqu'à 50%, puis (taux-50)×1,5 + 25 au-delà). En dessous de 10% d'IPP, capital unique.
              </p>
              <p>
                La <strong className="text-zinc-300">faute inexcusable de l'employeur</strong> s'applique également aux MP et
                permet d'obtenir une majoration de rente et la réparation intégrale des préjudices extra-patrimoniaux
                (souffrances, agrément, préjudice professionnel).
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-6 sm:p-8">
            <div className="flex items-start gap-4">
              <Stethoscope className="h-6 w-6 text-amber-400 shrink-0 mt-1" />
              <div>
                <h2 className="text-xl font-light text-zinc-100 mb-3">Contestation du taux IPP en MP</h2>
                <p className="text-sm text-zinc-300 leading-relaxed mb-3">
                  Comme en AT, le taux IPP fixé par la CPAM peut être contesté devant la <strong>Commission Médicale de Recours
                  Amiable (CMRA)</strong> dans un délai de 2 mois. Une expertise médicale indépendante et un dossier
                  argumentaire solide sont les leviers de succès.
                </p>
                <p className="text-sm text-zinc-400 leading-relaxed">
                  En MP, la difficulté supplémentaire réside dans la <strong>quantification des séquelles évolutives</strong>
                  (TMS, cancers professionnels, pathologies respiratoires) qui appellent une expertise spécialisée.
                </p>
              </div>
            </div>
            <a
              href="/dossier-express"
              data-testid="mp-cta-dossier"
              className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded-lg border border-amber-500/40 bg-amber-500/10 text-amber-300 hover:bg-amber-500/20 transition-colors text-sm font-medium"
            >
              <FileText className="h-4 w-4" /> Faire analyser mon dossier MP
              <ChevronRight className="h-4 w-4" />
            </a>
          </div>
        </section>

        <section className="max-w-5xl mx-auto px-5 sm:px-8 py-10 border-t border-zinc-900">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-zinc-600 shrink-0 mt-0.5" />
            <p className="text-xs text-zinc-600 italic leading-relaxed">
              Cette simulation est indicative et ne constitue pas un avis juridique opposable. La reconnaissance MP est
              soumise à des procédures administratives spécifiques (CPAM, CRRMP) et le taux IPP est fixé par expertise médicale.
            </p>
          </div>
        </section>
      </main>
    </>
  );
}
