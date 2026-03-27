# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)

## Entonnoir de Conversion — DONE
- Flow: Chatbot attire -> StrategiIA convertit -> Dossier Express monetise
- Guides PDF avec email gate pour capture de leads
- Email de relance automatique 48h apres telechargement guide

## StrategiIA — Entonnoir 3 paliers — DONE
Async polling, barre de progression, option RATP/SNCF
- Auto-open via URL param ?open=strategiia (pour liens email)

## Optimisation Mobile Complete — DONE
- 100dvh, safe areas, input 16px, ChatBot plein ecran, menu opaque
- Cartes empilees pour tableaux, tabs responsive, PdfPreview responsive

## Email Gate Guides PDF (Mar 2026) — DONE
- Champ email obligatoire avant telechargement
- POST /api/resources/request-guide
- Collection `guide_leads` avec segmentation par categorie

## Email Relance Automatique 48h (Mar 2026) — DONE
- Scheduler background `_guide_followup_scheduler()` — check toutes les heures
- 6 templates personnalises par categorie:
  * Maladie professionnelle
  * Accident du travail
  * Expertise medicale
  * MDPH
  * Recours
  * Assurances
- Tracking: pixel ouverture + click CTA
- Collections: `guide_followups` (sent_at, opened, clicked)
- CTA email redirige vers /?open=strategiia (auto-open modal)
- Admin stats: GET /api/admin/guide-leads/stats (taux ouverture/clic, par categorie)
- Teste manuellement: email envoye via Resend OK

## Refonte PDF Premium (Mar 2026) — DONE
- Moteur PDF completement reecrit: palette noir #1A1A1A / or #C9A84C / ivoire
- Header premium: nom + PIONNIER EN FRANCE + date + numero SES-XXXX-XXXXX
- TOUT tient sur 1 page A4 (court/moyen/long)
- Prompt LLM restructure: ton humain/chaleureux, 300 mots max, 6 sections premium
- Filigrane discret (gratuit) / sans filigrane (premium)
- Footer or fin + Document confidentiel
- Tests: 14/14 passes

## Correction Menu Mobile + Conseil du Jour (Mar 2026) — DONE
- Menu mobile: etend bord-a-bord (-mx-4), overflow-x hidden, scrollbar invisible
- Conseil du jour: corrige blocage priorite sans end_date, auto-expiration, rotation fiable
- Tests: backend 16/16, frontend verifie, 0 overflow horizontal

## Correction PDF Footer (Mar 2026) — DONE
- DEUX moteurs PDF identifies et corriges:
  * Backend pdf.py (FPDF) pour StrategiIA: marges, nettoyage URLs, contact block dynamique
  * Frontend SimulateurPage.jsx (jsPDF) pour Simulateur: remplace window.location.origin par SITE_DOMAIN, footer dynamique, checkPageBreak()
- Prompts LLM renforces: interdiction URLs
- Teste E2E: backend 8/8 tests, frontend flux complet verifie

## Refonte PDF Simulateur Premium (Mar 2026) — DONE
- generatePDF() dans SimulateurPage.jsx completement reecrit avec design premium
- Ancien design rouge [185,78,72] supprime — remplace par palette Noir/Or/Ivoire
- Header noir avec "Strategie & Expertise Sante" blanc + "PIONNIER EN FRANCE" or
- Numero rapport SES-YYYY-XXXXX + date a droite
- Barres d'accent dorees sur titres de sections
- Puces dorees (gold bullets) au lieu de cercles noirs
- Bloc profil sur fond ivoire avec accent or a gauche
- Services encadres avec bordure doree sur fond ivoire
- Footer: ligne or + "Document confidentiel" + copyright
- Watermark diagonal "Strategie & Expertise Sante"
- Fichier renomme: rapport-diagnostic-SES-YYYY.pdf
- Coherence visuelle totale entre PDF Simulateur et PDF Backend
- Logo bouclier haute resolution (264x288px) integre dans le header PDF
- Conclusion emotionnelle premium: "Vous n'etes plus seul(e)... SES est votre bouclier"
- Module shieldLogo.js cree pour le logo base64 (importe dans SimulateurPage.jsx)
- Tests: 100% backend + 100% frontend (flux E2E + analyse visuelle PDF confirme)

