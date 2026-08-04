# Préparation P2-1 — Cluster RSDAE (2 articles) — LECTURE SEULE
Créé le 2026-08-04. AUCUN code, AUCUNE rédaction avant validation utilisateur.

## 1. État des lieux GSC (source : audit CTR 2026-05-30 — données à rafraîchir)
| Requête | Impr. | Pos. | Page qui capte actuellement |
|---|---|---|---|
| rsdae (cumul) | 25+ | variée | dispersé (calculatrice-aah, guides refus) |
| rsdae | 9 | 14,7 | /calculatrice-aah (page non dédiée) |
| rsdae mdph | 4 | 16,7 | /guide/refus-mdph-aah-que-faire |
| rsdae aah | 1 | 1 (1 clic) | /guide/refus-mdph-aah-que-faire |

Diagnostic : demande réelle sur le concept RSDAE, mais AUCUNE page dédiée à l'intention définitionnelle → les impressions se dispersent sur des pages de refus/calcul. Opportunité : consolider avec 2 pages dédiées.

## 2. Actifs existants (anti-cannibalisation)
- `/guide/refus-aah-rsdae-non-reconnue` (P0, existant) → intention REFUS/RECOURS ("refus AAH RSDAE", RAPO). NE PAS chevaucher.
- `/guide/refus-mdph-aah-que-faire` → refus MDPH générique.
- `/calculatrice-aah` → simulation (capte "rsdae" par défaut, à rediriger via maillage).
- `/mdph` (pilier) → parcours MDPH global.

## 3. Article 1 — Page de référence du concept (intention informationnelle)
- **Slug proposé** : `/guide/rsdae-definition-criteres-aah`
- **Intention** : "rsdae", "rsdae définition", "rsdae c'est quoi", "rsdae mdph", "restriction substantielle et durable d'accès à l'emploi" — comprendre le critère qui conditionne l'AAH à taux 50-79 %.
- **Conversion** : lecteur en préparation de dossier AAH → CTA Dossier Express "Faire analyser mon dossier avant dépôt" + calculatrice AAH.
- **Titles (3 variantes)** :
  - V1 : `RSDAE : définition, critères MDPH et impact sur l'AAH` (54)
  - V2 : `RSDAE (AAH 50-79 %) : définition, critères, preuves` (51)
  - V3 : `RSDAE : la condition clé de l'AAH — définition et critères` (58)
- **H1 proposé** : `RSDAE : la condition qui décide de votre AAH entre 50 et 79 % d'incapacité`
- **Structure** :
  - Réponse rapide (candidate featured snippet : définition en 3 phrases)
  - H2 Définition légale (art. L.821-2 CSS, D.821-1-2 CSS)
  - H2 Les critères d'appréciation par la CDAPH (H3 substantielle / H3 durable ≥ 1 an / H3 non compensable par aménagements)
  - H2 RSDAE vs inaptitude vs invalidité (tableau comparatif)
  - H2 Comment la démontrer dans le dossier (certificat Cerfa + projet de vie + pièces)
  - H2 Cas concret anonymisé
  - H2 FAQ (5 Q/R, schema FAQPage)
  - CTA + bloc "Pour aller plus loin"

## 4. Article 2 — Angle conversion (intention anxiogène → forte conversion)
- **Slug proposé** : `/guide/rsdae-travail-mi-temps-aah`
- **Intention** : "rsdae et travail", "travailler avec aah rsdae", "aah mi-temps", "esat rsdae" — peur de perdre l'AAH en travaillant ; motif de refus fréquent ("apte à un mi-temps").
- **Conversion** : la plus forte du cluster — lecteur en risque de refus/suspension → CTA Dossier Express.
- **Titles (3 variantes)** :
  - V1 : `RSDAE et travail : peut-on travailler sans perdre l'AAH ?` (56)
  - V2 : `AAH et emploi : le mi-temps exclut-il la RSDAE ?` (47)
  - V3 : `Travailler avec l'AAH : mi-temps, ESAT et RSDAE` (47)
- **H1 proposé** : `RSDAE et travail : ce que dit vraiment le droit sur l'AAH et l'emploi`
- **Structure** :
  - Réponse rapide (le travail n'exclut PAS automatiquement la RSDAE — D.821-1-2 : mi-temps en milieu ordinaire compatible s'il résulte du handicap)
  - H2 Le principe légal (temps de travail < mi-temps / ESAT)
  - H2 Les 3 situations types (H3 milieu ordinaire mi-temps / H3 ESAT / H3 reprise après refus)
  - H2 Le piège des notifications ("votre handicap n'interdit pas un emploi")
  - H2 Sécuriser son dossier (pièces, formulations projet de vie)
  - H2 Cas concret + H2 FAQ (schema FAQPage)
  - CTA + ressources

## 5. Maillage prévu
Entrants (à créer lors de l'implémentation, hors pages gelées) :
- /mdph (section AAH) → Article 1
- /calculatrice-aah (mention RSDAE existante) → Article 1
- /guide/refus-aah-rsdae-non-reconnue → Article 1 ("comprendre la RSDAE") + Article 2
- /guide/refus-mdph-aah-que-faire → Article 1
- Article 1 ↔ Article 2 (liens croisés)
Sortants :
- Articles 1 et 2 → /guide/refus-aah-rsdae-non-reconnue (si refus), /calculatrice-aah, /dossier-express (CTA), /mdph
Répartition d'intentions (aucun chevauchement) : définition (A1) / travail-emploi (A2) / refus-recours (existant).

## 6. Pré-requis avant rédaction
1. Validation utilisateur : choix des titles (V1/V2/V3) et des slugs pour chaque article.
2. RECOMMANDÉ : export GSC frais filtré "rsdae" (16 mois, requêtes + pages) pour affiner — les données ci-dessus datent du 30/05.
3. Implémentation type : seed backend (seed_seo_pages.py) + sitemap, comme les guides existants. Pages gelées NON touchées (les liens entrants viennent de pages non gelées).

## 7. Cadence proposée
- Semaine du 2026-08-10 : rédaction + preview des 2 articles RSDAE (= 2 pages SEO/semaine) après validation du présent plan.
- En attente (décision utilisateur) : SSR (observation), Lot B /dossier-express (après J+28), fille MDPH (après données GSC).

## ARBITRAGES UTILISATEUR (2026-08-04) — PLAN VALIDÉ
- Article 1 Title: V1 « RSDAE : définition, critères MDPH et impact sur l'AAH » (50-79 %, preuves, critères -> H2/H3)
- Article 2 Title: V1 « RSDAE et travail : peut-on travailler sans perdre l'AAH ? » (ESAT/mi-temps -> sous-sections)
- Slugs validés tels quels. A1 = référence cluster, A2 = intention/conversion, lien croisé, zéro chevauchement avec /guide/refus-aah-rsdae-non-reconnue
- BLOQUANT: NE PAS RÉDIGER avant analyse de l'export GSC « rsdae » que l'utilisateur va fournir
- Étape suivante après export: plan Hn détaillé + maillage exact soumis à validation AVANT rédaction finale
