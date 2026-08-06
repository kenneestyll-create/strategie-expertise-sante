# AUDIT SEO COMPLET — strategie-expertise-sante.fr
**Date : 06/08/2026 — Données : GSC 6 mois (806 clics, 26 139 impressions) + crawl production + analyse du code source + maillage interne + SERP**

---

## 1. VERDICT SUR L'HYPOTHÈSE

**L'hypothèse est VALIDÉE à 90 %, avec une correction importante.**

| Hypothèse émise | Verdict | Preuve chiffrée |
|---|---|---|
| Les mots-clés principaux sont répartis sur trop de pages | ✅ VRAI | 5 pages se partagent l'intention « expertise médicale », 6 pages l'intention « maladie professionnelle », 5+ l'intention « IPP » |
| Google n'identifie pas les pages d'autorité | ✅ VRAI | Les 5 pages piliers = **3,5 % des clics** (28/806). « expertise médicale » → pos. 61, « maladie professionnelle » → pos. 73, « ptia » → pos. 92 |
| Cannibalisation | ✅ VRAI (partielle) | Détail §5 — surtout dilution : aucune page n'est assez forte pour ranker, plutôt que 2 pages qui alternent |
| Le maillage ne concentre pas l'autorité | ✅ VRAI — c'est le problème n°1 | La page la plus liée du site est **/contact (13 liens contextuels)**. Les 17 guides ont **0 lien contextuel entrant et 0 sortant**. /accident-travail-maladie-professionnelle reçoit **0 lien contextuel** |
| Pages commerciales brouillent les signaux | ⚠️ PARTIEL | Elles captent l'autorité interne (contact/agenda/dossier-express = cibles n°1-2-3 du maillage) mais ne cannibalisent pas les SERP |
| ❌ Correction : « problème technique SPA » | FAUX | Le rendu dynamique pour Googlebot fonctionne (HTML complet 77-150 Ko servi aux bots, titles/H1 corrects). La base technique est saine |

**Le site n'a pas un problème de contenu ni de technique : il a un problème d'architecture de l'autorité.** Google voit un site dont les pages fortes (outils) ne transmettent rien, dont les guides sont orphelins, et dont les pages piliers sont des impasses.

---

## 2. RADIOGRAPHIE DU TRAFIC RÉEL (GSC 6 mois)

### Répartition par type de page
| Type | Clics | % clics | Impressions | Constat |
|---|---|---|---|---|
| Outils (calculatrices/simulateurs) | 422 | **52,4 %** | 10 279 | Le vrai moteur du site |
| Guides (17) | 298 | **37,0 %** | 11 921 | 2e moteur, mais 3 guides font 80 % de ces clics |
| Pages piliers (5) | 28 | **3,5 %** | 2 707 | ÉCHEC — censées porter l'autorité |
| Pages commerciales | 10 | 1,2 % | 506 | Normal (pas leur rôle) |

### Top pages
| Page | Clics | Imp. | Pos. |
|---|---|---|---|
| /calculatrice-ipp | 370 (46 %) | 8 442 | 7,4 |
| /guide/recours-tribunal-judiciaire-pole-social | 166 (21 %) | 5 024 | 9,5 |
| /simulateur | 41 | 989 | 10,1 |
| /guide/refus-aah-rsdae-non-reconnue | 38 | 1 439 | 8,2 |
| /guide/refus-maladie-professionnelle-cpam-recours | 37 | 1 151 | 10,6 |
| **/medecin-conseil** | 11 | **1 803** | 14,6 — CTR 0,61 % : énorme potentiel gâché |