## Mode Admin/Test pour tunnels premium (Mar 2026) — DONE
- AdminTestProvider + useAdminTest hook pour toggle Mode Admin/Mode Client
- Toggle flottant en bas a gauche, visible uniquement quand admin connecte
- Backend: 3 endpoints admin bypass:
  * POST /api/strategiia/admin-bypass-premium (bypass Stripe, analyse premium directe)
  * POST /api/dossier-express/admin-bypass (bypass paiement, traitement direct)
  * POST /api/strategiia/register-email avec admin_test (quota illimite, pas de lead)
- Frontend: bypass email gate + payment gate sur StrategiIA, DossierExpress, Simulateur
- Toutes les donnees admin marquees admin_test=true en base
- Toggle DEPLACE exclusivement dans l'en-tete du Dashboard Admin (/admin)
- AUCUN element visible sur le site public, meme avec admin connecte
- Toggle discret dans la barre d'en-tete admin: "Test Client" (gris) / "Test Admin" (ambre)
- Securite: endpoints admin strictement proteges par JWT admin (403/401 sans token)
- Tests: site public verifie propre (0 elements parasites), admin dashboard verifie fonctionnel

## Correction Freeze Middleware ASGI (Mar 2026) — DONE
- **Cause racine:** Les `@app.middleware("http")` de Starlette utilisent `BaseHTTPMiddleware` en interne, provoquant `RuntimeError: No response returned.` quand une route appelle `await request.json()`
- **Endpoints affectes:** `POST /api/strategiia/analyze` et `POST /api/strategiia/admin-bypass-premium`
- **Fix:** Conversion des 2 middleware (SecurityHeaders + CacheControl) en **pure ASGI middleware classes** sans BaseHTTPMiddleware
- **Debug statements nettoyes** dans strategiia.py
- **Performance:** Reponse endpoint en 0.12s (retour immediat du job_id)
- **Tests:** 100% backend (8/8 curl), 100% frontend (8/8 playwright), testing agent iteration 111

## Correction 3 Bugs StrategiIA (Mar 2026) — DONE
- **Bug 1 — Erreurs de connexion intermittentes** : Le polling abandonnait au 1er echec reseau. Fix: compteur pollErrors (3 echecs consecutifs avant abandon) + flag jobCompleted contre race condition requetes en vol.
- **Bug 2 — Logo bouclier absent du PDF** : Le PDF backend (FPDF) n'avait jamais integre d'image. Fix: shield_logo.png (264x288, 9926 bytes) decode et sauvegarde dans backend/utils/, integre dans le header PDF (9mm a gauche du nom).
- **Bug 3 — Phrase de cloture tronquee** : Le regex _clean_analysis supprimait "Strategie & Expertise Sante" y compris dans la phrase "devient votre bouclier". Fix: regex modifie pour ne matcher qu'en debut de ligne + phrase hardcodee dans le template PDF + patterns de dedup pour eviter les doublons.
- Tests: iteration 112 — 100% backend (8/8 pytest), 100% frontend (6/6 playwright)

## Workflow Relecture Expert Personnalisee (Mar 2026) — DONE
- **Fix critique event loop** : `litellm.completion()` (synchrone) bloquait l'event loop asyncio pendant 40-70s. Fix: `asyncio.to_thread()` pour executer le LLM dans un thread pool. Le serveur reste reactif pendant toute la duree LLM.
- **Workflow 4 etapes** : en_attente → en_cours → valide → envoye. Aucun envoi automatique du document si Relecture Expert selectionne.
- **Admin dashboard** : 5 KPIs, boutons Traiter / Relire-Valider / Envoyer au client, dialog de relecture avec textarea et notes internes.
- **Endpoint send-reviewed** : POST /api/admin/premium-analyses/{id}/send-reviewed — genere le PDF avec marqueur "Version expert finalisee" et envoie par email via Resend.
- **Frontend client** : mention "24h a 48h ouvrees", etape "En attente de relecture expert" avec message rassurant (intervention humaine, delai, envoi par email).
- **PDF marqueur** : bandeau discret "Document relu et finalise dans le cadre de l'option Relecture expert personnalisee" dans le header.
- Tests: iteration 113 — backend 100% (10/10 pytest), frontend 100%

