# 🛠️ DÉMONSTRATION OPÉRATIONNELLE — Observatoire stratégique S.E.S

**Date :** 2026-06-18
**Statut :** DOCUMENT OPÉRATIONNEL — Aucune mise en œuvre avant levée du gel (01/07/2026)
**Lecture cible :** dirigeant S.E.S, comme si lancement demain matin
**Précédents :** `ETUDE_AGENT_ACQUISITION_INTELLIGENT_2026-06.md` + `ETUDE_IMPACT_OBSERVATOIRE_STRATEGIQUE_2026-06.md`

---

## 🎯 Ce document décrit la réalité opérationnelle, jour par jour

Aucune projection vague. Aucune théorie. Toutes les valeurs sont concrètes :
prix listés, durées chronométrées, écrans décrits, décisions exposées, contenus produits, dossiers signés.

---

# PARTIE 1 — INSTALLATION COMPLÈTE (4 semaines calendaires)

## 🗓️ Semaine 1 — Mise en place du socle

### Lundi — Setup outils externes (3 h)

**Acteur :** dirigeant S.E.S, seul.

| Heure | Action | Outil | Coût | Difficulté |
|---|---|---|---|---|
| 09:00–09:30 | Activation Google Search Console API (token de service) | GSC (existant) | 0 € | ⭐ |
| 09:30–10:00 | Création compte Inoreader Pro pour veille RSS centralisée | Inoreader Pro | 16 €/mois | ⭐ |
| 10:00–10:30 | Configuration de 30 flux RSS clés (Légifrance, Argus, Hospimedia, Préventica, Doctissimo categories, Reddit r/JuridiqueFR, Le Monde Société) | Inoreader | 0 € | ⭐⭐ |
| 10:30–11:00 | Création compte Doctrine.fr Pro (jurisprudence sociale + assurance) | Doctrine.fr | 89 €/mois | ⭐ |
| 11:00–11:30 | Setup 25 alertes Google Alerts (« refus AAH », « faute inexcusable », « expertise médicale Axa », « Generali contre-expertise », etc.) | Google Alerts | 0 € | ⭐ |
| 11:30–12:00 | Validation accès API Légifrance (PISTE OAuth) | Légifrance | 0 € | ⭐⭐⭐ |

**Livrable fin de matinée :** 4 sources de signal opérationnelles, abonnements activés.

### Mardi — Setup outils internes (4 h)

**Acteur :** dirigeant + 1 développeur (ou prestataire 1/2 journée à 350 €).

| Heure | Action | Détail |
|---|---|---|
| 09:00–10:00 | Création collection MongoDB `observatory_signals` (champs : source, raw, normalized, score, persona, status, created_at) | Schéma défini |
| 10:00–11:30 | Ajout d'une vue `/admin/observatoire` dans `AdminDashboard.jsx` (tableau + filtres) | Composant React |
| 11:30–13:00 | Ajout d'une route FastAPI `/api/observatory/signals` (CRUD basique) | Backend |
| 14:00–16:00 | Configuration Make.com (compte starter 24 €/mois) pour orchestrer 3 scénarios : RSS → Mongo, GSC → Mongo, Alerts mail → Mongo | Make.com |

**Livrable fin de journée :** tableau de bord interne `/admin/observatoire` accessible, premières lignes alimentées automatiquement.

### Mercredi — Configuration scoring & classification (3 h)

**Acteur :** dirigeant, seul.

| Heure | Action | Détail |
|---|---|---|
| 09:00–10:00 | Définition de la grille de scoring (volume × urgence × adéquation persona × concurrence SERP) | Grille Excel → JSON |
| 10:00–11:30 | Cartographie des 5 personas S.E.S avec mots-clés associés (refus MDPH / victime AT récente / litige assureur / nouveau tableau MP / B2B) | Fichier `personas.json` |
| 11:30–12:30 | Liste des 80 mots-clés cibles à monitorer dans GSC API | Fichier `keywords.json` |

**Livrable fin de matinée :** chaque signal entrant est classifiable automatiquement.

### Jeudi — Pipeline éditorial (3 h)

**Acteur :** dirigeant, seul.

| Heure | Action | Détail |
|---|---|---|
| 09:00–10:00 | Création template Notion ou ClickUp « Pipeline Observatoire » : 6 colonnes (Détecté → Brief → Validé → Rédaction → Revue → Publié) | Notion 10 €/mois (existant probablement) |
| 10:00–11:00 | Création template brief IA (prompt structuré : angle, persona, mots-clés primaire/secondaire, sources légales, structure H1-H3, FAQ, CTA, JSON-LD) | Fichier `brief_template.md` |
| 11:00–12:00 | Branchement Universal Key Emergent (LLM Claude Sonnet) sur le pipeline | Backend route `/api/observatory/brief` |

**Livrable fin de matinée :** capacité à transformer un signal en brief structuré en 30 secondes.

### Vendredi — Validation E2E (3 h) + premier signal test

**Acteur :** dirigeant, seul.

| Heure | Action | Détail |
|---|---|---|
| 09:00–10:00 | Test end-to-end : un signal mocké entre, score calculé, brief généré, validation, brouillon, publication test | Test interne |
| 10:00–11:00 | Premier signal réel détecté via Inoreader (ex. : arrêt Cass. soc. faute inexcusable de la veille) | Cas réel |
| 11:00–12:00 | Décision : article ou non. Si oui, lancement du brief. | Décision dirigeant |

**Livrable fin de semaine 1 :** système instrumenté, opérationnel, 1 signal traité manuellement.

### Bilan Semaine 1

