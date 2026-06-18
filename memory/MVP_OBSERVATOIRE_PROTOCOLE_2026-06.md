# 🧪 MVP OBSERVATOIRE — Plan d'expérimentation 30 jours, < 100 €

**Date :** 2026-06-18
**Statut :** PROTOCOLE DE TEST UNIQUEMENT — Aucune mise en œuvre avant levée du gel (01/07/2026)
**Forme :** plan d'expérimentation personnel, à exécuter en solo, sans aucun développement
**Objectif :** prouver ou réfuter la valeur réelle du concept Observatoire en 30 jours, avec moins de 100 € sortis du compte bancaire
**Précédents :** `DEMONSTRATION_OPERATIONNELLE_OBSERVATOIRE_2026-06.md`

---

## 🎯 Principe directeur

> *« Avant de construire l'usine, on goûte la soupe. »*

Le MVP **n'est pas** une version simplifiée de l'Observatoire complet.
Le MVP **est** un protocole d'expérimentation conçu pour répondre à une seule question :

> *« Est-ce que cette méthode me fait découvrir des choses que je n'aurais pas vues seul ? »*

Tout le reste (volume produit, automatisation, conversion, ROI) est **hors périmètre** de ce test.

---

# PARTIE 1 — Le MVP réel

## 1.1 Outils utilisés (toutes dépenses réelles affichées)

| Outil | Fonction | Coût réel sortie de compte |
|---|---|---|
| Google Search Console | Source #1 de signaux (vos données) | **0 €** — déjà actif |
| Google Trends | Tendances de recherche | **0 €** |
| Google Alerts | Veille mots-clés métier | **0 €** |
| Feedly Free | Lecture RSS centralisée (max 100 flux) | **0 €** |
| Légifrance + Cour de cassation open data | Jurisprudence et textes officiels | **0 €** |
| Google Sheets | Tableau de bord + classification | **0 €** — déjà disponible |
| Notion Free | Journal de bord + pipeline | **0 €** |
| ChatGPT Plus (1 mois) | Génération briefs, classification rapide, synthèses | **20 €** sur 1 mois |
| AnswerThePublic (gratuit 3 recherches/jour) | Détection de questions utilisateurs | **0 €** |
| Ahrefs Webmaster Tools | Backlinks et performance de votre propre site | **0 €** |
| Reserve sécurité (éventuel) | Achat ponctuel rapport, doc, ou demi-mois supplémentaire | **20–30 €** max |
| **TOTAL DÉPENSES RÉELLES 30 J** | | **20–50 €** |

⚠️ **Plafond strict : 50 €.** Le budget 100 € de l'ordre n'est consommé qu'en cas de surprise (ex. ChatGPT Plus prolongé, achat ponctuel d'un rapport sectoriel utile).

## 1.2 Ce qui est INTERDIT pendant le MVP

- ❌ Aucun développement de code
- ❌ Aucune création de base de données
- ❌ Aucun dashboard React/admin
- ❌ Aucune intégration Make.com / n8n / Zapier
- ❌ Aucun abonnement Doctrine.fr, Ahrefs Lite, Semrush
- ❌ Aucune publication d'asset (gel éditorial en vigueur)
- ❌ Aucune automatisation au-delà des alertes natives Google/RSS

## 1.3 Périmètre thématique étroit

Pour éviter la dispersion, le MVP se concentre sur **3 personas seulement** (pas 5) :

1. **Victime AT en recours** (Faute inexcusable, IPP, contestation)
2. **Demandeur MDPH refusé** (AAH, RAPO, RSDAE)
3. **Assuré en litige expertise** (Generali / Axa / Allianz, contre-expertise)

Tout signal hors de ces 3 personas est **archivé sans traitement**.

---

# PARTIE 2 — Jour 1 : installation (≈ 2 heures, dépense réelle : 20 €)

## 2.1 Plan détaillé jour 1

### Bloc 1 — Souscription ChatGPT Plus (5 min — 20 €)

- Aller sur chat.openai.com → Plans → Plus → 20 €/mois.
- **Configurer un rappel d'annulation à J+28** pour ne pas être prélevé une 2e fois si NO GO.

### Bloc 2 — Setup Google Alerts (20 min — 0 €)

