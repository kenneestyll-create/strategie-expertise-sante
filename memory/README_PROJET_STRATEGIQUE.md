# README PROJET STRATEGIQUE
## Strategie & Expertise Sante — Vue d'ensemble non technique
### Date de creation : 06/04/2026

---

## CE QUE FAIT VRAIMENT LE SITE

Strategie & Expertise Sante est une plateforme qui aide les gens a comprendre et defendre leurs droits face a des situations de sante liees au travail : accidents du travail, maladies professionnelles, litiges avec les assurances, demarches MDPH.

Le site propose trois services principaux :

1. **Analyse gratuite** : Le client decrit sa situation. L'IA analyse et produit un rapport de 550 mots identifiant le vrai probleme, les leviers et l'action prioritaire.

2. **Analyse premium** (payante) : Rapport approfondi de 2000 mots avec cadre juridique, evaluation strategique, forces/faiblesses du dossier, plan d'action detaille.

3. **Dossier Express** (payant) : Le client envoie ses documents medicaux. L'IA les analyse, croise les pieces, identifie les incoherences et produit un rapport de pre-expertise.

---

## CE QUI LE REND FORT

### L'IA n'est pas generique
Elle connait les tableaux de maladies professionnelles, les baremes IPP, les jurisprudences de reference, les pieges des assurances, les procedures MDPH. Ce n'est pas ChatGPT qui repond a une question medicale — c'est un copilote specialise qui a ete calibre pendant des mois.

### Les garde-fous sont reels
L'IA a des interdictions strictes : pas de formulations generiques, pas de redondance entre sections, pas de promesse de resultat, pas d'extrapolation. 36 expressions sont explicitement bannies. Chaque rapport est score sur 7 criteres de qualite.

### La base metier est proprietary
Trois bases de connaissances ont ete construites a la main :
- Les contrats d'assurance emprunteur (GENERALI, GROUPAMA, CNP) avec leurs pieges
- Le regime special RATP et ses procedures specifiques
- L'univers MDPH (AAH, PCH, RQTH, CMI, recours)

Ce savoir-faire est injecte automatiquement dans les analyses quand le contexte le demande.

### Le systeme apprend (silencieusement)
Chaque analyse genere un signal anonymise qui enrichit la base de donnees. Un jour, quand suffisamment de cas auront ete traites (500 minimum), le systeme pourra identifier des patterns predictifs.

---

## OU EST LA VRAIE VALEUR

La valeur n'est pas dans le code React ou la base MongoDB. Elle est dans :

1. **Les prompts IA** : 12 000 caracteres de calibrage fin qui font la difference entre un rapport generique et un rapport premium exploitable
2. **Les bases de connaissances** : des centaines de lignes de savoir metier structure
3. **La logique de scoring** : 7 criteres qui permettent de detecter automatiquement quand la qualite baisse
4. **Les patterns anonymises** : 40 enseignements metier qui enrichissent chaque analyse
5. **La collecte V2** : une base de donnees qui se constitue progressivement pour la future IA predictive

---

## CE QU'IL FAUDRA FAIRE ENSUITE

### A court terme
- **Obtenir les credentials S3** : pour que les PDF soient telechargeables
- **Passer Stripe en mode live** : pour accepter les vrais paiements
- **Verifier le domaine Resend** : pour envoyer des emails au-dela du sandbox
- **Fournir les informations du fondateur** : pour corriger les hallucinations du chatbot

### A moyen terme
- **Enrichir les bases metier** : ajouter de nouveaux assureurs, de nouveaux regimes speciaux
- **Enrichir les patterns** : chaque cas traite manuellement devrait generer 1-2 nouveaux patterns
- **Integrer HubSpot** : pour le suivi CRM des prospects
- **Ajouter Google Analytics** : pour mesurer le trafic et les conversions

### A long terme (quand le feu V2 sera vert)
- **Construire l'IA predictive V2** : exploiter les 500+ cas pour generer des insights statistiques
- **Developper l'acces B2B** : offre professionnelle pour les cabinets d'avocats, experts
- **Internationaliser** : adapter pour d'autres pays (Belgique, Suisse — meme droit social)

---

## CE QU'IL FAUDRA EVITER

### Ne pas casser ce qui marche
Les prompts IA ont ete calibres et valides. Les modifier "pour voir" ou "pour simplifier" est le meilleur moyen de degrader la qualite sans s'en rendre compte.

### Ne pas promettre l'impossible
Le site est un outil d'aide a la decision. Il n'est pas un cabinet d'avocats. Le wording juridique est delibere et protecteur.

### Ne pas preciper la V2
La V2 predictive ne doit etre lancee que quand 500+ cas auront ete traites. Lancer avant, c'est produire des predictions non fiables qui detruisent la credibilite.

### Ne pas negliger le design premium
Le positionnement est haut de gamme. Chaque element (couleurs, typographie, ton) doit rester sobre, professionnel et rassurant. Pas de clipart, pas d'emojis, pas de couleurs flashy.

---

## RESUME EN 5 POINTS

1. Le site aide les gens a comprendre et defendre leurs droits sante/travail
2. L'IA est specialisee et calibree, pas generique
3. La vraie valeur est dans les prompts, les bases metier et le scoring qualite
4. Le systeme apprend silencieusement en vue d'une future V2 predictive
5. Tout est documente, versionne et concu pour etre repris par n'importe qui

---

*Document cree le 06/04/2026 — Kit d'Independance Projet S.E.S*
