# RAPPORT P1-6 (v2) — AUDIT UX MOBILE TRANSVERSE, RE-VÉRIFIÉ SUR CODE ACTUEL
Date : 04/08/2026 — Complète et actualise l'audit initial du 31/07/2026.
Méthode : re-vérification de CHAQUE constat du 31/07 sur le code et le rendu actuels
(mesures runtime Playwright 390×844 + inspection code + mesure bundle production réelle).
**Aucune modification de code appliquée — audit 100 % lecture seule, conformément à l'ordre.**

## Contexte data (rappel GSC)
Mobile = 73 % des clics, CTR mobile 3,87 % vs desktop 2,01 %, position moyenne mobile 8,18.
Toute dégradation UX mobile touche 3 clics sur 4.

---

## STATUT RE-VÉRIFIÉ DES 7 CONSTATS (04/08/2026)

### 🔴 P0-A — Straté plein écran auto-ouvert sur mobile : **CONFIRMÉ (preuve du jour)**
- Mesure runtime 390×844 : après scroll 45 % + 15 s, l'overlay Straté s'ouvre en
  `fixed inset-0` et couvre **100 % du viewport** (`fullscreen_overlays: 1` mesuré,
  capture à l'appui — le contenu de la page est totalement masqué).
- Code : `useStrateTriggers.js` (scroll ≥ 40 % OU 15 s, 1×/24h) ne contient **aucune
  condition de viewport** ; `ChatBot.jsx` ligne ~371 : `fixed inset-0 sm:inset-auto...`.
- Impact : définition exacte de l'« interstitiel intrusif » pénalisé par Google sur mobile.
- Reco inchangée : sur mobile (< 640px), pas d'auto-ouverture plein écran — badge/pastille
  discret, ouverture plein écran au clic volontaire uniquement. Desktop inchangé.
- Faisabilité : FACILE (condition viewport dans `useStrateTriggers.js`).

### 🟠 P1-A — Thumb du slider Taux IPP : **CONFIRMÉ (mesuré 16×16 px ce jour)**
- Mesure runtime : `[role="slider"]` du `ipp-taux-slider` = **16×16 px** (norme tactile : 44 px).
- Code : `components/ui/slider.jsx` → `h-4 w-4` (défaut shadcn, jamais surchargé).
- Page n°1 du site (150 clics/28 j) ; la précision 1–100 % au doigt est le cœur de l'outil.
- Reco : thumb 24–28 px visuel + hit-area 44 px + saisie numérique alternative (champ ou −/+).
- Faisabilité : FACILE.

### ✅ P1-B — Cumul d'éléments sticky sur la home : **RÉSOLU / NON REPRODUIT**
- La bannière « Expertise imminente ? 97 EUR » est aujourd'hui une **section inline** dans le
  flux (`HomePage.jsx` ~412, aucun `fixed/sticky`). Mesure runtime à scroll 600 px : aucun
  élément fixé en bas ; seul le header sticky de **68 px** subsiste (~8 % du viewport — standard).
- **Aucune action requise.** (Constat du 31/07 caduc suite aux évolutions de la home.)

### 🟡 P2-A — Corps de texte des guides à 14 px : **CONFIRMÉ**
- `GuidePreviewBody.jsx` : `prose-p:text-sm prose-li:text-sm` (14 px) sur la lecture longue.
- Reco : 16 px mobile (`text-base sm:text-sm`) — améliore confort + dwell time (signal SEO).
- Faisabilité : FACILE — impacte le rendu des 17 guides : à valider explicitement avant exécution.

### ✅ P2-B — Badge « Gratuit » avec césure (/dossier-express) : **OBSOLÈTE**
- Le badge n'existe plus sur /dossier-express (grep : aucune occurrence). **Aucune action.**

### 🟡 P2-C — Hauteur des inputs 36 px : **CONFIRMÉ**
- `components/ui/input.jsx` : `h-9` (36 px). Fonctionnel, perfectible sur tunnels payants. Optionnel.

### 🟡 P2-D — Bundle JavaScript monolithique : **CONFIRMÉ (mesure prod du jour)**
- `main.e925cd52.js` en production = **413 780 octets gzip** (mesuré ce jour) — identique au 31/07.
- Tout est chargé dès la home (admin, forum, studio inclus). INP/TBT mobile dégradés sur
  appareils modestes.
- Reco : code-splitting par route (React.lazy sur AdminDashboard, Forum, Studio, pages
  secondaires) — gain estimé 30-40 % sur le bundle initial.
- Faisabilité : MOYENNE/LOURDE — chantier transverse à planifier séparément.

---

## SYNTHÈSE PRIORISÉE ACTUALISÉE (5 constats actifs sur 7)
| # | Constat | Statut 04/08 | Impact SEO | Impact UX | Faisabilité |
|---|---|---|---|---|---|
| P0-A | Interstitiel Straté plein écran mobile | 🔴 Confirmé (preuve) | ÉLEVÉ | ÉLEVÉ | Facile |
| P1-A | Slider IPP 16 px | 🟠 Confirmé (mesuré) | Indirect (conversion) | ÉLEVÉ | Facile |
| P2-A | Texte guides 14 px | 🟡 Confirmé | Modéré (dwell time) | Modéré | Facile |
| P2-C | Inputs 36 px | 🟡 Confirmé | Nul | Faible | Facile |
| P2-D | Bundle 413 Ko gzip | 🟡 Confirmé (mesure prod) | Modéré (INP) | Modéré | Lourde |
| ~~P1-B~~ | ~~Cumul sticky home~~ | ✅ Résolu/non reproduit | — | — | — |
| ~~P2-B~~ | ~~Badge « Gratuit » césure~~ | ✅ Obsolète | — | — | — |

## PLAN D'EXÉCUTION PROPOSÉ (sur votre ordre uniquement)
1. **Lot 1 (rapide, fort impact)** : P0-A (badge Straté mobile) + P1-A (slider IPP tactile + saisie
   numérique). ~Une session, testable immédiatement, zéro risque sur les flux existants.
2. **Lot 2 (sur validation)** : P2-A (16 px guides — après votre GO explicite car modifie les 17
   guides) + P2-C (inputs 44 px sur tunnels payants).
3. **Lot 3 (chantier séparé)** : P2-D code-splitting — à planifier après les sujets convenus
   (progression client temps réel, SEO /dossier-express).

Aucune modification ne sera appliquée sans votre validation explicite de ce rapport.
