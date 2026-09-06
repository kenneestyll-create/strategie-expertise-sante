# BENCHMARK E2E RÉEL — Dossier 108 pages (fichier réel fourni) — 06/09/2026
Aucune modification de code de production. Aucun déploiement. Test reproductible : `backend/tests/e2e_longctx_108p.py` + `e2e_longctx_suite.py`. Artefacts : ce dossier.

## 1. ARCHITECTURE RÉELLEMENT EXÉCUTÉE
PDF réel (9,5 MB, 108 pages) → `_process_files_payload` (chaîne d'extraction de production, source_type="test") → insertion dossier DB identique production → `_process_dossier_express` (fonction de production complète : injection knowledge patterns, PATH A natif Anthropic claude-sonnet-5 + thinking disabled, validateur de citations, génération PDF, stockage, email de livraison à delivered@resend.dev) → statut "completed / livre_client". RIEN n'a été mocké ni simulé.

## 2. TRAÇABILITÉ
- Dossier de test DB : id `testlc-a5168`, source_type `test` (exclu des KPI commerciaux)
- Logs : run.log (PATH A native réussie tentative 1 ; CITATION-CHECK total=11 verified=9 unverified=2 ; COMPLETE path=native_anthropic)
- Rapports générés : rapport_RUN1_prod_120k.md (pipeline prod), rapport_RUN3_fulltext_230k.md (comparaison texte intégral), texte_extrait.txt (extraction prod), texte_couche_native_230k.txt (couche OCR embarquée)

## 3. MESURES RÉELLES

### RUN 1 — PIPELINE DE PRODUCTION TEL QUEL
| Mesure | Valeur observée |
|---|---|
| Pages PDF | 108 |
| Caractères réellement extraits par la chaîne prod | **60 107** (extraction Gemini Vision 27/27 chunks) |
| Caractères transmis au LLM | 60 107 (< 120 000 → **la troncature 120k NE S'EST PAS déclenchée**) |
| Troncature à 120 000 | NON (voir « Limites » : le plafonnement réel intervient AVANT, à l'extraction) |
| Tokens input (API count_tokens Anthropic sur le payload exact) | **33 129** |
| Tokens output (API count_tokens sur le rapport) | **≈ 7 479** |
| Modèle réellement appelé | claude-sonnet-5 (log : path=native_anthropic) |
| Nombre d'appels LLM | **1** (PATH A, tentative 1 réussie — aucun fallback) |
| Temps extraction | **1 012,0 s (16 min 52 s)** |
| Temps LLM | **85,09 s** (timings DB) |
| Temps total E2E | 1 012 + 87,79 = **≈ 18 min 20 s** (analyse post-extraction : 87,79 s dont pdf 1,5 s, storage 0,85 s, email 0,34 s) |
| Erreurs / timeout | AUCUNE |
| Coût calculé sur tokens consommés | LLM : 33 129×2$/M + 7 479×10$/M = **0,141 $** + extraction Gemini 27 chunks : NON MESURÉ précisément (usage non exposé par LlmChat ; ordre de grandeur 0,3-0,6 $) |
| Longueur rapport final | 17 990 chars — **13/13 sections présentes, terminé proprement (non tronqué)** |
| Citations | validateur prod : 11 citations, 9 vérifiées, 2 non vérifiées |
| Livraison | PDF 102 141 B généré, email envoyé, statut livre_client |

### RUN 3 — COMPARAISON TEXTE INTÉGRAL (~230k), mêmes prompts, hors pipeline (aucun code prod modifié)
| Mesure | Valeur observée |
|---|---|
| Caractères transmis | **226 925** (couche texte OCR embarquée, 107/108 pages, extraite en 13,1 s par pdfplumber) |
| Tokens input réels (usage API) | **112 637** |
| Tokens output réels | 8 000 — **stop_reason=max_tokens → RAPPORT TRONQUÉ (11/13 sections)** |
| TTFT / temps LLM | 2,2 s / **90,8 s** |
| Coût réel | **0,3053 $** |
| Fallback proxy Emergent à cette taille | sonde réelle : accepté, réponse en 3,3 s |

## 4. RÉSULTAT FONCTIONNEL — EXPLOITATION DU DOSSIER COMPLET (preuve objective)
Dates présentes UNIQUEMENT après le caractère 120 000 du texte natif (pages ~55-108) : 12+ dates distinctes.
- RUN 1 (prod, texte Gemini 60k) en cite **0** ; le concept « consolidation » (3 occ., toutes en fin de dossier) : **0 occurrence** dans le rapport prod.
- RUN 3 (texte intégral) cite **12** de ces dates tardives et traite « consolidation » (5 occ.).
- Point commun sain : les deux runs identifient l'événement pivot (expertise d'arbitrage GAN du 07/09/2026, Drs FRABOULET/HIRSCH/ROUET) — date normalisée depuis « 07 SEPTEMBRE 2026 » (pas une hallucination, vérifié dans le texte source).

## 5. LIMITES RÉELLEMENT RENCONTRÉES (où → pourquoi → limite → chars envoyés)
1. **PLAFONNEMENT RÉEL = L'EXTRACTION, PAS la limite 120k.** `utils/document_extraction.py` → `_pdfplumber_pass_sync` ne lit que `pdf.pages[:30]` mais exige `lisibles ≥ 60 % du TOTAL des pages` → pour 108 pages il faudrait 65 pages lisibles sur un maximum comptabilisable de 30 : **impossible dès ~50 pages** → bascule systématique vers l'OCR Gemini même quand la couche texte est parfaite (ici 107/108 pages lisibles). Conséquences mesurées : 16 min 52 s d'extraction (vs 13,1 s en lecture directe) et texte réduit de 226 925 → 60 107 chars (**−73 % du contenu**). C'est LA cause racine des latences historiques sur gros dossiers.
2. La limite 120 000 chars (dossier_express.py l.612 + llm.py l.235) ne s'est pas déclenchée sur ce dossier — elle plafonnerait un texte intégral de 226 925 chars à 120 000 (perte silencieuse de ~47 %) si l'extraction était corrigée.
3. `max_tokens=8000` en sortie est insuffisant pour un dossier de cette richesse en texte intégral (RUN 3 tronqué à 11/13 sections). Le RUN 1 n'a pas été tronqué car son entrée appauvrie a produit un rapport moins dense.
4. Cap `wait_for(180 s)` PATH A : non atteint (85-91 s) — marge OK jusqu'à ~400-500k chars.

## 6. CONCLUSION : **PARTIEL**
- ✅ PASS technique : le pipeline actuel traite le dossier 108 pages de bout en bout sans erreur, sans timeout, avec livraison complète, 1 seul appel LLM natif, rapport 13/13 sections.
- ❌ FAIL qualitatif/latence : 17 min d'OCR inutile (couche texte lisible en 13 s), 73 % du contenu perdu à l'extraction, informations des pages tardives absentes du rapport, coût OCR superflu.
- ➜ Le long contexte Sonnet 5 fonctionne (112 637 tokens natif ET fallback proxy vérifiés) ; les correctifs nécessaires (À VALIDER, rien d'appliqué) : (1) corriger l'échantillonnage Level 1 (lire un échantillon représentatif de TOUTES les pages, seuil sur l'échantillon), (2) relever la limite 120k → ~800k chars, (3) max_tokens de sortie 8000 → 12 000 pour gros dossiers (architecture hybride option C), (4) cap PATH A 180 → 300 s pour gros dossiers.
