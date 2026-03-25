# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)

## Entonnoir de Conversion (Mar 2026) — DONE
- Flow: Chatbot attire -> StrategiIA convertit -> Dossier Express monetise
- Guides PDF avec email gate pour capture de leads (Mar 2026) — DONE

## Page d'Accueil — DONE
Hero premium sombre, responsive mobile-first

## Header — DONE
Navigation dropdowns, menu mobile opaque

## StrategiIA — Entonnoir 3 paliers — DONE
Async polling, barre de progression, option RATP/SNCF, options payantes mobile corrigees

## Optimisation Mobile Complete — DONE
- 100dvh, safe areas, input 16px, ChatBot plein ecran, menu opaque
- Cartes empilees pour tableaux, tabs responsive, PdfPreview responsive
- CTA MedecinConseil raccourci sur mobile
- Footer liens legaux visibles + copyright unique + safe area bottom

## Email Gate Guides PDF (Mar 2026) — DONE
- Champ email obligatoire avant telechargement
- Backend: POST /api/resources/request-guide (email, guide_id, category)
- Stockage dans collection `guide_leads` pour segmentation prospects
- Categories: Maladie professionnelle, Expertise medicale, MDPH, Recours, Accident du travail, Assurances
- Apres soumission: telechargement auto + CTA upsell StrategiIA
- Teste iteration_104 — 100% PASS (backend 9/9, frontend all PASS)

## Mascotte Strate — DONE
## Chatbot IA Expert — DONE
## Recherche IA — DONE
## Tracking Conversions — DONE

## Taches a venir
- **P1:** Dashboard admin pour stats tracking/conversions + leads guides
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search, HubSpot (attente)
