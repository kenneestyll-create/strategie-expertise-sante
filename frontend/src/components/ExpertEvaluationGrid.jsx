import { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { toast } from 'sonner';
import { ClipboardList, ChevronDown, Loader2, CheckCircle2 } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CRITERIA = [
  { key: 'fidelite_documentaire', label: 'Fidélité aux pièces', hint: "Les citations du rapport correspondent-elles exactement aux documents fournis ? Aucun élément inventé ?" },
  { key: 'pertinence_procedurale', label: 'Pertinence procédurale', hint: "Les voies de recours identifiées sont-elles justes (CRA, contestation du taux, CRRMP, seuil des 25 %) ?" },
  { key: 'respect_perimetre', label: 'Respect du périmètre', hint: "L'outil s'abstient-il de tout jugement clinique ? Reste-t-il sur l'organisation documentaire et la procédure ?" },
  { key: 'detection_qualite', label: 'Détection des documents illisibles', hint: "Le document volontairement dégradé (pièce n°4) a-t-il été signalé avant l'analyse ?" },
  { key: 'clarte_rapport', label: 'Clarté et utilité du rapport', hint: "Le rapport est-il structuré, lisible et réellement utile pour la personne concernée ?" },
  { key: 'experience_parcours', label: 'Fluidité du parcours', hint: "Dépôt des documents, consignes, réception du rapport : le parcours est-il simple de bout en bout ?" },
];

const COMMENTS = [
  { key: 'points_forts', label: 'Points forts observés' },
  { key: 'mises_en_defaut', label: "Mises en défaut, erreurs ou approximations relevées" },
  { key: 'reserves', label: 'Risques ou réserves (déontologiques, juridiques, cliniques)' },
];

const BENEFITS = [
  { key: 'gain_temps', label: 'Gain de temps' },
  { key: 'comprehension_initiale', label: 'Meilleure compréhension initiale du dossier' },
  { key: 'pieces_manquantes', label: 'Repérage de pièces manquantes' },
  { key: 'chronologie', label: 'Chronologie' },
  { key: 'incoherences', label: "Identification d'incohérences" },
  { key: 'tracabilite_sources', label: 'Traçabilité des sources' },
  { key: 'hierarchisation', label: 'Hiérarchisation des points à vérifier' },
];

export const ExpertEvaluationGrid = ({ token, email }) => {
  const [open, setOpen] = useState(false);
  const [ratings, setRatings] = useState({});
  const [comments, setComments] = useState({});
  const [benefits, setBenefits] = useState([]);
  const [sending, setSending] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    axios.get(`${API}/expert-access/feedback`, { params: { token, email } })
      .then((res) => {
        if (res.data.feedback) {
          setRatings(res.data.feedback.ratings || {});
          setComments(res.data.feedback.comments || {});
          setBenefits(res.data.feedback.benefits_observed || []);
          setSaved(true);
        }
      })
      .catch(() => {});
  }, [token, email]);

  const toggleBenefit = (key) => setBenefits((b) => b.includes(key) ? b.filter((x) => x !== key) : [...b, key]);

  const submit = async () => {
    setSending(true);
    try {
      await axios.post(`${API}/expert-access/feedback`, { token, email, ratings, comments, benefits });
      setSaved(true);
      toast.success('Votre évaluation a bien été enregistrée. Merci.');
    } catch (err) {
      toast.error(err.response?.data?.detail || "Envoi impossible");
    } finally {
      setSending(false);
    }
  };

  const hasContent = Object.keys(ratings).length > 0 || benefits.length > 0 || Object.values(comments).some((v) => v && v.trim());

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <section className="mb-10 rounded-xl border border-white/10 bg-white/[0.02]" data-testid="eval-grid-section">
        <CollapsibleTrigger asChild>
          <button className="w-full flex items-center justify-between p-5 text-left" data-testid="eval-grid-toggle">
            <span className="flex items-center gap-2.5">
              <ClipboardList className="w-4 h-4 text-[#C9A84C]" />
              <span className="text-sm font-semibold text-[#f5f0e8]">Grille d'évaluation — votre retour d'expert</span>
              {saved && <CheckCircle2 className="w-4 h-4 text-emerald-400" data-testid="eval-grid-saved-icon" />}
            </span>
            <ChevronDown className={`w-4 h-4 text-[#f5f0e8]/40 transition-transform ${open ? 'rotate-180' : ''}`} />
          </button>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="px-5 pb-6 space-y-6">
            <p className="text-xs text-[#f5f0e8]/50 leading-relaxed">
              À remplir après votre test, en une seule fois ou en plusieurs — vos réponses sont enregistrées et modifiables.
              Notez chaque critère de 1 (défaillant) à 5 (excellent). Vos critiques argumentées sont le livrable le plus précieux.
            </p>
            <div className="space-y-4">
              {CRITERIA.map((c) => (
                <div key={c.key} className="p-4 rounded-lg border border-white/8 bg-white/[0.02]">
                  <div className="flex items-start justify-between gap-4 flex-wrap">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-[#f5f0e8]">{c.label}</p>
                      <p className="text-xs text-[#f5f0e8]/45 mt-0.5 leading-relaxed">{c.hint}</p>
                    </div>
                    <div className="flex gap-1.5 shrink-0">
                      {[1, 2, 3, 4, 5].map((n) => (
                        <button key={n} type="button" onClick={() => setRatings((r) => ({ ...r, [c.key]: n }))}
                          data-testid={`eval-grid-rating-${c.key}-${n}`}
                          className={`w-8 h-8 rounded-md text-xs font-semibold border transition-colors ${
                            ratings[c.key] === n
                              ? 'bg-[#C9A84C] border-[#C9A84C] text-[#0a0a08]'
                              : 'border-white/15 text-[#f5f0e8]/60 hover:border-[#C9A84C]/50'
                          }`}>
                          {n}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-4 rounded-lg border border-[#C9A84C]/25 bg-[#C9A84C]/5" data-testid="eval-grid-benefits">
              <p className="text-sm font-medium text-[#f5f0e8] mb-1">Bénéfices professionnels réellement constatés</p>
              <p className="text-xs text-[#f5f0e8]/50 leading-relaxed mb-3">
                « Parmi les bénéfices potentiels suivants, lesquels avez-vous réellement constatés pendant votre test :
                gain de temps, meilleure compréhension initiale du dossier, repérage de pièces manquantes, chronologie,
                identification d'incohérences, traçabilité des sources, hiérarchisation des points à vérifier ? »
              </p>
              <div className="flex flex-wrap gap-2">
                {BENEFITS.map((b) => (
                  <button key={b.key} type="button" onClick={() => toggleBenefit(b.key)}
                    data-testid={`eval-grid-benefit-${b.key}`}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                      benefits.includes(b.key)
                        ? 'bg-[#C9A84C] border-[#C9A84C] text-[#0a0a08]'
                        : 'border-white/15 text-[#f5f0e8]/60 hover:border-[#C9A84C]/50'
                    }`}>
                    {benefits.includes(b.key) ? '✓ ' : ''}{b.label}
                  </button>
                ))}
              </div>
              <p className="text-[10px] text-[#f5f0e8]/35 mt-2">Ne cochez que ce que vous avez réellement constaté — « aucun » est un retour tout aussi précieux.</p>
            </div>
            <div className="space-y-4">
              {COMMENTS.map((c) => (
                <div key={c.key}>
                  <p className="text-xs font-medium text-[#f5f0e8]/70 mb-1.5">{c.label}</p>
                  <Textarea value={comments[c.key] || ''} onChange={(e) => setComments((v) => ({ ...v, [c.key]: e.target.value }))}
                    rows={3} data-testid={`eval-grid-comment-${c.key}`}
                    className="bg-white/5 border-white/10 text-[#f5f0e8] text-sm" placeholder="Votre observation…" />
                </div>
              ))}
            </div>
            <Button onClick={submit} disabled={sending || !hasContent}
              className="bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-medium" data-testid="eval-grid-submit">
              {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : saved ? 'Mettre à jour mon évaluation' : 'Enregistrer mon évaluation'}
            </Button>
          </div>
        </CollapsibleContent>
      </section>
    </Collapsible>
  );
};
