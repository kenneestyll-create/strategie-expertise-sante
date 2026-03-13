# Stratégie & Expertise Santé — PRD

## Problem Statement
Web application in French providing advice and support for occupational diseases, insurance disputes, and disability procedures.

## Architecture
- **Frontend:** React + Tailwind CSS + Shadcn UI (port 3000)
- **Backend:** FastAPI + MongoDB (port 8001, monolithic server.py)
- **Integrations:** Stripe (test), PayPal (sandbox), Claude Sonnet 4.5 (Emergent LLM Key), Resend (ACTIVE), HubSpot (pending)

## Completed Features
- Core pages: Home, About, Services, Resources, Contact
- Admin panel with JWT auth
- Forum, Chatbot, Reviews/Guestbook
- Referral system, PDF viewer
- IPP & AAH calculators with share & counter
- Global search (fuse.js), StratégiIA AI analysis (Phase 1)
- Simulator with PDF report & email capture
- Urgent alert floating button
- Interactive MDPH directory, disease tables, guides
- Z-index management system
- Stripe & PayPal integration (test/sandbox mode)
- Abandoned cart tracking + email relance system
- **Resend email integration (ACTIVE)** — test email + relance emails working
- Admin email diagnostic endpoints (/admin/email/status, /admin/email/test)

## Resend Integration Status (March 13, 2026)
- Code: ACTIVE and WORKING
- API Key: re_S8PKx...p2eQ (verified working)
- SENDER_EMAIL: onboarding@resend.dev (test sender — production needs verified domain)
- NOTIFICATION_EMAIL: not yet configured (needed for contact/urgent alert notifications)
- Tested: test email send OK, abandoned cart relance email send OK

## Pending
- P1: NOTIFICATION_EMAIL needed for contact form + urgent alert notifications
- P1: Verified sender domain for production email (replace onboarding@resend.dev)
- P1: HubSpot Portal ID needed for CRM integration
- P2: Production Stripe/PayPal keys for live payments
- P3: Legal content (user business details for CGU/Mentions Légales)

## Backlog
- StratégiIA Phase 2: Admin interface for anonymized case management
- StratégiIA Phase 3: Predictive model with relevance score
- Backend refactoring: Break server.py into modules

## Credentials
- Admin: admin@accompagn-sante.fr / Admin2024!
