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
  ArrowRight, 
  FileSearch, 
  Shield, 
  Users, 
  Briefcase,
  CheckCircle,
  Star,
  GraduationCap,
  Building2,
  CreditCard,
  Loader2,
  PartyPopper,
  Gift,
  Percent,
  Tag,
  Zap,
  Clock
} from 'lucide-react';
import axios from 'axios';

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

  // Check loyalty discount when email changes
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

  // Validate referral code
  const validateReferral = async (code) => {
    if (!code || code.length < 3) {
      setReferralValid(null);
      return;
    }
    try {
      const response = await axios.get(`${API}/referral/validate/${code}`);
      setReferralValid(response.data.valid);
      if (response.data.valid) {
        toast.success("Code parrainage valide ! -10%");
      }
    } catch (error) {
      setReferralValid(false);
    }
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
    if (!customerInfo.email) {
      toast.error("Veuillez entrer votre email");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/payments/checkout`, {
        package_id: selectedPackage.id,
        origin_url: window.location.origin,
        customer_email: customerInfo.email,
        customer_name: customerInfo.name,
        referral_code: referralValid ? customerInfo.referralCode : null
      });
      
      window.location.href = response.data.url;
    } catch (error) {
      console.error('Payment error:', error);
      toast.error("Erreur lors de l'initialisation du paiement");
      setLoading(false);
    }
  };

  const openPaymentModal = (pkg) => {
    setSelectedPackage(pkg);
    setReferralValid(null);
    setLoyaltyDiscount(0);
    setCustomerInfo({ email: '', name: '', referralCode: '' });
    setShowPaymentModal(true);
  };

  const prestationsParticuliers = [
    {
      id: "analyse_dossier",
      icon: FileSearch,
      title: "Analyse de dossier",
      description: "Étude personnalisée du dossier médical et administratif. Identification des points forts, des faiblesses et des éléments manquants.",
      price: "150",
      priceNote: "à partir de",
      features: [
        "Lecture complète du dossier",
        "Rapport d'analyse détaillé",
        "Recommandations personnalisées",
        "Échange téléphonique de restitution"
      ],
      payable: true
    },
    {
      id: "preparation_expertise",
      icon: Shield,
      title: "Préparation expertise médicale",
      description: "Accompagnement pour aborder sereinement une expertise médicale. Préparation du dossier et conseils stratégiques.",
      price: "250",
      priceNote: "à partir de",
      features: [
        "Analyse du dossier médical",
        "Préparation des arguments",
        "Simulation d'entretien",
        "Liste des documents à apporter"
      ],
      popular: true,
      payable: true
    },
    {
      id: "accompagnement_mdph",
      icon: Users,
      title: "Accompagnement MDPH",
      description: "Aide à la compréhension et structuration du dossier MDPH. Orientation vers les droits possibles.",
      price: "200",
      priceNote: "à partir de",
      features: [
        "Analyse de votre situation",
        "Aide au formulaire",
        "Conseils sur les pièces justificatives",
        "Suivi de la demande"
      ],
      payable: true
    },
    {
      id: "protection_juridique",
      icon: Shield,
      title: "Protection juridique",
      description: "Accompagnement dans l'activation et le suivi de votre protection juridique.",
      price: "200",
      priceNote: "à partir de",
      features: [
        "Identification de vos garanties",
        "Aide à la déclaration du litige",
        "Suivi des échanges assureur",
        "Orientation vers avocat spécialisé"
      ],
      payable: true
    },
    {
      id: "accompagnement_complet",
      icon: Briefcase,
      title: "Accompagnement complet",
      description: "Suivi global dans les démarches administratives et médicales. Accompagnement personnalisé sur la durée.",
      price: "500",
      priceNote: "à partir de",
      badge: "Sur devis",
      features: [
        "Analyse complète de la situation",
        "Stratégie personnalisée",
        "Suivi des démarches",
        "Disponibilité continue"
      ],
      payable: true
    }
  ];

  const prestationsPro = [
    {
      icon: GraduationCap,
      title: "Séminaires et formations",
      description: "Sessions d'information et de formation pour particuliers, associations, professionnels de santé et entreprises.",
      price: "Sur devis",
      priceNote: "selon format et public",
      features: [
        "En présentiel ou visioconférence",
        "Conférences ou ateliers",
        "Programme personnalisé",
        "Supports pédagogiques"
      ]
    },
    {
      icon: Building2,
      title: "Conseil aux entreprises",
      description: "Accompagnement des structures sur les enjeux liés aux AT/MP, au handicap et à la gestion des situations sensibles.",
      price: "Sur devis",
      priceNote: "",
      features: [
        "Sessions d'information RH",
        "Conférences de sensibilisation",
        "Analyse de situations spécifiques",
        "Accompagnement sur-mesure"
      ]
    }
  ];

  const prestationsUrgentes = [
    {
      id: "urgent_analyse_dossier",
      icon: FileSearch,
      title: "Analyse de dossier",
      description: "Analyse prioritaire de votre dossier médical et administratif sous 48h.",
      price: "250",
      priceStandard: "150",
      features: [
        "Traitement prioritaire 48h",
        "Rapport d'analyse express",
        "Recommandations personnalisées",
        "Échange téléphonique immédiat"
      ],
      payable: true
    },
    {
      id: "urgent_preparation_expertise",
      icon: Shield,
      title: "Préparation expertise",
      description: "Préparation accélérée pour une expertise médicale imminente.",
      price: "400",
      priceStandard: "250",
      features: [
        "Traitement prioritaire 48h",
        "Préparation d'urgence",
        "Simulation d'entretien rapide",
        "Disponibilité immédiate"
      ],
      payable: true
    },
    {
      id: "urgent_accompagnement_mdph",
      icon: Users,
      title: "Accompagnement MDPH",
      description: "Aide express pour les dossiers MDPH avec échéance proche.",
      price: "320",
      priceStandard: "200",
      features: [
        "Traitement prioritaire 48h",
        "Constitution dossier express",
        "Suivi accéléré",
        "Interlocuteur dédié"
      ],
      payable: true
    },
    {
      id: "urgent_accompagnement_complet",
      icon: Briefcase,
      title: "Accompagnement complet",
      description: "Prise en charge globale et immédiate de votre situation urgente.",
      price: "750",
      priceStandard: "500",
      features: [
        "Traitement prioritaire 48h",
        "Analyse complète express",
        "Stratégie immédiate",
        "Disponibilité 7j/7"
      ],
      payable: true
    }
  ];

  return (
    <main className="page-transition pt-20">
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Tarifs</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="tarifs-title">
              Des prestations adaptées à vos besoins
            </h1>
            <p className="text-lg text-muted-foreground">
              Des tarifs transparents pour un accompagnement de qualité. 
              Paiement sécurisé en ligne ou premier échange gratuit pour un devis personnalisé.
            </p>
            <div className="flex items-center gap-2 mt-4 text-sm text-muted-foreground">
              <CreditCard className="w-4 h-4 text-accent" />
              <span>Paiement sécurisé par carte bancaire</span>
            </div>
          </div>
        </div>
      </section>

      {/* Discount Banner */}
      <section className="py-4 bg-accent/10 border-b border-accent/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Percent className="w-4 h-4 text-accent" />
              <span><strong>-15% fidélité</strong> dès votre 2ème prestation</span>
            </div>
            <span className="hidden sm:block text-muted-foreground">|</span>
            <div className="flex items-center gap-2">
              <Gift className="w-4 h-4 text-accent" />
              <span><strong>-10% parrainage</strong></span>
              <Link to="/parrainage" className="text-accent underline hover:no-underline ml-1">
                Obtenir un code
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Prestations Particuliers */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h2 className="text-3xl font-semibold mb-4">Accompagnement des particuliers</h2>
            <p className="text-muted-foreground max-w-2xl">
              Des services pensés pour vous accompagner à chaque étape de vos démarches.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {prestationsParticuliers.map((prestation, index) => (
              <Card 
                key={index} 
                className={`relative border-border flex flex-col ${prestation.popular ? 'ring-2 ring-accent' : ''}`}
                data-testid={`tarif-card-${index}`}
              >
                {prestation.popular && (
                  <div className="absolute -top-3 left-6">
                    <Badge className="bg-accent text-accent-foreground gap-1">
                      <Star className="w-3 h-3" fill="currentColor" />
                      Plus demandé
                    </Badge>
                  </div>
                )}
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center">
                        <prestation.icon className="w-6 h-6 text-accent" strokeWidth={1.5} />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{prestation.title}</CardTitle>
                        {prestation.badge && (
                          <Badge variant="secondary" className="mt-1">{prestation.badge}</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  <CardDescription className="mt-3">{prestation.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex-1">
                  <div className="mb-6">
                    <p className="text-sm text-muted-foreground">{prestation.priceNote}</p>
                    <p className="text-4xl font-bold text-foreground">
                      {prestation.price}
                      {prestation.price !== "Sur devis" && <span className="text-lg font-normal text-muted-foreground"> €</span>}
                    </p>
                  </div>
                  <ul className="space-y-3">
                    {prestation.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter className="flex gap-2">
                  {prestation.payable && (
                    <Button 
                      className="flex-1 rounded-lg gap-2" 
                      variant={prestation.popular ? "default" : "outline"}
                      onClick={() => openPaymentModal(prestation)}
                      data-testid={`pay-button-${prestation.id}`}
                    >
                      <CreditCard className="w-4 h-4" />
                      Payer en ligne
                    </Button>
                  )}
                  <Link to="/contact" className={prestation.payable ? "" : "w-full"}>
                    <Button className="rounded-lg w-full" variant="outline">
                      Devis
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pass Urgent Section */}
      <section className="section-padding relative overflow-hidden" style={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)' }}>
        {/* Subtle background pattern */}
        <div className="absolute inset-0 opacity-5" style={{ backgroundImage: 'radial-gradient(circle at 25% 50%, white 1px, transparent 1px)', backgroundSize: '30px 30px' }} />
        
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="mb-12 text-center">
            <div className="inline-flex items-center gap-2 bg-amber-500/20 border border-amber-500/30 text-amber-300 px-4 py-2 rounded-full mb-4" data-testid="urgent-badge">
              <Zap className="w-4 h-4" fill="currentColor" />
              <span className="text-sm font-semibold tracking-wider uppercase">Traitement Prioritaire 48h</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-semibold text-white mb-4">
              Pass Urgent
            </h2>
            <p className="text-white/60 max-w-2xl mx-auto">
              Votre situation ne peut pas attendre ? Bénéficiez d'un traitement prioritaire 
              avec une prise en charge sous 48 heures.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5">
            {prestationsUrgentes.map((prestation, index) => (
              <div
                key={index}
                className="group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 flex flex-col hover:bg-white/10 transition-all duration-300 hover:border-amber-500/30"
                data-testid={`urgent-card-${prestation.id}`}
              >
                {/* Urgent Badge */}
                <div className="absolute -top-3 right-4">
                  <span className="inline-flex items-center gap-1 bg-amber-500 text-amber-950 text-xs font-bold px-3 py-1 rounded-full shadow-lg shadow-amber-500/20">
                    <Zap className="w-3 h-3" fill="currentColor" />
                    48h
                  </span>
                </div>

                <div className="flex items-center gap-3 mb-4 mt-1">
                  <div className="w-10 h-10 bg-amber-500/10 rounded-xl flex items-center justify-center">
                    <prestation.icon className="w-5 h-5 text-amber-400" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-semibold text-white text-base">{prestation.title}</h3>
                </div>

                <p className="text-white/50 text-sm mb-5 flex-grow leading-relaxed">{prestation.description}</p>

                {/* Price */}
                <div className="mb-5">
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-white">{prestation.price}</span>
                    <span className="text-white/40 text-sm">€</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-white/30 text-xs line-through">au lieu de {prestation.priceStandard} €</span>
                  </div>
                </div>

                {/* Features */}
                <ul className="space-y-2 mb-6">
                  {prestation.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      {i === 0 ? (
                        <Clock className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" strokeWidth={2} />
                      ) : (
                        <CheckCircle className="w-3.5 h-3.5 text-white/40 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                      )}
                      <span className={i === 0 ? "text-amber-300 font-medium" : "text-white/60"}>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button 
                  className="w-full rounded-xl gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold border-0 mt-auto"
                  onClick={() => openPaymentModal(prestation)}
                  data-testid={`pay-button-${prestation.id}`}
                >
                  <Zap className="w-4 h-4" fill="currentColor" />
                  Payer {prestation.price} €
                </Button>
              </div>
            ))}
          </div>

          <p className="text-center text-white/30 text-sm mt-8">
            Les réductions fidélité (-15%) et parrainage (-10%) s'appliquent aussi sur les Pass Urgent.
          </p>
        </div>
      </section>

      {/* Prestations Pro */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h2 className="text-3xl font-semibold mb-4">Séminaires et conseil aux entreprises</h2>
            <p className="text-muted-foreground max-w-2xl">
              Des interventions sur-mesure pour les organisations et les professionnels.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {prestationsPro.map((prestation, index) => (
              <Card key={index} className="border-border" data-testid={`tarif-pro-${index}`}>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center">
                      <prestation.icon className="w-6 h-6 text-accent" strokeWidth={1.5} />
                    </div>
                    <CardTitle className="text-xl">{prestation.title}</CardTitle>
                  </div>
                  <CardDescription className="mt-3">{prestation.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="mb-6">
                    {prestation.priceNote && (
                      <p className="text-sm text-muted-foreground">{prestation.priceNote}</p>
                    )}
                    <p className="text-3xl font-bold text-foreground">{prestation.price}</p>
                  </div>
                  <ul className="space-y-3">
                    {prestation.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter>
                  <Link to="/contact" className="w-full">
                    <Button className="w-full rounded-lg" variant="outline">
                      Nous contacter
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Note Section */}
      <section className="section-padding">
        <div className="max-w-3xl mx-auto text-center">
          <h3 className="text-2xl font-semibold mb-4">Premier échange gratuit</h3>
          <p className="text-muted-foreground mb-8">
            Chaque situation est unique. Avant tout engagement, je vous propose un premier 
            échange téléphonique gratuit de 20 minutes pour comprendre votre situation 
            et voir comment je peux vous accompagner.
          </p>
          <Link to="/contact">
            <Button size="lg" className="rounded-full px-8 gap-2" data-testid="tarifs-cta">
              Prendre rendez-vous
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Payment Modal */}
      <Dialog open={showPaymentModal} onOpenChange={setShowPaymentModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Paiement sécurisé</DialogTitle>
            <DialogDescription>
              {selectedPackage && (
                <>
                  <span className="font-semibold text-foreground">{selectedPackage.title}</span>
                  <span className="block text-2xl font-bold text-foreground mt-2">
                    {getDiscountedPrice(selectedPackage.price) ? (
                      <>
                        <span className="line-through text-muted-foreground text-lg mr-2">{selectedPackage.price} €</span>
                        {getDiscountedPrice(selectedPackage.price)} €
                      </>
                    ) : (
                      <>{selectedPackage.price} €</>
                    )}
                  </span>
                  {getActiveDiscount().percent > 0 && (
                    <span className="inline-flex items-center gap-1 mt-1 text-sm text-green-600 bg-green-50 px-2 py-1 rounded-full">
                      <Tag className="w-3 h-3" />
                      -{getActiveDiscount().percent}% {getActiveDiscount().type}
                    </span>
                  )}
                </>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="payment-email">Email *</Label>
              <Input
                id="payment-email"
                type="email"
                value={customerInfo.email}
                onChange={(e) => {
                  setCustomerInfo(prev => ({ ...prev, email: e.target.value }));
                  checkLoyaltyDiscount(e.target.value);
                }}
                placeholder="votre@email.fr"
                required
                data-testid="payment-email-input"
              />
              {loyaltyDiscount > 0 && (
                <p className="text-xs text-green-600 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  Client fidèle ! -15% appliqué automatiquement
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="payment-name">Nom complet</Label>
              <Input
                id="payment-name"
                value={customerInfo.name}
                onChange={(e) => setCustomerInfo(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Prénom Nom"
                data-testid="payment-name-input"
              />
            </div>
            {loyaltyDiscount === 0 && (
              <div className="space-y-2">
                <Label htmlFor="payment-referral" className="flex items-center gap-1">
                  <Gift className="w-3 h-3 text-accent" />
                  Code parrainage (optionnel)
                </Label>
                <div className="flex gap-2">
                  <Input
                    id="payment-referral"
                    value={customerInfo.referralCode}
                    onChange={(e) => setCustomerInfo(prev => ({ ...prev, referralCode: e.target.value.toUpperCase() }))}
                    placeholder="EX: ABC12345"
                    className="flex-1"
                    data-testid="payment-referral-input"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => validateReferral(customerInfo.referralCode)}
                    disabled={!customerInfo.referralCode}
                    data-testid="validate-referral-button"
                  >
                    Valider
                  </Button>
                </div>
                {referralValid === true && (
                  <p className="text-xs text-green-600 flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" />
                    Code valide ! -10% appliqué
                  </p>
                )}
                {referralValid === false && (
                  <p className="text-xs text-destructive">Code invalide ou expiré</p>
                )}
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              Vous serez redirigé vers notre plateforme de paiement sécurisée (Stripe).
            </p>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPaymentModal(false)}>
              Annuler
            </Button>
            <Button 
              onClick={handlePayment} 
              disabled={loading}
              className="gap-2"
              data-testid="confirm-payment-button"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Redirection...
                </>
              ) : (
                <>
                  <CreditCard className="w-4 h-4" />
                  Payer {getDiscountedPrice(selectedPackage?.price) || selectedPackage?.price} €
                </>
              )}
            </Button>
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
                {paymentDetails && (
                  <p className="text-foreground font-medium">
                    {paymentDetails.metadata?.package_name || 'Votre prestation'} - {paymentDetails.amount} €
                  </p>
                )}
                <p className="text-sm">
                  Vous recevrez un email de confirmation. Je vous contacterai très prochainement 
                  pour organiser notre premier échange.
                </p>
              </DialogDescription>
            </DialogHeader>
            <Button 
              className="mt-6 rounded-full"
              onClick={() => {
                setShowSuccessModal(false);
                window.history.replaceState({}, '', '/tarifs');
              }}
            >
              Fermer
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </main>
  );
};
