# Étude de faisabilité — Évolution Dossier Express IA vers plateforme d'analyse médico-juridique de référence
Date : 2026-08-04. LECTURE SEULE — aucun code modifié. Basée sur audit réel du code + recherche marché OCR.

## A. ARCHITECTURE ACTUELLE (constatée dans le code)
Pipeline : Upload chunké → extraction 3 niveaux (pdfplumber natif gratuit → Gemini 2.5 Pro Vision par lots de 4 pages → Tesseract secours) → analyse Claude (prompt 13 sections, garde-fous anti-hallucination) → scoring qualité interne 0-100 → PDF → email.
Par fichier, le backend produit déjà : pages, text_length, status (text_extracted/vision_extracted/vision_partial/extraction_failed…), method, preview. Le frontend reçoit `details` mais n'affiche qu'un comptage grossier. Gemini marque déjà [illisible]. Alertes admin sur échec OCR. Originaux stockés en object storage. `case_outcome_memory.py` stocke déjà des issues de dossiers (embryon P13). `quality_scoring.py` note chaque rapport.

## B. VERDICT PAR PRIORITÉ (existant % / faisabilité / coût dev / coût exploitation / impact)

| # | Fonctionnalité | Existant | Faisable sans refonte | Dev (j-h) | Coût/dossier | Impact réel |
|---|---|---|---|---|---|---|
| P1 | Contrôle qualité documentaire | ~40 % | OUI | 4-6 j | ~0 € (données déjà produites) | FORT |
| P2 | Pièces manquantes par type | ~50 % (post-analyse §10) | OUI | 4-6 j | +0,005 € (classif Flash) | FORT |
| P3 | Fiche de synthèse structurée | ~30 % | OUI | 4-6 j | +0,01-0,03 € | FORT (socle de P4/P5/P6/P8) |
| P4 | Score global de confiance | ~20 % (données existent) | OUI (dépend P1) | 2-3 j | 0 € | MOYEN-FORT |
| P5 | Détection délais + alertes | ~40 % (délais légaux dans prompt) | OUI (moteur de règles déterministe sur dates P3) | 5-8 j | ~0 € (Resend existant) | FORT, différenciant |
| P6 | Détection incohérences | ~60 % (exigé par prompt) | OUI (passe déterministe sur fiche P3) | 3-5 j | ~0 € | MOYEN (régularité) |
| P7 | Analyse sémantique avancée | ~70 % (Gemini 2.5 Pro + prompt) | Gain marginal | 1-2 j (tuning) | 0 € | FAIBLE incrémental |
| P8 | Matrice des preuves | ~25 % (texte déjà balisé [Page N] !) | OUI + vérification programmatique des citations | 4-6 j | ~0 € | TRÈS FORT (crédibilité) |
| P9 | Score de contestabilité | ~40 % (§8 matrice existante) | OUI (prudence YMYL) | 2-4 j | 0 € | MOYEN-FORT |
| P10 | Jurisprudences | ~50 % (base légale vérifiée ; juris. seulement si réf. exacte) | OUI via base locale CURATÉE (pas de génération libre) | 8-12 j + maintenance | ~0 € | MOYEN (risque hallucination si mal fait) |
| P11 | Recommandations stratégiques | ~85 % (§11+§12 déjà en place) | Déjà fait | 0-1 j | 0 € | MARGINAL |
| P12 | Anomalies documentaires (fraude) | ~5 % | Version minimale (métadonnées pypdf) seulement | 3-5 j | 0 € | FAIBLE + RISQUE juridique (fausse accusation) |
| P13 | Analyse comparative | ~15 % (case_outcome_memory existe) | NON à court terme (volume insuffisant + RGPD + chiffres trompeurs) | — | — | LONG TERME conditionné |
| P14 | Mode Professionnel | ~10 % (infra auth/PDF/agents existe) | OUI mais produit à part | 15-25 j | idem pipeline | FORT potentiel revenu B2B |

