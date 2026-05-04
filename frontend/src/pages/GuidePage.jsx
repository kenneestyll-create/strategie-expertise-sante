import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import axios from 'axios';
import { GuidePreviewBody } from '../components/GuidePreviewBody';

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
      document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
        try { if (JSON.parse(s.textContent)['@type'] === 'FAQPage') s.remove(); } catch {}
      });
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
  const markdownBody = typeof c.markdown_body === 'string' ? c.markdown_body : '';
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

        <GuidePreviewBody
          page={page}
          slug={slug}
          currentYear={CURRENT_YEAR}
          onCtaClick={handleCtaClick}
          isPreview={false}
        />
      </div>
    </main>
  );
};

export default GuidePage;
