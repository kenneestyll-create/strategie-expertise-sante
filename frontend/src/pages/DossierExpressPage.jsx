import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { toast } from 'sonner';
import {
  FileSearch, Upload, Mail, Clock, Shield, CheckCircle,
  ArrowRight, Loader2, FileText, Zap, Brain, AlertTriangle,
  ChevronRight, Sparkles, CreditCard, X, Crown
} from 'lucide-react';
import axios from 'axios';
import { SEO } from '@/components/SEO';
import { useReveal, useRevealChildren } from '@/hooks/useReveal';
import { DataConsentBox } from '@/components/DataConsentBox';
import { PdfCoverPreview } from '@/components/PdfCoverPreview';
import { DocumentUploader } from '@/components/DocumentUploader';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TYPES_DOSSIER = [
  "Accident du travail (AT)",
  "Maladie professionnelle (MP)",
  "Litige assurance / protection juridique",
  "Demande MDPH / AAH",
  "Expertise médicale",
  "Contestation taux IPP",
  "Autre"
];

const REGIMES = [
  "Régime général",
  "Régime agricole (MSA)",
  "Fonction publique",
  "Indépendant",
  "Autre"
];

export const DossierExpressPage = () => {
  const [searchParams] = useSearchParams();
  const [step, setStep] = useState('landing'); // landing, form, uploading, processing, success
  const [loading, setLoading] = useState(false);
  const [consent, setConsent] = useState(false);
  const [form, setForm] = useState({
    email: '', name: '', situation: '',
    type_dossier: '', regime: '',
    documents_text: ''
  });
  const [files, setFiles] = useState([]);
  const [dossierId, setDossierId] = useState(null);
  const [pollStatus, setPollStatus] = useState(null);
  const [premiumPdf, setPremiumPdf] = useState(false);
  const [analysePremium, setAnalysePremium] = useState(false);
  const [docChecks, setDocChecks] = useState({ readable: false, personal_info: false, dates_signatures: false });

  const featuresRef = useRevealChildren();
  const ctaBottomRef = useReveal();

  useEffect(() => {
    const payment = searchParams.get('payment');
    const sessionId = searchParams.get('session_id');
    if (payment === 'success' && sessionId) {
      const savedForm = sessionStorage.getItem('dossier_express_form');
      if (savedForm) {
        const parsed = JSON.parse(savedForm);
        setForm(parsed);
        setStep('form');
        toast.success("Paiement réussi ! Décrivez votre situation pour lancer l'analyse.");
      } else {
        setStep('form');
        toast.success("Paiement réussi ! Complétez le formulaire ci-dessous.");
      }
      window.history.replaceState({}, '', '/dossier-express');
    } else if (payment === 'cancelled') {
      toast.error("Paiement annulé");
      window.history.replaceState({}, '', '/dossier-express');
    }
  }, [searchParams]);

  // Poll for analysis status
  useEffect(() => {
    if (!dossierId || step !== 'processing') return;
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/dossier-express/status/${dossierId}`);
        setPollStatus(res.data);
        if (res.data.status === 'completed') {
          setStep('success');
          clearInterval(interval);
        } else if (res.data.status === 'error') {
          toast.error("Une erreur est survenue lors de l'analyse. Notre équipe a été notifiée.");
          clearInterval(interval);
        }
      } catch (e) { /* keep polling */ }
    }, 5000);
    return () => clearInterval(interval);
  }, [dossierId, step]);

  const handleCheckout = async () => {
    if (!form.email || !form.name) {
      toast.error("Veuillez renseigner votre nom et email");
      return;
    }
    sessionStorage.setItem('dossier_express_form', JSON.stringify(form));
    sessionStorage.setItem('dossier_express_premium_pdf', premiumPdf ? '1' : '0');
    sessionStorage.setItem('dossier_express_analyse_premium', analysePremium ? '1' : '0');
    setLoading(true);
    try {
      const res = await axios.post(`${API}/dossier-express/checkout`, {
        email: form.email,
        name: form.name,
        origin_url: window.location.origin,
        premium_pdf: premiumPdf,
        analyse_premium: analysePremium
      });
      window.location.href = res.data.url;
    } catch (err) {
      toast.error("Erreur lors du paiement. Veuillez réessayer.");
      setLoading(false);
    }
  };

  const handleSubmitDossier = async () => {
    if (!form.situation.trim()) {
      toast.error("Veuillez décrire votre situation");
      return;
    }
    setLoading(true);

    // Read file contents
    let documentsText = "";
    for (const file of files) {
      if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        documentsText += `\n--- ${file.name} ---\n` + await file.text();
      } else {
        documentsText += `\n--- ${file.name} (${file.type}, ${(file.size / 1024).toFixed(0)} Ko) ---\n[Document joint]\n`;
      }
    }

    try {
      const isPremium = sessionStorage.getItem('dossier_express_premium_pdf') === '1';
      const res = await axios.post(`${API}/dossier-express/submit`, {
        session_id: searchParams.get('session_id') || '',
        email: form.email,
        name: form.name,
        situation: form.situation,
        type_dossier: form.type_dossier,
        regime: form.regime,
        documents_text: documentsText,
        premium_pdf: isPremium
      });
      setDossierId(res.data.dossier_id);
      setStep('processing');
      sessionStorage.removeItem('dossier_express_form');
      sessionStorage.removeItem('dossier_express_premium_pdf');
    } catch (err) {
      toast.error("Erreur lors de l'envoi. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  // ==================== LANDING VIEW ====================
  if (step === 'landing') {
    return (
      <main className="page-transition pt-20">
      <SEO title="Dossier Express — Rapport d'analyse sous 2h" description="Uploadez vos documents, notre équipe les analyse avec l'aide de StratégiIA et vous recevez un rapport PDF complet sous 2 heures pour 97€." path="/dossier-express" />
        {/* Hero */}
        <section className="relative overflow-hidden" style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f3460 100%)' }}>
          <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(circle at 20% 50%, white 1px, transparent 1px)', backgroundSize: '24px 24px' }} />
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28 relative z-10">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <Badge className="bg-amber-500/20 text-amber-300 border-amber-500/30 mb-6" data-testid="dossier-express-badge">
                  <Zap className="w-3 h-3 mr-1" fill="currentColor" />
                  Rapport sous 2 heures
                </Badge>
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6" data-testid="dossier-express-title">
                  Dossier Express
                </h1>
                <p className="text-lg text-white/70 mb-8 leading-relaxed max-w-xl">
                  Uploadez vos documents, notre équipe les analyse avec l'aide de l'outil StratégiIA et vous recevez un <strong className="text-white">rapport PDF complet et personnalisé</strong> directement par email.
                </p>
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button
                    size="lg"
                    className="rounded-full px-8 gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold text-base"
                    onClick={() => setStep('form')}
                    data-testid="dossier-express-cta"
                  >
                    Analyser mon dossier - 97 €
                    <ArrowRight className="w-5 h-5" />
                  </Button>
                  <Link to="/tarifs">
                    <Button size="lg" variant="outline" className="rounded-full px-8 border-white/20 text-white hover:bg-white/10">
                      Voir tous les tarifs
                    </Button>
                  </Link>
                </div>
                {/* Price highlight */}
                <div className="mt-8 inline-flex items-center gap-3 bg-white/5 border border-white/10 rounded-2xl px-5 py-3">
                  <span className="text-3xl font-bold text-white">97 €</span>
                  <div className="text-sm text-white/60 leading-tight">
                    <span className="block">Rapport complet</span>
                    <span className="block text-amber-400 font-medium">Livré sous 2h par email</span>
                  </div>
                </div>
              </div>

              {/* Steps visual */}
              <div className="space-y-4 stagger">
                {[
                  { icon: Upload, title: "1. Uploadez vos documents", desc: "Documents médicaux, courriers CPAM, décisions..." },
                  { icon: Brain, title: "2. Analyse assistée par StratégiIA", desc: "Notre outil croise jurisprudences, barèmes et cas similaires pour affiner votre stratégie" },
                  { icon: FileText, title: "3. Recevez votre rapport PDF", desc: "Analyse complète, droits identifiés, stratégie recommandée" },
                  { icon: Mail, title: "4. Livré par email sous 2h", desc: "Rapport professionnel prêt à utiliser" }
                ].map((s, i) => (
                  <div key={i} className="reveal flex items-start gap-4 bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm hover:bg-white/[0.08] transition-all hover:border-amber-500/30 hover:translate-x-1 duration-300">
                    <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                      <s.icon className="w-5 h-5 text-amber-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white text-sm">{s.title}</h3>
                      <p className="text-white/50 text-sm mt-0.5">{s.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="section-padding">
          <div className="max-w-7xl mx-auto" ref={featuresRef}>
            <h2 className="text-2xl sm:text-3xl font-semibold text-center mb-12 reveal">Ce que contient votre rapport</h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 stagger">
              {[
                { icon: FileSearch, title: "Analyse de votre situation", desc: "Synthèse factuelle et identification des enjeux clés de votre dossier." },
                { icon: Shield, title: "Cadre juridique applicable", desc: "Textes de loi, jurisprudences pertinentes et barèmes officiels." },
                { icon: CheckCircle, title: "Vos droits identifiés", desc: "Liste exhaustive de vos droits avec explications claires." },
                { icon: AlertTriangle, title: "Points de vigilance", desc: "Faiblesses du dossier, pièces manquantes et risques." },
                { icon: Sparkles, title: "Stratégie recommandée", desc: "Plan d'action étape par étape avec délais indicatifs." },
                { icon: Clock, title: "Prochaines étapes", desc: "5 actions concrètes prioritaires à réaliser immédiatement." }
              ].map((f, i) => (
                <Card key={i} className="card-glow border-border reveal" data-testid={`feature-card-${i}`}>
                  <CardContent className="p-6 icon-bounce">
                    <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                      <f.icon className="w-5 h-5 text-accent" />
                    </div>
                    <h3 className="font-semibold mb-2">{f.title}</h3>
                    <p className="text-sm text-muted-foreground">{f.desc}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Disclaimer Legal */}
        <section className="py-6 bg-amber-50/50 border-y border-amber-200/30">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-start gap-3" data-testid="dossier-express-disclaimer">
              <AlertTriangle className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
              <p className="text-sm text-amber-900/70 leading-relaxed">
                <strong className="text-amber-900/90">Information importante :</strong> Le Dossier Express fournit une analyse documentaire et stratégique basée sur l'intelligence artificielle. 
                Ce service ne constitue pas une expertise médicale officielle ni une expertise judiciaire. 
                Il ne constitue pas un conseil juridique ni un avis médical. 
                Pour toute décision juridique ou médicale, consultez un professionnel qualifié.
              </p>
            </div>
          </div>
        </section>

        {/* CTA bottom */}
        <section className="section-padding bg-secondary">
          <div className="max-w-3xl mx-auto text-center reveal" ref={ctaBottomRef}>
            <h2 className="text-2xl sm:text-3xl font-semibold mb-4">Prêt à analyser votre dossier ?</h2>
            <p className="text-muted-foreground mb-8">
              En quelques minutes, recevez un rapport professionnel complet pour comprendre votre situation et vos options.
            </p>
            <Button
              size="lg"
              className="rounded-full px-10 gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold"
              onClick={() => setStep('form')}
              data-testid="dossier-express-cta-bottom"
            >
              Commencer - 97 €
              <ArrowRight className="w-5 h-5" />
            </Button>
            <p className="text-xs text-muted-foreground mt-4">Paiement sécurisé par Stripe. Rapport livré par email sous 2h.</p>
          </div>
        </section>
      </main>
    );
  }

  // ==================== FORM VIEW ====================
  if (step === 'form') {
    const hasPaid = searchParams.get('payment') === 'success' || searchParams.get('session_id');
    return (
      <main className="page-transition pt-20">
        <section className="section-padding">
          <div className="max-w-2xl mx-auto">
            <button onClick={() => setStep('landing')} className="text-sm text-muted-foreground hover:text-foreground mb-6 flex items-center gap-1">
              <ChevronRight className="w-4 h-4 rotate-180" /> Retour
            </button>
            <h2 className="text-3xl font-bold mb-2" data-testid="form-title">Votre Dossier Express</h2>
            <p className="text-muted-foreground mb-8">Remplissez les informations ci-dessous pour lancer l'analyse.</p>

            <div className="space-y-6">
              {/* Coordonnées */}
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="de-name">Nom complet *</Label>
                  <Input id="de-name" value={form.name} onChange={e => setForm(p => ({...p, name: e.target.value}))} placeholder="Prénom Nom" data-testid="de-name-input" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="de-email">Email *</Label>
                  <Input id="de-email" type="email" value={form.email} onChange={e => setForm(p => ({...p, email: e.target.value}))} placeholder="votre@email.fr" data-testid="de-email-input" />
                </div>
              </div>

              {/* Type & Régime */}
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Type de dossier</Label>
                  <select
                    value={form.type_dossier}
                    onChange={e => setForm(p => ({...p, type_dossier: e.target.value}))}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    data-testid="de-type-select"
                  >
                    <option value="">Sélectionnez...</option>
                    {TYPES_DOSSIER.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Régime</Label>
                  <select
                    value={form.regime}
                    onChange={e => setForm(p => ({...p, regime: e.target.value}))}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    data-testid="de-regime-select"
                  >
                    <option value="">Sélectionnez...</option>
                    {REGIMES.map(r => <option key={r} value={r}>{r}</option>)}
                  </select>
                </div>
              </div>

              {/* Situation */}
              <div className="space-y-2">
                <Label htmlFor="de-situation">Décrivez votre situation *</Label>
                <textarea
                  id="de-situation"
                  value={form.situation}
                  onChange={e => setForm(p => ({...p, situation: e.target.value}))}
                  rows={6}
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring"
                  placeholder="Décrivez votre situation en détail : historique, démarches entreprises, difficultés rencontrées, objectifs..."
                  data-testid="de-situation-input"
                />
                <p className="text-xs text-muted-foreground">Plus votre description est détaillée, plus l'analyse sera pertinente.</p>
              </div>

              {/* Document upload with quality control */}
              <div className="space-y-2">
                <Label>Documents (optionnel, max 5 fichiers)</Label>
                <DocumentUploader
                  files={files}
                  onFilesChange={setFiles}
                  maxFiles={5}
                  showChecklist={files.length > 0}
                  showGuide={true}
                />
              </div>

              {/* Action */}
              <DataConsentBox checked={consent} onChange={setConsent} className="mt-4" />

              {/* Analyse Premium option */}
              <label className="flex items-start gap-3 p-3 rounded-lg border border-border hover:border-amber-500/30 cursor-pointer transition-colors mt-3" data-testid="de-analyse-premium-option">
                <input type="checkbox" checked={analysePremium} onChange={e => setAnalysePremium(e.target.checked)} className="mt-0.5 accent-amber-500" />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-amber-400 text-sm">&#9889;</span>
                    <span className="text-sm font-medium">Analyse Premium</span>
                    <Badge className="bg-amber-500/10 text-amber-600 border-amber-500/20 text-[10px]">+49€</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">Votre dossier analysé par StratégiIA puis enrichi par la relecture personnelle de notre expert avec ses recommandations exclusives.</p>
                </div>
              </label>

              {/* Premium PDF option */}
              <label className="flex items-start gap-3 p-3 rounded-lg border border-border hover:border-accent/40 cursor-pointer transition-colors mt-3" data-testid="de-premium-pdf-option">
                <input type="checkbox" checked={premiumPdf} onChange={e => setPremiumPdf(e.target.checked)} className="mt-0.5 accent-amber-500" />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Crown className="w-4 h-4 text-accent" />
                    <span className="text-sm font-medium">Version professionnelle du rapport</span>
                    <Badge className="bg-accent/10 text-accent border-accent/20 text-[10px]">+19€</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">Rapport sans filigrane, mise en page optimisée pour impression ou transmission à un professionnel (avocat, médecin, expert).</p>
                </div>
                <PdfCoverPreview reportType="Dossier Express" />
              </label>

              {hasPaid ? (
                <Button
                  size="lg"
                  className="w-full rounded-xl gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold"
                  onClick={handleSubmitDossier}
                  disabled={loading || !form.situation.trim() || !form.email || !consent || (files.length > 0 && !(docChecks.readable && docChecks.personal_info && docChecks.dates_signatures))}
                  data-testid="de-submit-button"
                >
                  {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Envoi en cours...</> : <><Brain className="w-5 h-5" /> Soumettre mon dossier</>}
                </Button>
              ) : (
                <Button
                  size="lg"
                  className="w-full rounded-xl gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold"
                  onClick={handleCheckout}
                  disabled={loading || !form.email || !form.name || !consent || (files.length > 0 && !(docChecks.readable && docChecks.personal_info && docChecks.dates_signatures))}
                  data-testid="de-checkout-button"
                >
                  {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Redirection...</> : <><CreditCard className="w-5 h-5" /> Payer {97 + (premiumPdf ? 19 : 0) + (analysePremium ? 49 : 0)} € et lancer l'analyse</>}
                </Button>
              )}

              <p className="text-xs text-muted-foreground text-center">
                Paiement sécurisé par Stripe. Rapport PDF envoyé à votre email sous 2 heures maximum.
              </p>
            </div>
          </div>
        </section>
      </main>
    );
  }

  // ==================== PROCESSING VIEW ====================
  if (step === 'processing') {
    return (
      <main className="page-transition pt-20">
        <section className="section-padding">
          <div className="max-w-lg mx-auto text-center">
            <div className="w-20 h-20 bg-amber-500/10 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
              <Brain className="w-10 h-10 text-amber-500" />
            </div>
            <h2 className="text-2xl font-bold mb-3" data-testid="processing-title">Analyse en cours...</h2>
            <p className="text-muted-foreground mb-8">
              Votre dossier est en cours de traitement. Notre équipe, assistée par l'outil StratégiIA, prépare votre rapport. Vous le recevrez par email à <strong>{form.email}</strong>.
            </p>
            <div className="space-y-3 text-left max-w-sm mx-auto">
              {[
                { label: "Réception du dossier", done: true },
                { label: "Analyse en cours avec StratégiIA", done: false, active: true },
                { label: "Génération du rapport PDF", done: false },
                { label: "Envoi par email", done: false }
              ].map((s, i) => (
                <div key={i} className={`flex items-center gap-3 text-sm ${s.done ? 'text-green-600' : s.active ? 'text-amber-500 font-medium' : 'text-muted-foreground'}`}>
                  {s.done ? <CheckCircle className="w-5 h-5" /> : s.active ? <Loader2 className="w-5 h-5 animate-spin" /> : <div className="w-5 h-5 rounded-full border-2 border-muted" />}
                  {s.label}
                </div>
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-8">
              Vous pouvez fermer cette page. Le rapport sera envoyé à votre email sous 2 heures maximum.
            </p>
          </div>
        </section>
      </main>
    );
  }

  // ==================== SUCCESS VIEW ====================
  if (step === 'success') {
    return (
      <main className="page-transition pt-20">
        <section className="section-padding">
          <div className="max-w-lg mx-auto text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold mb-3" data-testid="success-title">Rapport envoyé !</h2>
            <p className="text-muted-foreground mb-6">
              Votre rapport Dossier Express a été envoyé à <strong>{form.email || pollStatus?.email}</strong>.
              Vérifiez votre boîte de réception (et vos spams).
            </p>
            <div className="bg-secondary rounded-xl p-6 text-left mb-8">
              <h3 className="font-semibold mb-3">Et ensuite ?</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />Lisez attentivement votre rapport d'analyse</li>
                <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />Suivez les prochaines étapes recommandées</li>
                <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />Pour un accompagnement personnalisé, prenez rendez-vous</li>
              </ul>
            </div>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/agenda">
                <Button className="rounded-full px-6 gap-2">
                  Réserver un appel
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Link to="/tarifs">
                <Button variant="outline" className="rounded-full px-6">
                  Voir nos prestations
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>
    );
  }

  return null;
};
