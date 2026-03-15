import { useState } from 'react';
import { X, ZoomIn } from 'lucide-react';

const CoverContent = ({ reportType = "StrategiIA", large = false }) => {
  const scale = large ? 1 : 1;
  const fontSize = large ? 'text-base' : 'text-[6px]';
  const titleSize = large ? 'text-2xl' : 'text-[9px]';
  const subtitleSize = large ? 'text-lg' : 'text-[7px]';
  const infoSize = large ? 'text-sm' : 'text-[5px]';
  const smallSize = large ? 'text-xs' : 'text-[4px]';
  const pad = large ? 'p-8' : 'p-2';
  const gap = large ? 'gap-4' : 'gap-1';

  return (
    <div className={`relative w-full h-full bg-[#1a1a2e] ${pad} flex flex-col overflow-hidden select-none`}>
      {/* Watermark */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ transform: 'rotate(-40deg)' }}>
        <span className={`${large ? 'text-3xl' : 'text-[10px]'} font-bold text-white/[0.06] whitespace-nowrap tracking-wider`}>
          Strategie & Expertise Sante
        </span>
      </div>

      {/* Gold accent bar */}
      <div className="w-full" style={{ height: large ? 4 : 2, background: '#b94e48', marginTop: large ? 40 : 10 }} />

      {/* Title block */}
      <div className={`flex flex-col items-center text-center mt-auto ${gap}`}>
        {/* Shield logo */}
        <div className={`${large ? 'w-14 h-14' : 'w-5 h-5'} rounded-md bg-white/10 flex items-center justify-center`}>
          <svg viewBox="0 0 40 44" className={`${large ? 'w-8 h-8' : 'w-3 h-3'}`}>
            <path d="M20 0L40 8V22C40 34 28 42 20 44C12 42 0 34 0 22V8L20 0Z" fill="#b94e48" />
            <text x="20" y="28" textAnchor="middle" fontFamily="serif" fontSize="16" fontWeight="bold" fill="white">FS</text>
          </svg>
        </div>
        <div>
          <p className={`${titleSize} font-bold text-white tracking-wide`}>Strategie & Expertise Sante</p>
          <p className={`${infoSize} text-white/50 mt-0.5`}>strategie-expertise-sante.fr</p>
        </div>

        {/* Divider */}
        <div className="w-1/3 mx-auto" style={{ height: large ? 2 : 1, background: '#b94e48' }} />

        <p className={`${subtitleSize} font-bold text-white`}>Rapport {reportType}</p>
      </div>

      {/* Info box */}
      <div className={`bg-white/[0.07] rounded ${large ? 'p-4 mt-6 mx-6' : 'p-1 mt-2 mx-1'} ${gap} flex flex-col`}>
        {[
          ['Numero du rapport', 'SES-2026-48721'],
          ['Date de generation', '15/03/2026'],
          ['Client / Dossier', 'Apercu — Exemple'],
        ].map(([label, val]) => (
          <div key={label} className="flex items-baseline" style={{ gap: large ? 8 : 2 }}>
            <span className={`${infoSize} font-semibold text-white/50`}>{label} :</span>
            <span className={`${infoSize} text-white/80`}>{val}</span>
          </div>
        ))}
      </div>

      {/* Bottom */}
      <div className={`mt-auto text-center ${smallSize} text-white/30 italic`}>
        Document confidentiel
      </div>
      <div className={`text-center ${smallSize} text-white/20`}>
        &copy; 2026 Strategie & Expertise Sante
      </div>
    </div>
  );
};

export const PdfCoverPreview = ({ reportType = "StrategiIA", className = "" }) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Miniature */}
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={`group relative flex-shrink-0 rounded-lg overflow-hidden border border-border/60 shadow-sm hover:shadow-md transition-all hover:scale-[1.02] cursor-zoom-in ${className}`}
        style={{ width: 90, height: 127, aspectRatio: '210/297' }}
        data-testid="pdf-cover-preview-thumb"
        aria-label="Apercu du rapport PDF"
      >
        <CoverContent reportType={reportType} />
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
          <ZoomIn className="w-5 h-5 text-white opacity-0 group-hover:opacity-100 transition-opacity drop-shadow-lg" />
        </div>
      </button>

      {/* Modal */}
      {open && (
        <div className="fixed inset-0 flex items-center justify-center p-4" style={{ zIndex: 9999 }}>
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setOpen(false)} />
          <div className="relative animate-in fade-in zoom-in-95 duration-200">
            <button
              onClick={() => setOpen(false)}
              className="absolute -top-3 -right-3 z-10 w-8 h-8 rounded-full bg-foreground text-primary-foreground flex items-center justify-center shadow-lg hover:bg-foreground/90 transition-colors"
              data-testid="pdf-cover-preview-close"
            >
              <X className="w-4 h-4" />
            </button>
            <div
              className="rounded-xl overflow-hidden border-2 border-border/40 shadow-2xl"
              style={{ width: 340, height: 480, aspectRatio: '210/297' }}
              data-testid="pdf-cover-preview-modal"
            >
              <CoverContent reportType={reportType} large />
            </div>
            <p className="text-center text-xs text-white/60 mt-3">Apercu de la page de garde du rapport</p>
          </div>
        </div>
      )}
    </>
  );
};