### Position réelle sur les requêtes stratégiques (têtes de cluster)
| Requête | Position | Impressions | Verdict |
|---|---|---|---|
| « ipp » / « crrmp » / « simulation ipp 2026 » | 1-3 | faibles | Seules victoires head-terms |
| « expertise médicale » | **61** | 77 | Invisible malgré page pilier dédiée |
| « maladie professionnelle » | **73** | 16 | Invisible |
| « médecin conseil » | 23-24 | 102 | Page 3 |
| « faute inexcusable » | **38** | 7 | Guide seul, sans soutien |
| « ptia » | **92** | 29 | Guide orphelin |
| « accident du travail » | **ABSENT** | 0 | Aucune impression |
| « invalidité » / « pension invalidité » | **ABSENT** | 0 | Aucun contenu dédié |
| « consolidation » / « rechute » | **ABSENT** | 0 | Aucun contenu dédié |
| « assurance emprunteur » | **ABSENT** | 0 | Aucun contenu dédié |

### Répartition thématique des requêtes (485 requêtes visibles)
| Thème | Req. | Clics | Imp. | Pos. moyenne |
|---|---|---|---|---|
| IPP / rente / simulateur | 95 | 156 | 5 606 | 8,3 ✅ |
| Accident du travail (longue traîne) | 25 | 54 | 1 665 | 7,9 ✅ |
| Pôle social / tribunal | 43 | 19 | 1 165 | 14,4 ⚠️ |
| RSDAE / AAH / MDPH | 128 | 16 | 1 059 | 20,8 ❌ (128 requêtes = demande énorme, position mauvaise) |
| Maladie professionnelle | 66 | 4 | 625 | 18,6 ❌ |
| **Expertise médicale** | 27 | **0** | 571 | 24,4 ❌ cœur de métier, zéro clic |
| Médecin conseil | 48 | 2 | 497 | 18,2 ❌ |
| Faute inexcusable | 15 | 5 | 366 | 9,3 ⚠️ |
| Assurance / PTIA / emprunteur | 16 | 0 | 104 | 47,9 ❌ |
| Invalidité | 3 | 0 | 3 | 34 ❌ |
| Consolidation / rechute | 3 | 0 | 3 | 56 ❌ |

---

## 3. AUDIT DU MAILLAGE INTERNE — LE PROBLÈME N°1

### 3.1 Liens contextuels entrants (hors header/footer) mesurés dans le code
| Page cible | Liens reçus | Commentaire |
|---|---|---|
| /contact | **13** | La page la plus « autoritaire » du site est… le formulaire de contact |
| /dossier-express | 4 | Commercial |
| /agenda | 4 | Commercial |
| /simulateur | 3 | |
| /medecin-conseil | 3 | |
| /calculatrice-ipp | **2** | La page qui fait 46 % des clics reçoit 2 liens |
| /expertise-medicale | **1** | Reçu de sa propre page fille |
| /accident-travail-maladie-professionnelle | **0** | Page pilier totalement isolée |
| /mdph | 1 | |
| **Chacun des 17 guides** | **0** | Orphelins — uniquement listés sur /guides-pratiques |

### 3.2 Liens sortants des guides : **ZÉRO**
Les 17 guides (37 % des clics, 45,6 % des impressions) ne contiennent **aucun lien interne** : ni vers un pilier, ni vers un autre guide, ni vers un outil. L'autorité qu'ils captent de Google **s'évapore**. C'est la plus grosse fuite d'autorité du site.

### 3.3 Ancres
- Header : « AT / MP » comme ancre vers la page accident du travail → **signal sémantique nul** pour Google.
- Ancres génériques dominantes : « Contact », « En savoir plus », « Voir tous les guides ».
- Aucune ancre exact-match « maladie professionnelle », « taux IPP », « expertise médicale » dans le maillage contextuel.

### 3.4 Profondeur de clics
| Page | Profondeur | Problème |
|---|---|---|
| Piliers | 2 (via dropdown menu) | OK mais dropdown = lien faible |
| Outils | 2 (dropdown + footer) | OK |
| **Guides** | **3** (Accueil → footer → /guides-pratiques → guide) | Trop profond pour des pages qui font 37 % des clics |
| /expertise-medicale/assureur | 3 | 1 seul chemin d'accès |