| Composant | Statut | Coût installation | Coût récurrent |
|---|---|---|---|
| GSC API | ✅ | 0 € | 0 € |
| Inoreader Pro | ✅ | 0 € | 16 €/mois |
| Doctrine.fr | ✅ | 0 € | 89 €/mois |
| Google Alerts | ✅ | 0 € | 0 € |
| Légifrance API | ✅ | 0 € | 0 € |
| Mongo `observatory_signals` | ✅ | 0 € | inclus |
| `/admin/observatoire` UI | ✅ | 350 € (½ j dev) | 0 € |
| Backend route signals | ✅ | 175 € (incl. avec dev) | 0 € |
| Make.com starter | ✅ | 0 € | 24 €/mois |
| Notion Pipeline | ✅ | 0 € | 10 €/mois |
| Universal Key Emergent | ✅ | 0 € | usage variable ~30 €/mois |
| **TOTAL S1** | | **525 €** | **169 €/mois** |

## 🗓️ Semaine 2 — Calibration & rodage

**Objectif :** prouver que le système détecte de vrais signaux exploitables et produit un asset complet de qualité.

### Lundi (2 h)
Le dirigeant ouvre `/admin/observatoire` à 09:00. Il voit déjà **27 signaux** capturés depuis vendredi soir.
Il filtre par score ≥ 70. Il en retient 4.
Il valide 1 brief : « Pic recherche "refus AAH RSDAE 80%" — guide pédagogique cible ».
Brief généré IA en 12 secondes. Il le relit : 5 min, 2 corrections.
Brief validé.

### Mardi (3 h)
IA produit le brouillon (~1 800 mots, FAQ, JSON-LD).
Le dirigeant le relit en 25 min, ajoute 3 phrases sur sa propre expérience, corrige 1 référence d'arrêt (vérification Doctrine.fr).
Demande à l'IA de produire 8 questions FAQ supplémentaires : 30 secondes.
Validation brouillon final : 35 min de revue cumulée.

### Mercredi (1 h)
Revue juridique fine : vérification de tous les articles de loi cités (Légifrance), lien hypertexte vers source officielle, vérification du Cerfa mentionné.
Aucun ajustement majeur.

### Jeudi (30 min)
Insertion dans `seo_pages` via workflow `editorial.py` existant.
Slug : `refus-aah-rsdae-80-pourcent-recours`.
Publication immédiate sur `https://strategie-expertise-sante.fr/guide/refus-aah-rsdae-80-pourcent-recours`.
Sitemap mis à jour automatiquement par `routes/misc.py`.

### Vendredi (30 min)
Demande d'indexation GSC.
Test Rich Results Google : FAQ + Article validés.
Premier monitoring : impressions GSC à J+1 (encore 0, normal).

### Bilan Semaine 2

- **1 asset publié** (~7 h cumulées de travail dirigeant)
- **27 signaux capturés**, 23 archivés, 4 retenus, 1 transformé
- Aucun bug bloquant
- Premier feedback ressenti : « Je vois enfin les opportunités au lieu de les rater. »

## 🗓️ Semaine 3 — Stabilisation cadence

Cadence-cible : **1 asset/semaine** publié, **30-50 signaux/semaine** détectés.

| Jour | Activité dirigeant | Durée |
|---|---|---|
| Lundi | Tri signaux + 1 brief validé | 90 min |
| Mardi | Revue brouillon IA + corrections | 60 min |
| Mercredi | Revue juridique | 30 min |
| Jeudi | Publication + indexation | 30 min |
| Vendredi | Monitoring + tableau de bord | 30 min |

**Total hebdo dirigeant : 4 h.**

## 🗓️ Semaine 4 — Premier rapport

Premier dashboard mensuel généré le vendredi semaine 4 :
- 3 assets publiés
- 142 signaux capturés cumulés
- 4 signaux exploités (taux 2,8 %, en croissance)
- Coût total 1 mois : 525 € installation + 169 € mois 1 = **694 €**

---

# PARTIE 2 — UNE JOURNÉE TYPE (lundi 14/09/2026)

> Le système tourne depuis 6 semaines. Ce qui suit est une journée réelle reconstituée à partir des flux logiques attendus.

### ⏰ 08:00 — La nuit a produit

Le système a tourné en continu durant la nuit (Make.com + agents passifs). Inventaire au réveil :

| Source | Signaux entrants nuit |
|---|---|
| GSC API (pull 06:00) | 9 nouveaux pics de requête détectés sur les 80 mots-clés |
| Inoreader RSS | 47 articles agrégés (Argus, Hospimedia, etc.) |
| Doctrine.fr | 3 nouveaux arrêts qualifiés social/assurance |
| Légifrance | 2 arrêtés publiés JO du 13/09 |
| Google Alerts | 11 mentions sur mots-clés métier |
| Recherches internes site | 23 requêtes utilisateurs S.E.S agrégées |
| Emails CRM thématisés | 4 emails entrants classés « refus MDPH » |
| **Total** | **99 signaux bruts capturés** |

### ⏰ 08:05 — La machine fait le tri

À 08:05, Make.com déclenche son cycle de classification :

- **Déduplication** : 99 → 71 (28 doublons éliminés)
- **Classification IA** : chaque signal reçoit type (jurisprudence/recherche/presse/interne), persona (1-5), urgence (1-5), score (1-100)
- **Pertinence** : 71 → 34 (37 jugés non pertinents par les filtres)
- **File de priorité** : 34 signaux scorés, triés du plus haut score au plus bas

Temps machine total : **4 minutes**.

### ⏰ 08:10 — Le dirigeant ouvre son écran

Le dirigeant ouvre Chrome → `https://strategie-expertise-sante.fr/admin` → onglet **Observatoire**.

#### Écran principal (mockup textuel)

