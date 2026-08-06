import { Link } from 'react-router-dom';
import { ChevronRight, BookOpen } from 'lucide-react';

export const SeoRelatedLinks = ({ title = 'Pour aller plus loin', links, testId = 'seo-related-links' }) => (
  <section className="mt-10 mb-2" data-testid={testId}>
    <h2 className="font-semibold text-sm mb-3 text-muted-foreground flex items-center gap-2">
      <BookOpen className="w-4 h-4" />
      {title}
    </h2>
    <div className="grid gap-2 sm:grid-cols-2">
      {links.map((l, i) => (
        <Link
          key={i}
          to={l.href}
          className="flex items-center gap-2 p-3 rounded-lg border border-border/50 hover:border-[#C9A84C]/40 hover:bg-[#C9A84C]/5 transition-colors text-sm text-foreground/80 hover:text-foreground"
          data-testid={`${testId}-item-${i}`}
        >
          <ChevronRight className="w-3.5 h-3.5 text-[#C9A84C] shrink-0" />
          <span>{l.text}</span>
        </Link>
      ))}
    </div>
  </section>
);
