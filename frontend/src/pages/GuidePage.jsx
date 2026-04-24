import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowRight, ChevronRight, AlertTriangle, CheckCircle, ShieldCheck, Lightbulb, X, Scale, Search, BookOpen } from 'lucide-react';
import { Button } from '../components/ui/button';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const CURRENT_YEAR = new Date().getFullYear();

const GuidePage = () => {
  const { slug } = useParams();
  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    axios.get(`${API}/guide/${slug}`)
      .then(res => setPage(res.data))
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [slug]);

  useEffect(() => {
    if (!page) return;
    const titleWithYear = `${page.title} en ${CURRENT_YEAR}`;
    document.title = `${titleWithYear} — Stratégie & Expertise Santé`;
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) metaDesc.setAttribute('content', page.meta_description || '');

    // Canonical URL — production domain
    let canonicalLink = document.querySelector('link[rel="canonical"]');
    if (!canonicalLink) {
      canonicalLink = document.createElement('link');
      canonicalLink.setAttribute('rel', 'canonical');
      document.head.appendChild(canonicalLink);
    }
    canonicalLink.setAttribute('href', `https://strategie-expertise-sante.fr/guide/${slug}`);

    // Open Graph URL
    let ogUrl = document.querySelector('meta[property="og:url"]');
    if (ogUrl) ogUrl.setAttribute('content', `https://strategie-expertise-sante.fr/guide/${slug}`);

    // Schema.org FAQPage structured data
    const faq = page.content?.faq;
    if (faq && faq.length > 0) {
      const existing = document.getElementById('faq-schema');
      if (existing) existing.remove();
      const script = document.createElement('script');
      script.id = 'faq-schema';
      script.type = 'application/ld+json';
      script.textContent = JSON.stringify({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq.map(f => ({
          "@type": "Question",
          "name": f.question,
          "acceptedAnswer": { "@type": "Answer", "text": f.answer }
        }))
      });
      document.head.appendChild(script);
      return () => { const el = document.getElementById('faq-schema'); if (el) el.remove(); };
    }
  }, [page, slug]);

  const handleCtaClick = () => {
    axios.post(`${API}/guide/${slug}/cta-click`).catch(() => {});
    const dest = page?.cta_type === 'accompagnement' ? '/agenda?type=conseil&' : '/dossier-express?';
    window.location.href = `${dest}source=seo&page=${slug}`;
  };

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-[#C9A84C] border-t-transparent rounded-full animate-spin" />
      </main>
    );
  }

  if (notFound || !page) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center gap-4 px-4">
        <h1 className="text-2xl font-bold">Page non trouvée</h1>
        <p className="text-muted-foreground">Ce guide n'existe pas ou a été désactivé.</p>
        <Link to="/guides-pratiques" className="text-[#C9A84C] hover:underline">Voir tous les guides</Link>
      </main>
    );
  }

  const c = page.content || {};
  const erreurs = Array.isArray(c.erreurs) ? c.erreurs : [];
  const solutions = Array.isArray(c.solutions) ? c.solutions : [];
  const orientation = Array.isArray(c.orientation) ? c.orientation : [];
  const blocages = Array.isArray(c.blocages) ? c.blocages : [];
  const maillage = Array.isArray(c.maillage) ? c.maillage : [];

  return (
    <main className="min-h-screen bg-background" data-testid="guide-page">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-xs text-muted-foreground mb-8" data-testid="guide-breadcrumb">
          <Link to="/" className="hover:text-foreground transition-colors">Accueil</Link>
          <ChevronRight className="w-3 h-3" />
          <Link to="/guides-pratiques" className="hover:text-foreground transition-colors">Guides</Link>
          <ChevronRight className="w-3 h-3" />
          <span className="text-foreground/70 truncate max-w-[200px]">{page.title}</span>
        </nav>

        {/* H1 */}
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold leading-tight mb-10 text-foreground" data-testid="guide-title">
          {page.title} en {CURRENT_YEAR}
        </h1>

        {/* Bloc Réponse Rapide (conditionnel) */}
        {c.reponse_rapide && (
          <section className="mb-10" data-testid="guide-reponse-rapide">
            <div className="p-5 rounded-xl bg-[#1a1a2e]/[0.03] border border-[#C9A84C]/20">
              <h2 className="font-semibold text-base mb-3 text-foreground flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-[#C9A84C]" />
                {c.reponse_rapide_titre || page.title}
              </h2>
              <p className="text-sm leading-relaxed text-foreground/80 mb-4">{c.reponse_rapide}</p>
              <Link to={`${page.cta_type === 'accompagnement' ? '/agenda?type=conseil' : '/dossier-express'}?source=seo&page=${slug}`}>
                <Button size="sm" className="bg-[#C9A84C] hover:bg-[#b8960f] text-[#1a1a2e] font-semibold gap-2 rounded-lg" data-testid="guide-reponse-rapide-cta">
                  {page.cta_label || 'Se faire accompagner'}
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </Link>
            </div>
          </section>
        )}

        {/* BLOC 1 — Contexte rapide / Situation */}
        {(c.contexte || c.situation) && (
          <section className="mb-8" data-testid="guide-contexte">
            <div className="flex items-start gap-3 p-5 rounded-xl bg-amber-50/50 border border-amber-200/50">
              <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
              <div>
                <h2 className="font-semibold text-base mb-2 text-foreground">Contexte et situation</h2>
                <p className="text-sm leading-relaxed text-foreground/80">{c.contexte || c.situation}</p>
              </div>
            </div>
          </section>
        )}

        {/* BLOC 2 — Limites de la lecture administrative */}
        {(c.limites || c.explication) && (
          <section className="mb-8" data-testid="guide-limites">
            <h2 className="font-semibold text-lg mb-3 text-foreground flex items-center gap-2">
              <Search className="w-4 h-4 text-[#C9A84C]" />
              Ce que les textes officiels ne vous disent pas
            </h2>
            <p className="text-sm leading-relaxed text-foreground/80">{c.limites || c.explication}</p>
          </section>
        )}

        {/* BLOC 3 — Analyse des blocages réels */}
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

        {/* Fallback: Solutions (old format) */}
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

        {/* BLOC 4 — Erreurs fréquentes */}
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

        {/* BLOC 5 — Lecture stratégique */}
        {c.strategie && (
          <section className="mb-8" data-testid="guide-strategie">
            <h2 className="font-semibold text-lg mb-3 text-foreground flex items-center gap-2">
              <Scale className="w-4 h-4 text-[#C9A84C]" />
              Lecture stratégique du dossier
            </h2>
            <div className="p-5 rounded-xl bg-[#1a1a2e]/5 border border-[#C9A84C]/15">
              <p className="text-sm leading-relaxed text-foreground/80">{c.strategie}</p>
            </div>
          </section>
        )}

        {/* BLOC 6 — Orientation concrète */}
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
                <p className="text-sm leading-relaxed text-foreground/80">{c.reassurance}</p>
              </div>
            </div>
          </section>
        )}

        {/* Maillage interne */}
        {maillage.length > 0 && (
          <section className="mb-10" data-testid="guide-maillage">
            <h2 className="font-semibold text-sm mb-3 text-muted-foreground flex items-center gap-2">
              <BookOpen className="w-4 h-4" />
              Guides connexes
            </h2>
            <div className="grid gap-2">
              {maillage.map((link, i) => (
                <Link key={i} to={`/guide/${link.slug}`} className="flex items-center gap-2 p-3 rounded-lg border border-border/50 hover:border-[#C9A84C]/40 hover:bg-[#C9A84C]/5 transition-colors text-sm text-foreground/80 hover:text-foreground">
                  <ChevronRight className="w-3.5 h-3.5 text-[#C9A84C] shrink-0" />
                  <span>{link.text}</span>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* CTA */}
        <section className="mb-12" data-testid="guide-cta">
          <div className="p-6 rounded-xl bg-[#1a1a2e] text-center">
            <p className="text-white/80 text-sm mb-4">Besoin d'une lecture stratégique de votre dossier ?</p>
            <Button
              onClick={handleCtaClick}
              className="bg-[#C9A84C] hover:bg-[#b8960f] text-[#1a1a2e] font-semibold px-8 h-12 text-sm gap-2"
              data-testid="guide-cta-button"
            >
              {page.cta_label || 'Analyser mon dossier maintenant'}
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </section>
      </div>
    </main>
  );
};

export default GuidePage;
