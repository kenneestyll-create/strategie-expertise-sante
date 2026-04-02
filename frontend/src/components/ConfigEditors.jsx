import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { CheckCircle, Save } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const TARIF_ITEMS = [
  { id: "analyse_dossier", label: "Analyse de dossier", defaultPrice: "150" },
  { id: "préparation_expertise", label: "Préparation expertise médicale", defaultPrice: "250" },
  { id: "accompagnement_mdph", label: "Accompagnement MDPH", defaultPrice: "200" },
  { id: "protection_juridique", label: "Protection juridique", defaultPrice: "200" },
  { id: "accompagnement_complet", label: "Accompagnement complet", defaultPrice: "500" },
  { id: "urgent_analyse_dossier", label: "Urgent — Analyse de dossier", defaultPrice: "250" },
  { id: "urgent_préparation_expertise", label: "Urgent — Préparation expertise", defaultPrice: "400" },
  { id: "urgent_accompagnement_mdph", label: "Urgent — Accompagnement MDPH", defaultPrice: "320" },
  { id: "urgent_accompagnement_complet", label: "Urgent — Accompagnement complet", defaultPrice: "750" },
];

export const TarifsEditor = ({ axiosConfig }) => {
  const [tarifs, setTarifs] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    axios.get(`${API}/admin/tarifs`, axiosConfig)
      .then(res => { if (res.data && typeof res.data === 'object') setTarifs(res.data); })
      .catch(() => {});
  }, []);

  const updateField = (id, field, value) => {
    setTarifs(prev => ({
      ...prev,
      [id]: { ...prev[id], [field]: value }
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/admin/tarifs`, tarifs, axiosConfig);
      toast.success('Tarifs mis à jour');
    } catch { toast.error('Erreur lors de la sauvegarde'); }
    setSaving(false);
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3">
        {TARIF_ITEMS.map(item => (
          <div key={item.id} className="flex items-center gap-3 p-3 rounded-lg border border-border/50 bg-muted/20" data-testid={`tarif-${item.id}`}>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-foreground truncate">{item.label}</p>
              <p className="text-[10px] text-muted-foreground">Par défaut : {item.defaultPrice} EUR</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex flex-col gap-1">
                <label className="text-[10px] text-muted-foreground">Prix EUR</label>
                <input
                  type="number"
                  min="0"
                  className="w-20 px-2 py-1 rounded border bg-background text-foreground text-xs"
                  placeholder={item.defaultPrice}
                  value={tarifs[item.id]?.price || ''}
                  onChange={e => updateField(item.id, 'price', e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-[10px] text-muted-foreground">Badge promo</label>
                <input
                  type="text"
                  className="w-28 px-2 py-1 rounded border bg-background text-foreground text-xs"
                  placeholder="Ex: -20%"
                  value={tarifs[item.id]?.badge || ''}
                  onChange={e => updateField(item.id, 'badge', e.target.value)}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
      <Button size="sm" className="gap-2" onClick={handleSave} disabled={saving} data-testid="tarifs-save-btn">
        <Save className="w-3 h-3" /> {saving ? 'Enregistrement...' : 'Enregistrer les tarifs'}
      </Button>
    </div>
  );
};

const CHIFFRE_DEFAULTS = [
  { prefix: "Plus de", value: 700000, unit: "", suffix: "accidents du travail par an en France", source: "CNAM" },
  { prefix: "Environ", value: 50000, unit: "", suffix: "maladies professionnelles reconnues chaque année", source: "CNAM" },
  { prefix: "Près de", value: 12, unit: " millions", suffix: "de personnes en situation de handicap", source: "INSEE" },
  { prefix: "Plus de", value: 300000, unit: "", suffix: "nouvelles demandes MDPH chaque année", source: "CNSA" },
];

export const ChiffresClesEditor = ({ axiosConfig }) => {
  const [chiffres, setChiffres] = useState(CHIFFRE_DEFAULTS);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    axios.get(`${API}/admin/chiffres-cles`, axiosConfig)
      .then(res => {
        if (res.data && Array.isArray(res.data) && res.data.length === 4) {
          setChiffres(res.data);
        }
      })
      .catch(() => {});
  }, []);

  const updateChiffre = (index, field, value) => {
    setChiffres(prev => prev.map((c, i) => i === index ? { ...c, [field]: field === 'value' ? Number(value) || 0 : value } : c));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/admin/chiffres-cles`, { chiffres }, axiosConfig);
      toast.success('Chiffres clés mis à jour');
    } catch { toast.error('Erreur lors de la sauvegarde'); }
    setSaving(false);
  };

  return (
    <div className="space-y-4">
      {chiffres.map((c, i) => (
        <div key={i} className="p-3 rounded-lg border border-border/50 bg-muted/20 space-y-2" data-testid={`chiffre-cle-${i}`}>
          <p className="text-xs font-semibold text-foreground">Chiffre {i + 1}</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div>
              <label className="text-[10px] text-muted-foreground">Préfixe</label>
              <input className="w-full px-2 py-1 rounded border bg-background text-foreground text-xs" value={c.prefix} onChange={e => updateChiffre(i, 'prefix', e.target.value)} />
            </div>
            <div>
              <label className="text-[10px] text-muted-foreground">Valeur</label>
              <input type="number" className="w-full px-2 py-1 rounded border bg-background text-foreground text-xs" value={c.value} onChange={e => updateChiffre(i, 'value', e.target.value)} />
            </div>
            <div>
              <label className="text-[10px] text-muted-foreground">Unité</label>
              <input className="w-full px-2 py-1 rounded border bg-background text-foreground text-xs" placeholder="ex: millions" value={c.unit} onChange={e => updateChiffre(i, 'unit', e.target.value)} />
            </div>
            <div>
              <label className="text-[10px] text-muted-foreground">Source</label>
              <input className="w-full px-2 py-1 rounded border bg-background text-foreground text-xs" value={c.source} onChange={e => updateChiffre(i, 'source', e.target.value)} />
            </div>
          </div>
          <div>
            <label className="text-[10px] text-muted-foreground">Texte descriptif</label>
            <input className="w-full px-2 py-1 rounded border bg-background text-foreground text-xs" value={c.suffix} onChange={e => updateChiffre(i, 'suffix', e.target.value)} />
          </div>
        </div>
      ))}
      <Button size="sm" className="gap-2" onClick={handleSave} disabled={saving} data-testid="chiffres-cles-save-btn">
        <Save className="w-3 h-3" /> {saving ? 'Enregistrement...' : 'Enregistrer les chiffres'}
      </Button>
    </div>
  );
};
