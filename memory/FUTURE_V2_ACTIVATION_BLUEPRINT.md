# FUTURE V2 ACTIVATION BLUEPRINT
## Plan d'activation de l'IA Predictive V2
## Strategie & Expertise Sante
### Date de creation : 06/04/2026

---

## PREAMBULE

Ce document est un plan d'activation pour une future IA predictive. Il n'est PAS un engagement de resultat. La V2 ne doit etre envisagee que si les conditions objectives sont reunies (voir Partie E).

L'approche est volontairement prudente : pas de science-fiction, pas de promesse exageree, pas de prediction magique. La V2 doit apporter de la valeur reelle et mesurable, pas un gadget marketing.

---

## PARTIE A — CE QUI EXISTE DEJA

### A.1 Collecte silencieuse des signaux

**Module** : `utils/case_outcome_memory.py`
**Collection MongoDB** : `case_outcomes`
**Statut** : ACTIF depuis le 05/04/2026

Chaque analyse StrategiIA et Dossier Express genere automatiquement un enregistrement anonymise contenant :
- `blocage_principal` + `blocages_secondaires` : types de blocages detectes par mots-cles
- `pieces_manquantes` : documents absents identifies
- `leviers_probables` : strategies potentielles detectees
- `famille_situation` : classification du type de dossier (at_mp, assurance_emprunteur, mdph_aah, etc.)
- `niveau_complexite` : faible / moyen / eleve (base sur le nombre de signaux)
- `quality_level` + `quality_score_value` : score qualite du rapport genere
- `categorie_dossier`, `regime_ou_type_garantie` : metadata de categorisation
- `source` : strategiia ou dossier_express

### A.2 Logique RGPD stricte

- Flag `improvement_optout` : si True, AUCUN stockage — le consentement est respecte absolument
- Separation stricte : les donnees personnelles du client ne sont JAMAIS dans `case_outcomes`
- Extraction par mots-cles uniquement (pas de LLM sur les donnees de collecte)
- Pas de reidentification possible (aucun nom, email, details personnels)

### A.3 V2 Readiness — Feu tricolore admin

**Endpoint** : `GET /api/knowledge-patterns/v2-readiness`
**Frontend** : `AdminV2Readiness.jsx` (onglet Config du dashboard)

Score de 0 a 100 calcule sur 4 axes :
- Volume (50 pts) : nombre de cas exploitables / 500
- Diversite (20 pts) : familles + categories uniques
- Completude (15 pts) : pourcentage de cas avec blocage documente
- Qualite (15 pts) : pourcentage avec quality_level + leviers

Feu tricolore :
- Rouge : < 200 cas OU score < 40
- Orange : 200-499 cas ET score >= 40
- Vert : >= 500 cas ET score >= 70

### A.4 Historique du score V2

**Endpoint** : `GET /api/knowledge-patterns/v2-readiness/history`
**Collection** : `v2_readiness_history` (snapshots quotidiens automatiques)

Graphique d'evolution visible dans le dashboard admin. Permet de suivre la progression sur 90 jours.

### A.5 Patterns reutilisables

40 patterns anonymises en base (`knowledge_patterns`), couvrant :
- 7 familles de sinistre
- 7 classes metier
- 5 types de blocage
- 7 types de patterns (blocage, levier, vigilance, erreur, argument, signal, piece)

### A.6 Bases metier reutilisables

3 bases de connaissances structurees (assurance, contestation, MDPH) directement exploitables pour enrichir les predictions V2.

---

## PARTIE B — CE QUI MANQUE POUR UNE VRAIE V2

### B.1 Moteur de detection de fragilite

**Ce que c'est** : Un systeme capable d'evaluer automatiquement la fragilite d'un dossier AVANT l'analyse IA, a partir des seules donnees du formulaire et de l'historique des cas similaires.

**Ce que ca apporterait** : Alerte precoce pour l'admin, orientation plus fine du client, personnalisation du rapport.

**Prerequis** : >= 500 cas structures avec blocages documentes + diversite suffisante.

### B.2 Moteur de hierarchisation des risques

