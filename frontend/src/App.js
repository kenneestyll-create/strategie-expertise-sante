import "@/App.css";
import { lazy, Suspense, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { Toaster } from "@/components/ui/sonner";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ChatBot } from "@/components/ChatBot";
import { AlerteUrgente } from "@/components/AlerteUrgente";
import { StrategiIAFab } from "@/components/StrategiIAFab";
import { AuthProvider } from "@/context/AuthContext";
import { ForumAuthProvider } from "@/context/ForumAuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { ScrollToTop } from "@/components/ScrollToTop";
import { useSearchHighlight } from "@/hooks/useSearchHighlight";

const SearchHighlighter = () => { useSearchHighlight(); return null; };

const SITE_URL = "https://scanner-fix-5.preview.emergentagent.com";

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

const faqPageSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Comment faire reconnaître une maladie professionnelle ?",
      "acceptedAnswer": { "@type": "Answer", "text": "La reconnaissance d'une maladie professionnelle passe par une déclaration auprès de la CPAM avec un certificat médical initial. La maladie doit figurer dans un tableau de maladies professionnelles ou être reconnue par le CRRMP." }
    },
    {
      "@type": "Question",
      "name": "Qu'est-ce que le taux d'IPP ?",
      "acceptedAnswer": { "@type": "Answer", "text": "Le taux d'Incapacité Permanente Partielle (IPP) évalue les séquelles définitives d'un accident du travail ou d'une maladie professionnelle. Il détermine le montant de l'indemnisation versée par la CPAM." }
    },
    {
      "@type": "Question",
      "name": "Comment constituer un dossier MDPH ?",
      "acceptedAnswer": { "@type": "Answer", "text": "Le dossier MDPH nécessite le formulaire Cerfa, un certificat médical récent, des justificatifs d'identité et de domicile, ainsi que tout document médical pertinent. Un accompagnement professionnel peut optimiser vos chances." }
    },
    {
      "@type": "Question",
      "name": "Combien coûte un accompagnement en maladie professionnelle ?",
      "acceptedAnswer": { "@type": "Answer", "text": "Les tarifs varient de la pré-analyse gratuite assistée par StratégiIA au Dossier Express IA à 97€, jusqu'à l'accompagnement complet à 500€. Le premier échange est toujours gratuit et sans engagement." }
    }
  ]
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
const ReferralPage = lazy(() => import("@/pages/ReferralPage").then(m => ({ default: m.ReferralPage })));
const AgendaPage = lazy(() => import("@/pages/AgendaPage").then(m => ({ default: m.AgendaPage })));
const SimulateurPage = lazy(() => import("@/pages/SimulateurPage").then(m => ({ default: m.SimulateurPage })));
const EspaceClientPage = lazy(() => import("@/pages/EspaceClientPage").then(m => ({ default: m.EspaceClientPage })));
const CalculatriceIPPPage = lazy(() => import("@/pages/CalculatriceIPPPage").then(m => ({ default: m.CalculatriceIPPPage })));
const CalculatriceAAHPage = lazy(() => import("@/pages/CalculatriceAAHPage").then(m => ({ default: m.CalculatriceAAHPage })));
const DossierExpressPage = lazy(() => import("@/pages/DossierExpressPage").then(m => ({ default: m.DossierExpressPage })));
const ForumPage = lazy(() => import("@/pages/ForumPage").then(m => ({ default: m.ForumPage })));
const ForumRegisterPage = lazy(() => import("@/pages/ForumRegisterPage").then(m => ({ default: m.ForumRegisterPage })));
const ForumLoginPage = lazy(() => import("@/pages/ForumLoginPage").then(m => ({ default: m.ForumLoginPage })));
const ForumCategoryPage = lazy(() => import("@/pages/ForumCategoryPage").then(m => ({ default: m.ForumCategoryPage })));
const ForumTopicPage = lazy(() => import("@/pages/ForumTopicPage").then(m => ({ default: m.ForumTopicPage })));
const ForumNewTopicPage = lazy(() => import("@/pages/ForumNewTopicPage").then(m => ({ default: m.ForumNewTopicPage })));

const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
  </div>
);

function App() {
  useEffect(() => {
    const schemas = [professionalServiceSchema, faqPageSchema, webSiteSchema];
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
          <ForumAuthProvider>
            <BrowserRouter>
              <ScrollToTop />
              <SearchHighlighter />
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
                  <Route path="/politique-confidentialite" element={<><Header /><PolitiqueConfidentialitePage /><Footer /></>} />
                  <Route path="/parrainage" element={<><Header /><ReferralPage /><Footer /></>} />
                  <Route path="/agenda" element={<><Header /><AgendaPage /><Footer /></>} />
                  <Route path="/simulateur" element={<><Header /><SimulateurPage /><Footer /></>} />
                  <Route path="/espace-client" element={<><Header /><EspaceClientPage /><Footer /></>} />
                  <Route path="/calculatrice-ipp" element={<><Header /><CalculatriceIPPPage /><Footer /></>} />
                  <Route path="/calculatrice-aah" element={<><Header /><CalculatriceAAHPage /><Footer /></>} />
                  <Route path="/dossier-express" element={<><Header /><DossierExpressPage /><Footer /></>} />
                  <Route path="/forum" element={<><Header /><ForumPage /><Footer /></>} />
                  <Route path="/forum/inscription" element={<><Header /><ForumRegisterPage /><Footer /></>} />
                  <Route path="/forum/connexion" element={<><Header /><ForumLoginPage /><Footer /></>} />
                  <Route path="/forum/categorie/:slug" element={<><Header /><ForumCategoryPage /><Footer /></>} />
                  <Route path="/forum/sujet/:topicId" element={<><Header /><ForumTopicPage /><Footer /></>} />
                  <Route path="/forum/nouveau" element={<><Header /><ForumNewTopicPage /><Footer /></>} />
                  <Route path="/forum/tous" element={<><Header /><ForumCategoryPage /><Footer /></>} />
                  <Route path="/admin/login" element={<AdminLoginPage />} />
                  <Route path="/admin" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />
                </Routes>
              </Suspense>
              <ChatBot />
              <StrategiIAFab />
              <AlerteUrgente />
              <Toaster position="top-right" richColors />
            </BrowserRouter>
          </ForumAuthProvider>
        </AuthProvider>
      </div>
    </HelmetProvider>
  );
}

export default App;
