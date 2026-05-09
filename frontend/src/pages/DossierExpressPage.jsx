import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import {
  FileSearch, Upload, Mail, Clock, Shield, CheckCircle,
  ArrowRight, Loader2, FileText, Zap, Brain, AlertTriangle,
  ChevronRight, Sparkles, CreditCard, Crown, Star,
  Users, Lock, RefreshCw, ShieldCheck, Award, TrendingUp,
  ChevronDown
} from 'lucide-react';
import axios from 'axios';
import { SEO } from '@/components/SEO';
import { useReveal, useRevealChildren } from '@/hooks/useReveal';
import { DataConsentBox } from '@/components/DataConsentBox';
import { PdfCoverPreview } from '@/components/PdfCoverPreview';
import { DocumentUploader } from '@/components/DocumentUploader';
import { useAdminTest } from '@/components/AdminTestBanner';
import { useVip } from '@/context/VipContext';

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
  "Régimes spéciaux RATP / SNCF",
  "Autre"
];

const GARANTIES_ASSURANCE_DE = [
  "ITT — Incapacité Temporaire Totale",
  "ITP — Incapacité Temporaire Partielle",
  "IPT — Invalidité Permanente Totale",
  "IPP — Invalidité Permanente Partielle",
  "PTIA — Perte Totale et Irréversible d'Autonomie",
  "PE — Perte d'Emploi",
  "Décès",
  "Autre / Je ne sais pas",
];

const TYPES_EXPERTISE_DE = [
  "Expertise amiable",
  "Expertise judiciaire",
  "Contre-expertise",
  "Expertise CPAM (contrôle médical)",
  "Expertise employeur",
  "Autre",
];

const TYPES_MDPH_DE = [
  "AAH refusée",
  "PCH refusée",
  "RQTH refusée",
  "Dossier complet refusé",
  "Carte mobilité inclusion refusée",
  "Orientation refusée",
  "Renouvellement refusé",
  "Autre",
];

const TYPES_CONTESTATION_IPP_DE = [
  "Taux IPP sous-évalué",
  "Taux IPP refusé",
  "Demande de révision de taux",
  "Contestation après expertise",
  "Autre",
];

// Mapping contextuel Dossier Express : sous-chaîne du type de dossier → config
const getContextDE = (type) => {
  const t = (type || '').toLowerCase();
  if (t.includes('assurance')) return { label: "Type de garantie concernée", placeholder: "Sélectionnez la garantie...", options: GARANTIES_ASSURANCE_DE };
  if (t.includes('mdph') || t.includes('aah')) return { label: "Type de demande MDPH", placeholder: "Sélectionnez la demande...", options: TYPES_MDPH_DE };
  if (t.includes('expertise')) return { label: "Type d'expertise", placeholder: "Sélectionnez le type d'expertise...", options: TYPES_EXPERTISE_DE };
  if (t.includes('contestation') || t.includes('ipp')) return { label: "Objet de la contestation", placeholder: "Sélectionnez...", options: TYPES_CONTESTATION_IPP_DE };
  return null; // fallback → Régime standard
};

/* ── Typologie des dossiers accompagnés (aucun témoignage nominatif — conformité RGPD/consumer law) ── */
const TYPOLOGIE = [
  { label: "Accidents du travail & AVP", type: "AT / IPP", detail: "Analyse des taux d'IPP acquis, identification des leviers de contestation, stratégie de consolidation." },
  { label: "Maladies professionnelles", type: "MP / CPAM", detail: "Constitution et renforcement des dossiers, reconnaissance hors tableau, contentieux tribunal administratif." },
  { label: "MDPH — prestations complexes", type: "AAH / PCH / RQTH", detail: "Profils lourds : transplantation, polyhandicap sensoriel, obésité à impact fonctionnel, restrictions poste de travail." },
];

/* ── Trust Badge Component ── */
const TrustBadge = ({ icon: Icon, label }) => (
  <div className="flex items-center gap-2 text-xs text-muted-foreground">
    <Icon className="w-3.5 h-3.5 text-accent/70" strokeWidth={1.5} />
    <span>{label}</span>
  </div>
);

