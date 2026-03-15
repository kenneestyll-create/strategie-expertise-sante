import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import {
  CheckCircle, Clock, AlertTriangle, Circle, ArrowRight,
  FileText, Brain, FolderOpen, Crown, Shield, Target
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
      } catch {}
      setLoading(false);
    };
    fetchProgress();
  }, [token]);

  if (loading) return <div className="h-32 flex items-center justify-center text-muted-foreground text-sm">Chargement...</div>;
  if (!data) return null;

  const { progress_pct, steps, next_action, counts } = data;

  const pieData = [
    { name: 'Validé', value: counts.completed, color: STATUS_CONFIG.completed.color },
    { name: 'En cours', value: counts.in_progress, color: STATUS_CONFIG.in_progress.color },
    { name: 'Action requise', value: counts.action_required, color: STATUS_CONFIG.action_required.color },
    { name: 'Non commencé', value: counts.not_started, color: STATUS_CONFIG.not_started.color },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-4 mb-6" data-testid="progress-dashboard">
      {/* Header with pie chart + progress bar */}
      <Card className="overflow-hidden">
        <CardContent className="p-0">
          <div className="flex flex-col md:flex-row">
            {/* Pie chart side */}
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
                  <span className="text-xl font-bold" data-testid="progress-percentage">{progress_pct}%</span>
                </div>
              </div>
            </div>

            {/* Progress details */}
            <div className="flex-1 p-4 md:p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold">Avancement de votre dossier</h3>
                <div className="flex gap-2">
                  {pieData.map((d, i) => (
                    <span key={i} className="flex items-center gap-1 text-[10px] text-muted-foreground">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: d.color }} />{d.name} ({d.value})
                    </span>
                  ))}
                </div>
              </div>

              {/* Full progress bar */}
              <div className="h-2.5 bg-muted rounded-full overflow-hidden mb-4" data-testid="progress-bar">
                <div className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all duration-700" style={{ width: `${progress_pct}%` }} />
              </div>

              {/* Next action callout */}
              {next_action && (
                <div className={`flex items-center gap-3 p-3 rounded-lg border ${next_action.status === 'action_required' ? 'bg-orange-50 border-orange-200' : 'bg-blue-50 border-blue-200'}`} data-testid="next-action">
                  <ArrowRight className={`w-4 h-4 flex-shrink-0 ${next_action.status === 'action_required' ? 'text-orange-600' : 'text-blue-600'}`} />
                  <div>
                    <p className={`text-xs font-semibold ${next_action.status === 'action_required' ? 'text-orange-700' : 'text-blue-700'}`}>
                      Prochaine action : {next_action.label}
                    </p>
                    <p className="text-[10px] text-muted-foreground">{next_action.detail}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Steps timeline */}
      <div className="grid gap-2" data-testid="progress-steps">
        {steps.map((step, i) => {
          const config = STATUS_CONFIG[step.status] || STATUS_CONFIG.not_started;
          const StepIcon = STEP_ICONS[step.id] || Circle;
          const isLast = i === steps.length - 1;

          return (
            <div key={step.id} className="flex items-stretch gap-3" data-testid={`step-${step.id}`}>
              {/* Timeline connector */}
              <div className="flex flex-col items-center w-8 flex-shrink-0">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${config.border} ${config.bg}`}>
                  <StepIcon className={`w-3.5 h-3.5 ${config.text}`} />
                </div>
                {!isLast && <div className="w-0.5 flex-1 bg-border my-1" />}
              </div>

              {/* Step content */}
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
    </div>
  );
};
