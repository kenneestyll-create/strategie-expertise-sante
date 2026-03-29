# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA specialises.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 (natif) + Fallback Emergent Universal Key (streaming httpx parallele)
- **PDF** : fpdf2 + jsPDF | **Email** : Resend | **Paiements** : Stripe + PayPal | **Stockage** : S3

## Agents IA V2 Premium
- StrategiIA (8.97/10) et Dossier Express IA (9.15/10)
- Fonctionnels via cle Anthropic native OU Emergent Universal Key (fallback streaming)
- Premium Emergent: 2 appels LLM PARALLELES (asyncio.gather) pour contourner le 60s gateway timeout
- Sections 1-5 et sections 6-9 generes independamment puis assembles
- Temps: ~57s backend, ~90s UX totale

## Pipeline de relecture expert (CORRIGE 29/03/2026)
- `premium_analyses` collection : file d'attente relecture pour StrategiIA ET Dossier Express
- Chaque entry a : type, email, status, relecture_expert_required=true, dossier_id
- admin-bypass-premium cree maintenant une entree automatiquement
- 47/47 documents ont relecture_expert_required=True
- Workflow: En attente -> Traiter -> En cours -> Relire/Valider -> Valide -> Envoyer au client

## Pipeline de Securite Paiement (DONE)
- Double protection pre-paiement : Launch Mode + LLM Health Check
- Pipeline post-paiement fail-safe avec 8 etapes tracees
- delivery_status + processing_step + notifications admin/client

## Bascule Commerciale (DONE)
- Mode Soft Launch (Ouvert/Controle/Indisponible)
- Monitoring Live 7 KPIs
- Suivi Client Temps Reel (/dossier-express/suivi)
- Diagnostic Services Admin (/admin/services-status)

## Tests passes
- iteration_140-145 : 121 tests, 0 echec
- Audit timing 29/03/2026 : 57s backend, 90s UX totale
- Test UI admin : Formulaire -> Teaser -> Basic -> Premium COMPLET
- Test admin relecture : StrategiIA 5 items, Dossier Express 42 items

## Etat des services (Preview)
- IA Anthropic : OK (emergent_fallback + streaming parallele)
- Paiement Stripe : ERREUR (cle test invalide)
- Email Resend : OK (sandbox)
- Stockage S3 : NON CONFIGURE
- Database MongoDB : OK
- Mode lancement : Ouvert

## Backlog
### P1 : Cles de production
- Fournir ANTHROPIC_API_KEY live (elimine le split, retour a 1 appel = ~30s)
- Fournir STRIPE_API_KEY live
- Configurer webhook Stripe live
- Configurer S3
- Verifier domaine Resend

### P2 : Integration HubSpot CRM
### P3 : Consolidation moteurs PDF
### P4 : Contenu juridique final
