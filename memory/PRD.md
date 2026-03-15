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
- Homepage: "Le défi en chiffres" — 4 stat blocks (700K AT, 50K MP, 12M handicap, 300K MDPH) with official source links (CNAM, INSEE, CNSA), black/gold cards, scroll animations, animated count-up (ease-out cubic, 1.3s, one-shot on scroll), impact phrase below

### Secured PDF Reports (Completed — Feb 2026)
- Server-side PDF generator (`_generate_secured_pdf` in server.py) with:
  - Cover page: report type, unique number (SES-YYYY-XXXXX), date, client name, type de dossier
  - Header on every page: brand name + site URL + report number
  - Footer on every page: copyright line
  - Semi-transparent diagonal watermark "Strategie & Expertise Sante" (default, removable for premium)
  - Legal mention on last page: copyright, IP protection, disclaimer
- New endpoint: `POST /api/strategiia/generate-pdf` — server-side PDF for StrategiIA (replaced client-side jsPDF)
- Premium PDF option (+19€): watermark-free version for professional use
  - StrategiIA: 29€ base → 48€ with premium PDF
  - Dossier Express: 97€ base → 116€ with premium PDF
  - UI: checkbox with Crown icon, +19€ badge, explanatory text on both pages
  - Dynamic pricing: checkout buttons update in real-time
- PDF Cover Preview: Clickable miniature of the cover page next to premium option, with zoom modal for detailed view. Shows logo, example report number, watermark, professional layout.

### Analyse Premium Option (Completed — Feb 2026)
- **StrategiIA** (+29€): Expert human review of AI-generated report, checkbox in premium purchase card
- **Dossier Express** (+49€): Expert enrichment with personal recommendations, checkbox before checkout
- Dynamic pricing: base + optional PDF Pro (+19€) + optional Analyse Premium (+29/49€)
- DB: `premium_analyses` collection stores orders with status tracking (en_attente → en_cours → termine)
- **Admin panel**: New "Premium" tab with notification badge, stats cards, and status management buttons
- Backend: `GET /api/admin/premium-analyses`, `PATCH /api/admin/premium-analyses/{id}`

### Navigation & Search Improvements (Completed — Feb 2026)
- **Scroll-to-top**: Global `ScrollToTop` component resets scroll to top (smooth) on every page navigation. Skips when URL has anchor hash.
- **Search anchoring**: Search results link to specific page sections via anchors (e.g., `#chiffres`). Page scrolls directly to relevant content.
- **Search highlighting**: Matching terms highlighted in golden badges on target pages, auto-fade after 4 seconds. Also in search results dropdown.
- **Admin notification email**: Resend email sent to admin when Analyse Premium is ordered (branded HTML with type, client, amount).

### RGPD / Data Consent (Completed — Feb 2026)
- **DataConsentBox** (`/app/frontend/src/components/DataConsentBox.jsx`): Reusable consent component with confidentiality notice, mandatory checkbox, and link to privacy policy.
- Integrated on: **StrategiIA**, **Dossier Express**, **Contact**, **Espace Client** (register mode only). Submit buttons disabled without consent.
- **Politique de confidentialité** (`/politique-confidentialite`): Dedicated RGPD page with 10 sections.
- Footer updated with link to privacy policy page.

### StratégiIA Phase 2 — Admin Case Management (Completed & Tested — March 2026)
- **Backend endpoints:**
  - `POST /api/admin/cas-anonymises` — Create anonymized case
  - `PATCH /api/admin/cas-anonymises/{case_id}` — Edit existing case
  - `DELETE /api/admin/cas-anonymises/{case_id}` — Delete case
  - `GET /api/admin/cas-anonymises` — List with search & filters
  - `GET /api/admin/cas-anonymises/stats` — Aggregated statistics
  - `POST /api/admin/cas-anonymises/import` — Bulk import (JSON/CSV, max 100)
- **Frontend admin UI:**
  - New "StratégiIA" tab in admin dashboard
  - Stats cards: total analyses, premium, anonymized cases, estimated revenue
  - Case form: type_dossier, regime, duree, strategie, resultat, score_pertinence, notes
  - Case list with search, type filter, edit modal, delete
  - Import button for bulk JSON/CSV upload
- **Testing:** 100% pass rate (iteration_33) — all 11 tests passed

### Search Index Enrichment (Completed & Tested — March 2026)
- Added `id` attributes to sections across Homepage, Services, Tarifs, Resources pages
- Updated `searchIndex.js` with new anchor entries (glossaire, guides, tarifs sections)
- **Testing:** 100% pass rate (iteration_33) — search and anchor navigation verified

### PageSpeed/SEO Optimization (Completed — March 2026)
- **SEO**: lang="fr", unique titles/descriptions per page (16+ pages), og:tags, twitter:card, canonical URLs
- **Schema.org JSON-LD**: 3 schemas (ProfessionalService, FAQPage, WebSite) injected dynamically via useEffect in App.js
- **Sitemap**: /sitemap.xml (static, 23 URLs with priority/changefreq)
- **Robots.txt**: /robots.txt (static, with Disallow /admin, Sitemap reference)
- **Performance**: React.lazy code splitting (30+ pages), Suspense loading, GZip compression, image lazy loading
- **react-helmet-async**: Dynamic per-page meta tags

## UI/UX
- Animations: scroll-triggered reveals (fade-in, slide-left/right, scale), staggered cards, card-glow hover, shimmer, float, icon-bounce, urgent-glow
- Disclaimer légal global: Footer, Homepage, Tarifs, StrategiIA, Dossier Express, Mentions Légales
- Repositionnement global: IA présentée comme outil d'aide à l'analyse au service de l'accompagnement humain
- Logo icon URL: https://static.prod-images.emergentagent.com/jobs/574c0cd2-0ae0-4513-8a36-a076963b0d88/images/6feb287ef88e3d9d1b52e1e4afa5fbb18a3e813dc8ddb26632f809c4d7b97324.png
- Logo full URL: https://static.prod-images.emergentagent.com/jobs/574c0cd2-0ae0-4513-8a36-a076963b0d88/images/b7a0e8feacc213c07dde10cadfe4911a1e660c1cf0aa56c500ce17b3c3ece35d.png

## Known Limitations
- LLM budget exceeded (needs recharge)
- Stripe/PayPal in test/sandbox mode
- Resend sender: onboarding@resend.dev (test sender)
- **Preview environment**: Emergent proxy overrides `X-Robots-Tag` to `noindex, nofollow` and Cloudflare injects `Content-Signal` into robots.txt — both resolved on custom domain deployment

## Pending (Blocked on User Action)
- P1: Recharge Emergent LLM Key (Profile → Universal Key → Add Balance)
- P1: NOTIFICATION_EMAIL, verified Resend domain
- P1: HubSpot Portal ID → set `HUBSPOT_PORTAL_ID` in backend/.env
- P2: Production Stripe/PayPal keys
- P3: Legal content finalization (business address, phone, host details)

## Backlog
- StratégiIA Phase 3: Predictive model with relevance score
- Backend refactoring: Break server.py into modules (user deprioritized)
- Legal content finalization
- Verified Resend domain for professional email sender

## Credentials
- Admin: admin@accompagn-sante.fr / Admin2024!
