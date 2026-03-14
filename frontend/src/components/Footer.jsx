import { Link } from 'react-router-dom';
import { Mail, Phone, Gift } from 'lucide-react';

export const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-foreground text-primary-foreground">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center gap-0 mb-4">
              <img 
                src="/logo.svg" 
                alt="Stratégie & Expertise Santé — Pionnier en France" 
                className="h-10 w-auto"
                style={{ filter: 'brightness(0) invert(1)' }}
              />
            </Link>
            <p className="text-primary-foreground/70 text-sm leading-relaxed max-w-md">
              Conseil et accompagnement pour les victimes de maladies professionnelles, 
              accidents du travail et litiges assurantiels. Une aide humaine et experte, 
              née d'une expérience vécue.
            </p>
          </div>

          {/* Navigation */}
          <div>
            <h4 className="font-semibold mb-4" style={{ fontFamily: "'Playfair Display', serif" }}>
              Navigation
            </h4>
            <ul className="space-y-2">
              <li>
                <Link to="/a-propos" className="text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors">
                  À propos
                </Link>
              </li>
              <li>
                <Link to="/accompagnements" className="text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors">
                  Accompagnements
                </Link>
              </li>
              <li>
                <Link to="/ressources" className="text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors">
                  Ressources
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors">
                  Contact
                </Link>
              </li>
              <li>
                <Link to="/parrainage" className="text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors flex items-center gap-1">
                  <Gift className="w-3 h-3" />
                  Parrainage
                </Link>
              </li>
              <li>
                <Link to="/agenda" className="text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors">
                  Agenda
                </Link>
              </li>
              <li>
                <Link to="/simulateur" className="text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors">
                  Simulateur
                </Link>
              </li>
              <li>
                <Link to="/espace-client" className="text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors">
                  Espace client
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-semibold mb-4" style={{ fontFamily: "'Playfair Display', serif" }}>
              Contact
            </h4>
            <ul className="space-y-3">
              <li>
                <a 
                  href="mailto:contact@strategie-expertise-sante.fr" 
                  className="flex items-center gap-2 text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors"
                >
                  <Mail className="w-4 h-4" strokeWidth={1.5} />
                  contact@strategie-expertise-sante.fr
                </a>
              </li>
              <li>
                <a 
                  href="tel:+33600000000" 
                  className="flex items-center gap-2 text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors"
                >
                  <Phone className="w-4 h-4" strokeWidth={1.5} />
                  06 00 00 00 00
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Disclaimer Legal */}
        <div className="mt-8 pt-6 border-t border-primary-foreground/10">
          <p className="text-xs text-primary-foreground/40 leading-relaxed max-w-4xl" data-testid="footer-disclaimer">
            Stratégie & Expertise Santé propose un accompagnement stratégique et une analyse documentaire. 
            Ce service ne constitue pas une expertise médicale officielle ni une expertise judiciaire, 
            lesquelles sont réalisées par des médecins experts et experts judiciaires agréés. 
            Les services proposés ne constituent pas un conseil juridique ni un avis médical. 
            Pour toute décision juridique ou médicale, consultez un professionnel qualifié.
          </p>
        </div>

        {/* Bottom */}
        <div className="mt-12 pt-8 border-t border-primary-foreground/10">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-primary-foreground/50">
              © {currentYear} Stratégie & Expertise Santé. Tous droits réservés.
            </p>
            <div className="flex items-center gap-6">
              <Link 
                to="/mentions-legales" 
                className="text-xs text-primary-foreground/50 hover:text-primary-foreground/70 transition-colors"
              >
                Mentions légales & CGU
              </Link>
              <Link 
                to="/admin/login" 
                className="text-xs text-primary-foreground/30 hover:text-primary-foreground/50 transition-colors"
                data-testid="admin-link"
              >
                Administration
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};
