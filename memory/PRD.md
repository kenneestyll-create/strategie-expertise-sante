# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)
- **Integrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search

## Recherche IA (Mar 2026) — REMPLACE RECHERCHE CLASSIQUE
- Fichier: `/app/frontend/src/components/GlobalSearch.jsx`
- **Concept:** La barre de recherche est un point d'entree vers l'IA
- Icone Sparkles, placeholder "Posez votre question..."
- **Suggestions IA**: 6 questions frequentes cliquables
- **Pendant la frappe**: Algolia montre des pages suggerees (debounce 250ms)
- **Bouton "Demander"** dore + "Ou demander a l'IA" sous les suggestions
- **Soumission (Enter/clic)**: dispatch `CustomEvent('strate-ask-ai')` → ChatBot ecoute et s'ouvre automatiquement avec la question pre-remplie, auto-envoyee apres 300ms
- **Chatbot** repond via Claude Sonnet 4.5 (ou FAQ)
- **Algolia** reste pour les suggestions de pages rapides (87 records, 29 synonymes)
- Tests: 9/9 backend + 15/15 frontend (iteration 94)

## Mascotte "Strate" (Mar 2026)
- TTS francais, conseils depuis DB, tracking deduplique, conversion tracking
- Tests: 16/16 backend (iteration 91)

## Admin Conseils Strate (Mar 2026)
- CRUD complet + sous-onglets Gestion/Statistiques
- Analytics: Top 10, courbe vues/clics, filtres

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
