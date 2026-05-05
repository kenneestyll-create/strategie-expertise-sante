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
 * Irreversible bulk purge button with mandatory "PURGER" confirmation.
 *
 * Props:
 *   endpoint: relative API path WITHOUT /api prefix (e.g. "/admin/bookings/purge-all")
 *   label: button text (default "Tout vider")
 *   dialogTitle: modal title
 *   dialogDescription: modal description text
 *   resourceLabel: short name used in toast (e.g. "RDV", "clients")
 *   onPurged: callback after successful purge
 */
export const PurgeAllButton = ({
  endpoint,
  label = 'Tout vider',
  dialogTitle = 'Tout vider — action irréversible',
  dialogDescription,
  resourceLabel = 'éléments',
  onPurged,
  size = 'sm',
  variant = 'outline',
  testid,
}) => {
  const { token } = useAuth();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [confirmInput, setConfirmInput] = useState('');

  const purge = async () => {
    if (confirmInput.trim() !== 'PURGER') {
      toast.error('Tapez exactement PURGER pour confirmer');
      return;
    }
    setLoading(true);
    try {
      const r = await axios.post(`${API}${endpoint}`, { confirm: 'PURGER' }, { headers: { Authorization: `Bearer ${token}` } });
      const deleted = r.data.deleted ?? r.data.codes_deleted ?? r.data.analyses_deleted ?? 0;
      toast.success(`${deleted} ${resourceLabel} supprimé(s)`);
      setOpen(false);
      setConfirmInput('');
      if (onPurged) onPurged(r.data);
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Erreur lors de la purge');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        size={size}
        variant={variant}
        onClick={() => setOpen(true)}
        className="gap-1.5 text-xs text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700"
        data-testid={testid}
      >
        <Trash2 className="w-3.5 h-3.5" />
        {label}
      </Button>
      <Dialog open={open} onOpenChange={(o) => !loading && setOpen(o)}>
        <DialogContent className="max-w-md" data-testid={`${testid}-dialog`}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="w-5 h-5" />
              {dialogTitle}
            </DialogTitle>
            <DialogDescription>
              {dialogDescription || `Cette action supprimera TOUS les ${resourceLabel}. Action irréversible.`}
            </DialogDescription>
          </DialogHeader>
          <div>
            <label className="text-xs font-semibold text-foreground/80 mb-1 block">
              Tapez <strong className="text-red-600">PURGER</strong> pour confirmer
            </label>
            <Input
              value={confirmInput}
              onChange={(e) => setConfirmInput(e.target.value)}
              placeholder="PURGER"
              className="h-9 text-sm"
              data-testid={`${testid}-confirm-input`}
              autoFocus
            />
          </div>
          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setOpen(false)} disabled={loading}>Annuler</Button>
            <Button
              variant="destructive"
              onClick={purge}
              disabled={loading || confirmInput.trim() !== 'PURGER'}
              className="gap-1.5"
              data-testid={`${testid}-confirm-btn`}
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
              Vider définitivement
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

/**
 * Small per-row delete icon button with inline confirmation.
 * Calls DELETE on the given endpoint.
 */
export const DeleteRowButton = ({ endpoint, onDeleted, confirmMessage = 'Supprimer cet élément ?', testid }) => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);

  const handleClick = async (e) => {
    e.stopPropagation();
    if (!window.confirm(confirmMessage)) return;
    setLoading(true);
    try {
      await axios.delete(`${API}${endpoint}`, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Élément supprimé');
      if (onDeleted) onDeleted();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Erreur suppression');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      size="icon"
      variant="ghost"
      onClick={handleClick}
      disabled={loading}
      className="h-7 w-7 text-red-500 hover:text-red-700 hover:bg-red-50"
      title="Supprimer"
      data-testid={testid}
    >
      {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
    </Button>
  );
};

export default PurgeAllButton;
