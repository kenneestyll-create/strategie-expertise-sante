import { useState, useEffect, useCallback } from 'react';
import { Volume2, ArrowRight, X } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const FALLBACK = {
  id: '', text: "Vous disposez en général de 2 ans pour déclarer une maladie professionnelle.", category: "droits", link: "/ressources", link_label: "En savoir plus",
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

/* ── TTS FR — Robuste Mobile Android + Desktop ── */

// Pré-chargement des voix (Promise + polling fallback)
let _voicesLoaded = null;
function loadVoices() {
  if (_voicesLoaded) return _voicesLoaded;
  _voicesLoaded = new Promise((resolve) => {
    let voices = speechSynthesis.getVoices();
    if (voices.length) { resolve(voices); return; }

    let resolved = false;
    const done = (v) => { if (!resolved) { resolved = true; resolve(v); } };

    speechSynthesis.onvoiceschanged = () => {
      done(speechSynthesis.getVoices());
    };

    // Polling fallback — certains navigateurs mobiles ne déclenchent jamais onvoiceschanged
    let attempts = 0;
    const interval = setInterval(() => {
      voices = speechSynthesis.getVoices();
      attempts++;
      if (voices.length || attempts > 30) {
        clearInterval(interval);
        done(voices);
      }
    }, 100);
  });
  return _voicesLoaded;
}

// Initialiser les voix au plus tôt (pas besoin d'attendre un clic)
if (typeof speechSynthesis !== 'undefined') {
  loadVoices();
}

// Fix mobile : le navigateur peut suspendre speechSynthesis sans interaction
if (typeof document !== 'undefined') {
  document.addEventListener('click', () => {
    if (typeof speechSynthesis !== 'undefined') speechSynthesis.resume();
  }, { once: false, passive: true });
}

async function speakFrench(text, onStart, onEnd, onError) {
  if (typeof speechSynthesis === 'undefined') { onError?.(); return; }

  const voices = await loadVoices();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'fr-FR';
  utterance.rate = 1;
  utterance.pitch = 1;
  utterance.onstart = onStart;
  utterance.onend = onEnd;
  utterance.onerror = onError;

  // Recherche robuste FR
  const frenchVoice =
    voices.find(v => v.lang === 'fr-FR') ||
    voices.find(v => v.lang === 'fr_FR') ||
    voices.find(v => v.lang?.startsWith('fr')) ||
    voices.find(v => v.name?.toLowerCase().includes('french')) ||
    voices.find(v => v.name?.toLowerCase().includes('français'));

  if (frenchVoice) {
    utterance.voice = frenchVoice;
  }

  // IMPORTANT : reset queue (fix bug mobile où la queue est bloquée)
  speechSynthesis.cancel();

  speechSynthesis.speak(utterance);
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

/* ═══════════════════════════════════════════
   WIDGET DESKTOP — Flottant en bas à droite
   ═══════════════════════════════════════════ */
const DesktopWidget = ({ conseil, isOpen, setIsOpen, isSpeaking, speak, close }) => (
  <div className="hidden md:block fixed" style={{ bottom: '7.5rem', right: '1.5rem', zIndex: 40 }} data-testid="mascotte-strate-desktop">
    {/* Fenêtre conseil */}
    {isOpen && (
      <div
        className="absolute bottom-16 right-0 mb-2 w-64 rounded-xl shadow-2xl border border-border overflow-hidden bg-background"
        style={{ animation: 'strateIn .25s ease-out' }}
        data-testid="strate-bubble"
      >
        <div className="flex items-center justify-between px-3 py-2 border-b border-border">
          <span className="text-[#C9A84C] text-[10px] font-semibold tracking-widest uppercase">Conseil du {getDateLabel()}</span>
          <button onClick={close} className="text-muted-foreground hover:text-foreground transition-colors" data-testid="strate-close" aria-label="Fermer">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="px-3 py-2.5">
          <p className="text-foreground text-[13px] leading-relaxed font-medium" data-testid="strate-conseil-text">{conseil.text}</p>
        </div>
        <div className="px-3 pb-2.5 flex items-center gap-1.5">
          <button
            onClick={speak}
            disabled={isSpeaking}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium transition-all ${isSpeaking ? 'bg-accent/20 text-accent animate-pulse' : 'bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground'}`}
            data-testid="strate-speak-btn"
          >
            <Volume2 className="w-3 h-3" />
            {isSpeaking ? 'Lecture...' : 'Écouter'}
          </button>
          <Link
            to={conseil.link}
            onClick={() => { trackClick(conseil.id); close(); }}
            className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium bg-foreground text-primary-foreground hover:bg-foreground/90 transition-all"
            data-testid="strate-action-btn"
          >
            {conseil.label} <ArrowRight className="w-2.5 h-2.5" />
          </Link>
        </div>
      </div>
    )}

    {/* Mascotte + bulle pulsante */}
    <div className="flex items-end gap-2">
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="mb-1 px-3 py-1.5 rounded-full text-[11px] font-semibold border border-foreground/20 hover:border-foreground/40 transition-all cursor-pointer bg-background shadow-sm"
          style={{ color: '#000000', animation: 'stratePulse 2.5s ease-in-out infinite' }}
          data-testid="strate-hint-bubble"
        >
          Conseil du jour
        </button>
      )}
      <button
        onClick={() => setIsOpen(o => !o)}
        className="group relative w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-all hover:scale-105 active:scale-95 border border-[#C9A84C]/30 hover:border-[#C9A84C]/60"
        style={{ background: '#1a1a1a' }}
        data-testid="strate-mascot-btn"
        aria-label="Straté - Conseil du jour"
      >
        <StrateSVG size={32} />
        {!isOpen && (
          <span className="absolute -top-2.5 -left-1 px-1.5 py-0.5 rounded-full text-[8px] font-bold text-white whitespace-nowrap" style={{ background: '#c0392b' }} data-testid="strate-date-badge">
            {getDateLabel()}
          </span>
        )}
      </button>
    </div>
  </div>
);

/* ═══════════════════════════════════════════
   WIDGET MOBILE — Intégré dans le flux
   ═══════════════════════════════════════════ */
const MobileWidget = ({ conseil, isSpeaking, speak }) => (
  <div className="md:hidden" data-testid="mascotte-strate-mobile">
    <div className="flex items-start gap-3 bg-card border border-border rounded-xl p-3.5 shadow-sm">
      {/* Avatar mascotte */}
      <div className="w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center border border-[#C9A84C]/30" style={{ background: '#1a1a1a' }}>
        <StrateSVG size={26} />
      </div>

      {/* Contenu */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-[10px] font-semibold text-[#C9A84C] uppercase tracking-widest">Conseil du {getDateLabel()}</span>
        </div>
        <p className="text-foreground text-[13px] leading-relaxed font-medium mb-2.5" data-testid="strate-mobile-text">
          {conseil.text}
        </p>
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            onClick={speak}
            disabled={isSpeaking}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium transition-all ${isSpeaking ? 'bg-accent/20 text-accent animate-pulse' : 'bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground'}`}
            data-testid="strate-mobile-speak"
          >
            <Volume2 className="w-3 h-3" />
            {isSpeaking ? 'Lecture...' : 'Écouter'}
          </button>
          <Link
            to={conseil.link}
            onClick={() => trackClick(conseil.id)}
            className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium bg-foreground text-primary-foreground hover:bg-foreground/90 transition-all"
            data-testid="strate-mobile-action"
          >
            {conseil.label} <ArrowRight className="w-2.5 h-2.5" />
          </Link>
        </div>
      </div>
    </div>
  </div>
);

/* ═══════════════════════════════════════════
   COMPOSANT PRINCIPAL
   ═══════════════════════════════════════════ */
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
    <>
      <DesktopWidget conseil={conseil} isOpen={isOpen} setIsOpen={setIsOpen} isSpeaking={isSpeaking} speak={speak} close={close} />
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
    </>
  );
};

/* Export mobile widget séparément pour l'intégrer dans le flux de la page */
export const MascotteMobileWidget = () => {
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
      })
      .catch(() => setConseil({ id: FALLBACK.id, text: FALLBACK.text, cat: FALLBACK.category, link: FALLBACK.link, label: FALLBACK.link_label }));
  }, [isAdmin]);

  const speak = useCallback(() => {
    if (!conseil) return;
    speakFrench(conseil.text, () => setIsSpeaking(true), () => setIsSpeaking(false), () => setIsSpeaking(false));
  }, [conseil]);

  if (!conseil || isAdmin) return null;

  return <MobileWidget conseil={conseil} isSpeaking={isSpeaking} speak={speak} />;
};
