import { useState } from 'react';
import axios from 'axios';
import { Mail, ShieldCheck, Loader2, ArrowRight, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/**
 * PillarLeadMagnet — sober, premium lead magnet block for SEO pillar pages.
 *
 * Props:
 *   pageId: 'mdph' | 'accident-travail-maladie-professionnelle' | 'expertise-medicale'
 *           | 'calculatrice-ipp' | 'calculatrice-aah'
 *   memoTitle: short headline shown above the email field (page-specific)
 *   bulletPoints?: optional 3-4 strings for value preview
 */
export const PillarLeadMagnet = ({ pageId, memoTitle, bulletPoints = [] }) => {
  const [email, setEmail] = useState('');
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (!email.trim()) {
      setError('Veuillez saisir votre adresse email.');
      return;
    }
    if (!consent) {
      setError('Merci de cocher le consentement RGPD pour recevoir le mémo.');
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API}/leads/pillar-subscribe`, {
        email: email.trim(),
        page_id: pageId,
        consent: true,
        page_url: typeof window !== 'undefined' ? window.location.pathname : null,
      });
      setDone(true);
    } catch (err) {
      setError(err?.response?.data?.detail || "Une erreur est survenue. Réessayez dans un instant.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      className="my-10 sm:my-14 rounded-2xl border border-[#C9A84C]/30 bg-gradient-to-br from-[#1a1814] via-[#13110d] to-[#0f0d0a] text-[#f4ecd6] p-6 sm:p-9 shadow-lg"
      data-testid={`pillar-lead-magnet-${pageId}`}
      aria-labelledby={`pillar-lead-${pageId}-title`}
    >
      {!done ? (
        <div className="grid lg:grid-cols-[1.4fr_1fr] gap-6 items-start">
          {/* Left: Value */}
          <div>
            <p className="inline-flex items-center gap-2 text-[10px] tracking-[0.18em] uppercase text-[#C9A84C] font-semibold mb-3">
              <Mail className="w-3.5 h-3.5" /> Mémo gratuit · format email
            </p>
            <h2
              id={`pillar-lead-${pageId}-title`}
              className="text-xl sm:text-2xl font-semibold leading-snug font-serif"
              data-testid={`pillar-lead-magnet-title-${pageId}`}
            >
              {memoTitle}
            </h2>
            {bulletPoints.length > 0 && (
              <ul className="mt-4 space-y-2 text-sm text-[#f4ecd6]/85">
                {bulletPoints.map((b, i) => (
                  <li key={i} className="flex gap-2 items-start">
                    <ArrowRight className="w-3.5 h-3.5 text-[#C9A84C] mt-0.5 flex-shrink-0" />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            )}
            <p className="mt-4 text-[11px] text-[#f4ecd6]/55 flex items-center gap-1.5">
              <ShieldCheck className="w-3 h-3" /> Aucun spam. Désinscription en 1 clic.
            </p>
          </div>

          {/* Right: Form */}
          <form onSubmit={submit} className="space-y-3 bg-[#1f1d18]/60 border border-[#C9A84C]/15 rounded-xl p-4 sm:p-5" data-testid={`pillar-lead-form-${pageId}`}>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="votre@email.fr"
              autoComplete="email"
              required
              className="bg-[#0f0d0a] border-[#C9A84C]/30 text-[#f4ecd6] placeholder:text-[#f4ecd6]/40 focus-visible:ring-[#C9A84C]"
              data-testid={`pillar-lead-email-${pageId}`}
            />
            <label className="flex gap-2 items-start text-[11px] text-[#f4ecd6]/75 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                className="mt-0.5 w-3.5 h-3.5 accent-[#C9A84C] flex-shrink-0"
                data-testid={`pillar-lead-consent-${pageId}`}
              />
              <span>
                J'accepte de recevoir ce mémo et la communication conforme RGPD de Stratégie &amp; Expertise Santé.
              </span>
            </label>
            {error && (
              <p className="text-[12px] text-red-300" role="alert" data-testid={`pillar-lead-error-${pageId}`}>
                {error}
              </p>
            )}
            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-[#C9A84C] hover:bg-[#B89640] text-[#0a0a08] font-semibold gap-2"
              data-testid={`pillar-lead-submit-${pageId}`}
            >
              {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Envoi…</> : <>Recevoir le mémo <ArrowRight className="w-4 h-4" /></>}
            </Button>
          </form>
        </div>
      ) : (
        <div className="text-center py-4" data-testid={`pillar-lead-success-${pageId}`}>
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-[#C9A84C]/15 border border-[#C9A84C]/40 mb-3">
            <CheckCircle2 className="w-6 h-6 text-[#C9A84C]" />
          </div>
          <h3 className="text-lg font-semibold font-serif">Mémo envoyé à votre adresse.</h3>
          <p className="mt-2 text-sm text-[#f4ecd6]/75">
            Vérifiez votre boîte de réception (et vos spams au cas où). Vous recevrez le mémo dans la minute.
          </p>
        </div>
      )}
    </section>
  );
};

export default PillarLeadMagnet;