Configurer **15 alertes** précises, fréquence « au fur et à mesure » :

| # | Mot-clé | Fréquence |
|---|---|---|
| 1 | « refus AAH RSDAE » | Au fur et à mesure |
| 2 | « refus pôle social AAH » | Au fur et à mesure |
| 3 | « faute inexcusable employeur Cour de cassation » | Au fur et à mesure |
| 4 | « IPP accident travail contestation » | 1×/jour |
| 5 | « expertise médicale Generali » | Au fur et à mesure |
| 6 | « expertise médicale Axa » | Au fur et à mesure |
| 7 | « contre-expertise assureur » | 1×/jour |
| 8 | « tableau maladie professionnelle nouveau » | Au fur et à mesure |
| 9 | « consolidation médicale assurance » | 1×/jour |
| 10 | « MDPH refus AEEH » | 1×/jour |
| 11 | « médecin expert assurance partial » | Au fur et à mesure |
| 12 | « barème AIPP 2026 » | Au fur et à mesure |
| 13 | « pôle social tribunal judiciaire AT » | 1×/jour |
| 14 | « CRRMP refus maladie professionnelle » | 1×/jour |
| 15 | « RAPO MDPH appel » | 1×/jour |

### Bloc 3 — Setup Feedly Free (25 min — 0 €)

Créer une collection « Observatoire MVP » avec **20 flux RSS** :

**Sources institutionnelles (5)**
- Légifrance Actualités
- Cour de cassation — derniers arrêts sociaux
- Conseil d'État — décisions récentes
- CNIL — sanctions et délibérations
- DARES — actualités

**Sources presse santé/social/assurance (10)**
- Argus de l'assurance (RSS public)
- L'Assurance en mouvement
- Hospimedia (RSS public)
- AEF Social
- Le Monde Santé
- Libération Société
- Faire-Face (handicap)
- APF France handicap actualités
- Cadre de Santé
- Préventica

**Sources B2B juridique (5)**
- Village de la Justice
- Dalloz Actualité (RSS public)
- Editions Législatives
- Doctrine (newsletter publique seule, pas la base payante)
- Lexbase (actualité publique)

### Bloc 4 — Setup Google Sheets « Observatoire MVP » (20 min — 0 €)

Créer un classeur Google Sheets avec **5 onglets** :

#### Onglet 1 — « Signaux bruts »

| Date | Heure | Source | Type | Titre court | URL | Persona | Score 1-5 | Idée d'action | Statut |
|---|---|---|---|---|---|---|---|---|---|

#### Onglet 2 — « Opportunités exploitables »

| Date détection | Sujet | Persona | Volume estimé GSC | Mot-clé principal | Concurrence | Idée d'asset | Priorité |
|---|---|---|---|---|---|---|---|

#### Onglet 3 — « Ma veille habituelle (témoin) »

> Cet onglet est crucial. Vous y notez **tout ce que vous découvrez par vos canaux habituels** (LinkedIn, conversations clients, jurisprudence ponctuellement consultée, presse parcourue le matin), **avant de regarder le MVP**.

| Date | Source habituelle | Sujet | Nouveau pour moi ? (O/N) |
|---|---|---|---|

#### Onglet 4 — « Croisement »

> Comparaison fin de semaine entre signaux MVP et veille habituelle.

| Sujet | Détecté par MVP (date) | Détecté par veille habituelle (date) | Antériorité MVP (jours) | Inédit ? |
|---|---|---|---|---|

#### Onglet 5 — « KPI MVP »

| Semaine | Signaux capturés | Opportunités retenues | Idées de contenu | Heures réelles passées |
|---|---|---|---|---|

### Bloc 5 — Setup Notion Free (10 min — 0 €)

Créer une page « Journal de bord MVP Observatoire » avec :
- Date de démarrage
- Date de fin (J+30)
- 4 sous-pages : Semaine 1, Semaine 2, Semaine 3, Semaine 4
- Une page « Décisions à prendre à J+30 »

### Bloc 6 — Configuration GSC (10 min — 0 €)

