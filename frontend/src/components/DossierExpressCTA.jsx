import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

/**
 * Encart de conversion sobre vers /dossier-express.
 * Design : barre dorée verticale, fond très discret, typographie serif sur le titre.
 * À placer juste avant la FAQ sur les pages stratégiques SEO.
 */
export const DossierExpressCTA = ({ title, text, ctaLabel, testId }) => {
  return (
    <section className="px-4 sm:px-6 lg:px-8 py-12 sm:py-14" data-testid={testId || 'dossier-express-cta'}>
      <div className="max-w-4xl mx-auto">
        <div className="relative bg-[#1a1a2e]/[0.025] border border-border/60 rounded-2xl px-6 sm:px-10 py-8 sm:py-10 overflow-hidden">
          {/* Fine accent line */}
          <div className="absolute left-0 top-6 bottom-6 w-[2px] bg-accent/70 rounded-full" aria-hidden="true" />
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div className="flex-1 max-w-2xl">
              <h3 className="font-serif text-xl sm:text-2xl text-foreground mb-3 leading-snug">
                {title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {text}
              </p>
            </div>
            <div className="flex-shrink-0">
              <Link
                to="/dossier-express"
                className="group inline-flex items-center gap-2 px-5 py-2.5 rounded-full border border-accent/40 bg-background hover:bg-accent hover:text-accent-foreground hover:border-accent transition-colors duration-300 text-sm font-medium text-foreground"
                data-testid={`${testId || 'dossier-express'}-link`}
              >
                <span>{ctaLabel}</span>
                <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-0.5" strokeWidth={1.75} />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
