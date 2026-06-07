# Opportunité SEO — Accidents du travail graves et mortels (étude préparatoire)

> **🚨 NON PUBLIÉ — DRAFT — DOCUMENT DE PRÉPARATION**
> Étude de marché et d'opportunité — aucune ligne de ce document n'est déployée.
> Aucune action ne sera engagée avant le 2026-06-16 et la validation explicite de l'utilisateur.

**Date de rédaction :** 2026-06-07
**Statut :** Étude préparatoire — décision à prendre après le 2026-06-16
**Sources :** Code source S.E.S (lecture passive), exports GSC 2026-05-30 et 2026-06-07, données publiques DARES / Ameli / INRS, comparables internes
**Limitation méthodologique majeure :** Aucun accès à SEMrush, Ahrefs, Google Keyword Planner. Les estimations de volume sont donc des **ordres de grandeur calibrés** par croisement de sources publiques, et non des mesures directes.

---

## 1. Avertissement éthique et méthodologique préalable

Le sujet « décès au travail » et « accident mortel » porte sur des situations **traumatiques** vécues par des familles endeuillées. Tout chantier sur ce thème doit respecter :

- **Tonalité grave et respectueuse** : aucune sensation, aucun marketing agressif, aucun pop-up exit-intent, aucune urgence artificielle.
- **Vocabulaire mesuré** : « décès du salarié » plutôt que « mort au travail », « accompagnement » plutôt que « obtenez la meilleure indemnisation ».
- **Disclaimer empathique** clairement affiché : la page n'est pas une plaidoirie commerciale mais un guide pratique d'information.
- **Pas de CTA « payant immédiat »** sur la première interaction : laisser l'utilisateur s'informer, lui donner de la valeur, et ne proposer un accompagnement payant qu'après plusieurs niveaux de lecture (≥ 2 scrolls, ou via un guide PDF gratuit).
- **Respect des règles de pratique commerciale loyale** : pas de chiffre inventé, sources juridiques systématiquement citées.

Cette contrainte éthique réduit potentiellement la conversion immédiate mais protège la réputation et la conformité légale (Code de la consommation art. L.121-1).

---

## 2. Cartographie du sujet et état actuel

### 2.1 État actuel du site S.E.S sur ce segment

| Source | Constat |
|---|---|
| Code source (`backend/seed_seo_pages.py` + pages React) | **Aucune page** ne traite spécifiquement du décès accident du travail, des ayants droit, du conjoint survivant, du capital décès AT/MP |
| GSC 2026-06-07 (28j) | **Aucune impression** captée sur les requêtes contenant `décès`, `mortel`, `conjoint`, `survivant`, `ayant droit`, `veuve`, `enquête inspection` |
| Maillage interne | `/guide/faute-inexcusable-employeur` mentionne le scénario décès en passant, sans page dédiée |

🟡 **Constat clair** : le site n'a **aucune présence SEO sur ce segment**. C'est à la fois un **manque** (opportunité non capitalisée) et une **opportunité de positionnement** (terrain neuf à structurer).

### 2.2 Réalité du marché (données publiques 2024-2025)

Source : DARES, Ameli, Assurance Maladie - Risques Professionnels, INRS.

| Donnée | Valeur (France, ordres de grandeur) |
|---|---|
| Décès suite à AT/MP par an (régime général) | **~ 700-800 décès** |
| Décès suite à AT (hors trajet) | ~ 550 / an |
| Accidents du travail graves (IPP ≥ 10 %) | ~ 30 000 / an |
| AT avec arrêt | ~ 600 000 / an |
| Maladies professionnelles reconnues | ~ 40 000 / an |
| Capital décès AT moyen versé | 12 × salaire mensuel moyen + frais funéraires plafonnés |
| Rente conjoint survivant | 40 % du salaire annuel défunt (60 % si > 55 ans ou invalide) |
| Rente orphelin | 25 % du salaire annuel par enfant (30 % à partir du 3ᵉ) |

