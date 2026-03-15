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
- Secured PDF Reports (watermarks, premium +19€), Analyse Premium (+29€/+49€)
- Navigation (scroll-to-top, anchoring), RGPD (DataConsentBox, privacy policy)
- StratégiIA Phase 2 (Admin case CRUD, bulk import), Phase 3 (relevance scoring)
- Analytics Dashboard (KPIs, recharts charts, period selector)
- Client Notification System (5 types, email + in-app, preferences, admin notify)
- Document Quality Control (format validation, checklist, scan guide, rejection notifications)
- OCR System Phase 1 (Tesseract.js + regex extraction, pre-fill forms)
- PageSpeed/SEO (Schema.org, sitemap, code splitting, lazy loading)
- Homepage: animated counters, Dossier Express banner

### OCR System — Phase 1 (Completed — March 15, 2026)
- **Frontend (`useOCR.js`):** Tesseract.js v7 worker with French language (fra)
  - Auto-triggers on image upload (JPG/PNG) in DocumentUploader (enableOCR=true)
  - `parseFields()` extracts: dates, montants, references, numero_ss, noms, taux_ipp, type_dossier_detected, contexte
  - Progress bar with percentage during processing
  - Manual "Relancer l'extraction OCR" button
- **Frontend (`OcrFieldsPreview.jsx`):** Shows extracted fields in categorized badges
  - Icons per field type (Calendar, DollarSign, Hash, User, Target)
  - Confidence percentage badge, source indicator (Tesseract/GPT-4o)
  - "Pré-remplir le formulaire" button — applies fields to parent form
  - Dismiss button to close preview
- **StrategiIA integration:** OCR pre-fills `type_dossier`, `situation`, `regime`
- **Dossier Express integration:** OCR pre-fills `situation`, `name`
- **Backend (`POST /api/documents/extract-fields`):** Server-side regex extraction
  - Same field extraction as frontend (dates, amounts, refs, SSN, names, IPP, types)
  - Returns `enhanced: false` (Phase 1), ready for Phase 2 GPT-4o
- **Testing:** 100% pass (iteration_38 — 22 backend + 10 frontend + 3 code review)

### OCR Phase 2 (Architecture Prepared, Pending LLM Budget)
- Backend endpoint ready: `POST /api/documents/extract-fields` with `enhanced` flag
- When GPT-4o budget available: AI-powered extraction with higher accuracy
- Coupling with Analyse Premium for expert validation of OCR results

## Known Limitations
- LLM budget exceeded (needs recharge)
- Stripe/PayPal in test/sandbox mode
- Resend sender: onboarding@resend.dev
- OCR Phase 1 (Tesseract.js) less accurate on complex documents — Phase 2 GPT-4o planned

## Pending (Blocked on User Action)
- P1: Recharge Emergent LLM Key (unlocks AI features + OCR Phase 2)
- P1: HubSpot Portal ID
- P2: Production Stripe/PayPal keys
- P3: Legal content finalization

## Backlog
- OCR Phase 2: GPT-4o enhanced extraction (pending LLM budget)
- Backend refactoring: Break server.py into modules
- Browser Push via Service Worker (Web Push API)
- Legal content finalization
- Verified Resend domain

## Credentials
- Admin: admin@accompagn-sante.fr / Admin2024!
- Test client: test-notif@example.com / Test1234!