Ouvrir GSC → Performance → définir 2 filtres mémorisés :
- **Filtre A** : Pages contenant `/guide/` (perf. cluster guides)
- **Filtre B** : Requêtes commençant par « comment », « refus », « contester », « droits »

Ces filtres seront utilisés chaque lundi matin.

### Bloc 7 — Configuration Google Trends (5 min — 0 €)

Créer 4 comparaisons mémorisées (URL bookmark) :
- « refus AAH » vs « contestation MDPH »
- « faute inexcusable » vs « accident travail recours »
- « expertise médicale assurance » vs « contre-expertise »
- « IPP accident travail » vs « rente accident travail »

### Bloc 8 — Configuration AnswerThePublic (5 min — 0 €)

Préparer 3 recherches à lancer hebdomadairement (lundis) :
- « refus AAH »
- « expertise médicale »
- « accident travail »

⚠️ Limite gratuite : 3 recherches/jour. Suffisant.

### Bilan Jour 1

| Indicateur | Valeur |
|---|---|
| Temps réel passé | 2 h 00 |
| Dépense réelle sortie de compte | **20 €** (ChatGPT Plus) |
| Outils configurés | 7 |
| Sources de signaux opérationnelles | 35 (Alerts + RSS) |

---

# PARTIE 3 — Semaine par semaine : protocole détaillé

## 🗓️ Semaine 1 — Collecte brute (≈ 4 h dans la semaine)

**Objectif principal :** capturer du signal et constater son volume réel.

### Routine quotidienne (15-20 min/jour, lundi à vendredi)

**Matin (10 min) :**
1. Ouvrir boîte mail → lire les digests Google Alerts de la veille
2. Ouvrir Feedly → marquer comme « pertinent » les articles concernant les 3 personas
3. Reporter dans l'onglet « Signaux bruts » : 1 ligne par signal pertinent

**Soir (5-10 min) :**
4. Noter dans l'onglet « Ma veille habituelle » tout sujet entendu en RDV client, vu sur LinkedIn, etc.

### Routine du vendredi (60 min, plage dédiée)

1. **Examen GSC (20 min) :**
   - Période : 7 derniers jours vs 7 jours précédents
   - Lister 5 requêtes émergentes (impressions × variation %)
   - Reporter dans l'onglet « Signaux bruts » avec source = « GSC »

2. **Examen Google Trends (10 min) :**
   - Ouvrir les 4 comparaisons enregistrées
   - Repérer les pics anormaux (variation > +50 % en 7 jours)
   - Reporter dans l'onglet « Signaux bruts »

3. **Examen AnswerThePublic (10 min) :**
   - Lancer les 3 recherches (« refus AAH », « expertise médicale », « accident travail »)
   - Capturer les nouvelles questions inédites
   - Reporter dans l'onglet « Signaux bruts »

4. **Scoring (20 min) :**
   - Pour chaque signal capturé semaine 1, attribuer un score 1-5 sur 4 critères :
     - Volume potentiel d'audience (1-5)
     - Adéquation S.E.S (1-5)
     - Urgence/fenêtre temporelle (1-5)
     - Faible concurrence éditoriale visible (1-5)
   - Calculer un score moyen
   - Marquer 🟢 si score moyen ≥ 4, 🟡 si 3-3.99, ⚪ si < 3

### Livrable Semaine 1

À J+7, vous devez avoir :

- ✅ Onglet « Signaux bruts » : **30-80 lignes** attendues
- ✅ Onglet « Ma veille habituelle » : **5-15 lignes**
- ✅ Une question écrite dans Notion : *« Suis-je submergé ou la quantité est-elle gérable ? »*

**Exemples concrets de signaux attendus Semaine 1 :**

| Source | Signal réel possible |
|---|---|
| Google Alerts | Arrêt Cass. soc. récent sur faute inexcusable |
| Feedly | Article Argus sur révision barème AIPP |
| GSC | Pic +60 % sur « refus AAH RSDAE 80 % » |
| Trends | Hausse saisonnière « AEEH rentrée » |
| ATP | Question inédite « combien de temps après refus AAH peut-on redemander » |
| RSS Hospimedia | Annonce nouveau Cerfa MDPH |

## 🗓️ Semaine 2 — Tri et premières opportunités (≈ 4 h dans la semaine)

