# JOURNAL DES MODIFICATIONS SEO — PHASE 1
**Date d'exécution : 06/08/2026 — GO utilisateur reçu le 06/08/2026**
**Périmètre : maillage interne, hubs outils, accueil, footer, médecin-conseil, propreté technique.**
**Exclusions respectées : /dossier-express, /expertise-medicale, /expertise-medicale/assureur non modifiées ; pas de cible de lien vers les pages gelées depuis les guides ; pas de page « Invalidité ».**
**Note d'écart assumé (P3/P4, sur ordre explicite)** : l'accueil et le footer contiennent un lien vers /expertise-medicale (listée dans l'ordre P3/P4). Le contenu de la page gelée reste inchangé.

---

## P1 — Maillage interne des 17 guides
**Mécanisme** : migration versionnée idempotente `2026-08-06-phase1-maillage-guides` (utils/seo_migrations.py), appliquée au démarrage, compatible preview + production, aucun écrasement (le champ `content.maillage` était vide sur les 17 guides).
**Rendu** : section « Pour aller plus loin » en bas de chaque guide (template étendu pour supporter les liens vers piliers/outils en plus des guides).
**Objectif SEO** : transformer 17 pages orphelines (0 lien entrant/sortant contextuel) en réseau transmettant l'autorité aux piliers et outils.
**Impact attendu** : +30-60 % de clics sur les guides sous 2-3 mois ; remontée des requêtes en position 5-20.

### Carte Guide → Cocon → Liens ajoutés (source → cible | ancre | justification)
| # | Guide source | Cocon | Cibles (ancres descriptives) |
|---|---|---|---|
| 1 | refus-mdph-aah-que-faire | MDPH/AAH | refus-aah-rsdae (« Refus AAH pour RSDAE non reconnue… »), rqth-strategic, pôle-social, /mdph, /calculatrice-aah — justif : 1 550 imp pos 16, doit irriguer et être irrigué par le cocon MDPH |
| 2 | taux-ipp-5-pourcent-contester | IPP | rente-AT-calcul, ipp-FPH, expertise-defavorable, /calculatrice-ipp — justif : relier la contestation IPP au simulateur (46 % des clics) |
| 3 | expertise-medicale-defavorable-recours | Expertise méd. | preparer-expertise, taux-ipp-5, pôle-social, /medecin-conseil — justif : pilier /expertise-medicale gelé → /medecin-conseil en cible relais jusqu'à J+28 |
| 4 | accident-travail-non-declare-employeur | AT | faute-inexcusable, rente-AT, pôle-social, /accident-travail-maladie-professionnelle |
| 5 | refus-maladie-professionnelle-cpam-recours | MP | reconnaitre-MP, delai-prescription, pôle-social, pilier AT/MP — justif : 37 clics à redistribuer |
| 6 | faute-inexcusable-employeur | AT | AT-non-declare, rente-AT, pôle-social, pilier AT/MP, /calculatrice-ipp — justif : 690 imp pos 9, sous-pilier en devenir |
| 7 | inaptitude-travail-droits-recours | AT/MDPH | refus-MP-cpam, rqth, pilier AT/MP, /mdph |
| 8 | rente-accident-travail-calcul-contestation | IPP/AT | taux-ipp-5, faute-inexcusable, /calculatrice-ipp, pilier AT/MP |
| 9 | recours-tribunal-judiciaire-pole-social | TRANSVERSAL | refus-MP-cpam, refus-mdph-aah, expertise-defavorable, faute-inexcusable, pilier AT/MP, /mdph — justif : 166 clics = pont d'autorité vers tous les cocons |
| 10 | delai-prescription-maladie-professionnelle | MP | reconnaitre-MP, refus-MP-cpam, pilier AT/MP |
| 11 | comment-preparer-expertise-medicale | Expertise méd. | expertise-defavorable, taux-ipp-5, /medecin-conseil, /calculatrice-ipp — justif : pos 37, a besoin de liens entrants (reçus de #3, #15) et sortants |
| 12 | comment-demander-rqth-strategic | MDPH | refus-mdph-aah, refus-aah-rsdae, /mdph, /calculatrice-aah |
| 13 | comment-faire-reconnaitre-maladie-professionnelle | MP | delai-prescription, refus-MP-cpam, MP-definition, pilier AT/MP |
| 14 | maladie-professionnelle-definition-droits | MP | reconnaitre-MP, refus-MP-cpam, pilier AT/MP — justif : pos 33,7, fusion prévue Phase 2 |
| 15 | ptia-definition-droits-strategie | Assurance | preparer-expertise, expertise-defavorable, /protection-juridique — justif : pos 92, orphelin raccroché au cocon assurance |
| 16 | refus-aah-rsdae-non-reconnue | MDPH | refus-mdph-aah, rqth, pôle-social, /mdph, /calculatrice-aah — justif : préfigure le cluster RSDAE |
| 17 | ipp-fonction-publique-hospitaliere | IPP | taux-ipp-5, rente-AT, /calculatrice-ipp |

## P2 — Calculatrices en hubs
| URL | Modification | Objectif | Impact attendu |
|---|---|---|---|
| /calculatrice-ipp | Bloc « Approfondir » : 6 liens (pilier AT/MP + 5 guides IPP/AT/pôle social). Aucun CTA commercial ajouté (1 seul CTA Dossier Express conservé, placé après l'information) | Redistribuer l'autorité de la page n°1 (46 % des clics) | Remontée du cocon IPP/AT |
| /calculatrice-aah | Bloc « Approfondir » : /mdph + 3 guides AAH/RQTH. CTA existant inchangé | Alimenter le cocon MDPH (128 requêtes pos 20,8) | Remontée « refus mdph aah » |
| /simulateur | Bloc « Comprendre vos droits avant de simuler » : 6 liens (2 outils, 2 piliers, 2 guides) | Hub d'orientation qui distribue | Répartition « simulateur ipp » |

## P3 — Accueil
| Élément | Avant | Après | Objectif |
|---|---|---|---|
| Title | « Accueil \| S.E.S. » | « Accident du travail, maladie professionnelle & expertise médicale : défendre vos droits » | Signal thématique de la page la plus forte |
| Meta description | générique | orientée intentions (reconnaître, contester, calculer, obtenir) | CTR |
| H1 | « Vous n'êtes plus seul face à votre dossier, vos droits ou vos recours » | « Vous n'êtes plus seul face à un accident du travail, une maladie professionnelle ou une expertise médicale » | Mots-clés dans le H1 en conservant la signature émotionnelle et le design (zone hero validée 01/04 : structure/classes inchangées, seul le texte évolue sur ordre P3 explicite) |
| Section | — | Nouvelle section « Domaines d'intervention » : 6 cartes → pilier AT/MP (×2 ancres AT et MP), /expertise-medicale, /calculatrice-ipp, /mdph, /guides-pratiques | Liens descendants accueil → piliers |

## P4 — Footer & navigation
| Élément | Modification | Objectif |
|---|---|---|
| Footer | Nouvelle colonne « Vos droits » : pilier AT/MP (ancre complète), /expertise-medicale, /calculatrice-ipp (« Calcul IPP & rente »), /mdph (« MDPH & AAH »), guide reconnaître-MP, /protection-juridique | Liens sitewide vers les piliers (absents avant) |
| Footer | Ancre « Choisir son médecin conseil » → « Médecin conseil CPAM » | Alignement intention |
| Header | Ancre « AT / MP » → « Accident du travail & maladie professionnelle » | Signal sémantique sitewide |
| Écart volontaire | 1 seul lien footer pour AT+MP (page unique jusqu'à la scission Phase 2) : deux ancres différentes vers la même URL n'apportent rien (Google ne retient que la première) | Efficacité |

## P5 — /medecin-conseil (MÉTHODE ADDITIVE)
| Élément | Modification |
|---|---|
| Title | « …erreurs à éviter et comment se préparer » → « Médecin conseil CPAM : rôle, convocation, avis et recours » |
| H1 | « Choisir le bon médecin conseil… » → « Médecin conseil CPAM ou médecin conseil de victime : comprendre les rôles, défendre votre indemnisation » (pont entre les 2 intentions) |
| Contenu | AJOUT (aucune suppression) : section informationnelle 4 blocs (rôle, convocation, portée de l'avis, recours) juste après le hero, avec 3 liens internes (calculatrice-ipp, guide pôle social, guide expertise défavorable). Sections commerciales existantes intégralement conservées après l'information |
| Justification | 1 803 imp CTR 0,61 % pos 14,6 ; cluster « médecin conseil cpam » ≈ 500 imp pos 12-15 |
| Impact attendu | CTR ×3-5, entrée top 10 du cluster CPAM |

## P6 — Propreté technique
| Action | Détail |
|---|---|
| /api/sitemap.xml | Header `X-Robots-Tag: noindex` ajouté (était indexé pos 27) |
| Rendu Googlebot | Vérifié post-modification |

## Suivi GSC (côté utilisateur)
Requêtes témoins à surveiller : « refus mdph aah », « médecin conseil cpam », « simulateur rente maladie professionnelle », « faute inexcusable », « calcul rente ipp accident du travail », « expertise médicale » (position), « maladie professionnelle » (position).
Date de référence avant/après : **06/08/2026** (préview) — date de déploiement production à consigner.
