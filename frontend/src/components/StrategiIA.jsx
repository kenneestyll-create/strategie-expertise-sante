import { useState, useCallback, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import {
  X, Brain, Send, Loader2, FileText, Download, Lock,
  MessageSquare, Phone, Mail, Share2, Copy, Check,
  AlertTriangle, CreditCard, ArrowRight, Sparkles, Gauge
} from 'lucide-react';
import axios from 'axios';
import jsPDF from 'jspdf';

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
  { value: 'autre', label: "Autre" },
];

const generatePremiumPDF = (analysis, formData) => {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' });
  const w = doc.internal.pageSize.getWidth();
  const margin = 18;
  const contentW = w - margin * 2;
  const accent = [185, 78, 72];
  const dark = [47, 44, 40];
  const bg = [249, 247, 242];

  doc.setFillColor(...accent);
  doc.rect(0, 0, w, 42, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text("Stratégie & Expertise Santé", margin, 16);
  doc.setFontSize(14);
  doc.text("StratégiIA — Rapport d'analyse", margin, 26);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.text(new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }), w - margin, 16, { align: 'right' });

  let y = 50;
  doc.setFillColor(...bg);
  doc.roundedRect(margin, y, contentW, 20, 3, 3, 'F');
  doc.setTextColor(...dark);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  const typeLabel = TYPES_DOSSIER.find(t => t.value === formData.type_dossier)?.label || formData.type_dossier;
  const regimeLabel = REGIMES.find(r => r.value === formData.regime)?.label || formData.regime;
  doc.text(`Type de dossier : ${typeLabel}`, margin + 5, y + 8);
  doc.text(`Régime : ${regimeLabel}`, margin + 5, y + 15);
  y += 28;

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9.5);
  for (const line of analysis.split('\n')) {
    if (y > 270) { doc.addPage(); y = 20; }
    if (line.startsWith('## ')) {
      y += 4;
      doc.setFillColor(...accent);
      doc.rect(margin, y - 1, 3, 7, 'F');
      doc.setTextColor(...accent);
      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.text(line.replace('## ', ''), margin + 6, y + 4);
      doc.setFontSize(9.5);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...dark);
      y += 10;
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      const wrapped = doc.splitTextToSize(`• ${line.slice(2)}`, contentW - 8);
      doc.text(wrapped, margin + 5, y);
      y += wrapped.length * 4.5 + 1.5;
    } else if (line.trim()) {
      const wrapped = doc.splitTextToSize(line, contentW);
      doc.text(wrapped, margin, y);
      y += wrapped.length * 4.5 + 1;
    } else { y += 3; }
  }

  y += 6;
  if (y > 260) { doc.addPage(); y = 20; }
  doc.setFillColor(255, 243, 205);
  doc.roundedRect(margin, y, contentW, 14, 2, 2, 'F');
  doc.setTextColor(180, 120, 30);
  doc.setFontSize(7.5);
  doc.setFont('helvetica', 'bold');
  doc.text("OUTIL D'AIDE À LA DÉCISION", margin + 4, y + 5);
  doc.setFont('helvetica', 'normal');
  doc.text("Les résultats sont indicatifs et ne constituent pas un conseil juridique.", margin + 4, y + 10);

  doc.setFillColor(...dark);
  doc.rect(0, 277, w, 20, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  doc.text("StratégiIA — Stratégie & Expertise Santé", margin, 285);
  return doc;
};

