# RAPPORT D'INVESTIGATION — Échec génération PDF Dossier Express IA
Date : 04/08/2026 — Investigation lecture seule (aucune modification appliquée)

## Symptôme
Essai utilisateur du 03/08/2026 21:11 UTC en PRODUCTION : dossier `58d69f01-3bc`
(admin@accompagn-sante.fr) → status `error`, delivery `incident_technique`,
échec à l'étape 6 (génération PDF) après analyse IA réussie.
Email d'incident envoyé automatiquement à contact@strategie-expertise-sante.fr (contient l'erreur exacte).

## Cause racine
`/app/backend/utils/pdf.py` ligne 138 : FONT_DIR = "/usr/share/fonts/truetype/liberation"
→ dépendance à des polices SYSTÈME (paquet OS `fonts-liberation`), absentes de :
- `/app/.emergent/system_deps.txt` (cron, poppler-utils, tesseract-ocr, tesseract-ocr-fra — pas de fonts)
- `/app/Dockerfile` (apt-get: tesseract, poppler, libmagic, nginx — pas de fonts)
Sans les .ttf, `PremiumPDF.__init__` → add_font lève FileNotFoundError → try/except étape 6 → "Echec generation PDF".

## Preuves
1. Repro locale (preview, polices présentes) : generate_dossier_pdf → PDF 71 487 bytes OK. Code sain.
2. git log : aucun changement pdf.py / dossier_express.py / storage.py depuis le dernier PDF prod réussi (12/06).
3. Chronologie : dernier PDF prod OK 12/06 (ancienne image) → redéploiement ~31/07 (nouvelle image de base
   `fastapi_react_mongo_shadcn_base_image_cloud_arm:release-18022026-2`, .emergent/emergent.yml créé 31/07)
   → échec 03/08. L'ancienne image contenait les polices, la nouvelle non.

## Impact
100 % des générations PDF prod cassées (Dossier Express payant inclus) jusqu'au correctif.
Analyse IA, paiement, tracking : fonctionnels.

## Correctifs proposés (EN ATTENTE D'ORDRE EXÉCUTIF)
- Option A (recommandée) : embarquer LiberationSans-{Regular,Bold,Italic,BoldItalic}.ttf dans
  backend/utils/fonts/ + FONT_DIR avec repli (repo d'abord, système ensuite). Immunité définitive.
- Option B : ajouter `fonts-liberation` à system_deps.txt + Dockerfile. Dépend de l'hébergeur.
Après correctif : redéployer + relancer le dossier 58d69f01-3bc via POST /api/admin/dossier-express/{id}/retry.

## Constat annexe (non bloquant, à garder pour plus tard)
Les dossiers prod ont delivery_status "genere_sans_email" / email_sent=false — à examiner
séparément si la livraison email pose question (hors périmètre de ce rapport).
