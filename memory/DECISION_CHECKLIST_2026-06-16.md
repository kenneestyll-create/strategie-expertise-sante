# Checklist de décision 2026-06-16 (J+30)

> **🚨 NON PUBLIÉ — DRAFT — DOCUMENT DE PRÉPARATION**
> Cette checklist sera utilisée à la date J+30 (2026-06-16) pour décider, sur la base de critères chiffrés et objectifs, du lancement de 4 chantiers indépendants.
> Aucune décision préalable, aucun déploiement, aucune modification de site avant cette date.

**Date de rédaction :** 2026-05-30
**Date d'application :** 2026-06-16
**Périmètre :** Décision GO/NO-GO sur 4 chantiers indépendants

---

## 0. Principes méthodologiques

### 0.1 Critères chiffrés uniquement
Aucun critère subjectif n'est admis. Tous les seuils sont **numériques**, **issus de l'export GSC** ou de **mesures observables** (impressions, position, CTR, ratio de pages, etc.).

### 0.2 Source unique de vérité
Un **nouvel export GSC** doit être effectué le 2026-06-16 avec les paramètres suivants :
- Période : **28 jours glissants** (du 2026-05-20 au 2026-06-16)
- Filtre pays : **France uniquement** (retirer le bruit US)
- Type de recherche : Web
- Sheets requises : **Queries, Pages, Devices, Graphique**

### 0.3 Règle de réversibilité
Aucune décision « JE NE SAIS PAS » : chaque chantier reçoit **GO**, **NO-GO**, ou **REPORT-30j** (avec date butoir de re-évaluation).

### 0.4 Composition de la décision
Chaque chantier est évalué sur 3 axes :
- **Santé de la page pilier `/expertise-medicale`** (non-régression)
- **Critères propres au chantier**
- **Capacité d'exécution** (ressources, blocages externes)

Tous les axes doivent être GO pour que le chantier soit GO.

---

## 1. Chantier 1 — SEO Phase 2 `/expertise-medicale` (enrichissement contenu)

### 1.1 Critères propres au chantier

| # | Critère | Seuil GO | Seuil NO-GO | Source vérifiable |
|---|---|---|---|---|
| 1.1 | Position moyenne 28j de `/expertise-medicale` | **≤ 25** | > 35 | GSC Pages.csv filtré page |
| 1.2 | Impressions 28j de `/expertise-medicale` | **≥ 100** | < 30 | GSC Pages.csv filtré page |
| 1.3 | Évolution position depuis 14j (avant vs 14j après 17/05) | **stable ou amélioration (Δ ≥ -5 positions)** | Dégradation > +10 positions | GSC comparaison |
| 1.4 | Présence d'au moins 3 requêtes non-marque captées | **≥ 3 requêtes hors `stratégie expertise`** | 0-1 requête | GSC Queries.csv |
| 1.5 | Aucune chute brutale d'impressions (vs avant Phase 1) | Δ impressions ≥ -30 % | Δ < -50 % | Graphique GSC |

### 1.2 Critères de santé globale du site

| # | Critère | Seuil GO | Seuil NO-GO | Source |
|---|---|---|---|---|
| 1.6 | Trafic France 28j (total) | **≥ 110 clics** (90 % du baseline 197/46j ≈ 120/28j) | < 70 clics | GSC Pays.csv |
| 1.7 | Aucune désindexation des 10 pages top trafic | 10/10 indexées | < 8/10 | GSC Pages.csv + Search Console |
| 1.8 | Aucune erreur critique Sentry frontend dans les 7 derniers jours | < 5 erreurs P0/P1 | ≥ 10 erreurs P0/P1 | Dashboard Sentry |

### 1.3 Critères de capacité d'exécution

| # | Critère | Seuil GO | Seuil NO-GO |
|---|---|---|---|
| 1.9 | Brouillons Phase 2 prêts | **OUI** (déjà rédigés dans `EXPERTISE_MEDICALE_PHASE2_3_DRAFT.md`) | Non |
| 1.10 | Validation juridique des contenus assureur + MDPH | **OUI** (déclenchée la semaine du 16/06) | Refus juriste |
| 1.11 | Aucun chantier P0 en cours qui préempte les ressources | OUI | Non |

### 1.4 Décision

