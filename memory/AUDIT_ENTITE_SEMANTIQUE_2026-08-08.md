# AUDIT ENTITÉ & SÉMANTIQUE — Stratégie & Expertise Santé
*08/08/2026 — Audit en lecture seule. AUCUNE modification effectuée (fichiers, textes, balises, schémas, maillage, config). Aucun déploiement.*
*Sources : crawl du site en production (sitemap + statuts HTTP), code source déployé (44 pages React), audit SEO performance du 06/08 réutilisé et re-vérifié post-Phase 1.*

---

## DIAGNOSTIC EN UNE PHRASE

**Google perçoit aujourd'hui Stratégie & Expertise Santé comme un service commercial d'accompagnement et de défense des victimes orienté indemnisation (« défendre vos droits », 94 occurrences d'« indemnisation »), et non comme une structure spécialisée d'analyse et de préparation stratégique de dossiers médico-administratifs intervenant en complément des professionnels — l'écart vient du vocabulaire dominant, de l'absence quasi totale de données structurées d'entité (aucun schéma Organization/WebSite/Person sur la page d'accueil) et d'une identité (fondateur, méthodologie, frontières) racontée émotionnellement mais jamais déclarée formellement aux machines.**

---

## 1. CE QUE GOOGLE COMPREND PROBABLEMENT AUJOURD'HUI

Une plateforme française d'aide aux victimes d'accidents du travail, maladies professionnelles et refus MDPH, qui :
- vend des analyses de dossier assistées par IA (« Dossier Express IA », 97 €) et de l'accompagnement humain ;
- publie des guides pratiques et des calculateurs d'indemnisation (IPP, AAH) ;
- se positionne dans le champ lexical de la **défense des droits** et de l'**indemnisation**.

**Catégorisation spontanée probable : « accompagnement médico-administratif » à coloration commerciale**, dans une zone grise entre l'assistance aux victimes, le juridique et le médical — sans que Google puisse dire précisément QUI est derrière ni OÙ s'arrête son périmètre.

## 2. CE QUE GOOGLE DEVRAIT COMPRENDRE (positionnement cible)

Stratégie & Expertise Santé (marque exploitée par KAPSULES KORPORATION) = **structure spécialisée dans l'analyse et la préparation stratégique de dossiers médico-administratifs complexes**, qui analyse, structure, documente et organise les pièces d'un dossier pour donner à la personne — et si besoin aux professionnels compétents (avocat, médecin-conseil de victime, expert) — une base de travail claire et exploitable. **Ni cabinet médical, ni cabinet d'avocats, ni expert judiciaire, ni organisme officiel, ni organisme d'indemnisation.** Outils propriétaires : Dossier Express IA (produit) et StratégiIA (assistant).

## 3. POURQUOI IL EXISTE UN ÉCART

