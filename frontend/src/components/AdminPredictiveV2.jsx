import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import {
  Loader2, RefreshCw, Lock, Unlock, ShieldCheck, ShieldAlert, ShieldOff,
  AlertTriangle, CheckCircle, XCircle, FlaskConical, ArrowLeftRight,
  History, Settings, Power, PowerOff, Eye, TrendingUp, Database, Layers,
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// =============================================================================
// SOUS-COMPOSANT : Verrous d'activation
// =============================================================================

const LockIndicator = ({ lock }) => {
  const passed = lock.passed;
  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg border ${passed ? 'border-emerald-200 bg-emerald-50/30' : 'border-red-200 bg-red-50/30'}`}
      data-testid={`v2-lock-${lock.id}`}>
      {passed ? <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" /> : <XCircle className="w-4 h-4 text-red-500 flex-shrink-0" />}
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium">{lock.label}</p>
        <p className="text-[10px] text-muted-foreground">
          {passed ? 'Satisfait' : lock.reason}
          {' '} ({lock.current} / {lock.required})
        </p>
      </div>
    </div>
  );
};

// =============================================================================
// COMPOSANT PRINCIPAL
// =============================================================================

export const AdminPredictiveV2 = ({ axiosConfig }) => {
  const [status, setStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activating, setActivating] = useState(false);

  // Dialogs
  const [showActivateStep1, setShowActivateStep1] = useState(false);
  const [showActivateStep2, setShowActivateStep2] = useState(false);
  const [showActivateStep3, setShowActivateStep3] = useState(false);
  const [confirmText, setConfirmText] = useState('');

  // Sandbox
  const [sandboxMode, setSandboxMode] = useState(false);
  const [sandboxSituation, setSandboxSituation] = useState('');
  const [sandboxType, setSandboxType] = useState('');
  const [sandboxResult, setSandboxResult] = useState(null);
  const [sandboxLoading, setSandboxLoading] = useState(false);

  // Comparator
  const [compareMode, setCompareMode] = useState(false);
  const [compareId, setCompareId] = useState('');
  const [compareResult, setCompareResult] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);

  // Tab interne
  const [activeTab, setActiveTab] = useState('overview');

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true);
      const [statusRes, historyRes, logRes] = await Promise.all([
        axios.get(`${API}/predictive-v2/status`, axiosConfig),
        axios.get(`${API}/knowledge-patterns/v2-readiness/history`, axiosConfig).catch(() => ({ data: { history: [] } })),
        axios.get(`${API}/predictive-v2/audit-log`, axiosConfig).catch(() => ({ data: { logs: [] } })),
      ]);
      setStatus(statusRes.data);
      setHistory(historyRes.data.history || []);
      setAuditLog(logRes.data.logs || []);
    } catch {
      toast.error("Erreur chargement V2");
    } finally {
      setLoading(false);
    }
  }, [axiosConfig]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  // --- Activation flow ---
  const handleActivateStep1 = () => {
    if (!status?.can_activate) {
      toast.error("Activation impossible — verrous non satisfaits");
      return;
    }
    setShowActivateStep1(true);
  };

  const handleActivateStep2 = () => {
    setShowActivateStep1(false);
    setShowActivateStep2(true);
  };

  const handleActivateStep3 = () => {
    setShowActivateStep2(false);
    setConfirmText('');
    setShowActivateStep3(true);
  };

  const handleActivateFinal = async () => {
    if (confirmText !== 'ACTIVER V2') {
      toast.error('Saisissez exactement : ACTIVER V2');
      return;
    }
    setActivating(true);
    try {
      await axios.post(`${API}/predictive-v2/activate`, { confirmation_text: confirmText }, axiosConfig);
      toast.success('V2 Predictive activee');
      setShowActivateStep3(false);
      setConfirmText('');
      await fetchAll();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Activation echouee");
    } finally {
      setActivating(false);
    }
  };

  const handleDeactivate = async () => {
    try {
      await axios.post(`${API}/predictive-v2/deactivate`, {}, axiosConfig);
      toast.success('V2 desactivee — retour V1 immediat');
      await fetchAll();
    } catch {
      toast.error("Erreur lors de la desactivation");
    }
  };

  // --- Sandbox ---
  const handleSandbox = async () => {
    if (!sandboxSituation.trim()) { toast.error("Situation requise"); return; }
    setSandboxLoading(true);
    setSandboxResult(null);
    try {
      const res = await axios.post(`${API}/predictive-v2/sandbox/analyze`, {
        situation: sandboxSituation, type_dossier: sandboxType,
      }, axiosConfig);
      setSandboxResult(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur sandbox");
    } finally {
      setSandboxLoading(false);
    }
  };

  // --- Comparator ---
  const handleCompare = async () => {
    if (!compareId.trim()) { toast.error("ID analyse requis"); return; }
    setCompareLoading(true);
    setCompareResult(null);
    try {
      const res = await axios.post(`${API}/predictive-v2/sandbox/compare`, {
        analysis_id: compareId,
      }, axiosConfig);
      setCompareResult(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur comparaison");
    } finally {
      setCompareLoading(false);
    }
  };

  if (loading) {
    return <Card data-testid="v2-predictive-card"><CardContent className="flex items-center justify-center py-16"><Loader2 className="w-5 h-5 animate-spin" /></CardContent></Card>;
  }

  if (!status) return null;

  const isEnabled = status.enabled;
  const canActivate = status.can_activate;
  const readiness = status.readiness;

  return (
    <div className="space-y-6" data-testid="v2-predictive-panel">
      {/* ===== HEADER + MASTER SWITCH ===== */}
      <Card className={`border-2 ${isEnabled ? 'border-emerald-300' : 'border-muted'}`} data-testid="v2-master-switch">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center gap-2">
              <Lock className="w-4 h-4" />
              IA Predictive V2 — Module dormant
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge className={isEnabled ? 'bg-emerald-500 text-white' : 'bg-muted text-muted-foreground'} data-testid="v2-status-badge">
                {isEnabled ? <><Power className="w-3 h-3 mr-1" />ACTIVE</> : <><PowerOff className="w-3 h-3 mr-1" />DESACTIVE</>}
              </Badge>
              <Button size="sm" variant="ghost" onClick={fetchAll} className="h-7 w-7 p-0" data-testid="v2-refresh">
                <RefreshCw className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
          <CardDescription className="text-[11px]">
            {isEnabled
              ? "La V2 est active. Les futures analyses integrent les signaux predictifs. Kill switch disponible ci-dessous."
              : "Module preinstalle mais totalement inactif. Aucun impact sur les analyses clients tant que OFF."
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3 flex-wrap">
            {isEnabled ? (
              <Button variant="destructive" size="sm" onClick={handleDeactivate} data-testid="v2-kill-switch">
                <PowerOff className="w-4 h-4 mr-1.5" /> Kill Switch — Desactiver immediatement
              </Button>
            ) : (
              <Button size="sm" onClick={handleActivateStep1} disabled={!canActivate}
                className={canActivate ? 'bg-emerald-600 hover:bg-emerald-700 text-white' : ''}
                data-testid="v2-activate-btn">
                {canActivate ? <Unlock className="w-4 h-4 mr-1.5" /> : <Lock className="w-4 h-4 mr-1.5" />}
                {canActivate ? 'Activer la V2' : 'Activation impossible'}
              </Button>
            )}
            {!canActivate && !isEnabled && (
              <p className="text-[10px] text-muted-foreground">Verrous non satisfaits — voir ci-dessous</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* ===== TABS INTERNES ===== */}
      <div className="flex gap-1 flex-wrap" data-testid="v2-internal-tabs">
        {[
          { id: 'overview', label: 'Vue d\'ensemble', icon: Eye },
          { id: 'sandbox', label: 'Sandbox', icon: FlaskConical },
          { id: 'compare', label: 'Comparateur', icon: ArrowLeftRight },
          { id: 'config', label: 'Parametres', icon: Settings },
          { id: 'audit', label: 'Audit', icon: History },
        ].map(t => (
          <Button key={t.id} size="sm" variant={activeTab === t.id ? 'default' : 'outline'}
            className="h-8 text-xs" onClick={() => setActiveTab(t.id)}
            data-testid={`v2-tab-${t.id}`}>
            <t.icon className="w-3.5 h-3.5 mr-1" />{t.label}
          </Button>
        ))}
      </div>

      {/* ===== TAB: VUE D'ENSEMBLE ===== */}
      {activeTab === 'overview' && (
        <div className="space-y-4" data-testid="v2-overview">
          {/* Verrous */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <ShieldCheck className="w-4 h-4" /> Verrous d'activation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {status.locks.map(lock => <LockIndicator key={lock.id} lock={lock} />)}
              </div>
            </CardContent>
          </Card>

          {/* Score breakdown */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <TrendingUp className="w-4 h-4" /> Score readiness {readiness.score}/100
                <Badge className={readiness.status === 'vert' ? 'bg-emerald-500 text-white' : readiness.status === 'orange' ? 'bg-amber-500 text-white' : 'bg-red-500 text-white'}>
                  {readiness.status.toUpperCase()}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                {[
                  { label: 'Total cas', value: readiness.total_cases, icon: Database },
                  { label: 'Exploitables', value: readiness.usable_cases, icon: CheckCircle },
                  { label: 'Familles', value: readiness.unique_families, icon: Layers },
                  { label: 'Avec blocage', value: readiness.with_blocage, icon: AlertTriangle },
                ].map((s, i) => (
                  <div key={i} className="p-3 rounded-lg border text-center">
                    <s.icon className="w-4 h-4 mx-auto mb-1 text-muted-foreground" />
                    <p className="text-xl font-bold">{s.value}</p>
                    <p className="text-[10px] text-muted-foreground uppercase">{s.label}</p>
                  </div>
                ))}
              </div>
              {/* Progress bars */}
              <div className="space-y-2">
                {[
                  { label: 'Volume', value: readiness.breakdown.volume, max: 50, color: 'bg-blue-500' },
                  { label: 'Diversite', value: readiness.breakdown.diversity, max: 20, color: 'bg-purple-500' },
                  { label: 'Completude', value: readiness.breakdown.completeness, max: 15, color: 'bg-amber-500' },
                  { label: 'Qualite', value: readiness.breakdown.quality, max: 15, color: 'bg-emerald-500' },
                ].map(b => (
                  <div key={b.label} className="space-y-0.5">
                    <div className="flex justify-between text-[10px]">
                      <span className="text-muted-foreground">{b.label}</span>
                      <span className="font-medium">{b.value}/{b.max}</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                      <div className={`h-full rounded-full ${b.color}`} style={{ width: `${Math.min(b.value / b.max * 100, 100)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* History chart */}
          {history.length > 1 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4" /> Evolution du score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-40" data-testid="v2-history-chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={history} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="v2PredGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#C9A84C" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#C9A84C" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="date" tickFormatter={(d) => { const p = d.split('-'); return `${p[2]}/${p[1]}`; }} tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
                      <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px', fontSize: 12 }} />
                      <Area type="monotone" dataKey="score" stroke="#C9A84C" fill="url(#v2PredGrad)" strokeWidth={2} dot={{ r: 3, fill: '#C9A84C' }} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* ===== TAB: SANDBOX ===== */}
      {activeTab === 'sandbox' && (
        <Card data-testid="v2-sandbox">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <FlaskConical className="w-4 h-4" /> Sandbox V2 — Test interne
            </CardTitle>
            <CardDescription className="text-[11px]">Testez l'analyse V2 sur un texte libre. Zero impact client. Aucune donnee stockee.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid sm:grid-cols-4 gap-3">
              <div className="sm:col-span-3">
                <Textarea placeholder="Decrivez une situation de test..." value={sandboxSituation} onChange={e => setSandboxSituation(e.target.value)}
                  className="h-24 text-sm" data-testid="v2-sandbox-input" />
              </div>
              <div className="space-y-2">
                <Select value={sandboxType} onValueChange={setSandboxType}>
                  <SelectTrigger className="h-9 text-xs" data-testid="v2-sandbox-type"><SelectValue placeholder="Type dossier" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="accident_travail">AT</SelectItem>
                    <SelectItem value="maladie_professionnelle">MP</SelectItem>
                    <SelectItem value="assurance">Assurance</SelectItem>
                    <SelectItem value="mdph">MDPH</SelectItem>
                    <SelectItem value="autre">Autre</SelectItem>
                  </SelectContent>
                </Select>
                <Button size="sm" className="w-full" onClick={handleSandbox} disabled={sandboxLoading} data-testid="v2-sandbox-run">
                  {sandboxLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FlaskConical className="w-4 h-4 mr-1" />}
                  Analyser
                </Button>
              </div>
            </div>
            {sandboxResult && (
              <div className="space-y-3 border-t pt-3" data-testid="v2-sandbox-result">
                <div className="flex items-center gap-3">
                  <Badge className={sandboxResult.v2_result.robustness_score >= 80 ? 'bg-emerald-500 text-white' : sandboxResult.v2_result.robustness_score >= 60 ? 'bg-amber-500 text-white' : 'bg-red-500 text-white'}>
                    Robustesse : {sandboxResult.v2_result.robustness_score}/100 ({sandboxResult.v2_result.robustness_level})
                  </Badge>
                  <span className="text-xs text-muted-foreground">{sandboxResult.v2_result.alert_count} alertes</span>
                </div>
                <div className="space-y-2">
                  {sandboxResult.v2_result.alerts.map((a, i) => (
                    <div key={i} className={`p-2.5 rounded-lg border text-xs ${a.severity === 'critique' ? 'border-red-300 bg-red-50/30' : a.severity === 'haute' ? 'border-amber-300 bg-amber-50/30' : 'border-muted'}`}>
                      <div className="flex items-center gap-2 mb-0.5">
                        <Badge variant="outline" className="text-[9px]">{a.severity}</Badge>
                        <span className="font-medium">{a.label}</span>
                      </div>
                      <p className="text-muted-foreground italic">{a.advice}</p>
                    </div>
                  ))}
                </div>
                <p className="text-[10px] text-muted-foreground italic">{sandboxResult.v2_result.disclaimer}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ===== TAB: COMPARATEUR ===== */}
      {activeTab === 'compare' && (
        <Card data-testid="v2-comparator">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <ArrowLeftRight className="w-4 h-4" /> Comparateur V1 / V2
            </CardTitle>
            <CardDescription className="text-[11px]">Comparez une analyse V1 existante avec les signaux V2. Outil interne — aucun impact client.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input placeholder="ID de l'analyse (strategiia ou dossier express)" value={compareId} onChange={e => setCompareId(e.target.value)}
                className="flex-1 text-sm" data-testid="v2-compare-input" />
              <Button size="sm" onClick={handleCompare} disabled={compareLoading} data-testid="v2-compare-run">
                {compareLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Comparer'}
              </Button>
            </div>
            {compareResult && (
              <div className="space-y-3 border-t pt-3" data-testid="v2-compare-result">
                <div className="flex gap-3 flex-wrap">
                  <Badge variant="outline" className="text-xs">Source : {compareResult.source}</Badge>
                  <Badge className={compareResult.v2_result.robustness_score >= 80 ? 'bg-emerald-500 text-white' : compareResult.v2_result.robustness_score >= 60 ? 'bg-amber-500 text-white' : 'bg-red-500 text-white'}>
                    V2 Robustesse : {compareResult.v2_result.robustness_score}/100
                  </Badge>
                </div>
                <div className="grid sm:grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg border">
                    <p className="text-[10px] font-semibold text-muted-foreground uppercase mb-2">Deja couvert par V1</p>
                    {compareResult.comparison.alerts_already_in_v1.length === 0 ? (
                      <p className="text-xs text-muted-foreground">Aucun signal V2 deja present dans V1</p>
                    ) : compareResult.comparison.alerts_already_in_v1.map((a, i) => (
                      <div key={i} className="text-xs flex items-center gap-1.5 py-0.5">
                        <CheckCircle className="w-3 h-3 text-emerald-500" /> {a.label}
                      </div>
                    ))}
                  </div>
                  <div className="p-3 rounded-lg border border-amber-200 bg-amber-50/20">
                    <p className="text-[10px] font-semibold text-amber-600 uppercase mb-2">Valeur ajoutee V2 ({compareResult.comparison.v2_added_value})</p>
                    {compareResult.comparison.alerts_new_in_v2.length === 0 ? (
                      <p className="text-xs text-muted-foreground">V1 couvre deja tous les signaux V2</p>
                    ) : compareResult.comparison.alerts_new_in_v2.map((a, i) => (
                      <div key={i} className="text-xs flex items-center gap-1.5 py-0.5">
                        <AlertTriangle className="w-3 h-3 text-amber-500" /> {a.label}
                        <Badge variant="outline" className="text-[8px] ml-auto">{a.severity}</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ===== TAB: PARAMETRES ===== */}
      {activeTab === 'config' && (
        <Card data-testid="v2-config">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Settings className="w-4 h-4" /> Parametres V2
            </CardTitle>
            <CardDescription className="text-[11px]">Parametre les seuils et la sensibilite. Non critique tant que la V2 est OFF.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid sm:grid-cols-2 gap-4">
              {[
                { key: 'v2_min_cases', label: 'Minimum cas exploitables', type: 'number', current: status.config.v2_min_cases },
                { key: 'v2_min_readiness_score', label: 'Score readiness minimum', type: 'number', current: status.config.v2_min_readiness_score },
                { key: 'v2_max_alerts_per_analysis', label: 'Max alertes par analyse', type: 'number', current: status.config.v2_max_alerts_per_analysis },
                { key: 'v2_prudence_level', label: 'Niveau de prudence', type: 'select', current: status.config.v2_prudence_level, options: ['haute', 'moyenne', 'basse'] },
              ].map(param => (
                <ConfigParam key={param.key} param={param} axiosConfig={axiosConfig} onUpdate={fetchAll} />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ===== TAB: AUDIT LOG ===== */}
      {activeTab === 'audit' && (
        <Card data-testid="v2-audit">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <History className="w-4 h-4" /> Journal d'audit V2
            </CardTitle>
          </CardHeader>
          <CardContent>
            {auditLog.length === 0 ? (
              <p className="text-xs text-muted-foreground py-4 text-center">Aucun evenement V2 enregistre</p>
            ) : (
              <div className="space-y-1.5 max-h-80 overflow-y-auto">
                {auditLog.map((log, i) => (
                  <div key={i} className="flex items-start gap-3 p-2 rounded border text-xs" data-testid={`v2-audit-entry-${i}`}>
                    <Badge variant="outline" className="text-[9px] flex-shrink-0 mt-0.5">
                      {log.event_type === 'activation' ? <Power className="w-3 h-3 mr-0.5 text-emerald-500" /> :
                       log.event_type === 'deactivation' ? <PowerOff className="w-3 h-3 mr-0.5 text-red-500" /> :
                       log.event_type === 'activation_refused' ? <ShieldOff className="w-3 h-3 mr-0.5 text-red-500" /> :
                       log.event_type === 'sandbox_test' ? <FlaskConical className="w-3 h-3 mr-0.5" /> :
                       log.event_type === 'sandbox_compare' ? <ArrowLeftRight className="w-3 h-3 mr-0.5" /> :
                       <Settings className="w-3 h-3 mr-0.5" />}
                      {log.event_type}
                    </Badge>
                    <div className="flex-1 min-w-0">
                      <span className="text-muted-foreground">{log.admin_email}</span>
                      {log.details && Object.keys(log.details).length > 0 && (
                        <span className="ml-2 text-[10px] text-muted-foreground">
                          {Object.entries(log.details).slice(0, 3).map(([k, v]) => `${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`).join(' | ')}
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] text-muted-foreground flex-shrink-0">
                      {log.timestamp ? new Date(log.timestamp).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : ''}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ===== ACTIVATION DIALOGS ===== */}
      <Dialog open={showActivateStep1} onOpenChange={setShowActivateStep1}>
        <DialogContent data-testid="v2-activate-dialog-1">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><ShieldAlert className="w-5 h-5 text-amber-500" /> Activation V2 — Etape 1/3</DialogTitle>
            <DialogDescription>Vous etes sur le point d'autoriser la couche V2 predictive sur les futures analyses.</DialogDescription>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">Cette action va integrer des signaux predictifs (alertes de fragilite, score de robustesse) dans les analyses StrategiIA et Dossier Express. Les rapports clients resteront inchanges dans leur structure.</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowActivateStep1(false)}>Annuler</Button>
            <Button onClick={handleActivateStep2} className="bg-amber-500 hover:bg-amber-600 text-white">Continuer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showActivateStep2} onOpenChange={setShowActivateStep2}>
        <DialogContent data-testid="v2-activate-dialog-2">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><ShieldAlert className="w-5 h-5 text-amber-500" /> Activation V2 — Etape 2/3</DialogTitle>
            <DialogDescription>Confirmez que vous comprenez que cette activation modifie le moteur d'analyse futur, tout en restant reversible.</DialogDescription>
          </DialogHeader>
          <ul className="text-sm space-y-1.5 text-muted-foreground">
            <li className="flex items-center gap-2"><CheckCircle className="w-3.5 h-3.5 text-emerald-500" /> La V2 est reversible a tout moment (kill switch)</li>
            <li className="flex items-center gap-2"><CheckCircle className="w-3.5 h-3.5 text-emerald-500" /> Les prompts USER ne sont pas modifies</li>
            <li className="flex items-center gap-2"><CheckCircle className="w-3.5 h-3.5 text-emerald-500" /> La structure PDF reste identique</li>
            <li className="flex items-center gap-2"><AlertTriangle className="w-3.5 h-3.5 text-amber-500" /> Les signaux V2 seront visibles dans le dashboard admin</li>
          </ul>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowActivateStep2(false)}>Annuler</Button>
            <Button onClick={handleActivateStep3} className="bg-amber-500 hover:bg-amber-600 text-white">Etape finale</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showActivateStep3} onOpenChange={setShowActivateStep3}>
        <DialogContent data-testid="v2-activate-dialog-3">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><Lock className="w-5 h-5 text-red-500" /> Activation V2 — Etape 3/3</DialogTitle>
            <DialogDescription>Saisissez exactement <strong>ACTIVER V2</strong> pour confirmer l'activation.</DialogDescription>
          </DialogHeader>
          <Input value={confirmText} onChange={e => setConfirmText(e.target.value)} placeholder="Tapez : ACTIVER V2"
            className="font-mono text-center" data-testid="v2-activate-confirm-input" />
          <DialogFooter>
            <Button variant="outline" onClick={() => { setShowActivateStep3(false); setConfirmText(''); }}>Annuler</Button>
            <Button onClick={handleActivateFinal} disabled={activating || confirmText !== 'ACTIVER V2'}
              className="bg-red-600 hover:bg-red-700 text-white" data-testid="v2-activate-confirm-btn">
              {activating ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Power className="w-4 h-4 mr-1" />}
              Confirmer l'activation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// =============================================================================
// SOUS-COMPOSANT : ConfigParam
// =============================================================================

const ConfigParam = ({ param, axiosConfig, onUpdate }) => {
  const [value, setValue] = useState(param.current);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const finalValue = param.type === 'number' ? parseInt(value, 10) : value;
      await axios.put(`${API}/predictive-v2/config`, { key: param.key, value: finalValue }, axiosConfig);
      toast.success(`${param.label} mis a jour`);
      onUpdate();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erreur');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium">{param.label}</label>
      <div className="flex gap-2">
        {param.type === 'select' ? (
          <Select value={value} onValueChange={v => { setValue(v); }}>
            <SelectTrigger className="h-9 text-xs flex-1"><SelectValue /></SelectTrigger>
            <SelectContent>
              {param.options.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
            </SelectContent>
          </Select>
        ) : (
          <Input type={param.type} value={value} onChange={e => setValue(e.target.value)} className="h-9 text-xs flex-1" />
        )}
        <Button size="sm" variant="outline" onClick={handleSave} disabled={saving} className="h-9 text-xs">
          {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Sauver'}
        </Button>
      </div>
    </div>
  );
};
