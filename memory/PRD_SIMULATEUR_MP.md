# PRD — Simulateur Maladie Professionnelle (MP)

**Statut :** PRÉPARATION — NON DÉPLOYÉ — DRAFT — AUCUN DÉVELOPPEMENT EN COURS
**Date de rédaction :** 2026-05-30
**Auteur :** Mission de préparation S.E.S
**Périmètre :** Vague 1 Simulateurs (AT + MP)
**Route cible (à créer) :** `/simulateur-maladie-professionnelle`
**Décision GO/NO-GO :** subordonnée à la Checklist du 2026-06-16
**Dépend de :** PRD Simulateur AT (réutilise 80 % de la logique)

---

## 1. Contexte et raison d'être

### 1.1 Constat marché
Les requêtes MP captées dans l'export GSC sont nombreuses mais éclatées :
- `simulateur rente maladie professionnelle` (15 impr, pos 10,07, 0 clic)
- `calcul rente maladie professionnelle` (5 impr, pos 14,4, **1 clic** = signal d'intention forte)
- `calcul rente ipp maladie professionnelle` (8 impr, pos 17)
- `maladie professionnelle tableau 57 indemnisation` (4 impr, pos 54)

Au total : **35+ impressions/46j** spécifiquement MP, plus le déversement de la requête longue traîne sur `/calculatrice-ipp` (qui ne distingue pas MP).

### 1.2 Différenciation vs Simulateur AT

| Point | AT | MP |
|-------|----|----|
| **Reconnaissance** | Quasi-automatique (présomption d'imputabilité, déclaration sous 48h) | **Complexe** : tableau MP applicable + critères (présomption) OU hors tableau via CRRMP (Comité régional de reconnaissance des maladies professionnelles) |
| **Délai prescription** | 2 ans à compter de l'accident | 2 ans à compter de la cessation du travail ou de l'établissement du certificat médical |
| **Calcul rente** | Identique (CSS L.434-2) | **Identique** (mêmes formules) |
| **Spécificité** | Mécanisme accidentel, fait unique | Pathologie progressive, expositions pluriannuelles |
| **Tableau requis** | Non | Oui (115 tableaux régime général + tableaux régime agricole) |
| **Hors tableau** | N/A | Possible si IPP ≥ 25 % ou décès → CRRMP |

**Conséquence design** : le simulateur MP partage 100 % de la logique de calcul de rente avec le Simulateur AT, mais ajoute **deux étapes amont spécifiques** :
1. Détermination du tableau MP applicable (ou bascule vers CRRMP).
2. Pré-validation des critères de reconnaissance (présomption d'origine ou critères CRRMP).

### 1.3 Positionnement vs `/guide/comment-faire-reconnaitre-maladie-professionnelle` (page existante)
- La page guide explique **comment** faire reconnaître une MP.
- Le simulateur MP chiffre **combien** vous toucheriez si la MP est reconnue.
- Complémentaires : maillage croisé fort.

### 1.4 Objectifs business
- **Acquisition SEO** : capter le longue traîne MP qui ne convertit pas aujourd'hui.
- **Conversion vers `/dossier-express`** : les MP refusées (taux de refus CPAM ~30 %) = segment à forte propension à payer.
- **Réutilisation maximale** du code AT (formules identiques) → coût de dev divisé par 2 vs développement isolé.

---

## 2. Profils utilisateurs (Personas)

### Persona 1 — « Le malade en cours de constitution de dossier » (50 %)
- Pathologie progressive (lombalgie, troubles musculo-squelettiques, surdité, asthme professionnel).
- Vient de découvrir l'existence de la procédure MP.
- Cherche à savoir combien il pourrait toucher → motivation pour entamer les démarches.
- Niveau juridique : faible.

### Persona 2 — « Le débouté de la CPAM (refus de reconnaissance) » (25 %)
- A déposé une demande, a reçu un refus.
- Cherche un calcul pour décider si la contestation vaut le coup.
- Niveau juridique : moyen (a déjà ferraillé avec la CPAM).
- Forte propension à payer un service (`/dossier-express`).

### Persona 3 — « Le candidat CRRMP » (15 %)
- A une pathologie hors tableau (ou tableau mais critères non remplis).
- Cherche à savoir si l'IPP estimée ≥ 25 % (seuil CRRMP).
- Niveau juridique : élevé, souvent accompagné d'un syndicat ou d'une association.

### Persona 4 — « Le conseiller / aidant / syndicaliste » (10 %)
- Aide un collègue.
- Cherche un outil de référence à partager.

---

## 3. Cahier des charges fonctionnel

### 3.1 Architecture de la page

```
[HERO — Simulateur Maladie Professionnelle : calculer ma rente MP]
[Bloc d'introduction (3 lignes)]

[ÉTAPE A — Reconnaissance MP]
  Question 1 : Votre pathologie est-elle dans un tableau MP ?
    → Oui  → Étape A.1 : Sélection du tableau (autocomplete)
    → Non  → Étape A.2 : Pré-évaluation CRRMP (3 questions)
    → Inconnu → Aide à la détermination (lien vers /guide/maladie-professionnelle-definition-droits)

[ÉTAPE B — Calcul de la rente]
  (Identique au Simulateur AT à partir d'ici)
  Q1 : Salaire annuel net 12 mois précédents
  Q2 : Taux IPP fixé (ou estimation)
  Q3 : Statut dossier
  Q4 : Faute inexcusable suspectée ?
  Q5 (opt) : Email pour PDF

[Bouton "Calculer ma rente MP"]

[RÉSULTATS]
  - Statut reconnaissance estimé (tableau / CRRMP / refusé probable)
  - Rente trimestrielle / annuelle (formule CSS L.434-2)
  - Indemnisation complémentaire si faute inexcusable
  - Comparatif scénarios (refus vs reconnaissance vs faute inex.)

[CTA → /dossier-express]
[Disclaimer + SEO + Maillage]
```

### 3.2 Étape A.1 — Sélection du tableau MP

**Données nécessaires :**
- Liste complète des 115 tableaux MP (régime général) + tableaux régime agricole.
- Pour chaque tableau : numéro, intitulé, pathologies couvertes, délai de prise en charge, expositions retenues.

**Source des données :**
- `frontend/src/data/maladiesProfessionnelles.js` (déjà existant dans le code projet, à confirmer).
- Compléter avec liste officielle Ameli (mise à jour 2026).

**UX :**
- Input autocomplete avec recherche par pathologie OU par numéro de tableau.
- Affichage à la sélection : « ✅ Tableau N°XX — [nom] — Délai de prise en charge : X mois — Expositions retenues : [liste] ».

**Validation des critères du tableau** (3 questions auto-générées) :
1. Votre pathologie correspond-elle à la liste exacte du tableau ? (Oui/Non/Inconnu)
2. Avez-vous été exposé(e) selon les conditions du tableau ? (Oui/Non)
3. Le délai entre la fin d'exposition et la première constatation est-il respecté ? (Oui/Non/Inconnu)

**Résultat de l'étape A.1 :**
- 3 « Oui » → ✅ Présomption d'origine acquise → tableau applicable.
- 1 ou 2 « Non » → ⚠️ Le tableau ne s'applique pas dans sa forme actuelle → bascule sur Étape A.2 CRRMP.

### 3.3 Étape A.2 — Pré-évaluation CRRMP

**Base légale :** CSS L.461-1 alinéa 4 (hors tableau si IPP ≥ 25 % ou décès) et alinéa 3 (tableau avec critères partiels via CRRMP).

**Questions (3 cumulatives) :**

1. **IPP attendue ≥ 25 % ?** (Saisie d'estimation)
   - Si Oui → CRRMP saisissable (cas alinéa 4).
   - Si Non et tableau partiel applicable → CRRMP via alinéa 3.
   - Si Non et pas de tableau → ❌ Non recevable.

2. **Lien direct et essentiel avec le travail (preuve médicale) ?** (Oui/Non/À documenter)

3. **Avez-vous une expertise médicale ou un rapport médical établissant ce lien ?** (Oui/En cours/Non)

**Résultat de l'étape A.2 :**
- 3 réponses positives → ✅ Dossier CRRMP recevable, calcul de rente affiché.
- 1 ou 2 réponses négatives → ⚠️ Probabilité faible mais simulateur affiche quand même la rente théorique avec disclaimer « SI reconnaissance ».

### 3.4 Étape B — Calcul de la rente (identique AT)

**Voir PRD Simulateur AT §3.2 et §4.** Mêmes formules :
- `taux_utile = if IPP<50: IPP/2 else 25+(IPP-50)`
- `rente_annuelle = SAR_plafonné × taux_utile`
- Capital pour IPP < 10 %
- Majoration faute inexcusable +100 % + indemnisation complémentaire

### 3.5 Spécificités MP additionnelles

#### A. Date de référence pour le SAR
- **AT** : 12 mois précédant l'accident (date unique).
- **MP** : 12 mois précédant la **première constatation médicale** OU 12 mois précédant la cessation du travail si la maladie a entraîné un arrêt → règle CSS L.434-15.

Le simulateur doit poser la question : « Quelle est la date de première constatation médicale (= date du certificat médical initial) ? »

#### B. Date d'effet de la rente
- Date de consolidation médicale fixée par le médecin conseil après expertise.
- Le simulateur affiche : « Date d'effet estimée : à la consolidation médicale (variable, généralement 6-24 mois après la première constatation). »

#### C. Délais de procédure
- Déclaration sous 15 jours après la première constatation.
- Instruction CPAM : 3 mois (renouvelables 3 mois).
- Si la CPAM ne se prononce pas → reconnaissance implicite.
- Le simulateur affiche un timeline visuel : Constatation → Déclaration → Instruction CPAM (3-6 mois) → Décision.

---

## 4. Algorithmes de calcul

### 4.1 Calcul de la rente MP
**Identique au Simulateur AT** (CSS L.434-2). Voir PRD AT §4.1.

### 4.2 Logique de reconnaissance (pseudo-code)

```
function evaluateReconnaissance(input) {
  const { tableau, critereTableauOK, ippEstimee, lienEssentiel, expertise } = input;
  
  // Cas A : Tableau MP avec critères remplis → présomption d'origine
  if (tableau && critereTableauOK === 'ALL_YES') {
    return {
      statut: 'TABLEAU_PRESOMPTION',
      probabilite: 'élevée',
      voie: 'CPAM directe',
      message: 'Présomption d'origine acquise (CSS L.461-1 al.2). Reconnaissance probable.'
    };
  }
  
  // Cas B : Tableau MP avec critères partiels → CRRMP alinéa 3
  if (tableau && critereTableauOK === 'PARTIAL') {
    return {
      statut: 'CRRMP_AL3',
      probabilite: 'moyenne',
      voie: 'CPAM puis CRRMP',
      message: 'Reconnaissance possible via CRRMP si lien direct prouvé (CSS L.461-1 al.3).'
    };
  }
  
  // Cas C : Hors tableau, IPP ≥ 25 % → CRRMP alinéa 4
  if (!tableau && ippEstimee >= 25 && lienEssentiel === 'OUI') {
    return {
      statut: 'CRRMP_AL4',
      probabilite: 'faible-moyenne',
      voie: 'CPAM puis CRRMP',
      message: 'Reconnaissance possible via CRRMP si lien direct et essentiel prouvé (CSS L.461-1 al.4).'
    };
  }
  
  // Cas D : Hors tableau, IPP < 25 % → non recevable
  if (!tableau && ippEstimee < 25) {
    return {
      statut: 'NON_RECEVABLE',
      probabilite: 'nulle',
      voie: 'Aucune',
      message: 'Pathologie hors tableau avec IPP < 25 % : non éligible CRRMP. Vérifiez si un tableau MP s'applique.'
    };
  }
  
  // Cas par défaut : incertain
  return {
    statut: 'INCERTAIN',
    probabilite: 'à évaluer',
    voie: 'Conseil personnalisé recommandé',
    message: 'Votre situation nécessite une analyse personnalisée. Consultez notre service.'
  };
}
```

### 4.3 Calcul du préjudice total (résultat composite)

```
function calculatePrejudiceTotal(input, reconnaissance) {
  const renteAnnuelle = calculateRenteAnnuelle(input.SAR, input.IPP);
  const ans = 20; // horizon viager moyen (à affiner selon âge)
  
  const renteCpamTotal = renteAnnuelle * ans;
  
  let fauteInexTotal = 0;
  if (input.fauteInexSuspectee === 'OUI') {
    const renteMajoree = renteAnnuelle * 2;
    const indemniteComplementaire = estimateIndemniteComplementaire(input.IPP);
    fauteInexTotal = renteMajoree * ans + indemniteComplementaire;
  }
  
  return {
    rentecpam20ans: renteCpamTotal,
    avecFauteInex20ans: fauteInexTotal || null,
    rentMensuelle: renteAnnuelle / 12,
    probabiliteReconnaissance: reconnaissance.probabilite
  };
}
```

---

## 5. Résultats à afficher

### 5.1 Bloc principal — Statut reconnaissance + rente

```
┌─────────────────────────────────────────────────────────┐
│  📋 Votre situation                                      │
│                                                         │
│  Tableau MP n°57 — Affections périarticulaires          │
│  ✅ Présomption d'origine acquise                        │
│  → Voie : reconnaissance directe par la CPAM             │
│                                                         │
│  💰 Rente MP estimée                                     │
│  Trimestrielle : 1 250 €                                │
│  Annuelle :     5 000 €                                 │
│  Sur 20 ans :   100 000 €                               │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Bloc comparatif — Scénarios

```
┌────────────────────┬──────────────┬─────────────────┬─────────────────┐
│                    │ Refus CPAM   │ Reconnaissance  │ + Faute inex.   │
├────────────────────┼──────────────┼─────────────────┼─────────────────┤
│ Rente annuelle     │      0 €     │     5 000 €     │   10 000 €      │
│ Indemnité complém. │      0 €     │        —        │   ~ 25 000 €    │
│ TOTAL sur 20 ans   │      0 €     │   100 000 €     │  225 000 €      │
└────────────────────┴──────────────┴─────────────────┴─────────────────┘

→ La marge entre "refus" et "reconnaissance" justifie pleinement
   la contestation si la CPAM refuse votre dossier.
```

### 5.3 Bloc timeline procédure (spécifique MP)

```
Constatation médicale (J0)
        │
        ▼ (sous 15 jours)
Déclaration CPAM
        │
        ▼ (instruction 3-6 mois)
Décision CPAM
        │
   ┌────┴────┐
   ▼         ▼
Accord    Refus → 2 mois pour contester (RAPO)
```

### 5.4 Bloc CTA conversion

```
🎯 Votre situation : présomption acquise, préjudice estimé 100 000 € sur 20 ans.

   → Faites analyser votre dossier MP pour maximiser la reconnaissance
     et identifier une éventuelle faute inexcusable
   [Bouton : Dossier Express IA — 49 €]
```

---

## 6. Limites juridiques et médicales

### 6.1 Disclaimer général
> ⚠️ **Estimation indicative.** Ce simulateur estime votre rente théorique SI la maladie professionnelle est reconnue. La reconnaissance dépend de l'instruction CPAM et, le cas échéant, de l'avis du CRRMP. Aucun engagement juridique.

### 6.2 Disclaimer sur le tableau MP
> ⚠️ **Les tableaux MP évoluent.** Cette liste est à jour au 2026-04-01. Si votre pathologie n'apparaît pas, elle peut faire l'objet d'une reconnaissance hors tableau si l'IPP ≥ 25 % (CSS L.461-1 al.4).

### 6.3 Disclaimer CRRMP
> ⚠️ **Le CRRMP est un avis consultatif.** La décision finale revient à la CPAM. Le taux de reconnaissance via CRRMP varie de 30 à 60 % selon les pathologies et la qualité du dossier.

### 6.4 Disclaimer médical
> ⚠️ **Seul le médecin conseil de la CPAM fixe le taux d'IPP final.** L'estimation que vous saisissez doit s'appuyer sur l'avis de votre médecin ou d'un médecin expert.

### 6.5 Spécificités hors scope V1
- **Maladies professionnelles agricoles** : régime MSA, formules très similaires mais barèmes distincts → V2.
- **Régime des fonctionnaires** : maladie imputable au service, procédure CITIS → V2.
- **Pathologies psychiques (burn-out)** : reconnaissance hors tableau quasi-systématique via CRRMP, IPP variable → traitement standard.
- **Cancers professionnels** : MP graves, indemnisation FIVA possible (amiante) → mention + lien externe vers FIVA, pas de calcul spécifique.

---

## 7. Architecture technique

### 7.1 Stack (identique AT)
- **Route** : `/simulateur-maladie-professionnelle`
- **Composant** : `frontend/src/pages/SimulateurMPPage.jsx`
- **Sous-composants partagés avec AT** :
  - `<RenteCalculatorEngine />` (formules CSS L.434-2 — **mutualisé**)
  - `<FauteInexcusableEstimator />` (mutualisé)
  - `<ResultPdfButton />` (mutualisé)
- **Sous-composants spécifiques MP** :
  - `<TableauMpSelector />` (autocomplete sur 115+ tableaux)
  - `<CrrmpPreCheck />` (questionnaire 3 questions)
  - `<RecognitionStatusBadge />` (statut reconnaissance + voie)

### 7.2 Données nécessaires (à versionner)
```javascript
// /app/frontend/src/data/baremes/mp_2026.js
export const MP_2026 = {
  version: '2026-04-01',
  validUntil: '2027-03-31',
  tableauxRegimeGeneral: [
    { numero: 1, nom: 'Plomb et ses composés', pathologies: [...], delaiPriseEnCharge: 30, ... },
    { numero: 4, nom: 'Hémopathies provoquées par le benzène', ... },
    { numero: 30, nom: 'Affections professionnelles consécutives à l'inhalation de poussières d'amiante', ... },
    { numero: 57, nom: 'Affections périarticulaires (TMS)', ... },
    { numero: 79, nom: 'Lésions chroniques du ménisque', ... },
    { numero: 97, nom: 'Affections chroniques du rachis lombaire — manutention manuelle', ... },
    { numero: 98, nom: 'Affections chroniques du rachis lombaire — vibrations', ... },
    // ... 115 tableaux régime général
  ],
  tableauxRegimeAgricole: [ ... ],  // 65+ tableaux MSA
  seuilCrrmp: 25,
  // Réutilisation des constantes de calcul depuis AT_2026
};
```

### 7.3 Backend
- Endpoint `POST /api/simulateur-mp/send-pdf` (similaire à AT).
- Endpoint `GET /api/simulateur-mp/tableaux/{numero}` : retourne le détail d'un tableau (cache 24h).
- Analytics : `simulateur_mp_events` collection MongoDB.

### 7.4 Réutilisation maximale
- **70 % du code** est partagé avec Simulateur AT (formules de calcul, composants UI rente, génération PDF).
- **30 % spécifique** : pré-étape reconnaissance (tableaux + CRRMP), spécificités timeline MP.
- Conséquence : si AT est développé d'abord, MP coûte 5 j de dev au lieu de 10 j.

---

## 8. UX / UI

### 8.1 Spécificité MP : étape de reconnaissance en amont
- Bandeau pédagogique en haut : « MP = maladie causée par votre travail. La reconnaissance nécessite soit un tableau MP, soit un avis CRRMP. Ce simulateur évalue les 2 voies. »
- Toggle clair entre « J'ai un tableau MP » et « Hors tableau / je ne sais pas ».

### 8.2 Recherche de tableau MP
- Autocomplete avec recherche fuzzy par mot-clé (« lombaire », « ménisque », « TMS », « épaule », « amiante », « surdité »).
- Affichage des tableaux les plus fréquents en premier (57, 97, 98, 30, 25, 42).
- Lien « Je ne trouve pas mon tableau » → bascule sur Étape A.2 (CRRMP).

### 8.3 Affichage du statut
- Badge couleur :
  - 🟢 `TABLEAU_PRESOMPTION` (vert : élevée)
  - 🟡 `CRRMP_AL3` ou `CRRMP_AL4` (orange : moyenne)
  - 🔴 `NON_RECEVABLE` (rouge : non éligible avec recommandation)
  - ⚪ `INCERTAIN` (gris : analyse personnalisée)

---

## 9. SEO On-page

### 9.1 Métadonnées
- **Title** : `Simulateur maladie professionnelle : rente, tableau, CRRMP` (58 chars)
- **Meta** : `Calculez votre rente MP selon votre salaire et taux d'IPP. Tableau MP applicable, CRRMP, faute inexcusable. Estimation chiffrée et démarches.` (146 chars)
- **Canonical** : `https://strategie-expertise-sante.fr/simulateur-maladie-professionnelle`
- **H1** : `Simulateur Maladie Professionnelle : calculer votre rente MP`

### 9.2 Schema.org
- `WebApplication` (calculator)
- `FAQPage` (8 questions, incluant CRRMP, tableaux, délais)
- `HowTo` (étapes de simulation)
- `BreadcrumbList`

### 9.3 Contenu SEO (~1000 mots sous le simulateur)
- Section « Tableau MP : présomption d'origine »
- Section « CRRMP : la voie hors tableau »
- Section « Calcul de la rente MP »
- Section « Cas particuliers » (TMS, surdité, amiante, lombalgies, pathologies psychiques)
- FAQ (8 questions)
- Maillage interne :
  - `/guide/comment-faire-reconnaitre-maladie-professionnelle`
  - `/guide/maladie-professionnelle-definition-droits`
  - `/guide/refus-maladie-professionnelle-cpam-recours`
  - `/guide/faute-inexcusable-employeur`
  - `/simulateur-accident-travail` (croisement AT/MP)
  - `/expertise-medicale` (POST 16/06 si GO)
  - `/dossier-express` (CTA)

---

## 10. Risques et mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Liste des 115 tableaux incomplète ou obsolète | Moyenne | **CRITIQUE** | Validation avec source officielle Ameli + processus de mise à jour annuel + affichage de la version. |
| Erreur dans la logique de reconnaissance (présomption vs CRRMP) | Moyenne | Élevé | Validation par juriste S.E.S avant publication. Tests unitaires : 30+ scénarios cumulatifs. |
| Promesse non tenue (rente affichée mais reconnaissance refusée) | Élevée (refus CPAM ~30 %) | **JURIDIQUE** | Disclaimer en gras à chaque étape : « rente SI reconnaissance ». Affichage du % de refus statistique par catégorie de MP. |
| Charge SEO ambiguë avec `/calculatrice-ipp` | Faible | Moyen | Maillage explicite : « Calcul IPP : voir /calculatrice-ipp ; Calcul rente MP : ici ». |
| Cas hors scope mal traités (fonctionnaires, marins, FIVA) | Moyenne | Moyen | Disclaimers explicites + redirection vers ressources externes (FIVA pour amiante, CITIS pour fonctionnaires). |
| Performance (115 tableaux à charger) | Faible | Faible | Lazy-loading du JSON des tableaux + index local pour recherche fuzzy. < 100 ms. |
| Stigmatisation des MP psychiques (burn-out) | Élevée (sensibilité) | Élevé | Section dédiée explicite « Pathologies psychiques : la voie CRRMP est possible avec rapport médical étayé ». Ton respectueux, non-décourageant. |

---

## 11. Estimation de charge

| Phase | Charge (jours-homme) |
|-------|----------------------|
| Spécifications | 0 (ce PRD) |
| Constitution / vérification de la base des 115 tableaux MP | 3 j |
| Validation juridique des formules + logique CRRMP | 2 j |
| Développement frontend (form + selector tableaux + result) | 5 j (réutilise 70 % du code AT si AT existe déjà) |
| Développement backend | 1 j |
| Tests unitaires (formules + logique reconnaissance) | 2 j |
| Tests E2E | 0,5 j |
| SEO on-page (1000 mots + 8 FAQ) | 1,5 j |
| QA + déploiement | 0,5 j |
| **TOTAL (si AT déjà déployé)** | **~15,5 jours-homme** |
| **TOTAL (si AT et MP en parallèle)** | **~22 jours-homme** (mutualisation max) |

**Recommandation :** développer AT en premier (PRD AT), puis MP après stabilisation et premières métriques AT.

---

## 12. Critères de succès

### 12.1 Métriques techniques (semaine 1)
- Recherche de tableau : temps de réponse < 200 ms
- Taux de complétion form ≥ 35 % (légèrement inférieur à AT car parcours plus long)
- 0 erreur Sentry critique

### 12.2 Métriques SEO (mois 1-3)
- Indexation Google ≤ 7 jours
- Position moyenne ≤ 15 sur « simulateur maladie professionnelle »
- ≥ 80 impressions / mois sur les requêtes ciblées

### 12.3 Métriques business (mois 2-3)
- Conversion simulateur → `/dossier-express` ≥ 3 % (supérieur à AT car cible plus convertissante)
- Téléchargement PDF ≥ 18 % des complétions
- Trafic mensuel ≥ 250 visites uniques à J+90

---

## 13. Périmètre exclu (V1)

- **Régime MSA (agricole)** : formules très similaires mais barème distinct → V2.
- **Régime fonctionnaire (CITIS)** : procédure différente → V2.
- **Pathologies amiante** : redirection vers FIVA.
- **Calcul du préjudice complet selon nomenclature Dintilhac** : trop complexe → traité dans `/dossier-express` premium.
- **Multi-MP cumulées** : 1 MP par simulation V1.
- **Maladies à effet différé** (cancers professionnels avec délai > 30 ans) : mention + disclaimer.

---

## 14. Dépendances et préalables

- ✅ Composant `<SEO />` disponible.
- ✅ `safeSessionStorage` migré.
- ✅ Backend Resend opérationnel.
- ⏳ **Constitution de la base des tableaux MP** (3 j) — peut commencer en parallèle des PRD AT.
- ⏳ **Validation juridique de la logique de reconnaissance** par juriste S.E.S.
- ⏳ **Recommandation : développer AT en premier**, valider le pattern UI, puis dupliquer pour MP en mutualisant.

---

## 15. Décision GO/NO-GO

**Préalable :** GO du Simulateur AT déjà accordé et stabilisé OU GO conjoint avec mutualisation forte.

**Critères GO** (cumulatifs) :
- ✅ /expertise-medicale stable post-observation
- ✅ Base des 115 tableaux MP constituée et validée
- ✅ Validation juridique CRRMP obtenue
- ✅ Capacité dev disponible

**Critères NO-GO** :
- ❌ Base des tableaux MP incomplète
- ❌ Risque consumériste mal maîtrisé sur la logique de reconnaissance
- ❌ /expertise-medicale en chute (priorité = remédiation)

---

**FIN DU PRD — Simulateur Maladie Professionnelle**
**Statut final : NON DÉPLOYÉ — DRAFT — EN ATTENTE DE GO 2026-06-16**
