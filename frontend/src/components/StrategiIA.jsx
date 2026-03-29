import { useState, useCallback, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { PremiumAnalysisRenderer } from '@/components/PremiumAnalysisRenderer';
import {
  X, Brain, Loader2, FileText, Download, Lock,
  MessageSquare, Phone, Mail, Copy, Check,
  AlertTriangle, CreditCard, ArrowRight, Sparkles, UserPlus, Crown,
  Target, Shield, Clock, User, CheckCircle
} from 'lucide-react';
import axios from 'axios';
import { DataConsentBox } from '@/components/DataConsentBox';
import { PdfCoverPreview } from '@/components/PdfCoverPreview';
import { useAdminTest } from '@/components/AdminTestBanner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TYPES_DOSSIER = [
  { value: 'at', label: "Accident du travail" },
  { value: 'mp', label: "Maladie professionnelle" },
  { value: 'mdph', label: "Demande MDPH / Handicap" },
  { value: 'assurance', label: "Litige assurantiel" },
  { value: 'expertise', label: "Expertise médicale" },
  { value: 'faute_inex', label: "Faute inexcusable employeur" },
  { value: 'recours', label: "Recours / Contestation" },
  { value: 'autre', label: "Autre" },
];

const REGIMES = [
  { value: 'general', label: "Régime général" },
  { value: 'agricole', label: "MSA (agricole)" },
  { value: 'fonctionnaire', label: "Fonction publique" },
  { value: 'independant', label: "Indépendant / TNS" },
  { value: 'ratp_sncf', label: "Régimes spéciaux RATP / SNCF" },
  { value: 'autre', label: "Autre" },
];

