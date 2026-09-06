# MOTEUR IA OFFICIEL — V2
## Strategie & Expertise Sante — Migration claude-sonnet-5
### Date de mise en production : 06/09/2026 — GO final utilisateur apres benchmark controle
### Remplace : IA_BASELINE_V1.md (05/04/2026) pour le SEUL composant "modele". Tout le reste de la V1 demeure GELE et inchange.

---

## A. CHANGEMENT UNIQUE DE LA V2

| Composant | V1 | V2 |
|---|---|---|
| Modele StrategiIA (natif + fallback) | claude-sonnet-4-5-20250929 | **claude-sonnet-5** |
| Modele Dossier Express (natif + fallback multistage) | claude-sonnet-4-5-20250929 | **claude-sonnet-5** |
| Parametre thinking | N/A | **{"type": "disabled"}** injecte automatiquement quand model == "claude-sonnet-5" (voie native `llm_sync_call` ET proxy `llm_stream_call`) |
| Prompts metier | GELES | **INCHANGES (aucune modification)** |
| Limite documents | 120 000 chars | **INCHANGEE** (fenetre 1M = chantier separe) |
| Chatbot | claude-haiku-4-5-20251001 | INCHANGE |
| Extraction PDF | gemini-2.5-pro (Emergent) | INCHANGE |
| OCR images | Tesseract | INCHANGE |
| Validation citations | deterministe | INCHANGEE |

Fichiers modifies (7 emplacements) :
- `utils/llm.py` : l.49 (thinking disabled natif), l.74-75 (thinking disabled proxy), l.211 (multistage -> sonnet-5)
- `routes/strategiia.py` : l.58 (health natif), l.83 (health fallback), l.212 (appel principal)
- `routes/dossier_express.py` : l.626 (appel principal)

Hors perimetre, VOLONTAIREMENT inchanges (toujours sur 4.5, fonctionnels) :
- `routes/admin.py` l.2257/2267 (ping diagnostic admin)
- `services/kit_professionnel.py` (KIT_MODEL_NAME)

## B. JUSTIFICATION (benchmark 06/09/2026, cas fictif DEMONSTRATION Claire, entrees identiques)
Voir /app/memory/benchmarks/SONNET5_2026-09-06/RAPPORT_BENCHMARK.md
- Qualite >= 4.5 (exactitude, fidelite documentaire, coherence juridique superieures)
- Fiabilite superieure : zero affirmation chiffree non sourcee (4.5 inventait des % de succes)
- 2x plus rapide (77s vs 153s), -35 % de cout mesure (0,095 $ vs 0,145 $ par dossier)
- Rapports complets (end_turn) la ou 4.5 tronquait a 8000 tokens sur cas lourd

## C. COMPORTEMENT / POINTS DE SURVEILLANCE
1. **thinking disabled OBLIGATOIRE** : sans lui, l'adaptive thinking (defaut Sonnet 5) consomme le budget de sortie -> rapports tronques (constate au benchmark). Ancien `budget_tokens` -> 400. temperature/top_p non defaut -> 400.
2. Tokenizer Sonnet 5 : ~+32 % de tokens d'entree sur texte identique (deja integre aux couts).
3. Rapports plus concis (~17k chars vs ~25k) mais complets.
4. Surveillance 1ers dossiers reels : citation nominale des medecins (moins spontanee qu'en 4.5) — le prompt gele l'impose pour expertises multiples.
5. Support proxy Emergent du param thinking VERIFIE le 06/09/2026 (test 400 enabled+budget / 200 disabled).

## D. COUTS V2 (tarif permanent Anthropic : 2 $/Mtok in, 10 $/Mtok out)
- StrategiIA : ~0,036 $/analyse (V1 : ~0,054 $)
- Dossier Express : ~0,10 $/dossier hors extraction (V1 : ~0,145 $) + Gemini inchange si PDF scannes
- 1 000 dossiers : ~170 $ tout compris (V1 : ~250 $)

## E. PROCEDURE DE ROLLBACK (< 5 minutes)
1. Snapshots complets pre-migration : `/app/memory/backups/MIGRATION_SONNET5_2026-09-04/` (llm.py, strategiia.py, dossier_express.py, IA_BASELINE_V1.md + md5 + commit e192447)
2. Rollback rapide sans restauration de fichiers : remplacer les 7 occurrences "claude-sonnet-5" par "claude-sonnet-4-5-20250929" (les blocs `thinking` conditionnels deviennent inertes, aucun autre changement necessaire)
3. Ou restauration integrale : `cp` des 3 snapshots `.SNAPSHOT` vers leurs emplacements + `sudo supervisorctl restart backend`
4. Verification post-rollback : `curl /api/health/llm` -> {"operational": true}
5. claude-sonnet-4-5-20250929 reste disponible sur la cle Anthropic (verifie au catalogue le 06/09/2026)
