# MOTEUR IA OFFICIEL — V1 VALIDEE
## Strategie & Expertise Sante — Baseline Strategique Finale
### Date de gel : 05/04/2026

---

## A. COMPOSANTS DU MOTEUR IA OFFICIEL

### 1. PROMPTS IA — VERSION OFFICIELLE GELEE

| Prompt | Fichier | Longueur cible | Statut |
|---|---|---|---|
| `STRATEGIIA_SYSTEM_PROMPT` | `constants/prompts.py` | N/A (system) | GELE |
| `STRATEGIIA_BASIC_PROMPT` | `constants/prompts.py` | 550 mots max | GELE |
| `STRATEGIIA_PREMIUM_PROMPT` | `constants/prompts.py` | 1800-2400 mots | GELE |
| `STRATEGIIA_SYSTEM_COMPACT` | `constants/prompts.py` | N/A (appels scindes) | GELE |
| `DOSSIER_EXPRESS_SYSTEM_PROMPT` | `constants/prompts.py` | N/A (system) | GELE |
| `DOSSIER_EXPRESS_PROMPT` | `constants/prompts.py` | 2000-2800 mots | GELE |
| `SYSTEM_PROMPT_LIGHT` | `utils/chatbot.py` | 2 lignes max | GELE |
| `SYSTEM_PROMPT_FULL` | `utils/chatbot.py` | 2 lignes max | GELE |
| `TABLEAUX_MP` | `utils/chatbot.py` | N/A (reference) | GELE |

### 2. MECANIQUES IA GELEES

#### 4 Blocs Premium (presents dans StrategiIA Premium et Dossier Express)
- Le vrai noeud du dossier
- Ce qui renforce / Ce qui fragilise
- Evaluation strategique rapide
- L'etape la plus rentable maintenant

#### Ciblage contextuel obligatoire
- **Classes metier** : Transport/conduite, BTP/manutention, Sante/soins, Administratif/bureau, Securite/intervention, Industriel/technique, Independant/liberal
- **Familles de sinistre** : Maladie professionnelle, Accident du travail, Rechute/aggravation, Sous-evaluation IPP, Refus CPAM/assurance, Expertise defavorable, Invalidite/inaptitude
- **Types de blocage** : Probatoire, Medical, Administratif, Qualification, Traduction fonctionnelle