## C. RÉPONSES AUX QUESTIONS
1. **Déjà existant totalement/partiellement** : P11 (85 %), P7 (70 %), P6 (60 %), P2/P10 (50 %), P1/P5/P9 (40 %), P3 (30 %), P8 (25 %). Vraiment nouveaux : P12, P13, P14.
2. **Gain mesurable maximal** : P1+P4 (moins de rapports dégradés, transparence pré-paiement), P3 (socle technique), P8 (crédibilité mesurable), P2 (complétude), P5 (valeur vitale client).
3. **Recherche / peu fiable aujourd'hui** : P12 (forensique documentaire par IA = peu fiable, risque d'accusation à tort), P13 (stats sur volume insuffisant = chiffres juridiquement dangereux), P10 en génération libre (hallucination — d'où l'approche base curatée).
4. **Réalisable sans reconstruire** : P1-P9 intégralement dans l'architecture actuelle (FastAPI + pipeline existant). Aucune refonte.
5. **Modifications d'architecture** : ajout d'une étape "post-extraction" (fiche structurée JSON + agrégats qualité) entre OCR et analyse ; nouveau statut/champs dans documents/dossiers ; 1 écran frontend (rapport qualité + choix continuer/remplacer). C'est tout.
6. **Coût dev estimatif** : Lot 1 (P3+P1+P4+P2) ≈ 14-21 j-h. Lot 2 (P8+P5+P6+P9) ≈ 14-23 j-h. Lot 3 (P10, P14, P12 min) ≈ 26-42 j-h.
7. **Coût exploitation/dossier** : actuel ≈ 0,10-0,25 € (OCR Gemini ~0,05 €/PDF + analyse Claude). Après Lot 1+2 : +0,02-0,04 € max. Marge sur 97 € : intacte (>99,5 %).
8. **ROI attendu** : ↓ réclamations/regénérations (chaque rapport raté coûte du support + réputation) ; ↑ conversion (transparence qualité AVANT analyse) ; ↑ prix justifiable (matrice preuves = crédibilité pro) ; P14 = nouveau segment B2B (cf. ETUDE_B2B_PREMIUM_2026-06).
9. **Différenciants marché** : P8 (matrice preuves page+passage vérifiée programmatiquement — quasi inexistant chez les concurrents grand public), P5 (alertes délais), P1/P4 (transparence documentaire), P9 (contestabilité).

## D. COMPARATIF TECHNOLOGIES OCR (recherche 2026)
| Solution | Précision (benchmarks publics) | Prix/1000 pages | Intégration | Verdict pour nous |
|---|---|---|---|---|
| **Gemini 2.5 Pro (actuel)** | ~90+ compréhension doc, excellent français médical | ~5-15 € (via LLM) | DÉJÀ intégré (emergentintegrations, clé universelle) | Référence actuelle solide |
| Mistral OCR | 94,9 global, 98,9 scannés | 2-4 $ | Clé API séparée à gérer | Meilleur rapport qualité/prix PUR OCR ; fournit confiance/page (utile P1/P4). À tester en pilote |
| Google Document AI | 83-94,9 selon processeur | 1,5-30 $ | Compte GCP, complexe | Sur-dimensionné pour notre besoin |
| Azure Document Intelligence | ~89,5 | ~10 $ | Compte Azure | Pas d'avantage décisif |
| AWS Textract | ~85 ; formulaires 65 $/1000 p. | 1,5-65 $ | Compte AWS | Piège tarifaire formulaires |
| Tesseract (open source, déjà en fallback) | Faible sur scans médiocres | 0 € | En place | Garder en secours uniquement |

**Conclusion techno** : le goulot d'étranglement n'est PAS le moteur OCR — c'est la qualité des documents source (constat Generali/Etchepare confirmé par l'architecture). Un changement de moteur = gain MARGINAL sur la qualité finale des rapports. Mistral OCR mérite un pilote comparatif (coût + confiance par page) mais ce n'est pas le levier prioritaire. Le levier prioritaire = chaîne de contrôle documentaire (P1-P4).

## E. FEUILLE DE ROUTE PROPOSÉE
- **Court terme — Lot 1 "Chaîne documentaire" (14-21 j-h)** : P3 fiche structurée → P1 contrôle qualité par page + écran client (remplacer/continuer) → P4 score de confiance → P2 pièces manquantes. Meilleur ratio valeur/coût/complexité.
- **Moyen terme — Lot 2 "Crédibilité & vigilance" (14-23 j-h)** : P8 matrice des preuves (avec vérification programmatique anti-hallucination) → P5 moteur de délais + alertes → P6 passe incohérences déterministe → P9 contestabilité.
- **Long terme — Lot 3 (sur décision produit)** : P10 base jurisprudences curatée → P14 Mode Professionnel (étude produit dédiée) → P12 version minimale métadonnées. P13 : gel jusqu'à volume suffisant + cadrage juridique.
- **Pilote parallèle optionnel** : benchmark Mistral OCR vs Gemini sur 10 dossiers réels anonymisés (2-3 j-h).

Décisions attendues de l'utilisateur : GO/NO-GO Lot 1, périmètre exact, arbitrage pilote OCR.
