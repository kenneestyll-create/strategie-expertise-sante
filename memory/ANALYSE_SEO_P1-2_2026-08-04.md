# ANALYSE SEO P1-2 — REPOSITIONNEMENT SÉMANTIQUE /dossier-express (04/08/2026)
Audit en lecture seule. AUCUNE modification effectuée. Plan soumis à validation.

---

## 1. ÉTAT ACTUEL DE LA PAGE (constats mesurés)

### Balises et contenu
| Élément | Valeur actuelle | Diagnostic |
|---|---|---|
| Title | « Dossier Express IA — Rapport d'analyse sous 2h » | 100 % orienté **marque produit**. Personne ne recherche « dossier express IA ». Zéro requête non-marque ciblée. |
| Meta description | « Uploadez vos documents, notre outil… 97€ » | Orientée fonctionnalité, aucune intention de recherche. |
| H1 | « Votre rapport d'analyse complet et personnalisé » | Générique — aucun mot-clé (ni maladie professionnelle, ni accident du travail, ni expertise, ni MDPH). |
| H2 (5) | « Ce que contient votre rapport » / « Typologie des dossiers analysés » / « Qu'est-ce que le Dossier Express IA ? » / FAQ / « Prêt à analyser votre dossier ? » | Aucun H2 ne porte une requête. La sémantique métier (AT/MP/CPAM/MDPH/assurance) n'apparaît que dans le corps de texte bas de page. |
| Contenu SEO | ~200 mots (1 section) | Trop court pour une page transactionnelle YMYL ; bonnes bases (mentions MP, AT, CPAM, MDPH, assurance) mais non structurées en Hn. |
| FAQ | 3-5 questions + schema FAQPage ✅ | Questions orientées produit (« Combien de temps… »), pas orientées requêtes. |
| Schema | FAQPage ✅ — **pas de schema Service/Offer** malgré un prix affiché (97 €) | Opportunité rich snippet non exploitée. |
| Sitemap | Présente ✅ | OK |

### Constat technique important (contexte, hors périmètre P1-2)
La prod sert une **coquille SPA vide (6,6 Ko) y compris à Googlebot** (vérifié par curl avec UA Googlebot : title générique du site, H1 absent du HTML brut). Google indexe via son rendu JavaScript (le site a des clics GSC, donc ça fonctionne), mais c'est un handicap structurel : indexation plus lente, autres moteurs/IA de recherche aveugles. À traiter un jour comme chantier séparé (prerender/SSG) — mentionné pour transparence, PAS dans P1-2.

## 2. MAILLAGE INTERNE (mesuré dans le code)

### Entrant — FORT ✅
- Header (nav principale, toutes pages), HomePage (hero + bannière « Expertise imminente »)
- 7 pages piliers via `DossierExpressCTA` : /accident-travail, /calculatrice-aah, /calculatrice-ipp, /expertise-medicale, /mdph, /medecin-conseil, /protection-juridique
- Guides (17) via le CTA de GuidePage
- ⚠️ Ancres probablement uniformes (« Dossier Express IA ») → signal sémantique répétitif, aucune ancre du type « faire analyser mon dossier maladie professionnelle ».

### Sortant — CUL-DE-SAC ❌
La page ne lie que : `/` (×2), `/agenda`, `/contact`, `/tarifs` (×1). **Aucun lien vers les guides ni les outils.** Une page money sans liens contextuels sortants = pas de circulation sémantique, pertes pour l'utilisateur indécis (qui repart au lieu d'aller mûrir sur un guide puis revenir).

## 3. INTENTIONS DE RECHERCHE À FORTE VALEUR (bas de funnel — service)
L'offre = analyse de dossier + rapport + stratégie, 97 €, 2 h. Les intentions « service » que la page devrait capter (aujourd'hui : AUCUNE) :

| Cluster d'intention | Exemples de requêtes | Valeur |
|---|---|---|
| A. Aide dossier MP/AT | « aide dossier maladie professionnelle », « qui peut m'aider pour mon dossier accident du travail », « faire analyser son dossier CPAM » | ⭐⭐⭐ cœur de cible, achat direct |
| B. Analyse de rapport d'expertise | « faire analyser un rapport d'expertise médicale », « deuxième avis rapport expertise », « contre-expertise médicale prix » | ⭐⭐⭐ très qualifié (cœur produit démontré : comparaison multi-expertises) |
| C. Contestation avec aide | « aide pour contester taux IPP », « aide recours CPAM », « aide recours MDPH refusé » | ⭐⭐⭐ jonction avec les guides existants (récupération du trafic info) |
| D. Alternative à l'avocat | « avocat maladie professionnelle prix », « combien coûte un avocat accident du travail », « analyse dossier moins cher qu'un avocat » | ⭐⭐ angle prix 97 € très différenciant |
| E. Litige assurance/prévoyance | « aide litige assurance invalidité », « analyse dossier prévoyance » | ⭐⭐ |

