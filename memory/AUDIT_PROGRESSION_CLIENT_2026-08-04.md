# ÉTAT DES LIEUX — PROGRESSION CLIENT DOSSIER EXPRESS (04/08/2026)
Audit en lecture seule — AUCUN code modifié.

## 1. CE QUI EXISTE DÉJÀ (riche, souvent méconnu)

### A. Écran de traitement sur /dossier-express (après soumission) — DÉJÀ TRÈS COMPLET
`DossierExpressPage.jsx` (~lignes 1099-1250) affiche pendant le traitement :
- **8 étapes** (STEPS : extracting → uploading → reading → analyzing_1/2/3 → generating → sending)
- **Barre segmentée** (1 segment par étape, remplissage progressif + pulse sur l'étape active)
- **Indicateur d'étape active** avec compteur « X / 8 » + détail explicatif
- **Timer écoulé** (« 2 min 14 s — estimé 3 à 5 min ») + pourcentage
- **Timeline verticale** avec coches vertes (fait) / spinner (en cours) / icônes (à venir)
- **Messages de valeur rotatifs** (6 messages, rotation 12 s)
- **Ligne temps réel `chunk_progress`** (data-testid="chunk-progress")

### B. Alimentation backend — statuts DÉJÀ disponibles et remontés
- Polling frontend : `GET /api/dossier-express/status/{id}` toutes les 3 s → renvoie le document
  complet, dont **`progress_step`** écrit par le pipeline : `reading` → `analyzing` /
  `analyzing_1` → `analyzing_2` / `analyzing_3` (PATH B multistage, `utils/llm.py`) →
  `generating` (PDF + stockage) → `sending` (email) → `completed`.
- `processing_step` interne (checkout_valide, extraction_en_cours, analyse_ia, pdf_en_cours,
  stockage_en_cours, email_en_cours, termine + états erreur_*) : mappé proprement.

### C. Page publique de suivi /dossier-express/suivi — EXISTE AUSSI
`SuiviDossierPage.jsx` + `GET /api/dossier-express/suivi/{id}?token=` : 7 étapes client
(labels humains centralisés dans `constants/statuses.py` : DOSSIER_STEP_CLIENT_MAP /
CLIENT_STEPS_DISPLAY), statuts completed/active/waiting, message client, `download_url` à la fin.

### D. Phase upload/extraction (avant soumission)
Événements `upload-progress` : pourcentage réel d'upload par chunk, puis **timer générique
local** (« Lecture IA en cours ~60-90 s — Xs écoulées », toutes les 2 s).

## 2. LES MANQUES CONFIRMÉS (précis et limités)

### M1 — La progression OCR RÉELLE par lot n'est jamais montrée au client ⭐ principal
Le backend expose depuis ce matin (correctif OCR) un champ `progress` riche via
`GET /api/upload/extract-status/{id}` : « Extraction OCR — <fichier> : lot 2/3 (pages 5-8)... ».
**Mais les 2 boucles de polling de `pdfExtractor.js` (~l.169 et ~l.317) ne lisent que
`status` (done/error) et IGNORENT le champ `progress`.** Le client voit à la place le timer
générique estimé. Vrai « lot 2/3 » disponible côté serveur, perdu côté client.

### M2 — Le message de reprise auto n'est jamais montré
« Reprise après interruption serveur... » (watchdog du matin) transite aussi par ce champ
`progress` ignoré → en cas de crash pod + reprise, le client voit un timer qui s'allonge
sans explication.

### M3 — Temps mort perçu pendant l'analyse IA (PATH A)
En production le chemin utilisé est PATH A « native_anthropic » (~174 s d'un seul bloc) qui
n'écrit que `analyzing` → l'écran reste figé sur l'étape 4/8 pendant ~3 min sans aucun
mouvement (les granularités analyzing_2/3 n'existent que sur PATH B multistage).
C'est le principal moment d'incertitude du parcours.

## 3. PREVIEW vs PRODUCTION
**Aucune différence structurelle** : code identique depuis le déploiement de ce matin
(Lot 1 + correctif OCR). Preuve : durant l'E2E prod de 09:24, l'API prod renvoyait bien
« lot 1/3 → 2/3 → 3/3 » à mon moniteur. Le champ existe en prod ; seul l'affichage client manque.

## 4. PROPOSITIONS (si vous validez — aucun code tant que pas d'ordre)
- **P-A (cœur, ~15 lignes, risque nul)** : dans les 2 boucles de polling de `pdfExtractor.js`,
  relayer `pollRes.data.progress` vers l'événement `upload-progress` existant → la ligne
  `chunk-progress` affiche le vrai « lot 2/3 (pages 5-8) » et « Reprise après interruption
  serveur... ». Zéro changement backend, zéro changement de layout.
- **P-B (confort, frontend seul)** : pendant `analyzing` (PATH A), faire progresser
  visuellement analyzing_1 → 2 → 3 sur base du temps écoulé (ex. paliers 60 s/120 s) pour
  supprimer les ~3 min d'écran figé. Purement cosmétique, honnête (libellés déjà génériques).
- **P-C (optionnel)** : afficher le nombre de pages détectées (« 9 pages en cours de lecture »)
  — donnée déjà présente dans `details[].pages` à la fin d'extraction, nécessiterait de
  l'exposer plus tôt côté backend (petit ajout).
