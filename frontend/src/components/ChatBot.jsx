import { useState, useRef, useEffect, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  MessageCircle, X, Send, Bot, User,
  ArrowRight, Gauge, Lock, FileText, Phone, Search, Sparkles, ShieldAlert, Headphones
} from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { useStrateTriggers, canAutoOpenOnPath } from '@/hooks/useStrateTriggers';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const CHAT_LIMIT = 3;

const WAITING_MESSAGES = [
  "Analyse de votre situation en cours",
  "Consultation de notre base juridique",
  "Préparation de votre réponse personnalisée",
];

const LoadingBubble = () => {
  const [msgIndex, setMsgIndex] = useState(0);
  const [progress, setProgress] = useState(0);  const [isLong, setIsLong] = useState(false);
  const startRef = useRef(Date.now());

  useEffect(() => {
    const msgTimer = setInterval(() => {
      setMsgIndex(prev => (prev + 1) % WAITING_MESSAGES.length);
    }, 3500);
    return () => clearInterval(msgTimer);
  }, []);

  useEffect(() => {
    const progTimer = setInterval(() => {
      const elapsed = Date.now() - startRef.current;
      const p = Math.min(92, (elapsed / 15000) * 92);
      setProgress(p);
      if (elapsed > 10000) setIsLong(true);
    }, 200);
    return () => clearInterval(progTimer);
  }, []);

  return (
    <div className="flex gap-3" data-testid="chatbot-loading">
      <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
        <Bot className="w-4 h-4 text-muted-foreground" />
      </div>
      <div className="max-w-[80%] bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3 space-y-2.5">
        <p className="text-sm text-foreground/80">
          Votre question est en cours d'analyse par notre IA
          <span className="inline-flex w-6 ml-0.5">
            <span className="animate-[blink_1.4s_infinite] [animation-delay:0ms]">.</span>
            <span className="animate-[blink_1.4s_infinite] [animation-delay:200ms]">.</span>
            <span className="animate-[blink_1.4s_infinite] [animation-delay:400ms]">.</span>
          </span>
        </p>
        <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-accent rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-xs text-muted-foreground italic transition-opacity duration-300" key={msgIndex}>
          {WAITING_MESSAGES[msgIndex]}...
        </p>
        {isLong && (
          <p className="text-xs text-accent font-medium" data-testid="chatbot-loading-long">
            Notre IA analyse votre cas en détail, merci de patienter encore quelques secondes...
          </p>
        )}
      </div>
    </div>
  );
};

/**
 * CtaLink — wraps a Link to support special pseudo-routes used by Straté:
 *  - "/strategiia" → does NOT navigate; dispatches the global window event
 *    "strategiia:open" so the StrategiIA popup opens in place. Falls back to
 *    /?open=strategiia query (preserves tracking) if the popup component isn't
 *    mounted on the current page.
 *  - any other href: standard react-router Link.
 */
const CtaLink = ({ href, src, track, onAfter, children }) => {
  const isStrategiia = typeof href === 'string' && (href === '/strategiia' || href.startsWith('/strategiia?') || href.startsWith('/strategiia#'));
  const handleClick = (e) => {
    track && track(href, src);
    if (isStrategiia) {
      e.preventDefault();
      try {
        window.dispatchEvent(new CustomEvent('strategiia:open', { detail: { src } }));
      } catch (_) { /* no-op */ }
      onAfter && onAfter();
      return;
    }
    onAfter && onAfter();
  };
  if (isStrategiia) {
    // Use a button so prevent-default works cleanly; styled as a link wrapper.
    return (
      <a href="#" onClick={handleClick} className="block" data-testid="strate-cta-strategiia">{children}</a>
    );
  }
  return (
    <Link to={href} onClick={handleClick}>{children}</Link>
  );
};

