# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)

## Chatbot IA Expert (Mar 2026) — CORRIGE
- Fichier: `/app/backend/utils/chatbot.py`
- **FAQ restreinte** : uniquement tarifs et contact (questions generales simples)
- **Detection signaux medicaux** : liste MEDICAL_SIGNALS bypass la FAQ (coccyg, hernie, canal carpien, burn out, faute inexcusable, etc.)
- **Exclusions FAQ** : must_not_contain empeche la FAQ de capturer des questions specifiques (ex: "combien toucher IPP" ne matche plus "tarifs")
- **Prompt Claude enrichi** : tous les tableaux MP (4, 6, 16bis, 25, 30, 42, 47, 57A-E, 66, 69, 79, 97, 98), procedure hors tableau CRRMP, IP/PGPF, persona expert
- **Orientation systematique** vers StrategiIA, Dossier Express, Calculatrice IPP en fin de reponse
- Tests: 11/11 backend (iteration 95)

## Recherche IA (Mar 2026)
- Barre de recherche → point d'entree IA, suggestions Algolia + envoi au chatbot
- Tests: 15/15 frontend (iteration 94)

## Mascotte "Strate" (Mar 2026)
- TTS francais, conseils DB, tracking, conversion

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
