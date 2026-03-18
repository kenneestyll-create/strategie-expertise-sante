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

### Dossier Express IA (PAYANT — 97 EUR)
- Score de solidite du dossier (XX/100) avec ring SVG anime
- 3 metriques cles : Completude, Qualite, Coherence
- Points de fragilite, alertes de risque, predictions
- Actions recommandees priorisees (max 3)

## Fonctionnalites implementees

### Scanner Documents CamScanner-like — Architecture DEFINITIVE (Mar 2026)
- **Architecture:** Worker OffscreenCanvas stateful + Hook fonctionnel simple
  - Worker: `/app/frontend/public/workers/scanner.worker.js`
  - Hook: `/app/frontend/src/hooks/useScannerWorker.js` (cache-busting URL)
  - Composant: `/app/frontend/src/components/DocumentScanner.jsx`
  - OpenCV.js: `/app/frontend/public/workers/opencv.js` (12MB, self-hosted, opencv-js-wasm@5.0.0)
- **Worker stateful:**
  - `scan`: createImageBitmap + OffscreenCanvas, stocke originalImage
  - `filter`: bw (binarize), enhanced (adjustContrast), original
  - `rotate`: left/right via rotateCanvas helper
  - `save`: convertToBlob JPEG 0.95
  - `ready`: emis apres chargement OpenCV.js (cvReady flag)
  - Preview envoie ArrayBuffer transferable + dimensions (width/height)
- **Auto-Crop OpenCV.js (CORRIGE - Mars 2026):**
  - Chargement local de OpenCV.js via importScripts (evite CORS)
  - Downscale pour detection rapide (max 800px), transform a pleine resolution
  - Canny edge detection multi-seuils (75/200, 50/150, 30/100)
  - findContours + approxPolyDP avec epsilon adaptatif
  - getPerspectiveTransform + warpPerspective pour redresser le document
  - Fonctionne pour camera ET import fichier (autoCrop=true)
  - Teste avec image realiste : 1920x1440 -> 1308x1089 (document isole du fond bois)
- **Hook simplifie:**
  - Pas de classe MobileScanner, juste useRef + useState
  - previewUrl, previewSize (dimensions 1:1), isReady, isProcessing
  - scan(), filter(), rotate(), save(), reset()
  - Cache-busting: `?v=${Date.now()}` sur l'URL du worker
- **Tests:** 8/8 passes (iteration 87)

### Securite, Conversion, Partenaires, etc.
- (Voir sessions precedentes pour details)

## Taches a venir
- **P1:** Outil de recadrage manuel comme fallback si auto-crop echoue
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
- OpenCV.js (opencv-js-wasm@5.0.0, self-hosted)
