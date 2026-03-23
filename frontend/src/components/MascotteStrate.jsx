import { useState, useEffect, useCallback, useRef } from 'react';
import { Volume2, RefreshCw, ArrowRight, X, Info } from 'lucide-react';
import { Link } from 'react-router-dom';

/* ── 30 CONSEILS VALIDÉS ── */
const CONSEILS = [
  { text: "Vous disposez en general de 2 ans pour declarer une maladie professionnelle apres le diagnostic.", cat: "droits", link: "/ressources", label: "Voir les ressources" },
  { text: "Une contestation d'une decision de la CPAM doit etre faite dans un delai de 2 mois.", cat: "droits", link: "/ressources", label: "En savoir plus" },
  { text: "Un accident du travail doit etre declare dans les 24 heures par l'employeur.", cat: "droits", link: "/accident-travail-maladie-professionnelle", label: "Accidents du travail" },
  { text: "Vous pouvez declarer vous-meme un accident si l'employeur ne le fait pas.", cat: "droits", link: "/ressources", label: "Voir les demarches" },
  { text: "Une rechute peut etre reconnue meme plusieurs annees apres consolidation.", cat: "droits", link: "/simulateur", label: "Analyser votre cas" },
  { text: "Vous pouvez etre assiste par un medecin lors d'une expertise.", cat: "expertise", link: "/ressources", label: "Preparer une expertise" },
  { text: "Preparer ses documents medicaux est essentiel avant toute expertise.", cat: "expertise", link: "/dossier-express", label: "Dossier Express IA" },
  { text: "Vous avez le droit de contester une expertise medicale.", cat: "expertise", link: "/ressources", label: "Vos droits" },
  { text: "Le medecin expert doit rester independant.", cat: "expertise", link: "/ressources", label: "En savoir plus" },
  { text: "Un rapport medical incomplet peut etre conteste.", cat: "expertise", link: "/simulateur", label: "Analyser votre dossier" },
  { text: "Une incapacite permanente donne droit a une indemnisation.", cat: "indemnisation", link: "/calculatrice-ipp", label: "Calculer votre IPP" },
  { text: "Le taux d'IPP influence directement le montant de l'indemnisation.", cat: "indemnisation", link: "/calculatrice-ipp", label: "Calculatrice IPP" },
  { text: "Une faute inexcusable de l'employeur peut majorer votre indemnisation.", cat: "indemnisation", link: "/simulateur", label: "Analyser avec StrategiIA" },
  { text: "Certains prejudices ne sont pas automatiquement indemnises.", cat: "indemnisation", link: "/ressources", label: "Voir les ressources" },
  { text: "Une perte de carriere peut etre reconnue sous conditions.", cat: "indemnisation", link: "/ressources", label: "IP et PGPF" },
  { text: "Une inaptitude peut ouvrir droit a des indemnites specifiques.", cat: "emploi", link: "/ressources", label: "Vos droits" },
  { text: "Le reclassement professionnel est une obligation de l'employeur.", cat: "emploi", link: "/accident-travail-maladie-professionnelle", label: "En savoir plus" },
  { text: "Une invalidite ne met pas fin automatiquement au contrat de travail.", cat: "emploi", link: "/ressources", label: "Voir les ressources" },
  { text: "Vous pouvez cumuler certaines aides selon votre situation.", cat: "emploi", link: "/ressources", label: "Aides disponibles" },
  { text: "Une reconversion peut etre financee dans certains cas.", cat: "emploi", link: "/ressources", label: "En savoir plus" },
  { text: "Conservez toujours une copie de vos documents medicaux.", cat: "demarches", link: "/dossier-express", label: "Dossier Express IA" },
  { text: "Les echanges avec la CPAM doivent etre traces.", cat: "demarches", link: "/ressources", label: "Voir les guides" },
  { text: "Un dossier incomplet peut ralentir votre indemnisation.", cat: "demarches", link: "/dossier-express", label: "Completez votre dossier" },
  { text: "Il est possible de se faire accompagner dans ses demarches.", cat: "demarches", link: "/contact", label: "Nous contacter" },
  { text: "Une demande peut etre reetudiee avec de nouveaux elements.", cat: "demarches", link: "/simulateur", label: "Analyser votre situation" },
  { text: "Anticiper une expertise ameliore souvent son resultat.", cat: "strategie", link: "/dossier-express", label: "Dossier Express IA" },
  { text: "Une bonne preparation peut influencer une decision.", cat: "strategie", link: "/simulateur", label: "StrategiIA" },
  { text: "Chaque situation est unique et merite une analyse personnalisee.", cat: "strategie", link: "/simulateur", label: "Analyser mon cas" },
  { text: "Ne pas agir dans les delais peut faire perdre des droits.", cat: "strategie", link: "/ressources", label: "Delais importants" },
  { text: "Se faire accompagner permet souvent d'optimiser ses demarches.", cat: "strategie", link: "/contact", label: "Prendre contact" },
];

