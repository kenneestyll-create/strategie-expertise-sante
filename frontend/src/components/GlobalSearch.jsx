import { useState, useEffect, useRef, useCallback } from 'react';
import { Search, X, Sparkles, ArrowRight } from 'lucide-react';
import { liteClient as algoliasearch } from 'algoliasearch/lite';

const searchClient = algoliasearch(
  process.env.REACT_APP_ALGOLIA_APP_ID,
  process.env.REACT_APP_ALGOLIA_SEARCH_KEY
);
const INDEX_NAME = process.env.REACT_APP_ALGOLIA_INDEX_NAME;

const SUGGESTIONS = [
  "Comment preparer une expertise medicale ?",
  "Quels sont mes droits apres un accident du travail ?",
  "Comment contester un taux d'IPP ?",
  "Qu'est-ce que la PGPF ?",
  "Comment faire un dossier MDPH ?",
  "C'est quoi la faute inexcusable ?",
];

export const GlobalSearch = () => {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [hints, setHints] = useState([]);
  const inputRef = useRef(null);
  const debounceRef = useRef(null);

  // Fetch light Algolia hints while typing (quick page suggestions)
  useEffect(() => {
    if (!query || query.trim().length < 2) { setHints([]); return; }
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      try {
        const { results } = await searchClient.search({
          requests: [{
            indexName: INDEX_NAME,
            query: query.trim(),
            hitsPerPage: 5,
            attributesToRetrieve: ['title', 'href', 'anchor', 'category'],
            attributesToHighlight: [],
          }],
        });
        setHints(results?.[0]?.hits || []);
      } catch { setHints([]); }
    }, 250);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [query]);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 100);
    else { setQuery(''); setHints([]); }
  }, [open]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); setOpen(p => !p); }
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  // Send question to chatbot IA
  const askAI = useCallback((text) => {
    if (!text || !text.trim()) return;
    setOpen(false);
    // Dispatch custom event that ChatBot listens to
    window.dispatchEvent(new CustomEvent('strate-ask-ai', { detail: { question: text.trim() } }));
  }, []);

  const handleSubmit = useCallback((e) => {
    e?.preventDefault();
    askAI(query);
  }, [query, askAI]);

  return (
    <>
      {/* Trigger button */}
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 px-4 py-2 rounded-full border border-[#C9A84C]/30 bg-[#C9A84C]/5 hover:bg-[#C9A84C]/10 text-muted-foreground text-sm transition-colors"
        data-testid="global-search-trigger"
        aria-label="Rechercher"
      >
        <Sparkles className="w-4 h-4 text-[#C9A84C]" />
        <span className="hidden sm:inline">Votre question...</span>
      </button>

      {/* Overlay */}
      {open && (
        <div className="fixed inset-0" style={{ zIndex: 'var(--z-modal)' }} data-testid="global-search-overlay">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setOpen(false)} />
          <div className="relative max-w-2xl mx-auto mt-[10vh]">
            <div className="bg-background border border-border rounded-2xl shadow-2xl overflow-hidden mx-4" data-testid="global-search-panel">

              {/* Search Input */}
              <form onSubmit={handleSubmit} className="flex items-center gap-3 px-5 py-4 border-b border-border">
                <Sparkles className="w-5 h-5 text-[#C9A84C] flex-shrink-0" />
                <input
                  ref={inputRef}
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="Votre question..."
                  className="flex-1 bg-transparent outline-none text-base placeholder:text-muted-foreground"
                  data-testid="global-search-input"
                />
                {query.trim().length > 0 && (
                  <button
                    type="submit"
                    className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-[#C9A84C] text-black text-sm font-medium hover:bg-[#C9A84C]/90 transition-colors"
                    data-testid="search-ask-ai-btn"
                  >
                    <Sparkles className="w-3.5 h-3.5" /> Demander
                  </button>
                )}
                {query && (
                  <button type="button" onClick={() => setQuery('')} className="p-1 hover:bg-muted rounded-md">
                    <X className="w-4 h-4 text-muted-foreground" />
                  </button>
                )}
                <button type="button" onClick={() => setOpen(false)} className="px-2 py-1 text-xs text-muted-foreground border border-border rounded-md hover:bg-muted">
                  Esc
                </button>
              </form>

              {/* Content area */}
              <div className="max-h-[55vh] overflow-y-auto" data-testid="global-search-results">

                {/* Algolia quick links while typing */}
                {hints.length > 0 && (
                  <div>
                    <div className="px-5 py-2 bg-muted/30 border-b border-border/50">
                      <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                        <Search className="w-3 h-3" /> Pages suggerees
                      </span>
                    </div>
                    {hints.map(hit => (
                      <button
                        key={hit.objectID}
                        onClick={() => {
                          setOpen(false);
                          const url = hit.anchor ? `${hit.href}#${hit.anchor}` : hit.href;
                          window.location.href = url;
                        }}
                        className="w-full flex items-center gap-3 px-5 py-2.5 hover:bg-muted/50 transition-colors text-left group"
                        data-testid={`search-hint-${hit.objectID}`}
                      >
                        <span className="text-sm flex-1 truncate">{hit.title}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                      </button>
                    ))}
                    <div className="px-5 py-2 border-t border-border/50 bg-muted/20">
                      <button
                        onClick={handleSubmit}
                        className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-[#C9A84C]/10 hover:bg-[#C9A84C]/20 text-[#C9A84C] text-sm font-medium transition-colors"
                        data-testid="search-ask-ai-instead"
                      >
                        <Sparkles className="w-4 h-4" /> Ou demander a l'IA : "{query}"
                      </button>
                    </div>
                  </div>
                )}

                {/* Default suggestions when empty */}
                {query.length < 2 && (
                  <div className="px-5 py-6">
                    <p className="text-sm text-muted-foreground mb-4 flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-[#C9A84C]" />
                      Posez votre question — notre IA vous repond instantanement
                    </p>
                    <div className="space-y-1.5">
                      {SUGGESTIONS.map(s => (
                        <button
                          key={s}
                          onClick={() => askAI(s)}
                          className="w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm rounded-xl hover:bg-muted/60 transition-colors group"
                          data-testid={`search-suggestion-${s.slice(0, 20).replace(/\s+/g, '-').toLowerCase()}`}
                        >
                          <Sparkles className="w-3.5 h-3.5 text-[#C9A84C]/60 group-hover:text-[#C9A84C] flex-shrink-0 transition-colors" />
                          <span className="text-muted-foreground group-hover:text-foreground transition-colors">{s}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* No Algolia results but user is typing */}
                {query.length >= 2 && hints.length === 0 && (
                  <div className="px-5 py-6 text-center">
                    <Sparkles className="w-8 h-8 text-[#C9A84C] mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground mb-3">Appuyez sur <strong>Entree</strong> pour poser votre question a l'IA</p>
                    <button
                      onClick={handleSubmit}
                      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-[#C9A84C] text-black text-sm font-medium hover:bg-[#C9A84C]/90 transition-colors"
                      data-testid="search-ask-ai-empty"
                    >
                      <Sparkles className="w-4 h-4" /> Demander a l'IA
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
