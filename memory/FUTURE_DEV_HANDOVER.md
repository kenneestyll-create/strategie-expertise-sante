# FUTURE DEV HANDOVER — Guide de reprise pour un futur developpeur
## Strategie & Expertise Sante
### Date de creation : 06/04/2026

---

## 1. CE QU'IL FAUT COMPRENDRE EN PREMIER

### Le projet en une phrase
S.E.S est une plateforme premium d'aide a la decision pour les victimes d'accidents du travail, maladies professionnelles et litiges sante. Elle utilise une IA specialisee (Claude Sonnet 4.5) pour generer des rapports strategiques personnalises.

### L'architecture en 30 secondes
- **Frontend** : React (port 3000), Tailwind CSS, Shadcn/UI
- **Backend** : FastAPI (port 8001), Python, prefix `/api` pour toutes les routes
- **Base de donnees** : MongoDB (via Motor, async)
- **IA** : Anthropic Claude Sonnet 4.5 (direct ou via Emergent proxy)
- **Paiements** : Stripe
- **Emails** : Resend
- **Stockage** : S3 (credentials manquantes actuellement)

### Les 3 produits coeur
1. **StrategiIA Basic** — Analyse gratuite (~550 mots) de la situation d'un client
2. **StrategiIA Premium** — Rapport approfondi payant (~2000 mots) avec cadre juridique, leviers, evaluation
3. **Dossier Express IA** — Pre-expertise documentaire payante (~2500 mots) des pieces medicales/administratives

### Le vrai actif du projet
Ce ne sont pas les pages web. C'est :
- Les **prompts IA** : 6 mois de calibrage pour obtenir un ton premium, humain, juridiquement prudent
- Les **bases de connaissances** : assurance, CCAS RATP, MDPH — structurees manuellement
- Le **moteur de patterns** : intelligence metier apprenante
- La **logique de scoring qualite** : 7 criteres calibres pour piloter la qualite des rapports

---

## 2. LES ERREURS CLASSIQUES A EVITER

### Erreur #1 : Modifier les prompts USER
Les prompts `STRATEGIIA_BASIC_PROMPT`, `STRATEGIIA_PREMIUM_PROMPT` et `DOSSIER_EXPRESS_PROMPT` ont ete calibres sur des dizaines de tests. Leur structure (sections, marqueurs, limites de mots) est exploitee par :
- Le frontend (readwall, sections)
- Le PDF (parsing markdown, titres)
- Le scoring qualite (detection des blocs premium)

Modifier un titre de section ou une contrainte casse potentiellement toute la chaine.

### Erreur #2 : Simplifier les prompts SYSTEM
Le `STRATEGIIA_SYSTEM_PROMPT` fait ~12 000 caracteres. Ca semble long. Mais chaque ligne a un role :
- Les formulations bannies empechent le LLM de produire du texte generique
- Les classes metier forcent la personnalisation
- Les regles anti-repetition empechent la redondance entre sections
- La logique de preuve de lecture empeche les rapports "passe-partout"

Supprimer des lignes "pour simplifier" degrade silencieusement la qualite.

### Erreur #3 : Changer le modele LLM sans recalibrage
Les prompts sont calibres pour Claude Sonnet 4.5. Passer a GPT-4, Gemini ou un autre modele sans recalibrer les prompts produira des rapports de qualite tres differente (structure, ton, longueur).

### Erreur #4 : Toucher au pipeline multi-stage sans comprendre
Le Dossier Express utilise un pipeline en 7 sections / 3 batches paralleles. Ce n'est pas de l'over-engineering : c'est la solution au timeout de 60 secondes du proxy Emergent. Chaque section est calibree pour etre generee en < 45 secondes.

### Erreur #5 : Ignorer le flag improvement_optout
Ce flag RGPD conditionne toute la collecte de donnees V2. S'il est a True, rien ne doit etre stocke. Si on le contourne, c'est une infraction RGPD.

### Erreur #6 : Modifier AdminDashboard.jsx sans tester exhaustivement
4000+ lignes, 14 onglets, dizaines de composants imbriques. Une modification dans l'onglet Config peut casser l'onglet Contacts si une variable partagee est touchee.

### Erreur #7 : Ecrire des URLs en dur
Toutes les URLs viennent des variables d'environnement. Le frontend utilise `REACT_APP_BACKEND_URL`, le backend utilise `MONGO_URL`, `STRIPE_API_KEY`, etc. Jamais de `localhost` dans le code.

---

## 3. LES FICHIERS A LIRE EN PRIORITE

Par ordre d'importance pour comprendre le projet :

1. **`/app/memory/IA_BASELINE_V1.md`** — Le gel officiel de l'IA V1 : ce qui est fige, pourquoi, comment evoluer
2. **`/app/backend/constants/prompts.py`** — Les prompts complets : le coeur du produit
3. **`/app/backend/utils/llm.py`** — Le pipeline LLM : comment les prompts sont executes
4. **`/app/backend/routes/strategiia.py`** — Le flux StrategiIA : de la requete au rapport
5. **`/app/backend/utils/quality_scoring.py`** — Le scoring qualite : comment la qualite est mesuree
6. **`/app/backend/routes/knowledge_patterns.py`** — Le moteur de patterns : l'intelligence apprenante
7. **`/app/memory/MASTER_ARCHITECTURE.md`** — L'architecture globale du projet
8. **`/app/memory/ZONES_GELEES_ET_MODIFIABLES.md`** — Ce qu'on peut toucher ou pas

---

## 4. CE QUI FAIT REELLEMENT LA VALEUR DU PROJET

