# Stratégie & Expertise Santé — PRD

## Problem Statement
Web application in French providing advice and support for occupational diseases, insurance disputes, and disability procedures.

## Architecture
- **Frontend:** React + Tailwind CSS + Shadcn UI (port 3000)
- **Backend:** FastAPI + MongoDB (port 8001, monolithic server.py)
- **Integrations:** Stripe (test), PayPal (sandbox), Claude Sonnet 4.5 (Emergent LLM Key), Resend (ACTIVE), HubSpot (pending), fpdf2 (PDF gen)

## Completed Features
- Core pages, Admin panel, Forum, Chatbot, Reviews, Referral system, PDF viewer
- IPP & AAH calculators with share & counter
- Global search (fuse.js), StratégiIA AI analysis (Phase 1)
- Simulator with PDF report & email capture
- Urgent alert floating button, MDPH directory, disease tables
- Stripe & PayPal (test/sandbox), Resend (ACTIVE), Abandoned cart emails
- Dossier Express (/dossier-express) — 97€ AI analysis + PDF + email
- Tarifs restructured as 4-step progressive journey

### NEW (March 13, 2026 - Quotas)
- **StrategiIA quota**: 3 free analyses/month per email, mandatory email registration, visible counter badge, quota exceeded redirect to /tarifs + /dossier-express
- **Chatbot quota**: 5 free questions/session, visible counter badge (X/5), quota exceeded banner with CTAs to /agenda, /dossier-express, /tarifs
- **Backend**: /strategiia/quota/{email}, /chatbot/quota/{session_id} endpoints
- **DB collections**: chatbot_sessions {session_id, count, created_at, updated_at}

## Known Limitations
- LLM budget exceeded (needs recharge via Profile → Universal Key → Add Balance)
- Stripe/PayPal in test/sandbox mode
- Resend sender: onboarding@resend.dev (test sender only)

## Pending
- P0: Recharge Emergent LLM Key balance
- P1: NOTIFICATION_EMAIL, verified Resend domain
- P1: HubSpot Portal ID for CRM
- P2: Production Stripe/PayPal keys

## Backlog
- StratégiIA Phase 2: Admin interface for anonymized case management
- StratégiIA Phase 3: Predictive model with relevance score
- Backend refactoring: Break server.py into modules
- Legal content finalization

## Credentials
- Admin: admin@accompagn-sante.fr / Admin2024!
