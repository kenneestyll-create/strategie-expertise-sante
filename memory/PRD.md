# Stratégie & Expertise Santé — PRD

## Problem Statement
Web application in French providing advice and support for occupational diseases, insurance disputes, and disability procedures.

## Architecture
- **Frontend:** React + Tailwind CSS + Shadcn UI + recharts + react-helmet-async (port 3000)
- **Backend:** FastAPI + MongoDB + GZip (port 8001, monolithic server.py)
- **Integrations:** Stripe (test), PayPal (sandbox), Claude Sonnet 4.5 (Emergent LLM Key), Resend (ACTIVE), HubSpot (pending), fpdf2 (PDF gen)

## Completed Features
- Core pages, Admin panel, Forum, Chatbot (5 free Q), Reviews, Referral system, PDF viewer
- IPP & AAH calculators, Global search (fuse.js), StratégiIA (read wall + scoring)
- Stripe & PayPal (test/sandbox), Resend (ACTIVE), Abandoned cart emails
- Secured PDF Reports, Analyse Premium, Navigation & Search, RGPD, Homepage animations
- StratégiIA Phase 2 (Admin case management), Search Index Enrichment, PageSpeed/SEO

### Analytics Dashboard (Completed — March 15, 2026)
- Admin "Analytique" tab with KPIs, recharts (activity, revenue, distributions), period selector
- Testing: 100% pass (iteration_34)

### StratégiIA Phase 3 — Relevance Scoring (Completed — March 15, 2026)
- `GET /api/strategiia/score` — composite score (0-100) from historical cases
- Score card in results with confidence badge, distribution bar, top strategies
- Testing: Backend 100% (iteration_35)

### Client Notification System (Completed — March 15, 2026)
- 4 types: analyse_premium_ready, payment_confirmed, dossier_in_progress, report_ready, document_rejected
- Registration form notification preferences, client settings panel, admin "Notifier" button
- Auto-notification on premium analysis status change
- Testing: 100% pass (iteration_36)

### Document Quality Control System (Completed — March 15, 2026)
- **Reusable `DocumentUploader` component** (`/app/frontend/src/components/DocumentUploader.jsx`):
  - Format validation: PDF, JPG, PNG, DOCX only
  - Size validation: max 10MB per file, min 100 bytes (corruption check)
  - File preview: thumbnails for images, icons for PDF/DOCX
  - "Supprimer et remplacer" button on each file (RefreshCw icon)
  - "Qualité vérifiée" badge after checklist completion
  - Error messages for invalid/corrupted files
- **Quality Checklist** (3 mandatory items before submission):
  - Documents lisibles et complets
  - Informations personnelles visibles
  - Dates et signatures lisibles
  - Submit buttons disabled until all checked (when files present)
- **Scan Guide** (collapsible):
  - 4 visual tips: bonne luminosité, scanner droit, pas de reflets, texte visible
  - Good vs Bad document visual comparison
- **Backend:**
  - `POST /api/documents/validate` — validates filename, size, MIME type
  - `POST /api/admin/notify-document-rejected/{client_id}` — sends rejection notification + email
- **Integration:**
  - Dossier Express: replaces old file upload with DocumentUploader
  - StrategiIA: new optional "Documents justificatifs" section
  - Admin Clients tab: "Documents à renvoyer" button per client
- **Testing:** 100% pass (iteration_37 — 15 backend + 12 frontend UI)

## Known Limitations
- LLM budget exceeded (needs recharge)
- Stripe/PayPal in test/sandbox mode
- Resend sender: onboarding@resend.dev

## Pending (Blocked on User Action)
- P1: Recharge Emergent LLM Key
- P1: HubSpot Portal ID
- P2: Production Stripe/PayPal keys
- P3: Legal content finalization

## Backlog
- Backend refactoring: Break server.py into modules
- Browser Push via Service Worker (Web Push API)
- Legal content finalization
- Verified Resend domain

## Credentials
- Admin: admin@accompagn-sante.fr / Admin2024!
- Test client: test-notif@example.com / Test1234!
