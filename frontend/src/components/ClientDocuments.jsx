import { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Upload, FileText, Image, Trash2, Download, Search, Filter,
  FolderOpen, Clock, CheckCircle, AlertTriangle, RefreshCw,
  ChevronDown, ChevronUp, Eye, X, Shield, Calendar, Tag,
  Building2, ScanLine, Pencil
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { DocumentUploader } from '@/components/DocumentUploader';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CATEGORIES = {
  at: { label: 'Accident du travail', color: 'bg-blue-100 text-blue-700 border-blue-200' },
  mp: { label: 'Maladie professionnelle', color: 'bg-purple-100 text-purple-700 border-purple-200' },
  mdph: { label: 'MDPH / AAH', color: 'bg-amber-100 text-amber-700 border-amber-200' },
  expertise: { label: 'Expertises médicales', color: 'bg-red-100 text-red-700 border-red-200' },
  cpam: { label: 'Courriers CPAM', color: 'bg-green-100 text-green-700 border-green-200' },
  tribunal: { label: 'Documents juridiques', color: 'bg-slate-100 text-slate-700 border-slate-200' },
  autre: { label: 'Autres', color: 'bg-gray-100 text-gray-600 border-gray-200' },
};

const STATUSES = {
  en_attente: { label: 'En attente', icon: Clock, color: 'bg-amber-100 text-amber-700' },
  valide: { label: 'Validé', icon: Shield, color: 'bg-green-100 text-green-700' },
  illisible: { label: 'Illisible', icon: AlertTriangle, color: 'bg-red-100 text-red-700' },
  corrige: { label: 'Corrigé', icon: RefreshCw, color: 'bg-blue-100 text-blue-700' },
};

const formatDate = (d) => d ? new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }) : '';

const DocStatusBadge = ({ status }) => {
  const s = STATUSES[status] || STATUSES.en_attente;
  return (
    <Badge variant="outline" className={`text-[10px] gap-0.5 ${s.color}`} data-testid={`doc-status-${status}`}>
      <s.icon className="w-2.5 h-2.5" />{s.label}
    </Badge>
  );
};

const CategoryBadge = ({ category }) => {
  const c = CATEGORIES[category] || CATEGORIES.autre;
  return <Badge variant="outline" className={`text-[10px] ${c.color}`}>{c.label}</Badge>;
};

