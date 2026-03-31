# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA isoles.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 — via Emergent LLM proxy
- **PDF** : fpdf2 (Premium Signature V2) | **Email** : Resend | **Paiements** : Stripe + PayPal

## Header Premium (30/03/2026)
- Logo : h-11 (ancrage de marque renforce)
- Hauteur : min-h 4.75rem desktop (plus statutaire)
- Fond : bg/80 transparent au repos, bg/95 au scroll, bordure bottom doree au scroll
- CTA : bouton outline dore statutaire (non agressif)
- Navigation : separateurs verticaux, tracking-wide, espacement genereux
- Dropdowns : fond #111110, bordure doree subtile, ombre profonde
- Dossier Express : icone Zap doree
- Tests : 100% PASS iteration 161 (29 tests desktop + mobile)

## Phase 2 Premium Home (30/03/2026)
- H1 : leading-[1.18] plus respirant, tailles lg:2.1rem xl:2.3rem
- Image droite : halo dore diffus, fondu haut+bas, filet dore horizontal bas, ombre profonde 70px, max-w 400px
- CTA Urgent : "Reponse sous 2h" remplace par "Besoin urgent ?" CTA integre (event alerte-urgente:open -> modal)
- Mascotte : scroll-reveal > 300px (Hero reste centre absolu)
- AlerteUrgente : bouton flottant scroll-reveal > 400px + ecoute event alerte-urgente:open
- Tests : 100% PASS iteration 161 (6/6 corrections verifiees)

### Structure implementee (13 sections)
1. **Hero** — Two-column propre (55fr/45fr) — V2 above-the-fold
2. **Dossier Express strip** — Bande urgence rouge
3. **Pourquoi ce site existe** — Narratif fondateur, fond ivoire #F8F5EF
4. **Nos deux intelligences** — StrategiIA vs Dossier Express IA
5. **Risques** — Ce que vous risquez sans accompagnement
6. **Ecosysteme** — 8 services en grille
7. **Methode S.E.S** — 5 etapes du processus
8. **Medecin conseil** — Enjeu financier majeur
9. **Confidentialite** — 3 piliers
10. **Chiffres cles** — Contexte national (4 stats animees)
11. **Confiance** — 4 piliers de credibilite
12. **Temoignages** — 6 temoignages anonymises
13. **CTA Final** — Signature emotionnelle

### Direction artistique
- Palette : #0a0a08 (fond), #111 (cartes), #C9A84C (or), #F8F5EF (ivoire)
- Typographie : Playfair Display (titres), sans-serif (corps)
- Theme : sombre, premium, luxe maitrise, or elegant

### Tests Homepage : 100% PASS (iteration 156-162)

## Correction Blocs Fondateur Desktop (31/03/2026)
- **Probleme** : Les 3 blocs CTA (Analyse IA, Documents, Orientation) sur la photo du fondateur etaient dupliques et inutiles sur desktop
- **Correction** : Ajout de `lg:hidden` aux 3 blocs dans la section "Pourquoi ce site existe" pour les masquer sur desktop uniquement
- **Fichier modifie** : HomePage.jsx (lignes 393, 403, 413)
- **Mobile** : Blocs conserves et visibles

## Fonctionnalites implementees
- Mascotte Strate : TTS francais robuste (speakFrench), widget desktop + mobile, rotation quotidienne des conseils
- Admin Conseils Strate : CRUD complet, analytics, stats, highlight/priorite
- Backend conseils : /api/conseils/* (today, view, click, conversion, admin endpoints)
- ChatBot : Orienteur ultra-court (3 questions max), prompt strict
- PDF Premium Signature V2
- DataConsentBox : Variantes adaptees
- Document Scanner : Camera native mobile (pas d'auto-crop)

## Correction Orthographique ASCII (30/03/2026)
- **Probleme** : Script de remplacement global avait corrompu les variables, cles DB, data-testid, noms de composants avec des accents
- **Correction** : Tous les identifiants programmatiques restaures en ASCII, texte affiche conserve avec accents francais
- **Fichiers corriges** : AlerteUrgente.jsx, AgendaPage.jsx, ContactPage.jsx, useAdminTheme.js, CalculatriceAAHPage.jsx, HomePage.jsx, AccidentTravailPage.jsx, ExpertiseMedicalePage.jsx, ProtectionJuridiquePage.jsx, AdminConseilsStrate.jsx, SimulateurPage.jsx, AdminDashboard.jsx, App.js, MentionsLegalesPage.jsx, PolitiqueConfidentialitePage.jsx, MedecinConseilPage.jsx, AvisPage.jsx
- **Bug critique corrige** : AlerteUrgente envoyait "telephone" (accentue) au backend qui attendait "telephone" (ASCII) -> formulaire alerte urgente non fonctionnel
- **Bug Admin corrige** : AdminDashboard lisait last_results.eligible (accentue) mais backend renvoyait "eligible" (ASCII)
- **Tests** : 100% PASS iteration 162 (10/10 backend, 13/13 frontend)

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
