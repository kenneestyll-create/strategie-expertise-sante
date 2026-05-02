import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import axios from 'axios';
import { SEO } from '@/components/SEO';
import { DossierExpressCTA } from '@/components/DossierExpressCTA';
import {
  Calculator,
  AlertTriangle,
  ArrowRight,
  Info,
  CalendarPlus,
  Users,
  Heart,
  Share2,
  Mail,
  MessageSquare,
  Phone,
  Copy,
  Check,
  Eye,
  ChevronDown
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// AAH avril 2026 : montant max = 1 041,59 €/mois
const AAH_MAX = 1041.59;
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
  const [searchParams] = useSearchParams();
  const [tauxInvalidite, setTauxInvalidite] = useState(80);
  const [situationFamiliale, setSituationFamiliale] = useState('seul');
  const [revenus, setRevenus] = useState(0);
  const [enfants, setEnfants] = useState(0);
  const [result, setResult] = useState(null);
  const [calculated, setCalculated] = useState(false);
  const [copied, setCopied] = useState(false);
  const [weeklyCount, setWeeklyCount] = useState(0);

  useEffect(() => {
    axios.get(`${API}/calculator/count`).then(r => setWeeklyCount(r.data.count)).catch(() => {});
  }, []);

  useEffect(() => {
    const t = searchParams.get('t');
    if (t) {
      const parsedT = parseInt(t, 10);
      const sf = searchParams.get('sf') || 'seul';
      const r = parseInt(searchParams.get('r') || '0', 10);
      const e = parseInt(searchParams.get('e') || '0', 10);
      if (parsedT >= 0 && parsedT <= 100) {
        setTauxInvalidite(parsedT);
        setSituationFamiliale(sf);
        setRevenus(r);
        setEnfants(e);
        const res = calculateAAH(parsedT, sf, r, e);
        setResult(res);
        setCalculated(true);
      }
    }
  }, [searchParams]);

  const handleCalculate = () => {
    const res = calculateAAH(tauxInvalidite, situationFamiliale, revenus, enfants);
    setResult(res);
    setCalculated(true);
    axios.post(`${API}/calculator/track`, { type: 'aah' }).then(() => {
      setWeeklyCount(prev => prev + 1);
    }).catch(() => {});
  };

  const getShareUrl = () => {
    const base = `${window.location.origin}/calculatrice-aah`;
    const params = new URLSearchParams({ t: tauxInvalidite, sf: situationFamiliale, r: revenus, e: enfants });
    return `${base}?${params.toString()}`;
  };

  const getShareText = () => {
    if (!result) return '';
    if (result.eligible) {
      return `Calculatrice AAH - Taux ${tauxInvalidite}% : AAH estimée à ${result.montant.toLocaleString('fr-FR')} €/mois. Estimez la vôtre :`;
    }
    return `Calculatrice AAH - Vérifiez votre éligibilité à l'AAH :`;
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
    const subject = encodeURIComponent('Mon estimation AAH - Stratégie & Expertise Santé');
    const body = encodeURIComponent(getShareText() + '\n\n' + getShareUrl());
    window.open(`mailto:?subject=${subject}&body=${body}`, '_blank');
  };

  return (
    <main className="page-transition pt-20">
      <SEO title="Calcul AAH : simulateur montant et éligibilité" description="Estimez votre AAH selon votre situation et vos revenus. Simulateur gratuit basé sur les barèmes 2026. Montant maximum : 1 041,59 €/mois." path="/calculatrice-aah" />
      {/* Hero */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Outil de simulation</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="aah-calculator-title">
              Calcul AAH — Simulateur montant et éligibilité
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

                  {/* Share buttons */}
                  <div className="pt-4 border-t border-border/50">
                    <p className="text-sm font-medium text-muted-foreground flex items-center gap-2 mb-3">
                      <Share2 className="w-4 h-4" /> Partager mon estimation
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={handleWhatsApp}
                        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-[#25D366]/10 text-[#25D366] hover:bg-[#25D366]/20 transition-colors"
                        data-testid="aah-share-whatsapp"
                      >
                        <MessageSquare className="w-4 h-4" /> WhatsApp
                      </button>
                      <button
                        onClick={handleSMS}
                        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-blue-500/10 text-blue-600 hover:bg-blue-500/20 transition-colors"
                        data-testid="aah-share-sms"
                      >
                        <Phone className="w-4 h-4" /> SMS
                      </button>
                      <button
                        onClick={handleEmail}
                        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-accent/10 text-accent hover:bg-accent/20 transition-colors"
                        data-testid="aah-share-email"
                      >
                        <Mail className="w-4 h-4" /> Email
                      </button>
                      <button
                        onClick={handleCopyLink}
                        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-muted hover:bg-muted/80 transition-colors"
                        data-testid="aah-share-copy"
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
            <div className="flex items-center justify-center gap-2 mt-6 py-3 px-5 bg-accent/5 border border-accent/15 rounded-full w-fit mx-auto" data-testid="aah-weekly-counter">
              <Eye className="w-4 h-4 text-accent" />
              <span className="text-sm font-medium text-muted-foreground">
                <strong className="text-foreground">{weeklyCount}</strong> personne{weeklyCount > 1 ? 's' : ''} {weeklyCount > 1 ? 'ont' : 'a'} estimé leurs droits cette semaine
              </span>
            </div>
          )}

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

          {/* SEO Content */}
          <section className="mt-12 space-y-8" data-testid="aah-seo-content">
            {/* L'essentiel */}
            <div className="p-5 rounded-xl bg-[#1a1a2e]/[0.03] border border-[#C9A84C]/20">
              <h2 className="font-semibold text-base mb-3 text-foreground">L'essentiel à retenir</h2>
              <ul className="space-y-1.5 list-none pl-0 text-sm text-muted-foreground">
                <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Montant max 2026 : <strong className="text-foreground">1 041,59 €/mois</strong> (revalorisation au 1er avril 2026)</span></li>
                <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Conditions : taux d'incapacité ≥ 80%, ou 50-79% avec RSDAE</span></li>
                <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Déconjugalisation : seuls <strong className="text-foreground">vos revenus</strong> comptent depuis octobre 2023</span></li>
                <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Cumul AAH + salaire : possible — l'AAH complète vos revenus</span></li>
                <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>L'AAH est exonérée d'impôt sur le revenu, de CSG et de CRDS</span></li>
                <li className="flex items-start gap-2"><span className="text-accent font-bold">·</span><span>Retraite : taux ≥ 80% → AAH maintenue en complément. Taux 50-79% → AAH remplacée par l'ASPA</span></li>
              </ul>
              <p className="text-xs text-muted-foreground mt-3 italic">Barèmes CAF en vigueur au 1er avril 2026. Montants indicatifs, susceptibles de revalorisation annuelle.</p>
            </div>

            {/* Pourquoi faire une simulation */}
            <div>
              <h2 className="text-lg font-semibold mb-2">Pourquoi faire une simulation AAH ?</h2>
              <p className="text-sm text-muted-foreground leading-relaxed">
                De nombreuses personnes pensent ne pas être éligibles à l'AAH — souvent à tort, notamment depuis la déconjugalisation. Même après un ancien refus, votre situation a pu évoluer. Ce simulateur vous permet de vérifier en quelques minutes si vous pouvez prétendre à cette allocation.
              </p>
            </div>

            {/* Comment est calculée l'AAH */}
            <div>
              <h2 className="text-lg font-semibold mb-2">Comment est calculée l'AAH ?</h2>
              <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
                <p>
                  L'AAH fonctionne en différentiel : la CAF compare le plafond de ressources à vos revenus réels, puis verse la différence. Sans revenu, vous percevez le montant plein. Avec des revenus d'activité, un abattement est appliqué — seule une partie de votre salaire est retenue dans le calcul, ce qui rend le cumul AAH + travail plus avantageux qu'une simple soustraction.
                </p>
                <p>
                  Le montant est recalculé chaque trimestre sur la base de votre déclaration trimestrielle de ressources. C'est pourquoi il peut varier d'un trimestre à l'autre, notamment en cas de changement d'activité ou de prime ponctuelle.
                </p>
              </div>
            </div>

            {/* Déconjugalisation */}
            <div className="p-5 rounded-xl bg-accent/5 border border-accent/15">
              <h2 className="text-lg font-semibold mb-2 text-foreground">Déconjugalisation : ce qui a changé</h2>
              <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">
                <p>
                  <strong className="text-foreground">Depuis octobre 2023, les revenus du conjoint ne bloquent plus l'AAH.</strong> Seuls vos revenus personnels sont pris en compte. Ce changement a rendu éligibles des milliers de personnes qui étaient exclues par le plafond conjugal.
                </p>
                <p>
                  Si vous n'aviez jamais fait la demande parce que votre conjoint travaille, ou si vous aviez essuyé un refus avant cette date — refaites une simulation. Votre situation peut avoir radicalement changé.
                </p>
              </div>
            </div>

            {/* Plafonds de ressources */}
            <div>
              <h2 className="text-lg font-semibold mb-3">Plafonds de ressources annuels (barème 2026)</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border border-border rounded-xl overflow-hidden">
                  <thead>
                    <tr className="bg-muted/50">
                      <th className="text-left p-3 font-medium text-foreground">Situation</th>
                      <th className="text-right p-3 font-medium text-foreground">Plafond annuel</th>
                      <th className="text-right p-3 font-medium text-foreground">Plafond mensuel</th>
                    </tr>
                  </thead>
                  <tbody className="text-muted-foreground">
                    <tr className="border-t border-border"><td className="p-3">Personne seule</td><td className="text-right p-3">12 499,08 €</td><td className="text-right p-3">1 041,59 €</td></tr>
                    <tr className="border-t border-border bg-muted/20"><td className="p-3">+ 1 enfant à charge</td><td className="text-right p-3">+6 249,54 €</td><td className="text-right p-3">+520,80 €</td></tr>
                    <tr className="border-t border-border"><td className="p-3">+ 2 enfants à charge</td><td className="text-right p-3">+12 499,08 €</td><td className="text-right p-3">+1 041,59 €</td></tr>
                  </tbody>
                </table>
              </div>
              <p className="text-xs text-muted-foreground mt-2 italic">Montants indicatifs au 1er avril 2026, susceptibles de revalorisation. Source : Code de la Sécurité sociale.</p>
            </div>

            {/* Cas concrets */}
            <div>
              <h2 className="text-lg font-semibold mb-3">Cas concrets</h2>
              <div className="space-y-3">
                <div className="p-4 rounded-xl bg-muted/30 border border-border">
                  <p className="font-medium text-sm text-foreground mb-1.5">Cas 1 — Personne seule, sans emploi, taux 80%</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Aucun revenu d'activité ni pension. L'AAH est versée à taux plein : <strong className="text-foreground">1 041,59 €/mois</strong>. Pas de calcul différentiel — le montant maximum s'applique directement.
                  </p>
                </div>
                <div className="p-4 rounded-xl bg-muted/30 border border-border">
                  <p className="font-medium text-sm text-foreground mb-1.5">Cas 2 — Activité à temps partiel, salaire 600 €/mois</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Après abattement sur les revenus d'activité, la ressource retenue est d'environ 400 €. L'AAH différentielle s'élève à environ <strong className="text-foreground">641 €/mois</strong>. Revenu total : ≈ 1 241 €. Travailler ne supprime pas l'AAH — elle complète vos revenus.
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
                    <p className="font-medium text-foreground">Ne pas demander l'AAH parce que le conjoint travaille</p>
                    <p className="text-muted-foreground text-xs mt-0.5">→ Depuis la déconjugalisation, seuls vos revenus comptent. Refaites une simulation.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                  <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                  <div>
                    <p className="font-medium text-foreground">Confondre taux d'invalidité et taux d'incapacité</p>
                    <p className="text-muted-foreground text-xs mt-0.5">→ Le taux d'invalidité (Sécurité sociale) et le taux d'incapacité (MDPH) sont deux évaluations distinctes avec des barèmes différents.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                  <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                  <div>
                    <p className="font-medium text-foreground">Déposer un dossier MDPH sans projet de vie</p>
                    <p className="text-muted-foreground text-xs mt-0.5">→ Le projet de vie est le seul document où vous décrivez l'impact réel du handicap sur votre quotidien. Sans lui, la RSDAE est rarement reconnue.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                  <span className="text-red-500 shrink-0 font-bold mt-0.5">✗</span>
                  <div>
                    <p className="font-medium text-foreground">Ne pas actualiser la déclaration trimestrielle</p>
                    <p className="text-muted-foreground text-xs mt-0.5">→ La CAF recalcule chaque trimestre. Une déclaration en retard peut entraîner un trop-perçu et un remboursement forcé.</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Encart conversion */}
          <DossierExpressCTA
            testId="aah-cta-dossier"
            title="Votre simulation ne correspond pas à votre réalité ?"
            text="Beaucoup de demandes AAH sont refusées non par manque de droits, mais à cause d'un dossier mal articulé sur le RSDAE ou les ressources. Le Dossier Express IA identifie le point de blocage exact et formule la stratégie pour votre prochain dépôt ou recours."
            ctaLabel="Analyser mon dossier AAH"
          />

          {/* FAQ */}
          <AAHCalculatriceFAQ />

          {/* CTA */}
          <div className="mt-12 p-8 bg-foreground text-primary-foreground rounded-2xl text-center" data-testid="aah-cta">
            <h2 className="text-2xl font-semibold mb-3">
              Besoin d'aide pour votre dossier ?
            </h2>
            <p className="text-primary-foreground/70 mb-6 max-w-lg mx-auto">
              La constitution d'un dossier MDPH est déterminante pour l'obtention de l'AAH.
              Je vous accompagné dans cette démarche cruciale.
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


const aahFaqData = [
  {
    question: "L'AAH est-elle cumulable avec un salaire ?",
    answer: "Oui. L'AAH fonctionne en différentiel : un abattement est appliqué sur vos revenus d'activité, et l'allocation complète la différence jusqu'au plafond. Travailler ne supprime pas l'AAH, elle s'ajuste à vos revenus."
  },
  {
    question: "Quelle est la différence entre un taux de 80% et un taux entre 50% et 79% ?",
    answer: "Avec un taux d'au moins 80%, l'AAH est attribuée sans restriction de durée. Avec un taux entre 50% et 79%, l'attribution est limitée à 1 à 5 ans et nécessite la reconnaissance d'une restriction substantielle et durable d'accès à l'emploi (RSDAE) par la CDAPH."
  },
  {
    question: "Comment est fixé le montant de l'AAH ?",
    answer: "Le montant dépend de vos ressources personnelles. Sans revenu, vous percevez le montant maximal (1 041,59 € en 2026). Avec des revenus, l'AAH est calculée en différentiel après abattement. Le montant est recalculé chaque trimestre sur la base de votre déclaration de ressources."
  },
  {
    question: "L'AAH est-elle imposable ?",
    answer: "Non. L'AAH est totalement exonérée d'impôt sur le revenu, de CSG et de CRDS. Elle ne doit pas être déclarée dans vos revenus imposables."
  },
  {
    question: "La déconjugalisation s'applique-t-elle automatiquement ?",
    answer: "Oui, depuis octobre 2023, seuls vos revenus personnels sont pris en compte, et non ceux de votre conjoint. Si l'ancien calcul conjugal était plus favorable, vous pouvez demander son maintien — mais ce cas est rare. Si vous aviez été refusé avant cette date, refaites une simulation."
  },
  {
    question: "Que devient l'AAH à l'ouverture des droits à la retraite ?",
    answer: "Cela dépend de votre taux d'incapacité. Avec un taux d'au moins 80%, l'AAH peut être maintenue en complément de votre pension de retraite si celle-ci est inférieure au montant de l'AAH (versement différentiel). Avec un taux entre 50% et 79%, l'AAH cesse à l'âge légal de la retraite et peut être remplacée par l'ASPA (Allocation de Solidarité aux Personnes Âgées) si vous y êtes éligible. Dans tous les cas, vous devez demander votre retraite — l'AAH ne dispense pas de cette démarche."
  }
];

const AAHCalculatriceFAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);

  useEffect(() => {
    // Remove ALL existing FAQPage schemas to prevent duplicates
    document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
      try { if (JSON.parse(s.textContent)['@type'] === 'FAQPage') s.remove(); } catch {}
    });
    const script = document.createElement('script');
    script.id = 'aah-faq-schema';
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": aahFaqData.map(f => ({
        "@type": "Question",
        "name": f.question,
        "acceptedAnswer": { "@type": "Answer", "text": f.answer }
      }))
    });
    document.head.appendChild(script);
    return () => { const el = document.getElementById('aah-faq-schema'); if (el) el.remove(); };
  }, []);

  return (
    <section className="mt-8" data-testid="aah-faq">
      <h2 className="text-lg font-semibold mb-4">Questions fréquentes sur l'AAH</h2>
      <div className="space-y-2">
        {aahFaqData.map((faq, i) => (
          <div key={i} className="border border-border rounded-xl overflow-hidden">
            <button
              onClick={() => setOpenIndex(openIndex === i ? null : i)}
              className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
              data-testid={`aah-faq-${i}`}
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
    </section>
  );
};
