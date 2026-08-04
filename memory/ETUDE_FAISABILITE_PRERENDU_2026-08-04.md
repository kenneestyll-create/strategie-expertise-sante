# ÉTUDE DE FAISABILITÉ — PRÉRENDU DES PAGES STRATÉGIQUES (04/08/2026)
Étude en lecture seule. AUCUN code modifié. Rapport comparatif soumis à validation.

## 0. ARCHITECTURE ACTUELLE (faits vérifiés)
- Frontend : **Create React App (react-scripts 5) + craco**, meta gérées par `react-helmet-async` côté client.
- Production : bundle statique servi derrière **Cloudflare** + ingress Emergent ; HTML en `no-cache`, assets `max-age=60` ; fallback SPA actif (toute route → index.html, cf. `vercel.json` : rewrite `/((?!api/).*)` → `/index.html`).
- **Constat mesuré** : la prod sert une coquille vide de 6,6 Ko à TOUS les agents, y compris Googlebot (vérifié par curl avec UA Googlebot) — title générique, aucun H1, aucun contenu dans le HTML source.
- Contenus : 41 URLs en sitemap dont **17 guides** (contenu long stocké en MongoDB, chargé via API au runtime — point clé pour le prérendu), 7 pages piliers, outils, pages service.
- Nuance importante et honnête : **Google rend le JavaScript** — le site est indexé et positionné (clics GSC réels). Le prérendu n'est donc pas un « déblocage » mais une **optimisation** (vitesse/fiabilité d'indexation) et surtout une **ouverture aux crawlers qui ne rendent PAS le JS** : Bing partiellement, et la quasi-totalité des **crawlers IA (ChatGPT/OAI-SearchBot, PerplexityBot, ClaudeBot)** — canal de découverte en forte croissance en 2026, aujourd'hui totalement aveugle sur le site.

---

## 1. APPROCHES POSSIBLES — COMPARATIF

### Option A — Prérendu statique AU BUILD (react-snap / puppeteer en postbuild)
Un navigateur headless crawle l'app après `yarn build` et écrit un HTML par route dans `build/`.
- Compatibilité : moyenne. react-snap est **non maintenu depuis 2019** ; nécessite Chrome **dans le pipeline de build Emergent** (non garanti, non contrôlable par nous) ; les 17 guides exigent l'API backend pendant le build (indisponible à ce moment — contournement fragile : appeler l'API de prod pendant le build = dépendance circulaire).
- Impacts : chaque build devient plus long et peut **échouer à cause du prérendu** → risque direct sur TOUS les déploiements, y compris les correctifs urgents.
- Verdict : ❌ risque de pipeline inacceptable pour un gain identique à l'option B.

### Option B — Snapshots statiques VERSIONNÉS (générés en preview, commités dans `public/`) ⭐
Je génère les snapshots HTML des pages stratégiques avec Playwright **dans l'environnement de preview** (rendu réel, données réelles, helmet résolu, JSON-LD inclus), je les écris dans `frontend/public/<route>/index.html`, ils sont versionnés et déployés comme simples fichiers statiques. Le serveur statique sert les fichiers existants AVANT le fallback SPA → les bots reçoivent le HTML complet ; le bundle JS embarqué prend ensuite le relais pour l'interactivité (les visiteurs ne voient aucune différence).
- Compatibilité : élevée — zéro changement de stack, zéro dépendance de build, réversible en supprimant les fichiers.
- Déploiement : inchangé (fichiers statiques ordinaires). **Un point à valider en premier** : confirmer que le serveur prod sert bien un fichier réel avant le fallback SPA (test à 5 min : déployer un fichier témoin `public/test-prerender/index.html` et le curl-er en prod).
- Performances : FCP/LCP améliorés sur les pages prérendues (contenu visible avant exécution JS) ; aucun impact serveur.
- Cache : HTML déjà en `no-cache` chez Cloudflare → fraîcheur garantie après chaque déploiement.
- Maintenance : LE point faible — les snapshots sont figés : ils doivent être **régénérés avant chaque déploiement qui modifie une page prérendue**. Mitigation : script `regenerate-snapshots` (une commande, ~2 min pour 25 pages) + ligne ajoutée à la checklist de pré-déploiement ; les guides changent rarement.
- Verdict : ✅ **meilleur rapport bénéfice/complexité** — ~1 session de mise en place, risque quasi nul.

