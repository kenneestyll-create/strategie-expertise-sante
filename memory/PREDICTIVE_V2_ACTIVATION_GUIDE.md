# PREDICTIVE V2 — GUIDE D'ACTIVATION
## Protocole complet pour activer la V2 le jour J
### Date de creation : 06/04/2026

---

## PREALABLE ABSOLU

Ne lisez ce guide que si le feu tricolore V2 est au VERT dans le dashboard admin.
Si le feu est rouge ou orange, l'activation est techniquement impossible.

---

## ETAPE 1 — VERIFIER LES CONDITIONS

1. Connectez-vous en admin
2. Allez dans l'onglet **Config**
3. Scrollez jusqu'a la section **IA Predictive V2 — Module dormant**
4. Verifiez que TOUS les verrous sont au vert :
   - Minimum 500 cas exploitables ✓
   - Score readiness >= 70 ✓
   - Diversite >= 3 familles ✓
   - Completude >= 50% avec blocage ✓
   - Feu tricolore = VERT ✓

Si un seul verrou est rouge : **ne pas activer**.

---

## ETAPE 2 — TESTER EN SANDBOX D'ABORD

Avant d'activer, utilisez le mode Sandbox :

1. Cliquez sur l'onglet **Sandbox** dans le panneau V2
2. Entrez une situation de test representative
3. Selectionnez le type de dossier
4. Cliquez **Analyser**
5. Verifiez que les alertes sont pertinentes et bien formulees
6. Repetez avec 3-5 situations differentes

Utilisez aussi le **Comparateur** :
1. Cliquez sur l'onglet **Comparateur**
2. Entrez l'ID d'une analyse existante
3. Verifiez la valeur ajoutee V2 par rapport a la V1

---

## ETAPE 3 — ACTIVER

1. Cliquez le bouton **Activer la V2** (vert)
2. Popup 1 : lisez et cliquez **Continuer**
3. Popup 2 : confirmez votre comprehension, cliquez **Etape finale**
4. Popup 3 : saisissez exactement **ACTIVER V2** dans le champ
5. Cliquez **Confirmer l'activation**

Le badge passera de "DESACTIVE" a "ACTIVE".

---

## ETAPE 4 — SURVEILLER

Apres activation :
- Verifiez les prochaines analyses dans le dashboard admin
- Les champs `v2_predictive` apparaitront dans les documents MongoDB
- Consultez le journal d'audit pour suivre les evenements
- Surveillez la qualite des rapports via le scoring existant

---

## ETAPE 5 — ROLLBACK SI NECESSAIRE

Si quelque chose ne va pas :
1. Cliquez le bouton rouge **Kill Switch — Desactiver immediatement**
2. La V2 est desactivee instantanement
3. Les futures analyses reviennent en V1 pur
4. Les analyses deja generees ne sont pas modifiees

Voir aussi : `PREDICTIVE_V2_ROLLBACK_GUIDE.md`

---

*Document cree le 06/04/2026 — Kit d'Independance Projet S.E.S*
