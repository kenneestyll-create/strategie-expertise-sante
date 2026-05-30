# PRD — Simulateur Accident du Travail (AT)

**Statut :** PRÉPARATION — NON DÉPLOYÉ — DRAFT — AUCUN DÉVELOPPEMENT EN COURS
**Date de rédaction :** 2026-05-30
**Auteur :** Mission de préparation S.E.S
**Périmètre :** Vague 1 Simulateurs (AT + MP)
**Route cible (à créer) :** `/simulateur-accident-travail`
**Décision GO/NO-GO :** subordonnée à la Checklist du 2026-06-16

---

## 1. Contexte et raison d'être

### 1.1 Constat marché
La requête `simulateur calcul ipp accident de travail` génère **294 impressions** sur 46 jours (export GSC), avec une position moyenne de 6,7 et un CTR de 2,38 %. La requête voisine `simulateur rente accident du travail` cumule 97 impressions (pos 9,75). Au total, **400+ impressions/46j non capturées** par S.E.S sur ce segment (la `/calculatrice-ipp` actuelle ne couvre que le taux IPP générique, sans contextualisation AT).

### 1.2 Positionnement vs `/calculatrice-ipp` existante
- `/calculatrice-ipp` = calcul du **taux d'incapacité permanente partielle** à partir d'un barème (générique, ne distingue ni AT ni MP ni accident de droit commun).
- `/simulateur-accident-travail` = calcul de la **rente AT** (en fonction du salaire annuel + taux IPP) avec spécificités CPAM : abattement 50 % sur la portion 0-50 % d'IPP, capital représentatif < 10 %, intégration faute inexcusable, comparatif avec/sans rente. **Complémentaire**, pas redondant.

### 1.3 Objectifs business
- **Acquisition SEO** : capter les 400+ impressions/46j (~260/mois) sur les requêtes « rente AT » / « simulateur AT ».
- **Conversion** : funnel direct vers `/dossier-express` pour les cas avec faute inexcusable ou taux IPP contestable.
- **Différenciation** : aucun concurrent francophone n'offre un simulateur AT chiffrant **à la fois** la rente CPAM **et** la majoration faute inexcusable.

---

## 2. Profils utilisateurs (Personas)

### Persona 1 — « Le victime AT récente » (60 % du trafic estimé)
- Vient d'avoir un AT, est en arrêt, attend la consolidation.
- Cherche à anticiper combien il touchera après consolidation.
- Niveau de connaissance juridique : faible.
- Besoin : calcul rapide, vulgarisation, sentiment d'orientation.
- Action attendue : sauvegarder la simulation, prendre RDV téléphonique ou dossier-express.

### Persona 2 — « Le consolidé qui doute du taux » (25 %)
- A reçu une notification CPAM avec taux IPP.
- Soupçonne que le taux est trop bas.
- Cherche à savoir ce qu'il toucherait avec un taux supérieur.
- Niveau juridique : moyen (a déjà lu sur le sujet).
- Besoin : comparatif scénarios (taux actuel vs taux contesté).
- Action attendue : conversion vers `/dossier-express` premium.

### Persona 3 — « Le syndicaliste / aidant » (10 %)
- Aide un collègue/proche.
- Cherche à valider une intuition financière.
- Niveau juridique : élevé.
- Besoin : précision, accès au détail du calcul, sources légales.
- Action attendue : partager l'URL, télécharger un PDF récap.

### Persona 4 — « L'avocat ou expert » (5 %)
- Utilise le simulateur pour une estimation rapide en consultation.
- Besoin : exhaustivité, mention claire des limites, références CSS.
- Action attendue : zéro conversion attendue, mais bénéfice de référence (backlinks naturels).

---

## 3. Cahier des charges fonctionnel

### 3.1 Architecture de la page

