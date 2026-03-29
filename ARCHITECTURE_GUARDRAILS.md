# ARCHITECTURE_GUARDRAILS.md
## Document de reference durable — Strategie & Expertise Sante

---

## 1. CARTOGRAPHIE DES FICHIERS

### Routes (responsabilite unique)
| Fichier | Service | Lignes | Responsabilite |
|---------|---------|--------|----------------|
| `routes/strategiia.py` | StrategiIA | ~590 | Analyse strategique, teaser, premium, PDF, admin-bypass |
| `routes/dossier_express.py` | Dossier Express | ~695 | Upload, extraction, pipeline IA, PDF, suivi, admin-bypass |
| `routes/admin.py` | Admin | ~1850 | Auth, CRUD, premium review workflow |
| `routes/payments.py` | Paiements | ~190 | Stripe, PayPal |

### Utilitaires (mutualises volontairement)
| Fichier | Consommateurs | Role |
|---------|---------------|------|
| `utils/llm.py` | strategiia, dossier_express | Appels LLM (sync, async, stream, multi-stage) |
| `utils/notifications.py` | strategiia, dossier_express | Alertes admin + delai client |
| `utils/document_extraction.py` | dossier_express uniquement | OCR, PDF parsing |
| `utils/pdf.py` | strategiia, dossier_express | Generation PDF |
| `utils/email.py` | strategiia, dossier_express, admin | Envoi email |
| `utils/storage.py` | dossier_express | Upload S3 |
| `utils/auth.py` | tous | JWT auth |

### Constants (source unique de verite)
| Fichier | Role |
|---------|------|
| `constants/prompts.py` | Tous les prompts LLM |
| `constants/statuses.py` | Tous les statuts, etapes, labels |
| `constants/workflows.py` | Configs (retry, limites, quotas) |
| `constants/guards.py` | Assertions anti-contamination + transitions |

---

## 2. COLLECTIONS MONGODB

| Collection | Service proprietaire | Schema minimal |
|------------|---------------------|----------------|
| `strategiia_analyses` | StrategiIA | id, email, type_dossier, status, analysis |
| `dossier_express` | Dossier Express | id, email, status, delivery_status, processing_step, analysis |
| `premium_analyses` | **PARTAGEE** (filtree par `type`) | id, type, email, status, relecture_expert_required |
| `cas_anonymises` | StrategiIA | id, type_dossier, strategie, resultat |
| `users` / `contacts` | Admin | email, role, created_at |

**REGLE** : `premium_analyses.type` DOIT etre `strategiia` ou `dossier_express`. Verifie par `assert_valid_service()`.

---

## 3. ZONES DE CONTAMINATION CROISEE

| Zone | Risque | Statut | Action |
|------|--------|--------|--------|
| `premium_analyses` collection | Moyen | SAIN — filtree par `type` + guard | Maintenir `assert_valid_service` a chaque insert |
| `utils/llm.py` | Faible | SAIN — fonctions pures, pas d'etat | Aucune action requise |
| `utils/notifications.py` | Faible | SAIN — fonctions pures | Aucune action requise |
| `utils/pdf.py` | Faible | SAIN — fonctions separees `generate_secured_pdf` vs `generate_dossier_pdf` | Aucune action requise |
| `routes/__init__.py` | Faible | SAIN — simple agregation | Ne pas modifier l'ordre |
| Prompts dans `constants/prompts.py` | Faible | SAIN — bien separes par service | Prefix clair par service |

---

## 4. CE QU'IL NE FAUT JAMAIS CASSER

### Tunnels critiques
1. **StrategiIA** : formulaire -> analyse teaser -> paywall -> premium -> PDF -> admin
2. **Dossier Express** : upload -> extraction -> multi-stage pipeline -> PDF -> suivi -> admin

### Invariants techniques
- `_has_llm_key()` doit etre appele avant tout appel LLM
- `assert_premium_analyses_entry()` doit etre appele avant toute insertion dans `premium_analyses`
- `_update_dossier_step()` doit etre le seul moyen de modifier `processing_step` et `delivery_status`
- Les appels LLM via proxy Emergent ne doivent JAMAIS depasser `max_tokens=1500` par section (timeout 60s)
- Le pipeline multi-stage DOIT generer 7 sections en 3 batches paralleles

---

## 5. CONVENTIONS DE NOMMAGE

- Routes : `/api/{service}/{action}` (ex: `/api/strategiia/analyze`, `/api/dossier-express/submit`)
- Fonctions privees : `_prefixe_action` (ex: `_process_dossier_express`, `_run_analysis`)
- Collections : snake_case (ex: `strategiia_analyses`, `dossier_express`)
- Logs : `[SERVICE][ID] message` (ex: `[DOSSIER_EXPRESS][bfc7d774] Batch 1/3: ...`)

---

## 6. ERREURS HISTORIQUES A NE PAS REPRODUIRE

| Erreur | Cause | Prevention |
|--------|-------|------------|
| Timeout 502/503 LLM | Appel unique trop gros (>60s) via proxy Emergent | Pipeline multi-stage, max_tokens=1500 |
| Contamination croisee | Monolithe strategiia.py melangeait tout | Fichiers separes + guards |
| OpenCV auto-crop boucle | Traitement image complexe en JS | NE JAMAIS reimplementer — camera native uniquement |
| Perte de prompts | Prompts dupliques dans plusieurs fichiers | Source unique dans `constants/prompts.py` |
| S3 crash pipeline | Echec upload S3 bloquait tout le pipeline | Upload S3 est non-bloquant (try/except) |

---

## 7. CHECKLIST OBLIGATOIRE AVANT TOUT DEPLOY

- [ ] `python3 -m pytest backend/tests/ -v` — tous les tests passent
- [ ] `ruff check backend/` — zero erreur lint
- [ ] Les 2 tunnels fonctionnent (curl E2E)
- [ ] Les routes dans `routes/__init__.py` incluent tous les routers
- [ ] Les imports dans chaque route sont corrects (pas de circular imports)
- [ ] Aucune cle API hardcodee (tout dans .env)
- [ ] Les logs sont prefixes par service
- [ ] Les prompts sont UNIQUEMENT dans `constants/prompts.py`

---

## 8. DEPENDANCES CRITIQUES

| Dependance | Usage | Risque si absente |
|------------|-------|-------------------|
| EMERGENT_LLM_KEY | Proxy LLM Anthropic | Pipeline IA bloque |
| ANTHROPIC_API_KEY | SDK natif (optionnel) | Fallback vers proxy |
| STRIPE_API_KEY | Paiements | Checkout bloque |
| RESEND_API_KEY | Emails | Emails non envoyes (non-bloquant) |
| S3 credentials | Stockage PDF | Download bloque (non-bloquant) |
| MONGO_URL | Base de donnees | App crash |
