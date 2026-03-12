import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Calculator,
  AlertTriangle,
  ArrowRight,
  Info,
  CalendarPlus,
  Users,
  Heart
} from 'lucide-react';

// AAH 2024-2025 : montant max = 971,37 €/mois
const AAH_MAX = 971.37;
// Plafond de ressources annuel pour une personne seule
const PLAFOND_SEUL = 11_656;
// Plafond pour couple
const PLAFOND_COUPLE = 21_098;
// Majoration par enfant à charge
const MAJORATION_ENFANT = 5828;

const calculateAAH = (tauxInvalidite, situationFamiliale, revenus, enfants) => {
  // Éligibilité : taux >= 80% ou entre 50 et 79% avec restriction substantielle
  if (tauxInvalidite < 50) {
    return {
      eligible: false,
      montant: 0,
      message: "Le taux d'invalidité minimum pour bénéficier de l'AAH est de 50%.",
      detail: "L'AAH est attribuée aux personnes ayant un taux d'incapacité d'au moins 80%, ou entre 50% et 79% avec une restriction substantielle et durable d'accès à l'emploi reconnue par la CDAPH."
    };
  }

  const isCouple = situationFamiliale === 'couple';
  const plafond = (isCouple ? PLAFOND_COUPLE : PLAFOND_SEUL) + (enfants * MAJORATION_ENFANT);
  const revenusAnnuels = revenus * 12;

  if (revenusAnnuels >= plafond) {
    return {
      eligible: false,
      montant: 0,
      message: "Vos revenus dépassent le plafond de ressources.",
      detail: `Plafond annuel pour votre situation : ${plafond.toLocaleString('fr-FR')} € (soit ${Math.round(plafond / 12).toLocaleString('fr-FR')} €/mois). Vos revenus annuels déclarés : ${revenusAnnuels.toLocaleString('fr-FR')} €.`,
      plafond
    };
  }

  // Calcul du montant
  let montantMensuel;
  if (revenusAnnuels === 0) {
    montantMensuel = AAH_MAX;
  } else {
    // AAH différentielle = (plafond - revenus) / 12, plafonné au max
    const aahDifferentielle = (plafond - revenusAnnuels) / 12;
    montantMensuel = Math.min(aahDifferentielle, AAH_MAX);
  }

  montantMensuel = Math.round(montantMensuel * 100) / 100;

  const isTauxPlein = tauxInvalidite >= 80;

  return {
    eligible: true,
    montant: montantMensuel,
    montantAnnuel: Math.round(montantMensuel * 12 * 100) / 100,
    message: `Estimation de votre AAH mensuelle`,
    detail: isTauxPlein
      ? `Avec un taux d'incapacité ≥ 80%, vous pouvez bénéficier de l'AAH sans restriction de durée. Le montant est calculé en fonction de vos ressources.`
      : `Avec un taux entre 50% et 79%, l'AAH est attribuée pour une période de 1 à 5 ans, sous réserve d'une restriction substantielle d'accès à l'emploi reconnue par la CDAPH.`,
    plafond,
    isTauxPlein
  };
};

