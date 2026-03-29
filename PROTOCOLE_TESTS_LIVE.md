# PROTOCOLE DE TESTS LIVE — Strategie & Expertise Sante

> Tests obligatoires a effectuer avec les VRAIES cles de production avant ouverture commerciale.
> Chaque test doit etre execute, documente et valide.

---

## TEST 1 — Paiement Live Complet Reussi

**Objectif** : Valider le flux complet paiement -> generation -> livraison.

**Methode** :
1. Acceder a `/dossier-express` en mode client
2. Remplir un dossier de test realiste (type: "Accident du travail")
3. Proceder au paiement via Stripe (carte test live ou carte reelle)
4. Attendre la generation complete
5. Verifier la reception de l'email avec PDF

**Critere de validation** :
- [ ] Paiement accepte par Stripe
- [ ] Dossier visible en admin avec `delivery_status = livre_client`
- [ ] Email recu avec PDF en piece jointe
- [ ] PDF lisible et conforme au format V2 Premium
- [ ] Page de suivi client montre "Rapport disponible"
- [ ] Lien de telechargement fonctionnel

---

## TEST 2 — Paiement Annule

**Objectif** : Verifier que l'annulation est propre et sans effet de bord.

**Methode** :
1. Lancer un checkout Dossier Express
2. Sur la page Stripe, cliquer "Retour" / abandonner
3. Verifier le retour client

**Critere de validation** :
- [ ] Client redirige vers `/dossier-express?payment=cancelled`
- [ ] Aucun dossier cree en base
- [ ] Message client clair : "Paiement annule"
- [ ] Aucune charge sur la carte

---

## TEST 3 — Paiement Reussi + Incident IA Controle

**Objectif** : Verifier le comportement en cas d'echec IA apres paiement.

**Methode** :
1. Temporairement invalider la cle Anthropic (ou vider le champ)
2. Lancer un dossier de test (bypass admin ou Stripe test)
3. Observer le comportement

**Critere de validation** :
- [ ] Dossier en base avec `delivery_status = incident_technique`
- [ ] `processing_step = erreur_ia`
- [ ] Notification admin envoyee
- [ ] Email de delai envoye au client
- [ ] Page de suivi client montre "Verification complementaire en cours"
- [ ] Bouton "Relancer" visible en admin
- [ ] Apres restauration de la cle : relance reussie

---

## TEST 4 — Email Client Bien Recu

**Objectif** : Valider la delivrabilite et la qualite de l'email.

**Methode** :
1. Utiliser une adresse email reelle (pas de sandbox)
2. Lancer un dossier complet
3. Verifier la boite de reception (et spam)

**Critere de validation** :
- [ ] Email recu dans la boite principale (pas spam)
- [ ] Objet professionnel : "Votre Rapport Dossier Express IA est pret"
- [ ] Design premium (noir & or, logo, boutons)
- [ ] Piece jointe PDF presente et lisible
- [ ] Bouton "Telecharger mon rapport PDF" fonctionnel
- [ ] Bouton "Etre accompagne par un expert" fonctionnel

---

## TEST 5 — PDF Accessible et Conforme

**Objectif** : Verifier la qualite du PDF genere en production.

**Methode** :
1. Telecharger le PDF depuis l'email OU depuis le lien de suivi
2. Ouvrir sur ordinateur ET mobile

**Critere de validation** :
- [ ] PDF s'ouvre correctement
- [ ] Mise en page premium (en-tete, pied de page, sections)
- [ ] Contenu substantiel (> 1000 mots d'analyse)
- [ ] Pas de caracteres casses ou d'encodage defectueux
- [ ] Mentions legales presentes

---

## TEST 6 — Visibilite Admin Complete

**Objectif** : Verifier que l'admin voit tout en temps reel.

**Methode** :
1. Se connecter en admin
2. Aller a l'onglet Dossier Express
3. Verifier tous les elements

**Critere de validation** :
- [ ] KPI Live affiches (commandes du jour, taux, incidents)
- [ ] Mode de lancement visible et modifiable
- [ ] Dossier de test visible avec badges corrects
- [ ] `delivery_status` et `processing_step` affiches
- [ ] Bouton "Consulter" permet de voir l'analyse
- [ ] Filtres fonctionnels (Livres, Incidents, En attente)

---

## TEST 7 — Suivi Client Temps Reel

**Objectif** : Valider l'experience de suivi client.

**Methode** :
1. Acceder a `/dossier-express/suivi?id={dossier_id}`
2. Observer la timeline de progression

**Critere de validation** :
- [ ] Timeline affichee avec 7 etapes
- [ ] Etapes completees en vert
- [ ] Etape active avec animation
- [ ] Message premium et rassurant
- [ ] Bouton de telechargement visible quand rapport pret
- [ ] Aucun terme technique visible

---

## TEST 8 — Mode Indisponible

**Objectif** : Verifier que la desactivation est propre.

**Methode** :
1. En admin, passer en mode "Indisponible"
2. En client, tenter un checkout

**Critere de validation** :
- [ ] Checkout bloque avec message premium
- [ ] Aucune session Stripe creee
- [ ] En admin, re-passer en "Ouvert" restaure le service

---

## MATRICE DE RESULTATS

| Test | Objectif | Resultat | Date | Valideur |
|------|----------|----------|------|----------|
| T1 | Paiement complet | | | |
| T2 | Paiement annule | | | |
| T3 | Incident controle | | | |
| T4 | Email client | | | |
| T5 | PDF conforme | | | |
| T6 | Admin visibility | | | |
| T7 | Suivi client | | | |
| T8 | Mode indisponible | | | |

**TOUS LES TESTS PASSES : [ ] OUI / [ ] NON**

Date : ___________
