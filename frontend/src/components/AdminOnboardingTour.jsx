import { useState, useEffect, useCallback } from 'react';
import { ChevronRight, ChevronLeft } from 'lucide-react';

const TOUR_KEY = 'ses_admin_onboarding_done';
const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function trackEvent(event, step, token) {
  if (!token) return;
  fetch(`${API}/admin/onboarding/track`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ event, step }),
  }).catch(() => {});
}

const StrateTourSVG = ({ size = 28 }) => (
  <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect x="20" y="8" width="24" height="48" rx="12" fill="#1a1a1a" stroke="#C9A84C" strokeWidth="2.5"/>
    <rect x="24" y="12" width="16" height="20" rx="8" fill="#2a2a2a" stroke="#C9A84C" strokeWidth="1.5"/>
    <circle cx="28" cy="22" r="2.5" fill="#C9A84C"/><circle cx="36" cy="22" r="2.5" fill="#C9A84C"/>
    <circle cx="28.8" cy="21.5" r="1" fill="#fff"/><circle cx="36.8" cy="21.5" r="1" fill="#fff"/>
    <path d="M28 27 Q32 31 36 27" stroke="#C9A84C" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
    <path d="M26 38 L32 35 L38 38 L38 46 Q32 50 26 46 Z" fill="#C9A84C" fillOpacity="0.9"/>
    <path d="M30 40 L32 39 L34 40 L34 44 Q32 46 30 44 Z" fill="#1a1a1a"/>
    <path d="M20 30 Q14 34 16 40" stroke="#C9A84C" strokeWidth="2" strokeLinecap="round" fill="none"/>
    <path d="M44 30 Q50 34 48 40" stroke="#C9A84C" strokeWidth="2" strokeLinecap="round" fill="none"/>
  </svg>
);

const STEPS = [
  {
    target: '[data-testid="admin-tabs-nav"]',
    title: 'Bienvenue !',
    message: 'Je suis Straté, votre assistant. Voici votre tableau de bord avec tous les onglets de gestion. Laissez-moi vous montrer l\'essentiel !',
  },
  {
    target: '[data-testid="tab-strategiia"]',
    title: 'StratégiIA',
    message: 'Consultez toutes les analyses IA de vos clients ici. Les analyses premium en attente nécessitent votre validation avant envoi au client.',
  },
  {
    target: '[data-testid="tab-dossier-express"]',
    title: 'Dossier Express',
    message: 'Traitez les dossiers payants sous 2h : consultez les documents soumis, ajoutez votre expertise, puis générez et livrez le PDF final.',
  },
  {
    target: '[data-testid="tab-config"]',
    title: 'Configuration',
    message: 'Modifiez compteurs, tarifs, badges promo et les 4 chiffres clés de la page d\'accueil. Tout est dynamique et se met à jour instantanément.',
  },
  {
    target: '[data-testid="admin-test-toggle"]',
    title: 'Mode Test',
    message: 'Basculez entre Admin et Client pour voir votre site comme un visiteur. Le bouton juste à côté active le mode sombre.',
  },
  {
    target: '[data-testid="admin-help-btn"]',
    title: 'Aide & Guide',
    message: 'Ctrl+H ou ce bouton ouvre le guide complet (15 sections documentées). Vous pouvez relancer ce tutoriel depuis le guide. Bonne gestion !',
  },
];