```
GO Phase 2 si :
  (TOUS les critères 1.1 à 1.5 = GO) ET
  (TOUS les critères 1.6 à 1.8 = GO) ET
  (TOUS les critères 1.9 à 1.11 = GO)

NO-GO Phase 2 si :
  AU MOINS UN critère = NO-GO

REPORT-30j Phase 2 si :
  Aucun NO-GO mais ≥ 1 critère en zone d'incertitude (entre seuil GO et seuil NO-GO)
  → Re-évaluation 2026-07-16
```

---

## 2. Chantier 2 — SEO Phase 3 `/expertise-medicale` (pages filles + maillage avancé)

### 2.1 Préalable absolu

**Le chantier 2 ne peut être GO que si le chantier 1 est GO.**
Phase 3 (pages filles) n'a aucun sens si Phase 2 (enrichissement pilier) n'est pas validée.

### 2.2 Critères propres

| # | Critère | Seuil GO | Seuil NO-GO | Source |
|---|---|---|---|---|
| 2.1 | Position 28j `/expertise-medicale` | **≤ 15** (plus exigeant que Phase 2) | > 25 | GSC Pages.csv |
| 2.2 | Impressions 28j sur la requête `stratégie expertise médicale assureur` | **≥ 70** (vs 116 sur 46j = 71/28j) | < 30 | GSC Queries.csv |
| 2.3 | CTR 28j sur `/expertise-medicale` | **≥ 2 %** | < 0,5 % | GSC Pages.csv |
| 2.4 | Volume cumulé des 5 requêtes longue traîne ciblées par pages filles | **≥ 100 impressions 28j** | < 30 | GSC Queries.csv |
| 2.5 | Évolution favorable Phase 2 (si déjà déployée) | Pos améliorée ≥ -3 / impr ≥ +20 % | Pos dégradée > +5 / impr -20 % | Comparaison J+30 vs J+15 |

### 2.3 Critères pages filles

| # | Critère | Seuil GO | Seuil NO-GO |
|---|---|---|---|
| 2.6 | Brouillons rédactionnels pages filles P0/P1 prêts (assureur, MDPH, AT) | **3/3 prêts** | < 2/3 |
| 2.7 | Templating React `<ChildPage />` réutilisable | Existe et testé | À développer ex nihilo |
| 2.8 | Plan de maillage interne validé | **OUI** | Non |
| 2.9 | Risque cannibalisation contrôlé (Title pages filles ≠ Title pilier) | **OUI** (audit anchors) | Non |

### 2.4 Décision

```
GO Phase 3 si :
  Phase 2 = GO ET (TOUS les critères 2.1 à 2.5 = GO) ET (TOUS les critères 2.6 à 2.9 = GO)

REPORT-30j Phase 3 si :
  Phase 2 = GO mais critères 2.x partiellement satisfaits
  → Déployer Phase 2 d'abord, ré-évaluer Phase 3 à 2026-07-16

NO-GO Phase 3 si :
  Phase 2 = NO-GO OU critères 2.x globalement défavorables
```

---

## 3. Chantier 3 — Pages filles (sous-ensemble priorisé)

### 3.1 Décomposition fine

Le chantier 3 est subdivisé en **3 vagues** indépendantes :

#### Vague 3a — `/expertise-medicale/assureur` (P0)
| # | Critère | Seuil GO | Seuil NO-GO |
|---|---|---|---|
| 3a.1 | Impressions 28j `stratégie expertise médicale assureur` | **≥ 50** | < 20 |
| 3a.2 | Position moyenne 28j de cette requête sur le pilier | **≤ 15** | > 30 |
| 3a.3 | Concurrence SERP fiable (compétiteurs identifiés) | ≤ 5 sites premium en top 10 | > 8 sites institutionnels |

→ **GO Vague 3a si 3a.1 + 3a.2 + 3a.3 = GO**. Décision indépendante des autres vagues.

#### Vague 3b — `/expertise-medicale/mdph`, `/accident-travail`, `/contre-expertise` (P1)
| # | Critère | Seuil GO | Seuil NO-GO |
|---|---|---|---|
| 3b.1 | Volume cumulé 3 requêtes cibles | **≥ 50 impressions 28j** | < 15 |
| 3b.2 | Vague 3a = GO ou stable depuis ≥ 14j | OUI | Non |
| 3b.3 | Capacité dev disponible | OUI | Non |

→ **GO Vague 3b** déclenche le développement séquentiel des 3 pages (1 par semaine).

