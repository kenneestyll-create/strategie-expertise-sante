# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)
- **Integrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search

## Moteur de Recherche — Algolia (Mar 2026)
- **Algolia App ID:** 54V9JMPOCR
- **Index:** strategie_sante
- **Records:** 87 (pages, outils, sections, guides, intents, maladies, MDPH, aides, IP/PGPF)
- **Synonymes:** 29 groupes (IPP, AT, MP, MDPH, AAH, docteur/medecin, avocat/juriste, etc.)
- **Config:** typo tolerance FR, removeStopWords FR, ignorePlurals FR, queryLanguages FR
- **Script indexation:** `/app/backend/algolia_index.py`
- **Composant:** `/app/frontend/src/components/GlobalSearch.jsx` (algoliasearch/lite v5)
- Recherche instantanee debounced 200ms, resultats groupes par categorie avec icones
- Highlight Algolia natif avec `<mark class="algolia-hl">`
- "Aucun resultat" → lien vers chatbot
- Attribution "Recherche par Algolia"
- Raccourci Ctrl+K
- Tests: 19/20 frontend (iteration 93)

## Mascotte "Strate" (Mar 2026)
- TTS francais, conseils depuis DB, tracking deduplique, conversion tracking
- Tests: 16/16 backend + 100% frontend (iteration 91)

## Admin Conseils Strate (Mar 2026)
- CRUD complet + sous-onglets Gestion/Statistiques
- Analytics: Top 10, taux de clic, courbe vues/clics/jour, filtres
- Tests: 16/16 backend + 100% frontend (iteration 91)

## Contenu IP & PGPF (Mar 2026)
- Integre dans: Ressources, Calculatrice IPP, Recherche, StrategiIA

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
- Algolia Search (plan gratuit, 10K recherches/mois)
- HubSpot (en attente credentials)
