# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA isoles.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 — PATH A (natif) / PATH B (Emergent proxy multi-stage)
- **PDF** : fpdf2 (premiumise 29/03/2026) | **Email** : Resend | **Paiements** : Stripe + PayPal

## PDF Premium Upgrade (29/03/2026)

### Fichier modifie
- `/app/backend/utils/pdf.py` — SEUL fichier modifie. Signatures identiques.

### Ameliorations visuelles
1. **Identite distincte par service**
   - StrategiIA : accents or/dore, ton strategique et emotionnel
   - Dossier Express : accents bleu marine, ton documentaire et structure
2. **Meilleure respiration** : espacement x2-3 entre sections, separateurs subtils
3. **Hierarchie renforcee** : titres 10pt bold avec barres d'accent colorees
4. **Inline markdown** : support **gras** et *italique* en milieu de phrase (fpdf2 markdown=True)
5. **Bullets colores** : or (StrategiIA) vs marine (Dossier Express)
6. **Callout boxes** : encadres sobres pour mots-cles (Important, Attention, Essentiel)

### Visuels utiles ajoutes
- **StrategiIA** : Jauge de vigilance (3 niveaux : Suivi recommande / Attention soutenue / Vigilance elevee) — basee sur l'analyse du contenu
- **Dossier Express** : Bandeau compact (nb pieces, pages, qualite extraction) + tableau detaille des documents

### Closing sections differenciees
- **StrategiIA** : "Votre situation, notre regard" — ton chirurgical, rassurant, orientant
- **Dossier Express** : "Ce que cette etude vous apporte" — ton methodique, credible, structurant
- **Signatures** : "Votre bouclier." (Strat) vs "La methode au service de vos droits." (DE)

### Tests de non-regression
- iteration_154: 10/10 backend + 4/4 frontend = 100% PASS
- 5 PDFs generes avec succes (29-40 KB, headers %PDF- valides)
- Routes, endpoints, pipelines, statuts: INTACTS

## DataConsentBox Variant Fix (29/03/2026)
- `DataConsentBox.jsx` : Supporte prop `variant` (`'informations'` | `'documents'` defaut)
- `StrategiIA.jsx` ligne 400 : `variant="informations"` (ne collecte pas de documents)
- `DossierExpressPage.jsx` ligne 714 : variant par defaut `"documents"` (collecte documents)
- Verifie visuellement : titre, description, accordion et checkbox adaptent le wording

## Etat des services
- IA Anthropic : OK (Emergent fallback)
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
- Premium PDF visual upgrade — DONE 29/03/2026
- DataConsentBox wording StrategiIA — DONE 29/03/2026

### P1 : Cles de production
- ANTHROPIC_API_KEY native (pipeline ~30s)
- STRIPE_API_KEY live
- S3 config (S3_ACCESS_KEY + S3_SECRET_KEY)
- Domaine Resend verifie

### P2 : Integration HubSpot CRM (en attente credentials)
### P3 : Consolidation moteurs PDF
### P4 : Contenu juridique final