function getConseilDuJour() {
  const today = new Date();
  const index = Math.floor(today.getTime() / (1000 * 60 * 60 * 24)) % CONSEILS.length;
  return CONSEILS[index];
}

/* ── SVG MASCOTTE ── */
const StrateSVG = ({ size = 52 }) => (
  <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    {/* Body - trombone/clip shape */}
    <rect x="20" y="8" width="24" height="48" rx="12" fill="#1a1a1a" stroke="#C9A84C" strokeWidth="2.5"/>
    <rect x="24" y="12" width="16" height="20" rx="8" fill="#2a2a2a" stroke="#C9A84C" strokeWidth="1.5"/>
    {/* Eyes */}
    <circle cx="28" cy="22" r="2.5" fill="#C9A84C"/>
    <circle cx="36" cy="22" r="2.5" fill="#C9A84C"/>
    <circle cx="28.8" cy="21.5" r="1" fill="#fff"/>
    <circle cx="36.8" cy="21.5" r="1" fill="#fff"/>
    {/* Smile */}
    <path d="M28 27 Q32 31 36 27" stroke="#C9A84C" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
    {/* Shield on body */}
    <path d="M26 38 L32 35 L38 38 L38 46 Q32 50 26 46 Z" fill="#C9A84C" fillOpacity="0.9"/>
    <path d="M30 40 L32 39 L34 40 L34 44 Q32 46 30 44 Z" fill="#1a1a1a"/>
    {/* Arms */}
    <path d="M20 30 Q14 34 16 40" stroke="#C9A84C" strokeWidth="2" strokeLinecap="round" fill="none"/>
    <path d="M44 30 Q50 34 48 40" stroke="#C9A84C" strokeWidth="2" strokeLinecap="round" fill="none"/>
  </svg>
);

/* ── COMPOSANT PRINCIPAL ── */
export const MascotteStrate = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [hasSpoken, setHasSpoken] = useState(false);
  const conseil = getConseilDuJour();
  const synthRef = useRef(null);

  /* Auto-show bubble after 3 seconds on first visit */
  useEffect(() => {
    const seen = sessionStorage.getItem('strate_seen');
    if (!seen) {
      const t = setTimeout(() => { setIsOpen(true); sessionStorage.setItem('strate_seen', '1'); }, 3000);
      return () => clearTimeout(t);
    }
  }, []);

  const speak = useCallback(() => {
    if (typeof speechSynthesis === 'undefined') return;
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(conseil.text);
    utterance.lang = 'fr-FR';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => { setIsSpeaking(false); setHasSpoken(true); };
    utterance.onerror = () => setIsSpeaking(false);
    // Try to find a French voice
    const voices = speechSynthesis.getVoices();
    const frVoice = voices.find(v => v.lang.startsWith('fr') && v.name.toLowerCase().includes('female'))
      || voices.find(v => v.lang.startsWith('fr'))
      || voices[0];
    if (frVoice) utterance.voice = frVoice;
    synthRef.current = utterance;
    speechSynthesis.speak(utterance);
  }, [conseil.text]);

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

  return (
    <div className="fixed z-40" style={{ bottom: '7.5rem', right: '1.5rem' }} data-testid="mascotte-strate">

      {/* ── Bulle de conseil ── */}
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
              onClick={close}
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

      {/* ── Mascotte (bouton flottant) ── */}
      <button
        onClick={handleMascotClick}
        className="group relative w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all hover:scale-110 active:scale-95 border-2 border-[#C9A84C]/40 hover:border-[#C9A84C]/70"
        style={{ background: 'linear-gradient(145deg, #1a1a1a 0%, #222 100%)' }}
        data-testid="strate-mascot-btn"
        aria-label="Strate - Conseil du jour"
      >
        <StrateSVG size={38} />
        {/* Pulse indicator when bubble is closed */}
        {!isOpen && (
          <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#C9A84C] flex items-center justify-center animate-bounce">
            <span className="text-[8px] font-bold text-black">!</span>
          </span>
        )}
      </button>
    </div>
  );
};
