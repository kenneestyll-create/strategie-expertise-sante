import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { QrCode } from 'lucide-react';
import { safeStorage } from '../utils/safeStorage';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

/**
 * Mini indicateur de tracking QR par PDF source.
 * Affiche le nombre de contacts arrivés via les QR codes des PDFs
 * (Dossier Express IA, StratégiIA, Auto-diagnostic).
 */
export const AdminQRStats = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = safeStorage.get('admin_token');
    axios
      .get(`${API}/admin/contacts/qr-stats`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => setData(r.data))
      .catch(() => setData({ total: 0, by_source: {}, labels: {} }))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) return null;

  const labels = data.labels || {};
  const order = ['dossier_express', 'strategiia', 'auto_diagnostic', 'inconnu'];
  const sources = order.filter((k) => data.by_source[k] !== undefined);

  return (
    <Card data-testid="admin-qr-stats">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center">
              <QrCode className="w-4.5 h-4.5 text-accent" strokeWidth={1.75} />
            </div>
            <div>
              <p className="text-sm font-semibold text-foreground">Contacts arrivés via QR</p>
              <p className="text-[11px] text-muted-foreground">Trafic depuis les PDFs imprimés/partagés</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-foreground" data-testid="qr-stats-total">{data.total}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Total</p>
          </div>
        </div>
        {data.total === 0 ? (
          <p className="text-[11px] text-muted-foreground italic mt-2">
            Aucun contact n'est encore arrivé via QR. Compteur actif dès le premier scan.
          </p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mt-3 pt-3 border-t border-border/50">
            {sources.map((src) => (
              <div key={src} className="flex items-center justify-between text-xs" data-testid={`qr-stats-${src}`}>
                <span className="text-muted-foreground truncate">{labels[src] || src}</span>
                <span className="font-semibold text-foreground ml-2">{data.by_source[src]}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
