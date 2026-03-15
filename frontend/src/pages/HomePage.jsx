import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SEO } from '@/components/SEO';
import { useReveal, useRevealChildren } from '@/hooks/useReveal';
import { 
  ArrowRight, 
  FileSearch, 
  Shield, 
  Users, 
  BookOpen, 
  Heart, 
  CheckCircle, 
  Lightbulb,
  Sparkles,
  Stethoscope,
  Scale,
  Building2,
  Star,
  Train,
  Bus,
  Eye,
  Zap,
  Clock,
  HardHat,
  Activity,
  Accessibility,
  ClipboardList,
  ExternalLink
} from 'lucide-react';
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

  // Reveal refs for scroll animations
  const bannerRef = useReveal();
  const chiffresRef = useRevealChildren();
  const innovationRef = useRevealChildren();
  const missionRef = useRevealChildren();
  const servicesRef = useRevealChildren();
  const reseauRef = useRevealChildren();
  const avisRef = useReveal();
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

  const services = [
    {
      icon: FileSearch,
      title: "Analyse de dossier",
      description: "Étude approfondie de votre situation médicale, administrative et assurantielle."
    },
    {
      icon: Shield,
      title: "Préparation aux expertises",
      description: "Accompagnement personnalisé pour aborder sereinement vos expertises médicales."
    },
    {
      icon: Users,
      title: "Stratégie AT/MP",
      description: "Conseil sur les démarches de reconnaissance en maladie professionnelle."
    },
    {
      icon: BookOpen,
      title: "Aide assurantielle",
      description: "Décryptage de vos contrats et accompagnement dans vos relations avec les assureurs."
    }
  ];

  const values = [
    "Une écoute bienveillante et sans jugement",
    "Des conseils clairs, sans jargon",
    "Une expérience vécue de l'intérieur",
    "Un accompagnement à votre rythme"
  ];

  const innovationPoints = [
    "Un accompagnement humain personnalisé",
    "Des outils technologiques au service de votre dossier",
    "Une approche humaine et pédagogique",
    "Un service encore peu développé en France"
  ];

  const partenaires = [
    { icon: Stethoscope, title: "Médecins experts" },
    { icon: Scale, title: "Avocats spécialisés" },
    { icon: FileSearch, title: "Experts en assurance" },
    { icon: Building2, title: "Associations de victimes" }
  ];

  const regimesSpeciaux = [
    { icon: Train, name: "SNCF", description: "Cheminots et agents SNCF" },
    { icon: Bus, name: "RATP", description: "Agents RATP" }
  ];

  const chiffresCles = [
    {
      icon: HardHat,
      value: 700000,
      unit: '',
      prefix: "Plus de",
      suffix: "accidents du travail par an en France",
      source: "CNAM",
      lien: "https://assurance-maladie.ameli.fr"
    },
    {
      icon: Activity,
      value: 50000,
      unit: '',
      prefix: "Environ",
      suffix: "maladies professionnelles reconnues chaque année",
      source: "CNAM",
      lien: "https://assurance-maladie.ameli.fr"
    },
    {
      icon: Accessibility,
      value: 12,
      unit: ' millions',
      prefix: "Près de",
      suffix: "de personnes en situation de handicap",
      source: "INSEE",
      lien: "https://www.insee.fr"
    },
    {
      icon: ClipboardList,
      value: 300000,
      unit: '',
      prefix: "Plus de",
      suffix: "nouvelles demandes MDPH chaque année",
      source: "CNSA",
      lien: "https://www.cnsa.fr"
    }
  ];

  return (
    <main className="page-transition">
      <SEO
        title="Accueil"
        description="Stratégie & Expertise Santé : accompagnement expert en maladie professionnelle, accident du travail, MDPH et protection juridique. Premier échange gratuit."
        path="/"
      />
      <section className="relative min-h-screen flex items-center pt-20">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ 
            backgroundImage: `url('https://images.unsplash.com/photo-1598016677484-ad34c3fd766e?auto=format&fit=crop&w=1920&q=60')`,
          }}
        />
        <div className="absolute inset-0 hero-overlay" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="max-w-3xl">
            {/* Badge pionnier - mis en valeur */}
            <div className="inline-flex items-center gap-2.5 bg-foreground text-primary-foreground px-5 py-2.5 rounded-full mb-6 shadow-lg" data-testid="pioneer-badge">
              <Sparkles className="w-5 h-5 text-accent" />
              <span className="text-sm font-bold uppercase tracking-wider">Service pionnier en France</span>
            </div>
            
            <h1 
              className="text-4xl sm:text-5xl lg:text-6xl font-semibold text-foreground leading-tight mb-6"
              data-testid="hero-title"
            >
              Vous n'êtes plus seul face à la maladie professionnelle
            </h1>
            <p className="text-base sm:text-lg font-medium text-foreground mb-3 max-w-2xl bg-background/70 backdrop-blur-sm inline-block px-4 py-2 rounded-lg" data-testid="hero-tagline">
              Conseil stratégique en expertise médicale, invalidité et démarches médico-administratives.
            </p>
            <p className="text-base sm:text-lg text-muted-foreground mb-4 max-w-2xl">
              Un service innovant dédié à l'accompagnement des personnes confrontées à des démarches 
              complexes liées au handicap, aux expertises médicales et aux procédures d'assurance.
            </p>
            <p className="text-sm text-accent font-medium mb-8 max-w-2xl flex items-center gap-2" data-testid="hero-positioning">
              <Heart className="w-4 h-4 flex-shrink-0" strokeWidth={1.5} />
              Un accompagnement humain renforcé par l'intelligence artificielle : l'expertise humaine au c&oelig;ur de chaque dossier, l'IA comme outil de précision.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/contact">
                <Button 
                  size="lg" 
                  className="btn-scale rounded-full px-8 gap-2 bg-foreground hover:bg-foreground/90 text-primary-foreground"
                  data-testid="hero-cta-primary"
                >
                  Nous contacter
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Link to="/a-propos">
                <Button 
                  variant="outline" 
                  size="lg" 
                  className="rounded-full px-8"
                  data-testid="hero-cta-secondary"
                >
                  Mon parcours
                </Button>
              </Link>
            </div>

            {/* Visitor Counter */}
            {visitorCount > 0 && (
              <div className="mt-8 inline-flex items-center gap-2 text-sm text-muted-foreground bg-background/80 backdrop-blur-sm px-4 py-2 rounded-full">
                <Eye className="w-4 h-4 text-accent" />
                <span><strong className="text-foreground">{visitorCount.toLocaleString('fr-FR')}</strong> visiteurs nous ont fait confiance</span>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Dossier Express — Urgent Banner */}
      <section className="relative overflow-hidden urgent-glow" data-testid="dossier-express-banner" ref={bannerRef}>
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
                Accéder au Dossier Express
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Régimes Spéciaux Section */}
      <section className="py-8 bg-foreground text-primary-foreground">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-center gap-6 md:gap-12">
            <p className="text-sm font-medium text-primary-foreground/70">
              Accompagnement spécialisé régimes spéciaux :
            </p>
            <div className="flex items-center gap-6">
              {regimesSpeciaux.map((regime, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center">
                    <regime.icon className="w-5 h-5 text-accent-foreground" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="font-semibold text-sm">{regime.name}</p>
                    <p className="text-xs text-primary-foreground/60">{regime.description}</p>
                  </div>
                </div>
              ))}
            </div>
            <Link to="/accompagnements#regimes-speciaux">
              <Button variant="secondary" size="sm" className="rounded-full gap-1">
                En savoir plus
                <ArrowRight className="w-3 h-3" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Le défi en chiffres */}
      <section className="section-padding bg-background" data-testid="chiffres-section" id="chiffres">
        <div className="max-w-7xl mx-auto" ref={chiffresRef}>
          <div className="text-center max-w-2xl mx-auto mb-14 reveal">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Contexte national</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">Le défi en chiffres</h2>
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

          <p className="text-center mt-12 text-muted-foreground italic max-w-2xl mx-auto reveal" style={{ fontFamily: "'Playfair Display', serif" }} data-testid="chiffres-impact-phrase">
            Derrière chaque chiffre, une personne confrontée à un parcours administratif complexe.
          </p>
        </div>
      </section>

      {/* Approche Innovante Section */}
      <section className="section-padding bg-accent/5">
        <div className="max-w-7xl mx-auto" ref={innovationRef}>
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="reveal-left">
              <div className="inline-flex items-center gap-2 text-accent mb-4">
                <Lightbulb className="w-5 h-5" strokeWidth={1.5} />
                <span className="text-sm font-medium uppercase tracking-wider">Innovation</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
                Une approche innovante
              </h2>
              <p className="text-muted-foreground mb-6">
                Ce service repose sur une approche encore peu développée en France : 
                <strong> l'accompagnement humain stratégique et pédagogique</strong> des personnes 
                confrontées à des procédures médicales, administratives ou assurantielles complexes, 
                renforcé par des outils d'aide à l'analyse comme StratégiIA.
              </p>
              <p className="text-muted-foreground mb-8">
                L'objectif est de permettre aux personnes concernées de mieux comprendre leur 
                situation, leurs droits et les étapes importantes de leur parcours. L'expertise humaine 
                reste au c&oelig;ur de chaque dossier, l'intelligence artificielle servant d'outil de précision 
                pour renforcer la qualité de l'accompagnement.
              </p>
              <div className="grid sm:grid-cols-2 gap-3">
                {innovationPoints.map((point, index) => (
                  <div key={index} className="flex items-start gap-2 icon-bounce">
                    <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    <span className="text-sm text-foreground">{point}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative reveal-right">
              <div className="aspect-square rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/7176026/pexels-photo-7176026.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Approche innovante en accompagnement santé au travail"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="absolute -bottom-4 -right-4 bg-foreground text-primary-foreground p-4 rounded-xl shadow-lg reveal-scale">
                <p className="text-2xl font-bold">+7 ans</p>
                <p className="text-sm text-primary-foreground/70">d'expérience terrain</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="section-padding bg-card">
        <div className="max-w-7xl mx-auto" ref={missionRef}>
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            <div className="reveal-left">
              <span className="text-sm font-medium text-accent uppercase tracking-wider">Notre mission</span>
              <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-6">
                Comprendre, accompagner, défendre vos droits
              </h2>
              <p className="text-muted-foreground mb-6">
                Quand la maladie ou l'accident survient dans le cadre professionnel, le parcours administratif 
                peut sembler insurmontable. Entre les formulaires, les expertises, les délais et le jargon technique, 
                beaucoup abandonnent leurs droits.
              </p>
              <p className="text-muted-foreground mb-8">
                <strong>Stratégie & Expertise Santé</strong> est né de cette réalité vécue. Mon rôle : vous aider à comprendre 
                chaque étape, à préparer vos dossiers et à défendre vos intérêts face aux organismes et assureurs.
              </p>
              <div className="space-y-3">
                {values.map((value, index) => (
                  <div key={index} className="flex items-start gap-3 icon-bounce">
                    <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    <span className="text-foreground">{value}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative reveal-right">
              <div className="aspect-[4/5] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/7111462/pexels-photo-7111462.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Accompagnement personnalisé en maladie professionnelle"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="absolute -bottom-6 -left-6 bg-accent text-accent-foreground p-6 rounded-xl shadow-lg max-w-xs reveal-scale">
                <Heart className="w-8 h-8 mb-2" strokeWidth={1.5} />
                <p className="text-sm font-medium">
                  "Une personne blessée par le système qui aide d'autres blessés à se relever."
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Preview */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto" ref={servicesRef}>
          <div className="text-center max-w-2xl mx-auto mb-12 reveal">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Accompagnements</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">
              Comment puis-je vous aider ?
            </h2>
            <p className="text-muted-foreground">
              Des services adaptés à votre situation, pour vous guider pas à pas dans vos démarches.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 stagger">
            {services.map((service, index) => (
              <Card 
                key={index} 
                className="card-glow border-border bg-card reveal"
                data-testid={`service-card-${index}`}
              >
                <CardContent className="p-6 icon-bounce">
                  <service.icon className="w-10 h-10 text-accent mb-4" strokeWidth={1.5} />
                  <h3 className="font-semibold text-lg mb-2">{service.title}</h3>
                  <p className="text-sm text-muted-foreground">{service.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="text-center mt-10 reveal">
            <Link to="/accompagnements">
              <Button variant="outline" className="rounded-full px-8 gap-2 btn-scale" data-testid="services-link">
                Découvrir tous les accompagnements
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Réseau Partenaires Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto" ref={reseauRef}>
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="reveal-left">
              <span className="text-sm font-medium text-accent uppercase tracking-wider">Réseau</span>
              <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-6">
                Un réseau de professionnels partenaires
              </h2>
              <p className="text-muted-foreground mb-6">
                Au cours de mon parcours, j'ai collaboré avec de nombreux professionnels de santé 
                et du domaine judiciaire. Ce réseau me permet aujourd'hui de vous orienter vers 
                les interlocuteurs les plus adaptés à votre situation.
              </p>
              <div className="grid grid-cols-2 gap-4 mb-8 stagger">
                {partenaires.map((item, index) => (
                  <div key={index} className="flex items-center gap-3 bg-card p-4 rounded-xl border border-border card-glow reveal icon-bounce">
                    <item.icon className="w-6 h-6 text-accent" strokeWidth={1.5} />
                    <span className="text-sm font-medium">{item.title}</span>
                  </div>
                ))}
              </div>
              <Link to="/partenaires">
                <Button variant="outline" className="rounded-full px-6 gap-2">
                  Découvrir le réseau
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
            <div className="relative reveal-right">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                <img
                  loading="lazy" 
                  src="https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&w=800" 
                  alt="Réseau de professionnels partenaires santé et juridique"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Avis Section Preview */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto text-center reveal" ref={avisRef}>
          <Star className="w-12 h-12 text-accent mx-auto mb-4 float" strokeWidth={1.5} />
          <h2 className="text-3xl font-semibold mb-4">Ce qu'ils en disent</h2>
          <p className="text-muted-foreground mb-8">
            Découvrez les témoignages des personnes que j'ai accompagnées.
          </p>
          <Link to="/avis">
            <Button variant="outline" className="rounded-full px-8 gap-2">
              Voir les témoignages
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Disclaimer Section */}
      <section className="py-8 bg-amber-50/50 border-y border-amber-200/30">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-start gap-3" data-testid="homepage-disclaimer">
            <Scale className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
            <div className="text-sm text-amber-900/70 leading-relaxed space-y-2">
              <p>
                <strong className="text-amber-900/90">Information importante :</strong> Stratégie & Expertise Santé propose un accompagnement stratégique et une analyse documentaire. 
                Ce service ne constitue pas une expertise médicale officielle ni une expertise judiciaire, 
                lesquelles sont réalisées par des médecins experts et experts judiciaires agréés.
              </p>
              <p>
                Les services proposés ne constituent pas un conseil juridique ni un avis médical. 
                Pour toute décision juridique ou médicale, consultez un professionnel qualifié.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center reveal" ref={ctaRef}>
          <h2 className="text-3xl sm:text-4xl font-semibold mb-6">
            Besoin d'aide pour y voir plus clair ?
          </h2>
          <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
            Chaque situation est unique. Contactez-moi pour un premier échange gratuit 
            et sans engagement. Ensemble, nous verrons comment je peux vous accompagner.
          </p>
          <Link to="/contact">
            <Button 
              size="lg" 
              variant="secondary"
              className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="cta-contact-button"
            >
              Me contacter
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </main>
  );
};
