import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Phone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { LogoFull } from '@/components/Logo';

export const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const navItems = [
    { name: 'À propos', href: '/a-propos' },
    { name: 'Accompagnements', href: '/accompagnements' },
    { name: 'StratégiIA', href: '/simulateur' },
    { name: 'Tarifs', href: '/tarifs' },
  ];

  const isActive = (path) => location.pathname === path;

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

          {/* Desktop Navigation — Center */}
          <div className="hidden lg:flex items-center gap-1 ml-12">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`px-4 py-2 text-[13px] font-medium rounded-md transition-all duration-200 ${
                  isActive(item.href)
                    ? 'text-[#C9A84C]'
                    : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8]'
                }`}
                data-testid={`nav-${item.name.toLowerCase().replace(/[\s\/]+/g, '-')}`}
              >
                {item.name}
              </Link>
            ))}
          </div>

          {/* Right side — CTA */}
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

          {/* Mobile Menu Button */}
          <button
            className="lg:hidden p-2 text-[#f5f0e8] hover:text-[#C9A84C] transition-colors"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            data-testid="mobile-menu-button"
            aria-label={isMenuOpen ? 'Fermer le menu' : 'Ouvrir le menu'}
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="lg:hidden border-t border-[#C9A84C]/10 max-h-[80vh] overflow-y-auto">
            <div className="flex flex-col py-3">
              <Link
                to="/"
                className={`px-4 py-3 text-sm font-medium transition-colors ${
                  isActive('/') ? 'text-[#C9A84C] bg-[#C9A84C]/5' : 'text-[#f5f0e8]/70 hover:text-[#f5f0e8] hover:bg-white/5'
                }`}
                onClick={() => setIsMenuOpen(false)}
                data-testid="mobile-nav-accueil"
              >
                Accueil
              </Link>
              {navItems.map((item) => (
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
              ))}

              {/* Mobile CTA */}
              <div className="px-4 pt-4 pb-2 border-t border-[#C9A84C]/10 mt-2">
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
