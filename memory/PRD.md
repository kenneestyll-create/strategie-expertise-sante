# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles et les litiges d'assurance.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral (Manrope + Playfair Display)
- **Integrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), apscheduler, fpdf2, slowapi

## Services — Separation gratuit/payant

### StrategiIA (GRATUIT)
- Formulaire simple : type de dossier + regime + situation
- Analyse IA basique (Claude Sonnet 4.5)
- Resultat textuel avec email gate pour rapport complet
- Bouton "Analyser mon dossier gratuitement"

### Dossier Express IA (PAYANT — 97EUR)
- Score de solidite du dossier (XX/100) avec ring SVG anime
- 3 metriques cles : Completude, Qualite, Coherence
- Points de fragilite, alertes de risque, predictions
- Actions recommandees priorisees (max 3)
- Indicateur navbar compact — uniquement pour clients payants
- **Gating:** Clients sans Dossier Express IA voient un teaser floute avec CTA

## Fonctionnalites implementees

### Scanner Documents CamScanner-like — Architecture DEFINITIVE (Mar 2026)
- **Architecture:** Web Worker + OffscreenCanvas (non-bloquant)
  - Worker stateful: `/app/frontend/public/workers/scanner.worker.js`
  - Hook React: `/app/frontend/src/hooks/useScannerWorker.js` (classe MobileScanner)
  - Composant: `/app/frontend/src/components/DocumentScanner.jsx`
- **Traitement dans le Worker:**
  - `scan`: createImageBitmap + OffscreenCanvas, stocke originalImageData
  - `filter`: bw (binarize), enhanced (adjustContrast), original
  - `rotate`: left/right via OffscreenCanvas transform
  - `save`: convertToBlob JPEG quality 0.95
- **Mode Simple/Avance:**
  - Simple (defaut): capture photo + Valider uniquement, aucun filtre/rotation visible
  - Avance: filtres (N&B, Contraste+, Original), rotation, multi-pages
  - Bascule via toggle en guide ou bouton "Mode avance" en preview
- **UI:** Guide -> Camera (requestAnimationFrame) -> Processing -> Preview -> Pages/PDF
- **Tests:** 20/20 passes (iteration 81)
- **Fichiers supprimes:** scannerEngine.js, opencvLoader.js, public/scanner.worker.js (ancien)

### Audit de Securite Complet (Mar 2026)
- JWT Secret obligatoire depuis env var
- Paiement securise (verification DB + fallback live Stripe + webhook cross-update)
- Rate Limiting 5/min sur endpoints d'authentification
- Uploads securises (MIME whitelist + extensions + 10Mo + scan signatures)
- CORS strict depuis ALLOWED_ORIGINS
- Documents securises (auth + propriete)
- Headers de securite

### Optimisation Tunnel de Conversion Dossier Express IA (Mar 2026)
- Landing page refonte avec compteur hebdomadaire, temoignages, CTA
- Formulaire avec indicateur de progression, sidebar valeur, options upsell
- Preparation Stripe production (STRIPE_MODE auto-detecte)

### Section Partenaires Footer (Mar 2026)

## Taches a venir
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test mode)
- PayPal (test mode)
- Claude Sonnet 4.5 (Emergent LLM Key)
- Resend (sandbox)
- HubSpot (partiellement, en attente credentials)
