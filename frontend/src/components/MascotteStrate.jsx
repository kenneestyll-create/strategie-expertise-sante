import { useState, useEffect, useCallback, useRef } from 'react';
import { Volume2, ArrowRight, X, Info } from 'lucide-react';
import { Link } from 'react-router-dom';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/* ── Fallback conseil if API fails ── */
const FALLBACK = {
  text: "Vous disposez en general de 2 ans pour declarer une maladie professionnelle apres le diagnostic.",
  category: "droits",
  link: "/ressources",
  link_label: "Voir les ressources",
};

/* ── SVG MASCOTTE ── */
const StrateSVG = ({ size = 52 }) => (
  <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect x="20" y="8" width="24" height="48" rx="12" fill="#1a1a1a" stroke="#C9A84C" strokeWidth="2.5"/>
    <rect x="24" y="12" width="16" height="20" rx="8" fill="#2a2a2a" stroke="#C9A84C" strokeWidth="1.5"/>
    <circle cx="28" cy="22" r="2.5" fill="#C9A84C"/>
    <circle cx="36" cy="22" r="2.5" fill="#C9A84C"/>
    <circle cx="28.8" cy="21.5" r="1" fill="#fff"/>
    <circle cx="36.8" cy="21.5" r="1" fill="#fff"/>
    <path d="M28 27 Q32 31 36 27" stroke="#C9A84C" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
    <path d="M26 38 L32 35 L38 38 L38 46 Q32 50 26 46 Z" fill="#C9A84C" fillOpacity="0.9"/>
    <path d="M30 40 L32 39 L34 40 L34 44 Q32 46 30 44 Z" fill="#1a1a1a"/>
    <path d="M20 30 Q14 34 16 40" stroke="#C9A84C" strokeWidth="2" strokeLinecap="round" fill="none"/>
    <path d="M44 30 Q50 34 48 40" stroke="#C9A84C" strokeWidth="2" strokeLinecap="round" fill="none"/>
  </svg>
);

/* ── TTS FR-FR — Fonction robuste ── */
function speakFrench(text, onStart, onEnd, onError) {
  if (typeof speechSynthesis === 'undefined') return;
  speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'fr-FR';
  utterance.rate = 0.9;
  utterance.pitch = 1;
  utterance.onstart = onStart;
  utterance.onend = onEnd;
  utterance.onerror = onError;

  const trySpeak = () => {
    const voices = speechSynthesis.getVoices();
    const frVoice =
      voices.find(v => v.lang === 'fr-FR') ||
      voices.find(v => v.lang.startsWith('fr'));
    if (frVoice) utterance.voice = frVoice;
    speechSynthesis.speak(utterance);
  };

  const voices = speechSynthesis.getVoices();
  if (voices.length > 0) {
    trySpeak();
  } else {
    speechSynthesis.onvoiceschanged = () => {
      trySpeak();
      speechSynthesis.onvoiceschanged = null;
    };
    // Fallback timeout if onvoiceschanged never fires
    setTimeout(() => {
      if (speechSynthesis.speaking) return;
      trySpeak();
    }, 500);
  }
}

