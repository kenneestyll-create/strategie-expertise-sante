import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ClipboardList } from 'lucide-react';

const CRITERIA_LABELS = {
  fidelite_documentaire: 'Fidélité aux pièces',
  pertinence_procedurale: 'Pertinence procédurale',
  respect_perimetre: 'Respect du périmètre',
  detection_qualite: 'Détection des documents illisibles',
  clarte_rapport: 'Clarté et utilité du rapport',
  experience_parcours: 'Fluidité du parcours',
};
const COMMENT_LABELS = {
  points_forts: 'Points forts observés',
  mises_en_defaut: 'Mises en défaut, erreurs ou approximations',
  reserves: 'Risques ou réserves',
};
const BENEFIT_LABELS = {
  gain_temps: 'Gain de temps',
  comprehension_initiale: 'Compréhension initiale du dossier',
  pieces_manquantes: 'Repérage de pièces manquantes',
  chronologie: 'Chronologie',
  incoherences: "Identification d'incohérences",
  tracabilite_sources: 'Traçabilité des sources',
  hierarchisation: 'Hiérarchisation des points à vérifier',
};

export const ExpertFeedbackDialog = ({ feedback, open, onOpenChange }) => {
  if (!feedback) return null;
  const ratings = feedback.ratings || {};
  const values = Object.values(ratings);
  const avg = values.length ? (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1) : null;
  const comments = feedback.comments || {};

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto" data-testid="ea-feedback-dialog">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-base">
            <ClipboardList className="w-4 h-4 text-[#C9A84C]" />
            Retour de {feedback.evaluator_name}
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-5 text-sm">
          <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
            <span className="text-xs text-muted-foreground">
              Soumis le {new Date(feedback.updated_at).toLocaleDateString('fr-FR')} à {new Date(feedback.updated_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
            </span>
            {avg && (
              <span className="font-semibold text-[#C9A84C]" data-testid="ea-feedback-average">
                Moyenne : {avg} / 5 <span className="text-xs text-muted-foreground font-normal">({values.length} critère{values.length > 1 ? 's' : ''})</span>
              </span>
            )}
          </div>
          <div className="space-y-2">
            {Object.entries(CRITERIA_LABELS).map(([key, label]) => (
              <div key={key} className="flex items-center justify-between gap-3 py-1 border-b border-border/50">
                <span className="text-xs">{label}</span>
                {ratings[key] ? (
                  <span className="flex gap-0.5" data-testid={`ea-feedback-rating-${key}`}>
                    {[1, 2, 3, 4, 5].map((n) => (
                      <span key={n} className={`w-5 h-5 rounded text-[10px] font-bold flex items-center justify-center ${n <= ratings[key] ? 'bg-[#C9A84C] text-white' : 'bg-muted text-muted-foreground'}`}>{n}</span>
                    ))}
                  </span>
                ) : (
                  <span className="text-[10px] text-muted-foreground italic">Non noté</span>
                )}
              </div>
            ))}
          </div>
          <div className="p-3 rounded-lg bg-muted/40">
            <p className="text-xs font-semibold mb-1.5">Bénéfices professionnels constatés</p>
            {(feedback.benefits_observed || []).length ? (
              <div className="flex flex-wrap gap-1.5" data-testid="ea-feedback-benefits">
                {feedback.benefits_observed.map((b) => (
                  <span key={b} className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-[#C9A84C]/15 text-[#8a6d2f] border border-[#C9A84C]/30">✓ {BENEFIT_LABELS[b] || b}</span>
                ))}
              </div>
            ) : (
              <p className="text-[11px] text-muted-foreground italic" data-testid="ea-feedback-no-benefits">Aucun bénéfice constaté (ou question non renseignée)</p>
            )}
          </div>
          {Object.entries(COMMENT_LABELS).map(([key, label]) => comments[key] ? (
            <div key={key}>
              <p className="text-xs font-semibold mb-1">{label}</p>
              <p className="text-xs text-muted-foreground whitespace-pre-wrap p-2.5 rounded-md bg-muted/40" data-testid={`ea-feedback-comment-${key}`}>{comments[key]}</p>
            </div>
          ) : null)}
        </div>
      </DialogContent>
    </Dialog>
  );
};