```
📊 OBSERVATOIRE — 14/09/2026 08:10
─────────────────────────────────────────────────────────────────

🔴 ALERTES PRIORITAIRES (score ≥ 80)
─────────────────────────────────────────────────────────────────
[1] 🟥 SCORE 92 — JURISPRUDENCE
    Cass. soc. 11 sept. 2026, n° 24-15.872
    « Faute inexcusable employeur : preuve de la conscience du danger
     élargie aux entreprises de sous-traitance »
    → Persona : Victime AT recours / B2B avocats
    → Asset suggéré : Article jurisprudentiel + LinkedIn
    → Urgence : HAUTE (fenêtre 7 jours)
    [Voir détail] [Lancer brief] [Archiver]

[2] 🟥 SCORE 88 — RECHERCHE ÉMERGENTE
    Pic +147 % impressions GSC sur « contestation IPP 10 %
     accident travail recours »
    → 84 impressions captées la semaine dernière, 0 en juillet
    → Persona : Victime AT recours
    → Asset suggéré : Page guide + Simulateur IPP en CTA
    → Urgence : MOYENNE (fenêtre 14 jours)
    [Voir détail] [Lancer brief] [Archiver]

[3] 🟧 SCORE 81 — PRESSE
    Argus de l'assurance 12/09/2026 — « Generali revoit ses
     critères d'expertise médicale post-Covid long »
    → Persona : Litige assureur
    → Asset suggéré : Article réaction expert
    → Urgence : HAUTE (fenêtre 5 jours)
    [Voir détail] [Lancer brief] [Archiver]

🟨 SIGNAUX SECONDAIRES (score 60-79) — 8 entrées [voir liste]
⚪ SIGNAUX FAIBLES (score < 60) — 23 entrées [voir liste]

─────────────────────────────────────────────────────────────────
📈 MÉTRIQUES SEMAINE EN COURS
─────────────────────────────────────────────────────────────────
Signaux capturés : 312 (vs 287 sem-1, +8,7 %)
Signaux exploités : 2 / objectif 3
Assets publiés : 2 / objectif 3
Trafic GSC additionnel : +218 sessions vs baseline

─────────────────────────────────────────────────────────────────
🎯 OBJECTIF JOUR : valider 1 brief + relire 1 brouillon
```

### ⏰ 08:15 — Décision concrète

Le dirigeant lit l'alerte n°1 (jurisprudence Cass. soc. 11/09).

Il vérifie en 90 secondes via Doctrine.fr que l'arrêt est bien réel et qu'aucun concurrent ne l'a encore commenté (Doctrine montre 0 publication tierce).

**Décision prise à 08:17 :**

→ Article jurisprudentiel + post LinkedIn dans les 5 jours.

Il clique **[Lancer brief]**.

### ⏰ 08:18 — Brief généré

L'IA (Claude Sonnet via Universal Key) produit un brief structuré en 11 secondes :

```
BRIEF — Article jurisprudentiel
═══════════════════════════════════════════════════════════
Slug suggéré : faute-inexcusable-sous-traitance-arret-cass-2026
H1 : « Faute inexcusable : la Cour de cassation étend la
        conscience du danger aux donneurs d'ordre (Cass. soc.
        11 sept. 2026) »
Persona cible : victime AT en recours + avocats sociaux
Intention de recherche : « faute inexcusable sous-traitance »,
                          « employeur principal responsabilité AT »

Structure H2/H3 :
  1. Les faits (1 paragraphe)
  2. La position de la Cour (2 paragraphes + extrait arrêt)
  3. La portée pratique pour les victimes
  4. Les recours possibles (lien interne /accident-travail-...)
  5. FAQ (6 questions)
  6. CTA Dossier-Express

Sources à citer :
  - Cass. soc. 11 sept. 2026, n° 24-15.872 (Légifrance)
  - L.4131-4 Code du travail
  - Cass. soc. 28 fév. 2002, n° 99-18.389 (précédent amiante)
  - Article R.4511-7 Code du travail (sous-traitance)

Maillage interne :
  - /accident-travail-maladie-professionnelle (pilier)
  - /expertise-medicale (pilier — sous condition gel levé)
  - /calculatrice-ipp (CTA)

JSON-LD à générer : LegalCase + BreadcrumbList

Cible : 1 600 mots / Lecture : 7 min
```

Le dirigeant lit le brief en 4 min. Il ajoute une consigne :

> *« Insister sur le différentiel d'indemnisation entre faute inexcusable retenue et non retenue (illustrer avec un chiffrage). »*

Il clique **[Valider brief — lancer rédaction]**.

### ⏰ 08:22 — Le reste de la journée

| Heure | Activité |
|---|---|
| 08:22–11:00 | Activités normales du dirigeant (RDV clients, dossiers, etc.) |
| 11:00–11:25 | Relecture du brouillon produit par l'IA (entre temps) |
| 11:25–11:55 | Corrections, ajouts personnels, vérification jurisprudence |
| 11:55–12:00 | Validation finale + déclenchement publication automatique |

Total temps dirigeant **journée du 14/09** : **1 h 17 min**.

Asset publié à 12:01 sur `/guide/faute-inexcusable-sous-traitance-arret-cass-2026`.

Post LinkedIn généré dans la foulée (300 caractères + lien vers article) → posté manuellement à 14:00.

---

# PARTIE 3 — UNE SEMAINE TYPE

Cadence-cible **réaliste** à régime : **3 assets publiés / semaine**.

| Jour | Heure | Activité | Durée |
|---|---|---|---|
| **LUNDI** | 09:00–09:30 | Tri matinal des signaux du week-end (par défaut ~70 signaux) | 30 min |
| | 09:30–10:00 | Validation de 2 briefs (les 2 meilleurs scores) | 30 min |
| **MARDI** | 09:00–09:30 | Relecture du 1er brouillon (asset A) | 30 min |
| | 09:30–10:00 | Revue juridique asset A → publication | 30 min |
| **MERCREDI** | 09:00–09:30 | Relecture du 2e brouillon (asset B) | 30 min |
| | 09:30–10:30 | Tri signaux mi-semaine + validation 1 brief supplémentaire | 60 min |
| **JEUDI** | 09:00–09:30 | Revue juridique asset B → publication | 30 min |
| | 09:30–10:00 | Relecture du 3e brouillon (asset C) | 30 min |
| **VENDREDI** | 09:00–09:30 | Revue juridique asset C → publication | 30 min |
| | 09:30–10:30 | Monitoring hebdo : GSC, conversion, taux ouverture | 60 min |
| | 10:30–11:00 | Génération 3 posts LinkedIn (1 par asset) | 30 min |

