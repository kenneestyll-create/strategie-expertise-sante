# Étude d'architecture finale — Lot 1 (pré-développement)
Date : 2026-08-04. LECTURE SEULE — zéro modification. Complète le CDC_LOT1 du même jour.

## 1. VALIDATION GLOBALE + SIMPLIFICATIONS
SF1-SF6 confirmées pertinentes. 3 optimisations identifiées :
- FUSION SF1+SF2 → module unique backend `quality_report` (une seule passe calcule qualité/page + score agrégé). Gain 1-2 j.
- FUSION SF4 dans le post-processeur SF6 → une seule couche « enrichissement de rapport » (tableau documentaire + mentions P4 + validation citations). Gain 1 j.
- SIMPLIFICATION SF5 v1 : classification des pièces intégrée au prompt d'extraction Gemini existant (le bilan par page inclut le type de document) = ZÉRO appel LLM supplémentaire. Fallback mots-clés déterministe. Gain 1 j + 0,005 €/dossier économisé.
→ Estimation révisée : 14-19 j-h (vs 16-23).

## 2. ARCHITECTURE ÉVOLUTIVE (anti-dette technique)
3 contrats d'interface à poser dès le Lot 1 (coût marginal, bénéfice majeur) :
- **Contrat A — Schéma d'extraction par page** : {doc_id, page, exploitabilité, drapeaux, type_pièce, méthode}. Tout moteur OCR futur (Mistral, Document AI…) = simple adaptateur produisant ce schéma. OCR-agnostique.
- **Contrat B — Fiche structurée (JSON normalisé)** : socle direct du moteur de délais (Lot 2), des incohérences déterministes (Lot 2), des recommandations avancées, et de l'analyse comparative anonymisée (Lot 3) — les features anonymisées en dérivent.
- **Contrat C — Post-processeur de rapport (pipeline de validateurs)** : v1 = validateur de citations (SF6) ; Lot 3 = validateur jurisprudence branché sur la base curatée (collection Mongo dédiée `jurisprudence_curated` : réf. exacte + résumé + tags — injection additive dans le contexte du prompt).
- **Mode Professionnel** : même pipeline, couche de rendu/prompt différente. Compatible si les contrats A/B/C sont respectés.
Points d'attention :
1. L'écran qualité (SF3) doit gérer LES 3 chemins d'entrée existants : paiement Stripe, bypass admin, bypass VIP.
2. Versionner la formule de score (`formula_version` stocké avec chaque score) pour recalibrage futur sans casser l'historique.
3. Ne PAS dupliquer le texte extrait en base (documents_text déjà volumineux) : stocker uniquement les métadonnées par page. TTL comme les extractions.
4. Parsing tolérant du bilan par page Gemini : si JSON malformé → dégradation gracieuse vers le statut par fichier actuel (jamais d'échec bloquant).

## 3. INSTRUMENTATION
Déjà disponible (constaté) : `case_outcomes` (anonymisé, respecte improvement_optout), `tracking_events`, `quality_score` stocké par dossier, métriques extraction [EXTRACT-PIPELINE][A-E] (logs uniquement, non persistées).
| Donnée souhaitée | Dispo | Dev nécessaire |
|---|---|---|
| Pages moyennes/dossier | logs seulement | Persister (inclus socle) |
| Taux pages illisibles | Non (naît avec SF1) | Inclus SF1 |
| Qualité moyenne extraction | Partiel (statuts) | Agrégation |
| Types de docs absents | Non (naît avec SF5) | Inclus SF5 |
| Score moyen de confiance | Non (naît avec SF2) | Inclus SF2 |
| Fréquence remplacements | Non (naît avec SF3) | Event SF3 |
| Fréquence « Continuer malgré tout » | Non (naît avec SF3) | Event SF3 |
→ Dev : +1-2 j inclus dans le lot (collection `docchain_stats` anonymisée + endpoint admin d'agrégats).
RGPD : métriques techniques sans identifiant ni contenu = risque faible. Règles : aucun texte de document dans les stats, propagation de l'improvement_optout existant, mention « amélioration continue » dans la politique de confidentialité (mécanisme opt-out déjà en place).

## 4. PERFORMANCE (estimation réaliste)
- Temps machine : +0-2 s/dossier (signaux textuels + agrégation + validateur <1 s). Sortie Gemini +5-10 % tokens (bilan/page) ≈ +2-5 s sur l'extraction (déjà 1-3 min) : imperceptible.
- Temps humain : SF3 ajoute une étape de décision client (voulu — c'est la fonctionnalité).
- Mémoire : négligeable (pas de rendu image en v1, métadonnées légères). Pod 512 MB : sûr.
- Coût : +0,01-0,03 €/dossier.
- Stabilité : moteur d'analyse INTOUCHÉ ; seul risque réel = modification du prompt d'extraction → mitigé par parsing tolérant + tests sur dossiers étalons avant déploiement.

## 5. FIABILITÉ PAR FONCTIONNALITÉ (sans promesse irréaliste)
| SF | Niveau | Limites précises |
|---|---|---|
| SF1 signaux textuels | Fiable | Ne distingue pas « page blanche volontaire » vs scan raté ; manuscrit dense partiellement détecté |
| SF1 drapeaux Gemini | Fiable | Auto-évaluation LLM parfois inconstante → toujours croisée avec les signaux textuels |
| SF2 score | Fiable en relatif / Moyennement fiable en absolu au lancement | Seuils initiaux arbitraires → niveaux qualitatifs d'abord, calibrage après 50-100 dossiers |
| SF3 écran + choix A/B | Très fiable | UI déterministe ; seul enjeu = UX (ne jamais bloquer) |
| SF4 tableau documentaire | Très fiable | Données mesurées |
| SF4 formulations P4 | Moyennement fiable | Heuristique : on ne sait pas ce qu'on ne peut pas lire — formulations toujours au conditionnel |
| SF5 pièces manquantes | Fiable (présence) / Moyennement fiable (absence) | Afficher « non détecté », jamais « absent » affirmatif |
| SF6 validateur citations | Très fiable (déterministe) | Citations paraphrasées → seuil fuzzy = quelques faux rejets possibles (préférable aux faux positifs) ; dépend de la fidélité du balisage [Page N] |

## 6. DIFFÉRENCIATION CONCURRENTIELLE
| Capacité Lot 1 | ChatGPT/Claude/Gemini (upload direct) | Mistral OCR / Document AI | Legal AI pro (Harvey, Legora) |
|---|---|---|---|
| Contrôle qualité documentaire pré-analyse | ✗ | Partiel (confiance OCR brute) | ✗ |
| Score de confiance documentaire affiché | ✗ | ✗ | ✗ |
| Référentiel pièces FR médico-social (CSS/MDPH/assurance) | ✗ | ✗ | ✗ (cible avocats US/corporate) |
| Vérification programmatique des citations | ✗ (hallucinations possibles) | ✗ | Partiel |
| Rapport PDF structuré + workflow + email | ✗ | ✗ | ✓ mais 10-100× le prix |
Avantages DURABLES : (1) référentiel métier FR = actif propriétaire cumulatif ; (2) boucle de données instrumentation/case_outcomes = fossé cumulatif ; (3) confiance mesurable (validateur) = crédibilité YMYL défendable. NON durable : la qualité brute d'analyse LLM (se banalise) — d'où l'importance de déplacer la valeur vers la chaîne documentaire et les données propriétaires.

## 7. RECOMMANDATION FINALE : **GO AVEC AJUSTEMENTS**
Ajustements : fusion SF1+SF2 ; fusion SF4→SF6 (couche enrichissement) ; SF5 v1 sans appel LLM dédié ; instrumentation intégrée au socle ; contrats A/B/C posés dès le début.
Ordre optimal :
- Phase A (5-7 j) : module quality_report (SF1+SF2 fusionnés) + persistance stats + contrats A/B.
- Phase B (3-4 j) : écran client SF3 (3 chemins d'entrée) → **JALON validation utilisateur en preview**.
- Phase C (4-6 j) : couche enrichissement rapport (SF4+SF6 : tableau + P4 + validateur citations) → **JALON validation rapport**.
- Phase D (2-3 j) : SF5 pièces manquantes (référentiel + détection intégrée).
Reportable sans perte de valeur : formulations P4 avancées (v1 = 2 formulations simples), upgrade LLM de SF5, calibrage fin du score (post 50-100 dossiers), pilote Mistral (déclencheurs définis au CDC).
Total révisé : **14-19 j-h**, +0,01-0,03 €/dossier, zéro refonte, compatible Lots 2-3 par construction.
