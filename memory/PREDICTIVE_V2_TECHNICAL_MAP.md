# PREDICTIVE V2 — CARTE TECHNIQUE
## Architecture technique complete du module V2
### Date de creation : 06/04/2026

---

## 1. FLUX DE DONNEES

```
Client soumet une analyse (StrategiIA ou Dossier Express)
    |
    v
Pipeline V1 existant (prompts, LLM, scoring qualite)
    |
    v
Case Outcome Memory (collecte silencieuse, si optout=false)
    |
    v
[HOOK V2 DORMANT]
    |
    └─ is_v2_enabled(db) ?
         |
         ├─ FALSE → fin (zero impact, zero latence)
         |
         └─ TRUE → run_predictive_analysis()
              |
              ├─ Detection fragilites (8 regles)
              ├─ Calcul score robustesse (0-100)
              ├─ Generation alertes triees par severite
              └─ Stockage dans le document d'analyse (champ v2_predictive)
```

---

## 2. ENDPOINTS API

| Methode | Route | Role |
|---------|-------|------|
| GET | `/api/predictive-v2/status` | Etat complet (flag, config, readiness, verrous) |
| POST | `/api/predictive-v2/activate` | Activation securisee (triple confirmation) |
| POST | `/api/predictive-v2/deactivate` | Kill switch immediat |
| GET | `/api/predictive-v2/config` | Configuration V2 |
| PUT | `/api/predictive-v2/config` | Modification parametres |
| POST | `/api/predictive-v2/sandbox/analyze` | Test sandbox (zero impact) |
| POST | `/api/predictive-v2/sandbox/compare` | Comparateur V1/V2 |
| GET | `/api/predictive-v2/audit-log` | Journal d'audit |

Tous ces endpoints sont **admin-only** (Depends(get_current_admin)).

---

## 3. COLLECTIONS MONGODB

### app_config (feature flag + parametres)
```json
{ "key": "predictive_v2_enabled", "value": false }
{ "key": "v2_min_cases", "value": 500 }
{ "key": "v2_min_readiness_score", "value": 70 }
{ "key": "v2_max_alerts_per_analysis", "value": 5 }
{ "key": "v2_prudence_level", "value": "haute" }
```

### v2_audit_log (tracabilite)
```json
{
  "id": "uuid",
  "event_type": "activation|deactivation|sandbox_test|sandbox_compare|config_change|activation_refused",
  "admin_email": "admin@...",
  "details": { ... },
  "timestamp": "ISO"
}
```

---

## 4. REGLES DE FRAGILITE

| ID | Label | Condition | Severite |
|----|-------|-----------|----------|
| no_medical_cert | Absence certificat medical | Mots-cles absents | haute |
| no_proof_of_exposure | Deficit probatoire | Mots-cles absents | haute |
| deadline_risk | Risque forclusion | Mots-cles presents | critique |
| weak_functional_translation | Traduction fonctionnelle | Mots-cles absents | moyenne |
| complexity_high | Complexite elevee | Niveau complexite | informative |
| no_project_vie | Projet de vie MDPH | MDPH sans projet | haute |
| undervaluation_risk | Sous-evaluation taux | Mots-cles presents | moyenne |
| no_witnesses | Absence temoignages | Mots-cles absents | basse |

---

## 5. POINTS D'INJECTION FUTURS

Quand la V2 sera active, les signaux pourront etre injectes dans :

| Zone | Comment | Fichier |
|------|---------|---------|
| Analyse StrategiIA | Champ `v2_predictive` dans le document MongoDB | strategiia.py |
| Dossier Express | Champ `v2_predictive` dans le document MongoDB | dossier_express.py |
| SYSTEM prompt | Via `generate_v2_context_block()` (futur) | predictive_v2.py |
| Dashboard admin | Affichage des alertes V2 dans la fiche analyse | AdminDashboard.jsx |

**Important** : l'injection dans le SYSTEM prompt n'est PAS activee actuellement.
Le hook dormant stocke les donnees V2 en base mais ne les injecte PAS dans les prompts LLM.
Cette injection sera une etape supplementaire a developper lors de l'activation reelle.

---

## 6. INDEPENDANCE VIS-A-VIS D'EMERGENT

Le module V2 est 100% independant d'Emergent :
- Le feature flag est en MongoDB (portable)
- Le moteur predictif est un fichier Python pur (pas de service externe)
- L'interface admin est du React standard
- Les routes utilisent FastAPI standard
- Aucune cle API externe n'est necessaire pour la V2

Pour deployer ailleurs :
1. Exporter le code source (deja sur GitHub)
2. Configurer MongoDB
3. Configurer la cle LLM Anthropic
4. Deployer sur n'importe quel serveur

---

*Document cree le 06/04/2026 — Kit d'Independance Projet S.E.S*
