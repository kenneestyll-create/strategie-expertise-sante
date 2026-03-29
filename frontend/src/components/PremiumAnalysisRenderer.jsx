import ReactMarkdown from 'react-markdown';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Brain, Shield, AlertTriangle, Target, Eye, FileSearch,
  Compass, Lightbulb, ListChecks, TrendingUp, Clock,
  FileText, Layers, Activity, CheckCircle
} from 'lucide-react';

const SECTION_ICONS = {
  'votre situation analysee': { icon: Eye, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200/60' },
  'lecture strategique du dossier': { icon: Compass, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200/60', premium: true },
  'lecture strategique': { icon: Compass, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200/60', premium: true },
  'cadre juridique applicable': { icon: Shield, color: 'text-indigo-600', bg: 'bg-indigo-50', border: 'border-indigo-200/60' },
  'leviers prioritaires identifies': { icon: Target, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200/60', premium: true },
  'leviers et points de vigilance': { icon: Target, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200/60' },
  'points de vigilance': { icon: AlertTriangle, color: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-200/60' },
  'angles potentiellement sous-exploites': { icon: Lightbulb, color: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-200/60', premium: true },
  'evaluation et perspectives': { icon: TrendingUp, color: 'text-teal-600', bg: 'bg-teal-50', border: 'border-teal-200/60' },
  'plan d\'action recommande': { icon: ListChecks, color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200/60', premium: true },
  'notre engagement a vos cotes': { icon: Brain, color: 'text-accent', bg: 'bg-accent/5', border: 'border-accent/20' },
  'notre engagement': { icon: Brain, color: 'text-accent', bg: 'bg-accent/5', border: 'border-accent/20' },
  // Dossier Express sections
  'synthese du dossier': { icon: FileText, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200/60' },
  'pieces detectees': { icon: Layers, color: 'text-teal-600', bg: 'bg-teal-50', border: 'border-teal-200/60', premium: true },
  'chronologie synthetique du dossier': { icon: Clock, color: 'text-indigo-600', bg: 'bg-indigo-50', border: 'border-indigo-200/60', premium: true },
  'elements cles identifies': { icon: Target, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200/60', premium: true },
  'droits et indemnisations identifies': { icon: Shield, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200/60' },
  'points potentiellement sous-exploites': { icon: Lightbulb, color: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-200/60', premium: true },
  'completude documentaire': { icon: Activity, color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200/60', premium: true },
  'strategie recommandee et prochaines etapes': { icon: ListChecks, color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200/60' },
  'conclusion': { icon: CheckCircle, color: 'text-accent', bg: 'bg-accent/5', border: 'border-accent/20' },
};

function normalize(str) {
  return str.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9 ']/g, '')
    .trim();
}

function findSectionConfig(title) {
  const norm = normalize(title);
  // Remove leading numbers like "1. " or "2. "
  const cleaned = norm.replace(/^\d+\s*\.?\s*/, '');
  for (const [key, val] of Object.entries(SECTION_ICONS)) {
    if (cleaned.includes(key) || key.includes(cleaned)) return val;
  }
  return null;
}

function parseSections(markdown) {
  if (!markdown) return [];
  // Split by ## or ### headers
  const lines = markdown.split('\n');
  const sections = [];
  let current = null;

  for (const line of lines) {
    const h2Match = line.match(/^#{2,3}\s+(.+)/);
    if (h2Match) {
      if (current) sections.push(current);
      const title = h2Match[1].trim();
      current = { title, content: '', config: findSectionConfig(title) };
    } else if (line.match(/^#\s+.+/)) {
      // Skip h1 headers (report title)
      continue;
    } else {
      if (current) {
        current.content += line + '\n';
      }
    }
  }
  if (current) sections.push(current);
  return sections;
}

export const PremiumAnalysisRenderer = ({ markdown, testIdPrefix = 'premium-section' }) => {
  const sections = parseSections(markdown);

  if (sections.length === 0) {
    return (
      <div className="prose prose-sm max-w-none text-sm leading-relaxed bg-muted/30 p-5 rounded-xl border border-border">
        <ReactMarkdown>{markdown}</ReactMarkdown>
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid={`${testIdPrefix}-container`}>
      {sections.map((section, idx) => {
        const Icon = section.config?.icon || FileText;
        const color = section.config?.color || 'text-foreground/70';
        const bg = section.config?.bg || 'bg-muted/30';
        const border = section.config?.border || 'border-border';
        const isPremium = section.config?.premium;

        return (
          <Card key={idx} className={`${border} ${isPremium ? 'ring-1 ring-accent/10' : ''} overflow-hidden`} data-testid={`${testIdPrefix}-${idx}`}>
            <CardContent className="p-0">
              {/* Section header */}
              <div className={`flex items-center gap-2.5 px-5 py-3 ${bg} border-b ${border}`}>
                <div className={`w-7 h-7 rounded-lg ${bg} flex items-center justify-center flex-shrink-0`}>
                  <Icon className={`w-4 h-4 ${color}`} />
                </div>
                <h3 className="font-semibold text-sm tracking-tight">{section.title}</h3>
                {isPremium && <Badge className="bg-accent/10 text-accent border-accent/20 text-[9px] px-1.5 py-0">Premium</Badge>}
              </div>
              {/* Section content */}
              <div className="px-5 py-4 prose prose-sm max-w-none text-sm leading-relaxed [&>ul]:space-y-1 [&>ol]:space-y-1 [&>p]:mb-2 [&>p:last-child]:mb-0">
                <ReactMarkdown>{section.content.trim()}</ReactMarkdown>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};
