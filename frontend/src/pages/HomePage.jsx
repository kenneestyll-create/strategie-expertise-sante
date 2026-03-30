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
          1. HERO — Structure propre, stable, 2 colonnes
      ══════════════════════════════════════════════════════════ */}
      <section className="relative bg-[#0a0a08]" data-testid="hero-section">
        {/* Fond premium — lueur dorée diffuse très discrète */}
        <div className="absolute top-1/2 right-0 w-[600px] h-[600px] -translate-y-1/2 translate-x-1/4 bg-[#C9A84C]/[0.03] rounded-full blur-[180px] pointer-events-none" />
        <div className="relative max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-12 lg:py-14">
          <div className="grid lg:grid-cols-[55fr_45fr] gap-8 lg:gap-12 items-center">

            {/* ── COLONNE GAUCHE : Contenu ── */}
            <div className="order-2 lg:order-1">
              {/* Badge — Sceau premium */}
              <div className="inline-flex items-center gap-4 bg-[#C9A84C]/[0.05] border border-[#C9A84C]/25 text-[#C9A84C] px-5 py-3 rounded-[10px] mb-4 shadow-[0_2px_12px_-4px_rgba(201,168,76,0.08)]" data-testid="pioneer-badge">
                <div className="w-9 h-9 rounded-lg border border-[#C9A84C]/30 bg-[#C9A84C]/[0.08] flex items-center justify-center flex-shrink-0">
                  <Scale className="w-[18px] h-[18px] text-[#C9A84C]" />
                </div>
                <div className="leading-normal min-w-0">
                  <span className="text-[11px] sm:text-xs font-extrabold uppercase tracking-[0.14em] block text-[#C9A84C]">Pionnier en France</span>
                  <span className="text-[10px] sm:text-[11px] text-[#C9A84C]/45 block mt-0.5">Plateforme d'analyse & d'accompagnement en droits sante</span>
                </div>
              </div>

              {/* Titre — compacté pour above-the-fold */}
              <h1
                className="text-[2rem] sm:text-[2.4rem] lg:text-[2.6rem] xl:text-[2.8rem] font-bold text-[#f5f0e8] leading-[1.10] mb-3"
                style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
                data-testid="hero-title"
              >
                Vous n'etes plus seul<br className="hidden sm:block" /> face a{' '}
                <span className="text-[#C9A84C]">votre dossier</span>,{' '}
                <span className="text-[#C9A84C]">vos droits</span><br className="hidden sm:block" /> ou{' '}
                <span className="text-[#C9A84C]">vos recours</span>.
              </h1>

              {/* Sous-titre */}
              <p className="text-sm sm:text-[15px] text-[#f5f0e8]/55 leading-relaxed mb-3 max-w-xl" data-testid="hero-subtitle">
                Analysez votre situation, identifiez vos leviers, comprenez vos droits et accedez a un accompagnement strategique humain en cas de{' '}
                <strong className="text-[#f5f0e8]/70">maladie professionnelle</strong>,{' '}
                <strong className="text-[#f5f0e8]/70">accident du travail</strong>,{' '}
                <strong className="text-[#f5f0e8]/70">MDPH</strong> ou{' '}
                <strong className="text-[#f5f0e8]/70">litige assuranciel</strong>.
              </p>

              {/* 3 points cles */}
              <div className="space-y-2 mb-4">
                {[
                  { icon: HeartHandshake, text: "Expertise nee d'un vecu concret" },
                  { icon: Crosshair, text: "Methode strategique & personnalisee" },
                  { icon: Brain, text: "Analyse IA + accompagnement humain" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-full border border-[#C9A84C]/30 bg-[#C9A84C]/5 flex items-center justify-center flex-shrink-0">
                      <item.icon className="w-3.5 h-3.5 text-[#C9A84C]" />
                    </div>
                    <span className="text-[#f5f0e8]/65 text-sm">{item.text}</span>
                  </div>
                ))}
              </div>

              {/* Preuve sociale */}
              <div className="flex flex-wrap items-center gap-4 sm:gap-5 mb-4">
                {visitorCount > 0 && (
                  <div className="flex items-center gap-2.5">
                    <div className="flex -space-x-1.5">
                      {[1,2,3].map(i => (
                        <div key={i} className="w-6 h-6 rounded-full bg-gradient-to-br from-[#C9A84C]/30 to-[#C9A84C]/10 border-2 border-[#0a0a08] flex items-center justify-center">
                          <Users className="w-2.5 h-2.5 text-[#C9A84C]/60" />
                        </div>
                      ))}
                    </div>
                    <div className="leading-tight">
                      <span className="text-[#f5f0e8] text-sm font-bold">{visitorCount.toLocaleString('fr-FR')}+</span>
                      <span className="text-[#f5f0e8]/30 text-xs block">personnes accompagnees</span>
                    </div>
                  </div>
                )}
                <div className="h-5 w-px bg-[#f5f0e8]/10 hidden sm:block" />
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-[#C9A84C]/15 flex items-center justify-center">
                    <Zap className="w-2.5 h-2.5 text-[#C9A84C]" />
                  </div>
                  <span className="text-[#f5f0e8]/60 text-xs font-medium">Reponse sous 2h</span>
                </div>
              </div>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-3 mb-2">
                <Button
                  size="lg"
                  onClick={() => window.dispatchEvent(new Event('strategiia:open'))}
                  className="w-full sm:w-auto rounded-lg px-7 py-5 gap-2 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-bold text-sm shadow-xl shadow-[#C9A84C]/20 transition-all hover:shadow-[#C9A84C]/35 hover:scale-[1.02] cursor-pointer"
                  data-testid="hero-cta-primary"
                >
                  <Sparkles className="w-4 h-4 flex-shrink-0" />
                  Lancer mon analyse
                </Button>
                <Link to="/contact">
                  <Button
                    variant="outline"
                    size="lg"
                    className="w-full sm:w-auto rounded-lg px-7 py-5 gap-2 border-[#C9A84C]/30 text-[#f5f0e8]/80 hover:bg-[#C9A84C]/5 hover:border-[#C9A84C]/50 text-sm transition-all"
                    data-testid="hero-cta-secondary"
                  >
                    Etre accompagne maintenant
                  </Button>
                </Link>
              </div>

              {/* Texte sous CTAs */}
              <p className="text-xs text-[#f5f0e8]/30 leading-relaxed">
                <span className="text-[#C9A84C]/50">Analyse immediate par IA</span> ou <span className="text-[#C9A84C]/50">prise en charge humaine personnalisee</span>.
              </p>
            </div>

            {/* ── COLONNE DROITE : Visuel premium — contenu ── */}
            <div className="order-1 lg:order-2 flex justify-center lg:justify-end">
              <div className="w-full max-w-[380px]">
                {/* Cadre image — ombre profonde + filet doré gauche */}
                <div className="relative">
                  <div className="overflow-hidden shadow-[0_25px_60px_-12px_rgba(0,0,0,0.7)]">
                    <img
                      src="https://images.pexels.com/photos/28446973/pexels-photo-28446973.jpeg?auto=compress&cs=tinysrgb&w=800"
                      alt="Expert en strategie sante"
                      className="w-full aspect-[4/5] object-cover object-top"
                      loading="eager"
                    />
                    {/* Fondu bas — intégration dans le fond */}
                    <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-[#0a0a08] to-transparent" />
                  </div>
                  {/* Filet doré vertical — accent luxe discret */}
                  <div className="absolute top-6 bottom-6 -left-3 w-[2px] bg-gradient-to-b from-transparent via-[#C9A84C]/40 to-transparent" />
                </div>
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
          2. POURQUOI CE SITE EXISTE — Ivory background, rounded image
      ══════════════════════════════════════════════════════════ */}
      <section className="relative py-16 sm:py-20 lg:py-24 overflow-hidden bg-[#F8F5EF]" data-testid="home-founder-quote">
        <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">
            {/* Left: Image with floating card */}
            <div className="flex justify-center">
              <div className="relative">
                <div className="w-64 h-72 sm:w-72 sm:h-80 rounded-3xl overflow-hidden shadow-xl">
                  <img
                    src="https://images.pexels.com/photos/28446973/pexels-photo-28446973.jpeg?auto=compress&cs=tinysrgb&w=600"
                    alt="Fondateur S.E.S"
                    className="w-full h-full object-cover object-top"
                  />
                </div>
                {/* Floating "Decision de justice" card */}
                <div className="absolute -top-3 -right-6 sm:-right-10 bg-[#111] border border-[#C9A84C]/25 rounded-xl px-4 py-3 shadow-xl z-10">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-[#C9A84C]/15 flex items-center justify-center flex-shrink-0">
                      <Scale className="w-4 h-4 text-[#C9A84C]" />
                    </div>
                    <div>
                      <p className="text-white text-[11px] font-semibold leading-tight">Decision de justice</p>
                      <p className="text-emerald-400 text-[10px]">reconnue favorable</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Text */}
            <div>
              <span className="text-[#C9A84C] text-xs font-medium uppercase tracking-[0.2em] mb-4 block">Pourquoi ce site existe</span>
              <h2
                className="text-xl sm:text-2xl lg:text-3xl font-bold leading-snug mb-6"
                style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
              >
                <span className="text-[#1a1a1a]">Ce service n'est pas ne d'une theorie.</span><br />
                <span className="text-[#C9A84C]">Il est ne d'un combat reel.</span>
              </h2>

              <p className="text-[#1a1a1a]/60 text-sm leading-relaxed mb-4">
                Strategie & Expertise Sante a ete fondee a partir d'un vecu concret du monde des maladies professionnelles, accidents du travail, invalidites et litiges administratifs.
              </p>
              <p className="text-[#1a1a1a]/60 text-sm leading-relaxed">
                Ici, chaque analyse vise un objectif simple : vous aider a mieux comprendre votre situation, defendre vos droits et eviter de rester seul face a des demarches complexes.
              </p>

              <footer className="mt-6 flex items-center gap-3" data-testid="home-founder-blockquote">
                <div className="w-8 h-px bg-[#C9A84C]/40" />
                <cite className="text-xs font-medium text-[#C9A84C]/70 not-italic tracking-widest uppercase">Fondateur — S.E.S</cite>
              </footer>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          3. NOS DEUX INTELLIGENCES DE DOSSIER
      ══════════════════════════════════════════════════════════ */}
      <section className="py-16 sm:py-20 lg:py-24 bg-[#F8F5EF]" data-testid="solutions-section" ref={solutionsRef}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12 reveal">
            <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Deux intelligences complementaires</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold mt-3 mb-4 text-[#1a1a1a]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Quel service est fait pour vous ?
            </h2>
            <p className="text-sm text-[#1a1a1a]/40">
              Deux parcours distincts, une meme exigence de qualite.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 lg:gap-8 stagger">
            {/* Card 1 — StrategiIA — DARK CARD */}
            <div className="reveal" data-testid="solution-card-0">
              <Link to="/simulateur" className="group block h-full">
                <div className="h-full bg-[#111] rounded-2xl p-7 sm:p-8 transition-all duration-300 hover:shadow-2xl hover:shadow-[#C9A84C]/5 group-hover:-translate-y-1">
                  <div className="flex items-center gap-4 mb-5">
                    <div className="w-12 h-12 rounded-xl bg-[#C9A84C]/10 flex items-center justify-center">
                      <Brain className="w-6 h-6 text-[#C9A84C]" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-[#f5f0e8]">StrategiIA</h3>
                      <p className="text-[#C9A84C] font-semibold text-xs">Pre-analyse gratuite</p>
                    </div>
                  </div>

                  <p className="text-[#f5f0e8]/45 text-sm leading-relaxed mb-5">
                    Votre premier eclairage strategique. Une analyse intelligente de votre situation pour comprendre vos droits et identifier vos leviers.
                  </p>

                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div>
                      <p className="text-[#C9A84C] text-[10px] font-bold uppercase tracking-wider mb-2.5">Ideal pour</p>
                      {["Comprendre votre situation", "Identifier vos droits", "Obtenir une premiere orientation"].map((t, i) => (
                        <div key={i} className="flex items-start gap-2 mb-2">
                          <CheckCircle className="w-3 h-3 text-[#C9A84C]/60 flex-shrink-0 mt-0.5" />
                          <span className="text-[#f5f0e8]/50 text-xs leading-tight">{t}</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <p className="text-[#C9A84C] text-[10px] font-bold uppercase tracking-wider mb-2.5">Ce que vous recevez</p>
                      {["Analyse strategique IA", "Orientation personnalisee", "Leviers d'action identifies"].map((t, i) => (
                        <div key={i} className="flex items-start gap-2 mb-2">
                          <CheckCircle className="w-3 h-3 text-[#C9A84C]/60 flex-shrink-0 mt-0.5" />
                          <span className="text-[#f5f0e8]/50 text-xs leading-tight">{t}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <span className="inline-flex items-center gap-2 text-[#C9A84C] text-sm font-medium group-hover:gap-3 transition-all">
                    Lancer mon analyse <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </Link>
            </div>

            {/* Card 2 — Dossier Express IA — IVORY CARD */}
            <div className="reveal" data-testid="solution-card-1">
              <Link to="/dossier-express" className="group block h-full">
                <div className="h-full bg-white border border-[#C9A84C]/15 rounded-2xl p-7 sm:p-8 transition-all duration-300 hover:shadow-2xl hover:shadow-[#C9A84C]/10 group-hover:-translate-y-1 relative overflow-hidden">
                  <div className="absolute top-4 right-4">
                    <span className="bg-red-600 text-white text-[9px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full">Urgence</span>
                  </div>

                  <div className="flex items-center gap-4 mb-5">
                    <div className="w-12 h-12 rounded-xl bg-[#C9A84C]/10 flex items-center justify-center">
                      <Zap className="w-6 h-6 text-[#C9A84C]" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-[#1a1a1a]">Dossier Express IA</h3>
                      <p className="text-[#C9A84C] font-semibold text-xs">97 EUR — Livre sous 2h</p>
                    </div>
                  </div>

                  <p className="text-[#1a1a1a]/50 text-sm leading-relaxed mb-5">
                    L'analyse documentaire complete de votre dossier. Un rapport structure, approfondi et exploitable pour vos demarches.
                  </p>

                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div>
                      <p className="text-[#C9A84C] text-[10px] font-bold uppercase tracking-wider mb-2.5">Ideal pour</p>
                      {["Expertise medicale imminente", "Preparer votre strategie", "Analyser vos documents"].map((t, i) => (
                        <div key={i} className="flex items-start gap-2 mb-2">
                          <CheckCircle className="w-3 h-3 text-[#C9A84C]/60 flex-shrink-0 mt-0.5" />
                          <span className="text-[#1a1a1a]/60 text-xs leading-tight">{t}</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <p className="text-[#C9A84C] text-[10px] font-bold uppercase tracking-wider mb-2.5">Ce que vous recevez</p>
                      {["Rapport d'analyse detaille", "Etude de vos documents", "Strategie d'action concrete"].map((t, i) => (
                        <div key={i} className="flex items-start gap-2 mb-2">
                          <CheckCircle className="w-3 h-3 text-[#C9A84C]/60 flex-shrink-0 mt-0.5" />
                          <span className="text-[#1a1a1a]/60 text-xs leading-tight">{t}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <span className="inline-flex items-center gap-2 text-[#C9A84C] text-sm font-medium group-hover:gap-3 transition-all">
                    Deposer mon dossier <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </Link>
            </div>
          </div>

          <div className="mt-8 text-center reveal">
            <Link to="/contact" data-testid="solution-card-2">
              <Button className="rounded-lg px-8 py-5 gap-2.5 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-bold text-sm">
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

    </main>
  );
};
