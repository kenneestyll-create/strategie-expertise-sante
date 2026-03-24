import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { X, Zap, Phone, Clock, Send, CheckCircle } from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const AlerteUrgente = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [formule, setFormule] = useState('2h');
  const [nom, setNom] = useState('');
  const [telephone, setTelephone] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!nom.trim() || !telephone.trim()) {
      toast.error('Veuillez renseigner votre nom et téléphone');
      return;
    }
    setSending(true);
    try {
      await axios.post(`${API}/alerte-urgente`, { nom, telephone, email, message, formule });
      setSent(true);
      toast.success('Demande urgente envoyée ! Nous vous rappelons très vite.');
    } catch {
      toast.error("Erreur lors de l'envoi. Réessayez.");
    } finally {
      setSending(false);
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    if (sent) {
      setSent(false);
      setNom('');
      setTelephone('');
      setEmail('');
      setMessage('');
      setFormule('2h');
    }
  };

  return (
    <>
      {/* Floating Button — Urgence bottom-left */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed flex items-center gap-2 px-4 py-2.5 rounded-full shadow-xl text-white font-semibold text-xs transition-all hover:scale-105 border border-red-500/30"
          style={{
            zIndex: 39,
            background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)',
            bottom: 'calc(1.5rem + env(safe-area-inset-bottom, 0px))',
            left: '1rem',
          }}
          data-testid="alerte-urgente-button"
          aria-label="Question urgente"
        >
          <Zap className="w-4 h-4 text-yellow-300" />
          <span className="hidden sm:inline">Urgence — réponse sous 2h</span>
          <span className="sm:hidden">Urgence</span>
        </button>
      )}

      {/* Modal */}
      {isOpen && (
        <div className="fixed inset-0 flex items-center justify-center p-4" style={{ zIndex: 'var(--z-chatbot)' }}>
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={handleClose} />

          {/* Panel */}
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

            {sent ? (
              /* Success state */
              <div className="p-8 text-center" data-testid="alerte-urgente-success">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Demande envoyée !</h3>
                <p className="text-muted-foreground text-sm mb-1">
                  Nous avons bien reçu votre demande urgente.
                </p>
                <p className="text-sm font-medium text-accent">
                  {formule === '30min' ? 'Rappel sous 30 minutes garanti.' : 'Réponse garantie sous 2 heures.'}
                </p>
                <Button onClick={handleClose} className="mt-6 rounded-full" data-testid="alerte-urgente-close-success">
                  Fermer
                </Button>
              </div>
            ) : (
              /* Form */
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

                {/* Email (optional) */}
                <div className="space-y-1.5">
                  <Label htmlFor="alerte-email" className="text-sm font-medium">Email (optionnel)</Label>
                  <Input
                    id="alerte-email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    placeholder="votre@email.fr"
                    type="email"
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
                  {sending ? (
                    'Envoi en cours...'
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Envoyer ma demande urgente
                    </>
                  )}
                </Button>

                <p className="text-xs text-muted-foreground text-center">
                  <Phone className="w-3 h-3 inline mr-1" />
                  {formule === '30min'
                    ? 'Nous vous rappelons sous 30 minutes.'
                    : 'Réponse garantie sous 2 heures.'}
                </p>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
};