**Objectif principal :** transformer le volume brut en opportunités qualifiées et tester ChatGPT en classification.

### Routine quotidienne (15-20 min/jour)

Identique à semaine 1.

### Routine du vendredi (75 min)

1. **Compilation des signaux semaine 2 (15 min) :** mêmes opérations que semaine 1.

2. **Test ChatGPT en classification (20 min) :**
   - Copier-coller dans ChatGPT les 30-50 signaux les plus récents avec ce prompt :

   ```
   Tu es un analyste stratégique pour Stratégie & Expertise Santé.
   Voici 50 signaux capturés cette semaine.
   Pour chacun :
   1. Classe en persona : Victime AT / Demandeur MDPH / Assuré litige expertise / Autre
   2. Note urgence (1-5)
   3. Note intention de recherche : informationnelle / transactionnelle / mixte
   4. Propose en 1 phrase un angle d'article si exploitable
   5. Identifie les 3 signaux qui te semblent les plus précieux et explique pourquoi.
   ```

   - Comparer le classement ChatGPT au vôtre (fait à la main).
   - Noter dans Notion : *« ChatGPT a-t-il vu quelque chose que je n'avais pas vu ? »*

3. **Création onglet « Opportunités exploitables » (40 min) :**
   - Prendre les 3 signaux les mieux notés (par vous et par ChatGPT)
   - Demander à ChatGPT pour chacun :

   ```
   Pour ce signal "X", produit :
   - 1 angle éditorial original
   - Les 3 mots-clés primaires à viser
   - Une estimation grossière du volume mensuel
   - Un titre d'article candidat (< 70 caractères)
   - 5 questions FAQ qu'un utilisateur poserait
   ```

   - Reporter dans l'onglet « Opportunités exploitables »

### Livrable Semaine 2

- ✅ Onglet « Signaux bruts » : 60-160 lignes cumulées
- ✅ Onglet « Opportunités exploitables » : **3-6 opportunités**, chacune avec angle + mots-clés + volume + titre
- ✅ Page Notion : *« Notes sur la qualité de la classification ChatGPT »*

## 🗓️ Semaine 3 — Croisement et inéditude (≈ 4 h dans la semaine)

**Objectif principal :** vérifier si le MVP détecte des choses **avant** ou **mieux** que votre veille habituelle.

### Routine quotidienne

Inchangée.

### Routine du vendredi (90 min) — point critique de l'expérimentation

1. **Compilation signaux semaine 3 (15 min)**

2. **Croisement MVP vs veille habituelle (45 min) :**
   - Ouvrir l'onglet « Croisement »
   - Pour chaque opportunité retenue depuis le début (toutes semaines confondues), répondre honnêtement :
     - L'aviez-vous déjà identifiée par votre veille habituelle ?
     - Si oui, quand ?
     - Sinon, le MVP vous l'a fait découvrir le ______
     - Antériorité du MVP : ____ jours
     - Est-ce un sujet inédit pour S.E.S ? (O/N)
     - Est-ce un sujet que vous auriez raisonnablement découvert par ailleurs sous 30 jours ?

3. **Tableau de comparaison qualitative (30 min) :**

   Pour chaque opportunité retenue :

| Opportunité | Source MVP | Date MVP | Date veille habituelle | Inédit ? | Action faisable < 14 j ? | Verdict perso |
|---|---|---|---|---|---|---|

   Verdict perso : 🟢 « Le MVP m'a fait gagner X jours / je n'aurais pas vu » / 🟡 « J'aurais vu mais plus tard » / 🔴 « Je l'avais déjà »

### Livrable Semaine 3

- ✅ Onglet « Croisement » rempli pour **toutes** les opportunités cumulées
- ✅ Compte des verdicts 🟢 / 🟡 / 🔴
- ✅ Page Notion : « Verdict mi-parcours »

## 🗓️ Semaine 4 — Décision GO/NO GO (≈ 4 h dans la semaine + 2 h bilan)

**Objectif principal :** trancher honnêtement.

### Routine quotidienne

Inchangée.

### Routine du vendredi final (J+30) — 2-3 h dédiées

1. **Compilation finale (30 min)** : tous les onglets finalisés

