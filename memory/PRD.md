# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)

## Entonnoir de Conversion — DONE
- Flow: Chatbot attire -> StrategiIA convertit -> Dossier Express monetise
- Guides PDF avec email gate pour capture de leads
- Email de relance automatique 48h apres telechargement guide

## StrategiIA — Entonnoir 3 paliers — DONE
Async polling, barre de progression, option RATP/SNCF
- Auto-open via URL param ?open=strategiia (pour liens email)

## Optimisation Mobile Complete — DONE
- 100dvh, safe areas, input 16px, ChatBot plein ecran, menu opaque
- Cartes empilees pour tableaux, tabs responsive, PdfPreview responsive

## Email Gate Guides PDF (Mar 2026) — DONE
- Champ email obligatoire avant telechargement
- POST /api/resources/request-guide
- Collection `guide_leads` avec segmentation par categorie

## Email Relance Automatique 48h (Mar 2026) — DONE
- Scheduler background `_guide_followup_scheduler()` — check toutes les heures
- 6 templates personnalises par categorie:
  * Maladie professionnelle
  * Accident du travail
  * Expertise medicale
  * MDPH
  * Recours
  * Assurances
- Tracking: pixel ouverture + click CTA
- Collections: `guide_followups` (sent_at, opened, clicked)
- CTA email redirige vers /?open=strategiia (auto-open modal)
- Admin stats: GET /api/admin/guide-leads/stats (taux ouverture/clic, par categorie)
- Teste manuellement: email envoye via Resend OK

## Correction Menu Mobile + Conseil du Jour (Mar 2026) — DONE
- Menu mobile: etend bord-a-bord (-mx-4), overflow-x hidden, scrollbar invisible
- Conseil du jour: corrige blocage priorite sans end_date, auto-expiration, rotation fiable
- Tests: backend 16/16, frontend verifie, 0 overflow horizontal

## Correction PDF Footer (Mar 2026) — DONE
- DEUX moteurs PDF identifies et corriges:
  * Backend pdf.py (FPDF) pour StrategiIA: marges, nettoyage URLs, contact block dynamique
  * Frontend SimulateurPage.jsx (jsPDF) pour Simulateur: remplace window.location.origin par SITE_DOMAIN, footer dynamique, checkPageBreak()
- Prompts LLM renforces: interdiction URLs
- Teste E2E: backend 8/8 tests, frontend flux complet verifie

## Taches a venir
- **P1:** Dashboard admin pour stats tracking/conversions + leads guides
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search, HubSpot (attente)
