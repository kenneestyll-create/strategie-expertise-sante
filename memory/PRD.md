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

## Autonomie technique — 100%
Aucune dépendance à emergentintegrations. Tous les SDK sont natifs.

| Composant | SDK | Variable d'env |
|-----------|-----|---------------|
| IA Chatbot/Analyse | `anthropic` | `ANTHROPIC_API_KEY` |
| OCR Avancée | `openai` | `OPENAI_API_KEY` |
| Paiements | `stripe` | `STRIPE_API_KEY` |
| Stockage fichiers | `boto3` (S3) | `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET` |
| Email | `resend` | `RESEND_API_KEY` |
| Recherche | `algoliasearch` | `ALGOLIA_APP_ID`, `ALGOLIA_API_KEY` |

## Fichiers de portabilité
- `Dockerfile` : Build multi-stage production
- `docker-compose.yml` : App + MongoDB
- `nginx.conf` : Reverse proxy + SPA
- `backend/.env.example` : Toutes les variables documentées
- `frontend/.env.example` : Variables frontend
- `README.md` : Guide complet d'installation

## Fonctionnalités (DONE)
- Auth Admin + Client, Dashboard Admin complet
- Scanner documents, StratégiIA, Dossier Express IA
- PDF premium, Paiements Stripe + PayPal
- Mascotte Straté + TTS français
- Upload chunké async (45MB), Auto-purge 30j
- Admin Human Review Workflow, Badge "Relu par expert"
- Portabilité SITE_URL, 0 URL hardcodée

## Backlog
### P1
- Activation paiements live (Stripe/PayPal)
### P2
- Intégration HubSpot CRM (attente identifiants)
### P3
- Refactoring EmailTemplateEditor.jsx
- Consolidation moteurs PDF (backend uniquement)