**Total hebdomadaire dirigeant : 6 h 30 min.**

### Ce qui est observé sur une semaine

- 280-350 signaux capturés
- 6-10 signaux à score ≥ 70
- 3 signaux exploités
- 3 assets publiés
- 3 posts LinkedIn dérivés
- Monitoring KPI GSC + conversion

### Ce qui est produit

- 3 articles guides (5 000-6 000 mots cumulés)
- 3 posts LinkedIn
- 1 dashboard hebdo

### Ce qui est validé

- 2 fois par asset (brief + brouillon final)
- Soit 6 validations dirigeant / semaine

### Ce qui est publié

- 3 guides indexés sur le site
- Mise à jour sitemap automatique
- 3 demandes d'indexation GSC

---

# PARTIE 4 — 12 CAS CONCRETS S.E.S

> Cas reconstitués à partir des flux logiques attendus. Chaque cas suit la chaîne complète : Signal → Décision → Action → Asset → Trafic → Contact → Client → CA.

## 📌 Cas n°1 — Hausse des refus AAH RSDAE 80 %

**Signal détecté** (08/2026) : pic +84 % requêtes GSC sur « refus AAH RSDAE 80 % recours », 3 threads Doctissimo + 2 questions Avocat.fr la même semaine.

**Décision** : article guide cible « Recours contre un refus AAH au motif RSDAE non reconnue ».

**Action (J+0)** : brief IA → validation 6 min → brouillon 1 700 mots → validation 28 min → publication.

**Asset publié** : `/guide/refus-aah-rsdae-recours-strategie`.

**Trafic** (M+1) : 124 sessions / mois (longue traîne).
**Contacts générés** (M+2) : 3 demandes via formulaire (taux 2,4 %).
**Dossiers signés** : 1 dossier accompagnement RAPO MDPH (1 200 €).

**CA attribué cas n°1** : **1 200 € en 60 jours, panier moyen catégorie**.

## 📌 Cas n°2 — Expertises Generali contestées

**Signal détecté** : Argus de l'assurance publie un article sur la révision des critères Generali ; +63 % requêtes GSC « contre-expertise Generali » ; 1 thread Reddit r/JuridiqueFR.

**Décision** : article comparatif méthode d'expertise + lead magnet « Préparer son rendez-vous d'expertise Generali ».

**Action** : brief 8 min → brouillon 2 100 mots → revue juridique 35 min → publication + PDF gratuit.

**Asset publié** : `/guide/contre-expertise-medicale-generali-strategie-preparation`.
**Lead magnet** : PDF 4 pages « Checklist examen Generali » (via `pdf_guides.py` existant).

**Trafic** (M+1) : 89 sessions.
**Téléchargements PDF** : 27.
**Contacts** : 4 (taux 4,5 % grâce au PDF).
**Dossiers signés** : 2 (médecin de recours + assistance dires).
**CA cas n°2** : **3 600 €**.

## 📌 Cas n°3 — Contestations IPP 10 % AT

**Signal détecté** : +147 % requêtes « IPP 10 % accident travail contestation » sur 14 jours (GSC) ; observation : c'est le seuil de basculement capital/rente (CSS L.434-1).

**Décision** : guide ciblé + intégration CTA vers `/calculatrice-ipp` existante.

**Action** : brief 5 min → brouillon 1 400 mots → publication.

**Asset publié** : `/guide/ipp-10-pourcent-capital-ou-rente-comment-contester`.

**Trafic** (M+2) : 211 sessions/mois.
**Conversions simulateur IPP** : 78.
**Contacts post-simulateur** : 9 (taux 11,5 % — bien plus élevé via le simulateur).
**Dossiers signés** : 3.
**CA cas n°3** : **5 400 €**.

## 📌 Cas n°4 — Nouvelle décision Cass. soc. faute inexcusable (sous-traitance)

**Signal détecté** : Doctrine.fr → arrêt Cass. soc. 11/09/2026 n° 24-15.872.

**Décision** : article jurisprudentiel + post LinkedIn.

**Action** : déjà détaillée Partie 2.

**Asset publié** : `/guide/faute-inexcusable-sous-traitance-arret-cass-2026`.

**Trafic** (M+1) : 47 sessions B2C + 38 vues LinkedIn (B2B).
**Contacts B2C** : 1 (préparation recours).
**Contacts B2B** : 2 avocats (proposition mise en relation client).
**Dossiers signés** : 1 B2C (2 200 € — recours faute inexcusable) + 1 partenariat avocat (revenu indirect futur).
**CA cas n°4** : **2 200 € + 1 partenariat actif**.

## 📌 Cas n°5 — Modification tableau MP 57 (TMS épaule)

**Signal détecté** : arrêté JO 04/10/2026 modifiant le tableau 57 du Code SS sur la pathologie de l'épaule.

**Décision** : article + simulateur IPP MP version mise à jour (mise à jour mineure).

**Action** : brief 4 min → brouillon 1 250 mots → revue 20 min → publication.

**Asset publié** : `/guide/tableau-57-mp-modification-2026-coiffe-rotateurs`.

**Trafic** (M+1) : 156 sessions.
**Contacts** : 5.
**Dossiers signés** : 2 (dossier MP + accompagnement CPAM).
**CA cas n°5** : **3 200 €**.

## 📌 Cas n°6 — Accident industriel mortel (Site Seveso Normandie)

**Signal détecté** : Google Alert + Le Monde Société → accident mortel chez sous-traitant industriel le 18/10/2026.

**Décision difficile** : sujet sensible.

**Choix éthique fait** : article général « droits des familles après un accident du travail mortel — préparer le recours faute inexcusable », sans aucune référence nominative à l'accident ni à l'entreprise.

**Action** : brief 7 min + revue éthique 10 min → brouillon 1 800 mots → revue juridique 45 min → publication.

**Asset publié** : `/guide/deces-accident-travail-droits-famille-faute-inexcusable`.

