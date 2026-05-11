# HUB SIMULATEUR — BLUEPRINT D'ARCHITECTURE
*Document de préparation — Mode preview uniquement — Date: 2026-02-11*

---

## 🎯 Objectif

Préparer l'activation d'une architecture **topic cluster** (hub + spokes) autour des simulateurs d'indemnisation, **sans impact production** tant que l'Étape 1 (correction sitemap) n'a pas été validée par les gates de décision SEO à J+21.

---

## 📍 État actuel (J+0)

### Page preview créée
- **Route** : `/simulateur-hub-preview`
- **Fichier** : `/app/frontend/src/pages/SimulateurHubPreviewPage.jsx`
- **Statut** : Visible uniquement par URL directe en preview
- **Protection SEO** :
  - `<meta name="robots" content="noindex, nofollow">`
  - `<link rel="canonical" href="https://strategie-expertise-sante.fr/simulateur">`
  - Absente du sitemap statique ET dynamique
  - Absente de toute navigation (Header / Footer / liens internes)

### Ce qui n'a PAS été touché
- `/simulateur` actuel (préservation des 158 impressions/mois)
- `sitemap.xml` (Étape 1 préservée)
- `robots.txt`
- `Header.jsx` / `Footer.jsx`
- Backend / API
- Aucune route fille créée

---

## 🏗️ Architecture cible (après activation J+21+)

```
/simulateur (HUB d'autorité)
│
├── /simulateur-rente-ipp-accident-travail  (Vague 1 — Priorité P0)
├── /simulateur-rente-maladie-professionnelle  (Vague 1 — Priorité P0)
├── /simulateur-aah-salaire-cumul  (Vague 2 — Priorité P1)
└── /simulateur-rente-ipp-faute-inexcusable  (Vague 2 — Priorité P2)
```

### Règles canonicals (à graver dans le marbre)
| Page | Canonical |
|---|---|
| HUB `/simulateur` | self → `https://strategie-expertise-sante.fr/simulateur` |
| Fille AT/IPP | self → `.../simulateur-rente-ipp-accident-travail` |
| Fille MP | self → `.../simulateur-rente-maladie-professionnelle` |
| Fille AAH | self → `.../simulateur-aah-salaire-cumul` |
| Fille Faute Inexcusable | self → `.../simulateur-rente-ipp-faute-inexcusable` |

**Règle absolue :** chaque fille = canonical auto-référent strict + ≥70 % de contenu unique vs hub.

---

## 📊 Gates de décision SEO (J+14 à J+21)

Avant toute bascule production du HUB, vérifier via Google Search Console :

| Gate | Métrique | Seuil minimum |
|---|---|---|
| Gate 1 | Pages indexées | ≥ 38 / 41 |
| Gate 2 | Pages "détectées non indexées" | ≤ 3 |
| Gate 3 | Sitemap status | "Réussite" sans erreur |
| Gate 4 | Impressions 14 derniers jours | ≥ 1 200 |

**4/4 verts → feu vert HUB activation + Vague 1 (AT + MP)**
**≤ 3/4 verts → diagnostic spécifique avant d'avancer**

---

## 🔄 Procédure de bascule J+21 (étapes futures, non exécutées)

### Étape A — Création des 2 pages filles Vague 1
1. Créer `/app/frontend/src/pages/SimulateurIPPAccidentTravailPage.jsx`
2. Créer `/app/frontend/src/pages/SimulateurMaladieProfessionnellePage.jsx`
3. Ajouter les 2 routes dans `App.js`
4. Chaque page = simulateur fonctionnel complet + contenu juridique 1000+ mots + canonical self
5. Maillage interne : hub → filles + filles → hub

### Étape B — Activation du HUB
1. Renommer `SimulateurHubPreviewPage.jsx` → `SimulateurHubPage.jsx` (ou fusionner avec SimulateurPage.jsx)
2. Retirer `noindex, nofollow`
3. Activer les 4 blocs cliquables (retrait "Bientôt disponible") :
   - Bloc AT → `/simulateur-rente-ipp-accident-travail` ✅
   - Bloc MP → `/simulateur-rente-maladie-professionnelle` ✅
   - Bloc AAH → désactivé (Vague 2) ⏸️
   - Bloc Faute inex. → désactivé (Vague 2) ⏸️
4. Migration de route : `/simulateur` charge désormais le HUB
5. Ajouter au sitemap : `/simulateur-rente-ipp-accident-travail` + `/simulateur-rente-maladie-professionnelle`

### Étape C — Re-soumission GSC
1. Re-soumettre le sitemap
2. "Demander une indexation" sur les 2 nouvelles pages filles
3. Vérifier statut "Découverte" → "Explorée" sous 7 jours

### Étape D — Observation Vague 1 (3 semaines)
Critères de décision Vague 2 (AAH + Faute inex.) :
- Les 2 filles Vague 1 sont indexées
- Hub `/simulateur` ne perd PAS >30% de ses impressions historiques
- Aucune nouvelle page "détectée non indexée"

### Étape E — Vague 2 (J+42+)
Mêmes étapes A → D pour AAH + Faute inexcusable.

---

## 🧩 Contenu rédigé (prêt à activer)

### H1 final
> Simulateurs d'indemnisation : IPP, AAH, accident du travail

### Mini-simulateur Light — Formules
| Type | Formule |
|---|---|
| AT (taux ≥ 10%) | Rente annuelle = Salaire annuel × (Taux IPP / 2) |
| AT (taux < 10%) | Capital = Salaire annuel × Taux IPP × 0,4 (indicatif) |
| MP | Identique AT (régime équivalent) |
| AAH | Maximum mensuel 2026 = 1 041,59 € − (revenus mensuels × 0,8) |

### FAQ (5 questions, ~1000 mots cumulés)
Voir code source de `SimulateurHubPreviewPage.jsx`.

---

## ⚠️ Risques identifiés et atténuations

| Risque | Atténuation |
|---|---|
| Google découvre l'URL preview | `noindex, nofollow` + canonical strict + sitemap propre |
| Duplicate content avec `/simulateur` | Canonical pointe vers `/simulateur` |
| Cannibalisation à l'activation | Filles avec ≥70% contenu unique + ancres internes distinctes |
| Perte d'autorité à la bascule J+21 | Hub conservera mini-simu (intention transactionnelle préservée) |

---

## 📌 Décisions techniques verrouillées

- ✅ Mini-simu = 3 champs (type + taux + salaire), calcul JS local, aucune API
- ✅ 4 blocs désaturés `opacity-60`, `pointer-events-none`, badge amber "Bientôt disponible"
- ✅ Style cohérent : dark + accents amber, identique au reste du site
- ✅ Schemas JSON-LD : `FAQPage` + `BreadcrumbList`
- ✅ data-testid sur tous les éléments interactifs
- ✅ Aucune entrée Header/Footer

---

## ✅ Checklist d'activation (à cocher au jour J+21)

- [ ] Gates SEO 1-4 vertes
- [ ] Cache Cloudflare purgé
- [ ] 2 pages filles Vague 1 codées et testées
- [ ] HUB remplace `/simulateur` (ou route bascule)
- [ ] `noindex, nofollow` RETIRÉ
- [ ] Sitemap mis à jour (+2 URLs)
- [ ] Re-soumission GSC effectuée
- [ ] Microsoft Clarity activé sur HUB + 2 filles
- [ ] Monitoring backend (OOM + queue Dossier Express) actif
