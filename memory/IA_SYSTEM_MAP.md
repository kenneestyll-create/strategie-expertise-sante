# IA SYSTEM MAP — Cartographie complete du systeme IA
## Strategie & Expertise Sante — Moteur IA V1
### Date de creation : 06/04/2026

---

## 1. INVENTAIRE COMPLET DES PROMPTS

### 1.1 STRATEGIIA_SYSTEM_PROMPT
- **Fichier** : `constants/prompts.py` (lignes 26-182)
- **Longueur** : ~12 000 caracteres
- **Role** : Prompt systeme principal. Definit l'identite, les competences, les references juridiques, les baremes, la specialisation contextuelle, les garde-fous redactionnels et les interdictions de StrategiIA.
- **Ou il intervient** : Injecte dans CHAQUE appel LLM StrategiIA (Basic et Premium) comme message `system`
- **Ce qu'il influence** : Le ton, la structure, la profondeur, la personnalisation metier/sinistre/blocage, la qualite redactionnelle, les formulations bannies
- **Ce qu'il ne faut pas casser** : Les 36 formulations bannies, les 7 classes metier, les 7 familles de sinistre, les 5 types de blocage, les regles anti-repetition, la logique de preuve de lecture reelle

### 1.2 STRATEGIIA_BASIC_PROMPT
- **Fichier** : `constants/prompts.py` (lignes 184-223)
- **Longueur** : ~1 900 caracteres
- **Role** : Prompt utilisateur pour le rapport gratuit. Definit la structure exacte en 3 sections avec marqueurs `---SECTION_1---`, `---SECTION_2---`, `---SECTION_3---`.
- **Ou il intervient** : Appel LLM unique (pas de split) pour les analyses gratuites
- **Ce qu'il influence** : Le format du rapport Basic (6 blocs), la limite de 550 mots, le ton chaleureux
- **Ce qu'il ne faut pas casser** : Les marqueurs de section (exploites par le frontend pour la readwall), la phrase de conclusion exacte, la limite de 550 mots

### 1.3 STRATEGIIA_PREMIUM_PROMPT
- **Fichier** : `constants/prompts.py` (lignes 225-310)
- **Longueur** : ~5 900 caracteres
- **Role** : Prompt utilisateur pour le rapport premium payant. Definit 12 sections structurees dont les 4 blocs premium exclusifs.
- **Ou il intervient** : Deux appels LLM paralleles (split sections 1-5 + sections 6-9)
- **Ce qu'il influence** : Le format complet du rapport Premium (12 sections), la fourchette 1800-2400 mots, la mini-matrice d'evaluation, les angles sous-exploites
- **Ce qu'il ne faut pas casser** : L'ordre des sections (le PDF les exploite), les titres markdown exacts, la phrase finale du bouclier, les 4 blocs premium

### 1.4 STRATEGIIA_SYSTEM_COMPACT
- **Fichier** : `constants/prompts.py` (lignes 490-491)
- **Longueur** : ~740 caracteres
- **Role** : Version condensee du SYSTEM_PROMPT pour les appels scindes Premium. Evite de depasser les limites de tokens sur chaque call parallele.
- **Ou il intervient** : Utilise comme `system` dans les 2 calls paralleles du Premium
- **Ce qu'il influence** : La coherence entre les 2 parties du rapport Premium
- **Ce qu'il ne faut pas casser** : Doit rester synthetique ET garder les directives essentielles

### 1.5 DOSSIER_EXPRESS_SYSTEM_PROMPT
- **Fichier** : `constants/prompts.py` (lignes 315-414)
- **Longueur** : ~6 400 caracteres
- **Role** : Prompt systeme pour la pre-expertise documentaire. Meme ADN que StrategiIA mais oriente lecture de pieces et croisement documentaire.
- **Ou il intervient** : Pipeline multi-stage Dossier Express (7 sections)
- **Ce qu'il influence** : La qualite de la lecture documentaire, la pertinence du croisement des pieces
- **Ce qu'il ne faut pas casser** : L'orientation "preuve de lecture reelle des pieces", les regles anti-genericite, les formulations bannies

