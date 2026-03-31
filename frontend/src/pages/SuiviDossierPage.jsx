import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  CheckCircle, Clock, Shield, FileText, Search,
  Download, Loader2, Mail, ArrowRight
} from 'lucide-react';
import axios from 'axios';
import { SEO } from '@/components/SEO';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STEP_ICONS = {
  received: CheckCircle,
  préparation: FileText,
  reading: Search,
  analysis: Shield,
  report: FileText,
  delivery: Mail,
  available: Download,
};

export const SuiviDossierPage = () => {
  const [searchParams] = useSearchParams();
  const [dossierId, setDossierId] = useState(searchParams.get('id') || '');
  const [token] = useState(searchParams.get('token') || '');
  const [tracking, setTracking] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchTracking = useCallback(async (id) => {
    if (!id || id.length < 10) return;
    setLoading(true);
    setError('');
    try {
      const params = token ? `?token=${token}` : '';
      const res = await axios.get(`${API}/dossier-express/suivi/${id}${params}`);
      setTracking(res.data);
    } catch {
      setError('Dossier introuvable. Vérifiez votre identifiant.');
      setTracking(null);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    const id = searchParams.get('id');
    if (id) {
      setDossierId(id);
      fetchTracking(id);
    }
  }, [searchParams, fetchTracking]);

  // Auto-refresh every 15s while processing
  useEffect(() => {
    if (!tracking || tracking.status === 'completed') return;
    const interval = setInterval(() => fetchTracking(dossierId), 15000);
    return () => clearInterval(interval);
  }, [tracking, dossierId, fetchTracking]);

  return (
    <main className="page-transition pt-20 pb-16">
      <SEO title="Suivi de votre dossier" description="Suivez l'avancement de votre analyse en temps réel" />
      <section className="max-w-2xl mx-auto px-4 sm:px-6">

        {/* Header */}
        <div className="text-center mb-10">
          <div className="w-14 h-14 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-5">
            <Shield className="w-7 h-7 text-accent" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight mb-2" style={{ fontFamily: "'Playfair Display', serif" }}>
            Suivi de votre dossier
          </h1>
          <p className="text-muted-foreground text-sm max-w-md mx-auto">
            Consultez l'avancement de votre analyse en toute transparence
          </p>
        </div>

        {/* Search bar (only if no tracking loaded) */}
        {!tracking && (
          <Card className="mb-8 border-border/60" data-testid="suivi-search-card">
            <CardContent className="p-6">
              <label className="text-sm font-medium mb-2 block">Identifiant de votre dossier</label>
              <div className="flex gap-2">
                <Input
                  value={dossierId}
                  onChange={(e) => setDossierId(e.target.value)}
                  placeholder="Entrez votre identifiant de dossier"
                  className="flex-1"
                  data-testid="suivi-input"
                />
                <Button
                  onClick={() => fetchTracking(dossierId)}
                  disabled={loading || dossierId.length < 10}
                  className="gap-2 rounded-lg"
                  data-testid="suivi-search-btn"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                  Rechercher
                </Button>
              </div>
              {error && <p className="text-red-500 text-sm mt-3" data-testid="suivi-error">{error}</p>}
            </CardContent>
          </Card>
        )}

        {/* Tracking Result */}
        {tracking && (
          <div className="space-y-6" data-testid="suivi-result">

            {/* Client greeting */}
            <Card className="border-accent/20 bg-accent/5">
              <CardContent className="p-5">
                <div className="flex items-start gap-3">
                  <Shield className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold mb-1">
                      {tracking.name ? `Bonjour ${tracking.name}` : 'Bonjour'}
                    </p>
                    <p className="text-sm text-muted-foreground leading-relaxed" data-testid="suivi-message">
                      {tracking.message}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Timeline */}
            <Card className="border-border/60" data-testid="suivi-timeline-card">
              <CardContent className="p-6">
                <h3 className="text-sm font-semibold mb-5 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-accent" />
                  Avancement de votre dossier
                </h3>
                <div className="space-y-0">
                  {tracking.steps.map((step, i) => {
                    const Icon = STEP_ICONS[step.key] || FileText;
                    const isCompleted = step.status === 'completed';
                    const isActive = step.status === 'active';
                    const isLast = i === tracking.steps.length - 1;

                    return (
                      <div key={step.key} className="flex gap-4" data-testid={`suivi-step-${step.key}`}>
                        {/* Vertical line + dot */}
                        <div className="flex flex-col items-center">
                          <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 border-2 transition-all ${
                            isCompleted ? 'bg-green-50 border-green-400' :
                            isActive ? 'bg-accent/10 border-accent ring-4 ring-accent/10' :
                            'bg-muted/40 border-muted-foreground/20'
                          }`}>
                            {isCompleted ? (
                              <CheckCircle className="w-4 h-4 text-green-600" />
                            ) : isActive ? (
                              <Loader2 className="w-4 h-4 text-accent animate-spin" />
                            ) : (
                              <Icon className="w-4 h-4 text-muted-foreground/40" />
                            )}
                          </div>
                          {!isLast && (
                            <div className={`w-0.5 h-8 my-1 ${isCompleted ? 'bg-green-300' : 'bg-muted-foreground/15'}`} />
                          )}
                        </div>

                        {/* Label */}
                        <div className={`pt-1.5 pb-3 ${isActive ? '' : ''}`}>
                          <p className={`text-sm font-medium ${
                            isCompleted ? 'text-green-700' :
                            isActive ? 'text-foreground' :
                            'text-muted-foreground/50'
                          }`}>
                            {step.label}
                          </p>
                          {isActive && tracking.status === 'incident' && (
                            <p className="text-xs text-amber-600 mt-1">
                              Notre équipe veille à la qualité de votre rapport
                            </p>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Download button if completed */}
            {tracking.status === 'completed' && tracking.download_url && (
              <Card className="border-green-200/60 bg-green-50/30" data-testid="suivi-download-card">
                <CardContent className="p-5 text-center">
                  <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Votre rapport est disponible</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Vous pouvez telecharger votre rapport personnalisé en toute sécurité.
                  </p>
                  <a href={tracking.download_url} target="_blank" rel="noopener noreferrer">
                    <Button className="gap-2 rounded-full px-8" data-testid="suivi-download-btn">
                      <Download className="w-4 h-4" />
                      Telecharger mon rapport PDF
                    </Button>
                  </a>
                </CardContent>
              </Card>
            )}

            {/* Incident reassurance */}
            {tracking.status === 'incident' && (
              <Card className="border-amber-200/40 bg-amber-50/20" data-testid="suivi-incident-card">
                <CardContent className="p-5">
                  <div className="flex items-start gap-3">
                    <Shield className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-semibold mb-1">Aucune action requise de votre part</h4>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        Votre paiement est confirme et vos documents sont conserves en toute confidentialité.
                        Vous recevrez votre rapport par email des qu'il sera finalise.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Footer actions */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
              <Link to="/contact">
                <Button variant="outline" className="rounded-full px-6 gap-2 text-sm w-full sm:w-auto">
                  <Mail className="w-4 h-4" />
                  Une question ?
                </Button>
              </Link>
              <Link to="/">
                <Button variant="ghost" className="rounded-full px-6 text-sm w-full sm:w-auto gap-2">
                  Retour a l'accueil <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </Link>
            </div>
          </div>
        )}
      </section>
    </main>
  );
};
