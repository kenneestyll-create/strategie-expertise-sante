# RAPPORT — PROGRESSION CLIENT VISUELLE (P-A + P-B) + CAUSE RACINE PROFONDE CORRIGÉE (04/08/2026)

## 1. P-A — Progression OCR réelle affichée au client
### Frontend (`pdfExtractor.js`, 2 boucles de polling)
- Le champ `progress` du serveur (« Extraction OCR — <fichier> : lot 2/3 (pages 5-8)... »,
  « Reprise après interruption serveur... ») est relayé vers la ligne client existante
  (`chunk-progress`) via l'événement `upload-progress`. Le timer générique s'efface dès
  qu'un progrès réel arrive.
### `DossierExpressPage.jsx`
- La condition d'affichage laisse passer les messages « Extraction » / « Reprise » sans
  préfixe « Transfert : ».
### Backend (petit ajustement NÉCESSAIRE, expliqué)
- Le chemin base64 asynchrone (`/extract-document-text`, utilisé par l'UI pour tout fichier
  < 5 Mo — donc la majorité des dossiers clients) utilisait un worker local dupliqué qui
  (a) n'émettait jamais le « lot X/Y » et (b) n'avait AUCUN heartbeat → le watchdog ajouté
  le matin aurait tué à tort toute extraction base64 > 180 s. Ce worker dupliqué est
  remplacé par le worker durci de `upload.py` (`_run_extraction`) : progression par lot,
  heartbeat 25 s, timeout global 25 min. 12 lignes, aucun nouveau comportement métier.

## 2. P-B — Fin de l'écran figé pendant l'analyse IA (états explicatifs, zéro artifice)
- `active-step-detail` : rotation (12 s) de 5 états explicatifs réels du travail d'analyse
  (« Lecture croisée de vos pièces... », « Confrontation aux textes, barèmes et
  jurisprudences... », etc.) — aucun faux pourcentage, aucune progression artificielle.
- `analysis-step-elapsed` : « ⏱ 1 min 04 s dans cette étape — durée habituelle : 2 à 4
  minutes » (compteur réel par étape, remis à zéro à chaque changement d'étape).
- Correctif de mapping : le statut legacy `analyzing` pointe désormais sur l'étape 4/8
  (« Analyse approfondie ») au lieu de 3/8.

## 3. DÉCOUVERTE MAJEURE — CAUSE RACINE PROFONDE DU CRASH POD CORRIGÉE
En instrumentant les polls, découverte que **chaque appel Gemini gelait TOUT le serveur**
pendant 30-150 s : `emergentintegrations 0.1.0` appelait `litellm.completion()`
(**synchrone**) à l'intérieur d'une fonction async → event loop bloquée → polls clients en
timeout ET probes de santé Kubernetes en échec → **c'est ce qui faisait tuer le pod de
production pendant les extractions** (le crash observé ce matin, absorbé jusqu'ici par le
watchdog + reprise S3).
**Correctif : mise à niveau `emergentintegrations 0.1.0 → 0.2.0`** (utilise
`litellm.acompletion`, réellement async). Compatibilité d'API vérifiée classe par classe
avant installation (LlmChat, UserMessage, FileContentWithMimeType, OpenAITextToSpeech,
get_integration_proxy_url : signatures identiques). `requirements.txt` mis à jour via pip freeze.

### Mesure avant/après (extraction du fichier réel, polls toutes les 3 s)
| | AVANT (0.1.0) | APRÈS (0.2.0) |
|---|---|---|
| Polls de statut pendant l'extraction | timeouts systématiques (25 s+) pendant chaque appel Gemini | **30/30 OK, 0 timeout** |
| Progression « lot X/Y » visible | jamais (polls bloqués) | **+3 s lot 1/3, +41 s lot 2/3, +81 s lot 3/3** |
| Risque de kill du pod prod pendant OCR | élevé (probes bloquées) | éliminé à la source |

## 4. VALIDATION COMPLÈTE
- **E2E frontend par agent de test (iteration_210)** : parcours complet Dossier Express en
  mode admin via l'UI avec le PDF réel — succès en 241 s, P-B validé à 100 % (rotation des
  5 états observée, compteur 4 s → 2 min 35 s, reset par étape vérifié, transition
  59 s → « 1 min 04 s » vérifiée), mobile 390×844 sans débordement, /dossier-express/suivi OK,
  aucune régression.
- **E2E backend post-upgrade 0.2.0** (fichier réel, pipeline complet preview) : extraction
  81 s (3/3 lots visibles au polling), analyse IA 179,8 s, PDF 112 282 o (%PDF- valide),
  stockage S3, email envoyé (`livre_client`), téléchargement HTTP 200.
- **Chatbot Straté** (flux LlmChat texte) : réponse correcte post-upgrade.
- **Pytest** : 42 passed / 0 failed (upload, chunks, OCR fields).

## 5. À DÉPLOYER
Preview uniquement. Le prochain déploiement livrera : P-A + P-B + upgrade
emergentintegrations 0.2.0 (prévention à la source des crashs pod pendant OCR).
