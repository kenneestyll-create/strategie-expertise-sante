# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA isoles.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 — PATH A (natif, appel unique 8000 tokens) / PATH B (Emergent proxy, multi-stage httpx 7 sections)
- **PDF** : fpdf2 + jsPDF | **Email** : Resend | **Paiements** : Stripe + PayPal

## Services (ISOLES — voir ARCHITECTURE_GUARDRAILS.md)
- **StrategiIA** : Analyse strategique MP/AT. Collection: strategiia_analyses.
- **Dossier Express IA** : Pipeline documentaire optimise. Collection: dossier_express. 8 etapes tracees.
- **Relecture admin** : Collection partagee premium_analyses (filtre par type).

## Pipeline Dossier Express IA (OPTIMISE 29/03/2026)

### Performance mesuree (PATH B — Emergent proxy)
| Metrique | Avant optimisation | Apres optimisation |
|----------|-------------------|-------------------|
| Temps total moyen | 186s | 95-110s |
| Parallelisme batches | Sequentiel (LlmChat bloquant) | Parallele reel (httpx streaming async) |
| LLM (% du total) | 99.5% | 99.5% |
| PDF generation | <0.5s | <0.5s |
| Email | <0.4s | <0.4s |
| Stockage S3 | Non configure | Non configure |

### Performance estimee (PATH A — Cle Anthropic native)
- Appel unique direct : ~25-35s (pas de batching necessaire)
- max_tokens=8000 (vs 1500 par section en multi-stage)
- documents_text: jusqu'a 12000 chars (vs 8000 avant)

### Structure du pipeline
- 7 sections : synthese, pieces, chrono, juridique, forces_vigilance, strategie_prejudices, plan_conclusion
- 3 batches paralleles via httpx streaming async
- Chaque appel < 40s (sous le timeout 60s du proxy Emergent)
- Instrumentation complete : timings par etape stockes en DB

### Qualite validee (29/03/2026 — 3 dossiers test)
| Dossier | Documents | Chars | Sections | Qualite |
|---------|-----------|-------|----------|---------|
| Leger (2 docs) | 2 | 24,671 | 21 | OK |
| Moyen (7 docs) | 7 | 25,389 | 26 | OK |
| Lourd (18 docs) | 18 | 25,975 | 31 | OK |

### Frontend UX attente
- Polling : 3s (vs 5s avant)
- Duree affichee : "1 a 3 minutes"
- Message erreur : "Restez sur cette page" (pas de "quittez/fermez")
- 7 etapes visuelles premium

## Tests de non-regression
- `/app/test_reports/iteration_150.json` — 16/16 PASS (post-endpoint fix)
- `/app/test_reports/iteration_151.json` — 13/13 PASS (post-optimisation pipeline)
- `/app/backend/tests/test_pipeline_optimization.py`

## Etat des services (Preview)
- IA Anthropic : OK (Emergent fallback multi-stage httpx)
- Paiement Stripe : TEST MODE
- Email Resend : OK (sandbox)
- Stockage S3 : NON CONFIGURE (manque S3_ACCESS_KEY + S3_SECRET_KEY)
- Database MongoDB : OK

## Backlog
### P0 : TERMINE
- Fix pipeline Dossier Express IA (multi-stage parallele) — DONE 29/03/2026
- UX Premium vue de traitement — DONE 29/03/2026
- Consolidation architecture — DONE 29/03/2026
- Livrable Final consolidation — DONE 29/03/2026
- Endpoint admin-bypass — DONE 29/03/2026
- Optimisation temps pipeline (186s→95-110s, -40%) — DONE 29/03/2026
- Instrumentation timings — DONE 29/03/2026
- Validation qualite 3 dossiers — DONE 29/03/2026
- UX: polling 3s, messages ameliores — DONE 29/03/2026

### P1 : Cles de production
- ANTHROPIC_API_KEY native → pipeline ~30s
- STRIPE_API_KEY live
- S3 config (S3_ACCESS_KEY + S3_SECRET_KEY)
- Domaine Resend verifie

### P2 : Integration HubSpot CRM (en attente credentials)
### P3 : Consolidation moteurs PDF
### P4 : Contenu juridique final
