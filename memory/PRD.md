# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)
- **Integrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox)

## Moteur de Recherche (Mar 2026) — AMELIORE
- Fichier: `/app/frontend/src/data/searchIndex.js`
- UI: `/app/frontend/src/components/GlobalSearch.jsx`
- **Normalisation des accents** (NFD) — "medecin" trouve "médecin"
- **Dictionnaire de synonymes** (80+ entries, francais medical/juridique) — "docteur"→"medecin", "argent"→"indemnisation", etc.
- **Correspondance par prefixe** — "indemn" → "indemnisation"
- **Keywords enrichis** sur toutes les entrees (20-30% plus de mots par entree)
- **Pages ajoutees**: Parrainage, Scanner documents
- **Intents utilisateur**: "burn out", "faute inexcusable", "combien vais-je toucher", "consolidation", "delais de prescription"
- **Icones par categorie**: Indemnisation (Scale), Guides (BookOpen), Sections (FileText)
- **Highlight accent-insensitive** dans les resultats
- **Deduplication** par href+anchor (evite les doublons)
- Scoring: titre(15) > keyword exact(8) > keyword prefix(5) > synonym(3) > base(3) + bonus phrase(25) + bonus all terms(20)
- Tests: 25/25 frontend (iteration 92)

## Mascotte "Strate" (Mar 2026)
- Composant: `/app/frontend/src/components/MascotteStrate.jsx`
- Conseils depuis la base de donnees via `/api/conseils/today`
- TTS: speakFrench() avec getVoices(), filtre fr-FR, onvoiceschanged
- Tracking deduplique: localStorage par conseil_id + date
- Conversion tracking: export `trackStrateConversion(action)`
- Tests: 16/16 backend + 100% frontend (iteration 91)

## Admin Conseils Strate (Mar 2026)
- Composant: `/app/frontend/src/components/AdminConseilsStrate.jsx`
- CRUD complet + sous-onglets Gestion/Statistiques
- Analytics: Top 10, taux de clic, courbe vues/clics/jour, filtres periode/categorie
- Tests: 16/16 backend + 100% frontend (iteration 91)

## Contenu IP & PGPF (Mar 2026)
- Integre dans: Ressources, Calculatrice IPP, Recherche, StrategiIA, AT page, Glossaire

## Scanner Documents (Mar 2026)
- Appareil photo natif (`<input capture="environment">`)

## Taches a venir
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test mode), PayPal (test mode)
- Claude Sonnet 4.5 (Emergent LLM Key)
- Resend (sandbox)
- HubSpot (partiellement, en attente credentials)
