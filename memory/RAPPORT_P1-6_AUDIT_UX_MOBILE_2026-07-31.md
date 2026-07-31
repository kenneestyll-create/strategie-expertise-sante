# RAPPORT P1-6 — AUDIT UX MOBILE COMPLET
Date : 31/07/2026 — Feuille de route Août/Septembre, Phase 2
Méthode : passe technique automatisée (14 pages, viewport 390×844) + passe visuelle (tunnels de conversion) + mesures de performance production.
**Aucune modification appliquée — audit en lecture seule, conformément à l'ordre.**

## Contexte data (GSC J+30)
- Mobile = 73 % des clics (187/258), CTR mobile 3,87 % vs desktop 2,01 %
- Position moyenne mobile 8,18 vs desktop 13,45 → Google sert déjà le site en mobile-first
- Toute dégradation UX mobile impacte directement 3 clics sur 4

## Pages auditées (14)
/, /calculatrice-ipp, /calculatrice-aah, /dossier-express, /tarifs, /simulateur, /agenda, /medecin-conseil, /mdph, /expertise-medicale, /contact, /guides-pratiques, /guide/ipp-fonction-publique-hospitaliere, /guide/refus-aah-rsdae-non-reconnue

---

## ✅ POINTS FORTS (ne rien toucher)
1. **Zéro débordement horizontal** sur les 14 pages (overflow = 0px partout).
2. **Aucun risque de zoom iOS** : tous les inputs/textarea/select à 16px (< 16px déclenche le zoom auto iOS).
3. **Images hero optimisées** : webp mobile 33 Ko + preload + fetchpriority=high + variante responsive. LCP image exemplaire.
4. **Menu mobile propre** : cibles tactiles 44px, sous-menus repliables, hiérarchie claire.
5. **Formulaires lisibles** : tunnels /tarifs, /agenda, /dossier-express, /contact bien rendus, labels clairs, hiérarchie prix nette.
6. **H1 et hiérarchie typographique** conformes sur toutes les pages (24–36px mobile).

---

## 🔴 P0 — Fort impact SEO + UX (1 constat)

