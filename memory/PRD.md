# PRD — Stratégie & Expertise Santé (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude (`anthropic` SDK natif) + OpenAI GPT-4o (`openai` SDK natif)
- **PDF** : fpdf2 (backend) + jsPDF (frontend)
- **Email** : Resend
- **Paiements** : Stripe (`stripe` SDK natif) + PayPal
- **Stockage** : S3 compatible (`boto3`)
- **OCR** : Tesseract + PyMuPDF (open source)
- **Recherche** : Algolia

## Autonomie : 100%
**0 dépendance à emergentintegrations.** Tous SDK natifs et standards.

## Validation redéploiement (28 mars 2026)
- Frontend build : OK (15MB, 182 fichiers statiques)
- 13/13 modules Python importent : OK
- 203 routes API chargées : OK
- 9/9 routes critiques HTTP 200 : OK
- Dockerfile + docker-compose validés : OK
- PRODUCTION_CHECKLIST.md créée : OK

## Fonctionnalités (DONE)
- Auth Admin + Client, Dashboard Admin complet
- Scanner documents, StratégiIA, Dossier Express IA
- PDF premium, Paiements Stripe + PayPal
- Mascotte Straté + TTS français
- Upload chunké async (45MB), Auto-purge 30j
- Admin Human Review, Badge "Relu par expert"
- Portabilité complète, 0 URL hardcodée
- **Refonte visuelle Admin Dashboard cockpit premium (28 mars 2026)**
  - Header compact avec branding S.E.S
  - Barre d'onglets scrollable avec séparateurs visuels
  - KPI Dossier Express : cartes premium avec icônes, sous-labels, pourcentages
  - AdminPremiumReview : stats avec icônes, cartes enrichies
  - Liste dossiers : icônes de statut, nom client proéminent, badges, actions groupées
  - 100% tests frontend passés (iteration_140)

## Backlog
### P1
- Activation paiements live (clés Stripe live + Anthropic)
### P2
- Intégration HubSpot CRM
### P3
- Refactoring EmailTemplateEditor.jsx
- Consolidation moteurs PDF (backend uniquement)