#### Garde-fous redactionnels
- Anti-genericite : 36 formulations bannies (tolerance zero)
- Anti-repetition : chaque section a une mission unique et exclusive
- Preuve de lecture reelle du dossier (croisement d'elements, chronologie)
- Humanisation redactionnelle haut de gamme
- Robustesse sur dossiers incomplets
- Verification croisee x3
- Nuance intelligente (formulations conditionnelles)
- Anti-hallucination (jamais d'extrapolation abusive)

#### Pipeline LLM
- Appel synchrone natif Anthropic (llm_sync_call)
- Appel asynchrone Emergent proxy (llm_async_call)
- Streaming httpx (llm_stream_call)
- Multi-stage 7 sections paralleles Dossier Express (generate_dossier_report_multistage)
- Appels scindes paralleles StrategiIA Premium (2 calls)
- Modele : claude-sonnet-4-5-20250929

### 3. BASE METIER IA VALIDEE

#### A. Base assurantielle
- **Fichier** : `constants/assurance_knowledge.py` (961 lignes)
- **Assureurs** : GENERALI, GROUPAMA, CNP
- **Garanties** : ITT, ITP, IPT, IPP, PTIA, PE, Deces
- **Helpers** : `get_assurance_context()`, `detect_assurance_context()`

#### B. Base CCAS RATP / Contestation
- **Fichier** : `constants/contestation_knowledge.py` (483 lignes)
- **Perimetre** : Procedures MP, contestation IPP, CSOM, Commission Medicale
- **Helpers** : `get_contestation_context()`, `detect_contestation_context()`

#### C. Base MDPH
- **Fichier** : `constants/mdph_knowledge.py` (641 lignes)
- **Perimetre** : AAH, PCH, RQTH, CMI, pension invalidite, maladies invalidantes, voies de recours, orientation professionnelle
- **Helpers** : `get_mdph_context()`, `detect_mdph_context()`

#### D. Moteur Patterns Anonymises
- **Route** : `routes/knowledge_patterns.py` (CRUD admin + moteur de selection)
- **Seeds** : `constants/seed_patterns.py`
- **En base** : 14 patterns AT/MP/assurantiel + 26 patterns MDPH Premium v1 = 40 patterns total
- **Scoring** : categorie (+5), type_sinistre (+10), metier (+3), blocage (+5), tags (+3 chacun)
- **Limites** : max 5 patterns, 4 vigilances, 4 leviers (total 12 injections)
- **Garde-fous** : usage_autorise=True obligatoire, anti-pollution hors contexte, fallback safe
- **Anti-hallucination** : formulations conditionnelles uniquement ("ce type de dossier est souvent fragilise lorsque...")

### 4. CADRE D'APPRENTISSAGE OFFICIEL ET CONFORME — V1

#### Logique RGPD / Amelioration continue
- `improvement_optout` : flag boolean dans chaque analyse (StrategiIA, Dossier Express)
- Si `improvement_optout=True` : aucun enrichissement, aucune injection de patterns
- Separation stricte : donnees clients (jamais reutilisees) vs patterns reutilisables (anonymises, abstraits)
- Interdiction absolue de reutilisation des donnees brutes identifiables
- Logique d'anonymisation metier : patterns generiques, non reidentifiables, juridiquement prudents
- Validation manuelle admin obligatoire avant activation (`usage_autorise=True`)
- Usage conditionnel uniquement : injection dans le SYSTEM prompt, jamais dans le USER prompt

#### Composant frontend associe
- `DataConsentBox.jsx` : case de consentement RGPD visible par le client
- Politique de Confidentialite mise a jour (section 12)

### 5. OUTIL INTERNE OFFICIEL DE PILOTAGE QUALITE — V1

- **Fichier** : `utils/quality_scoring.py` (220 lignes)
- **Criteres** (total /100) :
  - Personnalisation metier : 0-20
  - Personnalisation sinistre : 0-20
  - Identification du blocage : 0-15
  - Presence des blocs premium : 0-15
  - Densite utile : 0-15
  - Faible genericite : 0-10
  - Coherence globale : 0-5
- **Niveaux** :
  - Excellence : 80+/100
  - Premium : 60+/100
  - Solide : 40+/100
  - A Renforcer : <40/100
- **Usage** : interne admin uniquement, ne modifie pas le rendu client

---

## B. FICHIERS GELES

| Fichier | Perimetre gele | Lignes |
|---|---|---|
| `constants/prompts.py` | Tous les prompts systeme et utilisateur | 477 |
| `utils/llm.py` | Pipeline LLM complet | 342 |
| `utils/chatbot.py` | Chatbot prompts, FAQ, detection complexite | 199 |
| `utils/quality_scoring.py` | Scoring qualite interne | 220 |
| `constants/assurance_knowledge.py` | Base assurantielle | 961 |
| `constants/contestation_knowledge.py` | Base CCAS RATP | 483 |
| `constants/mdph_knowledge.py` | Base MDPH | 641 |
| `constants/seed_patterns.py` | Patterns seed (AT/MP + MDPH) | ~330 |
| `routes/knowledge_patterns.py` | Moteur de selection + CRUD | 320+ |

---

## C. CE QUI NE DOIT PAS ETRE MODIFIE SANS PROTOCOLE

- Les prompts USER valides (STRATEGIIA_BASIC_PROMPT, STRATEGIIA_PREMIUM_PROMPT, DOSSIER_EXPRESS_PROMPT)
- La structure des rapports PDF (sections markdown, titres, ordre)
- Les longueurs cibles (550/1800-2400/2000-2800 mots)
- La logique de scoring qualite (criteres, seuils, niveaux)
- Les garde-fous anti-hallucination et anti-genericite
- Le pipeline LLM (sync/async/stream/multi-stage)
- La logique RGPD (improvement_optout, separation donnees/patterns)
- Les patterns existants en base (modification = validation admin obligatoire)
- Les bases de connaissances (assurance, contestation, MDPH)
- Le frontend (Hero, Header, HomePage, CTA, ChatBot, tunnels client)
- Les workflows de paiement (Stripe, parcours client)

---

## D. CE QUI A ETE VALIDE

| Element | Methode de validation | Date |
|---|---|---|
| Prompts StrategiIA (Basic + Premium) | Test LLM + scoring qualite | 04/04/2026 |
| Prompt Dossier Express IA | Test LLM + scoring qualite | 04/04/2026 |
| Chatbot (orientation) | Test frontend + backend | 04/04/2026 |
| Base assurantielle (3 assureurs) | Tests unitaires | 03/2026 |
| Base CCAS RATP | Testing agent iteration 167-168 | 04/04/2026 |
| Base MDPH | Testing agent iteration 169 | 05/04/2026 |
| Pack Patterns MDPH v1 (26 patterns) | Testing agent iteration 170 | 05/04/2026 |
| Moteur knowledge_patterns (scoring) | Testing agent iteration 170 | 05/04/2026 |
| Scoring qualite | Integration dans pipeline | 04/04/2026 |
| Logique RGPD / improvement_optout | Testing agent iteration 167 | 04/04/2026 |
| Anti-pollution hors contexte | Test de non-regression | 05/04/2026 |

---

## E. PROTOCOLE OBLIGATOIRE DE FUTURE EVOLUTION

Toute modification du moteur IA V1 doit suivre ce protocole :

### Etape 1 : Definir la zone impactee
- Identifier precisement le fichier et le composant concerne
- Verifier qu'il fait partie de la zone gelee
- Si oui : ordre explicite du responsable requis

### Etape 2 : Isoler la modification
- Ne jamais modifier plusieurs briques critiques en meme temps
- Creer la modification dans un scope minimum
- Documenter ce qui change et pourquoi

### Etape 3 : Tester la non-regression
- Verifier que les prompts USER sont inchanges
- Verifier que la structure markdown des rapports est preservee
- Verifier que le scoring qualite retourne des resultats coherents
- Verifier que le moteur knowledge_patterns fonctionne sans pollution
- Verifier que les bases de connaissances injectent correctement
- Verifier qu'aucun impact frontend n'est genere
- Verifier qu'aucun impact PDF n'est genere

### Etape 4 : Valider la qualite metier
- Simuler au moins 3 cas concrets couvrant la zone modifiee
- Verifier que l'enrichissement est utile et pertinent
- Verifier que les garde-fous anti-hallucination sont respectes
- Verifier la formulation (conditionnelle, sobre, credible)

### Etape 5 : Documenter avant integration
- Mettre a jour ce fichier (IA_BASELINE_V1.md) avec la modification
- Ajouter la date, le perimetre et le resultat des tests
- Archiver le resultat du testing agent

### Exception : ajout de nouveaux patterns
L'ajout de NOUVEAUX patterns dans seed_patterns.py est autorise sans
modifier les patterns existants, a condition de :
1. Respecter la structure existante (memes champs, memes tags)
2. Utiliser une fonction de seed incrementale (idempotente)
3. Valider par testing agent (non-regression + injection qualitative)
4. Documenter dans ce fichier

---

## F. RISQUE DE REGRESSION — EVALUATION

**Niveau : NUL**

Justification :
- Les commentaires de gel sont purement documentaires (aucun impact fonctionnel)
- Aucun prompt n'a ete modifie sur le fond
- Aucune logique metier n'a ete alteree
- Aucun flux client n'a ete touche
- Aucune structure PDF n'a ete modifiee
- Aucun rendu frontend n'a ete touche
- Le gel est un acte de verrouillage, pas de transformation

---

*Document cree le 05/04/2026 dans le cadre du gel officiel du Moteur IA V1.*
*Tout futur agent ou developpeur doit lire ce document avant toute intervention sur les composants listes.*
