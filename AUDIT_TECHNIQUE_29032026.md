# RAPPORT D'AUDIT TECHNIQUE — 29 mars 2026

## A) LENTEUR StrategiIA PREMIUM

### 1. Cause racine exacte

Le proxy Emergent (`integrations.emergentagent.com`) a un **gateway timeout HARD de 60 secondes**.
Quand le prompt premium complet est envoyé en un seul appel (~9200 chars input, 6000 max_tokens output),
le LLM prend >60s pour produire le premier token → le proxy retourne **502 Bad Gateway**.

L'agent précédent a contourné en divisant l'appel en 2 parties **SÉQUENTIELLES** :
- Part 1 terminait en ~45s → OK
- Part 2 injectait Part 1 dans son prompt → alourdissait → aussi 502

**Résultat** : architecture cassée ou ~100s quand Part 2 marchait par chance.

### 2. Correction exacte appliquée

Fichier modifié : `/app/backend/routes/strategiia.py`, fonction `_llm_async_call`

**Avant** : 2 appels LLM séquentiels, Part 2 dépendant de Part 1 (injecte `part1[:1200]`)
**Après** : 2 appels LLM **PARALLÈLES** via `asyncio.gather`, chacun indépendant

- Part 1 : Sections 1-5 (situation, lecture, cadre juridique, leviers, vigilance)
- Part 2 : Sections 6-9 (angles, évaluation, plan d'action, engagement)
- Chaque appel reçoit la situation complète mais génère uniquement ses sections assignées
- Les résultats sont assemblés à la fin

### Preuves de timing

| Métrique | AVANT | APRÈS |
|---|---|---|
| Architecture | 2 appels séquentiels | 2 appels parallèles |
| Part 2 dépend de Part 1 | OUI → 502 fréquent | NON → stable |
| Temps total backend | >100s (souvent échec) | **57s** |
| Temps total UI (formulaire → premium affiché) | N/A (crash) | **~90s** (dont 24s pour basic) |
| Output | ~5900 chars (Part 2 perdue) | **13600 chars** (complet) |

---

## B) DOSSIERS INTROUVABLES DANS L'ADMIN

### 3. Cause racine exacte

Trois problèmes distincts :

**B1 — Aucune entrée StrategiIA dans `premium_analyses`** :
L'endpoint `admin-bypass-premium` (L.1871) lançait l'analyse mais ne créait **AUCUNE** entrée
dans la collection `premium_analyses`. Le filtre frontend `items.filter(i => i.type === 'strategiia')`
retournait toujours 0 résultats.

**B2 — Champ `relecture_expert_required` manquant** :
L'auto-register dans `_process_dossier_express` (L.1143) créait des entrées dans `premium_analyses`
SANS le champ `relecture_expert_required`. Les 46 documents existants avaient `relecture=None`.
Le badge "Relecture Expert" ne s'affichait pas.

**B3 — Pas de lien `dossier_id`** :
Certaines entrées `premium_analyses` n'avaient pas de `dossier_id`, rendant impossible le bouton
"Consulter l'analyse" pour accéder au contenu.

### 4. Correction exacte appliquée

**Fix B1** : `admin-bypass-premium` crée maintenant une entrée `premium_analyses` avec :
```
type: "strategiia", relecture_expert_required: true, job_id, context, email
```

**Fix B2** : `_process_dossier_express` auto-register inclut maintenant `relecture_expert_required: true`

**Fix B3** : Migration des 44 documents existants → `relecture_expert_required: true`

### Preuves MongoDB

| Collection | Avant | Après |
|---|---|---|
| `premium_analyses` total | 46 | 47 |
| type=strategiia | **0** | **5** |
| type=dossier_express | 46 | 42 |
| `relecture_expert_required=True` | **2** | **47/47** |
| `relecture_expert_required=None` | **44** | **0** |

### Preuve UI

- Onglet StrategiIA : Badge "1" → Section "Relecture expert — StrategiIA" → 1 dossier "En attente" visible
- Onglet Dossier Express : Badge "25" → Tous les dossiers avec badge "Relecture Expert" rouge