### Option C — Rendu dynamique ciblé (détection de bots)
Un proxy (Cloudflare Worker côté votre zone DNS, ou middleware) détecte les bots par User-Agent et leur sert un HTML prérendu, les humains recevant la SPA.
- Compatibilité : exige la maîtrise du proxy — soit un **Cloudflare Worker hors périmètre Emergent** (à administrer par vous), soit un headless Chrome dans le pod backend (~300 Mo de RAM : dangereux sur le tier actuel, on vient d'y stabiliser les OOM).
- Autres : Google a officiellement rétrogradé le « dynamic rendering » au rang de solution de contournement, risque de cloaking mal configuré, deux chaînes de rendu à maintenir.
- Verdict : ⚠️ pertinent seulement si l'option B échouait au point de validation n°1.

### Option D — Migration SSR/SSG complète (Next.js)
- Le « vrai » SSR : HTML frais à chaque requête, pour tous, pour toujours.
- Compatibilité : réécriture du routing des ~40 pages + contexts + admin ; runtime Node en prod à la place du statique (support côté plateforme à confirmer) ; 2 à 4 semaines d'effort ; **risque de régression élevé sur une app qui encaisse des paiements et vient d'être stabilisée**.
- Verdict : ❌ à ce stade — à réévaluer seulement si le SEO devient LE facteur limitant de croissance et après épuisement de l'option B.

### Option E — Enrichissement minimal de l'index.html
Meta/JSON-LD par défaut dans la coquille. Gain marginal (une seule page), ne répond pas au besoin. ❌

| Critère | A (build) | **B (snapshots)** | C (dynamique) | D (Next.js) |
|---|---|---|---|---|
| Effort initial | Moyen | **Faible (~1 session)** | Élevé | Très élevé |
| Risque déploiement | Élevé | **Quasi nul** | Moyen | Élevé |
| Maintenance | Faible | **Moyenne (régénération)** | Élevée | Faible |
| Fraîcheur HTML bots | À chaque build | À chaque régénération | Temps réel | Temps réel |
| Compatibilité archi actuelle | Moyenne | **Totale** | Partielle | Refonte |
| Réversibilité | Moyenne | **Totale (suppression fichiers)** | Moyenne | Nulle |

## 2. GAIN SEO ATTENDU (réaliste)
- **Google** : gain modéré — indexation plus rapide et fiable des nouvelles pages (guides), JSON-LD lu dans la source (rich snippets FAQ/Service plus stables), meilleur LCP. Pas de bond de positions à attendre : Google lisait déjà le contenu via rendu JS.
- **Bing/DuckDuckGo** : gain net (rendu JS partiel chez eux).
- **Crawlers IA (ChatGPT, Perplexity, Claude, etc.)** : gain maximal — aujourd'hui ils voient une page vide ; demain le contenu complet des guides → éligibilité aux citations dans les réponses IA, canal d'acquisition émergent parfaitement aligné avec votre positionnement expert.
- KPI de mesure : GSC « exploration » (pages découvertes→indexées plus vite), test « inspection d'URL » (HTML servi), logs de crawl Bing, apparitions dans les moteurs IA.

## 3. PAGES QUI EN BÉNÉFICIERAIENT RÉELLEMENT (par priorité)
1. **Les 17 guides** (`/guide/*`) — contenu long informationnel = 90 % du gain (c'est le contenu que les crawlers IA citeraient).
2. **7 pages piliers** (/accident-travail, /expertise-medicale, /mdph, /medecin-conseil, /protection-juridique…).
3. **/dossier-express** (fraîchement repositionnée — Lot A) et **/** (homepage, investigation pos. 31 en backlog).
4. Outils (/calculatrice-ipp, /calculatrice-aah, /agenda, /tarifs) — gain title/meta/JSON-LD, contenu interactif moindre.
   Exclus : tunnel de commande, admin, pages de suivi (aucun intérêt SEO, risque inutile).
   **Périmètre recommandé : ~28 URLs.**

## 4. RECOMMANDATION ARGUMENTÉE
**Option B — snapshots statiques versionnés, en 3 phases :**
- **Phase 0 (validation, 30 min)** : déployer 1 fichier témoin pour prouver que le serveur prod sert les fichiers réels avant le fallback SPA. Si échec → pivot vers l'option C (Worker Cloudflare).
- **Phase 1 (pilote, 3 pages)** : /dossier-express, /calculatrice-ipp, 1 guide. Vérifications : HTML complet servi aux bots (curl UA Googlebot), aucun flash visuel pour les humains, inspection URL GSC.
- **Phase 2 (généralisation, ~28 URLs)** : script `regenerate-snapshots` + procédure de pré-déploiement documentée dans la mémoire projet.
Pourquoi B : gain identique à A pour un risque de déploiement nul, entièrement réversible, aucune nouvelle infrastructure, compatible avec le rythme actuel (déploiements fréquents et maîtrisés), et il adresse le gain le plus différenciant (crawlers IA) sans toucher à une architecture qui vient d'être stabilisée. Next.js (D) reste l'horizon « propre » si le SEO devient le moteur n°1 de croissance — décision à réévaluer avec les données GSC du Lot A.