### La qualite des sorties IA
Le produit vit ou meurt par la qualite de ses rapports. Un rapport generique tue la credibilite. Un rapport personnalise, structure et juridiquement solide justifie le prix premium.

### La profondeur metier
Les bases de connaissances (assurance, CCAS, MDPH) et les patterns anonymises donnent a l'IA une expertise sectorielle que les concurrents n'ont pas.

### Le cadre de confiance
Le disclaimer juridique, la logique RGPD, la prudence redactionnelle, les formulations conditionnelles — tout ca construit la confiance du client.

### Le pipeline technique
Le multi-stage, le streaming, le scoring qualite, le parallele — ce n'est pas de la complexite gratuite. C'est ce qui permet de generer des rapports de 2500 mots en < 2 minutes sans timeout.

---

## 5. LES PIEGES TECHNIQUES / METIER / JURIDIQUES

### Techniques
- **MongoDB ObjectId** : `_id` n'est pas JSON serializable. Toujours exclure avec `{"_id": 0}` dans les projections ou supprimer avant de retourner une reponse
- **Timeouts proxy** : Le proxy Emergent a un timeout de 60 secondes. C'est pourquoi le pipeline est splitte en sections paralleles
- **Hot reload** : Le frontend et le backend ont le hot reload. Pas besoin de redemarrer sauf pour les `.env` ou les dependances
- **S3 manquant** : Les credentials S3 ne sont pas configurees. Les PDF ne sont pas telechargeables actuellement

### Metier
- **Ne pas confondre les regimes** : CPAM (regime general) vs CCAS (RATP) vs MSA (agricole). Chaque regime a ses propres procedures, delais et interlocuteurs
- **Tableaux MP** : Un numero de tableau specifique (ex: 57C) a des conditions precises de delai et de travaux. Ne pas generaliser
- **IPP vs IP vs PGPF** : Ce sont 3 choses differentes. L'IPP est un taux, l'IP est un prejudice, la PGPF est une perte de revenus

### Juridiques
- **Jamais de conseil juridique** : Le produit est un "outil d'aide a la decision", pas un avis juridique. Ce wording exact est obligatoire
- **Jamais d'URL generee** : Les rapports ne doivent contenir aucun lien web
- **Jamais de promesse de resultat** : Pas de "vous allez gagner", pas de "vous avez 80% de chances"
- **RGPD** : Le flag improvement_optout est sacre. Si le client dit non, c'est non

---

## 6. CE QU'IL NE FAUT JAMAIS "SIMPLIFIER" BETEMENT

### Les prompts
"Trop long" ne veut pas dire "a raccourcir". Chaque ligne des prompts a ete ajoutee pour corriger un defaut observe (genericite, repetition, hallucination). Supprimer une ligne, c'est risquer de reintroduire le defaut.

### Le scoring qualite
"Complexe" ne veut pas dire "inutile". Les 7 criteres sont la seule maniere de detecter automatiquement une baisse de qualite IA. Sans scoring, les regressions sont invisibles.

### Les formulations bannies
36 expressions sont listees dans le scoring qualite. Ce n'est pas de l'over-engineering. C'est le resultat de mois d'observation des tics de langage de Claude qui degraduent la qualite percue.

### Le pipeline multi-stage
7 sections en 3 batches avec des pauses de 2 secondes. Ca semble baroque. Mais c'est la seule facon d'obtenir des rapports complets sans timeout, sans perte de contexte, et avec une progression visible pour le client.

### La separation StrategiIA / Dossier Express
Ces deux produits ont leurs propres routes, prompts, PDF et tunnels. Ce n'est pas un doublon : c'est une separation deliberee pour eviter la contamination croisee (un bug Dossier Express ne doit jamais casser StrategiIA).

---

## 7. CHECKLIST DE REPRISE

En arrivant sur le projet :

- [ ] Lire IA_BASELINE_V1.md
- [ ] Lire MASTER_ARCHITECTURE.md
- [ ] Lire ZONES_GELEES_ET_MODIFIABLES.md
- [ ] Verifier que le backend demarre (`tail -n 20 /var/log/supervisor/backend.err.log`)
- [ ] Verifier que le frontend compile (naviguer vers l'URL de preview)
- [ ] Se connecter en admin (`admin@accompagn-sante.fr` / `Admin2024!`)
- [ ] Parcourir les 14 onglets du dashboard
- [ ] Lancer une analyse StrategiIA Basic de test
- [ ] Verifier le scoring qualite du rapport genere
- [ ] Lire les fichiers de prompts (`constants/prompts.py`)
- [ ] Comprendre le pipeline LLM (`utils/llm.py`)
- [ ] Verifier l'etat du feu tricolore V2 (onglet Config)

---

## 8. CONTACTS ET CREDENTIALS

### Credentials de test
- Admin : `admin@accompagn-sante.fr` / `Admin2024!`
- Client demo : `demo@test.com` / `Password123!`

### Variables d'environnement critiques
- `MONGO_URL` : connexion MongoDB
- `DB_NAME` : nom de la base de donnees
- `ANTHROPIC_API_KEY` : cle Anthropic native
- `EMERGENT_LLM_KEY` : cle Emergent Universal (fallback)
- `STRIPE_API_KEY` : cle Stripe
- `JWT_SECRET` : secret JWT pour l'authentification

### Services tiers
- **LLM** : Anthropic Claude Sonnet 4.5 (via `ANTHROPIC_API_KEY` ou Emergent proxy)
- **Paiements** : Stripe (mode test actuellement)
- **Emails** : Resend (sandbox, domaine non verifie)
- **Stockage** : S3 (credentials manquantes — PDF non telechargeables)

---

*Document cree le 06/04/2026 — Kit d'Independance Projet S.E.S*
