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
- Global search (fuse.js), StratégiIA (read wall: 1/4 teaser + email registration to unlock)
- Simulator with PDF report & email capture
- Urgent alert, MDPH directory, disease tables
- Stripe & PayPal (test/sandbox), Resend (ACTIVE), Abandoned cart emails
- Dossier Express (/dossier-express) — 97€ AI analysis + PDF + email
- Tarifs restructured as 4-step progressive journey
- Chatbot quota (5 free messages)
- Homepage: urgent red Dossier Express banner, "Le défi en chiffres" animated counters

### Secured PDF Reports (Completed — Feb 2026)
- Server-side PDF generator with cover page, headers, footers, watermarks, legal mentions
- Premium PDF option (+19€): watermark-free version
- PDF Cover Preview component

### Analyse Premium Option (Completed — Feb 2026)
- StrategiIA (+29€) and Dossier Express (+49€) expert human review
- Admin "Premium" tab with status management

### Navigation & Search (Completed — Feb 2026)
- ScrollToTop, search anchoring, search highlighting (mark.js)

### RGPD / Data Consent (Completed — Feb 2026)
- DataConsentBox component, Privacy Policy page, mandatory consent on forms

### StratégiIA Phase 2 — Admin Case Management (Completed — March 2026)
- CRUD endpoints for anonymized cases, bulk import, stats
- Admin "StratégiIA" tab with form, list, search, filter, import
- Testing: 100% pass (iteration_33)

### Search Index Enrichment (Completed — March 2026)
- Section anchors across pages, enriched searchIndex.js
- Testing: 100% pass (iteration_33)

### Analytics Dashboard (Completed — March 15, 2026)
- **Backend:** `GET /api/admin/analytics?period=7d|30d|90d` — aggregates KPIs, time series, package distribution, analyse types from 8 collections
- **KPIs:** total_revenue, pending_revenue, total_contacts, total_clients, conversion_rate, total_analyses, total_dossiers, total_forum_users, total_chatbot_sessions, calculator_usage
- **Frontend:** New "Analytique" tab in admin dashboard with:
  - Period selector (7/30/90 jours)
  - 5 KPI cards (Revenus, Contacts, Clients inscrits, Analyses IA, Forum)
  - Activity bar chart (contacts, analyses, inscriptions over time)
  - Revenue area chart with gradient fill
  - Package distribution pie chart
  - Analyse types horizontal bar chart
  - Revenue detail table by prestation
- Uses recharts (AreaChart, BarChart, PieChart)
- Testing: 100% pass (iteration_34, 15/15 tests)

### StratégiIA Phase 3 — Relevance Scoring (Completed — March 15, 2026)
- **Backend:** `GET /api/strategiia/score?type_dossier=X&regime=Y` — computes statistical relevance score from anonymized case history
  - Composite score (0-100): 60% success_rate + 40% avg_admin_score
  - Confidence levels: high (20+ cases), medium (5-19), low (1-4), insufficient_data (0)
  - Distribution: favorable, defavorable, en_cours, autre
  - Top successful strategies from favorable cases
  - Fallback: tries type_dossier only if type+regime yields 0 results
- **Frontend:** Score card in StrategiIA basic result view:
  - Score value in dark box (/100), confidence badge
  - Distribution progress bar (green/yellow/red)
  - Top strategies as badges
  - Auto-fetches via useEffect when analysis step changes
- Testing: Backend 100% pass (iteration_35, 11/11 tests)
- Frontend score card: Code review confirmed correct, E2E blocked by exhausted LLM key

### PageSpeed/SEO (Completed — March 2026)
- SEO, Schema.org, Sitemap, Robots.txt, code splitting, lazy loading

## UI/UX
- Black and gold theme, scroll-triggered animations
- Legal disclaimers across site
- Logo URLs in PRD

## Known Limitations
- LLM budget exceeded (needs recharge)
- Stripe/PayPal in test/sandbox mode
- Resend sender: onboarding@resend.dev (test sender)

## Pending (Blocked on User Action)
- P1: Recharge Emergent LLM Key (Profile → Universal Key → Add Balance)
- P1: NOTIFICATION_EMAIL, verified Resend domain
- P1: HubSpot Portal ID
- P2: Production Stripe/PayPal keys
- P3: Legal content finalization (business address, phone, host details)

## Backlog
- Backend refactoring: Break server.py into modules (user deprioritized)
- Legal content finalization
- Verified Resend domain for professional email sender

## Credentials
- Admin: admin@accompagn-sante.fr / Admin2024!
