# Stratégie & Expertise Santé — PRD

## Problem Statement
Web application in French providing advice and support for occupational diseases, insurance disputes, and disability procedures.

## Architecture
- **Frontend:** React + Tailwind CSS + Shadcn UI + react-helmet-async (port 3000)
- **Backend:** FastAPI + MongoDB + GZip (port 8001, monolithic server.py)
- **Integrations:** Stripe (test), PayPal (sandbox), Claude Sonnet 4.5 (Emergent LLM Key), Resend (ACTIVE), HubSpot (pending), fpdf2 (PDF gen)

## Completed Features
- Core pages, Admin panel, Forum, Chatbot (5 free Q), Reviews, Referral system, PDF viewer
- IPP & AAH calculators with share & counter
- Global search (fuse.js), StratégiIA (3 free/month per email)
- Simulator with PDF report & email capture
- Urgent alert, MDPH directory, disease tables
- Stripe & PayPal (test/sandbox), Resend (ACTIVE), Abandoned cart emails
- Dossier Express (/dossier-express) — 97€ AI analysis + PDF + email
- Tarifs restructured as 4-step progressive journey
- StrategiIA + Chatbot quotas with counters

### PageSpeed/SEO Optimization (March 14, 2026)
- **SEO**: lang="fr", unique titles/descriptions per page (16+ pages), og:tags, twitter:card, canonical URLs, Schema.org JSON-LD (ProfessionalService)
- **Sitemap**: /api/sitemap.xml (24 URLs with priority/changefreq)
- **Robots.txt**: /api/robots.txt with Disallow /admin, Sitemap reference
- **Performance**: React.lazy code splitting (30+ pages), Suspense loading, GZip compression, image lazy loading (loading="lazy" on all img tags), image quality reduced (q=60)
- **react-helmet-async**: Dynamic per-page meta tags

## Known Limitations
- LLM budget exceeded (needs recharge)
- Stripe/PayPal in test/sandbox mode
- Resend sender: onboarding@resend.dev (test sender)

## Pending
- P0: Recharge Emergent LLM Key
- P1: NOTIFICATION_EMAIL, verified Resend domain
- P1: HubSpot Portal ID
- P2: Production Stripe/PayPal keys

## Backlog
- StratégiIA Phase 2: Admin interface for anonymized case management
- StratégiIA Phase 3: Predictive model with relevance score
- Backend refactoring: Break server.py into modules
- Legal content finalization

## Credentials
- Admin: admin@accompagn-sante.fr / Admin2024!