/* ── Step Indicator ── */
const StepIndicator = ({ currentStep }) => {
  const steps = [
    { id: 1, label: "Informations" },
    { id: 2, label: "Paiement" },
    { id: 3, label: "Analyse" },
  ];
  return (
    <div className="flex items-center justify-center gap-2 mb-8" data-testid="form-step-indicator">
      {steps.map((s, i) => (
        <div key={s.id} className="flex items-center gap-2">
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all ${
            currentStep === s.id ? 'bg-accent text-white' :
            currentStep > s.id ? 'bg-accent/15 text-accent' : 'bg-muted text-muted-foreground'
          }`}>
            {currentStep > s.id ? <CheckCircle className="w-3 h-3" /> : <span>{s.id}</span>}
            <span className="hidden sm:inline">{s.label}</span>
          </div>
          {i < steps.length - 1 && <div className={`w-8 h-px ${currentStep > s.id ? 'bg-accent' : 'bg-border'}`} />}
        </div>
      ))}
    </div>
  );
};

/* ── Value Sidebar for Form ── */
const ValueReminder = ({ weeklyCount }) => (
  <div className="space-y-5" data-testid="form-value-sidebar">
    <Card className="bg-accent/[0.03]" style={{outline: '1px solid rgba(201,168,76,0.3)', outlineOffset: '-1px'}}>
      <CardContent className="p-5">
        <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <FileText className="w-4 h-4 text-accent" />
          Votre rapport contient
        </h4>
        <ul className="space-y-2.5">
          {[
            "Analyse complète de votre situation",
            "Cadre juridique et jurisprudences applicables",
            "Vos droits identifiés avec explications",
            "Points de vigilance et pièces manquantes",
            "Stratégie recommandée étape par étape",
            "5 actions prioritaires immédiates"
          ].map((item, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
              <CheckCircle className="w-3.5 h-3.5 text-accent flex-shrink-0 mt-0.5" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
    <Card className="border-border">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span className="text-xs font-medium text-emerald-700">Paiement 100% sécurisé</span>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-accent" />
          <span className="text-xs text-muted-foreground">Rapport livré sous 2h par email</span>
        </div>
        <div className="flex items-center gap-2">
          <RefreshCw className="w-4 h-4 text-blue-500" />
          <span className="text-xs text-muted-foreground">Satisfait ou analyse complémentaire offerte</span>
        </div>
        {weeklyCount > 0 && (
          <div className="flex items-center gap-2 pt-2 border-t border-border">
            <Users className="w-4 h-4 text-amber-500" />
            <span className="text-xs text-amber-700 font-medium">{weeklyCount} dossiers accompagnés à ce jour</span>
          </div>
        )}
      </CardContent>
    </Card>
  </div>
);

const dossierFaqData = [
  {
    question: "Combien de temps faut-il pour recevoir le rapport ?",
    answer: "Le rapport est livré par email sous 2 heures après le paiement et la soumission de vos informations. Il est envoyé au format PDF directement dans votre boîte mail."
  },
  {
    question: "Le Dossier Express remplace-t-il un avocat ou un médecin ?",
    answer: "Non. Le Dossier Express IA fournit une analyse documentaire et stratégique. Il ne constitue pas un avis juridique, médical ou une expertise officielle. Il vous aide à comprendre votre situation et à préparer vos démarches."
  },
  {
    question: "Quels types de dossiers peuvent être analysés ?",
    answer: "Le service couvre les accidents du travail, les maladies professionnelles, les litiges avec les assurances ou la protection juridique, et les demandes MDPH/AAH. Chaque analyse est personnalisée à votre situation spécifique."
  }
];

const DossierExpressFAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);

  useEffect(() => {
    document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
      try { if (JSON.parse(s.textContent)['@type'] === 'FAQPage') s.remove(); } catch {}
    });
    const script = document.createElement('script');
    script.id = 'dossier-faq-schema';
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": dossierFaqData.map(f => ({
        "@type": "Question",
        "name": f.question,
        "acceptedAnswer": { "@type": "Answer", "text": f.answer }
      }))
    });
    document.head.appendChild(script);
    return () => { const el = document.getElementById('dossier-faq-schema'); if (el) el.remove(); };
  }, []);

  return (
    <section className="section-padding bg-card" data-testid="dossier-faq">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-lg font-semibold mb-4">Questions fréquentes</h2>
        <div className="space-y-2">
          {dossierFaqData.map((faq, i) => (
            <div key={i} className="border border-border rounded-xl overflow-hidden">
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
                data-testid={`dossier-faq-${i}`}
              >
                <span className="font-medium text-sm text-foreground pr-4">{faq.question}</span>
                <ChevronDown className={`w-4 h-4 text-muted-foreground shrink-0 transition-transform ${openIndex === i ? 'rotate-180' : ''}`} />
              </button>
              {openIndex === i && (
                <div className="px-4 pb-4">
                  <p className="text-sm text-muted-foreground leading-relaxed">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export const DossierExpressPage = () => {
  const [searchParams] = useSearchParams();
  const [step, setStep] = useState('landing');
  const [loading, setLoading] = useState(false);
  const { isAdminMode, adminToken } = useAdminTest();
  const { isVip, vipName } = useVip();
  const [consent, setConsent] = useState(false);
  const [improvementOptout, setImprovementOptout] = useState(false);
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
  const [weeklyCount, setWeeklyCount] = useState(0);
  const [adminPaid, setAdminPaid] = useState(false);
  const [valueIdx, setValueIdx] = useState(0);
  const [elapsedSec, setElapsedSec] = useState(0);

  const featuresRef = useRevealChildren();
  const ctaBottomRef = useReveal();
  const testimonialsRef = useRevealChildren();

  // Fetch weekly count
  useEffect(() => {
    axios.get(`${API}/dossier-express/weekly-count`)
      .then(res => setWeeklyCount(res.data.count || 0))
      .catch(() => {});
  }, []);

  // Processing view: rotating value messages (only active during processing)
  useEffect(() => {
    if (step !== 'processing') return;
    const t = setInterval(() => setValueIdx(p => (p + 1) % 6), 12000);
    return () => clearInterval(t);
  }, [step]);

  // Processing view: elapsed time counter (reset when entering processing)
  useEffect(() => {
    if (step !== 'processing') { setElapsedSec(0); return; }
    const t = setInterval(() => setElapsedSec(p => p + 1), 1000);
    return () => clearInterval(t);
  }, [step]);

  useEffect(() => {
    const payment = searchParams.get('payment');
    const sessionId = searchParams.get('session_id');
    const stepParam = searchParams.get('step');
    if (stepParam === 'form') {
      setStep('form');
      window.history.replaceState({}, '', '/dossier-express');
    } else if (payment === 'success' && sessionId) {
      const savedForm = sessionStorage.getItem('dossier_express_form');
      if (savedForm) {
        const parsed = JSON.parse(savedForm);
        setForm(parsed);
        setStep('form');
        toast.success("Paiement confirmé ! Complétez votre dossier pour lancer l'analyse.");
      } else {
        setStep('form');
        toast.success("Paiement confirmé ! Complétez le formulaire ci-dessous.");
      }
      window.history.replaceState({}, '', '/dossier-express');
    } else if (payment === 'cancelled') {
      toast.error("Paiement annulé");
      window.history.replaceState({}, '', '/dossier-express');
    }
  }, [searchParams]);

  useEffect(() => {
    if (!dossierId || step !== 'processing') return;
    let pollErrors = 0;
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/dossier-express/status/${dossierId}`);
        pollErrors = 0;
        setPollStatus(res.data);
        if (res.data.status === 'completed') {
          setStep('success');
          clearInterval(interval);
          toast.success("Votre rapport est prêt ! Vérifiez votre email.");
        } else if (res.data.delivery_status === 'incident_technique') {
          // Incident detected — show reassuring fallback (still in processing view)
          setPollStatus(res.data);
        } else if (res.data.status === 'error') {
          clearInterval(interval);
          const errorMsg = res.data.error || "Une erreur est survenue lors de l'analyse.";
          if (errorMsg.toLowerCase().includes('budget')) {
            toast.error("Le service d'analyse nécessite un traitement complémentaire. Notre équipe a été notifiée. Vous serez contacté par email.", { duration: 10000 });
          } else {
            toast.error("Votre dossier est bien pris en charge. Un traitement complémentaire est en cours.", { duration: 8000 });
          }
          setStep('error');
        }
      } catch {
        pollErrors++;
        if (pollErrors >= 8) {
          toast.error("Connexion interrompue. Restez sur cette page, nous tentons de reconnecter automatiquement.");
          clearInterval(interval);
        }
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [dossierId, step]);

  const handleCheckout = async () => {
    if (!isAdminMode && !isVip && (!form.email || !form.name)) {
      toast.error("Veuillez renseigner votre nom et email");
      return;
    }
    // Admin bypass: skip Stripe, go directly to form
    if (isAdminMode && adminToken) {
      sessionStorage.setItem('dossier_express_form', JSON.stringify(form));
      sessionStorage.setItem('dossier_express_premium_pdf', premiumPdf ? '1' : '0');
      sessionStorage.setItem('dossier_express_admin_bypass', '1');
      setAdminPaid(true);
      toast.success("Mode Admin : paiement bypass — complétez le dossier puis lancez l'analyse.");
      return;
    }
    // VIP bypass: skip payment like admin
    if (isVip) {
      sessionStorage.setItem('dossier_express_form', JSON.stringify(form));
      sessionStorage.setItem('dossier_express_premium_pdf', premiumPdf ? '1' : '0');
      sessionStorage.setItem('dossier_express_admin_bypass', '1');
      setAdminPaid(true);
      toast.success(`Accès Partenaire VIP (${vipName}) : paiement offert.`);
      return;
    }
    sessionStorage.setItem('dossier_express_form', JSON.stringify(form));
    sessionStorage.setItem('dossier_express_premium_pdf', premiumPdf ? '1' : '0');
    sessionStorage.setItem('dossier_express_analyse_premium', analysePremium ? '1' : '0');
    setLoading(true);
    try {
      // === LAUNCH MODE CHECK ===
      try {
        const modeRes = await axios.get(`${API}/launch-mode`, { timeout: 5000 });
        if (modeRes.data?.mode === 'indisponible') {
          toast.error(modeRes.data.message || "Le service est temporairement suspendu pour maintenance programmee. Nous serons de retour tres prochainement.", { duration: 8000 });
          setLoading(false);
          return;
        }
      } catch { /* launch mode check non-blocking if endpoint fails */ }
      // === PRE-PAYMENT LLM HEALTH CHECK ===
      try {
        const healthRes = await axios.get(`${API}/health/llm`, { timeout: 15000 });
        if (!healthRes.data?.operational) {
          toast.error("Le service est momentanement indisponible pour finalisation technique. Merci de reessayer dans quelques instants.", { duration: 8000 });
          setLoading(false);
          return;
        }
      } catch {
        toast.error("Le service est momentanement indisponible pour finalisation technique. Merci de reessayer dans quelques instants.", { duration: 8000 });
        setLoading(false);
        return;
      }
      const res = await axios.post(`${API}/dossier-express/checkout`, {
        email: form.email,
        name: form.name,
        origin_url: window.location.origin,
        premium_pdf: premiumPdf,
        analyse_premium: analysePremium
      });
      window.location.href = res.data.url;
    } catch (err) {
      if (err.response?.status === 503) {
        toast.error("Le service est momentanement indisponible pour finalisation technique. Merci de reessayer dans quelques instants.", { duration: 8000 });
      } else {
        toast.error("Erreur lors du paiement. Veuillez reessayer.");
      }
      setLoading(false);
    }
  };

  const handleSubmitDossier = async () => {
    if (!form.situation.trim()) {
      toast.error("Veuillez décrire votre situation");
      return;
    }
    if (!isAdminMode && !form.email.trim()) {
      toast.error("Veuillez renseigner votre email");
      return;
    }
    setLoading(true);

    let documentsText = "";
    let documentDetails = [];
    let storedFiles = [];

    // Phase 1+2 UX — switch IMMEDIATELY to processing screen so the user sees rich progress
    // (steps timeline, segmented bar, rotating reassurance messages) instead of an opaque
    // "Envoi et analyse en cours…" with just a spinner during OCR extraction (60-180s).
    setPollStatus({ progress_step: 'extracting', files_count: files.length, documents_extracted: false });
    setStep('processing');
    window.scrollTo({ top: 0, behavior: 'smooth' });

    try {
      if (files.length > 0) {
        const hasLargeFiles = files.some(f => f.size > 5 * 1024 * 1024);
        const totalSize = files.reduce((s, f) => s + (f.size || 0), 0);
        if (hasLargeFiles) {
          toast.info("Fichiers volumineux détectés — upload fractionné sécurisé en cours...");
        } else if (totalSize > 2 * 1024 * 1024) {
          toast.info(`Envoi de ${files.length} document${files.length > 1 ? 's' : ''} — cela peut prendre quelques instants...`);
        } else {
          toast.info(`Lecture de ${files.length} document${files.length > 1 ? 's' : ''}...`);
        }
        const { extractTextFromFiles } = await import('@/utils/pdfExtractor');
        const onChunkProgress = (filename, uploaded, total) => {
          const pct = Math.round((uploaded / total) * 100);
          setPollStatus(prev => ({ ...prev, chunk_progress: `${filename}: ${pct}%` }));
        };
        // Listen for server-side extraction progress (Gemini Vision) — shows real-time elapsed estimate
        const handleUploadProgress = (event) => {
          const detail = event?.detail || {};
          if (detail.phase === 'extraction' && detail.message) {
            setPollStatus(prev => ({ ...prev, chunk_progress: detail.message }));
          }
        };
        if (typeof window !== 'undefined') window.addEventListener('upload-progress', handleUploadProgress);
        let extraction;
        try {
          extraction = await extractTextFromFiles(files, form.documents_text || '', onChunkProgress);
        } finally {
          if (typeof window !== 'undefined') window.removeEventListener('upload-progress', handleUploadProgress);
        }
        setPollStatus(prev => ({ ...prev, chunk_progress: null }));
        documentsText = extraction.combinedText;
        documentDetails = extraction.results || [];
        storedFiles = extraction.storedFiles || [];
        const extractedCount = extraction.extractedCount;
        if (extractedCount > 0) {
          toast.success(`${extractedCount}/${files.length} document${extractedCount > 1 ? 's' : ''} lu${extractedCount > 1 ? 's' : ''} avec succes`);
        } else if (form.documents_text) {
          toast.info("Contenu OCR des images inclus dans l'analyse");
        }
      } else if (form.documents_text) {
        documentsText = `--- Contenu extrait par OCR ---\n${form.documents_text}`;
      }
    } catch (fileErr) {
      console.error('File extraction error:', fileErr);
      const isTimeout = fileErr?.code === 'ECONNABORTED' || fileErr?.message?.includes('timeout');
      const isNetwork = !fileErr?.response && fileErr?.message?.includes('Network');
      if (isTimeout || isNetwork) {
        toast.error("L'envoi a pris trop de temps. Vérifiez votre connexion et réessayez.", { duration: 8000 });
      }
      if (form.documents_text) {
        documentsText = `--- Contenu extrait par OCR ---\n${form.documents_text}\n`;
      }
      for (const file of files) {
        documentsText += `\n--- ${file.name} (${file.type || 'inconnu'}, ${(file.size / 1024).toFixed(0)} Ko) ---\n[Extraction echouee]\n`;
      }
    }

    toast.info("Envoi de votre dossier pour analyse...");
    const isAdminBypass = isAdminMode && adminToken;
    try {
      const isPremium = sessionStorage.getItem('dossier_express_premium_pdf') === '1';
      const endpoint = isAdminBypass ? `${API}/dossier-express/admin-bypass` : `${API}/dossier-express/submit`;
      const payload = isAdminBypass ? {
        name: form.name, email: form.email, situation: form.situation,
        type_dossier: form.type_dossier, regime: form.regime,
        documents_text: documentsText, document_details: documentDetails,
        original_documents: storedFiles, premium_pdf: isPremium,
        improvement_optout: improvementOptout
      } : {
        session_id: searchParams.get('session_id') || '',
        email: form.email, name: form.name,
        situation: form.situation, type_dossier: form.type_dossier,
        regime: form.regime, documents_text: documentsText, document_details: documentDetails,
        original_documents: storedFiles, premium_pdf: isPremium,
        improvement_optout: improvementOptout
      };
      const headers = isAdminBypass ? { 'Authorization': `Bearer ${adminToken}` } : {};
      const res = await axios.post(endpoint, payload, { headers });
      setDossierId(res.data.dossier_id);
      // Already in 'processing' mode (set early at submit start). Just refresh poll status to enter the analysis steps.
      setPollStatus({ progress_step: 'uploading', files_count: files.length, documents_extracted: documentsText.length > 50 });
      sessionStorage.removeItem('dossier_express_form');
      sessionStorage.removeItem('dossier_express_premium_pdf');
      sessionStorage.removeItem('dossier_express_admin_bypass');
      if (isAdminBypass) toast.success("Dossier soumis — analyse IA en cours (mode admin).");
    } catch (err) {
      // Submission failed — revert from 'processing' back to 'form' so the user can retry.
      setStep('form');
      setPollStatus(null);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      if (err.response?.status === 402) {
        toast.error("Paiement requis. Veuillez procéder au paiement d'abord.");
      } else if (err.response?.status === 400) {
        toast.error(err.response?.data?.detail || "Données manquantes. Vérifiez le formulaire.");
      } else if (err.response?.status === 413) {
        toast.error("Fichiers trop volumineux. Réduisez la taille de vos documents.");
      } else {
        toast.error("Erreur lors de l'envoi. Veuillez réessayer.");
      }
    } finally {
      setLoading(false);
    }
  };

  // ==================== LANDING VIEW ====================
  if (step === 'landing') {
    return (
      <main className="page-transition pt-20">
      <SEO title="Dossier Express IA — Rapport d'analyse sous 2h" description="Uploadez vos documents, notre outil Dossier Express IA les analyse et vous recevez un rapport PDF complet sous 2 heures pour 97€." path="/dossier-express" />

        {/* Hero */}
        <section className="relative overflow-clip" style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f3460 100%)' }}>
          <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(circle at 20% 50%, white 1px, transparent 1px)', backgroundSize: '24px 24px' }} />
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-14 relative z-10">
            <div className="grid lg:grid-cols-2 gap-10 items-center">
              <div>
                {weeklyCount > 0 && (
                  <div className="inline-flex items-center gap-2 bg-emerald-500/15 border border-emerald-500/25 rounded-full px-3 py-1 mb-4">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span className="text-xs text-emerald-300 font-medium" data-testid="weekly-counter">{weeklyCount} dossiers accompagnés à ce jour</span>
                  </div>
                )}
                <Badge className="bg-amber-500/20 text-amber-300 border-amber-500/30 mb-4" data-testid="dossier-express-badge">
                  <Zap className="w-3 h-3 mr-1" fill="currentColor" />
                  Rapport sous 2 heures
                </Badge>
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-5" data-testid="dossier-express-title">
                  Votre rapport d'analyse<br />
                  <span className="text-amber-400">complet et personnalisé</span>
                </h1>
                <p className="text-base lg:text-lg text-white/70 mb-6 leading-relaxed max-w-xl">
                  Uploadez vos documents, notre outil Dossier Express IA croise <strong className="text-white">jurisprudences, barèmes et cas similaires</strong> pour identifier vos droits et construire votre stratégie.
                </p>

                {/* Price + CTA */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-6">
                  <Button
                    size="lg"
                    className="rounded-full px-8 gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold text-base shadow-lg shadow-amber-500/25 hover:shadow-amber-500/40 transition-all hover:scale-[1.02]"
                    onClick={() => { setStep('form'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                    data-testid="dossier-express-cta"
                  >
                    Analyser mon dossier — 97 €
                    <ArrowRight className="w-5 h-5" />
                  </Button>
                  <div className="text-sm text-white/50 leading-tight">
                    <span className="block text-amber-400/80 font-medium">Livré sous 2h par email</span>
                    <span className="block text-white/40 text-xs mt-0.5">Paiement sécurisé par Stripe</span>
                  </div>
                </div>

                {/* Trust signals */}
                <div className="flex flex-wrap gap-x-5 gap-y-2 pt-4 border-t border-white/10">
                  <TrustBadge icon={ShieldCheck} label="Paiement sécurisé" />
                  <TrustBadge icon={Lock} label="Données protégées RGPD" />
                  <TrustBadge icon={RefreshCw} label="Satisfait ou complément offert" />
                </div>
              </div>

              {/* Steps visual */}
              <div className="space-y-3">
                {[
                  { icon: Upload, title: "1. Décrivez votre situation", desc: "Type de dossier, régime, description et documents optionnels", accent: false },
                  { icon: CreditCard, title: "2. Paiement sécurisé — 97€", desc: "Par carte bancaire via Stripe. Traitement immédiat.", accent: false },
                  { icon: Brain, title: "3. Analyse par Dossier Express IA", desc: "Croisement de jurisprudences, barèmes officiels et cas similaires", accent: true },
                  { icon: Mail, title: "4. Rapport PDF par email sous 2h", desc: "Droits identifiés, stratégie recommandée, prochaines étapes concrètes", accent: false }
                ].map((s, i) => (
                  <div key={i} className={`flex items-start gap-4 rounded-xl p-4 backdrop-blur-sm transition-all duration-300 hover:translate-x-1 ${
                    s.accent ? 'bg-amber-500/10 border border-amber-500/20 hover:border-amber-500/40' : 'bg-white/5 border border-white/10 hover:bg-white/[0.08] hover:border-white/20'
                  }`}>
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      s.accent ? 'bg-amber-500/25' : 'bg-white/10'
                    }`}>
                      <s.icon className={`w-5 h-5 ${s.accent ? 'text-amber-400' : 'text-white/70'}`} />
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

        {/* Analyse croisée — Différenciation premium */}
        <section className="section-padding bg-gradient-to-b from-background to-amber-50/30 dark:to-amber-500/[0.03]" data-testid="cross-analysis-section">
          <div className="max-w-5xl mx-auto">
            <div className="grid lg:grid-cols-[1fr_auto_1fr] gap-8 lg:gap-10 items-center">
              <div className="space-y-3 reveal">
                <Badge className="bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/30 mb-1">
                  <Brain className="w-3 h-3 mr-1.5" />
                  Différenciation premium
                </Badge>
                <h2 className="text-2xl sm:text-3xl font-semibold leading-tight">
                  Analyse croisée de plusieurs<br />
                  <span className="text-amber-600 dark:text-amber-400">expertises médicales</span>
                </h2>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Dossier Express IA <strong className="text-foreground">ne se contente pas de résumer</strong> vos rapports. L'outil identifie chaque praticien, compare leurs conclusions et met en lumière les <strong className="text-foreground">divergences médicales exploitables</strong> — taux d'IPP, dates de consolidation, qualification PTIA, points de fragilité — pour transformer chaque contradiction en levier stratégique pour votre recours.
                </p>
              </div>

              {/* Vertical divider with icon */}
              <div className="hidden lg:flex flex-col items-center gap-3">
                <div className="w-px h-16 bg-gradient-to-b from-transparent via-amber-500/30 to-transparent" />
                <div className="w-10 h-10 rounded-full bg-amber-500/15 border border-amber-500/30 flex items-center justify-center">
                  <FileSearch className="w-5 h-5 text-amber-600" />
                </div>
                <div className="w-px h-16 bg-gradient-to-b from-transparent via-amber-500/30 to-transparent" />
              </div>

              {/* Right column — concrete benefits */}
              <ul className="space-y-3 reveal">
                {[
                  { label: "Chaque expert nommément cité", desc: "Dr Untel, date, mandataire, conclusion" },
                  { label: "Comparaison taux IPP & consolidation", desc: "Détection automatique des écarts" },
                  { label: "Identification des contradictions", desc: "Points exploitables en arbitrage médical" },
                  { label: "Synthèse stratégique unifiée", desc: "Au-delà du simple résumé OCR" },
                ].map((b, i) => (
                  <li key={i} className="flex items-start gap-3" data-testid={`cross-analysis-benefit-${i}`}>
                    <div className="w-6 h-6 rounded-full bg-amber-500/15 flex-shrink-0 flex items-center justify-center mt-0.5">
                      <CheckCircle className="w-3.5 h-3.5 text-amber-600" />
                    </div>
                    <div>
                      <span className="text-sm font-medium block">{b.label}</span>
                      <span className="text-xs text-muted-foreground">{b.desc}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        {/* What you get — Features */}
        <section className="section-padding">
          <div className="max-w-7xl mx-auto" ref={featuresRef}>
            <div className="text-center mb-10 reveal">
              <h2 className="text-2xl sm:text-3xl font-semibold mb-3">Ce que contient votre rapport</h2>
              <p className="text-muted-foreground max-w-lg mx-auto text-sm">Un document professionnel complet, personnalisé à votre situation, exploitable immédiatement.</p>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 stagger">
              {[
                { icon: FileSearch, title: "Analyse de votre situation", desc: "Synthèse factuelle, identification des enjeux clés et du contexte juridique de votre dossier." },
                { icon: Shield, title: "Cadre juridique applicable", desc: "Textes de loi, jurisprudences pertinentes et barèmes officiels adaptés à votre cas." },
                { icon: CheckCircle, title: "Vos droits identifiés", desc: "Liste exhaustive de vos droits avec explications claires et références légales." },
                { icon: AlertTriangle, title: "Points de vigilance", desc: "Faiblesses du dossier, pièces manquantes et risques de rejet anticipés." },
                { icon: Sparkles, title: "Stratégie recommandée", desc: "Plan d'action étape par étape avec délais et priorités pour maximiser vos chances." },
                { icon: TrendingUp, title: "Estimation des chances", desc: "Score de pertinence basé sur l'analyse de cas similaires et statistiques CNAM." }
              ].map((f, i) => (
                <Card key={i} className="card-glow border-border reveal group hover:-translate-y-1 transition-transform duration-300" data-testid={`feature-card-${i}`}>
                  <CardContent className="p-6">
                    <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4 group-hover:bg-accent/20 transition-colors">
                      <f.icon className="w-5 h-5 text-accent" />
                    </div>
                    <h3 className="font-semibold mb-2 text-sm">{f.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Typologie des dossiers traités */}
        <section className="section-padding bg-secondary/50">
          <div className="max-w-5xl mx-auto" ref={testimonialsRef}>
            <div className="text-center mb-10 reveal">
              <h2 className="text-2xl sm:text-3xl font-semibold mb-3">Typologie des dossiers analysés</h2>
              <p className="text-muted-foreground text-sm">Le Dossier Express IA a été conçu sur les situations réellement traitées — voici les grandes familles couvertes.</p>
            </div>
            <div className="grid md:grid-cols-3 gap-5 stagger">
              {TYPOLOGIE.map((t, i) => (
                <Card key={i} className="reveal hover:-translate-y-1 transition-transform duration-300" data-testid={`typologie-${i}`}>
                  <CardContent className="p-5">
                    <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-accent/10 border border-accent/20 mb-3">
                      <span className="text-[10px] font-semibold text-accent uppercase tracking-wider">{t.type}</span>
                    </div>
                    <h3 className="text-sm font-semibold text-foreground mb-2">{t.label}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{t.detail}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
            <p className="text-center text-[11px] text-muted-foreground/70 mt-6 italic">
              Aucune donnée personnelle identifiable publiée. Confidentialité stricte des personnes accompagnées.
            </p>
          </div>
        </section>

        {/* Legal disclaimer */}
        <section className="py-5 bg-amber-50/50 border-y border-amber-200/30">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-start gap-3" data-testid="dossier-express-disclaimer">
              <AlertTriangle className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
              <p className="text-xs text-amber-900/70 leading-relaxed">
                <strong className="text-amber-900/90">Information :</strong> Le Dossier Express IA fournit une analyse documentaire et stratégique basée sur l'intelligence artificielle. Il ne constitue pas une expertise médicale officielle, un conseil juridique ni un avis médical.
              </p>
            </div>
          </div>
        </section>

        {/* SEO Content */}
        <section className="section-padding" data-testid="dossier-seo-content">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-xl font-semibold mb-4">Qu'est-ce que le Dossier Express IA ?</h2>
            <div className="text-sm text-muted-foreground space-y-3 leading-relaxed">
              <p>
                Le Dossier Express IA est un service d'analyse documentaire proposé par Stratégie Expertise Santé. Il permet d'obtenir, en moins de 2 heures, un rapport complet et personnalisé sur votre situation en matière de maladie professionnelle, accident du travail, litige assurance ou demande MDPH.
              </p>
              <p>
                L'analyse croise vos documents avec les jurisprudences récentes, les barèmes officiels et les cas similaires pour identifier vos droits, évaluer la solidité de votre dossier et proposer une stratégie concrète. Le rapport est livré par email au format PDF.
              </p>
              <p className="font-medium text-foreground">À qui s'adresse ce service :</p>
              <ul className="space-y-1.5 list-none pl-0">
                <li className="flex items-start gap-2"><span className="text-accent mt-0.5">–</span><span>Victimes d'accident du travail ou de maladie professionnelle souhaitant connaître leurs droits</span></li>
                <li className="flex items-start gap-2"><span className="text-accent mt-0.5">–</span><span>Personnes en désaccord avec une décision CPAM, MDPH ou assurance</span></li>
                <li className="flex items-start gap-2"><span className="text-accent mt-0.5">–</span><span>Toute personne souhaitant une analyse rapide et fiable avant d'engager des démarches</span></li>
              </ul>
              <p>
                Le Dossier Express IA ne remplace pas un avis juridique ou médical officiel. Il constitue un outil d'aide à la décision qui vous permet de comprendre votre situation et de préparer vos prochaines étapes avec des éléments concrets.
              </p>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <DossierExpressFAQ />

        {/* Final CTA */}
        <section className="section-padding">
          <div className="max-w-2xl mx-auto reveal" ref={ctaBottomRef}>
            <Card className="border-accent/20 overflow-hidden">
              <CardContent className="p-0">
                <div className="bg-foreground text-primary-foreground p-8 text-center">
                  <div className="w-14 h-14 rounded-2xl bg-amber-500/20 flex items-center justify-center mx-auto mb-4">
                    <Brain className="w-7 h-7 text-amber-400" />
                  </div>
                  <h2 className="text-xl sm:text-2xl font-semibold mb-2">Prêt à analyser votre dossier ?</h2>
                  <p className="text-primary-foreground/60 mb-6 text-sm max-w-md mx-auto">
                    Recevez un rapport professionnel complet sous 2h pour comprendre votre situation, vos droits et votre stratégie.
                  </p>
                  <Button
                    size="lg"
                    className="rounded-full px-10 gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold shadow-lg shadow-amber-500/20 hover:scale-[1.02] transition-all"
                    onClick={() => { setStep('form'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                    data-testid="dossier-express-cta-bottom"
                  >
                    Commencer — 97 €
                    <ArrowRight className="w-5 h-5" />
                  </Button>
                  <div className="flex items-center justify-center gap-4 mt-5 text-xs text-primary-foreground/40">
                    <span className="flex items-center gap-1"><ShieldCheck className="w-3 h-3" /> Paiement sécurisé</span>
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> Livré sous 2h</span>
                    <span className="flex items-center gap-1"><RefreshCw className="w-3 h-3" /> Garantie satisfaction</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>
    );
  }

  // ==================== FORM VIEW ====================
  if (step === 'form') {
    const hasPaid = searchParams.get('payment') === 'success' || searchParams.get('session_id') || adminPaid;
    const totalAmount = 97 + (premiumPdf ? 19 : 0) + (analysePremium ? 49 : 0);

    return (
      <main className="page-transition pt-20">
        <section className="section-padding">
          <div className="max-w-5xl mx-auto">
            <button onClick={() => setStep('landing')} className="text-sm text-muted-foreground hover:text-foreground mb-4 flex items-center gap-1 transition-colors">
              <ChevronRight className="w-4 h-4 rotate-180" /> Retour
            </button>

            <StepIndicator currentStep={hasPaid ? 3 : 1} />

            <div className="grid lg:grid-cols-[1fr_320px] gap-8">
              {/* Main form */}
              <div>
                <h2 className="text-2xl sm:text-3xl font-bold mb-2" data-testid="form-title">
                  {hasPaid ? 'Complétez votre dossier' : 'Votre Dossier Express IA'}
                </h2>
                <p className="text-muted-foreground mb-6 text-sm">
                  {hasPaid ? 'Décrivez votre situation pour lancer l\'analyse Dossier Express IA.' : 'Remplissez les informations ci-dessous pour lancer l\'analyse.'}
                </p>

                <div className="space-y-5">
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
                      <Select value={form.type_dossier} onValueChange={v => setForm(p => ({...p, type_dossier: v, regime: ''}))}>
                        <SelectTrigger data-testid="de-type-select">
                          <SelectValue placeholder="Sélectionnez..." />
                        </SelectTrigger>
                        <SelectContent>
                          {TYPES_DOSSIER.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>
                        {getContextDE(form.type_dossier)?.label || 'Régime'}
                      </Label>
                      <Select value={form.regime} onValueChange={v => setForm(p => ({...p, regime: v}))}>
                        <SelectTrigger data-testid="de-regime-select">
                          <SelectValue placeholder={
                            getContextDE(form.type_dossier)?.placeholder || "Sélectionnez..."
                          } />
                        </SelectTrigger>
                        <SelectContent>
                          {(getContextDE(form.type_dossier)?.options || REGIMES).map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}
                        </SelectContent>
                      </Select>
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
                      className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring focus:ring-inset"
                      placeholder="Décrivez votre situation en détail : historique, démarches entreprises, difficultés rencontrées, objectifs..."
                      data-testid="de-situation-input"
                    />
                    <p className="text-xs text-muted-foreground">Plus votre description est détaillée, plus l'analyse sera pertinente.</p>
                  </div>

                  {/* Document upload */}
                  <div className="space-y-2">
                    <Label>Documents (optionnel, max 10 fichiers)</Label>
                    <DocumentUploader
                      files={files}
                      onFilesChange={setFiles}
                      maxFiles={10}
                      showChecklist={files.length > 0}
                      showGuide={true}
                      enableOCR={true}
                      onOcrResult={(result) => {
                        if (result?.fields) {
                          const f = result.fields;
                          if (f.type_dossier_detected?.length > 0 && !form.type_dossier) {
                            const typeMap = { at: 'Accident du travail (AT)', mp: 'Maladie professionnelle (MP)', mdph: 'Demande MDPH / AAH', expertise: 'Expertise médicale', ipp: 'Contestation taux IPP', assurance: 'Litige assurance / protection juridique' };
                            const matched = typeMap[f.type_dossier_detected[0]];
                            if (matched) setForm(prev => ({ ...prev, type_dossier: matched }));
                          }
                          if (f.organisme && !form.regime) {
                            const regimeMap = { MSA: 'Régime agricole (MSA)' };
                            const matched = regimeMap[f.organisme];
                            if (matched) setForm(prev => ({ ...prev, regime: matched }));
                            else setForm(prev => ({ ...prev, regime: 'Régime général' }));
                          }
                          if (f.noms?.length > 0 && !form.name.trim()) {
                            setForm(prev => ({ ...prev, name: f.noms[0] }));
                          }
                          if (!form.situation.trim()) {
                            let autoText = '';
                            if (f.resume) autoText += f.resume;
                            if (f.recommandations?.length > 0) autoText += '\n\nPoints identifiés : ' + f.recommandations.join('. ');
                            if (f.contexte && !autoText) autoText = f.contexte;
                            if (autoText) setForm(prev => ({ ...prev, situation: autoText }));
                          }
                          if (result.raw) setForm(prev => ({ ...prev, documents_text: result.raw.substring(0, 3000) }));
                        }
                      }}
                    />
                  </div>

                  <DataConsentBox checked={consent} onChange={setConsent} className="mt-3" improvementOptout={improvementOptout} onImprovementOptoutChange={setImprovementOptout} />

                  {/* Upsell options */}
                  <div className="space-y-2.5 pt-2">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Options</p>
                    <label className="flex items-start gap-3 p-3 rounded-lg border border-border hover:border-amber-500/30 cursor-pointer transition-colors" data-testid="de-analyse-premium-option">
                      <input type="checkbox" checked={analysePremium} onChange={e => setAnalysePremium(e.target.checked)} className="mt-0.5 accent-amber-500" />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Award className="w-4 h-4 text-amber-500" />
                          <span className="text-sm font-medium">Analyse Premium</span>
                          <Badge className="bg-amber-500/10 text-amber-600 border-amber-500/20 text-[10px]">+49€</Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">Rapport enrichi par la relecture personnelle de notre expert avec recommandations exclusives.</p>
                      </div>
                    </label>
                    <label className="flex items-start gap-3 p-3 rounded-lg border border-border hover:border-accent/40 cursor-pointer transition-colors" data-testid="de-premium-pdf-option">
                      <input type="checkbox" checked={premiumPdf} onChange={e => setPremiumPdf(e.target.checked)} className="mt-0.5 accent-amber-500" />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Crown className="w-4 h-4 text-accent" />
                          <span className="text-sm font-medium">Version professionnelle</span>
                          <Badge className="bg-accent/10 text-accent border-accent/20 text-[10px]">+19€</Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">Rapport sans filigrane, optimisé pour transmission à un avocat, médecin ou expert.</p>
                      </div>
                      <PdfCoverPreview reportType="Dossier Express IA" />
                    </label>
                  </div>

                  {/* Action button */}
                  {hasPaid ? (
                    <Button
                      size="lg"
                      className="w-full rounded-xl gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold shadow-lg shadow-amber-500/15 hover:shadow-amber-500/25 transition-all"
                      onClick={handleSubmitDossier}
                      disabled={loading || !form.situation.trim() || (!isAdminMode && !isVip && (!form.email || !consent))}
                      data-testid="de-submit-button"
                    >
                      {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Envoi et analyse en cours...</> : <><Brain className="w-5 h-5" /> Lancer l'analyse Dossier Express IA</>}
                    </Button>
                  ) : (
                    <Button
                      size="lg"
                      className="w-full rounded-xl gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold shadow-lg shadow-amber-500/15 hover:shadow-amber-500/25 transition-all"
                      onClick={handleCheckout}
                      disabled={loading || (!isAdminMode && !isVip && (!form.email || !form.name || !consent))}
                      data-testid="de-checkout-button"
                    >
                      {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Redirection vers le paiement...</> : isVip ? <><CreditCard className="w-5 h-5" /> Accès Partenaire — Lancer l'analyse</> : <><CreditCard className="w-5 h-5" /> {adminPaid ? 'Mode Admin — Paiement validé' : `Payer ${totalAmount} € — Analyse sous 2h`}</>}
                    </Button>
                  )}

                  <p className="text-[11px] text-muted-foreground text-center flex items-center justify-center gap-2">
                    <ShieldCheck className="w-3 h-3" />
                    Paiement sécurisé par Stripe — Rapport PDF envoyé par email sous 2 heures
                  </p>
                </div>
              </div>

              {/* Sidebar — value reminder */}
              <div className="hidden lg:block" style={{overflow: 'visible'}}>
                <div className="sticky top-24" style={{overflow: 'visible'}}>
                  <ValueReminder weeklyCount={weeklyCount} />
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    );
  }

  // ==================== PROCESSING VIEW ====================
  if (step === 'processing') {
    const filesCount = pollStatus?.files_count || files.length || 0;
    const docsExtracted = pollStatus?.documents_extracted || false;
    const deliveryStatus = pollStatus?.delivery_status;
    const isIncident = deliveryStatus === 'incident_technique';

    // If incident detected during polling, show reassurance
    if (isIncident) {
      return (
        <main className="page-transition pt-20">
          <section className="section-padding">
            <div className="max-w-xl mx-auto text-center">
              <div className="w-20 h-20 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Shield className="w-10 h-10 text-amber-600" />
              </div>
              <h2 className="text-2xl font-bold mb-3" data-testid="incident-title">Votre dossier est bien pris en charge</h2>
              <p className="text-muted-foreground mb-6 text-sm leading-relaxed max-w-md mx-auto">
                Un traitement complémentaire est en cours afin de vous garantir la meilleure qualité d'analyse possible.
                Notre équipe a été automatiquement informee et reviendra vers vous dans les meilleurs delais.
              </p>
              <Card className="text-left mb-8 border-amber-200/60 bg-amber-50/30">
                <CardContent className="p-5">
                  <div className="flex items-start gap-3">
                    <Shield className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-semibold mb-2">Aucune action requise de votre part</h4>
                      <ul className="space-y-2">
                        {[
                          "Votre paiement est bien confirmé et sécurisé",
                          "Vos documents sont conserves en toute confidentialité",
                          "Vous recevrez votre rapport par email des qu'il sera finalise",
                          "En cas de besoin, notre équipe vous contactera directement"
                        ].map((item, i) => (
                          <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                            <CheckCircle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0 mt-0.5" />
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Link to="/contact">
                  <Button variant="outline" className="rounded-full px-6 gap-2">
                    <Mail className="w-4 h-4" />
                    Nous contacter
                  </Button>
                </Link>
                <Link to="/">
                  <Button variant="ghost" className="rounded-full px-6">Retour a l'accueil</Button>
                </Link>
              </div>
            </div>
          </section>
        </main>
      );
    }

    const STEPS = [
      { key: 'extracting', label: 'Lecture intelligente de vos pièces', icon: FileSearch, detail: 'Extraction OCR cloud sécurisée — peut prendre 60 à 90s par PDF scanné.' },
      { key: 'uploading', label: 'Documents bien reçus et sécurisés', icon: Shield, detail: 'Vos pièces sont conservées de manière confidentielle.' },
      { key: 'reading', label: 'Identification des pièces transmises', icon: FileText, detail: 'Catégorisation et indexation des éléments médicaux et administratifs.' },
      { key: 'analyzing_1', label: 'Analyse documentaire et chronologie', icon: FileSearch, detail: 'Reconstitution de votre parcours à partir des pièces fournies.' },
      { key: 'analyzing_2', label: 'Cadre juridique et points de vigilance', icon: Brain, detail: 'Croisement avec les textes de loi, jurisprudences et barèmes applicables.' },
      { key: 'analyzing_3', label: 'Stratégie et estimation des préjudices', icon: TrendingUp, detail: 'Construction des recommandations et chiffrage personnalisé.' },
      { key: 'generating', label: 'Structuration de votre rapport personnalisé', icon: Sparkles, detail: 'Mise en forme de votre synthèse complète.' },
      { key: 'sending', label: 'Préparation de votre document final', icon: Award, detail: 'Génération du PDF et envoi sécurisé.' },
    ];

    const VALUE_MESSAGES = [
      "Votre dossier fait l'objet d'une analyse approfondie et individualisée",
      "Nous croisons actuellement vos pièces avec les points de vigilance les plus fréquents",
      "Chaque document transmis est pris en compte pour renforcer la pertinence de votre rapport",
      "Nous structurons votre rapport pour en faire ressortir les leviers les plus utiles",
      "Vos éléments sont confrontés aux jurisprudences et barèmes en vigueur",
      "L'analyse personnalisée de votre situation est en cours de finalisation",
    ];

    const currentProgress = pollStatus?.progress_step || 'uploading';
    const currentIdx = Math.max(0, STEPS.findIndex(s => s.key === currentProgress));
    // Map legacy 'analyzing' to 'analyzing_1' for backward compat
    const mappedIdx = currentProgress === 'analyzing' ? 2 : currentIdx;
    const progressPct = Math.max(5, Math.min(95, ((mappedIdx + 1) / STEPS.length) * 100));
    const activeStep = STEPS[mappedIdx] || STEPS[0];

    const elapsedMin = Math.floor(elapsedSec / 60);
    const elapsedSecRemainder = elapsedSec % 60;

    return (
      <main className="page-transition pt-20">
        <section className="section-padding">
          <div className="max-w-xl mx-auto">

            {/* Header premium */}
            <div className="text-center mb-8">
              <div className="relative w-20 h-20 mx-auto mb-5">
                <div className="absolute inset-0 bg-amber-500/15 rounded-full animate-ping" style={{ animationDuration: '3s' }} />
                <div className="relative w-20 h-20 bg-gradient-to-br from-amber-500/12 to-amber-600/8 rounded-full flex items-center justify-center border border-amber-500/20">
                  <Brain className="w-9 h-9 text-amber-500" />
                </div>
              </div>
              <h2 className="text-2xl font-bold mb-2" data-testid="processing-title">
                Votre dossier est en cours d'analyse
              </h2>
              <p className="text-muted-foreground text-sm leading-relaxed max-w-md mx-auto">
                Nos algorithmes analysent chacune de vos pièces pour produire un rapport structuré, personnalisé et directement exploitable.
              </p>
            </div>

            {/* Active step indicator + counter */}
            <div className="bg-amber-500/[0.06] border border-amber-500/15 rounded-xl p-4 mb-5" data-testid="dynamic-status">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-amber-600 animate-spin" />
                  <span className="text-sm font-semibold text-amber-700">{activeStep.label}</span>
                </div>
                <span className="text-xs font-mono text-amber-600/70 tabular-nums" data-testid="step-counter">
                  {mappedIdx + 1} / {STEPS.length}
                </span>
              </div>
              <p className="text-xs text-amber-600/70">{activeStep.detail}</p>
            </div>

            {/* Segmented progress bar — one segment per step, fills in sequence */}
            <div className="grid gap-1 mb-1" style={{ gridTemplateColumns: `repeat(${STEPS.length}, 1fr)` }} data-testid="progress-bar">
              {STEPS.map((_, i) => {
                const isCompleted = i < mappedIdx || pollStatus?.status === 'completed';
                const isCurrent = i === mappedIdx && pollStatus?.status !== 'completed';
                return (
                  <div
                    key={i}
                    className="relative h-1.5 rounded-full overflow-hidden bg-muted/70"
                    data-testid={`progress-segment-${i}`}
                  >
                    <div
                      className={`absolute inset-0 rounded-full transition-all duration-700 ${
                        isCompleted
                          ? 'bg-gradient-to-r from-amber-500 to-amber-600 w-full'
                          : isCurrent
                          ? 'bg-gradient-to-r from-amber-500 to-amber-600 w-full animate-pulse'
                          : 'w-0'
                      }`}
                    />
                  </div>
                );
              })}
            </div>
            <div className="flex items-center justify-between mb-6">
              <span className="text-[11px] text-muted-foreground tabular-nums" data-testid="elapsed-time">
                ⏱ {elapsedMin > 0 ? `${elapsedMin} min ${String(elapsedSecRemainder).padStart(2, '0')} s` : `${elapsedSec} s`} <span className="text-muted-foreground/60">— estimé 3 à 5 min</span>
              </span>
              <span className="text-[11px] text-muted-foreground">{Math.round(progressPct)}%</span>
            </div>

            {/* Live progress (chunk upload OR Gemini extraction status) */}
            {pollStatus?.chunk_progress && (
              <div className="text-[11px] text-amber-600 text-center mb-3 animate-pulse" data-testid="chunk-progress">
                {pollStatus.chunk_progress.includes('IA') || pollStatus.chunk_progress.includes('Préparation')
                  ? pollStatus.chunk_progress
                  : `Transfert : ${pollStatus.chunk_progress}`}
              </div>
            )}

            {/* Steps timeline */}
            <Card className="mb-5 border-border/60">
              <CardContent className="p-0">
                {STEPS.map((s, i) => {
                  const isDone = i < mappedIdx || (pollStatus?.status === 'completed');
                  const isActive = i === mappedIdx && pollStatus?.status !== 'completed';
                  const StepIcon = s.icon;
                  return (
                    <div
                      key={s.key}
                      className={`flex items-center gap-3.5 px-5 py-3 border-b border-border/40 last:border-0 transition-all duration-500 ${
                        isActive ? 'bg-amber-50/50' : ''
                      }`}
                      data-testid={`step-${s.key}`}
                    >
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-500 ${
                        isDone ? 'bg-emerald-100 text-emerald-600' :
                        isActive ? 'bg-amber-100 text-amber-600 ring-2 ring-amber-200' :
                        'bg-muted text-muted-foreground/50'
                      }`}>
                        {isDone ? <CheckCircle className="w-4 h-4" /> :
                         isActive ? <Loader2 className="w-4 h-4 animate-spin" /> :
                         <StepIcon className="w-3.5 h-3.5" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <span className={`text-sm block transition-colors ${
                          isDone ? 'text-emerald-600 font-medium' :
                          isActive ? 'text-amber-700 font-semibold' :
                          'text-muted-foreground/50'
                        }`}>
                          {s.label}
                        </span>
                        {isActive && (
                          <span className="text-[11px] text-amber-600/70 block mt-0.5">{s.detail}</span>
                        )}
                      </div>
                      {isDone && <span className="text-[10px] text-emerald-500 font-medium flex-shrink-0">OK</span>}
                    </div>
                  );
                })}
              </CardContent>
            </Card>

            {/* Rotating value message */}
            <div className="rounded-xl border border-accent/10 bg-accent/[0.03] p-4 mb-5" data-testid="value-message">
              <p className="text-[13px] text-center text-foreground/70 italic leading-relaxed transition-opacity duration-500">
                {VALUE_MESSAGES[valueIdx]}
              </p>
            </div>

            {/* Document count if applicable */}
            {filesCount > 0 && (
              <div className="flex items-center justify-center gap-2 mb-5 text-xs text-amber-700/80 font-medium" data-testid="docs-info">
                <FileText className="w-3.5 h-3.5" />
                <span>{filesCount} pièce{filesCount > 1 ? 's' : ''} {docsExtracted ? 'analysée' + (filesCount > 1 ? 's' : '') : 'intégrée' + (filesCount > 1 ? 's' : '')} dans votre rapport</span>
              </div>
            )}

            {/* Premium reassurance block */}
            <Card className="border-border/50 bg-card">
              <CardContent className="p-5">
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <ShieldCheck className="w-5 h-5 text-accent" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold mb-2">Pourquoi cette étape prend quelques instants</h4>
                    <p className="text-xs text-muted-foreground leading-relaxed mb-3">
                      Contrairement à un simple résumé automatique, notre système analyse réellement chacune de vos pièces. Le traitement croise vos documents avec les textes de loi, jurisprudences et barèmes applicables à votre situation, afin de produire une synthèse véritablement personnalisée et exploitable.
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <span className="text-[11px] text-muted-foreground flex items-center gap-1.5">
                        <Clock className="w-3 h-3 text-accent/60" />
                        Durée estimée : 3 à 5 minutes selon le volume
                      </span>
                      <span className="text-[11px] text-muted-foreground flex items-center gap-1.5">
                        <Lock className="w-3 h-3 text-accent/60" />
                        Données chiffrées et confidentielles
                      </span>
                      <span className="text-[11px] text-muted-foreground flex items-center gap-1.5">
                        <Shield className="w-3 h-3 text-accent/60" />
                        Paiement confirmé et sécurisé
                      </span>
                      <span className="text-[11px] text-muted-foreground flex items-center gap-1.5">
                        <Mail className="w-3 h-3 text-accent/60" />
                        Rapport envoyé par email à la fin
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* "Vous pouvez fermer cette page" reassurance footer — Niveau 3 */}
            <div className="mt-5 px-4 py-3 rounded-lg bg-muted/40 border border-border/40 flex items-start gap-2.5" data-testid="leave-page-reassurance">
              <Mail className="w-3.5 h-3.5 text-muted-foreground/70 mt-0.5 flex-shrink-0" />
              <p className="text-[11px] text-muted-foreground/80 leading-relaxed">
                <strong className="text-foreground/80">Vous pouvez fermer cette page en toute confiance.</strong> Votre dossier est traité côté serveur — un email vous sera automatiquement envoyé à <span className="font-mono text-foreground/70">{form.email || 'votre adresse'}</span> dès que le rapport est prêt. Aucune donnée n'est perdue.
              </p>
            </div>

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
            <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-10 h-10 text-emerald-600" />
            </div>
            <h2 className="text-2xl font-bold mb-3" data-testid="success-title">Votre rapport est prêt</h2>
            <p className="text-muted-foreground mb-2 text-sm leading-relaxed">
              Votre dossier a été analysé et structuré avec soin à partir de l'ensemble de vos pièces.
            </p>
            <p className="text-muted-foreground mb-6 text-sm">
              Le rapport personnalisé a été envoyé à <strong className="text-foreground">{form.email || pollStatus?.email}</strong>.
              Vérifiez votre boîte de réception (et vos spams).
            </p>
            <Card className="text-left mb-8">
              <CardContent className="p-5">
                <h3 className="font-semibold mb-3 text-sm">Et ensuite ?</h3>
                <ul className="space-y-2.5">
                  {[
                    "Lisez attentivement votre rapport d'analyse",
                    "Suivez les prochaines étapes recommandées",
                    "Rassemblez les documents manquants identifiés",
                    "Pour un accompagnement personnalisé, prenez rendez-vous"
                  ].map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <ChevronRight className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/agenda">
                <Button className="rounded-full px-6 gap-2">
                  Réserver un appel gratuit
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

  // ==================== ERROR VIEW ====================
  if (step === 'error') {
    return (
      <main className="page-transition pt-20">
        <section className="section-padding">
          <div className="max-w-lg mx-auto text-center">
            <div className="w-20 h-20 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Shield className="w-10 h-10 text-amber-600" />
            </div>
            <h2 className="text-2xl font-bold mb-3" data-testid="error-title">Votre dossier est bien pris en charge</h2>
            <p className="text-muted-foreground mb-6 text-sm leading-relaxed">
              Un traitement complémentaire est en cours afin de vous garantir la meilleure qualité d'analyse.
              Notre équipe a été automatiquement informee et reviendra vers vous a <strong className="text-foreground">{form.email || pollStatus?.email}</strong>.
            </p>
            <Card className="text-left mb-8 border-amber-200/60 bg-amber-50/30">
              <CardContent className="p-5">
                <h3 className="font-semibold mb-3 text-sm flex items-center gap-2">
                  <Shield className="w-4 h-4 text-amber-600" />
                  Ce que vous devez savoir
                </h3>
                <ul className="space-y-2.5">
                  {[
                    "Votre paiement est confirmé et sécurisé",
                    "Vos documents sont conserves en toute confidentialité",
                    "Notre équipe technique finalise votre rapport",
                    "Vous recevrez votre analyse par email dès que possible"
                  ].map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <CheckCircle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/contact">
                <Button variant="outline" className="rounded-full px-6 gap-2">
                  <Mail className="w-4 h-4" />
                  Nous contacter
                </Button>
              </Link>
              <Link to="/">
                <Button variant="ghost" className="rounded-full px-6">Retour a l'accueil</Button>
              </Link>
            </div>
          </div>
        </section>
      </main>
    );
  }

  return null;
};