### 3.5 Où va l'autorité aujourd'hui (carte actuelle)
```
                 ┌────────────── ACCUEIL (title « Accueil » !) ──────────────┐
                 │ H1 : « Vous n'êtes plus seul » (0 mot-clé)                │
                 └──── liens vers : contact, dossier-express, simulateur ────┘
                                        │
     header dropdown (ancres faibles)   │   footer (13 liens, dont admin!)
        │                               ▼
   5 PILIERS  ──────────────────►  /contact (13 liens = page la plus liée)
   (3,5 % des clics,                /agenda, /dossier-express
    quasi 0 lien entrant,
    sortants → contact)
        ✗ aucun lien vers les guides
        ✗ aucun lien vers les outils (sauf medecin-conseil→simulateur)

   17 GUIDES (37 % des clics)          OUTILS (52 % des clics)
   ────────────────────────           ─────────────────────────
   0 lien entrant contextuel          2 liens entrants (calculatrice-ipp)
   0 lien sortant                     sortants → agenda, contact, dossier-express
   profondeur 3                       ✗ aucun lien vers guides ni piliers
   = 17 impasses SEO                  = l'autorité des 8 442 imp. part vers /contact
```

---

## 4. AUDIT TITLE / H1 / INTENTIONS

| Page | Title | H1 | Diagnostic |
|---|---|---|---|
| / | « Accueil \| Stratégie & Expertise Santé » | « Vous n'êtes plus seul » | ❌ La page la plus puissante du site ne cible AUCUN mot-clé |
| /expertise-medicale | « Expertise Médicale : Stratégie Assureur, MDPH, Tribunal » | cohérent | ✅ Bon — mais 0 soutien de maillage |
| /accident-travail-maladie-professionnelle | « Accident du travail et maladie professionnelle : droits et recours » | idem | ⚠️ **2 intentions majeures sur 1 page** = dilution structurelle. Google ne peut pas en faire l'autorité ni de l'un ni de l'autre |
| /medecin-conseil | — | « Choisir le bon médecin conseil… » | ⚠️ 1 803 imp, CTR 0,61 % : intention mal alignée. Les requêtes réelles sont « médecin conseil **CPAM** » (247 imp cumulées) = intention info/défense, pas « choisir son médecin conseil » (intention achat) |
| /calculatrice-ipp | « Simulateur Rente IPP 2026 : Calcul + Contestation » | cohérent | ✅ La meilleure page du site |
| /tarifs | — | « Un accompagnement progressif… » | ❌ 0 mot-clé |
| /guides-pratiques | — | « Guides pratiques » | ❌ Hub sans sémantique, sans catégorisation thématique |
| Guides (17) | corrects individuellement | corrects | ✅ Titles bien construits — le problème n'est pas là |

---

## 5. CANNIBALISATION & DILUTION SÉMANTIQUE

### Cluster « Expertise médicale » — 5 pages en concurrence, résultat : pos. 61
- /expertise-medicale (pilier, pos. 13 sur ses requêtes)
- /expertise-medicale/assureur (« stratégie expertise médicale assureur » 293 imp, pos 12,6, 0 clic)
- /guide/comment-preparer-expertise-medicale (pos. moyenne **37**)
- /guide/expertise-medicale-defavorable-recours (pos. 8,2 mais 32 imp)
- /medecin-conseil (sémantiquement adjacent)
→ **Aucune ne se lie aux autres.** 5 signaux faibles au lieu d'1 signal fort.

### Cluster « Maladie professionnelle » — 6 pages, résultat : pos. 73
- /accident-travail-maladie-professionnelle (pilier bicéphale)
- /guide/maladie-professionnelle-definition-droits (pos. **33,7** — le guide "définition" est enterré)
- /guide/comment-faire-reconnaitre-maladie-professionnelle (pos. 8,8, 82 imp seulement)
- /guide/refus-maladie-professionnelle-cpam-recours (37 clics — le seul qui marche)
- /guide/delai-prescription-maladie-professionnelle (pos. 7,2 ✅)
- /guide/rente-accident-travail-calcul-contestation
→ Cannibalisation directe entre « definition-droits » et le pilier : mêmes intentions « maladie professionnelle définition/droits », les deux entre pos. 18 et 34.