#### Vague 3c — `/prevoyance`, `/dires`, `/medecin-de-recours` (P2)
| # | Critère | Seuil GO | Seuil NO-GO |
|---|---|---|---|
| 3c.1 | Vagues 3a + 3b = stables et conversions observées | OUI | Non |
| 3c.2 | Nouvelles données GSC à J+90 confirmant le potentiel | OUI | Non |

→ **GO Vague 3c reporté à 2026-09-16** (J+90) par construction.

### 3.2 Synthèse chantier 3

```
GO Pages filles si :
  AU MOINS la Vague 3a satisfait les 3 critères ET Phase 3 = GO

NO-GO Pages filles si :
  Phase 3 = NO-GO OU 3a.1, 3a.2 et 3a.3 toutes en NO-GO
```

---

## 4. Chantier 4 — Simulateurs Vague 1 (AT + MP)

### 4.1 Décomposition

Le chantier 4 est subdivisé en **2 sous-chantiers indépendants** :

#### Sous-chantier 4-AT — Simulateur Accident du Travail
| # | Critère | Seuil GO | Seuil NO-GO | Source |
|---|---|---|---|---|
| 4AT.1 | Impressions 28j sur requêtes simulateur AT (cumulé : « simulateur rente accident travail », « simulateur calcul ipp accident travail », « simulateur rente at », etc.) | **≥ 200 impr** | < 80 | GSC Queries.csv |
| 4AT.2 | CTR moyen 28j sur ces requêtes | **≥ 1 %** (signal d'intention) | < 0,3 % | GSC Queries.csv |
| 4AT.3 | Position moyenne actuelle (sans page dédiée) sur ces requêtes | **8-15** (zone exploitable) | > 25 (effort SEO trop lourd) | GSC Queries.csv |
| 4AT.4 | Validation juridique des formules CSS L.434 | **OUI** (juriste S.E.S validé) | Non | Document de validation interne |
| 4AT.5 | Barème 2026 confirmé (capital IPP < 10 %, plafonds) | **OUI** | Non | `frontend/src/data/baremes/at_2026.js` (à créer) |
| 4AT.6 | PRD AT complet et validé | **OUI** (déjà fait : `PRD_SIMULATEUR_AT.md`) | Non | `/app/memory/PRD_SIMULATEUR_AT.md` |
| 4AT.7 | Charge dev disponible (~11 j-h) | OUI | Non | Planning équipe |
| 4AT.8 | Aucun chantier `/expertise-medicale` urgent qui préempte | OUI | Non | Décision Phase 2/3 |

→ **GO Simulateur AT si 8/8 = GO**.

#### Sous-chantier 4-MP — Simulateur Maladie Professionnelle
| # | Critère | Seuil GO | Seuil NO-GO |
|---|---|---|---|
| 4MP.1 | Simulateur AT = GO et en cours de dev OU déployé | **OUI** | Non |
| 4MP.2 | Impressions 28j sur requêtes simulateur MP | **≥ 25 impr** | < 10 |
| 4MP.3 | Base des 115 tableaux MP constituée | **OUI** | Non |
| 4MP.4 | Validation juridique logique CRRMP | **OUI** | Non |
| 4MP.5 | PRD MP complet | **OUI** (déjà fait : `PRD_SIMULATEUR_MP.md`) | Non |
| 4MP.6 | Charge dev disponible (~15,5 j-h post-AT) | OUI | Non |

→ **GO Simulateur MP si 6/6 = GO**. Recommandation : déployer après stabilisation d'AT (J+30 post-AT).

### 4.2 Synthèse chantier 4

```
GO Simulateur AT si : 8/8 critères 4AT = GO
GO Simulateur MP si : 6/6 critères 4MP = GO (incluant AT en cours ou déployé)

NO-GO Simulateur AT/MP si :
  Validation juridique manquante (4AT.4 ou 4MP.4)
  OU charge dev indisponible
  OU /expertise-medicale en chute (Phase 2 NO-GO)
```

---

## 5. Tableau de bord récapitulatif (à remplir le 2026-06-16)

| Chantier | Critères chiffrés satisfaits | Score | Décision | Date butoir alternative |
|---|---|---|---|---|
| **C1 — Phase 2 `/expertise-medicale`** | __ /11 | ___ % | ☐ GO ☐ NO-GO ☐ REPORT | __________ |
| **C2 — Phase 3 maillage avancé** | __ /9 | ___ % | ☐ GO ☐ NO-GO ☐ REPORT | __________ |
| **C3a — Page fille assureur** | __ /3 | ___ % | ☐ GO ☐ NO-GO ☐ REPORT | __________ |
| **C3b — Pages filles MDPH/AT/contre-expertise** | __ /3 | ___ % | ☐ GO ☐ NO-GO ☐ REPORT | __________ |
| **C4-AT — Simulateur AT** | __ /8 | ___ % | ☐ GO ☐ NO-GO ☐ REPORT | __________ |
| **C4-MP — Simulateur MP** | __ /6 | ___ % | ☐ GO ☐ NO-GO ☐ REPORT | __________ |

**Règle d'or** : si un critère 1.1 à 1.8 (santé globale + santé pilier) est en NO-GO, **tous les chantiers basculent automatiquement en REPORT-30j**, sauf le chantier 4-AT qui est indépendant de l'évolution de `/expertise-medicale` (et peut donc GO seul si ses 8 critères sont satisfaits).

---

## 6. Procédure d'audit le 2026-06-16

1. Effectuer l'export GSC selon la configuration §0.2.
2. Remplir le tableau §5 critère par critère, **sans interprétation**.
3. Si un critère est ambigu (proche du seuil), passer en zone d'incertitude → REPORT.
4. Stocker l'export GSC dans `/app/memory/GSC_EXPORT_2026-06-16.zip` pour traçabilité.
5. Décision écrite stockée dans `/app/memory/DECISIONS_2026-06-16.md`.
6. Si GO sur ≥ 1 chantier : déclencher le sprint dev correspondant.

---

# 📊 SYNTHÈSE EXÉCUTIVE — Décisions stratégiques post 2026-06-16

> Cette synthèse anticipe les scénarios. Les décisions réelles dépendent des données GSC du 16/06.

## 7.1 Ce qui peut être lancé immédiatement après le 16/06

### 🟢 Probable GO (faible risque d'attente)

**1. Quick wins CTR Vague 1** *(audit déjà validé)*
- `/guide/faute-inexcusable-employeur`, `/guide/refus-mdph-aah-que-faire`, `/guide/inaptitude-travail-droits-recours`
- Aucune dépendance à `/expertise-medicale`
- Effort : 0,5 jour dev
- Impact : +20 clics/mois cumulés en 4-6 semaines

**2. SEO Phase 2 `/expertise-medicale` (enrichissement contenu)**
- Si critères 1.1 à 1.11 satisfaits (très probable car les signaux actuels sont bons)
- Effort : 2-3 jours
- Impact : capture des 116 impr/mois sur `stratégie expertise médicale assureur` (top buyer-intent)

**3. Page fille `/expertise-medicale/assureur`** *(vague 3a uniquement)*
- Si Phase 2 = GO et critères 3a satisfaits
- Effort : 3-4 jours
- Impact : 50-75 impressions captées/mois sur la longue traîne

### 🟡 GO conditionnel (à observer 14-30 jours après Phase 2)

**4. Pages filles MDPH + AT + contre-expertise**
- Lancer **après** stabilisation Phase 2 + page fille assureur
- Permet d'isoler le signal de chaque modification (méthodologie scientifique)

## 7.2 Ce qui devrait attendre davantage de données

### 🟠 REPORT recommandé même si GO probable

**A. Simulateur AT**
- Le PRD est prêt, mais le **trafic capté** (200+ impr/28j sur les requêtes simulateur AT) doit être validé sur 28j filtré France.
- L'export du 30/05 ne segmentait pas suffisamment.
- **Recommandation :** GO si critère 4AT.1 confirme ≥ 200 impr ; sinon REPORT à J+60 (mi-juillet).

**B. Simulateur MP**
- Dépend de la stabilisation d'AT (au moins 30 jours post-déploiement AT).
- **Recommandation :** REPORT systématique au 2026-08-16 minimum, même si critères favorables.

**C. Pages filles P2 (prévoyance, dires, médecin de recours)**
- Volume trop faible aujourd'hui pour justifier l'effort.
- **Recommandation :** REPORT à 2026-09-16 (J+90).

## 7.3 Meilleur ratio effort / impact

| Chantier | Effort (j-h) | Impact attendu /mois | Ratio |
|---|---|---|---|
| 🥇 **Quick wins CTR Vague 1 (3 pages P0/P1)** | 0,5 | +20 clics | **40 clics/j** |
| 🥈 **SEO Phase 2 `/expertise-medicale`** | 2,5 | +30-50 clics | 12-20 clics/j |
| 🥉 **Page fille `/expertise-medicale/assureur`** | 4 | +25-40 clics | 6-10 clics/j |
| 4. Quick wins Vague 2 (medecin-conseil + calcul-aah) | 0,3 | +13 clics | 43 clics/j |
| 5. Simulateur AT | 11 | +50-100 clics + conversion | 5-9 clics/j (+ revenu indirect) |
| 6. Pages filles MDPH/AT/contre-exp | 12 | +30-50 clics | 3-4 clics/j |
| 7. Simulateur MP | 15,5 | +30-60 clics + conversion | 2-4 clics/j |

**Synthèse :** les quick wins CTR (Vagues 1 et 2) offrent un ratio imbattable (≥ 40 clics/jour-homme). À déclencher en priorité absolue post-16/06.

## 7.4 Ordre de priorité recommandé entre les 4 chantiers majeurs

### Séquence optimale (sous réserve GO chaque étape)

```
SEMAINE 25 (17-23/06) ─ Si GO 16/06
├── J1     : Quick wins CTR Vague 1 (3 pages)        [0,5 j]
├── J2-4   : SEO Phase 2 /expertise-medicale          [2,5 j]
└── J5     : Quick wins CTR Vague 2 (medecin + AAH)  [0,3 j]

SEMAINE 26 (24-30/06) ─ Observation Phase 2
├── Suivi GSC quotidien sur /expertise-medicale
└── Décision Vague 3 (pages filles) à J+14 (08/07)

SEMAINE 27-28 ─ Si Phase 2 stable
├── Page fille /expertise-medicale/assureur           [4 j]
└── Quick win CTR Vague 3 (protection-juridique)     [0,2 j]

SEMAINE 29-32 ─ Si page fille assureur stable
├── Page fille /expertise-medicale/mdph               [3 j]
├── Page fille /expertise-medicale/accident-travail   [3 j]
└── Page fille /expertise-medicale/contre-expertise   [3 j]

SEMAINE 33-36 ─ Si trafic stabilisé et conversion OK
└── Simulateur AT                                     [11 j]

SEMAINE 37+ ─ Après stabilisation AT
└── Simulateur MP                                     [15,5 j]
```

### Justification de l'ordre

| Ordre | Raison |
|---|---|
| **1. SEO Phase 2** | Effort le plus faible, impact immédiat, dépendance externe minimale |
| **2. Pages filles** | Capitalise sur Phase 2, cluster sémantique amplifie le pilier |
| **3. Simulateur AT** | Effort moyen, impact moyen-fort, mais nécessite charge dev plus lourde et validation juridique |
| **4. Simulateur MP** | Plus complexe (tableaux MP + CRRMP), à dériver d'AT une fois stabilisé |

### ⚠️ Important — Si signaux GSC dégradés le 16/06

**Tous les chantiers `/expertise-medicale` passent en REPORT-30j.**
**Le Simulateur AT peut néanmoins être lancé en autonomie** (chantier indépendant de la page pilier).
**Les quick wins CTR Vague 1 restent GO** (zéro risque, zéro dépendance).

## 7.5 Garde-fous transverses

| Garde-fou | Application |
|---|---|
| Toute modification SEO sur `/expertise-medicale` doit être **précédée** d'un snapshot GSC | Capture export 14j avant modification |
| Pas plus d'**une modification majeure** sur `/expertise-medicale` par semaine | Préserve la lisibilité des signaux |
| **Rollback Git prêt** à chaque déploiement (commit identifiable) | Capacité de rétropédalage en < 24h |
| Monitoring Sentry frontend sur les pages modifiées pendant 14j post-déploiement | Détection régression UX |
| Re-évaluation hebdomadaire des critères de la checklist pendant 30j | Décisions adaptatives |

---

**FIN — `DECISION_CHECKLIST_2026-06-16.md`**
**🚨 NON PUBLIÉ — DRAFT — DOCUMENT DE PRÉPARATION**
**Aucune décision ne sera prise sans application stricte des critères chiffrés ci-dessus, et seulement à compter du 2026-06-16.**
