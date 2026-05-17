# PHASE 3 — Maillage Interne `/expertise-medicale`

**Statut** : 📋 PRÉPARATION SEULE — Aucun déploiement autorisé sans validation explicite utilisateur.
**Date création** : 2026-05-17
**Date Phase 1 livrée** : 2026-05-17 (H1 + Title + Meta + sous-titre intro)
**Date d'éligibilité validation** : J+21 = 2026-06-07 (au plus tôt) — J+30 = 2026-06-16 (recommandé)
**Bloqué par** : observation Phase 1 (CTR + position + impressions)

---

## 🎯 Objectif Phase 3

Renforcer l'autorité PageRank interne de la page Pillar `/expertise-medicale` via du maillage stratégique, **sans toucher au contenu** de la page elle-même ni à celui des pages sources (uniquement insertion de liens hypertextes).

---

## 📊 État actuel du maillage (audit 2026-05-17)

### Liens INTERNES vers `/expertise-medicale` (sources)
| Source | Type | Compte SEO ? |
|---|---|---|
| `frontend/src/components/Header.jsx` ligne 45 | Menu principal | ✅ Oui (sitewide) |
| `frontend/src/data/searchIndex.js` | Algolia search index | ⚠️ Mineur (search interne) |
| `frontend/src/pages/SimulateurPage.jsx.bak.20260514` | Backup orphelin | ❌ Non |
| **Total réel** | | **1 lien SEO actif** |