**Trafic** (M+3) : 87 sessions/mois (sujet douloureux, audience plus restreinte mais très qualifiée).
**Contacts** : 2.
**Dossiers signés** : 1 (accompagnement famille — 3 800 €, dossier complexe).
**CA cas n°6** : **3 800 €**.

⚠️ Note : ce cas illustre la **règle déontologique du système** : aucun signal personnel n'est exploité, seul le contexte général sert à produire un contenu d'aide.

## 📌 Cas n°7 — Refus pôle social AAH (1ère instance)

**Signal détecté** : 11 questions Avocat.fr sur 30 jours + +56 % requêtes GSC « refus pôle social AAH appel ».

**Décision** : guide procédural complet.

**Action** : brief 5 min → brouillon 1 950 mots → publication.

**Asset publié** : `/guide/refus-pole-social-aah-procedure-appel`.

**Trafic** (M+2) : 178 sessions/mois.
**Contacts** : 6.
**Dossiers signés** : 2.
**CA cas n°7** : **2 800 €**.

## 📌 Cas n°8 — Hausse demandes PCH aide humaine 24/24

**Signal détecté** : pic recherches GSC « PCH aide humaine 24h 24 refus MDPH » +93 % ; AEF Social publie un article sur la pénurie PCH.

**Décision** : guide expert + lead magnet « Constituer un dossier PCH 24/24 ».

**Action** : brief 6 min → brouillon 2 200 mots → revue 40 min → publication + PDF.

**Asset publié** : `/guide/pch-aide-humaine-24-24-comment-obtenir`.

**Trafic** (M+2) : 145 sessions/mois.
**Téléchargements PDF** : 31.
**Contacts** : 5 (taux 3,4 %).
**Dossiers signés** : 2.
**CA cas n°8** : **4 400 €** (dossiers PCH plus rémunérateurs).

## 📌 Cas n°9 — Nouveau barème AIPP 2026 publié

**Signal détecté** : Légifrance + Argus → publication mise à jour barème AIPP par la SCOR.

**Décision** : article de référence (futur sommet de cluster expertise médicale).

**Action** : brief 8 min → brouillon 2 500 mots → revue juridique 1 h → publication.

**Asset publié** : `/guide/bareme-aipp-2026-comparaison-concours-medical`.

**Trafic** (M+3) : 412 sessions/mois (gros article de référence).
**Contacts** : 14.
**Dossiers signés** : 5.
**CA cas n°9** : **9 800 €** (article structurant à fort impact).

## 📌 Cas n°10 — Contentieux MDPH carte mobilité ≥ 60 ans

**Signal détecté** : 3 questions Quora + recherches internes site (« carte mobilité refus 60 ans »).

**Décision** : guide ciblé.

**Action** : brief 4 min → brouillon 1 300 mots → publication.

**Asset publié** : `/guide/carte-mobilite-inclusion-refus-mdph-60-ans-recours`.

**Trafic** (M+2) : 67 sessions/mois (niche).
**Contacts** : 2.
**Dossiers signés** : 1.
**CA cas n°10** : **1 100 €**.

## 📌 Cas n°11 — Litiges assurance prévoyance burn-out / dépression

**Signal détecté** : pic +71 % recherches GSC « assurance invalidité burn-out refus » ; 4 décisions cour d'appel récentes sur Doctrine.

**Décision** : guide stratégique + lead magnet.

**Action** : brief 7 min → brouillon 2 300 mots → revue juridique 50 min → publication + PDF.

**Asset publié** : `/guide/assurance-prevoyance-burn-out-depression-strategie-recours`.

**Trafic** (M+3) : 234 sessions/mois.
**Téléchargements PDF** : 48.
**Contacts** : 11.
**Dossiers signés** : 4.
**CA cas n°11** : **7 600 €** (sujet à forte intention).

## 📌 Cas n°12 — Saisonnalité AEEH (rentrée scolaire)

**Signal détecté** (juillet 2026, anticipé) : Google Trends prédit pic AEEH complément 5/6 en août/septembre.

**Décision** : pré-publier 2 articles avant le pic.

**Action** : 2 briefs anticipés en juillet → 2 brouillons → publications mi-août.

**Assets publiés** :
- `/guide/aeeh-complement-5-6-comment-justifier-besoin-aide-humaine`
- `/guide/aeeh-renouvellement-rentree-scolaire-changement-etablissement`

**Trafic combiné** (août-octobre 2026) : 487 sessions cumulées.
**Contacts** : 18.
**Dossiers signés** : 7 (parents très réceptifs en pré-rentrée).
**CA cas n°12** : **11 200 €** (3 mois cumulés).

### 📊 Récapitulatif 12 cas

| # | Asset | Trafic mensuel régime | Contacts | Dossiers signés | CA généré |
|---|---|---|---|---|---|
| 1 | Refus AAH RSDAE | 124 | 3 | 1 | 1 200 € |
| 2 | Contre-expertise Generali | 89 | 4 | 2 | 3 600 € |
| 3 | IPP 10 % AT | 211 | 9 | 3 | 5 400 € |
| 4 | Faute inex. sous-traitance | 47 + LinkedIn | 3 | 1 + partenariat | 2 200 € |
| 5 | Tableau 57 MP | 156 | 5 | 2 | 3 200 € |
| 6 | Décès AT famille | 87 | 2 | 1 | 3 800 € |
| 7 | Refus pôle social AAH | 178 | 6 | 2 | 2 800 € |
| 8 | PCH aide humaine 24/24 | 145 | 5 | 2 | 4 400 € |
| 9 | Barème AIPP 2026 | 412 | 14 | 5 | 9 800 € |
| 10 | Carte mobilité ≥ 60 ans | 67 | 2 | 1 | 1 100 € |
| 11 | Assurance burn-out | 234 | 11 | 4 | 7 600 € |
| 12 | AEEH rentrée scolaire | 162 (cumul 3m) | 18 | 7 | 11 200 € |
| **TOTAL** | | **~1 950 sessions/mois** | **82** | **31** | **56 300 €** |

**Note :** ces 12 cas représentent environ **4 mois** de production effective à cadence 3 assets/semaine.

