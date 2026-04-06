# KNOWLEDGE SYSTEM MAP — Cartographie de l'intelligence metier
## Strategie & Expertise Sante
### Date de creation : 06/04/2026

---

## 1. KNOWLEDGE PATTERNS — Moteur central d'apprentissage

### A quoi ca sert

Les knowledge patterns sont des enseignements metier anonymises, abstraits et non identifiants. Ils capturent des schemas recurrents observes dans les dossiers traites : types de blocages, leviers utiles, erreurs frequentes, pieces manquantes, signaux faibles.

Ils permettent a l'IA de s'ameliorer progressivement sans reutiliser de donnees personnelles.

### Comment ca score

Le moteur de selection (`get_knowledge_patterns_context`) attribue un score a chaque pattern valide en base :

```
Score = categorie_match (+5)
      + type_sinistre_match (+10)
      + metier_match (+3)
      + blocage_match (+5)
      + tag_match (+3 par tag commun)
```

Seuls les patterns avec `usage_autorise=True` sont consideres.

### Comment ca selectionne

1. Recupere tous les patterns valides en base
2. Calcule le score de chaque pattern par rapport au contexte du dossier
3. Filtre : score minimum de 5 pour etre retenu
4. Trie par score decroissant
5. Selectionne :
   - Max 5 patterns generaux
   - Max 4 vigilances (`pattern_type == "vigilance"`)
   - Max 4 leviers (`pattern_type == "levier"`)
   - Total : max 12 injections

### Comment ca s'injecte

Le contexte genere est un bloc textuel insere dans le prompt USER, entre la situation client et le prompt de structure :

```
CONTEXTE MÉTIER ENRICHI (enseignements anonymisés issus de l'expérience) :
- [Type] : "[description du pattern]"
- [Type] : "[description du pattern]"
Note : ces enseignements sont des observations générales. Adapte-les au cas réel.
```

**Garde-fous** :
- Formulations conditionnelles uniquement ("ce type de dossier est souvent fragilise lorsque...")
- Jamais de certitude absolue
- Si contexte trop flou (0 signal) : rien n'est injecte

### Schema en base

```json
{
  "id": "uuid",
  "categorie_dossier": "maladie_professionnelle",
  "metier": "transport_conduite",
  "type_sinistre": "mp_tms",
  "type_garantie": null,
  "blocage_principal": "probatoire",
  "pattern_type": "blocage",
  "description": "[texte abstrait, max 500 chars]",
  "niveau_confiance": "eleve",
  "usage_autorise": true,
  "source_type": "strategiia",
  "tags": ["mp", "tms", "conduite"],
  "created_at": "ISO",
  "validated_by": "admin@...",
  "validated_at": "ISO"
}
```

### Statut actuel

- 40 patterns en base (14 AT/MP/assurantiel + 26 MDPH Premium v1)
- Tous valides (`usage_autorise: true`)
- Source : `constants/seed_patterns.py` (initialisation)

---

## 2. ASSURANCE_KNOWLEDGE — Base assurantielle

### Fichier : `constants/assurance_knowledge.py` (975 lignes)

### A quoi ca sert
Base de connaissances structuree sur les contrats d'assurance emprunteur. Permet a l'IA de comprendre les garanties, les definitions contractuelles, les pieges et les strategies de contestation specifiques a chaque assureur.

### Structure
- **GARANTIES_DEFINITIONS** : Definitions normalisees inter-assureurs (ITT, ITP, IPT, IPP, PTIA, PE, Deces)
- **ASSURANCE_KNOWLEDGE** : Dictionnaire par assureur (GENERALI, GROUPAMA, CNP)
  - Chaque assureur : identite, produits, garanties detaillees, particularites, points d'attention, leviers de contestation

### Helpers
- `get_assurance_context(assureur, garantie)` : Genere un bloc textuel cible pour injection dans le SYSTEM prompt
- `detect_insurer_from_text(text)` : Detecte automatiquement l'assureur dans le texte client

### Ce qui est statique
Tout le fichier est gele V1. Les definitions, les assureurs, les garanties, les strategies.

### Ce qui est enrichissable
Ajout de NOUVEAUX assureurs (sous protocole IA_BASELINE_V1.md). Pas de modification des assureurs existants.

---

## 3. CONTESTATION_KNOWLEDGE — Base CCAS RATP / Regimes speciaux

### Fichier : `constants/contestation_knowledge.py` (497 lignes)

### A quoi ca sert
Base dediee aux agents du regime special RATP et aux procedures de contestation de taux d'IPP. Couvre les specificites du regime CCAS RATP (procedures, interlocuteurs, delais) et les strategies de contestation par regime.

