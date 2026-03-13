# Stratégie & Expertise Santé — PRD

## Problem Statement
Web application in French providing advice and support for occupational diseases, insurance disputes, and disability procedures.

## Architecture
- **Frontend:** React + Tailwind CSS + Shadcn UI (port 3000)
- **Backend:** FastAPI + MongoDB (port 8001, monolithic server.py)
- **Integrations:** Stripe (test), PayPal (sandbox), Claude Sonnet 4.5 (Emergent LLM Key), Resend (pending), HubSpot (pending)

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
- Abandoned cart tracking (emails pending Resend key)

## Bug Fixes (March 13, 2026)
- **Header overflow (v2)**: Regrouped nav items — Accompagnements & Protection juridique moved into Expertises dropdown, font reduced to text-xs, logo to text-sm. CTA button now has 352px margin from right edge.
- **CTA differentiation**: "Nous contacter" (homepage→contact) vs "Réserver un appel" (header→agenda)
- **MDPH search (v2)**: Regex extraction (/\d+[a-b]?/i) handles "MDA 28", "MDPH 75", "département 59" etc. Returns exact single department.

## Pending / Blocked
- P1: Resend API key needed for abandoned cart emails
- P1: HubSpot Portal ID needed for CRM integration
- P2: Production Stripe/PayPal keys for live payments
- P3: Legal content (user business details for CGU/Mentions Légales)

## Backlog
- StratégiIA Phase 2: Admin interface for anonymized case management
- StratégiIA Phase 3: Predictive model with relevance score
- Backend refactoring: Break server.py into modules

## Credentials
- Admin: admin@strategie-expertise-sante.fr / Admin2024!
