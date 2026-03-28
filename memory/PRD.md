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
- **Dark Mode Admin "Noir & Or" (28 mars 2026)**
  - Scope : Dashboard admin uniquement (pages publiques non affectées)
  - Toggle : Détection automatique préférences système + bouton manuel dans le header
  - Palette : Noir profond (#121217) + accents or (#CCA33E) + texte chaud (#E7E2DA)
  - Portails : Dialogs, selects, popovers correctement thémés via body.admin-dark
  - Persistance : localStorage (clé: ses-admin-theme)
  - Tests : 14/14 passés (iteration_141)

## Backlog
### P1
- Activation paiements live (clés Stripe live + Anthropic)
### P2
- Intégration HubSpot CRM
### P3
- Refactoring EmailTemplateEditor.jsx
- Consolidation moteurs PDF (backend uniquement)
### P4
- Finaliser le contenu juridique
