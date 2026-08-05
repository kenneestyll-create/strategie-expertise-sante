# DOCUMENTATION LOT 1 — Chaîne documentaire Dossier Express IA
Version : 1.0 — 2026-08-05. Statut : Lot 1 GELÉ (préparation déploiement production).
Objectif : maintenance et évolution sans dépendance à la mémoire du développeur.

## 1. Architecture du module qualité documentaire
Flux : Upload chunké → Extraction (pdfplumber → Gemini 2.5 Pro Vision par lots de 4 pages → Tesseract secours)
→ **build_quality_report()** (additive) → Écran qualité client (si pages problématiques) → Soumission
→ Analyse (Claude) → **verify_citations()** → PDF avec tableau documentaire → Email.

Fichiers :
- `backend/utils/quality_report.py` — module qualité (SF1+SF2). Pur, synchrone, AUCUN appel LLM.
- `backend/utils/citation_check.py` — validateur de citations (C3). Pur, déterministe.
- `backend/routes/dossier_express.py` — intégrations : `_process_files_payload` (quality_report + stats),
  submit/admin-bypass (quality_choice/quality_summary), `_process_dossier_express` (citation check + PDF).
- `backend/utils/pdf.py` — tableau documentaire C1/C2 (`generate_secured_pdf`, bloc `quality_summary`).
- `backend/constants/prompts.py` — §4 : règle de citation verbatim « … ».
- `frontend/src/utils/pdfExtractor.js` — remonte `qualityReport` au composant.
- `frontend/src/pages/DossierExpressPage.jsx` — écran `quality_check` (data-testids `quality-gate-*`),
  `handleQualityContinue` / `handleQualityReplace`, `performSubmit`.
- `frontend/src/components/admin/QualityStatsPanel.jsx` + `GET /api/admin/quality-stats` — tableau de bord.

## 2. Schémas de données
### Contrat A — page (OCR-agnostique, stable)
`{doc_index, doc_name, page, exploitability: 'ok'|'partial'|'unusable', chars, illisible_marks, weight}`
### quality_report (retourné par l'extraction)
`{formula_version, files, pages_total, pages_ok, pages_partial, pages_unusable, confidence_score,
 confidence_level, alerts[], per_document[], pages[]}`
### per_document
`{name, status, weight, essential, pages_total, pages_ok, pages_partial, pages_unusable, partial_pages[], unusable_pages[]}`
### Collections Mongo
- `docchain_stats` (anonymisé, AUCUN nom de fichier/texte/email) : métriques + created_at.
- `dossier_express` : + `quality_choice`, `quality_summary` (sans le tableau pages), `citation_stats {total, verified, unverified}`.

## 3. Calcul du score qualité (formula_version 1.1)
- Valeur par page : ok=1.0 · partial=0.5 · unusable=0.0
- Classement page : chars<20 → unusable ; chars≥150 ET 0 [illisible] ET ratio alphanum ≥0.5 → ok ; sinon partial.
  Page déclarée mais absente du texte balisé [Page N] → unusable. Fichier sans balises → fallback statut fichier.
- Score = Σ(poids_page × valeur) / Σ(poids_page) × 100.
- Niveaux : ≥97 Excellent · ≥90 Élevé · ≥75 Bon · ≥50 Moyen · <50 Faible.

## 4. Règles de pondération
- Pièce « essentielle » (poids 1.5) si nom de fichier OU 3000 premiers caractères contiennent un mot-clé :
  expertise, conclusions de l'expert, taux d'incapacité/IPP, consolidation, notification, décision, CDAPH,
  CPAM, caisse primaire, contrat d'assurance, conditions générales, avenant, tableau des garanties.
  Normalisation : minuscules, underscores/tirets → espaces.
- Alerte `essential_degraded` si une pièce essentielle a ≥1 page unusable.
- Plafonnement : pièce essentielle majoritairement illisible (>50 % unusable) → niveau max « Moyen ».
- Biais assumé : sur-inclusion possible (conservateur).

