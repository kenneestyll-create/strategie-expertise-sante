# PRD — Stratégie & Expertise Santé

## Énoncé du problème
Application web complète en français pour fournir des conseils sur les maladies professionnelles et les litiges d'assurance.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Thème:** Warm neutral (Manrope + Playfair Display)
- **Intégrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), apscheduler (cron), fpdf2 (PDF), slowapi (rate limiting)

## Services — Séparation gratuit/payant

### StratégiIA (GRATUIT)
- Formulaire simple : type de dossier + régime + situation
- Analyse IA basique (Claude Sonnet 4.5)
- Pas d'OCR, pas de score de solidité, pas de document upload
- Résultat textuel avec email gate pour rapport complet
- Bouton "Analyser mon dossier gratuitement"

### Dossier Express (PAYANT — 97€)
- Score de solidité du dossier (XX/100) avec ring SVG animé
- 3 métriques clés toujours visibles : Complétude, Qualité, Cohérence
- Points de fragilité détectés avec sévérité
- Alertes de risque spécifiques par type de dossier
- Anticipation prédictive des motifs de refus
- Actions recommandées priorisées (max 3) avec badges de priorité
- Feedback temps réel (+X% après upload/suppression)
- Indicateur navbar compact — uniquement pour clients Dossier Express
- **Gating:** Clients sans Dossier Express voient un teaser flouté avec CTA "Dossier Express — 97€"

## Fonctionnalités implémentées

### Audit de Sécurité Complet (Mar 2026) ✅
- **P1 - JWT Secret:** Variable d'environnement obligatoire, serveur refuse de démarrer sans
- **P1 - Paiement sécurisé:** Vérification payment_verified + fallback live Stripe + webhook cross-update
- **P2 - Rate Limiting:** slowapi 5/min sur tous les endpoints d'authentification
- **P2 - Uploads sécurisés:** Whitelist MIME + extensions + limite 10Mo + scan signatures dangereuses
- **P2 - CORS strict:** Origins depuis variable d'environnement (pas de wildcard *)
- **P3 - Documents sécurisés:** Auth + vérification propriété sur tous les endpoints documents
- **Bonus - Headers de sécurité:** X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy

### Séparation StratégiIA / Dossier Express (Mar 2026)
- Backend: `has_dossier_express` flag dans `GET /api/client/dossier-analysis`
- Free: réponse limitée (score, dynamic_message, summary uniquement)
- Premium: réponse complète (key_metrics, predictions, risk_alerts, etc.)
- Frontend: `DossierExpressUpsell` component pour clients gratuits
- StrategiIA simplifié : retiré DocumentUploader, OCR, dossier quality score
- Navbar score gated derrière `has_dossier_express`

### Dossier Express — OCR Phase 2 intégré (Mar 2026)
- DocumentUploader avec `enableOCR=true` dans le formulaire Dossier Express
- Auto-remplissage des champs via OCR + GPT-4o
- Score composite (complétude 40%, qualité 20%, cohérence, analyses 15%, progression 15%, volume 10%)
- Messages dynamiques, points de fragilité, alertes de risque
- Actions recommandées priorisées (max 3) avec badges couleur
- Logique prédictive de refus par type de dossier

### Système de notifications
- Emails complétion (50/80/100%) + relances inactivité (J+7/14/21)
- A/B testing, campagnes programmées, templates éditables

### Guides PDF téléchargeables
- 6 guides PDF via fpdf2, police DejaVu Sans, branding

## Fichiers clés
- `/app/backend/config.py` — Configuration centralisée, JWT, rate limiter
- `/app/backend/server.py` — Middleware CORS, security headers, GZip
- `/app/backend/routes/payments.py` — Stripe/PayPal + webhook sécurisé
- `/app/backend/routes/strategiia.py` — StratégiIA + Dossier Express + payment verification
- `/app/backend/routes/client.py` — Documents sécurisés + analyse dossier
- `/app/frontend/src/components/DossierAnalysis.jsx` — Analyse premium + upsell
- `/app/frontend/src/components/layout/Header.jsx` — Navbar gated score

## Tâches en attente
- **HubSpot (P2):** En attente du HUBSPOT_PORTAL_ID
- **Paiements production (P2):** En attente des clés Stripe/PayPal live
- **Contenu juridique (P3):** En attente du contenu utilisateur

## Backlog
- Connecter le CTA Dossier Express 97€ au parcours de paiement Stripe
- Refactoring AdminDashboard.jsx (~2700 lignes)
- Refactoring EmailTemplateEditor.jsx (monolithique)
- Statistiques d'utilisation par template
- Campagnes récurrentes

## Credentials de test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client (gratuit): `test-analysis@test.com` / `Password123!`