export const ClientDocuments = ({ token, onDocumentsChange }) => {
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState({ total: 0, by_category: {}, by_status: {} });
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('list'); // list, category
  const [filterCat, setFilterCat] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [search, setSearch] = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const [uploadFiles, setUploadFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [lastOcr, setLastOcr] = useState(null);
  const [editTags, setEditTags] = useState(null);
  const [editCategory, setEditCategory] = useState('');

  const headers = { Authorization: `Bearer ${token}` };

  const fetchDocs = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (filterCat) params.category = filterCat;
      if (filterStatus) params.status = filterStatus;
      if (search) params.search = search;
      const res = await axios.get(`${API}/client/documents`, { headers, params });
      setDocuments(res.data.documents);
      setStats({ total: res.data.total, by_category: res.data.by_category, by_status: res.data.by_status });
    } catch {
      toast.error('Erreur chargement documents');
    } finally { setLoading(false); }
  }, [token, filterCat, filterStatus, search]);

  useState(() => { fetchDocs(); }, []);

  const handleUpload = async () => {
    if (uploadFiles.length === 0) return;
    setUploading(true);

    for (const file of uploadFiles) {
      try {
        const base64 = await fileToBase64(file);
        const ocrFields = lastOcr?.fields || {};
        // Auto-determine category from AI extraction
        let autoCategory = '';
        if (ocrFields.type_dossier_detected?.length > 0) {
          autoCategory = ocrFields.type_dossier_detected[0];
        }
        await axios.post(`${API}/client/documents`, {
          filename: file.name,
          file_data: base64,
          mime_type: file.type,
          size: file.size,
          ocr_fields: ocrFields,
          tags: {
            categorie: autoCategory,
            organisme: ocrFields.organisme || '',
            type_document: autoCategory || 'autre',
          },
        }, { headers });
      } catch {
        toast.error(`Erreur upload: ${file.name}`);
      }
    }

    toast.success(`${uploadFiles.length} document(s) uploadé(s) et analysé(s)`, {
      description: 'Votre score de dossier est en cours de mise à jour...',
    });
    setUploadFiles([]);
    setShowUpload(false);
    setLastOcr(null);
    setUploading(false);
    fetchDocs();
    if (onDocumentsChange) onDocumentsChange();
  };

  const deleteDoc = async (docId) => {
    if (!window.confirm('Supprimer ce document ?')) return;
    try {
      await axios.delete(`${API}/client/documents/${docId}`, { headers });
      toast.success('Document supprimé');
      fetchDocs();
      if (onDocumentsChange) onDocumentsChange();
    } catch { toast.error('Erreur suppression'); }
  };

  const updateDoc = async (docId, data) => {
    try {
      await axios.patch(`${API}/client/documents/${docId}`, data, { headers });
      toast.success('Document mis à jour');
      setEditTags(null);
      fetchDocs();
    } catch { toast.error('Erreur mise à jour'); }
  };

  const downloadDoc = async (docId, filename) => {
    try {
      const res = await axios.get(`${API}/client/documents/${docId}/download`, { 
        headers, 
        responseType: 'blob' 
      });
      const blobUrl = URL.createObjectURL(res.data);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(blobUrl);
    } catch { toast.error('Erreur téléchargement'); }
  };

  // Group by category for category view
  const grouped = {};
  documents.forEach(d => {
    const cat = d.category || 'autre';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(d);
  });

  return (
    <div className="space-y-4" data-testid="client-documents">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Card><CardContent className="p-3 text-center">
          <p className="text-xl font-bold">{stats.total}</p>
          <p className="text-[10px] text-muted-foreground uppercase">Documents</p>
        </CardContent></Card>
        <Card><CardContent className="p-3 text-center">
          <p className="text-xl font-bold text-green-600">{stats.by_status?.valide || 0}</p>
          <p className="text-[10px] text-muted-foreground uppercase">Validés</p>
        </CardContent></Card>
        <Card><CardContent className="p-3 text-center">
          <p className="text-xl font-bold text-amber-600">{stats.by_status?.en_attente || 0}</p>
          <p className="text-[10px] text-muted-foreground uppercase">En attente</p>
        </CardContent></Card>
        <Card><CardContent className="p-3 text-center">
          <p className="text-xl font-bold text-red-500">{stats.by_status?.illisible || 0}</p>
          <p className="text-[10px] text-muted-foreground uppercase">Illisibles</p>
        </CardContent></Card>
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-2">
        <Button size="sm" className="gap-1.5 text-xs rounded-lg" onClick={() => setShowUpload(!showUpload)} data-testid="upload-doc-btn">
          <Upload className="w-3.5 h-3.5" /> Ajouter un document
        </Button>
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Rechercher..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && fetchDocs()}
              className="pl-8 h-8 text-xs"
              data-testid="doc-search"
            />
          </div>
        </div>
        <select value={filterCat} onChange={e => { setFilterCat(e.target.value); setTimeout(fetchDocs, 100); }} className="h-8 text-xs border rounded-lg px-2 bg-background" data-testid="doc-filter-category">
          <option value="">Toutes catégories</option>
          {Object.entries(CATEGORIES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        <select value={filterStatus} onChange={e => { setFilterStatus(e.target.value); setTimeout(fetchDocs, 100); }} className="h-8 text-xs border rounded-lg px-2 bg-background" data-testid="doc-filter-status">
          <option value="">Tous statuts</option>
          {Object.entries(STATUSES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        <div className="flex gap-1 bg-muted rounded-lg p-0.5">
          <button onClick={() => setView('list')} className={`px-2 py-1 text-[10px] rounded ${view === 'list' ? 'bg-background shadow font-medium' : 'text-muted-foreground'}`} data-testid="view-list">Liste</button>
          <button onClick={() => setView('category')} className={`px-2 py-1 text-[10px] rounded ${view === 'category' ? 'bg-background shadow font-medium' : 'text-muted-foreground'}`} data-testid="view-category">Catégories</button>
        </div>
      </div>

      {/* Upload Panel */}
      {showUpload && (
        <Card className="border-accent/20" data-testid="doc-upload-panel">
          <CardContent className="p-4 space-y-3">
            <DocumentUploader
              files={uploadFiles}
              onFilesChange={setUploadFiles}
              maxFiles={5}
              showChecklist={uploadFiles.length > 0}
              showGuide={false}
              enableOCR={true}
              onOcrResult={(result) => setLastOcr(result)}
            />
            {uploadFiles.length > 0 && (
              <div className="flex gap-2">
                <Button size="sm" className="gap-1.5 text-xs" onClick={handleUpload} disabled={uploading} data-testid="confirm-upload-btn">
                  {uploading ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Upload className="w-3 h-3" />}
                  Enregistrer {uploadFiles.length} document(s)
                </Button>
                <Button size="sm" variant="ghost" className="text-xs" onClick={() => { setShowUpload(false); setUploadFiles([]); setLastOcr(null); }}>Annuler</Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Document List */}
      {loading ? (
        <div className="text-center py-12 text-muted-foreground text-sm">Chargement...</div>
      ) : documents.length === 0 ? (
        <Card><CardContent className="p-12 text-center">
          <FolderOpen className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="font-medium">Aucun document</p>
          <p className="text-sm text-muted-foreground mt-1">Ajoutez vos premiers documents pour commencer votre historique.</p>
        </CardContent></Card>
      ) : view === 'list' ? (
        /* Chronological List View */
        <div className="space-y-2" data-testid="docs-list-view">
          {documents.map(doc => (
            <DocumentCard key={doc.id} doc={doc} onDelete={deleteDoc} onDownload={downloadDoc} onEdit={(d) => { setEditTags(d); setEditCategory(d.category || 'autre'); }} />
          ))}
        </div>
      ) : (
        /* Category View */
        <div className="space-y-6" data-testid="docs-category-view">
          {Object.entries(CATEGORIES).map(([catKey, catInfo]) => {
            const catDocs = grouped[catKey];
            if (!catDocs || catDocs.length === 0) return null;
            return (
              <div key={catKey}>
                <div className="flex items-center gap-2 mb-2">
                  <FolderOpen className="w-4 h-4 text-accent" />
                  <h3 className="text-sm font-semibold">{catInfo.label}</h3>
                  <Badge variant="outline" className="text-[9px]">{catDocs.length}</Badge>
                </div>
                <div className="space-y-2 ml-6">
                  {catDocs.map(doc => (
                    <DocumentCard key={doc.id} doc={doc} compact onDelete={deleteDoc} onDownload={downloadDoc} onEdit={(d) => { setEditTags(d); setEditCategory(d.category || 'autre'); }} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Edit Tags Modal */}
      {editTags && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50" onClick={() => setEditTags(null)}>
          <Card className="w-full max-w-md" onClick={e => e.stopPropagation()} data-testid="edit-tags-modal">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2"><Tag className="w-4 h-4 text-accent" />Modifier les tags</CardTitle>
                <Button variant="ghost" size="icon" className="w-6 h-6" onClick={() => setEditTags(null)}><X className="w-4 h-4" /></Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <label className="text-xs font-medium">Catégorie</label>
                <select value={editCategory} onChange={e => setEditCategory(e.target.value)} className="w-full h-8 text-sm border rounded-lg px-2 mt-1 bg-background" data-testid="edit-category">
                  {Object.entries(CATEGORIES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs font-medium">Organisme</label>
                <Input defaultValue={editTags.tags?.organisme || ''} className="h-8 text-sm mt-1" data-testid="edit-organisme" id="edit-organisme" />
              </div>
              <div>
                <label className="text-xs font-medium">Date du document</label>
                <Input defaultValue={editTags.tags?.date_document || ''} className="h-8 text-sm mt-1" placeholder="JJ/MM/AAAA" data-testid="edit-date" id="edit-date" />
              </div>
              <div className="flex gap-2 pt-2">
                <Button size="sm" className="gap-1 text-xs" onClick={() => {
                  const organisme = document.getElementById('edit-organisme')?.value || '';
                  const date_document = document.getElementById('edit-date')?.value || '';
                  updateDoc(editTags.id, { category: editCategory, tags: { organisme, date_document } });
                }} data-testid="save-tags-btn">
                  <CheckCircle className="w-3 h-3" /> Enregistrer
                </Button>
                <Button size="sm" variant="ghost" className="text-xs" onClick={() => setEditTags(null)}>Annuler</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

const DocumentCard = ({ doc, compact = false, onDelete, onDownload, onEdit }) => {
  const isImage = doc.mime_type?.startsWith('image/');
  const Icon = isImage ? Image : FileText;
  const ext = doc.filename?.split('.').pop()?.toUpperCase() || '?';

  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg border border-border bg-card hover:bg-muted/30 transition-colors group ${compact ? 'py-2' : ''}`} data-testid={`doc-card-${doc.id}`}>
      <div className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
        <Icon className="w-4 h-4 text-muted-foreground" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-sm font-medium truncate">{doc.filename}</span>
          <Badge variant="outline" className="text-[8px] px-1">{ext}</Badge>
          <DocStatusBadge status={doc.status} />
          <CategoryBadge category={doc.category} />
          {doc.status === 'valide' && <Badge className="bg-green-100 text-green-700 border-green-200 text-[9px] gap-0.5 px-1"><Shield className="w-2 h-2" />Qualité vérifiée</Badge>}
        </div>
        <div className="flex items-center gap-3 mt-0.5 text-[10px] text-muted-foreground">
          <span>{formatDate(doc.created_at)}</span>
          {doc.tags?.organisme && <span className="flex items-center gap-0.5"><Building2 className="w-2.5 h-2.5" />{doc.tags.organisme}</span>}
          {doc.tags?.date_document && <span className="flex items-center gap-0.5"><Calendar className="w-2.5 h-2.5" />{doc.tags.date_document}</span>}
          {doc.versions?.length > 1 && <span>v{doc.versions.length}</span>}
        </div>
      </div>
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button variant="ghost" size="icon" className="w-7 h-7" onClick={() => onEdit(doc)} title="Modifier tags" data-testid={`edit-doc-${doc.id}`}><Pencil className="w-3 h-3" /></Button>
        <Button variant="ghost" size="icon" className="w-7 h-7" onClick={() => onDownload(doc.id, doc.filename)} title="Télécharger" data-testid={`download-doc-${doc.id}`}><Download className="w-3 h-3" /></Button>
        <Button variant="ghost" size="icon" className="w-7 h-7 text-muted-foreground hover:text-destructive" onClick={() => onDelete(doc.id)} title="Supprimer" data-testid={`delete-doc-${doc.id}`}><Trash2 className="w-3 h-3" /></Button>
      </div>
    </div>
  );
};

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
