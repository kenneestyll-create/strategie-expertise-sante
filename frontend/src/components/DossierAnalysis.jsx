import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Shield, AlertTriangle, AlertCircle, CheckCircle, ChevronDown, ChevronUp,
  ArrowRight, FileText, Brain, Upload, Zap, Target, TrendingUp, Info,
  ScanLine, Star, Crown, Sparkles, Eye, ChevronRight, Lock
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SEVERITY_CONFIG = {
  critical: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', icon: AlertCircle, badge: 'bg-red-100 text-red-700 border-red-200', label: 'Critique' },
  warning: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', icon: AlertTriangle, badge: 'bg-amber-100 text-amber-700 border-amber-200', label: 'Attention' },
  info: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', icon: Info, badge: 'bg-blue-100 text-blue-700 border-blue-200', label: 'Info' },
};

const SCORE_COLORS = {
  red: { text: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' },
  orange: { text: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-200' },
  amber: { text: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200' },
  blue: { text: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200' },
  green: { text: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200' },
};

const PRIORITY_BADGE = {
  haute: { label: 'Priorité haute', className: 'bg-red-100 text-red-700 border-red-200' },
  moyenne: { label: 'Priorité moyenne', className: 'bg-amber-100 text-amber-700 border-amber-200' },
  faible: { label: 'Priorité faible', className: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
};

const ACTION_ICONS = { upload: Upload, file: FileText, brain: Brain, zap: Zap, scan: ScanLine };

/* ── Score Ring ── */
const ScoreRing = ({ score, color, blurred }) => {
  const r = 54, c = 2 * Math.PI * r;
  const colors = SCORE_COLORS[color] || SCORE_COLORS.blue;
  const stopA = color === 'green' ? '#10b981' : color === 'blue' ? '#3b82f6' : color === 'amber' ? '#f59e0b' : color === 'orange' ? '#f97316' : '#ef4444';
  const stopB = color === 'green' ? '#22c55e' : color === 'blue' ? '#6366f1' : color === 'amber' ? '#eab308' : color === 'orange' ? '#fb923c' : '#f87171';
  return (
    <div className={`relative w-36 h-36 flex-shrink-0 ${blurred ? 'blur-sm opacity-60' : ''}`} data-testid="dossier-score-ring">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 128 128">
        <circle cx="64" cy="64" r={r} fill="none" stroke="hsl(var(--muted))" strokeWidth="8" />
        <circle cx="64" cy="64" r={r} fill="none" stroke="url(#scoreGrad)" strokeWidth="8" strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c - (score / 100) * c} className="transition-all duration-1000 ease-out" />
        <defs><linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stopColor={stopA} /><stop offset="100%" stopColor={stopB} /></linearGradient></defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-3xl font-bold ${colors.text}`} data-testid="dossier-score-value">{score}</span>
        <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">/100</span>
      </div>
    </div>
  );
};

/* ── Key Metric Mini Bar ── */
const KeyMetric = ({ label, value }) => {
  const barColor = value >= 80 ? 'bg-emerald-500' : value >= 50 ? 'bg-amber-500' : 'bg-red-400';
  const textColor = value >= 80 ? 'text-emerald-600' : value >= 50 ? 'text-amber-600' : 'text-red-500';
  return (
    <div className="flex-1 min-w-0" data-testid={`key-metric-${label.toLowerCase()}`}>
      <div className="flex items-baseline justify-between mb-1">
        <span className="text-[11px] text-muted-foreground truncate">{label}</span>
        <span className={`text-xs font-bold ml-1 ${textColor}`}>{value}%</span>
      </div>
      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-700 ${barColor}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
};

/* ── Breakdown Bar ── */
const BreakdownBar = ({ label, score, weight }) => {
  const barColor = score >= 80 ? 'bg-emerald-500' : score >= 60 ? 'bg-blue-500' : score >= 40 ? 'bg-amber-500' : 'bg-red-400';
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground">{label}</span>
        <div className="flex items-center gap-2">
          {weight > 0 && <span className="text-[10px] text-muted-foreground/60">{weight}%</span>}
          <span className={`text-xs font-semibold ${score >= 80 ? 'text-emerald-600' : score >= 60 ? 'text-blue-600' : score >= 40 ? 'text-amber-600' : 'text-red-500'}`}>{score}</span>
        </div>
      </div>
      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-700 ${barColor}`} style={{ width: `${score}%` }} />
      </div>
    </div>
  );
};

/* ── Upsell CTA for non-Dossier Express IA clients ── */
const DossierExpressUpsell = ({ score, dynamic_message }) => {
  const msgColor = SCORE_COLORS[dynamic_message?.color] || SCORE_COLORS.blue;
  return (
    <div className="space-y-4 mb-6" data-testid="dossier-analysis-upsell">
      {/* Teaser score card - blurred */}
      <Card className={`overflow-hidden border-2 ${msgColor.border} relative`} data-testid="dossier-score-card-teaser">
        <CardContent className="p-0">
          <div className="flex flex-col md:flex-row">
            <div className={`flex flex-col items-center justify-center p-6 md:border-r border-border ${msgColor.bg}`}>
              <ScoreRing score={score} color={dynamic_message?.color || 'blue'} blurred />
              <p className="text-xs font-semibold mt-2 text-center">Solidité du dossier</p>
            </div>
            <div className="flex-1 p-5 md:p-6">
              <div className="blur-sm opacity-50 pointer-events-none select-none">
                <div className="flex gap-4 p-3 rounded-lg bg-muted/30 border border-border/50 mb-3">
                  <div className="flex-1"><div className="h-1.5 bg-muted rounded-full mb-1" /><div className="h-3 bg-muted rounded w-16" /></div>
                  <div className="flex-1"><div className="h-1.5 bg-muted rounded-full mb-1" /><div className="h-3 bg-muted rounded w-16" /></div>
                  <div className="flex-1"><div className="h-1.5 bg-muted rounded-full mb-1" /><div className="h-3 bg-muted rounded w-16" /></div>
                </div>
                <div className="space-y-2">
                  <div className="h-4 bg-muted rounded w-3/4" />
                  <div className="h-3 bg-muted rounded w-full" />
                  <div className="h-3 bg-muted rounded w-5/6" />
                </div>
              </div>
              {/* Overlay lock */}
              <div className="absolute inset-0 flex items-center justify-center bg-background/50 backdrop-blur-[3px]">
                <div className="text-center p-6 max-w-sm">
                  <div className="w-14 h-14 rounded-2xl bg-amber-500/15 flex items-center justify-center mx-auto mb-3 shadow-lg shadow-amber-500/10">
                    <Zap className="w-7 h-7 text-amber-500" />
                  </div>
                  <h4 className="font-bold text-base mb-1" data-testid="upsell-title">Débloquez votre analyse complète</h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    Score de solidité, points de fragilité, alertes de risque, anticipation des refus et actions recommandées.
                  </p>
                  <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-[10px] text-muted-foreground mb-4">
                    <span className="flex items-center gap-1"><CheckCircle className="w-3 h-3 text-emerald-500" />Rapport sous 2h</span>
                    <span className="flex items-center gap-1"><Shield className="w-3 h-3 text-blue-500" />Stratégie personnalisée</span>
                    <span className="flex items-center gap-1"><Target className="w-3 h-3 text-accent" />Actions concrètes</span>
                  </div>
                  <Link to="/dossier-express">
                    <Button className="gap-2 rounded-full bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold shadow-lg shadow-amber-500/20 hover:scale-[1.02] transition-all" data-testid="upsell-dossier-express-btn">
                      <FileText className="w-4 h-4" /> Dossier Express IA — 97€
                      <ArrowRight className="w-4 h-4" />
                    </Button>
                  </Link>
                  <p className="text-[10px] text-muted-foreground mt-3">
                    Paiement sécurisé — Satisfait ou complément offert
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

/* ── Main Component ── */
export const DossierAnalysis = ({ token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [showAllRisks, setShowAllRisks] = useState(false);
  const [expandedRisk, setExpandedRisk] = useState(null);
  const [expandedPrediction, setExpandedPrediction] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const prevScoreRef = useRef(null);

  const fetchAnalysis = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/client/dossier-analysis`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const newScore = res.data.score;
      if (prevScoreRef.current !== null && newScore !== prevScoreRef.current) {
        const delta = newScore - prevScoreRef.current;
        if (delta > 0) {
          setFeedback({ type: 'up', delta, newScore });
        } else if (delta < 0) {
          setFeedback({ type: 'info', delta: 0, newScore, message: 'Score recalculé après modification.' });
        }
        setTimeout(() => setFeedback(null), 6000);
      }
      prevScoreRef.current = newScore;
      setData(res.data);
    } catch {
      setData(null);
    }
    setLoading(false);
  }, [token]);

  useEffect(() => { fetchAnalysis(); }, [token, fetchAnalysis]);

  useEffect(() => {
    const handleRefresh = () => { fetchAnalysis(); };
    window.addEventListener('dossier:refresh', handleRefresh);
    return () => window.removeEventListener('dossier:refresh', handleRefresh);
  }, [fetchAnalysis]);

  const handleActionClick = (action) => {
    if (action.cta_target === 'documents') {
      const tabBtn = document.querySelector('[data-testid="tab-documents"]');
      if (tabBtn) { tabBtn.click(); tabBtn.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
    } else if (action.cta_target === 'strategiia') {
      window.dispatchEvent(new Event('strategiia:open'));
    }
  };

  if (loading) {
    return (
      <Card className="mb-6"><CardContent className="p-8 flex items-center justify-center">
        <div className="flex items-center gap-3 text-muted-foreground">
          <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
          <span className="text-sm">Analyse de votre dossier en cours...</span>
        </div>
      </CardContent></Card>
    );
  }
  if (!data) return null;

  // ── FREE client: show upsell teaser ──
  if (!data.has_dossier_express) {
    return <DossierExpressUpsell score={data.score} dynamic_message={data.dynamic_message} />;
  }

  // ── DOSSIER EXPRESS client: full premium analysis ──
  const { score, key_metrics, dynamic_message, score_breakdown, weak_points, risk_alerts, missing_documents, actionable_count, recommended_actions, predictions, premium_cta } = data;
  const humanReviewed = data.human_reviewed;
  const reviewedAt = data.reviewed_at;
  const msgColor = SCORE_COLORS[dynamic_message.color] || SCORE_COLORS.blue;
  const displayedRisks = showAllRisks ? risk_alerts : risk_alerts.slice(0, 3);

  return (
    <div className="space-y-4 mb-6" data-testid="dossier-analysis">

      {/* ── Expert Review Banner ── */}
      {humanReviewed && (
        <div className="relative overflow-hidden rounded-xl border border-amber-300/50 bg-gradient-to-r from-amber-50/80 via-white to-amber-50/40" data-testid="expert-review-banner">
          <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-amber-400 to-amber-600 rounded-l-xl" />
          <div className="flex items-center gap-3 px-4 py-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center flex-shrink-0 shadow-md shadow-amber-200/40">
              <Shield className="w-4.5 h-4.5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-bold text-amber-900">Rapport vérifié par un expert</span>
                <Badge className="text-[8px] bg-amber-100 text-amber-800 border-amber-300/60">Analyse premium</Badge>
              </div>
              <p className="text-[11px] text-amber-700/70 mt-0.5">
                Ce dossier a été vérifié et complété par notre équipe d'experts pour garantir l'exhaustivité et la fiabilité des informations.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ── Real-time Feedback ── */}
      {feedback && (
        <div className={`animate-in slide-in-from-top-2 duration-300 p-3.5 rounded-lg flex items-center gap-3 ${feedback.type === 'up' ? 'bg-emerald-50 border border-emerald-200' : 'bg-blue-50 border border-blue-200'}`} data-testid="score-feedback-toast">
          <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${feedback.type === 'up' ? 'bg-emerald-100' : 'bg-blue-100'}`}>
            <TrendingUp className={`w-4.5 h-4.5 ${feedback.type === 'up' ? 'text-emerald-600' : 'text-blue-600'}`} />
          </div>
          <div className="flex-1">
            {feedback.type === 'up' ? (
              <>
                <p className="text-sm font-semibold text-emerald-800">Votre score a augmenté de +{feedback.delta}%</p>
                <p className="text-xs text-emerald-600">Cette action renforce significativement votre dossier — Solidité : <span className="font-bold">{feedback.newScore}%</span></p>
              </>
            ) : (
              <p className="text-sm text-blue-700">{feedback.message}</p>
            )}
          </div>
          {feedback.type === 'up' && <Sparkles className="w-5 h-5 text-emerald-400 animate-pulse flex-shrink-0" />}
        </div>
      )}

      {/* ── Main Score Card + Key Metrics ── */}
      <Card className={`overflow-hidden border-2 ${msgColor.border}`} data-testid="dossier-score-card">
        <CardContent className="p-0">
          <div className="flex flex-col md:flex-row">
            <div className={`flex flex-col items-center justify-center p-6 md:border-r border-border ${msgColor.bg}`}>
              <ScoreRing score={score} color={dynamic_message.color} />
              <p className="text-xs font-semibold mt-2 text-center" data-testid="dossier-score-label">Solidité du dossier</p>
              {humanReviewed && (
                <div className="mt-2 group relative" data-testid="expert-reviewed-badge">
                  <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gradient-to-r from-amber-50 to-amber-100 border border-amber-300/60 shadow-sm">
                    <CheckCircle className="w-3.5 h-3.5 text-amber-600" />
                    <span className="text-[10px] font-semibold text-amber-800 tracking-wide uppercase">Relu par expert</span>
                  </div>
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 px-3 py-2 bg-foreground text-primary-foreground text-[11px] rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none z-50">
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-2 h-2 bg-foreground rotate-45" />
                    Ce dossier a été vérifié et complété par notre équipe d'experts pour garantir l'exhaustivité et la fiabilité des informations.
                    {reviewedAt && <span className="block mt-1 text-primary-foreground/60">Relu le {new Date(reviewedAt).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}</span>}
                  </div>
                </div>
              )}
            </div>
            <div className="flex-1 p-5 md:p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-start gap-2 mb-2">
                  {dynamic_message.tone === 'urgent' && <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />}
                  {dynamic_message.tone === 'attention' && <AlertTriangle className="w-5 h-5 text-orange-500 flex-shrink-0 mt-0.5" />}
                  {dynamic_message.tone === 'encouraging' && <TrendingUp className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />}
                  {dynamic_message.tone === 'positive' && <Shield className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />}
                  {dynamic_message.tone === 'excellent' && <CheckCircle className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />}
                  <h3 className="text-base font-semibold" data-testid="dossier-dynamic-title">{dynamic_message.title}</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed" data-testid="dossier-dynamic-message">{dynamic_message.message}</p>
              </div>
              {key_metrics && (
                <div className="flex gap-4 mt-4 p-3 rounded-lg bg-muted/30 border border-border/50" data-testid="key-metrics">
                  <KeyMetric label="Complétude" value={key_metrics.completeness} />
                  <KeyMetric label="Qualité" value={key_metrics.quality} />
                  <KeyMetric label="Cohérence" value={key_metrics.coherence} />
                </div>
              )}
              {actionable_count > 0 && (
                <div className={`mt-3 flex items-center gap-3 p-3 rounded-lg ${msgColor.bg} border ${msgColor.border}`} data-testid="actionable-count">
                  <Zap className={`w-4 h-4 ${msgColor.text} flex-shrink-0`} />
                  <p className={`text-sm font-medium ${msgColor.text}`}><span className="font-bold">{actionable_count}</span> {actionable_count === 1 ? 'élément à traiter' : 'éléments à traiter'} pour renforcer votre dossier</p>
                </div>
              )}
              <button onClick={() => setShowBreakdown(!showBreakdown)} className="mt-3 flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors" data-testid="toggle-breakdown">
                {showBreakdown ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                {showBreakdown ? 'Masquer le détail complet' : 'Voir le détail complet du score'}
              </button>
            </div>
          </div>
          {showBreakdown && score_breakdown && (
            <div className="border-t border-border p-5 space-y-3 bg-muted/10" data-testid="score-breakdown">
              {Object.values(score_breakdown).map((item, i) => (
                <BreakdownBar key={i} label={item.label} score={item.score} weight={item.weight} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* ── Recommended Actions (max 3) ── */}
      {recommended_actions && recommended_actions.length > 0 && (
        <Card className="border-accent/20" data-testid="recommended-actions-section">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-4.5 h-4.5 text-accent" />
              <h4 className="text-sm font-semibold">Prochaines actions recommandées</h4>
            </div>
            <div className="space-y-2.5">
              {recommended_actions.map((action, i) => {
                const Icon = ACTION_ICONS[action.icon] || FileText;
                const priorityCfg = PRIORITY_BADGE[action.priority_level] || PRIORITY_BADGE.moyenne;
                return (
                  <button key={i} onClick={() => handleActionClick(action)} className="w-full text-left p-3 rounded-lg border border-border hover:border-accent/40 hover:bg-accent/5 transition-all group" data-testid={`recommended-action-${action.action_id}`}>
                    <div className="flex items-start gap-3">
                      <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0 group-hover:bg-accent/20 transition-colors"><Icon className="w-4 h-4 text-accent" /></div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-semibold">{action.title}</span>
                          <Badge variant="outline" className={`text-[8px] px-1.5 ${priorityCfg.className}`} data-testid={`priority-badge-${action.priority_level}`}>{priorityCfg.label}</Badge>
                        </div>
                        <p className="text-[11px] text-muted-foreground line-clamp-1 mt-0.5">{action.description}</p>
                      </div>
                      <div className="flex flex-col items-end gap-1 flex-shrink-0">
                        <Badge variant="outline" className="text-[8px] px-1.5 bg-emerald-50 text-emerald-700 border-emerald-200 whitespace-nowrap">{action.impact}</Badge>
                        <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/40 group-hover:text-accent transition-colors" />
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Weak Points ── */}
      {weak_points.length > 0 && (
        <Card data-testid="weak-points-section">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <Target className="w-4.5 h-4.5 text-accent" />
              <h4 className="text-sm font-semibold">Points de fragilité détectés</h4>
              <Badge variant="outline" className="text-[9px] ml-auto">{weak_points.length}</Badge>
            </div>
            <div className="space-y-3">
              {weak_points.map((wp, i) => {
                const config = SEVERITY_CONFIG[wp.severity] || SEVERITY_CONFIG.info;
                const IconC = config.icon;
                return (
                  <div key={i} className={`p-3 rounded-lg ${config.bg} border ${config.border}`} data-testid={`weak-point-${wp.id}`}>
                    <div className="flex items-start gap-2.5">
                      <IconC className={`w-4 h-4 ${config.text} flex-shrink-0 mt-0.5`} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`text-xs font-semibold ${config.text}`}>{wp.title}</span>
                          <Badge variant="outline" className={`text-[8px] px-1.5 ${config.badge}`}>{config.label}</Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">{wp.detail}</p>
                        <p className={`text-[11px] ${config.text} mt-1 font-medium`}>{wp.impact}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Risk Alerts ── */}
      {risk_alerts.length > 0 && (
        <Card data-testid="risk-alerts-section">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-4.5 h-4.5 text-red-500" />
              <h4 className="text-sm font-semibold">Alertes de risque</h4>
              <Badge variant="outline" className="text-[9px] bg-red-50 text-red-600 border-red-200 ml-auto">{risk_alerts.length} alerte{risk_alerts.length > 1 ? 's' : ''}</Badge>
            </div>
            <div className="space-y-3">
              {displayedRisks.map((alert, i) => {
                const config = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.warning;
                const IconC = config.icon;
                const isExpanded = expandedRisk === i;
                return (
                  <div key={i} className={`rounded-lg border ${config.border} overflow-hidden`} data-testid={`risk-alert-${i}`}>
                    <button onClick={() => setExpandedRisk(isExpanded ? null : i)} className={`w-full text-left p-3 ${config.bg} flex items-start gap-2.5 hover:opacity-90 transition-opacity`}>
                      <IconC className={`w-4 h-4 ${config.text} flex-shrink-0 mt-0.5`} />
                      <p className="text-xs leading-relaxed flex-1">{alert.message}</p>
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0 mt-0.5" /> : <ChevronDown className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0 mt-0.5" />}
                    </button>
                    {isExpanded && (
                      <div className="px-3 py-2.5 bg-white border-t border-border/50">
                        <p className="text-xs text-muted-foreground flex items-start gap-2"><ArrowRight className="w-3 h-3 text-accent flex-shrink-0 mt-0.5" /><span><strong className="text-foreground">Action recommandée :</strong> {alert.action}</span></p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            {risk_alerts.length > 3 && (
              <button onClick={() => setShowAllRisks(!showAllRisks)} className="mt-3 text-xs text-accent hover:text-accent/80 transition-colors flex items-center gap-1" data-testid="toggle-all-risks">
                {showAllRisks ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                {showAllRisks ? 'Voir moins' : `Voir toutes les alertes (${risk_alerts.length})`}
              </button>
            )}
          </CardContent>
        </Card>
      )}

      {/* ── Predictions ── */}
      {predictions && predictions.length > 0 && (
        <Card className="border-purple-200" data-testid="predictions-section">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <Eye className="w-4.5 h-4.5 text-purple-600" />
              <h4 className="text-sm font-semibold">Anticipation des motifs de refus</h4>
              <Badge variant="outline" className="text-[9px] bg-purple-50 text-purple-700 border-purple-200 ml-auto">Prédictif</Badge>
            </div>
            <div className="space-y-3">
              {predictions.map((pred, i) => {
                const isExpanded = expandedPrediction === i;
                const probColor = pred.probability === 'Certaine' || pred.probability === 'Élevée' ? 'bg-red-100 text-red-700 border-red-200' : 'bg-amber-100 text-amber-700 border-amber-200';
                return (
                  <div key={i} className="rounded-lg border border-purple-100 overflow-hidden" data-testid={`prediction-${i}`}>
                    <button onClick={() => setExpandedPrediction(isExpanded ? null : i)} className="w-full text-left p-3 bg-purple-50/50 flex items-start gap-2.5 hover:bg-purple-50 transition-colors">
                      <AlertCircle className="w-4 h-4 text-purple-500 flex-shrink-0 mt-0.5" />
                      <div className="flex-1 min-w-0"><div className="flex items-center gap-2 flex-wrap"><span className="text-xs font-semibold text-purple-900">{pred.title}</span><Badge variant="outline" className={`text-[8px] px-1.5 ${probColor}`}>{pred.probability}</Badge></div></div>
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0 mt-0.5" /> : <ChevronDown className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0 mt-0.5" />}
                    </button>
                    {isExpanded && (
                      <div className="px-3 py-3 bg-white border-t border-purple-100 space-y-2">
                        <p className="text-xs text-muted-foreground leading-relaxed">{pred.detail}</p>
                        <div className="flex items-start gap-2 p-2 rounded bg-red-50 border border-red-100"><AlertTriangle className="w-3 h-3 text-red-500 flex-shrink-0 mt-0.5" /><p className="text-[11px] text-red-700"><strong>Conséquence :</strong> {pred.consequence}</p></div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Missing Documents ── */}
      {missing_documents.length > 0 && (
        <Card className="border-accent/20" data-testid="missing-docs-actions">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="w-4.5 h-4.5 text-accent" />
              <h4 className="text-sm font-semibold">Documents à fournir</h4>
              <Badge variant="outline" className="text-[9px] bg-accent/10 text-accent border-accent/20 ml-auto">{missing_documents.length} manquant{missing_documents.length > 1 ? 's' : ''}</Badge>
            </div>
            <div className="space-y-2">
              {missing_documents.map((doc, i) => (
                <div key={i} className="flex items-center justify-between gap-2 p-2.5 rounded-lg border border-border hover:border-accent/30 transition-colors bg-background" data-testid={`missing-doc-${doc.key}`}>
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="w-7 h-7 rounded-md bg-muted flex items-center justify-center flex-shrink-0"><FileText className="w-3.5 h-3.5 text-muted-foreground" /></div>
                    <div className="min-w-0"><p className="text-xs font-medium truncate">{doc.label}</p><p className="text-[10px] text-muted-foreground capitalize">{doc.category}</p></div>
                  </div>
                  <Button size="sm" variant="outline" className="h-7 px-2.5 text-[10px] gap-1 rounded-full border-accent/30 text-accent hover:bg-accent/10" data-testid={`upload-doc-${doc.key}`}
                    onClick={() => { const tabBtn = document.querySelector('[data-testid="tab-documents"]'); if (tabBtn) tabBtn.click(); }}>
                    <Upload className="w-3 h-3" />Ajouter
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Premium Expert CTA ── */}
      {premium_cta && premium_cta.show && (
        <Card className="border-amber-300/50 bg-gradient-to-br from-amber-50/80 via-white to-orange-50/40 overflow-hidden relative" data-testid="premium-expert-cta">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-amber-200/20 to-transparent rounded-bl-full" />
          <CardContent className="p-5 relative">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center flex-shrink-0 shadow-lg shadow-amber-200/50"><Crown className="w-6 h-6 text-white" /></div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1"><h4 className="text-sm font-bold text-amber-900">{premium_cta.title}</h4><Badge className="text-[8px] bg-amber-100 text-amber-800 border-amber-300">Premium</Badge></div>
                <p className="text-xs text-amber-700/80 mb-3">{premium_cta.subtitle}</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 mb-4">
                  {premium_cta.features.map((f, i) => (<div key={i} className="flex items-center gap-1.5"><Star className="w-3 h-3 text-amber-500 flex-shrink-0" /><span className="text-[11px] text-amber-800">{f}</span></div>))}
                </div>
                <div className="flex items-center gap-3 flex-wrap">
                  <Button size="sm" className="gap-1.5 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-md shadow-amber-200/50 text-xs" data-testid="premium-cta-button"><Crown className="w-3.5 h-3.5" />{premium_cta.cta_label}</Button>
                  <span className="text-[10px] text-amber-600/70">{premium_cta.score_context}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
