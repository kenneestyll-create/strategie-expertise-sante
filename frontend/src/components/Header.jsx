import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Heart, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GlobalSearch } from '@/components/GlobalSearch';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const mainNavigation = [
    { name: 'Accueil', href: '/' },
    { name: 'À propos', href: '/a-propos' },
    { name: 'Accompagnements', href: '/accompagnements' },
    { name: 'Protection juridique', href: '/protection-juridique' },
  ];

  const expertiseItems = [
    { name: 'Expertise médicale', href: '/expertise-medicale' },
    { name: 'AT / MP', href: '/accident-travail-maladie-professionnelle' },
    { name: 'MDPH', href: '/mdph' },
  ];

  const servicesItems = [
    { name: 'Tarifs', href: '/tarifs' },
    { name: 'Séminaires', href: '/seminaires' },
    { name: 'Entreprises', href: '/entreprises' },
    { name: 'Partenaires', href: '/partenaires' },
    { name: 'Simulateur', href: '/simulateur' },
    { name: 'Calculatrice IPP', href: '/calculatrice-ipp' },
    { name: 'Calculatrice AAH', href: '/calculatrice-aah' },
    { name: 'Forum', href: '/forum' },
    { name: 'Avis', href: '/avis' },
    { name: 'Ressources', href: '/ressources' },
  ];

  const secondaryNavigation = [
    { name: 'Agenda', href: '/agenda' },
    { name: 'Contact', href: '/contact' },
  ];

  // All items for mobile menu
  const allNavigation = [
    { name: 'Accueil', href: '/' },
    { name: 'À propos', href: '/a-propos' },
    { name: 'Accompagnements', href: '/accompagnements' },
    { name: 'Protection juridique', href: '/protection-juridique' },
    { name: 'Expertise médicale', href: '/expertise-medicale' },
    { name: 'AT / MP', href: '/accident-travail-maladie-professionnelle' },
    { name: 'MDPH', href: '/mdph' },
    { name: 'Tarifs', href: '/tarifs' },
    { name: 'Séminaires', href: '/seminaires' },
    { name: 'Entreprises', href: '/entreprises' },
    { name: 'Partenaires', href: '/partenaires' },
    { name: 'Forum', href: '/forum' },
    { name: 'Avis', href: '/avis' },
    { name: 'Ressources', href: '/ressources' },
    { name: 'Simulateur', href: '/simulateur' },
    { name: 'Calculatrice IPP', href: '/calculatrice-ipp' },
    { name: 'Calculatrice AAH', href: '/calculatrice-aah' },
    { name: 'Agenda', href: '/agenda' },
    { name: 'Espace client', href: '/espace-client' },
    { name: 'Contact', href: '/contact' },
  ];

  const isActive = (path) => location.pathname === path;
  const isDropdownActive = (items) => items.some(item => location.pathname === item.href);

  return (
    <header className="fixed top-0 left-0 right-0 bg-background/80 backdrop-blur-md border-b border-border" style={{ zIndex: 'var(--z-header)' }}>
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-20">
          {/* Logo */}
          <Link 
            to="/" 
            className="flex items-center gap-2 text-foreground hover:opacity-80 transition-opacity"
            data-testid="header-logo"
          >
            <Heart className="w-6 h-6 text-accent flex-shrink-0" strokeWidth={1.5} />
            <span className="font-semibold text-base tracking-tight whitespace-nowrap" style={{ fontFamily: "'Playfair Display', serif" }}>
              Stratégie & Expertise Santé
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center gap-1">
            {/* Main navigation items */}
            {mainNavigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`px-3 py-2 text-sm font-medium transition-colors rounded-lg hover:bg-muted whitespace-nowrap ${
                  isActive(item.href) 
                    ? 'text-foreground' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
                data-testid={`nav-${item.name.toLowerCase().replace(/\s+/g, '-')}`}
              >
                {item.name}
              </Link>
            ))}

            {/* Expertise Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button 
                  className={`flex items-center gap-1 px-3 py-2 text-sm font-medium transition-colors rounded-lg hover:bg-muted ${
                    isDropdownActive(expertiseItems) 
                      ? 'text-foreground' 
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                  data-testid="nav-expertise-dropdown"
                >
                  Expertises
                  <ChevronDown className="w-4 h-4" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-56">
                {expertiseItems.map((item) => (
                  <DropdownMenuItem key={item.name} asChild>
                    <Link 
                      to={item.href}
                      className={isActive(item.href) ? 'bg-muted' : ''}
                      data-testid={`nav-${item.name.toLowerCase().replace(/[\s\/]+/g, '-')}`}
                    >
                      {item.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Services Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button 
                  className={`flex items-center gap-1 px-3 py-2 text-sm font-medium transition-colors rounded-lg hover:bg-muted ${
                    isDropdownActive(servicesItems) 
                      ? 'text-foreground' 
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                  data-testid="nav-services-dropdown"
                >
                  Services
                  <ChevronDown className="w-4 h-4" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-56">
                {servicesItems.map((item) => (
                  <DropdownMenuItem key={item.name} asChild>
                    <Link 
                      to={item.href}
                      className={isActive(item.href) ? 'bg-muted' : ''}
                      data-testid={`nav-${item.name.toLowerCase().replace(/\s+/g, '-')}`}
                    >
                      {item.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Secondary navigation items */}
            {secondaryNavigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`px-3 py-2 text-sm font-medium transition-colors rounded-lg hover:bg-muted whitespace-nowrap ${
                  isActive(item.href) 
                    ? 'text-foreground' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
                data-testid={`nav-${item.name.toLowerCase().replace(/\s+/g, '-')}`}
              >
                {item.name}
              </Link>
            ))}
          </div>

          {/* CTA Buttons - Desktop */}
          <div className="hidden lg:flex items-center gap-2">
            <GlobalSearch />
            <Link to="/espace-client">
              <Button 
                variant="outline"
                className="rounded-full px-4 text-sm"
                data-testid="header-client-button"
              >
                Espace client
              </Button>
            </Link>
            <Link to="/agenda">
              <Button 
                className="btn-scale rounded-full px-6"
                data-testid="header-cta-button"
              >
                Prendre rendez-vous
              </Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="lg:hidden p-2 text-foreground"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            data-testid="mobile-menu-button"
            aria-label={isMenuOpen ? 'Fermer le menu' : 'Ouvrir le menu'}
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="lg:hidden py-4 border-t border-border max-h-[70vh] overflow-y-auto">
            <div className="flex flex-col gap-1">
              {allNavigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`px-3 py-3 text-base font-medium transition-colors rounded-lg ${
                    isActive(item.href) 
                      ? 'text-foreground bg-muted' 
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                  data-testid={`mobile-nav-${item.name.toLowerCase().replace(/[\s\/]+/g, '-')}`}
                >
                  {item.name}
                </Link>
              ))}
              <Link to="/contact" onClick={() => setIsMenuOpen(false)}>
                <Button className="w-full rounded-full mt-4" data-testid="mobile-cta-button">
                  Prendre rendez-vous
                </Button>
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
};