### P0-A : Auto-ouverture Straté PLEIN ÉCRAN sur mobile = interstitiel intrusif
- **Constat** : le chatbot Straté s'auto-ouvre (scroll ≥ 40 % OU 15 s d'inactivité, 1×/24h) et occupe **100 % du viewport mobile** (`fixed inset-0`, mesuré 390×844). Le visiteur en pleine lecture est interrompu par un écran complet.
- **Impact SEO** : Google pénalise explicitement les « interstitiels intrusifs » sur mobile (page experience). Un overlay plein écran auto-déclenché après l'arrivée depuis la SERP correspond à la définition exacte. Risque réel sur un site dont 73 % du trafic est mobile.
- **Impact UX** : interruption de lecture sur les guides (les pages où l'on veut du dwell time) ; risque de rebond.
- **Recommandation** : sur mobile uniquement, remplacer l'auto-ouverture plein écran par une bulle/badge discret (ex. pastille « Straté » avec micro-label), l'ouverture plein écran restant au clic volontaire. Desktop inchangé (fenêtre 6px bottom/right non intrusive).
- **Faisabilité** : FACILE — condition viewport dans `useStrateTriggers.js` (désactiver auto-open < 640px) OU rendu réduit dans `ChatBot.jsx`. Zéro impact sur le flux conversationnel existant.

---

## 🟠 P1 — Impact conversion (2 constats)

### P1-A : Curseur Taux IPP trop petit sur la page n°1 du site
- **Constat** : sur /calculatrice-ipp (150 clics/28j, 1ʳᵉ page du site), le thumb du slider « Taux d'IPP » mesure **16×16px** — très en dessous des 44px recommandés (Apple HIG / WCAG 2.5.8). Régler précisément 1–100 % au doigt est difficile, or la précision est le cœur de l'outil (9 % vs 10 % = capital vs rente).
- **Impact** : friction sur l'outil de conversion principal ; résultats faussés si l'utilisateur n'arrive pas à viser son taux exact.
- **Recommandation** : agrandir la zone tactile du thumb sur mobile (24–28px visuel + hit area 44px) ET ajouter une saisie numérique alternative (champ ou boutons −/+) synchronisée avec le slider.
- **Faisabilité** : FACILE (CSS + un input contrôlé).

### P1-B : Cumul d'éléments fixes sur la home mobile
- **Constat** : header sticky 68px + barre sticky basse « Expertise imminente ? 97 EUR » ~90px = **~19 % du viewport occupé en permanence**.
- **Impact** : zone de lecture réduite ; effet « tunnel » ; cumulé avec P0-A, la page peut se retrouver majoritairement recouverte.
- **Recommandation** : masquer la barre basse lors du scroll vers le bas (réapparition au scroll up), ou la compacter (une ligne).
- **Faisabilité** : MOYENNE (listener scroll + transition CSS).

---

## 🟡 P2 — Confort et performance (4 constats)

### P2-A : Corps de texte des guides à 14px sur mobile
- Les guides (lecture longue, cœur de la stratégie SEO) utilisent `text-sm` (14px). Pour de la lecture longue mobile, 16px est le standard de confort (améliore dwell time — signal comportemental).
- Recommandation : passer le corps des guides à 16px sur mobile (`text-base sm:text-sm` ou équivalent). Touche `GuidePreviewBody.jsx` uniquement.
- Faisabilité : FACILE — mais modifie le rendu des 17 guides : à valider explicitement.

### P2-B : Badge « Gratuit » avec césure disgracieuse (/dossier-express)
- Le badge vert « Gratuit » casse en « Gratui-t » sur 2 lignes (largeur contrainte).
- Recommandation : `whitespace-nowrap` sur le badge. Faisabilité : TRIVIALE.

### P2-C : Hauteur des champs de formulaire 36px
- Inputs à 36px (recommandation tactile : 44px). Fonctionnel mais perfectible sur les tunnels payants (/agenda, /dossier-express).
- Faisabilité : FACILE (classe de hauteur responsive).

### P2-D : Bundle JavaScript monolithique — 413 Ko gzip
- `main.js` = 413 Ko gzip (~1,2 Mo à parser sur mobile), chargé intégralement dès la home (admin dashboard, forum, studio inclus). + 2 scripts tiers plateforme (emergent-main.js, debug-monitor.js) en production.
- Impact : INP/TBT mobile dégradés sur appareils modestes — signal « page experience ».
- Recommandation : code-splitting par route (React.lazy sur AdminDashboard, Forum, Studio, pages secondaires) — gain estimé 30-40 % sur le bundle initial.
- Faisabilité : MOYENNE/LOURDE — chantier technique transverse, à planifier séparément si retenu.

---

## SYNTHÈSE PRIORISÉE (impact SEO × UX × faisabilité)
| # | Constat | Impact SEO | Impact UX | Faisabilité | Reco |
|---|---|---|---|---|---|
| P0-A | Interstitiel Straté plein écran mobile | ÉLEVÉ (pénalité interstitiels) | ÉLEVÉ | Facile | À corriger en priorité |
| P1-A | Slider IPP 16px | Indirect (conversion) | ÉLEVÉ | Facile | À corriger |
| P1-B | Cumul sticky home | Modéré | Modéré | Moyenne | À corriger |
| P2-A | Texte guides 14px | Modéré (dwell time) | Modéré | Facile | À valider |
| P2-B | Badge « Gratuit » césure | Nul | Faible | Triviale | Quick fix |
| P2-C | Inputs 36px | Nul | Faible | Facile | Optionnel |
| P2-D | Bundle 413 Ko | Modéré (INP) | Modéré | Lourde | Chantier séparé |

## Rappel des consignes respectées
- Aucune modification déployée. Audit 100 % lecture seule.
- Recommandations classées par impact SEO, UX et faisabilité (livrable conforme).
- Prochaine étape selon feuille de route : Phase 3 (observation GSC P1-1, 28 j) — les corrections ci-dessus ne seront lancées que sur ordre exécutif.