### Pages /guide/* en DB (audit collection `seo_pages`) qui devraient mailler `/expertise-medicale`
**Aucune des 10 pages /guide/* ne pointe vers `/expertise-medicale`** dans leur section `content.maillage`.

→ Conclusion : la Pillar est sous-alimentée. Voilà la cause structurelle de la pos 63.

---

## 🛠 Plan d'action Phase 3 (à valider et exécuter après J+21)

### Action 1 — Ajouter `/expertise-medicale` au Footer
**Fichier** : `frontend/src/components/Footer.jsx` (entre lignes 211 et 217, juste avant "Choisir son médecin conseil")

**Nouveau lien à insérer** :
```jsx
<li>
  <Link to="/expertise-medicale" className="text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors">
    Expertise médicale
  </Link>
</li>
```

**Effet** : 1 lien sitewide × ~50 pages indexées = **+50 backlinks internes** instantanés vers la Pillar.

**Risque** : nul (ajout simple, pas de modif structurelle).

---

### Action 2 — Maillage depuis les 2 guides "cluster expertise"

#### 2a) `/guide/expertise-medicale-defavorable-recours` (catégorie `expertise`, pos GSC 8.2, 18 impr)
**Modification DB** : enrichir `content.maillage` pour ajouter une entrée pointant vers `/expertise-medicale`.

```python
{"slug": "expertise-medicale", "text": "Stratégie d'expertise médicale face à un assureur ou un tribunal"}
```

**Note technique** : `/expertise-medicale` n'est PAS un `/guide/*` slug. Il faut donc soit :
- Option A : étendre le composant `GuidePreviewBody.jsx` pour supporter le format `{"slug": "expertise-medicale", "type": "pillar"}` qui mappera vers `/expertise-medicale` (pas `/guide/expertise-medicale`)
- Option B : insérer le lien manuellement dans le contenu (HTML inline dans une section existante)
- **Recommandation** : Option A (plus propre, réutilisable pour les futures pages Pillar)

#### 2b) `/guide/comment-preparer-expertise-medicale` (catégorie `expertise`, pos GSC 11.6, 41 impr)
Idem — ajouter au maillage le lien Pillar avec une ancre différente (variation lexicale) :
```python
{"slug": "expertise-medicale", "text": "Vue d'ensemble de notre approche stratégique de l'expertise médicale"}
```

**Effet attendu** : 2 backlinks internes très topicalement liés depuis des pages elles-mêmes correctement positionnées → transmission d'autorité ciblée.

---

### Action 3 — Maillage depuis les 4 pages "sœurs" (pages services)

Pages-cibles (toutes en JSX, pas en DB) avec emplacement précis suggéré :

| Page source | Fichier | Emplacement suggéré | Ancre proposée |
|---|---|---|---|
| `/calculatrice-ipp` | `pages/CalculatriceIPPPage.jsx` | Dans la FAQ ou section "Erreurs à éviter" | "Préparer l'expertise médicale qui détermine votre IPP" |
| `/medecin-conseil` | `pages/MedecinConseilPage.jsx` | Bas de page, juste avant le CTA final | "Avant l'expertise : comprendre la stratégie globale" |
| `/accident-travail-maladie-professionnelle` | `pages/AccidentTravailMaladieProfPage.jsx` | Section "Étapes de la procédure" | "L'expertise médicale dans la procédure AT/MP" |
| `/mdph` | `pages/MdphPage.jsx` | Section sur l'évaluation | "Quand une expertise médicale est-elle déclenchée en MDPH ?" |

**Effet attendu** : 4 backlinks internes depuis pages à forte autorité topicale.

**Risque** : faible — ajouts ponctuels, pas de réécriture.

---

### Action 4 — Schema BreadcrumbList JSON-LD (optionnel, bonus)

Ajouter à `/expertise-medicale` un schema breadcrumb :
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Accueil", "item": "https://strategie-expertise-sante.fr/"},
    {"@type": "ListItem", "position": 2, "name": "Accompagnements", "item": "https://strategie-expertise-sante.fr/accompagnements"},
    {"@type": "ListItem", "position": 3, "name": "Expertise médicale", "item": "https://strategie-expertise-sante.fr/expertise-medicale"}
  ]
}
```

**Effet** : améliore l'affichage SERP (fil d'Ariane visible), aide Google à comprendre la hiérarchie.

---

## 📋 Synthèse — Backlinks ajoutés si plan complet exécuté

| Source | Nb backlinks ajoutés |
|---|---|
| Footer sitewide | +1 (présent sur ~50 pages) |
| `/guide/expertise-medicale-defavorable-recours` | +1 |
| `/guide/comment-preparer-expertise-medicale` | +1 |
| `/calculatrice-ipp` | +1 |
| `/medecin-conseil` | +1 |
| `/accident-travail-maladie-professionnelle` | +1 |
| `/mdph` | +1 |
| **TOTAL** | **+7 liens dédiés + 1 footer sitewide** |

Avant Phase 3 : **1 lien interne SEO actif**.
Après Phase 3 : **~8 liens internes** (× 8 d'autorité).

---

## 🎯 Estimation d'impact (à comparer avec mesure réelle Phase 1 d'abord)

| Métrique | Avant Phase 1 | Après Phase 1 seule (projeté J+21) | Après Phase 1+3 (projeté J+45) |
|---|---|---|---|
| Position moyenne `/expertise-medicale` | 63.1 | 40-55 | 20-35 |
| Impressions/mois | 32 | 50-80 | 100-200 |
| Clics/mois | 1 | 2-5 | 8-15 |

**⚠️ Ces chiffres sont indicatifs**. Le ROI réel ne sera mesurable qu'avec les données GSC post-déploiement.

---

## 🚦 Règles d'exécution (verrouillées)

1. ❌ **Aucune ligne de code de ce document ne sera déployée sans validation utilisateur explicite**.
2. ❌ Phase 3 ne peut être exécutée qu'**APRÈS observation Phase 1** (J+21 minimum).
3. ❌ Phase 2 (ajout sections MDPH/assureur) reste **BLOQUÉE** jusqu'à validation explicite séparée.
4. ✅ Ce document peut être enrichi/modifié librement (préparation), tant qu'aucun fichier code/DB n'est touché.

---

## 📅 Calendrier prévisionnel

| Date | Étape | Statut |
|---|---|---|
| 2026-05-17 | Phase 1 livrée (H1 + Title + Meta + sous-titre) | ✅ FAIT |
| 2026-05-17 | Plan Phase 3 rédigé | ✅ FAIT |
| 2026-05-17 → 2026-06-07 | Observation Phase 1 (J+21) | ⏳ EN COURS |
| ≥ 2026-06-07 | Restitution résultats Phase 1 + décision Phase 3 | ⏳ EN ATTENTE |
| ≥ 2026-06-07 (si GO) | Exécution Phase 3 (1 à 4 actions selon validation) | ⏳ EN ATTENTE |

---

## ✅ KPIs à observer en Phase 1 (rappel)

Ordre de priorité validé :
1. **CTR** (signal le plus rapide de réaction au nouveau title/H1)
2. **Position moyenne** par requête (`expertise médicale assureur`, `expertise médicale mdph`, `expertise médicale`)
3. **Impressions** (signal le plus lent — ne se déplace qu'après que la position ait bougé)

Suivi informatif uniquement — **aucune action sur la base de ces données avant J+21**.

---

*Document généré automatiquement — Source : audit GSC du 2026-05-17 (118 clics / 3 950 impressions / pos 9.9)*
