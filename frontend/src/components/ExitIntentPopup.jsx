import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { X, ScanSearch, FileText } from 'lucide-react';
import { safeStorage, safeSessionStorage } from '../utils/safeStorage';

const STORAGE_KEY = 'exitPopupShown';

export const ExitIntentPopup = () => {
  const [visible, setVisible] = useState(false);

  // Ne pas afficher en mode admin
  const isAdmin = !!safeStorage.get('admin_token');
  const isAdminRoute = typeof window !== 'undefined' && (window.location.pathname.startsWith('/admin') || window.location.pathname.startsWith('/login'));

  const show = useCallback(() => {
    if (isAdmin || isAdminRoute) return;
    if (safeSessionStorage.get(STORAGE_KEY)) return;
    safeSessionStorage.set(STORAGE_KEY, 'true');
    setVisible(true);
  }, [isAdmin, isAdminRoute]);

  const close = useCallback(() => setVisible(false), []);

  useEffect(() => {
    // Exit intent: mouse leaves the HTML element (works in iframes & modern browsers)
    const html = document.documentElement;
    const onMouseLeave = (e) => {
      // Only trigger when leaving toward the top (not scrollbar/bottom)
      if (e.clientY <= 5) show();
    };

    // Fallback: visibilitychange — user switches tab or minimizes
    const onVisChange = () => {
      if (document.visibilityState === 'hidden') show();
    };

    html.addEventListener('mouseleave', onMouseLeave);
    document.addEventListener('visibilitychange', onVisChange);
    return () => {
      html.removeEventListener('mouseleave', onMouseLeave);
      document.removeEventListener('visibilitychange', onVisChange);
    };
  }, [show]);

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4" data-testid="exit-intent-overlay">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={close} />

      {/* Popup */}
      <div
        className="relative w-full max-w-md bg-background rounded-2xl shadow-2xl border border-border overflow-hidden"
        style={{ animation: 'exitIn .3s ease-out' }}
        data-testid="exit-intent-popup"
      >
        {/* Close button */}
        <button
          onClick={close}
          className="absolute top-3 right-3 w-8 h-8 flex items-center justify-center rounded-full text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          data-testid="exit-intent-close"
          aria-label="Fermer"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Content */}
        <div className="px-6 pt-8 pb-6 text-center">
          <h2
            className="text-xl font-semibold text-foreground mb-3"
            data-testid="exit-intent-title"
          >
            Avant de partir...
          </h2>
          <p className="text-sm text-muted-foreground leading-relaxed mb-6 max-w-xs mx-auto">
            Avez-vous vérifié vos droits ? Une analyse rapide peut révéler
            des éléments importants dans votre situation.
          </p>

          <div className="flex flex-col gap-2.5">
            <Link to="/simulateur" onClick={close}>
              <Button
                className="w-full rounded-full gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
                data-testid="exit-intent-cta-strategiia"
              >
                <ScanSearch className="w-4 h-4" />
                Vérifier ma situation (StratégiIA)
              </Button>
            </Link>
            <Link to="/dossier-express" onClick={close}>
              <Button
                variant="outline"
                className="w-full rounded-full gap-2"
                data-testid="exit-intent-cta-dossier"
              >
                <FileText className="w-4 h-4" />
                Analyser mon dossier (Dossier Express)
              </Button>
            </Link>
          </div>
        </div>

        {/* Bottom subtle bar */}
        <div className="h-1 bg-accent/20" />
      </div>

      <style>{`
        @keyframes exitIn {
          from { opacity: 0; transform: translateY(-12px) scale(.97); }
          to   { opacity: 1; transform: translateY(0) scale(1); }
        }
      `}</style>
    </div>
  );
};
