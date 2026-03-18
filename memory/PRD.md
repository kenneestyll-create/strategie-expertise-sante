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
  - Hook: `/app/frontend/src/hooks/useScannerWorker.js` (pas de classe, useRef/useState)
  - Composant: `/app/frontend/src/components/DocumentScanner.jsx`
- **Worker stateful:**
  - `scan`: createImageBitmap + OffscreenCanvas, stocke originalImage
  - `filter`: bw (binarize), enhanced (adjustContrast), original
  - `rotate`: left/right via rotateCanvas helper
  - `save`: convertToBlob JPEG 0.95
  - `ready`: emis a l'init pour signaler que le Worker est pret
  - Preview envoie ArrayBuffer transferable + dimensions (width/height)
- **Hook simplifie:**
  - Pas de classe MobileScanner, juste useRef + useState
  - previewUrl, previewSize (dimensions 1:1), isReady, isProcessing
  - scan(), filter(), rotate(), save(), reset()
- **Composant propre:**
  - Canvas 1:1 (dimensions exactes de la photo, pas de reduction)
  - Controles TOUJOURS hors du canvas (jamais superposes)
  - Mode simple (capture + valider) / avance (filtres, rotation, multi-pages)
  - Mode avance par defaut (isSimpleMode=false)
  - Toggle bidirectionnel guide + preview
  - Worker 'ready' conditionne l'affichage toolbar avance
- **Tests:** 30/30 passes (iteration 84)
- **Fichiers supprimes:** scannerEngine.js, opencvLoader.js, public/scanner.worker.js (ancien)

### Securite, Conversion, Partenaires, etc.
- (Voir sessions precedentes pour details)

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