### Structure
- **RATP_REGIME** : Architecture complete (coordonnees, prestations, procedures MP, commission medicale)
- **CONTESTATION_PROCEDURES** : Procedures detaillees par regime (CCAS RATP et regime general CPAM)
  - CRA, TCI, expertise medicale, tribunal judiciaire
- **CONTESTATION_STRATEGY** : Points strategiques transversaux

### Helpers
- `get_contestation_context(regime, procedure)` : Injection dans le SYSTEM prompt
- `detect_contestation_context(text)` : Detection automatique du regime (RATP, CCAS, CSOM)

### Ce qui est statique
Tout le fichier est gele V1.

### Ce qui est enrichissable
Ajout de NOUVEAUX regimes speciaux (SNCF, EDF, etc.) sous protocole.

---

## 4. MDPH_KNOWLEDGE — Base MDPH

### Fichier : `constants/mdph_knowledge.py` (655 lignes)

### A quoi ca sert
Base de connaissances complete sur les droits MDPH. Couvre l'AAH, la PCH, la RQTH, les CMI, la pension d'invalidite, les maladies invalidantes et toutes les voies de recours.

### Structure
- **MDPH_GENERAL** : Presentation, missions, composition
- **AAH_ALLOCATION** : Conditions, montants, procedures, cumul
- **PCH_PRESTATION** : Types d'aide, conditions, evaluation
- **RQTH_RECONNAISSANCE** : Avantages, procedure, droits
- **CMI_CARTE** : Types (invalidite, priorite, stationnement)
- **PENSION_INVALIDITE** : Categories, montants, cumul AAH
- **MALADIES_INVALIDANTES** : Definition, exemples, droits
- **RECOURS_MDPH** : RAPO, TCI, expertise, conciliation
- **MDPH_STRATEGY** : Points strategiques, erreurs frequentes, conseils

### Helpers
- `get_mdph_context(droits_detectes)` : Injection dans le SYSTEM prompt
- `detect_mdph_context(text)` : Detection automatique de contexte MDPH (mots-cles)

### Ce qui est statique
Tout le fichier est gele V1.

### Ce qui est enrichissable
Ajout de nouvelles pathologies invalidantes, mise a jour des montants (baremes annuels), ajout de jurisprudences. Sous protocole.

---

## 5. SEED_PATTERNS — Patterns d'initialisation

### Fichier : `constants/seed_patterns.py` (429 lignes)

### A quoi ca sert
Liste de 40 patterns pre-definis utilises pour initialiser la collection `knowledge_patterns` en base MongoDB. Executee une seule fois au deploiement (fonction idempotente dans `server.py`).

### Categories de patterns
- **Blocages** : Schemas de blocage recurrents (probatoire, medical, administratif, contractuel, traduction fonctionnelle)
- **Leviers** : Strategies et actions qui ont montre leur efficacite
- **Vigilances** : Points d'attention et risques frequents
- **Erreurs frequentes** : Pieges classiques a eviter
- **Arguments utiles** : Elements de plaidoyer ou de negociation
- **Signaux faibles** : Indices subtils a ne pas negliger
- **Pieces manquantes** : Documents qui font souvent defaut

### Ce qui est statique
Les 40 patterns existants sont geles.

### Ce qui est enrichissable
Ajout de NOUVEAUX patterns autorise. La structure existante (memes champs, memes tags) doit etre respectee. Validation par testing agent obligatoire.

---

## 6. INJECTION AUTOMATIQUE vs INFORMATIF

| Source | Injecte automatiquement dans le LLM | Purement informatif (admin) |
|---|---|---|
| knowledge_patterns | OUI (via get_knowledge_patterns_context) | Aussi visible en dashboard admin |
| assurance_knowledge | OUI (via get_assurance_context) | Non visible directement |
| contestation_knowledge | OUI (via get_contestation_context) | Non visible directement |
| mdph_knowledge | OUI (via get_mdph_context) | Non visible directement |
| seed_patterns | NON (sert uniquement a initialiser la base) | Non visible |
| case_outcomes | NON (collecte V2 passive) | Visible via stats admin |

---

## 7. REUTILISABILITE POUR LA FUTURE V2

| Composant | Reutilisable pour V2 | Comment |
|---|---|---|
| knowledge_patterns | OUI | Base d'entrainement pour detection de patterns predictifs |
| case_outcomes | OUI | Donnees structurees pour apprentissage statistique |
| quality_scoring | OUI | Metrique d'evaluation des modeles V2 |
| Bases metier (assurance, MDPH, contestation) | OUI | Contexte enrichi pour les predictions |
| seed_patterns | OUI | Calibrage initial des modeles |
| SYSTEM prompts | Partiellement | Les directives de qualite restent valables |

---

*Document cree le 06/04/2026 — Kit d'Independance Projet S.E.S*
