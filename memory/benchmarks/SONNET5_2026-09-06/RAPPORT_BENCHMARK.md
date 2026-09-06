# BENCHMARK CONTRÔLÉ — claude-sonnet-4-5-20250929 vs claude-sonnet-5
Date : 06/09/2026 — Cas fictif Mme DEMONSTRATION Claire (6 pièces, MP hors tableau, refus CPAM IPP 20 % < 25 %)
Entrées STRICTEMENT identiques : même extraction (pipeline production), même system prompt (DOSSIER_EXPRESS_SYSTEM_PROMPT), même user_msg, max_tokens 8000.
Sauvegarde préalable : /app/memory/backups/MIGRATION_SONNET5_2026-09-04/ (commit e192447, md5 vérifiés).

## Runs
| Run | Modèle | Config | Temps | Tokens in/out | Chars | stop_reason | Coût |
|---|---|---|---|---|---|---|---|
| A | claude-sonnet-4-5-20250929 | prod actuelle | 153,0 s | 8 299 / 8 000 | 25 707 | **max_tokens (TRONQUÉ)** | 0,1449 $ |
| B | claude-sonnet-5 | défaut (thinking adaptatif ON) | 79,5 s | 10 978 / 8 000 | 9 237 | max_tokens (TRONQUÉ, thinking a mangé le budget) | 0,1020 $ |
| C | claude-sonnet-5 | **thinking désactivé** (drop-in) | 76,7 s | 10 978 / 7 263 | 17 593 | **end_turn (COMPLET)** | 0,0946 $ |
| D | claude-sonnet-5 | thinking ON + max 16k | 76,5 s | 10 978 / 7 164 | 17 264 | end_turn (complet) | 0,0936 $ |

## DÉCOUVERTES CRITIQUES
1. **Sonnet 5 a le « adaptive thinking » activé PAR DÉFAUT** (doc Anthropic officielle). Un simple remplacement du nom de modèle en production TRONQUERAIT les rapports (run B). Obligatoire : `thinking: {"type": "disabled"}` sur les appels natifs. L'ancien `budget_tokens` renvoie une 400 ; temperature/top_p non défaut → 400.
2. **Le run A révèle un problème LATENT de la prod actuelle** : sur ce cas lourd, Sonnet 4.5 atteint le plafond 8 000 tokens et la conclusion (§13) est coupée en pleine phrase. La prod actuelle tronque donc déjà les très gros dossiers.
3. Tokenizer Sonnet 5 compte ~32 % de tokens d'entrée en plus sur le même texte (10 978 vs 8 299) — déjà intégré dans les coûts mesurés.

