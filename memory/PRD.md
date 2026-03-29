# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA isoles.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 — via Emergent LLM proxy
- **PDF** : fpdf2 (Premium Signature V2 - 30/03/2026) | **Email** : Resend | **Paiements** : Stripe + PayPal

## PDF Premium Signature V2 (30/03/2026)

### Ameliorations visuelles (Dossier Express + StrategiIA)
1. **Espacement augmente** : section_title +60%, body_text line-height 4.2→4.8, bullet spacing +88%, lignes vides +67%
2. **Hierarchie renforcee** : sous-titres colores par service (or/navy), titres 10→10.5pt
3. **Closing standardise** : bloc officiel identique sur tous les PDFs
4. **Footer officiel** : `(c) 2026 SES -- SES-2026-XXXXX -- Document confidentiel -- Analyse preliminaire a visee informative -- strategie-expertise-sante.fr`
5. **Mention confidentialite** : bloc discret avant la signature
6. **Signature emotionnelle** : "Vous n'etes plus seul face a votre combat. Dorenavant, S.E.S est votre bouclier."

### Fichier modifie
- `/app/backend/utils/pdf.py` — SEUL fichier modifie

## Corrections precedentes (29-30/03/2026)

### DataConsentBox variants
- `StrategiIA.jsx` : `variant="informations"`
- `ContactPage.jsx` : `variant="informations"`
- `DossierExpressPage.jsx` : variant defaut `"documents"` + toujours visible

### Robot assistant refonte
- Bulle texte supprimee, prompt reecrit (orienteur ultra-court), limite 3 questions
- Backend chatbot branche sur Emergent LLM proxy

### Bugs corriges
- Focus PDF page A propos (lazy-load)
- Outline bleu "Outils" navbar
- Email obligatoire Question urgente

## Etat des services
- IA Anthropic (Emergent proxy) : OK
- Paiement Stripe : TEST MODE
- Email Resend : OK (sandbox)
- Stockage S3 : NON CONFIGURE
- Database MongoDB : OK

## Backlog
### P0 : TERMINE

### P1 : Cles de production
- STRIPE_API_KEY live
- S3 config
- Domaine Resend verifie

### P2 : Integration HubSpot CRM (en attente credentials)
### P4 : Contenu juridique final
