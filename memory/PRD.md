# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 (natif) + Fallback Emergent Universal Key (streaming httpx)
- **PDF** : fpdf2 + jsPDF | **Email** : Resend | **Paiements** : Stripe + PayPal

## Services (ISOLÉS — voir CONSOLIDATION_ARCHITECTURE.md)
- **StrategiIA** : Analyse strategique MP/AT. Collection: strategiia_analyses. Premium: asyncio.gather 2 appels paralleles.
- **Dossier Express IA** : Pipeline documentaire complet. Collection: dossier_express. 12 etapes tracees.
- **Relecture admin** : Collection partagee premium_analyses (filtre par type). Garde-fou assert_premium_analyses_entry.

## Fichiers de centralisation (CONSOLIDATION 29/03/2026)
- `/app/backend/constants/statuses.py` — Source unique de verite pour TOUS les statuts
- `/app/backend/constants/workflows.py` — Config pricing, retry, quotas
- `/app/backend/constants/guards.py` — Assertions anti-contamination croisee
- `/app/CONSOLIDATION_ARCHITECTURE.md` — Documentation complete d'architecture

## Tests de non-regression
- `/app/backend/tests/test_consolidation.py` — 16 tests unitaires
- `/app/backend/tests/test_consolidation_audit.py` — 19 tests API
- Total: 35 tests, 100% pass
- Commande: `cd /app/backend && python3 -m pytest tests/ -v`

## Etat des services (Preview)
- IA Anthropic : OK (emergent_fallback + streaming parallele)
- Paiement Stripe : ERREUR (cle test invalide)
- Email Resend : OK (sandbox)
- Stockage S3 : NON CONFIGURE
- Database MongoDB : OK
- Mode lancement : Ouvert

## Backlog
### P1 : Cles de production
- ANTHROPIC_API_KEY live → elimine le split, 1 appel = ~30s
- STRIPE_API_KEY live
- Webhook Stripe live
- S3 config
- Domaine Resend verifie

### P2 : Integration HubSpot CRM
### P3 : Consolidation moteurs PDF
### P4 : Contenu juridique final