2. **Bilan KPI quantitatif (30 min)** : remplir l'onglet « KPI MVP »

3. **Bilan qualitatif Notion (30 min)** : répondre par écrit à 6 questions (cf. Partie 4)

4. **Verdict GO/NO GO (30 min)** : application stricte de la règle de décision (cf. Partie 6)

5. **Décision parallèle obligatoire :** annulation ChatGPT Plus si NO GO, sinon prolongation

### Livrable Semaine 4

- ✅ Document Notion final « Verdict MVP Observatoire à J+30 »
- ✅ Décision tranchée

---

# PARTIE 4 — Livrables hebdomadaires concrets attendus

## 4.1 Récapitulatif livrables

| Semaine | Livrable principal | Forme |
|---|---|---|
| **S1** | Photographie brute du volume de signal exploitable | Tableau Sheets 30-80 lignes |
| **S2** | Liste qualifiée de 3-6 opportunités prioritaires | Tableau Sheets + classification ChatGPT |
| **S3** | Score d'inéditude mesuré objectivement | Tableau Sheets croisement |
| **S4** | Verdict GO/NO GO avec preuve | Document Notion 4 pages |

## 4.2 Exemples concrets de ce que vous trouverez probablement

Voici des exemples plausibles de ce que le MVP devrait détecter :

### Exemple 1 — Sujet émergent inattendu
**Signal :** pic Google Trends +180 % sur « simulateur AAH rentrée 2026 » mi-août.
**Action immédiate possible :** repérer si simulateur existant `/calculatrice-aah` est bien positionné.
**Valeur ajoutée :** anticipation rentrée → préparation pré-campagne (sans publier — gel respecté).

### Exemple 2 — Jurisprudence récente non encore commentée
**Signal :** arrêt Cass. soc. récent étendant la responsabilité employeur en sous-traitance.
**Action immédiate possible :** repérer angle juridique original avant que les concurrents le commentent.
**Valeur ajoutée :** capital éditorial préparé pour publication post-gel.

### Exemple 3 — Question utilisateur récurrente nouvelle
**Signal :** AnswerThePublic révèle 3 questions inédites sur « expertise médicale Allianz refus consolidation ».
**Action immédiate possible :** noter pour FAQ à venir.
**Valeur ajoutée :** détection d'un litige sectoriel spécifique sous-couvert.

### Exemple 4 — Tendance saisonnière sous-exploitée
**Signal :** Trends montre que « refus AEEH rentrée scolaire » double chaque août.
**Action immédiate possible :** planifier 2 articles à publier mi-juillet (post-gel).
**Valeur ajoutée :** calendrier éditorial pré-construit.

### Exemple 5 — Nouvelle réglementation à l'horizon
**Signal :** Légifrance signale décret modifiant le tableau MP n° 57 publication imminente.
**Action immédiate possible :** brouillon préparé pour publication J+1 après JO.
**Valeur ajoutée :** réactivité instantanée vs concurrence.

### Exemple 6 — Litige sectoriel pic
**Signal :** Argus publie un dossier sur l'augmentation des contestations Axa post-Covid.
**Action immédiate possible :** noter le sujet, dérouler en cluster potentiel.
**Valeur ajoutée :** opportunité B2B (avocats AXA-related).

---

# PARTIE 5 — Critères de réussite mesurables

## 5.1 Indicateurs quantitatifs (chiffres durs)

| KPI | Cible minimum (M+30) | Source |
|---|---|---|
| Signaux capturés | ≥ 120 | Onglet Signaux bruts |
| Opportunités exploitables retenues | ≥ 6 | Onglet Opportunités |
| Opportunités jugées **inédites** | ≥ 3 | Onglet Croisement |
| Opportunités avec **antériorité MVP** > 7 jours | ≥ 2 | Onglet Croisement |
| Idées de contenu nouvelles formulées | ≥ 8 | Notion |
| Heures réelles passées au total | ≤ 14 h | Notion (à mesurer honnêtement) |
| Dépense réelle compte bancaire | ≤ 50 € | Banque |

## 5.2 Indicateurs qualitatifs (à répondre honnêtement)

À l'issue des 30 jours, dans Notion, écrire la réponse à 6 questions :

