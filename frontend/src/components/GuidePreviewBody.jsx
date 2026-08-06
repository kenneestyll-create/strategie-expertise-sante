import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ChevronRight, AlertTriangle, CheckCircle, ShieldCheck, Lightbulb, X, Scale, Search, BookOpen } from 'lucide-react';
import { Button } from './ui/button';
import ReactMarkdown from 'react-markdown';

/**
 * Pixel-perfect rendering of a guide page body — used by both:
 *  - /guide/{slug} (public route) — wrapped in GuidePage with breadcrumb + analytics
 *  - Admin Studio preview modal — to validate exact rendering before publication
 *
 * Props match the seo_pages collection schema (content sub-document).
 */
export const GuidePreviewBody = ({ page, slug, currentYear, onCtaClick, isPreview = false }) => {
  const c = page?.content || {};
  const markdownBody = typeof c.markdown_body === 'string' ? c.markdown_body : '';
  const erreurs = Array.isArray(c.erreurs) ? c.erreurs : [];
  const solutions = Array.isArray(c.solutions) ? c.solutions : [];
  const orientation = Array.isArray(c.orientation) ? c.orientation : [];
  const blocages = Array.isArray(c.blocages) ? c.blocages : [];
  const maillage = Array.isArray(c.maillage) ? c.maillage : [];
  const ctaHref = `${page?.cta_type === 'accompagnement' ? '/agenda?type=conseil' : '/dossier-express'}?source=seo&page=${slug || ''}`;

  return (
    <>
      {/* H1 */}
      <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold leading-tight mb-10 text-foreground" data-testid="guide-title">
        {page.title}{currentYear ? ` en ${currentYear}` : ''}
      </h1>

      {/* Bloc Réponse Rapide */}
      {c.reponse_rapide && (
        <section className="mb-10" data-testid="guide-reponse-rapide">
          <div className="p-5 rounded-xl bg-[#1a1a2e]/[0.03] border border-[#C9A84C]/20">
            <h2 className="font-semibold text-base mb-3 text-foreground flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-[#C9A84C]" />
              {c.reponse_rapide_titre || page.title}
            </h2>
            <p className="text-sm leading-relaxed text-foreground/80 mb-4">{c.reponse_rapide}</p>
            {isPreview ? (
              <Button size="sm" className="bg-[#C9A84C] hover:bg-[#b8960f] text-[#1a1a2e] font-semibold gap-2 rounded-lg" data-testid="guide-reponse-rapide-cta" disabled>
                {page.cta_label || 'Se faire accompagner'}
                <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            ) : (
              <Link to={ctaHref}>
                <Button size="sm" className="bg-[#C9A84C] hover:bg-[#b8960f] text-[#1a1a2e] font-semibold gap-2 rounded-lg" data-testid="guide-reponse-rapide-cta">
                  {page.cta_label || 'Se faire accompagner'}
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </Link>
            )}
          </div>
        </section>
      )}

      {/* BLOC MARKDOWN BODY (legacy / fallback) */}
      {markdownBody && (
        <section className="mb-10" data-testid="guide-markdown-body">
          <div className="prose prose-neutral max-w-none prose-headings:font-semibold prose-h2:text-xl sm:prose-h2:text-2xl prose-h2:mt-10 prose-h2:mb-4 prose-h2:text-foreground prose-h3:text-base sm:prose-h3:text-lg prose-h3:mt-6 prose-h3:mb-3 prose-h3:text-foreground prose-p:text-sm prose-p:leading-relaxed prose-p:text-foreground/80 prose-li:text-sm prose-li:text-foreground/80 prose-strong:text-foreground prose-a:text-[#C9A84C] prose-a:no-underline hover:prose-a:underline">
            <ReactMarkdown
              skipHtml={false}
              components={{
                p: ({ node, children, ...props }) => {
                  const text = String(children || '');
                  if (text.includes('TERRAIN_HOOK:')) return null;
                  return <p className="text-sm leading-relaxed text-foreground/80 mb-4" {...props}>{children}</p>;
                },
                h2: ({ node, children, ...props }) => (
                  <h2 className="font-semibold text-lg sm:text-xl mt-8 mb-3 text-foreground" {...props}>{children}</h2>
                ),
                h3: ({ node, children, ...props }) => (
                  <h3 className="font-semibold text-base mt-6 mb-2 text-foreground" {...props}>{children}</h3>
                ),
                ul: ({ node, children, ...props }) => (
                  <ul className="list-disc pl-5 mb-4 space-y-1.5" {...props}>{children}</ul>
                ),
                ol: ({ node, children, ...props }) => (
                  <ol className="list-decimal pl-5 mb-4 space-y-1.5" {...props}>{children}</ol>
                ),
                li: ({ node, children, ...props }) => (
                  <li className="text-sm leading-relaxed text-foreground/80" {...props}>{children}</li>
                ),
                a: ({ node, children, ...props }) => (
                  <a className="text-[#C9A84C] font-medium hover:underline" {...props}>{children}</a>
                ),
                strong: ({ node, children, ...props }) => (
                  <strong className="font-semibold text-foreground" {...props}>{children}</strong>
                ),
              }}
            >
              {markdownBody.replace(/<!--\s*TERRAIN_HOOK:[^>]*-->/g, '')}
            </ReactMarkdown>
          </div>
        </section>
      )}

      {/* Contexte */}
      {(c.contexte || c.situation) && (
        <section className="mb-8" data-testid="guide-contexte">
          <div className="flex items-start gap-3 p-5 rounded-xl bg-amber-50/50 border border-amber-200/50">
            <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
            <div>
              <h2 className="font-semibold text-base mb-2 text-foreground">Contexte et situation</h2>
              <p className="text-sm leading-relaxed text-foreground/80 whitespace-pre-line">{c.contexte || c.situation}</p>
            </div>
          </div>
        </section>
      )}

      {/* Limites */}
      {(c.limites || c.explication) && (
        <section className="mb-8" data-testid="guide-limites">
          <h2 className="font-semibold text-lg mb-3 text-foreground flex items-center gap-2">
            <Search className="w-4 h-4 text-[#C9A84C]" />
            Ce que les textes officiels ne vous disent pas
          </h2>
          <p className="text-sm leading-relaxed text-foreground/80 whitespace-pre-line">{c.limites || c.explication}</p>
        </section>
      )}

      {/* Blocages */}
      {blocages.length > 0 && (
        <section className="mb-8" data-testid="guide-blocages">
          <h2 className="font-semibold text-lg mb-3 text-foreground flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-[#C9A84C]" />
            Les blocages réels rencontrés dans les dossiers
          </h2>
          <div className="space-y-3">
            {blocages.map((b, i) => (
              <div key={i} className="flex gap-3 items-start p-3 rounded-lg bg-muted/30 border border-border/50">
                <span className="flex items-center justify-center w-5 h-5 rounded-full bg-amber-500/10 text-amber-700 text-[10px] font-bold shrink-0 mt-0.5">{i + 1}</span>
                <p className="text-sm leading-relaxed text-foreground/80">{b}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Solutions (legacy fallback) */}
      {solutions.length > 0 && blocages.length === 0 && (
        <section className="mb-8" data-testid="guide-solutions">
          <h2 className="font-semibold text-lg mb-3 text-foreground flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-600" />
            Solutions concrètes
          </h2>
          <div className="space-y-3">
            {solutions.map((step, i) => (
              <div key={i} className="flex gap-3 items-start">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[#1a1a2e] text-white text-xs font-bold shrink-0">{i + 1}</span>
                <p className="text-sm leading-relaxed text-foreground/80 pt-0.5">{step}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Erreurs */}
      {erreurs.length > 0 && (
        <section className="mb-8" data-testid="guide-erreurs">
          <h2 className="font-semibold text-lg mb-3 text-foreground">Erreurs fréquentes à éviter</h2>
          <ul className="space-y-2">
            {erreurs.map((err, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-foreground/80">
                <X className="w-3.5 h-3.5 text-red-500 mt-0.5 shrink-0" />
                <span>{err}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* ===== P0-2 : CTA intermédiaire de conversion ===== */}
      {(erreurs.length > 0 || solutions.length > 0 || blocages.length > 0) && (
        <section className="mb-10" data-testid="guide-cta-mid">
          <div className="p-5 sm:p-6 rounded-xl border-2 border-[#C9A84C]/30 bg-gradient-to-br from-[#C9A84C]/5 to-[#C9A84C]/10">
            <p className="text-sm font-semibold text-foreground mb-1">
              Votre situation ressemble à ce guide ?
            </p>
            <p className="text-sm text-foreground/70 mb-4">
              Chaque dossier est unique. Un audit personnalisé permet d'identifier les leviers spécifiques à votre situation et de sécuriser votre stratégie de recours.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                asChild
                size="lg"
                className="flex-1 bg-[#C9A84C] hover:bg-[#b8960f] text-[#1a1a2e] font-semibold"
                data-testid="guide-cta-mid-dossier"
                onClick={() => {
                  try { window.clarity && window.clarity('event', 'guide_cta_mid_dossier_click'); } catch (e) { /* silent */ }
                }}
              >
                <Link to={ctaHref}>
                  Auditer mon dossier
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="flex-1 border-[#C9A84C]/40 hover:bg-[#C9A84C]/10 font-semibold"
                data-testid="guide-cta-mid-rdv"
                onClick={() => {
                  try { window.clarity && window.clarity('event', 'guide_cta_mid_rdv_click'); } catch (e) { /* silent */ }
                }}
              >
                <Link to={`/agenda?type=conseil&source=guide&page=${slug || ''}`}>
                  Prendre RDV
                </Link>
              </Button>
            </div>
            <p className="text-xs text-foreground/60 mt-3 text-center">
              Réponse sous 48 h — Sans engagement — 100 % confidentiel
            </p>
          </div>
        </section>
      )}

      {/* Stratégie */}
      {c.strategie && (
        <section className="mb-8" data-testid="guide-strategie">
          <h2 className="font-semibold text-lg mb-3 text-foreground flex items-center gap-2">
            <Scale className="w-4 h-4 text-[#C9A84C]" />
            Lecture stratégique du dossier
          </h2>
          <div className="p-5 rounded-xl bg-[#1a1a2e]/5 border border-[#C9A84C]/15">
            <p className="text-sm leading-relaxed text-foreground/80 whitespace-pre-line">{c.strategie}</p>
          </div>
        </section>
      )}

      {/* Orientation */}
      {orientation.length > 0 && (
        <section className="mb-8" data-testid="guide-orientation">
          <h2 className="font-semibold text-lg mb-3 text-foreground flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-600" />
            Ce que vous devez faire maintenant
          </h2>
          <div className="space-y-3">
            {orientation.map((step, i) => (
              <div key={i} className="flex gap-3 items-start">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[#1a1a2e] text-white text-xs font-bold shrink-0">{i + 1}</span>
                <p className="text-sm leading-relaxed text-foreground/80 pt-0.5">{step}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Réassurance */}
      {c.reassurance && (
        <section className="mb-8" data-testid="guide-reassurance">
          <div className="flex items-start gap-3 p-5 rounded-xl bg-emerald-50/50 border border-emerald-200/50">
            <ShieldCheck className="w-5 h-5 text-emerald-600 mt-0.5 shrink-0" />
            <div>
              <h2 className="font-semibold text-base mb-2 text-foreground">Vous n'êtes pas seul(e)</h2>
              <p className="text-sm leading-relaxed text-foreground/80 whitespace-pre-line">{c.reassurance}</p>
            </div>
          </div>
        </section>
      )}

      {/* Maillage */}
      {maillage.length > 0 && (
        <section className="mb-10" data-testid="guide-maillage">
          <h2 className="font-semibold text-sm mb-3 text-muted-foreground flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            Pour aller plus loin
          </h2>
          <div className="grid gap-2">
            {maillage.map((link, i) => {
              const target = link.href || `/guide/${link.slug}`;
              return isPreview ? (
                <div key={i} className="flex items-center gap-2 p-3 rounded-lg border border-border/50 text-sm text-foreground/80">
                  <ChevronRight className="w-3.5 h-3.5 text-[#C9A84C] shrink-0" />
                  <span>{link.text}</span>
                  <span className="text-[10px] text-muted-foreground ml-auto">{target}</span>
                </div>
              ) : (
                <Link key={i} to={target} className="flex items-center gap-2 p-3 rounded-lg border border-border/50 hover:border-[#C9A84C]/40 hover:bg-[#C9A84C]/5 transition-colors text-sm text-foreground/80 hover:text-foreground">
                  <ChevronRight className="w-3.5 h-3.5 text-[#C9A84C] shrink-0" />
                  <span>{link.text}</span>
                </Link>
              );
            })}
          </div>
        </section>
      )}

      {/* FAQ */}
      {Array.isArray(c.faq) && c.faq.length > 0 && (
        <section className="mb-10" data-testid="guide-faq">
          <h2 className="font-semibold text-lg mb-4 text-foreground">Questions fréquentes</h2>
          <div className="space-y-4">
            {c.faq.map((q, i) => (
              <div key={i} className="p-4 rounded-lg border border-border/50">
                <h3 className="font-semibold text-sm mb-2 text-foreground">{q.question}</h3>
                <p className="text-sm leading-relaxed text-foreground/80 whitespace-pre-line">{q.answer}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* CTA */}
      <section className="mb-12" data-testid="guide-cta">
        <div className="p-6 rounded-xl bg-[#1a1a2e] text-center">
          <p className="text-white/80 text-sm mb-4">Besoin d'une lecture stratégique de votre dossier ?</p>
          <Button
            onClick={onCtaClick}
            disabled={isPreview}
            className="bg-[#C9A84C] hover:bg-[#b8960f] text-[#1a1a2e] font-semibold px-8 h-12 text-sm gap-2"
            data-testid="guide-cta-button"
          >
            {page.cta_label || 'Analyser mon dossier maintenant'}
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </section>
    </>
  );
};

export default GuidePreviewBody;
