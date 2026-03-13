import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";

// Pages
import { HomePage } from "@/pages/HomePage";
import { AboutPage } from "@/pages/AboutPage";
import { ServicesPage } from "@/pages/ServicesPage";
import { ExpertiseMedicalePage } from "@/pages/ExpertiseMedicalePage";
import { AccidentTravailPage } from "@/pages/AccidentTravailPage";
import { MDPHPage } from "@/pages/MDPHPage";
import { SeminairesPage } from "@/pages/SeminairesPage";
import { EntreprisesPage } from "@/pages/EntreprisesPage";
import { ProtectionJuridiquePage } from "@/pages/ProtectionJuridiquePage";
import { TarifsPage } from "@/pages/TarifsPage";
import { PartenairesPage } from "@/pages/PartenairesPage";
import { AvisPage } from "@/pages/AvisPage";
import { ResourcesPage } from "@/pages/ResourcesPage";
import { ContactPage } from "@/pages/ContactPage";
import { MentionsLegalesPage } from "@/pages/MentionsLegalesPage";
import { AdminLoginPage } from "@/pages/AdminLoginPage";
import { AdminDashboard } from "@/pages/AdminDashboard";
import { ReferralPage } from "@/pages/ReferralPage";
import { AgendaPage } from "@/pages/AgendaPage";
import { SimulateurPage } from "@/pages/SimulateurPage";
import { EspaceClientPage } from "@/pages/EspaceClientPage";
import { CalculatriceIPPPage } from "@/pages/CalculatriceIPPPage";
import { CalculatriceAAHPage } from "@/pages/CalculatriceAAHPage";
import { DossierExpressPage } from "@/pages/DossierExpressPage";

// Forum Pages
import { ForumPage } from "@/pages/ForumPage";
import { ForumRegisterPage } from "@/pages/ForumRegisterPage";
import { ForumLoginPage } from "@/pages/ForumLoginPage";
import { ForumCategoryPage } from "@/pages/ForumCategoryPage";
import { ForumTopicPage } from "@/pages/ForumTopicPage";
import { ForumNewTopicPage } from "@/pages/ForumNewTopicPage";

// Components
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ChatBot } from "@/components/ChatBot";
import { AlerteUrgente } from "@/components/AlerteUrgente";
import { AuthProvider } from "@/context/AuthContext";
import { ForumAuthProvider } from "@/context/ForumAuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";

function App() {
  return (
    <div className="App grain-texture">
      <AuthProvider>
        <ForumAuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Public Routes */}
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
              <Route path="/parrainage" element={<><Header /><ReferralPage /><Footer /></>} />
              <Route path="/agenda" element={<><Header /><AgendaPage /><Footer /></>} />
              <Route path="/simulateur" element={<><Header /><SimulateurPage /><Footer /></>} />
              <Route path="/espace-client" element={<><Header /><EspaceClientPage /><Footer /></>} />
              <Route path="/calculatrice-ipp" element={<><Header /><CalculatriceIPPPage /><Footer /></>} />
              <Route path="/calculatrice-aah" element={<><Header /><CalculatriceAAHPage /><Footer /></>} />
              <Route path="/dossier-express" element={<><Header /><DossierExpressPage /><Footer /></>} />
              
              {/* Forum Routes */}
              <Route path="/forum" element={<><Header /><ForumPage /><Footer /></>} />
              <Route path="/forum/inscription" element={<><Header /><ForumRegisterPage /><Footer /></>} />
              <Route path="/forum/connexion" element={<><Header /><ForumLoginPage /><Footer /></>} />
              <Route path="/forum/categorie/:slug" element={<><Header /><ForumCategoryPage /><Footer /></>} />
              <Route path="/forum/sujet/:topicId" element={<><Header /><ForumTopicPage /><Footer /></>} />
              <Route path="/forum/nouveau" element={<><Header /><ForumNewTopicPage /><Footer /></>} />
              <Route path="/forum/tous" element={<><Header /><ForumCategoryPage /><Footer /></>} />
              
              {/* Admin Routes */}
              <Route path="/admin/login" element={<AdminLoginPage />} />
              <Route path="/admin" element={
                <ProtectedRoute>
                  <AdminDashboard />
                </ProtectedRoute>
              } />
            </Routes>
            
            {/* Global Chatbot */}
            <ChatBot />
            <AlerteUrgente />
            
            <Toaster position="top-right" richColors />
          </BrowserRouter>
        </ForumAuthProvider>
      </AuthProvider>
    </div>
  );
}

export default App;
