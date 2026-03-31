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
- Mascotte Straté (visuel + TTS hardcodé)
- Audit linguistique frontend (accents)
- Audit PDF encoding (cp1252)
- Fix variable `etape` → `etape` (AccidentTravailPage)

### Session actuelle (31/03/2026)
- **Refonte responsive globale définitive**:
  - Chaîne de confinement `overflow: clip` à chaque niveau DOM (html → body → #root → .App → main → sections)
  - `contain: paint` sur `main`
  - `clip-path: inset(0)` sur Hero (halos décoratifs)
  - `touch-action: pan-y; overscroll-behavior-x: none` global
  - Suppression du patch CSS App.css conflictuel (media query mobile qui écrasait Tailwind)
  - Scrollbar custom scopée desktop uniquement
  - Garde-fous CSS globaux: `section > div { overflow-x: clip; max-width: 100% }`, `section .grid > * { min-width: 0; max-width: 100% }`
  - `overflow-wrap: break-word` global sur textes dans les sections
- **Fix CTA ServicesPage**: Version mobile courte "Être accompagné" / desktop complète
- **Fix ContactPage**: Email break-all + overflow-wrap: anywhere + min-w-0 sur la chaîne flex/grid
- **Fix AboutPage**: Layout flex-col/sm:flex-row sur le download bar
- **Fix Header**: Logo `min-w-0` (au lieu de flex-shrink-0) + `overflow-x-clip` sur nav
- **Centrage optique Médecin Conseil**: Cards centrées sur mobile, font-sizes proportionnels
- **`100vw` → `100%`**: Supprimé dans index.css (body) et App.css (sections)
- **`overflow-hidden` → `overflow-clip`**: Toutes les sections de HomePage, DossierExpressPage, TarifsPage
- **Audit DOM 17 pages × 320px**: 17/17 PASS (0 overflow, scrollWidth = viewport)

## Backlog

### P0 (Aucun)
- Fix centrage "Choisir mon médecin conseil" sur mobile : CORRIGÉ (01/04/2026) — `text-center lg:text-left` sur la colonne texte

### P1
- Exécution du protocole de lancement Live (clés Stripe live, AWS S3, domaine Resend)

### P2
- Intégration HubSpot CRM (en attente credentials)
- Admin tips Straté (backend CRUD + frontend Admin tab + TTS français)

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
