# RAPPORT LOT 1 UX MOBILE — AVANT/APRÈS AVEC MESURES (04/08/2026)
Périmètre exécuté sur ordre : P0-A (interstitiel Straté mobile) + P1-A (curseur IPP tactile + saisie numérique).
Interdits respectés : SEO /dossier-express et progression client NON touchés. Zone gelée ChatBot (positionnement FAB mobile/desktop) NON modifiée.

## FICHIERS MODIFIÉS (3)
1. `frontend/src/hooks/useStrateTriggers.js` — garde viewport dans `maybeFire` : aucune auto-ouverture si `window.innerWidth < 640`. Le cooldown 24h n'est PAS consommé sur mobile (le comportement desktop du même visiteur reste intact). Ouverture volontaire au clic : inchangée.
2. `frontend/src/components/ui/slider.jsx` — thumb `h-6 w-6` (24px) sur mobile, `sm:h-4 sm:w-4` (16px inchangé) sur desktop + zone tactile étendue à 44px via pseudo-élément `before:-inset-2.5` (mobile uniquement).
3. `frontend/src/pages/CalculatriceIPPPage.jsx` — groupe de saisie précise sous le curseur : boutons − / + (44×44px, `ipp-taux-minus` / `ipp-taux-plus`) + champ numérique (`ipp-taux-input`, clamp 1–100, inputMode numeric, 16px anti-zoom iOS), le tout synchronisé bidirectionnellement avec le curseur et le badge `ipp-taux-display`.

## MESURES AVANT / APRÈS
| Mesure (runtime Playwright) | AVANT | APRÈS |
|---|---|---|
| Home mobile 390×844, scroll 45% + 16s : overlays plein écran | **1** (contenu 100 % masqué — capture du 04/08 09:43) | **0** ✅ (capture 09:53) |
| Cooldown 24h consommé inutilement sur mobile | Oui | **Non** ✅ |
| Thumb slider IPP mobile | **16×16 px** | **24×24 px** (+ hit-area 44 px) ✅ |
| Saisie précise du taux au doigt | Curseur seul (1–100 difficile) | Champ numérique + boutons −/+ 44px ✅ |
| Thumb slider desktop | 16×16 px | **16×16 px** (inchangé) ✅ |
| Auto-open Straté desktop (scroll 45% + 16s) | Fenêtre 380px bottom-right | **Fenêtre 380px bottom-right** (inchangé) ✅ |

## TESTS DE VALIDATION EXÉCUTÉS (tous PASS)
1. **Mobile 390×844 — absence de blocage du contenu** : après déclenchement des 2 triggers (scroll ≥ 40 % ET 15 s d'inactivité), 0 overlay plein écran détecté. ✅
2. **Simulateur IPP mobile** : saisie « 9 » → affichage 9 % ; bouton + → 10 % → le champ salaire (seuil rente) apparaît ; « Calculer l'estimation » → rente annuelle 1 250 € affichée (10 % × 25 000 €, formule intacte). ✅
3. **Non-régression desktop** : auto-open Straté fonctionne toujours (fenêtre 380 px, pas plein écran) ; thumb 16 px inchangé ; boutons −/+ opérationnels ; layout centré propre (captures). ✅
4. Effet de bord contrôlé : le slider de /calculatrice-aah bénéficie du même confort tactile mobile (24 px) — desktop inchangé ; aucun autre usage public du composant.

## DÉPLOIEMENT
Correctifs en PREVIEW uniquement. Au prochain redéploiement, seront livrés ensemble :
- Lot 1 UX mobile (ce rapport)
- Endpoint admin `DELETE /api/admin/dossier-express/{id}` → purge immédiate du résidu prod `5ef57e38-aba` (je l'exécute dès le déploiement confirmé).