**Volume des familles concernées chaque année** : ~ 700 conjoints survivants + ~ 1 000 orphelins + parents/ascendants = **~ 2 000 ayants droit potentiels / an** uniquement sur le périmètre décès. Si on inclut les AT graves (familles d'accidentés en état critique), le volume monte à **plusieurs dizaines de milliers**.

---

## 3. Étude des requêtes cibles

### 3.1 Estimation du volume mensuel France (méthode triangulation publique)

⚠️ **Estimations indicatives** établies en croisant : structure des requêtes longue traîne similaires sur le site (ex : `simulateur rente ipp` = 412 impr/28j), volumes connus sur des thèmes voisins, intuition basée sur le nombre de familles annuel.

| # | Requête cible | Volume mensuel estimé (FR) | Difficulté SEO | Concurrence dominante | Intention |
|---|---|---|---|---|---|
| 1 | `décès accident du travail` | 400-800 | Moyenne | Service-public, Ameli, INRS, cabinets avocats | Informationnel + démarches |
| 2 | `accident mortel au travail` | 200-400 | Faible-Moyenne | Presse + INRS + DARES | Informationnel large |
| 3 | `indemnisation famille accident du travail` | 200-400 | Moyenne | Cabinets avocats, Ameli | **Transactionnel** |
| 4 | `rente conjoint survivant accident du travail` | 150-300 | Faible | Ameli, Service-public | Démarche |
| 5 | `capital décès accident du travail` | 150-300 | Faible | Ameli, CPAM | Informationnel chiffré |
| 6 | `faute inexcusable décès salarié` | 100-200 | Moyenne | Cabinets avocats | **Transactionnel premium** |
| 7 | `droits du conjoint survivant accident travail` | 80-150 | Faible | Service-public | Démarche |
| 8 | `enquête inspection du travail accident grave` | 50-100 | Faible | Service-public, INRS | Procédural |
| 9 | `recours après décès accident du travail` | 50-100 | Moyenne | Cabinets avocats | **Transactionnel** |
| 10 | `ayant droit accident du travail mortel` | 30-80 | Faible | Ameli | Démarche |
| 11 | `démarches après décès au travail` | 80-150 | Faible | Service-public | Démarche |
| 12 | `prise en charge décès accident travail employeur` | 30-80 | Faible | INRS | B2B/préventif |
| 13 | `rente ayants droit décès AT calcul` | 30-80 | Faible | Ameli | Calcul |
| 14 | `procès faute inexcusable décès` | 30-80 | Moyenne | Cabinets avocats | Contentieux |
| 15 | `combien touche famille accident mortel travail` | 50-100 | Faible | Forums + cabinets | Recherche émotionnelle |

**Volume cumulé estimé : ~1 800 à 3 700 recherches mensuelles France** sur ce cluster. À titre de comparaison, le cluster « simulateur IPP » génère ~ 1 000 impressions / 28j sur le site actuel.

### 3.2 Validation par signaux indirects

| Signal indirect | Lecture |
|---|---|
| Présence forte de Service-public.fr et Ameli sur ces requêtes | Volume confirmé (Google n'amplifie ces sites que sur des requêtes substantielles) |
| Présence de cabinets d'avocats spécialisés (Sigma, Lexavoué, Maître Le Bot, etc.) | Le segment est **monétisable** (les avocats ne dépensent pas en SEO pour des requêtes sans valeur) |
| Forums (cdiscount-conso, jurifiable, expat-net) sur ces requêtes | Confirme le besoin d'information sociale + émotionnelle |
| Articles presse régionale (Ouest-France, La Voix du Nord) après chaque accident grave | Crée des pics ponctuels de recherche locale (peu exploitables en SEO permanent) |

### 3.3 SERP — Analyse qualitative du paysage concurrentiel

Sur les requêtes prime (`indemnisation famille accident du travail`, `faute inexcusable décès salarié`), la SERP française type contient typiquement :

```
1. Service-public.fr (généraliste, peu approfondi sur la stratégie)
2. Ameli.fr (institutionnel, sans dimension contentieuse)
3. Cabinet d'avocat #1 (transactionnel, mais souvent contenu thin)
4. Cabinet d'avocat #2 (contenu plus profond, mais orienté plaidoyer)
5. INRS.fr (préventif, pour les employeurs)
6. Forum (avis individuel, peu fiable)
7. Article presse régionale (non SEO permanent)
8. Cabinet d'avocat #3
9. Service-public.fr (autre page)
10. Légifrance ou texte juridique
```

🎯 **Lecture stratégique** : aucun acteur ne propose le positionnement S.E.S = **guide stratégique + outil de calcul + accompagnement pédagogique**. Le site peut s'insérer entre Service-public (trop institutionnel) et avocats (trop transactionnels) en occupant l'angle **« accompagnement stratégique des familles »**.

---

## 4. Potentiel business et conversion

### 4.1 Profil des visiteurs potentiels

| Persona | Maturité décisionnelle | Propension à payer |
|---|---|---|
| **Conjoint survivant (mois 1-3 post-décès)** | Très faible (sidération, démarches automatiques par CPAM) | Très faible |
| **Conjoint survivant (mois 3-12 post-décès)** | Émergente (commencent à comprendre les enjeux) | Moyenne |
| **Ayants droit en contentieux faute inexcusable** (an 1-2) | Élevée (cherchent expertise) | **Élevée** 🎯 |
| **Famille en cours d'enquête inspection** | Élevée | Moyenne |
| **Avocats / syndicats / associations** (aidants tiers) | Très élevée | Faible directement, mais prescription forte |

### 4.2 Conversion estimée

**Pessimiste** : 5 % du trafic capté contacte le service, dont 20 % deviennent client = **1 % conversion globale**.
**Réaliste** : 8 % contact, 30 % conversion = **2,4 % conversion globale**.
**Optimiste** : 12 % contact, 35 % conversion = **4,2 % conversion globale**.

**Hypothèse de ticket moyen** : le dossier « décès AT + faute inexcusable » est un dossier premium. Si le visiteur prend un Dossier Express IA (~49 €) **et qu'il bascule sur un accompagnement plus profond** (300-1 500 € sur des phases ultérieures), le **revenu annuel potentiel** se calcule comme suit :

| Scénario | Trafic capté/mois | Conversion | Clients/mois | Ticket moyen | Revenu mensuel | Revenu annuel |
|---|---|---|---|---|---|---|
| Pessimiste | 200 | 1 % | 2 | 49 € (Dossier Express simple) | ~100 € | ~1 200 € |
| Réaliste | 500 | 2,4 % | 12 | 80 € (mix express + premium) | ~960 € | **~11 500 €** |
| Optimiste | 900 | 4,2 % | 38 | 150 € (mix élevé en faute inexcusable) | ~5 700 € | **~68 000 €** |

🎯 **Lecture** : même dans le scénario réaliste, le **ROI annuel justifie 15-20 jours de développement** initial. Le scénario optimiste — atteignable si maillage et autorité E-E-A-T sont bien construits — peut dépasser le revenu du Simulateur IPP actuel.

### 4.3 Compatibilité avec Dossier Express et StratégiIA

| Outil | Compatibilité | Notes |
|---|---|---|
| **Dossier Express IA** | ✅ Forte | Analyser un dossier décès + faute inexcusable est exactement le service S.E.S. Adapter un sous-modèle "décès" |
| **StratégiIA** | ✅ Forte | L'analyse stratégique d'un dossier décès est plus complexe qu'un AT classique (multi-bénéficiaires) → valeur ajoutée IA forte |
| **Calculatrice IPP** | ⚠️ Indirecte | Le décès n'a pas d'IPP — c'est un capital + rente. **Nécessite un calculateur dédié** |
| **Simulateur AT** (en PRD) | ⚠️ Partielle | Le simulateur AT calcule la rente du sinistré vivant, pas la rente des ayants droit. **Variante distincte requise** |

---

## 5. Recommandation d'architecture cible

### 5.1 Décision préliminaire : page unique vs cluster vs simulateur

| Option | Coût | Impact attendu | Verdict |
|---|---|---|---|
| **Option A — Page unique** "Décès accident du travail" | 2-3 j | Couverture 4-5 requêtes, position 15-25 | ⚠️ Sous-dimensionné vu le volume cumulé estimé |
| **Option B — Cluster SEO complet** (1 pilier + 4-6 pages filles) | 12-18 j | Couverture 12-15 requêtes, position 5-12 sur les principales | 🟢 **Recommandé** |
| **Option C — Simulateur dédié seul** | 8-10 j | Très bonne conversion mais peu de SEO (les outils convertissent mais ne se ranquent pas seuls) | ⚠️ Insuffisant en isolation |
| **Option D — Cluster + simulateur (combo)** | 18-25 j | Couverture maximale + conversion maximale | 🎯 **Cible idéale long terme** |

### 5.2 Architecture cible — Cluster recommandé

```
/deces-accident-travail (PILIER)
│
├── /deces-accident-travail/ayants-droit          ← Conjoint, enfants, ascendants, déclaration
├── /deces-accident-travail/rente-conjoint        ← Calcul rente conjoint + simulateur dédié
├── /deces-accident-travail/capital-deces         ← Capital décès AT/MP + frais funéraires
├── /deces-accident-travail/faute-inexcusable     ← Procédure pôle social en cas de décès (premium)
├── /deces-accident-travail/enquete-inspection    ← Rôle inspection, procès-verbal, dossier
└── /deces-accident-travail/demarches-pratiques   ← Checklist démarches mois 1, 2, 3, 6, 12
```

**Outil dédié envisagé** : `/simulateur-rente-conjoint-survivant` (calculatrice à part, accessible depuis les pages cluster).

### 5.3 Maillage interne envisagé

```
Pilier /deces-accident-travail ←──────┐
   ↓ (vers ayants droit, rente, ...)  │
                                       │ (depuis :)
Pages existantes qui devraient mailler :
   • /guide/faute-inexcusable-employeur (ajoute lien naturel "Cas du décès → voir page dédiée")
   • /guide/accident-travail-non-declare-employeur (ajoute lien "Si décès lié")
   • /expertise-medicale (volet décès = expertise médicale post-mortem si autopsie ou cause médicale contestée)
   • /accident-travail-maladie-professionnelle (mention "En cas de décès, voir...")
   • Footer global (ajoute "Accompagnement familles" éventuel — à valider)
```

### 5.4 Parcours utilisateur recommandé

```
1. Arrivée SEO sur /deces-accident-travail/[page fille spécifique]
       ↓
2. Lecture du contenu pédagogique (zéro CTA agressif les 2 premiers tiers de page)
       ↓
3. Bloc « Comprendre votre situation » (1 minute) avec quiz léger
       ↓
4. Proposition d'un PDF gratuit "Guide démarches après décès AT" (email opt-in)
       ↓
5. Email de nurturing automatique (7 jours, 3 emails) — Resend déjà intégré
       ↓
6. Proposition mesurée d'un accompagnement humain (page "Notre accompagnement") — pas de checkout direct
       ↓
7. Si engagement : Dossier Express IA décès (variante du modèle existant)
```

**Différence majeure vs Dossier Express actuel** : aucune offre payante en 1ʳᵉ ouverture. Le funnel est **éducatif d'abord, transactionnel ensuite** — conforme à la sensibilité du sujet.

### 5.5 Schema.org recommandés

- `MedicalScholarlyArticle` (sur le pilier)
- `BreadcrumbList`
- `FAQPage` (6-8 questions par page fille)
- `HowTo` (sur "démarches pratiques")
- `LegalService` (organisation S.E.S sitewide — déjà planifié dans le draft Phase 2/3)

---

## 6. Comparaison avec les chantiers déjà étudiés

### 6.1 Tableau comparatif

| Critère | Phase 2 `/expertise-medicale` | Page fille `/assureur` | Simulateur AT | Simulateur MP | **Décès AT (cluster)** |
|---|---|---|---|---|---|
| **Volume mensuel ciblé** | 172 impr/28j observées | 114 impr/28j (déjà captées par pilier) | 200-500 estimé | 25-80 estimé | **~1 800-3 700 estimé** |
| **Difficulté SEO** | Faible (page existe, à enrichir) | Moyenne (terrain semi-vierge) | Moyenne | Moyenne-élevée | **Moyenne** (Service-public dominant) |
| **Effort dev** | 2-3 j | 4 j | 11 j | 15,5 j (mutualisé AT) | **12-18 j (cluster) ou 18-25 j (combo)** |
| **Conversion attendue** | Moyenne (info) | **Élevée (buyer-intent)** | Moyenne | Moyenne | **Élevée mais retardée** (cycle long) |
| **Ticket moyen client** | 49-150 € | 80-200 € | 49 € | 49 € | **80-300 €** (dossier complexe) |
| **Délai avant ROI** | 4-8 semaines | 6-10 semaines | 8-12 semaines | 12-16 semaines | **6-12 mois** (cycle décisionnel long) |
| **Risque réputationnel** | Faible | Faible | Faible | Moyen (CRRMP complexe) | **🔴 Élevé** (sensibilité éthique) |
| **Maturité préparatoire** | ✅ Draft complet | ✅ Inclus dans draft Phase 2/3 | ✅ PRD complet | ✅ PRD complet | ⚠️ **Étude préliminaire seule** |
| **Alignement avec /expertise-medicale** | 🎯 Direct | 🎯 Direct | Latéral | Latéral | Latéral (peut renforcer indirectement) |

### 6.2 Lecture stratégique de la comparaison

🥇 **Phase 2 et page fille `/assureur`** : restent les **chantiers de priorité absolue post-16/06**. ROI rapide, faible risque, maturité élevée.

🥈 **Simulateur AT** : reste le 2ᵉ chantier prioritaire, indépendant de `/expertise-medicale`.

🥉 **Cluster décès AT** : **le plus gros gisement SEO théorique** mais nécessite :
- Une maturité éditoriale spécifique (ton, références juridiques, empathie)
- Un cycle de conversion long (à mois 6-12)
- Un risque réputationnel à gérer (pas de communication maladroite)
- Une charge dev élevée (12-25 jours)

🟡 **Simulateur MP** : reste en queue de file, après stabilisation AT.

---

## 7. Classement multi-axes

### 7.1 Méthode

Notation 1 à 10 sur 4 axes, score combiné pondéré (SEO 25 % + Business 35 % + Effort inversé 20 % + Faisabilité immédiate 20 %).

### 7.2 Tableau de classement

| Chantier | Impact SEO | Impact business | Effort (10 = faible) | Faisabilité immédiate | **Score combiné** | **Rang** |
|---|---|---|---|---|---|---|
| Phase 2 `/expertise-medicale` | 7 | 8 | 9 | 10 | **8,2** | 🥇 #1 |
| Page fille `/expertise-medicale/assureur` | 8 | 9 | 7 | 9 | **8,3** | 🥇 #1 ex-aequo |
| Simulateur AT | 6 | 7 | 5 | 8 | **6,6** | 🥉 #3 |
| **Cluster décès AT** | **9** | **8** | **3** | **5** | **6,5** | **#4** |
| Simulateur MP | 5 | 6 | 4 | 6 | **5,4** | #5 |
| Simulateur rente conjoint (sous-projet décès) | 5 | 7 | 6 | 4 | **5,6** | #4 ex-aequo |

🎯 **Lecture clé** : le **cluster décès AT** a un score combiné **élevé en SEO (9/10) et business (8/10)**, mais est plombé par un effort important (3/10 = lourd) et une faisabilité immédiate moyenne (5/10 = nécessite préparation éthique + juridique).

### 7.3 Recommandation de priorité

```
COURT TERME (post 16/06, été 2026) :
   1. Phase 2 /expertise-medicale          [confirmé, GO probable]
   2. Page fille /assureur                  [confirmé, GO probable conditionnel]

MOYEN TERME (automne 2026) :
   3. Simulateur AT                         [si GSC 4AT.1 ≥ 200 impr/28j]
   4. Cluster décès AT — PHASE PRÉPARATOIRE
      • Brouillons rédactionnels (5-7 jours)
      • Validation juridique (2 jours)
      • Validation éthique (1 jour)
      • Décision GO/NO-GO final

LONG TERME (hiver 2026-2027) :
   5. Cluster décès AT — DÉPLOIEMENT (si GO préparatoire)
   6. Simulateur rente conjoint survivant
   7. Simulateur MP
```

---

## 8. Risques spécifiques au chantier "Décès AT"

### 8.1 Risques éthiques

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Communication perçue comme opportuniste / racoleuse | Moyenne | **CRITIQUE** | Ton sobre validé par juriste + éthicien + association de familles si possible |
| CTA prématuré déclenche un sentiment de "marchandisation du deuil" | Élevée si mal géré | **CRITIQUE** | Funnel éducatif d'abord, conversion en J+7 par email uniquement |
| Plainte ou signalement (réputation) | Faible si éthique respectée | **CRITIQUE** | Politique éditoriale formelle et publique sur la page |
| Diffusion sur réseaux sociaux d'une formulation maladroite | Moyenne | Élevée | Relecture systématique par 2 personnes avant publication |

### 8.2 Risques juridiques

| Risque | Mitigation |
|---|---|
| Diffusion d'informations juridiques erronées (responsabilité art. 1240 CC) | Validation juriste systématique, sources citées (CSS art. L.434-7 et suivants) |
| Publicité comparative non conforme | Aucune comparaison nominative avec d'autres cabinets / avocats |
| Démarchage abusif (art. L.121-7 Code consommation) | Aucun email automatique non sollicité, opt-in clair |

### 8.3 Risques SEO

| Risque | Mitigation |
|---|---|
| Cluster trop large dilue le PageRank | Pilier solide + maillage clair pages filles → pilier |
| Pénalisation YMYL (Your Money Your Life) | Auteur identifié, expertise prouvée (E-E-A-T), sources légales |
| Cannibalisation avec `/guide/faute-inexcusable-employeur` | Délimitation claire des intentions (générique vs décès) + maillage croisé |

### 8.4 Risques opérationnels

| Risque | Mitigation |
|---|---|
| Charge dev sous-estimée (cluster 6 pages = 12-18 j) | Découpage en sprints, livraison incrémentale (1 page tous les 7 j) |
| Coût de validation juridique sous-estimé | Budget 2-3 j juriste + 1 j éthicien à prévoir formellement |
| Effort éditorial supérieur à la moyenne (ton, sensibilité) | Pas de rédaction par IA seule — relecture humaine systématique |

---

## 9. Synthèse exécutive

### 9.1 Le sujet vaut-il l'effort ?

🟢 **Oui, conditionnellement** :
- **Volume SEO estimé** : 1 800-3 700 recherches/mois en France = potentiel équivalent ou supérieur au cluster `/expertise-medicale`.
- **Business** : ticket moyen 80-300 € + cycle de conversion à 6-12 mois = revenu annuel **11-68 k€**.
- **Différenciation** : terrain semi-vierge entre Service-public (institutionnel) et cabinets d'avocats (transactionnels).

🔴 **Mais sous conditions strictes** :
- Maturité éthique et éditoriale spécifique requise.
- Validation juridique non négociable.
- Pas avant que les chantiers prioritaires (Phase 2, page fille assureur, Simulateur AT) soient stabilisés.

### 9.2 Position recommandée dans le pipeline post-16/06

```
PRIORITÉ 1 (semaines 25-28, dès 17/06)
   ├── Phase 2 /expertise-medicale
   └── Page fille /expertise-medicale/assureur

PRIORITÉ 2 (semaines 29-36)
   ├── Pages filles complémentaires /mdph, /accident-travail, /contre-expertise
   └── Simulateur AT

PRIORITÉ 3 (semaines 37-44)
   └── 🆕 Cluster décès AT — PHASE PRÉPARATOIRE
        • Brouillons rédactionnels validés
        • Politique éditoriale formelle
        • Validation juridique
        • Décision GO/NO-GO déploiement

PRIORITÉ 4 (semaines 45-52)
   ├── 🆕 Cluster décès AT — DÉPLOIEMENT (si GO)
   └── Simulateur MP
```

### 9.3 Décision préliminaire suggérée

**À évaluer après le 16/06**. Le cluster décès AT est un **chantier de fort potentiel mais à maturité différée** — il ne doit pas court-circuiter les chantiers déjà préparés (Phase 2, assureur, Simulateur AT), mais doit **entrer formellement dans le backlog** comme chantier P2 stratégique à activer à l'automne/hiver 2026.

### 9.4 Décision finale à prendre après 16/06

3 options ouvertes :

| Option | Description |
|---|---|
| **A. GO préparatoire (recommandé)** | Lancer la phase préparatoire à l'automne 2026 (brouillons rédactionnels + validation juridique + politique éditoriale). Pas de déploiement avant fin 2026 / début 2027. |
| **B. REPORT** | Attendre une 2ᵉ confirmation du potentiel (nouvelle étude GSC à J+90, données concurrence approfondies via SEMrush/Ahrefs si accès budget). Ré-évaluer en octobre 2026. |
| **C. ABANDON** | Décision si le risque réputationnel est jugé trop élevé ou si les ressources sont insuffisantes. Le sujet reste en veille pour décision future. |

**Ma recommandation** : option **A (GO préparatoire à l'automne)**, après stabilisation des chantiers P1.

---

## 10. Annexes — Préalables avant un éventuel GO déploiement

### 10.1 Liste des préalables non négociables

- [ ] **Politique éditoriale formelle** sur le ton et la sensibilité (1 page de charte interne)
- [ ] **Validation juridique** des contenus par juriste S.E.S (sources CSS L.434-7 à L.434-16 minimum)
- [ ] **Validation éthique** par un tiers (éthicien, association de victimes, syndicaliste)
- [ ] **Bibliographie sources** (DARES, Ameli, INRS, jurisprudence Cass. soc.)
- [ ] **PDF gratuit "Guide démarches après décès AT"** rédigé et validé
- [ ] **Templates emails nurturing** (3 emails J+0, J+3, J+7) — Resend
- [ ] **Disclaimer empathique** standardisé sur toutes les pages cluster
- [ ] **Test utilisateur préalable** (3-5 personnes ayant vécu la situation — via association)
- [ ] **Plan de monitoring** spécifique post-lancement (Sentry + commentaires Clarity + plaintes)

### 10.2 Budget jours-homme (estimation détaillée)

| Phase | Jours-homme | Notes |
|---|---|---|
| Politique éditoriale + validation éthique | 2 | Document interne |
| Validation juridique | 2 | Juriste interne ou externe |
| Rédaction pilier + 6 pages filles | 8 | ~1 j par page de 800-1 200 mots |
| Développement React (templates, routes, schemas) | 4 | Réutilisation maillage existant |
| Schema.org + maillage interne | 1 | |
| Simulateur rente conjoint (optionnel) | 5 | Si combo activé |
| Tests + QA | 2 | |
| Validation tierce utilisateurs | 1 | Coordination |
| **TOTAL minimum (cluster seul)** | **20** | |
| **TOTAL combo (cluster + simulateur conjoint)** | **25** | |

---

**FIN — `OPPORTUNITE_SEO_ACCIDENTS_GRAVES_MORTELS_DRAFT.md`**
**🚨 NON PUBLIÉ — DRAFT — DOCUMENT DE PRÉPARATION**
**Décision GO / REPORT / ABANDON à prendre après le 2026-06-16 et stabilisation des chantiers P1.**
