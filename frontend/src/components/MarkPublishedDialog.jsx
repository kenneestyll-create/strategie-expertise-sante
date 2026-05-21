/**
 * MarkPublishedDialog — V4.3
 * Mini-dialog ouvert au clic "Marquer publié" pour capturer :
 *  - platform (tiktok / youtube / instagram / other)
 *  - public_url (optionnel)
 *
 * Appelle l'endpoint existant PATCH /admin/video-factory/{run_id}/status
 * avec body enrichi { status:'published', video_idx, platform, public_url? }.
 *
 * Zéro nouveau endpoint, zéro dashboard, zéro UI complexe — pure traçabilité.
 */
import { useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { CheckCircle2, Loader2 } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const PLATFORMS = [
  { value: 'tiktok',    label: 'TikTok' },
  { value: 'youtube',   label: 'YouTube Shorts' },
  { value: 'instagram', label: 'Instagram Reels' },
  { value: 'other',     label: 'Autre' },
];

export const MarkPublishedDialog = ({ open, onOpenChange, runId, videoIdx, axiosConfig, onPublished }) => {
  const [platform, setPlatform] = useState('tiktok');
  const [publicUrl, setPublicUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleConfirm = async () => {
    if (!platform) {
      toast.error('Sélectionnez une plateforme.');
      return;
    }
    const url = publicUrl.trim();
    if (url && !/^https?:\/\//i.test(url)) {
      toast.error('URL invalide — elle doit commencer par http:// ou https://');
      return;
    }
    setSubmitting(true);
    try {
      await axios.patch(
        `${API}/admin/video-factory/${runId}/status`,
        {
          status: 'published',
          video_idx: videoIdx,
          platform,
          public_url: url || null,
        },
        axiosConfig(),
      );
      toast.success(`Marqué publié sur ${PLATFORMS.find(p => p.value === platform)?.label || platform}`);
      onPublished?.({ videoIdx, platform, publicUrl: url || null });
      onOpenChange(false);
      setPublicUrl('');
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Échec mise à jour publication');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md" data-testid="mark-published-dialog">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-base">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            Marquer publié
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-3 py-1">
          <div className="space-y-1">
            <Label htmlFor="publish-platform" className="text-xs uppercase tracking-wide text-foreground/70">
              Plateforme <span className="text-red-500">*</span>
            </Label>
            <Select value={platform} onValueChange={setPlatform}>
              <SelectTrigger id="publish-platform" className="h-9 text-sm" data-testid="publish-platform-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PLATFORMS.map(p => (
                  <SelectItem key={p.value} value={p.value} className="text-sm">
                    {p.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1">
            <Label htmlFor="publish-url" className="text-xs uppercase tracking-wide text-foreground/70">
              URL publique <span className="text-foreground/50 font-normal normal-case">(optionnel)</span>
            </Label>
            <Input
              id="publish-url"
              type="url"
              placeholder="https://tiktok.com/@ses/video/..."
              value={publicUrl}
              onChange={(e) => setPublicUrl(e.target.value)}
              className="h-9 text-sm"
              data-testid="publish-url-input"
            />
            <p className="text-[10px] text-muted-foreground leading-relaxed">
              Lien direct vers le post publié. Utile pour retrouver vos vidéos plus tard.
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onOpenChange(false)}
            disabled={submitting}
            data-testid="publish-cancel"
          >
            Annuler
          </Button>
          <Button
            size="sm"
            onClick={handleConfirm}
            disabled={submitting}
            className="bg-emerald-600 hover:bg-emerald-700 text-white gap-1.5"
            data-testid="publish-confirm"
          >
            {submitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
            Confirmer la publication
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default MarkPublishedDialog;
