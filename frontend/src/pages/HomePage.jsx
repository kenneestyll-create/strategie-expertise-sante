import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { useReveal, useRevealChildren } from '@/hooks/useReveal';
import { 
  ArrowRight, Shield, CheckCircle, Sparkles, Stethoscope, Scale, Eye, Zap,
  Clock, HardHat, Activity, Accessibility, ClipboardList, ExternalLink,
  AlertTriangle, Phone, Crosshair, ScanSearch, ShieldAlert, CircleSlash,
  Compass, Focus, RefreshCcw, HeartHandshake, Award, TrendingUp, Brain,
  FileText, Lock, Users, BookOpen, Calculator, Search, CalendarDays
} from 'lucide-react';
import { MascotteMobileWidget } from '@/components/MascotteStrate';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/* ────────────────────────────────────────────
   Animated counter
──────────────────────────────────────────── */
const CountUpNumber = ({ value, unit = '', duration = 1200, started }) => {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    if (!started) return;
    let start = null, raf;
    const step = (ts) => {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      setDisplay(Math.floor((1 - Math.pow(1 - progress, 3)) * value));
      if (progress < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [started, value, duration]);
  return <>{display.toLocaleString('fr-FR')}{unit}</>;
};

/* ────────────────────────────────────────────
   Floating card for hero section
──────────────────────────────────────────── */
const FloatingCard = ({ icon: Icon, title, desc, delay, className = '' }) => (
  <div
    className={`absolute bg-[#111]/90 backdrop-blur-md border border-[#C9A84C]/20 rounded-xl px-4 py-3 shadow-2xl ${className}`}
    style={{ animation: `floatCard 4s ease-in-out ${delay}s infinite alternate` }}
  >
    <div className="flex items-center gap-3">
      <div className="w-9 h-9 rounded-lg bg-[#C9A84C]/15 flex items-center justify-center flex-shrink-0">
        <Icon className="w-4 h-4 text-[#C9A84C]" />
      </div>
      <div>
        <p className="text-white text-xs font-semibold leading-tight">{title}</p>
        <p className="text-white/40 text-[10px] leading-tight mt-0.5">{desc}</p>
      </div>
    </div>
  </div>
);

export const HomePage = () => {
  const [visitorCount, setVisitorCount] = useState(0);
  const [dossierCount, setDossierCount] = useState(0);
  const [countStarted, setCountStarted] = useState(false);
  const countSectionRef = useRef(null);

  const chiffresRef = useRevealChildren();
  const risquesRef = useRevealChildren();
  const methodeRef = useRevealChildren();
  const solutionsRef = useRevealChildren();
  const confianceRef = useRevealChildren();
  const ctaRef = useReveal();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [visitRes, dossierRes] = await Promise.allSettled([
          axios.post(`${API}/visitors/increment`),
          axios.get(`${API}/dossier-express/weekly-count`)
        ]);
        if (visitRes.status === 'fulfilled') setVisitorCount(visitRes.value.data.count);
        if (dossierRes.status === 'fulfilled') setDossierCount(dossierRes.value.data.count);
      } catch {
        try { const res = await axios.get(`${API}/visitors/count`); setVisitorCount(res.data.count); } catch {}
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    const el = countSectionRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setCountStarted(true); observer.disconnect(); } },
      { threshold: 0.3 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  /* ── Data arrays (unchanged business logic) ── */
  const risques = [
    { icon: CircleSlash, text: "Sous-evaluation de votre taux d'IPP" },
    { icon: ShieldAlert, text: "Mauvaise reconnaissance de l'incidence professionnelle" },
    { icon: ScanSearch, text: "Expertise medicale defavorable" },
    { icon: AlertTriangle, text: "Perte financiere importante et irreversible" },
  ];

  const methodeSES = [
    { num: "01", icon: Crosshair, title: "Analyse strategique", desc: "Etude approfondie de votre situation medicale, administrative et financiere." },
    { num: "02", icon: ShieldAlert, title: "Identification des risques", desc: "Reperage des failles, incoherences et points de vigilance." },
    { num: "03", icon: Compass, title: "Orientation experte", desc: "Mise en relation avec les experts les plus adaptes a votre pathologie." },
    { num: "04", icon: Focus, title: "Optimisation de l'expertise", desc: "Preparation strategique pour maximiser la reconnaissance." },
    { num: "05", icon: RefreshCcw, title: "Suivi et ajustement", desc: "Accompagnement continu et adaptation de la strategie." },
  ];

  const chiffresCles = [
    { icon: HardHat, value: 700000, unit: '', prefix: "Plus de", suffix: "accidents du travail par an en France", source: "CNAM", lien: "https://assurance-maladie.ameli.fr" },
    { icon: Activity, value: 50000, unit: '', prefix: "Environ", suffix: "maladies professionnelles reconnues chaque annee", source: "CNAM", lien: "https://assurance-maladie.ameli.fr" },
    { icon: Accessibility, value: 12, unit: ' millions', prefix: "Pres de", suffix: "de personnes en situation de handicap", source: "INSEE", lien: "https://www.insee.fr" },
    { icon: ClipboardList, value: 300000, unit: '', prefix: "Plus de", suffix: "nouvelles demandes MDPH chaque annee", source: "CNSA", lien: "https://www.cnsa.fr" },
  ];

  const confiance = [
    { icon: HeartHandshake, title: "Expertise terrain reelle", desc: "Nee d'une experience personnelle face aux memes epreuves que les votres." },
    { icon: Stethoscope, title: "Maitrise des enjeux medicaux", desc: "Tableaux de maladies professionnelles, baremes et procedures." },
    { icon: Award, title: "Approche strategique unique", desc: "Chaque dossier est traite comme un cas a part, avec une strategie sur mesure." },
    { icon: TrendingUp, title: "Vision orientee resultats", desc: "Obtenir la reconnaissance et l'indemnisation que vous meritez." },
  ];

  const temoignages = [
    { initials: "M.L.", age: "52 ans", badge: "AT", text: "Apres 18 mois de refus par la CPAM, mon accident du travail a enfin ete reconnu. Sans cet accompagnement, j'aurais abandonne les demarches.", result: "AT reconnue — Rente obtenue" },
    { initials: "P.D.", age: "45 ans", badge: "PTIA", badgeGold: true, text: "Mon assureur refusait de reconnaitre ma PTIA malgre l'avis de trois medecins. Grace a une strategie methodique, la garantie a ete activee apres 8 mois de recours.", result: "Garantie PTIA activee" },
    { initials: "S.B.", age: "38 ans", badge: "MP", text: "Ma maladie professionnelle n'etait pas dans les tableaux. L'accompagnement m'a permis de constituer un dossier solide — reconnaissance obtenue au premier passage.", result: "MP hors tableau reconnue" },
    { initials: "C.R.", age: "61 ans", badge: "IPP", text: "Mon taux d'IPP avait ete evalue a 5% alors que mes sequelles sont bien plus importantes. Apres contestation, le taux a ete reevalue a 23%.", result: "IPP reevaluee : 5% → 23%" },
    { initials: "A.M.", age: "34 ans", badge: "MDPH", text: "Mes demandes MDPH etaient systematiquement refusees. Grace a un dossier structure et des arguments adaptes, j'ai obtenu l'AAH en moins de 4 mois.", result: "AAH obtenue en 4 mois" },
    { initials: "J.T.", age: "48 ans", badge: "ITT", badgeGold: true, text: "Mon assurance refusait les indemnites ITT en invoquant une clause floue. L'analyse du contrat a permis de debloquer 14 mois d'arrieres.", result: "ITT versee — Arrieres recuperes" },
  ];

  const ecosysteme = [
    { icon: Brain, title: "StrategiIA", desc: "Analyse intelligente de votre situation", href: "/simulateur" },
    { icon: Zap, title: "Dossier Express IA", desc: "Rapport d'analyse complet sous 2h", href: "/dossier-express" },
    { icon: Users, title: "Accompagnement humain", desc: "Suivi personnalise par un expert", href: "/contact" },
    { icon: Stethoscope, title: "Medecin conseil", desc: "Orientation vers le bon specialiste", href: "/medecin-conseil" },
    { icon: Calculator, title: "Calculatrices IPP & AAH", desc: "Estimez vos droits en quelques clics", href: "/calculatrice-ipp" },
    { icon: BookOpen, title: "Ressources & guides", desc: "Documentation experte gratuite", href: "/ressources" },
    { icon: ScanSearch, title: "Scanner de documents", desc: "Numerisez vos pieces facilement", href: "/dossier-express" },
    { icon: CalendarDays, title: "Rendez-vous", desc: "Planifiez votre consultation", href: "/agenda" },
  ];

  return (
    <main className="page-transition">
      <SEO
        title="Accueil"
        description="Strategie & Expertise Sante : accompagnement expert en maladie professionnelle, accident du travail, MDPH et protection juridique."
        path="/"
      />

      {/* ══════════════════════════════════════════════════════════
          1. HERO — Two-column premium layout
      ══════════════════════════════════════════════════════════ */}
      <section className="relative overflow-hidden bg-[#0a0a08] pt-24 sm:pt-28 lg:pt-32 pb-16 sm:pb-20 lg:pb-28" data-testid="hero-section">
        {/* Subtle grain texture */}
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23D4AF37\' fill-opacity=\'1\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")' }} />
        {/* Gold gradient glow */}
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-[#C9A84C]/[0.04] rounded-full blur-[150px] translate-x-1/3 -translate-y-1/4" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            {/* ── LEFT COLUMN: Message ── */}
            <div className="text-left order-2 lg:order-1">
              {/* Badge */}
              <div className="inline-flex items-center gap-2.5 bg-[#C9A84C]/10 border border-[#C9A84C]/25 text-[#C9A84C] px-4 py-2 rounded-full mb-8" data-testid="pioneer-badge">
                <Shield className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="text-[10px] sm:text-xs font-bold uppercase tracking-[0.18em]">Pionnier en France</span>
              </div>

              {/* Main title */}
              <h1
                className="text-3xl sm:text-4xl lg:text-5xl xl:text-[3.4rem] font-semibold text-[#f5f0e8] leading-[1.15] mb-6"
                style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
                data-testid="hero-title"
              >
                Vous n'etes plus{' '}<span className="text-[#C9A84C]">seul</span>{' '}face a vos droits, votre dossier ou vos recours
              </h1>

              {/* Subtitle — metier */}
              <p className="text-sm sm:text-base text-[#f5f0e8]/50 leading-relaxed mb-6 max-w-xl" data-testid="hero-subtitle">
                Conseil et accompagnement strategique en droits MDPH, accident du travail, maladie professionnelle, invalidite et litiges assurantiels.
              </p>

              {/* Promise */}
              <p className="text-sm text-[#C9A84C]/70 leading-relaxed mb-8 max-w-lg italic" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
                Une lecture experte, humaine et strategique de votre situation pour identifier vos leviers d'action.
              </p>

              {/* 3 key points */}
              <div className="space-y-3 mb-10">
                {[
                  { icon: HeartHandshake, text: "Expertise nee d'un vecu concret" },
                  { icon: Crosshair, text: "Methode strategique & personnalisee" },
                  { icon: Brain, text: "Analyse IA + accompagnement humain" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-[#C9A84C]/10 flex items-center justify-center flex-shrink-0">
                      <item.icon className="w-4 h-4 text-[#C9A84C]" />
                    </div>
                    <span className="text-[#f5f0e8]/70 text-sm font-medium">{item.text}</span>
                  </div>
                ))}
              </div>

              {/* Social proof */}
              {visitorCount > 0 && (
                <div className="flex items-center gap-2.5 mb-8">
                  <div className="flex -space-x-2">
                    {[1,2,3,4].map(i => (
                      <div key={i} className="w-7 h-7 rounded-full bg-[#C9A84C]/20 border-2 border-[#0a0a08] flex items-center justify-center">
                        <Users className="w-3 h-3 text-[#C9A84C]/60" />
                      </div>
                    ))}
                  </div>
                  <span className="text-xs text-[#f5f0e8]/40">
                    <strong className="text-[#f5f0e8]/60">{visitorCount.toLocaleString('fr-FR')}+</strong> personnes nous ont fait confiance
                  </span>
                </div>
              )}

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 mb-6">
                <button
                  onClick={() => window.dispatchEvent(new Event('strategiia:open'))}
                  className="cursor-pointer"
                >
                  <Button
                    size="lg"
                    className="w-full sm:w-auto rounded-full px-8 py-6 gap-2.5 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-bold text-sm shadow-xl shadow-[#C9A84C]/20 transition-all hover:shadow-[#C9A84C]/35 hover:scale-[1.02]"
                    data-testid="hero-cta-primary"
                  >
                    <Search className="w-4 h-4 flex-shrink-0" />
                    Evaluer ma situation
                  </Button>
                </button>
                <Link to="/contact">
                  <Button
                    variant="outline"
                    size="lg"
                    className="w-full sm:w-auto rounded-full px-8 py-6 gap-2.5 border-[#f5f0e8]/15 text-[#f5f0e8]/80 hover:bg-[#f5f0e8]/5 hover:border-[#f5f0e8]/25 text-sm transition-all"
                    data-testid="hero-cta-secondary"
                  >
                    <Phone className="w-4 h-4 flex-shrink-0" />
                    Etre accompagne
                  </Button>
                </Link>
              </div>

              {/* Reassurances under CTAs */}
              <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-[10px] sm:text-xs text-[#f5f0e8]/30">
                <span className="flex items-center gap-1.5"><Clock className="w-3 h-3 text-[#C9A84C]/50" /> Reponse sous 2h</span>
                <span className="flex items-center gap-1.5"><Lock className="w-3 h-3 text-[#C9A84C]/50" /> 100% confidentiel</span>
                <span className="flex items-center gap-1.5"><Shield className="w-3 h-3 text-[#C9A84C]/50" /> Expertise reelle</span>
              </div>
            </div>

            {/* ── RIGHT COLUMN: Visual ── */}
            <div className="relative order-1 lg:order-2 flex justify-center lg:justify-end">
              <div className="relative w-full max-w-md lg:max-w-lg">
                {/* Shield background element */}
                <div className="absolute inset-0 flex items-center justify-center opacity-10">
                  <Shield className="w-[300px] h-[300px] text-[#C9A84C]" strokeWidth={0.5} />
                </div>

                {/* Hero image */}
                <div className="relative z-10 rounded-2xl overflow-hidden shadow-2xl shadow-black/40 border border-[#C9A84C]/10">
                  <img
                    src="https://images.pexels.com/photos/28446973/pexels-photo-28446973.jpeg?auto=compress&cs=tinysrgb&w=800"
                    alt="Expert en strategie sante"
                    className="w-full h-[350px] sm:h-[420px] lg:h-[480px] object-cover object-top"
                    loading="eager"
                  />
                  {/* Gradient overlay bottom */}
                  <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a08] via-transparent to-transparent opacity-60" />
                </div>

                {/* Floating cards */}
                <FloatingCard
                  icon={Brain}
                  title="Analyse IA"
                  desc="Lecture intelligente de votre situation"
                  delay={0}
                  className="hidden sm:flex -left-8 top-16 z-20"
                />
                <FloatingCard
                  icon={FileText}
                  title="Documents"
                  desc="Etude approfondie de vos pieces"
                  delay={1.5}
                  className="hidden sm:flex -right-6 top-1/3 z-20"
                />
                <FloatingCard
                  icon={Compass}
                  title="Orientation"
                  desc="Strategie adaptee a votre dossier"
                  delay={3}
                  className="hidden sm:flex -left-4 bottom-24 z-20"
                />

                {/* Gold particles effect */}
                <div className="absolute -top-4 -right-4 w-2 h-2 rounded-full bg-[#C9A84C]/40 animate-pulse" />
                <div className="absolute top-1/4 -right-8 w-1.5 h-1.5 rounded-full bg-[#C9A84C]/30 animate-pulse" style={{ animationDelay: '1s' }} />
                <div className="absolute bottom-1/3 -left-6 w-1 h-1 rounded-full bg-[#C9A84C]/25 animate-pulse" style={{ animationDelay: '2s' }} />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Dossier Express urgence strip ── */}
      <section className="relative overflow-hidden" data-testid="dossier-express-banner">
        <div className="absolute inset-0 bg-gradient-to-r from-red-800 via-red-700 to-red-800" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 sm:py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <Zap className="w-5 h-5 text-yellow-300 flex-shrink-0" />
              <div className="text-white text-sm">
                <span className="font-bold">Expertise imminente ?</span>
                <span className="text-red-200 ml-2">Rapport complet en 2h —</span>
                <span className="text-yellow-300 font-bold ml-1">97 EUR</span>
                {dossierCount > 0 && (
                  <span className="text-red-200 ml-2 text-xs" data-testid="dossier-express-counter">
                    (<strong className="text-yellow-300">{dossierCount}</strong> dossiers cette semaine)
                  </span>
                )}
              </div>
            </div>
            <Link to="/dossier-express" className="flex-shrink-0">
              <Button
                size="sm"
                className="bg-white text-red-700 hover:bg-yellow-50 font-bold rounded-full px-5 gap-1.5 shadow-lg text-xs"
                data-testid="dossier-express-banner-cta"
              >
                Dossier Express IA <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ── Conseil du jour — Mobile ── */}
      <div className="md:hidden px-4 py-4 bg-[#111]">
        <MascotteMobileWidget />
      </div>

      {/* ══════════════════════════════════════════════════════════
          2. POURQUOI CE SITE EXISTE
      ══════════════════════════════════════════════════════════ */}
      <section className="relative py-16 sm:py-20 lg:py-28 overflow-hidden bg-[#0c0c0c]" data-testid="home-founder-quote">
        <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23D4AF37\' fill-opacity=\'1\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")' }} />

        <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-5 gap-10 lg:gap-16 items-center">
            {/* Left: Visual */}
            <div className="lg:col-span-2 flex justify-center">
              <div className="relative">
                <div className="w-48 h-48 sm:w-56 sm:h-56 rounded-full bg-[#C9A84C]/[0.06] border border-[#C9A84C]/15 flex items-center justify-center">
                  <Scale className="w-20 h-20 text-[#C9A84C]/30" strokeWidth={1} />
                </div>
                <div className="absolute -bottom-2 -right-2 w-12 h-12 rounded-full bg-[#C9A84C] flex items-center justify-center shadow-lg shadow-[#C9A84C]/20">
                  <Shield className="w-6 h-6 text-[#0a0a08]" />
                </div>
              </div>
            </div>

            {/* Right: Text */}
            <div className="lg:col-span-3">
              <span className="text-[#C9A84C] text-xs font-medium uppercase tracking-[0.2em] mb-4 block">Pourquoi ce site existe</span>
              <h2
                className="text-xl sm:text-2xl lg:text-3xl font-semibold text-[#f5f0e8] leading-snug mb-6"
                style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
              >
                Ce service n'est pas ne d'une theorie.<br />
                <span className="text-[#C9A84C]">Il est ne d'un combat reel.</span>
              </h2>

              <div className="relative pl-6 border-l-2 border-[#C9A84C]/20 space-y-4">
                <p className="text-[#f5f0e8]/60 text-sm leading-relaxed">
                  Fort de mon experience personnelle et de mes succes obtenus face a de grands groupes d'assurance nationaux dans la reconnaissance de garanties PTIA et ITT, j'ai developpe Strategie & Expertise Sante pour accompagner toutes les personnes confrontees a ces demarches complexes.
                </p>
                <p className="text-[#f5f0e8]/60 text-sm leading-relaxed">
                  Chaque dossier que nous traitons porte la marque de cette experience vecue. Nous ne sommes pas des theoriciens : nous sommes passes par la, et nous savons exactement ce dont vous avez besoin pour avancer.
                </p>
              </div>

              <footer className="mt-6 flex items-center gap-3">
                <div className="w-8 h-px bg-[#C9A84C]/30" />
                <cite className="text-xs font-medium text-[#C9A84C]/60 not-italic tracking-widest uppercase" data-testid="home-founder-blockquote">Fondateur — S.E.S</cite>
              </footer>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          3. NOS DEUX INTELLIGENCES DE DOSSIER
      ══════════════════════════════════════════════════════════ */}
      <section className="py-16 sm:py-20 lg:py-28 bg-[#111]" data-testid="solutions-section" ref={solutionsRef}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Deux intelligences complementaires</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 mb-4 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Quel service correspond a votre besoin ?
            </h2>
            <p className="text-sm text-[#f5f0e8]/40">
              Deux parcours distincts, une meme exigence de qualite.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 lg:gap-8 stagger">
            {/* Card 1 — StrategiIA */}
            <div className="reveal" data-testid="solution-card-0">
              <Link to="/simulateur" className="group block h-full">
                <div className="h-full bg-[#0a0a08] border border-[#C9A84C]/20 rounded-2xl p-8 sm:p-10 transition-all duration-300 hover:border-[#C9A84C]/40 hover:shadow-xl hover:shadow-[#C9A84C]/5 group-hover:-translate-y-1">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-14 h-14 rounded-xl bg-[#C9A84C]/10 flex items-center justify-center">
                      <Brain className="w-7 h-7 text-[#C9A84C]" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-[#f5f0e8]">StrategiIA</h3>
                      <p className="text-[#C9A84C] font-semibold text-sm">Pre-analyse gratuite</p>
                    </div>
                  </div>

                  <p className="text-[#f5f0e8]/50 text-sm leading-relaxed mb-6">
                    Votre premier eclairage strategique. Une analyse intelligente de votre situation pour comprendre vos droits et identifier vos leviers d'action.
                  </p>

                  <div className="space-y-2.5 mb-8">
                    <p className="text-[#f5f0e8]/30 text-xs font-semibold uppercase tracking-wider mb-3">Ideal pour</p>
                    {["Comprendre votre situation rapidement", "Identifier vos droits et recours", "Obtenir une premiere orientation strategique", "Preparer une demarche structuree"].map((t, i) => (
                      <div key={i} className="flex items-start gap-2.5">
                        <CheckCircle className="w-4 h-4 text-[#C9A84C] flex-shrink-0 mt-0.5" />
                        <span className="text-[#f5f0e8]/60 text-sm">{t}</span>
                      </div>
                    ))}
                  </div>

                  <span className="inline-flex items-center gap-2 text-[#C9A84C] text-sm font-medium group-hover:gap-3 transition-all">
                    Lancer mon analyse <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </Link>
            </div>

            {/* Card 2 — Dossier Express IA */}
            <div className="reveal" data-testid="solution-card-1">
              <Link to="/dossier-express" className="group block h-full">
                <div className="h-full bg-[#F8F5EF] border border-[#C9A84C]/25 rounded-2xl p-8 sm:p-10 transition-all duration-300 hover:border-[#C9A84C]/50 hover:shadow-xl hover:shadow-[#C9A84C]/10 group-hover:-translate-y-1 relative overflow-hidden">
                  {/* Urgent badge */}
                  <div className="absolute top-4 right-4">
                    <span className="bg-red-600 text-white text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full">Urgence</span>
                  </div>

                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-14 h-14 rounded-xl bg-[#C9A84C]/15 flex items-center justify-center">
                      <Zap className="w-7 h-7 text-[#C9A84C]" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-[#1a1a1a]">Dossier Express IA</h3>
                      <p className="text-[#C9A84C] font-semibold text-sm">97 EUR — Livre sous 2h</p>
                    </div>
                  </div>

                  <p className="text-[#1a1a1a]/60 text-sm leading-relaxed mb-6">
                    L'analyse documentaire complete de votre dossier. Un rapport structure, approfondi et exploitable pour vos demarches.
                  </p>

                  <div className="space-y-2.5 mb-8">
                    <p className="text-[#1a1a1a]/30 text-xs font-semibold uppercase tracking-wider mb-3">Ce que vous recevez</p>
                    {["Rapport d'analyse detaille et structure", "Etude de vos documents medicaux et juridiques", "Identification des points forts et faiblesses", "Strategie d'action concrete et personnalisee"].map((t, i) => (
                      <div key={i} className="flex items-start gap-2.5">
                        <CheckCircle className="w-4 h-4 text-[#C9A84C] flex-shrink-0 mt-0.5" />
                        <span className="text-[#1a1a1a]/70 text-sm">{t}</span>
                      </div>
                    ))}
                  </div>

                  <span className="inline-flex items-center gap-2 text-[#C9A84C] text-sm font-medium group-hover:gap-3 transition-all">
                    Deposer mon dossier <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </Link>
            </div>
          </div>

          {/* Accompagnement complet CTA */}
          <div className="mt-8 text-center reveal">
            <Link to="/contact" data-testid="solution-card-2">
              <Button variant="outline" className="rounded-full px-8 py-5 gap-2.5 border-[#C9A84C]/20 text-[#C9A84C] hover:bg-[#C9A84C]/5 hover:border-[#C9A84C]/40">
                <Shield className="w-4 h-4" />
                Accompagnement strategique complet — Sur devis
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          4. RISQUES — Warning section
      ══════════════════════════════════════════════════════════ */}
      <section className="py-14 sm:py-16 bg-[#0a0a08] border-y border-[#C9A84C]/5" data-testid="risques-section">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8" ref={risquesRef}>
          <div className="text-center mb-10 reveal">
            <AlertTriangle className="w-7 h-7 text-amber-500 mx-auto mb-3" />
            <h2 className="text-lg sm:text-xl md:text-2xl font-semibold text-[#f5f0e8] mb-2">
              Ce que vous risquez sans accompagnement
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 gap-4 mb-10 stagger">
            {risques.map((r, i) => (
              <div key={i} className="flex items-start gap-3.5 p-4 rounded-xl border border-amber-500/10 bg-amber-500/[0.03] reveal" data-testid={`risque-${i}`}>
                <div className="w-9 h-9 rounded-lg bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                  <r.icon className="w-4 h-4 text-amber-500" />
                </div>
                <p className="text-[#f5f0e8]/60 text-sm leading-relaxed font-medium pt-1">{r.text}</p>
              </div>
            ))}
          </div>

          <div className="text-center reveal">
            <p className="text-sm text-[#C9A84C]/60 italic mb-6 max-w-lg mx-auto" style={{ fontFamily: "'Playfair Display', Georgia, serif" }} data-testid="risques-accroche">
              Une mauvaise decision aujourd'hui peut vous couter des milliers d'euros demain.
            </p>
            <Link to="/contact">
              <Button className="rounded-full px-7 gap-2 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-bold text-sm" data-testid="risques-cta">
                <Phone className="w-4 h-4" /> Etre accompagne <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          5. ECOSYSTEME DE SERVICES
      ══════════════════════════════════════════════════════════ */}
      <section className="py-16 sm:py-20 lg:py-28 bg-[#111]" data-testid="methode-section" ref={methodeRef}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Ecosysteme complet</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 mb-4 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Bien plus qu'un outil IA
            </h2>
            <p className="text-sm text-[#f5f0e8]/40">
              Un ecosysteme complet d'accompagnement, de l'analyse initiale au suivi personnalise.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-5 stagger">
            {ecosysteme.map((s, i) => (
              <Link key={i} to={s.href} className="group reveal" data-testid={`methode-step-${i}`}>
                <div className="h-full bg-[#0a0a08] rounded-xl p-5 sm:p-6 border border-white/5 hover:border-[#C9A84C]/20 transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-lg">
                  <div className="w-10 h-10 rounded-lg bg-[#C9A84C]/10 flex items-center justify-center mb-4">
                    <s.icon className="w-5 h-5 text-[#C9A84C]" />
                  </div>
                  <h3 className="font-semibold text-sm text-[#f5f0e8] mb-1.5 leading-snug">{s.title}</h3>
                  <p className="text-xs text-[#f5f0e8]/35 leading-relaxed">{s.desc}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          6. METHODE S.E.S — Process steps
      ══════════════════════════════════════════════════════════ */}
      <section className="py-16 sm:py-20 bg-[#0a0a08] border-y border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Notre approche</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 mb-4 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              La Methode <span className="text-[#C9A84C]">S.E.S</span>
            </h2>
            <p className="text-sm text-[#f5f0e8]/40">
              Une methodologie structuree et eprouvee pour defendre efficacement vos interets.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4 sm:gap-5">
            {methodeSES.map((m, i) => (
              <div key={i} className="relative group">
                <div className="h-full bg-[#111] rounded-xl p-5 border border-white/5 hover:border-[#C9A84C]/15 transition-all duration-300 group-hover:-translate-y-0.5">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-2xl font-bold text-[#C9A84C]/10">{m.num}</span>
                    <div className="w-8 h-8 rounded-lg bg-[#C9A84C]/10 flex items-center justify-center">
                      <m.icon className="w-4 h-4 text-[#C9A84C]" />
                    </div>
                  </div>
                  <h3 className="font-semibold text-sm text-[#f5f0e8] mb-1.5">{m.title}</h3>
                  <p className="text-xs text-[#f5f0e8]/35 leading-relaxed">{m.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          7. MEDECIN CONSEIL
      ══════════════════════════════════════════════════════════ */}
      <section className="py-16 sm:py-20 bg-[#111] border-b border-white/5" data-testid="medecin-conseil-home-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">
            <div className="min-w-0">
              <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Orientation strategique</span>
              <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 mb-4 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }} data-testid="home-medecin-conseil-title">
                Le choix du medecin conseil : un enjeu financier majeur
              </h2>
              <p className="text-[#f5f0e8]/50 text-sm leading-relaxed mb-4">
                Un medecin conseil mal choisi peut entrainer une sous-evaluation de vos sequelles et une perte d'indemnisation de plusieurs dizaines de milliers d'euros.
              </p>
              <p className="text-[#f5f0e8]/50 text-sm leading-relaxed mb-6">
                Nous vous orientons vers le professionnel le plus adapte a votre pathologie et a votre strategie juridique.
              </p>
              <Link to="/medecin-conseil">
                <Button className="rounded-full px-6 py-5 gap-2 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-bold text-sm" data-testid="home-medecin-conseil-cta">
                  <Stethoscope className="w-4 h-4" /> Choisir mon medecin conseil <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
            <div className="grid grid-cols-2 gap-4 min-w-0">
              <div className="bg-[#0a0a08] border border-white/5 p-5 rounded-xl">
                <p className="text-2xl sm:text-3xl font-bold text-[#C9A84C] mb-1">800 - 3 000 EUR</p>
                <p className="text-xs text-[#f5f0e8]/35">Cout moyen d'un medecin conseil</p>
              </div>
              <div className="bg-[#0a0a08] border border-white/5 p-5 rounded-xl">
                <p className="text-2xl sm:text-3xl font-bold text-[#C9A84C] mb-1">x10</p>
                <p className="text-xs text-[#f5f0e8]/35">Retour sur investissement potentiel</p>
              </div>
              <div className="col-span-2 bg-[#0a0a08] border border-white/5 p-5 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0" />
                  <p className="font-semibold text-sm text-[#f5f0e8]">Risque d'un mauvais choix</p>
                </div>
                <p className="text-xs text-[#f5f0e8]/40 leading-relaxed">
                  Un taux d'IPP sous-evalue de quelques points peut representer une perte de plusieurs dizaines de milliers d'euros sur votre indemnisation finale.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          8. CONFIDENTIALITE / SERENITE
      ══════════════════════════════════════════════════════════ */}
      <section className="py-16 sm:py-20 bg-[#0a0a08]">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <Lock className="w-7 h-7 text-[#C9A84C] mx-auto mb-3" />
            <h2 className="text-xl sm:text-2xl font-semibold text-[#f5f0e8] mb-3" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Vos documents sont entre de bonnes mains
            </h2>
            <p className="text-sm text-[#f5f0e8]/40 max-w-2xl mx-auto">
              Nous comprenons la nature sensible de vos documents medicaux et administratifs. La confidentialite et la securite de vos donnees sont au coeur de nos engagements.
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-5">
            {[
              { icon: Shield, title: "Confidentialite totale", desc: "Vos dossiers ne sont jamais partages avec des tiers. Traitement strictement confidentiel." },
              { icon: Lock, title: "Securite des donnees", desc: "Vos documents sont traites de maniere securisee et supprimes apres analyse si vous le souhaitez." },
              { icon: Eye, title: "Transparence", desc: "Vous restez maitre de vos informations a chaque etape. Aucune utilisation commerciale de vos donnees." },
            ].map((item, i) => (
              <div key={i} className="bg-[#111] border border-white/5 rounded-xl p-6 text-center hover:border-[#C9A84C]/15 transition-all">
                <div className="w-11 h-11 rounded-xl bg-[#C9A84C]/10 flex items-center justify-center mx-auto mb-4">
                  <item.icon className="w-5 h-5 text-[#C9A84C]" />
                </div>
                <h3 className="font-semibold text-sm text-[#f5f0e8] mb-2">{item.title}</h3>
                <p className="text-xs text-[#f5f0e8]/35 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          9. CHIFFRES CLES
      ══════════════════════════════════════════════════════════ */}
      <section className="py-16 sm:py-20 bg-[#111]" data-testid="chiffres-section" id="chiffres">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" ref={chiffresRef}>
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Contexte national</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 mb-4 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Le defi en chiffres
            </h2>
            <p className="text-sm text-[#f5f0e8]/40">
              Des millions de personnes sont concernees chaque annee en France.
            </p>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 stagger" ref={countSectionRef}>
            {chiffresCles.map((item, index) => (
              <div key={index} className="reveal" data-testid={`chiffre-bloc-${index}`}>
                <div className="h-full bg-[#0a0a08] border border-white/5 rounded-xl p-5 sm:p-6 flex flex-col items-center text-center transition-all hover:border-[#C9A84C]/10">
                  <div className="w-10 h-10 rounded-lg bg-[#C9A84C]/10 flex items-center justify-center mb-4">
                    <item.icon className="w-5 h-5 text-[#C9A84C]" strokeWidth={1.5} />
                  </div>
                  <p className="text-[10px] uppercase tracking-wider text-[#f5f0e8]/30 mb-1">{item.prefix}</p>
                  <p className="text-2xl sm:text-3xl font-bold text-[#C9A84C] leading-tight mb-1.5" data-testid={`chiffre-value-${index}`}>
                    <CountUpNumber value={item.value} unit={item.unit} duration={1300} started={countStarted} />
                  </p>
                  <p className="text-xs text-[#f5f0e8]/40 leading-relaxed flex-1 mb-3">{item.suffix}</p>
                  <a href={item.lien} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-[10px] text-[#f5f0e8]/20 hover:text-[#C9A84C] transition-colors" data-testid={`chiffre-source-${index}`}>
                    Source : {item.source} <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          10. CONFIANCE
      ══════════════════════════════════════════════════════════ */}
      <section className="py-16 sm:py-20 bg-[#0a0a08]" data-testid="confiance-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" ref={confianceRef}>
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Credibilite</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 mb-4 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Pourquoi nous faire confiance ?
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 stagger">
            {confiance.map((c, i) => (
              <div key={i} className="reveal" data-testid={`confiance-${i}`}>
                <div className="h-full p-6 rounded-xl bg-[#111] border border-white/5 hover:border-[#C9A84C]/15 transition-all">
                  <div className="w-10 h-10 rounded-lg bg-[#C9A84C]/10 flex items-center justify-center mb-4">
                    <c.icon className="w-5 h-5 text-[#C9A84C]" />
                  </div>
                  <h3 className="font-semibold text-sm text-[#f5f0e8] mb-2">{c.title}</h3>
                  <p className="text-xs text-[#f5f0e8]/35 leading-relaxed">{c.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          11. TEMOIGNAGES
      ══════════════════════════════════════════════════════════ */}
      <section className="py-16 sm:py-20 bg-[#111]" data-testid="testimonials-section">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <span className="text-[#C9A84C] text-xs font-medium uppercase tracking-[0.2em]">Ils ont fait confiance</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Des parcours transformes
            </h2>
            <p className="text-[#f5f0e8]/30 mt-3 max-w-xl mx-auto text-sm">
              Temoignages anonymises de personnes accompagnees par Strategie & Expertise Sante.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
            {temoignages.map((t, i) => (
              <div
                key={i}
                className={`p-5 rounded-xl border ${t.badgeGold ? 'border-[#C9A84C]/20 bg-[#C9A84C]/[0.03]' : 'border-white/5 bg-white/[0.01]'} hover:border-[#C9A84C]/15 transition-all`}
                data-testid={`testimonial-${i}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-full bg-[#C9A84C]/10 border border-[#C9A84C]/15 flex items-center justify-center">
                      <span className="text-[#C9A84C] text-[10px] font-bold">{t.initials}</span>
                    </div>
                    <div>
                      <span className="text-[#f5f0e8] text-sm font-medium">{t.initials}</span>
                      <span className="text-[#f5f0e8]/25 text-xs ml-1.5">{t.age}</span>
                    </div>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${t.badgeGold ? 'bg-[#C9A84C] text-[#1a1a1a]' : 'bg-white/5 text-[#f5f0e8]/40'}`}>
                    {t.badge}
                  </span>
                </div>
                <p className="text-[#f5f0e8]/45 text-sm leading-relaxed mb-3">{t.text}</p>
                <div className="flex items-center gap-2 pt-2 border-t border-white/5">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
                  <span className="text-emerald-400 text-xs font-medium">{t.result}</span>
                </div>
              </div>
            ))}
          </div>
          <p className="text-center text-[#f5f0e8]/15 text-[10px] mt-6">
            * Prenoms et details modifies pour preserver l'anonymat. Resultats reels obtenus pour nos clients.
          </p>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          12. DISCLAIMER
      ══════════════════════════════════════════════════════════ */}
      <section className="py-6 bg-[#111] border-y border-amber-500/5">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-start gap-3" data-testid="homepage-disclaimer">
            <Scale className="w-4 h-4 text-amber-500/50 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
            <div className="text-xs text-[#f5f0e8]/25 leading-relaxed space-y-1.5">
              <p>
                <strong className="text-[#f5f0e8]/40">Information importante :</strong> Strategie & Expertise Sante propose un accompagnement strategique et une analyse documentaire.
                Ce service ne constitue pas une expertise medicale officielle ni une expertise judiciaire.
              </p>
              <p>
                Les services proposes ne constituent pas un conseil juridique ni un avis medical.
                Pour toute decision juridique ou medicale, consultez un professionnel qualifie.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          13. CTA FINAL — Emotional close
      ══════════════════════════════════════════════════════════ */}
      <section className="relative py-20 sm:py-28 overflow-hidden bg-[#0a0a08]">
        {/* Background effect */}
        <div className="absolute inset-0 flex items-center justify-center opacity-[0.03]">
          <Shield className="w-[500px] h-[500px] text-[#C9A84C]" strokeWidth={0.3} />
        </div>

        <div className="relative max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center reveal" ref={ctaRef}>
          <h2
            className="text-2xl sm:text-3xl lg:text-4xl font-semibold text-[#f5f0e8] mb-6 leading-snug"
            style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
          >
            Votre situation merite une strategie claire, humaine et rigoureuse.
          </h2>

          <p className="text-[#f5f0e8]/45 text-sm sm:text-base mb-10 max-w-2xl mx-auto leading-relaxed">
            Chaque situation est unique. Contactez-nous pour une premiere consultation gratuite de 10 minutes et sans engagement. Ensemble, nous verrons comment vous accompagner.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link to="/contact">
              <Button
                size="lg"
                className="rounded-full px-10 py-6 gap-2.5 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-bold text-sm shadow-xl shadow-[#C9A84C]/20"
                data-testid="cta-contact-button"
              >
                <Phone className="w-4 h-4" /> Me contacter <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <Link to="/simulateur">
              <Button
                variant="outline"
                size="lg"
                className="rounded-full px-10 py-6 gap-2.5 border-[#f5f0e8]/10 text-[#f5f0e8]/60 hover:bg-[#f5f0e8]/5"
                data-testid="cta-simulateur-button"
              >
                Auto-diagnostic gratuit
              </Button>
            </Link>
          </div>

          {/* Brand signature */}
          <div className="pt-8 border-t border-[#C9A84C]/10">
            <p
              className="text-[#f5f0e8]/60 text-base italic mb-2"
              style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
            >
              Vous n'etes plus seul face a votre combat.
            </p>
            <p className="text-[#C9A84C] text-lg font-bold tracking-wide">
              Dorenavant, S.E.S est votre bouclier.
            </p>
          </div>
        </div>
      </section>

      {/* Floating card animation */}
      <style>{`
        @keyframes floatCard {
          0% { transform: translateY(0px); }
          100% { transform: translateY(-8px); }
        }
      `}</style>
    </main>
  );
};
