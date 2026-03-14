import { Shield, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DataConsentBox = ({ checked, onChange, className = '' }) => {
  return (
    <div className={`rounded-xl border border-amber-200 bg-amber-50/50 p-4 space-y-3 ${className}`} data-testid="data-consent-box">
      <div className="flex items-start gap-2.5">
        <Shield className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
        <div>
          <h4 className="font-semibold text-sm text-amber-900">Confidentialité et utilisation de vos documents</h4>
          <p className="text-xs text-amber-800/80 leading-relaxed mt-1.5">
            Les documents que vous transmettez sont utilisés uniquement dans le cadre de l'analyse de votre situation 
            et de l'accompagnement administratif proposé par Stratégie & Expertise Santé. Les informations médicales 
            restent strictement confidentielles. Elles ne sont jamais partagées avec des tiers sans votre accord. 
            Les analyses réalisées ne constituent ni un avis médical ni un conseil juridique.
          </p>
        </div>
      </div>
      <label className="flex items-start gap-2.5 cursor-pointer group" data-testid="data-consent-checkbox-label">
        <input
          type="checkbox"
          checked={checked}
          onChange={e => onChange(e.target.checked)}
          className="mt-0.5 w-4 h-4 rounded border-amber-300 text-accent focus:ring-accent/30 cursor-pointer"
          data-testid="data-consent-checkbox"
        />
        <span className="text-xs text-amber-900 leading-relaxed group-hover:text-amber-950 transition-colors">
          Je confirme transmettre ces documents volontairement et accepter leur analyse dans le cadre d'un accompagnement administratif et stratégique.
        </span>
      </label>
      <p className="text-[11px] text-amber-700/70 pl-6 leading-relaxed">
        Vous restez propriétaire de vos données et pouvez demander leur suppression à tout moment en contactant{' '}
        <a href="mailto:contact@strategie-expertise-sante.fr" className="underline hover:text-amber-900 transition-colors">contact@strategie-expertise-sante.fr</a>.{' '}
        <Link to="/politique-confidentialite" className="inline-flex items-center gap-0.5 underline hover:text-amber-900 transition-colors">
          Politique de confidentialité <ExternalLink className="w-2.5 h-2.5" />
        </Link>
      </p>
    </div>
  );
};
