import "@/App.css";
import { lazy, Suspense, useEffect } from "react";
import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { Toaster } from "@/components/ui/sonner";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ChatBot } from "@/components/ChatBot";
import { AlerteUrgente } from "@/components/AlerteUrgente";
import { MascotteStrate } from "@/components/MascotteStrate";
import { ExitIntentPopup } from "@/components/ExitIntentPopup";
import { StrategiIA } from "@/components/StrategiIA";
import { AuthProvider } from "@/context/AuthContext";
import { VipProvider } from "@/context/VipContext";
import { AdminTestProvider } from "@/components/AdminTestBanner";
import { ForumAuthProvider } from "@/context/ForumAuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { ScrollToTop } from "@/components/ScrollToTop";
import { useSearchHighlight } from "@/hooks/useSearchHighlight";
import { useContentProtection } from "@/hooks/useContentProtection";

const SearchHighlighter = () => { useSearchHighlight(); return null; };
const ContentProtectionGuard = () => { useContentProtection(); return null; };
const HideOnAdmin = ({ children }) => { const { pathname } = useLocation(); return pathname.startsWith('/admin') ? null : children; };

const SITE_URL = process.env.REACT_APP_SITE_URL || process.env.REACT_APP_BACKEND_URL || "";

const professionalServiceSchema = {
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "Stratégie & Expertise Santé",
  "description": "Conseil et accompagnement expert en maladie professionnelle, accident du travail, MDPH, expertise médicale et protection juridique.",
  "url": SITE_URL,
  "areaServed": { "@type": "Country", "name": "France" },
  "serviceType": ["Conseil en santé au travail", "Accompagnement MDPH", "Expertise médicale", "Protection juridique", "Analyse de dossier AT/MP"],
  "priceRange": "€€",
  "knowsAbout": ["Maladie professionnelle", "Accident du travail", "MDPH", "IPP", "AAH", "Expertise médicale", "Protection juridique", "Faute inexcusable"],
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Prestations",
    "itemListElement": [
      { "@type": "Offer", "name": "Pré-analyse StratégiIA", "price": "0", "priceCurrency": "EUR", "description": "Pré-analyse assistée par notre outil StratégiIA" },
      { "@type": "Offer", "name": "Dossier Express IA", "price": "97", "priceCurrency": "EUR", "description": "Rapport PDF complet livré sous 2h" },
      { "@type": "Offer", "name": "Analyse de dossier", "price": "150", "priceCurrency": "EUR", "description": "Étude personnalisée du dossier médical et administratif" },
      { "@type": "Offer", "name": "Accompagnement complet", "price": "500", "priceCurrency": "EUR", "description": "Suivi global des démarches" }
    ]
  }
};

const webSiteSchema = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Stratégie & Expertise Santé",
  "url": SITE_URL,
  "potentialAction": {
    "@type": "SearchAction",
    "target": `${SITE_URL}/ressources?q={search_term_string}`,
    "query-input": "required name=search_term_string"
  }
};