## Comparaison qualitative (A tronqué vs C complet), vérifiée pièce par pièce
| Critère | Sonnet 4.5 (A) | Sonnet 5 nothink (C) | Verdict |
|---|---|---|---|
| Exactitude | 1 erreur d'ordre dans la chronologie (02/04 placé après 28/04) ; « délai probablement expiré » spéculatif et contestable | Chronologie exacte et ordonnée ; délais énoncés sans sur-affirmation | **S5** |
| Fidélité aux documents | Bonne, citations verbatim | Supérieure : cite le fichier source de chaque citation ; relève la nuance « en lien évoqué » du CMI ; détecte que l'ARRÊT INITIAL du 18/02 est ABSENT des pièces (vrai — seul le scan de prolongation 15/04→15/06 est fourni) — non vu par 4.5 | **S5** |
| Hallucinations / affirmations non justifiées | Invente des probabilités de succès (« 40-50 % », « 60-70 % », « 70-80 % ») et un coût d'expertise (« 800-1500 € ») SANS source — contraire à la règle du system prompt ; SE « probable 4 à 5 » non sourcé | AUCUNE affirmation chiffrée non sourcée ; écrit « chances de succès : à ce stade indéterminées » — conforme à la règle | **S5 (net)** |
| Analyse PTIA / distinction IPP-PTIA | Cas démo sans volet PTIA : aucun des deux n'introduit de PTIA hors sujet (bonne retenue des deux). S5 explique mieux la mécanique seuil 25 % → CRRMP (évaluation AVANT imputabilité) | Égalité (+ pédagogie S5). ⚠️ Critère PTIA non testable sur ce cas — benchmark PTIA dédié possible avec un jeu de pièces assurance | = |
| Comparaison des évaluations médicales | Nomme Dr EXEMPLE et Dr SPECIMEN (pas Dr TYPE) | Compare mieux le fond (asymétrie d'objectivation : PHQ-9 vs aucune échelle côté médecin-conseil) mais NE NOMME PAS les médecins (« psychiatre traitant », « médecin-conseil ») | Partagé — ⚠️ point de surveillance S5 (citation nominale) |
| Cohérence juridique | L.461-1, R.461-8, L.433-1, R.433-1, L.434-1, L.452-1 — tous exacts | L.461-1, R.461-8, **L.141-1/R.141-1 (expertise médicale technique — la voie exacte pour contester le taux, absente chez 4.5)**, L.142-4, L.142-8, L.431-1, L.434-2, L.452-1 — tous exacts | **S5** |
| Structure du rapport | 13 sections conformes mais §13 TRONQUÉE | 13 sections conformes, complètes, + disclaimer final conforme | **S5** |
| Richesse / longueur | Plus détaillé (taux IJ 60/80 %, échelles HAD/SF-36 nommées, FI approfondie) mais au prix de la troncature | Plus concis, complet, stratégie plus actionnable (« sous 15 jours : CRA ») | Partagé |
| Informations perdues 4.5 → 5 | — | Non citées par S5 : sertraline 100 mg (traitement), échelles HAD/SF-36 nommées, taux IJ chiffrés, noms des médecins. AUCUNE info STRUCTURANTE perdue (le traitement reste sans impact stratégique) | à noter |
| Nouvelles affirmations non justifiées chez S5 | — | AUCUNE détectée (tout est traçable aux pièces) | ✅ |
| Temps de réponse | 153,0 s | 76,7 s | **S5 (2× plus rapide)** |
| Coût réel mesuré | 0,1449 $ | 0,0946 $ | **S5 (−35 %)** |

## VERDICT
Sonnet 5 (thinking désactivé) est ≥ 4.5 sur la qualité, SUPÉRIEUR sur la fiabilité (zéro invention chiffrée, meilleure fidélité documentaire, détection de pièce manquante), 2× plus rapide, −35 % de coût, et termine ses rapports sans troncature là où 4.5 est coupé. Critère de migration REMPLI.
Points de surveillance post-migration : (1) citation nominale des médecins moins spontanée — le prompt existant l'impose pour les expertises multiples, à surveiller sur les 1ers dossiers réels multi-expertises ; (2) rapports plus concis (~17k vs ~25k chars).

## PLAN DE MIGRATION PRÉPARÉ (NON APPLIQUÉ — attente validation user)
1. `utils/llm.py` (ZONE GELÉE — modification sous protocole IA_BASELINE_V1) :
   - `llm_sync_call` (voie native) : ajouter `thinking={"type": "disabled"}` au `client.messages.stream(...)`
   - l.206 `generate_section_llmchat` : "claude-sonnet-4-5-20250929" → "claude-sonnet-5" (⚠️ voie fallback proxy Emergent : vérifier le support du paramètre thinking par le proxy ; sinon conserver 4.5 sur le fallback dans un 1er temps)
2. `routes/strategiia.py` (l.58, 83, 212) : modèle → "claude-sonnet-5" (+ thinking disabled sur l'appel natif)
3. `routes/dossier_express.py` (l.628) : modèle → "claude-sonnet-5"
4. NE PAS toucher : limite 120 000 chars (test 1M différé), chatbot Haiku, extraction Gemini, prompts
5. Après GO : modification + test e2e sur le cas démo via l'API réelle + mise à jour IA_BASELINE_V1.md (V2) + rollback documenté (snapshots md5 dans backups/)

Rapports complets : rapport_sonnet_4_5.md, rapport_sonnet_5_nothink.md, rapport_sonnet_5_think16k.md, metrics.json, extraction_details.json (même dossier).