### 1.6 DOSSIER_EXPRESS_PROMPT
- **Fichier** : `constants/prompts.py` (lignes 416-485)
- **Longueur** : ~4 250 caracteres
- **Role** : Prompt utilisateur Dossier Express. Definit 13 sections structurees pour le rapport complet.
- **Ou il intervient** : Pipeline fallback (2 calls sequentiels) — le pipeline principal multi-stage utilise ses propres sous-prompts
- **Ce qu'il influence** : La structure du rapport Dossier Express quand le pipeline multi-stage n'est pas utilise
- **Ce qu'il ne faut pas casser** : Les 13 titres markdown exacts (exploites par le PDF)

### 1.7 SYSTEM_PROMPT_LIGHT et SYSTEM_PROMPT_FULL
- **Fichier** : `utils/chatbot.py` (lignes 142-161)
- **Role** : Prompts chatbot ultra-courts (2-3 lignes). Orientent vers StrategiIA ou Dossier Express en 1 phrase.
- **Difference** : LIGHT pour questions simples, FULL pour questions complexes (detection automatique par mots-cles)
- **Modele** : Claude Haiku 4.5 (max 100-150 tokens)
- **Ce qu'il ne faut pas casser** : La brievete (1 phrase + 1 lien), l'interdiction d'analyse

### 1.8 TABLEAUX_MP
- **Fichier** : `utils/chatbot.py` (lignes 96-128)
- **Role** : Reference statique des tableaux de maladies professionnelles. Utilisee pour les reponses du chatbot quand il detecte une question sur un tableau specifique.
- **Ce qu'il ne faut pas casser** : Les numeros de tableaux, les delais, les pathologies listees

---

## 2. LE PIPELINE IA REEL

### 2.1 Entree d'une demande

```
Formulaire client (SimulateurPage.jsx / DossierExpressPage.jsx)
    │
    │  Donnees : nom, situation, type_dossier, regime, metier, sinistre,
    │            blocage, montant, documents (si Dossier Express)
    │
    ↓
Backend (routes/strategiia.py ou routes/dossier_express.py)
```

### 2.2 Enrichissement contextuel (automatique, invisible pour le client)

```
Detection automatique (par mots-cles dans la situation) :
    │
    ├─ detect_insurer_from_text() → Si assureur detecte :
    │   └─ get_assurance_context(assureur, garantie) → Bloc textuel injecte
    │
    ├─ detect_contestation_context() → Si RATP/regime special detecte :
    │   └─ get_contestation_context(regime, procedure) → Bloc textuel injecte
    │
    ├─ detect_mdph_context() → Si MDPH/AAH/PCH/RQTH detecte :
    │   └─ get_mdph_context(droits_detectes) → Bloc textuel injecte
    │
    └─ get_knowledge_patterns_context(categorie, metier, sinistre, blocage) :
        └─ Selection et scoring des patterns pertinents → Bloc textuel injecte
```

### 2.3 Construction du prompt final

```
SYSTEM = STRATEGIIA_SYSTEM_PROMPT (ou DOSSIER_EXPRESS_SYSTEM_PROMPT)
         + "\n\n"
         + contexte_assurance (si detecte)
         + contexte_contestation (si detecte)
         + contexte_mdph (si detecte)

USER = situation_client
       + "\n\n"
       + contexte_patterns (si pertinent)
       + "\n\n"
       + STRATEGIIA_BASIC_PROMPT (ou PREMIUM_PROMPT ou DOSSIER_EXPRESS_PROMPT)
```

### 2.4 Appel LLM

**StrategiIA Basic** :
- 1 appel unique via `llm_stream_call`
- Max 3000 tokens
- ~550 mots attendus

**StrategiIA Premium** :
- 2 appels PARALLELES via `asyncio.gather`
- Part 1 : sections 1-5 (3000 tokens)
- Part 2 : sections 6-9 (2500 tokens)
- Assemblage : Part1 + "\n\n" + Part2
- ~1800-2400 mots attendus

**Dossier Express IA** :
- Pipeline multi-stage (`generate_dossier_report_multistage`)
- 7 sections en 3 batches paralleles :
  - Batch 1 : synthese + pieces + chronologie
  - Batch 2 : juridique + forces/vigilance
  - Batch 3 : strategie/prejudices + plan/conclusion
- 2 secondes de pause entre batches
- ~2000-2800 mots attendus

