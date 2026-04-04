import { useState, useRef, useEffect, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  MessageCircle, X, Send, Bot, User,
  ArrowRight, Gauge, Lock, FileText, Phone, Search, Sparkles
} from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const CHAT_LIMIT = 3;

const WAITING_MESSAGES = [
  "Analyse de votre situation en cours",
  "Consultation de notre base juridique",
  "Préparation de votre réponse personnalisée",
];

const LoadingBubble = () => {
  const [msgIndex, setMsgIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isLong, setIsLong] = useState(false);
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

const StrateMascotIcon = ({ size = 40 }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
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
      content: "Bonjour ! Je suis l'assistant d'orientation de S.E.S.\n\nDites-moi en quelques mots votre besoin et je vous oriente vers le bon outil."
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => { scrollToBottom(); }, [messages]);

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
    "Comment préparer une expertise ?",
    "Qu'est-ce que la MDPH ?",
    "Quels sont vos tarifs ?",
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
      {/* Mascot Floating Button — Desktop only (mobile trigger is in Hero) */}
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
              <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-accent-foreground" />
              </div>
              <div>
                <h3 className="font-semibold text-sm">Assistant d'orientation</h3>
                <p className="text-xs text-primary-foreground/70">Je vous guide vers le bon outil</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {/* Quota counter */}
              <Badge
                className={`text-[10px] ${remaining > 2 ? 'bg-green-500/20 text-green-300 border-green-500/30' : remaining > 0 ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' : 'bg-red-500/20 text-red-300 border-red-500/30'}`}
                data-testid="chatbot-quota-badge"
              >
                <Gauge className="w-3 h-3 mr-1" />
                {remaining}/{CHAT_LIMIT}
              </Badge>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-primary-foreground/10 rounded-lg transition-colors"
                aria-label="Fermer le chat"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/30">
            {messages.map((message, index) => (
              <div key={index}>
                <div className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${message.role === 'user' ? 'bg-accent text-accent-foreground' : 'bg-muted text-muted-foreground'}`}>
                    {message.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>
                  <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === 'user' ? 'bg-accent text-accent-foreground rounded-tr-sm' : 'bg-card border border-border rounded-tl-sm'}`}>
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
        </div>
      )}
    </>
  );
};
