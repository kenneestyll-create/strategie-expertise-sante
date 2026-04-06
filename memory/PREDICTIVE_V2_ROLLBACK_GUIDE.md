# PREDICTIVE V2 — GUIDE DE ROLLBACK
## Procedure de retour arriere immediat
### Date de creation : 06/04/2026

---

## SCENARIO : LA V2 EST ACTIVE ET IL FAUT LA DESACTIVER

### Methode 1 — Kill switch admin (recommandee)

1. Connectez-vous en admin
2. Onglet Config → section "IA Predictive V2"
3. Cliquez le bouton rouge **Kill Switch — Desactiver immediatement**
4. Le flag passe a OFF instantanement
5. Toutes les futures analyses reviennent en V1 pur
6. Aucun redemarrage necessaire

### Methode 2 — Modification directe en base (si l'admin est inaccessible)

```bash
# Connexion MongoDB
mongosh "votre_mongo_url/votre_db_name"

# Desactiver la V2
db.app_config.updateOne(
  { key: "predictive_v2_enabled" },
  { $set: { value: false, updated_at: new Date().toISOString() } }
)

# Verifier
db.app_config.findOne({ key: "predictive_v2_enabled" })
```

### Methode 3 — API directe (si le dashboard est indisponible)

```bash
TOKEN=$(curl -s -X POST "votre_url/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@accompagn-sante.fr","password":"votre_mot_de_passe"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -X POST "votre_url/api/predictive-v2/deactivate" \
  -H "Authorization: Bearer $TOKEN"
```

---

## CE QUI SE PASSE APRES LE ROLLBACK

- Les hooks V2 dans strategiia.py et dossier_express.py lisent le flag = false
- Le `if await is_v2_enabled(db)` retourne False immediatement
- Aucune logique V2 ne s'execute
- Aucun champ `v2_predictive` n'est ajoute aux nouvelles analyses
- Les analyses deja generees AVEC V2 conservent leurs donnees V2 (non supprimees)
- Le scoring qualite, les PDF, les paiements, les emails — tout reste identique

---

## CE QUI NE CHANGE PAS

- Les prompts USER : inchanges
- La structure PDF : inchangee
- Les pages publiques : inchangees
- Les paiements Stripe : inchanges
- Le tunnel client : inchange
- Le scoring qualite : inchange

---

*Document cree le 06/04/2026 — Kit d'Independance Projet S.E.S*
