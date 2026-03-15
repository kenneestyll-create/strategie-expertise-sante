# Stratégie & Expertise Santé — PRD

## Problem Statement
Web application in French providing advice and support for occupational diseases, insurance disputes, and disability procedures.

## Architecture
- **Frontend:** React + Tailwind CSS + Shadcn UI + recharts + Tesseract.js + react-helmet-async (port 3000)
- **Backend:** FastAPI + MongoDB + GZip (port 8001, monolithic server.py)
- **Integrations:** Stripe (test), PayPal (sandbox), Claude Sonnet 4.5 (Emergent LLM Key), Resend (ACTIVE), HubSpot (pending), fpdf2, Tesseract.js (OCR)

## Completed Features (Full List)
- Core pages, Admin panel (10 tabs), Forum, Chatbot (5 free Q), Reviews, Referral system, PDF viewer
- IPP & AAH calculators, Global search (fuse.js + anchors + highlighting)
- StratégiIA (read wall + relevance scoring + OCR), Dossier Express (AI analysis + OCR)
- Stripe & PayPal (test/sandbox), Resend (ACTIVE), Abandoned cart emails
- Secured PDF Reports, Analyse Premium (+29€/+49€), Navigation & Search, RGPD
- StratégiIA Phase 2 (Admin case CRUD), Phase 3 (relevance scoring)
- Analytics Dashboard, Client Notification System (5 types)
- Document Quality Control, OCR Phase 1 (Tesseract.js)
- Intelligent Document History
- PageSpeed/SEO, Homepage animations

### Intelligent Document History (Completed — March 15, 2026)
- **Backend CRUD (`client_documents` collection):**
  - `POST /api/client/documents` — upload with auto-categorization from OCR fields
  - `GET /api/client/documents` — list with filters (category, status, organisme, search) + stats
  - `GET /api/client/documents/{id}` — single document with file_data for download
  - `PATCH /api/client/documents/{id}` — update category, tags, status
  - `DELETE /api/client/documents/{id}` — delete document
  - `POST /api/client/documents/{id}/version` — add new version (sets status to "corrigé")
- **Auto-tagging:**
  - Category auto-detection from OCR `type_dossier_detected` → at, mp, mdph, expertise
  - Organisme auto-detection from OCR context (CPAM, CRAMIF, MSA, MDPH, CNSA, TASS, TCI)
  - Date, references, amounts, SSN, IPP rates from OCR fields
- **7 categories:** AT, MP, MDPH/AAH, Expertises médicales, Courriers CPAM, Documents juridiques, Autres
- **4 statuses:** en_attente, validé, illisible, corrigé
- **Frontend (ClientDocuments.jsx):**
  - "Mes Documents" tab in client portal (alongside "Mes Dossiers")
  - Stats cards: total, validés, en attente, illisibles
  - Two views: chronological list + category folders
  - Search bar, category filter, status filter
  - Upload panel with OCR-enabled DocumentUploader
  - Edit tags modal: category, organisme, date_document
  - Document cards: filename, ext badge, status badge, category badge, date, organisme
  - Download, edit, delete actions on hover
  - Version tracking (vN displayed)
- **File storage:** base64 in MongoDB (< 10MB per file)
- **Testing:** 100% pass (iteration_39 — 23 backend + 10 frontend)

## Known Limitations
- LLM budget exceeded (needs recharge)
- Stripe/PayPal in test/sandbox mode
- Resend sender: onboarding@resend.dev
- OCR Phase 1 (Tesseract.js) less accurate on complex docs — Phase 2 GPT-4o planned

## Pending (Blocked on User Action)
- P1: Recharge Emergent LLM Key
- P1: HubSpot Portal ID
- P2: Production Stripe/PayPal keys
- P3: Legal content finalization

## Backlog
- OCR Phase 2: GPT-4o enhanced extraction (pending LLM budget)
- Backend refactoring: Break server.py into modules
- Browser Push via Service Worker (Web Push API)
- Legal content finalization
- Verified Resend domain
- Object storage migration (for production file hosting)

## Credentials
- Admin: admin@accompagn-sante.fr / Admin2024!
- Test client: test-notif@example.com / Test1234!
