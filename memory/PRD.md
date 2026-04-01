# PRD — Stratégie & Expertise Santé (S.E.S)

## Problème original
Application web premium de conseil en maladie professionnelle (AT/MP). Scanner documentaire, contenu stratégique (IP, PGPF), mascotte IA "Straté", dashboard Admin, IA d'analyse (StrategiIA).

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + MongoDB
- **Intégrations**: Claude Sonnet 4.5 (Emergent LLM Key), Stripe (test), Resend (sandbox)

## Zones gelées

### Hero HomePage — VERROUILLÉ 01/04/2026
- Hauteur : 617px — above-the-fold sur 1366×768
- Paddings : `lg:pt-20` (top), `lg:pb-1` (bottom)
- Header fixed : 76px → badge à 80px (4px de marge)
- Ligne finale : bottom=613px → 155px de marge
- Fichier : `HomePage.jsx` lignes 139-350
- Commentaire protecteur dans le code
- Baselines : `hero-desktop.png`, `hero-laptop-1366.png`, `hero-mobile.png`
- Tests : suite 6 (Hero above-fold) dans `visual.spec.ts`

### Header — VERROUILLÉ 01/04/2026
- Fichier : `Header.jsx`
- Commentaire protecteur dans le code

### Frontend global — GELÉ 01/04/2026
- `layout-guardrails.css` : 13 règles CSS
- `FRONTEND_GUARDRAILS.md` : charte anti-casse
- `RELEASE_VISUAL_CHECKLIST.md` : checklist obligatoire
- `visual.spec.ts` : 341 tests Playwright
- 117 captures baseline

## Tâches accomplies

### Session actuelle (01/04/2026)
- Fix centrage "Choisir mon médecin conseil" : `text-center lg:text-left`
- Gel définitif du frontend : tests, baselines, guardrails
- Hero premium chirurgical : micro-optimisation visuelle
- Suppression doublon disclaimer mobile
- Fix badge coupé par header fixed : `lg:pt-20`
- Fix ligne finale : compression marges internes (-18px)
- Fix lisibilité badge + ligne finale : opacités renforcées
- Gel définitif Hero : commentaire renforcé, guardrails mis à jour, baselines régénérées

## Backlog

### P0 (Aucun)

### P1
- Protocole de lancement Live (Stripe live, AWS S3, Resend)

### P2
- HubSpot CRM (attente credentials)

### P3
- S3 PDF Download (attente credentials AWS)

## Credentials de test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client: `demo@test.com` / `Password123!`

## Contraintes utilisateur
- NO INITIATIVES: Exécuter uniquement ce qui est demandé
- Format de rapport obligatoire (CAUSE RACINE, BLOCS CONCERNÉS, etc.)
- Langue: Français uniquement
- FRONTEND GELÉ + HERO GELÉ : Voir FRONTEND_GUARDRAILS.md
