import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  ScanLine, CheckCircle, Calendar, DollarSign, FileText,
  User, Hash, Target, Loader2, ChevronDown, ChevronUp, X, Sparkles,
  Building2, MessageSquare, Lightbulb
} from 'lucide-react';

const FieldRow = ({ icon: Icon, label, values, color = 'text-foreground' }) => {
  if (!values || values.length === 0) return null;
  return (
    <div className="flex items-start gap-2.5 py-1.5">
      <Icon className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${color}`} />
      <div className="flex-1 min-w-0">
        <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{label}</p>
        <div className="flex flex-wrap gap-1 mt-0.5">
          {values.map((v, i) => (
            <Badge key={i} variant="outline" className="text-xs font-mono bg-muted/50">{v}</Badge>
          ))}
        </div>
      </div>
    </div>
  );
};

const TextBlock = ({ icon: Icon, label, text, color = 'text-foreground' }) => {
  if (!text) return null;
  return (
    <div className="flex items-start gap-2.5 py-1.5">
      <Icon className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${color}`} />
      <div className="flex-1 min-w-0">
        <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{label}</p>
        <p className="text-xs leading-relaxed mt-0.5">{text}</p>
      </div>
    </div>
  );
};

export const OcrFieldsPreview = ({ ocrResult, onApplyFields, onDismiss, className = '' }) => {
  const [expanded, setExpanded] = useState(true);

  if (!ocrResult || !ocrResult.fields) return null;

  const { fields, confidence, source } = ocrResult;
  const hasFields = Object.keys(fields).length > 0 && (
    fields.dates?.length || fields.montants?.length || fields.référénces?.length ||
    fields.noms?.length || fields.taux_ipp?.length || fields.type_dossier_detected?.length || 
    fields.numero_ss || fields.organisme || fields.resume || fields.recommandations?.length
  );

  if (!hasFields) return null;

  const typeLabels = { at: 'Accident du travail', mp: 'Maladie professionnelle', mdph: 'MDPH/AAH', expertise: 'Expertise médicale', ipp: 'Contestation IPP' };

  return (
    <Card className={`border-accent/30 bg-gradient-to-r from-accent/5 to-transparent ${className}`} data-testid="ocr-fields-preview">
      <CardContent className="p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-accent/10 flex items-center justify-center">
              <ScanLine className="w-4 h-4 text-accent" />
            </div>
            <div>
              <p className="text-sm font-semibold flex items-center gap-1.5">
                Informations extraites par OCR
                {confidence && <Badge variant="outline" className="text-[9px] px-1">{confidence}% confiance</Badge>}
              </p>
              <p className="text-[10px] text-muted-foreground">
                {source === 'tesseract' ? 'Extraction locale (Tesseract)' : 'Extraction IA (GPT-4o)'}
                {' — Vérifiez et corrigez si nécessaire'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="w-6 h-6" onClick={() => setExpanded(!expanded)}>
              {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </Button>
            <Button variant="ghost" size="icon" className="w-6 h-6 text-muted-foreground hover:text-destructive" onClick={onDismiss} data-testid="ocr-dismiss">
              <X className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>

        {expanded && (
          <div className="mt-3 space-y-1 border-t border-border/50 pt-2" data-testid="ocr-fields-list">
            {fields.type_dossier_detected?.length > 0 && (
              <FieldRow icon={Target} label="Type de dossier détecté" values={fields.type_dossier_detected.map(t => typeLabels[t] || t)} color="text-accent" />
            )}
            {fields.noms?.length > 0 && (
              <FieldRow icon={User} label="Noms détectés" values={fields.noms} color="text-blue-500" />
            )}
            {fields.dates?.length > 0 && (
              <FieldRow icon={Calendar} label="Dates" values={fields.dates} color="text-green-600" />
            )}
            {fields.montants?.length > 0 && (
              <FieldRow icon={DollarSign} label="Montants" values={fields.montants} color="text-emerald-600" />
            )}
            {fields.référénces?.length > 0 && (
              <FieldRow icon={Hash} label="Références / N° dossier" values={fields.référénces} color="text-purple-600" />
            )}
            {fields.numero_ss && (
              <FieldRow icon={FileText} label="N° Sécurité Sociale" values={[fields.numero_ss]} color="text-orange-600" />
            )}
            {fields.taux_ipp?.length > 0 && (
              <FieldRow icon={Target} label="Taux IPP" values={fields.taux_ipp.map(t => `${t}%`)} color="text-red-500" />
            )}
            {fields.organisme && (
              <FieldRow icon={Building2} label="Organisme émetteur" values={[fields.organisme]} color="text-indigo-600" />
            )}
            {fields.resume && (
              <TextBlock icon={MessageSquare} label="Résumé du document" text={fields.resume} color="text-slate-600" />
            )}
            {fields.recommandations?.length > 0 && (
              <div className="flex items-start gap-2.5 py-1.5">
                <Lightbulb className="w-3.5 h-3.5 mt-0.5 flex-shrink-0 text-amber-500" />
                <div className="flex-1 min-w-0">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Recommandations IA</p>
                  <ul className="mt-0.5 space-y-0.5">
                    {fields.recommandations.map((r, i) => (
                      <li key={i} className="text-xs leading-relaxed flex items-start gap-1.5">
                        <CheckCircle className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                        {r}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Apply button */}
            {onApplyFields && (
              <div className="pt-2 flex gap-2">
                <Button
                  size="sm"
                  className="gap-1.5 text-xs rounded-lg"
                  onClick={() => onApplyFields(fields)}
                  data-testid="ocr-apply-fields"
                >
                  <Sparkles className="w-3.5 h-3.5" /> Pré-remplir le formulaire
                </Button>
                <p className="text-[10px] text-muted-foreground self-center">Vous pourrez modifier les champs avant envoi</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export const OcrProgressBar = ({ processing, progress }) => {
  if (!processing) return null;
  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-accent/5 border border-accent/20" data-testid="ocr-progress">
      <Loader2 className="w-4 h-4 text-accent animate-spin flex-shrink-0" />
      <div className="flex-1">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium">Extraction OCR en cours...</span>
          <span className="text-xs text-muted-foreground">{progress}%</span>
        </div>
        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
          <div className="h-full bg-accent rounded-full transition-all duration-300" style={{ width: `${progress}%` }} />
        </div>
      </div>
    </div>
  );
};
