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
- Global search (fuse.js), StratégiIA (read wall: 1/4 teaser + email registration to unlock)
- Simulator with PDF report & email capture
- Urgent alert, MDPH directory, disease tables
- Stripe & PayPal (test/sandbox), Resend (ACTIVE), Abandoned cart emails
- Dossier Express (/dossier-express) — 97€ AI analysis + PDF + email
- Tarifs restructured as 4-step progressive journey
- Chatbot quota (5 free messages)
- Homepage: urgent red Dossier Express banner after hero section with weekly counter ("X dossiers traités cette semaine")
- UI/UX animations: scroll-triggered reveals (fade-in, slide-left/right, scale), staggered cards, card-glow hover, shimmer, float, icon-bounce, urgent-glow
- Animations on: Homepage, Tarifs (progressive reveal), Dossier Express (urgency-driven). No animations on À propos (sober/professional).
- Logo professionnel : bouclier noir #1a1a1a / or #C9A84C, intégré header + footer + favicon
- Logo icon URL: https://static.prod-images.emergentagent.com/jobs/574c0cd2-0ae0-4513-8a36-a076963b0d88/images/6feb287ef88e3d9d1b52e1e4afa5fbb18a3e813dc8ddb26632f809c4d7b97324.png
- Logo full URL: https://static.prod-images.emergentagent.com/jobs/574c0cd2-0ae0-4513-8a36-a076963b0d88/images/b7a0e8feacc213c07dde10cadfe4911a1e660c1cf0aa56c500ce17b3c3ece35d.png

### PageSpeed/SEO Optimization (March 14, 2026)
- **SEO**: lang="fr", unique titles/descriptions per page (16+ pages), og:tags, twitter:card, canonical URLs
- **Schema.org JSON-LD**: 3 schemas (ProfessionalService, FAQPage, WebSite) injected dynamically via useEffect in App.js
- **Sitemap**: /sitemap.xml (static, 23 URLs with priority/changefreq)
- **Robots.txt**: /robots.txt (static, with Disallow /admin, Sitemap reference)
- **Performance**: React.lazy code splitting (30+ pages), Suspense loading, GZip compression, image lazy loading (loading="lazy" on all img tags)
- **react-helmet-async**: Dynamic per-page meta tags (description, OG, Twitter, canonical) — no duplicate static tags in index.html
- **index.html cleanup**: Removed duplicate meta/OG tags, canonical moved to dynamic, Schema.org moved to dynamic injection

## Known Limitations
- LLM budget exceeded (needs recharge)
- Stripe/PayPal in test/sandbox mode
- Resend sender: onboarding@resend.dev (test sender)
- **Preview environment**: Emergent proxy overrides `X-Robots-Tag` to `noindex, nofollow` and Cloudflare injects `Content-Signal` into robots.txt — both resolved on custom domain deployment

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
