# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA isoles.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 — via Emergent LLM proxy
- **PDF** : fpdf2 (premiumise 29/03/2026) | **Email** : Resend | **Paiements** : Stripe + PayPal

## Corrections effectuees (29-30/03/2026)

### DataConsentBox variants
- `StrategiIA.jsx` : `variant="informations"` (ne collecte pas de documents)
- `ContactPage.jsx` : `variant="informations"` (ne collecte pas de documents)
- `DossierExpressPage.jsx` : variant par defaut `"documents"` (collecte documents) + toujours visible (meme admin)

### Bug focus PDF - Page A propos
- Lazy-loading du PDF via IntersectionObserver (charge uniquement quand visible)
- Empeche le plugin PDF Chrome de voler le focus au chargement

### Bug outline bleu "Outils" navbar
- Ajout `outline-none focus:outline-none focus-visible:outline-none` sur dropdownBtnClass

### Email obligatoire - Question urgente
- Label "Email (optionnel)" → "Email *"
- Validation ajoutee : email requis + format basique

### Robot assistant - Refonte complete (30/03/2026)
- **Bulle texte supprimee** : plus de "StrategiIA — Je vous aide..." en bas a droite
- **Animation pulsante supprimee** sur le bouton robot
- **Prompt systeme reecrit** : orienteur ultra-court (1 phrase + 1 lien, 2 lignes max)
- **Limite 3 questions** par session (etait 5)
- **max_tokens reduit** de 350 a 100
- **Message d'accueil simplifie** 
- **Header robot** : "Assistant d'orientation — Je vous guide vers le bon outil"
- **Backend chatbot** : utilise Emergent LLM proxy (etait branche sur ANTHROPIC_API_KEY vide)

## Etat des services
- IA Anthropic (Emergent proxy) : OK
- Paiement Stripe : TEST MODE
- Email Resend : OK (sandbox)
- Stockage S3 : NON CONFIGURE
- Database MongoDB : OK

## Backlog
### P0 : TERMINE
- Toutes corrections ci-dessus

### P1 : Cles de production
- ANTHROPIC_API_KEY native (pipeline ~30s)
- STRIPE_API_KEY live
- S3 config (S3_ACCESS_KEY + S3_SECRET_KEY)
- Domaine Resend verifie

### P2 : Integration HubSpot CRM (en attente credentials)
### P3 : Consolidation moteurs PDF
### P4 : Contenu juridique final