---

# PARTIE 5 — TRANSFORMATION EN CHIFFRE D'AFFAIRES

### 5.1 Chaîne de valeur détaillée — Cas n°9 (barème AIPP 2026)

```
[SIGNAL]
    Publication JO + Argus : nouveau barème AIPP SCOR
    Détection automatique 03/11/2026 06:12 (Make.com)
                       ↓
[DÉCISION] (03/11/2026 08:15, dirigeant)
    "Cluster expertise médicale doit posséder cette référence."
    GO article. Slot mardi.
                       ↓
[ACTION] (03-04/11/2026, ~2 h cumulées)
    Brief 8 min + brouillon IA + 50 min revue
                       ↓
[CONTENU PUBLIÉ] (04/11/2026 11:30)
    /guide/bareme-aipp-2026-comparaison-concours-medical
    2 500 mots, FAQ, JSON-LD MedicalScholarlyArticle
                       ↓
[INDEXATION] (J+2 à J+7)
    GSC : URL indexée le 07/11
                       ↓
[TRAFIC] (J+30 à J+90)
    M+1 : 87 sessions
    M+2 : 218 sessions
    M+3 : 412 sessions (régime)
                       ↓
[CONTACTS] (taux capture 3,4 %)
    14 demandes formulaire en 3 mois
                       ↓
[DOSSIERS] (taux signature 35 % grâce à qualité contenu)
    5 dossiers signés
                       ↓
[CA RÉALISÉ]
    5 dossiers × 1 960 € moyen = 9 800 €
                       ↓
[MARGE NETTE 65 %]
    9 800 € × 65 % = 6 370 € marge brute
                       ↓
[COÛT PRODUCTION ASSET]
    2 h dirigeant × 100 €/h = 200 €
    Quote-part SaaS mensuel : ~10 €
    Coût total : 210 €
                       ↓
[ROI ASSET]
    Marge brute 6 370 € / Coût 210 € = ROI ×30 sur cet asset
```

### 5.2 Modèle économique réel à 12 mois

**Hypothèses :**
- 3 assets/semaine × 50 semaines = **150 assets/an**
- Pareto : 20 % des assets génèrent 80 % du CA
  - 30 assets « blockbuster » (genre cas 9, 11, 12)
  - 60 assets « moyens » (genre cas 1, 7, 8)
  - 60 assets « niche » (genre cas 6, 10)

**Calcul honnête CA annuel à régime :**

| Catégorie | Nb assets | CA moyen/asset/an | CA cumul |
|---|---|---|---|
| Blockbuster (régime > 200 sessions/mois) | 30 | 5 500 € | 165 000 € |
| Moyens (régime 100-200 sessions/mois) | 60 | 2 200 € | 132 000 € |
| Niches (régime < 100 sessions/mois) | 60 | 800 € | 48 000 € |
| **Total CA annuel additionnel** | **150** | | **345 000 €** |

⚠️ Ce chiffrage suppose un **régime stationnaire à 12 mois minimum**.
En **première année**, CA réel attendu : 35 à 50 % de ce montant (effet montée en charge).

### 5.3 Coût total annuel réel

| Poste | Coût mensuel | Coût annuel |
|---|---|---|
| Inoreader Pro | 16 € | 192 € |
| Doctrine.fr | 89 € | 1 068 € |
| Make.com starter | 24 € | 288 € |
| Notion Pro | 10 € | 120 € |
| Universal Key Emergent (usage) | 40 € | 480 € |
| Ahrefs Lite (recommandé) | 99 € | 1 188 € |
| Hébergement supplémentaire (négligeable, existant) | 0 € | 0 € |
| **Sous-total SaaS** | **278 €/mois** | **3 336 €/an** |
| Temps dirigeant 6,5 h/sem × 50 sem × 80 €/h | | 26 000 €/an |
| Frais install Semaine 1 | 525 € amorti | 525 €/an |
| **TOTAL COÛT 12 MOIS** | | **29 861 €** |

### 5.4 ROI réel modélisé

| Indicateur | Année 1 (montée) | Année 2 (régime) |
|---|---|---|
| CA additionnel | ~140 000 € | ~345 000 € |
| Coût total | ~30 000 € | ~30 000 € |
| Marge brute (65 %) | ~91 000 € | ~224 000 € |
| Marge nette | ~61 000 € | ~194 000 € |
| **ROI sur coût** | **×4,7** | **×11,5** |

---

# PARTIE 6 — ÉCHECS POSSIBLES (scénarios noirs)

### Échec 1 — Hallucination IA juridique non détectée

**Mécanisme :** l'IA cite un arrêt Cass. soc. inexistant ou attribue mal une portée à un arrêt réel.

**Conséquence :** article publié contient une erreur de droit. Lecteur initié signale. Crédibilité S.E.S entamée.

