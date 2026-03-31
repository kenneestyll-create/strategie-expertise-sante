# PRD — Stratégie & Expertise Santé (S.E.S)

## Problème original
Application web premium de conseil en maladie professionnelle (AT/MP). Scanner documentaire, contenu stratégique (IP, PGPF), mascotte IA "Straté", dashboard Admin, IA d'analyse (StrategiIA).

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + MongoDB
- **Intégrations**: Claude Sonnet 4.5 (Emergent LLM Key), Stripe (test), Resend (sandbox)

## Tâches accomplies

### Sessions précédentes
- Scanner documentaire natif (caméra mobile)
- Contenu stratégique IP & PGPF intégré
- Mascotte Straté (visuel + TTS français + backend CRUD complet)
- Admin Conseils Straté (composant AdminConseilsStrate.jsx)
- Backend `/api/conseils` (CRUD, tracking, analytics, rotation quotidienne)
- Audit linguistique frontend (accents)
- Audit PDF encoding (cp1252)
- Refonte responsive globale (overflow-clip, 100vw → 100%, audit 17 pages)

### Session actuelle (01/04/2026)
- **Fix centrage "Choisir mon médecin conseil"** : `text-center lg:text-left`
- **GEL DÉFINITIF DU FRONTEND** :
  - `layout-guardrails.css` : 13 règles CSS anti-débordement
  - `FRONTEND_GUARDRAILS.md` : Charte anti-casse + 8 zones gelées + protocole obligatoire
  - `RELEASE_VISUAL_CHECKLIST.md` : Checklist visuelle avant prod
  - `visual.spec.ts` : 341 tests Playwright (10 suites × 13 pages × 8 résolutions)
  - 115 captures baseline dans `/frontend/tests/visual-baseline/`
  - Zones gelées documentées dans Hero + Header (commentaires code)
  - **341/341 tests PASS — 0 échec**

## Frontend — État gelé
Le frontend est officiellement gelé depuis le 01/04/2026.
Toute modification doit suivre le protocole dans `FRONTEND_GUARDRAILS.md`.

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