### Cluster « MDPH / AAH / RSDAE » — 128 requêtes, pos. moyenne 20,8
- /mdph (pilier faible, pos. 12, 231 imp)
- /guide/refus-mdph-aah-que-faire (pos. **16,25** sur 1 550 imp — 1er potentiel inexploité du site)
- /guide/refus-aah-rsdae-non-reconnue (pos. 8,2 ✅)
- /calculatrice-aah (pos. 9,4)
- /guide/comment-demander-rqth-strategic
→ « refus mdph » pos. 38, « dossier mdph refusé » pos. 41, « recours mdph refus aah » pos. 36 : Google hésite entre 3 pages, aucune ne gagne.

### Cluster « IPP » — force réelle mais éclatée
- /calculatrice-ipp ✅ (pos. 7,4) + /simulateur (pos. 10,1) + /guide/taux-ipp-5-pourcent-contester + /guide/rente-accident-travail-calcul-contestation + /guide/ipp-fonction-publique-hospitaliere
→ Pas de cannibalisation grave (intentions distinctes) mais **aucun hub « IPP » éditorial** ne fédère : « calcul ipp maladie professionnelle » (20 imp, pos 10), « calcul rente ipp accident du travail » (35 imp, pos 10,3) frappent à la porte sans soutien.

### Duplications techniques mineures
- Version **http://** indexée séparément (5 clics, pos. 1) → redirection 301 présente, OK, mais GSC la voit encore.
- **/api/sitemap.xml indexé** dans les résultats (27e) → à passer en `noindex` / X-Robots-Tag.
- /simulateur vs /calculatrice-ipp : « simulateur ipp » se répartit entre les deux.

---

## 6. CONCURRENTS QUI GAGNENT ET POURQUOI

| Concurrent | Où il nous bat | Pourquoi précisément |
|---|---|---|
| **previssima.fr** | simulateur rente IPP (pos. 1-3) | Page outil dédiée exact-match + site à forte autorité (10k+ pages retraite/santé), maillage massif entre fiches |
| **point-secu.com** | simulateur IPP, AT/MP | Cocon complet AT → IPP → rente : chaque page soutient les autres |
| **avf.fr** (Assoc. victimes) | indemnisation MP/AT | E-E-A-T associatif + arborescence /accident-maladie-travail/simulateur/… = silo sémantique parfait |
| **juritravail.com, reassurez-moi.fr** | expertise médicale contestation | Guides pratiques + autorité de domaine + pages « intention exacte » (refuser / contester / contre-expertise) |
| **Cabinets d'avocats** (barges-avocat, domcorp, caporale, jmp) | expertise médicale défavorable, faute inexcusable | E-E-A-T « avocat » + 1 page = 1 intention + jurisprudence citée |
| **ameli.fr / service-public.gouv.fr** | tous les head-terms (« maladie professionnelle », « accident du travail ») | Autorité étatique inatteignable → **ne pas viser le head-term sec, viser le mid-tail « intention »** (refus, recours, contestation, calcul, délais) |
| **macalculatriceenligne.com / calcunet.fr** | calcul taux IPP | Pure players outils, itèrent vite sur les variantes de requêtes |

**Leçon** : tous les gagnants ont soit un E-E-A-T fort, soit un cocon sémantique dense. Nous n'avons ni signal E-E-A-T structuré (pas de page auteur, pas de schema Person/Organization complet), ni cocon (0 lien entre nos pages).

---

## 7. ARCHITECTURE SEO IDÉALE — 6 COCONS

