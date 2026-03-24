import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, ChevronDown, Zap, Phone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GlobalSearch } from '@/components/GlobalSearch';
import { StrategiIA } from '@/components/StrategiIA';
import { LogoFull } from '@/components/Logo';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const expertiseItems = [
    { name: 'Accompagnements', href: '/accompagnements' },
    { name: 'Protection juridique', href: '/protection-juridique' },
    { name: 'Expertise médicale', href: '/expertise-medicale' },
    { name: 'Médecin conseil', href: '/medecin-conseil' },
    { name: 'AT / MP', href: '/accident-travail-maladie-professionnelle' },
    { name: 'MDPH', href: '/mdph' },
  ];

  const outilsItems = [
    { name: 'Simulateur StratégiIA', href: '/simulateur' },
    { name: 'Calculatrice IPP', href: '/calculatrice-ipp' },
    { name: 'Calculatrice AAH', href: '/calculatrice-aah' },
    { name: 'Ressources', href: '/ressources' },
  ];

  const moreItems = [
    { name: 'Tarifs', href: '/tarifs' },
    { name: 'Séminaires', href: '/seminaires' },
    { name: 'Entreprises', href: '/entreprises' },
    { name: 'Partenaires', href: '/partenaires' },
    { name: 'Forum', href: '/forum' },
    { name: 'Avis', href: '/avis' },
  ];

  const mobileNavigation = [
    { name: 'Accueil', href: '/' },
    { name: 'À propos', href: '/a-propos' },
    { type: 'divider', label: 'Domaines' },
    ...expertiseItems,
    { type: 'divider', label: 'Outils' },
    ...outilsItems,
    { type: 'divider', label: 'Plus' },
    ...moreItems,
    { name: 'Contact', href: '/contact' },
    { name: 'Espace client', href: '/espace-client' },
  ];

  const isActive = (path) => location.pathname === path;
  const isDropdownActive = (items) => items.some(item => location.pathname === item.href);

  return (
    <header
      className={`fixed top-0 left-0 right-0 transition-all duration-300 ${
        scrolled
          ? 'bg-[#0a0a08]/95 backdrop-blur-md shadow-lg shadow-black/10'
          : 'bg-[#0a0a08]/80 backdrop-blur-sm'
      }`}
      style={{ zIndex: 'var(--z-header, 9999)' }}
      data-testid="header"
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-[68px]">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center gap-0 hover:opacity-90 transition-opacity flex-shrink-0"
            data-testid="header-logo"
          >
            <LogoFull className="h-10 w-auto" textColor="#f5f0e8" />
          </Link>

          {/* Desktop Navigation — Center */}
          <div className="hidden lg:flex items-center gap-1 ml-8">
            <Link
              to="/a-propos"
              className={`px-3 py-1.5 text-[13px] font-medium rounded-md transition-colors ${
                isActive('/a-propos')
                  ? 'text-[#C9A84C]'
                  : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8]'
              }`}
              data-testid="nav-a-propos"
            >
              À propos
            </Link>

            {/* Expertise Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  className={`flex items-center gap-1 px-3 py-1.5 text-[13px] font-medium rounded-md transition-colors ${
                    isDropdownActive(expertiseItems)
                      ? 'text-[#C9A84C]'
                      : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8]'
                  }`}
                  data-testid="nav-expertise-dropdown"
                >
                  Expertises
                  <ChevronDown className="w-3.5 h-3.5 opacity-50" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-52 bg-[#141410] border-[#C9A84C]/15 text-[#f5f0e8]">
                {expertiseItems.map((item) => (
                  <DropdownMenuItem key={item.name} asChild>
                    <Link
                      to={item.href}
                      className={`text-[13px] ${isActive(item.href) ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/80 hover:text-[#f5f0e8]'}`}
                      data-testid={`nav-${item.name.toLowerCase().replace(/[\s\/]+/g, '-')}`}
                    >
                      {item.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Outils Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  className={`flex items-center gap-1 px-3 py-1.5 text-[13px] font-medium rounded-md transition-colors ${
                    isDropdownActive(outilsItems)
                      ? 'text-[#C9A84C]'
                      : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8]'
                  }`}
                  data-testid="nav-outils-dropdown"
                >
                  Outils
                  <ChevronDown className="w-3.5 h-3.5 opacity-50" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-52 bg-[#141410] border-[#C9A84C]/15 text-[#f5f0e8]">
                {outilsItems.map((item) => (
                  <DropdownMenuItem key={item.name} asChild>
                    <Link
                      to={item.href}
                      className={`text-[13px] ${isActive(item.href) ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/80 hover:text-[#f5f0e8]'}`}
                      data-testid={`nav-${item.name.toLowerCase().replace(/[\s\/]+/g, '-')}`}
                    >
                      {item.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Plus Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  className={`flex items-center gap-1 px-3 py-1.5 text-[13px] font-medium rounded-md transition-colors ${
                    isDropdownActive(moreItems)
                      ? 'text-[#C9A84C]'
                      : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8]'
                  }`}
                  data-testid="nav-plus-dropdown"
                >
                  Plus
                  <ChevronDown className="w-3.5 h-3.5 opacity-50" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-48 bg-[#141410] border-[#C9A84C]/15 text-[#f5f0e8]">
                {moreItems.map((item) => (
                  <DropdownMenuItem key={item.name} asChild>
                    <Link
                      to={item.href}
                      className={`text-[13px] ${isActive(item.href) ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/80 hover:text-[#f5f0e8]'}`}
                      data-testid={`nav-${item.name.toLowerCase().replace(/[\s\/]+/g, '-')}`}
                    >
                      {item.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
                <DropdownMenuItem asChild>
                  <Link
                    to="/contact"
                    className={`text-[13px] ${isActive('/contact') ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/80 hover:text-[#f5f0e8]'}`}
                    data-testid="nav-contact"
                  >
                    Contact
                  </Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Right side — CTA area */}
          <StrategiIA />
          <div className="hidden lg:flex items-center gap-2 ml-auto">
            <GlobalSearch />
            <Link to="/dossier-express">
              <Button
                variant="ghost"
                size="sm"
                className="rounded-full px-3 gap-1.5 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 font-semibold whitespace-nowrap border border-red-500/20"
                data-testid="header-dossier-express-btn"
              >
                <Zap className="w-3.5 h-3.5" />
                Urgence 97€
              </Button>
            </Link>
            <Link to="/espace-client">
              <Button
                variant="ghost"
                size="sm"
                className="rounded-full px-3 text-xs text-[#f5f0e8]/60 hover:text-[#f5f0e8] whitespace-nowrap"
                data-testid="header-client-button"
              >
                Espace client
              </Button>
            </Link>
            <Link to="/agenda">
              <Button
                size="sm"
                className="rounded-full px-5 gap-1.5 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-semibold text-xs shadow-lg shadow-[#C9A84C]/20 transition-all hover:shadow-[#C9A84C]/30 hover:scale-[1.02]"
                data-testid="header-cta-button"
              >
                <Phone className="w-3.5 h-3.5" />
                Réserver un appel
              </Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center gap-2 lg:hidden">
            <GlobalSearch />
            <button
              className="p-2 text-[#f5f0e8] hover:text-[#C9A84C] transition-colors"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              data-testid="mobile-menu-button"
              aria-label={isMenuOpen ? 'Fermer le menu' : 'Ouvrir le menu'}
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="lg:hidden border-t border-[#C9A84C]/10 max-h-[80vh] overflow-y-auto">
            <div className="flex flex-col py-3">
              {mobileNavigation.map((item, idx) => {
                if (item.type === 'divider') {
                  return (
                    <div key={idx} className="px-4 pt-4 pb-1">
                      <span className="text-[10px] font-bold uppercase tracking-[0.15em] text-[#C9A84C]/50">{item.label}</span>
                    </div>
                  );
                }
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`px-4 py-3 text-sm font-medium transition-colors ${
                      isActive(item.href)
                        ? 'text-[#C9A84C] bg-[#C9A84C]/5'
                        : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8] hover:bg-white/5'
                    }`}
                    onClick={() => setIsMenuOpen(false)}
                    data-testid={`mobile-nav-${item.name.toLowerCase().replace(/[\s\/]+/g, '-')}`}
                  >
                    {item.name}
                  </Link>
                );
              })}

              {/* Mobile CTAs */}
              <div className="flex flex-col gap-2 px-4 pt-4 pb-2 border-t border-[#C9A84C]/10 mt-2">
                <Link to="/dossier-express" onClick={() => setIsMenuOpen(false)}>
                  <Button
                    variant="outline"
                    className="w-full rounded-full gap-2 text-red-400 border-red-500/30 hover:bg-red-500/10 text-sm"
                    data-testid="mobile-urgence-button"
                  >
                    <Zap className="w-4 h-4" />
                    Dossier Express — 97€
                  </Button>
                </Link>
                <Link to="/agenda" onClick={() => setIsMenuOpen(false)}>
                  <Button
                    className="w-full rounded-full bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-semibold gap-2 text-sm"
                    data-testid="mobile-cta-button"
                  >
                    <Phone className="w-4 h-4" />
                    Réserver un appel
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
};
