import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  ArrowRight, BookOpen, AlertCircle, FileText, Shield, HelpCircle, Download,
  Search, MapPin, Phone, Mail, ExternalLink, ChevronRight, Activity, Table2,
  Scale, Users, Heart, Clipboard, Info, Briefcase, TrendingDown, CheckCircle, Brain, Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { MALADIES_PRO_TABLEAUX, TMS_LOCALISATION, IPP_EXEMPLES } from '@/data/maladiesProfessionnelles';
import { MDPH_DIRECTORY } from '@/data/mdphDirectory';
import { SEO } from '@/components/SEO';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/* ─── Sub-component: Guide Card with Email Gate ─── */
const GuideCard = ({ guide }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const isAdmin = !!localStorage.getItem('admin_token');

  const handleAdminDownload = () => {
    window.open(`${API}/resources/pdf/${guide.id}`, '_blank');
    toast.success("Téléchargement lancé");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !email.includes('@')) {
      toast.error("Veuillez saisir une adresse email valide");
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API}/resources/request-guide`, {
        email,
        guide_id: guide.id,
        guide_title: guide.title,
        category: guide.category,
      });
      setSent(true);
      toast.success("Guide envoyé ! Le téléchargement va démarrer.");
      // Auto-download the PDF
      window.open(`${API}/resources/pdf/${guide.id}`, '_blank');
    } catch {
      toast.error("Erreur lors de l'envoi. Réessayez.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-border flex flex-col" data-testid={`library-guide-${guide.id}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="w-10 h-10 sm:w-12 sm:h-12 bg-accent/10 rounded-xl flex items-center justify-center mb-2 flex-shrink-0">
            <FileText className="w-5 h-5 sm:w-6 sm:h-6 text-accent" strokeWidth={1.5} />
          </div>
          <Badge variant="secondary" className="text-[10px] flex-shrink-0">{guide.category}</Badge>
        </div>
        <CardTitle className="text-sm sm:text-base leading-tight">{guide.title}</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col">
        <p className="text-xs sm:text-sm text-muted-foreground flex-1">{guide.description}</p>

        {sent ? (
          <div className="mt-4 pt-4 border-t border-border space-y-3">
            <div className="flex items-center gap-2 text-green-600 text-sm">
              <CheckCircle className="w-4 h-4 flex-shrink-0" />
              <span>Guide envoyé avec succès !</span>
            </div>
            <button
              onClick={() => window.dispatchEvent(new Event('strategiia:open'))}
              className="w-full flex items-center justify-center gap-2 text-xs text-accent hover:text-accent/80 font-medium py-2 px-3 rounded-lg bg-accent/5 hover:bg-accent/10 transition-colors cursor-pointer"
              data-testid={`guide-upsell-${guide.id}`}
            >
              <Brain className="w-3.5 h-3.5 flex-shrink-0" />
              Analyse plus précise ? Lancez StratégiIA
            </button>
          </div>
        ) : isAdmin ? (
          <div className="mt-4 pt-4 border-t border-border">
            <Button
              onClick={handleAdminDownload}
              size="sm"
              className="w-full gap-2 rounded-lg h-9 text-xs"
              data-testid={`guide-admin-download-${guide.id}`}
            >
              <Download className="w-3.5 h-3.5" />
              Télécharger (admin)
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-4 pt-4 border-t border-border space-y-2.5">
            <label className="text-xs text-muted-foreground flex items-center gap-1.5">
              <Mail className="w-3.5 h-3.5 flex-shrink-0" />
              Recevez ce guide gratuitement par email
            </label>
            <div className="flex gap-2">
              <Input
                type="email"
                placeholder="votre@email.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="h-9 text-sm flex-1"
                data-testid={`guide-email-${guide.id}`}
                required
              />
              <Button
                type="submit"
                size="sm"
                disabled={loading}
                className="gap-1.5 rounded-lg h-9 flex-shrink-0 text-xs px-3"
                data-testid={`guide-submit-${guide.id}`}
              >
                {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                <span className="hidden sm:inline">Recevoir</span>
              </Button>
            </div>
          </form>
        )}
      </CardContent>
    </Card>
  );
};

/* ─── Sub-component: MDPH Search & Card ─── */
const MdphFinder = () => {
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(null);

  const filtered = useMemo(() => {
    if (!query.trim()) return MDPH_DIRECTORY;
    const q = query.trim().toLowerCase();
    // Extract number from query (handles "MDA 28", "MDPH 75", "département 13", etc.)
    const numMatch = q.match(/\d+[a-b]?/i);
    const depNum = numMatch ? numMatch[0].toUpperCase() : null;
    // Try exact match on department code (direct or extracted number)
    if (depNum) {
      const exactDep = MDPH_DIRECTORY.filter(m => m.dep === depNum || m.dep === depNum.padStart(2, '0'));
      if (exactDep.length > 0) return exactDep;
    }
    // Also try the full query as exact dep match
    const exactFull = MDPH_DIRECTORY.filter(m => m.dep.toLowerCase() === q);
    if (exactFull.length > 0) return exactFull;
    // Fallback: search by name and address only
    return MDPH_DIRECTORY.filter(m =>
      m.nom.toLowerCase().includes(q) ||
      m.adresse.toLowerCase().includes(q)
    );
  }, [query]);

  return (
    <div className="space-y-6">
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          value={query}
          onChange={e => { setQuery(e.target.value); setSelected(null); }}
          placeholder="Rechercher par n° de département ou nom (ex: 75, Paris)"
          className="pl-10"
          data-testid="mdph-search-input"
        />
      </div>

      {selected ? (
        <Card className="border-accent/30 bg-accent/5" data-testid="mdph-detail-card">
          <CardContent className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Badge variant="secondary" className="text-base px-3 py-1 mb-2">{selected.dep}</Badge>
                <h3 className="text-xl font-semibold">MDPH {selected.nom}</h3>
              </div>
              <button onClick={() => setSelected(null)} className="text-sm text-accent hover:underline">Retour</button>
            </div>
            <div className="grid gap-3">
              <div className="flex items-start gap-3 p-3 bg-background rounded-lg">
                <MapPin className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Adresse</p>
                  <p className="text-sm">{selected.adresse}</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-background rounded-lg">
                <Phone className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Téléphone</p>
                  <a href={`tel:${selected.tel}`} className="text-sm text-accent hover:underline">{selected.tel}</a>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-background rounded-lg">
                <Mail className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Email</p>
                  <a href={`mailto:${selected.email}`} className="text-sm text-accent hover:underline">{selected.email}</a>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-background rounded-lg">
                <ExternalLink className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Site web</p>
                  <a href={selected.site} target="_blank" rel="noopener noreferrer" className="text-sm text-accent hover:underline">{selected.site}</a>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2 max-h-[480px] overflow-y-auto pr-1" data-testid="mdph-list">
          {filtered.map(m => (
            <button
              key={m.dep}
              onClick={() => setSelected(m)}
              className="flex items-center gap-3 p-3 rounded-lg border border-border hover:border-accent/40 hover:bg-accent/5 transition-all text-left"
              data-testid={`mdph-${m.dep}`}
            >
              <span className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center text-sm font-bold flex-shrink-0">{m.dep}</span>
              <div className="min-w-0">
                <p className="text-sm font-medium truncate">{m.nom}</p>
                <p className="text-xs text-muted-foreground truncate">{m.tel}</p>
              </div>
              <ChevronRight className="w-4 h-4 text-muted-foreground ml-auto flex-shrink-0" />
            </button>
          ))}
          {filtered.length === 0 && (
            <p className="col-span-full text-center text-muted-foreground py-8">Aucun département trouvé pour "{query}"</p>
          )}
        </div>
      )}
    </div>
  );
};