**Principe : 1 cocon = 1 page pilier (hub) + 4-8 pages satellites (guides/outils) + maillage bidirectionnel systématique avec ancres exact-match. Les outils deviennent des aimants qui redistribuent vers les piliers.**

```
ACCUEIL (title réécrit : « Expertise médicale & maladie professionnelle : défendre vos droits »)
│
├── COCON 1 : MALADIE PROFESSIONNELLE (pilier À CRÉER : /maladie-professionnelle)
│     ├── guide/comment-faire-reconnaitre-maladie-professionnelle
│     ├── guide/refus-maladie-professionnelle-cpam-recours  ★ 37 clics
│     ├── guide/delai-prescription-maladie-professionnelle
│     ├── guide/maladie-professionnelle-definition-droits (à FUSIONNER dans le pilier)
│     ├── [À CRÉER] guide/crrmp-comite-reconnaissance (« crrmp » pos. 1 sur 2 imp = potentiel)
│     └── [À CRÉER] guide/tableau-maladies-professionnelles
│
├── COCON 2 : ACCIDENT DU TRAVAIL (pilier À CRÉER : /accident-du-travail —
│     │        scinder l'actuelle page bicéphale AT/MP)
│     ├── guide/accident-travail-non-declare-employeur
│     ├── guide/rente-accident-travail-calcul-contestation
│     ├── guide/faute-inexcusable-employeur  ★ 690 imp (à renforcer en sous-pilier)
│     ├── [À CRÉER] guide/consolidation-accident-travail (requête absente = terrain vierge)
│     └── [À CRÉER] guide/rechute-accident-travail
│
├── COCON 3 : IPP & INDEMNISATION (pilier À CRÉER : /taux-ipp — hub éditorial)
│     ├── /calculatrice-ipp  ★★ 370 clics — Y AJOUTER des liens sortants vers le cocon
│     ├── /simulateur (repositionné « hub simulateurs », canonical propre)
│     ├── guide/taux-ipp-5-pourcent-contester
│     ├── guide/ipp-fonction-publique-hospitaliere
│     └── [À CRÉER] guide/calcul-rente-ipp-maladie-professionnelle (« simulateur rente MP » 60 imp pos 8,2)
│
├── COCON 4 : EXPERTISE MÉDICALE & MÉDECIN CONSEIL (pilier EXISTANT à renforcer : /expertise-medicale)
│     ├── /expertise-medicale/assureur (293 imp pos 12,6 → gains rapides post-J+28)
│     ├── guide/comment-preparer-expertise-medicale (pos 37 → maillage = pos <15 atteignable)
│     ├── guide/expertise-medicale-defavorable-recours
│     ├── /medecin-conseil (réaligner sur « médecin conseil CPAM » : 247 imp)
│     └── [À CRÉER] guide/contre-expertise-medicale (modèle concurrents avocats)
│
├── COCON 5 : MDPH / AAH / INVALIDITÉ (pilier EXISTANT à renforcer : /mdph + pilier À CRÉER : /invalidite)
│     ├── guide/refus-mdph-aah-que-faire  ★ 1 550 imp pos 16 = 1re opportunité du site
│     ├── guide/refus-aah-rsdae-non-reconnue ★ + [2 articles RSDAE prévus — cluster déjà planifié]
│     ├── /calculatrice-aah
│     ├── guide/comment-demander-rqth-strategic
│     └── [À CRÉER] /invalidite (pension d'invalidité CPAM cat. 1/2/3 — thème 100 % absent,
│           complémentaire de l'IPP, forte demande nationale)
│
└── COCON 6 : ASSURANCE / PTIA / EMPRUNTEUR (pilier À CRÉER : /assurance-emprunteur-sante)
      ├── guide/ptia-definition-droits-strategie (pos 92 → orphelin à raccrocher)
      ├── /protection-juridique
      └── [À CRÉER] guide/refus-assurance-emprunteur-invalidite, guide/ipp-assurance-emprunteur

TRANSVERSAL : guide/recours-tribunal-judiciaire-pole-social ★ 166 clics
  → devient le « pont » cité par TOUS les cocons (recours judiciaire = étape finale commune)
  → lui-même lie vers chaque pilier selon le litige (actuellement : 0 lien)
```

