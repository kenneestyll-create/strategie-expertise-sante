import { useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Trash2, Loader2, AlertTriangle } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/**
 * Reusable "Purger les tests" button with two-step confirmation.
 *
 * Props:
 *   - section: backend section key (e.g. "clients", "bookings", "feedback", "editorial", "relance")
 *   - label: button label (default "Purger les tests")
 *   - onPurged: callback after successful purge
 *   - readonly: if true, hides the purge button (for relance which redirects to contacts)
 */
export const TestDataPurgeButton = ({ section, label = 'Purger les tests', onPurged, testid }) => {
  const { token } = useAuth();
  const cfg = { headers: { Authorization: `Bearer ${token}` } };
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [confirmInput, setConfirmInput] = useState('');

  const openDialog = async () => {
    setOpen(true);
    setConfirmInput('');
    setPreview(null);
    setLoading(true);
    try {
      const r = await axios.get(`${API}/admin/test-cleanup/${section}/preview`, cfg);
      setPreview(r.data);
    } catch {
      toast.error('Erreur lors de la détection des données de test');
      setOpen(false);
    } finally {
      setLoading(false);
    }
  };

  const purge = async () => {
    if (confirmInput.trim() !== 'PURGER') {
      toast.error('Tapez exactement PURGER pour confirmer');
      return;
    }
    setLoading(true);
    try {
      const r = await axios.post(
        `${API}/admin/test-cleanup/${section}/purge`,
        { confirm: 'PURGER' },
        cfg
      );
      toast.success(`${r.data.deleted} élément(s) de test supprimé(s)`);
      setOpen(false);
      if (onPurged) onPurged(r.data.deleted);
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Erreur lors de la purge');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        size="sm"
        variant="outline"
        onClick={openDialog}
        className="gap-1.5 text-xs text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700"
        data-testid={testid || `test-cleanup-${section}-btn`}
      >
        <Trash2 className="w-3.5 h-3.5" />
        {label}
      </Button>

      <Dialog open={open} onOpenChange={(o) => !loading && setOpen(o)}>
        <DialogContent className="max-w-md" data-testid={`test-cleanup-${section}-dialog`}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="w-5 h-5" />
              Purger les données de test
            </DialogTitle>
            <DialogDescription>
              Détection automatique des entrées contenant des emails de test (`@test.com`, `@example.com`,
              `+test`, `pytest`), des noms commençant par "Test" ou "Demo", et le compte admin
              (`admin@accompagn-sante.fr`). Action irréversible.
            </DialogDescription>
          </DialogHeader>

          {loading && !preview ? (
            <div className="py-6 flex items-center justify-center"><Loader2 className="w-5 h-5 animate-spin text-muted-foreground" /></div>
          ) : preview ? (
            <div className="space-y-3">
              <div className="bg-muted/50 rounded-lg p-3">
                <p className="text-sm font-semibold mb-1">
                  {preview.count} élément{preview.count > 1 ? 's' : ''} détecté{preview.count > 1 ? 's' : ''}
                </p>
                {preview.note && (
                  <p className="text-xs italic text-amber-700 mb-2">{preview.note}</p>
                )}
                {preview.sample && preview.sample.length > 0 ? (
                  <ul className="text-xs space-y-1 max-h-40 overflow-y-auto">
                    {preview.sample.slice(0, 15).map((s, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <span className="text-red-500 mt-0.5">▸</span>
                        <span className="font-mono text-[11px] truncate">{s.email || s.nom || s.topic || s.id}</span>
                      </li>
                    ))}
                    {preview.sample.length > 15 && (
                      <li className="text-muted-foreground italic">+ {preview.count - 15} autre{preview.count - 15 > 1 ? 's' : ''}</li>
                    )}
                  </ul>
                ) : (
                  <p className="text-xs text-muted-foreground italic">Aucune donnée de test détectée — rien à supprimer.</p>
                )}
              </div>

              {preview.count > 0 && !preview.note && (
                <div>
                  <label className="text-xs font-semibold text-foreground/80 mb-1 block">
                    Tapez <strong className="text-red-600">PURGER</strong> pour confirmer
                  </label>
                  <Input
                    value={confirmInput}
                    onChange={(e) => setConfirmInput(e.target.value)}
                    placeholder="PURGER"
                    className="h-9 text-sm"
                    data-testid={`test-cleanup-${section}-confirm-input`}
                    autoFocus
                  />
                </div>
              )}
            </div>
          ) : null}

          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setOpen(false)} disabled={loading}>Annuler</Button>
            {preview && preview.count > 0 && !preview.note && (
              <Button
                variant="destructive"
                onClick={purge}
                disabled={loading || confirmInput.trim() !== 'PURGER'}
                className="gap-1.5"
                data-testid={`test-cleanup-${section}-confirm-btn`}
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                Supprimer {preview.count} élément{preview.count > 1 ? 's' : ''}
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default TestDataPurgeButton;
