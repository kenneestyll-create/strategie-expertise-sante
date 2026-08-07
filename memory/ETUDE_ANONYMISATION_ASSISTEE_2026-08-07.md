# ÉTUDE — « Anonymisation assistée avant analyse » (module futur)
*07/08/2026 — Étude sur ordre. AUCUN développement réalisé. Décision utilisateur requise.*

## 1. Rappel du besoin
Permettre à un expert (puis, à terme, à un client) de déposer un dossier RÉEL et de le faire
anonymiser de façon assistée AVANT que l'IA d'analyse ne le traite :
réduction de la charge de préparation, utilisation de dossiers réels, confiance RGPD renforcée.

## 2. Constat d'architecture (déterminant pour la faisabilité)
Le pipeline actuel est : upload chunké → OCR Gemini 2.5 Pro (texte intégral) → **le texte extrait
revient au navigateur** (`form.documents_text` + `document_details`) → soumission → analyse Claude.

**Conséquence clé : l'analyse ne lit QUE le texte extrait, jamais le PDF.**
L'anonymisation peut donc se faire **au niveau du texte**, entre l'extraction et la soumission —
sans toucher au pipeline d'analyse, sans réécriture de PDF (la rédaction visuelle de PDF, type
caviardage, est 10× plus lourde et inutile ici).

