import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowRight, Calendar, FileText, Scale, Heart, Award, Download, ChevronLeft, ChevronRight, Shield, Trophy, Gavel, BookOpen, Users, Star, CheckCircle } from 'lucide-react';
import { SEO } from '@/components/SEO';

export const AboutPage = () => {
  const [pdfError, setPdfError] = useState(false);
  const [pdfVisible, setPdfVisible] = useState(false);
  const pdfSectionRef = useRef(null);

  useEffect(() => {
    const ref = pdfSectionRef.current;
    if (!ref) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setPdfVisible(true); observer.disconnect(); } },
      { rootMargin: '200px' }
    );
    observer.observe(ref);
    return () => observer.disconnect();
  }, []);
  const timeline = [
    {
      year: "Année 1",
      title: "Le diagnostic et l'incompréhension",
      description: "Diagnostic d'une maladie professionnelle. Premiers pas dans les démarches de reconnaissance auprès de la CPAM. Découverte d'un univers administratif complexe et souvent hostile, où l'on se sent seul face à la machine.",
      icon: FileText,
      badge: "CPAM / AT-MP",
      color: "from-blue-600 to-blue-800"
    },
    {
      year: "Année 2",
      title: "Les expertises médicales",
      description: "Multiplication des rendez-vous médicaux et expertises judiciaires. Découverte du fonctionnement du CRRMP. Apprentissage forcé du vocabulaire médico-administratif et des rouages du système.",
      icon: Scale,
      badge: "CRRMP / Expertises",
      color: "from-amber-600 to-amber-800"
    },
    {
      year: "Année 3-4",
      title: "Les victoires contre les assureurs",
      description: "Face aux grands groupes d'assurance nationaux, début d'un bras de fer pour la reconnaissance des garanties PTIA et ITT. Batailles juridiques intenses, refus successifs, recours méthodiques — et finalement, des succès déterminants.",
      icon: Trophy,
      badge: "PTIA / ITT",
      badgeColor: "bg-[#C9A84C] text-[#1a1a1a]",
      color: "from-[#C9A84C] to-[#8B7333]",
      highlight: true
    },
    {
      year: "Année 5-6",
      title: "L'expertise MDPH et invalidité",
      description: "Maîtrise des procédures MDPH, des demandes d'AAH, des contestations de taux d'IPP. Compréhension approfondie des barèmes, des voies de recours et des stratégies gagnantes.",
      icon: BookOpen,
      badge: "MDPH / AAH / IPP",
      color: "from-emerald-600 to-emerald-800"
    },
    {
      year: "Année 7+",
      title: "Naissance de Stratégie & Expertise Santé",
      description: "Décision de transformer ces années de combat en un service d'accompagnement unique en France. Création d'outils innovants (StratégiIA, Dossier Express IA, OCR intelligent) pour que personne ne vive ces épreuves seul.",
      icon: Star,
      badge: "Création",
      badgeColor: "bg-[#C9A84C] text-[#1a1a1a]",
      color: "from-[#C9A84C] to-[#8B7333]",
      highlight: true
    }
  ];

  const credentials = [
    {
      icon: Calendar,
      title: "4+ années d'expérience",
      description: "De vécu personnel dans les procédures AT/MP et assurantielles"
    },
    {
      icon: FileText,
      title: "Plusieurs dossiers accompagnés",
      description: "Étudiés, analysés et préparés avec méthode"
    },
    {
      icon: Scale,
      title: "Connaissance du système",
      description: "CPAM, MDPH, CRRMP, expertises, assurances"
    },
    {
      icon: Heart,
      title: "Approche humaine",
      description: "Une écoute bienveillante, sans jugement"
    }
  ];

  return (
    <main className="page-transition pt-20">
      <SEO title="Mon parcours" description="Découvrez le parcours et l'expertise de Stratégie & Expertise Santé en accompagnement des victimes de maladies professionnelles." path="/a-propos" />
      {/* Hero Section */}
      <section className="relative section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="text-sm font-medium text-accent uppercase tracking-wider">À propos</span>
              <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="about-title">
                Mon parcours, votre force
              </h1>
              <p className="text-lg text-muted-foreground mb-6">
                Je ne suis ni médecin, ni avocat, ni expert. Je suis quelqu'un qui a vécu de l'intérieur 
                ce que vous traversez peut-être aujourd'hui : la maladie professionnelle, les expertises 
                médicales interminables, et les combats contre les assurances.
              </p>
              <p className="text-muted-foreground">
                Pendant plus de sept ans, j'ai dû apprendre à naviguer dans un système complexe, 
                souvent opaque, parfois injuste. J'ai fait des erreurs, j'ai perdu du temps, 
                mais j'ai aussi compris comment il fonctionne.
              </p>
            </div>
            <div className="relative">
              <div className="aspect-square rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/18465014/pexels-photo-18465014.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Parcours personnel"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Timeline Section — Noir et Or */}
      <section className="section-padding bg-[#0c0c0c]" data-testid="timeline-section">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-14">
            <span className="text-[#C9A84C] text-sm font-medium uppercase tracking-[0.2em]">Chronologie</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-3 text-[#f5f0e8]">
              7 ans de combat, une mission
            </h2>
            <p className="text-[#f5f0e8]/50 mt-3 max-w-xl mx-auto text-sm">
              Chaque épreuve est devenue une expertise. Chaque obstacle, une compétence au service de mes clients.
            </p>
          </div>

          <div className="relative">
            {/* Timeline gold line */}
            <div className="absolute left-5 md:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-[#C9A84C]/60 via-[#C9A84C]/30 to-transparent transform md:-translate-x-px" />

            {timeline.map((item, index) => (
              <div 
                key={index}
                className={`relative flex flex-col md:flex-row gap-6 md:gap-10 mb-14 last:mb-0 ${
                  index % 2 === 0 ? 'md:flex-row-reverse' : ''
                }`}
                data-testid={`timeline-item-${index}`}
              >
                {/* Content card */}
                <div className={`flex-1 ${index % 2 === 0 ? 'md:text-right md:pr-14' : 'md:pl-14'} pl-14 md:pl-0`}>
                  <div className={`p-5 rounded-xl border ${item.highlight ? 'border-[#C9A84C]/40 bg-[#C9A84C]/5' : 'border-white/5 bg-white/[0.02]'} transition-all hover:border-[#C9A84C]/30`}>
                    <div className={`flex items-center gap-2 mb-3 ${index % 2 === 0 ? 'md:justify-end' : ''}`}>
                      <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${item.badgeColor || 'bg-white/10 text-[#f5f0e8]/70'}`}>
                        {item.badge}
                      </span>
                      <span className="text-[#C9A84C] text-xs font-semibold tracking-wider">{item.year}</span>
                    </div>
                    <h3 className="text-lg font-semibold text-[#f5f0e8] mb-2">{item.title}</h3>
                    <p className="text-sm text-[#f5f0e8]/60 leading-relaxed">{item.description}</p>
                  </div>
                </div>
                
                {/* Icon dot */}
                <div className={`absolute left-5 md:left-1/2 top-5 w-10 h-10 rounded-full border-2 flex items-center justify-center transform -translate-x-1/2 ${
                  item.highlight 
                    ? 'border-[#C9A84C] bg-[#C9A84C]/20' 
                    : 'border-[#C9A84C]/40 bg-[#0c0c0c]'
                }`}>
                  <item.icon className={`w-4 h-4 ${item.highlight ? 'text-[#C9A84C]' : 'text-[#C9A84C]/60'}`} />
                </div>
                
                {/* Spacer */}
                <div className="hidden md:block flex-1" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Citation du fondateur — Crédibilité */}
      <section className="section-padding bg-[#0c0c0c]" data-testid="founder-quote-section">
        <div className="max-w-4xl mx-auto">
          <div className="relative p-8 sm:p-12 rounded-2xl border border-[#D4AF37]/30 bg-gradient-to-br from-[#0c0c0c] to-[#1a1510]">
            {/* Decorative gold quote marks */}
            <div className="absolute top-4 left-6 text-[#D4AF37]/20 text-7xl sm:text-8xl font-serif leading-none select-none" aria-hidden="true">"</div>
            <div className="absolute bottom-4 right-6 text-[#D4AF37]/20 text-7xl sm:text-8xl font-serif leading-none select-none" aria-hidden="true">"</div>
            {/* Gold top accent line */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-1 rounded-full bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent" />
            <blockquote className="relative z-10" data-testid="founder-blockquote">
              <p className="text-lg sm:text-xl text-[#f5f0e8] leading-relaxed italic text-center" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
                Fort de mon expérience personnelle et de mes succès obtenus face à de grands groupes d'assurance nationaux dans la reconnaissance de garanties PTIA et ITT, j'ai développé Stratégie & Expertise Santé pour accompagner toutes les personnes confrontées à ces démarches complexes.
              </p>
              <footer className="mt-6 flex items-center justify-center gap-3">
                <div className="w-8 h-px bg-[#D4AF37]/50" />
                <cite className="text-sm font-medium text-[#D4AF37] not-italic tracking-wide uppercase">Fondateur, Stratégie & Expertise Santé</cite>
                <div className="w-8 h-px bg-[#D4AF37]/50" />
              </footer>
            </blockquote>
          </div>
        </div>
      </section>

      {/* Bloc Positionnement Premium — Manifeste Cabinet */}
      <section className="py-24 sm:py-32 bg-[#0c0c0c]" data-testid="positioning-manifesto">
        <div className="max-w-3xl mx-auto px-6 sm:px-8">
          <div className="relative pl-8 sm:pl-12 border-l-2 border-[#C9A84C]/40">
            {/* Accent dot at top of vertical line */}
            <div className="absolute -left-[5px] top-0 w-2 h-2 rounded-full bg-[#C9A84C]" />

            <h2
              className="text-2xl sm:text-3xl lg:text-4xl font-semibold text-[#f5f0e8] leading-tight tracking-tight"
              data-testid="positioning-title"
            >
              Nous n'intervenons pas après l'échec.
            </h2>

            <p
              className="mt-5 text-base sm:text-lg text-[#C9A84C]/70 leading-relaxed"
              data-testid="positioning-subtitle"
              style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
            >
              Nous intervenons avant qu'un dossier ne se fragilise, ne se perde ou ne s'effondre.
            </p>

            {/* Thin gold separator */}
            <div className="mt-8 mb-8 w-16 h-px bg-[#C9A84C]/25" />

            <p
              className="text-sm sm:text-base text-[#f5f0e8]/50 leading-relaxed max-w-2xl"
              data-testid="positioning-body"
            >
              Stratégie &amp; Expertise Santé intervient en amont pour analyser, structurer et renforcer un dossier avant qu'il ne soit affaibli par une mauvaise orientation, une lecture incomplète ou une perte de temps décisive.
            </p>

            {/* Accent dot at bottom of vertical line */}
            <div className="absolute -left-[5px] bottom-0 w-2 h-2 rounded-full bg-[#C9A84C]/30" />
          </div>
        </div>
      </section>

      {/* Why Me Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Pourquoi moi ?</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">
              L'expérience au service de l'accompagnement
            </h2>
            <p className="text-muted-foreground">
              Ce que j'ai appris à mes dépens, je le partage aujourd'hui pour vous épargner 
              les erreurs, le stress et l'isolement que j'ai connus.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {credentials.map((item, index) => (
              <div 
                key={index} 
                className="bg-background p-6 rounded-xl border border-border"
                data-testid={`credential-${index}`}
              >
                <item.icon className="w-10 h-10 text-accent mb-4" strokeWidth={1.5} />
                <h3 className="font-semibold mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Typologie des accompagnements — Ancrage factuel */}
      <section className="py-14 bg-[#0c0c0c]" data-testid="about-typologie">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <span className="text-[#C9A84C] text-sm font-medium uppercase tracking-[0.2em]">Domaines d'intervention</span>
            <h2 className="text-2xl sm:text-3xl font-semibold mt-3 text-[#f5f0e8]">Les dossiers que j'accompagne</h2>
            <p className="text-[#f5f0e8]/40 text-sm mt-3 max-w-xl mx-auto">
              Typologie réelle des situations que je traite — confidentialité stricte des personnes accompagnées.
            </p>
          </div>
          <div className="grid sm:grid-cols-3 gap-5">
            {[
              { type: "AT / MP", text: "Accidents du travail, maladies professionnelles en contentieux, consolidations, taux d'IPP acquis.", gold: false },
              { type: "MDPH", text: "Dossiers complexes : transplantation d'organe, polyhandicap sensoriel, restrictions poste, PCH, RQTH.", gold: true },
              { type: "PTIA / ITT", text: "Litiges assurantiels, reconnaissance de garanties acquises face aux grands assureurs nationaux.", gold: false },
            ].map((t, i) => (
              <div key={i} className={`p-5 rounded-xl border ${t.gold ? 'border-[#C9A84C]/30 bg-[#C9A84C]/5' : 'border-white/5 bg-white/[0.02]'}`} data-testid={`about-typologie-${i}`}>
                <div className="flex items-center gap-2 mb-3">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${t.gold ? 'bg-[#C9A84C] text-[#1a1a1a]' : 'bg-white/10 text-[#f5f0e8]/60'}`}>{t.type}</span>
                </div>
                <p className="text-[#f5f0e8]/60 text-sm leading-relaxed">{t.text}</p>
              </div>
            ))}
          </div>
          <p className="text-center text-[#f5f0e8]/20 text-[10px] mt-6">Aucune donnée personnelle identifiable n'est publiée — conformité RGPD.</p>
        </div>
      </section>

      {/* Document Juridique Section - PDF Viewer */}
      <section className="section-padding bg-secondary" data-testid="pdf-viewer-section" ref={pdfSectionRef}>
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Document officiel</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">
              Décision du Tribunal de Chartres
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Ce document témoigne de mon parcours juridique et de la reconnaissance obtenue 
              après des années de combat.
            </p>
          </div>

          <Card className="border-border overflow-hidden">
            <CardContent className="p-0">
              {/* PDF Embedded Viewer — lazy-loaded to prevent focus steal on page load */}
              <div className="w-full bg-muted/30" data-testid="pdf-embed-container">
                {pdfVisible ? (
                  <object
                    data="/decision-tribunal-chartres.pdf"
                    type="application/pdf"
                    className="w-full"
                    style={{ height: '700px' }}
                    tabIndex={-1}
                    data-testid="pdf-object"
                  >
                    <div className="p-12 text-center">
                      <FileText className="w-16 h-16 text-accent mx-auto mb-4" strokeWidth={1} />
                      <h3 className="font-semibold text-lg mb-2">Décision du Tribunal Judiciaire de Chartres</h3>
                      <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
                        Votre navigateur ne prend pas en charge l'affichage PDF intégré. 
                        Vous pouvez télécharger le document ci-dessous.
                      </p>
                      <a 
                        href="/decision-tribunal-chartres.pdf" 
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        <Button className="rounded-lg gap-2">
                          <Download className="w-4 h-4" />
                          Ouvrir le PDF
                        </Button>
                      </a>
                    </div>
                  </object>
                ) : (
                  <div className="flex items-center justify-center" style={{ height: '700px' }}>
                    <FileText className="w-12 h-12 text-muted-foreground/30" strokeWidth={1} />
                  </div>
                )}
              </div>
              {/* Download bar */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 bg-card border-t border-border">
                <div className="flex items-center gap-3 min-w-0">
                  <FileText className="w-5 h-5 text-accent flex-shrink-0" strokeWidth={1.5} />
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">Tribunal Judiciaire de Chartres — N°23/00331</p>
                    <p className="text-xs text-muted-foreground">Décision du 17/10/2025 — PDF, 50 Ko</p>
                  </div>
                </div>
                <a 
                  href="/decision-tribunal-chartres.pdf" 
                  download="Decision-Tribunal-Chartres-2300331.pdf"
                  data-testid="pdf-download-button"
                >
                  <Button variant="outline" className="rounded-lg gap-2">
                    <Download className="w-4 h-4" />
                    Télécharger
                  </Button>
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Engagement Section */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto text-center">
          <Award className="w-12 h-12 text-accent mx-auto mb-6" strokeWidth={1.5} />
          <blockquote className="text-2xl sm:text-3xl font-serif italic text-foreground mb-6">
            "Je ne promets pas de tout résoudre. Je promets de vous écouter, de vous expliquer, 
            et de vous accompagner dans ce parcours difficile. Ensemble, nous sommes plus forts."
          </blockquote>
          <p className="text-muted-foreground">— Fondateur de Stratégie & Expertise Santé</p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
            Prêt à être accompagné ?
          </h2>
          <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
            Contactez-moi pour discuter de votre situation. La première consultation téléphonique est gratuite — 10 minutes pour évaluer votre situation.
          </p>
          <Link to="/contact">
            <Button 
              size="lg" 
              className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="about-cta-button"
            >
              Prendre contact
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </main>
  );
};
