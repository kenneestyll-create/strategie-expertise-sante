# CONSOLIDATION ARCHITECTURE — Stratégie & Expertise Santé
# Date: 29 mars 2026
# Objectif: Stabilisation structurelle, isolation services, garde-fous

---

## 1. TABLEAU D'ISOLATION — StrategiIA vs Dossier Express IA

| Élément | StrategiIA | Dossier Express IA | Séparé | Action |
|---|---|---|---|---|
| **Prompts IA** | STRATEGIIA_SYSTEM_PROMPT + STRATEGIIA_BASIC/PREMIUM_PROMPT | DOSSIER_EXPRESS_PROMPT | OUI | Prompts dans strategiia.py L.30-250, séparés par variable |
| **Endpoint analyse** | /api/strategiia/analyze | /api/dossier-express/admin-bypass | OUI | Routes distinctes |
| **Endpoint checkout** | /api/strategiia/checkout | /api/dossier-express/checkout | OUI | Routes distinctes |
| **Endpoint admin bypass** | /api/strategiia/admin-bypass-premium | /api/dossier-express/admin-bypass | OUI | Routes distinctes |
| **Collection MongoDB analyse** | strategiia_analyses | dossier_express | OUI | Collections séparées |
| **Collection premium_analyses** | type="strategiia" | type="dossier_express" | OUI (champ type) | Filtre par type, garde-fou assert_valid_service |
| **Statuts progression** | in-memory _jobs{} (pending/done/error) | dossier.processing_step (12 étapes) | OUI | Modèles différents |
| **delivery_status** | N/A | en_attente/incident/livre/genere_sans_email | OUI | Exclusif Dossier Express |
| **Logique relecture expert** | relecture_expert_required=True | relecture_expert_required=True | PARTAGÉE | Même champ, même workflow admin |
| **Logique PDF** | generate_secured_pdf() | generate_dossier_pdf() | OUI | Fonctions distinctes dans utils/pdf.py |
| **Logique email** | notify_admin_premium_analysis("strategiia",...) | notify_admin_premium_analysis("dossier_express",...) | PARTAGÉE (paramétrique) | Même fonction, type en paramètre |
| **Admin dashboard** | Onglet StrategiIA (tab index 7) | Onglet Dossier Express (tab index 8) | OUI | Tabs séparés, filtre par type |
| **Composant admin relecture** | AdminPremiumReview productType="strategiia" | AdminPremiumReview productType="dossier_express" | OUI (paramétrique) | Même composant, props différentes |
| **Wording frontend** | "StratégiIA" | "Dossier Express IA" | OUI | Labels distincts |
| **Composant React principal** | StrategiIA.jsx | DossierExpressPage.jsx | OUI | Fichiers séparés |
| **Webhook Stripe** | strategiia_premium_* | dossier_express_* | OUI | Tags Stripe distincts |
| **Bypass admin** | admin-bypass-premium → crée premium_analyses type=strategiia | dossier-express/admin-bypass → crée premium_analyses type=dossier_express | OUI | Garde-fou assert_premium_analyses_entry |
| **Pipeline LLM** | _run_analysis() → _llm_async_call() | _process_dossier_express() → llm_call() | OUI | Fonctions séparées |
| **Health check** | /api/health/llm (partagé) | /api/health/llm (partagé) | PARTAGÉ | LLM check commun aux deux |

### Résultat isolation: 15 séparés / 3 partagés (paramétrique) / 0 contaminé

Les 3 éléments partagés sont PARAMÈTRIQUES (même code, type en paramètre) ce qui est correct architecturalement.

---

## 2. CENTRALISATION — Fichiers créés

| Fichier | Rôle | Contenu |
|---|---|---|
| `constants/statuses.py` | Source unique de vérité pour TOUS les statuts | Service, DossierStatus, DossierDelivery, DossierStep, PremiumStatus, JobStatus, DOSSIER_STEP_CLIENT_MAP, CLIENT_STEPS_DISPLAY |
| `constants/workflows.py` | Configuration workflow par service | Pricing, Stripe tags, retry config, quotas, limites fichiers |
| `constants/guards.py` | Assertions de protection | assert_valid_service, assert_premium_analyses_entry, assert_relecture_blocks_auto_send |

---

## 3. ZONES À RISQUE ET DÉPENDANCES

### 3.1 Zones historiquement instables

