import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import { UserPlus, Copy, Trash2, Loader2, GraduationCap, MessageSquareText, Send, FileText, Download, Eye, PenLine } from 'lucide-react';
import { ExpertFeedbackDialog } from './ExpertFeedbackDialog';
import { ExpertInvitationEditor } from './ExpertInvitationEditor';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const PROFILES = {
  medecin_expert: 'Médecin expert', avocat: 'Avocat', association: 'Association',
  comite_scientifique: 'Comité scientifique', beta_privee: 'Bêta privée', partenaire: 'Partenaire', autre: 'Autre',
};

const DEMO_CASE_FILES = [
  ['1-certificat-medical-initial.pdf', 'Certificat médical initial'],
  ['2-notification-refus-cpam.pdf', 'Notification de refus CPAM'],
  ['3-compte-rendu-psychiatrique.pdf', 'Compte rendu psychiatrique'],
  ['4-arret-travail-scan-degrade.pdf', 'Arrêt de travail (scan volontairement flou)'],
  ['5-elements-contexte-professionnel.pdf', 'Éléments de contexte professionnel'],
  ['6-courrier-medecin-conseil.pdf', 'Courrier du médecin-conseil'],
];

const DemoCasePreview = () => {
  const [open, setOpen] = useState(false);
  return (
    <div className="p-3 rounded-lg border border-dashed border-[#C9A84C]/40 bg-[#C9A84C]/5" data-testid="ea-demo-preview">
      <button className="w-full flex items-center justify-between text-left" onClick={() => setOpen(o => !o)} data-testid="ea-demo-preview-toggle">
        <span className="flex items-center gap-2 text-xs font-semibold">
          <Eye className="w-3.5 h-3.5 text-[#C9A84C]" /> Prévisualiser le cas fictif de démonstration
          <span className="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded border border-red-400/40 text-red-600 bg-red-500/10">Cas fictif</span>
        </span>
        <span className="text-[10px] text-muted-foreground">{open ? 'Réduire' : 'Afficher'}</span>
      </button>
      {open && (
        <div className="mt-3 space-y-2">
          <p className="text-[11px] text-muted-foreground leading-relaxed">
            Ce sont <strong>exactement les mêmes fichiers</strong> que ceux proposés à l'évaluateur sur /evaluation-expert
            (source unique : /cas-demonstration/). Chaque page porte le filigrane « CAS FICTIF DE DÉMONSTRATION ».
          </p>
          <div className="grid sm:grid-cols-2 gap-1.5">
            {DEMO_CASE_FILES.map(([file, label], i) => (
              <a key={file} href={`/cas-demonstration/${file}`} target="_blank" rel="noreferrer"
                className="flex items-center gap-2 text-[11px] p-2 rounded-md border border-border hover:border-[#C9A84C]/50 hover:bg-[#C9A84C]/5 transition-colors"
                data-testid={`ea-demo-file-${i + 1}`}>
                <FileText className="w-3.5 h-3.5 text-[#C9A84C] shrink-0" /> {i + 1}. {label}
              </a>
            ))}
          </div>
          <a href="/cas-demonstration/cas-demonstration-complet.zip" download
            className="inline-flex items-center gap-1.5 text-[11px] font-medium text-[#C9A84C] hover:underline mt-1"
            data-testid="ea-demo-zip">
            <Download className="w-3.5 h-3.5" /> Télécharger le dossier complet (.zip) — identique à celui de l'évaluateur
          </a>
        </div>
      )}
    </div>
  );
};

