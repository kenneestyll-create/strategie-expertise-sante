# Stratégie & Expertise Santé — PRD

## Problème original
Application web complète en français pour accompagner les victimes de maladies professionnelles, accidents du travail, litiges assurantiels et procédures d'invalidité (MDPH).

## Architecture (après refactoring mars 2026)
```
/app/backend/
├── server.py          (slim entry point)
├── config.py          (DB, env, constantes)
├── models.py          (modèles Pydantic)
├── pyproject.toml     (config pytest)
├── .github/workflows/ci.yml (CI/CD)
├── utils/
│   ├── auth.py        (auth, tokens)
│   ├── email.py       (notifications email Resend)
│   ├── chatbot.py     (FAQ + IA Claude)
│   ├── pdf.py         (génération PDF fpdf2)
│   ├── push.py        (notifications push VAPID/WebPush)
│   └── storage.py     (stockage objet Emergent)
├── routes/
│   ├── client.py      (portail client, docs, notifs, push, stockage)
│   └── ...            (admin, forum, payments, strategiia, misc, public, chatbot)
└── tests/             (210+ tests pytest)
```

## Tests unitaires — 210 tests (100% pass)
Exécution : `cd /app/backend && python -m pytest --cov=. --cov-report=term-missing -q`

| Module | Tests | Couverture |
|--------|-------|-----------|
| config | 9 | Constantes, packages, slots, DB |
| models | 22 | Validation Pydantic, defaults, bornes |
| utils/auth | 8 | Hash, verify, tokens (admin/forum/client) |
| utils/chatbot | 9 | FAQ matching, keywords |
| utils/pdf | 8 | PDF génération, watermark, caractères spéciaux |
| routes/public | 15 | Contact, FAQ, avis, visiteurs, parrainage |
| routes/chatbot | 4 | FAQ, IA fallback, quota |
| routes/forum | 16 | Auth, topics, replies, likes, reports, admin |
| routes/admin | 18 | Auth, contacts, analytics, FAQ, avis, clients |
| routes/payments | 5 | Packages, PayPal, Stripe validation |
| routes/client | 17 | Auth, profile, progress, documents CRUD, notifications |
| routes/strategiia | 16 | Score, quota, analyse, PDF, cas anonymisés CRUD |
| routes/misc | 30 | Booking, simulator, alerts, OCR, SEO, seed |

## Fonctionnalités implémentées
- [x] Site vitrine multipage (AT/MP, MDPH, expertises, tarifs, etc.)
- [x] Formulaire de contact + notifications email (Resend)
- [x] FAQ dynamique + chatbot IA (Claude Sonnet 4.5)
- [x] Forum communautaire avec modération admin
- [x] Simulateur de diagnostic interactif
- [x] Calculatrice IPP/AAH
- [x] Paiements Stripe + PayPal (sandbox)
- [x] Parrainage + fidélité (réductions auto)
- [x] Prise de RDV avec créneaux
- [x] StrategiIA (analyse IA, quota gratuit, premium, PDF)
- [x] Dossier Express (analyse complète IA + envoi email PDF)
- [x] Cas anonymisés (scoring de pertinence)
- [x] Portail client complet (inscription, dossiers, documents, notifications, progression)
- [x] OCR Phase 1 (Tesseract.js côté client)
- [x] Contrôle qualité documents
- [x] Historique intelligent documents
- [x] Dashboard progression client
- [x] Analytics admin (KPIs, graphiques recharts)
- [x] SEO (sitemap.xml, robots.txt, cache)
- [x] Refactoring backend modulaire (mars 2026)
- [x] Suite complète de tests unitaires pytest — 187 tests (mars 2026)
- [x] Suite de tests élargie — 210 tests, 0 échec, couverture 77.8% (fév 2026)
- [x] Pipeline CI/CD GitHub Actions (`.github/workflows/ci.yml`)
- [x] Push notifications navigateur (Service Worker VAPID, mars 2026)
- [x] Stockage objet Emergent (documents en production, mars 2026)
- [x] Push notifications automatiques (validation/rejet document, mise à jour dossier, mars 2026)
- [x] OCR Phase 2 GPT-4o (extraction intelligente de champs, mars 2026)
- [x] Admin — Onglet Documents (validation/rejet avec notifications auto, mars 2026)
- [x] Admin — Onglet Config (Resend, stockage objet, push, guide vérification domaine, mars 2026)
- [x] OCR automatique à l'upload — Pipeline complet Tesseract.js → GPT-4o → pré-remplissage automatique (mars 2026)
  - Dossier Express : auto-fill nom, type dossier, régime, situation
  - StratégiIA : auto-fill type dossier, régime, situation enrichie
  - Espace Client Documents : auto-tagging catégorie, organisme, type
  - Backend : auto-extraction GPT-4o pour PDF uploadés sans OCR client
  - OcrFieldsPreview : affiche organisme, résumé, recommandations IA
- [x] Scanner de documents smartphone — Caméra navigateur + guide visuel + amélioration image + OCR auto (mars 2026)
  - Composant DocumentScanner : 4 phases (guide → caméra → preview → traitement)
  - Guide visuel : 4 conseils (droit, visible, luminosité, reflets)
  - Amélioration Canvas : contraste, luminosité, netteté
  - Intégré dans Dossier Express, StratégiIA, Espace Client Documents
- [x] Mode multi-scan — Fusion multi-pages en PDF + OCR combiné (mars 2026)
  - 6 phases : guide → caméra → aperçu → revue pages → aperçu PDF → traitement
  - Barre de miniatures (PageStrip) avec suppression individuelle
  - Navigation entre pages (flèches), aperçu PDF (iframe jsPDF)
  - Fusion automatique en PDF A4 + OCR GPT-4o sur le texte combiné
  - Bandeau "Mode multi-pages : scannez plusieurs pages, elles seront fusionnées en un seul PDF"

## Éléments bloqués (action utilisateur)
1. **Budget LLM Emergent** épuisé → Profile → Universal Key → Add Balance
2. **HubSpot Portal ID** → fournir `HUBSPOT_PORTAL_ID`
3. **Clés Stripe/PayPal production** → fournir les clés live
4. **Contenu juridique** → fournir texte final Mentions Légales

## Tâches futures
- P2: Vérification domaine Resend (action utilisateur)
- P3: Activer intégrations production (HubSpot, Stripe/PayPal live, contenu juridique)

## Credentials test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client: inscription via `/espace-client`
