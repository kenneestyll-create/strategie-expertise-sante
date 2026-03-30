# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA isoles.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 — via Emergent LLM proxy
- **PDF** : fpdf2 (Premium Signature V2) | **Email** : Resend | **Paiements** : Stripe + PayPal

## Homepage Premium Refonte (30/03/2026)

### Structure implementee (13 sections)
1. **Hero** — Two-column premium (texte gauche + photo/cartes flottantes droite)
2. **Dossier Express strip** — Bande urgence rouge
3. **Pourquoi ce site existe** — Narratif fondateur, legitimite
4. **Nos deux intelligences** — StrategiIA vs Dossier Express IA (cartes comparatives)
5. **Risques** — Ce que vous risquez sans accompagnement
6. **Ecosysteme** — 8 services en grille (StrategiIA, DE, Accompagnement, Medecin, Calculatrices, Ressources, Scanner, RDV)
7. **Methode S.E.S** — 5 etapes du processus
8. **Medecin conseil** — Enjeu financier majeur
9. **Confidentialite** — 3 piliers (Confidentialite, Securite, Transparence)
10. **Chiffres cles** — Contexte national (4 stats animees)
11. **Confiance** — 4 piliers de credibilite
12. **Temoignages** — 6 temoignages anonymises
13. **CTA Final** — Signature emotionnelle "S.E.S est votre bouclier"

### Direction artistique
- Palette : #0a0a08 (fond), #111 (cartes), #C9A84C (or), #F8F5EF (ivoire)
- Typographie : Playfair Display (titres), sans-serif (corps)
- Theme : sombre, premium, luxe maitrise, or elegant

### Tests : 100% PASS
- 61/61 data-testid verifies
- Tous les liens valides
- APIs backend fonctionnelles
- Image hero chargee (Pexels CDN)

## Corrections precedentes (29-30/03/2026)
- DataConsentBox variants (StrategiIA, Contact, DossierExpress)
- Robot assistant refonte (orienteur ultra-court, 3 questions max)
- Focus PDF page A propos (lazy-load)
- Outline bleu "Outils" navbar
- Email obligatoire Question urgente
- PDF Premium Signature V2 (footer, confidentialite, signature emotionnelle)

## Etat des services
- IA Anthropic (Emergent proxy) : OK
- Paiement Stripe : TEST MODE
- Email Resend : OK (sandbox)
- Stockage S3 : NON CONFIGURE
- Database MongoDB : OK

## Backlog
### P1 : Cles de production
- STRIPE_API_KEY live
- S3 config
- Domaine Resend verifie

### P2 : Integration HubSpot CRM (en attente credentials)
### P4 : Contenu juridique final