⚠️ Point de vigilance actuel : les PDF **originaux** sont aussi stockés (S3 + collection `documents`,
visibles dans l'admin). En mode anonymisé, il faudra proposer de **ne pas conserver les originaux**
(ou de ne conserver que la copie texte anonymisée), sinon l'anonymisation est illusoire côté serveur.

## 3. Détection automatique des données personnelles — options
| Option | Méthode | Recall | Coût/dossier | Verdict |
|---|---|---|---|---|
| A. Déterministe | Regex : NIR (13-15 chiffres clé comprise), dates de naissance, emails, téléphones, codes postaux+villes, n° de dossier | Excellent sur formats structurés, nul sur les noms | 0 € | Indispensable mais insuffisant seul |
| B. NER locale | spaCy `fr_core_news_lg` ou Microsoft Presidio (PII engine) | Moyen en français médical (~80-85 % noms) | 0 € mais +250-400 MB RAM (**risque sur le tier 512 MB actuel**) | Déconseillé sur l'infra actuelle |
| C. Passe LLM | 1 appel (Gemini Flash ou Claude Haiku) sur le texte extrait → JSON `{entités: [{type, valeur, occurrences, remplacement_propose}]}` | Excellent (noms, employeurs, lieux, contexte) | ~0,003-0,01 € | Recommandé |
| **Hybride A+C (recommandé)** | Regex d'abord (garantie sur NIR/dates/contacts), LLM ensuite (noms, employeurs, adresses) ; fusion dédupliquée | Meilleur des deux | ~0,01 € | ✅ |

Types d'entités à détecter : nom/prénom (patient, médecins, tiers), NIR, date de naissance,
adresses, téléphone/email, employeur/établissement, n° de dossier CPAM/MDPH, RPPS/ADELI.

## 4. Prévisualisation & validation humaine (principe : rien n'est supprimé sans l'humain)
Nouvelle étape frontend entre « extraction terminée » et « lancer l'analyse » :
- Tableau des entités détectées : type · valeur trouvée · nb d'occurrences · remplacement proposé
  (pseudonymes stables : « Mme A. », « Dr B. », « Établissement E1 », « [NIR masqué] », dates → année seule).
- Chaque ligne : case à cocher (anonymiser / conserver) + remplacement éditable.
- Ajout manuel possible (sélection d'un passage non détecté → « anonymiser ceci »).
- Aperçu du texte final avec surlignage des substitutions AVANT validation.
- Bouton unique « Valider et lancer l'analyse » → seule la copie anonymisée part au backend.
- Cohérence garantie : le même pseudonyme remplace toutes les occurrences (mapping stable),
  ce qui préserve la lisibilité du rapport (« Mme A. » traçable dans les citations).

## 5. Conservation — règles RGPD proposées
- **Seul le texte anonymisé** est soumis, stocké (`documents_text`), analysé et cité dans le rapport.
- **La table de correspondance (pseudonyme ↔ vraie valeur) ne quitte JAMAIS le navigateur**
  (mémoire de session uniquement, rien en base) — c'est ce qui distingue une vraie anonymisation
  serveur d'une simple pseudonymisation (le RGPD continue de s'appliquer aux données pseudonymisées :
  ici, côté serveur, plus aucune donnée identifiante n'existe).
- Mode anonymisé ⇒ originaux non conservés : upload S3 des PDF sources désactivé (ou purge
  immédiate post-OCR). Les chunks d'upload expirent déjà (TTL 1 h, MongoDB).
- Le rapport PDF final et la mémoire IA (`case_outcomes` — déjà 100 % sans PII, vérifié le 07/08)
  ne contiennent que des pseudonymes.
- Limite résiduelle à assumer honnêtement : l'OCR transite par Gemini AVANT anonymisation
  (inévitable pour lire des scans). Mitigation : mention claire + DPA Google en sous-traitance,
  et pour les experts, alternative « cas fictif » déjà disponible.

## 6. Impact coût & performance
- **Coût IA** : +1 appel de détection sur ~20 000 caractères ≈ **+0,003 à 0,01 €/dossier**
  (analyse actuelle ≈ 0,25 €) → impact **< 4 %**. Remplacements = pur Python, 0 €.
- **Latence** : +4 à 10 s pour la détection (parallélisable par fichier), + le temps de relecture
  humaine (voulu). Aucun impact sur le temps d'analyse (texte de même taille).
- **RAM** : négligeable en hybride A+C (regex + appel API). L'option NER locale est écartée
  précisément pour le tier 512 MB.

## 7. Compatibilité avec l'architecture actuelle
- **Point d'insertion unique** : le frontend possède déjà le texte extrait avant soumission →
  1 nouvel endpoint `POST /api/anonymize/detect` (texte → entités JSON) + 1 écran de validation.
- **Zéro modification** : pipeline d'analyse, prompts, PDF, emails, quotas évaluateurs, source_type,
  Case Outcome Memory, pages publiques gelées.
- Réutilisation : `llm.py` (appel), patterns UI existants (étape contrôle qualité déjà présente
  dans le parcours — l'anonymisation serait une étape sœur, même ergonomie).
- Rollout proposé : **V1 réservée au mode évaluateur** (flag sur `expert_access`), V2 option
  publique payante ou incluse, V3 (non recommandée) caviardage visuel des PDF.

## 8. Risques identifiés
1. OCR imparfait sur scans dégradés → noms mal orthographiés non détectés → **c'est pour cela que
   la validation humaine avec aperçu surligné est non négociable** (l'expert reste responsable de
   la relecture — à écrire explicitement dans l'UI).
2. Faux positifs (ex. « Dr » dans une citation légale) → résolu par les cases à cocher.
3. Sur-anonymisation nuisant à l'analyse (ex. masquer les dates de procédure casserait le calcul
   des délais) → règle : **dates de procédure conservées, seule la date de naissance est réduite à l'année** ;
   les fonctions (« l'employeur », « le médecin-conseil ») remplacent les noms sans perte analytique.
4. Confiance excessive (« l'outil a tout anonymisé ») → formulation prudente : « anonymisation
   ASSISTÉE, sous votre contrôle », jamais « garantie ».

## 9. Estimation de réalisation (si validée)
- Backend : endpoint détection hybride + option « ne pas conserver les originaux » — ~0,5 jour.
- Frontend : écran de prévisualisation/validation + aperçu surligné — ~1 jour.
- Tests E2E + rédaction mentions RGPD — ~0,5 jour.
- **Total : ~2 jours**, coût récurrent ~0,01 €/dossier, aucun impact SEO, aucun impact public.

## 10. Recommandation
GO pour une **V1 texte, hybride regex+LLM, réservée aux évaluateurs**, avec validation humaine
obligatoire et non-conservation des originaux en mode anonymisé. Déclencheur idéal : après le
retour du Dr de Thiballier (son avis sur cette étape serait précieux — elle peut même lui être
présentée comme question dans un échange de suivi).

**EN ATTENTE DE VALIDATION UTILISATEUR — rien n'a été développé.**
