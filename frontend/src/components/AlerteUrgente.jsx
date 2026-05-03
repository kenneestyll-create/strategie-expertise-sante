import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { X, Zap, Phone, Clock, Send, CheckCircle, CreditCard, Loader2, Shield } from 'lucide-react';
import axios from 'axios';
import { useSearchParams } from 'react-router-dom';
import { useVip } from '@/context/VipContext';
import { PayPalScriptProvider, PayPalButtons } from '@paypal/react-paypal-js';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const AlerteUrgente = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [formule, setFormule] = useState('2h');
  const { isVip, vipName } = useVip();
  const [nom, setNom] = useState('');
  const [telephone, setTelephone] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [confirmedFormule, setConfirmedFormule] = useState('');
  const [showRecap, setShowRecap] = useState(false);
  const [cgvAccepted, setCgvAccepted] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    const onOpen = () => setIsOpen(true);
    window.addEventListener('alerte-urgente:open', onOpen);
    return () => window.removeEventListener('alerte-urgente:open', onOpen);
  }, []);

  // Handle Stripe return
  useEffect(() => {
    const urgentPayment = searchParams.get('urgent_payment');
    const sessionId = searchParams.get('session_id');
    const alertId = searchParams.get('alert_id');

    if (urgentPayment === 'success' && sessionId) {
      setIsOpen(true);
      setSending(true);
      axios.get(`${API}/alerte-urgente/confirm-payment/${sessionId}`)
        .then(res => {
          if (res.data.success) {
            setConfirmed(true);
            setConfirmedFormule(res.data.formule || '2h');
            toast.success('Paiement confirmé ! Votre demande urgente est enregistrée.');
          } else {
            toast.error('Le paiement n\'a pas été finalisé.');
          }
        })
        .catch(() => toast.error('Erreur de vérification du paiement.'))
        .finally(() => {
          setSending(false);
          const newParams = new URLSearchParams(searchParams);
          newParams.delete('urgent_payment');
          newParams.delete('session_id');
          setSearchParams(newParams, { replace: true });
        });
    } else if (urgentPayment === 'cancelled') {
      toast.error('Paiement annulé. La demande n\'a pas été envoyée.');
      if (alertId) {
        axios.delete(`${API}/alerte-urgente/cancel/${alertId}`).catch(() => {});
      }
      const newParams = new URLSearchParams(searchParams);
      newParams.delete('urgent_payment');
      newParams.delete('alert_id');
      setSearchParams(newParams, { replace: true });
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!nom.trim() || !telephone.trim() || !email.trim() || !email.includes('@')) {
      toast.error('Veuillez renseigner votre nom, téléphone et email');
      return;
    }
    setShowRecap(true);
  };

  const handlePay = async () => {
    if (!isVip && !cgvAccepted) {
      toast.error('Veuillez accepter les CGV et la renonciation au droit de rétractation.');
      return;
    }
    // VIP bypass
    if (isVip) {
      setSending(true);
      try {
        await axios.post(`${API}/alerte-urgente/vip`, { nom, telephone, email, message, formule });
        setConfirmed(true);
        setConfirmedFormule(formule);
        toast.success(`Accès Partenaire VIP (${vipName}) : alerte envoyée sans paiement.`);
      } catch {
        toast.error("Erreur lors de l'envoi de l'alerte.");
      }
      setSending(false);
      return;
    }
    setSending(true);
    try {
      await axios.post(`${API}/consent-log`, {
        email, service: `question_urgente_${formule}`, cgv_accepted: true, retractation_waived: true,
      });
      const res = await axios.post(`${API}/alerte-urgente`, {
        nom, telephone, email, message, formule,
        origin_url: window.location.origin,
      });
      if (res.data.url) {
        window.location.href = res.data.url;
      } else {
        toast.error('Erreur lors de la redirection vers le paiement.');
        setSending(false);
      }
    } catch (err) {
      const detail = err.response?.data?.detail || "Erreur lors de la création du paiement.";
      toast.error(detail);
      setSending(false);
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    setShowRecap(false);
    if (confirmed) {
      setConfirmed(false);
      setConfirmedFormule('');
      setNom('');
      setTelephone('');
      setEmail('');
      setMessage('');
      setFormule('2h');
    }
  };

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 flex items-center justify-center p-4" style={{ zIndex: 'var(--z-chatbot)' }}>
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={handleClose} />

          <div className="relative w-full max-w-md bg-background border border-border rounded-2xl shadow-2xl overflow-hidden" data-testid="alerte-urgente-modal">
            {/* Header */}
            <div className="flex items-center justify-between p-5 bg-orange-500 text-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <Zap className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-base">Question urgente</h3>
                  <p className="text-xs text-white/80">Réponse garantie sous 2h</p>
                </div>
              </div>
              <button onClick={handleClose} className="p-2 hover:bg-white/10 rounded-lg transition-colors" aria-label="Fermer">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Confirming payment state */}
            {sending && !confirmed && (
              <div className="p-8 text-center" data-testid="alerte-urgente-confirming">
                <Loader2 className="w-12 h-12 text-orange-500 mx-auto mb-4 animate-spin" />
                <p className="text-sm text-muted-foreground">Vérification du paiement en cours...</p>
              </div>
            )}

            {/* Confirmed state */}
            {confirmed && (
              <div className="p-8 text-center" data-testid="alerte-urgente-success">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Paiement confirmé !</h3>
                <p className="text-muted-foreground text-sm mb-1">
                  Votre demande urgente a été enregistrée et payée.
                </p>
                <p className="text-sm font-medium text-accent">
                  {confirmedFormule === '30min' ? 'Nous vous rappelons sous 30 minutes.' : 'Réponse garantie sous 2 heures.'}
                </p>
                <Button onClick={handleClose} className="mt-6 rounded-full" data-testid="alerte-urgente-close-success">
                  Fermer
                </Button>
              </div>
            )}

            {/* Recap before payment */}
            {showRecap && !confirmed && !sending && (
              <div className="p-5 space-y-4" data-testid="alerte-urgente-recap">
                <div className="text-center mb-2">
                  <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Récapitulatif</p>
                </div>

                <div className="rounded-xl border-2 border-orange-200 bg-orange-50/50 p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Formule</span>
                    <span className="text-sm font-semibold flex items-center gap-1.5">
                      {formule === '30min' ? <Zap className="w-3.5 h-3.5 text-orange-600" /> : <Clock className="w-3.5 h-3.5 text-orange-600" />}
                      Réponse sous {formule === '30min' ? '30 minutes' : '2 heures'}
                    </span>
                  </div>
                  <hr className="border-orange-200/60" />
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Nom</span>
                    <span className="text-sm font-medium">{nom}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Téléphone</span>
                    <span className="text-sm font-medium">{telephone}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Email</span>
                    <span className="text-sm font-medium text-xs">{email}</span>
                  </div>
                  {message && (
                    <>
                      <hr className="border-orange-200/60" />
                      <div>
                        <span className="text-xs text-muted-foreground">Message</span>
                        <p className="text-sm mt-0.5 line-clamp-2">{message}</p>
                      </div>
                    </>
                  )}
                  <hr className="border-orange-200/60" />
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold">Total à payer</span>
                    <span className="text-2xl font-bold text-orange-600">{formule === '30min' ? '80€' : '50€'}</span>
                  </div>
                </div>

                <div className="flex items-start gap-3 mt-1">
                  <input
                    type="checkbox"
                    id="cgv-urgent"
                    checked={cgvAccepted}
                    onChange={(e) => setCgvAccepted(e.target.checked)}
                    className="mt-0.5 w-5 h-5 min-w-[20px] rounded border-gray-300 text-accent focus:ring-accent cursor-pointer"
                    data-testid="cgv-consent-checkbox"
                  />
                  <label htmlFor="cgv-urgent" className="text-xs text-muted-foreground leading-relaxed cursor-pointer">
                    J'accepte les{' '}
                    <a href="/mentions-legales?tab=cgv" target="_blank" rel="noopener" className="text-accent underline">
                      Conditions Générales de Vente
                    </a>{' '}
                    et je renonce expressément à mon droit de rétractation conformément à l'article L.221-28 du Code de la consommation,
                    la prestation étant exécutée immédiatement après le paiement.
                  </label>
                </div>

                {cgvAccepted && (
                  <div className="grid grid-cols-2 gap-3">
                    <Button
                      onClick={handlePay}
                      disabled={sending}
                      className="gap-2 h-11 bg-orange-500 hover:bg-orange-600 text-white"
                      data-testid="alerte-recap-pay-button"
                    >
                      {sending ? <><Loader2 className="w-4 h-4 animate-spin" /> Chargement...</> : <><CreditCard className="w-4 h-4" />{formule === '30min' ? '80€' : '50€'} — Carte</>}
                    </Button>
                    <div className="h-11" data-testid="alerte-paypal-container">
                      <PayPalScriptProvider options={{ clientId: process.env.REACT_APP_PAYPAL_CLIENT_ID || 'sb', currency: 'EUR' }}>
                        <PayPalButtons
                          style={{ layout: 'horizontal', color: 'blue', shape: 'rect', label: 'pay', height: 44, tagline: false }}
                          createOrder={async (data, actions) => {
                            const amount = formule === '30min' ? '80.00' : '50.00';
                            const desc = formule === '30min' ? 'Question urgente — Réponse sous 30 min' : 'Question urgente — Réponse sous 2h';
                            return actions.order.create({ purchase_units: [{ amount: { currency_code: 'EUR', value: amount }, description: desc }] });
                          }}
                          onApprove={async (data, actions) => {
                            const details = await actions.order.capture();
                            const amount = formule === '30min' ? 80 : 50;
                            try {
                              await axios.post(`${API}/consent-log`, { email, service: `question_urgente_${formule}`, cgv_accepted: true, retractation_waived: true });
                              await axios.post(`${API}/alerte-urgente/paypal`, { order_id: details.id, nom, telephone, email, message, formule, amount });
                              setShowRecap(false);
                              setConfirmed(true);
                              setConfirmedFormule(formule);
                              toast.success('Paiement PayPal confirmé !');
                            } catch { toast.error("Erreur lors de l'enregistrement PayPal"); }
                          }}
                          onError={() => toast.error("Erreur PayPal")}
                          onCancel={() => toast.info("Paiement annulé")}
                        />
                      </PayPalScriptProvider>
                    </div>
                  </div>
                )}

                {!cgvAccepted && (
                  <Button disabled className="w-full rounded-lg gap-2 opacity-50" data-testid="alerte-recap-pay-disabled">
                    <CreditCard className="w-4 h-4" />
                    Acceptez les CGV pour payer
                  </Button>
                )}

                <button
                  type="button"
                  onClick={() => setShowRecap(false)}
                  className="w-full text-center text-xs text-muted-foreground hover:text-foreground transition-colors py-1"
                  data-testid="alerte-recap-back"
                >
                  Modifier ma demande
                </button>

                <p className="text-[11px] text-muted-foreground/60 text-center">Paiements sécurisés — Stripe & PayPal</p>
              </div>
            )}

            {/* Form */}
            {!confirmed && !sending && !showRecap && (
              <form onSubmit={handleSubmit} className="p-5 space-y-4" data-testid="alerte-urgente-form">
                {/* Formule selection */}
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setFormule('2h')}
                    className={`p-3 rounded-xl border-2 text-left transition-all ${
                      formule === '2h'
                        ? 'border-orange-500 bg-orange-50'
                        : 'border-border hover:border-orange-300'
                    }`}
                    data-testid="formule-2h"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Clock className="w-4 h-4 text-orange-600" />
                      <span className="text-sm font-semibold">Sous 2h</span>
                    </div>
                    <span className="text-xl font-bold text-orange-600">50€</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormule('30min')}
                    className={`p-3 rounded-xl border-2 text-left transition-all ${
                      formule === '30min'
                        ? 'border-orange-500 bg-orange-50'
                        : 'border-border hover:border-orange-300'
                    }`}
                    data-testid="formule-30min"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Zap className="w-4 h-4 text-orange-600" />
                      <span className="text-sm font-semibold">Sous 30min</span>
                    </div>
                    <span className="text-xl font-bold text-orange-600">80€</span>
                  </button>
                </div>

                {/* Name */}
                <div className="space-y-1.5">
                  <Label htmlFor="alerte-nom" className="text-sm font-medium">Nom complet *</Label>
                  <Input
                    id="alerte-nom"
                    value={nom}
                    onChange={e => setNom(e.target.value)}
                    placeholder="Votre nom"
                    required
                    data-testid="alerte-nom-input"
                  />
                </div>

                {/* Phone */}
                <div className="space-y-1.5">
                  <Label htmlFor="alerte-tel" className="text-sm font-medium">Téléphone *</Label>
                  <Input
                    id="alerte-tel"
                    value={telephone}
                    onChange={e => setTelephone(e.target.value)}
                    placeholder="06 12 34 56 78"
                    type="tel"
                    required
                    data-testid="alerte-tel-input"
                  />
                </div>

                {/* Email */}
                <div className="space-y-1.5">
                  <Label htmlFor="alerte-email" className="text-sm font-medium">Email *</Label>
                  <Input
                    id="alerte-email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    placeholder="votre@email.fr"
                    type="email"
                    required
                    data-testid="alerte-email-input"
                  />
                </div>

                {/* Message */}
                <div className="space-y-1.5">
                  <Label htmlFor="alerte-msg" className="text-sm font-medium">Décrivez brièvement votre blocage</Label>
                  <textarea
                    id="alerte-msg"
                    value={message}
                    onChange={e => setMessage(e.target.value)}
                    placeholder="Ex: Mon dossier MDPH a été refusé et le délai de recours expire bientôt..."
                    className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring min-h-[80px] resize-none"
                    data-testid="alerte-message-input"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={sending}
                  className="w-full rounded-lg gap-2 bg-orange-500 hover:bg-orange-600 text-white"
                  data-testid="alerte-submit-button"
                >
                  <CreditCard className="w-4 h-4" />
                  Payer et envoyer ma demande ({formule === '30min' ? '80€' : '50€'})
                </Button>

                <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
                  <CreditCard className="w-3 h-3" />
                  <span>Paiement sécurisé par Stripe</span>
                </div>

                <p className="text-xs text-muted-foreground text-center">
                  <Phone className="w-3 h-3 inline mr-1" />
                  {formule === '30min'
                    ? 'Nous vous rappelons sous 30 minutes après confirmation du paiement.'
                    : 'Réponse garantie sous 2 heures après confirmation du paiement.'}
                </p>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
};