const StrateMascotIcon = ({ size = 40 }) => (  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="4" y="8" width="32" height="24" rx="6" fill="#0a0a08" stroke="#C9A84C" strokeWidth="1.5"/>
    <rect x="10" y="14" width="6" height="5" rx="1.5" fill="#C9A84C"/>
    <rect x="24" y="14" width="6" height="5" rx="1.5" fill="#C9A84C"/>
    <rect x="16" y="24" width="8" height="2" rx="1" fill="#C9A84C" opacity="0.6"/>
    <rect x="15" y="2" width="10" height="4" rx="2" fill="#C9A84C" opacity="0.4"/>
    <line x1="20" y1="6" x2="20" y2="8" stroke="#C9A84C" strokeWidth="1.5" opacity="0.4"/>
  </svg>
);

export const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showBubble, setShowBubble] = useState(false);
  const [bubbleDismissed, setBubbleDismissed] = useState(true);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Bonjour ! Je suis l'assistant d'orientation de S.E.S.\n\nDites-moi en quelques mots votre besoin et je vous oriente vers le bon outil."
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const location = useLocation();
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 640;
  const isHomePage = location.pathname === '/';
  const [sessionId, setSessionId] = useState(null);
  const [questionsUsed, setQuestionsUsed] = useState(0);
  const [quotaExceeded, setQuotaExceeded] = useState(false);
  const messagesEndRef = useRef(null);
  const pendingQuestionRef = useRef(null);

  // --- STRATÉ mode state (Conciergerie IA) ---
  const [strateEnabled, setStrateEnabled] = useState(true);
  const [strateSessionId, setStrateSessionId] = useState(null);
  const [strateStep, setStrateStep] = useState(null); // null until greeting loaded
  const [strateMessage, setStrateMessage] = useState('');
  const [strateOptions, setStrateOptions] = useState([]);
  const [strateCtas, setStrateCtas] = useState(null); // { primary, alternative }
  const [strateFreeText, setStrateFreeText] = useState('');
  const [strateLoading, setStrateLoading] = useState(false);
  const [showFallbackChat, setShowFallbackChat] = useState(false);

  // Load Straté kill switch config once
  useEffect(() => {
    let cancelled = false;
    axios.get(`${API}/strate/config`).then((r) => {
      if (!cancelled) setStrateEnabled(!!r.data?.enabled);
    }).catch(() => { /* default stays true */ });
    return () => { cancelled = true; };
  }, []);

  // Auto-open via scroll/inactivity triggers
  useStrateTriggers({
    enabled: strateEnabled,
    isOpen,
    onTrigger: () => setIsOpen(true),
  });

  // When chat opens and Straté is enabled → fetch greeting once per session
  useEffect(() => {
    if (!isOpen || !strateEnabled || strateStep !== null || showFallbackChat) return;
    const fetchGreeting = async () => {
      setStrateLoading(true);
      try {
        const r = await axios.post(`${API}/strate/chat`, {
          step: 'greeting',
          page: location.pathname,
        });
        setStrateSessionId(r.data.session_id);
        setStrateStep('greeting');
        setStrateMessage(r.data.message);
        setStrateOptions(r.data.options || []);
        setStrateCtas(null);
      } catch (e) {
        setShowFallbackChat(true);
      } finally {
        setStrateLoading(false);
      }
    };
    fetchGreeting();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, strateEnabled, strateStep, showFallbackChat]);

  const strateAct = async (payload) => {
    setStrateLoading(true);
    try {
      const r = await axios.post(`${API}/strate/chat`, {
        session_id: strateSessionId,
        page: location.pathname,
        ...payload,
      });
      setStrateSessionId(r.data.session_id);
      setStrateStep(r.data.step);
      setStrateMessage(r.data.message || '');
      setStrateOptions(r.data.options || []);
      if (r.data.primary_cta || r.data.alternative_cta) {
        setStrateCtas({ primary: r.data.primary_cta, alternative: r.data.alternative_cta });
      } else {
        setStrateCtas(null);
      }
    } catch (e) {
      setShowFallbackChat(true);
    } finally {
      setStrateLoading(false);
    }
  };

  const strateTrackClick = (href, src) => {
    if (strateSessionId) {
      axios.post(`${API}/strate/chat`, {
        session_id: strateSessionId,
        step: 'route_click',
        page: location.pathname,
        text: href,
        category_id: src,
      }).catch(() => { /* silent */ });
    }
  };

  const strateSelectRoot = (optId) => {
    strateAct({ step: 'qualify', category_id: optId });
  };
  const strateSelectQualification = (optId) => {
    strateAct({ step: 'route', qualification_id: optId });
  };
  const strateSubmitFreeText = () => {
    const t = strateFreeText.trim();
    if (t.length < 3) return;
    strateAct({ step: 'free_text', text: t });
    setStrateFreeText('');
  };
  const strateReset = () => {
    setStrateStep(null);
    setStrateMessage('');
    setStrateOptions([]);
    setStrateCtas(null);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => { scrollToBottom(); }, [messages, strateStep, strateMessage]);

  // Delayed appearance of the bubble — disabled
  useEffect(() => {}, [isOpen, bubbleDismissed]);

  // Listen for AI questions from GlobalSearch
  useEffect(() => {
    const handler = (e) => {
      const question = e.detail?.question;
      if (!question) return;
      pendingQuestionRef.current = question;
      setIsOpen(true);
    };
    window.addEventListener('strate-ask-ai', handler);
    return () => window.removeEventListener('strate-ask-ai', handler);
  }, []);

  // Listen for chatbot:open event (from Hero mobile trigger)
  useEffect(() => {
    const handler = () => setIsOpen(true);
    window.addEventListener('chatbot:open', handler);
    return () => window.removeEventListener('chatbot:open', handler);
  }, []);

  // Auto-send pending question when chatbot opens
  useEffect(() => {
    if (isOpen && pendingQuestionRef.current && !loading && !quotaExceeded) {
      const q = pendingQuestionRef.current;
      pendingQuestionRef.current = null;
      // Small delay so the chat window renders first
      setTimeout(() => handleSend(q), 300);
    }
  }, [isOpen]);

  const remaining = Math.max(0, CHAT_LIMIT - questionsUsed);

  const quickQuestions = [
    "Comment préparer une expertise ?",
    "Qu'est-ce que la MDPH ?",
    "Quels sont vos tarifs ?",
    "Mes droits après un AT"
  ];

  const handleSend = async (text = input) => {
    if (!text.trim() || quotaExceeded) return;

    const userMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chatbot`, {
        message: text,
        session_id: sessionId
      });

      setSessionId(response.data.session_id);
      const newUsed = questionsUsed + 1;
      setQuestionsUsed(newUsed);

      // Check if the response indicates quota exceeded
      if (newUsed >= CHAT_LIMIT) {
        setQuotaExceeded(true);
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response,
        is_faq: response.data.is_faq
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Désolé, une erreur s'est produite. Veuillez réessayer ou [nous contacter directement](/contact)."
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* ╔═══════════════════════════════════════════════════════════╗
         ║  ZONE GELÉE — CHATBOT MOBILE VALIDÉ LE 04/04/2026       ║
         ║                                                          ║
         ║  Position mobile VERROUILLÉE par ordre du responsable.   ║
         ║  INTERDICTION ABSOLUE de modifier sans ordre explicite.  ║
         ║  Aucun agent Emergent ne doit toucher ce positionnement. ║
         ║                                                          ║
         ║  Mobile : bouton intégré dans le Hero (HomePage.jsx)     ║
         ║  Desktop : fixed bottom-6 right-4 (inchangé)            ║
         ╚═══════════════════════════════════════════════════════════╝ */}
      {!isOpen && !isMobile && (
        <div className="fixed bottom-6 right-4" style={{ zIndex: 'var(--z-chatbot)' }} data-testid="chatbot-fab-wrapper">
          <button
            onClick={() => { setIsOpen(true); }}
            className="group relative w-11 h-11 rounded-xl bg-[#0a0a08] border-2 border-[#C9A84C]/40 shadow-lg shadow-[#C9A84C]/10 flex items-center justify-center transition-all duration-300 hover:border-[#C9A84C]/70 hover:shadow-[#C9A84C]/25 hover:scale-105"
            data-testid="chatbot-button"
            aria-label="Ouvrir l'assistant"
          >
            <StrateMascotIcon size={24} />
            {/* Online indicator */}
            <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-[#0a0a08]" />
          </button>
        </div>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div
          className="fixed inset-0 sm:inset-auto sm:bottom-6 sm:right-6 w-full sm:w-[380px] sm:max-w-[calc(100vw-2rem)] h-full sm:h-[550px] sm:max-h-[min(550px,calc(100vh-6rem))] flex flex-col bg-background sm:border sm:border-border sm:rounded-2xl shadow-2xl overflow-hidden"
          style={{ zIndex: 'var(--z-chatbot)', maxHeight: '100dvh' }}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 bg-foreground text-primary-foreground">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center font-bold text-accent-foreground text-base" aria-hidden="true">
                S
              </div>
              <div>
                <h3 className="font-semibold text-sm" data-testid="strate-header-name">Straté</h3>
                <p className="text-[10px] text-primary-foreground/70" data-testid="strate-header-role">
                  Conciergerie IA · répond instantanément
                </p>
                {strateEnabled && !showFallbackChat && (
                  <Link
                    to="/agenda?src=strate_human_header"
                    onClick={() => { strateTrackClick('/agenda?src=strate_human_header', 'strate_human_header'); setIsOpen(false); }}
                    className="inline-flex items-center gap-1 text-[10px] text-[#C9A84C] hover:underline mt-0.5"
                    data-testid="strate-expert-link-header"
                  >
                    <Headphones className="w-3 h-3" /> Besoin d'un humain ? Parler à un expert
                  </Link>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {/* Quota counter — only visible in fallback chat mode */}
              {showFallbackChat && (
              <Badge
                className={`text-[10px] ${remaining > 2 ? 'bg-green-500/20 text-green-300 border-green-500/30' : remaining > 0 ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' : 'bg-red-500/20 text-red-300 border-red-500/30'}`}
                data-testid="chatbot-quota-badge"
              >
                <Gauge className="w-3 h-3 mr-1" />
                {remaining}/{CHAT_LIMIT}
              </Badge>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-primary-foreground/10 rounded-lg transition-colors"
                aria-label="Fermer le chat"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* ---------- STRATÉ MODE (structured reception) ---------- */}
          {strateEnabled && !showFallbackChat && (
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/30" data-testid="strate-body">
              {/* RGPD banner — always visible at top */}
              <div className="flex items-start gap-2 text-[11px] text-amber-900 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2" data-testid="strate-rgpd-banner">
                <ShieldAlert className="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-amber-600" />
                <span>Assistant IA. Merci de ne pas saisir de données médicales sensibles ici.</span>
              </div>

              {/* Current message bubble */}
              {strateMessage && (
                <div className="flex gap-3" data-testid="strate-message">
                  <div className="w-8 h-8 rounded-full bg-accent text-accent-foreground flex items-center justify-center flex-shrink-0 font-bold text-xs">S</div>
                  <div className="max-w-[85%] bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3">
                    <div className="text-sm prose prose-sm max-w-none">
                      <ReactMarkdown>{strateMessage}</ReactMarkdown>
                    </div>
                  </div>
                </div>
              )}

              {/* Loading state */}
              {strateLoading && (
                <div className="flex gap-3" data-testid="strate-loading">
                  <div className="w-8 h-8 rounded-full bg-accent/50 flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-4 h-4 animate-pulse text-accent-foreground" />
                  </div>
                  <div className="bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3 text-xs text-muted-foreground italic">
                    Un instant…
                  </div>
                </div>
              )}

              {/* Option buttons (greeting / qualify / confirm / out_of_scope) */}
              {!strateLoading && strateOptions.length > 0 && (
                <div className="ml-11 space-y-2" data-testid="strate-options">
                  {strateOptions.map((opt) => (
                    <button
                      key={opt.id}
                      onClick={() => {
                        if (strateStep === 'greeting') strateSelectRoot(opt.id);
                        else if (strateStep === 'qualify' || strateStep === 'confirm' || strateStep === 'out_of_scope') strateSelectQualification(opt.id);
                      }}
                      className="w-full text-left px-3 py-2.5 rounded-lg text-sm bg-card border border-border hover:border-[#C9A84C] hover:bg-[#C9A84C]/5 transition-all"
                      data-testid={`strate-opt-${opt.id}`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              )}

              {/* Free text input (step free_text) */}
              {!strateLoading && strateStep === 'free_text' && (
                <div className="ml-11 space-y-2" data-testid="strate-freetext">
                  <div className="flex gap-2">
                    <Input
                      value={strateFreeText}
                      onChange={(e) => setStrateFreeText(e.target.value)}
                      onKeyPress={(e) => { if (e.key === 'Enter') { e.preventDefault(); strateSubmitFreeText(); } }}
                      placeholder="Ex. : J'ai reçu un refus AAH en septembre…"
                      className="flex-1 rounded-lg"
                      data-testid="strate-freetext-input"
                    />
                    <Button onClick={strateSubmitFreeText} size="icon" className="rounded-lg" disabled={strateFreeText.trim().length < 3} data-testid="strate-freetext-send">
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}

              {/* Sensitive data warning */}
              {!strateLoading && strateStep === 'sensitive' && (
                <div className="ml-11 space-y-2" data-testid="strate-sensitive">
                  <Link
                    to="/agenda?src=strate_sensitive_redirect"
                    onClick={() => { strateTrackClick('/agenda?src=strate_sensitive_redirect', 'strate_sensitive_redirect'); setIsOpen(false); }}
                  >
                    <Button className="w-full gap-2 text-xs" data-testid="strate-sensitive-expert-btn">
                      <Headphones className="w-3.5 h-3.5" /> Parler à un expert
                    </Button>
                  </Link>
                </div>
              )}

              {/* Final CTAs (step route) */}
              {!strateLoading && strateStep === 'route' && strateCtas && (
                <div className="ml-11 space-y-2" data-testid="strate-final-ctas">
                  {strateCtas.primary && (
                    <CtaLink
                      href={strateCtas.primary.href}
                      src={strateCtas.primary.src}
                      track={strateTrackClick}
                      onAfter={() => setIsOpen(false)}
                    >
                      <Button className="w-full justify-start gap-2 text-xs bg-[#C9A84C] hover:bg-[#B89640] text-[#0a0a08] font-semibold" data-testid="strate-primary-cta">
                        <ArrowRight className="w-3.5 h-3.5" />
                        {strateCtas.primary.label}
                      </Button>
                    </CtaLink>
                  )}
                  {strateCtas.alternative && (
                    <CtaLink
                      href={strateCtas.alternative.href}
                      src={strateCtas.alternative.src}
                      track={strateTrackClick}
                      onAfter={() => setIsOpen(false)}
                    >
                      <Button variant="outline" className="w-full justify-start gap-2 text-xs" data-testid="strate-alt-cta">
                        <ArrowRight className="w-3.5 h-3.5" />
                        {strateCtas.alternative.label}
                      </Button>
                    </CtaLink>
                  )}
                  <button
                    onClick={strateReset}
                    className="w-full text-[11px] text-muted-foreground hover:text-foreground underline pt-1"
                    data-testid="strate-restart"
                  >
                    Recommencer
                  </button>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}

          {/* ---------- FALLBACK / LEGACY CHAT ---------- */}
          {(!strateEnabled || showFallbackChat) && (
          <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/30">
            {messages.map((message, index) => (
              <div key={index}>
                <div className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${message.role === 'user' ? 'bg-accent text-accent-foreground' : 'bg-muted text-muted-foreground'}`}>
                    {message.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>
                  <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === 'user' ? 'bg-accent text-accent-foreground rounded-tr-sm' : 'bg-card border border-border rounded-tl-sm'}`}>
                    <div className="text-sm prose prose-sm max-w-none">
                      <ReactMarkdown
                        components={{
                          a: ({ href, children }) => (
                            <Link to={href || '#'} className="text-accent underline hover:no-underline" onClick={() => setIsOpen(false)}>{children}</Link>
                          ),
                          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                          ul: ({ children }) => <ul className="list-disc pl-4 mb-2">{children}</ul>,
                          li: ({ children }) => <li className="mb-1">{children}</li>,
                          strong: ({ children }) => <strong className="font-semibold">{children}</strong>
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
                {/* CTA Buttons after AI responses (not welcome msg, not FAQ) */}
                {message.role === 'assistant' && index > 0 && !message.is_faq && (
                  <div className="ml-11 mt-2 flex flex-col gap-1.5" data-testid={`chatbot-cta-${index}`}>
                    <button
                      onClick={() => { setIsOpen(false); setTimeout(() => window.dispatchEvent(new Event('strategiia:open')), 300); }}
                      className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium bg-accent/10 text-accent hover:bg-accent/20 border border-accent/20 transition-all text-left"
                      data-testid="chatbot-cta-strategiia"
                    >
                      <Search className="w-3.5 h-3.5 flex-shrink-0" />
                      Analyse complète avec StratégiIA
                    </button>
                    <Link to="/dossier-express" onClick={() => setIsOpen(false)}>
                      <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium bg-foreground/5 text-foreground hover:bg-foreground/10 border border-border transition-all text-left" data-testid="chatbot-cta-dossier">
                        <FileText className="w-3.5 h-3.5 flex-shrink-0" />
                        Analyse de dossier réel (Dossier Express — 97€)
                      </button>
                    </Link>
                  </div>
                )}
              </div>
            ))}

            {loading && <LoadingBubble />}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Questions */}
          {messages.length <= 2 && !quotaExceeded && (
            <div className="px-4 py-2 border-t border-border bg-background">
              <p className="text-xs text-muted-foreground mb-2">Questions fréquentes :</p>
              <div className="flex flex-wrap gap-2">
                {quickQuestions.map((q, i) => (
                  <button key={i} onClick={() => handleSend(q)} className="text-xs bg-muted hover:bg-muted/80 px-3 py-1.5 rounded-full transition-colors" disabled={loading}>
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Quota Exceeded Banner */}
          {quotaExceeded && (
            <div className="px-4 py-4 border-t border-amber-200 bg-amber-50" data-testid="chatbot-quota-exceeded">
              <div className="flex items-start gap-3 mb-3">
                <Lock className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-amber-800">Vous avez utilisé vos 3 questions gratuites</p>
                  <p className="text-xs text-amber-600 mt-1">Pour aller plus loin dans votre démarche :</p>
                </div>
              </div>
              <div className="space-y-2">
                <Link to="/agenda" onClick={() => setIsOpen(false)}>
                  <Button size="sm" className="w-full rounded-lg gap-2 text-xs" data-testid="chatbot-quota-rdv">
                    <Phone className="w-3 h-3" /> Réserver un appel gratuit
                  </Button>
                </Link>
                <Link to="/dossier-express" onClick={() => setIsOpen(false)}>
                  <Button size="sm" variant="outline" className="w-full rounded-lg gap-2 text-xs mt-1" data-testid="chatbot-quota-dossier">
                    <FileText className="w-3 h-3" /> Dossier Express IA — 97€
                  </Button>
                </Link>
                <Link to="/tarifs" onClick={() => setIsOpen(false)}>
                  <Button size="sm" variant="ghost" className="w-full rounded-lg gap-2 text-xs mt-1" data-testid="chatbot-quota-tarifs">
                    <ArrowRight className="w-3 h-3" /> Voir nos prestations
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {/* Input */}
          {!quotaExceeded && (
            <div className="p-4 border-t border-border bg-background">
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={remaining > 0 ? "Posez votre question..." : "Limite atteinte"}
                  disabled={loading || remaining <= 0}
                  className="flex-1 rounded-full"
                  data-testid="chatbot-input"
                />
                <Button
                  onClick={() => handleSend()}
                  disabled={loading || !input.trim() || remaining <= 0}
                  size="icon"
                  className="rounded-full"
                  data-testid="chatbot-send"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-[10px] text-muted-foreground text-center mt-2">
                Il vous reste {remaining} question{remaining !== 1 ? 's' : ''} gratuite{remaining !== 1 ? 's' : ''}
              </p>
            </div>
          )}
          </>
          )}
        </div>
      )}
    </>
  );
};
