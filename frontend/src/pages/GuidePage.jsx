import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowRight, ChevronRight, AlertTriangle, CheckCircle, ShieldCheck, Lightbulb, X } from 'lucide-react';
import { Button } from '../components/ui/button';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

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

  const handleCtaClick = () => {
    axios.post(`${API}/guide/${slug}/cta-click`).catch(() => {});
    const dest = page?.cta_type === 'accompagnement' ? '/agenda?type=conseil' : '/dossier-express';
    window.location.href = `${dest}?source=seo&page=${slug}`;
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

  const content = page.content || {};
  const solutions = Array.isArray(content.solutions) ? content.solutions : [];
  const erreurs = Array.isArray(content.erreurs) ? content.erreurs : [];

  // Set document title + meta without Helmet (avoids crash with Emergent overlay)
  document.title = `${page.title} — Stratégie & Expertise Santé`;

  return (
    <main className="min-h-screen bg-background" data-testid="guide-page">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        <nav className="flex items-center gap-1.5 text-xs text-muted-foreground mb-8" data-testid="guide-breadcrumb">
          <Link to="/" className="hover:text-foreground transition-colors">Accueil</Link>
          <ChevronRight className="w-3 h-3" />
          <Link to="/guides-pratiques" className="hover:text-foreground transition-colors">Guides</Link>
          <ChevronRight className="w-3 h-3" />
          <span className="text-foreground/70 truncate max-w-[200px]">{page.title}</span>
        </nav>

        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold leading-tight mb-10 text-foreground" data-testid="guide-title">
          {page.title}
        </h1>

        {content.situation && (
          <section className="mb-8" data-testid="guide-situation">
            <div className="flex items-start gap-3 p-5 rounded-xl bg-amber-50/50 border border-amber-200/50">
              <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
              <div>
                <h2 className="font-semibold text-base mb-2 text-foreground">Votre situation</h2>
                <p className="text-sm leading-relaxed text-foreground/80">{content.situation}</p>
              </div>
            </div>
          </section>
        )}

        {content.explication && (
          <section className="mb-8" data-testid="guide-explication">
            <h2 className="font-semibold text-lg mb-3 text-foreground flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-[#C9A84C]" />
              Pourquoi cela arrive
            </h2>
            <p className="text-sm leading-relaxed text-foreground/80">{content.explication}</p>
          </section>
        )}

        {solutions.length > 0 && (
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

        {content.reassurance && (
          <section className="mb-10" data-testid="guide-reassurance">
            <div className="flex items-start gap-3 p-5 rounded-xl bg-emerald-50/50 border border-emerald-200/50">
              <ShieldCheck className="w-5 h-5 text-emerald-600 mt-0.5 shrink-0" />
              <div>
                <h2 className="font-semibold text-base mb-2 text-foreground">Vous n'êtes pas seul(e)</h2>
                <p className="text-sm leading-relaxed text-foreground/80">{content.reassurance}</p>
              </div>
            </div>
          </section>
        )}

        <section className="mb-12" data-testid="guide-cta">
          <div className="p-6 rounded-xl bg-[#1a1a2e] text-center">
            <p className="text-white/80 text-sm mb-4">Besoin d'aide pour votre situation ?</p>
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