export const StrategiIA = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState('email'); // email | form | loading | basic | premium | quota_exceeded
  const [typeDossier, setTypeDossier] = useState('');
  const [regime, setRegime] = useState('');
  const [situation, setSituation] = useState('');
  const [email, setEmail] = useState('');
  const [basicResult, setBasicResult] = useState('');
  const [premiumResult, setPremiumResult] = useState('');
  const [casesFound, setCasesFound] = useState(0);
  const [copied, setCopied] = useState(false);
  const [remaining, setRemaining] = useState(null);

  const checkQuota = async (emailToCheck) => {
    if (!emailToCheck || !emailToCheck.includes('@')) return;
    try {
      const { data } = await axios.get(`${API}/strategiia/quota/${encodeURIComponent(emailToCheck)}`);
      setRemaining(data.remaining);
      if (data.remaining <= 0) {
        setStep('quota_exceeded');
      } else {
        setStep('form');
      }
    } catch {
      setStep('form');
      setRemaining(3);
    }
  };

  const handleEmailSubmit = () => {
    if (!email.trim() || !email.includes('@')) {
      toast.error("Veuillez entrer un email valide");
      return;
    }
    checkQuota(email.trim().toLowerCase());
  };

  const handleAnalyzeBasic = async () => {
    if (!typeDossier || !situation.trim()) {
      toast.error("Veuillez remplir le type de dossier et la description");
      return;
    }
    setStep('loading');
    try {
      const { data } = await axios.post(`${API}/strategiia/analyze`, {
        type_dossier: typeDossier, regime, situation, premium: false, email: email.trim().toLowerCase()
      });
      if (data.quota_exceeded) {
        setRemaining(0);
        setStep('quota_exceeded');
        return;
      }
      setBasicResult(data.analysis);
      setCasesFound(data.cases_found);
      setRemaining(data.remaining);
      setStep('basic');
    } catch (e) {
      toast.error("Erreur lors de l'analyse. Réessayez.");
      setStep('form');
    }
  };

  const handleUpgradePremium = async () => {
    setStep('loading');
    try {
      const { data } = await axios.post(`${API}/strategiia/analyze`, {
        type_dossier: typeDossier, regime, situation, premium: true, email
      });
      setPremiumResult(data.analysis);
      setCasesFound(data.cases_found);
      setStep('premium');
    } catch {
      toast.error("Erreur lors de l'analyse premium.");
      setStep('basic');
    }
  };

  const handlePayForPremium = async () => {
    try {
      const { data } = await axios.post(`${API}/strategiia/checkout`, {
        origin_url: window.location.origin, email,
        context: `${typeDossier} - ${situation.slice(0, 100)}`
      });
      if (data.url) window.location.href = data.url;
    } catch { toast.error("Erreur de paiement. Réessayez."); }
  };

  const handleDownloadPDF = useCallback(() => {
    const doc = generatePremiumPDF(premiumResult, { type_dossier: typeDossier, regime });
    doc.save('strategiia-rapport-complet.pdf');
    toast.success("Rapport PDF téléchargé !");
  }, [premiumResult, typeDossier, regime]);

  const getShareText = () => `J'ai analysé mon dossier avec StratégiIA sur Stratégie & Expertise Santé. Analysez le vôtre :`;
  const getShareUrl = () => `${window.location.origin}/simulateur`;
  const handleWhatsApp = () => window.open(`https://wa.me/?text=${encodeURIComponent(getShareText() + ' ' + getShareUrl())}`, '_blank');
  const handleSMS = () => window.open(`sms:?body=${encodeURIComponent(getShareText() + ' ' + getShareUrl())}`, '_blank');
  const handleShareEmail = () => window.open(`mailto:?subject=${encodeURIComponent('StratégiIA — Analyse de dossier')}&body=${encodeURIComponent(getShareText() + '\n\n' + getShareUrl())}`, '_blank');
  const handleCopyLink = () => { navigator.clipboard.writeText(getShareUrl()); setCopied(true); setTimeout(() => setCopied(false), 2000); };

  const handleClose = () => setIsOpen(false);
  const handleReset = () => {
    setStep(email ? 'form' : 'email');
    setTypeDossier(''); setRegime(''); setSituation('');
    setBasicResult(''); setPremiumResult('');
    if (email) checkQuota(email);
  };

  // Quota badge component
  const QuotaBadge = () => {
    if (remaining === null) return null;
    const color = remaining > 1 ? 'bg-green-100 text-green-700 border-green-200' : remaining === 1 ? 'bg-amber-100 text-amber-700 border-amber-200' : 'bg-red-100 text-red-700 border-red-200';
    return (
      <Badge className={`${color} text-xs gap-1`} data-testid="strategiia-quota-badge">
        <Gauge className="w-3 h-3" />
        {remaining > 0 ? `${remaining} analyse${remaining > 1 ? 's' : ''} gratuite${remaining > 1 ? 's' : ''} restante${remaining > 1 ? 's' : ''}` : 'Quota épuisé'}
      </Badge>
    );
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-3.5 py-1.5 rounded-full text-sm font-medium bg-accent/10 text-accent hover:bg-accent/20 border border-accent/20 transition-all hover:scale-[1.02]"
        data-testid="strategiia-trigger"
      >
        <Brain className="w-4 h-4" />
        <span className="hidden xl:inline">StratégiIA</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0" style={{ zIndex: 'var(--z-modal)' }}>
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={handleClose} />
          <div className="relative max-w-2xl mx-auto mt-[5vh] mx-4 max-h-[90vh] flex flex-col">
            <div className="bg-background border border-border rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]" data-testid="strategiia-modal">
              {/* Header */}
              <div className="flex items-center justify-between p-5 bg-foreground text-primary-foreground flex-shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-accent rounded-xl flex items-center justify-center">
                    <Brain className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-base flex items-center gap-2">
                      StratégiIA
                      <Badge variant="secondary" className="text-[10px] px-1.5 py-0 bg-accent/20 text-accent border-0">Exclusif</Badge>
                    </h3>
                    <p className="text-xs text-primary-foreground/60">Analyse stratégique IA de votre dossier</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <QuotaBadge />
                  <button onClick={handleClose} className="p-2 hover:bg-white/10 rounded-lg transition-colors" aria-label="Fermer">
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="overflow-y-auto flex-1 p-5">

                {/* EMAIL STEP */}
                {step === 'email' && (
                  <div className="space-y-5" data-testid="strategiia-email-step">
                    <div className="text-center py-4">
                      <Brain className="w-12 h-12 text-accent mx-auto mb-3" />
                      <h3 className="text-lg font-semibold mb-2">Analysez votre dossier gratuitement</h3>
                      <p className="text-sm text-muted-foreground">3 analyses gratuites par mois. Inscrivez votre email pour commencer.</p>
                    </div>
                    <div className="space-y-2">
                      <Label className="font-medium">Votre email *</Label>
                      <Input
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        placeholder="votre@email.fr"
                        type="email"
                        data-testid="strategiia-email-input"
                        onKeyDown={e => e.key === 'Enter' && handleEmailSubmit()}
                      />
                    </div>
                    <Button onClick={handleEmailSubmit} className="w-full rounded-lg gap-2" disabled={!email.includes('@')} data-testid="strategiia-email-submit">
                      <ArrowRight className="w-4 h-4" /> Continuer
                    </Button>
                    <p className="text-[11px] text-muted-foreground text-center">
                      Votre email nous permet de vous identifier et de sauvegarder vos analyses.
                    </p>
                  </div>
                )}

                {/* FORM STEP */}
                {step === 'form' && (
                  <div className="space-y-4" data-testid="strategiia-form">
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
                    <Button onClick={handleAnalyzeBasic} className="w-full rounded-lg gap-2" disabled={!typeDossier || !situation.trim()} data-testid="strategiia-analyze-button">
                      <Brain className="w-4 h-4" /> Analyser mon dossier gratuitement
                    </Button>
                    <p className="text-[11px] text-muted-foreground text-center flex items-center justify-center gap-1">
                      <AlertTriangle className="w-3 h-3" />
                      Outil d'aide à la décision — Les résultats ne constituent pas un conseil juridique
                    </p>
                  </div>
                )}

                {/* LOADING */}
                {step === 'loading' && (
                  <div className="py-16 text-center" data-testid="strategiia-loading">
                    <Loader2 className="w-10 h-10 text-accent animate-spin mx-auto mb-4" />
                    <p className="font-semibold">StratégiIA analyse votre dossier...</p>
                    <p className="text-sm text-muted-foreground mt-2">Comparaison avec les jurisprudences et statistiques en cours</p>
                  </div>
                )}

                {/* BASIC RESULT */}
                {step === 'basic' && (
                  <div className="space-y-4" data-testid="strategiia-basic-result">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-5 h-5 text-accent" />
                      <h3 className="font-semibold">Analyse gratuite</h3>
                      {casesFound > 0 && <Badge variant="outline" className="text-xs">{casesFound} cas similaire{casesFound > 1 ? 's' : ''}</Badge>}
                    </div>
                    <div className="prose prose-sm max-w-none text-sm leading-relaxed whitespace-pre-wrap bg-muted/30 p-4 rounded-xl border border-border" data-testid="strategiia-basic-text">
                      {basicResult}
                    </div>
                    <div className="p-3 rounded-lg bg-yellow-50 border border-yellow-200/50">
                      <p className="text-xs text-yellow-700 flex items-start gap-2">
                        <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                        <strong>Outil d'aide à la décision — Les résultats sont indicatifs et ne constituent pas un conseil juridique.</strong>
                      </p>
                    </div>
                    <Card className="border-accent/30 bg-accent/5">
                      <CardContent className="p-4 space-y-3">
                        <div className="flex items-center gap-2">
                          <Lock className="w-5 h-5 text-accent" />
                          <div>
                            <h4 className="font-semibold text-sm">Rapport complet StratégiIA — 29€</h4>
                            <p className="text-xs text-muted-foreground">Jurisprudences détaillées, stratégie complète, score de pertinence, PDF professionnel</p>
                          </div>
                        </div>
                        <Button onClick={handlePayForPremium} className="w-full rounded-lg gap-2 bg-accent hover:bg-accent/90" data-testid="strategiia-buy-premium">
                          <CreditCard className="w-4 h-4" /> Obtenir le rapport complet — 29€
                        </Button>
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

                {/* PREMIUM RESULT */}
                {step === 'premium' && (
                  <div className="space-y-4" data-testid="strategiia-premium-result">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-5 h-5 text-accent" />
                      <h3 className="font-semibold">Rapport complet StratégiIA</h3>
                      <Badge className="bg-accent/10 text-accent border-accent/20 text-xs">Premium</Badge>
                    </div>
                    <div className="prose prose-sm max-w-none text-sm leading-relaxed whitespace-pre-wrap bg-muted/30 p-4 rounded-xl border border-border" data-testid="strategiia-premium-text">{premiumResult}</div>
                    <Card className="border-accent/20">
                      <CardContent className="p-4 flex items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                          <FileText className="w-6 h-6 text-accent" />
                          <div><p className="font-medium text-sm">Rapport PDF</p><p className="text-xs text-muted-foreground">Téléchargez votre analyse complète</p></div>
                        </div>
                        <Button onClick={handleDownloadPDF} size="sm" className="gap-1.5 rounded-lg" data-testid="strategiia-download-pdf"><Download className="w-3.5 h-3.5" /> PDF</Button>
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

                {/* QUOTA EXCEEDED */}
                {step === 'quota_exceeded' && (
                  <div className="space-y-5 text-center py-4" data-testid="strategiia-quota-exceeded">
                    <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto">
                      <Lock className="w-8 h-8 text-amber-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-2">Quota atteint</h3>
                      <p className="text-sm text-muted-foreground">
                        Vous avez utilisé vos <strong>3 analyses gratuites</strong> ce mois-ci.
                        Vos analyses se renouvellent le 1er du mois prochain.
                      </p>
                    </div>
                    <div className="space-y-3">
                      <Link to="/dossier-express" onClick={handleClose}>
                        <Button className="w-full rounded-lg gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold" data-testid="strategiia-quota-dossier-express">
                          <FileText className="w-4 h-4" /> Dossier Express — Rapport complet 97€
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
                      Premier échange toujours gratuit et sans engagement.
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
