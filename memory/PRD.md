# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)

## Mascotte Strate — Redesign (Mar 2026)
- Fichier: `/app/frontend/src/components/MascotteStrate.jsx`
- **Suppression** grande fenetre auto-ouverte (plus d'intrusion)
- **Bulle pulsante** "Conseil du jour" avec animation CSS pulse douce
- **Badge date rouge** "23 mars" sur la mascotte (incite a revenir)
- **Clic** → fenetre compacte 256px, header "CONSEIL DU [date]", fond #141414
- **Fermeture** X discret, animation slide-in
- **Actions** : Ecouter TTS + lien action dore
- Tracking inchange (views, clicks, conversions)
- Style sobre noir/or coherent avec la charte

## Chatbot IA Expert (Mar 2026)
- FAQ restreinte (tarifs, contact uniquement)
- Signaux medicaux → Claude avec tableaux MP
- Tests: 11/11 backend (iteration 95)

## Recherche IA (Mar 2026)
- Barre → IA chatbot + suggestions Algolia
- Tests: 15/15 frontend (iteration 94)

## Admin Conseils Strate (Mar 2026)
- CRUD + Analytics (Top 10, courbes, filtres)

## Taches a venir
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search, HubSpot (attente)