export const ResourcesPage = () => {
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);

  const categories = ["AT/MP", "Expertises", "Assurances", "MDPH"];

  useEffect(() => { fetchFaqs(); }, []);

  const fetchFaqs = async () => {
    try { const r = await axios.get(`${API}/faq`); setFaqs(r.data); }
    catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const getFaqsByCategory = (category) => faqs.filter(f => f.categorie === category);

  const glossary = [
    { term: "IPP", fullName: "Incapacité Permanente Partielle", definition: "Taux exprimé en pourcentage qui évalue les séquelles définitives d'un accident du travail ou d'une maladie professionnelle." },
    { term: "IP", fullName: "Incidence Professionnelle", definition: "Poste de préjudice indemnisant les conséquences sur la carrière : pénibilité accrue, dévalorisation, reconversion, perte d'opportunités." },
    { term: "PGPF", fullName: "Perte de Gains Professionnels Futurs", definition: "Indemnisation de la perte définitive de revenus après consolidation, calculée par capitalisation selon un barème officiel." },
    { term: "PTIA", fullName: "Perte Totale et Irréversible d'Autonomie", definition: "Garantie d'assurance couvrant l'état d'une personne qui ne peut plus exercer aucune activité professionnelle." },
    { term: "CRRMP", fullName: "Comité Régional de Reconnaissance des MP", definition: "Instance médicale qui statue sur les maladies hors tableau ou ne remplissant pas les conditions d'un tableau." },
    { term: "AT/MP", fullName: "Accident du Travail / Maladie Pro", definition: "Régime de la Sécurité sociale couvrant les accidents du travail et maladies professionnelles." },
    { term: "RQTH", fullName: "Reconnaissance Travailleur Handicapé", definition: "Décision administrative ouvrant des droits spécifiques en matière d'emploi." },
    { term: "MDPH", fullName: "Maison Départementale PH", definition: "Guichet unique pour toutes les démarches liées au handicap : RQTH, AAH, cartes, PCH, etc." },
    { term: "AAH", fullName: "Allocation Adultes Handicapés", definition: "Aide financière pour personnes handicapées (taux d'incapacité ≥ 80%, ou 50-79% avec restriction d'emploi)." },
    { term: "CMI", fullName: "Carte Mobilité Inclusion", definition: "Carte remplaçant les anciennes cartes d'invalidité, de priorité et de stationnement." },
    { term: "PGPA", fullName: "Perte de Gains Professionnels Actuels", definition: "Indemnisation des pertes de revenus entre l'accident et la consolidation (arrêt de travail, mi-temps thérapeutique)." },
    { term: "Dintilhac", fullName: "Nomenclature Dintilhac", definition: "Classification de référence des postes de préjudice corporel en France, utilisée pour structurer l'indemnisation." }
  ];

  const guides = [
    { icon: FileText, title: "Déclarer une maladie professionnelle", description: "Les étapes essentielles pour faire reconnaître votre maladie.", points: ["Obtenir un certificat médical initial", "Remplir le formulaire cerfa n°60-3950", "Envoyer à votre CPAM sous 15 jours", "Attendre la décision (3 mois max)"] },
    { icon: Shield, title: "Se préparer à une expertise médicale", description: "Conseils pour aborder sereinement cette étape.", points: ["Rassembler vos documents médicaux", "Lister vos symptômes au quotidien", "Préparer une chronologie", "Rester honnête et précis"] },
    { icon: AlertCircle, title: "Contester un refus d'indemnisation", description: "Vos recours face à un refus.", points: ["Demander les motifs par écrit", "Vérifier la conformité légale", "Saisir le médiateur", "Envisager une action judiciaire"] }
  ];

  return (
    <main className="page-transition pt-20">
      <SEO title="Ressources et guides" description="Ressources gratuites : IP, PGPF, annuaire MDPH, tableaux des maladies professionnelles, guides pratiques et outils de calcul." path="/ressources" />
      {/* Hero */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Ressources</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="resources-title">
              Comprendre pour mieux agir
            </h1>
            <p className="text-lg text-muted-foreground">
              Des explications pédagogiques et accessibles pour naviguer dans le monde
              des maladies professionnelles, des expertises et des droits au handicap.
            </p>
          </div>
        </div>
      </section>

      {/* Glossary */}
      <section className="section-padding" id="glossaire">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Lexique</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">Les termes à connaître</h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {glossary.map((item, i) => (
              <Card key={i} className="card-lift border-border" data-testid={`glossary-item-${item.term.toLowerCase()}`}>
                <CardHeader className="pb-2">
                  <span className="text-2xl font-bold text-accent">{item.term}</span>
                  <p className="text-sm text-muted-foreground">{item.fullName}</p>
                </CardHeader>
                <CardContent><p className="text-sm">{item.definition}</p></CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════ NEW CONTENT SECTIONS ═══════════════ */}
      <section className="section-padding bg-card" id="encyclopedie">
        <div className="max-w-7xl mx-auto">
          <div className="mb-10">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Encyclopédie</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">Base de connaissances</h2>
            <p className="text-muted-foreground max-w-2xl">
              Tout ce qu'il faut savoir sur les maladies professionnelles, l'IPP, l'incidence professionnelle, la PGPF, les MDPH et les aides disponibles.
            </p>
          </div>

          <Tabs defaultValue="tableaux" className="w-full" data-testid="encyclopedia-tabs">
            <TabsList className="w-full flex flex-nowrap sm:flex-wrap h-auto gap-1.5 sm:gap-2 bg-muted/50 p-2 rounded-xl mb-8 overflow-x-auto">
              <TabsTrigger value="tableaux" className="shrink-0 sm:flex-1 min-w-fit sm:min-w-[100px] gap-1 sm:gap-1.5 rounded-lg text-xs sm:text-sm" data-testid="enc-tab-tableaux">
                <Table2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" /> Tableaux MP
              </TabsTrigger>
              <TabsTrigger value="horstableau" className="shrink-0 sm:flex-1 min-w-fit sm:min-w-[100px] gap-1 sm:gap-1.5 rounded-lg text-xs sm:text-sm" data-testid="enc-tab-horstableau">
                <Scale className="w-3.5 h-3.5 sm:w-4 sm:h-4" /> Hors tableau
              </TabsTrigger>
              <TabsTrigger value="ipp" className="shrink-0 sm:flex-1 min-w-fit sm:min-w-[70px] gap-1 sm:gap-1.5 rounded-lg text-xs sm:text-sm" data-testid="enc-tab-ipp">
                <Activity className="w-3.5 h-3.5 sm:w-4 sm:h-4" /> IPP
              </TabsTrigger>
              <TabsTrigger value="ip" className="shrink-0 sm:flex-1 min-w-fit sm:min-w-[70px] gap-1 sm:gap-1.5 rounded-lg text-xs sm:text-sm" data-testid="enc-tab-ip">
                <Briefcase className="w-3.5 h-3.5 sm:w-4 sm:h-4" /> IP
              </TabsTrigger>
              <TabsTrigger value="pgpf" className="shrink-0 sm:flex-1 min-w-fit sm:min-w-[70px] gap-1 sm:gap-1.5 rounded-lg text-xs sm:text-sm" data-testid="enc-tab-pgpf">
                <TrendingDown className="w-3.5 h-3.5 sm:w-4 sm:h-4" /> PGPF
              </TabsTrigger>
              <TabsTrigger value="mdph" className="shrink-0 sm:flex-1 min-w-fit sm:min-w-[70px] gap-1 sm:gap-1.5 rounded-lg text-xs sm:text-sm" data-testid="enc-tab-mdph">
                <MapPin className="w-3.5 h-3.5 sm:w-4 sm:h-4" /> MDPH
              </TabsTrigger>
              <TabsTrigger value="aides" className="shrink-0 sm:flex-1 min-w-fit sm:min-w-[70px] gap-1 sm:gap-1.5 rounded-lg text-xs sm:text-sm" data-testid="enc-tab-aides">
                <Heart className="w-3.5 h-3.5 sm:w-4 sm:h-4" /> Aides MDPH
              </TabsTrigger>
            </TabsList>

            {/* ── Tab 1 : Tableaux maladies pro ── */}
            <TabsContent value="tableaux" data-testid="enc-content-tableaux">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Table2 className="w-5 h-5 text-accent" /> Tableau officiel des maladies professionnelles
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">
                      La Sécurité sociale reconnaît les maladies professionnelles inscrites dans des tableaux numérotés.
                      Chaque tableau précise la maladie, le délai de prise en charge et les travaux exposants.
                    </p>
                  </CardHeader>
                  <CardContent>
                    {/* Desktop: tableau classique */}
                    <div className="hidden md:block overflow-x-auto">
                      <table className="w-full text-sm" data-testid="maladies-pro-table">
                        <thead>
                          <tr className="border-b border-border">
                            <th className="text-left py-3 px-3 font-semibold w-20">N°</th>
                            <th className="text-left py-3 px-3 font-semibold">Maladie</th>
                            <th className="text-left py-3 px-3 font-semibold w-40">Délai de prise en charge</th>
                            <th className="text-left py-3 px-3 font-semibold hidden lg:table-cell">Travaux concernés</th>
                          </tr>
                        </thead>
                        <tbody>
                          {MALADIES_PRO_TABLEAUX.map((t, i) => (
                            <tr key={i} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                              <td className="py-3 px-3"><Badge variant="outline" className="font-mono">{t.numero}</Badge></td>
                              <td className="py-3 px-3 font-medium">{t.titre}</td>
                              <td className="py-3 px-3 text-muted-foreground">{t.delai}</td>
                              <td className="py-3 px-3 text-muted-foreground text-xs hidden lg:table-cell">{t.travaux}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Mobile: cartes empilées */}
                    <div className="md:hidden space-y-3" data-testid="maladies-pro-cards-mobile">
                      {MALADIES_PRO_TABLEAUX.map((t, i) => (
                        <div key={i} className="p-4 rounded-xl border border-border bg-muted/20" data-testid={`maladie-card-${t.numero}`}>
                          <div className="flex items-start gap-3">
                            <Badge variant="outline" className="font-mono text-sm flex-shrink-0 mt-0.5">{t.numero}</Badge>
                            <div className="flex-1 min-w-0">
                              <h4 className="font-medium text-sm leading-snug">{t.titre}</h4>
                              <div className="flex items-center gap-1.5 mt-2 text-xs text-muted-foreground">
                                <Activity className="w-3.5 h-3.5 flex-shrink-0 text-accent" />
                                <span>Délai : <strong className="text-foreground">{t.delai}</strong></span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* TMS detail */}
                <Card>
                  <CardHeader>
                    <CardTitle>Zoom sur les TMS (Tableau 57) — 1ère cause de maladie professionnelle</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      Les Troubles Musculo-Squelettiques représentent plus de 85% des maladies professionnelles reconnues en France.
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {TMS_LOCALISATION.map((tms, i) => (
                        <div key={i} className="p-4 rounded-xl border border-border bg-background" data-testid={`tms-${tms.tableau.toLowerCase()}`}>
                          <div className="flex items-center gap-2 mb-3">
                            <Badge className="bg-accent/10 text-accent border-accent/20">{tms.tableau}</Badge>
                            <h4 className="font-semibold">{tms.zone}</h4>
                          </div>
                          <ul className="space-y-1.5">
                            {tms.pathologies.map((p, j) => (
                              <li key={j} className="text-sm text-muted-foreground flex items-start gap-2">
                                <ChevronRight className="w-3.5 h-3.5 text-accent mt-0.5 flex-shrink-0" />{p}
                              </li>
                            ))}
                          </ul>
                          <p className="text-xs text-muted-foreground mt-3 pt-2 border-t border-border/50">
                            Délai de prise en charge : {tms.delai}
                          </p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* ── Tab 2 : Hors tableau ── */}
            <TabsContent value="horstableau" data-testid="enc-content-horstableau">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Scale className="w-5 h-5 text-accent" /> Reconnaissance hors tableau
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Si votre maladie ne figure dans aucun tableau ou si vous ne remplissez pas toutes les conditions,
                    vous pouvez quand même obtenir une reconnaissance via le CRRMP.
                  </p>
                </CardHeader>
                <CardContent className="space-y-8">
                  {/* Two paths */}
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="p-6 rounded-xl bg-accent/5 border border-accent/15">
                      <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                        <span className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center text-accent font-bold text-sm">1</span>
                        Alinéa 3 — Maladie inscrite au tableau
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Votre maladie figure dans un tableau mais vous ne remplissez pas <strong>toutes les conditions</strong>
                        (délai dépassé, travaux différents, etc.).
                      </p>
                      <div className="space-y-2">
                        <p className="text-sm font-medium">Conditions requises :</p>
                        <ul className="space-y-2">
                          <li className="text-sm flex items-start gap-2"><ChevronRight className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" /><span>La maladie est désignée dans un tableau</span></li>
                          <li className="text-sm flex items-start gap-2"><ChevronRight className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" /><span>Au moins une condition du tableau n'est pas remplie</span></li>
                          <li className="text-sm flex items-start gap-2"><ChevronRight className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" /><span>Le CRRMP établit que la maladie est directement causée par le travail</span></li>
                        </ul>
                      </div>
                    </div>
                    <div className="p-6 rounded-xl bg-accent/5 border border-accent/15">
                      <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                        <span className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center text-accent font-bold text-sm">2</span>
                        Alinéa 4 — Maladie absente des tableaux
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Votre maladie <strong>ne figure dans aucun tableau</strong>. Les conditions sont plus strictes.
                      </p>
                      <div className="space-y-2">
                        <p className="text-sm font-medium">Conditions requises :</p>
                        <ul className="space-y-2">
                          <li className="text-sm flex items-start gap-2"><ChevronRight className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" /><span><strong>Taux d'IPP &ge; 25%</strong> (ou décès de la victime)</span></li>
                          <li className="text-sm flex items-start gap-2"><ChevronRight className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" /><span>Lien <strong>direct et essentiel</strong> entre la maladie et le travail habituel</span></li>
                          <li className="text-sm flex items-start gap-2"><ChevronRight className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" /><span>Avis favorable du CRRMP après instruction du dossier</span></li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Procedure */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Procédure de saisine du CRRMP</h3>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                      {[
                        { step: 1, title: "Déclaration", desc: "Déclarez votre maladie professionnelle auprès de la CPAM avec un certificat médical initial." },
                        { step: 2, title: "Instruction CPAM", desc: "La CPAM instruit le dossier. Si les conditions du tableau ne sont pas remplies, elle transmet au CRRMP." },
                        { step: 3, title: "Examen CRRMP", desc: "Le comité (3 médecins) examine les pièces médicales et professionnelles. Il peut vous convoquer." },
                        { step: 4, title: "Décision", desc: "Le CRRMP rend un avis motivé. La CPAM vous notifie la décision. Recours possible sous 2 mois." }
                      ].map((s) => (
                        <div key={s.step} className="p-4 rounded-xl border border-border">
                          <span className="w-8 h-8 rounded-full bg-accent text-accent-foreground flex items-center justify-center text-sm font-bold mb-3">{s.step}</span>
                          <h4 className="font-semibold mb-2">{s.title}</h4>
                          <p className="text-sm text-muted-foreground">{s.desc}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-yellow-50 border border-yellow-200/50">
                    <p className="text-sm flex items-start gap-2">
                      <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                      <span>
                        <strong>Important :</strong> La procédure hors tableau est plus longue et exigeante.
                        Un accompagnement professionnel est fortement recommandé pour constituer un dossier solide.
                        <Link to="/contact" className="text-accent hover:underline ml-1">Contactez-nous pour être accompagné.</Link>
                      </span>
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* ── Tab 3 : IPP ── */}
            <TabsContent value="ipp" data-testid="enc-content-ipp">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="w-5 h-5 text-accent" /> L'Incapacité Permanente Partielle (IPP)
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid md:grid-cols-2 gap-8">
                      <div className="space-y-4">
                        <h3 className="font-semibold text-lg">Qu'est-ce que l'IPP ?</h3>
                        <p className="text-sm text-muted-foreground leading-relaxed">
                          L'<strong>Incapacité Permanente Partielle</strong> est un taux, exprimé en pourcentage,
                          qui mesure les <strong>séquelles définitives</strong> d'un accident du travail ou d'une maladie
                          professionnelle sur votre capacité physique et professionnelle.
                        </p>
                        <p className="text-sm text-muted-foreground leading-relaxed">
                          Ce taux est fixé par le <strong>médecin-conseil</strong> de la Sécurité sociale lorsque votre
                          état de santé est considéré comme stabilisé (consolidé). Il prend en compte :
                        </p>
                        <ul className="space-y-2">
                          {["La nature de l'infirmité et l'état général", "Les facultés physiques et mentales", "Les aptitudes et qualifications professionnelles", "L'âge de la victime au moment de la consolidation"].map((p, i) => (
                            <li key={i} className="text-sm flex items-start gap-2"><ChevronRight className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" />{p}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="space-y-4">
                        <h3 className="font-semibold text-lg">Comment est-il indemnisé ?</h3>
                        <div className="p-4 rounded-xl bg-muted/50 border border-border">
                          <h4 className="font-medium mb-2">Taux &lt; 10% : Capital forfaitaire</h4>
                          <p className="text-sm text-muted-foreground">
                            Versement unique calculé selon un barème fixe. Le montant augmente avec le taux.
                            Exemples : 3% ≈ 1 111 €, 5% ≈ 2 222 €, 9% ≈ 5 012 €.
                          </p>
                        </div>
                        <div className="p-4 rounded-xl bg-accent/5 border border-accent/15">
                          <h4 className="font-medium mb-2">Taux ≥ 10% : Rente viagère</h4>
                          <p className="text-sm text-muted-foreground">
                            Versement régulier (trimestriel ou mensuel) calculé à partir du salaire de référence et du
                            <strong> taux utile</strong> (moitié du taux jusqu'à 50%, puis totalité au-delà).
                          </p>
                        </div>
                        <div className="p-3 rounded-lg bg-blue-50 border border-blue-200/50">
                          <p className="text-sm flex items-start gap-2">
                            <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                            <Link to="/calculatrice-ipp" className="text-blue-700 hover:underline font-medium">
                              Estimez votre indemnisation IPP avec notre calculatrice en ligne →
                            </Link>
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Exemples concrets */}
                <Card>
                  <CardHeader>
                    <CardTitle>Exemples concrets de taux d'IPP</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      Voici des exemples illustratifs pour comprendre la signification concrète de chaque niveau de taux.
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3" data-testid="ipp-examples-list">
                      {IPP_EXEMPLES.map((ex, i) => (
                        <div key={i} className="flex gap-4 p-4 rounded-xl border border-border hover:bg-muted/20 transition-colors" data-testid={`ipp-example-${ex.taux}`}>
                          <div className="flex-shrink-0 w-16 h-16 rounded-xl bg-accent/10 flex items-center justify-center">
                            <span className="text-xl font-bold text-accent">{ex.taux}%</span>
                          </div>
                          <div className="space-y-1">
                            <p className="font-medium">{ex.description}</p>
                            <p className="text-sm text-accent font-medium">{ex.indemnisation}</p>
                            <p className="text-sm text-muted-foreground">{ex.consequences}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* ── Tab IP : Incidence Professionnelle ── */}
            <TabsContent value="ip" data-testid="enc-content-ip">
              <div className="space-y-6">
                {/* Definition */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Briefcase className="w-5 h-5 text-accent" /> Incidence Professionnelle (IP) — Définition
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-foreground/80 leading-relaxed">
                      L'<strong>incidence professionnelle</strong> (IP) est un poste de préjudice qui vise à indemniser les conséquences d'un accident ou d'une maladie professionnelle sur la vie professionnelle de la victime, au-delà de la simple perte de revenus. Elle couvre l'ensemble des répercussions négatives sur la carrière, les conditions de travail et les perspectives d'évolution professionnelle.
                    </p>
                    <p className="text-sm text-foreground/80 leading-relaxed">
                      Contrairement à l'<strong>Incapacité Permanente Partielle (IPP)</strong> qui mesure le déficit fonctionnel, l'incidence professionnelle évalue spécifiquement l'impact de ce déficit sur l'activité professionnelle de la victime. C'est un poste de préjudice complémentaire, reconnu par la jurisprudence et les barèmes d'indemnisation.
                    </p>
                  </CardContent>
                </Card>

                {/* Critères */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Scale className="w-5 h-5 text-accent" /> Critères retenus par les juridictions et assureurs
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid gap-4 sm:grid-cols-2">
                      {[
                        {
                          title: "Pénibilité accrue",
                          desc: "La victime peut continuer à travailler mais dans des conditions plus pénibles : efforts supplémentaires, fatigue accrue, douleurs lors de certaines tâches, aménagements nécessaires du poste.",
                          color: "bg-red-500/10 border-red-500/20 text-red-700 dark:text-red-400"
                        },
                        {
                          title: "Dévalorisation sur le marché du travail",
                          desc: "Le handicap ou les séquelles réduisent l'employabilité de la victime : difficulté à retrouver un emploi équivalent, discrimination à l'embauche, postes accessibles moins nombreux.",
                          color: "bg-orange-500/10 border-orange-500/20 text-orange-700 dark:text-orange-400"
                        },
                        {
                          title: "Perte d'opportunités professionnelles",
                          desc: "La victime ne peut plus accéder à des promotions, formations qualifiantes, missions spécifiques ou évolutions de carrière auxquelles elle aurait pu prétendre sans le dommage.",
                          color: "bg-amber-500/10 border-amber-500/20 text-amber-700 dark:text-amber-400"
                        },
                        {
                          title: "Nécessité de reconversion",
                          desc: "L'impossibilité de poursuivre dans le même métier impose une reconversion professionnelle, souvent vers un emploi moins qualifié ou moins rémunéré.",
                          color: "bg-blue-500/10 border-blue-500/20 text-blue-700 dark:text-blue-400"
                        }
                      ].map((item, i) => (
                        <div key={i} className={`p-4 rounded-xl border ${item.color}`}>
                          <h4 className="font-semibold text-sm mb-2">{item.title}</h4>
                          <p className="text-xs leading-relaxed opacity-90">{item.desc}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Justificatifs */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <FileText className="w-5 h-5 text-accent" /> Justificatifs nécessaires
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-3 sm:grid-cols-2">
                      {[
                        { title: "Rapports médicaux", items: ["Certificats médicaux détaillant les séquelles", "Rapport d'expertise médicale avec taux d'IPP", "Bilan fonctionnel et limitations identifiées", "Avis du médecin du travail sur l'aptitude"] },
                        { title: "Expertises", items: ["Expertise médicale judiciaire ou amiable", "Expertise ergonomique du poste de travail", "Évaluation par un médecin conseil spécialisé", "Bilan de compétences post-accident"] },
                        { title: "Attestations employeur", items: ["Attestation de l'employeur sur les restrictions", "Fiche de poste avant/après l'accident", "Historique des aménagements demandés", "Attestation de collègues (témoignages)"] },
                        { title: "Éléments de carrière", items: ["CV et parcours professionnel complet", "Bulletins de salaire (évolution sur 3-5 ans)", "Entretiens annuels d'évaluation", "Projections de carrière (promotions prévues)"] }
                      ].map((group, i) => (
                        <div key={i} className="p-4 rounded-xl bg-muted/50 border border-border/50">
                          <h4 className="font-semibold text-sm mb-3 text-accent">{group.title}</h4>
                          <ul className="space-y-1.5">
                            {group.items.map((item, j) => (
                              <li key={j} className="flex items-start gap-2 text-xs text-foreground/70">
                                <ChevronRight className="w-3 h-3 mt-0.5 text-accent flex-shrink-0" /> {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Exemples concrets */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Users className="w-5 h-5 text-accent" /> Exemples concrets d'indemnisation
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[
                        {
                          profil: "Ouvrier du batiment — 45 ans",
                          situation: "TMS epaule, IPP 15%. Ne peut plus porter de charges lourdes. Reclasse comme magasinier avec perte de primes.",
                          ip: "Pénibilité accrue + devalorisation",
                          indemnisation: "15 000 a 25 000 EUR"
                        },
                        {
                          profil: "Infirmiere — 38 ans",
                          situation: "Lombalgie chronique post-AT, IPP 20%. Reconversion vers un poste administratif hospitalier moins rémunéré.",
                          ip: "Reconversion + perte d'opportunités",
                          indemnisation: "30 000 a 50 000 EUR"
                        },
                        {
                          profil: "Cadre commercial — 52 ans",
                          situation: "Syndrome du canal carpien bilateral (MP), IPP 12%. Difficulté a utiliser un clavier. Retraité anticipee forcee.",
                          ip: "Devalorisation + perte de fin de carrière",
                          indemnisation: "40 000 a 80 000 EUR"
                        },
                        {
                          profil: "Technicien agricole — 35 ans",
                          situation: "Exposition pesticides, IPP 25%. Ne peut plus travailler en milieu agricole. Reconversion nécessaire.",
                          ip: "Reconversion totale + devalorisation",
                          indemnisation: "50 000 a 100 000 EUR"
                        }
                      ].map((ex, i) => (
                        <div key={i} className="p-4 rounded-xl border border-border/50 bg-card">
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                            <h4 className="font-semibold text-sm">{ex.profil}</h4>
                            <Badge variant="outline" className="text-accent border-accent/30 w-fit">{ex.indemnisation}</Badge>
                          </div>
                          <p className="text-xs text-foreground/70 mb-1">{ex.situation}</p>
                          <p className="text-xs text-muted-foreground">IP retenue : <span className="font-medium text-foreground/80">{ex.ip}</span></p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Disclaimer */}
                <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20" data-testid="ip-disclaimer">
                  <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-amber-800 dark:text-amber-300 leading-relaxed">
                    <strong>Avertissement :</strong> Ces informations sont fournies a titre indicatif et ne constituent pas un conseil juridique. Les montants d'indemnisation dependent de chaque situation individuelle et de l'appreciation des juges. Consultez un professionnel du droit pour une évaluation personnalisée de votre dossier.
                  </p>
                </div>

                {/* CTA */}
                <div className="flex flex-col sm:flex-row gap-3 items-center justify-center pt-2">
                  <Link to="/calculatrice-ipp">
                    <Button variant="outline" className="gap-2">
                      <Activity className="w-4 h-4" /> Calculer votre taux IPP
                    </Button>
                  </Link>
                  <Link to="/simulateur">
                    <Button className="gap-2">
                      <ArrowRight className="w-4 h-4" /> Analyser votre dossier avec StrategiIA
                    </Button>
                  </Link>
                </div>
              </div>
            </TabsContent>

            {/* ── Tab PGPF : Perte de Gains Professionnels Futurs ── */}
            <TabsContent value="pgpf" data-testid="enc-content-pgpf">
              <div className="space-y-6">
                {/* Definition */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingDown className="w-5 h-5 text-accent" /> Perte de Gains Professionnels Futurs (PGPF) — Définition
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-foreground/80 leading-relaxed">
                      La <strong>Perte de Gains Professionnels Futurs</strong> (PGPF) est un poste de préjudice qui compense la réduction définitive des revenus professionnels de la victime après la consolidation de ses blessures. Elle représente la différence entre ce que la victime aurait gagné sans l'accident et ce qu'elle gagnera effectivement avec ses séquelles.
                    </p>
                    <p className="text-sm text-foreground/80 leading-relaxed">
                      La PGPF fait partie de la <strong>nomenclature Dintilhac</strong>, référence en matière d'indemnisation du préjudice corporel en France. Elle se distingue nettement des autres postes de préjudice économique.
                    </p>
                  </CardContent>
                </Card>

                {/* Distinction perte actuelle vs future */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Scale className="w-5 h-5 text-accent" /> Distinction : perte actuelle vs. perte future
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
                        <h4 className="font-semibold text-sm mb-2 text-blue-700 dark:text-blue-400">Perte de Gains Professionnels Actuels (PGPA)</h4>
                        <ul className="space-y-1.5 text-xs text-foreground/70">
                          <li className="flex items-start gap-2"><ChevronRight className="w-3 h-3 mt-0.5 text-blue-500 flex-shrink-0" /> Couvre la période entre l'accident et la consolidation</li>
                          <li className="flex items-start gap-2"><ChevronRight className="w-3 h-3 mt-0.5 text-blue-500 flex-shrink-0" /> Indemnise les pertes de revenus pendant l'arrêt de travail</li>
                          <li className="flex items-start gap-2"><ChevronRight className="w-3 h-3 mt-0.5 text-blue-500 flex-shrink-0" /> Calcul : différence entre salaire habituel et indemnités journalières perçues</li>
                          <li className="flex items-start gap-2"><ChevronRight className="w-3 h-3 mt-0.5 text-blue-500 flex-shrink-0" /> Période limitée et quantifiable rétrospectivement</li>
                        </ul>
                      </div>
                      <div className="p-4 rounded-xl bg-accent/10 border border-accent/20">
                        <h4 className="font-semibold text-sm mb-2 text-accent">Perte de Gains Professionnels Futurs (PGPF)</h4>
                        <ul className="space-y-1.5 text-xs text-foreground/70">
                          <li className="flex items-start gap-2"><ChevronRight className="w-3 h-3 mt-0.5 text-accent flex-shrink-0" /> Couvre toute la période après consolidation jusqu'à la retraite</li>
                          <li className="flex items-start gap-2"><ChevronRight className="w-3 h-3 mt-0.5 text-accent flex-shrink-0" /> Indemnise la perte de capacité de gain définitive</li>
                          <li className="flex items-start gap-2"><ChevronRight className="w-3 h-3 mt-0.5 text-accent flex-shrink-0" /> Calcul : projection de carrière avec capitalisation (barème de capitalisation)</li>
                          <li className="flex items-start gap-2"><ChevronRight className="w-3 h-3 mt-0.5 text-accent flex-shrink-0" /> Prend en compte l'évolution salariale prévisible</li>
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Méthode de calcul */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Activity className="w-5 h-5 text-accent" /> Méthode de calcul en France
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-foreground/80 leading-relaxed">
                      Le calcul de la PGPF repose sur une méthodologie précise, validée par la jurisprudence française :
                    </p>
                    <div className="space-y-3">
                      {[
                        {
                          etape: "1. Projection de carrière",
                          desc: "Reconstitution du parcours professionnel hypothétique sans l'accident : évolution de poste, augmentations prévues, promotions probables, ancienneté.",
                        },
                        {
                          etape: "2. Évolution salariale prévisible",
                          desc: "Estimation du salaire futur en tenant compte de l'inflation, des conventions collectives, de l'ancienneté et des usages du secteur.",
                        },
                        {
                          etape: "3. Impact du handicap sur les revenus",
                          desc: "Évaluation de la réduction de revenus causée par les séquelles : temps partiel imposé, poste moins rémunéré, impossibilité de travailler.",
                        },
                        {
                          etape: "4. Capitalisation",
                          desc: "Application d'un barème de capitalisation (Gazette du Palais) pour convertir la perte annuelle en un capital unique, en fonction de l'âge de la victime et de l'espérance de vie.",
                        }
                      ].map((step, i) => (
                        <div key={i} className="flex gap-3 p-3 rounded-lg bg-muted/50 border border-border/30">
                          <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
                            <span className="text-xs font-bold text-accent">{i + 1}</span>
                          </div>
                          <div>
                            <h4 className="font-semibold text-sm">{step.etape}</h4>
                            <p className="text-xs text-foreground/70 mt-1">{step.desc}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="p-4 rounded-xl bg-muted/80 border border-border/50">
                      <p className="text-xs text-foreground/70 leading-relaxed">
                        <strong>Formule simplifiée :</strong> PGPF = (Salaire annuel sans accident - Salaire annuel avec séquelles) x Euro de rente (barème de capitalisation selon l'âge)
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Justificatifs */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <FileText className="w-5 h-5 text-accent" /> Justificatifs nécessaires
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-3 sm:grid-cols-2">
                      {[
                        { title: "Bulletins de salaire", items: ["12 à 36 derniers bulletins avant l'accident", "Bulletins post-consolidation (si reprise)", "Primes, heures supplémentaires, avantages en nature", "Attestations de paiement des indemnités perçues"] },
                        { title: "Contrats de travail", items: ["Contrat en vigueur au moment de l'accident", "Avenants et promotions obtenues", "Convention collective applicable", "Grille salariale de l'entreprise / du secteur"] },
                        { title: "Évolution professionnelle prévisible", items: ["Entretiens professionnels et plan de carrière", "Formations prévues ou en cours", "Promesses d'embauche ou de promotion", "Statistiques sectorielles d'évolution salariale"] },
                        { title: "Expertises économiques et médicales", items: ["Expertise médicale avec taux d'IPP", "Expertise économique (calcul de perte par actuaire)", "Avis du médecin du travail sur les restrictions", "Bilan de compétences ou d'orientation professionnelle"] }
                      ].map((group, i) => (
                        <div key={i} className="p-4 rounded-xl bg-muted/50 border border-border/50">
                          <h4 className="font-semibold text-sm mb-3 text-accent">{group.title}</h4>
                          <ul className="space-y-1.5">
                            {group.items.map((item, j) => (
                              <li key={j} className="flex items-start gap-2 text-xs text-foreground/70">
                                <ChevronRight className="w-3 h-3 mt-0.5 text-accent flex-shrink-0" /> {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Cas concrets */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Users className="w-5 h-5 text-accent" /> Cas concrets d'application
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[
                        {
                          profil: "Salarié du privé — Technicien, 40 ans",
                          situation: "Salaire net : 2 200 EUR/mois. Après AT grave, reclassé à mi-temps thérapeutique : 1 300 EUR/mois. Perte annuelle : 10 800 EUR.",
                          calcul: "10 800 EUR x 19,5 (euro de rente, homme 40 ans) = 210 600 EUR capitalisés",
                          indemnisation: "environ 210 000 EUR"
                        },
                        {
                          profil: "Fonctionnaire — Enseignant, 35 ans",
                          situation: "Salaire net : 2 500 EUR/mois. Maladie professionnelle, mise en retraite pour invalidité. Pension : 1 400 EUR/mois. Perte annuelle : 13 200 EUR.",
                          calcul: "13 200 EUR x 22,1 (euro de rente, homme 35 ans) = 291 720 EUR capitalisés",
                          indemnisation: "environ 290 000 EUR"
                        },
                        {
                          profil: "Indépendant — Artisan plombier, 48 ans",
                          situation: "Revenu moyen : 3 500 EUR/mois. TMS invalidant, ne peut plus exercer. Revenu après reconversion : 1 800 EUR/mois. Perte annuelle : 20 400 EUR.",
                          calcul: "20 400 EUR x 15,8 (euro de rente, homme 48 ans) = 322 320 EUR capitalisés",
                          indemnisation: "environ 320 000 EUR"
                        }
                      ].map((ex, i) => (
                        <div key={i} className="p-4 rounded-xl border border-border/50 bg-card">
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                            <h4 className="font-semibold text-sm">{ex.profil}</h4>
                            <Badge variant="outline" className="text-accent border-accent/30 w-fit">{ex.indemnisation}</Badge>
                          </div>
                          <p className="text-xs text-foreground/70 mb-1">{ex.situation}</p>
                          <p className="text-xs text-muted-foreground font-mono bg-muted/50 rounded px-2 py-1 mt-2">{ex.calcul}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Disclaimer */}
                <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20" data-testid="pgpf-disclaimer">
                  <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-amber-800 dark:text-amber-300 leading-relaxed">
                    <strong>Avertissement :</strong> Ces informations sont fournies à titre indicatif et ne constituent pas un conseil juridique. Les montants d'indemnisation dépendent de chaque situation individuelle, des barèmes de capitalisation en vigueur et de l'appréciation des juges. Consultez un professionnel du droit pour une évaluation personnalisée de votre dossier.
                  </p>
                </div>

                {/* CTA */}
                <div className="flex flex-col sm:flex-row gap-3 items-center justify-center pt-2">
                  <Link to="/calculatrice-ipp">
                    <Button variant="outline" className="gap-2">
                      <Activity className="w-4 h-4" /> Calculatrice IPP avec IP et PGPF
                    </Button>
                  </Link>
                  <Link to="/simulateur">
                    <Button className="gap-2">
                      <ArrowRight className="w-4 h-4" /> Analyser votre dossier avec StrategiIA
                    </Button>
                  </Link>
                </div>
              </div>
            </TabsContent>

            {/* ── Tab 4 : Annuaire MDPH ── */}
            <TabsContent value="mdph" data-testid="enc-content-mdph">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-accent" /> Annuaire des MDPH de France
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Trouvez les coordonnées de votre Maison Départementale des Personnes Handicapées.
                    Cliquez sur un département pour voir sa fiche complète.
                  </p>
                </CardHeader>
                <CardContent>
                  <MdphFinder />
                </CardContent>
              </Card>
            </TabsContent>

            {/* ── Tab 5 : Aides MDPH ── */}
            <TabsContent value="aides" data-testid="enc-content-aides">
              <div className="space-y-6">
                {/* CMI */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clipboard className="w-5 h-5 text-accent" /> La Carte Mobilité Inclusion (CMI)
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">
                      Depuis 2017, la CMI remplace les anciennes cartes d'invalidité, de priorité et de stationnement.
                      Elle comporte trois mentions possibles.
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-3 gap-4">
                      {[
                        {
                          type: "CMI Invalidité",
                          condition: "Taux d'incapacité ≥ 80%",
                          avantages: ["Réduction d'impôts (demi-part fiscale supplémentaire)", "Priorité d'accès aux places assises", "Accès prioritaire aux logements sociaux", "Avantages commerciaux divers"],
                          color: "red"
                        },
                        {
                          type: "CMI Priorité",
                          condition: "Station debout pénible, sans atteindre 80% d'incapacité",
                          avantages: ["Priorité dans les files d'attente", "Priorité pour les places assises dans les transports", "Priorité dans les salles d'attente"],
                          color: "blue"
                        },
                        {
                          type: "CMI Stationnement",
                          condition: "Périmètre de marche limité ou nécessité d'un accompagnant",
                          avantages: ["Stationnement gratuit sur toutes les places", "Utilisation des places réservées aux personnes handicapées", "Gratuité du stationnement (12h max)", "Valable dans toute l'Union Européenne"],
                          color: "green"
                        }
                      ].map((carte, i) => (
                        <div key={i} className={`p-5 rounded-xl border-2 border-${carte.color === 'red' ? 'red' : carte.color === 'blue' ? 'blue' : 'green'}-200/50 bg-${carte.color === 'red' ? 'red' : carte.color === 'blue' ? 'blue' : 'green'}-50/30`} data-testid={`cmi-${carte.color}`}>
                          <h4 className="font-semibold text-lg mb-2">{carte.type}</h4>
                          <p className="text-sm text-muted-foreground mb-3 pb-3 border-b border-border/50">
                            <strong>Condition :</strong> {carte.condition}
                          </p>
                          <p className="text-sm font-medium mb-2">Avantages :</p>
                          <ul className="space-y-1.5">
                            {carte.avantages.map((a, j) => (
                              <li key={j} className="text-sm text-muted-foreground flex items-start gap-2">
                                <ChevronRight className="w-3.5 h-3.5 text-accent mt-0.5 flex-shrink-0" />{a}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Aides techniques & PCH */}
                <Card>
                  <CardHeader>
                    <CardTitle>Aides techniques et Prestation de Compensation du Handicap (PCH)</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      La MDPH peut attribuer des aides financières pour compenser votre handicap au quotidien.
                    </p>
                  </CardHeader>
                  <CardContent>
                    <Accordion type="multiple" className="w-full">
                      {[
                        {
                          id: "aide-humaine",
                          title: "Aide humaine",
                          condition: "Difficulté absolue pour au moins 1 activité essentielle, ou difficulté grave pour au moins 2 activités",
                          content: "Financement d'un aidant familial ou d'un service d'aide à domicile pour les actes essentiels (toilette, habillage, alimentation), la surveillance, et les déplacements. Montant variable selon le nombre d'heures attribuées."
                        },
                        {
                          id: "aide-technique",
                          title: "Aides techniques",
                          condition: "Nécessité d'un équipement pour compenser le handicap",
                          content: "Financement d'équipements : fauteuil roulant, prothèses auditives, appareils de verticalisation, aides à la communication, matériel informatique adapté, etc. La PCH prend en charge jusqu'à 75% du coût avec un plafond triennal."
                        },
                        {
                          id: "aménagément-logement",
                          title: "Aménagement du logement",
                          condition: "Nécessité d'adapter le domicile au handicap",
                          content: "Travaux d'accessibilité : rampe d'accès, douche à l'italienne, monte-escalier, élargissement de portes, domotique. Prise en charge jusqu'à 10 000 € sur 10 ans (ou 50% du coût au-delà)."
                        },
                        {
                          id: "aménagément-vehicule",
                          title: "Aménagement du véhicule",
                          condition: "Nécessité d'adapter le véhicule ou surcoût de transport",
                          content: "Adaptation du poste de conduite, boîte automatique, rampe d'accès. Prise en charge jusqu'à 5 000 € sur 5 ans. Surcoûts de transport : 200 €/mois (ou 12 000 € sur 5 ans)."
                        },
                        {
                          id: "aide-animaliere",
                          title: "Aide animalière",
                          condition: "Recours à un animal d'assistance (chien guide, chien d'aide)",
                          content: "Prise en charge des frais liés à l'animal d'assistance : acquisition, entretien, nourriture, soins vétérinaires. Montant forfaitaire de 50 €/mois (3 000 € sur 5 ans)."
                        },
                        {
                          id: "charges-specifiques",
                          title: "Charges spécifiques et exceptionnelles",
                          condition: "Dépenses permanentes ou ponctuelles liées au handicap",
                          content: "Charges spécifiques (récurrentes) : couches, protections, alimentation spéciale — jusqu'à 100 €/mois. Charges exceptionnelles (ponctuelles) : réparation de matériel, frais de formation — jusqu'à 1 800 € sur 3 ans."
                        },
                        {
                          id: "aide-parentalite",
                          title: "Aide à la parentalité",
                          condition: "Parent en situation de handicap, enfant de moins de 7 ans à charge",
                          content: "Soutien financier dédié au parent handicapé pour assumer ses responsabilités éducatives. Aide humaine : 450 €/mois versés à partir des 3 ans du plus jeune enfant et jusqu'à ses 7 ans. Aide technique (3 versements forfaitaires) : 1 200 € aux 3 ans du plus jeune enfant, puis 1 000 € aux 6 ans de chaque enfant."
                        }
                      ].map(aide => (
                        <AccordionItem key={aide.id} value={aide.id} data-testid={`aide-${aide.id}`}>
                          <AccordionTrigger className="text-left hover:no-underline hover:text-accent">
                            <span className="flex items-center gap-2">
                              {aide.title}
                            </span>
                          </AccordionTrigger>
                          <AccordionContent className="space-y-3">
                            <div className="p-3 rounded-lg bg-accent/5 border border-accent/15">
                              <p className="text-sm"><strong>Condition d'attribution :</strong> {aide.condition}</p>
                            </div>
                            <p className="text-sm text-muted-foreground">{aide.content}</p>
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </CardContent>
                </Card>

                {/* AAH & RQTH summary */}
                <div className="grid md:grid-cols-2 gap-4">
                  <Card className="border-accent/20">
                    <CardContent className="p-6">
                      <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                        <Heart className="w-5 h-5 text-accent" /> AAH — Allocation Adultes Handicapés
                      </h3>
                      <p className="text-sm text-muted-foreground mb-3">
                        Aide financière mensuelle (max 1 041,59 €) pour les personnes avec un taux d'incapacité ≥ 80%,
                        ou 50-79% avec restriction substantielle d'accès à l'emploi.
                      </p>
                      <Link to="/calculatrice-aah" className="text-sm text-accent font-medium hover:underline flex items-center gap-1">
                        Estimer votre AAH <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </CardContent>
                  </Card>
                  <Card className="border-accent/20">
                    <CardContent className="p-6">
                      <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                        <Users className="w-5 h-5 text-accent" /> RQTH — Travailleur Handicapé
                      </h3>
                      <p className="text-sm text-muted-foreground mb-3">
                        Reconnaissance ouvrant des droits en emploi : aménagement de poste, priorité à l'embauche,
                        accès à des dispositifs spécifiques (Cap Emploi, AGEFIPH, FIPHFP).
                      </p>
                      <Link to="/mdph" className="text-sm text-accent font-medium hover:underline flex items-center gap-1">
                        En savoir plus <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      {/* Guides Section */}
      <section className="section-padding" id="guides">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Guides pratiques</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">Par où commencer ?</h2>
          </div>
          <div className="grid lg:grid-cols-3 gap-6">
            {guides.map((guide, i) => (
              <Card key={i} className="border-border" data-testid={`guide-${i}`}>
                <CardHeader>
                  <guide.icon className="w-10 h-10 text-accent mb-4" strokeWidth={1.5} />
                  <CardTitle className="text-xl">{guide.title}</CardTitle>
                  <p className="text-sm text-muted-foreground">{guide.description}</p>
                </CardHeader>
                <CardContent>
                  <ol className="space-y-3">
                    {guide.points.map((p, j) => (
                      <li key={j} className="flex items-start gap-3">
                        <span className="flex-shrink-0 w-6 h-6 bg-muted rounded-full flex items-center justify-center text-sm font-medium text-muted-foreground">{j + 1}</span>
                        <span className="text-sm">{p}</span>
                      </li>
                    ))}
                  </ol>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="section-padding bg-card" id="faq">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <HelpCircle className="w-12 h-12 text-accent mx-auto mb-4" strokeWidth={1.5} />
            <span className="text-sm font-medium text-accent uppercase tracking-wider">FAQ</span>
            <h2 className="text-3xl sm:text-4xl font-semibold mt-2 mb-4">Questions fréquentes</h2>
          </div>
          {loading ? (
            <div className="text-center text-muted-foreground" data-testid="faq-loading">Chargement...</div>
          ) : (
            <Tabs defaultValue="AT/MP" className="w-full" data-testid="faq-tabs">
              <TabsList className="w-full flex-wrap h-auto gap-2 bg-muted/50 p-2 rounded-xl mb-8">
                {categories.map(c => (
                  <TabsTrigger key={c} value={c} className="flex-1 min-w-0 rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-sm" data-testid={`faq-tab-${c.toLowerCase().replace('/', '-')}`}>
                    {c}
                  </TabsTrigger>
                ))}
              </TabsList>
              {categories.map(c => (
                <TabsContent key={c} value={c}>
                  <Accordion type="single" collapsible className="w-full">
                    {getFaqsByCategory(c).map((faq, i) => (
                      <AccordionItem key={faq.id} value={faq.id} className="border-border" data-testid={`faq-item-${i}`}>
                        <AccordionTrigger className="text-left hover:no-underline hover:text-accent">{faq.question}</AccordionTrigger>
                        <AccordionContent className="text-muted-foreground">{faq.reponse}</AccordionContent>
                      </AccordionItem>
                    ))}
                    {getFaqsByCategory(c).length === 0 && <p className="text-muted-foreground text-center py-8">Aucune question dans cette catégorie.</p>}
                  </Accordion>
                </TabsContent>
              ))}
            </Tabs>
          )}
        </div>
      </section>

      {/* PDF Library with Email Gate */}
      <section className="section-padding" id="bibliotheque">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 sm:mb-12">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Bibliothèque</span>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold mt-2 mb-4">Guides PDF téléchargeables</h2>
            <p className="text-sm text-muted-foreground max-w-2xl">Recevez gratuitement nos guides pratiques par email. Chaque guide est conçu pour vous accompagner concrètement dans vos démarches.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {[
              { id: 'guide_mp', title: "Déclarer une maladie professionnelle", description: "Feuille de route complète : éligibilité, CMI, dossier CPAM, instruction et indemnisation.", category: "Maladie professionnelle" },
              { id: 'guide_expertise', title: "Se préparer à une expertise médicale", description: "Check-list complète : documents, doléances, accompagnement et suivi post-expertise.", category: "Expertise médicale" },
              { id: 'guide_mdph', title: "Constituer un dossier MDPH", description: "Formulaires, projet de vie, certificat médical et stratégie de recours.", category: "MDPH" },
              { id: 'guide_recours', title: "Contester un refus", description: "Stratégie étape par étape : CRA, RAPO, médiateur et tribunal judiciaire.", category: "Recours" },
              { id: 'guide_ipp', title: "Comprendre le taux d'IPP", description: "Barème 2025, calcul de la rente, exemples concrets et contestation.", category: "Accident du travail" },
              { id: 'guide_assurance', title: "Activer sa protection juridique", description: "Où trouver sa PJ, déclaration du litige, choix de l'avocat et plafonds.", category: "Assurances" }
            ].map(g => (
              <GuideCard key={g.id} guide={g} />
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="section-padding bg-foreground text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <BookOpen className="w-12 h-12 text-accent mx-auto mb-6" strokeWidth={1.5} />
          <h2 className="text-3xl sm:text-4xl font-semibold mb-6">Une question spécifique ?</h2>
          <p className="text-primary-foreground/70 mb-8 max-w-2xl mx-auto">
            Ces ressources sont générales. Votre situation est unique et mérite une analyse personnalisée.
          </p>
          <Link to="/contact">
            <Button size="lg" className="rounded-full px-8 gap-2 bg-accent hover:bg-accent/90 text-accent-foreground" data-testid="resources-cta-button">
              Me poser votre question <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </main>
  );
};
