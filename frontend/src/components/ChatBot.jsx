import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  MessageCircle, X, Send, Loader2, Bot, User,
  ArrowRight, Gauge, Lock, FileText, Phone
} from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const CHAT_LIMIT = 5;

export const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Bonjour ! Je suis l'assistant de Stratégie & Expertise Santé, ici pour vous orienter. Comment puis-je vous aider aujourd'hui ?\n\nVous pouvez me poser des questions sur :\n- Les expertises médicales\n- La MDPH et vos droits\n- Les accidents du travail\n- La protection juridique\n- Nos tarifs et services\n\nPour un accompagnement personnalisé, n'hésitez pas à prendre rendez-vous avec notre équipe."
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [questionsUsed, setQuestionsUsed] = useState(0);
  const [quotaExceeded, setQuotaExceeded] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => { scrollToBottom(); }, [messages]);

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
      {/* Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-accent hover:bg-accent/90 text-accent-foreground rounded-full shadow-lg flex items-center justify-center transition-all hover:scale-105"
          style={{ zIndex: 'var(--z-chatbot)' }}
          data-testid="chatbot-button"
          aria-label="Ouvrir le chat"
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-[380px] max-w-[calc(100vw-2rem)] h-[550px] max-h-[calc(100vh-6rem)] flex flex-col bg-background border border-border rounded-2xl shadow-2xl overflow-hidden" style={{ zIndex: 'var(--z-chatbot)' }}>
          {/* Header */}
          <div className="flex items-center justify-between p-4 bg-foreground text-primary-foreground">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-accent-foreground" />
              </div>
              <div>
                <h3 className="font-semibold text-sm">Assistant</h3>
                <p className="text-xs text-primary-foreground/70">En ligne</p>
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
              <div key={index} className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
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
            ))}

            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                  <Bot className="w-4 h-4 text-muted-foreground" />
                </div>
                <div className="bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3">
                  <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
                </div>
              </div>
            )}

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
                  <p className="text-sm font-medium text-amber-800">Vous avez utilisé vos 5 questions gratuites</p>
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
