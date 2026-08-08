import { useState, useEffect } from 'react';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { Loader2, Send, RotateCcw, Save } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ExpertInvitationEditor = ({ token, open, onOpenChange }) => {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [isDefault, setIsDefault] = useState(true);
  const [busy, setBusy] = useState(null);
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (!open) return;
    axios.get(`${API}/admin/expert-access/invitation-template`, { headers })
      .then((res) => { setSubject(res.data.subject); setBody(res.data.body); setIsDefault(res.data.is_default); })
      .catch(() => toast.error('Chargement du modèle impossible'));
  }, [open]);

  const save = async () => {
    setBusy('save');
    try {
      await axios.put(`${API}/admin/expert-access/invitation-template`, { subject, body }, { headers });
      setIsDefault(false);
      toast.success('Modèle enregistré — il sera utilisé pour toutes les prochaines invitations');
    } catch (err) { toast.error(err.response?.data?.detail || 'Enregistrement impossible'); }
    finally { setBusy(null); }
  };

  const preview = async () => {
    setBusy('preview');
    try {
      const res = await axios.post(`${API}/admin/expert-access/invitation-template/preview`, { subject, body }, { headers });
      toast.success(`Aperçu envoyé à ${res.data.to} (valeurs d'exemple, lien inactif)`);
    } catch (err) { toast.error(err.response?.data?.detail || 'Envoi impossible'); }
    finally { setBusy(null); }
  };

  const reset = async () => {
    if (!window.confirm('Rétablir le modèle par défaut ? Vos modifications seront perdues.')) return;
    setBusy('reset');
    try {
      const res = await axios.delete(`${API}/admin/expert-access/invitation-template`, { headers });
      setSubject(res.data.subject); setBody(res.data.body); setIsDefault(true);
      toast.success('Modèle par défaut rétabli');
    } catch { toast.error('Réinitialisation impossible'); }
    finally { setBusy(null); }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[88vh] overflow-y-auto" data-testid="invitation-editor-dialog">
        <DialogHeader>
          <DialogTitle className="text-base">Modèle de l'email d'invitation {isDefault ? '(modèle par défaut)' : '(personnalisé)'}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 text-sm">
          <div className="p-2.5 rounded-md bg-muted/50 text-[11px] text-muted-foreground leading-relaxed">
            Variables disponibles (remplacées automatiquement à l'envoi) : <code className="font-semibold">{'{NOM}'}</code> (nom de l'évaluateur),{' '}
            <code className="font-semibold">{'{QUOTA}'}</code> (nombre d'analyses), <code className="font-semibold">{'{DATE_VALIDITE}'}</code> (date d'expiration).
            Mise en forme : <code className="font-semibold">**texte**</code> = gras · ligne commençant par <code className="font-semibold">- </code> = puce ·
            paragraphes séparés par une ligne vide. L'en-tête, le bouton doré (lien personnel) et le pied de page sont ajoutés automatiquement.
          </div>
          <div>
            <p className="text-xs font-medium mb-1">Objet</p>
            <Input value={subject} onChange={(e) => setSubject(e.target.value)} data-testid="invitation-editor-subject" />
          </div>
          <div>
            <p className="text-xs font-medium mb-1">Corps de l'email</p>
            <Textarea value={body} onChange={(e) => setBody(e.target.value)} rows={16}
              className="text-xs font-mono leading-relaxed" data-testid="invitation-editor-body" />
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <Button onClick={save} disabled={busy || !subject.trim() || !body.trim()} className="gap-1.5" data-testid="invitation-editor-save">
              {busy === 'save' ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />} Enregistrer
            </Button>
            <Button onClick={preview} disabled={busy} variant="outline" className="gap-1.5" data-testid="invitation-editor-preview">
              {busy === 'preview' ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />} M'envoyer un aperçu
            </Button>
            <Button onClick={reset} disabled={busy || isDefault} variant="ghost" className="gap-1.5 text-muted-foreground" data-testid="invitation-editor-reset">
              <RotateCcw className="w-3.5 h-3.5" /> Rétablir le modèle par défaut
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