export const CalculatriceAAHPage = () => {
  const [tauxInvalidite, setTauxInvalidite] = useState(80);
  const [situationFamiliale, setSituationFamiliale] = useState('seul');
  const [revenus, setRevenus] = useState(0);
  const [enfants, setEnfants] = useState(0);
  const [result, setResult] = useState(null);
  const [calculated, setCalculated] = useState(false);

  const handleCalculate = () => {
    const res = calculateAAH(tauxInvalidite, situationFamiliale, revenus, enfants);
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
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="aah-calculator-title">
              Calculatrice AAH
            </h1>
            <p className="text-lg text-muted-foreground">
              Estimez le montant de votre Allocation aux Adultes Handicapés (AAH)
              en fonction de votre taux d'invalidité, vos revenus et votre situation familiale.
            </p>
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="max-w-3xl mx-auto">
          {/* Disclaimer */}
          <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl mb-8" data-testid="aah-disclaimer">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-amber-800">
              <strong>Résultat indicatif uniquement</strong> — ne constitue pas un conseil juridique.
              L'attribution de l'AAH dépend de la décision de la CDAPH et de votre situation réelle.
              Les montants sont basés sur le barème en vigueur (AAH max : {AAH_MAX} €/mois).
            </p>
          </div>

          {/* Calculator Card */}
          <Card className="border-border" data-testid="aah-calculator-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="w-5 h-5 text-accent" />
                Simulation de l'AAH
              </CardTitle>
              <CardDescription>
                Renseignez votre situation pour estimer votre allocation mensuelle.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Taux invalidité */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label className="text-base font-medium">Taux d'invalidité</Label>
                  <span className="text-2xl font-bold text-accent" data-testid="aah-taux-display">{tauxInvalidite}%</span>
                </div>
                <Slider
                  value={[tauxInvalidite]}
                  onValueChange={(v) => { setTauxInvalidite(v[0]); setCalculated(false); }}
                  min={0}
                  max={100}
                  step={1}
                  data-testid="aah-taux-slider"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>0%</span>
                  <span className={tauxInvalidite >= 50 && tauxInvalidite < 80 ? 'text-amber-600 font-medium' : ''}>50% (seuil AAH)</span>
                  <span className={tauxInvalidite >= 80 ? 'text-green-600 font-medium' : ''}>80% (taux plein)</span>
                  <span>100%</span>
                </div>
              </div>

              {/* Situation familiale */}
              <div className="space-y-2">
                <Label className="text-base font-medium">Situation familiale</Label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => { setSituationFamiliale('seul'); setCalculated(false); }}
                    className={`flex items-center gap-2 p-3 rounded-lg border text-sm font-medium transition-all
                      ${situationFamiliale === 'seul' ? 'border-accent bg-accent/10 text-accent' : 'border-border hover:border-accent/50'}`}
                    data-testid="situation-seul"
                  >
                    <Users className="w-4 h-4" /> Personne seule
                  </button>
                  <button
                    type="button"
                    onClick={() => { setSituationFamiliale('couple'); setCalculated(false); }}
                    className={`flex items-center gap-2 p-3 rounded-lg border text-sm font-medium transition-all
                      ${situationFamiliale === 'couple' ? 'border-accent bg-accent/10 text-accent' : 'border-border hover:border-accent/50'}`}
                    data-testid="situation-couple"
                  >
                    <Heart className="w-4 h-4" /> En couple
                  </button>
                </div>
              </div>

              {/* Enfants */}
              <div className="space-y-2">
                <Label htmlFor="aah-enfants" className="text-base font-medium">Enfants à charge</Label>
                <Select value={String(enfants)} onValueChange={(v) => { setEnfants(Number(v)); setCalculated(false); }}>
                  <SelectTrigger data-testid="aah-enfants-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[0, 1, 2, 3, 4, 5].map(n => (
                      <SelectItem key={n} value={String(n)}>{n} enfant{n > 1 ? 's' : ''}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Revenus */}
              <div className="space-y-2">
                <Label htmlFor="aah-revenus" className="text-base font-medium">Revenus mensuels nets (€)</Label>
                <Input
                  id="aah-revenus"
                  type="number"
                  value={revenus}
                  onChange={(e) => { setRevenus(Number(e.target.value)); setCalculated(false); }}
                  placeholder="0"
                  min={0}
                  data-testid="aah-revenus-input"
                />
                <p className="text-xs text-muted-foreground">
                  Revenus d'activité ou pensions perçus. Mettez 0 si vous n'avez aucun revenu.
                </p>
              </div>

              <Button
                className="w-full rounded-lg gap-2"
                onClick={handleCalculate}
                data-testid="aah-calculate-button"
              >
                <Calculator className="w-4 h-4" />
                Calculer l'estimation
              </Button>

              {/* Results */}
              {calculated && result && (
                <div className={`mt-6 p-6 rounded-xl border space-y-4 ${result.eligible ? 'bg-green-50 border-green-200' : 'bg-muted/30 border-border'}`} data-testid="aah-result">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <Info className="w-4 h-4 text-muted-foreground" />
                    <span>{result.message}</span>
                  </div>

                  {result.eligible ? (
                    <>
                      <div className="grid sm:grid-cols-2 gap-4">
                        <div className="text-center p-4 bg-background rounded-lg">
                          <p className="text-sm text-muted-foreground mb-1">AAH mensuelle estimée</p>
                          <p className="text-4xl font-bold text-foreground" data-testid="aah-result-monthly">
                            {result.montant.toLocaleString('fr-FR')} €
                          </p>
                        </div>
                        <div className="text-center p-4 bg-background rounded-lg">
                          <p className="text-sm text-muted-foreground mb-1">Soit par an</p>
                          <p className="text-3xl font-bold text-accent" data-testid="aah-result-annual">
                            {result.montantAnnuel.toLocaleString('fr-FR')} €
                          </p>
                        </div>
                      </div>

                      <p className="text-sm text-muted-foreground">{result.detail}</p>

                      <div className="text-xs text-muted-foreground bg-background p-3 rounded-lg">
                        <p className="font-medium mb-1">Détail :</p>
                        <p>Taux d'invalidité : {tauxInvalidite}% {result.isTauxPlein ? '(taux plein ≥ 80%)' : '(50-79%, sous conditions)'}</p>
                        <p>Plafond de ressources annuel : {result.plafond?.toLocaleString('fr-FR')} € ({situationFamiliale === 'couple' ? 'couple' : 'personne seule'}{enfants > 0 ? ` + ${enfants} enfant${enfants > 1 ? 's' : ''}` : ''})</p>
                        <p>Revenus déclarés : {(revenus * 12).toLocaleString('fr-FR')} €/an</p>
                        <p>AAH max : {AAH_MAX} €/mois</p>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-4">
                      <p className="text-sm text-muted-foreground">{result.detail}</p>
                      {result.plafond && (
                        <p className="text-xs text-muted-foreground mt-2">
                          Plafond : {result.plafond.toLocaleString('fr-FR')} €/an — Vos revenus : {(revenus * 12).toLocaleString('fr-FR')} €/an
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Info Cards */}
          <div className="grid sm:grid-cols-2 gap-4 mt-8">
            <div className="p-5 bg-card border border-border rounded-xl">
              <h3 className="font-semibold mb-2">Taux ≥ 80%</h3>
              <p className="text-sm text-muted-foreground">
                L'AAH est attribuée <strong>sans restriction de durée</strong>. Le montant dépend uniquement
                de vos ressources. Possibilité de cumul partiel avec un salaire.
              </p>
            </div>
            <div className="p-5 bg-card border border-border rounded-xl">
              <h3 className="font-semibold mb-2">Taux 50% - 79%</h3>
              <p className="text-sm text-muted-foreground">
                L'AAH est attribuée pour <strong>1 à 5 ans</strong>, sous réserve d'une restriction
                substantielle et durable d'accès à l'emploi (RSDAE) reconnue par la CDAPH.
              </p>
            </div>
          </div>

          {/* CTA */}
          <div className="mt-12 p-8 bg-foreground text-primary-foreground rounded-2xl text-center" data-testid="aah-cta">
            <h2 className="text-2xl font-semibold mb-3">
              Besoin d'aide pour votre dossier ?
            </h2>
            <p className="text-primary-foreground/70 mb-6 max-w-lg mx-auto">
              La constitution d'un dossier MDPH est déterminante pour l'obtention de l'AAH.
              Je vous accompagne dans cette démarche cruciale.
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
