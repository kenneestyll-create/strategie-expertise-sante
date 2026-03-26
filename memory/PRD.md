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

## Refonte PDF Premium (Mar 2026) — DONE
- Moteur PDF completement reecrit: palette noir #1A1A1A / or #C9A84C / ivoire
- Header premium: nom + PIONNIER EN FRANCE + date + numero SES-XXXX-XXXXX
- TOUT tient sur 1 page A4 (court/moyen/long)
- Prompt LLM restructure: ton humain/chaleureux, 300 mots max, 6 sections premium
- Filigrane discret (gratuit) / sans filigrane (premium)
- Footer or fin + Document confidentiel
- Tests: 14/14 passes

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

## Refonte PDF Simulateur Premium (Mar 2026) — DONE
- generatePDF() dans SimulateurPage.jsx completement reecrit avec design premium
- Ancien design rouge [185,78,72] supprime — remplace par palette Noir/Or/Ivoire
- Header noir avec "Strategie & Expertise Sante" blanc + "PIONNIER EN FRANCE" or
- Numero rapport SES-YYYY-XXXXX + date a droite
- Barres d'accent dorees sur titres de sections
- Puces dorees (gold bullets) au lieu de cercles noirs
- Bloc profil sur fond ivoire avec accent or a gauche
- Services encadres avec bordure doree sur fond ivoire
- Footer: ligne or + "Document confidentiel" + copyright
- Watermark diagonal "Strategie & Expertise Sante"
- Fichier renomme: rapport-diagnostic-SES-YYYY.pdf
- Coherence visuelle totale entre PDF Simulateur et PDF Backend
- Logo bouclier haute resolution (264x288px) integre dans le header PDF
- Conclusion emotionnelle premium: "Vous n'etes plus seul(e)... SES est votre bouclier"
- Module shieldLogo.js cree pour le logo base64 (importe dans SimulateurPage.jsx)
- Tests: 100% backend + 100% frontend (flux E2E + analyse visuelle PDF confirme)

## Taches a venir
- **P1:** Dashboard admin pour stats tracking/conversions + leads guides
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search, HubSpot (attente)
