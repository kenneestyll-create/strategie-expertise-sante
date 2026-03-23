import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import {
  Plus, Pencil, Trash2, Star, Eye, MousePointerClick,
  Volume2, Search, Loader2, CheckCircle, XCircle, Calendar
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CATEGORIES = ["droits", "expertise", "indemnisation", "emploi", "demarches", "strategie", "actualite"];
const LINK_OPTIONS = [
  { value: "/calculatrice-ipp", label: "Calculatrice IPP" },
  { value: "/dossier-express", label: "Dossier Express IA" },
  { value: "/ressources", label: "Ressources" },
  { value: "/simulateur", label: "StrategiIA" },
  { value: "/contact", label: "Contact" },
  { value: "/accident-travail-maladie-professionnelle", label: "AT / MP" },
];

const EMPTY_FORM = {
  text: '', category: 'droits', link: '/ressources', link_label: 'En savoir plus',
  start_date: '', end_date: '', active: true, priority: false, tts_enabled: true,
};

const catColors = {
  droits: 'bg-blue-500/20 text-blue-400',
  expertise: 'bg-purple-500/20 text-purple-400',
  indemnisation: 'bg-amber-500/20 text-amber-400',
  emploi: 'bg-green-500/20 text-green-400',
  demarches: 'bg-cyan-500/20 text-cyan-400',
  strategie: 'bg-rose-500/20 text-rose-400',
  actualite: 'bg-orange-500/20 text-orange-400',
};

export const AdminConseilsStrate = ({ axiosConfig }) => {
  const [conseils, setConseils] = useState([]);
  const [stats, setStats] = useState({ total: 0, active: 0, total_views: 0, total_clicks: 0 });
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [catFilter, setCatFilter] = useState('all');

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  // Preview
  const [previewText, setPreviewText] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Delete
  const [deleteId, setDeleteId] = useState(null);

  const fetchConseils = useCallback(async () => {
    try {
      setLoading(true);
      const [listRes, statsRes] = await Promise.all([
        axios.get(`${API}/conseils/admin/list`, axiosConfig),
        axios.get(`${API}/conseils/admin/stats`, axiosConfig),
      ]);
      setConseils(listRes.data);
      setStats(statsRes.data);
    } catch {
      toast.error("Erreur de chargement des conseils");
    } finally {
      setLoading(false);
    }
  }, [axiosConfig]);

  useEffect(() => { fetchConseils(); }, [fetchConseils]);

  const openCreate = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setShowForm(true);
  };

  const openEdit = (c) => {
    setEditingId(c.id);
    setForm({
      text: c.text, category: c.category, link: c.link, link_label: c.link_label,
      start_date: c.start_date || '', end_date: c.end_date || '',
      active: c.active, priority: c.priority, tts_enabled: c.tts_enabled,
    });
    setShowForm(true);
  };

  const handleSave = async () => {
    if (!form.text.trim() || form.text.length < 5) {
      toast.error("Le texte doit contenir au moins 5 caracteres");
      return;
    }
    if (form.text.length > 200) {
      toast.error("Le texte ne doit pas depasser 200 caracteres");
      return;
    }
    try {
      setSaving(true);
      const payload = {
        ...form,
        start_date: form.start_date || null,
        end_date: form.end_date || null,
      };
      if (editingId) {
        await axios.put(`${API}/conseils/admin/${editingId}`, payload, axiosConfig);
        toast.success("Conseil mis a jour");
      } else {
        await axios.post(`${API}/conseils/admin/create`, payload, axiosConfig);
        toast.success("Conseil cree");
      }
      setShowForm(false);
      fetchConseils();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await axios.delete(`${API}/conseils/admin/${deleteId}`, axiosConfig);
      toast.success("Conseil supprime");
      setDeleteId(null);
      fetchConseils();
    } catch {
      toast.error("Erreur de suppression");
    }
  };

  const handleHighlight = async (id) => {
    try {
      await axios.post(`${API}/conseils/admin/${id}/highlight`, {}, axiosConfig);
      toast.success("Conseil mis en avant pour aujourd'hui !");
      fetchConseils();
    } catch {
      toast.error("Erreur");
    }
  };

  const previewTTS = (text) => {
    if (typeof speechSynthesis === 'undefined') return;
    speechSynthesis.cancel();
    setPreviewText(text);
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'fr-FR';
    utterance.rate = 0.9;
    const voices = speechSynthesis.getVoices();
    const frVoice = voices.find(v => v.lang === 'fr-FR') || voices.find(v => v.lang.startsWith('fr'));
    if (frVoice) utterance.voice = frVoice;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => { setIsSpeaking(false); setPreviewText(null); };
    utterance.onerror = () => { setIsSpeaking(false); setPreviewText(null); };
    speechSynthesis.speak(utterance);
  };

  const filtered = conseils.filter(c => {
    const matchSearch = c.text.toLowerCase().includes(searchTerm.toLowerCase());
    const matchCat = catFilter === 'all' || c.category === catFilter;
    return matchSearch && matchCat;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="admin-conseils-tab">
      {/* Stats KPI */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card><CardContent className="py-4 px-5">
          <p className="text-xs text-muted-foreground uppercase">Total conseils</p>
          <p className="text-2xl font-bold mt-1">{stats.total}</p>
        </CardContent></Card>
        <Card><CardContent className="py-4 px-5">
          <p className="text-xs text-muted-foreground uppercase">Actifs</p>
          <p className="text-2xl font-bold mt-1 text-green-600">{stats.active}</p>
        </CardContent></Card>
        <Card><CardContent className="py-4 px-5">
          <p className="text-xs text-muted-foreground uppercase">Vues totales</p>
          <p className="text-2xl font-bold mt-1 flex items-center gap-1"><Eye className="w-4 h-4 text-muted-foreground" />{stats.total_views}</p>
        </CardContent></Card>
        <Card><CardContent className="py-4 px-5">
          <p className="text-xs text-muted-foreground uppercase">Clics totaux</p>
          <p className="text-2xl font-bold mt-1 flex items-center gap-1"><MousePointerClick className="w-4 h-4 text-muted-foreground" />{stats.total_clicks}</p>
        </CardContent></Card>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <div className="flex gap-2 flex-1 w-full sm:w-auto">
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-9"
              data-testid="conseils-search"
            />
          </div>
          <Select value={catFilter} onValueChange={setCatFilter}>
            <SelectTrigger className="w-40" data-testid="conseils-cat-filter">
              <SelectValue placeholder="Categorie" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toutes</SelectItem>
              {CATEGORIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <Button onClick={openCreate} className="gap-2" data-testid="conseils-add-btn">
          <Plus className="w-4 h-4" /> Ajouter un conseil
        </Button>
      </div>

      {/* Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left">
                <th className="p-3 font-medium">Texte</th>
                <th className="p-3 font-medium w-24">Cat.</th>
                <th className="p-3 font-medium w-20 text-center">Actif</th>
                <th className="p-3 font-medium w-20 text-center">Priorite</th>
                <th className="p-3 font-medium w-16 text-center">Vues</th>
                <th className="p-3 font-medium w-16 text-center">Clics</th>
                <th className="p-3 font-medium w-24">Dates</th>
                <th className="p-3 font-medium w-40 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(c => (
                <tr key={c.id} className="border-b hover:bg-muted/30 transition-colors" data-testid={`conseil-row-${c.id}`}>
                  <td className="p-3 max-w-xs">
                    <p className="truncate">{c.text}</p>
                  </td>
                  <td className="p-3">
                    <Badge className={catColors[c.category] || 'bg-gray-500/20 text-gray-400'} variant="outline">
                      {c.category}
                    </Badge>
                  </td>
                  <td className="p-3 text-center">
                    {c.active ? <CheckCircle className="w-4 h-4 text-green-500 mx-auto" /> : <XCircle className="w-4 h-4 text-red-400 mx-auto" />}
                  </td>
                  <td className="p-3 text-center">
                    {c.priority && <Star className="w-4 h-4 text-amber-400 fill-amber-400 mx-auto" />}
                  </td>
                  <td className="p-3 text-center text-muted-foreground">{c.views}</td>
                  <td className="p-3 text-center text-muted-foreground">{c.clicks}</td>
                  <td className="p-3 text-xs text-muted-foreground">
                    {c.start_date && <span>{c.start_date}</span>}
                    {c.end_date && <span className="block">{c.end_date}</span>}
                  </td>
                  <td className="p-3 text-right">
                    <div className="flex items-center gap-1 justify-end">
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => previewTTS(c.text)}
                        disabled={isSpeaking && previewText === c.text}
                        title="Preview TTS"
                        data-testid={`conseil-preview-${c.id}`}
                      >
                        <Volume2 className={`w-4 h-4 ${isSpeaking && previewText === c.text ? 'text-amber-400 animate-pulse' : ''}`} />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => handleHighlight(c.id)}
                        title="Mettre en avant aujourd'hui"
                        data-testid={`conseil-highlight-${c.id}`}
                      >
                        <Star className={`w-4 h-4 ${c.priority ? 'text-amber-400 fill-amber-400' : ''}`} />
                      </Button>
                      <Button size="icon" variant="ghost" onClick={() => openEdit(c)} title="Modifier" data-testid={`conseil-edit-${c.id}`}>
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button size="icon" variant="ghost" onClick={() => setDeleteId(c.id)} title="Supprimer" data-testid={`conseil-delete-${c.id}`}>
                        <Trash2 className="w-4 h-4 text-red-400" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={8} className="p-8 text-center text-muted-foreground">Aucun conseil trouve</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="max-w-lg" data-testid="conseil-form-dialog">
          <DialogHeader>
            <DialogTitle>{editingId ? 'Modifier le conseil' : 'Nouveau conseil'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Texte du conseil *</label>
              <Textarea
                value={form.text}
                onChange={e => setForm(f => ({ ...f, text: e.target.value }))}
                placeholder="Ex: Vous disposez de 2 ans pour declarer..."
                maxLength={200}
                rows={3}
                data-testid="conseil-form-text"
              />
              <p className="text-xs text-muted-foreground mt-1">{form.text.length}/200</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Categorie</label>
                <Select value={form.category} onValueChange={v => setForm(f => ({ ...f, category: v }))}>
                  <SelectTrigger data-testid="conseil-form-category">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CATEGORIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Lien d'action</label>
                <Select value={form.link} onValueChange={v => setForm(f => ({ ...f, link: v }))}>
                  <SelectTrigger data-testid="conseil-form-link">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {LINK_OPTIONS.map(l => <SelectItem key={l.value} value={l.value}>{l.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Label du bouton</label>
              <Input
                value={form.link_label}
                onChange={e => setForm(f => ({ ...f, link_label: e.target.value }))}
                data-testid="conseil-form-link-label"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block flex items-center gap-1"><Calendar className="w-3 h-3" /> Date debut</label>
                <Input type="date" value={form.start_date} onChange={e => setForm(f => ({ ...f, start_date: e.target.value }))} data-testid="conseil-form-start-date" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block flex items-center gap-1"><Calendar className="w-3 h-3" /> Date fin</label>
                <Input type="date" value={form.end_date} onChange={e => setForm(f => ({ ...f, end_date: e.target.value }))} data-testid="conseil-form-end-date" />
              </div>
            </div>
            <div className="flex items-center gap-6">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={form.active} onChange={e => setForm(f => ({ ...f, active: e.target.checked }))} className="rounded" data-testid="conseil-form-active" />
                <span className="text-sm">Actif</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={form.priority} onChange={e => setForm(f => ({ ...f, priority: e.target.checked }))} className="rounded" data-testid="conseil-form-priority" />
                <span className="text-sm">Prioritaire aujourd'hui</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={form.tts_enabled} onChange={e => setForm(f => ({ ...f, tts_enabled: e.target.checked }))} className="rounded" data-testid="conseil-form-tts" />
                <span className="text-sm">TTS actif</span>
              </label>
            </div>
          </div>
          <DialogFooter className="gap-2">
            {form.text.length >= 5 && (
              <Button variant="outline" onClick={() => previewTTS(form.text)} className="gap-1" data-testid="conseil-form-preview-btn">
                <Volume2 className="w-4 h-4" /> Preview
              </Button>
            )}
            <Button variant="outline" onClick={() => setShowForm(false)}>Annuler</Button>
            <Button onClick={handleSave} disabled={saving} className="gap-1" data-testid="conseil-form-save-btn">
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
              {editingId ? 'Mettre a jour' : 'Creer'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <Dialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <DialogContent data-testid="conseil-delete-dialog">
          <DialogHeader>
            <DialogTitle>Supprimer ce conseil ?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">Cette action est irreversible.</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteId(null)}>Annuler</Button>
            <Button variant="destructive" onClick={handleDelete} data-testid="conseil-confirm-delete">Supprimer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
