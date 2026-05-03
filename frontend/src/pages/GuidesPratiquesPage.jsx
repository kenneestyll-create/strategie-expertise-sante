import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, FileText, Scale, Stethoscope, HardHat, BriefcaseBusiness } from 'lucide-react';
import { SEO } from '../components/SEO';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const CATEGORIES = {
  mdph: { label: 'MDPH', icon: FileText, color: 'text-blue-600', bg: 'bg-blue-50 border-blue-200/50' },
  accident_travail: { label: 'Accident du travail', icon: HardHat, color: 'text-orange-600', bg: 'bg-orange-50 border-orange-200/50' },
  expertise: { label: 'Expertise médicale', icon: Stethoscope, color: 'text-red-600', bg: 'bg-red-50 border-red-200/50' },
  indemnisation: { label: 'Indemnisation', icon: Scale, color: 'text-emerald-600', bg: 'bg-emerald-50 border-emerald-200/50' },
  emploi: { label: 'Emploi', icon: BriefcaseBusiness, color: 'text-purple-600', bg: 'bg-purple-50 border-purple-200/50' },
};

const GuidesPratiquesPage = () => {
  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/guides`)
      .then(res => setPages(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  // Group by category
  const grouped = {};
  pages.forEach(p => {
    const cat = p.category || 'autre';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(p);
  });

  return (
    <main className="min-h-screen bg-background" data-testid="guides-hub">
      <SEO title="Guides pratiques — Maladie professionnelle, AT/MP, MDPH" description="Guides concrets et actionnables : refus MDPH, contestation taux IPP, maladie professionnelle, expertise médicale. Solutions et stratégies pour faire valoir vos droits." path="/guides-pratiques" />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-xs text-muted-foreground mb-8" data-testid="guides-breadcrumb">
          <Link to="/" className="hover:text-foreground transition-colors">Accueil</Link>
          <ChevronRight className="w-3 h-3" />
          <span className="text-foreground/70">Guides pratiques</span>
        </nav>

        <h1 className="text-2xl sm:text-3xl font-bold mb-3 text-foreground">Guides pratiques</h1>
        <p className="text-sm text-muted-foreground mb-10 max-w-xl">
          Situations concrètes et solutions actionnables pour vos démarches santé, accident du travail, MDPH et expertise médicale.
        </p>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-6 h-6 border-2 border-[#C9A84C] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : pages.length === 0 ? (
          <p className="text-center text-muted-foreground py-12">Aucun guide disponible pour le moment.</p>
        ) : (
          <div className="space-y-10">
            {Object.entries(grouped).map(([cat, catPages]) => {
              const catInfo = CATEGORIES[cat] || { label: cat, icon: FileText, color: 'text-gray-600', bg: 'bg-gray-50 border-gray-200/50' };
              const Icon = catInfo.icon;
              return (
                <section key={cat} data-testid={`guides-category-${cat}`}>
                  <div className="flex items-center gap-2 mb-4">
                    <Icon className={`w-5 h-5 ${catInfo.color}`} />
                    <h2 className="font-semibold text-lg">{catInfo.label}</h2>
                    <span className="text-xs text-muted-foreground">({catPages.length})</span>
                  </div>
                  <div className="grid gap-3">
                    {catPages.map(p => (
                      <Link
                        key={p.slug}
                        to={`/guide/${p.slug}`}
                        className={`block p-4 rounded-lg border ${catInfo.bg} hover:shadow-sm transition-shadow`}
                        data-testid={`guide-card-${p.slug}`}
                      >
                        <h3 className="font-medium text-sm text-foreground mb-1">{p.title}</h3>
                        <p className="text-xs text-muted-foreground line-clamp-2">{p.meta_description}</p>
                      </Link>
                    ))}
                  </div>
                </section>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
};

export default GuidesPratiquesPage;
