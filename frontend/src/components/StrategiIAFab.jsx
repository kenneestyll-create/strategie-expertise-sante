import { Brain } from 'lucide-react';

export const StrategiIAFab = () => (
  <button
    onClick={() => window.dispatchEvent(new Event('strategiia:open'))}
    className="strategiia-fab hidden md:flex lg:hidden fixed z-40 items-center gap-2 px-4 py-3 rounded-full shadow-lg border border-[#C9A84C]/30 transition-all active:scale-95"
    style={{
      bottom: 'calc(5.5rem + env(safe-area-inset-bottom, 0px))',
      right: '1rem',
      background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)',
    }}
    data-testid="strategiia-fab"
    aria-label="Ouvrir StratégiIA"
  >
    <Brain className="w-5 h-5 text-[#C9A84C]" />
    <span className="text-[#C9A84C] text-sm font-semibold tracking-wide">StratégiIA</span>
  </button>
);