```
[HERO — Simulateur Accident du Travail : calculer ma rente]
[Bloc d'introduction pédagogique (3 lignes max)]
[Formulaire de saisie — multi-étapes, 1 question par écran sur mobile]
  Étape 1 : Salaire annuel net des 12 mois précédant l'AT
  Étape 2 : Taux d'IPP fixé (ou estimation si pas encore consolidé)
  Étape 3 : Situation (consolidé / en cours de consolidation / contestation)
  Étape 4 : Présomption de faute inexcusable (oui / non / je ne sais pas)
  Étape 5 (optionnelle) : Email pour recevoir un PDF récapitulatif
[Bouton "Calculer ma rente AT"]
[Bloc résultats — affichage dynamique]
  - Rente trimestrielle estimée
  - Capital représentatif (si IPP < 10 %)
  - Comparatif avec/sans faute inexcusable
  - Plafond annuel CPAM applicable
  - Date d'effet probable
[Bloc CTA → /dossier-express]
[Bloc disclaimer juridique]
[Section SEO contenu — explication de la formule, sources légales, FAQ Schema.org]
[Bloc maillage interne]
```

### 3.2 Données d'entrée (inputs utilisateur)

| Champ | Type | Obligatoire | Validation | Range autorisé |
|-------|------|-------------|------------|----------------|
| `salaire_annuel_net` | Number (€) | Oui | > 0, < 500 000 | 0 — 500 000 |
| `taux_ipp` | Number (%) | Oui | 0 — 100 | 0 — 100 |
| `statut_dossier` | Enum | Oui | `consolide` / `en_consolidation` / `contestation` | — |
| `presomption_faute_inexcusable` | Enum | Non (défaut : non) | `oui` / `non` / `inconnu` | — |
| `regime_assure` | Enum | Non (défaut : général) | `general` / `agricole` / `fonctionnaire` | — |
| `anciennete_emploi` | Enum | Non | `< 1 an` / `1-5 ans` / `5-10 ans` / `> 10 ans` | — (info marketing) |
| `email_pdf` | String | Non | Regex email | — |

### 3.3 Données dérivées (calculées en amont)

| Variable | Source | Formule |
|----------|--------|---------|
| `salaire_annuel_de_reference` (SAR) | Saisie utilisateur | `salaire_annuel_net` (déjà = base de calcul CSS L.434-15) |
| `taux_utile` | Calcul interne | `if taux_ipp < 50 : taux_ipp / 2` *(abattement 50 %)* `else : 25 + (taux_ipp - 50)` *(barème CSS L.434-2)* |
| `plafond_annuel_csar` | Constante 2026 | 175 968 € *(plafond annuel sécurité sociale 4×PASS — à mettre à jour annuellement)* |
| `sar_plafonne` | Calcul | `min(salaire_annuel_de_reference, plafond_annuel_csar)` |

---

## 4. Algorithmes de calcul (formules détaillées)

### 4.1 Rente Accident du Travail (cas standard : IPP ≥ 10 %)

**Base légale :** Code de la Sécurité Sociale, articles L.434-2 et L.434-15.

```
Taux utile = formule à 2 paliers :
  Si IPP < 50 % :  taux_utile = IPP / 2
  Si IPP ≥ 50 % :  taux_utile = 25 + (IPP − 50)

(Exemples :
  IPP = 20 % → taux_utile = 10 %
  IPP = 50 % → taux_utile = 25 %
  IPP = 75 % → taux_utile = 50 %
  IPP = 100 % → taux_utile = 75 %)

Rente annuelle brute = SAR_plafonné × Taux_utile

Rente trimestrielle = Rente_annuelle_brute / 4
Rente mensuelle (équivalent) = Rente_annuelle_brute / 12
```

**Plafond légal SAR (2026) :**
- Plafond bas (mini) : 19 558,80 € (1 × PASS plancher pour SAR)
- Plafond haut (8 × PASS pour la part de SAR > 1 × PASS) : ajustement à appliquer si SAR > 175 968 €.

**Cas spécifique : taux IPP entre 10 et 50 %**
- Possibilité d'option pour un **capital représentatif** au lieu de la rente (CSS L.434-1).
- Le simulateur doit afficher les **deux options** :
  - Option A : capital unique (calculé selon barème CPAM par âge et taux IPP).
  - Option B : rente trimestrielle viagère.
- Disclaimer : « Le choix capital vs rente est irréversible et dépend de l'espérance de vie, du projet personnel et de l'option fiscale. Consultez un conseiller. »

### 4.2 Rente Accident du Travail (IPP < 10 %)

**Base légale :** CSS L.434-1.

