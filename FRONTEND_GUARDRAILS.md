# CHARTE ANTI-CASSE FRONTEND — Stratégie & Expertise Santé

> Ce document est la **loi absolue** du projet frontend.
> Toute modification qui enfreint ces règles est **rejetée sans discussion**.
> Date de gel : 01/04/2026

---

## ZONES GELÉES — INTERDITES DE REFONTE LIBRE

Les zones suivantes sont sanctuarisées. Toute modification nécessite :
- Validation visuelle complète desktop + mobile (8 résolutions)
- Screenshots AVANT/APRÈS
- Tests Playwright PASS à 100%

### 1. Hero Home (`HomePage.jsx` — `data-testid="hero-section"`) — VERROUILLÉ 01/04/2026
- **STATUT : GELÉ DÉFINITIVEMENT — Ne pas modifier sans ordre explicite**
- Hauteur validée : 617px (above-the-fold sur 1366×768 avec chrome navigateur)
- Paddings validés : `lg:pt-20` (top), `lg:pb-1` (bottom) — calibrés pour header fixed 76px
- Hiérarchie visuelle : badge → sous-titre métier → H1 → paragraphe → 3 puces → ligne 24/7 → preuve sociale + urgence → CTAs → micro-texte
- Position des CTA : "Besoin urgent ?", "Lancer mon analyse", "Être accompagné maintenant"
- Équilibre texte / image : colonne gauche 55% texte, colonne droite 45% photo
- Mini-cartes desktop (Analyse IA, Documents, Orientation) : positions figées
- Ligne finale "Analyse immédiate par IA..." : doit rester visible sans scroll
- Badge "Pionnier en France" : doit être entièrement visible sous le header
- **Toute modification nécessite : ordre explicite + validation desktop 1366×768 + mobile 360px + tests Playwright PASS**

### 2. Header Desktop (`Header.jsx`)
- Logo à gauche, navigation au centre, CTA "Réserver un appel" à droite
- Dropdown menus fonctionnels
- Aucun élément ne dépasse ou ne se chevauche
- **Interdit de modifier sans test desktop + mobile + menu ouvert**

### 3. Header Mobile (`Header.jsx`)
- Logo + bouton hamburger uniquement
- Menu hamburger ouvre un panneau complet
- Aucun scroll horizontal causé par le menu
- **Interdit de modifier sans test sur 360/375/390/412 px**

### 4. Menu Mobile Ouvert
- Panneau plein écran
- Navigation complète accessible
- Fermeture propre (bouton X ou tap extérieur)
- **Interdit de modifier sans test mobile complet**

### 5. CTA Principaux (toutes pages)
- Boutons "Lancer mon analyse", "Être accompagné maintenant", "Choisir mon médecin conseil"
- Doivent toujours rentrer dans le viewport mobile (360px minimum)
- Texte jamais tronqué
- **Interdit d'ajouter du texte long sans version mobile courte (`sm:hidden` / `hidden sm:inline`)**

### 6. Blocs Statistiques / Cartes Mobile
- Cartes chiffrées (800–3000 EUR, x10, etc.)
- Centrées sur mobile (`items-center text-center` / `lg:items-start lg:text-left`)
- Grille 2 colonnes + pleine largeur en dessous
- **Interdit de changer la grille sans test mobile**

### 7. Sections à Encadrés
- "Risque d'un mauvais choix", "Dossier Express", blocs d'information
- Bordures, paddings, arrondis validés
- Aucun ne doit dépasser à droite du viewport
- **Interdit de modifier les paddings sans audit mobile**

### 8. Largeurs / Paddings / Alignements Critiques
- Toutes les sections utilisent : `max-w-{size} mx-auto px-4 sm:px-6 lg:px-8`
- Ce pattern est la norme — ne jamais le remplacer par `100vw`, `w-screen`, ou des paddings asymétriques
- `overflow-clip` sur toutes les sections (jamais `overflow-hidden`)
- **Interdit de modifier ce pattern sans audit 8 résolutions**

---

## INTERDICTIONS ABSOLUES

