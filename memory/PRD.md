# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA isoles.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 — PATH A (natif, appel unique 8000 tokens) / PATH B (Emergent proxy, multi-stage httpx 7 sections)
- **PDF** : fpdf2 + jsPDF | **Email** : Resend | **Paiements** : Stripe + PayPal

## Services (ISOLES — voir ARCHITECTURE_GUARDRAILS.md)
- **StrategiIA** : Analyse strategique MP/AT. Collection: strategiia_analyses. Analyse STOCKEE en DB avec job_id. PDF generable via /api/admin/strategiia/{id}/preview-pdf.
- **Dossier Express IA** : Pipeline documentaire optimise. Collection: dossier_express. PDF generable via /api/admin/dossier-express/{id}/preview-pdf.
- **Relecture admin** : Collection partagee premium_analyses. Bouton "Voir le PDF final" dans modale de relecture pour les deux services.

## Bugs corriges (29/03/2026)

### Bug 1: Analyse StrategiIA non stockee en DB
- Cause: _run_analysis() stockait le resultat uniquement en memoire (_jobs)
- Fix: Stocker l'analyse + job_id dans strategiia_analyses ET premium_analyses
- Fichiers: strategiia.py (lignes 148-155), admin.py (lignes 424-438)

### Bug 2: PDF StrategiIA inaccessible depuis l'admin
- Cause: Aucun endpoint admin et aucun bouton frontend pour generer/telecharger le PDF
- Fix: Endpoint GET /api/admin/strategiia/{id}/preview-pdf + bouton "Voir le PDF final" dans AdminPremiumReview
- Fichiers: admin.py (lignes 499-536), AdminPremiumReview.jsx (lignes 326-349)

## Tests
- iteration_150: 16/16 PASS (post-endpoint admin-bypass)
- iteration_151: 13/13 PASS (post-optimisation pipeline)
- iteration_152: 10/10 PASS (post-fix analyse stockage)
- iteration_153: 8/8 PASS (post-fix PDF preview)

## Etat des services (Preview)
- IA Anthropic : OK (Emergent fallback multi-stage httpx)
- Paiement Stripe : TEST MODE
- Email Resend : OK (sandbox)
- Stockage S3 : NON CONFIGURE
- Database MongoDB : OK

## Backlog
### P0 : TERMINE
- Consolidation architecture — DONE
- Optimisation pipeline Dossier Express — DONE
- Fix analyse StrategiIA non stockee — DONE
- Fix PDF StrategiIA inaccessible — DONE

### P1 : Cles de production
- ANTHROPIC_API_KEY native (pipeline ~30s)
- STRIPE_API_KEY live
- S3 config (S3_ACCESS_KEY + S3_SECRET_KEY)
- Domaine Resend verifie

### P2 : Integration HubSpot CRM (en attente credentials)
### P3 : Consolidation moteurs PDF
### P4 : Contenu juridique final
