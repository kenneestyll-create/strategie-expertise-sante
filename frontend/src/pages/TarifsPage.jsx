import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import {
  ArrowRight, FileSearch, Shield, Users, Briefcase,
  CheckCircle, Star, GraduationCap, Building2, CreditCard,
  Loader2, PartyPopper, Gift, Percent, Tag, Zap, Clock,
  Wallet, Brain, FileText, Sparkles, ChevronRight, Scale
} from 'lucide-react';
import axios from 'axios';
import { PayPalScriptProvider, PayPalButtons } from '@paypal/react-paypal-js';
import { SEO } from '@/components/SEO';
import { useReveal, useRevealChildren } from '@/hooks/useReveal';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const TarifsPage = () => {
  const [searchParams] = useSearchParams();
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [paymentDetails, setPaymentDetails] = useState(null);
  const [customerInfo, setCustomerInfo] = useState({ email: '', name: '', referralCode: '' });
  const [referralValid, setReferralValid] = useState(null);
  const [loyaltyDiscount, setLoyaltyDiscount] = useState(0);
  const [checkingDiscount, setCheckingDiscount] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('stripe');

  const step1Ref = useReveal();
  const step2Ref = useReveal();
  const step3Ref = useRevealChildren();
  const step4Ref = useRevealChildren();
  const proRef = useRevealChildren();
  const ctaRef = useReveal();

  useEffect(() => {
    const paymentStatus = searchParams.get('payment');
    const sessionId = searchParams.get('session_id');
    if (paymentStatus === 'success' && sessionId) {
      checkPaymentStatus(sessionId);
    } else if (paymentStatus === 'cancelled') {
      toast.error("Paiement annulé");
    }
  }, [searchParams]);

  const checkPaymentStatus = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/payments/status/${sessionId}`);
      if (response.data.payment_status === 'paid') {
        setPaymentDetails(response.data);
        setShowSuccessModal(true);
      }
    } catch (error) {
      console.error('Error checking payment:', error);
    }
  };

  const checkLoyaltyDiscount = async (email) => {
    if (!email || !email.includes('@')) return;
    setCheckingDiscount(true);
    try {
      const response = await axios.get(`${API}/client/discount/${encodeURIComponent(email)}`);
      setLoyaltyDiscount(response.data.loyalty_discount);
    } catch (error) {
      setLoyaltyDiscount(0);
    } finally {
      setCheckingDiscount(false);
    }
  };

  const validateReferral = async (code) => {
    if (!code || code.length < 3) { setReferralValid(null); return; }
    try {
      const response = await axios.get(`${API}/referral/validate/${code}`);
      setReferralValid(response.data.valid);
      if (response.data.valid) toast.success("Code parrainage valide ! -10%");
    } catch (error) { setReferralValid(false); }
  };

  const getActiveDiscount = () => {
    if (loyaltyDiscount > 0) return { percent: 15, type: 'fidélité' };
    if (referralValid) return { percent: 10, type: 'parrainage' };
    return { percent: 0, type: '' };
  };

  const getDiscountedPrice = (basePrice) => {
    const discount = getActiveDiscount();
    if (discount.percent === 0) return null;
    return (parseFloat(basePrice) * (1 - discount.percent / 100)).toFixed(2);
  };

  const handlePayment = async () => {
    if (!customerInfo.email) { toast.error("Veuillez entrer votre email"); return; }
    setLoading(true);
    try {
      const response = await axios.post(`${API}/payments/checkout`, {
        package_id: selectedPackage.id,
        origin_url: window.location.origin,
        customer_email: customerInfo.email,
        customer_name: customerInfo.name,
        referral_code: referralValid ? customerInfo.referralCode : null
      });
      if (response.data.url) {
        window.location.href = response.data.url;
      } else {
        toast.error("Erreur : URL de paiement non reçue");
        setLoading(false);
      }
    } catch (error) {
      toast.error("Erreur lors de l'initialisation du paiement");
      setLoading(false);
    }
  };

  const openPaymentModal = (pkg) => {
    setSelectedPackage(pkg);
    setReferralValid(null);
    setLoyaltyDiscount(0);
    setCustomerInfo({ email: '', name: '', referralCode: '' });
    setPaymentMethod('stripe');
    setShowPaymentModal(true);
  };

  const handleModalClose = (open) => {
    if (!open && selectedPackage && customerInfo.email && !loading) {
      axios.post(`${API}/relance/track`, {
        email: customerInfo.email,
        name: customerInfo.name,
        package_id: selectedPackage.id
      }).catch(() => {});
    }
    setShowPaymentModal(open);
  };

  const defaultPrestations = [
    { id: "analyse_dossier", icon: FileSearch, title: "Analyse de dossier", description: "Étude personnalisée du dossier médical et administratif. Identification des points forts, faiblesses et éléments manquants.", price: "150", features: ["Lecture complète du dossier", "Rapport d'analyse détaillé", "Recommandations personnalisées", "Échange téléphonique de restitution"] },
    { id: "préparation_expertise", icon: Shield, title: "Préparation expertise médicale", description: "Accompagnement pour aborder sereinement une expertise médicale.", price: "250", popular: true, features: ["Analyse du dossier médical", "Préparation des arguments", "Simulation d'entretien", "Documents à apporter"], valueProp: "Travail ciblé à fort impact stratégique avant un moment décisif." },
    { id: "accompagnement_mdph", icon: Users, title: "Accompagnement MDPH", description: "Aide à la compréhension et structuration du dossier MDPH.", price: "200", features: ["Analyse de votre situation", "Aide au formulaire", "Conseils pièces justificatives", "Suivi de la demande"] },
    { id: "protection_juridique", icon: Shield, title: "Protection juridique", description: "Accompagnement dans l'activation de votre protection juridique.", price: "200", features: ["Identification de vos garanties", "Aide à la déclaration du litige", "Suivi échanges assureur", "Orientation avocat spécialisé"] },
    { id: "accompagnement_complet", icon: Briefcase, title: "Accompagnement complet", description: "Suivi global des démarches administratives et médicales.", price: "500", badge: "Sur devis", features: ["Analyse complète de la situation", "Stratégie personnalisée", "Suivi des démarches", "Disponibilité continue"], valueProp: "Intervention globale pour les situations à fort enjeu." },
  ];

  const defaultUrgentes = [
    { id: "urgent_analyse_dossier", icon: FileSearch, title: "Analyse de dossier", price: "250", priceStandard: "150", features: ["Traitement prioritaire 48h", "Rapport d'analyse express", "Recommandations personnalisées", "Échange téléphonique immédiat"] },
    { id: "urgent_préparation_expertise", icon: Shield, title: "Préparation expertise", price: "400", priceStandard: "250", features: ["Traitement prioritaire 48h", "Préparation d'urgence", "Simulation d'entretien rapide", "Disponibilité immédiate"] },
    { id: "urgent_accompagnement_mdph", icon: Users, title: "Accompagnement MDPH", price: "320", priceStandard: "200", features: ["Traitement prioritaire 48h", "Constitution dossier express", "Suivi accéléré", "Interlocuteur dédié"] },
    { id: "urgent_accompagnement_complet", icon: Briefcase, title: "Accompagnement complet", price: "750", priceStandard: "500", features: ["Traitement prioritaire 48h", "Analyse complète express", "Stratégie immédiate", "Disponibilité 7j/7"] },
  ];

  const [prestations, setPrestations] = useState(defaultPrestations);
  const [prestationsUrgentes, setPrestationsUrgentes] = useState(defaultUrgentes);

  useEffect(() => {
    axios.get(`${API}/public/tarifs`).then(res => {
      const t = res.data;
      if (t && Object.keys(t).length > 0) {
        setPrestations(prev => prev.map(p => ({
          ...p,
          price: t[p.id]?.price || p.price,
          badge: t[p.id]?.badge || p.badge,
        })));
        setPrestationsUrgentes(prev => prev.map(p => ({
          ...p,
          price: t[p.id]?.price || p.price,
          priceStandard: t[p.id]?.priceStandard || p.priceStandard,
          badge: t[p.id]?.badge || p.badge,
        })));
      }
    }).catch(() => {});
  }, []);

  return (
    <main className="page-transition pt-20">
      <SEO title="Tarifs et prestations" description="Découvrez nos tarifs : pré-analyse gratuite assistée par StratégiIA, Dossier Express IA 97€, accompagnement personnalisé 150-500€. Première consultation gratuite — 10 minutes." path="/tarifs" />
      {/* Hero */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Votre parcours</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="tarifs-title">
              Un accompagnement progressif, adapté à vos besoins
            </h1>
            <p className="text-lg text-muted-foreground">
              Chaque situation est unique. Suivez les étapes pour trouver l'accompagnement qui vous correspond,
              du diagnostic gratuit à la prise en charge complète.
            </p>
          </div>
        </div>
      </section>

      {/* Discount Banner */}
      <section className="py-3 bg-accent/10 border-b border-accent/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Percent className="w-4 h-4 text-accent" />
              <span><strong>-15% fidélité</strong> dès la 2ème prestation</span>
            </div>
            <span className="hidden sm:block text-muted-foreground">|</span>
            <div className="flex items-center gap-2">
              <Gift className="w-4 h-4 text-accent" />
              <span><strong>-10% parrainage</strong></span>
              <Link to="/parrainage" className="text-accent underline hover:no-underline ml-1">Obtenir un code</Link>
            </div>
          </div>
        </div>
      </section>

      {/* ==================== ÉTAPE 1 : StratégiIA Pré-analyse gratuite ==================== */}
      <section className="section-padding" id="tarif-strategiia">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-full bg-accent text-accent-foreground flex items-center justify-center font-bold text-lg">1</div>
            <div>
              <h2 className="text-2xl font-semibold">Comprenez votre situation</h2>
              <p className="text-muted-foreground text-sm">Pré-analyse gratuite assistée par notre outil StratégiIA</p>
            </div>
          </div>

          <Card className="border-accent/30 bg-accent/5 overflow-hidden reveal-scale" data-testid="step-1-card" ref={step1Ref}>
            <CardContent className="p-6 sm:p-8">
              <div className="grid sm:grid-cols-[1fr,auto] gap-6 items-center">
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Brain className="w-6 h-6 text-accent" />
                    <h3 className="text-xl font-semibold">Pré-analyse StratégiIA</h3>
                    <Badge className="bg-green-100 text-green-700 border-green-200">Gratuit</Badge>
                  </div>
                  <p className="text-muted-foreground mb-4">
                    Décrivez votre situation en quelques lignes. Notre outil StratégiIA croise jurisprudences, barèmes officiels
                    et cas similaires pour vous donner un premier diagnostic : droits identifiés, démarche prioritaire
                    et estimation de vos chances.
                  </p>
                  <ul className="space-y-2 text-sm">
                    {["Synthèse de votre situation", "Droits principaux identifiés", "Première démarche à effectuer", "Score de pertinence"].map((f, i) => (
                      <li key={i} className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-accent" />{f}</li>
                    ))}
                  </ul>
                </div>
                <div className="text-center sm:text-right">
                  <p className="text-4xl font-bold text-accent mb-2">Gratuit</p>
                  <p className="text-xs text-muted-foreground mb-4">Sans engagement</p>
                  <Button className="rounded-full gap-2" data-testid="step-1-cta" onClick={() => window.dispatchEvent(new Event('strategiia:open'))}>
                    <Brain className="w-4 h-4" />
                    Lancer ma pré-analyse
                  </Button>
                  <p className="text-xs text-muted-foreground mt-2">Gratuit, sans engagement, 2 minutes</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-center my-6">
            <div className="flex flex-col items-center text-muted-foreground">
              <ChevronRight className="w-5 h-5 rotate-90" />
              <span className="text-xs mt-1">Besoin d'aller plus loin ?</span>
            </div>
          </div>
        </div>
      </section>

      {/* ==================== ÉTAPE 2 : Dossier Express IA ==================== */}
      <section className="section-padding bg-secondary pt-2" id="tarif-dossier-express">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-full bg-amber-500 text-amber-950 flex items-center justify-center font-bold text-lg">2</div>
            <div>
              <h2 className="text-2xl font-semibold">Analysez votre dossier en profondeur</h2>
              <p className="text-muted-foreground text-sm">Rapport PDF complet livré par email sous 2h</p>
            </div>
          </div>

          <Card className="border-amber-500/30 overflow-hidden reveal-scale" data-testid="step-2-card" ref={step2Ref}>
            <CardContent className="p-6 sm:p-8">
              <div className="grid sm:grid-cols-[1fr,auto] gap-6 items-center">
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <FileText className="w-6 h-6 text-amber-500" />
                    <h3 className="text-xl font-semibold">Dossier Express IA</h3>
                    <Badge className="bg-amber-100 text-amber-700 border-amber-200">
                      <Zap className="w-3 h-3 mr-1" fill="currentColor" />
                      Sous 2h
                    </Badge>
                  </div>
                  <p className="text-muted-foreground mb-4">
                    Uploadez vos documents, notre équipe les analyse avec l'aide de Dossier Express IA et génère un rapport
                    PDF complet : cadre juridique, droits identifiés, stratégie recommandée, prochaines étapes.
                  </p>
                  <ul className="grid sm:grid-cols-2 gap-2 text-sm">
                    {["Analyse complète de vos documents", "Cadre juridique applicable", "Stratégie recommandée détaillée", "Score de chances de succès", "Points de vigilance identifiés", "5 actions prioritaires"].map((f, i) => (
                      <li key={i} className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-amber-500" />{f}</li>
                    ))}
                  </ul>
                </div>
                <div className="text-center sm:text-right">
                  <p className="text-4xl font-bold text-foreground mb-1">97 <span className="text-lg font-normal text-muted-foreground">€</span></p>
                  <p className="text-xs text-muted-foreground mb-4">Paiement unique</p>
                  <Link to="/dossier-express">
                    <Button className="rounded-full gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold" data-testid="step-2-cta">
                      <FileText className="w-4 h-4" />
                      Commander mon rapport
                    </Button>
                  </Link>
                  <p className="text-xs text-muted-foreground mt-2">Rapport PDF envoyé par email</p>
                  <p className="text-[10px] text-muted-foreground/60 mt-1 italic">Lecture documentaire structurée à forte valeur de tri et d'orientation.</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-center my-6">
            <div className="flex flex-col items-center text-muted-foreground">
              <ChevronRight className="w-5 h-5 rotate-90" />
              <span className="text-xs mt-1">Besoin d'un accompagnement humain ?</span>
            </div>
          </div>
        </div>
      </section>

      {/* ==================== ÉTAPE 3 : Prestations personnalisées ==================== */}
      <section className="section-padding pt-2">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-full bg-accent text-accent-foreground flex items-center justify-center font-bold text-lg">3</div>
            <div>
              <h2 className="text-2xl font-semibold">Faites-vous accompagner par un expert</h2>
              <p className="text-muted-foreground text-sm">Prestations personnalisées avec suivi humain</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5 stagger" ref={step3Ref}>
            {prestations.map((p, i) => (
              <Card key={i} className={`relative border-border flex flex-col card-glow reveal ${p.popular ? 'ring-2 ring-accent' : ''}`} data-testid={`tarif-card-${i}`}>
                {p.popular && (
                  <div className="absolute -top-3 left-6">
                    <Badge className="bg-accent text-accent-foreground gap-1"><Star className="w-3 h-3" fill="currentColor" />Plus demandé</Badge>
                  </div>
                )}
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-accent/10 rounded-xl flex items-center justify-center">
                      <p.icon className="w-5 h-5 text-accent" strokeWidth={1.5} />
                    </div>
                    <div>
                      <CardTitle className="text-base">{p.title}</CardTitle>
                      {p.badge && <Badge variant="secondary" className="mt-1 text-xs">{p.badge}</Badge>}
                    </div>
                  </div>
                  <CardDescription className="mt-2 text-xs">{p.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex-1 pb-3">
                  <div className="mb-4">
                    <p className="text-xs text-muted-foreground">à partir de</p>
                    <p className="text-3xl font-bold">{p.price}<span className="text-base font-normal text-muted-foreground"> €</span></p>
                  </div>
                  <ul className="space-y-2">
                    {p.features.map((f, j) => (
                      <li key={j} className="flex items-start gap-2 text-xs"><CheckCircle className="w-3.5 h-3.5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />{f}</li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter className="flex flex-col gap-2 pt-0">
                  {p.valueProp && (
                    <p className="text-[10px] text-muted-foreground/50 italic w-full text-center mb-1">{p.valueProp}</p>
                  )}
                  <div className="flex gap-2 w-full">
                  <Button className="flex-1 rounded-lg gap-1.5 text-xs" variant={p.popular ? "default" : "outline"} onClick={() => openPaymentModal(p)} data-testid={`pay-button-${p.id}`}>
                    <CreditCard className="w-3.5 h-3.5" />Payer en ligne
                  </Button>
                  <Link to="/contact"><Button className="rounded-lg text-xs" variant="outline">Devis</Button></Link>
                  </div>
                </CardFooter>
              </Card>
            ))}
          </div>

          <div className="flex justify-center my-8">
            <div className="flex flex-col items-center text-muted-foreground">
              <ChevronRight className="w-5 h-5 rotate-90" />
              <span className="text-xs mt-1">Situation urgente ?</span>
            </div>
          </div>
        </div>
      </section>

      {/* ==================== ÉTAPE 4 : Pass Urgent ==================== */}
      <section className="section-padding relative overflow-clip pt-10" style={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)' }}>
        <div className="absolute inset-0 opacity-5" style={{ backgroundImage: 'radial-gradient(circle at 25% 50%, white 1px, transparent 1px)', backgroundSize: '30px 30px' }} />
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-full bg-amber-500 text-amber-950 flex items-center justify-center font-bold text-lg">4</div>
            <div>
              <h2 className="text-2xl font-semibold text-white">Votre situation ne peut pas attendre</h2>
              <p className="text-white/50 text-sm">Traitement prioritaire sous 48 heures</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5 stagger" ref={step4Ref}>
            {prestationsUrgentes.map((p, i) => (
              <div key={i} className="reveal group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-5 flex flex-col hover:bg-white/10 transition-all duration-300 hover:border-amber-500/30" data-testid={`urgent-card-${p.id}`}>
                <div className="absolute -top-3 right-4">
                  <span className="inline-flex items-center gap-1 bg-amber-500 text-amber-950 text-xs font-bold px-3 py-1 rounded-full shadow-lg shadow-amber-500/20">
                    <Zap className="w-3 h-3" fill="currentColor" />48h
                  </span>
                </div>
                <div className="flex items-center gap-3 mb-3 mt-1">
                  <div className="w-9 h-9 bg-amber-500/10 rounded-xl flex items-center justify-center">
                    <p.icon className="w-4 h-4 text-amber-400" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-semibold text-white text-sm">{p.title}</h3>
                </div>
                <div className="mb-4">
                  <span className="text-2xl font-bold text-white">{p.price}</span>
                  <span className="text-white/40 text-sm"> €</span>
                  <span className="block text-white/30 text-xs line-through mt-0.5">au lieu de {p.priceStandard} €</span>
                </div>
                <ul className="space-y-1.5 mb-5 flex-grow">
                  {p.features.map((f, j) => (
                    <li key={j} className="flex items-start gap-2 text-xs">
                      {j === 0 ? <Clock className="w-3 h-3 text-amber-400 flex-shrink-0 mt-0.5" strokeWidth={2} /> : <CheckCircle className="w-3 h-3 text-white/40 flex-shrink-0 mt-0.5" strokeWidth={1.5} />}
                      <span className={j === 0 ? "text-amber-300 font-medium" : "text-white/60"}>{f}</span>
                    </li>
                  ))}
                </ul>
                <Button className="w-full rounded-xl gap-1.5 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold text-xs border-0 mt-auto" onClick={() => openPaymentModal(p)} data-testid={`pay-button-${p.id}`}>
                  <Zap className="w-3.5 h-3.5" fill="currentColor" />Payer {p.price} €
                </Button>
              </div>
            ))}
          </div>
          <p className="text-center text-white/30 text-xs mt-6">Les réductions fidélité (-15%) et parrainage (-10%) s'appliquent aussi sur les Pass Urgent.</p>
        </div>
      </section>

      {/* Prestations Pro */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-semibold mb-2">Séminaires et conseil aux entreprises</h2>
          <p className="text-muted-foreground max-w-2xl mb-8 text-sm">Des interventions sur-mesure pour les organisations et professionnels.</p>
          <div className="grid md:grid-cols-2 gap-6 stagger" ref={proRef}>
            {[
              { icon: GraduationCap, title: "Séminaires et formations", description: "Sessions d'information et de formation pour particuliers, associations, professionnels de santé et entreprises.", features: ["En présentiel ou visioconférence", "Programme personnalisé", "Supports pédagogiques"] },
              { icon: Building2, title: "Conseil aux entreprises", description: "Accompagnement des structures sur les enjeux liés aux AT/MP, handicap et gestion des situations sensibles.", features: ["Sessions d'information RH", "Conférences de sensibilisation", "Accompagnement sur-mesure"] }
            ].map((p, i) => (
              <Card key={i} className="border-border card-glow reveal" data-testid={`tarif-pro-${i}`}>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-accent/10 rounded-xl flex items-center justify-center">
                      <p.icon className="w-5 h-5 text-accent" strokeWidth={1.5} />
                    </div>
                    <CardTitle className="text-lg">{p.title}</CardTitle>
                  </div>
                  <CardDescription className="mt-2 text-xs">{p.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold mb-4">Sur devis</p>
                  <ul className="space-y-2">
                    {p.features.map((f, j) => (
                      <li key={j} className="flex items-center gap-2 text-sm"><CheckCircle className="w-4 h-4 text-accent flex-shrink-0" strokeWidth={1.5} />{f}</li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter>
                  <Link to="/contact" className="w-full"><Button className="w-full rounded-lg" variant="outline">Nous contacter</Button></Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ==================== Justification tarifaire ==================== */}
      <section className="py-20 sm:py-24 bg-[#0c0c0c]" data-testid="tarifs-justification">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl sm:text-3xl font-semibold text-[#f5f0e8] mb-3">Comment nos tarifs sont construits</h2>
          <p className="text-sm sm:text-base text-[#f5f0e8]/50 mb-12 max-w-3xl leading-relaxed">
            Nos tarifs ne sont pas définis au hasard. Ils reflètent le temps d'analyse, le niveau de technicité mobilisé,
            la profondeur du travail réalisé et la valeur stratégique apportée à chaque dossier.
          </p>

          <div className="grid sm:grid-cols-2 gap-6">
            {[
              {
                icon: "Clock",
                title: "Temps réel mobilisé",
                text: "Chaque dossier nécessite un niveau d'attention, de lecture, de structuration et de réflexion différent. Nos tarifs tiennent compte du temps réellement nécessaire pour produire un travail utile, sérieux et exploitable."
              },
              {
                icon: "Brain",
                title: "Niveau d'expertise",
                text: "Nos analyses croisent les dimensions médicales, administratives, indemnitaires et stratégiques. L'objectif n'est pas de produire un simple texte, mais une lecture orientée décision."
              },
              {
                icon: "Sparkles",
                title: "Valeur concrète pour le client",
                text: "Une bonne orientation au bon moment peut éviter une erreur de procédure, une mauvaise stratégie ou une sous-évaluation du dossier — avec parfois un impact financier majeur."
              },
              {
                icon: "Scale",
                title: "Positionnement clair",
                text: "Nous nous situons entre l'information généraliste gratuite et l'intervention juridique spécialisée. Notre rôle : clarifier, structurer, sécuriser et faire gagner du temps."
              }
            ].map((item, i) => {
              const IconComp = { Clock, Brain, Sparkles, Scale }[item.icon];
              return (
                <div key={i} className="p-6 rounded-2xl border border-[#C9A84C]/10 bg-[#C9A84C]/[0.03]" data-testid={`justification-card-${i}`}>
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-9 h-9 rounded-xl bg-[#C9A84C]/10 flex items-center justify-center">
                      <IconComp className="w-4 h-4 text-[#C9A84C]" strokeWidth={1.5} />
                    </div>
                    <h3 className="font-semibold text-[#f5f0e8] text-sm">{item.title}</h3>
                  </div>
                  <p className="text-xs text-[#f5f0e8]/45 leading-relaxed">{item.text}</p>
                </div>
              );
            })}
          </div>

          {/* Phrase de réassurance */}
          <div className="mt-14 relative pl-6 sm:pl-8 border-l-2 border-[#C9A84C]/30" data-testid="tarifs-reassurance">
            <div className="absolute -left-[5px] top-0 w-2 h-2 rounded-full bg-[#C9A84C]" />
            <p className="text-base sm:text-lg text-[#f5f0e8]/70 leading-relaxed" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Vous ne payez pas pour du remplissage. Vous payez pour de la clarté, du ciblage, du temps gagné et des erreurs évitées.
            </p>
          </div>

          {/* Mini-FAQ Tarifaire */}
          <div className="mt-16 space-y-6" data-testid="tarifs-faq">
            <h3 className="text-lg font-semibold text-[#f5f0e8]/80 mb-6">Questions fréquentes</h3>
            {[
              {
                q: "Pourquoi vos prestations ne sont-elles pas gratuites ?",
                a: "Parce qu'un dossier sensible ne se joue pas sur une réponse générique. Chaque prestation repose sur un vrai travail d'analyse, de lecture, de structuration et d'orientation."
              },
              {
                q: "En quoi cela est-il différent d'une simple IA ?",
                a: "L'outil ne se contente pas de reformuler. Il a été structuré pour analyser des logiques de blocage, de preuves, de stratégie et de cohérence de dossier dans des situations souvent complexes."
              },
              {
                q: "Comment savoir si le prix est justifié pour mon dossier ?",
                a: "Le bon prix n'est pas seulement celui que l'on paie aujourd'hui, mais aussi celui des erreurs, des retards ou des leviers non exploités que l'on évite demain."
              }
            ].map((faq, i) => (
              <div key={i} className="border-b border-[#C9A84C]/10 pb-5" data-testid={`tarifs-faq-${i}`}>
                <p className="text-sm font-medium text-[#f5f0e8]/70 mb-2">{faq.q}</p>
                <p className="text-xs text-[#f5f0e8]/40 leading-relaxed">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Disclaimer Legal */}
      <section className="py-6 bg-amber-50/50 border-y border-amber-200/30">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-start gap-3" data-testid="tarifs-disclaimer">
            <Scale className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
            <p className="text-sm text-amber-900/70 leading-relaxed">
              <strong className="text-amber-900/90">Information importante :</strong> Stratégie & Expertise Santé propose un accompagnement stratégique et une analyse documentaire. 
              Ce service ne constitue pas une expertise médicale officielle ni une expertise judiciaire. 
              Les services proposés ne constituent pas un conseil juridique ni un avis médical. 
              Pour toute décision juridique ou médicale, consultez un professionnel qualifié.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="section-padding">
        <div className="max-w-3xl mx-auto text-center reveal" ref={ctaRef}>
          <h3 className="text-2xl font-semibold mb-3">Première consultation gratuite</h3>
          <p className="text-muted-foreground mb-6 text-sm">
            Chaque situation est unique. Avant tout engagement, je vous propose un premier
            échange téléphonique gratuit de 10 minutes.
          </p>
          <Link to="/agenda?type=decouverte">
            <Button size="lg" className="rounded-full px-8 gap-2" data-testid="tarifs-cta">
              Réserver mon appel gratuit <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Payment Modal */}
      <Dialog open={showPaymentModal} onOpenChange={handleModalClose}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Paiement sécurisé</DialogTitle>
            <DialogDescription>
              {selectedPackage && (
                <>
                  <span className="font-semibold text-foreground">{selectedPackage.title}</span>
                  <span className="block text-2xl font-bold text-foreground mt-2">
                    {getDiscountedPrice(selectedPackage.price) ? (
                      <><span className="line-through text-muted-foreground text-lg mr-2">{selectedPackage.price} €</span>{getDiscountedPrice(selectedPackage.price)} €</>
                    ) : <>{selectedPackage.price} €</>}
                  </span>
                  {getActiveDiscount().percent > 0 && (
                    <span className="inline-flex items-center gap-1 mt-1 text-sm text-green-600 bg-green-50 px-2 py-1 rounded-full">
                      <Tag className="w-3 h-3" />-{getActiveDiscount().percent}% {getActiveDiscount().type}
                    </span>
                  )}
                </>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="payment-email">Email *</Label>
              <Input id="payment-email" type="email" value={customerInfo.email} onChange={(e) => { setCustomerInfo(prev => ({ ...prev, email: e.target.value })); checkLoyaltyDiscount(e.target.value); }} placeholder="votre@email.fr" data-testid="payment-email-input" />
              {loyaltyDiscount > 0 && <p className="text-xs text-green-600 flex items-center gap-1"><CheckCircle className="w-3 h-3" />Client fidèle ! -15% appliqué</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="payment-name">Nom complet</Label>
              <Input id="payment-name" value={customerInfo.name} onChange={(e) => setCustomerInfo(prev => ({ ...prev, name: e.target.value }))} placeholder="Prénom Nom" data-testid="payment-name-input" />
            </div>
            {loyaltyDiscount === 0 && (
              <div className="space-y-2">
                <Label htmlFor="payment-referral" className="flex items-center gap-1"><Gift className="w-3 h-3 text-accent" />Code parrainage (optionnel)</Label>
                <div className="flex gap-2">
                  <Input id="payment-referral" value={customerInfo.referralCode} onChange={(e) => setCustomerInfo(prev => ({ ...prev, referralCode: e.target.value.toUpperCase() }))} placeholder="EX: ABC12345" className="flex-1" data-testid="payment-referral-input" />
                  <Button type="button" variant="outline" size="sm" onClick={() => validateReferral(customerInfo.referralCode)} disabled={!customerInfo.referralCode} data-testid="validate-referral-button">Valider</Button>
                </div>
                {referralValid === true && <p className="text-xs text-green-600 flex items-center gap-1"><CheckCircle className="w-3 h-3" />Code valide ! -10%</p>}
                {referralValid === false && <p className="text-xs text-destructive">Code invalide ou expiré</p>}
              </div>
            )}
            <div className="space-y-2">
              <Label>Mode de paiement</Label>
              <div className="grid grid-cols-2 gap-3">
                <button type="button" onClick={() => setPaymentMethod('stripe')} className={`flex items-center gap-2 p-3 rounded-lg border text-sm font-medium transition-all ${paymentMethod === 'stripe' ? 'border-accent bg-accent/10 text-accent' : 'border-border hover:border-accent/50'}`} data-testid="payment-method-stripe"><CreditCard className="w-4 h-4" /> Carte bancaire (Stripe)</button>
                <button type="button" onClick={() => setPaymentMethod('paypal')} className={`flex items-center gap-2 p-3 rounded-lg border text-sm font-medium transition-all ${paymentMethod === 'paypal' ? 'border-[#0070ba] bg-[#0070ba]/10 text-[#0070ba]' : 'border-border hover:border-[#0070ba]/50'}`} data-testid="payment-method-paypal"><Wallet className="w-4 h-4" /> PayPal</button>
              </div>
            </div>
          </div>

          <DialogFooter className="flex-col gap-2 sm:flex-col">
            {paymentMethod === 'stripe' ? (
              <div className="flex gap-2 w-full justify-end">
                <Button variant="outline" onClick={() => handleModalClose(false)}>Annuler</Button>
                <Button onClick={handlePayment} disabled={loading || !customerInfo.email} className="gap-2" data-testid="confirm-payment-button">
                  {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Redirection...</> : <><CreditCard className="w-4 h-4" />Payer {getDiscountedPrice(selectedPackage?.price) || selectedPackage?.price} €</>}
                </Button>
              </div>
            ) : (
              <div className="w-full space-y-3" data-testid="paypal-buttons-container">
                {!customerInfo.email ? (
                  <p className="text-sm text-center text-muted-foreground">Entrez votre email pour activer PayPal.</p>
                ) : (
                  <PayPalScriptProvider options={{ clientId: process.env.REACT_APP_PAYPAL_CLIENT_ID || 'sb', currency: 'EUR' }}>
                    <PayPalButtons
                      style={{ layout: 'horizontal', color: 'blue', shape: 'rect', label: 'pay', height: 45 }}
                      createOrder={async (data, actions) => {
                        const res = await axios.post(`${API}/paypal/calculate`, { package_id: selectedPackage.id, customer_email: customerInfo.email, customer_name: customerInfo.name, referral_code: referralValid ? customerInfo.referralCode : null });
                        return actions.order.create({ purchase_units: [{ amount: { currency_code: 'EUR', value: res.data.final_amount.toFixed(2) }, description: res.data.package_name }] });
                      }}
                      onApprove={async (data, actions) => {
                        const details = await actions.order.capture();
                        await axios.post(`${API}/paypal/record`, { order_id: details.id, package_id: selectedPackage.id, customer_email: customerInfo.email, customer_name: customerInfo.name, amount: parseFloat(getDiscountedPrice(selectedPackage?.price) || selectedPackage?.price), referral_code: referralValid ? customerInfo.referralCode : null });
                        setShowPaymentModal(false);
                        setPaymentDetails({ amount: getDiscountedPrice(selectedPackage?.price) || selectedPackage?.price, metadata: { package_name: selectedPackage?.title } });
                        setShowSuccessModal(true);
                        toast.success("Paiement PayPal réussi !");
                      }}
                      onError={() => toast.error("Erreur PayPal")}
                      onCancel={() => toast.info("Paiement annulé")}
                    />
                  </PayPalScriptProvider>
                )}
                <Button variant="outline" className="w-full" onClick={() => handleModalClose(false)}>Annuler</Button>
              </div>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Success Modal */}
      <Dialog open={showSuccessModal} onOpenChange={setShowSuccessModal}>
        <DialogContent className="max-w-md text-center">
          <div className="py-6">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <PartyPopper className="w-8 h-8 text-green-600" />
            </div>
            <DialogHeader>
              <DialogTitle className="text-2xl">Paiement réussi !</DialogTitle>
              <DialogDescription className="mt-4 space-y-2">
                <p>Merci pour votre confiance.</p>
                {paymentDetails && <p className="text-foreground font-medium">{paymentDetails.metadata?.package_name || 'Votre prestation'} - {paymentDetails.amount} €</p>}
                <p className="text-sm">Vous recevrez un email de confirmation. Je vous contacterai très prochainement.</p>
              </DialogDescription>
            </DialogHeader>
            <Button className="mt-6 rounded-full" onClick={() => { setShowSuccessModal(false); window.history.replaceState({}, '', '/tarifs'); }}>Fermer</Button>
          </div>
        </DialogContent>
      </Dialog>
    </main>
  );
};
