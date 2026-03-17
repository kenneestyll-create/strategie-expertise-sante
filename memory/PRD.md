# PRD — Stratégie & Expertise Santé

## Énoncé du problème
Application web complète en français pour fournir des conseils sur les maladies professionnelles et les litiges d'assurance.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Thème:** Warm neutral (Manrope + Playfair Display)
- **Intégrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), apscheduler, fpdf2, slowapi

## Services — Séparation gratuit/payant

### StratégiIA (GRATUIT)
- Formulaire simple : type de dossier + régime + situation
- Analyse IA basique (Claude Sonnet 4.5)
- Résultat textuel avec email gate pour rapport complet
- Bouton "Analyser mon dossier gratuitement"

### Dossier Express IA (PAYANT — 97€)
- Score de solidité du dossier (XX/100) avec ring SVG animé
- 3 métriques clés : Complétude, Qualité, Cohérence
- Points de fragilité, alertes de risque, prédictions
- Actions recommandées priorisées (max 3)
- Indicateur navbar compact — uniquement pour clients payants
- **Gating:** Clients sans Dossier Express IA voient un teaser flouté avec CTA

## Fonctionnalités implémentées

### Audit de Sécurité Complet (Mar 2026) ✅
- P1: JWT Secret obligatoire depuis env var
- P1: Paiement sécurisé (vérification DB + fallback live Stripe + webhook cross-update)
- P2: Rate Limiting 5/min sur endpoints d'authentification
- P2: Uploads sécurisés (MIME whitelist + extensions + 10Mo + scan signatures)
- P2: CORS strict depuis ALLOWED_ORIGINS
- P3: Documents sécurisés (auth + propriété)
- Headers de sécurité (X-Content-Type-Options, X-Frame-Options, etc.)

### Optimisation Tunnel de Conversion Dossier Express IA (Mar 2026) ✅
- **Landing page refonte:**
  - Compteur hebdomadaire en temps réel ("X dossiers analysés cette semaine")
  - Titre orienté valeur : "Votre rapport d'analyse complet et personnalisé"
  - 4 étapes visuelles au-dessus de la ligne de flottaison
  - Signaux de confiance (paiement sécurisé, RGPD, garantie satisfaction)
  - Section témoignages clients (3 avis avec notes 5 étoiles)
  - 6 cartes fonctionnalités du rapport
  - CTA final dans un card sombre
- **Formulaire refonte:**
  - Indicateur de progression (1. Informations → 2. Paiement → 3. Analyse)
  - Sidebar valeur sur desktop (contenu du rapport, signaux confiance, compteur)
  - Options upsell repositionnées (Analyse Premium +49€, Version Pro +19€)
  - Prix dynamique dans le bouton de paiement
  - Réassurance sous le bouton (Stripe + livraison 2h)
- **Upsell DossierAnalysis amélioré:**
  - Design amber avec icône Zap
  - Micro-signaux confiance (Rapport 2h, Stratégie personnalisée, Actions concrètes)
  - Bouton "Dossier Express — 97€" avec garantie satisfaction
- **Préparation Stripe production:**
  - `STRIPE_MODE` auto-détecté depuis le préfixe de la clé API
  - `STRIPE_WEBHOOK_SECRET` prêt pour la vérification de signature
  - `payment_config` exposé dans `/api/admin/analytics` (mode, configured)
  - Switch instantané : remplacer `STRIPE_API_KEY` dans .env suffit

### Renommage Dossier Express → Dossier Express IA (Mar 2026) ✅
- Renommage complet sur tout le site (frontend, backend, emails, PDFs)
- Cohérence branding avec StratégiIA
- Routes, collections DB et variables inchangées
- Validé par 13 tests + 4 vérifications grep

### Scanner Documents CamScanner-like (Mar 2026) ✅
- Phase d'ajustement post-capture : filtres (Original/Document/N&B), rotation 90°, recadrage manuel avec poignées draggables
- Bouton "Ajustement auto" (optionnel), validation directe possible sans manipulation
- Crop overlay SVG avec 4 poignées tactiles (44px touch targets), masque SVG
- Amélioration image : contraste + unsharp mask (mode Document), binarisation adaptative (mode N&B)
- Interface accessible : libellés simples, texte "les ajustements sont optionnels"
- Fix caméra mobile : timing stream/video corrigé (useEffect), double overlay supprimé

### Section Partenaires Footer (Mar 2026) ✅
- Formulaire dédié inline (Nom, Société, Email, Type de partenariat, Message)
- Endpoint `POST /api/partner-request` → stockage MongoDB + notification email
- Types : Professionnel de santé, Avocat/Juriste, Expert, Association, Sponsor, Autre
- Icônes contact rapide (LinkedIn + email), responsive 2 colonnes desktop

### Système complet StratégiIA / Dossier Express IA (Phases 1-3)
- Analyse IA, scoring, OCR, auto-remplissage, notifications, PDF

## Fichiers clés
- `/app/frontend/src/pages/DossierExpressPage.jsx` — Tunnel de conversion complet
- `/app/frontend/src/components/DossierAnalysis.jsx` — Analyse premium + upsell
- `/app/backend/config.py` — Configuration centralisée, JWT, rate limiter, Stripe
- `/app/backend/routes/payments.py` — Stripe/PayPal + webhook sécurisé
- `/app/backend/routes/strategiia.py` — StratégiIA + Dossier Express

## Tâches en attente
- **Paiements production (P1):** Remplacer `STRIPE_API_KEY` et `STRIPE_WEBHOOK_SECRET` dans .env — code prêt
- **HubSpot (P2):** En attente du HUBSPOT_PORTAL_ID
- **Contenu juridique (P3):** En attente du contenu utilisateur

## Backlog
- Audit logging (journalisation actions sensibles — pré-production)
- Refactoring AdminDashboard.jsx (~2700 lignes)
- Refactoring EmailTemplateEditor.jsx (monolithique)
- Statistiques d'utilisation par template
- Campagnes récurrentes

## Credentials de test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client: `test-analysis@test.com` / `Password123!`