**Ce que c'est** : Un classement automatique des risques identifies dans un dossier, base sur la frequence historique des echecs similaires.

**Ce que ca apporterait** : Section supplementaire dans les rapports ("Risques statistiquement frequents pour ce profil").

**Prerequis** : >= 500 cas + au moins 100 cas par famille principale.

### B.3 Moteur de priorisation des leviers

**Ce que c'est** : Un systeme qui recommande les leviers les plus efficaces en fonction du profil du dossier, base sur l'historique des cas resolus.

**Ce que ca apporterait** : Recommandations data-driven plutot que rule-based.

**Prerequis** : Champ `issue_reelle` et `action_recommandee` remplis dans case_outcomes (actuellement vides — necessitent un retour d'experience post-traitement).

### B.4 Score de robustesse documentaire

**Ce que c'est** : Pour Dossier Express, un indicateur objectif de la completude et de la force probatoire du dossier documentaire, base sur les cas anterieurs.

**Ce que ca apporterait** : Evaluation chiffree ("votre dossier a une robustesse de 72/100, les dossiers similaires resolus avaient en moyenne 85/100").

**Prerequis** : Historique substantiel de dossiers documentaires.

### B.5 Enrichissement comparatif inter-cas

**Ce que c'est** : La capacite de comparer un dossier avec des cas anonymises similaires et d'en tirer des insights ("dans 65% des cas similaires, le levier principal etait la contre-expertise").

**Ce que ca apporterait** : Credibilite statistique, arguments chiffres pour le client.

**Prerequis** : >= 500 cas diversifies + clustering par profil.

### B.6 Approche statistique prudente

**Ce que ca n'est PAS** : Du machine learning a grande echelle, des reseaux de neurones, du deep learning.

**Ce que ca pourrait etre** : Des statistiques descriptives et inferentielles simples, des analyses de frequence, des correlations factuelles, eventuellement de la classification supervisee legere (random forest, regression logistique) si le volume le justifie.

**Principe directeur** : La V2 doit etre explicable, verifiable et juridiquement defendable. Pas de boite noire.

---

## PARTIE C — CE QU'IL FAUDRA MODIFIER LE JOUR J

### C.1 Backend — Nouveaux modules

- Creer un module `utils/v2_predictive.py` : moteur d'analyse statistique des case_outcomes
- Creer des endpoints admin pour visualiser les predictions
- Etendre le pipeline StrategiIA et Dossier Express pour injecter les insights V2 dans le prompt SYSTEM (pas USER)

### C.2 Prompts SYSTEM — Enrichissement V2

- Ajouter un bloc optionnel dans STRATEGIIA_SYSTEM_PROMPT : "DONNEES STATISTIQUES INTERNES (si disponibles)"
- Ce bloc contiendrait les insights V2 : frequences de blocages, taux de succes par levier, profil de risque
- Formulations conditionnelles obligatoires : "les donnees internes suggerent que...", "dans les cas comparables documentes..."

### C.3 Moteur IA — Adaptation

- Possibilite d'augmenter les max_tokens pour integrer les insights V2
- Possibilite de rajouter un appel LLM specifique pour la section "Analyse predictive" du rapport

### C.4 Frontend — Affichage conditionnel

- Section supplementaire optionnelle dans les rapports Premium : "Eclairage statistique"
- Badge ou mention discrete : "Enrichi par l'experience de X dossiers similaires"
- Dashboard admin : tableau de bord V2 avec metriques predictives

---

## PARTIE D — CE QU'IL NE FAUDRA PAS TOUCHER

### D.1 Promesse de marque
Le ton premium, chaleureux, professionnel et rassurant ne doit PAS changer. La V2 enrichit, elle ne remplace pas l'approche humaine.

### D.2 Prudence juridique
- Aucune V2 ne doit "predire" un resultat judiciaire
- Aucune V2 ne doit promettre un montant d'indemnisation
- Formulations obligatoires : "les donnees suggerent", "selon l'experience documentee", "sous reserve"

### D.3 Interdiction de surpromettre
- Pas de score de probabilite de succes (ex: "78% de chances de gagner")
- Pas de benchmark client vs client
- Pas de comparaison identifiable entre dossiers

### D.4 Pipeline existant
- Les prompts USER valides restent inchanges
- Le scoring qualite reste identique
- La logique RGPD reste strictement respectee
- La structure PDF reste stable

### D.5 Structure de confiance du produit
- Le disclaimer "outil d'aide a la decision, pas un conseil juridique" reste present
- L'engagement humain (expertise manuelle, relecture admin) reste central
- La V2 est un COMPLEMENT, pas un remplacement

---

## PARTIE E — CONDITIONS DE LANCEMENT

La V2 ne doit etre envisagee QUE si TOUTES les conditions suivantes sont reunies :

| Condition | Seuil minimum | Verification |
|---|---|---|
| Feu tricolore V2 readiness | VERT | Dashboard admin |
| Cas exploitables | >= 500 | `case_outcomes` avec `utilisable_pour_apprentissage=True` |
| Base d'issues reelles | >= 200 cas avec `issue_reelle` rempli | Retour d'experience post-traitement |
| Diversite de cas | >= 5 familles de situation representees | Repartition dans case_outcomes |
| V1 stable | Aucune regression ouverte | Tests + monitoring |
| Logique RGPD | Tous les opt-out respectes | Audit `improvement_optout` |
| Validation responsable | Accord ecrit explicite | Decision humaine |

**Estimation realiste** : Au rythme actuel (3 cas en base), atteindre 500 cas prendra plusieurs mois d'activite commerciale reelle. La V2 n'est pas un objectif a court terme.

---

## PARTIE F — PROTOCOLE DE MISE EN PRODUCTION FUTURE

### F.1 Avant activation

1. **Verifier le score V2 readiness** : doit etre vert (>= 70/100, >= 500 cas)
2. **Auditer les case_outcomes** : verifier la qualite et la diversite des donnees
3. **Developper le module V2** : `utils/v2_predictive.py`
4. **Tester sur un echantillon** : simuler les predictions sur 50 cas connus, verifier la pertinence
5. **Faire valider par un juriste** : les formulations predictives doivent etre juridiquement sures
6. **Mettre a jour IA_BASELINE_V1.md** : documenter les modifications

### F.2 Deploiement progressif

1. **Phase 1 — Admin only** : afficher les predictions dans le dashboard admin uniquement
2. **Phase 2 — Premium only** : integrer dans les rapports Premium avec mention "enrichissement experimental"
3. **Phase 3 — Generalisation** : si les retours sont positifs, integrer dans tous les rapports

### F.3 Surveillance post-activation

1. **Monitoring qualite** : verifier que le scoring qualite ne diminue pas
2. **Feedback client** : surveiller les retours et les taux de satisfaction
3. **Regression IA** : verifier que les rapports sans V2 restent identiques
4. **Performance** : verifier que les temps de reponse restent acceptables

### F.4 Rollback si necessaire

1. **Desactiver le module V2** : retirer l'injection V2 du pipeline sans toucher au reste
2. **Revenir au pipeline V1 pur** : les prompts USER n'ayant pas change, le rollback est transparent
3. **Documenter la raison** : pourquoi le rollback a ete necessaire, quoi corriger avant une prochaine tentative

---

## INDEPENDANCE VIS-A-VIS D'EMERGENT

Ce blueprint est concu pour etre executable sans Emergent :

- Le code source est versionne sur GitHub
- Les bases de connaissances sont dans le code (pas sur des services externes)
- Le module V2 sera un fichier Python autonome
- Les donnees sont dans MongoDB (portable)
- Le seul point d'attention : la cle LLM (Anthropic native fonctionne sans Emergent)

Pour se passer d'Emergent :
1. Obtenir une cle API Anthropic directe
2. Configurer `ANTHROPIC_API_KEY` dans l'environnement
3. Deployer sur n'importe quel serveur (VPS, AWS, Railway, etc.)
4. Le pipeline `llm_sync_call` fonctionne directement sans Emergent

---

*Document cree le 06/04/2026 — Kit d'Independance Projet S.E.S*
