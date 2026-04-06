# PREDICTIVE V2 — SYSTEME DORMANT
## Documentation complete du module V2 preinstalle
### Date de creation : 06/04/2026

---

## 1. RESUME

Le module V2 Predictive est un systeme d'analyse preinstalle mais totalement inactif.
Il est concu pour etre active uniquement quand les conditions objectives sont reunies
(minimum 500 cas exploitables, score readiness >= 70, diversite suffisante).

**Statut actuel** : DESACTIVE (OFF)
**Impact sur les clients** : ZERO (tant que OFF)
**Reversibilite** : INSTANTANEE (kill switch admin)

---

## 2. ARCHITECTURE DU MODULE

### Backend
```
utils/predictive_v2.py          # Moteur predictif (regles de fragilite, scoring)
utils/predictive_logging.py     # Journalisation audit V2
routes/predictive_v2_admin.py   # Routes admin (status, activation, sandbox, comparateur, config, audit)
```

### Frontend
```
components/AdminPredictiveV2.jsx   # Panneau complet V2 dans l'onglet Config admin
```

### Collections MongoDB
```
app_config                      # Feature flag + parametres V2
v2_audit_log                    # Journal d'audit des actions V2
v2_readiness_history            # Historique du score readiness
case_outcomes                   # Donnees collectees pour la V2
```

---

## 3. FEATURE FLAG

Le coeur du systeme est un feature flag persistant en base de donnees :

```
Collection : app_config
Document : { key: "predictive_v2_enabled", value: false }
```

Ce flag est lu par :
- Le backend avant toute logique V2 (`is_v2_enabled(db)`)
- Les hooks dormants dans strategiia.py et dossier_express.py

**Si false** : aucun code V2 ne s'execute dans les flux clients.
**Si true** : les analyses integrent les signaux V2 (score de robustesse, alertes).

---

## 4. HOOKS DORMANTS

Deux hooks sont precables dans les pipelines existants :

### strategiia.py (apres le case outcome memory)
```python
from utils.predictive_v2 import is_v2_enabled, run_predictive_analysis
if await is_v2_enabled(db):
    # Analyse V2 + stockage resultats dans le document d'analyse
```

### dossier_express.py (apres le case outcome memory)
```python
from utils.predictive_v2 import is_v2_enabled, run_predictive_analysis
if await is_v2_enabled(db):
    # Analyse V2 + stockage resultats dans le document dossier
```

**Quand OFF** : le `if` court-circuite immediatement. Zero impact performance.

---

## 5. MOTEUR D'ANALYSE V2

Le moteur utilise une approche par regles (pas de ML/deep learning) :

### Regles de fragilite (8 regles actuelles)
- Absence de certificat medical detaille
- Deficit probatoire potentiel
- Risque de forclusion / delai
- Traduction fonctionnelle insuffisante
- Complexite elevee
- Projet de vie non mentionne (MDPH)
- Risque de sous-evaluation du taux
- Absence de temoignages

### Score de robustesse (0-100)
Inverse de la fragilite. Penalites par severite :
- Critique : -20 points
- Haute : -15 points
- Moyenne : -8 points
- Basse : -4 points
- Informative : -2 points

### Niveaux
- Solide (>= 80)
- Correct (60-79)
- Fragile (40-59)
- Tres fragile (< 40)

---

## 6. SECURITE DE L'ACTIVATION

### Triple confirmation
1. Popup 1 : information sur les consequences
2. Popup 2 : confirmation de comprehension
3. Popup 3 : saisie exacte de "ACTIVER V2"

### Verrous backend (refuses meme si le frontend est bypasse)
- Minimum 500 cas exploitables
- Score readiness >= 70
- Diversite >= 3 familles
- Completude >= 50% avec blocage
- Feu tricolore = VERT

### Audit
Chaque action est journalisee : activation, desactivation, test sandbox, modification de config.

---

## 7. KILL SWITCH

Bouton "Desactiver immediatement" dans l'admin.
- Effet : `predictive_v2_enabled = false`
- Resultat : retour V1 pur instantane
- Pas de redemarrage necessaire
- Pas d'intervention developpeur
- Pas de dependance a Emergent

---

*Document cree le 06/04/2026 — Kit d'Independance Projet S.E.S*
