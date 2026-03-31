# CHECKLIST VISUELLE OBLIGATOIRE — Avant mise en production

> Aucune modification frontend ne doit être considérée comme terminée
> si cette checklist n'est pas PASS à 100%.

---

## HOME

- [ ] Hero visible sans scroll desktop
- [ ] H1 non tronqué
- [ ] Badge "Pionnier en France" non coupé
- [ ] CTA visibles immédiatement
- [ ] Bloc IA 24/7 visible et propre
- [ ] Image droite entièrement contenue
- [ ] Aucun élément flottant parasite
- [ ] Section "Médecin Conseil" centrée sur mobile

---

## MOBILE (toutes pages)

- [ ] Aucun scroll horizontal
- [ ] Aucun encadré qui dépasse à droite
- [ ] Aucun bouton tronqué
- [ ] Cartes centrées
- [ ] Texte lisible sans zoom
- [ ] Header propre
- [ ] Menu mobile fonctionnel

---

## GLOBAL

- [ ] Accents OK (é, è, ê, à, ç, ù)
- [ ] Pas de régression sur Services / Tarifs / Médecin Conseil
- [ ] Screenshots comparés à la baseline (`/frontend/tests/visual-baseline/`)
- [ ] Tests Playwright visuels PASS (`visual.spec.ts`)

---

## RÉSOLUTIONS TESTÉES

- [ ] 360x800 (Samsung Galaxy)
- [ ] 375x812 (iPhone 13)
- [ ] 390x844 (iPhone 14)
- [ ] 412x915 (Pixel 7)
- [ ] 768x1024 (iPad portrait)
- [ ] 1024x768 (iPad paysage)
- [ ] 1366x768 (Laptop HD)
- [ ] 1440x900 (Desktop)

---

## PAGES VÉRIFIÉES

- [ ] `/` (Home)
- [ ] `/accompagnements` (Services)
- [ ] `/tarifs`
- [ ] `/medecin-conseil`
- [ ] `/dossier-express`
- [ ] `/strategiia`
- [ ] Menu mobile ouvert
- [ ] Header desktop
