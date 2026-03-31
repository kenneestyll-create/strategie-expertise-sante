# CHECKLIST VISUELLE OBLIGATOIRE — Avant mise en production

> Aucune modification frontend ne doit être considérée comme terminée
> si cette checklist n'est pas PASS à 100%.
> Date de gel : 01/04/2026

---

## HOME — Page d'accueil

- [ ] Hero visible sans scroll desktop (above-the-fold)
- [ ] Hero mobile sans scroll horizontal
- [ ] H1 non tronqué (desktop + mobile)
- [ ] Badge "Pionnier en France" non coupé
- [ ] CTA "Besoin urgent ?" visible immédiatement
- [ ] CTA "Lancer mon analyse" visible immédiatement
- [ ] CTA "Être accompagné maintenant" visible immédiatement
- [ ] Bloc IA 24/7 visible et propre
- [ ] Image droite (photo fondateur) entièrement contenue
- [ ] Aucun élément flottant parasite (blocs analyse, documents, orientation)
- [ ] Section "Médecin Conseil" centrée sur mobile
- [ ] Cartes statistiques (800-3000 EUR, x10) centrées sur mobile
- [ ] Encadré "Risque d'un mauvais choix" ne dépasse pas à droite

---

## HEADER

- [ ] Header desktop aligné : logo gauche, nav centre, CTA droite
- [ ] Header mobile propre : logo + hamburger
- [ ] Menu burger fonctionnel : ouverture, navigation, fermeture
- [ ] Aucun scroll horizontal causé par le menu ouvert
- [ ] Logo non tronqué sur mobile
- [ ] CTA "Réserver un appel" visible sur desktop

---

## MOBILE — Toutes pages (360/375/390/412 px)

- [ ] Aucun scroll horizontal (scrollWidth === clientWidth)
- [ ] Aucun encadré qui dépasse à droite
- [ ] Aucun bouton tronqué
- [ ] Aucun bouton plus large que le viewport
- [ ] Cartes centrées
- [ ] Texte lisible sans zoom
- [ ] Aucun texte long ne casse la mise en page
- [ ] Aucune page interne ne provoque de largeur supérieure au viewport
- [ ] Paddings symétriques gauche/droite

---

## PAGES INDIVIDUELLES

### /accompagnements (Services)
- [ ] CTA "Être accompagné" non tronqué sur mobile
- [ ] Cartes de services centrées
- [ ] Aucun débordement horizontal

### /tarifs
- [ ] Cartes de tarifs centrées et contenues
- [ ] Prix et badges non coupés
- [ ] CTA "Choisir" visible sur chaque carte

### /medecin-conseil
- [ ] Section centrée sur mobile
- [ ] CTA principal non tronqué
- [ ] Cartes informatives contenues

### /dossier-express
- [ ] Formulaire centré et fonctionnel
- [ ] Boutons de soumission non tronqués
- [ ] Étapes visibles et navigables

### /simulateur (StrategiIA)
- [ ] Interface de chat/analyse contenue
- [ ] Aucun débordement du formulaire

### /contact
- [ ] Formulaire centré
- [ ] Email ne déborde pas (word-break)
- [ ] Bouton "Envoyer" visible et non tronqué

### /a-propos
- [ ] Photos et texte équilibrés
- [ ] Aucun élément qui déborde

### /ressources
- [ ] Cartes de ressources centrées
- [ ] Liens et badges contenus

### /calculatrice-ipp
- [ ] Formulaire et résultats centrés
- [ ] Aucun tableau qui déborde

### /accident-travail-maladie-professionnelle
- [ ] Contenu texte ne déborde pas
- [ ] CTA visibles

---

## GLOBAL

- [ ] Accents OK (é, è, ê, à, ç, ù, ï, ô)
- [ ] Pas de régression sur Services / Tarifs / Médecin Conseil
- [ ] Screenshots comparés à la baseline (`/frontend/tests/visual-baseline/`)
- [ ] Tests Playwright visuels PASS (`visual.spec.ts`) — 0 échec

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

## PAGES TESTÉES PAR PLAYWRIGHT

- [ ] `/` (Home)
- [ ] `/accompagnements` (Services)
- [ ] `/tarifs`
- [ ] `/medecin-conseil`
- [ ] `/dossier-express`
- [ ] `/simulateur` (StrategiIA)
- [ ] `/contact`
- [ ] `/a-propos`
- [ ] `/accident-travail-maladie-professionnelle`
- [ ] `/ressources`
- [ ] `/calculatrice-ipp`
- [ ] `/expertise-medicale`
- [ ] `/mdph`
- [ ] Menu mobile ouvert
- [ ] Header desktop
- [ ] Hero desktop
- [ ] Hero mobile