## 5. Limites connues (détail : LIMITES_MODULE_QUALITE_2026-08-05.md)
- Mesure l'EXPLOITABILITÉ de l'extraction, pas l'esthétique (page floue lue par Gemini = ok, voulu).
- Ne détecte pas : ordre des pages, pièce manquante (SF5/Phase D), pertinence juridique, page blanche volontaire vs scan raté.
- Seuils v1.1 a priori → calibrage après 50-100 dossiers réels.
- Score jamais montré en % au client (niveaux qualitatifs uniquement — décision UX).

## 6. Validateur de citations (C3)
- Prompt : toute citation « … » doit être verbatim + référence (pièce, page). Interdiction de « … » pour paraphrase.
- `verify_citations(analysis, documents_text)` : extrait les « … » de 20-400 caractères, normalise (ASCII,
  minuscules, alphanumérique), cherche en substring dans le texte source normalisé.
  Trouvée → référence doc/page déduite des balises `--- nom ---` et `[Page N]`. Introuvable → suffixe
  « [référence non vérifiée] ». Stats stockées + log `[CITATION-CHECK][id] total= verified= unverified=`.
- PDF : ligne « Traçabilité des sources : X citation(s) vérifiée(s) sur Y ».
- Limite : citation légèrement reformulée par le LLM → non vérifiée (faux rejet préféré au faux positif).

## 7. Comportement en cas d'erreur (garde-fous)
- build_quality_report échoue → quality_report=None, pipeline INCHANGÉ (log warning).
- Persistance docchain_stats échoue → non bloquant.
- verify_citations échoue → rapport livré NON annoté (log warning).
- Tableau documentaire PDF échoue → try/except interne, rapport livré sans tableau.
- Pas de quality_summary (anciens dossiers) → PDF rétrocompatible (bloc compact historique).
- Écran qualité : jamais bloquant, « Continuer » toujours en 1 clic, paiement/session conservés.

## 8. Tests réalisés
- Corpus 13 profils : 13/13 conformes, FP=0, FN=0 (v1.1). Charge : 6 extractions simultanées 6/6.
- Testing agent iteration_211 : 8/8 PASS (Phase B, backend+frontend).
- Test manuel visuel Phase B (cas propre/dégradé, remplacer/continuer).
- Étalon réel bout en bout (dossier 210988c0-f21) : 7/7 citations vérifiées, tableau PDF complet.
- Coût ajouté : ~0 €/dossier (aucun appel LLM supplémentaire ; +~80 tokens de prompt).

## 9. Corpus de référence (base de non-régression PERMANENTE)
- `backend/tests/corpus/` : 16 PDF (R1-R5 référence, D1-D8 dégradés) — NE PAS SUPPRIMER.
- `backend/tests/build_corpus.py` (génération), `run_corpus.py` (runner + attentes humaines + FP/FN),
  `load_test.py` (charge), `tests_phase_a.py`, `test_quality_gate_phase_b.py`.
- RÈGLE : toute évolution du pipeline documentaire doit repasser `run_corpus.py` avant déploiement.
  Profils texte seulement (rapide, 0 coût) : `python3 tests/run_corpus.py --only R1,R2,R3,R4,R5,D5,D6,D7`.

## 10. Points prévus pour les Lots 2 et 3
- Contrat B (fiche structurée) : posé, non implémenté → moteur de délais, incohérences, comparatif (Lot 2+).
- Pipeline de validateurs (post-processeur rapport) : le validateur citations est le 1er ; jurisprudence curatée (Lot 3) s'y branche.
- Adaptateur OCR : tout nouveau moteur doit produire le Contrat A.
- Reportés sur décision : Mistral OCR, fraude documentaire, comparatif dossiers, stats de réussite, mode pro, jurisprudence auto.
