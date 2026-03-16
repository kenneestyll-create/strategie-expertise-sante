import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import {
  FileText, Plus, Copy, Trash2, Eye, Save, Loader2, Pencil, X, Check, RefreshCw
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

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

  const headers = { Authorization: `Bearer ${token}` };

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/admin/email-templates`, { headers });
      setTemplates(res.data.templates || []);
    } catch {
      toast.error('Erreur lors du chargement des templates');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchTemplates(); }, [fetchTemplates]);

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
        prenom: 'Marie', completeness_pct: 42
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
            Créez et modifiez vos modèles d'emails sans toucher au code
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
                        <Input
                          value={editForm.subject}
                          onChange={e => setEditForm(f => ({ ...f, subject: e.target.value }))}
                          className="mt-1 text-sm"
                          data-testid={`edit-subject-${tpl.name}`}
                        />
                      </div>
                      <div>
                        <label className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium">Texte d'introduction</label>
                        <Textarea
                          value={editForm.intro}
                          onChange={e => setEditForm(f => ({ ...f, intro: e.target.value }))}
                          className="mt-1 text-sm min-h-[60px]"
                          data-testid={`edit-intro-${tpl.name}`}
                        />
                      </div>
                      <div>
                        <label className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium">Texte de motivation</label>
                        <Textarea
                          value={editForm.motivation}
                          onChange={e => setEditForm(f => ({ ...f, motivation: e.target.value }))}
                          className="mt-1 text-sm min-h-[60px]"
                          data-testid={`edit-motivation-${tpl.name}`}
                        />
                      </div>
                      <div>
                        <label className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium">Texte du bouton CTA</label>
                        <Input
                          value={editForm.cta_text}
                          onChange={e => setEditForm(f => ({ ...f, cta_text: e.target.value }))}
                          className="mt-1 text-sm"
                          data-testid={`edit-cta-${tpl.name}`}
                        />
                      </div>
                      <div className="flex justify-end">
                        <Button size="sm" variant="outline" className="gap-1.5 text-xs" onClick={() => loadPreview(tpl)} data-testid={`preview-edit-${tpl.name}`}>
                          <Eye className="w-3.5 h-3.5" /> Aperçu en direct
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="grid gap-2">
                      <div className="flex items-start gap-2">
                        <span className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium min-w-[60px] pt-0.5">Sujet</span>
                        <p className="text-sm text-foreground">{tpl.subject}</p>
                      </div>
                      <div className="flex items-start gap-2">
                        <span className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium min-w-[60px] pt-0.5">Intro</span>
                        <p className="text-sm text-muted-foreground line-clamp-2">{tpl.intro}</p>
                      </div>
                      <div className="flex items-start gap-2">
                        <span className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium min-w-[60px] pt-0.5">CTA</span>
                        <Badge variant="outline" className="text-xs">{tpl.cta_text}</Badge>
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
              <Eye className="w-4 h-4 text-blue-500" /> Aperçu du template
            </DialogTitle>
          </DialogHeader>
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
        <DialogContent className="max-w-lg" data-testid="new-template-dialog">
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
              <Input value={newForm.subject} onChange={e => setNewForm(f => ({ ...f, subject: e.target.value }))} placeholder="Objet de l'email" className="mt-1" data-testid="new-tpl-subject" />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">Texte d'introduction</label>
              <Textarea value={newForm.intro} onChange={e => setNewForm(f => ({ ...f, intro: e.target.value }))} placeholder="Introduction du message..." className="mt-1 min-h-[60px]" data-testid="new-tpl-intro" />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">Texte de motivation</label>
              <Textarea value={newForm.motivation} onChange={e => setNewForm(f => ({ ...f, motivation: e.target.value }))} placeholder="Texte de motivation..." className="mt-1 min-h-[60px]" data-testid="new-tpl-motivation" />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">Texte du bouton CTA</label>
              <Input value={newForm.cta_text} onChange={e => setNewForm(f => ({ ...f, cta_text: e.target.value }))} placeholder="Compléter mon dossier" className="mt-1" data-testid="new-tpl-cta" />
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