/* ── COMPOSANT PRINCIPAL ── */
export const MascotteStrate = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [hasSpoken, setHasSpoken] = useState(false);
  const [conseil, setConseil] = useState(null);

  /* Fetch conseil du jour from backend */
  useEffect(() => {
    fetch(`${API}/conseils/today`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(data => setConseil({
        text: data.text,
        cat: data.category,
        link: data.link || '/ressources',
        label: data.link_label || 'En savoir plus',
      }))
      .catch(() => setConseil({
        text: FALLBACK.text,
        cat: FALLBACK.category,
        link: FALLBACK.link,
        label: FALLBACK.link_label,
      }));
  }, []);

  /* Auto-show bubble after 3 seconds on first visit */
  useEffect(() => {
    const seen = sessionStorage.getItem('strate_seen');
    if (!seen) {
      const t = setTimeout(() => { setIsOpen(true); sessionStorage.setItem('strate_seen', '1'); }, 3000);
      return () => clearTimeout(t);
    }
  }, []);

  const speak = useCallback(() => {
    if (!conseil) return;
    speakFrench(
      conseil.text,
      () => setIsSpeaking(true),
      () => { setIsSpeaking(false); setHasSpoken(true); },
      () => setIsSpeaking(false)
    );
  }, [conseil]);

  const handleMascotClick = useCallback(() => {
    if (isOpen) {
      speak();
    } else {
      setIsOpen(true);
    }
  }, [isOpen, speak]);

  const close = useCallback(() => {
    speechSynthesis?.cancel();
    setIsSpeaking(false);
    setIsOpen(false);
  }, []);

  const trackClick = useCallback(() => {
    if (!conseil) return;
    fetch(`${API}/conseils/click`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: conseil.text }),
    }).catch(() => {});
    close();
  }, [conseil, close]);

  if (!conseil) return null;

  return (
    <div className="fixed z-40" style={{ bottom: '7.5rem', right: '1.5rem' }} data-testid="mascotte-strate">

      {/* Bulle de conseil */}
      {isOpen && (
        <div
          className="absolute bottom-full right-0 mb-3 w-72 sm:w-80 rounded-2xl shadow-2xl border border-[#C9A84C]/30 overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-300"
          style={{ background: 'linear-gradient(145deg, #1a1a1a 0%, #111 100%)' }}
          data-testid="strate-bubble"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-2.5 border-b border-[#C9A84C]/20">
            <div className="flex items-center gap-2">
              <StrateSVG size={24} />
              <span className="text-[#C9A84C] text-xs font-semibold tracking-wide">CONSEIL DU JOUR</span>
            </div>
            <button onClick={close} className="text-white/40 hover:text-white/70 transition-colors p-1" data-testid="strate-close" aria-label="Fermer">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Conseil */}
          <div className="px-4 py-3">
            <p className="text-white/90 text-sm leading-relaxed" data-testid="strate-conseil-text">
              {conseil.text}
            </p>
          </div>

          {/* Actions */}
          <div className="px-4 pb-3 flex items-center gap-2">
            <button
              onClick={speak}
              disabled={isSpeaking}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                isSpeaking
                  ? 'bg-[#C9A84C]/30 text-[#C9A84C] animate-pulse'
                  : 'bg-[#C9A84C]/15 text-[#C9A84C] hover:bg-[#C9A84C]/25'
              }`}
              data-testid="strate-speak-btn"
            >
              <Volume2 className="w-3.5 h-3.5" />
              {isSpeaking ? 'Lecture...' : (hasSpoken ? 'Reecouter' : 'Ecouter')}
            </button>
            <Link
              to={conseil.link}
              onClick={trackClick}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-[#C9A84C] text-black hover:bg-[#C9A84C]/90 transition-all"
              data-testid="strate-action-btn"
            >
              {conseil.label} <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {/* Disclaimer */}
          <div className="px-4 pb-3 flex items-start gap-1.5" data-testid="strate-disclaimer">
            <Info className="w-3 h-3 text-white/25 flex-shrink-0 mt-0.5" />
            <p className="text-[10px] text-white/25 leading-relaxed">
              Information indicative — ne remplace pas un conseil juridique personnalise.
            </p>
          </div>
        </div>
      )}

      {/* Mascotte (bouton flottant) */}
      <button
        onClick={handleMascotClick}
        className="group relative w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all hover:scale-110 active:scale-95 border-2 border-[#C9A84C]/40 hover:border-[#C9A84C]/70"
        style={{ background: 'linear-gradient(145deg, #1a1a1a 0%, #222 100%)' }}
        data-testid="strate-mascot-btn"
        aria-label="Strate - Conseil du jour"
      >
        <StrateSVG size={38} />
        {!isOpen && (
          <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#C9A84C] flex items-center justify-center animate-bounce">
            <span className="text-[8px] font-bold text-black">!</span>
          </span>
        )}
      </button>
    </div>
  );
};