export const StrategiIA = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAdminMode, adminToken } = useAdminTest();

  // Allow external trigger (mobile FAB + email link)
  useEffect(() => {
    const open = () => setIsOpen(true);
    window.addEventListener('strategiia:open', open);

    // Auto-open if URL has ?open=strategiia
    const params = new URLSearchParams(window.location.search);
    if (params.get('open') === 'strategiia') {
      setIsOpen(true);
      // Clean up the URL
      window.history.replaceState({}, '', window.location.pathname);
    }

    return () => window.removeEventListener('strategiia:open', open);
  }, []);
  // Steps: form -> loading -> teaser -> basic -> premium | quota_exceeded
  const [step, setStep] = useState('form');
  const [typeDossier, setTypeDossier] = useState('');
  const [regime, setRegime] = useState('');
  const [situation, setSituation] = useState('');
  const [email, setEmail] = useState('');
  const [fullResult, setFullResult] = useState('');
  const [premiumResult, setPremiumResult] = useState('');
  const [casesFound, setCasesFound] = useState(0);
  const [copied, setCopied] = useState(false);
  const [remaining, setRemaining] = useState(null);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [consent, setConsent] = useState(false);
  const [premiumPdf, setPremiumPdf] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [analysePremium, setAnalysePremium] = useState(false);
  const [scoreData, setScoreData] = useState(null);

  // Fetch relevance score when we have results
  useEffect(() => {
    if ((step === 'basic' || step === 'teaser') && typeDossier) {
      axios.get(`${API}/strategiia/score`, { params: { type_dossier: typeDossier, regime } })
        .then(res => setScoreData(res.data))
        .catch(() => setScoreData(null));
    }
  }, [step, typeDossier, regime]);

  // Analyze without email — result gated behind read wall
  const handleAnalyze = async () => {
    if (!typeDossier || !situation.trim()) {
      toast.error("Veuillez remplir le type de dossier et la description");
      return;
    }
    setStep('loading');
    try {
      const headers = {};
      if (isAdminMode && adminToken) headers['Authorization'] = `Bearer ${adminToken}`;
      const { data } = await axios.post(`${API}/strategiia/analyze`, {
        type_dossier: typeDossier, regime, situation, premium: false,
        admin_test: isAdminMode
      }, { headers });
      if (data.quota_exceeded) {
        toast.error(data.message);
        setStep('form');
        return;
      }
      // Async polling — backend returns job_id immediately
      const jobId = data.job_id;
      let pollErrors = 0;
      let jobCompleted = false; // Flag to prevent race condition with in-flight requests
      const poll = setInterval(async () => {
        if (jobCompleted) return; // Skip if already done
        try {
          const { data: st } = await axios.get(`${API}/strategiia/status/${jobId}`);
          pollErrors = 0; // reset on success
          if (st.status === 'done') {
            jobCompleted = true;
            clearInterval(poll);
            setFullResult(st.analysis);
            setCasesFound(st.cases_found || 0);
            setRemaining(st.remaining ?? null);
            setStep('teaser');
          } else if (st.status === 'error') {
            jobCompleted = true;
            clearInterval(poll);
            toast.error(st.error || "Erreur lors de l'analyse.");
            setStep('form');
          }
        } catch {
          if (jobCompleted) return; // Ignore errors from in-flight requests after completion
          pollErrors++;
          if (pollErrors >= 3) {
            jobCompleted = true;
            clearInterval(poll);
            toast.error("Erreur de connexion persistante. Veuillez réessayer.");
            setStep('form');
          }
        }
      }, 3000);
    } catch (err) {
      const status = err?.response?.status;
      if (status === 503) {
        toast.error("Le service d'analyse est temporairement indisponible.");
      } else {
        toast.error("Erreur lors de l'analyse. Veuillez réessayer.");
      }
      setStep('form');
    }
  };

  // Register email to unlock full result
  const handleRegisterEmail = async () => {
    // Admin bypass: skip email validation, don't create leads
    if (isAdminMode && adminToken) {
      setEmail('admin-test@ses-interne.fr');
      setRemaining(999);
      setStep('basic');
      toast.success("Mode Admin : email bypass, pas de lead créé.");
      return;
    }
    if (!email.trim() || !email.includes('@')) {
      toast.error("Veuillez entrer un email valide");
      return;
    }
    setRegisterLoading(true);
    try {
      const headers = {};
      if (isAdminMode && adminToken) headers['Authorization'] = `Bearer ${adminToken}`;
      const { data } = await axios.post(`${API}/strategiia/register-email`, {
        email: email.trim().toLowerCase(),
        admin_test: isAdminMode
      }, { headers });
      setRemaining(data.remaining);
      if (data.remaining <= 0) {
        setStep('quota_exceeded');
      } else {
        setStep('basic');
      }
      toast.success("Inscription réussie ! Voici votre analyse complète.");
    } catch {
      // Even if registration fails, show the full result
      setStep('basic');
    } finally {
      setRegisterLoading(false);
    }
  };

  const handlePayForPremium = async () => {
    // Admin bypass: skip Stripe, run premium analysis directly WITH selected options
    if (isAdminMode && adminToken) {
      setStep('loading');
      const opts = [];
      if (analysePremium) opts.push('Relecture expert');
      if (premiumPdf) opts.push('PDF pro');
      toast.info(`Mode Admin : bypass paiement${opts.length ? ' (' + opts.join(' + ') + ')' : ''}, analyse en cours...`);
      try {
        const { data } = await axios.post(`${API}/strategiia/admin-bypass-premium`, {
          situation, type_dossier: typeDossier, regime,
          premium_pdf: premiumPdf, analyse_premium: analysePremium
        }, { headers: { 'Authorization': `Bearer ${adminToken}` } });
        if (premiumPdf) setPremiumPdf(true);
        const jobId = data.job_id;
        let pollErrors2 = 0;
        let jobCompleted2 = false; // Flag to prevent race condition
        const poll = setInterval(async () => {
          if (jobCompleted2) return;
          try {
            const { data: st } = await axios.get(`${API}/strategiia/status/${jobId}`);
            pollErrors2 = 0;
            if (st.status === 'done') {
              jobCompleted2 = true;
              clearInterval(poll);
              // If relecture expert selected: show waiting step, not immediate result
              if (analysePremium) {
                setStep('relecture_attente');
                toast.success("Mode Admin : dossier transmis pour relecture expert (simulation).");
              } else {
                setPremiumResult(st.analysis);
                setStep('premium');
                toast.success("Mode Admin : rapport premium généré (test interne).");
              }
            } else if (st.status === 'error') {
              jobCompleted2 = true;
              clearInterval(poll);
              toast.error(st.error || "Erreur lors de l'analyse premium.");
              setStep('basic');
            }
          } catch {
            if (jobCompleted2) return;
            pollErrors2++;
            if (pollErrors2 >= 3) { jobCompleted2 = true; clearInterval(poll); toast.error("Erreur de connexion persistante."); setStep('basic'); }
          }
        }, 3000);
      } catch { toast.error("Erreur bypass admin."); setStep('basic'); }
      return;
    }
    try {
      const { data } = await axios.post(`${API}/strategiia/checkout`, {
        origin_url: window.location.origin, email,
        context: `${typeDossier} - ${situation.slice(0, 100)}`,
        premium_pdf: premiumPdf,
        analyse_premium: analysePremium
      });
      if (data.url) window.location.href = data.url;
    } catch { toast.error("Erreur de paiement. Réessayez."); }
  };

  const handleDownloadPDF = useCallback(async () => {
    setPdfLoading(true);
    try {
      const { data } = await axios.post(`${API}/strategiia/generate-pdf`, {
        analysis: premiumResult,
        type_dossier: TYPES_DOSSIER.find(t => t.value === typeDossier)?.label || typeDossier,
        regime: REGIMES.find(r => r.value === regime)?.label || regime,
        name: email,
        premium_pdf: premiumPdf
      });
      const byteCharacters = atob(data.pdf_base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) byteNumbers[i] = byteCharacters.charCodeAt(i);
      const blob = new Blob([new Uint8Array(byteNumbers)], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = data.filename || 'strategiia-rapport.pdf';
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Rapport PDF téléchargé !");
    } catch {
      toast.error("Erreur lors de la génération du PDF.");
    } finally { setPdfLoading(false); }
  }, [premiumResult, typeDossier, regime, email, premiumPdf]);

  const getShareUrl = () => `${window.location.origin}/simulateur`;
  const getShareText = () => `J'ai analysé mon dossier avec StratégiIA sur Stratégie & Expertise Santé. Analysez le vôtre :`;
  const handleWhatsApp = () => window.open(`https://wa.me/?text=${encodeURIComponent(getShareText() + ' ' + getShareUrl())}`, '_blank');
  const handleSMS = () => window.open(`sms:?body=${encodeURIComponent(getShareText() + ' ' + getShareUrl())}`, '_blank');
  const handleShareEmail = () => window.open(`mailto:?subject=${encodeURIComponent('StratégiIA — Analyse de dossier')}&body=${encodeURIComponent(getShareText() + '\n\n' + getShareUrl())}`, '_blank');
  const handleCopyLink = () => { navigator.clipboard.writeText(getShareUrl()); setCopied(true); setTimeout(() => setCopied(false), 2000); };

  const handleClose = () => setIsOpen(false);
  const handleReset = () => {
    setStep('form');
    setTypeDossier(''); setRegime(''); setSituation('');
    setFullResult(''); setPremiumResult('');
    setConsent(false); setPremiumPdf(false); setAnalysePremium(false); setScoreData(null);
  };

  const [loadingStep, setLoadingStep] = useState(0);
  const [loadingPct, setLoadingPct] = useState(0);

  // Progress animation during loading
  useEffect(() => {
    if (step !== 'loading') { setLoadingStep(0); setLoadingPct(0); return; }
    const timers = [
      setTimeout(() => { setLoadingStep(1); setLoadingPct(15); }, 500),
      setTimeout(() => { setLoadingStep(2); setLoadingPct(35); }, 2500),
      setTimeout(() => { setLoadingStep(3); setLoadingPct(60); }, 5500),
      setTimeout(() => { setLoadingStep(4); setLoadingPct(85); }, 8500),
    ];
    return () => timers.forEach(clearTimeout);
  }, [step]);

  // Split analysis into 3 tiers based on ---SECTION--- markers
  const splitAnalysis = (text) => {
    if (!text) return { tier1: '', tier2: '', tier3: '' };
    const parts = text.split(/---SECTION_[123]---/).filter(p => p.trim());
    if (parts.length >= 3) {
      return { tier1: parts[0].trim(), tier2: parts[1].trim(), tier3: parts[2].trim() };
    }
    const lines = text.split('\n');
    const t1 = Math.ceil(lines.length / 3);
    const t2 = Math.ceil(lines.length * 2 / 3);
    return {
      tier1: lines.slice(0, t1).join('\n'),
      tier2: lines.slice(t1, t2).join('\n'),
      tier3: lines.slice(t2).join('\n'),
    };
  };

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0" style={{ zIndex: 'var(--z-modal)' }}>
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={handleClose} />
          <div className="relative w-full max-w-2xl mx-auto mt-[2vh] sm:mt-[5vh] px-3 sm:px-4 flex flex-col" style={{ maxHeight: '96vh', maxHeight: '96dvh' }}>
            <div className="bg-background border border-border rounded-2xl shadow-2xl overflow-hidden flex flex-col" style={{ maxHeight: '92vh', maxHeight: '92dvh' }} data-testid="strategiia-modal">
              {/* Header */}
              <div className="flex items-center justify-between p-5 bg-foreground text-primary-foreground flex-shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-accent rounded-xl flex items-center justify-center">
                    <Brain className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-base flex items-center gap-2">
                      StratégiIA
                      {isAdminMode ? (
                        <Badge data-testid="strategiia-admin-badge" className="text-[10px] px-1.5 py-0 bg-amber-500/30 text-amber-300 border-amber-400/50">
                          <Shield className="w-3 h-3 mr-0.5" />Admin
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="text-[10px] px-1.5 py-0 bg-accent/20 text-accent border-0">Exclusif</Badge>
                      )}
                    </h3>
                    <p className="text-xs text-primary-foreground/60">Outil d'aide à l'analyse stratégique</p>
                  </div>
                </div>
                <button onClick={handleClose} className="p-2 hover:bg-white/10 rounded-lg transition-colors" aria-label="Fermer">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Content */}
              <div className="overflow-y-auto flex-1 p-5">

                {/* FORM STEP — no email required */}
                {step === 'form' && (
                  <div className="space-y-4" data-testid="strategiia-form">
                    <div className="text-center pb-2">
                      <h3 className="text-lg font-semibold mb-1">Obtenez votre pré-analyse personnalisée</h3>
                      <p className="text-sm text-muted-foreground">Décrivez votre situation pour recevoir une pré-analyse gratuite assistée par notre outil StratégiIA</p>
                    </div>
                    <div className="p-3 rounded-lg bg-amber-50 border border-amber-200/50" data-testid="strategiia-disclaimer">
                      <p className="text-[11px] text-amber-800 leading-relaxed">
                        <strong>Information :</strong> Cet outil fournit une analyse documentaire et stratégique. 
                        Il ne constitue pas une expertise médicale officielle, un conseil juridique ni un avis médical. 
                        Consultez un professionnel qualifié pour toute décision.
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label className="font-medium">Type de dossier *</Label>
                      <Select value={typeDossier} onValueChange={setTypeDossier}>
                        <SelectTrigger data-testid="strategiia-type-select"><SelectValue placeholder="Sélectionnez le type de dossier" /></SelectTrigger>
                        <SelectContent>
                          {TYPES_DOSSIER.map(t => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="font-medium">Régime</Label>
                      <Select value={regime} onValueChange={setRegime}>
                        <SelectTrigger data-testid="strategiia-regime-select"><SelectValue placeholder="Sélectionnez votre régime" /></SelectTrigger>
                        <SelectContent>
                          {REGIMES.map(r => <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="font-medium">Décrivez votre situation *</Label>
                      <textarea
                        value={situation} onChange={e => setSituation(e.target.value)}
                        placeholder="Ex: J'ai développé un syndrome du canal carpien après 15 ans de travail en usine..."
                        className="flex w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring min-h-[120px] resize-none"
                        data-testid="strategiia-situation-input"
                      />
                    </div>
                    <DataConsentBox checked={consent} onChange={setConsent} />

                    <Button onClick={handleAnalyze} className="w-full rounded-lg gap-2" disabled={!typeDossier || !situation.trim() || !consent} data-testid="strategiia-analyze-button">
                      <Brain className="w-4 h-4" /> Obtenir ma pré-analyse gratuite
                    </Button>
                    <p className="text-[11px] text-muted-foreground text-center flex items-center justify-center gap-1">
                      <AlertTriangle className="w-3 h-3" />
                      Outil d'aide à la décision — Les résultats ne constituent pas un conseil juridique
                    </p>
                  </div>
                )}

                {/* LOADING — Barre de progression animée */}
                {step === 'loading' && (
                  <div className="py-10 space-y-6" data-testid="strategiia-loading">
                    <div className="flex flex-col items-center gap-3">
                      <div className="w-14 h-14 bg-accent/10 rounded-2xl flex items-center justify-center">
                        <Brain className="w-7 h-7 text-accent animate-pulse" />
                      </div>
                      <p className="font-semibold text-base">Analyse en cours...</p>
                    </div>

                    {/* Progress bar */}
                    <div className="max-w-md mx-auto space-y-2">
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-accent rounded-full transition-all duration-1000 ease-out"
                          style={{ width: `${loadingPct}%` }}
                          data-testid="strategiia-progress-bar"
                        />
                      </div>
                      <div className="flex justify-between text-[11px] text-muted-foreground">
                        <span>StratégiIA</span>
                        <span>{loadingPct}%</span>
                      </div>
                    </div>

                    {/* Dynamic step indicators */}
                    <div className="max-w-sm mx-auto space-y-3">
                      {[
                        'Identification du type de dossier',
                        'Croisement des jurisprudences',
                        'Recherche de cas similaires',
                        'Génération de votre pré-analyse',
                      ].map((label, i) => {
                        const stepNum = i + 1;
                        const isDone = loadingStep > stepNum;
                        const isActive = loadingStep === stepNum;
                        return (
                          <div
                            key={i}
                            className={`flex items-center gap-3 text-sm transition-opacity duration-500 ${loadingStep >= stepNum ? 'opacity-100' : 'opacity-30'}`}
                          >
                            <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${isDone ? 'bg-accent/20' : isActive ? 'bg-accent/10' : 'bg-muted'}`}>
                              {isDone ? <Check className="w-3.5 h-3.5 text-accent" /> : isActive ? <Loader2 className="w-3.5 h-3.5 text-accent animate-spin" /> : <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground/30" />}
                            </div>
                            <span className={isDone ? 'text-foreground/80' : isActive ? 'text-foreground' : ''}>{label}</span>
                          </div>
                        );
                      })}
                    </div>

                    <p className="text-xs text-muted-foreground text-center">Cela prend généralement 10 à 15 secondes</p>
                  </div>
                )}

                {/* ═══ PALIER 1 : TEASER — 1/3 visible, sans email ═══ */}
                {step === 'teaser' && (
                  <div className="space-y-0" data-testid="strategiia-teaser">
                    <div className="flex items-center gap-2 mb-3">
                      <Sparkles className="w-5 h-5 text-accent" />
                      <h3 className="font-semibold">Votre pré-analyse est prête</h3>
                      {casesFound > 0 && <Badge variant="outline" className="text-xs">{casesFound} cas similaire{casesFound > 1 ? 's' : ''}</Badge>}
                    </div>
                    {/* Tier 1 content — 1/3 visible */}
                    <div className="relative">
                      <div className="prose prose-sm max-w-none text-sm leading-relaxed bg-muted/30 p-4 rounded-xl border border-border" data-testid="strategiia-teaser-text">
                        <ReactMarkdown>{splitAnalysis(fullResult).tier1}</ReactMarkdown>
                      </div>
                      {/* Gradient fade overlay */}
                      <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-background via-background/95 to-transparent rounded-b-xl" />
                    </div>

                    {/* Email unlock CTA */}
                    <div className="relative -mt-6 pt-4" data-testid="strategiia-readwall">
                      <Card className="border-accent/40 bg-gradient-to-b from-accent/5 to-accent/10 shadow-lg">
                        <CardContent className="p-5 space-y-3 text-center">
                          <div className="w-12 h-12 bg-accent/15 rounded-full flex items-center justify-center mx-auto">
                            <UserPlus className="w-6 h-6 text-accent" />
                          </div>
                          <div>
                            <h4 className="font-bold text-base" data-testid="readwall-title">L'analyse continue...</h4>
                            <p className="text-sm text-muted-foreground mt-1">Entrez votre email pour débloquer l'analyse approfondie, les démarches prioritaires et une première estimation.</p>
                          </div>
                          <div className="flex gap-2 max-w-sm mx-auto">
                            <Input
                              value={email}
                              onChange={e => setEmail(e.target.value)}
                              placeholder="votre@email.fr"
                              type="email"
                              className="flex-1"
                              data-testid="strategiia-readwall-email"
                              onKeyDown={e => e.key === 'Enter' && handleRegisterEmail()}
                            />
                            <Button
                              onClick={handleRegisterEmail}
                              disabled={(!email.includes('@') && !(isAdminMode && adminToken)) || registerLoading}
                              className="gap-1.5 rounded-lg px-5"
                              data-testid="strategiia-readwall-submit"
                            >
                              {registerLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
                              Débloquer
                            </Button>
                          </div>
                          <p className="text-[11px] text-muted-foreground">
                            Pré-analyse gratuite et sans engagement. 3 analyses par mois.
                          </p>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                )}

                {/* ═══ PALIER 2 : APRÈS EMAIL — ~2/4 visible + upsell premium ═══ */}
                {step === 'basic' && (
                  <div className="space-y-4" data-testid="strategiia-basic-result">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-5 h-5 text-accent" />
                      <h3 className="font-semibold">Analyse intermédiaire</h3>
                      {casesFound > 0 && <Badge variant="outline" className="text-xs">{casesFound} cas similaire{casesFound > 1 ? 's' : ''}</Badge>}
                      {remaining !== null && remaining > 0 && (
                        <Badge className="bg-green-100 text-green-700 border-green-200 text-xs">{remaining} restante{remaining > 1 ? 's' : ''}</Badge>
                      )}
                    </div>

                    {/* Tier 1 + Tier 2 visible */}
                    <div className="relative">
                      <div className="prose prose-sm max-w-none text-sm leading-relaxed bg-muted/30 p-4 rounded-xl border border-border" data-testid="strategiia-basic-text">
                        <ReactMarkdown>{splitAnalysis(fullResult).tier1 + '\n\n' + splitAnalysis(fullResult).tier2}</ReactMarkdown>
                      </div>
                      {/* Gradient fade */}
                      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background via-background/95 to-transparent rounded-b-xl" />
                    </div>

                    {/* Preview locked content hints */}
                    <div className="space-y-2 px-1">
                      <div className="flex items-center gap-2 text-muted-foreground/60 text-xs">
                        <Lock className="w-3.5 h-3.5" />
                        <span className="line-through">Jurisprudences exactes applicables à votre dossier</span>
                      </div>
                      <div className="flex items-center gap-2 text-muted-foreground/60 text-xs">
                        <Lock className="w-3.5 h-3.5" />
                        <span className="line-through">Stratégie complète en 5-6 étapes</span>
                      </div>
                      <div className="flex items-center gap-2 text-muted-foreground/60 text-xs">
                        <Lock className="w-3.5 h-3.5" />
                        <span className="line-through">Score de pertinence et estimation chiffrée</span>
                      </div>
                      <div className="flex items-center gap-2 text-muted-foreground/60 text-xs">
                        <Lock className="w-3.5 h-3.5" />
                        <span className="line-through">Rapport PDF sécurisé téléchargeable</span>
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-yellow-50 border border-yellow-200/50">
                      <p className="text-xs text-yellow-700 flex items-start gap-2">
                        <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                        <strong>Outil d'aide à la décision — Les résultats sont indicatifs et ne constituent pas un conseil juridique.</strong>
                      </p>
                    </div>

                    {/* Premium upsell — 29€ */}
                    <Card className="border-accent/30 bg-gradient-to-b from-accent/5 to-accent/10 shadow-lg">
                      <CardContent className="p-5 space-y-4">
                        <div className="text-center">
                          <div className="w-14 h-14 bg-accent/15 rounded-full flex items-center justify-center mx-auto mb-3">
                            <Crown className="w-7 h-7 text-accent" />
                          </div>
                          <h4 className="font-bold text-lg">Rapport complet StratégiIA</h4>
                          <p className="text-sm text-muted-foreground mt-1">Débloquez l'analyse complète avec les informations les plus stratégiques</p>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div className="flex items-start gap-2 p-2 rounded-lg bg-background">
                            <Check className="w-3.5 h-3.5 text-accent mt-0.5 flex-shrink-0" />
                            <span>Jurisprudences précises avec références</span>
                          </div>
                          <div className="flex items-start gap-2 p-2 rounded-lg bg-background">
                            <Check className="w-3.5 h-3.5 text-accent mt-0.5 flex-shrink-0" />
                            <span>Stratégie détaillée étape par étape</span>
                          </div>
                          <div className="flex items-start gap-2 p-2 rounded-lg bg-background">
                            <Check className="w-3.5 h-3.5 text-accent mt-0.5 flex-shrink-0" />
                            <span>Score de pertinence personnalisé</span>
                          </div>
                          <div className="flex items-start gap-2 p-2 rounded-lg bg-background">
                            <Check className="w-3.5 h-3.5 text-accent mt-0.5 flex-shrink-0" />
                            <span>Rapport PDF sécurisé</span>
                          </div>
                        </div>

                        {/* Options add-on */}
                        <div className="space-y-3">
                          <label className="flex items-start gap-3 p-3 sm:p-4 rounded-lg border border-border hover:border-accent/40 cursor-pointer transition-colors" data-testid="strategiia-analyse-premium-option">
                            <input type="checkbox" checked={analysePremium} onChange={e => setAnalysePremium(e.target.checked)} className="mt-1 accent-amber-500 flex-shrink-0 w-4 h-4" />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between gap-2">
                                <span className="text-sm font-medium">Relecture expert personnalisée</span>
                                <Badge className="bg-amber-500/10 text-amber-600 border-amber-500/20 text-[10px] flex-shrink-0 whitespace-nowrap">+29€</Badge>
                              </div>
                              <p className="text-xs text-muted-foreground mt-1">Rapport relu et enrichi par notre expert — retour sous 24h à 48h ouvrées</p>
                              {analysePremium && (
                                <div className="mt-2 p-2 rounded-md bg-amber-50 border border-amber-200/50">
                                  <p className="text-[11px] text-amber-700 leading-relaxed">
                                    <strong>Intervention humaine réelle</strong> — Votre rapport sera relu, enrichi et validé par un expert avant envoi. Vous recevrez la version finalisée par email sous 24h à 48h ouvrées.
                                  </p>
                                </div>
                              )}
                            </div>
                          </label>
                          <label className="block p-3 sm:p-4 rounded-lg border border-border hover:border-accent/40 cursor-pointer transition-colors" data-testid="strategiia-premium-pdf-option">
                            <div className="flex items-start gap-3">
                              <input type="checkbox" checked={premiumPdf} onChange={e => setPremiumPdf(e.target.checked)} className="mt-1 accent-accent flex-shrink-0 w-4 h-4" />
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between gap-2">
                                  <div className="flex items-center gap-1.5 min-w-0">
                                    <Crown className="w-4 h-4 text-accent flex-shrink-0" />
                                    <span className="text-sm font-medium">Version professionnelle PDF</span>
                                  </div>
                                  <Badge className="bg-accent/10 text-accent border-accent/20 text-[10px] flex-shrink-0 whitespace-nowrap">+19€</Badge>
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">Sans filigrane, pour transmission à un professionnel</p>
                              </div>
                            </div>
                            {premiumPdf && (
                              <div className="mt-3 flex justify-center">
                                <PdfCoverPreview reportType="StrategiIA" />
                              </div>
                            )}
                          </label>
                        </div>

                        <Button onClick={handlePayForPremium} className="w-full rounded-lg gap-2 bg-accent hover:bg-accent/90 text-base py-5" data-testid="strategiia-buy-premium">
                          {isAdminMode ? (
                            <><Shield className="w-4 h-4" /> Tester en mode admin — {29 + (premiumPdf ? 19 : 0) + (analysePremium ? 29 : 0)}€ (bypass)</>
                          ) : (
                            <><CreditCard className="w-4 h-4" /> Obtenir le rapport complet — {29 + (premiumPdf ? 19 : 0) + (analysePremium ? 29 : 0)}€</>
                          )}
                        </Button>
                        <p className="text-[10px] text-muted-foreground text-center">
                          {isAdminMode ? "Mode Admin : aucun paiement réel ne sera effectué." : "Paiement sécurisé par Stripe. Satisfaction garantie."}
                        </p>
                      </CardContent>
                    </Card>

                    <div className="flex flex-wrap gap-2">
                      <button onClick={handleWhatsApp} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-[#25D366]/10 text-[#25D366] hover:bg-[#25D366]/20 transition-colors" data-testid="strategiia-share-whatsapp"><MessageSquare className="w-3.5 h-3.5" /> WhatsApp</button>
                      <button onClick={handleSMS} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-blue-500/10 text-blue-600 hover:bg-blue-500/20 transition-colors" data-testid="strategiia-share-sms"><Phone className="w-3.5 h-3.5" /> SMS</button>
                      <button onClick={handleShareEmail} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-accent/10 text-accent hover:bg-accent/20 transition-colors" data-testid="strategiia-share-email"><Mail className="w-3.5 h-3.5" /> Email</button>
                      <button onClick={handleCopyLink} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-muted hover:bg-muted/80 transition-colors" data-testid="strategiia-share-copy">{copied ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}{copied ? 'Copié !' : 'Copier'}</button>
                    </div>
                    <Button variant="ghost" onClick={handleReset} className="w-full gap-2 text-sm" data-testid="strategiia-new-analysis">Nouvelle analyse</Button>
                  </div>
                )}

                {/* ═══ PALIER 3 : PREMIUM — Contenu complet + exclusivités ═══ */}
                {step === 'premium' && (
                  <div className="space-y-4" data-testid="strategiia-premium-result">
                    <div className="flex items-center gap-2 mb-2">
                      <Crown className="w-5 h-5 text-accent" />
                      <h3 className="font-semibold">Rapport complet StratégiIA</h3>
                      <Badge className="bg-accent/10 text-accent border-accent/20 text-xs">Premium</Badge>
                    </div>

                    {/* Relevance Score Card — Exclusive premium */}
                    {scoreData && scoreData.score !== null && (
                      <Card className="border-accent/20 bg-gradient-to-r from-accent/5 to-transparent" data-testid="relevance-score-card">
                        <CardContent className="p-4">
                          <div className="flex items-start gap-4">
                            <div className="flex-shrink-0 w-16 h-16 rounded-xl bg-foreground flex flex-col items-center justify-center" data-testid="relevance-score-value">
                              <span className="text-2xl font-bold text-accent">{scoreData.score}</span>
                              <span className="text-[9px] text-primary-foreground/60 uppercase tracking-wider">/100</span>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <Target className="w-4 h-4 text-accent" />
                                <span className="text-sm font-semibold">Score de pertinence personnalisé</span>
                                <Badge variant="outline" className={`text-[10px] ${scoreData.confidence === 'high' ? 'border-green-400 text-green-600' : scoreData.confidence === 'medium' ? 'border-yellow-400 text-yellow-600' : 'border-orange-400 text-orange-600'}`}>
                                  {scoreData.confidence === 'high' ? 'Fiabilité haute' : scoreData.confidence === 'medium' ? 'Fiabilité moyenne' : 'Fiabilité limitée'}
                                </Badge>
                              </div>
                              <p className="text-xs text-muted-foreground">{scoreData.message}</p>
                              {scoreData.distribution && (scoreData.distribution.favorable + scoreData.distribution.defavorable) > 0 && (
                                <div className="mt-2">
                                  <div className="flex h-2 rounded-full overflow-hidden bg-muted">
                                    {scoreData.distribution.favorable > 0 && <div className="bg-green-500 transition-all" style={{width: `${(scoreData.distribution.favorable / scoreData.total_cases) * 100}%`}} />}
                                    {scoreData.distribution.en_cours > 0 && <div className="bg-yellow-400 transition-all" style={{width: `${(scoreData.distribution.en_cours / scoreData.total_cases) * 100}%`}} />}
                                    {scoreData.distribution.defavorable > 0 && <div className="bg-red-400 transition-all" style={{width: `${(scoreData.distribution.defavorable / scoreData.total_cases) * 100}%`}} />}
                                  </div>
                                  <div className="flex justify-between mt-1 text-[10px] text-muted-foreground">
                                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500 inline-block" />{scoreData.distribution.favorable} favorable{scoreData.distribution.favorable > 1 ? 's' : ''}</span>
                                    {scoreData.distribution.en_cours > 0 && <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-400 inline-block" />{scoreData.distribution.en_cours} en cours</span>}
                                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-400 inline-block" />{scoreData.distribution.defavorable} défavorable{scoreData.distribution.defavorable > 1 ? 's' : ''}</span>
                                  </div>
                                </div>
                              )}
                              {scoreData.top_strategies && scoreData.top_strategies.length > 0 && (
                                <div className="mt-2">
                                  <p className="text-[10px] font-medium text-muted-foreground mb-1">Stratégies favorables :</p>
                                  <div className="flex flex-wrap gap-1">
                                    {scoreData.top_strategies.map((s, i) => (
                                      <Badge key={i} variant="outline" className="text-[10px] bg-green-50 border-green-200 text-green-700">{s.strategie} ({s.count})</Badge>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    <PremiumAnalysisRenderer markdown={premiumResult} testIdPrefix="strategiia-premium-section" />
                    <Card className="border-accent/20">
                      <CardContent className="p-4 flex items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                          <FileText className="w-6 h-6 text-accent" />
                          <div>
                            <p className="font-medium text-sm">Rapport PDF sécurisé</p>
                            <p className="text-xs text-muted-foreground">{premiumPdf ? 'Version professionnelle sans filigrane' : 'Avec filigrane de protection'}</p>
                          </div>
                        </div>
                        <Button onClick={handleDownloadPDF} size="sm" className="gap-1.5 rounded-lg" disabled={pdfLoading} data-testid="strategiia-download-pdf">
                          {pdfLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />} PDF
                        </Button>
                      </CardContent>
                    </Card>
                    <div className="p-3 rounded-lg bg-yellow-50 border border-yellow-200/50">
                      <p className="text-xs text-yellow-700 flex items-start gap-2"><AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" /><strong>Outil d'aide à la décision — Les résultats sont indicatifs et ne constituent pas un conseil juridique.</strong></p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <button onClick={handleWhatsApp} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-[#25D366]/10 text-[#25D366] hover:bg-[#25D366]/20 transition-colors"><MessageSquare className="w-3.5 h-3.5" /> WhatsApp</button>
                      <button onClick={handleSMS} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-blue-500/10 text-blue-600 hover:bg-blue-500/20 transition-colors"><Phone className="w-3.5 h-3.5" /> SMS</button>
                      <button onClick={handleShareEmail} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-accent/10 text-accent hover:bg-accent/20 transition-colors"><Mail className="w-3.5 h-3.5" /> Email</button>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <a href="/agenda"><Button className="w-full rounded-lg gap-2" size="sm" data-testid="strategiia-rdv">Prendre rendez-vous <ArrowRight className="w-3.5 h-3.5" /></Button></a>
                      <Button variant="ghost" onClick={handleReset} className="w-full gap-2 text-sm" data-testid="strategiia-new-premium">Nouvelle analyse</Button>
                    </div>
                  </div>
                )}

                {/* ═══ EN ATTENTE DE RELECTURE EXPERT ═══ */}
                {step === 'relecture_attente' && (
                  <div className="space-y-5 py-4" data-testid="strategiia-relecture-attente">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Clock className="w-8 h-8 text-amber-600" />
                      </div>
                      <h3 className="text-lg font-semibold mb-2">Votre dossier a bien été transmis</h3>
                      <Badge className="bg-amber-500/10 text-amber-600 border-amber-500/20 text-xs px-3 py-1">En attente de relecture expert</Badge>
                    </div>

                    <Card className="border-amber-200/50 bg-amber-50/30">
                      <CardContent className="p-5 space-y-4">
                        <div className="space-y-3 text-sm text-foreground/80">
                          <div className="flex items-start gap-3">
                            <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                            <span>Votre demande de <strong>relecture expert personnalisée</strong> a bien été prise en compte.</span>
                          </div>
                          <div className="flex items-start gap-3">
                            <User className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />
                            <span>Un expert va personnellement relire, enrichir et valider votre rapport.</span>
                          </div>
                          <div className="flex items-start gap-3">
                            <Clock className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                            <span>Retour estimé : <strong>24h à 48h ouvrées</strong>.</span>
                          </div>
                          <div className="flex items-start gap-3">
                            <Mail className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                            <span>Vous recevrez votre document finalisé directement par email.</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <div className="p-3 rounded-lg bg-accent/5 border border-accent/20 text-center">
                      <p className="text-xs text-foreground/70 italic">
                        "Vous n'êtes plus seul(e) face à votre situation.<br/>Désormais, Stratégie & Expertise Santé devient votre bouclier."
                      </p>
                    </div>

                    <div className="space-y-2">
                      <a href="/agenda" className="block">
                        <Button className="w-full rounded-lg gap-2" size="sm" data-testid="relecture-attente-rdv">
                          <Phone className="w-4 h-4" /> Prendre rendez-vous en attendant
                        </Button>
                      </a>
                      <Button variant="ghost" onClick={handleClose} className="w-full gap-2 text-sm" data-testid="relecture-attente-close">
                        Fermer
                      </Button>
                    </div>
                  </div>
                )}


                {/* QUOTA EXCEEDED */}
                {step === 'quota_exceeded' && (
                  <div className="space-y-5 text-center py-4" data-testid="strategiia-quota-exceeded">
                    <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto">
                      <Lock className="w-8 h-8 text-amber-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-2">Quota atteint</h3>
                      <p className="text-sm text-muted-foreground">
                        Vous avez utilisé vos <strong>3 pré-analyses gratuites</strong> ce mois-ci.
                        Vos analyses se renouvellent le 1er du mois prochain.
                      </p>
                    </div>
                    <div className="space-y-3">
                      <Link to="/dossier-express" onClick={handleClose}>
                        <Button className="w-full rounded-lg gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold" data-testid="strategiia-quota-dossier-express">
                          <FileText className="w-4 h-4" /> Dossier Express IA — Rapport complet 97€
                        </Button>
                      </Link>
                      <Link to="/tarifs" onClick={handleClose}>
                        <Button variant="outline" className="w-full rounded-lg gap-2 mt-2" data-testid="strategiia-quota-tarifs">
                          <ArrowRight className="w-4 h-4" /> Voir toutes nos prestations
                        </Button>
                      </Link>
                      <Link to="/agenda" onClick={handleClose}>
                        <Button variant="ghost" className="w-full rounded-lg gap-2 mt-2 text-sm" data-testid="strategiia-quota-rdv">
                          <Phone className="w-4 h-4" /> Réserver un appel gratuit
                        </Button>
                      </Link>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Première consultation toujours gratuite (10 min) et sans engagement.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