1. *« Le MVP m'a-t-il fait découvrir au moins 1 sujet sur lequel je n'aurais jamais pensé seul ? »*
2. *« Le MVP m'a-t-il fait gagner du temps sur ma veille existante, ou m'en a-t-il fait perdre ? »*
3. *« Y a-t-il au moins 1 opportunité que le MVP m'a fait voir avant qu'elle ne soit publiée par un concurrent ? »*
4. *« La classification ChatGPT m'a-t-elle apporté une vraie valeur ou simplement reformulé ce que j'avais déjà ? »*
5. *« Au bout de 30 jours, est-ce que j'ai envie de continuer cette routine ? »*
6. *« Si je devais déléguer ce travail à quelqu'un, comprendrait-il facilement la méthode ? »*

## 5.3 Indicateur clé inéluctable (s'il n'y est pas, c'est NO GO)

> **Au moins UNE opportunité concrète, datée, vérifiable, jugée inédite par vous-même, et que vous n'auriez raisonnablement pas trouvée par ailleurs en moins de 30 jours.**

Sans cela, le MVP est invalidé. Quelle que soit la quantité de signaux capturée.

---

# PARTIE 6 — Règle GO / NO GO (à appliquer strictement)

## 6.1 Critères cumulatifs

### 🟢 GO version Réaliste (passer au déploiement Phase 0-1 décrit dans démo opérationnelle)

**Tous les critères suivants doivent être satisfaits :**

| # | Critère | Seuil |
|---|---|---|
| G1 | Opportunités inédites détectées | ≥ 3 |
| G2 | Opportunités avec antériorité MVP > 7 jours | ≥ 2 |
| G3 | Au moins 1 sujet bloqueur révélé (j'ignorais qu'il existait) | ≥ 1 |
| G4 | Réponses qualitatives 1 et 3 (Partie 5.2) | OUI |
| G5 | Heures hebdo réelles | ≤ 4 h/sem soutenables |
| G6 | Sensation personnelle « routine soutenable » | OUI |
| G7 | Dépenses réelles à J+30 | ≤ 50 € |

### 🟡 GO sous conditions — Version Minimale uniquement (cf. Partie 7 démo opérationnelle)

**Si certains critères sont satisfaits mais pas tous :**

| Condition | Implication |
|---|---|
| G1 atteint mais pas G2 | Continuer en version minimale (1 asset/sem) sans investir |
| G3 atteint mais G5 dépassé | Réduire périmètre à 2 personas et retester 30 j |
| G7 dépassé (> 50 €) | Auditer pourquoi, ajuster avant scaling |

### 🔴 NO GO (arrêter purement et simplement)

**Si l'un des critères suivants tombe :**

| # | Critère | Seuil rouge |
|---|---|---|
| N1 | Opportunités inédites détectées | 0 |
| N2 | Opportunités avec antériorité > 7 jours | 0 |
| N3 | Réponse qualitative 1 (Partie 5.2) | NON |
| N4 | Réponse qualitative 2 (Partie 5.2) | « Perdu du temps » |
| N5 | Heures hebdo réelles | > 6 h/sem (non soutenable) |
| N6 | Sensation personnelle « routine soutenable » | NON |

**N'importe lequel de ces critères = NO GO automatique.**

Dans ce cas :
- Annuler ChatGPT Plus
- Archiver le tableau Sheets pour mémoire
- Réorienter l'effort vers les 3 chantiers prioritaires (Quick Wins, Cluster SEO, Simulateur AT)

## 6.2 La règle ultime

> Si à J+30 vous ne pouvez pas pointer **2 opportunités spécifiques, datées, et nommées** dont vous diriez avec sincérité *« Sans ce MVP, je serais passé à côté »* — alors la valeur n'est pas démontrée, peu importe les autres indicateurs.

---

# PARTIE 7 — Risques de faux positifs et faux négatifs

> *« L'erreur la plus dangereuse n'est pas l'échec du test. C'est de croire à un succès illusoire. »*

## 7.1 Biais qui peuvent fausser un GO (faux positifs)

### Biais #1 — Biais de confirmation
**Mécanisme :** vous voulez que le MVP marche, donc vous valorisez ce que vous trouvez.
**Mitigation :** la règle « opportunité datée et nommée » force la rigueur. Et la question 1 qualitative ne se triche pas si vous y répondez honnêtement.

