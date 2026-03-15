# Stratégie & Expertise Santé — PRD

## Problem Statement
Web application in French providing advice and support for occupational diseases, insurance disputes, and disability procedures.

## Architecture
- **Frontend:** React + Tailwind CSS + Shadcn UI + recharts + react-helmet-async (port 3000)
- **Backend:** FastAPI + MongoDB + GZip (port 8001, monolithic server.py)
- **Integrations:** Stripe (test), PayPal (sandbox), Claude Sonnet 4.5 (Emergent LLM Key), Resend (ACTIVE), HubSpot (pending), fpdf2 (PDF gen)

## Completed Features
- Core pages, Admin panel, Forum, Chatbot (5 free Q), Reviews, Referral system, PDF viewer
- IPP & AAH calculators with share & counter
- Global search (fuse.js), StratégiIA (read wall + scoring), Dossier Express
- Stripe & PayPal (test/sandbox), Resend (ACTIVE), Abandoned cart emails
- Secured PDF Reports (watermarks, premium option +19€)
- Analyse Premium (+29€/+49€) with admin management
- Navigation & Search (scroll-to-top, anchoring, highlighting)
- RGPD / Data Consent (DataConsentBox, privacy policy)
- StratégiIA Phase 2 — Admin Case Management (CRUD, bulk import)
- Search Index Enrichment (section anchors across pages)
- PageSpeed/SEO (Schema.org, sitemap, code splitting)
- Homepage: animated counters, Dossier Express banner

### Analytics Dashboard (Completed — March 15, 2026)
- `GET /api/admin/analytics?period=7d|30d|90d` — KPIs, time series, distributions
- Admin "Analytique" tab with recharts: KPI cards, activity bar chart, revenue area chart, pie/bar distributions, detail table
- Testing: 100% pass (iteration_34)

### StratégiIA Phase 3 — Relevance Scoring (Completed — March 15, 2026)
- `GET /api/strategiia/score?type_dossier=X&regime=Y` — composite score (0-100) from historical cases
- Score card in StrategiIA results: score value, confidence badge, distribution bar, top strategies
- Testing: Backend 100% (iteration_35)

### Client Notification System (Completed — March 15, 2026)
- **Notification types:** analyse_premium_ready, payment_confirmed, dossier_in_progress, report_ready
- **Backend:**
  - `_create_client_notification()` helper: creates in-app notification + sends email via Resend
  - `GET /api/client/settings/notifications` — get preferences
  - `PATCH /api/client/settings/notifications` — update email/push preferences
  - `POST /api/admin/premium-analyses/{id}/notify` — admin manual notification (4 types)
  - Auto-notification on status change: 'en_cours' → dossier_in_progress, 'termine' → analyse_premium_ready
  - Registration now accepts `notifications_email` and `notifications_push` fields
- **Frontend Espace Client:**
  - Registration form: notification preference checkboxes (email + push)
  - Settings gear icon → notification settings panel with toggleable email/push preferences
  - Notification bell with unread badge (existing)
- **Frontend Admin:**
  - "Notifier" / "Relancer" button on each premium analysis in admin Premium tab
  - Sends contextual notification based on current analysis status
- **Email template:** Branded HTML with CTA button linking to espace-client
- **Testing:** 100% pass (iteration_36 — 18 backend + 11 frontend UI)

## UI/UX
- Black and gold theme, scroll-triggered animations
- Legal disclaimers across site

## Known Limitations
- LLM budget exceeded (needs recharge)
- Stripe/PayPal in test/sandbox mode
- Resend sender: onboarding@resend.dev (test sender)

## Pending (Blocked on User Action)
- P1: Recharge Emergent LLM Key (Profile → Universal Key → Add Balance)
- P1: NOTIFICATION_EMAIL, verified Resend domain
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