- Utiliser `whitespace-nowrap` sur un CTA long
- Utiliser `min-width` rigide sur mobile
- Utiliser `position: absolute` décoratif sans borne claire (`overflow: clip` ou `clip-path`)
- Utiliser des badges flottants non testés mobile
- Utiliser des tailles de police "à l'oeil" — respecter la hiérarchie validée
- Créer un hero plus haut que le premier écran desktop (above-the-fold)
- Agrandir un titre sans vérifier l'impact sur le fold
- Modifier les paddings globaux sans audit mobile réel
- Modifier le header sans test mobile + desktop
- Casser la hiérarchie du hero validé
- Utiliser `100vw` (remplacé par `100%` — la scrollbar cause un overflow)
- Utiliser `overflow-hidden` au lieu de `overflow-clip` (casse `blur` + `transform`)
- Appliquer des corrections CSS globales pour corriger un bug local
- Modifier `layout-guardrails.css` sans validation sur 8 résolutions
- Supprimer ou affaiblir les gardes-fous CSS existants
- Ajouter des éléments décoratifs absolus sans `clip-path: inset(0)` sur le parent

---

## OBLIGATIONS ABSOLUES AVANT VALIDATION

- [ ] Test desktop (1440px) + mobile (360px) minimum
- [ ] Test sur 360 / 375 / 390 / 412 px
- [ ] Vérifier que chaque CTA rentre entièrement dans le viewport
- [ ] Vérifier que chaque carte reste centrée
- [ ] Vérifier qu'aucun rectangle ne dépasse du viewport
- [ ] Vérifier que le hero reste complet above-the-fold
- [ ] Vérifier que les accents et apostrophes s'affichent correctement
- [ ] Fournir screenshots AVANT/APRÈS
- [ ] Comparer avec la baseline visuelle (`/frontend/tests/visual-baseline/`)
- [ ] Tests Playwright (`visual.spec.ts`) PASS à 100%
- [ ] Vérifier qu'aucune page ne crée de `scrollWidth > clientWidth`

---

## PROTOCOLE OBLIGATOIRE AVANT TOUTE MODIFICATION VISUELLE

### Étape 1 — Intention
Décrire précisément le bloc ciblé et le changement souhaité.
Format : "Modifier [bloc X] dans [fichier Y] pour [objectif Z]."

### Étape 2 — Vérification pré-modification
- Screenshot du bloc AVANT modification (360px + 1440px minimum)
- Lister les fichiers qui seront touchés

### Étape 3 — Modification ciblée
- Modifier UNIQUEMENT le bloc ciblé
- Ne toucher à AUCUN fichier global (guardrails, index.css, App.css)
- Ne modifier AUCUNE zone gelée sans autorisation explicite

### Étape 4 — Vérification post-modification
- Screenshot du bloc APRÈS modification (360px + 1440px minimum)
- Lancer les tests Playwright : `npx playwright test tests/visual.spec.ts`
- Tous les tests doivent passer

### Étape 5 — Rapport obligatoire
```
CAUSE RACINE: [Texte]
BLOCS CONCERNÉS: [Texte]
FICHIERS RÉELLEMENT MODIFIÉS: [Texte]
CORRECTIONS APPLIQUÉES: [Texte]
VALIDATION VISUELLE RÉELLE: [Texte]
TESTS EFFECTUÉS: [Texte]
RISQUE DE RÉGRESSION: [Faible/Moyen/Élevé + Justification]
STATUT FINAL: [Texte]
```

---

## RÈGLE DE TRAVAIL AVEC L'AGENT

### INTERDIT
> "améliore un peu le rendu"
> "harmonise l'ensemble"
> "ajuste le responsive globalement"

### OBLIGATOIRE
> "modifie uniquement [bloc précis], sans toucher au hero, au header, aux CTA, aux containers globaux, ni aux breakpoints. Fournis les fichiers modifiés exacts + preuve visuelle."

---

## HISTORIQUE DES PROBLÈMES RÉSOLUS (ne pas réintroduire)

| Problème | Cause | Solution | Ne jamais |
|---|---|---|---|
| Scroll horizontal mobile | `100vw` inclut la scrollbar | Remplacé par `100%` | Utiliser `100vw` |
| Éléments flottants créent un overflow | `position: absolute` sans containment | `overflow-clip` + `clip-path: inset(0)` | `overflow-hidden` avec `blur/transform` |
| CTA tronqué sur mobile | Texte long + `whitespace-nowrap` | Version courte mobile (`sm:hidden`) | `whitespace-nowrap` sur CTA |
| Cartes décalées à gauche | Alignement par défaut du texte | `text-center lg:text-left` | Alignement asymétrique |
| Samsung Internet vs Chromium | Différences de rendu sub-pixel | Paddings symétriques, pas de `calc()` complexe | Se fier uniquement aux screenshots Playwright |
