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
import { TarifsPage } from "@/pages/TarifsPage";
import { ProtectionJuridiquePage } from "@/pages/ProtectionJuridiquePage";
import { PartenairesPage } from "@/pages/PartenairesPage";
import { AvisPage } from "@/pages/AvisPage";
import { ResourcesPage } from "@/pages/ResourcesPage";
import { ContactPage } from "@/pages/ContactPage";
import { AdminLoginPage } from "@/pages/AdminLoginPage";
import { AdminDashboard } from "@/pages/AdminDashboard";

// Components
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { AuthProvider } from "@/context/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";

function App() {
  return (
    <div className="App grain-texture">
      <AuthProvider>
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
            
            {/* Admin Routes */}
            <Route path="/admin/login" element={<AdminLoginPage />} />
            <Route path="/admin" element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            } />
          </Routes>
          <Toaster position="top-right" richColors />
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;
