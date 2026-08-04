# RAPPORT RCA + CORRECTIF — EXTRACTION OCR GELÉE EN PRODUCTION (04/08/2026)

## 1. SYMPTÔME
Test E2E prod du 04/08 07:39 UTC : upload du « Rapport Dr Etchepare.pdf » OK (S3 : 3 309 077 octets),
puis statut `processing` / « Extraction OCR en cours... » à l'infini. Aucune erreur visible.

## 2. INVESTIGATION (preuves réelles, aucun test théorique)
- L'outil de logs runtime de la plateforme de déploiement n'a pas pu fournir les logs internes du
  conteneur prod (limitation outillage — 2 tentatives, analyses statiques seulement).
- **Reproduction preview** (code identique, fichier exact récupéré depuis S3) : extraction réussie
  en 84 s, 3/3 chunks Gemini, 21 2xx caractères → le code fonctionne, cause environnementale.
- **Reproduction PROD** (08:26 UTC, fichier exact via pipeline réel) : blocage reproduit. Preuve clé
  capturée par le moniteur de polling :
  - +40 s et +80 s : `GET /api/upload/extract-status` (simple lecture MongoDB) → **read timeout 30 s**
  - +95→+125 s : réponses **non-JSON (502 gateway)**
  - +136 s : le backend répond à nouveau, mais `processing` figé pour toujours
- **Conclusion RCA** : le pod prod devient non-réponsif pendant la phase Gemini (mémoire/CPU sur le
  tier limité), est **tué/redémarré** (OOM ou liveness probe Kubernetes), la tâche de fond
  `asyncio.create_task` meurt avec lui, et le statut MongoDB n'est jamais mis à jour → polling infini.
  (Nota : les runs prod de 00:26-00:33 UTC avaient réussi la MÊME extraction → instabilité
  intermittente du pod, pas un échec déterministe.)

## 3. CORRECTIF APPLIQUÉ (backend uniquement)
### `utils/document_extraction.py`
- **Timeout dur 150 s par appel Gemini** (`asyncio.wait_for`, `GEMINI_CALL_TIMEOUT_S`) — single et chunked.
  Un appel HTTP gelé = chunk en échec, l'extraction continue.
- **Travail CPU-bound déporté hors event loop** (`asyncio.to_thread`) : pdfplumber (niveau 1),
  construction des sous-PDF pypdf (chunking), fallback Tesseract (niveau 3). Le pod reste réponsif
  aux health probes pendant l'extraction → réduit le risque de kill Kubernetes.
- **Progression par chunk** via `progress_cb` : « Extraction OCR — <fichier> : lot 2/3 (pages 5-8)... ».

### `routes/upload.py`
- **Heartbeat MongoDB toutes les 25 s** (`last_heartbeat_at`) pendant l'extraction + `processing_started_at`.
- **Watchdog dans `/extract-status`** : heartbeat périmé > 180 s (`STALE_HEARTBEAT_S`) → worker mort.
- **Reprise automatique depuis S3 (1×, claim atomique `find_one_and_update` sur `retry_count`)** :
  le fichier original étant persisté sur S3 avant extraction, la tâche est relancée sur le pod
  survivant. Si la reprise meurt aussi → **erreur claire** au frontend (plus jamais de polling infini).
- **Plafond global 25 min** (`EXTRACTION_GLOBAL_TIMEOUT_S`) sur l'extraction complète.

### `routes/dossier_express.py`
- Propagation de `progress_cb` (`_process_files_payload` → `_extract_one_file` → pipeline).

### Tests hérités réalignés (dérives antérieures au correctif, sans lien)
- `tests/test_chunked_upload.py` : mode toujours-async (polling) + limite 500 chunks (relevée le 03/08).
- `tests/test_document_extraction_pipeline.py` : >10 fichiers → 400 (contrat actuel).

## 4. VALIDATION (fichier réel « Rapport Dr Etchepare.pdf », pipeline réel)
| Test | Résultat |
|---|---|
| Extraction nominale preview | ✅ done en 83 s, 3/3 chunks, progression par lot visible |
| **Crash simulé** (kill backend à +12 s d'extraction) | ✅ détection worker mort à +182 s → « Reprise après interruption serveur... » → re-téléchargement S3 → **done à +267 s, 21 211 chars** |
| Non-régression pytest (upload/extraction/OCR, 5 fichiers) | ✅ 61 passed, 0 failed |
| **E2E complet preview** : upload → S3 → OCR (21 237 c.) → analyse IA (23 673 c., 173,7 s) → PDF (111 419 o., « Etchepare » cité 9×) → stockage S3 → **email envoyé** → download HTTP 200 | ✅ dossier `c734f060-e45`, `delivery_status: livre_client`, `email_sent: true` |

## 5. RESTE À FAIRE
1. **REDÉPLOYER** (le correctif n'existe qu'en preview).
2. Re-valider l'E2E complet en PRODUCTION avec le fichier exact (procédure prête, fichier sur S3).
