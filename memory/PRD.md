# PRD — Stratégie & Expertise Santé

## Énoncé du problème
Application web complète en français pour fournir des conseils sur les maladies professionnelles et les litiges d'assurance.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Thème:** Warm neutral (Manrope + Playfair Display)
- **Intégrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), apscheduler (cron), fpdf2 (PDF)

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
- Alertes de risque spécifiques par type de dossier (AT, MP, MDPH, assurance, expertise, recours, faute inexcusable)
- Anticipation prédictive des motifs de refus
- Actions recommandées priorisées (max 3) avec badges de priorité (haute/moyenne/faible)
- Feedback temps réel (+X% après upload/suppression)
- Indicateur navbar compact (desktop + mobile) — uniquement pour clients Dossier Express
- CTA Premium "Analyse Expert" pour upsell
- **Gating:** Clients sans Dossier Express voient un teaser flouté avec CTA "Dossier Express — 97€"

## Fonctionnalités implémentées

### Séparation StratégiIA / Dossier Express (Mar 2026)
- Backend: `has_dossier_express` flag dans `GET /api/client/dossier-analysis`
- Free: réponse limitée (score, dynamic_message, summary uniquement)
- Premium: réponse complète (key_metrics, predictions, risk_alerts, etc.)
- Frontend: `DossierExpressUpsell` component pour clients gratuits (score flouté + lock + CTA 97€)
- StrategiIA simplifié : retiré DocumentUploader, OCR, dossier quality score
- Navbar score gated derrière `has_dossier_express`

### Analyse de dossier — Phases 1/2/3 (Feb-Mar 2026)
- Score composite (complétude 40%, qualité 20%, cohérence, analyses 15%, progression 15%, volume 10%)
- Messages dynamiques (5 seuils), points de fragilité, alertes de risque
- Actions recommandées priorisées (max 3) avec badges couleur
- Logique prédictive de refus par type de dossier
- CTA Premium "Analyse Expert Personnalisée"

### Système de notifications
- Emails complétion (50/80/100%) + relances inactivité (J+7/14/21)
- A/B testing, campagnes programmées, templates éditables

### Guides PDF téléchargeables
- 6 guides PDF via fpdf2, police DejaVu Sans, branding

## Fichiers clés
- `/app/frontend/src/components/DossierAnalysis.jsx` — Analyse premium + upsell
- `/app/frontend/src/components/StrategiIA.jsx` — Modal StratégiIA simplifié
- `/app/frontend/src/pages/EspaceClientPage.jsx` — Espace client + navbar gated
- `/app/frontend/src/components/ClientDocuments.jsx` — Upload + refresh
- `/app/backend/routes/client.py` — Endpoint dossier-analysis (free/premium)
- `/app/backend/routes/strategiia.py` — Endpoints StrategiIA/Dossier Express

## Tâches en attente
- **HubSpot (P2):** En attente du HUBSPOT_PORTAL_ID
- **Paiements production (P2):** En attente des clés Stripe/PayPal
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
