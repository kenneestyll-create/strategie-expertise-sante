# RAPPORT P5 — INVESTIGATION « GÉNÉRÉ SANS EMAIL » (Dossier Express IA)
Date : 04/08/2026 — Rapport AVANT toute modification (conformément à l'ordre exécutif)

## Constat
Les dossiers de production affichent `delivery_status = "genere_sans_email"` / `email_sent = false`.
Ce statut est posé par `routes/dossier_express.py` ligne ~852 : `"livre_client" if email_sent else "genere_sans_email"`.
Le PDF est bien généré et stocké — seul l'envoi de l'email final échoue.

## Cause identifiée : QUOTA QUOTIDIEN RESEND ÉPUISÉ
Anomalie REPRODUITE le 04/08 en preview :
- 21:47:46 — email de confirmation : `You have reached your daily email sending quota.`
- 21:50:05 — email de livraison du rapport : même erreur.

### Mécanisme
1. L'environnement de PREVIEW utilise la même clé RESEND_API_KEY que la production (la clé est dans backend/.env, déployé avec l'app).
2. Les tâches planifiées de preview (relances d'inactivité 3 niveaux, rapports hebdo) envoient des emails EN MASSE à des adresses de test résiduelles (`ratelimit_reg_*@test.com`, `upload_test_*@test.com`, etc.) — des centaines d'envois constatés dans les logs (ex. 10/07).
3. Le quota quotidien Resend est consommé par ces envois parasites → les emails RÉELS de production (livraison des rapports payés) échouent les jours de saturation.

### Éléments d'écartement
- Enregistrement utilisateur / récupération d'email : hors de cause (adresses correctes en base).
- SMTP : hors de cause (API Resend, domaine vérifié DKIM/SPF/DMARC depuis mai).
- Workflow : hors de cause (l'échec est propre, notifié, non bloquant — comportement voulu).
- Cas particulier détecté et corrigé au passage (P4) : si Resend n'était pas configuré, l'étape était
  silencieuse ; un log d'erreur explicite a été ajouté (`Email NON envoye — Resend non configure`).

## Recommandations (EN ATTENTE D'ORDRE — rien n'a été modifié sur ce point)
1. **Séparer les clés** : clé Resend distincte pour preview (ou aucune clé en preview) — la production ne doit jamais partager son quota avec un environnement de test.
2. **Garde-fou d'envoi** : ne jamais envoyer aux domaines de test (@test.com, @example.com, pytest-*) depuis les schedulers.
3. **Purger** les adresses de test résiduelles des listes de relance d'inactivité.
4. **Surveiller le quota** Resend (ou upgrade de plan si le volume réel le justifie).
5. En cas d'échec email, le bouton admin « retry » permet déjà de relivrer le rapport.
