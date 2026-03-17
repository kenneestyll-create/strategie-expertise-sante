import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Shield, AlertTriangle, AlertCircle, CheckCircle, ChevronDown, ChevronUp,
  ArrowRight, FileText, Brain, Upload, Zap, Target, TrendingUp, Info, X
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SEVERITY_CONFIG = {
  critical: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', icon: AlertCircle, badge: 'bg-red-100 text-red-700 border-red-200', label: 'Critique' },
  warning: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', icon: AlertTriangle, badge: 'bg-amber-100 text-amber-700 border-amber-200', label: 'Attention' },
  info: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', icon: Info, badge: 'bg-blue-100 text-blue-700 border-blue-200', label: 'Info' },
};

const SCORE_COLORS = {
  red: { gradient: 'from-red-500 to-red-400', text: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', ring: 'ring-red-200' },
  orange: { gradient: 'from-orange-500 to-amber-400', text: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-200', ring: 'ring-orange-200' },
  amber: { gradient: 'from-amber-500 to-yellow-400', text: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', ring: 'ring-amber-200' },
  blue: { gradient: 'from-blue-500 to-indigo-400', text: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200', ring: 'ring-blue-200' },
  green: { gradient: 'from-emerald-500 to-green-400', text: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', ring: 'ring-emerald-200' },
};

const ScoreRing = ({ score, color }) => {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const colors = SCORE_COLORS[color] || SCORE_COLORS.blue;

  return (
    <div className="relative w-36 h-36 flex-shrink-0" data-testid="dossier-score-ring">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 128 128">
        <circle cx="64" cy="64" r={radius} fill="none" stroke="hsl(var(--muted))" strokeWidth="8" />
        <circle
          cx="64" cy="64" r={radius} fill="none"
          stroke="url(#scoreGradient)" strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
        <defs>
          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={color === 'green' ? '#10b981' : color === 'blue' ? '#3b82f6' : color === 'amber' ? '#f59e0b' : color === 'orange' ? '#f97316' : '#ef4444'} />
            <stop offset="100%" stopColor={color === 'green' ? '#22c55e' : color === 'blue' ? '#6366f1' : color === 'amber' ? '#eab308' : color === 'orange' ? '#fb923c' : '#f87171'} />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-3xl font-bold ${colors.text}`} data-testid="dossier-score-value">{score}</span>
        <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">/100</span>
      </div>
    </div>
  );
};

const BreakdownBar = ({ label, score, weight }) => {
  const barColor = score >= 80 ? 'bg-emerald-500' : score >= 60 ? 'bg-blue-500' : score >= 40 ? 'bg-amber-500' : 'bg-red-400';

  return (
    <div className="space-y-1" data-testid={`breakdown-${label.toLowerCase().replace(/\s+/g, '-')}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground">{label}</span>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-muted-foreground/60">{weight}%</span>
          <span className={`text-xs font-semibold ${score >= 80 ? 'text-emerald-600' : score >= 60 ? 'text-blue-600' : score >= 40 ? 'text-amber-600' : 'text-red-500'}`}>
            {score}
          </span>
        </div>
      </div>
      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-700 ${barColor}`} style={{ width: `${score}%` }} />
      </div>
    </div>
  );
};

export const DossierAnalysis = ({ token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [showAllRisks, setShowAllRisks] = useState(false);
  const [expandedRisk, setExpandedRisk] = useState(null);

  const fetchAnalysis = async () => {
    try {
      const res = await axios.get(`${API}/client/dossier-analysis`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setData(res.data);
    } catch {
      setData(null);
    }
    setLoading(false);
  };

  useEffect(() => { fetchAnalysis(); }, [token]);

  // Listen for refresh events
  useEffect(() => {
    const handleRefresh = () => { fetchAnalysis(); };
    window.addEventListener('dossier:refresh', handleRefresh);
    return () => window.removeEventListener('dossier:refresh', handleRefresh);
  }, [token]);

  if (loading) {
    return (
      <Card className="mb-6">
        <CardContent className="p-8 flex items-center justify-center">
          <div className="flex items-center gap-3 text-muted-foreground">
            <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
            <span className="text-sm">Analyse de votre dossier en cours...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const { score, dynamic_message, score_breakdown, weak_points, risk_alerts, missing_documents, actionable_count } = data;
  const msgColor = SCORE_COLORS[dynamic_message.color] || SCORE_COLORS.blue;
  const displayedRisks = showAllRisks ? risk_alerts : risk_alerts.slice(0, 3);

  return (
    <div className="space-y-4 mb-6" data-testid="dossier-analysis">
      {/* Main Score Card */}
      <Card className={`overflow-hidden border-2 ${msgColor.border}`} data-testid="dossier-score-card">
        <CardContent className="p-0">
          <div className="flex flex-col md:flex-row">
            {/* Score Ring */}
            <div className={`flex flex-col items-center justify-center p-6 md:border-r border-border ${msgColor.bg}`}>
              <ScoreRing score={score} color={dynamic_message.color} />
              <p className="text-xs font-semibold mt-2 text-center" data-testid="dossier-score-label">
                Solidité du dossier
              </p>
            </div>

            {/* Dynamic Message + Actionable Count */}
            <div className="flex-1 p-5 md:p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-start gap-2 mb-2">
                  {dynamic_message.tone === 'urgent' && <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />}
                  {dynamic_message.tone === 'attention' && <AlertTriangle className="w-5 h-5 text-orange-500 flex-shrink-0 mt-0.5" />}
                  {dynamic_message.tone === 'encouraging' && <TrendingUp className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />}
                  {dynamic_message.tone === 'positive' && <Shield className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />}
                  {dynamic_message.tone === 'excellent' && <CheckCircle className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />}
                  <h3 className="text-base font-semibold" data-testid="dossier-dynamic-title">
                    {dynamic_message.title}
                  </h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed" data-testid="dossier-dynamic-message">
                  {dynamic_message.message}
                </p>
              </div>

              {/* Actionable count */}
              {actionable_count > 0 && (
                <div className={`mt-4 flex items-center gap-3 p-3 rounded-lg ${msgColor.bg} border ${msgColor.border}`} data-testid="actionable-count">
                  <Zap className={`w-4 h-4 ${msgColor.text} flex-shrink-0`} />
                  <p className={`text-sm font-medium ${msgColor.text}`}>
                    <span className="font-bold">{actionable_count}</span> {actionable_count === 1 ? 'élément à traiter' : 'éléments à traiter'} pour renforcer votre dossier
                  </p>
                </div>
              )}

              {/* Toggle breakdown */}
              <button
                onClick={() => setShowBreakdown(!showBreakdown)}
                className="mt-3 flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                data-testid="toggle-breakdown"
              >
                {showBreakdown ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                {showBreakdown ? 'Masquer le détail' : 'Voir le détail du score'}
              </button>
            </div>
          </div>

          {/* Score Breakdown */}
          {showBreakdown && score_breakdown && (
            <div className="border-t border-border p-5 space-y-3 bg-muted/10" data-testid="score-breakdown">
              {Object.values(score_breakdown).map((item, i) => (
                <BreakdownBar key={i} label={item.label} score={item.score} weight={item.weight} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Weak Points */}
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
                const Icon = config.icon;
                return (
                  <div key={i} className={`p-3 rounded-lg ${config.bg} border ${config.border}`} data-testid={`weak-point-${wp.id}`}>
                    <div className="flex items-start gap-2.5">
                      <Icon className={`w-4 h-4 ${config.text} flex-shrink-0 mt-0.5`} />
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

      {/* Risk Alerts */}
      {risk_alerts.length > 0 && (
        <Card data-testid="risk-alerts-section">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-4.5 h-4.5 text-red-500" />
              <h4 className="text-sm font-semibold">Alertes de risque</h4>
              <Badge variant="outline" className="text-[9px] bg-red-50 text-red-600 border-red-200 ml-auto">
                {risk_alerts.length} alerte{risk_alerts.length > 1 ? 's' : ''}
              </Badge>
            </div>
            <div className="space-y-3">
              {displayedRisks.map((alert, i) => {
                const config = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.warning;
                const Icon = config.icon;
                const isExpanded = expandedRisk === i;

                return (
                  <div
                    key={i}
                    className={`rounded-lg border ${config.border} overflow-hidden transition-all`}
                    data-testid={`risk-alert-${i}`}
                  >
                    <button
                      onClick={() => setExpandedRisk(isExpanded ? null : i)}
                      className={`w-full text-left p-3 ${config.bg} flex items-start gap-2.5 hover:opacity-90 transition-opacity`}
                    >
                      <Icon className={`w-4 h-4 ${config.text} flex-shrink-0 mt-0.5`} />
                      <p className="text-xs leading-relaxed flex-1">{alert.message}</p>
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0 mt-0.5" /> : <ChevronDown className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0 mt-0.5" />}
                    </button>
                    {isExpanded && (
                      <div className="px-3 py-2.5 bg-white border-t border-border/50">
                        <p className="text-xs text-muted-foreground flex items-start gap-2">
                          <ArrowRight className="w-3 h-3 text-accent flex-shrink-0 mt-0.5" />
                          <span><strong className="text-foreground">Action recommandée :</strong> {alert.action}</span>
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            {risk_alerts.length > 3 && (
              <button
                onClick={() => setShowAllRisks(!showAllRisks)}
                className="mt-3 text-xs text-accent hover:text-accent/80 transition-colors flex items-center gap-1"
                data-testid="toggle-all-risks"
              >
                {showAllRisks ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                {showAllRisks ? 'Voir moins' : `Voir toutes les alertes (${risk_alerts.length})`}
              </button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Missing Documents - Quick Actions */}
      {missing_documents.length > 0 && (
        <Card className="border-accent/20" data-testid="missing-docs-actions">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="w-4.5 h-4.5 text-accent" />
              <h4 className="text-sm font-semibold">Documents à fournir</h4>
              <Badge variant="outline" className="text-[9px] bg-accent/10 text-accent border-accent/20 ml-auto">
                {missing_documents.length} manquant{missing_documents.length > 1 ? 's' : ''}
              </Badge>
            </div>
            <div className="space-y-2">
              {missing_documents.map((doc, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between gap-2 p-2.5 rounded-lg border border-border hover:border-accent/30 transition-colors bg-background"
                  data-testid={`missing-doc-${doc.key}`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="w-7 h-7 rounded-md bg-muted flex items-center justify-center flex-shrink-0">
                      <FileText className="w-3.5 h-3.5 text-muted-foreground" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs font-medium truncate">{doc.label}</p>
                      <p className="text-[10px] text-muted-foreground capitalize">{doc.category}</p>
                    </div>
                  </div>
                  <Link to="/espace-client?tab=documents">
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 px-2.5 text-[10px] gap-1 rounded-full border-accent/30 text-accent hover:bg-accent/10"
                      data-testid={`upload-doc-${doc.key}`}
                    >
                      <Upload className="w-3 h-3" />
                      Ajouter
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* CTA: Launch analysis if none done */}
      {data.summary.analyses_ia === 0 && data.summary.total_documents >= 1 && (
        <Card className="border-accent/30 bg-gradient-to-r from-accent/5 to-transparent" data-testid="cta-launch-analysis">
          <CardContent className="p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center flex-shrink-0">
              <Brain className="w-6 h-6 text-accent" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold">Lancez votre analyse StratégiIA</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                Vos documents sont prêts. Obtenez une analyse stratégique personnalisée de votre dossier.
              </p>
            </div>
            <Button
              size="sm"
              className="gap-1.5 rounded-full whitespace-nowrap"
              onClick={() => window.dispatchEvent(new Event('strategiia:open'))}
              data-testid="cta-launch-strategiia"
            >
              Analyser <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
