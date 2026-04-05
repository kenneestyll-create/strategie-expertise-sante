import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Phone, Gift, Handshake, Linkedin, Send, CheckCircle, Loader2, Building2, User } from 'lucide-react';
import { LogoFull } from '@/components/Logo';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const PARTNER_TYPES = [
  "Sponsoring événementiel",
  "Partenariat stratégique / commercial",
  "Partenaire technologique / API",
  "Collaboration éditoriale / contenu",
  "Programme ambassadeur / influence",
  "Recherche & développement",
  "Autre (précisez dans le champ texte)",
];

export const Footer = () => {
  const currentYear = new Date().getFullYear();
  const [form, setForm] = useState({ name: '', company: '', email: '', partner_type: '', message: '' });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim() || !form.partner_type) {
      toast.error("Veuillez remplir les champs obligatoires");
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API}/partner-request`, form);
      setSubmitted(true);
      toast.success("Demande envoyée avec succès !");
    } catch {
      toast.error("Erreur lors de l'envoi. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <footer className="bg-foreground text-primary-foreground">
      {/* Partner / Sponsor Section */}
      <div className="border-b border-primary-foreground/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-14">
          <div className="grid lg:grid-cols-[1fr_380px] gap-10 lg:gap-16 items-start" data-testid="footer-partner-section">
            {/* Left — description */}
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-xl bg-accent/15 flex items-center justify-center flex-shrink-0">
                  <Handshake className="w-5 h-5 text-accent" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-semibold" style={{ fontFamily: "'Playfair Display', serif" }} data-testid="partner-section-title">
                  Devenez partenaire
                </h3>
              </div>
              <p className="text-sm text-primary-foreground/60 leading-relaxed max-w-xl mb-5">
                Vous êtes professionnel de santé, avocat, expert ou association ?
                Rejoignez notre réseau pour collaborer, sponsoriser nos actions ou contribuer à améliorer
                l'accompagnement des victimes de maladies professionnelles.
              </p>
              <div className="flex items-center gap-3">
                <a
                  href="https://www.linkedin.com/company/strategie-expertise-sante"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-9 h-9 rounded-full border border-primary-foreground/15 flex items-center justify-center text-primary-foreground/50 hover:text-[#0A66C2] hover:border-[#0A66C2]/40 transition-all"
                  title="LinkedIn"
                  data-testid="partner-linkedin-icon"
                >
                  <Linkedin className="w-4 h-4" strokeWidth={1.5} />
                </a>
                <a
                  href="mailto:partenaires@strategie-expertise-sante.fr"
                  className="w-9 h-9 rounded-full border border-primary-foreground/15 flex items-center justify-center text-primary-foreground/50 hover:text-accent hover:border-accent/40 transition-all"
                  title="Email partenariat"
                  data-testid="partner-email-icon"
                >
                  <Mail className="w-4 h-4" strokeWidth={1.5} />
                </a>
              </div>
            </div>

            {/* Right — form */}
            <div>
              {submitted ? (
                <div className="rounded-xl border border-primary-foreground/10 bg-primary-foreground/[0.04] p-6 text-center" data-testid="partner-form-success">
                  <CheckCircle className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
                  <p className="font-semibold text-sm mb-1">Demande envoyée !</p>
                  <p className="text-xs text-primary-foreground/50">Nous reviendrons vers vous rapidement.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="rounded-xl border border-primary-foreground/10 bg-primary-foreground/[0.04] p-4 sm:p-5 space-y-3" data-testid="partner-form">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <label className="text-[11px] text-primary-foreground/50 font-medium">Nom *</label>
                      <div className="relative">
                        <User className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-primary-foreground/30" />
                        <Input
                          value={form.name}
                          onChange={e => setForm(p => ({...p, name: e.target.value}))}
                          placeholder="Votre nom"
                          className="h-9 text-xs pl-8 bg-transparent border-primary-foreground/15 text-primary-foreground placeholder:text-primary-foreground/30 focus:border-accent/50"
                          data-testid="partner-name-input"
                        />
                      </div>
                    </div>
                    <div className="space-y-1">
                      <label className="text-[11px] text-primary-foreground/50 font-medium">Société</label>
                      <div className="relative">
                        <Building2 className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-primary-foreground/30" />
                        <Input
                          value={form.company}
                          onChange={e => setForm(p => ({...p, company: e.target.value}))}
                          placeholder="Votre société"
                          className="h-9 text-xs pl-8 bg-transparent border-primary-foreground/15 text-primary-foreground placeholder:text-primary-foreground/30 focus:border-accent/50"
                          data-testid="partner-company-input"
                        />
                      </div>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[11px] text-primary-foreground/50 font-medium">Email *</label>
                    <div className="relative">
                      <Mail className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-primary-foreground/30" />
                      <Input
                        type="email"
                        value={form.email}
                        onChange={e => setForm(p => ({...p, email: e.target.value}))}
                        placeholder="votre@email.fr"
                        className="h-9 text-xs pl-8 bg-transparent border-primary-foreground/15 text-primary-foreground placeholder:text-primary-foreground/30 focus:border-accent/50"
                        data-testid="partner-email-input"
                      />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[11px] text-primary-foreground/50 font-medium">Type de partenariat *</label>
                    <Select value={form.partner_type} onValueChange={v => setForm(p => ({...p, partner_type: v}))} data-testid="partner-type-select">
                      <SelectTrigger className="h-9 text-xs bg-[#1a1a1a] border-primary-foreground/15 text-primary-foreground data-[placeholder]:text-primary-foreground/30" data-testid="partner-type-trigger">
                        <SelectValue placeholder="Sélectionnez..." />
                      </SelectTrigger>
                      <SelectContent className="bg-[#1a1a1a] border-primary-foreground/15 text-primary-foreground">
                        {PARTNER_TYPES.map(t => (
                          <SelectItem key={t} value={t} className="text-xs text-primary-foreground/80 focus:bg-accent/20 focus:text-primary-foreground cursor-pointer" data-testid={`partner-type-option-${t.substring(0,10).replace(/\s/g,'-').toLowerCase()}`}>{t}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[11px] text-primary-foreground/50 font-medium">Message (optionnel)</label>
                    <textarea
                      value={form.message}
                      onChange={e => setForm(p => ({...p, message: e.target.value}))}
                      rows={2}
                      placeholder="Décrivez brièvement votre projet de collaboration..."
                      className="flex w-full rounded-md border border-primary-foreground/15 bg-transparent px-3 py-2 text-xs text-primary-foreground placeholder:text-primary-foreground/30 resize-none focus:outline-none focus:border-accent/50"
                      data-testid="partner-message-input"
                    />
                  </div>
                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full rounded-full gap-2 bg-accent hover:bg-accent/90 text-white font-medium h-9 text-xs shadow-lg shadow-accent/15 hover:shadow-accent/25 hover:scale-[1.01] transition-all"
                    data-testid="partner-submit-button"
                  >
                    {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                    {loading ? 'Envoi...' : 'Envoyer ma demande'}
                  </Button>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link to="/" className="logo-shimmer flex items-center gap-0 mb-4">
              <LogoFull className="h-10 w-auto" textColor="#ffffff" />
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
                <Link to="/medecin-conseil" className="text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors">
                  Choisir son médecin conseil
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
        <div className="mt-12 pt-8 border-t border-primary-foreground/10" style={{ paddingBottom: 'calc(1rem + env(safe-area-inset-bottom, 0px))' }}>
          <div className="flex flex-col items-center gap-4">
            <p className="text-xs text-primary-foreground/40 text-center">
              &copy; {currentYear} Stratégie & Expertise Santé. Tous droits réservés.
            </p>
            <p className="text-[10px] text-primary-foreground/25 text-center max-w-2xl leading-relaxed" data-testid="footer-ip-notice">
              Les contenus, textes, méthodologies, structures d'analyse et supports de Stratégie & Expertise Santé 
              sont protégés au titre de la propriété intellectuelle.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6">
              <Link 
                to="/mentions-legales" 
                className="text-xs text-primary-foreground/50 hover:text-primary-foreground/70 transition-colors"
              >
                Mentions légales & CGU
              </Link>
              <Link 
                to="/politique-confidentialite" 
                className="text-xs text-primary-foreground/50 hover:text-primary-foreground/70 transition-colors"
                data-testid="footer-privacy-link"
              >
                Politique de confidentialité
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