---

## 8. LISTE PRIORISÉE DES ACTIONS

### IMPACT FORT (S1-S4 — quick wins mesurables)
| # | Action | Effort | Impact estimé |
|---|---|---|---|
| 1 | **Injecter le maillage contextuel dans les 17 guides** (3-6 liens/guide : pilier + guides frères + outil, ancres exact-match) | Moyen (données en base `seo_pages`) | +30-60 % de clics guides sous 2-3 mois ; ~1 500 imp. en pos. 5-20 actuellement sans clic |
| 2 | **Ajouter des liens sortants aux 2 outils** (calculatrice-ipp → pilier IPP, guides contestation, guide MP ; calculatrice-aah → mdph, guides AAH) | Faible | Redistribue l'autorité de la page n°1 du site (46 % des clics) vers les cocons |
| 3 | **Réécrire title + H1 de l'accueil** avec les mots-clés cœur | Faible | La page d'accueil transmet enfin un signal thématique |
| 4 | **Corriger l'ancre « AT / MP »** → « Accident du travail & maladie professionnelle » + ajouter les piliers au footer | Faible | Signal sitewide immédiat |
| 5 | **Réaligner /medecin-conseil sur « médecin conseil CPAM »** (title + intro + section dédiée) | Faible | 1 803 imp × CTR 0,6 % → 3 % = ×5 clics |
| 6 | **Renforcer /guide/refus-mdph-aah-que-faire** (contenu + liens entrants depuis mdph, calculatrice-aah, guides AAH) | Moyen | 1 550 imp pos 16 → pos ≤10 = +80-120 clics/6 mois |
| 7 | noindex sur /api/sitemap.xml | Trivial | Propreté |

### IMPACT MOYEN (M2-M3 — restructuration)
| # | Action | Effort |
|---|---|---|
| 8 | **Scinder /accident-travail-maladie-professionnelle en 2 piliers** (/accident-du-travail + /maladie-professionnelle) avec 301 | Fort |
| 9 | **Créer le pilier éditorial /taux-ipp** (hub du cocon 3, lié par calculatrice) | Moyen |
| 10 | Fusionner /guide/maladie-professionnelle-definition-droits dans le pilier MP (301) | Faible |
| 11 | Restructurer /guides-pratiques en hub thématisé (sections par cocon, ancres descriptives) | Moyen |
| 12 | Faire du guide pôle social le « pont transversal » (liens bidirectionnels avec chaque pilier) | Faible |
| 13 | E-E-A-T : page auteur/à-propos renforcée, schema Organization + Person + Article sur les guides, dates de mise à jour visibles | Moyen |
| 14 | Post-J+28 : optimiser /expertise-medicale/assureur (293 imp pos 12,6) + CTA maillage | Faible |

### IMPACT FAIBLE (long terme / entretien)
| # | Action |
|---|---|
| 15 | Créer les contenus absents : /invalidite, consolidation, rechute, CRRMP, assurance emprunteur, contre-expertise |
| 16 | Breadcrumb schema (BreadcrumbList) sur guides + piliers |
| 17 | Surveiller http→https dans GSC (301 déjà en place) |
| 18 | FAQ schema sur les pages outils (rich snippets → CTR) |

---

## 9. LES 20 PAGES À MODIFIER EN PRIORITÉ