| Zone | Historique | Cause racine | Protection ajoutée |
|---|---|---|---|
| **StrategiIA premium LLM** | 5+ corrections agent, timeouts, 502, retries | Proxy Emergent gateway timeout 60s | Streaming httpx + split parallèle asyncio.gather |
| **premium_analyses.relecture** | 44 docs avec relecture=None | Insert sans le champ | assert_premium_analyses_entry() vérifie TOUS les champs |
| **premium_analyses.type** | 0 entries type=strategiia | admin-bypass ne créait pas d'entrée | Insertion systématique avec assert |
| **OCR / Document scanner** | Boucle infinie OpenCV | Auto-crop avec canvas | Supprimé. Native <input capture> |
| **litellm timeout** | Mal diagnostiqué comme 60s | OpenAI client interne retry | Contourné par httpx streaming direct |

### 3.2 Dépendances entre zones critiques

```
StrategiIA analyse basique
  → _run_analysis() → _llm_async_call()
  → strategiia_analyses collection
  → AUCUN impact sur Dossier Express

StrategiIA premium (admin-bypass)
  → _run_analysis() → _llm_async_call() (parallèle)
  → strategiia_analyses collection
  → premium_analyses collection (type=strategiia)
  → AUCUN impact sur Dossier Express

Dossier Express
  → _process_dossier_express() → llm_call()
  → dossier_express collection
  → premium_analyses collection (type=dossier_express)
  → AUCUN impact sur StrategiIA

Admin relecture
  → GET /api/admin/premium-analyses → TOUS les types
  → POST /api/admin/premium-analyses/{id}/status → modifie UN document par id
  → ISOLATION par id unique, aucun risque croisé
```

### 3.3 Pièges connus à NE PLUS reproduire

1. **Ne jamais utiliser `litellm.completion` directement** pour de longs prompts via le proxy Emergent. Utiliser `httpx` streaming.
2. **Ne jamais insérer dans `premium_analyses` sans `relecture_expert_required`**. Le garde-fou `assert_premium_analyses_entry` bloquera.
3. **Ne jamais supposer que le type est correct** — passer par `Service.STRATEGIIA` ou `Service.DOSSIER_EXPRESS` (constantes).
4. **Ne jamais ajouter d'auto-crop ou de traitement d'image custom** — native camera uniquement.
5. **Ne jamais tester uniquement en bash** — le user exige des tests UI pratiques.

---

## 4. GARDE-FOUS TECHNIQUES ACTIFS

### Backend assertions
- `assert_valid_service(type)` → bloque si type inconnu
- `assert_premium_analyses_entry(entry)` → bloque si champs manquants/incorrects
- `assert_relecture_blocks_auto_send(relecture)` → empêche l'envoi auto si relecture requise

### Logs métier structurés
Format: `[SERVICE][ID][ÉTAPE] détails`
Exemples:
- `[STRATEGIIA][admin-bypass][job_id] premium_analyses entry created`
- `[DOSSIER_EXPRESS][dossier_id][START] email=... type=... regime=...`

### Tests de non-régression
- `/app/backend/tests/test_consolidation.py` — 16 tests unitaires (constants, guards, isolation)
- `/app/backend/tests/test_consolidation_audit.py` — 19 tests API (endpoints, cross-contamination)
- Total: **35 tests, 100% pass**

---

## 5. RÉSULTAT AUDIT CONSOLIDATION

| Critère | Avant | Après |
|---|---|---|
| Isolation services | Partielle (premium_analyses sans type correct) | Complète avec assertions |
| Constantes centralisées | 0 fichier | 3 fichiers (statuses, workflows, guards) |
| Garde-fous actifs | 0 | 3 assertions bloquantes |
| Logs métier structurés | Formats mixtes | Format [SERVICE][ID][ÉTAPE] |
| Tests non-régression | 0 ciblés | 35 tests (16 unit + 19 API) |
| premium_analyses avec relecture=True | 2/46 (4%) | 47/47 (100%) |
| premium_analyses type=strategiia | 0 | 7+ |
| Documentation architecture | 0 | Ce document |

---

## 6. CHECKLIST AVANT TOUTE MODIFICATION FUTURE

Tout agent futur DOIT:
1. Lire ce document AVANT de modifier quoi que ce soit
2. Exécuter `pytest tests/test_consolidation.py tests/test_consolidation_audit.py` AVANT et APRÈS ses modifications
3. Utiliser les constantes de `constants/statuses.py` au lieu de hardcoder des strings
4. Utiliser les garde-fous de `constants/guards.py` pour toute insertion dans premium_analyses
5. Vérifier l'impact croisé (StrategiIA ↔ Dossier Express) après chaque modification
6. Ne JAMAIS revenir à litellm.completion pour le proxy Emergent
7. Ne JAMAIS insérer dans premium_analyses sans relecture_expert_required=True
