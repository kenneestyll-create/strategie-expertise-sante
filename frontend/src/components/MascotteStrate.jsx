import { useState, useEffect, useCallback } from 'react';
import { Volume2, ArrowRight, X } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const FALLBACK = {
  id: '', text: "Vous disposez en general de 2 ans pour declarer une maladie professionnelle.", category: "droits", link: "/ressources", link_label: "En savoir plus",
};

const MOIS = ['jan.', 'fev.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'aout', 'sept.', 'oct.', 'nov.', 'dec.'];

function getDateLabel() {
  const d = new Date();
  return `${d.getDate()} ${MOIS[d.getMonth()]}`;
}

/* ── SVG MASCOTTE ── */
const StrateSVG = ({ size = 52 }) => (
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

/* ── TTS FR ── */
function speakFrench(text, onStart, onEnd, onError) {
  if (typeof speechSynthesis === 'undefined') return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = 'fr-FR'; u.rate = 0.9; u.pitch = 1;
  u.onstart = onStart; u.onend = onEnd; u.onerror = onError;
  const go = () => {
    const v = speechSynthesis.getVoices();
    const fr = v.find(x => x.lang === 'fr-FR') || v.find(x => x.lang.startsWith('fr'));
    if (fr) u.voice = fr;
    speechSynthesis.speak(u);
  };
  speechSynthesis.getVoices().length > 0 ? go() : (speechSynthesis.onvoiceschanged = () => { go(); speechSynthesis.onvoiceschanged = null; });
}

/* ── Tracking ── */
function trackView(id) {
  if (!id) return;
  const key = `strate_view_${id}_${new Date().toDateString()}`;
  if (localStorage.getItem(key)) return;
  fetch(`${API}/conseils/view`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ conseil_id: id }) }).catch(() => {});
  localStorage.setItem(key, 'true');
}
function trackClick(id) {
  if (!id) return;
  fetch(`${API}/conseils/click`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ conseil_id: id }) }).catch(() => {});
}
export function trackStrateConversion(action) {
  const id = sessionStorage.getItem('strate_conseil_id');
  if (!id) return;
  fetch(`${API}/conseils/conversion`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ conseil_id: id, action }) }).catch(() => {});
}

/* ── COMPOSANT ── */
export const MascotteStrate = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [conseil, setConseil] = useState(null);
  const location = useLocation();
  const isAdmin = location.pathname.startsWith('/admin');

  useEffect(() => {
    if (isAdmin) return;
    fetch(`${API}/conseils/today`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(data => {
        setConseil({ id: data.id, text: data.text, cat: data.category, link: data.link || '/ressources', label: data.link_label || 'En savoir plus' });
        sessionStorage.setItem('strate_conseil_id', data.id);
        trackView(data.id);
      })
      .catch(() => setConseil({ id: FALLBACK.id, text: FALLBACK.text, cat: FALLBACK.category, link: FALLBACK.link, label: FALLBACK.link_label }));
  }, [isAdmin]);

  const speak = useCallback(() => {
    if (!conseil) return;
    speakFrench(conseil.text, () => setIsSpeaking(true), () => setIsSpeaking(false), () => setIsSpeaking(false));
  }, [conseil]);

  const close = useCallback(() => { speechSynthesis?.cancel(); setIsSpeaking(false); setIsOpen(false); }, []);

  if (!conseil || isAdmin) return null;

  return (
    <div className="fixed z-40" style={{ bottom: '7.5rem', right: '1.5rem' }} data-testid="mascotte-strate">

      {/* ── Fenetre compacte conseil ── */}
      {isOpen && (
        <div
          className="absolute bottom-16 right-0 mb-2 w-64 rounded-xl shadow-2xl border border-[#C9A84C]/25 overflow-hidden"
          style={{ background: '#141414', animation: 'strateIn .25s ease-out' }}
          data-testid="strate-bubble"
        >
          {/* Header compact */}
          <div className="flex items-center justify-between px-3 py-2 border-b border-[#C9A84C]/15">
            <span className="text-[#C9A84C] text-[10px] font-semibold tracking-widest uppercase">Conseil du {getDateLabel()}</span>
            <button onClick={close} className="text-white/30 hover:text-white/60 transition-colors" data-testid="strate-close" aria-label="Fermer">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Conseil */}
          <div className="px-3 py-2.5">
            <p className="text-white/85 text-[13px] leading-relaxed" data-testid="strate-conseil-text">{conseil.text}</p>
          </div>

          {/* Actions */}
          <div className="px-3 pb-2.5 flex items-center gap-1.5">
            <button
              onClick={speak}
              disabled={isSpeaking}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium transition-all ${
                isSpeaking ? 'bg-[#C9A84C]/25 text-[#C9A84C] animate-pulse' : 'bg-white/5 text-white/50 hover:bg-white/10 hover:text-white/70'
              }`}
              data-testid="strate-speak-btn"
            >
              <Volume2 className="w-3 h-3" />
              {isSpeaking ? 'Lecture...' : 'Ecouter'}
            </button>
            <Link
              to={conseil.link}
              onClick={() => { trackClick(conseil.id); close(); }}
              className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium bg-[#C9A84C] text-black hover:bg-[#C9A84C]/85 transition-all"
              data-testid="strate-action-btn"
            >
              {conseil.label} <ArrowRight className="w-2.5 h-2.5" />
            </Link>
          </div>
        </div>
      )}

      {/* ── Mascotte + bulle pulsante ── */}
      <div className="flex items-end gap-2">

        {/* Bulle "Conseil du jour" pulsante */}
        {!isOpen && (
          <button
            onClick={() => setIsOpen(true)}
            className="mb-1 px-3 py-1.5 rounded-full text-[11px] font-medium text-[#C9A84C] border border-[#C9A84C]/30 hover:border-[#C9A84C]/50 transition-all cursor-pointer"
            style={{ background: 'rgba(201,168,76,0.08)', animation: 'stratePulse 2.5s ease-in-out infinite' }}
            data-testid="strate-hint-bubble"
          >
            Conseil du jour
          </button>
        )}

        {/* Mascotte bouton */}
        <button
          onClick={() => setIsOpen(o => !o)}
          className="group relative w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-all hover:scale-105 active:scale-95 border border-[#C9A84C]/30 hover:border-[#C9A84C]/60"
          style={{ background: '#1a1a1a' }}
          data-testid="strate-mascot-btn"
          aria-label="Strate - Conseil du jour"
        >
          <StrateSVG size={32} />

          {/* Badge date rouge */}
          {!isOpen && (
            <span className="absolute -top-2.5 -left-1 px-1.5 py-0.5 rounded-full text-[8px] font-bold text-white whitespace-nowrap" style={{ background: '#c0392b' }} data-testid="strate-date-badge">
              {getDateLabel()}
            </span>
          )}
        </button>
      </div>

      <style>{`
        @keyframes stratePulse {
          0%, 100% { opacity: .75; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.03); }
        }
        @keyframes strateIn {
          from { opacity: 0; transform: translateY(8px) scale(.97); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
      `}</style>
    </div>
  );
};
