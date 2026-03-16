import { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import {
  FileText, Plus, Copy, Trash2, Eye, Loader2, Pencil, X, Check, RefreshCw, Code, Send, Clock, CalendarClock
} from 'lucide-react';
import axios from 'axios';
import { CampaignsDashboard } from './CampaignsDashboard';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const VARIABLES = [
  { key: 'prenom', label: 'Prénom', sample: 'Marie', color: 'bg-blue-100 text-blue-700 hover:bg-blue-200' },
  { key: 'nom', label: 'Nom', sample: 'Dupont', color: 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200' },
  { key: 'completeness', label: '% Complétude', sample: '42', color: 'bg-green-100 text-green-700 hover:bg-green-200' },
  { key: 'documents_missing', label: 'Docs manquants', sample: 'Attestation employeur, Certificat médical', color: 'bg-amber-100 text-amber-700 hover:bg-amber-200' },
  { key: 'date_inscription', label: 'Date inscription', sample: '15/01/2026', color: 'bg-purple-100 text-purple-700 hover:bg-purple-200' },
];

const VariableToolbar = ({ onInsert, targetField }) => (
  <div className="flex items-center gap-1.5 flex-wrap py-1.5 px-2 bg-muted/40 rounded-md border border-dashed" data-testid={`var-toolbar-${targetField}`}>
    <Code className="w-3 h-3 text-muted-foreground flex-shrink-0" />
    <span className="text-[10px] text-muted-foreground mr-1">Variables :</span>
    {VARIABLES.map(v => (
      <button
        key={v.key}
        type="button"
        onClick={() => onInsert(`{{${v.key}}}`)}
        className={`text-[10px] px-1.5 py-0.5 rounded-md font-medium cursor-pointer transition-colors ${v.color}`}
        title={`Insérer {{${v.key}}} — ${v.label} (ex: ${v.sample})`}
        data-testid={`var-btn-${v.key}-${targetField}`}
      >
        {`{{${v.key}}}`}
      </button>
    ))}
  </div>
);

const HighlightedText = ({ text }) => {
  if (!text) return null;
  const parts = text.split(/(\{\{[a-z_]+\}\})/g);
  return (
    <span>
      {parts.map((part, i) => {
        const match = part.match(/^\{\{([a-z_]+)\}\}$/);
        if (match) {
          const v = VARIABLES.find(x => x.key === match[1]);
          return (
            <span key={i} className={`inline-block text-[10px] px-1 py-0 rounded font-semibold ${v?.color || 'bg-gray-100 text-gray-600'}`}>
              {part}
            </span>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </span>
  );
};

const formatTimeAgo = (isoDate) => {
  if (!isoDate) return '';
  const diff = Date.now() - new Date(isoDate).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "à l'instant";
  if (mins < 60) return `il y a ${mins} min`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `il y a ${hrs}h`;
  const days = Math.floor(hrs / 24);
  return `il y a ${days}j`;
};

export const EmailTemplateEditor = ({ token }) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [previewHtml, setPreviewHtml] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [showNewDialog, setShowNewDialog] = useState(false);
  const [newForm, setNewForm] = useState({ name: '', label: '', subject: '', intro: '', motivation: '', cta_text: 'Compléter mon dossier' });
  const [creating, setCreating] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [activeFieldRef, setActiveFieldRef] = useState(null);
  const [sendTestTpl, setSendTestTpl] = useState(null);
  const [testForm, setTestForm] = useState({ email: '', prenom: 'Marie', nom: 'Dupont', completeness: '42', documents_missing: 'Attestation employeur, Certificat médical', date_inscription: '15/01/2026' });
  const [sending, setSending] = useState(false);
  const [testHistory, setTestHistory] = useState([]);
  const [testHistoryMap, setTestHistoryMap] = useState({});
  const [scheduleTpl, setScheduleTpl] = useState(null);
  const [scheduleForm, setScheduleForm] = useState({ date: '', time: '09:00', target: 'inactive_clients', ab_test_id: '' });
  const [scheduling, setScheduling] = useState(false);
  const [abTests, setAbTests] = useState([]);
  const [campaignsKey, setCampaignsKey] = useState(0);

  const subjectRef = useRef(null);
  const introRef = useRef(null);
  const motivationRef = useRef(null);
  const ctaRef = useRef(null);
  const newSubjectRef = useRef(null);
  const newIntroRef = useRef(null);
  const newMotivationRef = useRef(null);
  const newCtaRef = useRef(null);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/admin/email-templates`, { headers });
      const tpls = res.data.templates || [];
      setTemplates(tpls);
      // Fetch last test for each template
      const histMap = {};
      await Promise.all(tpls.map(async (t) => {
        try {
          const hRes = await axios.get(`${API}/admin/email-templates/${t.id}/test-history`, { headers });
          if (hRes.data.history?.length > 0) {
            histMap[t.id] = hRes.data.history[0];
          }
        } catch { /* ignore */ }
      }));
      setTestHistoryMap(histMap);
    } catch {
      toast.error('Erreur lors du chargement des templates');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchTemplates(); }, [fetchTemplates]);

  const insertAtCursor = (ref, field, formSetter, value) => {
    const el = ref?.current;
    if (el) {
      const start = el.selectionStart ?? el.value?.length ?? 0;
      const end = el.selectionEnd ?? start;
      const current = el.value || '';
      const newVal = current.slice(0, start) + value + current.slice(end);
      formSetter(f => ({ ...f, [field]: newVal }));
      requestAnimationFrame(() => {
        el.focus();
        const pos = start + value.length;
        el.setSelectionRange(pos, pos);
      });
    } else {
      formSetter(f => ({ ...f, [field]: (f[field] || '') + value }));
    }
  };

  const startEdit = (tpl) => {
    setEditingId(tpl.id);
    setEditForm({ subject: tpl.subject, intro: tpl.intro, motivation: tpl.motivation, cta_text: tpl.cta_text, label: tpl.label, status: tpl.status });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditForm({});
  };

  const saveEdit = async (id) => {
    setSaving(true);
    try {
      await axios.put(`${API}/admin/email-templates/${id}`, editForm, { headers });
      toast.success('Template mis à jour');
      setEditingId(null);
      setEditForm({});
      fetchTemplates();
    } catch {
      toast.error('Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const loadPreview = async (tpl) => {
    setPreviewLoading(true);
    setShowPreview(true);
    const data = editingId === tpl.id ? editForm : tpl;
    try {
      const res = await axios.post(`${API}/admin/email-templates/preview`, {
        subject: data.subject, intro: data.intro, motivation: data.motivation, cta_text: data.cta_text,
        prenom: 'Marie', completeness_pct: 42, documents_missing: 'Attestation employeur, Certificat médical initial'
      }, { headers });
      setPreviewHtml(res.data.html);
    } catch {
      toast.error("Erreur lors de l'aperçu");
      setShowPreview(false);
    } finally {
      setPreviewLoading(false);
    }
  };

  const createTemplate = async () => {
    if (!newForm.name.trim() || !newForm.subject.trim()) {
      toast.error('Le nom et le sujet sont obligatoires');
      return;
    }
    setCreating(true);
    try {
      await axios.post(`${API}/admin/email-templates`, { ...newForm, status: 'draft' }, { headers });
      toast.success('Nouveau template créé');
      setShowNewDialog(false);
      setNewForm({ name: '', label: '', subject: '', intro: '', motivation: '', cta_text: 'Compléter mon dossier' });
      fetchTemplates();
    } catch {
      toast.error('Erreur lors de la création');
    } finally {
      setCreating(false);
    }
  };

  const duplicateTemplate = async (id) => {
    try {
      await axios.post(`${API}/admin/email-templates/${id}/duplicate`, {}, { headers });
      toast.success('Template dupliqué');
      fetchTemplates();
    } catch {
      toast.error('Erreur lors de la duplication');
    }
  };

  const deleteTemplate = async () => {
    if (!deleteId) return;
    try {
      await axios.delete(`${API}/admin/email-templates/${deleteId}`, { headers });
      toast.success('Template supprimé');
      setDeleteId(null);
      fetchTemplates();
    } catch {
      toast.error('Erreur lors de la suppression');
    }
  };

  const seedDefaults = async () => {
    try {
      const res = await axios.post(`${API}/admin/email-templates/seed`, {}, { headers });
      if (res.data.created > 0) {
        toast.success(`${res.data.created} template(s) par défaut créé(s)`);
        fetchTemplates();
      } else {
        toast.info('Tous les templates par défaut existent déjà');
      }
    } catch {
      toast.error('Erreur lors du seed');
    }
  };

  const toggleStatus = async (tpl) => {
    const newStatus = tpl.status === 'active' ? 'draft' : 'active';
    try {
      await axios.put(`${API}/admin/email-templates/${tpl.id}`, { status: newStatus }, { headers });
      toast.success(`Template ${newStatus === 'active' ? 'activé' : 'désactivé'}`);
      fetchTemplates();
    } catch {
      toast.error('Erreur');
    }
  };

  const openSendTest = async (tpl) => {
    setSendTestTpl(tpl);
    setTestForm(f => ({ ...f, email: f.email || '' }));
    setTestHistory([]);
    try {
      const res = await axios.get(`${API}/admin/email-templates/${tpl.id}/test-history`, { headers });
      setTestHistory(res.data.history || []);
    } catch { /* ignore */ }
  };

  const sendTestEmail = async () => {
    if (!sendTestTpl) return;
    if (!testForm.email.trim()) {
      toast.error('Veuillez saisir une adresse email');
      return;
    }
    setSending(true);
    try {
      const res = await axios.post(`${API}/admin/email-templates/send-test`, {
        template_id: sendTestTpl.id,
        template_name: sendTestTpl.name,
        email: testForm.email,
        subject: sendTestTpl.subject,
        intro: sendTestTpl.intro,
        motivation: sendTestTpl.motivation,
        cta_text: sendTestTpl.cta_text,
        prenom: testForm.prenom,
        nom: testForm.nom,
        completeness: testForm.completeness,
        documents_missing: testForm.documents_missing,
        date_inscription: testForm.date_inscription,
      }, { headers });
      if (res.data.success) {
        toast.success(res.data.message);
      } else {
        toast.error(res.data.message || "Erreur lors de l'envoi");
      }
      // Refresh history
      const hRes = await axios.get(`${API}/admin/email-templates/${sendTestTpl.id}/test-history`, { headers });
      setTestHistory(hRes.data.history || []);
      setTestHistoryMap(m => ({ ...m, [sendTestTpl.id]: hRes.data.history?.[0] }));
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur lors de l'envoi du test");
    } finally {
      setSending(false);
    }
  };

  const openSchedule = async (tpl) => {
    setScheduleTpl(tpl);
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setScheduleForm({ date: tomorrow.toISOString().split('T')[0], time: '09:00', target: 'inactive_clients', ab_test_id: '' });
    try {
      const res = await axios.get(`${API}/admin/ab-tests`, { headers });
      setAbTests((res.data.tests || []).filter(t => t.status === 'active'));
    } catch { setAbTests([]); }
  };

  const scheduleCampaign = async () => {
    if (!scheduleTpl || !scheduleForm.date || !scheduleForm.time) {
      toast.error('Date et heure requises');
      return;
    }
    setScheduling(true);
    try {
      const scheduled_at = new Date(`${scheduleForm.date}T${scheduleForm.time}:00`).toISOString();
      await axios.post(`${API}/admin/campaigns/schedule`, {
        template_id: scheduleTpl.id,
        scheduled_at,
        target: scheduleForm.target,
        ab_test_id: scheduleForm.ab_test_id || null,
      }, { headers });
      toast.success('Campagne programmée avec succès');
      setScheduleTpl(null);
      setCampaignsKey(k => k + 1);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erreur lors de la programmation');
    } finally {
      setScheduling(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16" data-testid="templates-loading">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
        <span className="ml-2 text-sm text-muted-foreground">Chargement des templates...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="email-template-editor">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <FileText className="w-5 h-5 text-amber-500" />
            Éditeur de templates email
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Créez et modifiez vos modèles d'emails — utilisez les variables dynamiques pour personnaliser chaque envoi
          </p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" className="gap-1.5 text-xs" onClick={seedDefaults} data-testid="seed-defaults-btn">
            <RefreshCw className="w-3.5 h-3.5" /> Modèles par défaut
          </Button>
          <Button size="sm" className="gap-1.5 text-xs bg-amber-600 hover:bg-amber-700" onClick={() => setShowNewDialog(true)} data-testid="new-template-btn">
            <Plus className="w-3.5 h-3.5" /> Nouveau template
          </Button>
        </div>
      </div>

      {/* Variables reference card */}
      <Card className="border-dashed" data-testid="variables-reference-card">
        <CardContent className="py-3 px-4">
          <div className="flex items-center gap-2 mb-2">
            <Code className="w-4 h-4 text-violet-500" />
            <span className="text-xs font-semibold">Variables dynamiques disponibles</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {VARIABLES.map(v => (
              <div key={v.key} className="flex items-center gap-1.5 text-xs">
                <span className={`px-1.5 py-0.5 rounded font-mono font-medium text-[11px] ${v.color}`}>{`{{${v.key}}}`}</span>
                <span className="text-muted-foreground">{v.label}</span>
                <span className="text-[10px] text-muted-foreground/60 italic">ex: {v.sample}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Templates list */}
      {templates.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-40" />
            <p className="text-sm text-muted-foreground">Aucun template. Cliquez sur "Modèles par défaut" pour créer les templates de base.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {templates.map(tpl => {
            const isEditing = editingId === tpl.id;
            return (
              <Card key={tpl.id} className={`transition-all ${isEditing ? 'ring-2 ring-amber-400/50' : ''}`} data-testid={`template-card-${tpl.name}`}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <CardTitle className="text-sm font-semibold">
                        {isEditing ? (
                          <Input
                            value={editForm.label}
                            onChange={e => setEditForm(f => ({ ...f, label: e.target.value }))}
                            className="h-7 text-sm w-48"
                            data-testid={`edit-label-${tpl.name}`}
                          />
                        ) : tpl.label}
                      </CardTitle>
                      <Badge
                        variant="outline"
                        className={`text-[10px] cursor-pointer select-none ${tpl.status === 'active' ? 'bg-green-100 text-green-700 hover:bg-green-200' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'}`}
                        onClick={() => toggleStatus(tpl)}
                        data-testid={`toggle-status-${tpl.name}`}
                      >
                        {tpl.status === 'active' ? 'Actif' : 'Brouillon'}
                      </Badge>
                      {testHistoryMap[tpl.id] ? (
                        <span className="text-[10px] text-muted-foreground flex items-center gap-1" data-testid={`last-test-${tpl.name}`}>
                          <Clock className="w-3 h-3" />
                          Test {formatTimeAgo(testHistoryMap[tpl.id].sent_at)} → {testHistoryMap[tpl.id].email}
                        </span>
                      ) : (
                        <span className="text-[10px] text-muted-foreground/50 italic" data-testid={`no-test-${tpl.name}`}>Jamais testé</span>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      {isEditing ? (
                        <>
                          <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={cancelEdit} data-testid={`cancel-edit-${tpl.name}`}>
                            <X className="w-3.5 h-3.5" />
                          </Button>
                          <Button size="sm" className="h-7 gap-1 text-xs bg-green-600 hover:bg-green-700 px-2" onClick={() => saveEdit(tpl.id)} disabled={saving} data-testid={`save-edit-${tpl.name}`}>
                            {saving ? <Loader2 className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3" />}
                            Sauvegarder
                          </Button>
                        </>
                      ) : (
                        <>
                          <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={() => loadPreview(tpl)} data-testid={`preview-btn-${tpl.name}`}>
                            <Eye className="w-3.5 h-3.5 text-blue-500" />
                          </Button>
                          <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={() => openSendTest(tpl)} data-testid={`sendtest-btn-${tpl.name}`} title="Envoyer un email de test">
                            <Send className="w-3.5 h-3.5 text-emerald-500" />
                          </Button>
                          <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={() => openSchedule(tpl)} data-testid={`schedule-btn-${tpl.name}`} title="Programmer une campagne">
                            <CalendarClock className="w-3.5 h-3.5 text-violet-500" />
                          </Button>
                          <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={() => startEdit(tpl)} data-testid={`edit-btn-${tpl.name}`}>
                            <Pencil className="w-3.5 h-3.5 text-amber-500" />
                          </Button>
                          <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={() => duplicateTemplate(tpl.id)} data-testid={`duplicate-btn-${tpl.name}`}>
                            <Copy className="w-3.5 h-3.5 text-indigo-500" />
                          </Button>
                          <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={() => setDeleteId(tpl.id)} data-testid={`delete-btn-${tpl.name}`}>
                            <Trash2 className="w-3.5 h-3.5 text-red-400" />
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0 space-y-3">
                  {isEditing ? (
                    <div className="grid gap-3">
                      <div>
                        <label className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium">Sujet de l'email</label>
                        <VariableToolbar targetField="subject" onInsert={(v) => insertAtCursor(subjectRef, 'subject', setEditForm, v)} />
                        <Input
                          ref={subjectRef}
                          value={editForm.subject}
                          onChange={e => setEditForm(f => ({ ...f, subject: e.target.value }))}
                          className="mt-1 text-sm"
                          data-testid={`edit-subject-${tpl.name}`}
                        />
                      </div>
                      <div>
                        <label className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium">Texte d'introduction</label>
                        <VariableToolbar targetField="intro" onInsert={(v) => insertAtCursor(introRef, 'intro', setEditForm, v)} />
                        <Textarea
                          ref={introRef}
                          value={editForm.intro}
                          onChange={e => setEditForm(f => ({ ...f, intro: e.target.value }))}
                          className="mt-1 text-sm min-h-[60px]"
                          data-testid={`edit-intro-${tpl.name}`}
                        />
                      </div>
                      <div>
                        <label className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium">Texte de motivation</label>
                        <VariableToolbar targetField="motivation" onInsert={(v) => insertAtCursor(motivationRef, 'motivation', setEditForm, v)} />
                        <Textarea
                          ref={motivationRef}
                          value={editForm.motivation}
                          onChange={e => setEditForm(f => ({ ...f, motivation: e.target.value }))}
                          className="mt-1 text-sm min-h-[60px]"
                          data-testid={`edit-motivation-${tpl.name}`}
                        />
                      </div>
                      <div>
                        <label className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium">Texte du bouton CTA</label>
                        <VariableToolbar targetField="cta" onInsert={(v) => insertAtCursor(ctaRef, 'cta_text', setEditForm, v)} />
                        <Input
                          ref={ctaRef}
                          value={editForm.cta_text}
                          onChange={e => setEditForm(f => ({ ...f, cta_text: e.target.value }))}
                          className="mt-1 text-sm"
                          data-testid={`edit-cta-${tpl.name}`}
                        />
                      </div>
                      <div className="flex justify-end">
                        <Button size="sm" variant="outline" className="gap-1.5 text-xs" onClick={() => loadPreview(tpl)} data-testid={`preview-edit-${tpl.name}`}>
                          <Eye className="w-3.5 h-3.5" /> Aperçu avec variables résolues
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="grid gap-2">
                      <div className="flex items-start gap-2">
                        <span className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium min-w-[60px] pt-0.5">Sujet</span>
                        <p className="text-sm text-foreground"><HighlightedText text={tpl.subject} /></p>
                      </div>
                      <div className="flex items-start gap-2">
                        <span className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium min-w-[60px] pt-0.5">Intro</span>
                        <p className="text-sm text-muted-foreground line-clamp-2"><HighlightedText text={tpl.intro} /></p>
                      </div>
                      <div className="flex items-start gap-2">
                        <span className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium min-w-[60px] pt-0.5">CTA</span>
                        <Badge variant="outline" className="text-xs"><HighlightedText text={tpl.cta_text} /></Badge>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Preview Dialog */}
      <Dialog open={showPreview} onOpenChange={setShowPreview}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto" data-testid="template-preview-dialog">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-base">
              <Eye className="w-4 h-4 text-blue-500" /> Aperçu du template (variables résolues)
            </DialogTitle>
          </DialogHeader>
          <p className="text-xs text-muted-foreground -mt-2">
            Les variables <code className="bg-muted px-1 rounded">{`{{prenom}}`}</code>, <code className="bg-muted px-1 rounded">{`{{completeness}}`}</code>, etc. sont remplacées par des valeurs d'exemple.
          </p>
          {previewLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-5 h-5 animate-spin" />
            </div>
          ) : (
            <div className="border rounded-lg overflow-hidden bg-gray-50">
              <iframe
                srcDoc={previewHtml}
                title="Aperçu email"
                className="w-full min-h-[500px] border-0"
                sandbox=""
                data-testid="preview-iframe"
              />
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPreview(false)}>Fermer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* New Template Dialog */}
      <Dialog open={showNewDialog} onOpenChange={setShowNewDialog}>
        <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto" data-testid="new-template-dialog">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-base">
              <Plus className="w-4 h-4 text-amber-500" /> Nouveau template
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-3 py-2">
            <div>
              <label className="text-xs font-medium text-muted-foreground">Identifiant (slug)</label>
              <Input value={newForm.name} onChange={e => setNewForm(f => ({ ...f, name: e.target.value }))} placeholder="ex: relance_douce" className="mt-1" data-testid="new-tpl-name" />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">Libellé</label>
              <Input value={newForm.label} onChange={e => setNewForm(f => ({ ...f, label: e.target.value }))} placeholder="ex: Relance douce" className="mt-1" data-testid="new-tpl-label" />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">Sujet de l'email</label>
              <VariableToolbar targetField="new-subject" onInsert={(v) => insertAtCursor(newSubjectRef, 'subject', setNewForm, v)} />
              <Input ref={newSubjectRef} value={newForm.subject} onChange={e => setNewForm(f => ({ ...f, subject: e.target.value }))} placeholder="Objet de l'email" className="mt-1" data-testid="new-tpl-subject" />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">Texte d'introduction</label>
              <VariableToolbar targetField="new-intro" onInsert={(v) => insertAtCursor(newIntroRef, 'intro', setNewForm, v)} />
              <Textarea ref={newIntroRef} value={newForm.intro} onChange={e => setNewForm(f => ({ ...f, intro: e.target.value }))} placeholder="Bonjour {{prenom}}, votre dossier est à {{completeness}}%..." className="mt-1 min-h-[60px]" data-testid="new-tpl-intro" />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">Texte de motivation</label>
              <VariableToolbar targetField="new-motivation" onInsert={(v) => insertAtCursor(newMotivationRef, 'motivation', setNewForm, v)} />
              <Textarea ref={newMotivationRef} value={newForm.motivation} onChange={e => setNewForm(f => ({ ...f, motivation: e.target.value }))} placeholder="Documents manquants : {{documents_missing}}..." className="mt-1 min-h-[60px]" data-testid="new-tpl-motivation" />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">Texte du bouton CTA</label>
              <VariableToolbar targetField="new-cta" onInsert={(v) => insertAtCursor(newCtaRef, 'cta_text', setNewForm, v)} />
              <Input ref={newCtaRef} value={newForm.cta_text} onChange={e => setNewForm(f => ({ ...f, cta_text: e.target.value }))} placeholder="Compléter mon dossier" className="mt-1" data-testid="new-tpl-cta" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewDialog(false)}>Annuler</Button>
            <Button className="gap-1.5 bg-amber-600 hover:bg-amber-700" onClick={createTemplate} disabled={creating} data-testid="create-template-btn">
              {creating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
              Créer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Send Test Email Dialog */}
      <Dialog open={!!sendTestTpl} onOpenChange={(open) => { if (!open) setSendTestTpl(null); }}>
        <DialogContent className="max-w-md" data-testid="send-test-dialog">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-base">
              <Send className="w-4 h-4 text-emerald-500" /> Envoyer un email de test
            </DialogTitle>
          </DialogHeader>
          {sendTestTpl && (
            <div className="grid gap-3 py-1">
              <p className="text-xs text-muted-foreground">
                Template : <span className="font-medium text-foreground">{sendTestTpl.label}</span>
              </p>
              <div className="p-2.5 rounded-md bg-amber-50 border border-amber-200">
                <p className="text-[11px] text-amber-700">Resend est en mode sandbox. L'email ne sera livré qu'aux adresses vérifiées dans votre compte Resend.</p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Email destinataire</label>
                <Input
                  type="email"
                  value={testForm.email}
                  onChange={e => setTestForm(f => ({ ...f, email: e.target.value }))}
                  placeholder="votre@email.com"
                  className="mt-1"
                  data-testid="test-email-input"
                />
              </div>
              <div className="border rounded-md p-3 space-y-2">
                <p className="text-[10px] uppercase tracking-wide text-muted-foreground font-semibold">Valeurs de test des variables</p>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[10px] text-muted-foreground">Prénom</label>
                    <Input value={testForm.prenom} onChange={e => setTestForm(f => ({ ...f, prenom: e.target.value }))} className="h-7 text-xs mt-0.5" data-testid="test-var-prenom" />
                  </div>
                  <div>
                    <label className="text-[10px] text-muted-foreground">Nom</label>
                    <Input value={testForm.nom} onChange={e => setTestForm(f => ({ ...f, nom: e.target.value }))} className="h-7 text-xs mt-0.5" data-testid="test-var-nom" />
                  </div>
                  <div>
                    <label className="text-[10px] text-muted-foreground">% Complétude</label>
                    <Input value={testForm.completeness} onChange={e => setTestForm(f => ({ ...f, completeness: e.target.value }))} className="h-7 text-xs mt-0.5" data-testid="test-var-completeness" />
                  </div>
                  <div>
                    <label className="text-[10px] text-muted-foreground">Date inscription</label>
                    <Input value={testForm.date_inscription} onChange={e => setTestForm(f => ({ ...f, date_inscription: e.target.value }))} className="h-7 text-xs mt-0.5" data-testid="test-var-date" />
                  </div>
                </div>
                <div>
                  <label className="text-[10px] text-muted-foreground">Documents manquants</label>
                  <Input value={testForm.documents_missing} onChange={e => setTestForm(f => ({ ...f, documents_missing: e.target.value }))} className="h-7 text-xs mt-0.5" data-testid="test-var-docs" />
                </div>
              </div>
              {/* Test History */}
              {testHistory.length > 0 && (
                <div className="border rounded-md p-3 space-y-2" data-testid="test-history-section">
                  <p className="text-[10px] uppercase tracking-wide text-muted-foreground font-semibold flex items-center gap-1">
                    <Clock className="w-3 h-3" /> Derniers tests envoyés
                  </p>
                  <div className="space-y-1.5 max-h-[120px] overflow-y-auto">
                    {testHistory.slice(0, 5).map((h, i) => (
                      <div key={h.id || i} className="flex items-center justify-between text-[11px] py-1 px-2 rounded bg-muted/40" data-testid={`test-history-item-${i}`}>
                        <div className="flex items-center gap-2">
                          <span className={`w-1.5 h-1.5 rounded-full ${h.status === 'sent' ? 'bg-green-500' : 'bg-red-400'}`} />
                          <span className="text-muted-foreground">{h.email}</span>
                        </div>
                        <span className="text-muted-foreground/70">{formatTimeAgo(h.sent_at)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSendTestTpl(null)}>Annuler</Button>
            <Button className="gap-1.5 bg-emerald-600 hover:bg-emerald-700" onClick={sendTestEmail} disabled={sending} data-testid="confirm-send-test-btn">
              {sending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              Envoyer le test
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Schedule Campaign Dialog */}
      <Dialog open={!!scheduleTpl} onOpenChange={(o) => { if (!o) setScheduleTpl(null); }}>
        <DialogContent className="max-w-md" data-testid="schedule-campaign-dialog">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-base">
              <CalendarClock className="w-4 h-4 text-violet-500" /> Programmer une campagne
            </DialogTitle>
          </DialogHeader>
          {scheduleTpl && (
            <div className="grid gap-3 py-1">
              <p className="text-xs text-muted-foreground">
                Template : <span className="font-medium text-foreground">{scheduleTpl.label}</span>
              </p>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-medium text-muted-foreground">Date</label>
                  <Input
                    type="date"
                    value={scheduleForm.date}
                    onChange={e => setScheduleForm(f => ({ ...f, date: e.target.value }))}
                    min={new Date().toISOString().split('T')[0]}
                    className="mt-1"
                    data-testid="schedule-date-input"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground">Heure</label>
                  <Input
                    type="time"
                    value={scheduleForm.time}
                    onChange={e => setScheduleForm(f => ({ ...f, time: e.target.value }))}
                    className="mt-1"
                    data-testid="schedule-time-input"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Cible</label>
                <Select value={scheduleForm.target} onValueChange={v => setScheduleForm(f => ({ ...f, target: v }))}>
                  <SelectTrigger className="mt-1" data-testid="schedule-target-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="inactive_clients">Clients inactifs (+7 jours)</SelectItem>
                    <SelectItem value="all_clients">Tous les clients</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              {abTests.length > 0 && (
                <div>
                  <label className="text-xs font-medium text-muted-foreground">Test A/B (optionnel)</label>
                  <Select value={scheduleForm.ab_test_id || 'none'} onValueChange={v => setScheduleForm(f => ({ ...f, ab_test_id: v === 'none' ? '' : v }))}>
                    <SelectTrigger className="mt-1" data-testid="schedule-ab-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">Sans A/B testing</SelectItem>
                      {abTests.map(t => (
                        <SelectItem key={t.id} value={t.id}>{t.name} ({t.variants?.length} variantes)</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              <div className="p-2.5 rounded-md bg-violet-50 border border-violet-200">
                <p className="text-[11px] text-violet-700">
                  La campagne sera envoyée automatiquement à la date et heure indiquées. Les variables dynamiques seront résolues pour chaque client.
                </p>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setScheduleTpl(null)}>Annuler</Button>
            <Button className="gap-1.5 bg-violet-600 hover:bg-violet-700" onClick={scheduleCampaign} disabled={scheduling} data-testid="confirm-schedule-btn">
              {scheduling ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CalendarClock className="w-3.5 h-3.5" />}
              Programmer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Campaigns Dashboard */}
      <CampaignsDashboard token={token} key={campaignsKey} />

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteId} onOpenChange={(open) => { if (!open) setDeleteId(null); }}>
        <DialogContent data-testid="delete-template-dialog">
          <DialogHeader>
            <DialogTitle>Confirmer la suppression</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">Ce template sera définitivement supprimé. Cette action est irréversible.</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteId(null)}>Annuler</Button>
            <Button variant="destructive" className="gap-1.5" onClick={deleteTemplate} data-testid="confirm-delete-template-btn">
              <Trash2 className="w-3.5 h-3.5" /> Supprimer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
