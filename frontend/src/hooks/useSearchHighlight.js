import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * On page load, if URL contains ?highlight=... and/or a #hash,
 * scroll to the hash anchor and highlight matching text in the page.
 * Highlights auto-fade after 4 seconds.
 */
export const useSearchHighlight = () => {
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const highlight = params.get('highlight');
    const hash = location.hash?.replace('#', '');

    if (!highlight && !hash) return;

    // Wait for page content to render
    const timer = setTimeout(() => {
      // 1. Scroll to anchor if present
      if (hash) {
        const anchor = document.getElementById(hash);
        if (anchor) {
          anchor.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }

      // 2. Highlight matching terms
      if (highlight && highlight.length >= 2) {
        const terms = highlight.toLowerCase().split(/\s+/).filter(t => t.length >= 2);
        if (terms.length === 0) return;

        const regex = new RegExp(`(${terms.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'gi');

        // Walk text nodes in main content
        const main = document.querySelector('main') || document.querySelector('.App');
        if (!main) return;

        const walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, {
          acceptNode: (node) => {
            const tag = node.parentElement?.tagName;
            if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'INPUT', 'TEXTAREA'].includes(tag)) return NodeFilter.FILTER_REJECT;
            if (node.parentElement?.closest('[data-no-highlight]')) return NodeFilter.FILTER_REJECT;
            return regex.test(node.textContent) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
          }
        });

        const marks = [];
        const textNodes = [];
        while (walker.nextNode()) textNodes.push(walker.currentNode);

        // Limit to first 20 matches to avoid performance issues
        let count = 0;
        for (const textNode of textNodes) {
          if (count >= 20) break;
          const parent = textNode.parentElement;
          if (!parent || parent.tagName === 'MARK') continue;

          const text = textNode.textContent;
          const parts = text.split(regex);
          if (parts.length <= 1) continue;

          const fragment = document.createDocumentFragment();
          parts.forEach(part => {
            if (regex.test(part)) {
              const mark = document.createElement('mark');
              mark.className = 'search-highlight';
              mark.textContent = part;
              fragment.appendChild(mark);
              marks.push(mark);
              count++;
            } else {
              fragment.appendChild(document.createTextNode(part));
            }
            // Reset regex lastIndex
            regex.lastIndex = 0;
          });

          parent.replaceChild(fragment, textNode);
        }

        // Scroll to first highlight if no anchor
        if (!hash && marks.length > 0) {
          marks[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        // Auto-fade highlights after 4s
        const fadeTimer = setTimeout(() => {
          marks.forEach(mark => {
            mark.classList.add('search-highlight-fade');
          });
        }, 4000);

        return () => clearTimeout(fadeTimer);
      }
    }, 600);

    return () => clearTimeout(timer);
  }, [location.search, location.hash]);
};