### Biais #2 — Reformulation déguisée en découverte
**Mécanisme :** le MVP vous donne un sujet que vous connaissiez déjà, mais formulé autrement, et vous le notez comme « inédit ».
**Mitigation :** l'onglet « Ma veille habituelle » tenu en parallèle DOIT être rempli **avant** de regarder le MVP chaque jour. Si vous trichez, vous trichez contre vous-même.

### Biais #3 — Volume trompeur
**Mécanisme :** 200 signaux capturés vous donnent l'impression de « beaucoup » alors que la valeur est dans la qualité, pas la quantité.
**Mitigation :** seul le nombre d'opportunités **inédites** compte, pas le volume brut.

### Biais #4 — Effet ChatGPT impressionnant
**Mécanisme :** la classification ChatGPT semble brillante, donc vous concluez que le système marche.
**Mitigation :** la question 4 qualitative interroge précisément cela.

### Biais #5 — Sunk cost (coût engagé)
**Mécanisme :** vous avez consacré 14 h sur 30 jours, vous voulez justifier ce temps.
**Mitigation :** la règle ultime (Partie 6.2) impose 2 opportunités spécifiques. Pas négociable.

## 7.2 Biais qui peuvent fausser un NO GO (faux négatifs)

### Biais #6 — Mauvais timing du test
**Mécanisme :** la fenêtre 30 jours peut tomber sur une période creuse (août, congés sectoriels).
**Mitigation :** ne pas lancer le test en plein août. **Idéalement septembre-novembre ou février-avril.**

### Biais #7 — Périmètre trop large
**Mécanisme :** 5 personas dilueraient le signal. Le MVP en a 3, c'est déjà la borne haute.
**Mitigation :** respecter strictement les 3 personas définis.

### Biais #8 — Sous-utilisation ChatGPT
**Mécanisme :** vous ne savez pas prompter, donc la classification est faible.
**Mitigation :** les prompts sont fournis tels quels dans ce document. À copier-coller sans modifier au moins lors de la première semaine.

### Biais #9 — Veille habituelle déjà excellente
**Mécanisme :** si votre veille personnelle est déjà de top niveau, le MVP ne peut rien ajouter.
**Mitigation :** c'est en soi un résultat précieux. Un NO GO légitime indique que votre veille est efficace et qu'il faut investir ailleurs.

## 7.3 Risques opérationnels du MVP lui-même

| Risque | Probabilité | Mitigation |
|---|---|---|
| Submersion par le volume Google Alerts | Élevée | Pré-configurer 15 alertes max + filtrer par persona |
| ChatGPT Plus mal utilisé | Moyenne | Prompts fournis textuels |
| Oubli d'annulation ChatGPT Plus | Élevée | Rappel calendrier J+28 |
| Tableau Sheets pas tenu à jour | Élevée | Discipline quotidienne 15 min |
| Comparaison veille habituelle non sincère | Élevée | Notion comme journal de bord honnête |
| Saisonnalité défavorable | Moyenne | Choisir la fenêtre de test hors août |

---

# 🎯 LIVRABLE FINAL — Réponses aux 4 questions impératives

## Question 1 — Quel est le coût réel du MVP ?

**Dépenses réelles sortant du compte bancaire sur 30 jours :**

| Poste | Montant |
|---|---|
| ChatGPT Plus (1 mois) | 20 € |
| Marge de sécurité éventuelle (rapport, doc) | 0–30 € |
| **Coût réel attendu** | **20 € (objectif), 50 € (plafond)** |

**À comparer avec :**
- Version Réaliste complète : 169 €/mois × 12 = 2 028 €/an + 525 € installation
- Différentiel d'investissement risqué évité : **plus de 2 500 €**

→ Le MVP coûte donc **moins de 1 % du coût d'un déploiement plein** pour valider le concept.

## Question 2 — Combien de temps cela me prendra chaque semaine ?

**Heures réelles attendues (mesure honnête, pas valorisation théorique) :**