1. **/ (accueil)** — title « Accueil » à réécrire, H1 sans mot-clé, ajouter blocs de liens vers les 6 cocons
2. **/calculatrice-ipp** — ajouter 4-6 liens sortants vers cocon IPP/MP/AT (c'est le château d'eau du site)
3. **/guide/refus-mdph-aah-que-faire** — 1 550 imp pos 16 : enrichir + 5 liens entrants
4. **/medecin-conseil** — réalignement intention « CPAM » + maillage vers expertise-medicale
5. **/guide/recours-tribunal-judiciaire-pole-social** — 166 clics : en faire le pont transversal (liens vers/depuis chaque cocon)
6. **/accident-travail-maladie-professionnelle** — scission en 2 piliers
7. **/mdph** — enrichir en vrai pilier hub (128 requêtes du thème, pos 20,8)
8. **/guide/comment-preparer-expertise-medicale** — pos 37 : maillage depuis pilier + réoptimisation
9. **/guide/faute-inexcusable-employeur** — 690 imp pos 9 : enrichir en sous-pilier + liens
10. **/guide/maladie-professionnelle-definition-droits** — fusion dans pilier MP (301)
11. **/guides-pratiques** — hub thématisé par cocon
12. **/simulateur** — clarifier vs calculatrice-ipp + liens sortants
13. **/guide/refus-maladie-professionnelle-cpam-recours** — 37 clics : liens vers pilier MP + CRRMP
14. **/guide/ptia-definition-droits-strategie** — pos 92 : raccrocher au cocon 6 + enrichir
15. **/calculatrice-aah** — liens sortants vers cocon MDPH
16. **/guide/refus-aah-rsdae-non-reconnue** — intégrer au cluster RSDAE prévu
17. **/tarifs** — H1/title avec mots-clés service
18. **Header/Footer** — ancres + ajout piliers manquants au footer
19. **/expertise-medicale** *(post-J+28)* — 3-5 liens sortants vers ses satellites
20. **/expertise-medicale/assureur** *(post-J+28)* — viser pos ≤8 sur « stratégie expertise médicale assureur » (293 imp)

## 10. NOUVELLES PAGES PILIERS
| Page | Statut | Justification GSC |
|---|---|---|
| /maladie-professionnelle | À CRÉER (scission) | 66 requêtes, pos 18,6 — aucune page d'autorité dédiée |
| /accident-du-travail | À CRÉER (scission) | 25 requêtes en longue traîne pos 7,9 mais head-term absent |
| /taux-ipp (hub éditorial) | À CRÉER | 95 requêtes = 1er thème du site, aucun hub éditorial |
| /invalidite | À CRÉER | Thème 100 % absent, adjacent naturel IPP/AAH |
| /assurance-emprunteur-sante | À CRÉER | 16 requêtes pos 47,9, PTIA pos 92 |
| /expertise-medicale | RENFORCER (post-J+28) | Existe mais 1 lien entrant |
| /mdph | RENFORCER | Existe mais faible vs 128 requêtes du thème |

---

## 11. IMPACT GLOBAL QUANTIFIÉ (estimation prudente)
- Base actuelle : ~134 clics/mois.
- Actions impact fort seules (maillage + réalignements, sans nouveau contenu) : **+60-100 % sous 3-4 mois** (~230-270 clics/mois) — essentiellement en déplaçant les ~40 requêtes en position 5-20 qui totalisent ~2 500 imp. sans clic.
- Architecture complète (scissions + piliers + cocons + E-E-A-T) : **×3 à ×5 sous 8-12 mois**, avec le cocon IPP/indemnisation comme locomotive et MDPH/AAH comme 2e moteur.
- Réserve : les head-terms secs (« maladie professionnelle », « accident du travail ») resteront dominés par ameli/service-public — l'objectif réaliste est le top 3 des intentions mid-tail (refus, recours, calcul, contestation, délais).

## 12. CONTRAINTES RESPECTÉES
- Gel SEO J+28 : /dossier-express, /expertise-medicale, /expertise-medicale/assureur exclus de toute modification avant le point de mesure (actions 14, 19, 20 planifiées post-J+28).
- Aucune modification produit Dossier Express.
- Cluster RSDAE : s'insère dans le cocon 5 (déjà planifié, en attente de validation du plan).
