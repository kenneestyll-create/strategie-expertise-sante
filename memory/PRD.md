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

## Taches a venir
- **P1:** Dashboard admin pour stats tracking/conversions + leads guides
- **P0:** Finaliser Mode Admin Test Premium (Relecture expert, alertes email, badge dashboard)
- **P0:** Enrichissement rapport premium (1.5 pages, phrase cloture emotionnelle, orientation service)
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search, HubSpot (attente)
