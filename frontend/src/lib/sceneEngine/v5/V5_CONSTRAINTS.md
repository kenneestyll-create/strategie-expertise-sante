# V5_CONSTRAINTS.md — Garde-fous contractuels Scene Engine V5

**Date** : 2026-05-21
**Statut** : Contractuel pendant tout le développement V5.

## Cible produit V5

V5 = "Automated Documentary Composer". 1 brief → 1 vidéo .webm 9:16 composée
de 4 à 6 mini-plans **réalistes** (images/vidéos Pexels, Nano Banana, ou uploads
manuels) animés en Ken Burns + cuts/crossfades, avec voix-off TTS et sous-titres
burned-in. Ambiance documentaire sobre administratif, charte navy/or.

## 3 interdictions structurelles

### 1. AUCUNE forme géométrique dessinée par Canvas dans le rendu V5
- Interdits dans `plans/*.js` : `ctx.arc`, `ctx.fillRect` géométrique (sauf 1px
  pour bg uni), `ctx.fillText` pour gros chiffres count-up, dessin de balance,
  triangle, bar chart, etc.
- Autorisés : `ctx.drawImage(asset)`, `ctx.fillText` pour sous-titres et titre
  court, `ctx.filter` colorimétrique, `ctx.globalAlpha` pour crossfade.

### 2. AUCUN registry de plans thématiques
- Seuls 4 plan types **génériques** autorisés :
  - `BackgroundImagePlan` (image fullscreen + overlay)
  - `BackgroundVideoPlan` (vidéo fullscreen + overlay)
  - `TextCardPlan` (fond uni + 1 phrase courte fullscreen)
  - `OutroCTAPlan` (image + CTA + URL)
- Interdit : `LegalCourtroomPlan`, `MedicalExpertisePlan`, `StatsFocusPlan`, etc.

### 3. CHAQUE Plan DOIT charger un asset externe (sauf TextCardPlan)
- Si un `BackgroundImagePlan`, `BackgroundVideoPlan`, ou `OutroCTAPlan` est
  instancié sans asset → throw `Error('V5_CONSTRAINTS: plan requires external asset')`.
- TextCardPlan est l'unique plan sans asset (typo + fond uni navy uniquement).

## Transitions limitées à 2 types
- `cut` (default)
- `crossfade` 200ms

Aucune autre transition autorisée. Pas de wipe, glitch, zoom-blur, slide,
flash, motion-blur, etc.

## Architecture isolée
- Tout le code V5 vit dans `/app/frontend/src/lib/sceneEngine/v5/`.
- Le V4.4 (`/sceneEngine/scenes/*`) reste intact comme fallback.
- Aucun import V5 → V4.4 ou inverse.

## Filtre colorimétrique unifié
Tout asset image/vidéo passe par le même filtre CSS via `ctx.filter` :
```
saturate(0.78) contrast(1.06) brightness(0.96) hue-rotate(-4deg)
```
+ une légère vignette + un grain optionnel layer overlay 2% opacity.

Cohérence avec charte navy/or maintenue par overlays (titre + sous-titres),
pas par modification destructive de l'asset.

## Critère de validation Phase A
"Le rendu ressemble-t-il à une mini vidéo documentaire publiable ?"
- OUI → GO Phase B
- NON → arrêt définitif V5, pas de Phase B

Le critère n'est PAS "architecture propre". C'est uniquement le rendu visuel.

---

Ce document est immuable pendant le développement V5. Toute dérogation
nécessite une décision utilisateur explicite et documentée.
