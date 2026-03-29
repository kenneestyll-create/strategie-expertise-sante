# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA isoles.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 — PATH A (natif, appel unique 8000 tokens) / PATH B (Emergent proxy, multi-stage httpx 7 sections)
- **PDF** : fpdf2 + jsPDF | **Email** : Resend | **Paiements** : Stripe + PayPal

## Services (ISOLES — voir ARCHITECTURE_GUARDRAILS.md)
- **StrategiIA** : Analyse strategique MP/AT. Collection: strategiia_analyses. Analyse STOCKEE en DB avec job_id.
- **Dossier Express IA** : Pipeline documentaire optimise. Collection: dossier_express. 8 etapes tracees.
- **Relecture admin** : Collection partagee premium_analyses (filtre par type). Liee a strategiia_analyses via job_id.

## Bug Fix: Analyse StrategiIA non stockee (29/03/2026)
### Cause racine
- _run_analysis() stockait le resultat uniquement dans un dict en memoire (_jobs[job_id])
- Le document strategiia_analyses ne contenait PAS le texte de l'analyse
- premium_analyses n'etait jamais mis a jour avec l'analyse generee
- Resultat: la modale admin "Relire/Valider" affichait le texte brut du client au lieu de l'analyse IA

### Fix applique
1. strategiia.py: Stocker l'analyse + job_id dans strategiia_analyses
2. strategiia.py: Mettre a jour premium_analyses avec l'analyse via job_id
3. admin.py: Ameliorer le lookup full-content pour chercher via job_id (puis fallback email)

### Verification
- iteration_152: 10/10 PASS, analyse de 14,334 chars correctement retournee par full-content
- Frontend: modale affiche "## Votre situation analysee" au lieu du texte brut

## Pipeline Dossier Express IA (OPTIMISE 29/03/2026)
- 7 sections, 3 batches paralleles httpx streaming
- PATH B (Emergent proxy): ~95-110s
- PATH A (cle native Anthropic): estimee ~25-35s
- Qualite validee: 3 dossiers (24-26K chars, 21-31 sections)
- Instrumentation: timings stockes en DB par etape

## Tests de non-regression
- iteration_150: 16/16 PASS (post-endpoint admin-bypass)
- iteration_151: 13/13 PASS (post-optimisation pipeline)
- iteration_152: 10/10 PASS (post-fix analyse StrategiIA stockage)

## Etat des services (Preview)
- IA Anthropic : OK (Emergent fallback + pipeline multi-stage httpx)
- Paiement Stripe : TEST MODE
- Email Resend : OK (sandbox)
- Stockage S3 : NON CONFIGURE
- Database MongoDB : OK

## Backlog
### P0 : TERMINE
- Consolidation architecture — DONE
- Optimisation pipeline Dossier Express — DONE
- Fix analyse StrategiIA non stockee en DB — DONE 29/03/2026

### P1 : Cles de production
- ANTHROPIC_API_KEY native (pipeline ~30s)
- STRIPE_API_KEY live
- S3 config (S3_ACCESS_KEY + S3_SECRET_KEY)
- Domaine Resend verifie

### P2 : Integration HubSpot CRM (en attente credentials)
### P3 : Consolidation moteurs PDF
### P4 : Contenu juridique final