**Chatbot** :
- 1 appel unique (Claude Haiku 4.5, max 150 tokens)
- Reponse attendue : 1-2 phrases + 1 lien

### 2.5 Post-traitement

```
Texte brut LLM
    ↓
Scoring qualite (quality_scoring.score_report)
    → Score /100, niveau (Excellence/Premium/Solide/A Renforcer)
    → Stocke en base avec l'analyse
    ↓
Collecte V2 (case_outcome_memory)
    → Extraction features (blocages, pieces, leviers, famille)
    → Stockage anonymise si improvement_optout == False
    ↓
Generation PDF (utils/pdf.py ou utils/pdf_guides.py)
    → Parse markdown → FPDF2 → Upload S3 (si credentials)
    ↓
Notification admin (si premium)
    → Email Resend (si configure)
```

---

## 3. CE QUI EST GELE vs MODIFIABLE

### Prompts USER geles (INTERDICTION de modification)
- `STRATEGIIA_BASIC_PROMPT` — structure et contraintes du rapport Basic
- `STRATEGIIA_PREMIUM_PROMPT` — structure et contraintes du rapport Premium
- `DOSSIER_EXPRESS_PROMPT` — structure du rapport Dossier Express
- `SYSTEM_PROMPT_LIGHT` / `SYSTEM_PROMPT_FULL` — prompts chatbot

### Prompts SYSTEM enrichissables sous conditions
- `STRATEGIIA_SYSTEM_PROMPT` — peut recevoir de nouvelles jurisprudences, de nouveaux baremes, de nouvelles classes metier. MAIS : pas de modification des regles existantes, pas de suppression de formulations bannies, pas de changement de ton.
- `DOSSIER_EXPRESS_SYSTEM_PROMPT` — meme logique.

### Conditions d'enrichissement (protocole IA_BASELINE_V1.md)
1. Ordre explicite du responsable
2. Modification isolee (1 fichier a la fois)
3. Test de non-regression (empreintes SHA-256, scoring, patterns)
4. Validation qualite metier (3 cas simules)
5. Documentation dans IA_BASELINE_V1.md

---

## 4. RISQUES DE REGRESSION IA

### Ce qui peut rendre le texte trop generique
- Supprimer les formulations bannies du SYSTEM_PROMPT
- Retirer le ciblage contextuel obligatoire (classes metier / sinistre / blocage)
- Augmenter excessivement max_tokens (le LLM meuble avec du generique)
- Supprimer les regles anti-repetition

### Ce qui peut casser l'humanisation
- Modifier le bloc "HUMANISATION REDACTIONNELLE HAUT DE GAMME" du SYSTEM_PROMPT
- Ajouter des instructions contradictoires (ex: "sois concis" + "sois exhaustif")
- Changer le modele LLM sans recalibrage des prompts

### Ce qui peut polluer les categories entre elles
- Injecter du contexte assurance dans un dossier MDPH (les detections sont separees)
- Injecter des patterns de mauvaise categorie (le moteur de scoring protege, mais un bug le casserait)
- Modifier les helpers `detect_*_context()` sans comprendre la logique de detection

### Ce qui peut degrader la qualite premium
- Raccourcir les prompts USER (perte de structure)
- Reduire les max_tokens en dessous des seuils (rapports tronques)
- Desactiver le scoring qualite (perte de visibilite admin)
- Modifier le pipeline multi-stage Dossier Express (desequilibre entre sections)

---

## 5. MODELE LLM UTILISE

| Service | Modele | Usage |
|---|---|---|
| StrategiIA (Basic + Premium) | `claude-sonnet-4-5-20250929` | Analyses strategiques |
| Dossier Express IA | `claude-sonnet-4-5-20250929` | Pre-expertise documentaire |
| Chatbot | `claude-haiku-4-5-20251001` | Orientation rapide |
| OCR GPT | GPT Vision (via Emergent) | Extraction texte images |

### Modes de connexion
1. **Natif Anthropic** : cle API directe (`ANTHROPIC_API_KEY`)
2. **Emergent Fallback** : proxy via Emergent Universal Key (`EMERGENT_LLM_KEY`)
3. **Priorite** : natif Anthropic → Emergent fallback → erreur

---

*Document cree le 06/04/2026 — Kit d'Independance Projet S.E.S*
