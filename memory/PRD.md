# PRD — Stratégie & Expertise Santé

## Énoncé du problème
Application web complète en français pour fournir des conseils sur les maladies professionnelles et les litiges d'assurance. Nommée "Stratégie & Expertise Santé".

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Thème:** Noir et Or (warm neutral: Manrope + Playfair Display)
- **Intégrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), apscheduler (cron), fpdf2 (PDF)

## Fonctionnalités implémentées

### Core
- Authentification (admin + client), Dashboard client/admin (15 onglets)
- StratégiIA (analyse IA), Scoring qualité, Forum, chatbot, calculatrices

### StratégiIA Phase 1 — Analyse de dossier (Feb 2026)
- **Endpoint:** `GET /api/client/dossier-analysis` (authenticated)
- **Score composite "Solidité du dossier":** 0-100, basé sur complétude (40%), qualité docs (20%), analyses réalisées (15%), progression globale (15%), volume de pièces (10%)
- **Messages dynamiques:** 5 seuils (<30%=urgent, 30-50%=attention, 50-70%=encourageant, 70-85%=positif, >85%=expert)
- **Points de fragilité:** Détection automatique (documents manquants, illisibles, pas de validation, pas d'analyse IA, aucun document)
- **Alertes de risque:** Spécifiques par type de dossier (AT, MP, MDPH, assurance, expertise, faute inexcusable, recours) avec messages détaillés et actions recommandées
- **Compteur d'actions:** "X éléments à traiter pour renforcer votre dossier"
- **Détail du score:** Ventilation interactive avec barres de progression par critère
- **Documents manquants:** Liste avec boutons "Ajouter" redirigeant vers l'espace documents
- **Frontend:** Composant `DossierAnalysis.jsx` avec score ring SVG animé, cartes extensibles, design responsive
- **Fichiers:** `/app/backend/routes/client.py` (endpoint), `/app/frontend/src/components/DossierAnalysis.jsx` (UI)

### Système de notifications
- Emails complétion (50/80/100%) + relances inactivité (J+7/14/21)
- Cron hybride, tracking engagement, KPIs, CSV export, alertes, A/B testing

### Éditeur de templates email
- CRUD complet, aperçu live, toggle actif/brouillon, 3 templates défaut

### Variables dynamiques
- 5 variables : {{prenom}}, {{nom}}, {{completeness}}, {{documents_missing}}, {{date_inscription}}
- Barre d'insertion, coloration syntaxique, résolution automatique

### Mode test email + Historique
- Envoi test à une adresse, valeurs éditables, préfixe [TEST]
- Historique dans email_test_history, indicateurs visuels sur cartes

### Campagnes programmées
- Dialog date/heure + cible + A/B optionnel
- Scheduler vérifie toutes les 60s, exécution avec résolution variables
- Tableau de bord avec statuts colorés et actions

### Guides PDF téléchargeables (Bug fix - Feb 2026)
- 6 guides PDF générés à la volée via fpdf2 avec branding
- Endpoint public : `GET /api/resources/pdf/{guide_id}`

## Tâches à venir

### Phase 2: StratégiIA — Feedback temps réel & Recommandations (P1)
- Feedback temps réel après actions utilisateur (upload, analyse)
- Section "Prochaines actions recommandées" avec CTAs cliquables priorisés

### Phase 3: StratégiIA — Fonctionnalités avancées (P2)
- Logique prédictive anticipant les motifs de refus
- Enrichissement du dashboard client avec données StratégiIA
- Notifications intelligentes non intrusives
- CTA premium "Analyse Expert"

## Tâches en attente (bloquées)
- **HubSpot (P2):** En attente du HUBSPOT_PORTAL_ID
- **Paiements production (P2):** En attente des clés Stripe/PayPal production
- **Contenu juridique (P3):** En attente du contenu utilisateur

## Backlog
- Refactoring AdminDashboard.jsx (~2700 lignes)
- Refactoring EmailTemplateEditor.jsx (monolithique)
- Intégration templates ↔ A/B testing
- Statistiques d'utilisation par template
- Campagnes récurrentes

## Fichiers clés
- `/app/frontend/src/components/DossierAnalysis.jsx` — Analyse de dossier Phase 1
- `/app/frontend/src/components/ProgressDashboard.jsx` — Dashboard progression
- `/app/frontend/src/pages/EspaceClientPage.jsx` — Espace client
- `/app/frontend/src/components/StrategiIA.jsx` — Modal StrategiIA
- `/app/backend/routes/client.py` — Endpoints client + dossier-analysis
- `/app/backend/routes/strategiia.py` — Endpoints StrategiIA/Dossier Express
- `/app/backend/routes/admin.py` — Endpoints admin
- `/app/backend/utils/pdf_guides.py` — Génération PDF

## Credentials de test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client: `test-analysis@test.com` / `Password123!`