Note d'honnêteté : je n'ai pas de données GSC propres à /dossier-express en mémoire (les audits passés couvrent d'autres pages). **Recommandé avant exécution : m'indiquer (ou vérifier vous-même) les requêtes GSC actuelles de la page** — probablement quasi exclusivement marque, ce qui confirmerait le diagnostic. Le plan reste valide dans les deux cas : tout ce qui précède est incrémental.

## 4. REQUÊTES COUVERTES vs MANQUANTES
- **Couvertes** : marque (« dossier express ia », « stratégie expertise santé ») uniquement.
- **Manquantes** : la totalité des clusters A-E ci-dessus. Le mot « maladie professionnelle » n'apparaît ni dans le title, ni le H1, ni aucun H2.

## 5. RISQUE DE CANNIBALISATION (à piloter)
- /expertise-medicale, /accident-travail, /mdph = pages piliers **informationnelles** ; /dossier-express doit se positionner sur l'intention **« faire analyser / aide / service »**, pas sur l'info. Différenciation claire par le vocabulaire (« faire analyser », « aide », « rapport sous 2 h », « 97 € »).
- Ne PAS viser « contester taux IPP » en frontal (guides dédiés) — viser « AIDE pour contester ».

## 6. PLAN PROPOSÉ (exécution uniquement après votre validation)

### Lot A — Repositionnement de la page elle-même (cœur P1-2, page seule)
1. **Title** (~60 car.) : « Analyse de dossier maladie professionnelle & accident du travail — rapport sous 2 h » (variante à arbitrer avec vous)
2. **Meta description** (~150 car.) : intention + différenciateurs (97 €, 2 h, jurisprudences/barèmes, CPAM/MDPH/assurance)
3. **H1** : « Faites analyser votre dossier — accident du travail, maladie professionnelle, MDPH, assurance » (le sous-titre conserve la promesse conversion « rapport complet sous 2 h »)
4. **H2 sémantiques** : requalifier les H2 existants sans toucher au design (ex. « Ce que contient votre rapport d'analyse de dossier », « Pour quels litiges ? CPAM, MDPH, assurance, expertise médicale »)
5. **Contenu SEO enrichi** : 200 → ~550 mots, structuré en H3 par intention (analyse MP/AT · analyse de rapport d'expertise · aide recours MDPH · litige assurance), chaque H3 intégrant naturellement les requêtes cibles
6. **FAQ** : +3 questions orientées requêtes (« Combien coûte une analyse de dossier maladie professionnelle ? », « Puis-je faire analyser un rapport d'expertise médicale ? », « Est-ce utile avant un recours CPAM ou MDPH ? ») — schema FAQPage déjà branché
7. **Schema Service** avec offre 97 € (rich snippet prix)
8. **Bloc « Ressources utiles »** en bas de page : 3-4 liens sortants contextuels vers guides/outils à forte affinité (fin du cul-de-sac)
   → Zéro changement de design/layout, zéro impact sur le tunnel de commande.

### Lot B — Maillage entrant (modifie des pages existantes → validation séparée)
- Varier les ancres des 7 `DossierExpressCTA` selon la page hôte (ex. sur /mdph : « Faire analyser mon dossier MDPH ») — 1 attribut texte par page, fort signal sémantique.

### Lot C — Mesure
- Baseline GSC de la page avant déploiement (impressions/clics/requêtes) puis suivi J+28 sur les clusters A-E.

## 7. IMPACT ATTENDU (réaliste, sans promesse)
- Aujourd'hui la page ne capte **aucune requête non-marque** → toute impression gagnée est incrémentale ; les clusters visés sont moyenne traîne, concurrence modérée (avocats/forums), avec un différenciateur prix/délai fort.
- Effet secondaire attendu : meilleure conversion du trafic interne grâce à des ancres explicites (Lot B) et rétention des indécis via le bloc ressources.
- Contrainte assumée : page en CSR pur (cf. §1) — l'indexation passe par le rendu JS de Google ; les gains seront plus lents que sur un site SSR. KPI de succès J+28 : premières impressions non-marque > 100 ; J+90 : premières positions top 20 sur 2-3 requêtes des clusters A-C.
