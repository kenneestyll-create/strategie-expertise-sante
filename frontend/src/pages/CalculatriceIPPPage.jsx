import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { toast } from 'sonner';
import {
  Calculator,
  AlertTriangle,
  ArrowRight,
  Info,
  CalendarPlus,
  TrendingUp,
  Coins
} from 'lucide-react';

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
  const [taux, setTaux] = useState(15);
  const [salaire, setSalaire] = useState(25000);
  const [result, setResult] = useState(null);
  const [calculated, setCalculated] = useState(false);

  const handleCalculate = () => {
    const res = calculateIPP(taux, salaire);
    setResult(res);
    setCalculated(true);
  };

  return (
    <main className="page-transition pt-20">
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
                </div>
              )}
            </CardContent>
          </Card>

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