## Correction Bug Bloquant Dossier Express IA (Mar 2026) — DONE
- **Bug frontend** : En mode admin, `handleCheckout()` faisait `setStep('form')` sans rendre `hasPaid=true`. Le bouton "Lancer l'analyse" n'apparaissait jamais. Fix: ajout state `adminPaid` + `hasPaid` inclut `adminPaid`.
- **Bug backend event loop** : `_process_dossier_express` utilisait `await chat.send_message()` (synchrone via litellm.completion) bloquant l'event loop 50-60s. Fix: `asyncio.to_thread(_llm_sync_call, ...)` comme pour StrategiIA.
- **Bug timeout 60s proxy** : Le prompt Dossier Express (11 sections, 1000-1500 mots) depassait le timeout de 60s du proxy API. Fix: prompt optimise a 5 sections (800 mots max). Reponse en ~55s.
- **UX ameliore** : Messages de chargement explicites ("Televersement en cours...", "Analyse en cours..."), bouton desactive pendant l'envoi, gestion d'erreurs detaillee (413, 400, etc.), polling resilient (5 erreurs avant abandon).
- Tests: iteration 114 — backend 100% (9/9 pytest), frontend 100%

## Restructuration Admin & Fix Relecture Expert (Mar 2026) — DONE
- **Bug "Relire et valider"** : Le dialogue de relecture ne chargeait pas le contenu complet pour les Dossier Express (champ `context` manquant). Fix: nouveau endpoint `GET /api/admin/premium-analyses/{id}/full-content` qui récupère l'analyse depuis la bonne collection (strategiia_analyses ou dossier_express). Le dialogue affiche maintenant la situation client, le type de dossier, le régime, et le texte d'analyse complet.
- **Séparation Admin** : L'ancien onglet "Premium" unique a été remplacé par deux onglets distincts : "StrategiIA" (avec section Relecture expert — StrategiIA) et "Dossier Express" (avec stats production + section Relecture expert — Dossier Express IA + historique soumissions). Composant réutilisable `AdminPremiumReview.jsx` créé pour le workflow de relecture. Badges de notification sur chaque onglet indiquant les items en attente.
- **Fix send-reviewed** : L'endpoint `POST /api/admin/premium-analyses/{id}/send-reviewed` utilise maintenant le bon `report_type` (StrategiIA ou Dossier Express IA) au lieu du hardcodé "StrategiIA".
- **Stepper Dossier Express** : Ajout de 5 étapes dynamiques dans la vue processing (Téléversement → Lecture → Analyse → Génération → Envoi) avec barre de progression animée. Backend met à jour `progress_step` à chaque étape du traitement.
- Tests: iteration 115 — backend 100% (16/16 pytest), frontend 100%

## Fix validation réelle Dossier Express (Mar 2026) — DONE
Problèmes réels identifiés et corrigés:
- **Cause A — Documents absents dans l'admin** : `premium_analyses` n'était jamais créé pour les dossiers admin-bypass ni pour les soumissions standards. Fix: `_process_dossier_express` crée automatiquement un `premium_analyses` lié par `dossier_id` à chaque dossier complété. Le lien utilise `dossier_id` (fiable) au lieu de `email` (fragile avec dossiers multiples).
- **Cause B — Stepper invisible** : Le stepper existait dans le DOM mais la page restait scrollée au bas du formulaire. Fix: `window.scrollTo({ top: 0, behavior: 'smooth' })` après `setStep('processing')`.
- **Mode admin perdu** : `isAdminMode` était stocké uniquement en mémoire React, perdu lors de navigation entre pages. Fix: persistance dans `sessionStorage`.
- **Consultation directe** : Nouveau endpoint `GET /api/admin/dossier-express/{id}/analysis` + bouton "Consulter l'analyse" dans la liste admin pour accéder directement à l'analyse d'un dossier complété.
- Tests: iteration 116 — backend 100% (15/15 pytest), frontend 100%. Validation avec 8+ soumissions réelles, screenshots du stepper dynamique avec progression en temps réel.