1. **Vocabulaire dominant inversé** : « indemnisation » (94×), « garantie » (32×), « gain » (25×) écrasent « documentaire » (22×), « chronologie » (5×), « dossier médico-administratif » (2×). Le lexique du positionnement cible existe (« analyse » 285×, « stratégi- » 196×, « structur- » 60×) mais il est dilué dans un cadre narratif de défense/indemnisation.
2. **Zéro déclaration d'entité machine-lisible** : aucune balise JSON-LD sur la home ni dans index.html (0 script ld+json global). Google doit DEVINER qui est SES.
3. **Asymétrie de schémas** : la page /dossier-express porte Organization+Service+Offer alors que la home ne porte RIEN → risque réel que le graphe de connaissance associe l'entité principale à « Dossier Express IA » (le produit) plutôt qu'à SES (l'organisation).
4. **Identité humaine anonyme** : le fondateur est présenté (« Fondateur, Stratégie & Expertise Santé », récit « né d'un combat réel ») mais sans nom, sans schéma Person, sans qualification vérifiable.
5. **Le nom de marque contient « Expertise Santé »** : sans délimitation explicite et répétée, ce mot entretient la confusion avec l'expertise médicale réglementée (87 occurrences d'« expertise médicale » sur le site — légitimes car c'est le sujet traité, mais jamais bornées par une définition d'entité).
6. **La ligne de démarcation réglementaire existe** (disclaimers sur 10 pages) mais elle est défensive et éparse, jamais transformée en **proposition de valeur** (« notre périmètre volontaire = le documentaire et le procédural »).

## 4. LES 10 PROBLÈMES LES PLUS IMPORTANTS

1. Aucun schéma Organization/WebSite sur la page d'accueil (l'entité n'existe pas formellement pour Google).
2. Le produit (Dossier Express IA) est mieux « schématisé » que l'organisation → inversion identitaire potentielle.
3. Schémas médicaux À RISQUE sur /expertise-medicale : `MedicalProcedure`, `MedicalScholarlyArticle`, `PeopleAudience` — le contenu n'est PAS un article médical savant ni une procédure médicale pratiquée par SES ; ces types suggèrent une autorité médicale que SES ne revendique pas (risque YMYL/E-E-A-T inverse).
4. Fondateur anonyme : récit fort mais aucune identité nominative, aucun schéma Person, aucune qualification → plafond de crédibilité E-E-A-T.
5. Title home = « défendre vos droits » : cadre « défense » (proche avocat) au lieu de « analyse et préparation stratégique ».
6. Vocabulaire commercial non borné : « garantie » (32×) est le terme le plus dangereux (interdit de suggérer une garantie de résultat en matière indemnitaire) ; « faire basculer » (1×) à reformuler.
7. La relation aux professionnels (avocats, médecins) est présentée en « réseau de partenaires » mais jamais en « complémentarité de travail » (la base exploitable que SES leur fournit).
8. KAPSULES KORPORATION (exploitant, RCS 824 339 584 Chartres) n'apparaît que dans les mentions légales — lien marque/entité juridique invisible pour le graphe de connaissance.
9. Soft-404 : toute URL inconnue renvoie HTTP 200 avec « Page non trouvée » (SPA) — bruit d'indexation potentiel.
10. /parrainage est indexable mais absent du sitemap et quasiment non maillé (page semi-orpheline) ; « Mon parcours » (title de /a-propos) est un title faible pour LA page d'entité humaine.

## 5. LES 10 AMÉLIORATIONS PRIORITAIRES (proposées, NON appliquées)

1. Ajouter sur la home (et idéalement dans index.html) un JSON-LD `Organization` complet : name, alternateName (SES), legalName (KAPSULES KORPORATION), url, logo, description reprenant MOT POUR MOT le positionnement cible, contactPoint, sameAs, `knowsAbout` (AT/MP, MDPH, expertise médicale, IPP…), et surtout une description qui borne le périmètre.
2. Ajouter `WebSite` (+SearchAction éventuel) sur la home.
3. Requalifier les schémas de /expertise-medicale : remplacer MedicalScholarlyArticle/MedicalProcedure par `Article` + FAQPage (⚠️ page GELÉE jusqu'à fin du gel 28 j — planifier après).
4. Déclarer Dossier Express IA et StratégiIA en `SoftwareApplication`/`Service` avec `provider` → Organization SES (rétablit la hiérarchie produit < organisation).
5. Page /a-propos : nommer le fondateur (décision humaine à prendre), ajouter schéma `Person` (founder de Organization), qualifications réelles, et re-titrer (« Qui est Stratégie & Expertise Santé — méthode et périmètre »).
6. Écrire un paragraphe d'entité canonique (2-3 phrases du positionnement cible) et le placer à l'identique : home (bas de hero ou section « Qui sommes-nous »), /a-propos, footer court — la répétition verbatim est ce qui fixe une entité.
7. Transformer les disclaimers défensifs en section positive « Notre périmètre, volontaire » (home + pages services) : ce que SES fait / ne fait pas / avec qui elle travaille.
8. Purge lexicale ciblée : reformuler « garantie » lorsqu'il ne s'agit pas de garanties contractuelles réelles, supprimer « faire basculer », réduire la densité d'« indemnisation » dans les zones d'identité (hero, titles) tout en la CONSERVANT dans les guides/calculateurs (c'est l'intention de recherche des utilisateurs — ne pas y toucher).
9. Ajouter `BreadcrumbList` sur les guides et pages services (2 pages seulement en ont).
10. Sitemap : ajouter /parrainage et /auto-diagnostic (après déploiement) ; étudier une vraie page 404 (statut ou meta noindex sur l'état « non trouvé »).

---

## 6. ANALYSE DE LA PAGE D'ACCUEIL

- **Title** : « Accident du travail, maladie professionnelle & expertise médicale : défendre vos droits » — efficace en intention de recherche, mais cadre « défense » (registre avocat/victime) et zéro élément d'identité.
- **Meta-description** : « Faire reconnaître un accident du travail…, préparer une expertise médicale, contester… » — verbes d'action utilisateur, pas de définition de SES.
- **H1** : « Vous n'êtes plus seul face à un accident du travail, une maladie professionnelle ou une expertise médicale. » — émotionnel, empathique, très bon pour la conversion, muet pour l'entité.
- **Premier écran** : badge « PIONNIER EN FRANCE — Plateforme d'analyse & d'accompagnement en droits santé » (bon embryon de définition, mais « pionnier » = revendication invérifiable), sous-texte « Analysez votre situation, identifiez vos leviers, comprenez vos droits… accompagnement stratégique humain », CTA « Lancer mon analyse » / « Être accompagné maintenant ».
- **H2 de la page** : « Comprendre et défendre vos droits », « né d'un combat réel », « Ce que vous risquez sans accompagnement », « Bien plus qu'un outil IA », « La Méthode S.E.S », « Le choix du médecin conseil : un enjeu financier majeur », « Vos documents sont entre de bonnes mains », « Pourquoi nous faire confiance ? », « Les dossiers que nous accompagnons »…
- **Vocabulaire dominant** : droits, défendre, accompagnement, analyse, indemnisation. **Secondaire** : stratégie, méthode, IA, confiance, documents.
- **Mentions IA** : présentes (« Bien plus qu'un outil IA », « Analyse IA + accompagnement humain ») — transparence correcte.
- **Mentions des limites médicales/juridiques** : PAS sur la home (les disclaimers sont sur les pages outils/services).

**Réponse à la question principale — définition spontanée (2-3 phrases, comme Google/Gemini)** :
« Stratégie & Expertise Santé est une plateforme française en ligne qui aide les particuliers victimes d'accidents du travail, de maladies professionnelles ou de refus MDPH à défendre leurs droits et obtenir une indemnisation. Elle combine des analyses de dossier par intelligence artificielle, des calculateurs d'indemnités et un accompagnement humain payant. Elle semble opérer entre l'assistance administrative et le conseil, sans être un cabinet d'avocats ni un cabinet médical. »

**Classification de la perception actuelle : « accompagnement médico-administratif » (avec un pied dans « rédaction/constitution de dossiers »).**
Pourquoi : le lexique dominant est celui de l'accompagnement de victimes et de l'indemnisation ; les éléments d'« analyse documentaire spécialisée » et de « préparation stratégique » existent (Méthode S.E.S, « analyse », badge plateforme) mais sont noyés dans le récit émotionnel et jamais déclarés structurellement. La perception cible (« préparation stratégique de dossiers ») n'est atteinte nulle part de façon explicite et répétée.

---

## 7. ANALYSE DE L'ENTITÉ « STRATÉGIE & EXPERTISE SANTÉ »

**Fiche de connaissance que Google pourrait construire AUJOURD'HUI :**

| Champ | Contenu déductible | Solidité |
|---|---|---|
| Nom | Stratégie & Expertise Santé (S.E.S) | Forte (title, logo, textes) |
| Type | Plateforme web / service d'accompagnement | Moyenne (jamais déclaré) |
| Activité | Aide aux victimes AT/MP/MDPH, analyses de dossiers, guides, calculateurs | Moyenne |
| Spécialisation | Droits santé (AT/MP, MDPH, expertise médicale, assurance) | Moyenne |
| Public | Particuliers (salariés, victimes) + un volet entreprises | Moyenne |
| Services | Dossier Express IA 97 €, accompagnements personnalisés, pré-analyse gratuite | Forte (tarifs affichés) |
| Méthodologie | « Méthode S.E.S » évoquée sur la home | Faible (nommée, peu détaillée) |
| Limites | Disclaimers épars (« ne remplace pas ») sur 10 pages | Faible (jamais central) |
| Identité juridique | KAPSULES KORPORATION, EI, RCS 824 339 584 Chartres, TVA FR78824339584 | Présente MAIS confinée aux mentions légales |
| Lien Kapsules ↔ SES | « Marque/enseigne exploitée par » — uniquement mentions légales | Faible |
| Fondateur | Anonyme (« Fondateur », récit personnel) | Très faible |
| Outils | Dossier Express IA, StratégiIA, simulateurs | Moyenne (Dossier Express sur-représenté) |

**Informations importantes MANQUANTES pour l'entité** : schéma Organization global ; nom du fondateur (ou choix assumé d'anonymat avec entité renforcée autrement) ; définition canonique répétée du positionnement ; lien explicite produit→organisation (provider) ; sameAs (profils externes, annuaire, LinkedIn, presse) ; date de création de la marque ; périmètre déclaré (« ce que nous ne faisons pas ») en zone d'identité.

---

## 8. ANALYSE E-E-A-T (notes /10)

| Critère | Note | Justification |
|---|---|---|
| **Expérience** | 6/10 | Vrai point fort narratif : « né d'un combat réel », vécu du fondateur, cas accompagnés, avis clients (/avis). Mais invérifiable (anonymat) et non structuré (pas de dates, pas de volumétrie assumée). |
| **Expertise** | 4/10 | Contenus riches et précis (articles L.461-1, R.461-8, CRRMP, barèmes — présents dans guides et calculateurs) MAIS aucun auteur nommé, aucune qualification, pas de dates de mise à jour visibles sur les guides, pas de sources citées en références formelles. |
| **Autorité** | 3/10 | Aucun signal externe visible sur le site (presse, citations, associations, annuaires), pas de Person, pas de sameAs, marque jeune. « Pionnier en France » est une auto-revendication sans preuve. |
| **Fiabilité** | 6/10 | Mentions légales complètes (RCS, TVA, adresse, contact), RGPD dédié, CGV, tarifs publics transparents, disclaimers présents, transparence IA partielle (l'IA est nommée, ses limites peu). Manquent : identité humaine, dates de mise à jour, politique de correction. |

**Faiblesse structurante commune : l'anonymat du fondateur + l'absence d'auteurs datés plafonnent les 4 critères sur un site YMYL (santé/argent/droit), catégorie où Google exige le plus de preuves d'identité.**

---

## 9. ANALYSE SCHEMA.ORG (inventaire exhaustif du code déployé)

| Type | Présent ? | Où | Correct ? | Complet ? | Conforme au contenu ? |
|---|---|---|---|---|---|
| Organization | Oui (3 pages seulement) | /dossier-express, /expertise-medicale, /expertise-medicale/assureur | Partiel | Non (pas de legalName, sameAs, founder) | Oui mais MAL PLACÉ (devrait être global/home) |
| WebSite | **Non** | — | — | — | — |
| WebPage | **Non** | — | — | — | — |
| Article | Oui (1) | /expertise-medicale/assureur | Oui | Moyen | Oui |
| BreadcrumbList | Oui (2) | /expertise-medicale, /assureur | Oui | Oui | Oui — à généraliser aux guides |
| Person | **Non** | — | — | — | — |
| SoftwareApplication | **Non** | — | — | — | Candidats évidents : Dossier Express IA, StratégiIA |
| Product / Offer | Offer (1) | /dossier-express | Oui | Moyen | Oui |
| FAQPage / Question / Answer | Oui (~10 pages) | AT/MP, MDPH, médecin-conseil, calculatrices, dossier-express, protection-juridique, entreprises, parrainage, auto-diagnostic, guides (GuidePage) | Oui | Bon | Oui — point fort du site |
| HowTo | Oui (1) | /auto-diagnostic | Oui | Bon | Oui |
| LocalBusiness | Non | — | — | — | Non pertinent (service national en ligne) — ne pas ajouter |
| **MedicalProcedure / MedicalScholarlyArticle / PeopleAudience** | Oui (1) | /expertise-medicale | **DOUTEUX** | — | **NON : le contenu est un guide stratégique, pas un article médical savant ni une procédure réalisée par SES. Risque de sur-revendication médicale — exactement la confusion à éviter.** |
| index.html (global) | **0 script JSON-LD** | — | — | — | — |

**À ajouter (proposition, RIEN n'a été ajouté)** : Organization global enrichi (home/index.html), WebSite, Person (fondateur, si identité assumée), SoftwareApplication×2 avec provider→SES, BreadcrumbList sur les 17 guides, `Service` sur /accompagnements. **À retirer/requalifier** : les 3 types médicaux de /expertise-medicale (⚠️ page gelée — après le gel).

---

## 10. ARCHITECTURE SÉMANTIQUE

```
KAPSULES KORPORATION (entité juridique — invisible hors mentions légales)
└── STRATÉGIE & EXPERTISE SANTÉ (marque — entité principale voulue)
    ├── Activité principale : analyse & préparation stratégique de dossiers médico-administratifs
    │    (actuellement perçue : accompagnement/défense des victimes)
    ├── Domaines : AT/MP · MDPH/AAH/RQTH · Expertise médicale (CPAM/assureur/tribunal) · Litiges assurantiels
    ├── Services : Accompagnements personnalisés · Dossier Express IA (97 €) · Pré-analyse gratuite · Entreprises/Séminaires
    ├── Outils : Dossier Express IA (produit) · StratégiIA (assistant) · Auto-diagnostic · Simulateurs (hub /simulateur)
    ├── Guides : 17 guides interliés (Phase 1 OK) sous /guide/* + hub /guides-pratiques
    └── Calculateurs : /calculatrice-ipp · /calculatrice-aah (transformés en hubs, Phase 1 OK)
```

**Incohérences détectées** :
1. **Dossier Express IA risque d'être lu comme l'identité principale** : c'est la page la plus « schématisée » (Organization+Service+Offer), la plus citée en interne, avec un branding propre (« Dossier Express IA » apparaît même comme H1 de l'espace évaluateur). Rien ne dit structurellement « produit DE Stratégie & Expertise Santé ». → à corriger via provider/parentOrganization.
2. La hiérarchie marque→exploitant (SES→Kapsules) n'existe que dans une page légale non maillée sémantiquement.
3. Le hub /simulateur et l'Auto-diagnostic (restauré, non déployé) se partagent le champ « simulateur/diagnostic » — la distinction outil d'orientation vs calculateurs d'indemnisation est claire pour l'humain, pas déclarée pour la machine.

---

## 11. LES 20 PAGES STRATÉGIQUES (perception actuelle → cible)

| # | URL | Objectif | Perception probable actuelle | Perception cible | Priorité |
|---|---|---|---|---|---|
| 1 | / | Identité + conversion | Service de défense des victimes | Structure d'analyse stratégique de dossiers | **P1** |
| 2 | /a-propos | Entité humaine | Récit personnel anonyme (« Mon parcours ») | Fiche d'identité E-E-A-T (fondateur, méthode, périmètre) | **P1** |
| 3 | /dossier-express 🧊 | Produit phare | Produit autonome « analyse en 2 h » | Produit DE SES, analyse documentaire | P2 (gel 28 j) |
| 4 | /expertise-medicale 🧊 | Tête de cocon | Autorité quasi médicale (schémas Medical*) | Guide stratégique par un tiers non-médical | P2 (gel) |
| 5 | /expertise-medicale/assureur 🧊 | Cocon assurance | OK (Article+FAQ propres) | idem + entité | P3 (gel) |
| 6 | /accident-travail-maladie-professionnelle | Tête de cocon AT/MP | Guide droits/indemnisation | + angle préparation documentaire | P2 |
| 7 | /mdph | Tête de cocon MDPH | Guide droits | + angle structuration de dossier | P2 |
| 8 | /medecin-conseil | Cocon expertise | Guide rôle/recours | OK, borner le « conseil » | P2 |
| 9 | /protection-juridique | Cocon assurance | Guide | OK | P3 |
| 10 | /accompagnements | Services | « Services adaptés » générique | Offre d'analyse/préparation par niveaux | P2 |
| 11 | /tarifs | Transparence | Bon (fiabilité) | Ajouter périmètre par prestation | P3 |
| 12 | /simulateur | Hub calculateurs | Simulateurs d'indemnisation | OK (assumé : intention utilisateur) | P3 |
| 13 | /calculatrice-ipp | Hub IPP | Calculateur + conseils | OK | P3 |
| 14 | /calculatrice-aah | Hub AAH | Calculateur | OK | P3 |
| 15 | /guides-pratiques | Hub éditorial | Bibliothèque | + auteurs/dates | P2 |
| 16 | /guide/refus-maladie-professionnelle-cpam-recours | Guide majeur | Guide recours | + auteur, breadcrumb | P2 |
| 17 | /guide/comment-preparer-expertise-medicale | Guide majeur | Guide préparation | Vitrine idéale du positionnement cible | P2 |
| 18 | /guide/taux-ipp-5-pourcent-contester | Guide majeur | Guide contestation | + breadcrumb | P3 |
| 19 | /mentions-legales | Entité juridique | Complète mais isolée | Reliée à l'entité (Organization.legalName) | P2 |
| 20 | /contact | Conversion | OK | OK | P3 |

🧊 = gel SEO 28 jours en cours — aucune modification avant la fin du gel.

---

## 12. MAILLAGE INTERNE (état post-Phase 1, re-vérifié)

- ✅ Corrigé en Phase 1 : 17 guides interliés entre eux et vers les têtes de cocon ; calculatrices transformées en hubs avec liens sortants ; home et footer optimisés. Le problème n°1 de l'audit du 06/08 est résolu.
- Footer : 22 liens couvrant toutes les pages majeures (accueil, services, cocons, outils, légal) — sain.
- **Restes à traiter** : /parrainage (indexable, hors sitemap, quasi non maillé — semi-orpheline) ; /auto-diagnostic (restauré au menu, à ajouter au sitemap après déploiement) ; /avis et /forum faiblement reliés depuis les contenus (signaux d'expérience sous-exploités) ; aucune ancre interne ne porte le vocabulaire d'entité (« préparation stratégique de dossier ») — les ancres sont fonctionnelles (« calculer », « contester »), c'est bien pour l'intention, mais l'entité ne circule pas.
- **Plan de maillage proposé (non appliqué)** : depuis /a-propos vers les 4 têtes de cocon avec ancres de positionnement ; depuis chaque tête de cocon un lien retour vers /a-propos (« qui analyse votre dossier ») ; 2-3 liens contextuels des guides vers /avis (preuve sociale).

---

## 13. TITLES & META-DESCRIPTIONS (principales pages — recommandations, RIEN appliqué)

| Page | TITLE ACTUEL → PROBLÈME → RECOMMANDÉ |
|---|---|
| / | « …défendre vos droits » → cadre « défense », zéro identité → « Analyse stratégique de dossiers AT/MP, MDPH & expertise médicale — Stratégie & Expertise Santé » (⚠️ tester : le title actuel performe peut-être — changement à AB-tester après le gel, risque de perte de CTR si mal dosé) |
| /a-propos | « Mon parcours » → aucune valeur entité/SEO → « Qui est Stratégie & Expertise Santé ? Méthode, périmètre et fondateur » |
| /accompagnements | « Nos accompagnements » → générique → « Accompagnement stratégique de dossiers médico-administratifs — niveaux et méthode » |
| /avis | « Avis et témoignages » → OK → + marque : « Avis clients — Stratégie & Expertise Santé » |
| /agenda | « Rendez-vous confirmé » → title d'état de confirmation utilisé comme title de page (anomalie) → « Prendre rendez-vous — consultation gratuite 10 min » |
| /dossier-express 🧊 | « Analyse de dossier maladie professionnelle — rapport sous 2 h » → bon, ne pas toucher (gel + performant) |
| Guides | Titles gérés par les données de guides — globalement bons (audit 06/08) ; manquent auteur/dates dans le contenu, pas dans les titles |

Meta-descriptions : celles des cocons et calculatrices sont bonnes (intention + promesse). Celle de la home décrit des actions utilisateur sans définir SES → y intégrer une demi-phrase d'identité.

---

## 14. TEST DE COMPRÉHENSION PAR IA

**Question : « Puis-je faire confiance à Stratégie & Expertise Santé ? » — réponse simulée d'une IA ne connaissant que le site actuel :**

> « Stratégie & Expertise Santé est une plateforme française qui aide les victimes d'accidents du travail, de maladies professionnelles et de refus MDPH, via des analyses de dossier par IA (97 €) et un accompagnement humain. Points rassurants : mentions légales complètes (exploitant identifié au RCS de Chartres), tarifs transparents, avertissements indiquant que le service ne remplace ni un médecin ni un avocat, avis clients publiés. Points de vigilance : l'identité des personnes derrière le service n'est pas précisée (fondateur anonyme), il ne s'agit ni d'un cabinet d'avocats ni d'un cabinet médical, et les résultats ne peuvent pas être garantis. C'est probablement un service légitime d'aide à la constitution de dossiers, mais vérifiez son périmètre exact avant de payer. »

- **Correctement compris** : légitimité de base, transparence tarifaire, existence de limites, nature non réglementée.
- **Mal compris** : la valeur ajoutée est réduite à « aide à la constitution de dossiers » ; la complémentarité avec les professionnels est invisible ; la méthode (analyse, chronologie, cohérence, traçabilité) n'apparaît pas.
- **Manque** : qui est le fondateur, la méthodologie nommée et décrite, les preuves d'expérience structurées, la déclaration formelle d'entité.
- **Pourquoi l'IA réduit SES à une aide administrative** : en l'absence de définition canonique et de données structurées, l'IA se rabat sur le plus proche prototype connu (« service d'aide aux démarches ») — c'est le comportement par défaut face à une entité non déclarée.

**Même question APRÈS application des recommandations (simulation)** :
> « Stratégie & Expertise Santé est une structure spécialisée dans l'analyse et la préparation stratégique de dossiers médico-administratifs complexes (AT/MP, MDPH, expertises médicales). Elle n'est ni un cabinet médical ni un cabinet d'avocats et le revendique clairement : son rôle est d'analyser, structurer et documenter les pièces d'un dossier pour que la personne — et ses professionnels (avocat, médecin-conseil) — travaillent sur une base claire et exploitable. Le fondateur est identifié, la méthode est décrite, l'exploitant est enregistré au RCS, les tarifs sont publics et les limites explicites. C'est un intervenant spécialisé crédible sur le maillon documentaire et procédural, en amont ou en complément des professions réglementées. »

---

## 15. COMPARAISON AVEC LE POSITIONNEMENT CIBLE

| Élément | Compréhension actuelle | Compréhension cible | Écart |
|---|---|---|---|
| Nature de SES | Plateforme d'aide aux victimes | Structure spécialisée d'analyse de dossiers | **Fort** |
| Activité principale | Accompagnement + vente d'analyses IA | Analyse & préparation stratégique documentaire | **Fort** |
| Niveau de spécialisation | Généraliste « droits santé » | Spécialiste du dossier médico-administratif complexe | Moyen |
| Méthodologie | « Méthode S.E.S » évoquée | Méthode décrite : pièces, chronologie, cohérence, traçabilité | **Fort** |
| Valeur ajoutée | Obtenir une indemnisation | Base de travail claire et exploitable | **Fort** |
| Rôle de l'IA | Outil d'analyse rapide (transparent) | Assistance documentaire sous contrôle humain, limites déclarées | Moyen |
| Relation aux médecins | Réseau de partenaires | Complémentarité : SES prépare, le médecin juge | **Fort** |
| Relation aux avocats | Réseau de partenaires | Complémentarité : SES structure, l'avocat conseille/représente | **Fort** |
| Limites réglementaires | Disclaimers épars | Périmètre volontaire, central et assumé | Moyen |
| Public cible | Particuliers victimes | Particuliers + professionnels utilisateurs de la base documentaire | Moyen |

---

## 16. PLAN D'ACTION PRIORISÉ (proposé — RIEN n'a été modifié)

### PRIORITÉ 1 — Indispensable (sans risque pour le référencement actuel)
| Action | Page | Problème | Modification proposée | Raison SEO | Risque |
|---|---|---|---|---|---|
| 1.1 JSON-LD Organization global | index.html + home | Entité non déclarée | Organization complet (name, legalName Kapsules, description = positionnement cible, knowsAbout, contactPoint) | Fonde le graphe de connaissance | Nul (ajout invisible) |
| 1.2 JSON-LD WebSite | home | Absent | WebSite lié à l'Organization | Entité site | Nul |
| 1.3 Paragraphe d'entité canonique | home (section) + /a-propos | Définition inexistante | 2-3 phrases du positionnement cible, verbatim aux 2 endroits | Fixe la définition pour Google ET les IA | Faible (ajout, pas de remplacement) |
| 1.4 Provider sur Dossier Express | schémas existants /dossier-express 🧊 | Produit > organisation | Ajouter provider→Organization SES (JSON-LD uniquement, texte intact) | Rétablit la hiérarchie | Faible — MAIS page gelée : à faire à la fin du gel |
| 1.5 Reformuler « garantie » (hors garanties contractuelles) et « faire basculer » | pages concernées (hors gel) | Sur-promesse | Formulations factuelles | Réduit le risque YMYL | Nul |

### PRIORITÉ 2 — Important
| Action | Détail |
|---|---|
| 2.1 Refonte /a-propos | Title, identité du fondateur (décision humaine : lever l'anonymat ou compenser), schéma Person, méthode S.E.S. détaillée, périmètre |
| 2.2 Requalifier les schémas Medical* de /expertise-medicale | Article + FAQPage à la place — APRÈS le gel 28 j |
| 2.3 SoftwareApplication pour Dossier Express IA et StratégiIA | provider = SES |
| 2.4 Section « Notre périmètre, volontaire » | home + /accompagnements : fait / ne fait pas / avec qui |
| 2.5 BreadcrumbList sur les 17 guides | via GuidePage (1 seul fichier) |
| 2.6 Auteurs + dates de mise à jour sur les guides | E-E-A-T YMYL |
| 2.7 Sitemap : + /parrainage, + /auto-diagnostic | après déploiement |

### PRIORITÉ 3 — Optimisation
Titles /a-propos, /accompagnements, /agenda, /avis · ancres d'entité dans le maillage · liens contextuels vers /avis · vraie gestion 404 (noindex sur l'état non trouvé) · sameAs (profils externes à créer d'abord) · page « Méthode » dédiée à terme.

**Rappels de sécurité** : gel SEO 28 j sur /dossier-express, /expertise-medicale, /expertise-medicale/assureur — toute action sur ces pages est repoussée à la fin du gel. Le title de la home performe (position/CTR mesurés au 06/08) : le modifier comporte un risque réel de variation de CTR → le paragraphe d'entité + JSON-LD (risque nul) d'abord, le title ensuite, mesuré.

---

## DONNÉES BRUTES À TRANSMETTRE À CHATGPT

### A. Inventaire
- **Sitemap production : 42 URLs** (24 pages + 17 guides + hub guides), toutes en HTTP 200. Détail : /, /a-propos, /accompagnements, /expertise-medicale, /accident-travail-maladie-professionnelle, /mdph, /protection-juridique, /medecin-conseil, /tarifs, /dossier-express, /simulateur, /calculatrice-ipp, /calculatrice-aah, /ressources, /contact, /agenda, /forum, /avis, /seminaires, /entreprises, /partenaires, /mentions-legales, /cgv, /politique-confidentialite, /guides-pratiques + 17 /guide/*.
- **Hors sitemap mais indexables** : /parrainage. **Noindex volontaires** : /espace-client, /evaluation-expert, /acces-invite. **Robots.txt (dynamique)** : Disallow /admin, /admin-dashboard, /espace-client, /evaluation-expert, /cas-demonstration/.
- **Particularité SPA** : toute URL inconnue → HTTP 200 + « Page non trouvée » (soft-404). Les meta (title/desc/robots) sont injectées côté client (react-helmet) ; une meta statique « index, follow » coexiste dans index.html avec les meta injectées (Google applique la plus restrictive).

### B. Table title/description/H1/schémas par page (extraite du code déployé)
(44 fichiers pages ; sélection des indexables — voir section 9 pour les schémas)
- / : T=« Accident du travail, maladie professionnelle & expertise médicale : défendre vos droits » · H1=« Vous n'êtes plus seul face à… » · 12 H2 · schémas : AUCUN
- /a-propos : T=« Mon parcours » · H1=« Mon parcours, votre force » · schémas : aucun
- /accompagnements : T=« Nos accompagnements » · H1=« Des services adaptés à votre parcours »
- /expertise-medicale 🧊 : T=« Expertise Médicale : Stratégie Assureur, MDPH, Tribunal » · schémas : Organization, BreadcrumbList, FAQPage, **MedicalProcedure, MedicalScholarlyArticle, PeopleAudience**
- /expertise-medicale/assureur 🧊 : T=« Expertise médicale assureur : stratégie, préparation, recours » · schémas : Article, BreadcrumbList, FAQPage, Organization
- /dossier-express 🧊 : T=« Analyse de dossier maladie professionnelle — rapport sous 2 h » · schémas : Organization, Service, Offer, FAQPage
- /accident-travail-maladie-professionnelle : FAQPage · /mdph : FAQPage · /medecin-conseil : FAQPage · /protection-juridique : FAQPage · /calculatrice-ipp : FAQPage · /calculatrice-aah : FAQPage · /entreprises : FAQPage · /parrainage : FAQPage · /auto-diagnostic (non déployé) : FAQPage+HowTo · guides (GuidePage) : FAQPage
- /simulateur (hub) : H1=« Simulateurs d'indemnisation : IPP, AAH, accident du travail » — title/desc portés par le composant hub
- /tarifs : T=« Tarifs et prestations » (mentionne « Dossier Express IA 97€ », « StratégiIA »)
- /agenda : T=« Rendez-vous confirmé » (anomalie) · /avis : H1=« Livre d'or » · /forum : H1=« Forum d'entraide »

### C. Comptages lexicaux (code des pages, insensible à la casse)
- Positionnement cible : analyse 285 · stratégi- 196 · accompagnement 146 · structur- 60 · préparation 44 · pièces 40 · documentaire 22 · chronologie 5 · « dossier médico-administratif » 2
- Commercial : indemnisation 94 · garantie 32 · gain 25 · revaloris- 9 · optimis- 7 · gagner 5 · récupér- 3 · maximis- 2 · « faire basculer » 1
- Risque réglementaire : « expertise médicale » 87 (sujet traité — légitime) · diagnostic 45 (surtout auto-diagnostic — outil) · avocat 40 · représent- 15 · « conseil juridique » 10 · « avis médical » 9 · cabinet 2
- Disclaimers (« ne remplace pas / ne constitue pas / ne se substitue ») présents sur 10 pages : agenda, auto-diagnostic, calculatrices ×2, dossier-express, évaluateur, mentions légales, confidentialité, accompagnements, simulateur-preview.

### D. Identité juridique (mentions légales)
Marque/enseigne : Stratégie & Expertise Santé · Exploitant : KAPSULES KORPORATION · Forme : Entreprise individuelle · RCS : 824 339 584 Chartres · Immatriculation : 15/12/2016 · Siège : 4 Rue de la Corne du Parc, 28310 Janville-en-Beauce · TVA : FR78824339584 · Contact : contact@strategie-expertise-sante.fr / 07 59 93 60 67 · Responsable publication : KAPSULES KORPORATION · Fondateur : présenté sans nom sur /a-propos.

### E. Références internes
- Audit performance GSC : /app/memory/AUDIT_SEO_COMPLET_2026-08-06.md (positions, clics, cocons, cannibalisation)
- Journal Phase 1 : /app/memory/JOURNAL_SEO_PHASE1.md (maillage guides, hubs calculatrices, home/footer)
- Gel SEO 28 j actif sur : /dossier-express, /expertise-medicale, /expertise-medicale/assureur
- Écart preview/production au 08/08 : /auto-diagnostic + entrée menu « Simulateurs d'indemnisation » existent en preview, pas encore déployés.

*Fin de l'audit — aucune modification effectuée. En attente de l'analyse croisée et des décisions.*
