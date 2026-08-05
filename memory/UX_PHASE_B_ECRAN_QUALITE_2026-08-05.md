# Proposition UX — Écran qualité client (Phase B) — pour validation utilisateur
Date : 2026-08-05. Aucun développement frontend effectué — réflexion préalable exigée par l'ordre de mission.

## Principe directeur
Le client a DÉJÀ payé 97 € quand l'écran apparaît (paiement avant upload). Objectif : renforcer la confiance
(« ce service vérifie mes documents avant d'analyser ») sans créer d'inquiétude ni de friction. Ton positif,
jamais alarmiste, jamais bloquant.

## Les 3 approches étudiées

### Version simple (bandeau informatif)
« Votre dossier contient 43 pages. 41 pages sont exploitables. 2 pages nécessitent une vérification. » + bouton Continuer.
✅ Zéro friction, zéro anxiété. ❌ Le client ne sait ni QUELLES pages ni QUOI faire → la valeur (remplacer une pièce clé) est perdue ; pas de consentement éclairé si qualité faible.

### Version intermédiaire (divulgation progressive) — RECOMMANDÉE
Structure :
1. En-tête POSITIF : « ✓ Vérification qualité effectuée — 41 pages sur 43 parfaitement exploitables »
2. Si pages problématiques : bloc repliable « 2 pages méritent votre attention » → détail : « Document 3 (Rapport d'expertise) — pages 7 et 8 : lisibilité insuffisante »
3. Deux choix équivalents visuellement (aucune culpabilisation) :
   - « Remplacer ces pages » (recommandé si pièce essentielle) → re-upload ciblé
   - « Continuer avec mon dossier actuel » → 1 clic, mention discrète : « certaines conclusions pourront être limitées par la qualité de ces pages » (consentement loggé)
4. Cas dossier parfait (majorité) : simple confirmation verte 2 secondes, aucune étape supplémentaire ressentie.
✅ Valeur maximale, anxiété maîtrisée, consentement éclairé, friction quasi nulle pour les bons dossiers. C'est le standard des services premium (assurance en ligne, banque).

### Version avancée (score + explication détaillée)
Score de confiance chiffré + niveau + explication par page + alertes pièces essentielles.
✅ Transparence maximale. ❌ Pour un client grand public stressé (contexte médico-juridique), un « score 66 % — Moyen » AVANT l'analyse crée de l'anxiété et des appels support ; sur-information contraire à l'objectif « augmenter la confiance, pas la complexité ».

## Recommandation argumentée pour un service à 97 €
**Version intermédiaire côté client** + **version avancée réservée au RAPPORT et à l'admin** :
- Écran client : divulgation progressive (v. intermédiaire), niveaux qualitatifs uniquement (jamais de % brut).
- Le score chiffré et le détail complet apparaissent dans le rapport final (tableau documentaire, Phase C) où ils CRÉDIBILISENT le travail au lieu d'inquiéter avant.
- Alerte pièce essentielle dégradée (v1.1) : affichée en priorité avec formulation orientée solution (« votre rapport d'expertise contient 2 pages illisibles — le remplacer améliorera nettement l'analyse »).
- Admin : accès au détail complet (docchain_stats + quality_report) pour le support.

## Garde-fous UX
- JAMAIS de blocage : « Continuer » toujours accessible en 1 clic.
- Cas parfait (attendu majoritaire) : aucune étape ressentie (confirmation automatique).
- Wording positif : « exploitable / mérite votre attention », jamais « défaillant / mauvais / rejeté ».
- Choix loggé en base (consentement éclairé → protection juridique du service).
- 3 chemins d'entrée gérés : Stripe, bypass admin, bypass VIP.
