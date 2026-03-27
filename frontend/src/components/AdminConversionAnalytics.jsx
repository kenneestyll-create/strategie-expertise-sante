import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, Eye, Send, ArrowRight, QrCode, Mail, FileText, Globe, BadgeCheck } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const VIA_LABELS = {
  qr: { label: 'QR Code PDF', icon: QrCode, color: 'text-amber-600', bg: 'bg-amber-50' },
  email: { label: 'Email livraison', icon: Mail, color: 'text-blue-600', bg: 'bg-blue-50' },
  pdf_link: { label: 'Lien PDF', icon: FileText, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  direct: { label: 'Direct / Autre', icon: Globe, color: 'text-gray-600', bg: 'bg-gray-50' },
};

const SOURCE_LABELS = {
  dossier_express: 'Dossier Express IA',
  strategiia: 'StrategiIA',
  '': 'Non specifie',
};

const PRESTATION_LABELS = {
  accompagnement_mp: 'Accompagnement MP',
  protection_juridique: 'Protection juridique',
  expertise_medicale: 'Expertise medicale',
  dossier_complet: 'Dossier complet',
  consultation: 'Consultation',
  autre: 'Autre',
};

const formatDate = (d) => {
  if (!d) return '';
  const parts = d.split('-');
  return `${parts[2]}/${parts[1]}`;
};

const formatEuro = (v) => `${Number(v || 0).toLocaleString('fr-FR')}€`;

export const AdminConversionAnalytics = ({ axiosConfig }) => {
  const [data, setData] = useState(null);
  const [period, setPeriod] = useState('30d');
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async (p) => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/tracking/conversion-analytics?period=${p}`, axiosConfig);
      setData(res.data);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [axiosConfig]);

  useEffect(() => { fetchData(period); }, [period, fetchData]);

  if (loading && !data) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground text-sm">
          Chargement des donnees de conversion...
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground text-sm">
          Aucune donnee de conversion disponible.
        </CardContent>
      </Card>
    );
  }

  const { channels, timeseries, totals, prestations } = data;

  return (
    <div className="space-y-4" data-testid="conversion-analytics">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-amber-600" />
          Conversions & ROI — Origine des leads
        </h3>
        <div className="flex gap-1 bg-muted rounded-lg p-0.5" data-testid="conversion-period-selector">
          {[{ v: '7d', l: '7j' }, { v: '30d', l: '30j' }].map(p => (
            <button
              key={p.v}
              onClick={() => setPeriod(p.v)}
              className={`px-2.5 py-1 text-[11px] rounded-md transition-colors ${period === p.v ? 'bg-background shadow text-foreground font-medium' : 'text-muted-foreground hover:text-foreground'}`}
              data-testid={`conv-period-${p.v}`}
            >
              {p.l}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Summary - 5 cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        <Card>
          <CardContent className="py-3 px-4">
            <div className="flex items-center gap-2 mb-1">
              <Eye className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Visites</span>
            </div>
            <p className="text-xl font-bold" data-testid="conv-total-visits">{totals.visits}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="py-3 px-4">
            <div className="flex items-center gap-2 mb-1">
              <Send className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Formulaires</span>
            </div>
            <p className="text-xl font-bold text-amber-600" data-testid="conv-total-contacts">{totals.contacts}</p>
            <p className="text-[10px] text-muted-foreground">Taux: {totals.conversion_rate}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="py-3 px-4">
            <div className="flex items-center gap-2 mb-1">
              <BadgeCheck className="w-3.5 h-3.5 text-emerald-600" />
              <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Convertis</span>
            </div>
            <p className="text-xl font-bold text-emerald-600" data-testid="conv-total-conversions">{totals.conversions}</p>
            <p className="text-[10px] text-muted-foreground">Closing: {totals.close_rate}%</p>
          </CardContent>
        </Card>
        <Card className="sm:col-span-2 lg:col-span-2">
          <CardContent className="py-3 px-4">
            <div className="flex items-center gap-2 mb-1">
              <ArrowRight className="w-3.5 h-3.5 text-emerald-600" />
              <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Revenus generes</span>
            </div>
            <p className="text-2xl font-bold text-emerald-600" data-testid="conv-total-revenue">{formatEuro(totals.revenue)}</p>
          </CardContent>
        </Card>
      </div>

      {/* Channel breakdown with revenue */}
      {channels.length > 0 && (
        <Card>
          <CardHeader className="pb-2 pt-4 px-4">
            <CardTitle className="text-sm font-medium">ROI par canal d'acquisition</CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-4">
            <div className="space-y-2">
              {channels.map((ch, i) => {
                const viaKey = ch.via || 'direct';
                const meta = VIA_LABELS[viaKey] || VIA_LABELS.direct;
                const Icon = meta.icon;
                const sourceLabel = SOURCE_LABELS[ch.source] || ch.source || 'Autre';
                return (
                  <div key={i} className="flex items-center gap-3 py-2.5 border-b border-border last:border-0" data-testid={`conv-channel-${viaKey}-${ch.source || 'none'}`}>
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${meta.bg}`}>
                      <Icon className={`w-4 h-4 ${meta.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{meta.label}</p>
                      <p className="text-[11px] text-muted-foreground">{sourceLabel}</p>
                    </div>
                    <div className="text-right flex-shrink-0 grid grid-cols-5 gap-3 text-xs">
                      <div>
                        <p className="font-semibold">{ch.visits}</p>
                        <p className="text-muted-foreground text-[10px]">visites</p>
                      </div>
                      <div>
                        <p className="font-semibold text-amber-600">{ch.contacts}</p>
                        <p className="text-muted-foreground text-[10px]">contacts</p>
                      </div>
                      <div>
                        <p className="font-semibold text-emerald-600">{ch.conversions}</p>
                        <p className="text-muted-foreground text-[10px]">convertis</p>
                      </div>
                      <div>
                        <p className="font-semibold">{ch.close_rate}%</p>
                        <p className="text-muted-foreground text-[10px]">closing</p>
                      </div>
                      <div>
                        <p className="font-bold text-emerald-700">{formatEuro(ch.revenue)}</p>
                        <p className="text-muted-foreground text-[10px]">revenus</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Revenue by prestation type */}
      {prestations && prestations.length > 0 && (
        <Card>
          <CardHeader className="pb-2 pt-4 px-4">
            <CardTitle className="text-sm font-medium">Revenus par type de prestation</CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-4">
            <div className="space-y-2">
              {prestations.map((p, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-border last:border-0" data-testid={`prestation-${p.prestation}`}>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                    <span className="text-sm">{PRESTATION_LABELS[p.prestation] || p.prestation}</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-muted-foreground">{p.count} conversion{p.count > 1 ? 's' : ''}</span>
                    <span className="font-bold text-emerald-700">{formatEuro(p.revenue)}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Timeseries chart */}
      {timeseries.length > 0 && (
        <Card>
          <CardHeader className="pb-1 pt-4 px-4">
            <CardTitle className="text-sm font-medium">Visites & Contacts — Evolution</CardTitle>
          </CardHeader>
          <CardContent className="px-2 pb-3">
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={timeseries} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d6" />
                <XAxis dataKey="date" tickFormatter={formatDate} tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} allowDecimals={false} />
                <Tooltip
                  labelFormatter={(v) => `Date: ${formatDate(v)}`}
                  contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e0d6' }}
                />
                <Area type="monotone" dataKey="visits" stroke="#c9a84c" fill="#c9a84c" fillOpacity={0.15} name="Visites" />
                <Area type="monotone" dataKey="contacts" stroke="#059669" fill="#059669" fillOpacity={0.15} name="Contacts" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {channels.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground text-sm">
            Aucune visite trackee sur cette periode. Les donnees apparaitront lorsque des visiteurs arriveront sur /contact via un lien tracke (QR code, email, PDF).
          </CardContent>
        </Card>
      )}
    </div>
  );
};
