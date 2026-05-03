import { useState } from 'react';
import { Shield, ChevronDown, ExternalLink, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DataConsentBox = ({ checked, onChange, className = '', variant = 'documents', improvementOptout = false, onImprovementOptoutChange = null }) => {
  const [showDetails, setShowDetails] = useState(false);
  const [showImprovement, setShowImprovement] = useState(false);

  const isInfoOnly = variant === 'informations';

  return (
    <div className={`rounded-xl border border-[#C9A84C]/30 bg-[#FAF8F3] p-4 space-y-3 ${className}`} data-testid="data-consent-box">
      <div className="flex items-start gap-2.5">
        <Shield className="w-5 h-5 text-[#C9A84C] flex-shrink-0 mt-0.5" strokeWidth={1.5} />
        <div>
          <h4 className="font-semibold text-sm text-[#1A1A1A]">
            {isInfoOnly ? "Confidentialité de vos informations" : "Confidentialité de vos documents"}
          </h4>
          <p className="text-xs text-[#1A1A1A]/70 leading-relaxed mt-1.5">
            {isInfoOnly
              ? "Vos informations sont utilisées uniquement pour traiter votre demande. Votre description est analysée par un service d'intelligence artificielle sécurisé pour générer votre rapport. L'accès à vos données est strictement limité et encadré."
              : "Vos documents sont utilisés uniquement pour traiter votre demande. Le texte extrait est analysé par un service d'intelligence artificielle sécurisé pour générer votre rapport. L'accès à vos données est strictement limité et encadré."
            }
          </p>
        </div>
      </div>

      {/* Accordion — Que deviennent mes documents */}
      <button
        type="button"
        onClick={() => setShowDetails(!showDetails)}
        className="flex items-center gap-1.5 text-xs text-[#C9A84C] hover:text-[#1A1A1A] transition-colors ml-7 font-medium"
        data-testid="data-consent-details-toggle"
      >
        {isInfoOnly ? "Que deviennent mes informations ?" : "Que deviennent mes documents ?"}
        <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showDetails ? 'rotate-180' : ''}`} />
      </button>

      {showDetails && (
        <div className="ml-7 text-xs text-[#1A1A1A]/65 space-y-2 bg-white/60 rounded-lg p-3 border border-[#C9A84C]/15" data-testid="data-consent-details">
          {isInfoOnly ? (
            <>
              <div className="flex items-start gap-2">
                <span className="text-[#C9A84C] mt-0.5 text-[10px]">&#9679;</span>
                <span><strong>Analyse :</strong> Votre description est transmise à un service d'IA (Anthropic / Claude) pour générer votre rapport personnalisé.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#C9A84C] mt-0.5 text-[10px]">&#9679;</span>
                <span><strong>Conservation :</strong> Vos informations sont automatiquement purgées 30 jours après la finalisation de votre rapport.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#C9A84C] mt-0.5 text-[10px]">&#9679;</span>
                <span><strong>Accès :</strong> Seule l'équipe restreinte de Stratégie & Expertise Santé peut consulter votre dossier, dans le cadre strict de votre accompagnement.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#C9A84C] mt-0.5 text-[10px]">&#9679;</span>
                <span><strong>Suppression :</strong> Vous pouvez demander la suppression de vos données à tout moment.</span>
              </div>
            </>
          ) : (
            <>
              <div className="flex items-start gap-2">
                <span className="text-[#C9A84C] mt-0.5 text-[10px]">&#9679;</span>
                <span><strong>Extraction :</strong> Le texte de vos documents est extrait localement sur notre serveur (aucun service OCR tiers).</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#C9A84C] mt-0.5 text-[10px]">&#9679;</span>
                <span><strong>Analyse :</strong> Le texte extrait est transmis à un service d'IA (Anthropic / Claude) pour générer votre rapport personnalisé.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#C9A84C] mt-0.5 text-[10px]">&#9679;</span>
                <span><strong>Stockage :</strong> Vos fichiers originaux ne sont pas conservés. Seul le texte extrait est temporairement stocké pour le traitement de votre dossier.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#C9A84C] mt-0.5 text-[10px]">&#9679;</span>
                <span><strong>Conservation :</strong> Le texte extrait est automatiquement purgé 30 jours après la finalisation de votre rapport.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#C9A84C] mt-0.5 text-[10px]">&#9679;</span>
                <span><strong>Accès :</strong> Seule l'équipe restreinte de Stratégie & Expertise Santé peut consulter votre dossier, dans le cadre strict de votre accompagnement.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#C9A84C] mt-0.5 text-[10px]">&#9679;</span>
                <span><strong>Suppression :</strong> Vous pouvez demander la suppression de vos données à tout moment.</span>
              </div>
            </>
          )}
        </div>
      )}

      {/* Checkbox principale — consentement */}
      <label className="flex items-start gap-2.5 cursor-pointer group" data-testid="data-consent-checkbox-label">
        <input
          type="checkbox"
          checked={checked}
          onChange={e => onChange(e.target.checked)}
          className="mt-0.5 w-4 h-4 rounded border-[#C9A84C]/40 text-[#C9A84C] focus:ring-[#C9A84C]/30 cursor-pointer"
          data-testid="data-consent-checkbox"
        />
        <span className="text-xs text-[#1A1A1A]/80 leading-relaxed group-hover:text-[#1A1A1A] transition-colors">
          {isInfoOnly
            ? "Je transmets ces informations volontairement et j'accepte leur analyse par intelligence artificielle dans le cadre de mon accompagnement."
            : "Je transmets ces documents volontairement et j'accepte leur analyse par intelligence artificielle dans le cadre de mon accompagnement."
          }
        </span>
      </label>

      {/* Bloc amelioration continue — discret, deployable */}
      <div className="ml-7 border-t border-[#C9A84C]/10 pt-2.5 mt-1">
        <button
          type="button"
          onClick={() => setShowImprovement(!showImprovement)}
          className="flex items-center gap-1.5 text-xs text-[#1A1A1A]/50 hover:text-[#C9A84C] transition-colors font-medium"
          data-testid="improvement-toggle"
        >
          <TrendingUp className="w-3 h-3" />
          Amélioration continue du service
          <ChevronDown className={`w-3 h-3 transition-transform ${showImprovement ? 'rotate-180' : ''}`} />
        </button>

        {showImprovement && (
          <div className="mt-2 text-[11px] text-[#1A1A1A]/55 leading-relaxed space-y-2" data-testid="improvement-details">
            <p>
              Afin d'améliorer la pertinence et la qualité de ses analyses, Stratégie & Expertise Santé peut exploiter certains enseignements issus des dossiers traités, <strong>uniquement sous forme de données strictement anonymisées, agrégées et non réidentifiables</strong>, dans le respect du RGPD et des obligations de confidentialité.
            </p>
            <p>
              Aucune donnée nominative, médicale ou assurantielle identifiable n'est réutilisée pour un autre dossier.
            </p>
            {onImprovementOptoutChange && (
              <label className="flex items-start gap-2 cursor-pointer group mt-1.5" data-testid="improvement-optout-label">
                <input
                  type="checkbox"
                  checked={improvementOptout}
                  onChange={e => onImprovementOptoutChange(e.target.checked)}
                  className="mt-0.5 w-3.5 h-3.5 rounded border-[#C9A84C]/30 text-[#C9A84C] focus:ring-[#C9A84C]/20 cursor-pointer"
                  data-testid="improvement-optout-checkbox"
                />
                <span className="text-[11px] text-[#1A1A1A]/60 group-hover:text-[#1A1A1A]/80 transition-colors leading-relaxed">
                  Je ne souhaite pas que des enseignements anonymisés issus de mon dossier contribuent à l'amélioration du service.
                </span>
              </label>
            )}
          </div>
        )}
      </div>

      <p className="text-[11px] text-[#1A1A1A]/50 pl-6 leading-relaxed">
        Vous restez propriétaire de vos données.{' '}
        <a href="mailto:contact@strategie-expertise-sante.fr" className="underline hover:text-[#C9A84C] transition-colors">Demander une suppression</a>.{' '}
        <Link to="/politique-confidentialite" className="inline-flex items-center gap-0.5 underline hover:text-[#C9A84C] transition-colors">
          Politique de confidentialité <ExternalLink className="w-2.5 h-2.5" />
        </Link>
      </p>
    </div>
  );
};