| Semaine | Quotidien lundi-vendredi | Vendredi dédié | Total semaine |
|---|---|---|---|
| Semaine 1 | 5×20 min = 1 h 40 | 1 h | **2 h 40** |
| Semaine 2 | 5×20 min = 1 h 40 | 1 h 15 | **2 h 55** |
| Semaine 3 | 5×20 min = 1 h 40 | 1 h 30 | **3 h 10** |
| Semaine 4 | 5×20 min = 1 h 40 | 2 h 30 (bilan) | **4 h 10** |
| **Total 30 jours** | | | **≈ 13 h** |

Plus **2 h Jour 1** (installation) = **15 h cumulées sur 30 jours**.

À comparer avec une veille manuelle non structurée : la plupart des dirigeants la pratiquent **sans en mesurer le temps**. Vous mesurez ici pour la première fois.

## Question 3 — Quels résultats raisonnablement attendus à J+30 ?

**Plage réaliste, avec borne basse et borne haute :**

| Indicateur | Borne basse (déception) | Borne médiane (attendu) | Borne haute (réussite) |
|---|---|---|---|
| Signaux bruts capturés | 60 | 130 | 250 |
| Opportunités retenues | 2 | 6 | 12 |
| Opportunités inédites | 0 | 3 | 7 |
| Opportunités avec antériorité MVP > 7 j | 0 | 2 | 5 |
| Idées de contenu nouvelles | 4 | 10 | 20 |
| Verdict | 🔴 NO GO | 🟢 GO | 🟢 GO Ambitieux |

**Probabilités estimées :**
- Borne basse (NO GO) : 25 %
- Borne médiane (GO Réaliste) : 55 %
- Borne haute (GO Ambitieux) : 20 %

## Question 4 — À partir de quel résultat dois-je décider de construire une version plus avancée ?

**Règle stricte de bascule vers Phase 0 du déploiement complet :**

✅ **GO Phase 0 si — TOUS satisfaits :**
1. ≥ 3 opportunités inédites détectées sur 30 jours
2. ≥ 2 opportunités avec antériorité MVP > 7 jours
3. Au moins 1 « grosse découverte » que vous n'auriez objectivement pas vue ailleurs
4. Routine ressentie comme soutenable
5. Dépense réelle ≤ 50 €

🟡 **GO Version Minimale uniquement (sans investissement) si :**
- ≥ 2 opportunités inédites mais < 3
- Ou routine soutenable mais antériorité MVP faible
→ Continuer la même méthode manuelle au-delà des 30 jours, sans aucune montée en charge

🔴 **NO GO si :**
- 0 opportunité inédite OU
- Ressenti négatif (perte de temps, frustration) OU
- Réponse NON à la question qualitative #1
→ Arrêter, réinvestir l'effort sur Quick Wins CTR / Cluster SEO / Simulateur AT

**À ne JAMAIS faire :**
- Bascule directe vers la version Ambitieuse (42 k€/an) après le MVP
- Bascule sans avoir validé d'abord la Phase 0 (test 4-6 semaines décrit dans démo opérationnelle)

---

# 🔚 Synthèse exécutive du protocole MVP

| Élément | Valeur |
|---|---|
| Coût réel | **20 € (objectif) / 50 € (plafond) / 100 € (alerte rouge)** |
| Durée | **30 jours calendaires** |
| Temps réel | **≈ 15 h cumulées dirigeant** |
| Outils mobilisés | **9 outils, dont 8 gratuits** |
| Code écrit | **0 ligne** |
| Base de données | **0** |
| Automatisation | **0** |
| Personnes impliquées | **1 (vous)** |
| Risque financier max | **50 €** |
| Décision finale | **GO / GO Minimal / NO GO**, sur règles chiffrées |

**Vous saurez à J+30, avec moins de 50 € engagés et 15 h de travail, si l'Observatoire mérite ou non un investissement plus lourd.**

C'est exactement ce que demande votre méthode habituelle : décision chiffrée, défendable, réversible, sans gaspillage.

---

**FIN — `MVP_OBSERVATOIRE_PROTOCOLE_2026-06.md`**
**Protocole d'expérimentation — Compatible avec le gel éditorial en vigueur**
**Aucune mise en œuvre avant arbitrage explicite post-01/07/2026**
