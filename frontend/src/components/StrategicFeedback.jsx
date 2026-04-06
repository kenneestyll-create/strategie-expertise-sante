import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { MessageCircle, Send, Check, X, ChevronDown } from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CLARTE_OPTIONS = [
  { value: 'oui', label: 'Oui, tres clairement' },
  { value: 'partiellement', label: 'Partiellement' },
  { value: 'non', label: 'Non, pas assez clairement' },
];

export const StrategicFeedback = ({ source = '', typeDossier = '' }) => {
  const [open, setOpen] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const [frein, setFrein] = useState('');
  const [besoin, setBesoin] = useState('');
  const [clarte, setClarte] = useState('');
  const [commentaire, setCommentaire] = useState('');

  // Verifie si deja affiche cette session
  const storageKey = `ses_feedback_${source}`;
  if (typeof window !== 'undefined' && sessionStorage.getItem(storageKey)) {
    return null;
  }

  if (dismissed) return null;

  if (submitted) {
    return (
      <div className="mt-4 p-3 rounded-xl border border-emerald-200 bg-emerald-50/40 text-center" data-testid="feedback-success">
        <div className="flex items-center justify-center gap-2 text-sm text-emerald-700">
          <Check className="w-4 h-4" />
          <span>Merci pour votre retour. Il nous aide a mieux vous accompagner.</span>
        </div>
      </div>
    );
  }

  const handleSubmit = async () => {
    if (!clarte && !frein.trim() && !besoin.trim()) return;
    setSubmitting(true);
    try {
      await axios.post(`${API}/feedback`, {
        frein, besoin, clarte, commentaire,
        source, type_dossier: typeDossier,
      });
      setSubmitted(true);
      sessionStorage.setItem(storageKey, '1');
    } catch {
      // Silencieux — le feedback n'est pas critique
    } finally {
      setSubmitting(false);
    }
  };

  const handleDismiss = () => {
    setDismissed(true);
    sessionStorage.setItem(storageKey, '1');
  };

  if (!open) {
    return (
      <div className="mt-4" data-testid="feedback-trigger">
        <button
          onClick={() => setOpen(true)}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border border-dashed border-muted-foreground/20 bg-muted/20 hover:bg-muted/40 transition-colors text-xs text-muted-foreground"
        >
          <MessageCircle className="w-3.5 h-3.5" />
          <span>Votre avis nous aide a progresser</span>
          <ChevronDown className="w-3 h-3" />
        </button>
      </div>
    );
  }

  return (
    <div className="mt-4 rounded-xl border border-border/60 bg-card overflow-hidden" data-testid="feedback-form">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-border/40 bg-muted/20">
        <span className="text-xs font-medium flex items-center gap-1.5">
          <MessageCircle className="w-3.5 h-3.5 text-muted-foreground" />
          Retour d'experience (facultatif)
        </span>
        <button onClick={handleDismiss} className="p-1 rounded hover:bg-muted" data-testid="feedback-dismiss">
          <X className="w-3.5 h-3.5 text-muted-foreground" />
        </button>
      </div>

      <div className="p-4 space-y-4">
        {/* Q1 — Frein */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-foreground/80">
            Qu'est-ce qui vous a le plus freine ou manque dans votre situation ?
          </label>
          <Textarea
            value={frein} onChange={e => setFrein(e.target.value)}
            placeholder="Ex : je ne savais pas par ou commencer, il me manquait..."
            className="h-16 text-xs resize-none"
            maxLength={500}
            data-testid="feedback-frein"
          />
        </div>

        {/* Q2 — Besoin */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-foreground/80">
            Y a-t-il un accompagnement que vous auriez aime trouver ici ?
          </label>
          <Textarea
            value={besoin} onChange={e => setBesoin(e.target.value)}
            placeholder="Ex : un suivi personnalise, une aide pour les formulaires..."
            className="h-16 text-xs resize-none"
            maxLength={500}
            data-testid="feedback-besoin"
          />
        </div>

        {/* Q3 — Clarte */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-foreground/80">
            Avez-vous compris ce que le cabinet pouvait faire pour vous ?
          </label>
          <div className="flex flex-wrap gap-1.5" data-testid="feedback-clarte">
            {CLARTE_OPTIONS.map(opt => (
              <button key={opt.value}
                onClick={() => setClarte(opt.value)}
                className={`px-3 py-1.5 rounded-full text-xs transition-colors border ${clarte === opt.value
                  ? 'bg-foreground text-background border-foreground'
                  : 'bg-transparent text-foreground/70 border-border hover:border-foreground/30'
                }`}
                data-testid={`feedback-clarte-${opt.value}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Champ libre */}
        <div className="space-y-1.5">
          <label className="text-[11px] text-muted-foreground">
            Si vous souhaitez preciser quelque chose (facultatif) :
          </label>
          <Textarea
            value={commentaire} onChange={e => setCommentaire(e.target.value)}
            className="h-12 text-xs resize-none"
            maxLength={300}
            data-testid="feedback-commentaire"
          />
        </div>

        {/* Submit */}
        <Button size="sm" onClick={handleSubmit} disabled={submitting || (!clarte && !frein.trim() && !besoin.trim())}
          className="w-full h-9 text-xs gap-1.5" data-testid="feedback-submit">
          {submitting ? <span className="w-3.5 h-3.5 border-2 border-t-transparent border-current rounded-full animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          Envoyer mon retour
        </Button>

        <p className="text-[10px] text-muted-foreground text-center">
          Vos reponses sont anonymes et servent uniquement a ameliorer nos services.
        </p>
      </div>
    </div>
  );
};
