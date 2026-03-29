# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 (natif) + Fallback Emergent Universal Key (httpx streaming multi-stage)
- **PDF** : fpdf2 + jsPDF | **Email** : Resend | **Paiements** : Stripe + PayPal

## Services (ISOLES — voir ARCHITECTURE_GUARDRAILS.md)
- **StrategiIA** : Analyse strategique MP/AT. Collection: strategiia_analyses. Premium: asyncio.gather 2 appels paralleles.
- **Dossier Express IA** : Pipeline documentaire multi-stage (7 sections, 3 batches paralleles httpx). Collection: dossier_express. 12 etapes tracees.
- **Relecture admin** : Collection partagee premium_analyses (filtre par type). Garde-fou assert_premium_analyses_entry.

## Pipeline Dossier Express IA (OPTIMISE 29/03/2026)
- 7 sections : synthese, pieces, chrono, juridique, forces_vigilance, strategie_prejudices, plan_conclusion
- 3 batches paralleles via httpx streaming async (plus LlmChat bloquant)
- Chaque appel < 40s (sous le timeout 60s du proxy Emergent)
- Rapport total : ~26,000 chars, PDF ~38KB
- Temps pipeline total : ~113s (optimise de 186s, gain 39%)
- Deux chemins : PATH A (cle native Anthropic) / PATH B (Emergent multi-stage httpx)
- Voir `/app/DIAGNOSTIC_PIPELINE_DOSSIER_EXPRESS.md`

## Fichiers de centralisation (CONSOLIDATION 29/03/2026)
- `/app/backend/constants/statuses.py` — Source unique de verite pour TOUS les statuts
- `/app/backend/constants/workflows.py` — Config pricing, retry, quotas
- `/app/backend/constants/guards.py` — Assertions anti-contamination croisee
- `/app/ARCHITECTURE_GUARDRAILS.md` — Documentation complete d'architecture

## Tests de non-regression
- `/app/backend/tests/test_consolidation.py` — 16 tests unitaires
- `/app/backend/tests/test_consolidation_audit.py` — 19 tests API
- `/app/backend/tests/test_dossier_express_e2e.py` — 10 tests E2E
- `/app/test_reports/iteration_150.json` — 16/16 PASS (100% backend, 100% frontend)
- Commande: `cd /app/backend && python3 -m pytest tests/ -v`

## Etat des services (Preview)
- IA Anthropic : OK (emergent_fallback + pipeline multi-stage httpx)
- Paiement Stripe : ERREUR (cle test invalide)
- Email Resend : OK (sandbox)
- Stockage S3 : NON CONFIGURE (manque S3_ACCESS_KEY + S3_SECRET_KEY)
- Database MongoDB : OK
- Mode lancement : Ouvert
- Dossier Express Pipeline : OK (optimise 29/03/2026 — 113s)

## Backlog
### P0 : TERMINE
- Fix pipeline Dossier Express IA (multi-stage) — DONE 29/03/2026
- UX Premium vue de traitement Dossier Express — DONE 29/03/2026
- Consolidation architecture — DONE 29/03/2026
- Validation E2E StrategiIA — DONE 29/03/2026
- Validation E2E Dossier Express — DONE 29/03/2026
- Livrable Final consolidation — DONE 29/03/2026
- Endpoint admin-bypass Dossier Express — DONE 29/03/2026
- Optimisation temps pipeline (186s→113s, -39%) — DONE 29/03/2026

### P1 : Cles de production
- ANTHROPIC_API_KEY live → elimine le multi-stage, 1 appel = ~30s
- STRIPE_API_KEY live
- Webhook Stripe live
- S3 config (S3_ACCESS_KEY + S3_SECRET_KEY)
- Domaine Resend verifie

### P2 : Integration HubSpot CRM (en attente credentials)
### P3 : Consolidation moteurs PDF
### P4 : Contenu juridique final
