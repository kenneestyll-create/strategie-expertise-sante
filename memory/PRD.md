# PRD — Stratégie & Expertise Santé (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude (via emergentintegrations, migrable vers SDK natif)
- **PDF** : fpdf2 (backend) + jsPDF (frontend)
- **Email** : Resend
- **Paiements** : Stripe + PayPal (test mode)
- **OCR** : Tesseract + PyMuPDF (open source)

## Variables d'environnement centrales
| Variable | Fichier | Usage |
|----------|---------|-------|
| `SITE_URL` | backend/.env | Emails, sitemap, robots.txt, SEO |
| `REACT_APP_SITE_URL` | frontend/.env | SEO, canonical, OpenGraph |
| `REACT_APP_BACKEND_URL` | frontend/.env | Appels API frontend |

## Fonctionnalités implémentées (DONE)
- Auth Admin + Client, Dashboard Admin complet
- Scanner documents (caméra native), StratégiIA, Dossier Express IA
- PDF premium standardisés, Paiements Stripe + PayPal (test)
- Mascotte Straté + TTS français + Admin CRUD conseils
- Upload chunké async (45MB), Auto-purge 30j, DataConsentBox
- Admin Human Review Workflow (stockage originaux, édition analyse, regénération PDF)
- Badge "Relu par expert" côté client
- Portabilité SITE_URL (0 URL hardcodée, variables d'env centrales)
- Fichiers de portabilité : Dockerfile, docker-compose.yml, nginx.conf, .env.example, README.md
- .gitignore nettoyé

## Portabilité
| Composant | Portable | Si autonome, remplacer par |
|-----------|----------|---------------------------|
| Frontend React | ✅ 100% | — |
| Admin Dashboard | ✅ 100% | — |
| OCR / PDF | ✅ 100% | — |
| Emails (Resend) | ✅ 100% | — |
| Algolia | ✅ 100% | — |
| IA (Claude) | ⚠️ | SDK `anthropic` natif → `backend/utils/chatbot.py` |
| Stripe | ⚠️ | SDK `stripe` natif → `backend/routes/payments.py` |
| Object Storage | ⚠️ | AWS S3 / GCS → `backend/utils/storage.py` |
| MongoDB | ⚠️ | MongoDB Atlas / hébergé |

## Backlog
### P1
- Activation paiements live (Stripe/PayPal)
### P2
- Intégration HubSpot CRM (attente identifiants)
### P3
- Remplacement emergentintegrations → SDKs natifs
- Refactoring EmailTemplateEditor.jsx
- Consolidation moteurs PDF (backend uniquement)
