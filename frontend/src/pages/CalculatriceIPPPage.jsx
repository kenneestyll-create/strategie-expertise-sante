import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { toast } from 'sonner';
import axios from 'axios';
import { SEO } from '@/components/SEO';
import {
  Calculator,
  AlertTriangle,
  ArrowRight,
  Info,
  CalendarPlus,
  TrendingUp,
  Coins,
  Share2,
  Mail,
  MessageSquare,
  Phone,
  Copy,
  Check,
  Eye,
  Briefcase,
  TrendingDown,
  ChevronRight
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Barème AT/MP - capital forfaitaire pour taux < 10% (valeurs 2024 indicatives)
const CAPITAL_BAREME = {
  1: 468, 2: 760, 3: 1111, 4: 1754, 5: 2222,
  6: 2750, 7: 3336, 8: 3982, 9: 4688
};

const calculateIPP = (taux, salaire) => {
  if (taux <= 0 || taux > 100) return null;

  if (taux < 10) {
    // Capital forfaitaire
    const capital = CAPITAL_BAREME[taux] || 0;
    return {
      type: 'capital',
      montant: capital,
      description: `Indemnité en capital (versement unique) pour un taux de ${taux}%`,
      detail: `Pour les taux inférieurs à 10%, l'indemnisation se fait sous forme de capital forfaitaire versé en une seule fois.`
    };
  }

  // Rente viagère pour taux >= 10%
  // Le taux utile = (taux/2) pour la partie <= 50% + taux réel pour la partie > 50%
  let tauxUtile;
  if (taux <= 50) {
    tauxUtile = taux / 2;
  } else {
    tauxUtile = 25 + (taux - 50) * 1.5;
  }

  // Salaire de référence : plafonné et plancher
  const salaireRef = Math.max(salaire, 19744); // Salaire minimum de référence
  const renteAnnuelle = (salaireRef * tauxUtile) / 100;
  const renteMensuelle = renteAnnuelle / 12;

  return {
    type: 'rente',
    montantAnnuel: Math.round(renteAnnuelle * 100) / 100,
    montantMensuel: Math.round(renteMensuelle * 100) / 100,
    tauxUtile: Math.round(tauxUtile * 100) / 100,
    description: `Rente viagère pour un taux d'IPP de ${taux}%`,
    detail: `Le taux utile est calculé selon le barème AT/MP : la moitié du taux pour la partie jusqu'à 50%, puis 1,5x pour la partie au-delà.`
  };
};

export const CalculatriceIPPPage = () => {
  const [searchParams] = useSearchParams();
  const [taux, setTaux] = useState(15);
  const [salaire, setSalaire] = useState(25000);
  const [result, setResult] = useState(null);
  const [calculated, setCalculated] = useState(false);
  const [copied, setCopied] = useState(false);
  const [weeklyCount, setWeeklyCount] = useState(0);

  useEffect(() => {
    axios.get(`${API}/calculator/count`).then(r => setWeeklyCount(r.data.count)).catch(() => {});
  }, []);

  useEffect(() => {
    const t = searchParams.get('t');
    const s = searchParams.get('s');
    if (t) {
      const parsedT = parseInt(t, 10);
      const parsedS = s ? parseInt(s, 10) : 25000;
      if (parsedT >= 1 && parsedT <= 100) {
        setTaux(parsedT);
        setSalaire(parsedS);
        const res = calculateIPP(parsedT, parsedS);
        setResult(res);
        setCalculated(true);
      }
    }
  }, [searchParams]);

  const handleCalculate = () => {
    const res = calculateIPP(taux, salaire);
    setResult(res);
    setCalculated(true);
    axios.post(`${API}/calculator/track`, { type: 'ipp' }).then(() => {
      setWeeklyCount(prev => prev + 1);
    }).catch(() => {});
  };

  const getShareUrl = () => {
    const base = `${window.location.origin}/calculatrice-ipp`;
    const params = new URLSearchParams({ t: taux });
    if (taux >= 10) params.set('s', salaire);
    return `${base}?${params.toString()}`;
  };

  const getShareText = () => {
    if (!result) return '';
    if (result.type === 'capital') {
      return `Calculatrice IPP - Taux ${taux}% : indemnité en capital de ${result.montant.toLocaleString('fr-FR')} €. Estimez la vôtre :`;
    }
    return `Calculatrice IPP - Taux ${taux}% : rente estimée de ${result.montantMensuel.toLocaleString('fr-FR')} €/mois. Estimez la vôtre :`;
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(getShareUrl());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleWhatsApp = () => {
    window.open(`https://wa.me/?text=${encodeURIComponent(getShareText() + ' ' + getShareUrl())}`, '_blank');
  };

  const handleSMS = () => {
    window.open(`sms:?body=${encodeURIComponent(getShareText() + ' ' + getShareUrl())}`, '_blank');
  };

  const handleEmail = () => {
    const subject = encodeURIComponent('Mon estimation IPP - Stratégie & Expertise Santé');
    const body = encodeURIComponent(getShareText() + '\n\n' + getShareUrl());
    window.open(`mailto:?subject=${subject}&body=${body}`, '_blank');
  };

  return (
    <main className="page-transition pt-20">
      <SEO title="Calculatrice IPP" description="Estimez votre taux d'Incapacité Permanente Partielle (IPP) et le montant de votre indemnisation." path="/calculatrice-ipp" />
      {/* Hero */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Outil de simulation</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="ipp-calculator-title">
              Calculatrice de taux IPP
            </h1>
            <p className="text-lg text-muted-foreground">
              Estimez votre indemnisation potentielle selon le barème AT/MP en fonction
              de votre taux d'Incapacité Permanente Partielle.
            </p>
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="max-w-3xl mx-auto">
          {/* Disclaimer */}
          <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl mb-8" data-testid="ipp-disclaimer">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-amber-800">
              <strong>Résultat indicatif uniquement</strong> — ne constitue pas un conseil juridique.
              Les montants réels dépendent de nombreux facteurs (consolidation, barème en vigueur, situation personnelle).
              Consultez un professionnel pour une évaluation précise.
            </p>
          </div>

          {/* Calculator Card */}
          <Card className="border-border" data-testid="ipp-calculator-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="w-5 h-5 text-accent" />
                Simulation d'indemnisation IPP
              </CardTitle>
              <CardDescription>
                Renseignez votre taux d'IPP et votre salaire annuel de référence.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Taux IPP */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label className="text-base font-medium">Taux d'IPP</Label>
                  <span className="text-2xl font-bold text-accent" data-testid="ipp-taux-display">{taux}%</span>
                </div>
                <Slider
                  value={[taux]}
                  onValueChange={(v) => { setTaux(v[0]); setCalculated(false); }}
                  min={1}
                  max={100}
                  step={1}
                  className="w-full"
                  data-testid="ipp-taux-slider"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>1%</span>
                  <span>10% (seuil rente)</span>
                  <span>50%</span>
                  <span>100%</span>
                </div>
              </div>

              {/* Salaire (visible only if taux >= 10) */}
              {taux >= 10 && (
                <div className="space-y-2" data-testid="ipp-salaire-section">
                  <Label htmlFor="ipp-salaire" className="text-base font-medium">
                    Salaire annuel brut de référence (€)
                  </Label>
                  <Input
                    id="ipp-salaire"
                    type="number"
                    value={salaire}
                    onChange={(e) => { setSalaire(Number(e.target.value)); setCalculated(false); }}
                    placeholder="25000"
                    data-testid="ipp-salaire-input"
                  />
                  <p className="text-xs text-muted-foreground">
                    Salaire des 12 derniers mois précédant l'arrêt. Minimum de référence : 19 744 €.
                  </p>
                </div>
              )}

              <Button
                className="w-full rounded-lg gap-2"
                onClick={handleCalculate}
                data-testid="ipp-calculate-button"
              >
                <Calculator className="w-4 h-4" />
                Calculer l'estimation
              </Button>

              {/* Results */}
              {calculated && result && (
                <div className="mt-6 p-6 bg-muted/30 rounded-xl border border-border space-y-4" data-testid="ipp-result">
                  <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Info className="w-4 h-4" />
                    {result.description}
                  </div>

                  {result.type === 'capital' ? (
                    <div className="text-center py-4">
                      <p className="text-sm text-muted-foreground mb-2">Indemnité en capital (versement unique)</p>
                      <p className="text-4xl font-bold text-foreground" data-testid="ipp-result-amount">
                        {result.montant.toLocaleString('fr-FR')} €
                      </p>
                    </div>
                  ) : (
                    <div className="grid sm:grid-cols-2 gap-4">
                      <div className="text-center p-4 bg-background rounded-lg">
                        <p className="text-sm text-muted-foreground mb-1">Rente annuelle estimée</p>
                        <p className="text-3xl font-bold text-foreground" data-testid="ipp-result-annual">
                          {result.montantAnnuel.toLocaleString('fr-FR')} €
                        </p>
                      </div>
                      <div className="text-center p-4 bg-background rounded-lg">
                        <p className="text-sm text-muted-foreground mb-1">Soit par mois</p>
                        <p className="text-3xl font-bold text-accent" data-testid="ipp-result-monthly">
                          {result.montantMensuel.toLocaleString('fr-FR')} €
                        </p>
                      </div>
                    </div>
                  )}

                  <p className="text-sm text-muted-foreground">{result.detail}</p>

                  {result.type === 'rente' && (
                    <div className="text-xs text-muted-foreground bg-muted/50 p-3 rounded-lg">
                      <p className="font-medium mb-1">Détail du calcul :</p>
                      <p>Taux IPP : {taux}% → Taux utile : {result.tauxUtile}%</p>
                      <p>Salaire de référence : {salaire.toLocaleString('fr-FR')} €</p>
                      <p>Rente = {salaire.toLocaleString('fr-FR')} × {result.tauxUtile}% = {result.montantAnnuel.toLocaleString('fr-FR')} €/an</p>
                    </div>
                  )}

                  {/* Share buttons */}
                  <div className="pt-4 border-t border-border/50">
                    <p className="text-sm font-medium text-muted-foreground flex items-center gap-2 mb-3">
                      <Share2 className="w-4 h-4" /> Partager mon estimation
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={handleWhatsApp}
                        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-[#25D366]/10 text-[#25D366] hover:bg-[#25D366]/20 transition-colors"
                        data-testid="ipp-share-whatsapp"
                      >
                        <MessageSquare className="w-4 h-4" /> WhatsApp
                      </button>
                      <button
                        onClick={handleSMS}
                        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-blue-500/10 text-blue-600 hover:bg-blue-500/20 transition-colors"
                        data-testid="ipp-share-sms"
                      >
                        <Phone className="w-4 h-4" /> SMS
                      </button>
                      <button
                        onClick={handleEmail}
                        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-accent/10 text-accent hover:bg-accent/20 transition-colors"
                        data-testid="ipp-share-email"
                      >
                        <Mail className="w-4 h-4" /> Email
                      </button>
                      <button
                        onClick={handleCopyLink}
                        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-muted hover:bg-muted/80 transition-colors"
                        data-testid="ipp-share-copy"
                      >
                        {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                        {copied ? 'Copié !' : 'Copier le lien'}
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Weekly counter */}
          {weeklyCount > 0 && (
            <div className="flex items-center justify-center gap-2 mt-6 py-3 px-5 bg-accent/5 border border-accent/15 rounded-full w-fit mx-auto" data-testid="ipp-weekly-counter">
              <Eye className="w-4 h-4 text-accent" />
              <span className="text-sm font-medium text-muted-foreground">
                <strong className="text-foreground">{weeklyCount}</strong> personne{weeklyCount > 1 ? 's' : ''} {weeklyCount > 1 ? 'ont' : 'a'} estimé leurs droits cette semaine
              </span>
            </div>
          )}

          {/* Info Cards */}
          <div className="grid sm:grid-cols-2 gap-4 mt-8">
            <div className="p-5 bg-card border border-border rounded-xl">
              <Coins className="w-6 h-6 text-accent mb-3" strokeWidth={1.5} />
              <h3 className="font-semibold mb-2">Taux &lt; 10%</h3>
              <p className="text-sm text-muted-foreground">
                L'indemnisation se fait sous forme de <strong>capital forfaitaire</strong> versé en une seule fois.
                Le montant est fixé par décret selon un barème officiel.
              </p>
            </div>
            <div className="p-5 bg-card border border-border rounded-xl">
              <TrendingUp className="w-6 h-6 text-accent mb-3" strokeWidth={1.5} />
              <h3 className="font-semibold mb-2">Taux ≥ 10%</h3>
              <p className="text-sm text-muted-foreground">
                L'indemnisation prend la forme d'une <strong>rente viagère</strong> versée trimestriellement.
                Elle est calculée à partir du salaire et d'un taux utile.
              </p>
            </div>
          </div>

          {/* IP & PGPF Encarts explicatifs */}
          <div className="grid sm:grid-cols-2 gap-4 mt-6">
            <div className="p-5 bg-card border border-border rounded-xl" data-testid="ipp-encart-ip">
              <Briefcase className="w-6 h-6 text-accent mb-3" strokeWidth={1.5} />
              <h3 className="font-semibold mb-2">Incidence Professionnelle (IP)</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Au-dela du taux d'IPP, l'<strong>incidence professionnelle</strong> indemnise les consequences sur votre carriere : penibilite accrue, devalorisation sur le marche du travail, necessite de reconversion.
              </p>
              <ul className="space-y-1 mb-3">
                {["Penibilite accrue au poste", "Perte d'opportunites de carriere", "Devalorisation sur le marche de l'emploi", "Necessite de reconversion professionnelle"].map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                    <ChevronRight className="w-3 h-3 mt-0.5 text-accent flex-shrink-0" /> {item}
                  </li>
                ))}
              </ul>
              <Link to="/ressources" className="text-xs text-accent hover:underline font-medium">
                En savoir plus sur l'IP →
              </Link>
            </div>
            <div className="p-5 bg-card border border-border rounded-xl" data-testid="ipp-encart-pgpf">
              <TrendingDown className="w-6 h-6 text-accent mb-3" strokeWidth={1.5} />
              <h3 className="font-semibold mb-2">Perte de Gains Futurs (PGPF)</h3>
              <p className="text-sm text-muted-foreground mb-3">
                La <strong>PGPF</strong> compense la perte definitive de revenus apres consolidation. Elle se calcule par capitalisation de la perte annuelle selon un bareme officiel.
              </p>
              <ul className="space-y-1 mb-3">
                {["Projection de carriere sans accident", "Impact du handicap sur les revenus", "Capitalisation selon bareme Gazette du Palais", "Distinction avec la perte actuelle (PGPA)"].map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                    <ChevronRight className="w-3 h-3 mt-0.5 text-accent flex-shrink-0" /> {item}
                  </li>
                ))}
              </ul>
              <Link to="/ressources" className="text-xs text-accent hover:underline font-medium">
                En savoir plus sur la PGPF →
              </Link>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 mt-4" data-testid="ipp-ip-pgpf-note">
            <Info className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-amber-800 dark:text-amber-300 leading-relaxed">
              <strong>A savoir :</strong> Votre taux d'IPP peut ouvrir droit a une indemnisation complementaire au titre de l'incidence professionnelle et/ou de la PGPF. Ces postes de prejudice sont evaluables par un professionnel du droit ou via notre outil StrategiIA.
            </p>
          </div>

          {/* CTA */}
          <div className="mt-12 p-8 bg-foreground text-primary-foreground rounded-2xl text-center" data-testid="ipp-cta">
            <h2 className="text-2xl font-semibold mb-3">
              Besoin d'un accompagnement personnalisé ?
            </h2>
            <p className="text-primary-foreground/70 mb-6 max-w-lg mx-auto">
              Ce simulateur donne une estimation indicative. Pour une analyse précise de votre situation
              et un accompagnement adapté, prenez rendez-vous.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/agenda">
                <Button size="lg" className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground">
                  <CalendarPlus className="w-4 h-4" />
                  Prendre rendez-vous
                </Button>
              </Link>
              <Link to="/contact">
                <Button size="lg" variant="outline" className="rounded-full px-8 gap-2 border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/10">
                  Nous contacter
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};