```
Pas de rente. Capital forfaitaire unique selon barème :
  IPP 1 %  →  ~ 442,32 €
  IPP 2 %  →  ~ 718,89 €
  IPP 3 %  →  ~ 1 050,29 €
  IPP 4 %  →  ~ 1 658,77 €
  IPP 5 %  →  ~ 2 099,03 €
  IPP 6 %  →  ~ 2 599,07 €
  IPP 7 %  →  ~ 3 154,80 €
  IPP 8 %  →  ~ 3 763,12 €
  IPP 9 %  →  ~ 4 423,79 €
  (Source : barème INDICATIF actualisé chaque 01/04 — à versionner dans le code)
```

**⚠️ Important :** ces montants évoluent au 1ᵉʳ avril chaque année. Le simulateur doit afficher la date du barème utilisé (« Barème 2026, valable jusqu'au 31/03/2027 »).

### 4.3 Majoration Faute Inexcusable

**Base légale :** CSS L.452-2 et jurisprudence (Cass. soc. 28 février 2002, « arrêts amiante »).

**Effet** : la rente AT est **majorée** d'un montant pouvant aller **jusqu'au plafond du SAR**, soit en pratique entre +50 % et +100 % de la rente initiale, fixé par le tribunal.

**Indemnisation complémentaire** : en plus de la rente majorée, indemnisation des préjudices personnels (souffrance physique/morale, préjudice esthétique, préjudice d'agrément, perte de chance de promotion professionnelle, déficit fonctionnel temporaire/permanent).

```
Hypothèse simulateur (estimation conservative) :
  Rente_avec_faute = Rente_AT × 2 (majoration max théorique)
  
  + Indemnisation complémentaire estimée :
    Souffrances endurées (forfait) : 5 000 € à 30 000 €
    Préjudice esthétique :          1 000 € à 15 000 €
    Préjudice d'agrément :           1 000 € à 10 000 €
    Préjudice fonctionnel permanent : taux IPP × point_DFP (~1 500 €/point) 
                                      = IPP × 1500 € en estimation
```

**Disclaimer obligatoire affiché** :
> « Ces montants d'indemnisation complémentaire sont des estimations indicatives basées sur la jurisprudence moyenne. Le montant final est fixé par le tribunal du pôle social en fonction des éléments médicaux et de la situation personnelle. »

### 4.4 Plafond de cumul (sécurité)

Le simulateur doit vérifier que `Rente + Indemnité_complémentaire ≤ Préjudice_total_évalué` pour éviter les promesses irréalistes.

### 4.5 Indexation et revalorisation

- La rente AT est revalorisée chaque 1ᵉʳ avril selon le coefficient publié par décret.
- Le simulateur affiche un avertissement : « Montant estimé au 1ᵉʳ avril 2026. Revalorisation annuelle au 1ᵉʳ avril. »

---

## 5. Résultats à afficher (output UX)

### 5.1 Bloc principal — Résultat synthétique

```
┌─────────────────────────────────────────────────┐
│  💰 Votre rente AT estimée                       │
│                                                 │
│  Trimestrielle : 1 250 €                        │
│  Annuelle :     5 000 €                         │
│  Mensuelle (équiv.) : 416,67 €                  │
│                                                 │
│  Base de calcul : SAR 35 000 € × taux utile 14% │
│  Plafond appliqué : non (SAR < plafond CSS)     │
│  Date d'effet probable : T+30 jours              │
└─────────────────────────────────────────────────┘
```

### 5.2 Bloc comparatif — Avec / sans faute inexcusable

```
┌──────────────────────┬────────────────┬─────────────────┐
│                      │ Rente CPAM seule│ Avec faute inex.│
├──────────────────────┼────────────────┼─────────────────┤
│ Rente annuelle       │   5 000 €      │   10 000 €      │
│ Indemnités complém.  │       —        │   ~ 25 000 €    │
│ TOTAL sur 10 ans     │  50 000 €      │  125 000 €      │
└──────────────────────┴────────────────┴─────────────────┘
🟠 Si vous suspectez une faute inexcusable, contactez-nous.
```

### 5.3 Bloc explicatif (collapsible)

- Comment est calculée ma rente ?
- Pourquoi le taux utile diffère du taux IPP ?
- Qu'est-ce que le SAR (Salaire Annuel de Référence) ?
- Cas particuliers (régime agricole, fonctionnaire, étudiant).

### 5.4 Bloc CTA conversion

```
🎯 Votre estimation suggère un préjudice supérieur à 50 000 €
   et une situation de faute inexcusable probable.

   → Analyse complète de votre dossier en 48h via Dossier Express IA
   [Bouton : Lancer mon analyse — 49 €]
```

### 5.5 Bloc "Mon récap PDF"

- Champ email + bouton « Recevoir le récap par email ».
- PDF généré avec QR code (cohérence avec Calculatrice IPP et StratégiIA existants).
- Source légale citée en bas de page.

---

## 6. Limites juridiques et médicales (disclaimers obligatoires)

### 6.1 Disclaimer général (affiché en permanence sous le résultat)
> ⚠️ **Estimation indicative.** Ce simulateur calcule une estimation basée sur les barèmes officiels au 2026-04-01 et la jurisprudence moyenne. Le montant définitif de votre rente est notifié par la CPAM après consolidation et fixation officielle du taux d'IPP. Aucun engagement juridique de la part de Stratégie & Expertise Santé.

### 6.2 Disclaimer médical
> ⚠️ **Le taux d'IPP saisi ici est celui notifié par la CPAM ou estimé.** Le taux réel est fixé par le médecin conseil après expertise médicale. Une contestation du taux est possible dans les 2 mois suivant la notification.

### 6.3 Disclaimer faute inexcusable
> ⚠️ **La faute inexcusable ne se déclare pas, elle se prouve.** Trois conditions cumulatives doivent être réunies devant le tribunal du pôle social (conscience du danger, mesures nécessaires non prises, lien causal). Ce simulateur estime ce que vous pourriez obtenir SI la faute est reconnue, sans préjuger de la décision judiciaire.

### 6.4 Limites du modèle
- **Pas applicable** : militaires, marins, certains régimes spéciaux (calculs distincts non couverts par le simulateur).
- **Approximations** : la revalorisation annuelle au 1ᵉʳ avril n'est pas projetée sur les années futures (montant en euros constants 2026).
- **Hors champ** : préjudice professionnel (perte de carrière), perte de chance de promotion, retraite (impact différé).

### 6.5 Conformité RGPD
- Aucune donnée personnelle stockée si l'utilisateur ne fournit pas son email.
- Si email fourni : consentement explicite RGPD, base légale = intérêt légitime (envoi PDF), durée de conservation 12 mois, droit à l'effacement (lien dans le PDF).
- Aucun cookie tiers, aucun pixel marketing dans le simulateur.

---

## 7. Architecture technique (high-level)

### 7.1 Stack
- **Frontend** : React, route `/simulateur-accident-travail` dans `App.js`.
- **Composant** : `frontend/src/pages/SimulateurATPage.jsx`.
- **Sous-composants** :
  - `<SimulateurATForm />` (multi-étapes, état dans `useReducer`)
  - `<SimulateurATResult />` (affichage dynamique)
  - `<SimulateurATPdfButton />` (génération jsPDF côté client + envoi via backend `/api/simulateur-at/send-pdf`)
- **Constantes** : `frontend/src/data/baremes/at_2026.js` (barème capital IPP < 10 %, plafond CSS, coefficients).
- **Hooks utilitaires** : `useRenteATCalculator()` pour isoler la logique mathématique.

### 7.2 Backend (optionnel mais recommandé)
- Endpoint `POST /api/simulateur-at/send-pdf` :
  - Reçoit les inputs anonymisés + email.
  - Génère le PDF (jsPDF côté backend ou ReportLab Python).
  - Envoie via Resend.
  - Log d'événement anonyme dans MongoDB pour analytics (`simulateur_at_events`).
- Endpoint `GET /api/simulateur-at/stats` (admin) : taux de complétion, conversion vers dossier-express.

### 7.3 Constantes 2026 à versionner
```javascript
// /app/frontend/src/data/baremes/at_2026.js
export const AT_2026 = {
  version: '2026-04-01',
  validUntil: '2027-03-31',
  pass2026: 43992,        // Plafond annuel sécurité sociale 2026
  sarPlafondHaut: 175968, // 4 × PASS
  capitalIppLow: {
    1: 442.32, 2: 718.89, 3: 1050.29, 4: 1658.77, 5: 2099.03,
    6: 2599.07, 7: 3154.80, 8: 3763.12, 9: 4423.79
  },
  // ...
};
```

### 7.4 Analytics & tracking
- Événements à tracker (Google Analytics + Sentry breadcrumb) :
  - `simulateur_at_start`
  - `simulateur_at_step_completed_{n}`
  - `simulateur_at_calculated` (avec hash anonyme des inputs)
  - `simulateur_at_cta_clicked`
  - `simulateur_at_pdf_requested`

---

## 8. UX / UI (recommandations)

### 8.1 Pattern multi-étapes
- 5 écrans, 1 question par écran sur mobile (< 768 px).
- Bouton « Suivant » désactivé tant que validation invalide.
- Progress bar `1/5 → 5/5`.
- Bouton « Revenir » accessible à tout moment.
- Sauvegarde automatique via `safeSessionStorage` (déjà disponible) pour reprise sur F5 — clé `simulateur_at_form`.

### 8.2 Affichage des montants
- Format français : `1 250,00 €` (espace insécable + virgule).
- Montants importants en bold, gros corps (text-3xl).
- Couleur or `#C7A14A` pour les montants principaux (cohérence charte S.E.S).

### 8.3 Accessibilité
- WCAG AA : contraste suffisant, labels visibles, navigation clavier, ARIA.
- `data-testid` sur tous les inputs et boutons interactifs (cohérence règles projet).

### 8.4 Mobile-first
- Le simulateur est utilisé majoritairement sur mobile (constat GSC : mobile 4,56 % CTR vs desktop 1,5 %).
- Bouton CTA collant en bas d'écran après le résultat.

---

## 9. SEO On-page

### 9.1 Métadonnées
- **Title** : `Simulateur rente accident du travail 2026 : calculer ma rente AT` (61 chars)
- **Meta** : `Calculez en 2 minutes votre rente AT selon votre salaire et votre taux d'IPP. Comparatif avec/sans faute inexcusable. Estimation chiffrée + PDF récap.` (152 chars)
- **Canonical** : `https://strategie-expertise-sante.fr/simulateur-accident-travail`
- **H1** : `Simulateur Accident du Travail : calculez votre rente`

### 9.2 Schema.org
- `WebApplication` (type calculator)
- `FAQPage` (6 questions clés)
- `HowTo` (étapes de la simulation)
- `BreadcrumbList` (Accueil > Outils > Simulateur AT)

### 9.3 Contenu SEO (sous le simulateur, ~800 mots)
- Section « Comment fonctionne le calcul de la rente AT »
- Section « Cas particuliers » (régime agricole, fonctionnaire, < 10 %)
- Section « Faute inexcusable : 3 conditions »
- FAQ (6 questions)
- Maillage interne :
  - vers `/calculatrice-ipp` (pour contester le taux)
  - vers `/guide/faute-inexcusable-employeur`
  - vers `/guide/rente-accident-travail-calcul-contestation`
  - vers `/expertise-medicale` (POST 16/06 si GO)
  - vers `/dossier-express` (CTA conversion)

---

## 10. Risques et mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Erreur de calcul (formule mal implémentée) | Moyenne | **CRITIQUE** | Tests unitaires : `frontend/src/data/baremes/__tests__/at_calculator.test.js` avec 20+ cas de figure validés contre exemples officiels (Ameli, CSS, jurisprudence). |
| Barème obsolète | Élevée (annuel) | Élevé | Constantes versionnées (`at_2026.js`), tâche cron J-1 du 1er avril pour rappeler la mise à jour. Affichage de la version dans le résultat. |
| Promesse de gain inatteignable | Faible | **JURIDIQUE** | Disclaimers en gras, sources légales citées (CSS articles), validation par juriste avant publication. |
| Utilisation pour conseil juridique | Faible | Élevé | Disclaimer explicite « Estimation, pas conseil ». Pas de recommandation personnalisée non-anonymisée. |
| Charge SEO sur `/calculatrice-ipp` (cannibalisation) | Faible | Moyen | Schema.org explicite + maillage clair entre les 2 outils. Les requêtes sont distinctes (« simulateur rente AT » ≠ « calculatrice IPP »). |
| Performance (calcul lent côté JS) | Faible | Faible | Calcul pur < 1 ms, aucun appel réseau requis pour la simulation. |
| Conformité RGPD (email) | Moyenne | Élevé | Consent box obligatoire avant envoi PDF, base légale documentée. |

---

## 11. Estimation de charge (dev + QA + SEO)

| Phase | Charge (jours-homme) | Détail |
|-------|----------------------|--------|
| Spécifications fonctionnelles | 0 (ce PRD) | Déjà réalisé |
| Validation juridique des formules | 2 j | Médecin-conseil S.E.S + juriste externe |
| Développement frontend | 5 j | Form + result + PDF + responsive |
| Développement backend (envoi PDF) | 1 j | Endpoint Resend + log MongoDB |
| Tests unitaires (formules) | 1 j | 20+ cas de figure |
| Tests E2E (testing_agent_v3_fork) | 0,5 j | Multi-écrans, mobile, edge cases |
| SEO on-page (contenu 800 mots) | 1 j | Rédaction + FAQ + Schema |
| QA finale + déploiement | 0,5 j | Smoke test + monitoring Sentry |
| **TOTAL** | **~11 jours-homme** | Si dev seul à plein temps : ~3 semaines |

---

## 12. Critères de succès (à mesurer après lancement)

### 12.1 Métriques techniques (semaine 1)
- Temps de chargement < 2 s sur mobile 4G
- Taux de complétion form ≥ 40 % (start → résultat affiché)
- 0 erreur Sentry critique
- Score Lighthouse ≥ 90 (performance, accessibilité, SEO)

### 12.2 Métriques SEO (mois 1)
- Indexation par Google ≤ 7 jours après publication
- Position moyenne ≤ 15 sur « simulateur rente AT »
- ≥ 50 impressions / mois sur les requêtes ciblées

### 12.3 Métriques business (mois 2-3)
- Conversion simulateur → `/dossier-express` ≥ 2 %
- Téléchargement PDF (email fourni) ≥ 15 % des complétions
- Trafic mensuel ≥ 200 visites uniques au bout de 90 jours

---

## 13. Périmètre exclu (out of scope V1)

- Simulation des revalorisations futures (montants en euros 2026 uniquement).
- Calcul de l'IPP à partir du barème médical (c'est le rôle de `/calculatrice-ipp`).
- Calcul du capital représentatif pour rachat de rente (cas marginal, complexité actuarielle).
- Régime des marins / militaires / fonctionnaires (V2 si demande).
- Comparatif avec assurance privée (hors scope).
- Multi-langue (FR uniquement V1).

---

## 14. Dépendances et préalables

- ✅ Composant `<SEO />` déjà disponible.
- ✅ `safeSessionStorage` déjà migré (sauvegarde form).
- ✅ Backend Resend opérationnel pour envoi PDF.
- ✅ Schema.org pattern déjà utilisé sur `/calculatrice-ipp`, `/calculatrice-aah`.
- ⏳ **Validation juridique des formules** (à programmer avec un juriste S.E.S avant développement).
- ⏳ **Mise à jour annuelle du barème** : process à formaliser (responsable, deadline 31 mars).

---

## 15. Décision GO/NO-GO subordonnée à la Checklist 2026-06-16

Voir `/app/memory/DECISION_CHECKLIST_2026-06-16.md` (à rédiger après les PRD).

**Critères GO préliminaires** :
- ✅ /expertise-medicale n'a pas subi de chute SEO durant l'observation
- ✅ La trajectoire globale du site est stable ou positive
- ✅ Aucune autre P0 urgente ne préempte les ressources dev
- ✅ Le barème 2026 est validé par un juriste

**Critères NO-GO préliminaires** :
- ❌ /expertise-medicale en chute (priorité = remédiation Phase 1 avant développement nouveau)
- ❌ Crise technique en cours (Sentry > 10 erreurs critiques)
- ❌ Validation juridique non obtenue

---

**FIN DU PRD — Simulateur Accident du Travail**
**Statut final : NON DÉPLOYÉ — DRAFT — EN ATTENTE DE GO 2026-06-16**
