import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, ArrowRight, Table2, MapPin, Heart, Activity, FileText, Wrench, Globe, Scale, BookOpen, MessageCircle } from 'lucide-react';
import { liteClient as algoliasearch } from 'algoliasearch/lite';

const searchClient = algoliasearch(
  process.env.REACT_APP_ALGOLIA_APP_ID,
  process.env.REACT_APP_ALGOLIA_SEARCH_KEY
);
const INDEX_NAME = process.env.REACT_APP_ALGOLIA_INDEX_NAME;

const CATEGORY_ICONS = {
  'Outils': Wrench,
  'Pages': Globe,
  'Maladies professionnelles': Table2,
  'IPP — Exemples': Activity,
  'Annuaire MDPH': MapPin,
  'Aides MDPH': Heart,
  'Guides': BookOpen,
  'Indemnisation': Scale,
  'Sections': FileText,
};

export const GlobalSearch = () => {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);
  const navigate = useNavigate();
  const debounceRef = useRef(null);

  // Algolia search with debounce
  useEffect(() => {
    if (!query || query.trim().length < 2) {
      setResults([]);
      return;
    }
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const { results: searchResults } = await searchClient.search({
          requests: [{
            indexName: INDEX_NAME,
            query: query.trim(),
            hitsPerPage: 15,
            attributesToHighlight: ['title', 'description'],
            highlightPreTag: '<mark class="algolia-hl">',
            highlightPostTag: '</mark>',
          }],
        });
        setResults(searchResults?.[0]?.hits || []);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 200);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
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

  const handleSelect = useCallback((hit) => {
    setOpen(false);
    const anchor = hit.anchor || '';
    const url = anchor
      ? `${hit.href}?highlight=${encodeURIComponent(query.trim())}#${anchor}`
      : `${hit.href}?highlight=${encodeURIComponent(query.trim())}`;
    navigate(url);
  }, [navigate, query]);

  // Render highlighted text from Algolia
  const renderHighlight = useCallback((hit, attr) => {
    const hlResult = hit._highlightResult?.[attr];
    if (!hlResult || !hlResult.value) return hit[attr] || '';
    return <span dangerouslySetInnerHTML={{ __html: hlResult.value }} />;
  }, []);

  // Group results by category
  const grouped = results.reduce((acc, r) => {
    const cat = r.category || 'Autres';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(r);
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
          <div className="relative max-w-2xl mx-auto mt-[10vh]">
            <div className="bg-background border border-border rounded-2xl shadow-2xl overflow-hidden mx-4" data-testid="global-search-panel">
              {/* Search Input */}
              <div className="flex items-center gap-3 px-5 py-4 border-b border-border">
                <Search className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                <input
                  ref={inputRef}
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="Rechercher un sujet, une maladie, un outil, un departement..."
                  className="flex-1 bg-transparent outline-none text-base placeholder:text-muted-foreground"
                  data-testid="global-search-input"
                />
                {loading && (
                  <div className="w-4 h-4 border-2 border-muted-foreground/30 border-t-muted-foreground rounded-full animate-spin" />
                )}
                {query && !loading && (
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
                {/* No results */}
                {query.length >= 2 && !loading && results.length === 0 && (
                  <div className="px-5 py-10 text-center text-muted-foreground" data-testid="search-no-results">
                    <p className="text-sm">Aucun resultat pour "<strong>{query}</strong>"</p>
                    <p className="text-xs mt-3 mb-4">Essayez avec d'autres termes ou posez votre question a notre assistant</p>
                    <button
                      onClick={() => { setOpen(false); /* TODO: open chatbot */ }}
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-border hover:bg-muted text-sm transition-colors"
                      data-testid="search-chatbot-link"
                    >
                      <MessageCircle className="w-4 h-4" />
                      Poser une question au chatbot
                    </button>
                  </div>
                )}

                {/* Suggestions when empty */}
                {query.length < 2 && (
                  <div className="px-5 py-8 text-center text-muted-foreground">
                    <p className="text-sm mb-3">Tapez au moins 2 caracteres pour rechercher</p>
                    <div className="flex flex-wrap gap-2 justify-center">
                      {['canal carpien', 'MDPH', 'IPP', 'AAH', 'expertise medicale', 'burn out', 'indemnisation', 'faute inexcusable'].map(s => (
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

                {/* Grouped results */}
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
                      {items.map((hit, i) => (
                        <button
                          key={hit.objectID}
                          onClick={() => handleSelect(hit)}
                          className="w-full flex items-start gap-3 px-5 py-3 hover:bg-muted/50 transition-colors text-left group"
                          data-testid={`search-result-${hit.objectID}`}
                        >
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate group-hover:text-accent transition-colors algolia-result-title">
                              {renderHighlight(hit, 'title')}
                            </p>
                            <p className="text-xs text-muted-foreground truncate mt-0.5 algolia-result-desc">
                              {renderHighlight(hit, 'description')}
                            </p>
                          </div>
                          <ArrowRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 mt-1" />
                        </button>
                      ))}
                    </div>
                  );
                })}
              </div>

              {/* Algolia attribution */}
              {results.length > 0 && (
                <div className="px-5 py-2 border-t border-border/50 flex justify-end">
                  <span className="text-[10px] text-muted-foreground/50">Recherche par Algolia</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <style>{`
        .algolia-hl { background: hsl(var(--accent) / 0.2); color: hsl(var(--accent-foreground)); border-radius: 2px; padding: 0 2px; }
      `}</style>
    </>
  );
};
