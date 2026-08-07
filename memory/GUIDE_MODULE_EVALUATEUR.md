# GUIDE — Module « Évaluateur Expert » (mode d'emploi)
*Mis à jour le 06/08/2026 — fonctionnalité pérenne de Dossier Express IA.*

## À quoi ça sert
Donner un accès **gratuit, limité et traçable** à Dossier Express IA à des profils invités
(médecins experts, avocats, associations, comité scientifique, bêtas privées, partenaires),
sans paiement, sans pollution des statistiques commerciales, sans aucun impact SEO.

## Comment inviter un évaluateur (2 minutes)
1. **Dashboard admin → onglet « Dossier Express »** → carte dorée « Accès Évaluateurs Experts » (en haut).
2. Renseignez : nom (ex. « Dr de Thiballier »), email, type de profil, quota (vide = défaut), durée en jours (vide = défaut), notes internes éventuelles.
3. Cliquez **Créer** → le lien d'invitation est copié automatiquement dans votre presse-papiers.
4. Envoyez ce lien par email personnel à l'évaluateur (format : `https://strategie-expertise-sante.fr/evaluation-expert?t=...`).

## Ce que vit l'évaluateur
1. Il clique sur le lien → page privée (non indexée) → il confirme **son email** (celui de l'invitation).
2. Il découvre l'espace : concept, ce que l'outil n'est pas, méthode en 4 étapes, limites assumées, quota restant.
3. Bouton « Démarrer le test » → il arrive sur le parcours Dossier Express **réel** :
   - le paiement est remplacé par « Mode évaluation — Lancer l'analyse » ;
   - il vit exactement l'expérience client (upload, contrôle qualité, rapport PDF par email).
4. Chaque analyse décrémente son quota. Quota épuisé ou accès expiré → message propre avec votre contact.

## Gestion au quotidien (carte admin)
- **Quota** : modifiable à tout moment (champ à côté du compteur consommé/total).
- **+30 j** : prolonge l'expiration de 30 jours en un clic.
- **Interrupteur** : active/désactive l'accès instantanément.
- **Lien** : re-copie le lien d'invitation.
- **Poubelle** : supprime l'accès (les dossiers déjà générés restent en base, marqués eval_test).
- **Valeurs par défaut** (en haut à droite de la carte) : quota et durée appliqués aux futurs évaluateurs — modifiables librement, rien n'est codé en dur.

## Garanties intégrées
- Dossiers marqués `eval_test: true` + `evaluator_id` → **exclus** de : stats produit/business, rapport hebdomadaire, alerte « client réel », stats qualité (choix et citations).
- Page `/evaluation-expert` : noindex + absente du sitemap + `Disallow` dans robots.txt.
- Quota décrémenté côté serveur (anti-abus), token révocable, expiration automatique.
- Coût maximal par évaluateur : quota × ~0,25 € d'IA.

## Évolutivité prévue
Le champ « type de profil » permet demain de différencier les parcours (partenaires, comité
scientifique, bêtas) sans refonte : même collection, mêmes contrôles, droits ajustables.

## Point de vigilance connu (hors module)
Les invités VIP (`/acces-invite`) qui utilisent Dossier Express passent par l'ancien chemin
`/submit` **sans marquage** : leurs dossiers comptent dans les stats et peuvent déclencher
l'alerte « client réel ». Pour les évaluateurs, utilisez TOUJOURS le module Évaluateur
(lien `/evaluation-expert?t=...`), jamais l'accès VIP.
