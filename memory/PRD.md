# PRD — Stratégie & Expertise Santé (S.E.S)

## Problème original
Application web premium de conseil en maladie professionnelle (AT/MP). Scanner documentaire, contenu stratégique (IP, PGPF), mascotte IA "Straté", dashboard Admin, IA d'analyse (StrategiIA).

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + MongoDB
- **Intégrations**: Claude Sonnet 4.5 (Emergent LLM Key), Stripe (test), Resend (sandbox)

## Tâches accomplies

### Session précédente
- Scanner documentaire natif (caméra mobile)
- Contenu stratégique IP & PGPF intégré
- Mascotte Straté (visuel + TTS français + backend CRUD complet)
- Admin Conseils Straté (composant AdminConseilsStrate.jsx)
- Backend `/api/conseils` (CRUD, tracking, analytics, rotation quotidienne)
- Audit linguistique frontend (accents)
- Audit PDF encoding (cp1252)
- Fix variable `etape` (AccidentTravailPage)

### Session actuelle (01/04/2026)
- **Fix centrage "Choisir mon médecin conseil"** : `text-center lg:text-left` sur la colonne texte (P0 résolu)
- **Gel définitif du frontend — Anti-régression** :
  - `/frontend/src/styles/layout-guardrails.css` : Protection CSS globale définitive (box-sizing, overflow-x, word-wrap, media max-width)
  - `/FRONTEND_GUARDRAILS.md` : Charte anti-casse avec interdictions et obligations
  - `/RELEASE_VISUAL_CHECKLIST.md` : Checklist visuelle obligatoire avant mise en prod
  - `/frontend/tests/visual.spec.ts` : Tests Playwright de non-régression (scroll horizontal, CTA, cartes, texte, hero, header, menu mobile)
  - `/frontend/playwright.config.ts` : Configuration Playwright
  - 51 captures de baseline dans `/frontend/tests/visual-baseline/`
  - Zones gelées (commentaires) dans Hero (HomePage.jsx) et Header (Header.jsx)
  - Import guardrails CSS dans index.css
  - Tous tests PASS : 0 échec sur scroll, CTA, cartes, texte, hero, header, menu

## Backlog

### P0 (Aucun)
Aucune tâche critique en cours.

### P1
- Exécution du protocole de lancement Live (clés Stripe live, AWS S3, domaine Resend)

### P2
- Intégration HubSpot CRM (en attente credentials)

### P3
- S3 PDF Download (en attente credentials AWS)

### P4
- Contenu juridique final

## Credentials de test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client: `demo@test.com` / `Password123!`

## Contraintes utilisateur
- NO INITIATIVES: Exécuter uniquement ce qui est demandé
- NE PAS modifier la logique métier, routes, data-testid, tracking
- Clés MongoDB TOUJOURS en ASCII (pas d'accents)
- Format de rapport obligatoire (CAUSE RACINE, BLOCS CONCERNÉS, etc.)
- Langue: Français uniquement
- FRONTEND GELÉ : Voir FRONTEND_GUARDRAILS.md et RELEASE_VISUAL_CHECKLIST.md