// Lazy-loaded pages
const HomePage = lazy(() => import("@/pages/HomePage").then(m => ({ default: m.HomePage })));
const AboutPage = lazy(() => import("@/pages/AboutPage").then(m => ({ default: m.AboutPage })));
const ServicesPage = lazy(() => import("@/pages/ServicesPage").then(m => ({ default: m.ServicesPage })));
const ExpertiseMedicalePage = lazy(() => import("@/pages/ExpertiseMedicalePage").then(m => ({ default: m.ExpertiseMedicalePage })));
const AccidentTravailPage = lazy(() => import("@/pages/AccidentTravailPage").then(m => ({ default: m.AccidentTravailPage })));
const MDPHPage = lazy(() => import("@/pages/MDPHPage").then(m => ({ default: m.MDPHPage })));
const SeminairesPage = lazy(() => import("@/pages/SeminairesPage").then(m => ({ default: m.SeminairesPage })));
const EntreprisesPage = lazy(() => import("@/pages/EntreprisesPage").then(m => ({ default: m.EntreprisesPage })));
const ProtectionJuridiquePage = lazy(() => import("@/pages/ProtectionJuridiquePage").then(m => ({ default: m.ProtectionJuridiquePage })));
const TarifsPage = lazy(() => import("@/pages/TarifsPage").then(m => ({ default: m.TarifsPage })));
const PartenairesPage = lazy(() => import("@/pages/PartenairesPage").then(m => ({ default: m.PartenairesPage })));
const AvisPage = lazy(() => import("@/pages/AvisPage").then(m => ({ default: m.AvisPage })));
const ResourcesPage = lazy(() => import("@/pages/ResourcesPage").then(m => ({ default: m.ResourcesPage })));
const ContactPage = lazy(() => import("@/pages/ContactPage").then(m => ({ default: m.ContactPage })));
const MentionsLegalesPage = lazy(() => import("@/pages/MentionsLegalesPage").then(m => ({ default: m.MentionsLegalesPage })));
const PolitiqueConfidentialitePage = lazy(() => import("@/pages/PolitiqueConfidentialitePage"));
const AdminLoginPage = lazy(() => import("@/pages/AdminLoginPage").then(m => ({ default: m.AdminLoginPage })));
const AdminDashboard = lazy(() => import("@/pages/AdminDashboard").then(m => ({ default: m.AdminDashboard })));
const V5PhaseATest = lazy(() => import("@/pages/V5PhaseATest"));
const ReferralPage = lazy(() => import("@/pages/ReferralPage").then(m => ({ default: m.ReferralPage })));
const AgendaPage = lazy(() => import("@/pages/AgendaPage").then(m => ({ default: m.AgendaPage })));
const SimulateurPage = lazy(() => import("@/pages/SimulateurHubPage"));
const SimulateurIPPAccidentTravailPreviewPage = lazy(() => import("@/pages/SimulateurIPPAccidentTravailPreviewPage"));
const SimulateurMaladieProfessionnellePreviewPage = lazy(() => import("@/pages/SimulateurMaladieProfessionnellePreviewPage"));
const EspaceClientPage = lazy(() => import("@/pages/EspaceClientPage").then(m => ({ default: m.EspaceClientPage })));
const CalculatriceIPPPage = lazy(() => import("@/pages/CalculatriceIPPPage").then(m => ({ default: m.CalculatriceIPPPage })));
const CalculatriceAAHPage = lazy(() => import("@/pages/CalculatriceAAHPage").then(m => ({ default: m.CalculatriceAAHPage })));
const DossierExpressPage = lazy(() => import("@/pages/DossierExpressPage").then(m => ({ default: m.DossierExpressPage })));
const SuiviDossierPage = lazy(() => import("@/pages/SuiviDossierPage").then(m => ({ default: m.SuiviDossierPage })));
const ForumPage = lazy(() => import("@/pages/ForumPage").then(m => ({ default: m.ForumPage })));
const ForumRegisterPage = lazy(() => import("@/pages/ForumRegisterPage").then(m => ({ default: m.ForumRegisterPage })));
const ForumLoginPage = lazy(() => import("@/pages/ForumLoginPage").then(m => ({ default: m.ForumLoginPage })));
const ForumCategoryPage = lazy(() => import("@/pages/ForumCategoryPage").then(m => ({ default: m.ForumCategoryPage })));
const ForumTopicPage = lazy(() => import("@/pages/ForumTopicPage").then(m => ({ default: m.ForumTopicPage })));
const ForumNewTopicPage = lazy(() => import("@/pages/ForumNewTopicPage").then(m => ({ default: m.ForumNewTopicPage })));
const MedecinConseilPage = lazy(() => import("@/pages/MedecinConseilPage"));
const GuidePage = lazy(() => import("@/pages/GuidePage"));
const GuidesPratiquesPage = lazy(() => import("@/pages/GuidesPratiquesPage"));
const VipAccessPage = lazy(() => import("@/pages/VipAccessPage"));

const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
  </div>
);

