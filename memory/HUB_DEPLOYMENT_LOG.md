# HUB SIMULATEUR — DEPLOYMENT LOG

## 📍 Statut au 14/05/2026 (J+3 post-Étape 1)

**Étape 1 (correction sitemap) — Résultat validé :**
- ✅ Gate 1 : 42 / 41 pages indexées (dépassé +4)
- ✅ Gate 2 : 0 page "détectée non indexée"
- ✅ Gate 3 : Sitemap "Réussite" + 40 pages détectées
- ✅ Gate 4 : ~308 impressions / 24h (×14 vs baseline)

→ **4/4 gates vertes → feu vert Option B v2 (accélération contrôlée)**

---

## 🚀 Déploiement HUB — 14/05/2026

### Modifications appliquées (preview)
- ✅ Création `SimulateurHubPage.jsx` (basée sur SimulateurHubPreviewPage)
- ✅ Retrait `noindex, nofollow` + override useEffect
- ✅ Canonical : `https://strategie-expertise-sante.fr/simulateur` (self)
- ✅ Ajout paragraphe SEO ~250 mots (3 régimes d'indemnisation)
- ✅ Route `/simulateur` pointe vers `SimulateurHubPage`
- ✅ Sauvegarde de l'ancienne page : `SimulateurPage.jsx.bak.20260514`
- ✅ Suppression `SimulateurHubPreviewPage.jsx` (devenu redondant)
- ✅ Route `/simulateur-hub-preview` supprimée

### Conservation
- ✅ Mini-simulateur Light (3 champs : type / taux / salaire)
- ✅ FAQ enrichies (5 questions, ~1000 mots)
- ✅ Schemas JSON-LD : FAQPage + BreadcrumbList
- ✅ 4 blocs "Bientôt disponible" non cliquables
- ✅ Style dark + accents amber
- ✅ H1 : "Simulateurs d'indemnisation : IPP, AAH, accident du travail"

### Vague 1 — Pages filles preview-only (J+3)
- ✅ `SimulateurIPPAccidentTravailPreviewPage.jsx` — route `/simulateur-rente-ipp-accident-travail-preview`
  - noindex, nofollow + canonical futur : `https://strategie-expertise-sante.fr/simulateur-rente-ipp-accident-travail`
  - Simulateur fonctionnel AT (taux IPP, salaire, faute inexcusable)
  - Contenu juridique ~1000 mots (formule, faute inex., contestation taux)
  - Schema BreadcrumbList
  - CTA vers /dossier-express
- ✅ `SimulateurMaladieProfessionnellePreviewPage.jsx` — route `/simulateur-rente-maladie-professionnelle-preview`
  - noindex, nofollow + canonical futur : `https://strategie-expertise-sante.fr/simulateur-rente-maladie-professionnelle`
  - Simulateur fonctionnel MP (taux IPP, salaire, régime RG/RA/CRRMP)
  - Contenu juridique ~1000 mots (reconnaissance, prescription, contestation)
  - Schema BreadcrumbList
  - CTA vers /dossier-express

### Aucune modification de
- ❌ Backend
- ❌ Dossier Express IA
- ❌ robots.txt
- ❌ sitemap.xml (URL `/simulateur` déjà présente, seul le contenu change)
- ❌ Header / Footer
- ❌ Autres pages du site

---

## 📊 BASELINE FIGÉE PRÉ-DÉPLOIEMENT HUB

**Date de référence : 14/05/2026 (avant déploiement production)**

| Métrique | Valeur baseline | Source |
|---|---|---|
| Impressions /simulateur (28j) | 158 | Google Search Console |
| Position moyenne /simulateur | ~10 | GSC |
| CTR /simulateur | ~3,8 % | GSC |
| Requête principale | "simulateur rente ipp" | GSC |
| Pages indexées du site | 42 | GSC |
| Impressions totales 24h | ~308 | GSC |

---

## 🚦 GATES HUB (à valider avant 1er article éditorial)

| Gate | Critère | Seuil | À mesurer |
|---|---|---|---|
| Gate HUB-1 | `/simulateur` indexée dans GSC | Statut "Indexée" | À J+7 post-déploiement prod |
| Gate HUB-2 | Impressions /simulateur | ≥ 80% baseline (≥ 126 imp/28j) | À J+14 |
| Gate HUB-3 | Aucune nouvelle page "Détectée non indexée" | Compteur ≤ 0 nouvelle | À J+14 |

**Si 3/3 vertes → feu vert reprise éditoriale 1 article/semaine.**

---

## 🛡️ MONITORING + ROLLBACK AUTOMATIQUE

### Calendrier de surveillance hebdomadaire
- **J+7** post-déploiement prod : mesure impressions /simulateur (28j glissants)
- **J+14** post-déploiement prod : idem
- **J+21** post-déploiement prod : idem
- **J+28** post-déploiement prod : idem

### Seuil de rollback
- **Trigger : 110 imp / 28 jours** (= -30% vs baseline 158)
- **Condition : 2 mesures hebdomadaires consécutives** sous le seuil

### Procédure de rollback (si trigger atteint)
1. Renommer `SimulateurPage.jsx.bak.20260514` → `SimulateurPage.jsx`
2. Modifier `App.js` :
   - Remplacer `import("@/pages/SimulateurHubPage")` par `import("@/pages/SimulateurPage").then(m => ({ default: m.SimulateurPage }))`
3. Push GitHub + redéploiement
4. Surveillance reprise sur 14 jours

**Estimation effort rollback : 5 minutes de code + déploiement.**

---

## 📋 ACTIONS POST-DÉPLOIEMENT PRODUCTION (par utilisateur)

1. Push GitHub (Save to Github)
2. Déclencher déploiement production
3. Vérifier https://strategie-expertise-sante.fr/simulateur :
   - HTTP 200
   - Canonical correct (self)
   - Robots = index, follow
   - Mini-simulateur fonctionnel
   - Paragraphe SEO 3 régimes affiché
   - 4 blocs "Bientôt disponible" présents
4. Search Console → Inspection URL → coller `https://strategie-expertise-sante.fr/simulateur` → "Demander une indexation" (30 sec)
5. (Optionnel) Lighthouse manuel via PageSpeed Insights
6. Noter la **date exacte** du déploiement → c'est le J+0 du monitoring

---

## 📦 LIVRABLES SESSION 14/05/2026

- `/app/frontend/src/pages/SimulateurHubPage.jsx` (nouveau — HUB production)
- `/app/frontend/src/pages/SimulateurIPPAccidentTravailPreviewPage.jsx` (nouveau — Vague 1 preview)
- `/app/frontend/src/pages/SimulateurMaladieProfessionnellePreviewPage.jsx` (nouveau — Vague 1 preview)
- `/app/frontend/src/pages/SimulateurPage.jsx.bak.20260514` (sauvegarde rollback)
- `/app/frontend/src/App.js` (3 imports + 3 routes mis à jour)
- `/app/memory/HUB_SIMULATEUR_BLUEPRINT.md` (mis à jour)
- `/app/memory/HUB_DEPLOYMENT_LOG.md` (ce fichier)

---

## 🔄 ROADMAP POST-GATES HUB

**Si 3/3 Gates HUB vertes (typiquement J+10 à J+14) :**

### Phase A — Activation Vague 1 production (1 jour de code)
1. Renommer routes `/simulateur-rente-ipp-accident-travail-preview` → `/simulateur-rente-ipp-accident-travail` (production)
2. Idem pour MP
3. Retirer `noindex, nofollow` des 2 pages
4. Ajuster canonicals (devient self automatiquement)
5. Ajouter les 2 URLs au sitemap (`config.py` SITEMAP_PAGES + `sitemap.xml`)
6. Activer les 2 premiers blocs du HUB (retirer "Bientôt disponible" pour AT + MP)
7. Re-soumettre sitemap GSC + demander indexation des 2 nouvelles URLs

### Phase B — Reprise éditoriale (parallèle, dès Gates vertes)
- 1 article/semaine via Studio Éditorial S.E.S
- Ordre suggéré : "Simulateur rente IPP guide 2026" → "Faute inexcusable" → "AAH cumul salaire" → "Médecin Conseil CPAM"

### Phase C — Vague 2 (après Vague 1 stabilisée, ~J+42)
- AAH + cumul salaire (preview puis prod)
- Faute inexcusable (preview puis prod)