export const AdminOnboardingTour = ({ isActive, onClose, token }) => {
  const [step, setStep] = useState(0);
  const [rect, setRect] = useState(null);
  const [bubbleAbove, setBubbleAbove] = useState(false);

  const current = STEPS[step];

  const updatePosition = useCallback(() => {
    if (!isActive) return;
    const el = document.querySelector(current.target);
    if (el) {
      const r = el.getBoundingClientRect();
      setRect({ top: r.top - 6, left: r.left - 6, width: r.width + 12, height: r.height + 12 });
      setBubbleAbove(r.bottom > window.innerHeight * 0.6);
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      setRect(null);
    }
  }, [step, isActive, current.target]);

  useEffect(() => {
    if (!isActive) { setStep(0); return; }
    trackEvent('start', 0, token);
    const timer = setTimeout(updatePosition, 250);
    return () => clearTimeout(timer);
  }, [isActive, updatePosition]);

  // Track step views + reposition on step change
  useEffect(() => {
    if (!isActive) return;
    trackEvent('step', step, token);
    const timer = setTimeout(updatePosition, 250);
    return () => clearTimeout(timer);
  }, [step, token]);

  useEffect(() => {
    if (!isActive) return;
    window.addEventListener('resize', updatePosition);
    return () => window.removeEventListener('resize', updatePosition);
  }, [isActive, updatePosition]);

  // ESC to skip
  useEffect(() => {
    if (!isActive) return;
    const handler = (e) => { if (e.key === 'Escape') complete(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isActive]);

  const complete = () => {
    trackEvent('complete', step, token);
    localStorage.setItem(TOUR_KEY, 'true');
    setStep(0);
    onClose();
  };

  const next = () => (step < STEPS.length - 1 ? setStep(s => s + 1) : complete());
  const prev = () => step > 0 && setStep(s => s - 1);

  if (!isActive) return null;

  // Bubble position
  const bubbleStyle = {};
  if (rect) {
    const gap = 16;
    if (bubbleAbove) {
      bubbleStyle.bottom = `${window.innerHeight - rect.top + gap}px`;
    } else {
      bubbleStyle.top = `${rect.top + rect.height + gap}px`;
    }
    let left = rect.left;
    if (left + 370 > window.innerWidth - 16) left = window.innerWidth - 386;
    if (left < 16) left = 16;
    bubbleStyle.left = `${left}px`;
  } else {
    bubbleStyle.top = '50%';
    bubbleStyle.left = '50%';
    bubbleStyle.transform = 'translate(-50%, -50%)';
  }

  return (
    <>
      {/* Spotlight cutout */}
      {rect ? (
        <div
          className="fixed rounded-lg"
          style={{
            top: rect.top, left: rect.left, width: rect.width, height: rect.height,
            boxShadow: '0 0 0 9999px rgba(0,0,0,0.78)',
            border: '2px solid rgba(201,168,76,0.5)',
            zIndex: 9998, pointerEvents: 'none',
            transition: 'all 0.4s ease-out',
          }}
          data-testid="tour-spotlight"
        />
      ) : (
        <div className="fixed inset-0 bg-black/78" style={{ zIndex: 9998 }} />
      )}

      {/* Click blocker */}
      <div className="fixed inset-0" style={{ zIndex: 9997 }} />

      {/* Straté speech bubble */}
      <div
        className="fixed w-[340px] sm:w-[370px]"
        style={{ ...bubbleStyle, zIndex: 9999 }}
        data-testid="tour-bubble"
        key={step}
      >
        <div
          className="bg-[#1a1a1a] border-2 border-[#C9A84C]/70 rounded-xl p-4 shadow-2xl relative"
          style={{ animation: 'tourFadeIn .3s ease-out' }}
        >
          {/* Arrow pointing to target */}
          {rect && (
            <div
              className="absolute w-3 h-3 bg-[#1a1a1a] rotate-45"
              style={bubbleAbove
                ? { bottom: -7, left: 36, borderBottom: '2px solid rgba(201,168,76,0.7)', borderRight: '2px solid rgba(201,168,76,0.7)' }
                : { top: -7, left: 36, borderTop: '2px solid rgba(201,168,76,0.7)', borderLeft: '2px solid rgba(201,168,76,0.7)' }
              }
            />
          )}

          {/* Content */}
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-0.5">
              <div
                className="w-11 h-11 rounded-full flex items-center justify-center border border-[#C9A84C]/40"
                style={{ background: '#252525' }}
              >
                <StrateTourSVG size={28} />
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[#C9A84C] text-[11px] font-bold uppercase tracking-widest mb-1">
                {current.title}
              </p>
              <p className="text-white/85 text-[13px] leading-relaxed">
                {current.message}
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-white/10">
            <div className="flex items-center gap-1.5">
              {STEPS.map((_, i) => (
                <div
                  key={i}
                  className={`h-1.5 rounded-full transition-all duration-300 ${i === step ? 'w-5 bg-[#C9A84C]' : 'w-1.5 bg-white/20'}`}
                />
              ))}
            </div>
            <div className="flex items-center gap-2">
              {step === 0 ? (
                <button
                  onClick={complete}
                  className="text-white/40 hover:text-white/60 text-[11px] transition-colors"
                  data-testid="tour-skip"
                >
                  Passer
                </button>
              ) : (
                <button
                  onClick={prev}
                  className="text-white/50 hover:text-white text-[11px] flex items-center gap-0.5 transition-colors"
                  data-testid="tour-prev"
                >
                  <ChevronLeft className="w-3 h-3" /> Retour
                </button>
              )}
              <button
                onClick={next}
                className="bg-[#C9A84C] text-[#1a1a1a] px-3.5 py-1.5 rounded-full text-[11px] font-bold flex items-center gap-1 hover:bg-[#d4b45c] transition-colors"
                data-testid="tour-next"
              >
                {step === STEPS.length - 1 ? 'Terminer' : 'Suivant'}
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes tourFadeIn {
          from { opacity: 0; transform: translateY(6px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </>
  );
};

export { TOUR_KEY };
