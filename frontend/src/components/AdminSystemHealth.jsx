import { useState, useEffect } from 'react';
import axios from 'axios';
import { FileText, Mail, Activity, Database, HardDrive, RefreshCw } from 'lucide-react';
import { safeStorage } from '../utils/safeStorage';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const COMPONENTS = [
  { key: 'pdf', label: 'PDF', Icon: FileText },
  { key: 'email', label: 'Email', Icon: Mail },
  { key: 'api', label: 'API', Icon: Activity },
  { key: 'database', label: 'Base de données', Icon: Database },
  { key: 'storage', label: 'Stockage', Icon: HardDrive },
];

export const AdminSystemHealth = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(false);

  const load = () => {
    const token = safeStorage.get('admin_token');
    axios
      .get(`${API}/admin/system-health`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => { setData(r.data); setError(false); })
      .catch(() => setError(true));
  };

  useEffect(() => { load(); }, []);

  if (error) {
    return (
      <div className="mb-6 p-3 rounded-xl border border-red-300 bg-red-50 text-red-700 text-xs font-medium" data-testid="system-health-error">
        ⚠ Supervision indisponible — impossible de contacter /api/admin/system-health
      </div>
    );
  }
  if (!data) return null;

  const comps = data.components || {};
  const hasCritical = COMPONENTS.some(({ key }) => comps[key] && !comps[key].ok);

  return (
    <div
      className={`mb-6 p-3 rounded-xl border ${hasCritical ? 'border-red-300 bg-red-50/60' : 'border-border/60 bg-card/80'}`}
      data-testid="system-health-strip"
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold mr-1">
          État système{data.environment === 'preview' ? ' · preview' : ''}
        </span>
        {COMPONENTS.map(({ key, label, Icon }) => {
          const c = comps[key];
          const ok = c ? c.ok : false;
          const title = c ? `${c.detail}${c.last ? ` — dernier: ${c.last.ok ? 'OK' : 'ÉCHEC'} (${c.last.detail || ''})` : ''}` : 'inconnu';
          return (
            <span
              key={key}
              title={title}
              data-testid={`health-${key}`}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${
                ok
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-red-100 text-red-700 border-red-300 animate-pulse'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${ok ? 'bg-emerald-500' : 'bg-red-500'}`} />
              <Icon className="w-3 h-3" />
              {label}
            </span>
          );
        })}
        <button
          onClick={load}
          className="ml-auto text-muted-foreground hover:text-foreground transition-colors"
          title="Rafraîchir"
          data-testid="health-refresh-btn"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>
      {hasCritical && (
        <p className="mt-2 text-xs text-red-700 font-medium" data-testid="health-critical-msg">
          ⚠ Anomalie critique détectée — survolez le badge rouge pour le détail.
        </p>
      )}
    </div>
  );
};

export default AdminSystemHealth;
