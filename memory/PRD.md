# Stratégie & Expertise Santé — PRD

## Problem Statement
Web application in French providing advice and support for occupational diseases, insurance disputes, and disability procedures.

## Architecture
- **Frontend:** React + Tailwind CSS + Shadcn UI (port 3000)
- **Backend:** FastAPI + MongoDB (port 8001, monolithic server.py)
- **Integrations:** Stripe (test), PayPal (sandbox), Claude Sonnet 4.5 (Emergent LLM Key), Resend (ACTIVE), HubSpot (pending), fpdf2 (PDF gen)

## Completed Features
- Core pages: Home, About, Services, Resources, Contact
- Admin panel with JWT auth
- Forum, Chatbot, Reviews/Guestbook, Referral system, PDF viewer
- IPP & AAH calculators with share & counter
- Global search (fuse.js), StratégiIA AI analysis (Phase 1)
- Simulator with PDF report & email capture
- Urgent alert floating button
- Interactive MDPH directory, disease tables, guides
- Z-index management system
- Stripe & PayPal integration (test/sandbox mode)
- Abandoned cart tracking + email relance system
- Resend email integration (ACTIVE)
- Admin email diagnostic endpoints

### NEW (March 13, 2026)
- **Dossier Express** (`/dossier-express`): Full service — landing page, form with upload, Stripe checkout (97€), async AI analysis via Claude, PDF generation (fpdf2), email delivery via Resend
- **Tarifs restructured** (`/tarifs`): 4-step progressive journey:
  1. StratégiIA gratuite (first diagnostic)
  2. Dossier Express 97€ (complete AI report)
  3. Prestations personnalisées 150-500€ (human expert)
  4. Pass Urgent (48h priority)
- Header updated with Dossier Express in Services dropdown
- Search index updated with Dossier Express entry
- Backend: 3 new endpoints (checkout, submit, status) + admin endpoint

## DB Collections
- **dossier_express**: {id, session_id, email, name, situation, type_dossier, regime, documents_text, status, analysis, email_sent, created_at, completed_at}

## Known Limitations
- LLM budget exceeded (Current cost: 0.466/Max: 0.4) — user needs to recharge Universal Key balance
- Stripe/PayPal in test/sandbox mode
- Resend sender: onboarding@resend.dev (test sender only)

## Pending
- P0: Recharge Emergent LLM Key balance (Profile → Universal Key → Add Balance)
- P1: NOTIFICATION_EMAIL for contact notifications
- P1: Verified sender domain in Resend for production emails
- P1: HubSpot Portal ID for CRM
- P2: Production Stripe/PayPal keys

## Backlog
- StratégiIA Phase 2: Admin interface for anonymized case management
- StratégiIA Phase 3: Predictive model with relevance score
- Backend refactoring: Break server.py into modules
- Legal content finalization

## Credentials
- Admin: admin@accompagn-sante.fr / Admin2024!
