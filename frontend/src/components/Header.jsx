import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, ChevronDown, Phone, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
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
  const [mobileOpen, setMobileOpen] = useState(null); // track which mobile section is open
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    setIsMenuOpen(false);
    setMobileOpen(null);
  }, [location.pathname]);

  const accompagnementsItems = [
    { name: 'Accompagnements', href: '/accompagnements' },
    { name: 'Protection juridique', href: '/protection-juridique' },
    { name: 'Expertise médicale', href: '/expertise-medicale' },
    { name: 'Médecin conseil', href: '/medecin-conseil' },
    { name: 'AT / MP', href: '/accident-travail-maladie-professionnelle' },
    { name: 'MDPH', href: '/mdph' },
  ];

  const outilsItems = [
    { name: 'Calculatrice IPP', href: '/calculatrice-ipp' },
    { name: 'Calculatrice AAH', href: '/calculatrice-aah' },
    { name: 'Ressources', href: '/ressources' },
    { name: 'Forum', href: '/forum' },
    { name: 'Avis', href: '/avis' },
    { name: 'Séminaires', href: '/seminaires' },
    { name: 'Entreprises', href: '/entreprises' },
    { name: 'Partenaires', href: '/partenaires' },
    { name: 'Contact', href: '/contact' },
    { name: 'Espace client', href: '/espace-client' },
  ];

  const isActive = (path) => location.pathname === path;
  const isDropdownActive = (items) => items.some(item => location.pathname === item.href);

  const navLinkClass = (active) =>
    `px-3 py-2 text-[13px] font-medium rounded-md transition-all duration-200 ${
      active ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8]'
    }`;

  const dropdownBtnClass = (active) =>
    `flex items-center gap-1 px-3 py-2 text-[13px] font-medium rounded-md transition-all duration-200 ${
      active ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8]'
    }`;

  const mobileToggle = (section) =>
    setMobileOpen(prev => prev === section ? null : section);

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
            className="flex items-center hover:opacity-90 transition-opacity flex-shrink-0"
            data-testid="header-logo"
          >
            <LogoFull className="h-10 w-auto" textColor="#f5f0e8" />
          </Link>

          {/* ═══ Desktop Navigation ═══ */}
          <div className="hidden lg:flex items-center gap-0.5 ml-8">
            {/* À propos */}
            <Link to="/a-propos" className={navLinkClass(isActive('/a-propos'))} data-testid="nav-a-propos">
              À propos
            </Link>

            {/* Accompagnements dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={dropdownBtnClass(isDropdownActive(accompagnementsItems))} data-testid="nav-accompagnements-dropdown">
                  Accompagnements <ChevronDown className="w-3.5 h-3.5 opacity-50" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-56 bg-[#141410] border-[#C9A84C]/15">
                {accompagnementsItems.map((item) => (
                  <DropdownMenuItem key={item.href} asChild>
                    <Link
                      to={item.href}
                      className={`text-[13px] cursor-pointer ${isActive(item.href) ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/80 hover:text-[#f5f0e8]'}`}
                      data-testid={`nav-${item.name.toLowerCase().replace(/[\s\/]+/g, '-')}`}
                    >
                      {item.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Outils dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={dropdownBtnClass(isDropdownActive(outilsItems))} data-testid="nav-outils-dropdown">
                  Outils <ChevronDown className="w-3.5 h-3.5 opacity-50" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-52 bg-[#141410] border-[#C9A84C]/15">
                {outilsItems.map((item) => (
                  <DropdownMenuItem key={item.href} asChild>
                    <Link
                      to={item.href}
                      className={`text-[13px] cursor-pointer ${isActive(item.href) ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/80 hover:text-[#f5f0e8]'}`}
                      data-testid={`nav-${item.name.toLowerCase().replace(/[\s\/]+/g, '-')}`}
                    >
                      {item.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* StratégiIA */}
            <Link to="/simulateur" className={navLinkClass(isActive('/simulateur'))} data-testid="nav-strategiia">
              StratégiIA
            </Link>

            {/* Tarifs */}
            <Link to="/tarifs" className={navLinkClass(isActive('/tarifs'))} data-testid="nav-tarifs">
              Tarifs
            </Link>

            {/* Dossier Express IA */}
            <Link to="/dossier-express" className={navLinkClass(isActive('/dossier-express'))} data-testid="nav-dossier-express">
              <span className="flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-red-400" />
                Dossier Express IA
              </span>
            </Link>
          </div>

          {/* ═══ Right CTA ═══ */}
          <div className="hidden lg:flex items-center ml-auto">
            <Link to="/agenda">
              <Button
                size="sm"
                className="rounded-full px-6 gap-2 bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-semibold text-[13px] shadow-lg shadow-[#C9A84C]/20 transition-all hover:shadow-[#C9A84C]/30 hover:scale-[1.02]"
                data-testid="header-cta-button"
              >
                <Phone className="w-3.5 h-3.5" />
                Réserver un appel
              </Button>
            </Link>
          </div>

          {/* ═══ Mobile Menu Button ═══ */}
          <button
            className="lg:hidden p-2 text-[#f5f0e8] hover:text-[#C9A84C] transition-colors"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            data-testid="mobile-menu-button"
            aria-label={isMenuOpen ? 'Fermer le menu' : 'Ouvrir le menu'}
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* ═══ Mobile Navigation ═══ */}
        {isMenuOpen && (
          <div className="lg:hidden border-t border-[#C9A84C]/10 max-h-[85vh] overflow-y-auto" data-testid="mobile-menu">
            <div className="flex flex-col py-2">
              {/* Accueil */}
              <Link to="/" className={`px-4 py-3 text-sm font-medium ${isActive('/') ? 'text-[#C9A84C] bg-[#C9A84C]/5' : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8] hover:bg-white/5'}`} data-testid="mobile-nav-accueil">
                Accueil
              </Link>
              <Link to="/a-propos" className={`px-4 py-3 text-sm font-medium ${isActive('/a-propos') ? 'text-[#C9A84C] bg-[#C9A84C]/5' : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8] hover:bg-white/5'}`} data-testid="mobile-nav-a-propos">
                À propos
              </Link>

              {/* Accompagnements — collapsible */}
              <button
                onClick={() => mobileToggle('accompagnements')}
                className={`flex items-center justify-between px-4 py-3 text-sm font-medium w-full ${isDropdownActive(accompagnementsItems) ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/70'}`}
                data-testid="mobile-toggle-accompagnements"
              >
                Accompagnements
                <ChevronDown className={`w-4 h-4 transition-transform ${mobileOpen === 'accompagnements' ? 'rotate-180' : ''}`} />
              </button>
              {mobileOpen === 'accompagnements' && (
                <div className="bg-white/[0.02]">
                  {accompagnementsItems.map((item) => (
                    <Link
                      key={item.href}
                      to={item.href}
                      className={`block pl-8 pr-4 py-2.5 text-sm ${isActive(item.href) ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/60 hover:text-[#f5f0e8]'}`}
                      data-testid={`mobile-nav-${item.name.toLowerCase().replace(/[\s\/]+/g, '-')}`}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              )}

              {/* Outils — collapsible */}
              <button
                onClick={() => mobileToggle('outils')}
                className={`flex items-center justify-between px-4 py-3 text-sm font-medium w-full ${isDropdownActive(outilsItems) ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/70'}`}
                data-testid="mobile-toggle-outils"
              >
                Outils
                <ChevronDown className={`w-4 h-4 transition-transform ${mobileOpen === 'outils' ? 'rotate-180' : ''}`} />
              </button>
              {mobileOpen === 'outils' && (
                <div className="bg-white/[0.02]">
                  {outilsItems.map((item) => (
                    <Link
                      key={item.href}
                      to={item.href}
                      className={`block pl-8 pr-4 py-2.5 text-sm ${isActive(item.href) ? 'text-[#C9A84C]' : 'text-[#f5f0e8]/60 hover:text-[#f5f0e8]'}`}
                      data-testid={`mobile-nav-${item.name.toLowerCase().replace(/[\s\/]+/g, '-')}`}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              )}

              {/* Direct links */}
              <Link to="/simulateur" className={`px-4 py-3 text-sm font-medium ${isActive('/simulateur') ? 'text-[#C9A84C] bg-[#C9A84C]/5' : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8] hover:bg-white/5'}`} data-testid="mobile-nav-strategiia">
                StratégiIA
              </Link>
              <Link to="/tarifs" className={`px-4 py-3 text-sm font-medium ${isActive('/tarifs') ? 'text-[#C9A84C] bg-[#C9A84C]/5' : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8] hover:bg-white/5'}`} data-testid="mobile-nav-tarifs">
                Tarifs
              </Link>
              <Link to="/dossier-express" className={`px-4 py-3 text-sm font-medium flex items-center gap-1.5 ${isActive('/dossier-express') ? 'text-[#C9A84C] bg-[#C9A84C]/5' : 'text-red-400/80 hover:text-red-300 hover:bg-white/5'}`} data-testid="mobile-nav-dossier-express">
                <Zap className="w-3.5 h-3.5" />
                Dossier Express IA
              </Link>

              {/* Mobile CTA */}
              <div className="px-4 pt-4 pb-3 border-t border-[#C9A84C]/10 mt-2">
                <Link to="/agenda">
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
