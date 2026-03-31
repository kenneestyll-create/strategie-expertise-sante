# CHARTE ANTI-CASSE FRONTEND — Stratégie & Expertise Santé

> Ce document est la loi absolue du projet frontend.
> Toute modification qui enfreint ces règles est **rejetée sans discussion**.

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

---

## ZONES GELÉES

### Hero (`HomePage.jsx` — `data-testid="hero-section"`)
- Même hauteur générale
- Même hiérarchie visuelle
- Même position des CTA
- Même équilibre texte / image
- **Toute modification nécessite validation visuelle complète desktop + mobile**

### Header (`Header.jsx`)
- Structure, navigation, logo, CTA intouchables
- **Toute modification nécessite test mobile + desktop + menu ouvert**

---

## RÈGLE DE TRAVAIL AVEC L'AGENT

### INTERDIT
> "améliore un peu le rendu"

### OBLIGATOIRE
> "modifie uniquement [bloc précis], sans toucher au hero, au header, aux CTA, aux containers globaux, ni aux breakpoints. Fournis les fichiers modifiés exacts + preuve visuelle."

---

## FORMAT DE RAPPORT OBLIGATOIRE

Chaque fix doit inclure :
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