export const AdminExpertAccess = ({ token }) => {
  const [list, setList] = useState([]);
  const [config, setConfig] = useState({ default_quota: 3, default_validity_days: 30 });
  const [form, setForm] = useState({ name: '', email: '', profile_type: 'medecin_expert', quota_analyses: '', validity_days: '', notes: '' });
  const [loading, setLoading] = useState(false);
  const [feedbacks, setFeedbacks] = useState({});
  const [viewFeedback, setViewFeedback] = useState(null);
  const headers = { Authorization: `Bearer ${token}` };

  const load = useCallback(async () => {
    try {
      const [l, c, fb] = await Promise.all([
        axios.get(`${API}/admin/expert-access`, { headers }),
        axios.get(`${API}/admin/expert-access/config`, { headers }),
        axios.get(`${API}/admin/expert-access/feedback`, { headers }),
      ]);
      setList(l.data.evaluators || []);
      setConfig(c.data);
      const map = {};
      (fb.data.feedback || []).forEach((f) => { map[f.evaluator_id] = f; });
      setFeedbacks(map);
    } catch { toast.error('Chargement des évaluateurs impossible'); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const create = async () => {
    if (!form.name.trim() || !form.email.trim()) return toast.error('Nom et email requis');
    setLoading(true);
    try {
      const payload = { ...form };
      if (!payload.quota_analyses) delete payload.quota_analyses;
      if (!payload.validity_days) delete payload.validity_days;
      const res = await axios.post(`${API}/admin/expert-access`, payload, { headers });
      setForm({ name: '', email: '', profile_type: 'medecin_expert', quota_analyses: '', validity_days: '', notes: '' });
      await load();
      copyLink(res.data.token);
      toast.success(`Accès créé pour ${res.data.name} — lien d'invitation copié`);
    } catch (e) { toast.error(e.response?.data?.detail || 'Erreur de création'); }
    finally { setLoading(false); }
  };

  const copyLink = (t) => {
    const url = `${window.location.origin}/evaluation-expert?t=${t}`;
    navigator.clipboard.writeText(url).then(() => toast.success('Lien copié')).catch(() => toast.info(url));
  };

  const update = async (id, updates) => {
    try {
      await axios.put(`${API}/admin/expert-access/${id}`, updates, { headers });
      await load();
    } catch { toast.error('Mise à jour impossible'); }
  };

  const remove = async (id, name) => {
    if (!window.confirm(`Supprimer l'accès de ${name} ?`)) return;
    try { await axios.delete(`${API}/admin/expert-access/${id}`, { headers }); await load(); toast.success('Accès supprimé'); }
    catch { toast.error('Suppression impossible'); }
  };

  const [sendingInvite, setSendingInvite] = useState(null);
  const [editorOpen, setEditorOpen] = useState(false);

  const sendInvitation = async (e) => {
    const already = e.invitation_sent_at ? `\n(Une invitation a déjà été envoyée le ${new Date(e.invitation_sent_at).toLocaleDateString('fr-FR')}.)` : '';
    if (!window.confirm(`Envoyer l'email d'invitation à ${e.name} (${e.email}) ?${already}`)) return;
    setSendingInvite(e.id);
    try {
      await axios.post(`${API}/admin/expert-access/${e.id}/send-invitation`, {}, { headers });
      toast.success(`Invitation envoyée à ${e.email}`);
      await load();
    } catch (err) { toast.error(err.response?.data?.detail || "Envoi impossible"); }
    finally { setSendingInvite(null); }
  };

  const saveConfig = async () => {
    try { await axios.put(`${API}/admin/expert-access/config`, config, { headers }); toast.success('Valeurs par défaut enregistrées'); }
    catch { toast.error('Enregistrement impossible'); }
  };

  return (
    <Card className="border-2 border-[#C9A84C]/30" data-testid="admin-expert-access-card">
      <CardContent className="p-5 space-y-5">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-[#C9A84C]" />
            <div>
              <h3 className="font-semibold text-sm">Accès Évaluateurs Experts</h3>
              <p className="text-xs text-muted-foreground">Accès gratuits, dossiers marqués eval_test, exclus de tous les KPIs.</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <Button size="sm" variant="outline" className="h-7 text-xs gap-1.5" onClick={() => setEditorOpen(true)} data-testid="ea-edit-invitation">
              <PenLine className="w-3 h-3" /> Email d'invitation
            </Button>
            <span className="text-muted-foreground">Défauts :</span>
            <Input type="number" className="w-16 h-7 text-xs" value={config.default_quota}
              onChange={(e) => setConfig(c => ({ ...c, default_quota: e.target.value }))} data-testid="ea-config-quota" />
            <span className="text-muted-foreground">analyses /</span>
            <Input type="number" className="w-16 h-7 text-xs" value={config.default_validity_days}
              onChange={(e) => setConfig(c => ({ ...c, default_validity_days: e.target.value }))} data-testid="ea-config-days" />
            <span className="text-muted-foreground">jours</span>
            <Button size="sm" variant="outline" className="h-7 text-xs" onClick={saveConfig} data-testid="ea-config-save">OK</Button>
          </div>
        </div>

        <DemoCasePreview />

        <div className="grid sm:grid-cols-6 gap-2 items-end p-3 rounded-lg bg-muted/40" data-testid="ea-create-form">
          <Input placeholder="Nom (Dr ...)" value={form.name} onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))} className="sm:col-span-1 h-8 text-xs" data-testid="ea-input-name" />
          <Input placeholder="Email" type="email" value={form.email} onChange={(e) => setForm(f => ({ ...f, email: e.target.value }))} className="sm:col-span-1 h-8 text-xs" data-testid="ea-input-email" />
          <select value={form.profile_type} onChange={(e) => setForm(f => ({ ...f, profile_type: e.target.value }))} className="h-8 text-xs rounded-md border border-input bg-background px-2" data-testid="ea-input-profile">
            {Object.entries(PROFILES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          <Input placeholder={`Quota (${config.default_quota})`} type="number" value={form.quota_analyses} onChange={(e) => setForm(f => ({ ...f, quota_analyses: e.target.value }))} className="h-8 text-xs" data-testid="ea-input-quota" />
          <Input placeholder={`Jours (${config.default_validity_days})`} type="number" value={form.validity_days} onChange={(e) => setForm(f => ({ ...f, validity_days: e.target.value }))} className="h-8 text-xs" data-testid="ea-input-days" />
          <Button size="sm" onClick={create} disabled={loading} className="h-8 text-xs gap-1" data-testid="ea-create-button">
            {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <UserPlus className="w-3 h-3" />} Créer
          </Button>
          <Input placeholder="Notes internes (optionnel)" value={form.notes} onChange={(e) => setForm(f => ({ ...f, notes: e.target.value }))} className="sm:col-span-6 h-8 text-xs" data-testid="ea-input-notes" />
        </div>

        {list.length === 0 ? (
          <p className="text-xs text-muted-foreground italic" data-testid="ea-empty">Aucun évaluateur pour le moment.</p>
        ) : (
          <div className="space-y-2" data-testid="ea-list">
            {list.map((e) => {
              const expired = new Date(e.expires_at) < new Date();
              return (
                <div key={e.id} className={`flex items-center justify-between flex-wrap gap-2 p-3 rounded-lg border text-xs ${!e.active || expired ? 'opacity-60 border-border' : 'border-[#C9A84C]/30'}`} data-testid={`ea-row-${e.id}`}>
                  <div className="min-w-[220px]">
                    <p className="font-medium text-sm">{e.name} <span className="text-[10px] text-muted-foreground font-normal">({PROFILES[e.profile_type] || e.profile_type})</span></p>
                    <p className="text-muted-foreground">{e.email}{e.notes ? ` — ${e.notes}` : ''}</p>
                    <p className="text-[10px] text-muted-foreground mt-0.5" data-testid={`ea-activity-${e.id}`}>
                      {e.dossiers_count > 0 ? `${e.dossiers_count} analyse${e.dossiers_count > 1 ? 's' : ''} réalisée${e.dossiers_count > 1 ? 's' : ''}` : 'Aucune analyse'}
                      {' · '}Restant : {Math.max(0, e.quota_analyses - e.analyses_used)}
                      {e.last_activity_at ? ` · Dernière activité : ${new Date(e.last_activity_at).toLocaleDateString('fr-FR')}` : ' · Jamais connecté'}
                    </p>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-muted-foreground">Quota</span>
                    <strong data-testid={`ea-quota-${e.id}`}>{e.analyses_used}/{e.quota_analyses}</strong>
                    <Input type="number" defaultValue={e.quota_analyses} className="w-14 h-6 text-[11px]"
                      onBlur={(ev) => { const v = parseInt(ev.target.value); if (v && v !== e.quota_analyses) update(e.id, { quota_analyses: v }); }} data-testid={`ea-edit-quota-${e.id}`} />
                  </div>
                  <div className="text-muted-foreground">
                    {expired ? <span className="text-red-500 font-medium">Expiré</span> : <>Expire le {new Date(e.expires_at).toLocaleDateString('fr-FR')}</>}
                    <Button size="sm" variant="ghost" className="h-6 text-[10px] ml-1 px-1.5" onClick={() => update(e.id, { extend_days: 30 })} data-testid={`ea-extend-${e.id}`}>+30 j</Button>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button size="sm" variant={e.invitation_sent_at ? 'ghost' : 'default'} disabled={sendingInvite === e.id}
                      className={`h-6 text-[10px] gap-1 px-2 ${e.invitation_sent_at ? 'text-muted-foreground' : 'bg-[#C9A84C] hover:bg-[#b8963e] text-[#141410]'}`}
                      onClick={() => sendInvitation(e)} data-testid={`ea-invite-${e.id}`}>
                      {sendingInvite === e.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Send className="w-3 h-3" />}
                      {e.invitation_sent_at ? `Renvoyer (env. ${new Date(e.invitation_sent_at).toLocaleDateString('fr-FR')})` : 'Inviter'}
                    </Button>
                    {e.has_feedback ? (
                      <Button size="sm" variant="outline" className="h-6 text-[10px] gap-1 px-2 border-emerald-500/40 text-emerald-600 hover:text-emerald-700"
                        onClick={() => setViewFeedback(feedbacks[e.id])} data-testid={`ea-view-feedback-${e.id}`}>
                        <MessageSquareText className="w-3 h-3" /> Voir le retour
                      </Button>
                    ) : (
                      <span className="text-[10px] text-muted-foreground italic" data-testid={`ea-no-feedback-${e.id}`}>Pas de retour</span>
                    )}
                    <Switch checked={e.active} onCheckedChange={(v) => update(e.id, { active: v })} data-testid={`ea-toggle-${e.id}`} />
                    <Button size="sm" variant="outline" className="h-6 text-[10px] gap-1 px-2" onClick={() => copyLink(e.token)} data-testid={`ea-copy-${e.id}`}>
                      <Copy className="w-3 h-3" /> Lien
                    </Button>
                    <Button size="sm" variant="ghost" className="h-6 px-1.5 text-red-500" onClick={() => remove(e.id, e.name)} data-testid={`ea-delete-${e.id}`}>
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
        <ExpertFeedbackDialog feedback={viewFeedback} open={!!viewFeedback} onOpenChange={(o) => !o && setViewFeedback(null)} />
        <ExpertInvitationEditor token={token} open={editorOpen} onOpenChange={setEditorOpen} />
      </CardContent>
    </Card>
  );
};
