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
  PartyPopper
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
  const [customerInfo, setCustomerInfo] = useState({ email: '', name: '' });

  useEffect(() => {
    // Check for payment success
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
        customer_name: customerInfo.name
      });
      
      // Redirect to Stripe checkout
      window.location.href = response.data.url;
    } catch (error) {
      console.error('Payment error:', error);
      toast.error("Erreur lors de l'initialisation du paiement");
      setLoading(false);
    }
  };

  const openPaymentModal = (pkg) => {
    setSelectedPackage(pkg);
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
                    {selectedPackage.price} €
                  </span>
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
                onChange={(e) => setCustomerInfo(prev => ({ ...prev, email: e.target.value }))}
                placeholder="votre@email.fr"
                required
                data-testid="payment-email-input"
              />
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
                  Payer {selectedPackage?.price} €
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
