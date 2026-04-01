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
import { GoldDustOverlay } from '@/components/GoldDustOverlay';
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
    { icon: CircleSlash, text: "Sous-évaluation de votre taux d'IPP" },
    { icon: ShieldAlert, text: "Mauvaise reconnaissance de l'incidence professionnelle" },
    { icon: ScanSearch, text: "Expertise médicale défavorable" },
    { icon: AlertTriangle, text: "Perte financière importante et irréversible" },
  ];

  const methodeSES = [
    { num: "01", icon: Crosshair, title: "Analyse stratégique", desc: "Étude approfondie de votre situation médicale, administrative et financière." },
    { num: "02", icon: ShieldAlert, title: "Identification des risques", desc: "Repérage des failles, incohérences et points de vigilance." },
    { num: "03", icon: Compass, title: "Orientation experte", desc: "Mise en relation avec les experts les plus adaptés à votre pathologie." },
    { num: "04", icon: Focus, title: "Optimisation de l'expertise", desc: "Préparation stratégique pour maximiser la reconnaissance." },
    { num: "05", icon: RefreshCcw, title: "Suivi et ajustement", desc: "Accompagnement continu et adaptation de la stratégie." },
  ];

  const chiffresCles = [
    { icon: HardHat, value: 700000, unit: '', prefix: "Plus de", suffix: "accidents du travail par an en France", source: "CNAM", lien: "https://assurance-maladie.ameli.fr" },
    { icon: Activity, value: 50000, unit: '', prefix: "Environ", suffix: "maladies professionnelles reconnues chaque année", source: "CNAM", lien: "https://assurance-maladie.ameli.fr" },
    { icon: Accessibility, value: 12, unit: ' millions', prefix: "Près de", suffix: "de personnes en situation de handicap", source: "INSEE", lien: "https://www.insee.fr" },
    { icon: ClipboardList, value: 300000, unit: '', prefix: "Plus de", suffix: "nouvelles demandes MDPH chaque année", source: "CNSA", lien: "https://www.cnsa.fr" },
  ];

  const confiance = [
    { icon: HeartHandshake, title: "Expertise terrain réelle", desc: "Née d'une expérience personnelle face aux mêmes épreuves que les vôtres." },
    { icon: Stethoscope, title: "Maîtrise des enjeux médicaux", desc: "Tableaux de maladies professionnelles, barèmes et procédures." },
    { icon: Award, title: "Approche stratégique unique", desc: "Chaque dossier est traité comme un cas à part, avec une stratégie sur mesure." },
    { icon: TrendingUp, title: "Vision orientée résultats", desc: "Obtenir la reconnaissance et l'indemnisation que vous méritez." },
  ];

  const temoignages = [
    { initials: "M.L.", age: "52 ans", badge: "AT", text: "Après 18 mois de refus par la CPAM, mon accident du travail a enfin été reconnu. Sans cet accompagnement, j'aurais abandonné les démarches.", result: "AT reconnue — Rente obtenue" },
    { initials: "P.D.", age: "45 ans", badge: "PTIA", badgeGold: true, text: "Mon assureur refusait de reconnaître ma PTIA malgre l'avis de trois médecins. Grâce à une stratégie méthodique, la garantie a été activée après 8 mois de recours.", result: "Garantie PTIA activée" },
    { initials: "S.B.", age: "38 ans", badge: "MP", text: "Ma maladie professionnelle n'était pas dans les tableaux. L'accompagnement m'a permis de constituer un dossier solide — reconnaissance obtenue au premier passage.", result: "MP hors tableau reconnue" },
    { initials: "C.R.", age: "61 ans", badge: "IPP", text: "Mon taux d'IPP avait été évalué à 5% alors que mes séquelles sont bien plus importantes. Après contestation, le taux a été réévalué à 23%.", result: "IPP réévaluée : 5% → 23%" },
    { initials: "A.M.", age: "34 ans", badge: "MDPH", text: "Mes demandes MDPH étaient systématiquement refusées. Grâce à un dossier structuré et des arguments adaptés, j'ai obtenu l'AAH en moins de 4 mois.", result: "AAH obtenue en 4 mois" },
    { initials: "J.T.", age: "48 ans", badge: "ITT", badgeGold: true, text: "Mon assurance refusait les indemnités ITT en invoquant une clause floue. L'analyse du contrat a permis de débloquer 14 mois d'arriérés.", result: "ITT versée — Arriérés récupérés" },
  ];

  const ecosysteme = [
    { icon: Brain, title: "StrategiIA", desc: "Analyse intelligente de votre situation", href: "/simulateur" },
    { icon: Zap, title: "Dossier Express IA", desc: "Rapport d'analyse complet sous 2h", href: "/dossier-express" },
    { icon: Users, title: "Accompagnement humain", desc: "Suivi personnalisé par un expert", href: "/contact" },
    { icon: Stethoscope, title: "Médecin conseil", desc: "Orientation vers le bon spécialiste", href: "/medecin-conseil" },
    { icon: Calculator, title: "Calculatrices IPP & AAH", desc: "Estimez vos droits en quelques clics", href: "/calculatrice-ipp" },
    { icon: BookOpen, title: "Ressources & guides", desc: "Documentation experte gratuite", href: "/ressources" },
    { icon: ScanSearch, title: "Scanner de documents", desc: "Numérisez vos pièces facilement", href: "/dossier-express" },
    { icon: CalendarDays, title: "Rendez-vous", desc: "Planifiez votre consultation", href: "/agenda" },
  ];

  return (
    <main className="page-transition">
      <SEO
        title="Accueil"
        description="Stratégie & Expertise Santé : accompagnement expert en maladie professionnelle, accident du travail, MDPH et protection juridique."
        path="/"
      />

      {/* ══════════════════════════════════════════════════════════
          1. HERO — Structure propre, stable, 2 colonnes
      ══════════════════════════════════════════════════════════ */}
      {/* 
        ZONE GELÉE — HERO VALIDÉ
        Ne pas modifier librement cette section sans validation visuelle complète desktop + mobile.
        Toute modification doit conserver :
        - même hauteur générale
        - même hiérarchie visuelle
        - même position des CTA
        - même équilibre texte / image
      */}
      <section className="relative bg-[#0a0a08] overflow-clip" style={{ clipPath: 'inset(0)' }} data-testid="hero-section">
        {/* Fond premium — lueur dorée diffuse */}
        <div className="absolute top-1/2 right-0 w-[600px] h-[600px] -translate-y-1/2 translate-x-1/4 bg-[#C9A84C]/[0.05] rounded-full blur-[180px] pointer-events-none" />
        {/* Halo doré bas-gauche */}
        <div className="absolute bottom-0 left-0 w-[500px] h-[400px] bg-[#C9A84C]/[0.03] rounded-full blur-[150px] pointer-events-none translate-y-1/3 -translate-x-1/4" />
        {/* Halo doré bas-droite */}
        <div className="absolute bottom-0 right-0 w-[400px] h-[350px] bg-[#C9A84C]/[0.035] rounded-full blur-[130px] pointer-events-none translate-y-1/4 translate-x-1/4" />
        {/* Poussière d'or — particules scintillantes */}
        <GoldDustOverlay />
        <div className="relative max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8 pt-16 sm:pt-20 lg:pt-14 pb-4 sm:pb-6 lg:pb-3">
          <div className="grid lg:grid-cols-[55fr_45fr] gap-8 lg:gap-12 items-center">

            {/* ── COLONNE GAUCHE : Contenu ── */}
            <div className="relative z-10">
              {/* Badge — Reconstruit : structure simple et saine */}
              <div
                className="invisible sm:visible flex w-fit items-center gap-3.5 rounded-xl bg-[#161612] border border-[#C9A84C]/15 px-3.5 py-2 sm:px-5 sm:py-2.5 mb-2"
                data-testid="pioneer-badge"
              >
                <div className="w-8 h-8 rounded-md bg-[#C9A84C]/10 border border-[#C9A84C]/15 flex items-center justify-center flex-shrink-0">
                  <Scale className="w-4 h-4 text-[#C9A84C]" />
                </div>
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#C9A84C] block">Pionnier en France</span>
                  <span className="text-[11px] text-[#C9A84C]/55 block mt-0.5">Plateforme d'analyse & d'accompagnement en droits santé</span>
                </div>
              </div>

              {/* Sous-titre métier — clarification immédiate */}
              <p className="text-[12px] sm:text-[13px] uppercase tracking-[0.22em] text-[#f5f0e8]/35 mb-2 sm:mb-3" data-testid="hero-metier-subtitle">
                Conseil en droits MDPH, AT/MP et litiges assuranciels
              </p>

              {/* Titre — noble et respirant */}
              <h1
                className="text-[1.75rem] sm:text-[2rem] lg:text-[2.1rem] xl:text-[2.3rem] font-bold text-[#f5f0e8] leading-[1.22] mb-3"
                style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
                data-testid="hero-title"
              >
                Vous n'êtes plus seul<br className="hidden sm:block" /> face à{' '}
                <span className="text-[#C9A84C]">votre dossier</span>,{' '}
                <span className="text-[#C9A84C]">vos droits</span><br className="hidden sm:block" /> ou{' '}
                <span className="text-[#C9A84C]">vos recours</span>.
              </h1>

              {/* Sous-titre */}
              <p className="text-xs sm:text-[13px] text-[#f5f0e8]/50 leading-[1.8] mb-3 max-w-xl" data-testid="hero-subtitle">
                Analysez votre situation, identifiez vos leviers, comprenez vos droits et accédez à un accompagnement stratégique humain en cas de{' '}
                <strong className="text-[#f5f0e8]/70">maladie professionnelle</strong>,{' '}
                <strong className="text-[#f5f0e8]/70">accident du travail</strong>,{' '}
                <strong className="text-[#f5f0e8]/70">MDPH</strong> ou{' '}
                <strong className="text-[#f5f0e8]/70">litige assuranciel</strong>.
              </p>

              {/* 3 points clés */}
              <div className="space-y-2 mb-3">
                {[
                  { icon: HeartHandshake, text: "Expertise née d'un vécu concret" },
                  { icon: Crosshair, text: "Méthode stratégique & personnalisée" },
                  { icon: Brain, text: "Analyse IA + accompagnement humain" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-full border border-[#C9A84C]/25 bg-[#C9A84C]/[0.06] flex items-center justify-center flex-shrink-0">
                      <item.icon className="w-3.5 h-3.5 text-[#C9A84C]" />
                    </div>
                    <span className="text-[#f5f0e8]/60 text-[13px]">{item.text}</span>
                  </div>
                ))}
              </div>

              {/* Micro-ligne IA — pont de conversion */}
              <p className="text-[13px] text-[#C9A84C]/65 tracking-[0.04em] mb-3 border-l-2 border-[#C9A84C]/20 pl-3" data-testid="hero-ia-availability">
                <Zap className="w-3 h-3 inline-block mr-1.5 -mt-px text-[#C9A84C]/50" />
                Vos deux agents IA vous répondent immédiatement, à toute heure.
              </p>

              {/* Preuve sociale + CTA Urgent intégré */}
              <div className="flex flex-wrap items-center gap-5 sm:gap-6 mb-3">
                {visitorCount > 0 && (
                  <div className="flex items-center gap-2">
                    <div className="flex -space-x-1.5">
                      {[1,2,3].map(i => (
                        <div key={i} className="w-5 h-5 rounded-full bg-gradient-to-br from-[#C9A84C]/30 to-[#C9A84C]/10 border-2 border-[#0a0a08] flex items-center justify-center">
                          <Users className="w-2 h-2 text-[#C9A84C]/60" />
                        </div>
                      ))}
                    </div>
                    <div className="leading-tight">
                      <span className="text-[#f5f0e8] text-xs font-bold">{visitorCount.toLocaleString('fr-FR')}+</span>
                      <span className="text-[#f5f0e8]/30 text-[10px] block">personnes accompagnées</span>
                    </div>
                  </div>
                )}
                <div className="h-5 w-px bg-[#f5f0e8]/10 hidden sm:block" />
                <button
                  onClick={() => window.dispatchEvent(new Event('alerte-urgente:open'))}
                  className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg border border-[#C9A84C]/20 bg-[#C9A84C]/[0.06] text-[#C9A84C]/80 hover:text-[#C9A84C] hover:border-[#C9A84C]/35 hover:bg-[#C9A84C]/[0.1] transition-all cursor-pointer"
                  data-testid="hero-urgent-cta"
                >
                  <Zap className="w-3 h-3" />
                  <span className="text-xs font-medium tracking-wide">Besoin urgent ?</span>
                </button>
              </div>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-3.5 mb-2">
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
                    Être accompagné maintenant
                  </Button>
                </Link>
              </div>

              {/* Texte sous CTAs */}
              <p className="text-xs text-[#f5f0e8]/45 leading-relaxed tracking-wide">
                <span className="text-[#C9A84C]/70">Analyse immédiate par IA</span> ou <span className="text-[#C9A84C]/70">prise en charge humaine personnalisée</span>.
              </p>
            </div>

            {/* ── COLONNE DROITE : Visuel signature ── */}
            <div className="absolute inset-0 lg:relative lg:order-2 lg:flex lg:justify-center lg:justify-end">
              <div className="w-full h-full lg:max-w-[400px] relative">
                {/* Halo doré subtil derrière l'image */}
                <div className="absolute -inset-10 bg-[#C9A84C]/[0.04] rounded-full blur-[70px] pointer-events-none hidden lg:block" />
                {/* Cadre image — ombre profonde + filet doré gauche */}
                <div className="relative">
                  <div className="overflow-hidden shadow-[0_35px_80px_-15px_rgba(0,0,0,0.75)] h-full lg:h-auto">
                    <img
                      src="https://images.pexels.com/photos/28446973/pexels-photo-28446973.jpeg?auto=compress&cs=tinysrgb&w=800"
                      alt="Expert en stratégie santé"
                      className="w-full h-full lg:aspect-[4/5] object-cover object-top"
                      loading="eager"
                    />
                    {/* Fondu haut — intégration douce */}
                    <div className="absolute top-0 left-0 right-0 h-16 bg-gradient-to-b from-[#0a0a08]/40 to-transparent" />
                    {/* Fondu bas — intégration dans le fond */}
                    <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-[#0a0a08] via-[#0a0a08]/60 to-transparent" />
                    {/* Overlay sombre mobile — lisibilité du texte */}
                    <div className="absolute inset-0 bg-[#0a0a08]/70 lg:hidden" />
                  </div>

                  {/* ── 3 Blocs flottants sur l'image ── */}
                  {/* Bloc Analyse IA — haut gauche */}
                  <button onClick={() => window.dispatchEvent(new Event('strategiia:open'))} className="hidden lg:flex absolute z-20 lg:top-[12%] lg:left-[-8%] lg:right-auto items-center gap-2 sm:gap-2.5 bg-[#0c0c1a]/90 backdrop-blur-md border border-[#C9A84C]/10 rounded-xl px-2 py-1.5 sm:px-3.5 sm:py-2.5 shadow-[0_0_20px_rgba(201,168,76,0.12)] cursor-pointer hover:bg-[#0c0c1a]/95 hover:shadow-[0_0_25px_rgba(201,168,76,0.2)] hover:border-[#C9A84C]/20 transition-all" data-testid="hero-bloc-analyse">
                    <div className="w-7 h-7 sm:w-9 sm:h-9 rounded-lg bg-[#C9A84C]/15 border border-[#C9A84C]/30 flex items-center justify-center flex-shrink-0">
                      <Brain className="w-3.5 h-3.5 sm:w-4.5 sm:h-4.5 text-[#C9A84C]" />
                    </div>
                    <div>
                      <span className="text-white font-bold text-[10px] sm:text-xs block leading-tight">Analyse IA</span>
                      <span className="text-white/60 text-[8px] sm:text-[10px] block leading-tight">Lecture intelligente<br/>de votre situation</span>
                    </div>
                  </button>

                  {/* Bloc Documents — droite centre */}
                  <Link to="/dossier-express?step=form" className="hidden lg:flex absolute z-20 lg:top-[25%] lg:right-[-5%] items-center gap-2 sm:gap-2.5 bg-[#0c0c1a]/90 backdrop-blur-md border border-[#C9A84C]/10 rounded-xl px-2 py-1.5 sm:px-3.5 sm:py-2.5 shadow-[0_0_20px_rgba(201,168,76,0.12)] cursor-pointer hover:bg-[#0c0c1a]/95 hover:shadow-[0_0_25px_rgba(201,168,76,0.2)] hover:border-[#C9A84C]/20 transition-all" data-testid="hero-bloc-documents">
                    <div className="w-7 h-7 sm:w-9 sm:h-9 rounded-lg bg-[#C9A84C]/15 border border-[#C9A84C]/30 flex items-center justify-center flex-shrink-0">
                      <FileText className="w-3.5 h-3.5 sm:w-4.5 sm:h-4.5 text-[#C9A84C]" />
                    </div>
                    <div>
                      <span className="text-white font-bold text-[10px] sm:text-xs block leading-tight">Documents</span>
                      <span className="text-white/60 text-[8px] sm:text-[10px] block leading-tight">Étude approfondie<br/>de vos pièces</span>
                    </div>
                  </Link>

                  {/* Bloc Orientation — bas centre */}
                  <Link to="/simulateur" className="hidden lg:flex absolute z-20 lg:top-auto lg:right-auto lg:bottom-[38%] lg:left-1/2 lg:-translate-x-1/2 items-center gap-2 sm:gap-2.5 bg-[#0c0c1a]/90 backdrop-blur-md border border-[#C9A84C]/10 rounded-xl px-2 py-1.5 sm:px-3.5 sm:py-2.5 shadow-[0_0_20px_rgba(201,168,76,0.12)] cursor-pointer hover:bg-[#0c0c1a]/95 hover:shadow-[0_0_25px_rgba(201,168,76,0.2)] hover:border-[#C9A84C]/20 transition-all" data-testid="hero-bloc-orientation">
                    <div className="w-7 h-7 sm:w-9 sm:h-9 rounded-lg bg-[#C9A84C]/15 border border-[#C9A84C]/30 flex items-center justify-center flex-shrink-0">
                      <Compass className="w-3.5 h-3.5 sm:w-4.5 sm:h-4.5 text-[#C9A84C]" />
                    </div>
                    <div>
                      <span className="text-white font-bold text-[10px] sm:text-xs block leading-tight">Orientation</span>
                      <span className="text-white/60 text-[8px] sm:text-[10px] block leading-tight">Stratégie adaptée<br/>à votre dossier</span>
                    </div>
                  </Link>
                  <div className="absolute top-4 bottom-4 -left-3 w-[2px] bg-gradient-to-b from-transparent via-[#C9A84C]/35 to-transparent hidden lg:block" />
                  {/* Filet doré horizontal bas */}
                  <div className="absolute -bottom-2 left-8 right-8 h-[1px] bg-gradient-to-r from-transparent via-[#C9A84C]/20 to-transparent hidden lg:block" />
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ── Dossier Express urgence strip ── */}
      <section className="relative overflow-clip" data-testid="dossier-express-banner">
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
      <section className="relative py-16 sm:py-20 lg:py-24 overflow-clip bg-[#F8F5EF]" data-testid="home-founder-quote">
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
                {/* 3 Blocs CTA — mobile + desktop */}
                <button onClick={() => window.dispatchEvent(new Event('strategiia:open'))} className="absolute top-[15%] -left-4 sm:top-[15%] sm:-left-6 flex lg:hidden items-center gap-1.5 sm:gap-2 bg-[#0c0c1a]/90 backdrop-blur-sm rounded-lg px-2 py-1.5 sm:px-3 sm:py-2 shadow-[0_0_15px_rgba(201,168,76,0.12)] z-10 cursor-pointer hover:bg-[#0c0c1a]/95 hover:shadow-[0_0_20px_rgba(201,168,76,0.2)] transition-all" data-testid="founder-bloc-analyse">
                  <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-md bg-[#C9A84C]/15 border border-[#C9A84C]/30 flex items-center justify-center flex-shrink-0">
                    <Brain className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-[#C9A84C]" />
                  </div>
                  <div>
                    <span className="text-white font-bold text-[9px] sm:text-[11px] block leading-tight">Analyse IA</span>
                    <span className="text-white/50 text-[7px] sm:text-[9px] block leading-tight">Lecture intelligente</span>
                  </div>
                </button>

                <Link to="/dossier-express?step=form" className="absolute top-[25%] -right-4 sm:-right-6 flex lg:hidden items-center gap-1.5 sm:gap-2 bg-[#0c0c1a]/90 backdrop-blur-sm rounded-lg px-2 py-1.5 sm:px-3 sm:py-2 shadow-[0_0_15px_rgba(201,168,76,0.12)] z-10 cursor-pointer hover:bg-[#0c0c1a]/95 hover:shadow-[0_0_20px_rgba(201,168,76,0.2)] transition-all" data-testid="founder-bloc-documents">
                  <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-md bg-[#C9A84C]/15 border border-[#C9A84C]/30 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-[#C9A84C]" />
                  </div>
                  <div>
                    <span className="text-white font-bold text-[9px] sm:text-[11px] block leading-tight">Documents</span>
                    <span className="text-white/50 text-[7px] sm:text-[9px] block leading-tight">Étude de vos pièces</span>
                  </div>
                </Link>

                <Link to="/simulateur" className="absolute bottom-[30%] sm:bottom-[30%] left-1/2 -translate-x-1/2 flex lg:hidden items-center gap-1.5 sm:gap-2 bg-[#0c0c1a]/90 backdrop-blur-sm rounded-lg px-2 py-1.5 sm:px-3 sm:py-2 shadow-[0_0_15px_rgba(201,168,76,0.12)] z-10 cursor-pointer hover:bg-[#0c0c1a]/95 hover:shadow-[0_0_20px_rgba(201,168,76,0.2)] transition-all" data-testid="founder-bloc-orientation">
                  <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-md bg-[#C9A84C]/15 border border-[#C9A84C]/30 flex items-center justify-center flex-shrink-0">
                    <Compass className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-[#C9A84C]" />
                  </div>
                  <div>
                    <span className="text-white font-bold text-[9px] sm:text-[11px] block leading-tight">Orientation</span>
                    <span className="text-white/50 text-[7px] sm:text-[9px] block leading-tight">Stratégie adaptée</span>
                  </div>
                </Link>
              </div>
            </div>

            {/* Right: Text */}
            <div>
              <span className="text-[#C9A84C] text-xs font-medium uppercase tracking-[0.2em] mb-4 block">Pourquoi ce site existe</span>
              <h2
                className="text-xl sm:text-2xl lg:text-3xl font-bold leading-snug mb-6"
                style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
              >
                <span className="text-[#1a1a1a]">Ce service n'est pas né d'une théorie.</span><br />
                <span className="text-[#C9A84C]">Il est né d'un combat réel.</span>
              </h2>

              <p className="text-[#1a1a1a]/60 text-sm leading-relaxed mb-4">
                Stratégie & Expertise Santé a été fondée à partir d'un vécu concret du monde des maladies professionnelles, accidents du travail, invalidités et litiges administratifs.
              </p>
              <p className="text-[#1a1a1a]/60 text-sm leading-relaxed">
                Ici, chaque analyse vise un objectif simple : vous aider à mieux comprendre votre situation, défendre vos droits et éviter de rester seul face à des démarches complexes.
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
      <section className="py-16 sm:py-20 lg:py-24 overflow-clip bg-[#F8F5EF]" data-testid="solutions-section" ref={solutionsRef}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12 reveal">
            <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Deux intelligences complémentaires</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold mt-3 mb-4 text-[#1a1a1a]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Quel service est fait pour vous ?
            </h2>
            <p className="text-sm text-[#1a1a1a]/40">
              Deux parcours distincts, une même exigence de qualité.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 lg:gap-8 stagger">
            {/* Card 1 — StrategiIA — DARK CARD */}
            <div className="reveal" data-testid="solution-card-0">
              <Link to="/simulateur" className="group block h-full" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('strategiia:open')); }}>
                <div className="h-full bg-[#111] rounded-2xl p-7 sm:p-8 transition-all duration-300 hover:shadow-2xl hover:shadow-[#C9A84C]/5 group-hover:-translate-y-1">
                  <div className="flex items-center gap-4 mb-5">
                    <div className="w-12 h-12 rounded-xl bg-[#C9A84C]/10 flex items-center justify-center">
                      <Brain className="w-6 h-6 text-[#C9A84C]" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-[#f5f0e8]">StrategiIA</h3>
                      <p className="text-[#C9A84C] font-semibold text-xs">Pré-analyse gratuite</p>
                    </div>
                  </div>

                  <p className="text-[#f5f0e8]/45 text-sm leading-relaxed mb-5">
                    Votre premier éclairage stratégique. Une analyse intelligente de votre situation pour comprendre vos droits et identifier vos leviers.
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                    <div>
                      <p className="text-[#C9A84C] text-[10px] font-bold uppercase tracking-wider mb-2.5">Idéal pour</p>
                      {["Comprendre votre situation", "Identifier vos droits", "Obtenir une première orientation"].map((t, i) => (
                        <div key={i} className="flex items-start gap-2 mb-2">
                          <CheckCircle className="w-3 h-3 text-[#C9A84C]/60 flex-shrink-0 mt-0.5" />
                          <span className="text-[#f5f0e8]/50 text-xs leading-tight">{t}</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <p className="text-[#C9A84C] text-[10px] font-bold uppercase tracking-wider mb-2.5">Ce que vous recevez</p>
                      {["Analyse stratégique IA", "Orientation personnalisée", "Leviers d'action identifiés"].map((t, i) => (
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
              <Link to="/dossier-express?step=form" className="group block h-full">
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
                      <p className="text-[#C9A84C] font-semibold text-xs">97 EUR — Livré sous 2h</p>
                    </div>
                  </div>

                  <p className="text-[#1a1a1a]/50 text-sm leading-relaxed mb-5">
                    L'analyse documentaire complète de votre dossier. Un rapport structuré, approfondi et exploitable pour vos démarches.
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                    <div>
                      <p className="text-[#C9A84C] text-[10px] font-bold uppercase tracking-wider mb-2.5">Idéal pour</p>
                      {["Expertise médicale imminente", "Préparer votre stratégie", "Analyser vos documents"].map((t, i) => (
                        <div key={i} className="flex items-start gap-2 mb-2">
                          <CheckCircle className="w-3 h-3 text-[#C9A84C]/60 flex-shrink-0 mt-0.5" />
                          <span className="text-[#1a1a1a]/60 text-xs leading-tight">{t}</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <p className="text-[#C9A84C] text-[10px] font-bold uppercase tracking-wider mb-2.5">Ce que vous recevez</p>
                      {["Rapport d'analyse détaillé", "Étude de vos documents", "Stratégie d'action concrète"].map((t, i) => (
                        <div key={i} className="flex items-start gap-2 mb-2">
                          <CheckCircle className="w-3 h-3 text-[#C9A84C]/60 flex-shrink-0 mt-0.5" />
                          <span className="text-[#1a1a1a]/60 text-xs leading-tight">{t}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <span className="inline-flex items-center gap-2 text-[#C9A84C] text-sm font-medium group-hover:gap-3 transition-all">
                    Déposer mon dossier <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </Link>
            </div>
          </div>

          <div className="mt-8 text-center reveal">
            <Link to="/contact" className="block" data-testid="solution-card-2">
              <Button className="w-full rounded-lg px-6 py-5 gap-2.5 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-bold text-sm whitespace-normal h-auto text-center justify-center">
                <Shield className="w-4 h-4" />
                Accompagnement stratégique complet — Sur devis
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          4. RISQUES — Warning section
      ══════════════════════════════════════════════════════════ */}
      <section className="py-14 sm:py-16 overflow-clip bg-[#0a0a08] border-y border-[#C9A84C]/5" data-testid="risques-section">
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
              Une mauvaise décision aujourd'hui peut vous coûter des milliers d'euros demain.
            </p>
            <Link to="/contact">
              <Button className="rounded-full px-7 gap-2 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-bold text-sm" data-testid="risques-cta">
                <Phone className="w-4 h-4" /> Être accompagné <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          5. ECOSYSTEME DE SERVICES
      ══════════════════════════════════════════════════════════ */}
      <section className="py-16 sm:py-20 lg:py-28 overflow-clip bg-[#111]" data-testid="methode-section" ref={methodeRef}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Écosystème complet</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 mb-4 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Bien plus qu'un outil IA
            </h2>
            <p className="text-sm text-[#f5f0e8]/40">
              Un écosystème complet d'accompagnement, de l'analyse initiale au suivi personnalisé.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-5 stagger">
            {ecosysteme.map((s, i) => (
              <Link key={i} to={s.href} className="group reveal" data-testid={`méthode-step-${i}`}>
                <div className="h-full bg-[#0a0a08] rounded-xl p-4 sm:p-6 border border-white/5 hover:border-[#C9A84C]/20 transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-lg min-w-0">
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
      <section className="py-16 sm:py-20 overflow-clip bg-[#0a0a08] border-y border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Notre approche</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 mb-4 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              La Méthode <span className="text-[#C9A84C]">S.E.S</span>
            </h2>
            <p className="text-sm text-[#f5f0e8]/40">
              Une méthodologie structurée et éprouvée pour défendre efficacement vos intérêts.
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
      <section className="py-16 sm:py-20 overflow-clip bg-[#111] border-b border-white/5" data-testid="medecin-conseil-home-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-8 lg:gap-16 items-center">
            <div className="min-w-0 text-center lg:text-left">
              <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Orientation stratégique</span>
              <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 mb-4 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }} data-testid="home-médecin-conseil-title">
                Le choix du médecin conseil : un enjeu financier majeur
              </h2>
              <p className="text-[#f5f0e8]/50 text-sm leading-relaxed mb-4">
                Un médecin conseil mal choisi peut entraîner une sous-évaluation de vos séquelles et une perte d'indemnisation de plusieurs dizaines de milliers d'euros.
              </p>
              <p className="text-[#f5f0e8]/50 text-sm leading-relaxed mb-6">
                Nous vous orientons vers le professionnel le plus adapté à votre pathologie et à votre stratégie juridique.
              </p>
              <Link to="/medecin-conseil">
                <Button className="rounded-full px-6 py-5 gap-2 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-bold text-sm" data-testid="home-médecin-conseil-cta">
                  <Stethoscope className="w-4 h-4" /> Choisir mon médecin conseil <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:gap-4 min-w-0">
              <div className="bg-[#0a0a08] border border-white/5 p-4 sm:p-5 rounded-xl flex flex-col items-center text-center lg:items-start lg:text-left justify-center">
                <p className="text-base sm:text-xl lg:text-3xl font-bold text-[#C9A84C] mb-1 leading-tight">800 – 3 000 EUR</p>
                <p className="text-[11px] sm:text-xs text-[#f5f0e8]/35 leading-snug">Coût moyen d'un médecin conseil</p>
              </div>
              <div className="bg-[#0a0a08] border border-white/5 p-4 sm:p-5 rounded-xl flex flex-col items-center text-center lg:items-start lg:text-left justify-center">
                <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#C9A84C] mb-1">x10</p>
                <p className="text-[11px] sm:text-xs text-[#f5f0e8]/35 leading-snug">Retour sur investissement potentiel</p>
              </div>
              <div className="col-span-2 bg-[#0a0a08] border border-amber-500/10 p-4 sm:p-5 rounded-xl">
                <div className="flex items-center justify-center lg:justify-start gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0" />
                  <p className="font-semibold text-sm text-[#f5f0e8]">Risque d'un mauvais choix</p>
                </div>
                <p className="text-[11px] sm:text-xs text-[#f5f0e8]/40 leading-relaxed text-center lg:text-left">
                  Un taux d'IPP sous-évalué de quelques points peut représenter une perte de plusieurs dizaines de milliers d'euros sur votre indemnisation finale.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          8. CONFIDENTIALITE / SERENITE
      ══════════════════════════════════════════════════════════ */}
      <section className="py-16 sm:py-20 overflow-clip bg-[#0a0a08]">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <Lock className="w-7 h-7 text-[#C9A84C] mx-auto mb-3" />
            <h2 className="text-xl sm:text-2xl font-semibold text-[#f5f0e8] mb-3" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Vos documents sont entre de bonnes mains
            </h2>
            <p className="text-sm text-[#f5f0e8]/40 max-w-2xl mx-auto">
              Nous comprenons la nature sensible de vos documents médicaux et administratifs. La confidentialité et la sécurité de vos données sont au cœur de nos engagements.
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-5">
            {[
              { icon: Shield, title: "Confidentialité totale", desc: "Vos dossiers ne sont jamais partagés avec des tiers. Traitement strictement confidentiel." },
              { icon: Lock, title: "Sécurité des données", desc: "Vos documents sont traités de manière sécurisée et supprimés après analyse si vous le souhaitez." },
              { icon: Eye, title: "Transparence", desc: "Vous restez maître de vos informations à chaque étape. Aucune utilisation commerciale de vos données." },
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
      <section className="py-16 sm:py-20 overflow-clip bg-[#111]" data-testid="chiffres-section" id="chiffres">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" ref={chiffresRef}>
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Contexte national</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 mb-4 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Le défi en chiffres
            </h2>
            <p className="text-sm text-[#f5f0e8]/40">
              Des millions de personnes sont concernées chaque année en France.
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
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#C9A84C] leading-tight mb-1.5" data-testid={`chiffre-value-${index}`}>
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
      <section className="py-16 sm:py-20 overflow-clip bg-[#0a0a08]" data-testid="confiance-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" ref={confianceRef}>
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-xs font-medium text-[#C9A84C] uppercase tracking-[0.2em]">Crédibilité</span>
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
      <section className="py-16 sm:py-20 overflow-clip bg-[#111]" data-testid="testimonials-section">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <span className="text-[#C9A84C] text-xs font-medium uppercase tracking-[0.2em]">Ils ont fait confiance</span>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold mt-3 text-[#f5f0e8]" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              Des parcours transformés
            </h2>
            <p className="text-[#f5f0e8]/30 mt-3 max-w-xl mx-auto text-sm">
              Témoignages anonymisés de personnes accompagnées par Stratégie & Expertise Santé.
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
            * Prénoms et détails modifiés pour préserver l'anonymat. Résultats réels obtenus pour nos clients.
          </p>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          13. CTA FINAL — Emotional close
      ══════════════════════════════════════════════════════════ */}
      <section className="relative py-20 sm:py-28 overflow-clip bg-[#0a0a08]">
        {/* Background effect */}
        <div className="absolute inset-0 flex items-center justify-center opacity-[0.03]">
          <Shield className="w-[500px] h-[500px] text-[#C9A84C]" strokeWidth={0.3} />
        </div>

        <div className="relative max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center reveal" ref={ctaRef}>
          <h2
            className="text-2xl sm:text-3xl lg:text-4xl font-semibold text-[#f5f0e8] mb-6 leading-snug"
            style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
          >
            Votre situation mérite une stratégie claire, humaine et rigoureuse.
          </h2>

          <p className="text-[#f5f0e8]/45 text-sm sm:text-base mb-10 max-w-2xl mx-auto leading-relaxed">
            Chaque situation est unique. Contactez-nous pour une première consultation gratuite de 10 minutes et sans engagement. Ensemble, nous verrons comment vous accompagner.
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
              Vous n'êtes plus seul face à votre combat.
            </p>
            <p className="text-[#C9A84C] text-lg font-bold tracking-wide">
              Dorénavant, S.E.S est votre bouclier.
            </p>
          </div>
        </div>
      </section>

    </main>
  );
};
