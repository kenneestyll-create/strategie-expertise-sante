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

## Correction PDF Footer (Mar 2026) — DONE
- Bug de chevauchement footer/texte corrige dans pdf.py
- FOOTER_MARGIN=28mm, auto page break, _space_left() check 50mm pour bloc Contact
- Nettoyage URLs: _clean_analysis() supprime toutes URLs/domaines du LLM
- Prompts LLM renforces: interdiction explicite de generer des URLs
- Teste sur 6 PDFs (court, moyen, long, URLs, contact, API) — 0 overlap, 0 URL fuitee

## Taches a venir
- **P1:** Dashboard admin pour stats tracking/conversions + leads guides
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search, HubSpot (attente)
