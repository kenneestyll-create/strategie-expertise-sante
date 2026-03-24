import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { useReveal, useRevealChildren } from '@/hooks/useReveal';
import { 
  ArrowRight, 
  Shield, 
  CheckCircle, 
  Sparkles,
  Stethoscope,
  Scale,
  Eye,
  Zap,
  Clock,
  HardHat,
  Activity,
  Accessibility,
  ClipboardList,
  ExternalLink,
  AlertTriangle,
  Phone,
  Crosshair,
  ScanSearch,
  ShieldAlert,
  CircleSlash,
  Compass,
  Focus,
  RefreshCcw,
  HeartHandshake,
  Award,
  TrendingUp,
  Brain
} from 'lucide-react';
import { MascotteMobileWidget } from '@/components/MascotteStrate';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CountUpNumber = ({ value, unit = '', duration = 1200, started }) => {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (!started) return;
    let start = null;
    let raf;
    const step = (ts) => {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.floor(eased * value));
      if (progress < 1) { raf = requestAnimationFrame(step); }
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
        try {
          const res = await axios.get(`${API}/visitors/count`);
          setVisitorCount(res.data.count);
        } catch {}
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

  const risques = [
    { icon: CircleSlash, text: "Sous-évaluation de votre taux d'IPP" },
    { icon: ShieldAlert, text: "Mauvaise reconnaissance de l'incidence professionnelle" },
    { icon: ScanSearch, text: "Expertise médicale défavorable" },
    { icon: AlertTriangle, text: "Perte financière importante et irréversible" },
  ];

  const methodeSES = [
    { num: "01", icon: Crosshair, title: "Analyse stratégique du dossier", desc: "Étude approfondie de votre situation médicale, administrative et financière." },
    { num: "02", icon: ShieldAlert, title: "Identification des risques d'erreur", desc: "Repérage des failles, incohérences et points de vigilance dans votre parcours." },
    { num: "03", icon: Compass, title: "Orientation vers les bons professionnels", desc: "Mise en relation avec les experts les plus adaptés à votre pathologie." },
    { num: "04", icon: Focus, title: "Optimisation de l'expertise médicale", desc: "Préparation stratégique pour maximiser la reconnaissance de vos séquelles." },
    { num: "05", icon: RefreshCcw, title: "Suivi et ajustement", desc: "Accompagnement continu et adaptation de la stratégie selon l'évolution de votre dossier." },
  ];

  const solutions = [
    {
      icon: Zap,
      title: "Dossier Express",
      price: "97 €",
      desc: "Rapport d'analyse complet livré sous 2h. Idéal si vous avez une expertise imminente ou un dossier bloqué.",
      href: "/dossier-express",
      accent: true,
    },
    {
      icon: Brain,
      title: "StratégiIA",
      price: "Gratuit",
      desc: "Pré-analyse assistée par intelligence artificielle. Un premier diagnostic rapide et confidentiel de votre situation.",
      href: "/simulateur",
      accent: false,
    },
    {
      icon: Shield,
      title: "Accompagnement stratégique complet",
      price: "Sur devis",
      desc: "Suivi global de vos démarches : analyse, préparation, orientation, expertise et contestation si nécessaire.",
      href: "/contact",
      accent: false,
    },
  ];

  const confiance = [
    { icon: HeartHandshake, title: "Expertise terrain réelle", desc: "Née d'une expérience personnelle face aux mêmes épreuves que les vôtres." },
    { icon: Stethoscope, title: "Compréhension des enjeux médicaux et professionnels", desc: "Maîtrise des tableaux de maladies professionnelles, des barèmes et des procédures." },
    { icon: Award, title: "Approche stratégique unique", desc: "Chaque dossier est traité comme un cas à part, avec une stratégie sur mesure." },
    { icon: TrendingUp, title: "Vision orientée résultats", desc: "L'objectif est clair : obtenir la reconnaissance et l'indemnisation que vous méritez." },
  ];

  const chiffresCles = [
    { icon: HardHat, value: 700000, unit: '', prefix: "Plus de", suffix: "accidents du travail par an en France", source: "CNAM", lien: "https://assurance-maladie.ameli.fr" },
    { icon: Activity, value: 50000, unit: '', prefix: "Environ", suffix: "maladies professionnelles reconnues chaque année", source: "CNAM", lien: "https://assurance-maladie.ameli.fr" },
    { icon: Accessibility, value: 12, unit: ' millions', prefix: "Près de", suffix: "de personnes en situation de handicap", source: "INSEE", lien: "https://www.insee.fr" },
    { icon: ClipboardList, value: 300000, unit: '', prefix: "Plus de", suffix: "nouvelles demandes MDPH chaque année", source: "CNSA", lien: "https://www.cnsa.fr" },
  ];

  return (
    <main className="page-transition">
      <SEO
        title="Accueil"
        description="Stratégie & Expertise Santé : accompagnement expert en maladie professionnelle, accident du travail, MDPH et protection juridique. Premier échange gratuit."
        path="/"
      />

      {/* ══════════════════════════════════════════════════════════
          HERO — Premium sombre, lisible, haut de gamme
      ══════════════════════════════════════════════════════════ */}
      <section className="relative min-h-screen flex items-center pt-20" data-testid="hero-section">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1598016677484-ad34c3fd766e?auto=format&fit=crop&w=1920&q=60')" }}
        />
        <div className="absolute inset-0 bg-black/55" />

        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32 text-center">
          {/* Badge — Valorisé */}
          <div className="inline-flex items-center gap-2.5 bg-[#C9A84C]/15 backdrop-blur-sm border border-[#C9A84C]/30 text-[#C9A84C] px-5 py-2.5 rounded-full mb-10" data-testid="pioneer-badge">
            <Award className="w-4 h-4" />
            <span className="text-xs font-bold uppercase tracking-[0.18em]">Pionnier en France</span>
          </div>

          {/* Titre */}
          <h1
            className="text-3xl sm:text-4xl md:text-5xl font-semibold text-white leading-[1.15] mb-6 max-w-3xl mx-auto"
            style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
            data-testid="hero-title"
          >
            Vous n'êtes plus seul face à votre{' '}<span className="text-[#C9A84C]">accident du travail</span>{' '}ou votre{' '}<span className="text-[#C9A84C]">maladie professionnelle</span>
          </h1>

          {/* Sous-titre */}
          <p className="text-base sm:text-lg text-white/75 leading-relaxed max-w-2xl mx-auto mb-10" data-testid="hero-subtitle">
            Maximisez vos droits et évitez des pertes de plusieurs milliers d'euros
          </p>

          {/* 3 points clés */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-8 mb-12">
            <div className="flex items-center gap-2.5 text-white/60 text-sm">
              <CheckCircle className="w-4 h-4 text-[#C9A84C]" />
              <span>Accompagnement stratégique personnalisé</span>
            </div>
            <div className="flex items-center gap-2.5 text-white/60 text-sm">
              <CheckCircle className="w-4 h-4 text-[#C9A84C]" />
              <span>Expertise AT/MP et régimes spéciaux</span>
            </div>
            <div className="flex items-center gap-2.5 text-white/60 text-sm">
              <CheckCircle className="w-4 h-4 text-[#C9A84C]" />
              <span>Analyse assistée par intelligence artificielle</span>
            </div>
          </div>

          {/* Boutons — Hiérarchie visuelle renforcée */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10">
            <Link to="/contact">
              <Button
                size="lg"
                className="rounded-full px-10 py-6 gap-2.5 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-bold text-base shadow-xl shadow-[#C9A84C]/25 transition-all hover:shadow-[#C9A84C]/40 hover:scale-[1.02]"
                data-testid="hero-cta-primary"
              >
                <Phone className="w-5 h-5" />
                Être accompagné maintenant
              </Button>
            </Link>
            <Link to="/simulateur">
              <Button
                variant="outline"
                size="lg"
                className="rounded-full px-10 py-6 gap-2.5 border-white/20 text-white/90 hover:bg-white/10 hover:border-white/30 text-base transition-all"
                data-testid="hero-cta-secondary"
              >
                Analyser ma situation avec StratégiIA
              </Button>
            </Link>
          </div>

          {/* Compteur visiteurs */}
          {visitorCount > 0 && (
            <div className="inline-flex items-center gap-2 text-xs text-white/35">
              <Eye className="w-3.5 h-3.5" />
              <span><strong className="text-white/55">{visitorCount.toLocaleString('fr-FR')}</strong> visiteurs nous ont fait confiance</span>
            </div>
          )}
        </div>

      </section>

      {/* ══════════════════════════════════════════════════════════
          DOSSIER EXPRESS — Urgence Banner
      ══════════════════════════════════════════════════════════ */}
      <section className="relative overflow-hidden urgent-glow" data-testid="dossier-express-banner">
        <div className="absolute inset-0 bg-gradient-to-r from-red-700 via-red-600 to-red-700" />
        <div className="absolute inset-0 shimmer" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-white/15 backdrop-blur-sm rounded-xl flex items-center justify-center float">
                <Zap className="w-7 h-7 text-yellow-300" />
              </div>
              <div className="text-white">
                <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                  <span className="text-xs font-bold uppercase tracking-wider text-yellow-300 bg-yellow-300/15 px-2 py-0.5 rounded">Urgence</span>
                  <Clock className="w-3.5 h-3.5 text-red-200" />
                  <span className="text-xs text-red-200">Livré sous 2h</span>
                  {dossierCount > 0 && (
                    <span className="text-xs text-red-100 bg-white/10 px-2 py-0.5 rounded-full" data-testid="dossier-express-counter">
                      <strong className="text-yellow-300 count-pulse inline-block">{dossierCount}</strong> dossiers traités cette semaine
                    </span>
                  )}
                </div>
                <p className="font-bold text-base sm:text-lg leading-tight">
                  Expertise médicale imminente ? Dossier bloqué ?
                </p>
                <p className="text-sm text-red-100 font-medium">
                  Obtenez votre rapport d'analyse complet en 2h, préparé avec l'aide de StratégiIA — <span className="text-yellow-300 font-bold text-base">97€</span>
                </p>
              </div>
            </div>
            <Link to="/dossier-express" className="flex-shrink-0">
              <Button
                size="lg"
                className="bg-white text-red-700 hover:bg-yellow-50 font-bold rounded-full px-8 gap-2 shadow-xl hover:shadow-2xl transition-all hover:scale-105"
                data-testid="dossier-express-banner-cta"
              >
                <Zap className="w-4 h-4" />
                Accéder au Dossier Express IA
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ── Conseil du jour — Mobile (dans le flux) ── */}
      <div className="md:hidden px-4 py-4 bg-background">
        <MascotteMobileWidget />
      </div>

      {/* ══════════════════════════════════════════════════════════
          SECTION RISQUES
      ══════════════════════════════════════════════════════════ */}
      <section className="section-padding bg-card" data-testid="risques-section">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8" ref={risquesRef}>
          <div className="text-center mb-12 reveal">
            <AlertTriangle className="w-8 h-8 text-amber-600 mx-auto mb-4" />
            <h2 className="text-xl sm:text-2xl md:text-3xl font-semibold mb-3">
              Ce que vous risquez sans accompagnement
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 gap-4 sm:gap-5 mb-12 stagger">
            {risques.map((r, i) => (
              <div
                key={i}
                className="flex items-start gap-4 p-5 rounded-xl border border-amber-200/40 bg-amber-50/30 reveal"
                data-testid={`risque-${i}`}
              >
                <div className="w-10 h-10 rounded-lg bg-amber-100/60 flex items-center justify-center flex-shrink-0">
                  <r.icon className="w-5 h-5 text-amber-700" />
                </div>
                <p className="text-foreground/80 text-sm leading-relaxed font-medium pt-1.5">{r.text}</p>
              </div>
            ))}
          </div>

          <div className="text-center reveal">
            <p
              className="text-base sm:text-lg text-accent font-medium italic max-w-2xl mx-auto mb-8"
              style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
              data-testid="risques-accroche"
            >
              Une mauvaise décision aujourd'hui peut vous coûter des milliers d'euros demain.
            </p>
            <Link to="/contact">
              <Button
                size="lg"
                className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
                data-testid="risques-cta"
              >
                <Phone className="w-4 h-4" />
                Être accompagné dès maintenant
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          SECTION MÉTHODE S.E.S
      ══════════════════════════════════════════════════════════ */}
      <section className="section-padding bg-background" data-testid="methode-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" ref={methodeRef}>
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-sm font-medium text-accent uppercase tracking-[0.15em]">Notre approche</span>
            <h2 className="text-xl sm:text-2xl md:text-3xl font-semibold mt-2 mb-4">
              La Méthode <span className="text-accent">S.E.S</span>
            </h2>
            <p className="text-muted-foreground">
              Une méthodologie structurée et éprouvée pour défendre efficacement vos intérêts
              à chaque étape de votre parcours.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-5 stagger">
            {methodeSES.map((m, i) => (
              <div
                key={i}
                className="relative group reveal"
                data-testid={`methode-step-${i}`}
              >
                <div className="h-full bg-card rounded-2xl p-6 border border-border hover:border-accent/30 transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-lg">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-3xl font-bold text-accent/15">{m.num}</span>
                    <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center">
                      <m.icon className="w-4.5 h-4.5 text-accent" />
                    </div>
                  </div>
                  <h3 className="font-semibold text-sm mb-2 leading-snug">{m.title}</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">{m.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          SECTION SOLUTIONS
      ══════════════════════════════════════════════════════════ */}
      <section className="section-padding bg-secondary" data-testid="solutions-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" ref={solutionsRef}>
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-sm font-medium text-accent uppercase tracking-[0.15em]">Nos solutions</span>
            <h2 className="text-xl sm:text-2xl md:text-3xl font-semibold mt-2 mb-4">
              Choisissez l'accompagnement adapté à votre situation
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-6 stagger">
            {solutions.map((s, i) => (
              <Link key={i} to={s.href} className="group reveal" data-testid={`solution-card-${i}`}>
                <Card className={`h-full border-border hover:border-accent/40 transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-xl ${s.accent ? 'ring-2 ring-accent/30 relative' : ''}`}>
                  {s.accent && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <span className="bg-red-600 text-white text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-full">
                        Urgence
                      </span>
                    </div>
                  )}
                  <CardContent className="p-8">
                    <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-5">
                      <s.icon className="w-6 h-6 text-accent" />
                    </div>
                    <h3 className="text-xl font-semibold mb-1">{s.title}</h3>
                    <p className="text-accent font-bold text-lg mb-4">{s.price}</p>
                    <p className="text-sm text-muted-foreground leading-relaxed mb-6">{s.desc}</p>
                    <span className="inline-flex items-center gap-1.5 text-sm font-medium text-accent group-hover:gap-2.5 transition-all">
                      Découvrir <ArrowRight className="w-4 h-4" />
                    </span>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          CHIFFRES CLÉS
      ══════════════════════════════════════════════════════════ */}
      <section className="section-padding bg-background" data-testid="chiffres-section" id="chiffres">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" ref={chiffresRef}>
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Contexte national</span>
            <h2 className="text-xl sm:text-2xl md:text-3xl font-semibold mt-2 mb-4">Le défi en chiffres</h2>
            <p className="text-muted-foreground">
              Des millions de personnes sont concernées chaque année en France. Derrière ces chiffres, des parcours humains qui méritent un véritable accompagnement.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 stagger" ref={countSectionRef}>
            {chiffresCles.map((item, index) => (
              <div
                key={index}
                className="relative group reveal"
                data-testid={`chiffre-bloc-${index}`}
              >
                <div className="h-full bg-foreground text-primary-foreground rounded-2xl p-6 flex flex-col items-center text-center transition-transform duration-300 group-hover:-translate-y-1 group-hover:shadow-xl">
                  <div className="w-12 h-12 rounded-xl bg-accent/15 flex items-center justify-center mb-5">
                    <item.icon className="w-6 h-6 text-accent" strokeWidth={1.5} />
                  </div>
                  <p className="text-xs uppercase tracking-wider text-primary-foreground/50 mb-1">{item.prefix}</p>
                  <p className="text-3xl sm:text-4xl font-bold text-accent leading-tight mb-2" data-testid={`chiffre-value-${index}`}>
                    <CountUpNumber value={item.value} unit={item.unit} duration={1300} started={countStarted} />
                  </p>
                  <p className="text-sm text-primary-foreground/70 leading-relaxed flex-1 mb-4">{item.suffix}</p>
                  <a
                    href={item.lien}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-primary-foreground/40 hover:text-accent transition-colors"
                    data-testid={`chiffre-source-${index}`}
                  >
                    Source : {item.source} <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          SECTION CONFIANCE
      ══════════════════════════════════════════════════════════ */}
      <section className="section-padding bg-accent/5 border-y border-accent/10" data-testid="confiance-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" ref={confianceRef}>
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-sm font-medium text-accent uppercase tracking-[0.15em]">Crédibilité</span>
            <h2 className="text-xl sm:text-2xl md:text-3xl font-semibold mt-2 mb-4">
              Pourquoi nous faire confiance ?
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 stagger">
            {confiance.map((c, i) => (
              <div key={i} className="reveal" data-testid={`confiance-${i}`}>
                <div className="h-full p-6 rounded-2xl bg-card border border-border hover:border-accent/20 transition-all">
                  <div className="w-11 h-11 rounded-xl bg-accent/10 flex items-center justify-center mb-5">
                    <c.icon className="w-5 h-5 text-accent" />
                  </div>
                  <h3 className="font-semibold text-base mb-2">{c.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{c.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          FONDATEUR — Citation crédibilité
      ══════════════════════════════════════════════════════════ */}
      <section className="relative py-16 sm:py-20 overflow-hidden" data-testid="home-founder-quote">
        <div className="absolute inset-0 bg-[#0c0c0c]" />
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23D4AF37\' fill-opacity=\'1\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")' }} />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <span className="text-[#D4AF37] text-sm font-medium uppercase tracking-[0.2em]">Le mot du fondateur</span>
          </div>
          <div className="relative p-8 sm:p-10 rounded-2xl border border-[#D4AF37]/20 bg-[#0f0d08]/80 backdrop-blur-sm" data-testid="home-founder-card">
            <div className="absolute -top-4 left-8 w-8 h-8 flex items-center justify-center rounded-full bg-[#D4AF37] text-[#0c0c0c]">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983z"/></svg>
            </div>
            <blockquote data-testid="home-founder-blockquote">
              <p className="text-base sm:text-lg text-[#f5f0e8]/90 leading-relaxed italic text-center" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
                Fort de mon expérience personnelle et de mes succès obtenus face à de grands groupes d'assurance nationaux dans la reconnaissance de garanties PTIA et ITT, j'ai développé Stratégie & Expertise Santé pour accompagner toutes les personnes confrontées à ces démarches complexes.
              </p>
              <footer className="mt-5 flex items-center justify-center gap-3">
                <div className="w-6 h-px bg-[#D4AF37]/40" />
                <cite className="text-xs font-medium text-[#D4AF37]/80 not-italic tracking-widest uppercase">Fondateur</cite>
                <div className="w-6 h-px bg-[#D4AF37]/40" />
              </footer>
            </blockquote>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          MÉDECIN CONSEIL — Strategic section
      ══════════════════════════════════════════════════════════ */}
      <section className="section-padding bg-accent/5 border-y border-accent/10" data-testid="medecin-conseil-home-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="min-w-0">
              <span className="text-sm font-medium text-accent uppercase tracking-wider">Orientation stratégique</span>
              <h2 className="text-xl sm:text-2xl md:text-3xl font-semibold mt-2 mb-4" data-testid="home-medecin-conseil-title">
                Le choix du médecin conseil : un enjeu financier majeur
              </h2>
              <p className="text-muted-foreground mb-4 leading-relaxed">
                Un médecin conseil mal choisi peut entraîner une sous-évaluation de vos séquelles
                et une perte d'indemnisation de plusieurs dizaines de milliers d'euros.
              </p>
              <p className="text-muted-foreground mb-6 leading-relaxed">
                Nous vous orientons vers le professionnel le plus adapté à votre pathologie
                et à votre stratégie juridique.
              </p>
              <Link to="/medecin-conseil">
                <Button className="rounded-full px-5 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground whitespace-normal text-left h-auto py-2.5 text-sm" data-testid="home-medecin-conseil-cta">
                  <Stethoscope className="w-4 h-4 flex-shrink-0" />
                  <span>Être accompagné dans le choix de mon médecin conseil</span>
                  <ArrowRight className="w-4 h-4 flex-shrink-0" />
                </Button>
              </Link>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 min-w-0">
              <div className="bg-foreground text-primary-foreground p-5 rounded-xl">
                <p className="text-2xl sm:text-3xl font-bold text-accent mb-1">800 - 3 000 €</p>
                <p className="text-xs text-primary-foreground/60">Coût moyen d'un médecin conseil</p>
              </div>
              <div className="bg-foreground text-primary-foreground p-5 rounded-xl">
                <p className="text-2xl sm:text-3xl font-bold text-accent mb-1">x10</p>
                <p className="text-xs text-primary-foreground/60">Retour sur investissement potentiel</p>
              </div>
              <div className="sm:col-span-2 bg-foreground text-primary-foreground p-5 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0" />
                  <p className="font-semibold text-sm">Risque d'un mauvais choix</p>
                </div>
                <p className="text-xs text-primary-foreground/60 leading-relaxed">
                  Un taux d'IPP sous-évalué de quelques points peut représenter une perte de plusieurs dizaines de milliers d'euros sur votre indemnisation finale.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          TÉMOIGNAGES
      ══════════════════════════════════════════════════════════ */}
      <section className="relative py-16 sm:py-20 overflow-hidden" data-testid="testimonials-section">
        <div className="absolute inset-0 bg-[#0c0c0c]" />
        <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <span className="text-[#C9A84C] text-sm font-medium uppercase tracking-[0.2em]">Ils ont fait confiance</span>
            <h2 className="text-xl sm:text-2xl md:text-3xl font-semibold mt-3 text-[#f5f0e8]">
              Des parcours transformés
            </h2>
            <p className="text-[#f5f0e8]/40 mt-3 max-w-xl mx-auto text-sm">
              Témoignages anonymisés de personnes accompagnées par Stratégie & Expertise Santé.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { initials: "M.L.", age: "52 ans", badge: "AT", text: "Après 18 mois de refus par la CPAM, mon accident du travail a enfin été reconnu. Sans cet accompagnement, j'aurais abandonné les démarches.", result: "AT reconnue — Rente obtenue" },
              { initials: "P.D.", age: "45 ans", badge: "PTIA", badgeGold: true, text: "Mon assureur refusait de reconnaître ma PTIA malgré l'avis de trois médecins. Grâce à une stratégie méthodique, la garantie a été activée après 8 mois de recours.", result: "Garantie PTIA activée" },
              { initials: "S.B.", age: "38 ans", badge: "MP", text: "Ma maladie professionnelle n'était pas dans les tableaux. L'accompagnement m'a permis de constituer un dossier solide — reconnaissance obtenue au premier passage.", result: "MP hors tableau reconnue" },
              { initials: "C.R.", age: "61 ans", badge: "IPP", text: "Mon taux d'IPP avait été évalué à 5% alors que mes séquelles sont bien plus importantes. Après contestation, le taux a été réévalué à 23%.", result: "IPP réévaluée : 5% → 23%" },
              { initials: "A.M.", age: "34 ans", badge: "MDPH", text: "Mes demandes MDPH étaient systématiquement refusées. Grâce à un dossier structuré et des arguments adaptés, j'ai obtenu l'AAH en moins de 4 mois.", result: "AAH obtenue en 4 mois" },
              { initials: "J.T.", age: "48 ans", badge: "ITT", badgeGold: true, text: "Mon assurance refusait les indemnités ITT en invoquant une clause floue. L'analyse du contrat a permis de débloquer 14 mois d'arriérés.", result: "ITT versée — Arriérés récupérés" },
            ].map((t, i) => (
              <div
                key={i}
                className={`p-5 rounded-xl border ${t.badgeGold ? 'border-[#C9A84C]/30 bg-[#C9A84C]/5' : 'border-white/5 bg-white/[0.02]'} hover:border-[#C9A84C]/20 transition-all`}
                data-testid={`testimonial-${i}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2.5">
                    <div className="w-9 h-9 rounded-full bg-[#C9A84C]/10 border border-[#C9A84C]/20 flex items-center justify-center">
                      <span className="text-[#C9A84C] text-xs font-bold">{t.initials}</span>
                    </div>
                    <div>
                      <span className="text-[#f5f0e8] text-sm font-medium">{t.initials}</span>
                      <span className="text-[#f5f0e8]/30 text-xs ml-1.5">{t.age}</span>
                    </div>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${t.badgeGold ? 'bg-[#C9A84C] text-[#1a1a1a]' : 'bg-white/10 text-[#f5f0e8]/60'}`}>
                    {t.badge}
                  </span>
                </div>
                <p className="text-[#f5f0e8]/60 text-sm leading-relaxed mb-3">{t.text}</p>
                <div className="flex items-center gap-2 pt-2 border-t border-white/5">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
                  <span className="text-emerald-400 text-xs font-medium">{t.result}</span>
                </div>
              </div>
            ))}
          </div>
          <p className="text-center text-[#f5f0e8]/20 text-[10px] mt-8">
            * Prénoms et détails modifiés pour préserver l'anonymat. Résultats réels obtenus pour nos clients.
          </p>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          DISCLAIMER
      ══════════════════════════════════════════════════════════ */}
      <section className="py-8 bg-amber-50/50 border-y border-amber-200/30">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-start gap-3" data-testid="homepage-disclaimer">
            <Scale className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
            <div className="text-sm text-amber-900/70 leading-relaxed space-y-2">
              <p>
                <strong className="text-amber-900/90">Information importante :</strong> Stratégie & Expertise Santé propose un accompagnement stratégique et une analyse documentaire.
                Ce service ne constitue pas une expertise médicale officielle ni une expertise judiciaire.
              </p>
              <p>
                Les services proposés ne constituent pas un conseil juridique ni un avis médical.
                Pour toute décision juridique ou médicale, consultez un professionnel qualifié.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          CTA FINAL
      ══════════════════════════════════════════════════════════ */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center reveal" ref={ctaRef}>
          <h2 className="text-xl sm:text-2xl md:text-3xl font-semibold mb-6">
            Besoin d'aide pour y voir plus clair ?
          </h2>
          <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
            Chaque situation est unique. Contactez-moi pour un premier échange gratuit
            et sans engagement. Ensemble, nous verrons comment je peux vous accompagner.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/contact">
              <Button
                size="lg"
                className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
                data-testid="cta-contact-button"
              >
                <Phone className="w-4 h-4" />
                Me contacter
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <Link to="/simulateur">
              <Button
                variant="outline"
                size="lg"
                className="rounded-full px-8 gap-2 border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/5"
                data-testid="cta-simulateur-button"
              >
                Analyser avec StratégiIA
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
};