## Séparation Dossier Express IA / StratégiIA (Mar 2026) — DONE
- **Bug bloquant** : Le pipeline Dossier Express utilisait `STRATEGIIA_SYSTEM_PROMPT` comme prompt système, créant une confusion d'identité. De plus, l'absence de retry logic causait des blocages de 3-5 minutes sur erreurs LLM (502, budget exceeded).
- **Cause frontend** : Le stepper affichait "Analyse juridique par StratégiIA" au lieu de labels propres à Dossier Express.
- **Fix backend** : Création de `DOSSIER_EXPRESS_SYSTEM_PROMPT` (identité propre). Ajout retry logic (3 tentatives avec délai) dans `_process_dossier_express`. Gestion d'erreur améliorée avec `progress_step: "error"`.
- **Fix frontend** : Remplacement de TOUS les labels "StratégiIA" par "Dossier Express IA" dans la landing page, le formulaire, le stepper et l'admin. Nouveaux labels stepper : "Documents reçus", "Lecture des pièces transmises", "Analyse de votre dossier", "Rédaction de votre synthèse personnalisée", "Préparation de votre rapport final". Vue d'erreur dédiée avec bouton "Réessayer".
- **Admin** : Label "Analyse générée par StratégiIA" → "Analyse générée par Dossier Express IA".
- Tests: iteration 118 — backend 100% (8/8), frontend 100%

## Refonte UX Phase d'Attente Dossier Express (Mar 2026) — DONE
- **Contexte** : Le traitement backend est 100% asynchrone (continue même si le client ferme la page). L'ancienne phrase "Vous pouvez fermer cette page" était ambiguë et non premium.
- **Nouvelle vue processing** :
  * Titre clair : "Votre dossier est en cours d'analyse"
  * Sous-titre explicatif : "Vos documents ont bien été reçus. Notre moteur d'analyse documentaire examine actuellement votre dossier."
  * Bloc dynamique amber montrant l'étape active + détail ("Croisement avec les jurisprudences, barèmes et cas similaires.")
  * Barre de progression avec pourcentage visible
  * Timeline avec label "Terminé" sur chaque étape complétée
  * Détail contextuel sous l'étape active (texte explicatif)
  * Bloc de réassurance avec icône bouclier : "Vous n'avez pas besoin de rester sur cette page. Votre rapport vous sera automatiquement envoyé par email dès qu'il sera prêt."
  * Indicateurs "Livraison sous 2h" + "Données chiffrées"
  * Cercle pulsant autour de l'icône Brain (animation ping 2.5s)
  * Ring amber sur l'étape active + fond surélevé
- Tests: iteration 119 — backend 100% (6/6), frontend 100%

