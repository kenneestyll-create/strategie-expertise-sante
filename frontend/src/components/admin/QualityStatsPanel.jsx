import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { ShieldCheck, FileSearch, RefreshCw, Quote } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Metric = ({ value, label, testid }) => (
  <div className="rounded-xl border border-border bg-card p-4 text-center" data-testid={testid}>
    <div className="text-2xl font-semibold text-foreground">{value}</div>
    <div className="text-xs text-muted-foreground mt-1">{label}</div>
  </div>
);

export const QualityStatsPanel = ({ token }) => {
  const [stats, setStats] = useState(null);
  const [product, setProduct] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const h = { headers: { Authorization: `Bearer ${token}` } };
    fetch(`${API}/admin/quality-stats`, h).then(r => r.json()).then(setStats).catch(e => setError(String(e)));
    fetch(`${API}/admin/product-stats`, h).then(r => r.json()).then(setProduct).catch(() => {});
  }, [token]);

  if (error) return <p className="text-sm text-destructive" data-testid="quality-stats-error">Erreur de chargement : {error}</p>;
  if (!stats) return <p className="text-sm text-muted-foreground">Chargement…</p>;

  const ex = stats.extractions || {};
  const ch = stats.choices || {};
  const ci = stats.citations || {};

  return (
    <div className="space-y-6" data-testid="quality-stats-panel">
      <p className="text-xs text-muted-foreground">
        Statistiques techniques anonymisées de la chaîne documentaire (Lot 1) — aucune donnée personnelle ni médicale.
      </p>

      <div>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-3"><FileSearch className="w-4 h-4 text-accent" /> Extractions analysées</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <Metric value={ex.total ?? 0} label="dossiers analysés" testid="qs-total" />
          <Metric value={ex.avg_pages ?? '—'} label="pages moyennes" testid="qs-avg-pages" />
          <Metric value={ex.avg_confidence_score != null ? `${ex.avg_confidence_score}` : '—'} label="score qualité moyen" testid="qs-avg-score" />
          <Metric value={ex.degraded_rate_pct != null ? `${ex.degraded_rate_pct} %` : '—'} label="dossiers avec pages dégradées" testid="qs-degraded-rate" />
          <Metric value={ex.unusable_pages_rate_pct != null ? `${ex.unusable_pages_rate_pct} %` : '—'} label="pages illisibles" testid="qs-unusable-rate" />
          <Metric value={ex.partial_pages_rate_pct != null ? `${ex.partial_pages_rate_pct} %` : '—'} label="pages partielles" testid="qs-partial-rate" />
        </div>
        {ex.levels && Object.keys(ex.levels).length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3" data-testid="qs-levels">
            {Object.entries(ex.levels).map(([lvl, n]) => (
              <span key={lvl} className="text-xs px-2.5 py-1 rounded-full bg-secondary border border-border">{lvl} : {n}</span>
            ))}
          </div>
        )}
      </div>

      <div>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-3"><RefreshCw className="w-4 h-4 text-accent" /> Comportement face aux alertes qualité</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Metric value={ch.auto_ok ?? 0} label="dossiers sans alerte" testid="qs-choice-auto" />
          <Metric value={ch.continue_degraded ?? 0} label="ont continué malgré l'alerte" testid="qs-choice-continue" />
          <Metric value={ch.replaced_after_warning ?? 0} label="ont remplacé leurs pages" testid="qs-choice-replaced" />
          <Metric value={ch.not_available ?? 0} label="antérieurs au contrôle qualité" testid="qs-choice-na" />
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-3"><Quote className="w-4 h-4 text-accent" /> Traçabilité des citations</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Metric value={ci.dossiers_with_citations ?? 0} label="rapports avec citations" testid="qs-cit-dossiers" />
          <Metric value={ci.total ?? 0} label="citations contrôlées" testid="qs-cit-total" />
          <Metric value={ci.verified ?? 0} label="citations vérifiées" testid="qs-cit-verified" />
          <Metric value={ci.verified_rate_pct != null ? `${ci.verified_rate_pct} %` : '—'} label="taux de vérification" testid="qs-cit-rate" />
        </div>
      </div>

      {product && (
        <div data-testid="product-stats-section">
          <h3 className="text-sm font-semibold flex items-center gap-2 mb-3"><FileSearch className="w-4 h-4 text-accent" /> Pilotage produit &amp; business (phase d'observation)</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            <Metric value={product.produit?.visites_dossier_express ?? '—'} label="visites Dossier Express" testid="ps-visits" />
            <Metric value={product.produit?.paiements ?? 0} label="paiements" testid="ps-paid" />
            <Metric value={product.produit?.conversion_visite_achat_pct != null ? `${product.produit.conversion_visite_achat_pct} %` : '—'} label="conversion visite → achat" testid="ps-conversion" />
            <Metric value={product.produit?.abandons_apres_paiement ?? 0} label="abandons après paiement" testid="ps-abandons" />
            <Metric value={product.produit?.dossiers_completes ?? 0} label="rapports livrés" testid="ps-completed" />
            <Metric value={product.produit?.delai_moyen_analyse_s != null ? `${Math.round(product.produit.delai_moyen_analyse_s / 60)} min` : '—'} label="délai moyen d'analyse" testid="ps-delay" />
            <Metric value={product.business?.cout_ia_estime_par_dossier_eur != null ? `~${product.business.cout_ia_estime_par_dossier_eur} €` : '—'} label="coût IA estimé / dossier" testid="ps-cost" />
          </div>
          <p className="text-[11px] text-muted-foreground mt-2">{product.business?.note}</p>
        </div>
      )}

      <Card className="border-dashed">
        <CardContent className="p-4 flex items-start gap-3">
          <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
          <p className="text-xs text-muted-foreground">
            Ces indicateurs serviront de référence dès les premiers dossiers clients réels (phase 4 de l'ordre de mission).
            Le calibrage des seuils du score qualité (v1.1) est prévu après 50-100 dossiers réels.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