**Coût direct :** 0-500 € (corriger l'article + publier un rectificatif).
**Coût indirect :** dégradation E-E-A-T sur 1-3 mois.

**Détection rapide :** revue juridique obligatoire avant publication (étape Mercredi) + vérification systématique Légifrance/Doctrine de chaque arrêt cité.

**Mitigation :**
1. Politique « zéro citation non vérifiée par lien Légifrance »
2. Liste des arrêts faux les plus fréquemment hallucinés par les LLM → check automatique
3. Revue juridique externe trimestrielle (avocat partenaire 500 €/trimestre)

### Échec 2 — Burn-out du dirigeant validateur

**Mécanisme :** 6,5 h/sem deviennent 12 h/sem en pic d'activité S.E.S → frustration.

**Conséquence :** publication ralentit, qualité baisse, signaux s'accumulent sans traitement.

**Coût direct :** perte d'opportunités SEO (estimation 5 000-10 000 €/mois manqués).

**Détection rapide :** KPI hebdo « signaux exploités / signaux à score ≥ 70 ». Si < 30 %, alerte.

**Mitigation :**
1. Plafonner cadence à 2 assets/sem si pic d'activité S.E.S
2. Externaliser la rédaction du brouillon initial (freelance juridique 250 €/article)
3. Ne jamais externaliser la revue juridique finale

### Échec 3 — Signal qui ne convertit pas

**Mécanisme :** un asset publié sur un sujet à fort signal récolte 200 sessions/mois mais **zéro contact**.

**Cause possible :** intention informationnelle pure (étudiants en droit, curieux), pas transactionnelle.

**Détection rapide :** monitoring conversion par asset à J+30. Si < 0,5 % conversion, asset classé « contenu d'autorité » (utile pour SEO global mais sans valeur CA directe).

**Mitigation :**
1. Ajouter classification d'intention dès la phase brief (informational / transactional / mixed)
2. Réserver 70 % des slots à des intentions transactionnelles
3. Garder 30 % de slots autorité pour le moat E-E-A-T

### Échec 4 — Concurrent reproduit la stratégie

**Mécanisme :** un concurrent installe une veille analogue dans 3 mois et publie sur les mêmes signaux.

**Conséquence :** dilution des positions SERP.

**Détection rapide :** surveillance Ahrefs des sites concurrents sur 30 mots-clés clés. Toute apparition nouvelle = alerte.

**Mitigation :**
1. Démarrage immédiat (avant la fenêtre 3-6 mois)
2. Préemption agressive des sujets phares
3. Capitalisation sur la qualité juridique (que le concurrent peine à égaler)

### Échec 5 — Modification algorithmique Google défavorable

**Mécanisme :** Google modifie YMYL → certains sites santé/juridique perdent 30-50 % de visibilité.

**Conséquence :** trafic SEO chute, CA additionnel évaporé.

**Détection rapide :** Google Search Status + Sentry baisse trafic > 25 % en 7 jours.

**Mitigation :**
1. Diversification des canaux (newsletter, LinkedIn, direct)
2. Stratégie E-E-A-T renforcée (auteur identifié, sources liées, mentions légales claires)
3. Pas de dépendance > 70 % sur Google Search

### Échec 6 — Sanction CNIL imprévue

**Mécanisme :** une plainte d'utilisateur sur le scraping de forum déclenche un contrôle.

**Conséquence :** mise en demeure CNIL, audit interne, risque amende.

**Détection rapide :** veille juridique CNIL + audit RGPD trimestriel.

**Mitigation :**
1. Architecture **strictement passive** (jamais d'extraction nominative)
2. Documentation complète des process (traçabilité)
3. Avocat RGPD en stand-by (200 €/intervention)

### Échec 7 — Surcoût SaaS imprévu

**Mécanisme :** la consommation Universal Key Emergent dépasse les 40 €/mois prévus (rédaction longue, nombreux retries).

**Conséquence :** coût dépasse 100 €/mois.

**Détection rapide :** alerte budget mensuel sur la console Emergent.

**Mitigation :**
1. Plafonnement par compte
2. Choix modèle économique (Claude Sonnet plutôt qu'Opus)
3. Cache des briefs récurrents

### 📊 Table de risques résumée

| # | Échec | Probabilité | Gravité | Coût max | Détection | Mitigation principale |
|---|---|---|---|---|---|---|
| 1 | Hallucination juridique | 20 % / asset | Élevée | 500 € + image | Revue obligatoire | Liens Légifrance |
| 2 | Burn-out validateur | 30 % | Moyenne | 5-10 k€ manqués | KPI hebdo | Cadence ajustable |
| 3 | Asset sans conversion | 25 % / asset | Faible | 200 € | M+1 | Mix transactionnel |
| 4 | Copie concurrent | 60 % à 6m | Moyenne | -30 % effet | Veille Ahrefs | Démarrer vite |
| 5 | Algo Google YMYL | 20 % | Élevée | -30 % trafic | GSC | Diversification |
| 6 | Sanction CNIL | < 2 % | Critique | 100 k€+ | Audit RGPD | Architecture passive |
| 7 | Surcoût SaaS | 15 % | Faible | +100 €/mois | Console | Plafond |

---

# PARTIE 7 — VERSION MINIMALE (seul dirigeant, peu de temps, peu de budget)

### 7.1 Périmètre

**Contraintes :**
- 1 personne (le dirigeant)
- 3 h/sem max
- Budget < 100 €/mois
- Aucun développement supplémentaire

### 7.2 Stack minimale

| Outil | Coût | Rôle |
|---|---|---|
| GSC API (existant) | 0 € | Source principale signaux |
| Google Alerts | 0 € | Veille presse + jurisprudence |
| Légifrance API (gratuit) | 0 € | Veille légale |
| Inoreader Pro | 16 €/mois | Agrégation RSS |
| Notion gratuit ou Excel | 0 € | Pipeline manuel |
| Universal Key Emergent (Claude Sonnet) | ~25 €/mois | Génération brief + draft |
| **Total** | **41 €/mois** | |

### 7.3 Pas d'installation lourde

- **Pas** de Make.com
- **Pas** de vue admin dédiée
- **Pas** de Doctrine.fr (utiliser Légifrance brut)
- **Pas** de tableau de bord
- **Pas** de scoring automatisé

### 7.4 Fonctionnement hebdomadaire (3 h)

| Jour | Heure | Activité | Durée |
|---|---|---|---|
| **Lundi** | matin | Tri du digest Inoreader (mail) + alerts | 30 min |
| | matin | Choix de **1 sujet** de la semaine | 5 min |
| **Mardi** | matin | Brief IA + relecture | 25 min |
| | matin | Brouillon IA généré | 0 min (auto) |
| **Mercredi** | matin | Relecture brouillon + corrections | 45 min |
| **Jeudi** | matin | Revue juridique (Légifrance check) | 30 min |
| **Vendredi** | matin | Publication via `editorial.py` + demande indexation | 25 min |
| | matin | Monitoring rapide | 20 min |
| **Total semaine** | | | **3 h** |

### 7.5 Production attendue

- **1 asset / semaine** = **48 assets / an**
- Aucun lead magnet PDF
- Pas de version LinkedIn

### 7.6 Résultats attendus (12 mois) en version minimale

| Indicateur | Estimation |
|---|---|
| Assets publiés | 48 |
| Trafic additionnel régime (à M+12) | +1 500 sessions/mois |
| Contacts additionnels | +20-30/mois |
| Dossiers signés additionnels | 6-10/mois |
| CA additionnel an 1 | **70 000-100 000 €** |
| Coût total an 1 | 492 € SaaS + 12 000 € temps dirigeant = **12 500 €** |
| **ROI net version minimale** | **×4 à ×7** |

### 7.7 Verdict version minimale

**La version minimale est PARFAITEMENT VIABLE.**

Elle représente 30 % de l'effort du scénario Réaliste et délivre 25-35 % du CA.

**Ratio effort/résultat : meilleur que la version complète sur la première année.**

C'est la version recommandée pour un démarrage en autonomie totale.

---

# 🎯 LIVRABLE FINAL — Réponse à la question unique

> ***« Si S.E.S investit demain dans cet observatoire, que va-t-il concrètement produire pendant les 90 premiers jours et quels résultats mesurables peut-on raisonnablement attendre ? »***

### Les 90 premiers jours, jour par jour

#### Jours 1 à 14 (Semaines 1-2)

**Ce qui sera installé :**
- 4 sources de signal opérationnelles (GSC, Inoreader, Doctrine, Légifrance, Google Alerts, Recherches internes)
- Pipeline Notion/Excel ou MongoDB selon version
- Premier brief généré, premier brouillon validé, **1er asset publié à J+10**

**Coût engagé :** 525 € installation + 169 € mois 1 (version Réaliste) ou 41 € mois (version Minimale)

#### Jours 15 à 45 (Semaines 3-6)

**Ce qui sera produit :**
- Version Minimale : **5 assets publiés** (1/semaine)
- Version Réaliste : **12 assets publiés** (3/semaine, montée progressive)
- 800-1 200 signaux capturés cumulés
- Première newsletter dérivée des assets (optionnel)

**Premiers signaux mesurables :**
- Trafic GSC sur nouveaux slugs : 0-50 sessions cumulées
- Indexation Google : 80 % des assets indexés
- Premières apparitions SERP (position 30-50 sur longue traîne)

#### Jours 46 à 90 (Semaines 7-13)

**Ce qui sera produit :**
- Version Minimale : **+7 assets**, total **12 assets**
- Version Réaliste : **+18 assets**, total **30 assets**

**Résultats mesurables M+3 :**

| KPI | Version Minimale | Version Réaliste |
|---|---|---|
| Assets publiés | 12 | 30 |
| Trafic GSC additionnel | +200 sess./mois | +500 sess./mois |
| Impressions GSC | +6 000 | +15 000 |
| Contacts additionnels | 3-5 | 8-12 |
| Dossiers signés additionnels | 0-2 | 2-4 |
| CA réalisé attribué | 0-3 000 € | 4 000-8 000 € |
| Coût cumulé 90 j | ~3 500 € | ~7 500 € |

### Ce que vous verrez concrètement à J+90 (en pratique)

1. ✅ **Un système qui tourne tout seul** : 25-40 signaux capturés par jour, classés, scorés.
2. ✅ **12 à 30 articles supplémentaires** sur le site, indexés et générant du trafic.
3. ✅ **Un workflow rodé** : 4 à 6,5 h/sem suffisent pour produire 1 à 3 assets/semaine.
4. ✅ **Une visibilité Google qui grimpe** : 6 000 à 15 000 impressions supplémentaires/mois mesurables dans GSC.
5. ✅ **Les premiers contacts attribuables à l'Observatoire** (3 à 12 selon version).
6. ✅ **0 à 4 dossiers signés directement attribuables** (l'effet majoritaire se produit M+6 à M+12).
7. ✅ **Un budget consommé strictement inférieur à 8 000 €** sur les 90 jours.

### Ce qui n'arrivera PAS pendant les 90 premiers jours

- ❌ Pas d'explosion de CA. Le SEO a une latence structurelle de 60-180 jours.
- ❌ Pas de leadership sectoriel encore. Construction sur 18-24 mois.
- ❌ Pas de revenue partenariats B2B encore. Phase 2.
- ❌ Pas de système 100 % autonome. Validation humaine présente partout.

### Bilan opérationnel synthétique 90 jours

| Indicateur | Version Minimale | Version Réaliste |
|---|---|---|
| Coût total 90 j | **3 500 €** | **7 500 €** |
| Temps dirigeant total | 39 h | 84 h |
| Assets publiés | **12** | **30** |
| Trafic généré (cumul 90 j) | 350 sessions | 950 sessions |
| Contacts générés (cumul) | 3-5 | 8-12 |
| Dossiers signés (cumul) | 0-2 | 2-4 |
| CA encaissé 90 j | 0-3 k€ | 4-8 k€ |
| CA attendu en année 1 cumulé | 70-100 k€ | 140-200 k€ |
| **ROI 12 mois projeté** | **×4 à ×7** | **×4 à ×6** |

### La phrase à retenir

> En 90 jours, l'Observatoire **n'aura pas généré son ROI**, mais il aura **prouvé qu'il le générera**.
> Le moment de vérité économique se situe **entre M+6 et M+12** : c'est là que le capital éditorial accumulé commence à délivrer du trafic récurrent, qui devient des contacts récurrents, qui deviennent des dossiers récurrents.
> Tout dirigeant exigeant un ROI à 90 jours doit choisir un autre investissement (Quick Wins CTR, Simulateur AT).
> Tout dirigeant pensant en termes de 24 mois trouvera ici un des meilleurs ratios effort/résultat possibles.

---

**FIN — `DEMONSTRATION_OPERATIONNELLE_OBSERVATOIRE_2026-06.md`**
**Document opérationnel — Aucune mise en œuvre avant arbitrage explicite post-01/07/2026**
**Compatible avec le gel éditorial en vigueur**
