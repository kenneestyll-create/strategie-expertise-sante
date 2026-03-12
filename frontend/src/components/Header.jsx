import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: 'Accueil', href: '/' },
    { name: 'À propos', href: '/a-propos' },
    { name: 'Accompagnements', href: '/accompagnements' },
    { name: 'Expertise médicale', href: '/expertise-medicale' },
    { name: 'AT/MP', href: '/accident-travail-maladie-professionnelle' },
    { name: 'MDPH', href: '/mdph' },
    { name: 'Ressources', href: '/ressources' },
    { name: 'Contact', href: '/contact' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-20">
          {/* Logo */}
          <Link 
            to="/" 
            className="flex items-center gap-2 text-foreground hover:opacity-80 transition-opacity"
            data-testid="header-logo"
          >
            <Heart className="w-6 h-6 text-accent" strokeWidth={1.5} />
            <span className="font-semibold text-lg tracking-tight" style={{ fontFamily: "'Playfair Display', serif" }}>
              Accompagn'Santé
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center gap-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`link-underline text-sm font-medium transition-colors ${
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

          {/* CTA Button - Desktop */}
          <div className="hidden lg:block">
            <Link to="/contact">
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
          <div className="lg:hidden py-4 border-t border-border">
            <div className="flex flex-col gap-4">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`px-2 py-2 text-base font-medium transition-colors ${
                    isActive(item.href) 
                      ? 'text-foreground' 
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                  data-testid={`mobile-nav-${item.name.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  {item.name}
                </Link>
              ))}
              <Link to="/contact" onClick={() => setIsMenuOpen(false)}>
                <Button className="w-full rounded-full mt-2" data-testid="mobile-cta-button">
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