function App() {
  useEffect(() => {
    const schemas = [professionalServiceSchema, webSiteSchema];
    const scriptElements = schemas.map(schema => {
      const script = document.createElement('script');
      script.type = 'application/ld+json';
      script.textContent = JSON.stringify(schema);
      document.head.appendChild(script);
      return script;
    });
    return () => scriptElements.forEach(s => s.remove());
  }, []);

  return (
    <HelmetProvider>
      <div className="App grain-texture">
        <AuthProvider>
          <VipProvider>
          <AdminTestProvider>
          <ForumAuthProvider>
            <BrowserRouter>
              <ScrollToTop />
              <SearchHighlighter />
              <ContentProtectionGuard />
              <Suspense fallback={<PageLoader />}>
                <Routes>
                  <Route path="/" element={<><Header /><HomePage /><Footer /></>} />
                  <Route path="/a-propos" element={<><Header /><AboutPage /><Footer /></>} />
                  <Route path="/accompagnements" element={<><Header /><ServicesPage /><Footer /></>} />
                  <Route path="/expertise-medicale" element={<><Header /><ExpertiseMedicalePage /><Footer /></>} />
                  <Route path="/accident-travail-maladie-professionnelle" element={<><Header /><AccidentTravailPage /><Footer /></>} />
                  <Route path="/mdph" element={<><Header /><MDPHPage /><Footer /></>} />
                  <Route path="/seminaires" element={<><Header /><SeminairesPage /><Footer /></>} />
                  <Route path="/entreprises" element={<><Header /><EntreprisesPage /><Footer /></>} />
                  <Route path="/protection-juridique" element={<><Header /><ProtectionJuridiquePage /><Footer /></>} />
                  <Route path="/tarifs" element={<><Header /><TarifsPage /><Footer /></>} />
                  <Route path="/partenaires" element={<><Header /><PartenairesPage /><Footer /></>} />
                  <Route path="/avis" element={<><Header /><AvisPage /><Footer /></>} />
                  <Route path="/ressources" element={<><Header /><ResourcesPage /><Footer /></>} />
                  <Route path="/contact" element={<><Header /><ContactPage /><Footer /></>} />
                  <Route path="/mentions-legales" element={<><Header /><MentionsLegalesPage /><Footer /></>} />
                  <Route path="/cgv" element={<><Header /><MentionsLegalesPage /><Footer /></>} />
                  <Route path="/politique-confidentialite" element={<><Header /><PolitiqueConfidentialitePage /><Footer /></>} />
                  <Route path="/parrainage" element={<><Header /><ReferralPage /><Footer /></>} />
                  <Route path="/agenda" element={<><Header /><AgendaPage /><Footer /></>} />
                  <Route path="/rdv" element={<><Header /><AgendaPage /><Footer /></>} />
                  <Route path="/simulateur" element={<><Header /><SimulateurPage /><Footer /></>} />
                  <Route path="/simulateur-rente-ipp-accident-travail-preview" element={<><Header /><SimulateurIPPAccidentTravailPreviewPage /><Footer /></>} />
                  <Route path="/simulateur-rente-maladie-professionnelle-preview" element={<><Header /><SimulateurMaladieProfessionnellePreviewPage /><Footer /></>} />
                  <Route path="/espace-client" element={<><Header /><EspaceClientPage /><Footer /></>} />
                  <Route path="/calculatrice-ipp" element={<><Header /><CalculatriceIPPPage /><Footer /></>} />
                  <Route path="/calculatrice-aah" element={<><Header /><CalculatriceAAHPage /><Footer /></>} />
                  <Route path="/dossier-express" element={<><Header /><DossierExpressPage /><Footer /></>} />
                  <Route path="/strategiia" element={<Navigate to="/?open=strategiia" replace />} />
                  <Route path="/dossier-express/suivi" element={<><Header /><SuiviDossierPage /><Footer /></>} />
                  <Route path="/forum" element={<><Header /><ForumPage /><Footer /></>} />
                  <Route path="/forum/inscription" element={<><Header /><ForumRegisterPage /><Footer /></>} />
                  <Route path="/forum/connexion" element={<><Header /><ForumLoginPage /><Footer /></>} />
                  <Route path="/forum/categorie/:slug" element={<><Header /><ForumCategoryPage /><Footer /></>} />
                  <Route path="/forum/sujet/:topicId" element={<><Header /><ForumTopicPage /><Footer /></>} />
                  <Route path="/forum/nouveau" element={<><Header /><ForumNewTopicPage /><Footer /></>} />
                  <Route path="/forum/tous" element={<><Header /><ForumCategoryPage /><Footer /></>} />
                  <Route path="/medecin-conseil" element={<><Header /><MedecinConseilPage /><Footer /></>} />
                  <Route path="/guide/:slug" element={<><Header /><GuidePage /><Footer /></>} />
                  <Route path="/guides-pratiques" element={<><Header /><GuidesPratiquesPage /><Footer /></>} />
                  <Route path="/acces-invite" element={<><Header /><VipAccessPage /><Footer /></>} />
                  <Route path="/admin/login" element={<AdminLoginPage />} />
                  <Route path="/admin" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />
                  <Route path="/admin/v5-phaseA-test" element={<ProtectedRoute><V5PhaseATest /></ProtectedRoute>} />
                </Routes>
              </Suspense>
              <HideOnAdmin>
                <ChatBot />
                <StrategiIA />
                <AlerteUrgente />
                <MascotteStrate />
              </HideOnAdmin>
              <ExitIntentPopup />
              <Toaster position="top-right" richColors />
            </BrowserRouter>
          </ForumAuthProvider>
          </AdminTestProvider>
          </VipProvider>
        </AuthProvider>
      </div>
    </HelmetProvider>
  );
}

export default App;
