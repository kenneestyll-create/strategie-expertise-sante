import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import {
  CheckCircle, Clock, AlertTriangle, Circle, ArrowRight, Upload,
  FileText, Brain, FolderOpen, Crown, Shield, Target, AlertCircle
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STATUS_CONFIG = {
  completed: { color: '#16a34a', bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-200', icon: CheckCircle, label: 'Validé' },
  in_progress: { color: '#2563eb', bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200', icon: Clock, label: 'En cours' },
  action_required: { color: '#ea580c', bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-200', icon: AlertTriangle, label: 'Action requise' },
  not_started: { color: '#9ca3af', bg: 'bg-gray-100', text: 'text-gray-500', border: 'border-gray-200', icon: Circle, label: 'Non commencé' },
};

const STEP_ICONS = {
  inscription: Shield,
  documents: FileText,
  strategiia: Brain,
  dossier_express: FolderOpen,
  analyse_premium: Crown,
  finalisation: Target,
};

export const ProgressDashboard = ({ token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const res = await axios.get(`${API}/client/progress`, { headers: { Authorization: `Bearer ${token}` } });
        setData(res.data);
      } catch (e) { /* silent */ }
      setLoading(false);
    };
    fetchProgress();
  }, [token]);

  if (loading) return <div className="h-32 flex items-center justify-center text-muted-foreground text-sm">Chargement...</div>;
  if (!data) return null;

  const { progress_pct, steps, next_actions, counts, document_status, missing_documents, completeness_pct } = data;

  const pieData = [
    { name: 'Validé', value: counts.completed, color: STATUS_CONFIG.completed.color },
    { name: 'En cours', value: counts.in_progress, color: STATUS_CONFIG.in_progress.color },
    { name: 'Action requise', value: counts.action_required, color: STATUS_CONFIG.action_required.color },
    { name: 'Non commencé', value: counts.not_started, color: STATUS_CONFIG.not_started.color },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-4 mb-6" data-testid="progress-dashboard">
      {/* Header: Progress + Pie chart */}
      <Card className="overflow-hidden">
        <CardContent className="p-0">
          <div className="flex flex-col md:flex-row">
            <div className="flex items-center justify-center p-4 md:p-6 md:border-r border-border bg-muted/20 md:w-48">
              <div className="relative w-28 h-28" data-testid="progress-pie-chart">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} dataKey="value" cx="50%" cy="50%" innerRadius={32} outerRadius={48} paddingAngle={3} strokeWidth={0}>
                      {pieData.map((d, i) => <Cell key={i} fill={d.color} />)}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-bold" data-testid="progress-percentage">{progress_pct}%</span>
                  <span className="text-[9px] text-muted-foreground">avancement</span>
                </div>
              </div>
            </div>

            <div className="flex-1 p-4 md:p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold">Avancement de votre dossier</h3>
                <div className="flex gap-2 flex-wrap">
                  {pieData.map((d, i) => (
                    <span key={i} className="flex items-center gap-1 text-[10px] text-muted-foreground">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: d.color }} />{d.name} ({d.value})
                    </span>
                  ))}
                </div>
              </div>

              <div className="h-2.5 bg-muted rounded-full overflow-hidden mb-4" data-testid="progress-bar">
                <div className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all duration-700" style={{ width: `${progress_pct}%` }} />
              </div>

              {/* Completeness indicator */}
              {completeness_pct !== undefined && (
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xs text-muted-foreground">Complétude documentaire</span>
                  <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${completeness_pct >= 80 ? 'bg-green-500' : completeness_pct >= 50 ? 'bg-amber-500' : 'bg-red-400'}`}
                      style={{ width: `${completeness_pct}%` }}
                    />
                  </div>
                  <span className={`text-xs font-semibold ${completeness_pct >= 80 ? 'text-green-600' : completeness_pct >= 50 ? 'text-amber-600' : 'text-red-500'}`} data-testid="completeness-pct">
                    {completeness_pct}%
                  </span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Document status cards */}
      {document_status && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2" data-testid="document-status-cards">
          <Card><CardContent className="p-3 text-center">
            <p className="text-lg font-bold" data-testid="doc-total">{document_status.total}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Documents</p>
          </CardContent></Card>
          <Card><CardContent className="p-3 text-center">
            <p className="text-lg font-bold text-green-600" data-testid="doc-valide">{document_status.valide}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Validés</p>
          </CardContent></Card>
          <Card><CardContent className="p-3 text-center">
            <p className="text-lg font-bold text-amber-600" data-testid="doc-en-attente">{document_status.en_attente}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">En attente</p>
          </CardContent></Card>
          <Card><CardContent className="p-3 text-center">
            <p className="text-lg font-bold text-red-500" data-testid="doc-illisible">{document_status.illisible}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Illisibles</p>
          </CardContent></Card>
        </div>
      )}

      {/* Missing essential documents */}
      {missing_documents && missing_documents.length > 0 && (
        <Card className="border-amber-200 bg-amber-50/50" data-testid="missing-documents-section">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <AlertCircle className="w-4 h-4 text-amber-600" />
              <h4 className="text-sm font-semibold text-amber-800">Documents essentiels manquants</h4>
              <Badge variant="outline" className="text-[9px] bg-amber-100 text-amber-700 border-amber-300">{missing_documents.length} manquant{missing_documents.length > 1 ? 's' : ''}</Badge>
            </div>
            <div className="space-y-2">
              {missing_documents.map((doc, i) => (
                <div key={i} className="flex items-center justify-between gap-2 bg-white/70 rounded-lg px-3 py-2 border border-amber-100">
                  <div className="flex items-center gap-2 min-w-0">
                    <FileText className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                    <span className="text-xs text-foreground truncate">{doc.label}</span>
                    <Badge variant="outline" className="text-[8px] px-1 flex-shrink-0">{doc.category}</Badge>
                  </div>
                  <Link to="/espace-client?tab=documents">
                    <Button size="sm" variant="ghost" className="h-7 px-2 text-[10px] text-amber-700 hover:text-amber-900 hover:bg-amber-100 gap-1 flex-shrink-0" data-testid={`upload-missing-${i}`}>
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

      {/* Next actions - actionable */}
      {next_actions && next_actions.length > 0 && (
        <Card data-testid="next-actions-section">
          <CardContent className="p-4">
            <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <ArrowRight className="w-4 h-4 text-accent" />
              Prochaines actions
            </h4>
            <div className="space-y-2">
              {next_actions.map((action, i) => {
                const isUrgent = action.status === 'action_required';
                return (
                  <div
                    key={i}
                    className={`flex items-center justify-between gap-3 p-3 rounded-lg border ${isUrgent ? 'bg-orange-50 border-orange-200' : 'bg-blue-50 border-blue-200'}`}
                    data-testid={`next-action-${i}`}
                  >
                    <div className="min-w-0">
                      <p className={`text-xs font-semibold ${isUrgent ? 'text-orange-700' : 'text-blue-700'}`}>
                        {i + 1}. {action.label}
                      </p>
                      <p className="text-[10px] text-muted-foreground truncate">{action.detail}</p>
                    </div>
                    {action.cta && action.cta_link && (
                      <Link to={action.cta_link}>
                        <Button size="sm" className={`h-7 px-3 text-[10px] rounded-full whitespace-nowrap gap-1 ${isUrgent ? 'bg-orange-600 hover:bg-orange-700' : 'bg-blue-600 hover:bg-blue-700'}`} data-testid={`action-cta-${i}`}>
                          {action.cta}
                          <ArrowRight className="w-3 h-3" />
                        </Button>
                      </Link>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Steps timeline */}
      <Card>
        <CardContent className="p-4">
          <h4 className="text-sm font-semibold mb-3">Étapes de votre parcours</h4>
          <div className="grid gap-2" data-testid="progress-steps">
            {steps.map((step, i) => {
              const config = STATUS_CONFIG[step.status] || STATUS_CONFIG.not_started;
              const StepIcon = STEP_ICONS[step.id] || Circle;
              const isLast = i === steps.length - 1;

              return (
                <div key={step.id} className="flex items-stretch gap-3" data-testid={`step-${step.id}`}>
                  <div className="flex flex-col items-center w-8 flex-shrink-0">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${config.border} ${config.bg}`}>
                      <StepIcon className={`w-3.5 h-3.5 ${config.text}`} />
                    </div>
                    {!isLast && <div className="w-0.5 flex-1 bg-border my-1" />}
                  </div>
                  <div className={`flex-1 pb-3 ${isLast ? '' : 'border-b border-transparent'}`}>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{step.label}</span>
                      <Badge variant="outline" className={`text-[9px] px-1.5 ${config.bg} ${config.text} border-0`}>{config.label}</Badge>
                      {step.count !== undefined && step.required && (
                        <Badge variant="outline" className="text-[9px] px-1.5">{step.count}/{step.required}</Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">{step.detail}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
