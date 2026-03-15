# Stratégie & Expertise Santé — PRD

## Problème original
Application web complète en français pour accompagner les victimes de maladies professionnelles, accidents du travail, litiges assurantiels et procédures d'invalidité (MDPH).

## Architecture
```
/app/backend/
├── server.py          (68 lignes — point d'entrée slim)
├── config.py          (DB, env, constantes)
├── models.py          (modèles Pydantic)
├── utils/
│   ├── auth.py        (auth, tokens, dépendances)
│   ├── email.py       (notifications email Resend)
│   ├── chatbot.py     (FAQ + IA Claude)
│   └── pdf.py         (génération PDF fpdf2)
├── routes/
│   ├── public.py      (contact, FAQ, avis, visiteurs, parrainage)
│   ├── chatbot.py     (chatbot IA)
│   ├── forum.py       (forum CRUD + admin)
│   ├── payments.py    (Stripe + PayPal)
│   ├── admin.py       (dashboard admin, analytics, CRUD)
│   ├── client.py      (portail client, documents, notifications, progression)
│   ├── strategiia.py  (StratégiIA, Dossier Express, cas anonymisés)
│   └── misc.py        (RDV, simulateur, alertes, relance, SEO, seed)
└── tests/

/app/frontend/src/
├── pages/             (AdminDashboard, EspaceClient, StrategiIA, DossierExpress...)
├── components/        (DocumentUploader, OcrFieldsPreview, Chatbot...)
└── hooks/             (useOCR.js)
```

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
- [x] Portail client (inscription, dossiers, documents, notifications, progression)
- [x] OCR Phase 1 (Tesseract.js côté client)
- [x] Contrôle qualité documents (validation, checklist, guide scan)
- [x] Historique intelligent documents (tags, catégories, filtres)
- [x] Dashboard progression client (donut chart + timeline)
- [x] Analytics admin (KPIs, graphiques recharts)
- [x] SEO (sitemap.xml, robots.txt, cache)
- [x] **Refactoring backend** — monolithe 4327 lignes → 16 modules (mars 2026)

## Éléments bloqués (action utilisateur)
1. **Budget LLM Emergent** épuisé → Profile → Universal Key → Add Balance
2. **HubSpot Portal ID** → fournir `HUBSPOT_PORTAL_ID`
3. **Clés Stripe/PayPal production** → fournir les clés live
4. **Contenu juridique** → fournir texte final Mentions Légales

## Tâches futures
- P2: OCR Phase 2 (GPT-4o côté serveur) — bloqué par budget LLM
- P3: Push notifications navigateur (Service Worker)
- P3: Stockage objet (fichiers en production)
- P3: Domaine Resend vérifié

## Credentials test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client: inscription via `/espace-client`

## Intégrations
| Service | Statut |
|---------|--------|
| Stripe | Sandbox |
| PayPal | Sandbox |
| Claude Sonnet 4.5 (Emergent) | Budget épuisé |
| Resend | Actif |
| Tesseract.js | Actif (côté client) |
| HubSpot | En attente Portal ID |
| recharts | Actif |
| fpdf2 | Actif |
