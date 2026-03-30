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
1. **Hero** — Two-column propre (contenu gauche 55fr + visuel droite 45fr) — hauteur maitrisee par padding, image aspect 3:4 contenue, zero element flottant
2. **Dossier Express strip** — Bande urgence rouge
3. **Pourquoi ce site existe** — Narratif fondateur, fond ivoire #F8F5EF, image arrondie
4. **Nos deux intelligences** — StrategiIA vs Dossier Express IA (cartes 2 colonnes: Ideal pour / Ce que vous recevez)
5. **Risques** — Ce que vous risquez sans accompagnement
6. **Ecosysteme** — 8 services en grille
7. **Methode S.E.S** — 5 etapes du processus
8. **Medecin conseil** — Enjeu financier majeur
9. **Confidentialite** — 3 piliers
10. **Chiffres cles** — Contexte national (4 stats animees)
11. **Confiance** — 4 piliers de credibilite
12. **Temoignages** — 6 temoignages anonymises
13. **CTA Final** — Signature emotionnelle "S.E.S est votre bouclier"

### Direction artistique
- Palette : #0a0a08 (fond), #111 (cartes), #C9A84C (or), #F8F5EF (ivoire)
- Typographie : Playfair Display (titres), sans-serif (corps)
- Theme : sombre, premium, luxe maitrise, or elegant
- Hero image : bords nets (pas de rounded), pas de bordure

### Tests Homepage : 100% PASS (iteration 156)
- Tous les data-testid verifies
- Tous les liens (CTAs, navigation, cartes) pointent vers les bonnes routes
- APIs backend fonctionnelles (/api/conseils/today, /api/visitors/increment, /api/dossier-express/weekly-count)
- Mascotte Strate fonctionne (widget + conseil du jour)

## Fonctionnalites implementees
- Mascotte Strate : TTS francais robuste (speakFrench), widget desktop + mobile, rotation quotidienne des conseils
- Admin Conseils Strate : CRUD complet, analytics, stats, highlight/priorite
- Backend conseils : /api/conseils/* (today, view, click, conversion, admin/list, admin/create, admin/update, admin/delete, admin/stats, admin/analytics)
- ChatBot : Orienteur ultra-court (3 questions max), prompt strict
- PDF Premium Signature V2 : Footer uniforme, clause de confidentialite, phrase emotionnelle
- DataConsentBox : Variantes adaptees (StrategiIA, Contact, DossierExpress)
- Document Scanner : Camera native mobile (pas d'auto-crop)

## Corrections precedentes (29-30/03/2026)
- DataConsentBox wording (informations au lieu de documents)
- Robot assistant refonte (orienteur ultra-court)
- Focus PDF page A propos (lazy-load IntersectionObserver)
- Outline bleu "Outils" navbar
- Email obligatoire Question urgente
- PDF Premium Signature V2

## Etat des services
- IA Anthropic (Emergent proxy) : OK
- Paiement Stripe : TEST MODE
- Email Resend : OK (sandbox)
- Stockage S3 : NON CONFIGURE (en attente credentials AWS)
- Database MongoDB : OK

## Backlog
### P1 : Cles de production (Checklist Live)
- STRIPE_API_KEY live
- S3 config (credentials AWS)
- Domaine Resend verifie

### P2 : Integration HubSpot CRM (en attente credentials)
### P4 : Contenu juridique final
