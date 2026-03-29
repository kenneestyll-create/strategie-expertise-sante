# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA specialises.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 (natif) + Fallback Emergent Universal Key (streaming httpx)
- **PDF** : fpdf2 + jsPDF | **Email** : Resend | **Paiements** : Stripe + PayPal | **Stockage** : S3

## Agents IA V2 Premium
- StrategiIA (8.97/10) et Dossier Express IA (9.15/10)
- Fonctionnels via cle Anthropic native OU Emergent Universal Key (fallback streaming)
- Premium: analyse en 2 appels streaming pour contourner le gateway timeout de 60s du proxy Emergent

## Pipeline de Securite Paiement (DONE)
- Double protection pre-paiement : Launch Mode + LLM Health Check
- Pipeline post-paiement fail-safe avec 8 etapes tracees
- delivery_status + processing_step + notifications admin/client

## Bascule Commerciale (DONE)
- Mode Soft Launch (Ouvert/Controle/Indisponible)
- Monitoring Live 7 KPIs
- Suivi Client Temps Reel (/dossier-express/suivi)
- Diagnostic Services Admin (/admin/services-status)

## Bug Fix - StrategiIA Premium Timeout (DONE - 29 mars 2026)
- Cause racine : proxy Emergent gateway timeout 60s, prompt premium trop lourd (>9000 chars)
- Fix : streaming httpx direct + decoupe en 2 appels (Part 1: sections 1-5, Part 2: sections 6-9)
- Resultat : analyses premium de 13000+ chars generees en ~90s
- Fix supplementaire : bouton "Debloquer" readwall active en mode admin sans email

## Tests passes
- iteration_140-145 : 121 tests, 0 echec
- Test pratique UI admin 29/03/2026 : Formulaire -> Loading -> Teaser -> Readwall bypass -> Basic -> Premium COMPLET

## Etat des services (Preview)
- IA Anthropic : OK (emergent_fallback + streaming)
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
