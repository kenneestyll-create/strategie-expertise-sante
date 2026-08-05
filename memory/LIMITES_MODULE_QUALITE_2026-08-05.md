# Limites du module qualité documentaire (Phase A/B) — documentation de clôture
Date : 2026-08-05. Exigée par l'ordre de mission pré-commercialisation (§1).

## 1. Détecté AUTOMATIQUEMENT (fiable, testé sur corpus 13/13)
- Pages sans texte exploitable (vides, bruit, contraste insuffisant non lu par l'OCR) → « unusable », localisées par document et numéro de page.
- Pages partiellement lisibles (texte court, marqueurs [illisible], bruit OCR) → « partial ».
- Score de confiance pondéré (v1.1) : pièces essentielles (expertise, notification, décision, contrat — mots-clés) pèsent 1,5×.
- Alerte « pièce essentielle dégradée » + plafonnement du niveau si une pièce essentielle est majoritairement illisible.
- Traçage du choix client (auto_ok / continue_degraded / replaced_after_warning / not_available) en logs + base.
- Statistiques techniques anonymisées (docchain_stats) : pages, taux illisibles, scores, alertes.

## 2. Nécessite un JUGEMENT HUMAIN (le module ne le fait pas, par conception)
- Distinguer une page blanche volontaire (verso) d'un scan raté → le module signale, l'humain (client) tranche via l'écran de choix.
- Évaluer si une page illisible contient une information décisive → impossible de savoir ce qu'on ne peut pas lire ; formulations toujours au conditionnel (Phase C).
- Pertinence juridique des pièces fournies (une pièce lisible peut être hors sujet).
- Qualité du raisonnement du rapport final → relecture humaine des rapports (validation humaine maintenue en pré-commercialisation).

## 3. Traité dans les LOTS FUTURS
- Pièces MANQUANTES par type de dossier (référentiel + check-list) → SF5, Phase D.
- Ordre des pages incorrect, incohérences de dates/taux entre pièces → fiche structurée + passes déterministes, Lot 2.
- Tableau documentaire dans le rapport, mentions d'impact, validateur de citations → Phase C (préparée, non activée).
- Moteur de délais/alertes, matrice des preuves complète → Lot 2.
- Jurisprudence curatée, mode professionnel, comparatif anonymisé → Lot 3 (reportés sur décision utilisateur : pas assez de données réelles + risque juridique).

## 4. Points d'attention connus (v1.1)
- Seuils (150/20 caractères, ratio 0,5) fixés a priori → calibrage prévu après 50-100 dossiers réels.
- Détection « pièce essentielle » par mots-clés : sur-inclusion possible (courrier citant « expertise ») — biais conservateur assumé.
- Une page floue/tournée LUE intégralement par Gemini est classée exploitable : comportement voulu (on mesure l'exploitabilité de l'extraction, pas l'esthétique du scan).
- Le score chiffré n'est PAS montré au client (niveaux qualitatifs uniquement) — décision UX validée.

## 5. Base de non-régression permanente
- Corpus : /app/backend/tests/corpus/ (16 PDF) — NE PAS SUPPRIMER.
- Runner : python3 tests/run_corpus.py (attentes humaines codées, FP/FN automatiques).
- Charge : python3 tests/load_test.py. Phase B e2e : tests/test_quality_gate_phase_b.py (pytest, créé par le testing agent).
- Règle : toute évolution du pipeline documentaire DOIT repasser le corpus avant déploiement.
