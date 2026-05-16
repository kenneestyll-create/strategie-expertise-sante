import { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, RefreshCw, Download, Lock, Save, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import PremiumAnalysisRenderer from '@/components/admin/_PARsAdapter';

const API = process.env.REACT_APP_BACKEND_URL;

const SECTIONS = [
  { key: 'synthese_strategique', label: '1. Synthèse stratégique' },
  { key: 'diagnostic_juridique', label: '2. Diagnostic juridique' },
  { key: 'plan_action_chronologique', label: "3. Plan d'action chronologique" },
  { key: 'lettres_types', label: '4. Lettres-types' },
  { key: 'arguments_contestation', label: '5. Arguments de contestation' },
  { key: 'pieces_a_reclamer', label: '6. Pièces à réclamer' },
  { key: 'calendrier_suivi', label: '7. Calendrier de suivi' },
];

export default function KitProfessionnelTab({ dossierId, token }) {
  const [loading, setLoading] = useState(true);
  const [kit, setKit] = useState(null);
  const [exists, setExists] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [notes, setNotes] = useState('');
  const [savingNotes, setSavingNotes] = useState(false);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchKit = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/api/admin/dossier-express/${dossierId}/kit-professionnel`, { headers });
      setExists(!!res.data.exists);
      if (res.data.exists) {
        setKit(res.data);
        setNotes(res.data.admin_notes || '');
      } else {
        setKit(null);
      }
    } catch (e) {
      toast.error('Erreur chargement kit');
    } finally {
      setLoading(false);
    }
  }, [dossierId, token]);

  useEffect(() => { fetchKit(); }, [fetchKit]);

  const regenerate = async () => {
    setRegenerating(true);
    toast.info('Génération du kit en cours... (60-90 sec)');
    try {
      await axios.post(`${API}/api/admin/dossier-express/${dossierId}/kit-professionnel/regenerate`, {}, { headers });
      toast.success('Kit généré avec succès');
      await fetchKit();
    } catch (e) {
      toast.error('Erreur génération : ' + (e.response?.data?.detail || e.message).slice(0, 100));
    } finally {
      setRegenerating(false);
    }
  };

  const saveNotes = async () => {
    setSavingNotes(true);
    try {
      await axios.post(`${API}/api/admin/dossier-express/${dossierId}/kit-professionnel/notes`, { notes }, { headers });
      toast.success('Notes sauvegardées');
    } catch (e) {
      toast.error('Erreur sauvegarde notes');
    } finally {
      setSavingNotes(false);
    }
  };

  const downloadPDF = async () => {
    try {
      const res = await axios.get(`${API}/api/admin/dossier-express/${dossierId}/kit-professionnel/pdf`, {
        headers, responseType: 'blob'
      });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Kit_Pro_${dossierId.slice(0, 8)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      toast.error('Erreur téléchargement PDF');
    }
  };

  if (loading) {
    return <div className="flex items-center gap-2 p-6 text-sm text-muted-foreground"><Loader2 className="w-4 h-4 animate-spin" /> Chargement du kit...</div>;
  }

  if (!exists) {
    return (
      <div className="space-y-4 p-4" data-testid="kit-pro-empty">
        <div className="flex items-start gap-3 p-4 rounded-lg border border-amber-200 bg-amber-50">
          <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-amber-900">Kit Professionnel pas encore généré</p>
            <p className="text-xs text-amber-700 mt-1">
              Si le dossier vient d'être finalisé, le kit est en cours de génération en arrière-plan (60-90 sec).
              Sinon, cliquez sur "Générer" pour le créer maintenant.
            </p>
          </div>
        </div>
        <Button onClick={regenerate} disabled={regenerating} data-testid="kit-pro-generate-btn">
          {regenerating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <RefreshCw className="w-4 h-4 mr-2" />}
          {regenerating ? 'Génération en cours...' : 'Générer le kit professionnel'}
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="kit-pro-tab">
      {/* Disclaimer confidentialité */}
      <div className="flex items-start gap-3 p-3 rounded-lg border border-amber-300 bg-gradient-to-r from-amber-50 to-orange-50" data-testid="kit-pro-disclaimer">
        <Lock className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
        <div className="flex-1 text-xs">
          <p className="font-semibold text-amber-900">CONFIDENTIEL — Usage interne S.E.S uniquement</p>
          <p className="text-amber-800 mt-0.5">
            Document généré par IA. Validation humaine obligatoire avant tout envoi extérieur.
            <strong> Ne jamais transmettre au client.</strong>
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap items-center gap-2 pb-2 border-b" data-testid="kit-pro-actions">
        <Button size="sm" variant="outline" onClick={regenerate} disabled={regenerating} data-testid="kit-pro-regen-btn">
          {regenerating ? <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" /> : <RefreshCw className="w-3.5 h-3.5 mr-1.5" />}
          {regenerating ? 'Génération...' : 'Re-générer'}
        </Button>
        <Button size="sm" variant="outline" onClick={downloadPDF} data-testid="kit-pro-pdf-btn">
          <Download className="w-3.5 h-3.5 mr-1.5" /> Télécharger PDF
        </Button>
        <span className="text-[10px] text-muted-foreground ml-auto">
          Généré le {kit.generated_at ? new Date(kit.generated_at).toLocaleString('fr-FR') : '—'}
          {kit.regenerated_count > 0 && ` · ${kit.regenerated_count} régénération(s)`}
        </span>
      </div>

      {/* Sections */}
      <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
        {SECTIONS.map(s => {
          const content = kit[s.key];
          if (!content) return null;
          return (
            <details key={s.key} className="rounded-lg border bg-card" data-testid={`kit-pro-section-${s.key}`}>
              <summary className="cursor-pointer px-4 py-3 font-medium text-sm hover:bg-muted/50 transition-colors select-none">
                {s.label}
              </summary>
              <div className="px-4 pb-4 pt-2 border-t">
                <PremiumAnalysisRenderer markdown={content} testIdPrefix={`kit-${s.key}`} />
              </div>
            </details>
          );
        })}
      </div>

      {/* Notes internes éditables */}
      <div className="space-y-2 pt-3 border-t" data-testid="kit-pro-notes-section">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium">8. Notes internes (privées)</label>
          <Button size="sm" variant="ghost" onClick={saveNotes} disabled={savingNotes} data-testid="kit-pro-save-notes">
            {savingNotes ? <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" /> : <Save className="w-3.5 h-3.5 mr-1.5" />}
            Sauvegarder
          </Button>
        </div>
        <Textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Vos annotations personnelles, points de vigilance, suivi téléphonique, observations..."
          className="min-h-[120px] text-sm"
          data-testid="kit-pro-notes-textarea"
        />
      </div>
    </div>
  );
}