## Pipeline Documentaire Robuste Dossier Express IA (Mar 2026) — DONE
- **Problème** : Les PDF scannés et images étaient systématiquement ignorés par l'analyse IA. Seuls les PDF texte étaient partiellement extraits. Aucun OCR côté serveur.
- **Solution** : Pipeline d'extraction à 3 niveaux :
  * **Niveau 1** : `pdfplumber` pour les PDF texte (extraction directe, rapide)
  * **Niveau 2** : `pypdfium2` + `tesseract-ocr` (fra+eng) pour les PDF scannés (OCR automatique jusqu'à 15 pages)
  * **Niveau 3** : `tesseract` directement pour les images (JPG, PNG, etc.)
- **Métadonnées détaillées** : Chaque fichier a désormais : nom, méthode, statut (text_extracted/ocr_extracted/ocr_empty/extraction_failed), pages, volume de texte, aperçu
- **Stockage en base** : `document_details` sauvegardé dans chaque dossier express
- **Vue admin** : Bloc "Documents analysés" avec badge de statut couleur (vert=texte, bleu=OCR, orange=partiel, rouge=échec), méthode, pages, volume, aperçu du contenu
- **Injection confirmée** : Le texte extrait est réellement injecté dans le prompt LLM (vérifié E2E)
- **Dépendances système** : tesseract-ocr, tesseract-ocr-fra, poppler-utils, pytesseract, pdf2image
- Tests: iteration 120 — backend 100% (13/13), frontend 100%

## Encart Documentaire Premium dans le Rapport PDF (Mar 2026) — DONE
- **Encart "Base documentaire prise en compte"** intégré dans le PDF final, avant la signature de marque
- **3 métriques** : Documents analysés, Pages exploitées, Lisibilité documentaire
- **5 niveaux** : Excellente (texte) → Très bonne (mixte) → Bonne (OCR) → Partielle → Limitée
- **Phrase de réassurance** : "Certaines pièces peuvent nécessiter une relecture humaine complémentaire lorsqu'elles sont scannées, manuscrites ou de qualité inégale."
- **Design** : Accent doré, boîte ivoire, typographie cohérente avec le reste du PDF premium
- **Rétrocompatible** : Les PDF sans document_details continuent de fonctionner normalement
- Bug logique de priorité des conditions corrigé (Bonne vs Très bonne)
- Tests: iteration 121 — 13/13 backend + validation manuelle des 5 niveaux

## Prévisualisation Admin et Encart Documentaire (Mar 2026) — DONE
- **Encart PDF** : "Base documentaire prise en compte" intégré dans le rapport PDF avec 3 métriques + note de réassurance (fait précédemment)
- **Encart admin** : Réplique visuelle de l'encart PDF dans la modal admin avec grille de 3 métriques (documents, pages, lisibilité), liste de fichiers avec badges statut, note de réassurance
- **Preview PDF** : Nouvel endpoint `GET /api/admin/dossier-express/{id}/preview-pdf` + bouton "Prévisualiser le PDF" qui ouvre le rapport dans un nouvel onglet
- Tests: iteration 122 — backend 100% (6/6), frontend 100%

## Refonte Modal Admin Dossier Express — Onglets (Mar 2026) — DONE
- **3 onglets internes** dans la modal de consultation :
  * **Analyse** : Situation client + Encart Base documentaire (grille 3 métriques) + Texte analyse
  * **Documents uploadés** : Liste détaillée par fichier (icône, nom, type, pages, taille, badge lisibilité couleur, méthode, aperçu du contenu)
  * **Prévisualisation PDF** : Boutons "Visualiser le PDF final" (nouvel onglet) + "Télécharger le PDF" + résumé contenu
- **Boutons existants préservés** : Traiter (25) et Notifier (38) dans AdminPremiumReview intacts
- Tests: iteration 123 — backend 100%, frontend 100%

## Bouton "Consulter l'analyse" dans Relecture Expert (Mar 2026) — DONE
- **Problème** : Les 3 onglets (Analyse/Documents/PDF) étaient accessibles uniquement via une liste tout en bas de la page, invisible pour l'utilisateur
- **Fix** : Ajout d'un bouton "Consulter l'analyse" (amber) directement dans chaque entrée de la section "Relecture expert – Dossier Express IA" (AdminPremiumReview.jsx)
- Le bouton n'apparaît que pour les entrées ayant un `dossier_id` lié (35 sur 38)
- Les boutons Traiter (25), Notifier (38), Relire/Valider (10), Envoyer (1) restent intacts
- Le bouton n'apparaît PAS dans l'onglet StratégiIA (prop non passée)
- Tests: iteration 124 — backend 100%, frontend 100%

## Suppression de dossiers dans l'Admin (Mar 2026) — DONE
- Icône poubelle sur chaque ligne de la section "Relecture expert – Dossier Express IA"
- Confirmation `window.confirm` avant suppression irréversible
- Backend: `DELETE /api/admin/premium-analyses/{id}` supprime l'entrée ET le dossier lié dans `dossier_express`
- Tests: iteration 125 — 100% backend (4/4), frontend (33 icônes, tous boutons existants intacts)

## Pipeline OCR Renforcé et Persistant (Mar 2026) — DONE
- **Cause racine** : tesseract/poppler (binaires système) disparaissaient à chaque redémarrage d'environnement → OCR échouait silencieusement → tous les scans/images marqués "non extractible"
- **Fix persistance** : `start.sh` auto-installe tesseract-ocr + tesseract-ocr-fra + poppler-utils au démarrage
- **Pipeline 4 niveaux** :
  * Tentative 1 : Extraction texte native (pdfplumber)
  * Tentative 2 : OCR standard (pypdfium2 + tesseract fra+eng)
  * Tentative 3 : OCR renforcé (pré-traitement : autocontrast, contraste 1.5x, netteté 2x, débruitage, redimensionnement)
  * Tentative 4 : Fallback pdf2image 300dpi + OCR renforcé
- **Évaluation page par page** : chaque page classée lisible/partiellement lisible/non lisible
- **Pré-traitement image** : autocontrast, contraste, netteté, débruitage median, upscale si < 1500px
- Tests: iteration 126 — 16/16 backend (PDF texte, PDF scanné, image, edge cases)

## Conclusion PDF "Et maintenant ?" — Bloc Conversion Stratégique (Mar 2026) — DONE
- **Ancien bloc supprimé** : "Signature émotionnelle de marque" + "Contact & CTA block" (textes génériques)
- **Nouveau bloc 3 parties** sous le titre "Et maintenant ?" :
  * **Clôture émotionnelle** : Empathie, reconnaissance de l'épreuve, premier éclairage
  * **Transition stratégique** : Limites du rapport, nécessité d'analyse humaine approfondie, potentiel du dossier
  * **Orientation vers l'offre finale** : Boîte ivoire avec accent doré, CTA subtil "accompagnement sur mesure"
- **Signature finale** : "Stratégie & Expertise Santé — Votre bouclier."
- **Strip patterns ajoutés** : 4 regex pour empêcher le LLM de dupliquer les phrases hardcodées
- Tests: iteration 127 — 14/14 backend, 7/7 frontend

## Tunnel de Conversion Email Premium Dossier Express (Mar 2026) — DONE
- **Email de livraison refondé** : Template HTML premium noir/or/ivoire cohérent avec la marque S.E.S
- **Bouton principal** : "Télécharger mon rapport PDF" — lien stable via object storage + token unique
- **Texte d'accompagnement** : "Votre analyse personnalisée a bien été finalisée. Vous pouvez désormais consulter et télécharger votre rapport en toute simplicité."
- **Transition stratégique** : Bloc ivoire avec accent doré préparant la conversion
- **Bouton secondaire** : "Être accompagné par un expert" — redirige vers /contact
- **Endpoint de téléchargement** : `GET /api/dossier-express/{id}/download?token=xxx` — sécurisé, stable, sans friction
- **Stockage PDF** : PDF uploadé vers object storage avec chemin `strategie-expertise-sante/dossiers/{id}/{token}.pdf`
- **Lien discret dans le PDF** : "Accompagnement personnalisé : strategie-expertise-sante.fr/contact" en pied de rapport
- **Tunnel 3 niveaux** : Conversion depuis le site + depuis l'email + depuis le PDF
- Tests: iteration 128 — 18/18 backend, 8/8 frontend

## QR Code Premium dans le PDF Dossier Express (Mar 2026) — DONE
- **QR code visuel** intégré dans le bloc "Et maintenant ?", après la boîte d'orientation
- **Design harmonisé** : fill #1a1a1a (noir S.E.S), background #FAF8F3 (ivoire), 22mm centré
- **Label** : "Prochaine étape recommandée"
- **Description** : "Scannez pour accéder à l'accompagnement expert personnalisé S.E.S"
- **URL trackée** : `strategie-expertise-sante.fr/contact?src=pdf&type=dossier_express&via=qr`
- **Lien texte fallback** toujours présent sous le QR : "Première consultation offerte | strategie-expertise-sante.fr/contact"
- **Bibliothèque** : `qrcode[pil]` ajoutée à requirements.txt
- **Gestion fichiers** : QR généré en mémoire → temp PNG → embed FPDF → cleanup
- Le PDF devient un support de conversion même en version imprimée
- Tests: iteration 129 — 18/18 backend, 7/7 frontend

## Tracking Analytics de Conversion (Mar 2026) — DONE
- **Endpoint `POST /api/tracking/contact-visit`** : Enregistre chaque visite sur /contact avec attribution (via, source, campaign)
- **Modèle Contact enrichi** : `tracking_via`, `tracking_source`, `tracking_campaign` conservés dans la fiche lead
- **Frontend ContactPage** : Détecte automatiquement les params URL (via, source, campaign) via `useSearchParams()`, envoie le tracking au mount, passe les données au formulaire
- **Endpoint admin `GET /api/tracking/conversion-analytics`** : Agrège visites et contacts par canal, calcule les taux de conversion, produit une série temporelle quotidienne
- **Composant `AdminConversionAnalytics`** : Intégré dans l'onglet Analytics admin, affiche KPIs (visites, formulaires, taux conv.), tableau par canal (QR Code PDF, Email livraison, Lien PDF), graphique Recharts
- **URLs trackées cohérentes** : `?via=qr&source=dossier_express`, `?via=email&source=dossier_express`, `?via=pdf_link&source=...`
- Tests: iteration 130 — 21/21 backend, 6/6 frontend

## Tags d'Origine et Filtres de Leads (Mar 2026) — DONE
- **Tags automatiques sur chaque fiche lead** : Canal (QR PDF / Email / Lien PDF - ambre) + Source (Dossier Express IA / StrategiIA - bleu)
- **Filtres dans la liste contacts admin** : 4 filtres (Recherche, Statut, Canal, Source)
- **Filtre backend** : `GET /api/admin/contacts?via=qr&source=dossier_express` filtre au niveau DB
- **Fiche detail (modale)** : Bloc "Origine" avec icone globe + tags Canal/Source visibles
- **Contacts directs** : Aucun tag affiché (comportement correct)
- **Données conservées** : tracking_via + tracking_source suivent le lead du formulaire jusqu'à l'admin
- Tests: iteration 131 — 12/12 backend, 10/10 frontend

## Statut Converti & ROI par Canal (Mar 2026) — DONE
- **Statut "Converti"** ajoute au pipeline leads avec badge vert (BadgeCheck)
- **Formulaire de conversion** dans la modale contact : montant facture + type de prestation (6 types)
- **Champs DB** : `conversion_montant` (float), `conversion_prestation` (str), `conversion_date` (str)
- **KPI "Convertis"** dans le tab contacts avec compteur + revenu total
- **ROI par canal** dans l'onglet Analytics : revenus generes, closing rate, par canal (QR/Email/PDF/Direct)
- **Revenus par prestation** : breakdown Accompagnement MP, Protection juridique, Expertise medicale, etc.
- **Stats admin enrichies** : `GET /api/admin/stats` retourne `converti` + `total_revenue`
- **Analytics enrichi** : `GET /api/tracking/conversion-analytics` retourne `conversions`, `revenue`, `close_rate`, `prestations`
- Tests: iteration 132 — 11/11 backend, 14/14 frontend

## Taches a venir
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P3:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search, HubSpot (attente)
