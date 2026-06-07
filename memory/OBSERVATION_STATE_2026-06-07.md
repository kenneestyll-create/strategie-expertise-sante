# État d'observation de référence — `/expertise-medicale` à J+21

> **🚨 NON DÉPLOYÉ — DOCUMENT DE RÉFÉRENCE FIGÉ — LECTURE SEULE**
> Snapshot officiel de la trajectoire SEO à J+21 après le déploiement de la Phase 1.
> Ce document sert de **base de comparaison** pour l'analyse J+30 du 2026-06-16.

**Date du snapshot :** 2026-06-07 (J+21 après déploiement Phase 1 du 2026-05-17)
**Décision utilisateur :** ✅ Maintien de l'observation jusqu'au 2026-06-16. Aucune remédiation. Aucun rollback. Aucune nouvelle action SEO avant J+30.
**Source unique :** `/tmp/gsc2/*.csv` (export GSC 2026-06-07, 28 derniers jours, type Web)

---

## 1. Décision officielle datée 2026-06-07

L'utilisateur a expressément décidé :

- ❌ **Pas d'activation de l'option d'urgence J+21**
- ❌ **Pas de remédiation**
- ❌ **Pas de rollback**
- ❌ **Pas de rédaction du `PHASE1_ROLLBACK_PLAN.md` à ce stade** (suspendue, peut être réactivée si J+30 le justifie)
- ✅ **Maintien strict de l'observation jusqu'au 2026-06-16**
- ✅ **Décision Phase 2 / pages filles repoussée à l'export J+30**

**Aucune action corrective ni production supplémentaire ne sera engagée tant qu'un nouveau signal contraire n'apparaît pas.**

---

## 2. État de référence figé — Métriques clés J+21

### 2.1 `/expertise-medicale` (page sous observation)

| Métrique | Valeur figée J+21 | Note |
|---|---|---|
| **Clics 28 derniers jours** | **4** | Stable |
| **Impressions 28 derniers jours** | **172** | 🟢 +17 % vs export précédent |
| **CTR moyen** | **2,33 %** | Léger recul vs précédent |
| **Position moyenne** | **11,66** | 🟢 -8,7 places vs J+13 (était 20,38 sur 46j) |

### 2.2 Requêtes captées par `/expertise-medicale`

| Requête | Impressions 28j | Position | CTR | Évolution |
|---|---|---|---|---|
| `stratégie expertise médicale assureur` | **114** | **6,49** | 0 % | 🟢 -7,23 places (page 1) |
| `expertise médicale mdph` | 22 | 9,95 | 0 % | Stable |
| `expertise médicale accident du travail` | 5 | 23 | 0 % | Stable |
| `medecin expert mdph` | 3 | 10,33 | 0 % | Stable |
| `expertise médicale cnesst` | 1 | 2 | 0 % | (Canada, non significatif) |
| `expertise médicale demandée par assurance prévoyance` | 1 | 96 | 0 % | Stable |
| `délai pour demander une contre-expertise médicale` | 1 | 31 | 0 % | Stable |
| `contentieux post-expertise` | 1 | 39 | 0 % | Stable |
| `expertise médicale` (générique) | 1 | 48 | 0 % | Stable |
| `expertise at` | 1 | 6 | 0 % | Nouvelle émergence |
| `strategie expertise` | 1 | 8 | 0 % | Nouvelle émergence |

### 2.3 Santé globale du site (référence France)

| Métrique France 28j | Valeur figée J+21 |
|---|---|
| Clics | 177 |
| Impressions | 4 754 |
| CTR | 3,72 % |
| Position moyenne | 10,05 |

### 2.4 Confrontation aux seuils de dégradation (option B)

| Seuil B verrouillé | Valeur observée | Statut |
|---|---|---|
| Position `/expertise-medicale` > 40 ? | 11,66 | ✅ Très loin du seuil |
| Chute impressions > 50 % (vs 147 sur 46j ≈ 90/28j) ? | 172 (+91 %) | ✅ Inverse |
| CTR pilier < 0,5 % sur 7j ? | 2,33 % cumulé | ✅ Loin du seuil |

🟢 **Aucun seuil franchi. Aucune dégradation observée. La Phase 1 produit l'effet escompté.**

---

## 3. Baseline officielle figée pour comparaison J+30

Les valeurs ci-dessous serviront de **référence absolue** pour l'analyse du prochain export 2026-06-16.

| Élément | Baseline figée |
|---|---|
| **Position `/expertise-medicale` (28j)** | **11,66** |
| **Impressions `/expertise-medicale` (28j)** | **172** |
| **Clics `/expertise-medicale` (28j)** | **4** |
| **Position `stratégie expertise médicale assureur` (28j)** | **6,49** |
| **Impressions `stratégie expertise médicale assureur` (28j)** | **114** |
| **Clics France (site total)** | **177** |
| **Impressions France (site total)** | **4 754** |
| **Position moyenne France** | **10,05** |

---

## 4. Critères de comparaison à appliquer le 2026-06-16

Pour évaluer la trajectoire entre J+21 et J+30, appliquer ces 4 contrôles :

| Contrôle | Seuil de poursuite favorable | Seuil d'alerte |
|---|---|---|
| **Position `/expertise-medicale`** | ≤ 12 (stabilité ou amélioration) | > 18 (dégradation) |
| **Impressions `/expertise-medicale`** | ≥ 130 (≥ -25 % vs 172) | < 90 (chute > 50 %) |
| **Position requête prime `assureur`** | ≤ 8 (maintien page 1) | > 15 (sortie page 1) |
| **Trafic France total** | ≥ 130 clics | < 100 clics |

Si **les 4 contrôles sont favorables** au 16/06 → application directe de la Checklist `/app/memory/DECISION_CHECKLIST_2026-06-16.md` avec forte probabilité de GO Phase 2.

Si **≥ 1 contrôle en alerte** → activation de l'analyse de cause obligatoire (5 phases A-B-C-D-E figées dans le protocole de décision d'urgence).

---

## 5. Production en attente — Statut

| Livrable | Statut au 2026-06-07 |
|---|---|
| `AUDIT_CTR_2026-05-30.md` | ✅ Finalisé |
| `PRD_SIMULATEUR_AT.md` | ✅ Finalisé |
| `PRD_SIMULATEUR_MP.md` | ✅ Finalisé |
| `EXPERTISE_MEDICALE_PHASE2_3_DRAFT.md` | ✅ Finalisé |
| `DECISION_CHECKLIST_2026-06-16.md` | ✅ Finalisé |
| `PHASE1_ROLLBACK_PLAN.md` | ⏸️ **Suspendu sur décision utilisateur 2026-06-07** |
| Nouvelle production SEO | ⏸️ **Suspendue jusqu'au 2026-06-16** |

---

## 6. Reprise d'activité

La prochaine action autorisée est :
1. **Réception de l'export GSC J+30** (à effectuer le 2026-06-16 avec filtre Pays = France, 28 jours)
2. **Application de la Checklist de décision** (`DECISION_CHECKLIST_2026-06-16.md`)
3. **Activation conditionnelle** des chantiers selon les critères chiffrés

**Aucune action SEO, aucune modification de site, aucune nouvelle production avant cette date.**

---

**FIN — État d'observation figé**
**🔒 Référence officielle pour décision J+30**
