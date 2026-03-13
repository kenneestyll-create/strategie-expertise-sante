import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, ArrowRight, Table2, MapPin, Heart, Activity, FileText, Wrench, Globe } from 'lucide-react';
import { searchContent } from '@/data/searchIndex';

const CATEGORY_ICONS = {
  'Outils': Wrench,
  'Pages': Globe,
  'Maladies professionnelles': Table2,
  'IPP — Exemples': Activity,
  'Annuaire MDPH': MapPin,
  'Aides MDPH': Heart,
  'Guides': FileText,
};

export const GlobalSearch = () => {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const r = searchContent(query);
    setResults(r);
  }, [query]);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      setQuery('');
      setResults([]);
    }
  }, [open]);

  // Ctrl+K shortcut
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(prev => !prev);
      }
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const handleSelect = useCallback((entry) => {
    setOpen(false);
    navigate(entry.href);
  }, [navigate]);

  // Group results by category
  const grouped = results.reduce((acc, r) => {
    if (!acc[r.category]) acc[r.category] = [];
    acc[r.category].push(r);
    return acc;
  }, {});

  return (
    <>
      {/* Trigger button */}
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-border bg-muted/50 hover:bg-muted text-muted-foreground text-sm transition-colors"
        data-testid="global-search-trigger"
        aria-label="Rechercher"
      >
        <Search className="w-3.5 h-3.5" />
        <span className="hidden xl:inline">Rechercher...</span>
        <kbd className="hidden xl:inline-flex h-5 items-center gap-0.5 rounded border border-border bg-background px-1.5 text-[10px] font-mono text-muted-foreground">
          Ctrl K
        </kbd>
      </button>

      {/* Overlay */}
      {open && (
        <div
          className="fixed inset-0"
          style={{ zIndex: 'var(--z-modal)' }}
          data-testid="global-search-overlay"
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setOpen(false)} />

          {/* Search Panel */}
          <div className="relative max-w-2xl mx-auto mt-[10vh] mx-4">
            <div className="bg-background border border-border rounded-2xl shadow-2xl overflow-hidden" data-testid="global-search-panel">
              {/* Search Input */}
              <div className="flex items-center gap-3 px-5 py-4 border-b border-border">
                <Search className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                <input
                  ref={inputRef}
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="Rechercher un sujet, une maladie, un outil, un département..."
                  className="flex-1 bg-transparent outline-none text-base placeholder:text-muted-foreground"
                  data-testid="global-search-input"
                />
                {query && (
                  <button onClick={() => setQuery('')} className="p-1 hover:bg-muted rounded-md">
                    <X className="w-4 h-4 text-muted-foreground" />
                  </button>
                )}
                <button onClick={() => setOpen(false)} className="px-2 py-1 text-xs text-muted-foreground border border-border rounded-md hover:bg-muted">
                  Esc
                </button>
              </div>

              {/* Results */}
              <div className="max-h-[60vh] overflow-y-auto" data-testid="global-search-results">
                {query.length >= 2 && results.length === 0 && (
                  <div className="px-5 py-10 text-center text-muted-foreground">
                    <p className="text-sm">Aucun résultat pour "<strong>{query}</strong>"</p>
                    <p className="text-xs mt-2">Essayez avec d'autres termes : canal carpien, MDPH Paris, AAH, expertise...</p>
                  </div>
                )}

                {query.length < 2 && (
                  <div className="px-5 py-8 text-center text-muted-foreground">
                    <p className="text-sm mb-3">Tapez au moins 2 caractères pour rechercher</p>
                    <div className="flex flex-wrap gap-2 justify-center">
                      {['canal carpien', 'MDPH Paris', 'IPP 30%', 'AAH', 'expertise médicale', 'amiante'].map(s => (
                        <button
                          key={s}
                          onClick={() => setQuery(s)}
                          className="px-3 py-1.5 text-xs rounded-full border border-border hover:bg-muted hover:text-foreground transition-colors"
                          data-testid={`search-suggestion-${s.replace(/\s+/g, '-').toLowerCase()}`}
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {Object.entries(grouped).map(([category, items]) => {
                  const Icon = CATEGORY_ICONS[category] || FileText;
                  return (
                    <div key={category}>
                      <div className="px-5 py-2 bg-muted/30 border-b border-border/50">
                        <span className="flex items-center gap-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                          <Icon className="w-3.5 h-3.5" />
                          {category}
                        </span>
                      </div>
                      {items.map((item, i) => (
                        <button
                          key={`${category}-${i}`}
                          onClick={() => handleSelect(item)}
                          className="w-full flex items-start gap-3 px-5 py-3 hover:bg-muted/50 transition-colors text-left group"
                          data-testid={`search-result-${i}`}
                        >
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate group-hover:text-accent transition-colors">
                              {item.title}
                            </p>
                            <p className="text-xs text-muted-foreground truncate mt-0.5">{item.description}</p>
                          </div>
                          <ArrowRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 mt-1" />
                        </button>
                      ))}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
