# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA specialises.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4 (natif) + Fallback Emergent Universal Key
- **PDF** : fpdf2 + jsPDF | **Email** : Resend | **Paiements** : Stripe + PayPal | **Stockage** : S3

## Agents IA V2 Premium
- StrategiIA (8.97/10) et Dossier Express IA (9.15/10)
- Fonctionnels via cle Anthropic native OU Emergent Universal Key (fallback)

## Pipeline de Securite Paiement (DONE)
- Double protection pre-paiement : Launch Mode + LLM Health Check
- Pipeline post-paiement fail-safe avec 8 etapes tracees
- delivery_status + processing_step + notifications admin/client

## Bascule Commerciale (DONE)
- Mode Soft Launch (Ouvert/Controle/Indisponible)
- Monitoring Live 7 KPIs
- Suivi Client Temps Reel (/dossier-express/suivi)
- Diagnostic Services Admin (/admin/services-status)
- Documents : CHECKLIST_LIVE.md, STRATEGIE_SOFT_LAUNCH.md, PROTOCOLE_TESTS_LIVE.md

## Bug Fix - StrategiIA accessible en mode admin (DONE - 29 mars 2026)
- Cause : ANTHROPIC_API_KEY vide bloquait tous les utilisateurs y compris admins
- Fix : Fallback Emergent Universal Key (emergentintegrations) quand cle native absente
- _llm_sync_call utilise cle native en priorite, sinon emergentintegrations
- Health check enrichi (/api/health/llm) verifie les deux cles
- Endpoint diagnostic (/api/admin/services-status) pour visibilite complete
- UI Admin : panneau "Etat des services" avec 6 services couleur-codes

## Tests passes
- iteration_140-142 : UI + Dark Mode + Premium (61/61)
- iteration_143 : Pipeline securite (16/16)
- iteration_144 : Bascule commerciale (25/25)
- iteration_145 : Bug fix IA + diagnostic (19/19)
- Total cumule : 121 tests, 0 echec

## Etat des services (Preview)
- IA Anthropic : OK (emergent_fallback)
- Paiement Stripe : ERREUR (cle test invalide)
- Email Resend : OK (sandbox)
- Stockage S3 : NON CONFIGURE
- Database MongoDB : OK
- Mode lancement : Ouvert

## Backlog
### P1 : Cles de production
- Fournir ANTHROPIC_API_KEY live
- Fournir STRIPE_API_KEY live (sk_live_...)
- Configurer webhook Stripe live
- Configurer S3 (AWS_ACCESS_KEY_ID, etc.)
- Verifier domaine Resend

### P2 : Integration HubSpot CRM
### P3 : Consolidation moteurs PDF
### P4 : Contenu juridique final
